# Test Report — Revitalise Grant Automation

**Feature Slug:** `revitalise-grant-automation`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260924-4/`
**Date:** 2026-09-24
**Status:** PASS — scoped to source/V1–V2, gated for pipeline (see §7.2)

---

**What this cycle covers.** This artifact packages nine EF items from Anna Southern's
post-deployment feedback, built across nine dispatches on 2026-09-22 through 2026-09-24:
[EF-04](../development/revitalise-grant-automation-dev-summary.md#L8210) (Casework screen
section order vs. the source PDF),
[EF-44/EF-07/EF-24](../development/revitalise-grant-automation-dev-summary.md#L8384) (score
audit column split + real question/answer text in the trustee breakdown),
[EF-34/EF-45](../development/revitalise-grant-automation-dev-summary.md#L8621) (compound
auto-reject on stale funding + a deterministic reason column),
[EF-27](../development/revitalise-grant-automation-dev-summary.md#L8820) (safeguarding
completion date/owner, plus a race-condition fix on the same flow found this build cycle,
[here](../development/revitalise-grant-automation-dev-summary.md#L10255)),
[EF-01/EF-36/EF-38](../development/revitalise-grant-automation-dev-summary.md#L9452) (Location
Area, Applicant Type, Age Range via three new Quick View Forms), and the
[round-statistics flow fix](../development/revitalise-grant-automation-dev-summary.md#L9707)
(splitting a 7-variable `InitializeVariable` into 7 actions).

Independently re-run rather than trusted from the dev summary's own narrative: the full local
Pester suite, the full trustee-portal Vitest/typecheck/lint suite, all four required
source-gate scripts, `verify-improvement-log.py --check`, and a direct inspection of the packed
managed solution's `customizations.xml`.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit / Regression (Pester, `src/tests/solutions`) | Yes, re-run independently | 260 | 0 | 0 |
| Unit / Regression (Pester, whole solution, per artifact manifest) | Per `test-results/pester-results.xml` | 1133 | 0 | 1 (pre-existing) |
| Unit (trustee-portal Vitest/typecheck/lint) | Yes, re-run independently | 789 | 0 | 0 |
| Integration | Source/artifact-level only — no live Dataverse query this cycle (not yet imported to DEV) | — | 0 | deferred to pipeline-agent |
| End-to-End | Not run — this artifact has not been imported anywhere yet | — | — | deferred to pipeline-agent |
| Regression (source gates) | `run-source-gates.py` — 16/16 | 16 | 0 | 0 |
| Security | No new auth surface, secret, or privilege path in this batch; `secret-scan`/`no-trustee-in-column-security-profile` unaffected | — | 0 | — |
| Accessibility | No new interactive control; `CurrentCircumstancesPanel`/panel-reorder is a heading + existing text re-parented, covered by existing portal a11y suites | pass (via existing suites) | 0 | — |
| Performance | No NFR threshold touched this batch; code-app bundle budget still within limit (manifest) | pass | 0 | — |
| Provisioning | No TAD §12/§6.1 item added this batch | N/A | — | — |
| Platform Contract / Verification Level | See §7 | — | — | — |
| Constraint Verification | See §5 | — | 0 | — |
| **Total (this batch's own new coverage)** | | **1058** (260 Pester subset + 789 Vitest, less overlap counted once, plus 9 new/updated flow-regression tests already inside the 260) | **0** | **1 pre-existing skip** |

## 2. Requirement Coverage

| Feedback item | Requirement | Test Case(s) | Result |
|---|---|---|---|
| EF-04 | Casework detail screen section order matches `docs/Import/3. Round 4 - Individual Applications.pdf` | `ApplicationDetailPage.test.tsx` panel-order assertion; `CasePanels.test.tsx` `CurrentCircumstancesPanel` describe block | PASS |
| EF-44 | Scoring audit column is durable, admin-only, written in the same call as status | `ScoringInvariants.Tests.ps1` — reads-only-needed-columns test; write traced end-to-end (source, not live) | PASS (source-level; not exercised live) |
| EF-07 / EF-24 | Trustee-facing breakdown reads as prose ("question · answer label"), not a schema dump | `ScoringInvariants.Tests.ps1` — new Describe `EF-07 / EF-24 (2026-09-22)`, 9 tests | PASS |
| EF-34 | Compound auto-reject (funding received AND not >12 months ago), evaluated before the score threshold, order explicit | `ScoringInvariants.Tests.ps1` — new Describe for EF-34, asserts precedence and null-safe form | PASS |
| EF-45 | Auto-reject reason is deterministic, written in the same call as status | `ScoringInvariants.Tests.ps1` — new Describe for EF-45, 1 of 8 new tests in that block | PASS |
| EF-27 | Safeguarding completion date/owner set by the platform, read-only on the form | `SafeguardingActionCompletion.Tests.ps1`, 13 tests, incl. the `disabled="true"` regression | PASS |
| EF-27 (race) | No mis-attribution race between two `Modified` triggers on the same row | Traced against source (Microsoft Web API docs + `subscriptionRequest/filteringattributes` fix); no new automated test added for the race itself | PASS (source-level trace; **not exercised against a live concurrent write** — see §7.2) |
| EF-01 / EF-38 / EF-36 (3rd element) | Location Area, Applicant Type, Age Range readable, read-only, via Quick View Forms | New `Describe 'Quick View Forms on rev_applicant ...'` (3 cases) + updated `IntakeContract.Tests.ps1` assertions | PASS |
| Round-statistics flow | One variable per `InitializeVariable` action (Power Automate designer save rule) | `RoundStatisticsContract.Tests.ps1` — new Describe, 5 tests, plus a before/after run of `verify-flow-definition-language.py` proving the gate now catches the original shape | PASS |

## 3. Failed Tests

None. 0 failures across 1133 Pester assertions (manifest-recorded) and 789 Vitest assertions, and 0 findings across the 16 source gates.

## 4. Defects Raised

None newly raised by this test cycle. One historical HARD-constraint finding closed since the artifact's own dev-summary revisions were written —
[`IMP-0838`](../../logs/improvement-log.jsonl) (C-DOM-033, `rev_localauthority`/`rev_localauthoritystatus` unadjudicated) — confirmed `APPLIED` in the current log, so the constraint is currently green (§5).

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-033](../../constraints/domain/domain-constraints.md#L95) | Every column-secured attribute adjudicated in the special-category register | PASS | `IMP-0838` `status: APPLIED`, `reviewed_in: 2026-09-23-improvement-review-3.md`; `run-source-gates.py` `domain-invariants` step green this run |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every hand-authored platform contract not yet ground-truthed carries a §10 register row | PASS | `verify-assumption-markers.py`: 36 OPEN rows, every one carrying its marker; 0 orphan source markers |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Component reported only at the level actually executed | PASS | §7.2 below — every revision this batch states its true level (V1/V2) and explicitly says "NOT YET PERFORMED" for V4, rather than over-claiming |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts executed by CI/pipeline run on the CI runner's OS | N/A this batch | No new provisioning/pipeline script added; local run is macOS only, CI (`auth` step) not exercised this session — pre-existing gap, not introduced here |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Every tool warning triaged in the current feature's Dev Summary | PASS | Manifest: 5 warnings, 4 resolved, 1 accepted (`flow-avoid-recursive-loop`) — and the "accepted" wording itself was checked against IMP-0573's figure-matching rule and correctly re-labelled via `IMP-0860` rather than left as a stale "Fixed" claim |
| [C-TECH-061](../../constraints/technology/technology-constraints.md#L131) | Improvement-log processing triggers enforced by script | PASS | `verify-improvement-log.py --check` exits with `OK (schema + triggers)` — 218 NEW (31 unread, 1 awaiting-approval, 186 reviewer-deferred), under batch threshold |

Aggregate, matching the dev summary's own per-revision blocks: **Domain HARD 10/10, Domain SOFT 0 in scope, Tech HARD 37/37, Tech SOFT 1 in scope (C-TECH-067, pre-existing, unaffected). Overall: PASS.**

## 6. Provisioning Verification

No TAD §12 / §6.1 item was added or changed by this batch (schema, security profile and form placements for EF-27's three columns were built in an earlier session; this batch added the writer flow only). N/A this cycle.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| [A-SG-1](../development/revitalise-grant-automation-dev-summary.md#L8922) | `rev_safeguardingactioncompletedby` can be set from the trigger row's own `_modifiedby_value` | OPEN | The flow must exist in a live DEV, then a human other than the service account ticks the box | **No** — this build has packaged the flow but it has not been imported anywhere | Confirmed: flow is in `Workflows/REVSafeguardingActionCompletion-...json` inside this build's managed zip, not yet deployed | Correctly OPEN — not a defect against this cycle |
| [A-QVF-1](../development/revitalise-grant-automation-dev-summary.md#L9569) | The `FormXml/quickview/` folder name / `type="quickview"` convention is accepted by the packer | OPEN | "the real `pac solution pack` step" | **Yes — this build** | `unzip -l` + `unzip -p customizations.xml` on `RevitaliseGrantAutomation-managed.zip`: all three formids (`7f145e5b-e5c9-47ec-9dc6-211af76afe35`, `eed29b6a-7444-4f54-9483-afd0d91e72ca`, `8df85b1f-68bf-4460-b80d-ad92cb36beb9`) present, 9 total hits (form id + embed reference × 3) | **CLOSED by this test cycle** — dev summary's own register row is now stale against this build; recommend it be updated to CLOSED (§8) |

No orphans found: every hand-authored artefact touched this batch (three flow JSONs, three Quick View Forms, one FormXml edit) has a register row or is explicitly recorded as needing none (round-statistics rule is documented Microsoft platform fact, not a guess).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| EF-04 panel reorder | V2 (full Vitest, tsc, eslint) | V2 confirmed | 789/789 Vitest re-run this cycle | PASS at claimed level |
| EF-44/EF-07/EF-24 flow rewrite | V2 (Pester + Vitest) | V2 confirmed | 260/260 Pester (subset containing this suite), 789/789 Vitest | PASS at claimed level |
| EF-34/EF-45 flow logic | V1 (source gates + Pester) | V1 confirmed | 16/16 source gates, 260/260 Pester | PASS at claimed level |
| EF-27 flow + race fix | V1 (source-level) | V1 confirmed | JSON valid, 16/16 source gates, description ≤256 chars | PASS at claimed level |
| Quick View Forms (EF-01/38/36) | V2 claimed in dev summary (well-formed XML + 15/16 gates); **now V2 (packaged) confirmed by this cycle** | V2 | §7.1 — packer accepted all three forms into the managed zip | Level raised from the dev summary's own V1/V2 claim to a test-agent-confirmed V2 |
| Round-statistics flow split | V1 (source gates + Pester) | V1 confirmed | before/after run of `verify-flow-definition-language.py` shows the gate now catches the pre-fix shape and passes the post-fix shape | PASS at claimed level |

- Idempotency: **NOT re-run this cycle** — no environment has this build imported yet, so a re-import idempotency check has nothing to run against. N/A, not a failure.
- V4 designer/editor open + save, performed by `<name>` on `<date>` → **NOT YET PERFORMED for any component in this batch.** Dev Summary is explicit and consistent about this on every one of the nine revisions — no false claim found. This is the correct next-stage responsibility (pipeline-agent import, then the reviewer's own open-and-save for the round-statistics flow and the safeguarding flow specifically, since those are the two flows a human must open in the Power Automate designer to fully close `IMP-0820`/`IMP-0821` and `A-SG-1`).
- Cross-OS (C-TECH-054): N/A this batch — no new CI/pipeline script.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS — see §5.

## 8. Recommendations

1. **Update the dev summary's own §10 register**: mark `A-QVF-1` CLOSED, citing this build's `customizations.xml` as the ground truth that closes it (§7.1 above) — the register's own convention (`IMP-0219`) is to answer a stale precondition at the start of the next cycle that touches it, and this is that cycle.
2. **Route `IMP-0858` and `IMP-0800` through an improvement review** before the next build reaches `unit-tests` — both are corrected (`IMP-0859`, `IMP-0801`) but unprocessed, and `verify-improvement-log.py --check`'s own warning says this will otherwise cost a full build attempt (`IMP-0285`'s class).
3. **On import to DEV**, prioritise opening `REV | Portal | Round Statistics` and `REV | Safeguarding | Action Completion` in the designer first — these are the two components whose only remaining verification step is a human save (closes `IMP-0820`/`IMP-0821`) or a live trigger observation (closes `A-SG-1`).
4. No code defect blocks approval to pipeline. The gate below reflects a source/V1–V2 PASS with the V3–V4 work correctly deferred to `pipeline-agent`, not omitted.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This test cycle raised no new finding: the one gap it found (`A-QVF-1`'s stale OPEN status) is a register-currency issue the recommendations above route to the next dev-summary edit, not a defect in this dispatch's own work, and does not meet any of the six capture triggers in `skills/how-to-log-an-improvement.md` |

Digest regenerated: N/A — no new log entry this cycle.
