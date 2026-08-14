#!/usr/bin/env python3
"""Verify every rev_setting row description fits the column's own MaxLength.

D-021 (2026-08-14): `rev_setting.rev_description` is declared `MaxLength="500"` in
`src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml`. Nothing enforced
that limit against `provisioning/deploymentSettings/*-settings.json` before this script: not
`pac solution pack` (it never reads a deployment settings file), not the Pester suite (its
mocked Dataverse Web API accepts whatever string a test hands it), and not a human, because the
value only breaks something the first time `seed-settings.ps1` actually writes it to a real
environment. That is exactly what happened running `seed-settings.ps1 -Env dev` against
REV-GrantApplications-DEV for the first time: 4 of 11 rows failed with a Dataverse validation
error naming `rev_description`, after 7 rows had already been written. Same failure class, same
root cause, and the same fix shape as the flow-description length defect (C-TECH-049,
`scripts/verify-workflow-description-length.py`) — a platform field limit nothing in the build
pipeline could see.

Run:
    python3 scripts/verify-setting-description-length.py provisioning/deploymentSettings

Exits 0 when every settingRows[].description is within the limit, 1 otherwise. Wired into
config/<slug>-build.yml as the ``setting-description-length`` step.
"""

from __future__ import annotations

import glob
import json
import os
import sys

MAX_LENGTH = 500  # rev_setting.rev_description — Entities/rev_setting/Entity.xml <MaxLength>


def main(settings_dir: str) -> int:
    paths = sorted(glob.glob(os.path.join(settings_dir, "*.json")))
    if not paths:
        print(f"No .json files found under {settings_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []
    checked = 0

    for path in paths:
        filename = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            try:
                doc = json.load(fh)
            except json.JSONDecodeError as exc:
                errors.append(f"{filename}: not valid JSON ({exc})")
                continue

        rows = (doc.get("dataverse") or {}).get("settingRows")
        if not rows:
            continue  # e.g. dev-schema-settings.json, which has no settingRows at all.

        for row in rows:
            checked += 1
            description = row.get("description", "")
            if len(description) > MAX_LENGTH:
                errors.append(
                    f"{filename}: settingRows[key={row.get('key', '?')}].description is "
                    f"{len(description)} chars, over the {MAX_LENGTH}-char limit of "
                    "rev_setting.rev_description (D-021). Shorten it to the essential fact plus "
                    "a citation, and keep the full text in "
                    "provisioning/deploymentSettings/settings-rows.notes.md."
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"\nsetting-description-length: FAILED — {len(errors)} of {checked} row(s) exceed "
            f"the {MAX_LENGTH}-char rev_description limit.",
            file=sys.stderr,
        )
        return 1

    print(f"setting-description-length: OK — {checked} row(s) checked across {len(paths)} "
          f"file(s), all within {MAX_LENGTH} characters.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <deploymentSettings-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
