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

THE FOUR STATES OF A `NEW` FINDING (added 2026-08-21 — IMP-0154, IMP-0169; review 5 item 7
and review 6 item 6, cluster G). A finding's real state is one of four things, and until today
the gate could represent two of them, because the blocker trigger had exactly one discharge
field (`deferred_reason`). Both missing states cost real money inside two days:

  * `unread`             — no `deferred_reason`, no `reviewed_in`. Nobody has looked.
                           FAIL: run an improvement review.
  * `awaiting-approval`  — `reviewed_in` names a document that EXISTS on disk. A review has
                           already clustered this and is parked at its own gate. Still a FAIL
                           — a stalled review must not go quiet — but the instruction is the
                           opposite one: read that document and send the keyword. IMP-0154 is
                           what the old message cost: a second strategic-tier session
                           re-derived a six-rung cluster analysis that was sitting in a file,
                           because "processed and awaiting approval" rendered as "unread".
  * `reviewer-deferred`  — `deferred_reason` present. A recorded decision with an owner and a
                           return condition. Accepted; NOTE, not a failure.
  * `already-fixed`      — the entry carries an `evidence_grep` whose needle IS present in the
                           tree. The fix shipped and the bookkeeping did not follow. IMP-0169:
                           this review was convened by a blocker whose fix was already
                           committed in the same working tree.

  Precedence, deliberately, is: already-fixed > reviewer-deferred > awaiting-approval > unread.
  `already-fixed` outranks a deferral because the tree contradicts the deferral — deferring
  work that is already done is stale bookkeeping, not a decision. `reviewer-deferred` outranks
  `awaiting-approval` because an explicit reason naming an owner and a return condition is a
  STRONGER discharge than "a document mentions this"; if the weaker signal won, a review could
  never record a deferral in the very document that made the decision without the gate
  immediately reopening it.

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
    * `reviewed_in` names a file that EXISTS — see below
    * an entry that carries `evidence_grep` is checked AGAINST THE FILE, not against the
      file's existence, with opposite meanings on APPLIED and NEW — see below
    * a REJECTED entry carries a `rejected_reason`
    * a deferred NEW entry carries a `deferred_reason` — "no silent caps" applies to the
      queue as much as to a review

  The `reviewed_in` field must resolve (added 2026-08-21 — IMP-0154):

    `reviewed_in` is now load-bearing: it is what separates "a review has processed this and
    is waiting for you" from "nobody has looked". A path that does not exist is a claim about
    a file, and this repository's rule for an APPLIED-style claim is that it is checked
    against file content, never assumed (IMP-0140). A stamp naming a document nobody wrote
    would hand the queue a third way to lie about its own state.

  The `evidence_grep` field (optional, added 2026-08-21 — IMP-0140, IMP-0145; inverted
  reading on a NEW entry added the same day — IMP-0169):

    {"status": "APPLIED", "applied_by": "...",
     "evidence_grep": {"file": "skills/how-to-write-a-test-plan.md",
                       "contains": "platform contract"}}

    An APPLIED status is a CLAIM, not a result — C-COM-005's rule, turned on this log's own
    bookkeeping. It had never been turned on, and it failed twice inside four days:

      * IMP-0140 — IMP-0111 was marked APPLIED with applied_by "skills/how-to-write-a-test-plan.md
        exists and carries the rule". The file existed at 102 lines and did not mention the rule.
      * IMP-0145 — IMP-0105 was marked APPLIED because a knowledge document was updated. The
        settings file the same finding named still held {{TENANT_ID}} a day later, and the next
        agent to trust that APPLIED status lost a session to it.

    Both were reconciled against a file's EXISTENCE. This field reconciles against its CONTENT.

    A `NEW` status is equally a claim — "this has not been done" — and it was equally
    unchecked. The field is therefore honoured on a NEW entry too, with its meaning INVERTED:

      status APPLIED  →  the needle being ABSENT  is the error (an unevidenced claim)
      status NEW      →  the needle being PRESENT is the error (the fix already shipped;
                         reconcile the status to APPLIED, or correct the needle)

    On a NEW entry a MISSING file is not an error: the file the fix will land in need not
    exist yet, and its absence is the expected pre-fix state. On an APPLIED entry a missing
    file is an error, as before.

    It is deliberately OPT-IN in both directions. Roughly 130 APPLIED entries predate it and
    retrofitting them is not a job this gate should force; an entry without the field behaves
    exactly as before. It can therefore never turn the gate red for an entry nobody annotated.

  Triggers (--check only):
    * zero `NEW` entries of severity `blocker` in state `unread` or `awaiting-approval`
    * fewer than TRIGGER_BATCH `NEW` entries in those same two states
    * a census of all four states, printed every run

  Citation-versus-stamp WARNING (--check only, added 2026-08-21 — IMP-0154):
    Every NEW finding a review document processes should carry `reviewed_in` naming that
    document. Reported as a WARNING, never a failure — the reasoning is at
    check_citation_stamps().

