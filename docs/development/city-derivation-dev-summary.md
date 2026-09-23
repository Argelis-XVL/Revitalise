# Dev Summary Document — Postcode → City Reference Lookup

**Feature Slug:** city-derivation
**TAD Reference:** docs/architecture/city-derivation-architecture.md
**Date:** 2026-09-23
**Status:** DRAFT

---

## 1. Implementation Summary

`wbs:4.7` (CO-007, EF-03). A new Dataverse reference table, `rev_citysettlementregister`, holds
one row per UK postcode outward code (3,394 rows, measured directly from
`docs/Import/Postcode Details.xlsx`, sheet `Postcodes`), mapping the outward code to its
*Main Postal Town / City*. It is seeded once, per environment, by a new provisioning script —
never by a Cloud Flow (TAD ADR-003) — and read by the existing intake flow
(`REVIntakeWordPressToDataverse`) via a new `ListRecords` lookup step inserted immediately after
`Derive_location_area`. The result is written to a new secured column, `rev_applicant.rev_derivedcity`,
and a miss (outward code not in the register) is folded into the existing
`Derive_intake_review_note` Compose action as a fourth `concat()` clause (TAD ADR-004) — no new
flow action, branch, or write. `rev_derivedcity` is secured under `REV_TrusteeRestricted`,
matching its neighbours `rev_towncity`/`rev_locationarea` (TAD ADR-005).

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `Entities/rev_citysettlementregister/Entity.xml` | New table | Two columns (`rev_name` outward code, `rev_cityname`), alternate key on `rev_name`, OrganizationOwned, no option set (ADR-002), no relationships | FR-220–FR-222 |
| `Entities/rev_citysettlementregister/SavedQueries/AllCitySettlementRegisters.xml` | New view | Default view, `rev_name`/`rev_cityname` columns | TAD S9 |
| `Entities/rev_citysettlementregister/FormXml/main/{...71}.xml` | New form | Minimal 2-field read-only main form | TAD S9 |
| `Entities/rev_applicant/Entity.xml` | New column | `rev_derivedcity`, nvarchar(100), `IsSecured=1` | FR-224 |
| `Entities/rev_applicant/FormXml/main/{5cb234cc-...}.xml` | Form control | Read-only `rev_derivedcity` control added to `sec_contact`, next to `rev_localauthoritystatus` (C-TECH-077) | — |
| `Other/FieldSecurityProfiles.xml` | New FieldPermission | `rev_derivedcity` added to `REV_TrusteeRestricted` | ADR-005 |
| `Other/Solution.xml` | RootComponent | `rev_citysettlementregister` (type 1) | — |
| `AppModules/rev_grantadministration/AppModule.xml` | AppModuleComponent | `rev_citysettlementregister` added (IMP-0090 discipline — SubArea alone is not enough) | TAD S9 |
| `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` | SubArea | `rev_sub_citysettlementregister` under the existing **Operations** group | TAD S9 |
| `Workflows/REVIntakeWordPressToDataverse-....json` | Flow steps | `Lookup_city_register`, `Derive_city` inserted after `Derive_location_area`; `Derive_intake_review_note` extended (4th clause); `rev_derivedcity` write added to both `Refresh_existing_applicant` and `Create_new_applicant` | FR-221, FR-222, FR-224, FR-225 |
| `Workflows/REVIntakeWordPressToDataverse-....notes.md` | Notes | Entries for `Lookup_city_register`/`Derive_city`, including A-CSR-01 | — |
| `Roles/REV Admin/REV Admin.xml` | Privilege | `prvReadrev_citysettlementregister` (Global) | TAD S6.1 |
| `Roles/REV Service Automation/REV Service Automation.xml` | Privilege | `prvReadrev_citysettlementregister` (Global) only — see §6 deviation note | TAD S6.1 |
| `provisioning/dataverse/ensure-schema-helpers.psm1` | Hand-kept list | `rev_citysettlementregister` appended to `Get-RevEntityLogicalNames` | C-TECH-050 |
| `provisioning/dataverse/seed-city-settlement-register.ps1` | New script | One-off idempotent seed: 3,394 register rows + 2 `rev_setting` provenance rows | TAD ADR-003, S5.1 |
| `provisioning/dataverse/data/city-settlement-register.csv` | New data file | Converted once, offline, from `docs/Import/Postcode Details.xlsx` | TAD S4 |
| `config/revitalise-grant-automation-pipeline.yml` | Pipeline wiring | `seed-city-settlement-register.ps1` added to `post_deploy` for dev/tst_acc/prd | — |

