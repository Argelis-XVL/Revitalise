#!/usr/bin/env python3
"""Executes the SHIPPED `REV | Narrative | Scrub Free-Text` definition (wbs:5.3) and compares it with
the flow model in redaction_reference.py, over the 20-sample corpus and every fail-closed path.

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

Level: this is a definition-level execution in wdl_sim.py, not a platform run. It proves the JSON
does what the model does under the strictest reading of every uncertain semantic (wdl_sim.py's
header). It proves nothing about the AI Builder actions' real wire shape (A-NS-13, A-NS-16, A-NS-25)
or about the platform's own functions beyond their documented behaviour (A-NS-15). Those wait for DEV.

The prompt run action (Iteration 4) is the SHIPPED one: the mock below answers its real operation id,
checks it names the exported component and passes exactly the inputs the export declares, and wraps
each answer in the body path the flow reads (`prompt_wrap`; a test overrides it to prove a wrong path
fails closed).
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

import redaction_reference as rr  # noqa: E402
import wdl_sim  # noqa: E402
from test_flow_model import ALL_SETTINGS, corpus, simulated_entities  # noqa: E402

REPO = HERE.parents[2]
FLOW = (REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Workflows"
        / "REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json")
DEFINITION = json.loads(FLOW.read_text(encoding="utf-8"))["properties"]["definition"]
from test_prompt_component import INPUTS as PROMPT_INPUTS, model_id  # noqa: E402

PROMPT_MODEL_ID = model_id()


def platform_body(answer):
    """A-NS-25: where the flow reads the run action's answer. The mock puts it there by default."""
    return None if answer is None else {"responsev2": {"predictionOutput": answer}}
CANARY = "Zqxwvy"   # a made-up word: wherever it shows up in a run record, narrative text is there


@dataclass
class Run:
    status: str
    calls: list
    column_writes: dict
    decision_write: dict | None
    notices: list
    alerts: list
    engine: wdl_sim.Engine

    @property
    def reasons(self):
        return tuple(self.engine.results["Compose_decision"]["outputs"]["reasons"])


SEED_CODES = rr.load_register()
SEED = object()
OTHER_SETTING = {"rev_name": "PostcodeRegionMap", "rev_value": "{\"LS\": 1}", "modifiedon": "2026-10-07T10:00:00Z"}


def run_flow(row: dict, settings: dict, extract, status=6, case_insensitive=True, fail_get=False,
             fail_write=False, modified=None, register=SEED, definition=None, prompt=None,
             prompt_wrap=platform_body) -> Run:
    """`register`: the codes the register read returns (SEED: the seed file), or None for a failed
    read. `modified`: rev_setting name -> modifiedon (default one fixed time). `prompt`: the answer to
    each prompt call (None: the call fails, as the model treats a missing call). `prompt_wrap`: the
    body shape around that answer. `definition`: a mutated copy of the JSON, for mutation tests."""
    calls, column_writes, notices, alerts = [], {}, [], []
    decision = {}
    modified = modified or {}

    def connector(name, op, params):
        calls.append((name, op))
        if op == "GetItem":
            if fail_get:
                raise wdl_sim.ConnectorFailure("Dataverse refused the read")
            return {"rev_applicationid": "app-1", "rev_name": "APP-0001", **row}
        if op == "ListRecords" and params["entityName"] == "rev_settings":
            assert "$filter" not in params, "TAD 5.5.1: every row is read and filtered in the flow"
            rows = [{"rev_name": k, "rev_value": v, "modifiedon": modified.get(k, rr.DEFAULT_MODIFIED)}
                    for k, v in settings.items()]
            return {"value": rows + [OTHER_SETTING]}   # a newer non-Redaction row the guard rails must ignore
        if op == "ListRecords" and params["entityName"] == "rev_citysettlementregisters":
            assert params["$select"] == "rev_name" and "$filter" not in params, "ADR-073 item 7: no text reaches a query"
            codes = SEED_CODES if register is SEED else register
            if codes is None:
                raise wdl_sim.ConnectorFailure("register read failed")
            return {"value": [{"rev_name": c} for c in codes]}
        if op == "aibuilderpredict_customprompt":
            assert params["recordId"] == PROMPT_MODEL_ID, "the run action names the exported component"
            assert set(params) == {"recordId"} | {f"item/requestv2/{n}" for n in PROMPT_INPUTS}, sorted(params)
            if prompt is None:
                raise wdl_sim.ConnectorFailure("no prompt answer configured for this test")
            request = {n: params[f"item/requestv2/{n}"] for n in sorted(PROMPT_INPUTS)}
            try:
                return prompt_wrap(prompt(request))
            except Exception as e:  # noqa: BLE001 - any mock failure makes the ACTION fail
                raise wdl_sim.ConnectorFailure(str(e)) from e
        if op in ("UpdateRecord", "UpdateOnlyRecord"):
            items = {k[5:]: v for k, v in params.items() if k.startswith("item/")}
            if name.startswith("Write_rev_"):
                if fail_write:
                    raise wdl_sim.ConnectorFailure("Dataverse refused the write")
                column_writes.update(items)
            else:
                decision[name] = items
            return {}
        if op == "aibuilderpredict_entityextraction":
            assert params["item/requestv2/language"] == "en"
            text = params["item/requestv2/text"]
            assert 0 < len(text) <= rr.PREBUILT_MAX_CHARS
            try:
                ents = extract(text)
            except Exception as e:  # noqa: BLE001 - any mock failure makes the ACTION fail
                raise wdl_sim.ConnectorFailure(str(e)) from e
            if ents == "UNREADABLE":
                return {"responsev2": {"predictionOutput": {}}}
            return {"responsev2": {"predictionOutput": {"results": [
                {"type": e.type, "value": e.value, "startIndex": e.startIndex, "length": e.length, "score": e.score}
                for e in ents]}}}
        if op in ("PostCardToConversation", "PostMessageToConversation"):
            notices.append(params["body/messageBody"])
            return {}
        raise AssertionError(f"unexpected connector call {name} {op}")

    engine = wdl_sim.Engine(
        definition or DEFINITION, {"rev_applicationid": "app-1", "rev_status": status, "rev_name": "APP-0001"},
        parameters={"rev_ProcessOwnerUpn": "owner@example.org", "rev_GrantAdminAppUrl": "https://example.org/main.aspx?appid=1"},
        connector=connector, child_flow=lambda n, b: alerts.append(b), case_insensitive=case_insensitive)
    status_ = engine.run()
    return Run(status_, calls, column_writes, decision.get("Write_the_decision") or decision.get("Hold_the_record_for_review"),
               notices, alerts, engine)


def multi_extractor(texts_and_entities):
    """One mock call for a row whose columns hold different corpus samples."""
    def call(window):
        for plain, ents in texts_and_entities:
            off = plain.find(window)
            if off >= 0:
                return [rr.ExtractorEntity(t, v, s - off, n, sc) for t, v, s, n, sc in ents
                        if s >= off and s + n <= off + len(window)]
        raise AssertionError("window from no known text")
    return call


def model(row, settings, extract, **kw):
    if kw.get("register", SEED) is SEED:
        kw.pop("register", None)
    return rr.flow_scrub_record(row, settings, extract, **kw)


