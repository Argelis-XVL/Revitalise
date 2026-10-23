# Dev Summary Document — Settings: plain-language descriptions and a Category column

**Feature Slug:** revitalise-grant-automation (amends the existing `config/revitalise-grant-automation-build.yml` and pipeline; no new configuration)
**TAD Reference:** docs/architecture/revitalise-grant-automation-architecture.md (rev 35, ADR-090)
**Date:** 2026-10-23
**Status:** DRAFT
**Work items:** WI-0150 (blocked on the reviewer), WI-0151, WI-0152, WI-0153. `wbs:2.2`, change order CO-012 closed with no change order.

---

## 1. Implementation Summary

`rev_setting` gains a **Category** (a Choice column on a new global choice set, eight values) and every one of the 48 rows in the three settings files carries its category as label text. The Settings list (`AllSettings`) is ordered category, display name, key, with Category as the first column. The form shows Category read-only. Every one of the 48 descriptions was rewritten in plain language for the process owner and is identical in the `dev-scoring`, `test` and `prd` files. The seed script now writes `rev_category` on every row and, for an existing create-only row, updates only `rev_description` and `rev_category` by the row's own id, so the 16 create-only rows receive both on an existing environment without their value being touched.

**Not built, on purpose:**
- No grid-control (grouping) configuration is authored in source (ADR-090 item 4, `C-TECH-051`). Grouping is the process owner's own *Group by*, and whether the grid offers it is `A-SETCAT-1` / `A-SETCAT-2`, OPEN. The reviewer's *"GroupBy is available in the table view"* is an observation, not a DEV check as her role (TAD Approval).
- The 2 live rows beyond the 48 are not in the settings files, by design. The reviewer's DEV query (WI-0150) shows they are `CitySourceFile` (data type 1) and `CitySourceCapturedOn` (data type 7), created 2026-09-24 18:52:11 by `seed-city-settlement-register.ps1`. That script's existing keyed upsert now writes their plain-language description and category 6 (Postcodes and local authorities), taken from the same label table as `seed-settings.ps1` (`Get-SettingCategoryMap` in `provisioning-common.ps1`). They receive both only when that script next runs in each environment. The reworded `CitySourceFile` description (improvement review 2026-10-23-2, R1a) reaches DEV only on the reviewer's next run of the city script.

**Config decision (`IMP-0836`):** this amends the existing build and pipeline configuration. The pipeline already runs `ensure-schema.ps1` (prerequisites) and `seed-settings.ps1` (post-deploy) in every environment, so the new choice set and column and the new seeding path reach each environment through steps that already exist. `config/revitalise-grant-automation-build.yml` is unchanged.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| `OptionSets/rev_settingcategory.xml` | Global choice set (new) | Eight labels, values 1 to 8 in alphabetical label order | NFR-019 |
| `Other/Solution.xml` | Solution root component | `RootComponent type="9"` for `rev_settingcategory` | NFR-019 |
| `Entities/rev_setting/Entity.xml` | Table | New `rev_category` Choice column (not required, audited, not secured) | NFR-019 |
| `Entities/rev_setting/SavedQueries/AllSettings.xml` | View | Category first; orders by `rev_category`, `rev_displayname`, `rev_name` | NFR-019 |
| `Entities/rev_setting/FormXml/main/{60e05819-…}.xml` | Form | Category row, `disabled="true"` (read-only) | NFR-019 |
| `provisioning/deploymentSettings/{dev-scoring,test,prd}-settings.json` | Settings files | `category` on all 48 rows; all 48 `description` values rewritten | FR-017 |
| `provisioning/deploymentSettings/settings-rows.notes.md` | Developer notes | Previous descriptions of all 48 rows appended verbatim | — |
| `provisioning/dataverse/seed-settings.ps1` | Provisioning | `$categoryMap`, category pre-flight, probe selects id, description and category, create-only metadata update by id, `rev_category` in the create and upsert bodies | FR-017 |
| `provisioning/dataverse/seed-city-settlement-register.ps1` | Provisioning | The two provenance rows (`CitySourceFile`, `CitySourceCapturedOn`) get a plain-language description and `rev_category` 6; value, data type and effective-from behaviour unchanged | — |
| `provisioning/common/provisioning-common.ps1` | Shared helper | New `Get-SettingCategoryMap` (the label to value table both seed scripts use); `Invoke-DataverseApi` gains an optional `-AdditionalHeaders` (used for `If-Match: *` so the metadata update can never create a row) | — |
| `src/tests/provisioning/DataverseScripts.Tests.ps1`, `DeploymentSettings.Tests.ps1`, `_harness/ProvisioningTestHarness.psm1` | Tests | New cases for the create-only metadata path, the category pre-flight, the label table, and the descriptions; fixtures carry `category` | — |

