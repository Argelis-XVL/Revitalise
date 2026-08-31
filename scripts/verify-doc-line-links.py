#!/usr/bin/env python3
"""WIRED as the HARD `doc-line-links` build step: an identifier-labelled line-link must land in
the section that identifier names.

Class `gate-scope-mismatch` / the dangling-citation half of IMP-0430. Asserts on VALUES only:
does the target line, or the section containing it, carry the identifier the link label names?
No prose semantics anywhere.

HISTORY, and it is history rather than status (IMP-0465). This file was authored as a measured
CANDIDATE in a scratchpad and wired into
`config/revitalise-grant-automation-build.yml` (step `doc-line-links`, over `docs/architecture`
and `docs/plans`) in a later pass that updated the build config and not this docstring. For a
day the opening line read "CANDIDATE (scratchpad, not wired)" while the step was HARD and
passing, so an agent deciding whether its document edits were enforced got the wrong answer from
the file and the right one only from the config. `scripts/verify-build-config.py` now asserts
that a wired script's docstring does not deny its own wiring, so this cannot recur silently.

NARROWING 1 — the label must be a STRUCTURED identifier (`§3.4`, `A-R24`, `C-TECH-062`,
`IMP-0433`, `ADR-038`, `OQ-027`, `FR-061`, `NFR-026`, `EX-003`, `TD-07`). A bare integer is
NOT one: labels of the form `[line 142]` and `[Revision 5]` say what they are and claim no
section. Removes 44 of 102 raw findings across docs/.

NARROWING 2 — SECTION SCOPE, not a +/-3 line window. A link may deep-link INTO the body of the
section it names; it is dangling only if the identifier appears in neither the target line nor
the nearest enclosing markdown heading above it. Removes
docs/plans/revitalise-grant-automation-plan.md:348 `[Architecture §3.1]` -> `#L317` BY NAME:
§3.1's heading is at L286 and L317 is a table row inside that section, so the reader lands in
the right place.
"""
from __future__ import annotations
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
LINK = re.compile(r"\[([^\]]{1,80})\]\(([^)\s]+?\.md)#L(\d+)(?:-L?\d+)?\)")
IDENT = re.compile(
    r"^(?:§|S)\d+(?:\.\d+)*[a-z]?$|^A-R\d+$|^C-[A-Z]+-\d+$|^IMP-\d+$"
    r"|^ADR-[A-Z0-9-]+$|^OQ-\d+$|^FR-\d+$|^NFR-\d+$|^EX-\d+$|^TD-\d+$"
)
HEADING = re.compile(r"^#{1,6}\s+(.*)$")


def resolve(doc: pathlib.Path, rel: str, repo: pathlib.Path) -> pathlib.Path | None:
    for base in (doc.parent, repo):
        try:
            c = (base / rel).resolve()
        except OSError:
            continue
        if c.exists():
            return c
    return None


def enclosing_heading(lines: list[str], n: int) -> str:
    for i in range(min(n, len(lines)) - 1, -1, -1):
        m = HEADING.match(lines[i])
        if m:
            return m.group(1)
    return ""


def run(roots: list[pathlib.Path], repo: pathlib.Path) -> tuple[list[str], int, int]:
    findings: list[str] = []
    total = ident = 0
    for root in roots:
        if not root.exists():
            print(f"design-doc-links: FAIL — {root} does not exist", file=sys.stderr)
            return ["MISSING ROOT " + str(root)], 0, 0
        for p in sorted(root.rglob("*.md")):
            for ln, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                for m in LINK.finditer(line):
                    total += 1
                    label = m.group(1).strip().strip("`*").strip()
                    cand = label.split()[-1].strip("`*.,;:") if label else ""
                    if not IDENT.match(cand):
                        continue          # narrowing 1
                    ident += 1
                    tgt = resolve(p, m.group(2), repo)
                    if tgt is None:
                        findings.append(f"{p}:{ln}: [{label}] -> {m.group(2)} — target file does not exist")
                        continue
                    tl = tgt.read_text(encoding="utf-8").splitlines()
                    n = int(m.group(3))
                    if n > len(tl):
                        findings.append(f"{p}:{ln}: [{label}] -> {m.group(2)}#L{n} — past end of file ({len(tl)} lines)")
                        continue
                    needle = cand.lstrip("§S") if cand[0] in "§S" else cand
                    if needle in tl[n - 1] or cand in tl[n - 1]:
                        continue
                    head = enclosing_heading(tl, n)   # narrowing 2
                    if needle in head or cand in head:
                        continue
                    findings.append(
                        f"{p}:{ln}: [{label}] -> {m.group(2)}#L{n} — neither that line nor its "
                        f"section heading ({head[:50] or 'none'!r}) carries {cand}"
                    )
    return findings, total, ident


