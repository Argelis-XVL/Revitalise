# Improvement Review — 2026-09-23 (1)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 4 `NEW` → 4 clusters
**Trigger:** blocker escalation — two unread `blocker`-severity entries (IMP-0831, IMP-0835)
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This review processes the unread blocker it was dispatched for (IMP-0831), one unread
entry on the same feature whose property is the same one document upstream (IMP-0830), one finding
this review logged itself while measuring the blocker's root cause (IMP-0834), and **a second
unread blocker that was appended by another live session while this draft was being written**
(IMP-0835) — folded in rather than left, because an unread blocker keeps the queue gate red no
matter what this document concludes about the others. Everything else in the queue stays out of
scope: one unread blocker must not pull a review of everything around it (`IMP-0183`). §5 names
each excluded entry and the document it is waiting on.

---

## 0. What the reviewer needs to know first

**The verification that caught this worked exactly as designed, and it cost nothing to run.** The
architecture document flagged its own ONS query shape as unconfirmed (`A-LAR-01`), and scheduled
the check for `development-agent` *before* the flow's HTTP action was written. That check ran, and
found two of the three assumed field names do not exist. No build was halted and no live artefact
was wrong.

**What this review is about is the other half: the answer was already in this system's own log, a
week old, on the same endpoint.** A finding from 2026-09-17 had established that the ONS postcode
service returns codes rather than names. The architecture was written assuming a name field.

**And the measured reason it did not reach the author is not that nobody looked.** The lesson is in
the digest every agent reads. The digest renders the first 600 characters of a lesson and cuts the
rest into an appendix that no agent loads — grepped `agents/`, `skills/` and `CLAUDE.md` for
`known-failure-modes-appendix`, zero hits. The 2026-09-17 lesson put its concrete facts last, so
the half that was cut is exactly the half that would have prevented this. **68 of the 188 lessons
currently rendered in the digest are truncated the same way.** That is change 4 below, and it is
the one with reach beyond this feature.

**And the follow-up dispatch sent to fix the architecture stopped itself, correctly, for a
different reason.** It found the fix is not a swap of field names: there is no server-side grouping
on that layer at all, no aggregation mechanism anywhere in this project's established stack for a
1.8-million-row extract, and the name lookup needs a second external ONS service. That is a bigger
job than the one the tier was chosen for, so the architecture revision is **blocked on a re-dispatch
at the strategic tier** — reported in §5 under routed work, and it is the reviewer's to schedule,
not this review's. The general lesson behind it is change 5.

---

## 1. Regression check — did the last review's changes work?

