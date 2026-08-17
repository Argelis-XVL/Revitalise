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
    python3 scripts/verify-source-parses.py <solution-root> [--expect-flows N]

Exits 0 when everything parses (and the flow count matches, if asserted), 1 otherwise.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("solution_root", help="unpacked solution root, e.g. src/solutions/Foo")
    p.add_argument(
        "--expect-flows",
        type=int,
        default=None,
        help="assert exactly this many cloud-flow .json definitions exist under Workflows/",
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

    if args.expect_flows is not None and len(flow_files) != args.expect_flows:
        errors.append(
            f"  FLOW COUNT MISMATCH  - expected {args.expect_flows} cloud flow definition(s) "
            f"under Workflows/, found {len(flow_files)}. A flow that vanished from source packs "
            f"clean and simply never reaches the target environment."
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
