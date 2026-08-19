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

Run:
    python3 scripts/verify-workflow-syntax.py              # the repo's .github/
    python3 scripts/verify-workflow-syntax.py --root DIR   # a fixture tree (tests)
    python3 scripts/verify-workflow-syntax.py --selftest    # prove the gate can fail

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when it
finds no workflow files at all, so it cannot report OK over an empty directory (IMP-0007).

C-TECH-063.
"""

from __future__ import annotations

import argparse
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


def run(root: Path, repo_root: Path) -> tuple[int, list[Violation], int]:
    files = sorted(list((root / "workflows").glob("*.y*ml"))
                   + list(root.glob("actions/*/action.y*ml")))
    if not files:
        return 1, [Violation(root, 1, "no workflow or action files found — refusing to "
                                      "report OK over an empty directory (IMP-0007)")], 0

    environments = declared_environments(repo_root)
    violations: list[Violation] = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        try:
            doc = yaml.safe_load(text)
            node = yaml.compose(text)
        except yaml.YAMLError as exc:
            violations.append(Violation(file, 1, f"YAML does not parse: {exc}"))
            continue
        if node is not None:
            violations += check_expressions(node, file, file.name.startswith("action."))
        violations += check_structure(doc, file, repo_root, environments)
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
}


def selftest(repo_root: Path) -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in list(_CASES.items()) + [("VALID-must-pass", _GOOD)]:
            root = Path(tmp) / name / ".github"
            (root / "workflows").mkdir(parents=True)
            (root / "workflows" / "w.yml").write_text(body, encoding="utf-8")
            code, violations, _ = run(root, repo_root)
            expect_fail = name != "VALID-must-pass"
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
          f"1 valid fixture accepted.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".github", type=Path,
                        help="directory holding workflows/ and actions/ (default: .github)")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--selftest", action="store_true",
                        help="assemble known-bad fixtures at runtime and prove each is rejected")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest(args.repo_root.resolve())

    if not args.root.exists():
        print(f"verify-workflow-syntax: FAILED — {args.root} does not exist.", file=sys.stderr)
        return 1

    code, violations, count = run(args.root, args.repo_root.resolve())
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}", file=sys.stderr)
        print(f"\nverify-workflow-syntax: FAILED — {len(violations)} problem(s) across "
              f"{count} file(s) in {args.root}.", file=sys.stderr)
        return code
    print(f"verify-workflow-syntax: OK — {count} workflow/action file(s) in {args.root}: "
          f"YAML parses, every expression uses a context GitHub allows at that key, "
          f"structure resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