WHAT THIS STILL CANNOT SEE — three residual limitations, stated so the next agent does not
mistake a silence for a clean bill:

  * `already-fixed` only works where the fix has a greppable signature somebody thought to
    record in advance. A fix that shipped in a different shape than the finding predicted
    still reads as `unread`. Cluster G named this residual when it approved the change.
  * A review that stalls at its gate with NO blocker in it does not fail this gate. Its
    non-blocker entries are named in a NOTE (state `awaiting-approval`) and they still count
    toward the batch trigger, but nothing goes red until the tenth. Only the blocker rung is
    a FAIL, which is the scope review 5 item 7 approved.
  * `reviewed_in` is a single scalar. A finding processed by two reviews can name only one of
    them, so the citation check has to accept "this document or a later one" and can never be
    exact — see check_citation_stamps() for why that makes it a WARNING.

Run:
    python3 scripts/verify-improvement-log.py                  # schema only
    python3 scripts/verify-improvement-log.py --check          # schema + triggers (CI)
    python3 scripts/verify-improvement-log.py --log <path>     # non-default log (tests)
    python3 scripts/verify-improvement-log.py --selftest       # prove the four states differ

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when the
log is missing or empty, so it cannot report OK over nothing (IMP-0007).

Wired into .github/workflows/ci.yml -> validate, beside the C-TECH-059 digest check.
C-TECH-061.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

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

# ── Where reviews live, and what one is called ────────────────────────────────────────────
# Reviews are the only documents that PROCESS a finding. The design and redesign documents in
# the same directory cite findings as evidence for a narrative; holding them to a stamping
# rule would report 24 violations that are not defects.
REVIEWS_DIR = Path("docs/improvements")
REVIEW_DOC_GLOB = "*improvement-review*.md"

ID_IN_PROSE = re.compile(r"IMP-\d{4}")

# The four states a NEW finding can be in. Named once; the message text keys off these.
UNREAD = "unread"
AWAITING = "awaiting-approval"
DEFERRED = "reviewer-deferred"
SHIPPED = "already-fixed"


class Result(NamedTuple):
    """One run's whole verdict, so --selftest can assert on it without capturing stderr."""
    rc: int
    errors: list[str]
    triggers: list[str]
    warnings: list[str]
    notes: list[str]
    rows: list[dict]

    def text(self) -> str:
        return "\n".join(self.errors + self.triggers + self.warnings + self.notes)


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


# ── reviewed_in ───────────────────────────────────────────────────────────────────────────

def reviewed_in_paths(row: dict) -> list[str]:
    """The document(s) a finding says processed it. Scalar or list; both are accepted."""
    value = row.get("reviewed_in")
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def resolved_reviews(row: dict, repo_root: Path) -> tuple[list[str], list[str]]:
    """Split `reviewed_in` into (documents that exist, documents that do not)."""
    present, missing = [], []
    for rel in reviewed_in_paths(row):
        (present if (repo_root / rel).is_file() else missing).append(rel)
    return present, missing


def review_order_key(path: str) -> tuple[str, int] | None:
    """Chronological key for a review document, or None if it is not one.

    `2026-08-21-improvement-review.md` is the first review of that date and
    `-6.md` the sixth, so the ordinal cannot come from a lexicographic sort of the filename.
    """
    name = Path(path).name
    if not fnmatch.fnmatch(name, REVIEW_DOC_GLOB):
        return None
    date = DATE_PREFIX.match(name)
    ordinal = re.search(r"-(\d+)\.md$", name)
    return (date.group(0) if date else "0000-00-00", int(ordinal.group(1)) if ordinal else 1)


# ── evidence_grep ─────────────────────────────────────────────────────────────────────────

