#!/usr/bin/env python3
"""Verify an improvement review document is internally consistent before a human approves it.

WHY THIS EXISTS. Nothing in this repository reads a review document at all.
`scripts/verify-improvement-log.py` checks the LOG against review documents — that they exist, that
they cite ids, that a cited entry carries `reviewed_in` — and never a document's consistency with
itself. Two instances of class `approved-document-internally-inconsistent`:

  * `IMP-0302`. Review 27 §1 said, of a rung it declined to patch a third time: "This is instance
    33 of gate-cannot-fail and I am NOT proposing a third patch to that rung; section 5 puts it to
    you." Section 5 contained four bold questions and none of them was that one. The reviewer
    approved the document, so the altitude call was silently dropped. **A deferral has two halves
    and only one of them is load-bearing on its own:** naming a cap in the body is worthless if the
    decisions section does not carry it.
  * `IMP-0204`. Review 10 carried a status header saying "AWAITING — nothing has been applied"
    above a section recording the approval and four items that were, in fact, on disk. Establishing
    which half was true cost a full working-tree verification pass.

Second instance, so the altitude rule in `skills/how-to-promote-a-finding.md` §2 requires
generalising rather than patching. It is mechanically tractable because the section structure is
fixed by `templates/improvement-review-template.md`.

**THIS GATE SUBSUMES `check_review_status_headers()`** in `verify-improvement-log.py`, which
enforced `IMP-0204`'s half alone. Two gates asserting one rule is the duplication the anti-bloat
limits exist to prevent, so that function is retired into check (c) here rather than left running
alongside. Its fixture is preserved below and must still fail.

WHAT IT CHECKS

  (a) `CROSS-REF`   — every "section N" / "§N" reference resolves to a heading that exists in the
                      same document. An unresolved self-reference is invisible precisely because
                      it is internal: an external link would have been verified.
  (b) `LOST-DEFERRAL` — every sentence that defers a decision to a named section is matched by a
                      question in that section. This is `IMP-0302` exactly.
  (c) `STALE-HEADER` — a document carrying an "Applied" section must not still claim AWAITING.
                      A struck-through status is the correct way to record the history and is
                      explicitly allowed, or this check would forbid its own remedy.
  (d) `CLUSTER-COUNT` — every "→ N clusters" claim on a `Findings processed:` line matches the
                      count of DISTINCT `CLUSTER` blocks, excluding any that declares `(x0` new
                      members. This is `IMP-0332`: review 29 was amended in place to add clusters
                      H and I, and its §9 gate block still said "13 unread -> 7 clusters" over 9
                      CLUSTER blocks. An amendment updates the figures in view and leaves the
                      restatements. Measured: 3 findings, 3 true, 0 false across 35 documents.

WHY (d) IS THE ONLY COUNTING CHECK HERE, out of the four `IMP-0332` proposed. The other three were
built and measured against the whole corpus before being dropped (improvement review 30 §3):

  * per-type `Proposed:` sums vs the change table — 18 findings, **0 true**. A review's `Proposed:`
    line counts retirements, which are not rows of the change table, so the premise is wrong.
  * every "change N" prose reference resolves to a row — 6 findings, **0 true** (all were
    references to *another* review's numbering), and blind to `IMP-0332`'s own instance.
  * the Summary's decision count vs the bold questions in §5 — 1 true, 1 false, and the false one
    was the sentence *describing* the true one. Unfixable: a decision count lives only in prose,
    and reviews on this project narrate each other's figures constantly.

(d) survived because a cluster count has two STRUCTURAL homes — a `Findings processed:` header
field and the same field inside the fenced gate block — so scoping to that line excludes prose
entirely. That is the whole difference, and it is why this check is anchored to the line prefix
rather than to the word "clusters".

EXIT CODES: 0 clean (or `--warn-only`); 1 findings, or zero documents parsed (the `IMP-0007` shape
— a gate reporting OK over nothing); 2 usage error.

RESIDUAL, stated because every promotion leaves one. **(b) is a heuristic over prose.** It keys on
a deferral phrase from a fixed list plus a section number; a deferral phrased without naming a
section, or naming it in a way this list does not match, slips past. A "question" is recognised as
a bold span containing `?` — so a decision put to the reviewer as a flat statement rather than a
question is not counted. Both directions are stated rather than papered over: this gate raises the
floor, it does not close the class.

**(d) has two residuals of its own.** A document that quotes ANOTHER review's cluster block
verbatim would inflate this count, because dedupe is by label and a foreign label is still
distinct — no instance exists in 35 documents, and the fix if one appears is to scope the count to
the clusters section rather than the file. And the two figures this class keeps getting wrong most
— a review's decision count and its "change N" references — are covered by NOTHING here: both
live in free prose, both were measured, and both were dropped above. Improvement review 30 §7
asks whether to give the decision count a structural home so this same check can reach it.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HEADING_RE = re.compile(r"^#{2,3}\s+(?P<num>\d+)\s*\.\s*(?P<title>.+?)\s*$", re.MULTILINE)

# "section 5", "section 5.2", "§5", "§5.6", "sections 5 and 6"
SECTION_REF_RE = re.compile(r"(?:§|\bsection\s+)(?P<num>\d+)(?:\.\d+)?\b", re.IGNORECASE)

# A bold span carrying a question mark: `**Should the log gain a sixth state?**`
BOLD_QUESTION_RE = re.compile(r"\*\*[^*]*\?[^*]*\*\*")

# Phrases by which a body sentence HANDS A DECISION FORWARD to a section. A closed, high-precision
# list, and every loosening of it was measured and reverted:
#
#   * bare "asks" matched the "tasks" in "all 61 contracted tasks surveyed" — hence \b boundaries.
#   * bare "declined" fired on "section 7 declined to predict a delta", which is a review looking
#     BACK at what a section did, not a deferral forward to it. A retrospective is not a promise.
#
# The property being detected is narrow on purpose: the body says a decision is being handed to a
# named section. Anything vaguer belongs to the residual in this module's docstring, not to a gate.
DEFERRAL_PHRASES = (
    r"puts? (?:it|this|that) to you",
    r"put to you",
    # "carries" was here and was removed: "Section 8 carries the numbers" is a review pointing at
    # where its own results ended up, not a decision being handed over. Same lesson as "declined".
    r"\bsection \d+ (?:asks|puts|assigns|will ask)",
    r"assigns? (?:it|this)",
    r"is a section \d+ (?:decision|question|call)",
    r"leaves? (?:it|this) to you",
    r"for you to decide",
    r"\bI am not (?:proposing|answering|deciding)",
    r"not proposed here",
    r"\bdeferred? to section \d+",
    r"\bsection \d+ (?:below )?(?:puts|asks) it",
)
DEFERRAL_RE = re.compile("|".join(DEFERRAL_PHRASES), re.IGNORECASE)

# ANCHOR TERMS — the distinctive nouns a deferral is ABOUT, and the reason check (b) works at all.
#
# A first version asked only "does the target section contain any bold question?" and it did NOT
# fire on review 27, the document IMP-0302 was logged against — because §5 held four bold questions,
# none of them the one §1 promised. "Section 5 asks something" is not the property; "section 5 asks
# about THIS" is.
#
# So a deferring sentence's anchors are extracted — backticked code spans, IMP- ids, C-nnn ids,
# script filenames, snake_case identifiers — and at least one must appear in the target section.
# This reproduces IMP-0302's own detection method exactly: its author found the defect by grepping
# section 5 for `corrects` and getting zero hits.
ANCHOR_RES = (
    re.compile(r"`([^`]{3,60})`"),
    re.compile(r"\b(IMP-\d{4})\b"),
    re.compile(r"\b(C-(?:TECH|DOM|COM)-\d{3})\b"),
    re.compile(r"\b([a-z][a-z0-9]*(?:[-_][a-z0-9]+){1,6}\.(?:py|md|ps1|yml|json))\b"),
    re.compile(r"\b([a-z][a-z0-9]*_[a-z0-9_]{3,})\b"),
)

# Ported VERBATIM from verify-improvement-log.py's check_review_status_headers(), the function this
# gate subsumes. Anchoring AWAITING to a line that OPENS with `Status:` is the whole precision of
# the check: a first version here matched the bare word anywhere and reported review 11's Applied
# table, whose row 4 describes this very rule ("A review carrying an *Applied* section may no
# longer claim AWAITING"). A gate that fires on the sentence documenting it is worse than no gate.
# ── CLUSTER-COUNT (check d) — three regexes, and the scoping is the precision. ──────────────
#
# A cluster block opens a line: "CLUSTER A: approved-document-internally-inconsistent (x7...)".
# IMP-0332's own lesson names `grep -c '^CLUSTER '` as the mechanical count. That raw count was
# built first and MEASURED, and it scored 3 true positives against 2 false across 35 documents —
# so it is not what ships. Two narrowings remove both false positives, and each can name the
# finding it removes (improvement review 30, applying its own change 7):
#
#   * DISTINCT, not raw. 2026-08-19-improvement-review-3.md states 5 clusters and carries 6
#     `CLUSTER` lines, because its Addendum RE-QUOTES the build-context block verbatim after the
#     reviewer answered the open decision. Five distinct clusters, one block printed twice. The
#     approved change-table row says "the count of distinct CLUSTER blocks"; the raw count was my
#     deviation from it, not a tightening of it.
#   * `(x0` EXCLUDED. 2026-08-21-improvement-review-2.md states 6 clusters and carries 7, the
#     seventh being "test-coupled-to-absolute-counts (x0 NEW this session; IMP-0005/IMP-0039
#     carried forward" — a class reconciled with no finding from the batch in it. "15 NEW → 6
#     clusters" is a claim about the clusters the batch produced, and a block declaring x0 new
#     members is not one of them.
#
# Both true positives survive both narrowings: 2026-08-21-improvement-review.md claims 17 clusters
# over 7 blocks (the reconciliation-only finding count leaked into the cluster field), and
# 2026-08-22-improvement-review.md claims 4 over 3 in BOTH its structural homes.
CLUSTER_BLOCK_RE = re.compile(r"^CLUSTER\b[ \t]*(?P<label>.*)$", re.MULTILINE)
CARRIED_FORWARD_RE = re.compile(r"\(\s*x0\b", re.IGNORECASE)


def _distinct_clusters(text: str) -> int:
    """Distinct cluster blocks a review document processes.

    Deduplicated on the block's own label, and blocks declaring `(x0` new members excluded. Both
    narrowings are measured — see CLUSTER_BLOCK_RE above.
    """
    labels: set[str] = set()
    for m in CLUSTER_BLOCK_RE.finditer(text):
        label = m.group("label").strip()
        if CARRIED_FORWARD_RE.search(label):
            continue
        labels.add(re.sub(r"\s+", " ", label).lower())
    return len(labels)

# The claim is only read off a line that OPENS with `Findings processed:` — the header field
# (`**Findings processed:** 13 NEW (unread) → 9 clusters`) and the identically-named line inside
# the fenced gate block. Both are fixed by templates/improvement-review-template.md. Any other
# sentence mentioning clusters is prose and is deliberately not read: that is what separated this
# check from the three that were dropped.
FINDINGS_LINE_RE = re.compile(r"^\s*>?\s*\*{0,2}Findings\s+processed\*{0,2}\s*:", re.IGNORECASE)
CLUSTER_CLAIM_RE = re.compile(
    r"(?:→|-->|->)\s*\*{0,2}(?P<n>\d+)\*{0,2}\s*(?:distinct\s+)?clusters?\b", re.IGNORECASE)

APPLIED_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s.*\bapplied\b", re.IGNORECASE | re.MULTILINE)

# ── STALE-HEADER's vocabulary: a FAIL-CLOSED allowlist (improvement review 7, IMP-0558) ──────
#
# This used to be `AWAITING_RE`, matching the literal word AWAITING and nothing else. A header
# reading "**Status: DRAFT, parked at its gate.**" above a fully populated Applied section
# therefore passed clean — the precise contradiction this check was built to catch (IMP-0204) —
# and the OK line went on advertising "no status header contradicts an Applied section".
#
# The corpus made the gap invisible: 24 review documents used an AWAITING-shaped header and 0
# used DRAFT, so improvement review 6 was simply the first document to reach the gate in wording
# the gate could not see.
#
# WHY AN ALLOWLIST RATHER THAN A SIXTH SYNONYM. Adding DRAFT would have fixed this document and
# left PARKED, PENDING and NOT APPLIED equally invisible. A predicate that enumerates the shapes
# it knows is wrong by construction on the shapes nobody has met yet (IMP-0328, IMP-0557), so the
# unknown token is itself reported: an unrecognised status word FAILS rather than passing silently.
#
# MEASURED ACROSS ALL 65 REVIEW DOCUMENTS before wiring, per the corpus rule, and the measurement
# changed the design twice:
#   * REVISION is in live use (2026-08-24-improvement-review-6.md) and was absent from the token
#     set IMP-0558 proposed. A fail-closed allowlist without it reports a correct document on day
#     one — the defect a fail-open check would have absorbed harmlessly.
#   * 20 of 65 documents carry a struck-through `~~AWAITING` header, this project's convention for
#     "this status is superseded". STRUCK_RE must keep composing with the allowlist, not be
#     replaced by it, or the change fires on 20 correct documents.
# A fail-closed design converts every value its author did not think of into a false positive, so
# enumerating the corpus is not a refinement of this design — it IS the design (IMP-0560).

# Tokens that mean "this document is NOT yet applied". Each contradicts an Applied section.
PRE_APPROVAL_TOKENS = ("AWAITING", "DRAFT", "PARKED", "PENDING", "NOT APPLIED", "REVISION")
# Tokens that mean "this document IS applied, or is no longer live". None contradicts anything.
SETTLED_TOKENS = ("APPLIED", "SUPERSEDED", "WITHDRAWN", "REJECTED")

STATUS_LINE_RE = re.compile(r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s].*$", re.MULTILINE)
STRUCK_RE = re.compile(r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s]*~~",
                       re.IGNORECASE | re.MULTILINE)


def status_verdict(line: str) -> str:
    """Classify one `**Status:**` line as 'pre-approval', 'settled' or 'unknown'.

    Reads the FIRST recognised token, because a header routinely carries both halves of a
    transition — "~~AWAITING APPROVE IMPROVEMENTS~~ → **APPLIED 2026-09-01**" is the shape 20
    documents use, and its leading token is the struck-through one that STRUCK_RE already clears.
    """
    body = line.upper()
    hits = [(body.find(tok), tok, kind)
            for kind, toks in (("pre-approval", PRE_APPROVAL_TOKENS), ("settled", SETTLED_TOKENS))
            for tok in toks if body.find(tok) != -1]
    if not hits:
        return "unknown"
    return min(hits)[2]

# A "section N" belonging to ANOTHER document is not a self-reference. This project's reviews cite
# the TAD's section 9.3, the Dev Summary's §10 register, the SDD's section 9 and the template's
# sections constantly, and reporting those as dangling would bury the real finding. Measured: this
# guard is what separates 3 true positives from 8 raw matches on the current tree.
FOREIGN_DOC_RE = re.compile(
    r"\b(TAD|SDD|dev[- ]summary|summary|plan|template|review\s*\d*|WORKFLOW|CLAUDE|agreement|"
    r"register|report|architecture|handover|[\w.-]+\.md)\b(?:['’]s)?\W{0,12}$", re.IGNORECASE)

# "…§11 of the same document…" — the referent is named AFTER the reference.
FOREIGN_TRAILER_RE = re.compile(
    r"\s*of (?:the same|that|this) (?:document|summary|report|file|plan)", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    kind: str
    document: str
    line: int
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.document}:{self.line}: {self.detail}"


def _sections(text: str) -> dict[int, tuple[int, int, int]]:
    """section number -> (heading line, body start offset, body end offset)."""
    marks = [(int(m.group("num")), m.start(), m.end()) for m in HEADING_RE.finditer(text)]
    out: dict[int, tuple[int, int, int]] = {}
    for i, (num, start, end) in enumerate(marks):
        body_end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        line_no = text[:start].count("\n") + 1
        # A number may repeat (a "## 5." in a quoted block); first wins.
        out.setdefault(num, (line_no, end, body_end))
    return out


_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _sentences(text: str) -> list[tuple[int, str]]:
    """(line number, sentence) for every PROSE sentence — table rows and fenced blocks excluded.

    PARAGRAPH-SCOPED, not line-scoped. `IMP-0404`: this used to iterate PHYSICAL LINES —
    `for i, line in enumerate(lines, 1)` then `re.finditer` over that single line — and every
    review document in `docs/improvements/` is hard-wrapped at roughly 100 characters. So a
    sentence spanning a hard wrap was split, and `FOREIGN_DOC_RE`, which is anchored with `$`
    against text that never contained the preceding line, could not see the noun that exempts a
    foreign reference. `CROSS-REF` reported "the manual privilege revoke TAD\\n§12.1 names" as a
    dangling self-reference, because the referent noun `TAD` sat at the end of the previous line.
    A line break is whitespace, not a sentence boundary.

    The same line-scoping cut the other way for check (b): a deferral phrase and the section
    number it names had to share a physical line to be seen at all, so `LOST-DEFERRAL` silently
    missed a wrapped deferral. Joining paragraphs fixes both halves at once.

    FENCED BLOCKS ARE EXCLUDED, and that is the other half of the measurement. Joining a gate
    block's `key: value` lines into a paragraph manufactures sentences that exist in no document —
    and a filename splits at the `.` in `.md`. The naive paragraph join measured **4 findings, 0
    true, 4 false** for exactly those two reasons; excluding fences and reporting at most one
    lost deferral per document and target section removes all four BY NAME and changes nothing
    else. Corpus output is byte-identical to the pre-change baseline.

    Table rows stay excluded, for the reason they always were: an Applied table's change
    description cites other documents' sections constantly, with no noun in the cell to mark them
    foreign, and reporting those buries the finding that matters.
    """
    lines = text.splitlines()
    paragraphs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    in_fence = False
    for line_no, line in enumerate(lines, 1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            if current:
                paragraphs.append(current)
                current = []
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("|"):
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append((line_no, line.strip()))
    if current:
        paragraphs.append(current)

    out: list[tuple[int, str]] = []
    for paragraph in paragraphs:
        # Join, keeping a per-character map back to the source line so a sentence is reported at
        # the line where it STARTS rather than where its paragraph does.
        joined = ""
        line_of: list[int] = []
        for index, (line_no, line) in enumerate(paragraph):
            if index:
                joined += " "
                line_of.append(line_no)
            joined += line
            line_of.extend([line_no] * len(line))
        found = False
        for m in re.finditer(r"[^.!?]+[.!?]", joined):
            found = True
            start = min(m.start(), len(line_of) - 1) if line_of else 0
            out.append((line_of[start] if line_of else paragraph[0][0], m.group(0).strip()))
        if not found and joined.strip():
            out.append((paragraph[0][0], joined.strip()))
    return out


# ---------------------------------------------------------------------------------------------
# (e) PROPOSED-COUNT — IMP-0397, and the FOURTH attempt at this assertion in this repository
# ---------------------------------------------------------------------------------------------
#
# `IMP-0397`. Review 31's §9 gate block stated "2 gates/scripts, 1 skill/knowledge edits, 7
# agent-file edits" against a §3 change table carrying THREE skill/knowledge rows, and the
# reviewer's approval message quoted the wrong figure back — so the miscount reached the
# authorisation record before anyone noticed. The substance was itemised correctly and approved
# "as drafted"; only the summary arithmetic was wrong.
#
# WHY THIS IS SCOPED TO DOCUMENTS THAT DECLARE A CLOSED VOCABULARY, WHICH IS NOT HOW IT WAS
# PROPOSED. Review 30 built this check, measured it at 18 findings / 0 true, and diagnosed a
# SCOPING defect — its implementation swept the neighbouring `Digest:` line into the sum. Scoping
# it correctly this time still fails: measured over all 37 documents, the two obvious variants
# gave **17 findings / 24 documents** and **15 / 22**, with roughly ONE true positive between
# them. The reason is not parsing, and it is not the `Digest:` line:
#
#   * §3's `Type` column is an OPEN VOCABULARY of 65 distinct values across the corpus, 20 of
#     them mapping to no bucket at all; and
#   * the gate block's figures count FILES while the table counts ROWS ("2 gates/scripts" for
#     three rows that all edit two scripts).
#
# Both are DECLARATION problems, not parsing problems. So change 4a fixes the declaration — the
# template now declares a closed eight-value vocabulary and states that a per-type figure counts
# ROWS, never files — and this check applies only where that declaration is present. It can fire
# on no document written before it, and that is stated rather than dressed up as a clean run.

_VOCAB_DECL_RE = re.compile(r"`Type`\s+values?\b.{0,80}?closed vocabulary", re.IGNORECASE)

# The closed vocabulary, and the gate-block label each value is counted under.
_TYPE_BUCKETS = {
    "constraint": "constraints",
    "constraint-amendment": "constraint amendment",
    "script": "gates/scripts",
    "skill": "skill/knowledge edits",
    "knowledge": "skill/knowledge edits",
    "agent": "agent-file edits",
    "template": "template edits",
    "other": "other",
}

# `Proposed:` ... possibly wrapped over a second physical line. Terminated by the next `Key:`
# line of the gate block (`Altitude calls:`, `Digest:`) — which is review 30's defect, fixed by
# stopping at the next label rather than at the next blank line.
_PROPOSED_BLOCK_RE = re.compile(
    r"^Proposed:(?P<body>.*?)(?=^\s*[A-Z][A-Za-z ]{2,20}:|\Z)",
    re.MULTILINE | re.DOTALL)
_FIGURE_RE = re.compile(
    r"(?P<n>\d+)\s+(?P<label>constraint amendments?|constraints?|gates?/scripts?|"
    r"skill/knowledge edits?|agent-file edits?|template edits?|retirements?|other)",
    re.IGNORECASE)

# A §3 row id: `1`, `3a`, `7a`. Distinguishes a change row from a header or separator row.
_ROW_ID_RE = re.compile(r"^\d+[a-z]?$")


def _proposed_figures(text: str) -> dict[str, int] | None:
    match = _PROPOSED_BLOCK_RE.search(text)
    if match is None:
        return None
    out: dict[str, int] = {}
    for figure in _FIGURE_RE.finditer(match.group("body")):
        label = figure.group("label").lower().rstrip("s")
        label = {"constraint amendment": "constraint amendment",
                 "constraint": "constraints",
                 "gate/script": "gates/scripts",
                 "gates/script": "gates/scripts",
                 "skill/knowledge edit": "skill/knowledge edits",
                 "agent-file edit": "agent-file edits",
                 "template edit": "template edits",
                 "retirement": "retirements",
                 "other": "other"}.get(label, label)
        out[label] = out.get(label, 0) + int(figure.group("n"))
    return out or None


def _row_types(text: str) -> tuple[dict[str, int], list[str]]:
    """(count per gate-block bucket, Type values outside the closed vocabulary)."""
    counts: dict[str, int] = {}
    unknown: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip().strip("*` ") for c in stripped.strip("|").split("|")]
        if len(cells) < 3 or not _ROW_ID_RE.match(cells[0]):
            continue
        value = cells[1].lower()
        bucket = _TYPE_BUCKETS.get(value)
        if bucket is None:
            unknown.append(f"{cells[0]}={cells[1]}")
            continue
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts, unknown


def _check_proposed_counts(text: str, name: str,
                           sections: dict[int, tuple[int, int, int]]) -> list[Finding]:
    if not _VOCAB_DECL_RE.search(text):
        return []  # scoped: the declaration is what makes the arithmetic decidable at all
    claimed = _proposed_figures(text)
    if claimed is None:
        return []

    # COUNT §3'S TABLE ONLY, not every table in the document. Scoping this to the whole file
    # reported EVERY figure as exactly DOUBLE on the first document that declared the vocabulary —
    # because §10's applied record carries its own `Type` column with the same eight values, so
    # every row was counted twice. This is review 30's scoping defect wearing new clothes, and the
    # gate caught it in its own author's document on the first real run, which is the argument for
    # measuring against the corpus rather than the fixtures.
    if 3 not in sections:
        return []
    _line, body_start, body_end = sections[3]
    counts, unknown = _row_types(text[body_start:body_end])
    if not counts:
        return []

    line_no = next((i for i, l in enumerate(text.splitlines(), 1)
                    if l.startswith("Proposed:")), 1)
    findings: list[Finding] = []
    if unknown:
        findings.append(Finding(
            "PROPOSED-COUNT", name, line_no,
            f"§3 declares a closed `Type` vocabulary and then uses {len(unknown)} value(s) "
            f"outside it: {', '.join(unknown[:6])}. The closed vocabulary is what makes the "
            f"per-type arithmetic decidable — an open one measured 65 distinct values across the "
            f"corpus and roughly one true positive in seventeen findings (IMP-0397)."))
    for bucket, count in sorted(counts.items()):
        if bucket == "other":
            continue
        stated = claimed.get(bucket)
        if stated is None:
            findings.append(Finding(
                "PROPOSED-COUNT", name, line_no,
                f"§3 carries {count} row(s) of type mapping to '{bucket}' and the gate block's "
                f"`Proposed:` line states no figure for it. Derive the per-type figures by "
                f"counting the change table's ROWS by their Type column, never by recalling the "
                f"clustering (IMP-0397)."))
        elif stated != count:
            findings.append(Finding(
                "PROPOSED-COUNT", name, line_no,
                f"the gate block claims {stated} '{bucket}' and §3's change table carries "
                f"{count} row(s) of that type. A per-type figure counts ROWS, never files — and "
                f"review 31's approval message quoted its own wrong figure back to it, so the "
                f"miscount reached the authorisation record (IMP-0397)."))
    return findings


def check_document(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    name = path.name
    findings: list[Finding] = []
    sections = _sections(text)

    # ---- (c) STALE-HEADER — IMP-0204's half, subsumed from verify-improvement-log.py ----
    applied = APPLIED_HEADING_RE.search(text)
    if applied:
        applied_line = text[: applied.start()].count("\n") + 1
        for m in STATUS_LINE_RE.finditer(text):
            line = m.group(0)
            # A struck-through status is a status the author has already withdrawn. That is the
            # convention this repository uses to date a correction, and it stays authoritative
            # over the token inside it (20 of 65 documents rely on it).
            if STRUCK_RE.search(line):
                continue
            verdict = status_verdict(line)
            if verdict == "settled":
                continue
            here = text[: m.start()].count("\n") + 1
            if verdict == "pre-approval":
                findings.append(Finding(
                    "STALE-HEADER", name, here,
                    f"the status header still claims this document is not applied, but it "
                    f"carries an 'Applied' section at line {applied_line}. One document, two "
                    f"moments — and the header is the stale half. Strike it through and date "
                    f"the correction (IMP-0204, IMP-0181)."))
            else:
                # FAIL CLOSED. An unrecognised token is reported rather than passed, because the
                # whole defect this check exists for is a status word the predicate cannot see.
                findings.append(Finding(
                    "STALE-HEADER", name, here,
                    f"the status header uses a word this check does not recognise, and the "
                    f"document carries an 'Applied' section at line {applied_line}. This check "
                    f"fails closed on purpose: an unknown status token is exactly how a DRAFT "
                    f"header sat above an Applied section undetected (IMP-0558). Either use one "
                    f"of {', '.join(PRE_APPROVAL_TOKENS + SETTLED_TOKENS)}, or add the new token "
                    f"to the allowlist in this script if it is genuinely a new status."))
            break

    # ---- (d) CLUSTER-COUNT — a claimed cluster count matches the blocks present ----
    # Runs BEFORE the `if not sections` guard below: counting CLUSTER blocks needs no section map,
    # and the earliest reviews this parser cannot section are exactly the ones an amendment is
    # most likely to have left behind.
    clusters = _distinct_clusters(text)
    if clusters:
        for line_no, line in enumerate(text.splitlines(), 1):
            if not FINDINGS_LINE_RE.match(line):
                continue
            claim = CLUSTER_CLAIM_RE.search(line)
            if not claim:
                continue
            claimed = int(claim.group("n"))
            if claimed == clusters:
                continue
            findings.append(Finding(
                "CLUSTER-COUNT", name, line_no,
                f"claims {claimed} cluster(s) and the document contains {clusters} distinct "
                f"CLUSTER block(s). A review restates its own counts in up to five places — header, "
                f"Summary, change-table tally, verification table, gate block — and an "
                f"amendment updates the ones in view. Re-derive it: "
                f"grep -c '^CLUSTER ' on this file (IMP-0332)."))

    # ---- (e) PROPOSED-COUNT — the gate block's per-type figures match §3's rows ----
    findings += _check_proposed_counts(text, name, sections)

    # ---- (a) CROSS-REF — every self-reference resolves ----
    # A document whose headings this parser cannot resolve at all gets no cross-ref check: with an
    # empty section map EVERY reference dangles, and reporting "sections present: []" against the
    # earliest reviews (written before templates/improvement-review-template.md fixed the
    # structure) is the gate reporting against nothing rather than about something.
    if not sections:
        return findings

    for line_no, sentence in _sentences(text):
        for m in SECTION_REF_RE.finditer(sentence):
            num = int(m.group("num"))
            if num in sections:
                continue
            # A reference to another document's section is not a self-reference — named either
            # BEFORE the reference ("the TAD's section 9.3") or AFTER it ("§11 of the same
            # document", which is how a review cites the Dev Summary it has been discussing).
            if FOREIGN_DOC_RE.search(sentence[: m.start()]):
                continue
            if FOREIGN_TRAILER_RE.match(sentence[m.end():]):
                continue
            findings.append(Finding(
                "CROSS-REF", name, line_no,
                f"names section {num}, which this document has no heading for. Sections present: "
                f"{sorted(sections)}. An unresolved self-reference is invisible because nothing "
                f"resolves it — an external link would have been checked (IMP-0302)."))

    # ---- (b) LOST-DEFERRAL — a deferral to a section must find a question there ----
    # AT MOST ONE PER TARGET SECTION. A review states the same deferral more than once — in the
    # Summary, in the cluster block, and in the decisions table's own row — and reporting each
    # restatement turns one defect into four lines that read as four defects. Paragraph-scoping
    # made that visible: joining wraps surfaced repeats the line-scoped version had split apart.
    reported_sections: set[int] = set()
    for line_no, sentence in _sentences(text):
        if not DEFERRAL_RE.search(sentence):
            continue
        for m in SECTION_REF_RE.finditer(sentence):
            num = int(m.group("num"))
            if num not in sections:
                continue  # already reported by (a)
            if num in reported_sections:
                continue
            _, body_start, body_end = sections[num]
            body = text[body_start:body_end]

            anchors: set[str] = set()
            for rex in ANCHOR_RES:
                anchors |= {a.strip().lower() for a in rex.findall(sentence)}
            # Section references and the deferral verbs themselves are not topics.
            anchors = {a for a in anchors
                       if not SECTION_REF_RE.fullmatch(a) and len(a) >= 3
                       and a not in ("section", "improvement-agent")}

            if anchors:
                if any(a in body.lower() for a in anchors):
                    continue
                findings.append(Finding(
                    "LOST-DEFERRAL", name, line_no,
                    f"defers a decision to section {num}, and section {num} mentions none of "
                    f"what the deferral is about ({', '.join(sorted(anchors)[:4])}). A deferral "
                    f"has two halves and naming the cap in the body is worthless if the "
                    f"decisions section does not carry it — review 27 said section 5 would ask "
                    f"and section 5 asked four other questions instead, so the reviewer approved "
                    f"the document without the altitude call it promised (IMP-0302)."))
                reported_sections.add(num)
                break

            if not BOLD_QUESTION_RE.search(body):
                findings.append(Finding(
                    "LOST-DEFERRAL", name, line_no,
                    f"defers a decision to section {num}, and section {num} contains no bold "
                    f"question at all (IMP-0302)."))
                reported_sections.add(num)
                break

    return findings


def run(reviews_dir: Path) -> tuple[int, list[Finding], int]:
    if not reviews_dir.is_dir():
        return 1, [Finding("NO-SOURCE", str(reviews_dir), 0,
                           "directory does not exist, so this gate cannot see what it "
                           "checks (IMP-0007).")], 0

    docs = sorted(reviews_dir.glob("*-improvement-review*.md"))
    if not docs:
        return 1, [Finding("NO-SOURCE", str(reviews_dir), 0,
                           "no review documents matched, so this gate would be reporting OK over "
                           "nothing (IMP-0007).")], 0

    findings: list[Finding] = []
    for d in docs:
        findings.extend(check_document(d))
    return (1 if findings else 0), findings, len(docs)


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------

# IMP-0302's shape: section 1 defers to section 5; section 5 has no question.
_LOST = """# Improvement Review — 2026-01-01

