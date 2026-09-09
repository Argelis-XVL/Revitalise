#!/usr/bin/env python3
"""Instance wrapper for the engine's generic verify-code-app-column-bindings.py (Phase 3f).

The forbidden-column derivation mechanism (read FieldSecurityProfiles.xml, scope to the app's
own tables, whole-identifier scan, generated-dir exclusion) moved to
.engine/scripts/verify-code-app-column-bindings.py as Power Platform Code App knowledge. See
that file's docstring for the full C-TECH-069 rescoping history (IMP-0234/0236/0237/0240).

The one client-specific fact that stayed here is the trustee portal's own fail-closed
visibility conjunction (TAD §5.5) -- the three columns
(rev_narrativeredacted, rev_redactionreleased, rev_eligibleforround) that must appear in
authored source for the app to implement the control at all --
config/trustee-portal-required-columns.json.

USAGE (unchanged from before the split):
    python3 scripts/verify-code-app-column-bindings.py \\
        src/code-apps/trustee-review-portal \\
        src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml

Exits 0 when the app references no secured column and implements the conjunction, 1 otherwise.
Wired into config/revitalise-grant-automation-build.yml as the
`no-secured-columns-in-code-app` step.

Note: `--exclude-profile` was removed from this gate on 2026-08-23 (improvement review 19) --
passing it, or any third positional argument, is now a plain argparse usage error rather than
the old script's own explicit "flag removed" message.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-code-app-column-bindings.py"
REQUIRED_COLUMNS_PATH = "config/trustee-portal-required-columns.json"


def _load_engine():
    name = "_engine_verify_code_app_column_bindings"
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

    if "--require-columns" not in argv:
        argv = argv + ["--require-columns", REQUIRED_COLUMNS_PATH]

    return engine.main(["verify-code-app-column-bindings.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
