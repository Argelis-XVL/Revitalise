#!/usr/bin/env python3
"""Gate: verify the chain from contracted task to delivered artefact, in BOTH directions.

WHY BOTH DIRECTIONS
-------------------
PM-R24/PM-R25. A one-directional check finds only the gap you already suspected.

  task -> artefact   a task claims completion and its deliverable is absent
                     = UNEVIDENCED CLAIM. `IMP-0030`: WBS 0.4 marked Done with five of eight
                       named tables missing. **HARD — fails this gate.**

  artefact -> task   an artefact exists that no contracted task accounts for
                     = UNQUOTED WORK. Either the Client asked for something outside the accepted
                       specification (a change order) or it was built without being asked for.
                       **Reported; HARD only with --strict, or when a billable hour is attached.**

`IMP-0013` is why the artefact list is derived and never hand-written: the hand-written
verification list for the first DEV deploy named four component types correctly and omitted the
two that had silently not been created. A hand-written list encodes what you already suspected.

Run:
    python3 scripts/verify-wbs-chain.py
    python3 scripts/verify-wbs-chain.py --strict          # unquoted artefacts also fail
    python3 scripts/verify-wbs-chain.py --state <p> --map <p> --worklog <p>   # fixtures

Exit 0 clean, 1 on a violation, 2 on usage or a missing input. Fails — never passes — when an
input is missing (IMP-0007).
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import worklog as WL  # noqa: E402  — the SINGLE definition of what the ledger means (IMP-0093)

DEF_STATE = Path("logs/state/wbs-state.json")
DEF_MAP = Path("contract/evidence-map.json")
DEF_WORKLOG = Path("logs/worklog.jsonl")
DEF_CHANGE_ORDERS = Path("contract/change-orders")
DEF_EXCEPTIONS = Path("contract/known-exceptions.json")
SOLUTION_GLOB = "src/solutions/*"


def derived_artefacts() -> dict[str, list[str]]:
    """Enumerate the solution's real components. Derived, never hand-written (IMP-0013)."""
    ents = sorted(Path(p).name for p in glob.glob(f"{SOLUTION_GLOB}/Entities/*") if Path(p).is_dir())
    wfs = sorted({Path(p).name.split("-")[0]
                  for p in glob.glob(f"{SOLUTION_GLOB}/Workflows/*.json")})
    apps = sorted(Path(p).name for p in glob.glob(f"{SOLUTION_GLOB}/AppModules/*") if Path(p).is_dir())
    return {"entity": ents, "workflow": wfs, "appmodule": apps}


# Directories whose contents the derived state is a function of. If anything here is newer
# than the state file, the state file describes a repository that no longer exists.
STATE_INPUT_GLOBS = ("contract/**/*", "src/solutions/**/*")


def _newer_than_state(state_path: Path) -> tuple[str, int] | None:
    """The newest input file that postdates the state file, and how many do.

    Returns None when the state file is at least as new as every input, which is the only
    condition under which reading it is a result rather than a guess.
    """
    try:
        state_mtime = state_path.stat().st_mtime
    except OSError:
        return None

    newer: list[tuple[float, str]] = []
    for pattern in STATE_INPUT_GLOBS:
        for path in Path().glob(pattern):
            if not path.is_file():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime > state_mtime:
                newer.append((mtime, path.as_posix()))

    if not newer:
        return None
    newer.sort(reverse=True)
    return newer[0][1], len(newer)


