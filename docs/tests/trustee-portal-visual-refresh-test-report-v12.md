# Test Report — Trustee Portal Visual Refresh (v12)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260903-2/`
**Date:** 2026-09-03
**Status:** PASS (source/V2, gated for pipeline) — **with one residual explicitly NOT closed**

**Scope of this cycle:** this artifact packages two increments over the last-tested tree:
Revision 0.18 (`dev.verification[5]` made executable via `provisioning/dataverse/verify-solution-components.ps1`,
`wbs:6.8`) and Revision 1.10 (the third fix attempt at the round-statistics category-axis label
overlap, `AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY` in
[`RoundStatisticsCharts.tsx`](../../src/code-apps/trustee-review-portal/src/components/RoundStatisticsCharts.tsx#L330-L338),
`wbs:6.8`). Every earlier revision's own gate chain and assumption register are inherited, not
re-litigated here except where this cycle's own re-runs found something to say about them.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | `npx vitest run` (`src/code-apps/trustee-review-portal`) | 771 | 0 | 0 |
| Integration | Pester (`Invoke-Pester src/tests/provisioning/VerifySolutionComponents.Tests.ps1`) | 5 | 0 | 0 |
| End-to-End | — (source-only artifact; not yet pushed) | — | — | — |
| Regression | Full local gate chain re-run directly this cycle (below) | 6/6 gates | 0 | 0 |
| Security | No new auth/input surface this revision | N/A | N/A | N/A |
| Accessibility | No WCAG-relevant markup change this revision (arithmetic-only chart fix) | N/A | N/A | N/A |
| Performance | Not in scope this revision | — | — | — |
| Provisioning | `verify-solution-root-components.py` default + `--emit-json`, `verify-pipeline-config.py` | 3/3 | 0 | 0 |
| Compliance | No special-category surface touched this revision | N/A | N/A | N/A |
| **Total** | | **785** | **0** | **0** |

Independently re-run by test-agent this cycle (not taken on build-agent's/development-agent's own
report, per `IMP-0364`):

```
npx vitest run  → 39 files, 771/771 passed
python3 scripts/verify-improvement-log.py         → OK (schema), 586 entries
python3 scripts/verify-improvement-log.py --check → OK (schema + triggers), rc=0, 14 warnings (none new/blocking)
python3 scripts/verify-css-arithmetic.py          → PASS, 5 stylesheets, ambient body 17px
python3 scripts/verify-assumption-markers.py      → PASS, 19 OPEN rows, all marked, 46 total
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml → PASS, 72 steps, 57 gates
```

All figures match the Dev Summary's own claims exactly — no drift found between what was reported
and what re-running the same commands produces.

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-058/059/060 (round statistics, category-axis charts) | `CategoryBarChart`/`WellbeingComparisonChart` render wrapped category labels without overlapping the plot area | `RoundStatisticsCharts.test.tsx` (self-consistency: tick `dy` vs. `CATEGORY_AXIS_HEIGHT`) | **PASS (source-consistency only) — see §7.2, not a visual confirmation** |
| WBS 6.8 deliverable — `dev.verification[5]` component-completeness | New live-verification script exists, is correct against fixtures, and is wired into the pipeline config | `VerifySolutionComponents.Tests.ps1` (5/5), `verify-pipeline-config.py` | PASS (V2 — behavioural against a fixture; **live DEV run not yet performed**, see §7.1/§8) |

## 3. Failed Tests

None.

## 4. Defects Raised

None new. One pre-existing residual carried forward — see §7.1/§7.2 and Findings Logged.

## 5. Constraint & Compliance Verification

See §7's `CONSTRAINT CHECK` block below (per `skills/how-to-apply-constraints.md`). No HARD
violation and no HARD `UNEVALUABLE` row found in test-agent's scope (30 technology rows, 7 domain
rows). One SOFT technology row (`C-TECH-067`) carries an already-accepted, already-triaged warning
(11 fragile literal counts across Pester files — `docs/development/trustee-portal-visual-refresh-dev-summary.md#L2631`,
manifest `warnings_detail`), unchanged by this revision.

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `dev.verification[5]` — component-type completeness | `provisioning/dataverse/verify-solution-components.ps1 -Env dev` exits 0 against live DEV, closing the gap `IMP-0013` first recorded | `pwsh` run against DEV | **NOT PERFORMED — no `PROVISION_APP_ID`/`PROVISION_CERT_THUMBPRINT` in this session** (confirmed absent, not merely untried — Dev Summary §0.18 row, `logs/pipeline.log`). This is a pipeline-stage V3 concern per the dispatch brief, not re-litigated here; flagged so it is not silently dropped between agents |
| `verify-solution-components.ps1` behavioural correctness against a fixture | 5/5 Pester tests pass, including the FAILing/NAMED savedquery and missing-attribute fixtures | `Invoke-Pester src/tests/provisioning/VerifySolutionComponents.Tests.ps1` | PASS (V2 only — fixture, never a real environment) |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

