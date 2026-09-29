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
import json
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

# CHECK 2 — every `wbs:` tag resolves to a task in contract/wbs.json (IMP-0576).
#
# The WBS task id is the join key of the whole system: it is what lets a commit be traced to a
# contract line and a contract line to an invoice (CLAUDE.md, Commercial Rules 1). A tag that
# resolves to NO accepted task is therefore not a typo — it is work attributed to a contract line
# that does not exist, which makes the real line look unevidenced in both directions
# (verify-wbs-chain.py walks task->evidence and evidence->task, and neither walk can see this).
#
# IMP-0576: an early dispatch on trustee-portal-visual-refresh typed `wbs:6.9` without checking it,
# and every subsequent dispatch and commit copied it forward as established convention. Automation 6
# runs 6.1 through 6.8; there is no 6.9. It was caught by a human at a routing decision, 95 routing
# lines and 8 commits later.
#
# WHY IT LIVES HERE and not in verify-wbs-chain.py, which is the file the finding proposed: this
# gate already reads logs/routing.log, already runs on every build, already has a reviewer-set
# cutoff, and is already SOFT. Adding it to the PM gate instead would mean a check that runs only
# at PM gates over the same data. No new script, no new build step, no change to the verify-*.py
# count (IMP-0568, IMP-0569).
#
# REPORTED PER DISTINCT ID, not per line — 43 warnings about one mislabel is how a SOFT gate's
# output stops being read (IMP-0395).
#
# COMMIT MESSAGES ARE DELIBERATELY NOT COVERED. 8 commits carry the same bad tag and git history is
# not editable, so a gate over it would open red on work no dispatch can ever close. The cutoff is
# what keeps this check honest about the same problem in the log: pre-cutoff lines are history.
WBS_TAG_RE = re.compile(r"\bwbs:(?P<ids>\d+\.\d+(?:\s*,\s*\d+\.\d+)*)")
LINE_DATE_RE = re.compile(r"^\[(?P<ts>\d{4}-\d{2}-\d{2})")
DEFAULT_WBS = Path("contract/wbs.json")

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