## 3. Data Model Changes

TAD §3.1 `rev_setting`, rev 35. One column added, `rev_category` (Choice, global choice set `rev_settingcategory`). Neither the choice set nor the column can be created by solution import (`C-TECH-050`): they are created by `ensure-schema.ps1`, which reads `OptionSets/*.xml` and `Entities/*/Entity.xml` at run time. **Not yet run against any environment** (`A-SETCAT-4`).

| Value | Label |
|---|---|
| 1 | Acceptance emails and reminders |
| 2 | Automatic rejection rules |
| 3 | Data retention and erasure |
| 4 | Lookup lists and wording |
| 5 | Narrative scrubbing |
| 6 | Postcodes and local authorities |
| 7 | Round statistics |
| 8 | Scoring and eligibility |

The key-by-key placement is the table in ADR-090; all 48 file rows match it. A Pester test asserts each file row carries one of these eight labels and the same label in all three files, and that `seed-settings.ps1` holds the same eight labels and values as the XML.

## 4. Automation / Workflow Changes

None. No flow reads `rev_category`. No flow expression is touched.

## 5. Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `category` (new, every row) | dev, test, prd | Label text of the choice. A row with none, or an unknown one, stops the whole seed before any write. |
| `description` (all 48 rows) | dev, test, prd | Plain language, identical in all three files, longest 984 characters (column limit 2000). |

### Provisioning Scripts

| Script | Purpose | Pipeline Block | Idempotency Check |
|---|---|---|---|
| `provisioning/dataverse/ensure-schema.ps1 -Env dev` (unchanged) | Creates the choice set and column by Web API | existing `environment_prerequisites` and `post_deploy` steps, every environment | Existing check-then-create: `EXISTS` on a second run |
| `provisioning/dataverse/seed-settings.ps1` (changed) | Seeds rows; now also brings description and category level on create-only rows | existing `post_deploy` steps | A re-run where both already equal the file sends nothing and reports `EXISTS — left unchanged (createOnly)` |

**Consequence the reviewer should read (ADR-090 item 7):** the repository owns description and category on every seeded row. A description edited in the app is replaced by the next deploy. This was already true for the 32 upserted rows and is new for the 16 create-only rows. **The 16 create-only rows keep their old description on an existing environment until `seed-settings.ps1` runs there.**

## 6. Security Controls Implemented

`rev_category` is not secured and not personal data (TAD §3.1, Tier 2 configuration). No role, field-security profile or column-security row changes, so no row is owed to `constraints/domain/special-category-register.yml`. The create-only update sends exactly two columns and `If-Match: *`; a value the process owner changed is not in the request.

## 7. Known Limitations / Deferred Items

