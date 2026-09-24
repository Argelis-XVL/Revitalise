# Dev Summary Document — Postcode → Local Authority Reference Table

**Feature Slug:** postcode-lookup
**TAD Reference:** `docs/architecture/postcode-lookup-architecture.md` (Revision 2, reviewer `APPROVED`)
**Date:** 2026-09-23
**Status:** DRAFT (awaiting review)
**WBS task:** `4.6` (`contract/change-orders/CO-004.md`)

---

## 1. Implementation Summary

Built exactly what TAD Revision 2 specifies (increments 1 and 3 of CO-004): a new Dataverse
table `rev_localauthorityregister` (~2,900 rows, postcode outward code → local authority name),
a new global option set `rev_localauthorityresolutionstatus` (4 values, including the new
`Out of UK LA Scope`), an idempotent PowerShell harvester
(`provisioning/dataverse/seed-local-authority-register.ps1`) that pulls the register from ONS's
live ONSPD layer plus two LAD name services with pacing/retry (ADR-005) and dual reconciliation
(ADR-006), and a monthly watcher Cloud Flow (`REVLocalAuthorityRegisterWatch`) that alerts the
process owner when the register needs refreshing. The multi-authority threshold from TAD §13
(reviewer decision, 5%) is seeded as a `rev_setting` row the harvester reads and fails fast
without, per the TAD's own stated default.

