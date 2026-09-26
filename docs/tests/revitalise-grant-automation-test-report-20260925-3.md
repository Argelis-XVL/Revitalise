# Test Report — Revitalise Grant Automation (DocuSign designer save-failures, wbs:3.2/3.4)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260925-3/
**Date:** 2026-09-25
**Status:** FAIL

**Scope of this cycle:** the two DocuSign designer save-errors fixed in
`docs/development/revitalise-grant-automation-dev-summary.md`'s "Revision — DEV designer
save-failures fixed on both Acceptance envelope flows" (line 10798) and the two subsequent
build-blocker revisions (`IMP-0883`, `IMP-0888`), which carry no scope of their own. FAIL is
driven entirely by `C-TECH-058` against `A-DS-12`/`A-DS-13` — see §7.1. Everything this
dispatch's own change touches at source level is independently confirmed correct (§1, §7.2).

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester, `AcceptanceEnvelopeContract.Tests.ps1`, re-run live by test-agent) | 7 | 7 | 0 | 0 |
| Unit (build's own Pester run, per build-agent's handoff) | 1148 | 1148 | 0 | 0 |
| Regression (`LocalAuthorityRegister.Tests.ps1`, blocker fix `IMP-0888`) | 9 | 9 | 0 | 0 |
| Integration / End-to-End (live DocuSign designer open-and-save, V4) | 0 | 0 | 0 | 2 (out of reach — see §7.2) |
| Security | — | — | — | N/A this cycle (no auth/role/secured-column surface touched) |
| Accessibility | — | — | — | N/A this cycle (no UI screen touched) |
| Performance | — | — | — | N/A this cycle |
| Provisioning | — | — | — | N/A this cycle (no TAD §12/§6.1 item touched) |
| Compliance | 8 source gates | 8 | 0 | — |
| **Total** | | 1172 | 0 | 2 |

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-041 | Acceptance document created and routed via DocuSign on Approved | `Create_and_send_the_envelope` — [errors 1/2 fixed](docs/development/revitalise-grant-automation-dev-summary.md:10818) | **PARTIAL** — source-level shape confirmed correct (V1/V2); V4 open-and-save not yet performed |
| FR-042 | Two signatures in sequence, applicant then referee/GP | `AcceptanceEnvelopeContract.Tests.ps1` "referee signer bound to Application record" ([src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1:1](/Users/xvl/Library/CloudStorage/OneDrive-SharedLibraries-ArgelisConsultancy/Revitalise%20Respite%20Holidays%20-%20Optimisation%20Grant%20Application%20Process/Repository/Revitalise/src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1) | **PASS** at source level — confirmed live, this run |
| FR-045 | Status set to "Acceptance Signed" on both signatures received | `REVAcceptanceCompletion` trigger fix ([docs/development/revitalise-grant-automation-dev-summary.md:10837](docs/development/revitalise-grant-automation-dev-summary.md:10837)) | **FAIL** — `A-DS-13` (Connect-configuration-name) is explicitly not fixed; the flow is expected to still fail to save until a human resolves it live |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| V4-A-DS-13 | End-to-End / Platform Contract | `REVAcceptanceCompletion` designer open-and-save | Flow saves cleanly in DEV designer | Not run this cycle (requires human in DEV designer); Dev Summary itself predicts it will still fail on the Connect-configuration-name error | P2 — known, named, already tracked as `A-DS-13`, not a new defect this cycle introduced |
| V4-A-DS-12 | End-to-End / Platform Contract | `REVAcceptanceCreateEnvelope` designer open-and-save against the real connector schema | Flow saves cleanly and the real `signers` key names/merge-field placement are confirmed | Not run this cycle; source-level fix is a best-effort correction, "reasonable chance" per Dev Summary, unconfirmed | P2 — known, named, already tracked as `A-DS-12` |

## 4. Defects Raised

None raised by this test cycle. Both open items above are pre-existing, already-declared assumptions (`A-DS-12`, `A-DS-13`) carried into this cycle by the dispatch itself, not new findings from testing.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-001 | No hardcoded secrets | PASS | `secret-scan` step; no new credential-shaped literal in the two flow JSON files or the new test file |
| C-TECH-004 | Input validation/sanitisation | N/A this cycle | No user-input surface changed |
| C-TECH-006 | Authentication enforced | N/A this cycle | No auth surface changed |
| C-TECH-040 | Roles via group teams only | N/A this cycle | No security-role change |
| C-TECH-042 | Provisioning idempotency | N/A this cycle | No provisioning script changed |
| C-TECH-045 | DLP/connector compliance | PASS | `shared_docusign` connector unchanged; `connectionReferences` block byte-identical to the sibling flow's already-accepted shape (verified by re-running the JSON diff independently, this session) |
| C-TECH-046 | OOB roles never modified | N/A this cycle | No role touched |
| C-TECH-048 | No hand-rolled auth in Code Apps | N/A this cycle | No Code App data-source change in this revision's own scope |
| C-TECH-051 | No fabricated ids for platform-assigned components | PASS | Neither flow's `id`/`schemaName` was touched |
| **C-TECH-052** | Every hand-authored guess carries a §10 register row + source marker | **PASS** | `python3 scripts/verify-assumption-markers.py` — re-run this session, PASS: 35 OPEN rows checked, `A-DS-12`/`A-DS-13` both carry their marker in the relevant action/trigger `description` (confirmed independently by reading the packed field, 219/206 chars, both under the 256-char cap) |
| **C-TECH-053** | Component reported only at the level actually executed; V4 named with an owner before deploy is declared | **FAIL (for this specific claim)** — see §7.2. The Dev Summary itself states V4 "NOT YET PERFORMED", which is the honest and correct level statement C-TECH-053 requires — the constraint is not violated by that statement, but the **verification-level gate this test-agent runs still gates on it**, per this agent's own Fail Conditions |
| C-TECH-054 | CI-runner-OS scripts | PASS | No new script added; `LocalAuthorityRegister.Tests.ps1` fix is a literal-string correction inside an existing cross-platform Pester test, re-run live on this (Mac/POSIX) session |
| C-TECH-056 | Diagnostic components removed before export | N/A this cycle | No diagnostic component created |
| C-TECH-057 | Every build gate proven able to fail | PASS | No new build gate was wired this cycle (Dev Summary's own §"No new build-time gate was wired" — confirmed correct: this is a per-connector dynamic-schema class already established as ungroundable by static means, `A-DS-2`/`8`/`9`/`10`) |
| **C-TECH-058** | An OPEN §10 assumption blocks deployment into any environment where it could be closed, absent a recorded reviewer `OVERRIDE` | **FAIL** | `A-DS-12` and `A-DS-13` are both OPEN. DEV is the environment named as their own closing precondition (both rows' "Verification" column: "Open ... in the DEV designer"), and **DEV already exists** — it is the exact environment the reviewer used to produce the six designer errors this revision answers. No `OVERRIDE <A-nnn>` has been recorded anywhere in this session's evidence. This is a HARD constraint failure and the primary driver of this report's FAIL status |
| C-TECH-059 | Learning substrate never destroyed | PASS | `logs/improvement-log.jsonl` append-only, unbroken; `logs/known-failure-modes.md` regenerated (878 entries) per the prior revision's own log line |
| C-TECH-060 | No shipped text exceeds its length limit | PASS | Re-confirmed independently: longest `description` in `REVAcceptanceCreateEnvelope` is 219 chars (the `A-DS-12` marker line), under the 256-char designer cap; build-agent's own second-pass `run-source-gates.py` output (Dev Summary line 10952) already recorded the first-pass 258-char overflow and its fix, and this session's own length scan confirms no field over-limit today |
| C-DOM-004 | No personal data in logs | N/A this cycle | No log-writing action changed |
| C-DOM-010/011 | Audit logging | N/A this cycle | No audited entity/column touched |
| C-DOM-030/031/032 | Special-category data barred from scoring, secured, audited | N/A this cycle | Acceptance/DocuSign flows carry no special-category column |

**Overall constraint result: FAIL** — one HARD constraint (`C-TECH-058`) is violated by a pre-existing, correctly-declared, already-tracked condition. This is not a defect introduced by this dispatch's code; it is the honest state of two OPEN assumptions the dispatch itself could not close, which its own instructions correctly did not ask it to guess past.

## 6. Provisioning Verification

N/A this cycle — no TAD §12 or §6.1 item is touched by this revision.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-DS-12 | `signers` object keys (`"0"`/`"1"`) and merge-field placement inside signer `0`'s own `tabs` on `Create_and_send_the_envelope` | OPEN — supersedes wire-shape half of A-DS-2 | Open the flow in the DEV designer against the real `rev-docusign` connection/template and let it resolve the real key names | **YES — DEV already exists** and is exactly the environment that produced the six designer errors this revision answers | Source shape re-confirmed independently this session: no top-level `tabs` sibling to `signers`; `signers` is a keyed object `{"0": {...}, "1": {...}}`, not an array; document-level merge fields sit inside signer `"0"`'s own `tabs` (`Compose_template_tab_values` output) | **OPEN, and closeable now — FAIL per C-TECH-058** |
| A-DS-13 | `CreateHookEnvelopeV4` Connect-configuration-name key is undetermined; trigger left with only `accountId`/`events` | OPEN — explicitly **not** fixed, flow expected to still fail to save | Open `When_the_envelope_completes` in the DEV designer and let it resolve the actual required property | **YES — DEV already exists**, same environment | Source re-confirmed independently: trigger's `parameters` object is exactly `{"accountId": ..., "events": ["envelope-completed"]}`, no `name` key, `events` unchanged from its pre-existing A-DS-8-flagged value | **OPEN, and closeable now — FAIL per C-TECH-058. This is the more serious of the two: the Dev Summary itself predicts the flow will not save until a human acts** |

No orphan hand-authored artefacts found: both descriptions carry their `A-nnn` marker (confirmed by direct field read, not by re-running the generator's own claim).

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `REVAcceptanceCreateEnvelope` (source fix) | V1 (well-formed source corrected against real E1 error text) | **V2** — this session confirms the build-agent handoff's claim that both zips packed successfully, which V1 alone does not reach | `python3 -c "import json; json.load(...)"` (valid JSON, this session); build-agent's SUCCESS line, `logs/build.log` | PASS at the claimed+confirmed level |
| `REVAcceptanceCompletion` (source fix) | V1 | **V2** (packed) | Same as above | PASS at the claimed+confirmed level |
| `AcceptanceEnvelopeContract.Tests.ps1` (new regression test) | Not explicitly leveled in §11 — implicitly V2 (own suite green) | **V2, re-run live this session, not merely re-cited** | `Invoke-Pester -Path src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1` → 7/7 passed, this session, fresh run | PASS |
| Both DocuSign flows, end-to-end (V4/V5) | **NOT claimed** — Dev Summary explicitly states V4 "NOT YET PERFORMED" | **Not confirmable by test-agent** — a live DEV designer open-and-save is outside a test-agent dispatch's own reach, per this dispatch's own instruction | — | **Ceiling reached at V2 for this cycle; V4/V5 outstanding, named with no owner/date yet** |

- Idempotency: N/A this cycle — no provisioning/deploy step re-run (source and packaging only)
- V4 designer/editor open + save, performed by `<name>` on `<date>`: **NOT PERFORMED** — result: **FAIL** (required by `C-TECH-053`/`C-TECH-058` before either flow can be declared deployment-ready)
- Cross-OS (C-TECH-054): N/A — no new script
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): N/A this cycle

## 8. Recommendations

1. **Do not send this back to development-agent for another guess.** Both A-DS-12 and A-DS-13 have already had one best-effort correction each after live designer evidence; the Dev Summary's own reasoning (§"Ground truth established") is sound, and a second speculative correction with no new source would repeat the `platform-contract-guessed-not-groundtruthed` class rather than close it.
2. The correct next step is the reviewer opening both flows in the DEV designer (already named as mandatory `post_deploy` pre-activation steps in `config/revitalise-grant-automation-pipeline.yml`, confirmed present at lines 1315/1333/1405 this session) and either resolving them live or issuing an explicit `OVERRIDE A-DS-12`/`OVERRIDE A-DS-13` with a reason, per `C-TECH-058`, before pipeline-agent proceeds.
3. `Create Envelope` (A-DS-12) has a reasonable prospect of saving cleanly on first open; `Completion` (A-DS-13) is expected, on the evidence already gathered, to still require a live fix. Treat them as two separate outcomes, not one.
4. Because this is a HARD-constraint FAIL on a pre-existing, correctly-tracked condition rather than a defect in this dispatch's own change, `REQUEST RETEST` is only useful once the reviewer has actually acted on one or both flows in DEV — retesting the same unopened source will reproduce this exact FAIL.

---

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-09-25  **Response:** `APPROVED`, with `OVERRIDE A-DS-12` and `OVERRIDE A-DS-13`, per `C-TECH-058`

**Override reason, verbatim from the reviewer:** "both assumptions name the DEV designer as their
own closing step, and the corrected flow isn't in DEV yet to open."

**Why this override is sound, not a bypass of §7.1's finding:** both rows' own "Closing
precondition" column (§7.1 above) names the DEV designer as the closing step — but DEV, right
now, holds only the **pre-fix, broken** version of both flows (the version that produced the six
designer errors this dispatch answers). The corrected flow definitions exist only in this
artifact, not yet imported anywhere. §7.1 was correct that DEV *the environment* already exists;
it did not have visibility into the fact that DEV does not yet hold *this build's* corrected
source — that distinction only resolves once the artifact is actually imported. The override does
not waive C-TECH-058's requirement that the assumption eventually close against ground truth; it
recognises that for a first deploy of a fix, the only route to that ground truth is the deploy
itself. `A-DS-13` in particular is still expected, on the evidence already gathered, to fail to
save even after import — the override permits the attempt, not a claim that it will succeed.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This cycle's FAIL restates already-declared, already-marker-carrying OPEN assumptions (`A-DS-12`, `A-DS-13`) and an already-established constraint (`C-TECH-058`); it introduces no fact this repository did not already hold. Logging a duplicate finding here would not add information, matching the precedent set by `IMP-0883`'s own confirmation entry (`IMP-0884`) not being re-logged a second time |

Digest regenerated: NO — no new entry to regenerate against; `logs/known-failure-modes.md` already reflects the state confirmed by this test cycle (878 entries, generated 2026-09-25, per the file's own header read this session)
