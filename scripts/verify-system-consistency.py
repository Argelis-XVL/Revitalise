#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-system-consistency.py (Phase 9).

The mechanism lives at .engine/scripts/verify-system-consistency.py and is entirely generic —
it composes existing gates (generate-subagents.py --check, validate-instance.py,
verify-routing-reconciliation.py) and one new orphan-doc check, all read-only. This wrapper
exists only so the callable path stays scripts/verify-system-consistency.py, matching every
other Phase 3f/4/5/6/7/8 wrapper.

USAGE:
    python3 scripts/verify-system-consistency.py
    python3 scripts/verify-system-consistency.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-system-consistency.py"


def _load_engine():
    name = "_engine_verify_system_consistency"
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