class FlowAgreesWithModelOnCorpus(unittest.TestCase):
    def _compare(self, row, settings, extract, ci=True):
        sim = run_flow(row, settings, extract, case_insensitive=ci)
        dec, writes = model(row, settings, extract)
        self.assertEqual(sim.column_writes, writes)
        self.assertEqual(sim.reasons, dec.reasons)
        self.assertEqual(sim.decision_write, {"rev_redactionreleased": dec.released,
                                              "rev_redactionreviewrequired": dec.review_required,
                                              "rev_redactionconfidence": dec.confidence})
        self.assertEqual(bool(sim.notices), dec.review_required)
        return sim

    def test_each_sample_alone_in_the_narrative_column_both_string_semantics(self):
        for ci in (True, False):
            for s, plain, gold in corpus():
                for settings in ({}, ALL_SETTINGS):
                    with self.subTest(s["id"], case_insensitive=ci, settings=bool(settings)):
                        ents = simulated_entities(s, plain, gold)
                        sim = self._compare({"rev_narrativeraw": plain}, settings, multi_extractor([(plain, ents)]), ci)
                        self.assertEqual(sim.column_writes["rev_narrativeredacted"], s["expected"])

    def test_samples_spread_across_all_twelve_columns(self):
        samples = list(corpus())
        for chunk in (samples[:12], samples[12:]):
            row, texts = {}, []
            for (raw, _), (s, plain, gold) in zip(rr.SCRUB_COLUMNS, chunk):
                row[raw] = plain
                texts.append((plain, simulated_entities(s, plain, gold)))
            with self.subTest(first=chunk[0][0]["id"]):
                sim = self._compare(row, ALL_SETTINGS, multi_extractor(texts))
                self.assertEqual(len(sim.column_writes), len(chunk))


class FailClosedPaths(unittest.TestCase):
    TEXT = "My carer Ann visits. Call 07700 900123."
    ENTS = [rr.ExtractorEntity("PersonName", "Ann", 9, 3, 0.9)]

    def _ext(self, ents=None):
        e = self.ENTS if ents is None else ents
        return lambda w: e

    def test_only_eligible_for_panel_runs(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT}, ALL_SETTINGS, self._ext(), status=5)
        self.assertEqual((sim.status, sim.calls), ("Succeeded", []))

    def test_released_record_is_never_touched(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT, "rev_redactionreleased": True}, ALL_SETTINGS, self._ext())
        self.assertEqual([op for _, op in sim.calls], ["GetItem"])
        self.assertEqual((sim.column_writes, sim.decision_write), ({}, None))

    def test_release_with_all_settings_and_no_reason(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT}, ALL_SETTINGS, self._ext())
        self.assertEqual(sim.column_writes, {"rev_narrativeredacted": "My carer [NAME] visits. Call [PHONE]."})
        self.assertEqual(sim.decision_write, {"rev_redactionreleased": True, "rev_redactionreviewrequired": False,
                                              "rev_redactionconfidence": 0.9})
        self.assertEqual(sim.notices, [])

    def test_absent_settings_hold_every_record(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT}, {}, self._ext())
        self.assertEqual(sim.reasons, ("threshold-missing-or-invalid", "auto-release-off"))
        self.assertFalse(sim.decision_write["rev_redactionreleased"])
        self.assertEqual(len(sim.notices), 1, "the card is posted; the HTML fallback is skipped")

    def test_kept_counterpart_is_not_rewritten_and_not_scanned(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT, "rev_narrativeredacted": "Her correction"}, ALL_SETTINGS, self._ext())
        self.assertEqual(sim.column_writes, {})
        self.assertNotIn("aibuilderpredict_entityextraction", [op for _, op in sim.calls])
        self.assertEqual(sim.reasons, ("kept-existing-counterpart:rev_narrativeraw",))

    def test_extractor_failure_on_one_column_only_holds_that_column(self):
        def ext(w):
            if w.startswith("Second"):
                raise RuntimeError("no AI Builder credits")
            return self.ENTS
        row = {"rev_narrativeraw": self.TEXT, "rev_otherconditionraw": "Second column text"}
        sim = run_flow(row, ALL_SETTINGS, ext)
        self.assertEqual(set(sim.column_writes), {"rev_narrativeredacted"})
        self.assertEqual(sim.reasons, ("ai-error:rev_otherconditionraw",))
        self.assertEqual(sim.status, "Succeeded", "a handled extractor failure is a reason, not a failed run")
        self.assertEqual((sim.reasons, sim.column_writes), (model(row, ALL_SETTINGS, ext)[0].reasons, model(row, ALL_SETTINGS, ext)[1]))

    def test_unreadable_extractor_answer_is_ai_error_not_no_entities(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT}, ALL_SETTINGS, lambda w: "UNREADABLE")
        self.assertEqual(sim.reasons, ("ai-error:rev_narrativeraw",))
        self.assertEqual(sim.column_writes, {})

    def test_unmapped_type(self):
        sim = run_flow({"rev_narrativeraw": self.TEXT}, ALL_SETTINGS,
                       self._ext(self.ENTS + [rr.ExtractorEntity("Mystery", "Call", 21, 4, 0.99)]))
        self.assertEqual(sim.reasons, ("unmapped-entity-type:rev_narrativeraw",))

    def test_threshold_boundary_and_forms(self):
        for th, released in [("90", True), ("0.90", True), ("90%", True), ("0.91", False), ("abc", False), ("150", False)]:
            with self.subTest(th):
                sim = run_flow({"rev_narrativeraw": self.TEXT}, {**ALL_SETTINGS, "RedactionConfidenceThreshold": th}, self._ext())
                self.assertEqual(sim.decision_write["rev_redactionreleased"], released)
                self.assertEqual(sim.reasons, model({"rev_narrativeraw": self.TEXT},
                                                    {**ALL_SETTINGS, "RedactionConfidenceThreshold": th}, self._ext())[0].reasons)

    def test_auto_release_values(self):
        for v, released in [("true", True), ("TRUE", True), (" true ", True), ("yes", False), ("", False)]:
            with self.subTest(v):
                sim = run_flow({"rev_narrativeraw": self.TEXT}, {**ALL_SETTINGS, "RedactionAutoRelease": v}, self._ext())
                self.assertEqual(sim.decision_write["rev_redactionreleased"], released)

    def test_prompt_stage_on_fails_closed(self):
        """Rev 20: on with no category row is prompt-config-invalid and the stage does not run; with a
        valid category it runs, and a failed call (no answer configured here) is prompt-error."""
        sim = run_flow({"rev_narrativeraw": self.TEXT}, {**ALL_SETTINGS, "RedactionPromptStage": "on"}, self._ext())
        self.assertEqual(sim.reasons, ("prompt-config-invalid", "uncalibrated-stage:prompt"))
        settings = {**ALL_SETTINGS, "RedactionPromptStage": "on", "RedactionPromptCategory.Name": "names",
                    "RedactionPromptCalibrated": "NAME"}
        sim = run_flow({"rev_narrativeraw": self.TEXT}, settings, self._ext())
        self.assertEqual(sim.reasons, ("prompt-error:rev_narrativeraw",))
        self.assertEqual(sim.column_writes, {"rev_narrativeredacted": "My carer [NAME] visits. Call [PHONE]."})

    def test_no_model_detections_rule_d2(self):
        sim = run_flow({"rev_narrativeraw": "We would love a week by the sea."}, ALL_SETTINGS, self._ext([]))
        self.assertEqual(sim.reasons, ("no-model-detections",))
        self.assertIsNone(sim.decision_write["rev_redactionconfidence"])

    def test_long_text_windows_and_over_length(self):
        filler = "word " * 999
        text = filler + "ring 07700 900123 please " + filler
        windows = []

        def ext(w):
            windows.append(len(w))
            return []
        sim = run_flow({"rev_narrativeraw": text}, ALL_SETTINGS, ext)
        self.assertEqual(windows, [len(w) for _, w in rr.windows(text)])
        self.assertEqual(sim.column_writes, {})
        self.assertEqual(sim.reasons, ("redacted-exceeds-4000:rev_narrativeraw", "no-model-detections"))

    def test_each_residue_check_fires_in_the_flow(self):
        cases = {
            "digit-run": "ref 123 456 789 here", "postcode": "we are at W1A1AA now", "at-sign": "write to a@b",
            "street-word": "off Mill Lane", "practice-word": "the Health Centre", "age-phrase": "she is 7 years old",
            "district": "the M62 was closed",
        }
        for kind, text in cases.items():
            with self.subTest(kind):
                sim = run_flow({"rev_narrativeraw": text}, ALL_SETTINGS, self._ext([]))
                self.assertIn(f"residual-{kind}:rev_narrativeraw", sim.reasons)
                self.assertEqual(sim.reasons, model({"rev_narrativeraw": text}, ALL_SETTINGS, self._ext([]))[0].reasons)

    def test_a_shape_followed_by_a_digit_or_letter_is_not_a_phone(self):
        for text in ["order 07700 900123456 shipped", "code 07700 900123A here", "id X07700 900123 ok"]:
            with self.subTest(text):
                sim = run_flow({"rev_narrativeraw": text}, ALL_SETTINGS, self._ext([]))
                self.assertNotIn("[PHONE]", sim.column_writes["rev_narrativeredacted"])
                self.assertIn("residual-digit-run:rev_narrativeraw", sim.reasons)

    def test_a_deep_failure_names_the_leaf_action(self):
        """result() returns immediate children only (IMP-0109), so the alert descends to the write.
        The failing column is the LAST one processed: result() of a container inside a loop is read
        here as its latest run, and a later successful column would hide the leaf (notes.md)."""
        sim = run_flow({"rev_carecostsexplanation": self.TEXT}, ALL_SETTINGS, self._ext(), fail_write=True)
        self.assertEqual(len(sim.alerts), 1)
        self.assertIn("Action: Write_rev_carecostsexplanationredacted | Code: ConnectorFailure", sim.alerts[0]["text_2"])
        self.assertEqual(sim.decision_write, {"rev_redactionreleased": False, "rev_redactionreviewrequired": True})

    def test_a_failure_hidden_by_a_later_column_still_holds_and_alerts(self):
        row = {"rev_narrativeraw": self.TEXT, "rev_carecostsexplanation": "Fine text"}
        sim = run_flow(row, ALL_SETTINGS, self._ext(), fail_write=True)
        self.assertEqual(len(sim.alerts), 1)
        self.assertEqual(sim.decision_write, {"rev_redactionreleased": False, "rev_redactionreviewrequired": True})

    def test_a_failure_holds_the_record_and_alerts_without_text(self):
        sim = run_flow({"rev_narrativeraw": CANARY}, ALL_SETTINGS, self._ext(), fail_get=True)
        self.assertEqual(sim.decision_write, {"rev_redactionreleased": False, "rev_redactionreviewrequired": True})
        self.assertEqual(len(sim.alerts), 1)
        self.assertIn("Get_the_application", sim.alerts[0]["text_2"])
        self.assertNotIn("refused", sim.alerts[0]["text_2"], "the platform's message is not copied")


