#!/usr/bin/env python3
"""Score a LIVE run of the seeded narrative cases (TD-13..TD-15) against what the rules require (WBS 5.3/5.4).

Run:
  python3 src/tests/narrative/score_seeded_run.py --live <file.json> --settings none|on [--case TD-13,TD-15]

This is NOT score_live_run.py. That script scores the raw AI Builder extractor output over the 20
corpus samples. This one scores what the whole flow wrote to Dataverse for the three seeded
applications in src/tests/data/narrative-test-data.json: the twelve redacted counterparts, and the
release flags.

<file.json> is a read of the seeded rows AFTER the flow has run, one object per submission id:
  {"TESTDATA-TD-13": {"rev_narrativeredacted": "...", "rev_disabilityimpactdescriptionredacted": "...",
                      ..., "rev_redactionreleased": false, "rev_redactionreviewrequired": true},
   "TESTDATA-TD-14": {...}, "TESTDATA-TD-15": {...}}
Columns left out are read as empty. Only the twelve ...redacted columns and the two flags are read.
The counterparts are unsecured, so a plain read reaches them. Read the REDACTED columns only; the raw
columns are secured on purpose and this script has no use for them.

--settings says which rev_setting state the run happened under:
  none  no Redaction* rows at all (every record must go to review)
  on    RedactionConfidenceThreshold 0.85 and RedactionAutoRelease true, auto-release saved last

Exit 0 when every selected case matches, 1 otherwise, 2 for a usage problem. A case with no live row is
MISSING, which is neither a pass nor a fail of the flow: the flow has not run, or the row was not read.

What a mismatch means. PHONE and the postcode in an ADDRESS are found by the flow's own shape rules, so
a miss there is a flow defect. NAME, FAMILY MEMBER, GP PRACTICE, EMAIL, AGE and the street part of an
ADDRESS come from the AI Builder model: a miss there is model recall (wbs:5.7), and the report says
which kind it saw by printing the expected and the live text side by side.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction_reference as rr  # noqa: E402

DATA = HERE.parents[1] / "tests" / "data" / "narrative-test-data.json"
SETTINGS_KEY = {"none": "withoutRedactionSettings", "on": "withThresholdAndAutoRelease"}
COUNTERPARTS = [red for _, red in rr.SCRUB_COLUMNS]


def norm(v) -> str:
    return (v or "").strip() if isinstance(v, str) or v is None else str(v)


def score_case(case: dict, live: dict | None, settings: str) -> tuple[str, list[str]]:
    """-> (PASS | FAIL | MISSING, lines)."""
    if live is None:
        return "MISSING", ["no live row supplied for this case"]
    problems, lines = [], []
    for red in COUNTERPARTS:
        want = case["expectedRedacted"].get(red, "")
        got = norm(live.get(red))
        if want is None:
            ok = got == ""        # the flow must NOT have written this counterpart
            want_s = "(empty: the flow must not write it)"
        else:
            ok = got == norm(want)
            want_s = want
        if want in ("", None) and got == "":
            continue
        lines.append(f"  {'ok  ' if ok else 'FAIL'} {red}")
        if not ok:
            problems.append(red)
            lines.append(f"       expected: {want_s}")
            lines.append(f"       live:     {got or '(empty)'}")
    exp = case["expectedRecord"][SETTINGS_KEY[settings]]
    for flag, want in (("rev_redactionreleased", exp["released"]),
                       ("rev_redactionreviewrequired", exp["rev_redactionreviewrequired"])):
        got = live.get(flag)
        ok = got is want or got == want
        lines.append(f"  {'ok  ' if ok else 'FAIL'} {flag} = {got!r} (expected {want!r})")
        if not ok:
            problems.append(flag)
    if exp["reasons"]:
        lines.append("  reasons the process owner's card should list (not stored on the row; read the Teams card): "
                     + ", ".join(exp["reasons"]))
    return ("FAIL" if problems else "PASS"), lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", type=Path, required=True)
    ap.add_argument("--settings", choices=sorted(SETTINGS_KEY), required=True)
    ap.add_argument("--case", help="comma-separated case ids, default all")
    ap.add_argument("--data", type=Path, default=DATA)
    a = ap.parse_args()
    try:
        data = json.loads(a.data.read_text(encoding="utf-8"))
        live = json.loads(a.live.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"score_seeded_run: cannot read input: {e}", file=sys.stderr)
        return 2
    wanted = {c.strip().upper() for c in a.case.split(",")} if a.case else None
    cases = [c for c in data["cases"] if wanted is None or c["caseId"].upper() in wanted]
    if not cases or (wanted and len(cases) != len(wanted)):
        print("score_seeded_run: no such case id", file=sys.stderr)
        return 2
    worst = 0
    for c in cases:
        sid = c["application"]["rev_sourcesubmissionid"]
        verdict, lines = score_case(c, live.get(sid), a.settings)
        print(f"{verdict:7} {c['caseId']} ({sid}) - {c['purpose']}")
        print("\n".join(lines))
        worst = max(worst, 1 if verdict in ("FAIL", "MISSING") else 0)
    return worst


if __name__ == "__main__":
    sys.exit(main())
