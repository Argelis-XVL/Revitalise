# Improvement Review — 2026-10-05 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 16 `NEW` → 9 clusters (the 14 unread entries in the queue, plus 2 this review logged while checking the build-scoping change)
**Trigger:** reviewer request ("process these changes", relayed by lead-agent, 2026-10-05)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-05. The reviewer answered *"D1-3 agreed with suggestions. Approve improvements"*: `APPROVE IMPROVEMENTS`, with D-1, D-2 and D-3 all yes as suggested. Rows 1–8 are on disk; see *Applied* at the end. `reviewed_in` is stamped on all 16 entries.
**WBS:** system work, `wbs:system`, not billable. The underlying findings come from the Create Envelope rework (`wbs:3.2`), the intake (`wbs:4.2,4.3`) and the build-time work the reviewer asked for.

---

## Summary

The two build-scoping findings are the main business, and checking them against the code changed the picture in three ways. **Scoped builds would never actually be scoped today**: the runner looks for the last green build's result at one fixed path, and the last three builds wrote theirs somewhere else. **Editing a gate's own script would skip that gate**: I measured four steps where this happens. **And "refuse promotion of a scoped artifact" protects the wrong thing**: test and production never receive a build artifact. Power Platform Pipelines exports whatever DEV holds, so the guard has to be on what DEV was last given.

This review proposes 7 changes plus 1 config change that depends on your answer. It closes 10 entries when applied and defers 6, and asks you 3 questions. None of the questions blocks rows 1–6. *(Corrected at apply: the draft said 9 and 7, but its own disposition table names 10 closures and 6 deferrals.)*

---

## 1. Regression check — did the last review's changes work?

