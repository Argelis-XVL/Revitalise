# Test Report — Trustee Portal Visual Refresh (v16)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260925-2/`
**Date:** 2026-09-25
**Status:** PASS (source/V1–V2, gated for pipeline) — EF-04 and EF-43 are both confirmed correct
against ground truth this test-agent re-derived itself, not merely against the Dev Summary's own
account of them. Live DEV import/render (V3+) has not been attempted for this build and is not
claimed.

---

**Why this cycle exists.** Dev Summary Revision 1.19 (`wbs:6.8,6.10`) re-opens EF-04 a second
time — Revision 13's own comment claimed the Summary panel was delivered, and that claim was
false on the live screen (`IMP-0885`) — and builds EF-43 as its own screen. The dispatch brief
for this cycle explicitly flagged that both items are "reviewer-confirmed... by development-agent's
own re-verification pass, not just by compiling/testing" and asked this level to check that claim
rather than re-trust it, given the immediately preceding history of a false claim on the same
component. This cycle re-derives both fixes from the same primary sources development-agent
cites — the PDF and the feedback spreadsheet — rather than reading the Dev Summary's narrative as
sufficient.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app) | `npx vitest run` in `src/code-apps/trustee-review-portal`, independently re-run against the checked-out tree (matches the artifact — `manifest.json` `source_commit` `4192240`, current `HEAD` the same) | 797 | 0 | 0 |
| Unit (Pester) | Carried from `build/artifacts/trustee-portal-visual-refresh-20260925-2/test-results/pester-results.xml` (not independently re-run this cycle — no PowerShell/flow-JSON surface touched by EF-04/EF-43) | 1148 | 0 | 1 |
| Integration | `App.tsx` nav-state wiring (`fromGroup`, `groupCode`/`onBackToGroup`) covered by `App.test.tsx`'s 3 new/changed tests, part of the 797 above | — | — | — |
| End-to-End | Not reachable — this build has not been imported anywhere (V2 only, see §7.2) | — | — | — |
| Regression | `tsc --noEmit`, `eslint`, full local gate chain, independently re-run this cycle (below) | 6/6 | 0 | 0 |
| Security | No new auth/input surface — UI reordering and a new screen reusing existing, already-scoped data reads (`GroupsTable`/`ApplicationFilters` unchanged) | N/A | N/A | N/A |
| Accessibility | New/changed screens spot-checked (below) | — | 0 | — |
| Performance | Bundle budget re-checked (below) | 1/1 | 0 | 0 |
| Provisioning | No schema/provisioning change this scope | — | — | — |
| Compliance | No special-category/PII surface changed — `GroupsListPage`/`GroupsTable` expose the same fields the removed embedded table already did | N/A | — | — |
| **Total** | | **1945** | **0** | **1** |

Independently re-run by this test-agent this cycle, against the checked-out tree:

```
npx vitest run   (src/code-apps/trustee-review-portal)
    → 43 files, 797/797 tests passed
npx tsc --noEmit -p tsconfig.json   (src/code-apps/trustee-review-portal)
    → 0 errors
npx eslint .   (src/code-apps/trustee-review-portal)
    → 0 problems
python3 scripts/verify-css-arithmetic.py .
    → PASS — 5 authored stylesheets, ambient body size 17px; no rule/grid finding
      (no CSS changed this revision — confirmed via `git status --porcelain | grep '\.css'`, no hits)
python3 scripts/verify-code-app-bundle-budget.py src/code-apps/trustee-review-portal
    → PASS (via manifest.json's own code_app_bundle block: 1,209,890 / 1,241,000 js bytes,
      77,220 / 79,500 css bytes)
python3 scripts/verify-improvement-log.py --check
    → OK (schema + triggers), 892 entries (223 NEW, 660 APPLIED, 9 REJECTED), 9 warnings,
      0 unread blocker
python3 scripts/derive-wbs-state.py && python3 scripts/verify-wbs-chain.py
    → PASS — 0 violations, 40 warnings, 6 accepted exceptions (none touching wbs:6.8/6.10)
```

