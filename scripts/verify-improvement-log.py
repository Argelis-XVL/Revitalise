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

THE FIVE STATES OF A `NEW` FINDING (added 2026-08-21 — IMP-0154, IMP-0169; review 5 item 7
and review 6 item 6, cluster G; fifth state added 2026-08-22 — IMP-0181, review 8 item 1).
A finding's real state is one of five things, and on 2026-08-21 the gate could represent two, because the blocker trigger had exactly one discharge
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
  * `approved-not-applied` — added 2026-08-22 (IMP-0181, review 8 item 1). `approved_in` names
                           the review and item that APPROVED this, and the entry's own needle is
                           ABSENT from the tree. A human said yes and the work was never done.
                           FAIL, naming the artefact that does not exist. Four entries sat in
                           this condition for up to eleven days while this gate called them
                           "deferred with a recorded reason, accepted as a reviewed deferral" —
                           approved work reported as a decision somebody made. Review 6 asked
                           for this state in writing and got only the `already-fixed` half,
                           because nothing had been approved yet; review 7 then approved things.

  Precedence, deliberately, is: already-fixed > approved-not-applied > reviewer-deferred >
  awaiting-approval > unread. `approved-not-applied` sits second because it is a STRONGER
  statement than either waiting state: those two mean "a person still has to decide", and this
  one means "a person decided and the artefact is missing". Reporting the stronger fact as the
  weaker one is the entire defect (IMP-0181). It ranks below `already-fixed` for the same
  reason that one ranks first: the tree wins over any field.
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
    * a census of all five states, printed every run

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
    python3 scripts/verify-improvement-log.py --selftest       # prove the five states differ

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

# Position decides whether a cited id is a processing claim or a declared deferral (IMP-0196).
HEADING_LINE = re.compile(r"^\s{0,3}(#{1,6})\s")
DEFERRAL_HEADING = re.compile(
    r"^\s{0,3}#{1,6}\s.*\b(unprocessed|not\s+processed|deferred|deferrals)\b", re.IGNORECASE)

# The five states a NEW finding can be in. Named once; the message text keys off these.
UNREAD = "unread"
AWAITING = "awaiting-approval"
DEFERRED = "reviewer-deferred"
SHIPPED = "already-fixed"

# THE FIFTH STATE, added 2026-08-22 (IMP-0181, improvement review 8 item 1).
#
# An entry can be APPROVED and simply not done, and until now the log could not say so. Four
# entries — IMP-0148, IMP-0161, IMP-0162, IMP-0166 — sat in that condition for up to eleven
# days, and this gate reported every one of them as "deferred with a recorded reason, accepted
# as a reviewed deferral". Approved work that nobody did was being reported as a decision
# somebody made, which is worse than silence: a missing gate leaves you uncertain, this one
# returned a confident wrong answer.
#
# Review 6 predicted it in writing — it asked for the state to be modelled properly and got
# only the `already-fixed` half, because at that moment nothing had been approved. Review 7
# then approved things. One review later the predicted failure arrived, which is why this is a
# state and not another paragraph.
#
# The signal is two fields disagreeing: `approved_in` says a human approved it, and the entry's
# own `evidence_grep` needle is absent from the tree. Same field, third reading (IMP-0140
# APPLIED: needle must be present; IMP-0169 NEW: needle must be absent; here: needle absent
# PLUS an approval means outstanding, not pending).
APPROVED_NOT_APPLIED = "approved-not-applied"

# From this review onward, an entry moved to APPLIED must carry the needle that proves it.
# Bound to a cutoff rather than applied retroactively: only 26 of 164 applied entries carry one,
# so requiring it of all of them would emit 138 errors about work that is genuinely done, and a
# gate that cries wolf 138 times is a gate people learn to skip (review 6's cluster A made the
# same call for the same reason). Legacy entries are reported once, as a NOTE.
NEEDLE_REQUIRED_FROM = ("2026-08-21", 8)


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


# ── the five states ───────────────────────────────────────────────────────────────────────

def _review_order(name: str) -> tuple[str, int]:
    """Sort key for a review document filename: (date, review number within that date).

    '2026-08-21-improvement-review-8.md' -> ('2026-08-21', 8)
    '2026-08-22-improvement-review.md'   -> ('2026-08-22', 1)

    Needed because plain lexicographic comparison puts '-2.md' before '.md' (0x2d < 0x2e), so
    review 10 would sort before review 9. Reviews are named by date plus an optional ordinal,
    and this is that ordering made explicit rather than assumed.
    """
    stem = Path(name).name
    date = stem[:10]
    match = re.search(r"-review-(\d+)\.md$", stem)
    return date, int(match.group(1)) if match else 1


