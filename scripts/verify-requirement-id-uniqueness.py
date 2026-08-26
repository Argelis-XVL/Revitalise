#!/usr/bin/env python3
"""One identifier means one requirement across docs/plans/ — checked against DECLARED ranges.

WHY THIS EXISTS
---------------
`IMP-0327`. `FR-056`–`FR-064`, `NFR-026`–`NFR-028` and `OQ-031`–`OQ-039` were independently
allocated TWICE: by approved Amendments A-02 and A-03 in `revitalise-grant-automation-plan.md`,
and by `revitalise-form-field-corrections-plan.md`, whose own header said it continues the
parent's numbering "so no identifier is reused". Both documents were internally consistent;
neither read the other; the draft's claim was true on the day it was written. **19 identifiers**
(as this gate measured it: FR-056–063, NFR-026–027, OQ-031–038, US-016) meant two different
requirements each — `FR-061` was applicant demographic distributions in one and applicant-consent
explanation retention in the other; `NFR-027` was the withdrawn minimum-cell-size rule in one and
necessity-argument recording in the other.

**RESOLVED 2026-08-26 by plan-agent.** `revitalise-form-field-corrections-plan.md` was retired to
a superseded stub declaring `id-allocation: none`, and its requirements merged into
`revitalise-grant-automation-plan.md` as Amendment A-04 under `FR-070`–`FR-077`,
`NFR-030`–`NFR-032`, `US-020`–`US-023` and `OQ-040`–`OQ-048`. The root cause was structural, and
worth stating because this gate only detects it: **a delta SDD that numbers itself by continuing
its parent's sequence collides with that parent as soon as the parent grows.** The grant-automation
plan is now the sole allocator for this solution, which is what every other delta feature here
already did. This gate stays: it is what will catch the next document that starts allocating.

**One identifier meaning one requirement is the premise every traceability matrix, evidence rule
and acceptance record in this repository rests on.** An acceptance pack citing a bare `FR-061`
could accept the wrong requirement. That is why one instance is enough here: the ladder's
"a tool could catch it mechanically" rung, not an instance count.

WHY IT READS A DECLARATION AND NOT THE DOCUMENT'S OWN IDS
---------------------------------------------------------
**This design is the result of the corpus measurement, not of the first idea.** The obvious
gate — parse every id in definition position, report any appearing in two documents — was
measured against the real corpus first: **31 candidate collisions across 3 documents, of which
15 ARE FALSE POSITIVES.** All fifteen come from `revitalise-grant-record-plan.md`, which states
at its line 12 that it "introduces no new functional requirements" and cites the parent's ids in
a traceability table. 48% wrong on first contact, before wiring.

**Prose cannot reliably separate an ALLOCATING document from a CITING one.** A declared range
can, exactly. So each plan document declares the blocks it allocates, in a machine-readable
comment, and this gate compares declarations.

THE DECLARATION. One HTML comment anywhere in the document — invisible when rendered:

    <!-- id-allocation: FR-056..FR-064, NFR-026..NFR-028, US-016..US-019, OQ-031..OQ-039 -->

A document that allocates nothing says so explicitly, which is a claim and not a silence:

    <!-- id-allocation: none -->

Single ids are accepted (`FR-070`) as well as ranges. Prefixes are free-form uppercase
(`FR`, `NFR`, `US`, `OQ`, `D`, …).

WHAT IT CHECKS
  1. OVERLAP. No two documents declare the same identifier. Reports both locations.
  2. DECLARED. Every document in the directory carries a declaration. A missing one is
     reported, because a document that allocates ids and declares no range is invisible to
     check 1 — and a gate whose coverage depends on people remembering is the class this
     repository has recorded thirteen times.

WHAT IT CANNOT DO, stated because it bounds the value:
  * It compares DECLARATIONS, not the ids a document actually uses. A declaration that has gone
    stale relative to its own body is not detected here — deliberately, because detecting it
    needs the definition-position parse measured above at 48% false positives.
  * It does not resolve a collision it finds. Which side renumbers is `plan-agent`'s decision,
    not this gate's. The 2026-08-26 resolution measured both sides before choosing: the
    trustee-portal side carried ~175 citations in the plan, ~169 in its TAD, two priced change
    orders and ~25 live source files, against ~55 for the draft. **Measure before assuming the
    draft is cheaper** — this gate's own error message says it "normally" is, and that word is
    doing real work.

Usage
-----
    python3 scripts/verify-requirement-id-uniqueness.py
    python3 scripts/verify-requirement-id-uniqueness.py --plans-dir DIR [--warn-only]
    python3 scripts/verify-requirement-id-uniqueness.py --selftest

Exits 0 clean · 1 on any violation · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

DECLARATION = re.compile(r"<!--\s*id-allocation:\s*(?P<body>.*?)-->", re.DOTALL | re.IGNORECASE)
RANGE = re.compile(r"^(?P<prefix>[A-Z]{1,6})-(?P<lo>\d+)(?:\s*\.\.\s*(?:(?P<hiprefix>[A-Z]{1,6})-)?"
                   r"(?P<hi>\d+))?$")
NONE_TOKEN = re.compile(r"^none$", re.IGNORECASE)


class BadDeclaration(Exception):
    pass


def expand(body: str) -> set[str]:
    """The identifiers a declaration allocates. Raises on a token it cannot read."""
    tokens = [t.strip() for t in re.split(r"[,\n]", body) if t.strip()]
    if not tokens:
        raise BadDeclaration("the declaration is empty. Say 'none' explicitly rather than "
                             "leaving it blank — a silence is not a claim")
    ids: set[str] = set()
    for token in tokens:
        if NONE_TOKEN.match(token):
            continue
        match = RANGE.match(token)
        if not match:
            raise BadDeclaration(f"cannot read {token!r}. Use `FR-056..FR-064`, `FR-056..064` "
                                 f"or a single `FR-070`")
        prefix = match.group("prefix")
        lo = int(match.group("lo"))
        hi = int(match.group("hi")) if match.group("hi") else lo
        hiprefix = match.group("hiprefix")
        if hiprefix and hiprefix != prefix:
            raise BadDeclaration(f"{token!r} spans two prefixes ({prefix} and {hiprefix}); "
                                 f"declare one range per prefix")
        if hi < lo:
            raise BadDeclaration(f"{token!r} counts backwards")
        width = len(match.group("lo"))
        for n in range(lo, hi + 1):
            ids.add(f"{prefix}-{n:0{width}d}")
    return ids


def read_declarations(plans_dir: Path) -> tuple[dict[str, set[str]], list[str]]:
    """(document -> allocated ids, problems). A document with no declaration is a problem."""
    problems: list[str] = []
    declared: dict[str, set[str]] = {}
    docs = sorted(plans_dir.glob("*.md"))
    if not docs:
        problems.append(f"  NO PLAN DOCUMENTS - {plans_dir} holds no *.md. A gate with nothing "
                        f"to check must not report OK (IMP-0007).")
        return declared, problems

    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        matches = DECLARATION.findall(text)
        if not matches:
            problems.append(
                f"  NO ID DECLARATION - {doc.name} declares no id allocation. Add one HTML "
                f"comment — `<!-- id-allocation: FR-056..FR-064, NFR-026..NFR-028 -->`, or "
                f"`<!-- id-allocation: none -->` for a document that cites the parent's ids "
                f"rather than allocating its own. Without it this document is invisible to the "
                f"overlap check, which is how FR-056+ came to mean two things (IMP-0327)."
            )
            continue
        ids: set[str] = set()
        failed = False
        for body in matches:
            try:
                ids |= expand(body)
            except BadDeclaration as exc:
                problems.append(f"  UNREADABLE DECLARATION - {doc.name}: {exc}")
                failed = True
        if not failed:
            declared[doc.name] = ids
    return declared, problems


def check(plans_dir: Path) -> tuple[int, list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    declared, problems = read_declarations(plans_dir)
    errors += problems

    # ── check 1: overlap ──
    owners: dict[str, list[str]] = {}
    for doc, ids in declared.items():
        for ident in ids:
            owners.setdefault(ident, []).append(doc)

    collisions = {i: d for i, d in owners.items() if len(d) > 1}
    if collisions:
        # Group by the SET of documents so one paragraph covers a whole clashing block, rather
        # than sixteen near-identical lines nobody reads to the end.
        by_pair: dict[tuple[str, ...], list[str]] = {}
        for ident, docs in collisions.items():
            by_pair.setdefault(tuple(sorted(docs)), []).append(ident)
        for docs, ids in sorted(by_pair.items()):
            errors.append(
                f"  ID ALLOCATED TWICE - {len(ids)} identifier(s) are declared by "
                f"{' AND '.join(docs)}: {', '.join(sorted(ids))}. One identifier must mean one "
                f"requirement — it is the premise every traceability matrix, evidence rule and "
                f"acceptance record rests on, and an acceptance pack citing a bare number could "
                f"accept the wrong requirement (IMP-0327). Renumber one side; the DRAFT is "
                f"normally the cheaper one. Until it is resolved, never cite a bare identifier "
                f"in this range without naming its source document."
            )

    total = sum(len(v) for v in declared.values())
    notes.append(f"  {len(declared)} document(s) declaring {total} identifier(s); "
                 f"{len(collisions)} identifier(s) allocated more than once")
    return (1 if errors else 0), errors, notes


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_PARENT = ("# Parent SDD\n\n<!-- id-allocation: FR-001..FR-064, NFR-001..NFR-028 -->\n\n"
           "Body text mentioning FR-061 and NFR-027 many times.\n")
_CLASH = ("# Draft delta\n\n<!-- id-allocation: FR-056..FR-064, NFR-026..NFR-028 -->\n\n"
          "It continues the parent's numbering so no identifier is reused.\n")
_CLEAN = ("# Clean delta\n\n<!-- id-allocation: FR-065..FR-070 -->\n\nBody.\n")
# The FALSE-POSITIVE shape the naive design got wrong 15 times: a document that cites the
# parent's ids everywhere and allocates none. It must be silent.
_CITING = ("# Citing delta\n\n<!-- id-allocation: none -->\n\n"
           "> **This document introduces no new functional requirements.**\n\n"
           "| Req | Where |\n|---|---|\n| FR-061 | parent §4 |\n| NFR-027 | parent §5 |\n"
           "| FR-056 | parent §4 |\n")
_UNDECLARED = "# Undeclared\n\nAdds FR-080 to FR-090 with no declaration anywhere.\n"

_CASES: dict[str, tuple[dict[str, str], bool, str]] = {
    # name: (files, expect_fail, expected substring)
    "two-documents-declaring-the-same-block-fails": (
        {"parent.md": _PARENT, "draft.md": _CLASH}, True, "ID ALLOCATED TWICE"),
    # 12 = FR-056..064 (9) + NFR-026..028 (3), reported as ONE message rather than twelve
    # near-identical lines nobody reads to the end.
    "one-message-per-clashing-PAIR-not-one-per-id": (
        {"parent.md": _PARENT, "draft.md": _CLASH}, True, "12 identifier(s) are declared by"),
    "adjacent-non-overlapping-blocks-pass": (
        {"parent.md": _PARENT, "clean.md": _CLEAN}, False, "declaring"),
    # THE CONTROL THAT DECIDED THE DESIGN. Under the naive definition-position parse this
    # document produced 15 false positives; a declared range makes it exactly silent.
    "a-CITING-document-declaring-none-must-be-silent": (
        {"parent.md": _PARENT, "citing.md": _CITING}, False, "2 document(s)"),
    "a-document-with-no-declaration-is-reported": (
        {"parent.md": _PARENT, "undeclared.md": _UNDECLARED}, True, "NO ID DECLARATION"),
    "an-empty-declaration-is-refused-rather-than-read-as-none": (
        {"parent.md": _PARENT, "x.md": "# X\n\n<!-- id-allocation:  -->\n"}, True,
        "Say 'none' explicitly"),
    "an-unreadable-token-is-refused": (
        {"parent.md": _PARENT, "x.md": "# X\n\n<!-- id-allocation: FR56-FR64 -->\n"}, True,
        "cannot read"),
    "a-backwards-range-is-refused": (
        {"parent.md": _PARENT, "x.md": "# X\n\n<!-- id-allocation: FR-064..FR-056 -->\n"}, True,
        "counts backwards"),
    "a-range-spanning-two-prefixes-is-refused": (
        {"parent.md": _PARENT, "x.md": "# X\n\n<!-- id-allocation: FR-056..NFR-060 -->\n"}, True,
        "spans two prefixes"),
    "an-empty-directory-FAILS-rather-than-reporting-OK": (
        {}, True, "NO PLAN DOCUMENTS"),
}


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (files, expect_fail, want) in _CASES.items():
            root = Path(tmp) / name
            root.mkdir(parents=True)
            for rel, body in files.items():
                (root / rel).write_text(body, encoding="utf-8")
            rc, errors, notes = check(root)
            text = "\n".join(errors + notes)
            ok = ((rc != 0) if expect_fail else (rc == 0)) and want in text
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors + notes:
                    print(f"                   {line}")
                failures.append(name)
    if failures:
        print(f"\nverify-requirement-id-uniqueness: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-requirement-id-uniqueness: SELFTEST OK — {len(_CASES)} fixtures, "
          f"including the citing-document control that the naive design got wrong 15 times.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plans-dir", type=Path, default=Path("docs/plans"))
    p.add_argument("--warn-only", action="store_true",
                   help="report and exit 0 — what makes the build step SOFT")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()

    rc, errors, notes = check(args.plans_dir)
    if rc:
        label = "WARN" if args.warn_only else "FAILED"
        print(f"requirement-id-uniqueness: {label}\n" + "\n".join(errors + notes),
              file=sys.stderr)
        return 0 if args.warn_only else rc
    print("requirement-id-uniqueness: OK\n" + "\n".join(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