All figures reconcile against `build/artifacts/trustee-portal-visual-refresh-20260925-2/manifest.json`
(`status: SUCCESS`, `constraint_check: PASS`, `unit_tests.pester_passed: 1148`,
`code_app_bundle.result: PASS`, `solution_checker: 0 Critical, 0 High, 1 Medium, 0 Low, 0 Informational`
— meets the zero-Critical/zero-High policy; the Medium finding is in the packaged solution as a
whole, not attributable to this scope's code-app-only diff, and is not investigated further here).

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| EF-04 Δ4 (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 6) — panel order and heading match the delivered Trustee Pack | `<ScorePanel>` renders first at [`ApplicationDetailPage.tsx:247`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx), headed `"Summary"` at [`CasePanels.tsx:192`](../../src/code-apps/trustee-review-portal/src/components/CasePanels.tsx); locked by [`CasePanels.test.tsx:80`](../../src/code-apps/trustee-review-portal/src/components/CasePanels.test.tsx) and [`ApplicationDetailPage.test.tsx:56`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.test.tsx) | **PASS — re-derived independently, not read from the Dev Summary.** Opened `docs/Import/3. Round 4 - Individual Applications.pdf` p.1 directly this cycle: its own first section is titled "...INDIVIDUAL- Summary" and its first table is exactly the Application ID / Are you? / Score / Start-End Date / Individual Total / Exceptional Funding rows, ahead of "Application Details". The shipped screen's order (Summary → the portal-only Narrative panel → Application Details → …) puts the pack's own first section first. Independently re-ran `npx vitest run` (797/797, includes both regression tests above) |
| EF-04 — deliberately NOT widened to the pack's full Summary row set | `CasePanels.tsx` Revision 14 header, [`CasePanels.tsx:902-911`](../../docs/development/trustee-portal-visual-refresh-dev-summary.md) (Dev Summary citation) | **PASS, reasoning checked, not just read.** Three independent reasons given (Application ID already the `<h1>`; Start/End Date and total funding already in `HolidayPanel`; Exceptional Funding Amount blocked by OQ-031's own recorded reviewer answer) — the reviewer's own words ("Summary panel is missing at the top of the screen") are answered by section presence and order, not by row-for-row duplication. No test contradicts this; not a widened-scope claim to verify further |
| EF-43 Δ4/Δ5 (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 50) — group applications becomes its own screen with its own nav tab and a route back from a group member's detail page | `GroupsListPage.tsx` (new), routed from `App.tsx` nav button at [`App.tsx:346`](../../src/code-apps/trustee-review-portal/src/App.tsx); `groupCode`/`onBackToGroup` at [`App.tsx:417`](../../src/code-apps/trustee-review-portal/src/App.tsx) and [`ApplicationDetailPage.tsx:211`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.tsx); `GroupsTable` removed from `ApplicationsListPage.tsx`, locked by the `ApplicationsListPage — the group table is GONE (EF-43 Δ5)` describe block at [`ApplicationsListPage.test.tsx:188`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationsListPage.test.tsx) | **PASS — re-derived against the reviewer's own words in the spreadsheet row, not the plan's paraphrase.** Read row 50 directly this cycle: the four asks (whitespace/stacking complaint, separate screen "that is a copy" of the individual list, back-route from a group member's detail page, a new nav-bar tab) are each answered by one of the four changes the Dev Summary lists, confirmed present in source at the cited lines. `GroupsListPage.test.tsx` (new) covers title, both empty states, field set, opening a group, and filter behaviour — the coverage the old embedded describe block used to provide |
| EF-43 — the two-empty-state distinction ("no groups at all" vs "filters match nothing") | [`GroupsListPage.test.tsx:34`](../../src/code-apps/trustee-review-portal/src/pages/GroupsListPage.test.tsx), [`:110`](../../src/code-apps/trustee-review-portal/src/pages/GroupsListPage.test.tsx) | PASS — both cases present and distinct, matching the existing `ApplicationsListPage` pattern this screen copies |
| Regression — every other reviewer-confirmed item this revision leaves untouched (EF-07, EF-37 delivered; EF-09 correctly blocked) | Not re-verified this cycle — out of this dispatch's diff, no source change | **Carried, not re-tested.** No file touched by Revision 1.19 intersects these items' own components per `git status --porcelain` scoped to `trustee-review-portal/` (16 changed paths, all named in Dev Summary §2) |

## 3. Failed Tests

None.

## 4. Defects Raised

None. One process note, not a defect: `contract/change-orders/CO-005.md` establishes `6.10` as a
covered change-order task id (not one of the 61 baseline tasks in `contract/wbs.json`) — confirmed
by [`CO-005.md:54`](../../contract/change-orders/CO-005.md) and by `verify-wbs-chain.py` reporting 0
violations against it. Recorded here only because this cycle checked it rather than assumed it,
per `IMP-0724`'s own caution not to describe a change-order id as baseline.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-076 | CSS arithmetic (line-height / auto-fit column count) | PASS (N/A — no CSS changed) | `git status --porcelain \| grep '\.css'` — no hits; `verify-css-arithmetic.py` PASS, 5 stylesheets |
| C-TECH-052 | Every hand-authored platform artefact has a register row | PASS (N/A — no new platform-guess artefact; EF-04/EF-43 are code-app TSX/test-only) | No new Dev Summary §10 row added this revision; none required |
| C-TECH-053 | Verification level claimed matches level confirmed | PASS | See §7.2 — claimed V2, confirmed V2, no overclaim |
| C-TECH-055 | Build/pack warnings triaged | PASS | `manifest.json` `warnings: {total:2, accepted:2, untriaged:0}`; bundle-size drift row cites this revision's own ~5.2 kB increase, consistent with `GroupsListPage.tsx` landing |
| C-DOM-030 | No special-category column influences scoring | PASS (N/A — no scoring surface touched) | `GroupsTable`/`CasePanels` field sets unchanged by this revision; `no-special-category-data-in-scoring` build step in `manifest.json`'s `platform_limit_gates` |
| C-COM-002 | Work enters by WBS task id | PASS | `wbs:6.8,6.10` both covered — `6.8` in `contract/wbs.json`, `6.10` in `contract/change-orders/CO-005.md`; `verify-wbs-chain.py` 0 violations |
| C-COM-004 | No fee/rate figures in tracked files | PASS | This report, the Dev Summary Revision 1.19 section and its hours-proposal addendum all state hours only |

