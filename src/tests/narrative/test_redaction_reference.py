#!/usr/bin/env python3
"""Tests for the free-text redaction rules v0.1 (WBS 5.1 / 5.2).

Run:  python3 -m unittest discover -s src/tests/narrative -p 'test_*.py' -v
Also run by src/tests/narrative/NarrativeRedaction.Tests.ps1 inside the HARD `unit-tests` build step.

Every test here is about LOGIC: offsets, overlaps, ordering, windows, fail-closed decisions. None of
them measures the AI Builder model - that is score_live_run.py's job, against a live run.
"""
from __future__ import annotations

import json
import random
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402

CORPUS = json.loads((HERE / "corpus" / "narratives.json").read_text(encoding="utf-8"))
SAMPLES = CORPUS["samples"]
MARKUP = re.compile(r"\[\[([A-Z ]+):(.+?)\]\]")
SIMULATED_TYPE = {"NAME": "PersonName", "FAMILY MEMBER": "PersonName", "GP PRACTICE": "Organization",
                  "AGE": "Age"}


def parse_markup(marked: str):
    """-> (plain text, [(start, length, category)]) with code-point offsets."""
    plain, gold, pos = [], [], 0
    cursor = 0
    for m in MARKUP.finditer(marked):
        plain.append(marked[pos:m.start()])
        cursor += m.start() - pos
        gold.append((cursor, len(m.group(2)), m.group(1)))
        plain.append(m.group(2))
        cursor += len(m.group(2))
        pos = m.end()
    plain.append(marked[pos:])
    return "".join(plain), gold


def nth(text: str, value: str, occurrence: int = 1) -> int:
    idx = -1
    for _ in range(occurrence):
        idx = text.find(value, idx + 1)
        if idx < 0:
            raise AssertionError(f"value {value!r} occurrence {occurrence} not in text")
    return idx


def simulate_ai(sample, plain, gold):
    score = sample.get("ai_score", 0.93)
    ents = [rr.PrebuiltEntity(SIMULATED_TYPE[c], s, n, score) for s, n, c in gold if c in SIMULATED_TYPE]
    for x in sample.get("ai_extra", []):
        start = nth(plain, x["value"], x.get("occurrence", 1))
        ents.append(rr.PrebuiltEntity(x["type"], start, len(x["value"]), x.get("score", 0.9)))
    return ents


def gold_detections(gold):
    return [rr.Detection(s, n, "AGE" if c == "AGE" else c, 1.0, "rule") for s, n, c in gold]


class CorpusShape(unittest.TestCase):
    def test_at_least_15_samples_with_unique_ids(self):
        ids = [s["id"] for s in SAMPLES]
        self.assertGreaterEqual(len(ids), 15)
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_direct_category_is_exercised(self):
        cats = {c for s in SAMPLES for _, _, c in parse_markup(s["text"])[1]}
        for required in ["NAME", "FAMILY MEMBER", "GP PRACTICE", "ADDRESS", "PHONE", "EMAIL", "AGE"]:
            self.assertIn(required, cats)

    def test_hand_written_expected_agrees_with_gold_spans(self):
        """Guards the corpus itself: a typing slip in `expected` must fail here, not hide."""
        for s in SAMPLES:
            with self.subTest(s["id"]):
                plain, gold = parse_markup(s["text"])
                self.assertEqual(rr.apply(plain, gold_detections(gold)), s["expected"])


class PipelineAgainstCorpus(unittest.TestCase):
    """With a perfect simulated model, the rules must produce exactly the expected text."""

    def test_redacted_text_matches_expected(self):
        for s in SAMPLES:
            with self.subTest(s["id"]):
                plain, gold = parse_markup(s["text"])
                res = rr.redact_column(plain, simulate_ai(s, plain, gold))
                self.assertEqual(res.redacted, s["expected"])

    def test_final_spans_equal_gold_spans_exactly(self):
        """Stronger than text equality: no extra span, no missing span, right category."""
        for s in SAMPLES:
            with self.subTest(s["id"]):
                plain, gold = parse_markup(s["text"])
                res = rr.redact_column(plain, simulate_ai(s, plain, gold))
                self.assertEqual(sorted((d.start, d.length, d.category) for d in res.detections), sorted(gold))

    def test_no_raw_value_survives_in_redacted_output(self):
        for s in SAMPLES:
            with self.subTest(s["id"]):
                plain, gold = parse_markup(s["text"])
                red = rr.redact_column(plain, simulate_ai(s, plain, gold)).redacted
                for st, n, c in gold:
                    value = plain[st:st + n]
                    # Values that are also ordinary words appear elsewhere on purpose (S04, S05, S15).
                    if s["id"] in ("S04", "S05", "S15") and c in ("NAME", "FAMILY MEMBER"):
                        continue
                    self.assertNotIn(value, red)


