#!/usr/bin/env python3
"""C-TECH-075 — a supplied design artefact is intake'd by FULL DIRECTORY ENUMERATION,
not by the first folder found.

WHY THIS EXISTS (IMP-0028, IMP-0384, IMP-0510 — the THIRD instance)
--------------------------------------------------------------------
`CLAUDE.md`'s supplied-assets rule ends: *"A third instance is what would justify building
one [a gate]."* `IMP-0028` was a WBS quoting workbook read by nobody; `IMP-0384` was a design
system arriving in a directory named nowhere; `IMP-0510` is a supplied drop read exactly one
folder deep. The repository set its own threshold and the threshold is met.

`IMP-0510` concretely: the 2026-08-27 intake of `Designsystem/Revitalise Design System/` read
`readme.md` and `tokens/`, and never enumerated the sibling `ui_kits/trustee-review-portal/` —
seven files, an app-specific reference for the exact three screens the feature restyles,
created the same day. The TAD cited three paths under that drop and not that one.

WHAT IT ASSERTS — A VALUE, NOT A PHRASE
---------------------------------------
This compares a DIRECTORY LISTING against CITED PATHS. Both are values. That matters: five
prior prose gates in this repository were phrase-matchers over documentation and measured at
48%-100% false (IMP-0422), one of them going red on the erratum written to satisfy it
(IMP-0428). The rule that followed those measurements — *assert on values, not on phrases,
wherever a value exists* — is satisfiable here, and this gate is what satisfying it looks
like. Its failure mode is a renamed folder, not a rephrased sentence.

THE MATCH RULE, and why it is not "flag every uncited folder"
--------------------------------------------------------------
A subdirectory of a supplied drop is IN SCOPE only when its name matches a deliverable this
repository actually builds — a directory under `src/code-apps/`. `ui_kits/marketing-site/` is
a sibling of identical shape whose name matches no such deliverable, and it is correctly NOT
reported; flagging every uncited folder would have reported 16 in this drop alone. The
negative control is what makes the measurement meaningful rather than tautological.

RESIDUAL, stated because it is not covered: this checks that a matching folder is CITED, not
that it was OBEYED. A TAD can cite `ui_kits/trustee-review-portal/` and still convert the
wrong thing. Citation is the floor — it makes the artefact's existence impossible to miss —
and the design judgement above it belongs to architect-agent.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SUPPLIED_ROOTS = ("Designsystem",)
ARCHITECTURE_DIR = Path("docs") / "architecture"
DELIVERABLE_DIR = Path("src") / "code-apps"
SKIP_DIRS = {".git", "node_modules", "dist", "__pycache__", ".vite", "coverage"}


def deliverable_names(root: Path) -> set[str]:
    """The names of things this repository builds — currently the Code Apps.

    Read from the tree, never transcribed, so a new app is covered without editing this gate.
    """
    base = root / DELIVERABLE_DIR
    if not base.is_dir():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir() and p.name not in SKIP_DIRS}


def supplied_subdirectories(root: Path) -> list[Path]:
    """Every subdirectory, at any depth, of every supplied design drop."""
    found: list[Path] = []
    for name in SUPPLIED_ROOTS:
        base = root / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_dir() and not (set(path.parts) & SKIP_DIRS):
                found.append(path)
    return found


def architecture_text(root: Path) -> tuple[str, int]:
    """Every architecture document concatenated, plus the file count."""
    base = root / ARCHITECTURE_DIR
    if not base.is_dir():
        return "", 0
    docs = sorted(base.glob("*.md"))
    return "\n".join(d.read_text(encoding="utf-8", errors="replace") for d in docs), len(docs)


def citation_key(path: Path, root: Path) -> str:
    """The value a TAD writes when it cites this directory: `<parent>/<name>`.

    The full repo-relative path is not the right needle — documents legitimately abbreviate
    the long supplied-drop prefix (`ui_kits/.../ApplicationsList.jsx`). The last two
    components are specific enough to identify the folder and short enough to survive that
    abbreviation.
    """
    rel = path.relative_to(root)
    parts = rel.parts
    return "/".join(parts[-2:]) if len(parts) >= 2 else rel.name


def scan(root: Path) -> tuple[list[str], dict[str, int]]:
    names = deliverable_names(root)
    subdirs = supplied_subdirectories(root)
    text, doc_count = architecture_text(root)

    stats = {
        "deliverables": len(names),
        "subdirectories": len(subdirs),
        "architecture_docs": doc_count,
        "in_scope": 0,
    }

    findings: list[str] = []
    if not subdirs:
        return findings, stats

    for path in subdirs:
        if path.name not in names:
            continue
        stats["in_scope"] += 1
        key = citation_key(path, root)
        if key in text:
            continue
        file_count = sum(1 for p in path.iterdir() if p.is_file())
        findings.append(
            f"{path.relative_to(root)}: a supplied design directory whose name matches the "
            f"deliverable `{path.name}` under {DELIVERABLE_DIR}/, holding {file_count} file(s), "
            f"is cited by no document in {ARCHITECTURE_DIR}/ ({doc_count} searched; needle "
            f"`{key}`). Read it and cite the path, or record in the TAD that it is out of "
            f"scope and why. A supplied artefact read one folder deep is the defect "
            f"C-TECH-075 exists to stop (IMP-0028, IMP-0384, IMP-0510)."
        )
    return findings, stats


# ── selftest ──────────────────────────────────────────────────────────────────────────────

def build_fixture(root: Path, *, cite: bool) -> None:
    (root / DELIVERABLE_DIR / "widget-portal" / "src").mkdir(parents=True, exist_ok=True)
    drop = root / "Designsystem" / "Some Design System"
    (drop / "ui_kits" / "widget-portal").mkdir(parents=True, exist_ok=True)
    (drop / "ui_kits" / "widget-portal" / "Screen.jsx").write_text("x", encoding="utf-8")
    # The negative control: same shape, name matches no deliverable.
    (drop / "ui_kits" / "marketing-site").mkdir(parents=True, exist_ok=True)
    (drop / "tokens").mkdir(parents=True, exist_ok=True)

    arch = root / ARCHITECTURE_DIR
    arch.mkdir(parents=True, exist_ok=True)
    body = "# TAD\n\nThe drop supplies tokens/colors.css.\n"
    if cite:
        body += "ADR-040 reads `ui_kits/widget-portal/` in full.\n"
    (arch / "thing-architecture.md").write_text(body, encoding="utf-8")


def selftest() -> int:
    cases = [
        ("a matching supplied directory cited nowhere FAILS", False, 1),
        ("the same directory, cited by the TAD, PASSES", True, 0),
    ]
    failures = 0
    for name, cite, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root, cite=cite)
            findings, stats = scan(root)
            ok = len(findings) == expected
            print(f"  {'ok  ' if ok else 'FAIL'} {name}: expected {expected}, "
                  f"got {len(findings)} (in scope: {stats['in_scope']}, "
                  f"subdirectories: {stats['subdirectories']})")
            if not ok:
                failures += 1
                for finding in findings:
                    print(f"        {finding}")
    # The negative control is load-bearing: assert it explicitly, not by arithmetic.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_fixture(root, cite=True)
        findings, _ = scan(root)
        ok = not any("marketing-site" in f for f in findings)
        print(f"  {'ok  ' if ok else 'FAIL'} negative control: an uncited sibling matching no "
              f"deliverable is NOT reported")
        if not ok:
            failures += 1
    print(f"verify-design-source-coverage: selftest 3 fixture(s), {failures} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(REPO_ROOT),
                        help="repository root to scan (default: this repository)")
    parser.add_argument("--selftest", action="store_true",
                        help="run the fixtures that prove this gate can fail")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    root = Path(args.root).resolve()
    findings, stats = scan(root)

    if not findings:
        print(f"verify-design-source-coverage: PASS — {stats['subdirectories']} supplied "
              f"subdirectory(ies), {stats['in_scope']} matching a deliverable, all cited "
              f"across {stats['architecture_docs']} architecture document(s).")
        return 0

    for finding in findings:
        print(f"verify-design-source-coverage: {finding}")
    print(f"verify-design-source-coverage: FAILED — {len(findings)} uncited supplied "
          f"directory(ies) of {stats['in_scope']} in scope.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
