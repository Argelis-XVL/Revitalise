#!/usr/bin/env python3
"""Verify every FR/NFR id a change order prices still exists, unwithdrawn, in the SDD it sizes.

WHY THIS EXISTS. A change order that itemises hours per requirement id is valid only against the
revision of the requirement text it was sized on. Nothing in this repository compared the two, so
a withdrawn requirement keeps its line item and its hours indefinitely (`IMP-0297`).

MEASURED, on the tree this gate was written against:

  * `contract/change-orders/CO-001-A1.md` prices `NFR-027 — suppression/grouping helper` at
    1–1.5h. The SDD struck that row through and marked it WITHDRAWN by reviewer decision on
    2026-08-25, the same day.
  * The same document prices `FR-061 — demographic + benchmark charts` at 2–3.5h. FR-061 still
    exists, but its benchmark-comparison clause was withdrawn the same day and its SDD row is
    annotated REWORDED — so the half of the item the label names is gone while the id lives on.

Second instance of class `incorporated-document-version-mismatch`, after `IMP-0071` (the signed
agreement incorporated General Terms v1.3 and the file supplied was v1.2). The altitude rule in
`skills/how-to-promote-a-finding.md` §2 therefore forbids correcting CO-001-A1 by hand and moving
on, and requires the general property instead: **a commercial document is valid only against the
version of the artefact it cites.** This gate is that property for the one citation shape a script
can resolve exactly — a requirement id.

WHY IT IS SOFT, AND WHY THAT IS NOT A WEAKNESS. `CLAUDE.md` → Commercial Rules: "A commercial gate
never halts, retries or rolls back a build or a deploy. Delivery continues; the finding is
reported." A stale hours line in a change order misprices work; it breaks nothing at runtime, and
blocking a deployment on it would be the disproportionate response that teaches people to route
around gates. So: report, never block. Wire it with `--warn-only`.

EXIT CODES, following every other gate in `scripts/`:

  * 0 — every priced id resolves to a live, unwithdrawn requirement (or `--warn-only` was passed).
  * 1 — findings, of three kinds, none of which may stop a build:
      - `WITHDRAWN`  the SDD marks the id withdrawn, or strikes its row through. The change order
                     prices scope that no longer exists.
      - `ABSENT`     the id appears in no SDD requirement row at all. Either the sizing invented
                     it or the SDD dropped it silently.
      - `REWORDED`   the id lives, but its SDD row carries a dated REWORDED/withdrawn-clause
                     annotation. The hours were sized against text that has since changed, so the
                     line item needs re-confirming rather than deleting.
    Plus `NO-SOURCE` — a change order whose ids resolve against no SDD at all, which is the
    IMP-0007 shape (a gate reporting OK over nothing) and is surfaced rather than swallowed.
  * 2 — command-line usage error. Never a finding.

WHAT IT DOES NOT CATCH, stated because every promotion leaves a residual. It matches **ids**. A
change order that prices withdrawn scope in prose without naming an id is invisible to it, and so
is a sizing whose hours moved for a requirement whose text did not. It reads the requirement
tables' own markup, so an SDD that records a withdrawal in narrative prose without annotating the
row is equally invisible. It cannot judge whether a still-valid id's HOURS are right — only
whether the thing being priced still exists.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# A requirement id as it appears anywhere: FR-057, NFR-027.
ID_RE = re.compile(r"\b(N?FR)-(\d{1,4})\b")

# A requirement table row in the SDD, whose first cell is the id — optionally struck through.
# Anchored to the row start so a mention of an id inside another row's prose is not mistaken for
# that id's own definition.
SDD_ROW_RE = re.compile(r"^\|\s*(~~)?\s*(N?FR-\d{1,4})\s*(~~)?\s*\|(?P<body>.*)$", re.MULTILINE)

# Withdrawal / rewording markers, as this project actually writes them: a BOLD marker opening a
# dated annotation on the row itself — `**WITHDRAWN, Amendment A-03 Resolution, 2026-08-25 — …**`.
# The SDD's own words for the convention: "struck through and annotated, never silently deleted".
#
# KEYING ON THE BOLD MARKER IS THE WHOLE CORRECTNESS ARGUMENT, and it was learned by running this
# gate rather than by reasoning. A first version matched the bare word `withdrawn` anywhere in the
# row body and reported FR-059 as withdrawn, because FR-059's row says "No minimum-cell-size rule
# applies — see NFR-027, withdrawn by reviewer decision". That is FR-059 correctly citing ANOTHER
# requirement's withdrawal, in plain prose, and a gate that reports it is a gate people learn to
# ignore. A row's own disposition is written as a bold marker; a mention of someone else's is not.
WITHDRAWN_RE = re.compile(r"\*\*\s*WITHDRAWN\b", re.IGNORECASE)
REWORDED_RE = re.compile(r"\*\*\s*REWORDED\b", re.IGNORECASE)

# Where a change order itemises hours. Only table rows are read for priced ids: a change order's
# prose cites ids for context ("supersedes CO-001's estimate for FR-057") and pricing them would
# make the gate noisy in exactly the way that gets a gate ignored.
TABLE_ROW_RE = re.compile(r"^\|(?P<body>.+)\|\s*$", re.MULTILINE)

# `**Amends:** [`contract/change-orders/CO-001.md`](CO-001.md)` / `**Supersedes:** CO-001.md`
#
# THIS PROJECT NEVER EDITS AN APPROVED COMMERCIAL DOCUMENT IN PLACE. It writes a new one that
# supersedes it (`C-COM-003`'s logic for invoices, applied to change orders — CO-001-A1 says so in
# its own "Why an amendment, not a new change order" section). A superseded change order therefore
# prices withdrawn scope FOREVER, correctly: it is the historical record of what was agreed then.
#
# Without this rule the gate would report every superseded document on every run, permanently, and
# a permanent finding nobody can clear is how a gate teaches people to ignore it. So a change order
# another change order amends is reported at NOTE level and excluded from the exit code: the live
# document is the one that must be right. Learned by measurement — CO-001-A2 was drafted to
# supersede CO-001-A1 while this gate was being written, which would have made CO-001-A1's two
# findings immortal.
AMENDS_RE = re.compile(r"^\s*\*\*(?:Amends|Supersedes)\s*:?\*\*\s*(?P<targets>.+)$",
                       re.MULTILINE | re.IGNORECASE)
CO_FILE_RE = re.compile(r"([A-Za-z0-9][\w.-]*\.md)")


@dataclass(frozen=True)
class Finding:
    kind: str
    document: str
    line: int
    req_id: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.document}:{self.line}: {self.req_id} — {self.detail}"


def _priced_ids(text: str) -> dict[str, int]:
    """Requirement ids appearing in a table row of a change order, mapped to their line number.

    A table row is the itemisation shape: `| FR-061 — demographic + benchmark charts | 2h | ... |`.
    First occurrence wins, so the line reported is where the item is priced.
    """
    found: dict[str, int] = {}
    for row in TABLE_ROW_RE.finditer(text):
        line_no = text[: row.start()].count("\n") + 1
        body = row.group("body")
        # Skip a markdown separator row (|---|---|).
        if re.fullmatch(r"[\s|:-]+", body):
            continue
        for m in ID_RE.finditer(body):
            rid = f"{m.group(1)}-{int(m.group(2)):03d}"
            found.setdefault(rid, line_no)
    return found


def _sdd_rows(text: str) -> dict[str, list[tuple[str, bool]]]:
    """Requirement id -> list of (row body, id-struck-through) for every definition row."""
    rows: dict[str, list[tuple[str, bool]]] = {}
    for m in SDD_ROW_RE.finditer(text):
        m2 = ID_RE.search(m.group(2))
        if not m2:
            continue
        rid = f"{m2.group(1)}-{int(m2.group(2)):03d}"
        struck = bool(m.group(1) and m.group(3))
        rows.setdefault(rid, []).append((m.group("body"), struck))
    return rows


def _classify(rid: str, rows: list[tuple[str, bool]]) -> tuple[str, str] | None:
    """Return (kind, detail) if this id's SDD rows show a problem, else None.

    A requirement appears in more than one table (the catalogue, the traceability matrix). The
    catalogue row is the one carrying the annotation, so a problem in ANY row is reported — but a
    row that is merely a traceability entry cannot clear a withdrawal recorded elsewhere.
    """
    for body, struck in rows:
        if struck or WITHDRAWN_RE.search(body):
            how = "its row is struck through" if struck else "its row is marked WITHDRAWN"
            return (
                "WITHDRAWN",
                f"priced here, but the SDD has withdrawn it ({how}). The change order prices "
                f"scope that no longer exists — re-price against the approved text, and correct "
                f"the total.",
            )
    for body, _ in rows:
        if REWORDED_RE.search(body):
            return (
                "REWORDED",
                "priced here, and the id still exists, but its SDD row is annotated as reworded "
                "with a clause withdrawn. The hours were sized against text that has since "
                "changed, so this line item needs re-confirming against the approved wording "
                "rather than deleting.",
            )
    return None


def run(orders_dir: Path, sdd_paths: list[Path]) -> tuple[int, list[Finding], int, int]:
    findings: list[Finding] = []

    sdd_rows: dict[str, list[tuple[str, bool]]] = {}
    for p in sdd_paths:
        if not p.is_file():
            continue
        for rid, rows in _sdd_rows(p.read_text(encoding="utf-8")).items():
            sdd_rows.setdefault(rid, []).extend(rows)

    orders = sorted(orders_dir.glob("*.md")) if orders_dir.is_dir() else []
    checked_ids = 0

    # Which change orders have been superseded by a later one? Those are history, not live scope.
    superseded: set[str] = set()
    for order in orders:
        for m in AMENDS_RE.finditer(order.read_text(encoding="utf-8")):
            for target in CO_FILE_RE.findall(m.group("targets")):
                if target != order.name:
                    superseded.add(target)

    if not orders:
        # Nothing to check is not the same as everything being fine, but it is also not a defect:
        # a project with no change orders is the normal case. Report it and exit clean.
        return 0, [], 0, 0

    if not sdd_rows:
        findings.append(
            Finding(
                "NO-SOURCE",
                str(orders_dir),
                1,
                "(all)",
                f"{len(orders)} change order(s) itemise requirement ids and no SDD requirement "
                f"row was parsed from {', '.join(str(p) for p in sdd_paths)}. This gate cannot "
                f"see the thing it checks, so it is reporting that rather than passing over "
                f"nothing (IMP-0007).",
            )
        )
        return 1, findings, len(orders), 0

    for order in orders:
        text = order.read_text(encoding="utf-8")
        is_history = order.name in superseded
        for rid, line_no in sorted(_priced_ids(text).items()):
            checked_ids += 1
            rows = sdd_rows.get(rid)
            if not rows:
                verdict = (
                    "ABSENT",
                    "priced here, and no requirement row anywhere in the SDD defines it. "
                    "Either the sizing names an id that was never written, or the SDD "
                    "dropped it without striking it through.",
                )
            else:
                verdict = _classify(rid, rows)
            if not verdict:
                continue
            if is_history:
                findings.append(
                    Finding(
                        "NOTE",
                        order.name,
                        line_no,
                        rid,
                        f"would be reported as {verdict[0]}, but a later change order supersedes "
                        f"this document, so this line is the historical record of what was agreed "
                        f"at the time and is correct as written. Not counted.",
                    )
                )
            else:
                findings.append(Finding(verdict[0], order.name, line_no, rid, verdict[1]))

    blocking = [f for f in findings if f.kind != "NOTE"]
    return (1 if blocking else 0), findings, len(orders), checked_ids


# ---------------------------------------------------------------------------------------------
# Self-test. Fixtures are assembled at runtime, so this proves the gate can FAIL — the property
# `verify-build-config.py` requires of every gate, and the one IMP-0007's class is made of.
# ---------------------------------------------------------------------------------------------

_SDD_FIXTURE = """
# Plan

