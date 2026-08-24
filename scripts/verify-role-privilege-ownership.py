#!/usr/bin/env python3
"""Verify that no security role requests a privilege the platform will never create.

A Dataverse table's ``<OwnershipType>`` decides which privileges exist for it. This is not a
policy question the project gets to answer — the privilege GUIDs are created by the platform
when the table is created, and a role binding names one by id:

* **UserOwned** — Create, Read, Write, Delete, Append, AppendTo, **Assign**, **Share**.
* **OrganizationOwned** — Create, Read, Write, Delete, Append, AppendTo. **No Assign. No
  Share.** An organization-owned row has no individual owner, so there is nobody to assign it
  to and nobody to share it from, and Dataverse never creates either privilege.

Requesting an Assign or a Share on an organization-owned table is therefore not an over-grant
that the platform quietly ignores. It is a binding against a privilege that cannot be resolved,
and it fails:

    FAILED — Privilege 'prvAssignrev_provider' (Global) on Security role 'REV Admin' :
    privilege 'prvAssignrev_provider' does not exist in this environment

── WHY THIS EXISTS ──────────────────────────────────────────────────────────────────────────

On 2026-08-24 the reviewer's live ``ensure-schema.ps1 -Env dev`` run produced exactly four such
lines: ``prvAssignrev_provider`` and ``prvSharerev_provider``, on both ``REV Admin`` and ``REV
Service Automation`` (IMP-0254). ``rev_provider`` is organization-owned; the eight-privilege
block had been written from the shape the solution's UserOwned tables use.

The instructive part is that the project got this right and wrong in the same afternoon.
``rev_anonymisedstatistic`` is also organization-owned and its role blocks omit Assign and
Share correctly. A worked correct example in the same tree did not prevent the defect, because
nothing compared a privilege request against the ownership of the table it names. That is this
gate.

── GROUND TRUTH ─────────────────────────────────────────────────────────────────────────────

Read live from DEV on 2026-08-24 via ``privileges?$filter=endswith(name,'<table>')`` for every
custom table in the solution, cross-checked against each table's live
``EntityDefinitions(LogicalName='<t>')?$select=OwnershipType``. All ten tables agreed with the
sets above with no exceptions:

    rev_applicant  rev_application  rev_grant  rev_bankaccount  rev_payment  rev_review
        UserOwned          → all eight privileges exist
    rev_provider  rev_anonymisedstatistic  rev_errorlog  rev_setting
        OrganizationOwned  → Assign and Share ABSENT, the other six present

**Note the asymmetry, because it is what makes the mistake easy: DELETE DOES EXIST on an
organization-owned table.** The missing set is exactly {Assign, Share}. Withholding Delete —
which ``rev_anonymisedstatistic`` and ``rev_grant`` both do — is a separate, deliberate policy
decision about a privilege that is really there, and this gate must never conflate the two. It
therefore only ever reports a privilege the platform cannot create; it says nothing about a
privilege deliberately not requested.

── IT DERIVES, IT DOES NOT TRANSCRIBE ───────────────────────────────────────────────────────

Ownership is read from each table's own ``<OwnershipType>`` element and the requested verb is
split off the privilege name against the table names actually present under ``Entities/``.
Nothing here holds a list of which tables are organization-owned (C-TECH-060, C-TECH-067): a
table that changes ownership, or a new organization-owned table added next month, is checked
correctly for free. A transcribed list would have gone stale on exactly the change that matters.

Privileges naming something that is not a table in this solution — ``prvReadSavedQuery``,
``prvReadEnvironmentVariableValue`` and the other out-of-box bindings — are skipped and
counted. Their ownership is not knowable from this source tree, so asserting on them would be
a guess.

Run:
    python3 scripts/verify-role-privilege-ownership.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-role-privilege-ownership.py --selftest

Exits 0 when every requested privilege can exist, 1 otherwise. Wired into
config/<slug>-build.yml as the ``role-privilege-ownership`` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile

# The privilege verbs Dataverse will NOT create for a table, keyed by OwnershipType. Read this
# as "what the platform withholds", never as "what this project chooses not to grant" — the
# two are different questions and only the first belongs in a gate.
IMPOSSIBLE_VERBS: dict[str, frozenset[str]] = {
    "organizationowned": frozenset({"Assign", "Share"}),
    "userowned": frozenset(),
}

# Every verb the platform prefixes onto a table name to form a privilege. Used only to split a
# privilege name into (verb, table) and to recognise a name shaped like a table privilege at
# all; the decision itself comes from IMPOSSIBLE_VERBS above.
KNOWN_VERBS = ("Create", "Read", "Write", "Delete", "Append", "AppendTo", "Assign", "Share")


def table_ownership(root: str) -> dict[str, str]:
    """Every table's OwnershipType, READ from its own <OwnershipType> element.

    Lowercased for comparison. A table whose Entity.xml declares no OwnershipType is absent
    from the result and its privileges are reported as unknown rather than assumed.
    """
    found: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(root, "Entities/*/Entity.xml"))):
        table = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        # Strip comments first: rev_grant/Entity.xml discusses its own OwnershipType in prose
        # in the file header, and a regex over raw XML would read the sentence instead of the
        # element (IMP-0020, the same trap that let a marker inside a comment satisfy a check).
        source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
        match = re.search(r"<OwnershipType>([^<]+)</OwnershipType>", source)
        if match:
            found[table] = match.group(1).strip().lower()
    return found


def _split_privilege(name: str, tables: frozenset[str]) -> tuple[str, str] | None:
    """Split ``prv<Verb><table>`` into (verb, table), or None if it names no known table.

    Matches the LONGEST table suffix, so ``prvReadrev_application`` resolves to
    ``rev_application`` and never to a shorter table that happens to be a suffix of it.
    """
    if not name.startswith("prv"):
        return None
    candidates = sorted((t for t in tables if name.endswith(t)), key=len, reverse=True)
    for table in candidates:
        verb = name[len("prv"):-len(table)]
        if verb in KNOWN_VERBS:
            return verb, table
    return None


def role_privileges(root: str) -> list[tuple[str, str, str]]:
    """Every (role, privilege name, level) requested by any role file under Roles/."""
    found: list[tuple[str, str, str]] = []
    for path in sorted(glob.glob(os.path.join(root, "Roles/*/*.xml"))):
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        source = re.sub(r"<!--.*?-->", "", source, flags=re.S)
        role_match = re.search(r"<Role[^>]*\sname=\"([^\"]+)\"", source)
        role = role_match.group(1) if role_match else os.path.basename(os.path.dirname(path))
        for element in re.findall(r"<RolePrivilege\b[^>]*/>", source):
            name_match = re.search(r'\bname="([^"]+)"', element)
            if not name_match:
                continue
            level_match = re.search(r'\blevel="([^"]+)"', element)
            found.append((role, name_match.group(1),
                          level_match.group(1) if level_match else ""))
    return found


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")

    roles_dir = os.path.join(root, "Roles")
    if not os.path.isdir(roles_dir):
        print(f"FAIL - {roles_dir} is missing, so there are no role files to check. This gate "
              f"passing over an absent directory would be a gate that cannot fail (IMP-0007).")
        return 1

    ownership = table_ownership(root)
    if not ownership:
        print(f"FAIL - no <OwnershipType> was readable from any {root}/Entities/*/Entity.xml. "
              f"Without ownership there is nothing to check against, and reporting PASS here "
              f"would be a gate firing on nothing (IMP-0057).")
        return 1

    tables = frozenset(ownership)
    requests = role_privileges(root)
    if not requests:
        print(f"FAIL - no <RolePrivilege> element was found in any {roles_dir}/*/*.xml. Either "
              f"the roles ship no privileges, or this gate's reader is broken; both need a "
              f"person, not a PASS.")
        return 1

    problems: list[str] = []
    checked = 0
    skipped: list[str] = []

    for role, privilege, level in requests:
        split = _split_privilege(privilege, tables)
        if split is None:
            skipped.append(privilege)
            continue
        verb, table = split
        checked += 1
        owner = ownership[table]
        impossible = IMPOSSIBLE_VERBS.get(owner)
        if impossible is None:
            problems.append(
                f"  UNKNOWN OWNERSHIP - {table} declares OwnershipType '{owner}', which this "
                f"gate has no privilege set for. Add it to IMPOSSIBLE_VERBS with the live "
                f"privilege inventory that proves it, rather than letting the privilege "
                f"through unchecked."
            )
            continue
        if verb in impossible:
            legal = ", ".join(v for v in KNOWN_VERBS if v not in impossible)
            article = "an" if verb[0].upper() in "AEIOU" else "a"
            problems.append(
                f"  PRIVILEGE CANNOT EXIST - role '{role}' requests '{privilege}'"
                f"{f' ({level})' if level else ''}, but {table} is {owner} and Dataverse never "
                f"creates {article} {verb} privilege for an organization-owned table - there is no "
                f"individual owner to assign to or share from. The live run fails with "
                f"\"privilege '{privilege}' does not exist in this environment\". Remove this "
                f"line. The privileges that DO exist for {table} are: {legal} - note that "
                f"Delete is among them, so this is not a reason to drop Delete too."
            )

    if problems:
        print(f"FAIL - {len(problems)} role privilege(s) the platform will never create:")
        print("\n".join(problems))
        print(f"\n{checked} table privilege(s) checked across {len(set(r for r, _, _ in requests))} "
              f"role(s); {len(skipped)} non-solution privilege(s) skipped.")
        return 1

    org_owned = sorted(t for t, o in ownership.items() if o == "organizationowned")
    print(
        f"PASS - {checked} table privilege(s) across "
        f"{len(set(r for r, _, _ in requests))} role(s), every one a privilege the platform "
        f"actually creates for the table it names. "
        f"{len(org_owned)} organization-owned table(s) ({', '.join(org_owned)}) correctly "
        f"request no Assign and no Share. "
        f"{len(skipped)} out-of-box privilege(s) skipped as not derivable from this source tree."
    )
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# The known-bad fixture is the exact shape that failed live on 2026-08-24: an Assign and a
# Share requested on an organization-owned table. A gate with no known-bad fixture is a gate
# nobody has seen fail.

_ENTITY = """<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Name LocalizedName="T">{table}</Name>
  <EntityInfo><entity Name="{table}"><attributes /></entity></EntityInfo>
  <OwnershipType>{ownership}</OwnershipType>
  <PrimaryNameAttribute>rev_name</PrimaryNameAttribute>
