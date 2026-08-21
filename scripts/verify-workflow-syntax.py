#!/usr/bin/env python3
"""Validate every GitHub Actions workflow and composite action before it reaches GitHub.

WHY THIS EXISTS. On 2026-08-19 a provisioning-certificate guard was added to
`.github/workflows/ci.yml` using `if: ${{ secrets.PROVISION_CERT_PFX_BASE64 != '' }}`.
`secrets` is not an allowed context in ANY `if:`, so GitHub rejected the whole FILE and ran
**zero jobs** on every push for a day. Nobody noticed, because there is nothing to notice:

  * no job ran, so no gate produced output
  * no job ran, so no check failed and the commit carried no red X
  * the only signal was a notification email saying a run had happened

That is the one defect class CI structurally cannot report — the checker would have to be the
thing that fails to start. So this gate's primary home is LOCAL, before the commit, and its
copy in `validate` is the backstop for the case where the file still parses (IMP-0074).

It compounded the same day. `scripts/verify-improvement-log.py` detects duplicate finding ids
exactly, and a concurrent session had just produced one. It never fired: it only runs in CI,
and CI was dead on the invalid file it was about to be asked to check. **A repository whose
gates all live in one workflow has a single point of silence.** (IMP-0080)

The class arrived a third time on 2026-08-21, and this time the file was valid. `ci.yml`
triggered on `push` to `feature/**`, and no `feature/**` branch had ever existed here — so CI
had never run once, and every gate this repository describes as "wired into CI" had only ever
executed when an agent chose to run it by hand. The first two fixes asked *why the file was
rejected*. Neither asked whether a valid file would ever match a push. **A trigger that
matches no reachable ref is a gate with no inputs.** (IMP-0165)

WHAT IT CHECKS.

  Parse:
    * every file under .github/workflows/ and .github/actions/ is valid YAML

  Expression contexts — the check that would have caught IMP-0074:
    * every named-value in every `${{ }}` expression is one GitHub allows AT THAT KEY.
      `secrets` is absent from EVERY `if:` row of the context-availability table; a job-level
      `if:` additionally cannot see `env`, `steps`, `runner` or `job`. A composite action can
      never see `secrets` at all.
    * to branch on whether a secret exists, project it into a job-level `env` boolean — job
      `env` MAY read secrets — and test `env.FLAG == 'true'` in the step `if:`.

  Structure:
    * a workflow declares `on` and `jobs`; a job declares `runs-on` or `uses`
    * a step declares exactly one of `run` or `uses`
    * every `needs:` names a job that exists in the same file
    * every local `uses: ./path` resolves on disk
    * every `environment:` name is one of the keys the pipeline configs declare — the
      one-spelling rule (ADR-006). The allowed set is READ from config/*-pipeline.yml rather
      than transcribed here, because a value in both a document and a script default drifts
      and the path that passes it explicitly hides the drift (IMP-0051).

  Trigger reachability — the check that would have caught IMP-0165:
    * PER WORKFLOW: every `on.push.branches` / `on.pull_request.branches` filter list — and
      every `branches-ignore` — selects at least one branch ref that ACTUALLY EXISTS. A filter
      list matching zero existing refs is reported with the patterns and the refs it was
      compared against. A trigger with no branch filter at all matches every branch and is
      reachable by definition, so it is never reported.
    * REPO-WIDE: the repository's DEFAULT branch is covered by some workflow's `push` or
      `pull_request` trigger. `workflow_dispatch` alone does not count — a workflow only a
      human can start is a button, not a gate.
    * the refs are DISCOVERED (`git for-each-ref` over local and remote branches; the default
      branch from `origin/HEAD` with a fallback ladder), never transcribed — the same rule the
      environment keys follow, and for the same reason (IMP-0051): a branch list written into
      this script is stale the moment somebody pushes. `--refs` / `--default-branch` override
      both, which is what makes the check testable against a synthetic ref set instead of
      whatever this machine happens to have checked out.
    * IMP-0165, lineage IMP-0074, IMP-0080.

Run:
    python3 scripts/verify-workflow-syntax.py              # the repo's .github/
    python3 scripts/verify-workflow-syntax.py --root DIR   # a fixture tree (tests)
    python3 scripts/verify-workflow-syntax.py --selftest    # prove the gate can fail
    python3 scripts/verify-workflow-syntax.py --refs main,feature/x --default-branch main
                                                           # a synthetic ref set

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when it
finds no workflow files at all, and equally when it resolves no branch refs to compare
triggers against: it cannot report OK over an empty directory or an empty ref set (IMP-0007).

C-TECH-063.
"""

