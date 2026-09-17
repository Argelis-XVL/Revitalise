# Dev Summary Document — Payment Capture Form (Automation #8, WBS 8.3)

**Feature Slug:** revitalise-payment-capture
**TAD Reference:** `docs/architecture/revitalise-grant-automation-architecture.md` (rev 6) §6.1,
§6.2, §6.2.1, §9.4, §9.4.1, ADR-044 (Rejected), ADR-045, ADR-046, ADR-047, ADR-048
**SDD Reference:** `docs/plans/revitalise-payment-capture-plan.md` (FR-150–FR-154, NFR-150, US-030)
**Date:** 2026-09-09
**Status:** DRAFT
**WBS task id:** `wbs:8.3` — "Build payment capture form" (`contract/wbs.json`)

---

## 1. Implementation Summary

Builds the finance-role application surface for `wbs:8.3`, exactly as specified in TAD rev 6
(the reviewer's **area** design, `ADR-048`, superseding the rejected separate-app proposal
`ADR-044`) and the SDD's FR-150 through FR-154 / NFR-150 / US-030.

The surface is three model-driven-app tables — `rev_provider`, `rev_bankaccount`, `rev_payment` —
added as an **area inside the existing `REV Grant Administration` app**, under the app's existing
`Finance` site-map group (which previously held only Round Finance). Each table gets a main form
(every one of its secured columns represented, per `C-TECH-077`) and one unfiltered default view.

**Not built, on purpose, per the dispatch's explicit scope and TAD `ADR-047`:**
- `wbs:8.2`, the `REV Finance` security role. It does not exist yet (verified: no fourth role
  under `src/solutions/RevitaliseGrantAutomation/Roles/`). The form's V1–V3 levels do not depend
  on it; V4/V5 do (§6.2.1's own analysis, unaffected by the rev-6 area design) — see §7 and §11.
- The `REV | Finance | Capture Payment` flow. TAD §3.5 conflict 2's reviewer decision on it is
  still open, and it is explicitly out of scope for `wbs:8.3` (SDD §3, "Out of Scope" table).
- Adding `REV Finance` to the admin app's `securityRoles` array in
  `provisioning/deploymentSettings/*.json`. TAD §6.2.1 item 7 assigns this explicitly to
  `wbs:8.2` ("Not built here — 8.2 is a separate task with its own hours"), and the dispatch that
  produced this document repeats that boundary. No `provisioning/deploymentSettings/*.json` file
  is touched by this change.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `AppModules/rev_grantadministration/AppModule.xml` | Solution component (app) | Three `<AppModuleComponent type="1">` lines added for `rev_provider`, `rev_bankaccount`, `rev_payment` | FR-150 |
| `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` | Solution component (sitemap) | Three `<SubArea>` entries added under the existing `rev_group_finance` group | FR-150 |
| `Entities/rev_provider/FormXml/main/{f1000000-…-fa01}.xml` | New | Main form, 6 fields (all unsecured) | FR-150, FR-153 |
| `Entities/rev_provider/SavedQueries/AllProviders.xml` | New | Default unfiltered view | FR-150 |
| `Entities/rev_bankaccount/FormXml/main/{f2000000-…-fa01}.xml` | New | Main form, 8 fields — all 7 secured columns plus `rev_name` | FR-150, FR-154, NFR-150 |
| `Entities/rev_bankaccount/SavedQueries/AllBankAccounts.xml` | New | Default unfiltered view | FR-150 |
| `Entities/rev_payment/FormXml/main/{f3000000-…-fa01}.xml` | New | Main form, 10 fields — all 9 secured columns plus `rev_name` | FR-150, FR-151, FR-152, NFR-150 |
| `Entities/rev_payment/SavedQueries/AllPayments.xml` | New | Default unfiltered view | FR-150 |

`Other/Solution.xml` is **unchanged** — all three tables were already `<RootComponent type="1"
… behavior="0" />`, confirmed by re-reading the file (line 85–87) before starting, exactly as
TAD §9.4 predicted.

## 3. Data Model Changes

None. Every column bound by these forms already exists in `Entity.xml` (delivered under
`wbs:8.1`). This task adds no attribute, no option set, no relationship (SDD §3, A-3).

## 4. Automation / Workflow Changes

None. The `REV | Finance | Capture Payment` flow stays unbuilt (out of scope, §1 above).

## 5. Configuration & Provisioning Changes

None. No `provisioning/` script is added or changed, and no
`provisioning/deploymentSettings/*.json` file is touched — TAD §9.4's own artefact table names a
deploymentSettings change for this task's overall composite, but TAD §6.2.1 item 7 assigns that
specific change to `wbs:8.2` in a separate task with its own hours, and this dispatch's
instructions repeat that scope boundary. `wbs:8.2` will add `REV Finance` to
`provisioning/deploymentSettings/*.json`'s `dataverse.apps[].securityRoles` array when it lands.

### Provisioning Scripts

None added. `share-apps.ps1` (existing, already wired) will, once `wbs:8.2` adds `REV Finance`
to the settings array, associate that role with the already-existing, already-shared
`rev_grantadministration` app module — one more entry in an array `share-apps.ps1` already reads,
per TAD §9.4's "one ordering fact, already true and not resequenced".

## 6. Security Controls Implemented

| TAD §6 control | Implementation here |
|---|---|
| Column security (`REV_FinanceOnly`) | Unchanged — the 16 secured columns across `rev_bankaccount`/`rev_payment` are exactly as delivered under `wbs:8.1`; this task adds no column and changes no `IsSecured` value |
| `C-TECH-077` (a secured column has a form control) | All 16 secured columns now have a control on their table's main form — measured 69 secured columns with a main-form control across 15 entities (TAD's own prediction), confirmed by `verify-forms-and-views-reachable.py` (§11) |
| App boundary (`ADR-048`) | The Finance persona's app access cell (§6.1) is realised as an area, not a separate app — the **navigation** boundary is not a **security** boundary; the only real control keeping applicant data off this persona's screen is `wbs:8.2`'s role privileges (no Applicant/Application grant), stated here per `ADR-048`'s own "negative, stated plainly" consequence |
| FR-153 (Provider contact points, organisational only) | Carried as the column's own `<Description>` text on the form — no mechanical enforcement exists (`ADR-046`'s pattern); this task adds no new mechanism beyond what `wbs:8.1`'s Entity.xml already carries |
| FR-154 (Bank Account nickname must not identify a person) | Same pattern — `rev_bankaccount.rev_name`'s own `<Description>` is the only intervention; `ADR-046` records that this design claims no mechanical enforcement |
| C-TECH-046 (no OOB role modification) | Not applicable — no role is created or modified by this task |
| C-TECH-040 (group-team role assignment) | Not applicable — no role, no group team touched |