def rule_mentions(rules: dict) -> str:
    """One blob of every rule's text, so an artefact can be tested for being accounted for."""
    return json.dumps(rules)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", type=Path, default=DEF_STATE)
    ap.add_argument("--map", dest="map_", type=Path, default=DEF_MAP)
    ap.add_argument("--worklog", type=Path, default=DEF_WORKLOG)
    ap.add_argument("--change-orders", type=Path, default=DEF_CHANGE_ORDERS)
    ap.add_argument("--strict", action="store_true",
                    help="unquoted artefacts fail the gate as well")
    ap.add_argument("--exceptions", type=Path, default=DEF_EXCEPTIONS)
    ap.add_argument("--today", default=None, help="YYYY-MM-DD, for testing expiry")
    args = ap.parse_args(argv)

    for p in (args.state, args.map_):
        if not p.exists():
            print(f"verify-wbs-chain: missing {p}. Run scripts/import-baseline.py and "
                  f"scripts/derive-wbs-state.py first.", file=sys.stderr)
            return 2

    # ── the state file must not be STALER than what it describes ──────────────────────
    # IMP-0180 / IMP-0089, improvement review 8 item 6. This gate reads a GENERATED cache it
    # does not generate, and only ever complained when the file was MISSING. A file that is
    # present and stale is the worse case and was handled as success: on 2026-08-21 this gate
    # reported a table ABSENT that had been on disk for a day.
    #
    # IMP-0089 established the principle — "a preflight result that depends on files left
    # behind by a previous run is not a result" — and fixed the one instance it found. This is
    # the second instance of that exact shape in a different pair of scripts, so per
    # skills/how-to-promote-a-finding.md the fix is the property, not the instance: refuse to
    # run when the cache predates its own inputs, and name the command that rebuilds it.
    stale_against = _newer_than_state(args.state)
    if stale_against:
        newest, count = stale_against
        print(f"verify-wbs-chain: {args.state} is STALE — {count} file(s) under contract/ or "
              f"src/solutions/ are newer than it, the newest being {newest}. Every task state "
              f"below would be derived from a snapshot that predates the work it describes, "
              f"which is how this gate once reported a table absent that had been on disk for "
              f"a day (IMP-0180). Refusing to report over a stale cache (IMP-0089).\n"
              f"    Rebuild it:  python3 scripts/derive-wbs-state.py\n"
              f"    Then re-run: python3 scripts/verify-wbs-chain.py",
              file=sys.stderr)
        return 2

    state = json.loads(args.state.read_text(encoding="utf-8"))
    rules = json.loads(args.map_.read_text(encoding="utf-8"))["rules"]
    if not state.get("tasks"):
        print(f"verify-wbs-chain: {args.state} contains no tasks — refusing to report OK over "
              f"nothing (IMP-0007).", file=sys.stderr)
        return 2

    # ── accepted exceptions: enumerated, owned, dated. Never a silent waiver ──
    import datetime as _dt
    today = args.today or _dt.date.today().isoformat()
    exceptions, exc_errors = [], []
    if args.exceptions.exists():
        try:
            exceptions = json.loads(args.exceptions.read_text(encoding="utf-8"))["exceptions"]
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"verify-wbs-chain: {args.exceptions} is unreadable: {exc}", file=sys.stderr)
            return 2
        for e in exceptions:
            missing = [f for f in ("id", "matches", "reason", "owner", "clears_when", "expires")
                       if not e.get(f)]
            if missing:
                exc_errors.append(f"EXCEPTION {e.get('id', '(no id)')} is missing "
                                  f"{', '.join(missing)} — an unowned or undated exception is a "
                                  f"silent waiver and fails this gate")
            elif e["expires"] < today:
                exc_errors.append(f"EXCEPTION {e['id']} EXPIRED on {e['expires']} (today {today}) "
                                  f"— owner {e['owner']}; clears when: {e['clears_when']}")

    def excused(msg: str):
        for e in exceptions:
            if e.get("matches") and e["matches"] in msg and e.get("expires", "") >= today \
                    and not [f for f in ("id", "reason", "owner", "clears_when") if not e.get(f)]:
                return e
        return None

    violations: list[str] = list(exc_errors)
    warnings: list[str] = []

    # ── direction 1: task -> artefact (HARD) ──────────────────────────────────
    overclaims = [t for t in state["tasks"] if t["verdict"] == "OVERCLAIM"]
    for t in overclaims:
        missing = [e["note"] for e in t["evidence"] if e["ok"] is False]
        msg = (f"UNEVIDENCED CLAIM — task {t['id']} ({t['task']}) is claimed "
               f"'{t['claimed_status']}' but derives '{t['derived_status']}'. Absent: "
               + "; ".join(missing))
        ex = excused(msg)
        if ex:
            warnings.append(f"{msg}  [ACCEPTED {ex['id']} until {ex['expires']}, "
                            f"owner {ex['owner']}]")
        else:
            violations.append(msg)

    unverifiable = [t for t in state["tasks"] if t["verdict"] == "unverifiable"]
    for t in unverifiable:
        warnings.append(f"UNVERIFIABLE CLAIM — task {t['id']} is claimed "
                        f"'{t['claimed_status']}' and has no checkable evidence rule")

    for t in state["tasks"]:
        if t["verdict"] == "UNDERCLAIM":
            warnings.append(f"UNDERCLAIM — task {t['id']} ({t['task']}) derives "
                            f"'{t['derived_status']}' against a blank Status")

    # ── direction 2: artefact -> task (report; HARD with --strict) ────────────
    blob = rule_mentions(rules)
    unaccounted: list[str] = []
    for kind, names in derived_artefacts().items():
        for n in names:
            if n not in blob:
                unaccounted.append(f"{kind} {n}")
    for u in unaccounted:
        msg = (f"UNQUOTED WORK — {u} exists in the solution and no contracted task accounts for "
               f"it. Either raise a change order or add its evidence rule.")
        ex = excused(msg)
        if ex:
            warnings.append(f"{msg}  [ACCEPTED {ex['id']} until {ex['expires']}, "
                            f"owner {ex['owner']}]")
        else:
            (violations if args.strict else warnings).append(msg)

    # ── direction 2b: a billable hour against a task outside the baseline (HARD) ──
    known_ids = {t["id"] for t in state["tasks"]}
    covered = set()
    if args.change_orders.exists():
        for co in args.change_orders.glob("CO-*.md"):
            for tok in co.read_text(encoding="utf-8").split():
                if tok.strip("`,;") and tok.strip("`,;")[0].isdigit():
                    covered.add(tok.strip("`,;"))
    invoiced_to_date = None
    if args.worklog.exists():
        # The superseded-session rule lives in scripts/lib/worklog.py and NOWHERE ELSE.
        # This gate re-implemented it by omission and reported 64 h + a corrected 20 h = 84 h,
        # while verify-worklog.py and compute-invoice.py both reported 64 (IMP-0093).
        ledger, ledger_errors = WL.load(args.worklog)
        violations.extend(ledger_errors)
        invoiced_to_date = WL.invoiced_to_date(ledger)
        for i, s in enumerate(ledger, 1):
            if s.get("_superseded"):
                warnings.append(
                    f"SUPERSEDED — session {s.get('id')} is corrected by a later entry and is "
                    f"excluded from every total. Kept in the ledger so the correction stays "
                    f"visible (C-COM-003).")
                continue
            if not s.get("billable", False):
                continue
            # A historic seed is hours invoiced BEFORE this ledger existed (D-7): 64 hours across
            # Phase 0 and the Phase 2 build, with the split not recorded by anyone. It legitimately
            # carries no task ids, and scripts/verify-worklog.py owns its invariants (status BILLED,
            # declared split or an explicit unknown, and a note so no later invoice re-derives it).
            if s.get("kind") == "historic_seed":
                warnings.append(
                    f"HISTORIC SEED — session {s.get('id')} carries {s.get('hours')} h invoiced "
                    f"before the ledger existed, allocated by phase with the split unrecorded "
                    f"(D-7). Never re-derive per-phase actuals for those phases.")
                continue
            ids = s.get("wbs") or []
            if not ids:
                violations.append(f"{args.worklog}:{i} session {s.get('id')} is billable and "
                                  f"declares no WBS task (C-COM-002)")
            for tid in ids:
                if tid not in known_ids and tid not in covered and s.get("scope") != "change_order":
                    violations.append(
                        f"{args.worklog}:{i} session {s.get('id')} bills WBS '{tid}', which is "
                        f"absent from the accepted baseline and covered by no change order "
                        f"(C-COM-002)")

    art = derived_artefacts()
    print(f"verify-wbs-chain: {len(state['tasks'])} contracted tasks · "
          f"{sum(len(v) for v in art.values())} solution artefacts "
          f"({', '.join(f'{k}={len(v)}' for k, v in art.items())})")
    if invoiced_to_date is not None:
        print(f"  invoiced to date: {invoiced_to_date:g} h — must equal compute-invoice.py's "
              f"'Already invoiced' figure; both read scripts/lib/worklog.py (IMP-0093)")
    for w in warnings:
        print(f"  WARN  {w}")
    for v in violations:
        print(f"  FAIL  {v}", file=sys.stderr)

    if violations:
        print(f"\nverify-wbs-chain: {len(violations)} violation(s), {len(warnings)} warning(s).",
              file=sys.stderr)
        return 1
    live = [e for e in exceptions if e.get("expires", "") >= today]
    print(f"verify-wbs-chain: PASS — 0 violations, {len(warnings)} warning(s), "
          f"{len(live)} accepted exception(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
