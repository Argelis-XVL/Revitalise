#!/usr/bin/env python3
"""Verify that every secured column has a field permission, and vice versa.

In Dataverse a column marked ``IsSecured=1`` is readable by NOBODY except a System
Administrator until a field security profile releases it. This project deliberately has no
System Administrator among its application personas (TAD section 6.5, ADR-019), so:

* A secured column MISSING from ``REV_TrusteeRestricted`` is unreadable and unwritable by the
  process owner and by the service identity. The symptom is not a security hole - it is a blank
  field nobody can account for, or an intake write that fails with a permission error naming a
  column the developer believed was fine. That is the expensive direction.
* A field permission for a column that is NOT secured is harmless at runtime but misleading: it
  reads as a control that is doing something when it is not.

Both directions are checked. This exists for the same reason
``verify-solution-root-components.py`` does: the solution source is hand-authored ahead of a live
DEV environment, so nothing round-trips through ``pac solution unpack`` to keep the two files
honest with each other.

Columns may be exempted by listing them in EXPECTED_UNSECURED below, with a reason. An exemption
is a deliberate, reviewed decision, which is why it lives in code rather than being inferred.

Run:
    python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation

Exits 0 when consistent, 1 otherwise. Wired into config/<slug>-build.yml as the
``field-security-coverage`` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys

# Columns that are personal data but are deliberately NOT secured. Each entry is a reviewed
# decision, so it carries its reason here rather than only in a document.
EXPECTED_UNSECURED: dict[tuple[str, str], str] = {
    ("rev_application", "rev_breaklocation"): (
        "Trustee-visible by design (grant-application-data-model-v0.2.md). A trustee cannot judge "
        "a request for a break without knowing where the break is. Names a place, not a person."
    ),
}


def _read_all(pattern: str, root: str) -> str:
    out = []
    for path in sorted(glob.glob(os.path.join(root, pattern), recursive=True)):
        with open(path, encoding="utf-8") as handle:
            out.append(handle.read())
    return "\n".join(out)


def secured_columns(root: str) -> set[tuple[str, str]]:
    """Every (table, column) whose attribute definition carries IsSecured=1."""
    found: set[tuple[str, str]] = set()
    for path in sorted(glob.glob(os.path.join(root, "Entities/*/Entity.xml"))):
        table = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        for name, body in re.findall(
            r'<attribute PhysicalName="([^"]+)">(.*?)</attribute>', source, re.S
        ):
            if "<IsSecured>1</IsSecured>" in body:
                found.add((table, name))
    return found


def released_columns(root: str) -> set[tuple[str, str]]:
    """Every (table, column) granted a permission by any field security profile.

    Field security profiles live in Other/FieldSecurityProfiles.xml, not a
    FieldSecurityProfiles/ folder. That path is fixed by SolutionPackagerLib's component
    configuration (directory "Other", file "$(type)s.xml") and FieldSecurityProfileProcessor
    returns null WITHOUT an error if it is absent, so the folder form used to drop the profile
    out of the package silently - see Dev Summary revision 0.5.
    """
    source = _read_all("Other/FieldSecurityProfiles.xml", root)
    return set(
        re.findall(
            r"<entityname>([^<]+)</entityname>\s*<attributelogicalname>([^<]+)</attributelogicalname>",
            source,
        )
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")

    if not os.path.isfile(os.path.join(root, "Other", "FieldSecurityProfiles.xml")):
        print(f"FAIL - {root}/Other/FieldSecurityProfiles.xml is missing. The packer reads that "
              f"exact path and silently ships nothing if it is absent, so a missing file here "
              f"means 34 secured columns nobody can read.")
        return 1

    secured = secured_columns(root)
    released = released_columns(root)

    problems: list[str] = []

    for table, column in sorted(secured - released):
        problems.append(
            f"  UNREADABLE - {table}.{column} is IsSecured=1 but no field security profile "
            f"releases it. Nobody but a System Administrator can read or write it."
        )

    for table, column in sorted(released - secured):
        if (table, column) in EXPECTED_UNSECURED:
            continue
        problems.append(
            f"  POINTLESS PERMISSION - {table}.{column} has a field permission but the column is "
            f"not IsSecured=1, so the permission grants nothing."
        )

    for (table, column), reason in sorted(EXPECTED_UNSECURED.items()):
        if (table, column) in secured:
            problems.append(
                f"  EXEMPTION CONTRADICTED - {table}.{column} is listed in EXPECTED_UNSECURED "
                f"({reason.split('.')[0]}.) but the column is now IsSecured=1. Resolve which is "
                f"intended."
            )

    if problems:
        print(f"FAIL - field security coverage is inconsistent ({len(problems)} problem(s)):")
        print("\n".join(problems))
        return 1

    print(
        f"PASS - {len(secured)} secured column(s), every one released by a field security "
        f"profile, and no permission granted for an unsecured column "
        f"({len(EXPECTED_UNSECURED)} reviewed exemption(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
