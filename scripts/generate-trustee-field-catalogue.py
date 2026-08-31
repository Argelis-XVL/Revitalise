#!/usr/bin/env python3
"""Generate the trustee portal's restricted-field catalogue (ADR-032, FR-078, TAD §3.2.3).

WHY THIS EXISTS. Amendment A-05 puts eleven `REV_TrusteeRestricted` columns on the trustee
detail screen's board pack — benefit status, employment status, and the helper/referee/
emergency-contact identity columns. ADR-032 decided the app must NEVER query any of them
(the process owner IS a profile member, so binding them would show her their real values on
a screen designed to be anonymous, and `no-secured-columns-in-code-app` would fail the build
on the reference anyway). Instead FR-078's "explicit restricted state that names the field"
is rendered from a static catalogue — label, board-pack group, `restricted: true` — with NO
`$select` naming a secured column anywhere.

ADR-032's own stated cost: "a column later removed from `REV_TrusteeRestricted` would keep
rendering as restricted until someone edits the catalogue... the mitigation is to derive it
at build time... rather than hand-typed." This script is that derivation, using the IDENTICAL
technique `scripts/verify-code-app-column-bindings.py` already uses for its own forbidden
set: read `Other/FieldSecurityProfiles.xml` at generation time and FAIL LOUDLY if the ground
truth has moved out from under the catalogue, rather than silently emitting stale output.

WHAT "DERIVED" MEANS HERE, PRECISELY. Which eleven (entity, column) pairs belong on the
trustee detail screen, and which of the SDD §7.1b board-pack groups each belongs to, is a
requirements decision this script cannot read off any XML file — nothing in solution source
encodes "this column is one of Amendment A-05's board-pack fields." So the eleven pairs are a
short, OWNED manifest below, cited to SDD §7.1b Amendment A-05, Finding 1. What IS derived,
and never hand-typed, is everything that could silently drift:

  1. That each pair is actually secured, still, in `REV_TrusteeRestricted` — read from
     `Other/FieldSecurityProfiles.xml` at generation time. A pair the manifest lists but the
     profile no longer secures FAILS this script rather than shipping a false "restricted"
     claim for a column that has since been declassified.
  2. Each column's LABEL — read from the column's own `<displayname>` in
     `Entities/rev_application/Entity.xml`, never typed here, so a rename in solution source
     flows through on the next run (the same convention `schema.ts`'s option-label maps
     already use for choice values, applied here to a column's own display name).

WHAT IS DELIBERATELY NOT IN THE OUTPUT. The generated file carries NO Dataverse logical
column name — only a stable, app-chosen `key`, a `label` and a `group`. Two reasons: (1) the
catalogue has no runtime use for the raw name (nothing is ever queried, so there is nothing
to look up by it), and (2) it means the shipped app bundle never contains the literal
secured-column strings at all, which is a stronger property than merely being excluded from
`no-secured-columns-in-code-app`'s scan.

Usage
-----
    python3 scripts/generate-trustee-field-catalogue.py \\
        --profile src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml \\
        --entities src/solutions/RevitaliseGrantAutomation/Entities \\
        --out src/code-apps/trustee-review-portal/src/generated/trusteeRestrictedFieldCatalogue.ts

    --check   Regenerate in memory and diff against the committed --out file; exit 1 if the
              committed file is stale, missing, or the manifest no longer matches ground
              truth. Wired into config/revitalise-grant-automation-build.yml as the
              `trustee-field-catalogue` step, BEFORE `no-secured-columns-in-code-app` and
              before typecheck/build (the app imports the generated file).

Exits 0 clean · 1 on any drift or validation failure · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROFILE_NAME = "REV_TrusteeRestricted"
ENTITY_NAME = "rev_application"

# The owned manifest — SDD `docs/plans/revitalise-grant-automation-plan.md` §7.1b, Amendment
# A-05 Finding 1. (key, column, group). `column` is the Dataverse logical name used ONLY to
# cross-check ground truth below; it is NEVER written to the generated output.
MANIFEST: tuple[tuple[str, str, str], ...] = (
    ("benefit-status", "rev_receivesbenefits", "Financial eligibility"),
    ("benefit-provider", "rev_benefitprovider", "Financial eligibility"),
    ("employment-status", "rev_employmentstatus", "Financial eligibility"),
    ("helper-name", "rev_helpername", "Helper, referee and emergency contact"),
    ("helper-email", "rev_helperemail", "Helper, referee and emergency contact"),
    ("helper-phone", "rev_helperphone", "Helper, referee and emergency contact"),
    ("referee-name", "rev_refereename", "Helper, referee and emergency contact"),
    ("referee-email", "rev_refereeemail", "Helper, referee and emergency contact"),
    ("referee-phone", "rev_refereephone", "Helper, referee and emergency contact"),
    ("emergency-contact-name", "rev_emergencycontactname", "Helper, referee and emergency contact"),
    ("emergency-contact-phone", "rev_emergencycontactphone", "Helper, referee and emergency contact"),
)

GROUP_ORDER = ("Financial eligibility", "Helper, referee and emergency contact")

HEADER = """/*
 * GENERATED — do not hand-edit. Regenerate with
 * `python3 scripts/generate-trustee-field-catalogue.py` (see that script's docstring)
 * after any change to Other/FieldSecurityProfiles.xml or Entities/rev_application/Entity.xml.
 * CI and the `trustee-field-catalogue` build step verify it is current with `--check`.
 *
 * ADR-032, FR-078, TAD §3.2.3 — the eleven `REV_TrusteeRestricted` columns Amendment A-05
 * puts on the trustee detail screen's board pack, rendered as a restricted state WITHOUT
 * ever being queried. This file is NOT `pac`/`pa` CLI output (unlike its siblings under
 * src/generated/) — it lives here because that directory is the one place this app's own
 * build gate (`no-secured-columns-in-code-app`) already treats as generator output.
 *
 * Deliberately carries NO Dataverse logical column name — see the generation script's
 * docstring for why. `restricted` is always `true`; it is a literal here, not a query result.
 */

