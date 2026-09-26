#!/usr/bin/env python3
"""Instance wrapper for the engine's work-item ledger verifier (WS-W1).

The mechanism lives at .engine/scripts/verify-work-items.py and the one ledger module at
.engine/scripts/lib/work_items.py; neither names this client. This instance supplies no facts of
its own here: the id prefix, environment chain and contract location are read by the engine from
instance.yaml. This wrapper exists so every caller keeps calling `scripts/verify-work-items.py`, the
convention every Phase 3f script established.

USAGE (unchanged from the engine script):
    python3 scripts/verify-work-items.py --check
    python3 scripts/verify-work-items.py --check --scope WI-0001,WI-0002 --at-least built
    python3 scripts/verify-work-items.py --warn-only
    python3 scripts/verify-work-items.py --selftest

Specification: docs/improvements/2026-09-26-improvement-review.md section 3.6. Wired into
config/revitalise-grant-automation-build.yml as the SOFT `work-items` step (--warn-only).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-work-items.py"


def _load_engine():
    name = "_engine_verify_work_items"
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
    return _load_engine().main(argv)


if __name__ == "__main__":
    sys.exit(main())