from __future__ import annotations

import argparse
import functools
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

# ── The context-availability table ───────────────────────────────────────────
# Source: GitHub Actions "Contexts" reference, availability table. Encoded per KEY, because
# that is how GitHub scopes it — the same expression is legal in `env:` and rejected in `if:`.

_STEP_IF = frozenset({"github", "needs", "strategy", "matrix", "job", "runner",
                      "env", "vars", "steps", "inputs"})
_JOB_IF = frozenset({"github", "needs", "vars", "inputs"})
_JOB_ENV = frozenset({"github", "needs", "strategy", "matrix", "vars", "secrets", "inputs"})
_PERMISSIVE = frozenset({"github", "needs", "strategy", "matrix", "job", "runner", "env",
                         "vars", "steps", "secrets", "inputs", "jobs"})

# Expression functions and literals are not contexts; never report them as one.
_FUNCTIONS = frozenset({"success", "failure", "always", "cancelled", "hashFiles", "contains",
                        "startsWith", "endsWith", "format", "join", "toJSON", "toJson",
                        "fromJSON", "fromJson"})
_LITERALS = frozenset({"true", "false", "null"})

_EXPR = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)
_QUOTED = re.compile(r"'[^']*'")
# Only the ROOT of a dotted chain is a context: in `needs.validate.outputs.slug` that is
# `needs`, not `outputs`. The lookbehind is what makes it the root rather than any segment.
_NAMED_VALUE = re.compile(r"(?<![A-Za-z0-9_.\-])([A-Za-z_][A-Za-z0-9_-]*)\s*(?:\.|\[|\()")


class Violation:
    def __init__(self, path: Path, line: int, message: str, remedy: str = "") -> None:
        self.path, self.line, self.message, self.remedy = path, line, message, remedy

    def __str__(self) -> str:
        out = f"{self.path}:{self.line}: {self.message}"
        if self.remedy:
            out += f"\n    → {self.remedy}"
        return out


def _named_values(expr: str) -> set[str]:
    """Every named-value referenced in an expression, ignoring string literals."""
    stripped = _QUOTED.sub("''", expr)
    found = set(_NAMED_VALUE.findall(stripped))
    return {n for n in found if n not in _FUNCTIONS and n not in _LITERALS}


def _expressions(value: str, *, bare: bool) -> list[str]:
    """The expression bodies in a scalar.

    `if:` may be written bare — `if: success()` — as well as wrapped in `${{ }}`. Every other
    key must wrap, and an unwrapped value there is a literal string, not an expression.
    """
    wrapped = _EXPR.findall(value)
    if wrapped:
        return wrapped
    return [value] if bare and value.strip() else []


def _allowed_for(key: str, path: tuple, is_action: bool) -> frozenset[str]:
    if key == "if":
        # jobs.<id>.if has no `steps` segment above it; a step's if does.
        return _STEP_IF if "steps" in path else _JOB_IF
    if key == "env":
        return _JOB_ENV
    if key in ("runs-on", "environment"):
        return _JOB_ENV - {"secrets"}
    return _PERMISSIVE


def _walk(node, path: tuple):
    """Yield (key, value_node, path) for every mapping entry, depth-first, with line marks."""
    if isinstance(node, yaml.MappingNode):
        for key_node, value_node in node.value:
            key = str(getattr(key_node, "value", ""))
            # YAML 1.1 resolves a bare `on:` to the boolean True.
            if key == "True":
                key = "on"
            yield key, value_node, path
            yield from _walk(value_node, path + (key,))
    elif isinstance(node, yaml.SequenceNode):
        for index, item in enumerate(node.value):
            yield from _walk(item, path + (str(index),))