| ID | Requirement | Priority |
|---|---|---|
| FR-057 | The system SHALL scope to the current round. | Medium |
| FR-059 | The system SHALL present the need profile. *(No minimum-cell-size rule applies — see NFR-027, withdrawn by reviewer decision, Resolution 2026-08-25.)* | Medium |
| FR-061 | The system SHALL present distributions. *(source: deck.)* WARNING **REWORDED, 2026-08-25 — the benchmark-comparison clause is withdrawn by reviewer decision.** | Medium |
| ~~NFR-027~~ | ~~Suppression below a configured minimum.~~ WARNING **WITHDRAWN, 2026-08-25 — explicit reviewer risk-acceptance.** | Medium |

| FR-057 | US-016 AC-1 |
| FR-061 | US-016 AC-5 |
"""

_ORDER_BAD = """
# CO-999 — a change order pricing withdrawn scope

| Item | Low | High | Basis |
|---|---|---|---|
| FR-057 — round scoping | 0.5h | 1h | Reuses an existing mechanism |
| FR-059 — exceptional-circumstance breakdown | 1.5h | 2.5h | Grouped counts |
| FR-061 — demographic + benchmark charts | 2h | 3.5h | Chart work |
| NFR-027 — suppression/grouping helper | 1h | 1.5h | Built once |
| FR-999 — a requirement nobody wrote | 1h | 2h | Invented |
"""

_ORDER_GOOD = """
# CO-998 — a clean change order