Audited: [`docs/improvements/2026-09-22-improvement-review-2.md`](2026-09-22-improvement-review-2.md)

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L166) step 6 — read `observable_at` at draft time, decide CLOSE or DEFER before the wording is approved | 2026-09-22 | `draft-states-a-disposition-the-closure-rules-forbid` | NO — 1 instance total, still the originating one | **Working.** Exercised by this review: it is what turned IMP-0831 from a drafted closure into a drafted deferral, before the gate rather than after it |
| Review 2's §1–§2 record on IMP-0817 — no rule change, a reading correction only | 2026-09-22 | `build-blocked-by-the-finding-it-remediates` | NO | Working — leave alone |
| Check 9 of [`scripts/verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py) recorded as this class's standing defence (IMP-0816) | 2026-09-22 | `platform-contract-guessed-not-groundtruthed` | **YES — IMP-0831** | **Not a gate failure.** The gate defends flow-expression shape in solution source; IMP-0831 is an external REST source's field names, which no gate in this repository can see. Different sub-property, correctly undefended — see the cluster's `Residual` |

**Changes whose class recurred after a *prose* fix:** none in this audit window.
**Changes whose class recurred after a *gate*:** `platform-contract-guessed-not-groundtruthed`, and
the gate did not fire because the instance is outside its input. Logging this as a
`gate-cannot-fail` finding would be wrong, and `logs/class-defences.json`'s own authoring rule says
why: a defence is recorded against the **sub-property it actually defends**, never the whole class
name. Check 9 defends flow-expression shape. Nothing defends "an external service returns the
fields a design assumed", and nothing can.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x1 unread: IMP-0831)
Altitude:   CLASS — but a NEW sub-property of a class already at x63. The 63 prior instances are
            about artefacts this repository can open. This one is about an artefact only the
            network can answer for, where the system's own PRIOR ANSWER was the cheapest source
            and was not consulted.
Ladder row: "The system's own memory failed" → a read-path change. Plus "an agent had the
            information and still did the wrong thing" → a skill edit.
Becomes:    skills/how-to-verify-a-platform-contract.md §2 gains a row naming the improvement log
            itself as a governing artefact for any external source previously ground-truthed
            (change 1); agents/architect-agent.md's step table loads that skill at §4, where the
            request/response contract is actually written, not only at §12 (change 2).
Retires:    nothing — see §4.
Cites:      IMP-0831, IMP-0751
Residual:   No gate. The join key would be "the source's own name as the document happens to spell
            it" (`ONSPD_LATEST_UK`), matched against prose in a log entry. Measured the mechanical
            alternative first: architecture documents in this repo contain 4 external URL literals
            in total and NONE of them is this endpoint, so the URL-keyed check the finding itself
            proposes would have scored zero on the document that produced the finding. A
            name-keyed check over prose is the instrument this repository has measured five times
            at 48–100% false (IMP-0422). Prose, deliberately.
```

```
CLUSTER: sdd-mechanism-claim-not-ground-truthed  (x1 unread: IMP-0830)
Altitude:   CLASS, merged with the cluster above — one property, one document earlier. Both wrote
            a design claim from a DESCRIPTION of an artefact instead of from the artefact: one
            from a data portal's page plus a plan-stage paraphrase, one from an existing
            component's observed behaviour rather than the column definition that bounds it.
Ladder row: "An agent had the information and still did the wrong thing" → skill edit; plus a
            step-order fix, because the skill that carries the rule was not in plan-agent's list
            at all.
Becomes:    a second row in the same §2 table (change 1), plus agents/plan-agent.md loading that
            skill's §2 when a requirement claims a new capability reuses an existing component's
            mechanism (change 3).
Retires:    nothing — see §4.
Cites:      IMP-0830
Residual:   `scripts/verify-design-doc-claims.py` catches design-document claims that carry a
            CHECKABLE VALUE — a column that does not exist, a contrast ratio that does not
            recompute. IMP-0830's claim ("the same lookup shape as PostcodeRegionMap") contains no
            value to check, so it stays outside that gate. Extending the gate is not proposed: the
            extension would have to read what "same shape" means.
```

```
CLUSTER: read-path-drops-the-load-bearing-half  (x1: IMP-0834, logged by this review)
Altitude:   CLASS — the mechanism is independent of this incident. It applies to every lesson any
            agent has ever written, and 68 of 188 rendered lessons are currently truncated.
Ladder row: "The system's own memory failed" → a read-path change.
Becomes:    skills/how-to-log-an-improvement.md states the 600-character budget where the `lesson`
            field is specified, and requires the decisive fact in the first sentences (change 4).
Retires:    nothing.
Cites:      IMP-0834, IMP-0831, IMP-0751
Residual:   This reduces future loss; it does nothing for the 68 lessons already truncated. Raising
            LESSON_BUDGET is NOT proposed — the constant was chosen by measurement (the generator
            was run at 400, 600 and 800) and raising it taxes every reader of a page read before
            every dispatch. A gate is not proposed either: "was the cut half the load-bearing
            half" is a judgement about meaning, which is the prose instrument again.
```

```
CLUSTER: dispatched-below-required-tier  (x2 genuine: IMP-0835, IMP-0398; IMP-0290 was REJECTED
            as a false instance — that dispatch had in fact been escalated)
Altitude:   CLASS — second genuine instance, so the altitude rule forbids another instance patch.
            The property, independent of the instance: A TIER IS CHOSEN FROM THE BRIEF, BEFORE THE
            WORK THAT DETERMINES THE TIER. Both instances are architect-agent only because
            architecture is where ground-truthing routinely changes the size of the job; nothing
            in the mechanism is specific to that agent.
Ladder row: "The ORDER of steps was wrong" → an activation-order fix, carried mechanically.
Becomes:    scripts/generate-subagents.py's escalation preamble (change 5). That preamble is
            emitted into EVERY .claude/agents/<name>.md, so one edit reaches every pinned agent,
            and `generate-subagents.py --check` is already a HARD build step — the change cannot
            silently fail to reach the generated files.
Retires:    nothing.
Cites:      IMP-0835, IMP-0398
Residual:   The preamble tells an agent to STOP and ask for re-dispatch; nothing forces it to.
            Nothing can: a pinned model cannot escalate itself, so the only mechanical alternative
            would be a gate reading an output to judge whether its author should have been on a
            bigger model — which is not measurable. Measured the cheaper alternative and rejected
            it: skills/how-to-select-a-model.md is the topical home, and it is referenced by
            CLAUDE.md and by NO agent file, so a rule placed there alone would be read by nobody
            at the moment it applies.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L96) §2 | Two rows in the governing-artefact table: what an **external data service returns** is cited from a live metadata call plus this system's own log grepped by the source's name — never a portal page or an SDD's description of it; whether a new requirement can **reuse an existing component's mechanism** is cited from that component's reading action and its storing column's own declared limits — never the SDD's paraphrase of its behaviour | IMP-0831, IMP-0830, IMP-0751 | NO — instruction change | N/A |
| 2 | agent | [`agents/architect-agent.md`](../../agents/architect-agent.md#L84) | Step table gains a row: **§4 integrations — request/response contract** loads `how-to-verify-a-platform-contract.md`. It is currently loaded only at §12.1/§12.2, which is after §4 has already named the response fields | IMP-0831 | NO — instruction change | N/A |
| 3 | agent | [`agents/plan-agent.md`](../../agents/plan-agent.md#L136) | Step table gains a row: a requirement claiming a new capability shares **"the same shape or mechanism" as an existing component** loads `how-to-verify-a-platform-contract.md` §2. That skill is in no plan-agent step today | IMP-0830 | NO — instruction change | N/A |
| 4 | skill | [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L45) | The `lesson` field's guidance states the digest's 600-character budget, that the cut is taken at a sentence boundary from the END, and that the tail is relocated to an appendix no agent loads — so the decisive fact goes in the first sentences | IMP-0834 | NO — instruction change | N/A |
| 5 | script | [`scripts/generate-subagents.py`](../../scripts/generate-subagents.py#L196) **and its unsplit duplicate** `.engine/scripts/generate-subagents.py` | The escalation preamble emitted into every generated agent file stops being a pre-start-only check: it gains the re-check point, naming ground-truthing as the moment that changes the estimate the tier was chosen from, and `BLOCKED` + re-dispatch as the response. Regenerating `.claude/agents/` is part of the same change | IMP-0835, IMP-0398 | **YES** — `python3 scripts/generate-subagents.py --check` | **already wired** — HARD at [`config/revitalise-grant-automation-build.yml#L110`](../../config/revitalise-grant-automation-build.yml#L110) |

**Constraint budget:** 0 of 3 used.

**Change 5 is two files, not one.** `scripts/generate-subagents.py` and
`.engine/scripts/generate-subagents.py` are byte-identical with nothing keeping them in step, and
the build runs the `scripts/` copy — so an engine-only edit would parse, pass `--check` and never
execute. Both are edited in the same change and
`python3 scripts/verify-engine-instance-split.py` is run before closing.

**No new gate is proposed, and each cluster's `Residual` says why in its own terms.** The honest
summary: the first three findings are about a claim made in prose about an artefact elsewhere, and
the only mechanical join keys available are prose phrases. One was measured directly for this
review — see the first cluster's `Residual`, where the finding's own proposed mechanism scores zero
on the document that produced the finding. Change 5 is mechanical without being a new gate: it
edits a generator whose `--check` is already a HARD build step, so the change reaching every
generated agent file is verified by a gate that exists.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows and 10 already retired reviewed for overlap
> with the two skill sections this review edits; none currently redundant.

The closest candidate was examined and is **kept**: the **dataset-portal-page row** in
[`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L737),
added by IMP-0751 — the very finding whose lesson was truncated here. It defends a different half (what a source *contains* versus how it is *reached*),
and change 1 adds the third half (what it *returns*) rather than replacing it. Retiring it would
lose coverage.

Counts derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10;
`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 86.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812,
IMP-0818, IMP-0819, IMP-0820, IMP-0821, IMP-0822, IMP-0823, IMP-0824, IMP-0825, IMP-0826,
IMP-0827, IMP-0828, IMP-0829, IMP-0832, IMP-0833, IMP-0836, IMP-0837

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0820, IMP-0821 | (blocker, already reviewed) | **Not this review's to re-derive.** A review has processed them and is parked at [`2026-09-22-improvement-review-3.md`](2026-09-22-improvement-review-3.md). The remedy is the keyword, not a session | the reviewer responds to that document |
| IMP-0824 | (blocker, already reviewed) | Same — parked at [`2026-09-22-improvement-review-4.md`](2026-09-22-improvement-review-4.md) | the reviewer responds to that document |
| IMP-0798 … IMP-0803, IMP-0811, IMP-0812 | various, none blocker | Declared out of scope by [review 1 of 2026-09-22](2026-09-22-improvement-review.md) and already carrying its `excluded_by` stamp | the next batch review, or their own trigger |
| IMP-0818, IMP-0819 | various, none blocker | Declared out of scope by [review 3 of 2026-09-22](2026-09-22-improvement-review-3.md), stamp already present | as above |
| IMP-0822, IMP-0823, IMP-0825 | various, none blocker | Declared out of scope by [review 4 of 2026-09-22](2026-09-22-improvement-review-4.md), stamp already present | as above |
| IMP-0826, IMP-0827, IMP-0828, IMP-0829 | various, none blocker | Unread and unstamped at this review's activation. Out of scope: one unread blocker does not pull a review of the queue around it | the next batch review (queue is at 19 unread) |
| IMP-0832, IMP-0833, IMP-0836 | `sdd-summary-claim-not-scope-checked-against-cited-section`, `tool-capability-misdescribed-in-handoff`, `per-feature-build-config-vs-solution-scoped-gate-wiring` | Appended by other live sessions **during** this review. All three `friction`. Same reason | the next batch review |

| IMP-0837 | `rule-lives-in-a-file-no-agent-loads` | Appended by another session at 13:10, `friction`. **It independently measures the same thing cluster 4's `Residual` measures** — that `skills/how-to-select-a-model.md` is named by no agent file — which is why change 5 puts the escalation re-check in the generated agent preamble instead of in that skill. Processing it properly means deciding what happens to a 148-line skill nobody reads, which is a batch-review question | the next batch review |

**On approval**, `excluded_by: docs/improvements/2026-09-23-improvement-review.md` is stamped on
the eight entries that carry no exclusion stamp yet — IMP-0826, IMP-0827, IMP-0828, IMP-0829,
IMP-0832, IMP-0833, IMP-0836, IMP-0837 — so that obeying the no-silent-caps rule does not raise a citation warning per
excluded id (`IMP-0557`). The field takes the bare path and nothing else.

### Dispositions of the three processed entries

| Finding | `observable_at` | Disposition | Why |
|---|---|---|---|
| IMP-0831 | **V5** | **DEFER** — stays `NEW`, gains `deferred_reason` + `revisit_when` | A V5 defect is closed by an end-to-end execution with real inputs. The correcting execution is the revised flow issuing the corrected grouped query against the live ONS layer — the architecture revision is routed to `architect-agent` and the flow is not built. Nobody in this session can produce that observation, so this is drafted as a deferral from the start rather than as a closure that would have to be walked back at apply time (`IMP-0815`) |
| IMP-0830 | V1 | **CLOSE** on approval → `APPLIED` | V1 is settled by `evidence_grep`; changes 1 and 3 are the fix |
| IMP-0834 | V1 | **CLOSE** on approval → `APPLIED` | As above; change 4 is the fix |
| IMP-0835 | `n/a` | **CLOSE** on approval → `APPLIED` | `n/a` needs only `evidence_grep`; change 5 is the fix, and the needle is grepped in the generated file after regeneration, not written from the intended wording |

The deferral is what clears the blocker rung of
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1373): a bare `revisit_when`
discharges nothing, and a `deferred_reason` is a **reviewer-authored** decision — which is what
`APPROVE IMPROVEMENTS` against this document makes it. Simulated before parking; result in §6.

### Routed work — one item, and it is not this review's to do

| Item | Owner | State when re-measured at draft time |
|---|---|---|
| The postcode-lookup architecture revision (§4, §5, §12.2, ADR-001) is **blocked on a `model: opus` re-dispatch**. The standard-tier architect dispatch stopped, correctly, on discovering that the fix needs an aggregation mechanism this project's own knowledge files already record as unavailable anywhere in the stack, plus a second external ONS service | `lead-agent` | **Still open.** Re-measured: `docs/architecture/postcode-lookup-architecture.md` still carries the assumed field names in §4 and `A-LAR-01` still reads unresolved in §12.2 |

This is reported, not dispatched. Change 5 makes the *stopping* a standing instruction for every
agent; it does nothing about this particular revision, which needs the re-dispatch.

---

## 6. Digest impact

| | Before | After (projected — re-measured at apply time, not carried forward) |
|---|---|---|
| Log entries | 831 | 831 |
| Distinct lessons rendered | 188 | ~190 |
| Recurring classes (x≥2) | 60 | 60–61 |
| Digest lines | 747 | ~752 |

The "before" row was measured at 830 entries and the log reached 831 during this draft — two other
live sessions appended while it was open. Every figure here is re-measured after regeneration
rather than quoted from this table.

Regenerate with `python3 scripts/generate-known-failure-modes.py` on approval and confirm with
`--check`.

**Simulation — run before parking, on a scratch copy; the real log was never written by it.**
Applying all four dispositions plus the seven exclusion stamps, the gate's **unread-blocker
trigger disappears**. What remains is the trigger for the three `awaiting-approval` blockers parked
at reviews 3 and 4 of 2026-09-22, which this review may not touch and which only the reviewer's
keyword against *those* documents clears.

The simulation also produced three `evidence_grep` errors — one per entry drafted for closure —
because the needles point at wording the approved changes have not yet written. That is the
expected shape of simulating before approval, not a defect in the plan: each needle is grepped in
its target file after the edit lands, and re-pointed there if the wording moved
(`grep -c '<needle>' <file>` returning 1 is the whole check).

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-23-improvement-review.md

Findings processed: 4 NEW  →  4 clusters
Regression check:   3 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 2 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 0 left as notes
Digest:             will regenerate — ~190 lessons, 60 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Applied 2026-09-23** on `APPROVE IMPROVEMENTS`, as part of a batch applying six parked reviews.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `skills/how-to-verify-a-platform-contract.md` §2 — two governing-artefact rows: what an external data service RETURNS, and whether a requirement can reuse an existing component's mechanism | 2026-09-23 | IMP-0830 |
| 2 | `agents/architect-agent.md` — step table gains the §4 integrations row loading the contract skill where the response fields are first named | 2026-09-23 | (IMP-0831 — deferred) |
| 3 | `agents/plan-agent.md` — step table gains the "same shape or mechanism" row; the skill was in no plan-agent step before | 2026-09-23 | IMP-0830 |
| 4 | `skills/how-to-log-an-improvement.md` — the `lesson` field states the 600-char budget, the end-cut at a sentence boundary, and the appendix no agent loads | 2026-09-23 | IMP-0834 |
| 5 | `scripts/generate-subagents.py` **and** its `.engine` twin — the escalation preamble gains the post-ground-truthing re-check; `.claude/agents/` regenerated | 2026-09-23 | IMP-0835 |

Entries rejected, with reasons: none.

**Change 5 verified mechanically, not asserted.** Both copies were edited and confirmed
byte-identical, `generate-subagents.py` was run, and `--check` reports `.claude/agents is current
(18 files)`. The new clause reaches **16 of 18** generated agent files — the other two declare no
`escalate_to_strategic_when`, so the preamble block does not render for them. That is the correct
count, not a partial application.

**IMP-0835 is closed ONCE, here and in review 2 of the same day, not twice.** Both reviews
independently processed it: this one as change 5, review 2 as its only change. The two changes are
complementary rather than competing — the generated preamble carries the rule to every dispatched
agent at activation, the skill carries it to the four ground-truthing agents at the moment the
trigger fires. The entry's `reviewed_in` now lists both documents and its `applied_by` names both
changes.

**On change 4, a premise was re-measured at apply time and the wording changed as a result.** The
draft's text instructed the reader to *"grep for `known-failure-modes-appendix` and you get zero
hits"*. That was true when the draft was written and **false the moment the change landed** — the
instruction's own text is two hits. A rule that falsifies itself on application teaches the reader
the rule is wrong, so it was rewritten as a dated measurement (*"Measured 2026-09-23: … the only
mentions of it anywhere in the read path are the two in this paragraph"*). The substance is
unchanged. Recorded here rather than made silently.

**Step 5 of the apply-time checklist, re-measured:** `verify-derived-counts.py` reported 4 drifted
claims at draft time. See the batch-level record for what it reports now and which single claim was
this review's to correct.

**Apply-time checklist, in order.** Each change lands with its own bookkeeping — statuses move as
the change lands, never all at the end; the digest is regenerated once, last.

1. Changes 1–4, each followed by `grep -c '<needle>' <file>` before its entry's `evidence_grep` is
   written, and by that entry's status move.
2. Change 5 in **both** copies of the generator, then `python3 scripts/generate-subagents.py`,
   then `--check`, then `python3 scripts/verify-engine-instance-split.py`.
3. `excluded_by` stamped on the seven out-of-scope entries; `deferred_reason` + `revisit_when`
   written on IMP-0831 **verbatim from §5**.
4. `python3 scripts/verify-improvement-log.py --check`, then
   `python3 scripts/generate-known-failure-modes.py`, then `--check`.
5. `python3 scripts/verify-derived-counts.py`. It currently reports **4** drifted claims. One is
   this agent's to fix — the digest's own line-count sentence in
   [`scripts/generate-known-failure-modes.py`](../../scripts/generate-known-failure-modes.py#L46),
   which drifts as a *consequence* of the regeneration every review is required to perform. The
   other three (two secured-column counts in the grant-automation Dev Summary, one in the REV
   Trustee role XML) are delivery-owned, pre-date this review, and are reported, not touched.

**This review's output spans two repositories.** All four changes
are in `skills/` and `agents/`, which are symlinks into the `.engine` submodule. Publishing is:
commit in `.engine`, `git -C .engine push origin HEAD:main`, verify with
`git -C .engine branch -r --contains HEAD` (it must list `origin/main`), then the instance commit
carrying the pointer bump. A clean `git status` proves nothing about whether the pointee is
reachable.
