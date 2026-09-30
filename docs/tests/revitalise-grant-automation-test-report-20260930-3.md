# Test Report — Revitalise Grant Automation (WI-0052 nav bar order and rename; wbs:6.8)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260930-3/
**Date:** 2026-09-30
**Status:** PARTIAL
**WBS:** `6.8` (WI-0052). Deliverables `4.5` and the other test-result tasks are not claimed by this report.
**Target:** DEV deploy only. Previous cycle: [20260930-2 report](revitalise-grant-automation-test-report-20260930-2.md) (approved, deployed to DEV).

---

## Summary

**PARTIAL: the only change from the deployed artifact is the Trustee Portal nav bar, and it is safe to deploy to DEV.** I checked the delta myself: both solution zips (managed and unmanaged) are file-for-file identical to 20260930-2, the provisioning folder is identical, and the code app bundle differs only by the nav change. All suites are green. Nothing has run on DEV yet, so the bar has not been seen in a browser.

**Waiting on you:** approve the DEV deploy, then look at the Trustee Portal nav bar once and confirm the order and the label.

---

## What was verified

1. **Delta confirmed against 20260930-2, not taken from the brief.** I unzipped both zips of each artifact and compared them: no difference in either. `diff -rq` on `provisioning/` shows no difference. The code app has one differing script (`index-DxpBAQa-.js` vs `index-DQZcTKg3.js`, sizes 1209886 vs 1209892 bytes) and `index.html` differs only in that script name; the stylesheet `index-CSw66u6M.css` is the same. The manifest differs only in the WBS list (4.2 and 4.3 dropped, correctly, since they were deployed), build number, dirty-path count and bundle name. So no flow, table, role or script changed, and the flow results from the last cycle carry over unchanged.
2. **The shipped bundle has the new order and label.** In [the bundle](../../build/artifacts/revitalise-grant-automation-20260930-3/code-app/assets/index-DQZcTKg3.js) the button labels appear in the order Round overview, Group applications, Individual applications. "Applications list" no longer appears; the old bundle had it once and "Individual applications" zero times.
3. **Source change is small and only the nav.** [App.tsx](../../src/code-apps/trustee-review-portal/src/App.tsx#L346) moves the Round overview button first and renames the last one. [ApplicationDetailPage.tsx](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx) changed comments only (I read the diff). No new element, route or handler.
4. **The order is asserted by a test.** [The new test](../../src/code-apps/trustee-review-portal/src/App.test.tsx#L173) asserts the exact list of three names, and the older tests were updated to the new label. Note the 20260930-2 report described the opposite order (Group applications first); this artifact supersedes it as WI-0052 was reopened.
5. **Suites re-run by me on this tree.** Code app: 798 of 798 pass, type check clean. Pester: 1245 pass, 0 fail, 1 skipped (`src/tests/Invoke-Tests.ps1`). Source gates: 16 of 16 pass (`run-source-gates.py`, exit 0).

---

## What this lets me claim, and what it does not

**Can claim:** V2 for the artifact (packaged, bundle inspected), V1 for the nav order (unit test). The work-item WI-0052 is at state `packaged`.

**Cannot claim:** V3 or above for the nav bar. Not observed: the bar rendered in the Power Apps host, the active-tab highlight on each screen there, and the layout on a narrow window.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit: Pester | 1246 | 1245 | 0 | 1 |
| Unit: code app vitest | 798 | 798 | 0 | 0 |
| Integration: source gates | 16 | 16 | 0 | 0 |
| Integration: zips and provisioning vs 20260930-2 | 3 | 3 | 0 | 0 |
| Regression | included above | | 0 | 0 |
| End-to-End: nav bar in DEV | 0 | 0 | 0 | needs DEV deploy |
| Accessibility | n/a | n/a | n/a | Three existing buttons reordered and one relabelled; landmark, `aria-current` and accessible names unchanged in kind. Reading order now matches visual order. No new control. |
| Security | n/a | n/a | n/a | No data, auth or flow change |
| Performance | n/a | n/a | n/a | Bundle +6 bytes |
| Provisioning | n/a | n/a | n/a | Folder identical to the last approved cycle |

## 2. Defects

None.

## 3. Observations

- **Obs-1 (P4).** Stale wording "Applications list" remains only in comments in [app.module.css](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L636) and [layout.test.ts](../../src/code-apps/trustee-review-portal/src/styles/layout.test.ts#L339), and in the visual-refresh architecture doc; none is user-visible. Not a defect.
- Carried forward unchanged from the last cycle: unsecured Dataverse row triggers (IMP-0966) and a selftest depending on a live defect (IMP-0967). Outside this artifact.

## 5. Constraint Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Hand-authored artefacts have a register row | PASS | No new hand-authored platform artefact; solution zips identical |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Level claimed equals level confirmed | PARTIAL | Manifest claims V2; I confirm V2. No V3 or above, see 7.2 |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Pipeline scripts run on runner's OS | PARTIAL | Build ran on macOS; no Linux run. Unchanged from last cycle |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest: 5 warnings, 5 accepted with citations, 0 untriaged |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | PASS | Solution zips identical to the approved artifact |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Gates proven able to fail | PASS | Unchanged from last cycle; gates re-run green |
| All other in-scope rows | | PASS (carried forward) | No file in their area differs from 20260930-2 |

No HARD violation.

## 6. Provisioning Verification

No difference from 20260930-2. Carried forward from [20260928-1 §6](revitalise-grant-automation-test-report-20260928-1.md).

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure
Unchanged: the 9 OPEN rows concern flow save and run behaviour on DEV and are unaffected by this delta (solutions identical; the 20260930-2 import already happened). No configuration default with a fail-safe declaration is touched. No orphan artefact.

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Trustee portal nav order and label (WI-0052) | V2 | V2 (bundle inspected), V1 (unit test) | Items 2, 4 | PARTIAL: not V3 |
| All Dataverse and flow components | unchanged | unchanged | Item 1 | Carried forward |

- Idempotency: N/A, solution unchanged.
- V4 human check: reviewer to view the nav bar on DEV after deploy. `OPEN`

## 8. Recommendations

1. Deploy to DEV (code app only changes; the solution zips are identical, so an import is a no-op).
2. After deploy, open the Trustee Portal and confirm the bar reads Round overview, Group applications, Individual applications, and the highlight follows each screen.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged

None. Digest not regenerated (no entries appended).