**Status:** DRAFT.

## 1. Regression check

This is instance 33 and I am NOT proposing a third patch to that rung; section 5 puts it to you.

## 5. What you need to decide

Nothing blocks this review. Three things are worth noting but need no answer.
"""

# The same document with the question actually present.
_FOUND = _LOST.replace(
    "Nothing blocks this review. Three things are worth noting but need no answer.",
    "**Should the corrects rung's sibling be built?** My recommendation is to build it.")

# A dangling self-reference.
_DANGLING = """# Improvement Review — 2026-01-02

## 1. Regression check

The measured figures are in section 9, which does not exist here.
"""

# IMP-0204's preserved fixture — the one check_review_status_headers() caught.
_STALE = """# Improvement Review — 2026-01-03

**Status:** AWAITING APPROVE IMPROVEMENTS — nothing in section 3 has been applied.

## 3. Proposed changes

One change.

## 8. Applied

APPROVE IMPROVEMENTS received. All of section 3 applied.
"""

# IMP-0332's shape: an amendment added a cluster and the gate block still carries the old count.
# Both structural homes appear — the header field and the fenced gate block — because both were
# wrong in the real instance, and the fenced one is the one nobody re-derived.
_MISCOUNT = """# Improvement Review — 2026-01-05

**Findings processed:** 13 unread → 7 clusters

