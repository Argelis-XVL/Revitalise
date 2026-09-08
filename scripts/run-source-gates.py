#!/usr/bin/env python3
"""Run the SOURCE-ONLY build gates for a feature, without waiting for a build.

WHY THIS EXISTS
---------------
A development-agent dispatch authors solution source and then presents CODE REVIEW REQUIRED.
The gates that would catch a structural defect in what it just wrote are real, HARD and already
wired into config/<slug>-build.yml — they simply run at BUILD time, which can be one or many
dispatches later. When a batch is deliberately held open for a group build, defects accumulate
across that gap with nothing observing them.

IMP-0619 was one such gate (root-components-resolve) missed by the wbs:3.2 dispatch. IMP-0621 is
what running the whole set found: five further HARD gates red on the working tree and green at
HEAD, every one introduced by the same uncommitted batch. IMP-0286 and IMP-0307 are the same
mechanism at a different gate, two dispatches apart, patched at the time by naming two scripts in
agents/development-agent.md — which is why this tool DERIVES the list instead of carrying one.

WHAT IT SELECTS, AND WHY THAT RULE
----------------------------------
A step qualifies when BOTH hold:

  1. its command names a solution source root (`src/solutions/<Name>`), and
  2. every tool its command invokes is on a FAIL-CLOSED allowlist — `grep` (any of its spellings),
     `echo`, and `python3 scripts/verify-*.py`. A step invoking any other tool is excluded, so a
     command shape nobody has enumerated is left OUT rather than swept in.

Measured against config/revitalise-grant-automation-build.yml, adjudicating every candidate by
hand. 18 of the 73 steps name a solution root; the table is the choice of rule over those 18:

  * inputs-exist-on-disk heuristic ....... 67 of 73 steps, ~55 relevant — REJECTED. It sweeps in
                                           `pac solution pack`, `npm ci`, `npm run build`, the
                                           Pester install and the Playwright install: network,
                                           auth and multi-minute steps
  * any `verify-*.py` step, no path ...... 13 + 22 steps — REJECTED by improvement review 5. It
                                           sweeps in `improvement-log-check`, which is red by
                                           design whenever any blocker is open
  * names the solution root, ANY tool .... 18 steps, 16 relevant — the 2 false positives are the
                                           `pac solution pack` steps: network, auth, minutes
  * SOLUTION ROOT + tool allowlist ....... 16 steps, 16 relevant, 0 false positives, ~20 seconds,
    (this tool, 2026-09-08)                no authentication, no writes

Until 2026-09-08 condition 2 read "invokes `scripts/verify-*.py`", which selected 13 and silently
dropped the three HARD inverted-`grep` checks over solution source
(`no-special-category-data-in-scoring`, `no-hardcoded-environment-values`,
`no-hardcoded-thresholds` — 0.03 seconds for all three). IMP-0658 is the blocker that cost: an
authoring dispatch ran this tool, got 13 of 13 green, and handed off source that
`no-hardcoded-environment-values` rejected at build step 46. The gate shape, not the gate's
subject matter, was the whole of the gap — which is why condition 2 is now about what a command
COSTS to run rather than what it is named.

RESIDUAL, stated because every promotion leaves one, and now PRINTED rather than only documented.
The selection is scoped to the SOLUTION source root, so a gate reading only src/code-apps/ or
provisioning/, or one taking no path at all (`verify-assumption-register.py`), is outside it and
still waits for the build. That is why every run ends with a `NOT covered by this run` list: this
tool reports 16 of 73 steps, never "the source is clean". A green run here is a statement about
16 named gates and nothing else.

This is NOT itself a gate: it invokes gates the build already invokes, so wiring it as a build
step would run all 16 twice. It is deliberately named outside the `verify-*` convention and
exposes no generator-style verification mode, which is what keeps
scripts/verify-build-config.py's suite-gate rung from requiring a step for it.

USAGE
    python3 scripts/run-source-gates.py config/<slug>-build.yml
    python3 scripts/run-source-gates.py config/<slug>-build.yml --list
    python3 scripts/run-source-gates.py --selftest

EXIT CODES
    0  every selected gate passed
    1  at least one selected gate failed, or no gate was selected (the IMP-0007 shape: a runner
       reporting success over an empty set)
    2  usage error
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

GATE_RE = re.compile(r"scripts/verify-[\w.-]+\.py")
SOLUTION_RE = re.compile(r"src/solutions/[A-Za-z0-9_.-]+")

# Fail-closed: a tool absent from this set disqualifies the step. Everything here is a local,
# read-only, sub-second-to-~20-second invocation that needs no network and no authentication.
# `python3` qualifies only when the segment invoking it also matches GATE_RE.
CHEAP_TOOLS = {"grep", "egrep", "fgrep", "echo", "true", ":"}
PYTHON_TOOLS = {"python", "python3"}

STEP_TIMEOUT_SECONDS = 600


def split_segments(command: str) -> list[str]:
    """Split a shell command on `&&`, `||`, `|`, `;` and newlines, respecting quotes.

    Quote-awareness is the load-bearing part: several of the checks this selects are
    `grep -rnE 'a|b|c'`, whose alternation would otherwise be read as a pipeline.
    """
    segments, current, quote = [], [], ""
    i = 0
    while i < len(command):
        ch = command[i]
        if quote:
            current.append(ch)
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            current.append(ch)
            i += 1
            continue
        if command.startswith("&&", i) or command.startswith("||", i):
            segments.append("".join(current))
            current = []
            i += 2
            continue
        if ch in "|;\n":
            segments.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    segments.append("".join(current))
    return [s.strip() for s in segments if s.strip()]


def is_cheap_local_check(command: str) -> bool:
    """True when EVERY tool the command invokes is on the allowlist. Fail-closed by design."""
    segments = split_segments(command)
    if not segments:
        return False
    for segment in segments:
        segment = segment.lstrip("!( \t")
        if not segment:
            return False
        tool = segment.split()[0].rsplit("/", 1)[-1]
        if tool in CHEAP_TOOLS:
            continue
        if tool in PYTHON_TOOLS and GATE_RE.search(segment):
            continue
        return False
    return True


def load_steps(config_path: Path) -> list[dict]:
    try:
        import yaml
    except ImportError:  # pragma: no cover - environment guarantee
        print("run-source-gates: PyYAML is required.", file=sys.stderr)
        raise SystemExit(2)
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"run-source-gates: cannot read {config_path}: {exc}", file=sys.stderr)
        raise SystemExit(2)
    steps = (config or {}).get("steps") or []
    if not isinstance(steps, list):
        print(f"run-source-gates: {config_path} has no list of steps.", file=sys.stderr)
        raise SystemExit(2)
    return [s for s in steps if isinstance(s, dict)]


def select(steps: list[dict]) -> list[dict]:
    """The two-part rule the module docstring measures. Both halves are load-bearing."""
    chosen = []
    for step in steps:
        command = step.get("command") or ""
        if SOLUTION_RE.search(command) and is_cheap_local_check(command):
            chosen.append(step)
    return chosen


def report_uncovered(steps: list[dict], selected: list[dict]) -> None:
    """Print every step this run did NOT execute.

    IMP-0658: a runner that prints only its passes reads as complete coverage of the source,
    and the dispatch that read it that way handed off source a 0.03-second grep would have
    rejected. The list is deliberately unfiltered — this build config carries no machine-readable
    severity field (SOFT is expressed in YAML comments and by a step's own `--warn-only` flag),
    so no honest filter to "HARD steps only" exists here. Naming all of them says less than a
    severity-filtered list would, and says only true things.
    """
    chosen = {id(s) for s in selected}
    uncovered = [str(s.get("name", "<unnamed>")) for s in steps if id(s) not in chosen]
    print(f"NOT covered by this run — {len(uncovered)} of {len(steps)} build step(s). A green run "
          f"above is a statement about {len(selected)} named gates, not about the source:")
    line = "   "
    for name in uncovered:
        if len(line) + len(name) + 2 > 96:
            print(line.rstrip().rstrip(","))
            line = "   "
        line += f" {name},"
    if line.strip():
        print(line.rstrip().rstrip(","))
    print()


def run(selected: list[dict], repo_root: Path) -> int:
    width = max((len(str(s.get("name", "?"))) for s in selected), default=1)
    failures: list[str] = []
    for step in selected:
        name = str(step.get("name", "<unnamed>"))
        completed = subprocess.run(
            step["command"], shell=True, cwd=repo_root,
            capture_output=True, text=True, timeout=STEP_TIMEOUT_SECONDS,
        )
        status = "PASS" if completed.returncode == 0 else "FAIL"
        print(f"  {status}  {name:<{width}}  (exit {completed.returncode})")
        if completed.returncode != 0:
            failures.append(name)
            tail = (completed.stdout + completed.stderr).strip().splitlines()
            for line in tail[-6:]:
                print(f"        {line}")
    print()
    if failures:
        print(f"run-source-gates: FAILED — {len(failures)} of {len(selected)} source gate(s) "
              f"red: {', '.join(failures)}.")
        print("  These are HARD build steps. A build dispatched now halts on the first of them.")
        return 1
    print(f"run-source-gates: OK — {len(selected)} source gate(s) pass. This is V1 "
          "(well-formed source); packaging, import and runtime are not proven by it.")
    return 0


def selftest() -> int:
    """Prove the selection rule discriminates AND that a red gate propagates.

    Fixtures are synthetic and self-contained: each `command` carries a path-shaped token that
    the two regexes match, while what actually executes is a trivial interpreter call. That
    separation is the point — it tests THIS file's logic, not the repository's gates.
    """
    failures: list[str] = []

    passing = "python3 -c pass  # scripts/verify-fixture.py src/solutions/Fixture"
    failing = "python3 -c 'import sys; sys.exit(1)'  # scripts/verify-fixture.py src/solutions/Fixture"
    cases = [
        ("selects a gate naming a solution root", [{"name": "a", "command": passing}], 1),
        ("rejects a gate naming no solution root",
         [{"name": "a", "command": "python3 scripts/verify-thing.py docs/"}], 0),
        ("rejects a solution-naming step that invokes an unlisted tool (pac)",
         [{"name": "a", "command": "pac solution pack --folder src/solutions/Fixture"}], 0),
        ("selects an inverted-grep check over the solution",
         [{"name": "a", "command": "! grep -rn 'x' src/solutions/Fixture"}], 1),
        ("selects an inverted grep whose pattern contains a pipe, and its trailing echo",
         [{"name": "a", "command": "! grep -rnE 'a|b' src/solutions/Fixture && echo 'clean'"}], 1),
        ("fail-closed: rejects a grep chained into an unlisted tool",
         [{"name": "a", "command": "grep -rn 'x' src/solutions/Fixture | npx sometool"}], 0),
        ("fail-closed: rejects a python invocation that is not a verify-*.py gate",
         [{"name": "a", "command": "python3 tools/other.py src/solutions/Fixture"}], 0),
        ("rejects a cheap check naming no solution root",
         [{"name": "a", "command": "! grep -rn 'x' docs/"}], 0),
    ]
    for label, steps, expected in cases:
        got = len(select(steps))
        if got != expected:
            failures.append(f"{label}: expected {expected} selected, got {got}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        if run([{"name": "green", "command": passing}], root) != 0:
            failures.append("a passing gate did not produce exit 0")
        if run([{"name": "red", "command": failing}], root) != 1:
            failures.append("a failing gate did not produce exit 1 — THIS GATE CANNOT FAIL")

    for line in failures:
        print(f"  selftest FAIL: {line}")
    if failures:
        print(f"run-source-gates: SELFTEST FAILED — {len(failures)} case(s).")
        return 1
    print(f"run-source-gates: selftest OK — {len(cases) + 2} case(s), including the negative "
          "case proving a red gate propagates.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the source-only build gates for a feature, ahead of any build.")
    parser.add_argument("config", nargs="?", help="path to config/<slug>-build.yml")
    parser.add_argument("--list", action="store_true",
                        help="print the selected gates without running them")
    parser.add_argument("--selftest", action="store_true",
                        help="prove the selection rule and the failure path")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if not args.config:
        parser.print_usage(sys.stderr)
        print("run-source-gates: a build config path is required.", file=sys.stderr)
        return 2

    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"run-source-gates: {config_path} does not exist.", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parent.parent
    steps = load_steps(config_path)
    selected = select(steps)

    if not selected:
        print(f"run-source-gates: NO source gate selected from {config_path}. Either the config "
              f"invokes no `scripts/verify-*.py` against a `src/solutions/<Name>` path, or the "
              f"convention this selection rests on has changed. Reporting OK here would be a "
              f"runner passing over an empty set.")
        return 1

    print(f"run-source-gates: {len(selected)} source gate(s) of {len(steps)} build step(s) "
          f"from {config_path}\n")
    if args.list:
        for step in selected:
            print(f"  {step.get('name')}\n      {step.get('command','').strip()}")
        print()
        report_uncovered(steps, selected)
        return 0
    exit_code = run(selected, repo_root)
    report_uncovered(steps, selected)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
