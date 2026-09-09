#!/usr/bin/env python3
"""Instance wrapper for the engine's generic route-cascade.py (Phase 5).

The mechanism lives at .engine/scripts/route-cascade.py and is entirely generic — it loads,
validates, renders and routes against .engine/loops/delivery.loop.yaml, which carries no
Revitalise fact. This wrapper exists only so callers at the repo root
(`python3 scripts/route-cascade.py ...`) don't need to know the engine is a submodule,
matching the convention every Phase 3f/4 script established.

USAGE:
    python3 scripts/route-cascade.py                # validate the delivery loop
    python3 scripts/route-cascade.py --render        # print the phase chain
    python3 scripts/route-cascade.py --route SPEC_GAP
    python3 scripts/route-cascade.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "route-cascade.py"


def _load_engine():
    name = "_engine_route_cascade"
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
    # No positional loop path is passed by default, so the engine module resolves its own
    # DEFAULT_LOOP (relative to itself) rather than the instance's cwd.
    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
