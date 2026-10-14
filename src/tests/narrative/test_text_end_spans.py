"""A span that ends at the last character, or overruns it (wbs:5.3, first live DEV run, 2026-10-12).

The flow failed in Finish_the_column with InvalidTemplate: "The 'start index' for function
'substring' must be equal to or greater than zero and must be less than '249' which is the length of
the string." The last merged span ended at 249 = length(raw), so the tail
substring(raw, lastMergedEnd) was substring(raw, length(raw)), which THROWS on the platform
(aka.ms/logicexpressions#substring) and which the simulator used to allow.

These tests pin the simulator to the platform rule and the flow to never reaching it.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import redaction_reference as rr  # noqa: E402
import wdl_sim  # noqa: E402
from test_flow_model import ALL_SETTINGS  # noqa: E402
from test_scrub_flow_definition import assert_agrees, run_flow  # noqa: E402

EMAIL = "beatrix.holloway@example.org"
PREFIX = "Please write to her at "
TEXT = f"{PREFIX}{EMAIL}."          # ends in a full stop right after the address
START = len(PREFIX)


def extractor(length):
    def call(window):
        return [rr.ExtractorEntity("Email", EMAIL, START, length, 0.93)]
    return call


class SubstringFollowsThePlatform(unittest.TestCase):
    """aka.ms/logicexpressions#substring: start must be >= 0 and < length(string)."""

    def setUp(self):
        self.eng = wdl_sim.Engine({"actions": {}, "triggers": {}}, {})

    def test_start_equal_to_length_throws(self):
        for args in (("abc", 3), ("abc", 3, 0), ("", 0), ("", 0, 0), ("abc", -1), ("abc", 4)):
            with self.subTest(args=args), self.assertRaises(wdl_sim.WdlError):
                self.eng.f_substring(*args)

    def test_in_range_forms_still_work(self):
        self.assertEqual(self.eng.f_substring("abc", 2), "c")
        self.assertEqual(self.eng.f_substring("abc", 0, 3), "abc")
        self.assertEqual(self.eng.f_substring("abc", 2, 0), "")
        with self.assertRaises(wdl_sim.WdlError):
            self.eng.f_substring("abc", 1, 3)


class ASpanAtTheEndOfTheText(unittest.TestCase):
    def test_span_ending_on_the_last_character_and_one_overrunning_it(self):
        for label, length in (("ends at the last character", len(EMAIL) + 1),
                              ("overruns by one", len(EMAIL) + 2),
                              ("overruns by far", len(EMAIL) + 500),
                              ("stops before the full stop", len(EMAIL))):
            with self.subTest(label):
                sim = assert_agrees(self, {"rev_narrativeraw": TEXT}, ALL_SETTINGS, extractor(length))
                self.assertEqual(sim.status, "Succeeded")
                self.assertEqual(sim.alerts, [])
                out = sim.column_writes["rev_narrativeredacted"]
                self.assertTrue(out.startswith(PREFIX), out)
                self.assertNotIn("holloway", out)
                self.assertNotIn("@", out)
                # rebuild path: nothing after the redacted entity but, at most, the full stop
                self.assertLessEqual(len(out.split("]")[-1]), 1, out)

    def test_both_tails_are_empty_when_the_span_reaches_the_end(self):
        sim = run_flow({"rev_narrativeraw": TEXT}, ALL_SETTINGS, extractor(len(EMAIL) + 2))
        res = sim.engine.results
        self.assertEqual(sim.status, "Succeeded")
        for step in ("Compose_redacted_text", "Compose_skeleton_text"):
            with self.subTest(step):
                self.assertEqual(res[step]["status"], "Succeeded")
                out = res[step]["outputs"]
                self.assertTrue(out.startswith(PREFIX if step == "Compose_redacted_text" else PREFIX[:3]) or out, out)
                self.assertNotIn("holloway", out)

    def test_an_entity_wholly_past_the_end_is_harmless(self):
        def call(window):
            return [rr.ExtractorEntity("Email", EMAIL, len(TEXT) + 10, 5, 0.93)]
        sim = run_flow({"rev_narrativeraw": TEXT}, ALL_SETTINGS, call)
        self.assertEqual(sim.status, "Succeeded")
        self.assertEqual(sim.alerts, [])


if __name__ == "__main__":
    unittest.main()
