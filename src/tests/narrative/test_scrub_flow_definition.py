#!/usr/bin/env python3
"""Executes the SHIPPED `REV | Narrative | Scrub Free-Text` definition, rebuilt to TAD rev 22 / ADR-075 in
Iteration 9 and changed by TAD rev 30 / ADR-082 in Iteration 14 (wbs:5.3, 5.6): one extractor call per BATCH of
columns, one prompt that rewrites and corrects spelling. Compares it with the flow model in redaction_reference.py.

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

Level: a definition-level execution in wdl_sim.py, not a platform run. The rewrite prompt is a STAND-IN
(corpus_support.py): a good model, and bad models written to break the checks. What this proves is the
property ADR-075 and ADR-082 rest on: whatever the model answers, the flow writes a column only when P1 (no
extractor value survives) and P2 (every word of the rewrite is an input word, a closed-list word, a plural
form, or the corrected half of a DECLARED, validated near-spelling pair) pass. It proves nothing about the
live model's quality (wbs:5.7), the AI Builder wire shapes (A-NS-13, A-NS-16, A-NS-31), the offsets of a
joined call (A-NS-41), a nested loop's save (A-NS-42) or a designer save (V4).

No narrative text is printed: assertion messages name sample ids and reason codes only (C-DOM-004).
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import corpus_support as cs  # noqa: E402
import redaction_reference as rr  # noqa: E402
import wdl_sim  # noqa: E402

REPO = HERE.parents[2]
FLOW = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
        / "REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json")
DEFINITION = json.loads(FLOW.read_text(encoding="utf-8"))["properties"]["definition"]
ENTITY_XML = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Entities" / "rev_application" / "Entity.xml"

# A-NS-31, closed 2026-10-16: the rewrite prompt component's id, as exported from DEV after R1b
# (test_prompt_component.py reads the same id out of Other/Customizations.xml). Rev 30 (ADR-082 item 4): the
# spelling prompt (763cff31-...) is no longer called, so the flow carries one prompt id.
REWRITE_ID = "e853d7c8-dd36-4917-951f-50108a812fc4"
RETIRED_SPELLING_ID = "763cff31-d653-416b-a52f-7e6f400bce21"
PROMPT_INPUTS = {REWRITE_ID: {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}}
SEED_CODES = rr.load_register()
SEED = object()
OTHER_SETTING = {"rev_name": "PostcodeRegionMap", "rev_value": "{\"LS\": 1}", "modifiedon": "2026-10-20T10:00:00Z"}
CANARY = "Zqxwvy"   # a made-up word: wherever it shows up in a run record, narrative text is there


def walk(actions):
    for n, a in actions.items():
        yield n, a
        for sub in (a.get("actions"), (a.get("else") or {}).get("actions"), (a.get("default") or {}).get("actions")):
            if isinstance(sub, dict):
                yield from walk(sub)
        for c in (a.get("cases") or {}).values():
            yield from walk(c.get("actions") or {})


ACTIONS = dict(walk(DEFINITION["actions"]))


@dataclass
class Run:
    status: str
    calls: list
    prompt_inputs: list
    column_writes: dict
    decision_write: dict | None
    notices: list
    alerts: list
    engine: wdl_sim.Engine

    @property
    def reasons(self):
        res = self.engine.results.get("Compose_decision", {}).get("outputs")
        return tuple(res["reasons"]) if res else None

    def ops(self, op):
        return [n for n, o in self.calls if o == op]


def run_flow(row, settings, extract, rewrite=cs.good_rewrite, *, status=6,
             case_insensitive=True, fail_write=False, modified=None, register=SEED, definition=None,
             stop_loops_on_failure=False) -> Run:
    calls, prompt_inputs, column_writes, notices, alerts, decision = [], [], {}, [], [], {}
    modified = modified or {}

    def connector(name, op, params):
        calls.append((name, op))
        if op == "GetItem":
            return {"rev_applicationid": "app-1", "rev_name": "APP-0001", **row}
        if op == "ListRecords" and params["entityName"] == "rev_settings":
            assert "$filter" not in params, "TAD 5.5.1: every row is read and filtered in the flow"
            rows = [{"rev_name": k, "rev_value": v, "modifiedon": modified.get(k, rr.DEFAULT_MODIFIED)}
                    for k, v in settings.items()]
            return {"value": rows + [OTHER_SETTING]}
        if op == "ListRecords" and params["entityName"] == "rev_citysettlementregisters":
            assert params["$select"] == "rev_name" and "$filter" not in params
            codes = SEED_CODES if register is SEED else register
            if codes is None:
                raise wdl_sim.ConnectorFailure("register read failed")
            return {"value": [{"rev_name": c} for c in codes]}
        if op == "aibuilderpredict_entityextraction":
            assert params["item/requestv2/language"] == "en"
            text = params["item/requestv2/text"]
            assert 0 < len(text) <= rr.EXTRACTOR_MAX_CHARS
            try:
                ents = extract(text)
            except Exception as e:  # noqa: BLE001 - any mock failure makes the ACTION fail
                raise wdl_sim.ConnectorFailure(str(e)) from e
            if ents == "UNREADABLE":
                return {"responsev2": {"predictionOutput": {}}}
            return {"responsev2": {"predictionOutput": {"results": [
                {"type": e.type, "value": e.value, "startIndex": e.startIndex, "length": e.length, "score": e.score}
                for e in ents]}}}
        if op == "aibuilderpredict_customprompt":
            rid = params["recordId"]
            assert set(params) == {"recordId"} | {f"item/requestv2/{n}" for n in PROMPT_INPUTS[rid]}, sorted(params)
            inputs = {n: params[f"item/requestv2/{n}"] for n in PROMPT_INPUTS[rid]}
            prompt_inputs.append((rid, inputs))
            try:
                ans = rewrite(**inputs)
            except Exception as e:  # noqa: BLE001
                raise wdl_sim.ConnectorFailure(str(e)) from e
            return {"responsev2": {"predictionOutput": ans}}
        if op == "UpdateOnlyRecord":
            items = {k[5:]: v for k, v in params.items() if k.startswith("item/")}
            if name.startswith("Write_rev_"):
                if fail_write:
                    raise wdl_sim.ConnectorFailure("Dataverse refused the write")
                column_writes.update(items)
            else:
                decision[name] = items
            # "Update a row" returns the updated row (connector reference; test report 20261016-3, D-1),
            # and the flow's identity can read the raw narrative columns, so the stand-in returns them too.
            # A-NS-39: until 2026-10-16 this returned {}, and the run-history test could not see the gap.
            return {"rev_applicationid": "app-1", "rev_name": "APP-0001", **row, **items}
        if op in ("PostCardToConversation", "PostMessageToConversation"):
            notices.append(params["body/messageBody"])
            return {}
        raise AssertionError(f"unexpected connector call {name} {op}")

    engine = wdl_sim.Engine(
        definition or DEFINITION, {"rev_applicationid": "app-1", "rev_status": status, "rev_name": "APP-0001"},
        parameters={"rev_ProcessOwnerUpn": "owner@example.org", "rev_GrantAdminAppUrl": "https://example.org/main.aspx?appid=1"},
        connector=connector, child_flow=lambda n, b: alerts.append(b), case_insensitive=case_insensitive,
        stop_loops_on_failure=stop_loops_on_failure)
    st = engine.run()
    return Run(st, calls, prompt_inputs, column_writes,
               decision.get("Write_the_decision") or decision.get("Hold_the_record_for_review"), notices, alerts, engine)


def model(row, settings, extract, rewrite=cs.good_rewrite, **kw):
    if kw.get("register", SEED) is SEED:
        kw.pop("register", None)
    return rr.flow_scrub_record(row, settings, extract, rewrite, **kw)


class Agreement(unittest.TestCase):
    """The shipped JSON and the oracle give the same writes, reasons and decision."""

    def compare(self, row, settings, extract, rewrite=cs.good_rewrite, ci=True, **kw):
        sim = run_flow(row, settings, extract, rewrite, case_insensitive=ci, **kw)
        dec, writes, outcomes = model(row, settings, extract, rewrite, **kw)
        self.assertEqual(sim.status, "Succeeded")
        self.assertEqual(sim.column_writes, writes)
        self.assertEqual(sim.reasons, dec.reasons)
        # ADR-078: the flow never writes rev_redactionreleased; review required on every scrubbed record,
        # and one card per scrubbed record, with or without a reason.
        self.assertEqual(sim.decision_write, {"rev_redactionreviewrequired": True,
                                              "rev_redactionconfidence": dec.confidence})
        self.assertFalse(dec.released)
        self.assertTrue(dec.review_required)
        self.assertEqual(len(sim.notices), 1)
        return sim, dec, writes, outcomes


def one(text, ents=()):
    return {"rev_narrativeraw": text}, cs.extractor_for([(text, list(ents))])


class FlowAgreesWithModelOnCorpus(Agreement):
    def test_each_sample_alone_both_string_semantics_and_both_settings(self):
        for ci in (True, False):
            for s, plain, gold in cs.corpus():
                for settings in (cs.RULES, cs.ALL_SETTINGS):
                    with self.subTest(s["id"], case_insensitive=ci, settings=bool(settings)):
                        row, ext = one(plain, cs.simulated_entities(s, plain, gold))
                        self.compare(row, settings, ext, ci=ci)

    def test_samples_spread_across_all_twelve_columns(self):
        samples = list(cs.corpus())
        for chunk in (samples[:12], samples[12:]):
            row, texts = {}, []
            for (raw, _), (s, plain, gold) in zip(rr.SCRUB_COLUMNS, chunk):
                row[raw] = plain
                texts.append((plain, cs.simulated_entities(s, plain, gold)))
            with self.subTest(first=chunk[0][0]["id"]):
                sim, *_ = self.compare(row, cs.ALL_SETTINGS, cs.extractor_for(texts))
                # ADR-082: one extractor call per batch of at most 5,000 characters, one prompt call per column.
                self.assertEqual(len(sim.ops("aibuilderpredict_entityextraction")),
                                 len(rr.plan_batches([len(row[raw]) for raw, _ in rr.SCRUB_COLUMNS if raw in row])))
                self.assertEqual(len(sim.ops("aibuilderpredict_customprompt")), len(chunk))

    def test_the_model_never_receives_a_value_the_extractor_found(self):
        """ADR-075 item 2: the rewrite prompt gets the labelled text, so no labelled span's text reaches it."""
        for s, plain, gold in cs.corpus():
            ents = cs.simulated_entities(s, plain, gold)
            row, ext = one(plain, ents)
            sim = run_flow(row, cs.RULES, ext)
            (rid, inp), = sim.prompt_inputs
            self.assertEqual(rid, REWRITE_ID)
            lab, kept, _, _ = rr.label_spans(plain, cs.as_entities(ents))
            self.assertEqual(inp["Narrative"], rr.labelled_text(plain, kept), s["id"])
            for span in kept:
                inside = plain[span.start:span.end]
                if len(inside) > 3:
                    self.assertNotIn(inside, inp["Narrative"], s["id"])

    def test_a_good_model_writes_the_expected_text(self):
        """With the good stand-in the written text is the oracle's expected_scrub: names to They, the key applied."""
        cases = {
            "Sam relies on me and she needs her rest.": ([("PersonName", "Sam", 0, 3, 0.95)], "They rely on me and they need their rest."),
            "My husband Derek Hale helps me and he drives.": ([("PersonName", "Derek Hale", 11, 10, 0.97)], "My partner helps me and they drive."),
            "My wife and son help at home.": ([], "My partner and child help at home."),
        }
        for text, (ents, want) in cases.items():
            row, ext = one(text, ents)
            sim, *_ = self.compare(row, cs.ALL_SETTINGS, ext)
            self.assertEqual(sim.column_writes["rev_narrativeredacted"], want)
            self.assertEqual(rr.expected_scrub(text, cs.as_entities(ents)), want)


