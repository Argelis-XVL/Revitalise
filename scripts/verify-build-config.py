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

What check 2 does NOT prove — read this before you wire a new gate
-----------------------------------------------------------------
Check 2 runs a new gate's known-bad fixture and accepts a failure as coverage. That is a
CAN-IT-FAIL proof, and it is the strongest thing this script is able to assert. It says
nothing about whether the gate fails on the RIGHT things.

So the obligation on you, the agent adding the gate, is one more command:

    python3 scripts/<the-new-gate>.py <the real corpus>

**Run it against the whole corpus it will run over, read every finding one at a time, decide
true or false positive, and state the measured precision where the gate is introduced** — "N
findings across M documents, K true positives".

A gate's fixtures are written by the same author, in the same sitting, from the same mental
model as the regex, so they encode the author's assumptions rather than testing them. Four
gates were added on 2026-08-25, each with passing fixtures; against the real tree they
produced five distinct false-positive classes and one MASKED TRUE POSITIVE — a plausible FIFO
pairing rule reported zero unreconciled dispatches while hiding the one genuine stall
(IMP-0319). Where a new gate reports 0 findings against a corpus you know contains an
instance, that is the tell, not a clean run.

AND READ THE EXIT CODE BEFORE YOU MAKE THE STEP BLOCKING
--------------------------------------------------------
`IMP-0439`, a blocker, 2026-08-28. *"The gate is correct"* and *"the build is green"* are two
different questions, and until this paragraph existed only the first was ever asked. Improvement
review 36 added `verify-provisioning-test-presence.py`, measured it properly — 3 findings, all
true positives — and wired it as step 4 of 72. **No step in that build config declares a
severity**, so a non-zero exit halts the build, and the gate exits 1: the next build was dead
before it packed anything, over three provisioning scripts that predated the dispatch.

    python3 scripts/<the-new-gate>.py ; echo $?     # ← the question this paragraph adds

A correct gate that is red is still a halted build, and pre-existing debt is **not the
introducing dispatch's to fix** (`C-COM-002`). `IMP-0320` is the recorded correct handling: that
dispatch built its gate, measured it red over two pre-existing flows it did not touch, and
deliberately did **not** wire it, recording why. Two legitimate answers, and "switch it off" is
neither of them, because a gate disabled because reality violates it is the `gate-cannot-fail`
class arriving by the front door:

  1. leave the step unwired, with the reason recorded where the next agent will read it; or
  2. wire it and give it a declared baseline — `config/gate-baselines.json` via
     `scripts/lib/gate_baseline.py` — where every entry carries an owner, a clearing action and a
     dated expiry, suppresses the FAIL but **never** the report, and fails the gate when it
     expires.

Note that this preflight cannot check it for you, and that is not an oversight: the check would be
*"every blocking step exits 0 against the current tree"*, which is the build itself. Running the
whole sequence to preflight the sequence is not a preflight.