Prose may mention NFR-027 for history without pricing it.

| Item | Low | High | Basis |
|---|---|---|---|
| FR-057 — round scoping | 0.5h | 1h | Reuses an existing mechanism |
"""


def selftest() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        sdd = root / "plan.md"
        sdd.write_text(_SDD_FIXTURE, encoding="utf-8")

        # 1. Known-bad: one WITHDRAWN, one REWORDED, one ABSENT; FR-057 clean.
        bad = root / "bad"
        bad.mkdir()
        (bad / "CO-999.md").write_text(_ORDER_BAD, encoding="utf-8")
        code, findings, orders, ids = run(bad, [sdd])
        kinds = sorted(f.kind for f in findings)
        if code != 1:
            failures.append(f"known-bad exited {code}, expected 1")
        if kinds != ["ABSENT", "REWORDED", "WITHDRAWN"]:
            failures.append(f"known-bad kinds were {kinds}, expected ABSENT/REWORDED/WITHDRAWN")
        if not any(f.req_id == "NFR-027" and f.kind == "WITHDRAWN" for f in findings):
            failures.append("known-bad did not report NFR-027 as WITHDRAWN")
        if not any(f.req_id == "FR-061" and f.kind == "REWORDED" for f in findings):
            failures.append("known-bad did not report FR-061 as REWORDED")
        if any(f.req_id == "FR-057" for f in findings):
            failures.append("known-bad reported the clean FR-057 row")
        # REGRESSION FIXTURE for the false positive this gate shipped with in its first form:
        # FR-059's row cites NFR-027's withdrawal in prose. That is FR-059 being correct, not
        # FR-059 being withdrawn, and reporting it is how a gate earns a reputation for noise.
        if any(f.req_id == "FR-059" for f in findings):
            failures.append("FR-059 was reported, but its row only CITES another requirement's "
                            "withdrawal in prose — a row's own disposition is a bold marker")
        if ids != 5:
            failures.append(f"known-bad checked {ids} ids, expected 5")

        # 2. Known-good: a clean order, and an id mentioned only in prose is not priced.
        good = root / "good"
        good.mkdir()
        (good / "CO-998.md").write_text(_ORDER_GOOD, encoding="utf-8")
        code, findings, orders, ids = run(good, [sdd])
        if code != 0 or findings:
            failures.append(f"known-good exited {code} with {len(findings)} finding(s), expected 0")
        if ids != 1:
            failures.append(f"known-good checked {ids} ids, expected 1 (prose must not be priced)")

        # 3. Cannot report OK over nothing: orders present, no SDD rows parsed.
        empty_sdd = root / "empty.md"
        empty_sdd.write_text("# nothing here\n", encoding="utf-8")
        code, findings, orders, ids = run(bad, [empty_sdd])
        if code != 1 or not any(f.kind == "NO-SOURCE" for f in findings):
            failures.append("a change order against an SDD with no requirement rows did not "
                            "report NO-SOURCE")

        # 4. No change orders at all is clean, not a defect.
        none_dir = root / "none"
        none_dir.mkdir()
        code, findings, orders, ids = run(none_dir, [sdd])
        if code != 0 or findings:
            failures.append("an empty change-order directory was reported as a defect")

        # 5. Supersession: the same bad document, once amended by a later one, drops to NOTE and
        # stops failing the gate. Without this, a superseded change order — which this project
        # deliberately never edits in place — would be reported on every run forever.
        hist = root / "hist"
        hist.mkdir()
        (hist / "CO-999.md").write_text(_ORDER_BAD, encoding="utf-8")
        (hist / "CO-999-A1.md").write_text(
            "# CO-999-A1\n\n**Amends:** [`contract/change-orders/CO-999.md`](CO-999.md) — the "
            "hours line only.\n\n| Item | Low | High | Basis |\n|---|---|---|---|\n"
            "| FR-057 — round scoping | 0.5h | 1h | Unchanged |\n",
            encoding="utf-8")
        code, findings, orders, ids = run(hist, [sdd])
        if code != 0:
            failures.append(f"a superseded change order still failed the gate (exit {code}) — it "
                            f"is history, and this project never edits an approved commercial "
                            f"document in place")
        if not all(f.kind == "NOTE" for f in findings):
            failures.append(f"superseded findings were not all NOTE: "
                            f"{sorted({f.kind for f in findings})}")
        if not findings:
            failures.append("superseded document produced no NOTE at all — it should still be "
                            "visible, just not counted")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\nverify-change-order-requirements --selftest: FAILED "
              f"({len(failures)} failure(s)).", file=sys.stderr)
        return 1

    print("verify-change-order-requirements --selftest: OK — 6 fixture(s): a change order "
          "pricing a withdrawn id, a reworded id and an absent id all report; a clean order and "
          "prose-only mentions do not; an SDD with no requirement rows reports NO-SOURCE rather "
          "than passing over nothing; an empty change-order directory is clean; a superseded change order drops to NOTE and stops failing.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--orders-dir", type=Path, default=Path("contract/change-orders"),
                        help="directory of change orders (default: contract/change-orders)")
    parser.add_argument("--sdd", type=Path, nargs="*",
                        default=[Path("docs/plans/revitalise-grant-automation-plan.md")],
                        help="SDD document(s) whose requirement tables the ids resolve against")
    parser.add_argument("--warn-only", action="store_true",
                        help="print findings and exit 0 — the wiring this SOFT commercial gate "
                             "requires, because a commercial gate never halts a build")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove this gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    code, findings, orders, ids = run(args.orders_dir, list(args.sdd))

    notes = [f for f in findings if f.kind == "NOTE"]
    blocking = [f for f in findings if f.kind != "NOTE"]

    for f in notes:
        print(f"NOTE: {f}", file=sys.stderr)

    if blocking:
        label = "WARNING" if args.warn_only else "ERROR"
        for f in blocking:
            print(f"{label}: {f}", file=sys.stderr)
        withdrawn = sum(1 for f in blocking if f.kind == "WITHDRAWN")
        absent = sum(1 for f in blocking if f.kind == "ABSENT")
        reworded = sum(1 for f in blocking if f.kind == "REWORDED")
        nosource = sum(1 for f in blocking if f.kind == "NO-SOURCE")
        print(
            f"\nverify-change-order-requirements: FAILED (SOFT — report as WARN, do not block a "
            f"build or a deploy) — {withdrawn} withdrawn, {absent} absent, {reworded} reworded, "
            f"{nosource} no-source, across {ids} priced id(s) in {orders} change order(s); "
            f"{len(notes)} note(s) on superseded documents not counted."
            + (" Exiting 0: --warn-only." if args.warn_only else ""),
            file=sys.stderr,
        )
        return 0 if args.warn_only else code

    print(f"verify-change-order-requirements: OK — {ids} priced requirement id(s) across "
          f"{orders} change order(s) all resolve to a live, unwithdrawn requirement"
          + (f"; {len(notes)} note(s) on superseded documents not counted." if notes else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
