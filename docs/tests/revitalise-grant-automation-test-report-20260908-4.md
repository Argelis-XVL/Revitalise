# Test Report — Revitalise Grant Automation (DocuSign Acceptance Workflow Batch)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260908-4/
**Date:** 2026-09-08
**Status:** FAIL
**WBS:** 3.2 (Create Envelope), 3.3 (Reminders & Escalation), 3.4 (Completion)

---

**Scope note.** This build is a documentation/settings-mirroring pass over the same DocuSign
automation content already imported to DEV as build `-20260907-3`
([`logs/pipeline.log`](../../logs/pipeline.log) 2026-09-07 06:10, V3). No flow logic changed
between `-3` and this build. This report does **not** carry forward the prior cycle's scoping
decision to treat the assumption register as "unchanged, not re-litigated" — that decision was
correct in [`-20260906-3`](revitalise-grant-automation-test-report-20260906-3.md) only because no
import had happened yet. An import has since happened, over 24 hours have elapsed, and the
register must be re-asked against the environment's current state (see §7.1, and `IMP-0670`).

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Vitest, Code App) | Yes | 771 | 0 | 0 |
| Unit (Pester, provisioning) | Yes | 1022 | 0 | 1 |
| Regression (Solution Checker) | Yes | 0 Critical/High/Medium/Low/Informational | 0 | — |
| Security (field security coverage) | Yes | 69/69 secured columns released, 0 baselined findings | 0 | — |
| Coverage threshold | Yes | 81.26% (threshold 80.0%) | 0 | — |
| Platform Contract | Yes | 1 new orphan-class finding (`IMP-0670`, see §7.1) | 1 | — |
| Verification Level | Yes | V3 reached in DEV for the functional content; V4 not performed | 1 | — |
| Process gate (`improvement-log-check`) | Yes | Re-run live: `OK`, 0 unread blockers | 0 | — |
| **Total** | | 1862 | 1 (constraint-level) | 1 |

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-041 | Acceptance document pre-populated, routed via DocuSign on Approved | `REVAcceptanceCreateEnvelope` — well-formed (V1), packaged (V2), imported to DEV (V3, 2026-09-07 06:10) | **PARTIAL** — no live envelope has been created; wire-shape assumption A-DS-2 (tab values) unconfirmed |
| FR-042 | Two signatures in sequence, applicant then referee/GP | Role names ground-truthed against the live template's anchor-tag table ([dev-summary §"reviewer-supplied DocuSign anchor-tag ground truth"](../development/revitalise-grant-automation-dev-summary.md#L6355)) | **PARTIAL** — role-name/value half confirmed; connector dynamic-schema half (A-DS-2) unconfirmed |
| FR-043 | Reminders at 3 and 7 days | `Set_reminder_cadence` calls `AddReminders` with `Setting.ReminderDays=[3,7]` ([dev-summary §"IMP-0618 resolved"](../development/revitalise-grant-automation-dev-summary.md#L6706)) | **PARTIAL** — design and settings-row confirmed; live override-takes-precedence fact (A-DS-11a) unconfirmed |
| FR-044 | Escalation to process owner at 14 days | `REVAcceptanceRemindersEscalation`, `Setting.EscalationDays=14`, `rev_escalatedon` idempotency stamp — field security profile confirmed released ([`FieldSecurityProfiles.xml#L592`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L592)) | PASS at V1–V3 |
| FR-045 | Grant status → Acceptance Signed, signed PDF filed to SharePoint | `REVAcceptanceCompletion` — DocuSign Connect webhook trigger unconfirmed against the connector's own dropdown (A-DS-8); SharePoint `CreateFile` wire shape unconfirmed (A-DS-10 remainder) | **PARTIAL** |
| FR-046 | Manual print-sign-scan route | TAD §5.8–5.10 records this as "recorded directly on the Grant record through the Model-Driven App — no flow, by design" ([architecture.md#L744](../architecture/revitalise-grant-automation-architecture.md#L744)) | Not a flow requirement; no automated test applies — confirmed by design decision, not by execution |
| FR-047 | Batch issuance for multiple approved grants at one meeting | Not exercised by this dispatch's scope (wired via `REV \| Portal \| Finalise Decisions`, [architecture.md#L723](../architecture/revitalise-grant-automation-architecture.md#L723)) | Out of this batch's WBS scope — carried, not tested here |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-DS-058 | Constraint Verification | C-TECH-058 re-evaluated against current environment state | Every §10 row OPEN and closeable in an existing environment either closed, or covered by a reviewer `OVERRIDE <A-nnn>` recorded in the Deployment Summary | DEV has run this DocuSign content live since 2026-09-07 06:10 (V3); six rows (A-DS-2 wire-shape half, A-DS-3, A-DS-8, A-DS-9, A-DS-10 wire-shape half, A-DS-11a) remain OPEN, each closeable by a single designer session or one test envelope in that same environment; no `docs/deployments/revitalise-grant-automation-deployment-summary.md` addendum records this import or any `OVERRIDE` | **P1** |
| T-DS-053 | Verification Level | Human open-and-save (V4) performed for the three new flows, per C-TECH-053 | V4 confirmed by a named human, dated | `logs/pipeline.log`'s 2026-09-07 06:10 entry states in its own text: *"V4 (designer open-and-save of the three new DocuSign flows) NOT performed"* — unchanged in every Dev Summary revision through 2026-09-08 | **P1** |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-DS-01 | P1 | C-TECH-058: deployment proceeded to DEV with six DEV-closeable assumption-register rows OPEN and no recorded `OVERRIDE` | T-DS-058 |
| D-DS-02 | P1 | C-TECH-053: no V4 human open-and-save step recorded for any of the three DocuSign flows, over 24h after V3 import | T-DS-053 |

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-001 | No hardcoded secrets | PASS | `gitleaks`-class scan clean; DocuSign account/template ids are environment variables, not literals |
| C-TECH-004 | Input validation | PASS | Unaffected by this batch — no new external input surface |
| C-TECH-006 | Auth enforced on non-public routes | PASS | Unaffected — DocuSign flows trigger on Dataverse row events, not an HTTP endpoint |
| C-TECH-040 | Dataverse roles via group teams only | PASS | No direct user role assignment introduced this batch |
| C-TECH-042 | Provisioning idempotent, CONVERGENCE declared | PASS | `provisioning-step-convergence` re-run clean per dev-summary §"five HARD build gates" revision |
| C-TECH-045 | DLP connector groups | PASS | DocuSign already in Business DLP group (TAD §6.4); re-checked, no change needed |
| C-TECH-047 | No hardcoded environment values | PASS | Re-run live this build; the two live-org-URL-in-comment near-misses from 2026-09-06/07 are both fixed and re-verified clean |
| C-TECH-050 | Field Security Profile writes via Web API, not solution import | PASS | The `rev_grant.rev_escalatedon` `FieldPermission` was created out-of-band via `ensure-schema.ps1`'s Web API path after two solution-import attempts failed identically (`logs/pipeline.log` 2026-09-07 06:00) — the exact route this constraint requires |
| C-TECH-052 | Every hand-authored artefact has a register row | PASS | All eleven DocuSign guesses (A-DS-1 through A-DS-11) are registered, each carrying its marker in source; `verify-assumption-markers.py` re-run clean, 23 OPEN rows checked |
| **C-TECH-053** | Reported only at the level actually executed; V4 named step performed | **FAIL** | Manifest honestly claims V2 for this artifact; the environment (a different but content-identical build) reached V3 on 2026-09-07 06:10; **no V4 (human open-and-save) has been performed or recorded for any of the three flows**, over 24h later |
| **C-TECH-058** | OPEN §10 assumption blocks deployment to an environment where it could be closed, absent a recorded `OVERRIDE` | **FAIL** | See D-DS-01 / T-DS-058 above. Contrast with [`-20260906-3`](revitalise-grant-automation-test-report-20260906-3.md#L78), which correctly scored this **PASS as scoped** because the deploy had not yet happened — the precondition changed on 2026-09-07 06:10 and no subsequent cycle re-asked the question until this one (`IMP-0670`) |
| C-DOM-033 | Special-category register — `rev_grant.rev_escalatedon` classification | PASS | Row present at [`special-category-register.yml#L308`](../../constraints/domain/special-category-register.yml) (`pending_adjudication:`), `domain-invariants` re-run clean |

## 6. Provisioning Verification

| Item (TAD §12) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_docusign` / `rev_SharedDocuSign` connection reference | connectorid `shared_docusign` | `pac connection list` + live FetchXML of the deployed `connectionreference` row, both confirming `shared_docusign` (A-DS-1 CLOSED, [dev-summary#L7033](../development/revitalise-grant-automation-dev-summary.md#L7033)) | PASS |
| `rev_SharedSharePoint` connection reference | connectorid `shared_sharepointonline` | Reviewer bound a real connection in the DEV maker portal; corroborated by `pac connection list` (A-DS-10 connector-identity half CLOSED, [dev-summary#L7138](../development/revitalise-grant-automation-dev-summary.md#L7138)) | PASS |
| DocuSign `SendEnvelope`/`AddReminders` wire shape (tabs, `signers`) | Confirmed against the designer's resolved schema | **Not yet performed** (A-DS-2) | **OPEN — closeable in DEV now** |
| DocuSign Connect webhook `events` value (`envelope-completed`) | Confirmed against connector's own dropdown | **Not yet performed** (A-DS-8) | **OPEN — closeable in DEV now** |
| SharePoint `CreateFile` parameter names / `Path` response | Confirmed against the designer's resolved schema | **Not yet performed** (A-DS-10 remainder) | **OPEN — closeable in DEV now** |
| `rev_grant.rev_escalatedon` FieldPermission on `REV_TrusteeRestricted` | Released, `CanRead/Update/Create`=4 | `verify-field-security-coverage.py` live: PASS, 69 secured columns, 0 baselined findings | PASS |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Result |
|---|---|---|---|---|---|
| A-DS-1 | DocuSign connector id | CLOSED | Live `pac connection list` / FetchXML | Yes, already used | PASS |
| A-DS-2 | Signer role names + wire shape for tab values | PARTIALLY CLOSED (role names/values only) | DEV designer session against template `b832b15e-...` | **DEV exists, solution imported since 2026-09-07 06:10** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-3 | `rev_grant` CREATED trigger + lookup-navigation read | OPEN | Trigger the flow once in DEV, read raw trigger outputs | **DEV exists** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-4/A-DS-5/A-DS-6 | Referee-tab / prefill product decisions | OPEN, reviewer-decision-only | Reviewer's word, no technical step | N/A (not environment-closeable) | Correctly carried — not a C-TECH-058 case |
| A-DS-7 | No DocuSign status query in escalation eligibility | Design decision, not OPEN | — | — | PASS |
| A-DS-8 | DocuSign Connect `events` value | OPEN | DEV designer, resolve dropdown | **DEV exists** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-9 | `documentId: 'combined'` | OPEN | First real completed envelope | **DEV exists (once A-DS-2/8 close and one envelope is sent)** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-10 | SharePoint `CreateFile` wire shape | PARTIALLY CLOSED (connector identity only) | DEV designer session | **DEV exists** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-11(a) | `AddReminders` overrides template live | OPEN | Send one real envelope, read reminder config back | **DEV exists** | **FAIL — closeable now, not closed, no OVERRIDE** |
| A-DS-11(b) | Repeat-forever cadence acceptable | CLOSED, reviewer-accepted | — | — | PASS |

No orphan hand-authored contracts found (every guess in this batch's three flows carries its A-DS-n marker, per `verify-assumption-markers.py`).

### 7.2 Verification levels achieved

| Component | Level claimed (manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `RevitaliseGrantAutomation.zip` / managed | V2 — packaged, Solution Checker clean | V2 confirmed for **this** artifact | `solution-checker/pac-solution-check-stdout.log`, correlation id `baf7e325-...` | PASS |
| DocuSign/SharePoint automation content (same flow definitions) | — | **V3** in DEV, established by build `-20260907-3`, not this build | `logs/pipeline.log` 2026-09-07 06:10 entry | PASS (honestly attributed to the correct build) |
| Three DocuSign flows, designer open-and-save | V4 named in `config/revitalise-grant-automation-pipeline.yml`'s DEV `post_deploy` | **NOT PERFORMED** | Same pipeline.log entry's own text; unchanged through every dev-summary revision to 2026-09-08 | **FAIL** |

- Idempotency: PASS — the 2026-09-07 06:10 import was re-run once and succeeded cleanly (async `24464caf-...`).
- V4 designer/editor open + save: **FAIL** — not performed, no named owner/date recorded.
- Cross-OS (C-TECH-054): N/A — no new pipeline/CI script this batch.
- Warnings triaged (C-TECH-055): PASS — manifest shows 6 total, 2 resolved, 4 accepted, 0 untriaged, each citing a Dev Summary line.
- Diagnostic components removed (C-TECH-056): N/A — none created this batch.

## 8. Recommendations

1. Do not proceed to `pipeline-agent` for further promotion of this batch until either (a) a
   human performs the V4 open-and-save step for all three flows and sends one real test
   envelope in DEV (closing A-DS-2/3/8/9/10/11a), or (b) the reviewer records an explicit
   `OVERRIDE A-DS-2, A-DS-3, A-DS-8, A-DS-9, A-DS-10, A-DS-11a` with a reason in a
   `docs/deployments/revitalise-grant-automation-deployment-summary.md` addendum for the
   2026-09-07 06:10 DEV import, per C-TECH-058.
2. Add the missing Deployment Summary addendum for the 2026-09-07 06:10 DEV import itself —
   none exists in `docs/deployments/revitalise-grant-automation-deployment-summary.md` naming
   build `-20260907-3` or this batch's wbs:3.2/3.3/3.4 deploy at all.
3. Correct the stale test-count citations `IMP-0669` already flagged (Dev Summary §L5175/§L7485
   read "228/228 tests, 97.78% coverage"; this build's live output is 771/771, 98.47%) — not a
   test-agent P1 on its own, but worth folding into the same revision that resolves item 2.
4. Once V4 is performed (or overridden) and re-verified live, re-run this Test Report — the
   functional test cases in §2 are otherwise ready to move from PARTIAL to PASS with no further
   source change expected.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0670 | `gate-cannot-fail` | blocker | C-TECH-058 must be re-evaluated by test-agent every cycle against current pipeline.log/environment state, never carried forward as "unchanged, not re-litigated" once an actual import has occurred between test cycles — the precondition (does the environment now exist) can change with no source edit to prompt a re-read. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