## 3. Data Model Changes

Per TAD §3. `rev_citysettlementregister` (new, OrganizationOwned, no relationships): `rev_name`
(outward code, max 4, primary name, alternate key `rev_citysettlementregister_name`),
`rev_cityname` (max 100, always populated for every row that exists — a miss is the absence of a
row, ADR-002). `rev_applicant` gains `rev_derivedcity` (max 100, `IsSecured=1`, populated by the
intake flow only, `null` on a register miss). No new global option set (contrast with the sibling
postcode-lookup register — ADR-002). Two new `rev_setting` rows (`CitySourceFile`,
`CitySourceCapturedOn`), data not schema.

**Ground-truthed against the actual source file, not the TAD's paraphrase of it** (re-measured in
this dispatch, independently of the TAD's own §1 measurement, using `openpyxl` against
`docs/Import/Postcode Details.xlsx`, sheet `Postcodes`): 3,394 data rows, header row
`Postcode District | Main Postal Town / City | Postcode Area | County / Broad Area | Region |
Country`, zero blank city values, zero duplicate outward codes, max outward-code length 4, max
city-name length 20. Confirms every measurement the TAD's §1 states.

## 4. Automation / Workflow Changes

Two new steps in `REVIntakeWordPressToDataverse`, inserted immediately after
`Derive_location_area` (TAD S5.2's stated sequencing point):

1. **`Lookup_city_register`** — `ListRecords` against `rev_citysettlementregisters`, filtered on
   the alternate key `rev_name` = the outward code `Compute_outward_code` already derived.
2. **`Derive_city`** — `null` on a miss (zero rows), never a guess; otherwise the register row's
   `rev_cityname`.

`Derive_intake_review_note`'s `runAfter` gains `Derive_city` alongside its existing
`Derive_preferred_contact_method` dependency, and its `concat()` gains a fourth clause naming a
city-register miss (`city: outward code "<code>" not found in the city register. `) — the SAME
Compose action, not a new one (ADR-004). `Create_or_refresh_the_applicant`'s two branches
(`Refresh_existing_applicant`, `Create_new_applicant`) both gain
`rev_derivedcity: @outputs('Derive_city')`. `rev_towncity` is untouched in both (FR-228).

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `CitySourceFile` (rev_setting) | dev/test/prd | `Postcode Details.xlsx`, seeded once, never updated (NFR-221) |
| `CitySourceCapturedOn` (rev_setting) | dev/test/prd | `2026-09-16` (delivery date, fixed — not the seed run date) |

### Provisioning Scripts

| Script | Purpose | Pipeline Block (tenant_prerequisites / post_deploy:\<env\>) | Idempotency Check |
|---|---|---|---|
| `provisioning/dataverse/ensure-schema.ps1` (unchanged) | Creates `rev_citysettlementregister`, its two attributes, its alternate key, `rev_applicant.rev_derivedcity`, and the new `FieldPermission` on `REV_TrusteeRestricted` — schema-source-driven, needed only the `Get-RevEntityLogicalNames` list addition | `environment_prerequisites` (already wired per environment) | Existing EXISTS/CREATED/FAILED reporting, unchanged |
| `provisioning/dataverse/seed-city-settlement-register.ps1` (new) | Upserts the 3,394 register rows + 2 `rev_setting` provenance rows | `post_deploy:dev`, `post_deploy:tst_acc`, `post_deploy:prd` | Keyed GET+PATCH per row on the alternate key (C-TECH-042); CSV pre-flight-validated before any write |

## 6. Security Controls Implemented

- **`rev_derivedcity` secured under `REV_TrusteeRestricted`** (TAD ADR-005) — same profile as
  `rev_towncity`/`rev_locationarea`, released to `REV Admin` and `REV Service Automation` only.
  `C-DOM-033` obligation: see the pending-adjudication note below — **this dispatch cannot apply
  it directly** (the protection hook blocks a write to `constraints/`).
- **`REV Admin`**: `prvReadrev_citysettlementregister` (Global) — read-only, for troubleshooting a
  lookup miss from the Operations SubArea. **Naming correction from TAD S6.1**: the TAD's persona
  table names this grant "REV Base User" — no such role exists in `Roles/` (verified against
  source before writing this entry; the actual roles are `REV Admin`, `REV Finance`,
  `REV Service Automation`, `REV Trustee`). The Grant Administrator persona's actual role in this
  solution is `REV Admin`, and that is where the grant was made.
- **`REV Service Automation`**: `prvReadrev_citysettlementregister` (Global) only. **Documented
  deviation from TAD S6.1**, which also lists Create/Write for this role: the intake flow's
  `Lookup_city_register` step only reads the table (TAD S5.2); `seed-city-settlement-register.ps1`
  authenticates as the `PROVISION_APP_ID` service principal, which
  `knowledge/technology/dataverse.md` records as running with System Administrator privilege for
  provisioning writes — the identical reason `rev_setting` carries no
  `prvCreaterev_setting`/`prvWriterev_setting` on this role despite being seeded by a script.
  Granting Create/Write here would be an unused, unverifiable over-grant on the flow's own runtime
  identity. Flagged for reviewer acknowledgement, same class as the pre-existing
  `rev_errorlog` Write deviation already recorded in `REV Admin.xml`.
- **Trustee**: no membership of `REV_TrusteeRestricted`, no privilege on
  `rev_citysettlementregister` — unchanged exclusion (TAD S6.1).

### C-DOM-033 — pending_adjudication entry (BLOCKED for this agent, drafted here)

`rev_derivedcity` carries `IsSecured=1` and must be entered in
`constraints/domain/special-category-register.yml` under `pending_adjudication:` (never
`columns:` — it is a secured quasi-identifier, not Article 9 data, per TAD ADR-005), matching the
pattern its two neighbours `rev_towncity`/`rev_locationarea` already follow there. The write is
correctly refused by `.claude/hooks/protect-system-rules.py` — `constraints/` is
improvement-agent's. Exact entry to add, in the same style as the existing
`# ── Added 2026-09-18 (IMP-0761) ──` block (`constraints/domain/special-category-register.yml`
line 383 for the precedent format):

```yaml
  # rev_applicant.rev_derivedcity — wbs:4.7 (CO-007, EF-03), TAD city-derivation-architecture.md
  # ADR-005. Third location attribute on rev_applicant, mirroring the already-secured
  # rev_towncity/rev_locationarea (2026-09-17 EF-02: trustees see no location at all).
  # Geographic quasi-identifier, not Article 9 data.
  - { entity: rev_applicant, name: rev_derivedcity }
```

**This file already carries two other unresolved entries of this exact class** (`rev_localauthority`,
`rev_localauthoritystatus` — `IMP-0838`, grant-admin-app, still `NEW`/unapplied as of this
dispatch). Logged as `IMP-0843` (blocker) rather than silently skipped, per
`agents/development-agent.md`'s "One refusal to expect" note — **not fixed here**; recommend
applying all three entries together in one improvement-agent pass rather than three separate
ones.

## 7. Known Limitations / Deferred Items

- **No refresh mechanism** (TAD ADR-003, CO-007 Out of Scope) — a future source-file revision
  requires a new, separately-priced WBS item, not an extension of this design.
- **No backfill for applications already on file** (SDD OQ-222, explicit carve-out, out of scope
  for `wbs:4.7`).
- **OQ-220 (alphanumeric London outward codes)** — the client's file has no `EC1A`/`SW1A`-style
  suffixed codes (confirmed by inspection, TAD §11); every such applicant resolves to a
  register miss at a volume not yet quantified. Carried forward, owned by the reviewer.
- **`scripts/verify-tad-coverage.py`'s `C-TECH-066` gate does not scan this sibling TAD by
  default** — same known, already-flagged gap the sibling `postcode-lookup-architecture.md` §11
  and `grant-admin-app-architecture.md` both already carry for their own new/changed tables. Not
  resolved here.
- **No `config/city-derivation-build.yml` / `-pipeline.yml` produced** — see §8. This is the
  established, already-decided precedent (`IMP-0836`, applied by the `grant-admin-app` dispatch),
  not a fresh decision made silently in this one.
- **Seed script per-row log volume** — `seed-city-settlement-register.ps1`'s header records the
  judgement call: the Script Contract's "one line per resource" is honoured literally (3,394 lines
  possible), with a one-line summary printed at the end specifically so a reviewer does not have
  to scroll through all of them. Not resolved as a script-contract amendment in this dispatch.

