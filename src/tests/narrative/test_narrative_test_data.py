#!/usr/bin/env python3
"""Tests for src/tests/data/narrative-test-data.json, the three seeded narrative cases (WBS 5.3 / 5.4).

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

What they prove: the data file is loadable by seed-test-data.ps1 (same preflight rules), the plain text
in each application is the gold markup with the markup removed, every gold span is a span the rules can
produce, the expected redacted text and the expected record decision are what the flow model produces with
a perfect extractor, and the text is synthetic (Ofcom drama phone numbers, reserved email domains).
They do not measure the AI Builder model: score_seeded_run.py does that, against a live run.

REV 22 (Iteration 9, 2026-10-16): the file's expectedRedacted and expectedRecord are the rev 20 deterministic flow's
output and are marked stale in the file itself (`_rev22`); they are regenerated after the two prompts exist (TAD 12.6.1
R1). The tests that compared them with the retired flow model are replaced by RevTwentyTwo below.
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
from corpus_support import simulated_entities  # noqa: E402
from test_redaction_reference import parse_markup  # noqa: E402

REPO = HERE.parents[2]
DATA = json.loads((REPO / "src" / "tests" / "data" / "narrative-test-data.json").read_text(encoding="utf-8"))
CASES = DATA["cases"]
SCORING_IDS = {c["caseId"] for c in json.loads(
    (REPO / "src" / "tests" / "data" / "scoring-test-data.json").read_text(encoding="utf-8"))["cases"]}
SETTINGS = {"withoutRedactionSettings": {},
            "withThreshold": {"RedactionConfidenceThreshold": "0.85"}}   # ADR-078: RedactionAutoRelease retired
OFCOM_PHONE = re.compile(r"^(07700 900\d{3}|\(?0113\)? 496 0\d{3}|020 7946 0\d{3})$")
EMAIL = re.compile(r"[\w.+-]+@([\w.-]+)")


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


class RevTwentyTwo(unittest.TestCase):
    def test_the_file_says_its_expectations_are_stale(self):
        self.assertIn("STALE SINCE 2026-10-16", DATA["_rev22"])

    def test_the_labelled_text_holds_no_value_the_extractor_finds(self):
        """What the rewrite prompt would receive for each seeded column, with a perfect extractor: no gold value
        the extractor owns is left in it (phones and postcodes are the prompt's to label, ADR-075 item 3)."""
        for c in CASES:
            for col, marked in c["narratives"].items():
                plain, gold = parse_markup(marked)
                if rr.column_state(plain, None) != "scrub":
                    continue
                ents = [rr.ExtractorEntity(*e) for e in simulated_entities({}, plain, gold)]
                _, kept, _, _ = rr.label_spans(plain, ents)
                labelled = rr.labelled_text(plain, kept)
                for e in ents:
                    self.assertNotIn(e.value, labelled, f"{c['caseId']} {col}")

    def test_td14_is_over_5000_characters_and_is_no_longer_scrubbed(self):
        plain, _ = parse_markup(CASES[1]["narratives"]["rev_narrativeraw"])
        self.assertGreater(len(plain), rr.EXTRACTOR_MAX_CHARS)
        self.assertEqual(rr.column_state(plain, None), "too-long")


class Scorer(unittest.TestCase):
    def live_from_expected(self, case, released, review):
        live = {r: v for r, v in case["expectedRedacted"].items() if v}
        live.update({"rev_redactionreleased": released, "rev_redactionreviewrequired": review})
        return live

    def test_perfect_live_rows_pass(self):
        for c in CASES:
            exp = c["expectedRecord"]["withThreshold"]
            live = self.live_from_expected(c, exp["released"], exp["rev_redactionreviewrequired"])
            if c["caseId"] == "TD-14":
                live.pop("rev_narrativeredacted", None)
            self.assertEqual(scorer.score_case(c, live, "on")[0], "PASS", c["caseId"])

    def test_a_missed_name_fails_and_a_missing_row_is_not_a_pass(self):
        c = CASES[0]
        exp = c["expectedRecord"]["withThreshold"]
        live = self.live_from_expected(c, False, True)
        live["rev_narrativeredacted"] = live["rev_narrativeredacted"].replace("[NAME]", "Beatrix", 1)
        self.assertEqual(scorer.score_case(c, live, "on")[0], "FAIL")
        self.assertEqual(scorer.score_case(c, None, "on")[0], "MISSING")

    def test_every_expected_record_waits_for_the_process_owner(self):
        """TAD rev 25, ADR-078: the flow never releases; review required on every scrubbed record; no auto-release hint."""
        for c in CASES:
            self.assertEqual(set(c["expectedRecord"]), {"withoutRedactionSettings", "withThreshold"}, c["caseId"])
            for state, exp in c["expectedRecord"].items():
                with self.subTest(c["caseId"], state=state):
                    self.assertIs(exp["released"], False)
                    self.assertIs(exp["rev_redactionreviewrequired"], True)
                    self.assertFalse([r for r in exp["reasons"] if r.startswith("auto-release")])

    def test_a_record_the_flow_released_fails(self):
        c = CASES[0]
        live = self.live_from_expected(c, True, False)
        self.assertEqual(scorer.score_case(c, live, "on")[0], "FAIL")

    def test_writing_the_too_long_counterpart_fails_td14(self):
        c = CASES[1]
        live = self.live_from_expected(c, False, True)
        live["rev_narrativeredacted"] = "x" * 100
        self.assertEqual(scorer.score_case(c, live, "on")[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
