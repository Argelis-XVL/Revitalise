#!/usr/bin/env python3
"""Every append-only ledger the workflow roster declares is READ by something, and the
commercial ledger holds at least as many entries as the acts that should have written them.

WHY THIS IS A ROSTER GATE AND NOT A COMMERCIAL-EVENTS GATE
----------------------------------------------------------
`IMP-0312`. `agents/WORKFLOW.md`'s logging roster declares `logs/commercial-events.jsonl` as
the append-only record every authorised commercial act must produce, written by the three PM
agents. It was **0 bytes** when a dispatch found it on 2026-08-25, five days and three
authorised acts after the first one — a baseline lock and two approved change orders, each of
which has a line in `logs/pm.log` saying it happened.

Every individual gate passed the whole time, and the reason is the interesting part: the
obligation was DECLARATIVE ONLY. `pm-agent.md`'s BASELINE INTAKE mode and
`how-to-run-a-phase-acceptance.md` §7 both say "append a line" in prose;
`commercial-agent.md`'s gate template has no line item for it at all (contrast
`worklog.jsonl`, which is load-bearing in that gate block via `BILLABLE FOR APPROVAL`). And
**no script in `scripts/` referenced the file** — confirmed by grep, 0 readers.

`declared-policy-not-mechanically-enforced` is the largest class in the digest. So this gate is
deliberately built over the ROSTER, not over one ledger:

    check 1 — every append-only ledger the roster declares has at least one reader in scripts/
    check 2 — the commercial ledger's entry count is not less than the count of authorising
              lines in logs/pm.log

Check 1 is the generalisation. A gate written for `commercial-events.jsonl` alone would be an
instance patch on the largest class in the digest, and the NEXT declared ledger would repeat
this exactly — which is `IMP-0232`'s lesson one level up: that fix generalised the rule and
hand-wrote the list, and the list is what went stale. Here the list comes from the roster.

WHAT IT DOES NOT AND CANNOT CHECK, stated because a count is a weak assertion: it compares
COUNTS. It cannot tell whether a ledger entry is TRUE, whether it describes the act beside it,
or whether the right agent wrote it — only that authorised acts do not outnumber the records
they were supposed to produce. A ledger with the right number of wrong entries passes.

Usage
-----
    python3 scripts/verify-commercial-events.py
    python3 scripts/verify-commercial-events.py --workflow PATH --scripts-dir DIR --logs-dir DIR
    python3 scripts/verify-commercial-events.py --selftest

Exits 0 clean · 1 on any violation · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# A roster row: | `logs/x.jsonl` | owner | format |. Append-only is stated in the FORMAT cell,
# which is where WORKFLOW.md actually puts it.
ROSTER_ROW = re.compile(r"^\|\s*`(?P<path>logs/[^`]+)`\s*\|(?P<owner>[^|]*)\|(?P<fmt>[^|]*)\|")
APPEND_ONLY = re.compile(r"append-only", re.IGNORECASE)
GENERATED = re.compile(r"\bgenerated\b", re.IGNORECASE)

COMMERCIAL_LEDGER = "logs/commercial-events.jsonl"

# The acts that MUST produce a commercial-events line, read off logs/pm.log's own vocabulary.
# `[CHANGE-ORDER] — <id> APPROVED` is the approval; a `determination` or `drafted` line on the
# same tag is NOT an authorised act and must not be counted, or the gate demands entries for
# work that was only considered.
AUTHORISING = (
    re.compile(r"\bAPPROVE\s+BASELINE\b"),
    re.compile(r"\[CHANGE-ORDER\][^\n]*?\b[A-Z]{2}-\d+[A-Za-z0-9-]*\s+APPROVED\b"),
    re.compile(r"\bCLIENT\s+ACCEPTED\b"),
    re.compile(r"\bISSUE\s+INVOICE\b"),
)


def roster_ledgers(workflow: Path) -> tuple[list[str], str]:
    """Append-only ledger paths the roster declares. ([], reason) when it cannot be read."""
    if not workflow.is_file():
        return [], f"{workflow} does not exist"
    found: list[str] = []
    for line in workflow.read_text(encoding="utf-8").splitlines():
        row = ROSTER_ROW.match(line.strip())
        if not row:
            continue
        cells = row.group("owner") + row.group("fmt")
        # A generated file has no author to hold to an append-only obligation.
        if APPEND_ONLY.search(cells) and not GENERATED.search(cells):
            found.append(row.group("path"))
    if not found:
        return [], (f"parsed no append-only ledger rows from {workflow}'s logging roster. This "
                    f"gate reads that table; a parser that has stopped matching finds nothing, "
                    f"and finding nothing is a FAILURE here, never an OK (IMP-0007)")
    return found, ""


def readers_of(ledger: str, scripts_dir: Path) -> list[str]:
    """Scripts that name this ledger. A reader is any script mentioning the path or basename."""
    stem = Path(ledger).name
    hits: list[str] = []
    for script in sorted(scripts_dir.rglob("*")):
        if not script.is_file() or script.suffix not in {".py", ".sh", ".ps1"}:
            continue
        try:
            text = script.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if ledger in text or stem in text:
            hits.append(str(script))
    return hits


def authorising_lines(pm_log: Path) -> list[str]:
    if not pm_log.is_file():
        return []
    out: list[str] = []
    for line in pm_log.read_text(encoding="utf-8", errors="replace").splitlines():
        if any(p.search(line) for p in AUTHORISING):
            out.append(line.strip())
    return out


def ledger_entries(path: Path) -> tuple[int, list[str]]:
    """(count, malformed lines). A ledger that does not parse is not a ledger."""
    if not path.is_file():
        return 0, []
    count = 0
    bad: list[str] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
            count += 1
        except json.JSONDecodeError as exc:
            bad.append(f"line {n}: {exc}")
    return count, bad


def check(workflow: Path, scripts_dir: Path, logs_dir: Path) -> tuple[int, list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []

    ledgers, why = roster_ledgers(workflow)
    if why:
        return 1, [f"  CANNOT READ THE ROSTER  - {why}"], notes

    # ── check 1: every declared append-only ledger has a reader ──
    for ledger in ledgers:
        hits = readers_of(ledger, scripts_dir)
        if hits:
            notes.append(f"  {ledger}: {len(hits)} reader(s) in {scripts_dir}")
            continue
        errors.append(
            f"  LEDGER WITH NO READER  - {ledger} is declared append-only in "
            f"{workflow}'s logging roster and NO script in {scripts_dir} references it. A "
            f"ledger nothing reads can stay empty indefinitely with every individual gate "
            f"still passing — which is exactly what happened to {COMMERCIAL_LEDGER} for five "
            f"days and three authorised acts (IMP-0312). Add a check that reads it, or take "
            f"the row out of the roster."
        )

    # ── check 2: authorised acts do not outnumber the records they should have produced ──
    pm_log = logs_dir / "pm.log"
    ledger_path = logs_dir / Path(COMMERCIAL_LEDGER).name
    acts = authorising_lines(pm_log)
    count, malformed = ledger_entries(ledger_path)
    for bad in malformed:
        errors.append(f"  LEDGER LINE DOES NOT PARSE - {ledger_path} {bad}")
    if acts and count < len(acts):
        errors.append(
            f"  MISSING LEDGER ENTRIES - {len(acts)} authorising act(s) in {pm_log} against "
            f"{count} entry(ies) in {ledger_path}. Every authorised commercial act (APPROVE "
            f"BASELINE, a change order APPROVED, CLIENT ACCEPTED, ISSUE INVOICE) must produce "
            f"one line in the same session that authorises it. Acts on record:\n"
            + "\n".join(f"      {a[:120]}" for a in acts)
        )
    notes.append(f"  {len(acts)} authorising act(s) in {pm_log.name}, {count} ledger entry(ies)")
    return (1 if errors else 0), errors, notes


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_ROSTER = """## Logging

