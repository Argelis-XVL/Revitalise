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

── THE THIRD CHECK: A SECURED COLUMN THE PLATFORM WILL NOT SECURE (C-TECH-070) ──────────────

The two checks above ask whether source agrees with itself. They cannot ask the more basic
question: **is this column one Dataverse can secure at all?** Two shapes are not, and this
project has now been bitten by both — one loudly, one silently:

* **A table's PRIMARY NAME attribute can never be secured.** ``IsSecured=1`` on it makes
  Dataverse refuse to create the table, with ``0x8004f501 "The field '<name>' is not
  securable."`` On 2026-08-23 this failed ``rev_bankaccount`` and ``rev_payment`` outright,
  taking every dependent column, relationship, privilege and field permission with them
  (IMP-0249). The source was authored from the TAD's literal "every column in this table"
  wording; nothing checked it against a real create call, and *this gate reported PASS over it*
  in build #4 hours before the live run rejected it.

* **A MONEY column's automatic ``_base`` twin cannot be secured.** The platform creates
  ``<name>_base`` alongside every Money column with ``CanBeSecuredForRead=False``, so anyone
  holding table Read can read the same number from the twin. Securing the authored column is
  therefore not a confidentiality control (IMP-0047, verified live 2026-08-19 on
  ``rev_grant.rev_amountawarded``). This one creates cleanly and fails silently, which is why
  it went four days unreported: the finding proposed this very warning, and was closed on the
  knowledge-file half of its own proposed change.

The first is a FAIL — the create call will not succeed, so there is nothing to discuss. The
second is a WARNING, deliberately: on 2026-08-19 the reviewer accepted the risk on the basis
that the table privilege is the real control (only REV Admin and REV Service Automation hold
Read on ``rev_grant``, and both are entitled to the amount). A build failure would overturn a
recorded decision; a warning puts the fact in front of whoever next writes a role.

**Both read the primary name from each table's own ``<PrimaryNameAttribute>`` declaration and
the type from the column's own ``<Type>``. Neither is transcribed** — C-TECH-067's rule, and
the reason this survives a table whose primary name is not ``rev_name``.

── THE FOURTH CHECK: A SECURED COLUMN THE CREATION PATH CANNOT DELIVER (IMP-0255) ───────────

The three checks above all ask questions about *source*. On 2026-08-24 five field permissions
failed live with ``0x8004f508`` — "attribute is NOT secured for entity fieldpermission" — while
**every check above correctly reported PASS**, because source was entirely self-consistent:
``rev_bankaccount.rev_applicantid``, ``rev_bankaccount.rev_providerid``,
``rev_payment.rev_grantid``, ``rev_payment.rev_bankaccountid`` and
``rev_payment.rev_providerid`` each declare ``IsSecured=1`` in their own Entity.xml *and* each
has a field permission in ``REV_FinanceOnly``. Both directions agreed. The columns were
unsecured anyway.

**The gap was never in source — it was between source and the code that creates the column.**
A Dataverse lookup cannot be created as a standalone attribute, so
``ConvertTo-RevAttributeBody`` throws for ``Type 'lookup'`` and every lookup is instead created
as the inline ``Lookup`` deep-insert inside ``ConvertTo-RevRelationshipBody``. That body set
DisplayName, Description and RequiredLevel — and dropped ``IsSecured`` on the floor. So the
flag was declared, released, checked, and never sent.

