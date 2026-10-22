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

REVISION 4 OF THE PORTAL TAD (trustee-portal-design-2 ADR-085 G2, SDD A-14, 2026-10-22). The
portal now SELECTS the three columns the trustee release profile grants (benefit status, benefit
provider, employment status). This wrapper reads that profile's name from
config/trustee-release-profile.json and passes it to the engine as `--released-profile <name>`;
the engine removes that profile's columns from the forbidden set ONLY if every permission in it
is read-only, and FAILS if the named profile is absent, empty, or grants update or create. With no
flag, the engine behaves exactly as before. The flag is an ENGINE change (.engine, improvement-
agent behind APPROVE IMPROVEMENTS); until the pinned engine supports it, this wrapper FAILS with
a message naming that, rather than running the old forbidden set and reporting the three columns
as a breach - or, worse, quietly not passing the flag. It never weakens the check.

Note: `--exclude-profile` was removed from this gate on 2026-08-23 (improvement review 19) --
passing it, or any third positional argument, is now a plain argparse usage error rather than
the old script's own explicit "flag removed" message.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "verify-code-app-column-bindings.py"
REQUIRED_COLUMNS_PATH = "config/trustee-portal-required-columns.json"
RELEASE_PROFILE_CONFIG = REPO_ROOT / "config" / "trustee-release-profile.json"
RELEASED_PROFILE_FLAG = "--released-profile"


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


def _release_profile_name() -> str | None:
    try:
        with open(RELEASE_PROFILE_CONFIG, encoding="utf-8") as handle:
            name = (json.load(handle) or {}).get("profile")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"no-secured-columns-in-code-app: FAILED — cannot read {RELEASE_PROFILE_CONFIG}: "
              f"{exc}", file=sys.stderr)
        return None
    if not isinstance(name, str) or not name.strip():
        print(f"no-secured-columns-in-code-app: FAILED — {RELEASE_PROFILE_CONFIG} names no "
              "'profile'.", file=sys.stderr)
        return None
    return name


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])

    if RELEASED_PROFILE_FLAG not in argv:
        name = _release_profile_name()
        if name is None:
            return 1
        # Fail closed BEFORE loading the engine when it cannot honour the flag: an argparse
        # "unrecognized arguments" exit 2 reads like a typo, not like the pending engine change.
        if RELEASED_PROFILE_FLAG not in ENGINE_SCRIPT.read_text(encoding="utf-8"):
            print("no-secured-columns-in-code-app: FAILED — the pinned engine "
                  f"({ENGINE_SCRIPT.relative_to(REPO_ROOT)}) does not support "
                  f"{RELEASED_PROFILE_FLAG}, so the release profile '{name}' cannot be "
                  "subtracted from the forbidden set. Expected until the engine change of portal "
                  "TAD ADR-085 G2 lands (improvement-agent, APPROVE IMPROVEMENTS) and the "
                  "submodule pointer is bumped. Not weakened: no column was let through.",
                  file=sys.stderr)
            return 1
        argv = argv + [RELEASED_PROFILE_FLAG, name]

    engine = _load_engine()
    if "--require-columns" not in argv:
        argv = argv + ["--require-columns", REQUIRED_COLUMNS_PATH]

    return engine.main(["verify-code-app-column-bindings.py", *argv])


if __name__ == "__main__":
    sys.exit(main())