## 8. Build Instructions

**No `config/city-derivation-build.yml` or `config/city-derivation-pipeline.yml` was produced.**
This is not a fresh decision — it is the same, already-established precedent `IMP-0836` recorded
for the `grant-admin-app` dispatch on this exact question, re-applied here rather than re-derived:
`.github/workflows/ci.yml`'s `SLUG` mechanism and `scripts/verify-build-config.py`'s
`suite-gate-is-not-a-step` check together mean a new feature slug's build config would have to
replicate nearly all of the existing ~1,000/~2,000-line `revitalise-grant-automation-build.yml`/
`-pipeline.yml` to pass its own preflight, and no feature slug other than
`revitalise-grant-automation` has ever had its own config across CO-003 through CO-007.

This change is built and deployed as an addition to the existing `revitalise-grant-automation`
feature build — `config/revitalise-grant-automation-build.yml` (unchanged — every generic gate
this change touches is source-driven and needed no new step) and
`config/revitalise-grant-automation-pipeline.yml` (changed — three new `post_deploy` steps wiring
`seed-city-settlement-register.ps1` into dev/tst_acc/prd, see §5).

## 9. Test Guidance

- **Happy path:** an applicant whose postcode's outward code has a register row →
  `rev_derivedcity` holds the register's `rev_cityname`; `rev_intakereviewnote` unchanged (no
  fourth clause).
