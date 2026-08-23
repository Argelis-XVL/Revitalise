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

Run:
    python3 scripts/verify-column-security-membership.py provisioning/deploymentSettings

Exits 0 when the invariant holds, 1 otherwise. Wired into config/<slug>-build.yml as the
`no-trustee-in-column-security-profile` step.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")
    if not os.path.isdir(root):
        print(f"no-trustee-in-column-security-profile: FAILED — {root} is not a directory. "
              "A gate pointed at a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    settings = load_settings(root)
    if not settings:
        print(f"no-trustee-in-column-security-profile: FAILED — no *-settings.json under "
              f"{root}. Nothing was scanned, so this is not a pass.", file=sys.stderr)
        return 1

    errors: list[str] = []
    profiles_checked = 0
    files_with_profiles = 0

    for rel, doc in settings:
        dataverse = doc.get("dataverse") or {}
        profiles = dataverse.get("columnSecurityProfiles")
        if not profiles:
            # A settings file need not declare profiles (a DEV-only file may not). Only the
            # complete absence across every file is a failure, handled after the loop.
            continue
        files_with_profiles += 1

        group_teams = dataverse.get("groupTeams")
        if not group_teams:
            errors.append(
                f"{rel}: declares columnSecurityProfiles but no groupTeams, so membership "
                "cannot be resolved to a role. Unevaluable is not satisfied — declare the "
                "teams or remove the profiles.")
            continue

        trustee_teams: dict[str, str] = {}
        for team in group_teams:
            name = team.get("name")
            for role in team.get("securityRoles") or []:
                if TRUSTEE_ROLE_PATTERN.search(role or ""):
                    trustee_teams[str(name)] = role

        for profile in profiles:
            profiles_checked += 1
            pname = profile.get("name", "<unnamed>")
            members = profile.get("memberTeams")
            if not members:
                errors.append(
                    f"{rel}: profile '{pname}' has no memberTeams. A profile with no members "
                    "releases its secured columns to nobody — including the process owner — "
                    "which is a different defect from the one this gate exists for, and is "
                    "still a defect.")
                continue
            for member in members:
                if str(member) in trustee_teams:
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
          "a trustee-facing role is a member of any column security profile.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
