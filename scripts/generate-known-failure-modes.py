#!/usr/bin/env python3
"""Generate logs/known-failure-modes.md — the READ path of the self-learning loop.

Why this script exists
----------------------
This system never had a capture problem. build-agent and pipeline-agent already wrote
forensic-quality post-mortems: `logs/build.log` entries run to 300 words with confirmed
root causes, and build #6's manifest carried a structured
`defect_found_and_fixed_this_build` array with a `why_it_was_never_caught` field per
defect. Nothing ever read any of it back.

Those two agents were also the only ones in the roster whose activation loaded no
prior-experience input at all — not the deployment handover document, not their own logs,
not the assumption register. So every build re-entered the same minefield with no map, and
the map it drew on the way out went to a directory the next build overwrote.

The proof, in the reviewer's own words on 2026-08-17, about a procedure established the day
before: "yesterday you moved and got the certificate from the mac keychain. Make it so that
you can use that again."

This script turns the append-only log into something an agent can afford to read on every
activation: ONE page, deduplicated, ordered by recurrence, grouped by the moment in the
workflow where each lesson applies.

Why a generated digest and not the raw log
------------------------------------------
CLAUDE.md forbids re-reading files already in context and treats token cost as a first-class
constraint. A JSONL log that grows by ~20 entries a week cannot be read on every build. The
digest is capped, so its cost grows far more slowly than the log behind it.

BUT IT IS NOT FLAT, AND THIS DOCSTRING USED TO SAY IT WAS
---------------------------------------------------------
"its cost stays flat while the log behind it grows" was written when the log held 26 entries. It
is false, and it was believed: the WS-B capability workstream
(docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md) inferred from the
file's size that NO compaction existed at all, and recommended a 60-day age cutoff that selects
zero rows on a corpus 20 days old.

Measured 2026-09-01 at 562 log entries: the digest is 621 lines. Marginal growth has fallen from
~430 bytes per log entry (at 26-148 entries) to ~100, because MAX_PER_SECTION binds in 6 of the 10
populated sections. What still grows is the number of distinct CLASSES, not the number of
findings. Roughly 75% of the file is rendered lesson prose, bounded in count at
MAX_PER_SECTION x sections but not in length.

The line count above is registered in scripts/derived-counts-registry.json as
`known-failure-modes-digest-line-count`, so verify-derived-counts.py reports it the moment it
drifts. Do not retype it; that is what IMP-0529 and IMP-0534 are.

Usage
-----
    python3 scripts/generate-known-failure-modes.py            # writes logs/known-failure-modes.md
    python3 scripts/generate-known-failure-modes.py --check    # exit 1 if the file is stale
    python3 scripts/generate-known-failure-modes.py --stdout   # print, do not write

`--check` is what CI and the improvement-agent use: it regenerates in memory and compares,
so a log entry added without regenerating the digest is caught rather than silently ignored.

This script REFUSES to run over a structurally invalid log — and there is no flag to skip it
-----------------------------------------------------------------------------------------
Every agent's Improvement Capture block tells it to append a finding and then run THIS script.
Until 2026-08-28 this script parsed the log with a bare `json.loads` and validated nothing, so
it exited 0 over entries `verify-improvement-log.py` rejects. The two scripts disagreed about
what a valid entry is, and only the one nobody was instructed to run was authoritative.

The cost, on 2026-08-27 (`IMP-0369`): three agents appended eleven malformed entries and two
duplicate ids across one afternoon, each saw this script exit 0, and each moved on. The log went
red, a queued build was halted by the `improvement-log-check` step, and the defect was found only
because an unrelated agent happened to run the validator after its own append.

So this script now calls `check_schema(..., structural_only=True)` from
`verify-improvement-log.py` and exits 2 naming every bad entry. The subset is deliberate and
measured — see that function's docstring. There is intentionally NO `--skip-validation` flag: a
bypass is precisely the thing whose absence makes this change work.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

LOG = Path("logs/improvement-log.jsonl")
OUT = Path("logs/known-failure-modes.md")

# The on-demand half of the read path. Everything the digest's per-section caps hide, in full,
# plus every id the digest's tables truncate. NOT loaded at activation by any agent — it exists so
# that capping and truncating are RELOCATIONS rather than losses, which is the only basis on which
# a page whose job is to be read is allowed to hide anything at all.
APPENDIX = Path("logs/known-failure-modes-appendix.md")

# Maximum lessons rendered per section. Anything beyond is COUNTED AND NAMED, never
# silently dropped — a digest that truncates in silence reads as "this is everything".
# RAISED FROM 8 TO 20 ON 2026-08-19. At 47 entries the `before-build` section held 17
# lessons and SHOWED EIGHT — in the one section build-agent reads first, on the one page it
# reads before its own config. The cap was written when the log had 26 entries and no section
# was near it; it silently became a filter on the most-used page in the system. A digest that
# drops more than half of its busiest section is not a checklist.
#
# 20 is chosen to be above the largest current section with room to grow, not as a permanent
# answer: the real fix when a section genuinely exceeds this is to SPLIT the section (a new
# moment in the workflow), not to raise the number again. The dropped-lesson note below stays,
# so hitting the cap is still visible rather than silent.
MAX_PER_SECTION = 20

# ── Two class names, one property (improvement review 29 change 17, IMP-0330) ──────────────
#
# `test-coupled-to-absolute-counts` counts test fixtures asserting an absolute schema figure.
# `hand-maintained-count-drifts-from-source` counts hand-typed figures in documents. They are
# the SAME property — a value copied out of source drifting from source — and the finding that
# prompted this could have been filed under either.
#
# Why that matters here and not somewhere else: the altitude rule fires on the SECOND instance
# of a class, and sixteen instances of one property recorded as seven and nine produce a weaker
# signal than sixteen ever should. `skills/how-to-log-an-improvement.md` warns in as many words
# that a near-duplicate class name defeats the mechanism.
#
# THIS IS A READ-PATH ALIAS AND NOTHING MORE. It collapses the two rows of the recurring-classes
# table into one so the count is visible; it deliberately does NOT merge the remedies, does NOT
# change which section a lesson renders in, and does NOT rewrite any entry's own
# `class_instance_of`. A test fixture and a report figure are checked by different tools and
# both of those tools work. The canonical name is the one that describes the property rather
# than one of its two victims.
CLASS_ALIASES: dict[str, str] = {
    "test-coupled-to-absolute-counts": "hand-maintained-count-drifts-from-source",
}


def canonical_class(cls: str) -> str:
    """The name a class is COUNTED under in the recurring-classes table."""
    return CLASS_ALIASES.get(cls, cls)


# ── Id enumeration is the file's only genuinely unbounded term (improvement review 10) ──────
#
# Measured 2026-09-01 at 539 log entries: exhaustive id lists cost 8,160 bytes — 4,710 in the
# Recurring-classes table's `Findings` column and 3,450 in the capped-lesson index — and both grow
# by ~11 bytes for every finding ever logged, forever. Every other term in this file is bounded:
# rendered lesson prose is MAX_PER_SECTION x sections, and the prose blocks are constant.
#
# Truncating to the SIX MOST RECENT ids keeps what a reader actually uses — "has this bitten us
# lately, and where do I look" — and drops the archaeology. The COUNT is never truncated: `x27`
# still reads `x27`, because the count is the promotion-ladder signal and the whole point of the
# table. Only the enumeration moves, and it moves into the appendix rather than out of existence.
MAX_IDS_PER_ROW = 6

# ── Per-lesson rendered-length budget (improvement review 7, 2026-09-01) ─────────────────────
#
# MAX_PER_SECTION bounds how MANY lessons render. Nothing bounded how LONG each one is, and that
# is the axis this file actually grew on: mean lesson length measured 256 characters over the
# log's first six days and 583 over its last six — 2.3x, on 555 findings totalling ~300,000
# characters of lesson text. A future 800-entry log at today's mean writes a materially bigger
# digest than an 800-entry log at the original mean, with the cap unchanged and nothing reporting
# it. Every activation of build-agent, pipeline-agent, pm-agent, acceptance-agent,
# commercial-agent and test-agent pays that difference.
#
# The budget TRUNCATES IN THE DIGEST ONLY. The log keeps every lesson whole, and the appendix
# already renders capped lessons in full — so an over-budget lesson is relocated, never lost,
# which is the same contract the per-section cap already operates under.
#
# CHOSEN BY MEASUREMENT, NOT BY TASTE. The generator was run at 400, 600 and 800 and the truncated
# text inspected at each. 400 cut mid-mechanism through the platform-contract lessons whose detail
# is the entire value — the Dataverse PUT-vs-PATCH lesson lost the "full current object" clause,
# which is the half a reader needs. 800 truncated almost nothing and moved the size barely at all.
# 600 is the knee: it leaves every measured platform-contract lesson's mechanism intact while
# catching the long procedural narratives, whose first two sentences carry the instruction and
# whose remainder is the incident story.
LESSON_BUDGET = 600

# Truncation must land on a sentence boundary, never mid-clause: a lesson cut at "never use PUT
# with a partial" inverts its own instruction. If no boundary exists inside the budget the lesson
# renders whole — a run-on sentence is not improved by being severed.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def correction_markers(fs: list[dict], corrected: dict, contested: dict) -> list[str]:
    """The '⚠ CORRECTED / CONTESTED' sub-lines for one lesson, or [].

    ONE implementation, called by BOTH renderers (improvement review 8, `IMP-0565`).

    This used to live only inside `render()`'s `emit()`. `render_appendix()` has its own `emit()`
    and never got it — so a lesson a later finding had DISPROVED lost its warning the moment it
    fell past the per-section cap, and read as authoritative in the very file the digest sends
    readers to for capped detail. Measured 2026-09-01: 10 CORRECTED and 1 CONTESTED markers in the
    digest, **0** in the appendix, with 10 marked lessons rendering only in the appendix.

    The selftest that missed it asserted every capped lesson APPEARS in the appendix — a presence
    check inside one renderer. The assertion that catches this class is a COMPARISON BETWEEN the
    two renderers, and it is in `selftest()` now. Same shape as `IMP-0563`: a second renderer does
    not inherit the first one's guarantees, and only a cross-renderer assertion notices.
    """
    marks = sorted({c for f in fs for c in corrected.get(f["id"], [])})
    if marks:
        by = ", ".join(f"`{m}`" for m in marks)
        return [f"  <br><sub>**⚠ CORRECTED by {by}** — a later finding contradicts this "
                f"lesson. Read both before acting on it; the marker does not decide which "
                f"is right.</sub>"]
    # A lesson whose claim is DISPUTED but unsettled is not corrected, and must not read as
    # authoritative either (IMP-0460). Suppressed when a `corrects` marker already stands:
    # "wrong" subsumes "disputed", and two markers on one lesson read as noise.
    disputes = sorted({c for f in fs for c in contested.get(f["id"], [])})
    if disputes:
        by = ", ".join(f"`{m}`" for m in disputes)
        return [f"  <br><sub>**⚠ CONTESTED by {by}** — a later finding disputes a claim in "
                f"this lesson and NEITHER has been re-tested. Read that entry before relying "
                f"on this one; it carries the form that is safe under either answer.</sub>"]
    return []


def budget_lesson(lesson: str, budget: int | None = None) -> tuple[str, bool]:
    """Return (rendered_lesson, was_truncated), cutting only at a sentence boundary.

    `budget` is resolved at CALL time, not bound as a default: `budget=LESSON_BUDGET` in the
    signature captures the value when this function is DEFINED, so a caller sweeping the constant
    to compare 400/600/800 would silently measure 600 four times and read four identical digest
    sizes as evidence the budget does nothing. That is the shape of a measurement that never ran
    (IMP-0542) — and it happened while measuring this very change.
    """
    if budget is None:
        budget = LESSON_BUDGET
    if budget <= 0 or len(lesson) <= budget:
        return lesson, False
    cut, out = 0, ""
    for piece in _SENTENCE_END.split(lesson):
        nxt = (out + " " + piece).strip() if out else piece
        if len(nxt) > budget:
            break
        out, cut = nxt, len(nxt)
    if not out:
        return lesson, False          # no boundary inside the budget — leave it whole
    return out, cut < len(lesson.strip())


def id_number(finding_id: str) -> int:
    """The numeric part of `IMP-nnnn`, for ordering by recency. 0 if unparseable."""
    try:
        return int(str(finding_id).split("-")[1])
    except (IndexError, ValueError):
        return 0


def id_cell(ids: list[str]) -> str:
    """An id list for a table cell, truncated to the MAX_IDS_PER_ROW most recent.

    The full list is always in `logs/known-failure-modes-appendix.md`, so this is a RELOCATION
    and never a loss — which is the only reason truncating is acceptable on a page whose entire
    job is to be the read path.
    """
    ordered = sorted(set(ids), key=id_number)
    if len(ordered) <= MAX_IDS_PER_ROW:
        return ", ".join(ordered)
    kept = ordered[-MAX_IDS_PER_ROW:]
    return f"{', '.join(kept)} (+{len(ordered) - MAX_IDS_PER_ROW} earlier — see appendix)"

# Routing table: class_instance_of -> the section (i.e. the moment in the workflow where the
# lesson applies). Deterministic and reviewable; the improvement-agent edits this table when
# it introduces a new class, so a new class cannot land in no section at all.
SECTIONS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "before-build",
        "Before you execute a build config",
        ("gate-cannot-fail", "gate-scope-mismatch", "repo-path-contains-spaces",
         "test-coupled-to-absolute-counts", "two-invocation-paths-disagree",
         # Added 2026-08-19 with IMP-0057. The mirror of gate-cannot-fail: a gate that
         # fires on nothing. Same section, because it is the same moment — you are about
         # to trust what a build gate just told you.
         "gate-fires-on-nothing"),
    ),
    (
        "before-authoring",
        "Before you hand-author a platform artefact",
        ("platform-contract-guessed-not-groundtruthed", "platform-field-length-limit-unenforced",
         # Added 2026-08-22 (improvement review 10). Both were landing in Unrouted, which by
         # that section's own words reaches nobody, while both apply at exactly this moment.
         # `platform-fact-groundtruthed` is the same question as its `-guessed-` sibling asked
         # from the other side — someone went and got the ground truth, and the next person
         # about to hand-author against that platform is who needs it (IMP-0185, IMP-0193,
         # IMP-0194, IMP-0195). `environment-feature-flag-undeclared` is a per-environment
         # product toggle that no solution source can carry and no script can read back
         # (IMP-0182).
         "platform-fact-groundtruthed", "environment-feature-flag-undeclared"),
    ),
    (
        "before-deploy",
        "Before you declare a deploy or an import successful",
        ("exit-zero-does-not-mean-created", "v3-does-not-imply-v4",
         "register-predicts-but-does-not-block"),
    ),
    (
        "before-success",
        "Before you report SUCCESS at all",
        ("no-assertion-on-shipped-content", "learning-substrate-destroyed"),
    ),
    (
        "operating",
        "Operating constraints of this environment",
        (
            "harness-blocks-destructive-call",
            "repo-path-contains-spaces",
            # Added 2026-08-24 (IMP-0253). Same shape as repo-path-contains-spaces: a local
            # fact about THIS machine that breaks a command assumed portable. It was landing in
            # Unrouted, inside an overflow of 33 lessons the digest names but does not print,
            # so the lesson reached the file and no reader.
            "instruction-untested-in-target-shell",
        ),
    ),
    # Added 2026-08-19. Three classes were landing in Unrouted — which reaches nobody at the
    # moment it applies — and all three are about the same moment: you are about to run
    # something somewhere it has never actually run. IMP-0048 (a certificate thumbprint
    # exported to a runner with an empty certificate store), IMP-0054 (a filename whose case
    # only resolves on a case-insensitive filesystem) and C-TECH-054's original incident (a
    # Windows-only PSDrive in a script bound for a Linux runner) are one question asked three
    # ways: does this work on the machine that will run it, as opposed to the one it was
    # written on?
    (
        "before-running-elsewhere",
        "Before you run something on a machine it has never run on",
        ("credential-not-on-the-machine-that-needs-it", "os-specific-assumption-untested",
         "agent-instructions-describe-a-topology-that-changed",
         # Added 2026-08-21 (improvement review 3). Both landed in the Unrouted section,
         # which reaches nobody, while their entire purpose is to be read at exactly this
         # moment — before a script is pointed at an environment it has not run against.
         # IMP-0145 (a settings placeholder known for a day and never fixed) and IMP-0146
         # (a provisioning identity with no application user in the target org).
         "config-placeholder-known-but-not-fixed",
         "provisioning-identity-not-onboarded-to-target-environment"),
    ),
    # Added 2026-08-18 (improvement review). Five lessons were landing in the Unrouted
    # section — which reaches nobody at the moment it applies — because the commercial and
    # self-change classes had no home. Section name and the first three classes are as
    # specified in docs/improvements/2026-08-18-project-management-system-redesign.md §5.2;
    # the last two are declared here ahead of the scripts that will emit them, so a finding
    # logged before that work lands still routes.
    (
        "before-commercial",
        "Before you bill an hour, accept a phase, or report status",
        ("baseline-restated-not-cited", "work-order-not-driven-by-contract",
         "instrument-exists-never-used", "billable-hour-without-resolving-evidence",
         "status-claimed-above-verification-level",
         # Added 2026-08-19 when the PM capability was built. `completion-claimed-not-verified`
         # is the spreadsheet form of exit-zero-does-not-mean-created and `invoiced-is-not-
         # completed` its commercial form; both apply at this moment, not at deploy time.
         "commercial-baseline-wrong", "completion-claimed-not-verified",
         "invoiced-is-not-completed", "double-billed-session",
         "contract-date-used-as-a-delivery-fact",
         "evidence-rule-satisfied-by-a-forward-reference"),
    ),
    # These two are about this system changing ITSELF rather than about delivery, so they
    # apply at a different moment: when a request arrives that is not a feature.
    (
        "before-extending",
        "Before you extend this system or accept a new kind of input",
        ("no-route-for-system-capability-request", "input-type-with-no-owning-agent",
         # Added 2026-08-19 with IMP-0059. Not about delivery — about the moment an agent
         # writes something a human has to act on.
         "output-shape-defeats-the-reader",
         # Added 2026-08-19 with IMP-0062.
         "test-seam-in-the-wrong-scope",
         # IMP-0034 — an agent's declared Knowledge to Load pointing at template scaffolding.
         # It sat in Unrouted from 2026-08-18 until 2026-08-19, which is exactly the failure
         # the Unrouted section exists to make visible.
         "declared-knowledge-source-is-empty"),
    ),
]

HEADER = """\
# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` ({n_entries} entries, {n_lessons} distinct lessons)
Generated: {generated}