class P2TheRewriteAddsNoWord(Agreement):
    """ADR-075 item 6: a rewrite that adds a word is not written (rewrite-invalid), whatever the word."""
    TEXT = "Sam relies on me. I help them every day."
    ENTS = [("PersonName", "Sam", 0, 3, 0.95)]

    def bad(self, change):
        row, ext = one(self.TEXT, self.ENTS)
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=cs.rewrite_then(change))
        self.assertEqual(writes, {})
        self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)
        return sim

    def test_a_rewrite_that_adds_a_name_is_held(self):
        self.bad(lambda t: t.replace("They", "Derek"))

    def test_a_rewrite_that_adds_a_phone_number_is_held(self):
        self.bad(lambda t: t + " Ring 07700 900999.")

    def test_a_rewrite_that_adds_a_sentence_is_held(self):
        self.bad(lambda t: t + " The family lives near the station.")

    def test_a_rewrite_that_undoes_a_label_is_held_by_p2_or_p1(self):
        row, ext = one("Ring Ann on Monday.", [("PersonName", "Ann", 5, 3, 0.9)])
        dec, writes, _ = model(row, cs.ALL_SETTINGS, ext, cs.rewrite_then(lambda t: "Ring Ann on Monday."))
        self.assertEqual(writes, {})
        self.assertTrue({"rewrite-invalid:rev_narrativeraw", "identifier-survived:rev_narrativeraw"} & set(dec.reasons))

    def test_what_p2_allows(self):
        """Moving, dropping, closed-list words, plural agreement forms: all pass P2 (and nothing is added)."""
        lab = "[NAME] relies on her mum and needs help."
        self.assertEqual(rr.validate_rewrite(lab, "They rely on their parent and need help."), [])
        self.assertEqual(rr.validate_rewrite(lab, "help needs and"), [])
        self.assertEqual(rr.validate_rewrite(lab, "They rely on [FAMILY MEMBER] and [PHONE]."), [])
        self.assertEqual(rr.validate_rewrite("my uncle came", "a relative came"), [])
        self.assertEqual(rr.validate_rewrite(lab, "They rely on Derek."), ["derek"])

    def test_a_neutral_word_is_allowed_only_while_the_row_says_so(self):
        """ADR-076 item 2: P2's closed list IS the row. Add 'nana = grand-parent' and the good model's
        'grand-parent' is written; without the line the same answer is rewrite-invalid."""
        row, ext = one("My nana visits.", [])
        with_line = {**cs.ALL_SETTINGS, "RedactionNeutralTerms": cs.RULES["RedactionNeutralTerms"] + "\nnana = grand-parent"}
        sim, dec, writes, _ = self.compare(row, with_line, ext)
        self.assertEqual(writes, {"rev_narrativeredacted": "My grand-parent visits."})
        self.assertNotIn("rewrite-invalid:rev_narrativeraw", dec.reasons)
        rw = lambda **_: cs.answer("My grand-parent visits.")   # noqa: E731 - the same answer, line absent
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertEqual(writes, {})
        self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)


class P1NoFoundIdentifierSurvives(Agreement):
    def test_a_found_value_repeated_elsewhere_undetected_is_held(self):
        """The extractor found 'Ann' once; the text says it again where the extractor did not. The second
        one reaches the rewrite as text, a good model keeps it, and P1 refuses the write."""
        text = "Ann helps me. I trust Ann."
        row, ext = one(text, [("PersonName", "Ann", 0, 3, 0.9)])
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes, {})
        self.assertIn("identifier-survived:rev_narrativeraw", dec.reasons)

    def test_p1_is_case_blind_and_matches_whole_words_only(self):
        self.assertEqual(rr.surviving_identifiers("They said ANN's coming", ["ann"]), ["ann"])
        self.assertEqual(rr.surviving_identifiers("an annual review", ["ann"]), [])
        self.assertEqual(rr.surviving_identifiers("ring 07700 900123", ["07700 900123"]), ["07700 900123"])


class SpellingDeclaredPairs(Agreement):
    """ADR-082 items 4 to 6 (rev 30): the rewrite prompt also corrects spelling and DECLARES each correction after a
    `###CORRECTIONS###` line as `wrong=>right`. P2 accepts a corrected word only as the right half of a declared pair
    that passes the pair rule; anything else it did not get from the input is `rewrite-invalid` and the column is not
    written. (Replaces the word-by-word acceptance of the retired second call, ADR-075 item 4.)"""
    TEXT = "I care for my partner who has dementai and needs help."

    def held(self, rewrite, text=None):
        row, ext = one(text or self.TEXT)
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rewrite)
        self.assertEqual(writes, {})
        self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)
        return dec

    def test_a_declared_near_spelling_of_a_lower_case_input_word_is_written(self):
        for ci in (True, False):
            row, ext = one(self.TEXT)
            _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=cs.rewrite_corrected({"dementai": "dementia"}), ci=ci)
            self.assertEqual(writes["rev_narrativeredacted"], "I care for my partner who has dementia and needs help.")
            self.assertEqual(dec.reasons, ("no-model-detections",))

    def test_the_same_correction_undeclared_is_rewrite_invalid(self):
        self.held(cs.rewrite_corrected({"dementai": "dementia"}, declare=[]))

    def test_each_refused_declaration_is_rewrite_invalid(self):
        """The pair rule's six refusals, each with the correction applied in the text and declared."""
        cases = {
            "a different first letter": ({"care": "scare"}, None),
            "a length change of 3": ({"dementai": "dementiaxyz"}, None),
            "a capitalised wrong word": ({"I": "We"}, None),
            "a wrong word that is not in the input": ({"dementai": "dementia"}, [("dementaix", "dementia")]),
            "a closed-list wrong word": ({"my": "mu"}, None),          # 'my' is on the closed list
            "a right word with a digit": ({"care": "car3"}, None),
        }
        for name, (fixes, declare) in cases.items():
            for ci in (True, False):
                with self.subTest(name, ci=ci):
                    row, ext = one(self.TEXT)
                    _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=cs.rewrite_corrected(fixes, declare), ci=ci)
                    self.assertEqual(writes, {})
                    self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)

    def test_a_correction_never_brings_back_a_gendered_word(self):
        """FR-100: 'sun' to 'son' keeps the first letter and the length and is still refused, as declared."""
        self.assertEqual(rr.valid_corrections("We sit in the sun", ["sun=>son"]), [])
        self.assertEqual(rr.valid_corrections("We sit in the sunn", ["sunn=>sun"]), ["sun"])
        row, ext = one("We sit in the sun and the breze.")
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=cs.rewrite_corrected({"sun": "son"}))
        self.assertEqual(writes, {})
        self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)

    def test_a_declared_pair_does_not_excuse_a_different_added_word(self):
        """The safety proof: a rewrite that adds a name, a number or a sentence is held by P2 as before, whatever
        correction it declares."""
        good = lambda **i: cs.good_rewrite(**i)["text"]   # noqa: E731
        for change in (lambda t: t.replace("partner", "Derek"), lambda t: t + " Ring 07700 900999.",
                       lambda t: t + " The family lives near the station."):
            with self.subTest(change("x partner")):
                self.held(lambda change=change, **i: cs.corrections_answer(
                    change(good(**i)).replace("dementai", "dementia"), [("dementai", "dementia")]))

    def test_a_word_that_is_not_an_input_word_cannot_be_declared(self):
        """The labelled text 'Ring [NAME] on Mondya.': 'them' is the rewrite's word, not an input word."""
        row, ext = one("Ring Ann on Mondya.", [("PersonName", "Ann", 5, 3, 0.9)])
        for ci in (True, False):
            _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci,
                                             rewrite=cs.rewrite_corrected({"them": "then", "Mondya.": "Monday."}))
            self.assertEqual(writes, {})
            self.assertIn("rewrite-invalid:rev_narrativeraw", dec.reasons)

    def test_the_answer_is_split_at_the_first_delimiter_and_malformed_lines_are_ignored(self):
        want = "I care for my partner who has dementia and needs help."
        answers = {
            "a second delimiter line is not a pair": f"{want}\n###CORRECTIONS###\ndementai=>dementia\n###CORRECTIONS###\nx=>y",
            "malformed lines": f"{want}\n###CORRECTIONS###\n\nnot a pair\na=>b=>c\ndementai=>dementia\n=>\ndementai =>",
            "carriage returns": f"{want}\r\n###CORRECTIONS###\r\ndementai=>dementia\r\n",
            "trailing white space before the delimiter": f"{want}\n\n   \n###CORRECTIONS###\ndementai=>dementia",
        }
        for name, text in answers.items():
            for ci in (True, False):
                with self.subTest(name, ci=ci):
                    row, ext = one(self.TEXT)
                    _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=lambda t=text, **_: cs.answer(t), ci=ci)
                    self.assertEqual(writes["rev_narrativeredacted"], want)

    def test_no_delimiter_means_no_corrections_and_the_whole_answer_is_the_rewrite(self):
        row, ext = one(self.TEXT)
        _, _, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes["rev_narrativeredacted"], self.TEXT)

    def test_an_answer_that_is_only_corrections_is_prompt_error(self):
        row, ext = one(self.TEXT)
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext,
                                         rewrite=lambda **_: cs.answer("###CORRECTIONS###\ndementai=>dementia"))
        self.assertEqual(writes, {})
        self.assertEqual(dec.reasons, ("prompt-error:rev_narrativeraw", "no-model-detections"))

    def test_the_spelling_prompt_is_never_called(self):
        row, ext = one(self.TEXT)
        sim, *_ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=cs.rewrite_corrected({"dementai": "dementia"}))
        self.assertEqual([rid for rid, _ in sim.prompt_inputs], [REWRITE_ID])

    def test_the_pair_rule_in_the_reference(self):
        lab = "I care for my [NAME] who has dementai and needs help. Ann"
        ok = lambda *lines: rr.valid_corrections(lab, list(lines))   # noqa: E731
        self.assertEqual(ok("dementai=>dementia"), ["dementia"])
        self.assertEqual(ok("dementai=>dementIA"), ["dementia"])               # the right word is compared in lower case
        self.assertEqual(ok("dementai=>Dementia"), [])                          # first letter must be the same letter, as written
        self.assertEqual(ok("Ann=>Anne"), [])                                   # a capitalised word is never changed
        self.assertEqual(ok("dementai=>dementi4"), [])                         # letters only
        self.assertEqual(ok("dementai =>dementia"), ["dementia"])               # white space around a word is trimmed
        self.assertEqual(ok("dementai=>dement ia"), [])                         # a single word
        self.assertEqual(ok("care=>carefully", "care=>cares"), ["cares"])      # +5 refused, +1 taken
        self.assertEqual(ok("[NAME]=>[NAMES]"), [])                             # a label is never changed


