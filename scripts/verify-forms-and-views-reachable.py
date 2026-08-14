#!/usr/bin/env python3
"""Verify that every entity's FormXml/ and SavedQueries/ folder is actually reachable.

D-018 (2026-08-14): `pac solution pack` silently drops every file under an entity's
SavedQueries/ and FormXml/ folders unless that entity's Entity.xml also declares the two
empty marker elements <FormXml /> and <SavedQueries />. Without them, the pack SUCCEEDS,
the import SUCCEEDS, and the component simply never reaches the target environment — the
same "packs clean, ships nothing" failure class as the root-components check next to this
one, and the reason this solution shipped to DEV with 0 views and 0 forms on all four tables
despite 8 SavedQueries files and 4 FormXml files sitting on disk the whole time. Confirmed by
direct experiment (see docs/development/revitalise-grant-automation-dev-deployment-handover.md
section 6 and Dev Summary revision 1.0, D-018) and ground-truthed against a real DEV
export, which carries the same two elements on every entity.

This script asserts BOTH directions, exactly like verify-solution-root-components.py does for
RootComponents:

* An entity with a SavedQueries/ or FormXml/ folder containing at least one *.xml file, but
  without the matching marker element in Entity.xml, packs that folder's content to nothing —
  caught here, not fifteen import attempts later.
* An entity declaring a marker element with no matching folder (or an empty one) is not
  actually wrong — Dataverse accepts an empty <FormXml />/<SavedQueries /> exactly as it
  accepts a table with only default forms/views — but is flagged as a warning: it is either a
  no-op marker or a component someone meant to add and forgot to.

Run:
    python3 scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation

Exits 0 when every folder with content is reachable, 1 otherwise. Wired into
config/<slug>-build.yml as the ``forms-and-views-reachable`` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys


def find_entity_dirs(solution_root: str) -> list[str]:
    entities_root = os.path.join(solution_root, "Entities")
    if not os.path.isdir(entities_root):
        return []
    return sorted(
        os.path.join(entities_root, name)
        for name in os.listdir(entities_root)
        if os.path.isdir(os.path.join(entities_root, name))
    )


def count_xml_files(folder: str) -> int:
    if not os.path.isdir(folder):
        return 0
    return len(glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True))


def has_marker(entity_xml_text: str, element: str) -> bool:
    # Matches both the empty self-closing form (<FormXml />) that every real DEV export
    # uses and, defensively, a non-self-closing empty element (<FormXml></FormXml>) —
    # never a populated one: this project's Entity.xml files never inline form/view
    # content (see the D-018 fix comment in each Entity.xml), so presence of the tag at
    # all is the only thing that matters here.
    pattern = rf"<{element}\s*/>|<{element}>\s*</{element}>"
    return re.search(pattern, entity_xml_text) is not None


def main(solution_root: str) -> int:
    entity_dirs = find_entity_dirs(solution_root)
    if not entity_dirs:
        print(f"No Entities/ folder found under {solution_root}", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    checked = 0

    for entity_dir in entity_dirs:
        entity_name = os.path.basename(entity_dir)
        entity_xml_path = os.path.join(entity_dir, "Entity.xml")
        if not os.path.isfile(entity_xml_path):
            errors.append(f"{entity_name}: no Entity.xml found")
            continue

        with open(entity_xml_path, encoding="utf-8") as fh:
            entity_xml_text = fh.read()

        for element, folder_name in (("FormXml", "FormXml"), ("SavedQueries", "SavedQueries")):
            checked += 1
            folder = os.path.join(entity_dir, folder_name)
            file_count = count_xml_files(folder)
            marker_present = has_marker(entity_xml_text, element)

            if file_count > 0 and not marker_present:
                errors.append(
                    f"{entity_name}: {folder_name}/ has {file_count} file(s) but Entity.xml "
                    f"declares no <{element} /> marker — pac solution pack will drop all of "
                    f"them silently (D-018). Add <{element} /> before </Entity>."
                )
            elif marker_present and file_count == 0:
                warnings.append(
                    f"{entity_name}: Entity.xml declares <{element} /> but {folder_name}/ has "
                    "no files (or does not exist) — harmless, but confirm this is intentional."
                )

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"\nforms-and-views-reachable: FAILED — {len(errors)} of {checked} "
            "entity/element checks would silently drop content at pack time.",
            file=sys.stderr,
        )
        return 1

    print(f"forms-and-views-reachable: OK — {checked} entity/element checks, "
          f"{len(warnings)} warning(s), across {len(entity_dirs)} entities.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <solution-root>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
