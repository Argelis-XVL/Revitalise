#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-field-length-limits.py (Phase 3f).

THE GENERAL GATE FOR CLASS `platform-field-length-limit-unenforced`. This replaced two
retired instance-level gates (`verify-workflow-description-length.py`, C-TECH-049;
`verify-setting-description-length.py`, D-021), each of which hardcoded one field's limit as a
literal and asserted it instead of reading it — see
docs/improvements/agent-instruction-history.md for the incident history (IMP-0009 and the
`skills/how-to-promote-a-finding.md` §2 pattern this violated).

The checking mechanism moved to .engine/scripts/verify-field-length-limits.py — it reads
declared limits from Entity.xml generically and carries Power Automate's own fixed
flow-description limit (256 chars, PLATFORM_LIMITS) as reusable platform knowledge. The one
thing that stayed here is this client's own mapping from a settings-row JSON field to the
Dataverse column it lands in (`config/field-length-mappings.json` — from
provisioning/dataverse/seed-settings.ps1 lines 205-209), because that mapping is specific to
this solution's schema, not a Power Platform fact.

USAGE (unchanged from before the split):
    python3 scripts/verify-field-length-limits.py \
        src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings
    python3 scripts/verify-field-length-limits.py --check-fixtures ...
    python3 scripts/verify-field-length-limits.py --selftest

Wired into config/revitalise-grant-automation-build.yml as the `field-length-limits` step
(C-TECH-060).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-field-length-limits.py"
# Bare relative strings, matching the pre-split script's own defaults exactly (both were always
# relative to the invocation cwd, which build/pipeline config always sets to the repo root) --
# an absolute path here would still be correct but would change this gate's printed message,
# which callers may parse.
DEFAULT_SCHEMA_ROOT = "src/solutions/RevitaliseGrantAutomation"
COLUMN_MAP_PATH = "config/field-length-mappings.json"


def _load_engine():
    name = "_engine_verify_field_length_limits"
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
        return engine.main(["verify-field-length-limits.py", "--selftest"])

    if "--schema" not in argv:
        argv = argv + ["--schema", str(DEFAULT_SCHEMA_ROOT)]
    if "--column-map" not in argv:
        argv = argv + ["--column-map", str(COLUMN_MAP_PATH)]

    return engine.main(["verify-field-length-limits.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