A gate wired with false positives is the failure mode that teaches people to configure gates
away, which is the whole class this file exists to prevent — one level up.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
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
    # Added 2026-08-19 with the `domain-invariants` and `component-shape` steps. Without
    # these rows those steps are real gates that this preflight does not recognise AS gates,
    # so they would never be required to prove they can fail — a gate-shaped hole in the
    # gate-over-the-gates. Caught by noticing the step count rise while the gate count did
    # not; if you add a gate whose name matches nothing here, the preflight will report it
    # as an ordinary step and say nothing.
    r".*-invariants$",
    r".*-shape$",
    r".*-content$",
    r".*-resolve$",
    r".*-reachable$",
    r".*-validate$",
    r".*-syntax$",
    # Added 2026-08-21 with the `coverage-threshold` step. IMP-0132: `unit-tests` carried the
    # test-count gate AND the coverage gate, and a manifest holds one result per step, so the
    # coverage figure could be — and was — omitted while the step read as reported. Splitting
    # it out only helps if the preflight recognises the new step AS a gate.
    r".*-threshold$",
    # Added 2026-08-24 (improvement review 25) with the `metadata-write-verbs` and
    # `constraint-verifiers` steps. Same reasoning as the 2026-08-19 block above, and it is worth
    # restating because the review that added these rows was ABOUT a gate nobody ran: a gate
    # whose step name matches nothing here is reported as an ordinary step and is never required
    # to prove it can fail. Wiring a gate in and leaving it unrecognised AS a gate is
    # `gate-cannot-fail` one level up (IMP-0276, IMP-0275).
    r".*-verbs$",
    r".*-verifiers$",
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

        # `tee PATH` WRITES its argument. Added 2026-08-19: the `lint` step tees the solution
        # checker's stdout into the artifact and then asserts the file is non-empty in the SAME
        # command. Without this branch the assertion read as a consumed path that no EARLIER
        # step produces, so preflight reported `[dead-target]` on a step that is correct — and
        # it only surfaced on a FRESH artifact directory, because on a reused one the file
        # happened to exist already. A checker that passes because of a leftover file is the
        # same defect class it exists to catch. IMP-0089.
        if cmd == "tee":
            for a in non_flags:
                tok = _strip_quotes(a)
                if _looks_like_path(tok):
                    produced.add(_expand_known_vars(tok))
            continue

        # `-OutputPath DIR` on the Pester runner WRITES two named files into DIR. Added
        # 2026-08-21 with the `coverage-threshold` step, which consumes one of them.
        #
        # This is IMP-0089 a second time, and it caught me the same way it caught the `lint`
        # step: preflight PASSED while I was pointing at a reused artifact directory that
        # already held coverage.xml from an earlier run, and FAILED the moment ARTIFACT_DIR
        # resolved to a fresh one. The producer was always real — the checker just could not
        # see it, because the runner takes a DIRECTORY and the file names live inside
        # src/tests/Invoke-Tests.ps1. Naming them here is a transcription, so it can drift;
        # the drift is visible as a [dead-target] on the very next fresh build, which is the
        # cheapest possible failure mode for it.
        if "-OutputPath" in [_strip_quotes(a) for a in args]:
            stripped = [_strip_quotes(a) for a in args]
            index = stripped.index("-OutputPath")
            if index + 1 < len(stripped):
                out_dir = _expand_known_vars(stripped[index + 1]).rstrip("/")
                produced.add(out_dir)
                for produced_file in ("coverage.xml", "pester-results.xml"):
                    produced.add(f"{out_dir}/{produced_file}")

        # `test -s PATH` / `[ -s PATH ]` assert ON a path. Within a step that produced the path
        # a moment earlier this is self-verification, not consumption of a prior step's output.
        if cmd in {"test", "["}:
            for a in non_flags:
                tok = _strip_quotes(a)
                if _looks_like_path(tok) and _expand_known_vars(tok) in produced:
                    continue
                if _looks_like_path(tok):
                    consumed.add(_expand_known_vars(tok))
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


def is_gate(name: str, command: str = "") -> bool:
    """A step is a gate if its NAME matches a known pattern, or if it invokes a verify script.

    The name patterns are a whitelist, and a whitelist needs a new row every time a gate is
    added with an unanticipated name — which is a gate-shaped hole in the gate-over-the-gates
    (IMP-0050, and again on 2026-08-21 when `flow-definition-language` matched nothing and the
    step count rose while the gate count did not). The second clause is structural instead of
    lexical: anything running `scripts/verify-*.py` is a gate whatever it is called, so a new
    gate cannot be silently exempt from the negative-test requirement by being named oddly.
    """
    if any(re.match(p, name) for p in GATE_NAME_PATTERNS):
        return True
    return bool(re.search(r"scripts/verify-[\w.-]+\.py", command or ""))


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
        if not is_gate(name, s.get("command", "") or "") or name in GATE_EXEMPT:
            continue
        # The suite registers a gate by quoting its exact step name.
        if f"'{name}'" in suite_text or f'"{name}"' in suite_text:
            continue
        # SECOND, STRONGER PATH — added 2026-08-21. A gate whose command invokes a script that
        # supports `--selftest` proves it can fail by BEING RUN here, which is a better
        # assertion than a step name appearing in a Pester file: the string match proves a test
        # was named, not that anything fails. Only unregistered gates take this path, so the
        # preflight stays fast and the blast radius is the new gate alone.
        proof = _selftest_proof(s, repo_root)
        if proof is True:
            continue
        detail = (f"is a gate with no negative test in {SELFTEST_SUITE}."
                  if proof is None else
                  f"is a gate whose own --selftest FAILED: {proof}")
        violations.append(
            Violation(
                "no-negative-test",
                name,
                detail,
                f"add a known-bad fixture under src/tests/fixtures/known-bad/{name}/ and an "
                f"It block asserting `{name}` exits non-zero against it, or give the script a "
                f"`--selftest` that exits 0 only when every known-bad case is rejected.",
            )
        )
    return violations