def check_expressions(doc_node, file: Path, is_action: bool) -> list[Violation]:
    out: list[Violation] = []
    for key, value_node, path in _walk(doc_node, ()):
        if not isinstance(value_node, yaml.ScalarNode):
            continue
        allowed = _allowed_for(key, path, is_action)
        for expr in _expressions(str(value_node.value), bare=(key == "if")):
            for name in sorted(_named_values(expr)):
                if name in allowed:
                    continue
                line = value_node.start_mark.line + 1
                if name == "secrets" and key == "if":
                    out.append(Violation(
                        file, line,
                        f"`secrets` is not available in `{key}:` — GitHub rejects the whole "
                        f"FILE with 'Unrecognized named-value: secrets' and runs no jobs",
                        "project it into a job-level `env` boolean (job `env` MAY read "
                        "secrets) and test `env.FLAG == 'true'` here — IMP-0074"))
                elif name in _PERMISSIVE:
                    out.append(Violation(
                        file, line,
                        f"`{name}` is not available in `{key}:` here "
                        f"(allowed: {', '.join(sorted(allowed))})",
                        "read the context-availability table for this key before assuming"))
                else:
                    out.append(Violation(
                        file, line,
                        f"`{name}` is not a GitHub context or function",
                        "check the spelling against the Contexts reference"))
    return out


def check_structure(doc, file: Path, repo_root: Path, environments: set[str]) -> list[Violation]:
    out: list[Violation] = []
    if not isinstance(doc, dict):
        return [Violation(file, 1, "file does not parse to a mapping")]

    is_action = file.name.startswith("action.")
    if is_action:
        runs = doc.get("runs") or {}
        steps = runs.get("steps") or [] if isinstance(runs, dict) else []
        out += _check_steps(steps, file, repo_root, "runs")
        return out

    # `on` may have been resolved to the boolean True by YAML 1.1.
    if "on" not in doc and True not in doc:
        out.append(Violation(file, 1, "workflow declares no `on:` trigger"))
    jobs = doc.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        out.append(Violation(file, 1, "workflow declares no `jobs:`"))
        return out

    for name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if "runs-on" not in job and "uses" not in job:
            out.append(Violation(file, 1, f"job `{name}` declares neither `runs-on` nor `uses`"))
        for dep in _as_list(job.get("needs")):
            if dep not in jobs:
                out.append(Violation(file, 1,
                                     f"job `{name}` needs `{dep}`, which is not a job in this file"))
        env = job.get("environment")
        env_name = env.get("name") if isinstance(env, dict) else env
        if env_name and environments and env_name not in environments:
            out.append(Violation(
                file, 1,
                f"job `{name}` targets environment `{env_name}`, which is not one of the keys "
                f"the pipeline configs declare ({', '.join(sorted(environments))})",
                "one spelling, everywhere — ADR-006"))
        out += _check_steps(job.get("steps") or [], file, repo_root, f"job `{name}`")
    return out


def _check_steps(steps, file: Path, repo_root: Path, where: str) -> list[Violation]:
    out: list[Violation] = []
    if not isinstance(steps, list):
        return out
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        label = step.get("name") or step.get("uses") or f"step {index + 1}"
        has_run, has_uses = "run" in step, "uses" in step
        if not has_run and not has_uses:
            out.append(Violation(file, 1,
                                 f"{where}: `{label}` declares neither `run` nor `uses`"))
        if has_run and has_uses:
            out.append(Violation(file, 1,
                                 f"{where}: `{label}` declares both `run` and `uses`"))
        uses = step.get("uses", "")
        if isinstance(uses, str) and uses.startswith("./"):
            target = repo_root / uses[2:]
            if not (target.exists() or (target / "action.yml").exists()
                    or (target / "action.yaml").exists()):
                out.append(Violation(file, 1,
                                     f"{where}: `{label}` uses local action `{uses}`, "
                                     f"which does not exist"))
    return out


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def declared_environments(repo_root: Path) -> set[str]:
    """The environment keys the pipeline configs declare. Read, never transcribed (IMP-0051)."""
    found: set[str] = set()
    for config in sorted((repo_root / "config").glob("*-pipeline.yml")):
        try:
            doc = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        environments = doc.get("environments")
        if isinstance(environments, dict):
            found |= set(environments)
    return found


# ── Trigger reachability ─────────────────────────────────────────────────────
# A workflow that DECLARES `on:` is not the same as a workflow that CAN FIRE. Everything below
# answers the second question, and it answers it against refs read out of git rather than a
# branch list written down here (IMP-0165, lineage IMP-0074, IMP-0080).

# Only these two events select branches for a code change. `workflow_dispatch` is deliberately
# absent: it needs a human, so it is never evidence that a gate runs.
_BRANCH_EVENTS = ("push", "pull_request")

