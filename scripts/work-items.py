#!/usr/bin/env python3
"""Instance wrapper for the engine's work-item ledger write tool (WS-W1).

The mechanism lives at .engine/scripts/work-items.py and its one ledger module at
.engine/scripts/lib/work_items.py; neither names this client. This instance supplies no facts of
its own here: the id prefix, environment chain and contract location are read by the engine from
instance.yaml. This wrapper exists so every caller keeps calling `scripts/work-items.py`, the
convention every Phase 3f script established.

USAGE (unchanged from the engine script):
    python3 scripts/work-items.py add --type pbi --title "..." --source-ref "..." --acceptance "..." --by pm-agent
    python3 scripts/work-items.py transition WI-0001 built --evidence ev.json --by development-agent
    python3 scripts/work-items.py export --format table
    python3 scripts/work-items.py --selftest

Specification: docs/improvements/2026-09-26-improvement-review.md section 3.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "work-items.py"


def _load_engine():
    name = "_engine_work_items"
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
