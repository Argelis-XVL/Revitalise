# Test Report — Revitalise Grant Automation (WI-0013 wellbeing wording, WI-0053 pink rectangle; wbs:6.8)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260930-6/
**Date:** 2026-09-30
**Status:** PARTIAL
**WBS:** `6.8` (WI-0013, WI-0053). Other test-result deliverables are not claimed.
**Target:** DEV code-app push, plus one changed flow in the solution zip.
**Previous cycle:** [20260930-5 report](revitalise-grant-automation-test-report-20260930-5.md)

---

## Summary

**PARTIAL: safe to push to DEV, nothing found wrong, but no one has looked at either fix in a browser.** Both items are present in the shipped bundle: the wellbeing labels use the question wording and the chart component can no longer draw its own bar. The one flow change nobody asked for is equivalent to the old one on reading and passes the static gates, but no test runs the expression.

**Waiting on you:** approve the DEV push, then do the check in section 8.

---

## What was verified

1. **Delta confirmed by me, not taken from the brief.** I unzipped the managed and unmanaged zips of -5 and -6 and compared every member: exactly one differs in each, the [round statistics flow](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L3005). The `provisioning/` folders are identical. In the code app only the script (`index-BHFze4c4.js`) and `index.html` differ.
2. **WI-0013 is in the bundle.** "Go out and do something you enjoy", "Enjoy other people’s company" and "Have a break when you’ve needed one" are each present once in -6. "Wellbeing question 8", "9" and "10" were present in -5 and are absent in -6. The [heading map](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L764) feeds the chart series at [charts.ts](../../src/code-apps/trustee-review-portal/src/domain/charts.ts#L123). The circumstance score title "Circumstance score, 0 to 60" is in both bundles, so the second clause was already met.
3. **WI-0053 is in the bundle.** `chartBar` appears 3 times in the -5 script and 0 times in -6. The "Exceptional circumstance cited" call site ([RoundStatistics.tsx](../../src/code-apps/trustee-review-portal/src/components/RoundStatistics.tsx#L498)) passes no picture, so it now renders a title and table only. Two tests pin it: [component](../../src/code-apps/trustee-review-portal/src/components/DistributionChart.test.tsx#L295) and [full screen](../../src/code-apps/trustee-review-portal/src/pages/LandingPage.test.tsx#L124). The old stylesheet rule for `chartBar` is still in the CSS as dead code, which is harmless.
4. **The flow change.** Source and both zip members are byte-identical (same sha256). The new expression tests the same three conditions as the old one and returns the text `true` or `false` instead of `string(<boolean>)`. The description is 237 characters, under the 256 limit. No other flow in the solution uses `string()` around a boolean.
5. **Suites re-run by me.** Code app: 792 of 792 pass (44 files), type check clean. Source gates: 16 of 16 pass, including flow-definition-language, component-shape and field-length-limits.

---

## What covers the flow change, and what does not

**Covered:** a build-agent packed it; a development-agent review called it sound; static gates pass (well-formedness, field length, flow language rules, packed component shape). It is logged as an out-of-dispatch edit (IMP-0981, in the [log](../../logs/improvement-log.jsonl#L977)).

**Not covered:**
- No work item names it, so the board does not track it.
- No test evaluates the expression, so "string of a boolean renders True/False" is reasoned, not measured.
- It has not been imported or run. The unseeded-threshold branch, which the design says must answer `null`, is textually unchanged but not executed.

The first two bullets cannot be closed from here. The third closes with the DEV import and one run of the statistics flow.

---

## What this lets me claim, and what it does not

**Can claim:** V2 for the artifact (packaged, delta and bundle inspected), V1 for both code-app fixes (tests and bundle strings).
**Cannot claim:** V3 or above. Nobody opened the round overview in DEV, and the flow has not been imported. V4 and V5 not reached. WI-0013 and WI-0053 stay at `packaged`.

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit: code app vitest | 792 | 792 | 0 | 0 |
| Unit: type check | 1 | 1 | 0 | 0 |
| Integration: artifact diff against -5 (2 zips, provisioning, code app) | 4 | 4 | 0 | 0 |
| Integration: source gates | 16 | 16 | 0 | 0 |
| Integration: bundle strings (6 wording and chart strings) | 6 | 6 | 0 | 0 |
| Security | n/a | | | No new data column or role; -6 requests the same columns as -5 (label strings are static text) |
| Accessibility | n/a | | | Table and caption retained per the design; visual check in section 8 |
| Performance | n/a | | | Bundle 1,209.95 kB, down 0.88 kB, warning already accepted |
| Provisioning | n/a | | | Folder identical to -5 |
| Real-browser (Chromium) | not run | | | No spec covers the round overview legend or the removed bar; harness not extended in this cycle |

## 2. Defects

None.

## 3. Observations

- **Obs-1.** Long question wording in chart legends and axis labels has not been seen rendered. Truncation or wrapping is possible.
- **Obs-2.** `chartSummary` in `domain/landing.ts` and the `chartBar` CSS rule are now unused by components. Harmless.
- **Obs-3.** WI-0009 reports one work-items gate failure (stale `CasePanels.tsx` evidence). It predates this work and is not this build's defect.

## 4. Traceability

| Item | WBS | Acceptance | Result |
|---|---|---|---|
| WI-0013 | 6.8 | Wording for wellbeing 8, 9, 10 and circumstance score; datapoint labels not "answer 8, 9, 10" | Met at V1/V2, not seen live |
| WI-0053 | 6.8 | Rectangle not rendered beside "Exceptional circumstance cited" | Met at V1/V2, not seen live |

## 5. Constraint Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-014 | Unit test coverage threshold | PASS | 792 of 792 pass; the build manifest reports its coverage gate green; not re-derived by me |
| C-TECH-052 | Hand-authored contracts have a register row | PASS | No new hand-authored platform contract; the flow edit changes an expression, not a shape |
| C-TECH-053 | Level claimed equals level reached | PASS | Claim is V1/V2; section above says V3 and up are not reached |
| C-TECH-054 | Scripts run on the CI OS | PASS | No script added or changed |
| Secured columns in code app | No secured column requested | PASS | `no-secured-columns-in-code-app` gate passes |
| Field-length limits | Designer limits on flow text | PASS | Description 237 of 256 |
| Domain constraints | In scope for a label and chart change | PASS | No personal data, scoring or audit behaviour touched; `domain-invariants` gate passes |
| Remaining C-TECH rows | Not touched by this delta | Not re-run | Carried from the build manifest's `constraint_check: PASS`; I did not re-verify each of the 59 |

## 6. Fail-safe default check

The one fail-safe in the delta is the flow's unseeded anomaly threshold answering `null`. That text is unchanged in -6. No test reaches the success outcome under that default in this cycle, and none did in -5. It is carried, not newly opened.

## 7. Platform Contract and Verification Level

**7.1** No new §10 assumption. Revision 12 states none. The claim that `string(<boolean>)` yields `True` or `False` has no register row and no measurement.
**7.2** Code app V1 to V2. Flow V2 (packed, accepted by the packer). V3 needs the DEV import. V4 needs a human open-and-save. V5 needs one run.

## 8. Recommendations

1. Approve the DEV push of `revitalise-grant-automation-20260930-6`.
2. After import, open the Round overview as a trustee. Confirm: (a) the wellbeing Q8 to Q10 legend, tooltip and table rows read the question wording; (b) no pink rectangle under "Exceptional circumstance cited"; (c) long labels do not clip.
3. Run the round statistics flow once with the anomaly threshold seeded and once unseeded, and confirm the response parses. This closes the gap in the flow section above.
4. Ask the lead to raise a work item for the flow change, so the board tracks it.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none new | | | The out-of-dispatch flow edit is already logged as IMP-0981 |