# A shallow CI checkout can carry almost no refs, and a `pull_request` checkout is detached and
# carries no branch at all. On GitHub the event's own branch names are then the ground truth.
_CI_BRANCH_ENV = ("GITHUB_BASE_REF", "GITHUB_HEAD_REF")


def _git(repo_root: Path, args: list[str]) -> str:
    """One read-only git command. Empty string when git is absent or the command fails."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(repo_root),
                              capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout if proc.returncode == 0 else ""


def discovered_refs(repo_root: Path) -> set[str]:
    """Every branch name that exists here. DISCOVERED, never transcribed (IMP-0051)."""
    refs: set[str] = set()
    for line in _git(repo_root, ["for-each-ref", "--format=%(refname)",
                                 "refs/heads", "refs/remotes"]).splitlines():
        name = line.strip()
        if name.startswith("refs/heads/"):
            refs.add(name[len("refs/heads/"):])
        elif name.startswith("refs/remotes/"):
            # Strip the remote prefix: refs/remotes/origin/main → main. The remote's own
            # symbolic HEAD is not a branch, so it is dropped rather than added as "HEAD".
            parts = name[len("refs/remotes/"):].split("/", 1)
            if len(parts) == 2 and parts[1] != "HEAD":
                refs.add(parts[1])
    head = _git(repo_root, ["symbolic-ref", "--short", "--quiet", "HEAD"]).strip()
    if head:
        refs.add(head)
    for variable in _CI_BRANCH_ENV:
        value = os.environ.get(variable, "").strip()
        if value:
            refs.add(value)
    if os.environ.get("GITHUB_REF_TYPE", "").strip() == "branch":
        value = os.environ.get("GITHUB_REF_NAME", "").strip()
        if value:
            refs.add(value)
    return {ref for ref in refs if ref}


def default_branch(repo_root: Path, refs: set[str]) -> str:
    """The repository's default branch, read from a remote's symbolic HEAD.

    Fallback ladder, because a shallow or remote-less checkout has no `origin/HEAD`: any other
    remote's HEAD, then `main`/`master` if such a branch exists, then the checked-out branch.
    """
    remotes = ["origin"] + [r for r in _git(repo_root, ["remote"]).split() if r != "origin"]
    for remote in remotes:
        prefix = f"refs/remotes/{remote}/"
        target = _git(repo_root, ["symbolic-ref", f"{prefix}HEAD"]).strip()
        if target.startswith(prefix):
            return target[len(prefix):]
    for candidate in ("main", "master"):
        if candidate in refs:
            return candidate
    return _git(repo_root, ["symbolic-ref", "--short", "--quiet", "HEAD"]).strip()


def _compile_filter(pattern: str, *, quantifiers: bool) -> re.Pattern | None:
    """One GitHub branch-filter pattern as a regex. `**` crosses `/`; `*` and `?` do not."""
    out, index, end = ["^"], 0, len(pattern)
    while index < end:
        char = pattern[index]
        if char == "\\" and index + 1 < end:
            out.append(re.escape(pattern[index + 1]))
            index += 2
        elif char == "*":
            double = pattern.startswith("**", index)
            out.append(".*" if double else "[^/]*")
            index += 2 if double else 1
        elif char in "?+":
            if quantifiers and len(out) > 1:
                out.append(char)
            else:
                out.append("[^/]" if char == "?" else re.escape(char))
            index += 1
        elif char == "[":
            close = pattern.find("]", index + 2)
            if close == -1:
                out.append(re.escape(char))
                index += 1
            else:
                body = pattern[index + 1:close]
                out.append("[" + ("^" + body[1:] if body.startswith("!") else body) + "]")
                index = close + 1
        else:
            out.append(re.escape(char))
            index += 1
    try:
        return re.compile("".join(out) + "$")
    except re.error:
        return None


@functools.lru_cache(maxsize=None)
def _readings(pattern: str) -> tuple:
    """Both readings of a pattern, deduplicated.

    GitHub's filter-pattern cheat sheet documents `?` and `+` as QUANTIFIERS over the preceding
    character; the same two characters read as ordinary glob wildcards in every other tool, and
    neither reading contains the other. This is a HARD gate, so a pattern that would match
    under either reading is treated as reachable rather than reported. Patterns using neither
    character — which is all of them here — compile identically both ways.
    """
    compiled, seen = [], set()
    for quantifiers in (False, True):
        regex = _compile_filter(pattern, quantifiers=quantifiers)
        if regex is not None and regex.pattern not in seen:
            seen.add(regex.pattern)
            compiled.append(regex)
    return tuple(compiled)


def _matches(pattern: str, ref: str) -> bool:
    return any(regex.match(ref) for regex in _readings(pattern))


def _filter_matches(patterns: list[str], ref: str) -> bool:
    """Does a `branches:` list select this ref?

    A leading `!` negates. GitHub selects a ref when some positive pattern matches it and no
    negative pattern does, and requires at least one positive pattern — a list of only
    exclusions, and an empty list, select nothing.
    """
    positives = [p for p in patterns if not p.startswith("!")]
    negatives = [p[1:] for p in patterns if p.startswith("!")]
    if not positives or not any(_matches(p, ref) for p in positives):
        return False
    return not any(_matches(n, ref) for n in negatives)


def _filter_list(value) -> list[str] | None:
    """A branch filter as written: None when the key is absent, else a list of patterns.

    `branches: []` is NOT None — an explicitly empty list selects nothing, and that is the
    finding. A bare `branches:` with no value cannot be told apart from an absent key by the
    parser, and is read as absent, which is the direction that cannot produce a false failure.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return None


