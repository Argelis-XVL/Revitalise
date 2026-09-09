#!/usr/bin/env python3
"""Instance wrapper for the engine's generic validate-instance.py (Phase 4).

The checking mechanism lives at .engine/scripts/validate-instance.py — it is entirely
generic (no Revitalise fact appears in it) and takes the instance file to check as its only
argument, defaulting to ./instance.yaml. This wrapper exists only so every caller
(config/revitalise-grant-automation-build.yml, .github/workflows/ci.yml, a developer's shell)
can keep calling `scripts/validate-instance.py`, matching the convention every Phase 3f
script established.

USAGE:
    python3 scripts/validate-instance.py
    python3 scripts/validate-instance.py instance.yaml
    python3 scripts/validate-instance.py --selftest

Wired into config/revitalise-grant-automation-build.yml as the `validate-instance` step and
into .github/workflows/ci.yml's `validate` job (Phase 4, audit rec 13).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "validate-instance.py"


def _load_engine():
    name = "_engine_validate_instance"
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
    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