| Log | Owner | Format |
|---|---|---|
| `logs/routing.log` | lead-agent | one line per action |
| `logs/worklog.jsonl` | **commercial-agent only** | one object per session, append-only |
| `logs/commercial-events.jsonl` | the three PM agents | one object per act, append-only |
| `logs/state/*` | **generated** — a script, append-only | never hand-edited |
"""

_ACT = ("[2026-08-24 16:20] [COMMERCIAL] [f] [CHANGE-ORDER] — CO-001 APPROVED (reviewer)\n")
_NON_ACT = ("[2026-08-24 16:05] [COMMERCIAL] [f] [CHANGE-ORDER] — determination: considered\n"
            "[2026-08-25 15:35] [COMMERCIAL] [f] [CHANGE-ORDER] — drafted CO-001-A2\n")
_ENTRY = '{"id": "CE-0001", "type": "change-order", "action": "APPROVED"}\n'


def selftest() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        def case(name: str, *, roster: str, reader_for: list[str], pm: str, ledger: str,
                 expect_fail: bool, want: str = "", must_not: str = "") -> None:
            root = Path(tmp) / name
            (root / "agents").mkdir(parents=True, exist_ok=True)
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            (root / "logs").mkdir(parents=True, exist_ok=True)
            (root / "agents" / "WORKFLOW.md").write_text(roster, encoding="utf-8")
            for i, ledger_path in enumerate(reader_for):
                (root / "scripts" / f"reads{i}.py").write_text(
                    f'LEDGER = "{ledger_path}"\n', encoding="utf-8")
            (root / "logs" / "pm.log").write_text(pm, encoding="utf-8")
            (root / "logs" / "commercial-events.jsonl").write_text(ledger, encoding="utf-8")

            rc, errors, notes = check(root / "agents" / "WORKFLOW.md",
                                      root / "scripts", root / "logs")
            text = "\n".join(errors + notes)
            ok = (((rc != 0) if expect_fail else (rc == 0))
                  and (not want or want in text)
                  and (not must_not or must_not not in text))
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors + notes:
                    print(f"                   {line}")
            cases.append((name, ok))

        both = ["logs/worklog.jsonl", "logs/commercial-events.jsonl"]

        # check 1
        case("a-declared-ledger-with-no-reader-fails",
             roster=_ROSTER, reader_for=["logs/worklog.jsonl"], pm="", ledger="",
             expect_fail=True, want="LEDGER WITH NO READER")
        # A GENERATED file says "append-only" in the same cell and has no author to hold to the
        # obligation, so it must be excluded from check 1 — the roster's `logs/state/*` row.
        # rc 0 alone would not prove the exclusion, so the assertion is on its ABSENCE.
        case("a-generated-append-only-file-is-not-held-to-the-rule",
             roster=_ROSTER, reader_for=both, pm="", ledger="",
             expect_fail=False, want="logs/commercial-events.jsonl: 1 reader(s)",
             must_not="logs/state")
        case("an-unparseable-roster-fails-rather-than-passing-over-nothing",
             roster="# no table here\n", reader_for=both, pm="", ledger="",
             expect_fail=True, want="parsed no append-only ledger rows")
        case("a-missing-workflow-file-fails",
             roster="", reader_for=both, pm="", ledger="", expect_fail=True,
             want="parsed no append-only ledger rows")
        # check 2
        case("an-authorised-act-with-no-ledger-entry-fails",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger="",
             expect_fail=True, want="MISSING LEDGER ENTRIES")
        case("an-authorised-act-WITH-its-entry-passes",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger=_ENTRY,
             expect_fail=False, want="1 authorising act(s)"),
        # The over-firing control, and the reason the pattern is not a bare [CHANGE-ORDER]:
        # a determination and a draft are not authorised acts and must demand nothing.
        case("a-determination-and-a-draft-are-NOT-acts-and-demand-no-entry",
             roster=_ROSTER, reader_for=both, pm=_NON_ACT, ledger="",
             expect_fail=False, want="0 authorising act(s)")
        case("a-malformed-ledger-line-fails",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger="{not json\n" + _ENTRY,
             expect_fail=True, want="DOES NOT PARSE")

    failed = [n for n, ok in cases if not ok]
    if failed:
        print(f"\nverify-commercial-events: SELFTEST FAILED — {', '.join(failed)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-commercial-events: SELFTEST OK — {len(cases)} fixtures, both checks "
          f"proven able to fail and to pass, plus one over-firing control.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--workflow", type=Path, default=Path("agents/WORKFLOW.md"))
    p.add_argument("--scripts-dir", type=Path, default=Path("scripts"))
    p.add_argument("--logs-dir", type=Path, default=Path("logs"))
    p.add_argument("--warn-only", action="store_true",
                   help="report and exit 0. This is what makes the build step SOFT: a "
                        "commercial gate never halts a build (CLAUDE.md, Commercial Rules)")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()

    rc, errors, notes = check(args.workflow, args.scripts_dir, args.logs_dir)
    if rc:
        label = "WARN" if args.warn_only else "FAILED"
        print(f"commercial-events: {label}\n" + "\n".join(errors + notes), file=sys.stderr)
        return 0 if args.warn_only else rc
    print("commercial-events: OK\n" + "\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
