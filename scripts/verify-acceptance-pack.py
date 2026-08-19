#!/usr/bin/env python3
"""Gate: a phase acceptance record may not claim more than the evidence supports.

WHY THIS EXISTS
---------------
PM-R17/R18/R19. Build Terms B1 makes the phase acceptance record part of the Agreed Specification,
and B4/B11 hang the warranty window and the per-phase liability cap off its date. It is the highest-
consequence document this system produces, and until now it did not exist at all.

WHAT IT ENFORCES
----------------
  1  required fields present: Phase, Go-live, Accepted by, Accepted on, contracted hours
  2  `Accepted on` is a real ISO date, not in the future, not before the phase's go-live
  3  `Accepted by` is a named person — V6 is never inferred (PM-R18)
  4  every WBS task in the phase appears in the pack's table
  5  no task is claimed at a level above the evidence: a task whose derived state is not complete
     must appear in the open-items section with an owner
  6  a variance is stated ONLY if every task in the phase is closed (IMP-0065)
  7  the "does not assert" section is present and names the B8 platform exclusions — the pack is
     what fixes the boundary, so dropping it is not a formatting slip

Run:
    python3 scripts/verify-acceptance-pack.py contract/acceptance/PA-phase0.md
Exit 0 clean, 1 on a violation, 2 usage.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

STATE = Path("logs/state/wbs-state.json")
SA = Path("contract/service-agreement.json")
PARAMS = Path("contract/delivery-parameters.json")
REQUIRED_FIELDS = ["Phase", "Go-live", "Accepted by", "Accepted on", "Contracted hours"]
PLACEHOLDER = re.compile(r"<[^>\n]{2,60}>")


def field(txt: str, name: str) -> str | None:
    m = re.search(rf"(?im)^\s*[-*]?\s*{re.escape(name)}\s*:\s*(.+?)\s*$", txt)
    return m.group(1).strip() if m else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", type=Path)
    ap.add_argument("--today", default=None)
    args = ap.parse_args(argv)

    if not args.pack.exists():
        print(f"verify-acceptance-pack: {args.pack} does not exist", file=sys.stderr)
        return 2
    txt = args.pack.read_text(encoding="utf-8")
    today = args.today or dt.date.today().isoformat()
    v: list[str] = []

    # 1
    vals = {}
    for f in REQUIRED_FIELDS:
        val = field(txt, f)
        vals[f] = val
        if not val:
            v.append(f"missing required field '{f}:'")
        elif PLACEHOLDER.search(val):
            v.append(f"field '{f}:' still contains a template placeholder: {val}")

    # 2 / 3
    acc = vals.get("Accepted on")
    if acc and not PLACEHOLDER.search(acc):
        try:
            accd = dt.date.fromisoformat(acc)
            if accd.isoformat() > today:
                v.append(f"'Accepted on: {acc}' is in the future (today {today})")
            gl = vals.get("Go-live")
            if gl and not PLACEHOLDER.search(gl):
                try:
                    if dt.date.fromisoformat(gl) > accd:
                        v.append(f"go-live {gl} is after acceptance {acc}")
                except ValueError:
                    v.append(f"'Go-live: {gl}' is not an ISO date")
        except ValueError:
            v.append(f"'Accepted on: {acc}' is not an ISO date")
    by = vals.get("Accepted by")
    if by and (PLACEHOLDER.search(by) or len(by.split()) < 2):
        v.append(f"'Accepted by: {by}' must name a person — V6 is an act by the Client's authorised "
                 f"contact and is never inferred (PM-R18)")

    # 4 / 5 / 6
    phase = (vals.get("Phase") or "").split("—")[0].strip()
    if STATE.exists() and phase and not PLACEHOLDER.search(phase):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        params = json.loads(PARAMS.read_text(encoding="utf-8")) if PARAMS.exists() else {}
        complete = set(params.get("complete_states", []))
        tasks = [t for t in state["tasks"] if t["phase"].lower() == phase.lower()]
        if not tasks:
            v.append(f"no WBS tasks found for phase {phase!r} — check the Phase field matches the "
                     f"WBS 'Phase' column")
        listed = set(re.findall(r"\|\s*`?(\d+\.\d+)`?\s*\|", txt))
        for t in tasks:
            if t["id"] not in listed:
                v.append(f"WBS task {t['id']} ({t['task']}) is in {phase} and is not listed in the "
                         f"pack")
        open_tasks = [t for t in tasks if t["derived_status"] not in complete]
        open_section = txt.split("Open items carried into warranty", 1)
        carried = open_section[1] if len(open_section) > 1 else ""
        for t in open_tasks:
            if t["id"] not in carried:
                v.append(f"WBS task {t['id']} derives '{t['derived_status']}' and is not carried in "
                         f"the open-items section — a pack may not claim a phase complete above its "
                         f"evidence (PM-R19)")
        if open_tasks and re.search(r"(?im)^\|\s*Variance\s*\|\s*[-+]?\d", txt):
            v.append(f"a variance is stated while {len(open_tasks)} task(s) in {phase} are still "
                     f"open — an invoiced figure below estimate on an unfinished phase says nothing "
                     f"about efficiency (IMP-0065)")

    # 7
    if "does not assert" not in txt.lower():
        v.append("the 'What this record does not assert' section is missing")
    for needed in ("B8", "DocuSign", "QuickBooks"):
        if needed not in txt:
            v.append(f"the exclusions section does not mention {needed} — the pack is what fixes the "
                     f"boundary, so this is not a formatting slip")

    print(f"verify-acceptance-pack: {args.pack}")
    for x in v:
        print(f"  FAIL  {x}", file=sys.stderr)
    if v:
        print(f"\nverify-acceptance-pack: {len(v)} violation(s).", file=sys.stderr)
        return 1
    print("verify-acceptance-pack: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
