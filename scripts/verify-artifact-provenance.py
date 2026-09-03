#!/usr/bin/env python3
"""An artifact directory cited for deploy went through build-agent's managed process.

`C-TECH-030` — pipeline-agent's pre-Stage-1 preflight. Run it against the directory a
dispatch names as its deploy target, BEFORE any `deploy_command` or ALM stage executes.

    python3 scripts/verify-artifact-provenance.py build/artifacts/<slug>-<YYYYMMDD>-<n>/

WHY THIS EXISTS
---------------
`IMP-0582`. A pipeline-agent dispatch was told to deploy
`build/artifacts/trustee-portal-visual-refresh-20260902-3/`. That directory held both solution
zips, a code-app `dist/` and `test-results/` — everything a finished build leaves EXCEPT the two
things that record that a build finished: no `manifest.json`, and no `SUCCESS` line in
`logs/build.log`. A build-agent session had died after packing and before writing its manifest,
and nothing in the directory distinguishes that from a completed build. `C-TECH-030` already
said every deploy target must be the managed artifact produced by build-agent; its Verify By
column said "no manual deploy steps", which is a description, not a command. Nothing ran.

So the property asserted here is PROVENANCE, not content: this directory is the output of a
build that ran to completion, was recorded, and was tested. It says nothing about what is
inside the zips — `verify-build-manifest-note.py` and the build config's own gates own that.

WHAT IT CHECKS (HARD — exit 1, deploy does not begin)
-----------------------------------------------------
  * the directory exists
  * it contains a `manifest.json` that parses
  * that manifest's `artifact_path` names THIS directory — a manifest copied from a sibling
    build proves that sibling ran, not this one
  * the manifest's `status` begins with `SUCCESS` or `DEPLOYED` — never `FAILED`, `BLOCKED`,
    empty or absent
  * some file under `docs/tests/` names this directory — test-agent's approval names the
    specific build it approved, and a build nobody tested is not a deploy candidate

AND ONE WARNING (exit 0, reported)
----------------------------------
  * no matching `SUCCESS — build/artifacts/<name>` line in `logs/build.log`

The build.log line is DELIBERATELY not a hard failure, and the corpus is why.
`revitalise-grant-automation-20260823-2` was really built, really tested and really deployed,
and has no SUCCESS line: that log is appended by hand at the end of a dispatch, so a missing
line is evidence a log write was skipped, not evidence a build never ran. `manifest.json` is
written by build-agent as part of the build itself, which makes it the load-bearing signal.
Failing hard on the weaker of two signals is how a gate teaches people to route around it
(`IMP-0181`).

CORPUS MEASUREMENT (2026-09-02, improvement review of `IMP-0582`)
----------------------------------------------------------------
Run over all 51 directories under `build/artifacts/` and, separately, over the 9 directories
`logs/pipeline.log` records as having actually been deployed — the corpus this gate will run
over in real use:

  * 9 of 9 real deploy targets PASS every hard check. 0 false positives.
  * 1 of those 9 (`revitalise-grant-automation-20260823-2`) raises the build.log WARNING, and
    that observation is TRUE — the line really is missing. It is a warning for the reason above.
  * `trustee-portal-visual-refresh-20260902-3`, the directory of `IMP-0582`, FAILS on
    `no-manifest` and on `no-test-report`. That is the finding, reproduced.
  * The other 41 directories are failed builds, blocked builds, and pre-convention
    directories that were never deploy targets. They are not this gate's corpus and are not
    counted either way.

The allowed `status` prefixes are ENUMERATED FROM THE CORPUS, not invented (`IMP-0560`): the
38 manifests on disk carry first words `SUCCESS`, `DEPLOYED`, `FAILED`, `BLOCKED` and one null.
`DEPLOYED` is in the allowed set because `revitalise-alert-links-20260820-1` and three siblings
record a real deploy in `status` rather than the word SUCCESS, and a re-deploy of one of those
is legitimate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACT_ROOT = "build/artifacts"
BUILD_LOG = "logs/build.log"
TEST_DOCS = "docs/tests"

# Enumerated from the 38 manifests on disk, 2026-09-02. See the module docstring.
OK_STATUS_PREFIXES = ("SUCCESS", "DEPLOYED")


@dataclass
class Finding:
    kind: str
    why: str
    fix: str

    def render(self) -> str:
        return f"  {self.kind}\n      {self.why}\n      FIX: {self.fix}"


def _norm(path: str) -> str:
    return path.strip().rstrip("/")


def evaluate(name: str,
             manifest_raw: str | None,
             build_log: str,
             test_doc_hits: int) -> tuple[list[Finding], list[str]]:
    """Pure core. `manifest_raw` is None when the file is absent; `test_doc_hits` is the number
    of files under docs/ that name this artifact directory."""
    errors: list[Finding] = []
    warnings: list[str] = []

    if manifest_raw is None:
        errors.append(Finding(
            "no-manifest",
            f"{ARTIFACT_ROOT}/{name}/manifest.json does not exist. build-agent writes the "
            f"manifest as the LAST act of a build, so its absence means the build did not "
            f"finish — the zips and test-results present in the directory are what a build "
            f"leaves BEFORE it finishes, not evidence that it did (IMP-0582).",
            "do not deploy this directory. Re-run build-agent, which will resolve a fresh "
            "directory via scripts/resolve-artifact-dir.py, and deploy the artifact named on "
            "its HANDOFF line. Leave this one in place as evidence.",
        ))
        # Nothing else is knowable without a manifest; the build.log check still is.
    else:
        try:
            manifest = json.loads(manifest_raw)
        except json.JSONDecodeError as exc:
            manifest = None
            errors.append(Finding(
                "manifest-unparseable",
                f"{ARTIFACT_ROOT}/{name}/manifest.json is not valid JSON: {exc}",
                "re-run build-agent; a truncated manifest is a half-written one.",
            ))
        if isinstance(manifest, dict):
            declared = _norm(str(manifest.get("artifact_path", "")))
            expected = f"{ARTIFACT_ROOT}/{name}"
            if not declared:
                errors.append(Finding(
                    "manifest-names-no-artifact",
                    "manifest.json carries no 'artifact_path'. Without it the manifest cannot "
                    "be tied to the directory it sits in.",
                    "re-run build-agent.",
                ))
            elif declared != expected:
                errors.append(Finding(
                    "manifest-names-another-artifact",
                    f"manifest.json's artifact_path is '{declared}', not '{expected}'. A "
                    f"manifest copied from a sibling build proves that sibling ran, not this "
                    f"one.",
                    "re-run build-agent for this feature rather than reusing a directory.",
                ))
            status = manifest.get("status")
            if not isinstance(status, str) or not status.strip():
                errors.append(Finding(
                    "build-status-absent",
                    "manifest.json carries no 'status'. A build with no recorded outcome is "
                    "not a build that succeeded.",
                    "re-run build-agent.",
                ))
            elif not status.strip().upper().startswith(OK_STATUS_PREFIXES):
                errors.append(Finding(
                    "build-not-successful",
                    f"manifest.json records status '{status.strip()[:120]}'. A deploy target's "
                    f"status must begin with one of {list(OK_STATUS_PREFIXES)}.",
                    "deploy the artifact from a build that succeeded. If build-agent now "
                    "writes a legitimate third outcome word, add it to OK_STATUS_PREFIXES in "
                    "this script in the same change that introduces it.",
                ))

    if test_doc_hits == 0:
        errors.append(Finding(
            "no-test-report-names-this-build",
            f"no file under {TEST_DOCS}/ names '{name}'. test-agent's report names the "
            f"specific build it approved (C-TECH-030's build → test → deploy chain), so a "
            f"build no report names has not been approved for deploy.",
            f"route the artifact to test-agent first, or — if a report does cover it — make "
            f"that report name '{name}' explicitly rather than by implication.",
        ))

    if not re.search(rf"SUCCESS — {re.escape(ARTIFACT_ROOT)}/{re.escape(name)}/?(\s|$)",
                     build_log, re.MULTILINE):
        warnings.append(
            f"no 'SUCCESS — {ARTIFACT_ROOT}/{name}' line in {BUILD_LOG}. That log is appended "
            f"by hand at the end of a dispatch, so this is evidence a log write was skipped "
            f"rather than evidence the build never ran — the manifest is the load-bearing "
            f"signal. Append the missing line if the build did succeed."
        )

    return errors, warnings


def check_dir(artifact_dir: Path, repo_root: Path) -> tuple[list[Finding], list[str]]:
    name = artifact_dir.name
    if not artifact_dir.is_dir():
        return [Finding(
            "no-artifact-directory",
            f"{artifact_dir} does not exist or is not a directory.",
            "check the artifact path on build-agent's HANDOFF line; do not guess it from a "
            "directory listing.",
        )], []

    manifest_path = artifact_dir / "manifest.json"
    manifest_raw = (manifest_path.read_text(encoding="utf-8")
                    if manifest_path.is_file() else None)

    build_log_path = repo_root / BUILD_LOG
    build_log = build_log_path.read_text(encoding="utf-8") if build_log_path.is_file() else ""

    test_dir = repo_root / TEST_DOCS
    hits = 0
    if test_dir.is_dir():
        for f in test_dir.rglob("*"):
            if f.is_file():
                try:
                    if name in f.read_text(encoding="utf-8", errors="ignore"):
                        hits += 1
                except OSError:
                    continue

    return evaluate(name, manifest_raw, build_log, hits)


def selftest() -> int:
    failures: list[str] = []
    good_manifest = json.dumps({
        "artifact_path": "build/artifacts/feat-20260902-2/",
        "status": "SUCCESS",
    })
    log = "[2026-09-02 13:32] [BUILD] [feat] SUCCESS — build/artifacts/feat-20260902-2/\n"

    # 1. The complete case passes with no finding at all.
    e, w = evaluate("feat-20260902-2", good_manifest, log, 1)
    if e or w:
        failures.append(f"a complete artifact must pass clean, got {e} / {w}")

    # 2. IMP-0582 itself: zips on disk, no manifest, no build.log line, no test report.
    e, w = evaluate("feat-20260902-3", None, log, 0)
    kinds = {f.kind for f in e}
    if kinds != {"no-manifest", "no-test-report-names-this-build"}:
        failures.append(f"the IMP-0582 shape must fail on manifest and test report, got {kinds}")
    if len(w) != 1:
        failures.append(f"the IMP-0582 shape must also warn on build.log, got {w}")

    # 3. A manifest copied from a sibling build.
    e, _ = evaluate("feat-20260902-3", good_manifest, log, 1)
    if [f.kind for f in e] != ["manifest-names-another-artifact"]:
        failures.append(f"a copied manifest must be caught, got {[f.kind for f in e]}")

    # 4. A failed build is never a deploy target.
    bad = json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/",
                      "status": "FAILED - halted at unit-tests"})
    e, _ = evaluate("feat-20260902-2", bad, log, 1)
    if [f.kind for f in e] != ["build-not-successful"]:
        failures.append(f"a FAILED build must be rejected, got {[f.kind for f in e]}")

    # 5. BLOCKED likewise — this is what build-agent wrote for -20260902-4.
    blocked = json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/",
                          "status": "BLOCKED"})
    e, _ = evaluate("feat-20260902-2", blocked, log, 1)
    if [f.kind for f in e] != ["build-not-successful"]:
        failures.append(f"a BLOCKED build must be rejected, got {[f.kind for f in e]}")

    # 6. A null status is not a pass. revitalise-grant-automation-20260831-2 is the real one.
    e, _ = evaluate("feat-20260902-2",
                    json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/"}), log, 1)
    if [f.kind for f in e] != ["build-status-absent"]:
        failures.append(f"a missing status must be rejected, got {[f.kind for f in e]}")

    # 7. The FALSE POSITIVE this gate is designed not to produce: a real, tested, deployed
    #    artifact whose build.log line was never appended (revitalise-grant-automation-20260823-2)
    #    warns, and does not fail.
    e, w = evaluate("feat-20260902-2", good_manifest, "", 1)
    if e:
        failures.append(f"a missing build.log line must NOT fail the gate, got {e}")
    if len(w) != 1 or "appended by hand" not in w[0]:
        failures.append(f"a missing build.log line must produce one warning, got {w}")

    # 8. 'DEPLOYED TO DEV, NOT RUNNABLE — ...' is a real status on four artifacts and passes.
    deployed = json.dumps({
        "artifact_path": "build/artifacts/feat-20260902-2",   # no trailing slash: also real
        "status": "DEPLOYED TO DEV, NOT RUNNABLE — flows off, environment variables blank",
    })
    e, _ = evaluate("feat-20260902-2", deployed, log, 1)
    if e:
        failures.append(f"a DEPLOYED status and slashless artifact_path must pass, got {e}")

    # 9. A truncated manifest is not a silent pass.
    e, _ = evaluate("feat-20260902-2", '{"artifact_path": "build/art', log, 1)
    if not any(f.kind == "manifest-unparseable" for f in e):
        failures.append(f"a truncated manifest must be caught, got {[f.kind for f in e]}")

    if failures:
        print("verify-artifact-provenance --selftest: FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("verify-artifact-provenance --selftest: PASS — 9 fixtures (complete artifact; the "
          "IMP-0582 shape; manifest copied from a sibling; FAILED build; BLOCKED build; null "
          "status; missing build.log line WARNS and does not fail; DEPLOYED status with a "
          "slashless artifact_path; truncated manifest)")
    return 0


def report(artifact_dir: Path, errors: list[Finding], warnings: list[str]) -> int:
    for w in warnings:
        print(f"  WARNING {w}")
    if errors:
        print(f"verify-artifact-provenance: FAILED — {artifact_dir} is not a deployable "
              f"build artifact ({len(errors)} problem(s)). C-TECH-030 (HARD): do not begin "
              f"Stage 1.")
        for f in errors:
            print(f.render())
        return 1
    print(f"verify-artifact-provenance: PASS — {artifact_dir} has a build record "
          f"(manifest.json, a successful status, and a test report naming it)"
          f"{' with 1 warning' if warnings else ''}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("artifact_dir", nargs="?", help="the artifact directory cited for deploy")
    ap.add_argument("--selftest", action="store_true", help="run built-in fixtures")
    ap.add_argument("--corpus", action="store_true",
                    help="report over every directory under build/artifacts (measurement only; "
                         "always exits 0)")
    ap.add_argument("--root", default=str(REPO_ROOT), help="repo root (for the tests)")
    args = ap.parse_args(argv)

    repo_root = Path(args.root)

    if args.selftest:
        return selftest()

    if args.corpus:
        for d in sorted((repo_root / ARTIFACT_ROOT).iterdir()):
            if not d.is_dir():
                continue
            e, w = check_dir(d, repo_root)
            print(f"{'FAIL' if e else 'pass'} {d.name}: "
                  f"{','.join(f.kind for f in e) or 'clean'}"
                  f"{' | WARN no-build-log-entry' if w else ''}")
        return 0

    if not args.artifact_dir:
        ap.error("an artifact directory is required (or --selftest / --corpus)")

    artifact_dir = Path(args.artifact_dir)
    errors, warnings = check_dir(artifact_dir, repo_root)
    return report(artifact_dir, errors, warnings)


if __name__ == "__main__":
    sys.exit(main())
