#!/usr/bin/env python3
"""Assert the built Code App bundle against a DECLARED byte budget.

WHY THIS EXISTS (IMP-0573, seventh instance of class `untriaged-tool-warning`).

Vite's warning text — "Some chunks are larger than 500 kB after minification" — is
IDENTICAL whether the chunk is 558 kB or 1,204 kB. Six prior instances of this class
were closed by adding a prose row to a Dev Summary's C-TECH-055 triage table; the
seventh had that row, and the row's cited figure was less than half the truth, because
`recharts@3.10.1` landed in a later commit than the prose and nothing reconciled them.

A gate that diffs warning SIGNATURES (the deferred `warnings_detail[]` diff behind
`IMP-0500`) cannot catch this: the signature is unchanged. The only thing that can is an
assertion on the VALUE — which is what `agents/improvement-agent.md` requires anyway
("assert on VALUES, not on PHRASES, wherever a value exists").

So the triage obligation moves from "a human re-reads prose against a log" to "the
committed budget file must be raised, deliberately, in the same commit that grows the
bundle." Raising it is one line and requires a `reason` and a `triaged_in`; not raising
it halts the build at the commit that caused the growth, not three revisions later.

INPUT   <code-app-dir>/bundle-budget.json   (tracked; reviewed in diffs)
MEASURES <code-app-dir>/dist/...            (gitignored; produced by `code-app-build`)

HARD. Exit 1 on any budget exceeded, any budget entry matching no built file, and any
missing/malformed budget file.
"""

from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
import tempfile
from pathlib import Path

BUDGET_FILENAME = "bundle-budget.json"
REQUIRED_ENTRY_KEYS = {"glob", "max_bytes", "reason", "triaged_in"}
# A budget more than this fraction above the measured size no longer describes reality:
# it is the loose budget that lets the NEXT recharts through silently. SOFT.
STALE_HEADROOM = 0.25


def gzip_size(path: Path) -> int:
    """Compressed size, as vite reports it. Level 9, no mtime in the header."""
    return len(gzip.compress(path.read_bytes(), compresslevel=9, mtime=0))