**Ground-truth finding made in this dispatch, not anticipated by the TAD:** the sibling intake
flow (`REVIntakeWordPressToDataverse`) already contains a `Find_local_authority_register_row` /
`Derive_local_authority_status` / `Derive_local_authority` sequence — wbs:0.11 (CO-003)'s own
consumption logic, built ahead of this table existing, carrying its own `A-GAA-01`
("entity set name guessed, register table not yet built") and `A-GAA-02` ("register's own option
values 100001-3 guessed, not yet buildable") assumptions. Two things are now verifiable that
were not before this dispatch:

1. **A-GAA-01 can now be closed CONFIRMED**: that flow's guessed entity set name,
   `rev_localauthorityregisters`, is byte-identical to this table's actual, platform-assigned...
   pending A-LAR-05 below (this table has not yet been created in a live environment, so the
   *platform's own* answer is still unconfirmed — but the two documents' guesses at least agree
   with each other, which was not previously true of anything).
2. **The TAD §8 interface obligation is independently confirmed already satisfied**:
   `Derive_local_authority_status`'s final `else` branch collapses ANY unrecognised
   `rev_resolutionstatus` value — including this Revision's new `100004` (`Out of UK LA Scope`)
   — to the same "Not Known" signal value the missing-row and `NI Pending Licence` cases already
   use. This is a genuine default/else, not an enumeration of three literals, so the fourth status
   value this document adds does not silently mis-handle in that flow. **This is wbs:0.11's own
   document's assumption, not this document's — reported here because it is evidence this
   dispatch produced, not because this document owns closing it.**

This is a `CASCADE`-adjacent finding rather than a cascade: it does not block this feature, and
it is reported in this gate's output for lead-agent/pm-agent to route to whichever agent next
touches wbs:0.11's own Dev Summary/TAD assumption register.

**Sub-agent fan-out not performed** — the register table, harvester, watcher flow and role
privilege grants are one tightly-coupled unit around a single ONS query shape and a single set of
resolution rules; splitting across `data-agent`/`automation-agent`/`config-agent` would have
meant re-deriving the same ONS field mapping in three prompts for no isolation benefit
(`IMP-0498` pattern).

---

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `rev_localauthorityregister` | Dataverse table (new) | 6 columns, alternate key on `rev_name` | FR-200–FR-203, FR-208, FR-209 |
| `rev_localauthorityresolutionstatus` | Global option set (new) | 4 values (100001–100004) | FR-202, FR-203 |
| `AllLocalAuthorityRegisters` | Saved view (new) | Troubleshooting view, Operations SubArea | TAD S9 |
| `provisioning/dataverse/seed-local-authority-register.ps1` | Provisioning script (new) | ONS harvest, 10-step pipeline per TAD S5.1 | FR-200, FR-204–FR-207 |
| `src/tests/provisioning/LocalAuthorityRegister.Tests.ps1` | Test (new) | 9 behavioural tests, no live network call | C-TECH-014 |
| `REVLocalAuthorityRegisterWatch` | Cloud Flow (new) | Monthly edition-marker watcher | FR-204, FR-205, NFR-201 |
| `ensure-schema-helpers.psm1` | Provisioning helper (amended) | Added `rev_localauthorityregister` to `Get-RevEntityLogicalNames` | C-TECH-050 |
| `REV Admin.xml`, `REV Service Automation.xml` | Security roles (amended) | Read privilege on new table (deviates from TAD S6.1 — see §6) | C-TECH-040 |
| `AppModule.xml`, `AppModuleSiteMap.xml` | MDA components (amended) | New table reachable under Operations | TAD S9 |
| `Solution.xml` | Solution manifest (amended) | RootComponents for the table, option set and flow | — |
| `dev-auditing-settings.json`, `test-settings.json`, `prd-settings.json` | Deployment settings (amended) | `rev_localauthorityregister` added to `auditedTables`; `LocalAuthorityRegisterMultiAuthorityThresholdPercent` setting row seeded at 5 | C-TECH-064, TAD S13 |
| `revitalise-grant-automation-pipeline.yml` | Pipeline config (amended) | Harvester wired as `post_deploy` in dev/tst_acc/prd, sequencing note for wbs:0.11 (not built here) | TAD S8, S12 |

---

## 3. Data Model Changes

Per TAD §3, exactly as specified: `rev_name` (pk, 4 chars, derived from ONSPD's `PCDS` only —
ADR-007), `rev_localauthorityname` (100 chars, null unless `Resolved` — ADR-003),
`rev_ladcode` (20 chars), `rev_ladnamesource` (20 chars, `LAD26_EW` | `LAD25_UK` — new in
Revision 2, ADR-004), `rev_resolutionstatus` (picklist, 4 values), `rev_lastseeninsource`
(date only). Alternate key `rev_localauthorityregister_name` on `rev_name`.

**One design decision the TAD's §3 does not pin down, made here:** for a `Multi-Authority` row,
`rev_ladcode` is populated with the MODAL (largest-share) authority's code, for provenance —
`rev_localauthorityname` still stays null per ADR-003. For `NI Pending Licence` and
`Out of UK LA Scope`, both `rev_ladcode` and `rev_ladnamesource` are left null (BT's underlying
LAD is deliberately never surfaced, per FR-203's licence-ground withholding; the pseudo-codes are
not real LAD codes at all). This is a modelling choice within the TAD's silence, not a guessed
platform fact, so it is not an `A-nnn` row — flagged here for the reviewer to confirm or override.

---

## 4. Automation / Workflow Changes

`REVLocalAuthorityRegisterWatch` (new): monthly `Recurrence` trigger, one `Http` GET of the
ONSPD layer root, a `ListRecords` read of `rev_setting`, an `If` comparing the two, a 1:1 Teams
chat prompt on a mismatch (ADR-015), and the same `Find_the_failed_action` →
`Describe_the_failure` → `Alert_on_failure` failure path every other flow in this solution uses
— extended with the `If`-descent pattern (`IMP-0109`) because `Check_source_edition`'s own child
is itself a container. Verified clean by `scripts/verify-flow-definition-language.py` (initially
caught one real defect — see §11).

---

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `dataverse.auditing.auditedTables` += `rev_localauthorityregister` | dev, test, prd | C-TECH-064 |
| `dataverse.settingRows` += `LocalAuthorityRegisterMultiAuthorityThresholdPercent` = `5` | dev, test, prd | TAD S13, reviewer decision 2026-09-23 |
| `rev_setting` rows `LocalAuthorityRegisterLastRefreshedOn` / `…LastRefreshStatus` / `…SourceEdition` | dev, test, prd | Written by the harvester itself, not seeded |

### Provisioning Scripts

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `provisioning/dataverse/seed-local-authority-register.ps1` | Harvest & upsert the register from ONS | `post_deploy:dev`, `post_deploy:tst_acc`, `post_deploy:prd` | Keyed PATCH on `rev_name` (upsert); re-run reports EXISTS |
| `ensure-schema.ps1` (amended, not new) | Creates the table/option set/key | `environment_prerequisites` (all three envs, already wired — no new step needed since the script is driven by its hand-kept entity list, now including this table) | Existing GET-before-create pattern |

---

## 6. Security Controls Implemented

| Control | Implementation |
|---|---|
| Authorisation | `REV Admin` and `REV Service Automation` both get `prvReadrev_localauthorityregister` (Global). **Deviates from TAD §6.1**, which states Service Automation should hold Create/Read/Write, and names a "REV Base User" role. Neither is buildable as stated: (a) `seed-local-authority-register.ps1` authenticates via the app-only provisioning credential (System Administrator privilege per `knowledge/technology/dataverse.md`), not via this role, so Create/Write would be an unused, unverifiable over-grant — the identical, already-established pattern `rev_citysettlementregister`'s own role entries and `rev_setting` itself use; (b) **no "REV Base User" role exists in `Roles/`** (verified against source before writing these entries) — `REV Admin` is this solution's actual Grant Administrator role, the same substitution `rev_citysettlementregister`'s own role entry already made and documented. **Flagged for reviewer acknowledgement**, same class as the `rev_citysettlementregister` precedent. |
| No new secret | Harvester reuses `PROVISION_APP_ID` + certificate; ONS needs no credential |
| Data classification | No personal data (NFR-202) — confirmed, no `special-category-register.yml` row needed |
| Audit | `IsAuditEnabled=1` on the table; `auditedTables` updated in all three settings files (pre-empting C-TECH-064, per dispatch instruction) |
| Group teams | No change — table access rides the existing `REV Grant Administrators` / service-principal bindings, no new persona |

---

## 7. Known Limitations / Deferred Items

- **The refresh depends on a person acting on a Teams alert** (ADR-002-R2) — accepted trade-off,
  reviewer decision recorded in TAD §13/ADR-002-R2 consequences.
- **A-LAR-02 (Dataverse throughput for ~2,900 keyed upserts)** remains OPEN from the TAD — not
  re-verified in this dispatch (no live environment available); the harvester's per-row upsert
  loop is a straight port of the proven `seed-city-settlement-register.ps1` shape at ~3,394 rows,
  which is evidence in the same direction but not a substitute for timing this specific table.
- **A-LAR-03 (edition-marker stability across a real republication)** remains OPEN — cannot be
  observed until ONS actually republishes.
- **A-LAR-04 (TAD §12.2) — RESOLVED 2026-09-24, source-only, no environment needed.** Test-agent's
  report (`docs/tests/postcode-lookup-test-report.md` §7.1) narrowed this from a rule-level trace to
  the sampled-execution comparison TAD/Dev Summary themselves specify; run and closed in
  `docs/architecture/postcode-lookup-architecture.md` §12.2 — 12 real UK postcodes spanning 2/3/4-char
  outward codes plus BT and three formatting edge cases, zero divergence between the harvester's
  `Get-OutwardCode` and the intake flow's `Compute_outward_code`.
- **wbs:0.11's own `A-GAA-01`/`A-GAA-02` assumptions** are now partly answerable from this
  dispatch's ground truth (§1) — routing note for whichever agent next touches that document,
  not a defect in this one.
- **Mixed pseudo-code + real-LAD outward code** (an outcode whose unit postcodes include BOTH a
  UK LAD and a Crown Dependency pseudo-code) is not observed to occur in ONSPD's postal geography
  (Isle of Man/Channel Island outward codes are administratively disjoint from UK ones), and the
  harvester's resolution logic filters pseudo-codes out before applying the modal/threshold rule
  — but this has not been checked against the live 1.8M-row dataset in this dispatch. Low risk,
  not registered as an `A-nnn` (it is an edge-case-frequency question, not a platform-contract
  guess), noted here for completeness.

---

## 8. Build Instructions

No new solution or artifact type: this feature ships inside the existing
`RevitaliseGrantAutomation` solution. **No new `config/postcode-lookup-build.yml` was created** —
every prior feature added to this same solution (wbs:4.7/CO-007, wbs:6.9, wbs:8.3, …) has amended
the shared `config/revitalise-grant-automation-build.yml` in place rather than creating a
parallel per-slug config, and `scripts/verify-build-config.py` is written against that
convention (it requires every `verify-*`/`--check`-shaped script under `scripts/` to be wired as
a step in ONE config — a fresh per-slug file fails that check by construction, having none of
the other 83 steps). The shared build config's existing generic steps (`audited-tables`,
`assumption-markers`, `assumption-register`, `provisioning-test-presence`,
`flow-definition-language`, `role-privilege-ownership`, `field-length-limits`, …) already scan
the whole solution/repository and required no new step for this feature — confirmed by running
`python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` (PASS, 84
steps / 65 gates) and `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml`
(16/16 source gates green — see §11 for what that run actually caught).

