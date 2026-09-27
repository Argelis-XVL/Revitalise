#!/usr/bin/env python3
"""Instance wrapper for the engine's post-deploy completeness gate (WS-X).

The mechanism lives at .engine/scripts/verify-post-deploy-completeness.py, and since improvement
review 2026-09-26 (6) its marker grammar and post_deploy vocabulary live in
.engine/scripts/lib/deploy_markers.py, shared with the work-item ledger's deploy-record evidence
(IMP-0909). An instance-side byte copy could not import that module, so this file became a wrapper
in the scripts/work-items.py pattern. It supplies no client facts: the pipeline config is passed on
the command line.

USAGE (unchanged from the engine script):
    python3 scripts/verify-post-deploy-completeness.py config/<slug>-pipeline.yml --env <env> --pending
    python3 scripts/verify-post-deploy-completeness.py config/<slug>-pipeline.yml --audit --as-of-git --warn-only
    python3 scripts/verify-post-deploy-completeness.py --selftest

Specification: docs/improvements/2026-09-26-improvement-review-3.md (WS-X) and
docs/improvements/2026-09-26-improvement-review-6.md section 3.5.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-post-deploy-completeness.py"


def _load_engine():
    name = "_engine_verify_post_deploy_completeness"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(2)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    return _load_engine().main(argv)


if __name__ == "__main__":
    sys.exit(main())