export interface TrusteeRestrictedFieldCatalogueEntry {
  readonly key: string;
  readonly label: string;
  readonly group: string;
  readonly restricted: true;
}

export const TRUSTEE_RESTRICTED_FIELD_CATALOGUE: readonly TrusteeRestrictedFieldCatalogueEntry[] = [
"""

FOOTER = "] as const;\n"


def secured_pairs(profile_path: Path) -> set[tuple[str, str]]:
    tree = ET.parse(profile_path)
    pairs: set[tuple[str, str]] = set()
    for profile in tree.getroot().iter("FieldSecurityProfile"):
        if profile.get("name") != PROFILE_NAME:
            continue
        for permission in profile.iter("FieldPermission"):
            entity = (permission.findtext("EntityName") or "").strip()
            column = (permission.findtext("AttributeName") or "").strip()
            if entity and column:
                pairs.add((entity, column))
    return pairs


def entity_display_names(entity_path: Path) -> dict[str, str]:
    """PhysicalName -> displayname, for every attribute in one Entity.xml."""
    tree = ET.parse(entity_path)
    names: dict[str, str] = {}
    for attribute in tree.getroot().iter("attribute"):
        physical = attribute.get("PhysicalName")
        if not physical:
            continue
        displaynames = attribute.find("displaynames")
        if displaynames is None:
            continue
        displayname = displaynames.find("displayname")
        if displayname is None:
            continue
        label = displayname.get("description")
        if label:
            names[physical] = label
    return names


def build_entries(profile_path: Path, entities_root: Path) -> list[tuple[str, str, str]]:
    """Returns (key, label, group) triples, validated against ground truth. Raises on drift."""
    if not profile_path.is_file():
        raise SystemExit(
            f"trustee-field-catalogue: FAILED — {profile_path} does not exist, so the "
            "manifest cannot be validated against ground truth."
        )
    entity_path = entities_root / ENTITY_NAME / "Entity.xml"
    if not entity_path.is_file():
        raise SystemExit(
            f"trustee-field-catalogue: FAILED — {entity_path} does not exist, so no column "
            "label can be derived."
        )

    pairs = secured_pairs(profile_path)
    if not pairs:
        raise SystemExit(
            f"trustee-field-catalogue: FAILED — {profile_path} declares no FieldPermission "
            f"under '{PROFILE_NAME}'. A gate that finds nothing to validate against must not "
            "pass over it (IMP-0007)."
        )
    labels = entity_display_names(entity_path)

    errors: list[str] = []
    entries: list[tuple[str, str, str]] = []
    for key, column, group in MANIFEST:
        if (ENTITY_NAME, column) not in pairs:
            errors.append(
                f"'{column}' (key '{key}') is in this script's manifest but is NOT secured "
                f"under '{PROFILE_NAME}' in {profile_path} any more. Either it was "
                "declassified (remove it from MANIFEST and re-derive the app's Group-A "
                "column list) or the profile regressed (a security defect, not a catalogue "
                "one)."
            )
            continue
        label = labels.get(column)
        if not label:
            errors.append(
                f"'{column}' (key '{key}') has no <displayname> in {entity_path}, so no "
                "label can be derived without hand-typing one."
            )
            continue
        entries.append((key, label, group))

    if errors:
        raise SystemExit(
            "trustee-field-catalogue: FAILED — " + "; ".join(errors)
        )

    # Stable, deterministic order: the SDD §7.1b group order, then the manifest's own order
    # within a group (which is itself already grouped) — never alphabetical, which would
    # separate "Helper Name" from "Helper Email" from the referee/emergency rows they are
    # meant to sit beside.
    order = {group: index for index, group in enumerate(GROUP_ORDER)}
    entries.sort(key=lambda entry: order.get(entry[2], len(order)))
    return entries


def render(entries: list[tuple[str, str, str]]) -> str:
    lines = [HEADER]
    for key, label, group in entries:
        lines.append(
            "  { key: "
            + ts_string(key)
            + ", label: "
            + ts_string(label)
            + ", group: "
            + ts_string(group)
            + ", restricted: true },\n"
        )
    lines.append(FOOTER)
    return "".join(lines)


def ts_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        default="src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml",
    )
    parser.add_argument(
        "--entities", default="src/solutions/RevitaliseGrantAutomation/Entities"
    )
    parser.add_argument(
        "--out",
        default=(
            "src/code-apps/trustee-review-portal/src/generated/"
            "trusteeRestrictedFieldCatalogue.ts"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the committed --out file is stale or missing, rather than writing it.",
    )
    args = parser.parse_args(argv[1:])

    try:
        entries = build_entries(Path(args.profile), Path(args.entities))
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 1

    content = render(entries)
    out_path = Path(args.out)

    if args.check:
        if not out_path.is_file():
            print(
                f"trustee-field-catalogue: FAILED — {out_path} does not exist. Run "
                "`python3 scripts/generate-trustee-field-catalogue.py` and commit the result.",
                file=sys.stderr,
            )
            return 1
        current = out_path.read_text(encoding="utf-8")
        if current != content:
            print(
                f"trustee-field-catalogue: FAILED — {out_path} is stale against "
                f"{args.profile} and {args.entities}/{ENTITY_NAME}/Entity.xml. Re-run "
                "`python3 scripts/generate-trustee-field-catalogue.py` and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(
            f"trustee-field-catalogue: OK — {out_path} matches {len(entries)} validated "
            f"entr{'y' if len(entries) == 1 else 'ies'} across {len(GROUP_ORDER)} group(s)."
        )
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"trustee-field-catalogue: wrote {len(entries)} entries to {out_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
