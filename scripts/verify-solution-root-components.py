#!/usr/bin/env python3
"""Verify that an unpacked Power Platform solution is internally consistent.

Every component declared in ``Other/Solution.xml`` under ``<RootComponents>`` must have a
definition file on disk, and every definition file on disk must be declared. Both directions
matter:

* A declared component with no definition makes ``pac solution pack`` fail late, with a
  generic error that does not name the component. This script names it in one second.
* A definition with no declaration packs successfully and then does not ship - the component
  silently never reaches the target environment, which is the harder failure to notice.

This exists because the solution source is hand-authored ahead of a live DEV environment, so
there is no round-trip through ``pac solution unpack`` to keep the manifest honest.

Run:
    python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation

Exits 0 when consistent, 1 otherwise. Wired into config/<slug>-build.yml as the
``root-components-resolve`` step.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

# Dataverse solution component type -> (human label, how to find its definitions on disk).
# Each collector returns the set of identifiers that Solution.xml would use for that type:
# a schema name for some types, a GUID for others.
COMPONENT_TYPES: dict[str, str] = {
    "1": "table",
    "9": "global option set",
    "10": "relationship",
    "20": "security role",
    "29": "cloud flow",
    "62": "sitemap",
    "70": "field security profile",
    "80": "model-driven app",
    "380": "environment variable definition",
    # 10371 (connection reference) is DELIBERATELY ABSENT - see Solution.xml's own comment,
    # added 2026-08-14. This Dataverse version's root-components resolver
    # (SolutionComponentTypeMap.RetrievePlatformName) throws "Invalid component type provided
    # 10371" on ANY RootComponent entry of this type, confirmed by a live `pac solution import`
    # failure, so Solution.xml no longer declares one. Connection references still ship - they
    # come entirely from Other/Customizations.xml's <connectionreferences> block - there is
    # just no root-component consistency check possible for this type in this version.
}


def _read_all(pattern: str, root: str) -> str:
    """Concatenate every file matching a glob, so one regex can sweep them all."""
    out = []
    for path in sorted(glob.glob(os.path.join(root, pattern), recursive=True)):
        with open(path, encoding="utf-8") as handle:
            out.append(handle.read())
    return "\n".join(out)


def _dir_names(pattern: str, root: str) -> set[str]:
    """Folder names for component types stored one-folder-per-component."""
    return {
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(root, pattern), recursive=True)
    }


def collect_on_disk(root: str) -> dict[str, set[str]]:
    """Where each component type's definition lives, and which identifier declares it.

    Both the paths and the identifier FORM below are dictated by SolutionPackagerLib, not
    chosen: they were read out of the decompiled processors and then confirmed against a real
    `pac solution pack` for both package types (Dev Summary revision 0.5). Two of them are
    counter-intuitive and were previously wrong here:

    * type 62 (app sitemap) and type 80 (model-driven app) are declared BY NAME, never by GUID.
      AppModuleProcessor and AppModuleSitemapProcessor do not populate Component.Id, so
      RootComponentsValidation can only ever build a name-based key for them. Matching on
      <sitemapid>/<appmoduleid> here would re-introduce the exact mismatch that made the pack
      fail. The app sitemap also lives in its own top-level AppModuleSiteMaps/ folder, not
      beside AppModule.xml.
    * type 20 (security role) is keyed on the ``id`` ATTRIBUTE of <Role>, not a <RoleId> child.
    """
    return {
        "1": _dir_names("Entities/*/Entity.xml", root),
        "9": {
            os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(root, "OptionSets/*.xml"))
        },
        # Detail files are grouped by ReferencedEntityName; Other/Relationships.xml is the index.
        "10": set(
            re.findall(r'<EntityRelationship Name="([^"]+)"', _read_all("Other/Relationships/*.xml", root))
        ),
        "20": set(re.findall(r'<Role\s+id="([^"]+)"', _read_all("Roles/*/*.xml", root))),
        "29": set(re.findall(r'WorkflowId="([^"]+)"', _read_all("Workflows/**/*.data.xml", root))),
        "62": set(
            re.findall(
                r"<SiteMapUniqueName>([^<]+)</SiteMapUniqueName>",
                _read_all("AppModuleSiteMaps/*/AppModuleSiteMap.xml", root),
            )
        ),
        "70": set(
            re.findall(
                r'<FieldSecurityProfile[^>]*\sfieldsecurityprofileid="([^"]+)"',
                _read_all("Other/FieldSecurityProfiles.xml", root),
            )
        ),
        "80": set(
            # PascalCase <UniqueName> (not <uniquename>) since 2026-08-14: fixed to match the
            # real Dataverse element casing, confirmed via a real model-driven app the user
            # built in DEV, exported and unpacked - the original lowercase shape was a
            # fabricated guess that a live `pac solution import` rejected outright with a
            # generic NullReferenceException. See AppModule.xml's own header for the full story.
            re.findall(r"<UniqueName>([^<]+)</UniqueName>", _read_all("AppModules/*/AppModule.xml", root))
        ),
        # Folder is environmentvariabledefinitions/<schemaname>/environmentvariabledefinition.xml
        # (lowercase, one folder per variable), not the flat EnvironmentVariables/<name>.xml this
        # checked before 2026-08-14. That flat layout matched a decompiled-source claim about
        # which folder EnvVariablesProcessor reads, but it described an older `pac` CLI version:
        # against pac CLI 2.4.1 it packed with no error and no warning specific to this
        # component, then silently failed to ship as a real component at all, only surfacing
        # when a live import reached a Workflow bound to one of these variables ("Failed to find
        # environment variables with schema name(s)..."). See any environmentvariabledefinition.xml
        # file's own header for the full story.
        "380": _dir_names("environmentvariabledefinitions/*/environmentvariabledefinition.xml", root),
        # No "10371" entry - see the COMPONENT_TYPES comment above. Connection references have
        # no RootComponent declaration to check on-disk definitions against in this version.
    }


_USAGE = "<solution-root> [--emit-json]"
_EXAMPLE = "src/solutions/RevitaliseGrantAutomation"


def emit_live_check_targets(root: str) -> dict:
    """The SINGLE list of what a live environment must contain, derived from source.

    Added for `provisioning/dataverse/verify-solution-components.ps1` (IMP-0013's own
    remediation: the first DEV deploy was called "verified" against a hand-typed type list
    that silently omitted systemform/savedquery). This function is that list's ONLY producer —
    the PowerShell script consumes exactly this JSON rather than re-deriving its own, so the
    two can never silently diverge (the failure class this whole step exists to prevent).

    Two parts, because they are declared two different ways in this solution:

    1. ``declared`` — every <RootComponent> in Solution.xml, CASE-PRESERVED (unlike the PASS/
       FAIL path above, which lowercases for set-comparison only). Case matters here: type 380
       schemaNames are genuinely mixed-case (e.g. "rev_ProcessOwnerUpn" - see Solution.xml
       itself) and a live alternate-key lookup by schemaname is case-sensitive.
    2. ``subcomponents`` — systemform and savedquery are NEVER declared as their own
       <RootComponent> in this solution: every type "1" entity ships with behavior="0"
       ("Include Subcomponents"), so its forms and views ride in as subcomponents of the
       entity instead. Derived here directly from each entity folder's FormXml/*/*.xml
       (filename, minus braces, is the live formid) and SavedQueries/*.xml (the
       <savedqueryid> each file declares) - the same on-disk truth `collect_on_disk` reads
       for type "1", never a hand-typed name.

       ASSUMPTION (flagged, not silently taken) - A-VSC-2, wbs:6.8, Dev Summary section 10:
       every entity folder under Entities/ is currently declared behavior="0" (verified
       against Solution.xml at the time this was written - every type "1" RootComponent line
       carries behavior="0"). If a future entity ever ships behavior="1" (Do Not Include
       Subcomponents), this would over-check rather than under-check for it - the safe
       direction of error, but still a guess about a future state.
    """
    manifest_path = os.path.join(root, "Other", "Solution.xml")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = handle.read()

    declared: dict[str, list[dict[str, str]]] = {}
    for ctype, schema, cid in re.findall(
        r'<RootComponent type="(\d+)"(?:\s+schemaName="([^"]*)")?(?:\s+id="([^"]*)")?', manifest
    ):
        label = COMPONENT_TYPES.get(ctype, f"unknown type {ctype}")
        if schema:
            identifier, kind = schema, "schema"
        else:
            identifier, kind = cid.strip("{}"), "id"
        declared.setdefault(ctype, {"label": label, "kind": kind, "identifiers": []})
        declared[ctype]["identifiers"].append(identifier)

    systemform_ids: set[str] = set()
    savedquery_ids: set[str] = set()
    for path in glob.glob(os.path.join(root, "Entities", "*", "FormXml", "*", "*.xml")):
        systemform_ids.add(os.path.splitext(os.path.basename(path))[0].strip("{}"))
    for path in glob.glob(os.path.join(root, "Entities", "*", "SavedQueries", "*.xml")):
        with open(path, encoding="utf-8") as handle:
            match = re.search(r"<savedqueryid>([^<]+)</savedqueryid>", handle.read())
        if match:
            savedquery_ids.add(match.group(1).strip("{}"))

    return {
        "declared": declared,
        "subcomponents": {
            "systemform": sorted(systemform_ids),
            "savedquery": sorted(savedquery_ids),
        },
    }


def _usage_error(got: int) -> int:
    """Print the SIGNATURE, not the whole module docstring (IMP-0470).

    A usage error answered with the entire docstring and exit 2 reads like a real finding rather
    than a mistyped command. The wbs:6.9 dispatch quoted a one-argument invocation of the
    two-argument `verify-code-app-column-bindings.py`; it printed 98 lines of prose and cost a
    re-check to establish that nothing was actually wrong. Exit code is unchanged at 2 — only the
    output is, so every caller that keys on the code behaves identically.
    """
    name = os.path.basename(__file__)
    print(f"{name}: USAGE ERROR — expected 1 argument(s), got {got}.", file=sys.stderr)
    print(f"  usage:   python3 scripts/{name} {_USAGE}", file=sys.stderr)
    print(f"  example: python3 scripts/{name} {_EXAMPLE}", file=sys.stderr)
    print("  This is a usage error, NOT a finding. The rationale is this file's module docstring.",
          file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[2] != "--emit-json"):
        return _usage_error(len(argv) - 1)
    root = argv[1].rstrip("/")
    emit_json = len(argv) == 3

    if emit_json:
        # Pure query mode for a consumer script (verify-solution-components.ps1) - no
        # PASS/FAIL side effect, no exit-code meaning beyond "the JSON was produced".
        print(json.dumps(emit_live_check_targets(root), indent=2))
        return 0

    manifest_path = os.path.join(root, "Other", "Solution.xml")
    customizations_path = os.path.join(root, "Other", "Customizations.xml")

    for required in (manifest_path, customizations_path):
        if not os.path.isfile(required):
            print(f"FAIL - {required} is missing. `pac solution pack` requires both "
                  f"Other/Solution.xml and Other/Customizations.xml.")
            return 1

    with open(manifest_path, encoding="utf-8") as handle:
        manifest = handle.read()

    declared: dict[str, set[str]] = {}
    for ctype, schema, cid in re.findall(
        r'<RootComponent type="(\d+)"(?:\s+schemaName="([^"]*)")?(?:\s+id="([^"]*)")?', manifest
    ):
        declared.setdefault(ctype, set()).add((schema or cid or "").lower())

    on_disk_raw = collect_on_disk(root)
    on_disk = {k: {v.lower() for v in vs} for k, vs in on_disk_raw.items()}

    problems: list[str] = []
    total_declared = 0

    for ctype, keys in sorted(declared.items(), key=lambda kv: int(kv[0])):
        label = COMPONENT_TYPES.get(ctype)
        total_declared += len(keys)
        if label is None:
            problems.append(
                f"  type {ctype}: declared in Solution.xml but this script does not know where "
                f"that component type is stored. Add it to COMPONENT_TYPES."
            )
            continue
        for key in sorted(keys):
            if key not in on_disk.get(ctype, set()):
                problems.append(f"  MISSING DEFINITION - type {ctype} ({label}): {key}")

    for ctype, keys in sorted(on_disk.items(), key=lambda kv: int(kv[0])):
        label = COMPONENT_TYPES[ctype]
        for key in sorted(keys):
            if key not in declared.get(ctype, set()):
                problems.append(
                    f"  NOT DECLARED - type {ctype} ({label}): {key} exists on disk but is absent "
                    f"from <RootComponents>, so it will not ship."
                )

    if problems:
        print(f"FAIL - solution manifest and source do not agree ({len(problems)} problem(s)):")
        print("\n".join(problems))
        return 1

    print(
        f"PASS - {total_declared} root components declared in Solution.xml, "
        f"every one has a definition on disk, and nothing on disk is undeclared."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
