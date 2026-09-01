#!/usr/bin/env python3
"""Verify every dispatch recorded in logs/routing.log was closed by a terminal line.

WHY THIS EXISTS. A dispatched agent that ERRORS is caught by `agents/WORKFLOW.md` → "When a
dispatch dies instead of finishing". A dispatch that produces **nothing** is caught by nothing at
all: the improvement-log gate finds findings that were logged and left unread, not work that was
never done. Three instances in under twelve hours (`IMP-0300`, `IMP-0291`, and the resumed
improvement-agent dispatch `IMP-0300` itself records):

  * 2026-08-24 23:25 — development-agent dispatched to add the A-FIN-07 source marker. `A-FIN`
    appeared nowhere in the target file twelve hours later.
  * 2026-08-24 23:25 — improvement-agent resumed "to fold in IMP-0286 and IMP-0287". Neither id
    appeared anywhere in the review document it was resumed to edit.
  * 2026-08-25 09:23 — architect-agent dispatched for a combined TAD; stalled with no gate output,
    noticed only because the reviewer said so.

Third instance of class `dispatched-agent-stalls-silently`, so the altitude rule in
`skills/how-to-promote-a-finding.md` §2 forbids a fourth prose patch: review 27 change 6 added the
CONVENTION (every `ROUTED_TO` is closed by a terminal line) and this is the check.

WHY IT IS FORWARD-ONLY FROM A CUTOFF, WHICH IS THE WHOLE DESIGN. Measured on the log this gate was
written against: **109 `ROUTED_TO` lines against 17 `GATE_RECEIVED`** and one `STALLED`. A gate over
the full history would emit roughly ninety findings about dispatches that completed fine under a
convention that did not exist yet — and a gate that cries ninety times on its first run is a gate
people configure away. That is the `IMP-0181` precedent, already applied to the improvement log:
enforce from the date the rule became real, and say so out loud rather than quietly excluding.

Dispatches before the cutoff are counted and reported as OUT-OF-SCOPE in the summary — visible,
never silently dropped.

THE CUTOFF IS A CONVENTION DECISION, NOT A DEFECT FIX, AND IT IS THE REVIEWER'S TO MAKE. It was
2026-08-25 (the day the convention itself was established) until 2026-09-01, when the reviewer set
it to **2026-08-31** — *"the reconciliation date can be yesterday … everything before that is
history"*. It is INCLUSIVE of its own day: timestamps are `[YYYY-MM-DD HH:MM]`, a date-only cutoff
parses to midnight, and the comparison is a strict `<`, so 2026-08-31 dispatches are in scope and
everything before that day is not.

WHY THIS GATE IS STILL `--warn-only` AFTER THAT RE-SCOPING, WHICH IS THE POINT WORTH READING.
Moving the cutoff did NOT empty the queue: 33 unreconciled before, **17 after**. SOFT is therefore
a measurement, not a preference — flipping it HARD today reds every build on seventeen real
unclosed dispatches from one evening's session series. The remedy is to reconcile those seventeen
and then drop the flag, not to pick a cutoff late enough to read zero. A cutoff of 2026-09-01 does
read zero unreconciled, and it does so over four dispatches of which four are in-flight and none is
closed — a green over an empty corpus, which is the tell `agents/improvement-agent.md` names and
not evidence of anything. Whoever removes `--warn-only` should re-run this gate first and paste the
count.

WHAT "CLOSED" MEANS. A `ROUTED_TO:<agent>` line for feature F is closed by a LATER line whose
marker is one of `GATE_RECEIVED` / `STALLED` / `BLOCKED` / `HANDOFF_RECEIVED` and which names the
same agent and the same feature. Terminals are consumed: two dispatches to one agent need two
terminal lines, which is exactly the defect `IMP-0300` records — a resumed session reuses an id
whose earlier `GATE_RECEIVED` reads as if it closed the later dispatch.

EXIT CODES:

  * 0 — every in-scope dispatch is closed (or only in-flight ones remain, or `--warn-only`).
  * 1 — at least one UNRECONCILED dispatch: in scope, older than the grace period, no terminal
    line. Also 1 if the log is missing or holds no parseable dispatch line at all, which is the
    `IMP-0007` shape — a gate reporting OK over nothing.
  * 2 — command-line usage error. Never a finding.

IN-FLIGHT IS NOT A FINDING. A dispatch younger than `--grace-minutes` (default 120) has simply not
finished yet — the session running this check is itself usually one of them. Reported as a note.

RESIDUAL, stated because every promotion leaves one. **This reads the log's shape, never the
artefact.** A dispatch that writes a terminal line and produced no actual work is invisible here,
which is `IMP-0300`'s own remedy ("before trusting a routing.log claim that work was done, grep the
artefact") and stays prose. It also cannot see a dispatch that was never logged at all: an agent
that skips its `ROUTED_TO` line is outside every check in this file.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# [2026-08-25 15:18] [LEAD] [system] ROUTED_TO:improvement-agent — text
LINE_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2})[ T](?P<hm>\d{2}:\d{2})\]\s*"
    r"(?:\[(?P<actor>[^\]]*)\]\s*)?"
    r"(?:\[(?P<feature>[^\]]*)\]\s*)?"
    r"(?P<marker>[A-Z_]+)\s*:\s*(?P<rest>.*)$"
)

TERMINAL_MARKERS = {"GATE_RECEIVED", "STALLED", "BLOCKED", "HANDOFF_RECEIVED"}
DISPATCH_MARKER = "ROUTED_TO"

# The reconciliation date. Dispatches timestamped BEFORE this day are history; this day itself is
# in scope, because the comparison below is a strict `<` against midnight.
#
# Set 2026-09-01 by reviewer decision, answering the cutoff half of improvement review 7 §6 open
# decision 1 ("Should routing-reconciliation ever go HARD, and from what cutoff?"). Recorded in
# docs/improvements/2026-09-01-improvement-review-2.md (IMP-0547). The previous value was
# 2026-08-25, the day review 27 change 6 established the convention itself.
DEFAULT_CUTOFF = "2026-08-31"


@dataclass
class Entry:
    line_no: int
    when: datetime
    feature: str
    marker: str
    agent: str
    text: str


def _agent_of(rest: str) -> str:
    """The agent name a marker names: `improvement-agent — reviewer sent ...` -> that agent."""
    m = re.match(r"\s*([a-z][a-z0-9-]*agent|[a-z][a-z0-9-]{2,})", rest.strip(), re.IGNORECASE)
    return m.group(1).lower() if m else ""


def parse(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for i, raw in enumerate(text.splitlines(), 1):
        m = LINE_RE.match(raw.strip())
        if not m:
            continue
        marker = m.group("marker")
        if marker != DISPATCH_MARKER and marker not in TERMINAL_MARKERS:
            continue
        try:
            when = datetime.strptime(f"{m.group('ts')} {m.group('hm')}", "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        entries.append(Entry(
            line_no=i,
            when=when,
            feature=(m.group("feature") or "").strip(),
            marker=marker,
            agent=_agent_of(m.group("rest")),
            text=m.group("rest").strip()[:120],
        ))
    return entries


@dataclass
class Finding:
    kind: str
    line_no: int
    when: datetime
    agent: str
    feature: str
    detail: str

    def __str__(self) -> str:
        return (f"{self.kind}: routing.log:{self.line_no}: "
                f"[{self.when:%Y-%m-%d %H:%M}] {self.agent or '<unnamed agent>'} "
                f"[{self.feature or 'no feature'}] — {self.detail}")


def run(log: Path, cutoff: datetime, now: datetime,
        grace: timedelta) -> tuple[int, list[Finding], dict[str, int]]:
    stats = {"dispatches": 0, "in_scope": 0, "out_of_scope": 0,
             "closed": 0, "in_flight": 0, "unreconciled": 0, "terminals": 0}

    if not log.is_file():
        return 1, [Finding("NO-LOG", 0, now, "", "",
                           f"{log} does not exist, so this gate cannot see the thing it checks "
                           f"(IMP-0007).")], stats

    entries = parse(log.read_text(encoding="utf-8"))
    dispatches = [e for e in entries if e.marker == DISPATCH_MARKER]
    terminals = [e for e in entries if e.marker in TERMINAL_MARKERS]
    stats["dispatches"] = len(dispatches)
    stats["terminals"] = len(terminals)

    if not dispatches:
        return 1, [Finding("NO-DISPATCHES", 0, now, "", "",
                           f"{log} holds no parseable {DISPATCH_MARKER} line. Either the log's "
                           f"format changed or nothing has ever been dispatched; both are worth "
                           f"reporting rather than passing over nothing (IMP-0007).")], stats

    # MATCHING IS LIFO, AND THAT IS LOAD-BEARING. A terminal line closes the MOST RECENT still-open
    # dispatch for its agent and feature, not the oldest.
    #
    # This was FIFO in the first version, and the live log disproved it. Three architect-agent
    # dispatches for one feature on 2026-08-25 (09:23, 09:52, 13:52) against two terminal lines
    # (11:32, 14:20): FIFO paired 09:23<-11:32 and 09:52<-14:20, leaving the 13:52 dispatch —
    # which had in fact completed — looking open, and reporting the count as 0 unreconciled once
    # the grace period absorbed it. The 09:23 dispatch is the one that actually stalled; it is the
    # incident IMP-0291 was logged for. FIFO therefore laundered the one real defect in the log
    # into a false note about a healthy dispatch.
    #
    # LIFO gets it right for the reason the log is written the way it is: an agent reports on what
    # it was most recently asked to do, and a re-dispatch (09:52 says "re-dispatch: prior
    # architect-agent dispatch ... launched 09:23") supersedes the attempt before it. An abandoned
    # older dispatch stays open, which is exactly the finding wanted.
    #
    # Terminals are still CONSUMED, so a resumed session's later dispatch cannot be closed by the
    # terminal line that already closed an earlier one — IMP-0300's defect.
    findings: list[Finding] = []
    open_stacks: dict[tuple[str, str], list[Entry]] = {}
    closed_ids: set[int] = set()

    for e in sorted(entries, key=lambda e: (e.when, e.line_no)):
        key = (e.agent, e.feature)
        if e.marker == DISPATCH_MARKER:
            open_stacks.setdefault(key, []).append(e)
        elif open_stacks.get(key):
            closed_ids.add(open_stacks[key].pop().line_no)

    for d in sorted(dispatches, key=lambda e: (e.when, e.line_no)):
        if d.when < cutoff:
            stats["out_of_scope"] += 1
            continue
        stats["in_scope"] += 1

        if d.line_no in closed_ids:
            stats["closed"] += 1
            continue

        if now - d.when < grace:
            stats["in_flight"] += 1
            findings.append(Finding(
                "IN-FLIGHT", d.line_no, d.when, d.agent, d.feature,
                f"dispatched {int((now - d.when).total_seconds() // 60)} minute(s) ago with no "
                f"terminal line yet — inside the {int(grace.total_seconds() // 60)}-minute grace "
                f"period, so not a finding. Close it with GATE_RECEIVED, BLOCKED or STALLED."))
            continue

        stats["unreconciled"] += 1
        findings.append(Finding(
            "UNRECONCILED", d.line_no, d.when, d.agent, d.feature,
            f"dispatched and never closed by a GATE_RECEIVED / BLOCKED / STALLED line naming the "
            f"same agent and feature. A dispatch that produces nothing is invisible to every "
            f"other gate in this system, so verify the artefact it was supposed to produce before "
            f"assuming it ran (IMP-0300, IMP-0291)."))

    code = 1 if stats["unreconciled"] else 0
    return code, findings, stats


# ---------------------------------------------------------------------------------------------
# Self-test — fixtures at runtime, proving the gate can fail and cannot pass over nothing.
# ---------------------------------------------------------------------------------------------

_FIXTURE = """
[2026-08-20 09:00] [LEAD] [old-feature] ROUTED_TO:plan-agent — before the cutoff, never closed
[2026-08-26 09:00] [LEAD] [featA] ROUTED_TO:development-agent — closed properly below
[2026-08-26 09:30] [LEAD] [featA] GATE_RECEIVED:development-agent — done
[2026-08-26 10:00] [LEAD] [featB] ROUTED_TO:architect-agent — never closed, well past grace
[2026-08-26 10:05] [LEAD] [featC] ROUTED_TO:test-agent — closed by BLOCKED
[2026-08-26 10:20] [LEAD] [featC] BLOCKED:test-agent — could not proceed
[2026-08-26 11:00] [LEAD] [featD] ROUTED_TO:pm-agent — resumed-session case, see below
[2026-08-26 11:10] [LEAD] [featD] GATE_RECEIVED:pm-agent — closes the 11:00 dispatch
[2026-08-26 11:20] [LEAD] [featD] ROUTED_TO:pm-agent — SECOND dispatch, must NOT reuse the 11:10 terminal
[2026-08-26 23:50] [LEAD] [featE] ROUTED_TO:build-agent — inside the grace period
"""


def selftest() -> int:
    failures: list[str] = []
    now = datetime(2026, 8, 27, 0, 0)
    cutoff = datetime(2026, 8, 26, 0, 0)
    grace = timedelta(minutes=120)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        log = root / "routing.log"
        log.write_text(_FIXTURE, encoding="utf-8")
        code, findings, stats = run(log, cutoff, now, grace)

        if code != 1:
            failures.append(f"known-bad exited {code}, expected 1")
        unrec = {(f.agent, f.feature) for f in findings if f.kind == "UNRECONCILED"}
        if ("architect-agent", "featB") not in unrec:
            failures.append("the never-closed architect-agent dispatch was not reported")
        # THE RESUMED-SESSION CASE, which is IMP-0300's actual defect.
        if ("pm-agent", "featD") not in unrec:
            failures.append("the SECOND pm-agent dispatch was not reported — a terminal line was "
                            "reused to close two dispatches, which is IMP-0300 exactly")
        if stats["unreconciled"] != 2:
            failures.append(f"expected 2 unreconciled, got {stats['unreconciled']}")
        # Forward-only.
        if stats["out_of_scope"] != 1:
            failures.append(f"expected 1 out-of-scope dispatch, got {stats['out_of_scope']}")
        if any(f.agent == "plan-agent" for f in findings):
            failures.append("a pre-cutoff dispatch was reported — this gate is forward-only")
        # Grace period.
        if not any(f.kind == "IN-FLIGHT" and f.agent == "build-agent" for f in findings):
            failures.append("the in-grace build-agent dispatch was not reported as IN-FLIGHT")
        if any(f.kind == "UNRECONCILED" and f.agent == "build-agent" for f in findings):
            failures.append("an in-flight dispatch was counted as a defect")
        # Properly closed ones stay silent.
        if any(f.agent == "development-agent" for f in findings):
            failures.append("a properly closed dispatch was reported")
        if stats["closed"] != 3:
            failures.append(f"expected 3 closed, got {stats['closed']}")

        # Known-good: every in-scope dispatch closed.
        good = root / "good.log"
        good.write_text(
            "[2026-08-26 09:00] [LEAD] [featA] ROUTED_TO:development-agent — x\n"
            "[2026-08-26 09:30] [LEAD] [featA] GATE_RECEIVED:development-agent — y\n",
            encoding="utf-8")
        code, findings, stats = run(good, cutoff, now, grace)
        if code != 0 or findings:
            failures.append(f"known-good exited {code} with {len(findings)} finding(s)")

        # Cannot report OK over nothing.
        empty = root / "empty.log"
        empty.write_text("nothing parseable here\n", encoding="utf-8")
        code, findings, stats = run(empty, cutoff, now, grace)
        if code != 1 or not any(f.kind == "NO-DISPATCHES" for f in findings):
            failures.append("a log with no dispatch lines did not report NO-DISPATCHES")

        code, findings, stats = run(root / "absent.log", cutoff, now, grace)
        if code != 1 or not any(f.kind == "NO-LOG" for f in findings):
            failures.append("a missing log did not report NO-LOG")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\nverify-routing-reconciliation --selftest: FAILED ({len(failures)} failure(s)).",
              file=sys.stderr)
        return 1

    print("verify-routing-reconciliation --selftest: OK — 5 fixture(s): an unclosed dispatch "
          "reports; a RESUMED second dispatch to the same agent is not closed by the earlier "
          "terminal line (IMP-0300); pre-cutoff dispatches are out of scope, not findings; a "
          "dispatch inside the grace period is IN-FLIGHT, not a defect; a missing log and a log "
          "with no dispatch lines both report rather than passing over nothing.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--log", type=Path, default=Path("logs/routing.log"))
    parser.add_argument("--cutoff", default=DEFAULT_CUTOFF,
                        help=f"YYYY-MM-DD; dispatches before this date are out of scope, and "
                             f"this date itself IS in scope (default: {DEFAULT_CUTOFF}, the "
                             f"reconciliation date set by reviewer decision 2026-09-01). "
                             f"Forward-only by design — see the module docstring")
    parser.add_argument("--grace-minutes", type=int, default=120,
                        help="a dispatch younger than this with no terminal line is IN-FLIGHT, "
                             "not a finding (default: 120)")
    parser.add_argument("--now", default=None,
                        help="override 'now' as YYYY-MM-DD HH:MM (testing)")
    parser.add_argument("--warn-only", action="store_true",
                        help="print findings and exit 0")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove this gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    try:
        cutoff = datetime.strptime(args.cutoff, "%Y-%m-%d")
    except ValueError:
        print(f"usage error: --cutoff must be YYYY-MM-DD, got {args.cutoff!r}", file=sys.stderr)
        return 2
    now = (datetime.strptime(args.now, "%Y-%m-%d %H:%M") if args.now else datetime.now())

    code, findings, stats = run(args.log, cutoff, now, timedelta(minutes=args.grace_minutes))

    notes = [f for f in findings if f.kind in ("IN-FLIGHT",)]
    hard = [f for f in findings if f.kind not in ("IN-FLIGHT",)]

    for f in notes:
        print(f"NOTE: {f}", file=sys.stderr)
    if hard:
        label = "WARNING" if args.warn_only else "ERROR"
        for f in hard:
            print(f"{label}: {f}", file=sys.stderr)

    summary = (f"{stats['unreconciled']} unreconciled, {stats['in_flight']} in flight, "
               f"{stats['closed']} closed, of {stats['in_scope']} dispatch(es) in scope "
               f"since {args.cutoff} ({stats['out_of_scope']} earlier dispatch(es) out of scope "
               f"by design, {stats['dispatches']} total, {stats['terminals']} terminal line(s))")

    if code != 0:
        print(f"\nverify-routing-reconciliation: FAILED — {summary}."
              + (" Exiting 0: --warn-only." if args.warn_only else ""), file=sys.stderr)
        return 0 if args.warn_only else code

    print(f"verify-routing-reconciliation: OK — {summary}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