# ════════════════════════════════════════════════════════════════════════════════════════════════
# Rev 20 (TAD 5.5.1): the shipped JSON against the model for the register, the settings and the prompt
# ════════════════════════════════════════════════════════════════════════════════════════════════
from test_flow_model import CATS, T0, T1, T2, answer, corpus_rev20  # noqa: E402


def assert_agrees(tc, row, settings, extract, ci=True, **kw):
    """The shipped flow (simulated) and the model give the same writes, reasons and decision."""
    sim = run_flow(row, settings, extract, case_insensitive=ci, **kw)
    kw.pop("definition", None)
    if "prompt" in kw:
        kw["prompt_call"] = kw.pop("prompt")
    dec, writes = model(row, settings, extract, **kw)
    tc.assertEqual(sim.status, "Succeeded")
    tc.assertEqual(sim.column_writes, writes)
    tc.assertEqual(sim.reasons, dec.reasons)
    tc.assertEqual(sim.decision_write, {"rev_redactionreleased": dec.released,
                                        "rev_redactionreviewrequired": dec.review_required,
                                        "rev_redactionconfidence": dec.confidence})
    return sim


class Rev20Register(unittest.TestCase):
    """ADR-073 in the shipped flow: the TAD 5.5.1 postcode table, the rev 20 corpus, and the register
    being unavailable."""

    def test_rev20_corpus_both_string_semantics(self):
        for ci in (True, False):
            for s, plain, _ in corpus_rev20():
                with self.subTest(s["id"], case_insensitive=ci):
                    sim = assert_agrees(self, {"rev_narrativeraw": plain}, ALL_SETTINGS, lambda w: [], ci)
                    self.assertEqual(sim.column_writes["rev_narrativeredacted"], s["expected"])
                    got = [r.split(":")[0].replace("residual-", "") for r in sim.reasons if r.startswith("residual-")]
                    self.assertEqual(got, s["expected_reasons"])

    def test_the_postcode_table_row_by_row(self):
        rows = [("at LS6 2AB now", "at [ADDRESS] now", ()), ("at EC1A 1BB now", "at [ADDRESS] now", ()),
                ("at LS62AB now", "at [ADDRESS] now", ()), ("at W1A1AA now", "at W1A1AA now", ("residual-postcode",)),
                ("we are in LS6 area", "we are in [ADDRESS] area", ()), ("post code LS6", "post code [ADDRESS]", ()),
                ("we live in LS6", "we live in LS6", ("residual-district",)), ("my N95 mask", "my N95 mask", ()),
                ("postcode LS6 2ABC", "postcode LS6 2ABC", ())]
        for text, red, residue in rows:
            with self.subTest(text):
                sim = assert_agrees(self, {"rev_narrativeraw": text}, ALL_SETTINGS, lambda w: [])
                self.assertEqual(sim.column_writes["rev_narrativeredacted"], red)
                self.assertEqual(tuple(r.split(":")[0] for r in sim.reasons if r.startswith("residual-")), residue)

    def test_a_failed_or_short_register_read_fails_closed_without_failing_the_run(self):
        for reg in (None, SEED_CODES[:2999], []):
            with self.subTest(rows=None if reg is None else len(reg)):
                sim = assert_agrees(self, {"rev_narrativeraw": "at LS62AB, in LS6 area"}, ALL_SETTINGS, lambda w: [], register=reg)
                self.assertEqual(sim.column_writes["rev_narrativeredacted"], "at LS62AB, in LS6 area")
                self.assertIn("postcode-register-unavailable", sim.reasons)
                self.assertEqual(sim.alerts, [], "a handled read failure is a reason, not a failed run")

    def test_the_20_sample_corpus_with_the_register_unavailable(self):
        for s, plain, gold in corpus():
            with self.subTest(s["id"]):
                assert_agrees(self, {"rev_narrativeraw": plain}, ALL_SETTINGS,
                              multi_extractor([(plain, simulated_entities(s, plain, gold))]), register=None)

    def test_the_register_is_read_once_per_run(self):
        row = {raw: "in LS6 area" for raw, _ in rr.SCRUB_COLUMNS}
        sim = run_flow(row, ALL_SETTINGS, lambda w: [])
        self.assertEqual([n for n, _ in sim.calls].count("List_postcode_districts"), 1)
        self.assertEqual(set(sim.column_writes.values()), {"in [ADDRESS] area"})


