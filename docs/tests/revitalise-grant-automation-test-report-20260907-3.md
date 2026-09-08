# Test Report — Revitalise Grant Automation (DocuSign Acceptance Workflow Batch, Phase-2/Final Build)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260907-3/
**Date:** 2026-09-07
**Status:** PASS
**WBS:** 3.2 (Create Envelope), 3.3 (Reminders & Escalation), 3.4 (Completion) — phase-2/final build,
restoring `rev_grant.rev_escalatedon`'s `FieldPermission` and closing the two-phase Dataverse
import workaround opened by `-20260907-2`.

---

**Scope note.** Per this dispatch's brief, the DocuSign assumption register (A-DS-1/2/3/8/10/11) is
**not re-litigated** here — unchanged from
[`-20260906-3`](revitalise-grant-automation-test-report-20260906-3.md#L91) and already correctly
gated as `post_deploy` steps. This report verifies only what changed since `-20260907-2`: that the
temporary FieldPermission removal is fully reversed, source-verified, and that this build's
verification level is reported honestly against what has actually been deployed.

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | Yes | 1022 | 0 | 1 |
| Regression | Yes | Solution Checker 0 Critical/High/Medium/Low/Informational | 0 | — |
| Security (field security coverage) | Yes | `field-security-coverage` PASS, 69 secured columns, 0 baselined findings — re-run live | 0 | — |
| Platform Contract | Yes | No new orphans; A-DS register unchanged (not re-litigated per scope) | — | — |
| **Verification Level** | Yes | V2 confirmed for THIS build; not conflated with `-2`'s deployed state (§7.2) | 0 | — |
| Process gate (`improvement-log-check`) | Yes | Re-run live: `OK` — 644 entries, 19 warnings, 0 unread blockers | 0 | — |
| **Total** | | 1022 (Pester) + 1 (field-security-coverage) + 1 (solution checker) | 0 | 1 |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| wbs:3.2 | `rev_grant` created → DocuSign envelope via `REVAcceptanceCreateEnvelope` | Unchanged from `-3`/`-2`; not re-tested this dispatch (out of scope delta) | PASS at V1/V2, carried forward |
| wbs:3.3 | Reminders/escalation, including `rev_escalatedon` column, now fully released | `verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation`, re-run live this dispatch; source read of [`FieldSecurityProfiles.xml:587-596`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L587) | PASS — column ships `IsSecured=1` with its `FieldPermission` restored (`CanRead`/`CanUpdate`/`CanCreate` = 4), no baseline entry remains |
| wbs:3.4 | Completion → signed PDF to SharePoint | Unchanged from `-3`/`-2`; not re-tested this dispatch | PASS at V1/V2, carried forward |

## 3. Failed Tests
None.

## 4. Defects Raised
None. One **friction finding** raised — see §5 and Findings Logged.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-052 | Every hand-authored platform artefact has a register row | PASS | No new hand-authored artefact this batch; A-DS-1…11 rows already registered, unchanged |
| C-TECH-053 | Reported only at the level actually executed | PASS | `logs/pipeline.log`'s last entry naming `revitalise-grant-automation` is the [2026-09-07 04:40 SUCCESS](../../logs/pipeline.log) idempotent re-import of build `-20260907-2` (the phase-1 workaround content). No entry names build `-20260907-3` or this artifact path. Manifest's own `"verification_level": "V2 — packaged; layout accepted by the packer and by the Microsoft-hosted Solution Checker … content and target-environment acceptance not proven by this build"` is the honest claim for THIS build — see §7.2 for why it must not be read against `-2`'s deploy history |
| C-DOM-030/031/032 | Special-category exclusion / secured / audited | PASS | `rev_grant.rev_escalatedon` register row confirmed present at [`constraints/domain/special-category-register.yml:308`](../../constraints/domain/special-category-register.yml#L308); `Entity.xml` unchanged (`IsSecured=1` throughout) |
| `field-security-coverage` (HARD) | Every secured column released or covered by a dated, owned baseline | PASS | Re-run live: `python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation` → `PASS — 69 secured column(s) … 0 baselined UNREADABLE finding(s)` — the phase-1 baseline entry is **absent**, not merely expired, confirmed by reading `config/gate-baselines.json`'s `baselines` array directly (no `rev_grant.rev_escalatedon` row remains) |
| Process gate: `improvement-log-check` | Every build gate must pass when re-run | PASS | `python3 scripts/verify-improvement-log.py --check` re-run live: `OK (schema + triggers) — 644 entries … 19 warning(s)`, 0 unread blockers |

**Phase-2 restoration confirmed, three ways, not one, matching the discipline the phase-1 report
demanded of itself:**
1. **Gate baseline removed** — `config/gate-baselines.json`'s `baselines` array (re-read this
   dispatch) carries no `field-security-coverage` entry for `rev_grant.rev_escalatedon`, only the
   `_seventh_gate_added_2026_09_07` narrative note explaining why the mechanism was built.
2. **Live gate re-run** — `verify-field-security-coverage.py` reports 69/69 secured columns
   released, 0 baselined findings (quoted above), matching build-agent's gate output exactly.
3. **Source-level FieldPermission restored** — [`FieldSecurityProfiles.xml:587-596`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L587)
   carries the `rev_grant.rev_escalatedon` `FieldPermission` block back in full (`CanRead=4`,
   `CanUpdate=4`, `CanCreate=4`, `CanReadUnmasked=0`) — the exact verbatim block the phase-1 report's
   §8 recommendation named.

**Self-healing count derivation confirmed, not merely re-run.** `src/tests/provisioning/EnsureSchema.Tests.ps1`
(`$script:ExpectedReleasedSecuredColumnCount` at [line 161](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L161))
computes the released-column count by reading `config/gate-baselines.json` live and subtracting any
current, non-expired `field-security-coverage` entry from the full secured-column count — it was never
hand-bumped for phase 1 and needed no edit for phase 2 either. With the baseline entry now gone,
`ExpectedReleasedSecuredColumnCount` collapses to `ExpectedSecuredColumnCount` (69) by construction,
exactly as [the comment at line 140](../../src/tests/provisioning/EnsureSchema.Tests.ps1#L140)
predicted it would. This is why Pester's 1022/1022 is a genuine confirmation of the restored state,
not a stale pin left over from the phase-1 variant.

**One stale source comment found, not blocking.** The header comment at
[`FieldSecurityProfiles.xml:467-473`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L467)
still reads "Twelve columns in THIS phase-1 build variant … temporarily UNRELEASED here" and points to
"the PHASE 1 OF 2 comment at the end of this profile's rev_grant block" — but the actual
`FieldPermission` element for `rev_escalatedon` (line 587) is present and correct, and the
`-20260907-2` report's own §8 recommendation #3 already anticipated this exact gap ("when phase 2
touches that comment block, correct…"). The functional artefact is right; only the narrative header
above it was not updated to match. Not a defect against any constraint or requirement — logged as a
friction finding (`IMP-0648`) so the comment gets corrected rather than compounding into a third
stale reference.

## 6. Provisioning Verification
Not applicable to this delta — no new security role, group team, or app-sharing surface. Unchanged
from `-3`/`-2` §6.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure
Unchanged from `-20260906-3`'s [§7.1](revitalise-grant-automation-test-report-20260906-3.md#L91)
(A-DS-1 through A-DS-11) — per this dispatch's brief, not re-litigated here. No new Dev Summary §10
row is introduced by this batch; the FieldPermission restoration is a source-level reversal of a
gate-baseline entry, not a new platform assumption.

### 7.2 Verification levels achieved — **do not conflate this build with `-20260907-2`'s deploy history**

| Component | Level claimed (manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Solution package `-20260907-3` (managed + unmanaged) | `V2 — packaged; layout accepted by the packer and by the Microsoft-hosted Solution Checker, content and target-environment acceptance not proven by this build` | **V2 confirmed — this artifact has NOT been deployed anywhere** | `logs/pipeline.log`'s last matching entry is [2026-09-07 04:40](../../logs/pipeline.log), which SUCCEEDED for build `-20260907-2` (Import ID `c185001f-b1aa-f111-aaab-7ced8d43e1b4`) — that import shipped the **workaround state** (missing `FieldPermission`). No log entry names `-20260907-3` or this manifest's `source_commit`/artifact path. Solution Checker ran live for THIS artifact ([`solution-checker/pac-solution-check-stdout.log`](../../build/artifacts/revitalise-grant-automation-20260907-3/solution-checker/pac-solution-check-stdout.log)), 0 findings at every severity | PASS — honestly reported |
| `rev_grant.rev_escalatedon` field security | Fully restored, phase 2 of 2 (complete) | **Confirmed restored by source and by live gate** | §5 above (three-way confirmation) | PASS |

**The distinction this dispatch was asked to be precise about:** DEV currently runs build
`-20260907-2`'s content (the phase-1 workaround, `rev_escalatedon` live without its FieldPermission,
imported twice successfully at 04:35 and 04:40, idempotency proven for THAT content). Build
`-20260907-3` — this artifact, carrying the restored FieldPermission — is packaged and
Solution-Checker-clean but **has not itself been imported to any environment**. Its honest
verification level is **V2**, matching the manifest's own claim. Deploying `-3` to DEV is the next
step, not something already accomplished by `-2`'s deploy.

- Idempotency: N/A for this build's own content — no import of `-20260907-3` has occurred yet.
  (Idempotency IS proven for `-20260907-2`'s workaround content, at 04:35/04:40, but that is a
  different artifact and does not transfer to this one.)
- V4 designer/editor open + save: not reached, correctly not claimed — unreachable before a deploy
  of this build specifically.
- Cross-OS (C-TECH-054): `build_os: Darwin 25.6.0 arm64 (macOS 26.6.2)` per manifest — local run, not
  CI; no cross-OS-specific script newly added this batch — N/A.
- Warnings triaged (C-TECH-055): manifest shows 4 warnings total, 1 resolved, 3 accepted, **0
  untriaged**. Each accepted warning cites a Dev Summary line and is pre-existing/structural
  (npm deprecation, chunk-size re-check against a re-verified budget, and the
  EntityRelationship/EnvironmentVariableDefinition root-component note that grows 1:1 with schema).
  Result: **PASS**.

## 8. Recommendations

1. Proceed to `pipeline-agent` for a DEV deploy of build `-20260907-3`. Only that deploy — not
   `-20260907-2`'s already-successful imports — will confirm the phase-2 restoration clears cleanly
   against the same field security profile that failed with "Object reference not set to an instance
   of an object" on [2026-09-07 00:52](../../logs/pipeline.log) before the workaround existed.
2. Correct the stale "phase-1 build variant … temporarily UNRELEASED" header comment at
   [`FieldSecurityProfiles.xml:467-473`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L467)
   to reflect that all thirteen `rev_grant` columns named there are now released (`IMP-0648`).
3. Once `-20260907-3` imports cleanly to DEV, re-run for idempotency per C-TECH-053, then this batch's
   V-level story is complete end to end (V1 → V2 → V3 → idempotency) for the first time since the
   00:52 failure.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0648 | `source-comment-not-updated-on-phase-completion` | friction | When a phase-1/phase-2 workaround comment names "the end of this profile's rev_grant block" as the place to look, update BOTH ends when phase 2 lands — the header describing the temporary state is as load-bearing as the FieldPermission block itself. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
