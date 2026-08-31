# Improvement Review 41 — 2026-08-29

**Status:** APPLIED 2026-08-29 under `APPROVE IMPROVEMENTS`. All four changes are on disk; §9
records what landed, what was measured at apply time, and the one entry left deliberately open.
**Findings processed:** 1 `NEW` → 1 cluster
**Scope:** [`IMP-0484`](../../logs/improvement-log.jsonl) only — the single `blocker` that summoned
this dispatch immediately per [`WORKFLOW.md` L89](../../agents/WORKFLOW.md#L89)'s processing
trigger. The gate reports **7 unread** entries; the other six are `rework`/`friction` and are left
alone per [`improvement-agent.md` L87](../../agents/improvement-agent.md#L87) — *one unread blocker
must not pull a review of everything around it*. They are named in §5.
**WBS:** `wbs:6.9`. The finding carries `commercial_impact: none` — DEV only, no billed hours
claimed against unverified work.

---

## Summary

**Log absence is not write absence, and the fix is one word wider than the finding asked for.**
[`IMP-0484`](../../logs/improvement-log.jsonl) proposes that
[`WORKFLOW.md` L89](../../agents/WORKFLOW.md#L89)'s fourth case be strengthened to require a live
spot-check. Reading the rule as it actually stands narrows that: rule 1 at
[`WORKFLOW.md` L110](../../agents/WORKFLOW.md#L110) **already** requires direct verification — it
just names only file-shaped evidence (*"its mtime and its content"*), and lead-agent's 09:00 line
checked exactly that and nothing else. So this is not a missing rule; it is a rule whose evidence
vocabulary has no entry for a dispatch whose artefact is a live environment.

The second half is the more durable one, and it is a **generalisation, not a new idea**:
[`pipeline-agent.md` L441](../../agents/pipeline-agent.md#L441) logs once per *stage*, so a death
between the first write and the end of the stage leaves durable changes on disk and nothing
recording them. That is the same property [`IMP-0301`](../../logs/improvement-log.jsonl) and
[`IMP-0333`](../../logs/improvement-log.jsonl) already forced into
[`improvement-agent.md` L239](../../agents/improvement-agent.md#L239) as *"do the bookkeeping
INCREMENTALLY"*. Second agent, same property — the altitude rule at
[`how-to-promote-a-finding.md` L44](../../skills/how-to-promote-a-finding.md#L44) forbids another
lone instance patch, so the property goes into
[`C-TECH-065`](../../constraints/technology/technology-constraints.md#L135), which already governs
these markers and already reaches four agents.

**One design was cut by measurement.** The obvious shape — reuse `WRITE ATTEMPTED:` with a
`STARTED` outcome — turns the HARD gate **red on the well-formed case**, measured, not reasoned.
§6 has the run.

---

## 1. Regression check — did review 40's changes work?

Review 40 applied 13 changes on 2026-08-28. Six unread entries have been logged since, which is
enough to audit four of them.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| Change 6 — usage-error docstring across [`verify-code-app-column-bindings.py` L234](../../scripts/verify-code-app-column-bindings.py#L234) + 6 siblings | `gate-invocation-omits-required-arg` | **YES — [`IMP-0479`](../../logs/improvement-log.jsonl)** | **Wrong altitude.** See below |
| Change 12 — the `contests` edge in [`verify-improvement-log.py` L405](../../scripts/verify-improvement-log.py#L405) | `gate-reassures-wrongly` | **YES — [`IMP-0478`](../../logs/improvement-log.jsonl)** | **Predicted by review 40's own §7 and it happened anyway** |
| Change 13 — check 7's suppressed-exception count in [`verify-flow-definition-language.py` L574](../../scripts/verify-flow-definition-language.py#L574) | `gate-reassures-wrongly` | **YES — [`IMP-0483`](../../logs/improvement-log.jsonl)** | **Working mechanically, and the number it now prints reads as reassurance** |
| Changes 7 + 8 — the `Deferred:` line, [`verify-improvement-log.py` L252](../../scripts/verify-improvement-log.py#L252) + [`improvement-review-template.md` L106](../../templates/improvement-review-template.md#L106) | `gate-fires-on-nothing` | **NO** | **Working.** This document uses the field in §5 and the gate reads it |
| Changes 1–5, 9–11 | various | No evidence either way | Nothing in this batch touches them |

The four audit questions, for the recurrence that matters to *this* review:

- **Change 6 — was it prose or a gate?** A gate change, applied to **seven named scripts**.
  **Did it run?** Yes, and it works in all seven. **So what recurred?**
  [`IMP-0479`](../../logs/improvement-log.jsonl) is the same class in an **eighth** place the
  enumeration did not reach — an agent file, [`build-agent.md`](../../agents/build-agent.md),
  quoting a gate invocation with a required flag missing. Fixing seven call sites by name is an
  instance patch wearing a gate's clothes: the property is *"every quoted invocation of a gate is
  complete"*, and nothing checks the quoted invocations that live in `agents/` prose. **This is the
  same defect shape as the one this review is processing** — an enumeration that names the media it
  happens to know about. I am flagging it, not fixing it: `IMP-0479` is unread, `friction`, and
  outside this single-finding dispatch (§5).
- **Did closure evidence match the level each defect was visible at?** For change 6, yes — a usage
  error is V1 and was re-run. That is precisely why the recurrence is about *scope*, not proof.

---

## 2. Clusters and promotion decisions

```
CLUSTER: stage-level-logging-hides-mid-stage-writes  (x1: IMP-0484)
         — but see Altitude: this is x3 of a property already patched twice elsewhere

Altitude:   CLASS — and the class is NOT the one the finding named.
            IMP-0484's own class has one member. Its PROPERTY — "a durable external change
            landed and nothing records it, because the record is batched to the end" — has
            three: IMP-0301 (improvement-agent, 6 of 12 changes on disk, log said none),
            IMP-0333 (improvement-agent, amended document, false completion note), and
            IMP-0484 (pipeline-agent, 4 live DEV writes, zero pipeline.log trace).
            The first two were patched in improvement-agent.md L239 ONLY. Under
            how-to-promote-a-finding.md L44, the third may not get a second lone instance
            patch — it must be generalised.

Ladder row: TWO rows fire, and they are different halves of the defect.
            · "The ORDER of steps was wrong" -> the write-then-log order in
              pipeline-agent.md L441 is what makes a mid-stage death unrecordable.
            · "An agent had the information and still did the wrong thing" -> lead-agent
              had WORKFLOW.md L110 and applied it correctly to file-shaped artefacts; the
              rule's evidence vocabulary is what was incomplete, not the agent's reading.

Becomes:    1. WORKFLOW.md L110 — rule 1's evidence vocabulary gains the non-file medium,
               keyed on WHAT THE DISPATCH WRITES TO. Borrows the fifth case's own already-
               correct wording at L151 ("Verify live state directly") rather than inventing
               a concept: the fourth case is brought up to the fifth's standard.
            2. pipeline-agent.md L441 + L191 — one record per OPERATION, appended BEFORE the
               write (WRITE BEGUN:) and completed after (the existing WRITE ATTEMPTED:
               outcome line). Never batched to end-of-stage.
            3. verify-provisioning-report.py — learns the WRITE BEGUN: marker, so the
               convention in (2) does not create a new blind spot. Measured, §6.
            4. C-TECH-065 — the constraint amendment that carries the property to the four
               agents its Applies To column already names. This is the generalisation
               vehicle; WORKFLOW.md cannot be, because CLAUDE.md declares it lead-agent-only,
               so a rule placed there would be unread by every agent that must obey it.

Retires:    nothing — see §4. No instance gate exists for this property to replace.

Cites:      IMP-0484 (the finding), IMP-0301 + IMP-0333 (the property's prior instances),
            IMP-0291 + IMP-0357 (the fourth and fifth cases this edits), IMP-0252 (the
            report-back markers being extended), IMP-0172 (the death class itself)

Residual:   FOUR things, and the first is the one to read.

            (a) NONE of this could have detected the 2026-08-28 instance. That dispatch
                left no log line at all, so there is nothing in the corpus for change 3 to
                find — it is load-bearing only FORWARD, from the first dispatch that emits
                the marker. Stated plainly because a gate reporting 0 findings against its
                corpus is normally the tell (improvement-agent.md L410); here the absence
                IS the defect, and I am not recording it as a clean run.

            (b) A dispatch can still die BEFORE its first WRITE BEGUN: append. The window
                shrinks from "a whole stage" to "one operation" and does not close. Nothing
                closes it — the record and the write cannot be made atomic across a process
                death — which is exactly why change 1 (the reader-side live spot-check) is
                not optional and not replaced by change 2.

            (c) Change 1 is PROSE and will stay prose. WORKFLOW.md L123 already records
                why the mechanical half was declined — 99 ROUTED_TO lines against 9
                GATE_RECEIVED, ~90 false positives on history — and IMP-0319 measured a
                plausible FIFO pairing of dispatches to terminal lines reporting ZERO
                unreconciled dispatches while HIDING the one real stall. I am not
                re-proposing that gate. It remains a forward-from-a-cutoff convention
                decision for the reviewer, not a defect fix.

            (d) The live spot-check itself needs credentials. improvement-agent.md L359
                forbids me authoring an executable that authenticates to a live environment
                — that is delivery work. Change 1 therefore names the OBLIGATION and points
                at scripts that already exist (ensure-schema.ps1 -Env <env> reports
                EXISTS/CREATED per component and is idempotent, which is what made the
                2026-08-29 discovery possible at all). It does not add a new one.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | agent | [`WORKFLOW.md` L110](../../agents/WORKFLOW.md#L110) | Fourth-case rule 1's evidence vocabulary is keyed on **the medium the dispatch writes to**, not on files. A pipeline-agent dispatch's artefact is the **live environment**; mtime, log content and marker absence are evidence about the repository and say nothing about DEV. Carries the 2026-08-29 instance as its worked example | IMP-0484, IMP-0291, IMP-0357 | N/A — instruction change |
| 2 | agent | [`pipeline-agent.md` L441](../../agents/pipeline-agent.md#L441) and [L191](../../agents/pipeline-agent.md#L191) | Logging becomes **one record per live operation, not one per stage**: append `WRITE BEGUN: <script> -Env <env>` immediately *before* each live write, and the existing `WRITE ATTEMPTED:` outcome line immediately *after*. A mid-stage death then leaves a dangling `WRITE BEGUN:` — partial evidence instead of none | IMP-0484, IMP-0301, IMP-0333 | YES — `python3 scripts/verify-provisioning-report.py --check` |
| 3 | script | [`verify-provisioning-report.py` L50](../../scripts/verify-provisioning-report.py#L50) | Learns `WRITE BEGUN:`: (a) it counts as a provisioning write for the preflight-pairing rule, so a begun write with no `PREFLIGHT:` **fails** as an attempted one does; (b) it is an intent line, so `WRITE_OUTCOME` is **not** applied to it; (c) a `WRITE BEGUN:` with no matching outcome is **reported as a NOTE naming script and environment — never a failure**, because that dangling marker is the death signature this whole review exists to preserve | IMP-0484 | YES — `--selftest` plus `--check` over `logs/pipeline.log` |
| 4 | constraint-amendment | [`C-TECH-065`](../../constraints/technology/technology-constraints.md#L135) | Fourth rung, in the row that already owns these markers and already names `pipeline-agent, development-agent, build-agent, test-agent`: **the record of a live write is written per operation, not per stage** — a report-back batched to the end of a stage is a report that a terminated session never files. `Verify By` gains change 3's two commands | IMP-0484, IMP-0301, IMP-0333, IMP-0252 | YES — the two commands in change 3 |

**Constraint budget:** **0 of 3 used.** Change 4 is an amendment to an existing row, not a new one.
`C-TECH-065` already carries a *"Third rung, added 2026-08-22"* and an *"EXTENDED 2026-08-24"* — a
fourth rung on the row that owns the markers is cheaper than a new row that would have to
cross-reference it, and it inherits the existing `Applies To` reach that makes this a
generalisation rather than a fifth instance patch.

Change 1 is the only one that is not mechanically verifiable, and it is deliberately prose — see
§2 `Residual (c)` for the measurement that declined its gate.

---

## 4. Retirements

> Retirement check performed: the 4 constraints in this review's blast radius were reviewed
> (`C-TECH-064`, `C-TECH-065`, `C-TECH-066`, and the already-retired `C-TECH-031` that names
> `C-TECH-065` as its successor), and **none is currently redundant**, because this review
> *widens* the only row that overlaps rather than replacing it. Nothing is superseded, so retiring
> anything here would lose coverage rather than consolidate it.

Derived, not typed: **10** retired rows
(`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), unchanged by this review, and
matching the figure registered in
[`derived-counts-registry.json`](../../scripts/derived-counts-registry.json) — no drift.

**One candidate is named for a future review, not this one.** Change 2's per-operation rule makes
[`pipeline-agent.md` L441](../../agents/pipeline-agent.md#L441)'s stage-level line a *summary*
rather than the sole record. If a later review generalises per-operation logging to `build-agent`
and `commercial-agent` as well, the three agents' separate Logging sections become the instance
patches this review was careful not to add a fourth of — and *that* is the moment to consolidate
them into one rule with one home.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0478, IMP-0479, IMP-0480, IMP-0481, IMP-0482, IMP-0483

Six of the seven unread entries. This was a **single-finding blocker dispatch**, and
[`improvement-agent.md` L87](../../agents/improvement-agent.md#L87) is explicit that an unread
blocker must not pull a review of everything around it. All six are `rework` or `friction`; none
fires a trigger on its own. The 86 `reviewer-deferred` entries are untouched and unread by this
review.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [`IMP-0478`](../../logs/improvement-log.jsonl) | `gate-reassures-wrongly` | Review 40's §7 already put this to the reviewer as a schema question; it is a live open decision, not a fresh finding | the reviewer answers review 40 §7 |
| [`IMP-0479`](../../logs/improvement-log.jsonl) | `gate-invocation-omits-required-arg` | **Second instance — audited in §1 and it needs generalising, not another named-file patch.** Out of this dispatch's scope | the next batch review, or a third instance |
| [`IMP-0480`](../../logs/improvement-log.jsonl) | `declared-policy-not-mechanically-enforced` | Delivery finding on ADR-039's k=5 threshold; needs the TAD, not the rules | the next batch review |
| [`IMP-0481`](../../logs/improvement-log.jsonl) | `approved-document-internally-inconsistent` | Same class as `IMP-0482`; the two are one cluster and should be processed together | the next batch review |
| [`IMP-0482`](../../logs/improvement-log.jsonl) | `approved-document-internally-inconsistent` | See above | the next batch review |
| [`IMP-0483`](../../logs/improvement-log.jsonl) | `gate-reassures-wrongly` | Audited in §1 as a recurrence against review 40's change 13; the fix is a wording call on that gate's output | the next batch review |

**`IMP-0484` is NOT on the deferred line, and it is also NOT being closed.** It is *processed* —
all four changes cite it — but its `observable_at` is **V3**, and the reproduction step is *a
pipeline-agent dispatch dying mid-stage after live writes*. I cannot stage that, and
[`improvement-agent.md` L263](../../agents/improvement-agent.md#L263) is unambiguous that a V2+
entry is not closed by a document saying it was fixed. So on approval it takes `reviewed_in`, a
`deferred_reason` recording what landed, and a `revisit_when` naming the observation that would
close it: **the next `pipeline-agent` dispatch that performs a live write emits per-operation
`WRITE BEGUN:` markers, and `logs/pipeline.log` shows them.** That is cheap, it happens on the very
next deploy, and it moves the entry to `reviewer-deferred` — which clears the blocker trigger
honestly rather than by a closure nobody tested (`IMP-0208`, `IMP-0224`, `IMP-0225`).

---

## 6. Measurement — the design the corpus cut

**The obvious design fails, and only running it says so.** The natural way to express "a write
started" is to reuse the existing marker with a new outcome token. Run against the live gate:

| Fixture | Shape | Result |
|---|---|---|
| A | `WRITE ATTEMPTED: … — STARTED`, dangling | **FAILED** — *"states no outcome … must carry SUCCEEDED, FAILED or REFUSED"* |
| B | `WRITE ATTEMPTED: … — STARTED` **then** `— SUCCEEDED` | **FAILED** — the well-formed case is red too |
| C | `WRITE BEGUN: …` then `WRITE ATTEMPTED: … — SUCCEEDED` | PASS — *"1 entry judged (1 with a provisioning write)"* |
| D | `WRITE BEGUN: …` dangling — **the death signature** | PASS — *"1 entry judged (**0 with a provisioning write**)"* |

Fixture B is the finding: [`WRITE_OUTCOME` at L55](../../scripts/verify-provisioning-report.py#L55)
is `\b(SUCCEEDED|FAILED|REFUSED)\b` and is applied to every `WRITE ATTEMPTED:` body, so an intent
line sharing that keyword is red **whether or not the operation completed**. A convention that
turns a HARD gate red on its own correct use is a convention every agent learns to route around.
Hence the distinct `WRITE BEGUN:` keyword in changes 2 and 3.

**Fixture D is why change 3 exists rather than being skipped as cosmetic.** `WRITE BEGUN:` is inert
in the gate as it stands, so adopting the convention *without* change 3 would have the gate print
**"0 with a provisioning write"** over a log that plainly records a write beginning — a new
`gate-reassures-wrongly` surface (×25 in this repo) manufactured by this very review. Change 3
pre-empts it.

**Corpus run, before any change:** `--check` PASSES over `logs/pipeline.log` — *11 entries judged
(1 with a provisioning write, all carrying a preflight result); 21 predate the 2026-08-24
convention*. `--selftest` PASSES, 5 fixtures. Change 3 alters **no verdict on any of the 32
entries**, because no entry uses the new marker yet. Per §2 `Residual (a)` that is the honest
reading and not a clean-run claim.

**Two claims of the finding, executed rather than read** — per
[`improvement-agent.md` L136](../../agents/improvement-agent.md#L136):

- *"`verify-provisioning-report.py` … does not and cannot check the inverse"* — **confirmed.** The
  gate reads only the log; run above.
- *"`logs/pipeline.log` has zero entries between 2026-08-27 21:01 and this dispatch's own first
  write"* — **confirmed.** [L31](../../logs/pipeline.log#L31) is `2026-08-27 21:01`;
  [L32](../../logs/pipeline.log#L32) is the fresh dispatch. Nothing between.

### One correction to the finding's own diagnosis

[`IMP-0484`](../../logs/improvement-log.jsonl)'s `expected` clause states that the fourth case
*"treats an absent pipeline.log entry … as sufficient evidence that 'nothing happened'"*. **It does
not.** [`WORKFLOW.md` L110](../../agents/WORKFLOW.md#L110) already says *"Verify the target artefact
directly — its mtime and its content — for a partial write, before assuming nothing happened."*
Lead-agent obeyed that rule; [`routing.log` L380](../../logs/routing.log#L380) shows it checking
log content, deployment-summary mtime, marker absence and `ListAgents` — four checks, every one of
them about a **file or a session**, not one about DEV.

The finding's `lesson` field is correct and its remedy is correct; only its characterisation of the
rule is imprecise, and the difference is load-bearing: it makes change 1 a **vocabulary widening of
an existing rule** rather than a new rule bolted alongside it. On approval this is recorded as a
`corrects` edge on a new entry, class `finding-diagnosis-unverified` (×14 → ×15) — the mechanism
review 39 built for exactly this. **The id is allocated with
`python3 scripts/allocate-improvement-id.py` at append time, not now**: two peer sessions were live
on this repo yesterday and an id read minutes early is a duplicate (`IMP-0312`, `IMP-0080`).

### Out of scope, reported not fixed

`python3 scripts/verify-derived-counts.py` is **red (SOFT)** on 3 claims — two secured-column
counts in [`dev-summary`](../../docs/development/revitalise-grant-automation-dev-summary.md) (67 vs
source 68) and one in [`REV Trustee.xml` L73](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L73)
(51 vs 52). All three are the `rev_ethnicgroup` column landing after the prose was written. Not
mine and not this review's WBS scope (`C-COM-002`); flagged so it is not mistaken for something
this review introduced. My own two registered claims — verify-script count **51** and retired
constraints **10** — are current.

Separately, and smaller: **three line-links inherited from review 40's change table had already
drifted** and were re-grepped for §1 (`verify-improvement-log.py` L388 now lands on a JSON error
handler, L1281 inside a docstring, `verify-code-app-column-bindings.py` L232 on a blank line).
`verify-doc-line-links.py` reports `OK — 0 line-link(s)` on this document because `docs/improvements`
is one of the three directories it explicitly does not cover — *"historical reviews nobody owns."*
That exclusion is deliberate and I am not proposing to change it; noted only so the `OK` above is
not read as these links having been machine-checked. They were grepped by hand.

`verify-review-document.py` over the whole directory is **red on 4 pre-existing findings** in
`2026-08-22-improvement-review.md` (3 × `CLUSTER-COUNT`) and `2026-08-25-improvement-review.md`
(1 × `LOST-DEFERRAL`) — historical reviews, untouched by this one. **This document passes clean**
(`--only`, quoted in the gate output below). Recorded so the directory-level red is not attributed
to this review.

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 481 | 482 |
| Distinct lessons | 480 | 481 |
| Recurring classes (x≥2) | 39 | 39 |
| Digest lines | 583 | measured at apply time — not predicted |

`IMP-0484` is already rendered (the generator reads lessons regardless of status), so the delta
comes entirely from the one `corrects` entry in §6, whose class is already `x14`. **The line count
is deliberately left unpredicted:** a review that predicted 31→26 and measured 31→30 is
[`IMP-0198`](../../logs/known-failure-modes.md#L28), and the digest's own routing table warns that
a class's lessons do not necessarily render in the section its name suggests.

Regenerated with `python3 scripts/generate-known-failure-modes.py`, confirmed current with
`--check`, and validated **first** with `python3 scripts/verify-improvement-log.py` — validator
before generator, per `CLAUDE.md`'s learning rules (`IMP-0369`: regenerating is not validating).

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-29-improvement-review.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   13 prior changes audited, 3 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 1 gates/scripts,
                    0 skill/knowledge edits, 2 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 481 lessons, 39 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — 2026-08-29

**All four changes landed as approved. Nothing was withheld, and nothing was narrowed.** The
re-verification required before applying re-ran every executable claim rather than re-reading it,
and each measurement below is a run.

| # | Change | State | Measured at apply time |
|---|---|---|---|
| 1 | [`WORKFLOW.md`](../../agents/WORKFLOW.md#L110) fourth case, rule 1 | **APPLIED** as approved | N/A — instruction change. Confirmed before editing that rule 1 did already require direct verification, which is what makes this a vocabulary widening; that correction is `IMP-0490` |
| 2 | [`pipeline-agent.md`](../../agents/pipeline-agent.md#L191) report-back block + Logging | **APPLIED** as approved | N/A — instruction change |
| 3 | [`verify-provisioning-report.py`](../../scripts/verify-provisioning-report.py#L96) learns `WRITE BEGUN:` | **APPLIED** as approved | `--selftest` **PASS, 8 fixtures** (up from 5; the three new ones are begun-then-settled passes clean, dangling begun is a NOTE not a failure, begun with no preflight fails). `--check` over `logs/pipeline.log` **PASS — 11 entries judged, 1 with a provisioning write, 21 predate the convention** |
| 4 | [`C-TECH-065`](../../constraints/technology/technology-constraints.md#L135) fourth rung | **APPLIED** as approved | Verified by change 3's two commands, both exit 0 |

**Change 3 altered no verdict on any existing entry, and that is recorded as the honest reading
rather than as a clean run.** No entry in the corpus carries the new marker yet, so the gate is
load-bearing only forward, from the first dispatch that emits one. §2 `Residual (a)` predicted
exactly this and the measurement confirms it: 11 judged, 1 with a write, 21 skipped — identical to
the pre-change run.

**One entry appended, one entry left open.**

- **[`IMP-0490`](../../logs/improvement-log.jsonl) — appended and closed.** The `corrects` edge on
  `IMP-0484`'s diagnosis that §6 promised, class `finding-diagnosis-unverified`. Its id was
  allocated from the log's current maximum immediately before appending, not read minutes earlier
  (`IMP-0312`, `IMP-0080`) — the max read `IMP-0489` at that moment, with zero duplicates.
- **[`IMP-0484`](../../logs/improvement-log.jsonl) — PROCESSED, NOT CLOSED, exactly as §5 said.**
  `observable_at` is V3 and the reproduction step is a `pipeline-agent` dispatch dying mid-stage
  after live writes, which no session can stage. It now carries `reviewed_in`, a `deferred_reason`
  recording all four changes and their measurements, and the approved `revisit_when` **verbatim**.
  It has moved from `unread` to a recorded deferral, which clears the blocker trigger honestly
  rather than by a closure nobody tested (`IMP-0208`, `IMP-0224`, `IMP-0225`).

**Queue effect.** `python3 scripts/verify-improvement-log.py --check` no longer names `IMP-0484` in
any trigger. Digest regenerated and confirmed current with `--check` — 487 entries, 486 distinct
lessons, 585 lines. The line count was measured after regenerating, never predicted (`IMP-0198`).