**Sequencing (reviewer decision, 2026-09-23, TAD S8): the harvester must run before wbs:0.11's
columns go live in each environment.** This document adds the harvester as a `post_deploy` step
in `config/revitalise-grant-automation-pipeline.yml` for dev/tst_acc/prd, each carrying an
explicit comment naming the constraint — but does **not** place wbs:0.11's own steps relative to
it, per the dispatch instruction ("state the ordering, don't build the deploy ordering
yourself"). **pipeline-agent must enforce the relative order once wbs:0.11's own pipeline-config
change lands.**

---

## 9. Test Guidance

`LocalAuthorityRegister.Tests.ps1` (9 tests, all passing, `pwsh` + Pester 5.7.1) covers: threshold
read-first-and-fail-fast; single-LAD resolution with LAD26 name join; LAD25 fallback
(`rev_ladnamesource`); BT withholding (name join skipped even though a name is available);
pseudo-code → `Out of UK LA Scope`; multi-authority threshold boundary (exactly at the seeded 5%);
exact-reconciliation failure aborting the whole run; a LAD resolving in neither name service
aborting the whole run; and the ADR-005 400-retry-with-backoff path. No test makes a live network
call — `Invoke-RestMethod` is mocked for both the ONS and Dataverse hosts via the existing
`ProvisioningTestHarness.psm1`, which routes purely on method + URI regex regardless of host.

**For test-agent:** the harvester's live behaviour against the real ONS endpoint (query shape,
volume, timing) is NOT exercised by this test file by design (per `knowledge/technology/testing-tools.md`)
— that is what A-LAR-01 (TAD, RESOLVED) and A-LAR-02/03/06 (OPEN, this document) cover instead.

