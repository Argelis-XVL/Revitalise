# Test Report — Applicant form: missing Ethnic Group control

**Feature Slug:** applicant-ethnicgroup-form-defect
**Artifact:** build/artifacts/applicant-ethnicgroup-form-defect-20260905-5/
**Date:** 2026-09-05
**Status:** PASS (at the level this artifact can be tested — build/static/constraint layers only; V3–V5 belong to pipeline-agent, see §7.2)

---

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (Pester) | 1023 | 1022 | 0 | 1 |
| Unit (Code App vitest) | 1022 | 1022 | 0 | 0 |
| Integration (schema/form cross-reference) | 2 | 2 | 0 | 0 |
| End-to-End | 0 | — | — | N/A — requires deployed environment, out of test-agent scope this cycle |
| Regression (Pester full suite) | 1023 | 1022 | 0 | 1 |
| Security | 0 | — | — | N/A — no auth/role surface changed |
| Accessibility | 0 | — | — | N/A — standard Model-Driven App picklist control, no custom UI |
| Performance | 0 | — | — | N/A — no NFR threshold engaged by a single form cell |
| Provisioning | 0 | — | — | N/A — no provisioning script change |
| Compliance (domain invariants) | 4 | 4 | 0 | 0 |
| **Total** | 2074 | 2072 | 0 | 2 |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-061 | Trustee-portal ethnic-group distribution chart, which needs applicant data to exist | Control-placement + type cross-check (this report §7.1); data-entry itself is V4/V5, deferred to pipeline-agent | PASS at the level testable pre-deployment |

## 3. Failed Tests
None.

