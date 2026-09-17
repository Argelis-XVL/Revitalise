#!/usr/bin/env python3
"""Instance wrapper for the engine's generic generate-restricted-field-catalogue.py (Phase 3f).

Generates the trustee portal's restricted-field catalogue (ADR-032, FR-078, TAD §3.2.3). The
derivation mechanism (validate a manifest against the live field security profile and entity
schema, fail loudly on drift, render deterministic TypeScript with no logical column name in
the output) moved to .engine/scripts/generate-restricted-field-catalogue.py as the general
ADR-032 pattern -- see that file's docstring for why a hand-typed catalogue is unsafe.

The one client-specific fact that stayed here is WHICH eleven (entity, column) pairs belong on
this screen and which SDD §7.1b board-pack group each is in --
config/trustee-restricted-field-catalogue.json. That manifest cannot be read off any XML file;
it is a requirements decision, cited to SDD Amendment A-05 Finding 1.

Usage (unchanged from before the split)
-----
    python3 scripts/generate-trustee-field-catalogue.py
    python3 scripts/generate-trustee-field-catalogue.py --check

--check   Regenerate in memory and diff against the committed --out file; exit 1 if the
          committed file is stale, missing, or the manifest no longer matches ground truth.
          Wired into config/revitalise-grant-automation-build.yml as the
          `trustee-field-catalogue` step, BEFORE `no-secured-columns-in-code-app` and before
          typecheck/build (the app imports the generated file).

Exits 0 clean · 1 on any drift or validation failure · 2 on a usage error.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "generate-restricted-field-catalogue.py"

MANIFEST_PATH = "config/trustee-restricted-field-catalogue.json"
DEFAULT_PROFILE = "src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml"
DEFAULT_ENTITIES = "src/solutions/RevitaliseGrantAutomation/Entities"
DEFAULT_OUT = (
    "src/code-apps/trustee-review-portal/src/generated/trusteeRestrictedFieldCatalogue.ts"
)


def _load_engine():
    name = "_engine_generate_restricted_field_catalogue"
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
        return engine.main(["generate-restricted-field-catalogue.py", "--selftest"])

    defaults = {
        "--manifest": MANIFEST_PATH,
        "--profile": DEFAULT_PROFILE,
        "--entities": DEFAULT_ENTITIES,
        "--out": DEFAULT_OUT,
    }
    for flag, value in defaults.items():
        if flag not in argv:
            argv = argv + [flag, value]

    return engine.main(["generate-restricted-field-catalogue.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