SETTINGS_TEXT = "My carer Ann visits off Mill Wynd. My goddaughter Ella and Oak Lane Clinic help at the hub."
SETTINGS_ENTS = [rr.ExtractorEntity("PersonName", "Ann", 9, 3, 0.9), rr.ExtractorEntity("PersonName", "Ella", 50, 4, 0.9),
                 rr.ExtractorEntity("Organization", "Oak Lane Clinic", 59, 15, 0.9)]


class Rev20Settings(unittest.TestCase):
    """ADR-074 in the shipped flow: every row of the TAD 5.5.1 settings table, against the model."""

    def _agree(self, settings, modified=None, ci=True):
        return assert_agrees(self, {"rev_narrativeraw": SETTINGS_TEXT}, settings, lambda w: SETTINGS_ENTS, ci, modified=modified)

    def test_the_text_is_what_the_entities_say(self):
        for e in SETTINGS_ENTS:
            self.assertEqual(SETTINGS_TEXT[e.startIndex:e.startIndex + e.length], e.value)

    def test_word_lists(self):
        cases = [
            ({}, None),
            ({"RedactionStreetWordsExtra": "wynd"}, None),
            ({"RedactionKinshipWordsExtra": "Goddaughter"}, None),
            ({"RedactionPracticeSuffixesExtra": "clinic\nhealth hub"}, None),
            ({"RedactionPracticeWordsExtra": "hub"}, None),
            ({"RedactionStreetWordsExtra": "wynd\n7th"}, "RedactionStreetWordsExtra"),
            ({"RedactionKinshipWordsExtra": "  \n "}, "RedactionKinshipWordsExtra"),
            ({"RedactionPracticeSuffixesExtra": "c"}, "RedactionPracticeSuffixesExtra"),
            ({"RedactionPracticeWordsExtra": "--"}, "RedactionPracticeWordsExtra"),
            ({"redactionstreetwordsextra": "wynd"}, None),
            ({"RedactionKinshipWordsExtra": "step-grandson\ngoddaughter", "RedactionStreetWordsExtra": "o'connell"}, None),
        ]
        for ci in (True, False):
            for extra, invalid in cases:
                with self.subTest(extra, case_insensitive=ci):
                    sim = self._agree({**ALL_SETTINGS, **extra}, ci=ci)
                    bad = [r for r in sim.reasons if r.startswith("redaction-setting-invalid:")]
                    self.assertEqual(bad, [f"redaction-setting-invalid:{invalid}"] if invalid else [])

    def test_each_valid_addition_changes_the_output_as_designed(self):
        s = {**ALL_SETTINGS, "RedactionStreetWordsExtra": "wynd", "RedactionKinshipWordsExtra": "goddaughter",
             "RedactionPracticeSuffixesExtra": "clinic", "RedactionPracticeWordsExtra": "hub"}
        sim = self._agree(s)
        self.assertEqual(sim.column_writes["rev_narrativeredacted"],
                         "My carer [NAME] visits off Mill Wynd. My goddaughter [FAMILY MEMBER] and [GP PRACTICE] help at the hub.")
        self.assertEqual(sim.reasons, ("residual-street-word:rev_narrativeraw", "residual-practice-word:rev_narrativeraw"))
        floor = self._agree(ALL_SETTINGS)
        self.assertEqual(floor.column_writes["rev_narrativeredacted"],
                         "My carer [NAME] visits off Mill Wynd. My goddaughter [NAME] and Oak Lane Clinic help at the hub.")

    def test_auto_release_guard(self):
        s = {**ALL_SETTINGS, "RedactionStreetWordsExtra": "lane"}
        for modified, want in [({"RedactionAutoRelease": T1, "RedactionStreetWordsExtra": T0}, ()),
                               ({"RedactionAutoRelease": T1}, ()),
                               ({"RedactionAutoRelease": T0, "RedactionStreetWordsExtra": T1}, ("auto-release-stale",)),
                               ({"RedactionAutoRelease": T0, "RedactionConfidenceThreshold": T2}, ("auto-release-stale",))]:
            with self.subTest(modified):
                sim = assert_agrees(self, {"rev_narrativeraw": "My carer Ann visits."}, s,
                                    lambda w: [rr.ExtractorEntity("PersonName", "Ann", 9, 3, 0.9)], modified=modified)
                self.assertEqual(sim.reasons, want)

    def test_a_newer_row_outside_redaction_does_not_stale_auto_release(self):
        """OTHER_SETTING (PostcodeRegionMap) is saved after everything; the in-flow filter keeps it out."""
        sim = assert_agrees(self, {"rev_narrativeraw": "My carer Ann visits."}, ALL_SETTINGS,
                            lambda w: [rr.ExtractorEntity("PersonName", "Ann", 9, 3, 0.9)])
        self.assertTrue(sim.decision_write["rev_redactionreleased"])

    def test_prompt_configuration_and_calibration(self):
        on = {**ALL_SETTINGS, "RedactionPromptStage": "on"}
        cases = [
            (on, None),
            ({**on, **CATS}, None),
            ({**on, **CATS, "RedactionPromptCategory.Pet": "dogs"}, None),
            ({**on, **CATS, "RedactionPromptCategory.GpPractice": "  "}, None),
            ({**on, **CATS, "RedactionPromptCalibrated": "true"}, None),
            ({**on, **CATS, "RedactionPromptCalibrated": "name , ADDRESS, name"}, None),
            ({**on, **CATS, "RedactionPromptCalibrated": "NAME"}, None),
            ({**on, **CATS, "RedactionPromptCalibrated": "NAME, ADDRESS, GP PRACTICE"}, None),
            ({**on, **CATS, "RedactionPromptCalibrated": "NAME, ADDRESS"}, {"RedactionPromptCalibrated": T0, "RedactionPromptCategory.Name": T1}),
            ({**on, **CATS, "RedactionPromptCalibrated": "NAME, ADDRESS"}, {"RedactionPromptCalibrated": T1, "RedactionAutoRelease": T2}),
            ({**ALL_SETTINGS, **CATS, "RedactionPromptCalibrated": "junk"}, None),
        ]
        for ci in (True, False):
            for settings, modified in cases:
                with self.subTest(settings=sorted(settings), modified=modified, case_insensitive=ci):
                    self._agree(settings, modified, ci)


def _use_branch(definition):
    return (definition["actions"]["Scrub_free_text"]["actions"]["For_each_column"]["actions"]
            ["Scrub_the_column_if_it_has_text"]["actions"]["Keep_or_scrub_the_column"]["else"]["actions"]
            ["Scan_the_column_in_windows"]["actions"]["Use_the_prompt_on_the_window"]["actions"])


