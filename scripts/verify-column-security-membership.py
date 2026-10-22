#!/usr/bin/env python3
"""Verify no team holding a trustee-facing role is a MEMBER of a column security profile.

WHY THIS EXISTS. On 2026-08-21 a dispatch instruction told an agent to "bind REV Trustee to
the existing REV_TrusteeRestricted field security profile." That is backwards, and it is the
most dangerous single mistake available in this solution.

A field security profile's membership list is who it GRANTS the secured columns TO — not who
it withholds them from. REV_TrusteeRestricted releases 51 Tier 4 columns including
`rev_application.rev_narrativeraw`, which is Article 9 special-category data. The profile's
own description says so:

    "Every persona that is not a member of this profile - including every trustee -
     receives no value for these columns from any surface: app, view, export or API."
    -- src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml

NON-MEMBERSHIP IS THE CONTROL. Adding the trustee team to that list would have been a live
special-category disclosure — exactly what FR-036, NFR-003 and ADR-002 exist to prevent. The
agent caught it and refused before anything was written (IMP-0153, severity `blocker`, class
`platform-contract-guessed-not-groundtruthed`), so nothing was exposed. But it was caught by a
person reading carefully, and nothing in this repository would have caught it otherwise:

  * `FieldSecurityProfiles.xml` carries only FieldPermissions. It has no membership at all,
    so no gate over solution source can see this.
  * Membership is per-environment state applied by
    `provisioning/dataverse/ensure-column-security-profile-members.ps1` from
    `provisioning/deploymentSettings/<env>-settings.json`.
  * `verify-field-security-coverage.py` checks which COLUMNS are secured. It never reads
    `memberTeams`.

So the one place the mistake would actually be made had no gate on it. This is that gate.

WHAT IT CHECKS, AND WHY IT DERIVES RATHER THAN TRANSCRIBES. The naive check is "assert
memberTeams == ['REV Admins', 'REV Service Accounts']". That is a transcription, and
C-TECH-060's lesson is that transcribed values drift from the thing they claim to assert. So
the invariant is derived from the settings file itself:

  1. Read `dataverse.groupTeams[]` and collect every team whose `securityRoles` include a
     role this project treats as trustee-facing (see TRUSTEE_ROLE_PATTERN).
  2. Read `dataverse.columnSecurityProfiles[]` and FAIL if any such team appears in any
     profile's `memberTeams`.

The rule therefore keeps working when roles, teams or profiles are renamed or added, and it
generalises to any future persona that must be kept out by non-membership.

It also fails CLOSED in three ways, because a gate that cannot fail is worse than no gate
(C-TECH-057):

  * no settings file found, or none declaring `columnSecurityProfiles`  -> FAILED, not PASS
  * a profile declaring `columnSecurityProfiles` with no `groupTeams` to resolve against
    -> FAILED (the assertion is unevaluable, which is not the same as satisfied)
  * a profile whose `memberTeams` is missing or empty -> FAILED (a profile with no members
    makes its columns unreadable by anyone, including the process owner)

REVISION 4 OF THE PORTAL TAD (ADR-084/ADR-085 G1, SDD A-14, 2026-10-22) - ONE POSITIVE CASE.
Trustees now read three secured answers through a profile that releases only those, read only.
So a trustee-role team MAY be a member of exactly one profile, and only while all of this holds:

  * the profile is the one `config/trustee-release-profile.json` names (no literal here);
  * in FieldSecurityProfiles.xml every one of its permissions is CanRead=4, CanUpdate=0,
    CanCreate=0, and it holds at least one;
  * its (entity, column) set EQUALS the special-category register's rows carrying a
    `trustee_release` block - so widening it takes a register edit too (two keys);
  * its only members are trustee-role teams ("Its only member is the trustee group team").

Anything else FAILS as before; a trustee team in REV_TrusteeRestricted still fails with the
original message. And COMPLETENESS: every settings file that declares a trustee-role team must
declare the release profile with every such team as a member (otherwise F1-F3 render "Not
recorded" for every trustee - a blackout that looks like an unanswered question, R-D2-15); a file
that declares no trustee-role team (DEV) must declare no entry for it.

Each failure says which rule failed.

Run:
    python3 scripts/verify-column-security-membership.py provisioning/deploymentSettings \
        --profiles src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml \
        --register constraints/domain/special-category-register.yml \
        [--release-config config/trustee-release-profile.json]

Exits 0 when the invariant holds, 1 otherwise, 2 on a usage error. Wired into
config/<slug>-build.yml as the `no-trustee-in-column-security-profile` step.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import yaml  # PyYAML; the register is YAML
except ImportError:  # pragma: no cover - fail closed below
    yaml = None

# A role name matching this is a persona whose access to secured columns must be prevented by
# NON-MEMBERSHIP. Kept as a pattern rather than a fixed list so a second trustee-like persona
# (an external panel member, an auditor) is covered on the day it is added rather than on the
# day someone remembers this file.
TRUSTEE_ROLE_PATTERN = re.compile(r"trustee|panel|observer", re.IGNORECASE)


def load_settings(root: str) -> list[tuple[str, dict]]:
    paths = sorted(glob.glob(os.path.join(root, "*-settings.json")))
    out: list[tuple[str, dict]] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            try:
                out.append((os.path.relpath(path), json.load(handle)))
            except json.JSONDecodeError as exc:
                print(f"ERROR: {os.path.relpath(path)}: not valid JSON — {exc}", file=sys.stderr)
    return out


def parse_args(argv: list[str]) -> dict | None:
    """Positional settings dir, required --profiles/--register, optional --release-config."""
    out: dict = {"release_config": _DEFAULT_RELEASE_CONFIG}
    positional: list[str] = []
    flags = {"--profiles": "profiles", "--register": "register", "--release-config": "release_config"}
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in flags:
            if i + 1 >= len(argv):
                return None
            out[flags[arg]] = argv[i + 1]
            i += 2
            continue
        if arg.startswith("--"):
            return None
        positional.append(arg)
        i += 1
    if len(positional) != 1 or "profiles" not in out or "register" not in out:
        return None
    out["root"] = positional[0].rstrip("/")
    return out


def load_release_profile_name(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        name = (json.load(handle) or {}).get("profile")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{path} has no non-empty 'profile' value")
    return name


def load_profile_permissions(path: str) -> dict[str, list[tuple[str, str, int, int, int]]]:
    """name -> [(entity, column, canread, canupdate, cancreate)] from FieldSecurityProfiles.xml."""
    root = ET.parse(path).getroot()
    profiles: dict[str, list[tuple[str, str, int, int, int]]] = {}
    for fsp in root.iter("FieldSecurityProfile"):
        perms = []
        for perm in fsp.iter("FieldPermission"):
            def num(tag: str) -> int:
                text = (perm.findtext(tag) or "").strip()
                return int(text) if text.lstrip("-").isdigit() else -1
            perms.append(((perm.findtext("EntityName") or "").strip(),
                          (perm.findtext("AttributeName") or "").strip(),
                          num("CanRead"), num("CanUpdate"), num("CanCreate")))
        profiles[str(fsp.get("name"))] = perms
    return profiles


def load_register_releases(path: str) -> set[tuple[str, str]]:
    """Every (entity, column) the special-category register marks with a trustee_release block."""
    if yaml is None:
        raise ValueError("PyYAML is not installed, so the register cannot be read")
    with open(path, encoding="utf-8") as handle:
        doc = yaml.safe_load(handle) or {}
    rows = doc.get("columns") if isinstance(doc, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f"{path} has no top-level 'columns' list")
    released: set[tuple[str, str]] = set()
    for row in rows:
        if isinstance(row, dict) and row.get("trustee_release"):
            released.add((str(row.get("entity")), str(row.get("name"))))
    return released


def release_profile_problems(name: str, profiles: dict, released: set[tuple[str, str]]) -> list[str]:
    """Why the named release profile may NOT have trustee members; empty when it may."""
    if name not in profiles:
        return [f"the release profile '{name}' named by the release config is not declared in "
                "FieldSecurityProfiles.xml"]
    perms = profiles[name]
    problems: list[str] = []
    if not perms:
        problems.append(f"the release profile '{name}' grants no permission at all")
    for entity, column, can_read, can_update, can_create in perms:
        if (can_read, can_update, can_create) != (4, 0, 0):
            problems.append(
                f"the release profile '{name}' grants {entity}.{column} CanRead={can_read}, "
                f"CanUpdate={can_update}, CanCreate={can_create}; a trustee release must be read "
                "only (4/0/0)")
    granted = {(e, c) for e, c, *_ in perms}
    if granted != released:
        extra = sorted(f"{e}.{c}" for e, c in granted - released)
        missing = sorted(f"{e}.{c}" for e, c in released - granted)
        problems.append(
            f"the release profile '{name}' does not grant exactly the register's trustee_release "
            f"columns: granted but not released by the register {extra or 'none'}; released by "
            f"the register but not granted {missing or 'none'}")
    return problems


_USAGE = ("<deployment-settings-dir> --profiles <FieldSecurityProfiles.xml> --register <special-category-register.yml> "
          "[--release-config <trustee-release-profile.json>]")
_EXAMPLE = ("provisioning/deploymentSettings --profiles src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml "
            "--register constraints/domain/special-category-register.yml")
_DEFAULT_RELEASE_CONFIG = "config/trustee-release-profile.json"


def _usage_error(got: int) -> int:
    """Print the SIGNATURE, not the whole module docstring (IMP-0470).

    A usage error answered with the entire docstring and exit 2 reads like a real finding rather
    than a mistyped command. The wbs:6.9 dispatch quoted a one-argument invocation of the
    two-argument `verify-code-app-column-bindings.py`; it printed 98 lines of prose and cost a
    re-check to establish that nothing was actually wrong. Exit code is unchanged at 2 — only the
    output is, so every caller that keys on the code behaves identically.
    """
    name = os.path.basename(__file__)
    print(f"{name}: USAGE ERROR — expected 1 positional argument plus --profiles and --register; {got}.", file=sys.stderr)
    print(f"  usage:   python3 scripts/{name} {_USAGE}", file=sys.stderr)
    print(f"  example: python3 scripts/{name} {_EXAMPLE}", file=sys.stderr)
    print("  This is a usage error, NOT a finding. The rationale is this file's module docstring.",
          file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args is None:
        return _usage_error(len(argv) - 1)
    root = args["root"]
    if not os.path.isdir(root):
        print(f"no-trustee-in-column-security-profile: FAILED — {root} is not a directory. "
              "A gate pointed at a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    # The release profile, its permissions and the register's release rows. Any of them
    # unreadable FAILS: an unevaluable positive case is not a permitted one.
    try:
        release_name = load_release_profile_name(args["release_config"])
        profiles = load_profile_permissions(args["profiles"])
        released = load_register_releases(args["register"])
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"no-trustee-in-column-security-profile: FAILED — could not read the release "
              f"profile's inputs: {exc}", file=sys.stderr)
        return 1
    release_problems = release_profile_problems(release_name, profiles, released)

    settings = load_settings(root)
    if not settings:
        print(f"no-trustee-in-column-security-profile: FAILED — no *-settings.json under "
              f"{root}. Nothing was scanned, so this is not a pass.", file=sys.stderr)
        return 1

    errors: list[str] = []
    profiles_checked = 0
    files_with_profiles = 0
    release_memberships = 0

    for rel, doc in settings:
        dataverse = doc.get("dataverse") or {}
        declared = dataverse.get("columnSecurityProfiles")
        group_teams = dataverse.get("groupTeams") or []

        trustee_teams: dict[str, str] = {}
        for team in group_teams:
            name = team.get("name")
            for role in team.get("securityRoles") or []:
                if TRUSTEE_ROLE_PATTERN.search(role or ""):
                    trustee_teams[str(name)] = role

        if not declared:
            # A settings file need not declare profiles (a DEV-only file may not). Only the
            # complete absence across every file is a failure, handled after the loop. But a file
            # that declares a trustee team and no release profile leaves trustees blind (R-D2-15).
            if trustee_teams:
                errors.append(
                    f"{rel}: [completeness] declares trustee-role team(s) {sorted(trustee_teams)} "
                    f"but no columnSecurityProfiles, so the release profile '{release_name}' has "
                    "no members here and every trustee sees 'Not recorded' for the released "
                    "answers.")
            continue
        files_with_profiles += 1

        if not group_teams:
            errors.append(
                f"{rel}: declares columnSecurityProfiles but no groupTeams, so membership "
                "cannot be resolved to a role. Unevaluable is not satisfied — declare the "
                "teams or remove the profiles.")
            continue

        release_entry = None
        for profile in declared:
            profiles_checked += 1
            pname = profile.get("name", "<unnamed>")
            members = profile.get("memberTeams")
            if pname == release_name:
                release_entry = profile
            if not members:
                errors.append(
                    f"{rel}: profile '{pname}' has no memberTeams. A profile with no members "
                    "releases its secured columns to nobody — including the process owner — "
                    "which is a different defect from the one this gate exists for, and is "
                    "still a defect.")
                continue
            for member in members:
                is_trustee = str(member) in trustee_teams
                if pname == release_name:
                    if not is_trustee:
                        errors.append(
                            f"{rel}: [release-membership] profile '{pname}' lists member team "
                            f"'{member}', which holds no trustee-facing role. The release "
                            "profile's only member is the trustee group team (ADR-084).")
                        continue
                    if release_problems:
                        for problem in release_problems:
                            errors.append(
                                f"{rel}: [release-profile] profile '{pname}' lists trustee "
                                f"team '{member}', but {problem}. A trustee team is permitted "
                                "in this profile only while it is read only and equals the "
                                "register's trustee_release rows (ADR-085 G1).")
                    else:
                        release_memberships += 1
                    continue
                if is_trustee:
                    role = trustee_teams[str(member)]
                    errors.append(
                        f"{rel}: profile '{pname}' lists member team '{member}', which holds "
                        f"the '{role}' role. A profile's membership GRANTS its secured columns; "
                        "for a trustee persona the control IS non-membership. This would "
                        "release Article 9 special-category data (rev_narrativeraw) to a "
                        "trustee. See IMP-0153 and ADR-002.")
                elif TRUSTEE_ROLE_PATTERN.search(str(member)):
                    errors.append(
                        f"{rel}: profile '{pname}' lists member team '{member}', whose NAME "
                        "reads as a trustee persona even though no declared groupTeam of that "
                        "name holds a trustee role. Either the team is undeclared or the name "
                        "is misleading; both need resolving before this can pass.")

        # COMPLETENESS (ADR-085 G1): trustee teams here <=> the release profile, with all of them.
        if trustee_teams:
            listed = {str(m) for m in (release_entry or {}).get("memberTeams") or []}
            missing = sorted(set(trustee_teams) - listed)
            if release_entry is None:
                errors.append(
                    f"{rel}: [completeness] declares trustee-role team(s) {sorted(trustee_teams)} "
                    f"but no '{release_name}' entry, so trustees would see 'Not recorded' for "
                    "every released answer (R-D2-15).")
            elif missing:
                errors.append(
                    f"{rel}: [completeness] '{release_name}' omits trustee-role team(s) "
                    f"{missing}; every trustee team must be a member.")
        elif release_entry is not None:
            errors.append(
                f"{rel}: [completeness] declares '{release_name}' but no trustee-role team, so "
                "the entry can name no valid member. A file with no trustee team (DEV) declares "
                "no entry for the release profile.")

    if not files_with_profiles:
        print("no-trustee-in-column-security-profile: FAILED — no settings file declares "
              "dataverse.columnSecurityProfiles. This solution ships a column security "
              "profile, so its membership must be provisioned somewhere; a gate that finds "
              "nothing to check is not a gate that passed.", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nno-trustee-in-column-security-profile: FAILED — {len(errors)} finding(s) "
              f"across {profiles_checked} profile(s).", file=sys.stderr)
        return 1

    print(f"no-trustee-in-column-security-profile: OK — {profiles_checked} profile "
          f"membership list(s) across {files_with_profiles} settings file(s); no team holding "
          "a trustee-facing role is a member of any column security profile except "
          f"'{release_name}' ({release_memberships} membership(s)), which is read only and "
          f"equals the register's {len(released)} trustee_release column(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
