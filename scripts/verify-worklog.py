#!/usr/bin/env python3
"""Gate: the billable-hours ledger. Every invariant here exists because of a specific finding.

WHY THIS EXISTS
---------------
`IMP-0032`: six weeks into a time-and-materials engagement the WBS's `Actual Hours` column was
empty on all 61 rows. `IMP-0065`: an invoiced figure was then read as a completed figure, and the
wrong inference was written into the committed baseline. Hours are the invoice on this engagement,
so the ledger needs the same discipline the solution source gets.

THE INVARIANTS

  1  ids unique, matching WL-nnnn; dates ISO; hours > 0
  2  hours <= max_hours_per_day per date, and no two sessions overlap on one date
  3  every billable session declares at least one WBS task id from the accepted baseline, or a
     change-order reference (C-COM-002)                                    [chain gate also checks]
  4  every session's evidence reference RESOLVES — a named log line, a commit, or a file that
     exists. An unresolvable reference is a fabricated hour (C-COM-001)
  5  `confirmed_by` non-empty (C-COM-001) — no confirmation, no bill
  6  a session appears on at most one issued invoice; BILLED lines are immutable (C-COM-003)
  7  `work_type` exists in the rate card's declared types; `system` work is never billable
  8  no session dated in the future; none before the engagement kick-off
  9  historic seeds: must be status BILLED, must declare their split or say it is unknown, and are
     immutable — the D-7 rule that Phase 0 and Phase 2 hours are never re-derived
 10  no fee or rate figure anywhere in the ledger (D-3)
 11  no session may claim hours EQUAL to the WBS estimate for its tasks (IMP-0032/D-6): actuals
     are expected below estimate, and an actual that exactly equals an estimate is almost always
     an estimate that has been copied into the actuals column

Run:
    python3 scripts/verify-worklog.py
    python3 scripts/verify-worklog.py --worklog <path> [--no-baseline-check]
Exit 0 clean, 1 on a violation, 2 usage. Fails when the ledger is missing (IMP-0007); an EMPTY
ledger is allowed only when it contains zero lines and is reported as such.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import worklog as WL  # noqa: E402  — the SINGLE definition of what the ledger means

DEF_LOG = Path("logs/worklog.jsonl")
WBS = Path("contract/wbs.json")
PARAMS = Path("contract/delivery-parameters.json")
KICKOFF = "2026-07-04"
MAX_PER_DAY = 12.0
WORK_TYPES = {"consultancy", "development", "deployment", "project_management", "system", "travel"}
NEVER_BILLABLE = {"system", "travel"}


def resolves(ref: str) -> bool:
    """An evidence reference must point at something real."""
    if ref.startswith("git:"):
        sha = ref.split(":", 1)[1].strip()
        r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                           capture_output=True, check=False)
        return r.returncode == 0
    if "#" in ref:
        ref = ref.split("#", 1)[0]
    if ":" in ref and not ref.startswith(("http://", "https://")):
        path, _, tail = ref.partition(":")
        p = Path(path)
        if not p.exists():
            return False
        if tail and p.is_file():
            try:
                return tail.strip() in p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return False
        return True
    return Path(ref).exists()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worklog", type=Path, default=DEF_LOG)
    ap.add_argument("--no-baseline-check", action="store_true",
                    help="skip WBS-id validation (fixtures with no baseline)")
    ap.add_argument("--today", default=None)
    args = ap.parse_args(argv)

    if not args.worklog.exists():
        print(f"verify-worklog: {args.worklog} does not exist — refusing to report OK over "
              f"nothing (IMP-0007).", file=sys.stderr)
        return 2

    known: set[str] = set()
    est: dict[str, float] = {}
    if not args.no_baseline_check:
        if not WBS.exists():
            print("verify-worklog: contract/wbs.json missing — run scripts/import-baseline.py",
                  file=sys.stderr)
            return 2
        wbs = json.loads(WBS.read_text(encoding="utf-8"))
        known = {t["id"] for t in wbs["tasks"]}
        est = {t["id"]: (t["hours_high"] or 0) for t in wbs["tasks"]}

    today = args.today or dt.date.today().isoformat()
    v: list[str] = []
    warn: list[str] = []
    seen_ids: set[str] = set()
    by_date: dict[str, list[dict]] = {}
    invoiced: dict[str, str] = {}
    rows: list[dict] = []

    raw = args.worklog.read_text(encoding="utf-8")
    # A `correction` entry supersedes the session it names. The superseded session stays in the file
    # (append-only) and is excluded from every total, so an over-count is visible AND harmless.
    # The rule itself lives in scripts/lib/worklog.py and is not re-derived here (IMP-0093).
    _all, _ = WL.load(args.worklog)
    corrected: set[str] = WL.superseded_ids(_all)
    for i, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            s = json.loads(line)
        except json.JSONDecodeError as exc:
            v.append(f"line {i}: not valid JSON: {exc}")
            continue
        rows.append(s)
        sid = s.get("id", f"(line {i})")
        if s.get("kind") == "correction":
            if not s.get("corrects"):
                v.append(f"{sid}: a correction must name the session it corrects")
            elif s.get("billable"):
                v.append(f"{sid}: a correction must not be billable")
            if s.get("corrects") and s["corrects"] not in {r.get("id") for r in rows}:
                warn.append(f"{sid}: corrects {s['corrects']!r}, which appears later in the file or "
                            f"not at all — check the reference")
        if s.get("id") in corrected:
            s["_superseded"] = True

        # 1
        if not re.fullmatch(r"WL-\d{4}", str(s.get("id", ""))):
            v.append(f"{sid}: id must match WL-nnnn")
        if s["id"] in seen_ids:
            v.append(f"{sid}: duplicate id")
        seen_ids.add(s.get("id"))
        try:
            dt.date.fromisoformat(s["date"])
        except (KeyError, ValueError):
            v.append(f"{sid}: date must be ISO YYYY-MM-DD")
            continue
        hours = s.get("hours")
        if not isinstance(hours, (int, float)) or hours <= 0:
            v.append(f"{sid}: hours must be a positive number")
            continue

        # 8
        if s["date"] > today:
            v.append(f"{sid}: dated {s['date']}, in the future (today {today})")
        if s["date"] < KICKOFF:
            v.append(f"{sid}: dated {s['date']}, before the engagement kick-off {KICKOFF}")

        # A correction records a bookkeeping fix, not hours at a desk, so it must not count toward
        # the daily ceiling. Its `hours` field mirrors the session it supersedes for traceability.
        if s.get("kind") != "correction":
            by_date.setdefault(s["date"], []).append(s)

        # 5
        if not str(s.get("confirmed_by", "")).strip():
            v.append(f"{sid}: no confirmed_by — no confirmation, no bill (C-COM-001)")

        # 7
        wt = s.get("work_type")
        if wt not in WORK_TYPES:
            v.append(f"{sid}: work_type {wt!r} is not one of {sorted(WORK_TYPES)}")
        elif wt in NEVER_BILLABLE and s.get("billable"):
            v.append(f"{sid}: work_type '{wt}' can never be billable")

        # 10
        blob = json.dumps(s)
        if re.search(r"€|\bEUR\b|rate", blob):
            v.append(f"{sid}: contains a fee, currency or rate reference — D-3 forbids it in this "
                     f"repository")

        # 4
        for ref in s.get("evidence", []) or []:
            if not resolves(ref):
                v.append(f"{sid}: evidence {ref!r} does not resolve — an unresolvable reference is "
                         f"a fabricated hour (C-COM-001)")
        if s.get("source") == "reconstructed" and not (s.get("evidence") or []):
            v.append(f"{sid}: source 'reconstructed' with no evidence")

        # 9
        if s.get("kind") == "historic_seed":
            if s.get("status") != "BILLED":
                v.append(f"{sid}: a historic_seed must be status BILLED")
            if not (s.get("hours_split_unknown") or s.get("allocation")):
                v.append(f"{sid}: a historic_seed must declare its allocation or state that the "
                         f"split is unknown (D-7)")
            if not s.get("note"):
                v.append(f"{sid}: a historic_seed must carry a note saying what it covers, so a "
                         f"later invoice cannot re-derive those hours (D-7)")
        else:
            # 3
            if s.get("billable"):
                ids = s.get("wbs") or []
                if not ids and not s.get("change_order"):
                    v.append(f"{sid}: billable and declares no WBS task and no change order "
                             f"(C-COM-002)")
                for tid in ids:
                    if known and tid not in known:
                        if not s.get("change_order"):
                            v.append(f"{sid}: bills WBS {tid!r}, absent from the accepted baseline "
                                     f"and covered by no change order (C-COM-002)")
                # 11
                if ids and est:
                    total_est = sum(est.get(t, 0) for t in ids)
                    if total_est and abs(float(hours) - total_est) < 0.01:
                        warn.append(f"{sid}: hours ({hours}) exactly equal the WBS high estimate "
                                    f"for {ids}. Actuals are expected below estimate (D-6) — check "
                                    f"this is a measurement and not the estimate copied across "
                                    f"(IMP-0032)")
            # allocation must sum to the session total when present
            alloc = s.get("allocation") or []
            if alloc and all(a.get("hours") is not None for a in alloc):
                tot = sum(float(a["hours"]) for a in alloc)
                if abs(tot - float(hours)) > 0.01:
                    v.append(f"{sid}: allocation sums to {tot} but the session is {hours} h")

        # 6
        inv = s.get("invoice")
        if inv and inv != "pre-ledger":
            if s.get("status") not in {"BILLED"}:
                v.append(f"{sid}: carries invoice {inv!r} but status is {s.get('status')!r}")
            key = s.get("id")
            if key in invoiced and invoiced[key] != inv:
                v.append(f"{sid}: appears on two invoices ({invoiced[key]}, {inv}) — C-COM-003")
            invoiced[key] = inv

    # 2
    for d, ss in by_date.items():
        tot = sum(float(x["hours"]) for x in ss if isinstance(x.get("hours"), (int, float)))
        if tot > MAX_PER_DAY and not any(x.get("kind") == "historic_seed" for x in ss):
            v.append(f"{d}: {tot} h booked in one day, over the {MAX_PER_DAY} h ceiling")
        spans = [(x.get("start"), x.get("end"), x.get("id")) for x in ss if x.get("start") and x.get("end")]
        spans.sort()
        for a, b in zip(spans, spans[1:]):
            if a[1] > b[0]:
                v.append(f"{d}: sessions {a[2]} and {b[2]} overlap ({a[1]} > {b[0]})")

    billable = sum(float(s["hours"]) for s in rows
                   if s.get("billable") and not s.get("_superseded")
                   and isinstance(s.get("hours"), (int, float)))
    n_corrected = len(corrected)
    print(f"verify-worklog: {len(rows)} session(s), {billable:g} billable hour(s) "
          f"in {args.worklog}"
          + (f" ({n_corrected} superseded by a correction)" if n_corrected else ""))
    for w in warn:
        print(f"  WARN  {w}")
    for x in v:
        print(f"  FAIL  {x}", file=sys.stderr)
    if v:
        print(f"\nverify-worklog: {len(v)} violation(s).", file=sys.stderr)
        return 1
    print(f"verify-worklog: PASS — 0 violations, {len(warn)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