def approved_but_absent(row: dict, repo_root: Path) -> tuple[bool, str]:
    """True when a human approved this entry and the artefact it promises is not on disk.

    The whole point of the fifth state: `approved_in` is a claim that somebody said yes, and
    the needle is what proves the yes turned into a file. When the two disagree, the entry is
    outstanding work — never a deferral, and never 'pending a keyword'.
    """
    approved = str(row.get("approved_in") or "").strip()
    if not approved:
        return False, ""
    spec = row.get("evidence_grep")
    if not isinstance(spec, dict):
        return False, ""
    target = str(spec.get("file") or "").strip()
    needle = str(spec.get("contains") or "").strip()
    if not target or not needle:
        return False, ""

    path = repo_root / target
    if not path.is_file():
        return True, f"{target} does not exist (needle {needle!r} unreachable)"
    try:
        if needle in path.read_text(encoding="utf-8", errors="replace"):
            return False, ""
    except OSError:
        return False, ""
    return True, f"{target} exists but does not contain {needle!r}"


def classify(row: dict, repo_root: Path) -> tuple[str, str]:
    """Return (state, detail) for one NEW entry. Precedence is argued in the module docstring."""
    if evidence_says_shipped(row, repo_root):
        spec = row["evidence_grep"]
        return SHIPPED, f"{spec.get('file')} already contains {spec.get('contains')!r}"
    # Ahead of DEFERRED and AWAITING on purpose. Both of those say "waiting on a person to
    # decide"; this one says "a person already decided and the work is not done", and reporting
    # the stronger fact as the weaker one is precisely IMP-0181.
    outstanding, why = approved_but_absent(row, repo_root)
    if outstanding:
        return APPROVED_NOT_APPLIED, why
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

    # ── The census. Every NEW entry lands in exactly one of five buckets, printed every run,
    # because the whole defect this replaces was a state the gate could not say out loud.
    notes.append(
        f"verify-improvement-log: NOTE — {len(new_rows)} NEW entry(ies): "
        f"{len(ids_in(UNREAD))} {UNREAD}, {len(ids_in(AWAITING))} {AWAITING}, "
        f"{len(ids_in(DEFERRED))} {DEFERRED}, {len(ids_in(SHIPPED))} {SHIPPED}, "
        f"{len(ids_in(APPROVED_NOT_APPLIED))} {APPROVED_NOT_APPLIED}."
    )

    # ── STATE 5 of 5: approved, and the artefact is not there. A FAIL, and named. ───────────
    # This is the state whose absence let four approved items read as accepted deferrals for up
    # to eleven days (IMP-0181). It fails rather than warns because there is nothing left to
    # decide: a human already said yes, so the only remaining question is who does the work.
    outstanding = ids_in(APPROVED_NOT_APPLIED)
    if outstanding:
        lines = [f"{len(outstanding)} NEW entry(ies) APPROVED and NOT APPLIED — a human said "
                 f"yes and the artefact is still absent. This is not a deferral and not a "
                 f"pending keyword (IMP-0181):"]
        for row in outstanding:
            _state, why = states[str(row.get("id"))]
            lines.append(f"      {row.get('id')} -> {why}")
            lines.append(f"          approved in: "
                         f"{str(row.get('approved_in') or '')[:150]}")
        lines.append("    Resolve by DOING the work, or by withdrawing the approval in a new "
                     "review that says why. Re-deferring it is what produced this state.")
        errors.append("\n".join(lines))

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

    # ── STATE 4 of 5: already fixed in the tree. The failing message lives in
    # check_evidence_grep(), which is where the evidence is read; this only names the state.
    shipped = ids_in(SHIPPED)
    if shipped:
        notes.append(f"verify-improvement-log: NOTE — {len(shipped)} finding(s) in state "
                     f"'{SHIPPED}': {', '.join(str(r.get('id')) for r in shipped)}. Each is "
                     f"reported as an ERROR below, with the file and line that proves it.")

    # ── An APPLIED status without a needle is the next generation of this same defect ────────
    # IMP-0181, second half. What made the four outstanding items invisible was not only the
    # missing state — it was that only 26 of 164 applied entries carry an evidence_grep at all,
    # so for most of the log there is nothing to check in either direction. Requiring it
    # retroactively would emit 138 errors about finished work, so it binds from review 8 forward
    # and the legacy tail is reported once, as a number, deliberately not as an error.
    missing_needle: list[str] = []
    legacy_without_needle = 0
    for row in rows:
        if row.get("status") != "APPLIED":
            continue
        ptype = str((row.get("proposed_change") or {}).get("type") or "").strip().lower()
        if ptype == "none":
            continue                      # nothing was promised, so there is nothing to prove
        if isinstance(row.get("evidence_grep"), dict):
            continue
        reviewed_in = str(row.get("reviewed_in") or "").strip()
        if reviewed_in and _review_order(reviewed_in) >= NEEDLE_REQUIRED_FROM:
            missing_needle.append(
                f"{row.get('id')} (applied by {Path(reviewed_in).name}, "
                f"proposed_change.type={ptype!r})")
        else:
            legacy_without_needle += 1

    if missing_needle:
        errors.append(
            f"{len(missing_needle)} entry(ies) moved to APPLIED on or after improvement review "
            f"{NEEDLE_REQUIRED_FROM[1]} ({NEEDLE_REQUIRED_FROM[0]}) with no 'evidence_grep':\n"
            + "\n".join(f"      {m}" for m in missing_needle)
            + f"\n    An APPLIED status is a claim (C-COM-005 applied to this log), and without "
              f"a needle nothing can ever check it — which is how four approved items stayed "
              f"invisible for eleven days (IMP-0181, IMP-0140). Add "
              f"{{\"file\": ..., \"contains\": ...}} naming the artefact and a string that "
              f"proves the substance, not merely the file.")

    if legacy_without_needle:
        notes.append(
            f"verify-improvement-log: NOTE — {legacy_without_needle} APPLIED entry(ies) predate "
            f"the evidence_grep requirement (improvement review {NEEDLE_REQUIRED_FROM[1]}, "
            f"{NEEDLE_REQUIRED_FROM[0]}) and carry no needle. Not an error, and deliberately not "
            f"back-filled: the work is done and 138 errors about finished work is how a gate "
            f"teaches people to route around it (IMP-0181).")

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