- The 2 extra rows get their description and category only when `seed-city-settlement-register.ps1` next runs per environment. That script also upserts the ~3,394 register rows (about 6,800 sequential calls, a GET and a PATCH per row; duration not measured). A re-run is idempotent (keyed upserts), so it is safe; no provenance-only script was added because every mutating provisioning script must satisfy the script contract (a CREATED path and a README inventory row).
- **Grouping is not delivered by source.** What ships is a list sorted by category, filterable on Category. Whether *Group by* is available to the process owner's role is reviewer-observed, not checked (`A-SETCAT-1`, `A-SETCAT-2`).
- `verify-tad-coverage.py` exits 1 on TAD §3.1 line 1228: it reads the paragraph's heading token `rev_setting` and the choice-set name `rev_settingcategory` as missing columns. The column itself is in source. The fix is a wording change in the TAD, owned by architect-agent (`IMP-1244`).
- `DeploymentSettings.Tests.ps1` still asserts a 1000-character description limit while the column is 2000 (`IMP-1243`); all descriptions were kept at 1000 or fewer so the test is green, and nothing was edited in that assertion.

**SDD changes owed:** none.

## 8. Build Instructions

No change to `config/revitalise-grant-automation-build.yml`. The solution gains one global choice set root component (`type="9"`) and one attribute on an existing table. Before the solution import in each environment, the pipeline's existing `ensure-schema.ps1` step must run so the choice set and column exist. Then `seed-settings.ps1` runs as it already does.

## 9. Test Guidance

