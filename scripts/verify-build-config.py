#!/usr/bin/env python3
"""Preflight a build config: the gate over the gates.

Why this script exists
----------------------
Three of this project's own build gates were found broken in live use, each having
recorded PASS while checking nothing at all:

  B2  `lint` ran BEFORE `pack-managed` and pointed `--path` at the unpacked source
      FOLDER, while `pac solution check` requires a packed `.zip`. Broken from the day it
      was written; it survived builds #1-#4 because `auth` — and therefore `lint` — was
      deferred every time, so it never executed to fail.
  B5  `no-special-category-data-in-scoring`, a HARD FR-016 compliance gate, targeted the
      scoring flow's path WITHOUT its `.json` extension. `grep -r` on a nonexistent path
      exits 2 (error, not "no match"), and the step's leading `!` inverts any non-zero
      exit into a pass. The gate never read the flow, from the day it was written.
  B8  `secret-scan` lacked `--no-git` for two revisions, so `gitleaks detect` scanned
      commit history instead of the working tree. For those revisions none of the 47 files
      under src/solutions/ was tracked, so C-TECH-001 recorded PASS over none of the
      delivered source.

A gate that cannot fail is worse than no gate, because it manufactures the confidence
that stops anyone looking. At the time of writing this repo had 11 hand-written gates,
653 passing tests, and not one test that any gate can fail.

Full analysis: docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md
§2.5 and §4.4. Findings IMP-0002, IMP-0004, IMP-0007.

What it checks
--------------
0. SHELL SYNTAX. Every command shell-parses with `bash -n` — the CI runner executes each
   as `bash -euo pipefail -c`, and a YAML folded scalar can silently produce a multi-line
   value that is a syntax error (IMP-0025).
1. INPUT AVAILABILITY / STEP ORDER. Every path a step consumes either exists on disk now,
   or is produced by an EARLIER step. A path produced by a LATER step is an ordering
   defect (B2). A path that nothing produces and that does not exist is a dead target
   (B5).
2. NEGATIVE TEST COVERAGE. Every gate step is registered in the gate self-test suite
   (src/tests/build/BuildGates.Tests.ps1) with a known-bad fixture, so it is proven able
   to fail.
3. INVERTED-GREP SAFETY. A step using the `! grep ... && echo` pattern must have a
   registered negative test — that pattern turns *every* grep failure mode, including
   "target does not exist", into a pass.
4. ENV VAR DECLARATION. Every `$VAR` a command references is either declared in
   `required_env_vars`, set by the build-agent itself (`$ARTIFACT_DIR`), or a documented
   shell/CI built-in — so a missing CI secret fails by name instead of opaquely.

Exit codes: 0 all checks pass · 1 one or more violations · 2 usage/parse error.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a config defect
    print("verify-build-config: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

# ── Configuration of the checker itself ───────────────────────────────────────────

# Flags whose following token is a path this step CONSUMES.
INPUT_FLAGS = {"--path", "--folder", "--source", "-File", "-Path", "--config", "--file"}

# Flags whose following token is a path this step PRODUCES.
OUTPUT_FLAGS = {"--zipfile", "--outputDirectory", "--outputpath", "-OutputPath", "--out"}

# Step names that are gates: they must be provable-failable (check 2).
# A step is a gate if its name matches any of these, and it is not in GATE_EXEMPT.
GATE_NAME_PATTERNS = (
    r"^verify-",
    r"^preflight-",
    r"^no-",
    r".*-length$",
    r".*-limits$",
    r".*-coverage$",
    r".*-resolve$",
    r".*-reachable$",
    r".*-validate$",
    r".*-syntax$",
    r"^secret-scan$",
    r"^unit-tests$",
    r"^lint$",
)

# Steps that look like gates by name but are exempt, each with a stated reason.
GATE_EXEMPT = {
    # The preflight cannot self-test via the suite it is asserting the existence of;
    # it is covered directly by src/tests/build/VerifyBuildConfig.Tests.ps1 instead.
    "preflight-build-config": "covered by src/tests/build/VerifyBuildConfig.Tests.ps1",
    # `lint` is pac solution check — a Microsoft-hosted service. A known-bad fixture would
    # assert Microsoft's behaviour, not ours, and needs live auth. Ordering and input type
    # ARE checked here (check 1), which is the defect that actually occurred (B2).
    "lint": "third-party hosted analyser; input type and order covered by check 1",
    # `unit-tests` is the Pester suite itself. Its ability to fail is demonstrated every
    # time a test fails; a fixture asserting "Pester can report failure" is circular.
    "unit-tests": "the test runner itself; self-evidently failable",
    # `verify-tooling` asserts the presence of pac/pwsh/python. Its negative case is an
    # absent toolchain, which cannot be fixtured without uninstalling the toolchain.
    "verify-tooling": "negative case is an absent toolchain; not fixturable",
}

# Env vars the build-agent sets itself, plus CI/shell built-ins. Not expected in
# required_env_vars.
AGENT_PROVIDED_VARS = {"ARTIFACT_DIR", "ARTIFACT_DIR_NAME"}
BUILTIN_VARS = {"HOME", "PATH", "PWD", "USER", "TMPDIR", "RUNNER_OS", "GITHUB_SHA", "GITHUB_REF"}

# Tokens that look like paths but are not (globs handled separately).
# NOTE: `$` is deliberately NOT in this list. It was, briefly, and that made every
# `"$ARTIFACT_DIR"/x.zip` token invisible to the checker — silently disabling the ordering
# check on exactly the paths the build passes between steps. A bare `$VAR` with no
# separator is excluded by BARE_VAR_RE instead.
NON_PATH_PREFIXES = ("http://", "https://", "-")
BARE_VAR_RE = re.compile(r"^\$\{?\w+\}?$")

SELFTEST_SUITE = Path("src/tests/build/BuildGates.Tests.ps1")


class Violation:
    def __init__(self, check: str, step: str, message: str, remedy: str = "") -> None:
        self.check = check
        self.step = step
        self.message = message
        self.remedy = remedy

    def __str__(self) -> str:
        out = f"  [{self.check}] step `{self.step}`\n      {self.message}"
        if self.remedy:
            out += f"\n      → {self.remedy}"
        return out


# ── Token extraction ──────────────────────────────────────────────────────────────


def _strip_quotes(tok: str) -> str:
    return tok.strip().strip('"').strip("'")


def _expand_known_vars(tok: str) -> str:
    """Expand $ARTIFACT_DIR-style vars from the environment when set.

    Left unexpanded when unset: the ordering check compares token TEXT, so an unexpanded
    `"$ARTIFACT_DIR"/x.zip` still matches the producer's token exactly. That is the
    property check 1 depends on, and it works whether or not the build has resolved the
    directory yet.
    """
    def repl(m: re.Match[str]) -> str:
        name = m.group(1) or m.group(2)
        return os.environ.get(name, m.group(0))

    return re.sub(r"\$\{(\w+)\}|\$(\w+)", repl, tok)


def _looks_like_path(tok: str) -> bool:
    if not tok or tok.startswith(NON_PATH_PREFIXES):
        return False
    if tok in {"&&", "||", ";", "|", ">", ">>"}:
        return False
    if BARE_VAR_RE.match(tok):
        return False  # `$ARTIFACT_DIR` alone is a directory handle, not a checkable path
    # A path either contains a separator or has a file extension we care about.
    return "/" in tok or bool(re.search(r"\.(py|ps1|json|xml|yml|yaml|zip|md|csv)$", tok))


OPERATORS = {"&&", "||", ";", "|"}
INTERPRETERS = {"python3", "python", "pwsh", "bash", "sh", "node"}


def _segments(tokens: list[str]) -> list[list[str]]:
    """Split a token list into shell segments on &&, ||, ; and |."""
    segs: list[list[str]] = [[]]
    for t in tokens:
        if t in OPERATORS:
            segs.append([])
        else:
            segs[-1].append(t)
    return [s for s in segs if s]


def extract_paths(command: str) -> tuple[set[str], set[str]]:
    """Return (consumed, produced) path tokens for one step's shell command.

    Dispatches per shell segment on the command name, because a token's meaning depends
    entirely on which program is reading it. The original flag-only version read
    `grep -rnE "body/(rev_a|rev_b)" flow.json`'s regex ALTERNATION as a path, because it
    contains a `/` — a false positive on the very gate this checker exists to protect.
    """
    consumed: set[str] = set()
    produced: set[str] = set()

    # Blank out inline python/pwsh program text: paths inside those are glob patterns and
    # string literals, resolved by the program itself at run time, not statically here.
    scrubbed = re.sub(r"""(-c|-Command)\s+(['"]).*?\2""", r"\1 INLINE", command, flags=re.S)

    try:
        tokens = shlex.split(scrubbed, comments=False, posix=True)
    except ValueError:
        # Unbalanced quotes across a YAML folded block — fall back to whitespace split.
        tokens = scrubbed.split()

    for seg in _segments(tokens):
        # A leading `!` negates the segment's exit status; the command follows it.
        if seg and _strip_quotes(seg[0]) == "!":
            seg = seg[1:]
        if not seg:
            continue

        cmd = _strip_quotes(seg[0])
        args = seg[1:]
        non_flags = [a for a in args if not _strip_quotes(a).startswith("-")]

        if cmd == "grep":
            # grep [flags] PATTERN path...  — the first non-flag arg is the pattern.
            for a in non_flags[1:]:
                tok = _strip_quotes(a)
                if _looks_like_path(tok):
                    consumed.add(_expand_known_vars(tok))
            continue

        if cmd in {"mkdir", "touch"}:
            for a in non_flags:
                tok = _strip_quotes(a)
                if _looks_like_path(tok):
                    produced.add(_expand_known_vars(tok))
            continue

        if cmd == "rm":
            continue  # targets are destroyed, neither consumed nor produced

        if cmd in {"cp", "mv"}:
            # last non-flag is the destination; the rest are sources
            for a in non_flags[:-1]:
                tok = _strip_quotes(a)
                if _looks_like_path(tok):
                    consumed.add(_expand_known_vars(tok))
            if non_flags:
                dest = _strip_quotes(non_flags[-1])
                if _looks_like_path(dest):
                    produced.add(_expand_known_vars(dest))
            continue

        # Generic: pac / gitleaks / python3 / pwsh / any tool. Flags decide direction;
        # bare path-shaped arguments are inputs.
        for i, raw in enumerate(args):
            tok = _strip_quotes(raw)
            prev = _strip_quotes(args[i - 1]) if i else ""
            if prev in INPUT_FLAGS and _looks_like_path(tok):
                consumed.add(_expand_known_vars(tok))
            elif prev in OUTPUT_FLAGS and _looks_like_path(tok):
                produced.add(_expand_known_vars(tok))
            elif (
                prev not in INPUT_FLAGS
                and prev not in OUTPUT_FLAGS
                and not raw.startswith("-")
                and _looks_like_path(tok)
            ):
                consumed.add(_expand_known_vars(tok))
        if cmd not in INTERPRETERS and _looks_like_path(cmd):
            consumed.add(_expand_known_vars(cmd))

    return consumed, produced


# ── Checks ────────────────────────────────────────────────────────────────────────


def is_gate(name: str) -> bool:
    return any(re.match(p, name) for p in GATE_NAME_PATTERNS)


def check_inputs_and_order(steps: list[dict], repo_root: Path) -> list[Violation]:
    violations: list[Violation] = []
    per_step: list[tuple[str, set[str], set[str]]] = []
    for s in steps:
        consumed, produced = extract_paths(s.get("command", "") or "")
        per_step.append((s.get("name", "<unnamed>"), consumed, produced))

    for idx, (name, consumed, _) in enumerate(per_step):
        produced_earlier = {p for _, _, prod in per_step[:idx] for p in prod}
        produced_later: dict[str, str] = {}
        for later_name, _, prod in per_step[idx + 1 :]:
            for p in prod:
                produced_later.setdefault(p, later_name)

        for path in sorted(consumed):
            # Unresolved variable in the path: cannot check existence, but CAN check order.
            has_unresolved_var = "$" in path

            if path in produced_earlier:
                continue

            # Ordering defect: something later produces exactly this path (B2).
            if path in produced_later:
                violations.append(
                    Violation(
                        "order",
                        name,
                        f"consumes `{path}`, which is produced by the LATER step "
                        f"`{produced_later[path]}`.",
                        f"move `{name}` after `{produced_later[path]}`, or repoint it at an "
                        f"input that already exists. This is defect B2 verbatim.",
                    )
                )
                continue

            # A prefix of this path is produced later (e.g. consumes DIR/file.zip while
            # a later step produces DIR/) — same ordering defect, one level up.
            later_prefix = next(
                (p for p in produced_later if path.startswith(p.rstrip("/") + "/")), None
            )
            if later_prefix:
                violations.append(
                    Violation(
                        "order",
                        name,
                        f"consumes `{path}`, inside `{later_prefix}` which is produced by the "
                        f"LATER step `{produced_later[later_prefix]}`.",
                        f"move `{name}` after `{produced_later[later_prefix]}`.",
                    )
                )
                continue

            if has_unresolved_var:
                # Not produced by any step and contains an unresolved var — cannot verify
                # existence here. Reported as a warning-level violation only if no step
                # produces its parent directory at all.
                parent_produced = any(
                    path.startswith(p.rstrip("/") + "/") for _, _, prod in per_step for p in prod
                )
                if not parent_produced:
                    violations.append(
                        Violation(
                            "dead-target",
                            name,
                            f"consumes `{path}`; the variable is unresolved and no step in this "
                            f"config produces it or its parent.",
                            "declare the producing step, or export the variable before the build.",
                        )
                    )
                continue

            if not (repo_root / path).exists():
                violations.append(
                    Violation(
                        "dead-target",
                        name,
                        f"consumes `{path}`, which does not exist and is not produced by any "
                        f"earlier step.",
                        "fix the path. A gate pointed at a nonexistent target does not fail — "
                        "it silently passes. This is defect B5 verbatim.",
                    )
                )

    return violations


def check_shell_syntax(steps: list[dict]) -> list[Violation]:
    """Shell-parse every step command with `bash -n`.

    IMP-0025. The `unit-tests` step put its `Install-Module` call on a MORE-INDENTED line
    inside a `>` folded scalar. YAML preserves newlines on more-indented lines in a folded
    block, so the value reaching `bash -c` was genuinely multi-line with `&& pwsh …` starting
    its own line — a bash syntax error. That step would have failed on EVERY CI run, and had
    never been caught because every build to date ran interactively, with the agent invoking
    Pester directly rather than through scripts/ci/run-config-steps.sh.

    The CI runner executes each command as `bash -euo pipefail -c "$VALUE"`, so `bash -n` on
    the same string is exactly the right check, and it costs a millisecond.
    """
    violations: list[Violation] = []
    for s in steps:
        name = s.get("name", "<unnamed>")
        cmd = s.get("command", "") or ""
        if not cmd.strip():
            continue
        proc = subprocess.run(
            ["bash", "-n"], input=cmd, capture_output=True, text=True, check=False
        )
        if proc.returncode != 0:
            detail = (proc.stderr or "").strip().splitlines()
            first = detail[0] if detail else f"bash -n exited {proc.returncode}"
            hint = ""
            if any(l.lstrip().startswith(("&&", "||", "|")) for l in cmd.splitlines()):
                hint = (
                    " A line begins with `&&`/`||`. In a YAML `>` folded scalar, MORE-INDENTED "
                    "lines keep their newlines — keep every line at the same indentation and "
                    "put continuation operators at line END."
                )
            violations.append(
                Violation(
                    "shell-syntax",
                    name,
                    f"command is not valid shell: {first}",
                    f"the CI runner executes this as `bash -euo pipefail -c`, so it would fail "
                    f"on every run.{hint}",
                )
            )
    return violations


def check_tool_contracts(steps: list[dict]) -> list[Violation]:
    """Assert each tool receives the SHAPE of input it actually accepts.

    This is the check that catches defect B2 in full. Ordering alone does not: the
    historical defect pointed `pac solution check --path` at
    `src/solutions/RevitaliseGrantAutomation`, a directory that has always existed, so
    there was no dead target and nothing produced-later to compare against. The only
    statically detectable property was that `pac solution check` requires a PACKED .zip
    and was being handed a source folder.

    Each row is a platform contract learned by execution, encoded so it cannot be
    forgotten. Add a row whenever a tool rejects an input shape in a way a document
    would not have prevented.
    """
    contracts = [
        # (command pattern, flag, expected shape, why)
        (
            r"pac\s+solution\s+check",
            "--path",
            "zip",
            "`pac solution check --path` takes a PACKED solution .zip (glob-matched), not an "
            "unpacked source folder — it fails with \"the value passed to '--path' is "
            "invalid\". Defect B2: this step pointed at the source folder for every revision "
            "up to 2026-08-16, and only failed when a build first had live auth to run it.",
        ),
        (
            r"pac\s+solution\s+import",
            "--path",
            "zip",
            "`pac solution import --path` takes a packed solution .zip.",
        ),
        (
            r"pac\s+solution\s+pack",
            "--folder",
            "dir",
            "`pac solution pack --folder` takes an unpacked source DIRECTORY.",
        ),
        (
            r"pac\s+solution\s+unpack",
            "--zipfile",
            "zip",
            "`pac solution unpack --zipfile` takes a packed solution .zip.",
        ),
    ]

    violations: list[Violation] = []
    for s in steps:
        name = s.get("name", "<unnamed>")
        cmd = " ".join((s.get("command", "") or "").split())
        for pattern, flag, shape, why in contracts:
            if not re.search(pattern, cmd):
                continue
            m = re.search(rf"{re.escape(flag)}\s+(\S+)", cmd)
            if not m:
                continue
            target = _strip_quotes(m.group(1))
            is_zip = target.endswith(".zip")
            # A directory here means "no file extension in the final segment".
            is_dir = "." not in Path(target).name
            ok = is_zip if shape == "zip" else is_dir
            if not ok:
                violations.append(
                    Violation(
                        "input-type",
                        name,
                        f"passes `{flag} {target}` — expected a {'packed .zip' if shape == 'zip' else 'source directory'}.",
                        why,
                    )
                )
    return violations


def check_negative_tests(steps: list[dict], repo_root: Path) -> list[Violation]:
    violations: list[Violation] = []
    suite_path = repo_root / SELFTEST_SUITE
    suite_text = suite_path.read_text(encoding="utf-8") if suite_path.exists() else ""

    if not suite_text:
        return [
            Violation(
                "no-selftest-suite",
                "<config>",
                f"the gate self-test suite `{SELFTEST_SUITE}` does not exist.",
                "every gate must be proven able to fail against a known-bad fixture.",
            )
        ]

    for s in steps:
        name = s.get("name", "<unnamed>")
        if not is_gate(name) or name in GATE_EXEMPT:
            continue
        # The suite registers a gate by quoting its exact step name.
        if f"'{name}'" not in suite_text and f'"{name}"' not in suite_text:
            violations.append(
                Violation(
                    "no-negative-test",
                    name,
                    f"is a gate with no negative test in {SELFTEST_SUITE}.",
                    f"add a known-bad fixture under src/tests/fixtures/known-bad/{name}/ and an "
                    f"It block asserting `{name}` exits non-zero against it.",
                )
            )
    return violations


def check_inverted_grep(steps: list[dict], repo_root: Path) -> list[Violation]:
    violations: list[Violation] = []
    suite_path = repo_root / SELFTEST_SUITE
    suite_text = suite_path.read_text(encoding="utf-8") if suite_path.exists() else ""

    for s in steps:
        name = s.get("name", "<unnamed>")
        cmd = s.get("command", "") or ""
        if not re.search(r"(^|\s)!\s*grep", cmd):
            continue
        registered = f"'{name}'" in suite_text or f'"{name}"' in suite_text
        if not registered:
            violations.append(
                Violation(
                    "unsafe-inverted-grep",
                    name,
                    "uses the `! grep ... && echo` pattern with no negative test. That pattern "
                    "converts EVERY grep failure mode — including 'target does not exist' "
                    "(exit 2) — into a pass.",
                    "register a known-bad fixture for it, or replace the inline grep with a "
                    "script that distinguishes 'no match' from 'could not read the target'.",
                )
            )
    return violations


def check_env_vars(steps: list[dict], declared: list[str]) -> list[Violation]:
    violations: list[Violation] = []
    known = set(declared) | AGENT_PROVIDED_VARS | BUILTIN_VARS
    for s in steps:
        name = s.get("name", "<unnamed>")
        cmd = s.get("command", "") or ""
        # PowerShell `$PSVersionTable`, `$_`, `$errors`, `$fail` etc. are script-local.
        # Only flag ALL-CAPS shell-style vars, which is the CI-secret shape. The trailing
        # lookahead is load-bearing: without it `$PSVersionTable` matches as `$PSV`.
        for var in sorted(set(re.findall(r"\$\{?([A-Z][A-Z0-9_]{2,})\}?(?![A-Za-z0-9_])", cmd))):
            if var not in known:
                violations.append(
                    Violation(
                        "undeclared-env-var",
                        name,
                        f"references `${var}`, which is not in `required_env_vars` and is not "
                        f"agent-provided.",
                        "add it to required_env_vars so a missing value fails by name rather "
                        "than opaquely inside the tool.",
                    )
                )
    return violations


# ── Entry point ───────────────────────────────────────────────────────────────────


def run(config_path: Path, repo_root: Path) -> tuple[int, list[Violation], int]:
    try:
        cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"verify-build-config: {config_path} is not valid YAML: {exc}", file=sys.stderr)
        return 2, [], 0

    steps = cfg.get("steps") or []
    if not isinstance(steps, list) or not steps:
        print(f"verify-build-config: {config_path} declares no steps", file=sys.stderr)
        return 2, [], 0

    violations: list[Violation] = []
    violations += check_shell_syntax(steps)
    violations += check_inputs_and_order(steps, repo_root)
    violations += check_tool_contracts(steps)
    violations += check_negative_tests(steps, repo_root)
    violations += check_inverted_grep(steps, repo_root)
    violations += check_env_vars(steps, cfg.get("required_env_vars") or [])

    return (1 if violations else 0), violations, len(steps)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("config", type=Path, help="path to the build config YAML")
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repo root that relative paths resolve against (default: cwd)",
    )
    args = p.parse_args(argv)

    if not args.config.exists():
        print(f"verify-build-config: {args.config} not found", file=sys.stderr)
        return 2

    code, violations, n_steps = run(args.config, args.repo_root)
    if code == 2:
        return 2

    gates = [s.get("name", "") for s in (yaml.safe_load(args.config.read_text(encoding="utf-8")).get("steps") or []) if is_gate(s.get("name", ""))]

    if violations:
        print(f"BUILD CONFIG PREFLIGHT: FAIL — {len(violations)} violation(s)\n")
        for v in violations:
            print(v)
        print(
            "\nA gate that cannot fail is worse than no gate. Fix the above before building.\n"
            "Context: docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §4.4"
        )
        return 1

    exempt_note = ", ".join(f"{k} ({v})" for k, v in GATE_EXEMPT.items() if k in gates)
    print(
        f"BUILD CONFIG PREFLIGHT: PASS — {n_steps} steps, {len(gates)} gates.\n"
        f"  shell syntax (bash -n):          OK\n"
        f"  input availability / step order: OK\n"
        f"  tool input-type contracts:       OK\n"
        f"  negative-test coverage:          OK\n"
        f"  inverted-grep safety:            OK\n"
        f"  env var declaration:             OK"
    )
    if exempt_note:
        print(f"  exempt from negative test:       {exempt_note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