def check_evidence_grep(row: dict, ident: str, repo_root: Path) -> list[str]:
    """Verify an entry's status against the CONTENT of the file it names.

    IMP-0140 / IMP-0145 gave this field its APPLIED reading: both were APPLIED statuses
    reconciled against a file existing. 'The file is there' and 'the rule is in the file' are
    not the same fact, and this project has now paid for that twice.

    IMP-0169 gave it the inverted NEW reading: a NEW status is the claim "this has not been
    done", and that claim was unchecked. Same field, same needle, opposite verdict.
    """
    spec = row.get("evidence_grep")
    if spec is None:
        return []

    status = row.get("status")
    if status not in ("APPLIED", "NEW"):
        return [f"{ident}: carries 'evidence_grep' but status is {status!r}. The field "
                f"reconciles an APPLIED claim (needle must be present) or a NEW claim "
                f"(needle must be absent); on any other status it is a check that never runs."]

    if not isinstance(spec, dict):
        return [f"{ident}: evidence_grep must be an object "
                f"{{\"file\": ..., \"contains\": ...}}, got {type(spec).__name__}"]

    target = str(spec.get("file") or "").strip()
    needle = str(spec.get("contains") or "").strip()
    if not target or not needle:
        return [f"{ident}: evidence_grep needs both 'file' and 'contains'. A grep with no "
                f"needle is the existence check this field exists to replace."]

    path = repo_root / target
    if not path.is_file():
        # On a NEW entry the file the fix will land in need not exist yet — its absence IS
        # the expected pre-fix state, and reporting it would make the field unusable as a
        # forward watch. On an APPLIED entry the same absence is a false claim.
        if status == "NEW":
            return []
        return [f"{ident}: evidence_grep names '{target}', which does not exist. The entry "
                f"claims APPLIED against a file that is not there."]

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        # A check that cannot run must not pass silently, on either status.
        return [f"{ident}: evidence_grep cannot read '{target}' — {exc}"]

    found = needle in text
    if status == "APPLIED" and not found:
        return [f"{ident}: status APPLIED, but '{target}' does not contain "
                f"{needle!r}. The file exists; the substance does not. This is exactly "
                f"IMP-0140 — an APPLIED status is a claim, and this one is false."]
    if status == "NEW" and found:
        line = next((n for n, l in enumerate(text.splitlines(), start=1) if needle in l), "?")
        return [f"{ident}: status NEW, but '{target}':{line} ALREADY contains {needle!r}. "
                f"This finding's fix appears to have shipped — reconcile the status: move it "
                f"to APPLIED naming what applied it, or correct the needle if it matched "
                f"something else. IMP-0169: a review was convened by a blocker whose fix was "
                f"already committed in the same working tree."]
    return []


def evidence_says_shipped(row: dict, repo_root: Path) -> bool:
    """True when a NEW entry's own evidence_grep needle is already in the tree."""
    spec = row.get("evidence_grep")
    if not isinstance(spec, dict):
        return False
    target = str(spec.get("file") or "").strip()
    needle = str(spec.get("contains") or "").strip()
    if not target or not needle:
        return False
    path = repo_root / target
    if not path.is_file():
        return False
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def check_schema(rows: list[dict], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, int] = {}
    root = repo_root or Path.cwd()

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

        # `reviewed_in` decides whether a NEW finding reads as "a review has this" or as
        # "nobody has looked". A stamp is therefore a claim about a file, and this repository
        # checks such a claim against the file (IMP-0140), never assumes it.
        raw_stamp = row.get("reviewed_in")
        if raw_stamp is not None and not isinstance(raw_stamp, (str, list)):
            errors.append(f"{ident}: reviewed_in must be a path or a list of paths, got "
                          f"{type(raw_stamp).__name__}")
        else:
            _, absent = resolved_reviews(row, root)
            for rel in absent:
                errors.append(f"{ident}: reviewed_in names '{rel}', which does not exist. A "
                              f"stamp is a claim that a document processed this finding — an "
                              f"unresolvable one gives the queue a third way to lie about "
                              f"its own state (IMP-0154).")

        errors += check_evidence_grep(row, ident, root)

        if status == "REJECTED" and not row.get("rejected_reason"):
            errors.append(f"{ident}: status REJECTED with no 'rejected_reason'")

        change = row.get("proposed_change")
        if isinstance(change, dict):
            if "type" not in change:
                errors.append(f"{ident}: proposed_change has no 'type'")
        elif change is not None and not isinstance(change, str):
            errors.append(f"{ident}: proposed_change must be an object or a string")

    return errors


