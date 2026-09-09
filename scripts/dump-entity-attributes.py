#!/usr/bin/env python3
"""Instance wrapper for the engine's generic dump-entity-attributes.py (Phase 3f).

The checking mechanism moved to .engine/scripts/dump-entity-attributes.py — it is fully
generic, so nothing here re-implements it. This wrapper only supplies this instance's
solution path, so every existing caller of `scripts/dump-entity-attributes.py` (this repo's
own docs, IMP-nnnn findings, skills/how-to-verify-a-platform-contract.md) keeps working with
the exact same command line as before the split.

WHY THIS EXISTS. A negative claim about schema is the one claim a partial scan cannot
support — the evidence is the WHOLE attribute set. IMP-0326/IMP-0337/IMP-0338 are the incident
history for why this tool exists at all; see the engine copy's docstring for the full account
and skills/how-to-verify-a-platform-contract.md for the rule it makes one command to obey.

USAGE (unchanged from before the split):
    python3 scripts/dump-entity-attributes.py rev_application
    python3 scripts/dump-entity-attributes.py --list
    python3 scripts/dump-entity-attributes.py rev_application --grep date
    python3 scripts/dump-entity-attributes.py --all --grep location
    python3 scripts/dump-entity-attributes.py --selftest   (runs the ENGINE's synthetic-fixture
        selftest, plus this wrapper's own check that the instance solution path resolves)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "dump-entity-attributes.py"
DEFAULT_SOLUTION = REPO_ROOT / "src" / "solutions" / "RevitaliseGrantAutomation"


def _load_engine():
    name = "_engine_dump_entity_attributes"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses needs the module registered before exec
    spec.loader.exec_module(module)
    return module


def wrapper_selftest(engine) -> int:
    """This wrapper's own concern: does the instance solution path actually resolve."""
    if not DEFAULT_SOLUTION.is_dir():
        print(f"WRAPPER SELFTEST FAILURE: {DEFAULT_SOLUTION} does not exist.", file=sys.stderr)
        return 1
    dirs = engine.entities(DEFAULT_SOLUTION)
    if not dirs:
        print(f"WRAPPER SELFTEST FAILURE: no Entities/ found under {DEFAULT_SOLUTION}.",
              file=sys.stderr)
        return 1
    print(f"dump-entity-attributes wrapper selftest: OK — {DEFAULT_SOLUTION} resolves and has "
          f"{len(dirs)} entity(ies).")
    return 0


def main(argv: list[str] | None = None) -> int:
    engine = _load_engine()
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--selftest" in argv:
        engine_rc = engine.selftest()
        wrapper_rc = wrapper_selftest(engine)
        return engine_rc or wrapper_rc

    if "--solution" not in argv:
        argv = argv + ["--solution", str(DEFAULT_SOLUTION)]

    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
