#!/usr/bin/env python3
"""Instance wrapper for the engine's generic run-deploy.py (Phase 7).

The mechanism lives at .engine/scripts/run-deploy.py and knows no client's environment
names. This wrapper supplies Revitalise's own environment_chain from instance.yaml by
default (so the last-hop gate check resolves against THIS client's actual chain,
dev/tst_acc/prd, without the caller having to type it every time).

USAGE (unchanged, --environment-chain applied automatically when omitted):
    python3 scripts/run-deploy.py config/revitalise-grant-automation-pipeline.yml tst_acc --skip-promotion
    python3 scripts/run-deploy.py config/revitalise-grant-automation-pipeline.yml prd --gate-keyword "APPROVE PRD"
    python3 scripts/run-deploy.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "run-deploy.py"
INSTANCE_YAML = REPO_ROOT / "instance.yaml"


def _load_engine():
    name = "_engine_run_deploy"
    spec = importlib.util.spec_from_file_location(name, ENGINE_SCRIPT)
    if spec is None or spec.loader is None:
        print(f"ERROR: could not load engine script at {ENGINE_SCRIPT} — is the .engine "
              f"submodule initialized? (git submodule update --init)", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _default_environment_chain() -> str | None:
    if yaml is None or not INSTANCE_YAML.exists():
        return None
    doc = yaml.safe_load(INSTANCE_YAML.read_text(encoding="utf-8")) or {}
    chain = doc.get("environment_chain")
    if isinstance(chain, list) and chain:
        return ",".join(chain)
    return None


def main(argv: list[str] | None = None) -> int:
    engine = _load_engine()
    argv = list(argv if argv is not None else sys.argv[1:])
    if "--environment-chain" not in argv and "--selftest" not in argv:
        default_chain = _default_environment_chain()
        if default_chain:
            argv = argv + ["--environment-chain", default_chain]
    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