class BatchedExtraction(Agreement):
    """ADR-082 items 1 to 3 (rev 30): the columns to scrub are packed in order into calls of at most 5,000
    characters (separators counted); each entity goes back to its column by offset; a failed call holds every
    column of its batch."""

    @staticmethod
    def text(tag, n):
        """A synthetic column of exactly n characters whose first word is the tag (so the mock can tell columns apart)."""
        s = (tag + " " + "word " * (n // 5 + 2))[:n]
        return s[:-1] + "x" if s.endswith(" ") else s

    def row_of(self, lengths):
        cols = [raw for raw, _ in rr.SCRUB_COLUMNS]
        row = {raw: self.text(f"tag{i}", n) for i, (raw, n) in enumerate(zip(cols, lengths))}
        return row, [row[c] for c in cols[:len(lengths)]]

    def calls_for(self, lengths, **kw):
        row, texts = self.row_of(lengths)
        calls = []
        ext = cs.extractor_for([(t, []) for t in texts], calls)
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, **kw)
        return sim, dec, writes, texts, calls

    def test_the_typical_application_is_one_call_whatever_the_column_count(self):
        for n_cols in (1, 5, 12):
            sim, dec, writes, texts, calls = self.calls_for([100] * n_cols)
            self.assertEqual(len(sim.ops("aibuilderpredict_entityextraction")), 1, n_cols)
            self.assertEqual(len(sim.ops("aibuilderpredict_customprompt")), n_cols)

    def test_the_limit_is_5000_characters_including_separators(self):
        for lengths, want in (([2499, 2499], [[0, 1]]), ([2500, 2499], [[0], [1]]), ([5000], [[0]]), ([5000, 1], [[0], [1]]),
                              ([3000, 3000], [[0], [1]]), ([2000, 2000, 996], [[0, 1, 2]]), ([2000, 2000, 997], [[0, 1], [2]]),
                              ([100, 4900], [[0], [1]]), ([100, 4898], [[0, 1]])):
            with self.subTest(lengths=lengths):
                self.assertEqual(rr.plan_batches(lengths), want)
                sim, dec, writes, texts, calls = self.calls_for(lengths)
                calls = calls[:len(want)]       # compare() runs the shipped flow first, then the oracle, on one mock
                self.assertEqual(len(sim.ops("aibuilderpredict_entityextraction")), len(want))
                self.assertTrue(all(c <= 5000 for c in calls))
                # the text sent is each column exactly as stored, joined by two line feeds, in column order
                self.assertEqual(calls, [sum(len(texts[i]) for i in b) + 2 * (len(b) - 1) for b in want])

    def test_no_column_chosen_means_no_call(self):
        self.assertEqual(rr.plan_batches([]), [])
        row = {"rev_narrativeraw": "kept", "rev_narrativeredacted": "the admin's text", "rev_otherconditionraw": "   "}
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, lambda _: [])
        self.assertEqual(sim.ops("aibuilderpredict_entityextraction"), [])
        self.assertEqual(sim.status, "Succeeded")

    def test_an_entity_in_a_later_column_goes_back_to_that_column(self):
        t = ["Ann helps me.", "Then Bob visits.", "Later Cara calls on Dee."]
        row = dict(zip(["rev_narrativeraw", "rev_otherconditionraw", "rev_caresupportdescription"], t))
        found = [(t[0], ents_at(t[0], ("PersonName", "Ann"))), (t[1], ents_at(t[1], ("PersonName", "Bob"))),
                 (t[2], ents_at(t[2], ("PersonName", "Cara"), ("PersonName", "Dee")))]
        for ci in (True, False):
            sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, cs.extractor_for(found), ci=ci)
            self.assertEqual(len(sim.ops("aibuilderpredict_entityextraction")), 1)
            self.assertEqual([i["Narrative"] for _, i in sim.prompt_inputs],
                             ["[NAME] helps me.", "Then [NAME] visits.", "Later [NAME] calls on [NAME]."])
            self.assertEqual(dec.reasons, ())

    def test_an_entity_that_straddles_two_columns_holds_both(self):
        a, b = "Ring Ann", "Smith today."
        row = {"rev_narrativeraw": a, "rev_otherconditionraw": b}
        joined = a + "\n\n" + b
        value = "Ann\n\nSmith"
        ext = cs.batch_extractor(lambda text: [("PersonName", value, text.index(value), len(value), 0.9)])
        for ci in (True, False):
            sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci)
            self.assertEqual(writes, {})
            self.assertEqual([r for r in dec.reasons if r.startswith("overlapping")],
                             ["overlapping-identifiers:rev_narrativeraw", "overlapping-identifiers:rev_otherconditionraw"])
            self.assertEqual(len(joined), 8 + 2 + 12)

    def test_a_straddling_entity_holds_the_column_even_when_another_span_contains_it_there(self):
        a, b = "We see Moorside Surgery", "Ann rang."
        row = {"rev_narrativeraw": a, "rev_otherconditionraw": b}
        value = "Surgery\n\nAnn"
        ext = cs.batch_extractor(lambda text: [("PersonName", value, text.index(value), len(value), 0.9)])
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes, {})
        self.assertIn("overlapping-identifiers:rev_narrativeraw", dec.reasons)
        self.assertIn("overlapping-identifiers:rev_otherconditionraw", dec.reasons)

    def test_an_entity_inside_the_separator_touches_no_column(self):
        a, b = "Ring Ann", "Smith today."
        row = {"rev_narrativeraw": a, "rev_otherconditionraw": b}
        ext = cs.batch_extractor(lambda text: [("PersonName", "\n\n", len(a), 2, 0.9)])
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual([r for r in dec.reasons if "overlapping" in r], [])
        self.assertEqual(set(writes), {"rev_narrativeredacted", "rev_otherconditionredacted"})
        self.assertEqual(rr.map_entities([a, b], [rr.ExtractorEntity("PersonName", "\n\n", len(a), 2, 0.9)]), [[], []])

    def test_a_line_break_inside_a_column_does_not_move_the_next_columns_offsets(self):
        """The property of A-NS-41, as far as a simulator can show it: the extractor mock counts the joined text
        character by character, a CRLF inside a column included, and the flow rebases by the same count."""
        a, b = "First line\r\nAnn is here.", "\r\nBob and Cara\r\nvisit."
        row = {"rev_narrativeraw": a, "rev_otherconditionraw": b}

        def found(text):
            out = []
            for name in ("Ann", "Bob", "Cara"):
                out.append(("PersonName", name, text.index(name), len(name), 0.9))
            return out
        for ci in (True, False):
            sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, cs.batch_extractor(found), ci=ci)
            self.assertEqual([i["Narrative"] for _, i in sim.prompt_inputs],
                             ["First line\r\n[NAME] is here.", "\r\n[NAME] and [NAME]\r\nvisit."])
            self.assertEqual(rr.batch_layout([a, b]), [(0, len(a)), (len(a) + 2, len(a) + 2 + len(b))])

    def test_a_failed_batch_marks_every_column_in_it_and_no_other(self):
        row, texts = self.row_of([3900, 3900, 100])         # batches: [0] and [1, 2]
        for failing_first in (0, 1):
            def ext(text, hit=texts[failing_first]):
                if text.startswith(hit):
                    raise RuntimeError("no credits")
                return []
            for ci in (True, False):
                with self.subTest(failing_batch=failing_first, ci=ci):
                    sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci)
                    cols = [raw for raw, _ in rr.SCRUB_COLUMNS][:3]
                    bad = cols[:1] if failing_first == 0 else cols[1:]
                    self.assertEqual([r for r in dec.reasons if r.startswith("ai-error")], [f"ai-error:{c}" for c in bad])
                    self.assertEqual(set(writes), {red for raw, red in rr.SCRUB_COLUMNS[:3] if raw not in bad})
                    self.assertEqual(len(sim.ops("aibuilderpredict_customprompt")), 3 - len(bad))

    def test_an_unreadable_answer_is_a_failed_batch(self):
        sim, dec, writes, _ = self.compare({"rev_narrativeraw": "Ann helps.", "rev_otherconditionraw": "Bob helps."},
                                           cs.ALL_SETTINGS, lambda _: "UNREADABLE")
        self.assertEqual(writes, {})
        self.assertEqual(dec.reasons, ("ai-error:rev_narrativeraw", "ai-error:rev_otherconditionraw"))
        self.assertEqual(sim.ops("aibuilderpredict_customprompt"), [])

    def test_the_plan_names_columns_and_numbers_never_text(self):
        row, texts = self.row_of([300, 300, 4900])
        sim, *_ = self.calls_for([300, 300, 4900])
        plans = [v for var, v in sim.engine.assignments if var == "batchPlan" and isinstance(v, dict)]
        self.assertTrue(plans)
        for entry in plans:
            self.assertEqual(set(entry), {"raw", "red", "batch", "used"})
            self.assertTrue(all(isinstance(entry[k], int) for k in ("batch", "used")))
        self.assertEqual([(e["batch"], e["used"]) for e in plans], [(0, 300), (0, 602), (1, 4900)])

    def test_the_reference_batching(self):
        self.assertEqual(rr.plan_batches([4998, 1]), [[0], [1]])      # 4998 + 2 + 1 = 5001
        self.assertEqual(rr.plan_batches([4997, 1]), [[0, 1]])
        self.assertEqual(rr.plan_batches([10, 5000, 10]), [[0], [1], [2]])
        self.assertEqual(rr.batch_layout(["ab", "cde"]), [(0, 2), (4, 7)])
        ents = [rr.ExtractorEntity("PersonName", "b\n\nc", 1, 4, 0.9), rr.ExtractorEntity("PersonName", "de", 4, 2, 0.8)]
        got = rr.map_entities(["ab", "cde"], ents)
        self.assertEqual([(e.startIndex, e.length, e.crosses) for e in got[0]], [(1, 1, True)])
        self.assertEqual([(e.startIndex, e.length, e.crosses) for e in got[1]], [(0, 1, True), (0, 2, False)])