PROMPT_SETTINGS = {**ALL_SETTINGS, **CATS, "RedactionPromptStage": "on", "RedactionPromptCalibrated": "NAME, ADDRESS"}
PROMPT_TEXT = "Our neighbour Bob Jones and his dog visit; Ann told us at her annual review."


def _raise(_):
    raise RuntimeError("no prompt credits")


GOOD = {"label": "NAME", "quote": "Bob Jones"}
PROMPT_ANSWERS = {
    "valid": lambda r: answer([GOOD, {"label": "NAME", "quote": "Ann"}]),
    "valid, empty array": lambda r: answer([]),
    "valid, overlaps the extractor": lambda r: answer([{"label": "NAME", "quote": "Jones"}]),
    "call fails": _raise,
    "no body": lambda r: None,
    "stopped for length": lambda r: answer([GOOD], reason="length"),
    "finishReason Stop": lambda r: answer([GOOD], reason="Stop"),
    "blank text": lambda r: answer(text="   "),
    "prose": lambda r: answer(text="Bob Jones is a name."),
    "label not configured": lambda r: answer([GOOD, {"label": "GP PRACTICE", "quote": "Ann"}]),
    "label unknown": lambda r: answer([GOOD, {"label": "PASSWORD", "quote": "Ann"}]),
    "quote absent": lambda r: answer([GOOD, {"label": "NAME", "quote": "Zoe"}]),
    "quote only inside a word": lambda r: answer([GOOD, {"label": "NAME", "quote": "nnua"}]),
    "quote too short": lambda r: answer([GOOD, {"label": "NAME", "quote": "B"}]),
    "quote too long": lambda r: answer([GOOD, {"label": "NAME", "quote": "x" * 201}]),
    "quote a number": lambda r: answer([GOOD, {"label": "NAME", "quote": 42}]),
    "quote an array": lambda r: answer([GOOD, {"label": "NAME", "quote": ["Bob", "Ann"]}]),
    "item not an object": lambda r: answer([GOOD, "Ann"]),
    "item has no quote": lambda r: answer([GOOD, {"label": "NAME"}]),
    "label a number": lambda r: answer([GOOD, {"label": 7, "quote": "Ann"}]),
    "an object, not an array": lambda r: answer({"label": "NAME", "quote": "Ann"}),
    "a string": lambda r: answer("Ann"),
    "null": lambda r: answer(None),
}


class PromptStageInTheShippedFlow(unittest.TestCase):
    """ADR-072 items 5-8 and ADR-074 item 2: the shipped validation and fail-closed paths, executed."""

    def test_a_failing_call_is_prompt_error_per_column(self):
        row = {"rev_narrativeraw": PROMPT_TEXT, "rev_carecostsexplanation": "Ann pays."}
        sim = assert_agrees(self, row, PROMPT_SETTINGS, lambda w: [])
        self.assertEqual([r for r in sim.reasons if r.startswith("prompt")],
                         ["prompt-error:rev_narrativeraw", "prompt-error:rev_carecostsexplanation"])
        self.assertEqual(len(sim.column_writes), 2, "the counterparts are still written, without prompt spans")

    def test_the_answer_comes_from_the_shipped_run_action(self):
        use = _use_branch(DEFINITION)
        self.assertEqual(use["Compose_prompt_answer"]["runAfter"], {"Run_the_redaction_prompt": ["Succeeded"]})
        self.assertEqual(use["Run_the_redaction_prompt"]["inputs"]["host"]["operationId"], "aibuilderpredict_customprompt")

    def test_an_answer_at_another_body_path_fails_closed(self):
        """A-NS-25 in the safe direction: if the platform puts the answer anywhere else, the flow reads
        null and the column is prompt-error. It can never use a misplaced answer, valid or not."""
        for wrap in (lambda a: a, lambda a: {"responsev2": a}, lambda a: {"predictionOutput": a}):
            sim = run_flow({"rev_narrativeraw": PROMPT_TEXT}, PROMPT_SETTINGS, lambda w: [],
                           prompt=PROMPT_ANSWERS["valid"], prompt_wrap=wrap)
            self.assertEqual(sim.column_writes["rev_narrativeredacted"], PROMPT_TEXT)
            self.assertIn("prompt-error:rev_narrativeraw", sim.reasons)

    def test_the_call_passes_the_window_and_this_runs_categories_by_input_name(self):
        """A-NS-20: the three inputs, by the names the export declares, and the window is the Narrative."""
        seen = []
        text = "Bob Jones visits. " + "word " * 1000 + "Ann helps."
        run_flow({"rev_narrativeraw": text}, PROMPT_SETTINGS, lambda w: [],
                 prompt=lambda r: seen.append(dict(r)) or answer([]))
        self.assertEqual(len(seen), 2, "one call per 5,000-character window")
        self.assertEqual({k for r in seen for k in r}, PROMPT_INPUTS)
        self.assertTrue(seen[0]["Narrative"].startswith("Bob Jones") and seen[1]["Narrative"].endswith("Ann helps."))
        self.assertTrue(all(len(r["Narrative"]) <= 5000 for r in seen))

    def test_every_answer_shape_agrees_with_the_model(self):
        spliced = DEFINITION
        for ci in (True, False):
            for name, prompt in PROMPT_ANSWERS.items():
                with self.subTest(name, case_insensitive=ci):
                    assert_agrees(self, {"rev_narrativeraw": PROMPT_TEXT}, PROMPT_SETTINGS,
                                  lambda w: [rr.ExtractorEntity("PersonName", "Bob Jones", 14, 9, 0.9)], ci,
                                  definition=spliced, prompt=prompt)

    def test_what_each_answer_does(self):
        spliced = DEFINITION
        expect = {"valid": ("Our neighbour [NAME] and his dog visit; [NAME] told us at her annual review.", None),
                  "call fails": (PROMPT_TEXT, "prompt-error"), "prose": (PROMPT_TEXT, "prompt-error"),
                  "stopped for length": (PROMPT_TEXT, "prompt-error"),
                  "quote only inside a word": (PROMPT_TEXT, "prompt-output-invalid"),
                  "a string": (PROMPT_TEXT, "prompt-output-invalid"),
                  "valid, empty array": (PROMPT_TEXT, None)}
        for name, (red, reason) in expect.items():
            with self.subTest(name):
                sim = run_flow({"rev_narrativeraw": PROMPT_TEXT}, PROMPT_SETTINGS, lambda w: [], definition=spliced,
                               prompt=PROMPT_ANSWERS[name])
                self.assertEqual(sim.column_writes["rev_narrativeredacted"], red)
                got = [r.split(":")[0] for r in sim.reasons if r.startswith("prompt")]
                self.assertEqual(got, [reason] if reason else [])

    def test_the_request_carries_this_runs_categories(self):
        spliced, seen = DEFINITION, []
        run_flow({"rev_narrativeraw": PROMPT_TEXT}, PROMPT_SETTINGS, lambda w: [], definition=spliced,
                 prompt=lambda r: seen.append(dict(r)) or answer([]))
        self.assertEqual(seen, [{"Categories": "ADDRESS: A street or building with no number\nNAME: People's names, including nicknames",
                                 "AllowedLabels": "ADDRESS, NAME", "Narrative": PROMPT_TEXT}])

    def test_one_bad_window_discards_the_column_and_windows_agree(self):
        text = "Bob Jones visits. " + "word " * 1000 + "Ann helps."
        def prompt(r):
            return answer([GOOD] if "Bob" in r["Narrative"] else [{"label": "NAME", "quote": "Zoe"}])
        spliced = DEFINITION
        sim = assert_agrees(self, {"rev_narrativeraw": text}, PROMPT_SETTINGS, lambda w: [], definition=spliced, prompt=prompt)
        self.assertIn("prompt-output-invalid:rev_narrativeraw", sim.reasons)

    def test_the_stage_does_not_run_when_off_or_misconfigured(self):
        spliced, seen = DEFINITION, []
        for settings in (ALL_SETTINGS, {**ALL_SETTINGS, "RedactionPromptStage": "on"},
                         {**PROMPT_SETTINGS, "RedactionPromptCategory.Pet": "dogs"}):
            run_flow({"rev_narrativeraw": PROMPT_TEXT}, settings, lambda w: [], definition=spliced,
                     prompt=lambda r: seen.append(r) or answer([]))
        self.assertEqual(seen, [])

    def test_a_prompt_answer_never_reaches_run_history_unsecured(self):
        text = f"My friend {CANARY} visits; {CANARY.lower()} helps."
        spliced = DEFINITION
        sim = run_flow({"rev_narrativeraw": text}, PROMPT_SETTINGS, lambda w: [], definition=spliced,
                       prompt=lambda r: answer([{"label": "NAME", "quote": CANARY}, {"label": "NAME", "quote": "Zz"}]))
        self.assertIn("prompt-output-invalid:rev_narrativeraw", sim.reasons)
        self.assertEqual(leaks(sim), [])
        for var, val in sim.engine.assignments:
            self.assertNotIn(CANARY.lower(), json.dumps(val).lower(), var)


