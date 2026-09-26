#!/usr/bin/env python3
"""Verify a packed solution's <forms type> wrapper matches its split source, per form.

WHY THIS EXISTS (IMP-0874, blocker). `pac solution pack`'s SolutionPackager derives the
packed `customizations.xml` `<forms type="...">` WRAPPER attribute for a form from the
`FormXml/<foldername>/` PATH SEGMENT of the source tree — NOT from the split source file's
own root `<forms type>` attribute. `verify-component-shape.py`'s `entity form` shape
(`constraints/technology/component-shapes.yml`) reads only the split SOURCE files, with
`xml.etree.ElementTree`, over `Entities/*/FormXml/*/*.xml` — so it correctly reports a
corrected source attribute as OK, even when the containing folder still carries the old
name and the packer keeps emitting the old value into every artifact this build produces.
IMP-0867 corrected three FormXml files' own `type` attribute from `quickview` to `quick`
and closed A-QVF-1 on that basis; the packed artifact still shipped `type="quickview"` for
all three, reproducing the live DEV import failure IMP-0866 recorded, and nothing before
this gate ever opened the packed zip to notice.

This is the `gate-scope-mismatch` class (`logs/known-failure-modes.md`, x25+1 after this
finding): the existing gate's scope is source, the deployable is the packed zip, and
nothing compared the two for this property.

WHAT IT CHECKS. This is a COMPARISON, not a vocabulary check — `verify-component-shape.py`
already owns the accepted vocabulary (main/mobile/quickCreate/quick, via
`component-shapes.yml`'s `attribute_values`); re-stating that list here would be the same
invariant encoded twice; this script owns the one property that check structurally cannot
see: whether the packer PRESERVED the source's declared value.

For every split FormXml source file under `<solution_root>/Entities/*/FormXml/*/*.xml`
(root element `<forms type="...">`, one `<systemform><formid>` per file), this reads the
source's OWN declared `type` attribute, then opens `<packed_zip>` and reads the SAME
formid's enclosing `<forms type>` WRAPPER attribute from `customizations.xml`. The two
must be equal for every form the source declares.

Run:
    python3 scripts/verify-packed-form-types.py \
        src/solutions/RevitaliseGrantAutomation \
        "$ARTIFACT_DIR"/RevitaliseGrantAutomation.zip

Exits 0 when every packed form's wrapper type matches its own source file's declared type.
Exits 1 on any mismatch, on a form present in source but absent from the packed
customizations.xml (dropped silently), or when the solution root, the zip, or
customizations.xml cannot be read — this gate never passes over nothing (IMP-0007). Exits
2 on a usage error.

Wired into config/<slug>-build.yml as the `component-shape-packed` step, immediately after
`pack-unmanaged` — the earliest point in the build a packed artifact exists to check.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def read_source_form_types(solution_root: Path) -> dict[str, tuple[str, str]]:
    """formid -> (declared type, source file path), for every split FormXml file."""
    pattern = os.path.join(str(solution_root), "Entities", "*", "FormXml", "*", "*.xml")
    result: dict[str, tuple[str, str]] = {}
    for path in sorted(glob.glob(pattern)):
        rel = os.path.relpath(path)
        try:
            text = Path(path).read_text(encoding="utf-8")
            element = ET.fromstring(text)
        except (OSError, ET.ParseError) as exc:
            print(f"ERROR: {rel}: could not be read/parsed as XML — {exc}", file=sys.stderr)
            continue
        if element.tag != "forms":
            continue
        declared_type = element.get("type")
        for systemform in element.findall("systemform"):
            formid_el = systemform.find("formid")
            if formid_el is None or not formid_el.text:
                continue
            result[formid_el.text.strip().lower()] = (declared_type or "", rel)
    return result


def read_packed_form_types(zip_path: Path) -> dict[str, str]:
    """formid -> packed <forms type> wrapper value, read from the packed customizations.xml."""
    with zipfile.ZipFile(zip_path) as zf:
        data = zf.read("customizations.xml")
    root = ET.fromstring(data)
    result: dict[str, str] = {}
    for entity in root.iter("Entity"):
        formxml = entity.find("FormXml")
        if formxml is None:
            continue
        for forms in formxml.findall("forms"):
            packed_type = forms.get("type") or ""
            for systemform in forms.findall("systemform"):
                formid_el = systemform.find("formid")
                if formid_el is None or not formid_el.text:
                    continue
                result[formid_el.text.strip().lower()] = packed_type
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("solution_root", type=Path,
                        help="path to the unpacked solution source, e.g. src/solutions/<Name>")
    parser.add_argument("packed_zip", type=Path,
                        help="path to the packed solution .zip (unmanaged or managed)")
    args = parser.parse_args(argv)

    if not args.solution_root.is_dir():
        print(f"packed-form-types: FAILED — '{args.solution_root}' is not a directory. "
              f"A gate pointed at a missing target does not pass (IMP-0007).", file=sys.stderr)
        return 1

    if not args.packed_zip.is_file():
        print(f"packed-form-types: FAILED — '{args.packed_zip}' does not exist. Run this "
              f"step after the pack step that produces it.", file=sys.stderr)
        return 1

    source_forms = read_source_form_types(args.solution_root)
    if not source_forms:
        print(f"packed-form-types: FAILED — no FormXml source files matched under "
              f"{args.solution_root}. Either this solution has no hand-authored forms — remove "
              f"this step — or the glob has drifted and this gate has been checking nothing.",
              file=sys.stderr)
        return 1

    try:
        packed_forms = read_packed_form_types(args.packed_zip)
    except KeyError:
        print(f"packed-form-types: FAILED — '{args.packed_zip}' contains no customizations.xml.",
              file=sys.stderr)
        return 1
    except (zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"packed-form-types: FAILED — '{args.packed_zip}' could not be read as a solution "
              f"zip — {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for formid, (source_type, source_path) in source_forms.items():
        if formid not in packed_forms:
            errors.append(
                f"{source_path}: formid {formid} declares type=\"{source_type}\" in source but "
                f"is ABSENT from the packed {args.packed_zip.name}'s customizations.xml — the "
                f"packer dropped it silently."
            )
            continue
        packed_type = packed_forms[formid]
        if packed_type != source_type:
            errors.append(
                f"{source_path}: source declares type=\"{source_type}\" but the packed "
                f"customizations.xml wraps the same formid ({formid}) in "
                f"type=\"{packed_type}\" — `pac solution pack` derives the packed wrapper from "
                f"the containing FormXml/<foldername>/ path segment, not from this file's own "
                f"attribute (IMP-0874). Rename the containing folder to match the declared type, "
                f"do not edit this file."
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\npacked-form-types: FAILED — {len(errors)} form(s) whose packed wrapper does not "
              f"match their own source-declared type, across {len(source_forms)} source form(s) "
              f"checked against {args.packed_zip}.", file=sys.stderr)
        return 1

    print(f"packed-form-types: OK — {len(source_forms)} form(s)' packed <forms type> wrapper in "
          f"{args.packed_zip} match their own source-declared type.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
