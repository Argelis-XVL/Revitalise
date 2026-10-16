# Improvement Review — 2026-10-16

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 31 `NEW` → 13 clusters (26 unread, 2 fixed-in-flight, 1 reviewer-deferred entry whose return condition has been met, and 2 logged by this review while drafting)
**Trigger:** post-deploy batch — the DEV deploy of build `revitalise-grant-automation-20261009-3` (flow 1009 only, `wbs:0.4`, WI-0028) stopped before any write at the provenance check, [pipeline.log L344](logs/pipeline.log#L344)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT, parked at its gate.~~ **APPLIED 2026-10-16**, on the reviewer's "approve improvements" (sent as its own message, relayed verbatim by lead-agent, [routing.log 16:38](logs/routing.log)). All 12 rows applied. One row was narrowed (row 4) and two dispositions differ from the draft (IMP-1105 closed instead of deferred; IMP-1121 withheld as the draft made conditional). See §9. D-1 was not answered, and IMP-1124 stays deferred on it.
**WBS:** system work, `wbs:system`, not billable. The findings belong to wbs:0.2, 0.4, 3.4, 4.2, 4.6 and 5.1–5.6, as each entry records.

---

## Summary

Twelve changes are proposed: two gate scripts, five knowledge or skill edits, four agent-file edits and one template edit. No new constraints, no retirements. The biggest is to the flow-definition gate: it gets four checks for flow shapes that imported cleanly but then would not save or would not turn on in DEV. Two other checks in that gate were proposed nine days ago and never built. Two of the four new checks catch the real defects in this repository's own git history.

You have one decision to make (D-1, about a monthly flow that may not turn on). Six live observations are listed under "What is still open". This review cannot make them, so those findings stay open honestly instead of being closed on paper.

## What has been built

Nothing yet. This is a draft. What it proposes:

1. **The flow-definition gate learns four more shapes that the designer or the activation step rejects** — [verify-flow-definition-language.py](scripts/verify-flow-definition-language.py#L547), run as the HARD build step [flow-definition-language](config/revitalise-grant-automation-build.yml#L710). The four shapes are a Switch with no case, a variable set to a bare empty string, a scheduled trigger with weekdays on a daily frequency, and a raw id written into a lookup column. On today's 11 flows the checks find nothing, which is correct because every instance has been fixed. Replaying the history proves they work: the three committed versions before the fixes trip the weekday check on the Daily Summary and the lookup check on Safeguarding Action Completion.

2. **The gate's self-test runs on every build again** — [verify-build-config.py L633](scripts/verify-build-config.py#L633). The build preflight treated the flow gate as "has a negative test" because its step name happens to appear in an unrelated test. So it never ran the gate's own self-test, and when the narrative rebuild broke four of that self-test's assertions, nothing noticed. The fix: a name counts as registered only when it is in a test's title. Measured: 22 of 23 registered gates are unaffected, and this one gate is the only change.

3. **One knowledge section collects the designer-save and activation facts from this batch** — [power-automate.md, Hand-Authoring](knowledge/technology/power-automate.md#L444). Thirteen dated facts, each from a live observation or a documentation page read today. None of them was in the file: a grep for each key phrase returned 0.

4. **The domain knowledge files stop saying "UK only"** — [regulations.md L38](knowledge/domain/regulations.md#L38), [compliance-requirements.md L22](knowledge/domain/compliance-requirements.md#L22). They now cite the amended SDD residency requirement instead of restating it. This also closes the old Swiss-region finding, because the legal office's answer of 16 October meets its return condition.

5. **Four rule edits for the agents that wrote the neutral-terms design** — the A-09 / ADR-075 incident produced eight findings from three agents in one day. They reduce to four habits: show a defaulted open question as a worked example; compare an SDD amendment and a TAD revision written in parallel before either goes to you; state a security guarantee as the property it protects; and judge a flow's size against what someone can maintain, not against the platform's 500-action ceiling.

## Elements added

| Element | Where |
|---|---|
| Checks 14–17 and their self-test fixtures | [scripts/verify-flow-definition-language.py](scripts/verify-flow-definition-language.py#L547) |
| Knowledge subsection *Designer save and activation — what import does not check* | [knowledge/technology/power-automate.md](knowledge/technology/power-automate.md#L444) |
| Skill subsection *A test double is a platform contract too* | [how-to-verify-a-platform-contract.md](skills/how-to-verify-a-platform-contract.md#L825) |
| Architect-agent subsection *An ADR states what it protects and what it costs* | [architect-agent.md](agents/architect-agent.md#L190) |
| Dev Summary template line *SDD changes owed* | [dev-summary-template.md §7](templates/dev-summary-template.md#L39) |

## Elements changed

| Element | Change |
|---|---|
| [verify-build-config.py](scripts/verify-build-config.py#L633) and its engine twin | registration needs the step name in a test title |
| [lead-agent.md parallel-dispatch rule](agents/lead-agent.md#L247) | adds the case of "same reviewer answer, two documents" |
| [lead-agent.md tier rule](agents/lead-agent.md#L121) and [WORKFLOW.md step 4](agents/WORKFLOW.md#L148) | the tier goes on every routing line, default included |
| [plan-agent.md open questions](agents/plan-agent.md#L61) | a default is shown as an example, and it follows the direction of a reversing decision |
| [Skill §4 register](skills/how-to-verify-a-platform-contract.md#L499) and [§12c](skills/how-to-verify-a-platform-contract.md#L948) | per-environment setting rows; "kept" rules traced to the as-is process |
| Two domain knowledge files | residency text cites SDD NFR-009 as amended |

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-10-07](docs/improvements/2026-10-07-improvement-review.md). It applied rows 1–10 on 2026-10-08 and declined row 11.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Row 1 — AI Builder facts in power-automate.md | 2026-10-08 | `platform-contract-guessed-not-groundtruthed` | **YES, as a reader miss** — IMP-1117: plan-agent wrote "the redaction model stays in-region". Fact (d) at [power-automate.md L412](knowledge/technology/power-automate.md#L412) already said prompt models in a Switzerland environment are cross-geo, but plan-agent does not load that file (grep of `agents/plan-agent.md` for `power-automate.md`: 0) | **The prose was right and its reader was wrong.** A plan-agent load line would be wrong, because it does not author platform detail. The fix belongs at the step that brings the TAD's evidence to plan-agent: row 10 |
| Row 2 — Select/Filter inputs secured | 2026-10-08 | `gate-fired` | NO | Working |
| Row 3 — Solution Checker recursive-loop note | 2026-10-08 | `untriaged-tool-warning` | NO | Working |
| Row 4 — live read recipes | 2026-10-08 | `capability-established` | NO | Working |
| Row 5 — local simulator + mutation and crossing rule | 2026-10-08 | `oracle-comparison-covers-only-enumerated-combinations` | **YES, twice.** IMP-1099 (09 Oct): no test put a failure into a multi-window text. IMP-1109 (12 Oct): the simulator accepted a substring start the platform rejects | **Prose recurred, so it escalates to a gate.** IMP-1099's half was already escalated in flight: check 13 executes the loop exit. IMP-1109 is a new property, simulator leniency, which the row-5 rule did not cover. Row 7 below adds it, and the simulator now carries the platform rule with a boundary test |
| Row 6 — npm audit remedy order | 2026-10-08 | `gate-fired` | NO | Working |
| Row 7 — audit steps moved early | 2026-10-08 | `gate-fired` | NO | Working |
| Row 8 — provenance build.log matcher | 2026-10-08 | `two-invocation-paths-disagree` | NO. Today's halt is a different rule in the same gate (`no-test-report-names-this-build`), and it **fired correctly**: no test report names build 20261009-3 | Working. The gate did its job and test-agent has been routed |
| Row 9 — limit counting convention | 2026-10-08 | `platform-contract-guessed-not-groundtruthed` | Class neighbour IMP-1121: an expression of 12,701 characters against the 8,192 limit | **Defended.** The narrative suite's PlatformLimits test caught it before any build. It checks every flow, not only the narrative one ([test_solution_flows.py L65](src/tests/narrative/test_solution_flows.py#L65)) |
| Row 10 — inventory before a constant list | 2026-10-08 | `existing-asset-not-considered-in-design` | NO | Working |

**Recurred after a prose fix:** rows 1 and 5. Row 1 is handled by row 10 of this review. Row 5's recurrence was already escalated to a gate (check 13) in flight, and its new half is row 7.
**Recurred after a gate:** none. **New `gate-cannot-fail` finding:** IMP-1123 (below), from re-measuring IMP-1122.
**Closure level audit:** every prior closure at V2 or higher carried `reobserved`. Nothing to reopen.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-contract-guessed-not-groundtruthed — flow shapes that import but will not save or turn on  (x7: IMP-1095, IMP-1098, IMP-1099, IMP-1104, IMP-1105, IMP-1106, IMP-1107)
Altitude:   CLASS — x91 in the digest; the general gate for flow definitions already exists, so this adds checks to it, never a new script
Ladder row: "a tool could catch it mechanically" + "second instance → generalise" (IMP-1105 is the second raw-lookup instance after IMP-1010, whose knowledge line already existed)
Becomes:    checks 14–17 in scripts/verify-flow-definition-language.py (row 1); facts in power-automate.md (row 3)
Retires:    nothing — no instance gate exists for any of the four shapes
Cites:      IMP-1095, IMP-1098, IMP-1099, IMP-1105, IMP-1106, IMP-1107
Residual:   UpdateRecord (upsert) vs UpdateOnlyRecord is NOT gated: 12 UpdateRecord writes remain in 5 flows,
            and whether each should create a missing row is a design question, not a shape error. Routed R4.
            Check 15 catches the literal "" only; a value computed to empty at runtime is invisible to it.
            Checks 12 and 13 stay in the instance wrapper with the new ones. skills/how-to-promote-a-finding.md §6
            says stay client-specific when unsure: one tenant has measured these, and an engine move ships to every client.
```

`IMP-1104` is **rejected**, not applied. Its proposed fix (frequency Week plus weekDays) was withdrawn by `IMP-1106`. The re-observation `IMP-1107` showed that removing weekDays from a Day trigger is enough. Check 16 rests on 1107's observation plus the documentation, not on 1104.

```
CLUSTER: platform facts measured live, outside the definition  (x3: IMP-1096, IMP-1100, IMP-1102)
Altitude:   INSTANCE facts with a general cause — one instance each
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge line
Becomes:    three facts in the row-3 knowledge section (callback URL refuses app-only token; webhook registration name
            is an environment variable; import over an Activated flow leaves it Draft)
Retires:    nothing
Cites:      IMP-1096, IMP-1100, IMP-1102
Residual:   IMP-1096 still needs an architect decision on the callback-URL check (routed R3). No gate can tell a
            registration name from a constant, so IMP-1100's rule relies on the author reading it.
```

```
CLUSTER: test double more lenient than the platform  (x1: IMP-1109)
Altitude:   CLASS of method — the same failure as row 5 of the last review, arriving from a new side
Ladder row: "an agent had the information and still did the wrong thing" → skill edit
Becomes:    skill subsection (row 7); substring fact in row 3
Retires:    nothing
Cites:      IMP-1109
Residual:   the proposed substring gate is NOT built: 87 substring() calls across 11 flows, 25 in the safe concat form,
            so the candidate would raise 62 findings nobody has adjudicated. Deferred with that count.
```

```
CLUSTER: platform-field-length-limit-unenforced  (x1 new: IMP-1121; x3 in the class)
Altitude:   CLASS — already defended
Ladder row: none new. Read "Defended by" first: the PlatformLimits test checks every flow at 8,192 and caught this
Becomes:    a knowledge line (reuse an intermediate through a Compose) in row 3; no new gate
Retires:    nothing
Cites:      IMP-1121
Residual:   the defending test file src/tests/narrative/test_solution_flows.py is UNTRACKED today (git status ??).
            Closure is conditional on it being tracked at apply time, otherwise WITHHELD (routed R5).
```

```
CLUSTER: gate-cannot-fail — a selftest that runs nowhere  (x2: IMP-1122, IMP-1123)
Altitude:   CLASS — x57; fix the preflight rule that decides whether a selftest runs, not one CI line
Ladder row: "a tool could catch it mechanically"
Becomes:    verify-build-config.py registration rule (row 2); the check-12 self-test plant moves to the owned fixture (row 1)
Retires:    nothing
Cites:      IMP-1122, IMP-1123
Residual:   IMP-1122 proposed wiring the selftest into ci.yml. Row 2 makes that redundant: the build preflight
            now executes it. A gate that is registered by title but whose test is weak is still trusted.
```

```
CLUSTER: approved document narrower than the client or the reviewer meant  (x8, one incident, A-09 / ADR-075:
         IMP-1110, IMP-1111, IMP-1113, IMP-1117, IMP-1118, IMP-1119, IMP-1120, IMP-1116)
Altitude:   CLASS — `approved-spec-silent-on-client-requirement` x4, all in this batch; plus three single-instance neighbours.
            No mechanical home: each step is a judgement only the reviewer reads. Four habit edits, each on the
            agent that made the choice
Ladder row: "an agent had the information and still did the wrong thing" / "the order of steps was wrong" (row 10)
Becomes:    plan-agent (row 9: IMP-1119, IMP-1120); lead-agent (row 10: IMP-1117, IMP-1118);
            architect-agent (row 8: IMP-1111, IMP-1113); skill §12c (row 6: IMP-1110); skill §4 (row 5: IMP-1116)
Retires:    nothing
Cites:      IMP-1110, IMP-1111, IMP-1113, IMP-1116, IMP-1117, IMP-1118, IMP-1119, IMP-1120
Residual:   nothing here can fail a build. Eight findings in one day from one design question is the size of
            the miss. The defence is that the reviewer sees worked examples and one reconciled pair of documents
```

```
CLUSTER: requirement text restated downstream drifts from its source  (x3: IMP-1114, IMP-1115, IMP-1063)
Altitude:   CLASS — `stale-claim-contradicting-rechecked-source` x34
Ladder row: "one instance, general cause" → cite, do not restate (row 4); route the owed change (row 12)
Becomes:    domain knowledge edits citing SDD NFR-009 (row 4); "SDD changes owed" line in the Dev Summary template (row 12)
Retires:    nothing
Cites:      IMP-1114, IMP-1115, IMP-1063
Residual:   no gate compares a decision table with FR text. IMP-1063 is taken into scope beyond the queue:
            it is reviewer-deferred, but IMP-1115 asks for its disposition and its return condition ("the
            customer answers the residency question") was met on 2026-10-16
```

```
CLUSTER: dispatched below the tier models.yml requires  (x1 new: IMP-1112; class neighbour `dispatched-below-required-tier` x2)
Altitude:   CLASS — third instance across two class names
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    lead-agent + WORKFLOW: every ROUTED_TO line carries `tier:<resolved>`, default included (row 11)
Retires:    nothing
Cites:      IMP-1112
Residual:   recording the tier makes a missed escalation visible to the dispatched agent's own pre-check;
            it does not decide the escalation. Measured: 8 of the last 40 ROUTED_TO lines name a tier.
```

```
CLUSTER: wrong-artefact-cited-as-evidence — evidence-map flow names  (x1 new: IMP-1097; second instance after IMP-1067)
Altitude:   CLASS by count, but the general gate measures badly, so data fix only
Ladder row: "second instance → generalise" — attempted and measured, then declined
Becomes:    nothing in this review; data fix routed to pm-agent (R1)
Retires:    nothing
Cites:      IMP-1097
Residual:   a rule "every workflow evidence value matches a flow file" scores 4 of 11 as unmatched, and 2 of
            those are true (3.4, 5.3). The other 2 are tasks not yet built, correctly not_started. A near-name
            matcher catches 3.4 and cannot catch 5.3 (REVAnonymise vs REVNarrativeScrubFreeText). The real join
            is the TAD flow table, which is a capability-sized change. R1 from the last review is still undone
            after 8 days (0 occurrences of REVNarrativeScrubFreeText in the map)
```

```
CLUSTER: seed pre-flight checks a fixed flow list  (x1: IMP-1108)
Altitude:   INSTANCE — delivery work in provisioning/, not this agent's to author
Becomes:    routed R2 to development-agent
Cites:      IMP-1108
Residual:   until it lands, narrative seeding needs -AllowInactiveFlows, which also silences the useful checks
```

```
CLUSTER: recurrence key outside the documented frequency  (x1: IMP-1124, logged by this review)
Altitude:   CLASS neighbour of IMP-1107; held at decision D-1
Becomes:    D-1
Cites:      IMP-1124
Residual:   check 16 covers weekDays only until D-1 is answered
```

Two single-entry notes:

```
CLUSTER: harness-blocks-destructive-call  (x1: IMP-1101) — REJECTED, no rule change: the refusal protocol was followed (one
         attempt, the exact command handed to the reviewer, run from the lead session at 12:50 with the outcome logged).
         Same disposition as IMP-0891, IMP-0946 and IMP-0953.
CLUSTER: instrument-scope-assumed-not-read  (x1: IMP-1103) — CLOSED: the scorer it needed was added in the same dispatch
         (src/tests/narrative/score_seeded_run.py, tracked). One instance, no rule.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [scripts/verify-flow-definition-language.py](scripts/verify-flow-definition-language.py#L547) (instance wrapper, beside checks 12–13) | **Check 14:** a Switch whose `cases` is empty or missing. **Check 15:** a SetVariable whose `inputs.value` is the literal `""` (use `@string('')`). **Check 16:** a Recurrence whose `schedule.weekDays` is set and `frequency` is not `Week`. **Check 17:** an `item/<col>` key on CreateRecord/UpdateRecord/UpdateOnlyRecord where `<col>` is `lookup` in `Entities/*/Entity.xml` and the key lacks `@odata.bind`. Self-test: one owned fixture per check; the check-12 plant at L481, which still names a live container, moves to the owned [CrossLoopReference.json](src/tests/fixtures/known-bad/flow-cross-loop-reference/CrossLoopReference.json) fixture. Docstring states each check's source and limits | IMP-1095, IMP-1098, IMP-1099, IMP-1105, IMP-1107, IMP-1122 | YES — `--selftest`; corpus today **0 findings across 11 flows** (5 Switch, 45 SetVariable, 3 Recurrence, 2 lookup writes, all clean — correct, every instance was fixed). Positive control on history: commits 85b2abd, d193a63, 5aea0d4 each give **check 16 = 1** (Daily Summary) and **check 17 = 1** (Safeguarding); 2 of 2 true | already wired — HARD step `flow-definition-language`, [build config L710](config/revitalise-grant-automation-build.yml#L710) |
| 2 | script | [scripts/verify-build-config.py L633](scripts/verify-build-config.py#L633) **and** `.engine/scripts/verify-build-config.py` L633 (same logic in both; the files differ only in two exemption entries) | A step counts as registered only when its quoted name appears on a `Describe`, `Context` or `It` title line; otherwise `_selftest_proof` runs. Self-test fixture: a suite that mentions a step only in an assertion body is not registered | IMP-1122, IMP-1123 | YES — measured: **23 quoted gate steps, 22 named in a title, 1 not** (`flow-definition-language`). That one now takes the selftest path, which exits 0 today. 1 of 1 true | already wired — HARD step `preflight-build-config`, [build config L83](config/revitalise-grant-automation-build.yml#L83) |
| 3 | knowledge | [power-automate.md, end of Hand-Authoring](knowledge/technology/power-automate.md#L444) | New subsection **Designer save and activation — what import does not check**, each line dated with its evidence: (a) a Draft import does not template-validate, so the first real check is a designer save; (b) a Switch needs at least one case; (c) a SetVariable to empty is `@string('')`; (d) `UpdateRecord` is the connector's *Upsert a row* and `UpdateOnlyRecord` is *Update a row*; (e) nothing outside a Foreach/Until may read an action inside it (check 12); (f) a loop that advances only on success needs a failure exit (check 13); (g) Recurrence `weekDays` only with `Week`, `hours`/`minutes` only with `Day` or `Week` (Microsoft Learn, read 2026-10-16); (h) an import over an Activated flow leaves it Draft; (i) a webhook trigger's registration name on a shared external account comes from an environment variable; (j) `listCallbackUrl` refuses the provisioning app-only token (`ClientScopeAuthorizationFailed`); (k) an expression is at most 8,192 characters, so put a reused intermediate in its own Compose; (l) `substring()` start must be below the length | IMP-1095, IMP-1096, IMP-1098, IMP-1099, IMP-1100, IMP-1102, IMP-1107, IMP-1109, IMP-1121 | YES — needle `what import does not check` (0 today) | N/A |
| 4 | knowledge | [regulations.md L38](knowledge/domain/regulations.md#L38), [compliance-requirements.md L22 and L54](knowledge/domain/compliance-requirements.md#L22) | Replace "100% UK … zero transfers outside the UK" with a citation: residency is as SDD NFR-009 and NFR-011 state them after Amendment A-09 (approved 2026-10-16): storage and backup in the UK or Switzerland (UK adequacy, client legal office 2026-10-16), AI prompt processing in the EU Data Boundary, flex routing off. CR-06 status becomes **resolved by A-09**, citing the SDD instead of restating it | IMP-1115, IMP-1063 | YES — `grep -c 'Zero transfers outside the UK' knowledge/domain/*.md` = 0 | N/A |
| 5 | skill | [how-to-verify-a-platform-contract.md §4](skills/how-to-verify-a-platform-contract.md#L499) | Add to the register rules: *"A per-environment setting that a consequence rests on gets one register row per environment. An earlier design's instruction about that setting ('keep it unticked') is a plan, not a reading, and is never cited as its evidence."* | IMP-1116 | N/A — instruction change | N/A |
| 6 | skill | [§12c](skills/how-to-verify-a-platform-contract.md#L948) | Add: *"A rules document's KEPT items are claims about the source too. Trace each thing it says is deliberately kept to the source's description of the current manual process. Where that process removes it by hand, it is a question for the client, not a decision."* | IMP-1110 | N/A — instruction change | N/A |
| 7 | skill | new subsection after [*A `--selftest` must not write…*](skills/how-to-verify-a-platform-contract.md#L825) | **A test double is a platform contract too.** Every function a simulator implements has its documented argument-range rule checked against the platform page, with one test per boundary (start equal to length, empty input). Test data puts an entity on the first and the last character. A simulator that is more lenient than the platform proves nothing about the boundary | IMP-1109 | N/A — instruction change | N/A |
| 8 | agent | [architect-agent.md](agents/architect-agent.md#L190), new subsection before *A default is specified…* | **An ADR states what it protects and what it costs.** (a) A guarantee that limits what may reach an output states the property — the closed set of permitted sources — and lists the current mechanism under it as one way to meet it. (b) An ADR that adds actions to a flow states the resulting action count with a one-line maintainability judgement for the flow's purpose; the platform limit is a ceiling, not a budget. (c) An ADR whose context cites a held dependency names the stages that exist only because of the hold, so lifting the hold triggers a re-weigh of the whole chain. Engine-level text; grepped for client literals before writing | IMP-1111, IMP-1113 | N/A — instruction change | N/A |
| 9 | agent | [plan-agent.md, open questions](agents/plan-agent.md#L61), after the "three moves" paragraph | *"Show every default you state as one concrete example: an input and the output it produces. 'Approved at defaults' covers only what the reviewer was shown. And when the question is a gap in a decision that reverses an earlier rule, the default follows the direction of the decision, never the behaviour it replaced."* | IMP-1119, IMP-1120 | N/A — instruction change | N/A |
| 10 | agent | [lead-agent.md parallel-dispatch rule](agents/lead-agent.md#L247) | Add a second trigger: two briefs that **restate the same reviewer answer** (typically an SDD amendment and a TAD revision) are compared before either is relayed for approval. After both return, send one short dispatch, or a resume of either, to check its restatements against the other's text and the TAD's measured evidence. The approval relay carries the result | IMP-1117, IMP-1118 | N/A — instruction change | N/A |
| 11 | agent | [lead-agent.md L121](agents/lead-agent.md#L121) and [WORKFLOW.md step 4](agents/WORKFLOW.md#L148) | "Record the resolved tier **when a dispatch is escalated**" becomes "on **every** `ROUTED_TO`, including each one batched into a `RESUMED` line: `tier:<name>` — the default included". A dispatched agent then sees `tier:standard` against its own trigger list and stops at once | IMP-1112 | N/A — instruction change | N/A |
| 12 | template | [dev-summary-template.md §7](templates/dev-summary-template.md#L39) | Add a line under Known Limitations: **SDD changes owed** — every reviewer decision taken during development that changes an FR's text, with the FR id and the decision date. lead-agent routes each one to plan-agent | IMP-1114 | YES — needle `SDD changes owed` (0 today) | N/A |

**Constraint budget:** 0 of 3 used. Every change here has a home lower on the ladder or is an instruction.

**Where rows land:** rows 5–11 edit files in `agents/`, `skills/` and `templates/`, which live in the `.engine` submodule. So does half of row 2. They need an engine commit pushed **first**, checked with `git -C .engine branch -r --contains HEAD`, and only then the pointer bump here.

---

## 4. Retirements

> Retirement check performed: 88 live constraint rows and 10 retired (derived with the anchored grep). The rows touching flow definitions and gate wiring were read: none is made redundant by checks 14–17 or by the registration change, because none names those shapes. The nearest candidate, `IMP-1122`'s proposed ci.yml line, is **not added** rather than added and later retired: row 2 makes it redundant before it exists.

---

## 5. Findings left unprocessed

**Deferred:** none

Every unread and fixed-in-flight entry is processed. Some stay **open after processing**, because the observation that closes them is a live one nobody in this session can make. Each carries `reviewed_in` and a drafted reviewer-authored `deferred_reason`:

| Finding | Level | Why it stays open | Revisit when |
|---|---|---|---|
| IMP-1095 | V4 | fix verified at source (V1); the rebuilt flow has not been saved in the designer | the reviewer opens REV \| Narrative \| Scrub Free-Text in the DEV designer after its next import and it saves |
| IMP-1098 | V4 | same | same observation |
| IMP-1100 | V4 | the env-var binding has not crossed into a managed environment | the first TST/ACC import shows the Connect name from `rev_DocuSignConnectName` without an edit |
| IMP-1102 | V3 | a platform behaviour, documented in row 3; no new import over an Activated flow yet | the next scoped import over an Activated flow records pre- and post-statecode in pipeline.log |
| IMP-1105 | V3 | the WI-0028 deploy that ships the fixed lookup stopped before any write | flow 1009 activates in DEV after the WI-0028 import with no hand edit |
| IMP-1109 | V4 | the simulator is fixed; no live run on text ending in an entity | the first DEV run of the rebuilt scrub flow on a text whose last span ends at the last character |
| IMP-1096 | V3 | needs an architect decision (R3) | architect-agent records ADR-011 intervention 4's choice |
| IMP-1097 | n/a | data fix routed (R1); gate declined on measurement | `contract/evidence-map.json` task 3.4 names `REVAcceptanceCompletion` |
| IMP-1108 | V3 | delivery work (R2) | `seed-test-data.ps1` reads required flows per data file |
| IMP-1124 | V3 | needs D-1 | the reviewer has turned Register Watch on in DEV once |

---

## 6. Digest impact

| | Before | After (predicted) |
|---|---|---|
| Log entries | 1118 | 1120 (+IMP-1123, IMP-1124) |
| Distinct lessons | 1099 | ~1099 (+2 new, −2 rejected: IMP-1101, IMP-1104) |
| Recurring classes (x≥2) | 87 | 87 |
| Digest lines | 630 | about 630 |

Regenerated with `python3 scripts/generate-known-failure-modes.py` on apply, then `--check`. The figures above are predictions, and the applied record will carry the measured ones.

---

## What is still open

**Six live observations** close nine of this batch's findings, listed in §5. Most are a minute each in the DEV designer. They do not block anything. They are what turns "fixed at source" into "fixed".

**R1 — pm-agent: correct two evidence-map values.** Task 3.4 points at `REVAcceptanceComplete` ([evidence-map.json L252](contract/evidence-map.json#L252)), and the flow is `REVAcceptanceCompletion`. Task 5.3 still points at `REVAnonymise` ([L320](contract/evidence-map.json#L320)). That part was routed on 8 October and is still undone. Until both are fixed, both tasks derive as not started although their flows exist.

**R2 — development-agent: the seeding pre-flight checks the flows this data file needs.** The proposal is in the finding: a `requiredFlows` key per data file, Intake dropped from the default, and the registration checks kept under `-AllowInactiveFlows`.

**R3 — architect-agent: decide the callback-URL check.** Microsoft's flow API refused the provisioning identity's token. Either accept the manual hash fallback, or test a signed-in user token first. Nobody should guess a header.

**R4 — development-agent: decide upsert or update for 12 Dataverse writes in 5 flows.** `UpdateRecord` creates the row when it does not exist. For each write, decide whether that is wanted. If a row was deleted on purpose, an upsert brings it back.

**R5 — development-agent: track `src/tests/narrative/test_solution_flows.py`.** It holds the only check of the 8,192-character limit and is untracked today. The closure of the expression-limit finding is withheld until it is tracked.

**Test report for build 20261009-3** is already routed to test-agent by lead-agent. It is what clears today's deploy halt. It is listed here only so this review does not repeat it.

## What you need to decide

**D-1. Should the scheduled-trigger check also cover hours on a monthly trigger?**

**Problem** — Microsoft's documentation says a schedule's hours and minutes apply only to daily or weekly triggers, and the Local Authority Register Watch is monthly with hours set ([trigger, L50](src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json#L50)); nobody has ever turned it on.
**Suggested fix** — turn it on once in the DEV designer: if it refuses, development-agent changes the trigger and the check is extended to hours and minutes; if it activates, the check stays weekdays-only and the finding closes with that observation.
**What happens if you don't** — the monthly check may sit switched off after every import, which is the hand fix the Daily Summary needed after each import until 9 October.
[Finding IMP-1124](logs/improvement-log.jsonl)

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-16-improvement-review.md

Findings processed: 31 NEW  →  13 clusters
Regression check:   10 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 5 skill/knowledge edits,
                    4 agent-file edits, 1 template edits, 0 retirements
Altitude calls:     4 generalised from instance to class, 2 left as notes
Digest:             will regenerate — ~1099 lessons, 87 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Planned dispositions

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before. Planned dispositions, simulated against a scratch copy of the log before parking (see the gate output for the result):

| Disposition | Entries |
|---|---|
| CLOSE → APPLIED (V1 / n/a, `evidence_grep`) | IMP-1099, IMP-1103, IMP-1106, IMP-1110, IMP-1111, IMP-1112, IMP-1113, IMP-1114, IMP-1115, IMP-1116, IMP-1117, IMP-1118, IMP-1119, IMP-1120, IMP-1121 (conditional on R5), IMP-1122, IMP-1123 |
| CLOSE → APPLIED (V3, with `reobserved` from the reviewer's 2026-10-09 16:42 turn-on, [pipeline.log L343](logs/pipeline.log#L343)) | IMP-1107 |
| REJECTED | IMP-1101 (no rule change follows), IMP-1104 (withdrawn by IMP-1106), IMP-1063 (requirement amended by A-09; the measured Swiss region now meets it) |
| Stays NEW, reviewer-authored deferral | IMP-1095, IMP-1096, IMP-1097, IMP-1098, IMP-1100, IMP-1102, IMP-1105, IMP-1108, IMP-1109, IMP-1124 |

---

## 9. Applied record — 2026-10-16

Re-verified before applying (step 8): `verify-improvement-log.py --check` showed 3 entries appended after the draft (IMP-1125–1127; IMP-1128 arrived during apply). **None carries `corrects` against an entry this review acts on.** They are left for the next batch. The corpus re-measured the same for checks 14–17. Routed rows R1 and R5 re-measured as still undone. The draft's prediction for row 1 (2 of 2 true per pre-fix commit) and for row 2 (23 → 22, 1 lost, 0 gained) re-measured exactly.

| # | Change | Applied at | Entries moved |
|---|---|---|---|
| 1 | Checks 14–17 + owned fixtures; check-12 plant moved to the owned fixture. `--selftest` 22 of 22 PASS; real corpus exit 0 (11 flows, 9 lookup columns); history 85b2abd / d193a63 / 5aea0d4 each flag check 16 (Daily Summary) and check 17 (Safeguarding), 9ee9e00 flags nothing | `scripts/verify-flow-definition-language.py` | IMP-1105 (APPLIED, see deviation 2), IMP-1107 (APPLIED, `reobserved` V3) |
| 2 | Registration by test title, in both copies, plus a Pester proof in `src/tests/build/VerifyBuildConfig.Tests.ps1` (the gate has no `--selftest` of its own, so the proof goes in its own test file). Preflight exit 0; the registry tests 2 of 2 pass | `scripts/verify-build-config.py`, `.engine/scripts/verify-build-config.py` | IMP-1122, IMP-1123 |
| 3 | Knowledge subsection, facts (a)–(l) | `knowledge/technology/power-automate.md` | IMP-1099 |
| 4 | Residency cites SDD NFR-009/NFR-011 as amended — **narrowed**, deviation 1 | two `knowledge/domain/` files | IMP-1115 (APPLIED), IMP-1063 (REJECTED) |
| 5 | Per-environment setting register rows | skill §4 | IMP-1116 |
| 6 | KEPT items traced to the as-is process | skill §12c | IMP-1110 |
| 7 | A test double is a platform contract too | skill, new section | none closed (IMP-1109 is V4, deferred) |
| 8 | An ADR states what it protects and what it costs | `agents/architect-agent.md` | IMP-1111, IMP-1113 |
| 9 | Defaults shown as examples, and following a reversing decision | `agents/plan-agent.md` | IMP-1119, IMP-1120 |
| 10 | Compare parallel restatements before relaying for approval | `agents/lead-agent.md` | IMP-1117, IMP-1118 |
| 11 | `tier:<name>` on every `ROUTED_TO` | `agents/lead-agent.md`, `agents/WORKFLOW.md` | IMP-1112 |
| 12 | SDD changes owed | `templates/dev-summary-template.md` | IMP-1114 |
| — | Closed with no rule change | — | IMP-1103, IMP-1106 (APPLIED); IMP-1101, IMP-1104 (REJECTED) |
| — | Housekeeping the closing checklist requires: the digest-size sentence (627 → 629 lines) in both copies of the generator | `scripts/generate-known-failure-modes.py` + engine twin | — |

**Deviation 1 — row 4 NARROWED.** The approved wording said CR-06 becomes "resolved by A-09". It now reads "**Requirement** resolved by A-09", and states that evidence is per processing service and lives in the TAD. Measurement: A-09 settles what is required and evidences no service's location, and nothing in this review measured where DocuSign, QuickBooks or SharePoint process data. The claim this removes is that those three services' residency is evidenced. That is the per-service mistake IMP-1117 records. Recorded in IMP-1115's `applied_by` too.

**Deviation 2 — IMP-1105 CLOSED, not deferred.** The draft deferred it until flow 1009 activated in DEV after the WI-0028 import with no hand edit. That happened at 13:09 today ([pipeline.log L345](logs/pipeline.log#L345)): statecode Activated, live definition identical to source with the `@odata.bind` lookup. It closes on that V3 observation. Who ticked the box is a separate question that waits on the reviewer's live tick.

**Withheld as the draft made conditional — IMP-1121.** `src/tests/narrative/test_solution_flows.py`, the only defence of the 8,192-character limit, is still untracked. The entry stays open with a reviewer-approved deferral until R5 is done.

**Still open, with reviewer-approved deferrals:** IMP-1095, IMP-1096, IMP-1097, IMP-1098, IMP-1100, IMP-1102, IMP-1108, IMP-1109, IMP-1121, IMP-1124. **Residual measured at apply:** IMP-1095 and IMP-1098 still classify as *fixed in flight* although deferred. They do not halt any build, but they will count toward the next batch until the designer save is observed.

**Measured after apply:** `verify-improvement-log.py --check` exit 0 (0 awaiting-approval, no warning; 4 unread entries belong to the next batch). Digest regenerated: 1124 entries, 1102 distinct lessons, 88 recurring classes, 629 lines. `generate-known-failure-modes.py --check` current. `verify-derived-counts.py` OK (11 of 11). `verify-engine-instance-split.py` exit 0. Rows 5–11 and half of row 2 are in the engine submodule, published first. The commits are named in the gate output.