</Entity>
"""

_ROLE = """<?xml version="1.0" encoding="utf-8"?>
<Role name="{role}">
  <RolePrivileges>
{privileges}  </RolePrivileges>
</Role>
"""


def _tree(base: str, *, ownership: str, verbs: tuple[str, ...],
          extra: str = "") -> str:
    table = "rev_thing"
    root = os.path.join(base, "sol")
    os.makedirs(os.path.join(root, "Entities", table), exist_ok=True)
    os.makedirs(os.path.join(root, "Roles", "R One"), exist_ok=True)
    with open(os.path.join(root, "Entities", table, "Entity.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_ENTITY.format(table=table, ownership=ownership))
    lines = "".join(
        f'    <RolePrivilege name="prv{verb}{table}" level="Global" />\n' for verb in verbs
    ) + extra
    with open(os.path.join(root, "Roles", "R One", "R One.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_ROLE.format(role="R One", privileges=lines))
    return root


_ALL_EIGHT = KNOWN_VERBS
_SIX = tuple(v for v in KNOWN_VERBS if v not in ("Assign", "Share"))

_CASES = {
    # IMP-0254: the shape that produced four FAILED lines on the live DEV run.
    "assign-share-on-org-owned-must-fail": (
        {"ownership": "OrganizationOwned", "verbs": _ALL_EIGHT}, 1,
        "PRIVILEGE CANNOT EXIST"),
    # The fix: the same table, the six privileges that exist. Delete stays.
    "six-on-org-owned-must-pass": (
        {"ownership": "OrganizationOwned", "verbs": _SIX}, 0, "PASS"),
    # All eight on a user-owned table is correct and must not be flagged.
    "all-eight-on-user-owned-must-pass": (
        {"ownership": "UserOwned", "verbs": _ALL_EIGHT}, 0, "PASS"),
    # An out-of-box privilege names no table here; it must be skipped, not guessed at.
    "out-of-box-privilege-must-be-skipped": (
        {"ownership": "OrganizationOwned", "verbs": _SIX,
         "extra": '    <RolePrivilege name="prvReadSavedQuery" level="Global" />\n'}, 0,
        "1 out-of-box privilege(s) skipped"),
    # An ownership value this gate has no inventory for must be reported, never waved through.
    "unknown-ownership-must-fail": (
        {"ownership": "BusinessOwned", "verbs": _SIX}, 1, "UNKNOWN OWNERSHIP"),
}

# Delete must never be reported as impossible on an organization-owned table — that is the
# asymmetry this gate exists to keep straight, and an exit code cannot prove its absence.
_MUST_NOT_CONTAIN = {
    "assign-share-on-org-owned-must-fail": "requests 'prvDeleterev_thing'",
    "six-on-org-owned-must-pass": "PRIVILEGE CANNOT EXIST",
}


def selftest() -> int:
    import contextlib
    import io

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (kwargs, want_rc, want_text) in _CASES.items():
            root = _tree(os.path.join(tmp, name), **kwargs)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                rc = main(["verify-role-privilege-ownership.py", root])
            text = buffer.getvalue()
            banned = _MUST_NOT_CONTAIN.get(name)
            ok = (rc == want_rc and want_text in text
                  and (not banned or banned not in text))
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in text.splitlines():
                    print(f"                   {line}")

    if failures:
        print(f"\nverify-role-privilege-ownership: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-role-privilege-ownership: SELFTEST OK — {len(_CASES)} fixtures. The shape "
          f"that failed live fails here, Delete on an organization-owned table is never "
          f"flagged, and an ownership value with no known inventory is reported rather than "
          f"waved through.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
