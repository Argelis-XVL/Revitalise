# Test Report — Trustee Portal Visual Refresh (v13)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260903-3/` (V2, packaged)
**Date:** 2026-09-03
**Status:** PASS (source/V2, gated for pipeline) — **one residual still not closed, unchanged in kind, changed in confidence**

**Scope of this cycle:** Revision 1.11 (`wbs:6.8`, `IMP-0590`) — the fourth attempt at the
category-axis label-overlap defect on
[`RoundStatisticsCharts.tsx`](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L456-495),
and the first attempt in this history backed by a real-Chromium `getBoundingClientRect()`
measurement rather than a re-derivation of the same `dy` arithmetic three prior rounds already
checked (`IMP-0509`, `IMP-0577`, `IMP-0581`, `IMP-0584`). Every claim below on this specific
defect was **independently re-run by this test-agent session**, not taken from `development-agent`'s
or `frontend-agent`'s report — per `IMP-0364`.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | `npx vitest run` (`src/code-apps/trustee-review-portal`) | 771 | 0 | 0 |
| Visual regression (real Chromium) | `npm run test:visual` (Playwright 1.62.1) | 2 | 0 | 0 |
| Integration | Not re-run this cycle (no provisioning source changed since v12) | — | — | — |
| End-to-End | — (source-only artifact; not yet pushed) | — | — | — |
| Regression | Full local gate chain re-run directly this cycle (below) | 5/5 gates | 0 | 0 |
| Security | No new auth/input surface this revision | N/A | N/A | N/A |
| Accessibility | No WCAG-relevant markup change this revision (SVG `dy` relocation only) | N/A | N/A | N/A |
| Performance | Not in scope this revision | — | — | — |
| Provisioning | Not re-run this cycle — no provisioning script touched by Revision 1.11 | — | — | — |
| Compliance | No special-category surface touched this revision | N/A | N/A | N/A |
| **Total** | | **773** | **0** | **0** |

Independently re-run by test-agent this cycle:

```
npx playwright install chromium                    → installed clean, this session had no prior browser cache
npm run test:visual                                → 2/2 PASS (post-fix tree, as delivered)
[reverted only the fix hunk in RoundStatriaCharts.tsx#L486-495 to Revision 12's shape]
npm run test:visual                                → 2/2 FAIL, both at minGap = -4px (exact match to Dev Summary's claim)
[restored the fix; git diff confirms tree returned to the delivered state]
npm run test:visual                                → 2/2 PASS again
npx vitest run                                      → 39 files, 771/771 passed
python3 scripts/verify-improvement-log.py           → OK (schema), 589 entries
python3 scripts/verify-improvement-log.py --check   → OK (schema + triggers), rc=0, 14 warnings (none new/blocking)
python3 scripts/verify-css-arithmetic.py            → PASS, 5 stylesheets, ambient body 17px
python3 scripts/verify-assumption-markers.py        → PASS, 19 OPEN rows, all marked, 46 total
python3 scripts/verify-assumption-register.py       → PASS, 68 rows/17 registers/5 docs, 35 open, none contradicted
python3 scripts/verify-tad-coverage.py               → OK, 174 columns / 13 tables, 8 owned deferrals, 2 baselined findings (unrelated to this defect)
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml → PASS, 72 steps, 57 gates
```

