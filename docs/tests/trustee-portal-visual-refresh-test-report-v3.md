# Test Report (v3) — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** `trustee-portal-visual-refresh`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260826-2/`
**Cycle:** third pass — re-test after the FAIL on D-10 in [test-report-v2.md](trustee-portal-visual-refresh-test-report-v2.md#L12)
**Dev Summary:** [trustee-portal-visual-refresh-dev-summary.md](../development/trustee-portal-visual-refresh-dev-summary.md)
**TAD:** [trustee-portal-visual-refresh-architecture.md](../architecture/trustee-portal-visual-refresh-architecture.md)
**SDD:** [revitalise-grant-automation-plan.md](../plans/revitalise-grant-automation-plan.md) — Amendments A-02/A-03 (FR-057–FR-063)
**WBS:** `6.1`, `6.3`, `6.9` — see D-16, this build's manifest no longer states them
**Date:** 2026-08-26 · **Tier:** strategic (special-category data central to the scope under test)

**Status:** **PARTIAL**

---

## 1. Test Summary

**D-10 is genuinely fixed, and I verified it by reasoning through the run graph myself rather than
by reading the fix description.** No P1 or P2 defect is open. The run is **PARTIAL** and not PASS
because nothing in this feature has reached V5 and the flow is still absent from every environment —
the same structural position as the previous two cycles, now with the blocking defect removed.

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Regression (Code App) | `npx vitest run --coverage` | 372 | 0 | 0 |
| Unit / Regression (PowerShell) | `pwsh src/tests/Invoke-Tests.ps1` | 876 | 0 | 1 |
| Integration | not executed — flow absent from DEV, app has no generated flow service | — | — | — |
| End-to-End | not executed — same reason | — | — | — |
| Security | 8 gates re-run with the build's own invocations | 8 | 0 | 0 |
| Accessibility | chart table-first rule, unchanged this revision | carried | 0 | 0 |
| Performance | no NFR threshold measurable without a live flow | — | — | — |
| Provisioning | live query against DEV, with positive control | 4 | 0 | 0 |
| Platform Contract | run-graph traced by hand, both branches, all 5 flows audited | 1 | 0 | 0 |
| Compliance / Constraint | 6 domain HARD, 26 tech HARD, 1 tech SOFT | 32 | 0 | 1 warn |
| **Total** | | **1298** | **0** | **1** |

**The change under test is one token, and I confirmed that is all it is.** The unmanaged solution
zip in this artifact differs from the previously-tested build
(`revitalise-grant-automation-20260826-1`) in exactly one file, and that file differs in exactly two
places: `"Skipped"` removed from one `runAfter` list, and one `description` string extended to record
the fix. The Code App half of the artifact is **byte-identical** between the two builds. So the
previous cycle's verification of the schema, the UI and the `rev_roundfinance` data-source
registration still describes these exact bytes, and re-running it would have produced no new
information.

**D-10 is fixed in the shipped bytes, not only in source.** I extracted the flow definition from
both packaged zips — managed and unmanaged — and confirmed each carries
`Alert_on_failure: ["Succeeded","Failed","TimedOut"]`. Checking source alone would not have proven
what deploys.

---

## 2. Requirement Coverage

Unchanged from the previous cycle except where the flow's behaviour is the subject. No requirement
moved to `PASS` end-to-end, because no metric can travel from Dataverse to the screen yet (§7.2).

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-035 | Detail view: redacted narrative, score breakdown, break type + "other" specifier, preferred dates, location, funding, applicant-type and care context | TC-035a…f | **PARTIAL (carried)** — three columns still unwired, D-12 |
| FR-039 | Print/offline export reusing FR-035's field list | TC-039 | **PARTIAL (carried)** |
| FR-057 | Landing screen shell, full viewport width | TC-057 | **PASS (V2, carried)** — byte-identical Code App |
| FR-058 | Total applications received, date round opened, average per day | TC-058a/b | **PARTIAL (carried)** — `applicationsReceived` authored; `applicationsPerDay` still an explicit `null` |
| FR-059–FR-062 | Distributions: break type, gender, age range, applicant type, ethnic group, wellbeing, life satisfaction, three headline proportions | TC-059…062 | **PARTIAL (carried)** — UI renders any distribution; the flow emits `null` for every one |
| FR-063 | Round financial position + charity capacity figures | TC-063 | **PARTIAL (carried)** — 13 columns live and audited; no row exists in DEV |
| NFR-024 | Accessibility (WCAG 2.1 AA per ADR-020) | TC-N24a…d | **PASS for what exists (carried)** |
| NFR-026 | Full-viewport-width, brand-consistent rendering | TC-N26a/b | **PARTIAL (carried)** — brand half explicitly unmet by design (A-R26) |
| NFR-001, NFR-003 | No secured column released; no identifying attribute in a trustee view | TC-SEC-01…04 | **PASS** — re-verified this cycle, §5 |
| NFR-013 | Data minimisation | TC-SEC-05 | **PASS** — re-verified against the changed flow, §5 |
| **TAD §5.1** | **The flow responds exactly once per outcome, and responds on failure** | **TC-SEC-06b** | **PASS — D-10 closed, §3** |

---

## 3. D-10: how I verified it, and what the fix rests on

**Conclusion: the success path now reaches exactly one `Response` action, and the failure path still
reaches `Respond_error`.** I derived both by walking the `runAfter` graph from the trigger, not by
re-reading the fix note.

The corrected condition is at
[flow line 304](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L304)
and now reads `Alert_on_failure: ["Succeeded","Failed","TimedOut"]`.

**Success branch — traced action by action.** `Compute_statistics`
([line 66](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L66))
succeeds, so:

| Action | Its `runAfter` requires | Actual predecessor status | Result |
|---|---|---|---|
| `Find_the_failed_action` | `Compute_statistics` Failed/TimedOut | Succeeded | **Skipped** |
| `Describe_the_failure` | `Find_the_failed_action` Succeeded | Skipped | **Skipped** |
| `Compose_run_link` | `Describe_the_failure` Succeeded | Skipped | **Skipped** |
| `Alert_on_failure` | both above Succeeded | Skipped | **Skipped** |
| `Respond_error` | `Alert_on_failure` Succeeded/Failed/TimedOut | **Skipped — not in the list** | **Skipped** |

The chain terminates. One `Response` fires — whichever of the four business-outcome actions inside
the `Switch` the run reached. This holds identically for all four of those outcomes, because each
leaves the scope `Succeeded`.

**Failure branch — traced the same way.** `Compute_statistics` Failed →
`Find_the_failed_action` runs (its condition matches) → `Describe_the_failure` runs →
`Compose_run_link` runs → `Alert_on_failure` runs → `Respond_error` accepts **all three** of that
action's possible terminal statuses, so the caller receives a `status:"error"` body whether the
alert itself succeeded, failed or timed out. The failure path is not weakened by the fix.

**The platform semantics the fix depends on are V5-verified inside this solution, not merely
documented.** This matters, because the previous cycle could only rate the defect on documented
`Skipped`-status behaviour. `REVScoringCalculateAndFlag` carries a structurally identical error
chain — `Find_the_failed_action` at
[line 796](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json#L796)
hanging off a `["Failed","TimedOut"]` condition — and that flow is verified live in DEV across 12 of
12 successful runs with no spurious failure alert. Skip-propagation through exactly this shape is
therefore proven behaviour in this environment. What remains unproven is only `Respond_error`
itself, which has no precedent here (A-FLOW-05 claim (a), §7.1).

**Repository-wide, the D-10 class is now clean.** I audited every `Response` action in all five
flows for a `runAfter` accepting `Skipped`:

| Flow | `Response` actions | Any accepting `Skipped`? | Correct? |
|---|---|---|---|
| `REVOpsFailureAlert` | 1 | yes — `Respond_to_calling_flow` | yes, nothing else responds |
| `REVIntakeWordPressToDataverse` | 5 | no | yes — [line 1382](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1382) is the precedent |
| `REVPortalRoundStatistics` | **5** | **no** | **yes — fixed** |
| `REVScoringCalculateAndFlag` | 0 | — | — |
| `REVScoringDailySummary` | 0 | — | — |

The only remaining `Skipped`-accepting `Response` in the solution is the one where it is safe.

**One correction to the record.** Both the previous report and
[Dev Summary line 106](../development/trustee-portal-visual-refresh-dev-summary.md#L106) call this a
"four-`Response` flow". It has **five** — the four business outcomes plus `Respond_error`. The
diagnosis and the fix are unaffected; the count is wrong in two documents and is now D-17.

### Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| TC-PC-04 | Platform Contract | The failure alert names the action that actually failed | `failureDetail` names the leaf action | Names the containing `Switch` for 8 of the 10 actions that can fail, D-15 | **P3** |
| TC-REG-01 | Regression | A regression test guards the D-02/D-10 fix | A test asserts the failure path's shape | Still no test in `src/tests/` references any part of this flow's failure path, D-11 | **P3** |
| TC-CHAIN-01 | Platform Contract | The artifact manifest states the WBS tasks it discharges | `wbs` field present, as in the previous build | Field absent from this build's manifest, D-16 | **P3** |
| TC-PC-03 | Platform Contract | Dev Summary §9's suite figures match a measured run | Figures match | [§9 line 470](../development/trustee-portal-visual-refresh-dev-summary.md#L470) states 874/1/1; measured **876/0/1**, D-14 | **P4** |

No P1 and no P2. None of the four is a FAIL driver under
[my fail conditions](../../agents/test-agent.md#L99).

---

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-15** | **P3** | **New. The failure alert cannot name the action that failed.** `Find_the_failed_action` filters `@result('Compute_statistics')` for the child whose status is Failed — correct as far as it goes — but `Compute_statistics` has only two immediate children ([line 75](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L75) and [line 99](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L99)), and the second is a `Switch` hiding 8 descendants. A failure in any of those 8 — including `List_applications_in_round` ([line 130](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L130)), the up-to-1000-row read that is by far the likeliest thing to fail at runtime — makes the `Switch` the Failed child, whose message is the wrapper "An action failed. No dependent actions succeeded." Same root shape as D-10: a pattern copied from `REVScoringDailySummary`, whose own `Summarise` scope ([line 104](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVScoringDailySummary-8F1C2A44-1003-4B7A-9E21-0A1B2C3D4E03.json#L104)) has six children and **no containers**, so the pattern reaches the leaf there and cannot here | TC-PC-04 |
| **D-16** | **P3** | **New, and a regression against the previous build.** The previous build's manifest carried `"wbs": ["6.1","6.3","6.9"]` on line 3; this build's manifest has no `wbs` field at all. Nothing in [the build config](../../config/revitalise-grant-automation-build.yml) requires one, so an unenforced convention regressed silently. It matters because the artifact is what deploys and what work is booked against, and `scripts/verify-wbs-chain.py`'s artefact→task direction has nothing to read | TC-CHAIN-01 |
| **D-17** | **P4** | **New.** Two documents describe this as a four-`Response` flow; it has five. [Dev Summary line 106](../development/trustee-portal-visual-refresh-dev-summary.md#L106) and the previous report's §4 table both carry it. No behavioural consequence — recorded because the count is the exact precondition that made D-10 unsafe, so a wrong count is the wrong safety check | §3 |

**Carried forward, unchanged:**

- **D-05 (P3), third consecutive cycle unaddressed.** `rev_roundfinance.rev_name` reaches an OData `$filter` ([line 146](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L146)) and a hand-built JSON document ([line 195](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L195)) unescaped. Admin-only input on a table the service identity already reads in full, so blast radius stays narrow — but it is the one privileged read path this feature adds and it now needs an explicit decision to fix or accept, not a fourth carry-forward.
- **D-11 (P3).** No regression test guards this flow's failure path. [The test-plan skill](../../skills/how-to-write-a-test-plan.md#L80) requires one for every P1 or P2 fixed; D-02 and now D-10 have none. This is why D-10 shipped through a green suite, a clean packer and a clean Solution Checker, and why D-15 has done the same.
- **D-12 (P3).** `rev_otherbreaktype`, `rev_additionalamountrequested` and `rev_exceptionalfundingrequested` still appear only in the platform-generated `Rev_applicationsModel.ts` — confirmed by grep this cycle — so FR-035's structured half is still unwired.
- **D-13 (P3).** `6.9` is still absent from [contract/wbs.json](../../contract/wbs.json) (verified programmatically: phase 6 holds `6.1`–`6.8`). [Dev Summary line 9](../development/trustee-portal-visual-refresh-dev-summary.md#L9) still names `6.5`, whose contracted deliverable is "Shared app + access test", and no access test has been performed in any of the three cycles. `pm-agent`/`commercial-agent`, not a retest item.
- **D-14 (P4), third consecutive cycle.** Dev Summary §9 states 874/1/1 and explains the one failure as the learning-loop gate failing at 17 unread findings. That explanation is now stale too: the gate is green and the measured figure is 876/0/1.

**Closed this cycle:** **D-10**, verified above.

---

## 5. Constraint & Compliance Verification

Scope filter applied: rows whose `Scope` column names `test-agent`. Rows verified live in earlier
cycles that this build does not touch are carried on the byte-identity evidence in §1 and marked so,
rather than restated as fresh live results.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | PASS, with a stated limit | `domain-invariants` exit 0. `Secure Outputs` set on the one row-reading action ([line 157](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L157)) and correctly absent from every `Response`. **Evidence level V1** — no gate can observe `secureData` taking effect; that is A-FLOW-03, still OPEN |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CUD on sensitive entities audit-logged | PASS (carried) | Live-verified cycle 1; packaged schema byte-identical |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit records carry timestamp, actor, action, entity id, before/after | PASS (platform-provided) | Dataverse's own audit store; no custom audit writer added |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences an automated outcome | **PASS** | `domain-invariants` exit 0; FR-016 grep gate exit 0. Re-confirmed against the changed flow: it emits counts only and feeds no eligibility or scoring outcome |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured=1` | **PASS** | Gate green; 4 documented exceptions each printed with reason and owner. The three `…redacted` columns are correctly not register entries — they are redactions whose sources stay secured |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled=1` | **PASS** | 20/20. Two non-register attributes with auditing off are reported, not failed |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated and sanitised | PASS (with residual) | The flow declares no input parameters at all — the trigger's schema is an empty property set ([line 35](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L35)) — so there is no caller-steerable surface. Residual is D-05's internal concatenation |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit-test coverage meets the threshold | PASS, both numbers stated | Code App **372/372 at 96.27%** statement/line — re-measured by me. PowerShell **876/0/1**; the 81.81% line-coverage figure is build-agent's measurement, **which I did not independently re-measure** |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Assumption register + `A-nnn` markers in source | PASS | `verify-assumption-markers.py` PASS — 14 OPEN rows, every one carrying its marker; 33 total, 12 closed, 0 orphans |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level actually executed | **PASS** | §7.2. Every Dev Summary §11 claim re-checked; none overclaims. The A-FLOW-05 claim-(b) closure is correctly described as static inspection rather than a ladder level |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI runner's OS | **Not verified** | Source review only. No new script this revision, and CI has still never executed on this project |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Warnings triaged | PASS | 83 warnings, 0 untriaged per the manifest, each with a recorded rationale |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate proven able to fail | PASS | `verify-build-config.py` all checks OK; 4 exemptions named, not silent. `verify-flow-definition-language.py --selftest` — 13 checks, gate can fail |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No shipped text exceeds its governing limit | PASS | `field-length-limits` exit 0 — 183 flow descriptions within 256 chars. Notably this gate caught the fix's own first draft at 436 chars, per Dev Summary §0.3 |
| [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) | Learning-loop triggers current | **PASS — was RED last cycle** | `verify-improvement-log.py --check` exit 0; 3 unread against a batch trigger of 10. This was the one PowerShell test failure in the previous cycle and is now green |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state source cannot express, verified LIVE | PASS (carried) + live this cycle | Cycle 1's 14 live queries stand on byte-identity. This cycle I re-ran the flow-presence query live, with positive control — §6 |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD schema/access tables are a checked specification | **PASS** | `verify-tad-coverage.py` OK — 148 column specs across 11 table blocks, 9 owned and dated deferrals, 0 violations |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Readers survive a second instance; identity is (table, column) | PASS | `verify-source-reader-plurality.py` OK, 37 readers |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | `IsSecured` protects a stored value, never a projection | PASS | `verify-field-security-coverage.py` OK, with the two standing platform warnings. This feature correctly used `Decimal`, not `Money`, for all seven measures |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | A declared property is only delivered if the builder emits it | PASS | Gate green; 1 accepted latent gap with a named owner |
| — | No secured column reaches the Code App | **PASS** | `verify-code-app-column-bindings.py` OK — 68 authored files reference none of 62 forbidden columns across 7 tables; all 3 fail-closed visibility columns present |
| — | No trustee in a column security profile | **PASS** | `verify-column-security-membership.py` OK — no team holding a trustee-facing role is a member of any profile |
| — | Code App data sources resolve | **PASS** | `verify-code-app-data-sources.py` OK — **5 registrations / 5 declared**. The fix from three passes ago still holds, on a byte-identical Code App |
| — | Shipped prose names only columns that exist | PASS | `verify-shipped-content.py` OK — 6 entities with UI, all reachable |
| — | Requirement ids unique (promoted HARD this week) | PASS | `verify-requirement-id-uniqueness.py` exit 0 |

**The special-category question, answered directly.** The flow names **no** special-category column
anywhere — I applied the FR-016 column list to the new flow definition as well as to the scoring
flow it is written against, and it is clean. Its two reads select
`rev_name,rev_roundopenedon,rev_roundclosedon` from the round table and **only**
`rev_applicationid` from `rev_applications`. Every demographic and wellbeing aggregate FR-059–FR-062
names is still an explicit `null` in the response, so no special-category data traverses this path
in this version at all. That is the honest position, and it means the aggregation and redaction risk
this feature's escalation exists for is **deferred, not discharged** — it arrives with the version
that populates those metrics.

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6                 |  violations: NONE
                                          |  unevaluable: NONE
Domain   SOFT: 0 in scope                 |  warnings:   NONE
Tech     HARD: 26 / 26 of 26              |  violations: NONE
                                          |  unevaluable: NONE
Tech     SOFT: 1 in scope                 |  warnings:   C-TECH-067
  C-TECH-067: source-derived-test-counts reports 10 fragile absolute-count literals in the
              test tree (SOFT, --warn-only, reviewer-pre-accepted per the build handoff)
Overall: WARN
```

**One check I could not run, stated rather than skipped.** `verify-wbs-chain.py` refused to report,
correctly, because `logs/state/wbs-state.json` is older than two files under `src/solutions/`. I did
not rebuild it — that cache is `pm-agent`'s generated artefact and regenerating it mid-test would
have made this report the thing that changed the state it audits. So the contract chain is
**unverified this cycle**, in both directions, and D-16 sits inside exactly that gap.

---

## 6. Provisioning Verification

| Item | Expected | Verified Via | Result |
|---|---|---|---|
| `REV \| Portal \| Round Statistics` in DEV | Present if deployed | Live `pac env fetch` on `workflow` as `svc_grantapplications` against `REV-GrantApplications-DEV` | **ABSENT** — 0 matches |
| Positive control for that query | The other four `REV` flows visible | Same query | **PASS** — Failure Alert, Daily Summary, Calculate & Flag, Intake all returned |
| `rev_roundfinance` as a Code App data source | Present in the generated config | `verify-code-app-data-sources.py` — 5/5 | **PASS (carried, byte-identical)** |
| Schema half (table, 13 attributes, key, redacted columns, roles, auditing) | As cycle 1 | Byte-identity of the packaged solution | **PASS (carried)** |

**The absence is a measured fact, not an inability to look.** Live Dataverse reads worked from this
session, and the positive control proves the query would have found the flow had it been there.

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Each row's closing precondition is answered fresh, separately from its status.

| ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|---|
| A-FLOW-01 | Hand-authored `kind: "PowerApp"` trigger and `Response` shapes will save in the designer | OPEN | Import, then a human opens and saves it | Environment yes, flow no | **OPEN** |
| A-FLOW-02 | `prvReadWorkflow` at Global is sufficient and not excessive | OPEN | Grant it and nothing else, invoke as a real trustee | Grant is live; flow is not | **OPEN** |
| A-FLOW-03 | `Secure Outputs` hides row data from run history | OPEN | One real run, then read its history as owner | No run has occurred | **OPEN** |
| A-FLOW-04 | `rev_SharedDataverse` binds to a Power-Apps-triggered flow | OPEN | Same designer-save step as A-FLOW-01 | No import | **OPEN** |
| A-FLOW-05 (a) | `Respond_error` executes and returns a body on a genuine failure | OPEN | Force a failure, confirm a `status:"error"` body | No import | **OPEN** |
| A-FLOW-05 (b) | `Respond_error` does **not** execute on a successful run | **Closed statically this revision** | Inspection of the corrected `runAfter` | — | **Closure CONFIRMED — §3.** The row now states both directions, which is the correction my previous cycle asked for, and the negative half is genuinely settled by inspection |
| ~~A-LAND-1~~ | Stand-in matches the generated `rev_roundfinance` service | CLOSED | — | — | **Closure holds** — gate 5/5 on a byte-identical app |
| A-LAND-2 | The generated flow service is a static no-argument `Run()` | OPEN | `pa app add flow`, then swap the default | **Still never run** — `fetchRoundStatistics` still defaults to a stand-in that rejects | **OPEN, and it is why nothing is end-to-end** |
| A-LAND-3 | FR-062's three proportions are `{population, count, percentage}` | OPEN | The flow emits one populated | Flow emits `null` | **OPEN** |
| A-LAND-4 | FR-060's total row mirrors a data row minus the category | OPEN | The flow emits a real `breakTypeProfile` | Flow emits `null` | **OPEN** |

**A-FLOW-05's correction is the right fix, and I checked it rather than accepting it.** The row now
carries two claims and closes only the one that inspection can close, leaving (a) open with its live
verification step named. Closing this row from a failure-only live test would no longer certify the
bug — which was the defect in the original wording.

**Orphan check (C-TECH-052):** no orphans; the marker gate resolves all 14 OPEN rows to real files
containing their own ids.

**Eight rows remain OPEN and every one is closable only by deploying.** My fail conditions treat an
OPEN assumption as a FAIL where an environment exists in which it could be closed. DEV exists, but
the flow must be imported first, and import is `pipeline-agent`'s stage — after this gate. So these
are reported OPEN and are not independent FAIL drivers, consistently with both previous cycles. They
are [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) blockers on the deploy
itself, which needs the reviewer's explicit `OVERRIDE`.

### 7.2 Verification levels achieved

| Component | Level claimed (§11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `rev_roundfinance` + 13 attributes + alternate key | V4 | **V4 — carried** | Live-verified cycle 1; packaged bytes identical | PASS |
| 3 redacted columns on `rev_application` | V4 | **V4 — carried** | As above | PASS |
| Role privilege grants (3 roles) | V4 | **V4 — carried** | As above | PASS |
| Table auditing on `rev_roundfinance` | V4 | **V4 — carried** | As above | PASS |
| `REV \| Portal \| Round Statistics` flow | V2 | **V2 — confirmed, and confirmed still not V3** | Both zips carry it; Solution Checker 0/0/0/0/0; **absent from DEV** by live query with positive control | PASS on the claim |
| **The flow's success/failure branching** | **V2 + one property by inspection** | **Confirmed as described** | §3. The success-path property is settled by the `runAfter` graph, and skip-propagation through this exact shape is V5-proven in `REVScoringCalculateAndFlag`. `Respond_error` firing remains untested | **PASS — D-10 closed** |
| **The failure alert's diagnostic content** | not separately claimed | **V1 — and defective at V1** | §4 D-15. No gate can see it; only a deliberate failure would | **FAIL — D-15 (P3)** |
| `LandingPage.tsx` + the three components | V2 | **V2 — confirmed** | 372/372 across 21 files at 96.27%, re-run by me | PASS |
| `rev_roundfinance` Code App data source | V3 (binding), not V4 | **V3 — confirmed as claimed** | Gate 5/5; no real signed-in read | PASS on the claim |
| ADR-026 brand theme | V2 | **V2 — carried** | Byte-identical app | PASS on the claim |

- **Idempotency (V3 re-run):** not applicable this cycle — no deploy has occurred.
- **V4 designer open + save: NOT PERFORMED.** The flow has never been imported anywhere. This single step would close A-FLOW-01, A-FLOW-03, A-FLOW-04 and half of A-FLOW-05.
- **Cross-OS (C-TECH-054):** source review only; CI has still never run on this project.
- **Diagnostic components (C-TECH-056):** none created; `rev_roundfinance` holds 0 rows.

**The level this feature has actually reached, stated plainly:**

> **The schema half is V4 in DEV. The flow is V2 — packaged, Solution-Checker-clean, never imported —
> and its success-path defect is now fixed and verified by inspection against live-proven platform
> behaviour. The Code App is V2, byte-identical to the previously-tested build, except the
> `rev_roundfinance` data-source binding, which is V3. Nothing in this feature has reached V5. No
> FR-058–FR-063 figure can travel from Dataverse to the screen today, because the flow is not
> deployed and `pa app add flow` has still never been run.**

---

## 8. Recommendations

**1. This artifact is fit to deploy to DEV, and deploying is now the only way to learn anything more.**
Every remaining question about this feature — five assumption rows, the V4 designer save, whether
`Respond_error` returns a body — is answerable only by an import. The blocking defect is gone.

**2. Fix D-15 in the same visit as the import, not after it.** One extra `Query` action over
`@result('Switch_on_open_round_count')`, taken when the Failed child is itself a container, would
recover the leaf. It is worth doing before the first real failure rather than after, because the
alert is the only diagnostic the trustee-facing path produces.

**3. D-11 is now the finding I would act on above the others.** Three cycles, two defects in this
one flow's failure path, both invisible to a green suite. A source-level test asserting reachability
of `Response` actions per outcome would have caught D-10 in milliseconds and would catch D-15's
class too.

**4. D-05 needs a decision, not a fourth carry-forward.** Fix the escaping or record an accepted
exception with an owner and a date in [known-exceptions.json](../../contract/known-exceptions.json).

**5. Three items are not retest items.** D-12 is a scope question; D-13 and D-16 belong to
`pm-agent`/`commercial-agent` under the rule that work enters by WBS task id; D-14 and D-17 are
documentation accuracy in the Dev Summary.

---

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0349 | `platform-contract-guessed-not-groundtruthed` | rework | Filtering `result(scope)` for the Failed child only reaches the leaf when the scope's immediate children are leaves — copy that pattern into a scope containing a Switch, If or Foreach and the alert names the container with the platform's useless wrapper message |
| IMP-0350 | `no-assertion-on-shipped-content` | rework | A build manifest field that no gate requires can disappear between two consecutive builds of the same feature with every gate green — the artifact lost the WBS ids it is deployed and booked against |
| IMP-0351 | `hand-maintained-count-drifts-from-source` | friction | The `Response`-action count was the precondition that made D-10 unsafe, and two documents state it wrong — when a count is a safety precondition, derive it rather than transcribing it |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