class ReplacementLogic(unittest.TestCase):
    def test_from_end_equals_independent_forward_rebuild_on_random_spans(self):
        rnd = random.Random(20261005)
        cats = ["NAME", "PHONE", "ADDRESS", "EMAIL", "FAMILY MEMBER", "GP PRACTICE"]
        for _ in range(500):
            text = "".join(rnd.choice("abcde fgh,ij") for _ in range(rnd.randint(1, 120)))
            spans, pos = [], 0
            while pos < len(text):
                pos += rnd.randint(0, 10)
                n = rnd.randint(1, 8)
                if pos + n > len(text):
                    break
                spans.append(rr.Detection(pos, n, rnd.choice(cats), 1.0, "rule"))
                pos += n + rnd.randint(1, 3)  # disjoint, never touching
            rnd.shuffle(spans)
            expected, cursor = [], 0
            for d in sorted(spans, key=lambda d: d.start):
                expected += [text[cursor:d.start], rr.LABEL[d.category]]
                cursor = d.end
            expected.append(text[cursor:])
            self.assertEqual(rr.apply(text, spans), "".join(expected))

    def test_naive_forward_replacement_would_corrupt_and_ours_does_not(self):
        text = "Ann rang Bob."
        spans = [rr.Detection(0, 3, "NAME", 1, "rule"), rr.Detection(9, 3, "NAME", 1, "rule")]
        naive = text
        for d in sorted(spans, key=lambda d: d.start):  # forward, offsets NOT adjusted
            naive = naive[:d.start] + rr.LABEL[d.category] + naive[d.end:]
        self.assertNotEqual(naive, "[NAME] rang [NAME].")
        self.assertEqual(rr.apply(text, spans), "[NAME] rang [NAME].")

    def test_search_and_replace_would_over_redact_common_word_and_offsets_do_not(self):
        s = next(x for x in SAMPLES if x["id"] == "S04")
        plain, gold = parse_markup(s["text"])
        self.assertEqual(plain.lower().count("will"), 2)
        self.assertIn(" will drive", rr.apply(plain, gold_detections(gold)))

    def test_nested_partial_and_duplicate_overlaps_merge_to_one_span(self):
        text = "Contact Sarah Jane Price today"
        dets = [rr.Detection(8, 10, "NAME", 0.81, "aibuilder"),   # Sarah Jane
                rr.Detection(19, 5, "NAME", 0.90, "aibuilder"),   # Price
                rr.Detection(8, 16, "NAME", 0.95, "aibuilder"),   # Sarah Jane Price
                rr.Detection(8, 16, "NAME", 0.95, "aibuilder"),   # duplicate
                rr.Detection(14, 10, "NAME", 0.85, "aibuilder")]  # Jane Price (partial)
        merged = rr.merge(text, dets)
        self.assertEqual([(d.start, d.length) for d in merged], [(8, 16)])
        self.assertEqual(rr.apply(text, merged), "Contact [NAME] today")

    def test_merge_never_raises_confidence(self):
        dets = [rr.Detection(0, 5, "NAME", 0.40, "aibuilder"), rr.Detection(2, 5, "NAME", 0.99, "aibuilder")]
        self.assertEqual(rr.merge("abcdefgh", dets)[0].score, 0.40)

    def test_overlap_takes_highest_precedence_category(self):
        text = "Dr Patel's Surgery"
        dets = [rr.Detection(3, 5, "NAME", 0.9, "aibuilder"), rr.Detection(0, 18, "GP PRACTICE", 1.0, "rule")]
        merged = rr.merge(text, dets)
        self.assertEqual([(d.start, d.length, d.category) for d in merged], [(0, 18, "GP PRACTICE")])

    def test_touching_non_address_spans_stay_separate(self):
        text = "Ann, Bob"
        dets = [rr.Detection(0, 3, "NAME", 1, "rule"), rr.Detection(5, 3, "NAME", 1, "rule")]
        self.assertEqual(rr.apply(text, rr.merge(text, dets)), "[NAME], [NAME]")

    def test_adjacent_address_parts_coalesce(self):
        text = "at 3 Mill Lane, LS6 2AB today"
        res = rr.redact_column(text, [])
        self.assertEqual(res.redacted, "at [ADDRESS] today")


