#!/usr/bin/env python3
"""Assert that every OPEN Unvalidated Assumptions Register row carries its marker in source.

WHY IT IS NOT CALLED `verify-assumption-register.py`. Improvement review 27 proposed exactly that
name, and that file already existed — a HARD gate wired at build step `assumption-register` since
2026-08-23 (`IMP-0211`) checking a DIFFERENT half of the same constraint. Writing this script to
the approved filename destroyed 312 lines of working, wired gate, and the only reason it was
noticed is that the build config already named a step for it. See `IMP-0296`. The two are
deliberately separate files:

  * `verify-assumption-register.py` — a row's STATUS must not contradict its own document's
    narrative. Its `row_is_closed()` reads the whole row line for a closure word, which is loose
    on purpose: it prefers missing a stale row to shouting about a settled one.
  * this script — an OPEN row must carry its `A-nnn` marker in the source its *Where* column
    names. It reads the Status COLUMN specifically, because the looser whole-line read is wrong
    here: `A-FIN-05`'s row says *"Cannot be closed in DEV"* in its *How to close it* cell, so a
    whole-line read calls that row closed and silently skips a genuine orphan.

They are not merged because reusing either status reader for the other's question loses coverage
in the quiet direction, which is the `gate-cannot-fail` shape this project has recorded 32 times.

WHY THIS EXISTS AT ALL. `C-TECH-052` is HARD and has two halves. The first — *a guessed platform
contract is recorded as a row in Dev Summary §10* — has been kept faithfully. The second — *and
carries an `A-nnn` comment at the point of the guess in source* — was enforced by a sentence in
the constraint's own `Verify By` column naming a **human**:

    "test-agent cross-checks the register against the hand-authored artefacts and reports orphan
     guesses as a defect."

A HARD rule whose enforcement is whether a session remembers to grep is the shape of `IMP-0165`
and `IMP-0174`, both blockers, both in the class
`declared-policy-not-mechanically-enforced`. `IMP-0286` is instance 8: `A-FIN-07` was added on
2026-08-24 naming `ensure-auditing.ps1#L171` as *Where*, and no `A-FIN` string existed anywhere
in that file. Its sibling `A-FIN-06`, added the same day from the same pattern, does carry its
marker. The difference was that one session happened to grep.

WHAT THE ROW'S "Where" COLUMN IS FOR. It is a claim about source: *this is the line the guess is
made at*. A register row is the system's memory of an unproven assumption, and the marker is what
makes that memory reachable from the code — the next author of that line learns it is a guess by
reading the line, not by knowing the register exists. A row whose marker is missing is a register
entry the code cannot see.

WHAT IT CHECKS.

  For every register row whose CURRENT status is not closed, resolve the *Where* column to one or
  more real files and require the row's own id (`A-002`, `A-FIN-07`, `A-TR-4`, …) to appear
  somewhere in at least one of them.

  "CURRENT status" matters, and it is why this reads the whole document rather than one table.
  This register is maintained by APPENDING an update table, not by editing the original row:
  `A-FIN-04`'s original row at §10 still reads `**OPEN**`, and a three-column update table 80
  lines later reads `**CLOSED — WRONG**`. The last row that names an id in a table that has a
  Status column is the truth about that id.

WHAT COUNTS AS CLOSED. `CLOSED`, `VERIFIED`, `CORRECTED`, `RESOLVED`, `WITHDRAWN`, `n/a`. Anything
else — including a word nobody has used yet — is read as OPEN. That direction is deliberate: an
unrecognised status produces a demand for a marker, which is noisy and safe, rather than a silent
skip, which is the `gate-cannot-fail` shape this repository has recorded 32 times. The first draft
of this script had `VERIFIED` missing from that list and reported `A-FIN-03` — closed at V3
against a live org — as an orphan. That false positive is now a fixture.

TWO EXEMPTIONS, BOTH REPORTED RATHER THAN SILENT. A file this project cannot put a durable
comment in cannot be asked for a marker:

  * **`environmentvariabledefinitions/` — a platform law.** Such a file may not carry a comment at
    all. `IMP-0045` records four consecutive solution imports failing with `0x80040216` at
    `ImportXml.GetComponentsList`, naming no component, because one carried this project's ordinary
    header comment; `pac solution pack` exits 0 and the file stays valid XML, so nothing below a
    real import can see it. Demanding the marker there would be this gate breaking the build it is
    defending. Everywhere ELSE in `src/solutions/` a comment is fine and already carries markers
    today (`Other/Solution.xml`, `Other/FieldSecurityProfiles.xml`,
    `Other/Relationships/rev_provider.xml`, `Roles/REV Trustee/REV Trustee.xml`).
  * **`src/generated/` and `.power/` — generator output.** A marker written there is discarded the
    next time the generator runs. A row whose *Where* names a generated file alongside an authored
    one is still checked against the authored one; only an all-generated row is exempt.

WHAT IT CANNOT SEE — the residual, stated because a gate without one is a false sense of one.

  * **It greps the FILE, not the LINE.** A marker sitting in a header comment while the guess is
    made 400 lines below passes. Checking the line would mean tracking a line number across every
    edit to the file, which is a worse failure mode than this one.
  * **A *Where* column that names no resolvable file is reported as UNRESOLVED, not as a
    failure.** Some rows describe their location in prose ("see links"). Those are counted and
    named in the output so the silence is visible, but they do not fail the gate.
  * **It does not check the converse** — a marker in source with no register row. That is the
    opposite defect and nobody has met it.
  * **It says nothing about whether the assumption is TRUE.** That is what the row's *How to
    close it* column is for, and closing it needs a live environment.

Run:
    python3 scripts/verify-assumption-markers.py
    python3 scripts/verify-assumption-markers.py --selftest

Exits 0 when clean, 1 on any orphan, 2 on a usage error. Fails — never passes — when it finds ZERO
register rows to inspect, because a checker that checks nothing must not report PASS (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCAN_GLOBS = ("docs/development/*.md",)

# A register row's id. `A-001`, `A-FIN-07`, `A-TR-12`.
ROW_ID = re.compile(r"^(~~)?\s*(A-(?:[A-Z]{2,4}-)?\d{1,3})\s*(~~)?$")

# Header cells that carry the two things this gate reads. "Where" also matches "Where in source";
# "Status" also matches "Status this dispatch".
WHERE_HEADER = re.compile(r"^where\b", re.IGNORECASE)
STATUS_HEADER = re.compile(r"^status\b", re.IGNORECASE)

# `[`ensure-auditing.ps1#L171`](provisioning/dataverse/ensure-auditing.ps1#L171)`
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
# A bare repo path inside a code span: `` `OptionSets/rev_conditionprofile.xml` ``
CODE_SPAN = re.compile(r"`([^`]+)`")
PATHISH = re.compile(
    r"^[\w./\-{} ]+\.(?:ps1|psm1|py|md|xml|json|ts|tsx|js|yml|yaml)(?::\d+(?:-\d+)?)?$")
# Three ways this register points at a line, all of which are noise to a file lookup:
# `#L171`, `:279-292`, `:6-25`.
LINE_SUFFIX = re.compile(r"(?:#L?\d+(?:-L?\d+)?|:\d+(?:-\d+)?)$")

# A status is closed when it says so. Everything else is read as OPEN — see the module docstring.
CLOSED_WORDS = ("CLOSED", "VERIFIED", "CORRECTED", "RESOLVED", "WITHDRAWN", "SUPERSEDED")

# Two kinds of file this project cannot put a marker in. Both are stated as reasons rather than
# silently skipped, because a silent skip is how a gate stops covering what it claims to.
EXEMPT_DIRS: tuple[tuple[str, str], ...] = (
    # IMP-0045. A comment in one of these files fails solution import with 0x80040216 at
    # ImportXml.GetComponentsList, naming no component, while pac solution pack exits 0.
    ("environmentvariabledefinitions/",
     "files under environmentvariabledefinitions/ may contain NO comment at all — a comment "
     "there fails solution import with 0x80040216 at ImportXml.GetComponentsList, naming no "
     "component, while pac solution pack exits 0 and the file stays valid XML (IMP-0045)"),
    # Generator output. A marker written here is discarded the next time the generator runs, so
    # requiring one would teach agents to write a comment that silently disappears.
    ("src/generated/",
     "src/generated/ is generator output, not authored source — a marker written there is "
     "discarded the next time the generator runs. Mark the AUTHORED file that relies on the "
     "guess instead"),
    (".power/",
     ".power/ is tooling output, not authored source — a marker written there does not survive "
     "the tool that writes it"),
)

TABLE_SEP = re.compile(r"^\|[\s:|-]+\|$")


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_closed(status: str) -> bool:
    upper = status.upper()
    if any(word in upper for word in CLOSED_WORDS):
        return True
    # `n/a — closed`, `n/a` on its own.
    return upper.replace("*", "").strip().startswith("N/A")


def resolve_targets(where: str, repo_root: Path, doc_dir: Path) -> tuple[list[Path], list[str]]:
    """Files a *Where* cell names. Returns (resolved, unresolved-fragments).

    Two forms, in order of trust: a markdown link's href, then a bare path inside a code span.
    Three resolutions are tried per fragment, in order of how much is being assumed:

      1. relative to the REPOSITORY root — how most rows are written;
      2. relative to the DOCUMENT — how a markdown link that renders on GitHub is written
         (`../../src/code-apps/.../client.ts:279-292`);
      3. a search for that exact tail, accepted only when it matches exactly ONE file — because a
         code-span path is often written relative to the solution root
         (`OptionSets/rev_conditionprofile.xml`), and an ambiguous tail resolved by guessing is
         how a gate starts reporting on the wrong file.
    """
    resolved: list[Path] = []
    unresolved: list[str] = []
    seen: set[Path] = set()

    candidates = list(MD_LINK.findall(where))
    if not candidates:
        candidates = [span for span in CODE_SPAN.findall(where) if PATHISH.match(span)]

    for candidate in candidates:
        fragment = LINE_SUFFIX.sub("", candidate.strip()).strip()
        if not fragment:
            continue
        found: Path | None = None
        for base in (repo_root, doc_dir):
            attempt = (base / fragment).resolve()
            if attempt.is_file() and repo_root in attempt.parents:
                found = attempt
                break
        if found is None:
            matches = [p for p in repo_root.rglob(fragment) if p.is_file()]
            if len(matches) == 1:
                found = matches[0]
        if found is None:
            unresolved.append(fragment)
            continue
        if found not in seen:
            seen.add(found)
            resolved.append(found)

    if not candidates:
        unresolved.append(where[:70] or "(empty)")
    return resolved, unresolved


def exempt_reason(path: Path) -> str | None:
    text = path.as_posix()
    for directory, reason in EXEMPT_DIRS:
        if directory in text:
            return reason
    return None


def scan_document(path: Path, repo_root: Path) -> dict:
    """Collect the current status and the current Where target for every id in one document."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rows: dict[str, dict] = {}

    where_index: int | None = None
    status_index: int | None = None
    width = 0

    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line.startswith("|"):
            where_index = status_index = None
            continue
        if TABLE_SEP.match(line):
            continue

        cells = split_row(line)
        header_where = next((i for i, c in enumerate(cells) if WHERE_HEADER.match(c)), None)
        header_status = next((i for i, c in enumerate(cells) if STATUS_HEADER.match(c)), None)
        if header_where is not None or header_status is not None:
            if not ROW_ID.match(cells[0]):
                where_index, status_index, width = header_where, header_status, len(cells)
                continue

        match = ROW_ID.match(cells[0])
        if not match or len(cells) != width:
            continue
        identifier = match.group(2)
        struck = bool(match.group(1))
        entry = rows.setdefault(identifier, {
            "id": identifier, "status": None, "status_line": None,
            "where": None, "where_line": None, "struck": False,
        })
        entry["struck"] = entry["struck"] or struck
        if status_index is not None and status_index < len(cells):
            entry["status"] = cells[status_index]
            entry["status_line"] = number
        if where_index is not None and where_index < len(cells) and cells[where_index]:
            entry["where"] = cells[where_index]
            entry["where_line"] = number

    return rows


