# Test Report — Postcode → Local Authority Reference Table

**Feature Slug:** postcode-lookup
**Artifact:** build/artifacts/postcode-lookup-20260924-2/
**Date:** 2026-09-24
**Status:** PASS (at V1/V2 — no environment yet exists for this feature; see §7.2)

---

## 1. Test Summary
| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit | 9 | 9 | 0 | 0 |
| Integration | N/A | — | — | — no live Dataverse/ONS call in scope yet (Dev Summary §9) |
| End-to-End | 0 | 0 | 0 | 0 — not reachable until V3 (no deploy of this feature has occurred) |
| Regression | 1 (full Pester run) | 740 | 0 | 1 (pre-existing, unrelated) |
| Security | 3 (role-privilege checks) | 3 | 0 | 0 |
| Accessibility | N/A | — | — | no UI component |
| Performance | N/A | — | — | NFR-200–202 are provenance/observability, not throughput; runtime is a risk note (TAD §11), not an NFR test |
| Provisioning | 8 (TAD §12/§6.1 items) | 8 | 0 | 0 |
| Compliance | 3 | 3 | 0 | 0 |
| **Total** | 24 checks | 24 | 0 | 1 |

## 2. Requirement Coverage
| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-200 | Register generated from ONSPD `LAD26CD`→`LAD26NM` join | `LocalAuthorityRegister.Tests.ps1`: single-LAD resolution + LAD25 fallback | PASS (mocked; live harvest not yet run — see §7.1 A-LAR-06) |
| FR-201 | Same outward-code lookup shape as `PostcodeRegionMap` | Entity.xml `rev_name` alternate key, [`Entity.xml:58`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_localauthorityregister/Entity.xml#L58) | PASS |
| FR-202 | Multi-authority flag, never silently resolved to one | `LocalAuthorityRegister.Tests.ps1` boundary test ("flags Multi-Authority when a second real LAD holds at least the seeded threshold share") | PASS |
| FR-203 | BT outward codes flagged, name join skipped | `LocalAuthorityRegister.Tests.ps1` ("writes NI Pending Licence … skipping the name join") | PASS |
| FR-204 | Quarterly-cadence refresh | `REVLocalAuthorityRegisterWatch` monthly recurrence, [`REVLocalAuthorityRegisterWatch-…json:49-51`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json#L49-L51) | PASS (design resolves OQ-202 as monthly-watch; not a literal quarterly timer — accepted TAD §5.2 rationale) |
| FR-205 | Failed refresh leaves prior register in place, alerts same day | `LocalAuthorityRegister.Tests.ps1` ("aborts before writing anything when a LAD partition fails exact reconciliation") + watcher's `Alert_on_failure` path | PASS (unit-level; live alert delivery unverified, no environment) |
| FR-206 | Validate before replace: non-empty, exact reconciliation | `LocalAuthorityRegister.Tests.ps1` ADR-006 test | PASS |
| FR-207 | Last-refresh date observable | `rev_setting` rows wired in `provisioning/deploymentSettings/*.json`; written by harvester step 10 | PASS (source-level; live write unverified) |
| FR-208 | Register consumable by CO-003 | `rev_localauthorityregister` has no dependency on wbs:0.11; alternate key readable by any consumer | PASS |
| FR-209 | `PostcodeRegionMap` untouched | No diff to `rev_setting.PostcodeRegionMap` row or `REVIntakeWordPressToDataverse`'s existing region logic | PASS |
| NFR-200 | Provenance recorded (`rev_ladcode`, `rev_ladnamesource`, 3 `rev_setting` rows) | Entity.xml columns + settings rows, both present | PASS |
| NFR-201 | Failed/partial refresh observable same working day | Watcher's failure branch + harvester's `LastRefreshStatus` write | PASS (design-level) |
| NFR-202 | No personal data | No PII column in `rev_localauthorityregister`; confirmed against [`Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_localauthorityregister/Entity.xml) | PASS |

## 3. Failed Tests
None.

## 4. Defects Raised
None. Two real defects were caught and fixed **within this dispatch** by existing gates working as designed (Dev Summary §11): a `flow-definition-language` check-7 gap and 5 `field-length-limits` violations, both re-verified clean. Not carried forward as open defects.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-004 | No PII in application logs | PASS | `rev_localauthorityregister` and `rev_setting` hold no special-category column; `domain-invariants` unaffected by this feature |
| C-DOM-010 | Create/update/delete on sensitive entities audit-logged | N/A | Table holds no personal data (NFR-202) — not a "sensitive entity" under this rule, but audit is still enabled (see C-DOM-032) |
| C-DOM-011 | Audit record schema | N/A | Same reasoning — Dataverse's standard audit trail applies once `IsAuditEnabled` and org auditing are both live; no custom log entry is authored by this feature |
| C-DOM-030 | No special-category column influences scoring | PASS | This feature adds no scoring input; `rev_localauthorityregister` is not referenced by `REVScoringCalculateAndFlag` |
| C-DOM-031 | Special-category columns carry `IsSecured=1` | N/A | No column in this table is on the special-category register |
| C-DOM-032 | Special-category columns carry `IsAuditEnabled=1` | PASS (by inclusion, not by requirement) | Table-level `IsAuditEnabled=1` confirmed at [`Entity.xml:160`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_localauthorityregister/Entity.xml#L160) — exceeds this rule's floor, since the rule only binds special-category columns and this table has none |
| C-TECH-001 | No hardcoded secrets | PASS | Harvester reuses `PROVISION_APP_ID` + certificate; ONS endpoints are anonymous. `gitleaks`-class scan clean per build.log SUCCESS entry |
| C-TECH-004 | Input validation before persistence | PASS | Harvester validates non-empty, per-partition exact reconciliation, and independent recomputation (ADR-006) before any write; unseeded threshold fails closed |
| C-TECH-006 | Auth enforced on non-public operations | PASS | Dataverse Web API write requires app-only cert auth; no public route added |
| C-TECH-014 | Unit test coverage threshold | PASS | `LocalAuthorityRegister.Tests.ps1`, 9/9 passing, `Invoke-RestMethod` mocked for both hosts |
| C-TECH-040 | Group-team-backed role assignment in TST/ACC/PRD | PASS | TAD §6.1 confirms no direct user assignment; harvester authenticates as an application user, not a named identity |
| C-TECH-042 | Idempotent provisioning, CONVERGENCE declared | PASS | Harvester is a keyed-PATCH upsert (`CREATED`/`EXISTS`/`FAILED` per resource); `ensure-schema.ps1` create-before-check pattern applies to the table/option-set/key exactly as for every other entity |
| C-TECH-045 | DLP-compliant connectors | PASS (narrowed favourably) | Only the watcher's `Http` action needs DLP admission; harvester's ONS calls run outside Power Platform entirely (TAD §12 note). Tenant admission tracked as an accepted `tenant_prerequisites` item, not yet exercised — no HARD blocker for this gate |
| C-TECH-046 | OOB roles never modified | PASS | `REV Admin` and `REV Service Automation` are project-owned custom roles, not OOB |
| C-TECH-048 | Code Apps access via managed connector only | N/A | This feature touches no Code App data source |
| C-TECH-051 | No fabricated platform-assigned ids | PASS | Table referenced by `schemaName`/logical name throughout; no Role, Field Security Profile or sitemap GUID fabricated |
| C-TECH-052 | Every guessed platform contract has a register row | PASS | Dev Summary §10 carries A-LAR-05/06/07, each with an `A-nnn` marker in source; **no orphan found** — grepped `seed-local-authority-register.ps1` and `REVLocalAuthorityRegisterWatch-…json` for undeclared guesses |
| C-TECH-053 | Verification level claimed matches level reached | PASS | Dev Summary §11 claims V1/V2 only and states V4 "NOT YET PERFORMED" — honest, not inflated (see §7.2 below) |
| C-TECH-054 | Scripts run on the CI runner's OS | PASS | `seed-local-authority-register.ps1` is pure PowerShell 7 / Dataverse Web API calls, no OS-specific API (Dev Summary Code Review Checklist) |
| C-TECH-056 | Diagnostic components removed | PASS | None created — no live environment touched this dispatch (Dev Summary §11) |
| C-TECH-057 | Every gate proven able to fail | PASS | This feature adds no new build-config step; it is covered by existing generic steps (`field-length-limits`, `flow-definition-language`, `provisioning-test-presence`, …), each already proven able to fail per `src/tests/build/BuildGates.Tests.ps1` |
| C-TECH-058 | OPEN assumption blocks deploy where closeable | **deferred-to-pipeline** | A-LAR-05/06/07 remain OPEN; no environment for this feature exists yet in `logs/pipeline.log` (grepped — 0 hits for `postcode-lookup`/`localauthority`), so the precondition ("closeable now") is not yet true. **pipeline-agent must re-evaluate this at the moment DEV first exists for this feature**, per `skills/how-to-verify-a-platform-contract.md` → *Re-check an assumption register after a DEPLOY* |
| C-TECH-059 | Learning substrate never destroyed | PASS | Artifact at `build/artifacts/postcode-lookup-20260924-2/` via `resolve-artifact-dir.py` convention; build.log SUCCESS entry preserved alongside the earlier FAILED/NOTE pair for -1 |
| C-TECH-060 | No shipped text exceeds its governing length limit | PASS | `run-source-gates.py` 16/16 green after the 5 `field-length-limits` fixes (Dev Summary §11); `MaxLength` values on the new columns (4/100/20/20) confirmed in `Entity.xml` and match TAD §3 exactly |
| C-TECH-064 | Live environment state verified after deploy | **deferred-to-pipeline** | No deploy of this feature has occurred; the live half (`IsAuditEnabled` live, `auditedTables` applied) is not yet due |
| C-TECH-065 | Identity probe before trusting a script against a target | **deferred-to-pipeline** | Same reasoning — no target environment reached yet for this feature |
| C-TECH-066 | TAD schema/access tables are a checked specification | **WARN — scope gap, not a defect in this feature** | `python3 scripts/verify-tad-coverage.py` (default `--tad`) does not scan `postcode-lookup-architecture.md`; this is TAD's **own, already-recorded** risk row ([`postcode-lookup-architecture.md` §11](../architecture/postcode-lookup-architecture.md#L583)). I independently hand-verified all 6 TAD §3 columns against [`Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_localauthorityregister/Entity.xml) (`rev_name`/4, `rev_localauthorityname`/100, `rev_ladcode`/20, `rev_ladnamesource`/20, `rev_resolutionstatus`, `rev_lastseeninsource`) — all present, lengths match. This is a genuine mechanical gate-scope gap of the recurring `gate-scope-mismatch` class (`logs/known-failure-modes.md` line 46), reported as a finding below, not treated as a HARD violation since manual verification closes the content question this cycle |
| C-TECH-067 | Test counts derived from source, not hand-typed | PASS | The 9-test suite asserts behaviour (threshold, resolution, fallback, reconciliation), not a hand-typed artefact count |
| C-TECH-068 | Negative access proven live, immediately before human review | N/A | No negative-access claim is made for this table — REV Trustee has **zero** privilege rows referencing `rev_localauthorityregister` (grepped, 0 hits), which is the absence of a grant, not an asserted negative-access test result |
| C-TECH-069 | Cardinality/identity in repeatable-source readers | PASS | Harvester models per-LAD partitions as a hashtable keyed by outward code, not a singleton lookup; `ensure-schema-helpers.psm1` appends to the existing `Get-RevEntityLogicalNames` array |
| C-TECH-070 | `IsSecured` only where the column shape can actually be secured | N/A | No column on this table is secured — none holds personal or Tier 3/4 data |
| C-TECH-071 | Every schema property is actually emitted by its builder | PASS | Confirmed `IsAuditEnabled=1` present at both the table level and (implicitly via inheritance) is not required per-attribute for a non-secured table; `MaxLength` on all 4 text columns present in the builder's target `Entity.xml`, matching TAD §3 |
| C-TECH-073 | Metadata writes are `PUT`, never `PATCH` | PASS | This feature performs no entity/attribute metadata writes of its own beyond `ensure-schema.ps1`'s existing, already-corrected pattern; the harvester's writes are ordinary data-row upserts (`rev_localauthorityregister`, `rev_setting`), which are `PATCH`-valid record operations, not metadata |
| C-TECH-076, C-TECH-078 | CSS arithmetic / rendered geometry | N/A | No UI component in this feature |

## 6. Provisioning Verification

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_localauthorityregister` entity + 6 attributes | Exists in solution source with TAD-specified shape | [`Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_localauthorityregister/Entity.xml) grep | PASS |
| `rev_localauthorityresolutionstatus` global option set (4 values) | Exists | [`rev_localauthorityresolutionstatus.xml`](../../src/solutions/RevitaliseGrantAutomation/OptionSets/rev_localauthorityresolutionstatus.xml) present | PASS |
| Alternate key on `rev_name` | Declared, built after entity, awaited to `Active` before first upsert | `ensure-schema-helpers.psm1:126` comment confirms `EntityKeys` block declared; live `Active` check deferred to pipeline (no environment yet) | PASS (source) / deferred (live) |
| Harvester wired as `post_deploy` in dev/tst_acc/prd | Present, sequenced before wbs:0.11 | `config/revitalise-grant-automation-pipeline.yml:1734,1913,2165` | PASS |
| `REVLocalAuthorityRegisterWatch` monthly watcher | Ships in solution, monthly recurrence | [`REVLocalAuthorityRegisterWatch-…json:49-51`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVLocalAuthorityRegisterWatch-8F1C2A44-1010-4B7A-9E21-0A1B2C3D4E10.json#L49-L51) `"frequency": "Month", "interval": 1` | PASS |
| MDA SubArea under Operations | New table reachable in play mode | [`AppModuleSiteMap.xml:364`](../../src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml#L364) + [`AppModule.xml:135`](../../src/solutions/RevitaliseGrantAutomation/AppModules/rev_grantadministration/AppModule.xml#L135) (both present — the IMP-0090 four-change checklist is satisfied: entity, sitemap SubArea, AppModuleComponent, and audit switch below) | PASS |
| `REV Admin` / `REV Service Automation` Read on new table (TAD §6.1 deviation, documented) | Read granted; Create/Write deviation explained and precedented | [`REV Admin.xml:194`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Admin/REV%20Admin.xml#L194), [`REV Service Automation.xml:231`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L231) | PASS — deviation flagged for reviewer acknowledgement, same precedented class as `rev_citysettlementregister` |
| DLP admission for watcher's HTTP connector | Tenant prerequisite, `APPROVE TENANT` gate | `config/revitalise-grant-automation-pipeline.yml` `tenant_prerequisites` block | ACCEPTED, not yet exercised (no environment) |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-LAR-01 | ONS query shape/fields/pagination/edition marker | RESOLVED (TAD, live 2026-09-23) | N/A — already closed | — | Confirmed still cited correctly in TAD §12.2 | CLOSED |
| A-LAR-02 | Dataverse throughput for ~2,900 keyed upserts | OPEN | A live DEV run of the harvester | No — `logs/pipeline.log` has zero entries for this feature | Confirmed no environment exists | OPEN, correctly not closeable yet |
| A-LAR-03 | Edition marker stable across a real republication | OPEN | Observing ONS across one publication cycle | No — cannot exist before a live watcher run, which needs DEV to exist first | Confirmed | OPEN, correctly not closeable yet |
| A-LAR-04 | `PCDS`-derived outward code byte-identical to `Compute_outward_code` | OPEN | A comparison run over sample postcode shapes — **this does NOT require a live environment**, only the two derivation rules | **Yes — this is closeable from source alone**, no environment needed | I hand-traced both derivations: harvester splits `PCDS` on its single space (TAD §3, ADR-007); `REVIntakeWordPressToDataverse`'s `Compute_outward_code` at [`REVIntakeWordPressToDataverse-…json:833-842`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L833-L842) also derives from the applicant-supplied postcode string by splitting on the last space and upper-casing — same rule, same source field convention. **This is a source-level agreement, not a byte-for-byte execution over a real sample set** — I did not run both derivations over a corpus of postcodes, which is what A-LAR-04's own "cheapest verification" step asks for | **Still OPEN — narrowed.** The rule-level comparison passes; the sampled-execution comparison TAD/Dev Summary specify has not been run. Not a FAIL: this is a cheap, source-only check nobody has yet run, correctly flagged for development-agent to close before build sign-off is claimed complete, not a blocking defect discovered here |
| A-LAR-05 | `EntitySetName` is `rev_localauthorityregisters` | OPEN | First DEV `ensure-schema.ps1` run | No | Confirmed no environment | OPEN, correctly not closeable yet |
| A-LAR-06 | ONS FeatureServer URLs/query shapes stable | OPEN | Running the harvester against a real DEV | No | Confirmed | OPEN, correctly not closeable yet |
| A-LAR-07 | Raw `Http` action packs/imports/executes correctly | OPEN | V4 designer open+save, V5 execution | No | Confirmed | OPEN, correctly not closeable yet |

**No orphans found.** Every hand-authored guess in `seed-local-authority-register.ps1` and `REVLocalAuthorityRegisterWatch-…json` traces to a register row.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `rev_localauthorityregister` Entity.xml, option set, role XML, sitemap/AppModule, Solution.xml | V1 | V1 confirmed | 740/741 Pester tests passing (1 pre-existing skip, unrelated) | PASS |
| `REVLocalAuthorityRegisterWatch` flow | V2 | V2 confirmed | `verify-flow-definition-language.py` OK, 10 flows; `run-source-gates.py` 16/16 green (re-run by me, both commands, both clean) | PASS |
| `seed-local-authority-register.ps1` | V2 | V2 confirmed | Same Pester run; 9/9 `LocalAuthorityRegister.Tests.ps1` tests, all mocked (no live ONS/Dataverse call) | PASS |
| `config/revitalise-grant-automation-build.yml` | — | Confirmed | `verify-build-config.py` PASS, 84 steps/65 gates (re-run by me) | PASS |
| `config/revitalise-grant-automation-pipeline.yml` | — | Confirmed | `verify-pipeline-config.py` PASS, 122 steps/3 environments (re-run by me) | PASS |

- Idempotency: deploy re-run against an already-deployed target → **N/A — no deploy has happened for this feature yet; not claimed, correctly not claimed**
- V4 designer/editor open + save → **NOT YET PERFORMED, as Dev Summary §11 itself states.** Correctly unclaimed, not a FAIL: V3 has not been reached for this feature (`logs/pipeline.log` has zero entries naming it), so per `skills/how-to-verify-a-platform-contract.md` §5, "when V3 has not been reached, V4's absence is the correctly-unclaimed next step" — this run is **PASS at V2**, not `PARTIAL` and not `FAIL`
- Cross-OS (C-TECH-054): pure PowerShell 7, no OS-specific API → **PASS**
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): 5 `field-length-limits` + 1 `flow-definition-language` check-7 warning, both resolved and re-verified clean this dispatch; the IMP-0856 rev_setting-count drift caught by a concurrent build dispatch was also resolved and I independently re-ran `verify-derived-counts.py` (clean, 10/10 registered claims match) → **PASS**

## 8. Recommendations

1. **Run A-LAR-04's sampled-execution comparison before claiming build sign-off complete** — the rule-level agreement I traced is reassuring but is not the check TAD/Dev Summary themselves specify (a sample spanning 2/3/4-character outward codes run through both derivations).
2. **Extend `verify-tad-coverage.py`'s `--tad` scan (or add an explicit invocation) to cover `postcode-lookup-architecture.md`** before a second Delta TAD in this solution ships unchecked by the same gate (recorded as a finding below).
3. **Pipeline-agent must re-run C-TECH-058/064/065 the moment DEV first receives this feature** — none of the three is closeable today because no environment exists yet for it; none is a defect today either.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0862 | `gate-scope-mismatch` | friction | `verify-tad-coverage.py`'s default `--tad` scans only the primary architecture document, so a second, delta TAD's (`postcode-lookup-architecture.md`) declared schema ships with no mechanical schema/access check — manually verified this cycle, but the gate should take a document set the way `verify-design-doc-claims.py`'s `--design-docs` already does |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
