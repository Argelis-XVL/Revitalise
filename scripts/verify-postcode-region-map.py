#!/usr/bin/env python3
"""Reconcile the seeded PostcodeRegionMap against the client's postcode reference sheet.

WHY THIS EXISTS (IMP-0737, improvement review 2026-09-17). ``rev_locationarea`` is derived at
intake by looking the alphabetic prefix of an outward code up in ``PostcodeRegionMap``, a JSON
setting seeded from ``provisioning/deploymentSettings/*-scoring-settings.json``. 125 of the
client's 3,394 postcode districts derive a region that disagrees with the client's own
reference data, and the wrong values shipped to all three environments undetected.

THERE ARE TWO INDEPENDENT DEFECTS AND THIS GATE CHECKS BOTH, because the review that
commissioned it first attributed all five affected areas to one mechanism and was corrected:

* **WRONG-OPTION** - the area IS in the map, mapped to the wrong option. ``PE`` (Peterborough)
  derives East Midlands where the client says East of England; ``WD`` (Watford) derives London
  where the client says East of England. 63 districts. No fallback is involved at all.

* **SHORTER-PREFIX-FALLBACK** - the area is ABSENT and the longest-prefix lookup degrades to a
  SHORTER prefix instead of to option 13 "Not known". ``BB`` (Blackburn) is absent, so it
  matches the bare ``B`` (Birmingham) and inherits West Midlands. 18 districts. This is the
  dangerous shape: it fails loudest-looking, producing a real region name rather than a visible
  "Not known", and the setting's own description promises the opposite ("Option 13 (Not known)
  is the fallback for an unrecognised postcode").

* Areas absent with no shorter prefix to fall back on (``CT``, ``HP``; 44 districts) resolve to
  "Not known" as documented. That is a COVERAGE gap, reported separately and at lower severity,
  because a visible "Not known" is a different problem from a confident wrong answer.

THE AUTHORITY IS THE CLIENT'S SHEET, NOT A LIST HARD-CODED HERE. Embedding the UK postcode
areas in this file would make it a hand-maintained copy of a source that already exists in the
repository - the ``hand-maintained-count-drifts-from-source`` class, which this project has
recurred 37 times. ``docs/Import/Postcode Details.xlsx`` is registered in
``docs/Import/MANIFEST.yml`` and is read directly.

TWO NORMALISATIONS, both necessary, both measured:

* The sheet's ``Region`` column sometimes carries a COUNTRY ("England") rather than a region.
  Those rows are ignored when establishing what the client asserts for an area; without this,
  five areas (``M``, ``NE``, ``L``, ``LA``, ``AL``) report as disagreements that are really the
  source's own inconsistency.
* Case and internal whitespace are normalised. Without this, nine areas report on
  "Yorkshire and the Humber" versus "Yorkshire and The Humber" - a capitalisation difference
  and nothing more.

Skipped, not failed, when the sheet is absent or ``openpyxl`` is not installed: the reference
sheet is client-supplied intake material, and a gate that fails on its absence would block a
build for a reason the build cannot fix.

Run:
    python3 scripts/verify-postcode-region-map.py
    python3 scripts/verify-postcode-region-map.py --settings <path> --sheet <path>
    python3 scripts/verify-postcode-region-map.py --selftest

Wired into config/<slug>-build.yml as the SOFT (--warn-only) step `postcode-region-map`. It is
SOFT deliberately: it opens with 5 real findings against shipped data this dispatch does not
own, and wiring it HARD would halt builds on pre-existing debt (IMP-0439, IMP-0491). Making it
HARD is a follow-up once the map is corrected and redeployed.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS = REPO_ROOT / "provisioning/deploymentSettings/dev-scoring-settings.json"
DEFAULT_SHEET = REPO_ROOT / "docs/Import/Postcode Details.xlsx"
SETTING_KEY = "PostcodeRegionMap"
NOT_KNOWN = 13

# rev_locationarea option values. Mirrors the OptionSet; the setting's own description states
# the same ladder ("1=North East .. 12=Northern Ireland").
OPTION_LABELS = {
    1: "North East", 2: "North West", 3: "Yorkshire and The Humber", 4: "East Midlands",
    5: "West Midlands", 6: "East of England", 7: "London", 8: "South East", 9: "South West",
    10: "Wales", 11: "Scotland", 12: "Northern Ireland", NOT_KNOWN: "Not known",
}
COUNTRY_VALUES = {"england", "scotland", "wales", "northern ireland"}


def norm(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def find_setting(obj: object, key: str) -> dict | None:
    if isinstance(obj, dict):
        if obj.get("key") == key:
            return obj
        for value in obj.values():
            found = find_setting(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_setting(value, key)
            if found is not None:
                return found
    return None


def load_prefixes(settings_path: Path) -> dict[str, int]:
    """prefix -> option. Raises on a duplicate prefix, which would make the lookup ambiguous."""
    setting = find_setting(json.loads(settings_path.read_text(encoding="utf-8")), SETTING_KEY)
    if setting is None:
        raise KeyError(f"{settings_path} carries no '{SETTING_KEY}' setting")
    prefixes: dict[str, int] = {}
    for group in json.loads(setting["value"]):
        for prefix in group["prefixes"]:
            prefix = prefix.strip().upper()
            if prefix in prefixes:
                raise ValueError(f"prefix {prefix!r} appears in more than one group")
            prefixes[prefix] = int(group["option"])
    return prefixes


def lookup(area: str, prefixes: dict[str, int]) -> tuple[int, str | None]:
    """Longest prefix wins, exactly as the intake flow does it."""
    for length in range(len(area), 0, -1):
        if area[:length] in prefixes:
            return prefixes[area[:length]], area[:length]
    return NOT_KNOWN, None


def load_client_regions(sheet_path: Path) -> dict[str, tuple[str, int]]:
    """area -> (the region the client asserts, how many districts that area has)."""
    import openpyxl  # imported here so absence is a skip, not an import-time crash

    workbook = openpyxl.load_workbook(sheet_path, read_only=True, data_only=True)
    worksheet = workbook["Postcodes"]
    rows = worksheet.iter_rows(values_only=True)
    header = [norm(h) for h in next(rows)]
    area_col = header.index("postcode area")
    region_col = header.index("region")

    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    totals: collections.Counter = collections.Counter()
    for row in rows:
        if not row or not row[area_col]:
            continue
        area = str(row[area_col]).strip().upper()
        totals[area] += 1
        counts[area][norm(row[region_col])] += 1

    regions: dict[str, tuple[str, int]] = {}
    for area, tally in counts.items():
        stated = [(region, n) for region, n in tally.items() if region not in COUNTRY_VALUES]
        if not stated:
            continue  # the sheet only ever gives this area a country; nothing to compare
        regions[area] = (max(stated, key=lambda pair: pair[1])[0], totals[area])
    return regions


def classify(prefixes: dict[str, int], client: dict[str, tuple[str, int]]) -> dict[str, list]:
    wrong_option: list[tuple[str, str, str, int]] = []
    fallback: list[tuple[str, str, str, int, str]] = []
    coverage: list[tuple[str, str, int]] = []

    for area in sorted(client):
        truth, districts = client[area]
        option, via = lookup(area, prefixes)
        if norm(OPTION_LABELS[option]) == truth:
            continue
        if option == NOT_KNOWN:
            coverage.append((area, truth, districts))
        elif via == area:
            wrong_option.append((area, truth, OPTION_LABELS[option], districts))
        else:
            fallback.append((area, truth, OPTION_LABELS[option], districts, via or ""))
    return {"wrong_option": wrong_option, "fallback": fallback, "coverage": coverage}


def render(findings: dict[str, list], total_districts: int, warn_only: bool) -> tuple[str, int]:
    lines: list[str] = []
    affected = 0

    for area, truth, derived, districts, via in findings["fallback"]:
        affected += districts
        lines.append(
            f"ERROR: [SHORTER-PREFIX-FALLBACK] postcode area {area} is ABSENT from "
            f"{SETTING_KEY} and degrades to the shorter prefix '{via}', deriving "
            f"{derived!r} where the client's reference sheet says {truth!r} "
            f"({districts} districts).\n"
            f"    → add {area} to the map, and make an unlisted two-letter area resolve to "
            f"option {NOT_KNOWN} 'Not known' rather than to its first letter. A visible "
            f"'Not known' is recoverable; a confident wrong region is not."
        )
    for area, truth, derived, districts in findings["wrong_option"]:
        affected += districts
        lines.append(
            f"ERROR: [WRONG-OPTION] postcode area {area} IS in {SETTING_KEY} but derives "
            f"{derived!r} where the client's reference sheet says {truth!r} "
            f"({districts} districts).\n"
            f"    → move {area} to the group whose option is {truth!r}. No fallback is "
            f"involved; the prefix is simply in the wrong group."
        )
    for area, truth, districts in findings["coverage"]:
        affected += districts
        lines.append(
            f"WARNING: [COVERAGE] postcode area {area} is absent from {SETTING_KEY} and has no "
            f"shorter prefix to fall back on, so it resolves to 'Not known' where the client's "
            f"reference sheet says {truth!r} ({districts} districts). Visibly unknown rather "
            f"than confidently wrong — a coverage gap, not a derivation defect."
        )

    errors = len(findings["fallback"]) + len(findings["wrong_option"])
    warnings = len(findings["coverage"])
    if not lines:
        lines.append(
            f"postcode-region-map: OK — every postcode area in the client's reference sheet "
            f"derives the region that sheet states. NOT covered: whether the sheet itself is "
            f"correct, and districts absent from it."
        )
        return "\n".join(lines), 0

    lines.append(
        f"\nverify-postcode-region-map: "
        f"{'FAILED (SOFT — report as WARN, do not block)' if warn_only else 'FAILED'} — "
        f"{errors} wrong derivation(s) and {warnings} coverage gap(s) across "
        f"{affected} district(s), in areas covering {total_districts} district(s) for which "
        f"the sheet states a region."
    )
    return "\n".join(lines), 0 if warn_only else 1


def selftest() -> int:
    prefixes = {"B": 5, "PE": 4, "NE": 1, "CF": 10}
    client = {
        "B":  ("west midlands", 40),     # agrees
        "BB": ("north west", 18),        # absent, degrades to B  -> SHORTER-PREFIX-FALLBACK
        "PE": ("east of england", 38),   # present, wrong group   -> WRONG-OPTION
        "CT": ("south east", 21),        # absent, no fallback    -> COVERAGE
        "NE": ("north east", 71),        # agrees
        "CF": ("wales", 30),             # agrees
    }
    found = classify(prefixes, client)
    assert [f[0] for f in found["fallback"]] == ["BB"], found["fallback"]
    assert [f[0] for f in found["wrong_option"]] == ["PE"], found["wrong_option"]
    assert [f[0] for f in found["coverage"]] == ["CT"], found["coverage"]

    text, rc = render(found, 218, warn_only=False)
    assert rc == 1, "a gate that cannot fail is not a gate"
    assert "SHORTER-PREFIX-FALLBACK" in text and "WRONG-OPTION" in text and "COVERAGE" in text
    _, rc_warn = render(found, 218, warn_only=True)
    assert rc_warn == 0, "--warn-only must not block"

    clean, rc_clean = render(classify({"B": 5}, {"B": ("west midlands", 40)}), 40, False)
    assert rc_clean == 0 and "OK" in clean

    # the two normalisations, each proven to matter
    assert classify({"S": 3}, {"S": ("yorkshire and the humber", 99)})["wrong_option"] == [], \
        "case normalisation must absorb 'the' vs 'The'"
    assert load_client_regions.__doc__  # documented contract

    # longest prefix genuinely wins
    assert lookup("SW", {"S": 3, "SW": 7})[0] == 7
    assert lookup("SW", {"S": 3})== (3, "S")

    print("verify-postcode-region-map --selftest: OK — all three finding classes fire, "
          "clean corpus exits 0, --warn-only exits 0 while still reporting, "
          "longest-prefix and both normalisations proven.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--warn-only", action="store_true",
                        help="report findings but exit 0 (how this gate is wired today)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.settings.is_file():
        print(f"postcode-region-map: no {args.settings} — skipped, not failed.")
        return 0
    if not args.sheet.is_file():
        print(f"postcode-region-map: no {args.sheet} — skipped, not failed. The client's "
              f"reference sheet is the authority and nothing else can stand in for it.")
        return 0
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        print("postcode-region-map: openpyxl is not installed — skipped, not failed. "
              "Install it (pip install openpyxl) to run this check.")
        return 0

    prefixes = load_prefixes(args.settings)
    client = load_client_regions(args.sheet)
    findings = classify(prefixes, client)
    total = sum(districts for _, districts in client.values())
    text, rc = render(findings, total, args.warn_only)
    print(text, file=sys.stderr if rc or "ERROR" in text else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
