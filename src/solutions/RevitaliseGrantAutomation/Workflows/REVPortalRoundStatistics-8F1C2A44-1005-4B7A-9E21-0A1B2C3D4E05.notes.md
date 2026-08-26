# REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every
action, trigger, parameter and schema property — exceeding it blocks the flow from being saved
in the designer at all (same limit `REVOpsFailureAlert-...notes.md` documents). The condensed
descriptions actually shipped in this file keep the essential fact; the full reasoning that
would otherwise live there is preserved here, keyed by the same JSON path.

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
