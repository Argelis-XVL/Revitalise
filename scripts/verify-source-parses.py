#!/usr/bin/env python3
"""Verify every solution XML file is well-formed and every cloud-flow JSON parses.

Extracted from an inline `python3 -c "..."` one-liner in
config/<slug>-build.yml (2026-08-17).

Why it was extracted
--------------------
As an inline one-liner with a hardcoded glob it could not be pointed at a fixture, so it
could not be proven able to fail — and this build's other gates showed exactly why that
matters: three of them recorded PASS for months while checking nothing
(docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §2.5).
A gate must be runnable against known-bad input, which means it must be a script that
takes a path.

Verification level: V1 (well-formed) only, per C-TECH-053. Parsing proves the bytes are
syntactically valid XML/JSON. It proves nothing about whether any name inside is real,
whether the platform will accept the shape, or whether the component works.

Usage
-----
    python3 scripts/verify-source-parses.py <solution-root> [--expect-flows N|manifest]

Exits 0 when everything parses (and the flow count matches, if asserted), 1 otherwise.

`--expect-flows manifest` — why the literal was retired
-------------------------------------------------------
`test-coupled-to-absolute-counts` reached its seventh instance on 2026-08-25 (`IMP-0315`,
after `IMP-0005`, `0039`, `0120`, `0155`, `0212`, `0235`). Adding one flow broke this
assertion in TWO hand-typed places at once — `config/<slug>-build.yml` and
`src/tests/build/BuildGates.Tests.ps1` — and the project had patched the class by bumping a
number six times already. `skills/how-to-promote-a-finding.md` §2 forbids a seventh.

So the count is DERIVED, from `Other/Solution.xml`'s `<RootComponent type="29">` entries —
one per cloud flow, by GUID. The important property is that this is an **independent** source
in the same tree, not the glob the check is guarding: comparing `Workflows/*.json` against
itself would be a tautology that can never fail, which is the `gate-cannot-fail` class this
whole script exists inside.

It also closes a direction nothing else covered. `verify-solution-root-components.py` checks
disk → declared (a flow on disk that nobody declared). This closes declared → disk (a flow
declared in the manifest whose definition is gone), for free.

Residual, stated because it is real: a flow deliberately deleted from BOTH representations is
a legitimate change and is not reported. This asserts AGREEMENT between two places; it never
knows intent (`IMP-0317` supplied the independent source).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET


# A cloud flow's RootComponent type. Declared once, per flow, by GUID — never by name, which
# is why grepping Solution.xml for a flow's display name finds nothing (IMP-0317).
CLOUD_FLOW_COMPONENT_TYPE = "29"


def declared_flow_count(root: str) -> tuple[int | None, str]:
    """How many cloud flows Other/Solution.xml declares. (count, detail-or-error)."""
    manifest = os.path.join(root, "Other", "Solution.xml")
    if not os.path.isfile(manifest):
        return None, f"{os.path.join('Other', 'Solution.xml')} does not exist"
    try:
        tree = ET.parse(manifest)
    except ET.ParseError as exc:
        return None, f"Other/Solution.xml is not well-formed: {exc}"
    declared = [el for el in tree.getroot().iter("RootComponent")
                if el.get("type") == CLOUD_FLOW_COMPONENT_TYPE]
    return len(declared), f"{len(declared)} <RootComponent type=\"29\"> entry(ies)"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("solution_root", help="unpacked solution root, e.g. src/solutions/Foo")
    p.add_argument(
        "--expect-flows",
        default=None,
        metavar="N|manifest",
        help="assert this many cloud-flow .json definitions exist under Workflows/. Prefer "
             "'manifest', which DERIVES the count from Other/Solution.xml's RootComponent "
             "type=\"29\" entries instead of hardcoding it (IMP-0315 — seventh instance of "
             "test-coupled-to-absolute-counts; the literal is retired)",
    )
    args = p.parse_args(argv)

    root = args.solution_root
    if not os.path.isdir(root):
        print(f"verify-source-parses: {root} is not a directory", file=sys.stderr)
        return 1

    errors: list[str] = []

    xml_files = sorted(glob.glob(os.path.join(root, "**", "*.xml"), recursive=True))
    for path in xml_files:
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"  XML NOT WELL-FORMED - {os.path.relpath(path, root)}: {exc}")

    flow_files = sorted(glob.glob(os.path.join(root, "Workflows", "**", "*.json"), recursive=True))
    for path in flow_files:
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"  JSON DOES NOT PARSE  - {os.path.relpath(path, root)}: {exc}")

    expected: int | None = None
    source = ""
    if args.expect_flows is not None:
        if str(args.expect_flows).strip().lower() == "manifest":
            expected, detail = declared_flow_count(root)
            if expected is None:
                # Refuse rather than skip. A count that cannot be derived must not silently
                # become "no assertion" — that is the gate-cannot-fail shape exactly.
                errors.append(
                    f"  FLOW COUNT UNDERIVABLE - --expect-flows manifest needs the solution "
                    f"manifest and {detail}. Fix the manifest or pass an explicit number."
                )
            else:
                source = f" (derived from the manifest: {detail})"
        else:
            try:
                expected = int(args.expect_flows)
            except ValueError:
                p.error(f"--expect-flows takes an integer or 'manifest', not "
                        f"{args.expect_flows!r}")
            source = " (hardcoded — prefer 'manifest', see IMP-0315)"

    if expected is not None and len(flow_files) != expected:
        errors.append(
            f"  FLOW COUNT MISMATCH  - expected {expected} cloud flow definition(s){source} "
            f"under Workflows/, found {len(flow_files)}. A flow that vanished from source packs "
            f"clean and simply never reaches the target environment; a flow declared in the "
            f"manifest with no definition on disk does the same."
        )

    if errors:
        print("source-validate: FAILED\n" + "\n".join(errors), file=sys.stderr)
        return 1

    print(
        f"source-validate: OK - {len(xml_files)} XML file(s) well-formed, "
        f"{len(flow_files)} flow definition(s) parse. "
        f"This is V1 (well-formed) and proves nothing about content."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