## 2. Clusters

```
CLUSTER A: gate-cannot-fail  (x2)
```

```
CLUSTER B: learning-substrate-destroyed  (x1)
```

```
CLUSTER C: output-shape-defeats-the-reader  (x1)
```

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-01-05-improvement-review.md

Findings processed: 13 unread  →  7 clusters
```
"""

# The same document with both restatements re-derived.
_COUNT_OK = _MISCOUNT.replace("7 clusters", "3 clusters")

# Prose that NARRATES another review's cluster count must not fire. This is the exact shape that
# killed the three dropped checks: a review discussing "review 29's 13 unread → 7 clusters" is
# reporting history, not claiming its own figure. Scoping to the `Findings processed:` line prefix
# is what excludes it, and this fixture is what holds that scoping in place.
_NARRATED = _COUNT_OK.replace(
    "## 2. Clusters",
    "## 2. Clusters\n\nReview 29 said 13 unread → 7 clusters and was wrong; see below.")

# Both measured false positives, as fixtures. Each was a real document reporting a correct figure,
# and each must stay silent or this check ships at 60% precision.
#
# (i) an Addendum re-quotes a cluster block verbatim — 3 distinct clusters, 4 CLUSTER lines.
_REQUOTED = _COUNT_OK + """
## 10. Addendum — the deferred cluster was applied after all

```
CLUSTER C: output-shape-defeats-the-reader  (x1)
```
"""

# (ii) a class reconciled with no finding from this batch in it — declared `(x0`, so not one of the
# clusters the batch produced.
_CARRIED = _COUNT_OK + """
## 11. Carried forward

```
CLUSTER D: test-coupled-to-absolute-counts  (x0 NEW this session; IMP-0005 carried forward)
```
"""

_STRUCK_OK = _STALE.replace(
    "**Status:** AWAITING APPROVE IMPROVEMENTS — nothing in section 3 has been applied.",
    "**Status:** ~~AWAITING APPROVE IMPROVEMENTS — nothing applied~~ — corrected 2026-01-04: "
    "applied in full.")

# IMP-0404's EXACT shape, and the whole reason _sentences() became paragraph-scoped: the referent
# noun `TAD` sits at the end of one physical line and the section number it identifies begins the
# next. FOREIGN_DOC_RE would match "TAD §12.1" on one line; line-scoped, it never saw the noun and
# reported a foreign reference as a dangling self-reference. The document has a §1 and no §12.
_WRAPPED_FOREIGN_REF = """# Improvement Review — 2026-01-06

## 1. Regression check

This cluster is deferred because its remedy is the manual privilege revoke TAD
§12.1 names, which authenticates to a live environment.
"""

# The control: the same reference with no foreign noun anywhere IS a dangling self-reference and
# must still be reported, so the paragraph join has not simply switched the check off.
_WRAPPED_SELF_REF = _WRAPPED_FOREIGN_REF.replace(
    "the manual privilege revoke TAD\n§12.1 names", "the remedy described in\n§12.1")

# (e) PROPOSED-COUNT. A document declaring change 4a's closed vocabulary whose gate block and §3
# table agree. Both halves must be present for the check to run at all.
_COUNTS_OK = """# Improvement Review — 2026-01-07

## 3. Proposed changes

`Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
`script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change |
|---|---|---|---|
| 1 | script | scripts/a.py | one |
| 2 | script | scripts/b.py | two |
| 3 | knowledge | knowledge/x.md | three |
| 3a | agent | agents/y.md | four |
| 4 | template | templates/z.md | five |

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-01-07-improvement-review.md

Proposed:           0 constraints (cap 3), 2 gates/scripts, 1 skill/knowledge edits,
                    1 agent-file edits, 1 template edits, 0 retirements
Altitude calls:     1 generalised from instance to class
Digest:             will regenerate — 400 lessons, 37 recurring classes
```
"""

# Review 31's actual defect: three skill/knowledge rows, "1 skill/knowledge edits" claimed.
_COUNTS_WRONG = _COUNTS_OK.replace("| 3 | knowledge |", "| 3 | skill |").replace(
    "| 3a | agent | agents/y.md | four |",
    "| 3a | agent | agents/y.md | four |\n| 3b | knowledge | knowledge/w.md | six |\n"
    "| 3c | knowledge | knowledge/v.md | seven |")

# The SCOPING control: the same wrong arithmetic in a document that declares NO closed vocabulary
# is out of scope, because an open Type column measured 65 distinct values and ~1 true positive in
# 17 findings. Every one of the 39 existing documents is in this state.
_COUNTS_NO_VOCAB = _COUNTS_WRONG.replace(
    "`Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·\n"
    "`script` · `skill` · `knowledge` · `agent` · `template` · `other`.\n", "")

# A Type value outside the declared vocabulary — the declaration is what makes it decidable.
_COUNTS_OFF_VOCAB = _COUNTS_OK.replace("| 2 | script |", "| 2 | build-gate |")

# The `Digest:` line must NOT be swept into the sum. This is review 30's own defect, which it
# diagnosed as the whole problem, and this fixture holds the fix in place: `37 recurring classes`
# and `400 lessons` sit two lines below `Proposed:` and match no label.
_COUNTS_DIGEST_ADJACENT = _COUNTS_OK

# A SECOND table with the same `Type` column, in §10's applied record, must not be counted. This
# is what the check reported against its own author's document on its first real run: every figure
# came back exactly DOUBLE. Review 30's scoping defect, in a new place.
_COUNTS_APPLIED_TABLE = _COUNTS_OK.replace("## 9. Gate", """## 10. Applied

| # | Type | Change | Entries |
|---|---|---|---|
| 1 | script | scripts/a.py | IMP-0001 |
| 2 | script | scripts/b.py | IMP-0002 |
| 3 | knowledge | knowledge/x.md | IMP-0003 |
| 3a | agent | agents/y.md | IMP-0004 |
| 4 | template | templates/z.md | IMP-0005 |

## 9. Gate""")


def selftest() -> int:
    failures: list[str] = []

    def kinds_for(content: str, fname: str = "2026-01-01-improvement-review.md") -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / fname
            p.write_text(content, encoding="utf-8")
            return sorted(f.kind for f in check_document(p))

    if "LOST-DEFERRAL" not in kinds_for(_LOST):
        failures.append("a deferral to a section with no question was not reported (IMP-0302)")
    if "LOST-DEFERRAL" in kinds_for(_FOUND):
        failures.append("a deferral whose question IS present was reported anyway")
    if "CROSS-REF" not in kinds_for(_DANGLING):
        failures.append("a reference to a nonexistent section was not reported")
    if "CROSS-REF" in kinds_for(_LOST):
        failures.append("a resolvable section reference was reported as dangling")
    # IMP-0204's fixture must still fail under the gate that subsumed its check.
    if "STALE-HEADER" not in kinds_for(_STALE):
        failures.append("IMP-0204's fixture did not fail — coverage was LOST in the "
                        "generalisation, which is a regression, not a promotion")
    if "STALE-HEADER" in kinds_for(_STRUCK_OK):
        failures.append("a struck-through status was reported, so the gate forbids its own remedy")
    # (d) CLUSTER-COUNT. Three fixtures: it fires on the real IMP-0332 shape, it is silent when
    # the figures agree, and it is silent on prose narrating ANOTHER review's count — the last is
    # the one that decides whether this check is shippable at all.
    if "CLUSTER-COUNT" not in kinds_for(_MISCOUNT):
        failures.append("a gate block claiming 7 clusters over 3 CLUSTER blocks was not "
                        "reported (IMP-0332)")
    if kinds_for(_MISCOUNT).count("CLUSTER-COUNT") < 2:
        failures.append("only one of the two structural homes was checked — the header field and "
                        "the fenced gate block are BOTH restatements, and IMP-0332's real "
                        "instance had the body updated and the gate block left behind")
    if "CLUSTER-COUNT" in kinds_for(_COUNT_OK):
        failures.append("a document whose cluster figures agree was reported anyway")
    if "CLUSTER-COUNT" in kinds_for(_NARRATED):
        failures.append("prose narrating another review's cluster count was read as this "
                        "document's own claim — the failure mode that dropped the other three "
                        "checks IMP-0332 proposed")
    # The two measured false positives. Both were correct documents, and each fixture holds one
    # narrowing in place against a future simplification of the count.
    if "CLUSTER-COUNT" in kinds_for(_REQUOTED):
        failures.append("a cluster block RE-QUOTED in an addendum was counted twice — the "
                        "measured false positive on 2026-08-19-improvement-review-3.md, and the "
                        "reason the approved wording says 'distinct'")
    if "CLUSTER-COUNT" in kinds_for(_CARRIED):
        failures.append("a carried-forward cluster declaring `(x0` new members was counted as one "
                        "of this batch's clusters — the measured false positive on "
                        "2026-08-21-improvement-review-2.md")
    # IMP-0404. _sentences() is paragraph-scoped, so a foreign reference whose referent noun fell
    # on the previous physical line is no longer read as a dangling self-reference.
    if "CROSS-REF" in kinds_for(_WRAPPED_FOREIGN_REF):
        failures.append("a foreign document's section reference split across a hard wrap was "
                        "reported as a dangling self-reference — IMP-0404's exact defect, and "
                        "the reason _sentences() joins a paragraph before splitting it")
    if "CROSS-REF" not in kinds_for(_WRAPPED_SELF_REF):
        failures.append("a genuinely dangling reference split across a hard wrap was NOT "
                        "reported, so the paragraph join switched the check off rather than "
                        "fixing it")
    # (e) PROPOSED-COUNT. Four fixtures, and the third is the one that decides shippability.
    if "PROPOSED-COUNT" in kinds_for(_COUNTS_OK):
        failures.append("a document whose gate-block per-type figures agree with §3's rows was "
                        "reported anyway")
    if "PROPOSED-COUNT" not in kinds_for(_COUNTS_WRONG):
        failures.append("review 31's actual defect — three skill/knowledge rows against a "
                        "claimed 1 — was not reported (IMP-0397)")
    if "PROPOSED-COUNT" in kinds_for(_COUNTS_NO_VOCAB):
        failures.append("the same wrong arithmetic was reported in a document declaring NO "
                        "closed Type vocabulary. That scoping is what separates this from the "
                        "17-findings/1-true measurement the naive version produced, and all 39 "
                        "existing documents are in that state")
    if "PROPOSED-COUNT" not in kinds_for(_COUNTS_OFF_VOCAB):
        failures.append("a Type value outside the declared closed vocabulary was accepted")
    if "PROPOSED-COUNT" in kinds_for(_COUNTS_DIGEST_ADJACENT):
        failures.append("the gate block's Digest: line was swept into the Proposed: sum — review "
                        "30's own defect, which it mistook for the whole problem")
    if "PROPOSED-COUNT" in kinds_for(_COUNTS_APPLIED_TABLE):
        failures.append("§10's applied-record table was counted alongside §3's, doubling every "
                        "figure — the defect this check reported against its own author's "
                        "document on its first real run, and the reason the row count is scoped "
                        "to §3's body rather than to the whole file")

    with tempfile.TemporaryDirectory() as td:
        code, findings, n = run(Path(td))
        if code != 1 or not any(f.kind == "NO-SOURCE" for f in findings):
            failures.append("an empty directory did not report NO-SOURCE")
        code, findings, n = run(Path(td) / "absent")
        if code != 1 or not any(f.kind == "NO-SOURCE" for f in findings):
            failures.append("a missing directory did not report NO-SOURCE")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\nverify-review-document --selftest: FAILED ({len(failures)} failure(s)).",
              file=sys.stderr)
        return 1

    # DERIVED, not retyped. This line read "14 fixture(s)" while 21 assertions ran, which is
    # `hand-maintained-count-drifts-from-source` (x20) inside a gate whose own job is to catch a
    # document disagreeing with itself. Counted from the source of truth: the assertions.
    total = sum(1 for line in Path(__file__).read_text(encoding="utf-8").splitlines()
                if "failures.append(" in line)
    print(f"verify-review-document --selftest: OK — {total} assertion(s): a deferral to a "
          "questionless section reports and one with its question does not, at most once per "
          "target section (IMP-0302); a dangling section reference reports and a resolvable one "
          "does not; a FOREIGN document's section reference split across a hard wrap does NOT "
          "report while a genuinely dangling wrapped one still does, so paragraph-scoping fixed "
          "the check rather than switching it off (IMP-0404); IMP-0204's stale-header fixture "
          "still fails under the check that subsumed it, and a struck-through status does not, so "
          "the gate does not forbid its own remedy; a cluster count wrong in BOTH structural "
          "homes reports twice, an agreeing one does not, prose narrating another review's count "
          "does not, and neither a re-quoted cluster block nor an `(x0` carried-forward one is "
          "counted — both measured false positives (IMP-0332); a gate block's per-type Proposed "
          "figures are reconciled against §3's ROWS, but ONLY in a document declaring the closed "
          "Type vocabulary, and the adjacent Digest: line is not swept into the sum (IMP-0397); "
          "a missing and an empty directory both report rather than passing over nothing.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reviews-dir", type=Path, default=Path("docs/improvements"))
    parser.add_argument("--only", type=Path, default=None,
                        help="check a single document instead of the directory")
    parser.add_argument("--warn-only", action="store_true", help="print findings and exit 0")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove this gate can fail")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.only:
        if not args.only.is_file():
            print(f"usage error: {args.only} is not a file", file=sys.stderr)
            return 2
        findings = check_document(args.only)
        code, n = (1 if findings else 0), 1
    else:
        code, findings, n = run(args.reviews_dir)

    if findings:
        label = "WARNING" if args.warn_only else "ERROR"
        for f in findings:
            print(f"{label}: {f}", file=sys.stderr)
        by_kind: dict[str, int] = {}
        for f in findings:
            by_kind[f.kind] = by_kind.get(f.kind, 0) + 1
        print(f"\nverify-review-document: FAILED — "
              + ", ".join(f"{v} {k.lower()}" for k, v in sorted(by_kind.items()))
              + f", across {n} document(s)."
              + (" Exiting 0: --warn-only." if args.warn_only else ""), file=sys.stderr)
        return 0 if args.warn_only else code

    print(f"verify-review-document: OK — {n} review document(s): every section reference "
          f"resolves, every deferral to a section finds a question there, no status header "
          f"contradicts an Applied section, and every claimed cluster count matches the CLUSTER "
          f"blocks present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