# ── the four states ───────────────────────────────────────────────────────────────────────

def classify(row: dict, repo_root: Path) -> tuple[str, str]:
    """Return (state, detail) for one NEW entry. Precedence is argued in the module docstring."""
    if evidence_says_shipped(row, repo_root):
        spec = row["evidence_grep"]
        return SHIPPED, f"{spec.get('file')} already contains {spec.get('contains')!r}"
    if row.get("deferred_reason"):
        present, _ = resolved_reviews(row, repo_root)
        where = f"; processed into {', '.join(present)}" if present else ""
        return DEFERRED, f"revisit_when: {row.get('revisit_when') or 'NOT RECORDED'}{where}"
    present, _ = resolved_reviews(row, repo_root)
    if present:
        return AWAITING, ", ".join(present)
    return UNREAD, ""


def check_triggers(rows: list[dict], repo_root: Path) -> tuple[list[str], list[str]]:
    """WORKFLOW.md -> Processing triggers, enforced rather than remembered.

    Returns (errors, notes).
    """
    errors: list[str] = []
    notes: list[str] = []
    new_rows = [r for r in rows if r.get("status") == "NEW"]
    states = {str(r.get("id")): classify(r, repo_root) for r in new_rows}

    def ids_in(state: str, only_blockers: bool = False) -> list[dict]:
        return [r for r in new_rows
                if states[str(r.get("id"))][0] == state
                and (not only_blockers or r.get("severity") == "blocker")]

    # ── The census. Every NEW entry lands in exactly one of four buckets, printed every run,
    # because the whole defect this replaces was a state the gate could not say out loud.
    notes.append(
        f"verify-improvement-log: NOTE — {len(new_rows)} NEW entry(ies): "
        f"{len(ids_in(UNREAD))} {UNREAD}, {len(ids_in(AWAITING))} {AWAITING}, "
        f"{len(ids_in(DEFERRED))} {DEFERRED}, {len(ids_in(SHIPPED))} {SHIPPED}."
    )

    # Every NEW entry is named by id somewhere in this output, not merely counted — a queue
    # reported only as a number is the queue nobody read (IMP-0033).
    unread = ids_in(UNREAD)
    if unread:
        notes.append(f"verify-improvement-log: NOTE — {len(unread)} finding(s) in state "
                     f"'{UNREAD}': {', '.join(str(r.get('id')) for r in unread)}. Nothing "
                     f"records that anyone has looked at these.")

    # ── STATE 1 of 4: unread blockers. The original trigger, message unchanged in substance.
    unread_blockers = ids_in(UNREAD, only_blockers=True)
    if unread_blockers:
        ids = ", ".join(str(r.get("id")) for r in unread_blockers)
        errors.append(
            f"{len(unread_blockers)} NEW entry(ies) of severity 'blocker' in state "
            f"'{UNREAD}' — no 'deferred_reason' and no 'reviewed_in': {ids}.\n"
            f"    agents/WORKFLOW.md -> Processing triggers: a blocker routes to "
            f"improvement-agent IMMEDIATELY — do not batch.\n"
            f"    Resolve by running an improvement review (gate: APPROVE IMPROVEMENTS), or "
            f"by recording an explicit 'deferred_reason' on each entry and re-running."
        )

    # ── STATE 2 of 4: blockers a review has already processed. SAME exit code, COMPLETELY
    # different instruction — that distinction is the entire point of this state existing.
    # IMP-0154: a strategic-tier session re-derived a six-rung cluster analysis that was
    # already written down, because the old message said "run a review" over a review that
    # had been run and was parked at its gate.
    awaiting_blockers = ids_in(AWAITING, only_blockers=True)
    if awaiting_blockers:
        lines = "\n".join(
            f"      {r.get('id')} -> {states[str(r.get('id'))][1]}" for r in awaiting_blockers)
        errors.append(
            f"{len(awaiting_blockers)} NEW entry(ies) of severity 'blocker' in state "
            f"'{AWAITING}' — a review has already processed these and is parked at its own "
            f"gate:\n{lines}\n"
            f"    DO NOT run another review and DO NOT re-derive the analysis. READ the "
            f"document(s) named above and respond APPROVE IMPROVEMENTS, or give feedback for "
            f"revision.\n"
            f"    This stays a FAIL because a stalled review must not go quiet — but the "
            f"remedy is a keyword, not a session (IMP-0154)."
        )

    # ── The batch trigger counts UNREAD and AWAITING entries, not all NEW ones ─────────────
    # The trigger's purpose is "this queue has unfinished business nobody has closed". An
    # entry carrying a `deferred_reason` — and, by convention, a `revisit_when` — is proof
    # somebody did look: it was clustered, judged, and consciously not acted on, usually
    # because skills/how-to-promote-a-finding.md §2 forbids an instance patch for a class that
    # needs generalising. Counting those would make the gate permanently red for a system
    # doing exactly what its own promotion ladder asks, and a gate that cannot go green
    # teaches people to ignore it — the mirror image of a gate that cannot fail.
    #
    # AWAITING entries are still counted. They are unfinished, and the pressure is correct;
    # what was wrong before was the instruction, not the exit code. `already-fixed` entries
    # are excluded here only because check_evidence_grep() already fails on each one with a
    # more specific message; they are not silent.
    #
    # IMP-0033, the incident behind this rule, was 23 entries with NO reasons on any of them.
    pending = ids_in(UNREAD) + ids_in(AWAITING)

    if len(pending) >= TRIGGER_BATCH:
        n_unread, n_awaiting = len(ids_in(UNREAD)), len(ids_in(AWAITING))
        ids = ", ".join(str(r.get("id")) for r in pending[:12])
        more = "" if len(pending) <= 12 else f", +{len(pending) - 12} more"
        errors.append(
            f"{len(pending)} NEW entries awaiting closure — {n_unread} {UNREAD}, "
            f"{n_awaiting} {AWAITING} (batch trigger is {TRIGGER_BATCH}): {ids}{more}.\n"
            f"    agents/WORKFLOW.md -> Processing triggers: route to improvement-agent at "
            f"the next routing decision — but read the state first. An "
            f"'{AWAITING}' entry needs the keyword sent against the document it names, not a "
            f"second review of the same findings.\n"
            f"    IMP-0033 is what an unprocessed queue looks like after four days — 23 "
            f"entries, none of them carrying a reason."
        )

    # ── STATE 3 of 4: reviewer-deferred. Accepted, and kept VISIBLE. A backlog that stops
    # being counted is a backlog that stops being revisited; "no silent caps" applies to the
    # queue as much as to a review's output.
    deferred = ids_in(DEFERRED)
    if deferred:
        notes.append(f"verify-improvement-log: NOTE — {len(deferred)} finding(s) deferred "
                     f"with a recorded reason, accepted as a reviewed deferral: "
                     f"{', '.join(str(r.get('id')) for r in deferred)}.")
        no_revisit = [r for r in deferred if not r.get("revisit_when")]
        if no_revisit:
            notes.append(f"verify-improvement-log: NOTE — {len(no_revisit)} of those name no "
                         f"'revisit_when': "
                         f"{', '.join(str(r.get('id')) for r in no_revisit)}. A deferral with "
                         f"no trigger to come back is a decision to never do it.")

    # A non-blocker entry parked behind a review's gate does not fail — the blocker rung
    # above does that — but it is named, so a stalled review with no blockers in it is at
    # least visible. Second residual limitation in the module docstring.
    awaiting_other = [r for r in ids_in(AWAITING) if r.get("severity") != "blocker"]
    if awaiting_other:
        notes.append(f"verify-improvement-log: NOTE — {len(awaiting_other)} non-blocker "
                     f"finding(s) in state '{AWAITING}': "
                     f"{', '.join(str(r.get('id')) for r in awaiting_other)}. Read the "
                     f"document each one names and send the keyword; do not re-derive.")

    # ── STATE 4 of 4: already fixed in the tree. The failing message lives in
    # check_evidence_grep(), which is where the evidence is read; this only names the state.
    shipped = ids_in(SHIPPED)
    if shipped:
        notes.append(f"verify-improvement-log: NOTE — {len(shipped)} finding(s) in state "
                     f"'{SHIPPED}': {', '.join(str(r.get('id')) for r in shipped)}. Each is "
                     f"reported as an ERROR below, with the file and line that proves it.")

    return errors, notes


