# Test Report — trustee-portal-visual-refresh (v8)

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** build/artifacts/trustee-portal-visual-refresh-20260901-2/
**Date:** 2026-09-02
**Status:** FAIL
**wbs:** 6.9

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | Pester (`src/tests/Invoke-Tests.ps1`) + Vitest | 1001 Pester + 755 Vitest = 1756 | 0 | 1 (Pester, pre-existing `verify-improvement-log --check` self-referential case, unchanged) |
| Integration | Pester provisioning + Code App repository/schema suites | included above | 0 | 0 |
| End-to-End | none this cycle — no signed-in session available to this agent | 0 | — | all (no V4/V5 credential) |
| Regression | full suite re-run this cycle | included above | 0 | 0 |
| Security | disclosure-control source checks (below) | source-level only | 0 | live column-security-membership read for this build |
| Accessibility | data-table disclosure (item 1), `verify-css-arithmetic.py` (C-TECH-076, item 2) | PASS, 0 findings | 0 | screenshot-level (A-DS-1) |
| Performance | code-app-bundle-budget (new, review-10) | PASS — 1,204,716 / 77,221 bytes, matching the budget file | 0 | — |
| Provisioning | `verify-pipeline-config.py`, manifest `platform_limit_gates` | PASS | 0 | live post-deploy queries (not yet re-run against this exact build) |
| Compliance | `domain-invariants`, C-DOM-030/031/032 (source-level) | PASS | 0 | — |
| **Total** | | 1756 (source-level) | **0 (source-level)** | **2 blocking gaps at V4/V5 — see §7, unchanged in kind from Test Report v7** |

**The FAIL verdict is not driven by a red test, same as every prior cycle on this feature.** The artifact's own [manifest](../../build/artifacts/trustee-portal-visual-refresh-20260901-2/manifest.json) records `constraint_check: PASS`, `preflight: PASS — 72 steps, 57 gates`, `verification_level: "V2 — packaged"`, `warnings: {total:8, resolved:1, accepted:7, untriaged:0}`, hosted Solution Checker 0 findings all severities, Pester 1001/1002, Vitest 755/755, coverage 83.1% against the 80% floor. The FAIL is the same [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) Verification-Level finding Test Report v7 raised, re-checked rather than assumed carried forward, plus one new documentation-accuracy finding this cycle (§7.3).

## 2. Requirement Coverage

