#!/usr/bin/env python3
"""Verify every GUID in hand-authored solution source is a parseable UUID.

WHY THIS EXISTS. While authoring rev_grant on 2026-08-18 the form's cell, tab, section and
form ids were written with a non-hex character in them — `{a1000000-0000-4000-8000-00000000ga01}`
contains a `g`. `pac solution pack` accepted the folder and exited 0. Nothing in the build
noticed: the file is well-formed XML, so `source-validate` passes; the ids are not
RootComponents, so `verify-solution-root-components.py` never looks at them.

That is the same shape as every defect in this project's digest that cost a deployment: a
plausible-looking hand-authored value the packer does not validate, which fails or misbehaves
only later, in an environment, with an error that names nothing useful (IMP-0006, IMP-0011,
IMP-0018). The difference is that this one is trivially checkable, so it should never reach an
environment again.

WHAT IT CHECKS. Every `{...}` token that is 36 characters long, in every .xml file under the
solution root, plus every GUID appearing in a FILE NAME (SolutionPackager names form and view
files after their ids, so a malformed name is as broken as a malformed element).

Run:
    python3 scripts/verify-guid-syntax.py src/solutions/RevitaliseGrantAutomation

Exits 0 when every GUID parses, 1 otherwise. Wired into config/<slug>-build.yml as the
`guid-syntax` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import uuid

GUID_TOKEN = re.compile(r"\{([^{}\s]{36})\}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")
    if not os.path.isdir(root):
        print(f"guid-syntax: FAILED — {root} is not a directory. A gate pointed at a missing "
              "target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    paths = sorted(glob.glob(os.path.join(root, "**", "*.xml"), recursive=True))
    if not paths:
        print(f"guid-syntax: FAILED — no .xml files found under {root}", file=sys.stderr)
        return 1

    errors: list[str] = []
    checked = 0

    for path in paths:
        rel = os.path.relpath(path)
        # The file NAME carries an id for forms and saved queries.
        for token in GUID_TOKEN.findall(os.path.basename(path)):
            checked += 1
            try:
                uuid.UUID(token)
            except ValueError:
                errors.append(f"{rel}: FILE NAME contains a malformed GUID '{{{token}}}'")
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        for token in sorted(set(GUID_TOKEN.findall(text))):
            checked += 1
            try:
                uuid.UUID(token)
            except ValueError:
                errors.append(f"{rel}: malformed GUID '{{{token}}}' — not a parseable UUID")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nguid-syntax: FAILED — {len(errors)} malformed GUID(s) of {checked} checked. "
              "`pac solution pack` accepts these and exits 0; the target does not.",
              file=sys.stderr)
        return 1

    print(f"guid-syntax: OK — {checked} GUID(s) across {len(paths)} file(s) all parse as UUIDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