# ── citation versus stamp ─────────────────────────────────────────────────────────────────

def processing_citations(text: str) -> set[str]:
    """Finding ids this document cites in a PROCESSING position.

    A review cites findings in two shapes that mean "I worked on this": the `Cites:` line of
    a cluster block, and the `Cites` column of the proposed-changes table. Everything else —
    "IMP-0033 is what an unprocessed queue looks like" — is prose citing a precedent, which is
    not a claim to have processed anything.
    """
    found: set[str] = set()
    cites_col: int | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("cites:"):
            found |= set(ID_IN_PROSE.findall(stripped))
            continue
        if not stripped.startswith("|"):
            cites_col = None          # tables are contiguous; a prose line ends one
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if "cites" in lowered:
            cites_col = lowered.index("cites")
            continue
        if cites_col is not None and cites_col < len(cells):
            found |= set(ID_IN_PROSE.findall(cells[cites_col]))
    return found


def check_citation_stamps(rows: list[dict], reviews_dir: Path) -> list[str]:
    """Every NEW finding a review document processed should carry `reviewed_in` naming it.

    THE INCIDENT (IMP-0154). Review 5 stamped `reviewed_in` on the entries it deferred and
    NOT on the finding about missing stamps that it appended itself. Five hours later a second
    strategic-tier session re-derived that finding's analysis, because an unstamped entry is
    indistinguishable from an unread one.

    WHY THIS IS A WARNING AND NOT A FAIL — three reasons, all of them about what the check can
    actually prove:

      1. A citation is not proof of processing. A cluster's `Cites:` line legitimately mixes
         the findings the cluster resolves with the precedents it learns from; IMP-0033 is
         cited by four reviews that processed none of it. A missing stamp is therefore
         evidence worth reading, not a demonstrated defect, and constraints/README.md reserves
         HARD for a rule whose violation is unambiguous.
      2. `reviewed_in` is a single scalar. A finding processed by review 3 and re-processed by
         review 6 can only name the later one, so the rule has to accept "this document or a
         later one" and can never be exact.
      3. The gate has to stay runnable. Failing here would put it permanently red over
         fifteen historical documents nobody is going to restamp — a gate that cannot go
         green teaches people to ignore it, which is the failure mode this file's own batch
         trigger already argues against.

    Scope is NEW entries only, and that is not a convenience. The harm is a finding that
    *reads as unread*; an APPLIED or REJECTED status already says out loud that someone
    processed it, so a missing stamp there costs bookkeeping tidiness, not a duplicated
    session. Ids cited by a review but absent from the log are skipped, so that pointing
    --log at a fixture reports nothing rather than everything.
    """
    if not reviews_dir.is_dir():
        return []

    docs = sorted(reviews_dir.glob(REVIEW_DOC_GLOB))
    if not docs:
        return []

    new_rows = {str(r.get("id")): r for r in rows if r.get("status") == "NEW"}
    cited_anywhere: dict[str, list[Path]] = {}
    cited_as_processed: dict[str, list[Path]] = {}
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ident in set(ID_IN_PROSE.findall(text)) & set(new_rows):
            cited_anywhere.setdefault(ident, []).append(doc)
        for ident in processing_citations(text) & set(new_rows):
            cited_as_processed.setdefault(ident, []).append(doc)

    warnings: list[str] = []
    for ident in sorted(cited_anywhere):
        row = new_rows[ident]
        stamps = reviewed_in_paths(row)
        # Newest first, chronologically — `-6.md` is the sixth review of a date, not a name
        # that sorts after `-.md`, so the ordering has to come from review_order_key().
        newest_first = sorted(cited_anywhere[ident],
                             key=lambda d: review_order_key(str(d)) or ("0000-00-00", 0),
                             reverse=True)
        where = ", ".join(d.name for d in newest_first[:3])
        if len(newest_first) > 3:
            where += ", …"

        if not stamps:
            warnings.append(
                f"{ident}: status NEW, cited by {len(cited_anywhere[ident])} review "
                f"document(s) ({where}) and carries NO 'reviewed_in'. Whoever reads the "
                f"queue next cannot tell this from a finding nobody has opened — stamp it "
                f"with the review that processed it (IMP-0154)."
            )
            continue

        if ident not in cited_as_processed:
            continue
        newest = max((review_order_key(str(d)) for d in cited_as_processed[ident]),
                     default=None)
        stamped = [k for k in (review_order_key(s) for s in stamps) if k is not None]
        if newest and stamped and max(stamped) < newest:
            docs_named = ", ".join(Path(s).name for s in stamps)
            processed_in = ", ".join(d.name for d in cited_as_processed[ident])
            warnings.append(
                f"{ident}: status NEW, processed by {processed_in} (named in a 'Cites' "
                f"position) but 'reviewed_in' still names the earlier {docs_named}. The "
                f"stamp should name the review that last worked on it (IMP-0154)."
            )

    return warnings


