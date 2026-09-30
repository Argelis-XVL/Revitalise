# Improvement Review — 2026-09-29 (1): the DEV intake revert, and the build it blocks

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 6 `NEW` → 4 clusters (4 unread, plus 2 logged by this review from what its re-measurement showed)
**Trigger:** deploy-lane blocker escalation ([routing.log L1069](logs/routing.log#L1069)). Its scope is every unread entry, so it is also the post-deploy batch owed after the DEV stage lines at [pipeline.log L237](logs/pipeline.log#L237) and [L241](logs/pipeline.log#L241)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT. Parked at the gate, nothing applied.~~ **APPLIED 2026-09-30, in the working tree, not committed.** `APPROVE IMPROVEMENTS` from Xander Lykopoulos, relayed by lead-agent. All three changes landed. Five entries are closed and one is deferred with a reason. One closure was narrowed at apply (§8). The designer-save question was not answered at approval and is recorded as unanswered.
**WBS:** system work, `wbs:system`. The findings come from the `wbs:4.2,4.3` intake deploy and the `wbs:6.8` build it blocks. No change here is billable.

---

## Summary

The build that carries the trustee portal's menu reorder is stopped by one critical finding: after a DEV import, the intake flow's field mapping was read back complete and then found gone twenty minutes later. This review keeps that finding in the halting category, because what broke was the live DEV flow. It corrects the finding's explanation, which the platform's own timestamps contradict, and proposes three reference-file edits. No new rule, gate or script.

**Waiting on you:** `APPROVE IMPROVEMENTS`. **The build stays blocked until the keyword is applied.** Recording this draft against the finding does not release the build. One question below, about the designer, would settle the cause. The keyword does not depend on the answer.

## What this review proposes

1. **A new section on reading live state after an import** ([build-and-deploy.md, after L194](knowledge/technology/build-and-deploy.md#L194)). Re-read a flow's live definition and its last-modified time just before claiming it is deployed. Explain any write that came after your import. Put platform times and log times on one clock before calling anything a cause. Treat an open designer tab as a risk during a live-fix import.

2. **Correct the stated import time and set a timeout that fits it** ([build-and-deploy.md L179](knowledge/technology/build-and-deploy.md#L179)). The file says an import takes 60–100 seconds. This solution now takes 4–6 minutes. A 3-minute client-side timeout cut off two imports today that went on to succeed on the server. The new line sets at least 600 seconds, and says a timeout on an import is resolved with a server-side query before anything is reported.

3. **Record that `pac env fetch` returns times in UTC with no zone marker** ([testing-tools.md, after L161](knowledge/technology/testing-tools.md#L161)). The logs are local time, and nothing on the page tells the two apart. Mixing them is what made the first explanation of the revert look right.

### Elements changed

| Element | Change |
|---|---|
| `knowledge/technology/build-and-deploy.md` step 4 | Import duration corrected to the measured 4–6 minutes; wrapper budget for `pac solution import` at least 600 s. The withdrawn figure is kept, struck through |
| `knowledge/technology/build-and-deploy.md` | New subsection *A live read is a snapshot: re-read it immediately before the V3 claim* |
| `knowledge/technology/testing-tools.md` → *Verifying live Dataverse state* | One paragraph: date-times come back in UTC, with no zone marker |

## What is still open

**The cause of the revert is not proven.** The explanation in the finding was that a failing platform job undid the mapping. The platform's own rows rule that out: both failed jobs happened before the check that saw the mapping intact, and the write that removed it had no job attached. The leading candidate is a save from a designer tab that was opened before the import. Nothing has tested that yet.

**A live-only defect has no fast release from the build block.** A delivery agent can release a build itself only when its fix lands in a file that ships. This defect was fixed by re-importing, with no source change, so only a review can release it. That is the design working as written. It is the first time it has been exercised, and it is noted here, not changed.

**The client-side timeout finding stays open.** It is only closed by an import that runs under the new budget. That cannot happen in this session.

**Two mechanical ideas are named and not proposed.** One is a check that every npm security advisory has its own triage note. The rule that exists caught both cases so far, and a check would stop the build the same way. The other is having the finding-id allocator stamp the real clock time on every entry. Both are recorded for the next batch (§2).

## What you need to decide

**1. Send `APPROVE IMPROVEMENTS`, as a resume to this agent, to release the build.**

**Problem** — The build that pushes the menu reorder to DEV halts at its first learning-log check while the critical finding is open. It is still open after this draft, because a finding a review is looking at still halts builds.
**Suggested fix** — Approve. On apply, the finding closes with the re-run the second DEV import already recorded, and the check passes.
**What happens if you don't** — Every build of this feature halts at step 5, including the one the menu reorder needs.
[verify-improvement-log.py L1636](scripts/verify-improvement-log.py#L1636)

---

**2. Did anyone save "REV | Intake | WordPress to Dataverse" in the designer on 29 September at about 20:30–20:35?**

**Problem** — The only write to the flow after the verified import was at 20:35 CEST. It was made under the same account the browser on this Mac signs in with, and an app publish in the maker portal ran four minutes earlier.
**Suggested fix** — Answer yes or no. Yes confirms the designer-tab cause, and the new section's "not proven" becomes a fact at the next batch.
**What happens if you don't** — Nothing breaks. The new section already covers both causes, but the next revert will be diagnosed from the same uncertainty.
[pipeline.log L238](logs/pipeline.log#L238)

---

Closing line: the queue check exits 1 before this draft and exits 1 after it, with the finding moved from "never looked at" to "waiting on this review" (§7). A simulation of the applied state exits 0 (§5). Live DEV was re-queried read-only three times through `pac env fetch`, and the npm audit was re-run. **Not verified:** the designer-save cause; whether the 600-second budget fits a real import; that the new knowledge text changes what the next deploy agent does.

---

## 0. Where this review departs from its findings and its brief, and why

**The blocker's explanation is contradicted by the platform's own timestamps, so this review corrects it and does not transcribe it.** IMP-0956 says `AsyncUpdateModernFlowPlugin` ("Async update of workflow") failed twice *during this same import* and then reverted the mapping. Re-queried read-only at about 22:35 CEST:

| What | Rendered by `pac env fetch` | CEST |
|---|---|---|
| Async update of workflow, **Failed** (ProcessStage does not exist) | 5:37 PM | 19:37, before any import that day |
| ImportSolution, first import | 6:05 PM → 6:10 PM | 20:05 → 20:10 |
| Async update of workflow, **Failed** (concurrent Delete) | 6:17 PM | 20:17, inside the idempotency re-run |
| PublishAllXml | 6:18 PM → 6:19 PM | 20:18 → 20:19 |
| Verification reads 81 of 81 keys ([L236–237](logs/pipeline.log#L236), stamped 18:23–18:25) | — | 20:23 → 20:25 |
| OnAppModulePublish (a maker-portal publish) | 6:31 PM | 20:31 |
| `workflow.modifiedon`, as IMP-0956 records it; mapping gone | 6:35 PM | 20:35 |
| ImportSolution, the retry | 7:29 PM → 7:34 PM | 21:29 → 21:34 |
| `workflow.modifiedon` now | 7:34 PM | 21:34, the retry itself |

The zone is fixed by the last two rows. The retry is logged as starting at 21:29 CEST ([L239](logs/pipeline.log#L239)) and committed at 21:52:45 +0200, and it renders as 7:29 PM, so `pac env fetch` renders UTC. The first dispatch stamped its log lines in UTC: commit `c20aa62` at 20:26:18 +0200 adds exactly the line stamped 18:25. **Both Failed rows come before the verification that read the mapping intact, and no async operation regarding this workflow exists at or near the 20:35 write.** The plugin cannot be what removed the mapping. The finding's other premise, that `modifiedby` = `svc_grantapplications` means "not a human", is contradicted by [code-apps.md L327](knowledge/technology/code-apps.md#L327). On this Mac the browser signs in as that account. Logged as IMP-0959 with `corrects: IMP-0956`. The timestamp mix itself is logged as IMP-0960.

**`defect_in: live:dev` is correct, and the lane stays `deploy`.** The brief asked whether it should be. The broken artefact was the live DEV flow definition, and `live:<env>` is the value that names one ([verify-improvement-log.py L588](scripts/verify-improvement-log.py#L588)). The corrected cause is still a write to live DEV. Re-labelling it to a knowledge path would lower the lane by misnaming the artefact, and that clears the build by making the gate see less. This review does not propose it.

**The proposed polling protocol is narrowed.** IMP-0956 proposed checking `asyncoperation` for the flow's jobs before any V3 claim, and IMP-0958 ran that as a 10-minute poll. The check stays as one step of four. It is no longer treated as the signal, because on the evidence the job it watches for was not the cause. The step that settles the question is comparing `workflow.modifiedon` with the import's completion, and that is one read.

**The import timeout is set to 600 seconds, not the finding's 400.** Two measured end-to-end imports are about 315 s and 325 s. At 400 s that leaves 23% margin on a solution that keeps growing. 600 s is about 1.8× the longest one. It still ends a real `pac` hang ten minutes in, where `pac`'s own limit would take 60 minutes ([pipeline.yml L113](config/revitalise-grant-automation-pipeline.yml#L113)).

**Parked entries are named, not re-derived.** IMP-0934 is a governance-lane blocker parked in `2026-09-27-improvement-review.md`. IMP-0855 is parked in `2026-09-23-improvement-review-7.md`. IMP-0298's warning concerns `2026-08-28-improvement-review-2.md`. Each needs its own keyword. None halts a build.

---

## 1. Regression check — did the last review's changes work?

The last review applied is [2026-09-28-improvement-review.md](docs/improvements/2026-09-28-improvement-review.md), applied 2026-09-29. Since then: two DEV imports, one build blocked, one build halted, and six findings plus this review's two.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Check 10, no zero-argument `createArray()` (row 1) | 2026-09-29 | `platform-contract-guessed-not-groundtruthed` | NO. Live intake flow reads 0 after both imports, matching source | Working |
| `fixes` field and its unprocessed-target warning (row 5) | 2026-09-29 | `two-recorded-lessons-contradict-each-other` | Exercised: the gate warned "IMP-0955: fixed by IMP-0957, and no review has processed it" | Working. It is what put IMP-0955 in this review |
| Trigger tag on every improvement-agent routing line (rows 6, 8) | 2026-09-29 | `learning-substrate-destroyed` | NO. Routing check 4: 0 untagged, 0 unknown, 0 mis-laned, of 1 dispatch | Working |
| Post-deploy batch after every stage line (review 7) | 2026-09-26 | `learning-substrate-destroyed` | **YES, prose half.** No batch followed the PARTIAL at [L237](logs/pipeline.log#L237); routing check 3 reports it | Reported, never halting. This review covers the same scope, so the gap closes here. No new rule: the tag check went live the same day and has not had a full cycle |
| build-agent's warning exception (row 11) | 2026-09-29 | `untriaged-tool-warning` | NO. The new npm advisory is a third-party tool warning, which the exception does not cover. build-agent blocked the build correctly under the Dev Summary rule | Working as scoped |
| Pre-state flow read, and `pac env fetch` as the Auto Mode route (rows 12, 14, 20) | 2026-09-29 | `live-verification-capability` | Exercised four times: two pre-states, the read that found the revert, this review's re-measurement | Working |
| `fixed_in_flight` discharge (review 4) | 2026-09-26 | `build-blocked-by-the-finding-it-remediates` | First exercise. pipeline-agent correctly declined to stamp it, because the fix left no needle in a shipped file | Working as designed. A live-only defect always needs a review to release a build. Noted, one instance, no change |

**Changes whose class recurred after a *prose* fix:** the post-deploy batch row. It is already escalated to a checked tag, and that check reported the miss, so a further escalation waits for a full cycle.
**Changes whose class recurred after a *gate*:** none.
**Closure evidence against level:** no entry closed by the last review has recurred.

---

## 2. Clusters and promotion decisions

Instance counts are re-derived from `class_instance_of` and the tree, not from the findings' prose.

```
CLUSTER: what a post-import live read proves  (x3: IMP-0956, IMP-0958, IMP-0959)
Altitude:   CLASS — the instance is "the async plugin reverted this flow". The property is
            "a live read is true when it was taken; a write after your import must be explained
            before you claim V3". It holds under either cause.
Ladder row: "one instance, general cause, a human needs to know it" → knowledge, plus a routed
            mechanical step (a script beats prose, but a live-authenticating script is delivery work)
Becomes:    build-and-deploy.md new subsection (row 1); routed: a DEV post_deploy step that re-reads
            every flow's clientdata and modifiedon and diffs it against source (§3.2)
Retires:    nothing
Cites:      IMP-0956, IMP-0958, IMP-0959
Residual:   the designer-save cause is unproven (decision 2). Until the routed step exists, the rule
            is prose read at pipeline-agent's activation step 2, not at the moment of the V3 claim.
            A revert after the stage line is written is invisible to any post-deploy step.
```

```
CLUSTER: client-timeout-misread-as-write-failure  (x1: IMP-0954)
Altitude:   INSTANCE, but its root cause is a stale figure in a knowledge file every deploy agent
            reads (60–100 s), so the fix is correcting that figure. Two timeouts in one day, and
            neither was misreported: both were resolved server-side
Ladder row: knowledge
Becomes:    build-and-deploy.md step 4 corrected; wrapper budget of at least 600 s (row 2)
Retires:    nothing
Cites:      IMP-0954
Residual:   nothing enforces the budget. The import is wrapped ad hoc by the agent, not by any
            config step (the DEV stage command is unwrapped). Deferred until an import runs under
            the new budget
```

```
CLUSTER: log-timestamp-not-taken-from-the-clock  (x1: IMP-0960)
Altitude:   INSTANCE, one knowledge line
Ladder row: knowledge
Becomes:    testing-tools.md: pac renders UTC with no marker; logs are local; quote the zone (row 3)
Retires:    nothing
Cites:      IMP-0960
Residual:   agents still type their own timestamps. Mechanical candidate for the next batch, not
            proposed here: allocate-improvement-id.py stamps a clock-taken recorded_at inside the
            lock it already holds. An ordering check would not help: the skewed lines are monotonic
```

```
CLUSTER: untriaged-tool-warning  (x1 NEW: IMP-0955, fixed by IMP-0957; class x18)
Altitude:   NOTE — no change. The rule caught it: build-agent blocked the build, development-agent
            added the Dev Summary row. Second npm-advisory instance (IMP-0700/0701 the first)
Ladder row: "a tool could catch it mechanically" is available and NOT taken. A check comparing
            npm audit advisory ids with the Dev Summary would block the build exactly as the rule
            did. It buys determinism, not cost. The broader form was rejected last review (IMP-0941)
Becomes:    nothing. IMP-0955 closes on a V2 re-run of the audit
Retires:    nothing
Cites:      IMP-0955
Residual:   the check is a candidate the first time an advisory reaches a packed artefact without
            its own triage row, which is the rule's failure the check would prevent
```

**Premises grepped at draft time.** IMP-0956's proposal was grepped against its target: `build-and-deploy.md` has no post-import re-read rule, so the gap is real. IMP-0954's premise that the wrapper prints its stray-process text "unconditionally" is partly false. [run-with-timeout.sh L94](scripts/run-with-timeout.sh#L94) prints it only when a `pac` binary is running. On this Mac that is almost always true, because VS Code bundles its own. The finding's conclusion survives. The 180 s figure traces to step 4's stale duration (60–100 s plus 20–45 s ≈ 145 s), which is why row 2 corrects the figure and does not just add a budget.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | `knowledge/technology/build-and-deploy.md` (insert after [L195](knowledge/technology/build-and-deploy.md#L195), before *Diagnosing a Failed Import*) | New subsection, text below | IMP-0956, IMP-0958, IMP-0959 | N/A — reference text | N/A |
| 2 | knowledge | `knowledge/technology/build-and-deploy.md` step 4 ([L179](knowledge/technology/build-and-deploy.md#L179)) | Duration corrected, old figure struck through; wrapper budget ≥ 600 s; a 124 on an import is resolved by a filtered `importjob` query | IMP-0954 | N/A — reference text | N/A |
| 3 | knowledge | `knowledge/technology/testing-tools.md` (after the paging note at [L161](knowledge/technology/testing-tools.md#L161), so the section's later "next paragraph" reference at L175 still points where it did) | One paragraph: UTC with no zone marker, measured; convert and label | IMP-0960 | N/A — reference text | N/A |

**Constraint budget:** 0 of 3 used.

**Row 1, the text to insert:**

```markdown
### A live read is a snapshot: re-read it immediately before the V3 claim

*Recorded 2026-09-29 (`IMP-0956`, its cause corrected by `IMP-0959`; `IMP-0958`).*

**Re-read a flow's live definition, and its `modifiedon`, immediately before you write a V3 claim
about it — not only once, straight after the import.** On 2026-09-29 the intake flow's
`Create_application` mapping read back complete (81 of 81 keys) after a DEV import and was gone
when the same field was read about twenty minutes later, with no further deploy logged.

1. **Compare `workflow.modifiedon` with your import's completion.** A later `modifiedon` means
   something wrote the flow after you did. Find out what before you claim anything about its content.
2. **Put every time on one clock first.** `pac env fetch` renders date-times in UTC with no zone
   marker, and `logs/` lines are local time (`testing-tools.md` → *Verifying live Dataverse state*).
3. **Read the flow's async jobs, but do not call a Failed one the cause without the clock check.**
   Query `asyncoperation` on `regardingobjectid` = the workflow id with a date bound. A Failed
   *"Async update of workflow"* row was first blamed for this revert; on one clock, both Failed rows
   came before the verification that read the mapping intact, and the write that removed it had no
   async job at all.
4. **Before a live-fix import of a flow someone is diagnosing in the designer, ask for that tab to
   be closed without saving.** A designer tab opened before the import, if saved afterwards, can
   write its old definition back. On this Mac the browser signs in as the same account `pac` uses
   (`code-apps.md`), so `modifiedby` cannot tell that save from an import. This is the leading
   candidate for the 2026-09-29 revert and it is **not proven**: the reverted content matched the
   reviewer's pre-import view of the flow exactly, which this cause predicts, and nothing has varied it.
```

**Row 2, step 4 becomes:**

```markdown
**4. Pack and import.** ~~A full clean import of a mid-sized solution takes **60–100 seconds**
plus 20–45s to publish.~~ *Withdrawn 2026-09-29 (`IMP-0954`): that figure dates from the first
DEV deployment.* **This solution now takes 4–6 minutes to import and publish**: 4m10s plus 1m05s
on 2026-09-27, about 5m25s end to end on 2026-09-29. **Anything that fails in under ~40 seconds
failed early, at a structural stage** — before the platform ever looked at your content.

**Give `pac solution import` a wrapper budget of at least 600 seconds.**
A `scripts/run-with-timeout.sh 180` wrapper killed the local `pac` twice on 2026-09-29 while the
import went on to succeed on the server. A 124 from the wrapper says nothing about the import:
resolve it with an `importjob` query filtered by `solutionname` and a date bound (*An unfiltered
`importjob` query can omit a live row*, below) before you report any outcome.
```

**Row 3, the paragraph:**

```markdown
**Date-times come back in UTC, with no zone marker.** Measured 2026-09-29: the `ImportSolution`
job for an import begun at 21:29 CEST reads `createdon` 7:29 PM. `logs/` lines are local time,
taken from `date` when the line is written. Convert before comparing the two, and write the zone
beside every platform time you quote. Mixing them put one dispatch's `pipeline.log` lines two
hours behind the next one's, and made a failed platform job read as the cause of a change it
preceded (`IMP-0959`, `IMP-0960`).
```

`evidence_grep` needles, each confirmed at apply to be one line of its file: row 1 `### A live read is a snapshot: re-read it immediately before the V3 claim` (IMP-0956) and `came before the verification that read the mapping intact` (IMP-0959); row 2 `Give \`pac solution import\` a wrapper budget of at least 600 seconds.` (for the deferred IMP-0954's record only); row 3 `**Date-times come back in UTC, with no zone marker.**` (IMP-0960).

### 3.1 Engine or client (skill §6)

All three rows are instance knowledge files, not engine files, and they carry this client's literals (flow name, service account) deliberately. The properties are platform facts and would be engine-level with the literals stripped. They stay client-specific for now: that is the skill's default when in doubt, and no second client has met them.

### 3.2 Routed work — handed on once this review lands

Re-measured at draft time; re-measured again at apply before anything is handed on.

| To | Item | From |
|---|---|---|
| development-agent | A DEV `post_deploy` step (and one per later environment that imports flows) that re-reads every flow's `workflow.clientdata` and `modifiedon` through `pac env fetch`. It diffs the definition against `src/solutions/RevitaliseGrantAutomation/Workflows/*.json` and fails when content differs, or when `modifiedon` is later than the import's completion. Read-only, no provisioning credential needed. pipeline-agent's rule 4 makes a declared step mandatory ([pipeline-agent.md L459](agents/pipeline-agent.md#L459)) | IMP-0956, IMP-0959 |
| reviewer | Decision 2 | IMP-0959 |

---

## 4. Retirements

> Retirement check performed: 87 live constraint rows, 10 retired (`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`, re-run at apply). None is made redundant: this review adds no constraint, gate or script. One text retirement is part of row 2: the "60–100 seconds" import duration is withdrawn in place and struck through, because it is the figure the 180-second wrapper came from.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0934, IMP-0855, IMP-0298, IMP-0961

None of the unread entries at draft time is unprocessed. The first three ids above are parked in other reviews (§0) and are cited only as context. IMP-0961 was logged by this review at apply time, after the draft was approved (§8). It is left unread for the next batch: it is not a blocker, and processing it here would apply something the reviewer has not seen.

**Dispositions, decided from each entry's `observable_at` (step 6's table):**

| Finding | Level | Disposition | Closure evidence |
|---|---|---|---|
| IMP-0956 | V3 | **CLOSE** → `APPLIED`, row 1 | `reobserved` V3: pipeline-agent's retry re-read the live definition after a 10-minute job poll, 81 of 81 keys, 0 value differences ([L241](logs/pipeline.log#L241)). Plus improvement-agent's read at apply that `modifiedon` is still the retry's own write |
| IMP-0959 | V3 | **CLOSE** → `APPLIED`, row 1 | `reobserved` V3: improvement-agent re-runs the two read-only queries at apply |
| IMP-0960 | V1 | **CLOSE** → `APPLIED`, row 3 | `evidence_grep` |
| IMP-0955 | V2 | **CLOSE** → `APPLIED`, no system change; the fix is the Dev Summary revision ([L11662](docs/development/revitalise-grant-automation-dev-summary.md#L11662)) | `reobserved` V2: improvement-agent re-runs `npm --prefix src/code-apps/trustee-review-portal audit --audit-level=high` at apply. At draft it lists exactly two advisories, both with their own Dev Summary row |
| IMP-0958 | V3 | **REJECT** — it records that the retry protocol worked and proposes no change. It serves as IMP-0956's re-observation, and its reading of the cause is corrected by IMP-0959. Precedent: IMP-0937, IMP-0953 | — |
| IMP-0954 | V3 | **DEFER from the start.** Row 2 lands, but only an import under the new budget re-observes it | `deferred_reason` at apply; `revisit_when`: *the next `pac solution import` runs under a wrapper budget of at least 600 s and either completes without a client-side 124, or its 124 is resolved by a filtered `importjob` query before any outcome is reported* |

**Simulated before parking.** In a scratch root (every top-level path linked to this repository except `logs/` and `knowledge/`, which are copies), with the dispositions above applied to the copied log and the three edits applied to the copied `knowledge/`, `verify-improvement-log.py --check` exits **0**: 0 deploy-open blockers, 0 unread, and the only warning is IMP-0298's, which belongs to another parked review. All five needles match exactly one line. The simulation never wrote to the real log; the only change to it is this draft's six `reviewed_in` stamps.

---

## 6. Digest impact

| | Before this review | Now (draft, regenerated) | After apply |
|---|---|---|---|
| Log entries | 954 | 956 (this review appended two) | 957 (IMP-0961 appended at apply, left unread) |
| Distinct lessons | 939 | 941 | 941, measured after regeneration (`--check` exit 0) |
| Recurring classes (x≥2) | — | unchanged in number: IMP-0959 makes `finding-diagnosis-unverified` x34; the two new classes are single | unchanged |
| Digest lines | — | 605 | 605 |

The digest was regenerated after the two appends (`generate-known-failure-modes.py --check` exits 0). `verify-derived-counts.py` reports 5 drifted claims, all pre-existing and none produced by this review. They are the `rev_setting` row count in the pipeline config (twice), two secured-column counts in the Dev Summary, and one in the REV Trustee role header. Each belongs to the agent that owns that file. It is a SOFT step and is reported, not fixed here.

**Apply-time obligation:** regenerate, run `--check`, then `verify-derived-counts.py`, and correct the generator's size sentence in both copies if it drifted.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-29-improvement-review.md

Findings processed: 6 NEW  →  4 clusters
Regression check:   7 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 3 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 3 left as notes
Digest:             regenerated at draft — 941 lessons, IMP-0959 joins a x34 class;
                    will regenerate at apply (IMP-0958 rejected)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Record of what is done on approval

**Keyword:** `APPROVE IMPROVEMENTS`, from Xander Lykopoulos (verbatim "Approve improvements", given after the draft was summarised to him), relayed by lead-agent as a resume, 2026-09-30 06:29 CEST ([routing.log](logs/routing.log)). **The designer-save question (decision 2) was not answered, and is recorded as unanswered.** The keyword did not depend on it.

**Re-verified before applying (step 8):**
- The queue had no new entries after the draft, and none carries `corrects` against a processed entry.
- Both target files were byte-identical to `HEAD`, and the sim copies were built from them.
- No import has run since 21:51 CEST.
- The three live reads were repeated and match the draft-time values. `modifiedon` is still the retry's own write.
- The routed flow-diff step still does not exist in the pipeline config (`grep clientdata|modifiedon` returns nothing).

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | `knowledge/technology/build-and-deploy.md`: new subsection *A live read is a snapshot*, before *Diagnosing a Failed Import* | working tree, uncommitted | IMP-0956 `APPLIED` (reobserved V3), IMP-0959 `APPLIED` (reobserved V3) |
| 2 | `knowledge/technology/build-and-deploy.md` step 4: duration corrected, old figure struck through, ≥ 600 s wrapper budget | working tree, uncommitted | IMP-0954 deferred with the approved `revisit_when`, verbatim |
| 3 | `knowledge/technology/testing-tools.md`: UTC paragraph after the paging note | working tree, uncommitted | IMP-0960 `APPLIED` |
| — | no system change | — | IMP-0955 `APPLIED`, **narrowed** (below); IMP-0958 `REJECTED` |

**NARROW-AND-REPORT: IMP-0955.** The draft said the re-run audit "lists exactly two advisories, both with their own Dev Summary row". Re-run at apply, 2026-09-30 06:33 CEST, it lists **14 GHSA ids, and exits 1** at `--audit-level=high` (5 vulnerabilities: 3 moderate, 2 high). The high ones are on `brace-expansion` and `undici`, all reached only through devDependencies. The lockfile is unchanged against `HEAD`, so the advisories were published overnight.
- **2 of the 14 are cited:** GHSA-3wwx-pv8p-q78v and GHSA-82fw-gwwq-j7x9. **12 are not.**
- The closure is narrowed to the one advisory this finding named, which is triaged. The other 12 are a new instance, logged as IMP-0961. The narrowing removes a claim that would now be false ("the audit is clean") and changes no rule.

**Consequence for the build this review was meant to release.** `improvement-log-check` now passes. The next build of this feature will then halt at the HARD `code-app-audit` step ([build.yml L740](config/revitalise-grant-automation-build.yml#L740)), because of the high advisories above. This review does not fix that. It is dependency maintenance, and it is routed below.

**Routed work, re-measured at apply and handed on:**

| To | Item | From |
|---|---|---|
| development-agent | **Before the menu-reorder build.** In `src/code-apps/trustee-review-portal`, run `npm audit fix` (non-force; npm reports a fix available for both high packages). Then re-run `npm audit --audit-level=high` and the unit tests, and add a Dev Summary §11 row for every advisory that remains | IMP-0961 |
| development-agent | The DEV `post_deploy` flow-definition re-read step, as in §3.2. Still absent | IMP-0956, IMP-0959 |
| reviewer | Decision 2, unanswered | IMP-0959 |

**Entries rejected:**

| Finding | Rejected because |
|---|---|
| IMP-0958 | It records that the retry protocol worked and proposes no change of its own. Its measurement is IMP-0956's re-observation, and its reading of the cause is corrected by IMP-0959 |

