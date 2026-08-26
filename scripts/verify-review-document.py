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
AWAITING_RE = re.compile(
    r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s].*\bAWAITING\b", re.IGNORECASE | re.MULTILINE)
STRUCK_RE = re.compile(r"^\s*(?:>\s*)?\*{0,2}Status:?\*{0,2}[:\s]*~~",
                       re.IGNORECASE | re.MULTILINE)

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


def _sentences(text: str) -> list[tuple[int, str]]:
    """(line number, sentence) for every PROSE sentence — table rows excluded.

    Table rows are skipped deliberately. An Applied table's change description cites other
    documents' sections constantly ("§10 checklist: a removal recorded by someone else is
    re-queried", meaning the Dev Summary's assumption register) with no noun in the cell to mark
    them foreign, and reporting those buries the finding that matters. The defect this gate exists
    for — a deferral promised in the body and missing from the decisions section — is prose in both
    halves. Measured: this exclusion removes the last false positive on the current tree.
    """
    lines = text.splitlines()
    prose_offsets: list[tuple[int, str]] = []
    offset = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            prose_offsets.append((i, line))
        offset += len(line) + 1

    out: list[tuple[int, str]] = []
    for line_no, line in prose_offsets:
        for m in re.finditer(r"[^.!?\n]+[.!?]", line):
            out.append((line_no, m.group(0).strip()))
        # A line with no terminator still carries a reference worth resolving.
        if not re.search(r"[.!?]", line) and line.strip():
            out.append((line_no, line.strip()))
    return out


def check_document(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    name = path.name
    findings: list[Finding] = []
    sections = _sections(text)

    # ---- (c) STALE-HEADER — IMP-0204's half, subsumed from verify-improvement-log.py ----
    applied = APPLIED_HEADING_RE.search(text)
    if applied:
        for m in AWAITING_RE.finditer(text):
            line = m.group(0)
            if STRUCK_RE.search(line):
                continue
            # Only a status-ish line counts, not any prose mentioning the word.
            if not re.search(r"\*\*Status", line, re.IGNORECASE) and "AWAITING" not in line[:80]:
                continue
            findings.append(Finding(
                "STALE-HEADER", name, text[: m.start()].count("\n") + 1,
                f"the status header still claims AWAITING, but this document carries an "
                f"'Applied' section at line {text[: applied.start()].count(chr(10)) + 1}. One "
                f"document, two moments — and the header is the stale half. Strike it through "
                f"and date the correction (IMP-0204, IMP-0181)."))
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
    for line_no, sentence in _sentences(text):
        if not DEFERRAL_RE.search(sentence):
            continue
        for m in SECTION_REF_RE.finditer(sentence):
            num = int(m.group("num"))
            if num not in sections:
                continue  # already reported by (a)
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
                break

            if not BOLD_QUESTION_RE.search(body):
                findings.append(Finding(
                    "LOST-DEFERRAL", name, line_no,
                    f"defers a decision to section {num}, and section {num} contains no bold "
                    f"question at all (IMP-0302)."))
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

    print("verify-review-document --selftest: OK — 14 fixture(s): a deferral to a questionless "
          "section reports and one with its question does not (IMP-0302); a dangling section "
          "reference reports and a resolvable one does not; IMP-0204's stale-header fixture still "
          "fails under the check that subsumed it, and a struck-through status does not, so the "
          "gate does not forbid its own remedy; a cluster count wrong in BOTH structural homes "
          "reports twice, an agreeing one does not, prose narrating another review's count does "
          "not, and neither a re-quoted cluster block nor an `(x0` carried-forward one is counted "
          "— both measured false positives (IMP-0332); a missing and an empty directory both "
          "report rather than passing over nothing.")
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