def _trigger_filters(doc: dict) -> list[dict]:
    """Every `push` / `pull_request` trigger a workflow declares, with its branch filters.

    `on:` has three shapes — a bare event name, a list of them, and a mapping of event to
    filters — and YAML 1.1 may have resolved the key itself to the boolean True.
    """
    on = doc["on"] if "on" in doc else doc.get(True)
    if isinstance(on, str):
        events: dict = {on: None}
    elif isinstance(on, list):
        events = {name: None for name in on if isinstance(name, str)}
    elif isinstance(on, dict):
        events = {name: value for name, value in on.items() if isinstance(name, str)}
    else:
        return []

    out: list[dict] = []
    for event in _BRANCH_EVENTS:
        if event not in events:
            continue
        filters = events[event] if isinstance(events[event], dict) else {}
        out.append({
            "event": event,
            "branches": _filter_list(filters.get("branches")),
            "branches-ignore": _filter_list(filters.get("branches-ignore")),
            # A push trigger filtered to tags only never fires on a branch push.
            "tags-only": (_filter_list(filters.get("tags")) is not None
                          or _filter_list(filters.get("tags-ignore")) is not None),
        })
    return out


def _selects(trigger: dict, ref: str) -> bool:
    """Would this trigger fire on a push to, or a pull request against, `ref`?"""
    if trigger["branches"] is not None:
        return _filter_matches(trigger["branches"], ref)
    if trigger["branches-ignore"] is not None:
        return not any(_matches(p, ref) for p in trigger["branches-ignore"])
    return not trigger["tags-only"]


def _line_of(node, keys: tuple[str, ...]) -> int:
    """The line a nested key sits on in the composed document, or 1 when it cannot be found."""
    if node is None:
        return 1
    for key, value_node, path in _walk(node, ()):
        if path + (key,) == keys:
            return value_node.start_mark.line + 1
    return 1


def check_reachability(doc: dict, node, file: Path, refs: set[str],
                       default: str) -> tuple[list[Violation], bool]:
    """Assertion (a) per workflow, plus whether this workflow covers the default branch."""
    out: list[Violation] = []
    covers_default = False
    listed = ", ".join(sorted(refs))
    for trigger in _trigger_filters(doc):
        event = trigger["event"]
        if default and _selects(trigger, default):
            covers_default = True
        for key in ("branches", "branches-ignore"):
            patterns = trigger[key]
            if patterns is None:
                continue
            if key == "branches":
                selected = [r for r in refs if _filter_matches(patterns, r)]
            else:
                selected = [r for r in refs
                            if not any(_matches(p, r) for p in patterns)]
            if selected:
                continue
            out.append(Violation(
                file, _line_of(node, ("on", event, key)),
                f"`on.{event}.{key}` selects no branch that exists: {patterns} matched none "
                f"of the {len(refs)} ref(s) in this repository ({listed}) — a trigger that "
                f"matches no reachable ref is a gate with no inputs, so this workflow has "
                f"never been able to fire on a {event}",
                "widen the filter to a branch this project actually uses, or drop it — "
                "IMP-0165"))
    return out, covers_default