# ── run / selftest / main ─────────────────────────────────────────────────────────────────

def run(log_path: Path, repo_root: Path, check: bool,
        reviews_dir: Path | None = None) -> Result:
    rows, errors = load(log_path)
    errors = errors + check_schema(rows, repo_root)

    triggers: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    if check:
        triggers, notes = check_triggers(rows, repo_root)
        warnings = check_citation_stamps(rows, reviews_dir or (repo_root / REVIEWS_DIR))

    rc = 1 if (errors or triggers) else 0
    return Result(rc, errors, triggers, warnings, notes, rows)


# Every fixture below is (log rows, files to write into the fixture tree, expected rc,
# a string the output must contain). The four states are the first four cases, in order, so a
# reader can see at a glance that the gate distinguishes them — and the two "must pass" cases
# prove none of the four is simply always-red.
def _entry(**over) -> dict:
    row = {"id": "IMP-9001", "ts": "2026-08-21T00:00", "agent": "improvement-agent",
           "feature": "fixture", "class": "fixture-class", "severity": "blocker",
           "what": "w", "expected": "e", "root_cause": "r", "detected_by": "agent-self",
           "why_it_was_never_caught": "n", "class_instance_of": "c", "lesson": "l",
           "proposed_change": {"type": "script", "target": "x", "summary": "s"},
           "status": "NEW"}
    row.update(over)
    return row


