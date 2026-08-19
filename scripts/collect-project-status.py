#!/usr/bin/env python3
"""The single status snapshot every PM status answer is rendered from.

WHY A SNAPSHOT AND NOT AN AGENT READING DOCUMENTS
-------------------------------------------------
PM-R28. A status query will be asked often, so it must be cheap; and it must not be able to
hallucinate. So the numbers are computed here, once, and the agent is only allowed to say what
appears in this output. `agents/pm-agent.md` states the rule: no figure in a status answer that is
absent from this JSON.

WHAT IT REFUSES TO DO
---------------------
  * report a verification level above the evidence — V-levels come from logs/pipeline.log's own
    words, and V6 only from a recorded client acceptance
  * treat a claimed WBS status as fact — `derived_status` leads, `claimed_status` is shown beside it
  * report a variance for a phase that is still open (IMP-0065)
  * compute a warranty window while D-4's clause text is missing

Run:
    python3 scripts/collect-project-status.py            # human block
    python3 scripts/collect-project-status.py --json
    python3 scripts/collect-project-status.py --as-of 2026-09-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

SA = Path("contract/service-agreement.json")
WBS = Path("contract/wbs.json")
STATE = Path("logs/state/wbs-state.json")
DRIFT = Path("logs/state/baseline-drift.md")
WORKLOG = Path("logs/worklog.jsonl")
IMPLOG = Path("logs/improvement-log.jsonl")
PIPELINE = Path("logs/pipeline.log")
EXTDEPS = Path("contract/external-dependencies.json")
ACCEPT = Path("contract/acceptance")


def run_json(script: str, *extra: str) -> dict | None:
    try:
        r = subprocess.run([sys.executable, script, "--json", *extra],
                           capture_output=True, text=True, check=False)
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None
    except (OSError, json.JSONDecodeError):
        return None


def collect(as_of: str | None) -> dict:
    today = as_of or dt.date.today().isoformat()
    for p in (SA, WBS, STATE):
        if not p.exists():
            print(f"collect-project-status: missing {p} — run scripts/import-baseline.py and "
                  f"scripts/derive-wbs-state.py", file=sys.stderr)
            raise SystemExit(2)
    sa = json.loads(SA.read_text(encoding="utf-8"))
    wbs = json.loads(WBS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))

    ready = run_json("scripts/wbs-ready-set.py") or {}
    sched = run_json("scripts/schedule-risk.py", "--as-of", today) or {}

    # hours
    hours = {"invoiced": 0.0, "confirmed_unbilled": 0.0, "sessions": 0}
    if WORKLOG.exists():
        for line in WORKLOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            s = json.loads(line)
            hours["sessions"] += 1
            if not s.get("billable"):
                continue
            if s.get("status") == "BILLED" or s.get("invoice"):
                hours["invoiced"] += float(s["hours"])
            else:
                hours["confirmed_unbilled"] += float(s["hours"])

    # verification level, from the pipeline log's own words — never inferred
    levels = []
    if PIPELINE.exists():
        for line in PIPELINE.read_text(encoding="utf-8").splitlines()[-12:]:
            m = re.search(r"\[([A-Z/]+)\]\s+(SUCCESS|FAILED|HELD)", line)
            lv = re.findall(r"\bV([2-6])\b", line)
            if m:
                levels.append({"env": m.group(1), "result": m.group(2),
                               "levels_mentioned": sorted(set(lv)),
                               "date": line[1:17],
                               "v4_outstanding": bool(re.search(r"V4[^.]{0,80}(outstanding|NOT YET)",
                                                                line, re.I))})
    latest = levels[-1] if levels else None

    # findings queue
    findings = {"new": 0, "blockers_new": 0}
    if IMPLOG.exists():
        for line in IMPLOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("status") == "NEW":
                findings["new"] += 1
                if d.get("severity") == "blocker":
                    findings["blockers_new"] += 1

    # blockers with owner and age
    blockers = []
    if EXTDEPS.exists():
        deps = json.loads(EXTDEPS.read_text(encoding="utf-8"))["dependencies"]
        for name, d in deps.items():
            if d.get("state") != "outstanding":
                continue
            first = d.get("first_seen")
            age = None
            if first:
                age = (dt.date.fromisoformat(today) - dt.date.fromisoformat(first)).days
            blockers.append({"what": name, "owner": d.get("owner"), "age_days": age,
                             "internal": bool(d.get("internal")),
                             "evidence": d.get("evidence")})
    unconfirmed = 0
    if EXTDEPS.exists():
        unconfirmed = sum(1 for d in json.loads(EXTDEPS.read_text(encoding="utf-8"))["dependencies"]
                          .values() if d.get("state", "unknown") == "unknown")

    accepted = sorted(p.name for p in ACCEPT.glob("PA-*.md")) if ACCEPT.exists() else []

    drift = {}
    if DRIFT.exists():
        txt = DRIFT.read_text(encoding="utf-8")
        drift = {
            "reconciled": "RECONCILED" in txt,
            # v0.6 is not coming (reviewer, 2026-08-19); the 20-hour gap is closed by an invoice.
            # Read the resolution from the baseline rather than inferring it from the report's prose.
            "wbs_v06_outstanding": False,
            "baseline_final": True,
            "overclaims": len([d for d in state["disagreements"] if d["verdict"] == "OVERCLAIM"]),
            "underclaims": len([d for d in state["disagreements"] if d["verdict"] == "UNDERCLAIM"]),
        }

    return {
        "as_of": today,
        "engagement": {"total_contracted_hours": sa["total_hours"],
                       "basis": sa["basis"],
                       "completion_due": sa["milestones"].get("completion"),
                       "baseline_version": wbs["source"]["version"],
                       "baseline_accepted_by_client": wbs["source"]["accepted_by_client"]},
        "tasks": {"total": wbs["totals"]["tasks"],
                  "derived_counts": state["derived_counts"]},
        "schedule": sched.get("phases", []),
        "schedule_totals": sched.get("totals", {}),
        "queue": ready.get("counts", {}),
        "next_ready": [{"id": r["id"], "phase": r["phase"], "task": r["task"],
                        "hours": f"{r['hours_low']:g}-{r['hours_high']:g}"}
                       for r in ready.get("ready", [])[:5]],
        "hours": hours,
        "latest_deploy": latest,
        "acceptance_records": accepted,
        "warranty": {"status": sa["warranty"].get("status"),
                     "reason": sa["warranty"].get("reason"),
                     "open_issue": sa["warranty"].get("open_issue"),
                     "acceptance_routes": ["written confirmation",
                                           "10 business days' silence after submission",
                                           "live operational use"]},
        "blockers": sorted(blockers, key=lambda b: -(b["age_days"] or 0)),
        "unconfirmed_preconditions": unconfirmed,
        "findings": findings,
        "drift": drift,
    }


def render(s: dict) -> str:
    e = s["engagement"]
    L = [f"PROJECT STATUS — Grant Application Process        as of {s['as_of']}",
         f"{e['basis']} · {e['total_contracted_hours']} contracted hours · completion "
         f"{e['completion_due']} · baseline WBS {e['baseline_version']}"
         + (" (client-accepted)" if e["baseline_accepted_by_client"] else ""), ""]
    L.append("Phase    Due          Open   Remaining  Cum.hdrm  Blocked  Verdict")
    for p in s["schedule"]:
        L.append(f"{p['phase']:<8} {p['due']}  {p['open_tasks']:>2}/{p['total_tasks']:<2}  "
                 f"{p['remaining_hours_low']:>4.0f}-{p['remaining_hours_high']:<4.0f}h  "
                 f"{p['cumulative_headroom_hours']:>+8.1f}h  "
                 f"{p['client_blocked_hours_high']:>5.0f}h  {p['verdict']}")
    q = s["queue"]
    L += ["", f"Queue    {q.get('ready', 0)} ready · {q.get('client_blocked', 0)} blocked on the "
              f"Client · {q.get('blocked', 0)} awaiting a predecessor · "
              f"{q.get('complete', 0)}/{q.get('total', 0)} complete"]
    if s["next_ready"]:
        L.append("Next     " + " · ".join(f"{r['id']} {r['task'][:30]} ({r['hours']}h)"
                                          for r in s["next_ready"][:3]))
    h = s["hours"]
    L.append(f"Hours    {h['invoiced']:g} invoiced · {h['confirmed_unbilled']:g} confirmed "
             f"unbilled · {h['sessions']} ledger session(s)")
    d = s["latest_deploy"]
    if d:
        lv = ("V" + "/V".join(d["levels_mentioned"])) if d["levels_mentioned"] else "level unstated"
        L.append(f"Deploy   {d['env']} {d['result']} {d['date']} — {lv}"
                 + ("  (V4 outstanding)" if d["v4_outstanding"] else ""))
    L.append(f"Accepted {len(s['acceptance_records'])} phase acceptance record(s)"
             + ("" if s["acceptance_records"] else " — none yet; no warranty window has started"))
    w = s["warranty"]
    if w["status"] == "AVAILABLE":
        L.append("Warranty clause text present; acceptance has three routes (written · 10 business "
                 "days' silence after submission · live use) and the earliest wins")
    else:
        L.append(f"Warranty {w['status']} — {w.get('reason') or 'no clause text'}, so no window is "
                 f"computed")
    if w.get("open_issue"):
        L.append(f"         open: {w['open_issue'][:140]}")
    if s["blockers"]:
        L.append("Blockers")
        for b in s["blockers"]:
            age = f"{b['age_days']}d" if b["age_days"] is not None else "age unknown"
            L.append(f"         {'[internal] ' if b['internal'] else ''}{b['what']} — "
                     f"{b['owner']} — open {age}")
    L.append(f"Unconfirmed preconditions: {s['unconfirmed_preconditions']} "
             f"(neither satisfied nor known-blocked — someone must ask)")
    dr = s["drift"]
    if dr:
        L.append(f"Baseline {'reconciled' if dr['reconciled'] else 'NOT RECONCILED'} · "
                 f"{dr['overclaims']} overclaim · {dr['underclaims']} underclaim"
                 + (" · WBS v0.6 outstanding" if dr.get("wbs_v06_outstanding") else
                    " · baseline final, no v0.6 coming"))
    f = s["findings"]
    L.append(f"Findings {f['new']} NEW in the improvement log ({f['blockers_new']} blocker)"
             + (" — improvement-agent is due" if f["blockers_new"] or f["new"] >= 10 else ""))
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--as-of", default=None)
    args = ap.parse_args(argv)
    s = collect(args.as_of)
    print(json.dumps(s, indent=2, ensure_ascii=False) if args.json else render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
