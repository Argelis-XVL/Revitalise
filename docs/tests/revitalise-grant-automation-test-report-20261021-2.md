# Test Report — Revitalise Grant Automation, flow #7 Finalise Decisions (wbs:6.6) and flow #11 Capture Payment (wbs:8.6), build 20261021-2

**Feature Slug:** revitalise-grant-automation
**Artifact:** [`build/artifacts/revitalise-grant-automation-20261021-2/`](../../build/artifacts/revitalise-grant-automation-20261021-2/manifest.json) (packed from a dirty tree, 27 uncommitted paths, per its manifest; `scoped: false`)
**Date:** 2026-10-21  **Tester:** test-agent (standard tier, no override)  **WBS:** 6.6, 8.6 (the Test results deliverables feed tasks 6.x and 8.5)
**Items:** WI-0129; WI-0131 to WI-0139 and WI-0141 to WI-0144 ride in the same package
**Status:** FAIL. One Fail Condition is met and nothing else is: 12 of the 14 OPEN Dev Summary §10 rows could be closed in DEV, which exists, and none is (C-TECH-058). No defect was found in the source, the package or the tests.

Highest level this agent executed: **V1** (local tests) and a byte check of the V2 package. DEV facts below are the reviewer's, quoted and not upgraded (C-TECH-053).

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped | Evidence |
|---|---|---|---|---|---|
| Unit and integration, solution (Pester, whole suite, re-run by test-agent) | 1481 | 1480 | 0 | 1 | `src/tests/Invoke-Tests.ps1`, 392 s, matches the manifest's own count |
| Flow #7 file alone | 36 | 36 | 0 | 0 | [`FinaliseDecisions.Tests.ps1`](../../src/tests/solutions/FinaliseDecisions.Tests.ps1), incl. the single-chain and one-`runAfter`-key tests |
| Code app, trustee-review-portal (vitest, re-run) | 790 | 790 | 0 | 0 | 45 files; `tsc --noEmit` clean |
| Code app, trustee-review-portal-cards (vitest, re-run) | 888 | 888 | 0 | 0 | 49 files; `tsc --noEmit` clean |
| Regression | included above | | | | The two code-app bundles are the vite 7.3.7 bump (Dev Summary §16). Installed vite is 7.3.7 in both. The build recorded identical bundle sizes to build -8 |
| Security (static) | 3 | 3 | 0 | 0 | `npm audit --audit-level=high`: 0 vulnerabilities in both apps; flow-definition check 11 (secure outputs on personal-data reads) OK for 13 flows |
| Source gates re-run by test-agent | 4 | 4 | 0 | 0 | flow-definition-language (13 flows, checks 11 to 18), assumption-markers (82 OPEN rows each carrying its marker), assumption-register (234 rows), improvement-log schema |
| Package fidelity | 4 | 4 | 0 | 0 | Flows 1012 and 1013 are byte-identical to source in both the unmanaged and managed zips. Builds -6 and -2 differ in the unmanaged zip in exactly one file, the flow 1012 JSON, so flow 1013 is unchanged since the build the reviewer accepted |
| Build run | 102 steps | 101 ran | 0 | 1 | `auth` skipped (out of context, V3 not established by the build); Solution Checker 0 critical, 0 high, 1 medium (standing row) |
| Accessibility, Performance | N/A | | | | No screen source changed; the apps were rebuilt for the dependency bump only |
| Provisioning | not run | | | | No Graph or Dataverse query was made by this agent. The deploy re-read (13 of 13 flows match live) is pipeline-agent's, [pipeline.log](../../logs/pipeline.log#L431) |
| Cross-OS (C-TECH-054) | not run | | | | Tests ran on macOS only; CI's runner was not executed by this agent |

## 2. Requirement Coverage

| Requirement | Test and result |
|---|---|
| Flow #7: the verdict rule, the grant created, the snapshot written, the review stamped (WI-0129 clauses) | Executed by the 36 Pester tests on the shipped JSON: **PASS at V1**. DEV: the reviewer's verdict below |
| Flow #7: one chain in the designer (the third reopen) | Structure asserted by two new tests (single root, one `runAfter` key per action): **PASS at V1**. DEV: the reviewer's verdict below |
| Flow #11: grant date, grant status, application status, reversal, report (FR-107 to FR-113) | Pester `CapturePayment.Tests.ps1` plus the in-memory executions inside the 1480: **PASS at V1**. DEV: the reviewer's verdict below |
| Dependency fix, vite 7.3.7 (wbs:6.1 to 6.4) | Audit, typecheck and both vitest suites re-run by test-agent: **PASS at V1** |

**Reviewer-executed evidence, quoted, not upgraded.**

