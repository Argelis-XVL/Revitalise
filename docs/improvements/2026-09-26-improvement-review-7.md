# Improvement Review — 2026-09-26 (7): Group 2, the post-deploy batch and the production guard

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode, Group 2 only: WS-U (one batched improvement run after every deployment) and WS-V (production guard for governance findings)
**Authorising artefact:** [capability design, WS-U](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L176) and [WS-V](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L214). The reviewer's settled rows S-1 to S-5 are taken as given; Group 1 is taken as approved in [review 2026-09-26-4](docs/improvements/2026-09-26-improvement-review-4.md#L351) (D-1, D-3, D-9, D-10)
**Findings processed:** 3 NEW → 3 clusters (all three logged by this review from its own measurements; 14 unread entries outside the capability scope are named in section 5)
**Trigger:** reviewer request (capability mode)
**Gate:** `APPROVE IMPROVEMENTS`. Not sent with this dispatch, by design
**Status:** ~~DRAFT — parked at the gate, nothing applied~~ **APPLIED 2026-09-26 in the working tree, NOT committed** (reviewer: one commit after the whole plan). The authorisation record, the changes and the executed results are in section 8
**WBS:** `wbs:n/a`. System work on the rules, outside the contracted WBS, not billable (`C-COM-002`)

---

## Summary

Group 2 is buildable, and both halves were prototyped and run before this draft was written. **The post-deploy batch replaces a trigger that has never fired**: the rule "a finished feature goes to improvement-agent" has sat in three agent files since August, deploy summaries were committed 18 times this month, and not one improvement dispatch was ever routed on it. **The production guard needs one widening, not two.** Group 1's D-10 already stops any unfixed technical blocker in every environment, so the only gap left is a technical fix whose stamp nobody has reviewed yet.

Three decisions are waiting on you (D-2, D-4, and one new one about the batch-size rule), then `APPROVE IMPROVEMENTS`. Nothing has been applied.

## What this review proposes