---

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim | Where in source | Evidence | Why not verified | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-LAR-05 | `rev_localauthorityregister`'s `EntitySetName` is `rev_localauthorityregisters` | `Entities/rev_localauthorityregister/Entity.xml` | E4 (pattern-matched from every other custom table in this solution, all of which pluralise by appending `s`) | Dataverse assigns the entity set name; not confirmed against a live environment | `EntityDefinitions(LogicalName='rev_localauthorityregister')?$select=EntitySetName` after the first DEV `ensure-schema.ps1` run | OPEN |
| A-LAR-06 | ONS's ONSPD/LAD26/LAD25 FeatureServer base URLs (org id `ESMARspQHYMw9BZ9`) and the exact query shapes in `seed-local-authority-register.ps1`/`REVLocalAuthorityRegisterWatch` are correct and stable | `provisioning/dataverse/seed-local-authority-register.ps1` (default URLs), `src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json` (`Get_ONSPD_edition_marker`) | E2/E3 — the org id was independently confirmed via web search against `geoportal.statistics.gov.uk`; this dispatch's own attempt to re-query the live endpoint directly (beyond the TAD's own Revision 2 live measurement) returned a tool-side error rather than a live JSON response, so it is NOT re-confirmed live in this dispatch | The fetch tool available in this session could not complete a raw JSON GET against the ArcGIS FeatureServer; the TAD's own Revision 2 claims a live measurement from an earlier dispatch, which this dispatch could not independently re-execute | Run the harvester with `-Env dev` against a real DEV environment and confirm the bootstrap/harvest/name-join calls succeed and the edition marker reads as a plausible date | OPEN |
| A-LAR-07 | The `Http` action type's `method`/`uri`/`retryPolicy` shape (used by `REVLocalAuthorityRegisterWatch`'s `Get_ONSPD_edition_marker`) packs, imports and executes correctly — no flow in this solution had previously used a raw `Http` action | `src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json` | E2 — confirmed against Microsoft's own published Workflow Definition Language / Logic Apps schema reference (`learn.microsoft.com/azure/logic-apps/workflow-definition-language-schema`, `.../logic-apps-workflow-actions-triggers`), fetched in this dispatch | Documented schema, not a live import/execution against a real tenant | V4: open and save this flow in a real environment's flow designer; V5: let it run once and confirm the HTTP call succeeds | OPEN |

