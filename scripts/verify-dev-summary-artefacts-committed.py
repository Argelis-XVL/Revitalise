#!/usr/bin/env python3
"""Every source path a Dev Summary cites must be TRACKED BY GIT. Reports the ones that are not.

WHY THIS EXISTS
---------------
`IMP-0486`, a blocker. A Dev Summary stated *"TAD Revision 4 implemented in full: the supplied
design system adopted as a typed component and token layer"*, and the reviewer's own screenshots
two days later showed the pre-refresh UI. The entire conversion — `src/components/ds/`,
`ds-tokens.css`, `ds.module.css`, every consuming component — was sitting untracked in a working
tree. It existed. It compiled. A falsified gate passed over it. None of that is evidence that
anything shipped, and a reviewer deciding what to expect on screen reads "implemented in full" as
V4.

WHAT IT ASSERTS ON, AND WHAT IT DELIBERATELY DOES NOT
-----------------------------------------------------
It asserts on **git's answer**: is this path in `git ls-files`? That is a fact about a commit.

The obvious alternative was measured first and REJECTED: requiring a commit sha near any
*"shipped" / "implemented in full" / "live"* sentence scored **99 hits across 7 documents, ≈83%
false** — "the shipped bundle" (build output), "'already shipped' and trustee-visible" (quoting
another document), "would have shipped a…" (a counterfactual), "What shipped carries no `<v>`"
(describing XML). That is squarely in the 48–100% band this repository has now measured five
times (`IMP-0422`, `IMP-0428`), and `agents/improvement-agent.md` is explicit: **assert on VALUES,
not on PHRASES, wherever a value exists.** A commit is a value.

The polarity consequence matters and is why this design is safe where the phrase design was not: a
document CORRECTED by committing its artefacts scores strictly BETTER, never worse. A retained
erratum phrase inverts a phrase-based gate; nothing about a commit can invert this one.

WHY IT IS SOFT
--------------
During normal development a Dev Summary legitimately cites work that is not committed yet. A HARD
gate would be red for the whole of every in-flight feature and would be routed around within a day
— the measured lesson of `IMP-0439` and `IMP-0477` (`hard-gate-red-on-pre-existing-debt`, ×2). So
this reports; it does not halt. `--warn-only` exits 0, which is the mechanism `derived-counts`
already uses to wire a SOFT check into a build config whose steps declare no severity.

SCOPE, stated because a gate's silence is not a result
------------------------------------------------------
* Only paths that EXIST on disk are judged. A cited path that exists nowhere is a *stale citation*
  — a different defect, and judging it here would false-positive on globs, illustrative paths and
  renamed files. Reported as a separate count, never as a finding.
* Only regular files. A cited directory is not a thing `git ls-files` can answer about.
* It cannot read the SENTENCE. A Dev Summary that cites only committed files and still overclaims
  in prose passes clean. `C-TECH-053`'s deploy-side rung is the half that governs the wording, and
  it is prose because no gate can judge it.

Usage
-----
    python3 scripts/verify-dev-summary-artefacts-committed.py [docs/development ...]
    python3 scripts/verify-dev-summary-artefacts-committed.py --warn-only   # SOFT wiring
    python3 scripts/verify-dev-summary-artefacts-committed.py --selftest

Exits 0 clean (or always, under --warn-only) · 1 with findings · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = ("docs/development",)

# Top-level directories of this repository. A path is a candidate only when it is rooted at one
# of them, which is what keeps prose fragments and URLs out of the corpus.
TOP_LEVEL = (
    "src", "provisioning", "scripts", "config", "contract", "docs", "knowledge", "skills",
    "agents", "templates", "constraints", "build", "logs", "tests",
)

# `src/foo/bar.ts`, with an extension. Deliberately requires the extension: a directory is not
# something git ls-files can answer about, and a bare word is not a path.
PATH_RE = re.compile(
    r"(?<![\w/.-])(?:\.{1,2}/)*(?P<path>(?:" + "|".join(TOP_LEVEL) + r")"
    r"(?:/[\w.@%+-]+)*"
    r"/[\w.@%+-]+\.[A-Za-z0-9]{1,6})")

# Trailing punctuation a sentence leaves glued to a path.
TRAILING = ").,;:'\"`]}"


def cited_paths(text: str) -> list[str]:
    """Every repository-rooted file path this document names, de-duplicated, in first-seen order."""
    seen: dict[str, None] = {}
    for m in PATH_RE.finditer(text):
        raw = m.group("path").rstrip(TRAILING)
        if raw:
            seen.setdefault(raw, None)
    return list(seen)


def tracked_set(repo: Path) -> set[str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-files"],
                         capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise SystemExit(f"verify-dev-summary-artefacts-committed: `git ls-files` failed in "
                         f"{repo} — {out.stderr.strip()}. A gate whose input is unavailable must "
                         f"fail, not pass over nothing (IMP-0007).")
    return set(out.stdout.split("\n")) - {""}


def documents(repo: Path, roots: list[str]) -> list[Path]:
    found: list[Path] = []
    for r in roots:
        p = (repo / r) if not Path(r).is_absolute() else Path(r)
        if p.is_dir():
            found.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            found.append(p)
    return found


def run(repo: Path, roots: list[str], tracked: set[str] | None = None) -> tuple[list[str], dict]:
    docs = documents(repo, roots)
    if not docs:
        raise SystemExit(f"verify-dev-summary-artefacts-committed: no .md documents found under "
                         f"{', '.join(roots)}. A gate with no inputs must fail (IMP-0007).")
    known = tracked_set(repo) if tracked is None else tracked
    findings: list[str] = []
    stats = {"documents": len(docs), "paths": 0, "judged": 0, "absent": 0, "findings": 0}
    distinct: set[str] = set()

    for doc in docs:
        rel_doc = doc.relative_to(repo).as_posix() if doc.is_relative_to(repo) else doc.as_posix()
        for path in cited_paths(doc.read_text(encoding="utf-8", errors="replace")):
            distinct.add(path)
            target = repo / path
            if not target.is_file():
                # A stale citation, or a glob, or an illustrative path. Counted, never a finding.
                stats["absent"] += 1
                continue
            stats["judged"] += 1
            if path in known:
                continue
            stats["findings"] += 1
            findings.append(
                f"{rel_doc} cites {path}, which EXISTS on disk and is NOT tracked by git. The "
                f"document's claims about it are claims about an uncommitted working tree: it "
                f"has not been committed, so it cannot have been built from a commit, deployed, "
                f"or seen by anyone but this machine. Either commit it, or state the claim as "
                f"'authored, not yet deployed' (C-TECH-053, IMP-0486).")
    stats["paths"] = len(distinct)
    return findings, stats


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# Fixtures prove the gate CAN fail. The corpus run is what proves it fails on the right things,
# and its measured precision belongs in the review that wires it (IMP-0319).

def selftest() -> int:
    failures: list[str] = []

    def case(why: str, ok: bool, detail: str = "") -> None:
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {why}{(' — ' + detail) if detail else ''}")
        if not ok:
            failures.append(why)

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / "docs/development").mkdir(parents=True)
        (repo / "src/components").mkdir(parents=True)
        (repo / "src/components/Tracked.tsx").write_text("//\n", encoding="utf-8")
        (repo / "src/components/Untracked.tsx").write_text("//\n", encoding="utf-8")
        doc = repo / "docs/development/feature-dev-summary.md"

        doc.write_text("The conversion ships in `src/components/Tracked.tsx`.\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked={"src/components/Tracked.tsx"})
        case("a cited path that IS tracked produces no finding", not f and s["judged"] == 1,
             f"{s}")

        doc.write_text("Implemented in full: `src/components/Untracked.tsx`.\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked={"src/components/Tracked.tsx"})
        case("a cited path that exists and is UNTRACKED is a finding",
             len(f) == 1 and "NOT tracked by git" in f[0], f"{len(f)} finding(s)")

        doc.write_text("See `src/components/Gone.tsx` and `src/**/*.tsx`.\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked=set())
        case("a cited path that does NOT exist is counted, never a finding",
             not f and s["absent"] >= 1, f"absent={s['absent']}")

        doc.write_text("Nothing here names a path at all.\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked=set())
        case("a document naming no path yields nothing", not f and s["paths"] == 0)

        doc.write_text("Both `src/components/Tracked.tsx` and `src/components/Untracked.tsx`, "
                       "and `src/components/Untracked.tsx` again.\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked={"src/components/Tracked.tsx"})
        case("a path cited twice in one document is reported once",
             len(f) == 1 and s["paths"] == 2, f"{len(f)} finding(s), {s['paths']} path(s)")

        # A markdown link with a relative prefix resolves to the same repository path.
        doc.write_text("See [the file](../../src/components/Untracked.tsx).\n", encoding="utf-8")
        f, s = run(repo, ["docs/development"], tracked=set())
        case("a relative markdown link is normalised to its repository path",
             len(f) == 1 and "src/components/Untracked.tsx" in f[0])

        # Refusing to pass over nothing (IMP-0007).
        empty = repo / "docs/empty"
        empty.mkdir()
        try:
            run(repo, ["docs/empty"], tracked=set())
            case("a corpus with no documents ABORTS rather than passing", False)
        except SystemExit:
            case("a corpus with no documents ABORTS rather than passing", True)

    if failures:
        print(f"\nverify-dev-summary-artefacts-committed: SELFTEST FAILED — "
              f"{len(failures)} case(s)", file=sys.stderr)
        return 1
    print("\nverify-dev-summary-artefacts-committed: SELFTEST OK — 7 fixtures. Fixtures prove it "
          "CAN fail; the corpus run is what proves it fails on the right things.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("roots", nargs="*", default=list(DEFAULT_ROOTS),
                   help="documents or directories to read (default: docs/development)")
    p.add_argument("--warn-only", action="store_true",
                   help="print findings and exit 0 — this gate is SOFT, and this is how it is "
                        "wired into a build config whose steps declare no severity")
    p.add_argument("--selftest", action="store_true", help="run the fixture suite and exit")
    p.add_argument("--repo", default=str(REPO), help="repository root")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()

    repo = Path(args.repo).resolve()
    roots = args.roots or list(DEFAULT_ROOTS)
    findings, stats = run(repo, roots)

    for f in findings:
        print(f"  UNCOMMITTED: {f}")
    tail = (f"{stats['documents']} document(s), {stats['paths']} distinct cited path(s), "
            f"{stats['judged']} judged, {stats['absent']} cited but absent from disk "
            f"(not judged — a stale citation is a different defect)")
    if findings:
        print(f"verify-dev-summary-artefacts-committed: {len(findings)} finding(s) "
              f"(SOFT — report as WARN, do not block) — {tail}")
        return 0 if args.warn_only else 1
    print(f"verify-dev-summary-artefacts-committed: OK — {tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
