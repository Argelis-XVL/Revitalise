#!/usr/bin/env python3
"""Instance wrapper for the engine's generic run-build.py (Phase 7).

The mechanism lives at .engine/scripts/run-build.py and is entirely generic. This wrapper
exists only so the callable path stays scripts/run-build.py, matching every other Phase
3f/4/5/6 wrapper in this repo.

USAGE:
    python3 scripts/run-build.py config/revitalise-grant-automation-build.yml
    python3 scripts/run-build.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "run-build.py"


def _load_engine():
    name = "_engine_run_build"
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