def leaks(sim):
    exempt = {"If", "Until", "Scope", "Switch", "Terminate"}
    out = []
    for r in sim.engine.records:
        if r.type in exempt:
            continue
        blob_in = json.dumps(r.inputs, ensure_ascii=False).lower()
        blob_out = json.dumps(r.outputs, ensure_ascii=False).lower()
        secure_in = "inputs" in r.secure
        secure_out = "outputs" in r.secure or (r.type == "Compose" and secure_in)
        if r.type in ("SetVariable", "AppendToArrayVariable", "InitializeVariable"):
            secure_in = secure_out = False  # variable actions cannot be secured at all
        if CANARY.lower() in blob_in and not secure_in:
            out.append(f"{r.name} inputs")
        if CANARY.lower() in blob_out and not secure_out:
            out.append(f"{r.name} outputs")
    return sorted(set(out))


class RunHistoryAndVariables(unittest.TestCase):
    """C-DOM-004, NFR-012, ADR-071 item 5, TAD 5.5 'What is never in run history'."""

    TEXT = (f"My husband {CANARY} Pmrtk lives at 14 {CANARY} Road, Leeds LS6 2AB; ring 07700 900123 or "
            f"{CANARY.lower()}@example.org. Dr {CANARY}'s Surgery knows. I am 72 years old and {CANARY} said so.")

    def _run(self):
        t = self.TEXT
        ents = [rr.ExtractorEntity("PersonName", f"{CANARY} Pmrtk", t.index(CANARY), len(CANARY) + 6, 0.9),
                rr.ExtractorEntity("StreetAddress", f"14 {CANARY} Road, Leeds", t.index("14 "), len(f"14 {CANARY} Road, Leeds"), 0.8),
                rr.ExtractorEntity("Email", f"{CANARY.lower()}@example.org", t.index(CANARY.lower()), len(CANARY) + 12, 0.99),
                rr.ExtractorEntity("Organization", f"Dr {CANARY}'s Surgery", t.index("Dr "), len(f"Dr {CANARY}'s Surgery"), 0.7),
                rr.ExtractorEntity("Age", "72 years old", t.index("72"), 12, 0.95)]
        return run_flow({"rev_narrativeraw": t}, {}, lambda w: ents)

    def test_the_canary_run_redacts_everything_but_the_unowned_name(self):
        sim = self._run()
        red = sim.column_writes["rev_narrativeredacted"]
        self.assertEqual(red, "My husband [FAMILY MEMBER] lives at [ADDRESS]; ring [PHONE] or [EMAIL]. [GP PRACTICE] knows. "
                              f"I am [AGE 65 to 74] and {CANARY} said so.")

    def test_every_action_that_sees_text_hides_it(self):
        sim = self._run()
        exempt = {"If", "Until", "Scope", "Switch", "Terminate"}
        leaks = []
        for r in sim.engine.records:
            if r.type in exempt:
                continue
            blob_in = json.dumps(r.inputs, ensure_ascii=False).lower()
            blob_out = json.dumps(r.outputs, ensure_ascii=False).lower()
            secure_in = "inputs" in r.secure
            secure_out = "outputs" in r.secure or (r.type == "Compose" and secure_in)
            if r.type in ("SetVariable", "AppendToArrayVariable", "InitializeVariable"):
                secure_in = secure_out = False  # variable actions cannot be secured at all
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
        self.assertIn("auto-release-off", sim.notices[0])

    def test_the_trigger_and_the_row_read_are_secured(self):
        trig = next(iter(DEFINITION["triggers"].values()))
        self.assertIn("outputs", trig["runtimeConfiguration"]["secureData"]["properties"])
        get = DEFINITION["actions"]["Scrub_free_text"]["actions"]["Get_the_application"]
        self.assertIn("outputs", get["runtimeConfiguration"]["secureData"]["properties"])


class PlatformLimits(unittest.TestCase):
    """Limits the packer does not enforce (C-TECH-049), checked over EVERY flow in the solution.
    Power Automate's documented limits (E2, 'Limits of automated, scheduled, and instant flows'):
    an expression is at most 8,192 characters, actions nest at most 8 deep, a flow holds at most
    500 actions. A breach packs and imports, and fails only when the flow is saved or run.

    A-NS-26 (OPEN, E2): REVNarrativeScrubFreeText nests containers 8 deep with leaf actions inside the
    8th. This test counts CONTAINERS, so it passes at 8. Whether the platform counts those leaves as a
    ninth level is documentation only and has never been confirmed. If it does, the flow imports but
    cannot be saved in the designer. Closed by the DEV import and a designer open-and-save."""

    CONTAINERS = ("If", "Foreach", "Until", "Scope", "Switch")

    def _children(self, a):
        out = dict(a.get("actions") or {})
        out.update((a.get("else") or {}).get("actions") or {})
        for c in (a.get("cases") or {}).values():
            out.update(c.get("actions") or {})
        out.update((a.get("default") or {}).get("actions") or {})
        return out

    def _walk(self, actions, depth, stats):
        for _, a in actions.items():
            stats["count"] += 1
            if a.get("type") in self.CONTAINERS:
                stats["depth"] = max(stats["depth"], depth + 1)
                self._walk(self._children(a), depth + 1, stats)

    def _strings(self, node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, dict):
            for v in node.values():
                yield from self._strings(v)
        elif isinstance(node, list):
            for v in node:
                yield from self._strings(v)

    def test_every_flow_is_within_the_documented_limits(self):
        flows = sorted(FLOW.parent.glob("*.json"))
        manifest = (FLOW.parents[1] / "Other" / "Solution.xml").read_text(encoding="utf-8")
        self.assertEqual(len(flows), manifest.count('<RootComponent type="29"'),
                         "every cloud flow the solution declares is checked (C-TECH-067: both sides from source)")
        for f in flows:
            with self.subTest(f.name):
                d = json.loads(f.read_text(encoding="utf-8"))["properties"]["definition"]
                stats = {"count": 0, "depth": 0}
                self._walk(d["actions"], 0, stats)
                self.assertLessEqual(stats["count"], 500)
                self.assertLessEqual(stats["depth"], 8)
                longest = max((len(s) for s in self._strings(d) if s.startswith("@")), default=0)
                self.assertLessEqual(longest, 8192)


