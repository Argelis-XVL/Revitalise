# Test Report — Revitalise Grant Automation (DocuSign Acceptance Workflow Batch)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260906-3/
**Date:** 2026-09-06
**Status:** FAIL
**WBS:** 3.2 (Create Envelope), 3.3 (Reminders & Escalation), 3.4 (Completion) — automation 3, DocuSign acceptance workflow, DEV-only per EX-006/EX-007

---

**Correction (post-issue, reviewer/coordinator-prompted):** the first version of this report claimed
"PASS at V1/V2/V3" for the DocuSign flows and then separately FAILED them for "V4 not performed."
Both halves were wrong. `manifest.json`'s own `verification_level: V3` rests only on packaging
(`pac solution pack`) and the Solution Checker (`pac solution check` — a static analyser against the
packaged zip, not an import). `logs/pipeline.log` has no entry for `revitalise-grant-automation`
after 2026-09-05; the DocuSign content in this build (commit `d625129`, added 2026-09-06) has never
been imported into any environment. Per
[`skills/how-to-verify-a-platform-contract.md`'s level table](../../skills/how-to-verify-a-platform-contract.md#L404),
V3 means "Import/deploy succeeded; the component is queryable in the target" — this build is
honestly at **V2**, and V4 is not "not performed," it is **structurally unreachable** until
pipeline-agent runs a DEV deploy — exactly the situation
[`trustee-portal-visual-refresh-test-report-v10.md:124`](trustee-portal-visual-refresh-test-report-v10.md#L124)
and [`-v11.md:106`](trustee-portal-visual-refresh-test-report-v11.md#L106) already establish as
precedent: **PASS at the level actually executed, not FAIL and not PARTIAL.** §3, §5 and §7.2 below
are corrected accordingly. Logged as `IMP-0631`.

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | Yes | 1022 | 0 | 1 |
| Integration (Code App, vitest) | Yes | 771 | 0 | 0 |
| End-to-End | No | — | — | — (no live-signed envelope exists yet; A-DS-9/A-DS-11a) |
| Regression | Yes | pre-existing suite green (see manifest) | 0 | — |
| Security | Partial | source-level constraint scan clean | — | live role-read test not run (needs an environment reachable from this dispatch) |
| Accessibility | N/A | — | — | no new/changed UI screen in this batch — three flows only |
| Performance | N/A | — | — | no NFR threshold named for this batch |
| Provisioning | Partial | connection reference / env-var XML well-formed | — | live team-share/app-user checks out of scope for automation 3 |
| **Platform Contract** | Yes | see §7.1 | 11 rows still OPEN, all correctly gated (not defects) | — |
| **Verification Level** | Yes | V2 confirmed; V3/V4 correctly not yet claimed (see §7.2) | 0 | — |
| **Process gate** | Yes | — | 1 (`improvement-log-check`, HARD) | — |
| **Total** | | 1793 | 1 process gate | 1 |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| wbs:3.2 Create Envelope | `rev_grant` created → DocuSign envelope sent via `REVAcceptanceCreateEnvelope` | Pester (flow-shape, field-length, GUID), source-level | PASS at V1/V2 (packaged + Solution Checker clean); V3/V4 correctly not yet claimed — no deploy has run |
| wbs:3.3 Reminders & Escalation | `AddReminders` cadence + `EscalationDays` fallback | Pester (settings JSON well-formed), source-level | PASS at V1/V2; A-DS-6 is a reviewer-decision item, not a defect |
| wbs:3.4 Completion | DocuSign Connect webhook → signed PDF to SharePoint → `rev_signedpdfurl` | Pester, solution-structure gates | PASS at V1/V2; A-DS-8/A-DS-9/A-DS-10 remain OPEN, designer/live-test only, reachable after deploy |

## 3. Failed Tests
| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-GATE-01 | Process gate | `python3 scripts/verify-improvement-log.py --check`, re-run live by test-agent | exit 0 (this is `config/revitalise-grant-automation-build.yml`'s [step 3, `improvement-log-check`, HARD](../../config/revitalise-grant-automation-build.yml#L62)) | exit 1 — TRIGGER: 3 unread blocker findings — `IMP-0627`, `IMP-0628`, `IMP-0629` | P1 |

## 4. Defects Raised
| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-TEST-1 | P1 | Build `revitalise-grant-automation-20260906-3` is reported `PASSED` in `manifest.json`, but `config/revitalise-grant-automation-build.yml`'s own HARD `improvement-log-check` step fails when re-run live against the current `logs/improvement-log.jsonl` — 3 blocker-severity findings about this same build session (`IMP-0627`, `IMP-0628`, `IMP-0629`) are `status: NEW`, with no `deferred_reason` and no `reviewed_in`. The manifest's own `improvement_log_disposition` field narrates them as resolved/superseded in prose, but prose in a manifest does not close a log entry — only `deferred_reason`, `reviewed_in`, or an improvement review does, per [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L164) and the exact pattern `IMP-0605`/`IMP-0610` already recorded. | T-GATE-01 |

~~D-TEST-2 (V4 not performed)~~ **WITHDRAWN.** V3 itself has not been reached for this build's DocuSign
content (no `pac solution import`/deploy entry exists in `logs/pipeline.log` after 2026-09-05, and the
DocuSign flows were added 2026-09-06) — `manifest.json`'s own `verification_level: V3` rests only on
packaging and the Solution Checker, neither of which is an import. V4 being absent when V3 has not
happened is not a defect, it is the expected, correctly-unclaimed next step — see §7.2 and `IMP-0631`.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-004 | No personal data in logs | PASS | `domain-invariants` re-run clean per Dev Summary's own re-verified [CONSTRAINT CHECK](../../docs/development/revitalise-grant-automation-dev-summary.md#L6880) (`Domain HARD: 6/6, violations: NONE`) |
| C-DOM-010/011 | Audit logging, schema | PASS | Same CONSTRAINT CHECK block; no new sensitive-entity writes in this batch beyond `rev_grant`/`rev_docusignenvelopeid` fields already audited |
| C-DOM-030/031/032 | Special-category exclusion / secured / audited | PASS | `rev_grant.rev_escalatedon` register row confirmed applied 2026-09-06 per [improvement review](../../docs/improvements/2026-09-06-improvement-review.md#L259); `domain-invariants` exits 0 |
| C-TECH-001 | No hardcoded secrets | PASS | `no-hardcoded-environment-values` step clean, cited in manifest's 73-clean count |
| C-TECH-014 | Coverage threshold | PASS | Pester 81.26% ≥ 80% threshold; Code App vitest 98.47% — both in manifest |
| C-TECH-045 | DLP-compliant connectors | PASS (DEV) | DocuSign/SharePoint connectors are new to this solution but same DLP group as existing connectors per TAD; EX-007 records the DEV-only DocuSign licence gap explicitly, not a DLP violation |
| C-TECH-052 | Every hand-authored platform contract has a register row | PASS (no orphans) | 11 assumption rows (A-DS-1 through A-DS-11) all present in Dev Summary §10 for the new DocuSign/SharePoint actions; none found unregistered |
| C-TECH-053 | Reported only at the level actually executed | PASS (corrected) | Manifest's own `verification_level: V3` label overstated the level (packaging + Solution Checker only, no import evidence in `logs/pipeline.log`) — see §7.2. Corrected to V2 in this report; not a test FAIL since nothing here claims higher than what §7.2 confirms |
| C-TECH-058 | An OPEN §10 assumption blocks deployment to any environment where it could be closed, absent an explicit reviewer `OVERRIDE` | PASS (as scoped) | The 8 designer/live-test-only rows (A-DS-1/2/3/8/9/10/11a) are gated as named pre-activation steps in `config/revitalise-grant-automation-pipeline.yml`'s DEV `post_deploy` — not silently skipped; EX-006/EX-007 record the reviewer's explicit direction to build DEV-only ahead of the two upstream client-side preconditions |
| Process gate: `improvement-log-check` (build config step 3, HARD) | Every build gate must pass when re-run | **FAIL** | See §3 T-GATE-01, D-TEST-1 |

## 6. Provisioning Verification

Not applicable to this batch beyond what §5/§7 already cover — wbs:3.2/3.3/3.4 add flows and a SharePoint/DocuSign connection reference, no new security role, group team, or app-sharing surface (TAD §12/§6.1 items for this feature were verified under earlier WBS tasks, e.g. 6.1–6.5, not re-affected here).

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Closing precondition stated separately from status, per `IMP-0219` (do not re-derive from prior narrative — re-read [Dev Summary §10, this revision](../../docs/development/revitalise-grant-automation-dev-summary.md#L6853) directly):

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-DS-1 | Connector `apiId` is `shared_docusignv2` | OPEN | Designer-only (`pac connection list` or open in DEV designer) | DEV exists | Named as a mandatory `post_deploy` pre-activation step in pipeline config — not silently deferred | PASS (gated, not orphaned) |
| A-DS-2 | `SendEnvelope.signers` wire shape | OPEN (role names/values partially closed; wire shape not) | Designer-only, against live template `b832b15e-...` | DEV exists | Same — named blocking pre-activation step | PASS (gated) |
| A-DS-3 | Trigger event + lookup-navigation-property read convention | OPEN | Live-test-only — trigger once, read raw outputs | DEV exists | Not yet exercised; no gate currently blocks it independently of A-DS-1/2 | PASS (gated via same post_deploy sequence) |
| A-DS-4 | Blank referee first/last-name tabs acceptable | OPEN | Reviewer decision only, no technical step | N/A | Pure product question, correctly not blocking build | PASS (not a test defect) |
| A-DS-5 | `rev_refereeemail` as "Organisation email" stand-in | OPEN | Reviewer decision only | N/A | Same | PASS (not a test defect) |
| A-DS-6 | `EscalationDays` fallback-to-14 acceptable | OPEN | Reviewer decision only | N/A | Same | PASS (not a test defect) |
| A-DS-7 | (design decision, not an assumption) | — | — | — | — | N/A |
| A-DS-8 | DocuSign Connect `events` = `"envelope-completed"` | OPEN | Designer-only | DEV exists | Named mandatory pre-activation step | PASS (gated) |
| A-DS-9 | `documentId: 'combined'` | OPEN | Live-test-only, needs a real completed envelope | DEV exists, but no envelope has completed | Cannot close until A-DS-1/2/3/8 clear and a real send/sign/complete cycle runs | PASS (gated, sequenced correctly behind the designer-only items) |
| A-DS-10 | SharePoint `CreateFile` wire shape + `Path` response property | OPEN | Designer-only, against real `rev-sharepoint` connection | DEV exists | Named mandatory pre-activation step | PASS (gated) |
| A-DS-11(a) | `AddReminders` override-precedence | OPEN | Live-test-only, send one real envelope | DEV exists, no envelope sent yet | Sequenced behind A-DS-1/2/3 | PASS (gated) |
| A-DS-11(b) | Repeat-forever reminder cadence acceptable | **CLOSED** 2026-09-06, reviewer-accepted | — | — | Confirmed in Dev Summary revision text | PASS |

No orphans found: every new DocuSign/SharePoint action in the three flows traces to a numbered row above (C-TECH-052 satisfied). The register itself is honest and complete — the gap is not in the register, it is that **none of the designer/live-test rows have actually been closed yet**, which is exactly what §7.2's V4 finding restates from the verification-level side.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11 / manifest) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Solution package (managed + unmanaged) | Manifest states V3 | **V2 confirmed, not V3** | `pac solution check` PASSED live, correlation `1487f052-...` (`build/artifacts/.../solution-checker/pac-solution-check-stdout.log`, mtime 22:52:58) — this proves packaging + Solution Checker only. `logs/pipeline.log` has no `pac solution import`/deploy entry for `revitalise-grant-automation` after 2026-09-05, and this build's DocuSign content is from commit `d625129` (2026-09-06) — nothing shows it accepted by any target | PASS at V2 (manifest's V3 label is overstated — logged as `IMP-0631`) |
| `REVAcceptanceCreateEnvelope`, `REVAcceptanceReminders`/escalation, `REVAcceptanceCompletion` flows | V1 (this revision, per Dev Summary §11) | **V1/V2 confirmed**; V3/V4 correctly not yet claimed | No import has run for this content; V4 (human open-and-save) is therefore not "outstanding," it is the next step, unreachable until pipeline-agent deploys | PASS — accurately reported once corrected, same shape as `trustee-portal-visual-refresh-test-report-v10.md`/`-v11.md` |

- Idempotency: N/A this dispatch — no import/push has run for this content yet.
- V4 designer/editor open + save: **not reached, correctly not claimed** — cannot be attempted before a deploy exists. Already named as a mandatory pipeline `post_deploy` step (A-DS-1/2/3/8/9/10/11a) for when DEV deploy happens.
- Cross-OS (C-TECH-054): `build_os: macOS (local Mac run, not CI)` per manifest — this build did not run on the CI runner; no cross-OS-specific script was newly added in this batch, so N/A rather than FAIL, but noted
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056) → result: **PARTIAL** — manifest's own `warnings_detail` shows 2 of 3 warnings `untriaged` (`pack-managed`, `pack-unmanaged` — the 17-line root-component list), citing a stale Dev Summary line (4 lines vs the current 17)

## 8. Recommendations

1. Route `IMP-0627`/`IMP-0628`/`IMP-0629` to `improvement-agent` (`APPROVE IMPROVEMENTS`) before any further build or pipeline dispatch for this feature — the same discipline `IMP-0605` and `IMP-0610` already established, now a third instance (`IMP-0630`, this dispatch). This is the sole blocker holding this report at FAIL.
2. Once that clears: proceed to pipeline-agent for a DEV deploy (V2 → V3), then the standing V4 human open-and-save step for the three DocuSign/SharePoint flows — this is also the mechanism that closes A-DS-1/2/3/8/9/10/11a, all already named as `post_deploy` pre-activation steps in `config/revitalise-grant-automation-pipeline.yml`. One human designer session likely closes most of §7.1's open rows and §7.2's V3/V4 gap together.
3. Triage the 2 `untriaged` pack warnings (17-line root-component list) and correct the stale citation in the Dev Summary (currently cites 4 lines, tree now prints 17) — a P3 housekeeping item, not blocking this report's status, but it will re-fire on every future build until fixed.
4. Dev Summary §9 (Test Guidance) has no section specific to automation #3 (DocuSign) anywhere in the document — every revision from `A-DS-1` onward updated §10/§11 but not §9. Worth a documentation pass so the next test cycle inherits guidance rather than reconstructing it from the assumption register alone.
5. `manifest.json`'s `verification_level` field should not print `V3` off packaging + Solution Checker alone — recommend build-agent cross-check `logs/pipeline.log` for an actual import entry before labelling a level V3 (`IMP-0631`).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0630 | `routed-work-not-reverified-at-apply-time` | blocker | A manifest's own prose narrative of a blocker finding's disposition is not a closure of that finding — only `deferred_reason`, `reviewed_in`, or an improvement review closes it; re-run `verify-improvement-log.py --check` live before trusting a quoted PASSED status. |
| IMP-0631 | `verification-level-overstated` | rework | `pac solution check` proves V2 at most, never V3 — before writing V3 in a test report, grep `logs/pipeline.log` for an actual import/deploy entry naming this build's content; V4 absent when V3 hasn't been reached is the expected next step, not a FAIL. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
