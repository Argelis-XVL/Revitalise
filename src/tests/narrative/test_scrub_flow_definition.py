#!/usr/bin/env python3
"""Executes the SHIPPED `REV | Narrative | Scrub Free-Text` definition, rebuilt to TAD rev 22 / ADR-075 in
Iteration 9 (wbs:5.3, 5.6), and compares it with the flow model in redaction_reference.py.

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

Level: a definition-level execution in wdl_sim.py, not a platform run. The two prompts are STAND-INS
(corpus_support.py): a good model, and bad models written to break the checks. What this proves is the
property ADR-075 rests on: whatever the models answer, the flow writes a column only when P1 (no
extractor value survives) and P2 (the rewrite added no word) pass, and the spelling answer is accepted
only word by word. It proves nothing about the live models' quality (wbs:5.7), the AI Builder wire
shapes (A-NS-13, A-NS-16, A-NS-31) or a designer save (V4).

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

# A-NS-31, closed 2026-10-16: the two prompt components' ids, as exported from DEV after R1b
# (test_prompt_component.py reads the same ids out of Other/Customizations.xml).
REWRITE_ID = "e853d7c8-dd36-4917-951f-50108a812fc4"
SPELLING_ID = "763cff31-d653-416b-a52f-7e6f400bce21"
PROMPT_INPUTS = {REWRITE_ID: {"Narrative", "NeutralTerms", "Titles", "NameRules", "Labels"}, SPELLING_ID: {"Text"}}
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


def run_flow(row, settings, extract, rewrite=cs.good_rewrite, spelling=cs.echo_spelling, *, status=6,
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
                ans = (rewrite if rid == REWRITE_ID else spelling)(**inputs)
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


def model(row, settings, extract, rewrite=cs.good_rewrite, spelling=cs.echo_spelling, **kw):
    if kw.get("register", SEED) is SEED:
        kw.pop("register", None)
    return rr.flow_scrub_record(row, settings, extract, rewrite, spelling, **kw)


class Agreement(unittest.TestCase):
    """The shipped JSON and the oracle give the same writes, reasons and decision."""

    def compare(self, row, settings, extract, rewrite=cs.good_rewrite, spelling=cs.echo_spelling, ci=True, **kw):
        sim = run_flow(row, settings, extract, rewrite, spelling, case_insensitive=ci, **kw)
        dec, writes, outcomes = model(row, settings, extract, rewrite, spelling, **kw)
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
                self.assertEqual(len(sim.ops("aibuilderpredict_entityextraction")), len(chunk))
                self.assertEqual(len(sim.ops("aibuilderpredict_customprompt")), 2 * len(chunk))

    def test_the_model_never_receives_a_value_the_extractor_found(self):
        """ADR-075 item 2: the rewrite prompt gets the labelled text, so no labelled span's text reaches it."""
        for s, plain, gold in cs.corpus():
            ents = cs.simulated_entities(s, plain, gold)
            row, ext = one(plain, ents)
            sim = run_flow(row, cs.RULES, ext)
            (rid, inp), (rid2, inp2) = sim.prompt_inputs
            self.assertEqual((rid, rid2), (REWRITE_ID, SPELLING_ID))
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


