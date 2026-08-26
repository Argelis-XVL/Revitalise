# Improvement Review 24 — 2026-08-24

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `NEW` (`unread`) → 4 clusters
**Trigger:** blocker escalation — three unread blockers ([IMP-0270](../../logs/improvement-log.jsonl#L267), [IMP-0271](../../logs/improvement-log.jsonl#L268), [IMP-0272](../../logs/improvement-log.jsonl#L269)), routed immediately per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L207)
**Status:** **APPLIED 2026-08-24** on `APPROVE IMPROVEMENTS` from Xander Lykopoulos — with two changes held back and one handover. Sections 1–8 are the review as approved and are left unedited; **section 9 records what actually went to disk, and section 10 records what did not and why.** Read section 10 first if you are here for the platform contract: the ground truth moved between drafting and applying.
**Scope note:** the fourth review dated 2026-08-24, after [21](./2026-08-24-improvement-review.md), [22](./2026-08-24-improvement-review-2.md) and [23](./2026-08-24-improvement-review-3.md). My dispatch named three findings; the log gate reports **six** unread, so all six are processed here — see section 6.
**WBS:** the defects behind this review serve [task 0.4](../../contract/wbs.json); the review itself is system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md))

---

## Summary

**Two real gaps are open in the live DEV environment right now, and the most useful thing this batch found is why neither was caught: a HARD rule that demands live verification is satisfied by a deploy step whose script is the word `manual`.** Five columns that source says are confidential are unsecured live, and four tables holding no rows yet have no audit trail — both invisible to every gate in the build, all of which are green and all of which read source.

One of the three critical findings is **already fixed on disk** and its status was simply stale. The code fix for another is being written by a parallel dispatch, so I propose the durable half and leave the code alone.

**What needs you:** approval of one new constraint, four gate/script changes, two knowledge edits and one agent-file edit — plus a decision on whether to hand the live environment-state verifier to a delivery agent, which is the piece that actually closes this class.

---

## 1. Regression check — did the last review's changes work?

[Review 23](./2026-08-24-improvement-review-3.md) was applied yesterday. Its ten changes are audited below.

