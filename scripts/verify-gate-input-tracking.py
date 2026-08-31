#!/usr/bin/env python3
"""No gate under scripts/ selects an input the repository ignores. Stdlib only.

WHY THIS EXISTS. `IMP-0410`, a blocker, and the fourth instance of `gate-scope-mismatch` — the
first in which **the gate's own input selection** is the defect rather than a document's
description of it.

`verify-audited-tables.py`'s `SETTINGS_GLOB` matched
`provisioning/deploymentSettings/acc-settings.json`: a Pester fixture written by
`New-SettingsFixture`, gitignored at `.gitignore:58` with the stated reason *"so a crashed run
cannot leave a fixture that gets committed and then read as a real settings file"*. The ignore
rule stopped it being committed and did nothing about it being READ. An interrupted run left it
behind, the HARD `audited-tables` step went red on 13 undeclared table/environment pairs inside a
throwaway file, and **no commit could turn it green** — while on a CI runner, where the fixture
never exists, the same gate passed. A gate whose verdict depends on local filesystem state is not
a gate.

An instance patch was forbidden here (`skills/how-to-promote-a-finding.md` L44, the altitude
rule), so the fix is a shared helper (`scripts/lib/tracked_paths.py`) plus this lock, which stops
the NEXT gate acquiring the same defect.

WHAT IT CHECKS. Every `*.glob(...)` / `*.rglob(...)` call under `scripts/`, extracted from the
AST — never grepped, because a pattern inside a docstring or a comment is `IMP-0020`'s trap.
Module-level string constants are resolved, so `SETTINGS_GLOB` is followed to its value. A pattern
is EXPANDED and checked only when both halves are known:

  * the pattern resolves to a string literal that does not begin with `*`, and
  * the receiver is recognisably the repository root — a name in `REPO_ROOT_NAMES`.

Anything else is UNRESOLVED and reported as a coverage gap, never as a finding. This narrowing is
not fastidiousness: the first draft of this gate expanded a bare `*` from the wrong base and
measured **4 findings, 0 true, 4 false**, three of them its own extractor's fault
(`docs/improvements/2026-08-28-improvement-review-4.md` section 6).

DECLARING YOUR OWN HANDLING. Two gates read ignored paths BY DESIGN and must not adopt the
helper: `verify-build-manifest-note.py` globs `build/artifacts/` (931 files, 909 ignored — a
blanket exclusion would empty its input set and, under its own no-inputs rule, fail it), and
`verify-toolchain-claims.py` filters `node_modules` with a hardcoded string. A script says so by
carrying a line containing:

    GATE-INPUT-TRACKING: <why this script's ignored inputs are correct>

or by importing `tracked_glob` from `scripts/lib/tracked_paths.py`. Declared scripts are SKIPPED
and NAMED in the output — a silent skip list is the thing this gate exists to prevent.

WHAT IT DOES NOT COVER, stated because the gate reads as more complete than it is:
  * UNANCHORED patterns applied to a base computed at runtime. They are the majority.
  * `verify-audited-tables.py` itself, now that it declares handling — so this lock protects
    FUTURE gates and no longer its own founding instance. That is a regression lock, not coverage.
  * Nothing forces a new gate to call the helper. This gate only fires once the ignored path
    actually exists on the machine running it.

Run:
    python3 scripts/verify-gate-input-tracking.py
    python3 scripts/verify-gate-input-tracking.py --selftest

Exits 0 when no resolvable gate input is ignored, 1 on any, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from tracked_paths import IgnoreCheckUnavailable, ignored_paths  # noqa: E402

SCRIPTS_GLOB = "scripts/*.py"
GLOB_METHODS = ("glob", "rglob")

# Receiver names that ARE the repository root. Deliberately short: a pattern expanded from the
# wrong base is a false positive, and this gate has already measured that mistake once.
REPO_ROOT_NAMES = ("repo_root", "REPO_ROOT")

DECLARATION_MARKER = "GATE-INPUT-TRACKING:"
HELPER_MODULE = "tracked_paths"


def module_constants(tree: ast.Module) -> dict[str, str]:
    """Module-level `NAME = "literal"` assignments, so a named glob constant can be followed."""
    out: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = node.value.value
    return out


def receiver_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return f"<{type(node).__name__}>"


def declares_own_handling(source: str, tree: ast.Module) -> str | None:
    """The declared reason, or None.

    The marker is matched on source TEXT so that a comment counts — the whole point is a human
    stating an intent the AST cannot carry. The helper import, by contrast, is matched on the AST,
    because a substring search is not precise enough to be a skip criterion: the first version of
    this function looked for the token `tracked_paths` anywhere in the file and skipped
    `derive-wbs-state.py`, whose own helper is *named* `_git_tracked_paths`. A false SKIP is the
    one direction this gate must not fail in, and only the real-corpus run exposed it.

    A reason beginning with `<` is a documentation placeholder, not a declaration — this file's
    own docstring documents the marker, and matching it would make the gate skip itself.
    """
    for line in source.splitlines():
        if DECLARATION_MARKER in line:
            reason = line.split(DECLARATION_MARKER, 1)[1].strip().rstrip('"\'')
            if reason.startswith("<") or not reason:
                continue
            return reason
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == HELPER_MODULE:
            return f"resolves its globs through scripts/lib/{HELPER_MODULE}.py"
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[-1] == HELPER_MODULE for alias in node.names):
                return f"resolves its globs through scripts/lib/{HELPER_MODULE}.py"
    return None


def collect(repo_root: Path) -> tuple[list[tuple[str, int, str, str]],
                                      list[tuple[str, int, str, str]],
                                      dict[str, str]]:
    """Return (resolvable, unresolved, declared).

    resolvable / unresolved items are (script_rel, lineno, pattern_or_reason, method).
    declared maps script_rel -> the declared reason.
    """
    resolvable: list[tuple[str, int, str, str]] = []
    unresolved: list[tuple[str, int, str, str]] = []
    declared: dict[str, str] = {}

    for path in sorted(repo_root.glob(SCRIPTS_GLOB)):
        rel = path.relative_to(repo_root).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError) as exc:
            unresolved.append((rel, 0, f"unparseable: {exc}", "-"))
            continue

        reason = declares_own_handling(source, tree)
        consts = module_constants(tree)

        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in GLOB_METHODS and node.args):
                continue
            arg = node.args[0]
            pattern: str | None = None
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                pattern = arg.value
            elif isinstance(arg, ast.Name) and arg.id in consts:
                pattern = consts[arg.id]

            recv = receiver_name(node.func.value)

            if reason is not None:
                declared.setdefault(rel, reason)
                continue
            if pattern is None:
                unresolved.append((rel, node.lineno, f"pattern not a resolvable literal "
                                                     f"({receiver_name(arg)})", node.func.attr))
                continue
            if pattern.startswith("*"):
                unresolved.append((rel, node.lineno, f"unanchored pattern {pattern!r} on "
                                                     f"base {recv}", node.func.attr))
                continue
            if recv not in REPO_ROOT_NAMES:
                unresolved.append((rel, node.lineno, f"anchored pattern {pattern!r} on a base "
                                                     f"this gate cannot resolve ({recv})",
                                   node.func.attr))
                continue
            resolvable.append((rel, node.lineno, pattern, node.func.attr))

    return resolvable, unresolved, declared


def scan(repo_root: Path) -> tuple[list[tuple[str, int, str, list[Path]]],
                                   list[tuple[str, int, str, str]],
                                   dict[str, str], int, str | None]:
    """Return (findings, unresolved, declared, inputs_examined, unavailable_reason)."""
    resolvable, unresolved, declared = collect(repo_root)

    every: list[Path] = []
    per_call: list[tuple[str, int, str, list[Path]]] = []
    for rel, lineno, pattern, method in resolvable:
        matched = sorted(repo_root.glob(pattern) if method == "glob"
                         else repo_root.rglob(pattern))
        per_call.append((rel, lineno, pattern, matched))
        every.extend(matched)

    if not every:
        return [], unresolved, declared, 0, None

    try:
        ignored = ignored_paths(sorted(set(every)), repo_root)
    except IgnoreCheckUnavailable as exc:
        return [], unresolved, declared, len(every), str(exc)

    findings = []
    for rel, lineno, pattern, matched in per_call:
        hits = [p for p in matched if p in ignored]
        if hits:
            findings.append((rel, lineno, pattern, hits))
    return findings, unresolved, declared, len(every), None


def selftest() -> int:
    import subprocess
    import tempfile

    failed = 0

    def check(why: str, ok: bool, detail: str) -> None:
        nonlocal failed
        print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {detail}")
        failed += 0 if ok else 1

    def make_repo(root: Path, script_body: str, ignore: str = "") -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        (root / "scripts").mkdir()
        (root / "scripts" / "verify-thing.py").write_text(script_body, encoding="utf-8")
        d = root / "provisioning" / "deploymentSettings"
        d.mkdir(parents=True)
        (d / "dev-settings.json").write_text("{}", encoding="utf-8")
        (d / "acc-settings.json").write_text("{}", encoding="utf-8")
        (root / ".gitignore").write_text(ignore, encoding="utf-8")

    # 1. The founding defect, reproduced: an anchored glob from repo_root over a dir with an
    #    ignored file, and no declaration. MUST be a finding — this is the can-it-fail proof.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("an undeclared gate globbing an IGNORED path is a finding (IMP-0410, can-it-fail)",
              len(findings) == 1 and [p.name for p in findings[0][3]] == ["acc-settings.json"],
              f"{len(findings)} finding(s), {n} input(s) examined")

    # 2. The same script, with the same glob, DECLARING its handling. MUST be skipped and named.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # The marker is BUILT, never written literally: a fixture containing it verbatim made
        # this gate skip its own file, which is the same false-skip class as case 7.
        make_repo(root,
                  f'# {DECLARATION_MARKER} build artifacts are ignored by design\n'
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("a script DECLARING its own handling is skipped and NAMED",
              not findings and "scripts/verify-thing.py" in declared,
              f"{len(findings)} finding(s), declared={list(declared.values())}")

    # 3. Nothing ignored -> no finding. The gate is not a glob-counter.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="")
        findings, unresolved, declared, n, unavail = scan(root)
        check("with nothing ignored the same glob is clean",
              not findings and n == 2, f"{len(findings)} finding(s), {n} input(s)")

    # 4. The false-positive class this gate measured and narrowed away: an anchored pattern on a
    #    base that is NOT the repo root must be UNRESOLVED, never a finding.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'def f(p):\n    return p.rglob("manifest.json")\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("an anchored pattern on an UNRESOLVABLE base is a coverage gap, not a finding",
              not findings and len(unresolved) == 1 and "cannot resolve" in unresolved[0][2],
              f"{len(findings)} finding(s), {len(unresolved)} unresolved")

    # 5. A bare `*` is never expanded from repo_root — the extractor bug that measured 3 false
    #    positives in this gate's first draft.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'def f(repo_root):\n    return repo_root.glob("*")\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("an UNANCHORED pattern is a coverage gap, not a finding",
              not findings and len(unresolved) == 1 and "unanchored" in unresolved[0][2],
              f"{len(findings)} finding(s), {len(unresolved)} unresolved")

    # 6. A pattern inside a comment or docstring is not a glob call (IMP-0020's trap).
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  '"""We used to repo_root.glob("provisioning/deploymentSettings/*.json")."""\n'
                  '# repo_root.glob("provisioning/deploymentSettings/*.json")\n'
                  'x = 1\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("a glob named only in a docstring or comment is NOT a call (IMP-0020)",
              not findings and not unresolved, f"{len(findings)} finding(s), {n} input(s)")

    # 7. The FALSE SKIP this gate shipped with for one run: a script whose own helper is merely
    #    NAMED like the shared one must NOT be treated as declaring. Found on the real corpus, not
    #    by any fixture — derive-wbs-state.py defines `_git_tracked_paths`.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def _git_tracked_paths():\n    return frozenset()\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("a look-alike helper NAME does not count as declaring (false-skip lock)",
              len(findings) == 1 and not declared,
              f"{len(findings)} finding(s), declared={list(declared)}")

    # 8. A documentation placeholder is not a declaration, or this gate would skip itself.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  f'"""Say so with {DECLARATION_MARKER} <why these inputs are correct>."""\n'
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("a '<placeholder>' reason is documentation, not a declaration",
              len(findings) == 1 and not declared,
              f"{len(findings)} finding(s), declared={list(declared)}")

    # 9. A real import of the shared helper DOES count.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_repo(root,
                  'from tracked_paths import tracked_glob\n'
                  'SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"\n'
                  'def f(repo_root):\n    return repo_root.glob(SETTINGS_GLOB)\n',
                  ignore="provisioning/deploymentSettings/acc-settings.json\n")
        findings, unresolved, declared, n, unavail = scan(root)
        check("importing the shared helper counts as declaring",
              not findings and len(declared) == 1,
              f"{len(findings)} finding(s), declared={list(declared.values())}")

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="No gate under scripts/ selects an input the repository ignores (IMP-0410).")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--verbose", action="store_true",
                        help="list every unresolved pattern, not just the count")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]

    findings, unresolved, declared, examined, unavailable = scan(repo_root)

    if unavailable:
        print(f"GATE INPUT TRACKING: SKIPPED — {unavailable}. Nothing was excluded and nothing "
              f"is claimed; this gate needs `git check-ignore` to reach a verdict.",
              file=sys.stderr)
        return 0

    for rel, lineno, pattern, hits in findings:
        # Capped: an unfiltered node_modules sweep is 624 paths, and an error nobody can read is
        # an error nobody acts on.
        shown = [p.relative_to(repo_root).as_posix() for p in hits[:5]]
        names = ", ".join(shown)
        if len(hits) > len(shown):
            names += f", … and {len(hits) - len(shown)} more"
        print(f"ERROR: {rel}:{lineno}: glob {pattern!r} selects {len(hits)} path(s) the "
              f"repository IGNORES — {names}. A gate's verdict must not depend on local "
              f"filesystem state no commit can change: it is inverted between this machine and "
              f"CI, where the ignored path does not exist (IMP-0410). Resolve the glob through "
              f"scripts/lib/tracked_paths.py's tracked_glob(), which excludes ignored paths and "
              f"names each exclusion — or, if these inputs are correct, say so in a line "
              f"containing '{DECLARATION_MARKER} <why>'.", file=sys.stderr)

    if findings:
        print(f"\nGATE INPUT TRACKING: FAILED — {len(findings)} gate(s) select "
              f"{sum(len(h) for *_, h in findings)} ignored path(s).", file=sys.stderr)
        return 1

    print(f"GATE INPUT TRACKING: PASS — {examined} resolvable gate input(s) examined, none "
          f"ignored by the repository.")
    for rel, reason in sorted(declared.items()):
        print(f"  declares its own handling (skipped): {rel} — {reason}")
    print(f"  NOT COVERED: {len(unresolved)} glob call(s) whose pattern or base this gate "
          f"cannot resolve statically. This is a coverage gap, not a clean bill — the gate "
          f"covers anchored patterns applied to the repository root.")
    if args.verbose:
        for rel, lineno, why, method in unresolved:
            print(f"    {rel}:{lineno} .{method}() — {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