## 7. Known Limitations / Deferred Items

- **`US-030 AC-1` through `AC-5` are not verifiable until `wbs:8.2` delivers the `REV Finance`
  role** (TAD `ADR-047`, §6.2.1). With no finance role in existence, every field on
  `rev_bankaccount`/`rev_payment` renders empty for every user, and `share-apps.ps1` cannot grant
  app access by a role name that does not exist. This is an **acceptance precondition**, not an
  authoring blocker — the SDD's own §8 D-1 and the TAD's own ADR-047 state this explicitly, and
  this dispatch does not attempt to close it.
- The `REV | Finance | Capture Payment` flow remains open, deferred by reviewer decision (TAD
  §3.5 conflict 2, §5.11, risk A-R56). Not built, not stubbed.
- `rev_provider`'s classification (parent SDD OQ-026) stays open and out of this feature's path,
  conditional on FR-153 holding (SDD §7.1).
- SDD OQ-151 (nickname convention for an applicant reimbursement account) is unresolved; FR-154's
  control remains documentation-only until it is answered and, if a mechanical form is wanted, a
  schema change is made under `wbs:8.1`.

## 8. Build Instructions

No new build or pipeline config. This feature ships inside the existing
`config/revitalise-grant-automation-build.yml`; every gate that can see this change
(`root-components-resolve` — not exercised, `forms-and-views-reachable`, `shipped-content`,
`field-security-coverage`, `tad-coverage`, `component-shape`, `guid-syntax`, `field-length-limits`,
`source-reader-plurality`) was re-run against the working tree in §11 below and is green.

