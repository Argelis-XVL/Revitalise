#!/usr/bin/env python3
"""Remaining contracted work per phase against the days left to its contractual date.

WHY THIS EXISTS
---------------
PM-R09, and `IMP-0031`. The agreement fixes five dates — Phase 0 by 28 Aug 2026, Phase 1 by 25
Sep, Phase 2 by 16 Oct, Phase 3 by 27 Nov, Completion 11 Dec — and until now no agent had ever
read one. Dates were invisible, so the only way to notice a phase was late was to remember it.

TWO NUMBERS THAT MUST NOT BE CONFLATED (D-6):
  * ESTIMATES stay at the WBS figures. Do not re-estimate downward because AI assistance is
    expected — the WBS is the customer-accepted specification (D-5).
  * CAPACITY is physical: 16 h/week. Schedule risk is computed against that, not against expected
    AI throughput, because a date is missed in wall-clock time.
Actual hours are expected well below estimate. That makes this report pessimistic by design, and
pessimistic is the right direction for a contractual date.

Client-blocked work is reported separately: a phase that cannot start is not a phase running late
for the same reason, and the remedy is a phone call rather than more hours.

Run:
    python3 scripts/schedule-risk.py
    python3 scripts/schedule-risk.py --as-of 2026-09-01
    python3 scripts/schedule-risk.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SA = Path("contract/service-agreement.json")
STATE = Path("logs/state/wbs-state.json")
PARAMS = Path("contract/delivery-parameters.json")
WBS = Path("contract/wbs.json")
PHASES = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4"]


def working_days(a: dt.date, b: dt.date) -> int:
    if b <= a:
        return 0
    n = 0
    d = a
    while d < b:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def compute(as_of: str | None) -> dict:
    for p in (SA, STATE, PARAMS, WBS):
        if not p.exists():
            print(f"schedule-risk: missing {p}", file=sys.stderr)
            raise SystemExit(2)
    sa = json.loads(SA.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    wbs = json.loads(WBS.read_text(encoding="utf-8"))

    today = dt.date.fromisoformat(as_of) if as_of else dt.date.today()
    cap_week = params["capacity_hours_per_week"]
    cap_day = cap_week / 5.0
    complete = set(params["complete_states"])
    ext = {}
    p = Path("contract/external-dependencies.json")
    if p.exists():
        ext = json.loads(p.read_text(encoding="utf-8"))["dependencies"]
    auto = wbs["per_automation"]

    rows = []
    for ph in PHASES:
        tasks = [t for t in state["tasks"] if t["phase"] == ph]
        if ph == "Phase 1":
            tasks += [t for t in state["tasks"] if t["phase"] == "Phases 1–4"]
        open_tasks = [t for t in tasks if t["derived_status"] not in complete]
        lo = sum(t["hours_low"] or 0 for t in open_tasks)
        hi = sum(t["hours_high"] or 0 for t in open_tasks)
        blocked = [t for t in open_tasks
                   if any(ext.get(d, {}).get("state") == "outstanding"
                          for d in auto.get(t["automation"], {}).get("external_dependencies", []))]
        blocked_hi = sum(t["hours_high"] or 0 for t in blocked)

        key = ph.lower().replace(" ", "_")
        due = sa["milestones"].get(key) or sa["milestones"].get("completion")
        due_d = dt.date.fromisoformat(due)
        wd = working_days(today, due_d)
        avail = round(wd * cap_day, 1)
        headroom = round(avail - hi, 1)
        rows.append({
            "phase": ph, "due": due, "days_remaining": (due_d - today).days,
            "working_days_remaining": wd,
            "contracted_hours": sa["phase_hours"].get(key),
            "open_tasks": len(open_tasks), "total_tasks": len(tasks),
            "remaining_hours_low": lo, "remaining_hours_high": hi,
            "client_blocked_tasks": len(blocked), "client_blocked_hours_high": blocked_hi,
            "capacity_hours_available": avail, "headroom_hours": headroom,
        })

    # Capacity is SHARED across phases. Computing each phase against the full capacity to its own
    # date counts the same hours four times, which is how a plan reads OK on every line and misses
    # its dates anyway. So the verdict is cumulative: to hit Phase N you must also finish 0..N-1.
    running = 0.0
    for r in rows:
        running += r["remaining_hours_high"]
        r["cumulative_remaining_high"] = round(running, 1)
        r["cumulative_headroom_hours"] = round(r["capacity_hours_available"] - running, 1)
        due_d = dt.date.fromisoformat(r["due"])
        if r["open_tasks"] == 0:
            r["verdict"] = "COMPLETE"
        elif due_d < today:
            r["verdict"] = "OVERDUE"
        elif r["cumulative_headroom_hours"] < 0:
            r["verdict"] = "OVER CAPACITY"
        elif r["cumulative_headroom_hours"] < r["cumulative_remaining_high"] * 0.25:
            r["verdict"] = "TIGHT"
        elif r["client_blocked_hours_high"] >= r["remaining_hours_high"] * 0.5 and r["remaining_hours_high"] > 0:
            r["verdict"] = "BLOCKED ON CLIENT"
        else:
            r["verdict"] = "OK"

    # ── compression: the dates did not move, the start did ────────────────────────────────
    # The agreement's five dates were set from a 2026-07-04 kick-off. Delivery began 2026-08-10.
    # Each phase's PLANNED window is the gap between its milestone and the previous one; its ACTUAL
    # window is what is left of that once the late start is taken into account. Reported because a
    # phase can be comfortably inside its hour allocation and still have lost most of its calendar.
    ps = params.get("project_start", {})
    compression = None
    if ps.get("actual_work_start"):
        ko = dt.date.fromisoformat(ps["contractual_kick_off"])
        ws = dt.date.fromisoformat(ps["actual_work_start"])
        bounds = [ko] + [dt.date.fromisoformat(r["due"]) for r in rows]
        per_phase = []
        for i, r in enumerate(rows):
            planned_from, planned_to = bounds[i], bounds[i + 1]
            actual_from = max(planned_from, ws)
            planned = (planned_to - planned_from).days
            actual = max(0, (planned_to - actual_from).days)
            per_phase.append({
                "phase": r["phase"], "planned_window_days": planned,
                "actual_window_days": actual,
                "lost_days": planned - actual,
                "lost_share": round((planned - actual) / planned, 2) if planned else None,
            })
        compression = {
            "contractual_kick_off": ko.isoformat(), "actual_work_start": ws.isoformat(),
            "calendar_lost_days": (ws - ko).days,
            "end_dates_unchanged": True,
            "per_phase": per_phase,
            "relief": ps.get("relief_clause", {}).get("reference"),
            "attribution_open": [k for k, v in ps.get("delay_attribution", {}).items()
                                 if v.get("attributable_to") == "UNDETERMINED"],
        }

    return {"compression": compression,
            "as_of": today.isoformat(), "capacity_hours_per_week": cap_week,
            "estimating_rule": params["estimating_rule"], "phases": rows,
            "totals": {
                "remaining_hours_high": sum(r["remaining_hours_high"] for r in rows),
                "client_blocked_hours_high": sum(r["client_blocked_hours_high"] for r in rows),
                "open_tasks": sum(r["open_tasks"] for r in rows),
            }}


def render(s: dict) -> str:
    L = [f"SCHEDULE RISK — as of {s['as_of']} · capacity {s['capacity_hours_per_week']} h/week "
         f"(physical) · estimates at WBS values (D-6)", "",
         "Phase    Due          Days  Open  Remaining   Cumulative  Capacity  Headroom  Blocked  Verdict",
         "─" * 104]
    for r in s["phases"]:
        L.append(f"{r['phase']:<8} {r['due']}  {r['days_remaining']:>5}  "
                 f"{r['open_tasks']:>2}/{r['total_tasks']:<2} "
                 f"{r['remaining_hours_low']:>4.0f}-{r['remaining_hours_high']:<4.0f}h  "
                 f"{r['cumulative_remaining_high']:>9.0f}h  "
                 f"{r['capacity_hours_available']:>7.1f}h  "
                 f"{r['cumulative_headroom_hours']:>+8.1f}h  "
                 f"{r['client_blocked_hours_high']:>5.0f}h  {r['verdict']}")
    t = s["totals"]
    c = s.get("compression")
    if c:
        L += ["", f"── Calendar compression — the dates did not move, the start did " + "─" * 42,
              f"   Kick-off {c['contractual_kick_off']} · work began {c['actual_work_start']} · "
              f"{c['calendar_lost_days']} days lost before delivery, end dates unchanged", "",
              "   Phase    Planned window   Actual window   Lost"]
        for x in c["per_phase"]:
            share = f" ({x['lost_share']:.0%})" if x["lost_share"] else ""
            L.append(f"   {x['phase']:<8} {x['planned_window_days']:>10}d "
                     f"{x['actual_window_days']:>14}d {x['lost_days']:>6}d{share}")
        if c["attribution_open"]:
            L.append(f"   Relief: {c['relief']} may apply to client-caused delay. Attribution "
                     f"still open for: {', '.join(c['attribution_open'])}")
    L += ["", "─" * 104,
          f"{'TOTAL':<8} {'':<12} {'':>5}  {t['open_tasks']:>5} "
          f"{'':>5}{t['remaining_hours_high']:<4.0f}h {'':>18} "
          f"{'':>3}    {t['client_blocked_hours_high']:.0f}h blocked on the Client", "",
          "Headroom is capacity minus the CUMULATIVE remaining high estimate — to hit a phase's "
          "date you must also have finished every earlier phase, and the same hours cannot serve "
          "two phases.",
          "Actual hours are expected well below estimate (D-6), so a negative headroom is a "
          "warning, not a forecast — but a date is missed in wall-clock time, so the pessimistic "
          "direction is the right one.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    s = compute(args.as_of)
    print(json.dumps(s, indent=2) if args.json else render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