| FR/Item | Requirement | Test Case(s) | Result |
|---|---|---|---|
| Reviewer UI batch, second round, 6 items (nav-bar detail-button scoping, chart label sizing, filter-field height, button alignment, data-table disclosure, whitespace rhythm) — Dev Summary Revision 1.7 | Delivered per [Dev Summary §0.16](../development/trustee-portal-visual-refresh-dev-summary.md#L1497) | `npx vitest run` 755/755 across 39 files; new/rebased assertions in `DistributionChart.test.tsx`, `RoundStatisticsCharts.test.tsx`, `styles/layout.test.ts` (4 new describe blocks), `App.test.tsx`; `verify-css-arithmetic.py` (C-TECH-076) PASS | PASS at source level (V2). **NOT V4** — no signed-in trustee has viewed this build |
| Item 1 — data table disclosure (`.srOnly` + "Show the data table") | WCAG 1.1.1/1.3.1 text alternative preserved, not `<details>` (would remove from a11y tree) | `DistributionChart.test.tsx` asserts `aria-expanded`/`aria-controls`, table stays mounted | PASS at source level — jsdom computes no CSS, so visual hiding is asserted structurally, consistent with this feature's standing residual (A-R39/A-DS-1) |
| Item 5 — nav-bar third button scoped to detail view, reversing ADR-040 (`IMP-0510`) | Reviewer's explicit direction this round, superseding the prior round's persistent-three-button decision | `App.test.tsx` re-based assertions | PASS at source level. **TAD not yet amended** — Dev Summary §0.16 point 2 states this plainly; `architect-agent` has not been asked. Not a defect (transparently disclosed), but a live doc/code divergence — see §7.1 |
| Code-app-bundle-budget (`C-TECH-055`, `IMP-0573`, review-10) | Bundle magnitude gated mechanically | `verify-code-app-bundle-budget.py` — 1,204,716 bytes actual vs. budget, PASS | PASS, new gate this build cycle |
| IMP-0511 — round-statistics freshness fail-safe | A trustee sees a computed figure once the flow completes, under the actual deployed default | `RoundStatisticsStaleAfterSeconds=300` confirmed **live in DEV twice** since the fix ([`logs/pipeline.log:51`](../../logs/pipeline.log#L51), [`:61`](../../logs/pipeline.log#L61), both post-2026-08-30). Generic mechanism proven at any non-null bound: `roundStatistics.test.ts` case 3 (`staleAfterSeconds:120`) reaches `status:"ok"` | **Setting is live and correct. End-to-end path is currently broken for an unrelated reason** — see next row and §7.3 |
| A-FLOW-03/06/09/11/13 — round-statistics flow trigger/expressions | Flow accepted, opens/saves in designer, fires on a real trigger | [Deployment Summary](../deployments/trustee-portal-visual-refresh-deployment-summary.md#L51) records `callbackregistration.createdon` for `rev_roundstatisticsrequest` **STALE since 2026-08-27 18:22**, unmoved by the build-8 flow-definition replacement on 2026-08-31 — Dataverse cannot deliver a trigger event into a registration pinned to a superseded definition (IMP-0104/IMP-0114 mechanism). No designer open/turn-off/turn-on has been performed since | **FAIL** at V4 — the flow **cannot currently fire live**, independent of whether `staleAfterSeconds` is seeded correctly |
| A-LAND-3/A-LAND-4, A-TR-13, A-FIN-03, A-DS-1 | Various — see Dev Summary §10 | Unchanged this cycle; this build touches none of the code these rows describe | OPEN, carried forward unchanged, covered by the standing [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) OVERRIDE ([`pipeline.log:41`](../../logs/pipeline.log#L41)) |
| A-FLOW-09 (applications-per-day denominator convention) | — | Still unanswered; not re-asked this cycle, out of this UI-only revision's scope | **Accepted deferral, not a new defect** — same status as Test Report v7 |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-1 | Verification Level (C-TECH-053) / Provisioning | `REV \| Portal \| Round Statistics` flow trigger is registered against the definition currently live | A trustee action reaches the flow and a computed result appears | `callbackregistration.createdon` unchanged since 2026-08-27 18:22, across the 2026-08-31 build-8 redeploy that replaced the flow definition ([Deployment Summary L51](../deployments/trustee-portal-visual-refresh-deployment-summary.md#L51)); no designer open/turn-off/turn-on recorded since. The flow **cannot fire live** in its current registered state | P1 (blocker), carried forward — same defect class as Test Report v7's T-2, re-confirmed on newer evidence |
| T-2 | Platform Contract (C-TECH-052) | The TAD's OQ-042 rows describe the currently-shipping default accurately | OQ-042 rows state the reviewer's actual, live-confirmed decision (300, seeded 2026-08-30) | [Architecture doc L2831/L4106/L4303](../architecture/trustee-portal-visual-refresh-architecture.md#L4303) still states unseeded/null is "the approved," "safe" default; `roundStatistics.ts:499` and `roundStatistics.test.ts:743` both still label null "the shipping default." `IMP-0511`'s own `proposed_change` named this exact correction on 2026-08-30 and its `status` is still `NEW` | P3 (friction) — logged this cycle as `IMP-0575`, §7.3 |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| A-FLOW-03/06/09/11/13, A-LAND-3/4, A-TR-13 (pre-existing, OPEN, carried, covered by standing OVERRIDE) | P1 (Verification Level) | Flow's V4 designer-save step still not performed; the flow's own trigger registration is additionally now stale relative to the current definition | T-1 |
| IMP-0575 (new, this cycle, friction) | P3 | `roundStatistics.ts:499` and `roundStatistics.test.ts:743` both mislabel the pre-`IMP-0511`-fix `null` value as "the shipping default"; the TAD's OQ-042 rows carry the same stale claim, unremediated since 2026-08-30 despite `IMP-0511` naming this exact correction | T-2 |
| IMP-0510 (pre-existing, ADR-040 reversal, not a defect — transparently disclosed) | — | Dev Summary §0.16 point 2 states plainly that item 5 reverses ADR-040 without a matching TAD amendment yet | — |

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform contract has a §10 register row | PASS | `verify-assumption-markers.py` — Dev Summary §9 last run: PASS, 17 OPEN rows, all carrying source marker, 44 total, unchanged this revision (no new hand-authored contract; UI-only work) |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Component reported only at the verification level executed; V4 named with an owner | **FAIL** | Round-statistics flow reported V2 (packaged)/V3 (accepted) only, never overclaimed — Dev Summary §11 is honest about this. V4 designer-save not performed by anyone named; trigger registration additionally stale (see T-1) |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Every tool warning triaged in **this** feature's Dev Summary | PASS | Manifest `warnings: {total:8, resolved:1, accepted:7, untriaged:0}`; each row cites `docs/development/trustee-portal-visual-refresh-dev-summary.md#Lnnn`; bundle-magnitude half now mechanical (`code-app-bundle-budget`, PASS at 1,204,716/77,221 bytes) |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed, creation/removal recorded | PASS | No diagnostic component created this revision (UI/CSS only) |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | An OPEN §10 assumption blocking deploy requires an explicit reviewer `OVERRIDE` with reason | PASS (standing) | [`pipeline.log:41`](../../logs/pipeline.log#L41) — 2026-08-30 override naming all 8 rows still stands and was re-checked, none newly closed, none newly contradicted, this revision touches none of them |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | No shipped text exceeds its schema-declared length limit | PASS | `verify-field-length-limits.py` clean per manifest `preflight: PASS` |
| [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) | Improvement-log queue clear of unread blockers, under batch trigger | PASS | `python3 scripts/verify-improvement-log.py --check` run this cycle (after appending IMP-0575): exit 0, 12 unread (non-blocker), 119 reviewer-deferred, 0 awaiting-approval, well under the 30-entry threshold |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Disclosure-control settings rows read back live; Dataverse-trigger evidence must be an OBSERVED EFFECT, not metadata | **FAIL (flow), PASS (setting)** | `RoundStatisticsStaleAfterSeconds` confirmed live=300 twice post-fix (pipeline.log:51,:61) — the setting clause is discharged. The flow-trigger clause is explicitly **not**: metadata (`callbackregistration` existence/`createdon`) is inadmissible evidence per this constraint's own text, and it is all that exists for this trigger since 2026-08-27 |
| [C-DOM-030/031/032](../../constraints/domain/domain-constraints.md#L92) | Special-category columns excluded from scoring; secured + audited | PASS | `domain-invariants` build step PASS (source-level); no change to the special-category register this revision |

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundfinance` / `rev_roundstatisticsresult` tables + attributes + auditing | Exist live, `IsAuditEnabled=true` | Carried from prior cycles' live reads (2026-08-26/29); no live credential in this session to re-query | PASS (carried, not re-verified live this cycle — unchanged by a UI-only revision) |
| `RoundStatisticsStaleAfterSeconds` disclosure/tunable | Non-empty `rev_value` row read back from DEV | [`pipeline.log:51`](../../logs/pipeline.log#L51), [`:61`](../../logs/pipeline.log#L61) — `RoundStatisticsStaleAfterSeconds still 300` confirmed by live query, twice, post the 2026-08-30 fix | **PASS**, live-confirmed (this is the one row that changed status since Test Report v7) |
| Round-statistics flow trigger (Dataverse row-trigger) | Designer-saved (V4), OBSERVED-EFFECT proof, registration current | [Deployment Summary L51/L55](../deployments/trustee-portal-visual-refresh-deployment-summary.md#L51) — registration **stale since 2026-08-27**, unmoved by the 2026-08-31 flow-definition replacement; REVIEWER ACTION REQUIRED block names the exact designer steps, not yet performed | **FAIL — regressed since Test Report v7's baseline concern.** v7 found this OPEN; this cycle's own evidence shows the redeploy that happened since made it actively broken (a stale registration against a *replaced* definition, not merely an unconfirmed one) |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Unchanged this revision: this build is UI/CSS presentation work only (nav-bar visibility scoping, chart label
sizing, filter-field box-sizing, button-group gutters, data-table disclosure, spacing scale) against data and
controls the app already had. It touches none of the code or flow definitions the eight standing §10 rows
describe, so none moves. `verify-assumption-markers.py` — PASS, 17 OPEN, 44 total, unchanged.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-FLOW-03/06/09/11/13 | Flow expression/trigger contracts | OPEN | Designer open-and-save (V4), then an OBSERVED-EFFECT run | No — registration stale since 2026-08-27, unmoved by the 08-31 redeploy | Confirmed via Deployment Summary; not independently re-queried (no live credential this session) | OPEN, correctly, and the trigger is presently non-functional (§7.3 is a distinct, narrower finding) |
| A-LAND-3/A-LAND-4 | FR-062 proportions / FR-060 total-row shape | OPEN | A real (flow-produced) populated response | No — flow cannot currently fire to produce one | Unchanged | OPEN, correctly |
| A-TR-13 | `rev_careprovidedtype` wire shape | OPEN | A populated live row to read | No — zero populated rows in DEV | Unchanged | OPEN, correctly |
| A-FIN-03 | Decimal control classid renders as numeric editor | OPEN | Human opens the `rev_roundfinance` form | Form live; human step not recorded | Unchanged | OPEN, correctly |
| A-DS-1 | Muted/quiet visual states distinguishable | OPEN | One signed-in V4 session | No mechanism in this session | Unchanged | OPEN, correctly |
| A-FLOW-09 | Applications-per-day denominator convention | OPEN, deliberately parked | Reviewer/Emily answer | Not asked again this cycle | Excluded from FAIL reasoning, same as v7 |

**No orphans found.** `verify-assumption-markers.py`'s last recorded run reports every OPEN row's marker present in source.

**One item worth naming that is not a §10 row.** Dev Summary §0.16 point 2 states item 5 (nav-bar button scoping)
reverses ADR-040 at this round's explicit reviewer direction, and that `architect-agent` has not yet been asked
for a formal TAD amendment. This is disclosed, not hidden, and is not a defect — but it means the TAD's own text
now describes a control the shipped code does not have, a second (unrelated) live doc/code divergence alongside
§7.3's. Recommend closing it in the same TAD pass as §7.3's OQ-042 correction.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Reviewer UI batch, round 2 (6 items, §0.16) | V2 (source-level) | V2 confirmed, not overclaimed | 755/755 Vitest, `verify-css-arithmetic.py` PASS, `verify-code-app-bundle-budget.py` PASS | PASS at claimed level |
| Round-statistics flow (trigger, expressions) | V2 (packaged) | **V3 was reached 2026-08-31 (build-8), then regressed** — the same import that replaced the flow definition left the trigger registration pointing at a superseded version | No designer-save event in either log since the 08-27 registration or the 08-31 redefinition | **FAIL — worse than v7's finding, not merely unchanged**: v7 found "V3 only, not V4"; this cycle finds the V3 itself is now stale relative to the live definition |
| `RoundStatisticsStaleAfterSeconds` fail-safe default | Not separately leveled; TAD prose still calls unseeded the safe default | **The deployed value (300) is E1-confirmed live, twice, post-fix.** The TAD's own description of what is safe/shipping is stale (§7.3) | `pipeline.log:51,:61` | **PASS on the setting itself — this is the one line item that improved since Test Report v7.** The residual risk is the flow trigger (above), not this setting |

- Idempotency: deploy re-run against an already-deployed target → `PASS` (Dev Summary §11/pipeline.log record paired import runs, most recently 2026-08-31, each re-run clean)
- V4 designer/editor open + save, performed by `<no one — not yet performed>` on `<n/a>` → **FAIL**
- Cross-OS (C-TECH-054): `N/A` — no CI-runner-specific script introduced this revision
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → `PASS`

### 7.3 `IMP-0511` residual and the new `IMP-0575` documentation finding

**The functional bug IMP-0511 named is fixed and the fix is live-confirmed**, not merely seeded: `pipeline.log:51`
and `:61` both independently query `RoundStatisticsStaleAfterSeconds` post the 2026-08-30 fix and both read `300`.
`roundStatistics.test.ts`'s case 3 (`staleAfterSeconds:120` → `status:"ok"`) demonstrates the underlying mechanism
generically succeeds at any non-null bound, so no further test naming the literal figure 300 is required to close
the functional half of this Fail Condition — the code is not special-cased on a magic number.

**What remains open, and it is two distinct things, not one:**

1. **The flow cannot currently fire live at all** (§6, §7.1, T-1) — a stale trigger registration, unrelated to
   `staleAfterSeconds`. Even with the setting correct, no trustee can currently trigger a fresh computation.
2. **Three prose surfaces still describe the pre-fix state as current** — `roundStatistics.ts:499`'s own doc-comment
   ("`staleAfterSeconds` null (the shipping default…)"), `roundStatistics.test.ts:743`'s case-4 comment ("The
   SHIPPING configuration"), and the TAD's OQ-042 rows (architecture.md L2831/L4106/L4303, "Unseeded is a valid,
   fail-safe state"). `IMP-0511`'s own `proposed_change` asked for exactly this correction on 2026-08-30 and its
   `status` is still `NEW` in `logs/improvement-log.jsonl` — three days and two live-confirmed deploys later. Logged
   this cycle as `IMP-0575` (friction — the functional risk is low, since the code is not literally broken by this,
   but it is precisely the "a defect that a passing static test did not catch" shape this agent's Improvement
   Capture rules require reporting, and it is the exact worked example `test-agent.md:114-117` names by id).

## 8. Recommendations

1. **Do not treat this build as closing IMP-0511.** The setting is fixed and live; the flow that would exercise it
   currently cannot fire at all. Both facts belong in the Deployment Summary if this build proceeds.
2. Pipeline-agent's next deploy should perform, in this order: import → re-confirm `RoundStatisticsStaleAfterSeconds`
   live (expected unchanged, still 300) → **the designer open/turn-off/turn-on step** for `REV | Portal | Round
   Statistics` (named in the standing Deployment Summary REVIEWER ACTION REQUIRED block) → confirm
   `callbackregistration.createdon` moves → the V4/V5 OBSERVED-EFFECT run C-TECH-064 requires.
3. Route `IMP-0575` (or fold into the next `architect-agent` TAD pass) to correct OQ-042's three rows and the two
   source/test comments, and to formally amend ADR-040 for item 5's reversal in the same pass — both are prose
   divergences from what is actually shipping, not code defects, and both are cheap to fix together.
4. If the reviewer again elects to override this FAIL to proceed to deploy (as was done for Test Report v7's
   equivalent finding, `logs/routing.log:412`), the Deployment Summary must name **both** current-cycle facts:
   the flow cannot fire until the designer step is performed, and the setting is confirmed correct.

---

```
CONSTRAINT CHECK
Domain   HARD: 6 / 6 of 6     |  violations: NONE
                               |  unevaluable: NONE
Domain   SOFT: 0               |  warnings:   NONE
Tech     HARD: 21 / 23 of 23  |  violations: C-TECH-053, C-TECH-064
                               |  unevaluable: NONE
Tech     SOFT: 1 (C-TECH-067)  |  warnings:   NONE
  C-TECH-053: REV | Portal | Round Statistics flow — V4 designer-save not performed;
    `callbackregistration.createdon` stale since 2026-08-27 18:22, unmoved by the 2026-08-31
    build-8 flow-definition replacement (docs/deployments/trustee-portal-visual-refresh-deployment-summary.md#L51)
  C-TECH-064: same flow — the only admissible evidence for a Dataverse-trigger is an OBSERVED
    EFFECT run, and none exists since the registration went stale (metadata alone is inadmissible
    per this constraint's own text). The disclosure-control half of this same constraint
    (RoundStatisticsStaleAfterSeconds) is separately PASS, live-confirmed twice (pipeline.log:51,:61)
Overall: BLOCKED
```

Both violations are carried forward from Test Report v7 (same underlying gap: this flow has never
reached V4), covered by the standing [C-TECH-058](../../constraints/technology/technology-constraints.md#L128)
OVERRIDE recorded at [`pipeline.log:41`](../../logs/pipeline.log#L41). Per that constraint, deployment may
proceed only on the reviewer's explicit `OVERRIDE` naming these rows and a reason — a commercial/delivery
gate never halts a deploy on its own account, but the reviewer's decision must be recorded in the Deployment
Summary, not inferred from this report's status.

TEST REVIEW REQUIRED — docs/tests/trustee-portal-visual-refresh-test-report-v8.md  |  Result: FAIL
Respond APPROVED to proceed to Pipeline, REQUEST RETEST to re-run, or give feedback for dev fixes.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0575 | `stale-claim-contradicting-rechecked-source` | friction | When an emergency fix changes a seeded default outside the normal dev-summary/TAD revision cycle, grep for every doc-comment and test-comment naming the OLD value as "the shipping/default" configuration and correct them in the same pass. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (572 entries, 569 distinct lessons)
