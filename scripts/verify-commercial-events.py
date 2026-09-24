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
    check 3 — every AUTHORISING ledger entry names the human who authorised it and the channel
              the keyword arrived through (C-COM-011, IMP-0787)

CHECK 3 FOUND 0 VIOLATIONS ON THE DAY IT WAS WIRED, AND THAT IS THE CORRECT NUMBER.
All six real entries already carried `authorised_by` and `relayed_by` — the convention was
followed 6 times out of 6 and read by NOTHING: grepped 2026-09-20, the token `relayed_by`
appeared in the ledger file and in no script anywhere. Proven by mutation rather than by
reading: stripping both fields from all six rows changed the gate's output not at all before
this check existed, and fails six times after it. So this is a regression guard on a convention,
not a fix for a live defect — say so rather than reporting a clean run (`IMP-0542`).

It is here because the convention is what makes a RELAYED gate keyword safe. Nothing in this
harness authenticates a human, so the record is the whole control: a named authoriser is what
lets the reviewer repudiate an authorisation they did not give, while the act is still
revertible. `IMP-0787` is what an unwritten version of that policy cost.

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
#
# The keyword must introduce the act, not merely appear on the line. Measured 2026-09-24 over
# logs/pm.log: the bare pattern matched 4 lines, 2 of them real acts (line 3, line 22) and 2 of
# them mentions -- line 21 "awaiting APPROVE BASELINE", and line 32 quoting the act it backfilled
# (IMP-0829, IMP-0864). This mirrors the CHANGE-ORDER pattern's own anchor on APPROVED.
AUTHORISING = (
    re.compile(r"\bAPPROVE\s+BASELINE\b\s*(?:\(|—)"),
    re.compile(r"\[CHANGE-ORDER\][^\n]*?\b[A-Z]{2}-\d+[A-Za-z0-9-]*\s+APPROVED\b"),
    re.compile(r"\bCLIENT\s+ACCEPTED\b"),
    re.compile(r"\bISSUE\s+INVOICE\b"),
)


# ── check 3's vocabulary (C-COM-011, IMP-0787) ────────────────────────────────────────────
#
# WHICH ROWS. The `action` values present in the real ledger on 2026-09-20 are APPROVED (x4),
# IMPORTED (x1) and CLOSED (x1). The first two are authorising acts and are checked; ISSUED and
# ACCEPTED are added because logs/pm.log's AUTHORISING vocabulary above names ISSUE INVOICE and
# CLIENT ACCEPTED, and a ledger row for either is an authorisation whether or not one exists yet.
# CLOSED is deliberately OUT: closing a change order authorises nothing.
#
# This set UNDER-fires rather than over-fires by construction — an action nobody has written yet
# is skipped, not failed. That is the safe direction for a fail-closed set (IMP-0560): a value
# the author did not think of becomes a missed check, never a false positive on day one.
AUTHORISING_ACTIONS = {"APPROVED", "IMPORTED", "ISSUED", "ACCEPTED"}

# `relayed_by` answers "how did the keyword reach the agent that acted". Two values, because the
# harness has two channels: through lead-agent, or in a turn the acting agent could see itself.
RELAY_CHANNELS = {"lead-agent", "direct"}

# A name that names nobody. `authorised_by: "reviewer"` is the specific shape this check exists
# to reject — logs/pm.log's own CO-001 line reads "(reviewer, via lead-agent)" with no person in
# it, and a record nobody can be held to is not a record (IMP-0787).
ANONYMOUS = {"", "unknown", "n/a", "na", "none", "reviewer", "the reviewer",
             "human", "the human", "user", "the user", "client", "the client"}


def provenance_errors(path: Path) -> list[str]:
    """C-COM-011: an authorising entry names the human and the channel, or it is not one."""
    if not path.is_file():
        return []
    out: list[str] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # already reported by ledger_entries; do not report it twice
        if not isinstance(entry, dict):
            continue
        action = str(entry.get("action", "")).strip().upper()
        if action not in AUTHORISING_ACTIONS:
            continue
        ident = entry.get("id", f"line {n}")
        who = entry.get("authorised_by")
        how = entry.get("relayed_by")
        if not isinstance(who, str) or who.strip().lower() in ANONYMOUS:
            out.append(
                f"  UNNAMED AUTHORISER - {ident} records action {action} with "
                f"authorised_by={who!r}. C-COM-011: an authorising act names the HUMAN who "
                f"authorised it. Nothing in this harness authenticates a human; the name is "
                f"what lets the reviewer repudiate an authorisation they did not give, while "
                f"the act is still revertible (IMP-0787)."
            )
        if how not in RELAY_CHANNELS:
            out.append(
                f"  UNRECORDED CHANNEL - {ident} records action {action} with "
                f"relayed_by={how!r}, which is not one of {sorted(RELAY_CHANNELS)}. "
                f"C-COM-011: record whether the keyword arrived through lead-agent or in a "
                f"turn this agent could see. agents/WORKFLOW.md -> 'What channel a keyword "
                f"must arrive through' (IMP-0787)."
            )
    return out


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
    # ── check 3: every authorising entry names its human and its channel (C-COM-011) ──
    prov = provenance_errors(ledger_path)
    errors.extend(prov)

    notes.append(f"  {len(acts)} authorising act(s) in {pm_log.name}, {count} ledger entry(ies)")
    notes.append(f"  authorisation provenance: {len(prov)} unnamed/unrecorded (C-COM-011)")
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
_ENTRY = ('{"id": "CE-0001", "type": "change-order", "action": "APPROVED", '
          '"authorised_by": "Anna Southern", "relayed_by": "lead-agent"}\n')
