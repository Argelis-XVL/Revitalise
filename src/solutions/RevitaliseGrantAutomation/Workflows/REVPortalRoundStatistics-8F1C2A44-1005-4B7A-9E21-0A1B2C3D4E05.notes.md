# REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every
action, trigger, parameter and schema property — exceeding it blocks the flow from being saved
in the designer at all (same limit `REVOpsFailureAlert-...notes.md` documents). The condensed
descriptions actually shipped in this file keep the essential fact; the full reasoning that
would otherwise live there is preserved here, keyed by the same JSON path.

---

# READ THIS FIRST — REVISION 5 (ADR-038, `wbs:6.9`, 2026-08-28) supersedes the transport

**The sections below marked ADR-030 describe a mechanism that no longer exists.** They are kept
because they are the record of *why* it was built that way and of the two defects (D-02, D-10)
that were fixed inside it, and because the whole computation half — the 46 `Filter_*` actions,
the 8 `Compose_*_categories`, `Compose_wellbeing_questions` and `Compose_response_body` — is
**unchanged and still current**. What changed is only how the flow is asked and how it answers.

| Was (ADR-030) | Is (ADR-038) |
|---|---|
| `manual` trigger, `type: "Request"`, `kind: "PowerApp"`, invoked by the Code App | `When_a_refresh_is_requested`, `type: "OpenApiConnectionWebhook"`, Dataverse row trigger |
| Five `Response`/`kind: "PowerApp"` actions returned the document to a waiting caller | Five `UpdateRecord` write-backs put the document on `rev_roundstatisticsresult`. **No response action, no caller waiting** |
| Wrote nothing | Writes exactly one row, one column set, on a table it does **not** trigger on |
| No freshness field | `staleAfterSeconds` beside `metrics` in **every** document |

**Two assumption rows retire with the mechanism they were about, and neither retires as
"proven".** `A-FLOW-01` (the `kind: "PowerApp"` trigger shape) and `A-FLOW-05` (whether a
`Response` action reached from a failure branch satisfies the Power Apps trigger contract) both
had **no subject left** the moment the trigger and the five `Response` actions were deleted.
That is a different thing from having been verified, and the distinction matters to whoever reads
the register next: the questions were never answered, they stopped being asked. `A-FLOW-03`
(Secure Outputs), `A-FLOW-04` (the failure path) and `A-FLOW-06` (`$expand`) are **all still
open** — every one of those shapes survives into Revision 5 unchanged. `A-FLOW-07` is new below.

---

## `/properties/definition/description`

REV | Portal | Round Statistics. TAD `docs/architecture/trustee-portal-visual-refresh-architecture.md`
ADR-030, section 5.1. Computes FR-057-FR-062's figures live, on demand, over the open round, on
the flow's own connection reference — never the invoking trustee's. Takes NO input parameters.
Writes nothing.

**A-nnn (Dev Summary Unvalidated Assumptions Register).** The manual trigger (`kind: "PowerApp"`)
and the `Response`/`kind: "PowerApp"` action shapes in this file are **GUESSED**, not
ground-truthed against a real export of this specific shape — this solution's other four flows
(`REVIntakeWordPressToDataverse`, `REVScoringCalculateAndFlag`, `REVScoringDailySummary`,
`REVOpsFailureAlert`) are all Dataverse-row-triggered or scheduled, and none uses the Power Apps
trigger. Microsoft's own public documentation (`microsoft_docs_search`/`fetch`, confirmed live
this session) describes the CLI surface around this mechanism in detail — `pa app list-flows`,
`pa app add flow --flow-id <id>`, the generated typed service's `Run()` method — but does not
expose the trigger/Response action's raw JSON shape, which the Power Automate designer abstracts
away for most users. This file's `ListRecords`/`OpenApiConnection` actions ARE ground-truthed —
copied from `REVScoringDailySummary`'s `Count_applications_scored_in_the_window` action, which is
real, already-authored solution source in this repository.