def accepted_task_ids(wbs: Path) -> set[str] | None:
    """The accepted task ids, or None if the contract cannot be read.

    None is not an empty set. An unreadable baseline must REPORT, never silently accept every
    tag — a gate that passes over nothing is IMP-0007.
    """
    try:
        data = json.loads(wbs.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        return None
    ids = {str(t["id"]) for t in tasks if isinstance(t, dict) and "id" in t}
    return ids or None


def check_wbs_tags(log_text: str, cutoff: datetime,
                   wbs: Path) -> tuple[list[Finding], dict[str, int]]:
    """Every `wbs:` tag on or after the cutoff names an accepted task (IMP-0576)."""
    stats = {"wbs_tags": 0, "wbs_tags_in_scope": 0, "wbs_ids_seen": 0, "wbs_ids_unknown": 0}
    valid = accepted_task_ids(wbs)
    if valid is None:
        return [Finding("NO-WBS", 0, cutoff, "", "",
                        f"{wbs} could not be read as a task list, so the tag check cannot see "
                        f"the thing it checks. Not passing over nothing (IMP-0007).")], stats

    # id -> (first line number, first timestamp, how many in-scope lines carry it)
    unknown: dict[str, tuple[int, datetime, int]] = {}
    seen: set[str] = set()
    for line_no, line in enumerate(log_text.splitlines(), start=1):
        tags = WBS_TAG_RE.findall(line)
        if not tags:
            continue
        stats["wbs_tags"] += len(tags)
        m = LINE_DATE_RE.match(line)
        if not m:
            continue
        try:
            when = datetime.strptime(m.group("ts"), "%Y-%m-%d")
        except ValueError:
            continue
        if when < cutoff:
            continue
        stats["wbs_tags_in_scope"] += len(tags)
        for group in tags:
            for task_id in (part.strip() for part in group.split(",")):
                seen.add(task_id)
                if task_id in valid:
                    continue
                first_no, first_when, count = unknown.get(task_id, (line_no, when, 0))
                unknown[task_id] = (first_no, first_when, count + 1)

    stats["wbs_ids_seen"] = len(seen)
    stats["wbs_ids_unknown"] = len(unknown)

    findings = []
    for task_id, (first_no, first_when, count) in sorted(unknown.items()):
        findings.append(Finding(
            "UNKNOWN-WBS-TAG", first_no, first_when, "", "",
            f"`wbs:{task_id}` names no task in {wbs} ({len(valid)} accepted tasks), and "
            f"{count} line(s) on or after the cutoff carry it. The WBS task id is the join key "
            f"between a dispatch, a commit and an invoice, so an id that resolves to nothing "
            f"leaves the work it describes attributed to no contract line and the real line "
            f"looking unevidenced. Resolve it to an accepted id, or take it to commercial-agent "
            f"as a change-order decision (C-COM-002, IMP-0576)."))
    return findings, stats


def run(log: Path, cutoff: datetime, now: datetime,
        grace: timedelta,
        wbs: Path | None = None) -> tuple[int, list[Finding], dict[str, int]]:
    stats = {"dispatches": 0, "in_scope": 0, "out_of_scope": 0,
             "closed": 0, "in_flight": 0, "unreconciled": 0, "terminals": 0,
             "wbs_tags": 0, "wbs_tags_in_scope": 0, "wbs_ids_seen": 0, "wbs_ids_unknown": 0}

    if not log.is_file():
        return 1, [Finding("NO-LOG", 0, now, "", "",
                           f"{log} does not exist, so this gate cannot see the thing it checks "
                           f"(IMP-0007).")], stats

    log_text = log.read_text(encoding="utf-8")

    # CHECK 2 runs FIRST and independently: a bad task id is worth reporting whether or not any
    # dispatch is unreconciled, and the early returns below would otherwise skip it.
    wbs_findings: list[Finding] = []
    if wbs is not None:
        wbs_findings, wbs_stats = check_wbs_tags(log_text, cutoff, wbs)
        stats.update(wbs_stats)

    entries = parse(log_text)
    dispatches = [e for e in entries if e.marker == DISPATCH_MARKER]
    terminals = [e for e in entries if e.marker in TERMINAL_MARKERS]
    stats["dispatches"] = len(dispatches)
    stats["terminals"] = len(terminals)

    if not dispatches:
        return 1, wbs_findings + [
            Finding("NO-DISPATCHES", 0, now, "", "",
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
    findings: list[Finding] = list(wbs_findings)
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

    code = 1 if (stats["unreconciled"] or wbs_findings) else 0
    return code, findings, stats


# ---------------------------------------------------------------------------------------------
# CHECK 3 — every deploy is followed by ONE post-deploy improvement batch (improvement review
# 2026-09-26-7; capability design 2026-09-26 WS-U requirement 7). REPORT, NEVER HALT.
#
# WHY. The trigger it backs has existed in prose since 2026-08-17 ("a feature or phase completes
# -> after the Deployment Summary") and was never followed: Deployment Summaries were committed
# 18 times from 2026-09-01 to 2026-09-26, and none of the 142 improvement-agent dispatches in
# logs/routing.log names that trigger as its reason. A prose trigger nobody can see being skipped
# is skipped. This check makes the skip visible; it does not make the batch happen.
#
# WHAT IT READS. A deploy is a `[PIPELINE]` stage line in logs/pipeline.log whose environment is
# in instance.yaml -> environment_chain and whose status is SUCCESS, PARTIAL or FAILED. HELD is
# not a deploy (a stage paused at a gate or a refusal) and CONFIG is not an environment. Stage
# lines of ONE feature less than --grace-minutes apart are ONE episode: a retry burst or a
# dev-then-test dispatch is followed by one batch, which is the no-stacking rule. An episode is
# covered by a routing.log line ROUTED_TO / RESUMED / RE-DISPATCHED / SKIPPED naming
# improvement-agent and carrying `trigger:post-deploy`, written at or after the episode's last
# stage line and before the same feature's next episode starts.
#
# WHY IT NEVER TOUCHES THE EXIT CODE, even without --warn-only. Check 1 is SOFT today and its
# going HARD is an open decision (agents/WORKFLOW.md); this check must not go HARD with it by
# accident. The design says report, never halt: a process fact never stops a build.
#
# FORWARD-ONLY from POST_DEPLOY_REQUIRED_FROM, the day the trigger became a written convention with
# a routing-line marker. Every earlier deploy lacks the marker by construction.
# ---------------------------------------------------------------------------------------------

POST_DEPLOY_REQUIRED_FROM = "2026-09-26"   # the apply date (improvement review 2026-09-26-7)
STAGE_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2}) (?P<hm>\d{2}:\d{2})\]\s*\[PIPELINE\]\s*"
    r"\[(?P<feature>[^\]]+)\]\s*\[(?P<env>[^\]]+)\]\s*(?P<status>SUCCESS|PARTIAL|FAILED|HELD)\b")
DEPLOY_STATUSES = {"SUCCESS", "PARTIAL", "FAILED"}
BATCH_MARKERS = {"ROUTED_TO", "RESUMED", "RE-DISPATCHED", "SKIPPED"}
BATCH_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2})[ T](?P<hm>\d{2}:\d{2})\].*?"
    r"\b(?P<marker>ROUTED_TO|RESUMED|RE-DISPATCHED|SKIPPED)\s*:\s*improvement-agent\b"
    r"(?P<rest>.*)$")