The register (Dev Summary §10) carries 46 rows total, 19 OPEN, all with a live source marker
(confirmed by `verify-assumption-markers.py`, re-run directly this cycle). None of the 19 OPEN
rows names a closing precondition that an environment now open could satisfy and has not been
re-checked — each was individually re-verified live against DEV as recently as Revision 1.4
(2026-08-30) and the stated blockers (designer-save not yet performed, no signed-in trustee
session, a still-unanswered reviewer question) are unchanged by this revision, which adds only
two new rows:

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| `A-VSC-1` | The Web API existence check for a `sitemap` component (via its parent `AppModule`'s `uniquename`) is a valid stand-in for a direct sitemap check | OPEN | A live run of the new script against DEV | **No** — no credential in this session (see §6) | Re-confirmed: no such run has occurred; source-level reasoning (E3) is unchanged | Correctly OPEN |
| `A-VSC-2` | Every `Entities/` folder keeps declaring `behavior="0"` so the derived `systemform`/`savedquery` target list stays complete as the solution grows | OPEN | A future entity's `RootComponent` line carrying `behavior="1"` | N/A — a future-state precondition | Re-confirmed current state: `grep` shows all 13 `type="1"` `RootComponent` lines carry `behavior="0"` today | Correctly OPEN |

No orphan hand-authored artefact was found without a register row (`C-TECH-052`).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `provisioning/dataverse/verify-solution-components.ps1` | V2 — behavioural, against a fixture, never a real environment | **Confirmed V2**, independently re-run | `Invoke-Pester src/tests/provisioning/VerifySolutionComponents.Tests.ps1` → 5/5 PASS, this session | PASS at the claimed level |
| `scripts/verify-solution-root-components.py --emit-json` | V2, source-only | **Confirmed V2** | Re-run against real solution + 2 fixture variants | PASS at the claimed level |
| Whole build artifact | V2 — packaged; layout accepted by the packer, content unverified (manifest) | **Confirmed V2** | Manifest, preflight PASS (72 steps/57 gates), constraint_check PASS | Accurately stated, not overclaimed |
| **`RoundStatisticsCharts.tsx`'s category-axis label gap** (`AXIS_LABEL_GAP`/`TICK_ASCENT_PX`/`FIRST_TICK_LINE_DY`) | Not claimed above V2/E4 by Dev Summary — correctly described as arithmetic self-consistency, not a rendered confirmation | **Confirmed at E4/V2 only, and NO HIGHER LEVEL IS CLAIMABLE FROM THIS SESSION.** `RoundStatisticsCharts.test.tsx` asserts `dy`/`CATEGORY_AXIS_HEIGHT` self-consistency and does **not** name `AXIS_LABEL_GAP`, `TICK_ASCENT_PX` or `FIRST_TICK_LINE_DY` anywhere (confirmed by direct grep this cycle) — the same gap test-agent's own prior finding [`IMP-0584`](../../logs/improvement-log.jsonl#L581) recorded against the previous build. jsdom computes no font-metric layout, so this cannot be closed by any vitest assertion, and this session has no browser/live credential to render the chart either. **This is the third attempt at the identical reviewer-reported symptom** (`IMP-0509`, `IMP-0577`, `IMP-0581` were each caught only by a human on a rendered screen after a green suite) | **NOT VERIFIED beyond source self-consistency. Carried forward, not resolved.** |

- Idempotency: `verify-solution-root-components.py` re-run produced byte-identical output before/after this change → **PASS**.
- V4 designer/editor open + save: **not performed** — this artifact has not been pushed to any environment (Dev Summary §0.18/§11, confirmed).
- Cross-OS (C-TECH-054): the new PowerShell script was authored and tested on macOS only this cycle; CI-runner-OS execution is a pipeline-stage concern, not yet run → **N/A this cycle, flagged for pipeline-agent**.
- Warnings triaged (C-TECH-055): manifest shows 79 total, 14 resolved, 65 accepted, **0 untriaged** → PASS.
- Diagnostic components removed (C-TECH-056): no diagnostic component was created in a live environment this revision (source-only) → PASS, N/A.

**Per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" test:** the V4 human
open-and-look step for the axis-label fix is genuinely not yet due — this artifact has not been
deployed. This is recorded as `deferred-to-pipeline`, **not** a violation and **not** a request to
the reviewer to do something impossible from here. What IS being said plainly: a clean local gate
chain is not evidence the visual defect is fixed, given the identical claim has been made and
disproved twice already on this same file. The next V4 step (pipeline/reviewer, on DEV deploy)
should look at this chart specifically before the item is closed.

## 8. Recommendations

1. **Pipeline-agent's V4 step must specifically re-examine the round-statistics category-axis
   label gap** on a real rendered screen before `IMP-0581`'s underlying symptom is treated as
   closed. Do not infer correctness from this cycle's green suite.
2. **A structural gap remains open, not a new one:** no build gate in this repository can assert
   SVG baseline/ascent arithmetic (`C-TECH-076` is explicitly scoped to CSS declarations — the
   Dev Summary itself notes `verify-css-arithmetic.py` does not cover this file's SVG `dy` values,
   [Dev Summary L3821-3823](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L3821)).
   `IMP-0584` (test-agent, prior cycle) already proposes broadening `C-TECH-076` to a symbolic
   check over named gap/ascent/descender constants; it is `NEW`/unread in the log as of this
   session (confirmed via `verify-improvement-log.py`) and is not re-logged here — see Findings
   Logged.
3. **`dev.verification[5]`'s live DEV run remains a pipeline-stage open item**, per the dispatch
   brief — not re-raised as a test-agent defect, since no credential was available in-session to
   attempt it (correctly deferred per `skills/how-to-verify-a-platform-contract.md` §3's harness-mode
   rule).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle re-confirmed `IMP-0584`'s residual still applies to the current build and found no new instance of it or any other class — a re-confirmation is not itself a new finding per `skills/how-to-log-an-improvement.md`'s triggers (no second attempt, no new contradiction, no new correction). `IMP-0584` stays `NEW`/unread and is carried forward, not restated. |

Digest regenerated: **NO** (no new entry this cycle; `logs/known-failure-modes.md` already reflects `IMP-0584` as of the 2026-09-03 generation cited at its own header).
