#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-flow-trigger-body-isolation.py (Phase 3f).

Makes two properties of `REV | Portal | Round Statistics` (TAD
docs/architecture/trustee-portal-visual-refresh-architecture.md §6.3.1/§6.3.3, ADR-038
APPROVED) into checked ones: it reads nothing from its own trigger body (Check A), and its
result document is composed from an enumerated field list, never a serialised row object
(Check B). The trigger-isolation and row-bearing-taint-fixpoint mechanism moved to
.engine/scripts/verify-flow-trigger-body-isolation.py as reusable PII-taint-tracking-over-
Power-Automate-expressions tooling -- see that file's docstring.

The three client-specific facts that stayed here:
  --trigger-column   rev_triggeredon (the column §6.3.1 says must never appear at all)
  --result-column    item/rev_resultjson (check B's sink)
  --exempt-template  config/round-statistics-exempt-templates.json -- ADR-039's one XPath
                     sum() exemption, a reviewed, one-off escape hatch, not a platform fact.

Run:
    python3 scripts/verify-flow-trigger-body-isolation.py \\
        src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json
    python3 scripts/verify-flow-trigger-body-isolation.py --selftest

Exits 0 when the named flow is clean, 1 on any violation or unreadable input, 2 on a usage
error. C-TECH-049, C-TECH-052, C-TECH-057.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-flow-trigger-body-isolation.py"

TRIGGER_COLUMN = "rev_triggeredon"
RESULT_COLUMN = "item/rev_resultjson"
EXEMPT_TEMPLATE_PATH = "config/round-statistics-exempt-templates.json"
DEFAULT_SOLUTION = "src/solutions/RevitaliseGrantAutomation"


def _load_engine():
    name = "_engine_verify_flow_trigger_body_isolation"
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

    if "--selftest" in argv:
        return engine.main(["verify-flow-trigger-body-isolation.py", "--selftest"])

    if "--solution" not in argv:
        argv = argv + ["--solution", DEFAULT_SOLUTION]
    if "--trigger-column" not in argv:
        argv = argv + ["--trigger-column", TRIGGER_COLUMN]
    if "--result-column" not in argv:
        argv = argv + ["--result-column", RESULT_COLUMN]
    if "--exempt-template" not in argv:
        argv = argv + ["--exempt-template", EXEMPT_TEMPLATE_PATH]

    return engine.main(["verify-flow-trigger-body-isolation.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
