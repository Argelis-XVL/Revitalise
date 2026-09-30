# Test Report — Revitalise Grant Automation (WI-0008 wellbeing sub-sections; wbs:6.8)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260930-5/
**Date:** 2026-09-30
**Status:** PARTIAL
**WBS:** `6.8` (WI-0008). Other test-result deliverables are not claimed.
**Target:** DEV code-app push only. Previous cycle: [20260930-4 report](revitalise-grant-automation-test-report-20260930-4.md) (validated and deployed).

---

## Summary

**PARTIAL: safe to push to DEV, nothing found wrong, but no trustee has seen the screen yet.** The only change since 20260930-4 is that the wellbeing answers in Current Circumstances are split into three headed groups with a wider gap between groups than between rows. Every row label and its order is identical to -4. The spacing check is a real browser measurement, and I proved it can fail: with the spacing rule removed it fails at all three widths; with it, it passes.

**Waiting on you:** approve the DEV code-app push, then do the check in section 8.

---

## What was verified

1. **Delta confirmed by me, not taken from the brief.** I unzipped the managed and the unmanaged solution zip of -4 and -5 and compared every member: identical in both. The `provisioning/` folders are identical. In the code app only the script (`index-CZyWPEFg.js` to `index-Bvg85yZA.js`), the stylesheet and `index.html` differ. So no solution, flow, role, profile or column changed.
2. **Row order and labels unchanged from -4.** I pulled all 89 `label:"..."` strings, in order, from both shipped bundles: the lists are identical. The bundle headings differ by exactly one entry: `Life satisfaction` (new). The other two sub-headings ("In the last 2 weeks…", "In the last year…") already existed in -4's bundle. The ordering against the PDF was checked in the -4 report (its item 2) and, because the sequence is unchanged, that result stands. The new heading text is the one the reviewer confirmed.
3. **The three groups are in the shipped bundle.** [The layout](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L432) has an unheaded group (C1, the score) then "Life satisfaction" ([line 449](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L449)), "In the last 2 weeks…" ([line 465](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L465)) and "In the last year…" ([line 505](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L505)); the bundle shows C2 as the first row of "Life satisfaction".
4. **The spacing rule is shipped.** The -5 stylesheet contains `._detailGroup+._detailGroup{margin-top:var(--space-12)}` (48px); -4's stylesheet has no `detailGroup` at all. Source: [app.module.css](../../src/code-apps/trustee-review-portal/src/styles/app.module.css#L656).
5. **The group-gap browser check is real.** [The Playwright spec](../../src/code-apps/trustee-review-portal/src/test/visual/application-detail-layout.visual.spec.ts#L164) measures, in Chromium at 320, 390 and 1280px, that the smallest gap between groups is at least twice the largest gap between rows, and that no heading sits above the previous group's last answer. Run 1 (as shipped): 8 of 8 pass. Run 2 (I changed the rule to `margin-top: 0`): the three new tests fail, `Expected >= 32, Received 12 / 12 / 0`; the other three layout tests still pass. Run 3 (rule restored, file byte-identical to before): pass. The two round-statistics tests are unaffected.
6. **No secured column requested.** I scanned every `rev_` name in the -5 bundle against the packed `customizations.xml` (79 secured columns; positive control `rev_carecostsexplanation` is flagged). The only hit is `rev_applicantid`, the same unsecured-on-`rev_application` key as in the -4 report.
7. **Suites re-run by me on this tree.** Code app: 792 of 792 pass (44 files), type check clean. That is 2 more than -4's 790, consistent with the new sub-section tests, though I did not diff test names. Pester and the source gates were not re-run: no file they cover differs from -4 (item 1), so the -4 results (1245 pass, 16 of 16) carry forward.

---

## What this lets me claim, and what it does not

**Can claim:** V2 for the artifact (packaged; delta and bundle inspected), V1 for the grouping and V1/measured-in-Chromium for the spacing (harness, not the real app).
**Cannot claim:** V3 or above. Not observed: a trustee opening a real case in DEV. WI-0008 stays at `packaged`.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit: code app vitest | 792 | 792 | 0 | 0 |
| Unit: Pester | carried from -4 | | | no differing file |
| Integration: source gates | carried from -4 | | | no differing file |
| Integration: artifact diff against -4 (2 zips, provisioning, code app) | 4 | 4 | 0 | 0 |
| Integration: bundle labels and headings against -4 | 2 | 2 | 0 | 0 |
| Real-browser: detail layout and group gap (Chromium, 3 widths) | 6 | 6 | 0 | 0 |
| Negative control: gap test with rule removed | 3 | 0 | 3 (expected) | 0 |
| Security: secured-column scan of bundle | 1 | 1 | 0 | 0 |
| Accessibility | n/a | | | Headings are h3 inside the existing h2 panel; heading order to confirm in the browser check |
| Performance | n/a | | | Bundle 1,210.83 kB, warning already accepted |
| Provisioning | n/a | | | Folder identical to -4 |

## 2. Defects

None.

## 3. Observations

- **Obs-1.** The spacing is measured in the test harness page, not the deployed app, so the real-screen look is the post-deploy check.
- Carried forward from -4: comment-only Obs-1 (stale "row X3"), F5 empty until automation #5.

## 5. Constraint Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Hand-authored artefacts have a register row | PASS | No platform artefact differs from -4 |
| C-TECH-053 | Level claimed equals level confirmed | PARTIAL | Manifest claims V2; I confirm V2 |
| C-TECH-054 | Pipeline scripts run on runner's OS | PARTIAL | Build on macOS, no Linux run. Unchanged |
| C-TECH-055 | Tool warnings triaged | PASS | Manifest: 5 warnings, 5 accepted, 0 untriaged |
| C-TECH-056 | Diagnostic components removed | PASS | Solution zips unchanged |
| C-TECH-057 | Gates proven able to fail | PASS | Item 5 negative control; item 6 positive control |
| no-secured-columns-in-code-app (HARD) | Portal requests no secured column | PASS | Item 6 |
| All other in-scope rows | | PASS (carried forward) | Solution and provisioning byte-identical to -4 |

No HARD violation.

## 6. Provisioning Verification
Identical to -4; carried forward.

## 7. Platform Contract & Verification-Level Audit
### 7.1 Assumption register
Unchanged: no flow, column or fail-safe default touched. No orphan artefact.
### 7.2 Levels

| Component | Claimed | Confirmed | Result |
|---|---|---|---|
| Wellbeing three sub-sections (WI-0008) | V2 | V2 (bundle), V1 (tests, Chromium harness) | PARTIAL: not V3 |
| Everything else | unchanged | unchanged | Carried forward |

V4 human check: `OPEN`, section 8.

## 8. Post-deploy check for the reviewer
As a **trustee**, open an individual application in DEV and scroll to Current Circumstances. Confirm: the score line, then three headed groups ("Life satisfaction", "In the last 2 weeks…", "In the last year…"), each heading visibly separated from the answer above it, real questions and answers, and the same row order as before. WI-0008 can be closed on this check.

## 9. Recommendations
Approve the DEV code-app push of -5 (no solution import needed; the solution zips equal -4's).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged
None.
