# Improvement Review — 2026-10-16 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 12 `NEW` → 11 clusters (the 8 unread at dispatch, 3 that test-agent and development-agent logged while this draft was being written, and 1 logged by this review; the 2 fixed-in-flight entries were processed by the previous review and are named in §5, not re-derived)
**Trigger:** post-deploy batch — the DEV deploy of build `revitalise-grant-automation-20261016-3` stopped before any write at the provenance check, [pipeline.log L347](logs/pipeline.log#L347)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT, parked at its gate.~~ **APPLIED 2026-10-17**, on the reviewer's "Approve improvements" (Xander Lykopoulos, relayed verbatim by lead-agent). Rows 1–12 applied; rows 1–3 follow the reviewer's D-1 answer rather than the draft's default; row 13 WITHHELD as the draft made conditional. See §9.
**WBS:** system work, `wbs:system`, not billable. The findings belong to wbs:5.3 and 5.6, as each entry records.

---

## Summary

Thirteen changes are proposed: five agent-file edits, four script edits (one conditional), two knowledge lines, one data row and one constraint wording change. No new constraints and no retirements. The most important pair is about the deploy check: today it accepts any test report that mentions a build, even a failed one, and lead-agent sends deploys before checking it, so two DEV deploys stopped at that check today.

One decision is yours (D-1): what a DEV deploy needs from testing. The draft follows what you have done in practice: DEV accepts any report that names the build, and Test/Acc and Production need a report that passed.

## What has been built

Nothing yet. This is a draft. What it proposes:

1. **The deploy check reads the test report's verdict, not just its existence** — [verify-artifact-provenance.py L193](scripts/verify-artifact-provenance.py#L193). Today any file under `docs/tests/` that mentions the build counts as approval, including tonight's failed report for build 20261016-3. After the change, a deploy to Test/Acc or Production needs a report naming the build whose status is PASS or PARTIAL. Replayed over every past build: 18 builds are named only by failed reports, 6 of them were deployed, and all 6 went to DEV only, with your go. So the stricter rule beyond DEV would have refused none of the deploys you actually made.

2. **lead-agent runs the same check before it sends a deploy** — [lead-agent.md, pre-dispatch checks](agents/lead-agent.md#L412). The deploy agent ran it at its own first step and stopped twice today, at 12:58 and 20:11, because no test report named the build ([pipeline.log L343](logs/pipeline.log#L343), [L347](logs/pipeline.log#L347)). Running it one step earlier sends the right agent the first time.

3. **The constraint text says what the check enforces** — [C-TECH-030](constraints/technology/technology-constraints.md#L71). It says Test, Acc and Prd, while the check also stops DEV. The new wording states both levels, per D-1.

4. **Parallel dispatches are told which git commands they must not run** — [lead-agent.md, parallel-dispatch rule](agents/lead-agent.md#L252). A development dispatch stashed the whole shared working tree to measure a baseline while another dispatch was editing the architecture document. It popped back cleanly, but it could have lost that session's work.

5. **A redesign that undoes an approved reviewer decision says so** — [architect-agent.md, supersession rule](agents/architect-agent.md#L96). The data-driven settings you asked for were moved into a fixed prompt during a simplification, and you found out only after creating the prompts in DEV.

6. **Two fixes to this agent's own instructions** — [improvement-agent.md L515](agents/improvement-agent.md#L515) and [L710](agents/improvement-agent.md#L710). The engine publish step says to push to `main`, and today the engine is on a feature branch, so following it literally would have put unreviewed work on the branch every client pins. And the instruction for changing log entries describes rewriting the whole shared log; the harness refused that today, correctly, and editing each entry's line worked.

7. **Smaller fixes and records.** The engine copy of the GUID check gets the fix the project copy already has. The improvement-log check stops saying two deferred entries count toward the batch, which they do not. Two platform facts are written down: the Dataverse create that DEV refused today, and that a Dataverse write puts the whole row into run history. The flow check that already hides personal data on reads is extended to writes, once three remaining writes are fixed. And the digest learns that a row-count check already covers the pipeline descriptions.

## Elements added

| Element | Where |
|---|---|
| Status rule in the deploy check, with selftest fixtures | [verify-artifact-provenance.py](scripts/verify-artifact-provenance.py#L193) |
| Line: create-only write is a POST to the entity set | [dataverse.md, Alternate Keys](knowledge/technology/dataverse.md#L188) |
| Line: a Dataverse write's outputs are the row | [power-automate.md, Run history is a log](knowledge/technology/power-automate.md#L337) |
| Class-defence row for counts in prose | [logs/class-defences.json](logs/class-defences.json#L60) |

## Elements changed

| Element | Change |
|---|---|
| [lead-agent.md L412](agents/lead-agent.md#L412) | provenance check before a pipeline dispatch |
| [lead-agent.md L252](agents/lead-agent.md#L252) | forbidden git commands named in parallel briefs |
| [architect-agent.md L96](agents/architect-agent.md#L96) | supersession lists reviewer decisions, kept or reversed |
| [improvement-agent.md L515](agents/improvement-agent.md#L515) | publish to the branch containing the parent commit |
| [improvement-agent.md L710](agents/improvement-agent.md#L710) | change log rows by editing each row's line, never a whole-file rewrite |
| [C-TECH-030](constraints/technology/technology-constraints.md#L71) | text states the per-environment rule |
| [verify-improvement-log.py L1657](scripts/verify-improvement-log.py#L1657) and its engine twin | census note splits reviewed fixed-in-flight entries |
| [.engine/scripts/verify-guid-syntax.py L217](.engine/scripts/verify-guid-syntax.py#L217) | quote excluded from the shape scan |
| [verify-flow-definition-language.py check 11](scripts/verify-flow-definition-language.py#L155) | covers writes as well as reads (conditional) |

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-10-16](docs/improvements/2026-10-16-improvement-review.md). It applied rows 1–12 at about 16:50 today, so the window is a few hours.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Row 1 — flow checks 14–17 | 2026-10-16 | `platform-contract-guessed-not-groundtruthed` | Class neighbour IMP-1131 (a Web API write in a provisioning script, not a flow shape) | **Working.** A different property in the same large class |
| Row 2 — selftest registration by test title | 2026-10-16 | `gate-cannot-fail` | NO | Working |
| Row 3 — designer-save facts | 2026-10-16 | `platform-contract-guessed-not-groundtruthed` | NO | Working |
| Row 4 — residency cites the SDD | 2026-10-16 | `stale-claim-contradicting-rechecked-source` | NO | Working |
| Row 5 — per-environment register rows | 2026-10-16 | `approved-spec-silent-on-client-requirement` | NO | Working |
| Row 6 — KEPT items traced to the as-is process | 2026-10-16 | same | NO | Working |
| Row 7 — a test double is a platform contract | 2026-10-16 | `oracle-comparison-covers-only-enumerated-combinations` | **Same property twice:** IMP-1131 (the seed script's mocked Web API accepted a write DEV refused) and IMP-1133 (the flow test's stand-in returns nothing from a write the platform answers with the row) | **Not a recurrence.** Both stand-ins were written before row 7 landed. IMP-1133 was found by test-agent applying exactly that rule. Two more instances keep the rule warranted; rows 9 and 10 below record the two facts |
| Row 8 — an ADR states what it protects and costs | 2026-10-16 | `workaround-accretion-after-constraint-lifts` | Class neighbour IMP-1125 | **Not a recurrence.** The reversal was in TAD rev 22, written before row 8. A new property, handled by row 5 below |
| Row 9 — defaults as examples | 2026-10-16 | `approved-spec-silent-on-client-requirement` | NO | Working |
| Row 10 — compare parallel restatements | 2026-10-16 | same | NO | Working |
| Row 11 — `tier:` on every dispatch line | 2026-10-16 | `dispatched-below-required-tier` | Measured: 7 of 9 dispatches logged after 16:51 carry a tier. The 2 without are both on one line at 16:56 ([routing.log L1449](logs/routing.log#L1449)) | **Working, re-measure next review.** The session that wrote L1449 most likely loaded lead-agent.md before the change; unverified |
| Row 12 — SDD changes owed | 2026-10-16 | `stale-claim-contradicting-rechecked-source` | NO | Working |

**Recurred after a prose fix:** none. **Recurred after a gate:** none.
**The gate that fired twice:** `verify-artifact-provenance.py` stopped two DEV deploys today on the same rule. The previous review called the first one "fired correctly", and it was. The second repeats the same routing order, so it gets a fix at the dispatch step (cluster 1). Separately, the same gate is found to accept a failed report (cluster 2).
**Closure level audit:** the previous review's two V3 closures (IMP-1105, IMP-1107) carry `reobserved`. Nothing to reopen.

---

## 2. Clusters and promotion decisions

```
CLUSTER: gate-scope-mismatch — deploy dispatched before the test report  (x1 new: IMP-1132; 2 halts today, same rule)
Altitude:   CLASS of routing order — the gate is right, and the dispatch step skipped the agent the gate asks for
Ladder row: "the order of steps was wrong" → the dispatcher runs the deploy agent's first check before dispatching
Becomes:    lead-agent.md pre-dispatch: run verify-artifact-provenance.py <artifact> --env <env> beside the
            --target-env check; on a missing or failing report, route test-agent first, and relay a FAIL verdict
            to the reviewer before a DEV deploy (row 3). C-TECH-030 text states the per-environment rule (row 1)
Retires:    nothing
Cites:      IMP-1132
Residual:   The finding's premise is partly wrong, measured: it says the 2026-10-09 scoped pushes avoided the
            check with a temp pack. The first halt was today at 12:58 (pipeline.log L343), test-agent was routed,
            and the 13:09 temp-pack push cited a build a test report by then named. Its suggested lesson ("a DEV
            scoped push is otherwise a source push with build none") is NOT adopted: it describes a way round the
            gate. lead-agent's check is prose; nothing fails if lead skips it, but the deploy agent's step 3 still does
```

```
CLUSTER: gate-reassures-wrongly — the deploy check accepts a failed test report  (x1 new: IMP-1134; x37 in the class)
Altitude:   CLASS — assert on the report's VALUE (its Status word), never on a phrase
Ladder row: "a tool could catch it mechanically" — the gate exists; it checked mention, not approval
Becomes:    verify-artifact-provenance.py (both copies, byte-identical today): the test-report check reads each
            naming report's first "**Status:**" word. For any environment after the first of environment_chain,
            or when --env is absent, at least one naming report must say PASS or PARTIAL; anything else, an
            unparseable status included, is not approval (fail closed). For the first environment, a naming
            report of any status passes, per D-1. New finding kind no-passing-test-report-names-this-build.
            Selftest: a FAIL-only report fails for tst_acc and passes for dev; a FAIL plus a PASS report passes (row 2)
Retires:    nothing
Cites:      IMP-1134
Residual:   Corpus measured before choosing the set: 49 reports under docs/tests/, every one parses — PASS 17,
            FAIL 16, PARTIAL 15, BLOCKED 1. Replay over build/artifacts/: 56 builds are named by a report today;
            18 are named only by FAIL reports and flip. 6 of the 18 were deployed, all to DEV with the reviewer's go;
            under the first-environment rule none of the 6 is refused, and 0 deploys beyond DEV are refused. So
            18 of 18 flips are true (a FAIL report is not approval) and 0 historical deploys are lost. NOT covered:
            a PASS report superseded by a later FAIL for the same build still passes, and the reviewer's APPROVED
            on a PARTIAL report lives in routing.log, which this check does not read
```

```
CLUSTER: no-assertion-on-shipped-content — Dataverse writes leave the row in run history  (x2, one incident: IMP-1133, IMP-1136; x38 in the class)
Altitude:   CLASS — check 11 already defends the READ half of this property; the write half is the second side of it
Ladder row: "second instance → generalise" — extend the existing check, never a new script
Becomes:    check 11 of scripts/verify-flow-definition-language.py extended from reads to writes: a CreateRecord,
            UpdateRecord or UpdateOnlyRecord on a table that has a column in config/personal-data-columns.json must
            set secureData "outputs" (row 13, CONDITIONAL — see residual). power-automate.md, "Run history is a log":
            "A Dataverse write (Add, Update or Upsert a row) returns the row it wrote, so its outputs carry every
            column; secure outputs as well as inputs, and make a test stand-in for a write return the row, not {}" (row 10)
Retires:    nothing
Cites:      IMP-1133, IMP-1136
Residual:   Measured over the 11 flows: 20 writes to rev_application or rev_applicant. At HEAD, 17 have no secure
            outputs (the scrub flow's 14, plus Safeguarding Action Completion 1 and Scoring Calculate and Flag 2). In
            today's working tree development-agent has secured the scrub flow's 14, leaving 3. So the extended check
            would go red on 3 writes in flows this review does not own, and the flow gate has no baseline mechanism.
            Row 13 is therefore applied only if those 3 are secured first (routed R2); otherwise it is WITHHELD and
            reported, as the previous review did for its conditional row. Precision: 3 of 3 true, on the documented
            behaviour that a write returns the row — not yet observed in this tenant's run history. A false positive
            costs one extra secured action, the safe direction. NOT covered: special-category narrative columns are not
            in personal-data-columns.json, so a table holding only those is not checked; and run history itself is
            V5, so IMP-1133 stays open on a deferral (§8)
```

```
CLUSTER: platform-contract-guessed-not-groundtruthed — create-only Dataverse write  (x1: IMP-1131; x92 in the class)
Altitude:   INSTANCE fact with a general cause — one measured refusal, written as a measurement, not as a law
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge line
Becomes:    dataverse.md, Alternate Keys: "A keyed PATCH through an alternate key with If-None-Match: * was refused
            for an absent row in DEV (404, 0x80060891, 2026-10-16). Create-only is a POST to the entity set; the
            alternate key refuses a duplicate. Measured in this tenant; the documented pattern was not" (row 9)
Retires:    nothing
Cites:      IMP-1131
Residual:   Why Dataverse refused is NOT established, and the line says so. TAD A-NS-36 still states the disproved
            claim (routed R1). Every other Web API write in provisioning/ is still tested only against mocks
```

```
CLUSTER: workaround-accretion-after-constraint-lifts — approved decision reversed inside a supersession  (x1 new: IMP-1125; x2 in the class)
Altitude:   CLASS neighbour of IMP-1113; a different property: a reviewer decision carried only inside a mechanism
Ladder row: "an agent had the information and still did the wrong thing" → agent-file edit
Becomes:    architect-agent.md, after the IMP-0692 table: an ADR that supersedes another lists every reviewer
            decision quoted in the superseded ADR, each marked kept or reversed; each reversal is a numbered item
            in the gate output's decisions (row 5)
Retires:    nothing
Cites:      IMP-1125
Residual:   only decisions QUOTED in the superseded ADR are listed. A decision recorded only in the routing log is
            invisible to this rule. No gate can tell a reversal from a refinement
```

```
CLUSTER: concurrent-session-same-file-write — a dispatch mutated the shared tree to measure a baseline  (x1 new: IMP-1126; x4 in the class)
Altitude:   CLASS — the dispatcher is the only agent that knows another dispatch is live
Ladder row: "the order of steps was wrong" → the parallel-dispatch rule names the commands
Becomes:    lead-agent.md rung 5: a brief sent while another dispatch works in the same tree says that git stash,
            git checkout -- <path>, git reset --hard and any index change are not allowed, and gives the
            alternative: git show HEAD:<file> into the scratchpad, or git worktree add (row 4)
Retires:    nothing
Cites:      IMP-1126
Residual:   The finding asked for WORKFLOW.md "Session Boundaries, parallel-dispatch paragraph". Measured: no such
            paragraph exists (grep "parallel" in WORKFLOW.md: 0 lines), and WORKFLOW.md is read only by lead-agent.
            The parallel rule lives in lead-agent.md rung 5, so the rule goes there and reaches the dispatched agent
            through its brief. An agent dispatched alone gets no such sentence
```

```
CLUSTER: hand-maintained-count-drifts-from-source — pipeline seed descriptions  (x1 new: IMP-1127; x49 in the class)
Altitude:   CLASS — already defended. The finding's premise fails re-measurement
Ladder row: none new. The digest's "Defended by" cell for this class is empty, which is why the finding was written
Becomes:    a class-defence row: verify-derived-counts.py, claim pipeline-rev-setting-row-count, covers
            "the N rev_setting rows" in the pipeline config against len(dataverse.settingRows) (row 11)
Retires:    nothing
Cites:      IMP-1127
Residual:   Measured: the registry already holds this claim (derived-counts-registry.json L7). Replaying HEAD's text
            ("36") against today's settings files (40) gives 2 DRIFT findings, the two lines the finding names:
            2 of 2 true. The gate is SOFT (--warn-only), so it reports and never blocks. Other counts in the same
            file ("3,394-row", "three FR-062 threshold rows") are not registered
```

```
CLUSTER: gate-fires-on-nothing — GUID shape scan matched exported JSON  (x1 new: IMP-1128; x17 in the class)
Altitude:   INSTANCE fix to an existing gate; engine and project copies have diverged
Ladder row: "a tool could catch it mechanically" — the gate exists; this keeps its two copies the same
Becomes:    .engine/scripts/verify-guid-syntax.py L217 gets the project copy's quote exclusion and its comment (row 8)
Retires:    nothing
Cites:      IMP-1128
Residual:   Measured: the engine copy fails today's source with 2 false positives (the Labels and Titles prompt
            inputs) and the project copy passes, 716 elements in 123 files. No new fixture: the Pester test
            "passes against the real solution source" (BuildGates.Tests.ps1 L296) already holds the exported
            prompt JSON. No GUID can contain a quote, so the narrowing removes no true positive
```

```
CLUSTER: agent-instructions-describe-a-topology-that-changed — engine publish branch  (x1 new: IMP-1129; x9 in the class)
Altitude:   INSTANCE of the class, in this agent's own file
Ladder row: "an agent had the information and still did the wrong thing" → agent-file edit
Becomes:    improvement-agent.md "COMMITTED IS NOT PUBLISHED": find the remote branch that contains HEAD~1
            (git -C .engine branch -r --contains HEAD~1), push HEAD to it, verify with branch -r --contains HEAD.
            The "detached by default" and "## HEAD (no branch)" sentences say they hold only for a detached
            checkout. Pushing to main is a release decision (row 6)
Retires:    nothing
Cites:      IMP-1129
Residual:   Measured now: .engine is on deploy-first-learning-and-item-closure tracking its origin branch, HEAD
            11fc47b contained only by that branch. Swept for other copies of the instruction: 0 outside this file
```

```
CLUSTER: gate-reassures-wrongly — census note says deferred entries count toward the batch  (x1 new: IMP-1130)
Altitude:   INSTANCE — a message, not a rule. The proposal's premise fails when executed
Ladder row: "a tool could catch it mechanically" — the gate is right; its sentence is not
Becomes:    verify-improvement-log.py (both copies, byte-identical today): the fixed-in-flight NOTE names
            which entries are in no review (counted toward the batch) and which are "already reviewed and
            reviewer-deferred" (not counted, waiting on their revisit_when). The census line gets the same split (row 7)
Retires:    nothing
Cites:      IMP-1130
Residual:   NARROWED from the proposal. Executed, not read: classify() puts IMP-1095 and IMP-1098 in fixed-in-flight,
            and the batch rung's pending count is 8, all unread, with neither of them in it (unreviewed_fixed
            excludes an entry whose reviewed_in names an existing review, L1807). The production guard already
            releases a deferred one (L1693). So nothing is miscounted. Only the NOTE text at L1657 is wrong, and
            it is what made lead-agent's brief count them in this batch's scope
```

```
CLUSTER: harness-blocks-destructive-call — whole-log rewrite refused at draft time  (x1 new: IMP-1135, logged by this review; x17 in the class)
Altitude:   INSTANCE — this agent's own instruction names a method the harness refuses
Ladder row: "an agent had the information and still did the wrong thing" → agent-file edit
Becomes:    improvement-agent.md, the "programmatic rewrite" bullet at L710: a field change on existing log rows is
            made by editing each row's line in place, never by rewriting the whole file; ensure_ascii=False still
            binds any row that is re-serialised (row 12)
Retires:    nothing
Cites:      IMP-1135
Residual:   Additive and describes the operation as it is: the refused command and the per-line edit change the
            same rows, and the refusal is not routed round. Whether auto mode is what made today's rewrite refusable
            is not established (refusal_context recorded on the entry). The apply step will make 11 status changes
            by per-line edit, which is slower but is the operation the classifier allows
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | constraint-amendment | [C-TECH-030](constraints/technology/technology-constraints.md#L71) | **D-1 default:** *"Every deployment uses an artifact build-agent produced and a test report names. Beyond the first environment of the chain, the naming report's status is PASS or PARTIAL and the artifact is managed. No ad-hoc deploys."* Verify By keeps the command and adds `--env <env>`. If D-1 is answered differently, the sentence and row 2's first-environment branch change together | IMP-1132, IMP-1134 | YES — `python3 scripts/verify-artifact-provenance.py <artifact> --env <env>` | N/A |
| 2 | script | [scripts/verify-artifact-provenance.py L193](scripts/verify-artifact-provenance.py#L193) and `.engine/scripts/verify-artifact-provenance.py` (identical today) | Status-aware test-report check as in cluster 2; the file walk at [L296](scripts/verify-artifact-provenance.py#L296) collects each naming report's status instead of a count. Selftest gains three cases | IMP-1134 | YES — `--selftest`; replay over `build/artifacts/`: 18 of 56 named builds flip, 18 true, 0 past deploys refused | `SUITE_GATE_EXEMPT` (already, [verify-build-config.py L750](scripts/verify-build-config.py#L750): its input is an artifact plus a test report, which no build has); runs at [pipeline-agent step 3](agents/pipeline-agent.md#L68) |
| 3 | agent | [lead-agent.md L412](agents/lead-agent.md#L412), after the `--target-env` sentence | *"And run `python3 scripts/verify-artifact-provenance.py <the artifact the dispatch names> --env <env>`, the deploy agent's own step 3. If it fails on the test report, route test-agent first. If the only report naming the build is FAIL and the target is DEV, relay that verdict to the reviewer and deploy only on their go (`IMP-1132`: two DEV deploys halted on this rule on 2026-10-16)."* | IMP-1132 | N/A — instruction change | N/A |
| 4 | agent | [lead-agent.md rung 5](agents/lead-agent.md#L252), parallel-dispatch paragraph | *"A brief sent while another dispatch works in the same tree says: no `git stash`, `git checkout -- <path>`, `git reset --hard` or index change. To measure a baseline, run the gate on `git show HEAD:<file>` copied into the scratchpad, or in a `git worktree add` checkout."* | IMP-1126 | N/A — instruction change | N/A |
| 5 | agent | [architect-agent.md L96](agents/architect-agent.md#L96), after the IMP-0692 table | *"An ADR that supersedes another, in whole or in part, lists every reviewer decision quoted in the superseded ADR, each marked kept or reversed. Every reversal is a numbered item in your gate output's decisions, never only a supersession note. A simplification that undoes something the reviewer asked for is a reversal."* Engine text, grepped for client literals before writing | IMP-1125 | N/A — instruction change | N/A |
| 6 | agent | [improvement-agent.md L504–L531](agents/improvement-agent.md#L515) | Replace `push origin HEAD:main` with: `git -C .engine branch -r --contains HEAD~1` names the branch; push `HEAD:<that branch>`; verify with `branch -r --contains HEAD`. Scope the "detached by default" and `## HEAD (no branch)` sentences to a detached checkout. Pushing to `main` is a release decision, not a publish step | IMP-1129 | N/A — instruction change | N/A |
| 7 | script | [scripts/verify-improvement-log.py L1657](scripts/verify-improvement-log.py#L1657) and `.engine/scripts/verify-improvement-log.py` (identical today) | The fixed-in-flight NOTE and the census line split the state into "in no review, counted toward the batch" and "already reviewed and reviewer-deferred, not counted". Message only; no state or count changes | IMP-1130 | YES — `--selftest`, then `--check`: today's output names IMP-1095 and IMP-1098 as already reviewed, with the batch count unchanged | already wired — HARD step `improvement-log-check`, [build config L95](config/revitalise-grant-automation-build.yml#L95) |
| 8 | script | [.engine/scripts/verify-guid-syntax.py L217](.engine/scripts/verify-guid-syntax.py#L217) | `LEGACY_SHAPE_TOKEN` excludes `"`, with the project copy's three-line comment, so the two copies are byte-identical again | IMP-1128 | YES — both copies on `src/solutions/RevitaliseGrantAutomation` exit 0 (engine copy exits 1 today, 2 findings, 0 true); `cmp` of the two copies = 0 | already wired — HARD step `guid-syntax`, [build config L543](config/revitalise-grant-automation-build.yml#L543) (runs the project copy) |
| 9 | knowledge | [dataverse.md, Alternate Keys](knowledge/technology/dataverse.md#L188) | The dated create-only line in cluster 4 | IMP-1131 | YES — needle `0x80060891` (0 today) | N/A |
| 10 | knowledge | [power-automate.md, Run history is a log](knowledge/technology/power-automate.md#L337) | The write-outputs line in cluster 3 | IMP-1133, IMP-1136 | YES — needle `IMP-1133` (0 today) | N/A |
| 11 | other | [logs/class-defences.json](logs/class-defences.json#L60) | New row: class `hand-maintained-count-drifts-from-source`, property "the N rev_setting rows in the pipeline config, against len(dataverse.settingRows) of the three settings files", defended by `verify-derived-counts.py` (SOFT), `wired_at` `config/revitalise-grant-automation-build.yml (derived-counts)`, `not_covered` naming every other count | IMP-1127 | YES — `python3 scripts/verify-class-defences.py`; the digest's Defended-by cell for the class fills in | N/A |
| 12 | agent | [improvement-agent.md L710](agents/improvement-agent.md#L710) | Bullet becomes: *"To change fields on existing rows of `logs/improvement-log.jsonl`, edit each row's line in place, never rewrite the whole file: other sessions append to it, and a whole-file rewrite is a shared-resource change the harness may refuse (`IMP-1135`). Any row you re-serialise uses `json.dumps(..., ensure_ascii=False)`"* followed by the existing raw-bytes reason | IMP-1135 | N/A — instruction change | N/A |
| 13 | script | [scripts/verify-flow-definition-language.py check 11, L155](scripts/verify-flow-definition-language.py#L155) (instance wrapper, where check 11 lives) | Check 11 also inspects `CreateRecord`/`UpdateRecord`/`UpdateOnlyRecord` whose `entityName` is a table with a column in `config/personal-data-columns.json`, and requires `secureData` `outputs`. Self-test gains one known-bad write and one known-good. **Conditional:** applied only if the corpus measures 0 at apply time, i.e. R2 has secured the 3 remaining writes; otherwise WITHHELD | IMP-1136 | YES — `--selftest`; corpus today 3 findings across 20 writes, 3 true (HEAD: 17) | already wired — HARD step `flow-definition-language`, [build config L710](config/revitalise-grant-automation-build.yml#L710) |

**Constraint budget:** 0 of 3 used. Row 1 changes wording and states what row 2 enforces.

**Where rows land:** rows 3–6 and 12, and the engine halves of rows 2, 7 and 8, are in the `.engine` submodule. They need an engine commit pushed **first** to the branch that already holds the engine's HEAD (today `deploy-first-learning-and-item-closure`, not `main`), checked with `git -C .engine branch -r --contains HEAD`, and only then the pointer bump here. Row 6 changes that very instruction, and row 12 the one for editing the log.

---

## 4. Retirements

> Retirement check performed: 88 live constraint rows and 10 retired (derived with the anchored grep). C-TECH-030 was read in full. It is amended, not redundant: it is the only constraint naming the build-to-deploy chain, and the provenance script is its Verify By. No other row touches what this batch changes.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1095, IMP-1098

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| IMP-1095 | `platform-contract-guessed-not-groundtruthed` | Processed by the previous review; reviewer-deferred there. Its fix is at source. The deploy that would have imported the rebuilt flow stopped before any write, so the designer save it waits for has not happened | the reviewer opens REV \| Narrative \| Scrub Free-Text in the DEV designer after its next import and it saves (unchanged) |
| IMP-1098 | same | same | same |

The lead's census listed these two as in scope because the check's note says they are "counted toward the batch". They are not: row 7 corrects the sentence.

---

## 6. Digest impact

| | Before | After (predicted) |
|---|---|---|
| Log entries | 1132 | 1132 |
| Distinct lessons | 1106 at last generation (+4 since: IMP-1133 to IMP-1136) | about 1110 |
| Recurring classes (x≥2) | 88 | 88 |
| Digest lines | 630 | about 630 |

Regenerated with `python3 scripts/generate-known-failure-modes.py` on apply, then `--check`. The "Defended by" cell for `hand-maintained-count-drifts-from-source` fills in (row 11). The figures above are predictions; the applied record will carry the measured ones.

---

## What is still open

**R1 — architect-agent: record that A-NS-36 was disproved.** The TAD row still states that a keyed PATCH with If-None-Match creates a missing settings row. DEV refused it, and the POST that replaced it worked on two runs at 18:06 today ([routing.log L1455](logs/routing.log#L1455)). Re-measured now: the row is unchanged.

**R2 — development-agent: hide the outputs of the 3 remaining writes to the applications table.** They are in Safeguarding Action Completion (1) and Scoring Calculate and Flag (2). The scrub flow's 14, which test-agent's failed report for build 20261016-3 named, are already hidden in today's working tree (measured), and the stand-in fix is development-agent's own finding. Row 13 lands only once these 3 are done. This is delivery work under wbs:5.3, not this review's.

**The test report for build 20261016-3** exists now and is a FAIL. Under today's check that FAIL report would let the DEV deploy through; under row 2 it still does for DEV, which is why row 3 has lead-agent show you the verdict first.

**One designer save** still closes the two narrative-flow findings in §5. It waits on the next import of that flow.

## What you need to decide

**D-1. What should a DEV deploy need from testing?** — **ANSWERED 2026-10-17**, verbatim: *"tests happen in DEV. Customer tests happen in ACC. Solutions move from DEV to ACC via Power Platform Pipelines."* Applied as: a DEV deploy needs no test report; beyond DEV a PASS or PARTIAL report naming the build is required. See §9. The question as drafted is kept below.

**Problem** — The constraint text exempts DEV, the check does not, and you have deployed six DEV builds whose only test report was a FAIL, so the rules and the practice say three different things.
**Suggested fix** — DEV needs a test report that names the build, whatever its verdict, and lead-agent shows you a FAIL verdict before you say go; Test/Acc and Production need a PASS or PARTIAL report (rows 1–3).
**What happens if you don't** — The draft applies this default. The alternatives are to require a passing report in DEV too (one more test cycle before each DEV look) or to drop the DEV report entirely (the deploy check then says nothing about DEV).
[C-TECH-030](constraints/technology/technology-constraints.md#L71)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-16-improvement-review-2.md

Findings processed: 12 NEW  →  11 clusters
Regression check:   12 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 4 gates/scripts,
                    2 skill/knowledge edits, 5 agent-file edits, 1 other, 0 retirements
Altitude calls:     3 generalised from instance to class, 4 left as notes
Digest:             will regenerate — ~1110 lessons, 88 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Planned dispositions

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before. Each disposition follows the entry's `observable_at`. The set was simulated against a scratch copy of the log before parking (see the closing line).

| Disposition | Entries | Closure needle / deferral |
|---|---|---|
| CLOSE → APPLIED (V1 / n/a, `evidence_grep`) | IMP-1125 | `agents/architect-agent.md` · `kept or reversed` |
| | IMP-1126 | `agents/lead-agent.md` · `git stash` |
| | IMP-1127 | `logs/class-defences.json` · `IMP-1127` |
| | IMP-1128 | `.engine/scripts/verify-guid-syntax.py` · `[^{}\s"]{36}` |
| | IMP-1129 | `agents/improvement-agent.md` · `branch -r --contains HEAD~1` |
| | IMP-1130 | `scripts/verify-improvement-log.py` · `already reviewed and reviewer-deferred` (narrowed, see cluster) |
| | IMP-1132 | `agents/lead-agent.md` · `IMP-1132` |
| | IMP-1134 | `scripts/verify-artifact-provenance.py` · `no-passing-test-report-names-this-build` |
| | IMP-1135 | `agents/improvement-agent.md` · `edit each row's line in place` |
| CLOSE → APPLIED (V3, `reobserved`) | IMP-1131 | `knowledge/technology/dataverse.md` · `0x80060891`; `reobserved` V3 from the 18:06 DEV seed, two runs, run by lead-agent with the reviewer's approval ([routing.log L1455](logs/routing.log#L1455)) |
| DEFER from the start (V5), reviewer-authored | IMP-1133 | `deferred_reason`: knowledge line applied (row 10); the flow and stand-in fix is routed (R2); the outputs being hidden can only be seen in a run's history. `revisit_when`: the first DEV run of the rebuilt scrub flow shows the 14 writes' outputs hidden in run history |
| CLOSE → APPLIED if row 13 lands, else DEFER | IMP-1136 | `scripts/verify-flow-definition-language.py` · `reads personal column(s) or writes` (the extended finding text). If row 13 is withheld: reviewer-authored `deferred_reason`, `revisit_when` the 3 writes in R2 are secured |
| Not processed (§5) | IMP-1095, IMP-1098 | — |

Verification at draft time: `verify-improvement-log.py --check` exit 0 after stamping (0 unread; the two citation warnings gone). Simulation of the first eight entries, before the two late findings arrived: census 0 unread and 0 awaiting-approval; the schema accepted every field, `reobserved` included; the only errors were the needles that cannot exist until the changes land (expected before apply); the real log untouched. Re-run for all twelve after folding the late findings in: 0 unread, 0 awaiting-approval, IMP-1133 deferred; 11 errors, every one a needle that cannot exist until its change lands, 0 of any other kind; real log byte-identical before and after (`cmp` 0). The real log then reads exit 0, 12 awaiting-approval, no warnings. Entries appended after this draft is parked belong to the next batch. Measured, not read: `classify()` and the batch count for IMP-1095/1098; the derived-counts replay (2 of 2 true); both GUID-check copies on the real source; the test-report status corpus (49 of 49 parse) and the provenance replay (18 flips, 0 past deploys refused); secure-outputs on all 29 Dataverse writes in the 11 flows. Not verified: live Dataverse and run-history behaviour (taken from the logged DEV runs and documentation), and whether lead-agent will follow rows 3 and 4 (prose).

---

## 9. Applied record — 2026-10-17

**Re-verified before applying (step 8).** `verify-improvement-log.py --check`: no entry appended after the draft, no `corrects` against any entry this review acts on, 12 awaiting-approval. Routed rows re-measured: R1 still undone (TAD A-NS-36 unchanged); R2 still undone and not dispatched (3 of 20 writes to personal-data tables lack secure outputs). Lead's question about Power Platform Pipelines: both [pipeline-agent.md L32](agents/pipeline-agent.md#L32) and [the pipeline config L22](config/revitalise-grant-automation-pipeline.yml#L22) already describe it as the DEV → TST/ACC → PRD promotion mechanism (ADR-007), so no finding is logged.

**D-1, the reviewer's answer, verbatim:** *"D-1 answer… tests happen in DEV. Customer tests happen in ACC. Solutions move from DEV to ACC via Power Platform Pipelines."* Lead-agent's reading, which this apply confirms against the draft: DEV is where testing happens, so a DEV deploy needs no test report at all; the PASS/PARTIAL requirement applies before TST/ACC and PRD. This was the third alternative listed under D-1 ("drop the DEV report entirely"), so rows 1–3 changed shape within the approved options:

| # | Change | Where | Entries moved |
|---|---|---|---|
| 1 | C-TECH-030 text: every deploy uses a build-agent artifact; DEV needs no test report; beyond DEV a PASS or PARTIAL report naming the build and the managed artifact. D-1 quoted in the row | `constraints/technology/technology-constraints.md` | IMP-1132 (with rows 2–3) |
| 2 | Test-report rule split into `evaluate_test_reports()`: none for the first environment of `environment_chain`; beyond it, or with no `--env`, a naming report whose Status is PASS or PARTIAL (new kind `no-passing-test-report-names-this-build`). Selftest 23 of 23 PASS; a mutant without the verdict rule fails it. Real artifact 20261016-3: `--env dev` PASS, `--env tst_acc` FAIL on its FAIL report. Both copies byte-identical | `scripts/verify-artifact-provenance.py` + engine twin | IMP-1134 |
| 3 | lead-agent runs the provenance check before dispatching pipeline-agent; DEV needs no report; beyond DEV, route test-agent first | `agents/lead-agent.md` | IMP-1132 |
| 4 | Parallel briefs name forbidden git commands, with the `git show` / `git worktree` alternative | `agents/lead-agent.md` | IMP-1126 |
| 5 | Superseding ADR lists reviewer decisions kept or reversed | `agents/architect-agent.md` | IMP-1125 |
| 6 | Engine publish to the branch containing `HEAD~1`; detached-checkout sentences scoped | `agents/improvement-agent.md` | IMP-1129 |
| 7 | Fixed-in-flight NOTE split into "in no review" and "already reviewed and reviewer-deferred". Selftest exit 0; `--check` now names IMP-1095/1098 as not counted. Both copies | `scripts/verify-improvement-log.py` + engine twin | IMP-1130 (narrowed, see cluster) |
| 8 | Quote exclusion in the engine copy; copies byte-identical; both exit 0 on the real source; the known-bad fixture still exits 1 | `.engine/scripts/verify-guid-syntax.py` | IMP-1128 |
| 9 | Alternate Keys item 3: create-only is a POST | `knowledge/technology/dataverse.md` | IMP-1131 (`reobserved` V3) |
| 10 | Write outputs carry the row; the "no gate checks it" sentence updated to name check 11 (reads only) | `knowledge/technology/power-automate.md` | none closed (IMP-1133 V5, deferred) |
| 11 | Class-defence row; `verify-class-defences.py` OK, 6 defences | `logs/class-defences.json` | IMP-1127 |
| 12 | Log rows changed by per-line edit, never a whole-file rewrite | `agents/improvement-agent.md` | IMP-1135 |
| — | Housekeeping the closing checklist requires: digest-size sentence 630 → 632 in both copies of the generator | `scripts/generate-known-failure-modes.py` + engine twin | — |

**Withheld as the draft made conditional — row 13.** R2 has not been dispatched and the 3 Safeguarding/Scoring writes still lack secure outputs, so extending check 11 to writes would turn the flow gate red on work this review does not own. IMP-1136 stays open with a reviewer-approved deferral (`revisit_when`: the 3 writes in R2 are secured).

**Still open, with reviewer-approved deferrals:** IMP-1133 (V5, run history), IMP-1136 (row 13). IMP-1095 and IMP-1098 unchanged (§5).

**Gate scripts changed by this apply** (a build-agent dispatch ran in parallel; re-run these): `verify-artifact-provenance.py` (SUITE_GATE_EXEMPT; pipeline-agent step 3), `verify-improvement-log.py` (HARD `improvement-log-check`), `verify-guid-syntax.py` (engine copy only; the build runs the unchanged project copy), `generate-known-failure-modes.py` (one docstring line). Data: `logs/class-defences.json`, `logs/improvement-log.jsonl`.

**Measured after apply:** `verify-improvement-log.py --check` exit 0 — 0 unread, 0 awaiting-approval, no warnings. Digest regenerated: 1132 entries, 1110 distinct lessons, 632 lines; `--check` current; the Defended-by cell for `hand-maintained-count-drifts-from-source` now names `verify-derived-counts.py`. `verify-derived-counts.py` OK (11 of 11). `verify-class-defences.py` OK. `verify-engine-instance-split.py` exit 0 (62 unsplit duplicates, up from 61: the GUID check is identical again). `verify-build-config.py` exit 0. `verify-flow-definition-language.py` exit 0.

**Not published.** The dispatch said no commit. Rows 3–6 and 12, and the engine halves of rows 2, 7 and 8 plus the generator line, are uncommitted in `.engine` (on `deploy-first-learning-and-item-closure`). They must be committed and pushed there first, checked with `git -C .engine branch -r --contains HEAD`, and only then the pointer bump and the instance files committed here.