def split_deferral_citations(text: str) -> tuple[set[str], set[str]]:
    """Finding ids this document names only to DECLARE THEM DEFERRED, and all the rest.

    THE INCIDENT (IMP-0196, third instance of `gate-fires-on-nothing`). Two rules in this
    system pulled against each other, and this check enforced one of them against the other.
    `skills/how-to-promote-a-finding.md` §3.4 — "no silent caps" — REQUIRES a review to name
    every finding it deferred and why. This check then read every named id as a processing
    claim and demanded a `reviewed_in` stamp for it. Improvement review 10 named its nine
    out-of-scope deferrals in the template's own "Findings left unprocessed" table and earned
    nine warnings for it, four of them on unread blockers that same document said needed their
    own dispatch. Stamping those would have been a false claim, so the honest review looked
    worse than one that quietly said nothing.

    A declared deferral is a legitimate, informative state: the review is on record as having
    seen the finding and consciously not taken it. That is the opposite of the harm this check
    exists to catch, which is a finding that *reads as unread*.

    So position decides meaning, exactly as it already does in processing_citations(): an id
    under a "Findings left unprocessed" (or "deferred") heading is a declaration, an id in a
    `Cites:` line or a proposed-change row is a processing claim. An id in BOTH positions is
    treated as processed — the stronger signal wins, the same precedence rule the four-state
    model at the top of this file uses.

    Returns (inside_a_deferral_section, everywhere_else). The second half is what decides
    whether a stamp is owed, because an id named ONLY inside a deferral section is the one
    case this function exists to excuse. Splitting rather than returning a single set matters:
    an id can appear in both halves, and plain set subtraction would then let the deferral row
    suppress the processing claim — the selftest case `deferred-AND-cited-as-processed-still-
    warns` is that mistake, caught while writing this.
    """
    inside: set[str] = set()
    outside: set[str] = set()
    in_section = False
    section_level = 0
    for line in text.splitlines():
        heading = HEADING_LINE.match(line)
        if heading:
            level = len(heading.group(1))
            if DEFERRAL_HEADING.match(line):
                in_section, section_level = True, level
                continue
            if in_section and level <= section_level:
                in_section = False
        (inside if in_section else outside).update(ID_IN_PROSE.findall(line))
    return inside, outside