## 4. Defects Raised
None new. See §7.1 for the one pre-existing open item this dispatch does not close.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | Special-category register is the single source; scoring-flow alternation matches it | PASS | Re-ran `python3 scripts/verify-domain-invariants.py` live this session: `DOMAIN INVARIANTS: PASS — 21 special-category column(s) verified`, `C-DOM-030 register ↔ FR-016 gate: in sync (21 names)`. `rev_ethnicgroup` now present at [special-category-register.yml:139](../../constraints/domain/special-category-register.yml#L139) (closed by `IMP-0598`, `status: APPLIED`) |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Every register column carries `IsSecured=1` unless a named exception | PASS | Same live run: `C-DOM-031 column security: 17 secured, 4 documented exception(s)`; `rev_ethnicgroup` `IsSecured="1"` at [Entity.xml:344](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L344), not one of the 4 exceptions |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Every register column carries `IsAuditEnabled=1` | PASS | Same live run: `C-DOM-032 auditing: 21 / 21 enabled`; `rev_ethnicgroup` `IsAuditEnabled="1"` at [Entity.xml:344](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L344). This is a **source-only** check (C-TECH-064 governs the live half — organisation/table audit switches — and is out of scope for a form-surface-only change with no environment write) |
| C-DOM-033 (`IMP-0598`'s own gate) | Every `IsSecured=1` column is in `columns:` or `pending_adjudication:` | PASS | Same live run: `68 secured = 17 registered + 51 pending adjudication, 0 undeclared` |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated ids for platform-assigned components | PASS | New cell id `{49468c72-4079-4547-bd56-4ad1eaf156a9}` is a FormXml cell, not in the enumerated platform-assigns-on-creation list (Role/Field Security Profile/sitemap/app); hand-authored GUIDs are the correct pattern here |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Unvalidated Assumptions Register complete, no orphans | PASS | Dev Summary §10 has one row (A-AEG-1), closed by construction — copied verbatim from three sibling controls already live on the same form, independently confirmed by this report (§7.1) |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Component reported only at the level actually executed | PASS, with a correction | Dev Summary §11 (written before build ran) claims V1 only; the actual build (`build/artifacts/applicant-ethnicgroup-form-defect-20260905-5/manifest.json:17`) packed both zips and passed the live Solution Checker (`0 Critical/0 High/0 Medium/0 Low/0 Informational`), which is genuinely **V2**. Reported here at the corrected, current level — see §7.2 |
| [C-TECH-055](../../constraints/technology/technology-constraints.md) | Tool warnings triaged | PASS | `logs/build.log` 2026-09-05 18:11 entry confirms both real warnings (glob@10.5.0, pack-managed 14-line notice) are now cited with matching prior-accepted rationale in Dev Summary §11 (closing `IMP-0609`) |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every build gate proven able to fail | PASS | `preflight-build-config PASS — 73 steps, 57 gates, all with negative-test coverage` (manifest.json:16) |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD schema/access tables checked against source | PASS | Dev Summary §11 cites `verify-tad-coverage.py` OK, 174 §3.1 columns matched, re-affirmed unchanged by this form-only edit |
| [C-TECH-078](../../constraints/technology/technology-constraints.md#L148) | Rendered-geometry claims measured in a real browser | PASS / N-A for this change | `code-app-visual-tests` step ran 2/2 Chromium tests passed (unrelated to this MDA form change, which introduces no code-app geometry) |
| C-COM-002 | Work enters by WBS task id | PASS | This entire dispatch is scoped to [WBS 0.4](../../contract/wbs.json#L224) per Dev Summary header; no undeclared scope found |

No HARD constraint failure. No P1/P2 defect open.

## 6. Provisioning Verification
N/A — no TAD §12 or §6.1 item changed by this dispatch (Dev Summary §5/§6: "None").

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-AEG-1 | `{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}` is the correct control classid for `rev_ethnicgroup`, matching Gender/Age Range/Applicant Type | CLOSED by construction | N/A — ground truth from the same file | Yes | **Independently re-verified, not merely accepted.** [FormXml/main/{5cb234cc...}.xml:9](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/FormXml/main/%7B5cb234cc-f4af-4e97-a024-c71b7da66399%7D.xml#L9) declares `control id="rev_ethnicgroup" classid="{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}" datafieldname="rev_ethnicgroup"`, placed between the `rev_gender` and `rev_dateofbirth` rows in `sec_identity`. Cross-checked against [Entity.xml:336-349](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_applicant/Entity.xml#L336): `<Type>picklist</Type>`, `<OptionSetName>rev_ethnicgroup</OptionSetName>`, `IsSecured="1"`. Cross-checked against [OptionSets/rev_ethnicgroup.xml](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_ethnicgroup.xml): `<OptionSetType>picklist</OptionSetType>`, six ONS-style options + "Prefer not to say" — same shape as `rev_gender`'s own picklist and its identical control classid on the same form. Field security profile `REV_TrusteeRestricted` at [FieldSecurityProfiles.xml:200](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L200) already releases `rev_ethnicgroup`, unchanged by this dispatch. This is a **matched, correctly-typed control**, not merely well-formed XML | **CLOSED, confirmed** |

**Orphan check (C-TECH-052):** none found — the one hand-authored contract this dispatch introduces (the FormXml cell) has its register row, and it is closed on the same ground truth cited above, not on inference.

**Standing item not closed by this dispatch, correctly:** [IMP-0597](../../logs/improvement-log.jsonl) (the finding this fix responds to) is deliberately left `NEW`/open per its own `deferred_reason` — the gate (`C-TECH-077` + `verify-forms-and-views-reachable.py` form-surface-coverage check) is proven in both polarities, but the V4 re-observation it requires (a named reviewer entering a test applicant with an ethnic-group value on the **deployed** DEV form, and confirming the value reaches the FR-061 chart) cannot happen from this session — no environment write occurred here. This is **not** a test-agent finding to log fresh; it is the correct, already-recorded state, and its `revisit_when` names exactly what pipeline-agent's post-deploy step must do next.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| FormXml well-formedness | V1 | V1 | `xml.etree.ElementTree.parse` clean (re-run) | PASS |
| Form/option-set/entity cross-reference | V1 | V1 | `verify-forms-and-views-reachable.py` and `verify-tad-coverage.py` both OK (Dev Summary §11); independently re-confirmed by direct XML read in §7.1 above | PASS |
| Solution pack + live Solution Checker | Dev Summary said **NOT PERFORMED** | **V2 — actually reached**, by the later real build | Both zips present in `build/artifacts/applicant-ethnicgroup-form-defect-20260905-5/`; `solution-checker/pac-solution-check-stdout.log` reports `0 Critical / 0 High / 0 Medium / 0 Low / 0 Informational` (correlation `92557282-a160-4977-90b2-143cff563d5a`); Pester 1022/0 failed/1 skipped, code-app 1022/1022, per `logs/build.log` 2026-09-05 18:15 SUCCESS entry and this artifact's own files | **Reported at the corrected level, PASS** |
| Solution import (V3) | NOT PERFORMED | **NOT PERFORMED** | No `pac solution import` in `logs/pipeline.log` for this artifact | Correctly not claimed — pipeline-agent's next step |
| Human open-and-save in designer (V4) | NOT YET PERFORMED | **NOT YET PERFORMED** | No maker-session evidence exists | Correctly not claimed |
| Live data entry for a trustee (V5) | NOT YET PERFORMED | **NOT YET PERFORMED** | Depends on V3/V4 | Correctly not claimed — this is the reviewer's original ask, and it is out of test-agent's scope; it belongs to pipeline-agent next |

- Idempotency: N-A this dispatch — no live deploy attempted (build-only artifact); pipeline-agent's re-run-once rule applies at its own dispatch.
- V4 designer/editor open + save: **NOT YET PERFORMED** — result: `FAIL if claimed complete; correctly NOT claimed here`.
- Cross-OS (C-TECH-054): N-A — no new script, `Invoke-Pester` ran on this Mac, matches CI runner family (PowerShell/pac cross-platform tooling, no OS-specific API touched).
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS — both warnings triaged with rationale (Dev Summary §11); no diagnostic components created.

**Why this artifact is a source-level artifact, not a duplicate of the solution-checker path in `revitalise-grant-automation-20260905-1`:** the checker log's own printed path names that other directory because this build was originally resolved and populated under the wrong `--feature` argument, then the whole directory was renamed to the correct `applicant-ethnicgroup-form-defect-20260905-5` — a known, already-logged and closed finding (`IMP-0611`, severity `friction`, "no content lost, directory renamed"), not a fresh evidence-mismatch defect. Confirmed by reading `IMP-0611` directly rather than assuming.

## 8. Recommendations

1. **Hand this artifact to pipeline-agent for DEV deployment (V3), then the named V4 step** — a signed-in maker/reviewer opens the Applicant main form, confirms "Ethnic Group" renders between Gender and Date of Birth, sets and saves a value, and confirms it appears only to a `REV_TrusteeRestricted`-exempt/holding user.
2. **After deployment, re-observe `IMP-0597`** exactly as its own `revisit_when` specifies: enter a test applicant with an ethnic-group value on the deployed DEV form and confirm it reaches the FR-061 distribution chart. This is the reviewer's original ask and is out of this report's scope by design.
3. No dev fixes needed — the source-level fix is correct and ground-truthed against the option-set, entity, and field-security definitions it depends on, not merely well-formed.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This session found no new gap: the one apparent anomaly (solution-checker log naming a different artifact directory) resolved to an already-logged, closed finding (`IMP-0611`) on inspection, and the register gap (`IMP-0598`) was already applied. Nothing here needed a fresh entry. |

Digest regenerated: NO — no new entry to regenerate for.
