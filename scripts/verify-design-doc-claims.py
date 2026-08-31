#!/usr/bin/env python3
"""Compare a design document's CHECKABLE FACTUAL CLAIMS against the source that settles them.

THE GENERAL GATE FOR CLASS `approved-document-internally-inconsistent` (x15 in
logs/known-failure-modes.md, six of them in one batch). Every gate in this repository compares
source against source. Nothing has ever compared a design document's checkable factual claims
against the source that settles them, which is why the class reached fifteen instances undefended.

Two claim types are checkable without reading intent, and this checks those two only:

  * `IMP-0379` — TAD §3.4 and risk `A-R24` both state that `rev_ethnicgroup` "does not exist …
    it was never built — deliberately", and the handoff quoted `A-R24` to justify leaving
    `ethnicGroupDistribution` null. The SAME document's §12.1, added later the same day, records
    that the column WAS built ("the attribute `rev_applicant.rev_ethnicgroup` exists"), and
    `Entities/rev_applicant/Entity.xml`'s own committed description confirms it. The two sections
    were never reconciled, so the next reader of §3.4 alone concludes no data source can exist.

  * `IMP-0391` — the same TAD's §8.4.1 states the design system's warning-tone title at `3.18:1`
    where the WCAG 2.1 formula over the two hex values that row itself names gives `3.16:1`. A
    transcription slip in the second decimal, in the table that is the entire basis of an ADR a
    later reader will trust without re-deriving. The shipped `ds-tokens.css` and
    `ds-tokens.test.ts` both carry `3.16`, so the DOCUMENT is the wrong copy.

WHAT IT CHECKS, over `docs/architecture/` AND `docs/plans/` — TWO checks:

  (a) a document asserting that a `rev_*` column DOES NOT EXIST or was NEVER BUILT, where that
      column is present in a solution `Entity.xml`. HARD.
  (b) every contrast ratio a MARKDOWN TABLE ROW states, recomputed from the hex values that row
      itself names. HARD.

`docs/plans/` is covered because no gate reads it at all today: `verify-tad-coverage.py`'s
`--design-docs` defaults to `docs/architecture` only, and one of the plan documents carries a
classification table two findings in this batch are about.

WHY CHECK (a) ASSERTS ABSENCE-AGAINST-PRESENCE, WHICH IS THE OPPOSITE OF HOW IT WAS PROPOSED
--------------------------------------------------------------------------------------------
`IMP-0374` and `IMP-0376` both ask for the other direction: a prose claim that a column IS
withheld from trustees, checked against a schema showing it visible. That was built and run over
all seven design documents first: **7 findings, 0 true, 7 false.** Every one was the OLD WORDING
SURVIVING INSIDE ITS OWN RETRACTION — both documents were corrected on 2026-08-27 and now quote
the wrong sentence in order to withdraw it, which a phrase-presence check cannot tell from an
assertion. Worse, the same run scored the corpus's one genuinely false sentence
("`rev_ethnicgroup` does not exist") as CONSISTENT, because it names a column that really is
secured. So that direction is not shipped, both its instances are already corrected on disk, and
what those two findings leave behind is a prose rule in
`skills/how-to-verify-a-platform-contract.md` §4 instead.

MEASURED BEFORE WIRING, and both narrowings remove their false positives BY NAME:

  check (a): **21 raw absence-phrase matches → 2 findings, 2 true, 0 false.**
    · narrowing 1 — the claim's subject must be an EXISTING `rev_*` column within 40 characters
      BEFORE the phrase. 21 → 3. Removes, among others, "The **job itself is not built**" and
      "`REV_FinanceOnly` is not built in this slice" (a role, not a column).
    · narrowing 2 — a SCOPE QUALIFIER after the phrase disqualifies it. 3 → 2. Removes
      `docs/plans/revitalise-grant-record-plan.md:256`, "`rev_providerid` is not built in this
      slice", BY NAME: that is a dated decision record about one delivery slice, not a claim
      about today's schema.
    Both survivors are `rev_ethnicgroup`, which is `IMP-0379`'s defect exactly.

  check (b): reads TABLE ROWS ONLY, bolded `**n.nn**` and `n.nn:1` figures only, and pairs a
    single named hex with the page surface when the row says "white". The first form measured
    **7 units, 1 true, 6 false** — every false one a stated figure whose second colour was a
    design-system token named three clauses away, or a WCAG floor (`4.5`, `3:1`) or a WBS id
    (`6.1`) read as a measurement. Scoped to table rows it measured **2 findings, 1 true, 1
    false**, and one further narrowing removed the false one BY NAME: a row naming two hexes AND
    the word "white" is UNCHECKABLE, because at
    `docs/architecture/trustee-portal-visual-refresh-architecture.md:2136` the second figure is
    bolded together with trailing prose and does not parse, so the one figure that does parse got
    paired with the wrong two colours against a row that is entirely correct.
    **Final: 1 finding, 1 true, 0 false, 12 figures recomputing exactly, 4 rows declared
    UNCHECKABLE by name.**

  WHOLE GATE, against the real corpus: **3 findings across 7 documents, 3 true, 0 false.** It is
  therefore RED on wiring, deliberately, on `rev_ethnicgroup` ×2 and the `3.18` figure — all
  three in one document, owner `architect-agent`.

RESIDUAL — four, and the first two matter most:

  1. Check (a) reports the SAME defect twice in one document, because the document states it
     twice (§3.4 and A-R24). Two FURTHER statements of it — §3.4's own heading and a summary
     line — are NOT reported, because no column is named within 40 characters of the phrase.
     That is a coverage gap, not a false positive, and it is stated because the gate will
     otherwise read as more complete than it is.
  2. Check (b) reads TABLE ROWS ONLY. Every measured false positive was in PROSE, where a stated
     figure sits beside colours named three clauses away. Prose is declared out of scope rather
     than silently missed, and an UNCHECKABLE row is named rather than passed over.
  3. Neither check can read a claim's LOGIC. `IMP-0380`'s staleness half and `IMP-0347`'s
     one-sided-assumption half are wording properties; they get prose rules, not this gate.
  4. Check (a) knows only what `Entity.xml` declares. A column that exists LIVE and not in
     source, or the reverse, is `IMP-0372`'s class and needs a live reconciliation this cannot do.

Run:
    python3 scripts/verify-design-doc-claims.py docs/architecture docs/plans
    python3 scripts/verify-design-doc-claims.py --selftest   # prove it can fail

Exits 0 clean · 1 on any violation or unreadable input · 2 on a usage error. Fails — never
passes — when it finds no documents at all (IMP-0007). C-DOM-001, C-TECH-057.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── check (a) ──────────────────────────────────────────────────────────────────────────────

_ABSENCE = re.compile(
    r"(does not exist|do not exist|never built|was not built|were not built|is not built"
    r"|are not built|not built|no such column)", re.I)
_REV_COLUMN = re.compile(r"rev_[a-z0-9_]+")

# A scope qualifier makes the sentence a dated decision about one delivery slice rather than a
# claim about today's schema. This is narrowing 2, and it removes `rev_providerid` by name.
_SCOPE_QUALIFIER = re.compile(
    r"\b(in this (slice|pass|dispatch|release|phase|version|revision)|yet\b)", re.I)

# How far back to look for the claim's SUBJECT. This is narrowing 1.
_SUBJECT_WINDOW = 40


def source_columns(repo_root: Path = REPO_ROOT) -> set[str]:
    """Every `rev_*` attribute any solution Entity.xml declares. Read, never transcribed."""
    columns: set[str] = set()
    for path in sorted(repo_root.glob("src/solutions/*/Entities/*/Entity.xml")):
        try:
            tree = ET.parse(path)
        except (ET.ParseError, OSError):
            continue
        for attribute in tree.iter("attribute"):
            name = attribute.get("PhysicalName") or attribute.findtext("LogicalName")
            if name:
                columns.add(name.lower())
    return columns


def check_absence_claims(doc: Path, text: str, columns: set[str]) -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _ABSENCE.finditer(line):
            window = line[max(0, match.start() - _SUBJECT_WINDOW):match.start()].lower()
            subjects = [c for c in _REV_COLUMN.findall(window) if c in columns]
            if not subjects:
                continue  # narrowing 1: no existing column is the claim's subject
            if _SCOPE_QUALIFIER.search(line[match.end():match.end() + _SUBJECT_WINDOW]):
                continue  # narrowing 2: a dated decision about one slice, not about the schema
            errors.append(
                f"{doc}:{lineno}: states that `{subjects[-1]}` {match.group(1).lower()}, and "
                f"that column IS declared in a solution Entity.xml. A later section of the same "
                f"document, or another document entirely, is the half that matches source — and "
                f"the next reader of this line alone will conclude no data source can exist "
                f"(IMP-0379). Reconcile the two in one pass, or say what is actually missing "
                f"(a field permission, a flow, an intake capture) rather than the column."
                f"\n    WRITING THE CORRECTION: this check cannot tell an assertion from its own "
                f"retraction, so an erratum that quotes the withdrawn sentence will re-trip it "
                f"(IMP-0428). State the correction SOURCE-FIRST — \"`{subjects[-1]}` exists; this "
                f"document twice asserted the opposite\" — so no column name sits within "
                f"{_SUBJECT_WINDOW} characters BEFORE an absence phrase. Do not add a retraction "
                f"phrase to this gate to clear it: a phrase-triggered skip is an escape hatch any "
                f"author could use on a real finding, and narrowing this gate is "
                f"improvement-agent's call (IMP-0422, five measured instances).")
    return errors


# ── check (b) ──────────────────────────────────────────────────────────────────────────────

_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
# Bolded `**4.49**` or an explicit `4.49:1`. Deliberately NOT a bare `4.5`: the Floor column is
# full of them, and a floor is a requirement, not a measurement.
_RATIO = re.compile(r"\*\*\s*([0-9]{1,2}\.[0-9]{2})\s*\*\*|(?<![0-9.])([0-9]{1,2}\.[0-9]{2}):1")
_WHITE = re.compile(r"\bwhite\b", re.I)
_PAGE_SURFACE = "ffffff"


def _luminance(hex6: str) -> float:
    """WCAG 2.1 relative luminance."""
    out = []
    for index in (0, 2, 4):
        channel = int(hex6[index:index + 2], 16) / 255
        out.append(channel / 12.92 if channel <= 0.03928
                   else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    light, dark = sorted((_luminance(hex_a), _luminance(hex_b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _ratios(line: str) -> list[str]:
    return [a or b for a, b in _RATIO.findall(line)]


def check_contrast_rows(doc: Path, text: str) -> tuple[list[str], int, list[str]]:
    """(errors, figures verified, rows declared uncheckable)."""
    errors: list[str] = []
    verified = 0
    uncheckable: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.lstrip().startswith("|"):
            continue  # TABLE ROWS ONLY — prose is declared out of scope, see the docstring
        figures = _ratios(line)
        if not figures:
            continue
        hexes = [h.lower() for h in _HEX.findall(line)]
        # THE PAIRING RULE, and its second clause is a NARROWING that removes a measured false
        # positive by name. A row naming TWO hexes AND the word "white" is ambiguous: at
        # trustee-portal-visual-refresh-architecture.md:2136 the row is "`--text-muted` `#8a8a8a`
        # on white | **3.45** | … on `--surface-band` `#ede8f1` **2.86 — below even the 3:1
        # floor**". Its second figure is bolded together with trailing prose, so only 3.45 parses
        # as a figure — and pairing 3.45 with (#8a8a8a, #ede8f1) reported a 2.86 mismatch against
        # a row that is entirely correct. So "white" plus more than one hex is UNCHECKABLE.
        white = bool(_WHITE.search(line))
        pair: tuple[str, str] | None = None
        if len(figures) == 1 and len(hexes) == 2 and not white:
            pair = (hexes[0], hexes[1])
        elif len(figures) == 1 and len(hexes) == 1 and white:
            pair = (hexes[0], _PAGE_SURFACE)
        if pair is None:
            uncheckable.append(
                f"{doc}:{lineno}: states {len(figures)} ratio figure(s) "
                f"({', '.join(figures)}) against {len(hexes)} named hex value(s)"
                f"{' and the word ' + chr(39) + 'white' + chr(39) if white else ''}, so the "
                f"pairing is ambiguous. Declared UNCHECKABLE rather than passed over: this "
                f"check pairs exactly two named colours with no 'white', or one named colour "
                f"with the page surface when the row says 'white'.")
            continue
        computed = contrast_ratio(*pair)
        stated = float(figures[0])
        if round(computed, 2) != round(stated, 2):
            errors.append(
                f"{doc}:{lineno}: states a contrast ratio of {stated:.2f} for "
                f"#{pair[0]} on #{pair[1]}, and the WCAG 2.1 formula over those two values "
                f"gives {computed:.4f} ({round(computed, 2):.2f}). A contrast table is the whole "
                f"basis of an accessibility decision a later reader will trust without "
                f"re-deriving it (IMP-0391). Check the SHIPPED stylesheet too — last time the "
                f"document was the wrong copy and the CSS was right."
                f"\n    WRITING THE CORRECTION: this check reads markdown TABLE ROWS only, and "
                f"prose is out of scope by design. So keep the RETRACTED figure in the paragraph "
                f"and leave only the CORRECT one in the row, where it recomputes and counts as "
                f"verified. An erratum that states the old ratio beside the two hex values inside "
                f"a table row re-trips this check on its own correction (IMP-0428).")
        else:
            verified += 1
    return errors, verified, uncheckable


# ── driver ─────────────────────────────────────────────────────────────────────────────────

def run(roots: list[Path], repo_root: Path = REPO_ROOT) -> int:
    docs: list[Path] = []
    for root in roots:
        if root.is_file():
            docs.append(root)
        elif root.is_dir():
            docs += sorted(root.glob("*.md"))
        else:
            print(f"design-doc-claims: FAILED — {root} does not exist. A gate pointed at a "
                  "missing target does not pass (IMP-0007).", file=sys.stderr)
            return 1
    if not docs:
        print(f"design-doc-claims: FAILED — no markdown documents found under "
              f"{', '.join(str(r) for r in roots)}. A gate with nothing to check must not "
              "report OK (IMP-0007).", file=sys.stderr)
        return 1

    columns = source_columns(repo_root)
    if not columns:
        print("design-doc-claims: FAILED — no rev_* columns found in any solution Entity.xml, so "
              "check (a) has no reference to compare against. A gate that cannot read its "
              "source must fail rather than pass every claim (IMP-0007).", file=sys.stderr)
        return 1

    errors: list[str] = []
    verified = 0
    uncheckable: list[str] = []
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{doc}: unreadable — {exc}")
            continue
        errors += check_absence_claims(doc, text, columns)
        row_errors, row_verified, row_uncheckable = check_contrast_rows(doc, text)
        errors += row_errors
        verified += row_verified
        uncheckable += row_uncheckable

    for line in uncheckable:
        print(f"UNCHECKABLE: {line}", file=sys.stderr)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\ndesign-doc-claims: FAILED — {len(errors)} claim(s) across {len(docs)} design "
              f"document(s) that the source they are about contradicts. {verified} contrast "
              f"figure(s) verified, {len(uncheckable)} row(s) declared uncheckable.",
              file=sys.stderr)
        return 1

    print(f"design-doc-claims: OK — {len(docs)} design document(s), {len(columns)} rev_* columns "
          f"read from Entity.xml: no document claims an existing column does not exist, and all "
          f"{verified} checkable contrast figure(s) recompute exactly. "
          f"{len(uncheckable)} row(s) declared UNCHECKABLE above and NOT covered by this OK. "
          f"NOTE: prose is out of scope for check (b), and neither check can read a claim's "
          f"logic — only its values.")
    return 0


# ── Self-test: the gate must be able to fail (C-TECH-057) ────────────────────

def selftest() -> int:
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        # A throwaway repo root whose Entity.xml declares exactly one column.
        entity = base / "repo" / "src" / "solutions" / "S" / "Entities" / "rev_applicant"
        entity.mkdir(parents=True)
        (entity / "Entity.xml").write_text(
            '<Entity><attributes>'
            '<attribute PhysicalName="rev_ethnicgroup" /><attribute PhysicalName="rev_gender" />'
            '</attributes></Entity>', encoding="utf-8")
        root = base / "repo"

        def case(label: str, body: str, expected: int) -> None:
            docs = base / f"case{len(checks)}"
            docs.mkdir()
            (docs / "d.md").write_text(body, encoding="utf-8")
            checks.append((label, run([docs], repo_root=root) == expected))

        # ── check (a) ────────────────────────────────────────────────────────────────────
        case("check (a): a claim that an EXISTING column does not exist is rejected — "
             "IMP-0379's exact shape",
             "**`rev_ethnicgroup` does not exist.** It was never built.\n", 1)
        case("check (a): the same claim in a RISK TABLE ROW is rejected",
             "| **A-R24** | `rev_ethnicgroup` was deliberately never built | Medium |\n", 1)
        case("check (a): a claim about a column that genuinely is NOT in source PASSES",
             "**`rev_nosuchcolumn` does not exist.** It was never built.\n", 0)
        case("check (a): narrowing 1 — an absence phrase whose subject is NOT a column PASSES "
             "('The job itself is not built', 'REV_FinanceOnly is not built')",
             "| NFR-010 | The **job itself is not built** — this slice ships the trigger |\n"
             "| **Finance role** | `REV_FinanceOnly` is not built |\n", 0)
        case("check (a): narrowing 2 — a SCOPE QUALIFIER after the phrase PASSES, removing "
             "revitalise-grant-record-plan.md:256's `rev_providerid` by name",
             "| **OQ-G03** | `rev_ethnicgroup` is not built in this slice | arrives with 8.1 |\n",
             0)
        case("check (a): a column named more than 40 characters before the phrase is NOT "
             "reported — the stated coverage gap, pinned so it cannot change unnoticed",
             "`rev_ethnicgroup` is a planned column on the applicant table and, as it turns "
             "out, does not exist.\n", 0)

        # ── check (b) ────────────────────────────────────────────────────────────────────
        # #c47a00 on #fdf5e6 — the real row. Stated 3.18, WCAG gives 3.16.
        case("check (b): IMP-0391's exact row — a stated **3.18** against a recomputed 3.16 — "
             "is rejected",
             "| Pair | Ratio | Floor |\n|---|---|---|\n"
             "| `--warning` `#c47a00` on `#fdf5e6` | **3.18** | 4.5 normal text |\n", 1)
        case("check (b): the corrected figure PASSES",
             "| `--warning` `#c47a00` on `#fdf5e6` | **3.16** | 4.5 normal text |\n", 0)
        case("check (b): one named hex plus the word 'white' pairs with the page surface",
             "| `--pink-700` `#c4006c` on white | **5.89** PASS |\n", 0)
        case("check (b): the same row with a wrong figure is rejected",
             "| `--pink-700` `#c4006c` on white | **5.99** PASS |\n", 1)
        case("check (b): a FLOOR is not a measurement — an unbolded 4.5 or a 3:1 in the Floor "
             "column must not be read as a stated ratio",
             "| `--x` `#000000` on white | 4.5 normal text | 3:1 |\n", 0)
        case("check (b): a WBS id in a table row is not a ratio",
             "| **OQ-040** | keep the supplied navy | 6.1 |\n", 0)
        case("check (b): PROSE is out of scope — the same wrong figure outside a table row is "
             "not reported, which is where every measured false positive was",
             "The warning title measures **3.18** on `#c47a00` over `#fdf5e6` in prose.\n", 0)
        case("check (b): a multi-figure row is declared UNCHECKABLE and PASSES, not silently "
             "verified",
             "| `--focus-ring` `#ec4ea3` | **3.40** white · **2.82** `#ede8f1` | 3.0 |\n", 0)
        case("check (b): the narrowing — two hexes AND the word 'white' is UNCHECKABLE, not "
             "paired. This is trustee-portal-visual-refresh-architecture.md:2136 in fixture "
             "form, whose second figure is bolded with trailing prose and does not parse",
             "| `--text-muted` `#8a8a8a` on white | **3.45** | 4.5 | on `#ede8f1` "
             "**2.86 — below even the 3:1 floor** |\n", 0)

        empty = base / "empty"
        empty.mkdir()
        checks.append(("a directory with no markdown FAILS", run([empty], repo_root=root) == 1))
        checks.append(("a missing directory FAILS",
                       run([base / "nope"], repo_root=root) == 1))
        checks.append(("a repo whose Entity.xml declares no rev_* column FAILS rather than "
                       "passing every claim",
                       run([base / "case0"], repo_root=base / "empty") == 1))

        # The arithmetic itself, against the two values IMP-0391 is about.
        computed = round(contrast_ratio("c47a00", "fdf5e6"), 2)
        checks.append((f"the WCAG formula gives 3.16 for #c47a00 on #fdf5e6 (got {computed})",
                       computed == 3.16))

        # IMP-0428: the finding must TELL the author how to word the correction, because this
        # gate cannot read a retraction and the authoring form is the whole mitigation. A
        # message-only assertion, deliberately: the gate's VERDICT is unchanged by this review.
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            run([base / "case0"], repo_root=root)
        emitted = buf.getvalue()
        checks.append(("check (a)'s finding tells the author to state the correction "
                       "SOURCE-FIRST (IMP-0428's mitigation, which is prose and must reach "
                       "the author at the moment the gate fires)",
                       "SOURCE-FIRST" in emitted))
        checks.append(("check (a)'s finding warns against adding a retraction phrase to this "
                       "gate — the escape hatch this review deliberately WITHHELD",
                       "escape hatch" in emitted))
        buf_b = io.StringIO()
        with contextlib.redirect_stderr(buf_b):
            run([base / "case6"], repo_root=root)
        checks.append(("check (b)'s finding tells the author to keep the RETRACTED figure out "
                       "of the table row and in the paragraph (IMP-0428)",
                       "RETRACTED figure" in buf_b.getvalue()))

    print("\n── SELFTEST ────────────────────────────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\ndesign-doc-claims selftest: FAILED — {len(failed)} check(s)", file=sys.stderr)
        return 1
    print(f"\ndesign-doc-claims selftest: OK — {len(checks)} check(s); the gate can fail.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="*", help="design document directories or files")
    parser.add_argument("--selftest", action="store_true",
                        help="prove this gate can fail, then exit")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.roots:
        parser.print_usage(sys.stderr)
        return 2
    return run([Path(r.rstrip("/")) for r in args.roots])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