## How to use this file

Read it **before** your own config or instruction set, and treat it as a checklist against
that config — not as background reading. Every line below is a defect that actually happened
on this project, with the finding ids that recorded it. A `x{{n}}` marker means that class has
now recurred {{n}} times, which is the system telling you a general gate is missing where an
instance patch was applied.

`build-agent` and `pipeline-agent` load this file on activation
(`agents/build-agent.md` step 0, `agents/pipeline-agent.md` step 0). Other agents load it
when their work touches a listed area.
"""

FOOTER = """\
---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
"""


def load(log_path: Path) -> list[dict]:
    if not log_path.exists():
        raise FileNotFoundError(f"{log_path} does not exist — nothing to generate from")
    rows = []
    for i, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{log_path}:{i} is not valid JSON: {exc}") from exc
        # The validator's messages name the LINE for a duplicate id, so carry it. Without
        # this the duplicate-id error reads "also on line ?" and the reader has to grep.
        if isinstance(row, dict):
            row.setdefault("__line", i)
        rows.append(row)
    return rows


def structural_errors(rows: list[dict], repo_root: Path | None = None) -> list[str]:
    """Errors about the entries' own shape, borrowed from the authoritative validator.

    See this module's docstring for why the digest generator validates at all, and
    `verify-improvement-log.py`'s `check_schema` for why the subset is structural-only.

    Returns [] if the validator cannot be imported — a missing sibling must not make the
    digest unbuildable, but it IS reported, because silently degrading to the old
    validate-nothing behaviour is the exact defect this function exists to close.
    """
    import importlib.util

    sibling = Path(__file__).resolve().parent / "verify-improvement-log.py"
    if not sibling.exists():
        print(f"generate-known-failure-modes: WARNING — {sibling.name} not found beside this "
              f"script, so the log was NOT validated. Run it yourself before trusting this "
              f"digest (IMP-0369).", file=sys.stderr)
        return []
    try:
        spec = importlib.util.spec_from_file_location("_rev_improvement_log_validator", sibling)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module.check_schema(rows, repo_root or Path.cwd(), structural_only=True)
    except Exception as exc:  # pragma: no cover — a broken validator, not a broken log
        print(f"generate-known-failure-modes: WARNING — could not run {sibling.name}'s schema "
              f"check ({exc}), so the log was NOT validated (IMP-0369).", file=sys.stderr)
        return []


# ── Where a lesson actually renders, and by which mechanism (IMP-0198) ────────────────────
# THREE independent mechanisms decide a lesson's section, and they have a silent precedence:
#
#   1. `capability: true` on ANY finding sharing the lesson  → "Capabilities", always, whatever
#      the class says. This one is invisible from the class routing table below.
#   2. the SECTIONS routing table                            → that section
#   3. nothing matches                                       → "Unrouted"
#
# And a fourth, subtler one: a class named in TWO section tuples resolves to the LAST, because
# `section_of` is built by overwriting. `repo-path-contains-spaces` is in both `before-build`
# and `operating` today and renders only in `operating`.
#
# Improvement review 10 predicted the Unrouted section would fall 31 -> 26 by adding two classes
# to the table. Measured: 31 -> 30. Four of the five findings carried `capability: true` and had
# never been in Unrouted at all — mechanism 1 had already placed them, and nothing rendered said
# so. The recurring-classes table showed the class; it did not show where the class's lessons
# actually went. That is what these two functions exist to make visible.

CAPABILITY_SECTION = "Capabilities"
UNROUTED_SECTION = "Unrouted"


def build_section_of() -> dict[str, str]:
    """class_instance_of -> section key. Last tuple wins, which is mechanism 4 above."""
    section_of: dict[str, str] = {}
    for key, _title, classes in SECTIONS:
        for c in classes:
            section_of[c] = key
    return section_of


def duplicated_classes() -> dict[str, list[str]]:
    """Classes named in more than one section tuple, with every section that names them."""
    seen: dict[str, list[str]] = defaultdict(list)
    for key, _title, classes in SECTIONS:
        for c in classes:
            seen[c].append(key)
    return {c: keys for c, keys in seen.items() if len(keys) > 1}


def routing_of(rows: list[dict]) -> dict[str, dict[str, int]]:
    """For each class, how many of its LESSONS render in which section.

    Keyed by class, then by section key (or ``Capabilities`` / ``Unrouted``). Counts lessons,
    not findings, because a lesson is what the digest renders as a line.
    """
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    by_lesson: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_lesson[r["lesson"]].append(r)

    section_of = build_section_of()
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for lesson, findings in by_lesson.items():
        cls = findings[0].get("class_instance_of", "unclassified")
        if any(f.get("capability") for f in findings):
            where = CAPABILITY_SECTION
        else:
            where = section_of.get(cls) or UNROUTED_SECTION
        # Keyed by the CANONICAL name so the aliased row can find its own breakdown. The
        # section each lesson renders in is untouched — an alias merges the count, never the
        # remedy, so an aliased row honestly shows both sections its lessons live in.
        out[canonical_class(cls)][where] += 1
    return {c: dict(v) for c, v in out.items()}


def renders_in(breakdown: dict[str, int]) -> str:
    """One compact cell naming every section a class's lessons render in, and how many."""
    parts = []
    for where, n in sorted(breakdown.items(), key=lambda kv: (-kv[1], kv[0])):
        parts.append(f"`{where}`" + (f" ×{n}" if n > 1 else ""))
    return ", ".join(parts)