# The same act, recorded the way IMP-0787's own pm.log line reads it: "(reviewer, via
# lead-agent)" — a channel, and nobody to hold to it.
_ENTRY_ANON = ('{"id": "CE-0001", "type": "change-order", "action": "APPROVED", '
               '"authorised_by": "reviewer", "relayed_by": "lead-agent"}\n')
_ENTRY_NO_CHANNEL = ('{"id": "CE-0001", "type": "change-order", "action": "APPROVED", '
                     '"authorised_by": "Anna Southern"}\n')
# CLOSED authorises nothing, so it is checked by nothing — the under-firing edge, asserted so a
# later widening of AUTHORISING_ACTIONS has to change this fixture deliberately.
_ENTRY_CLOSED = '{"id": "CE-0002", "type": "change-order", "action": "CLOSED"}\n'

# The two APPROVE BASELINE MENTIONS measured in logs/pm.log on 2026-09-24 (lines 21 and 32):
# a line saying the act is still awaited, and a timesheet line quoting the act it backfilled.
# Neither authorises anything, and the bare keyword pattern counted both (IMP-0829, IMP-0864).
_BASELINE_MENTIONS = (
    "[2026-09-10 15:10] [PM] [system] [BASELINE] — WBS v0.6 intake verification: 61 tasks "
    "unchanged. No import performed — awaiting APPROVE BASELINE.\n"
    "[2026-09-20 14:00] [COMMERCIAL] [system] [TIMESHEET] — Backfilled the ledger: CE-0008 "
    "(2026-08-20 03:10 APPROVE BASELINE amendment, pm.log:3), each ts'd to its own moment.\n"
)
# And the two real acts from the same file (lines 3 and 22), in both spellings the anchor keeps.
_BASELINE_ACTS = (
    "[2026-08-20 03:10] [PM] [system] APPROVE BASELINE — estimating_rule amended.\n"
    "[2026-09-10 16:05] [PM] [system] [BASELINE] — APPROVE BASELINE (Xander Lykopoulos): "
    "imported WBS v0.6.\n"
)
_ENTRY_BASELINE_2 = ('{"id": "CE-0003", "type": "baseline", "action": "IMPORTED", '
                     '"authorised_by": "Xander Lykopoulos", "relayed_by": "direct"}\n'
                     '{"id": "CE-0008", "type": "baseline", "action": "IMPORTED", '
                     '"authorised_by": "Xander Lykopoulos", "relayed_by": "direct"}\n')


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
        # The two measured APPROVE BASELINE mentions (IMP-0829, IMP-0864). The keyword must
        # INTRODUCE the act — followed by "(" or an em dash — not merely appear on the line.
        case("an-APPROVE-BASELINE-mention-is-NOT-an-act",
             roster=_ROSTER, reader_for=both, pm=_BASELINE_MENTIONS, ledger="",
             expect_fail=False, want="0 authorising act(s)")
        # …and the anchor must not cost the real acts, in either spelling they are written in.
        case("both-real-APPROVE-BASELINE-spellings-are-still-acts",
             roster=_ROSTER, reader_for=both, pm=_BASELINE_ACTS, ledger=_ENTRY_BASELINE_2,
             expect_fail=False, want="2 authorising act(s)")
        case("a-malformed-ledger-line-fails",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger="{not json\n" + _ENTRY,
             expect_fail=True, want="DOES NOT PARSE")
        # check 3 (C-COM-011, IMP-0787)
        case("an-authorising-entry-naming-no-human-fails",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger=_ENTRY_ANON,
             expect_fail=True, want="UNNAMED AUTHORISER")
        case("an-authorising-entry-with-no-channel-fails",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger=_ENTRY_NO_CHANNEL,
             expect_fail=True, want="UNRECORDED CHANNEL")
        # The under-firing control: CLOSED is not an authorising act and must demand nothing,
        # so rc 0 alone would not prove it — the assertion is on the ABSENCE of a finding.
        case("a-CLOSED-entry-is-not-an-authorising-act-and-is-not-checked",
             roster=_ROSTER, reader_for=both, pm="", ledger=_ENTRY_CLOSED,
             expect_fail=False, want="provenance: 0 unnamed", must_not="UNNAMED AUTHORISER")
        # A malformed line must be reported ONCE, by check 2, not twice.
        case("a-malformed-line-is-not-reported-again-by-check-3",
             roster=_ROSTER, reader_for=both, pm=_ACT, ledger="{not json\n" + _ENTRY,
             expect_fail=True, must_not="UNNAMED AUTHORISER")

    failed = [n for n, ok in cases if not ok]
    if failed:
        print(f"\nverify-commercial-events: SELFTEST FAILED — {', '.join(failed)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-commercial-events: SELFTEST OK — {len(cases)} fixtures, all three checks "
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
