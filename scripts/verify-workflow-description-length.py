#!/usr/bin/env python3
"""Verify no Power Automate flow description exceeds the platform's save limit.

Power Automate enforces a hard 256-character limit on the `description` field of every
action, trigger, parameter and trigger-schema property in a cloud flow. Exceeding it does
not fail `pac solution pack` or `pac solution import` - both succeed silently. It fails
much later and much more confusingly: the flow imports fine, but a maker opening it in the
designer gets "Flow save failed with code 'InvalidTemplate'" (or simply cannot save any
edit at all) the first time anyone tries to touch it, with no indication which of the
dozens of actions is the culprit. Discovered live during Revitalise's first DEV import -
see docs/development/revitalise-grant-automation-dev-summary.md and every
Workflows/*.notes.md file for the incident and the fix.

This script finds the offending field in one second, at build time, before it ever
reaches an environment - the description-length equivalent of root-components-resolve.

Run:
    python3 scripts/verify-workflow-description-length.py src/solutions/RevitaliseGrantAutomation

Exits 0 when every description is within the limit, 1 otherwise. Wired into
config/<slug>-build.yml as the `workflow-description-length` step.
"""

from __future__ import annotations

import glob
import json
import os
import sys

MAX_LENGTH = 256


def find_oversized_descriptions(data: object, path: str = "") -> list[tuple[str, int]]:
    """Walk a parsed flow definition and collect every description over the limit."""
    problems: list[tuple[str, int]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}/{key}"
            if key == "description" and isinstance(value, str) and len(value) > MAX_LENGTH:
                problems.append((new_path, len(value)))
            problems.extend(find_oversized_descriptions(value, new_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            problems.extend(find_oversized_descriptions(item, f"{path}[{index}]"))
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")

    flow_paths = sorted(glob.glob(os.path.join(root, "Workflows", "**", "*.json"), recursive=True))
    if not flow_paths:
        print(f"FAIL - no flow definitions found under {root}/Workflows/")
        return 1

    problems: list[str] = []
    total_checked = 0
    for path in flow_paths:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        for json_path, length in find_oversized_descriptions(data):
            total_checked += 1
            problems.append(
                f"  {os.path.basename(path)}{json_path}: {length} characters "
                f"({length - MAX_LENGTH} over the {MAX_LENGTH}-character limit)"
            )

    if problems:
        print(
            f"FAIL - {len(problems)} description(s) exceed Power Automate's "
            f"{MAX_LENGTH}-character save limit:"
        )
        print("\n".join(problems))
        print(
            "\nCondense each to the essential fact and citation; move the full reasoning to a "
            "companion <FlowName>.notes.md file next to the flow's .json (see any existing "
            "Workflows/*.notes.md for the pattern). Do not truncate blindly - a half-sentence "
            "description is worse than a short, complete one."
        )
        return 1

    print(f"PASS - {len(flow_paths)} flow definition(s) checked, every description within {MAX_LENGTH} characters.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