1. **After every deploy, lead-agent runs one improvement batch in the background, and delivery carries on** ([processing triggers](agents/WORKFLOW.md#L401), [lead-agent routing](agents/lead-agent.md#L297)). The trigger is the pipeline stage line, which is written for every deploy, not the deploy summary, which pipeline-agent is only told to write after production. The routing line carries the tag `trigger:post-deploy` so a check can count it. Before routing, lead-agent also runs the post-deploy completeness audit that review 2026-09-26-3 handed on.

2. **One open batch review at a time.** If the last batch's review is still waiting for your keyword, the next deploy's batch adds a section to that same document instead of opening a second one. If the queue is empty, lead-agent writes a `SKIPPED` line instead of dispatching a strategic-tier agent to do nothing (1 of 21 deploy gaps this month logged no finding).

3. **A report-only check that shows a skipped batch** ([reconciliation check](scripts/verify-routing-reconciliation.py#L257)). It is a third check inside the routing-reconciliation step the build already runs. It never changes that script's exit code, even without `--warn-only`, so it cannot go HARD by accident when the dispatch check does.

4. **A production guard in the queue gate** ([gate triggers](scripts/verify-improvement-log.py#L1542)). A new `--target-env <env>` flag: when the environment is the last in the chain (`prd` here), the gate also fails on any open governance blocker and on any fixed-in-flight entry the reviewer has not reviewed or deferred. Earlier environments are never held. A misspelt environment name is a usage error, so `prod` cannot slip through as an early environment.

5. **The guard runs where production deploys run.** It becomes the first `pre_deploy` step of the `prd` block ([prd pre_deploy](config/revitalise-grant-automation-pipeline.yml#L2148)), which `run-deploy.py` executes mechanically, and pipeline-agent runs it before every stage. Placing it exposed that [pipeline-agent's step order](agents/pipeline-agent.md#L428) never mentions `pre_deploy` at all, so a hand-run deploy skips the steps the runner executes. That is fixed in the same change.

### Elements added

| Element | Where | Purpose |
|---|---|---|
| `--target-env <env>` and the production guard | `scripts/verify-improvement-log.py` (both copies) | holds open governance blockers and unreviewed fixed-in-flight entries before the last environment only |
| Check 3, post-deploy batch | `scripts/verify-routing-reconciliation.py` (both copies) | reports a deploy with no tagged batch after it; never changes the exit code |
| `trigger:post-deploy` routing tag, `SKIPPED:improvement-agent` line | `agents/lead-agent.md`, `agents/WORKFLOW.md` | makes a batch, or its deliberate skip, countable |
| `NEXT: improvement-agent (post-deploy batch)` line | `agents/pipeline-agent.md` gate outputs | hands lead-agent the queue size on every stage result |
| Guard step in `prd` `pre_deploy` | pipeline config and `config/pipeline.yml.example` | the mechanical enforcement point |

### Elements changed

| Element | Change |
|---|---|
| [C-TECH-061](constraints/technology/technology-constraints.md#L131) | gains the production-guard clause; Verify By names `--target-env <env>`. Additive, nothing withdrawn |
| "Feature completes" trigger row | replaced in WORKFLOW, lead-agent and improvement-agent; withdrawn wording retained |
| pipeline-agent step order | `pre_deploy` inserted between the prerequisites and the deploy command |
| Two templates | review trigger vocabulary; deploy summary records the guard result and the queued-findings count |

## What is still open

**The batch-size rule keeps halting builds, and this review recommends keeping it.** The design's fifth WS-U requirement assumed it had already been made non-fatal; it was not ([withheld 2026-08-31](docs/improvements/2026-08-31-improvement-review-8.md#L188)). At today's floor of 45 it has halted no build since it became adaptive on 2026-09-11, and under the new trigger it becomes the only mechanical backstop if batches are skipped. The one real risk is a batch review left without a keyword across about three deploys. That is decision D-U1 below.

**The new check will make a skipped batch visible; it will not make it happen.** It lives in a SOFT step whose output already carries 176 unreconciled dispatches, so its separate summary line is the part a reader will actually see. The effective prompts are pipeline-agent's `NEXT:` line, which lead-agent reads in every gate output, and the batch-size rule behind it.

**The guard has never met a production deploy, because none has happened.** All 60 stage lines in the deploy log are DEV, TST/ACC or config. So the guard is proven only by its fixtures and a clean run on today's log (V1). The first `APPROVE PRD` dispatch is its first real exercise.

**Two sibling drafts edit the same files.** Review 2026-09-26-5 (work board and intake) and review 2026-09-26-6 (close-out loop and typed evidence) both touch `pipeline-agent.md`, `lead-agent.md`, `WORKFLOW.md` and the deploy summary template. The plan of application anchors every edit on a heading or a quoted sentence, never on a line number.

## Measurements

### Premises re-measured

| Group 2 premise | Design said | Measured 2026-09-26 | Verdict |
|---|---|---|---|
| The new trigger keys on "every pipeline-agent Deployment Summary" | yes | pipeline-agent is told to write one only after production ([Stage 3](agents/pipeline-agent.md#L520)); no production deploy has happened. Summaries were written on DEV deploys by habit (18 commits since 2026-09-01) | **false as a key** — the stage line is written for every stage and is used instead |
| The existing "feature completes" trigger works | implied | 0 of 142 improvement-agent dispatches name it; the dispatch-share report has no category for it | **never fired** |
| WS-I made the batch rung non-fatal (WS-U requirement 5) | yes | withheld 2026-08-31; the rung exits 1 (executed by Group 1) | **false** — decision D-U1 |
| Batch scope includes "every governance blocker" (WS-U requirement 1) | yes | a governance blocker already parked in another review would be re-derived, which improvement-agent's activation step 2 forbids | **narrowed** to unread plus unreviewed fixed-in-flight entries |
| `config/pipeline.yml.example` is an engine file | yes | it is an instance file; `git -C .engine ls-files` lists no pipeline example | **false** — edited in the instance |
| pipeline-agent has a pre-flight where the guard plugs in | yes | its pre-deploy constraint check covers C-TECH-061 (scope includes pipeline-agent), so amending that row's Verify By is the hook; but its step order omits `pre_deploy` | holds, with one defect fixed |
| The guard must cover governance blockers only | yes | with D-10, open deploy blockers already fail everywhere; fixed-in-flight entries pass everywhere, production included | **widen by one state** — decision D-2 |

### What the new trigger costs

| Window | Deploy episodes | Improvement-agent routings in the same window |
|---|---|---|
| 2026-09-01 → 26 | 22 (29 stage lines; bursts under two hours merged) | 51 |
| 2026-09-15 → 26 | 9 | 33 |

An episode is the stage lines of one feature less than two hours apart: a retry burst, or two builds deployed within the hour. Four episodes this month had more than one line, and each is one batch's worth of work (two quick redeploys, two failed attempts, a five-line retry burst, a failed build and its fix). The batch count is well under the routings that already happen. 22 of the 33 routings since 2026-09-15 were the blocker rung, which Group 1 now narrows (7 were capability work, 1 the batch rung, 3 other).

Findings logged between consecutive deploys since 2026-08-20: median **6**, mean **14.9**, and **4 of 51** gaps reached 45, all of them multi-day gaps with no deploy.

### The two prototypes, executed

Both changes were built on scratch copies of the current working-tree files and run. The exact text is in the appendices.

| Check | Result |
|---|---|
| Queue gate `--selftest` | **99 of 99** pass (the existing 89 plus 10 guard fixtures) |
| Guard mutation proof | removing each piece in turn fails a named fixture: fixed-in-flight holding, the no-chain fail-safe, the misspelt-environment check, governance holding, the reviewer-deferral release |
| Guard on the real log | `prd`, `dev`, `tst_acc` exit 0; `prod` exits 2. **0 held, and 0 is correct:** no open blocker carries `defect_in` yet, all 59 open blockers are reviewer-deferred, and none is fixed in flight |
| Plain `--check` on the real log | exit 0, unchanged |
| Reconciliation `--selftest` | pass, with 10 new check-3 cases; five mutations each fail one |
| Check 3 on the real logs, default cutover | **0 findings, and 0 is correct**: no deploy has happened since the cutover date |
| Check 3 with the cutover moved to 2026-09-01 (a design measurement, not a proposal) | **22 episodes, 22 without a batch, 0 covered.** Each was read against the log: every one is a real deploy episode, and none was followed by a batch, because the tag did not exist. HELD and CONFIG lines were correctly left out |
| Check 3 and the exit code | without `--warn-only` the script still exits 1 only for its first check's 176 unreconciled dispatches, exactly as before |
| Pipeline config with the guard step | `verify-pipeline-config.py` PASS, 126 steps (was 125), the new script path resolved |

## What you need to decide

These are grouped by workstream. D-U1 does not depend on the other two. D-2 and D-4 are the design's own open decisions.

---

**D-2. Adopt the production guard, widened to hold unreviewed fixed-in-flight entries as well?**

**Problem** — A technical fix stamped in flight passes the gate in every environment, production included, and the stamp is a claim the gate cannot check (who ran the re-run, and whether it passed).
**Suggested fix** — Yes: before the last environment only, hold open governance blockers and fixed-in-flight entries until you review or defer them; unfixed technical blockers need no clause because D-10 already stops them everywhere.
**What happens if you don't** — With the design's wording, an unreviewed in-flight fix to a special-category-data flow can reach production. Without the guard at all, every governance finding waits indefinitely, production included.
[design, D-2](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L483)

---

**D-4. Run the post-deploy batch alongside delivery, extending one open review, and skip it when the queue is empty?**

**Problem** — A batch the next build must wait for brings back the block this design removes, and a second review opened while the first waits doubles your keywords.
**Suggested fix** — Yes: dispatch in the background, extend the parked batch review instead of opening another, and log `SKIPPED` rather than dispatch when there are no unread or unreviewed fixed-in-flight entries.
**What happens if you don't** — Either each deploy waits for a keyword, or you receive one review per deploy (9 in the last eleven days). Without the skip, the design's literal "exactly one run" dispatches a strategic-tier agent to find nothing.
[design, D-4](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L490)

---

**D-U1 (new). Keep the batch-size rule as a build halt, and withdraw WS-U requirement 5?**

**Problem** — The design assumed this rule had already been made non-fatal; it was withheld on 2026-08-31 because it is the only pressure on an unprocessed queue.
**Suggested fix** — Keep it: it has halted no build at the current floor, and it is the one mechanical backstop if post-deploy batches get skipped. The alternative is to count only entries no review has looked at yet, so a review waiting for your keyword never halts a build.
**What happens if you don't** — If you choose the alternative, a batch review can wait any length of time without consequence before production, where the guard still stops it. If you keep the rule, a review left without a keyword for about three deploys (at 15 findings per deploy on average) will halt the next build until you answer it.
[review 8, withheld](docs/improvements/2026-08-31-improvement-review-8.md#L188)

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Group 1: blocker lanes, fixed-in-flight, threshold pointers ([review 2026-09-26-4](docs/improvements/2026-09-26-improvement-review-4.md#L373)) | 2026-09-26, working tree | `build-blocked-by-the-finding-it-remediates`, `hand-maintained-count-drifts-from-source` | not measurable: no build or deploy has run since (last build 2026-09-25 17:26, last deploy 20:06) | too early to call; leave alone |
| WS-X: post-deploy completeness gate ([review 2026-09-26-3](docs/improvements/2026-09-26-improvement-review-3.md#L282)) | 2026-09-26, working tree | `pipeline-dispatch-stops-before-declared-post-deploy` | not measurable, same reason. Its `--audit` run today: 0 findings over 0 stage lines since its cutover | too early to call |
| WS-Z: per-section digest reads ([review 2026-09-26-2](docs/improvements/2026-09-26-improvement-review-2.md)) | 2026-09-26 | read-path cost | not measurable | too early to call |
| WS-W1: work-item ledger ([review 2026-09-26](docs/improvements/2026-09-26-improvement-review.md)) | 2026-09-26 | capability, no class | n/a | nothing to audit |

**Changes whose class recurred after a prose fix:** none measurable yet.
**Changes whose class recurred after a gate:** none.

This review's own finding on the "feature completes" trigger is a recurrence of `declared-policy-not-mechanically-enforced` against a prose rule, and it is escalated to a tagged routing line plus a report-only check, not to more prose.

---

## 2. Clusters and promotion decisions

```
CLUSTER: WS-U — one batched improvement run after every deployment  (x1: IMP-0913)
Altitude:   ENGINE. Nothing names this client: the trigger reads the stage-line format pipeline-agent
            writes everywhere, and the environment chain comes from instance.yaml
Ladder row: "a tool could catch it mechanically" (the skip) + "the order of steps was wrong" (the
            trigger keyed on an artefact produced only after production)
Becomes:    WORKFLOW Processing-triggers row; lead-agent "After every pipeline result" sequence (with
            the WS-X --audit hand-on); improvement-agent post-deploy batch mode; pipeline-agent NEXT
            line; review template trigger value; verify-routing-reconciliation.py check 3 (report only)
Retires:    the "feature or phase completes" trigger row, in three agent files, withdrawn wording kept
Cites:      IMP-0913; design WS-U requirements 1-7 (1 narrowed, 5 withdrawn per D-U1)
Residual:   the batch is still a prose trigger. Check 3 reports a skip inside a SOFT step whose output
            is already noisy; the batch-size rule is the only thing that eventually forces it. The
            stage line is the key, so a deploy recorded without a [PIPELINE] stage line (a reviewer
            running pac by hand, say) triggers nothing and is reported by nothing
```

```
CLUSTER: WS-V — production guard  (x1: IMP-0914)
Altitude:   ENGINE mechanism (the last element of environment_chain), INSTANCE data (the chain and
            the prd pre_deploy step)
Ladder row: "a tool could catch it mechanically"; IMP-0914 is "two invocation paths disagree", fixed
            at the prose path because the runner is already right
Becomes:    verify-improvement-log.py --target-env and the guard; C-TECH-061 clause and Verify By;
            prd pre_deploy step (pipeline config and example); pipeline-agent Stage 3 and step order
Retires:    nothing
Cites:      IMP-0914; design WS-V requirement and D-2
Residual:   the guard reads the log, never the live environment. It trusts defect_in for the lane,
            so a deploy defect mis-tagged as governance is held at production and nowhere earlier,
            which is the design's intended backstop. A production promotion done in the Pipelines UI
            without run-deploy.py or pipeline-agent never runs the step at all
```

```
CLUSTER: design premises that failed re-measurement  (x1: IMP-0915; class finding-premise-fails-re-measurement)
Altitude:   INSTANCE — three readings of this repository in one design document
Ladder row: "one instance, specific, no general mechanism" → an erratum where the wrong claim is written
Becomes:    an erratum under WS-U and WS-V in the capability design
Retires:    nothing
Cites:      IMP-0915 (a fourth premise is already IMP-0905)
Residual:   nothing checks a design document's premises; the draft-time premise grep is the control,
            and it caught all three here
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-improvement-log.py` + `.engine/` copy, byte-identical | `load_environment_chain()`; `check_triggers(..., target_env)`; production guard holding open governance blockers and fixed-in-flight entries without a `deferred_reason`, at the last environment only, fail-safe to "every target" when no chain is declared; `--target-env` implies `--check`; an environment not in the chain exits 2. Text: Appendix A | WS-V, D-2, IMP-0914 | YES — `python3 scripts/verify-improvement-log.py --selftest` (99 fixtures); `--target-env prod` exits 2 | already wired — HARD [`improvement-log-check`](config/revitalise-grant-automation-build.yml#L80) runs `--check` unchanged; the guard runs from change 10's `pre_deploy` step and pipeline-agent's constraint check |
| 2 | script | `scripts/verify-routing-reconciliation.py` + `.engine/` copy, byte-identical | Check 3: every deploy episode (SUCCESS, PARTIAL or FAILED stage lines of one feature under two hours apart, environments from `environment_chain`) needs a `trigger:post-deploy` routing line (ROUTED_TO, RESUMED, RE-DISPATCHED or SKIPPED, naming improvement-agent) before that feature's next episode. Report only; never changes the exit code. `POST_DEPLOY_REQUIRED_FROM` set to the apply date. Text: Appendix B | WS-U.7, IMP-0913 | YES — `python3 scripts/verify-routing-reconciliation.py --selftest` | already wired — SOFT (`--warn-only`) at [`routing-reconciliation`](config/revitalise-grant-automation-build.yml#L134) |
| 3 | constraint-amendment | `constraints/technology/technology-constraints.md` | C-TECH-061 gains: *before a deploy to the last environment of `instance.yaml` → `environment_chain`, additionally no `governance`-lane blocker in `unread` or `awaiting-approval`, and no `fixed-in-flight` entry without a reviewer's `deferred_reason`*. Verify By adds `python3 scripts/verify-improvement-log.py --check --target-env <env>`, run before every stage. Nothing withdrawn | WS-V, D-2 | YES — the command above | N/A |
| 4 | agent | `agents/WORKFLOW.md` | Processing triggers: the "feature or phase completes" row becomes "every pipeline-agent stage result — SUCCESS, PARTIAL or FAILED, any environment — one post-deploy batch, in the background, alongside the next delivery dispatch", withdrawn wording retained; the governance row's "feature completes" becomes "the post-deploy batch"; one sentence naming the production guard | WS-U.1–3, WS-V, IMP-0913 | N/A — instruction change | N/A |
| 5 | agent | `agents/lead-agent.md` | Routing table row as in change 4; new subsection *After every pipeline result — the post-deploy sequence*: close the pipeline `ROUTED_TO`; run `verify-post-deploy-completeness.py config/<slug>-pipeline.yml --audit` and report exit 1 as a wrong status word; run the queue gate; if unread and unreviewed fixed-in-flight are both 0, log `SKIPPED:improvement-agent — trigger:post-deploy, queue empty`; if a post-deploy batch review is parked, resume or re-dispatch to extend it; if one is still running, wait for it to park; otherwise dispatch in the background; the next delivery dispatch may go in parallel. "Run it BEFORE dispatching" gains: before dispatching pipeline-agent, run the gate with `--target-env <env>` | WS-U.1–4, WS-X hand-on, D-4 | N/A — instruction change | N/A |
| 6 | agent | `agents/improvement-agent.md` | Activation-trigger row as in change 4; a *Post-deploy batch mode* paragraph: scope is unread entries plus fixed-in-flight entries no review has processed, while entries parked in another review are named, not re-derived; extend an open batch review under *Amending a draft* (gate block first, note last); header `**Trigger:** post-deploy batch`; fixed-in-flight dispositions follow the `observable_at` table, and the deploy that shipped the fix is usually the re-observation | WS-U.1, WS-U.4, IMP-0915 | N/A — instruction change | N/A |
| 7 | agent | `agents/pipeline-agent.md` | *Executing an Environment Block*: `pre_deploy` inserted after the prerequisites, before `deploy_command`; Stage 3: run `verify-improvement-log.py --check --target-env prd` beside the rollback check, and a non-zero exit halts with the ids it names; the Stage 1, Stage 3 and Deployment Failure output blocks end with `NEXT: improvement-agent (post-deploy batch) — <n> findings queued`, n being unread plus fixed-in-flight from the gate's census | WS-U.6, WS-V, IMP-0914 | N/A — instruction change | N/A |
| 8 | template | `templates/improvement-review-template.md` | Trigger vocabulary: `feature completion` becomes `post-deploy batch` | WS-U | N/A — template text | N/A |
| 9 | template | `templates/deployment-summary-template.md` | Under Environment Results: a line recording the production-guard command and exit for the last environment; under Findings Logged: `Findings queued for the post-deploy batch: <n>` | WS-U.6, WS-V | N/A — template text | N/A |
| 10 | other | `config/revitalise-grant-automation-pipeline.yml` | First `prd` `pre_deploy` step: `python3 scripts/verify-improvement-log.py --check --target-env prd`, described as the production guard. Lands after change 1, or the step exits 2 on an unknown flag | WS-V | YES — `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` (measured PASS, 126 steps) | N/A |
| 11 | other | `config/pipeline.yml.example` | The same step in its `prd` `pre_deploy` list, with `prd` written as the last element of `environment_chain` | WS-V, IMP-0915 | N/A — example file | N/A |
| 12 | other | `docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md` | Erratum under WS-U and WS-V, headed *Erratum (improvement review 2026-09-26-7)*: the trigger keys on the stage line; requirement 1's scope is narrowed; requirement 5 is withdrawn or kept per D-U1; the example file is an instance file | IMP-0915 | YES — needle grep | N/A |

**Constraint budget:** 0 of 3 used (one amendment, which the cap does not count).

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows and 10 retired, derived with the struck-id grep. None is redundant: C-TECH-061 is amended, and no other row speaks to improvement triggers or production promotion of findings.

The design's retirement candidate 1 is retired here, in prose rather than in `constraints/`: the "feature or phase completes → improvement-agent after the Deployment Summary" trigger. The sweep, run with a positive control that returned its hit:

```
grep -rn -i "feature or phase complete\|feature completes\|after the Deployment Summary\|feature completion" .engine/agents/ .engine/templates/ .engine/skills/ constraints/ CLAUDE.md scripts/*.py loops/ config/*.yml knowledge/ .engine/scripts/ .claude/agents/
.engine/agents/lead-agent.md:303          instruction  → change 5
.engine/agents/improvement-agent.md:49    instruction  → change 6
.engine/agents/WORKFLOW.md:405            instruction  → change 4
.engine/agents/WORKFLOW.md:409            instruction  → change 4
.engine/templates/improvement-review-template.md:5   instruction → change 8
```

Candidate 2 (the self-deferral sentence) was handled by Group 1.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901, IMP-0902

| Finding | Why not processed here | Revisit when |
|---|---|---|
| The 14 unread entries above | Capability mode: this review is authorised by the design and scoped to Group 2. None is a blocker, and the queue gate exits 0 | the first post-deploy batch once this lands |

Entries appended by sibling drafts (IMP-0908 to IMP-0912) and the awaiting-approval entry IMP-0855 are left to the documents they name.

---

## 6. Digest impact

| | Before this review | After appending (regenerated) | After apply (predicted) |
|---|---|---|---|
| Log entries | 908 | 911 | 911 |
| Distinct lessons | 899 | 902 | 902 |
| Recurring classes (x≥2) | 70 | 70 | 70 |

This review's three findings are already in the digest, regenerated after appending, validator first. All three join existing classes. Sibling drafts are appending to the same log, so the figures are re-derived at apply time, never retyped.

---

## Plan of application

Written now so the apply step is mechanical. Everything is re-verified against the tree before it is edited (activation step 8).

1. **Working tree only. No commit and no push, in either repository.** The reviewer's instruction, verbatim: *"Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."* Engine files (`agents/`, `templates/`, `.engine/scripts/`) are edited in the `.engine` working tree, instance files in the instance working tree. The single commit that follows is the reviewer's, after every group.
2. **Preconditions.** Group 1 is in the working tree (review 2026-09-26-4, its Applied section). WS-X change 2 (pipeline-agent *Logging*) appears to be present in the working tree already, and it is re-checked, not assumed. Sibling drafts -5 and -6 edit `pipeline-agent.md`, `lead-agent.md`, `WORKFLOW.md` and the deploy summary template: whichever applies later re-reads each file immediately before editing it and anchors on headings and quoted sentences.
3. **Order.** (a) Both script pairs from Appendices A and B. Before patching, check the working-tree sha1 of `scripts/verify-improvement-log.py` against the base the diff was made on (prefix `1a8b028c3d2d`); if it moved, re-apply by hunk and re-run the fixtures, never force the patch. Copy each result to `.engine/scripts/` and confirm `cmp`. Set `POST_DEPLOY_REQUIRED_FROM` to the apply date. (b) `--selftest` for both; the queue gate on the real log with `--check`, and with `--target-env prd`, `dev` and `prod`. (c) Only then the pipeline config step (change 10) and the example (change 11). (d) C-TECH-061, then the four agent files, the two templates, and the erratum.
4. **Bookkeeping as each change lands** (all three are V1 or n/a, so all three close):

   | Entry | `observable_at` | Disposition | Needle |
   |---|---|---|---|
   | IMP-0913 | V1 | CLOSE | `agents/WORKFLOW.md` contains `trigger:post-deploy` |
   | IMP-0914 | V1 | CLOSE | `agents/pipeline-agent.md` contains ``1a. `pre_deploy` — after the prerequisites`` (the new step-order line; grep it to one line before writing the needle) |
   | IMP-0915 | n/a | CLOSE | the design contains `Erratum (improvement review 2026-09-26-7)` |

   **Simulated before parking.** The three closures, with these needles planted in scratch copies of the three target files, were run through `verify-improvement-log.py --check` against a scratch log on a scratch tree: exit 0, no error or warning on any of the three. The real log was never written by the simulation.

5. **Closing checks:** `verify-improvement-log.py --check` and `--selftest`, `verify-routing-reconciliation.py --selftest`, `verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml`, `verify-engine-instance-split.py`, `verify-build-config.py config/revitalise-grant-automation-build.yml`, `generate-known-failure-modes.py --check`, `verify-derived-counts.py`, `verify-doc-line-links.py`, `verify-review-document.py`, `verify-class-defences.py`, `validate-instance.py`. No new `verify-*.py` script, so the registered script count does not move.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-7.md

Findings processed: 3 NEW  →  3 clusters
Regression check:   4 prior changes audited, 0 classes recurred (none measurable yet)
Proposed:           0 constraints (cap 3), 1 constraint amendment, 2 gates/scripts,
                    0 skill/knowledge edits, 4 agent-file edits, 2 template edits, 3 other,
                    1 retirement (the "feature completes" trigger row, prose)
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 902 lessons, 70 recurring classes
Decisions open:     D-2, D-4, D-U1 (new)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

Verification: both prototypes run on scratch copies — the queue gate's 99 fixtures pass and five mutations each fail a named fixture; the reconciliation selftest passes and five mutations each fail; the guard holds nothing on today's log, and 0 is correct; check 3 reports 0 at its cutover and 22 of 22 real episodes over a moved window; the pipeline config passes with the new step. **Not verified:** no production deploy has run the guard, and no deploy has yet been followed by a tagged batch. Both are the first live exercises (V3), and nobody in this session can make them.

---

## 8. Applied

**Authorisation, recorded before any change** (`agents/WORKFLOW.md` → "What channel a keyword must arrive through"):

| Field | Value |
|---|---|
| `authorised_by` | Xander Lykopoulos (the reviewer; git user Xander Lykopoulos) |
| `relayed_by` | lead-agent, quoted verbatim from the reviewer's own conversation turn in the commissioning session |
| Keyword, verbatim | "Du1 agreed alternative / D2 agreed / D4 agreed / Approve improvements group 2" |
| Recorded | 2026-09-26 21:14, before the first edit |
| Artefacts this act produces | changes 1–12 of section 3, as amended by the decisions below, and the bookkeeping in the plan of application |

All four relay conditions hold: the relay comes from lead-agent, carries the keyword verbatim, names the human, and says it is quoted from that session's own turn.

**The decisions as applied:**
- **D-U1: the alternative.** The batch-size rule stays a build halt, but it counts only entries no review has looked at yet: `unread` entries, plus `fixed-in-flight` entries whose `reviewed_in` names no existing review. An `awaiting-approval` entry, and a fixed-in-flight entry a review has processed, is reported and not counted. WS-U requirement 5 is withdrawn.
- **D-2: yes, widened.** Before the last environment only, the guard holds open governance blockers and fixed-in-flight entries with no reviewer `deferred_reason`.
- **D-4: yes.** The batch runs alongside delivery, extends one open batch review, and is skipped when the queue is empty.

**Re-verified before applying (step 8).** Queue gate exit 0. No entry appended since the draft carries `corrects` naming IMP-0913, IMP-0914 or IMP-0915; IMP-0916 (a sibling's finding about the `corrects` warning) touches nothing here. Both scripts were still at the base the appendices were diffed against (sha1 prefixes `1a8b028c3d2d` and `bf5fa5130d45`, instance and engine identical). Every other file was re-read immediately before its edit. Reviews -5 and -6 are unapproved and nothing of theirs is in the tree.

**Not committed, per the reviewer's instruction** ("Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."). No git write command was run in either repository.

| # | Change | Applied at (working tree) | Entries moved |
|---|---|---|---|
| 1 | Production guard (`--target-env`, `load_environment_chain()`, D-2 widening with the reviewer-deferral release), **plus the D-U1 narrowing of the batch rung** and its docstring line | `scripts/verify-improvement-log.py` + `.engine/scripts/verify-improvement-log.py`, byte-identical | — |
| 2 | Check 3, post-deploy batch, report only; `POST_DEPLOY_REQUIRED_FROM = "2026-09-26"` | `scripts/verify-routing-reconciliation.py` + `.engine/scripts/verify-routing-reconciliation.py`, byte-identical | IMP-0913 → APPLIED (with 4–6) |
| 3 | C-TECH-061: batch clause per D-U1 (withdrawn wording retained), production-guard clause, Verify By adds `--target-env <env>` | `constraints/technology/technology-constraints.md` | — |
| 4 | Processing triggers: post-deploy row, D-U1 batch row, governance row names the guard; withdrawn wording retained | `agents/WORKFLOW.md` | (IMP-0913) |
| 5 | Routing table row; `--target-env` before dispatching pipeline-agent; *After every pipeline result — the post-deploy sequence* (incl. the WS-X `--audit` hand-on) | `agents/lead-agent.md` | (IMP-0913) |
| 6 | Trigger rows (post-deploy, D-U1 batch wording); *Post-deploy batch mode* paragraph | `agents/improvement-agent.md` | (IMP-0913) |
| 7 | `1a. pre_deploy` in the environment-block order; Stage 3 production guard; `NEXT:` line on Stage 1, Stage 3 and failure outputs | `agents/pipeline-agent.md` | IMP-0914 → APPLIED |
| 8 | Trigger vocabulary `post-deploy batch` | `templates/improvement-review-template.md` | — |
| 9 | Production-guard line; findings-queued line | `templates/deployment-summary-template.md` | — |
| 10 | Guard as the first `prd` `pre_deploy` step (landed after change 1) | `config/revitalise-grant-automation-pipeline.yml` | — |
| 11 | Guard step in the example `prd` `pre_deploy` | `config/pipeline.yml.example` | — |
| 12 | Errata under WS-U (three corrections, requirement 5 withdrawn per D-U1) and WS-V | capability design | IMP-0915 → APPLIED |

**Deviation, and why — D-U1's exact scope.** The approved alternative reads *"count only entries no review has looked at yet"*. The relay glossed it as *"(unread)"*. Applied literally: `unread` **plus** `fixed-in-flight` entries whose `reviewed_in` names no existing review, because a stamped fix that no review has yet read is exactly "an entry no review has looked at", and counting only `unread` would let stamped fixes accumulate without any pressure at all. An `awaiting-approval` entry, and a fixed-in-flight entry a review has already processed, is reported and not counted. Fixture `batch-trigger-du1-reviewed-fixed-in-flight-not-counted` and the pre-existing `fif-e-counted-toward-the-batch` pin both halves. If "unread only" was meant, it is a one-line change: drop `unreviewed_fixed` from `pending`. **One existing fixture's expected text was updated** (`fif-e-counted-toward-the-batch`) because the trigger message now says "not yet in any review"; its asserted exit code and count are unchanged.

**Executed results (after applying):**
- `verify-improvement-log.py --selftest`: **101 of 101** fixtures (the 89 existing, 10 guard, 2 D-U1). Mutations: counting awaiting entries again, counting reviewed fixed-in-flight entries, and dropping fixed-in-flight entirely each fail a named fixture. The five guard mutations were run on the prototype.
- `--check`: exit 0. `--target-env prd`, `dev`, `tst_acc`: exit 0 (the guard is clear for `prd`, not applicable to the other two). `--target-env prod`: **exit 2**.
- `verify-routing-reconciliation.py --selftest`: pass, including the 10 check-3 cases. Build form (`--warn-only`): exit 0, check 3 reporting `0 deploy episode(s) with no batch … since 2026-09-26 (38 earlier episode(s) out of scope)`. Without the flag the exit code is still 1, only because of check 1's pre-existing 176 unreconciled dispatches.
- `verify-pipeline-config.py`: PASS, 126 steps. `run-deploy.py --selftest`: PASS. `verify-post-deploy-completeness.py --audit`: 0 findings.
- `generate-known-failure-modes.py --check`: current (912 entries). `verify-derived-counts.py`: OK, 11 claims. `verify-engine-instance-split.py`, `verify-build-config.py`, `verify-doc-line-links.py`, `verify-class-defences.py`, `validate-instance.py`: exit 0.
- `verify-review-document.py`: this document passes. The whole-corpus run exits 1 on five findings in four historical reviews from August, none touched here; the build runs that step `--warn-only`.

**Correction 2026-09-27 (same authorisation, relayed by lead-agent): client literals removed from the engine copy of `verify-routing-reconciliation.py`.** Check 3's selftest named this instance's environment chain, which an engine file must not carry. Changed, in both copies (byte-identical): the fixture chain `["dev", "tst_acc", "prd"]` became `["dev", "test", "prod"]`; the burst fixture's `TST_ACC` stage line became `TEST`; the block comment's "DEV-then-TST/ACC dispatch" became "dev-then-test dispatch". No behaviour changed and CHECK 4 (review 2026-09-26-6) was not touched. Results: `--selftest` exit 0 (check-1, check-2, check-3 and check-4 cases); `verify-engine-instance-split.py` exit 0; `grep -ci 'tst_acc\|tst/acc'` returns 0 in both copies (positive control: 11 in the pipeline config); a client-name grep of the engine copy returns 0.

**Second correction 2026-09-27 (same authorisation, engine-standard decision S-5): client literals removed from two more engine files.** `verify-improvement-log.py` (both copies, byte-identical): the guard fixtures' chain `[dev, tst_acc, prd]` became `[dev, test, prod]`; fixture `guard-e2-fixed-in-flight-tst_acc-passes` became `guard-e2-fixed-in-flight-test-passes` (target `test`); the `-prd-` fixtures became `-prod-` with target `prod`, since `prd` is not in the generic chain; the misspelt-name fixture now passes `production`; and the guard comment "this instance holds special-category data" became "above all where the instance holds special-category data". `agents/pipeline-agent.md`: this review's added step-order line now says "the test-stage flow-statecode capture and the production-stage confirmations … For the last environment of the chain"; the two TST/ACC mentions that were already there at HEAD (L32, the Stage 0.5 paragraph) are left alone as earlier debt. Results: `--selftest` 101 of 101; `--check` exit 0; `--target-env prd` exit 0 and `prod` exit 2 on the real instance; `verify-engine-instance-split.py` exit 0; a `tst_acc`/`TST/ACC` grep over this review's added lines in both engine files returns 0. `verify-post-deploy-completeness.py` and `lib/deploy_markers.py` were not touched.

**Level reached:** V1 for both mechanisms. The first production deploy that runs the guard, and the first deploy followed by a tagged batch, are their first live exercises.

## Appendix A — `scripts/verify-improvement-log.py`, the diff as measured

Base: the working-tree file with sha1 prefix `1a8b028c3d2d` (Group 1 applied). Both copies land byte-identical.

```diff
--- a/scripts/verify-improvement-log.py
+++ b/scripts/verify-improvement-log.py
@@ -524,8 +524,39 @@
             result = None
     _DEPLOY_PATHS_CACHE[key] = result
     return result
+
+
+_ENV_CHAIN_CACHE: dict[str, list[str] | None] = {}
 
 
+def load_environment_chain(repo_root: Path) -> list[str] | None:
+    """instance.yaml -> environment_chain, or None when it is absent or unreadable.
+
+    The PRODUCTION GUARD (improvement review 2026-09-26-7, capability design 2026-09-26 WS-V)
+    binds only the LAST environment of this chain. None means the last environment cannot be
+    known, and the guard then applies to EVERY target: an instance that forgot the key must
+    never have its production deploy treated as an early one (the same fail-safe direction as
+    load_deploy_paths).
+    """
+    key = str(repo_root.resolve())
+    if key in _ENV_CHAIN_CACHE:
+        return _ENV_CHAIN_CACHE[key]
+    result: list[str] | None = None
+    path = repo_root / "instance.yaml"
+    if path.is_file():
+        try:
+            import yaml
+            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
+            chain = data.get("environment_chain") if isinstance(data, dict) else None
+            if isinstance(chain, list):
+                cleaned = [str(e).strip() for e in chain if str(e).strip()]
+                result = cleaned or None
+        except Exception:  # noqa: BLE001 — unreadable means "unknown", and unknown guards
+            result = None
+    _ENV_CHAIN_CACHE[key] = result
+    return result
+
+
 def _strip_dot_slash(path: str) -> str:
     """Remove ONE leading './' — never lstrip('./'), which would turn '.github/' into 'github/'."""
     path = path.strip()
@@ -1539,7 +1570,8 @@
     return UNREAD, ""
 
 
-def check_triggers(rows: list[dict], repo_root: Path) -> tuple[list[str], list[str]]:
+def check_triggers(rows: list[dict], repo_root: Path,
+                   target_env: str | None = None) -> tuple[list[str], list[str]]:
     """WORKFLOW.md -> Processing triggers, enforced rather than remembered.
 
     Returns (errors, notes).
@@ -1607,6 +1639,41 @@
                 + ". Confirm the broken artefact really is not deployable; if it is, correct "
                   "'defect_in' or add 'lane_override: deploy'.")
 
+    # ── PRODUCTION GUARD (improvement review 2026-09-26-7, capability design WS-V, D-2). A
+    # governance finding waits for the batch review in every environment but the LAST one: a
+    # production promotion is where an unreviewed security or compliance defect stops being
+    # recoverable, and this instance holds special-category data. A fixed-in-flight entry is
+    # held here too: its stamp is a claim the gate cannot verify (who ran the re-run, and did it
+    # exit 0), and the batch review is where that claim is read. Deploy-lane blockers in
+    # `unread` or `awaiting-approval` need no clause here — they already fail in EVERY
+    # environment (D-10). Reviewer-deferred entries pass: a deferral is the reviewer's decision.
+    if target_env is not None:
+        chain = load_environment_chain(repo_root)
+        last = chain[-1] if chain else None
+        if chain is None or target_env == last:
+            # A reviewer's deferral releases a fixed-in-flight entry too: classify() ranks the
+            # stamp above the deferral, so without this line a V4 fix nobody can re-observe
+            # would hold production forever against the reviewer's own decision.
+            held = governance_open + [r for r in fixed if not r.get("deferred_reason")]
+            where = (f"'{target_env}' is the last environment of instance.yaml -> "
+                     f"environment_chain" if chain else
+                     f"instance.yaml declares no environment_chain, so every target is "
+                     f"treated as the last")
+            if held:
+                errors.append(
+                    f"PRODUCTION GUARD: {len(held)} finding(s) must be reviewed or deferred "
+                    f"before a deploy to '{target_env}' ({where}): "
+                    + ", ".join(f"{r.get('id')} ({states[str(r.get('id'))][0]}, "
+                                f"{lane.get(str(r.get('id')), 'n/a')} lane)" for r in held)
+                    + ".\n    Send APPROVE IMPROVEMENTS against the review each names, or have "
+                      "the reviewer record a deferral. Earlier environments are not held.")
+            else:
+                notes.append(f"verify-improvement-log: NOTE — production guard for "
+                             f"'{target_env}': clear ({where}).")
+        else:
+            notes.append(f"verify-improvement-log: NOTE — production guard not applicable: "
+                         f"'{target_env}' is not the last environment ('{last}').")
+
     # ── STATE 5 of 5: approved, and the artefact is not there. A FAIL, and named. ───────────
     # This is the state whose absence let four approved items read as accepted deferrals for up
     # to eleven days (IMP-0181). It fails rather than warns because there is nothing left to
@@ -2451,7 +2518,7 @@
 # ── run / selftest / main ─────────────────────────────────────────────────────────────────
 
 def run(log_path: Path, repo_root: Path, check: bool,
-        reviews_dir: Path | None = None) -> Result:
+        reviews_dir: Path | None = None, target_env: str | None = None) -> Result:
     rows, errors = load(log_path)
     errors = errors + check_schema(rows, repo_root)
     # A false `reviewed_in` on a review's OWN appended finding. An ERROR, not a warning: it asks
@@ -2464,7 +2531,7 @@
     warnings: list[str] = []
     notes: list[str] = []
     if check:
-        triggers, notes = check_triggers(rows, repo_root)
+        triggers, notes = check_triggers(rows, repo_root, target_env)
         rdir = reviews_dir or (repo_root / REVIEWS_DIR)
         warnings = check_citation_stamps(rows, rdir, repo_root)
         # RETIRED 2026-08-25, improvement review 28 change 6: check_review_status_headers() used to
@@ -3076,6 +3143,43 @@
 }
 
 
+# PRODUCTION GUARD fixtures (improvement review 2026-09-26-7, WS-V). (rows, files, target_env,
+# expected rc, text). The chain is THIS instance's, so the fixtures test the real topology.
+_INSTANCE_CHAIN = _INSTANCE_LANES + "environment_chain: [dev, tst_acc, prd]\n"
+_GOV = dict(defect_in=["agents/WORKFLOW.md"])
+_TARGET_ENV_CASES: dict = {
+    "guard-a-governance-unread-dev-passes": (
+        [_entry(**_GOV)], {"instance.yaml": _INSTANCE_CHAIN}, "dev", 0, "not applicable"),
+    "guard-b-governance-unread-prd-fails": (
+        [_entry(**_GOV)], {"instance.yaml": _INSTANCE_CHAIN}, "prd", 1, "PRODUCTION GUARD"),
+    "guard-c-governance-awaiting-prd-fails": (
+        [_entry(reviewed_in=_REVIEW, **_GOV)],
+        {"instance.yaml": _INSTANCE_CHAIN, _REVIEW: _REVIEW_BODY}, "prd", 1, "PRODUCTION GUARD"),
+    "guard-d-governance-deferred-prd-passes": (
+        [_entry(deferred_reason="reviewer decided", revisit_when="later", **_GOV)],
+        {"instance.yaml": _INSTANCE_CHAIN}, "prd", 0, "clear"),
+    "guard-e-fixed-in-flight-prd-fails": (
+        [_entry(defect_in=["src/x.ts"], fixed_in_flight=_FIF,
+                evidence_grep={"file": "src/x.ts", "contains": "the fix"})],
+        {"instance.yaml": _INSTANCE_CHAIN, "src/x.ts": "here is the fix\n"}, "prd", 1,
+        "PRODUCTION GUARD"),
+    "guard-e2-fixed-in-flight-tst_acc-passes": (
+        [_entry(defect_in=["src/x.ts"], fixed_in_flight=_FIF,
+                evidence_grep={"file": "src/x.ts", "contains": "the fix"})],
+        {"instance.yaml": _INSTANCE_CHAIN, "src/x.ts": "here is the fix\n"}, "tst_acc", 0,
+        "not applicable"),
+    "guard-e3-fixed-in-flight-reviewer-deferred-prd-passes": (
+        [_entry(defect_in=["src/x.ts"], fixed_in_flight=_FIF, deferred_reason="reviewer: V4, "
+                "re-observe after the next DEV deploy", revisit_when="next DEV deploy",
+                evidence_grep={"file": "src/x.ts", "contains": "the fix"})],
+        {"instance.yaml": _INSTANCE_CHAIN, "src/x.ts": "here is the fix\n"}, "prd", 0, "clear"),
+    "guard-f-no-chain-guards-every-target": (
+        [_entry(**_GOV)], {"instance.yaml": _INSTANCE_LANES}, "dev", 1, "declares no environment_chain"),
+    "guard-g-non-blocker-governance-is-not-held": (
+        [_entry(severity="friction", **_GOV)], {"instance.yaml": _INSTANCE_CHAIN}, "prd", 0, "clear"),
+}
+
+
 def selftest() -> int:
     failures: list[str] = []
     with tempfile.TemporaryDirectory() as tmp:
@@ -3113,6 +3217,37 @@
                 for line in result.text().splitlines():
                     print(f"                   {line}")
 
+        for name, (rows, files, env, want_rc, want_text) in _TARGET_ENV_CASES.items():
+            root = Path(tmp) / name
+            root.mkdir(parents=True)
+            for rel, body in files.items():
+                dest = root / rel
+                dest.parent.mkdir(parents=True, exist_ok=True)
+                dest.write_text(body, encoding="utf-8")
+            log = root / "log.jsonl"
+            log.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
+                           encoding="utf-8")
+            result = run(log, root, True, target_env=env)
+            ok = result.rc == want_rc and want_text in result.text()
+            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {result.rc} "
+                  f"(expected {want_rc})")
+            if not ok:
+                failures.append(name)
+                for line in result.text().splitlines():
+                    print(f"                   {line}")
+        # A misspelt production target is a usage error, never an early environment.
+        typo_root = Path(tmp) / "guard-h-unknown-env"
+        typo_root.mkdir(parents=True)
+        (typo_root / "instance.yaml").write_text(_INSTANCE_CHAIN, encoding="utf-8")
+        (typo_root / "log.jsonl").write_text(json.dumps(_entry(**_GOV)) + "\n", encoding="utf-8")
+        typo_rc = main(["--log", str(typo_root / "log.jsonl"), "--repo-root", str(typo_root),
+                        "--target-env", "prod"])
+        ok = typo_rc == 2
+        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} guard-h-unknown-env → exit {typo_rc} "
+              f"(expected 2)")
+        if not ok:
+            failures.append("guard-h-unknown-env")
+
         # The missing-log case needs no tree at all (IMP-0007).
         missing = run(Path(tmp) / "no-such-log.jsonl", Path(tmp), False)
         ok = missing.rc == 1 and "does not exist" in missing.text()
@@ -3143,7 +3278,8 @@
         print(f"\nverify-improvement-log: SELFTEST FAILED — {', '.join(failures)}",
               file=sys.stderr)
         return 1
-    print(f"\nverify-improvement-log: SELFTEST OK — {len(_CASES) + 2} fixtures, all six "
+    print(f"\nverify-improvement-log: SELFTEST OK — "
+          f"{len(_CASES) + len(_TARGET_ENV_CASES) + 3} fixtures, all six "
           f"states of a NEW finding and both blocker lanes distinguished, and every "
           f"pre-existing check still fires.")
     return 0
@@ -3175,6 +3311,11 @@
     parser.add_argument("--warn-only", action="store_true",
                         help="print every finding and exit 0 — for a second observation that "
                              "must report drift without failing the build (IMP-0343)")
+    parser.add_argument("--target-env", default=None,
+                        help="the environment about to be deployed to; implies --check. When "
+                             "it is the last element of instance.yaml -> environment_chain, "
+                             "the production guard also fails on open governance-lane blockers "
+                             "and fixed-in-flight entries (WS-V)")
     parser.add_argument("--selftest", action="store_true",
                         help="assemble fixtures at runtime and prove all five states of a "
                              "NEW finding are distinguished")
@@ -3184,7 +3325,15 @@
         return selftest()
 
     root = (args.repo_root or Path.cwd())
-    result = run(args.log, root, args.check, args.reviews_dir)
+    if args.target_env is not None:
+        chain = load_environment_chain(root)
+        if chain is not None and args.target_env not in chain:
+            print(f"verify-improvement-log: usage error — --target-env {args.target_env!r} is "
+                  f"not in instance.yaml -> environment_chain {chain}. A misspelt production "
+                  f"target must not pass as an early environment.", file=sys.stderr)
+            return 2
+    result = run(args.log, root, args.check or args.target_env is not None,
+                 args.reviews_dir, args.target_env)
 
     for note in result.notes:
         print(note, file=sys.stderr)
```

## Appendix B — `scripts/verify-routing-reconciliation.py`, the diff as measured

Base: the file as committed (the instance and engine copies are byte-identical today). `POST_DEPLOY_REQUIRED_FROM` is set to the apply date when it lands.

```diff
--- a/scripts/verify-routing-reconciliation.py
+++ b/scripts/verify-routing-reconciliation.py
@@ -346,6 +346,114 @@
 
     code = 1 if (stats["unreconciled"] or wbs_findings) else 0
     return code, findings, stats
+
+
+# ---------------------------------------------------------------------------------------------
+# CHECK 3 — every deploy is followed by ONE post-deploy improvement batch (improvement review
+# 2026-09-26-7; capability design 2026-09-26 WS-U requirement 7). REPORT, NEVER HALT.
+#
+# WHY. The trigger it backs has existed in prose since 2026-08-17 ("a feature or phase completes
+# -> after the Deployment Summary") and was never followed: Deployment Summaries were committed
+# 18 times from 2026-09-01 to 2026-09-26, and none of the 142 improvement-agent dispatches in
+# logs/routing.log names that trigger as its reason. A prose trigger nobody can see being skipped
+# is skipped. This check makes the skip visible; it does not make the batch happen.
+#
+# WHAT IT READS. A deploy is a `[PIPELINE]` stage line in logs/pipeline.log whose environment is
+# in instance.yaml -> environment_chain and whose status is SUCCESS, PARTIAL or FAILED. HELD is
+# not a deploy (a stage paused at a gate or a refusal) and CONFIG is not an environment. Stage
+# lines of ONE feature less than --grace-minutes apart are ONE episode: a retry burst or a
+# DEV-then-TST/ACC dispatch is followed by one batch, which is the no-stacking rule. An episode is
+# covered by a routing.log line ROUTED_TO / RESUMED / RE-DISPATCHED / SKIPPED naming
+# improvement-agent and carrying `trigger:post-deploy`, written at or after the episode's last
+# stage line and before the same feature's next episode starts.
+#
+# WHY IT NEVER TOUCHES THE EXIT CODE, even without --warn-only. Check 1 is SOFT today and its
+# going HARD is an open decision (agents/WORKFLOW.md); this check must not go HARD with it by
+# accident. The design says report, never halt: a process fact never stops a build.
+#
+# FORWARD-ONLY from POST_DEPLOY_REQUIRED_FROM, the day the trigger became a written convention with
+# a routing-line marker. Every earlier deploy lacks the marker by construction.
+# ---------------------------------------------------------------------------------------------
+
+POST_DEPLOY_REQUIRED_FROM = "2026-09-27"   # set to the apply date when this change lands
+STAGE_RE = re.compile(
+    r"^\[(?P<ts>\d{4}-\d{2}-\d{2}) (?P<hm>\d{2}:\d{2})\]\s*\[PIPELINE\]\s*"
+    r"\[(?P<feature>[^\]]+)\]\s*\[(?P<env>[^\]]+)\]\s*(?P<status>SUCCESS|PARTIAL|FAILED|HELD)\b")
+DEPLOY_STATUSES = {"SUCCESS", "PARTIAL", "FAILED"}
+BATCH_MARKERS = {"ROUTED_TO", "RESUMED", "RE-DISPATCHED", "SKIPPED"}
+BATCH_RE = re.compile(
+    r"^\[(?P<ts>\d{4}-\d{2}-\d{2})[ T](?P<hm>\d{2}:\d{2})\].*?"
+    r"\b(?P<marker>ROUTED_TO|RESUMED|RE-DISPATCHED|SKIPPED)\s*:\s*improvement-agent\b"
+    r"(?P<rest>.*)$")
+
+
+def load_environment_chain(repo_root: Path) -> list[str] | None:
+    try:
+        import yaml
+        data = yaml.safe_load((repo_root / "instance.yaml").read_text(encoding="utf-8")) or {}
+    except Exception:  # noqa: BLE001 — no chain means every bracketed environment is eligible
+        return None
+    chain = data.get("environment_chain") if isinstance(data, dict) else None
+    return [str(e).strip().lower() for e in chain] if isinstance(chain, list) and chain else None
+
+
+def _norm_env(env: str) -> str:
+    return env.strip().lower().replace("/", "_")
+
+
+def check_post_deploy_batches(routing_text: str, pipeline_text: str, since: datetime,
+                              now: datetime, grace: timedelta,
+                              chain: list[str] | None) -> tuple[list[Finding], dict[str, int]]:
+    stats = {"pd_stage_lines": 0, "pd_episodes": 0, "pd_covered": 0, "pd_in_flight": 0,
+             "pd_missing": 0, "pd_out_of_scope": 0}
+    stages: list[tuple[datetime, str, str, int]] = []
+    for i, raw in enumerate(pipeline_text.splitlines(), 1):
+        m = STAGE_RE.match(raw.strip())
+        if not m or m.group("status") not in DEPLOY_STATUSES:
+            continue
+        env = _norm_env(m.group("env"))
+        if env == "config" or (chain is not None and env not in chain):
+            continue
+        when = datetime.strptime(f"{m.group('ts')} {m.group('hm')}", "%Y-%m-%d %H:%M")
+        stages.append((when, m.group("feature").strip(), env, i))
+    batches = []
+    for raw in routing_text.splitlines():
+        m = BATCH_RE.match(raw.strip())
+        if m and "trigger:post-deploy" in m.group("rest"):
+            batches.append(datetime.strptime(f"{m.group('ts')} {m.group('hm')}",
+                                             "%Y-%m-%d %H:%M"))
+    episodes: dict[str, list[list[tuple[datetime, str, str, int]]]] = {}
+    for st in sorted(stages):
+        eps = episodes.setdefault(st[1], [])
+        if eps and st[0] - eps[-1][-1][0] < grace:
+            eps[-1].append(st)
+        else:
+            eps.append([st])
+    findings: list[Finding] = []
+    for feature, eps in episodes.items():
+        for n, ep in enumerate(eps):
+            last = ep[-1][0]
+            if last < since:
+                stats["pd_out_of_scope"] += 1
+                continue
+            stats["pd_episodes"] += 1
+            stats["pd_stage_lines"] += len(ep)
+            nxt = eps[n + 1][0][0] if n + 1 < len(eps) else None
+            if any(b >= last and (nxt is None or b < nxt) for b in batches):
+                stats["pd_covered"] += 1
+            elif nxt is None and now - last < grace:
+                stats["pd_in_flight"] += 1
+            else:
+                stats["pd_missing"] += 1
+                lines = ", ".join(f"L{s[3]} {s[2]}" for s in ep)
+                findings.append(Finding(
+                    "POST-DEPLOY-BATCH-MISSING", ep[-1][3], last, "improvement-agent", feature,
+                    f"pipeline.log {lines}: a deploy with no `trigger:post-deploy` improvement "
+                    f"batch after it (ROUTED_TO, RESUMED, RE-DISPATCHED or SKIPPED) before this "
+                    f"feature's next deploy. agents/WORKFLOW.md -> Processing triggers: one "
+                    f"batch follows every deploy, alongside the next delivery dispatch. Reported, "
+                    f"never halting."))
+    return findings, stats
 
 
 # ---------------------------------------------------------------------------------------------
@@ -480,6 +588,50 @@
         if code != 1 or not any(f.kind == "NO-WBS" for f in findings):
             failures.append("an unreadable wbs.json did not report NO-WBS — the check passed "
                             "over nothing, which is IMP-0007")
+
+    # CHECK 3 — post-deploy batch (WS-U requirement 7).
+    pd_since = datetime(2026, 9, 27)
+    pd_now = datetime(2026, 9, 28, 12, 0)
+    chain = ["dev", "tst_acc", "prd"]
+    P = "[{}] [PIPELINE] [{}] [{}] {} — x\n"
+    B = "[{}] [LEAD] [system] {}:improvement-agent — {}\n"
+    cases = {
+        # (pipeline, routing, expected missing, expected in-flight)
+        "deploy-then-batch-is-clean": (
+            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
+            B.format("2026-09-27 10:05", "ROUTED_TO", "trigger:post-deploy"), 0, 0),
+        "deploy-with-no-batch-reports": (
+            P.format("2026-09-27 10:00", "f", "DEV", "FAILED"), "", 1, 0),
+        "dev-then-tst-burst-one-batch-is-clean": (
+            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS")
+            + P.format("2026-09-27 10:40", "f", "TST_ACC", "PARTIAL"),
+            B.format("2026-09-27 10:45", "ROUTED_TO", "trigger:post-deploy"), 0, 0),
+        "batch-after-second-episode-only-reports-the-first": (
+            P.format("2026-09-27 08:00", "f", "DEV", "SUCCESS")
+            + P.format("2026-09-27 14:00", "f", "DEV", "SUCCESS"),
+            B.format("2026-09-27 14:05", "RESUMED", "trigger:post-deploy"), 1, 0),
+        "skipped-line-counts-as-the-batch": (
+            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
+            B.format("2026-09-27 10:01", "SKIPPED", "trigger:post-deploy, queue empty"), 0, 0),
+        "held-and-config-lines-are-not-deploys": (
+            P.format("2026-09-27 10:00", "f", "DEV", "HELD")
+            + P.format("2026-09-27 11:00", "f", "CONFIG", "SUCCESS"), "", 0, 0),
+        "pre-cutover-deploy-is-out-of-scope": (
+            P.format("2026-09-20 10:00", "f", "DEV", "SUCCESS"), "", 0, 0),
+        "recent-deploy-is-in-flight": (
+            P.format("2026-09-28 11:30", "f", "DEV", "SUCCESS"), "", 0, 1),
+        "batch-without-the-trigger-tag-does-not-count": (
+            P.format("2026-09-27 10:00", "f", "DEV", "SUCCESS"),
+            B.format("2026-09-27 10:05", "ROUTED_TO", "blocker IMP-0001, immediately"), 1, 0),
+        "environment-outside-the-chain-is-ignored": (
+            P.format("2026-09-27 10:00", "f", "SANDBOX", "SUCCESS"), "", 0, 0),
+    }
+    for name, (ptxt, rtxt, want_missing, want_flight) in cases.items():
+        found, st = check_post_deploy_batches(rtxt, ptxt, pd_since, pd_now,
+                                              timedelta(minutes=120), chain)
+        if st["pd_missing"] != want_missing or st["pd_in_flight"] != want_flight:
+            failures.append(f"check 3 '{name}': missing {st['pd_missing']} (want {want_missing}),"
+                            f" in flight {st['pd_in_flight']} (want {want_flight})")
 
     if failures:
         for f in failures:
@@ -516,6 +668,11 @@
                              "not a finding (default: 120)")
     parser.add_argument("--now", default=None,
                         help="override 'now' as YYYY-MM-DD HH:MM (testing)")
+    parser.add_argument("--pipeline-log", type=Path, default=Path("logs/pipeline.log"),
+                        help="deploy stage lines for check 3 (post-deploy batch)")
+    parser.add_argument("--post-deploy-since", default=POST_DEPLOY_REQUIRED_FROM,
+                        help=f"YYYY-MM-DD; check 3 is forward-only from this date "
+                             f"(default: {POST_DEPLOY_REQUIRED_FROM})")
     parser.add_argument("--warn-only", action="store_true",
                         help="print findings and exit 0")
     parser.add_argument("--selftest", action="store_true",
@@ -535,6 +692,23 @@
     code, findings, stats = run(args.log, cutoff, now, timedelta(minutes=args.grace_minutes),
                                 wbs=args.wbs)
 
+    # CHECK 3 never changes `code` — see its block comment.
+    pd_stats = {"pd_missing": 0, "pd_covered": 0, "pd_in_flight": 0, "pd_episodes": 0,
+                "pd_out_of_scope": 0}
+    if args.pipeline_log.is_file() and args.log.is_file():
+        pd_findings, pd_stats = check_post_deploy_batches(
+            args.log.read_text(encoding="utf-8"),
+            args.pipeline_log.read_text(encoding="utf-8"),
+            datetime.strptime(args.post_deploy_since, "%Y-%m-%d"), now,
+            timedelta(minutes=args.grace_minutes), load_environment_chain(Path.cwd()))
+        for f in pd_findings:
+            print(f"REPORT: {f}", file=sys.stderr)
+    print(f"verify-routing-reconciliation: post-deploy batches — {pd_stats['pd_missing']} "
+          f"deploy episode(s) with no batch, {pd_stats['pd_covered']} covered, "
+          f"{pd_stats['pd_in_flight']} in flight, since {args.post_deploy_since} "
+          f"({pd_stats['pd_out_of_scope']} earlier episode(s) out of scope). Report only.",
+          file=sys.stderr)
+
     notes = [f for f in findings if f.kind in ("IN-FLIGHT",)]
     hard = [f for f in findings if f.kind not in ("IN-FLIGHT",)]
 
```