class SpellingAcceptedWordByWord(Agreement):
    TEXT = "I care for my partner who has dementai and needs help."

    def run_with(self, spelling):
        row, ext = one(self.TEXT)
        return self.compare(row, cs.ALL_SETTINGS, ext, spelling=spelling)

    def test_a_near_spelling_of_a_lower_case_word_is_taken(self):
        _, _, writes, _ = self.run_with(cs.spelling_from({"dementai": "dementia"}))
        self.assertEqual(writes["rev_narrativeredacted"], "I care for my partner who has dementia and needs help.")

    def test_an_answer_with_a_different_word_count_is_discarded(self):
        _, dec, writes, _ = self.run_with(lambda Text: cs.answer(Text.replace("dementai", "demen tia")))
        self.assertEqual(writes["rev_narrativeredacted"], self.TEXT)
        self.assertFalse([r for r in dec.reasons if "spell" in r])

    def test_each_refused_change_is_refused_at_that_word_only(self):
        fixes = {"dementai": "dementia",       # taken
                 "I": "We",                    # capitalised: refused
                 "help.": "help!",             # punctuation: refused
                 "partner": "husband",         # closed-list word, and a different first letter: refused
                 "who": "wha"}                 # taken (same first letter, same length)
        _, _, writes, _ = self.run_with(cs.spelling_from(fixes))
        self.assertEqual(writes["rev_narrativeredacted"], "I care for my partner wha has dementia and needs help.")

    def test_a_label_is_never_changed(self):
        row, ext = one("Ring Ann on Mondya.", [("PersonName", "Ann", 5, 3, 0.9)])
        spell = cs.spelling_from({"[NAME]": "[NAMES]", "them": "then", "Mondya.": "Monday."})
        sim, _, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, spelling=spell)
        self.assertEqual(writes["rev_narrativeredacted"], "Ring them on Mondya.")

    def test_a_correction_never_brings_back_a_gendered_word(self):
        """FR-100: 'sun' to 'son' keeps the first letter and the length, and is still refused."""
        self.assertFalse(rr.take_correction("sun", "son"))
        self.assertTrue(rr.take_correction("sunn", "sun"))
        row, ext = one("We sit in the sun and the breze.")
        _, _, writes, _ = self.compare(row, cs.ALL_SETTINGS, ext, spelling=cs.spelling_from({"sun": "son", "breze.": "breeze."}))
        self.assertEqual(writes["rev_narrativeredacted"], "We sit in the sun and the breeze.")

    def test_a_failed_spelling_call_writes_the_rewrite_with_no_reason(self):
        _, dec, writes, _ = self.run_with(cs.failing)
        self.assertEqual(writes["rev_narrativeredacted"], self.TEXT)
        self.assertEqual(dec.reasons, ("no-model-detections",))   # no entity in this text; nothing about spelling


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
        (rid, inp), _ = sim.prompt_inputs
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
        name-fragment widening and check (3 actions); 97 after ADR-078 removed the auto-release reads and the If. A ceiling,
        not a count: a later change that grows the flow back towards rev 20's 313 fails here."""
        self.assertLessEqual(len(ACTIONS), 100)

        def depth(actions, d=0):
            return max([d] + [depth(sub, d + 1) for _, a in actions.items()
                              for sub in [a.get("actions"), (a.get("else") or {}).get("actions")]
                              + [c.get("actions") for c in (a.get("cases") or {}).values()] if isinstance(sub, dict) and sub])
        self.assertLessEqual(depth(DEFINITION["actions"]), 5)

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

    def test_no_until_no_result_and_three_variables(self):
        blob = json.dumps(DEFINITION)
        self.assertNotIn('"Until"', blob)
        self.assertNotIn("result(", blob)
        inits = [a["inputs"]["variables"][0]["name"] for a in ACTIONS.values() if a["type"] == "InitializeVariable"]
        self.assertEqual(inits, ["reasons", "scores", "anyScrubbed"])

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
        rw, sp = ACTIONS["Run_the_rewrite_prompt"], ACTIONS["Run_the_spelling_prompt"]
        self.assertEqual(rw["inputs"]["parameters"]["recordId"], REWRITE_ID)
        self.assertEqual(sp["inputs"]["parameters"]["recordId"], SPELLING_ID)
        self.assertEqual(set(rw["inputs"]["parameters"]), {"recordId"} | {f"item/requestv2/{n}" for n in PROMPT_INPUTS[REWRITE_ID]})
        self.assertEqual(set(sp["inputs"]["parameters"]), {"recordId", "item/requestv2/Text"})
        blob = json.dumps(DEFINITION)
        self.assertEqual(blob.count(REWRITE_ID), 1)
        self.assertEqual(blob.count(SPELLING_ID), 1)
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