def load_environment_chain(repo_root: Path) -> list[str] | None:
    try:
        import yaml
        data = yaml.safe_load((repo_root / "instance.yaml").read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — no chain means every bracketed environment is eligible
        return None
    chain = data.get("environment_chain") if isinstance(data, dict) else None
    return [str(e).strip().lower() for e in chain] if isinstance(chain, list) and chain else None


def _norm_env(env: str) -> str:
    return env.strip().lower().replace("/", "_")


def check_post_deploy_batches(routing_text: str, pipeline_text: str, since: datetime,
                              now: datetime, grace: timedelta,
                              chain: list[str] | None) -> tuple[list[Finding], dict[str, int]]:
    stats = {"pd_stage_lines": 0, "pd_episodes": 0, "pd_covered": 0, "pd_in_flight": 0,
             "pd_missing": 0, "pd_out_of_scope": 0}
    stages: list[tuple[datetime, str, str, int]] = []
    for i, raw in enumerate(pipeline_text.splitlines(), 1):
        m = STAGE_RE.match(raw.strip())
        if not m or m.group("status") not in DEPLOY_STATUSES:
            continue
        env = _norm_env(m.group("env"))
        if env == "config" or (chain is not None and env not in chain):
            continue
        when = datetime.strptime(f"{m.group('ts')} {m.group('hm')}", "%Y-%m-%d %H:%M")
        stages.append((when, m.group("feature").strip(), env, i))
    batches = []
    for raw in routing_text.splitlines():
        m = BATCH_RE.match(raw.strip())
        if m and "trigger:post-deploy" in m.group("rest"):
            batches.append(datetime.strptime(f"{m.group('ts')} {m.group('hm')}",
                                             "%Y-%m-%d %H:%M"))
    episodes: dict[str, list[list[tuple[datetime, str, str, int]]]] = {}
    for st in sorted(stages):
        eps = episodes.setdefault(st[1], [])
        if eps and st[0] - eps[-1][-1][0] < grace:
            eps[-1].append(st)
        else:
            eps.append([st])
    findings: list[Finding] = []
    for feature, eps in episodes.items():
        for n, ep in enumerate(eps):
            last = ep[-1][0]
            if last < since:
                stats["pd_out_of_scope"] += 1
                continue
            stats["pd_episodes"] += 1
            stats["pd_stage_lines"] += len(ep)
            nxt = eps[n + 1][0][0] if n + 1 < len(eps) else None
            if any(b >= last and (nxt is None or b < nxt) for b in batches):
                stats["pd_covered"] += 1
            elif nxt is None and now - last < grace:
                stats["pd_in_flight"] += 1
            else:
                stats["pd_missing"] += 1
                lines = ", ".join(f"L{s[3]} {s[2]}" for s in ep)
                findings.append(Finding(
                    "POST-DEPLOY-BATCH-MISSING", ep[-1][3], last, "improvement-agent", feature,
                    f"pipeline.log {lines}: a deploy with no `trigger:post-deploy` improvement "
                    f"batch after it (ROUTED_TO, RESUMED, RE-DISPATCHED or SKIPPED) before this "
                    f"feature's next deploy. agents/WORKFLOW.md -> Processing triggers: one "
                    f"batch follows every deploy, alongside the next delivery dispatch. Reported, "
                    f"never halting."))
    return findings, stats


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


# ---------------------------------------------------------------------------------------------
# CHECK 4 — a delivery dispatch carries its work-item ids (improvement review 2026-09-26 (6);
# capability design 2026-09-26 WS-W part W3). REPORT, NEVER HALT.
#
# WHY. Items used to fall out between agents because nothing carried them: handoffs named WBS task
# ids, and "done" was whatever a dev summary said. W3 puts `items:<id,...>` beside `wbs:` on every
# delivery dispatch (agents/lead-agent.md -> How Delegation Happens). This makes a dispatch that
# carries a numeric `wbs:` tag and no `items:` tag VISIBLE; it does not make the ids appear.
#
# WHAT IT READS. `ROUTED_TO`, `RESUMED` or `RE-DISPATCHED` lines in logs/routing.log naming
# development-, build-, test- or pipeline-agent, dated on or after ITEMS_REQUIRED_FROM. Plan- and
# architect-agent dispatches are not in scope: items are closed from development onward.
#
# WHY IT NEVER TOUCHES THE EXIT CODE, even without --warn-only: the design says "report only", and
# check 1 going HARD must not drag this with it (the same rule as check 3).
#
# SKIPPED WITH ONE NOTE when the ledger file does not exist, so an instance that has no work items
# hears nothing. FORWARD-ONLY from the apply date: measured at apply, 38 delivery dispatches since
# 2026-09-15 carried a numeric `wbs:` tag and none carried `items:`, correctly, because no ledger
# existed yet.
# ---------------------------------------------------------------------------------------------

ITEMS_REQUIRED_FROM = "2026-09-27"   # the apply date (improvement review 2026-09-26 (6))
DEFAULT_LEDGER = Path("logs/work-items.jsonl")
ITEM_DELIVERY_AGENTS = ("development-agent", "build-agent", "test-agent", "pipeline-agent")
ITEM_DISPATCH_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2})[ T](?P<hm>\d{2}:\d{2})\].*?"
    r"\b(?P<marker>ROUTED_TO|RESUMED|RE-DISPATCHED)\s*:\s*(?P<agent>[a-z][a-z-]*-agent)\b(?P<rest>.*)$")
