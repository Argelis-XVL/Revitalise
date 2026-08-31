#!/usr/bin/env python3
"""Verify no shipped text value exceeds the length limit that governs it.

THE GENERAL GATE FOR CLASS `platform-field-length-limit-unenforced`.

This replaces two instance-level gates, and exists because they were two instances of one
class:

  * `verify-workflow-description-length.py` (C-TECH-049, retired) hardcoded 256 and looked
    only at flow `description` fields. Power Automate rejects a longer one at *designer save
    time* — `pac solution pack` and `pac solution import` both succeed silently, so the
    failure surfaced only when a maker opened the flow and could not save it, naming no
    field. 62 fields were over the cap on the first live DEV import.
  * `verify-setting-description-length.py` (D-021, retired) hardcoded 500 and looked only at
    `settingRows[].description`, against a `rev_setting.rev_description` that declared
    `MaxLength="500"` in the solution's own Entity.xml AT THE TIME; four of eleven seed rows
    failed live, mid-run, after seven had already been written (IMP-0009). That column now
    declares 2000 — which is the point: this gate reads the number, the retired one asserted it.
    (This sentence said "is MaxLength=500" until 2026-08-31, by which time it was 1500 adrift:
    a comment transcribing the very number the script exists to avoid transcribing.)

Two gates, one class, and no coverage for the third instance — the exact pattern
`skills/how-to-promote-a-finding.md` §2 forbids. The property, independent of the instance,
is: **no shipped text value exceeds the limit that governs it, whether that limit is declared
by the schema in this repo or fixed by the platform.**

So this gate does what neither instance did:

  1. It READS declared limits from `Entities/*/Entity.xml` instead of hardcoding them. Change
     `<MaxLength>` in the schema and the gate follows; the retired scripts would have kept
     asserting the old number.
  2. It carries platform-fixed limits that no schema declares in ONE named table
     (`PLATFORM_LIMITS`), each with its citation, instead of as a bare literal in a script.
  3. It checks EVERY settings-row field that maps to a column — `key` → `rev_name` (100),
     `value` → `rev_value` (4000), `description` → `rev_description` (1000 since 2026-08-21,
     500 before that — the gate follows the schema, which is the point) — where the
     retired gate checked `description` alone. `key` and `value` were never covered.
  4. It refuses to pass on an unreadable schema or an empty scan. A gate that finds nothing
     to check and reports PASS is IMP-0007's defect, and it is the reason this file fails
     loudly instead of skipping.

Run:
    python3 scripts/verify-field-length-limits.py \
        src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings

Each PATH is scanned for every surface it contains, so one command covers both surfaces and
either can be handed a known-bad fixture directory on its own. Declared limits come from
--schema (default: src/solutions/RevitaliseGrantAutomation), because a fixture directory
carries no Entity.xml of its own.

Exits 0 when every value is within its limit, 1 on any violation or unscannable input, 2 on a
usage error. Wired into config/<slug>-build.yml as the `field-length-limits` step
(C-TECH-060).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET

DEFAULT_SCHEMA_ROOT = "src/solutions/RevitaliseGrantAutomation"

# Limits the platform enforces but no schema in this repo declares. One table, each row
# citing the incident that put it here — not a literal buried in a function.
PLATFORM_LIMITS = {
    "flow-description": (
        256,
        "Power Automate action/trigger/parameter/schema-property `description` — hard save "
        "limit in the designer; pack and import both succeed past it (C-TECH-049 origin, "
        "Dev Summary §2.7)",
    ),
}

# settingRows[] field -> the rev_setting column seed-settings.ps1 writes it to
# (provisioning/dataverse/seed-settings.ps1 lines 205-209). The limit for each comes from
# Entity.xml, never from this file.
SETTING_ROW_COLUMNS = {
    "key": ("rev_setting", "rev_name"),
    "value": ("rev_setting", "rev_value"),
    "description": ("rev_setting", "rev_description"),
}


def read_declared_limits(schema_root: str) -> dict[tuple[str, str], int]:
    """Harvest every <MaxLength> an entity declares, keyed by (entity, logical name)."""
    limits: dict[tuple[str, str], int] = {}
    pattern = os.path.join(schema_root, "Entities", "*", "Entity.xml")
    for path in sorted(glob.glob(pattern)):
        entity = os.path.basename(os.path.dirname(path))
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            raise RuntimeError(f"{path}: not parseable XML ({exc})") from exc
        for attribute in root.iter("attribute"):
            logical = attribute.findtext("LogicalName")
            max_length = attribute.findtext("MaxLength")
            if logical and max_length and max_length.strip().isdigit():
                limits[(entity, logical.strip())] = int(max_length.strip())
    return limits


def walk_descriptions(data: object, path: str = "") -> list[tuple[str, str]]:
    """Collect every `description` string in a parsed flow definition, with its JSON path."""
    found: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            here = f"{path}/{key}"
            if key == "description" and isinstance(value, str):
                found.append((here, value))
            found.extend(walk_descriptions(value, here))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            found.extend(walk_descriptions(item, f"{path}[{index}]"))
    return found


def check_flows(root: str) -> tuple[int, list[str]]:
    """Every flow description against the platform's fixed cap. Returns (checked, errors)."""
    limit, citation = PLATFORM_LIMITS["flow-description"]
    paths = sorted(glob.glob(os.path.join(root, "Workflows", "**", "*.json"), recursive=True))
    checked = 0
    errors: list[str] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: not valid JSON ({exc})")
                continue
        for json_path, value in walk_descriptions(data):
            checked += 1
            if len(value) > limit:
                errors.append(
                    f"{os.path.relpath(path)}{json_path}: {len(value)} chars, "
                    f"{len(value) - limit} over the {limit}-char limit — {citation}. "
                    "Condense to the essential fact plus a citation and move the reasoning "
                    "to the companion <FlowName>.notes.md."
                )
    return checked, errors


