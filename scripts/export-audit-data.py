#!/usr/bin/env python3
"""Instance wrapper for the engine's audit-viewer export -- the work board (WS-W part W5).

The mechanism lives at .engine/scripts/export-audit-data.py and the page template at
.engine/templates/audit-viewer.html; neither names this client. This instance supplies no facts of
its own here: the slug, ledger location and environment chain are read by the engine from
instance.yaml. No redaction list yet -- this view is for the reviewer's own machine (reviewer
decision S-4); a redaction list arrives with the Phase 11 view meant for an external auditor.

USAGE (unchanged from the engine script):
    python3 scripts/export-audit-data.py                 # -> docs/audit/<slug>-audit.html
    python3 scripts/export-audit-data.py --out-dir PATH
    python3 scripts/export-audit-data.py --selftest

Specification: docs/improvements/2026-09-26-improvement-review-5.md section 3.3.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "export-audit-data.py"


def _load_engine():
    name = "_engine_export_audit_data"
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