APPLIED_HEADING = re.compile(r"^\s{0,3}#{1,6}\s.*\bapplied\b", re.IGNORECASE | re.MULTILINE)
AWAITING_STATUS = re.compile(
    r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s].*\bAWAITING\b", re.IGNORECASE | re.MULTILINE)
STRUCK_STATUS = re.compile(r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s]*~~", re.IGNORECASE |
                           re.MULTILINE)


def check_review_status_headers(reviews_dir: Path) -> list[str]:
    """A review document must not claim AWAITING while carrying an 'Applied' section.

    IMP-0204, improvement review 11 item 4. Applying a review appends a section recording what
    was applied; nothing rewrites the status header written at drafting time, so the two halves
    of one document end up dating from different moments — and the header is always the stale
    one.

    Review 10 carried both at once: 'Status: AWAITING APPROVE IMPROVEMENTS. Nothing in section 3
    has been applied' above a section 9 recording the approval and four items that were, in
    fact, on disk. Four log entries pointed at that document as their applied_by. Establishing
    which half was true cost a full working-tree verification pass before the next review could
    even start, and IMP-0181 had already recorded the one-level-down version of this: a review's
    proposals must be verified against the tree, never against its prose.

    A struck-through status (`~~AWAITING …~~`) is the CORRECT way to record the history, so it
    is explicitly allowed — otherwise this check would forbid its own remedy.
    """
    problems: list[str] = []
    if not reviews_dir.is_dir():
        return problems

    for path in sorted(reviews_dir.glob("*-improvement-review*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        applied = APPLIED_HEADING.search(text)
        if not applied:
            continue
        status = AWAITING_STATUS.search(text)
        if not status or STRUCK_STATUS.search(text):
            continue
        line_no = text[:status.start()].count("\n") + 1
        applied_line = text[:applied.start()].count("\n") + 1
        problems.append(
            f"{path.name}:{line_no}: the status header still says AWAITING, but this document "
            f"carries an 'Applied' section at line {applied_line}. One document, two moments — "
            f"and the header is the stale half. Correct it (strike it through and date the "
            f"correction, which is what review 6's header now does) so the next reader is not "
            f"told that applied work is outstanding (IMP-0204, IMP-0181).")
    return problems


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
    # Ids named somewhere OTHER than a deferral table. Only these can read as "unread" to the
    # next person, so only these are missing a stamp in the sense that matters (IMP-0196).
    cited_substantively: dict[str, list[Path]] = {}
    for doc in docs:
        try:
            text = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        known = set(new_rows)
        _deferred_only, elsewhere = split_deferral_citations(text)
        processed = processing_citations(text) & known
        for ident in set(ID_IN_PROSE.findall(text)) & known:
            cited_anywhere.setdefault(ident, []).append(doc)
        # Substantive = named outside any deferral section, or claimed in a processing
        # position. The union is what stops a deferral row suppressing a real claim.
        for ident in (elsewhere & known) | processed:
            cited_substantively.setdefault(ident, []).append(doc)
        for ident in processed:
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
            # Named ONLY to declare it deferred, under the no-silent-caps rule. That is a
            # review being explicit about what it did not take, not an unstamped processing
            # claim — and demanding a stamp here punishes the honest review (IMP-0196).
            if ident not in cited_substantively:
                continue
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
        rdir = reviews_dir or (repo_root / REVIEWS_DIR)
        warnings = check_citation_stamps(rows, rdir)
        # A review contradicting itself is a WARNING, not a FAIL: it never blocks delivery, and
        # the remedy is an edit to a document rather than any change to the log.
        warnings += check_review_status_headers(rdir)

    rc = 1 if (errors or triggers) else 0
    return Result(rc, errors, triggers, warnings, notes, rows)


# Every fixture below is (log rows, files to write into the fixture tree, expected rc,
# a string the output must contain). The five states are the first cases, in order, so a
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

# IMP-0196: a review naming its deferrals, as the no-silent-caps rule requires, and nothing else.
_DEFERRAL_ONLY_BODY = (
    "# fixture review\n\n## 3. Proposed changes\n\n"
    "| # | Change | Cites |\n|---|---|---|\n| 1 | something else | IMP-9002 |\n\n"
    "## 5. Findings left unprocessed\n\n"
    "| Finding | Why deferred |\n|---|---|\n| IMP-9001 | out of scope for this dispatch |\n\n"
    "## 6. Digest impact\n\nNothing further.\n")

# The over-suppression control: the SAME id declared deferred in section 5 *and* claimed in a
# Cites position. The stronger signal must win, so this must still warn.
_DEFERRED_AND_CITED_BODY = (
    "# fixture review\n\n## 3. Proposed changes\n\n"
    "| # | Change | Cites |\n|---|---|---|\n| 1 | a change | IMP-9001 |\n\n"
    "## 5. Findings left unprocessed\n\n"
    "| Finding | Why deferred |\n|---|---|\n| IMP-9001 | also mentioned here |\n")

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
    # ── STATE 5: approved, and the artefact is missing (IMP-0181) ──
    # The needle's file does not exist at all — the IMP-0148 shape, where an approved script
    # was never written.
    "STATE-5-approved-not-applied-file-absent": (
        [_entry(approved_in="review 5 items 1-3 — the canary probe",
                evidence_grep={"file": "provisioning/x.ps1", "contains": "canary"})],
        {}, True, 1, "APPROVED and NOT APPLIED"),
    # The file exists and the substance does not — the IMP-0162/IMP-0166 shape. This is the
    # case an existence check passes and only a needle catches.
    "STATE-5-approved-not-applied-substance-absent": (
        [_entry(approved_in="review 6 item 7 — escalation conditions",
                evidence_grep={"file": "config/models.yml", "contains": "sole enforcement"})],
        {"config/models.yml": "tier: standard\n"}, True, 1, "APPROVED and NOT APPLIED"),
    # THE OVER-FIRE CONTROL. An approval whose needle IS present must fall through to
    # already-fixed and must never report as outstanding — otherwise every finished item
    # reports forever and the state is worthless.
    "STATE-5-must-not-fire-when-the-needle-is-present": (
        [_entry(approved_in="review 6 item 9 — the toolchain rewrite",
                evidence_grep={"file": "knowledge/x.md", "contains": "getClient("})],
        {"knowledge/x.md": "use getClient(dataSourcesInfo) from the SDK\n"}, True, 1,
        "appears to have shipped"),
    # An approval with NO needle cannot be checked in either direction, and must not be
    # guessed at — it stays in whatever state its other fields put it in.
    "STATE-5-approval-without-a-needle-is-not-outstanding": (
        [_entry(severity="friction", approved_in="review 6 item 12",
                deferred_reason="owner: reviewer", revisit_when="next review")],
        {}, True, 0, "accepted as a reviewed deferral"),
    # ── the APPLIED-needs-a-needle rule, both sides of its cutoff ──
    "APPLIED-after-the-cutoff-without-a-needle-fails": (
        [_entry(status="APPLIED", applied_by="fixture", reviewed_in=_LATER_REVIEW,
                proposed_change={"type": "script", "target": "scripts/x.py", "summary": "s"})],
        {_LATER_REVIEW: _REVIEW_BODY}, True, 1, "with no 'evidence_grep'"),
    "APPLIED-type-none-needs-no-needle": (
        [_entry(status="APPLIED", applied_by="fixture", reviewed_in=_LATER_REVIEW,
                proposed_change={"type": "none", "target": "n/a", "summary": "log note only"})],
        {_LATER_REVIEW: _REVIEW_BODY}, True, 0, "NEW entry(ies)"),
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
    # ── a declared deferral is not an unstamped processing claim (IMP-0196) ──
    "deferral-table-citation-must-not-warn": (
        [_entry(severity="friction", deferred_reason="owner: reviewer",
                revisit_when="next review")],
        {_REVIEW: _DEFERRAL_ONLY_BODY}, True, 0, "accepted as a reviewed deferral"),
    "deferred-AND-cited-as-processed-still-warns": (
        [_entry(severity="friction", deferred_reason="owner: reviewer",
                revisit_when="next review")],
        {_REVIEW: _DEFERRED_AND_CITED_BODY}, True, 0, "carries NO 'reviewed_in'"),
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
    print(f"\nverify-improvement-log: SELFTEST OK — {len(_CASES) + 1} fixtures, all five "
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
                        help="assemble fixtures at runtime and prove all five states of a "
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