| Prior change | Class it targeted | Recurred? | Verdict |
|---|---|---|---|
| [verify-declared-property-reaches-creation-path.py](../../scripts/verify-declared-property-reaches-creation-path.py) + [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | a declared property the creating code never sends | no — for its own class | **Worked, and immediately tripped its neighbour.** The new script fired the adjacent HARD gate [source-reader-plurality](../../config/revitalise-grant-automation-build.yml#L279) on its first full build. See cluster C |
| [verify-provisioning-step-convergence.py](../../scripts/verify-provisioning-step-convergence.py) | a create-only step that never corrects itself | no | **Worked.** Nothing in this batch is a convergence defect |
| Fourth rung in [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py#L118) | a fixture count claimed and never checked | no | **Worked.** No stale fixture count in this batch |
| `historical` exemption in [verify-derived-counts.py](../../scripts/verify-derived-counts.py#L237) | a dated record rewritten to match today | no | Worked for what it exempted — **but the gate underneath it is wrong.** See cluster C |
| **Review 23's own derived figure — "67, confirmed three independent ways"** | — | **YES** | **The review handed a wrong number to a delivery agent.** This is the row that matters |
| [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L110) — a finding's cause is a hypothesis, re-verify it | acting on an unverified diagnosis | no | **Worked, and it is what caught the row above.** The delivery agent counted the source itself instead of obeying the gate |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84), [C-TECH-070](../../constraints/technology/technology-constraints.md#L141), [C-TECH-065](../../constraints/technology/technology-constraints.md#L135)/[067](../../constraints/technology/technology-constraints.md#L137) amendments | non-executable verification, stale literals | no | Worked |
| [security-model.md](../../knowledge/technology/security-model.md#L34) and [dataverse.md](../../knowledge/technology/dataverse.md#L261) metadata facts | guessing a metadata contract | **YES — the next day** | The new metadata section covers **reads** only. The defect that landed was a **write**. See cluster B |

**The fifth row is the important one, and it is a clean demonstration of why one of this batch's proposals is needed.**

Review 23 measured the trustee role file's secured-column count as 67 and passed that figure to `development-agent` to write into the role file's header. The right answer is **51**. The number 67 is [REV_TrusteeRestricted](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml)'s 51 permissions plus REV_FinanceOnly's 16, added together by a gate that counts the whole file regardless of which profile the claim is about. Writing 67 there would have **overstated a privacy control** by sixteen columns it does not cover.

It was caught because the delivery agent counted the source by hand rather than trusting the gate — which is exactly the behaviour review 23's own skill edit had just established. The process worked; the tool was wrong.

**The eighth row is the second recurrence.** Review 23 added a metadata-reading section to the knowledge file, including the rule that a 400 on a metadata GET means an illegal projection. The next live run failed on a metadata **PATCH** — a different verb, the same polymorphism trap, and the knowledge edit was scoped to reads.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: platform-state-divergence  (x2 BLOCKERS: IMP-0270, IMP-0271)
Altitude:  CLASS — instances 7 and 8 of a class at x8. IMP-0178 already recorded
           IMP-0271's exact lesson as PROSE on 2026-08-21 and the defect recurred
           verbatim three days later, which per the altitude rule forbids a third
           prose statement of the same sentence.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise"
Becomes:   a 5th rung in verify-constraint-verifiers.py — a HARD constraint whose
           Verify By demands LIVE verification, resolving only to a pipeline step
           declared `script: manual`, is reported as not mechanically enforced.
           Plus a skill edit for the per-defect re-query, and a HANDOVER of the live
           verifier to a delivery agent (it authenticates; it is not mine to write).
Retires:   nothing. No instance gate existed — the step existed and was never executable.
Cites:     IMP-0270, IMP-0271, IMP-0082, IMP-0085, IMP-0178, IMP-0222
Residual:  The new rung proves a step is EXECUTABLE, never that anyone RAN it. That
           second question needs a deploy-time record and is not built here. Named so
           the gap is not mistaken for coverage.
```

```
CLUSTER B: platform-contract-guessed-not-groundtruthed  (x1 BLOCKER: IMP-0272)
Altitude:  CONSTRAINT, skipping ahead deliberately. One member in its own right, but
           how-to-promote-a-finding.md §4 permits skipping to a constraint row when the
           severity is blocker and the mechanism is a platform law. It is instance 34 of
           the project's largest class, and the read-side twin is already documented.
Ladder row: "a platform law" + "prefer the most mechanical home"
Becomes:   1 constraint + scripts/verify-metadata-write-casts.py + a knowledge line
           beside its read-side sibling.
Deferred:  the CODE fix in ensure-schema.ps1 step 3b. A development-agent dispatch is
           editing that file now; proposing an edit to it here would collide.
Cites:     IMP-0272
Residual:  The gate reads URI-building source text. A URI assembled across several
           variables, or built at runtime from a lookup table, is not visible to it.
```

```
CLUSTER C: a check whose scope was right only by coincidence  (x2: IMP-0268, IMP-0269)
Altitude:  Two different class names, one property. IMP-0269 is instance 6 of
           test-assumed-name-is-solution-unique; IMP-0268 is the 4th false positive of
           the plurality gate and the 1st from a newly authored file. Both are: a check
           validated when the solution held ONE instance, producing a FALSE claim once a
           second existed. C-TECH-069 already states this rule; its gate cannot reach a
           JSON registry (it scans .py/.ps1/.psm1 only), so no new constraint is needed.
Ladder row: "a tool could catch it mechanically"
Becomes:   scope the count derive to the profile the claim names + wire the count gate
           into the build at all. IMP-0268 needs nothing: its fix is already on disk.
Retires:   nothing. See section 4 for the two registry rows I propose removing.
Cites:     IMP-0268, IMP-0269, IMP-0240, IMP-0169
Residual:  Scoping the derive fixes ONE row. Two other rows in the same registry use the
           same file-wide count against dated historical claims — inert today because
           they are `historical`-exempt, and wrong the moment anyone un-exempts them.
```

```
CLUSTER D: declared-policy-not-mechanically-enforced  (x1: IMP-0265)
Altitude:  AGENT FILE, and the measurement makes it concrete rather than advisory.
           Instance 6 of the class. Same shape as IMP-0183, in a second file: the log
           gate grew a four-state model, improvement-agent.md was updated to match, and
           lead-agent.md was not.
Ladder row: "an agent had the information and still did the wrong thing" + "the system's
           own memory failed"
Becomes:   lead-agent.md's two hand-written greps are replaced by the gate script that
           already exists, plus a dispatch-time ordering rule.
Cites:     IMP-0265, IMP-0183
Residual:  Prose in an agent file, checked by nothing. I considered a gate and rejected
           it: nothing can observe whether an agent ran a command before dispatching.
```

**I measured cluster D rather than accepting it, and the measurement is worse than the finding said.** [lead-agent.md](../../agents/lead-agent.md#L137) tells the lead agent to count the queue with two greps. Run today they return **25 pending and 11 blockers**. The gate's honest answer is **6 unread and 3 unread blockers** — the difference is 19 findings the reviewer already deferred with a recorded reason. A routing trigger that is permanently and visibly over-tripped is a trigger that gets ignored, which is the mechanism behind this whole class.

---

## 3. Proposed changes

| # | Type | Target | What it does | Can it fail? |
|---|---|---|---|---|
| 1 | **script** | [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py#L118) — 5th rung | A HARD constraint whose `Verify By` demands live verification must resolve to at least one **executable** step. Reports every HARD row whose only route is a step declared `script: manual`. [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) is a live fixture today | YES — C-TECH-064 fails it now; a fixture with an executable step passes |
| 2 | **handover, not authored here** | `provisioning/dataverse/` — the C-TECH-064 live environment-state verifier | The executable form of the deploy check that has sat [`script: manual`](../../config/revitalise-grant-automation-pipeline.yml#L913) since 2026-08-19. **I am not writing it**: it authenticates to a live environment, which [my own instructions](../../agents/improvement-agent.md#L220) make delivery work. Requirement and queries stated in section 5 | n/a — a handover |
| 3 | **skill** | [how-to-verify-a-platform-contract.md §9](../../skills/how-to-verify-a-platform-contract.md#L235) | Extends "one instance proves one instance" to sibling defects: when a handoff cites one live re-run as closing several defects fixed in the same revision, each defect's own re-query is run separately. One confirmed fix is not evidence for its sibling | Partly — the check is mechanical, the remembering is prose |
| 4 | **constraint** | `C-TECH-072` (HARD), new | **A Web API call against a polymorphic metadata collection names the concrete derived type in the URI, not only in the request body.** Covers the read side (a 404 under the wrong cast) and the write side (`PATCH` rejected outright on the uncast base collection). `Verify By` is change 5 | Change 5 is its `Verify By` |
| 5 | **script** | `scripts/verify-metadata-write-casts.py` (new) | Fails any metadata write under `provisioning/` whose URI targets `/Attributes(...)` with no `Microsoft.Dynamics.CRM.*AttributeMetadata` cast segment. Catches [the live failure](../../provisioning/dataverse/ensure-schema.ps1#L626) and will catch the in-flight fix if it lands wrong | YES — the current uncast URI is the fixture; a cast one passes |
| 6 | **knowledge** | [testing-tools.md](../../knowledge/technology/testing-tools.md#L238) | The write-side rule beside the read-side "404 trap" it already documents. A fact belongs beside its sibling — review 23's own principle | Facts are live-verified; change 5 is the enforcement |
| 7 | **script + registry** | [verify-derived-counts.py](../../scripts/verify-derived-counts.py#L184) and [the trustee row](../../scripts/derived-counts-registry.json#L88) | Gives the pair-count derive a scope selector, and scopes the trustee claim to `REV_TrusteeRestricted`. The gate then derives **51**, matching the prose, and the false drift clears honestly instead of by editing correct text | YES — a fixture with two profiles must return the scoped count, not the sum |
| 8 | **build gate** | [build.yml](../../config/revitalise-grant-automation-build.yml#L279) | Wires `python3 scripts/verify-derived-counts.py` in as a **SOFT** step (WARN, never blocking). It is currently reachable only by hand, which is why a drift it detects correctly stood for a day | YES — it exits 1 on a real drift today |
| 9 | **agent** | [lead-agent.md](../../agents/lead-agent.md#L137) | Replaces the two greps with `python3 scripts/verify-improvement-log.py --check`, and adds the ordering rule: run it **before** dispatching build-agent or pipeline-agent, whose own pre-flight will otherwise discover it after the dispatch | Partly — prose, but it removes a wrong command rather than adding a right one |

**One new constraint against a cap of three.** Clusters A, C and D need none: A is enforcement of [C-TECH-064](../../constraints/technology/technology-constraints.md#L134), which already says the right thing; C is enforcement of [C-TECH-069](../../constraints/technology/technology-constraints.md#L140), same; D is a stale instruction, not a missing rule.

**Change 5 is deliberately scoped to `provisioning/` and deliberately not applied to `ensure-schema.ps1` itself.** A parallel dispatch is editing that file. The gate will judge whatever it lands.

---

## 4. Retirements

**No constraint row retires, and I checked rather than assuming.** The nearest candidates were C-TECH-064 and C-TECH-069 — both turn out to be *correct rules with unreachable verification*, so both are enforced by new gates rather than retired. Retiring either would remove the rule that names the defect.

**Two registry rows are the retirement candidate.** [The handover row and the review-5 row](../../scripts/derived-counts-registry.json#L88) both compare a file-wide count against dated historical claims of 39, and both are permanently `historical`-exempt — they can never fire and can never be actioned. They are two more copies of the unscoped derive that produced this batch's false drift. I propose removing them in change 7 rather than scoping three rows to one live claim.

**Derived, not typed:** 78 live constraint rows and 10 retired, via `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`.

---

## 5. What you need to decide

**Two live gaps are open in DEV, and neither closes from this repository.**

Five lookup columns that source marks confidential report unsecured live, and the finance profile holds 11 of its intended 16 permissions. The code fix for the cause is being written now by another dispatch; after it lands, someone has to re-run `pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev` and confirm the five columns come back secured.

Separately, all four new finance tables report no audit trail. That one needs no code at all — `pwsh provisioning/dataverse/ensure-auditing.ps1 -Env dev`, which is proven working, and then `EntityDefinitions(LogicalName='<t>')?$select=IsAuditEnabled` returning true for each. The tables hold no rows yet, so this is harmless today and a real defect the moment the first application is created.

**Do you want the live environment-state verifier built?**

This is the decision that actually closes the class rather than patching it. A deploy step already exists that would have caught both gaps: it reads live audit state for every table folder in source and reports each failure by name. It has said `script: manual` since 2026-08-19, waiting on an executable form that was handed to a delivery agent and never written — and because it is a checklist item rather than a command, nobody ran it.

My change 1 makes that condition **visible** on every build: a HARD rule verified only by a manual step gets reported. It does not make it go away. The verifier itself authenticates to Dataverse, so my own instructions put it under `provisioning/` and in a delivery agent's hands, not mine.

I recommend dispatching it to `development-agent` with the queries C-TECH-064 already enumerates. The alternative — leaving it manual — is defensible only if you are content that the operator checklist is the control, and this batch is evidence that it is not.

---

## 6. Findings left unprocessed

**States excluded, stated so the cap is not silent:** 19 `reviewer-deferred` (each carrying a reason a human accepted), 0 `awaiting-approval`, 0 `already-fixed` by the gate's reckoning, and every `APPLIED`/`REJECTED` entry. All **6** `unread` entries were read in full and all six are dispositioned above.

**My dispatch named three findings and the queue held six.** The three extra are all `unread`, which [activation step 2](../../agents/improvement-agent.md#L102) makes my scope regardless of what the dispatch listed. Processing the three blockers alone would have split cluster C across two reviews.

**One finding was already fixed before I read it.** [IMP-0268](../../logs/improvement-log.jsonl#L265) proposed adding an exemption marker to a script; [the marker is on disk at line 97](../../scripts/verify-declared-property-reaches-creation-path.py#L97), citing the finding by id, and the gate now passes 35 readers. It was reported as unread rather than already-fixed because it carries no `evidence_grep` needle — and that field is used by the log gate but documented nowhere in [the schema skill](../../skills/how-to-log-an-improvement.md). Worth a one-line addition; I have not proposed one, to stay inside the cap, and it belongs to whoever next edits that skill.

**Three findings stay open, and they are the three blockers.** Their defects are live-environment state at V3, and nothing in this session can observe them fixed — I have no live access. Closing them on my knowledge and gate work is exactly the defect that [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) was amended to prevent. Each gets a `deferred_reason` and a `revisit_when` naming the exact command and who can run it.

**That is what clears the blocked build, and it clears it honestly.** [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) is red right now, which is what stopped the finance-table build. A recorded deferral is a reviewer's decision and does not trip the gate; an unread queue is not a decision. Three deferrals plus three closures takes the queue from 6 unread to 0.

**A concurrent session may be writing this log.** The last review recorded it growing mid-derivation. On approval I re-read immediately before appending.

---

## 7. Digest impact

**I am not predicting a number.** Review 20's own lesson is that a predicted delta was wrong because the generator routes a lesson by two mechanisms and one silently wins.

What I can state without measuring: the digest is **current right now** (`--check` green at 269 entries), and one class table row moves from x6 to x8 while `source-reader-plurality-false-positive` appears for the first time. On approval I regenerate and report the measured before-and-after.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review-4.md

Findings processed: 6 unread  →  4 clusters
Regression check:   10 prior changes audited, 2 classes recurred
Proposed:           1 constraint (cap 3), 4 gates/scripts, 2 skill/knowledge edits,
                    1 agent-file edit, 0 constraint retirements
                    (+ 2 registry rows removed, + 1 handover to a delivery agent)
Altitude calls:     2 generalised from instance to class, 1 skipped ahead to a constraint
                    (blocker + platform law), 1 code fix deferred to an in-flight dispatch
Digest:             will regenerate and report measured — currently current at 269 entries

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification executed for this review:** the log gate's state breakdown read before any finding; 2 gate runs (`verify-source-reader-plurality` OK at 35 readers, `verify-derived-counts` exit 1 on its one real drift); the pipeline preflight run (PASS, 83 steps, 40 executable / 43 manual); the two profile counts read out of the solution XML independently (51 and 16, summing to the 67 the gate reports); lead-agent's two documented greps executed and compared against the gate (25/11 versus 6/3); the uncast PATCH URI read at [ensure-schema.ps1 L626](../../provisioning/dataverse/ensure-schema.ps1#L626); the plurality exemption confirmed on disk; the `blocked_on` staleness threshold read (14 days, so the 2026-08-19 notes have 9 days left and will not self-report); digest `--check` green.

**Not verified, and it is the honest limit of this review:** every script in section 3 is **unwritten** — nothing here is on disk, so per [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) changes 1, 5, 7 and 8 are at **V0**. No live Dataverse call was made by anything in this review; the three blockers' live state is read from the findings, not re-observed by me.

---

## 9. What was applied

**Seven of the nine proposed changes are on disk. One is a handover, and two are held back because their premise was disproved between drafting and approval — see section 10.**

| # | Type | Target | State |
|---|---|---|---|
| 1 | script | [verify-constraint-verifiers.py L224](../../scripts/verify-constraint-verifiers.py#L224) — rung 5 | **APPLIED**, and it fires on [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) exactly as predicted |
| 2 | handover | `provisioning/dataverse/` — the C-TECH-064 live verifier | **HANDED OVER, not written.** See below |
| 3 | skill | [how-to-verify-a-platform-contract.md L244](../../skills/how-to-verify-a-platform-contract.md#L244) | **APPLIED** |
| 4 | constraint | `C-TECH-072` | **HELD BACK** — premise disproved, section 10 |
| 5 | script | `scripts/verify-metadata-write-casts.py` | **HELD BACK** — would fail correct code, section 10 |
| 6 | knowledge | [testing-tools.md L244](../../knowledge/technology/testing-tools.md#L244) | **APPLIED, with corrected content** — section 10 |
| 7 | script + registry | [verify-derived-counts.py L222](../../scripts/verify-derived-counts.py#L222), [registry L69](../../scripts/derived-counts-registry.json#L69) | **APPLIED** |
| 8 | build gate | [build.yml L275](../../config/revitalise-grant-automation-build.yml#L275) | **APPLIED** |
| 9 | agent | [lead-agent.md L137](../../agents/lead-agent.md#L137) | **APPLIED** |

### The measurements, not the predictions

**Rung 5 discriminates: it reports one row of two, and the one it reports is the right one.** [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) fails because its only pipeline route is [`environments.dev.verification[4]`](../../config/revitalise-grant-automation-pipeline.yml#L913), declared `script: manual`. `C-TECH-065` demands live verification too and passes, because three of its four routes are executable. `C-TECH-070` and `C-DOM-032` are correctly *not* classified as live demands — both verify source-side by design, and C-DOM-032's own text says so.

**The false drift cleared without editing correct prose.** The trustee claim's derive now returns **51** scoped to `REV_TrusteeRestricted` against **67** unscoped, both measured directly. The role file's header, which said 51 and was right all along, is untouched. Two registry rows were removed and the reason is recorded in [the registry's own header](../../scripts/derived-counts-registry.json#L4) rather than lost in this document; the registry is 7 rows and green.

**The build config grew one SOFT step and stayed green.** Preflight reports **44 steps, 33 gates, PASS** — the new [`derived-counts`](../../config/revitalise-grant-automation-build.yml#L275) step proves itself failable through its own `--selftest`, so it needed no new known-bad fixture.

**Cluster D's measurement got worse again between drafting and applying, which is the point.** The two greps [lead-agent.md](../../agents/lead-agent.md#L137) used to carry returned **27 pending and 12 blockers** today, against the gate's **6 unread and 3 unread blockers**. When this review was drafted the same greps said 25 and 11. A trigger that over-reports by 21 and drifts further every day is one nobody can act on.

### Digest impact — measured, and the measurement is zero

**The digest did not change: 271 entries, 271 distinct lessons, 477 lines, byte-identical before and after regeneration.**

This is worth recording because [section 7](#7-digest-impact) declined to predict a delta and still guessed the shape wrongly. It expected `platform-state-divergence` to move x6 → x8 and `source-reader-plurality-false-positive` to appear. Neither happened, because **the generator already renders `NEW` entries**: `platform-state-divergence` [was already x8](../../logs/known-failure-modes.md#L43) before this review touched anything, and the plurality class has one member, below the recurring-class table's threshold. Moving a finding from `NEW` to `APPLIED` changes its status, not its lesson or its class, so the digest is invariant under exactly the operation an improvement review performs.

Review 20's lesson holds and generalises: do not predict digest deltas. This review adds the reason — for status-only changes the honest prediction is **zero**.

### Findings dispositioned

**Three closed, three deferred, and the deferrals are the honest half.**

| Finding | State | Why |
|---|---|---|
| [IMP-0265](../../logs/improvement-log.jsonl#L262) | **APPLIED** | change 9 |
| [IMP-0268](../../logs/improvement-log.jsonl#L265) | **APPLIED** | its fix was already on disk; re-verified, not re-applied |
| [IMP-0269](../../logs/improvement-log.jsonl#L266) | **APPLIED** | changes 7 + 8, both halves |
| [IMP-0270](../../logs/improvement-log.jsonl#L267) | **deferred** | live V3 state; the skill edit is applied, the defect is not observable here |
| [IMP-0271](../../logs/improvement-log.jsonl#L268) | **deferred** | live V3 state; needs one script run and no code |
| [IMP-0272](../../logs/improvement-log.jsonl#L269) | **deferred** | live V3 state, **and** its diagnosis was superseded — section 10 |

Each deferral carries a `deferred_reason` and a `revisit_when` naming the exact command and that only the reviewer can run it. **None was closed on a document saying it was fixed** — that is `IMP-0208`'s failure, found still live three days later by `IMP-0224`/`IMP-0225`.

The queue is now **0 unread and 0 unread blockers**, from 6 and 3. [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) is green, which is what was blocking the finance-table build, and it is green because six findings were decided rather than because anything was hand-cleared.

### The handover (change 2), stated so it is not mistaken for done

**The C-TECH-064 live environment-state verifier is not written, and nothing in this review wrote it.** It authenticates to a live Dataverse environment, which [improvement-agent.md](../../agents/improvement-agent.md#L220) makes delivery work belonging under `provisioning/` — the folder governed by the 375-assertion script contract, where review 18 already shipped one live verifier that could never run.

What a delivery agent needs is entirely in [C-TECH-064's own `Verify By`](../../constraints/technology/technology-constraints.md#L134): the organisation switch and retention query, `EntityDefinitions(LogicalName='x')?$select=IsAuditEnabled` per entity folder under `Entities/`, option sets against `OptionSets/*.xml`, `fieldpermissions` against every `IsSecured=1` column, column-security profile **membership**, and `systemuserroles`. The table list is derived from disk, so it covers tables that do not exist yet.

**Rung 5 now reports the gap on every run of that gate — but that gate is itself wired into nothing.** `verify-constraint-verifiers.py` appears in no build config, no CI workflow and no constraint's `Verify By`; it runs only when somebody types it. [Section 5](#5-what-you-need-to-decide) claimed change 1 makes the condition "visible on every build", and that claim is **false as built**. It is the same defect as [IMP-0269](../../logs/improvement-log.jsonl#L266)'s second gap, in a second gate, and it was not in this review's approved scope to fix — wiring it as HARD would immediately block every build on C-TECH-064, which is a delivery decision, not a rules one.

---

## 10. What was held back, and why — cluster B

**Changes 4 and 5 were approved and are deliberately not on disk. Their premise was disproved by a parallel dispatch after this review was drafted and before it was applied, and building them would have enforced a rule that is false.**

### What the review proposed

`C-TECH-072` (HARD): *"A Web API call against a polymorphic metadata collection names the concrete derived type in the URI, not only in the request body"* — with [`scripts/verify-metadata-write-casts.py`](#3-proposed-changes) failing any metadata write under `provisioning/` whose URI targets `/Attributes(...)` without a `Microsoft.Dynamics.CRM.*AttributeMetadata` cast segment.

### What is actually true

[IMP-0273](../../logs/improvement-log.jsonl#L270), logged at 21:20 on 2026-08-24 — after this review was written, before the keyword arrived — **corrects** [IMP-0272](../../logs/improvement-log.jsonl#L269), and it did so by fetching Microsoft's own *Update a column* worked example rather than reasoning from the symptom. Column metadata updates are **`PUT` with the entire current object**, and the cast segment belongs on the **preparatory `GET` only**. It does not carry over to the write URI.

The live error text is the tell, and this review misread it: `"does not support http method 'PATCH'"` is a **verb** rejection. A wrong cast on this codebase's read side fails with a **404** — that is [the 404 trap](../../knowledge/technology/testing-tools.md#L238) already documented here. Two traps that read alike from the message alone, with different fixes.

### Why building it anyway would have been the expensive kind of wrong

**The corrected fix is already on disk and uses an uncast `PUT`.** [ensure-schema.ps1 step 3b](../../provisioning/dataverse/ensure-schema.ps1#L684) now `PUT`s the full object to `EntityDefinitions(LogicalName='<t>')/Attributes(LogicalName='<a>')` with no cast segment, per the fetched example. Change 5 as specified would have failed that line.

So the gate would have been **red against correct code**, and the only way to make it green would have been to restore the shape that already failed live on all five columns. This project has paid for that exact mistake twice in two days — the plurality gate reporting [a false privacy breach against legitimate code](../../constraints/technology/technology-constraints.md#L140), and [the derived-count gate](../../logs/improvement-log.jsonl#L266) whose correction would have overstated a privacy control. A HARD gate enforcing a false rule is worse than no gate: it is a standing instruction to write the defect back in.

### What was applied instead

**Change 6's slot, with the content the evidence supports.** [testing-tools.md L244](../../knowledge/technology/testing-tools.md#L244) now carries the write-side rule beside its read-side sibling — the three-step `GET`-cast / mutate / `PUT`-uncast shape, the two look-alike traps and how to tell them apart, and why `ensure-auditing.ps1`'s entity-level `PATCH` was a misleading precedent (it works; the entity and attribute endpoints are not the same shape). It closes by naming [`A-FIN-06`](../../docs/development/revitalise-grant-automation-dev-summary.md#L5881) as still open, so nobody reads it as confirmed.

**This is a knowledge line and not a constraint on purpose.** The contract flipped twice inside 24 hours and the corrected form is still at V1/V2 — no live run has confirmed the `PUT` yet. A rule written now would be written from a document, which is precisely what [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) was amended to stop.

### What this needs from you

**Nothing urgent, and one thing later.** The corrected wording is recorded in [IMP-0272's `revisit_when`](../../logs/improvement-log.jsonl#L269): once the reviewer's re-run confirms the `PUT` at V3, whoever re-observes it should decide whether *"`PATCH` is unsupported on `EntityDefinitions(...)/Attributes(...)`; update with a full-object `PUT` to the uncast URI"* has earned a constraint row. It will then be a confirmed platform law rather than a hypothesis, and the 3-per-review cap has room.

### The general lesson, which is about this agent and not about Dataverse

**A review's own diagnosis is a hypothesis with the same status as the finding's.** Review 23 established that rule in [how-to-log-an-improvement.md](../../skills/how-to-log-an-improvement.md#L110) and [section 1](#1-regression-check--did-the-last-reviews-changes-work) audited it as *"worked"* — while this review was, in cluster B, doing the thing the rule forbids: pattern-matching a live write failure onto a known read-side trap and proposing a HARD gate on the match. It was caught by re-reading the log before appending, which this review had itself committed to in [section 6](#6-findings-left-unprocessed) because a concurrent session had grown the log during the last review.

That habit is the only control that caught this. It is worth keeping for the same reason [the top of improvement-agent.md](../../agents/improvement-agent.md#L22) gives: this agent's output edits the rules every other agent obeys, and it is the least supervised output in the system.

---

## 11. Verification executed at application

**Level reached: V1 for everything written here, per [C-TECH-053](../../constraints/technology/technology-constraints.md#L108). No live environment was touched by any of it.**

| Check | Result |
|---|---|
| [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) `--selftest` | **16 fixtures, PASS** (5 new for rung 5) |
| Same, against the real tree | **exit 1** — reports C-TECH-064 and nothing else |
| [verify-derived-counts.py](../../scripts/verify-derived-counts.py) `--selftest` | **14 fixtures, PASS** (5 new for the scope selector) |
| Same, against the real registry | **exit 0**, 7 rows, the false drift gone |
| [verify-build-config.py](../../scripts/verify-build-config.py) | **PASS — 44 steps, 33 gates** |
| [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py) | **PASS** — re-run because rung 5 imports it |
| [verify-source-reader-plurality.py](../../scripts/verify-source-reader-plurality.py) | **exit 0**, 35 readers — IMP-0268's on-disk fix confirmed |
| `verify-improvement-log.py --check` | **OK** — 271 entries, 0 unread, 0 unread blockers |
| `generate-known-failure-modes.py --check` | **current**, 271 entries |
| `Invoke-Pester src/tests/build/` | **117 / 117 passed, 0 failed** |
| `Invoke-Pester src/tests/` (whole suite) | **875 passed, 0 failed, 1 skipped of 876** |
| Scoped vs unscoped derive, measured directly | **51 vs 67** |

**Not verified, and it is the honest limit of this application.** Nothing here made a live Dataverse call, so the three deferred findings' environment state is exactly as it was — unobserved by me. `ScriptContract.Tests.ps1` was not run because this review touched no file under `provisioning/`. Rung 5 proves a step is *executable*, never that anyone *ran* it. And `verify-constraint-verifiers.py` is itself wired into no build config, so rung 5's finding is only seen by someone who runs it by hand — stated plainly in section 9 because section 5 claimed otherwise.

---

## 12. What this application itself logged

**One new finding, [IMP-0275](../../logs/improvement-log.jsonl#L272), and it is about this agent rather than about Dataverse.**

Two of nine approved changes were disproved in the roughly two hours between this review reaching its gate and the keyword arriving. Nothing in [improvement-agent.md's activation step 8](../../agents/improvement-agent.md#L127) requires re-verifying a review's own evidence before applying it — *"on approval: apply the changes"* treats the proposals as settled once drafted. The only reason this was caught is a log re-read this review had committed to for an unrelated reason.

There is a compounding factor worth naming: the entry that invalidated the two changes, [IMP-0273](../../logs/improvement-log.jsonl#L270), arrived in state `reviewer-deferred` — the state [activation step 2](../../agents/improvement-agent.md#L104) correctly tells the agent to leave alone and merely report. That is right for scope and wrong for corrections. A finding carrying `corrects` against something a review is about to act on is load-bearing whatever its state, and **`corrects` is checked by nothing today** — which makes this a script rung rather than another paragraph, and it would have fired here.

[IMP-0273](../../logs/improvement-log.jsonl#L270) has also been stamped with `reviewed_in` naming this review. Its own deferral is unchanged: it was read and acted on, not closed, and the `PUT` it describes is still awaiting the reviewer's live re-run.
