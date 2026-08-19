#!/usr/bin/env python3
"""Propose candidate work sessions from repository evidence. NEVER writes the ledger.

WHY THE SPLIT MATTERS
---------------------
This script produces a **proposal**. `logs/worklog.jsonl` is the ledger of record and only
`commercial-agent` writes it, only after `APPROVE TIMESHEET`. If this script could write the ledger,
the system would be generating its own invoices.

WHAT IT CAN AND CANNOT SEE
--------------------------
It can see when a build ran, when a deploy landed, when a commit was made and when a finding was
recorded. It cannot see the hour spent reading the WBS, the call with Emily, the maker-portal clicks,
or the agent working while you did something else.

So the output reports **two separate numbers** and never conflates them:

    evidence_span    first to last timestamp in the cluster. A LOWER BOUND on elapsed time.
    proposed         span + a lead-in allowance, rounded. A FLOOR for you to raise.

Work precedes its first log line — a `build.log` entry is written *after* the work that produced it.
The 2026-08-16 cluster spans 1.68 h and its log entry describes decompilation-grade diagnosis, a
secret-scan incident and three stale assertions fixed. Nobody did that in 1.68 hours.

`--lead-in` is therefore a floor, never a ceiling, and every proposal says so.

Run:
    python3 scripts/reconstruct-worklog.py --since 2026-08-18
    python3 scripts/reconstruct-worklog.py --since 2026-08-01 --json
    python3 scripts/reconstruct-worklog.py --since 2026-08-01 --gap 90 --lead-in 45
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

LOGS = {"build": Path("logs/build.log"), "pipeline": Path("logs/pipeline.log"),
        "routing": Path("logs/routing.log")}
IMPLOG = Path("logs/improvement-log.jsonl")
WORKLOG = Path("logs/worklog.jsonl")
EVMAP = Path("contract/evidence-map.json")
TS = re.compile(r"^\[(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})\]")


def gather(since: str) -> list[dict]:
    ev: list[dict] = []
    for kind, path in LOGS.items():
        if not path.exists():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = TS.match(line)
            if not m or m.group(1) < since:
                continue
            ev.append({"when": f"{m.group(1)}T{m.group(2)}", "kind": kind,
                       "ref": f"{path}:{m.group(1)} {m.group(2)}", "text": line[:400]})
    if IMPLOG.exists():
        for line in IMPLOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = (d.get("ts") or "")[:16]
            if len(ts) >= 16 and ts[:10] >= since:
                ev.append({"when": ts, "kind": "finding",
                           "ref": f"{IMPLOG}:{d.get('id')}",
                           "text": f"{d.get('id')} {d.get('what', '')[:200]}"})
    try:
        r = subprocess.run(["git", "log", f"--since={since}",
                            "--date=format:%Y-%m-%dT%H:%M", "--pretty=%h|%ad|%s"],
                           capture_output=True, text=True, check=False)
        for line in r.stdout.splitlines():
            sha, when, subj = line.split("|", 2)
            ev.append({"when": when, "kind": "commit", "ref": f"git:{sha}", "text": subj[:300]})
    except (OSError, ValueError):
        pass
    return sorted(ev, key=lambda e: e["when"])


def propose_wbs(texts: str) -> list[str]:
    """Reverse-lookup the evidence map: which tasks name an artefact this session mentions?"""
    if not EVMAP.exists():
        return []
    rules = json.loads(EVMAP.read_text(encoding="utf-8"))["rules"]
    hits = set()
    for tid, rs in rules.items():
        for r in rs:
            for key in ("value", "pattern", "file"):
                v = r.get(key)
                if not v or r.get("kind") == "manual":
                    continue
                name = Path(str(v)).name.replace("*", "").strip()
                if len(name) >= 6 and name.lower() in texts.lower():
                    hits.add(tid)
    return sorted(hits)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="YYYY-MM-DD")
    ap.add_argument("--gap", type=int, default=90, help="idle minutes that end a session")
    ap.add_argument("--lead-in", type=int, default=45,
                    help="minutes of work assumed BEFORE the first log line of a session")
    ap.add_argument("--increment", type=float, default=0.25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    ev = gather(args.since)
    if not ev:
        print(f"reconstruct-worklog: no evidence at or after {args.since}", file=sys.stderr)
        return 1

    already: set[str] = set()
    if WORKLOG.exists():
        for line in WORKLOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                s = json.loads(line)
                for r in s.get("evidence", []) or []:
                    already.add(r)

    clusters: list[list[dict]] = [[ev[0]]]
    for a, b in zip(ev, ev[1:]):
        ta = dt.datetime.fromisoformat(a["when"])
        tb = dt.datetime.fromisoformat(b["when"])
        if (tb - ta).total_seconds() / 60.0 > args.gap:
            clusters.append([b])
        else:
            clusters[-1].append(b)

    out = []
    for c in clusters:
        first = dt.datetime.fromisoformat(c[0]["when"])
        last = dt.datetime.fromisoformat(c[-1]["when"])
        span_h = (last - first).total_seconds() / 3600.0
        raw = span_h + args.lead_in / 60.0
        proposed = round(raw / args.increment) * args.increment
        proposed = max(proposed, args.increment)
        texts = " ".join(x["text"] for x in c)
        kinds = sorted({x["kind"] for x in c})
        wt = ("deployment" if "pipeline" in kinds else
              "development" if "build" in kinds or "commit" in kinds else
              "project_management")
        sysish = bool(re.search(r"agents/|skills/|constraints/|scripts/|self-learning|improvement",
                                texts))
        out.append({
            "date": first.date().isoformat(),
            "start": first.strftime("%H:%M"), "end": last.strftime("%H:%M"),
            "evidence_span_hours": round(span_h, 2),
            "proposed_hours": round(proposed, 2),
            "work_type": "system" if sysish and wt != "deployment" else wt,
            "billable": not sysish,
            "wbs_suggested": propose_wbs(texts),
            "evidence": [x["ref"] for x in c],
            "already_in_ledger": [r for r in (x["ref"] for x in c) if r in already],
            "events": len(c), "kinds": kinds,
            "activity": c[0]["text"][:160],
        })

    if args.json:
        print(json.dumps({"since": args.since, "gap_minutes": args.gap,
                          "lead_in_minutes": args.lead_in, "candidates": out}, indent=2))
        return 0

    tot_span = sum(c["evidence_span_hours"] for c in out)
    tot_prop = sum(c["proposed_hours"] for c in out)
    print(f"CANDIDATE SESSIONS since {args.since} — {len(out)} cluster(s), "
          f"evidence span {tot_span:.2f}h → proposed {tot_prop:.2f}h "
          f"(gap {args.gap}m, lead-in {args.lead_in}m)\n")
    print("  date        window        span  proposed  type          billable  WBS suggested")
    for c in out:
        print(f"  {c['date']}  {c['start']}-{c['end']}  {c['evidence_span_hours']:>5.2f}h  "
              f"{c['proposed_hours']:>7.2f}h  {c['work_type']:<13} "
              f"{'yes' if c['billable'] else 'NO ':<8}  "
              f"{', '.join(c['wbs_suggested']) or '—'}")
        if c["already_in_ledger"]:
            print(f"      ⚠ {len(c['already_in_ledger'])} evidence ref(s) already in the ledger — "
                  f"check for a double count")
    print("\nThese are a FLOOR derived from timestamps, not a record of your attention. Work precedes"
          "\nits first log line, and the repository cannot see calls, walkthroughs or portal clicks."
          "\nEdit any line, add human-declared sessions, then APPROVE TIMESHEET.")
    print("\nNothing has been written. logs/worklog.jsonl is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