def check_setting_rows(root: str, limits: dict[tuple[str, str], int]) -> tuple[int, list[str]]:
    """Every settings-row field against its column's DECLARED MaxLength."""
    checked = 0
    errors: list[str] = []
    for path in sorted(glob.glob(os.path.join(root, "*.json"))):
        with open(path, encoding="utf-8") as handle:
            try:
                doc = json.load(handle)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: not valid JSON ({exc})")
                continue
        rows = (doc.get("dataverse") or {}).get("settingRows")
        if not rows:
            continue  # e.g. dev-schema-settings.json — no settingRows at all.
        for row in rows:
            for field, (entity, column) in SETTING_ROW_COLUMNS.items():
                value = row.get(field)
                if not isinstance(value, str):
                    continue
                limit = limits.get((entity, column))
                if limit is None:
                    # Never skip silently: an unknown limit is an unenforced limit.
                    errors.append(
                        f"{os.path.basename(path)}: settingRows[key="
                        f"{row.get('key', '?')}].{field} maps to {entity}.{column}, which "
                        "declares no <MaxLength> in the schema this gate read. Add it, or "
                        "correct SETTING_ROW_COLUMNS."
                    )
                    continue
                checked += 1
                if len(value) > limit:
                    errors.append(
                        f"{os.path.basename(path)}: settingRows[key="
                        f"{row.get('key', '?')}].{field} is {len(value)} chars, over the "
                        f"{limit}-char MaxLength that {entity}.{column} declares in "
                        f"Entities/{entity}/Entity.xml. Shorten it and keep the full text in "
                        "provisioning/deploymentSettings/settings-rows.notes.md."
                    )
    return checked, errors


KNOWN_BAD_ROOT = "src/tests/fixtures/known-bad"


