#!/usr/bin/env python3
"""A dispatch that attempted a provisioning write must record its access preflight.

WHY THIS EXISTS (IMP-0252, IMP-0245). `C-TECH-065` requires a read-only identity probe
(`provisioning/dataverse/verify-environment-access.ps1`) before any script is trusted against a
target environment, and `verify-pipeline-config.py` check 12 enforces it -- over the CONFIG FILE.
The config is correct: all three environments declare the probe first. What no gate could see is
whether the SESSION ran it, and a dispatch that executes only a slice of the pipeline skipped it:
the 2026-08-23 18:35 Stage 0.5 entry went from a pre-state read straight to a refused write, with
no probe result anywhere, and that session is the direct predecessor of the refused dispatch in
IMP-0252.

So this gate reads the report-back instead of the plan. `agents/pipeline-agent.md` ->
"Reviewer-Executed Operations" -> *The report-back block* requires two structured markers in the
`logs/pipeline.log` entry:

    PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId <guid>)
    WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — REFUSED <reason>

This gate fails when a WRITE ATTEMPTED marker has no PREFLIGHT marker in the same entry.

IT PARSES THE MARKERS, NEVER THE PROSE, and that is deliberate. A draft of this check scraped the
log text for provisioning script names and immediately produced a false positive: the 2026-08-22
09:58 entry names `bind-roles-to-groups.ps1` and `share-apps.ps1` only to say their DEV steps
"remain dead-as-declared" -- mentioned, never attempted. A gate that cannot tell a mention from an
attempt is a gate that gets routed around.

FORWARD-ONLY from REQUIRED_FROM. The markers are a convention introduced on 2026-08-24; the 21
entries before it predate both the convention and, for four of them, the probe script itself.
Failing over finished work is how a gate teaches people to ignore it (IMP-0181).

No network, no credentials, no writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PIPELINE_LOG = REPO / "logs" / "pipeline.log"

# The convention's start date. An entry stamped on or before this is not judged.
REQUIRED_FROM = "2026-08-24"

ENTRY_STAMP = re.compile(r"^\[(\d{4}-\d{2}-\d{2})\s")
PREFLIGHT = re.compile(r"^\s*PREFLIGHT:\s*(?P<body>.+)$", re.MULTILINE)
WRITE_ATTEMPTED = re.compile(r"^\s*WRITE ATTEMPTED:\s*(?P<body>.+)$", re.MULTILINE)

# A preflight line must state an outcome, not merely name the script. "PREFLIGHT: ran it" is the
# shape this project's own history warns about: a claim where a result belongs (C-TECH-053).
PREFLIGHT_OUTCOME = re.compile(r"\b(PASS|FAIL|REFUSED)\b")
WRITE_OUTCOME = re.compile(r"\b(SUCCEEDED|FAILED|REFUSED)\b")


def entries(text: str) -> list[tuple[str, str]]:
    """Split the log into (date, entry-text). One entry per bracketed timestamp line."""
    out: list[tuple[str, str]] = []
    current_date: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        m = ENTRY_STAMP.match(line)
        if m:
            if current_date is not None:
                out.append((current_date, "\n".join(buf)))
            current_date = m.group(1)
            buf = [line]
        elif current_date is not None:
            buf.append(line)
    if current_date is not None:
        out.append((current_date, "\n".join(buf)))
    return out


def check_text(text: str, required_from: str = REQUIRED_FROM) -> tuple[list[str], dict]:
    errors: list[str] = []
    stats = {"entries": 0, "judged": 0, "with_write": 0, "with_preflight": 0, "skipped_old": 0}

    for date, body in entries(text):
        stats["entries"] += 1
        if date <= required_from:
            stats["skipped_old"] += 1
            continue
        stats["judged"] += 1

        writes = [m.group("body").strip() for m in WRITE_ATTEMPTED.finditer(body)]
        preflights = [m.group("body").strip() for m in PREFLIGHT.finditer(body)]
        if preflights:
            stats["with_preflight"] += 1
        if not writes:
            continue
        stats["with_write"] += 1

        if not preflights:
            errors.append(
                f"[{date}] reports {len(writes)} provisioning write attempt(s) — first is "
                f"'{writes[0][:70]}' — and no PREFLIGHT line. C-TECH-065 requires the "
                f"read-only access probe before the write, and the report is what proves the "
                f"session ran it. Run "
                f"`pwsh -NoProfile -File provisioning/dataverse/verify-environment-access.ps1 "
                f"-Env <env>` first, even for a single Stage 0.5 prerequisite (IMP-0252).")
            continue

        for pf in preflights:
            if not PREFLIGHT_OUTCOME.search(pf):
                errors.append(
                    f"[{date}] PREFLIGHT line states no outcome: '{pf[:70]}'. It must carry "
                    f"PASS, FAIL or REFUSED — naming the probe is a claim that it ran, not a "
                    f"result (C-TECH-053).")
        for w in writes:
            if not WRITE_OUTCOME.search(w):
                errors.append(
                    f"[{date}] WRITE ATTEMPTED line states no outcome: '{w[:70]}'. It must "
                    f"carry SUCCEEDED, FAILED or REFUSED.")

    return errors, stats


def selftest() -> int:
    failures: list[str] = []

    good = (
        "[2026-08-25 09:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId abc-123)\n"
        "WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — SUCCEEDED\n"
    )
    errors, stats = check_text(good)
    if errors:
        failures.append(f"a complete report must pass, got: {errors}")
    if stats["with_write"] != 1 or stats["with_preflight"] != 1:
        failures.append(f"stats wrong on the good fixture: {stats}")

    # The real defect: a write with no preflight.
    bad = (
        "[2026-08-25 18:35] [PIPELINE] [feat] [DEV] HELD — Stage 0.5\n"
        "WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — REFUSED "
        "auto mode classifier\n"
    )
    errors, _ = check_text(bad)
    if len(errors) != 1 or "no PREFLIGHT line" not in errors[0]:
        failures.append(f"a write with no preflight must fail once, got: {errors}")

    # The false positive this gate was designed to avoid: prose naming scripts never attempted.
    prose = (
        "[2026-08-25 09:58] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "share-apps.ps1 and bind-roles-to-groups.ps1's DEV steps remain dead-as-declared, "
        "not re-attempted. ensure-schema.ps1 was not run this dispatch.\n"
    )
    errors, stats = check_text(prose)
    if errors:
        failures.append(f"prose mentioning scripts must NOT be read as an attempt, got: {errors}")
    if stats["with_write"] != 0:
        failures.append("prose mention was counted as a write attempt")

    # A claim where a result belongs.
    no_outcome = (
        "[2026-08-25 10:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "PREFLIGHT: verify-environment-access.ps1 -Env dev — ran it\n"
        "WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — done\n"
    )
    errors, _ = check_text(no_outcome)
    if len(errors) != 2:
        failures.append(f"expected 2 outcome errors, got {len(errors)}: {errors}")

    # Forward-only: the same defect before the convention existed is not judged.
    old = bad.replace("2026-08-25", "2026-08-23")
    errors, stats = check_text(old)
    if errors:
        failures.append(f"a pre-convention entry must be skipped, got: {errors}")
    if stats["skipped_old"] != 1:
        failures.append(f"forward-only accounting wrong: {stats}")

    if failures:
        print("verify-provisioning-report --selftest: FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("verify-provisioning-report --selftest: PASS — 5 fixtures (complete report; write "
          "with no preflight; prose mention not an attempt; outcome-less claims; forward-only)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify logs/pipeline.log")
    ap.add_argument("--selftest", action="store_true", help="run built-in fixtures")
    ap.add_argument("path", nargs="?", default=None, help="log to check (default pipeline.log)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    target = Path(args.path) if args.path else PIPELINE_LOG
    if not target.exists():
        print(f"verify-provisioning-report: {target} not found", file=sys.stderr)
        return 2

    errors, stats = check_text(target.read_text(encoding="utf-8"))
    if errors:
        print("verify-provisioning-report: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"verify-provisioning-report: PASS — {stats['judged']} entry(ies) judged "
          f"({stats['with_write']} with a provisioning write, all carrying a preflight "
          f"result); {stats['skipped_old']} predate the {REQUIRED_FROM} report-back "
          f"convention and are not judged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