All figures match the Dev Summary's own claims exactly — no drift between what was reported and
what re-running the same commands produces, **and this cycle goes one step further than v12's
re-run**: it reproduces the described *polarity* itself (fails at exactly `-4px` on the reverted
code, passes at `>= 12px` with the fix restored), rather than only re-running the fixed tree once.

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-058/059/060 (round statistics, category-axis charts) | `CategoryBarChart`/`WellbeingComparisonChart` render wrapped category labels without overlapping the plot area | [`round-statistics-charts.visual.spec.ts`](../../src/code-apps/trustee-review-portal/src/test/visual/round-statistics-charts.visual.spec.ts#L43-64) — real Chromium, `getBoundingClientRect()`, asserts `minGap >= 12px` | **PASS — confirmed by a real render, not source self-consistency, and confirmed both ways (fails pre-fix, passes post-fix) by this test-agent independently** |
| WBS 6.8 deliverable — round-statistics category-axis chart fix | Fourth reviewer-reported instance closed with rendered evidence | Independent revert/restore cycle above | PASS at V2/E4 (real browser, this machine's pinned Chromium) — **not V4** (no live signed-in DEV render yet) |

## 3. Failed Tests

None, on the artifact as delivered. (The deliberately-reverted intermediate state used to prove
test polarity failed as expected — see §1 — and was restored before this report was written; `git
diff` against the artifact's source commit shows no residual change.)

## 4. Defects Raised

None new.

## 5. Constraint & Compliance Verification

See the `CONSTRAINT CHECK` block below. No HARD violation and no HARD `UNEVALUABLE` row found in
test-agent's scope. `C-TECH-076` (SVG/CSS arithmetic gate) is explicitly scoped to CSS
declarations, not SVG `dy` values — the structural gap `IMP-0584` named (no build gate can assert
this class of defect symbolically) is unchanged by this revision; it is closed for the *specific*
symptom by the new Playwright test, not by a broadened gate. One SOFT technology row (`C-TECH-067`)
carries an already-accepted warning (fragile literal counts across Pester files), unchanged by this
revision and not re-litigated.

## 6. Provisioning Verification

No provisioning script changed in Revision 1.11. `dev.verification[5]`'s live-DEV run remains the
same open item v12 recorded (no `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` in this session) —
not re-raised here, carried forward per §7.1.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Re-run this cycle: 19 OPEN rows (`verify-assumption-markers.py`), all with a live source marker;
68 rows across 17 registers (`verify-assumption-register.py`), 35 open, none contradicted. No new
`A-nnn` row this revision — the fix corrects which SVG element a previously-declared design token
(`AXIS_LABEL_GAP`) attaches to; it does not introduce a new hand-authored platform-contract guess.
No orphan hand-authored artefact found (`C-TECH-052`).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Whole build artifact | V2 — packaged; layout accepted by the packer, content unverified | **Confirmed V2** | `manifest.json`: `constraint_check: PASS`, `preflight: PASS — 72 steps/57 gates`, `status: SUCCESS`; entry present at [`logs/build.log:76-77`](../../logs/build.log#L76) | PASS at the claimed level |
| **`RoundStatisticsCharts.tsx`'s category-axis label gap** | **V2, real-browser (Chromium), E4** — explicitly **not** V4 (Dev Summary [L2966-2969](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L2966)) | **Confirmed at exactly the level claimed — the first round in this defect's four-round history where the claimed level and the confirmed level are the same thing.** This test-agent independently re-ran the real-Chromium spec against the delivered tree (PASS), then against the pre-fix shape (FAIL at `minGap = -4px`, matching the Dev Summary's own cited figure exactly), then restored and re-confirmed PASS. This closes the gap [`IMP-0584`](../../logs/improvement-log.jsonl#L581) named — a rendered-DOM measurement existed for the first time — and this session did not merely re-read that measurement, it reproduced it | **CONFIRMED at V2/E4 (real Chromium, this machine). NOT V4 — no live signed-in-trustee DEV render exists yet, and none is claimed.** |
| `provisioning/dataverse/verify-solution-components.ps1` (carried from v12, unchanged) | V2 — behavioural, against a fixture | Not re-run this cycle (no change since v12; re-confirming behaviourally-unchanged provisioning outside this cycle's scope would not add evidence) | v12's own re-run stands | Unchanged, carried forward |

- **Idempotency:** N/A this cycle — no provisioning script changed.
- **V4 designer/editor open + save:** not performed — this artifact has not been pushed to any
  environment.
- **Cross-OS (C-TECH-054):** the Playwright spec and harness were authored and run on macOS only,
  by both `frontend-agent` and this test-agent session; CI-runner-OS execution remains a
  pipeline-stage concern → **N/A this cycle, flagged for pipeline-agent**, same as v12's finding
  for the provisioning script.
- **Warnings triaged (C-TECH-055):** manifest shows 8 total, 1 resolved, 7 accepted, **0
  untriaged** (one new citation gap this build, `IMP-0592`, logged by `build-agent` — not this
  feature's own defect, not re-litigated here) → PASS.
- **Diagnostic components removed (C-TECH-056):** no diagnostic component created in a live
  environment this revision (source-only) → PASS, N/A.

**Per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test:** V4 for this
chart genuinely is not yet due — the artifact has not been deployed. Recorded as
`deferred-to-pipeline`, not a violation. What changed this cycle, and is the reason this is not
simply v12 repeated: **the pre-V4 evidence available to test at all has itself changed kind** —
from "the arithmetic is self-consistent" (E3, three times, each disproved live) to "a real browser
measured a positive gap, and measured a negative one when the fix was removed" (E4, confirmed
independently). That is a materially stronger claim than v12's own §7.2 could make, and it is
still honestly short of V4.

## 8. Recommendations

1. **Pipeline-agent's V4 step should still look at this chart specifically on first live render**,
   not because this round's evidence is weak, but because a fourth reviewer-reported recurrence on
   this exact file is what the dispatch was responding to — the first three rounds were also
   "green" by their own evidence standard. Confirming the closure at V4 is normal process, not
   distrust of this round's method.
2. **CI wiring gap, stated plainly and not this test-agent's to close:** `npm run test:visual` is
   not called from any step in `config/revitalise-grant-automation-build.yml` or
   `config/revitalise-grant-automation-pipeline.yml` (confirmed by grep this cycle — neither file
   names `test:visual` or `playwright`). A fifth regression of this exact shape would be caught
   only by a human on a rendered screen until this is wired in. This is a known, already-stated gap
   (Dev Summary [L3965-3971](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L3965)),
   not silently accepted here — flagged for build-agent/pipeline-agent/reviewer, since wiring a new
   build step is outside test-agent's authority.
3. **`C-TECH-076`'s SVG-arithmetic gap remains structurally open**, per `IMP-0584` (`NEW`/unread as
   of this session, confirmed via `verify-improvement-log.py`) — not re-logged here, since nothing
   this cycle changes its status or its lesson.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle re-confirmed the fix independently, at a higher confidence than a re-read (reproducing the fail/pass polarity directly rather than accepting the report), and found no new instance of any class. A re-confirmation is not itself a new finding per `skills/how-to-log-an-improvement.md`'s triggers (no second attempt, no new contradiction, no new correction, no verification-level claim that failed to confirm). |

Digest regenerated: **NO** (no new entry this cycle; `logs/known-failure-modes.md` already
reflects `IMP-0590` as of the 2026-09-03 generation cited at its own header).