def check_fixtures(limits: dict[tuple[str, str], int]) -> tuple[int, list[str]]:
    """A known-bad fixture must still be known-bad.

    ADDED 2026-08-31 (improvement review 48, IMP-0521 cluster).

    This gate reads its limits from the schema, which is its whole virtue — widen a
    `<MaxLength>` and the gate correctly follows. But the NEGATIVE fixtures do not follow: they
    are static files whose only job is to violate the limit, and when the limit moved out from
    under `setting-description-length` its padding (1478 chars) quietly stopped exceeding the
    new 2000. The fixture still existed, the negative test still ran, and it asserted a
    non-zero exit that no longer happened.

    So the gate lost its proof that it can fail, and said nothing — `gate-cannot-fail` in its
    most literal form. It surfaced at `unit-tests`, build step 69, as `expected non-zero, got
    0`: a message about an exit code, naming neither the fixture nor the limit.

    This runs the real checks over each `*-length` fixture and asserts they still produce at
    least one error, at build step 36, naming the fixture and the number to beat.
    """
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        *KNOWN_BAD_ROOT.split("/"))
    if not os.path.isdir(root):
        return 0, [f"{KNOWN_BAD_ROOT}/: not a directory. A fixture check with no fixtures to "
                   f"read must fail rather than report PASS (IMP-0007)."]

    fixtures = sorted(d for d in os.listdir(root)
                      if d.endswith("-length") and os.path.isdir(os.path.join(root, d)))
    if not fixtures:
        return 0, [f"{KNOWN_BAD_ROOT}/: no '*-length' fixture directories found. This check "
                   f"exists to prove those fixtures still violate their limits; with none to "
                   f"read it must fail, not pass (IMP-0007)."]

    errors: list[str] = []
    for name in fixtures:
        path = os.path.join(root, name)
        found: list[str] = []
        if os.path.isdir(os.path.join(path, "Workflows")):
            found.extend(check_flows(path)[1])
        if glob.glob(os.path.join(path, "*.json")):
            found.extend(check_setting_rows(path, limits)[1])
        if found:
            continue

        # Report the number to beat, which is the thing the unit-test failure never said.
        longest = ""
        for json_path in glob.glob(os.path.join(path, "*.json")):
            try:
                with open(json_path, encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, ValueError):
                continue
            for _where, value in walk_descriptions(data):
                if len(value) > len(longest):
                    longest = value
        detail = (f"its longest text value is {len(longest)} chars" if longest
                  else "no text value could be read from it")
        errors.append(
            f"{KNOWN_BAD_ROOT}/{name}: this KNOWN-BAD fixture no longer violates any limit — "
            f"{detail}. A limit was almost certainly widened in the schema and the fixture's "
            f"padding was not regenerated with it, which silently disarms the negative test "
            f"that proves this gate can fail. Regenerate the padding so it exceeds the "
            f"CURRENT declared limit.")
    return len(fixtures), errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__)
    parser.add_argument("paths", nargs="+", help="directories to scan for shipped text values")
    parser.add_argument(
        "--check-fixtures",
        action="store_true",
        help="assert every known-bad '*-length' fixture still exceeds its CURRENT declared limit",
    )
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA_ROOT,
        help=f"solution root whose Entities/*/Entity.xml declare the limits (default: {DEFAULT_SCHEMA_ROOT})",
    )
    args = parser.parse_args(argv[1:])

    try:
        limits = read_declared_limits(args.schema)
    except RuntimeError as exc:
        print(f"field-length-limits: FAILED — {exc}", file=sys.stderr)
        return 1
    if not limits:
        print(
            f"field-length-limits: FAILED — no <MaxLength> declarations found under "
            f"{args.schema}/Entities/. Without declared limits this gate checks nothing, and "
            "a gate that checks nothing must not report PASS (IMP-0007).",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    surfaces: list[str] = []
    flow_values = row_values = 0
    fixtures_checked = 0

    if args.check_fixtures:
        fixtures_checked, fixture_errors = check_fixtures(limits)
        errors.extend(fixture_errors)
        if fixtures_checked:
            surfaces.append(f"known-bad-fixtures:{fixtures_checked}")

    for path in args.paths:
        if not os.path.isdir(path):
            errors.append(f"{path}: not a directory. A gate pointed at a missing target does not fail.")
            continue
        if os.path.isdir(os.path.join(path, "Workflows")):
            checked, found = check_flows(path)
            flow_values += checked
            errors.extend(found)
            surfaces.append(f"flows:{path}")
        if glob.glob(os.path.join(path, "*.json")):
            checked, found = check_setting_rows(path, limits)
            row_values += checked
            errors.extend(found)
            surfaces.append(f"setting-rows:{path}")

    if not surfaces:
        print(
            "field-length-limits: FAILED — none of the given paths contained a scannable "
            f"surface (a Workflows/ folder or *.json settings files): {', '.join(args.paths)}",
            file=sys.stderr,
        )
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        # Two different failure shapes share this exit, and conflating them in the summary is
        # how a reader misdiagnoses one as the other: a shipped value OVER its limit, and a
        # known-bad fixture no longer UNDER-shooting one. Count them separately.
        fixture_failures = sum(1 for e in errors if e.startswith(KNOWN_BAD_ROOT))
        value_failures = len(errors) - fixture_failures
        parts = []
        if value_failures:
            parts.append(f"{value_failures} value(s) exceed the limit that governs them")
        if fixture_failures:
            parts.append(f"{fixture_failures} known-bad fixture(s) no longer violate any limit, "
                         f"so this gate's proof that it can fail is disarmed")
        print(
            f"\nfield-length-limits: FAILED — {'; '.join(parts)} (C-TECH-060).",
            file=sys.stderr,
        )
        return 1

    fixture_note = (f"; {fixtures_checked} known-bad fixture(s) still violate their current "
                    f"limits" if args.check_fixtures else "")
    print(
        f"field-length-limits: OK — {flow_values} flow description(s) within "
        f"{PLATFORM_LIMITS['flow-description'][0]} chars; {row_values} settings-row value(s) "
        f"within the MaxLength their columns declare; {len(limits)} declared limit(s) read "
        f"from {args.schema}/Entities/{fixture_note}. Surfaces: {', '.join(surfaces)}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
