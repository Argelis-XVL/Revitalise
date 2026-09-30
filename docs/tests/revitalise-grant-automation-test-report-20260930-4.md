# Test Report — Revitalise Grant Automation (WI-0005 Trustee Pack detail screen, WI-0008 wellbeing Q&A; wbs:6.8)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260930-4/
**Date:** 2026-09-30
**Status:** PARTIAL
**WBS:** `6.8` (WI-0005, WI-0008). Other test-result deliverables are not claimed by this report.
**Target:** DEV deploy only. Previous cycle: [20260930-3 report](revitalise-grant-automation-test-report-20260930-3.md) (deployed to DEV).

---

## Summary

**PARTIAL: safe to deploy to DEV, nothing found wrong, but no trustee has seen the screen yet.** I compared this artifact with 20260930-3 myself: the only solution change is the one new column, and the only code app change is the rebuilt detail screen. The rendered order matches the PDF and the reviewer's six decisions, the portal names no secured column, and every column it asks for exists in the packed solution.

**Waiting on you:** approve the DEV deploy, then do the four post-deploy checks in section 8.

---

## What was verified

1. **Delta confirmed against 20260930-3, not taken from the brief.** I unzipped both the managed and the unmanaged zip of each artifact. The file lists are identical and the only file that differs, in both, is `customizations.xml`, by one added attribute: `rev_carecostsexplanationredacted`, type ntext, MaxLength 4000, `IsSecured` 0, audit on. The `provisioning/` folders are identical. The code app differs in its script (`index-CZyWPEFg.js` against `index-DQZcTKg3.js`), stylesheet and the `index.html` that names them. So no flow, role, profile or script changed in this cycle. The flow files that show as modified in git were already inside the 20260930-3 zips.
2. **Field order matches the PDF and the map (check 1).** I extracted pages 1 and 2 of the PDF with `pdftotext` and compared the row sequence with [the layout](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L555). Summary, Application Details, About Applicant, Current Circumstances and Financial Eligibility appear in the Pack's order with the Pack's labels, including the Pack's own "Do you savings over £6,000?". The approved deviations are where the reviewer put them: Status and Review round first in Summary ([S0a](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L211), S0b), the "other exceptional circumstance" row directly after D11 ([D11a](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L305)), and the two "other condition" rows directly after A3 ([A3a](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L366), A3b). Their trigger values (4 and 10) equal the "Other (please specify)" option values in [the option maps](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L573). Application ID reads `rev_name`, as ruled. Start and End Date read the two date columns, not the typed text.
3. **Removed rows are gone from the shipped bundle.** I searched the bundle: "Further details (not in the Trustee Pack)", "Provisional date", "Provider preference" and "Score breakdown" do not appear. Seven columns left the bundle (`rev_providerpreference`, `rev_scorebreakdown`, `rev_exceptionalfundingrequested`, `rev_incomeflag`, `rev_exceptionalfundingdetailredacted`, `rev_careprovidedexampleredacted`, `rev_othercareprovidedtyperedacted`) and the listed new ones arrived. "Preferred dates" still appears; it is the applications list screen, which the map says is out of scope.
4. **No secured column is requested (check 2).** Three independent results. The [source gate](../../config/revitalise-grant-automation-build.yml#L766) `no-secured-columns-in-code-app` passes. My own scan of every `rev_` name in the shipped bundle against the packed `customizations.xml` finds no secured column on `rev_application` or `rev_review` (the only hit, `rev_applicantid`, is the applicant table's key and an unsecured column on `rev_application`; it is secured only on `rev_bankaccount`). The positive control works: the same scan flags the secured `rev_carecostsexplanation` as secured (79 secured attributes read).
5. **The new column is unsecured and in no profile (check 2).** `IsSecured` is 0 in the packed XML; `rev_carecostsexplanationredacted` appears zero times in [FieldSecurityProfiles.xml](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml), while its secured source is listed at [line 437](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L437). `verify-field-security-coverage.py` passes (80 secured columns all released, no permission granted for an unsecured column) and `no-trustee-in-column-security-profile` passes.
6. **Every selected column exists in the packed solution (check 3).** I parsed the four column lists in [schema.ts](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L206) (list, detail extra, review; detail is the union) and looked each up in the packed `customizations.xml` of the artifact: none missing. The only bundle names not in the XML are entity-set and key names, not columns.
7. **Suites re-run by me on this tree.** Code app: 790 of 790 pass (44 files), type check clean. Pester: 1245 pass, 0 fail, 1 skipped. Source gates: 16 of 16 pass. The vitest count is 8 below the last cycle's 798; that fits the portal-only rows and tests removed by the reviewer's decision 4, but I did not diff the test names, so treat the reason as likely and not proven.
8. **Pinned in tests.** The layout test holds its own transcription of the PDF ([applicationDetailLayout.test.ts](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.test.ts#L29)); the page test compares the rendered rows to the spec and checks the conditional rows ([ApplicationDetailPage.test.tsx](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.test.tsx#L63)). Note the page test compares the screen with the spec itself, so the PDF match rests on the layout test plus my own comparison in item 2.

---

## What this lets me claim, and what it does not

**Can claim:** V2 for the artifact (packaged, delta and bundle inspected), V1 for row order, conditionals and the no-secured-column rule (unit tests and gates). WI-0005 and WI-0008 stay at `packaged`.

**Cannot claim:** V3 or above for anything. Not observed: a trustee opening a case in DEV, values rendering from real data, and the withheld state.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit: code app vitest | 790 | 790 | 0 | 0 |
| Unit: Pester | 1246 | 1245 | 0 | 1 |
| Integration: source gates | 16 | 16 | 0 | 0 |
| Integration: field-security coverage and trustee-profile membership | 2 | 2 | 0 | 0 |
| Integration: artifact diff against 20260930-3 (2 zips, provisioning, code app) | 4 | 4 | 0 | 0 |
| Integration: bundle and select list against packed XML | 2 | 2 | 0 | 0 |
| Regression | included above | | 0 | 0 |
| End-to-End: trustee sees values in DEV | 0 | 0 | 0 | needs DEV deploy |
| Accessibility | n/a | n/a | n/a | Not exercised. Screen is definition lists and headings; the new rows reuse the existing row component. Confirm heading order in the browser check below |
| Security | 2 | 2 | 0 | Secured-column scan (source and bundle); no auth, role or profile change |
| Performance | n/a | n/a | n/a | Bundle size unchanged in kind (about 1.21 MB, budget warning already accepted) |
| Provisioning | n/a | n/a | n/a | Folder identical to the last cycle. Column existence in DEV is a live fact, see 7.1 |

## 2. Defects

None.

## 3. Observations

- **Obs-1 (P4).** A comment in [the layout](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L238) still says the applicant's typed date "is row X3", a row that no longer exists. Comment only.
- **Obs-2.** F5 stays empty until the narrative-scrubbing automation (#5, deferred) writes the new twin, so trustees will see "withheld" for it after release, like the other twins. Known and stated in the field map.
- Carried forward unchanged: unsecured Dataverse row triggers (IMP-0966), a selftest depending on a live defect (IMP-0967).

## 5. Constraint Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-050](../../constraints/technology/technology-constraints.md#L92) | Columns created by the schema script, not by import | PASS | Lead read-only fetch confirmed the column in DEV; I did not repeat it |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Hand-authored artefacts have a register row | PASS | One new attribute; no other hand-authored platform artefact differs |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Level claimed equals level confirmed | PARTIAL | Manifest claims V2; I confirm V2. Nothing above |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Pipeline scripts run on runner's OS | PARTIAL | Build ran on macOS; no Linux run. Unchanged |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest: 5 warnings, 5 accepted with citations, 0 untriaged |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | PASS | Solution delta is one production column |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Gates proven able to fail | PASS | Positive control on the secured-column scan works (item 4) |
| no-secured-columns-in-code-app (HARD) | Portal requests no secured column | PASS | Items 4, 5 |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) to [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Special-category columns secured and audited | PASS | `domain-invariants` gate passes; new column is an unsecured redacted output with audit on, same position as `rev_narrativeredacted` |
| All other in-scope rows | | PASS (carried forward) | No file in their area differs from 20260930-3 |

No HARD violation.

## 6. Provisioning Verification

No provisioning file differs from 20260930-3. Carried forward from [20260928-1 §6](revitalise-grant-automation-test-report-20260928-1.md).

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure
The 9 OPEN rows concern flow save and run behaviour on DEV and are unaffected: no flow differs from the deployed artifact. One live fact for this delta: the column must exist in DEV before the code app is pushed, or the portal's read of a whole case fails. The lead confirmed it by read-only fetch; the pipeline should re-check it before the push. No fail-safe configuration default is touched. No orphan artefact.

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Detail screen order and conditional rows (WI-0005) | V2 | V2 (bundle), V1 (tests) | Items 2, 3, 8 | PARTIAL: not V3 |
| Wellbeing Q&A rows C2 to C12 (WI-0008) | V2 | V2 (bundle), V1 (tests) | Item 2 | PARTIAL: not V3 |
| New column `rev_carecostsexplanationredacted` | V2 | V2 (packed XML); exists in DEV per lead's fetch | Items 1, 5 | PARTIAL |
| All other components | unchanged | unchanged | Item 1 | Carried forward |

- Idempotency: import of an unchanged solution plus one column is an update; not re-run by me.
- V4 human check: `OPEN`, see section 8.

## 8. Post-deploy checks for the reviewer (cannot be settled offline)

1. As a **trustee**, open one individual application in DEV. Confirm the screen loads (no error banner) and the section and row order matches the PDF, with Status and Review round at the top of Summary.
2. Confirm F1, F2, F3 read "Restricted" and that no benefit, provider or employment value shows anywhere.
3. On an application where D11 is "Other (please specify)" and one where A3 includes "Other", confirm the extra rows appear straight after D11 and A3, and do not appear otherwise.
4. Confirm the wellbeing questions and answers (C2 to C12) show real answers, F5 shows "withheld", and Start and End Date show "Not recorded" until the grant admin fills them.

## 9. Recommendations

1. Approve the DEV deploy (solution import, then code-app push; re-check the new column exists in DEV before the push).
2. Do the four checks above. WI-0008 can be closed on check 4, WI-0005 on checks 1 to 3, per the reviewer's decision 5 and 6.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged

None. Digest not regenerated (no entries appended).
