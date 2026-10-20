#!/usr/bin/env python3
"""An artifact directory cited for deploy went through build-agent's managed process.

`C-TECH-030` — pipeline-agent's pre-Stage-1 preflight. Run it against the directory a
dispatch names as its deploy target, BEFORE any `deploy_command` or ALM stage executes.

    python3 scripts/verify-artifact-provenance.py build/artifacts/<slug>-<YYYYMMDD>-<n>/ --env <env>

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
  * BEYOND THE FIRST ENVIRONMENT of `instance.yaml` → `environment_chain` (or with no `--env`):
    some file under `docs/tests/` names this directory AND at least one such report's first
    `**Status:**` word is PASS or PARTIAL. A report that merely mentions the build is not approval
    of it (IMP-1134): a FAIL report naming the build used to pass this check. Any other word, an
    unparseable status included, is not approval (fail closed). For the FIRST environment no test
    report is required: reviewer decision D-1, 2026-10-17, verbatim: "tests happen in DEV. Customer
    tests happen in ACC. Solutions move from DEV to ACC via Power Platform Pipelines." A DEV deploy
    is what test-agent tests, so requiring its report first was circular (IMP-1132: two DEV deploys
    halted on it on 2026-10-16).

  * a CHANGE-SCOPED artifact (`scoped: true` in `manifest.json` or `run-build-result.json`) is
    deployed only to the FIRST environment of `instance.yaml` → `environment_chain`, and only
    with `--env <name>` saying where it is going (IMP-1052). A scoped build skipped producer
    steps, so its directory is deliberately incomplete; whatever is promoted from the first
    environment must come from a full run. Unscoped artifacts are unaffected by `--env`.

AND ONE WARNING (exit 0, reported)
----------------------------------
  * no `logs/build.log` line whose status word is `SUCCESS` and which names `build/artifacts/<name>`

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
  * 1 of those 9 (`revitalise-grant-automation-20260823-2`) raised the build.log WARNING. That
    observation was FALSE: its SUCCESS line exists and names the artifact later in the sentence,
    which the one fixed `SUCCESS — path` shape could not see. Re-measured 2026-10-08 (improvement
    review 2026-10-07, IMP-1093) over 162 artifact names: the old shape recognised 49 and the
    status-word anchor recognises 53, all 4 added real successes, 0 lost.
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


def build_log_records_success(name: str, build_log: str) -> bool:
    """True when some build.log line's STATUS WORD is SUCCESS and the line names the artifact.

    The status word is the first word after the line's leading `[...]` tags and an optional
    `wbs:<ids>` token. Anchoring on it, rather than on one fixed `SUCCESS — path` shape, is
    IMP-1093: the writer is an agent's free text and has produced a hyphen for the em dash, a
    `wbs:` tag before the word, a `(V2 packaged)` qualifier after it, and the path later in the
    sentence. A line that starts BLOCKED or FAILED and mentions SUCCESS later still does not match.
    """
    pattern = re.compile(
        rf"^(?:\[[^\]\n]*\]\s*)*(?:wbs:\S+\s+)?SUCCESS\b[^\n]*?"
        rf"{re.escape(ARTIFACT_ROOT)}/{re.escape(name)}(?![A-Za-z0-9._-])",
        re.MULTILINE)
    return bool(pattern.search(build_log))


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
             build_log: str) -> tuple[list[Finding], list[str]]:
    """Pure core of the build-record checks. `manifest_raw` is None when the file is absent.
    The test-report rule is evaluate_test_reports(), because it depends on the target."""
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

    if not build_log_records_success(name, build_log):
        warnings.append(
            f"no line in {BUILD_LOG} whose status word is SUCCESS and which names "
            f"{ARTIFACT_ROOT}/{name}. That log is appended "
            f"by hand at the end of a dispatch, so this is evidence a log write was skipped "
            f"rather than evidence the build never ran — the manifest is the load-bearing "
            f"signal. Append the missing line if the build did succeed."
        )

    return errors, warnings


def environment_chain(repo_root: Path) -> list[str]:
    """`instance.yaml` → `environment_chain`, in order. Empty when absent or unreadable."""
    path = repo_root / "instance.yaml"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        doc = yaml.safe_load(text) or {}
        chain = doc.get("environment_chain") if isinstance(doc, dict) else None
        if isinstance(chain, list):
            return [str(e).strip() for e in chain if str(e).strip()]
    except Exception:  # noqa: BLE001 — fall back to the flow-style line below
        pass
    m = re.search(r"^environment_chain:\s*\[([^\]]*)\]", text, re.MULTILINE)
    return [e.strip().strip("'\"") for e in m.group(1).split(",") if e.strip()] if m else []


# The first `**Status:**` word of a test report. Enumerated over the 49 reports under docs/tests/
# on 2026-10-16: every one parses, to PASS 17, FAIL 16, PARTIAL 15, BLOCKED 1 (IMP-1134).
STATUS_WORD = re.compile(r"^\*\*Status:?\s*(?:\*\*)?:?\s*\**\s*([A-Z]+)", re.MULTILINE)
APPROVING_STATUSES = ("PASS", "PARTIAL")


def report_status(text: str) -> str | None:
    """The first Status word of a test report, or None when it has none."""
    m = STATUS_WORD.search(text)
    return m.group(1) if m else None


def evaluate_test_reports(name: str, statuses: list[str | None], env: str | None,
                          chain: list[str]) -> list[Finding]:
    """Pure core of the test-report rule. `statuses` holds one entry per docs/tests/ file that
    names the artifact. No report is needed for the first environment (D-1, 2026-10-17); beyond
    it, or with no --env, one naming report must say PASS or PARTIAL (IMP-1134)."""
    if env and chain and env == chain[0]:
        return []
    if not statuses:
        return [Finding(
            "no-test-report-names-this-build",
            f"no file under {TEST_DOCS}/ names '{name}'. Beyond the first environment a deploy "
            f"needs test-agent's report on this specific build (C-TECH-030).",
            f"route the artifact to test-agent first, or — if a report does cover it — make "
            f"that report name '{name}' explicitly rather than by implication.",
        )]
    if not any(s in APPROVING_STATUSES for s in statuses):
        found = ", ".join(sorted({s or "no Status line" for s in statuses}))
        return [Finding(
            "no-passing-test-report-names-this-build",
            f"{len(statuses)} report(s) under {TEST_DOCS}/ name '{name}', and none has a Status "
            f"of {' or '.join(APPROVING_STATUSES)} (found: {found}). A report that names a build "
            f"is not approval of it (IMP-1134).",
            "fix what the report failed on, rebuild, and have test-agent report on the new build.",
        )]
    return []


def evaluate_scope(scoped: bool, env: str | None, chain: list[str]) -> list[Finding]:
    """Pure core of the IMP-1052 check. A change-scoped artifact goes to the first environment of
    the chain and nowhere else; an unscoped one is not this check's business."""
    if not scoped:
        return []
    if not env:
        return [Finding(
            "scoped-artifact-needs-env",
            "this artifact is CHANGE-SCOPED (scoped: true): a run-build.py --changed-since run "
            "skipped producer steps, so the directory is deliberately incomplete. Where it may "
            "go depends on the target environment, and none was given.",
            "re-run with --env <the environment this deploy targets>.",
        )]
    if not chain:
        return [Finding(
            "no-environment-chain",
            "this artifact is CHANGE-SCOPED and instance.yaml declares no environment_chain, so "
            "the first environment — the only one a scoped artifact may reach — is unknown.",
            "declare environment_chain in instance.yaml, or deploy a full (unscoped) build.",
        )]
    if env != chain[0]:
        return [Finding(
            "scoped-artifact-beyond-first-environment",
            f"this artifact is CHANGE-SCOPED and the target is '{env}', but a scoped artifact "
            f"deploys only to '{chain[0]}' (the first of {chain}). Whatever is promoted from "
            f"'{chain[0]}' must come from a full run (IMP-1052).",
            "run build-agent WITHOUT --changed-since, deploy that artifact to the first "
            "environment, and promote from there.",
        )]
    return []