class Windows(unittest.TestCase):
    def test_windows_respect_limit_and_cover_text(self):
        text = ("word " * 3000).strip()
        ws = rr.windows(text)
        self.assertTrue(all(len(w) <= rr.PREBUILT_MAX_CHARS for _, w in ws))
        covered = set()
        for off, w in ws:
            self.assertEqual(text[off:off + len(w)], w)
            covered.update(range(off, off + len(w)))
        self.assertEqual(covered, set(range(len(text))))

    def test_entity_straddling_a_window_boundary_is_still_redacted(self):
        filler = "x" * 4990
        text = filler + " Margaret Ellison rang. " + "y " * 2000
        name_at = text.index("Margaret Ellison")

        def fake_model(chunk):  # finds the name only when it is wholly inside the window
            i = chunk.find("Margaret Ellison")
            return [rr.PrebuiltEntity("PersonName", i, 16, 0.9)] if i >= 0 else []

        first_end = rr.windows(text)[0][1].__len__()
        self.assertLess(first_end, name_at + 16, "fixture must straddle the first boundary")
        ents = rr.prebuilt_over_windows(text, fake_model)
        self.assertIn(name_at, [e.start for e in ents])
        self.assertIn(" [NAME] rang.", rr.redact_column(text, ents).redacted)

    def test_short_text_is_one_window(self):
        self.assertEqual(rr.windows("short"), [(0, "short")])


class Utf16Offsets(unittest.TestCase):
    def test_non_bmp_character_shifts_utf16_offsets_and_conversion_restores_them(self):
        s = next(x for x in SAMPLES if x["id"] == "S16")
        plain, gold = parse_markup(s["text"])
        cp_start = gold[0][0]
        utf16_start = len(plain[:cp_start].encode("utf-16-le")) // 2
        self.assertEqual(utf16_start, cp_start + 1)  # the emoji is two UTF-16 code units
        self.assertEqual(rr.utf16_to_codepoints(plain, utf16_start), cp_start)


class Rules(unittest.TestCase):
    def cats(self, text):
        return [(text[d.start:d.end], d.category) for d in rr.rule_detections(text)]

    def test_phone_negatives(self):
        for t in ["Budget £1,200 in 2019", "Room 0161", "ref 12345678", "since 01/02/2020"]:
            with self.subTest(t):
                self.assertNotIn("PHONE", [c for _, c in self.cats(t)])

    def test_duration_is_not_an_age(self):
        self.assertEqual(self.cats("I have cared for her for five years"), [])
        self.assertEqual(self.cats("We waited 3 years for a ramp"), [])

    def test_age_bands_match_option_set_labels(self):
        self.assertEqual(rr.age_band(17), "Under 18")
        self.assertEqual(rr.age_band(18), "18 to 24")
        self.assertEqual(rr.age_band(74), "65 to 74")
        self.assertEqual(rr.age_band(75), "75 and over")
        self.assertEqual(rr.age_band(None), "Not known")
        self.assertEqual(rr.age_from_text("ninety-one"), 91)
        self.assertEqual(rr.age_from_text("twelve"), 12)

    def test_every_pattern_claim_in_the_rules_document_section_6(self):
        cases = {
            "She is a 12-year-old girl": "She is a [AGE Under 18] girl",
            "we live at Flat 3, 14 Elm Road, Leeds LS6 2AB now": "we live at [ADDRESS] now",
            "post to GIR 0AA": "post to [ADDRESS]",
            "we park off Mill Lane daily": "we park off [ADDRESS] daily",
            "aged 45 and tired": "[AGE 45 to 54] and tired",
            "0113 496 0000 or a ref 12345678": "[PHONE] or a ref 12345678",
        }
        for text, expected in cases.items():
            with self.subTest(text):
                self.assertEqual(rr.redact_column(text, []).redacted, expected)
        t = "I visit my late mother-in-law Joan weekly"
        res = rr.redact_column(t, [rr.PrebuiltEntity("PersonName", t.index("Joan"), 4, 0.9)])
        self.assertEqual(res.redacted, "I visit my late mother-in-law [FAMILY MEMBER] weekly")

    def test_destination_park_without_number_is_not_an_address(self):
        self.assertEqual(self.cats("We would love a day in Hyde Park"), [])

    def test_non_gp_organisation_is_retained(self):
        res = rr.redact_column("Leeds Carers Centre helped", [rr.PrebuiltEntity("Organization", 0, 19, 0.9)])
        self.assertEqual(res.redacted, "Leeds Carers Centre helped")

    def test_extension_point_exists_and_is_empty_in_v0_1(self):
        self.assertEqual(rr.INDIRECT_RULES, [])

    def test_extension_point_is_wired(self):
        def fake_indirect(text, _dets):
            i = text.find("three sisters")
            return [rr.Detection(i, 13, "NAME", 1.0, "rule")] if i >= 0 else []
        rr.INDIRECT_RULES.append(fake_indirect)
        try:
            self.assertEqual(rr.redact_column("I have three sisters", []).redacted, "I have [NAME]")
        finally:
            rr.INDIRECT_RULES.clear()


