#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-field-security-coverage.py (Phase 3f).

The checking mechanism -- secured-vs-released coverage, the primary-name-cannot-be-secured
check, the Money _base-twin warning, the secured-lookup name-companion warning, and the
config/gate-baselines.json consultation -- moved to
.engine/scripts/verify-field-security-coverage.py, entirely as Power Platform/Dataverse
platform knowledge. See that file's docstring for the full incident history (IMP-0249,
IMP-0047, IMP-0255) behind each check.

The one client-specific fact that stayed here is this solution's own list of columns that are
deliberately, permanently unsecured despite being personal data --
config/field-security-exemptions.json (currently one entry: rev_application.rev_breaklocation,
per grant-application-data-model-v0.2.md).

USAGE (unchanged from before the split):
    python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-field-security-coverage.py --selftest

Wired into config/revitalise-grant-automation-build.yml as the `field-security-coverage` step.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-field-security-coverage.py"
EXEMPTIONS_PATH = "config/field-security-exemptions.json"


def _load_engine():
    name = "_engine_verify_field_security_coverage"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    engine = _load_engine()
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--selftest" in argv:
        return engine.main(["verify-field-security-coverage.py", "--selftest"])

    if "--exempt-unsecured" not in argv:
        argv = argv + ["--exempt-unsecured", EXEMPTIONS_PATH]

    return engine.main(["verify-field-security-coverage.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
