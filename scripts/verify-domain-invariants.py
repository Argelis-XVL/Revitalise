#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-domain-invariants.py (Phase 3f).

Enforces the domain constraints (C-DOM-030, C-DOM-031, C-DOM-032, C-DOM-004, C-DOM-033) that
are mechanically decidable from solution source, against
constraints/domain/special-category-register.yml. The entire register-consistency mechanism
moved to .engine/scripts/verify-domain-invariants.py as generic sensitive-data-governance
tooling -- see that file's docstring for the full IMP-0598 history and why UNADJUDICATED-SECURED
is shaped as an enumerated set rather than a heuristic.

Note: the engine's generic messages use descriptive labels (REGISTER-ENTITY-MISMATCH,
SECURITY-REQUIRED, AUDIT-REQUIRED, DUPLICATE-ENTITY, UNADJUDICATED-SECURED) rather than this
project's own C-DOM-nnn constraint IDs, since those IDs are Revitalise's own numbering. Map:
  REGISTER-ENTITY-MISMATCH -> C-DOM-030   SECURITY-REQUIRED    -> C-DOM-031
  AUDIT-REQUIRED           -> C-DOM-032   DUPLICATE-ENTITY     -> C-DOM-004
  UNADJUDICATED-SECURED    -> C-DOM-033

USAGE (unchanged from before the split):
    python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation

Wired into config/revitalise-grant-automation-build.yml as the `domain-invariants` step.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-domain-invariants.py"

DEFAULT_REGISTER = "constraints/domain/special-category-register.yml"
FR016_STEP = "no-special-category-data-in-scoring"
DEFAULT_BUILD_CONFIG = "config/revitalise-grant-automation-build.yml"


def _load_engine():
    name = "_engine_verify_domain_invariants"
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

    if "--register" not in argv:
        argv = argv + ["--register", DEFAULT_REGISTER]
    if "--build-config" not in argv:
        argv = argv + ["--build-config", DEFAULT_BUILD_CONFIG, "--fr016-step", FR016_STEP]
    elif "--fr016-step" not in argv:
        argv = argv + ["--fr016-step", FR016_STEP]

    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