The cheapest verification, in order: (1) this file importing cleanly via `pac solution
pack`/`pac solution import` — a malformed workflow definition is rejected at import with a named
error, so import succeeding is real V1→V2 evidence the JSON is at least well-formed enough for
Dataverse to accept, not proof it runs; (2) a human opening it in the Power Automate designer and
saving it without a validation error — required anyway, because binding the connection reference
needs interactive OAuth consent that cannot be scripted (same "every flow imports deactivated"
constraint `REVScoringDailySummary`'s own `.data.xml` documents, TAD section 12.1 A-R34); (3) once
turned on, `pa app list-flows` showing it and `pa app add flow --flow-id <id>` in
`src/code-apps/trustee-review-portal` generating a working typed service; (4) a real invocation
as a signed-in trustee, reconciling the response against an admin-side tally (TAD section 12.2's
own V4/V5 rows — A-R33, A-R37).

**THIS FIRST VERSION computes only `applicationsReceived`** (FR-058's headline count) for the
exactly-one-open-round case. Every other TAD section 3.3 metric —
`exceptionalCircumstanceMix`, `exceptionalFundingSummary`, `breakTypeProfile`,
`genderDistribution`, `ageRangeDistribution`, `applicantTypeDistribution`, `wellbeingLastYear`,
`lifeSatisfactionDistribution`, the three OQ-039 proportions, and `applicationsPerDay` — is
explicit `null` in the response, not silently omitted. `ethnicGroupDistribution` is `null` by
design regardless (A-R24 — no data source, TAD section 3.4). Closing the rest needs: a
`List_applicants_in_round` action reading `rev_applicant.rev_gender`/`rev_agerange`/
`rev_applicanttype` for the round's applicants (Secure Outputs ON — these are the columns
`REV_TrusteeRestricted` denies a trustee at value level, section 6.3), a `rev_setting` read for
the three FR-062 thresholds, and the array-expression grouping logic (`length(filter(...))`
per option-set value) `ADR-030`/section 5.1 specifies. Deliberately not guessed here alongside
the trigger/Response shapes — two unverified guess classes stacked on top of each other in one
flow is a harder failure to diagnose than one at a time, and the trigger mechanism is the
decisive, sequencing-first question (TAD section 12.2, "Verified at: DEV, FIRST").

## Failure path (D-02 / TC-SEC-06 fix, test report §3/§4) — `A-FLOW-05`

Added to close a defect the test report found: every action in the first version ran
`runAfter: [...["Succeeded"]]` only, so a failure of `List_the_open_round` or
`List_applications_in_round` terminated the flow run with no `Response` ever reached — a bare
platform failure to the calling code app, no `rev_errorlog` row, no alert. TAD §5.1's "On failure"
row and its own mermaid flowchart (`R0 & R1 & R2 -.-> ERR`) both require the same
`rev_errorlog` + `REV | Ops | Failure Alert` pattern parent §5.14 already establishes, **and** a
non-`ok` `status` in the response so the screen degrades honestly (TAD §3.3 property 4).

**Shape copied from `REVScoringDailySummary`, not invented.** Top-level `Initialise_failure_detail`
(must be top-level — `InitializeVariable` inside a Scope/Switch/If is accepted at pack/import time
and then the designer refuses to save the flow, IMP-0137, enforced by
`verify-flow-definition-language.py`); the original body (`List_the_open_round` through
`Switch_on_open_round_count`) wrapped in one new `Scope` (`Compute_statistics`) rather than
attaching a failure branch to each of the two `OpenApiConnection` actions separately — one catch
point for both, matching `REVScoringDailySummary`'s `Summarise` scope, and simpler than duplicating
the alert wiring under two different branches of the `Switch`; `Find_the_failed_action` (`Query`,
`from: @result('Compute_statistics')`, `where: status eq Failed` — not `result(scope)[0]`, which
returns the first child regardless of which one actually failed, the same trap
`REVScoringDailySummary`'s own comment names); `Describe_the_failure` (`Scope` containing one
`SetVariable`); `Compose_run_link`; `Alert_on_failure` (`type: "Workflow"`,
`host.workflowReferenceName: "8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04"`, confirmed already a
Solution.xml root component — `grep -n "1004-4b7a" .../Other/Solution.xml` line 222 — so no
Solution.xml change was needed here). Calling that flow this way already writes the
`rev_errorlogs` row and alerts the process owner; a second, duplicate `rev_errorlog` Create action
was deliberately NOT hand-authored in this file.

**Severity: `Warning`, not `Error`.** Weighed the same way `REVScoringDailySummary`'s own comment
weighs its choice ("a missed summary loses oversight for a day but loses no data and blocks no
application"): a failed live read here costs the trustee one dashboard load — no data is lost, no
application processing is blocked, and reloading the screen simply re-invokes the flow. That is a
smaller cost than a missed daily summary, so `Warning` is at least as appropriate; `Error`/`Critical`
were rejected as over-classifying a transient, retryable, on-demand read and diluting the alert
channel a genuine intake or scoring failure depends on.

**`status: "error"` — the fifth value, chosen deliberately.** TAD §3.3's response contract comment
already reserves four non-`ok` strings for known business outcomes: `no-open-round`,
`ambiguous-round`, `truncated`, `threshold-unset` (the last not yet emitted by this first version —
FR-062's thresholds are still unset per §5.2). None of those describes a genuine action failure, so
a fifth was needed rather than overloading one of the four. `"error"` was chosen over an
alternative like `"unavailable"` because it reads directly against TAD §5.3's own diagnostic wording
("figures unavailable") without duplicating that exact phrase into a machine-readable enum value,
and a frontend-agent dispatch building the landing screen in parallel is being told to treat ANY
unrecognised non-`ok` status as the generic "figures unavailable" diagnostic — so the exact string
is not a hard coordination dependency, only a documented one.

**`Respond_error`'s body deliberately omits `roundKey`.** The Scope this catches spans
`List_the_open_round` through the whole `Switch`, so a failure could occur before or after the
round key is known. Referencing `outputs('Compose_round_key')` when that action never ran would
itself be a runtime expression error inside the failure handler — the one place that must not
fail. The body matches `Respond_no_open_round`/`Respond_ambiguous_round`'s shape instead (no
`roundKey`), which is always safe because it references only `Capture_computedOn`, guaranteed to
have run before the `Scope` starts.

**`A-FLOW-05` (Dev Summary Unvalidated Assumptions Register, continuing A-FLOW-01..04).** None of
this solution's five flows had previously exercised a `Response` action (`kind: "PowerApp"`)
reached via a `runAfter: ["Failed","TimedOut","Skipped"]` branch — `REVOpsFailureAlert`'s own
`Respond_to_calling_flow` does the same *shape* of always-respond-regardless-of-status wiring, but
its `Response` is `kind: "Http"` (a child-flow response), not `kind: "PowerApp"` (a synchronous
Power Apps caller). Whether the Power Apps trigger/response contract tolerates being satisfied from
a failure branch several actions removed from the trigger — rather than from a `Succeeded` chain
starting immediately after it, the shape every other `Respond_*` action in this file already uses —
is UNVERIFIED, for the same reason A-FLOW-01 is unverified: no live import, no designer save, no
real invocation yet (this stays V2 per the test report). Marked in the top-level description and at
`Respond_error`'s own description (the actual point the guessed shape is exercised). Cheapest
verification is the same step that closes A-FLOW-01: a human opens the flow in the Power Automate
designer after import, saves it without a validation error, then forces a failure (e.g. temporarily
disabling the `rev_SharedDataverse` connection) and confirms the code app actually receives the
`status: "error"` body rather than a bare platform failure.

## `/properties/definition/actions/.../List_applications_in_round/description`

All rows in the round, no eligibility filter — this is FR-058's *received* population, wider
than FR-038 lets a trustee *see* (TAD section 1.1, obstacle B). `Secure Outputs` is set
(`runtimeConfiguration.secureData.properties: ["outputs"]`) even though only `rev_applicationid`
is selected, because this action reads application rows at all — TAD section 6.4's control is
about the read, not the column list. `$top: 1000` is above the 434-application evidence volume
(`Round 3 Stats.pptx`) with headroom, matching the page-cap intent in section 5.1 property 3;
crossing it returns `status: "truncated"` rather than a silently short count.

## `/properties/definition/actions/.../Compose_response_body/description`

FIRST VERSION — `applicationsReceived` only. Every other section 3.3 metric is explicit `null`,
not omitted, with the full list and the reason each awaits follow-on work stated above under
`/properties/definition/description`.

## `/properties/definition/actions/Respond_error/description` — D-10 fix (test report v2, §4)

Test-agent's re-test (`docs/tests/trustee-portal-visual-refresh-test-report-v2.md`) found that the
D-02 fix above shipped a P1: the original `runAfter` on `Alert_on_failure` accepted `"Skipped"`
alongside `"Succeeded"`, `"Failed"`, `"TimedOut"`. On a **successful** run the whole failure chain
(`Find_the_failed_action` → `Describe_the_failure` → `Compose_run_link` → `Alert_on_failure`) is
skipped by design — `Find_the_failed_action` only satisfies its own `runAfter` when
`Compute_statistics` is `Failed`/`TimedOut`. `Skipped` being an accepted status on `Respond_error`
meant it then executed anyway, on every successful run, after `Respond_ok` (or whichever of the
other three business-outcome `Respond_*` actions actually applied) had already sent a body. A
four-`Response` flow responded twice on its happy path.

**Root cause.** The wiring was copied from `REVOpsFailureAlert`'s `Respond_to_calling_flow`,
described in this file's own §4 comment (Dev Summary) as "the same shape of
always-respond-regardless-of-status wiring." That flow has **exactly one** `Response` action
total, so accepting `Skipped` is correct and safe there — nothing else responds. This flow has
**four**. Copying an always-respond shape without checking how many terminal `Response` actions
the source flow has reproduces the shape without the precondition that makes it safe.

**The fix.** Removed `"Skipped"` from `Respond_error`'s `runAfter` on `Alert_on_failure` — now
`["Succeeded","Failed","TimedOut"]`, matching `REVIntakeWordPressToDataverse`'s
`Respond_500_intake_failed` exactly, the solution's only other multi-`Response` flow with the
identical `Alert_on_failure` predecessor, which already omitted `Skipped` for this exact reason.
One token changed; no new action, no Solution.xml change.

**What this closes and what it does not.** `A-FLOW-05` (above) asked only whether `Respond_error`
"will actually execute and return a body" on a genuine failure — it did not ask whether it might
execute when it should not. That one-sided framing is why D-10 was missed the first time
(test-agent's own diagnosis). The negative direction is now closed **statically**: with `Skipped`
removed, `Respond_error` cannot fire when `Alert_on_failure` is skipped, which is exactly the
successful-run case — deterministic from the platform's own `runAfter`/`Skipped` semantics, no
live run needed. The positive direction (does it fire, and does the caller receive the body, on a
genuine failure) remains open, unchanged from A-FLOW-05's original scope — still no live import.

**A residual, named rather than silently carried.** `Find_the_failed_action`'s own `runAfter` on
`Compute_statistics` accepts only `["Failed","TimedOut"]`, not `Skipped`. If `Compute_statistics`
itself were ever skipped — only reachable if `Capture_computedOn` or `Initialise_failure_detail`,
both earlier top-level actions with trivial bodies (`utcNow()`; a literal string default), themselves
failed or were skipped — no response of any kind would reach the caller. This is structurally
identical to `REVIntakeWordPressToDataverse`'s own accepted precedent shape (the flow just named as
the correct pattern to copy) and was not raised by test-agent as a defect in its own right, only as
"worth checking in the same change." Out of this fix's scope — the instruction was the one-token
`Skipped` removal, matching the precedent exactly, not a redesign of the catch boundary.

## SECOND VERSION (`wbs:6.9`, this dispatch) — `genderDistribution`, `ageRangeDistribution`,
## `applicantTypeDistribution`, `wellbeingLastYear`, `lifeSatisfactionDistribution`

Closes five of the FIRST VERSION's declared-`null` metrics. `ethnicGroupDistribution` and the three
OQ-039 proportions (`highHoursCareProportion`, `lowLifeSatisfactionProportion`,
`unableToTakeBreakProportion`) stay `null` — out of this dispatch's explicit scope, and OQ-039's
`rev_setting` thresholds are still unset regardless (A-R29). Nothing in the trigger, `Response`
shapes, or D-02/D-10 failure path changed; every action added sits inside the existing
`Compute_statistics` Scope, so the FIRST VERSION's failure-branch coverage (`Find_the_failed_action`
→ `Alert_on_failure`) still reaches every new action unchanged.

**Data sources, both ground-truthed live against DEV, not guessed.** `rev_wellbeinganswer8/9/10`
and `rev_feelingscaleanswer` live on `rev_application` itself (no join needed — TAD §5.2's own
table names them there). `rev_gender`/`rev_agerange`/`rev_applicanttype` live on `rev_applicant`,
reached via `rev_application.rev_applicantid`, a lookup. TAD §5.1's flowchart shows a separate
`List rev_applicant for the round's applicants` action; that shape was NOT used, and the reason is
arithmetic, not preference — the round's applicant IDs form a dynamic list that has to reach
`rev_applicant`'s own `$filter` somehow, and every mechanism this project has ever used for
multi-value matching (`rev_name eq 'X' or rev_name eq 'Y'`, `REVIntakeWordPressToDataverse` line
653) builds a literal string per value. At the round's own evidence volume (434) that produces a
~26,000-character filter, well past any workable request-URI length. **`$expand` on
`List_applications_in_round` avoids the join and the ID-list filter entirely**: one extra parameter,
`rev_applicantid($select=rev_gender,rev_agerange,rev_applicanttype)`, returns each application's
applicant fields nested under the `rev_applicantid` key of the SAME row. Verified live, this
session, two ways: (1) the lookup's navigation property name —
`EntityDefinitions(LogicalName='rev_application')/ManyToOneRelationships?$filter=ReferencingAttribute
eq 'rev_applicantid'` returns `ReferencingEntityNavigationPropertyName: "rev_applicantid"` (i.e.
identical to the attribute's own logical name, not a capitalised variant); (2) the raw Web API shape
— `rev_applications?$select=...&$expand=rev_applicantid($select=rev_gender,rev_agerange,
rev_applicanttype)&$top=2` against DEV returns exactly the nested-object shape this file assumes,
gender values included. **Both of those prove the raw Dataverse Web API contract. They do NOT prove
the `List rows` connector's `OpenApiConnection` action accepts a literal `"$expand"` key in
`parameters` the same way it already accepts `"$select"`/`"$filter"`/`"$top"` in this exact
action** — Microsoft's own docs (`Use lists of rows in flows` → *Expand Query*) describe the
DESIGNER's simplified entry syntax (`primarycontactid(contactid,fullname)`, no `$select=`), not the
underlying JSON parameter name the connector's swagger declares, and no flow in this solution has
ever used `$expand` before. **`A-FLOW-06`** (Dev Summary Unvalidated Assumptions Register,
continuing A-FLOW-01..05): the literal `"$expand"` key, and whether its value needs the raw
`$select=` form (used here, matching this connector's other three parameters) or the designer's
bare form, is UNVERIFIED beyond E1 on the raw Web API and E2 on the designer's abstraction of a
DIFFERENT case (`Get a row by ID`, not `List rows`, and a different navigation property).
Cheapest verification: the same ladder A-FLOW-01 already uses — (1) import, (2) open in the
designer and save without a validation error (the fastest way to see whether `$expand` reached the
right underlying parameter, since the designer renders whatever the connector actually stored), (3)
a real invocation reconciling `genderDistribution` against an admin-side tally (this is also
A-R33's own V5 check, so it closes both in one pass).

**Tallying technique.** TAD §5.1 describes this as `length(filter(...))` "and equivalents" — that
literal phrase is WRONG against this project's own already-ground-truthed platform fact
(`IMP-0124`: the workflow definition language has no `select()`/`filter()` expression; Filter array
is a data-operation ACTION). Implemented as the ACTION instead: one `Query`-type (Filter array)
action per category value (46 total — 5 gender + 9 age range + 3 applicant type + 3×6 wellbeing +
11 life satisfaction — matching TAD A-R36's own "~40 array expressions" estimate), each filtering
`List_applications_in_round`'s output directly with a path-qualified `where` (e.g.
`equals(item()?['rev_applicantid']?['rev_gender'], 1)`), then one `Compose` per metric assembling
the `categories` JSON array from each filter's `length(body(...))`. All 46 filters run in parallel
(`runAfter: {}`) since Filter array does no connector I/O.

**Percentage — a real defect this session found and fixed before shipping, not a guess accepted on
faith.** The first draft guarded division-by-zero (an empty round) with
`if(equals(population,0),0,mul(div(...),100))`. Microsoft's own function reference states plainly
that `if()` "Parameters are evaluated from left to right" — i.e. **all three arguments are
evaluated before one is chosen**, so the `div(...)` branch still runs, and still throws, even when
the guard condition is true. Confirmed by writing a small evaluator for the exact expression
subset this file uses (`scratchpad/eval_wdl.py`, not shipped) and running it against a
zero-application round: the `if()`-guarded version threw `ZeroDivisionError`; the shipped version —
`mul(div(float(count),float(max(population,1))),100)` — does not, because it never divides by a
literal `0` and gives the same correct answer (`0`) whenever population is `0` (count is then
necessarily `0` too). The same evaluator was run against a 271-row synthetic round with three
deliberately-null genders: every category summed to population exactly, except gender, which
summed to population minus the three nulls — proving nulls are neither miscounted nor silently
folded into a real category.

**`wellbeingLastYear` scope.** Only `rev_wellbeinganswer8/9/10` — the three agreement-scale "last
year" questions — never the seven SWEMWBS frequency-scale questions (TAD §5.2, Amendment A-01's
evidence). `Compose_wellbeing_questions` assembles the three into the `questions` array §3.3
specifies; each question object carries its own `column` name and `population` (same value as
every other metric here — the round's application count — since nothing filters the population
before this point).

**`rev_setting` — deliberately not read.** The handoff for this dispatch names `rev_setting` (FR-062
thresholds) alongside the read list, inherited from TAD §5.1's own "Reads" row, but none of the
five metrics this pass adds is one of the three OQ-039 proportions those thresholds gate — they are
raw distributions, not proportions against an unset threshold. Reading `rev_setting` here would add
a live call for a value nothing in this version's scope consumes. Left for whichever dispatch
closes OQ-039 and the three proportions. **SUPERSEDED IN REVISION 5:** `rev_setting` *is* now read,
for `RoundStatisticsStaleAfterSeconds` — a different key, for a different reason (§3.3 property 7,
not FR-062). The OQ-039 thresholds are still not read and the paragraph above still holds for them.

---

# THIRD VERSION — Revision 5 / ADR-038 / `wbs:6.9`, authored 2026-08-28

## 1. TAD §12.3 step 1 — the live/source reconciliation. This is the only durable record of it

The live DEV solution was exported and unpacked on 2026-08-28 and the live definition of this flow
diffed against source **before a line of the new trigger was written**, because §12.3 step 1 is the
one step in the rollout whose order cannot change (A-R50): everything downstream overwrites the
live definition, so an unrecorded hand-edit is lost the moment it is overwritten. The complete
difference set, and what was done with each:

| # | Difference | Which side was ahead | Decision |
|---|---|---|---|
| 1 | **Trigger.** Live: `OpenApiConnectionWebhook` / `SubscribeWebhookTrigger` on `shared_commondataserviceforapps`, named `When_a_row_is_added,_modified_or_deleted` (the designer default), `message: 3`, `entityname: rev_roundstatisticsrequest`, `scope: 4`, `runas: 3`. Source: the V1 `type: "Request"` / `kind: "PowerApp"` trigger named `manual` | **LIVE** | Source now carries the row trigger. Renamed to `When_a_refresh_is_requested` — see §3 below |
| 2 | **The compute half, 54 actions.** Live is the FIRST version: no `Filter_*`, no `Compose_*_categories`, `genderDistribution`/`ageRangeDistribution`/`applicantTypeDistribution`/`wellbeingLastYear`/`lifeSatisfactionDistribution` all emitted as `null`, and `List_applications_in_round` selecting `rev_applicationid` only with **no `$expand`** | **SOURCE** | Source kept in full. **Deliberately NOT regressed to live.** The first import will restore all 54 actions |
| 3 | **The five `Response` actions were NOT hand-edited.** `Respond_ok`, `Respond_error`, `Respond_no_open_round`, `Respond_ambiguous_round`, `Respond_truncated` are **byte-identical** live and in source, all still `type: "Response"` / `kind: "PowerApp"` | Neither | See §2 — this contradicts the TAD and the contradiction is recorded, not smoothed over |
| 4 | `definition.description` is `null` live, populated in source — the designer stripped it | **SOURCE** | Source's kept and rewritten for Revision 5 |
| 5 | `properties.templateName: ""` present live, in no source flow in this solution | Live artefact | **Not adopted.** A designer artefact, not a decision |
| 6 | `metadata.operationMetadataId` GUIDs on live actions, on no source action | Live artefact | **Not adopted**, same reason |
| 7 | `.json.data.xml`: live `StateCode 1 / StatusCode 2` (Activated), source `0 / 1` (Draft). Also packer-casing variance — live `AsyncAutodelete` vs source `AsyncAutoDelete`, `ModernFlowType` present live, `BusinessProcessType` present in source | Neither | **Source's Draft kept** — every flow in this solution imports deactivated on purpose, and §12.3 step 6 recreates the registration from the designer anyway. Casing variance is cosmetic and source matches the other four flows: **nothing changed** |
| 8 | **A-R50's specific fear did not materialise.** Live `scope` is `4` (Organization), not silently `1` (User) | — | Recorded. There is exactly **one** hand-edit (the trigger) and exactly **one** loss (the top-level description). Nothing that session did is unaccounted for |
| 9 | Live `callbackregistration` for this flow: `entityname = rev_roundstatisticsrequest`, `message = Modified`, `scope = Organization`, `createdon = 2026-08-27 18:22` | — | Used as corroborating evidence in §3. **Not** used as evidence the trigger fires — `C-TECH-064` clause (a) makes a registration's existence and `createdon` inadmissible |

## 2. One place the APPROVED TAD is factually wrong about what happened, and it is corrected here

TAD §12.3's preamble states that *"the flow's trigger **and its final action** were changed by hand
in the Power Automate designer on 2026-08-27."* **The second half is wrong.** Item 3 above is the
measurement: all five `Response` actions are byte-identical between the live export and source. Only
the trigger was hand-edited.

This is recorded rather than quietly ignored because the sentence is load-bearing for the *order* of
§12.3 — it is the justification for capturing the live definition before authoring — and a future
reader who checks it and finds it false has no way to tell whether the reconciliation was done
against a wrong premise or the premise was wrong. It was the latter. The instruction §12.3 gives is
still correct and was still followed; only one of its two stated reasons existed.

## 3. `subscriptionRequest/message` is `3`, and the approved ADR's literal `2` would have shipped a dead feature

**TAD §5.1.1 and ADR-038 both specify `message: 2`, labelled *(Updated)*. `2` does not mean Updated.
It means Deleted.**

Read live out of REV-GrantApplications-DEV on 2026-08-28 via the `stringmap` table — the
`callbackregistration.message` option set, in full:

| value | label |
|---|---|
| 1 | Added |
| 2 | **Deleted** |
| 3 | **Modified** |
| 4 | Added or Modified |
| 5 | Added or Deleted |
| 6 | Modified or Deleted |
| 7 | Added or Modified or Deleted |

**Corroborated end-to-end in both directions on this exact tenant**, which is what raises it above a
table read: `REVScoringCalculateAndFlag`'s `subscriptionRequest/message: 1` produced a live
`callbackregistration` reading `Added`; **this** flow's live `subscriptionRequest/message: 3`
produced a live `callbackregistration` reading `Modified` (item 9 above). The connector parameter
passes straight through to `callbackregistration.message`.

**So `3` is authored, and the ADR's intent — not its literal — is what was implemented.** §5.1.1
says *"changing only `message` (1 → 2)"* and labels it *(Updated)*; §1.5 and ADR-038 both say the
trigger fires on the app's write; and §5.1.1 also instructs that the shape be copied from the one
**proven live**. `3` is the only value that satisfies all three. Building the literal `2` would have
registered a *delete* trigger on a row nothing ever deletes: a permanently dead feature reporting
*"still working"* to every trustee forever, with every source-side gate green — which is **A-R47**
exactly, the risk the TAD itself rates *High* impact.

**`4` (Added or Modified) was considered and rejected.** The row is seeded once by provisioning and
created never again, so the `Added` half can only ever fire on a re-provision; `3` is the narrower
value and the correct one. A wider trigger on a table this flow deliberately does not write is not
harmless — it is a bigger surface for a self-trigger loop that the split (§6.3.2) currently makes
structurally impossible.

**Raised as a TAD erratum and an improvement-log finding** at the dispatching agent's gate. The
authoring session does not edit the approved TAD.

**Where the marker lives.** JSON has no comments, so the measurement is recorded in the trigger's own
`description` — the only comment surface Power Automate attaches to a trigger's parameters, and the
mechanism this file already uses for every other in-source citation. 256 characters is the cap, so
the description carries the fact and the citation and this section carries the evidence.

## 4. `subscriptionRequest/filteringattributes` is deliberately absent

Not an omission. Three reasons, in the order that matters:

1. **The schema already solved the problem the filter would solve.** After §3.9.2 reduced the
   request table to the ask, the only mutable column left on the trigger table is the one the app
   writes. A `filteringattributes` narrowing to it would narrow a set that is already a single
   element.
2. **The flow writes a different table entirely** (§6.3.2), so there is no self-trigger loop for the
   filter to prevent. That is what the request/result split bought, and adding the filter would
   obscure it by implying the loop is being held off by a parameter rather than by the schema.
3. **It is an unverified connector parameter** — it appears in no flow in this solution, and §12.2
   carries it as a GUESS row marked *not required for this design*.

Recorded here so a later session does not add an unproven parameter to solve a problem the schema
already solved. If it is ever wanted, §12.2 says it is a verification row first.

## 5. `rev_status` — which integer, on which path, read from where

Read from `OptionSets/rev_roundstatisticsrequeststatus.xml:8-22` (the global option set the result
table reuses — ADR-038 deliberately introduces **no new** option set, so no new `IMP-0019`
relabelling risk):

| value | label | Written by |
|---|---|---|
| 1 | Pending | **Nothing in this flow.** The app infers "in flight" from the timestamps (§5.3.1); the flow never claims to be starting, only to have finished |
| 2 | Complete | `Write_ok_result` — and only that action |
| 3 | Error | `Write_no_open_round_result`, `Write_ambiguous_round_result`, `Write_truncated_result`, `Write_error_result` |

**Why the three business outcomes get `Error` and not `Complete`.** `no-open-round`,
`ambiguous-round` and `truncated` are not failures of the flow — the flow did exactly the right
thing. But §3.3 property 4 is the governing rule: *anything other than `ok` means the app renders
the diagnostic state and no figures at all.* `rev_status` is a coarse, audited mirror of that same
verdict, and mapping a no-figures outcome to `Complete` would make the one audited column disagree
with the document it accompanies. The precise reason is always in `rev_resultjson.status`, which
carries all five values; `rev_status` answers only *"are these figures safe to show."*
`rev_roundstatisticsresult.rev_status` documents `DefaultValue=2` as *Complete* — that is the
seeded row's resting state, "no computation in flight", written once by
`provisioning/dataverse/seed-round-statistics-result.ps1`, and is unrelated to this mapping. (The
column of the same name on `rev_roundstatisticsrequest` is ADR-038-superseded and written by
nothing — its seeder stopped setting it on 2026-08-28, `IMP-0438`.)

## 6. `staleAfterSeconds` — the one genuinely new field, and the trap in reading it

**`rev_setting.rev_value` is `ntext`** — confirmed at `Entities/rev_setting/Entity.xml:33`
(`<Type>ntext</Type>`, `MaxLength` 4000) before the expression was written, not assumed. So the
value arrives as a **string** and the contract wants a **JSON number or the literal `null`**.

Implemented as three small `Compose` actions rather than one expression, so each is separately
readable and separately inspectable:

| Action | Does |
|---|---|
| `Compose_stale_setting_raw` | Row-count guard. Exactly one row → the trimmed value; anything else (0 rows, and 2 is impossible while `rev_setting`'s alternate key holds) → the empty string |
| `Compose_stale_setting_nondigits` | Strips `0`–`9`. Empty result ⇒ the raw value is digits only |
| `Compose_stale_after_seconds` | Emits the digits as a bare JSON number, else the literal `null` |

**No numeric cast anywhere, and that is the whole design.** `int()` and `float()` **throw** on a
non-numeric string. A throw inside the scope fails the scope, which would mean **a mistyped tunable
takes the entire screen down** — every mount showing *"figures unavailable"* because someone typed
`120 seconds` into a setting row. §3.3 property 7 is explicit that this field is an optional
tunable whose absence is the fail-safe, so it must not be able to block the figures. Every function
used (`replace`, `empty`, `trim`, `startsWith`, `length`, `coalesce`, `string`, `if`, `and`, `or`,
`not`) is **total** — none can throw on any input.

**That also sidesteps a contradiction in this project's own records rather than betting on either
side of it.** `IMP-0124`'s lesson ends *"if() evaluates ONLY the branch it takes here, proven by
TD-07 failing and TD-08 passing"*, while this very file's Percentage note above cites Microsoft's
function reference for the opposite — *"parameters are evaluated from left to right"*, i.e. all
three arguments evaluate before one is chosen. **Both branches of every `if()` here are total, so
the shipped expression is correct under either semantics** and the contradiction does not need
resolving to ship. It is flagged as an improvement-log finding because two recorded lessons
disagreeing about a core language semantic will cost the next session real time.

**Leading zeros are rejected on purpose.** `007` is digits-only and is **not valid JSON** — a bare
`007` would make the whole document unparseable and the app's type guard would reject a document
that was otherwise perfect. So the test is *digits-only **and** (length 1 **or** does not start with
`0`)*, which admits `0` and `120` and refuses `007`.

**Verified by simulation, not by assertion.** The three expressions were re-implemented in Python
using only the documented semantics of the functions they call and run over 13 cases: row absent,
`120`, `' 120 '`, `0`, `''`, a null value, `abc`, `12.5`, `-5`, `007`, `1e3`, `120 seconds`, and two
rows. All 13 produced the intended output, and the resulting document parsed as JSON with
`staleAfterSeconds` typed `number` or `null` in every case. This proves the **logic**. It proves
nothing about whether the platform accepts the expressions — see §10.

**A documented simplification, recorded rather than adopted.** Microsoft's function reference lists
**`isInt`** and **`isFloat`** (*"return a boolean that indicates whether a string is an integer"*)
in the string-functions table of *Reference guide to functions in expressions for workflows in Azure
Logic Apps and Power Automate*, read 2026-08-28. `isInt(v)` would replace
`Compose_stale_setting_nondigits` and most of the guard with one total call. It was **not** adopted
in this pass on purpose: `isInt` appears in no flow in this solution, is a comparatively recent
addition to the language, and this flow's designer save is on the critical path at §12.3 step 6 — an
unrecognised function is exactly the class of thing that blocks a save. `replace`/`empty` have been
in the language since 2016 and are documented with a worked example in Microsoft's own Logic Apps
authoring guide. **Whoever next opens this flow in the designer can settle `isInt` in one minute**;
if it validates, collapsing the three actions to one is a strict improvement and this paragraph is
the reason it was left on the table.

**Why `null` and only `null` in the error document.** `staleAfterSeconds` is in **all five**
documents. Four carry the real value; `Compose_error_document` carries the literal `null`
unconditionally, because `Read_the_freshness_bound` lives **inside** `Compute_statistics` and a run
that reached the error path may never have executed it. Referencing
`outputs('Compose_stale_after_seconds')` from an action that may not have run would be a runtime
expression error **inside the failure handler — the one place that must not fail**, which is the
same reasoning that already keeps `roundKey` out of the error document. And `null` is the right
answer on its own terms: §3.3 property 7 defines it as *always recompute*, so a failed computation
is retried on the next mount instead of being cached for `S` seconds. Putting the settings read at
the top level instead would have bought a prettier error document at the cost of an **uncaught**
Dataverse read — a bad trade.

## 7. Ordering: `Capture_computedOn` stays first, and the result row is still the first *read*

The dispatch asked for the result-row read as the *"new first action, before `Capture_computedOn`"*.
It is not first; it is fourth, and the three actions ahead of it are two `Compose`s and one variable
declaration. The reason is that two instructions in the same specification pull opposite ways:

- §3.3 property 5 — `computedOn` is *"captured ONCE, **before any read**"*, and the dispatch
  requires that property to *"stay true"*.
- §5.1.1 point 4 — *"the result row is read **FIRST**, before the privileged read."*

Read literally, both cannot hold. But §5.1.1 point 4's stated purpose is *"diagnosed as 'not
provisioned' in one cheap call, instead of after tallying a whole round to no effect"* — it is about
ordering against the **privileged read**, not against a `Compose` of `utcNow()`. So:
`Capture_computedOn` → `Initialise_failure_detail` → `Compose_run_link` → `Read_the_result_row`.
Nothing between the stamp and the first read touches Dataverse, so **the stamp is still before every
read** and **the result row is still the first table read**, ahead of `List_the_open_round` and
`List_applications_in_round` by a whole scope. Both properties hold, and neither was traded.

`Compose_run_link` moved from the failure tail to the top for a plain reason: there are now **three**
alert paths, and all three need the deep link. It depends on nothing but `workflow()`.

## 8. Two new alert paths, because a missing row and an unreadable table are different faults

The flow holds **no Create privilege** on `rev_roundstatisticsresult` by design (§3.9.4), so it can
never repair either fault. Both therefore alert and terminate rather than continuing:

| Path | Fires when | Diagnosis it gives |
|---|---|---|
| `Alert_result_row_unreadable` → `Stop_run_result_row_unreadable` | `Read_the_result_row` is `Failed`/`TimedOut` | *"Could not read `rev_roundstatisticsresults`… check the table exists and REV Service Automation holds Read on it"* — i.e. A-R46 (table never created) or A-R49 (privilege) |
| `Alert_result_row_not_provisioned` → `Stop_run_result_row_not_provisioned` (in the `else` of `Check_exactly_one_result_row`) | the read succeeded and returned other than exactly one row | *"holds N row(s) with rev_name CURRENT, expected exactly 1. Seed the result row for this environment"* |

**Separated on purpose.** A hard read failure and a missing row have completely different remedies —
one is a privilege or a schema step, the other is `seed-…-result.ps1` — and collapsing them into one
message would send whoever is on call to the wrong place. A-R46 is rated *Medium/High* precisely
because *"the step reports success having created nothing"*, so the message names the count.

**`Skipped` is deliberately absent from both `Terminate` actions' `runAfter`.** On every healthy run
the alert above each one is skipped; accepting `Skipped` would terminate **every healthy run**. That
is the same defect as **D-10** (documented above: a `Response` accepting `Skipped` fired on every
successful run), applied pre-emptively to a new shape rather than after a test found it. The same
discipline is why `Compose_error_document` keeps `["Succeeded","Failed","TimedOut"]` and not
`Skipped` — D-10's fix, carried across the rewrite intact.

**`Check_exactly_one_result_row` puts the failure in `else` and leaves `actions` empty.** Reads
slightly backwards, and the reason is conservatism: the inverted form needs the `not` condition
operator, which appears in no flow in this solution. The empty-`then` form uses only `and` + `equals`
— already proven in three flows here. One less unverified shape on the critical path.

## 9. `A-FLOW-07` (NEW, OPEN) — the result table's entity set name and primary id attribute

**The guess.** This flow hand-authors two platform-assigned names for a table that does not exist
live yet: the entity **set** `rev_roundstatisticsresults` (in five `UpdateRecord` actions and one
`ListRecords`) and the primary id attribute `rev_roundstatisticsresultid` (in
`Read_the_result_row`'s `$select` and `Compose_result_row_id`'s expression).

**Marker in source:** `Compose_result_row_id`'s `description` names `A-FLOW-07` at the point of the
guess (`C-TECH-052`).

**Evidence today — E1 on the pattern, on this tenant, from a platform-generated file.**
`src/code-apps/trustee-review-portal/.power/schemas/dataverse/roundstatisticsrequests.Schema.json:10`
carries `"x-ms-dataverse-primary-id": "rev_roundstatisticsrequestid"` for the **sibling** table. That
file is generated by `pa app add data-source` against live DEV, so it is the platform echoing its own
name, not an author's convention — and it confirms `<logicalname>id` for a table created by this
project's own `ensure-schema.ps1`, on the same publisher prefix, one day earlier. The entity set
`rev_roundstatisticsrequests` is confirmed the same way.

**Why it is still a GUESS.** §12.2 carries the row and says plainly **"Do not hand-author it"** —
Dataverse pluralises the set name and assigns the primary id, and the author does not choose either.
E1 on a sibling is evidence about a *convention*, not about *this instance*. `C-TECH-051` forbids
fabricating a platform-assigned id, and this is adjacent to that: it is the smallest unavoidable
guess, because the flow cannot be authored at all without naming the table it writes.

**Cheapest closure, and it is already in the rollout.** §12.3 step 3 creates the table; the
prerequisite sweep then reads
`EntityDefinitions(LogicalName='rev_roundstatisticsresult')?$select=EntitySetName,PrimaryIdAttribute`
and §12.3 step 9's `pa app add data-source --table rev_roundstatisticsresult` echoes both names back.
**Both happen before step 5's import**, so this row closes by reading, not by running — and if
either name differs, six string literals in this file change and nothing else does.

## 10. What was executed in this pass, and what it does not prove (`C-TECH-053`)

**Executed, all local:** JSON parse; every `runAfter` resolved to a sibling at the same nesting
level; all 87 `description` fields within 256 (four were over on the first draft and were trimmed —
the cap bites on ordinary prose, every time); `verify-flow-definition-language.py` clean over all
five flows; `verify-flow-trigger-body-isolation.py` checks A1/A2/A3/B1 clean, and confirmed to
**fail** on this file's own pre-edit state, so it is not passing vacuously; `verify-field-length-limits.py`
clean; the `no-hardcoded-thresholds` grep clean; `pac solution pack` exit 0 for **both** Managed and
Unmanaged with `Processing Component: Workflows` and this flow present in both zips; `pac solution
check` on the packed managed zip — 0 findings at Critical/High/Medium/Low/Informational.

**This is V1/V2 and nothing more.** No import, no designer save, no observed run, no live write of
any kind happened in this pass. Specifically **not** proven:

- **That the trigger fires.** `message: 3` is E1 for the option-set *semantics* and for the
  parameter passing through to `callbackregistration.message`; it says nothing about whether *this*
  registration delivers events. That is A-R45/A-R47, it is an **observed effect** and nothing else
  counts: write the app's column, wait, assert `rev_computedon` on the **result** row changed.
  `statecode`, a `callbackregistration`'s existence or `createdon`, a matching `scope` or `runas`,
  and a **Resubmit** are all inadmissible (`C-TECH-064` clause (a)).
- **That the write-backs write.** The flattened `item/<column>` shape is E1 negative-proven on this
  project (`IMP-0116`) and a gate now enforces it structurally — but *for this instance*, the only
  proof is reading `rev_resultjson` back after the first observed effect and finding it non-empty.
  **A green run with an empty column is the signature of the nested form**, and it is the failure
  mode that would make this whole design silently do nothing with every gate green.
- **That the expressions evaluate.** `pac solution pack` and `pac solution import` accept a
  malformed expression silently; the designer save at §12.3 step 6 is the first thing that reads
  them. The `staleAfterSeconds` chain, `startsWith`, `not`/`and`/`or` as expression functions and
  the `$expand` parameter (`A-FLOW-06`) are all first exercised there.
- **That `Secure Outputs` does what §6.4.1 needs** — `A-FLOW-03`/A-R35, unchanged and still open.

**One incidental correction to a recorded fact.** `IMP-0010`/`IMP-0079` attribute
`pac solution check --outputDirectory` writing nothing to *"this repo's space-bearing path."* It was
run in this pass against a path containing **no spaces at all**, the CLI reported *"Downloading 1
files… Finished downloading 1 files"*, and the directory contained nothing but the stdout log teed
into it by hand. **The spaces are not the cause.** The operative rule is simply: read the solution
checker's result from **stdout**, always. Raised as an improvement-log finding.

---

# FOURTH VERSION — the D-11 fix / `wbs:6.9`, authored 2026-08-28

Closes three of the four keys test report v4 recorded as literal `null` (defect **D-11**, TAD
Erratum 5.3 §0.8, `contract/tad-deferrals.json` → `UR-001`/`UR-002`/`UR-003`): FR-058's
`applicationsPerDay`, FR-059's `exceptionalCircumstanceMix` and `exceptionalFundingSummary`, and
FR-060's `breakTypeProfile`. **Four MONEY-AVERAGE measures inside those documents stay `null`** and
that is a declared absence, not an oversight — §2 below. Nothing in the trigger, the write-back
shapes, the `staleAfterSeconds` chain or the D-02/D-10 failure path changed. Every action added sits
inside the existing `Compute_statistics` Scope, so `Find_the_failed_action` → `Alert_on_failure`
still reaches all of them unchanged.

**17 actions added, all inside `Condition_page_cap` → `else` → `actions`** — the branch taken when
the round fits in one page. The truncated branch still emits `status: truncated` and no figures, so
none of this can produce a partial screen (TAD §5.1 property 2).

| Added | Type | Serves |
|---|---|---|
| `Filter_exceptionalcircumstance_1` … `_4` | Query (Filter array) | FR-059 `exceptionalCircumstanceMix` |
| `Filter_exceptionalfunding_any` | Query | FR-059 `exceptionalFundingSummary` |
| `Filter_breaktype_1` … `_5` | Query | FR-060 `breakTypeProfile` |
| `Compose_round_opened_on` | Compose | FR-058, `A-FLOW-10` |
| `Compose_applications_per_day` | Compose | FR-058, `A-FLOW-09` |
| `Compose_exceptionalcircumstance_categories` | Compose | FR-059 |
| `Compose_exceptional_funding_summary` | Compose | FR-059, `A-FLOW-08` |
| `Compose_breaktype_rows` | Compose | FR-060, `A-FLOW-08` |
| `Compose_breaktype_total` | Compose | FR-060, `A-FLOW-08` |
| `Compose_breaktype_profile` | Compose | FR-060 |

## 1. `$select` widened by exactly three columns, and by nothing else

`/properties/definition/actions/Compute_statistics/actions/Switch_on_open_round_count/cases/Exactly_one_open_round/actions/List_applications_in_round/inputs/parameters/$select`

Added `rev_breaktype`, `rev_exceptionalcircumstance`, `rev_exceptionalfundingrequested`. All three
are `IsSecured=0` on `rev_application` (`Entities/rev_application/Entity.xml`), and all three are
read by an expression in this change — which is the whole test for whether a column belongs in a
privileged read.

**Four columns were deliberately NOT added, and each omission is load-bearing:**

- `rev_otherbreaktype` and `rev_otherexceptionalcircumstance` are **free text**, the second is
  `IsSecured=1`, and TAD §3.1 puts both out of scope. Free text inside an aggregate-only document is
  exactly what §6.3.3's live V5 assertion looks for. Nothing here needs them: FR-059 and FR-060 want
  a count per option value, and *Other* is option 4 and option 5 respectively — a count, not a
  transcription of what somebody typed.
- `rev_costs`, `rev_amountrequested`, `rev_additionalamountrequested` — the money columns — are not
  selected because **nothing in this dispatch computes over them** (§2). Selecting a column no
  expression reads widens the privileged read for no return.

`$expand`, `$filter`, `$top`, the retryPolicy and `runtimeConfiguration.secureData` are untouched.

## 2. `A-FLOW-08` (NEW, OPEN) — the four money-average measures, and why they are `null`

**Markers in source:** the `description` of `Compose_exceptional_funding_summary`,
`Compose_breaktype_rows` and `Compose_breaktype_total`. All three carry the same absence, so all
three name the marker.

**The four fields:** `exceptionalFundingSummary.averageAmountRequested`, and `breakTypeProfile`'s
`averageCost`, `averageAmountRequested` and `percentageOfCost` — on every one of the five rows and
on the total row.

**Why they cannot be built here, stated as a platform fact rather than a preference.** The workflow
definition language's math functions are exactly `add, div, max, min, mod, mul, pow, rand, range,
sub`. **There is no `sum()` over an array**, and `add()` takes exactly two operands. So a sum over a
**fixed, small** number of operands is expressible by nesting `add()` — which is precisely why
`Compose_breaktype_total`'s `count` IS real, five operands nested four deep — while a sum over a
**variable-length** collection is not expressible at all. An average over the round's rows needs the
second kind.

**Four mechanisms exist and none of them is a dev decision.** `Apply to each` + a variable;
`xpath(xml(...),'sum(...)')`; OData `$apply`; FetchXML `aggregate`. Two of those are already
recorded as unavailable through this connector (TAD §5.1's negative result on aggregate FetchXML,
ADR-030), one changes the flow's shape from declarative to iterative, and one is a serialisation
trick this project has never ground-truthed. **Choosing between them is an architecture decision and
it is routed to `architect-agent`.** Emitting `0` instead would be worse than emitting nothing: TAD
§3.3 point 3 — *"an unavailable metric is `null`, never `0`"* — and a fabricated `0` average cost on
a board pack is a figure, not a gap.

**What makes this safe on the app side, and it is not luck.** `parseBreakTypeTotal`
(`src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts`) returns the total only if
at least one of its four fields is non-`null`. `count` is real, so the total row survives; the three
money fields render as absences. `parseExceptionalFundingSummary` requires a numeric `anyCount` and
tolerates a `null` `averageAmountRequested`, so the real percentage still reaches the screen.
`parseBreakTypeRow` requires `value` and `count` and tolerates all three money fields being `null`.
**No app-side file was changed in this dispatch, and none needed to be.**

## 3. `A-FLOW-09` (NEW, OPEN) — the `days` denominator is a reading of FR-058, not a stated rule

**Marker in source:** `Compose_applications_per_day`'s `description`.

FR-058 asks for *"the average applications received per day"* and says nothing about how a day is
counted. Three readings were available and they differ by up to a whole day on a young round:

| Reading | On a round opened today | Chosen? |
|---|---|---|
| Whole elapsed days, floor 1 (**shipped**) | `days = 1`, so the figure equals the count | ✅ |
| Whole elapsed days, no floor | `days = 0` → **divide by zero → the whole computation fails** | ❌ |
| Fractional elapsed days | `days = 0.14` → 7× the real arrival rate on the opening morning | ❌ |

Shipped as `max(div(sub(ticks(computedOn), ticks(openedOn)), 864000000000), 1)`. Both `ticks()`
operands are int64, so `div` is **integer** division and the result is whole elapsed days; the
`max(..., 1)` makes the round's opening day count as day 1 and is what stops the denominator ever
being `0`. `864000000000` is ticks-per-day, a unit conversion, not a threshold — it is not a
`rev_setting` candidate.

**`rev_roundopenedon` is entered, never derived** (TAD §3.5, and the column's own description in
`Entities/rev_roundfinance/Entity.xml`). There is deliberately **no** `MIN(rev_submittedon)`
fallback: a round with a quiet first week would report a later open date and an inflated per-day
figure. An absent open date means the metric is absent, and it emits `null`.

## 4. The `if()` guard is total on BOTH branches, and the dispatch instruction said otherwise

**This is the one place this pass did not build what it was asked to build, and the reason is a
contradiction already recorded in this repository.** The instruction for this dispatch stated that
`if()` *"evaluates only the branch it takes in this runtime, proven on this project by TD-07/TD-08
(IMP-0124), so the guard is real"*, and asked for
`if(empty(coalesce(outputs('Compose_round_opened_on'),'')), 'null', concat(...))`.

That premise is contested **inside this very file**. The SECOND VERSION section above records the
opposite conclusion — Microsoft's own function reference stating parameters are evaluated left to
right, and this project's percentage guard rewritten to `max(population,1)` because of it. It is
`IMP-0378` (`platform-fact-groundtruthed`, **APPLIED**): *"Never rely on `if()` to guard a division,
an array index, or any other operation that throws on the untaken branch's own inputs — both
branches are evaluated regardless of the condition."* And `IMP-0412`
(`two-recorded-lessons-contradict-each-other`) records that the two lessons conflict, that **the
question is open**, and that the standing instruction is to write guarded arithmetic **correct under
either semantics**.

**What would have shipped on the instruction as written.** With an absent `rev_roundopenedon`,
`ticks(null)` and `formatDateTime(null, 'yyyy-MM-dd')` both throw. Under eager evaluation the
`Compose` fails, the Scope fails, `Alert_on_failure` fires, and the result row gets an error
document — so a round whose open date has simply not been typed in yet takes **every figure on the
trustee landing screen** down with it. That is a strictly worse failure than the `null` the field
was supposed to emit.

**What shipped instead.** The date is coalesced to `computedOn` before it reaches either function:

```
ticks(coalesce(outputs('Compose_round_opened_on'), outputs('Capture_computedOn')))
```

With an absent date the difference is `0`, `max(0,1)` is `1`, `formatDateTime` gets a valid
timestamp, and **neither branch can throw**. The `if()` still returns the literal `'null'`, so the
emitted document is identical to what the instruction asked for. This is the same technique
`Compose_stale_setting_nondigits` already uses two sections above — its own description says
*"replace/empty are total, so neither branch of the if() below can throw whichever
argument-evaluation order the platform uses"* — so the convention was already established in this
file; this pass just applied it to the new guard as well.

**Both semantics were executed, not reasoned about.** The evaluator described in §6 was run twice
over the shipped expressions, once with `if()` lazy and once with all three arguments evaluated. The
four simulated documents are byte-identical between the two runs. Neither run is platform evidence —
settling `IMP-0412` still needs one deliberate live run — but the construction no longer depends on
the answer.

## 5. `A-FLOW-10` (NEW, OPEN) — `ticks()` / `formatDateTime()` over a `DateOnly` Dataverse value

**Marker in source:** `Compose_round_opened_on`'s `description`.

`rev_roundopenedon` is declared `<Type>datetime</Type>` with `<Format>date</Format>` and
`<DateTimeBehavior>DateOnly</DateTimeBehavior>`. Over the Web API a DateOnly column returns
`"2026-08-01"` — **no time part, no offset**. Both `ticks()` and `formatDateTime()` are documented
against "a timestamp", and `2026-08-01` is a valid ISO-8601 date, so this should parse. But
**`ticks(` appears in no flow in this solution** — grepped, zero hits across all five definitions
before this change — so the connector-to-runtime shape is E1 at best: a reading of the function
reference, not an artefact the platform produced.

Cheapest verification is the ladder `A-FLOW-01` already uses, and step 2 is nearly free: (1) import,
(2) open in the designer and save without a validation error, (3) one real run against a round with
a known open date, reconciling `applicationsPerDay.days` against a hand count of calendar days. Step
3 is the same live run that closes `A-FLOW-06` and `A-R33`, so it costs no extra pass.

If it turns out `ticks()` rejects a date with no time part, the fix is one function:
`ticks(concat(outputs('Compose_round_opened_on'),'T00:00:00Z'))` — but **do not pre-emptively add
that**, because it is a second guess stacked on the first, and `concat` on an already-full timestamp
would then be the broken case.

## 6. What was executed in this pass, and what it does not prove (`C-TECH-053`)

**Executed, all local, no live call of any kind:**

- JSON parses; every new `runAfter` resolves to a sibling at the same nesting level; all
  descriptions within 256 (`verify-field-length-limits.py` clean).
- `verify-flow-definition-language.py` clean over all five flows — no `select(`/`filter(`, no
  alternate-key Row ID, no nested `item` on an UpdateRecord, no nested `InitializeVariable`.
- `verify-flow-trigger-body-isolation.py` checks A1/A2/A3/**B1** clean. **B1 is the one that
  matters here**: it derives the row-bearing action set from source and rejects any reference
  reaching `item/rev_resultjson` whose innermost enclosing function is not `length` or `empty`.
  Every new count is `length(body('Filter_…'))`; `Compose_round_opened_on` uses `first(...)` on
  `List_the_open_round`, which is not row-bearing because `rev_roundfinance` declares no
  `IsSecured=1` attribute and the action carries no `secureData` — the same reason
  `Compose_round_key` has always been allowed to do it.
- **The response document was simulated and parsed.** A small evaluator for the WDL subset this
  file uses (scratchpad only, not shipped) executed every `Query` and `Compose` in the `else` branch
  in `runAfter` order over a synthetic 434-row round, and `json.loads()` succeeded on the resulting
  document. Four scenarios × two `if()` semantics = eight documents, all valid JSON, all with §3.3's
  exact metric key order: open date present · open date absent (`applicationsPerDay` = `null`) ·
  round opened today (`days` = 1, no divide-by-zero) · zero rows in the round (every count 0, every
  percentage 0, no divide-by-zero). `sum(rows.count)` equalled `total.count` in every case.
- `src/tests/solutions/RoundStatisticsContract.Tests.ps1` — 34 assertions, green, and
  **falsified by mutation** rather than trusted: reverting `applicationsPerDay` to a literal `null`
  failed 2; adding `rev_otherexceptionalcircumstance` + `rev_otherbreaktype` to `$select` failed 2;
  adding a **sixth option to `OptionSets/rev_breaktype.xml` alone**, leaving the flow untouched,
  failed 6 — which is the proof that the option values are derived from source and not transcribed.
  Both mutated files were restored and verified byte-identical by `sha256`.

**This is V1 and nothing more.** No pack, no import, no designer save, no observed run. Specifically
**not** proven, beyond what the THIRD VERSION section already lists:

- **That any new expression evaluates.** `ticks()`, `formatDateTime()` over a DateOnly value
  (`A-FLOW-10`), and the nested `add()` chain are all first exercised by the designer save at TAD
  §12.3 step 6. The local evaluator is a model of the runtime, written by the same pass that wrote
  the expressions — it can only catch the errors that pass thought to look for, and it caught two
  real ones (an over-escaped `\"` in six Compose inputs, and the `ticks(null)` throw in §4).
- **That the figures are right.** Every count here is `length()` over a `Filter array` whose `where`
  compares an option-set integer. A round-level reconciliation against an admin-side tally is V5 and
  is the same run that closes `A-FLOW-06`.
- **That `days` reads as a trustee expects.** `A-FLOW-09` is a reading of a requirement, and the
  only thing that closes it is the reviewer looking at the number on the screen next to the round's
  open date.

---

# FIFTH VERSION — the four money averages, and the `k = 5` disclosure gate / `wbs:6.9`, authored 2026-08-28

Builds what the FOURTH VERSION's §2 declared unbuildable, on the mechanism TAD Revision 6 decided
(**ADR-039**, APPROVED) and the threshold the reviewer set at the same gate (**OQ-043 → `k = 5`**,
TAD §0.9.1). **A-FLOW-08 is RESOLVED and its markers are removed from this file.** Two new open
assumptions replace it: **A-FLOW-11** (`xml()`/`xpath()` have never run on this tenant) and
**A-FLOW-12** (a reading of FR-060's *"including exceptional funding"*).

**88 actions added**, taking the definition from 105 to **193**. 84 sit inside
`Condition_page_cap` → `else` → `actions` beside the existing metric actions; 4 are the `k` chain
at `Compute_statistics` level, beside the freshness chain, because the `Switch` has to be able to
wait on them. Nothing in the trigger, the write-back shapes, the `staleAfterSeconds` chain or the
D-02/D-10 failure path changed.

| Added | Count | Type | Serves |
|---|---|---|---|
| `Filter_breaktype<n>_cost_present` / `_requested_present` / `_both_present` | 15 | Query | FR-060 |
| `Select_breaktype<n>_cost_values` / `_requested_values` / `_both_cost_values` / `_both_requested_values` | 20 | Select | FR-060 |
| `Compose_breaktype<n>_cost_sum` / `_requested_sum` / `_both_cost_sum` / `_both_requested_sum` | 20 | Compose | FR-060, `A-FLOW-11` |
| `Compose_breaktype<n>_average_cost` / `_average_requested` / `_percentage_of_cost` | 15 | Compose | FR-060 |
| `Compose_breaktype_total_{cost,requested}_{population,sum}`, `_both_population`, `_both_{cost,requested}_sum` | 7 | Compose | FR-060 total row |
| `Compose_breaktype_total_average_{cost,requested}`, `_percentage_of_cost` | 3 | Compose | FR-060 total row |
| `Filter_exceptionalfunding_amount_present`, `Select_…_amount_values`, `Compose_…_amount_sum`, `Compose_exceptionalfunding_average_amount` | 4 | Query/Select/Compose | FR-059, `A-FLOW-11` |
| `Read_the_money_measure_minimum`, `Compose_money_minimum_{raw,nondigits,population}` | 4 | OpenApiConnection/Compose | the `k` gate |

**ADR-039's cost estimate was ~40 added actions and the measured figure is 88.** The estimate
counted ~3 net new actions per sum for thirteen sums. What it did not count: a presence `Filter`
per measure (which is the arithmetic, not an optimisation — §5.1.2 property 2), a second `Select`
and a second sum for each `percentageOfCost` ratio, the `k` read chain, and the total row's
population/sum helpers. The decision is unaffected — 88 is still a factor of ~11 below candidate
1's ~950, nothing iterates, and the flow stays far inside the documented 500-action limit — but
the figure is recorded because an estimate restated as a result is how this project's baseline
rule got written.

## 1. `$select` widened by exactly three columns — and the FOURTH VERSION's own rule is why

`/properties/definition/actions/Compute_statistics/actions/Switch_on_open_round_count/cases/Exactly_one_open_round/actions/List_applications_in_round/inputs/parameters/$select`

Added `rev_costs`, `rev_amountrequested`, `rev_additionalamountrequested`. The FOURTH VERSION's §1
declared these three deliberately absent *"because nothing in this dispatch computes over them —
selecting a column no expression reads widens the privileged read for no return."* **That premise
changed; the rule did not.** All three are now read by an expression here, which is the whole test
for whether a column belongs in a privileged read, and `RoundStatisticsContract.Tests.ps1` now
asserts the rule in both directions: every one of the three is selected, and **every** selected
column is matched against an `item()?['<column>']` read in the definition, so a future `$select`
widening with no reader reddens.

Still deliberately NOT added, unchanged: `rev_otherbreaktype` and
`rev_otherexceptionalcircumstance` (free text, the second `IsSecured=1`).

## 2. A correction to ADR-039's literal shape — the empty subset is `NaN`, not `0`

**This is the one place this pass did not build what the approved document literally writes, and
the reason was measured rather than reasoned.** §5.1.2's shape is:

```
Compose_<m>_sum  xpath(xml(concat('<r><v>', join(body('Select_<m>_values'), '</v><v>'), '</v></r>')), 'sum(/r/v)')
```

Run against **libxml2**, a conformant XPath 1.0 engine, on the exact shapes this construction
produces:

| XML | `sum(/r/v)` |
|---|---|
| `<r><v>10.5</v><v>20.25</v></r>` | `30.75` |
| `<r></r>` | `0` |
| `<r><v></v></r>` | **`NaN`** |
| `<r><v>10</v><v></v></r>` | **`NaN`** |

`join()` over an **empty** array yields `''`, so the literal shape builds `<r><v></v></r>` — row
three — whenever a presence subset is empty. §0.9 already records that `NaN` is not valid JSON;
what it does not say is that the `NaN` **escapes**, because the total row sums the five per-type
sums with a nested `add()`, so one break type with no costed application makes
`rev_resultjson` unparseable and takes **all thirteen metrics** off the screen. TAD §12.2
deliberately seeds a round with exactly that break type.

**What shipped instead** — the XML carries no `<v>` at all when the subset is empty, so the
node set is empty rather than containing an empty element, and `sum()` is `0`, which the average
guard withholds:

```
@xpath(xml(concat('<r>', if(empty(body('Select_<m>_values')), '',
                            concat('<v>', join(body('Select_<m>_values'), '</v><v>'), '</v>')),
                  '</r>')), 'sum(/r/v)')
```

Both branches of that `if()` are plain string concatenation, so neither can throw whichever
argument-evaluation order the platform uses (`IMP-0378` / `IMP-0412`). **The guard is enforced,
not just written down**, in two independent places: `RoundStatisticsContract.Tests.ps1` asserts
the template byte-for-byte, and `scripts/verify-flow-trigger-body-isolation.py`'s check B1 treats
only this exact template as a scalar reduction — the unguarded form fails it, with an on-disk
known-bad fixture (`src/tests/fixtures/known-bad/flow-reads-no-trigger-body/UnguardedXPathSum.json`)
and a `BuildGates.Tests.ps1` block holding that line.

## 3. `A-FLOW-11` (NEW, OPEN) — `xml()` and `xpath()` have never run on this tenant

**Markers in source:** the `description` of all 21 `Compose_*_sum` actions.

The pattern is first-party documented (function reference, Example 7) and the engine is named as
the .NET XPath library, hence XPath 1.0, whose `sum()` semantics are a standard and were measured
above. What is unverified is the **Logic Apps wrapper**: no flow in this solution has ever called
`xml()` or `xpath()`, and a conformant local engine is a model of the runtime, not the runtime.

Three residuals inside that, stated separately because they fail differently:

1. **`xpath()` returning a value `float()`/`div()` accept.** If it returns a node set or an
   unparseable string the `Compose` throws, `Compute_statistics` fails, `rev_errorlog` is written
   and `REV | Ops | Failure Alert` fires. **Fail-loud, and no wrong number is possible.**
2. **A money value serialised in EXPONENT notation.** XPath 1.0's number conversion does not
   accept `1.5E+03`, so one such value would make the whole sum `NaN`. .NET only formats a double
   that way at magnitudes far outside any grant amount, so this is bounded rather than eliminated
   — recorded, not machinery-guarded. It fails as an unparseable document, i.e. a `pending`
   screen, never as a wrong figure.
3. **A money column arriving as a non-numeric string.** Same `NaN` outcome as (2), same detection.

`§12.2`'s verification is what closes all three, and its own wording is the reason it works: *"A
populated average alone proves nothing — it is the shape a naive unguarded expression also
produces on data that happens to be complete."*

## 4. `A-FLOW-12` (NEW, OPEN) — FR-060's *"including exceptional funding"* is a reading

**Markers in source:** the `description` of the five `Filter_breaktype<n>_requested_present`
actions.

SDD FR-060 asks for *"the average grant amount requested (including exceptional funding)"*, and
TAD §3.1 maps `rev_additionalamountrequested` to **FR-060** as well as FR-059. So the per-row
value summed here is `rev_amountrequested` **+** `rev_additionalamountrequested`, presence being
either column populated:

```
Select ... @string(add(float(coalesce(item()?['rev_amountrequested'], 0)),
                       float(coalesce(item()?['rev_additionalamountrequested'], 0))))
```

That is the identical arithmetic the app's own already-approved `totalFundingRequested`
(`src/code-apps/trustee-review-portal/src/domain/format.ts`) performs for FR-035 — *"summed
UNCONDITIONALLY … one populated and the other absent sums as if the absent one were zero"* —
which is why the two screens cannot disagree about what a grant ask is.

**The competing reading**, and why it is not obviously wrong: ADR-039's cost paragraph says *"five
break-type rows × two money columns"*, which reads as `rev_costs` and `rev_amountrequested` alone.
That is a costing phrase rather than a contract, the count of thirteen sums holds either way, and
§3.1's column mapping is the more specific statement — but a reviewer sentence settles it, and if
the answer is the base ask alone the fix is one expression per break type and nothing else.

Note the `coalesce`-to-zero here is **not** the coercion §5.1.2 property 2 forbids: presence is
decided by the `Filter` before this runs, and a row with one of the two columns populated has a
known total. A row with **neither** never reaches the `Select`.

## 5. The `k` gate — one setting, one comparison, and the fail-safe direction

`Read_the_money_measure_minimum` reads `rev_setting` where
`rev_name eq 'RoundStatisticsMoneyMeasureMinimumPopulation'`, on the same shape as the freshness
chain two sections up. Then:

```
Compose_money_minimum_population
  @int(concat('0', if(and(not(empty(outputs('Compose_money_minimum_raw'))),
                          empty(outputs('Compose_money_minimum_nondigits'))),
                      outputs('Compose_money_minimum_raw'), '999999999')))
```

**`int()` is applied once, to digits only, so it cannot throw** — which is why the sentinel is a
digit string rather than a negative number and why the `if()` sits *inside* the `concat` rather
than around the `int()`. An absent, empty or non-numeric setting therefore yields `999999999`, a
threshold no round can reach under the 1000-row page cap, and **every money measure is withheld**.
That is the direction TAD §12.1 calls fail-safe-but-not-approved, which is why the value is seeded
in all three environment settings files rather than left to the default.

Each of the thirteen measures then compares its **own** population:

```
@if(or(empty(body('Filter_<m>_present')), less(length(body('Filter_<m>_present')), <k>)), 'null',
    concat('{"value":', string(div(float(outputs('Compose_<m>_sum')),
                                  float(max(length(body('Filter_<m>_present')), 1)))),
           ',"population":', string(length(body('Filter_<m>_present'))), '}'))
```

Three properties worth naming:

- **`max(…, 1)` is load-bearing, not defensive.** Deleting it raises a divide-by-zero on a break
  type with no costed application — reproduced by mutation this pass — because both `if()` branches
  may be evaluated.
- **The `empty()` clause is redundant for every `k ≥ 1` and is kept anyway.** It is §5.1.2 property
  3's own requirement, and it is the only control at `k = 0`: without it, XPath's plausible `0`
  over an empty node set would be published as an average cost of zero. A mutation deleting it
  stayed green until a `k = 0` scenario was added to the simulation — which is why that scenario
  exists.
- **`k` binds these thirteen measures and nothing else.** Every categorical distribution stays
  unsuppressed on the reviewer's 2026-08-25 decision (TAD §0.9.1 point 3), and reading `k` as a
  revival of NFR-027 would silently suppress six charts. The contract test asserts both
  directions: no categorical compose references the `k` action, and exactly thirteen composes do.

## 6. What was executed in this pass, and what it does not prove (`C-TECH-053`)

**Executed, all local, no live call of any kind:**

- JSON parses; every `outputs()`/`body()`/`result()` reference resolves to a real action; every
  `runAfter` key is a sibling at the same nesting level; all 193 descriptions ≤ 256
  (`verify-field-length-limits.py` clean).
- `verify-flow-definition-language.py` clean over all five flows. The `Select` **action** is not
  the non-existent `select(` **expression** its check 1 rejects, and a `"select":` JSON key does
  not match its regex — confirmed by running it, not by reading it.
- `verify-flow-trigger-body-isolation.py` clean — **after the gate was extended, because it
  rejected the approved design.** See §7.
- **The response document was simulated and parsed**, by a scratchpad evaluator over the shipped
  expression text, with `xpath`/`sum` handed to libxml2 and **both `if()` branches always
  evaluated** so an untaken-branch throw is a failure. 31 assertions across six scenarios:
  `k = 5` · `k` unseeded · `k` mistyped (`'five'`) · `k = 1` · `k = 0` · an empty round. The
  `k = 5` round carries, simultaneously, a break type with 8 costed rows (reconciled against a
  hand-computed mean), one with **every** `rev_costs` blank, one with a **mix** (population 5 <
  count 9), one **below** `k` (count 3 published, three money measures `null` — §3.3's worked
  example exactly), and one with **no applications at all**.
- **Falsified by mutation, four times, each reverted:** removing the empty guard from the XML →
  the total row's `averageCost` came back **`NaN`**; deleting one `max(…,1)` → **divide-by-zero**;
  using the row count as a denominator instead of the presence subset → the mean moved from 900 to
  500 and the population from 5 to 9, which is §3.3 property 8's *"the one thing that will
  silently be false"* caught mechanically; deleting the `empty()` clause → caught only by the
  `k = 0` scenario.
- `src/tests/solutions/RoundStatisticsContract.Tests.ps1` — **47 assertions, green**, up from 34,
  with the A-FLOW-08 Describe replaced rather than deleted, exactly as its own comment instructed.

**This is V1 and nothing more.** No pack, no import, no designer save, no observed run.
Specifically **not** proven: that any new expression evaluates (`xml`, `xpath`, `join`, `int`,
`trim`, `startsWith` over these inputs are all first exercised by the designer save at TAD §12.3
step 6); that the figures are right against a real round; and that the k threshold is actually
seeded in the target environment, which is a `post_deploy` step and not a source fact.

## 7. A HARD build gate rejected the approved design, and was extended rather than bypassed

`scripts/verify-flow-trigger-body-isolation.py` check **B1** — *the result document is composed
from an enumerated field list, never from a serialised row object* — **failed on this flow the
first time it was run against the new actions.** Reproduced, not predicted. The reason is
structural: the sum traverses the round's rows, so `Select_<m>_values` is row-bearing, and taint
propagated through every downstream `Compose` to `item/rev_resultjson`.

The gate now recognises **one** additional reduction, and the argument is a single sentence: **an
XPath `sum()` returns an XPath number, and a number cannot carry a row** — which holds whatever
the feeding `Select` projects, because a `Select` projecting whole rows would make `sum(/r/v)`
return `NaN`, never a row.

`xpath`, `join` and `xml` were deliberately **not** added to the reducing-function allow-list.
That would have exempted `join(body('List_applications_in_round'), ',')`, which serialises rows.
Instead one **anchored template** matches a `Compose`'s entire input expression, with the same
`Select` named in both `body()` positions and the XPath expression pinned to the literal
`sum(/r/v)`. Five selftest cases hold the boundary: a node-returning `'/r/v'`, two different
source actions, the unguarded form, and the template plus one extra reference in the same
expression are all still rejected. Selftest went from 15 cases to 20, and the build config's
coverage comment was corrected with them.