def _selftest_proof(step: dict, repo_root: Path):
    """True if the step's script proves itself able to fail; None if it offers no --selftest;
    a reason string if the selftest ran and did not pass."""
    cmd = step.get("command", "") or ""
    match = re.search(r"(scripts/[\w./-]+\.py)", cmd)
    if not match:
        return None
    script = repo_root / match.group(1)
    if not script.exists():
        return None
    try:
        if "--selftest" not in script.read_text(encoding="utf-8"):
            return None
    except OSError:
        return None
    try:
        result = subprocess.run([sys.executable, str(script), "--selftest"],
                                cwd=repo_root, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"could not execute {match.group(1)} --selftest ({exc})"
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip().splitlines()
        return f"{match.group(1)} --selftest exited {result.returncode}: {tail[-1] if tail else 'no output'}"
    return True


# Gate scripts with deliberately NO step in this build config, each with a stated reason.
# Mirrors GATE_EXEMPT: an exemption with a reason is a decision, a silent skip is a hole.
#
# Every entry here is a script that runs at a DIFFERENT gate than the build — a PM, commercial or
# acceptance gate, or a one-off import — so requiring a build step for it would be wrong, not
# merely noisy. Anything that checks a build input belongs in the config, not in this dict.
SUITE_GATE_EXEMPT: dict[str, str] = {
    "verify-acceptance-pack.py":
        "acceptance-agent's gate: a phase acceptance record vs its evidence. Runs at phase "
        "acceptance, which is not a build.",
    "verify-handover-pack.py":
        "acceptance-agent's handover gate: every credential the solution depends on is accounted "
        "for. Runs at handover.",
    "verify-ledger-readers.py":
        "commercial-agent's ledger invariant (every worklog.jsonl reader goes through "
        "scripts/lib/worklog.py). Governs the hours ledger, not the solution.",
    "verify-provisioning-report.py":
        "pipeline-agent's post-deploy gate: a provisioning dispatch recorded its access preflight "
        "(C-TECH-065). There is no provisioning report at build time.",
    "verify-wbs-chain.py":
        "pm-agent's contracted-task-to-artefact chain, both directions. Runs at PM gates; a build "
        "cannot resolve task state.",
    "verify-worklog.py":
        "commercial-agent's billable-hours ledger invariants. Hours, not build inputs.",
    "derive-wbs-state.py":
        "pm-agent tool: derives task state from evidence for the plan of record. Not a gate over "
        "anything a build produces.",
    "import-baseline.py":
        "one-off generator for the committed commercial baseline, run when a contractual source "
        "document changes. Not a per-build check.",
    "refusal-history.py":
        "reporting tool that renders the harness-refusal matrix from the improvement log. Produces "
        "a document, asserts nothing.",
    "verify-build-manifest-note.py":
        "build-agent's own post-manifest check (IMP-0324, improvement review 29 change 14). It "
        "reads $ARTIFACT_DIR/manifest.json, which build-agent writes AFTER every step in this "
        "config has run — so a step here would name a path nothing in the config produces, which "
        "is a gate that cannot run and precisely what this file exists to catch. It is invoked by "
        "name in agents/build-agent.md, immediately after the manifest is written and before the "
        "gate output.",
}


def check_suite_gates_are_steps(steps: list[dict], repo_root: Path) -> list[Violation]:
    """The EXACT INVERSE of check_negative_tests(): every gate script the suite exercises
    must be invoked by a step in the build config.

    check_negative_tests() asks "does every gate step have a test in the suite?" — it walks
    from the config to the suite. Nothing walked the other way, so a HARD assertion could live
    inside the suite, be exercised there, and have no step of its own. Such a gate is reachable
    in a build ONLY by whatever step runs the whole suite, which on this project is
    `unit-tests`, 41st of 46 and the most expensive step in the sequence.

    That is IMP-0285 (`blocker`): `verify-improvement-log.py --check` — pure Python, about one
    second — was red for an entire ~9-minute build attempt that then had to be discarded,
    because the only thing that ran it was the Pester suite near the end. And it is the SECOND
    instance of the property, not the first: IMP-0132 recorded `unit-tests` carrying both the
    test-count gate and the coverage gate, fixed by splitting `coverage-threshold` out into its
    own step. Two instances of "a HARD gate hides inside `unit-tests`" forbid a third instance
    patch under the altitude rule in skills/how-to-promote-a-finding.md §2, so this rung asserts
    the general property instead of adding the two missing steps and moving on.

    A script the suite names only to assert it is ABSENT is not a gate the suite exercises, so
    membership is filtered by existence on disk. That is not a convenience: the two retired
    instance gates from this project's founding altitude story —
    `verify-workflow-description-length.py` and `verify-setting-description-length.py`, both
    replaced by `verify-field-length-limits.py` under C-TECH-060 — are named in the suite by an
    It block asserting they are gone. Keying on the name alone would report the retirement as a
    violation and pressure a future agent into resurrecting exactly the two scripts the altitude
    rule deleted.

    WIDENED 2026-08-25 (IMP-0309), and the reason is the residual this docstring used to end on.
    The rung originally keyed on scripts named in BuildGates.Tests.ps1, and its stated residual was
    "one that lives in no suite at all is invisible here". Within the hour that residual acquired an
    instance: `generate-subagents.py --check` had been failing with all 18 `.claude/agents/` files
    stale for ~26 hours while two separate artefacts asserted they were current, and it is in no
    suite, so this rung could not see it. **A residual that acquires an instance in under an hour
    was not a residual, it was a scope decision.**

    So the source of truth is now `scripts/` itself, in three parts:
      * every script the suite exercises (the original behaviour, unchanged),
      * every `verify-*.py` in `scripts/` — the naming convention for a gate on this project,
      * every script exposing a `--check` mode, which is what makes a GENERATOR assertable:
        `--check` means "tell me whether the generated artefact is current" and a generated
        artefact carries no staleness signal at its point of use.

    RESIDUAL, restated honestly: this still says nothing about WHERE in the config a step sits,
    only that one exists. A gate invoked through an indirection this regex cannot see (a wrapper
    script, a shell variable holding the script name) is still invisible. And a script that is
    neither named `verify-*` nor exposes `--check` — a checker with an idiosyncratic name and no
    check mode — remains outside the net; the convention is what makes this tractable.
    """
    suite_path = repo_root / SELFTEST_SUITE
    suite_text = suite_path.read_text(encoding="utf-8") if suite_path.exists() else ""

    # Any scripts/ path in any command, not just verify-*, so a generator's step counts.
    config_scripts = {
        m for s in steps
        for m in re.findall(r"scripts/([\w.-]+\.py)", s.get("command", "") or "")
    }

    candidates: set[str] = set(re.findall(r"(verify-[\w.-]+\.py)", suite_text))
    scripts_dir = repo_root / "scripts"
    if scripts_dir.is_dir():
        for path in scripts_dir.glob("*.py"):
            if path.name.startswith("verify-"):
                candidates.add(path.name)
                continue
            # A generator with a --check mode is an assertable gate; without one it is a tool.
            try:
                if "--check" in path.read_text(encoding="utf-8"):
                    candidates.add(path.name)
            except OSError:
                continue

    violations: list[Violation] = []
    for script in sorted(candidates):
        if script in config_scripts or script in SUITE_GATE_EXEMPT:
            continue
        # Named in the suite but absent from scripts/ — a retirement assertion, not a gate.
        if not (repo_root / "scripts" / script).exists():
            continue
        in_suite = script in suite_text
        why = (f"`{script}` is exercised by {SELFTEST_SUITE} but no step in this config invokes "
               f"it, so in a build it is reachable only via the step that runs the whole suite."
               if in_suite else
               f"`{script}` is a gate in `scripts/` (it is named `verify-*` or exposes a "
               f"`--check` mode) and no step in this config invokes it, so a build never runs "
               f"it at all.")
        violations.append(
            Violation(
                "suite-gate-is-not-a-step",
                script,
                why,
                f"add a step invoking `scripts/{script}`, placed as early as its inputs allow, "
                f"or add it to SUITE_GATE_EXEMPT with a stated reason "
                f"(IMP-0285, IMP-0132, IMP-0309).",
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


# ── A step must not be documented as EXPECTED to fail ─────────────────────────────
#
# IMP-0414. The comment above `flow-definition-language` read: "It currently FAILS on six live
# instances in the intake flow (IMP-0112's own prediction) — that is the gate working, not a false
# positive." Measured 2026-08-28 in the worktree AND against `git show HEAD:`: the gate exits 0
# over all five flow definitions and the intake flow's alternate-key GetItem count is ZERO in both.
# IMP-0112 had been closed before the line was last read.
#
# The failure mode is silent and one-directional, which is what makes it worth a gate: a step
# documented as expected-to-be-red is a step whose GENUINE regression gets read as the known
# condition and waved through — the exact inverse of what a gate is for. A deliberately-red gate
# belongs in contract/known-exceptions.json, where it carries an owner, a clearing action and a
# dated expiry that verify-wbs-chain.py already enforces, not in a sentence that outlives the
# condition it describes.
#
# WHY THE RETRACTION GUARD EXISTS, and it is the whole design. The NAIVE phrase match scored the
# CORRECTED file WORSE than the defective one — 2 findings on the working tree, 1 at HEAD, a
# POLARITY INVERSION, because a correction quotes the old sentence in order to withdraw it and
# this one quotes it twice. Measured across 4 config files: 3 findings, 1 true, 2 false. Skipping
# a comment block that contains a retraction marker removes both false positives BY NAME (the
# quoted sentence, and "whose config says it is EXPECTED to be red") and leaves the true positive
# standing. Re-measured: 1 finding, 1 true, 0 false.
#
# Its residual is declared rather than hidden: the guard is a phrase list. A future correction
# worded outside it is a false positive; an assertion avoiding the red phrases is a false
# negative. Four measured attempts across two reviews now say a prose-proximity check cannot tell
# an assertion from its own retraction in this repository's documentation style — assert on
# VALUES, not phrases, wherever that is possible. Here it is not, so the guard is explicit.

ASSERTS_CURRENTLY_FAILS = (
    r"currently\s+fails",
    r"expected\s+to\s+be\s+red",
    r"deliberately\s+red",
    r"expected\s+to\s+fail",
    r"is\s+known\s+to\s+fail",
    r"fails?\s+at\s+rest",
)

# A block containing any of these is a RETRACTION of such a claim, not a claim.
RETRACTION_MARKERS = (
    r"\bCORRECTED\b",
    r"this\s+comment\s+(?:used\s+to\s+)?read",
    r"this\s+comment\s+said",
    r"no\s+longer\s+true",
    r"has\s+not\s+been\s+true",
    r"that\s+was\s+corrected",
    r"stopped\s+being\s+true",
)


def _comment_blocks_by_step(config_text: str) -> list[tuple[str, str, int]]:
    """Return (step_name, comment_block_text, block_start_line) for each step preceded by one.

    A "block" is the run of consecutive `#` lines immediately above a `- name:` line, with blank
    lines breaking the run. Comments elsewhere in the file belong to no step and are ignored: a
    claim has to be attached to a step for this check to be about anything.
    """
    out = []
    block: list[str] = []
    block_start = 0
    for idx, raw in enumerate(config_text.splitlines(), start=1):
        line = raw.strip()
        if line.startswith("#"):
            if not block:
                block_start = idx
            block.append(line.lstrip("#").strip())
            continue
        m = re.match(r"-\s+name:\s*(\S+)", line)
        if m and block:
            out.append((m.group(1), "\n".join(block), block_start))
        # Any non-comment line ends the run — including the step line itself.
        block = []
    return out


def check_no_expected_failure_claims(config_text: str) -> list[Violation]:
    violations: list[Violation] = []
    for step_name, block, lineno in _comment_blocks_by_step(config_text):
        if any(re.search(p, block, re.IGNORECASE) for p in RETRACTION_MARKERS):
            continue
        hits = [p for p in ASSERTS_CURRENTLY_FAILS
                if re.search(p, block, re.IGNORECASE)]
        if not hits:
            continue
        phrase = re.search(hits[0], block, re.IGNORECASE)
        violations.append(
            Violation(
                "step-documented-as-expected-to-fail",
                step_name,
                f"its comment block (line {lineno}) asserts the step currently fails — "
                f"{phrase.group(0)!r}. A step documented as expected-to-be-red is a step whose "
                f"REAL regression gets read as the known condition and waved through, which is "
                f"the inverse of what a gate is for. The sentence also outlives the condition: "
                f"IMP-0414 found this exact claim standing over a gate that had been green for "
                f"days, its cited finding already closed.",
                "if the gate is deliberately red, record it in contract/known-exceptions.json "
                "with an owner, a clearing action and a dated expiry (verify-wbs-chain.py "
                "enforces those). If it is no longer red, delete the claim — or, if you are "
                "withdrawing it in place, say so with a retraction marker such as `CORRECTED "
                "<date>. This comment read \"...\"`, which this check honours.",
            )
        )
    return violations


# A wiring status claim lives in the docstring's OPENING CLAUSE — the text before the first
# blank line. That scope is the whole design, and it was forced by measurement rather than taste
# (improvement review 40 §6a).
#
# The obvious form — this pattern anywhere in the docstring — measured 2 findings, 1 true, 1
# false across the 44 wired verify scripts. The false one is this very file, whose line 90
# advises an author to "leave the step unwired, with the reason recorded": advice about OTHER
# steps, not a claim about its own wiring.
#
# WORSE, AND THE ACTUAL REASON FOR THE NARROWING: this repository's correction convention RETAINS
# withdrawn wording as history, so a corrected docstring contains strictly MORE of this pattern
# than the defective one did. The unnarrowed form therefore scores the CORRECTED file as a finding
# too — fixing the defect would not clear the gate, which is inverted polarity and means the
# DESIGN is wrong, not the wording (IMP-0422, IMP-0428). The opening clause is the one position
# where a correction necessarily REMOVES the phrase instead of retaining it. Measured after
# narrowing: 1 finding, 1 true, 0 false; the corrected file is clean.
DENIES_OWN_WIRING = re.compile(r"\bnot\s+wired\b|\bunwired\b|CANDIDATE\s*\(", re.IGNORECASE)


def _docstring_opening_clause(path: Path) -> str:
    """The module docstring's text before its first blank line, or '' if there is none."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    if text.count('"""') < 2:
        return ""
    return text.split('"""')[1].split("\n\n")[0]


def check_wired_scripts_do_not_deny_wiring(steps: list[dict],
                                           repo_root: Path) -> list[Violation]:
    """A script a step INVOKES may not say, in its own opening line, that it is not wired.

    THE INCIDENT (IMP-0465). `scripts/verify-doc-line-links.py` opened with "CANDIDATE
    (scratchpad, not wired)" while being the HARD `doc-line-links` step, passing on every run.
    It was authored as a measured candidate and wired in a later pass that updated the build
    config and not the docstring, and nothing compared the two. An agent deciding whether its
    document edits were enforced read the file and got the wrong answer; only the config had the
    right one.

    Second instance of the property — IMP-0322 is the same defect in the other direction, a
    docstring undercounting its own checks, which cost a finding recorded as fact from the
    intended end state rather than the tree. So the altitude rule forbids a third docstring fixed
    by hand, and this is the derived check instead: the WIRING is a value (is this script named by
    a step's command?), so the claim can be compared against it rather than trusted.

    ITS LIMIT, stated because it is real: a status claim written BELOW the first blank line is not
    seen, and nothing here checks a docstring's check COUNT — that has no single derivable home in
    these scripts. This closes the direction that misleads about enforcement, not every way a
    docstring can be wrong.
    """
    violations: list[Violation] = []
    seen: set[str] = set()
    for step in steps:
        command = step.get("command", "") or ""
        for rel in re.findall(r"scripts/verify-[\w.-]+\.py", command):
            if rel in seen:
                continue
            seen.add(rel)
            path = repo_root / rel
            if not path.is_file():
                continue  # a missing script is check_inputs_and_order's finding, not this one.
            hit = DENIES_OWN_WIRING.search(_docstring_opening_clause(path))
            if not hit:
                continue
            violations.append(
                Violation(
                    "wired-script-denies-its-own-wiring",
                    step.get("name", "?"),
                    f"{rel}'s docstring opens by denying that it is wired — {hit.group(0)!r} — "
                    f"and this step invokes it, so it IS wired and runs on every build. A gate's "
                    f"own prose is where an agent looks to decide whether its work is enforced, "
                    f"and this direction of error understates enforcement: the reader concludes "
                    f"nothing checks them (IMP-0465).",
                    "correct the docstring's OPENING line to state that it is wired, and move the "
                    "candidate/scratchpad history below the first blank line, marked as history. "
                    "Retaining the old wording as history is correct and does not trip this check "
                    "— only the opening clause is read.",
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


VALID_WHEN = {"always", "ci", "local"}

# Shell builtins and control words that are never a declared tool.
SHELL_BUILTINS = {
    "cd", "echo", "export", "set", "test", "true", "false", "exit", "rm", "mkdir", "cp", "mv",
    "ls", "cat", "grep", "sed", "awk", "printf", "if", "then", "else", "fi", "for", "while",
    "do", "done", "[", "!", "unzip", "find", "sort", "uniq", "wc", "head", "tail", "tr", "cut",
    # POSIX coreutils. Present on every machine that can run a shell, so declaring them in
    # `required_tools` would be noise. Anything NOT on this list is a real dependency.
    "tee", "xargs", "dirname", "basename", "date", "touch", "chmod", "diff", "tar", "gzip",
}


def _declared_tools(cfg: dict) -> dict[str, str]:
    """Map tool name -> context, from the config's `required_tools` block."""
    out: dict[str, str] = {}
    for entry in cfg.get("required_tools") or []:
        if isinstance(entry, str):
            out[entry] = "always"
        elif isinstance(entry, dict) and entry.get("name"):
            out[str(entry["name"])] = str(entry.get("context") or "always")
    return out


def check_execution_context(steps: list[dict], cfg: dict, context: str) -> list[Violation]:
    """Every step declares a valid `when:`, and every tool it needs is declared and present.

    Added 2026-08-19 (IMP-0041, IMP-0077 — fourth instance of
    `two-invocation-paths-disagree`). Two symptoms of one gap: the config could not say which
    execution context a thing belonged to.

      IMP-0041  the `auth` step needs GitHub's OIDC token env vars, which exist only inside an
                Actions run. It was therefore "deferred" on every local build — four times in a
                row while reporting SUCCESS, which hid a broken `lint` step behind it.
      IMP-0077  `scripts/ci/run-config-steps.sh`, the ONLY path ci.yml uses to execute these
                steps, needs `yq`. Nothing declared it, `verify-tooling` hand-listed three other
                binaries, and the runner could not execute on this machine at all.

    The generalisation the altitude rule demanded: derive the tool list from what the steps and
    the shared runner actually invoke, instead of hand-listing, and give a step an explicit
    context instead of an indefinite deferral.
    """
    violations: list[Violation] = []
    declared = _declared_tools(cfg)

    if not declared:
        violations.append(Violation(
            "no-required-tools", "<config>",
            "declares no `required_tools` block.",
            "declare every tool the steps and scripts/ci/run-config-steps.sh invoke, each with "
            "a context, so a missing binary fails by name in one second (IMP-0077).",
        ))
        return violations

    # 1. Declared tools must resolve on PATH for the context we are running in.
    for tool, tool_context in sorted(declared.items()):
        if tool_context not in VALID_WHEN:
            violations.append(Violation(
                "bad-context", tool,
                f"has context `{tool_context}`, which is not one of {sorted(VALID_WHEN)}.",
                "use always, ci or local.",
            ))
            continue
        if tool_context in ("always", context) and shutil.which(tool) is None:
            violations.append(Violation(
                "tool-missing", tool,
                f"is declared `context: {tool_context}` but does not resolve on PATH in this "
                f"`{context}` run.",
                f"install it, or change its context if it genuinely is not needed here. "
                f"IMP-0077: run-config-steps.sh needs `yq` and nothing said so.",
            ))

    # 2. Every step's `when:` is valid, and every bare command it invokes is declared.
    for s in steps:
        name = s.get("name", "<unnamed>")
        when = str(s.get("when") or "always")
        if when not in VALID_WHEN:
            violations.append(Violation(
                "bad-when", name,
                f"has `when: {when}`, which is not one of {sorted(VALID_WHEN)}.",
                "use always, ci or local.",
            ))
        cmd = s.get("command", "") or ""
        tokens = shlex.split(cmd, comments=False, posix=True) if cmd.strip() else []
        expect_command = True
        for tok in tokens:
            if tok in OPERATORS:
                expect_command = True
                continue
            if not expect_command:
                continue
            expect_command = False
            base = tok.split("/")[-1]
            if tok.startswith("-") or "/" in tok or "=" in tok or base in SHELL_BUILTINS:
                continue
            if base in declared:
                continue
            violations.append(Violation(
                "undeclared-tool", name,
                f"invokes `{base}`, which is not in `required_tools`.",
                "declare it with a context. A step that names a tool the machine lacks should "
                "fail in the preflight, not halfway through the build.",
            ))
    return violations


# ── Entry point ───────────────────────────────────────────────────────────────────


# A relocated-narrative pointer, written by improvement review 2026-09-01-4 (capability WS-C).
# The build config carried 1,339 comment lines, 1,304 of them historical narrative, and
# build-agent reads the file in full on every dispatch. The narrative moved to a changelog
# document and each moved block left one of these behind.
#
# WHY THIS IS CHECKED. The relocation's whole promise is "nothing is lost, only relocated", and a
# pointer is the only thing carrying that promise. A pointer to a deleted file or a renamed
# heading silently converts the promise into a loss — and unlike a dangling link in prose, nobody
# reads a config comment looking for rot. `verify-doc-line-links.py` cannot cover it: that gate
# reads `docs/architecture` and `docs/plans` and this is a YAML comment.
#
# It asserts on VALUES — does the file exist, does the anchor appear as a heading in it — never on
# phrasing, which is the instrument this repository has measured at 48-100% false five times
# (IMP-0422, IMP-0428).
HISTORY_POINTER = re.compile(r"#\s*History:\s*(?P<path>[^\s#]+)#(?P<anchor>\S+)")


def _history_anchors(path: Path) -> set[str]:
    """Every `## \\`anchor\\`` heading in a history document, backticks stripped."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return set()
    return {m.group(1).strip().strip("`")
            for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)}


def check_history_pointers(config_text: str, repo_root: Path) -> list[Violation]:
    """Every `# History: <file>#<anchor>` pointer resolves to a real heading in a real file."""
    violations: list[Violation] = []
    cache: dict[Path, set[str]] = {}
    for lineno, line in enumerate(config_text.split("\n"), 1):
        m = HISTORY_POINTER.search(line)
        if not m:
            continue
        target = repo_root / m.group("path")
        anchor = m.group("anchor")
        if not target.exists():
            violations.append(Violation(
                "history-pointer-unresolved", f"line {lineno}",
                f"points at {m.group('path')}, which does not exist. The narrative this step "
                f"used to carry was MOVED there, so a missing file is not a broken link — it is "
                f"the reasoning being gone.",
                "restore the file, or restore the comment block into the config and delete the "
                "pointer. Do not leave a pointer to nothing.",
            ))
            continue
        if target not in cache:
            cache[target] = _history_anchors(target)
        if anchor not in cache[target]:
            violations.append(Violation(
                "history-pointer-unresolved", f"line {lineno}",
                f"points at {m.group('path')}#{anchor}, and that file carries no `## {anchor}` "
                f"heading. Its {len(cache[target])} headings do not include it, so the section "
                f"was renamed or removed after the pointer was written.",
                f"rename the heading back, or update this pointer to the section that now holds "
                f"the narrative. Available headings are the `## ` lines in {m.group('path')}.",
            ))
    return violations


def run(config_path: Path, repo_root: Path,
        context: str = "local") -> tuple[int, list[Violation], int]:
    # Read once as TEXT as well as YAML: yaml.safe_load discards comments, and
    # check_no_expected_failure_claims is about what a comment CLAIMS (IMP-0414).
    try:
        config_text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"verify-build-config: cannot read {config_path}: {exc}", file=sys.stderr)
        return 2, [], 0
    try:
        cfg = yaml.safe_load(config_text)
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
    violations += check_suite_gates_are_steps(steps, repo_root)
    violations += check_inverted_grep(steps, repo_root)
    violations += check_env_vars(steps, cfg.get("required_env_vars") or [])
    violations += check_execution_context(steps, cfg, context)
    violations += check_no_expected_failure_claims(config_text)
    violations += check_wired_scripts_do_not_deny_wiring(steps, repo_root)
    violations += check_history_pointers(config_text, repo_root)

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
    p.add_argument(
        "--context",
        choices=sorted(VALID_WHEN - {"always"}),
        default="ci" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
        help="execution context to validate against (default: ci inside GitHub Actions, "
             "otherwise local). A step or tool whose context does not match is reported as "
             "out-of-context rather than deferred (IMP-0041, IMP-0077).",
    )
    args = p.parse_args(argv)

    if not args.config.exists():
        print(f"verify-build-config: {args.config} not found", file=sys.stderr)
        return 2

    code, violations, n_steps = run(args.config, args.repo_root, args.context)
    if code == 2:
        return 2

    gates = [s.get("name", "") for s in (yaml.safe_load(args.config.read_text(encoding="utf-8")).get("steps") or []) if is_gate(s.get("name", ""), s.get("command", "") or "")]

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
        f"  suite gates have their own step: OK\n"
        f"  inverted-grep safety:            OK\n"
        f"  env var declaration:             OK\n"
        f"  wired scripts own their wiring:  OK\n"
        f"  no step documented as red:       OK\n"
        f"  history pointers resolve:        OK\n"
        f"  execution context / tooling:     OK ({args.context})"
    )
    if exempt_note:
        print(f"  exempt from negative test:       {exempt_note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
