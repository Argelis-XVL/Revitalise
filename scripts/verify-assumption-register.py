#!/usr/bin/env python3
"""An Unvalidated Assumptions Register row must not stay open after its own document closes it.

WHY THIS EXISTS. Four stale rows in two days, in one register, every one found by accident while
doing something else:

  * `A-TR-12` — row said *"E2 · Compare against the host's own behaviour on first paint"*; closed
    from the installed SDK's `.d.ts`.
  * `A-TR-6`  — row said *"E4 · Re-run after the next DEV import"*, while §11 of the same document
    recorded the closure **twice** and stated *"no register change needed"*.
  * `A-TR-10` — row said *"E3 · Save a verdict against DEV"*; closed by a live positive/negative
    control pair that is quoted four screens further down.
  * `A-TR-7`  — row said *"E3 · Log the returned payload against DEV"*; closed the same day.

`C-TECH-052` makes the register the tracking mechanism for every hand-authored guess, and
`IMP-0014` is what an OPEN row costs: *"an Unvalidated Assumptions Register row that is still OPEN
is a prediction of a live defect, not paperwork."* So a register that says OPEN about settled work
is not a tidy-up problem — it is the tracker crying wolf, and the next reader either re-does closed
verification or learns to skim the register. `IMP-0014`'s whole point stops working.

The failure is always the same shape and always one-directional: **the narrative gets updated and
the table does not.** Nobody edits a 5,000-line document's summary and its register in one pass, and
nothing has ever compared them.

THE ALTITUDE CALL. Third instance of the class (`hand-maintained-count-drifts-from-source`, x4 —
`IMP-0150`, `IMP-0160`, `IMP-0176`, `IMP-0198`, and this is the same property applied to a STATUS
rather than a number), so per `skills/how-to-promote-a-finding.md` §2 it may not get another
per-row correction. The generalisable property:

    A register row's status and its own document's narrative are two statements of one fact,
    and only the row is authoritative for readers.

WHAT IT DOES NOT COVER. It compares a row against **claims in the same document**. A row closed by
evidence recorded somewhere else entirely — a test report, a deployment summary, a commit message —
is invisible here, and that is the honest limit rather than an oversight: the check would need to
read the whole repository to find it, and a closure worth trusting is worth recording where the
register is. The inverse case (a row marked CLOSED that the document never evidences) is REPORTED,
never failed, because closure evidence legitimately lives in linked documents.

Run:
    python3 scripts/verify-assumption-register.py
    python3 scripts/verify-assumption-register.py --selftest

Exits 0 when every register row agrees with its own document, 1 on any disagreement, 2 on a usage
error. Fails — never passes — when it finds no register or no rows (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCAN_GLOBS = ("docs/development/*.md", "docs/architecture/*.md", "docs/tests/*.md")

REGISTER_HEADING = re.compile(
    r"^(?P<hashes>#{1,6})\s+.*Unvalidated Assumptions Register", re.IGNORECASE)
ANY_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+")

# A register row's first cell is the assumption id: A-001, A-TR-12, A-TRM-2, A-G01.
ROW_ID = re.compile(r"^\|\s*(?P<struck>~~)?\s*(?P<id>A-[A-Z]{0,4}-?\d+)\s*(?:~~)?\s*\|")

ASSUMPTION_ID = re.compile(r"A-[A-Z]{0,4}-?\d+")

# "A-TR-10 CLOSED", "**A-TR-7 CLOSED**", "A-TR-6 | **CLOSED** — …", "A-001 closed above".
#
# The window is deliberately small AND filtered, because the first draft of this check produced
# two false positives on one real line:
#
#   "A-TR-1, A-TR-4, A-TR-5, A-TR-8, A-TR-9, A-TR-11 remain OPEN (A-TR-12 was closed …)"
#
# A naive "<id> … CLOSED within N characters" matched `A-TR-1` against A-TR-12's `closed`, and
# reported two settled-looking rows that are genuinely open — the exact opposite of this gate's
# purpose, and the direction that would teach people to ignore it. So a claim only counts when
# nothing between the id and the word CLOSED is another assumption id or a negation.
CLOSED_WINDOW = 90
NEGATORS = ("open", "remain", "not ", "unless", "until", "would", "if ")


def closure_claims(text: str) -> dict[str, int]:
    """Every "<id> … CLOSED" claim in `text`, mapped to its 0-based line number."""
    found: dict[str, int] = {}
    for m in ASSUMPTION_ID.finditer(text):
        ident = m.group(0)
        window = text[m.end():m.end() + CLOSED_WINDOW]
        window = window.split("\n")[0]
        low = window.lower()
        idx = low.find("closed")
        if idx == -1:
            continue
        gap = window[:idx]
        if ASSUMPTION_ID.search(gap):
            continue                       # the CLOSED belongs to a later id, not this one
        if any(neg in gap.lower() for neg in NEGATORS):
            continue                       # "remain OPEN", "not closed", "would be closed"
        found.setdefault(ident, text[:m.start()].count("\n"))
    return found

# A row is RESOLVED however its author chose to word it. Widened 2026-08-23 after A-001 was
# reported stale: that row is fully resolved and says so at length — "**CORRECTED 2026-08-16.** The
# guess was **wrong** … Real classid obtained as genuine E1 ground truth …" — but never uses the
# word "closed". A guess that turned out wrong is CORRECTED, not closed, and insisting on one
# vocabulary would have made the gate wrong about a row that is a model of how to record a
# closure.
#
# The trade-off is deliberate and one-directional: a wider marker list risks MISSING a stale row
# (a false negative) rather than flagging a settled one (a false positive). A gate that is wrong
# in the loud direction is a gate people switch off, and this one exists to be read.
CLOSED_MARKERS = ("closed", "~~", "corrected", "resolved", "superseded", "withdrawn",
                  "no longer applies")


def register_spans(lines: list[str]) -> list[tuple[int, int]]:
    """Line ranges (0-based, end-exclusive) of every assumptions-register section."""
    spans: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        m = REGISTER_HEADING.match(line)
        if not m:
            continue
        depth = len(m.group("hashes"))
        end = len(lines)
        for j in range(i + 1, len(lines)):
            h = ANY_HEADING.match(lines[j])
            if h and len(h.group("hashes")) <= depth:
                end = j
                break
        spans.append((i, end))
    return spans


def row_is_closed(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in CLOSED_MARKERS)


def scan(repo_root: Path) -> tuple[list[str], list[str], dict[str, int]]:
    failures: list[str] = []
    notes: list[str] = []
    counts = {"files": 0, "registers": 0, "rows": 0, "open_rows": 0}

    seen: set[Path] = set()
    for pattern in SCAN_GLOBS:
        for path in sorted(repo_root.glob(pattern)):
            if path in seen or not path.is_file():
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            lines = text.splitlines()
            spans = register_spans(lines)
            if not spans:
                continue
            counts["files"] += 1
            counts["registers"] += len(spans)
            rel = path.relative_to(repo_root).as_posix()

            register_line_range = {n for start, end in spans for n in range(start, end)}

            # Every "<id> … CLOSED" claim OUTSIDE the register sections, with its line number.
            closed_elsewhere: dict[str, int] = {}
            for ident, line_no in closure_claims(text).items():
                if line_no in register_line_range:
                    continue
                closed_elsewhere[ident] = line_no + 1

            for start, end in spans:
                for n in range(start, end):
                    rm = ROW_ID.match(lines[n])
                    if not rm:
                        continue
                    counts["rows"] += 1
                    ident = rm.group("id")
                    if row_is_closed(lines[n]):
                        if ident not in closed_elsewhere:
                            notes.append(
                                f"{rel}:{n + 1}: {ident} is marked closed in the register and this "
                                f"document does not say so anywhere else. Reported, not failed — "
                                f"the evidence may legitimately live in a linked document.")
                        continue
                    counts["open_rows"] += 1
                    if ident in closed_elsewhere:
                        failures.append(
                            f"{rel}:{n + 1}: {ident}'s register row still reads as OPEN, but line "
                            f"{closed_elsewhere[ident]} of the same document says it is CLOSED. "
                            f"The row is what readers act on, and an open row is a prediction of a "
                            f"live defect (IMP-0014, C-TECH-052) — so a stale one sends somebody "
                            f"to re-verify settled work, or teaches them to skim the register. "
                            f"Strike the row through and record what closed it.")
    return failures, notes, counts


def selftest() -> int:
    import tempfile

    def doc(register_row: str, narrative: str) -> str:
        return (
            "# Dev Summary\n\n"
            "### §10 Unvalidated Assumptions Register\n\n"
            "| Id | Assumption | Evidence | How to close |\n|---|---|---|---|\n"
            f"{register_row}\n\n"
            "### §11 Verification Evidence\n\n"
            f"{narrative}\n")

    cases = [
        ("a stale open row whose document says CLOSED is caught",
         "| A-TR-10 | the guard | E3 | Save a verdict against DEV |",
         "3. **A-TR-10 CLOSED** — proven live.", True),
        ("a struck-through row is not a failure",
         "| ~~A-TR-10~~ | ~~the guard~~ **CLOSED (E1)** | E1 | closed live |",
         "3. **A-TR-10 CLOSED** — proven live.", False),
        ("a row saying CLOSED inline is not a failure",
         "| A-TR-10 | the guard — CLOSED | E1 | closed live |",
         "3. **A-TR-10 CLOSED** — proven live.", False),
        ("a genuinely open row with no closure claim passes",
         "| A-TR-11 | something unproven | E3 | run it against DEV |",
         "Nothing closed this dispatch.", False),
        ("a closure claim INSIDE the register does not count as narrative",
         "| A-TR-10 | the guard | E3 | Save a verdict against DEV |",
         "Unrelated prose with no ids.", False),
        # The two false positives the first draft produced on one real line.
        ("an id in a 'remain OPEN' list is not closed by a LATER id's closure",
         "| A-TR-1 | the baseline | E3 | sign in as a trustee |",
         "6. **A-TR-1, A-TR-4, A-TR-11 remain OPEN** (A-TR-12 was closed 2026-08-22).", False),
        ("'not closed' / 'would be closed' do not count as closure",
         "| A-TR-4 | something | E3 | run it |",
         "A-TR-4 is not closed yet, and would be closed by a live run.", False),
        ("a plain 'A-nnn closed above' still counts",
         "| A-001 | the classid | E2 | open it in the designer |",
         "**Severity:** P2, now CLOSED. **Register:** A-001 closed above.", True),
        # A-001's real shape: resolved at length, in the row, without the word "closed".
        ("a row resolved as CORRECTED is not stale, even though it never says 'closed'",
         "| A-001 | the classid | E2 | open it | **CORRECTED 2026-08-16.** The guess was wrong; "
         "real classid read back from the platform. |",
         "**Severity:** P2, now CLOSED. **Register:** A-001 closed above.", False),
    ]

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for why, row, narrative, expect_fail in cases:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "docs" / "development").mkdir(parents=True)
            (root / "docs" / "development" / "s.md").write_text(doc(row, narrative),
                                                               encoding="utf-8")
            failures, _notes, counts = scan(root)
            got = bool(failures)
            ok = got == expect_fail
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(failures)} failure(s) over "
                  f"{counts['rows']} row(s) in {counts['registers']} register(s)")
            if not ok:
                for f in failures:
                    print(f"          {f}")
                failed += 1

    # The IMP-0007 control: a document set with no register at all yields nothing to check.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs" / "development").mkdir(parents=True)
        (root / "docs" / "development" / "s.md").write_text("# No register here\n", encoding="utf-8")
        _f, _n, counts = scan(root)
        ok = counts["registers"] == 0 and counts["rows"] == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  a document set with no register yields zero rows "
              f"(caller must fail, not pass): registers={counts['registers']}")
        failed += 0 if ok else 1

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="An assumptions-register row must agree with its own document's narrative.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]
    failures, notes, counts = scan(repo_root)

    if counts["registers"] == 0 or counts["rows"] == 0:
        print(f"ERROR: found {counts['registers']} assumptions register(s) and "
              f"{counts['rows']} row(s) across {SCAN_GLOBS}. C-TECH-052 requires a register per "
              f"feature with a row per guessed contract, so finding none means either the "
              f"register is gone or the heading/row patterns stopped matching. A checker with no "
              f"inputs must fail rather than report PASS (IMP-0007).", file=sys.stderr)
        return 1

    for note in notes:
        print(f"NOTE: {note}")

    if failures:
        for f in failures:
            print(f"ERROR: {f}", file=sys.stderr)
        print(f"\nASSUMPTION REGISTER: FAILED — {len(failures)} stale row(s) of "
              f"{counts['open_rows']} open, across {counts['registers']} register(s) in "
              f"{counts['files']} document(s).", file=sys.stderr)
        return 1

    print(f"ASSUMPTION REGISTER: PASS — {counts['rows']} row(s) across {counts['registers']} "
          f"register(s) in {counts['files']} document(s); {counts['open_rows']} still open, and "
          f"none of them is contradicted by its own document.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