class Decision(unittest.TestCase):
    def col(self, text, ents=None, error=False):
        return (text, rr.redact_column(text, ents or [], error=error))

    def named(self, score):
        text = "My name is Margaret Ellison."
        return self.col(text, [rr.PrebuiltEntity("PersonName", 11, 16, score)])

    def test_threshold_is_read_from_setting_in_either_form(self):
        self.assertEqual(rr.parse_threshold("0.85"), 0.85)
        self.assertEqual(rr.parse_threshold("85"), 0.85)
        self.assertEqual(rr.parse_threshold("85%"), 0.85)
        for bad in [None, "", "abc", "0", "-1", "150"]:
            self.assertIsNone(rr.parse_threshold(bad))

    def test_missing_threshold_fails_closed(self):
        d = rr.decide({"narrative": self.named(0.99)}, None)
        self.assertTrue(d.review_required)
        self.assertFalse(d.released)

    def test_threshold_boundary_both_directions(self):
        at = rr.decide({"narrative": self.named(0.85)}, "0.85")
        below = rr.decide({"narrative": self.named(0.8499)}, "0.85")
        self.assertEqual((at.review_required, at.released), (False, True))
        self.assertEqual((below.review_required, below.released), (True, False))
        self.assertIn("below-threshold", below.reasons)

    def test_threshold_change_needs_no_code_change(self):
        self.assertTrue(rr.decide({"narrative": self.named(0.90)}, "0.95").review_required)
        self.assertFalse(rr.decide({"narrative": self.named(0.90)}, "0.80").review_required)

    def test_lowest_score_across_all_columns_decides(self):
        d = rr.decide({"a": self.named(0.99), "b": self.named(0.70)}, "0.85")
        self.assertEqual(d.confidence, 0.70)
        self.assertTrue(d.review_required)

    def test_ai_error_on_any_column_fails_closed(self):
        d = rr.decide({"a": self.named(0.99), "b": self.col("Some text", error=True)}, "0.85")
        self.assertEqual((d.review_required, d.released), (True, False))
        self.assertIn("ai-error:b", d.reasons)

    def test_missing_result_for_non_empty_column_fails_closed(self):
        d = rr.decide({"a": ("Some text", None)}, "0.85")
        self.assertTrue(d.review_required)

    def test_empty_columns_are_out_of_scope(self):
        d = rr.decide({"a": self.named(0.99), "b": (None, None), "c": ("   ", None)}, "0.85")
        self.assertFalse(d.review_required)

    def test_no_model_detections_goes_to_review_by_default_and_releases_only_by_policy(self):
        cols = {"a": self.col("We would love a week by the sea.")}
        self.assertIn("no-model-detections", rr.decide(cols, "0.85").reasons)
        self.assertFalse(rr.decide(cols, "0.85", empty_detection_policy="release").review_required)

    def test_rule_only_detections_do_not_count_as_model_confidence(self):
        cols = {"a": self.col("Call 07700 900123 please.")}
        d = rr.decide(cols, "0.85")
        self.assertIsNone(d.confidence)
        self.assertIn("no-model-detections", d.reasons)

    def test_unmapped_entity_type_fails_closed(self):
        cols = {"a": self.col("Margaret rang", [rr.PrebuiltEntity("Person", 0, 8, 0.99)])}
        d = rr.decide(cols, "0.85")
        self.assertIn("unmapped-entity-type:a", d.reasons)
        self.assertFalse(d.released)

    def test_redacted_text_over_counterpart_max_length_fails_closed(self):
        text = "word " * 900 + "Margaret Ellison"
        cols = {"a": self.col(text, [rr.PrebuiltEntity("PersonName", len(text) - 16, 16, 0.99)])}
        d = rr.decide(cols, "0.85")
        self.assertIn(f"redacted-exceeds-{rr.REDACTED_MAX_CHARS}:a", d.reasons)

    def test_decision_never_carries_input_text(self):
        for s in SAMPLES:
            plain, gold = parse_markup(s["text"])
            res = rr.redact_column(plain, simulate_ai(s, plain, gold))
            for policy_text in [repr(rr.decide({"narrative": (plain, res)}, "0.85")),
                                repr(rr.decide({"narrative": (plain, None)}, None))]:
                for word in re.findall(r"[A-Za-z]{4,}", plain):
                    # The Decision's own vocabulary (field names, reason codes, column key).
                    if word.lower() in {"decision", "review", "required", "released", "confidence",
                                        "reasons", "true", "false", "none", "narrative", "threshold",
                                        "missing", "invalid", "error", "below", "model",
                                        "detections", "unmapped", "entity", "type", "exceeds"}:
                        continue
                    self.assertNotIn(word, policy_text, f"{s['id']}: {word!r} leaked into a decision")