Note what this means for the check IMP-0255 itself proposed ("every attribute named in
FieldSecurityProfiles.xml resolves to something in source that declares IsSecured=1"). That
check already exists above as POINTLESS PERMISSION, and it passed — because the declaration was
there. **A source-only gate could not have caught this defect at any strictness.** What was
needed was a gate that reads the provisioning path.

**RETIRED FROM THIS GATE ON 2026-08-24, improvement review 23.** The check that lived here
asked whether ``ConvertTo-RevRelationshipBody`` sets ``IsSecured`` on the lookup body — one
property, one function. It is replaced by
``scripts/verify-declared-property-reaches-creation-path.py``, which asks the general question
of *every* property ``ConvertFrom-RevEntityXml`` parses against *every* builder that can create
an attribute. Per ``skills/how-to-promote-a-finding.md`` §2 the second instance of a class may
not get another instance-level gate, and the paragraphs above are the class statement; keeping a
single-property copy of it here would be exactly the duplicate coverage the altitude rule
forbids.

All three of this check's known-bad fixtures moved to that gate and still fail there —
``dropped-issecured-must-fail``, ``carried-issecured-must-pass`` and
``missing-helpers-module-must-fail``. That assertion is the coverage proof the retirement rule
demands; the generalisation also caught one gap this check could never see, ``IsAuditEnabled``
missing from the same lookup body.

What stays here is the part that is genuinely about *confidentiality* rather than about property
transmission: the name-companion warning below.

**Securability was ground-truthed, not assumed.** Read live from DEV on 2026-08-24: all five
lookups report ``CanBeSecuredForRead``/``ForCreate``/``ForUpdate`` = True with ``IsSecured`` =
False. A lookup is fully securable — unlike the primary name in the third check, whose live
``CanBeSecuredForRead`` is False on both tables. The two are different limits and must not be
collapsed into one.

── THE SECOND WARNING: A SECURED LOOKUP'S NAME COMPANION IS NOT SECURED ─────────────────────

Dataverse maintains a ``<lookup>name`` String column beside every lookup, holding the *primary
name value of the related row*, and it reports ``CanBeSecuredForRead=False`` — verified live
2026-08-24 on all five (``rev_applicantidname``, ``rev_provideridname``, ``rev_grantidname``,
``rev_bankaccountidname``). This is structurally the Money ``_base`` problem: securing the
lookup hides the GUID and not the text.

For this solution the residual is narrow, because three of the four targets have an autonumber
primary name — ``rev_applicantidname`` yields ``REV-A-00001`` and ``rev_grantidname``
``GR-2026-00001``, both pseudonymous references rather than identity. The exception worth
knowing is ``rev_provideridname``, which yields the provider's real organisation name. As with
Money, the actual control is the table privilege: no role but Finance holds Read on
``rev_bankaccount`` or ``rev_payment`` (NFR-002). Warning, not failure — but whoever next grants
a role Read on either table needs this in front of them.

Run:
    python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-field-security-coverage.py --selftest

Exits 0 when consistent, 1 otherwise. Wired into config/<slug>-build.yml as the
``field-security-coverage`` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile

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


def _attribute_blocks(source: str) -> list[tuple[str, str]]:
    """Every (PhysicalName, body) attribute block in one Entity.xml."""
    return re.findall(r'<attribute PhysicalName="([^"]+)">(.*?)</attribute>', source, re.S)


def primary_name_attributes(root: str) -> dict[str, str]:
    """Every table's primary name column, READ from its own <PrimaryNameAttribute>.

    Derived, never transcribed (C-TECH-067). A table whose primary name is not ``rev_name``
    is checked correctly for free; a hardcoded ``rev_name`` would have silently stopped
    checking the moment one existed.
    """
    found: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(root, "Entities/*/Entity.xml"))):
        table = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        match = re.search(r"<PrimaryNameAttribute>([^<]+)</PrimaryNameAttribute>", source)
        if match:
            found[table] = match.group(1).strip().lower()
    return found


def secured_columns_of_type(root: str, wanted: set[str]) -> set[tuple[str, str]]:
    """Every (table, column) that is IsSecured=1 AND whose <Type> is in ``wanted``."""
    found: set[tuple[str, str]] = set()
    for path in sorted(glob.glob(os.path.join(root, "Entities/*/Entity.xml"))):
        table = os.path.basename(os.path.dirname(path))
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        for name, body in _attribute_blocks(source):
            if "<IsSecured>1</IsSecured>" not in body:
                continue
            type_match = re.search(r"<Type>([^<]+)</Type>", body)
            if type_match and type_match.group(1).strip().lower() in wanted:
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
            # PascalCase and AttributeName (not attributelogicalname) since 2026-08-14: fixed
            # to match the real Dataverse element names/casing, confirmed via a live
            # `pac solution export` of DEV after ensure-schema.ps1 created this profile via the
            # Web API — the original lowercase/attributelogicalname shape was a fabricated
            # guess that a live `pac solution import` rejected outright. See
            # FieldSecurityProfiles.xml's own header for the full story.
            r"<EntityName>([^<]+)</EntityName>\s*<AttributeName>([^<]+)</AttributeName>",
            source,
        )
    )


