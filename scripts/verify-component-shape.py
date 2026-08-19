#!/usr/bin/env python3
"""Verify hand-authored solution components against their proven element shape.

WHY THIS EXISTS. `pac solution pack` validates a folder against its own layout rules, not
against what the target platform accepts. A hand-authored component can be well-formed XML,
pack cleanly with exit 0, and be rejected or silently ignored by Dataverse. That class —
`platform-contract-guessed-not-groundtruthed` — has seven recorded instances on this project
and is the most expensive one in the digest.

Two of them are the same defect and produced this gate:

  IMP-0045 (blocker)  An environmentvariabledefinition.xml authored with a leading XML
    declaration and an explanatory comment. Import failed FOUR TIMES with
    `0x80040216 — An unexpected error occurred` at ImportXml.GetComponentsList, naming no
    component, while the file stayed valid XML and pack exited 0 every time.

  IMP-0037 (rework)  An option set authored by copying a proven sibling's shape — read with
    `head -12`, which stops before the optionset-level <Descriptions> and <displaynames> that
    sit after </options>. Both were missing. Pack accepted that too.

ONE GATE, NOT TWO. `skills/how-to-promote-a-finding.md` §2: the second instance of a class may
not get its own instance patch. Both are "the authored element set differs from the one the
platform requires", so this reads a single reference table —
`constraints/technology/component-shapes.yml` — and every future component type is a block in
that file rather than another script. Nothing about either incident is transcribed into this
program (C-TECH-060's rule).

WHAT IT CHECKS, per shape block:
  * the file's root element is the declared one
  * `allow_prolog: false` — nothing whatsoever precedes the root element: no XML declaration,
    no comment, no processing instruction, no stray text
  * `required_children` — each named element exists as a DIRECT child of the root

Run:
    python3 scripts/verify-component-shape.py src/solutions/RevitaliseGrantAutomation

Exits 0 when every matched file conforms, 1 otherwise, 2 on a usage error. Fails — never
passes — when the solution root, the shapes file, or a shape's file set cannot be read, so it
cannot report OK over nothing (IMP-0007).

Wired into config/<slug>-build.yml as the `component-shape` step.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the CI job installs it explicitly
    print("verify-component-shape: FAILED — pyyaml is not installed "
          "(`python3 -m pip install pyyaml`).", file=sys.stderr)
    raise SystemExit(1)

DEFAULT_SHAPES = Path("constraints/technology/component-shapes.yml")

# Anything at all before the first `<rootname`. Captures the XML declaration, comments,
# processing instructions and stray text in one check, because the import reader accepts
# none of them and distinguishing between them would only invite an exception.
def leading_noise(text: str, root: str) -> str | None:
    marker = f"<{root}"
    index = text.find(marker)
    if index == -1:
        return None
    prefix = text[:index]
    return prefix if prefix.strip() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solution_root", type=Path,
                        help="path to the unpacked solution, e.g. src/solutions/<Name>")
    parser.add_argument("--shapes", type=Path, default=DEFAULT_SHAPES)
    args = parser.parse_args(argv)

    if not args.solution_root.is_dir():
        print(f"component-shape: FAILED — '{args.solution_root}' is not a directory. A gate "
              f"pointed at a missing target does not pass (IMP-0007).", file=sys.stderr)
        return 1

    if not args.shapes.is_file():
        print(f"component-shape: FAILED — shapes file '{args.shapes}' does not exist. A shape "
              f"gate with no reference table checks nothing.", file=sys.stderr)
        return 1

    try:
        config = yaml.safe_load(args.shapes.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"component-shape: FAILED — '{args.shapes}' is not valid YAML: {exc}",
              file=sys.stderr)
        return 1

    shapes = (config or {}).get("shapes") or []
    if not shapes:
        print(f"component-shape: FAILED — '{args.shapes}' declares no shapes.", file=sys.stderr)
        return 1

    errors: list[str] = []
    checked = 0

    for shape in shapes:
        name = shape.get("name", "(unnamed shape)")
        pattern = shape.get("glob")
        root_name = shape.get("root")
        if not pattern or not root_name:
            errors.append(f"shape '{name}': both 'glob' and 'root' are required.")
            continue

        paths = sorted(glob.glob(os.path.join(str(args.solution_root), pattern), recursive=True))
        if not paths:
            # A shape whose file set is empty is either a component type this solution no
            # longer has (remove the block) or a glob that stopped matching (a silent hole).
            # Neither is a pass.
            errors.append(
                f"shape '{name}': glob '{pattern}' matched no files under "
                f"{args.solution_root}. Either the component type is gone — remove the block "
                f"from {args.shapes} — or the glob has drifted and this shape has been "
                f"checking nothing."
            )
            continue

        for path in paths:
            rel = os.path.relpath(path)
            checked += 1
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{rel}: could not be read — {exc}")
                continue

            try:
                element = ET.fromstring(text)
            except ET.ParseError as exc:
                errors.append(f"{rel}: not well-formed XML — {exc}")
                continue

            if element.tag != root_name:
                errors.append(f"{rel}: root element is <{element.tag}>, expected "
                              f"<{root_name}> ({name}).")
                continue

            if shape.get("allow_prolog") is False:
                noise = leading_noise(text, root_name)
                if noise is not None:
                    snippet = " ".join(noise.split())[:90]
                    note = str(shape.get("prolog_note") or "").strip().replace("\n", " ")
                    errors.append(
                        f"{rel}: content precedes the root element — \"{snippet}…\". {note}"
                    )

            missing = [child for child in (shape.get("required_children") or [])
                       if element.find(child) is None]
            if missing:
                note = str(shape.get("children_note") or "").strip().replace("\n", " ")
                errors.append(
                    f"{rel}: missing required direct child element(s) of <{root_name}>: "
                    f"{', '.join('<' + m + '>' for m in missing)}. {note}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\ncomponent-shape: FAILED — {len(errors)} problem(s) across {checked} "
              f"hand-authored component file(s). `pac solution pack` accepts every one of "
              f"these and exits 0; the target does not.", file=sys.stderr)
        return 1

    print(f"component-shape: OK — {checked} component file(s) match the "
          f"{len(shapes)} shape(s) declared in {args.shapes}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