- Flow #7, DEV, Xander Lykopoulos, 2026-10-21, recorded on `WI-0129` at [work-items.jsonl:917](../../logs/work-items.jsonl#L917): *"Perfect, the finalise workflow now has the right structure in designer and creates a grant. Ready for acceptance testing by the process owner."* This is the reviewer's observation of the designer and of one run that created a grant. It does not say the designer save was done, so no V4 save is recorded. It does not cover a split verdict, a deferral, a retry, several selected rows or a run-only member.
- Flow #11 and the payment rule, DEV, same reviewer, 2026-10-20, recorded on WI-0131 to WI-0139 and WI-0141 to WI-0144 at [work-items.jsonl:895](../../logs/work-items.jsonl#L895) and following: *"Capture payment workflow is working. The business rule is working too. This feature is accepted."* It names no assumption row, so no row is closed by it.

## 3. Failed Tests
None.

## 4. Defects Raised

| ID | Severity | Description |
|---|---|---|
| D-1 | P2 (a Fail Condition, not a code defect) | 12 §10 rows are OPEN and closable in DEV; no `OVERRIDE` is on record. See §7.1 |

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-030](../../constraints/technology/technology-constraints.md#L71) | Deploy beyond DEV needs a PASS or PARTIAL report naming the build | **Not met until this report is PASS or PARTIAL** | `verify-artifact-provenance.py … --env dev` PASS; `--env tst_acc` FAILED before this report existed (no report named the build). With a FAIL report it will still fail |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guess has a register row and a marker | PASS | 82 OPEN rows each carry their marker; 0 source markers without a row; the untracked `Rev-Payment-Issued` rule is a platform export copied unedited ([Dev Summary L13133](../../docs/development/revitalise-grant-automation-dev-summary.md#L13133)), and it is packed |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | §7.2 |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI runner OS | NOT VERIFIED | macOS only |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Warnings triaged | PASS | Manifest: 5 warnings, 0 untriaged |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | NOT VERIFIED | Scratch flow `cecb708b-…` is the reviewer's to delete after the A-FD-10 run ([Dev Summary L13185](../../docs/development/revitalise-grant-automation-dev-summary.md#L13185)). Not re-read live by this agent |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN rows block deployment where closable | **FAIL** | §7.1: A-FD-2, A-FD-4, A-FD-9, A-FD-11 and A-CP-1 to A-CP-7, A-CP-9 name a DEV session or run as their own check, so they did not block the DEV deploy and they do block every later environment. No `OVERRIDE` is on record for any of them |
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS | Check 11 OK over 13 flows; flow #7's alert names an id and a step only ([Dev Summary §14](../../docs/development/revitalise-grant-automation-dev-summary.md#L13219)) |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column drives an automated outcome | PASS | Flow #7's outcome depends on verdicts only; flow #11 reads dates and payment flags only. Static read, not a run |
| Remaining domain rows scoped to test-agent (C-DOM-010, 011, 031, 032) | Audit and secured columns | No change in this build | No column added or secured by either revision per Dev Summary; not re-queried live |
| Configuration defaults the TAD declares fail-safe (IMP-0511 rule) | A test reaches the success outcome at the unseeded default | N/A | Neither flow depends on a seeded `rev_setting` default. The only new setting is `rev_FinanceAlertUpn`, an alert recipient, not a gate on an outcome |

## 6. Provisioning Verification
Not run against any environment by this agent. Two facts the promotion needs, both from source: the TST/ACC deployment settings carry `rev_FinanceAlertUpn` as the token `{{FINANCE_ALERT_UPN_TSTACC}}` ([pac-import-tstacc.json](../../provisioning/deploymentSettings/pac-import-tstacc.json#L26)), and flow #7's run-only share needs the TST/ACC group `REV-PP-GrantApplications-Admins-ACC` ([notes.md L45](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalFinaliseDecisions-8F1C2A44-1012-4B7A-9E21-0A1B2C3D4E12.notes.md#L45)). Neither was checked to exist.

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

Precondition for every row below: *does DEV exist and hold this build?* **Yes** — the build was imported, re-imported and re-read at 11:46 on 2026-10-21 ([pipeline.log L431](../../logs/pipeline.log#L431)). Every row is shown as it stands in the Dev Summary. Nothing was closed by inference.

| ID | Claim (short) | Status per Dev Summary | Closable in DEV? | Result |
|---|---|---|---|---|
| [A-FD-2](../../docs/development/revitalise-grant-automation-dev-summary.md#L12937) | A review with fewer than two verdicts and no outcome is left on the view, nothing changed | OPEN | Yes, one run | OPEN, blocks later environments |
| [A-FD-4](../../docs/development/revitalise-grant-automation-dev-summary.md#L13209) | Connector returns choices as numbers, multi-select as `"1,2"`, date-only as string; `GetItem` returns columns under `body` and accepts `$select` | OPEN | Yes, one run read back | OPEN. The reviewer's run created a grant; the register row was not updated and this agent does not infer closure |
| [A-FD-5](../../docs/development/revitalise-grant-automation-dev-summary.md#L12939) | N approvals start N runs of flow #8 inside DocuSign's call limit | OPEN | Needs the wbs:3.7 bulk test | OPEN, later-environment row |
| [A-FD-7](../../docs/development/revitalise-grant-automation-dev-summary.md#L12940) | A retry between snapshot and stamp can repeat a snapshot row | OPEN | No, nothing to check until it happens | OPEN, not closable |
| [A-FD-9](../../docs/development/revitalise-grant-automation-dev-summary.md#L12941) | Flow menu lists the flow to a run-only admins member and not to Finance; three rows start three runs | OPEN | Yes, test users | OPEN, blocks later environments |
| [A-FD-11](../../docs/development/revitalise-grant-automation-dev-summary.md#L12943) | A user licensed for the app can run the flow without a Power Automate licence | OPEN | Yes, plus a licensing check before TST/ACC | OPEN, blocks later environments |
| A-FD-10 | Trigger shape and id path | CLOSED ([L13208](../../docs/development/revitalise-grant-automation-dev-summary.md#L13208)), measured by export and the reviewer's run | n/a | Not re-verified; accepted as recorded |
| [A-CP-1 to A-CP-7](../../docs/development/revitalise-grant-automation-dev-summary.md#L13047) | Capture Payment trigger, filter, date round-trip, concurrency, status filter, null clears, secured writes | OPEN (seven rows) | Yes, one Finance test-user session. Its work item [WI-0140](../../logs/work-items.jsonl#L853) is deferred: *"Needs a Finance test user in a live DEV session"* | OPEN. The 2026-10-20 acceptance quote is not mapped to rows by this agent |
| [A-CP-9](../../docs/development/revitalise-grant-automation-dev-summary.md#L13055) | The payment business rule: six checks, one run per save | OPEN | Yes | OPEN. The reviewer said the rule works; the six checks are not recorded |
| A-CP-8 | Withdrawn by amendment c | WITHDRAWN | n/a | n/a |

Orphans: none (assumption-markers gate, re-run). A-FD-5 and A-FD-7 are on the list because the reviewer asked for the open rows as they stand; neither is a DEV-closable Fail Condition on its own.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Flow #7 and flow #11 source | V1 | V1, test-agent executed | Sections 1 and 2 | PASS |
| Package | V2 | V2, test-agent confirmed | Byte-identical flows in both zips | PASS |
| Deploy to DEV | V3 | V3, pipeline-agent's record | [pipeline.log L431](../../logs/pipeline.log#L431): import and idempotent re-run exit 0, both code apps pushed, 13 of 13 live flows match. `intake-callback-url-compare` not run (no credential; owner reviewer): the carried-over PARTIAL | Not re-executed by this agent |
| Flow #7 designer and a run that created a grant | not claimed above V3 by the Dev Summary | Reviewer-observed, quoted in §2 | Verbatim quote, `WI-0129` `verified:dev` | Reported, not upgraded. Designer save and live re-read (IMP-1020) is not stated |
| Flow #11 and the payment rule | not claimed above V3 | Reviewer-observed on 2026-10-20, quoted in §2 | Same flow bytes in -6 and -2 | Reported, not upgraded |

- Idempotency: deploy re-run against the already-deployed target, exit 0 (pipeline-agent's record) → PASS.
- V4 designer open and save, then re-read live: **not stated by the reviewer** for flow #7; not performed by this agent → NOT CONFIRMED.
- Cross-OS: NOT VERIFIED.
- Warnings and diagnostic components: warnings PASS; scratch flow not re-read (§5).

## 8. Recommendations

1. **To reach PARTIAL on this same build, no rebuild needed.** Either record the DEV observations against the rows (the reviewer's DEV run covers some of them), or reply with `OVERRIDE <ids>` and a reason for the rows that stay open. Then a short retest dispatch (`-v2`) re-evaluates §7.1 and §5 and flips the Status. A rebuild is not needed because the zips are not at fault.
2. For TST/ACC: set the token for `rev_FinanceAlertUpn`, share flow #7 run-only with the ACC admins group, and run `m365-licensing-check` for A-FD-11 before the process owner is told it can be used without a licence.
3. Delete scratch flow `cecb708b-…` in DEV once A-FD-10's run is accepted.
4. Commit before promotion so the source commit identifies what shipped (27 paths were uncommitted at pack time).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged
None. Digest regenerated: NO (no entry appended).