The last applied reviews are [2026-10-05](docs/improvements/2026-10-05-improvement-review.md#L1) and [2026-09-30-2](docs/improvements/2026-09-30-improvement-review-2.md#L1), both applied this morning. For 09-30-2 I audited only the rows whose class has a new finding in this batch.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 10-05 row 1: plain-column gate Rule B counts only flow write payloads | 2026-10-05 | `gate-cannot-fail` | NO | Working |
| 10-05 row 2: Rule C, a calculated column written by a flow | 2026-10-05 | `gate-cannot-fail` | NO | Working. 0 calculated columns in source, so only its fixture has made it fail |
| 10-05 row 3: option-set entry re-tagged | 2026-10-05 | `exit-zero-does-not-mean-created` | NO | Working |
| 10-05 row 5: digest size line | 2026-10-05 | derived count | n/a | Will drift again on regeneration. Handled at apply by `verify-derived-counts.py` |
| 10-05 row 6: 8 referee columns pending adjudication | 2026-10-05 | domain invariants | NO | Working. The two catalogues now hold the columns too |
| 10-05 D-1: a hotfix runs the source gates first | 2026-10-05 (decision only) | `solution-source-edited-outside-dispatch` | **2 new entries, not a recurrence** | Both describe the 3–4 October hotfixes, which happened before D-1 was decided. No hotfix has run since: [pipeline.log](logs/pipeline.log#L1) has no 5 October line. D-1 is still prose in a draft design and nothing enforces it |
| 09-30-2 rows 9, 19(a), 20: two gate-scope fixes | 2026-10-05 | `gate-scope-mismatch` | 2 new entries, different gates | Working for the gates they targeted. The class is a catch-all of 31 |
| 09-30-2 row 11: test-agent transcribes row by row | 2026-10-05 | `no-assertion-on-shipped-content` | 1 new entry | **Working.** The new gap was found *by* that method, before deploy |
| 09-30-2 row 26: knowledge bullet on `string(<boolean>)` | 2026-10-05 | `solution-source-edited-outside-dispatch` | NO | Working |
| 09-30-2 row 30: a stale deferral annotated | 2026-10-05 | `stale-deferral-uncaught-across-sessions` | 1 new entry, different mechanism | The new entry is about amendments to a parked review, not deferral expiry |
| Review 2026-09-08-2 change 5: step 6, "dump one member before filtering by an attribute" | 2026-09-08 | `approved-change-wording-assumes-a-field-that-does-not-exist` | **YES** (instance 2 from `class_instance_of`; the finding's prose says "third") | **Recurred after a prose fix.** See C4 for why the escalation still stays in prose |

**Changes whose class recurred after a *prose* fix:** the step-6 bullet. The answer is to sharpen the wording and require a measured count in the change row, not to add a gate (C4).
**Changes whose class recurred after a *gate*:** none.

---

## 2. Clusters and promotion decisions

```
CLUSTER: capability-established + two-invocation-paths-disagree + gate-scope-mismatch
         — the build-scoping change  (x4: IMP-1051, IMP-1052, IMP-1053, IMP-1054)
Altitude:   ENGINE for the mechanism and the agent rules; CLIENT-SPECIFIC for which step groups
            are scoped and for "promotion exports from DEV". Stripping this client's literals still
            leaves a true statement: "a scoped build is an inner-loop artifact for the first
            environment; whatever is promoted from that environment must come from a full run".
            I checked my drafted text for client names, the table prefix and environment names
            and found none.
Ladder row: "a capability was established" + "a tool could catch it mechanically"
Becomes:    rows 4–7 (+ row 8, which depends on D-1)
Retires:    nothing
Cites:      IMP-1051, IMP-1052, IMP-1053, IMP-1054
Residual:   (a) "the artifact named at a later stage is the newest one deployed to DEV" is an
            instruction. The deploy record is prose in pipeline.log, so no gate reads it.
            (b) Implicit inputs (row 5) only catch files a command names. A script that reads a
            config file it does not name on the command line is still invisible to scoping.
```

**What I measured, and how it changes the two findings:**

1. **The base for `last-green` is never found.** [resolve_last_green](.engine/scripts/run-build.py#L193) globs `build/artifacts/<feature>-*/run-build-result.json`. [build-agent step 5](agents/build-agent.md#L92) runs the runner without `--result-out`, so the result goes wherever the dispatch decides. For this feature, 14 result files sit at **5 different paths**. The three newest builds (20261002-3, 20261005-4, 20261005-5) wrote sibling files the glob cannot match. So even after the next full run records a `git_head`, every scoped run would print "FULL RUN" and look like the documented first-run behaviour. Logged as a new finding.
2. **A gate is skipped when its own script changes.** I ran the runner's planner with a changed set of just `scripts/verify-packed-form-types.py`. `component-shape-packed`, which *runs* that script, came back `skipped_unchanged` because its `paths:` was `src/solutions/**` ([component-shape-packed](config/revitalise-grant-automation-build.yml#L1085)). The same is true for both bundle-budget steps and `lint`: **4 of the 24 scoped steps**. Logged as a new finding.
3. **Promotion never takes a build artifact.** The [pipeline config](config/revitalise-grant-automation-pipeline.yml#L88) records that Pipelines exports the solution from DEV when promotion is requested. Refusing a scoped artifact at test and production is still worth doing as a gate (row 6), but the real rule is about **what DEV was last given** (row 7).
4. **"Skip the DEV import when the zip is absent" is not safe as proposed.** `last-green` is the last *green* build, not the last *deployed* one. A green build that was never deployed, followed by a scoped one, would leave DEV without its change. The import also resets live drift: this morning's review found an option-set change in DEV that no log line explains. Packing the solution takes **11.5 s** (pack-managed 9.8 s, pack-unmanaged 1.5 s, form-type check 0.1 s, build 20261005-5), so D-1 suggests always packing. The ~5-minute import would stay.
5. **Publishing state.** Engine commit `592b245` is in no remote branch (`git -C .engine branch -r --contains 592b245` prints nothing). The instance branch, which points at it, is 4 commits ahead of its remote. Nothing is broken yet, but **the engine must be pushed first**, or a fresh clone cannot resolve the pointer.

```
CLUSTER: gate-fires-on-nothing  (x1: IMP-1039)
Altitude:   CLASS fix inside an existing gate (ENGINE — both copies are byte-identical)
Ladder row: "a tool could catch it mechanically" — the defect is in the tool
Becomes:    row 1
Retires:    nothing
Cites:      IMP-1039
Residual:   the sibling count in check_left_behind() keeps counting closures only. No measured
            instance there, and widening it would change a second gate's output unasked.
```

Measured on a scratch copy against the real log: **warnings 2 → 1**. The one removed is the false "still parked" warning about a review that closed nothing because all its entries were deferred. The one left is this batch's own stamp warning. The selftest still passes all 107 fixtures.

```
CLUSTER: stale-deferral-uncaught-across-sessions  (x1 here: IMP-1040)
Altitude:   agent-file edit (ENGINE)
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    row 2
Cites:      IMP-1040
Residual:   live re-measurement still needs a credentialled session. The edit makes the
            amendment say, per row, which items it could not re-measure.
```

```
CLUSTER: approved-change-wording-assumes-a-field-that-does-not-exist  (x2: IMP-0660, IMP-1042)
Altitude:   agent-file edit, kept in prose on purpose (ENGINE)
Ladder row: recurrence after prose → would normally escalate to a gate
Becomes:    row 3: the bullet names instruction prose explicitly, and the change row must carry
            the literal's match count, so the reviewer can see the measurement
Cites:      IMP-0660, IMP-1042
Residual:   no gate. A gate over draft instruction prose is a phrase gate, the shape measured five
            times at 48–100% false. Both instances were caught at apply by NARROW-AND-REPORT
            before reaching another agent.
```

```
CLUSTER: solution-source-edited-outside-dispatch  (x2 here: IMP-1043, IMP-1044)
Altitude:   none new. The class remedy is 10-05 decision D-1 (a hotfix runs the gates first)
Becomes:    nothing. Both fixes landed in source today (the 35 tests were rewritten; TAD rev 16
            added ADR-070; both catalogues hold the referee columns)
Cites:      IMP-1043, IMP-1044
Residual:   the proposed "columns an ADR says will not exist" check is declined for now. It
            would be a fourth gate over this class, and D-1 prevents the cause.
```

```
CLUSTER: hand-maintained-count-drifts-from-source  (x2 here: IMP-1045, IMP-1048)
Altitude:   INSTANCE — test-file fixes, both landed
Becomes:    nothing. Routed residual R3
Cites:      IMP-1045, IMP-1048
Residual:   the proposal to DERIVE the secured-column pin from the profile file is declined. A pin
            derived from the file it checks can never fail, and the pin exists to make a change
            need a reviewer (you confirmed 42 today). Two order checks still compare positions
            with no existence check (R3).
```

```
CLUSTER: gate-scope-mismatch  (x2 here: IMP-1046, IMP-1047)
Altitude:   IMP-1047 INSTANCE, landed (the generator now writes both apps' copies).
            IMP-1046 needs your decision on WHERE an expiring deferral should surface (D-3).
Cites:      IMP-1046, IMP-1047
Residual:   until D-3 is answered, an expiry is found by the build that halts on it.
```

```
CLUSTER: live-definition-drifts-from-source  (x1: IMP-1041)
Becomes:    nothing new. Already routed by 10-05 D-3 (deploy the intake flow from source through
            a gated build). No deploy has run since, so it stays open
Cites:      IMP-1041
```

```
CLUSTER: no-assertion-on-shipped-content (IMP-1049) · wrong-artefact-cited-as-evidence (IMP-1050)
Altitude:   INSTANCE — test and source-comment fixes owned by development-agent
Becomes:    routed R1, R2
Cites:      IMP-1049, IMP-1050
Residual:   none beyond the routed work
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-improvement-log.py` and `.engine/scripts/verify-improvement-log.py` (identical) | In the corrects-warning's "was this review's keyword given" test ([L2581](scripts/verify-improvement-log.py#L2581)), count an entry carrying a `deferred_reason` as evidence, alongside APPLIED and REJECTED. New selftest fixture `all-deferral-review-is-not-parked` | IMP-1039 | YES — `--selftest`; `--check` on the real log drops the false warning (measured 2 → 1) | already wired (`improvement-log-check`) |
| 2 | agent | [agents/improvement-agent.md](agents/improvement-agent.md#L298) *Amending a draft* | Add: before writing the amendment note, re-measure every routed row and every deferral whose return condition names a live observation that the draft carries forward. Rewrite met rows in place, and say per row what could not be re-measured | IMP-1040 | N/A — instruction | N/A |
| 3 | agent | [agents/improvement-agent.md](agents/improvement-agent.md#L173) step 6, third bullet | Make it read "in a gate's code **or in an instruction's prose** (*every entry whose X is Y*) alike", and require the literal's match count in the change row | IMP-0660, IMP-1042 | N/A — instruction | N/A |
| 4 | agent | [agents/build-agent.md](agents/build-agent.md#L92) step 5, the runner section, and [*A Deferred Step*](agents/build-agent.md#L227) | (a) Step 5 always passes `--result-out "$ARTIFACT_DIR"/run-build-result.json`. (b) New subsection *Change-scoped runs*: use `--changed-since last-green` only for an inner-loop build that goes no further than the first environment of `instance.yaml` → `environment_chain`. Run `--plan` first and quote its counts. Any build whose content will be promoted from that environment runs unscoped. The first `last-green` run is full. (c) The manifest records `scoped`, `skipped_unchanged`, `base_ref`, and `full_run_reason` when present. (d) A `skipped_unchanged` step goes under `steps_not_executed` with `reason: skipped-unchanged`. It is not a deferral, does not increment `consecutive_deferrals`, and is counted on its own gate-output line | IMP-1051, IMP-1053 | N/A — instruction (row 5(b) makes (a) the default as well) | N/A |
| 5 | script | `.engine/scripts/run-build.py` (the instance file is a wrapper, unchanged) | (a) A step also runs when any repo file its `command` names has changed, whatever its `paths:` says. (b) With no `--result-out` and `ARTIFACT_DIR` set, write to `$ARTIFACT_DIR/run-build-result.json`. Fixtures `step-runs-when-its-own-script-changes` and `result-defaults-into-artifact-dir` | IMP-1053, IMP-1054 | YES — `--selftest`; re-run of this review's planner probe: the 3 changed-script cases must leave all 4 consumer steps `would_run` | already wired — it is the runner build-agent's step 5 invokes, not a `verify-*.py` gate |
| 6 | script | `scripts/verify-artifact-provenance.py` and `.engine/` copy (identical) | New `--env <name>`. If the manifest or `run-build-result.json` says `scoped: true`, fail unless `--env` is the first entry of `instance.yaml` → [environment_chain](instance.yaml#L42). Without `--env`, fail with a message saying to pass it. Unscoped artifacts are unaffected. Four fixtures cover scoped and unscoped, with first, later and no environment | IMP-1052 | YES — `--selftest`; corpus: 0 manifests on disk carry `scoped`, so **0 findings, correct because no scoped build has run** | `SUITE_GATE_EXEMPT` (existing entry at [L731](scripts/verify-build-config.py#L731): its input is a finished artifact); invoked at pipeline-agent activation step 3 |
| 7 | agent | [agents/pipeline-agent.md](agents/pipeline-agent.md#L64) activation step 3, plus a paragraph after it | Step 3 passes `--env <env>`. **A change-scoped artifact deploys only to the first environment, and only what it contains.** The solution import always runs (D-1). A Code App whose package step was skipped is pushed only if `git diff --name-only <git_head of the build last pushed there> -- <app folder>` prints nothing, recorded as `NOT RUN — unchanged since <build>` with that output. With no such base it is a `DEPLOYMENT FAILED` whose remedy is a full build (D-2). This is a named exception to the "every post_deploy step runs" rule. **Before any later stage**, the artifact named must be the newest one deployed to the first environment, and unscoped, because Pipelines promotes what that environment holds | IMP-1052 | Partly — the unscoped half via row 6; "newest deployed" is instruction only | N/A |
| 8 | other | [config/revitalise-grant-automation-build.yml](config/revitalise-grant-automation-build.yml#L1068) | **Only if D-1 is "always pack".** Remove `paths:` from `pack-managed`, `pack-unmanaged` and `component-shape-packed`, and move the `paths_solution` anchor onto `lint`, which stays scoped. +11.5 s per scoped run | IMP-1052 | YES — `verify-build-config.py` exit 0; `--plan` shows the three steps `would_run` for a code-app-only change | N/A |

**Constraint budget:** 0 of 3 used.

---

## 4. Retirements

> Retirement check performed: 88 live constraints, 10 retired (derived by grep). None is redundant. One candidate for **rewording**, not retirement: [C-TECH-030](constraints/technology/technology-constraints.md#L71) says deployments to Test, Acc and Prd use the build-agent artifact, but on this project those environments get no artifact (Pipelines exports from DEV). Left for the next review, because changing a HARD row's wording is not something this batch needs.

---

## 5. Findings left unprocessed

**Deferred:** none

Every unread entry is processed here. Dispositions to write **at apply** (`observable_at` was read for each):

| Entry | Disposition | Why |
|---|---|---|
| Parked-review false warning (IMP-1039) | **CLOSE** on row 1 (V1) | needle on the new fixture name |
| Amendment did not re-measure carried rows (IMP-1040) | **DEFER** (V3) | row 2 lands, but the defect was seen live and nobody here can re-run it. Return: the next amendment of a parked review re-measures its live rows |
| Intake flow does not write total cost live (IMP-1041) | **DEFER** (V3) | Return: the intake flow is deployed from source and `verify-live-flow-definitions.py --env dev` reports no difference for it |
| Approved filter matched nothing (IMP-1042) | **CLOSE** on row 3 (V1) | |
| 35 stale envelope tests (IMP-1043) | **CLOSE** (V1) | fix landed: needle `REWRITTEN 2026-10-05 to TAD rev 16` in the envelope contract tests |
| Hotfix reversed an approved decision unrecorded (IMP-1044) | **CLOSE** (V1) | fix landed: needle `"rev_application.rev_refereejobtitle": "nvarchar"` in `config/attribute-type-lock.json`. The check proposal is declined, as stated in C5 |
| Secured-column pin and vacuous order test (IMP-1045) | **CLOSE** (V1), narrowed | the pin is now 42 with your ruling, and the vacuous test was fixed. The derived-pin proposal is declined. Residual is R3 |
| Deferral expiry found at step 45 (IMP-1046) | **DEFER** (V1) | Return: D-3 answered |
| Generator wrote one of two copies (IMP-1047) | **CLOSE** (V1) | needle `DEFAULT_OUTS = (` in the generator |
| Literal-id deferral test (IMP-1048) | **CLOSE** (V1) | needle `(TAD rev 17 deleted TD-011)` |
| Nested queries not checked for secure data (IMP-1049) | **DEFER** (V1) | Return: R1 lands, and removing `secureData` from the three queries fails the suite |
| Wrong change order cited (IMP-1050) | **DEFER** (n/a) | Return: R2 lands |
| Build scoping capability (IMP-1051) | **CLOSE** on row 4 (n/a) | |
| Scoped artifact consumed as complete (IMP-1052) | **DEFER** (V3) | rows 6–7 land, but the defect is a live deploy. Return: the first scoped artifact is handed to pipeline-agent and handled by row 7 |
| `last-green` base never found (IMP-1053) | **CLOSE** on rows 4 + 5(b) (V1) | |
| Gate skipped when its own script changes (IMP-1054) | **CLOSE** on row 5(a) (V1) | |

**Routed work** (to be re-measured at apply):

| # | To | What |
|---|---|---|
| R1 | development-agent | Assert `secureData` on the three failure-lookup queries nested under `Describe_the_failure`, and decide the four older unsecured cases explicitly |
| R2 | development-agent | Replace CO-008 with ADR-070 in both apps' `fieldCatalogue.test.ts` ([L22](src/code-apps/trustee-review-portal/src/domain/fieldCatalogue.test.ts#L22), [L60](src/code-apps/trustee-review-portal/src/domain/fieldCatalogue.test.ts#L60), same lines in the cards app). Correct the rev 15 table in the Create Envelope [notes](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.notes.md#L429) ("Routing 1 / 2", `Fill_the_tabs`) |
| R3 | development-agent | Add existence checks before the two position comparisons at [L139–140](src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L139) of the envelope contract tests |

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1048 | 1050 (+2 logged by this review) |
| Digest | **STALE now**: `generate-known-failure-modes.py --check` exit 1, and that check is build step 125 | regenerated at apply, or before the next build (see *What is still open*) |

---

## What is still open

**~~The 16 entries are not stamped with this review, and the digest is stale.~~** *Resolved at apply, 2026-10-05: the stamp write succeeded on this dispatch and the digest was regenerated.* Draft-time text, kept for the record: the harness refused my write to `logs/improvement-log.jsonl` when I tried to add `reviewed_in`, and then refused a read-only `git diff` of it. I did not retry by another route.

**Thirteen gate-baseline entries expire on 13–14 October**, starting at [gate-baselines L187](config/gate-baselines.json#L187), and [EX-004](contract/known-exceptions.json#L36) expires on 16 October. [TD-007](contract/tad-deferrals.json#L16) expires on 19 October. Any build after the 13th halts on these, as the build in IMP-1046 did, unless the owners clear or re-date them first.

**The engine change is unpublished.** Push `.engine` first, check that `git -C .engine branch -r --contains HEAD` lists the remote branch, and only then push the instance branch.

## What you need to decide

**D-1 — Should a scoped build always pack the solution, so DEV always gets a fresh import?**

**Problem** — A code-app-only scoped build leaves no solution zip, and skipping the DEV import is unsafe: the last green build may never have been deployed, and the import also clears live drift.
**Suggested fix** — Always pack (row 8, +11.5 s). The ~5-minute DEV import stays on every deploy.
**What happens if you don't** — Pipeline-agent cannot deploy a code-app-only scoped artifact at all. It refuses, and you run a full build instead.
[pack-managed](config/revitalise-grant-automation-build.yml#L1068)

---

**D-2 — When a scoped build skips an unchanged Code App, may pipeline-agent skip that app's push?**

**Problem** — The skipped app has no package in the artifact, and the rule today is that every declared post-deploy step runs.
**Suggested fix** — Skip only with proof: a `git diff` from the build last pushed to DEV shows no change in that app's folder. Otherwise refuse and ask for a full build.
**What happens if you don't** — Every deploy of a scoped build that touched one app needs a full build first, so most of the time saved on deploy builds is lost.
[post-deploy rule](agents/pipeline-agent.md#L480)

---

**D-3 — Where should an approaching deferral or baseline expiry reach you?**

**Problem** — Expiry is only checked by the build gate, so it is found when a build halts. That happened today, and 13 more entries expire in 8–9 days.
**Suggested fix** — Before lead-agent relays any "Approved for build", it lists every register entry expiring within 14 days, with its owner. The rule would be drafted in the next review.
**What happens if you don't** — The next build after 13 October halts on expired baselines, exactly as today's did.
[tad-coverage expiry check](scripts/verify-tad-coverage.py#L589)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-05-improvement-review-2.md

Findings processed: 16 NEW  →  9 clusters
Regression check:   11 prior changes audited, 1 class recurred (after a prose fix; kept in prose, reason in C4)
Proposed:           0 constraints (cap 3), 3 gates/scripts, 0 skill/knowledge edits,
                    4 agent-file edits, 0 retirements   (+1 config change conditional on D-1)
Altitude calls:     2 generalised from instance to class, 6 left as notes
Digest:             will regenerate — 1050 entries; currently STALE (refused log write, see §6)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verified here:** `run-build.py --selftest` PASS; `--plan --changed-since last-green` ran (101 would run and 1 skipped for context, which is correct: no result carries a `git_head` yet); the planner probe over 3 changed-script cases (4 consumer steps skipped each time, the defect reproduced); `verify-build-config.py` on the scoped config exit 0; the row 1 patch on a scratch copy (warnings 2 → 1, selftest 107/107). **Not verified:** anything live; the result-path fix until a full build runs; rows 5–7, which are not written yet.

---

## Applied — 2026-10-05

**Keyword received:** *"D1-3 agreed with suggestions. Approve improvements"* (reviewer, relayed by lead-agent, 2026-10-05). **D-1 yes:** always pack the solution, so row 8 applies. **D-2 yes:** skip an unchanged Code App push only with `git diff` proof, otherwise refuse. **D-3 yes:** the expiry rule is drafted in the next review.

**Re-verified before applying (step 8).** No entry was appended after the draft (the highest id was still IMP-1054), and none carries `corrects` against these 16. The three routed rows were re-measured and all three are still open: R1 (the three nested queries are named by no test), R2 (`CO-008` still at lines 22 and 60 of both `fieldCatalogue.test.ts`, and `Routing 1 / 2` still at [L429](src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.notes.md#L429) of the notes), R3 (the two comparisons at [L139](src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L139) still have no existence check). IMP-1041's premise still holds: [pipeline.log](logs/pipeline.log#L1) has no 5 October line.

### What has been built

1. **A review that deferred everything no longer reads as "still parked"** — [verify-improvement-log.py](scripts/verify-improvement-log.py#L2475), both copies identical. A deferral now counts as evidence the keyword was given. The false IMP-0298 warning is gone from the real log. **Deviation, stated:** the drafted fixture alone could not fail. An expected text of `''` asserts nothing, and a warning rung exits 0 either way, so I added a banned-text row for it. With the fix removed, the fixture now fails. Selftest: 108 fixtures. Logged as IMP-1055.
2. **A selector in instruction prose gets the same check as one in gate code** — [improvement-agent.md step 6](agents/improvement-agent.md#L173). The change row must now carry the literal's match count. The worked example was re-measured: `gate == 'none'` matches 0 of 8 exceptions.
3. **An amendment re-measures what it carries forward** — [improvement-agent.md *Amending a draft*](agents/improvement-agent.md#L309).
4. **build-agent writes its result where `last-green` looks, and has rules for scoped runs** — [step 5](agents/build-agent.md#L92) and [*Change-scoped runs*](agents/build-agent.md#L250).
5. **The runner runs a step whose own script changed, and writes the result into the artifact directory by default** — [command_inputs](.engine/scripts/run-build.py#L255) and [the default path](.engine/scripts/run-build.py#L485). The two new fixtures were each mutation-checked: each fails with its fix removed. **Planner probe, re-run:** with each of the 3 changed scripts in turn, the consumer step comes back `would_run`, so all 4 consumers run (`component-shape-packed`, both bundle-budget steps, `lint`). At draft time all 4 were `skipped_unchanged`.
6. **The provenance gate refuses a scoped artifact beyond the first environment** — [evaluate_scope](scripts/verify-artifact-provenance.py#L214), both copies identical, new [`--env`](scripts/verify-artifact-provenance.py#L427). Selftest: 14 fixtures, the 4 drafted plus one that reads the scope flag and the environment chain from disk. The engine fixtures use a generic chain. **Corpus:** 0 artifacts on disk carry `scoped`, so there are **0 findings, which is correct because no scoped build has run.** The newest real artifact (20261005-5) passes with `--env dev` and with `--env prd`.
7. **pipeline-agent's scoped-deploy rule** — [activation step 3](agents/pipeline-agent.md#L81), with a one-line cross-reference at the [post-deploy rule](agents/pipeline-agent.md#L484).
8. **The solution is always packed** — [pack-managed](config/revitalise-grant-automation-build.yml#L1068) has no `paths:`, and neither do `pack-unmanaged` or `component-shape-packed`. The anchor moved to [lint](config/revitalise-grant-automation-build.yml#L1104). The [header comment](config/revitalise-grant-automation-build.yml#L53) records D-1. A code-app-only change now plans all three pack steps `would_run` (89 would run, 12 skipped). **A side effect to know about:** row 5 now makes `component-shape-packed` run when its own script changes. Before row 8, the pack steps would still have been skipped in that case, the zip would have been missing, and the step would have failed. Row 8 closes that gap.

### Dispositions written

| Closed (10) | Deferred (6) |
|---|---|
| IMP-1039, 1042, 1043, 1044, 1045 (narrowed, as drafted), 1047, 1048, 1051, 1053, 1054 | IMP-1040, 1041, 1046, 1049, 1050, 1052 |

Every closure has an `evidence_grep`, and each needle was checked to match one line before it was written. **IMP-1046's return condition, "D-3 answered", is applied word for word as approved, and it is already met.** Its `deferred_reason` says so, so the next review picks it up and drafts the rule.

### Digest

1051 entries (the 1050 at draft time, plus IMP-1055), 1033 distinct lessons, 83 recurring classes. Regenerating moved the registered digest-size line from 617 to 618, and I corrected it in both copies of [generate-known-failure-modes.py](scripts/generate-known-failure-modes.py#L45).

### Still open after apply

**The engine change is unpublished, and there is more of it now.** `.engine` holds uncommitted edits to 7 files on top of `592b245`, which is on no remote branch. The order still applies: commit and push `.engine`, check that `git -C .engine branch -r --contains HEAD` lists the remote branch, and only then commit and push the instance pointer.

**IMP-1055 is unread.** This review logged it while applying row 1, and the next batch review owns it.
