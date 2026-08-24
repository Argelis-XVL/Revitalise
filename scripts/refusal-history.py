#!/usr/bin/env python3
"""Render the harness-refusal evidence matrix from logs/improvement-log.jsonl.

WHY THIS EXISTS (IMP-0252). `agents/pipeline-agent.md` carried a hand-typed table of what the
instances of `harness-blocks-destructive-call` showed, so that the next occurrence would be
diagnostic rather than another anecdote. The table worked -- and then went stale the moment the
class recurred: it described *seven* instances while the log held eight, in the one section an
agent reads while a deploy is already going wrong. A table about a recurring class needs retyping
on every recurrence of that class, which is the least reliable moment to expect it.

So the table is retired and this script replaces it. The log is the source; this only formats it.

Two modes beyond the default listing:

  --check     Fails when an agent file has grown a hand-maintained table of these instances
              again. It looks for the retired artefact's SHAPE -- a markdown table whose header
              names instances/occurrences and whose rows carry IMP- ids -- not for prose. A
              sentence recounting the history ("it described seven instances while the log held
              eight") is legitimate and must keep passing; a table that has to be retyped is not.

  --selftest  Synthetic fixtures for both the matrix and the --check shape detector.

No network, no credentials, no writes. Repository-internal, per agents/improvement-agent.md
("Your own executables belong in scripts/").
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOG = REPO / "logs" / "improvement-log.jsonl"
AGENT_DIR = REPO / "agents"

# The class this script reports on, and the neighbouring class that records the SUCCESSES.
# Both matter: a refusal history with no successes in it reads as "this never works", and the
# 2026-08-23 pair (ensure-auditing.ps1 succeeded, provisioning-common reads refused, same day,
# same credential route) is the single most decision-relevant fact in the set.
REFUSAL_CLASS = "harness-blocks-destructive-call"
SUCCESS_CLASSES = ("foreground-write-not-refused",)

UNRECORDED = "unrecorded"

# --check: the retired table's shape. A header row naming instances/occurrences, in a file that
# also talks about refusals, with IMP- ids in the body.
TABLE_HEADER = re.compile(r"^\s*\|.*\b(instances?|occurrences?)\b.*\|", re.IGNORECASE)
IMP_ID = re.compile(r"\bIMP-\d{4}\b")


def load_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def context_of(row: dict) -> tuple[str, str, str]:
    """(harness_mode, dispatch, layer) -- all three honestly 'unrecorded' when absent.

    refusal_context became mandatory for this class on 2026-08-23 (improvement review 4,
    scripts/verify-improvement-log.py). Entries before that carry nothing, and printing
    'unrecorded' for them is the point: it is what shows that the first seven instances could
    not settle what decides a refusal.
    """
    ctx = row.get("refusal_context")
    if not isinstance(ctx, dict):
        return (UNRECORDED, UNRECORDED, UNRECORDED)
    return (
        str(ctx.get("harness_mode") or UNRECORDED),
        str(ctx.get("dispatch") or UNRECORDED),
        str(ctx.get("layer") or UNRECORDED),
    )


def build_matrix(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    refusals, successes = [], []
    for row in rows:
        cls = row.get("class_instance_of")
        if cls == REFUSAL_CLASS:
            mode, dispatch, layer = context_of(row)
            refusals.append({
                "id": row.get("id", "?"),
                "ts": str(row.get("ts") or "")[:16],
                "harness_mode": mode,
                "dispatch": dispatch,
                "layer": layer,
                "status": row.get("status", "?"),
            })
        elif cls in SUCCESS_CLASSES:
            mode, dispatch, _ = context_of(row)
            successes.append({
                "id": row.get("id", "?"),
                "ts": str(row.get("ts") or "")[:16],
                "harness_mode": mode,
                "dispatch": dispatch,
            })
    return refusals, successes


def render(refusals: list[dict], successes: list[dict]) -> str:
    out: list[str] = []
    out.append(f"REFUSAL HISTORY — class '{REFUSAL_CLASS}', derived from "
               f"logs/improvement-log.jsonl")
    out.append("")
    if not refusals:
        out.append("  (no instances recorded)")
    else:
        out.append(f"  {'id':<10} {'when':<17} {'harness_mode':<13} {'dispatch':<16} "
                   f"{'layer refused':<14} status")
        out.append(f"  {'-' * 10} {'-' * 17} {'-' * 13} {'-' * 16} {'-' * 14} ------")
        for r in refusals:
            out.append(f"  {r['id']:<10} {r['ts']:<17} {r['harness_mode']:<13} "
                       f"{r['dispatch']:<16} {r['layer']:<14} {r['status']}")
    out.append("")
    out.append(f"  {len(refusals)} refusal(s) recorded.")

    by_mode: dict[str, int] = {}
    for r in refusals:
        by_mode[r["harness_mode"]] = by_mode.get(r["harness_mode"], 0) + 1
    if by_mode:
        summary = ", ".join(f"{k}: {v}" for k, v in sorted(by_mode.items()))
        out.append(f"  By harness_mode — {summary}")

    if successes:
        out.append("")
        out.append("  Recorded SUCCESSES for the same operation class (read these before "
                   "concluding it never works):")
        for s in successes:
            out.append(f"    {s['id']:<10} {s['ts']:<17} harness_mode={s['harness_mode']}, "
                       f"dispatch={s['dispatch']}")

    out.append("")
    out.append("  Reminder: a refusal is a CONTROL, not an obstacle. The legitimate responses are")
    out.append("  additive — prove access with the read-only preflight, perform the write in the")
    out.append("  session scoped for it, or hand the exact command to the reviewer with the query")
    out.append("  that proves the outcome. Never reduce what the harness is told (IMP-0264).")
    return "\n".join(out)


def find_handmaintained_tables(agent_dir: Path) -> list[str]:
    """Locate a re-grown hand-maintained instance table. Shape, not prose."""
    problems: list[str] = []
    for path in sorted(agent_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if "refus" not in text.lower():
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if not TABLE_HEADER.match(line):
                continue
            # Look at the rows following the header (header, separator, then body).
            body = lines[i + 1:i + 8]
            ids = [m for row in body for m in IMP_ID.findall(row)]
            if len(ids) >= 3:
                # Tolerate a path outside the repo: --selftest runs this over a temp directory.
                try:
                    rel: Path | str = path.relative_to(REPO)
                except ValueError:
                    rel = path.name
                problems.append(
                    f"{rel}:{i + 1}: a hand-maintained table of refusal instances has "
                    f"re-grown here ({len(ids)} IMP ids in its rows). This is the artefact "
                    f"retired on 2026-08-24 for going stale at seven-versus-eight "
                    f"(IMP-0252). Point at `python3 scripts/refusal-history.py` instead.")
    return problems


def selftest() -> int:
    failures: list[str] = []

    # Fixture 1: the matrix reproduces every row the retired table asserted, plus the entry
    # that made it stale, and reports 'unrecorded' rather than guessing.
    rows = [
        {"id": "IMP-0021", "ts": "2026-08-16T21:09",
         "class_instance_of": REFUSAL_CLASS, "status": "APPLIED"},
        {"id": "IMP-0173", "ts": "2026-08-21T22:45",
         "class_instance_of": "foreground-write-not-refused", "status": "APPLIED"},
        {"id": "IMP-0245", "ts": "2026-08-23T18:30", "class_instance_of": REFUSAL_CLASS,
         "status": "APPLIED",
         "refusal_context": {"harness_mode": "auto", "dispatch": "background"}},
        {"id": "IMP-0252", "ts": "2026-08-24T08:05", "class_instance_of": REFUSAL_CLASS,
         "status": "NEW",
         "refusal_context": {"harness_mode": "auto", "dispatch": "lead-foreground",
                             "layer": "dispatch"}},
    ]
    refusals, successes = build_matrix(rows)
    if len(refusals) != 3:
        failures.append(f"expected 3 refusals, got {len(refusals)}")
    if len(successes) != 1:
        failures.append(f"expected 1 success, got {len(successes)}")
    if refusals[0]["harness_mode"] != UNRECORDED:
        failures.append("a pre-2026-08-23 entry must report harness_mode 'unrecorded', "
                        f"got {refusals[0]['harness_mode']!r}")
    if refusals[2]["layer"] != "dispatch":
        failures.append("IMP-0252's layer must render as 'dispatch'")
    text = render(refusals, successes)
    for needle in ("IMP-0252", "dispatch", "auto: 2", "IMP-0173"):
        if needle not in text:
            failures.append(f"rendered matrix is missing {needle!r}")

    # Fixture 2: --check catches the retired table's shape and spares legitimate prose.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "bad-agent.md").write_text(
            "# Bad\nRefusals happen.\n\n"
            "| What the seven instances actually show | |\n"
            "|---|---|\n"
            "| `IMP-0021`, `IMP-0040` | handed the reviewer a command |\n"
            "| `IMP-0173` | one success |\n"
            "| `IMP-0245` | refused under Auto Mode |\n",
            encoding="utf-8")
        (d / "good-agent.md").write_text(
            "# Good\nA refusal is a control. Read the history with "
            "`python3 scripts/refusal-history.py`.\n\n"
            "The table that stood here until 2026-08-24 described seven instances while the "
            "log held eight (IMP-0252), which is why it is gone.\n",
            encoding="utf-8")
        problems = find_handmaintained_tables(d)
        if len(problems) != 1:
            failures.append(f"--check expected exactly 1 problem, got {len(problems)}: "
                            f"{problems}")
        elif "bad-agent.md" not in problems[0]:
            failures.append(f"--check flagged the wrong file: {problems[0]}")

    if failures:
        print("refusal-history --selftest: FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("refusal-history --selftest: PASS — 2 fixtures "
          "(matrix incl. 'unrecorded' handling; table-shape detector vs. legitimate prose)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="fail if an agent file has re-grown a hand-maintained instance table")
    ap.add_argument("--selftest", action="store_true", help="run built-in fixtures")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not LOG.exists():
        print(f"refusal-history: {LOG} not found", file=sys.stderr)
        return 2

    if args.check:
        problems = find_handmaintained_tables(AGENT_DIR)
        if problems:
            print("refusal-history --check: FAILED")
            for p in problems:
                print(f"  {p}")
            return 1
        print("refusal-history --check: PASS — no hand-maintained refusal-instance table in "
              "agents/")
        return 0

    refusals, successes = build_matrix(load_rows(LOG))
    print(render(refusals, successes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