def check(app_dir: Path) -> tuple[list[str], list[str]]:
    """Return (hard_findings, soft_findings)."""
    hard: list[str] = []
    soft: list[str] = []

    budget_path = app_dir / BUDGET_FILENAME
    if not budget_path.is_file():
        return ([
            f"{budget_path}: no bundle budget declared. Every Code App whose build emits a "
            f"chunk-size warning needs one, so that a growth in MAGNITUDE fails a build even "
            f"though the warning TEXT is unchanged (C-TECH-055, IMP-0573). Create it with one "
            f"entry per built asset family: "
            f'{{"assets": [{{"glob": "dist/assets/*.js", "max_bytes": N, '
            f'"reason": "...", "triaged_in": "docs/development/<feature>-dev-summary.md#Lnnn"}}]}}'
        ], soft)

    try:
        budget = json.loads(budget_path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return ([f"{budget_path}: not valid JSON — {exc}"], soft)

    entries = budget.get("assets")
    if not isinstance(entries, list) or not entries:
        return ([f"{budget_path}: 'assets' must be a non-empty list of budget entries"], soft)

    dist = app_dir / "dist"
    if not dist.is_dir():
        return ([
            f"{dist}: no built output to measure. This gate runs AFTER the build step that "
            f"produces dist/ (`code-app-build`); run that first."
        ], soft)

    for idx, entry in enumerate(entries):
        label = f"{budget_path} assets[{idx}]"
        if not isinstance(entry, dict):
            hard.append(f"{label}: not an object")
            continue
        missing = REQUIRED_ENTRY_KEYS - set(entry)
        if missing:
            hard.append(
                f"{label}: missing required key(s) {sorted(missing)}. "
                f"'reason' and 'triaged_in' are what make a raised budget a TRIAGE rather than "
                f"a silent bump — a budget raised without them is the defect this gate exists for"
            )
            continue

        pattern = str(entry["glob"])
        matches = sorted(Path(p) for p in glob.glob(str(app_dir / pattern)))
        if not matches:
            # gate-cannot-fail guard: a budget nothing matches is a budget that always passes.
            hard.append(
                f"{label}: glob {pattern!r} matched NO file under {app_dir}. A budget entry that "
                f"matches nothing is a gate that cannot fail — fix the glob or remove the entry"
            )
            continue

        max_bytes = entry["max_bytes"]
        max_gzip = entry.get("max_gzip_bytes")
        if not isinstance(max_bytes, int) or max_bytes <= 0:
            hard.append(f"{label}: 'max_bytes' must be a positive integer, got {max_bytes!r}")
            continue

        for f in matches:
            actual = f.stat().st_size
            rel = f.relative_to(app_dir)
            if actual > max_bytes:
                hard.append(
                    f"{rel}: {actual:,} bytes ({actual / 1000:.2f} kB) EXCEEDS the declared "
                    f"budget of {max_bytes:,} bytes ({max_bytes / 1000:.2f} kB) by "
                    f"{actual - max_bytes:,} bytes. The build tool's warning text has not "
                    f"changed and is NOT evidence that nothing changed (IMP-0573). Either reduce "
                    f"the bundle, or raise 'max_bytes' in {BUDGET_FILENAME} in this same commit "
                    f"with a 'reason' naming what grew it and a 'triaged_in' pointing at the row "
                    f"in THIS feature's Dev Summary that records the decision (C-TECH-055)"
                )
                continue

            # ADVISORY ONLY, and deliberately so. Python's gzip and rollup's reporter
            # disagree by ~0.06% on this bundle (471,087 vs vite's printed 471.37 kB), so a
            # HARD assertion on a gzip figure would be an assertion on an implementation
            # detail. Raw bytes are exact and reproducible; that is what blocks.
            if isinstance(max_gzip, int) and max_gzip > 0:
                gz = gzip_size(f)
                if gz > max_gzip:
                    soft.append(
                        f"{rel}: {gz:,} gzipped bytes (measured by python gzip -9) exceeds the "
                        f"declared 'max_gzip_bytes' of {max_gzip:,}. Advisory: gzip figures are "
                        f"implementation-dependent, so only 'max_bytes' blocks a build"
                    )

            headroom = (max_bytes - actual) / max_bytes
            if headroom > STALE_HEADROOM:
                soft.append(
                    f"{rel}: {actual:,} bytes against a budget of {max_bytes:,} — "
                    f"{headroom * 100:.0f}% headroom. A budget this loose no longer describes "
                    f"the bundle and will not notice the next dependency that grows it. "
                    f"Tighten 'max_bytes' toward the measured figure"
                )

    return hard, soft


def selftest() -> int:
    """Prove the gate CAN fail, and in which direction, on real bytes."""
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as td:
        app = Path(td) / "app"
        (app / "dist" / "assets").mkdir(parents=True)
        js = app / "dist" / "assets" / "index-abc123.js"
        js.write_bytes(b"x" * 1000)

        def budget(**over):
            entry = {
                "glob": "dist/assets/*.js",
                "max_bytes": 1000,
                "reason": "selftest",
                "triaged_in": "docs/x.md#L1",
            }
            entry.update(over)
            (app / BUDGET_FILENAME).write_text(json.dumps({"assets": [entry]}))

        budget()
        h, s = check(app)
        checks.append(("exactly at budget passes", not h))

        budget(max_bytes=999)
        h, s = check(app)
        checks.append(("one byte over budget FAILS", len(h) == 1 and "EXCEEDS" in h[0]))

        budget(max_bytes=1_000_000)
        h, s = check(app)
        checks.append(("loose budget is SOFT, not HARD", not h and len(s) == 1))

        budget(glob="dist/assets/*.nope")
        h, s = check(app)
        checks.append(("budget matching no file FAILS", len(h) == 1 and "cannot fail" in h[0]))

        budget()
        del_entry = json.loads((app / BUDGET_FILENAME).read_text())
        del del_entry["assets"][0]["reason"]
        (app / BUDGET_FILENAME).write_text(json.dumps(del_entry))
        h, s = check(app)
        checks.append(("entry missing 'reason' FAILS", len(h) == 1 and "missing required" in h[0]))

        budget()
        (app / BUDGET_FILENAME).unlink()
        h, s = check(app)
        checks.append(("absent budget file FAILS", len(h) == 1 and "no bundle budget" in h[0]))

        budget()
        gz_probe = gzip_size(js)
        checks.append(("gzip size is measured, not guessed", 0 < gz_probe < 1000))

        budget(max_gzip_bytes=1)
        h, s = check(app)
        checks.append(("gzip budget exceeded is SOFT only", not h and any("gzipped" in x for x in s)))

    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in checks if not ok]
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} checks passed")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("app_dir", nargs="?", help="the Code App root (contains dist/ and bundle-budget.json)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.app_dir:
        ap.error("app_dir is required unless --selftest is given")

    app_dir = Path(args.app_dir)
    if not app_dir.is_dir():
        print(f"verify-code-app-bundle-budget: FAILED — {app_dir} is not a directory")
        return 1

    hard, soft = check(app_dir)
    for f in soft:
        print(f"WARNING: {f}")
    for f in hard:
        print(f"ERROR: {f}")

    if hard:
        print(f"verify-code-app-bundle-budget: FAILED — {len(hard)} budget violation(s) in {app_dir}")
        return 1
    print(
        f"verify-code-app-bundle-budget: PASS — {app_dir} within declared budget"
        + (f", {len(soft)} advisory" if soft else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