def _scoped_flag(artifact_dir: Path) -> bool:
    for fname in ("manifest.json", "run-build-result.json"):
        f = artifact_dir / fname
        if f.is_file():
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(doc, dict) and doc.get("scoped") is True:
                return True
    return False


def check_dir(artifact_dir: Path, repo_root: Path,
              env: str | None = None) -> tuple[list[Finding], list[str]]:
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
    statuses: list[str | None] = []
    if test_dir.is_dir():
        for f in test_dir.rglob("*"):
            if f.is_file():
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if name in text:
                    statuses.append(report_status(text))

    chain = environment_chain(repo_root)
    errors, warnings = evaluate(name, manifest_raw, build_log)
    errors += evaluate_test_reports(name, statuses, env, chain)
    errors += evaluate_scope(_scoped_flag(artifact_dir), env, chain)
    return errors, warnings


def selftest() -> int:
    failures: list[str] = []
    good_manifest = json.dumps({
        "artifact_path": "build/artifacts/feat-20260902-2/",
        "status": "SUCCESS",
    })
    log = "[2026-09-02 13:32] [BUILD] [feat] SUCCESS — build/artifacts/feat-20260902-2/\n"

    # 1. The complete case passes with no finding at all.
    e, w = evaluate("feat-20260902-2", good_manifest, log)
    if e or w:
        failures.append(f"a complete artifact must pass clean, got {e} / {w}")

    # 2. IMP-0582 itself: zips on disk, no manifest, no build.log line, no test report.
    e, w = evaluate("feat-20260902-3", None, log)
    kinds = {f.kind for f in e} | {f.kind for f in evaluate_test_reports(
        "feat-20260902-3", [], "tst", ["dev", "tst", "prd"])}
    if kinds != {"no-manifest", "no-test-report-names-this-build"}:
        failures.append(f"the IMP-0582 shape must fail on manifest and test report, got {kinds}")
    if len(w) != 1:
        failures.append(f"the IMP-0582 shape must also warn on build.log, got {w}")

    # 3. A manifest copied from a sibling build.
    e, _ = evaluate("feat-20260902-3", good_manifest, log)
    if [f.kind for f in e] != ["manifest-names-another-artifact"]:
        failures.append(f"a copied manifest must be caught, got {[f.kind for f in e]}")

    # 4. A failed build is never a deploy target.
    bad = json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/",
                      "status": "FAILED - halted at unit-tests"})
    e, _ = evaluate("feat-20260902-2", bad, log)
    if [f.kind for f in e] != ["build-not-successful"]:
        failures.append(f"a FAILED build must be rejected, got {[f.kind for f in e]}")

    # 5. BLOCKED likewise — this is what build-agent wrote for -20260902-4.
    blocked = json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/",
                          "status": "BLOCKED"})
    e, _ = evaluate("feat-20260902-2", blocked, log)
    if [f.kind for f in e] != ["build-not-successful"]:
        failures.append(f"a BLOCKED build must be rejected, got {[f.kind for f in e]}")

    # 6. A null status is not a pass. revitalise-grant-automation-20260831-2 is the real one.
    e, _ = evaluate("feat-20260902-2",
                    json.dumps({"artifact_path": "build/artifacts/feat-20260902-2/"}), log)
    if [f.kind for f in e] != ["build-status-absent"]:
        failures.append(f"a missing status must be rejected, got {[f.kind for f in e]}")

    # 7. The FALSE POSITIVE this gate is designed not to produce: a real, tested, deployed
    #    artifact whose build.log line was never appended (revitalise-grant-automation-20260823-2)
    #    warns, and does not fail.
    e, w = evaluate("feat-20260902-2", good_manifest, "")
    if e:
        failures.append(f"a missing build.log line must NOT fail the gate, got {e}")
    if len(w) != 1 or "appended by hand" not in w[0]:
        failures.append(f"a missing build.log line must produce one warning, got {w}")

    # 8. 'DEPLOYED TO DEV, NOT RUNNABLE — ...' is a real status on four artifacts and passes.
    deployed = json.dumps({
        "artifact_path": "build/artifacts/feat-20260902-2",   # no trailing slash: also real
        "status": "DEPLOYED TO DEV, NOT RUNNABLE — flows off, environment variables blank",
    })
    e, _ = evaluate("feat-20260902-2", deployed, log)
    if e:
        failures.append(f"a DEPLOYED status and slashless artifact_path must pass, got {e}")

    # 9. A truncated manifest is not a silent pass.
    e, _ = evaluate("feat-20260902-2", '{"artifact_path": "build/art', log)
    if not any(f.kind == "manifest-unparseable" for f in e):
        failures.append(f"a truncated manifest must be caught, got {[f.kind for f in e]}")

    # 10-13. IMP-1052: a change-scoped artifact goes to the first environment only.
    chain = ["dev", "test", "prod"]
    if evaluate_scope(True, "dev", chain):
        failures.append("a scoped artifact to the FIRST environment must pass")
    if [f.kind for f in evaluate_scope(True, "test", chain)] != [
            "scoped-artifact-beyond-first-environment"]:
        failures.append("a scoped artifact to a LATER environment must fail")
    if [f.kind for f in evaluate_scope(True, None, chain)] != ["scoped-artifact-needs-env"]:
        failures.append("a scoped artifact with NO --env must fail and say to pass it")
    if evaluate_scope(False, "prod", chain) or evaluate_scope(False, None, chain):
        failures.append("an unscoped artifact must be unaffected, with or without --env")

    # 14. The flag is read from the directory: run-build-result.json alone is enough.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "manifest.json").write_text(json.dumps({"status": "SUCCESS"}), encoding="utf-8")
        if _scoped_flag(d):
            failures.append("a manifest with no scoped flag must read as unscoped")
        (d / "run-build-result.json").write_text(json.dumps({"scoped": True}), encoding="utf-8")
        if not _scoped_flag(d):
            failures.append("scoped: true in run-build-result.json must be read")
        (d / "instance.yaml").write_text("environment_chain: [dev, stage, live]\n",
                                         encoding="utf-8")
        if environment_chain(d) != ["dev", "stage", "live"]:
            failures.append(f"environment_chain not read: {environment_chain(d)}")

    # 15-17. IMP-1093: the status word is what is anchored, not one fixed line shape.
    real = ("[2026-10-07 12:22] [BUILD] [feat] wbs:5.3,5.4,5.6 SUCCESS (V2 packaged) — "
            "build/artifacts/feat-20260902-2/ — re-dispatch of blocked -2\n")
    hyphen = "[2026-09-30 09:40] [BUILD] [feat] SUCCESS - build/artifacts/feat-20260902-2 (V2)\n"
    blocked_line = ("[2026-09-30 09:40] [BUILD] [feat] BLOCKED — lint red after a SUCCESS pack of "
                    "build/artifacts/feat-20260902-2/\n")
    for label, text in (("the 20261007-3 line", real), ("the hyphen line", hyphen)):
        _, w = evaluate("feat-20260902-2", good_manifest, text)
        if w:
            failures.append(f"{label} records a success and must not warn, got {w}")
    _, w = evaluate("feat-20260902-2", good_manifest, blocked_line)
    if len(w) != 1:
        failures.append(f"a BLOCKED line naming the artifact must still warn, got {w}")
    _, w = evaluate("feat-20260902-2", good_manifest,
                    "[2026-09-02 13:32] [BUILD] [feat] SUCCESS — build/artifacts/feat-20260902-21/\n")
    if len(w) != 1:
        failures.append(f"a SUCCESS line naming a LONGER artifact name must still warn, got {w}")

    # 19-23. IMP-1134 and reviewer decision D-1 (2026-10-17): the report's VERDICT, and only
    #        beyond the first environment.
    ch = ["dev", "tst", "prd"]
    if [f.kind for f in evaluate_test_reports("b", ["FAIL"], "tst", ch)] != [
            "no-passing-test-report-names-this-build"]:
        failures.append("a FAIL-only report must not approve a deploy beyond the first environment")
    if evaluate_test_reports("b", ["FAIL"], "dev", ch) or evaluate_test_reports("b", [], "dev", ch):
        failures.append("the first environment needs no test report, whatever exists (D-1)")
    if evaluate_test_reports("b", ["FAIL", "PASS"], "prd", ch) or \
            evaluate_test_reports("b", ["PARTIAL"], "tst", ch):
        failures.append("a PASS or PARTIAL report naming the build must approve it")
    if [f.kind for f in evaluate_test_reports("b", [None], None, ch)] != [
            "no-passing-test-report-names-this-build"]:
        failures.append("no --env is strict, and a report with no Status line is not approval")
    if (report_status("x\n**Status:** PASS (scoped)\n") != "PASS"
            or report_status("**Status: FAIL** — reason\n") != "FAIL"
            or report_status("**Status:** **FAIL — gate BLOCKED.**\n") != "FAIL"):
        failures.append("the three Status line shapes in docs/tests/ must all parse")

    if failures:
        print("verify-artifact-provenance --selftest: FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("verify-artifact-provenance --selftest: PASS — 23 fixtures (complete artifact; the "
          "IMP-0582 shape; manifest copied from a sibling; FAILED build; BLOCKED build; null "
          "status; missing build.log line WARNS and does not fail; DEPLOYED status with a "
          "slashless artifact_path; truncated manifest; scoped artifact to the first, a later "
          "and no environment; unscoped unaffected; scoped flag and chain read from disk; "
          "build.log status word anchored: wbs-tagged and hyphen SUCCESS lines pass, a BLOCKED "
          "line and a longer artifact name still warn; test-report VERDICT beyond the first "
          "environment, none needed for the first, three Status shapes parse)")
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
          f"(manifest.json, a successful status, and — beyond the first environment — a "
          f"PASS or PARTIAL test report naming it)"
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
    ap.add_argument("--env", default=None,
                    help="the environment this deploy targets; required for a change-scoped "
                         "artifact, which may reach only the first of instance.yaml's "
                         "environment_chain (IMP-1052)")
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
    errors, warnings = check_dir(artifact_dir, repo_root, args.env)
    return report(artifact_dir, errors, warnings)


if __name__ == "__main__":
    sys.exit(main())
