#!/usr/bin/env python3
"""Resolve the next artifact directory for a feature, per WORKFLOW.md's
`build/artifacts/<slug>-<date>-<n>/` convention.

Why this script exists
----------------------
`config/revitalise-grant-automation-build.yml` hardcoded
`build/artifacts/revitalise-grant-automation-20260810-1/` in seven places and kept
using it for every subsequent build. Six builds wrote to that one directory, so the
manifests for builds #1-#3 no longer exist anywhere and build #6 overwrote #5 on disk.
The manifest is the richest structured failure record this system produces — it carries
`defect_found_and_fixed_this_build` with a `why_it_was_never_caught` field per defect —
and it was being destroyed by the build's own config.

See docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md §2.3
(incident B10, IMP-0016).

Contract
--------
Prints one line: the repo-relative path of the next unused artifact directory for
today's date. Does NOT create it — the build's `clean` step does that, so a failed
resolve cannot leave an empty directory behind that shifts the next build's number.

    $ scripts/resolve-artifact-dir.py --feature revitalise-grant-automation
    build/artifacts/revitalise-grant-automation-20260817-1

`n` is the lowest positive integer for which no directory exists, so it is stable if
called twice before the directory is created, and monotonic within a date once builds
start landing. `--date` and `--root` exist for the tests.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

MAX_BUILDS_PER_DAY = 500  # a runaway-loop backstop, far above any real build count


def resolve(feature: str, root: Path, date: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", feature):
        raise ValueError(
            f"feature slug {feature!r} must be lowercase kebab-case — it becomes a directory name"
        )
    if not re.fullmatch(r"\d{8}", date):
        raise ValueError(f"date {date!r} must be YYYYMMDD")

    for n in range(1, MAX_BUILDS_PER_DAY + 1):
        candidate = root / f"{feature}-{date}-{n}"
        if not candidate.exists():
            return candidate.as_posix()
    raise RuntimeError(
        f"more than {MAX_BUILDS_PER_DAY} artifact directories exist for {feature} on {date}"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feature", required=True, help="feature slug, lowercase kebab-case")
    p.add_argument("--root", default="build/artifacts", help="artifact root (default: build/artifacts)")
    p.add_argument("--date", default=None, help="YYYYMMDD; defaults to today")
    args = p.parse_args(argv)

    date = args.date or _dt.date.today().strftime("%Y%m%d")
    try:
        print(resolve(args.feature, Path(args.root), date))
    except (ValueError, RuntimeError) as exc:
        print(f"resolve-artifact-dir: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
