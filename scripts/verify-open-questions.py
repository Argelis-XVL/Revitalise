#!/usr/bin/env python3
"""SOFT gate: an SDD open question is not due at a moment no gate can observe.

WHAT WENT WRONG. `OQ-151` asked the business what nickname convention satisfies a High-priority
requirement whose own ADR says *the convention IS the control*. It was dated **"Before build"**.
The build happened with it open and shipped a column description whose two worked examples were
both the wrong payee type — so the requirement shipped with a convention stated only for the case
it was not written for.

"Before build" is a date with no mechanism behind it: nothing reads the open-question table, and
no build step fails on an open question naming the feature being built. And it was the **wrong
event anyway** — the exposure that question guards becomes live when a deploy grants a persona
Read on the table, not when a form is packed (`IMP-0711`).

WHAT THIS CHECKS, AND WHY IT IS DELIBERATELY NARROW. It reports an open question whose due cell is
an **exact member of a small declared set of known non-events**. Nothing more.

THE DESIGN THAT WAS MEASURED AND REJECTED, because the next author will otherwise rebuild it.
The obvious check is "does the due cell name a specific enough event" — implemented as "does it
anchor to a WBS task id, an ISO date, a gate keyword or a named artefact". Measured over the real
corpus at application time: **51 open questions across 4 plans, of which 25 (49%) would be
reported** — and most of those are legitimate project events that simply carry no task id:
*"Before go-live"*, *"At environment setup"*, *"Before procurement"*, *"At TAD stage"*. A gate
reporting half its corpus, mostly wrongly, is the instrument this repository has measured at
48-100% false **five** times (`IMP-0422`, `IMP-0428`).

So this asserts on **exact membership of a closed set**, which is decidable and cannot
false-positive, instead of on specificity, which is a judgement. Measured on the same corpus:
**5 findings, 5 true positives.**

THE RESIDUAL, stated because it is real: exact matching hands an author an escape hatch — rename
the cell to *"at build stage"* and this goes quiet without the question becoming any better dated.
That is why the rule itself lives in `agents/plan-agent.md`, where the author reads it before
writing, and why the finding message below states the good form rather than only the bad one.
This gate is the floor, not the rule.

Run:
    python3 scripts/verify-open-questions.py                 # report
    python3 scripts/verify-open-questions.py --warn-only     # always exit 0 (build step)
    python3 scripts/verify-open-questions.py --selftest       # prove both polarities
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_GLOB = "docs/plans/*-plan.md"

OQ_ROW = re.compile(r"^(?:\*\*)?~*\s*(OQ-\d+)")

# Exact, normalised values that name no observable event. Extend this list only with a value
# measured in the corpus — never with a pattern, which is how this becomes a phrase gate.
KNOWN_NON_EVENTS = frozenset({
    "before build",
    "before build starts",
    "before development",
    "before development starts",
    "before dev",
    "tbd",
    "tbc",
    "asap",
})

# A row whose status cell says the question is settled is out of scope: a closed question's due
# date is history, and re-dating it would rewrite the record.
CLOSED_WORDS = ("CLOSED", "RESOLVED", "ANSWERED", "WITHDRAWN", "SUPERSEDED", "n/a")


def normalise(cell: str) -> str:
    """Strip markdown emphasis, links and punctuation so an exact set match is meaningful."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)      # links -> their text
    s = s.replace("*", "").replace("`", "").replace("~", "")
    s = s.strip().strip(".").strip()
    return " ".join(s.lower().split())


def row_is_closed(cells: list[str]) -> bool:
    joined = " ".join(cells).upper()
    return any(w.upper() in joined for w in CLOSED_WORDS)