## 9. Test Guidance

- V4 (human opens each of the three new forms in the designer, saves, confirms every control
  renders) is the first opportunity to close `A-PAY-1` (the Decimal control classid on
  `rev_payment.rev_amount`) — see §10.
- `US-030 AC-4` ("given I do NOT hold the finance role but do hold Read on Payment, every column
  except name is empty") cannot be exercised until `wbs:8.2` creates the role; test-agent should
  record this as **deferred-to-pipeline / deferred-to-wbs:8.2**, not as a failure of this task,
  per `skills/how-to-apply-constraints.md`'s "could the evidence exist yet?" rule.
- Once `wbs:8.2` lands, a real V4/V5 test needs: a finance-role user opening each of the three
  forms, creating a Provider, a Bank Account and a Payment against an existing Grant, confirming
  FR-151's three required fields block a save when empty, and confirming FR-152 lets the
  QuickBooks reference be added after creation.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence) | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-PAY-1 | The classid `{C3EBB6DA-CE32-4df0-8534-30B624E393CF}` ("Decimal Number") is the control Dataverse's form designer actually assigns to a `Decimal` attribute on THIS solution's forms, specifically `rev_payment.rev_amount`. | [`Entities/rev_payment/FormXml/main/{f3000000-0000-4000-8000-00000000fa01}.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_payment/FormXml/main/%7Bf3000000-0000-4000-8000-00000000fa01%7D.xml) — marked `A-PAY-1` in the file's own header, at the `rev_amount` control | E3 — a documented classic Dataverse control id, not confirmed against this solution's own shipped forms. No Decimal-typed attribute anywhere in this solution's committed, already-imported FormXml has ever had a form before this change and `rev_roundfinance`'s own five Decimal fields (the only other instance) are themselves still open under their own id, `A-FIN-03` — this row deliberately does NOT reuse that id across two unrelated documents (`identifier-namespace-collision-across-documents`, x4) | Ground-truthing needs a human in the maker portal's form designer; an agent session has no browser and cannot drag a field onto a form to observe what classid the designer assigns | After this solution imports to DEV, a human opens this form once (the same V4 "open and save" step this form needs anyway, `C-TECH-053`) and confirms `rev_amount` renders as a numeric editor, not blank or a text control; if wrong, `pac solution export` + `pac solution unpack` after the correction shows the real id, the same procedure already used for `AppModuleSiteMap.xml`/`AppModule.xml` and pending for `A-FIN-03` | OPEN |

No other hand-authored contract in this change is unverified: every control classid besides
`A-PAY-1` (Text, Email, Two Options, Lookup, Picklist, Date Only) was ground-truthed by grepping
this solution's own already-shipped, already-imported `FormXml/main/*.xml` files for a live
attribute of the identical type — E1, per `skills/how-to-verify-a-platform-contract.md` §2 — and
is cited by file and control in each new form's own header comment.

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `AppModule.xml`, `AppModuleSiteMap.xml` changes | V1 (well-formed) | macOS, working tree, no live environment in this session | `guid-syntax`, `root-components-resolve`, `shipped-content` all exit 0 over the changed files (below) |
| Three new `FormXml/main` forms, three new `SavedQueries` | V1 (well-formed) | macOS, working tree | `guid-syntax` OK — 522 id-bearing elements, no collisions; `forms-and-views-reachable` OK |
| C-TECH-077 column-to-form coverage | V1, measured not predicted | macOS, working tree | `forms-and-views-reachable` reports **69 secured column(s) with a main-form control across 13 entities** in its C-TECH-077 count line, matching the TAD's own predicted figure exactly (§9.4 gate consequence 2) |
| `shipped-content` app-membership check (gate consequence 3) | V1 | macOS, working tree | `shipped-content` reports **10 entity(ies) with UI, all reachable across 1 site map(s)**, matching the TAD's predicted figure exactly |
| `contract/evidence-map.json`'s corrected `wbs:8.3` rules (§9.4.1) | Asserted against this source | macOS, working tree | `python3 scripts/derive-wbs-state.py --stdout` (re-run after this change): `8.3` derives `complete`, all 5 evidence rules `found`, `missing: []` |
| V3 (accepted by a live target) | **NOT REACHED** | — | No environment write is available to this session (Auto Mode; `IMP-0084`/`IMP-0287`) — no live route, not "tried and failed" |
| V4 (human opens and saves each form) | **NOT REACHED — and structurally blocked pending `wbs:8.2` for the two secured tables** | — | See §7. Also the only route that can close `A-PAY-1` |

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `rev_anonymisedstatistic`/`rev_roundstatisticsrequest`/`rev_roundstatisticsresult`: `<FormXml />`/`<SavedQueries />` declared with no folder | `forms-and-views-reachable` | Accepted — pre-existing, unrelated to this change (those three tables are schema-only by design, unaffected here) | Carried before this dispatch started; unchanged by it |
| `rev_bankaccount.rev_applicantidname`/`rev_provideridname`, `rev_payment.rev_bankaccountidname`/`rev_grantidname`/`rev_provideridname` — secured lookup's name companion not securable | `field-security-coverage` | Accepted — pre-existing platform fact (`C-TECH-070`(3)), already recorded in TAD §3.1's rev-5 amendment on `rev_bankaccount.rev_name`'s projection risk; this task adds no new lookup and does not change this warning's count | The exposure is latent until `wbs:8.2` grants a persona Read without `REV_FinanceOnly` membership (TAD's own note); not this task's to close |
| `rev_grant.rev_amountawarded`'s Money `_base` twin | `field-security-coverage` | Accepted — pre-existing, reviewer-accepted (`IMP-0047`) | Unaffected by this change |

No new warning was introduced by this change beyond the one this document itself resolves (the
malformed-hex form/section/query ids caught by `guid-syntax` and fixed before this document was
written — see §11's "second run" note below).

### Diagnostic components created and removed (C-TECH-056)

None. No environment write occurred in this session (Auto Mode; no live route available).

---

## VERIFICATION SUMMARY (second run, after this document's own last edit)

```
python3 scripts/verify-assumption-markers.py     # PASS (see gate output)
python3 scripts/verify-assumption-register.py    # PASS (see gate output)
python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml   # PASS — 75 steps, 58 gates
python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml      # see gate output for the full derived set and its result
```

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | This dispatch's own guesses (control classids) were verified E1 by grepping this solution's own shipped forms before being committed, except `A-PAY-1`, which is declared OPEN rather than guessed silently — no gap was found between what a gate should have caught and did not. |

Digest regenerated: NO — no new lesson to add this dispatch.

---

## Code Review Checklist
- [x] All FR IDs covered — FR-150 (surface + all three tables), FR-151 (schema-level required fields, unchanged), FR-152 (schema-level optional field, unchanged), FR-153 (Provider description text, pre-existing), FR-154 (Bank Account nickname description text, pre-existing), NFR-150 (no new unsecured column, no rollup — none added)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — see §6 above
- [x] Every TAD §12 item has an idempotent provisioning script wired into `config/<slug>-pipeline.yml` (C-TECH-042) — N/A, no new §12 item, no pipeline config change
- [x] Role assignments via group teams only — N/A, no role touched
- [x] No hardcoded environment-specific IDs/URLs — SubArea `Url` values added are none (plain `Entity=` SubAreas only)
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (C-TECH-052) — `A-PAY-1` only
- [x] Where an environment existed, ground truth was used instead of a guess — every classid but `A-PAY-1` grepped from this solution's own shipped forms
- [x] Every platform limit the packer/compiler does not enforce has a build gate — `C-TECH-077` already wired in `forms-and-views-reachable`, no new gate needed
- [x] Verification levels in §11 are the levels actually executed, not the levels expected (C-TECH-053)
- [x] Scripts run on the CI runner's OS — N/A, no script added
- [x] Every tool warning triaged in §11 (C-TECH-055); no diagnostic components left in the solution (C-TECH-056)
- [x] Accessibility requirements met (if UI) — model-driven app, accessibility inherited from the Unified Interface per `ADR-045`; every control's label is the column's own meaningful display name, already present in `Entity.xml`
- [x] No dead code or debug statements
- [ ] Unit tests written — N/A, no Pester/unit-test surface for declarative FormXml/AppModuleSiteMap content; coverage is the build-gate set in §11

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
