# Test Report — trustee-portal-visual-refresh (v7)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260831-5/
**Date:** 2026-08-31
**Status:** FAIL
**wbs:** 6.9

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | Pester (`src/tests/Invoke-Tests.ps1`) + Vitest | 1001 Pester + 689 Vitest = 1690 | 0 | 1 (Pester, pre-existing `verify-improvement-log --check` self-referential case) |
| Integration | Pester provisioning + Code App repository/schema suites | included above | 0 | 0 |
| End-to-End | none this cycle — no signed-in session available | 0 | — | all (no V4/V5 credential) |
| Regression | full suite re-run this cycle | included above | 0 | 0 |
| Security | disclosure-control source checks (below) | source-level only | 0 | live column-security-membership read |
| Accessibility | `verify-css-line-height.py` (C-TECH-076) re-run this cycle | PASS, 0 findings | 0 | screenshot-level (A-DS-1, `<dt>`/`<dd>` render) |
| Performance | n/a — no NFR threshold in scope for this revision | — | — | — |
| Provisioning | `verify-pipeline-config.py`, `verify-provisioning-step-convergence.py` (source-level, per Dev Summary §11) | PASS | 0 | live post-deploy queries (not yet re-run against this build) |
| Compliance | domain-invariants, C-DOM-030/031/032 (source-level) | PASS | 0 | — |
| **Total** | | 1690 (source-level) | **0 (source-level)** | **2 blocking gaps at V4/V5 — see §7** |

**The FAIL verdict is not driven by a red test.** Every automated gate this cycle re-ran is green — the artifact's own [manifest](../../build/artifacts/trustee-portal-visual-refresh-20260831-5/manifest.json) records `constraint_check: PASS`, `preflight: PASS — 70 steps, 55 gates`, hosted Solution Checker `0 Critical/High/Medium/Low/Informational` ([solution-checker log](../../build/artifacts/trustee-portal-visual-refresh-20260831-5/solution-checker/pac-solution-check-stdout.log)). The FAIL is a **Verification Level / disclosure-safe-default** finding under §7 — the same shape [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) and this agent's own Fail Conditions exist to catch precisely because a green suite does not see it.

## 2. Requirement Coverage