class RerunNeverOverwritesAHuman(unittest.TestCase):
    """Reviewer scope addition 2026-10-05: an admin's correction on the Narrative Scrubbing tab
    must survive a later re-run of the scrub (status change, re-trigger)."""

    def test_admin_correction_survives_a_rerun(self):
        existing = {"narrative": "My carer [NAME] visits daily.", "othercondition": None}
        new = {"narrative": "My carer [NAME] visits daily and Hope [NAME].", "othercondition": "Asthma."}
        plan = rr.plan_writes(False, existing, new)
        self.assertNotIn("narrative", plan.writes)          # the correction is not touched
        self.assertEqual(plan.writes, {"othercondition": "Asthma."})
        self.assertEqual(plan.kept, ("narrative",))

    def test_a_kept_column_stops_the_flow_releasing_the_record(self):
        text = "My name is Margaret Ellison."
        col = (text, rr.redact_column(text, [rr.PrebuiltEntity("PersonName", 11, 16, 0.99)]))
        plan = rr.plan_writes(False, {"narrative": "edited by admin"}, {"narrative": col[1].redacted})
        d = rr.decide_with_plan({"narrative": col}, "0.85", plan)
        self.assertEqual((d.review_required, d.released), (True, False))
        self.assertIn("kept-existing-counterpart:narrative", d.reasons)

    def test_released_record_is_never_touched(self):
        plan = rr.plan_writes(True, {"narrative": "approved text", "othercondition": None},
                              {"narrative": "[NAME] new", "othercondition": "new"})
        self.assertTrue(plan.skip_record)
        self.assertEqual(plan.writes, {})
        self.assertIsNone(rr.decide_with_plan({}, "0.85", plan))

    def test_clearing_a_counterpart_is_how_an_admin_asks_for_a_rescrub(self):
        for cleared in (None, "", "   \n"):
            with self.subTest(repr(cleared)):
                plan = rr.plan_writes(False, {"narrative": cleared}, {"narrative": "[NAME] rang."})
                self.assertEqual(plan.writes, {"narrative": "[NAME] rang."})
                self.assertEqual(plan.reasons, ())

    def test_first_run_writes_everything_and_can_release(self):
        text = "My name is Margaret Ellison."
        col = (text, rr.redact_column(text, [rr.PrebuiltEntity("PersonName", 11, 16, 0.99)]))
        plan = rr.plan_writes(False, {"narrative": None}, {"narrative": col[1].redacted})
        d = rr.decide_with_plan({"narrative": col}, "0.85", plan)
        self.assertEqual(plan.writes, {"narrative": "My name is [NAME]."})
        self.assertEqual((d.review_required, d.released), (False, True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
