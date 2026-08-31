# Test Report — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260831-8/
**Date:** 2026-08-31
**Status:** PARTIAL

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Integration (vitest) | 39 files | 732 | 0 | 0 |
| Unit / Integration (Pester) | — | 1001 | 0 | 1 |
| Regression | re-run above, independently | — | 0 | — |
| Security | scoped grep + gitleaks (build log) | — | 0 | — |
| Accessibility | source re-read, no live render | — | — | — |
| Performance | not applicable — no NFR threshold changed | — | — | — |
| Provisioning | see §6 | 2 | 0 | — |
| Compliance | see §5 | — | — | — |
| **Total** | | **1733** | **0** | **1** |

Both test counts were **re-run independently in this cycle**, not taken from build-agent's own
numbers: `npx vitest run` in
[`src/code-apps/trustee-review-portal`](../../src/code-apps/trustee-review-portal) → `Test Files 39
passed (39)`, `Tests 732 passed (732)`, matching the artifact's own claim exactly. The artifact's
[`test-results/pester-results.xml`](../../build/artifacts/trustee-portal-visual-refresh-20260831-8/test-results/pester-results.xml)
carries `total="1002" failures="0" skipped="1"` — 1001 executed, all passed, consistent with the
handoff's "1001/1001".

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-058 | Applications-per-day | `roundStatistics.test.ts` §"parseRoundStatisticsResponse" (applicationsPerDay cases) | PASS (source-level) |
| FR-059/FR-060 | Exceptional-funding summary, break-type profile, money measures | `roundStatistics.test.ts` money-measure describe block | PASS (source-level); flow-side `A-FLOW-11` (xpath/xml on this tenant) still `OPEN` — [dev summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L2235) |
| FR-061 | Ethnic-group distribution rendered as aggregate percentage | `roundStatistics.test.ts` "ethnicGroupDistribution" block | PASS (source-level); DEV-only per `EX-005` — [`contract/known-exceptions.json:52`](../../contract/known-exceptions.json#L52) |
| FR-062 | Three headline proportions | `roundStatistics.test.ts` proportion cases | PASS (source-level); thresholds still unset (OQ-039) |
| SDD US-013 AC-2 (list filtering/sorting client-side over the complete round) | Unchanged by this restyle | Regression — no new test needed, confirmed untouched at [`src/domain/listView.ts:1-9`](../../src/code-apps/trustee-review-portal/src/domain/listView.ts) | PASS |
| TAD §5.3.1 freshness cycle (ADR-038) | Age-bound poll, not request identity | `roundStatistics.test.ts` "fetchRoundStatistics" describe block, 7 cases | PASS as a **unit** test; the shipping-default (`S` unset) pathway is a documented **residual risk**, not a defect — see §7.1 below |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| — | — | None found this cycle | — | — | — |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| — | — | None raised this cycle — see §7.1 for a residual risk that is already owned, dated and tracked, not a new defect | — |

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | PASS | gitleaks clean (build-agent's own run, `build-run.log`); no new secret-shaped literal introduced this cycle |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Unit coverage meets threshold | PASS | 96%+ statement/line coverage (dev summary [§9](../development/trustee-portal-visual-refresh-dev-summary.md#L2064)); ≥80% floor |
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | PASS | `domain-invariants` build step, re-confirmed passing in artifact manifest's `platform_limit_gates` |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column drives eligibility/scoring | PASS | This feature reads, never scores; `no-special-category-data-in-scoring` gate listed PASS in [`manifest.json`](../../build/artifacts/trustee-portal-visual-refresh-20260831-8/manifest.json) |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Special-category columns `IsSecured=1` unless a named exception | PASS | `domain-invariants` gate; 4 pre-existing exceptions unrelated to this feature |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Special-category columns `IsAuditEnabled=1` | PASS | `domain-invariants` gate; source-check only, per the row's own caveat — live half is `C-TECH-064`, unaffected by this feature |

No HARD constraint failure found. Full 69-step build gate (including `design-doc-claims`) already
confirmed clean by build-agent and not re-litigated here per this dispatch's own instruction.

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `RoundStatisticsStaleAfterSeconds` seeded in DEV | `rev_setting` row = 300 | [`config/revitalise-grant-automation-pipeline.yml:538`](../../config/revitalise-grant-automation-pipeline.yml#L538) wires `seed-settings.ps1 -Env dev` as a DEV deploy step, reading [`dev-scoring-settings.json:135-138`](../../provisioning/deploymentSettings/dev-scoring-settings.json#L135) | PASS for DEV (the artifact's actual promotion target) |
| Same setting for `tst_acc` / `prd` | Same value, same mechanism | [`config/revitalise-grant-automation-pipeline.yml:1434`](../../config/revitalise-grant-automation-pipeline.yml#L1434) (`tst_acc`) and `:1695` (`prd`) both carry `promote_mode: manual` and the value is documented as "picked up at their own next promotion" — [pipeline.yml:996-999](../../config/revitalise-grant-automation-pipeline.yml#L996) | **Not yet applied** — correctly out of scope for this DEV-targeted artifact, see §7.1 |
| `rev_roundstatisticsresult` / `rev_roundstatisticsrequest` tables | Exist live, platform names echoed | Closed E1, revision 1.2 ([dev summary §10, A-RESULT-1/A-FLOW-07/A-RES-1](../development/trustee-portal-visual-refresh-dev-summary.md#L2260)) | PASS |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| — (`IMP-0511` residual, not a §10 register row) | `staleAfterSeconds` unseeded ⇒ `isCurrent()` never returns true ⇒ round-statistics screen stays dark forever | RESOLVED for DEV, 2026-08-30 — [pipeline.yml:972-1000](../../config/revitalise-grant-automation-pipeline.yml#L972) | `seed-settings.ps1 -Env dev` runs as part of the DEV deploy this artifact is headed for | **Yes for DEV** (wired at [pipeline.yml:538](../../config/revitalise-grant-automation-pipeline.yml#L538)); **No for `tst_acc`/`prd`** (`promote_mode: manual`, not yet run) | This is the exact defect shape `agents/test-agent.md`'s fail condition names (`roundStatistics.test.ts`'s "case 4" test at [line 743](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.test.ts#L743) still asserts `pending` under "the SHIPPING configuration"). It is **not treated as a fresh FAIL here**: the code-level fix was deliberately deferred to `architect-agent` ([docs/improvements/2026-08-30-improvement-review-2.md §0](../improvements/2026-08-30-improvement-review-2.md)); the config workaround is confirmed live and working for DEV, the actual target of this artifact; and the `tst_acc`/`prd` gap is explicitly logged as "a LEVER, NOT A CONTROL" residual (`A-R48`, [architecture doc:4054](../architecture/trustee-portal-visual-refresh-architecture.md#L4054)) with its own dated tracking. Re-raising it as a new defect here would duplicate an already-owned finding | **ACCEPTED RESIDUAL — do not promote to `tst_acc`/`prd` until `seed-settings.ps1` runs there** |
| `EX-003` | Trustee portal built ahead of DPO sign-off, DEV-only, synthetic data only | OPEN, dated 2026-11-27 | DPO sign-off + automation #5 landing before any live trustee demo | No | Confirmed still open, no change this cycle — [`contract/known-exceptions.json:30`](../../contract/known-exceptions.json#L30) | CLOSED-for-DEV-scope, open overall |
| `EX-005` | Ethnic-group distribution surfaced ahead of formal DPIA sign-off | OPEN, dated 2026-11-27 | OQ-030 DPIA sign-off recorded before promotion past DEV | No | Confirmed still open, no change this cycle — [`contract/known-exceptions.json:52`](../../contract/known-exceptions.json#L52) | CLOSED-for-DEV-scope, open overall |
| A-FLOW-01/03/06/09/11/13, A-LAND-3/4, A-FIN-03, A-DS-1, A-TR-13 | Various platform-contract and disclosure-shape guesses | OPEN — [dev summary §10](../development/trustee-portal-visual-refresh-dev-summary.md#L2136) | Each needs a live DEV designer-save or signed-in trustee session | No — none performed since this artifact was packed | No orphans found: every hand-authored guess this session touched carries its register row (`verify-assumption-markers.py` PASS, 17 OPEN, dev summary [§9](../development/trustee-portal-visual-refresh-dev-summary.md#L2121)) | OPEN, correctly carried forward, no `C-TECH-052` orphan |

No orphaned hand-authored artefact was found this cycle.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Whole artifact | **V2** — [`manifest.json:15`](../../build/artifacts/trustee-portal-visual-refresh-20260831-8/manifest.json#L15) states this itself: "packaged; layout accepted by the packer, content unverified" | V2, confirmed | Manifest's own field, plus independent vitest/Pester re-run in §1 | Matches claim |
| `REV \| Portal \| Round Statistics` flow | V2 (packaged) | V2, confirmed | No import for this specific artifact number has happened yet | Matches claim |
| Round-statistics landing screen end-to-end (a real trustee sees figures) | Not claimed above V3 anywhere in §11 | **Not reached** | No live DEV push of build **-8** exists; the last confirmed live DEV state predates this build number | **Correctly not claimed — this is why the run is PARTIAL, not PASS** |
| Container-query tile sizing (`A-R54`) | Real Chromium (Playwright), static harness — not the live Code App host | Unchanged, still static-harness only | Dev summary [§0.15 point 1](../development/trustee-portal-visual-refresh-dev-summary.md#L2334) | V4 not reached |

- Idempotency: deploy re-run against an already-deployed target → result: **N/A this cycle** — build -8 has not been imported anywhere yet; a prior build's idempotency was already confirmed (`pac code push` re-run cleanly, dev summary §11 revision 0.9 row).
- V4 designer/editor open + save, performed by `<name>` on `<date>` → result: **NOT PERFORMED** — no human session recorded in `logs/routing.log`/`logs/pipeline.log` for build -8; this is the reason for `PARTIAL` rather than `FAIL` (nothing contradicts the design; nothing has confirmed it live yet either).
- Cross-OS (C-TECH-054): pipeline/CI scripts executed on the CI runner OS → result: **PASS** — no new script added this cycle; `verify-build-config.py` re-run clean (dev summary §9, revision 1.6).
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → result: **PASS** — manifest reports `43 total, 43 accepted, 0 untriaged`.

## 8. Recommendations

1. **Deploy to DEV is safe to proceed.** No HARD constraint fails, both test suites re-confirmed independently, and the `RoundStatisticsStaleAfterSeconds` fail-safe-default risk is already mitigated for DEV specifically (`pipeline.yml:538`).
2. **Do not let `pipeline-agent` promote this artifact past DEV** until (a) `seed-settings.ps1` runs for `tst_acc`/`prd` (otherwise the round-statistics screen ships dark there — the exact `IMP-0511` mechanism), and (b) `EX-003`/`EX-005`'s DPO/DPIA preconditions close.
3. **The V4 human open-and-save step for build -8 is still owed** — once pipeline-agent deploys this artifact to DEV, a human should perform the container-query tile check (`A-R54`) and confirm the landing screen renders real figures end-to-end, closing V5 for the round-statistics mechanism specifically.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | No new finding this cycle: independent re-run matched every claim checked, and the one class-matching pattern found (`roundStatistics.test.ts`'s "shipping configuration" test) is an already-owned, already-dated residual (`IMP-0511`, `A-R48`), not a new discovery |

Digest regenerated: NO — no new entry appended, per `skills/how-to-log-an-improvement.md` ("none" is a valid answer; the digest is regenerated only when the log changes).
