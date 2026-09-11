#!/usr/bin/env python3
"""Report improvement-agent's share of agent dispatches, and its COMPOSITION.

WHY THIS EXISTS. This system's purpose is delivery, and its learning loop is meant to run
alongside that — not to crowd it out. Nothing measured whether it was. On 2026-09-10 the reviewer
asked for improvement-agent's dispatch share and it had to be reconstructed by hand from
`logs/routing.log`, line by line; the answer was **90 of 294 dispatches, 30.6%** against a
10-15% intent (`IMP-0719`).

WHY IT REPORTS COMPOSITION AND NOT JUST THE SHARE, which is the part worth understanding before
changing this script. Four findings were written about that 30.6%, and between them they
attributed it to causes measuring 8, 12 and 45 dispatches. Re-derived by classifying each line
into exactly one category: the batch trigger they called "the largest single driver" was **8**
(8.9%), the blocker trigger one of them put at 12 was **31** (34.4%), and the largest correctable
driver — **24 dispatches that existed only to relay a gate keyword to an agent whose draft was
already parked**, plus 7 more that only moved a status field — was named by NONE of them
(`IMP-0720`).

The reason is mechanical and it is why a bare percentage would not have helped: those four
findings each counted with overlapping `grep -c` keyword searches. Overlapping counts
double-count a line naming two causes, and — the part that actually cost — a category whose
lines contain none of the searched words returns **nothing**, which is indistinguishable from a
category measured at zero (`IMP-0542`'s shape, applied to a classification rather than to a
shell pipeline). The keyword-relay lines say "reviewer said APPROVE IMPROVEMENTS" and contain
neither "blocker" nor "batch", so they were invisible.

So this script assigns every dispatch line to EXACTLY ONE category, in a documented precedence,
and prints the category table beside the share. A share that moves without a visible cause is
not actionable, and a cause nobody enumerated is how this went unmeasured for 294 dispatches.

WHAT IT IS NOT. It is not a gate and it never blocks: a process or commercial finding never
halts a build (`CLAUDE.md`, Commercial Rules; PM-R30). `--warn-only` exists so it can be wired
as a build step that reports and exits 0. The threshold below is a REPORTING flag, deliberately
not an enforcement bound — the legitimate share depends on how much genuine blocker work
exists, which no script can judge.

RESIDUAL, stated honestly. A resume via `SendMessage` leaves NO repository trace, so a
continuation that was correctly handled as a resume is invisible here and a continuation
mis-handled as a fresh dispatch is counted — which is the right direction (the metric is
pessimistic about the behaviour it wants to discourage) but means this cannot verify compliance
with the resume rule, only make its consequence visible. `agents/WORKFLOW.md` states that
limitation where the rule is written.

Run:
    python3 scripts/report-dispatch-share.py                 # human report
    python3 scripts/report-dispatch-share.py --warn-only     # always exit 0 (build step)
    python3 scripts/report-dispatch-share.py --window 100     # last N dispatches only
    python3 scripts/report-dispatch-share.py --json           # machine-readable
    python3 scripts/report-dispatch-share.py --selftest       # prove the categories separate
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROUTING_LOG = REPO_ROOT / "logs" / "routing.log"

# The agent whose share this reports. Not parameterised: the intent being protected is
# specifically "review work must not crowd out delivery", and no other agent has that shape.
SUBJECT = "improvement-agent"

# A REPORTING threshold, not an enforcement bound. 15% is the top of the reviewer's stated
# 10-15% intent (2026-09-10).
FLAG_ABOVE_PCT = 15.0

# A dispatch line. RESUMED / RE-DISPATCHED are continuations of one cycle, not fresh triggers;
# they are counted separately so a dispatch-share figure cannot conflate the two (`IMP-0718`).
DISPATCH_RE = re.compile(
    r"\b(?P<verb>ROUTED_TO|RESUMED|RE-DISPATCHED):\s*(?P<agent>[a-z0-9-]+agent)\b")

# Exactly one category per line, first match wins. The precedence is the argument of this
# script, so it is written down rather than left in the order of an if-chain:
#
#   A relay/apply  before everything — a line saying "reviewer said APPROVE IMPROVEMENTS" often
#                  ALSO names the blocker that opened the review, and it is the relay that
#                  describes what the dispatch actually did.
#   B bookkeeping  before the triggers, for the same reason: "close IMP-nnnn (blocker)" is a
#                  status move, not a blocker review.
#   C continuation before the triggers: a resumed cycle is not a fresh trigger.
#   D capability   before the triggers: capability mode is authorised by a design document,
#                  not by a finding, so a finding id in the line is incidental.
#   E blocker      before batch: the blocker rung fires immediately and outranks the queue count.
#   F batch        last of the triggers.
CATEGORIES: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    ("A", "relay a gate keyword / apply a parked draft",
     re.compile(r"approve improvements|approve all|reviewer approved|apply review|relay",
                re.I)),
    ("B", "bookkeeping-only status move",
     re.compile(r"\b(close|closing|mark resolved|reobserve|properly so|--check exits 0)\b",
                re.I)),
    ("C", "continuation / revision of a live cycle",
     re.compile(r"\b(revision|revise|resum|continuation|feedback|amend|fold)\b", re.I)),
    ("D", "capability mode", re.compile(r"capability", re.I)),
    ("E", "blocker trigger", re.compile(r"blocker", re.I)),
    ("F", "batch trigger", re.compile(r"batch|unread|queue|>=?\s*\d+\s*(new|unread)", re.I)),
)
NO_ANALYSIS = ("A", "B")   # categories that carry no new analytical work


def classify(line: str) -> tuple[str, str]:
    for key, label, pattern in CATEGORIES:
        if pattern.search(line):
            return key, label
    return "G", "other / unclassified"


def dispatches(text: str) -> list[tuple[str, str, str]]:
    """(verb, agent, line) for every dispatch line, in log order."""
    out = []
    for line in text.splitlines():
        m = DISPATCH_RE.search(line)
        if m:
            out.append((m.group("verb"), m.group("agent"), line))
    return out


def report(log_text: str, window: int | None = None) -> dict:
    all_d = dispatches(log_text)
    if window:
        all_d = all_d[-window:]
    total = len(all_d)
    subject = [d for d in all_d if d[1] == SUBJECT]
    counts: Counter[tuple[str, str]] = Counter()
    for _verb, _agent, line in subject:
        counts[classify(line)] += 1

    n_subject = len(subject)
    share = (100.0 * n_subject / total) if total else 0.0
    no_analysis = sum(v for (k, _l), v in counts.items() if k in NO_ANALYSIS)
    # What the share would be if the no-analysis dispatches had been resumes.
    adj_total, adj_subject = total - no_analysis, n_subject - no_analysis
    adj_share = (100.0 * adj_subject / adj_total) if adj_total else 0.0

    per_agent = Counter(agent for _v, agent, _l in all_d)
    return {
        "total_dispatches": total,
        "subject": SUBJECT,
        "subject_dispatches": n_subject,
        "share_pct": round(share, 1),
        "flag_above_pct": FLAG_ABOVE_PCT,
        "flagged": share > FLAG_ABOVE_PCT,
        "no_analysis_dispatches": no_analysis,
        "share_pct_if_relays_were_resumes": round(adj_share, 1),
        "composition": {f"{k} {label}": v for (k, label), v in
                        sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0]))},
        "continuations": sum(1 for v, a, _ in all_d if a == SUBJECT and v != "ROUTED_TO"),
        "top_agents": dict(per_agent.most_common(6)),
        "window": window,
    }


def render(r: dict) -> str:
    lines = []
    scope = f"last {r['window']} dispatches" if r["window"] else "all logged dispatches"
    lines.append(f"DISPATCH SHARE ({scope})")
    lines.append("")
    lines.append(f"  {r['subject']}: {r['subject_dispatches']} of {r['total_dispatches']} "
                 f"dispatches = {r['share_pct']}%"
                 + ("  ** above the " f"{r['flag_above_pct']}% reporting flag **"
                    if r["flagged"] else ""))
    lines.append("")
    lines.append("  Composition — each dispatch counted in exactly one category:")
    for label, n in r["composition"].items():
        pct = 100.0 * n / r["subject_dispatches"] if r["subject_dispatches"] else 0.0
        lines.append(f"    {n:4d}  {pct:5.1f}%  {label}")
    lines.append("")
    lines.append(f"  Of these, {r['no_analysis_dispatches']} carry no new analysis "
                 f"(categories A and B). agents/WORKFLOW.md routes those as RESUMES, not "
                 f"dispatches;")
    lines.append(f"  handled that way the share reads "
                 f"{r['share_pct_if_relays_were_resumes']}%.")
    lines.append(f"  Continuations marked as such in the log (RESUMED/RE-DISPATCHED): "
                 f"{r['continuations']}.")
    lines.append("")
    lines.append("  This is a REPORT, never a gate: a process finding does not halt a build.")
    return "\n".join(lines)


def selftest() -> int:
    """Prove the categories separate, and that a no-keyword category is not lost."""
    failures: list[str] = []

    def case(name: str, line: str, expect_key: str) -> None:
        got, _label = classify(line)
        if got != expect_key:
            failures.append(f"{name}: expected {expect_key}, got {got} for {line!r}")

    # The category that four findings missed entirely, because it names no trigger keyword.
    case("relay-with-no-trigger-keyword",
         "[LEAD] ROUTED_TO:improvement-agent — reviewer said APPROVE IMPROVEMENTS, apply", "A")
    case("relay-outranks-the-blocker-that-opened-it",
         "ROUTED_TO:improvement-agent — APPROVE IMPROVEMENTS for the blocker review", "A")
    case("bookkeeping-outranks-blocker",
         "ROUTED_TO:improvement-agent — close IMP-0638 (blocker) so --check exits 0", "B")
    case("continuation", "ROUTED_TO:improvement-agent — revision round 2 of the draft", "C")
    case("capability", "ROUTED_TO:improvement-agent — capability mode, A1/A2", "D")
    case("blocker", "ROUTED_TO:improvement-agent — IMP-0569 (blocker, unread), immediate", "E")
    case("batch", "ROUTED_TO:improvement-agent — batch trigger crossed (33 unread of 30)", "F")
    case("unclassified-is-visible-not-dropped",
         "ROUTED_TO:improvement-agent — something nobody anticipated", "G")

    # A line must be counted once, not once per matching keyword.
    both = "ROUTED_TO:improvement-agent — APPROVE IMPROVEMENTS; blocker batch capability"
    if sum(1 for _k, _l, p in CATEGORIES if p.search(both)) < 2:
        failures.append("fixture no longer matches multiple categories — it must, to prove "
                        "that precedence assigns exactly one")
    if classify(both)[0] != "A":
        failures.append("a multi-keyword line must resolve to exactly one category (A)")

    # Continuations are dispatch lines too, and are attributed to the right agent.
    text = ("[2026-01-01] ROUTED_TO:build-agent — x\n"
            "[2026-01-02] ROUTED_TO:improvement-agent — IMP-1 (blocker, unread)\n"
            "[2026-01-03] RESUMED:improvement-agent — reviewer said APPROVE IMPROVEMENTS\n"
            "[2026-01-04] ROUTED_TO:test-agent — y\n")
    r = report(text)
    if r["total_dispatches"] != 4:
        failures.append(f"expected 4 dispatches, got {r['total_dispatches']}")
    if r["subject_dispatches"] != 2:
        failures.append(f"expected 2 subject dispatches, got {r['subject_dispatches']}")
    if r["continuations"] != 1:
        failures.append(f"expected 1 continuation, got {r['continuations']}")
    if r["share_pct"] != 50.0:
        failures.append(f"expected 50.0%, got {r['share_pct']}")
    # One of the two is a relay, so the adjusted share must drop.
    if r["share_pct_if_relays_were_resumes"] >= r["share_pct"]:
        failures.append("removing a relay must lower the adjusted share")

    # An empty log must not divide by zero or claim a share.
    empty = report("")
    if empty["total_dispatches"] != 0 or empty["share_pct"] != 0.0 or empty["flagged"]:
        failures.append("an empty log must report 0 and flag nothing")

    # The flag must be able to fire AND not fire.
    hot = report("ROUTED_TO:improvement-agent — IMP-1 (blocker, unread)\n")
    if not hot["flagged"]:
        failures.append("100% share must trip the reporting flag")
    cold = report("".join("ROUTED_TO:build-agent — x\n" for _ in range(20))
                  + "ROUTED_TO:improvement-agent — IMP-1 (blocker, unread)\n")
    if cold["flagged"]:
        failures.append("~4.8% share must NOT trip the reporting flag")

    for f in failures:
        print(f"  FAIL  {f}")
    if failures:
        print(f"report-dispatch-share --selftest: FAILED — {len(failures)} failure(s)")
        return 1
    print("report-dispatch-share --selftest: PASS (11 checks: one category per line, "
          "precedence, continuations, empty log, both flag polarities)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", type=Path, default=ROUTING_LOG)
    p.add_argument("--window", type=int, default=None,
                   help="consider only the last N dispatches")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--warn-only", action="store_true",
                   help="always exit 0 (how this is wired as a build step)")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()

    try:
        text = a.log.read_text(encoding="utf-8")
    except OSError as e:
        print(f"report-dispatch-share: cannot read {a.log}: {e}")
        return 0 if a.warn_only else 1

    r = report(text, a.window)
    print(json.dumps(r, indent=2) if a.json else render(r))
    # Even without --warn-only this returns 0 when the flag is not tripped; the flag itself
    # is advisory, and a non-zero here would make a REPORT into a gate.
    return 0


if __name__ == "__main__":
    sys.exit(main())
