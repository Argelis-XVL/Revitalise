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

PER-OPERATION MARKERS (IMP-0484, added 2026-08-29). A third marker joins the two above:

    WRITE BEGUN: provisioning/dataverse/ensure-schema.ps1 -Env dev

`agents/pipeline-agent.md` now requires it to be appended IMMEDIATELY BEFORE each live write, with
the `WRITE ATTEMPTED:` outcome line immediately after. The reason is a death, not tidiness: on
2026-08-28 a pipeline-agent dispatch created a table, four attributes, an alternate key, two role
privilege grants, an audit switch and a seed row in DEV and then died before composing its
end-of-stage entry, leaving ZERO log trace. Log absence was read as write absence and the
reconciliation concluded there was "nothing to reconcile". A dangling `WRITE BEGUN:` would have
said otherwise.

So this gate treats the new marker three ways, and the third is the load-bearing one:

  (a) a WRITE BEGUN is a provisioning write for the preflight-pairing rule above — begun with no
      PREFLIGHT fails exactly as attempted-with-no-PREFLIGHT does;
  (b) it is an INTENT line, so the outcome vocabulary is NOT applied to it. Reusing
      `WRITE ATTEMPTED: … — STARTED` was measured first and turns this gate red on the
      well-formed case, because WRITE_OUTCOME is applied to every WRITE ATTEMPTED body. A
      convention that reddens a HARD gate on its own correct use gets routed around;
  (c) a WRITE BEGUN with no matching WRITE ATTEMPTED is reported as a NOTE naming the script and
      environment, and is NEVER a failure. That dangling marker is the death signature this whole
      convention exists to preserve — failing on it would teach dispatches to withhold the line
      until the outcome is known, which is the batching this replaced.

Without (a) and (c) the marker would be inert here, and an entry plainly recording a write
beginning would print "0 with a provisioning write" — a new gate-reassures-wrongly surface
manufactured by the fix.

FORWARD-ONLY, and honestly so: no entry in the corpus uses WRITE BEGUN yet, so this changes no
verdict on any existing entry. It is load-bearing from the first dispatch that emits the marker.

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
# The intent line, appended BEFORE the write. Deliberately its own keyword rather than a new
# outcome token on WRITE ATTEMPTED — see (b) in the docstring, which was measured, not reasoned.
WRITE_BEGUN = re.compile(r"^\s*WRITE BEGUN:\s*(?P<body>.+)$", re.MULTILINE)

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


def operation_key(body: str) -> str:
    """The '<script> -Env <env>' half of a marker body, without its outcome.

    A BEGUN line and its ATTEMPTED line describe one operation and differ only in what follows
    the em dash, so the text before it is what pairs them. Compared case-insensitively on
    collapsed whitespace: these lines are hand-written by an agent, and pairing must not fail on
    a double space.
    """
    head = re.split(r"\s+[—–-]\s+", body, maxsplit=1)[0]
    return " ".join(head.split()).casefold()


