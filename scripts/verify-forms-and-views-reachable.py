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
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.tracked_paths import (  # noqa: E402
    IgnoreCheckUnavailable, describe_untracked, untracked_paths,
)

# GATE-INPUT-TRACKING: reads the WORKING TREE on purpose (authoring-time gate) and REPORTS its
# untracked inputs rather than dropping them — see scripts/lib/tracked_paths.py, "TWO INPUT
# UNIVERSES" (IMP-0437). --committed-only reproduces CI's verdict when that is what is wanted.


def gate_inputs(entity_dirs: list[str]) -> list[Path]:
    """Every file whose presence or absence can change this gate's verdict.

    That is the Entity.xml it reads AND the FormXml/SavedQueries content it counts — the counting
    is the half `IMP-0437` was about: three untracked view/form files silenced two warnings that
    CI still emitted, so the gate's own inputs are what must be reported, not just its outputs.
    """
    inputs: list[Path] = []
    for entity_dir in entity_dirs:
        entity_xml = Path(entity_dir) / "Entity.xml"
        if entity_xml.is_file():
            inputs.append(entity_xml)
        for folder_name in ("FormXml", "SavedQueries"):
            folder = os.path.join(entity_dir, folder_name)
            inputs.extend(sorted(
                Path(p) for p in glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True)))
    return inputs


def find_entity_dirs(solution_root: str) -> list[str]:
    entities_root = os.path.join(solution_root, "Entities")
    if not os.path.isdir(entities_root):
        return []
    return sorted(
        os.path.join(entities_root, name)
        for name in os.listdir(entities_root)
        if os.path.isdir(os.path.join(entities_root, name))
    )


def count_xml_files(folder: str, skip: set[Path] | None = None) -> int:
    if not os.path.isdir(folder):
        return 0
    found = glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True)
    if skip:
        found = [p for p in found if Path(p) not in skip]
    return len(found)


def strip_comments(xml_text: str) -> str:
    """Remove XML comments before any structural check.

    IMP-0020 (2026-08-17): `has_marker` regexed the RAW file text, so an `<FormXml />`
    appearing inside an XML *comment* satisfied the gate and the real, missing marker went
    unreported — the exact "packs clean, ships nothing" defect this script exists to catch
    (D-018), reintroduced through the gate's own back door. Found while building the
    known-bad fixture for this gate: the fixture's comment said which elements it was
    deliberately omitting, named them in tag form, and the gate passed.

    No real Entity.xml in this solution was affected at the time of the fix (all four
    carry genuine markers), so this closes a latent hole rather than a live defect. It is
    exactly the class of hole that only a negative test finds:
    docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §2.5.
    """
    return re.sub(r"<!--.*?-->", "", xml_text, flags=re.S)


def has_marker(entity_xml_text: str, element: str) -> bool:
    # Matches both the empty self-closing form (<FormXml />) that every real DEV export
    # uses and, defensively, a non-self-closing empty element (<FormXml></FormXml>) —
    # never a populated one: this project's Entity.xml files never inline form/view
    # content (see the D-018 fix comment in each Entity.xml), so presence of the tag at
    # all is the only thing that matters here. Comments are stripped first — see above.
    pattern = rf"<{element}\s*/>|<{element}>\s*</{element}>"
    return re.search(pattern, strip_comments(entity_xml_text)) is not None


def main(solution_root: str, committed_only: bool = False) -> int:
    entity_dirs = find_entity_dirs(solution_root)
    if not entity_dirs:
        print(f"No Entities/ folder found under {solution_root}", file=sys.stderr)
        return 1

    # IMP-0437. Resolve the tracked/untracked split BEFORE deciding anything, so the verdict can
    # say which universe produced it. Failing open keeps the pre-helper behaviour.
    repo_root = Path(__file__).resolve().parent.parent
    untracked: set[Path] = set()
    split_unavailable: str | None = None
    try:
        untracked = untracked_paths(gate_inputs(entity_dirs), repo_root)
    except IgnoreCheckUnavailable as exc:
        split_unavailable = str(exc)

    if committed_only and split_unavailable:
        print(f"forms-and-views-reachable: FAILED — --committed-only cannot be honoured: "
              f"{split_unavailable}. Refusing to report a commit-scoped verdict computed from "
              "the working tree.", file=sys.stderr)
        return 1

    skip = untracked if committed_only else set()

    errors: list[str] = []
    warnings: list[str] = []
    checked = 0

    entities_considered = 0
    for entity_dir in entity_dirs:
        entity_name = os.path.basename(entity_dir)
        entity_xml_path = os.path.join(entity_dir, "Entity.xml")
        if not os.path.isfile(entity_xml_path):
            errors.append(f"{entity_name}: no Entity.xml found")
            continue
        if Path(entity_xml_path) in skip:
            # --committed-only: this whole table is not in the commit, so CI does not see it.
            continue
        entities_considered += 1

        with open(entity_xml_path, encoding="utf-8") as fh:
            entity_xml_text = fh.read()

        for element, folder_name in (("FormXml", "FormXml"), ("SavedQueries", "SavedQueries")):
            checked += 1
            folder = os.path.join(entity_dir, folder_name)
            file_count = count_xml_files(folder, skip)
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

    # IMP-0437. The scope line goes with EVERY verdict, pass or fail, because the number a reader
    # transcribes is printed on both paths. Naming the files is the whole control: a bare count is
    # what got copied into a Dev Summary and disagreed with CI.
    if committed_only:
        scope = (f"scope: COMMIT — {len(untracked)} untracked input(s) excluded, "
                 f"{entities_considered} entities considered. Comparable to CI.")
    elif split_unavailable:
        scope = ("scope: WORKING TREE — tracked/untracked split UNAVAILABLE "
                 f"({split_unavailable}), so this verdict may differ from CI and nothing here "
                 "can say whether it does. Do not transcribe these counts.")
    elif untracked:
        scope = (f"scope: WORKING TREE — {len(untracked)} UNTRACKED input(s) read as if "
                 "delivered, so this verdict may differ from CI. Do not transcribe these counts "
                 "as a claim about delivered source; re-run with --committed-only for CI's "
                 "verdict (IMP-0437).")
    else:
        scope = ("scope: WORKING TREE — every input is tracked, so this verdict matches the "
                 "commit.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"\nforms-and-views-reachable: FAILED — {len(errors)} of {checked} "
            f"entity/element checks would silently drop content at pack time. {scope}",
            file=sys.stderr,
        )
        for line in describe_untracked(sorted(untracked), repo_root):
            print(line, file=sys.stderr)
        return 1

    print(f"forms-and-views-reachable: OK — {checked} entity/element checks, "
          f"{len(warnings)} warning(s), across "
          f"{entities_considered if committed_only else len(entity_dirs)} entities. {scope}")
    for line in describe_untracked(sorted(untracked), repo_root):
        print(line)
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--committed-only"]
    if len(args) != 1:
        print(f"Usage: {sys.argv[0]} [--committed-only] <solution-root>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(args[0], committed_only="--committed-only" in sys.argv[1:]))
