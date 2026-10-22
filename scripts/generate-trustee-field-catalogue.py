#!/usr/bin/env python3
"""Instance wrapper for the engine's generic generate-restricted-field-catalogue.py (Phase 3f).

Generates the trustee portal's restricted-field catalogue (ADR-032, FR-078, TAD §3.2.3). The
derivation mechanism (validate a manifest against the live field security profile and entity
schema, fail loudly on drift, render deterministic TypeScript with no logical column name in
the output) moved to .engine/scripts/generate-restricted-field-catalogue.py as the general
ADR-032 pattern -- see that file's docstring for why a hand-typed catalogue is unsafe.

The one client-specific fact that stayed here is WHICH eleven (entity, column) pairs belong on
this screen and which SDD §7.1b board-pack group each is in --
config/trustee-restricted-field-catalogue.json. That manifest cannot be read off any XML file;
it is a requirements decision, cited to SDD Amendment A-05 Finding 1.

G4 (portal TAD trustee-portal-design-2 Revision 4, ADR-085, 2026-10-22). A manifest field whose
column the trustee RELEASE profile grants (config/trustee-release-profile.json) FAILS: a field
cannot be both shown and "restricted". The three A-14 columns left the manifest for that reason;
the generator logic is otherwise unchanged. Checked before the engine runs, on every mode.

Usage (unchanged from before the split)
-----
    python3 scripts/generate-trustee-field-catalogue.py
    python3 scripts/generate-trustee-field-catalogue.py --check

--check   Regenerate in memory and diff against the committed --out file; exit 1 if the
          committed file is stale, missing, or the manifest no longer matches ground truth.
          Wired into config/revitalise-grant-automation-build.yml as the
          `trustee-field-catalogue` step, BEFORE `no-secured-columns-in-code-app` and before
          typecheck/build (the app imports the generated file).

Exits 0 clean · 1 on any drift or validation failure · 2 on a usage error.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_SCRIPT = REPO_ROOT / ".engine" / "scripts" / "generate-restricted-field-catalogue.py"

MANIFEST_PATH = "config/trustee-restricted-field-catalogue.json"
DEFAULT_PROFILE = "src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml"
DEFAULT_ENTITIES = "src/solutions/RevitaliseGrantAutomation/Entities"
# EVERY code-app copy. There is one since 2026-10-22: the list-layout app was retired and the card
# app took its folder name (TAD trustee-portal-design-2 §9.4). Keep the tuple: if a second app ever
# returns, a single output would leave the second copy stale while --check passed (IMP-1047).
DEFAULT_OUTS = (
    "src/code-apps/trustee-review-portal/src/generated/trusteeRestrictedFieldCatalogue.ts",
)
DEFAULT_OUT = DEFAULT_OUTS[0]  # kept for importers of the old name
RELEASE_PROFILE_CONFIG = "config/trustee-release-profile.json"


def _flag_value(argv: list[str], flag: str, default: str) -> str:
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def check_no_released_field(manifest_path: str, profile_path: str,
                            release_config: str = RELEASE_PROFILE_CONFIG) -> list[str]:
    """G4: problems when a manifest field's column is granted by the trustee release profile."""
    try:
        with open(REPO_ROOT / release_config, encoding="utf-8") as handle:
            name = (json.load(handle) or {}).get("profile")
        with open(REPO_ROOT / manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)
        root = ET.parse(REPO_ROOT / profile_path).getroot()
    except (OSError, json.JSONDecodeError, ET.ParseError) as exc:
        return [f"G4 could not read its inputs: {exc}"]
    if not isinstance(name, str) or not name.strip():
        return [f"G4: {release_config} names no 'profile'"]
    matches = [p for p in root.iter("FieldSecurityProfile") if p.get("name") == name]
    if len(matches) != 1:
        return [f"G4: the release profile '{name}' is declared {len(matches)} time(s) in "
                f"{profile_path}; expected exactly once"]
    released = {((perm.findtext("EntityName") or "").strip(),
                 (perm.findtext("AttributeName") or "").strip())
                for perm in matches[0].iter("FieldPermission")}
    entity = manifest.get("entity")
    problems = []
    for field in manifest.get("fields") or []:
        key, column = field[0], field[1]
        if (entity, column) in released:
            problems.append(
                f"G4: manifest field '{key}' is the column {entity}.{column}, which the trustee "
                f"release profile '{name}' grants. A field cannot be both shown and restricted: "
                f"remove it from {manifest_path} (ADR-085).")
    return problems


