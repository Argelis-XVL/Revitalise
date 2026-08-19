#!/usr/bin/env python3
"""Preflight a per-feature pipeline config — the gate over the DEPLOY gates.

WHY THIS EXISTS. `scripts/verify-build-config.py` proved the idea: a config is code, and this
project's configs have had bugs that no amount of careful reading caught. That preflight covers
`config/<slug>-build.yml` only. Nothing has ever checked `config/<slug>-pipeline.yml`, and
IMP-0042 recorded the consequence as a `blocker`:

    "There is no preflight for pipeline.yml. A pipeline step can name a script that does not
     exist, a parameter that does not exist, or a path that does not exist, and nothing will
     say so until the stage runs against a live environment."

Two of the seven open blockers on 2026-08-19 were the same defect, written twice:

  * IMP-0042 — `ensure-schema.ps1 -Env dev -AlternateKeysOnly`. That parameter does not exist.
  * IMP-0046 — `ensure-site.ps1 -Env dev -LibraryOnly`. That parameter does not exist either.

Both are statically decidable in milliseconds against the script's own `param()` block. Both
were instead discovered by a human, mid-deploy, against a live environment.

WHAT IT CHECKS.

  1. Structure — the config parses, and declares `feature`, `artifact` and `environments`.
  2. Artifact path (C-TECH-059) — `artifact` must be a TEMPLATE resolved per run, not a
     literal dated directory. `config/revitalise-grant-automation-pipeline.yml` carried
     `build/artifacts/revitalise-grant-automation-20260810-1/` long after the build started
     resolving a fresh directory per run, so `stage-dev`'s artifact check could only ever
     fail. Same class as IMP-0016, in the file that constraint did not cover.
  3. Every step in every list — tenant operations, environment_prerequisites, pre_deploy,
     post_deploy, smoke_tests, verification — has a description and exactly one non-empty
     `script` or `command`.
  4. Manual steps are RECOGNISED, not executed. `scripts/ci/run-config-steps.sh` treats
     `manual`, `manual step — ...` and `n/a` as recorded-not-run; anything the runner would
     hand to `bash -c` is shell-parsed here with `bash -n`.
  5. Script existence — any `provisioning/**` or `scripts/**` path named by a step exists.
  6. PARAMETER CONTRACTS — every `-Parameter` passed to a `.ps1` appears in that script's own
     `param()` block. This is the IMP-0042 / IMP-0046 gate.
  7. Unresolved placeholders — a `{{TOKEN}}` left in a command is reported, never executed.
  8. Environment variables — every `$VAR` a command depends on is declared in the config's
     `required_env_vars`, so a missing CI secret fails with a name instead of an opaque error
     (the same reasoning as build.yml's `required_env_vars` block).
  9. Rollback (C-TECH-033) — the production environment declares a rollback route.

Run:
    python3 scripts/verify-pipeline-config.py config/<slug>-pipeline.yml

Exits 0 on PASS, 1 on any violation, 2 on a usage error. Fails — never passes — when the
config is missing or empty, so it cannot report PASS over nothing (IMP-0007).

Wired into .github/workflows/ci.yml -> validate, beside the build preflight. C-TECH-062.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the CI job installs it explicitly
    print("verify-pipeline-config: FAILED — pyyaml is not installed "
          "(`python3 -m pip install pyyaml`).", file=sys.stderr)
    raise SystemExit(1)

# Values the CI runner records rather than executes. Kept in sync with the `case` block in
# scripts/ci/run-config-steps.sh — a value this list accepts but that runner does not would
# be handed to `bash -c` and die with "manual: command not found".
MANUAL_PREFIXES = ("manual", "n/a", "none")

STEP_LISTS = ("environment_prerequisites", "pre_deploy", "post_deploy",
              "smoke_tests", "verification")

# A repo-relative path this gate can check the existence of.
REPO_PATH = re.compile(r"(?<![\w/.-])((?:provisioning|scripts|src|config)/[\w./-]+)")
PS_PARAM = re.compile(r"(?<=\s)-([A-Za-z][A-Za-z0-9]*)")
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
ENV_VAR = re.compile(r"\$(?:\{)?([A-Z][A-Z0-9_]{2,})(?:\})?")

# Environment variables the runner itself provides, so a config need not declare them.
AMBIENT_ENV = {"GITHUB_STEP_SUMMARY", "GITHUB_OUTPUT", "GITHUB_ENV", "HOME", "PATH", "PWD"}


def is_manual(value: str) -> bool:
    lowered = value.strip().lower()
    return any(lowered == p or lowered.startswith(p + " ") for p in MANUAL_PREFIXES)


def powershell_params(path: Path) -> set[str] | None:
    """Return the parameter names declared by a .ps1 `param()` block, or None if absent."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    match = re.search(r"(?im)^\s*param\s*\(", text)
    if not match:
        return None

    # Balance parentheses from the opening one so nested [ValidateSet(...)] etc. are included.
    start = text.index("(", match.start())
    depth, end = 0, None
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                end = index
                break
    if end is None:
        return None

    block = text[start:end]
    # A parameter is a `$Name` that is not inside a string or a default expression; taking
    # every `$Name` immediately followed by `,`, `)`, `=` or end-of-line is precise enough,
    # and errs toward accepting a name (a false PASS on one parameter is far cheaper than a
    # false FAIL that blocks every deploy).
    return {m.group(1) for m in re.finditer(r"\$([A-Za-z_][A-Za-z0-9_]*)\s*(?=[,)=\r\n])", block)}


def iter_steps(config: dict):
    """Yield (location, step_dict) for every executable step list in the config."""
    tenant = config.get("tenant_prerequisites") or {}
    for index, step in enumerate(tenant.get("operations") or []):
        yield f"tenant_prerequisites.operations[{index}]", step

    for env_name, block in (config.get("environments") or {}).items():
        if not isinstance(block, dict):
            continue
        for list_name in STEP_LISTS:
            for index, step in enumerate(block.get(list_name) or []):
                yield f"environments.{env_name}.{list_name}[{index}]", step


def check_step(location: str, step, declared_env: set[str] | None,
               repo_root: Path, errors: list[str], stats: dict) -> None:
    if not isinstance(step, dict):
        errors.append(f"{location}: expected a mapping, got {type(step).__name__}")
        return

    if not str(step.get("description") or "").strip():
        errors.append(f"{location}: no 'description'. Every step is reported to a human at "
                      f"a gate; an unnamed step cannot be approved or recorded.")

    present = [k for k in ("script", "command") if str(step.get(k) or "").strip()]
    if not present:
        errors.append(f"{location}: has neither a non-empty 'script' nor 'command'. "
                      f"run-config-steps.sh exits 1 on this at deploy time.")
        return
    if len(present) == 2:
        errors.append(f"{location}: declares BOTH 'script' and 'command'. The CI runner reads "
                      f"one field per list and would silently ignore the other.")
        return

    value = str(step[present[0]]).strip()

    if is_manual(value):
        stats["manual"] += 1
        return
    stats["executable"] += 1

    for token in PLACEHOLDER.findall(value):
        errors.append(f"{location}: unresolved placeholder {{{{{token}}}}} in the command. "
                      f"The runner would pass it to bash verbatim.")

    # Shell-parse. A syntax error here is a guaranteed deploy-time failure (IMP-0025's class).
    probe = subprocess.run(["bash", "-n", "-c", value], capture_output=True, text=True)
    if probe.returncode != 0:
        errors.append(f"{location}: not valid shell — {probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else 'bash -n failed'}")
        return

    if declared_env is not None:
        for var in sorted(set(ENV_VAR.findall(value))):
            if var in AMBIENT_ENV or var in declared_env:
                continue
            errors.append(f"{location}: uses ${var}, which is not in the config's "
                          f"'required_env_vars'. Declare it, so a missing CI secret fails "
                          f"with a name instead of inside the tool.")

    # Repo paths named by the step must exist, and .ps1 parameters must be real.
    for candidate in REPO_PATH.findall(value):
        target = repo_root / candidate
        if not target.exists():
            errors.append(f"{location}: names '{candidate}', which does not exist. "
                          f"(IMP-0042's class — discovered live, mid-deploy, in a real "
                          f"environment.)")
            continue
        stats["paths_checked"] += 1
        if target.suffix.lower() != ".ps1":
            continue

        declared = powershell_params(target)
        if declared is None:
            errors.append(f"{location}: '{candidate}' declares no param() block, but the step "
                          f"passes parameters to it.")
            continue

        # Only inspect the parameters attached to THIS script's invocation.
        tail = value.split(candidate, 1)[1]
        tail = re.split(r"[;&|]|\breturn\b", tail, maxsplit=1)[0]
        lowered = {d.lower() for d in declared}
        for param in PS_PARAM.findall(tail):
            if param.lower() in lowered:
                stats["params_checked"] += 1
                continue
            errors.append(
                f"{location}: '{candidate}' has no parameter -{param}. "
                f"Declared: {', '.join('-' + d for d in sorted(declared)) or '(none)'}. "
                f"IMP-0042 and IMP-0046 are both exactly this, found by a human mid-deploy."
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", type=Path, help="path to config/<slug>-pipeline.yml")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="repository root for path resolution (default: cwd)")
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or Path.cwd()).resolve()

    if not args.config.is_file():
        print(f"verify-pipeline-config: FAILED — {args.config} does not exist. A preflight "
              f"pointed at a missing config must fail, not pass (IMP-0007).", file=sys.stderr)
        return 1

    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"verify-pipeline-config: FAILED — {args.config} is not valid YAML: {exc}",
              file=sys.stderr)
        return 1

    if not isinstance(config, dict) or not config:
        print(f"verify-pipeline-config: FAILED — {args.config} is empty or not a mapping.",
              file=sys.stderr)
        return 1

    errors: list[str] = []

    for key in ("feature", "artifact", "environments"):
        if key not in config:
            errors.append(f"top level: required key '{key}' is missing.")

    # ── C-TECH-059: the artifact path is resolved per run, never a literal ──────────────
    artifact = str(config.get("artifact") or "")
    if artifact:
        templated = "${" in artifact or "{{" in artifact or config.get("artifact_dir_resolver")
        dated = re.search(r"-\d{8}-\d+/?$", artifact.rstrip("/"))
        if dated and not templated:
            errors.append(
                f"top level: 'artifact' is the literal dated path '{artifact}'. The build "
                f"resolves a fresh directory per run via scripts/resolve-artifact-dir.py, so "
                f"this path stops existing after the next build and ci.yml's artifact check "
                f"can only fail. Use a template plus 'artifact_dir_resolver' "
                f"(C-TECH-059, IMP-0016)."
            )
        elif not templated and not (repo_root / artifact).exists():
            errors.append(f"top level: 'artifact' path '{artifact}' does not exist and is "
                          f"not a template.")

    environments = config.get("environments") or {}
    if not isinstance(environments, dict) or not environments:
        errors.append("top level: 'environments' declares no environment.")
        environments = {}

    declared_env = config.get("required_env_vars")
    if declared_env is None:
        print("verify-pipeline-config: NOTE — no 'required_env_vars' block; environment "
              "variable checking is skipped. build.yml declares one; this config should too.",
              file=sys.stderr)
    else:
        declared_env = set(declared_env)

    stats = {"manual": 0, "executable": 0, "paths_checked": 0, "params_checked": 0}
    step_count = 0
    for location, step in iter_steps(config):
        step_count += 1
        check_step(location, step, declared_env, repo_root, errors, stats)

    if step_count == 0:
        errors.append("no executable steps found anywhere in the config. A pipeline preflight "
                      "that scans nothing must fail rather than report PASS (IMP-0007).")

    # ── C-TECH-033: production declares a rollback route ────────────────────────────────
    prd = environments.get("prd") or environments.get("prod") or {}
    if isinstance(prd, dict) and prd:
        has_rollback = bool(str(prd.get("rollback_command") or "").strip()) or \
                       bool(str(config.get("rollback_artifact") or "").strip())
        if not has_rollback:
            errors.append("environments.prd: no 'rollback_command' and no top-level "
                          "'rollback_artifact' (C-TECH-033).")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nPIPELINE CONFIG PREFLIGHT: FAILED — {len(errors)} problem(s) across "
              f"{step_count} step(s) in {args.config}.", file=sys.stderr)
        return 1

    print(f"PIPELINE CONFIG PREFLIGHT: PASS — {step_count} steps across "
          f"{len(environments)} environment(s).")
    print(f"  executable / manual:             {stats['executable']} / {stats['manual']}")
    print(f"  shell syntax (bash -n):          OK")
    print(f"  repo paths resolved:             {stats['paths_checked']}")
    print(f"  .ps1 parameters verified:        {stats['params_checked']}")
    print(f"  artifact path resolved per run:  OK")
    print(f"  rollback route declared (prd):   OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
