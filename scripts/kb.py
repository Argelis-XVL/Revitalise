#!/usr/bin/env python3
"""Instance wrapper for the engine's generic kb.py (Phase 6).

The knowledge-database mechanism lives entirely at .engine/scripts/kb.py and knows no
client's literals — `dump`'s content-redaction filter (6f) takes its denylist from the
CALLER, by design, so this wrapper supplies Revitalise's own: the client name, and this
solution's `rev_` Dataverse table/column prefix convention (provisioning/dataverse and every
src/solutions/RevitaliseGrantAutomation/Entities/rev_*.xml file uses it). Every other kb.py
command passes straight through unchanged.

USAGE (unchanged from the engine script, `dump` gets Revitalise's defaults for free):
    python3 scripts/kb.py init
    python3 scripts/kb.py migrate --log logs/improvement-log.jsonl
    python3 scripts/kb.py dump --out .engine/kb.sql          # redact terms applied automatically
    python3 scripts/kb.py dump --out /tmp/backup.sql --include-instance --redact ""  # override
    python3 scripts/kb.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "kb.py"

# This client's own literals — never read by the engine script itself. Kept here, not in
# instance.yaml, because it is a dump-time redaction denylist, not delivery configuration.
DEFAULT_REDACT_TERMS = ["revitalise", r"rev_[a-z0-9_]*", "tst_acc"]


def _load_engine():
    name = "_engine_kb"
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
    if argv and argv[0] == "dump" and "--redact" not in argv:
        argv = argv + [a for term in DEFAULT_REDACT_TERMS for a in ("--redact", term)]
    return engine.main(argv)


if __name__ == "__main__":
    sys.exit(main())