def _load_engine():
    name = "_engine_generate_restricted_field_catalogue"
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
        rc = engine.main(["generate-restricted-field-catalogue.py", "--selftest"])
        return rc or _selftest_g4() or _selftest_all_outputs_checked()

    g4 = check_no_released_field(_flag_value(argv, "--manifest", MANIFEST_PATH),
                                 _flag_value(argv, "--profile", DEFAULT_PROFILE))
    if g4:
        for problem in g4:
            print(f"ERROR: {problem}", file=sys.stderr)
        print("trustee-field-catalogue: FAILED (G4)", file=sys.stderr)
        return 1

    defaults = {
        "--manifest": MANIFEST_PATH,
        "--profile": DEFAULT_PROFILE,
        "--entities": DEFAULT_ENTITIES,
    }
    for flag, value in defaults.items():
        if flag not in argv:
            argv = argv + [flag, value]

    # An explicit --out targets exactly that file; otherwise every app copy is written/checked.
    outs = [DEFAULT_OUTS[i] for i in range(len(DEFAULT_OUTS))] if "--out" not in argv else [None]
    rc = 0
    for out in outs:
        call = argv if out is None else argv + ["--out", out]
        rc = max(rc, engine.main(["generate-restricted-field-catalogue.py", *call]))
    return rc


def _selftest_g4() -> int:
    """G4 must fail a manifest field whose column the release profile grants, and pass the real one."""
    import tempfile

    if check_no_released_field(MANIFEST_PATH, DEFAULT_PROFILE):
        print("SELFTEST FAIL: G4 rejects the committed manifest")
        return 1
    with open(REPO_ROOT / RELEASE_PROFILE_CONFIG, encoding="utf-8") as handle:
        name = json.load(handle)["profile"]
    root = ET.parse(REPO_ROOT / DEFAULT_PROFILE).getroot()
    released = [p for p in root.iter("FieldSecurityProfile") if p.get("name") == name]
    if len(released) != 1:
        print(f"SELFTEST FAIL: release profile {name} not declared exactly once")
        return 1
    perm = next(iter(released[0].iter("FieldPermission")), None)
    if perm is None:
        print(f"SELFTEST FAIL: release profile {name} grants nothing to test against")
        return 1
    with open(REPO_ROOT / MANIFEST_PATH, encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["fields"] = list(manifest["fields"]) + [
        ["selftest-released", (perm.findtext("AttributeName") or "").strip(), manifest["group_order"][0]]
    ]
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "manifest.json"
        bad.write_text(json.dumps(manifest), encoding="utf-8")
        if not check_no_released_field(str(bad), DEFAULT_PROFILE):
            print("SELFTEST FAIL: G4 passed a manifest naming a released column")
            return 1
    print("SELFTEST OK: G4 fails a released column in the manifest")
    return 0


def _selftest_all_outputs_checked() -> int:
    """A stale copy (the last in DEFAULT_OUTS) must fail --check (IMP-1047)."""
    second = REPO_ROOT / DEFAULT_OUTS[-1]
    if not second.exists():
        print(f"SELFTEST FAIL: {DEFAULT_OUTS[-1]} missing")
        return 1
    original = second.read_bytes()
    try:
        second.write_bytes(original + b"// stale\n")
        if main(["--check"]) == 0:
            print("SELFTEST FAIL: --check passed with a stale app copy")
            return 1
    finally:
        second.write_bytes(original)
    if main(["--check"]) != 0:
        print("SELFTEST FAIL: --check failed on restored copies")
        return 1
    print("SELFTEST OK: stale copy fails --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