| FR/Item | Requirement | Test Case(s) | Result |
|---|---|---|---|
| ADR-040/041/042 (nav bar, grid width, header padding, subheading, self-hosted font) | Redesign per TAD Revision 7 | `npx vitest run` 689/689 across 38 files, `npx vite build` clean ([Dev Summary §11, Revision 1.5](../development/trustee-portal-visual-refresh-dev-summary.md#L2332)) | PASS (V2 — source-level only, no V4 signed-in confirmation) |
| Container-query stat-tile shrink (`A-R54`) | Tile renders without overflow at narrow column counts | Static-harness Playwright/Chromium render, not the Code App's own WebView2 host ([Dev Summary §11](../development/trustee-portal-visual-refresh-dev-summary.md#L2338)) | PASS at V4-equivalent (real Chromium); **NOT V4 against the actual host** |
| IMP-0509 — stat-tile value overflow/line-height fix | Wrapped currency values do not overlap | `verify-css-line-height.py` re-run this cycle: PASS, 0 findings across 5 stylesheets, ambient body 17px | PASS at source level (V1/V2). **NOT V4** — no rendered screenshot exists anywhere in this repository (see §7.2) |
| IMP-0514 — `rev_setting.rev_description` MaxLength correction | Entity.xml MaxLength matches live DEV (2000) | `pipeline.log:42` records the live `pac solution export`/unpack confirming live MaxLength=2000 matches the corrected Entity.xml | PASS (E1, live-confirmed 2026-08-30) |
| IMP-0511 — round-statistics freshness fail-safe | A trustee sees a computed figure under the shipping (unseeded) `staleAfterSeconds` default | **No test reaches this outcome.** `RoundStatisticsStaleAfterSeconds=300` is seeded in three settings-file JSONs but has not been deployed to DEV or observed by a human (see §7.3) | **FAIL** — this is the Fail Condition [test-agent.md:109](../../agents/test-agent.md#L109) names by id |
| A-FLOW-01/03/04/05/06/11/13 — round-statistics flow trigger/expressions | Flow accepted, opens/saves in designer, fires on a real trigger | No newer live evidence than [Dev Summary Revision 1.4](../development/trustee-portal-visual-refresh-dev-summary.md#L2213) (2026-08-30); `logs/pipeline.log` has zero entries after 2026-08-30 22:05 confirming nothing has changed live since | **FAIL** at V4 (designer open-and-save not performed) — see §7.2 |
| A-FLOW-09 (applications-per-day denominator convention) | — | Deliberately parked for next release; SDD Amendment A-06 records the corrected definition, shipped flow still uses the old per-round convention | **Accepted deferral, not a defect** — per reviewer instruction to this test cycle and [Dev Summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L2147) |
| A-DS-1 (muted/quiet visual distinguishability) | A sighted trustee reads the two states as distinct | No mechanism to verify from this session; no V4 session recorded | OPEN — carried forward, not newly failed |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-1 | Platform Contract / Fail-safe default | The `staleAfterSeconds` fail-safe under the shipped/unseeded default reaches the approved user-visible outcome | A trustee sees a computed figure once the flow completes | No test or live observation exists confirming this; `isCurrent()`'s `NaN` comparison meant the app **never** showed a result under the null default ([IMP-0511](../../logs/improvement-log.jsonl#L508)); the seeded fix (300s) is source-only, not deployed | P1 (blocker) |
| T-2 | Verification Level (C-TECH-053) | `REV \| Portal \| Round Statistics` flow reaches V4 (designer open-and-save) before being reported deployed | Human opens flow in designer, saves without validation error | Not performed — `callbackregistration.createdon` unchanged since 2026-08-27 18:22 across every live check to date, most recently [Dev Summary Revision 1.4](../development/trustee-portal-visual-refresh-dev-summary.md#L2223) | P1 |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| IMP-0511 (pre-existing, blocker, carried) | P1 | Round-statistics freshness fail-safe never shows a computed result under its shipped default; fix seeded in config, not deployed/observed | T-1 |
| A-FLOW-03/06/11/13 (pre-existing, OPEN, carried) | P2 (Verification Level) | Flow's V4 designer-save step still not performed; no OBSERVED-EFFECT evidence admissible under [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) exists for this flow | T-2 |
| IMP-0523 (new, this cycle, friction) | P3 | `verify-css-line-height.py` crashes (unhandled `TypeError`) when given an explicit path argument its own `--help` documents; build invokes it bare so this does not affect the build | — |
| IMP-0524 (new, this cycle, friction) | P3 | IMP-0509's own `deferred_reason` states `.panelHeading`/`.cardTitle` are still line-height-defective; re-running the same gate against this artifact's `source_commit` (6ae5bf6) shows 0 findings — the note is stale, corrected here | — |

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform contract has a §10 register row | PASS | `verify-assumption-markers.py` reported PASS in the Dev Summary's own last run; no orphan found this cycle |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Component reported only at the verification level executed; V4 named with an owner | **FAIL** | Round-statistics flow reported only as far as V3 (accepted/imported); V4 designer-save not performed by anyone named. See §7.2 |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Every tool warning triaged in **this** feature's Dev Summary | PASS | Manifest `warnings: {total:6, resolved:6, untriaged:0}`; each row cites `docs/development/trustee-portal-visual-refresh-dev-summary.md#Lnnn` per the 2026-08-30 amendment |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed, creation/removal recorded | PASS | [Dev Summary §11](../development/trustee-portal-visual-refresh-dev-summary.md#L2376) — two temp local files (`tmp_verify_harness.html`, `tmp_verify.mjs`), both confirmed removed |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | An OPEN §10 assumption blocking deploy requires an explicit reviewer `OVERRIDE` with reason | PASS | [`pipeline.log:41`](../../logs/pipeline.log) records the 2026-08-30 21:23 override naming all 8 rows and the reviewer's reason; the 8 rows are correctly still carried OPEN, not silently closed |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No shipped text exceeds its schema-declared length limit | PASS | `verify-field-length-limits.py` clean this build; IMP-0514's live MaxLength correction closed the one prior drift |
| [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) | Improvement-log queue clear of unread blockers, under batch trigger | PASS | `python3 scripts/verify-improvement-log.py --check` run this cycle (after appending IMP-0523/0524): exit 0, 3 unread (non-blocker), 105 reviewer-deferred, 0 awaiting-approval |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state solution source cannot express is verified LIVE; metadata-only evidence inadmissible for a cloud-flow trigger; disclosure-control settings rows read back live | **FAIL** (for the round-statistics flow and the `staleAfterSeconds`/`k=5` disclosure controls) | No OBSERVED-EFFECT run exists for the flow; `RoundStatisticsStaleAfterSeconds`/`k=5` not yet confirmed read back from DEV post-deploy for this build |
| [C-DOM-030/031/032](../../constraints/domain/domain-constraints.md#L92) | Special-category columns excluded from scoring; secured + audited | PASS | `domain-invariants` build step PASS (source-level); no change to the special-category register this revision |

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundfinance` table + attributes + auditing | Exists live, `IsAuditEnabled=true` | Live GET, confirmed in [Dev Summary §11](../development/trustee-portal-visual-refresh-dev-summary.md#L2274) (2026-08-26/29 reads — not re-queried this cycle, no live credential in this session) | PASS (carried, not re-verified live this cycle) |
| `rev_roundstatisticsresult` table | Exists live, `A-RESULT-1`/`A-FLOW-07`/`A-RES-1` closed | [`pipeline.log`](../development/trustee-portal-visual-refresh-dev-summary.md#L2185) 2026-08-29 live echo, matching independent `EntityDefinitions` read | PASS (carried) |
| `RoundStatisticsStaleAfterSeconds`/`k=5` disclosure controls | Non-empty `rev_value` rows read back from the environment just deployed to | **Not performed for this build.** No `pipeline.log` entry after 2026-08-30 22:05; no deploy of build `-5` to DEV has occurred yet | **NOT VERIFIED** — [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) names this pipeline-agent's `post_deploy` obligation, owed at the next deploy, not skippable |
| Round-statistics flow trigger (Dataverse row-trigger redesign) | Designer-saved (V4), OBSERVED-EFFECT proof | Not performed; `callbackregistration.createdon` unchanged since 2026-08-27 18:22 | **NOT VERIFIED** |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Nine rows remain OPEN in [Dev Summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L2066), each re-verified against DEV live state by the Dev Summary's own Revision 1.4 pass (2026-08-30) rather than accepted from an older narrative — the exact discipline [IMP-0219](../../logs/known-failure-modes.md) requires. This test cycle found **no newer live evidence** to update any of them against: `logs/pipeline.log` carries zero entries for this feature after 2026-08-30 22:05, and this session holds no live Dataverse credential, so the closing-precondition table below is Revision 1.4's own re-measurement, checked for staleness against the log rather than re-derived from prose.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-FLOW-03/06/11/13 | Flow expression/trigger contracts (`Secure Outputs`, `$expand`, `xpath` sum, `result()` on Switch/If) | OPEN | Designer open-and-save (V4), then an OBSERVED-EFFECT run | No — `callbackregistration` unchanged since 2026-08-27 | Confirmed no newer log entry exists; not independently re-queried (no credential) | OPEN, correctly |
| A-LAND-3/A-LAND-4 | FR-062 proportions / FR-060 total-row shape | OPEN | A real (flow-produced, not seeded) populated response | No — only seed-data population observed, predating the trigger write ([Dev Summary Revision 1.4](../development/trustee-portal-visual-refresh-dev-summary.md#L2232)) | Confirmed the seed-vs-flow distinction is stated correctly | OPEN, correctly |
| A-TR-13 | `rev_careprovidedtype` wire shape | OPEN | A populated live row to read | No — zero populated rows exist in DEV for this column at all | Confirmed via Dev Summary's own live query citation | OPEN, correctly |
| A-FIN-03 | Decimal control classid renders as numeric editor | OPEN | Human opens the `rev_roundfinance` form | Form is live and accepted; human step not recorded in either log | OPEN, correctly |
| A-DS-1 | Muted/quiet visual states are distinguishable to a sighted trustee | OPEN | One signed-in V4 session | No mechanism in this session | OPEN, correctly |
| A-FLOW-09 | Applications-per-day denominator convention | OPEN, deliberately parked | Reviewer/Emily answer | Not yet asked again | **Excluded from this cycle's FAIL reasoning per explicit reviewer instruction** — SDD Amendment A-06 already records the corrected definition; shipping the old convention is a tracked deferral, not a new defect |

**No orphans found.** `verify-assumption-markers.py`'s last recorded run (Dev Summary §9) reports every OPEN row's marker present in source.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| ADR-040/041/042 redesign (nav/grid/padding/subheading/font) | V2 | V2 confirmed | Manifest `verification_level: V2`, 689/689 tests, clean build | PASS at claimed level |
| Container-query stat-tile clamp | V4-equivalent (real Chromium), not V4 against host | Confirmed as stated — not overclaimed | [Dev Summary §11](../development/trustee-portal-visual-refresh-dev-summary.md#L2338) explicitly distinguishes the two | PASS at claimed level |
| IMP-0509 line-height fix | V2, explicitly **not** V4 | V2 confirmed, gate re-run this cycle: PASS, 0 findings (correcting the stale two-rule note — see IMP-0524) | Source-level only; no screenshot exists anywhere in this repository | PASS at claimed level (V4 remains the honest open gap, unchanged) |
| Round-statistics flow (trigger, `Secure Outputs`, `$expand`, xpath sum) | V2 (packaged, checked) | **V3 only** (accepted/imported live, per 2026-08-27 21:01 pipeline entry) — **not V4** | No designer-save event in either log since import | **FAIL at claimed vs. confirmed level** |
| `RoundStatisticsStaleAfterSeconds` fail-safe default | Not separately leveled in §11; treated as a safe default in TAD prose | **No level reached for the outcome that matters** — the shipping/unseeded default has never been shown to reach the approved user-visible result, and the seeded fix is source-only | [IMP-0511](../../logs/improvement-log.jsonl#L508) deferred_reason, re-checked this cycle: config seeded, DEV deploy and human observation both still outstanding | **FAIL — this is the exact case [test-agent.md:108-111](../../agents/test-agent.md#L108) names** |

- Idempotency: deploy re-run against an already-deployed target → `PASS` (Dev Summary §11 records paired import runs, most recently 2026-08-26/29, each re-run clean)
- V4 designer/editor open + save, performed by `<no one — not yet performed>` on `<n/a>` → **FAIL**
- Cross-OS (C-TECH-054): `N/A` — no CI-runner-specific script introduced this revision
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → `PASS`

### 7.3 The `IMP-0511` fail-safe default, checked against this test-agent's own Fail Condition

[test-agent.md:108-111](../../agents/test-agent.md#L108) names IMP-0511 by id as the worked example of *"a configuration default the TAD declares fail-safe has no test reaching a SUCCESS outcome under that exact default."* Re-checked, not assumed, this cycle:

- **Source-side fix exists:** `RoundStatisticsStaleAfterSeconds = 300` is seeded in `dev-scoring-settings.json`, `test-settings.json`, `prd-settings.json` ([IMP-0511 deferred_reason](../../logs/improvement-log.jsonl#L508)).
- **Not deployed:** `logs/pipeline.log` shows no deploy of any build since 2026-08-30 22:05; build `-5` (this artifact) has not been pushed to DEV.
- **Not observed:** no `revisit_when` (*"seed RoundStatisticsStaleAfterSeconds in DEV, open the trustee portal landing screen, and record whether a computed figure appears"*) has been carried out.
- **No test asserts the SUCCESS outcome at all**, seeded or unseeded — the deferred_reason itself says unit tests "presumably mock the timing/staleness math directly," and this cycle found no `roundStatistics.test.ts`-shaped assertion exercising the real write-then-poll cycle end to end.

This is not a stale carry-forward: this is the **live, current** state of the one item this agent's own Fail Conditions name explicitly, and it remains open. **FAIL** stands on this basis alone, independent of the flow-trigger V4 gap in §7.2.

## 8. Recommendations

1. **Do not deploy build `-5` to DEV as a basis for declaring the round-statistics feature working.** Deploy is fine under the standing [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) override, but the Deployment Summary must name the `staleAfterSeconds` gap and the flow's V4 gap as known-broken surfaces per the 2026-08-23 amendment to [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) — a green build does not mean the screen works.
2. Pipeline-agent's next deploy should perform, in order: deploy → seed/confirm `RoundStatisticsStaleAfterSeconds=300` live → the `post_deploy` disclosure-control read-back [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) requires for both `staleAfterSeconds` and `k=5` → hand the reviewer the private/incognito V4 open-and-observe step for both the landing screen and the flow designer.
3. architect-agent's still-open durable question (whether `fetchRoundStatistics`'s poll loop should carry its own current-document test independent of `isCurrent()`) remains unresolved and is a better long-term fix than relying on the seeded value alone — a clock-skew or slow-poll edge case can still reproduce IMP-0511's symptom even at 300s.
4. Fix the two friction-level findings (IMP-0523, IMP-0524) at convenience; neither blocks this feature.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0523 | `hand-authored-tool-crashes-on-documented-argument` | friction | Exercise every branch a script's own `--help` documents, not only the one the build config happens to invoke. |
| IMP-0524 | `stale-claim-contradicting-rechecked-source` | friction | Re-run a cited gate against the artifact's own `source_commit` before repeating a `deferred_reason`'s figures — they are a snapshot, not a live fact. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (521 entries, 519 distinct lessons)