class FailClosedPaths(Agreement):
    TEXT = "My carer Ann visits most days."
    ENTS = [("PersonName", "Ann", 9, 3, 0.9)]

    def test_only_eligible_for_panel_runs(self):
        row, ext = one(self.TEXT, self.ENTS)
        sim = run_flow(row, {}, ext, status=5)
        self.assertEqual(sim.calls, [])

    def test_released_record_is_never_touched(self):
        row, ext = one(self.TEXT, self.ENTS)
        sim = run_flow({**row, "rev_redactionreleased": True}, cs.ALL_SETTINGS, ext)
        self.assertEqual([op for _, op in sim.calls], ["GetItem"])

    def test_no_reason_still_waits_for_the_process_owner_with_a_card(self):
        """ADR-078: no reason is not a release. Flagged, carded ("None found by the checks"), never released."""
        row, ext = one(self.TEXT, self.ENTS)
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(dec.reasons, ())
        self.assertIn("rev_narrativeredacted", writes)
        self.assertEqual(sim.decision_write["rev_redactionconfidence"], 0.9)
        self.assertNotIn("rev_redactionreleased", sim.decision_write)
        self.assertIn("None found by the checks", sim.notices[0])
        self.assertIn("Narrative ready for your review", sim.notices[0])

    def test_no_flow_action_writes_the_release_gate(self):
        """ADR-078 item 1: only a person sets rev_redactionreleased; the flow only reads it (Stop_if_already_released)."""
        for n, a in ACTIONS.items():
            params = (a.get("inputs") or {}).get("parameters") or {} if isinstance(a.get("inputs"), dict) else {}
            with self.subTest(n):
                self.assertNotIn("item/rev_redactionreleased", params)

    def test_absent_threshold_is_a_hint(self):
        row, ext = one(self.TEXT, self.ENTS)
        _, dec, writes, _ = self.compare(row, cs.RULES, ext)
        self.assertEqual(dec.reasons, ("threshold-missing-or-invalid",))
        self.assertIn("rev_narrativeredacted", writes)

    def test_no_settings_at_all_scrubs_nothing(self):
        """ADR-076 consequence 6: before the create-only seed has run, every record is held."""
        row, ext = one(self.TEXT, self.ENTS)
        sim, dec, writes, _ = self.compare(row, {}, ext)
        self.assertEqual(writes, {})
        for k in rr.RULE_KEYS:
            self.assertIn(f"redaction-setting-invalid:{k}", dec.reasons)
        self.assertEqual(sim.ops("aibuilderpredict_entityextraction"), [])

    def test_extractor_failure_is_ai_error_and_nothing_reaches_the_prompts(self):
        def boom(_):
            raise RuntimeError("no credits")
        for ext in (boom, lambda _: "UNREADABLE"):
            row = {"rev_narrativeraw": self.TEXT}
            sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
            self.assertEqual(writes, {})
            self.assertEqual(dec.reasons, ("ai-error:rev_narrativeraw",))
            self.assertEqual(sim.ops("aibuilderpredict_customprompt"), [])

    def test_a_failed_or_unusable_rewrite_is_prompt_error(self):
        for rw in (cs.failing, lambda **_: cs.answer("cut off", "Length"), lambda **_: cs.answer("   ")):
            row, ext = one(self.TEXT, self.ENTS)
            _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
            self.assertEqual(writes, {})
            self.assertEqual(dec.reasons, ("prompt-error:rev_narrativeraw",))

    def test_the_kill_switch_writes_nothing_and_calls_nothing(self):
        row, ext = one(self.TEXT, self.ENTS)
        sim, dec, writes, _ = self.compare(row, {**cs.ALL_SETTINGS, "RedactionPromptStage": "Off"}, ext)
        self.assertEqual(writes, {})
        self.assertIn("prompt-stage-off", dec.reasons)
        self.assertEqual(sim.ops("aibuilderpredict_entityextraction") + sim.ops("aibuilderpredict_customprompt"), [])

    def test_any_other_stage_value_leaves_the_prompts_on(self):
        for v in ("on", "", "of", "true"):
            row, ext = one(self.TEXT, self.ENTS)
            _, dec, writes, _ = self.compare(row, {**cs.ALL_SETTINGS, "RedactionPromptStage": v}, ext)
            self.assertIn("rev_narrativeredacted", writes)

    def test_kept_counterpart_too_long_and_empty(self):
        long_text = "word " * 1001
        row = {"rev_narrativeraw": self.TEXT, "rev_narrativeredacted": "the admin's text",
               "rev_otherconditionraw": long_text, "rev_caresupportdescription": "   "}
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, lambda _: [])
        self.assertEqual(writes, {})
        self.assertEqual(dec.reasons, ("kept-existing-counterpart:rev_narrativeraw", "too-long:rev_otherconditionraw"))
        self.assertEqual(sim.ops("aibuilderpredict_entityextraction"), [])

    def test_unmapped_type_and_partial_overlap(self):
        row, ext = one(self.TEXT, [("Mystery", "Ann", 9, 3, 0.9)])
        _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertIn("unmapped-entity-type:rev_narrativeraw", dec.reasons)
        row, ext = one(self.TEXT, [("PersonName", "carer Ann", 3, 9, 0.9), ("PersonName", "Ann visits", 9, 10, 0.9)])
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes, {})
        self.assertIn("overlapping-identifiers:rev_narrativeraw", dec.reasons)

    def test_a_contained_span_is_dropped_and_the_longer_label_wins(self):
        text = "We see Dr Patel's Surgery weekly."
        ents = [("Organization", "Dr Patel's Surgery", 7, 18, 0.8), ("PersonName", "Patel", 10, 5, 0.9)]
        row, ext = one(text, ents)
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes["rev_narrativeredacted"], "We see [GP PRACTICE] weekly.")
        self.assertEqual(sim.decision_write["rev_redactionconfidence"], 0.8)

    def test_over_4000_characters_after_the_rewrite_is_not_written(self):
        text = "help " * 900
        row, ext = one(text.strip())
        rw = cs.rewrite_then(lambda t: t + " " + "help " * 200)
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertEqual(writes, {})
        self.assertIn("redacted-exceeds-4000:rev_narrativeraw", dec.reasons)

    def test_each_residue_check_writes_and_holds(self):
        cases = {"Ring 07700 900123 today.": "digit-run", "We live in LS62AB now.": "postcode",
                 "Write to me at home@ today.": "at-sign", "We live on the high road.": "street-word",
                 "The practice is near.": "practice-word", "I am 72 years old.": "age-phrase",
                 "We are in LS6 area.": "district", "Then Ms. Brown, the lady, said no.": "gendered-term"}
        for text, kind in cases.items():
            with self.subTest(kind):
                row, ext = one(text)
                rw = cs.rewrite_then(lambda t: t.replace("person", "lady")) if kind == "gendered-term" else cs.good_rewrite
                _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
                self.assertIn(f"residual-{kind}:rev_narrativeraw", dec.reasons)
                self.assertIn("rev_narrativeredacted", writes)

    def test_a_rewrite_that_drops_text_writes_and_holds(self):
        text = "one two three four five six seven eight nine ten"
        row, ext = one(text)
        rw = cs.rewrite_then(lambda t: " ".join(t.split(" ")[:8]))
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertIn("rewrite-dropped-text:rev_narrativeraw", dec.reasons)
        self.assertIn("rev_narrativeredacted", writes)

    def test_settings_rows(self):
        row, ext = one(self.TEXT, self.ENTS)
        for settings, reason in (
                ({**cs.RULES, "RedactionConfidenceThreshold": "95"}, "below-threshold"),
                ({**cs.RULES, "RedactionConfidenceThreshold": "abc"}, "threshold-missing-or-invalid"),
                ({**cs.ALL_SETTINGS, "RedactionStreetWordsExtra": "wynd\nB4D!"}, "redaction-setting-invalid:RedactionStreetWordsExtra"),
                ({**cs.ALL_SETTINGS, "RedactionPracticeWordsExtra": "\n \n"}, "redaction-setting-invalid:RedactionPracticeWordsExtra")):
            with self.subTest(reason):
                _, dec, _, _ = self.compare(row, settings, ext)
                self.assertIn(reason, dec.reasons)
        for at in ("2026-10-15T09:00:00Z", "not a date"):         # ADR-078: modifiedon is not read at all
            _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, modified={k: at for k in cs.ALL_SETTINGS})
            self.assertEqual(dec.reasons, ())

    def test_a_retired_setting_row_is_ignored(self):
        """RedactionAutoRelease included (ADR-078): a leftover row, 'true' or not, changes nothing."""
        row, ext = one(self.TEXT, self.ENTS)
        for value in ("anything", "true"):
            settings = {**cs.ALL_SETTINGS, **{k: value for k in rr.RETIRED_KEYS}}
            _, dec, writes, _ = self.compare(row, settings, ext)
            self.assertEqual(dec.reasons, ())
            self.assertFalse(dec.released)

    def test_a_retired_neutral_terms_extra_row_is_ignored(self):
        row, ext = one(self.TEXT, self.ENTS)
        _, dec, writes, _ = self.compare(row, {**cs.ALL_SETTINGS, "RedactionNeutralTermsExtra": "not = valid = at all"}, ext)
        self.assertEqual(dec.reasons, ())

    def test_register_unavailable(self):
        row, ext = one(self.TEXT, self.ENTS)
        for reg in (None, SEED_CODES[:10]):
            _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, register=reg)
            self.assertIn("postcode-register-unavailable", dec.reasons)

    def test_no_model_detections(self):
        row, ext = one("We would love a week by the sea.")
        _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(dec.reasons, ("no-model-detections",))