def corrections_of(rows: list[dict]) -> dict[str, list[str]]:
    """corrected finding id -> the ids of the findings that CORRECT it.

    WHY THIS EXISTS (improvement review 29 change 8, IMP-0314). `corrects` appeared nowhere in
    this generator — grep returned nothing — so the digest had no handling of the field at all.
    A lesson a later finding has DISPROVED rendered as authoritative on the one page every
    agent reads first, and there is no page where that costs more.

    The instance: `IMP-0287` recorded that under Auto Mode a cert-touching `pwsh` call is
    refused regardless of read or write, and that a dispatched agent has zero live-Dataverse
    reach. `IMP-0314` then ran two `provisioning/dataverse/*.ps1` WRITES against DEV from a
    primary agent's own foreground session, exit 0 both times, verified afterwards by read
    queries against the same environment. The blanket claim is wrong for that shape.

    WHAT THE MARKER DOES AND DOES NOT DO. It sends the reader to both entries. It does not
    decide which is right, it does not edit or delete the original lesson, and it does not
    rewrite history — `IMP-0287`'s observation may still hold for nested dispatches, which is
    exactly why the correcting entry is surfaced BESIDE it rather than replacing it.

    Only findings still carrying a lesson can be corrected in a way the reader can act on, so
    a `corrects` naming an id that is absent, REJECTED or lessonless is ignored here;
    `check_corrections()` in scripts/verify-improvement-log.py is what reports those.
    """
    live_ids = {r.get("id") for r in rows
                if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")}
    out: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        # `corrects` is a string OR a list of ids (IMP-0420, review 36 change 9). One disproved
        # root cause may be recorded in several findings, and marking one of them left the others
        # rendering as authoritative — IMP-0010's lesson still LED with the disproved
        # space-in-path cause while IMP-0079's carried the marker. The previous `str()` coercion
        # turned a list into "['IMP-0010', ...]", which resolved to nothing and was dropped here
        # in silence: the failure shape that hides itself.
        for target in corrects_targets(r):
            if target in live_ids and r.get("id"):
                out[target].append(str(r["id"]))
    return {k: sorted(v) for k, v in out.items()}


def corrects_targets(row: dict) -> list[str]:
    """The finding id(s) this entry supersedes. Scalar or list; both accepted (`IMP-0420`).

    Deliberately duplicated from scripts/verify-improvement-log.py rather than imported: these
    two scripts share no module today, and introducing an import between them to save nine lines
    would couple the digest generator to the validator's load order. If a third consumer of
    `corrects` appears, that is the point to move all three into scripts/lib/.
    """
    value = row.get("corrects")
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def contests_of(rows: list[dict]) -> dict[str, list[str]]:
    """contested finding id -> the ids of the findings that CONTEST it.

    A SECOND, WEAKER EDGE THAN `corrects`, and the distinction is the whole point. `corrects`
    means *the earlier entry is wrong* — `skills/how-to-log-an-improvement.md` requires that it be
    established, and `knowledge/technology/power-automate.md` reserves it for whichever of two
    rival claims eventually loses. `contests` means *the earlier entry's claim is DISPUTED and
    nobody has settled it*, which is a state this repository was already in and had no way to
    render.

    WHY IT EXISTS (`IMP-0460`). `IMP-0124`'s lesson is one sentence carrying two claims of very
    different standing: `select()`/`filter()` do not exist as expressions — ground-truthed, and
    enforced by `verify-flow-definition-language.py` check 1 — followed by a trailing
    *"Related: if() evaluates ONLY the branch it takes here"*, which `IMP-0378` contradicts from
    Microsoft's function reference and `IMP-0412` records as OPEN. The digest rendered the whole
    sentence verbatim, so the contested clause read with the ground-truthed clause's authority on
    the one page every agent loads first — and it is the clause an author reaches for when writing
    a guard. One did: a `wbs:6.9` dispatch brief quoted it as settled ground truth, and the
    expression built on it had to be rewritten before it shipped.

    WHAT THE MARKER DOES NOT DO. It does not decide the question, and it does not say which clause
    of a multi-claim lesson is the contested one — it cannot; a lesson is one string. It sends the
    reader to the entry that frames the dispute, which is where the safe-under-either-answer
    instruction lives.

    Same resolution rules as `corrections_of`: an id that is absent, REJECTED or lessonless is
    ignored here.
    """
    live_ids = {r.get("id") for r in rows
                if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")}
    out: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        for target in contests_targets(r):
            if target in live_ids and r.get("id"):
                out[target].append(str(r["id"]))
    return {k: sorted(v) for k, v in out.items()}


def contests_targets(row: dict) -> list[str]:
    """The finding id(s) whose claim this entry DISPUTES without settling. Scalar or list.

    Accepts a list from the outset: `corrects` did not, and `IMP-0420` is what that cost — a
    one-to-one field met a one-to-many world, a list was coerced by `str()` into a string that
    resolved to nothing, and it was dropped in silence.
    """
    value = row.get("contests")
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def live_lessons(rows: list[dict]) -> dict[str, list[dict]]:
    """Lesson text -> the findings carrying it.

    Only APPLIED and NEW entries carry lessons forward. A finding the improvement-agent reviewed
    and explicitly rejected must not keep teaching.

    Deduplicating on lesson TEXT is meant to collapse two findings teaching the same thing into one
    line with an `x{n}` marker. MEASURED 2026-09-01, IT MERGES NOTHING: 543 live findings produce
    543 distinct lesson texts, and the marker has never fired. See `sort_key` for what that cost —
    an aggregation that never aggregates promoted the tiebreak below it into the ranking function.
    It is kept rather than deleted because it is correct if lesson texts ever do repeat, and
    `main()` now prints the merge count so its inertness is visible at every run (`IMP-0545`).
    """
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    by_lesson: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_lesson[r["lesson"]].append(r)
    return by_lesson


def group_lessons(
    rows: list[dict],
) -> tuple[dict[str, list[tuple[str, list[dict]]]],
           list[tuple[str, list[dict]]],
           list[tuple[str, list[dict]]]]:
    """(section key -> lessons, capability lessons, unrouted lessons).

    ONE placement function, used by both the digest and the appendix. They must agree about what
    is capped: an appendix that computed placement independently could omit the very lesson the
    digest says to look there for, and nothing would report it.
    """
    section_of = build_section_of()
    grouped: dict[str, list[tuple[str, list[dict]]]] = defaultdict(list)
    capabilities: list[tuple[str, list[dict]]] = []
    unrouted: list[tuple[str, list[dict]]] = []

    for lesson, findings in live_lessons(rows).items():
        if any(f.get("capability") for f in findings):
            capabilities.append((lesson, findings))
            continue
        key = section_of.get(findings[0].get("class_instance_of", ""))
        if key is None:
            unrouted.append((lesson, findings))
        else:
            grouped[key].append((lesson, findings))
    return grouped, capabilities, unrouted


def render(rows: list[dict], generated: str) -> str:
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    by_lesson = live_lessons(rows)
    grouped, capabilities, unrouted = group_lessons(rows)

    def sort_key(item: tuple[str, list[dict]]) -> tuple[int, int, int, int]:
        """What survives the per-section cap: recurring, then blocker, then UNFIXED, then NEWEST.

        THIS KEY USED TO END IN ASCENDING ID, AND THAT MEANT OLDEST-FIRST (`IMP-0543`, the second
        instance of `IMP-0383`'s class — the first fix indexed what the cap hid without changing
        WHICH lessons it hid).

        The mechanism is worth stating, because it is a trap any ranking function can fall into.
        Deduplication is on lesson TEXT, and lesson text is free prose that this project's own
        reporting standards push toward long, incident-specific paragraphs — mean length rose from
        ~180 chars on 2026-08-14 to ~600 by 2026-08-22. Exact string equality across independently
        authored 500-character paragraphs is effectively never true, so measured on 2026-09-01,
        543 live findings produced 543 distinct lesson texts and `-len(fs)` was CONSTANT at -1 for
        every item in the corpus. A term that never discriminates is not a no-op: it silently
        promotes the term below it. Ascending id stopped being a stable-sort tiebreak and became
        the ranking function — and on a defect log, ascending id means preferring the lessons most
        likely to be already fixed.

        What that cost, measured before the change: of 176 rendered lessons, 150 were already
        `APPLIED`; rendered median timestamp was 2026-08-20 against 2026-08-26 for the 367 the cap
        hid; and of 253 lessons logged on or after 2026-08-25, TWENTY-FIVE reached the page that
        `build-agent` and `pipeline-agent` read at activation step 0.

        The two new terms encode the selection the WS-B design document's own criteria imply —
        prefer what is not yet fixed, then prefer what is recent — rather than inheriting whatever
        a tiebreak happens to do once the terms above it go inert.
        """
        _lesson, fs = item
        blockers = sum(1 for f in fs if f.get("severity") == "blocker")
        # An unfixed lesson is one no review has closed yet: it is still live experience, where an
        # APPLIED one usually has a gate standing behind it now.
        unfixed = 0 if any(f.get("status") == "NEW" for f in fs) else 1
        return (-len(fs), -blockers, unfixed, -id_number(fs[0]["id"]))

    out: list[str] = [
        HEADER.format(n_entries=len(rows), n_lessons=len(by_lesson), generated=generated)
    ]

    # ── Recurring classes: the promotion-ladder signal, surfaced at the top ───────────
    # A class with n>=2 means an instance was patched where a general gate was needed. On
    # this project that is not hypothetical: the 256-char flow-description cap and the
    # 500-char setting-description cap were fixed by two separate scripts, and the "import
    # reported success but created nothing" class was rediscovered two days after its first
    # appearance because nothing generalised the first fix.
    by_class: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_class[canonical_class(r.get("class_instance_of", "unclassified"))].append(r)
    recurring = sorted(
        ((c, fs) for c, fs in by_class.items() if len(fs) >= 2),
        key=lambda kv: (-len(kv[1]), kv[0]),
    )
    if recurring:
        out.append("\n## Recurring classes — where a general gate is missing\n")
        out.append(
            "Each of these has happened more than once. Per "
            "`skills/how-to-promote-a-finding.md`, the second instance of a class may **not** "
            "get another instance-level patch: it must be generalised, and the instance gates "
            "retired.\n"
        )
        out.append(
            "**`Renders in` is where this class's lessons actually appear below** — not where "
            "the routing table says they should. A lesson whose finding carries "
            "`capability: true` renders under `Capabilities` whatever its class, so a class can "
            "sit in this table and have none of its lessons in the section you expect. Reading "
            "the class name alone and inferring a section is how one review predicted a digest "
            "delta of 31→26 and measured 31→30 (`IMP-0198`).\n"
        )
        routing = routing_of(rows)
        out.append("| Count | Class | Renders in | Findings |")
        out.append("|---|---|---|---|")
        for cls, fs in recurring:
            ids = id_cell([f["id"] for f in fs])
            where = renders_in(routing.get(cls, {}))
            aliased = sorted({c for c in CLASS_ALIASES if CLASS_ALIASES[c] == cls
                              and any(f.get("class_instance_of") == c for f in fs)})
            name = f"`{cls}`"
            if aliased:
                name += " (also logged as " + ", ".join(f"`{c}`" for c in aliased) + ")"
            out.append(f"| **x{len(fs)}** | {name} | {where} | {ids} |")
        out.append("")

        if any(CLASS_ALIASES[c] == cls for cls, _ in recurring for c in CLASS_ALIASES):
            pairs = "; ".join(f"`{c}` → `{canon}`" for c, canon in sorted(CLASS_ALIASES.items()))
            out.append(
                f"> **Two class names describing one property are COUNTED as one row here.** "
                f"{pairs}. The alias is in this table only: each lesson still renders in its own "
                f"section below, and the two halves keep their own gates, because a test "
                f"fixture and a figure in a document are checked by different tools. The count "
                f"is merged because the altitude rule fires on the *second* instance of a class "
                f"— and a property recorded under two names produces a weaker signal than its "
                f"true instance count ever should (`IMP-0330`).\n"
            )

        dupes = duplicated_classes()
        if dupes:
            listed = "; ".join(
                f"`{c}` → {', '.join(f'`{k}`' for k in keys)} (renders in `{keys[-1]}`)"
                for c, keys in sorted(dupes.items())
            )
            out.append(
                f"> **A class named in two sections renders only in the last one.** {listed}. "
                f"This is a silent precedence in the routing table, not a decision anything "
                f"records — fix it by naming the class once, in the section where the lesson "
                f"actually applies.\n"
            )

    corrected = corrections_of(rows)
    contested = contests_of(rows)

    def _capped_index(dropped: list[tuple[str, list[dict]]]) -> list[str]:
        """The capped-lesson note, as an INDEX GROUPED BY CLASS rather than a flat id list.

        `IMP-0383`. This note used to be one run of ids: "41 further lesson(s) … Findings:
        IMP-0024, IMP-0026, …". Grepping all 498 lines of the digest for CSS, theming, fonts,
        contrast, accessibility, npm, Vite, React or TypeScript returned **zero rendered
        lessons** — every front-end lesson on the project sat behind a per-section cap, named by
        id only, in a section that read as complete. The digest is the READ PATH: build-agent and
        pipeline-agent read it at activation step 0.

        Grouping by `class_instance_of` is FULLY DERIVED — no subject vocabulary to maintain, and
        nothing to go stale as the project's subject areas change. A reader scanning the note now
        sees WHICH KINDS of lesson are hidden, not just how many.

        BE CLEAR ABOUT WHAT THIS DOES NOT DO, because it is weaker than the two fixes the cap's
        own comment prefers: it does NOT raise the cap and does NOT split any section. It makes
        what is hidden FINDABLE rather than VISIBLE. The honest reason is that ~105 lessons sit
        behind caps across five sections, and splitting five sections into new workflow moments
        is a design decision about when agents read what — not a defect fix, and not one to take
        inside a batch review. `--subject <term>` is the other half: it prints every matching
        lesson whether rendered or capped.
        """
        by_class: dict[str, list[str]] = {}
        for _key, findings in dropped:
            for finding in findings:
                cls = canonical_class(str(finding.get("class_instance_of")
                                          or finding.get("class") or "unclassified"))
                by_class.setdefault(cls, []).append(finding["id"])
        total = sum(len(ids) for ids in by_class.values())
        lines = [
            f"\n> **{total} further lesson(s) in this section are not shown** "
            f"(cap: {MAX_PER_SECTION}), indexed below by class so you can see WHAT KIND of "
            f"lesson you are not being shown — not only how many. Read one with "
            f"`python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints "
            f"every matching lesson rendered or capped; read the full text of every capped "
            f"lesson in `{APPENDIX.name}`; or read them all in `logs/improvement-log.jsonl`."
        ]
        for cls, ids in sorted(by_class.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            lines.append(f">   · **`{cls}`** (×{len(ids)}): {id_cell(ids)}")
        return lines

    def emit(title: str, items: list[tuple[str, list[dict]]], note: str = "") -> None:
        if not items:
            return
        items = sorted(items, key=sort_key)
        total_findings = sum(len(f) for _, f in items)
        out.append(f"\n## {title}\n")
        if note:
            out.append(f"{note}\n")
        plural = lambda n, w: f"{n} {w}" + ("" if n == 1 else "s")  # noqa: E731
        out.append(f"*{plural(len(items), 'lesson')} from {plural(total_findings, 'finding')}.*\n")
        shown = items[:MAX_PER_SECTION]
        for lesson, fs in shown:
            ids = ", ".join(sorted(f["id"] for f in fs))
            recur = f" **x{len(fs)}**" if len(fs) > 1 else ""
            shown_lesson, truncated = budget_lesson(lesson)
            if truncated:
                # Say the text was cut and where the rest is. A silent truncation would be the
                # worse defect: a reader cannot tell a lesson that ends from one that stops.
                shown_lesson += (" **[…]** <sub>*truncated — full text in "
                                 "`known-failure-modes-appendix.md`*</sub>")
            out.append(f"- {shown_lesson}{recur}  \n  <sub>{ids}</sub>")
            # A lesson a later finding has disproved must not read as authoritative here.
            # Shared with render_appendix() so the two renderers cannot drift (IMP-0565).
            out.extend(correction_markers(fs, corrected, contested))
        dropped = items[MAX_PER_SECTION:]
        if dropped:
            out.extend(_capped_index(dropped))
        out.append("")

    for key, title, _classes in SECTIONS:
        emit(title, grouped.get(key, []))

    emit(
        "Capabilities established in earlier sessions",
        capabilities,
        "These are things that WORK and were once lost. Do not ask the reviewer to re-supply "
        "them.",
    )

    if unrouted:
        emit(
            "Unrouted — no section assigned",
            unrouted,
            "> These findings' `class_instance_of` values are missing from the routing table "
            "in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches "
            "the agent at the moment it applies.",
        )

    out.append("")
    out.append(FOOTER)
    return "\n".join(out)


APPENDIX_HEADER = """\
# Known Failure Modes — Appendix

**GENERATED FILE — do not hand-edit.** Written by
`python3 scripts/generate-known-failure-modes.py` alongside `logs/known-failure-modes.md`.

Source: `logs/improvement-log.jsonl` ({n_entries} entries)
Generated: {generated}

## What this file is, and who reads it

`logs/known-failure-modes.md` is the page `build-agent` and `pipeline-agent` read at activation
step 0, so it is capped: at most {cap} lessons per section, and at most {maxids} finding ids per
table cell. **This file is where everything those two limits exclude actually lives.**

Nobody loads it on activation. Read it when the digest points you here — a capped-section note, or
a `(+N earlier — see appendix)` in a table cell — or when you want the full history of one class.

A capped lesson is not a less important lesson. The cap keeps the digest affordable to read on
every dispatch; it is not a judgement that what it hides is settled.
"""


def render_appendix(rows: list[dict], generated: str) -> str:
    """Every lesson the digest's caps hide, in full, plus every id its tables truncate.

    This is what makes the digest's caps a RELOCATION rather than a loss (improvement review 10,
    the WS-B capability design). `_capped_index()` in the digest names WHAT KIND of lesson is
    hidden and its ids; this file carries the lesson TEXT, which is the part an agent actually
    needs when the index tells it something relevant is missing.
    """
    def sort_key(item: tuple[str, list[dict]]) -> tuple[int, int, int, int]:
        _lesson, fs = item
        blockers = sum(1 for f in fs if f.get("severity") == "blocker")
        unfixed = 0 if any(f.get("status") == "NEW" for f in fs) else 1
        return (-len(fs), -blockers, unfixed, -id_number(fs[0]["id"]))

    grouped, capabilities, unrouted = group_lessons(rows)
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    # Same two maps render() builds. Computed here so BOTH renderers emit the correction and
    # contest markers through correction_markers() — the appendix carried none before (IMP-0565).
    corrected = corrections_of(rows)
    contested = contests_of(rows)

    out = [APPENDIX_HEADER.format(n_entries=len(rows), generated=generated,
                                  cap=MAX_PER_SECTION, maxids=MAX_IDS_PER_ROW)]

    # ── Part 1: the full id list behind every truncated table cell ───────────────────────────
    by_class: dict[str, list[dict]] = defaultdict(list)
    for r in live:
        by_class[canonical_class(r.get("class_instance_of", "unclassified"))].append(r)
    truncated = {c: fs for c, fs in by_class.items() if len(fs) > MAX_IDS_PER_ROW}
    if truncated:
        out.append("\n## Full finding ids, for every class the digest truncates\n")
        out.append(
            f"The digest shows the {MAX_IDS_PER_ROW} most recent ids per class. These are all of "
            f"them, oldest first.\n"
        )
        for cls, fs in sorted(truncated.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            ids = ", ".join(sorted({f["id"] for f in fs}, key=id_number))
            out.append(f"- **`{cls}`** (×{len(fs)}): {ids}")
        out.append("")

    # ── Part 2: every capped lesson, in full ────────────────────────────────────────────────
    def emit(title: str, items: list[tuple[str, list[dict]]]) -> None:
        dropped = sorted(items, key=sort_key)[MAX_PER_SECTION:]
        if not dropped:
            return
        out.append(f"\n## {title} — capped lessons\n")
        out.append(
            f"*{len(dropped)} lesson(s) the digest does not render, in the same order it "
            f"ranked them.*\n"
        )
        for lesson, fs in dropped:
            ids = ", ".join(sorted(f["id"] for f in fs))
            recur = f" **x{len(fs)}**" if len(fs) > 1 else ""
            cls = canonical_class(fs[0].get("class_instance_of", "unclassified"))
            out.append(f"- {lesson}{recur}  \n  <sub>{ids} · `{cls}`</sub>")
            # The appendix is where a capped lesson actually lives, so a lesson a later finding
            # disproved needs its warning HERE most of all — this is the file the digest sends
            # readers to (IMP-0565).
            out.extend(correction_markers(fs, corrected, contested))
        out.append("")

    for key, title, _classes in SECTIONS:
        emit(title, grouped.get(key, []))
    emit("Capabilities established in earlier sessions", capabilities)
    emit("Unrouted — no section assigned", unrouted)

    # ── Part 3: every RENDERED lesson the digest truncated, in full ──────────────────────────
    #
    # Part 2 carries the lessons the per-section cap EXCLUDED. A lesson inside the cap but over
    # LESSON_BUDGET is a different population: the digest renders it, cuts it at a sentence
    # boundary, and tells the reader the rest is here. Without this part that sentence is false —
    # the digest would be pointing at a page that does not hold what it promised, which is the
    # exact failure this file's own header warns about. The two populations do not overlap:
    # Part 2 is `[MAX_PER_SECTION:]`, this is the truncated members of `[:MAX_PER_SECTION]`.
    def truncated_in(items: list[tuple[str, list[dict]]]) -> list[tuple[str, list[dict]]]:
        return [(lesson, fs) for lesson, fs in sorted(items, key=sort_key)[:MAX_PER_SECTION]
                if budget_lesson(lesson)[1]]

    all_truncated: list[tuple[str, list[dict]]] = []
    for key, _title, _classes in SECTIONS:
        all_truncated += truncated_in(grouped.get(key, []))
    all_truncated += truncated_in(capabilities)
    all_truncated += truncated_in(unrouted)

    if all_truncated:
        out.append(f"\n## Rendered lessons the digest truncated, in full\n")
        out.append(
            f"*{len(all_truncated)} lesson(s) the digest shows in shortened form. Each is cut at a "
            f"sentence boundary once it exceeds {LESSON_BUDGET} characters and marked `[…]` there; "
            f"this is the complete text.*\n"
        )
        seen: set[str] = set()
        for lesson, fs in all_truncated:
            ids = ", ".join(sorted(f["id"] for f in fs))
            if ids in seen:
                continue
            seen.add(ids)
            cls = canonical_class(fs[0].get("class_instance_of", "unclassified"))
            out.append(f"- {lesson}  \n  <sub>{ids} · `{cls}`</sub>")
            out.extend(correction_markers(fs, corrected, contested))
        out.append("")

    out.append("")
    out.append(
        "---\n\nEvery entry in full, including the ones with no lesson text: "
        "`logs/improvement-log.jsonl`. Search across both files with "
        "`python3 scripts/generate-known-failure-modes.py --subject <term>`.\n"
    )
    return "\n".join(out)


def print_subject(rows: list[dict], term: str) -> int:
    """`--subject TERM`: every lesson matching TERM, RENDERED OR CAPPED (IMP-0383).

    The digest's per-section caps hid an entire delivery area. Grepping all 498 lines for CSS,
    theming, fonts, contrast, accessibility, npm, Vite, React or TypeScript returned ZERO
    rendered lessons on a project with a React front end — every one sat in the hidden remainder
    of several sections at once, named by id only, in sections that read as complete.

    This searches the LOG, not the digest, so a cap cannot hide anything from it. The lesson text
    and the class are printed in full; whether the digest happens to render that line is a
    separate question this deliberately does not ask, because the reader's question is "what does
    this project already know about X", not "which page is it on".
    """
    needle = term.lower()
    live = [r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")]
    matches = [r for r in live
               if needle in " ".join(str(r.get(k) or "") for k in
                                     ("lesson", "class_instance_of", "class", "what",
                                      "root_cause", "feature")).lower()]
    if not matches:
        print(f"known-failure-modes --subject {term!r}: NO lesson matches, across "
              f"{len(live)} live lesson-carrying entries. That is not evidence of safety — it "
              f"is evidence that nobody has been bitten by it here yet, or that this project "
              f"calls it something else. Try a narrower term.")
        return 0

    by_class: dict[str, list[dict]] = defaultdict(list)
    for row in matches:
        by_class[canonical_class(str(row.get("class_instance_of")
                                     or row.get("class") or "unclassified"))].append(row)

    print(f"known-failure-modes --subject {term!r}: {len(matches)} lesson-carrying entry(ies) "
          f"across {len(by_class)} class(es), searched in logs/improvement-log.jsonl so no "
          f"per-section cap can hide one.\n")
    for cls, entries in sorted(by_class.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"── {cls}  (×{len(entries)}) "
              f"{'─' * max(0, 74 - len(cls) - len(str(len(entries))))}")
        for row in sorted(entries, key=lambda r: r["id"]):
            print(f"  {row['id']}  [{row.get('severity', '?')}, "
                  f"observable_at {row.get('observable_at', '?')}, "
                  f"{row.get('status', '?')}]")
            for line in textwrap.wrap(str(row["lesson"]), width=94):
                print(f"      {line}")
        print()
    return 0


def print_routing(rows: list[dict]) -> int:
    """`--routing`: the per-class breakdown IMP-0198 asked for.

    The question this answers, which nothing answered before: *if I add this class to the
    routing table, what actually moves?* The honest answer is often "nothing", because the
    lessons are already placed by the capability flag.
    """
    routing = routing_of(rows)
    section_of = build_section_of()
    dupes = duplicated_classes()

    width = max((len(c) for c in routing), default=20)
    print(f"{'CLASS'.ljust(width)}  {'IN TABLE?':<10}  RENDERS IN")
    print(f"{'-' * width}  {'-' * 10}  {'-' * 40}")

    movable: list[str] = []
    for cls in sorted(routing, key=lambda c: (-sum(routing[c].values()), c)):
        breakdown = routing[cls]
        in_table = "yes" if cls in section_of else "NO"
        cells = ", ".join(f"{w}×{n}" for w, n in
                          sorted(breakdown.items(), key=lambda kv: (-kv[1], kv[0])))
        print(f"{cls.ljust(width)}  {in_table:<10}  {cells}")
        if breakdown.get(UNROUTED_SECTION):
            movable.append(f"{cls} ({breakdown[UNROUTED_SECTION]} lesson(s))")

    print()
    if movable:
        print("Adding these classes to SECTIONS would move a lesson out of Unrouted:")
        for m in sorted(movable):
            print(f"  - {m}")
    else:
        print("Every lesson is placed. Adding any class to SECTIONS would move nothing.")

    capability_only = [c for c, b in routing.items()
                       if CAPABILITY_SECTION in b and c not in section_of]
    if capability_only:
        print()
        print("These classes are NOT in the routing table and still render nowhere near "
              "Unrouted,")
        print("because the capability flag placed their lessons first — adding them to "
              "SECTIONS moves nothing:")
        for c in sorted(capability_only):
            print(f"  - {c} → {renders_in(routing[c]).replace('`', '')}")

    if dupes:
        print()
        print("Classes named in more than one section (the LAST one wins, silently):")
        for c, keys in sorted(dupes.items()):
            print(f"  - {c}: {', '.join(keys)}  → renders in {keys[-1]}")

    return 0


def selftest(rows: list[dict]) -> int:
    """Prove this generator CAN fail, then assert the size envelope WS-B asked for.

    Two different questions, and the second is the one this file exists to answer. A green
    `--selftest` that only proves the code runs is a can-it-fail proof and nothing more
    (`agents/improvement-agent.md`, "And run it against the REAL CORPUS before you wire it").
    """
    import copy
    import random

    failures: list[str] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(label)

    print("generate-known-failure-modes --selftest")
    print("\nA. Can it fail?")
    # A generator that cannot report a bad log is the gate-cannot-fail class (IMP-0369).
    bad = structural_errors([{"id": "IMP-0001"}], Path.cwd())
    check("a structurally invalid entry is reported", bool(bad),
          f"{len(bad)} error(s) raised" if bad else "NO error raised over a log with no lesson, "
                                                    "no status and no class")
    ranked = sorted(
        [("old", [{"id": "IMP-0001", "status": "APPLIED", "severity": "friction"}]),
         ("new", [{"id": "IMP-0999", "status": "NEW", "severity": "friction"}])],
        key=lambda it: (-len(it[1]),
                        -sum(1 for f in it[1] if f.get("severity") == "blocker"),
                        0 if any(f.get("status") == "NEW" for f in it[1]) else 1,
                        -id_number(it[1][0]["id"])),
    )
    check("sort_key ranks unfixed-and-newer above applied-and-older", ranked[0][0] == "new",
          f"order: {[k for k, _ in ranked]}")
    check("id_cell truncates and says how many it dropped",
          id_cell([f"IMP-{i:04d}" for i in range(1, 21)]).endswith("earlier — see appendix)"),
          id_cell([f"IMP-{i:04d}" for i in range(1, 21)]))

    print("\nB. Does the real corpus render, and is nothing lost?")
    digest = render(rows, "2026-01-01")
    appendix = render_appendix(rows, "2026-01-01")
    grouped, capabilities, unrouted = group_lessons(rows)
    sk = lambda it: (-len(it[1]),  # noqa: E731
                     -sum(1 for f in it[1] if f.get("severity") == "blocker"),
                     0 if any(f.get("status") == "NEW" for f in it[1]) else 1,
                     -id_number(it[1][0]["id"]))
    capped = []
    for items in list(grouped.values()) + [capabilities, unrouted]:
        capped += sorted(items, key=sk)[MAX_PER_SECTION:]
    missing = [fs[0]["id"] for lesson, fs in capped if lesson not in appendix]
    check("every capped lesson appears in the appendix", not missing,
          f"{len(capped)} capped, {len(missing)} missing" +
          (f": {missing[:5]}" if missing else ""))
    # The digest hides things; it must never hide that it is hiding them.
    check("the digest still names every capped lesson's class",
          capped == [] or "further lesson(s) in this section are not shown" in digest)

    # ── The per-lesson budget: it must cut, say so, and keep the full text reachable ─────────
    long_lesson = ("First sentence carries the rule. " * 4) + ("Second clause adds detail. " * 30)
    cut, was = budget_lesson(long_lesson, 600)
    check("a lesson over budget is truncated", was, f"{len(long_lesson)} -> {len(cut)} chars")
    check("truncation lands on a sentence boundary, never mid-clause",
          cut.rstrip().endswith("."), repr(cut[-40:]))
    check("a lesson under budget is untouched", budget_lesson("Short rule.", 600) == ("Short rule.", False))
    check("a budget of 0 disables truncation", budget_lesson(long_lesson, 0)[1] is False)
    # A single unbroken sentence longer than the budget is left WHOLE rather than severed:
    # cutting "never use PUT with a partial body" mid-clause inverts the instruction.
    check("a lesson with no sentence boundary in budget renders whole",
          budget_lesson("x" * 900, 600) == ("x" * 900, False))

    # The promise the digest prints is "full text in the appendix". Assert the promise is TRUE —
    # Part 2 of the appendix carries CAPPED lessons, and a truncated-but-rendered lesson is a
    # different population that would otherwise be promised and absent.
    truncated_ids = []
    for items in list(grouped.values()) + [capabilities, unrouted]:
        for lesson, fs in sorted(items, key=sk)[:MAX_PER_SECTION]:
            if budget_lesson(lesson)[1]:
                truncated_ids.append((lesson, fs[0]["id"]))
    absent = [i for lesson, i in truncated_ids if lesson not in appendix]
    check("every TRUNCATED lesson appears in the appendix in full", not absent,
          f"{len(truncated_ids)} truncated, {len(absent)} missing" +
          (f": {absent[:5]}" if absent else ""))
    check("the digest marks a truncated lesson visibly",
          not truncated_ids or "**[…]**" in digest)

    # ── Cross-renderer: an annotation must not exist in one renderer and not the other ───────
    #
    # THIS IS A COMPARISON BETWEEN THE TWO FILES, deliberately, and that is the whole point.
    # The pre-existing assertions all check a property INSIDE one renderer ("every capped lesson
    # appears in the appendix" is a presence check), and a marker implemented in render() and
    # missing from render_appendix() satisfies every one of them. Measured before the fix: 10
    # CORRECTED + 1 CONTESTED in the digest, 0 in the appendix, 10 marked lessons rendering only
    # in the appendix and therefore reading as authoritative (IMP-0565).
    corrected_map = corrections_of(rows)
    contested_map = contests_of(rows)
    flagged = set(corrected_map) | set(contested_map)
    unmarked: list[str] = []
    for items in list(grouped.values()) + [capabilities, unrouted]:
        for lesson, fs in sorted(items, key=sk):
            if not (flagged & {f["id"] for f in fs}):
                continue
            expected = correction_markers(fs, corrected_map, contested_map)
            if not expected:
                continue
            where = digest if lesson in digest else (appendix if lesson in appendix else "")
            if where and expected[0] not in where:
                unmarked.append(fs[0]["id"])
    check("every corrected/contested lesson carries its marker in whichever file renders it",
          not unmarked,
          f"{len(flagged)} flagged, {len(unmarked)} unmarked" +
          (f": {unmarked[:6]}" if unmarked else ""))

    print("\nC. Size envelope as the log grows (WS-B's stated verification)")
    # Synthetic entries are RESAMPLED from the real corpus, so lesson-length distribution matches
    # this project's actual writing rather than a fixture author's guess.
    pool = [r for r in rows if r.get("lesson")]
    random.seed(20260901)
    budget = {700: 145_000, 1000: 155_000, 1500: 175_000}
    grown = copy.deepcopy(rows)
    nxt = max(id_number(r.get("id", "")) for r in rows)
    for target in sorted(budget):
        while len(grown) < target:
            nxt += 1
            clone = copy.deepcopy(random.choice(pool))
            clone["id"] = f"IMP-{nxt:04d}"
            clone["lesson"] = f"{clone['lesson']} [synthetic {nxt}]"
            clone["status"] = "APPLIED"
            clone.pop("capability", None)
            grown.append(clone)
        size = len(render(grown, "2026-01-01").encode("utf-8"))
        check(f"at {target} log entries the digest stays under {budget[target]:,} bytes",
              size <= budget[target], f"{size:,} bytes")

    print(f"\n{'SELFTEST PASSED' if not failures else 'SELFTEST FAILED — ' + ', '.join(failures)}")
    return 0 if not failures else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--log", type=Path, default=LOG)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--appendix", type=Path, default=APPENDIX,
                   help="the on-demand companion file holding every capped lesson in full and "
                        "every truncated id list. Written and --check'd alongside --out")
    p.add_argument("--selftest", action="store_true",
                   help="prove this generator can fail, and assert the digest's size envelope "
                        "against synthetic logs at 700/1000/1500 entries, then exit")
    p.add_argument("--check", action="store_true", help="exit 1 if the written file is stale")
    p.add_argument("--stdout", action="store_true", help="print instead of writing")
    p.add_argument("--as-of", default=None, help="YYYY-MM-DD stamp (default: today)")
    p.add_argument("--routing", action="store_true",
                   help="print where every class's lessons render, and by which mechanism, "
                        "then exit. Answers 'will adding this class to the routing table "
                        "move anything?' without reading the generator (IMP-0198)")
    p.add_argument("--subject", metavar="TERM",
                   help="print every lesson matching TERM — RENDERED OR CAPPED — then exit. The "
                        "digest's per-section caps hide ~105 lessons behind an id list, and "
                        "before this flag existed the whole front-end subject area (CSS, "
                        "theming, contrast, npm, Vite, TypeScript) rendered nowhere at all "
                        "(IMP-0383)")
    args = p.parse_args(argv)

    try:
        rows = load(args.log)
    except (FileNotFoundError, ValueError) as exc:
        print(f"generate-known-failure-modes: {exc}", file=sys.stderr)
        return 2

    # The one command every agent IS instructed to run is now the authoritative one. See this
    # module's docstring; there is no flag to skip this (IMP-0369).
    bad = structural_errors(rows, args.log.resolve().parent.parent)
    if bad:
        print(f"generate-known-failure-modes: REFUSING — {args.log} has "
              f"{len(bad)} structural problem(s). The digest is not built or checked over a "
              f"malformed log, because an entry the validator rejects is an entry the next "
              f"agent cannot read back (IMP-0369).", file=sys.stderr)
        for err in bad:
            print(f"  ERROR: {err}", file=sys.stderr)
        print(f"\n  Fix the entries, then re-run. Allocate any replacement id with:\n"
              f"    python3 scripts/allocate-improvement-id.py\n"
              f"  Full check (triggers, citations, corrections too):\n"
              f"    python3 scripts/verify-improvement-log.py", file=sys.stderr)
        return 2

    if args.selftest:
        return selftest(rows)

    if args.routing:
        return print_routing(rows)

    if args.subject:
        return print_subject(rows, args.subject)

    # --check must not depend on the date, or the file would be "stale" every midnight.
    # It compares everything except the Generated: line.
    stamp = args.as_of or _dt.date.today().isoformat()
    text = render(rows, stamp)
    appendix_text = render_appendix(rows, stamp)

    if args.stdout:
        print(text)
        return 0

    if args.check:
        def strip_stamp(s: str) -> str:
            return "\n".join(l for l in s.splitlines() if not l.startswith("Generated:"))

        # BOTH files are checked. The appendix carries the lesson text the digest's caps hide, so
        # a stale appendix is the digest pointing at a page that no longer holds what it promised
        # — the same "a lesson that never reaches the reader teaches nobody" failure, one level
        # further along the read path.
        for path, expected, what in ((args.out, text, "digest"),
                                     (args.appendix, appendix_text, "appendix")):
            if not path.exists():
                print(f"generate-known-failure-modes: {path} does not exist — run without "
                      f"--check to create it", file=sys.stderr)
                return 1
            if strip_stamp(path.read_text(encoding="utf-8")) != strip_stamp(expected):
                print(
                    f"generate-known-failure-modes: {path} ({what}) is STALE relative to "
                    f"{args.log}.\n"
                    f"  Run: python3 scripts/generate-known-failure-modes.py\n"
                    f"  A log entry that never reaches the digest teaches nobody.",
                    file=sys.stderr,
                )
                return 1
        print(f"generate-known-failure-modes: {args.out} and {args.appendix} are current "
              f"({len(rows)} entries).")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    args.appendix.parent.mkdir(parents=True, exist_ok=True)
    args.appendix.write_text(appendix_text, encoding="utf-8")
    # Derived from the SAME `live` set the digest header uses (render(), and lesson_sections()
    # above it): NEW or APPLIED, with a lesson. A REJECTED finding must stop teaching, so it is
    # excluded from the digest — and this line used to count every row instead, which made stdout
    # say "330 distinct lessons" while the file it had just written said 329.
    #
    # That one-line gap is not staleness and not a concurrent session, and IMP-0334 exists because
    # improvement review 29 spent a paragraph of analysis on it before finding the cause: the
    # log's single REJECTED entry, IMP-0290, whose lesson text is unique. Two figures labelled the
    # same thing, counting different populations. Now they read from one set and the difference is
    # LABELLED rather than left for the next reader to re-derive.
    live_lessons = {r["lesson"] for r in rows
                    if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")}
    rejected = len([r for r in rows if r.get("status") == "REJECTED" and r.get("lesson")])
    excluded = f" ({rejected} rejected, excluded)" if rejected else ""
    print(
        f"generate-known-failure-modes: wrote {args.out} — {len(rows)} entries, "
        f"{len(live_lessons)} distinct teaching lessons{excluded}, "
        f"{len(text.splitlines())} lines."
    )
    print(
        f"generate-known-failure-modes: wrote {args.appendix} — "
        f"{len(appendix_text.splitlines())} lines (capped lessons in full; not read on "
        f"activation)."
    )
    # The digest's SIZE is what every activation of six agents pays, and until now nothing
    # reported it — so the growth that motivated the per-lesson budget was invisible between
    # reviews. Print it, and print what the budget is currently saving, so a future reader can
    # see the trend without re-deriving it (improvement review 7).
    global LESSON_BUDGET
    n_truncated = text.count("**[…]**")
    size = len(text.encode("utf-8"))
    _kept, LESSON_BUDGET = LESSON_BUDGET, 0
    try:
        unbudgeted = len(render(rows, stamp).encode("utf-8"))
    finally:
        LESSON_BUDGET = _kept
    print(f"generate-known-failure-modes: digest is {size:,} bytes — "
          f"{unbudgeted - size:,} fewer than unbudgeted, from a {LESSON_BUDGET}-char per-lesson "
          f"budget truncating {n_truncated} lesson(s) into the appendix. Read at activation by "
          f"build-agent, pipeline-agent, pm-agent, acceptance-agent, commercial-agent and "
          f"test-agent.")
    # IMP-0545: an aggregation key that never aggregates is invisible — it emits valid output and
    # the only symptom is that the collapsed form never appears. Printing the merge count is what
    # makes "this key has gone inert" a thing you can see rather than a thing you must measure.
    n_live = len([r for r in rows if r.get("status") in {"NEW", "APPLIED"} and r.get("lesson")])
    merged = n_live - len(live_lessons)
    print(
        f"generate-known-failure-modes: lesson-text deduplication merged {merged} finding(s) "
        f"({n_live} findings → {len(live_lessons)} lesson groups)."
        + ("  Merging 0 means the `x{n}` recurrence marker cannot fire; the class-level "
           "Recurring-classes table is the only working aggregation (IMP-0545)."
           if merged == 0 else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
