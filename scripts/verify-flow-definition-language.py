#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-flow-definition-language.py (Phase 3f).

THE GENERAL GATE FOR CLASS `platform-contract-guessed-not-groundtruthed` (x16 in
logs/known-failure-modes.md). Checks 1-6's mechanism (nonexistent expression functions,
alternate-key Row IDs, the asymmetric CreateRecord/UpdateRecord connector, InitializeVariable
scoping, the multi-Response Skipped trap, and the failure-path-reaches-error-recording check)
is pure Power Automate/Dataverse platform knowledge and moved to
.engine/scripts/verify-flow-definition-language.py unchanged. Check 7's mechanism (result()
immediate-children-only descent tracking, the terminate-only narrowing) also moved; its
EXCEPTIONS -- three live, dated, owned waivers on this project's actual flows -- stayed here as
config/flow-check7-exceptions.json, since they are actively-managed governance data, not a
platform fact.

Check 5's configuration: this project's error-recording path is `REV | Ops | Failure Alert`
(workflow 8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04) and the table it writes is `rev_errorlog`.

USAGE (unchanged from before the split):
    python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-flow-definition-language.py --selftest

--selftest runs the engine's synthetic-fixture proof AND this wrapper's own extended proof
against the REAL corpus: that the two live check-7 exceptions suppress today, and that an
artificially future date expires them. That real-corpus assertion cannot live in the engine
(it has no access to this solution's actual flows), so it stays here.

Exits 0 when every definition is clean, 1 on any violation or unreadable input, 2 on a usage
error. C-TECH-052.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-flow-definition-language.py"

FAILURE_ALERT_WORKFLOW = "8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04"
ERRORLOG_TABLE = "rev_errorlog"
CHECK7_EXCEPTIONS_PATH = "config/flow-check7-exceptions.json"
CORPUS = REPO_ROOT / "src" / "solutions" / "RevitaliseGrantAutomation"


def _load_engine():
    name = "_engine_verify_flow_definition_language"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _extended_selftest(engine) -> int:
    """The real-corpus proof the original script's own selftest carried: the two declared
    check-7 exceptions suppress today, and an artificially future date expires them."""
    if not CORPUS.is_dir():
        print("flow-definition-language wrapper selftest: SKIPPED — no solution tree at "
              f"{CORPUS} (run from the repository root).", file=sys.stderr)
        return 1

    exceptions = engine.load_check7_exceptions(CHECK7_EXCEPTIONS_PATH)
    checks = []

    rc_today = engine.run(
        CORPUS, failure_alert_workflow=FAILURE_ALERT_WORKFLOW, errorlog_table=ERRORLOG_TABLE,
        check7_exceptions=exceptions,
    )
    checks.append(("the two declared exceptions suppress the FAILURE today", rc_today == 0))

    rc_expired = engine.run(
        CORPUS, failure_alert_workflow=FAILURE_ALERT_WORKFLOW, errorlog_table=ERRORLOG_TABLE,
        check7_exceptions=exceptions, today="2099-01-01",
    )
    checks.append(("an EXPIRED exception fails the build", rc_expired == 1))

    print("\n── WRAPPER SELFTEST (real corpus) ─────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\nflow-definition-language wrapper selftest: FAILED — {len(failed)} check(s)",
              file=sys.stderr)
        return 1
    print(f"\nflow-definition-language wrapper selftest: OK — {len(checks)} check(s) against "
          "the real corpus.")
    return 0


def main(argv: list[str] | None = None) -> int:
    engine = _load_engine()
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--selftest" in argv:
        engine_rc = engine.main(["verify-flow-definition-language.py", "--selftest"])
        wrapper_rc = _extended_selftest(engine)
        return engine_rc or wrapper_rc

    if "--failure-alert-workflow" not in argv:
        argv = argv + ["--failure-alert-workflow", FAILURE_ALERT_WORKFLOW]
    if "--errorlog-table" not in argv:
        argv = argv + ["--errorlog-table", ERRORLOG_TABLE]
    if "--check7-exceptions" not in argv:
        argv = argv + ["--check7-exceptions", CHECK7_EXCEPTIONS_PATH]

    return engine.main(["verify-flow-definition-language.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