def ents_at(text, *found):
    """(type, value) pairs -> extractor tuples with the offsets the value has in the text, in order."""
    out, at = [], 0
    for typ, value in found:
        at = text.index(value, at)
        out.append((typ, value, at, len(value), 0.9))
        at += len(value)
    return out


class NameFragments(Agreement):
    """Iteration 11 (IMP-1139): a fragment joined to a name by a hyphen or apostrophe never reaches the
    trustee text. The span is widened in the flow; anything still joined to a label is P3 name-fragment."""

    def _labelled(self, sim):
        return [i["Narrative"] for rid, i in sim.prompt_inputs if rid == REWRITE_ID]

    def test_a_joined_fragment_is_inside_the_label_under_both_string_semantics(self):
        cases = {  # text, extractor value, labelled text the rewrite prompt must receive
            "My name is Beatrix Holloway-Reed and I need a break.": ("Beatrix Holloway", "My name is [NAME] and I need a break."),
            "I am Oswin Pennington-Clarke": ("Oswin Pennington", "I am [NAME]"),                    # fragment at the end
            "Ask Mrs O'Brien now.": ("Brien", "Ask Mrs [NAME] now."),                                  # before the span
            "Mary-Ann helps.": ("Ann", "[NAME] helps."),
            "Ask Mrs O’Brien now.": ("Brien", "Ask Mrs [NAME] now."),                                  # curly apostrophe
            "I wash Sam's clothes.": ("Sam", "I wash [NAME]'s clothes."),                              # possessive kept
            "Sam-": ("Sam", "[NAME]-"),                                                                # no letter after
        }
        for text, (value, labelled) in cases.items():
            for ci in (True, False):
                with self.subTest(labelled, ci=ci):
                    row, ext = one(text, ents_at(text, ("PersonName", value)))
                    sim, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci)
                    self.assertEqual(self._labelled(sim), [labelled])
                    self.assertNotIn("residual-name-fragment:rev_narrativeraw", dec.reasons)

    def test_only_a_name_is_widened(self):
        text = "Ring 0113 496 0214-ext now."
        row, ext = one(text, ents_at(text, ("PhoneNumber", "0113 496 0214")))
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(self._labelled(sim), ["Ring [PHONE]-ext now."])
        self.assertIn("residual-name-fragment:rev_narrativeraw", dec.reasons)     # input side: held, written
        self.assertIn("rev_narrativeredacted", writes)

    def test_a_second_fragment_is_held_input_side(self):
        text = "Ann Smith-Jones-Brown helps me."
        row, ext = one(text, ents_at(text, ("PersonName", "Ann Smith")))
        sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(self._labelled(sim), ["[NAME]-Brown helps me."])
        self.assertIn("residual-name-fragment:rev_narrativeraw", dec.reasons)
        self.assertIn("rev_narrativeredacted", writes)

    def test_a_label_joined_in_the_rewrite_is_held_output_side(self):
        text = "Dr Ann Smith met Reed today."
        row, ext = one(text, ents_at(text, ("PersonName", "Dr Ann Smith")))
        rw = cs.rewrite_then(lambda t: t.replace("[NAME] met Reed", "[NAME]-Reed met"))
        for ci in (True, False):
            with self.subTest(ci=ci):
                _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw, ci=ci)
                self.assertIn("residual-name-fragment:rev_narrativeraw", dec.reasons)
                self.assertIn("rev_narrativeredacted", writes)
        rw = cs.rewrite_then(lambda t: t.replace("[NAME] met Reed", "[NAME]'s Reed met"))
        _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertNotIn("residual-name-fragment:rev_narrativeraw", dec.reasons)     # a possessive is not held

    def test_a_dr_title_stays_outside_the_label(self):
        for title in ("Dr", "Dr.", "Doctor", "dr"):
            text = f"{title} Adeyemi at Moorside Medical Centre reviews my medication."
            row, ext = one(text, ents_at(text, ("PersonName", f"{title} Adeyemi"), ("Organization", "Moorside Medical Centre")))
            with self.subTest(title):
                sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
                self.assertEqual(self._labelled(sim), [f"{title} [NAME] at [GP PRACTICE] reviews my medication."])
                self.assertEqual(writes["rev_narrativeredacted"], f"{title} [NAME] at [GP PRACTICE] reviews my medication.")
        text = "Dr Drew reviews me."                                 # "Dr" alone, or a name that starts "Dr": no trim
        row, ext = one(text, ents_at(text, ("PersonName", "Dr")))
        sim, _, _, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(self._labelled(sim), ["[NAME] Drew reviews me."])


class PracticeNamesTheExtractorMisses(Agreement):
    """TAD rev 29, ADR-075 item 2 "Decided: label" (IMP-1170): a capitalised practice suffix, walked back over at most
    four capitalised words (or St / St.), is labelled [GP PRACTICE] before the rewrite, whatever the extractor said."""

    def _labelled(self, text, ents=(), settings=None, ci=True):
        row, ext = one(text, list(ents))
        sim, dec, writes, _ = self.compare(row, settings or cs.ALL_SETTINGS, ext, ci=ci)
        return [i["Narrative"] for r, i in sim.prompt_inputs if r == REWRITE_ID], dec

    def test_the_tads_worked_examples(self):
        cases = {
            "Dr Adeyemi at Moorside Medical Centre reviews me.": (("PersonName", "Dr Adeyemi"),),
            "We go to The Old Mill Surgery.": (),
            "St John's Health Centre is near.": (),
            "We use St. John's Surgery now.": (),
            "I see Dr Patel's Surgery.": (("PersonName", "Patel"),),          # the extractor's name is contained
            "Yesterday Moorside Surgery rang.": (),                           # ambiguity labels more
        }
        want = {
            "Dr Adeyemi at Moorside Medical Centre reviews me.": "Dr [NAME] at [GP PRACTICE] reviews me.",
            "We go to The Old Mill Surgery.": "We go to [GP PRACTICE].",
            "St John's Health Centre is near.": "[GP PRACTICE] is near.",
            "We use St. John's Surgery now.": "We use [GP PRACTICE] now.",
            "I see Dr Patel's Surgery.": "I see [GP PRACTICE].",
            "Yesterday Moorside Surgery rang.": "[GP PRACTICE] rang.",
        }
        for text, found in cases.items():
            for ci in (True, False):
                with self.subTest(text, ci=ci):
                    lab, dec = self._labelled(text, ents_at(text, *found), ci=ci)
                    self.assertEqual(lab, [want[text]])
                    self.assertNotIn("residual-practice-word:rev_narrativeraw", dec.reasons)

    def test_iteration_14_an_extractor_span_and_a_practice_span_in_one_column_sort_on_one_type(self):
        """IMP-1198, DEV 2026-10-21, build 20261021-3, application 1086: Compose_column_outcome sorts the labelled spans
        by 'score'. An extractor span carries float(score); the practice-suffix span carried the integer literal 2, so a
        column with both was InvalidTemplate. wdl_sim.f_sort now rejects mixed Integer/Float like the platform; this
        column (a PersonName the extractor found, a practice suffix it did not) fails before the fix and is written after."""
        text = "Dr Adeyemi at Moorside Medical Centre reviews me."
        for ci in (True, False):
            with self.subTest(ci=ci):
                lab, dec = self._labelled(text, ents_at(text, ("PersonName", "Dr Adeyemi")), ci=ci)
                self.assertEqual(lab, ["Dr [NAME] at [GP PRACTICE] reviews me."])
                self.assertEqual(dec.reasons, ())

    def test_iteration_14_the_sim_rejects_a_sort_over_mixed_integer_and_float(self):
        f_sort = lambda arr: wdl_sim.Engine.f_sort(None, arr, "score")   # noqa: E731  (f_sort reads no engine state)
        with self.assertRaises(wdl_sim.WdlError):
            f_sort([{"score": 0.9}, {"score": 2}])
        self.assertEqual(f_sort([{"score": 2.0}, {"score": 0.9}])[0]["score"], 0.9)

    def test_what_is_never_labelled(self):
        for text in ("I had surgery last spring.", "The practice nurse visits.", "We use a health centre.",
                     "Surgery was cancelled.", "We went to the Surgery.", "Moorside Surgeryx is not a word."):
            for ci in (True, False):
                with self.subTest(text, ci=ci):
                    lab, _ = self._labelled(text, ci=ci)
                    self.assertEqual(lab, [text])

    def test_the_walk_stops(self):
        cases = {"I would like. Moorside Surgery rang.": "I would like. [GP PRACTICE] rang.",   # a full stop
                 "Call 01 Moorside Surgery.": "Call 01 [GP PRACTICE].",                        # a digit
                 "One Two Three Four Five Surgery.": "One [GP PRACTICE].",                     # four words at most
                 "My Moorside Surgery and Hilltop Health Centre.": "[GP PRACTICE] and [GP PRACTICE]."}
        for text, want in cases.items():
            with self.subTest(text):
                self.assertEqual(self._labelled(text)[0], [want])

    def test_an_extractor_span_partly_overlapping_a_practice_holds_the_column(self):
        text = "Moorside Surgery Ann visits."
        row, ext = one(text, ents_at(text, ("PersonName", "Surgery Ann")))
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes, {})                                     # not written
        self.assertIn("overlapping-identifiers:rev_narrativeraw", dec.reasons)

    def test_an_equal_extractor_organization_is_kept_once(self):
        text = "We see Moorside Medical Centre."
        lab, dec = self._labelled(text, ents_at(text, ("Organization", "Moorside Medical Centre")))
        self.assertEqual(lab, ["We see [GP PRACTICE]."])
        self.assertEqual(dec.confidence, 0.9)        # the extractor's score; a rule span carries none

    def test_an_extra_practice_word_is_a_suffix_capitalised(self):
        text = "We go to Moorside Walk In Clinic weekly."
        settings = {**cs.ALL_SETTINGS, "RedactionPracticeWordsExtra": "walk in clinic"}
        self.assertEqual(self._labelled(text, settings=settings)[0], ["We go to [GP PRACTICE] weekly."])
        self.assertEqual(self._labelled(text)[0], [text])
        self.assertEqual(rr.run_context(settings).practice_suffixes[-1], "Walk In Clinic")


