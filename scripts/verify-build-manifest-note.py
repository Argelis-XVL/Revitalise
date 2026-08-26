#!/usr/bin/env python3
"""A build manifest's free-text notes record COUNTS, never an inventory of shipped content.

WHY THIS FORBIDS A SHAPE INSTEAD OF CHECKING A CLAIM
---------------------------------------------------
`IMP-0324`. Build `20260825-1`'s `source_commit_note` said the packaged working tree "includes
the trustee-portal-visual-refresh changes (rev_roundfinance table, LandingPage/charts UI,
A-FIN-05/07/A-002 marker fixes)". No `LandingPage*`, chart or `RoundStatistics*` file existed
anywhere under `src/code-apps/`, and the built bundle in the same artifact contained none; the
Dev Summary correctly reported them as NOT STARTED. The dirty-path COUNT in the same note was
correct — `IMP-0078` required the sha and the count, and both were right. The note went further
and enumerated what the dirty tree contained, and that enumeration was written from the
dispatch's intended scope rather than from the tree.

Nothing reads manifest prose. `verify-build-config.py` validates steps, inputs and negative-test
coverage; no gate reads `manifest.json`'s free text, so any artefact name in it is unchecked and
travels into the deploy and into any acceptance pack built from the artifact.

**The obvious gate — extract every path-like token and resolve it to a real file — was NOT
built, and the reason is on the record.** That is fuzzy prose-matching, and fuzzy prose-matching
produced five distinct false-positive classes in one sitting on 2026-08-25 (`IMP-0319`). So this
forbids a CLASS OF CLAIM instead of adjudicating one: a note may not contain a filename-shaped
or `rev_*`-shaped token at all. **Zero false positives are structurally possible**, because
there is nothing to judge — the token is either there or it is not, and a note that needs one is
a note saying something it should not say.

WHAT IT CHECKS, over every free-text note field in a manifest:
  * no `rev_*` identifier  (a table, column or option set named as shipped content)
  * no filename-shaped token — `Something.tsx`, `foo.json`, `LandingPage.tsx`
  * no bare component-name token in `PascalCase.ext` form

Counts, shas, tool versions, plain prose and the words `src/`, `provisioning/`, `config/` as
DIRECTORIES are all fine: a directory is where the count was taken, not a claim about contents.

WHAT IT CANNOT DO: it cannot tell a true enumeration from a false one, and does not try. It
removes the ability to make either.

Usage
-----
    python3 scripts/verify-build-manifest-note.py <manifest.json | artifact-dir> [...]
    python3 scripts/verify-build-manifest-note.py --selftest

Exits 0 clean · 1 on any violation · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# Every field whose value is free text a human wrote. Kept explicit rather than "any string":
# `build_tool` and `build_os` legitimately carry version strings full of dots.
NOTE_FIELDS = ("source_commit_note", "note", "notes", "provenance_note", "packaging_note")

# A `rev_*` identifier — a table, column or option set named as shipped content.
PREFIXED_IDENT = re.compile(r"(?<![A-Za-z0-9_])(rev_[a-z][a-z0-9_]{2,})")
# A filename: a token with an extension this project actually ships.
FILENAME = re.compile(
    r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_-]+\.(?:tsx?|jsx?|json|xml|md|ps1|psm1|py|css|zip|yml|yaml))"
    r"(?![A-Za-z0-9_])")

# Directory names are not content claims: they say WHERE a count was taken.
ALLOWED_DIRS = {"src/", "provisioning/", "config/", "build/", "docs/", "scripts/", "logs/"}


def offenders(text: str) -> list[str]:
    found: list[str] = []
    found += [f"`{m}`" for m in dict.fromkeys(PREFIXED_IDENT.findall(text))]
    found += [f"`{m}`" for m in dict.fromkeys(FILENAME.findall(text))
              if not any(m.startswith(d) for d in ALLOWED_DIRS)]
    return found


def check_manifest(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"  MANIFEST UNREADABLE - {path}: {exc}"]
    if not isinstance(data, dict):
        return [f"  MANIFEST UNREADABLE - {path}: top level is not an object"]

    errors: list[str] = []
    for field in NOTE_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        bad = offenders(value)
        if bad:
            errors.append(
                f"  NOTE ENUMERATES CONTENT - {path} `{field}` names "
                f"{', '.join(bad)}. A manifest note records the dirty-path COUNT and stops "
                f"there (IMP-0078); enumerating what the tree CONTAINS restates the dispatch's "
                f"intended scope, not the tree, and nothing reads that prose — build 20260825-1 "
                f"claimed a LandingPage and charts that existed nowhere in the artifact "
                f"(IMP-0324). Point at `wbs`, `steps_not_executed` and the count instead."
            )
    return errors


def resolve(targets: list[str]) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    problems: list[str] = []
    for raw in targets:
        p = Path(raw)
        if p.is_dir():
            found = sorted(p.rglob("manifest.json"))
            if not found:
                problems.append(f"  NO MANIFEST - {p} contains no manifest.json. A gate with "
                                f"nothing to check must not report OK (IMP-0007).")
            paths += found
        elif p.is_file():
            paths.append(p)
        else:
            problems.append(f"  TARGET MISSING - {p} does not exist. A gate pointed at a "
                            f"missing target does not pass (IMP-0007).")
    return paths, problems


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_GOOD_NOTE = ("HEAD describes the last COMMIT only. 41 uncommitted paths exist under src/, "
              "provisioning/ and config/ at pack time — this build packaged the WORKING TREE "
              "(pac solution pack reads disk, not git), so source_commit is descriptive of "
              "ancestry only (IMP-0078's caution). See `wbs` for the contracted scope.")
_BAD_TABLE = _GOOD_NOTE + " It includes the rev_roundfinance table."
_BAD_FILE = _GOOD_NOTE + " It includes LandingPage.tsx and the charts."

_CASES: dict[str, tuple[dict, bool, str]] = {
    "a-note-naming-a-rev_-table-fails": (
        {"source_commit_note": _BAD_TABLE}, True, "`rev_roundfinance`"),
    "a-note-naming-a-filename-fails": (
        {"source_commit_note": _BAD_FILE}, True, "`LandingPage.tsx`"),
    # The real note from build 20260825-1, reduced to its shape: BOTH offences at once.
    "the-real-20260825-1-note-fails-on-both-counts": (
        {"source_commit_note": _GOOD_NOTE + " includes the trustee-portal-visual-refresh "
                                            "changes (rev_roundfinance table, LandingPage/charts "
                                            "UI, A-FIN-05/07/A-002 marker fixes)"},
        True, "NOTE ENUMERATES CONTENT"),
    # THE OVER-FIRING CONTROLS. Every one of these is a legitimate note or field.
    "a-count-only-note-naming-DIRECTORIES-passes": (
        {"source_commit_note": _GOOD_NOTE}, False, ""),
    "version-strings-full-of-dots-are-not-notes-and-must-not-be-scanned": (
        {"build_tool": "pac 2.4.1+g3799f3e (.NET 10.0.5)",
         "build_os": "Darwin 25.6.0 arm64", "source_commit_note": _GOOD_NOTE}, False, ""),
    "a-manifest-with-no-note-field-passes": (
        {"feature": "x", "source_tree_dirty_paths": 0}, False, ""),
    "an-empty-note-passes": (
        {"source_commit_note": "   "}, False, ""),
}


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (payload, expect_fail, want) in _CASES.items():
            path = Path(tmp) / f"{name}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = check_manifest(path)
            rc = 1 if errors else 0
            text = "\n".join(errors)
            ok = ((rc != 0) if expect_fail else (rc == 0)) and (not want or want in text)
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors:
                    print(f"                   {line}")
                failures.append(name)

        # Refusing to pass over nothing.
        empty = Path(tmp) / "emptydir"
        empty.mkdir()
        _paths, problems = resolve([str(empty)])
        ok = bool(problems)
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"a-directory-with-no-manifest-FAILS → {len(problems)} problem(s)")
        if not ok:
            failures.append("a-directory-with-no-manifest-FAILS")
        _paths, problems = resolve([str(Path(tmp) / "nope")])
        ok = bool(problems)
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"a-missing-target-FAILS → {len(problems)} problem(s)")
        if not ok:
            failures.append("a-missing-target-FAILS")

    if failures:
        print(f"\nverify-build-manifest-note: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-build-manifest-note: SELFTEST OK — {len(_CASES) + 2} fixtures, 4 of them "
          f"over-firing controls. This forbids a SHAPE, so zero false positives are structural.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("targets", nargs="*", help="manifest.json files, or directories to search")
    p.add_argument("--warn-only", action="store_true", help="report and exit 0")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()
    if not args.targets:
        p.error("give at least one manifest.json or directory (or --selftest)")

    paths, problems = resolve(args.targets)
    errors = list(problems)
    for path in paths:
        errors += check_manifest(path)

    if errors:
        label = "WARN" if args.warn_only else "FAILED"
        print(f"build-manifest-note: {label}\n" + "\n".join(errors), file=sys.stderr)
        return 0 if args.warn_only else 1
    print(f"build-manifest-note: OK — {len(paths)} manifest(s) checked; no note enumerates "
          f"shipped content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
