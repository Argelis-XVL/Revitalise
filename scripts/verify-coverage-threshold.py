#!/usr/bin/env python3
"""Enforce the C-TECH-014 line-coverage threshold as its OWN build step.

WHY THIS EXISTS. On 2026-08-21 the first full build since 08-19 failed C-TECH-014 at 67.78%
against an 80% threshold. Coverage had been 89.13% two days earlier. Four test-harness scripts
added on 08-20 (`remove-test-data.ps1`, `seed-test-data.ps1`, `test-data-common.psm1`,
`verify-test-data.ps1`) contributed 661 instructions with ZERO coverage; excluding them, the
figure is 1870 of 2098 = 89.13%, i.e. unchanged.

The regression is not the interesting part. The interesting part is that nothing said so for a
day and three deploys. `unit-tests` was ONE build step carrying TWO gates — a test-count gate
and a coverage gate — and a manifest's `gates_executed` holds one string per step. So the
08-20 manifests recorded `"unit-tests": "782 passed, 1 failed, 1 skipped"` and omitted the
percentage, and a manifest missing half a step's result still looked complete. A HARD
constraint went from passing to failing and no artifact in the repository says so (IMP-0132,
the seventeenth instance of `gate-cannot-fail`).

THE FIX IS STRUCTURAL, NOT A BIGGER WARNING. Coverage is now its own named step. Two gates in
one step can hide one result; two steps cannot hide a step. `unit-tests` still runs Pester and
still fails on a failing test, but it no longer owns the threshold — this does, and it reads
the JaCoCo report Pester already writes rather than re-running a 37-second suite.

WHAT IT CHECKS. The line counters in a JaCoCo `coverage.xml`, aggregated over every measured
source file, against a threshold passed on the command line — never defaulted silently, because
a number living in both a document and a script default drifts and the path that passes it
explicitly hides the drift (IMP-0051).

THE EXCLUSION LIST, AND WHY IT IS NARROW. `--exclusions` names a JSON file enumerating source
files that are measured by the runner but must not count toward the threshold. It exists for
ONE category: scripts that are themselves verification harness, where line coverage is the
wrong instrument. `verify-test-data.ps1` reporting PASS over wrong data is the
`gate-cannot-fail` class, and a known-bad fixture proving it reports FAIL is a stronger
guarantee for that file than 80% of its lines being executed by a mock.

So the exclusion is not a waiver and it is not open-ended:

  * every entry carries a `reason` and a `proven_able_to_fail` naming the fixture or test that
    substitutes for the coverage — an entry missing either FAILS this gate;
  * `proven_able_to_fail: null` is accepted ONLY with a `deferred_to` and a dated `expires`,
    and an expired entry FAILS. That is the `known-exceptions.json` shape, for the same reason:
    a gate switched off because reality violates it is `gate-cannot-fail` arriving by the front
    door;
  * the count is capped (`_max_entries`) so the carve-out cannot quietly become the norm.

Run:
    python3 scripts/verify-coverage-threshold.py <coverage.xml> --threshold 80 \\
        --exclusions src/tests/coverage-exclusions.json
    python3 scripts/verify-coverage-threshold.py --selftest    # prove the gate can fail

Exits 0 when coverage meets the threshold, 1 on any violation or unreadable input, 2 on a
usage error. Fails — never passes — on a report with no measured lines, so it cannot report OK
over an empty run (IMP-0007). C-TECH-014, C-TECH-057.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ── Reading the JaCoCo report ────────────────────────────────────────────────
# Pester writes one <class> per source file, with the file's path (no extension) in @name and
# a <counter type="LINE" missed=".." covered=".."> child. Aggregating the LINE counters
# reproduces Pester's own CoveragePercent, which is what C-TECH-014 is written against.


def _read_line_counters(report: Path) -> dict[str, tuple[int, int]]:
    """Return {source-name: (missed, covered)} for every measured file."""
    try:
        root = ET.parse(report).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError(f"{report} is not a readable JaCoCo report: {exc}") from exc

    per_file: dict[str, tuple[int, int]] = {}
    for cls in root.iter("class"):
        name = (cls.get("name") or "").replace("\\", "/")
        if not name:
            continue
        for counter in cls.findall("counter"):
            if counter.get("type") != "LINE":
                continue
            missed = int(counter.get("missed") or 0)
            covered = int(counter.get("covered") or 0)
            prev = per_file.get(name, (0, 0))
            per_file[name] = (prev[0] + missed, prev[1] + covered)
    return per_file


# ── Reading and validating the exclusion list ────────────────────────────────


def _load_exclusions(path: Path | None) -> tuple[list[dict], list[str]]:
    """Return (entries, errors). An invalid list is a gate failure, never a silent pass."""
    if path is None:
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], [f"{path} is not readable JSON: {exc}"]

    entries = data.get("exclusions")
    if not isinstance(entries, list):
        return [], [f"{path} declares no 'exclusions' list"]

    errors: list[str] = []
    cap = data.get("_max_entries")
    if not isinstance(cap, int):
        errors.append(f"{path} declares no integer '_max_entries' cap — an uncapped carve-out "
                      "is a waiver")
    elif len(entries) > cap:
        errors.append(f"{path} holds {len(entries)} exclusion(s) against its own cap of {cap}")

    today = _dt.date.today()
    for entry in entries:
        source = entry.get("source", "<unnamed>")
        if not entry.get("reason"):
            errors.append(f"exclusion '{source}' carries no 'reason'")
        proof = entry.get("proven_able_to_fail")
        if proof:
            continue
        # No substitute proof yet — allowed only as a dated, owned deferral.
        if not entry.get("deferred_to"):
            errors.append(f"exclusion '{source}' has no 'proven_able_to_fail' and no "
                          "'deferred_to' owner — that is a waiver, not an exclusion")
        expires = entry.get("expires")
        if not expires:
            errors.append(f"exclusion '{source}' has no 'proven_able_to_fail' and no 'expires' "
                          "— an exception with no expiry never clears")
            continue
        try:
            if _dt.date.fromisoformat(expires) < today:
                errors.append(f"exclusion '{source}' EXPIRED on {expires} — it needs the "
                              "substitute proof, or a re-dated decision")
        except ValueError:
            errors.append(f"exclusion '{source}' has an unparseable 'expires' value {expires!r}")
    return entries, errors


def _matches(source_name: str, pattern: str) -> bool:
    """JaCoCo @name carries no extension, so compare on the extension-stripped path."""
    stripped = pattern.rsplit(".", 1)[0] if pattern.endswith((".ps1", ".psm1")) else pattern
    return source_name == stripped.replace("\\", "/")


# ── The gate ─────────────────────────────────────────────────────────────────


def run(report: Path, threshold: float, exclusions_path: Path | None) -> int:
    try:
        per_file = _read_line_counters(report)
    except ValueError as exc:
        print(f"coverage-threshold: FAILED — {exc}", file=sys.stderr)
        return 1

    if not per_file:
        print(f"coverage-threshold: FAILED — {report} measures no source files at all. A gate "
              "that finds nothing to check and reports OK is IMP-0007's defect.", file=sys.stderr)
        return 1

    entries, errors = _load_exclusions(exclusions_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\ncoverage-threshold: FAILED — the exclusion list is invalid, so no coverage "
              f"figure from it can be trusted ({len(errors)} problem(s)).", file=sys.stderr)
        return 1

    patterns = [e.get("source", "") for e in entries]
    counted: dict[str, tuple[int, int]] = {}
    excluded: dict[str, tuple[int, int]] = {}
    for name, counts in per_file.items():
        if any(_matches(name, p) for p in patterns if p):
            excluded[name] = counts
        else:
            counted[name] = counts

    missed = sum(m for m, _ in counted.values())
    covered = sum(c for _, c in counted.values())
    total = missed + covered
    if total == 0:
        print("coverage-threshold: FAILED — every measured file is excluded, so the threshold "
              "is being applied to nothing.", file=sys.stderr)
        return 1

    percent = round(covered / total * 100, 2)

    print(f"coverage-threshold: {covered} of {total} line(s) covered = {percent}% "
          f"(threshold {threshold}%)")
    print(f"  files counted : {len(counted)}")
    if excluded:
        ex_missed = sum(m for m, _ in excluded.values())
        ex_covered = sum(c for _, c in excluded.values())
        print(f"  files excluded: {len(excluded)} — {ex_covered} of "
              f"{ex_missed + ex_covered} line(s); each carries a reason and a substitute proof")
        for name in sorted(excluded):
            entry = next((e for e in entries if _matches(name, e.get("source", ""))), {})
            proof = entry.get("proven_able_to_fail") or (
                f"DEFERRED to {entry.get('deferred_to')}, expires {entry.get('expires')}")
            print(f"      {name} — {proof}")

    if percent < threshold:
        print(f"\ncoverage-threshold: FAILED — {percent}% is below the {threshold}% threshold in "
              "knowledge/technology/coding-standards.md (C-TECH-014).", file=sys.stderr)
        return 1
    return 0


# ── Self-test: the gate must be able to fail (C-TECH-057) ────────────────────

_GOOD = """<?xml version="1.0"?><report name="t"><package name="p">
<class name="provisioning/dataverse/a"><counter type="LINE" missed="1" covered="9"/></class>
</package></report>"""
_BAD = """<?xml version="1.0"?><report name="t"><package name="p">
<class name="provisioning/dataverse/a"><counter type="LINE" missed="9" covered="1"/></class>
</package></report>"""
_EMPTY = """<?xml version="1.0"?><report name="t"><package name="p"></package></report>"""


def selftest() -> int:
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        good, bad, empty = tmpdir / "g.xml", tmpdir / "b.xml", tmpdir / "e.xml"
        good.write_text(_GOOD, encoding="utf-8")
        bad.write_text(_BAD, encoding="utf-8")
        empty.write_text(_EMPTY, encoding="utf-8")

        checks.append(("90% passes an 80% threshold", run(good, 80, None) == 0))
        checks.append(("10% FAILS an 80% threshold", run(bad, 80, None) == 1))
        checks.append(("a report measuring nothing FAILS", run(empty, 80, None) == 1))
        checks.append(("a missing report FAILS", run(tmpdir / "nope.xml", 80, None) == 1))

        # An exclusion can rescue the bad report — and only when it is well formed.
        ok_list = tmpdir / "ok.json"
        ok_list.write_text(json.dumps({"_max_entries": 4, "exclusions": [
            {"source": "provisioning/dataverse/a.ps1", "reason": "harness",
             "proven_able_to_fail": "fixture x"}]}), encoding="utf-8")
        checks.append(("excluding every file FAILS rather than passing on nothing",
                       run(bad, 80, ok_list) == 1))

        no_reason = tmpdir / "nr.json"
        no_reason.write_text(json.dumps({"_max_entries": 4, "exclusions": [
            {"source": "provisioning/dataverse/b.ps1", "proven_able_to_fail": "x"}]}),
            encoding="utf-8")
        checks.append(("an exclusion with no reason FAILS", run(good, 80, no_reason) == 1))

        waiver = tmpdir / "w.json"
        waiver.write_text(json.dumps({"_max_entries": 4, "exclusions": [
            {"source": "provisioning/dataverse/b.ps1", "reason": "r"}]}), encoding="utf-8")
        checks.append(("an exclusion with no proof and no owner FAILS", run(good, 80, waiver) == 1))

        expired = tmpdir / "x.json"
        expired.write_text(json.dumps({"_max_entries": 4, "exclusions": [
            {"source": "provisioning/dataverse/b.ps1", "reason": "r", "deferred_to": "dev",
             "expires": "2000-01-01"}]}), encoding="utf-8")
        checks.append(("an EXPIRED exclusion FAILS", run(good, 80, expired) == 1))

        uncapped = tmpdir / "u.json"
        uncapped.write_text(json.dumps({"exclusions": [
            {"source": "provisioning/dataverse/b.ps1", "reason": "r",
             "proven_able_to_fail": "x"}]}), encoding="utf-8")
        checks.append(("an uncapped exclusion list FAILS", run(good, 80, uncapped) == 1))

    print("\n── SELFTEST ────────────────────────────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [label for label, passed in checks if not passed]
    if failed:
        print(f"\ncoverage-threshold selftest: FAILED — {len(failed)} check(s)", file=sys.stderr)
        return 1
    print(f"\ncoverage-threshold selftest: OK — {len(checks)} check(s); the gate can fail.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True, description=__doc__)
    parser.add_argument("report", nargs="?", help="JaCoCo coverage.xml written by Pester")
    parser.add_argument("--threshold", type=float,
                        help="minimum line coverage percent; never defaulted (IMP-0051)")
    parser.add_argument("--exclusions", help="JSON file enumerating files not counted")
    parser.add_argument("--selftest", action="store_true",
                        help="prove this gate can fail, then exit")
    args = parser.parse_args(argv[1:])

    if args.selftest:
        return selftest()
    if not args.report or args.threshold is None:
        parser.print_usage(sys.stderr)
        print("coverage-threshold: both a report path and --threshold are required.",
              file=sys.stderr)
        return 2
    return run(Path(args.report), args.threshold,
               Path(args.exclusions) if args.exclusions else None)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