class DefinitionConstants(unittest.TestCase):
    def _compose(self, name):
        found = []

        def walk(actions):
            for n, a in actions.items():
                if n == name:
                    found.append(a["inputs"])
                for key in ("actions",):
                    if isinstance(a.get(key), dict):
                        walk(a[key])
                if isinstance(a.get("else"), dict):
                    walk(a["else"].get("actions", {}))
                for c in (a.get("cases") or {}).values():
                    walk(c.get("actions", {}))
        walk(DEFINITION["actions"])
        self.assertEqual(len(found), 1, name)
        return found[0]

    def test_constants_are_the_reference_lists(self):
        self.assertEqual([(c["raw"], c["red"]) for c in self._compose("Compose_scrub_columns")], rr.SCRUB_COLUMNS)
        self.assertEqual(self._compose("Compose_shape_table"), rr.SHAPE_TABLE)
        self.assertEqual(self._compose("Compose_label_text"), rr.LABEL_BY_CODE)
        self.assertEqual(self._compose("Compose_extractor_type_codes"), rr.EXTRACTOR_TYPE_CODE)
        self.assertEqual(self._compose("Compose_kin_words"), rr.KIN_WORDS)
        self.assertEqual(self._compose("Compose_kin_tails"), rr.KIN_TAILS)
        # rev 20: the floors the settings add to, the register shapes and the prompt maps
        self.assertEqual(self._compose("Compose_practice_suffixes"), rr.GP_SUFFIXES)
        self.assertEqual(self._compose("Compose_street_words"), rr.STREET_WORDS)
        self.assertEqual(self._compose("Compose_practice_words"), rr.PRACTICE_WORDS)
        self.assertEqual(self._compose("Compose_register_shape_table"), rr.REGISTER_SHAPE_TABLE)
        self.assertEqual(self._compose("Compose_prompt_category_labels"), rr.PROMPT_CATEGORY_LABELS)
        self.assertEqual(self._compose("Compose_prompt_label_codes"), rr.PROMPT_LABEL_ALLOW)

    def test_every_setting_in_the_tad_table_is_read(self):
        """TAD 5.5.1's settings table: each row the flow reads by name has its own Find_setting_ action
        (the category rows are read by prefix), and the read itself has no $filter."""
        names = set()

        def walk(actions):
            for n, a in actions.items():
                names.add(n)
                for sub in (a.get("actions"), (a.get("else") or {}).get("actions")):
                    if isinstance(sub, dict):
                        walk(sub)
        walk(DEFINITION["actions"])
        for key in ["RedactionConfidenceThreshold", "RedactionAutoRelease", "RedactionPromptStage",
                    "RedactionPromptCalibrated", *rr.WORD_LIST_KEYS]:
            self.assertIn(f"Find_setting_{key}", names)
        read = DEFINITION["actions"]["Scrub_free_text"]["actions"]["Read_redaction_settings"]["inputs"]["parameters"]
        self.assertEqual(read, {"entityName": "rev_settings", "$select": "rev_name,rev_value,modifiedon"})

    def test_every_counterpart_has_exactly_one_write(self):
        sw = (DEFINITION["actions"]["Scrub_free_text"]["actions"]["For_each_column"]["actions"]
              ["Scrub_the_column_if_it_has_text"]["actions"]["Keep_or_scrub_the_column"]["else"]["actions"]
              ["Finish_the_column"]["else"]["actions"]["Write_or_hold_the_column"]["actions"]["Write_the_counterpart"])
        cases = {c["case"]: c["actions"] for c in sw["cases"].values()}
        self.assertEqual(set(cases), {red for _, red in rr.SCRUB_COLUMNS})
        for red, actions in cases.items():
            (a,) = actions.values()
            self.assertEqual([k for k in a["inputs"]["parameters"] if k.startswith("item/")], [f"item/{red}"])

    def test_the_prompt_component_is_referenced_once_by_its_id(self):
        """ADR-072, Iteration 4: the run action is built; the stage still ships OFF (no setting row)."""
        blob = json.dumps(DEFINITION)
        self.assertEqual(blob.count(PROMPT_MODEL_ID), 1)
        self.assertEqual(blob.count("aibuilderpredict_customprompt"), 1)


# --- Trigger loops (C-TECH-055 triage of Solution Checker `flow-avoid-recursive-loop`, IMP-1090) ---------
#
# The live Solution Checker flags every Dataverse write to the trigger's own table, whatever the trigger's
# filteringattributes say: it still flags REVSafeguardingActionCompletion after that trigger was filtered
# (IMP-0858, IMP-0948). Whether a flow can actually re-trigger itself, or another flow, is decided by the
# definitions: a Dataverse row-changed trigger with filteringattributes fires only when an update names one
# of those columns, and UpdateRecord sends only the `item/<column>` parameters it is given.

DATAVERSE = "shared_commondataserviceforapps"
# Every Dataverse operation the solution's flows use, classified. An unclassified one fails the test, so a
# new write operation cannot slip past the loop check by being unknown to it.
READ_OPS = {"GetItem", "ListRecords", "SubscribeWebhookTrigger",
            "aibuilderpredict_entityextraction", "aibuilderpredict_customprompt"}
WRITE_OPS = {"UpdateRecord": "update", "UpdateOnlyRecord": "update", "CreateRecord": "create"}
# subscriptionRequest/message: 1 create, 2 delete, 3 update, 4 create or update, 5 create or delete,
# 6 update or delete, 7 all three.
FIRES_ON = {"create": {1, 4, 5, 7}, "update": {3, 4, 6, 7}}

# The 14 actions the 2026-10-07 Solution Checker report (build 20261007-2) names on this flow, as triaged in
# the narrative Dev Summary §4.11. If the flow gains or loses a write to rev_applications, this set and that
# row are both out of date.
CHECKER_FLAGGED = {f"Write_{red}" for _, red in rr.SCRUB_COLUMNS} | {"Write_the_decision", "Hold_the_record_for_review"}


def _dataverse_actions(actions):
    """Every Dataverse connector action at any depth: (name, operationId, parameters)."""
    for name, a in actions.items():
        if not isinstance(a, dict):
            continue
        inputs = a.get("inputs")
        host = inputs.get("host") if isinstance(inputs, dict) else None
        if isinstance(host, dict) and host.get("connectionName") == DATAVERSE:
            yield name, host["operationId"], inputs.get("parameters", {})
        for child in (a.get("actions"), (a.get("else") or {}).get("actions"), (a.get("default") or {}).get("actions")):
            if isinstance(child, dict):
                yield from _dataverse_actions(child)
        for case in (a.get("cases") or {}).values():
            yield from _dataverse_actions(case.get("actions") or {})