_REVIEW = "docs/improvements/2026-08-21-improvement-review-9.md"
_LATER_REVIEW = "docs/improvements/2026-08-22-improvement-review-2.md"
_REVIEW_BODY = ("# fixture review\n\n```\nCites:      IMP-9001\n```\n\n"
                "| # | Change | Cites |\n|---|---|---|\n| 1 | a change | IMP-9001 |\n")

_CASES: dict[str, tuple[list[dict], dict[str, str], bool, int, str]] = {
    # name: (rows, files, use_check, expected_rc, expected substring)
    "STATE-1-unread": (
        [_entry()], {}, True, 1, "in state 'unread'"),
    "STATE-2-awaiting-approval": (
        [_entry(reviewed_in=_REVIEW)], {_REVIEW: _REVIEW_BODY}, True, 1,
        "DO NOT run another review"),
    "STATE-3-reviewer-deferred": (
        [_entry(deferred_reason="owner: reviewer", revisit_when="next review")], {}, True, 0,
        "accepted as a reviewed deferral"),
    "STATE-4-already-fixed": (
        [_entry(evidence_grep={"file": "scripts/x.py", "contains": "the fix"})],
        {"scripts/x.py": "line one\nhere is the fix\n"}, True, 1,
        "appears to have shipped"),
    # ── the same two fields, in the states where they must NOT fire ──
    "NEW-evidence-not-yet-shipped-must-pass": (
        [_entry(status="NEW", severity="friction",
                deferred_reason="waiting on the fix",
                evidence_grep={"file": "scripts/x.py", "contains": "the fix"})],
        {"scripts/x.py": "line one\nnothing here yet\n"}, True, 0, ""),
    "APPLIED-evidence-present-must-pass": (
        [_entry(status="APPLIED", applied_by="scripts/x.py",
                evidence_grep={"file": "scripts/x.py", "contains": "the fix"})],
        {"scripts/x.py": "here is the fix\n"}, False, 0, ""),
    "APPLIED-evidence-absent": (
        [_entry(status="APPLIED", applied_by="scripts/x.py",
                evidence_grep={"file": "scripts/x.py", "contains": "the fix"})],
        {"scripts/x.py": "nothing here yet\n"}, False, 1,
        "The file exists; the substance does not"),
    "REJECTED-evidence-grep-still-refused": (
        [_entry(status="REJECTED", rejected_reason="no",
                evidence_grep={"file": "scripts/x.py", "contains": "the fix"})],
        {"scripts/x.py": "here is the fix\n"}, False, 1, "a check that never runs"),
    # ── a stamp is a claim about a file (IMP-0140 turned on reviewed_in) ──
    "reviewed_in-names-a-document-that-does-not-exist": (
        [_entry(reviewed_in=_REVIEW)], {}, False, 1, "which does not exist"),
    # ── the citation-versus-stamp WARNING: visible, and never the exit code ──
    "citation-without-stamp-warns-but-passes": (
        [_entry(severity="friction", deferred_reason="owner: reviewer",
                revisit_when="next review")],
        {_REVIEW: _REVIEW_BODY}, True, 0, "carries NO 'reviewed_in'"),
    "stamp-older-than-the-review-that-processed-it": (
        [_entry(severity="friction", deferred_reason="owner: reviewer",
                revisit_when="next review", reviewed_in=_REVIEW),
         _entry(id="IMP-9002", severity="friction", status="APPLIED",
                applied_by="fixture")],
        {_REVIEW: _REVIEW_BODY, _LATER_REVIEW: _REVIEW_BODY}, True, 0,
        "still names the earlier"),
    # ── regression guards on the checks that predate all of this ──
    "duplicate-id-unknown-severity-missing-field": (
        [_entry(severity="catastrophic"), _entry(), {"id": "IMP-9003"}], {}, False, 1,
        "duplicate id"),
    "empty-log": ([], {}, False, 1, "contains no entries"),
    "batch-trigger": (
        [_entry(id=f"IMP-9{n:03d}", severity="friction") for n in range(100, 100 + TRIGGER_BATCH)],
        {}, True, 1, f"batch trigger is {TRIGGER_BATCH}"),
}


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (rows, files, check, want_rc, want_text) in _CASES.items():
            root = Path(tmp) / name
            root.mkdir(parents=True)
            for rel, body in files.items():
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(body, encoding="utf-8")
            log = root / "log.jsonl"
            log.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

            result = run(log, root, check)
            ok = result.rc == want_rc and (not want_text or want_text in result.text())
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {result.rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in result.text().splitlines():
                    print(f"                   {line}")

        # The missing-log case needs no tree at all (IMP-0007).
        missing = run(Path(tmp) / "no-such-log.jsonl", Path(tmp), False)
        ok = missing.rc == 1 and "does not exist" in missing.text()
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} nonexistent-log → exit {missing.rc} "
              f"(expected 1)")
        if not ok:
            failures.append("nonexistent-log")

    if failures:
        print(f"\nverify-improvement-log: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-improvement-log: SELFTEST OK — {len(_CASES) + 1} fixtures, all four "
          f"states of a NEW finding distinguished, and every pre-existing check still fires.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG,
                        help=f"path to the finding log (default: {DEFAULT_LOG})")
    parser.add_argument("--check", action="store_true",
                        help="also enforce WORKFLOW.md's processing triggers (CI mode)")
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="root that 'evidence_grep.file' and 'reviewed_in' paths resolve "
                             "against (default: cwd)")
    parser.add_argument("--reviews-dir", type=Path, default=None,
                        help=f"directory of review documents for the citation-versus-stamp "
                             f"check (default: <repo-root>/{REVIEWS_DIR})")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove all four states of a "
                             "NEW finding are distinguished")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    root = (args.repo_root or Path.cwd())
    result = run(args.log, root, args.check, args.reviews_dir)

    for note in result.notes:
        print(note, file=sys.stderr)
    for warning in result.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    if result.rc != 0:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        for error in result.triggers:
            print(f"TRIGGER: {error}", file=sys.stderr)
        total = len(result.errors) + len(result.triggers)
        print(f"\nverify-improvement-log: FAILED — {total} problem(s) across "
              f"{len(result.rows)} entry(ies) in {args.log}.", file=sys.stderr)
        return 1

    rows = result.rows
    counts = {
        "NEW": sum(1 for r in rows if r.get("status") == "NEW"),
        "APPLIED": sum(1 for r in rows if r.get("status") == "APPLIED"),
        "REJECTED": sum(1 for r in rows if r.get("status") == "REJECTED"),
    }
    mode = "schema + triggers" if args.check else "schema"
    warned = f", {len(result.warnings)} warning(s)" if result.warnings else ""
    print(f"verify-improvement-log: OK ({mode}) — {len(rows)} entries "
          f"({counts['NEW']} NEW, {counts['APPLIED']} APPLIED, "
          f"{counts['REJECTED']} REJECTED) in {args.log}{warned}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