def scan(repo_root: Path) -> tuple[list[str], list[str], dict]:
    """Return (failures, notes, stats)."""
    failures: list[str] = []
    notes: list[str] = []
    stats = {"documents": 0, "rows": 0, "open": 0, "checked": 0,
             "closed": 0, "unresolved": 0, "exempt": 0}

    paths: list[Path] = []
    for pattern in SCAN_GLOBS:
        paths.extend(sorted(repo_root.glob(pattern)))

    for path in paths:
        rows = scan_document(path, repo_root)
        if not rows:
            continue
        stats["documents"] += 1
        rel = path.relative_to(repo_root).as_posix()

        for identifier, entry in sorted(rows.items()):
            stats["rows"] += 1
            status = entry["status"]
            if entry["struck"] and not status:
                stats["closed"] += 1
                continue
            if status is None:
                # A table with no Status column anywhere for this id — the id is tracked, but
                # this document never says whether it is open. Not a failure; named so it shows.
                notes.append(f"{rel}: {identifier} appears in no table with a Status column, so "
                             f"its state is unknown and no marker was required of it.")
                continue
            if is_closed(status):
                stats["closed"] += 1
                continue

            stats["open"] += 1
            where = entry["where"]
            if not where:
                stats["unresolved"] += 1
                notes.append(f"{rel}:{entry['status_line']}: {identifier} is OPEN "
                             f"({status[:40]}) and no table row names a 'Where' target for it, so "
                             f"its source marker cannot be checked.")
                continue

            resolved, unresolved = resolve_targets(where, repo_root, path.parent)
            if not resolved:
                stats["unresolved"] += 1
                notes.append(
                    f"{rel}:{entry['where_line']}: {identifier} is OPEN and its 'Where' column "
                    f"resolves to no file in this repository ({', '.join(unresolved)[:80]}). "
                    f"Write it as a markdown link to a real path and this row becomes checkable.")
                continue

            exemptions = [exempt_reason(p) for p in resolved]
            if all(exemptions) and exemptions:
                stats["exempt"] += 1
                notes.append(f"{rel}:{entry['where_line']}: {identifier} is OPEN and EXEMPT — "
                             f"{exemptions[0]}")
                continue

            stats["checked"] += 1
            checkable = [p for p in resolved if not exempt_reason(p)]
            if any(identifier in p.read_text(encoding="utf-8", errors="replace")
                   for p in checkable):
                continue

            targets = ", ".join(p.relative_to(repo_root).as_posix() for p in checkable)
            failures.append(
                f"{rel}:{entry['where_line']}: register row {identifier} is OPEN and names "
                f"{targets} as 'Where' the guess is made, but the string '{identifier}' appears "
                f"nowhere in that file. C-TECH-052 is HARD and requires an '{identifier}' comment "
                f"at the point of the guess in source, so the next author of that line learns it "
                f"is an unproven assumption by reading the line. Add the comment, or close the "
                f"register row.")

    return failures, notes, stats