_USAGE = "<solution-root>"
_EXAMPLE = "src/solutions/RevitaliseGrantAutomation"


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
    if len(argv) != 2:
        return _usage_error(len(argv) - 1)
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

    # ── C-TECH-070: a secured column the platform will not secure ────────────────────────
    primary = primary_name_attributes(root)
    for table, column in sorted(secured):
        if primary.get(table) == column.lower():
            problems.append(
                f"  NOT SECURABLE - {table}.{column} is IsSecured=1 and it is that table's "
                f"PRIMARY NAME attribute. Dataverse refuses to create the table at all: "
                f"0x8004f501 \"The field '{column}' is not securable.\" A primary name column "
                f"can never carry field-level security, whatever a source document's wording "
                f"says. Set IsSecured=0 and remove its field permission."
            )

    # Property transmission — whether the creation path actually SENDS a declared IsSecured —
    # was checked here until 2026-08-24 and is now owned by
    # scripts/verify-declared-property-reaches-creation-path.py for every parsed property, not
    # just this one. See this module's header for the retirement and its coverage proof.
    secured_lookups = sorted(secured_columns_of_type(root, {"lookup"}))

    warnings: list[str] = []
    # ONE warning for all of them, not one per column. The same paragraph repeated five times
    # is the shape that defeats the reader (IMP-0059); the columns are the variable part, so
    # they are the list and the explanation is said once.
    if secured_lookups:
        companions = ", ".join(f"{t}.{c}name" for t, c in secured_lookups)
        tables = ", ".join(sorted({t for t, _ in secured_lookups}))
        warnings.append(
            f"  A SECURED LOOKUP'S NAME COMPANION IS NOT SECURED - {len(secured_lookups)} "
            f"secured lookup(s) each have a companion column Dataverse will not secure: "
            f"{companions} (all CanBeSecuredForRead=False, verified live 2026-08-24). Each "
            f"holds the RELATED row's primary name value, so securing the lookup hides the "
            f"GUID and not the text - structurally the Money _base problem. Residual here is "
            f"narrow: rev_applicant and rev_grant have autonumber primary names, so those "
            f"companions yield a pseudonymous reference (REV-A-00001, GR-2026-00001). THE ONE "
            f"THAT MATTERS is any provider lookup, whose companion yields the provider's real "
            f"organisation name. The control is the TABLE PRIVILEGE, not column security "
            f"(NFR-002: only Finance holds Read on {tables}). Confirm that before granting any "
            f"new role Read on either table."
        )
    for table, column in sorted(secured_columns_of_type(root, {"money"})):
        warnings.append(
            f"  MONEY IS NOT SECURABLE IN FULL - {table}.{column} is IsSecured=1, but Dataverse "
            f"maintains {column}_base alongside it with CanBeSecuredForRead=False. Anyone with "
            f"Read on {table} can read the same value from the twin, so column security is not "
            f"the control here - the TABLE PRIVILEGE is. Accepted by the reviewer 2026-08-19 on "
            f"that basis. Before granting any new role Read on {table}, confirm it is entitled "
            f"to this amount. Use Decimal instead for any NEW restricted amount."
        )

    if problems:
        print(f"FAIL - field security coverage is inconsistent ({len(problems)} problem(s)):")
        print("\n".join(problems))
        if warnings:
            print(f"\nWARNING ({len(warnings)}):")
            print("\n".join(warnings))
        return 1

    print(
        f"PASS - {len(secured)} secured column(s), every one released by a field security "
        f"profile, no permission granted for an unsecured column, and no secured column of a "
        f"shape Dataverse refuses to secure ({len(EXPECTED_UNSECURED)} reviewed exemption(s), "
        f"{len(secured_lookups)} secured lookup(s) carrying the companion caveat below)."
    )
    if warnings:
        print(f"\nWARNING - {len(warnings)} secured column(s) the platform cannot fully "
              f"protect. Not a build failure; a standing fact whoever writes the next role "
              f"needs:")
        print("\n".join(warnings))
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# Each fixture is one of the two shapes that reached a live environment, plus the clean case.
# A gate with no known-bad fixture is a gate nobody has seen fail.