- **Miss / unseeded register:** outward code absent from the register (including "register table
  has zero rows because the seed script has not run yet") → `rev_derivedcity` null,
  `rev_intakereviewnote` gains `city: outward code "<code>" not found in the city register. `.
  **This is the case to test FIRST in DEV**, since the register may not be seeded there yet when
  this flow is first tested.
- **Trustee non-visibility (FR-256/ADR-005):** confirm a trustee-authenticated read of
  `rev_applicant` cannot read `rev_derivedcity` — same test shape as the existing
  `rev_locationarea`/`rev_localauthority` trustee-exclusion tests.
- **Regression:** `rev_locationarea`, `rev_localauthority`, `rev_towncity` and every other existing
  intake-flow write must be unaffected — confirmed by the unchanged parts of the `runAfter` chain
  and unchanged outputs elsewhere in the flow (§4).
- **CSV integrity:** `provisioning/dataverse/data/city-settlement-register.csv` re-measured
  independently in this dispatch (§3) — 3,394 rows, zero blanks, zero duplicates.

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-CSR-01 | `rev_citysettlementregister`'s Dataverse entity set (collection) name is `rev_citysettlementregisters` (regular English pluralisation, matching every other entity in this solution). If wrong, `Lookup_city_register` fails loudly (404/`EntityNotFound`) on first run against a seeded environment, never silently. | [`Entities/rev_citysettlementregister/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_citysettlementregister/Entity.xml) (`EntitySetName` element); [`REVIntakeWordPressToDataverse-....json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json), action `Lookup_city_register`; full reasoning in [the flow's `.notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.notes.md) | E4 (inference by analogy with every other entity in this solution) | Dataverse assigns the entity set name; no environment exists yet to read it back from | `GET EntityDefinitions(LogicalName='rev_citysettlementregister')?$select=EntitySetName` after the first DEV prerequisite run; if wrong, a one-line `entityName`/`EntitySetName` correction | OPEN |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `Entity.xml`, `FormXml`, `SavedQueries`, `Solution.xml`, `FieldSecurityProfiles.xml`, `AppModule.xml`, `AppModuleSiteMap.xml`, Role XML | V1/V2 — statically checked against every applicable generic gate | macOS (dev workstation) | See gate list below — all green |
| `REVIntakeWordPressToDataverse-....json` | V1 — well-formed (JSON parse) + statically checked | macOS | `python3 -c "import json; json.load(...)"` → OK; `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` → OK, no new findings introduced |
| `provisioning/dataverse/data/city-settlement-register.csv` | V1 — re-derived and cross-checked against the TAD's own measurement | macOS | `openpyxl` read of `docs/Import/Postcode Details.xlsx` sheet `Postcodes`: 3,394 rows, 0 blanks, 0 duplicates, max outward-code length 4, max city-name length 20 — matches TAD §1 exactly |
| `provisioning/dataverse/seed-city-settlement-register.ps1`, `ensure-schema-helpers.psm1` change | V1 — syntax/pattern-consistent with proven sibling scripts (`seed-settings.ps1`, `seed-round-statistics-result.ps1`) | macOS | Not executed against a live PowerShell host in this dispatch (no environment exists) — pattern reused verbatim (keyed GET+PATCH upsert on an alternate key), not independently re-derived |
| No environment exists for this feature yet | V3/V4/V5 not reached | — | Deferred to pipeline-agent; DEV import is the first opportunity to ground-truth A-CSR-01 |

**Local gates run (all against the working tree, all green except the one expected/flagged
refusal, zero unexplained new findings):**

```
python3 scripts/verify-field-length-limits.py src/solutions/RevitaliseGrantAutomation provisioning/deploymentSettings
  → OK — 516 flow descriptions within 256 chars (was checked BEFORE two over-limit descriptions
    were found and shortened — Lookup_city_register, Derive_intake_review_note; this is the
    post-fix, passing run)
python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation
  → PASS - 80 root components declared, every one has a definition on disk, nothing undeclared
python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation
  → OK - 9 flows, no new findings (3 pre-existing dated exceptions, unrelated to this change)
python3 scripts/verify-forms-and-views-reachable.py src/solutions/RevitaliseGrantAutomation
  → OK - 78 secured columns with a main-form control (C-TECH-077) (was 77; +1 for rev_derivedcity),
    6 pre-existing warnings, unrelated to this change
python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation
  → PASS - 78 secured columns, every one released by a field security profile
python3 scripts/verify-role-privilege-ownership.py src/solutions/RevitaliseGrantAutomation
  → PASS - 115 table privileges, rev_citysettlementregister correctly requests no Assign/Share
    (OrganizationOwned)
python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation
  --register constraints/domain/special-category-register.yml
  --build-config config/revitalise-grant-automation-build.yml
  → FAILED (EXPECTED) - rev_applicant.rev_derivedcity is UNADJUDICATED-SECURED, exactly as §6/§10
    predicts. Two PRE-EXISTING failures for the same reason (rev_localauthority,
    rev_localauthoritystatus, IMP-0838) are also printed, unrelated to and not introduced by this
    dispatch.
```

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| Two flow action descriptions initially exceeded 256 chars (`Lookup_city_register` 458 chars, `Derive_intake_review_note` 349 chars) | Authoring, caught by `verify-field-length-limits.py` | Resolved | Condensed to ≤256 chars in-JSON, full reasoning moved to the flow's `.notes.md`, per this project's own established pattern |
| `verify-domain-invariants.py`: `rev_derivedcity` UNADJUDICATED-SECURED | `run-source-gates.py` via `config/revitalise-grant-automation-build.yml` | Accepted, expected, not resolved by this agent | C-DOM-033 handoff to improvement-agent — see §6, `IMP-0843` |
| `verify-forms-and-views-reachable.py`: 6 pre-existing `<FormXml />`/`<SavedQueries />` empty-folder warnings (`rev_anonymisedstatistic`, `rev_roundstatisticsrequest`, `rev_roundstatisticsresult`) | Same script | Accepted, pre-existing | Present before this dispatch's changes; deliberate per each entity's own header (no form/view needed) |

### Diagnostic components created and removed (C-TECH-056)

| Component | Environment | Purpose | Removed (date / how) |
|---|---|---|---|
| None | — | No environment exists for this feature; no diagnostic component was created in any live environment | n/a |

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0843 | `pending-adjudication-entry-needed` | blocker | Add `{ entity: rev_applicant, name: rev_derivedcity }` to `pending_adjudication:` in `constraints/domain/special-category-register.yml` (basis: geographic quasi-identifier mirroring rev_towncity/rev_locationarea, not Article 9 data, per TAD ADR-005) — confirmed BLOCKED for development-agent by the protection hook, as designed; apply behind `APPROVE IMPROVEMENTS` before the next real build, together with the two still-unresolved `IMP-0838` entries. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (839 entries, 831 distinct lessons)

---

## Code Review Checklist
- [x] All FR IDs covered (FR-220 through FR-229 traced in §3/§4/§5)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented (with one naming correction and one documented deviation — §6)
- [x] Every TAD §12 item has an idempotent provisioning script wired into the pipeline config (§5)
- [x] Role assignments via group teams only — no direct user assignments (unchanged; no role/group change in this dispatch)
- [x] No hardcoded environment-specific IDs/URLs
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (A-CSR-01, present in both the Entity.xml `EntitySetName` comment and the flow JSON action description)
- [x] Where an environment existed, ground truth was used instead of a guess — no environment exists for this feature; the one open assumption is correctly OPEN, not guessed-and-hidden. The source CSV itself was independently re-measured against the actual .xlsx, not taken on the TAD's word.
- [x] Every platform limit the packer/compiler does not enforce has a build gate — no new platform-limit class introduced; all existing generic gates re-run green (except the expected domain-invariants refusal, §6/§11)
- [x] Verification levels in §11 are the levels actually executed (V1/V2 only — no environment exists)
- [x] Scripts run on the CI runner's OS — `seed-city-settlement-register.ps1` is PowerShell 7, same runtime as every other script in `provisioning/dataverse/`
- [x] Every tool warning triaged in §11; no diagnostic components left anywhere
- [ ] Accessibility requirements met (if UI) — the new form controls follow the existing MDA shell pattern; not independently re-verified this dispatch, consistent with "no new interactive surface" scope (TAD §8)
- [x] No dead code or debug statements
- [ ] Unit tests written — no source-level test added over the new flow logic in this dispatch (see note below)

**Sub-agent fan-out not performed** — schema (data-agent), automation (automation-agent) and
provisioning (config-agent-class work) were implemented directly in this dispatch rather than
fanned out. The change is small and tightly coupled across exactly the files the TAD names
(one table, one column, one flow extension, one role/security-profile edit, one new script) —
splitting it across sub-agent dispatches would have meant re-reading the same TAD sections and
the same sibling-precedent source files (grant-admin-app's landed columns, seed-settings.ps1) in
each one, for no coordination benefit, per `IMP-0498`/`IMP-0470`/`IMP-0143`'s judgement-call
allowance.

**Regression test note:** this dispatch does not fix a defect a Test Report raised, so the
`skills/how-to-write-a-test-plan.md` line-80 regression-test obligation does not apply. No
source-level test was added over `Derive_city`'s null-on-miss branch or the register lookup —
flagged here rather than silently, consistent with `agents/development-agent.md`'s
"Regression tests for hand-authored artefacts" guidance applying most directly to *fixes*, not
first-time builds; §9 above gives test-agent the specific cases to exercise instead.

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