def _table_of(entity_set):
    """Entity set name -> logical name, as the flows spell them (rev_applications -> rev_application)."""
    return entity_set[:-1] if entity_set.endswith("s") else entity_set


def trigger_of(definition):
    """(table, messages, filter columns or None for 'any column') for a Dataverse row trigger, else None."""
    for t in definition["triggers"].values():
        p = (t.get("inputs") or {}).get("parameters") or {}
        if "subscriptionRequest/entityname" not in p:
            return None
        if t.get("conditions"):
            raise AssertionError("trigger conditions present: extend the loop check to read them")
        cols = p.get("subscriptionRequest/filteringattributes")
        cols = {c.strip() for c in cols.split(",") if c.strip()} if cols else None
        return p["subscriptionRequest/entityname"], {p["subscriptionRequest/message"]}, cols
    return None


def writes_of(definition):
    """[(action, kind, table, columns or None for 'every column')] for every Dataverse write."""
    out = []
    for name, op, params in _dataverse_actions(definition["actions"]):
        if op in READ_OPS:
            continue
        if op not in WRITE_OPS:
            raise AssertionError(f"{name}: Dataverse operation {op} is not classified as a read or a write")
        cols = {k[len("item/"):] for k in params if k.startswith("item/")}
        whole_body = "item" in params
        out.append((name, WRITE_OPS[op], _table_of(params["entityName"]), None if whole_body else cols))
    return out


def loop_edges(flows):
    """flows: {flow name: definition}. Edge (a, b, action) where action in flow a can fire flow b's trigger."""
    edges = []
    for b, db in flows.items():
        trig = trigger_of(db)
        if trig is None:
            continue
        table, messages, filt = trig
        for a, da in flows.items():
            for action, kind, wtable, cols in writes_of(da):
                if wtable != table or not (messages & FIRES_ON[kind]):
                    continue
                if kind == "update" and filt is not None and cols is not None and not (cols & filt):
                    continue
                edges.append((a, b, action))
    return edges


def cycles(edges):
    """Flows that lie on a cycle (a self-loop included)."""
    graph = {}
    for a, b, _ in edges:
        graph.setdefault(a, set()).add(b)

    def reaches(start, goal, seen):
        for n in graph.get(start, ()):
            if n == goal:
                return True
            if n not in seen:
                seen.add(n)
                if reaches(n, goal, seen):
                    return True
        return False
    return {f for f in graph if reaches(f, f, set())}


def all_flows():
    return {f.name.split("-")[0]: json.loads(f.read_text(encoding="utf-8"))["properties"]["definition"]
            for f in sorted(FLOW.parent.glob("*.json"))}


def _find(definition, action_name):
    for name, _, params in _dataverse_actions(definition["actions"]):
        if name == action_name:
            return params
    raise KeyError(action_name)


class NoTriggerLoop(unittest.TestCase):
    """The Solution Checker's 14 `flow-avoid-recursive-loop` results on this flow are false positives,
    proven here from the definition; each mutation below turns one into a real loop and must fail."""

    def test_the_trigger_is_filtered_to_rev_status_with_no_conditions(self):
        self.assertEqual(trigger_of(DEFINITION), ("rev_application", {3}, {"rev_status"}))

    def test_written_columns_are_disjoint_from_the_trigger_filter(self):
        table, _, filt = trigger_of(DEFINITION)
        own = [(n, cols) for n, _, t, cols in writes_of(DEFINITION) if t == table]
        self.assertTrue(own)
        for name, cols in own:
            with self.subTest(name):
                self.assertIsNotNone(cols, "a whole-row write can name any column")
                self.assertFalse(cols & filt, f"{name} writes {sorted(cols & filt)}, which the trigger listens on")

    def test_the_writes_are_exactly_the_ones_the_checker_flagged(self):
        """The triage row names 14 actions. A new write to rev_applications must be re-triaged."""
        self.assertEqual({n for n, _, t, _ in writes_of(DEFINITION) if t == "rev_application"}, CHECKER_FLAGGED)
        self.assertEqual(len(CHECKER_FLAGGED), 14)

    def test_no_flow_in_the_solution_is_on_a_trigger_loop(self):
        """Self-loops and loops through another flow (this flow and REVSafeguardingActionCompletion both
        trigger on rev_application updates)."""
        flows = all_flows()
        self.assertIn("REVNarrativeScrubFreeText", flows)
        self.assertEqual(cycles(loop_edges(flows)), set())

    # --- mutations: each one makes a real loop, and the checks above must see it ---

    def _mutated(self, change):
        flows = all_flows()
        d = copy.deepcopy(flows["REVNarrativeScrubFreeText"])
        change(d)
        flows["REVNarrativeScrubFreeText"] = d
        return d, flows

    def test_mutation_a_write_that_names_rev_status_is_a_loop(self):
        d, flows = self._mutated(lambda d: _find(d, "Write_the_decision").__setitem__("item/rev_status", 6))
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))
        _, _, filt = trigger_of(d)
        self.assertTrue(any(cols & filt for n, _, _, cols in writes_of(d) if n == "Write_the_decision"))

    def test_mutation_an_unfiltered_trigger_is_a_loop(self):
        def drop(d):
            (t,) = d["triggers"].values()
            del t["inputs"]["parameters"]["subscriptionRequest/filteringattributes"]
        _, flows = self._mutated(drop)
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))

    def test_mutation_a_whole_row_write_is_a_loop(self):
        _, flows = self._mutated(lambda d: _find(d, "Hold_the_record_for_review").__setitem__("item", {}))
        self.assertIn("REVNarrativeScrubFreeText", cycles(loop_edges(flows)))

    def test_mutation_a_cross_flow_loop_is_found(self):
        """This flow writes the column the safeguarding flow listens on, and that flow writes rev_status."""
        flows = all_flows()
        d = copy.deepcopy(flows["REVNarrativeScrubFreeText"])
        _find(d, "Write_the_decision")["item/rev_safeguardingactioncompleted"] = True
        sg = copy.deepcopy(flows["REVSafeguardingActionCompletion"])
        (params,) = [p for _, op, p in _dataverse_actions(sg["actions"]) if op == "UpdateRecord"]
        params["item/rev_status"] = 6
        flows.update({"REVNarrativeScrubFreeText": d, "REVSafeguardingActionCompletion": sg})
        self.assertEqual(cycles(loop_edges(flows)), {"REVNarrativeScrubFreeText", "REVSafeguardingActionCompletion"})

    def test_mutation_an_unclassified_dataverse_operation_fails(self):
        d, _ = self._mutated(lambda d: None)
        hold = d["actions"]["Hold_the_record_for_review"]
        hold["inputs"]["host"]["operationId"] = "PerformBoundAction"
        with self.assertRaises(AssertionError):
            writes_of(d)

    def test_mutation_a_trigger_condition_is_not_silently_ignored(self):
        d, _ = self._mutated(lambda d: next(iter(d["triggers"].values())).__setitem__(
            "conditions", [{"expression": "@true"}]))
        with self.assertRaises(AssertionError):
            trigger_of(d)


if __name__ == "__main__":
    unittest.main()
