# Test Report — Revitalise Grant Automation, ADR-083 retention delete jobs (wbs:0.7)

**Feature Slug:** revitalise-grant-automation
**Artifact:** none. Source-level change, not packed. Scope: the two new `jobKey` branches in [ensure-bulk-delete-jobs.ps1](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L300), the settings entries in [test-settings.json](../../provisioning/deploymentSettings/test-settings.json#L331) and [prd-settings.json](../../provisioning/deploymentSettings/prd-settings.json#L379), their Pester tests, and the pipeline step descriptions. Unrelated uncommitted changes in the same files (the `REV_TrusteeFinancialEligibility` profile, `dev-settings.json` group ids, `EnsureSchema.Tests.ps1`) belong to other sessions and are not judged here.
**Date:** 2026-10-22  **Tester:** test-agent, strategic tier (model override recorded in [routing.log](../../logs/routing.log), 13:11 correction line)  **WBS:** 0.7
**Items:** WI-0142
**Status:** FAIL. No defect was found in the source or the tests. The run fails on one rule only: two OPEN register rows, `A-RET-1` and `A-NS-47`, could be closed in DEV, which exists, and are not (test-agent Fail Conditions; C-TECH-058). A third, `A-NS-45`, was half-measured in DEV by this agent and one of its premises is false as written.

Highest level reached: **V1** (Pester over a faked Dataverse), plus read-only DEV queries that confirm names, the option value, and that DEV accepts both query shapes as a read. No job exists in any environment and none was created.

## Summary

The source does what ADR-083 says. Both new query branches, both settings entries and the schedule order match TAD §3.4.1. 589 targeted tests and the full provisioning suite (791) pass, and 7 of 8 deliberate mutations of the new code were caught. What is not proven is whether the platform accepts and executes the two jobs. One design premise about who can read AI Event rows is false in DEV and goes to you.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped | Evidence |
|---|---|---|---|---|---|
| Unit: the three suites named in the Dev Summary, re-run by test-agent | 590 | 589 | 0 | 1 | `DeploymentSettings` 51, `DataverseScripts` 89, `ScriptContract` 450. Matches Dev Summary §11's count. The skip is pre-existing |
| Regression: whole `src/tests/provisioning` suite | 792 | 791 | 0 | 1 | Same skip |
| Mutation check on the two new branches (test-agent) | 8 | 7 caught | 1 survived | 0 | See §3. Script restored byte-identical afterwards (sha1 `26d7da80…` before and after) |
| Integration, read-only against DEV (test-agent, `pac env fetch` as `svc_grantapplications`) | 8 queries | 8 answered | 0 | 0 | §6 |
| End-to-end | not run | | | | No job exists. DEV gets neither job by design (reviewer D-1); TST/ACC and PRD were out of bounds for this dispatch |
| Security | 2 | 1 | 1 finding | 0 | Secrets: none added (static read). `A-NS-45` premise (c): false as written in DEV (§7.1, decision 1) |
| Accessibility, Performance | N/A | | | | No screen. Job runtime is the platform's |
| Cross-OS (C-TECH-054) | not run | | | | macOS only. The new code is plain hashtables, with no OS-specific call |

## 2. Requirement Coverage

| Requirement | Test case(s) | Result |
|---|---|---|
| [FR-048](../../docs/plans/revitalise-grant-automation-plan.md#L2178) / [NFR-010](../../docs/plans/revitalise-grant-automation-plan.md#L2344): paid-grant applications deleted 6 years after final payment | [DataverseScripts L899](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L899) asserts entity, status 11, inner join to `rev_grant` on `rev_applicationid`, `OlderThanXMonths` 72 in `LinkCriteria`. [DeploymentSettings L572](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L572) asserts 72 months, monthly, 01:40 in both environments | **PASS at V1** |
| TAD §3.4.1: paid-grant job before the orphan sweep | Same test (01:40 vs 02:40) | **PASS at V1**. Same recurrence, created on the same day, so the order holds by start time. Not executed |
| ADR-083 item 2: `msdyn_aievent` older than 30 days, daily, PRD only | [DataverseScripts L928](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L928); [DeploymentSettings L557](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L557) (absent from TST/ACC, present once in PRD) and [L608](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L608) (30 days, daily, 03:30) | **PASS at V1** |
| ADR-083 item 1: the cascade removes Review, Grant and Payment | Solution source read by test-agent: [application→grant Cascade](../../src/solutions/RevitaliseGrantAutomation/Other/Relationships/rev_application.xml#L26), grant→payment Cascade ([rev_grant.xml L20](../../src/solutions/RevitaliseGrantAutomation/Other/Relationships/rev_grant.xml#L20)), application→review Cascade. Provider→grant is Restrict, which blocks only deleting a provider | **PASS at E1 (source)**. Not executed |
| DEV gets no job | `dev-settings.json` has no `bulkDeleteJobs` entry for either key | **PASS** |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| MUT-7 | Unit (mutation) | Changed `msdyn_aieventid` to `msdyn_aievent_id` in the `aiEvents` column set | At least one test fails | 0 failures | P4. The one name in this branch measured in DEV (E1, `A-NS-47`) is pinned by no test |

The other seven mutations were each caught: status 11→4, months→days, inner→left-outer join, `rev_grant`→`rev_payment`, the AI entity name, and `createdon`→`modifiedon`.

## 4. Defects Raised

| Defect ID | Severity | Description | Linked test |
|---|---|---|---|
| D-ADR083-1 | P4 | No test asserts the `aiEvents` selected column `msdyn_aieventid` ([script L373](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L373)) | MUT-7 |

No P1, P2 or P3 defect.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-003](../../constraints/domain/domain-constraints.md#L36) | Retention defined and automated deletion implemented (not test-agent-scoped; checked because it is the point of the change) | PASS at source, not live | The 6-year job was absent from every settings file before this change. It is now in both. No environment holds it |
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS | The script's report lines name jobs, not rows (unchanged code path) |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47), C-DOM-011 | Deletes on sensitive tables audited | No change | No table or audit setting changed. Whether bulk deletes appear in the audit log is not measured |
| C-DOM-030, C-DOM-031, C-DOM-032 | Special-category columns | No change | No column added or changed by this revision |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No secrets | PASS | Static read of the diff |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent provisioning | PASS at V1 | The existing name-keyed `EXISTS` path is unchanged and covers both new jobs ([L798](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L798)) |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guess has a register row | PASS, one note | `A-RET-1`, `A-NS-45` to `A-NS-47` cover the hand-authored shapes. Note: the paid-grant clock column `rev_finalpaymentdate` is secured ([Entity.xml L314](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_grant/Entity.xml#L314)). The job then depends on its owner being able to read that column. The TAD says only a System Administrator creates these jobs ([TAD L2759](../../docs/architecture/revitalise-grant-automation-architecture.md#L2759)), which covers it, but no register row states it. Recommendation 3 |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | §7.2 |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Runs on the CI runner OS | NOT VERIFIED | macOS only. CI runs `ubuntu-latest` |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN rows block where closable | **FAIL** | §7.1: `A-RET-1` and `A-NS-47` can be closed in DEV with synthetic rows and a one-off delete. No `OVERRIDE` is recorded |
| C-TECH-065 | Identity probe before a script is trusted | No change | No new step. The PRD run is the reviewer's, as administrator |
| C-TECH-067 (SOFT) | Counts not hand-typed | WARN | [DeploymentSettings L565–L568](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L565) assert literal 5 and 6. The comments explain them but do not say *count-coupled by design* |
| C-TECH-079 | Work items move on evidence | PASS | WI-0142 is not moved by this report |
| Remaining test-agent-scoped tech rows (004, 006, 014, 040, 045, 046, 048, 051, 056, 057, 059, 060, 064, 066, 068 to 071, 073, 078) | Apps, roles, schema, gates, rendering | N/A | No input handling, route, code app, role, schema, gate, metadata write or screen in this change |
| Fail-safe configuration defaults (IMP-0511) | | N/A | The TAD declares no fail-safe default for these jobs |

## 6. Provisioning Verification

Read-only, DEV (`REV-GrantApplications-DEV`), 2026-10-22, as `svc_grantapplications@revitalise.org.uk`. Nothing written.

| Item | Expected | Verified via | Result |
|---|---|---|---|
| Option 11 of `rev_application.rev_status` | Grant Paid | `stringmap` fetch: `Grant Paid`, 11, Application | **PASS (E1)**; matches [source L58](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_applicationstatus.xml#L58) |
| Paid-grant query shape, run as a read | Accepted; names resolve | The exact FetchXML equivalent (status 11, inner link `rev_grant` on `rev_applicationid`, `olderthan-x-months` 72 on `rev_finalpaymentdate`) | **Accepted**, 0 rows. This proves the names and the relationship. It does not prove the `BulkDelete` QueryExpression body, or that the job selects the right rows |
| `aiEvents` query shape, run as a read | Accepted | Count of `msdyn_aievent` with `createdon` older than 30 days | **Accepted**, 0 rows (DEV rows date from 2026-10-20/21) |
| Paid grants in DEV | | Grants with a final payment date | One grant (`86049ed0…`), status Paid, final payment 2026-10-20, **application status Under Review, not Grant Paid**. The paid-grant job would never select it. Decision 2 |
| Jobs in any environment | None | Not queried. The Dev Summary and the dispatch both state none was created | Not measured |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| [A-RET-1](../../docs/development/revitalise-grant-automation-dev-summary.md#L13307) | The paid-grant query is accepted by `BulkDelete` and selects exactly the right applications | OPEN | Synthetic rows (Grant Paid at 73 months, 71 months and no date; Approved at 73 months) plus the query, then a one-off delete. Register says TST/ACC; DEV has the same schema | **Yes: DEV** | Names, option value and relationship confirmed E1; shape accepted as a read. Selection and `BulkDelete` acceptance not run (they need writes, which this dispatch did not have) | **OPEN, closable in DEV** |
| [A-NS-45](../../docs/development/revitalise-grant-automation-dev-summary.md#L13308) | No person can read an `msdyn_aievent` row | OPEN | DEV reads for (b) and (c); TST/ACC reads for (c) and (d) after a scrub-flow run there | DEV: yes. TST/ACC: needs a run there | **(b) TRUE, E1:** Basic User `prvReadmsdyn_AIEvent` depth 1 (own rows). **(c) FALSE as written, E1:** the 11 latest rows are owned and created by `svc_grantapplications`, access mode Read-Write (a sign-in account), which holds System Administrator in DEV. Also seen: `AIB Roles`, `Service Reader` and `Service Writer` read at organisation depth; in DEV only non-interactive Microsoft service users hold them | **OPEN; (c) to reviewer** per the TAD's own rule ([TAD L7187](../../docs/architecture/revitalise-grant-automation-architecture.md#L7187)) |
| A-NS-46 | Deleting AI events does not change credit reporting | OPEN | PRD after the first run | Not yet | No | OPEN, PRD only by design |
| [A-NS-47](../../docs/development/revitalise-grant-automation-dev-summary.md#L13310) | `BulkDelete` accepts and runs the `msdyn_aievent` job | OPEN (key name E1) | Register says PRD first run. A one-off delete over DEV's own AI Event rows would close it earlier | **Yes: DEV** | Key name and shape accepted as a read | **OPEN, closable in DEV** |

Orphans: none. One unstated dependency, the secured clock column (§5, C-TECH-052).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `paidGrantApplications` branch + settings | V1 | V1 | 589/0/1 re-run; mutations caught | PASS |
| `aiEvents` branch + settings | V1 | V1 | Same; MUT-7 survived (P4) | PASS |

- Idempotency: re-run against a deployed target: N/A, nothing deployed.
- V4 designer open and save: N/A, no designer artefact.
- Cross-OS (C-TECH-054): NOT VERIFIED (macOS only).
- Warnings (C-TECH-055) and diagnostic components (C-TECH-056): N/A. No build; nothing created in any environment.

## What you need to decide

**1. Accept that the service account can read up to a month of raw narrative in PRD, or change the flow's owner?**

**Problem** — ADR-083 item 4 says no person can read AI Event rows, but in DEV they are owned by `svc_grantapplications`, an account a person signs in as (this agent did), and it holds System Administrator.
**Suggested fix** — (a) accept and record it in the DPIA as "readable by whoever holds the service account credentials, at most 31 days" (recommended for now: the daily job is what caps the exposure); or (b) move the scrub flow's Dataverse and AI Builder connections to an application user, which is a design change for architect-agent.
**What happens if you don't** — The DPIA and RoPA would state a control that does not hold in DEV and probably not in PRD. Who reads AI events in PRD would be decided by who holds that password.
[TAD A-NS-45](../../docs/architecture/revitalise-grant-automation-architecture.md#L7187)

---

**2. Why is DEV's paid grant still linked to an application at Under Review?**

**Problem** — Grant `86049ed0…` is Paid with a final payment date, but its application is Under Review. The 6-year job selects on the application's status, so a record like this is kept for ever.
**Suggested fix** — Lead-agent checks the Capture Payment run history for that grant. If the row was set by hand it is test data and nothing changes. If the flow skipped the application update, that is a `wbs:8.6` defect.
**What happens if you don't** — Any paid grant whose application did not reach Grant Paid is never deleted, which breaks C-DOM-003 without anyone seeing it.
[ADR-083 job definition](../../provisioning/dataverse/ensure-bulk-delete-jobs.ps1#L300)

---

**3. Close `A-RET-1` and `A-NS-47` in DEV now, or record an `OVERRIDE`?**

**Problem** — Both can be closed in DEV, and the test-agent rule fails the run until they are.
**Suggested fix** — (a) authorise one DEV session that writes the four synthetic applications of `A-RET-1`, runs the query, then runs a one-off (non-recurring) `BulkDelete` for each key and records the deleted counts (recommended; DEV's AI events are test text, and this is not a standing job, so D-1 holds); or (b) reply `OVERRIDE A-RET-1` / `OVERRIDE A-NS-47` with a reason, and they close on the first TST/ACC and PRD runs.
**What happens if you don't** — The first proof that the platform accepts either job comes from the reviewer's PRD run. A refusal there means hand-building the job in the wizard at go-live.
[Dev Summary §10](../../docs/development/revitalise-grant-automation-dev-summary.md#L13307)

---

## 8. Recommendations

1. development-agent: add one assertion that the `aiEvents` column set is `msdyn_aieventid` (D-ADR083-1).
2. development-agent: mark the literal 5 and 6 in [DeploymentSettings L565](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L565) *count-coupled by design*, or derive them (C-TECH-067).
3. architect-agent: add a register row for "the job owner can read the secured `rev_finalpaymentdate`". It holds for a System Administrator owner, which the TAD already requires.
4. Write FetchXML for `pac env fetch --xml` with single-quoted attributes on macOS (IMP-1220).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1219 | `design-premise-about-identity-type-unmeasured` | friction | When a design rests on 'no person can read it', measure the owning identity's accessmode and roles, not its name. |
| IMP-1220 | `cli-argument-quoting` | friction | Write FetchXML attributes with single quotes when passing it to pac env fetch --xml. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

Verification: 589 targeted and 791 full-suite Pester tests passed, 0 failed; 7 of 8 mutations caught; 8 read-only DEV queries. Not verified: any `BulkDelete` acceptance or execution, Linux execution, audit of bulk deletes, TST/ACC or PRD state.
