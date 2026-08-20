#!/usr/bin/env python3
"""What has been DELIVERED, priced at the WBS estimate for those deliverables.

WHY THIS EXISTS, AND WHY IT IS NOT reconstruct-worklog.py
--------------------------------------------------------
Two different questions, and conflating them is how this engagement got a HOLD:

  reconstruct-worklog.py   "how long was I at the keyboard?"   — evidence spans, a FLOOR
  this script              "what did the Client receive?"      — WBS estimates, a CEILING

The reviewer's decision, 2026-08-20, in their own words: *"Just look at what is built and compare
that to what is estimated in the WBS. The actual session times don't have to be equated. Its my
benefit that the development and deployment is quicker then doing it all manual."*

On a deliverable basis the productivity gain accrues to the supplier, which is a legitimate
commercial position on a fixed breakdown of accepted scope — and the opposite of what
`docs/Import/baseline-lock.yml` D-6 recorded. See THE CONFLICT below; this script prints it every
run rather than resolving it silently.

WHAT IT WILL NOT DO
-------------------
  * treat a claimed status as a result — completion is DERIVED from evidence (C-COM-005), read
    from logs/state/wbs-state.json, which scripts/derive-wbs-state.py generates
  * earn anything for a task whose evidence is `manual` only — nothing in the repository can
    confirm those, so they are reported as UNPROVEN and left for a human, never quietly counted
  * earn a partial task's full estimate — reported separately, never added in
  * re-bill: hours already invoiced come from scripts/lib/worklog.py and are subtracted
  * emit one number where the WBS gives a band. Low and high are both real.

Run:
    python3 scripts/deliverable-hours.py
    python3 scripts/deliverable-hours.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import worklog as WL  # noqa: E402

STATE = Path("logs/state/wbs-state.json")
WBS = Path("contract/wbs.json")
PARAMS = Path("contract/delivery-parameters.json")
SA = Path("contract/service-agreement.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--outside-wbs", type=float, default=20.0,
                    help="hours inside the invoiced total that bought work NO WBS task covers, "
                         "and which therefore may not be credited against delivered tasks. "
                         "Default 20: the reviewer confirmed on 2026-08-20 that WL-0001's 64 "
                         "hours include ~20 for DocuSign platform selection and for "
                         "documentation rework after a solution design change, neither of which "
                         "the accepted WBS carries. Crediting them against WBS tasks would "
                         "under-bill the delivered scope by that much.")
    ap.add_argument("--exclude", nargs="*", default=["2.8"],
                    help="task ids to hold out of EARNED despite deriving complete. Default 2.8: "
                         "its deliverable is a client sign-off and its evidence rule resolves to "
                         "our own test report (IMP-0097).")
    args = ap.parse_args(argv)

    for p in (STATE, WBS, PARAMS):
        if not p.exists():
            print(f"deliverable-hours: {p} missing — run scripts/derive-wbs-state.py first. A "
                  f"gate or a figure computed from a missing input must fail, not guess "
                  f"(IMP-0007).", file=sys.stderr)
            return 2

    state = json.loads(STATE.read_text(encoding="utf-8"))
    wbs = json.loads(WBS.read_text(encoding="utf-8"))
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    sa = json.loads(SA.read_text(encoding="utf-8")) if SA.exists() else {}
    complete_states = set(params.get("complete_states", []))

    held = {x.strip() for x in args.exclude if x.strip()}
    buckets = {"earned": [], "partial": [], "unproven": [], "not_started": [], "held": []}
    for t in state["tasks"]:
        st = t["derived_status"]
        if t["id"] in held and st in complete_states:
            buckets["held"].append(t)
        elif st in complete_states:
            buckets["earned"].append(t)
        elif st == "partial":
            buckets["partial"].append(t)
        elif st == "manual_only":
            buckets["unproven"].append(t)
        else:
            buckets["not_started"].append(t)

    def band(rows):
        return (round(sum(r["hours_low"] for r in rows), 1),
                round(sum(r["hours_high"] for r in rows), 1))

    per_phase: dict[str, dict] = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0]))
    for name, rows in buckets.items():
        for t in rows:
            cell = per_phase[t["phase"]][name]
            cell[0] += t["hours_low"]
            cell[1] += t["hours_high"]
            cell[2] += 1

    invoiced_total = WL.invoiced_to_date(WL.load()[0])
    # Only the portion of the invoiced total that bought WBS scope may be credited against
    # delivered WBS tasks. Crediting out-of-breakdown work would silently discount the build.
    invoiced = round(invoiced_total - args.outside_wbs, 1)
    e_low, e_high = band(buckets["earned"])
    p_low, p_high = band(buckets["partial"])
    u_low, u_high = band(buckets["unproven"])
    gap = wbs.get("known_gap") or {}
    gap_hours = float(gap.get("hours") or 0)

    result = {
        "basis": "delivered scope priced at the WBS estimate (reviewer decision 2026-08-20)",
        "invoiced_to_date": invoiced_total,
        "invoiced_outside_the_wbs": args.outside_wbs,
        "invoiced_credited_against_wbs_scope": invoiced,
        "held_back": {"tasks": [t["id"] for t in buckets["held"]],
                      "low": band(buckets["held"])[0], "high": band(buckets["held"])[1]},
        "earned": {"tasks": len(buckets["earned"]), "low": e_low, "high": e_high},
        "partial": {"tasks": len(buckets["partial"]), "low": p_low, "high": p_high},
        "unproven_manual_only": {"tasks": len(buckets["unproven"]), "low": u_low, "high": u_high},
        "not_started": {"tasks": len(buckets["not_started"])},
        "invoiceable_now": {"low": round(e_low - invoiced, 1), "high": round(e_high - invoiced, 1)},
        "known_gap_hours_outside_the_wbs": gap_hours,
        "contract_total_hours": sa.get("total_hours"),
        "per_phase": {ph: {k: {"low": round(v[0], 1), "high": round(v[1], 1), "tasks": v[2]}
                           for k, v in d.items()} for ph, d in per_phase.items()},
        "conflicts_with": "docs/Import/baseline-lock.yml D-6 / contract/delivery-parameters.json "
                          "estimating_rule — both say an actual may never be proposed AT the "
                          "estimate (IMP-0032). This script does exactly that, by decision.",
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("DELIVERED SCOPE PRICED AT THE WBS ESTIMATE   (hours only — D-3)\n")
    print(f"  Basis: what the Client received, not how long it took. Completion is DERIVED from")
    print(f"         evidence in logs/state/wbs-state.json, never read from a Status column"
          f" (C-COM-005).\n")
    print(f"  {'bucket':<28} {'tasks':>5}   {'low':>7}  {'high':>7}")
    print(f"  {'-'*28} {'-'*5}   {'-'*7}  {'-'*7}")
    for label, key in (("EARNED — evidenced", "earned"),
                       ("held back — see --exclude", "held"),
                       ("partial — not earned yet", "partial"),
                       ("UNPROVEN — manual evidence", "unproven"),
                       ("not started", "not_started")):
        rows = buckets[key]
        lo, hi = band(rows)
        print(f"  {label:<28} {len(rows):>5}   {lo:>7.1f}  {hi:>7.1f}")
    print()
    print(f"  earned                          {e_low:>7.1f}  {e_high:>7.1f}")
    print(f"  invoiced to date                {-invoiced_total:>7.1f}  {-invoiced_total:>7.1f}   "
          f"(C-COM-003)")
    print(f"  add back: bought non-WBS work   {args.outside_wbs:>7.1f}  {args.outside_wbs:>7.1f}   "
          f"(no WBS task covers it)")
    print(f"  {'='*32} {'='*7}  {'='*7}")
    print(f"  INVOICEABLE NOW                 {e_low - invoiced:>7.1f}  {e_high - invoiced:>7.1f}")
    print()
    for ph in sorted(per_phase):
        d = per_phase[ph]
        ear = d.get("earned", [0, 0, 0])
        unp = d.get("unproven", [0, 0, 0])
        par = d.get("partial", [0, 0, 0])
        print(f"  {ph:<9} earned {ear[2]:>2} task(s) {ear[0]:>6.1f}-{ear[1]:<6.1f} · "
              f"partial {par[2]:>2} · unproven {unp[2]:>2} ({unp[0]:.0f}-{unp[1]:.0f}h)")
    print()
    if gap_hours:
        print(f"  Outside the WBS entirely: {gap_hours:g} h — {gap.get('scope', '')}. Already")
        print(f"  performed and already inside the invoiced total; no task can carry it until a")
        print(f"  WBS v0.6 exists (C-COM-009 — v0.5 is the customer-accepted specification).\n")
    print("  THE CONFLICT, stated every run. contract/delivery-parameters.json's estimating_rule")
    print("  and baseline-lock.yml D-6 both say an actual may NEVER be proposed at the estimate")
    print("  value (IMP-0032). This script does precisely that, because the reviewer decided on")
    print("  2026-08-20 that delivered scope, not elapsed time, is the billing basis. One of the")
    print("  two must be amended behind APPROVE BASELINE — until then the repository holds two")
    print("  contradictory rules and this line is the only thing saying so.\n")
    print("  UNPROVEN is the number that decides the answer. Nothing in the repository can confirm")
    print("  a task whose only evidence rule is `manual`. Each is a question for you, not a gap to")
    print("  round away.")
    print("\nNothing has been written. logs/worklog.jsonl is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