Full constraint check (all HARD+SOFT rows scoped to `test-agent`) was not re-run row-by-row this
cycle beyond the rows above: this revision's diff is confined to `src/code-apps/trustee-review-portal/**`
(TSX + test files only, no schema/flow/security surface), and `manifest.json`'s own
`constraint_check: PASS` covers the full-solution gate chain build-agent already ran against the
same tree. The rows above are the ones whose scope specifically intersects this diff.

## 6. Provisioning Verification

Not applicable — no TAD §12 or §6.1 item touched by this revision (code-app UI change only, no
new site/team/app registration/role/sharing).

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

No Dev Summary §10 row was added or touched by Revision 1.19 — EF-04/EF-43 are author-composed UI
logic (panel order, heading text, a new screen reusing existing components), not a platform guess.
Confirmed by reading Dev Summary §10 in full: every row present concerns the round-statistics flow
(`A-FLOW-*`, `A-LAND-*`, `A-TR-*`, `A-DS-12`), none of which this revision's diff touches. No
orphan found: `verify-assumption-markers.py`'s last recorded run (Revision 1.19's own checklist,
35 OPEN rows across 10 documents) is unaffected by a TSX/test-only change.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| EF-04 (panel order + heading) | V2 — "Not pushed to any environment" ([Revision 1.19 checklist](../../docs/development/trustee-portal-visual-refresh-dev-summary.md)) | **Confirmed at exactly V2** — source correct, `tsc`/`eslint`/`vitest` clean, matches PDF ground truth read directly this cycle | `ApplicationDetailPage.tsx:247-249`, `CasePanels.tsx:192`, independent `npx vitest run` (797/797) | PASS — claim matches confirmed level |
| EF-43 (GroupsListPage + nav + back-link) | V2 — same | **Confirmed at exactly V2** | `GroupsListPage.tsx`, `App.tsx:335-422`, `GroupsListPage.test.tsx` (6 new tests, all passing) | PASS |
| Whole artifact (`trustee-portal-visual-refresh-20260925-2`) | `manifest.json`: `"V2 — packaged; layout accepted by the packer. Content, platform acceptance and designer/editor usability are NOT proven by this build."` | Confirmed — `pac solution check` 0 Critical/0 High; no import attempted | `manifest.json` | PASS |

- Idempotency: N/A this cycle — no import attempted, nothing to re-run.
- V4 designer/editor open + save: N/A this cycle — code-app TSX/test change, no Dataverse/flow
  artefact touched; V4 does not apply to this scope.
- Cross-OS (C-TECH-054): N/A this cycle — no new script authored.
- Warnings triaged (C-TECH-055): PASS — `manifest.json` `warnings: {total:2, accepted:2, untriaged:0}`.

**This cycle does not claim V3, V4 or V5 for EF-04/EF-43, and neither does the Dev Summary.** The
"reviewer-confirmed" language in the dispatch and in Revision 1.19 describes the reviewer's live
observation of the *pre-fix* screen (the defect that triggered this revision — confirmed directly
against `docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 6/50 "today" column, both read
"Not done yet"/"Partly done" as of the check date), not a live observation of this fix. The fix
itself has never been imported or rendered live. That gap is stated plainly, not implied by
omission: **the next cycle to touch this build must be a live DEV import (V3) and a signed-in
trustee screen check (V4/V5) before EF-04/EF-43 can be called delivered rather than merely
correct-in-source.**

## 8. Recommendations

1. Proceed to pipeline for a DEV import of `trustee-portal-visual-refresh-20260925-2` — this is
   the only way to close V3 for EF-04/EF-43, and per the Fail Conditions rule "an OPEN assumption
   against an environment that could close it" is a defect on the *next* cycle, not this one,
   because this cycle has no environment yet to close anything against.
2. On the next test cycle after import, verify live: (a) the detail screen's first panel reads
   "Summary" for a real application; (b) the new "Group applications" nav tab is present, opens
   the new screen, and a group member's detail page offers "Back to group …".
3. No action needed on the `6.10` change-order-id note in §4 — it is correctly covered, recorded
   here only as a checked fact rather than an assumed one.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle independently re-derived both EF-04's pack order and EF-43's reviewer asks from the primary sources (PDF, feedback spreadsheet) rather than the Dev Summary's own narrative, and found no drift. `6.10`'s change-order (not baseline) status was checked directly (`CO-005.md`, `verify-wbs-chain.py`) rather than assumed, and found correctly covered. No new defect class, no stale claim, no capture trigger from `skills/how-to-log-an-improvement.md` applies. |