ITEMS_TAG_RE = re.compile(r"\bitems:[A-Z][A-Z0-9]{0,9}-\d{4,}")


def check_item_tags(routing_text: str, since: datetime) -> tuple[list[Finding], dict[str, int]]:
    """Delivery dispatches on/after `since` with a numeric `wbs:` tag and no `items:` tag."""
    stats = {"it_dispatches": 0, "it_missing": 0, "it_carrying": 0, "it_out_of_scope": 0}
    findings: list[Finding] = []
    for i, raw in enumerate(routing_text.splitlines(), 1):
        m = ITEM_DISPATCH_RE.match(raw.strip())
        if not m or m.group("agent") not in ITEM_DELIVERY_AGENTS:
            continue
        rest = m.group("rest")
        if not WBS_TAG_RE.search(rest):
            continue
        when = datetime.strptime(f"{m.group('ts')} {m.group('hm')}", "%Y-%m-%d %H:%M")
        if when < since:
            stats["it_out_of_scope"] += 1
            continue
        stats["it_dispatches"] += 1
        if ITEMS_TAG_RE.search(rest):
            stats["it_carrying"] += 1
            continue
        stats["it_missing"] += 1
        fm = LINE_RE.match(raw.strip())
        findings.append(Finding("NO-ITEMS", i, when, m.group("agent"),
                                (fm.group("feature") or "").strip() if fm else "",
                                f"{m.group('marker')} carries a wbs: tag and no items: tag — "
                                f"dispatch work items by id (agents/WORKFLOW.md → Handoff Contract)"))
    return findings, stats


# ---------------------------------------------------------------------------------------------
# CHECK 5 — every improvement-agent dispatch names its trigger from a CLOSED vocabulary
# (improvement review 2026-09-28, change 6; IMP-0950, IMP-0936, IMP-0887). Report only.
#
# Two routing lines in two days stated the trigger from a remembered form of the rule: a
# governance-lane blocker routed "immediately" under the pre-lane wording (routing.log 2026-09-27
# 20:04, IMP-0936), and a post-deploy batch routed as "261 NEW entries, exceeds batch threshold"
# with no tag, when the trigger counts unread entries only (2026-09-28 08:05, IMP-0950). A free-text
# reason cannot be checked; a tag from a fixed list can. And ONE of the five tags carries a value
# this gate can verify without reconstructing the past: `trigger:deploy-blocker` must name at least
# one IMP id whose lane, derived from its own `defect_in`, is `deploy`. The lane is a property of
# the entry, not of the moment, so the check is exact.
#
# FORWARD-ONLY from the apply date, like checks 3 and 4: the vocabulary did not exist before it.
# Measured with `--improvement-trigger-since 2026-09-26` over the log as it stood at apply: 9
# improvement-agent dispatches, 9 untagged — 7 capability-mode dispatches on the evening of
# 2026-09-26, before any tag existed, plus the 2 instances above. Every one is a true "no tag";
# only the 2 are a wrong STATED trigger. The default is today, so the first run reports 0.
# NOT COVERED: a `trigger:batch-threshold` count is not verified. reviewed_in stamps carry no
# timestamp, so the queue at a past moment cannot be reconstructed.
# ---------------------------------------------------------------------------------------------

IMPROVEMENT_TRIGGER_FROM = "2026-09-29"   # the apply date (improvement review 2026-09-28)
IMPROVEMENT_TRIGGERS = ("post-deploy", "batch-threshold", "deploy-blocker", "reviewer",
                        "capability")
IMPROVEMENT_DISPATCH_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2})[ T](?P<hm>\d{2}:\d{2})\].*?"
    r"\b(?P<marker>ROUTED_TO|RE-DISPATCHED)\s*:\s*improvement-agent\b(?P<rest>.*)$")
TRIGGER_TAG_RE = re.compile(r"\btrigger:(?P<t>[a-z-]+)")
IMP_ID_RE = re.compile(r"\bIMP-\d{4}\b")