def selftest() -> int:
    """Prove the gate can fail, and that each narrowing removes what it claims to."""
    import tempfile
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        target = base / "docs" / "architecture"
        target.mkdir(parents=True)
        # L1 heading, L4 §3.4's heading, L5 §3.4's body, L6 §9.9's heading, L7 §9.9's body,
        # L8 an A-R24 risk row. The two sections are what separate "deep link into the right
        # section" from "points at the wrong section entirely".
        (target / "arch.md").write_text(
            "# Doc\n\nintro\n"            # L1-3
            "### 3.4 The ethnic-group column\n"   # L4
            "body of three-four\n"                # L5
            "### 9.9 Something else entirely\n"   # L6
            "body of nine-nine\n"                 # L7
            "| **A-R24** | the risk row | Medium |\n",   # L8
            encoding="utf-8")
        src = base / "docs" / "plans"
        src.mkdir(parents=True)

        def case(label: str, body: str, expected: int) -> None:
            (src / "plan.md").write_text(body, encoding="utf-8")
            findings, _, _ = run([src], base)
            checks.append((label, (1 if findings else 0) == expected))

        case("a link pointing into a DIFFERENT section than its label names is reported — "
             "plan.md:1126 [§3.4] -> #L363's exact shape, IMP-0430's defect",
             "see [§3.4](../architecture/arch.md#L7) for detail\n", 1)
        case("a link landing ON the identifier's own heading PASSES",
             "see [§3.4](../architecture/arch.md#L4) for detail\n", 0)
        case("narrowing 2 — a DEEP LINK into the BODY of the section it names PASSES; this is "
             "plan.md:348 [Architecture §3.1] -> #L317 removed BY NAME, the one measured false "
             "positive of the six",
             "see [Architecture §3.4](../architecture/arch.md#L5) for detail\n", 0)
        case("a link landing on a risk-table ROW carrying its own id PASSES",
             "see [A-R24](../architecture/arch.md#L8) for the risk\n", 0)
        case("a risk id pointing at the WRONG row is reported — plan.md:1126 [A-R24] -> #L924",
             "see [A-R24](../architecture/arch.md#L5) for the risk\n", 1)
        case("narrowing 1 — a label that is a BARE LINE NUMBER is not an identifier claim "
             "([line 142], [Revision 5] — 44 of 102 raw findings removed by this)",
             "see [line 6](../architecture/arch.md#L6) and [Revision 5](../architecture/arch.md#L6)\n",
             0)
        case("a link PAST END OF FILE is reported",
             "see [§3.4](../architecture/arch.md#L9999)\n", 1)
        case("a link to a MISSING FILE is reported",
             "see [§3.4](../architecture/nope.md#L4)\n", 1)

        findings, _, _ = run([base / "does-not-exist"], base)
        checks.append(("a missing root FAILS rather than passing over nothing (IMP-0007)",
                       bool(findings)))

    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\ndoc-line-links selftest: FAILED — {len(failed)} check(s)", file=sys.stderr)
        return 1
    print(f"\ndoc-line-links selftest: OK — {len(checks)} check(s); the gate can fail.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("roots", nargs="*", default=["docs/architecture", "docs/plans"])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--selftest", action="store_true",
                    help="prove this gate can fail, then exit")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    repo = pathlib.Path(a.repo).resolve()
    findings, total, ident = run([pathlib.Path(r) for r in a.roots], repo)
    for f in findings:
        print("DANGLING: " + f, file=sys.stderr)
    if findings:
        print(f"\ndoc-line-links: FAILED — {len(findings)} dangling of {ident} "
              f"identifier-labelled link(s) ({total} line-link(s) read). A line number is stale "
              f"the next time either file is edited, and the pass that writes the pointer never "
              f"edits the target (IMP-0389) — prefer citing the SECTION IDENTIFIER without "
              f"'#Lnnn', or re-grep the number.", file=sys.stderr)
        return 1
    print(f"doc-line-links: OK — {total} line-link(s), {ident} identifier-labelled, all resolving "
          f"to a line or a section heading carrying that identifier. NOT covered: labels that are "
          f"not structured identifiers, and the 56 dangling links in docs/development, docs/tests "
          f"and docs/improvements — approved deliverables and historical reviews nobody owns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
