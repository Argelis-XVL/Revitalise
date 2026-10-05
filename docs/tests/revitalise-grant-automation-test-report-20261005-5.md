# Test Report — Revitalise Grant Automation, build 20261005-5 (Create Envelope hotfix reconciliation, referee columns, TAD rev 16/17)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261005-5/
**Date:** 2026-10-05
**WBS:** wbs:3.2, 4.2, 4.3 (this report is the test evidence for the Create Envelope work under 3.2; it is not the 3.5 sign-off, which needs a run)
**Status:** PARTIAL

**Conclusion.** Nothing in source is wrong: 1329 Pester tests, 790 + 888 Code App tests, 19 of 19 source gates and a further 27 build gates all pass when re-run here, and the packed flow is byte-identical to source. The result is PARTIAL and not PASS because nothing has been executed in DEV: the corrected Create Envelope flow has never run, the designer open-and-save step has not been done, and six DocuSign assumptions are still open. No P1 or P2 defect is open. Three small defects (P3) should be fixed before the commit.

---

## 1. Test Summary

All counts are from runs made by test-agent on 2026-10-05, not copied from the build log (the build's own 1329 / 0 / 1 matches).

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — Pester (all of `src/tests`, includes envelope contract 69, intake 158, scoring, provisioning) | 1330 | 1329 | 0 | 1 |
| Unit — Code App vitest, trustee-review-portal | 790 | 790 | 0 | 0 |
| Unit — Code App vitest, trustee-review-portal-cards | 888 | 888 | 0 | 0 |
| Static — `tsc --noEmit`, both apps | 2 | 2 | 0 | 0 |
| Source gates (`run-source-gates.py`) | 19 | 19 | 0 | 0 |
| Further build gates re-run by name (shipped-content, tad-coverage x2, flow-definition-language, variant-parity, derived-counts, assumption register/markers/ids, audited-tables, doc-line-links, others) | 27 | 27 | 0 | 0 |
| Generator `--check` (21 entries, both app copies) | 2 | 2 | 0 | 0 |
| Mutation probes (my own, see 3.1) | 13 | 11 caught | 2 survived* | 0 |
| Integration / End-to-End / Performance / Accessibility | — | — | — | not run: needs DEV (section 8) |
| Security (run-history masking, column security) | static only | pass | 0 | live half needs DEV |
| Provisioning (TAD 12 items on a live org) | — | — | — | not run: needs DEV |

*One survivor was a scripting error in my probe (an action name I mistyped), the other is defect D-1 below.

## 2. Requirement Coverage

| Requirement | Test case(s) | Result |
|---|---|---|
| FR-041 (two signatures, sent on approval) | `AcceptanceEnvelopeContract.Tests.ps1` chain, bind and send tests | Covered at source level. DEV run needed. |
| FR-042 (second signer) | No-routing-order test ([AcceptanceEnvelopeContract.Tests.ps1#L214](../../src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L214)) | Covered. Known doc lag: SDD says "in sequence"; TAD rev 16 overrides by reviewer ruling. Not a defect. |
| R1 failure lookup (three new cases) | Container-count pin, case-per-container test ([#L386](../../src/tests/solutions/AcceptanceEnvelopeContract.Tests.ps1#L386)); removing a case fails one test and the flow-language gate | Structure covered. The cases are never executed against a failed run (needs DEV). |
| R2 / D-2 secure data on 42 actions | Closure test, named-action test, 13 + 9 single-action removals | Covered, except the three new failure-lookup queries (D-1). |
| Escalation card (R3) | `verify-shipped-content.py` | PASS. |
| Provisioning text (R4) | Provisioning Pester suite, text read in `ensure-schema.ps1` | PASS. |
| ADR-070 referee columns | `domain-invariants`, `field-security-coverage`, `tad-coverage`, type lock, generator `--check`, packed `customizations.xml` | PASS: eight columns secured and audited in both packed solutions. |
| Backfill dropped | grep of repo: no reference left outside history documents; git shows the script deleted | PASS. |
| TAD rev 16/17 (TD-006, TD-011 removed; TD-007 re-dated) | `tad-coverage` and `tad-coverage-cards` | PASS. TD-007 expires 2026-10-19. |

## 3. Failed Tests

None.

### 3.1 What the mutation probes showed

I removed one setting at a time from a copy of the flow, ran the envelope suite, and restored the file (SHA-1 identical before and after). Eleven removals were each caught by at least one test. One was not: the secure-data setting on the three new queries inside the failure-lookup cases (D-1).

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-1 | P3 | The three new `Find_the_failed_step_inside_*` queries are secured in source and TAD 5.8, but removing that setting leaves all 69 envelope tests green. The test walks only top-level actions. The four older cases' queries are unsecured, which is undecided rather than wrong. Logged as [IMP-1049](../../logs/improvement-log.jsonl). | none exists |
| D-2 | P3 | Both Code Apps' `fieldCatalogue.test.ts` credit the eight referee columns to CO-008 ([trustee-review-portal L22](../../src/code-apps/trustee-review-portal/src/domain/fieldCatalogue.test.ts#L22), [L60](../../src/code-apps/trustee-review-portal/src/domain/fieldCatalogue.test.ts#L60); same lines in the cards app). CO-008 is the duplicate-grant check and is unapproved. The columns belong to ADR-070. Logged as [IMP-1050](../../logs/improvement-log.jsonl). | n/a (comment and test title) |
| D-3 | P3 | The Create Envelope notes file still says "Routing 1 / 2" in its rev 15 sequence table ([notes.md#L429](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06.notes.md#L429)) and lists `Fill_the_tabs`. Only one list line was corrected; the no-routing-order test reads action descriptions, not this file. Logged under the same finding as D-2. | n/a |

None of these blocks deployment. All three are comment, title or notes text, plus one missing assertion.

## 5. Constraint & Compliance Verification

Scope: rows naming test-agent that this change touches. Rows outside this change are not re-judged here.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS | `domain-invariants` gate (in the 19); run history masked on 52 actions, 47 inputs and outputs, 5 inputs only |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column reaches scoring | PASS | `no-special-category-data-in-scoring` and the 42-column pin test |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns secured | PASS | Eight new columns carry IsSecured 1 in the packed solution, both zips; 42 secured on `rev_application` |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns audited | PASS (source only) | Packed attributes show auditing on; the live switch is C-TECH-064 and is a post-deploy check |
| [C-DOM-033](../../constraints/domain/domain-constraints.md#L95) | Every secured column adjudicated | PASS | Eight rows added to `special-category-register.yml` |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No secrets in source | PASS | `secret-scan` step exit 0 |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | 82.79% against 80.0% (build manifest; not re-measured here) |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Platform contracts in the register | PASS | Register and marker gates exit 0; A-DS-14 to A-DS-19 all have rows, no orphans found |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Level claimed equals level reached | PARTIAL | Highest reached is V2 (packed). Nothing is V3, V4 or V5. The build manifest and Dev Summary both say V1/V2, which is correct |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI OS | NOT VERIFIED | All runs here and in the build were on macOS. The only script changed is the Python generator, which uses no OS-specific API; not exercised on the Linux runner |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest: 10 warnings, 10 accepted, 0 untriaged. Solution Checker: 1 Medium, 0 Critical or High |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | No diagnostic components shipped | PASS | The hotfix's removed `secureData` is restored; no diagnostic action found in the 107 actions |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate can fail | PASS | Generator `--selftest` proves a stale second copy fails; removing a failure-lookup case fails both a test and the flow-language gate |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumptions block deployment | PASS for DEV, BLOCKS later environments | A-DS-14 to A-DS-18 are OPEN and name a DEV run as their check, so they do not block the DEV deploy but do block TST/ACC |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | Text length limits | PASS | `field-length-limits` gate; referee address 250, postcode 10 |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD tables are a checked specification | PASS | `tad-coverage` and `tad-coverage-cards` exit 0 |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Counts derived from source, or annotated | SOFT NOTE | The 34 to 42 pin and the 13 to 21 / 10 to 18 catalogue counts were fixed by retyping a bigger number. They are annotated with a reason, so the gate passes, but this is the 47th instance of the class |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Secured column shapes | PASS | Eight plain `nvarchar` columns, no calculated or platform-owned shape |

## 6. Provisioning Verification

Not run. Every TAD 12 and 6.1 item needs a live org. The one new provisioning duty is TAD 12.1: TST/ACC and PRD need `ensure-schema.ps1` run for the eight referee columns before the flow is imported there.

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

All six rows are in [Dev Summary section 10, rev 16 rows](../development/revitalise-grant-automation-dev-summary.md#L12651). Closing precondition for each is the same two facts: this build imported into DEV, and one Create Envelope run on it.

| Assumption ID | Claim (short) | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-DS-14 | Draft holds both roles; update fills, not adds; send sends the draft | OPEN | This build in DEV, one run | DEV exists; this build is not in it | Source shape and operation order only | OPEN, not closeable before deploy |
| A-DS-15 | Tab recipient ids equal signer ids; prefill flag; document id | OPEN | Same | Same | Both id spellings tested against fixtures | OPEN |
| A-DS-16 | Tab spelling, language, reminders, organisation tab | OPEN | Same | Same | Which form each call sends, by test | OPEN |
| A-DS-17 | Six-digit code accepted and required by the link | OPEN | Same, plus a signing link opened | Same | Static only | OPEN |
| A-DS-18 | Reassignment off is inherited | OPEN | Template setting read in DocuSign | DocuSign account exists | None | OPEN |
| A-DS-19 | Template routing order | CLOSED, not applicable | Reviewer ruling | n/a | No `routingOrder` in either bind or in the packed flow (the two text hits are descriptions) | CLOSED |

No orphans: the marker, register and id-collision gates exit 0.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Create Envelope flow, referee columns, catalogue, tests, scripts | V1 source, V2 packaged | V2 | Packed flow equals source byte for byte; both zips contain the eight secured, audited columns | Confirmed at V2 |
| DEV flow baseline (Dev Summary section 0) | V5-read | Not re-read by me | Read-only DEV check was made by development-agent; I did not repeat it | Not re-verified |
| Corrected Create Envelope run | not claimed | V0 for the corrected flow | Never run | PARTIAL |

- Idempotency: deploy re-run against an already-deployed target: NOT RUN (nothing deployed).
- V4 designer open and save, then re-read live: NOT PERFORMED. Required: this flow has failed to save in the DEV designer before (2026-09-25, 2026-10-03). Owner: the reviewer.
- Cross-OS (C-TECH-054): NOT VERIFIED on the CI runner.
- Warnings triaged and diagnostics removed (C-TECH-055, C-TECH-056): PASS.

## 8. Checks that need DEV, left for post-deploy

1. Import this build into DEV, then run `verify-live-flow-definitions.py --env dev`: the flow must equal source, now including the 52 `secureData` settings (DEV runs the unsecured version today).
2. Open Create Envelope in the DEV designer, save, and re-read live (V4). Owner: reviewer.
3. One approved grant to test mailboxes: both signers emailed together (R7), access code asked for on the link (A-DS-17), tabs correct (A-DS-15, A-DS-16), organisation tab shows the company, template reassignment off (A-DS-18).
4. One deliberate failure per new container (empty tabs, mismatched signer, company-tab fill) to see the alert name the leaf action; and confirm run history shows no names, emails, phones or tab values.
5. `ensure-schema.ps1` on DEV for the eight referee columns; confirm secured, audited, and that only the process owner and service profile can read them (C-TECH-064, C-TECH-068).
6. Confirm the DEV intake still writes `rev_fullname` and `rev_costs` for a new submission (the existing rows stay NULL by decision).
7. Re-run the Code App parity and visual checks against DEV data if the catalogue change is to be shown to trustees.

## 9. Recommendations

- Fix D-1 to D-3 in a development-agent pass before commit; none needs a rebuild of the platform artefacts except D-2's test titles, which affect the Code App test files only.
- TD-007 expires 2026-10-19. If CO-008 is not decided by then the next build halts at `tad-coverage` again.
- The SDD FR-041/FR-042 wording is a known lag; plan-agent should align it so the next review does not rediscover it.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1049 | `no-assertion-on-shipped-content` | friction | A secure-data test that walks only top-level actions cannot see Query actions nested in Switch cases; walk every nested action. |
| IMP-1050 | `wrong-artefact-cited-as-evidence` | friction | Cite the decision record whose scope names the thing (ADR-070), not the change order raised the same day. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