def scan(repo_root: Path) -> tuple[list[str], int, int]:
    """Return (findings, rows_inspected, plans_inspected)."""
    findings: list[str] = []
    rows = plans = 0
    for plan in sorted(repo_root.glob(PLAN_GLOB)):
        plans += 1
        for n, line in enumerate(plan.read_text(encoding="utf-8",
                                                errors="ignore").splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells:
                continue
            m = OQ_ROW.match(cells[0])
            if not m:
                continue
            rows += 1
            if row_is_closed(cells):
                continue
            due = normalise(cells[-1])
            if due in KNOWN_NON_EVENTS:
                rel = plan.relative_to(repo_root)
                findings.append(
                    f"{rel}:{n}: {m.group(1)} is due {cells[-1].strip()!r}, which names no "
                    f"observable event — no gate reads it, and it is usually the wrong moment "
                    f"anyway. Date it against the EVENT that makes the answer load-bearing: the "
                    f"deploy that grants the privilege, the run that first reads the value, a "
                    f"WBS task id, or a dated gate. If the answer must ship before the owner has "
                    f"decided, state the architecturally-derived DEFAULT, narrow the question to "
                    f"confirm-or-replace, and re-date it (IMP-0711).")
    return findings, rows, plans


def selftest() -> int:
    failures: list[str] = []
    import tempfile

    def run(body: str) -> list[str]:
        d = Path(tempfile.mkdtemp())
        (d / "docs" / "plans").mkdir(parents=True)
        (d / "docs" / "plans" / "x-plan.md").write_text(body, encoding="utf-8")
        return scan(d)[0]

    header = "| Id | Question | Owner | Due |\n|---|---|---|---|\n"

    # FIRES: the exact phrase that caused the incident, plain and emphasised.
    if len(run(header + "| OQ-1 | q | o | Before build |\n")) != 1:
        failures.append("a plain 'Before build' must be reported")
    if len(run(header + "| OQ-2 | q | o | **Before build starts** |\n")) != 1:
        failures.append("markdown emphasis must not hide a known non-event")

    # DOES NOT FIRE: a real event, however unspecific it looks to a human.
    for ok in ("Before go-live", "At environment setup", "Before WBS 6.9 build",
               "2026-10-01", "Before DPIA sign-off", "APPROVE PRD"):
        if run(header + f"| OQ-3 | q | o | {ok} |\n"):
            failures.append(f"{ok!r} names an event and must NOT be reported")

    # DOES NOT FIRE: a closed question's due date is history.
    if run(header + "| OQ-4 | q | o | CLOSED 2026-01-01 — answered | Before build |\n"):
        failures.append("a closed question must be out of scope")

    # A non-table line, and a table that is not an OQ table, must be ignored.
    if run("just prose\n\n| Not | An | OQ | Before build |\n"):
        failures.append("a non-OQ table row must be ignored")

    # Rows must actually be counted, or this gate could pass over nothing (IMP-0007).
    d = Path(tempfile.mkdtemp())
    (d / "docs" / "plans").mkdir(parents=True)
    (d / "docs" / "plans" / "x-plan.md").write_text(
        header + "| OQ-9 | q | o | Before go-live |\n", encoding="utf-8")
    if scan(d)[1] != 1:
        failures.append("an inspected row must be counted")

    for f in failures:
        print(f"  FAIL  {f}")
    if failures:
        print(f"verify-open-questions --selftest: FAILED — {len(failures)} failure(s)")
        return 1
    print("verify-open-questions --selftest: PASS (11 checks: both polarities, emphasis "
          "stripping, closed rows out of scope, row counting)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--warn-only", action="store_true",
                   help="report and exit 0 (how this is wired as a build step)")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()

    findings, rows, plans = scan(REPO_ROOT)

    if rows == 0:
        print("verify-open-questions: inspected ZERO open-question rows across "
              f"{plans} plan(s). Either no plan keeps an open-question table, or the table "
              "shape changed and OQ_ROW stopped matching. A checker that checks nothing must "
              "say so (IMP-0007).", file=sys.stderr)
        return 0 if a.warn_only else 1

    for f in findings:
        print(f"WARN: {f}", file=sys.stderr)

    verdict = (f"{len(findings)} open question(s) due at a non-event"
               if findings else "every open question is dated against an observable event")
    print(f"OPEN QUESTIONS: {verdict} — {rows} row(s) inspected across {plans} plan(s).")
    return 0 if (a.warn_only or not findings) else 1


if __name__ == "__main__":
    sys.exit(main())