# ── Fixtures ───────────────────────────────────────────────────────────────────────────────────
# Case 2 is the one that matters: it is the false positive the first draft of this script emitted
# against a row closed at V3 against a live org.
_CASES: list[tuple[str, str, str, int]] = [
    # (name, register markdown, source file body, expected failures)
    ("an-OPEN-row-whose-marker-is-present-passes",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-FIN-06 | a guess | [`s.ps1`](provisioning/s.ps1) | **OPEN** |\n",
     "# A-FIN-06 in the Dev Summary register\n", 0),

    ("a-VERIFIED-row-is-closed-and-needs-no-marker",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-FIN-03 | a guess | [`s.ps1`](provisioning/s.ps1) | **E1 — VERIFIED 2026-08-23.** |\n",
     "nothing here\n", 0),

    ("an-OPEN-row-with-no-marker-fails",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-FIN-07 | a guess | [`s.ps1`](provisioning/s.ps1#L171) | **OPEN** |\n",
     "nothing here\n", 1),

    ("a-CLOSED-status-in-a-later-append-table-wins-over-the-original-OPEN-row",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-FIN-04 | a guess | [`s.ps1`](provisioning/s.ps1) | **OPEN** |\n"
     "\ntext between the tables\n\n"
     "| ID | Assumption | Status |\n|---|---|---|\n"
     "| A-FIN-04 | a guess | **CLOSED — WRONG.** |\n",
     "nothing here\n", 0),

    ("a-struck-through-row-is-closed",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| ~~A-FIN-01~~ | ~~a guess~~ | [`s.ps1`](provisioning/s.ps1) | **VERIFIED** |\n",
     "nothing here\n", 0),

    ("an-unrecognised-status-word-is-read-as-OPEN-and-still-demands-the-marker",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-009 | a guess | [`s.ps1`](provisioning/s.ps1) | **PENDING REVIEW** |\n",
     "nothing here\n", 1),

    ("a-Where-column-naming-no-real-file-is-a-note-not-a-failure",
     "| ID | Claim | Where in source | Status |\n|---|---|---|---|\n"
     "| A-010 | a guess | see links | OPEN |\n",
     "nothing here\n", 0),

    ("a-table-with-no-Status-column-demands-nothing",
     "| id | Claim | Ev. | Cheapest verification |\n|---|---|---|---|\n"
     "| A-TR-1 | a guess | E3 | Sign in as a trustee |\n",
     "nothing here\n", 0),

    ("a-bare-code-span-path-resolves-by-unique-tail-match",
     "| ID | Claim | Where | Status |\n|---|---|---|---|\n"
     "| A-002 | a guess | `dataverse/s.ps1`, option `value=\"9\"` | OPEN |\n",
     "nothing here\n", 1),
]


def selftest() -> int:
    import tempfile

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, register, source, want in _CASES:
            root = Path(tmp) / name
            (root / "docs" / "development").mkdir(parents=True)
            (root / "provisioning" / "dataverse").mkdir(parents=True)
            (root / "docs" / "development" / "x-dev-summary.md").write_text(
                register, encoding="utf-8")
            (root / "provisioning" / "s.ps1").write_text(source, encoding="utf-8")
            (root / "provisioning" / "dataverse" / "s.ps1").write_text(source, encoding="utf-8")
            failures, notes, stats = scan(root)
            ok = len(failures) == want
            print(f"  {'ok  ' if ok else 'FAIL'}  {name}: {len(failures)} failure(s) "
                  f"(want {want}); {stats['rows']} row(s), {stats['open']} open, "
                  f"{stats['checked']} checked")
            if not ok:
                failed += 1
                for message in failures + notes:
                    print(f"          {message[:170]}")

    # The two exemptions, which cannot use the shared fixture layout above.
    for label, target, body, want_failures, want_exempt in (
        ("an environmentvariabledefinition target is EXEMPT, not a failure (IMP-0045)",
         "src/solutions/S/environmentvariabledefinitions/e/environmentvariabledefinition.xml",
         "<root/>\n", 0, 1),
        ("a generator-output target is EXEMPT — a marker there would not survive regeneration",
         "src/code-apps/a/src/generated/models/CommonModels.ts",
         "export interface IGetAllOptions {}\n", 0, 1),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "development").mkdir(parents=True)
            destination = root / target
            destination.parent.mkdir(parents=True)
            destination.write_text(body, encoding="utf-8")
            (root / "docs" / "development" / "x-dev-summary.md").write_text(
                f"| ID | Claim | Where | Status |\n|---|---|---|---|\n"
                f"| A-020 | a guess | [`t`]({target}) | OPEN |\n", encoding="utf-8")
            failures, notes, stats = scan(root)
            ok = len(failures) == want_failures and stats["exempt"] == want_exempt
            print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {len(failures)} failure(s), "
                  f"{stats['exempt']} exempt")
            if not ok:
                failed += 1

    # The IMP-0007 control: a tree with no register must yield zero rows, and main() must then
    # FAIL rather than report PASS over nothing.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs" / "development").mkdir(parents=True)
        _f, _n, stats = scan(root)
        ok = stats["rows"] == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  an empty docs/development tree yields 0 rows "
              f"(caller must fail, not pass): rows={stats['rows']}")
        if not ok:
            failed += 1

    total = len(_CASES) + 3
    if failed:
        print(f"\nSELFTEST: FAILED — {failed} case(s) of {total} fixtures", file=sys.stderr)
        return 1
    print(f"\nSELFTEST: PASS\nverify-assumption-markers: SELFTEST OK — {total} fixtures.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assert every OPEN Unvalidated Assumptions Register row carries its A-nnn "
                    "marker in the source file its 'Where' column names (C-TECH-052).")
    parser.add_argument("--selftest", action="store_true",
                        help="run the scanner against known-good and known-bad fixtures")
    parser.add_argument("--repo-root", default=None,
                        help="repository root (default: this script's parent directory)")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]

    failures, notes, stats = scan(repo_root)

    if stats["rows"] == 0:
        print("ERROR: inspected ZERO Unvalidated Assumptions Register rows across "
              f"{stats['documents']} document(s) under docs/development/. Either this project no "
              "longer keeps a register — in which case C-TECH-052 should be retired rather than "
              "left reporting PASS — or the §10 table shape changed and ROW_ID/WHERE_HEADER "
              "stopped matching. A checker that checks nothing must fail (IMP-0007).",
              file=sys.stderr)
        return 1

    for message in notes:
        print(f"NOTE: {message}", file=sys.stderr)

    if failures:
        for message in failures:
            print(f"ERROR: {message}", file=sys.stderr)
        print(f"\nASSUMPTION MARKERS: FAILED — {len(failures)} orphan guess(es) of "
              f"{stats['checked']} OPEN row(s) checked ({stats['rows']} row(s) total, "
              f"{stats['closed']} closed, {stats['unresolved']} unresolvable, "
              f"{stats['exempt']} exempt) across {stats['documents']} document(s).",
              file=sys.stderr)
        return 1

    print(f"ASSUMPTION MARKERS: PASS — {stats['checked']} OPEN row(s) checked, every one "
          f"carrying its marker in source; {stats['rows']} row(s) total, {stats['closed']} "
          f"closed, {stats['unresolved']} unresolvable, {stats['exempt']} exempt, across "
          f"{stats['documents']} document(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
