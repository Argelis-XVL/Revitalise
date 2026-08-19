#!/usr/bin/env python3
"""Validate logs/improvement-log.jsonl, and enforce the loop's own processing triggers.

WHY THIS EXISTS. `agents/WORKFLOW.md` -> Processing triggers says an improvement review runs
immediately on any `blocker`-severity entry, and at the next routing decision once ten `NEW`
entries have accumulated. Both rules lived only as prose in an agent file, and both have now
failed twice:

  * 2026-08-18 — IMP-0033: all 32 entries carried `status: NEW`, including 23 whose proposed
    change had already shipped. Four one-line knowledge proposals sat unapplied for four days
    because nobody could tell "nothing was learned" from "nobody did the bookkeeping".
  * 2026-08-19 — 23 `NEW` entries, seven of them `blocker`, with both triggers standing.
    The digest was current, every gate was green, and the queue was simply not read.

That is `gate-cannot-fail` at the system's own altitude. This project's own evidence
(constraints/README.md rule 5, C-TECH-060) is that a rule becomes effective when a script
runs it, not when it is written down. This is that script.

WHAT IT CHECKS.

  Schema (always):
    * every line parses as JSON and is an object
    * required fields present: id, ts, agent, feature, class, severity, what, expected,
      root_cause, detected_by, why_it_was_never_caught, class_instance_of, lesson,
      proposed_change, status
    * `id` matches IMP-nnnn and is unique
    * `severity` in {friction, rework, blocker}
    * `status` in {NEW, APPLIED, REJECTED}
    * `ts` starts with an ISO date
    * an APPLIED entry names what applied it (`applied_by` or `reviewed_in`)
    * a REJECTED entry carries a `rejected_reason`
    * a deferred NEW entry carries a `deferred_reason` — "no silent caps" applies to the
      queue as much as to a review

  Triggers (--check only):
    * zero `NEW` entries of severity `blocker`
    * fewer than TRIGGER_BATCH `NEW` entries in total

Run:
    python3 scripts/verify-improvement-log.py                  # schema only
    python3 scripts/verify-improvement-log.py --check          # schema + triggers (CI)
    python3 scripts/verify-improvement-log.py --log <path>     # non-default log (tests)

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when the
log is missing or empty, so it cannot report OK over nothing (IMP-0007).

Wired into .github/workflows/ci.yml -> validate, beside the C-TECH-059 digest check.
C-TECH-061.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_LOG = Path("logs/improvement-log.jsonl")

# Ten is WORKFLOW.md's batch trigger. Changing it here changes what CI enforces, so it is
# named once and referenced, never transcribed into a second place.
TRIGGER_BATCH = 10

ID_PATTERN = re.compile(r"^IMP-\d{4}$")
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}")

REQUIRED_FIELDS = (
    "id", "ts", "agent", "feature", "class", "severity", "what", "expected",
    "root_cause", "detected_by", "why_it_was_never_caught", "class_instance_of",
    "lesson", "proposed_change", "status",
)

VALID_SEVERITY = {"friction", "rework", "blocker"}
VALID_STATUS = {"NEW", "APPLIED", "REJECTED"}


def load(log_path: Path) -> tuple[list[dict], list[str]]:
    """Return (rows, errors). A missing or empty log is an error, not an empty pass."""
    if not log_path.is_file():
        return [], [f"{log_path} does not exist. A gate pointed at a missing target must "
                    f"fail, not pass (IMP-0007)."]

    rows: list[dict] = []
    errors: list[str] = []
    for lineno, raw in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {lineno}: not valid JSON — {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"line {lineno}: expected a JSON object, got {type(row).__name__}")
            continue
        row["__line"] = lineno
        rows.append(row)

    if not rows and not errors:
        errors.append(f"{log_path} contains no entries. An empty finding log is either a "
                      f"brand-new project or a destroyed learning substrate (C-TECH-059) — "
                      f"this gate will not distinguish them by passing.")
    return rows, errors


def check_schema(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, int] = {}

    for row in rows:
        line = row.get("__line", "?")
        ident = row.get("id", f"(line {line})")

        missing = [f for f in REQUIRED_FIELDS if f not in row]
        if missing:
            errors.append(f"{ident}: missing required field(s): {', '.join(missing)} "
                          f"— schema in skills/how-to-log-an-improvement.md §2")

        if "id" in row:
            if not ID_PATTERN.match(str(row["id"])):
                errors.append(f"{ident}: id '{row['id']}' does not match IMP-nnnn")
            elif row["id"] in seen_ids:
                errors.append(f"{ident}: duplicate id — also on line {seen_ids[row['id']]}. "
                              f"Ids are the join key for the digest and every review document.")
            else:
                seen_ids[str(row["id"])] = line

        if "ts" in row and not DATE_PREFIX.match(str(row["ts"])):
            errors.append(f"{ident}: ts '{row['ts']}' does not start with an ISO date")

        severity = row.get("severity")
        if severity is not None and severity not in VALID_SEVERITY:
            errors.append(f"{ident}: severity '{severity}' is not one of "
                          f"{sorted(VALID_SEVERITY)}")

        status = row.get("status")
        if status is not None and status not in VALID_STATUS:
            errors.append(f"{ident}: status '{status}' is not one of {sorted(VALID_STATUS)}")

        if status == "APPLIED" and not (row.get("applied_by") or row.get("reviewed_in")):
            errors.append(f"{ident}: status APPLIED with neither 'applied_by' nor "
                          f"'reviewed_in' — an applied finding must name the change that "
                          f"applied it, or the next regression check has nothing to audit")

        if status == "REJECTED" and not row.get("rejected_reason"):
            errors.append(f"{ident}: status REJECTED with no 'rejected_reason'")

        change = row.get("proposed_change")
        if isinstance(change, dict):
            if "type" not in change:
                errors.append(f"{ident}: proposed_change has no 'type'")
        elif change is not None and not isinstance(change, str):
            errors.append(f"{ident}: proposed_change must be an object or a string")

    return errors


def check_triggers(rows: list[dict]) -> list[str]:
    """WORKFLOW.md -> Processing triggers, enforced rather than remembered."""
    errors: list[str] = []
    new_rows = [r for r in rows if r.get("status") == "NEW"]
    blockers = [r for r in new_rows if r.get("severity") == "blocker"]

    # A blocker carrying an explicit `deferred_reason` is a reviewer's decision, recorded
    # where the next review will read it — that is the "no silent caps" rule honoured, not
    # broken, so it does not trip the gate. A blocker with no reason is an unread queue.
    undeferred = [r for r in blockers if not r.get("deferred_reason")]

    if undeferred:
        ids = ", ".join(str(r.get("id")) for r in undeferred)
        errors.append(
            f"{len(undeferred)} NEW entry(ies) of severity 'blocker' with no "
            f"'deferred_reason': {ids}.\n"
            f"    agents/WORKFLOW.md -> Processing triggers: a blocker routes to "
            f"improvement-agent IMMEDIATELY — do not batch.\n"
            f"    Resolve by running an improvement review (gate: APPROVE IMPROVEMENTS), or "
            f"by recording an explicit 'deferred_reason' on each entry and re-running."
        )
    elif blockers:
        print(f"verify-improvement-log: NOTE — {len(blockers)} NEW blocker(s), each with an "
              f"explicit deferred_reason. Accepted as a reviewed deferral.", file=sys.stderr)

    # ── The batch trigger counts UNREVIEWED entries, not all NEW ones ──────────────────
    # The trigger's purpose is "nobody has looked at this". An entry carrying a
    # `deferred_reason` — and, by convention, a `revisit_when` — is proof that somebody did:
    # it was clustered, judged, and consciously not acted on, usually because
    # skills/how-to-promote-a-finding.md §2 forbids an instance patch for a class that needs
    # generalising. Counting those would make the gate permanently red for a system doing
    # exactly what its own promotion ladder asks, and a gate that cannot go green teaches
    # people to ignore it — the mirror image of a gate that cannot fail.
    #
    # IMP-0033, the incident behind this rule, was 23 entries with NO reasons on any of them.
    # That is what this counts.
    unreviewed = [r for r in new_rows if not r.get("deferred_reason")]

    if len(unreviewed) >= TRIGGER_BATCH:
        ids = ", ".join(str(r.get("id")) for r in unreviewed[:12])
        more = "" if len(unreviewed) <= 12 else f", +{len(unreviewed) - 12} more"
        errors.append(
            f"{len(unreviewed)} NEW entries with no 'deferred_reason' "
            f"(batch trigger is {TRIGGER_BATCH}): {ids}{more}.\n"
            f"    agents/WORKFLOW.md -> Processing triggers: route to improvement-agent at "
            f"the next routing decision.\n"
            f"    IMP-0033 is what an unprocessed queue looks like after four days — 23 "
            f"entries, none of them carrying a reason."
        )

    # Deferred work stays VISIBLE even though it does not fail the gate. A backlog that
    # stops being counted is a backlog that stops being revisited; "no silent caps" applies
    # to the queue as much as to a review's output.
    deferred = [r for r in new_rows if r.get("deferred_reason")]
    if deferred:
        no_revisit = [r for r in deferred if not r.get("revisit_when")]
        print(f"verify-improvement-log: NOTE — {len(deferred)} finding(s) deferred with a "
              f"recorded reason: {', '.join(str(r.get('id')) for r in deferred)}.",
              file=sys.stderr)
        if no_revisit:
            print(f"verify-improvement-log: NOTE — {len(no_revisit)} of those name no "
                  f"'revisit_when': {', '.join(str(r.get('id')) for r in no_revisit)}. A "
                  f"deferral with no trigger to come back is a decision to never do it.",
                  file=sys.stderr)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG,
                        help=f"path to the finding log (default: {DEFAULT_LOG})")
    parser.add_argument("--check", action="store_true",
                        help="also enforce WORKFLOW.md's processing triggers (CI mode)")
    args = parser.parse_args(argv)

    rows, errors = load(args.log)
    errors += check_schema(rows)

    trigger_errors = check_triggers(rows) if args.check else []

    if errors or trigger_errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for error in trigger_errors:
            print(f"TRIGGER: {error}", file=sys.stderr)
        total = len(errors) + len(trigger_errors)
        print(f"\nverify-improvement-log: FAILED — {total} problem(s) across "
              f"{len(rows)} entry(ies) in {args.log}.", file=sys.stderr)
        return 1

    counts = {
        "NEW": sum(1 for r in rows if r.get("status") == "NEW"),
        "APPLIED": sum(1 for r in rows if r.get("status") == "APPLIED"),
        "REJECTED": sum(1 for r in rows if r.get("status") == "REJECTED"),
    }
    mode = "schema + triggers" if args.check else "schema"
    print(f"verify-improvement-log: OK ({mode}) — {len(rows)} entries "
          f"({counts['NEW']} NEW, {counts['APPLIED']} APPLIED, "
          f"{counts['REJECTED']} REJECTED) in {args.log}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