class PunctuationFidelity(Agreement):
    """Iteration 11: the rewrite dropped full stops and commas in DEV (2026-10-19). Two or more marks fewer
    AND more than 10% fewer: written and held, rewrite-dropped-punctuation."""
    TEXT = "We pay for a cleaner twice a month, about £80, because I cannot manage the housework."

    def test_dropped_punctuation_writes_and_holds(self):
        row, ext = one(self.TEXT)
        rw = cs.rewrite_then(lambda t: t.replace(",", "").replace(".", ""))
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertIn("rewrite-dropped-punctuation:rev_narrativeraw", dec.reasons)
        self.assertIn("rev_narrativeredacted", writes)

    def test_one_mark_fewer_is_not_held(self):
        row, ext = one(self.TEXT)
        rw = cs.rewrite_then(lambda t: t.rstrip("."))
        _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=rw)
        self.assertEqual(dec.reasons, ("no-model-detections",))     # no entities in this text; nothing else


class SeededCasesSeenInDev(Agreement):
    """Iteration 11: the seeded synthetic cases TD-13 and TD-15 (src/tests/data/narrative-test-data.json), with
    the extractor answers the DEV outputs of 2026-10-19 imply (surname fragment missed; "Dr" inside the span)."""
    DATA = json.loads((REPO / "src" / "tests" / "data" / "narrative-test-data.json").read_text(encoding="utf-8"))

    def app(self, case):
        return next(c for c in self.DATA["cases"] if c["caseId"] == case)["application"]

    def test_td13_the_hyphenated_surname_and_the_dr_title(self):
        a = self.app("TD-13")
        n = a["rev_narrativeraw"]
        d = a["rev_disabilityimpactdescription"]
        c = a["rev_caresupportdescription"]
        row = {"rev_narrativeraw": n, "rev_disabilityimpactdescription": d, "rev_caresupportdescription": c}
        ext = cs.extractor_for([
            (n, ents_at(n, ("PersonName", "Beatrix Holloway"), ("Age", "68 years old"), ("PersonName", "Cormac"),
                        ("Age", "71 years old"), ("StreetAddress", "9 Quarry Road, Leeds LS6 3QT"),
                        ("PhoneNumber", "07700 900231"), ("Email", "beatrix.holloway@example.org"))),
            (d, ents_at(d, ("PersonName", "Dr Adeyemi"), ("Organization", "Moorside Medical Centre"))),
            (c, ents_at(c, ("PersonName", "Cormac"), ("PersonName", "Imogen"), ("Age", "40 years old"))),
        ])
        for ci in (True, False):
            with self.subTest(ci=ci):
                sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci)
                self.assertEqual(dec.reasons, ())
                self.assertNotIn("reed", " ".join(writes.values()).lower())
                self.assertNotIn("reed", " ".join(i["Narrative"] for _, i in sim.prompt_inputs if "Narrative" in i).lower())
                self.assertTrue(writes["rev_narrativeredacted"].startswith("My name is [NAME] and I am [AGE 65 to 74]."))
                self.assertEqual(writes["rev_disabilityimpactdescriptionredacted"],
                                 "Parkinson's makes walking slow and I fall more often than I would like. "
                                 "Dr [NAME] at [GP PRACTICE] reviews my medication every three months.")
                self.assertEqual(writes["rev_caresupportdescriptionredacted"],
                                 "My partner helps me wash and dress each morning and cooks most meals. "
                                 "Our child, who is [AGE 35 to 44], does the shopping at weekends.")

    def test_td13_the_gp_practice_is_labelled_beside_dr_name(self):
        """DEV 2026-10-20, build 20261020-1: "... Dr [NAME] at Moorside Medical Centre reviews ..." with
        residual-practice-word. Pinned here: with a name and an Organization ending in a practice suffix, the shipped
        flow labels the practice, whether the name span includes "Dr" or not (the Iteration 11 trim and widening touch
        PersonName spans only). The DEV text is reproduced only when the extractor returns no such Organization; then
        P3 flags the column, as in DEV (next test)."""
        d = self.app("TD-13")["rev_disabilityimpactdescription"]
        want = ("Parkinson's makes walking slow and I fall more often than I would like. "
                "Dr [NAME] at [GP PRACTICE] reviews my medication every three months.")
        for name in ("Dr Adeyemi", "Adeyemi"):
            for ci in (True, False):
                with self.subTest(name=name, ci=ci):
                    row = {"rev_disabilityimpactdescription": d}
                    ext = cs.extractor_for([(d, ents_at(d, ("PersonName", name), ("Organization", "Moorside Medical Centre")))])
                    sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, ci=ci)
                    self.assertEqual([i["Narrative"] for r, i in sim.prompt_inputs if r == REWRITE_ID], [want])
                    self.assertEqual(writes["rev_disabilityimpactdescriptionredacted"], want)
                    self.assertEqual(dec.reasons, ())

    def test_td13_a_practice_the_extractor_misses_is_labelled(self):
        """TAD rev 29, ADR-075 item 2 "Decided: label" (IMP-1170). The DEV shape of 2026-10-20: the extractor's
        Organization is absent, truncated or over-long. The practice is now labelled by its capitalised suffix, so the
        column is written as with a good extractor answer, and no reason is given."""
        d = self.app("TD-13")["rev_disabilityimpactdescription"]
        want = ("Parkinson's makes walking slow and I fall more often than I would like. "
                "Dr [NAME] at [GP PRACTICE] reviews my medication every three months.")
        for org in (None, "Moorside Medical", "Moorside Medical Centre reviews"):
            for ci in (True, False):
                with self.subTest(org=org, ci=ci):
                    found = [("PersonName", "Dr Adeyemi")] + ([("Organization", org)] if org else [])
                    row = {"rev_disabilityimpactdescription": d}
                    sim, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, cs.extractor_for([(d, ents_at(d, *found))]), ci=ci)
                    self.assertEqual([i["Narrative"] for r, i in sim.prompt_inputs if r == REWRITE_ID], [want])
                    self.assertEqual(writes["rev_disabilityimpactdescriptionredacted"], want)
                    self.assertEqual(dec.reasons, ())

    def test_td15_the_writers_own_name(self):
        a = self.app("TD-15")
        n = a["rev_narrativeraw"]
        row, ext = one(n, ents_at(n, ("PersonName", "Fenella Aldous"), ("Email", "f.aldous@example.org")))
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext)
        self.assertEqual(writes["rev_narrativeredacted"],
                         "I am [NAME] and since my stroke I cannot cross the street alone. The practice nurse visits "
                         "every Thursday and my sibling helps when they can. You can email me at [EMAIL].")
        self.assertEqual(dec.reasons, ("residual-street-word:rev_narrativeraw", "residual-practice-word:rev_narrativeraw"))


