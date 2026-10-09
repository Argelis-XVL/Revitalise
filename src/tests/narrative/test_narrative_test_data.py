#!/usr/bin/env python3
"""Tests for src/tests/data/narrative-test-data.json, the three seeded narrative cases (WBS 5.3 / 5.4).

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

What they prove: the data file is loadable by seed-test-data.ps1 (same preflight rules), the plain text
in each application is the gold markup with the markup removed, every gold span is a span the rules can
produce, the expected redacted text and the expected record decision are what the flow model produces with
a perfect extractor, and the text is synthetic (Ofcom drama phone numbers, reserved email domains).
They do not measure the AI Builder model: score_seeded_run.py does that, against a live run.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402
import score_seeded_run as scorer  # noqa: E402
from test_flow_model import extractor_for, simulated_entities  # noqa: E402
from test_redaction_reference import parse_markup  # noqa: E402

REPO = HERE.parents[2]
DATA = json.loads((REPO / "src" / "tests" / "data" / "narrative-test-data.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
SCORING_IDS = {c["caseId"] for c in json.loads(
    (REPO / "src" / "tests" / "data" / "scoring-test-data.json").read_text(encoding="utf-8"))["cases"]}
SETTINGS = {"withoutRedactionSettings": {},
            "withThresholdAndAutoRelease": {"RedactionConfidenceThreshold": "0.85", "RedactionAutoRelease": "true"}}
OFCOM_PHONE = re.compile(r"^(07700 900\d{3}|\(?0113\)? 496 0\d{3}|020 7946 0\d{3})$")
EMAIL = re.compile(r"[\w.+-]+@([\w.-]+)")


def run(case, settings, ents_score=0.93):
    def extract(window):
        for marked in case["narratives"].values():
            plain, gold = parse_markup(marked)
            if window in plain:
                return extractor_for(plain, simulated_entities({}, plain, gold, ents_score))(window)
        return []
    row = {k: v for k, v in case["application"].items() if isinstance(v, str)}
    return rr.flow_scrub_record(row, settings, extract)


class FileShape(unittest.TestCase):
    def test_three_cases_with_new_ids_and_the_teardown_markers(self):
        self.assertEqual([c["caseId"] for c in CASES], ["TD-13", "TD-14", "TD-15"])
        self.assertFalse({c["caseId"] for c in CASES} & SCORING_IDS)
        for c in CASES:
            sid = c["application"]["rev_sourcesubmissionid"]
            self.assertEqual(sid, "TESTDATA-" + c["caseId"])
            self.assertEqual(c["applicant"]["rev_lastcontactdate"], "1900-01-01")
            self.assertTrue(c["applicant"]["rev_firstname"] and c["applicant"]["rev_lastname"])

    def test_seed_script_can_load_it_without_touching_the_scoring_file(self):
        # The loader sends every non-underscore key of `application`; none may be a column that does not exist.
        import xml.etree.ElementTree as ET
        ent = REPO / "src" / "solutions" / "RevitaliseGrantAutomation" / "Entities"
        for table, key in (("rev_application", "application"), ("rev_applicant", "applicant")):
            names = {a.findtext("LogicalName") for a in ET.parse(ent / table / "Entity.xml").getroot().iter("attribute")}
            for c in CASES:
                for col in c[key]:
                    self.assertIn(col, names, f"{c['caseId']}: {key}.{col} is not a column of {table}")

    def test_every_free_text_column_sent_is_one_of_the_twelve(self):
        raw = {r for r, _ in rr.SCRUB_COLUMNS}
        red = {r for _, r in rr.SCRUB_COLUMNS}
        for c in CASES:
            for col in c["narratives"]:
                self.assertIn(col, raw)
            for col in c["expectedRedacted"]:
                self.assertIn(col, red)
            self.assertEqual(set(c["expectedRedacted"]), red, "every counterpart has an expectation")

    def test_plain_text_in_the_application_is_the_gold_markup_without_markup(self):
        for c in CASES:
            for col, marked in c["narratives"].items():
                self.assertEqual(c["application"][col], parse_markup(marked)[0], f"{c['caseId']} {col}")
            for raw, _ in rr.SCRUB_COLUMNS:
                if raw not in c["narratives"]:
                    self.assertNotIn(raw, c["application"], "a column with no gold must not carry text")


class Synthetic(unittest.TestCase):
    def test_every_phone_is_an_ofcom_drama_number_and_every_email_a_reserved_domain(self):
        for c in CASES:
            for marked in c["narratives"].values():
                plain, gold = parse_markup(marked)
                for s, n, cat in gold:
                    if cat == "PHONE":
                        self.assertRegex(plain[s:s + n], OFCOM_PHONE)
                    if cat == "EMAIL":
                        self.assertIn(EMAIL.match(plain[s:s + n]).group(1), ("example.org", "example.com"))
            for col in ("rev_phone",):
                self.assertRegex(c["applicant"][col], OFCOM_PHONE)
            self.assertTrue(c["applicant"]["rev_email"].endswith("@example.invalid"))

    def test_no_text_is_taken_from_the_corpus_or_the_import_folder(self):
        corpus = (HERE / "corpus" / "narratives.json").read_text(encoding="utf-8")
        for c in CASES:
            for marked in c["narratives"].values():
                for s, n, cat in parse_markup(marked)[1]:
                    value = parse_markup(marked)[0][s:s + n]
                    self.assertNotIn(value, corpus, f"{c['caseId']}: '{value}' is a corpus value")

    def test_every_gold_category_is_one_the_rules_know(self):
        known = set(rr.LABEL) | {"AGE"}
        for c in CASES:
            for marked in c["narratives"].values():
                for _, _, cat in parse_markup(marked)[1]:
                    self.assertIn(cat, known)

    def test_the_three_cases_between_them_exercise_every_label(self):
        cats = {cat for c in CASES for m in c["narratives"].values() for _, _, cat in parse_markup(m)[1]}
        self.assertEqual(cats, set(rr.LABEL) | {"AGE"})


class FlowModelAgrees(unittest.TestCase):
    def test_expected_redacted_text_is_what_the_flow_model_writes(self):
        for c in CASES:
            _, writes = run(c, SETTINGS["withThresholdAndAutoRelease"])
            for red, want in c["expectedRedacted"].items():
                if want is None:
                    self.assertNotIn(red, writes, f"{c['caseId']} {red} must not be written")
                elif want == c["application"].get(red):          # present already or a clean pass-through
                    self.assertTrue(red not in writes or writes[red] == want)
                elif want:
                    self.assertEqual(writes.get(red), want, f"{c['caseId']} {red}")
                else:
                    self.assertNotIn(red, writes)

    def test_expected_record_is_what_the_flow_model_decides(self):
        for c in CASES:
            for name, settings in SETTINGS.items():
                dec, _ = run(c, settings)
                exp = c["expectedRecord"][name]
                self.assertEqual(dec.released, exp["released"], f"{c['caseId']} {name}")
                self.assertEqual(dec.review_required, exp["rev_redactionreviewrequired"])
                self.assertEqual(list(dec.reasons), exp["reasons"], f"{c['caseId']} {name}")

    def test_td13_below_threshold_when_the_model_is_less_sure(self):
        dec, _ = run(CASES[0], SETTINGS["withThresholdAndAutoRelease"], ents_score=0.80)
        self.assertFalse(dec.released)
        self.assertIn("below-threshold", dec.reasons)

    def test_td13_to_td15_have_the_roles_the_reviewer_asked_for(self):
        typical, edge, review = CASES
        self.assertTrue(run(typical, SETTINGS["withThresholdAndAutoRelease"])[0].released)
        self.assertEqual(run(edge, SETTINGS["withThresholdAndAutoRelease"])[0].reasons, ("redacted-exceeds-4000:rev_narrativeraw",))
        reasons = run(review, SETTINGS["withThresholdAndAutoRelease"])[0].reasons
        self.assertEqual({r.split(":")[0] for r in reasons},
                         {"residual-street-word", "residual-practice-word", "kept-existing-counterpart"})

    def test_td14_needs_three_windows_and_the_overlap_holds_the_phone_and_email(self):
        c = CASES[1]
        plain, gold = parse_markup(c["narratives"]["rev_narrativeraw"])
        w = rr.windows(plain)
        self.assertEqual([(o, len(t)) for o, t in w], [(0, 4998), (4798, 4998), (9596, 860)])
        for s, n, cat in gold:
            self.assertTrue(any(s >= o and s + n <= o + len(t) for o, t in w), f"{cat} at {s} is whole in no window")
        for cat in ("PHONE", "EMAIL"):
            s, n, _ = next(g for g in gold if g[2] == cat)
            self.assertGreaterEqual(sum(1 for o, t in w if s >= o and s + n <= o + len(t)), 2)
        # redacted text really is too long to write, and the raw column has no street or practice word
        self.assertGreater(len(rr.flow_scrub_column("c", plain, None, lambda _w: []).redacted), 4000)


class Scorer(unittest.TestCase):
    def live_from_expected(self, case, released, review):
        live = {r: v for r, v in case["expectedRedacted"].items() if v}
        live.update({"rev_redactionreleased": released, "rev_redactionreviewrequired": review})
        return live

    def test_perfect_live_rows_pass(self):
        for c in CASES:
            exp = c["expectedRecord"]["withThresholdAndAutoRelease"]
            live = self.live_from_expected(c, exp["released"], exp["rev_redactionreviewrequired"])
            if c["caseId"] == "TD-14":
                live.pop("rev_narrativeredacted", None)
            self.assertEqual(scorer.score_case(c, live, "on")[0], "PASS", c["caseId"])

    def test_a_missed_name_fails_and_a_missing_row_is_not_a_pass(self):
        c = CASES[0]
        exp = c["expectedRecord"]["withThresholdAndAutoRelease"]
        live = self.live_from_expected(c, True, False)
        live["rev_narrativeredacted"] = live["rev_narrativeredacted"].replace("[NAME]", "Beatrix", 1)
        self.assertEqual(scorer.score_case(c, live, "on")[0], "FAIL")
        self.assertEqual(scorer.score_case(c, None, "on")[0], "MISSING")

    def test_writing_the_too_long_counterpart_fails_td14(self):
        c = CASES[1]
        live = self.live_from_expected(c, False, True)
        live["rev_narrativeredacted"] = "x" * 100
        self.assertEqual(scorer.score_case(c, live, "on")[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
