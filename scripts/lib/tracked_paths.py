#!/usr/bin/env python3
"""Glob a repository path, then EXCLUDE whatever git ignores — and say which. Stdlib only.

WHY THIS MODULE EXISTS
----------------------
`IMP-0410`, a blocker. `scripts/verify-audited-tables.py`'s `SETTINGS_GLOB` is
`provisioning/deploymentSettings/*.json`. `New-SettingsFixture` in
`src/tests/provisioning/ProvisioningTestHarness.psm1` writes a fully-resolved settings file to
`provisioning/deploymentSettings/acc-settings.json` and its `AfterAll` removes it. `.gitignore`
line 58 ignores that path, with the stated reason *"so a crashed run cannot leave a fixture that
gets committed and then read as a real settings file"*.

The ignore rule stops the fixture being COMMITTED. It does nothing about it being READ. An
interrupted Pester run left the file on disk and the HARD `audited-tables` build step went red on
8 undeclared table/environment pairs inside a throwaway file — **and no commit could fix it**.
Worse, the verdict is INVERTED between machines: on a CI runner, where the fixture never exists,
the same gate passes. A gate whose answer depends on local filesystem state is not a gate.

THE RULE THIS ENCODES
---------------------
A gate that selects its inputs by glob over a directory must exclude anything the repository
ignores. Two mechanisms — a `.gitignore` line and a glob literal — were written independently,
so a file was simultaneously *"not part of the repository"* and *"a settings file this gate must
validate"*. Neither list knew about the other. This module is the shared list.

WHY EXCLUSIONS ARE REPORTED BY NAME
-----------------------------------
Silently narrowing a gate's input set is how a gate stops being able to fail. `IMP-0007` is this
project's founding instance: a checker with no inputs must FAIL, never report PASS. So this
module never decides that question — it returns what it dropped, and the CALLER keeps its own
empty-input-set failure. `verify-audited-tables.py` line 207's `if not declaring:` branch is
untouched by adopting this helper, deliberately.

WHAT IT DOES NOT DO
-------------------
It is **opt-in**, and that is a real weakness worth stating rather than hiding: nothing forces a
new gate to call it. `scripts/verify-gate-input-tracking.py` is the answer to that — it fails when
any anchored glob literal under `scripts/` resolves to an ignored path and the script has not
declared its own handling.

Two gates read ignored paths BY DESIGN and must NOT adopt this:
  * `verify-build-manifest-note.py` globs `build/artifacts/` — 931 files, 909 of them ignored.
    A blanket exclusion would empty its input set and, under its own no-inputs rule, fail it.
  * `verify-toolchain-claims.py` filters `node_modules` at line 190 by a hardcoded string.

TWO INPUT UNIVERSES, AND A GATE MUST DECLARE WHICH ONE IT READS
--------------------------------------------------------------
Added 2026-08-28 (`IMP-0437`, improvement review 37). `IMP-0410` was the IGNORED direction. There
is a second, opposite direction — UNTRACKED — and it is not the same defect with the sign flipped,
because the correct handling differs per gate:

  * **The working tree** is the right universe for an AUTHORING-TIME gate. Uncommitted work is
    exactly what it exists to check, so it MUST NOT adopt a tracked-only rule.
  * **The commit** is the right universe for a gate whose output is transcribed as a claim about
    delivered source — a warning COUNT copied into a Dev Summary, for instance.

`IMP-0437` proposed resolving EVERY glob-driven gate's inputs through `git ls-files`. Measured
against this repository, that would have dropped 5 files from one gate's inputs, 2 of them whole
entity directories, and left `verify-superseded-column-writers.py` with **zero inputs** — the only
three "UNUSED FROM REVISION" markers in the repository live in an untracked `Entity.xml`. It would
equally have dropped all three `seed-round-statistics-*.ps1` files from
`verify-provisioning-test-presence.py`, which are the exact scripts `IMP-0433`/`IMP-0434` are
about. So the generalisation is real and the wording was not.

**The rule this encodes: REPORT the split, do not narrow the inputs.** A gate keeps reading the
working tree and NAMES its untracked inputs, so nobody transcribes a count without seeing that the
verdict is working-tree-specific. Where reproducing the commit's verdict is genuinely wanted, that
is an explicit flag the caller passes — never the default, and never implicit.

WHAT IT PROVIDES
----------------
    ignored_paths(paths, repo_root)         -> set of paths git ignores (one batched call)
    tracked_glob(repo_root, pattern)        -> (kept, excluded) — sorted lists of Path
    describe_exclusions(excluded, root)     -> lines a gate prints so the narrowing is visible
    untracked_paths(paths, repo_root)       -> set of paths git does not track (one batched call)
    describe_untracked(untracked, root)     -> lines a gate prints so the SPLIT is visible

`git check-ignore` is invoked ONCE with every candidate on stdin, not once per file. Where git is
absent or the call fails, NOTHING is excluded and the caller is told: failing open here keeps a
gate's verdict identical to its pre-helper behaviour rather than silently emptying it.

`untracked_paths` fails open the same way and for the same reason — an empty set would read as
"everything is tracked", which is the quiet direction of exactly the defect this addresses.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = ["ignored_paths", "tracked_glob", "describe_exclusions", "IgnoreCheckUnavailable",
           "untracked_paths", "describe_untracked"]


class IgnoreCheckUnavailable(RuntimeError):
    """`git check-ignore` could not be consulted. Callers fail OPEN, and say so."""


def ignored_paths(paths: list[Path], repo_root: Path) -> set[Path]:
    """Every path in `paths` that git ignores, resolved in ONE batched subprocess call.

    `git check-ignore --stdin` exits 0 when at least one path is ignored, 1 when none are, and
    128 on a usage or repository error. Only the first two are answers; 128 means we do not know,
    which is `IgnoreCheckUnavailable` and never an empty set — an empty set would read as
    "nothing is ignored" and silently restore the defect this module exists to remove.
    """
    if not paths:
        return set()
    payload = "\n".join(p.as_posix() for p in paths)
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "check-ignore", "--stdin"],
            input=payload, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise IgnoreCheckUnavailable(f"could not run `git check-ignore`: {exc}") from exc
    if proc.returncode not in (0, 1):
        raise IgnoreCheckUnavailable(
            f"`git check-ignore` exited {proc.returncode}: {proc.stderr.strip() or 'no stderr'}")
    out: set[Path] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            out.add(Path(line) if Path(line).is_absolute() else repo_root / line)
    return out


def tracked_glob(repo_root: Path, pattern: str) -> tuple[list[Path], list[Path]]:
    """`repo_root.glob(pattern)` minus everything git ignores.

    Returns `(kept, excluded)`, both sorted. An empty `kept` is returned as-is: deciding whether
    no inputs is a PASS or a FAIL belongs to the caller (`IMP-0007`), and this helper must not
    make a gate unfailable by answering it here.

    Where the ignore check is unavailable the helper fails OPEN — everything is kept, nothing is
    excluded — because narrowing a gate's inputs on the strength of a failed subprocess is the
    worse of the two errors.
    """
    candidates = sorted(repo_root.glob(pattern))
    if not candidates:
        return [], []
    try:
        ignored = ignored_paths(candidates, repo_root)
    except IgnoreCheckUnavailable:
        return candidates, []
    kept = [p for p in candidates if p not in ignored]
    excluded = [p for p in candidates if p in ignored]
    return kept, excluded


def describe_exclusions(excluded: list[Path], repo_root: Path) -> list[str]:
    """One line per excluded path, for a gate to print. Never silent (`IMP-0410`)."""
    lines = []
    for path in excluded:
        try:
            rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            rel = path.as_posix()
        lines.append(f"  excluded, ignored by git (not delivered source): {rel}")
    return lines


def untracked_paths(paths: list[Path], repo_root: Path) -> set[Path]:
    """Every path in `paths` that git does not TRACK, resolved in ONE batched call.

    Distinct from `ignored_paths` in both mechanism and meaning. An ignored path is one the
    repository has decided is not source; an untracked path is one that is not in the commit
    *yet* — normal mid-feature, and the reason a gate's verdict can differ from CI's (`IMP-0437`).

    `git ls-files --cached -z --` over the candidates lists which of them ARE tracked; the
    complement is the answer. Anything git cannot answer is `IgnoreCheckUnavailable`, never an
    empty set — an empty set would read as "everything is tracked", which is the quiet direction
    of the defect this exists to expose.
    """
    if not paths:
        return set()
    rels = []
    for p in paths:
        try:
            rels.append(p.relative_to(repo_root).as_posix())
        except ValueError:
            rels.append(p.as_posix())
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--cached", "-z", "--", *rels],
            capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise IgnoreCheckUnavailable(f"could not run `git ls-files`: {exc}") from exc
    if proc.returncode != 0:
        raise IgnoreCheckUnavailable(
            f"`git ls-files` exited {proc.returncode}: {proc.stderr.strip() or 'no stderr'}")
    tracked = {(repo_root / line) for line in proc.stdout.split("\0") if line.strip()}
    return {p for p, rel in zip(paths, rels) if (repo_root / rel) not in tracked}


def describe_untracked(untracked: list[Path], repo_root: Path) -> list[str]:
    """One line per untracked input, for a gate to print. Never silent (`IMP-0437`).

    The wording says what the reader must not do with the number: an untracked input means this
    verdict may differ from CI's, so the count must not be transcribed as a claim about source.
    """
    lines = []
    for path in sorted(untracked):
        try:
            rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            rel = path.as_posix()
        lines.append(f"  UNTRACKED input, read as if delivered: {rel}")
    return lines


def _selftest() -> int:
    """Proves the helper CAN exclude, CAN keep, and fails OPEN — in a real throwaway git repo."""
    import tempfile

    failed = 0

    def check(why: str, ok: bool, detail: str) -> None:
        nonlocal failed
        print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {detail}")
        failed += 0 if ok else 1

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        d = root / "provisioning" / "deploymentSettings"
        d.mkdir(parents=True)
        for name in ("dev-settings.json", "test-settings.json", "acc-settings.json"):
            (d / name).write_text("{}", encoding="utf-8")
        (root / ".gitignore").write_text(
            "provisioning/deploymentSettings/acc-settings.json\n", encoding="utf-8")

        kept, excluded = tracked_glob(root, "provisioning/deploymentSettings/*.json")
        check("the ignored fixture is excluded and the real files are kept",
              [p.name for p in kept] == ["dev-settings.json", "test-settings.json"]
              and [p.name for p in excluded] == ["acc-settings.json"],
              f"kept={[p.name for p in kept]} excluded={[p.name for p in excluded]}")

        check("every exclusion is described by name",
              len(describe_exclusions(excluded, root)) == 1
              and "acc-settings.json" in describe_exclusions(excluded, root)[0],
              describe_exclusions(excluded, root)[0].strip())

        (root / ".gitignore").write_text("", encoding="utf-8")
        kept2, excluded2 = tracked_glob(root, "provisioning/deploymentSettings/*.json")
        check("with nothing ignored, nothing is excluded (the helper is not a filter)",
              len(kept2) == 3 and excluded2 == [],
              f"kept={len(kept2)} excluded={len(excluded2)}")

        kept3, excluded3 = tracked_glob(root, "provisioning/deploymentSettings/*.nomatch")
        check("a glob matching nothing returns empty and does NOT raise "
              "(the caller owns the IMP-0007 decision)",
              kept3 == [] and excluded3 == [],
              f"kept={len(kept3)} excluded={len(excluded3)}")

    # ── The UNTRACKED direction (IMP-0437) ────────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        d = root / "Entities" / "rev_thing"
        d.mkdir(parents=True)
        committed = d / "Entity.xml"
        committed.write_text("<x/>", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "Entities/rev_thing/Entity.xml"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "x"], check=True, capture_output=True)
        newcomer = d / "Untracked.xml"
        newcomer.write_text("<x/>", encoding="utf-8")

        un = untracked_paths([committed, newcomer], root)
        check("a file in the commit is NOT reported untracked; a new file IS",
              un == {newcomer}, f"untracked={[p.name for p in un]}")

        check("every untracked input is described by name, and the line warns against "
              "transcribing the count",
              len(describe_untracked(list(un), root)) == 1
              and "Untracked.xml" in describe_untracked(list(un), root)[0]
              and "as if delivered" in describe_untracked(list(un), root)[0],
              describe_untracked(list(un), root)[0].strip())

        check("with nothing new on disk, nothing is reported untracked (not a filter)",
              untracked_paths([committed], root) == set(),
              f"untracked={len(untracked_paths([committed], root))}")

        check("an IGNORED file and an UNTRACKED file are different answers — the two "
              "directions are not one check (IMP-0437)",
              untracked_paths([newcomer], root) == {newcomer}
              and ignored_paths([newcomer], root) == set(),
              "untracked=1 ignored=0")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)  # NOT a git repository — check-ignore must be unavailable here
        (root / "a.json").write_text("{}", encoding="utf-8")
        raised = False
        try:
            ignored_paths([root / "a.json"], root)
        except IgnoreCheckUnavailable:
            raised = True
        check("outside a git repository the check raises rather than returning an empty set",
              raised, f"raised={raised}")
        raised_un = False
        try:
            untracked_paths([root / "a.json"], root)
        except IgnoreCheckUnavailable:
            raised_un = True
        check("and so does untracked_paths — an empty set would read as 'everything is "
              "tracked', the quiet direction of the defect",
              raised_un, f"raised={raised_un}")
        kept4, excluded4 = tracked_glob(root, "*.json")
        check("and tracked_glob FAILS OPEN — keeps everything, excludes nothing",
              len(kept4) == 1 and excluded4 == [],
              f"kept={len(kept4)} excluded={len(excluded4)}")

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