class RuleRows(Agreement):
    """ADR-076: the four rule rows - guard rails that fail closed, and the single source of the prompt's
    rules and of checks P2 and P3."""
    TEXT = "My carer Ann visits most days and she helps."
    ENTS = [("PersonName", "Ann", 9, 3, 0.9)]

    def held(self, key, value):
        row, ext = one(self.TEXT, self.ENTS)
        settings = {**cs.ALL_SETTINGS, key: value} if value is not None else \
            {k: v for k, v in cs.ALL_SETTINGS.items() if k != key}
        sim, dec, writes, _ = self.compare(row, settings, ext)
        self.assertEqual(writes, {})
        self.assertIn(f"redaction-setting-invalid:{key}", dec.reasons)
        self.assertEqual(sim.ops("aibuilderpredict_entityextraction") + sim.ops("aibuilderpredict_customprompt"), [])
        return dec

    def test_each_row_absent_or_blank_stops_both_prompts(self):
        for key in rr.RULE_KEYS:
            for value in (None, "", "  \r\n \n"):
                with self.subTest(key, value=repr(value)):
                    self.held(key, value)

    def test_malformed_lines(self):
        cases = {
            "RedactionNeutralTerms": ["he they", "he = they = them", "h3 = they", "he = th3y",
                                      "she = they\nher = she",            # a neutral word that is also a word to replace
                                      "a" * 41 + " = person"],
            "RedactionTitles": ["Mr\nM r", "Mr\nDoctorOfMed", "Mr\nMr2", "Mr\nMr.."],
            "RedactionLabels": ["NAME = a name", "[name] = a name", "[NAME = a name", "[ ] = nothing", "[NAME!] = x"],
        }
        for key, values in cases.items():
            for value in values:
                with self.subTest(key, value=value):
                    self.held(key, value)

    def test_none_is_an_intended_empty_list_and_other_good_forms_pass(self):
        row, ext = one(self.TEXT, self.ENTS)
        for key, value in (("RedactionTitles", "none"), ("RedactionTitles", "Mr.\r\nDame"),
                           ("RedactionLabels", "NONE"), ("RedactionLabels", "[NAME]\n[CARE HOME 2] = a home"),
                           ("RedactionNeutralTerms", cs.RULES["RedactionNeutralTerms"] + "\n\nnana = grandparent"),
                           ("RedactionNameRules", "One free-text rule.")):
            with self.subTest(key, value=value):
                _, dec, writes, _ = self.compare(row, {**cs.ALL_SETTINGS, key: value}, ext)
                self.assertNotIn(f"redaction-setting-invalid:{key}", dec.reasons)
                self.assertIn("rev_narrativeredacted", writes)

    def test_the_four_prompt_inputs_are_the_rows_as_written(self):
        """One Compose_settings feeds the prompt; the inputs are the rows with carriage returns removed."""
        row, ext = one(self.TEXT, self.ENTS)
        settings = {**cs.ALL_SETTINGS, "RedactionNameRules": "Rule one.\r\nRule two."}
        sim = run_flow(row, settings, ext)
        (rid, inp), = sim.prompt_inputs
        self.assertEqual(inp["NeutralTerms"], cs.RULES["RedactionNeutralTerms"])
        self.assertEqual(inp["Titles"], cs.RULES["RedactionTitles"])
        self.assertEqual(inp["Labels"], cs.RULES["RedactionLabels"])
        self.assertEqual(inp["NameRules"], "Rule one.\nRule two.")
        a = ACTIONS["Run_the_rewrite_prompt"]["inputs"]["parameters"]
        for n in ("NeutralTerms", "Titles", "NameRules", "Labels"):
            self.assertTrue(a[f"item/requestv2/{n}"].startswith("@outputs('Compose_settings')"), n)

    def test_the_gendered_check_is_the_row(self):
        """A-R93, pinned: P3 looks for exactly the words the row replaces. With 'she = they' in the row a model
        that leaves 'she' is held; with the line deleted the same text is written without that reason."""
        row, ext = one(self.TEXT, self.ENTS)
        lazy = lambda **_: cs.answer("My carer [NAME] visits most days and she helps.")   # noqa: E731
        _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=lazy)
        self.assertIn("residual-gendered-term:rev_narrativeraw", dec.reasons)
        no_she = "\n".join(l for l in cs.RULES["RedactionNeutralTerms"].split("\n") if not l.startswith("she ="))
        _, dec, writes, _ = self.compare(row, {**cs.ALL_SETTINGS, "RedactionNeutralTerms": no_she}, ext, rewrite=lazy)
        self.assertNotIn("residual-gendered-term:rev_narrativeraw", dec.reasons)
        self.assertIn("rev_narrativeredacted", writes)

    def test_the_title_check_matches_capitals_as_written_under_both_string_semantics(self):
        for ci in (True, False):
            for text, held in (("Ms Smith rang.", True), ("I have MS and rest.", False), ("Mr. Jones came.", True),
                               ("I miss my mum.", False)):
                with self.subTest(text=text, case_insensitive=ci):
                    row, ext = one(text)
                    keep = lambda t=text, **_: cs.answer(t.replace("mum", "parent"))   # noqa: E731
                    _, dec, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, rewrite=keep, ci=ci)
                    self.assertEqual("residual-title:rev_narrativeraw" in dec.reasons, held)

    def test_an_edit_to_a_rule_row_needs_no_reconfirmation(self):
        """ADR-078 consequence 3: no stale guard; a later edit to a rule row adds no reason."""
        row, ext = one(self.TEXT, self.ENTS)
        for key in rr.RULE_KEYS:
            with self.subTest(key):
                _, dec, _, _ = self.compare(row, cs.ALL_SETTINGS, ext, modified={key: "2026-10-20T09:00:00Z"})
                self.assertEqual(dec.reasons, ())

    def test_the_seed_in_every_settings_file_is_the_oracles_and_create_only(self):
        """ADR-076 item 6: each environment's settings file seeds the four rows once (createOnly), with the
        same text as rr.SEED_ROWS, and the seeded rows make a valid rule set."""
        folder = REPO / "provisioning" / "deploymentSettings"
        for name in ("dev-scoring-settings.json", "test-settings.json", "prd-settings.json"):
            rows = {r["key"]: r for r in json.loads((folder / name).read_text(encoding="utf-8"))["dataverse"]["settingRows"]}
            for key in rr.RULE_KEYS:
                with self.subTest(name, key=key):
                    self.assertEqual(rows[key]["value"], rr.SEED_ROWS[key])
                    self.assertIs(rows[key].get("createOnly"), True)
                    self.assertEqual(rows[key]["dataType"], "Text")
                    self.assertIn("Synthetic examples only", rows[key]["description"])
            with self.subTest(name, key="RedactionConfidenceThreshold"):     # ADR-078 item 5
                self.assertEqual(rows["RedactionConfidenceThreshold"]["value"], rr.THRESHOLD_SEED)
                self.assertIs(rows["RedactionConfidenceThreshold"].get("createOnly"), True)
            others = [k for k in rows if k.startswith("Redaction") and k not in rr.RULE_KEYS
                      and k != "RedactionConfidenceThreshold"]
            self.assertEqual(others, [], "no other Redaction* row is seeded: a deploy would overwrite the owner's edit")
            self.assertNotIn("RedactionAutoRelease", rows)
        self.assertTrue(rr.SEED_CONTEXT().rules_ok)
        self.assertTrue(all(len(v) <= 4000 for v in rr.SEED_ROWS.values()))


class TheFailureHandler(unittest.TestCase):
    """ADR-075 item 9: one handler after the main scope - hold, run link, alert, end the run as Failed."""

    def test_a_failed_write_holds_alerts_once_and_fails_the_run(self):
        for stop in (False, True):
            row, ext = one("My carer Ann visits.", [("PersonName", "Ann", 9, 3, 0.9)])
            sim = run_flow(row, cs.ALL_SETTINGS, ext, fail_write=True, stop_loops_on_failure=stop)
            self.assertEqual(sim.status, "Failed")
            self.assertEqual(sim.decision_write, {"rev_redactionreviewrequired": True})     # ADR-078: release never written
            self.assertEqual(len(sim.alerts), 1)
            self.assertNotIn("Ann", json.dumps(sim.alerts))
            self.assertEqual(sim.alerts[0]["text_3"], "APP-0001")

    def test_a_failure_anywhere_in_the_column_holds_and_alerts(self):
        names = [n for n, a in ACTIONS.items() if a["type"] in ("Compose", "Select", "Query")
                 and n in dict(walk(ACTIONS["Label_rewrite_and_check_the_column"]["actions"]))]
        self.assertGreater(len(names), 20)
        for name in names:
            with self.subTest(name):
                d = copy.deepcopy(DEFINITION)
                a = dict(walk(d["actions"]))[name]
                if a["type"] == "Compose":
                    a["inputs"] = "@int('not a number')"
                else:
                    a["inputs"]["from"] = "@int('not a number')"
                row, ext = one("My carer Ann visits.", [("PersonName", "Ann", 9, 3, 0.9)])
                sim = run_flow(row, cs.ALL_SETTINGS, ext, definition=d)
                self.assertEqual(sim.status, "Failed")
                self.assertEqual(sim.decision_write["rev_redactionreviewrequired"], True)
                self.assertEqual(sim.column_writes, {})
                self.assertEqual(len(sim.alerts), 1)


class RunHistoryAndVariables(unittest.TestCase):
    """C-DOM-004, NFR-012: no narrative text in run history where secureData does not hide it, and none in
    any variable or notification."""
    TEXT = (f"My husband {CANARY} Pmrtk lives at 14 {CANARY} Road, Leeds; mail {CANARY.lower()}@example.org. "
            f"Dr {CANARY}'s Surgery knows. I am 72 years old and {CANARY} said so.")

    def _run(self, **kw):
        t = self.TEXT
        ents = [("PersonName", f"{CANARY} Pmrtk", t.index(CANARY), len(CANARY) + 6, 0.9),
                ("StreetAddress", f"14 {CANARY} Road, Leeds", t.index("14 "), len(f"14 {CANARY} Road, Leeds"), 0.8),
                ("Email", f"{CANARY.lower()}@example.org", t.index(CANARY.lower()), len(CANARY) + 12, 0.99),
                ("Organization", f"Dr {CANARY}'s Surgery", t.index("Dr "), len(f"Dr {CANARY}'s Surgery"), 0.7),
                ("Age", "72 years old", t.index("72"), 12, 0.95)]
        row, ext = one(t, ents)
        return run_flow(row, cs.RULES, ext, **kw)

    def test_the_canary_run_labels_what_the_extractor_found_and_p1_reads_values_only(self):
        """P1 searches for each VALUE the extractor returned ('Zqxwvy Pmrtk'), so a bare 'Zqxwvy' the
        extractor did not return is not a hit: it is the prompt's to label, and here the stand-in does not.
        The run-history tests below need that text to reach the write."""
        sim = self._run()
        self.assertEqual(sim.column_writes["rev_narrativeredacted"],
                         f"My partner lives at [ADDRESS]; mail [EMAIL]. [GP PRACTICE] knows. I am [AGE 65 to 74] and {CANARY} said so.")

    def test_every_action_that_sees_text_hides_it(self):
        for kw in ({}, {"fail_write": True}):
            sim = self._run(**kw)
            exempt = {"If", "Scope", "Switch", "Terminate", "Foreach"}
            leaks = []
            for r in sim.engine.records:
                if r.type in exempt:
                    continue
                blob_in = json.dumps(r.inputs, ensure_ascii=False).lower()
                blob_out = json.dumps(r.outputs, ensure_ascii=False).lower()
                secure_in = "inputs" in r.secure
                secure_out = "outputs" in r.secure or (r.type == "Compose" and secure_in)
                if r.type in ("SetVariable", "AppendToArrayVariable", "InitializeVariable"):
                    secure_in = secure_out = False
                if CANARY.lower() in blob_in and not secure_in:
                    leaks.append(f"{r.name} inputs")
                if CANARY.lower() in blob_out and not secure_out:
                    leaks.append(f"{r.name} outputs")
            self.assertEqual(sorted(set(leaks)), [])

    def test_no_variable_ever_holds_text(self):
        sim = self._run()
        for var, val in sim.engine.assignments:
            self.assertNotIn(CANARY.lower(), json.dumps(val).lower(), var)

    def test_the_notification_carries_reference_and_codes_only(self):
        sim = self._run()
        self.assertEqual(len(sim.notices), 1)
        self.assertNotIn(CANARY.lower(), sim.notices[0].lower())
        self.assertIn("APP-0001", sim.notices[0])

    def test_every_dataverse_read_and_write_of_the_application_is_secured_both_ways(self):
        """D-1 (test report 20261016-3): GetItem returns the row, and so does every update, and the row holds
        the 12 raw narratives. All 15 actions on rev_applications hide their outputs, and the 14 writes their inputs too (A-NS-39)."""
        found = []
        for n, a in ACTIONS.items():
            inputs = a.get("inputs") if isinstance(a.get("inputs"), dict) else {}
            if (inputs.get("parameters") or {}).get("entityName") == "rev_applications":
                found.append(n)
                props = a["runtimeConfiguration"]["secureData"]["properties"]
                self.assertIn("outputs", props, n)            # the returned row
                if inputs["host"]["operationId"] == "UpdateOnlyRecord":
                    self.assertIn("inputs", props, n)         # the written text (a GetItem's inputs are ids only)
        self.assertEqual(len(found), 15, sorted(found))   # Get_the_application, 12 counterparts, decision, hold

    def test_the_trigger_and_every_ai_call_are_secured_both_ways(self):
        trig = next(iter(DEFINITION["triggers"].values()))
        self.assertIn("outputs", trig["runtimeConfiguration"]["secureData"]["properties"])
        for n, a in ACTIONS.items():
            inputs = a.get("inputs") if isinstance(a.get("inputs"), dict) else {}
            if (inputs.get("host") or {}).get("operationId", "").startswith("aibuilderpredict"):
                self.assertEqual(a["runtimeConfiguration"]["secureData"]["properties"], ["inputs", "outputs"], n)