---

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `rev_localauthorityregister` Entity.xml, option set, role XML, AppModule/SiteMap, Solution.xml | V1 (well-formed, internally consistent) | macOS (this session), pwsh 7 | `pwsh -NoProfile -Command "Import-Module Pester -RequiredVersion 5.7.1; ... Invoke-Pester -Configuration $c"` over `src/tests/provisioning` — 740 passed, 0 failed, 1 skipped (pre-existing, unrelated) |
| `REVLocalAuthorityRegisterWatch` flow definition | V2 (packages / passes source gates) — **not V3/V4** | macOS (this session) | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` → OK, 10 flows, no new EXCEPTION. **First run caught a real check-7 defect** (own container-descent gap) — fixed, re-run clean. `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` — 16/16 green. **First run of this gate caught 5 real `field-length-limits` violations** (a top-level flow `description` and 4 action `description`s over the 256-char designer save limit) — all condensed and fixed; second run 16/16 green, confirming the fix and demonstrating exactly the value `run-source-gates.py`'s own header describes (a defect caught before build, not after). |
| `seed-local-authority-register.ps1` | V2 (parses, passes `ScriptContract.Tests.ps1`'s mechanical rules) — **not V3/V4/V5** | macOS, pwsh 7.x | Same Pester run above; `LocalAuthorityRegister.Tests.ps1` (9/9 passing) exercises the script's logic with `Invoke-RestMethod` mocked, never against a live ONS endpoint |
| `config/revitalise-grant-automation-build.yml` (amended by reference only — no new steps needed) | — | macOS | `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` → PASS, 84 steps, 65 gates |
| `config/revitalise-grant-automation-pipeline.yml` (amended) | — | macOS | `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` → PIPELINE CONFIG PREFLIGHT: PASS, 122 steps across 3 environments (pre-existing ACCEPTED baselines only, no new ones introduced) |

**Human open-and-save (V4): NOT YET PERFORMED.** No live environment credential was exercised in
this dispatch (see A-LAR-06/07). This must happen before the first real deployment, per
C-TECH-053 — recorded here rather than silently assumed.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| 5× `field-length-limits` violation (flow/action `description` over 256 chars) | `run-source-gates.py` first run | Resolved | Condensed every offending description to under the limit; longer reasoning moved to the flow's `.notes.md` sibling |
| 1× `flow-definition-language` check-7 `ERROR` (own flow's `Describe_the_failure` not descending into a nested container) | `verify-flow-definition-language.py` first run | Resolved | Rewrote `Describe_the_failure` as an `If` that descends into `Source_moved_or_never_harvested` via `result()`, mirroring `REVIntakeWordPressToDataverse`'s own `IMP-0109` fix |
| C-TECH-055 build halt: `config/revitalise-grant-automation-pipeline.yml` lines 573 and 1880 still said "the 21 rev_setting rows" after CO-004/TAD §13 added `LocalAuthorityRegisterMultiAuthorityThresholdPercent` to `dataverse.settingRows` in all three deployment-settings files (dev-scoring, test, prd — each now 22 entries) | Build dispatch (`revitalise-grant-automation` build-agent, concurrent) surfaced the drift; logged as `IMP-0856`, class `hand-maintained-count-drifts-from-source`, severity `rework` | Resolved (this dispatch) | Both lines corrected to "the 22 rev_setting rows"; `python3 scripts/verify-derived-counts.py` re-run — the `pipeline-rev-setting-row-count` claim no longer drifts (0/3 source files disagree). Four unrelated pre-existing drifts remain in the same run's output (secured-column-count ×3, known-failure-modes digest line count) — out of this dispatch's scope (not touched by CO-004/TAD §13), reported as WARN per the gate's own SOFT severity, not fixed here |

### Diagnostic components created and removed (C-TECH-056)

None — no live environment was touched in this dispatch.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| none | — | — | No new finding met the six capture triggers this dispatch — the two defects caught (§11) were caught and fixed by the EXISTING gates working exactly as designed, which is the gates succeeding, not a gap to log |

Digest regenerated: NO — no improvement-log entry was written this dispatch.

---

## Code Review Checklist
- [x] All FR IDs covered (FR-200–FR-209, NFR-200–NFR-202 — increments 1 and 3 only, per CO-004)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented (with one documented, precedented deviation — §6)
- [x] Every TAD §12 item has an idempotent provisioning script wired into `config/revitalise-grant-automation-pipeline.yml`
- [x] Role assignments via existing roles only — no direct user assignments
- [x] No hardcoded environment-specific IDs/URLs (the ONS URL is a public, environment-invariant literal — see harvester header and flow notes.md for why that is not a C-TECH-047 violation)
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (A-LAR-05, A-LAR-06, A-LAR-07)
- [x] Where an environment existed — none did in this dispatch; ground truth was instead obtained via web search + Microsoft Learn schema lookup, both recorded honestly as E2/E3, not claimed as live verification
- [x] Every platform limit the packer/compiler does not enforce has a build gate (`field-length-limits`, `flow-definition-language`, already in the shared config, confirmed to catch this feature's own real defects)
- [x] Verification levels in §11 are the levels actually executed, not the levels expected
- [x] Scripts run on the CI runner's OS — pure PowerShell 7, no OS-specific API
- [x] Every tool warning triaged in §11; no diagnostic components left anywhere
- [ ] Accessibility requirements — N/A, no UI component
- [x] No dead code or debug statements (temporary debug instrumentation used while diagnosing the Pester test harness was removed before this Dev Summary was written — verified by diff against the pre-debug backup)
- [x] Unit tests written (`LocalAuthorityRegister.Tests.ps1`, 9/9 passing)

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