_ENTITY = """<?xml version="1.0" encoding="utf-8"?>
<Entity>
  <Name LocalizedName="T">{table}</Name>
  <EntityInfo>
    <entity Name="{table}">
      <attributes>
        <attribute PhysicalName="{pname}">
          <Type>nvarchar</Type>
          <IsSecured>{psec}</IsSecured>
        </attribute>
        <attribute PhysicalName="rev_amount">
          <Type>{amount_type}</Type>
          <IsSecured>{asec}</IsSecured>
        </attribute>
      </attributes>
    </entity>
  </EntityInfo>
  <PrimaryNameAttribute>{pname}</PrimaryNameAttribute>
</Entity>
"""

_PROFILE = """<?xml version="1.0" encoding="utf-8"?>
<FieldSecurityProfiles>
  <FieldSecurityProfile name="P">
    <FieldPermissions>
{perms}    </FieldPermissions>
  </FieldSecurityProfile>
</FieldSecurityProfiles>
"""


def _tree(base: str, *, psec: str, asec: str, amount_type: str) -> str:
    table = "rev_thing"
    root = os.path.join(base, "sol")
    os.makedirs(os.path.join(root, "Entities", table), exist_ok=True)
    os.makedirs(os.path.join(root, "Other"), exist_ok=True)
    with open(os.path.join(root, "Entities", table, "Entity.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_ENTITY.format(table=table, pname="rev_name", psec=psec,
                                    asec=asec, amount_type=amount_type))
    perms = ""
    for column, flag in (("rev_name", psec), ("rev_amount", asec)):
        if flag == "1":
            perms += (f"      <FieldPermission>\n        <EntityName>{table}</EntityName>\n"
                      f"        <AttributeName>{column}</AttributeName>\n"
                      f"      </FieldPermission>\n")
    with open(os.path.join(root, "Other", "FieldSecurityProfiles.xml"), "w",
              encoding="utf-8") as handle:
        handle.write(_PROFILE.format(perms=perms))
    return root


_CASES = {
    # IMP-0249: the shape that failed rev_bankaccount and rev_payment live.
    "secured-primary-name-must-fail": (
        {"psec": "1", "asec": "1", "amount_type": "decimal"}, 1, "NOT SECURABLE"),
    # IMP-0047: the shape that creates cleanly and leaks through the _base twin.
    "secured-money-must-warn": (
        {"psec": "0", "asec": "1", "amount_type": "money"}, 0,
        "MONEY IS NOT SECURABLE IN FULL"),
    # The fix for both: primary name released, restricted amount typed Decimal.
    "clean-tree-must-pass": (
        {"psec": "0", "asec": "1", "amount_type": "decimal"}, 0, "PASS"),
    # The three property-transmission fixtures that lived here moved to
    # verify-declared-property-reaches-creation-path.py on 2026-08-24 with the check they
    # exercised. They still fail there; that is the coverage proof for the retirement.
    # The name-companion warning fires on any secured lookup, and only on a secured lookup.
    "secured-lookup-must-warn-about-name-companion": (
        {"psec": "0", "asec": "1", "amount_type": "lookup"}, 0,
        "NAME COMPANION IS NOT SECURED"),
}

# A warning that must NOT fire cannot be proved by an exit code — a false warning changes
# neither rc nor PASS. The clean case names the string its output must be free of.
# A decimal column must never draw the lookup name-companion warning, and a lookup must never
# draw the Money one — two warnings that would otherwise be easy to fire on the wrong shape
# without changing any exit code or the PASS line.
_MUST_NOT_CONTAIN: dict[str, tuple[str, ...]] = {
    "clean-tree-must-pass": ("MONEY IS NOT SECURABLE", "NAME COMPANION"),
    "secured-lookup-must-warn-about-name-companion": ("MONEY IS NOT SECURABLE",),
    "secured-money-must-warn": ("NAME COMPANION",),
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
                rc = main(["verify-field-security-coverage.py", root])
            text = buffer.getvalue()
            banned = _MUST_NOT_CONTAIN.get(name, ())
            ok = (rc == want_rc and want_text in text
                  and not any(phrase in text for phrase in banned))
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in text.splitlines():
                    print(f"                   {line}")

    if failures:
        print(f"\nverify-field-security-coverage: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-field-security-coverage: SELFTEST OK — {len(_CASES)} fixtures. Both "
          f"shapes that reached a live environment fail or warn, and the clean tree is "
          f"silent about both. Property transmission moved to "
          f"verify-declared-property-reaches-creation-path.py (9 fixtures) on 2026-08-24.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