def run(root: Path, repo_root: Path, refs: set[str] | None = None,
        default: str | None = None) -> tuple[int, list[Violation], int]:
    files = sorted(list((root / "workflows").glob("*.y*ml"))
                   + list(root.glob("actions/*/action.y*ml")))
    if not files:
        return 1, [Violation(root, 1, "no workflow or action files found — refusing to "
                                      "report OK over an empty directory (IMP-0007)")], 0

    if refs is None:
        refs = discovered_refs(repo_root)
    if default is None:
        default = default_branch(repo_root, refs)

    environments = declared_environments(repo_root)
    violations: list[Violation] = []
    workflows = 0
    covered = False
    for file in files:
        text = file.read_text(encoding="utf-8")
        try:
            doc = yaml.safe_load(text)
            node = yaml.compose(text)
        except yaml.YAMLError as exc:
            violations.append(Violation(file, 1, f"YAML does not parse: {exc}"))
            continue
        # A composite action has no `on:`, so trigger reachability does not apply to it.
        is_action = file.name.startswith("action.")
        if node is not None:
            violations += check_expressions(node, file, is_action)
        violations += check_structure(doc, file, repo_root, environments)
        if not is_action and isinstance(doc, dict):
            workflows += 1
            if refs:
                found, covers = check_reachability(doc, node, file, refs, default)
                violations += found
                covered = covered or covers

    # Assertion (b), and the two ways its inputs can be missing. An empty ref set is the same
    # class of defect as an empty directory: there is nothing to compare against, so the only
    # honest answer is a failure (IMP-0007).
    if not refs:
        violations.append(Violation(
            root, 1,
            "resolved zero branch refs to compare triggers against — refusing to report OK "
            "over an empty ref set (IMP-0007)",
            "run this inside a git working tree, or pass --refs"))
    elif not default:
        violations.append(Violation(
            root, 1,
            "could not resolve the repository's default branch, so trigger coverage cannot be "
            "checked — refusing to report OK over a missing input (IMP-0007)",
            "pass --default-branch"))
    elif workflows and not covered:
        violations.append(Violation(
            root / "workflows", 1,
            f"default branch `{default}` is covered by no workflow's `push` or "
            f"`pull_request` trigger across {workflows} workflow file(s) — every gate that "
            f"only runs in CI is therefore unreachable on the branch the work lands on, and "
            f"`workflow_dispatch` alone is a button a human presses, not a gate",
            f"add `{default}` to some workflow's push or pull_request branch filter — "
            "IMP-0165"))
    return (1 if violations else 0), violations, len(files)


# ── Self-test: prove the gate can fail, and prove it still passes valid input ─
# Fixtures are ASSEMBLED AT RUNTIME, never committed. A known-bad workflow file at rest in
# .github/ would be picked up by GitHub itself and break the repository it exists to protect
# (IMP-0024).

_GOOD = """
name: good
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    env:
      HAS_CERT: ${{ secrets.SOME_SECRET != '' }}
    steps:
      - run: echo installed
        if: ${{ env.HAS_CERT == 'true' }}
      - run: echo missing
        if: ${{ env.HAS_CERT != 'true' }}
"""

# The reachability check must pass on a filter that DOES match, or it is a gate that fires
# unconditionally and tells nobody anything. Both of these run against a synthetic ref set.
_GOOD_GLOB = """
name: good-glob
on:
  push:
    branches:
      - main
      - "feature/**"
  pull_request:
    branches: [main]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
"""

_GOOD_IGNORE = """
name: good-ignore
on:
  push:
    branches-ignore:
      - gh-pages
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
"""

_VALID = {
    "VALID-must-pass": _GOOD,
    "VALID-glob-that-matches": _GOOD_GLOB,
    "VALID-branches-ignore-that-leaves-branches": _GOOD_IGNORE,
}

