#!/usr/bin/env python3
"""Compute the hours for a monthly invoice. HOURS ONLY — no fee is calculated here.

WHY NO FEE
----------
D-3, in the reviewer's words: *"Hours for the baseline is perfect."* No fee figure and no hourly
rate appears anywhere in this repository. The invoice document carries hours; the money is applied
outside the repo from a rate held outside it. That is also why `verify-worklog.py` fails any ledger
line containing a currency or rate reference.

WHY A SCRIPT AND NOT AN AGENT
-----------------------------
PM-R12. An agent that adds up hours by hand will eventually add them up wrong, and this output goes
to a client's finance address. Totals are computed here; the agent's prose wraps numbers it did not
invent, and `verify-worklog.py` recomputes and compares before an invoice may be issued.

WHAT IT WILL NOT DO
-------------------
  * bill a session twice — a session already carrying an `invoice` is excluded (C-COM-003)
  * bill non-billable work — `system` and `travel` never appear
  * re-derive the historic seed — D-7's 64 hours are reported as already invoiced and excluded
  * compute a variance against an estimate for a phase that is still open (IMP-0065): an invoiced
    figure below estimate on an unfinished phase says nothing about efficiency

Run:
    python3 scripts/compute-invoice.py --month 2026-08
    python3 scripts/compute-invoice.py --month 2026-08 --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

LOG = Path("logs/worklog.jsonl")
WBS = Path("contract/wbs.json")
STATE = Path("logs/state/wbs-state.json")
PARAMS = Path("contract/delivery-parameters.json")


def compute(month: str) -> dict:
    if not LOG.exists():
        print(f"compute-invoice: {LOG} missing", file=sys.stderr)
        raise SystemExit(2)
    rows = [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    wbs = json.loads(WBS.read_text(encoding="utf-8")) if WBS.exists() else {"tasks": []}
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"tasks": []}
    params = json.loads(PARAMS.read_text(encoding="utf-8")) if PARAMS.exists() else {}
    complete = set(params.get("complete_states", []))

    task_phase = {t["id"]: t["phase"] for t in wbs["tasks"]}
    open_by_phase: dict[str, int] = defaultdict(int)
    for t in state.get("tasks", []):
        if t["derived_status"] not in complete:
            open_by_phase[t["phase"]] += 1

    corrected = {s["corrects"] for s in rows
                 if s.get("kind") == "correction" and s.get("corrects")}
    billable, excluded, already = [], [], []
    for s in rows:
        if s.get("id") in corrected:
            continue          # superseded by a correction — excluded from every total
        if s.get("kind") == "correction":
            continue
        if s.get("kind") == "historic_seed":
            already.append(s)
            continue
        if not s.get("date", "").startswith(month):
            continue
        if s.get("invoice"):
            already.append(s)
        elif not s.get("billable"):
            excluded.append(s)
        else:
            billable.append(s)

    by_type: dict[str, float] = defaultdict(float)
    by_phase: dict[str, float] = defaultdict(float)
    by_task: dict[str, float] = defaultdict(float)
    for s in billable:
        h = float(s["hours"])
        by_type[s.get("work_type", "?")] += h
        alloc = s.get("allocation") or []
        if alloc and all(a.get("hours") is not None for a in alloc):
            for a in alloc:
                tid = a.get("wbs")
                by_task[tid] += float(a["hours"])
                by_phase[task_phase.get(tid, "(unmapped)")] += float(a["hours"])
        else:
            ids = s.get("wbs") or ["(unmapped)"]
            share = h / len(ids)
            for tid in ids:
                by_task[tid] += share
                by_phase[task_phase.get(tid, "(unmapped)")] += share

    total = round(sum(float(s["hours"]) for s in billable), 2)

    # quoted-vs-actual, but ONLY for phases that are closed (IMP-0065)
    est_high = defaultdict(float)
    for t in wbs["tasks"]:
        est_high[t["phase"]] += t["hours_high"] or 0
    variance = []
    for ph, booked in sorted(by_phase.items()):
        if open_by_phase.get(ph, 0) > 0:
            variance.append({"phase": ph, "booked_this_month": round(booked, 2),
                             "estimate_high": est_high.get(ph),
                             "variance": None,
                             "why_no_variance": f"{open_by_phase[ph]} task(s) still open — a "
                                                f"variance against an estimate is meaningless "
                                                f"until the phase is closed (IMP-0065)"})
        else:
            variance.append({"phase": ph, "booked_this_month": round(booked, 2),
                             "estimate_high": est_high.get(ph),
                             "variance": round(booked - est_high.get(ph, 0), 2),
                             "why_no_variance": None})

    return {
        "month": month, "units": "hours", "no_fee_reason": "D-3 — hours only in this repository",
        "total_billable_hours": total,
        "sessions_billable": len(billable), "sessions_excluded": len(excluded),
        "sessions_already_invoiced": len(already),
        "by_work_type": {k: round(v, 2) for k, v in sorted(by_type.items())},
        "by_phase": {k: round(v, 2) for k, v in sorted(by_phase.items())},
        "by_task": {k: round(v, 2) for k, v in sorted(by_task.items())},
        "excluded": [{"id": s["id"], "hours": s["hours"],
                      "reason": s.get("non_billable_reason") or s.get("work_type")}
                     for s in excluded],
        "previously_invoiced_hours": round(
            sum(float(s["hours"]) for s in already if s.get("billable")), 2),
        "phase_variance": variance,
    }


def render(r: dict) -> str:
    L = [f"INVOICE HOURS — {r['month']}   (hours only; no fee is computed in this repository, D-3)",
         "",
         f"Billable this month : {r['total_billable_hours']:g} h across "
         f"{r['sessions_billable']} session(s)",
         f"Already invoiced    : {r['previously_invoiced_hours']:g} h "
         f"({r['sessions_already_invoiced']} session(s)) — excluded, never re-billed (C-COM-003)",
         f"Non-billable        : {len(r['excluded'])} session(s)", ""]
    if r["by_work_type"]:
        L += ["By work type:"] + [f"   {k:<20} {v:>7g} h" for k, v in r["by_work_type"].items()] + [""]
    if r["by_phase"]:
        L += ["By phase:"] + [f"   {k:<20} {v:>7g} h" for k, v in r["by_phase"].items()] + [""]
    if r["by_task"]:
        L += ["By WBS task:"] + [f"   {k:<20} {v:>7g} h" for k, v in r["by_task"].items()] + [""]
    if r["excluded"]:
        L += ["Excluded as non-billable:"] + \
             [f"   {e['id']:<10} {e['hours']:>5g} h  {e['reason']}" for e in r["excluded"]] + [""]
    open_ph = [v for v in r["phase_variance"] if v["variance"] is None]
    if open_ph:
        L += ["No variance reported for these phases — they are still open:"]
        L += [f"   {v['phase']}: {v['why_no_variance']}" for v in open_ph]
        L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month", required=True, help="YYYY-MM")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    r = compute(args.month)
    print(json.dumps(r, indent=2) if args.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