- A live `ensure-schema.ps1` run must show `CREATED` for the choice set and the column and `EXISTS` for everything else (`A-SETCAT-4`).
- After the first live `seed-settings.ps1`, every one of the 48 rows has a category and the 16 create-only rows show the new description with their value unchanged. Check one create-only row whose value the process owner edited: the value must survive.
- Open the Settings list as the process owner's role and check the order and that Category is the first column. Then try *Group by* on the Category column header (`A-SETCAT-1`).

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-SETCAT-1 | The Power Apps grid control's *Enable grouping* property and the *Group by* item in a column's header menu work on a choice column in this app, for the process owner's role. If wrong, the list is still sorted and filterable and nothing is lost but grouping. | [`Entities/rev_setting/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml) (comment on `rev_category`) | E2 (Microsoft documentation, read 2026-10-23); the reviewer reports it available (observation) | Not exercised as the process owner's role; no DEV session | DEV: open the list as her role, group by Category (expect eight collapsed sections); and with the property off confirm no group item | OPEN |
| A-SETCAT-2 | Table-level grid configuration survives export and import as solution source and can be committed. If wrong, grouping needs a manual step per environment and is dropped. | [`Entities/rev_setting/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml) (comment on `rev_category`) | E4 | No grid configuration exists in source today and none is authored here (`C-TECH-051`) | DEV: configure, export, diff against source, import into a clean environment | OPEN |
| A-SETCAT-3 | A sort on a choice column is by value or by label (undocumented here) and an empty Category sorts first; either way the order is the same because values 1 to 8 follow the alphabetical label order. | [`Entities/rev_setting/SavedQueries/AllSettings.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/SavedQueries/AllSettings.xml) (comment above the view), [`OptionSets/rev_settingcategory.xml`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_settingcategory.xml) (header comment) | E4 | Needs a live list with a mix of categories and one blank | DEV: open the list with all eight categories plus one blank row; expect category order, blank first; and that no row from category 8 appears above category 1 | OPEN |
| A-SETCAT-4 | `ensure-schema.ps1` adds the new global choice set and the new column to the existing `rev_setting` table without touching existing columns, and a second run reports `EXISTS`. If wrong, the column is missing and the seed's `rev_category` writes fail visibly per row. | [`Entities/rev_setting/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml) (comment on `rev_category`), [`OptionSets/rev_settingcategory.xml`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_settingcategory.xml) | E3 (the script's own header and its Pester suite; never run against this change) | Needs the reviewer-held DEV credential | DEV: `CREATED` for the choice set and column, `EXISTS` for the rest; then a second run, expect `EXISTS` for both | OPEN |
| A-SETCAT-5 | The two live rows the settings files lack are `RetentionStaleCaseMonths` and `ErasureNotificationEmail`. | — | E1 (the reviewer's own DEV query, WI-0150: `CitySourceCapturedOn` type 7 and `CitySourceFile` type 1, created 2026-09-24 18:52:11) | — | — | CORRECTED 2026-10-23 (DISPROVED; the two rev 34 keys do not exist yet; the real rows are written by [`seed-city-settlement-register.ps1`](../../provisioning/dataverse/seed-city-settlement-register.ps1) and placed in category 6 by ADR-090) |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Choice set, column, view, form, Solution.xml, settings files, seed script | V1 well-formed | macOS (dev workstation) | `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` exit 0, 19 of 89 steps, all PASS; includes `source-validate`, `component-shape`, `attribute-type-stability`, `forms-and-views-reachable`, `field-length-limits` |
| Seed script (create-only metadata path, category pre-flight, label table) | V1, by mocked Web API | macOS | `pwsh -NoProfile -File <runner> -Files src/tests/provisioning` exit 0: 810 passed, 0 failed, 1 skipped (the skip was already there) |
| Whole unit-test suite | V1, by mocked Web API and fixtures | macOS | `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -OutputPath <dir>` exit 0: 1511 passed, 0 failed, 1 skipped (includes the Python narrative suite). **This is the build's unit-tests step.** The earlier close-out ran `src/tests/provisioning` only, which is how build 20261023-1 failed on `test_scrub_flow_definition.py` (the four Redaction rule descriptions no longer contain the literal "Synthetic examples only"). Fixed in the test: it now asserts "never paste text from an application" and equality with `SEED_DESCRIPTIONS` (updated to the new text in `redaction_reference.py`); the descriptions were not reverted (`IMP-1248`, fixed by `IMP-1249`). |
| Provenance rows' body (description, category 6, value unchanged) | V1, by mocked Web API | macOS | included in the Pester run above (810 passed) |
| Live choice set and column, live seeding | **Not reached** | — | Needs the DEV credential: REVIEWER ACTION REQUIRED |

NOT covered by the source-gates run: packaging, the code-app suite, provisioning steps and every document gate. A green run is a statement about the gates it names only. Both new live behaviours (`A-SETCAT-4`, the update-by-id with `If-Match: *`) are proven against a fake API, not against Dataverse.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `verify-tad-coverage.py`: 2 violations on TAD §3.1 line 1228 | tad-coverage | Accepted, not mine | The column is in source. The TAD's own wording trips the parser. Logged as `IMP-1244`; architect-agent rewrites the line. |
| `verify-derived-counts.py`: 1 drifted claim (bundle size prose, dev summary line 4893) | derived-counts (SOFT) | Accepted, not mine | Unrelated to this change; already logged as `IMP-1242`. |
| Assumption-marker NOTEs for other documents' registers | assumption-markers | Accepted | Standing; no row of this feature is among them. |
| Standing warnings of the shared source-gate steps | source gates | Cited | None emitted by the 19 gates in this run. |
| `pac solution pack`: "Following root components are not defined in customizations", **21** `Type=` lines (9 `EntityRelationship`, 2 `AIModel`, 10 `EnvironmentVariableDefinition`) in build 20261023-2; **from the next build 20** (1 `AIModel`), because WI-0154 removed the retired detector prompt `{122be8e0-…}` from the solution (revitalise-narrative-scrubbing-dev-summary.md, Iteration 15) | pack-managed (build 20261023-2) | Accepted, standing | Read from `build/artifacts/revitalise-grant-automation-20261023-2/run-build-result.json`. The three types are the standing set, with the same relationships and environment variables cited in [revitalise-grant-automation-dev-summary.md#L1677](revitalise-grant-automation-dev-summary.md#L1677) and [revitalise-narrative-scrubbing-dev-summary.md#L403](revitalise-narrative-scrubbing-dev-summary.md#L403); the two `AIModel` lines are the one named at [revitalise-narrative-scrubbing-dev-summary.md#L945](revitalise-narrative-scrubbing-dev-summary.md#L945), which on its own covers only the AIModel lines, not the other 19. **This change's new root component (`type="9"`, `rev_settingcategory`) is not among the 21**: no `OptionSet` line appears in the output. |
| The same notice, 21 lines, same three types and same counts | pack-unmanaged (build 20261023-2) | Accepted, standing | Identical list to pack-managed above (checked line by line by type: 10 / 9 / 2 in both). |
| Vite "Some chunks are larger than 500 kB": JS 857.73 kB, CSS 150.78 kB | code-app-build (build 20261023-2) | Accepted, standing | This change touches nothing under `src/code-apps`. Compared with [trustee-portal-design-2-dev-summary.md#L394](trustee-portal-design-2-dev-summary.md#L394): JS 857,730 B measured there and 857.73 kB now (unchanged); CSS 150,250 B there and 150.78 kB now (+530 B, from other work in the tree), both within that row's unchanged maxima of 871,100 B and 152,800 B in `bundle-budget.json`. `code-app-bundle-budget` passed in the same build. |

### Diagnostic components created and removed (C-TECH-056)

None.

## 12. Work Items — close-out record (C-TECH-079)

Filled from the evidence passed to `scripts/work-items.py transition`; see the ledger for the authoritative copy.

| Item | External id | Source (`source_ref`) | State |
|---|---|---|---|
| WI-0150 | CO-012-1 | contract/change-orders/CO-012.md | answered by the reviewer's DEV query; see the ledger for the state reached |
| WI-0151 | CO-012-2 | contract/change-orders/CO-012.md#L11 | built (see ledger) |
| WI-0152 | CO-012-3 | contract/change-orders/CO-012.md#L10 | built (see ledger) |
| WI-0153 | CO-012-4 | contract/change-orders/CO-012.md#L12 | built (see ledger) |

Deferred: none. WI-0150's clause 3 (rows present in all three settings files) is met by a different route than it says: the architect's corrected ADR-090 has the city script's existing upsert reach the two rows, not the files.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1243 | `stale-field-limit-literal-in-pester-test` | friction | A test that restates a platform field limit as a literal must read it from Entity.xml like `verify-field-length-limits.py` does, or be deleted in favour of that gate. |
| IMP-1249 | `close-out-ran-a-subset-of-the-build-test-suite` | friction | Before closing an item that edits a shared data file, grep src/tests for the replaced text and record the full src/tests/Invoke-Tests.ps1 run as its test-run evidence (fixes IMP-1248). |
| IMP-1246 | `strict-mode-property-access-in-hand-written-probe` | friction | Under the Set-StrictMode that provisioning-common.ps1 turns on, read an optional property such as `@odata.nextLink` through `PSObject.Properties`, not `$r.'@odata.nextLink'`; and say where a handed-over script was written and test-run it before returning the path. |
| IMP-1244 | `tad-coverage-reads-delta-paragraph-names-as-columns` | friction | In TAD §3.1 a delta paragraph names its new column and writes any choice-set name without backticks, or the tad-coverage gate reads it as a missing column. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist
- [x] All FR IDs covered
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented (no change)
- [x] Every TAD §12 item has an idempotent provisioning script wired into the pipeline config (existing steps)
- [x] Role assignments via group teams only (no change)
- [x] No hardcoded environment-specific IDs/URLs
- [x] Every guessed platform contract is in §10 and commented `A-nnn` in source (C-TECH-052)
- [ ] Where an environment existed, ground truth was used instead of a guess — no environment credential available; REVIEWER ACTION REQUIRED
- [x] Every platform limit the packer does not enforce has a build gate (`field-length-limits` reads the column's 2000)
- [x] Verification levels in §11 are the levels actually executed (C-TECH-053)
- [x] Scripts run on the CI runner's OS
- [x] Every tool warning triaged in §11 (C-TECH-055); no diagnostic components
- [x] Accessibility requirements met (Category is a labelled read-only field)
- [x] No dead code or debug statements
- [x] Unit tests written
- [ ] Every carried work item is built or deferred, each clause traced to a line (C-TECH-079) — see ledger

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