_CASES = {
    "secrets-in-step-if": """
name: bad
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
        if: ${{ secrets.SOME_SECRET != '' }}
""",
    "env-in-job-if": """
name: bad
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    if: ${{ env.FLAG == 'true' }}
    steps:
      - run: echo hi
""",
    "step-with-neither-run-nor-uses": """
name: bad
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - name: does nothing
""",
    "needs-a-job-that-does-not-exist": """
name: bad
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    needs: [nope]
    steps:
      - run: echo hi
""",
    "not-yaml-at-all": """
name: bad
on: [push
jobs: {
""",
    # The IMP-0165 shape itself: a valid file, correct in every other respect, triggering on a
    # branch pattern no ref matches. The `pull_request` trigger keeps the default branch
    # covered, so this fixture isolates assertion (a).
    "trigger-matches-no-branch-that-exists": """
name: bad
on:
  push:
    branches:
      - "feature/**"
  pull_request:
    branches: [main]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
""",
    # Assertion (b): a workflow only a human can start leaves the default branch ungated.
    "default-branch-covered-by-nothing": """
name: bad
on:
  workflow_dispatch:
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
""",
    "negation-excludes-every-branch": """
name: bad
on:
  push:
    branches:
      - "**"
      - "!main"
      - "!project-management"
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
""",
    "branches-ignore-ignores-every-branch": """
name: bad
on:
  push:
    branches-ignore:
      - "**"
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
""",
}

# The refs the fixtures are checked against. Synthetic on purpose: the gate must not depend on
# which branches happen to exist on the machine running the selftest.
_SELFTEST_REFS = frozenset({"main", "project-management"})
_SELFTEST_DEFAULT = "main"
_CASE_REFS = {"VALID-glob-that-matches": frozenset({"main", "project-management", "feature/x"})}


def selftest(repo_root: Path) -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in list(_CASES.items()) + list(_VALID.items()):
            root = Path(tmp) / name / ".github"
            (root / "workflows").mkdir(parents=True)
            (root / "workflows" / "w.yml").write_text(body, encoding="utf-8")
            refs = set(_CASE_REFS.get(name, _SELFTEST_REFS))
            code, violations, _ = run(root, repo_root, refs, _SELFTEST_DEFAULT)
            expect_fail = name not in _VALID
            ok = (code != 0) if expect_fail else (code == 0)
            verdict = "OK" if ok else "DID NOT BEHAVE"
            print(f"  {verdict:16} {name} → exit {code}, {len(violations)} violation(s)")
            if not ok:
                failures.append(name)
                for violation in violations:
                    print(f"                   {violation}")
    if failures:
        print(f"\nverify-workflow-syntax: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-workflow-syntax: SELFTEST OK — {len(_CASES)} known-bad fixtures rejected, "
          f"{len(_VALID)} valid fixture(s) accepted, all against a synthetic ref set "
          f"({', '.join(sorted(_SELFTEST_REFS))}; default `{_SELFTEST_DEFAULT}`).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".github", type=Path,
                        help="directory holding workflows/ and actions/ (default: .github)")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--selftest", action="store_true",
                        help="assemble known-bad fixtures at runtime and prove each is rejected")
    parser.add_argument("--refs", action="append", metavar="NAMES",
                        help="comma-separated branch names to check triggers against; "
                             "repeatable (default: discovered with git for-each-ref)")
    parser.add_argument("--default-branch", metavar="NAME",
                        help="the repository's default branch "
                             "(default: discovered from origin/HEAD)")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest(args.repo_root.resolve())

    if not args.root.exists():
        print(f"verify-workflow-syntax: FAILED — {args.root} does not exist.", file=sys.stderr)
        return 1

    repo_root = args.repo_root.resolve()
    # Resolved here, not inside run(), so the OK line can state what was actually compared.
    refs = ({ref.strip() for group in args.refs for ref in group.split(",") if ref.strip()}
            if args.refs is not None else discovered_refs(repo_root))
    default = args.default_branch or default_branch(repo_root, refs)

    code, violations, count = run(args.root, repo_root, refs, default)
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}", file=sys.stderr)
        print(f"\nverify-workflow-syntax: FAILED — {len(violations)} problem(s) across "
              f"{count} file(s) in {args.root}.", file=sys.stderr)
        return code
    print(f"verify-workflow-syntax: OK — {count} workflow/action file(s) in {args.root}: "
          f"YAML parses, every expression uses a context GitHub allows at that key, "
          f"structure resolves, every branch filter selects at least one of the "
          f"{len(refs)} ref(s) that exist, and default branch `{default}` is covered by a "
          f"push or pull_request trigger.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