def _load_lane_function(repo_root: Path):
    """(derive_lane over the real log) from verify-improvement-log.py, or None if unavailable."""
    import importlib.util
    script = Path(__file__).resolve().parent / "verify-improvement-log.py"
    try:
        spec = importlib.util.spec_from_file_location("_vil_for_routing", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        rows, _errors = mod.load(repo_root / "logs" / "improvement-log.jsonl")
        by_id = {str(r.get("id")): r for r in rows}
        paths = mod.load_deploy_paths(repo_root)
        return lambda ident: (mod.derive_lane(by_id[ident], paths) if ident in by_id else None)
    except Exception:  # noqa: BLE001 — the lane half is skipped with a note, never silently
        return None


def check_improvement_triggers(routing_text: str, since: datetime,
                               lane_of=None) -> tuple[list[Finding], dict[str, int]]:
    """improvement-agent dispatches on/after `since`: tag present, in vocabulary, lane-true."""
    stats = {"ia_dispatches": 0, "ia_untagged": 0, "ia_unknown": 0, "ia_wrong_lane": 0,
             "ia_out_of_scope": 0, "ia_lane_unchecked": 0}
    findings: list[Finding] = []
    for i, raw in enumerate(routing_text.splitlines(), 1):
        m = IMPROVEMENT_DISPATCH_RE.match(raw.strip())
        if not m:
            continue
        when = datetime.strptime(f"{m.group('ts')} {m.group('hm')}", "%Y-%m-%d %H:%M")
        if when < since:
            stats["ia_out_of_scope"] += 1
            continue
        stats["ia_dispatches"] += 1
        fm = LINE_RE.match(raw.strip())
        feature = (fm.group("feature") or "").strip() if fm else ""
        rest = m.group("rest")
        tags = [t.group("t") for t in TRIGGER_TAG_RE.finditer(rest)]
        if not tags:
            stats["ia_untagged"] += 1
            findings.append(Finding(
                "NO-TRIGGER-TAG", i, when, "improvement-agent", feature,
                f"{m.group('marker')} names no trigger. Tag it with one of "
                f"{', '.join('trigger:' + t for t in IMPROVEMENT_TRIGGERS)}, copied from what "
                f"`verify-improvement-log.py --check` printed on this run (IMP-0950)"))
            continue
        unknown = [t for t in tags if t not in IMPROVEMENT_TRIGGERS]
        if unknown:
            stats["ia_unknown"] += 1
            findings.append(Finding(
                "UNKNOWN-TRIGGER", i, when, "improvement-agent", feature,
                f"trigger:{unknown[0]} is not in the vocabulary "
                f"({', '.join(IMPROVEMENT_TRIGGERS)})"))
            continue
        if "deploy-blocker" in tags:
            ids = IMP_ID_RE.findall(rest)
            if lane_of is None:
                stats["ia_lane_unchecked"] += 1
                continue
            lanes = [lane_of(x) for x in ids]
            if "deploy" not in lanes:
                stats["ia_wrong_lane"] += 1
                findings.append(Finding(
                    "NOT-A-DEPLOY-BLOCKER", i, when, "improvement-agent", feature,
                    f"trigger:deploy-blocker names {', '.join(ids) or 'no IMP id'}, and none "
                    f"derives to the deploy lane. A governance-lane blocker waits for the next "
                    f"batch (agents/WORKFLOW.md → Processing triggers; IMP-0936)"))
    return findings, stats


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

        # -------------------------------------------------------------------------------------
        # CHECK 2 — wbs tag resolution (IMP-0576).
        # -------------------------------------------------------------------------------------
        wbs = root / "wbs.json"
        wbs.write_text(json.dumps({"tasks": [{"id": "6.8"}, {"id": "0.4"}]}), encoding="utf-8")

        tagged = root / "tagged.log"
        tagged.write_text(
            # Pre-cutoff: a bad tag here is HISTORY, and must not be reported.
            "[2026-08-20 09:00] [LEAD] [old] ROUTED_TO:plan-agent — wbs:9.9 before the cutoff\n"
            "[2026-08-26 09:00] [LEAD] [featA] ROUTED_TO:development-agent — wbs:6.8 valid\n"
            "[2026-08-26 09:30] [LEAD] [featA] GATE_RECEIVED:development-agent — wbs:6.8 done\n"
            # The real defect: an id that resolves to no accepted task, on two lines.
            "[2026-08-26 10:00] [LEAD] [featB] ROUTED_TO:pm-agent — wbs:6.9 no such task\n"
            "[2026-08-26 10:10] [LEAD] [featB] GATE_RECEIVED:pm-agent — wbs:6.9 again\n"
            # A comma list: one good id, one bad, in a single tag.
            "[2026-08-26 10:20] [LEAD] [featC] ROUTED_TO:test-agent — wbs:0.4,7.7 mixed\n"
            "[2026-08-26 10:25] [LEAD] [featC] GATE_RECEIVED:test-agent — closed\n",
            encoding="utf-8")
        code, findings, stats = run(tagged, cutoff, now, grace, wbs=wbs)

        bad = {f.detail.split("`")[1] for f in findings if f.kind == "UNKNOWN-WBS-TAG"}
        if bad != {"wbs:6.9", "wbs:7.7"}:
            failures.append(f"expected exactly wbs:6.9 and wbs:7.7 reported, got {sorted(bad)}")
        if "wbs:9.9" in bad:
            failures.append("a PRE-CUTOFF bad tag was reported — check 2 is forward-only too")
        if stats["wbs_ids_unknown"] != 2:
            failures.append(f"expected 2 unknown ids, got {stats['wbs_ids_unknown']}")
        # One finding per distinct id, never per line: 6.9 appears on two lines.
        if len([f for f in findings if f.kind == "UNKNOWN-WBS-TAG"]) != 2:
            failures.append("check 2 reported per LINE rather than per distinct id")
        if not any("2 line(s)" in f.detail for f in findings if f.kind == "UNKNOWN-WBS-TAG"):
            failures.append("the finding for wbs:6.9 did not report its 2 in-scope occurrences")
        if code != 1:
            failures.append(f"a log with an unresolvable wbs tag exited {code}, expected 1")

        # A valid tag alone must not trip it, and must not mask an otherwise clean log.
        clean = root / "clean.log"
        clean.write_text(
            "[2026-08-26 09:00] [LEAD] [featA] ROUTED_TO:development-agent — wbs:6.8,0.4\n"
            "[2026-08-26 09:30] [LEAD] [featA] GATE_RECEIVED:development-agent — wbs:6.8\n",
            encoding="utf-8")
        code, findings, stats = run(clean, cutoff, now, grace, wbs=wbs)
        if code != 0 or findings:
            failures.append(f"a log with only valid tags exited {code} with {len(findings)}")
        if stats["wbs_ids_seen"] != 2:
            failures.append(f"expected 2 distinct valid ids seen, got {stats['wbs_ids_seen']}")

        # An unreadable baseline must REPORT, not accept every tag (IMP-0007).
        code, findings, stats = run(clean, cutoff, now, grace, wbs=root / "absent.json")
        if code != 1 or not any(f.kind == "NO-WBS" for f in findings):
            failures.append("an unreadable wbs.json did not report NO-WBS — the check passed "
                            "over nothing, which is IMP-0007")

    # CHECK 3 — post-deploy batch (WS-U requirement 7).
    pd_since = datetime(2026, 9, 27)
    pd_now = datetime(2026, 9, 28, 12, 0)
    chain = ["dev", "test", "prod"]
    P = "[{}] [PIPELINE] [{}] [{}] {} — x\n"
    B = "[{}] [LEAD] [system] {}:improvement-agent — {}\n"
    cases = {
        # (pipeline, routing, expected missing, expected in-flight)
        "deploy-then-batch-is-clean": (
            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
            B.format("2026-09-27 10:05", "ROUTED_TO", "trigger:post-deploy"), 0, 0),
        "deploy-with-no-batch-reports": (
            P.format("2026-09-27 10:00", "f", "DEV", "FAILED"), "", 1, 0),
        "dev-then-tst-burst-one-batch-is-clean": (
            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS")
            + P.format("2026-09-27 10:40", "f", "TEST", "PARTIAL"),
            B.format("2026-09-27 10:45", "ROUTED_TO", "trigger:post-deploy"), 0, 0),
        "batch-after-second-episode-only-reports-the-first": (
            P.format("2026-09-27 08:00", "f", "DEV", "SUCCESS")
            + P.format("2026-09-27 14:00", "f", "DEV", "SUCCESS"),
            B.format("2026-09-27 14:05", "RESUMED", "trigger:post-deploy"), 1, 0),
        "skipped-line-counts-as-the-batch": (
            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
            B.format("2026-09-27 10:01", "SKIPPED", "trigger:post-deploy, queue empty"), 0, 0),
        "held-and-config-lines-are-not-deploys": (
            P.format("2026-09-27 10:00", "f", "DEV", "HELD")
            + P.format("2026-09-27 11:00", "f", "CONFIG", "SUCCESS"), "", 0, 0),
        "pre-cutover-deploy-is-out-of-scope": (
            P.format("2026-09-20 10:00", "f", "DEV", "SUCCESS"), "", 0, 0),
        "recent-deploy-is-in-flight": (
            P.format("2026-09-28 11:30", "f", "DEV", "SUCCESS"), "", 0, 1),
        "batch-without-the-trigger-tag-does-not-count": (
            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
            B.format("2026-09-27 10:05", "ROUTED_TO", "blocker IMP-0001, immediately"), 1, 0),
        "environment-outside-the-chain-is-ignored": (
            P.format("2026-09-27 10:00", "f", "SANDBOX", "SUCCESS"), "", 0, 0),
    }
    for name, (ptxt, rtxt, want_missing, want_flight) in cases.items():
        found, st = check_post_deploy_batches(rtxt, ptxt, pd_since, pd_now,
                                              timedelta(minutes=120), chain)
        if st["pd_missing"] != want_missing or st["pd_in_flight"] != want_flight:
            failures.append(f"check 3 '{name}': missing {st['pd_missing']} (want {want_missing}),"
                            f" in flight {st['pd_in_flight']} (want {want_flight})")

    # CHECK 4 — work-item ids on delivery dispatches (review 2026-09-26 (6)). Report only.
    it_since = datetime(2026, 9, 27)
    R = "[{}] [LEAD] [f] {}:{} — {}\n"
    it_cases = {
        # (routing text, expected missing, expected carrying)
        "pre-cutoff-dispatch-is-silent": (R.format("2026-09-20 10:00", "ROUTED_TO", "development-agent", "wbs:6.8"), 0, 0),
        "items-tag-is-clean": (R.format("2026-09-27 10:00", "ROUTED_TO", "development-agent", "wbs:6.8 items:WI-0001,WI-0002"), 0, 1),
        "wbs-without-items-reports": (R.format("2026-09-27 10:00", "ROUTED_TO", "build-agent", "wbs:6.8"), 1, 0),
        "resumed-and-re-dispatched-count": (R.format("2026-09-27 10:00", "RESUMED", "pipeline-agent", "wbs:6.8")
                                            + R.format("2026-09-27 11:00", "RE-DISPATCHED", "test-agent", "wbs:6.8"), 2, 0),
        "plan-agent-is-out-of-scope": (R.format("2026-09-27 10:00", "ROUTED_TO", "plan-agent", "wbs:6.8"), 0, 0),
        "system-work-has-no-numeric-wbs": (R.format("2026-09-27 10:00", "ROUTED_TO", "development-agent", "wbs:system"), 0, 0),
    }
    for name, (rtxt, want_missing, want_carry) in it_cases.items():
        found, st4 = check_item_tags(rtxt, it_since)
        if st4["it_missing"] != want_missing or st4["it_carrying"] != want_carry or len(found) != want_missing:
            failures.append(f"check 4 '{name}': missing {st4['it_missing']} (want {want_missing}), "
                            f"carrying {st4['it_carrying']} (want {want_carry})")

    # CHECK 5 — improvement-agent trigger tags (improvement review 2026-09-28). Report only.
    ia_since = datetime(2026, 9, 29)
    lanes = {"IMP-9001": "deploy", "IMP-9002": "governance"}
    ia_cases = {
        # (routing text, expected finding kinds)
        "pre-cutoff-is-silent": (R.format("2026-09-27 20:04", "ROUTED_TO", "improvement-agent",
                                          "Any UNREAD blocker routes immediately (IMP-9002)"), []),
        "untagged-reports": (R.format("2026-09-29 10:00", "ROUTED_TO", "improvement-agent",
                                      "261 NEW entries, exceeds batch threshold"),
                             ["NO-TRIGGER-TAG"]),
        "known-tag-is-clean": (R.format("2026-09-29 10:00", "ROUTED_TO", "improvement-agent",
                                        "trigger:post-deploy, 12 unread"), []),
        "unknown-tag-reports": (R.format("2026-09-29 10:00", "RE-DISPATCHED", "improvement-agent",
                                         "trigger:blocker"), ["UNKNOWN-TRIGGER"]),
        "governance-blocker-tagged-deploy-reports": (
            R.format("2026-09-29 10:00", "ROUTED_TO", "improvement-agent",
                     "trigger:deploy-blocker IMP-9002"), ["NOT-A-DEPLOY-BLOCKER"]),
        "deploy-blocker-is-clean": (R.format("2026-09-29 10:00", "ROUTED_TO", "improvement-agent",
                                             "trigger:deploy-blocker IMP-9001"), []),
        "resumed-is-not-a-fresh-trigger": (R.format("2026-09-29 10:00", "RESUMED",
                                                    "improvement-agent", "relay keyword"), []),
    }
    for name, (rtxt, want_kinds) in ia_cases.items():
        found5, _st5 = check_improvement_triggers(rtxt, ia_since, lanes.get)
        if [f.kind for f in found5] != want_kinds:
            failures.append(f"check 5 '{name}': got {[f.kind for f in found5]}, "
                            f"want {want_kinds}")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\nverify-routing-reconciliation --selftest: FAILED ({len(failures)} failure(s)).",
              file=sys.stderr)
        return 1

    print("verify-routing-reconciliation --selftest: OK — 8 fixture(s). CHECK 1: an unclosed "
          "dispatch reports; a RESUMED second dispatch to the same agent is not closed by the "
          "earlier terminal line (IMP-0300); pre-cutoff dispatches are out of scope, not "
          "findings; a dispatch inside the grace period is IN-FLIGHT, not a defect; a missing "
          "log and a log with no dispatch lines both report rather than passing over nothing. "
          "CHECK 2 (IMP-0576): an unresolvable `wbs:` tag reports ONCE per distinct id with its "
          "occurrence count, a comma list is split so one bad id in `wbs:0.4,7.7` is caught, a "
          "pre-cutoff bad tag is history and stays silent, a log of only valid tags exits 0, and "
          "an unreadable contract/wbs.json reports NO-WBS instead of accepting every tag.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--log", type=Path, default=Path("logs/routing.log"))
    parser.add_argument("--wbs", type=Path, default=DEFAULT_WBS,
                        help=f"the accepted task list every `wbs:` tag must resolve to "
                             f"(default: {DEFAULT_WBS}). Same cutoff as the dispatch check")
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
    parser.add_argument("--pipeline-log", type=Path, default=Path("logs/pipeline.log"),
                        help="deploy stage lines for check 3 (post-deploy batch)")
    parser.add_argument("--post-deploy-since", default=POST_DEPLOY_REQUIRED_FROM,
                        help=f"YYYY-MM-DD; check 3 is forward-only from this date "
                             f"(default: {POST_DEPLOY_REQUIRED_FROM})")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER,
                        help=f"the work-item ledger; check 4 is skipped with a note when it does "
                             f"not exist (default: {DEFAULT_LEDGER})")
    parser.add_argument("--items-since", default=ITEMS_REQUIRED_FROM,
                        help=f"YYYY-MM-DD; check 4 is forward-only from this date "
                             f"(default: {ITEMS_REQUIRED_FROM})")
    parser.add_argument("--improvement-trigger-since", default=IMPROVEMENT_TRIGGER_FROM,
                        help=f"YYYY-MM-DD; check 5 is forward-only from this date "
                             f"(default: {IMPROVEMENT_TRIGGER_FROM})")
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

    code, findings, stats = run(args.log, cutoff, now, timedelta(minutes=args.grace_minutes),
                                wbs=args.wbs)

    # CHECK 3 never changes `code` — see its block comment.
    pd_stats = {"pd_missing": 0, "pd_covered": 0, "pd_in_flight": 0, "pd_episodes": 0,
                "pd_out_of_scope": 0}
    if args.pipeline_log.is_file() and args.log.is_file():
        pd_findings, pd_stats = check_post_deploy_batches(
            args.log.read_text(encoding="utf-8"),
            args.pipeline_log.read_text(encoding="utf-8"),
            datetime.strptime(args.post_deploy_since, "%Y-%m-%d"), now,
            timedelta(minutes=args.grace_minutes), load_environment_chain(Path.cwd()))
        for f in pd_findings:
            print(f"REPORT: {f}", file=sys.stderr)
    print(f"verify-routing-reconciliation: post-deploy batches — {pd_stats['pd_missing']} "
          f"deploy episode(s) with no batch, {pd_stats['pd_covered']} covered, "
          f"{pd_stats['pd_in_flight']} in flight, since {args.post_deploy_since} "
          f"({pd_stats['pd_out_of_scope']} earlier episode(s) out of scope). Report only.",
          file=sys.stderr)

    # CHECK 4 never changes `code` — see its block comment.
    if not args.ledger.is_file():
        print(f"verify-routing-reconciliation: work-item ids — skipped, no ledger at {args.ledger} "
              f"(an instance with no work items). Report only.", file=sys.stderr)
    elif args.log.is_file():
        it_findings, it_stats = check_item_tags(args.log.read_text(encoding="utf-8"),
                                                datetime.strptime(args.items_since, "%Y-%m-%d"))
        for f in it_findings:
            print(f"REPORT: {f}", file=sys.stderr)
        print(f"verify-routing-reconciliation: work-item ids — {it_stats['it_missing']} delivery "
              f"dispatch(es) with wbs: and no items:, {it_stats['it_carrying']} carrying items:, "
              f"since {args.items_since} ({it_stats['it_out_of_scope']} earlier out of scope). "
              f"Report only.", file=sys.stderr)

    # CHECK 5 never changes `code` — see its block comment.
    if args.log.is_file():
        lane_of = _load_lane_function(Path.cwd())
        ia_findings, ia = check_improvement_triggers(
            args.log.read_text(encoding="utf-8"),
            datetime.strptime(args.improvement_trigger_since, "%Y-%m-%d"), lane_of)
        for f in ia_findings:
            print(f"REPORT: {f}", file=sys.stderr)
        print(f"verify-routing-reconciliation: improvement-agent triggers — {ia['ia_untagged']} "
              f"untagged, {ia['ia_unknown']} unknown tag, {ia['ia_wrong_lane']} deploy-blocker "
              f"naming no deploy-lane id, of {ia['ia_dispatches']} dispatch(es) since "
              f"{args.improvement_trigger_since} ({ia['ia_out_of_scope']} earlier out of scope"
              + (f"; lane half skipped for {ia['ia_lane_unchecked']}: verify-improvement-log.py "
                 f"could not be loaded" if ia['ia_lane_unchecked'] else "")
              + "). Report only.", file=sys.stderr)

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
               f"by design, {stats['dispatches']} total, {stats['terminals']} terminal line(s)); "
               f"{stats['wbs_ids_unknown']} unknown of {stats['wbs_ids_seen']} distinct wbs "
               f"task id(s) across {stats['wbs_tags_in_scope']} in-scope tag(s) of "
               f"{stats['wbs_tags']} total")

    if code != 0:
        print(f"\nverify-routing-reconciliation: FAILED — {summary}."
              + (" Exiting 0: --warn-only." if args.warn_only else ""), file=sys.stderr)
        return 0 if args.warn_only else code

    print(f"verify-routing-reconciliation: OK — {summary}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