class DefinitionShape(unittest.TestCase):
    """ADR-075, 'The flow a maker reads'."""

    def test_size_and_nesting_stay_what_a_maker_can_read(self):
        """About 95 actions in the TAD's rev 23 estimate; 97 as built (Dev Summary Iteration 10); 100 with Iteration 11's
        name-fragment widening and check (3 actions); 97 after ADR-078 removed the auto-release reads and the If; 100
        with rev 29's practice spans; 109 with rev 30 (ADR-082: the batch plan and the nested batch loop, minus the
        spelling call). A ceiling, not a count: ADR-082 item 8 raises it to 125 and the nesting limit to 6 (the platform
        allows 500 and 8, Microsoft Learn, read 2026-10-21); a change that would cross it goes back to the reviewer with
        what it proposes to remove."""
        self.assertLessEqual(len(ACTIONS), 125)

        def depth(actions, d=0):
            return max([d] + [depth(sub, d + 1) for _, a in actions.items()
                              for sub in [a.get("actions"), (a.get("else") or {}).get("actions")]
                              + [c.get("actions") for c in (a.get("cases") or {}).values()] if isinstance(sub, dict) and sub])
        self.assertLessEqual(depth(DEFINITION["actions"]), 6)
        self.assertEqual(depth(DEFINITION["actions"]), 6)    # the batch loop wraps the column loop: exactly one level more

    def test_every_expression_is_under_the_platform_limit(self):
        """Microsoft Learn (Limits of automated, scheduled and instant flows, read 2026-10-21): an expression holds
        8,192 characters. The pair rule's Select and the two Compose_check_texts forms are the longest new ones."""
        longest = []

        def scan(v, where):
            if isinstance(v, str):
                longest.append((len(v), where))
            elif isinstance(v, dict):
                for k, x in v.items():
                    scan(x, f"{where}.{k}")
            elif isinstance(v, list):
                for x in v:
                    scan(x, where)
        for n, a in ACTIONS.items():
            scan(a.get("inputs"), n)
        self.assertLess(max(longest)[0], 8192, max(longest))

    def test_no_compose_in_any_flow_secures_outputs(self):
        """DEV 2026-10-20: the designer refused to save the scrub flow, "InvalidSecureDataConfiguration ...
        'outputs' are not supported in 'properties'" (0x80060467) on Compose_raw_classes. A Compose's outputs are
        its inputs, so ['inputs'] secures both; pack and import accepted the bad shape. Every flow in the solution.
        The same rule is check 18 of scripts/verify-flow-definition-language.py."""
        bad = []
        for f in sorted(FLOW.parent.glob("*.json")):
            for name, a in walk(json.loads(f.read_text(encoding="utf-8"))["properties"]["definition"]["actions"]):
                props = ((a.get("runtimeConfiguration") or {}).get("secureData") or {}).get("properties") or []
                if a.get("type") == "Compose" and "outputs" in props:
                    bad.append(f"{f.name}: {name}")
        self.assertEqual(bad, [])
        self.assertEqual(ACTIONS["Compose_raw_classes"]["runtimeConfiguration"]["secureData"]["properties"], ["inputs"])

    def test_no_until_no_result_and_four_variables(self):
        blob = json.dumps(DEFINITION)
        self.assertNotIn('"Until"', blob)
        self.assertNotIn("result(", blob)
        inits = [a["inputs"]["variables"][0]["name"] for a in ACTIONS.values() if a["type"] == "InitializeVariable"]
        self.assertEqual(inits, ["reasons", "scores", "anyScrubbed", "batchPlan"])
        # check 4 (InitializeVariable scoping): all four at the top level, never inside the scope or a loop
        self.assertEqual([n for n, a in DEFINITION["actions"].items() if a["type"] == "InitializeVariable"],
                         ["Initialise_reasons", "Initialise_scores", "Initialise_any_scrubbed", "Initialise_batch_plan"])

    def test_the_constants_are_the_oracles(self):
        c = ACTIONS["Compose_constants"]["inputs"]
        self.assertEqual([(x["raw"], x["red"]) for x in c["columns"]], rr.SCRUB_COLUMNS)
        self.assertEqual(c["labels"], rr.LABEL_BY_CODE)
        self.assertEqual(c["typeCodes"], rr.EXTRACTOR_TYPE_CODE)
        self.assertEqual(c["numberWords"], rr.NUMBER_WORDS)
        self.assertEqual(c["closedWords"], rr.closed_words())
        self.assertNotIn("genderedWords", c)        # rev 23: the gendered list is the RedactionNeutralTerms row
        self.assertEqual(c["streetWords"], rr.STREET_WORDS)
        self.assertEqual(c["practiceWords"], rr.PRACTICE_WORDS)
        self.assertEqual((c["batchLimit"], c["separator"], c["correctionsMark"], c["pairLengthChange"]),
                         (rr.BATCH_LIMIT, rr.BATCH_SEPARATOR, rr.CORRECTIONS_MARK, rr.PAIR_MAX_LENGTH_CHANGE))   # ADR-082 items 1, 5, 6
        sel = json.dumps(ACTIONS["Select_spans"]["inputs"]["select"]["code"])
        for s in rr.GP_SUFFIXES:
            self.assertIn(f"' {s}'", sel)

    def test_the_label_set_is_read_from_one_place(self):
        """Reviewer, 2026-10-16: labels change once more after Emily's test. Every label text in the flow
        comes from Compose_constants: no other action spells one, and the closed list holds every word of
        every label in the map (so P2 accepts a label the map adds)."""
        consts = json.dumps(ACTIONS["Compose_constants"]["inputs"]["labels"])
        for n, a in ACTIONS.items():
            if n == "Compose_constants":
                continue
            blob = json.dumps(a.get("inputs"))
            for label in rr.LABEL_BY_CODE.values():
                self.assertNotIn(label, blob, n)
        self.assertTrue(all(label in consts for label in rr.LABEL_BY_CODE.values()))
        self.assertTrue(set(rr.label_words()) <= set(ACTIONS["Compose_constants"]["inputs"]["closedWords"]))
        self.assertIn("[FAMILY MEMBER]", rr.LABEL_BY_CODE.values())   # kept by decision, 2026-10-16

    def test_the_columns_are_every_redacted_pair_in_entity_xml(self):
        xml = ENTITY_XML.read_text(encoding="utf-8")
        for raw, red in rr.SCRUB_COLUMNS:
            self.assertIn(f'Name="{raw}"', xml)
            self.assertIn(f'Name="{red}"', xml)

    def test_every_counterpart_has_exactly_one_write(self):
        sw = ACTIONS["Write_the_counterpart"]
        cases = {c["case"]: c["actions"] for c in sw["cases"].values()}
        self.assertEqual(set(cases), {red for _, red in rr.SCRUB_COLUMNS})
        for red, actions in cases.items():
            (a,) = actions.values()
            self.assertEqual(a["inputs"]["host"]["operationId"], "UpdateOnlyRecord")
            self.assertEqual([k for k in a["inputs"]["parameters"] if k.startswith("item/")], [f"item/{red}"])

    def test_the_prompt_run_actions_carry_the_exported_ids_and_the_tad_inputs(self):
        """A-NS-31, closed: the recordIds are the exported components' ids, named once each (C-TECH-051:
        never invented; until 2026-10-16 they were placeholders). The input names are the TAD's (rev 23): Narrative, NeutralTerms, Titles, NameRules,
        Labels; Text."""
        rw = ACTIONS["Run_the_rewrite_prompt"]
        self.assertEqual(rw["inputs"]["parameters"]["recordId"], REWRITE_ID)
        self.assertEqual(set(rw["inputs"]["parameters"]), {"recordId"} | {f"item/requestv2/{n}" for n in PROMPT_INPUTS[REWRITE_ID]})
        blob = json.dumps(DEFINITION)
        self.assertEqual(blob.count(REWRITE_ID), 1)
        # ADR-082 item 4: the spelling prompt, and the three actions that called and read it, are gone
        self.assertNotIn(RETIRED_SPELLING_ID, blob)
        for gone in ("Run_the_spelling_prompt", "Compose_spelling", "Select_spelling_words", "Extract_entities_from_the_column",
                     "Compose_entities"):
            self.assertNotIn(gone, ACTIONS)
            self.assertNotIn(gone, blob)
        self.assertNotIn("122be8e0-4b6b-44cd-a9a9-d1faff162b02", blob)   # the rev 20 detector prompt is not called

    def test_every_setting_the_tad_keeps_is_read_and_no_retired_one(self):
        for key in ["RedactionConfidenceThreshold", "RedactionPromptStage", *rr.WORD_LIST_KEYS,
                    *rr.RULE_KEYS]:
            self.assertIn(f"Find_setting_{key}", ACTIONS)
        blob = json.dumps(DEFINITION).lower()
        for key in rr.RETIRED_KEYS:
            self.assertNotIn(key.lower(), blob)


if __name__ == "__main__":
    unittest.main()