def check_text(text: str, required_from: str = REQUIRED_FROM
               ) -> tuple[list[str], list[str], dict]:
    """(failures, notes, stats). Notes are reported and never fail the gate."""
    errors: list[str] = []
    notes: list[str] = []
    stats = {"entries": 0, "judged": 0, "with_write": 0, "with_preflight": 0, "skipped_old": 0,
             "dangling_begun": 0}

    for date, body in entries(text):
        stats["entries"] += 1
        if date <= required_from:
            stats["skipped_old"] += 1
            continue
        stats["judged"] += 1

        writes = [m.group("body").strip() for m in WRITE_ATTEMPTED.finditer(body)]
        begun = [m.group("body").strip() for m in WRITE_BEGUN.finditer(body)]
        preflights = [m.group("body").strip() for m in PREFLIGHT.finditer(body)]
        if preflights:
            stats["with_preflight"] += 1
        if not writes and not begun:
            continue
        # (a) A begun write is a provisioning write. Counting only completed ones would print
        #     "0 with a provisioning write" over a log recording one starting.
        stats["with_write"] += 1

        if not preflights:
            first = (writes or begun)[0]
            errors.append(
                f"[{date}] reports {len(writes) + len(begun)} provisioning write(s) — first is "
                f"'{first[:70]}' — and no PREFLIGHT line. C-TECH-065 requires the "
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
        # (b) The outcome vocabulary applies to WRITE ATTEMPTED only. A WRITE BEGUN states an
        #     intent; demanding an outcome of it is what reddens the well-formed case.
        for w in writes:
            if not WRITE_OUTCOME.search(w):
                errors.append(
                    f"[{date}] WRITE ATTEMPTED line states no outcome: '{w[:70]}'. It must "
                    f"carry SUCCEEDED, FAILED or REFUSED.")

        # (c) A begun write with no outcome line is the death signature. Report it; never fail.
        settled = {operation_key(w) for w in writes}
        for b in begun:
            if operation_key(b) not in settled:
                stats["dangling_begun"] += 1
                notes.append(
                    f"[{date}] WRITE BEGUN with no matching WRITE ATTEMPTED: '{b[:90]}'. The "
                    f"session recorded starting this write and never recorded its outcome, "
                    f"which is what a mid-operation death looks like (IMP-0484). This is NOT a "
                    f"failure. Reconcile it by verifying LIVE STATE — the idempotent "
                    f"provisioning script reports EXISTS/CREATED per component — per "
                    f"agents/WORKFLOW.md 'the fourth case', rule 1.")

    return errors, notes, stats


def selftest() -> int:
    failures: list[str] = []

    good = (
        "[2026-08-25 09:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId abc-123)\n"
        "WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — SUCCEEDED\n"
    )
    errors, notes, stats = check_text(good)
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
    errors, _, _ = check_text(bad)
    if len(errors) != 1 or "no PREFLIGHT line" not in errors[0]:
        failures.append(f"a write with no preflight must fail once, got: {errors}")

    # The false positive this gate was designed to avoid: prose naming scripts never attempted.
    prose = (
        "[2026-08-25 09:58] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "share-apps.ps1 and bind-roles-to-groups.ps1's DEV steps remain dead-as-declared, "
        "not re-attempted. ensure-schema.ps1 was not run this dispatch.\n"
    )
    errors, _, stats = check_text(prose)
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
    errors, _, _ = check_text(no_outcome)
    if len(errors) != 2:
        failures.append(f"expected 2 outcome errors, got {len(errors)}: {errors}")

    # Forward-only: the same defect before the convention existed is not judged.
    old = bad.replace("2026-08-25", "2026-08-23")
    errors, _, stats = check_text(old)
    if errors:
        failures.append(f"a pre-convention entry must be skipped, got: {errors}")
    if stats["skipped_old"] != 1:
        failures.append(f"forward-only accounting wrong: {stats}")

    # ── WRITE BEGUN, the per-operation marker (IMP-0484) ──────────────────────────────────
    # The well-formed case: begun, then settled. This is the fixture that the rejected
    # "WRITE ATTEMPTED: … — STARTED" design turned RED, which is why the keyword is distinct.
    begun_settled = (
        "[2026-08-29 09:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId abc-123)\n"
        "WRITE BEGUN: provisioning/dataverse/ensure-schema.ps1 -Env dev\n"
        "WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — SUCCEEDED\n"
    )
    errors, notes, stats = check_text(begun_settled)
    if errors or notes:
        failures.append(f"a begun-then-settled write must pass with no note, got: "
                        f"{errors} / {notes}")
    if stats["with_write"] != 1:
        failures.append(f"a settled begun write must count as a write: {stats}")

    # The death signature: begun and never settled. A NOTE, never a failure, and the entry
    # still counts as carrying a provisioning write.
    dangling = (
        "[2026-08-29 09:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId abc-123)\n"
        "WRITE BEGUN: provisioning/dataverse/ensure-schema.ps1 -Env dev\n"
    )
    errors, notes, stats = check_text(dangling)
    if errors:
        failures.append(f"a dangling WRITE BEGUN must NOT fail the gate, got: {errors}")
    if len(notes) != 1 or "no matching WRITE ATTEMPTED" not in notes[0]:
        failures.append(f"a dangling WRITE BEGUN must produce one note, got: {notes}")
    if "ensure-schema.ps1 -Env dev" not in (notes[0] if notes else ""):
        failures.append("the note must name the script and the environment")
    if stats["with_write"] != 1 or stats["dangling_begun"] != 1:
        failures.append(f"a dangling begun write must still count as a write: {stats}")

    # (a): a begun write with no preflight fails exactly as an attempted one does.
    begun_no_preflight = (
        "[2026-08-29 09:00] [PIPELINE] [feat] [DEV] SUCCESS\n"
        "WRITE BEGUN: provisioning/dataverse/ensure-schema.ps1 -Env dev\n"
    )
    errors, _, _ = check_text(begun_no_preflight)
    if len(errors) != 1 or "no PREFLIGHT line" not in errors[0]:
        failures.append(f"a begun write with no preflight must fail once, got: {errors}")

    if failures:
        print("verify-provisioning-report --selftest: FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("verify-provisioning-report --selftest: PASS — 8 fixtures (complete report; write "
          "with no preflight; prose mention not an attempt; outcome-less claims; forward-only; "
          "WRITE BEGUN settled; WRITE BEGUN dangling is a NOTE not a failure; WRITE BEGUN with "
          "no preflight fails)")
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

    errors, notes, stats = check_text(target.read_text(encoding="utf-8"))
    # Notes print in both directions. A dangling WRITE BEGUN is the one signal this gate exists
    # to surface, and burying it under a FAILED header would lose it.
    for n in notes:
        print(f"  NOTE {n}")
    if errors:
        print("verify-provisioning-report: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1

    dangling = (f"; {stats['dangling_begun']} WRITE BEGUN marker(s) with no recorded outcome — "
                f"see the NOTE(s) above, and verify live state"
                if stats["dangling_begun"] else "")
    print(f"verify-provisioning-report: PASS — {stats['judged']} entry(ies) judged "
          f"({stats['with_write']} with a provisioning write, all carrying a preflight "
          f"result); {stats['skipped_old']} predate the {REQUIRED_FROM} report-back "
          f"convention and are not judged{dangling}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
