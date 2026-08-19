#!/usr/bin/env python3
"""Assert that shipped solution content is REACHABLE and CONSISTENT, not merely well-formed.

WHY THIS EXISTS. This project has a class of defect called `no-assertion-on-shipped-content`,
recorded four times. Every instance is the same shape: a component that packs cleanly, imports
cleanly, passes every structural gate — and is still wrong or unusable when a human looks at it.

  IMP-0052  rev_grant shipped with a main form and three saved queries and NO SubArea in the
            app's site map. Nothing could navigate to any of it. `forms-and-views-reachable`
            passed, because it asks whether the PACKER will keep the form — a different
            question from whether a PERSON can reach it. Confirmed by the reviewer on
            2026-08-19 as a real defect: "the grant table and views/forms should have been
            available in the model driven app."

  IMP-0008  A shipped <Description> still named `rev_carersupport`, a column deleted in the
            same build. Prose inside metadata is shipped content too, and nothing reads it.

  IMP-0015  Eleven scored-answer fields carried generic form labels ("Wellbeing Answer 1")
            instead of the real survey questions. Structurally perfect, semantically wrong.

ONE GATE, NOT THREE. `skills/how-to-promote-a-finding.md` §2 forbids giving the fourth instance
of a class its own instance patch. Checks 1 and 2 below are implemented; check 3 is declared
and NOT silently omitted — see NOT_YET_IMPLEMENTED at the bottom of this docstring.

WHAT IT CHECKS.

  1. NAVIGABILITY (IMP-0052) — every entity that ships a FormXml/ or SavedQueries/ folder
     appears as a SubArea in at least one AppModuleSiteMap, unless the entity is listed in
     `headless_entities` in the shapes file. Adding a table is TWO changes; this is the second.

  2. NO DANGLING COLUMN REFERENCES (IMP-0008) — no <Description> or <displayname> text
     anywhere in the solution names a `<prefix>_` column that does not exist in any Entity.xml.
     Prose in metadata ships to the environment and is read by makers.

  NOT_YET_IMPLEMENTED — form label TEXT vs the attribute's own authored displayname (IMP-0015).
  It needs a rule for which of the two wins when they legitimately differ (a form may shorten a
  long column label on purpose), and that is a decision, not a lookup. Declared here rather
  than omitted, so the gap is visible: `IMP-0015` stays open with this script named as its home.

Run:
    python3 scripts/verify-shipped-content.py src/solutions/RevitaliseGrantAutomation

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when the
solution root has no entities or no site map, so it cannot report OK over nothing (IMP-0007).

Wired into config/<slug>-build.yml as the `shipped-content` step.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Entities that legitimately have no navigation. Kept here rather than in a separate file
# because it is two lines and belongs beside the check that reads it; promote it to the
# shapes file if it ever grows past a handful.
HEADLESS_ENTITIES: set[str] = set()

COLUMN_REF = re.compile(r"\b(rev_[a-z0-9]+)\b")


def entities_with_ui(solution_root: Path) -> dict[str, list[str]]:
    """entity -> the UI folders it ships (FormXml, SavedQueries)."""
    found: dict[str, list[str]] = {}
    for entity_dir in sorted(Path(solution_root, "Entities").glob("*")):
        if not entity_dir.is_dir():
            continue
        kinds = []
        for kind in ("FormXml", "SavedQueries"):
            sub = entity_dir / kind
            if sub.is_dir() and any(sub.rglob("*.xml")):
                kinds.append(kind)
        if kinds:
            found[entity_dir.name] = kinds
    return found


def sitemap_entities(solution_root: Path) -> tuple[set[str], int]:
    """Every entity referenced by a SubArea, across every app module site map."""
    referenced: set[str] = set()
    maps = sorted(Path(solution_root, "AppModuleSiteMaps").rglob("*.xml"))
    for path in maps:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for sub in root.iter("SubArea"):
            entity = sub.get("Entity")
            if entity:
                referenced.add(entity.strip())
            # A SubArea may reach an entity only through a Url= querystring.
            url = sub.get("Url") or ""
            for match in re.finditer(r"etn=([a-z0-9_]+)", url):
                referenced.add(match.group(1))
    return referenced, len(maps)


def declared_columns(solution_root: Path) -> set[str]:
    columns: set[str] = set()
    for path in sorted(Path(solution_root, "Entities").glob("*/Entity.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for attribute in root.iter("attribute"):
            name = (attribute.findtext("LogicalName")
                    or attribute.get("PhysicalName") or "").strip().lower()
            if name:
                columns.add(name)
    return columns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solution_root", type=Path)
    parser.add_argument("--allow-headless", nargs="*", default=[],
                        help="entities that deliberately have no navigation")
    args = parser.parse_args(argv)

    if not args.solution_root.is_dir():
        print(f"shipped-content: FAILED — '{args.solution_root}' is not a directory. A gate "
              f"pointed at a missing target does not pass (IMP-0007).", file=sys.stderr)
        return 1

    errors: list[str] = []
    headless = HEADLESS_ENTITIES | {e.strip() for e in args.allow_headless if e.strip()}

    # ── 1. Navigability (IMP-0052) ──────────────────────────────────────────────────────
    ui = entities_with_ui(args.solution_root)
    if not ui:
        print(f"shipped-content: FAILED — no entity under '{args.solution_root}/Entities' "
              f"ships a FormXml/ or SavedQueries/ folder. A gate with no scannable surface "
              f"must fail rather than report OK (IMP-0007).", file=sys.stderr)
        return 1

    referenced, n_maps = sitemap_entities(args.solution_root)
    if n_maps == 0:
        errors.append(f"no AppModuleSiteMaps/**/*.xml found under '{args.solution_root}'. "
                      f"Every entity below would be trivially 'unreachable', so this gate "
                      f"refuses to guess.")
    else:
        for entity, kinds in sorted(ui.items()):
            if entity in headless or entity in referenced:
                continue
            errors.append(
                f"NAVIGABILITY — {entity} ships {' and '.join(kinds)} but appears in no "
                f"SubArea of any app site map, so nobody can reach it in the app. Adding a "
                f"table is TWO changes: the entity, and a SubArea in "
                f"AppModuleSiteMaps/. (IMP-0052 — this shipped once, in WBS 0.4, and was "
                f"found by the reviewer.) If it is deliberately headless, pass it to "
                f"--allow-headless with a reason in the build config."
            )

    # ── 2. No dangling column references in shipped prose (IMP-0008) ────────────────────
    columns = declared_columns(args.solution_root)
    if not columns:
        errors.append("no attributes found in any Entity.xml — cannot check shipped prose "
                      "for references to deleted columns.")
    else:
        for path in sorted(Path(args.solution_root).rglob("*.xml")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for element_name in ("Description", "description", "displayname", "DisplayName"):
                for match in re.finditer(
                        rf'<{element_name}[^>]*\b(?:description|default)="([^"]*)"', text):
                    prose = match.group(1)
                    for ref in set(COLUMN_REF.findall(prose)):
                        if ref.lower() in columns:
                            continue
                        # Entity and option-set names share the prefix; they are not columns.
                        if (Path(args.solution_root, "Entities", ref).is_dir()
                                or Path(args.solution_root, "OptionSets", ref + ".xml").is_file()):
                            continue
                        errors.append(
                            f"DANGLING REFERENCE — {os.path.relpath(path)}: shipped "
                            f"<{element_name}> prose names '{ref}', which is not a column in "
                            f"any Entity.xml, not an entity and not an option set. A "
                            f"description naming a deleted column ships to every environment "
                            f"and is read by makers (IMP-0008)."
                        )

    if errors:
        for error in sorted(set(errors)):
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nshipped-content: FAILED — {len(set(errors))} problem(s). These are defects "
              f"a packer and an import both accept.", file=sys.stderr)
        return 1

    print(f"shipped-content: OK — {len(ui)} entity(ies) with UI, all reachable across "
          f"{n_maps} site map(s); shipped prose references only columns that exist.")
    if headless:
        print(f"  deliberately headless: {', '.join(sorted(headless))}")
    print(f"  NOT CHECKED: form label TEXT vs the attribute's authored displayname "
          f"(IMP-0015) — needs a precedence rule, see this script's docstring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
