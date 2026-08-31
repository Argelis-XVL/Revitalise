#!/usr/bin/env python3
"""A property the solution source declares is only delivered if the code that builds the
create call emits it. This gate compares the two.

Usage:
    verify-declared-property-reaches-creation-path.py <repo-root>
    verify-declared-property-reaches-creation-path.py --selftest

WHY THIS EXISTS. `IMP-0255`, and the reason it is a general gate rather than another
one-property check is `IMP-0258`'s corollary:

    A source-vs-source gate can NEVER catch a source-vs-creation-path gap.

Five lookup columns on `rev_bankaccount` and `rev_payment` declared `<IsSecured>1</IsSecured>`
in their own `Entity.xml`. `ConvertFrom-RevEntityXml` parsed the flag. `FieldSecurityProfiles.xml`
named all five. Source was entirely self-consistent, and every source-reading gate correctly
passed — including `verify-field-security-coverage.py`, which had been extended the day before
for exactly this class of defect. The columns were still created unsecured, because
`ConvertTo-RevRelationshipBody` never put `IsSecured` on the `$lookupBody` it sends. Five
Tier 4 columns were unprotected in the only environment anyone was testing in, with every
gate green (`IMP-0259`).

WHAT THIS CHECKS. `ConvertFrom-RevEntityXml` reads N properties off each `<attribute>`. Every
builder that can create an attribute must, for each of those properties, either:

  * REFERENCE it            → the property can reach the platform. Fine.
  * declare it NOT_APPLICABLE with a reason → the shape cannot carry it at all. Fine.
  * declare it a KNOWN_GAP with an owner and a finding id → WARNS on every run. Not fine,
                             but visible, which is the whole point.
  * none of the above       → FAIL. This is the IMP-0255 shape.

A property newly added to the parser therefore fails this gate until somebody decides, in
writing, which of the three it is. That is the property being defended: the decision is forced
to be explicit rather than defaulting to silence.

WHY A LOOKUP IS THE ONLY SHAPE THAT NEEDED THIS. `ConvertTo-RevAttributeBody` throws for
`Type 'lookup'` — a Dataverse lookup cannot be created as a standalone attribute. Lookups are
created only as the inline `Lookup` deep-insert inside `ConvertTo-RevRelationshipBody`, so every
property a lookup will ever have must be on that one body or it is never set at all. Combined
with `ensure-schema.ps1`'s relationship step being create-only, that made lookups the only
columns in the solution with no reconcile path — see `C-TECH-042` and step 3b.

SEVERITY DESIGN, and it is deliberate. A KNOWN_GAP warns rather than fails because the gap it
records today (`IsAuditEnabled` on the lookup shape) is latent: all twelve lookup columns in the
solution declare `IsAuditEnabled=1`, which is the platform default the builder assumes when it
emits nothing, so nothing is currently mis-delivered. Failing the build over a gap that has no
live consequence teaches people to route around the gate (`IMP-0181`). Removing a KNOWN_GAP
entry without fixing the builder makes this gate FAIL, which is the ratchet.

RESIDUAL, stated because it is not covered. This gate compares a parser's output to a builder's
output by NAME. It cannot know whether a property is semantically inapplicable to a shape, so it
trusts NOT_APPLICABLE — and a wrong entry there is a silent pass. It also cannot see a property
the parser itself never reads: if `Entity.xml` declares something `ConvertFrom-RevEntityXml`
does not parse, both sides agree and both are wrong. That second rung belongs to a different
check and does not exist.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

HELPERS = os.path.join("provisioning", "dataverse", "ensure-schema-helpers.psm1")

# ── The builders that can create an attribute ──────────────────────────────────────────────
# Each entry names the region of the module whose text is searched for a property reference.
# "function" means the whole function body; "hashtable" means one $name = @{...} construction
# plus any $name.<prop> = ... assignments in that function — which is how the lookup body is
# built, and searching the whole enclosing function would let a property mentioned anywhere in
# ConvertTo-RevRelationshipBody (the relationship body itself sets several) satisfy the check.
BUILDERS: dict[str, dict[str, str]] = {
    "ConvertTo-RevAttributeBody": {
        "kind": "function",
        "shape": "every non-lookup attribute type",
    },
    "ConvertTo-RevRelationshipBody/$lookupBody": {
        "kind": "hashtable",
        "function": "ConvertTo-RevRelationshipBody",
        "variable": "lookupBody",
        "shape": "lookup",
    },
}

# WHY R3 OF verify-source-reader-plurality.py DOES NOT APPLY HERE. That gate DERIVES its reader
# list by scanning for mentions of the solution's repeatable source, and the docstring above
# mentions Entity.xml and FieldSecurityProfiles.xml while explaining the defect — so this file is
# scanned, and R3 then sees `PhysicalName` below with no owning-table token anywhere in it.
# C-TECH-069's IDENTITY clause governs "anything deciding whether a column is restricted", and
# resolution by (table, column) is what it requires. This gate decides whether a BUILDER EMITS A
# PROPERTY. It never reaches a column: the 19 names it handles are the LEFT-HAND keys of
# ConvertFrom-RevEntityXml's own pscustomobject literal — AttributeMetadata property keys, the same
# on every table — and the right-hand values behind them, which are where real column names like
# rev_name live, are never read. Confirmed by reading both files end to end on 2026-08-24: the only
# file this gate opens is ensure-schema-helpers.psm1, and it uses no XML parser at all.
# plurality-exempt: R3 the names handled here are AttributeMetadata property KEYS (PhysicalName, Type, IsSecured, ...) taken from the parser's own pscustomobject literal and matched against builder SOURCE TEXT; no column value and no table ever enters, so there is no (table, column) decision for a cross-table name collision to corrupt (IMP-0268)
#
# Scoped to this file deliberately. R3's own detection logic is untouched: a reader that really
# does collect per-instance attribute names with no owning table is still flagged, which is the
# regression this exemption was tested against before being added.

# A parsed property whose name differs from the property name sent to the Web API.
ALIASES: dict[str, tuple[str, ...]] = {
    "PhysicalName": ("SchemaName",),
    "Type": ("@odata.type", "AttributeTypeName", "AttributeType"),
    "OptionSetName": ("OptionSet", "GlobalOptionSet"),
    "IsGlobal": ("OptionSet", "GlobalOptionSet"),
}

# ── The three declarations ─────────────────────────────────────────────────────────────────
# NOT_APPLICABLE: the shape genuinely cannot carry the property. A reason is MANDATORY — an
# entry with an empty reason fails this gate, because "not applicable" with no argument is how
# a real gap gets filed as a non-problem.
NOT_APPLICABLE: dict[tuple[str, str], str] = {
    ("ConvertTo-RevRelationshipBody/$lookupBody", "MaxLength"):
        "a lookup stores a GUID reference, not text; LookupAttributeMetadata has no MaxLength",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "Format"):
        "StringFormat/IntegerFormat do not exist on LookupAttributeMetadata",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "DateTimeBehavior"):
        "DateTimeBehavior exists only on DateTimeAttributeMetadata",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "OptionSetName"):
        "a lookup has no option set; its target is ReferencedEntity on the relationship",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "IsGlobal"):
        "IsGlobal qualifies an option set, and a lookup has none",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "MinValue"):
        "numeric range does not apply to a GUID reference",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "MaxValue"):
        "numeric range does not apply to a GUID reference",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "Precision"):
        "decimal precision does not apply to a GUID reference",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "DefaultValue"):
        "Dataverse rejects a default value on a lookup column",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "AutoNumberFormat"):
        "autonumber applies to string columns only",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "SourceType"):
        "a calculated/rollup lookup is not a shape this solution creates",
    ("ConvertTo-RevRelationshipBody/$lookupBody", "Formula"):
        "a lookup is never a calculated column here",
}

# KNOWN_GAP: the builder SHOULD carry this property and does not. Warns every run. Each entry
# names the owner and the finding, so the warning is actionable rather than ambient.
KNOWN_GAP: dict[tuple[str, str], str] = {
    ("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"):
        "ConvertTo-RevAttributeBody emits IsAuditEnabled=@{Value=$false} to turn auditing OFF "
        "for a column that declares 0; the lookup body has no equivalent, so a lookup "
        "declaring IsAuditEnabled=0 would be created with auditing ON. LATENT TODAY: all 12 "
        "lookup columns in the solution declare 1, which is the default the builder assumes "
        "when it emits nothing. Owner: development-agent (one line in $lookupBody, the same "
        "shape as the IsSecured fix). Found by improvement review 23 measuring IMP-0255's "
        "class rather than its instance",
}


def _strip_comments(source: str) -> str:
    """Remove <# block #> and # line comments.

    Both carry these property names at length in this module — the header prose discusses
    IsSecured for twenty lines — and a marker inside a comment satisfying a structural check is
    its own recorded defect (IMP-0020).
    """
    source = re.sub(r"<#.*?#>", "", source, flags=re.S)
    return re.sub(r"(?m)^\s*#.*$", "", source)


def parsed_properties(source: str) -> list[str]:
    """The property names ConvertFrom-RevEntityXml puts on each parsed attribute.

    Read from the pscustomobject literal inside the attribute loop, so adding a property to the
    parser adds it here with no edit to this gate. That is the point: the gate must not carry
    its own copy of the list it is checking (IMP-0038, IMP-0069's family).
    """
    match = re.search(
        r"function\s+ConvertFrom-RevEntityXml\b(.*?)(?=\nfunction\s|\Z)", source, re.S)
    if match is None:
        return []
    body = match.group(1)
    # The attribute-level pscustomobject is the one carrying PhysicalName.
    for block in re.finditer(r"\[pscustomobject\]@\{(.*?)\n        \}", body, re.S):
        text = block.group(1)
        if "PhysicalName" not in text:
            continue
        return [m.group(1) for m in re.finditer(r"(?m)^\s{12}(\w+)\s*=", text)]
    return []


def builder_region(source: str, name: str) -> str | None:
    """The text of one builder, per its BUILDERS entry."""
    spec = BUILDERS[name]
    func = spec.get("function", name)
    match = re.search(rf"function\s+{re.escape(func)}\b(.*?)(?=\nfunction\s|\Z)", source, re.S)
    if match is None:
        return None
    body = match.group(1)
    if spec["kind"] == "function":
        return body
    var = spec["variable"]
    table = re.search(rf"\${var}\s*=\s*@\{{(.*?)\n    \}}", body, re.S)
    assigns = re.findall(rf"(?m)^.*\${var}\.\w+\s*=.*$", body)
    if table is None and not assigns:
        return None
    return (table.group(1) if table else "") + "\n" + "\n".join(assigns)


def references(region: str, prop: str) -> bool:
    """Does this builder region mention the property, under its own name or an alias?"""
    for candidate in (prop, *ALIASES.get(prop, ())):
        if re.search(rf"(?<![\w-]){re.escape(candidate)}(?![\w])", region):
            return True
    return False


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
    module = os.path.join(root, HELPERS)
    if not os.path.isfile(module):
        print(f"FAIL - {HELPERS} not found under '{root}'. This check is not allowed to pass "
              f"on a missing target (IMP-0007).")
        return 1

    with open(module, encoding="utf-8") as handle:
        source = _strip_comments(handle.read())

    props = parsed_properties(source)
    if not props:
        print(f"FAIL - could not read the parsed property list out of "
              f"ConvertFrom-RevEntityXml in {HELPERS}. The gate reads that list from source "
              f"rather than carrying a copy, so it cannot run without it.")
        return 1

    problems: list[str] = []
    warnings: list[str] = []
    checked = 0

    for builder, spec in BUILDERS.items():
        region = builder_region(source, builder)
        if region is None:
            problems.append(
                f"  BUILDER NOT FOUND - {builder} could not be located in {HELPERS}. Either it "
                f"was renamed (update BUILDERS in this gate) or the construction it names was "
                f"restructured. Not treated as a pass.")
            continue
        for prop in props:
            checked += 1
            key = (builder, prop)
            if references(region, prop):
                if key in NOT_APPLICABLE:
                    problems.append(
                        f"  STALE EXEMPTION - {builder} now references '{prop}', but this gate "
                        f"still lists it NOT_APPLICABLE ({NOT_APPLICABLE[key]}). Remove the "
                        f"exemption.")
                if key in KNOWN_GAP:
                    problems.append(
                        f"  GAP CLOSED, ENTRY LEFT BEHIND - {builder} now references '{prop}'. "
                        f"Delete its KNOWN_GAP entry so the ratchet holds.")
                continue
            if key in KNOWN_GAP:
                warnings.append(f"  KNOWN GAP - {builder} does not carry '{prop}'. "
                                f"{KNOWN_GAP[key]}")
                continue
            if key in NOT_APPLICABLE:
                if not NOT_APPLICABLE[key].strip():
                    problems.append(
                        f"  EXEMPTION WITHOUT A REASON - {builder}/'{prop}' is listed "
                        f"NOT_APPLICABLE with an empty reason. 'Not applicable' with no "
                        f"argument is how a real gap gets filed as a non-problem.")
                continue
            problems.append(
                f"  DECLARED BUT NEVER SENT - the parser reads '{prop}' off every attribute, "
                f"and {builder} (shape: {spec['shape']}) neither references it nor declares it "
                f"inapplicable. Source can declare '{prop}' and the platform will never receive "
                f"it: the column is created without it, every gate reading only source passes, "
                f"and the symptom appears at V3 or later. This is the IMP-0255 shape. Either "
                f"emit it, or add a NOT_APPLICABLE/KNOWN_GAP entry with a reason.")

    if problems:
        print(f"FAIL - a declared property does not reach the creation path "
              f"({len(problems)} problem(s)):")
        print("\n".join(problems))
        if warnings:
            print(f"\nWARNING ({len(warnings)}):")
            print("\n".join(warnings))
        return 1

    print(f"PASS - {len(props)} parsed propert(ies) x {len(BUILDERS)} builder(s) = {checked} "
          f"pair(s) checked; every one is emitted, or declared inapplicable with a reason "
          f"({len(NOT_APPLICABLE)} exemption(s)), or a recorded gap ({len(KNOWN_GAP)}).")
    if warnings:
        print(f"\nWARNING - {len(warnings)} property(ies) a builder should carry and does not. "
              f"Not a build failure; latent until a column declares one:")
        print("\n".join(warnings))
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# Fixtures 1-3 are inherited from verify-field-security-coverage.py, whose IsSecured-specific
# check this gate replaces. Per skills/how-to-promote-a-finding.md a generalisation that loses
# coverage is a regression, so the retired check's own known-bad shapes must still fail here.

_PARSER = """
function ConvertFrom-RevEntityXml {
    param($Path)
    $attributes = foreach ($attr in $attrs) {
        [pscustomobject]@{
            PhysicalName     = $attr.PhysicalName
            Type             = $attr.Type
            DisplayName      = $attr.displaynames.displayname.description
            RequiredLevel    = $requiredLevelText
            IsSecured        = ($attr.IsSecured -eq '1')
            IsAuditEnabled   = ($attr.IsAuditEnabled -eq '1')
{extra_parsed}        }
    }
}
"""

_ATTRIBUTE_BUILDER = """
function ConvertTo-RevAttributeBody {
    <# IsSecured is a plain Edm.Boolean. Formula and SourceType discussed here only. #>
    param($Attribute)
    if ($Attribute.Type -eq 'lookup') { throw 'lookup columns are created by the relationship' }
    $common = @{
        SchemaName    = $Attribute.PhysicalName
        DisplayName   = New-RevLabel -Text $Attribute.DisplayName
        RequiredLevel = New-RevRequiredLevel -Level $Attribute.RequiredLevel
        '@odata.type' = $odataType
    }
    if ($Attribute.IsSecured) { $common.IsSecured = $true }
    if (-not $Attribute.IsAuditEnabled) { $common.IsAuditEnabled = @{ Value = $false } }
{extra_attr}    return $common
}
"""

_RELATIONSHIP_BUILDER = """
function ConvertTo-RevRelationshipBody {
    <# The lookup body used to omit IsSecured. IsAuditEnabled is named in this comment too. #>
    param($Relationship, $LookupAttribute)
    $lookupBody = @{
        '@odata.type' = 'Microsoft.Dynamics.CRM.LookupAttributeMetadata'
        SchemaName    = $LookupAttribute.PhysicalName
        DisplayName   = New-RevLabel -Text $LookupAttribute.DisplayName
        RequiredLevel = New-RevRequiredLevel -Level $LookupAttribute.RequiredLevel
    }
{extra_lookup}    return @{
        SchemaName = $Relationship.SchemaName
        Lookup     = $lookupBody
    }
}
"""

_SETS_ISSECURED = "    if ($LookupAttribute.IsSecured) { $lookupBody.IsSecured = $true }\n"
_SETS_AUDIT = ("    if (-not $LookupAttribute.IsAuditEnabled) "
               "{ $lookupBody.IsAuditEnabled = @{ Value = $false } }\n")


def _tree(base: str, *, lookup_extra: str = "", parsed_extra: str = "",
          attr_extra: str = "", module: bool = True) -> str:
    root = os.path.join(base, "repo")
    if module:
        path = os.path.join(root, HELPERS)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = (_PARSER.replace("{extra_parsed}", parsed_extra)
                + _ATTRIBUTE_BUILDER.replace("{extra_attr}", attr_extra)
                + _RELATIONSHIP_BUILDER.replace("{extra_lookup}", lookup_extra))
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        os.makedirs(root, exist_ok=True)
    return root


def selftest() -> int:
    import contextlib
    import io

    # Each case: kwargs, expected rc, text that must appear, and a patch to the declarations.
    cases: list[tuple[str, dict, int, str, dict]] = [
        # ── inherited from the retired IsSecured-specific check ────────────────────────────
        # Both carry the real KNOWN_GAP entry for IsAuditEnabled, so these two fixtures turn on
        # IsSecured alone. Without it the first fixture fails for two reasons at once and the
        # second cannot pass at all — which is the gate being right about the live tree, not a
        # fixture being wrong, and it is worth keeping visible in the fixture set.
        ("dropped-issecured-must-fail",
         {"lookup_extra": ""}, 1, "DECLARED BUT NEVER SENT",
         {"gap": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "latent"}}),
        ("carried-issecured-must-pass",
         {"lookup_extra": _SETS_ISSECURED}, 0, "PASS",
         {"gap": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "latent"}}),
        ("missing-helpers-module-must-fail",
         {"module": False}, 1, "not found", {}),
        # ── the gap this gate found that no finding had recorded ───────────────────────────
        ("live-isauditenabled-gap-must-warn",
         {"lookup_extra": _SETS_ISSECURED}, 0, "KNOWN GAP",
         {"gap": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "latent"}}),
        ("gap-closed-but-entry-left-must-fail",
         {"lookup_extra": _SETS_ISSECURED + _SETS_AUDIT}, 1, "GAP CLOSED, ENTRY LEFT BEHIND",
         {"gap": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "latent"}}),
        # ── the exemption machinery must not become a rubber stamp ─────────────────────────
        ("exemption-without-a-reason-must-fail",
         {"lookup_extra": _SETS_ISSECURED}, 1, "EXEMPTION WITHOUT A REASON",
         {"na": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "   "}}),
        ("stale-exemption-must-fail",
         {"lookup_extra": _SETS_ISSECURED + _SETS_AUDIT}, 1, "STALE EXEMPTION",
         {"na": {("ConvertTo-RevRelationshipBody/$lookupBody", "IsAuditEnabled"): "claimed"}}),
        # ── a property newly added to the parser must fail until somebody decides ──────────
        ("new-parser-property-must-fail",
         {"lookup_extra": _SETS_ISSECURED + _SETS_AUDIT,
          "parsed_extra": "            Tier             = $tierText\n"},
         1, "DECLARED BUT NEVER SENT", {}),
        # ── a renamed builder must be reported, never skipped into a pass ──────────────────
        ("renamed-builder-must-fail",
         {"lookup_extra": _SETS_ISSECURED + _SETS_AUDIT}, 1, "BUILDER NOT FOUND",
         {"builders": True}),
    ]

    real_na, real_gap = dict(NOT_APPLICABLE), dict(KNOWN_GAP)
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, kwargs, want_rc, want_text, patch in cases:
            NOT_APPLICABLE.clear()
            NOT_APPLICABLE.update(patch.get("na", {}))
            KNOWN_GAP.clear()
            KNOWN_GAP.update(patch.get("gap", {}))
            renamed = patch.get("builders", False)
            if renamed:
                BUILDERS["ConvertTo-RevRenamedBody"] = {
                    "kind": "function", "shape": "gone"}
            root = _tree(os.path.join(tmp, name), **kwargs)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                rc = main(["verify-declared-property-reaches-creation-path.py", root])
            text = buffer.getvalue()
            if renamed:
                del BUILDERS["ConvertTo-RevRenamedBody"]
            ok = rc == want_rc and want_text in text
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in text.splitlines():
                    print(f"                   {line}")

    NOT_APPLICABLE.clear()
    NOT_APPLICABLE.update(real_na)
    KNOWN_GAP.clear()
    KNOWN_GAP.update(real_gap)

    if failures:
        print(f"\nverify-declared-property-reaches-creation-path: SELFTEST FAILED — "
              f"{', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nverify-declared-property-reaches-creation-path: SELFTEST OK — {len(cases)} "
          f"fixtures. The shape that reached a live environment fails, the exemption machinery "
          f"cannot be used as a rubber stamp, and a property newly added to the parser fails "
          f"until somebody decides in writing which of the three it is.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
