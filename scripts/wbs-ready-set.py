#!/usr/bin/env python3
"""What to build next, computed from the contracted dependency graph.

WHY THIS EXISTS
---------------
`IMP-0031`. `agents/lead-agent.md` routes whatever the reviewer asks for next. There is no queue,
no dependency graph and no contractual date anywhere in the system, so build order is set by
conversation. The result on 2026-08-18: Phase 1 — contractually due 25 September — had 0 of its 13
tasks started, while Phase 2, due three weeks later, had 8 done.

49 of the 61 tasks carry `Depends On`. That is a DAG, and it has been sitting unread in a
spreadsheet. This script computes the ready set from it.

CLIENT-SIDE BLOCKERS ARE SEPARATED, NOT HIDDEN. The workbook's own Summary sheet names them —
"DocuSign licence", "Alex (webhook config)", "DPO sign-off", "QBO API access". Work that is ready
for us and blocked on the Client is a different management problem from work we can simply start,
and conflating them is how a phase reaches its date with the build finished and nothing accepted.

Run:
    python3 scripts/wbs-ready-set.py
    python3 scripts/wbs-ready-set.py --json
    python3 scripts/wbs-ready-set.py --phase "Phase 1"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WBS = Path("contract/wbs.json")
STATE = Path("logs/state/wbs-state.json")
PARAMS = Path("contract/delivery-parameters.json")
DECLARED = Path("contract/declared-complete.json")
EXTDEPS = Path("contract/external-dependencies.json")
PHASE_ORDER = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phases 1–4"]


def load() -> tuple[dict, dict, dict, set[str]]:
    for p in (WBS, STATE, PARAMS):
        if not p.exists():
            print(f"wbs-ready-set: missing {p}", file=sys.stderr)
            raise SystemExit(2)
    wbs = json.loads(WBS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    declared = set()
    if DECLARED.exists():
        declared = {d["id"] for d in json.loads(DECLARED.read_text(encoding="utf-8"))["declared"]}
    extdeps = {}
    if EXTDEPS.exists():
        extdeps = json.loads(EXTDEPS.read_text(encoding="utf-8"))["dependencies"]
    return wbs, state, params, declared, extdeps


def compute() -> dict:
    wbs, state, params, declared, extdeps = load()
    complete_states = set(params["complete_states"])
    by_id = {t["id"]: t for t in state["tasks"]}
    auto = wbs["per_automation"]

    def is_complete(tid: str) -> bool:
        if tid in declared:
            return True
        t = by_id.get(tid)
        return bool(t and t["derived_status"] in complete_states)

    dependents: dict[str, int] = {tid: 0 for tid in by_id}
    for t in state["tasks"]:
        for d in t["depends_on"]:
            if d in dependents:
                dependents[d] += 1

    ready, blocked_by_task, blocked_by_client, done = [], [], [], []
    for t in state["tasks"]:
        tid = t["id"]
        if is_complete(tid):
            done.append(tid)
            continue
        unmet = [d for d in t["depends_on"] if not is_complete(d)]
        # Only an OUTSTANDING precondition blocks. An unknown one is reported, not assumed unmet:
        # treating every listed dependency as unmet made 0 of 61 tasks ready, which is not a queue.
        all_ext = auto.get(t["automation"], {}).get("external_dependencies", [])
        ext = [d for d in all_ext if extdeps.get(d, {}).get("state") == "outstanding"]
        unconfirmed = [d for d in all_ext if extdeps.get(d, {}).get("state", "unknown") == "unknown"]
        row = {
            "id": tid, "phase": t["phase"], "automation": t["automation"],
            "task": t["task"], "deliverable": t["deliverable"],
            "hours_low": t["hours_low"], "hours_high": t["hours_high"],
            "derived_status": t["derived_status"], "claimed_status": t["claimed_status"],
            "unmet_dependencies": unmet, "external_dependencies": ext,
            "unconfirmed_preconditions": unconfirmed,
            "blocker_owners": sorted({extdeps.get(d, {}).get("owner", "?") for d in ext}),
            "downstream_dependents": dependents.get(tid, 0),
        }
        if unmet:
            blocked_by_task.append(row)
        elif ext:
            blocked_by_client.append(row)
        else:
            ready.append(row)

    def order(rows):
        return sorted(rows, key=lambda r: (
            PHASE_ORDER.index(r["phase"]) if r["phase"] in PHASE_ORDER else 99,
            -r["downstream_dependents"],
            r["id"]))

    return {
        "ready": order(ready),
        "ready_but_client_blocked": order(blocked_by_client),
        "blocked_by_predecessor": order(blocked_by_task),
        "complete": sorted(done),
        "declared_complete": sorted(declared),
        "counts": {"ready": len(ready), "client_blocked": len(blocked_by_client),
                   "blocked": len(blocked_by_task), "complete": len(done),
                   "total": len(state["tasks"])},
    }


def render(r: dict, phase: str | None) -> str:
    L = [f"READY SET — {r['counts']['ready']} ready · "
         f"{r['counts']['client_blocked']} ready but blocked on the Client · "
         f"{r['counts']['blocked']} waiting on a predecessor · "
         f"{r['counts']['complete']}/{r['counts']['total']} complete", ""]

    def table(title, rows, extra):
        rows = [x for x in rows if not phase or x["phase"] == phase]
        L.append(f"── {title} ({len(rows)}) " + "─" * max(0, 50 - len(title)))
        if not rows:
            L.append("   none")
            return
        for x in rows[:20]:
            L.append(f"   {x['id']:<5} {x['phase']:<8} {x['task'][:44]:<44} "
                     f"{(str(x['hours_low']) + '-' + str(x['hours_high'])):>9}h  "
                     f"→{x['downstream_dependents']}")
            if extra and x[extra]:
                L.append(f"         {extra.replace('_', ' ')}: " + "; ".join(x[extra])[:96])
        if len(rows) > 20:
            L.append(f"   … {len(rows) - 20} more")

    table("READY — start these", r["ready"], "unconfirmed_preconditions")
    L.append("")
    table("READY FOR US, BLOCKED ON THE CLIENT", r["ready_but_client_blocked"],
          "external_dependencies")
    L.append("")
    table("WAITING ON A PREDECESSOR", r["blocked_by_predecessor"], "unmet_dependencies")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--phase", default=None)
    args = ap.parse_args(argv)
    r = compute()
    print(json.dumps(r, indent=2, ensure_ascii=False) if args.json else render(r, args.phase))
    return 0


if __name__ == "__main__":
    sys.exit(main())
