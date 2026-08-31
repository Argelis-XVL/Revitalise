# Test Report (v4) — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260828-2/`
**WBS:** `6.9` — not one of the 61 base tasks; made a covered id by [CO-001](../../contract/change-orders/CO-001.md#L30), APPROVED 2026-08-24, so [C-COM-002](../../constraints/commercial/commercial-constraints.md#L35) is satisfied
**Date:** 2026-08-28
**Supersedes:** [v3](trustee-portal-visual-refresh-test-report-v3.md) — this cycle tests TAD Revision 5 + Erratum 5.1 + Erratum 5.2 (ADR-038), which v3 predates
**Status: FAIL** — and the failure is a requirement-coverage and document-accuracy failure, **not a fault in the build artifact**

---

## 0. Read this first

**Every disclosure control ADR-038 exists to deliver is correct in source, and I verified each one myself rather than reading the claim.** The five things the dispatch named all hold at source level, and one of them (the write-boundary split) is the closure of a real exposure.

**Nothing in this feature is verified live end-to-end, and it cannot be.** `rev_roundstatisticsresult` does not exist in DEV — I queried it. The flow reads that table first, so it cannot have run; the trustee's Read-only privilege on it cannot exist; and the one V5 assertion [TAD §12.2](../architecture/trustee-portal-visual-refresh-architecture.md#L3196) assigns to `test-agent` has no subject. **The honest ceiling this cycle is V2 (source + packaged), plus four live E1 reads I took myself.**

**The FAIL is one thing:** three SDD requirements this feature is contracted to deliver are not delivered, no deferral record exists for them, and the approved TAD's own traceability matrix presents them as covered. That combination can produce a false phase acceptance. It is cheap to correct and it does not block deploying to DEV.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app, re-run by me) | 662 | 662 | 0 | 0 |
| Unit / Integration (Pester, per manifest) | 943 | 942 | 0 | 1 |
| Integration (flow source, structural) | 14 | 14 | 0 | 0 |
| End-to-End (V5) | 0 | — | — | **all — no environment** |
| Regression | 662 | 662 | 0 | 0 |
| Security / disclosure control | 11 | 9 | 2 | 0 |
| Accessibility | 0 | — | — | **all — jsdom computes no CSS** |
| Performance | 0 | — | — | **all — A-R36, needs V5** |
| Provisioning (live E1 reads) | 4 | 2 | 2 | 0 |
| Compliance / constraint | 31 | 28 | 2 | 1 |
| **Total executed** | **2327** | **2323** | **4** | **2** |

`npx vitest run` → **662 passed / 38 files, exit 0**, run by me at 16:32 — matches [manifest.json](../../build/artifacts/trustee-portal-visual-refresh-20260828-2/manifest.json#L66) exactly. The Pester figure is the manifest's; I did not re-run the 120 s suite, and I say so rather than restating it as mine.

The two security failures and the two provisioning failures are **the same two facts**: the two stale live privileges. They are counted once per layer because each layer asks a different question of them.

---

## 2. Requirement Coverage

Derived from [TAD Appendix A](../architecture/trustee-portal-visual-refresh-architecture.md#L3278) against what the shipped flow actually composes at [`Compose_response_body`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1076).

| FR ID | Requirement | Test case / evidence | Result |
|---|---|---|---|
| FR-057 | One open round, no selector | App direct-reads `rev_roundfinance` `rev_isopen`, `top 2`; flow asserts the same invariant in `Switch_on_open_round_count` with explicit zero / ambiguous branches | **PASS** (V2) |
| FR-058 | Total received · round-open date · **average per day** | `applicationsReceived` computed; open date direct-read. **`applicationsPerDay` is a literal `null`** in the shipped document | **PARTIAL — D-11** |
| FR-059 | Exceptional-circumstance counts · total and % citing any · average exceptional funding | **`exceptionalCircumstanceMix` and `exceptionalFundingSummary` are both literal `null`.** No action computes either | **FAIL — D-11** |
| FR-060 | Break-type breakdown, four measures + total row | **`breakTypeProfile` is a literal `null`.** No action computes it | **FAIL — D-11** |
| FR-061 | Gender · age-range · applicant-type · ethnic group | First three computed from 5 + 9 + 3 `Filter array` actions. `ethnicGroupDistribution` `null` — documented, A-R24, Erratum 5.2 | **PASS as designed** (V2) |
| FR-062 | Wellbeing last-year · life satisfaction · three proportions | `wellbeingLastYear` (3 questions × 6 bands) and `lifeSatisfactionDistribution` (11 bands) computed. Three proportions `null` pending OQ-039 — documented, A-R29 | **PASS as designed** (V2) |
| FR-063 | Round finance figures | Direct trustee read of `rev_roundfinance` (ADR-028) | **PASS** (V2) |
| NFR-013 | Nothing persisted | Correctly **withdrawn** in Revision 5 — one row is now persisted, and [§6.4.1](../architecture/trustee-portal-visual-refresh-architecture.md#L2077) states the trade rather than hiding it | **PASS** |
| NFR-021, NFR-022 | Latency | Not measured. Needs V5, A-R36 | **NOT TESTED** |
| NFR-024, NFR-026 | Accessibility, brand | Arithmetic over declared token values only; no screen has ever been rendered (A-R39) | **NOT TESTED at V4** |

**The four `null` metrics are disclosed** at [Dev Summary §7](../development/trustee-portal-visual-refresh-dev-summary.md#L1240) — *"Still `null` by design: … `applicationsPerDay`, `exceptionalCircumstanceMix`, `exceptionalFundingSummary`, `breakTypeProfile`"*. **Three artefacts contradict that disclosure**, and that is D-11:

1. [Appendix A's FR-059 row](../architecture/trustee-portal-visual-refresh-architecture.md#L3290) reads *"Response `exceptionalCircumstanceMix` / `exceptionalFundingSummary`"* with no partial marker — where FR-035, FR-061 and FR-062 all carry one, so the omission reads as deliberate coverage.
2. [Appendix A's Revision 5 row](../architecture/trustee-portal-visual-refresh-architecture.md#L3307) asserts *"**No requirement gains or loses coverage**"*. True of the transport change; false of the document as a whole.
3. [`contract/tad-deferrals.json`](../../contract/tad-deferrals.json) holds **no entry** for any of the four metrics or the three FRs — I checked all seven strings.

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-SEC-04 | Security / live | `prvReadWorkflow` absent from `REV Trustee` in DEV | Not bound | **Bound, `privilegedepthmask` 8 (Global)**, `roleprivilegeid ea54378b-87a0-f111-b8de-70a8a5079a1b` | P2 (expected-red by design) |
| T-SEC-05 | Security / live | `prvWriterev_roundstatisticsrequest` absent from `REV Service Automation` in DEV | Not bound | **Bound, mask 8 (Global)**, `roleprivilegeid 83a7aa39-40a2-f111-b8de-7ced8d43e1b4` | P2 (expected-red by design) |
| T-PROV-06 | Provisioning / live | `rev_roundstatisticsresult` exists in DEV | Present | **ABSENT** — `entity` query returns `rev_roundstatisticsrequest` and `rev_roundfinance` only | P2 (ordering, not defect) |
| T-PROV-07 | Provisioning / live | Table-level `IsAuditEnabled` on the result table | `true` | **Unevaluable** — no table to read it from | — |

**Both privilege failures are the design's own prediction, and that is the point.** [TAD §12.2](../architecture/trustee-portal-visual-refresh-architecture.md#L3196) records each as *"E1 that it will FAIL on the first run"* and *"MEASURED FAILING, not predicted"*, because [`ensure-schema.ps1:747-750`](../../provisioning/dataverse/ensure-schema.ps1#L747) grants privileges and revokes none. My read-backs confirm both, independently, at E1 — which is what makes them a verification rather than an assurance. They clear at [§12.3 step 8](../architecture/trustee-portal-visual-refresh-architecture.md#L3251).

---

## 4. Defects Raised

| Defect ID | Severity | Description | Owner |
|---|---|---|---|
| **D-11** | **P2** | FR-058 partial, FR-059 and FR-060 undelivered; **no deferral record**, and TAD Appendix A presents all three as covered. Risks a phase acceptance above the evidence ([C-COM-006](../../constraints/commercial/commercial-constraints.md#L44)) | architect-agent (matrix + deferral) · commercial-agent (sizing, already flagged as A-R28) |
| **D-12** | **P2** | The write boundary is **not enforced in DEV**: two stale Global privileges live, and the result table absent entirely. Documented as A-R49 and sequenced at §12.3 step 8 — carried as a hard gating item, not a build fault | pipeline-agent |
| D-13 | P3 | [§3.3](../architecture/trustee-portal-visual-refresh-architecture.md#L1049)'s `status` enumeration names five values; the system produces **seven**. The flow's failure path writes `status:"error"` ([`Compose_error_document`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1076)) and the app synthesises `"pending"`. **No behavioural risk** — `types.ts` types `status` as a bare `string` deliberately and falls back correctly — but a reviewer running §6.3.3's V5 key-set assertion against an error document would read two legitimate divergences as failures | architect-agent |
| D-14 | P3 | [`verify-assumption-markers.py`](../../scripts/verify-assumption-markers.py) cannot resolve the percent-encoded path in A-FIN-03's `Where` column, so it emits a NOTE and **exits 0 without checking that OPEN row's marker at all**. The marker is in fact present (I grepped: 1 occurrence). A gate that silently skips a row it was written to check | improvement-agent |
| D-15 | P3 | [`verify-role-privilege-ownership.py`](../../scripts/verify-role-privilege-ownership.py) counts removal **comment occurrences**, not distinct (role, privilege) pairs, so it reports *"3 declared privilege removal(s)"* where there are **two** — `prvReadWorkflow` on `REV Trustee` is detected twice (lines 237 and 395 of the same file). The script's own header says it measures 2. A reader reconciling "3" against the TAD's "TWO grants are withdrawn" hunts for a third that does not exist — and miscounting privilege removals is the exact defect Erratum 5.1 exists to correct | improvement-agent |

**No defect was found in the flow, the freshness logic, the role source, the schema or the app.** D-11 is scope and documents; D-12 is environment ordering; D-13–D-15 are gate and document precision.

---

## 5. Constraint & Compliance Verification

Rows where Scope includes `test-agent`, both files, HARD and SOFT. Every gate below was **re-run by me**, not read from the manifest.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | **PASS** | `domain-invariants` exit 0; the flow's error document carries `status`/`computedOn`/`staleAfterSeconds`/`metrics:null` and no row data |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CUD on sensitive entities audit-logged | **PARTIAL** | Source flags correct; the live table switch is unverifiable — the table does not exist. May not be cited without C-TECH-064, per that row's own text |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit record schema | **PARTIAL** | Same reason |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences scoring | **PASS** | `domain-invariants` exit 0; `no-special-category-data-in-scoring` exit 0. This feature adds no scoring path |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured=1` | **PASS** | `domain-invariants` exit 0, 4 pre-existing exceptions printed as designed. The result table adds **no** register entry — verified: it holds no personal data |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled=1` | **PASS** | `domain-invariants` exit 0. `rev_resultjson`'s `IsAuditEnabled=0` is **not** a violation — it is in no register entry, and the exclusion is documented at the column, at [§3.9.3](../architecture/trustee-portal-visual-refresh-architecture.md#L1367) and at [§6.4.1](../architecture/trustee-portal-visual-refresh-architecture.md#L2077), reasoned on the split making the service identity the only writer. **I checked this specifically because [IMP-0401] names that flag as part of the defect being closed** — it is a deliberate decision, not a repeat |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | **PASS** | `no-hardcoded-environment-values` per manifest; no credential in any artefact I read |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated | **PASS** | The flow consumes **no** input at all (§6.3.1, verified below). The app's type guard validates the document |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Auth enforced | **PASS** | Entra + host-brokered identity, unchanged; no new endpoint |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | **PASS** | 662/662 re-run by me; manifest records 83.1% (1711/2059) against 80%. **Figure checked, not pass count** |
| [C-TECH-040](../../constraints/technology/technology-constraints.md#L82) | Group teams only above DEV | **PASS** | No direct assignment added; DEV's direct model unchanged |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent + convergence + **removal owes a revoke and an absence read-back** | **FAIL (live), PASS (source)** | `provisioning-step-convergence` exit 0; `role-privilege-ownership` exit 0 with both removals sequenced. **The live half fails and is expected to** — D-12 |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | DLP connector groups | **PASS** | Every connector on both sides is `shared_commondataserviceforapps`. ADR-038 closed this by deleting the second group |
| [C-TECH-046](../../constraints/technology/technology-constraints.md#L88) | No OOB role modified | **PASS** | Three custom roles only; the *App Opener* equivalence argument has no subject any more |
| [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | Code Apps use CLI-generated data sources | **PARTIAL** | `code-app-data-sources` passes **only with `--allow`** for `rev_roundstatisticsresults`, because the table does not exist for `pa app add data-source` to read. Correctly handled: neither generated file was hand-edited (`grep -c` → 0 in both). First use of the escape hatch; clears at §12.3 step 9 |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform ids | **PASS** | `root-components-resolve` per manifest; the three A-RESULT-1/A-FLOW-07/A-RES-1 rows correctly record the entity-set name as a guess rather than asserting it |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Assumptions registered with a source marker | **PASS with one gate gap** | `assumption-markers` exit 0, `assumption-register` exit 0, `component-shape` per manifest. **No orphans found.** D-14 is the gate's blind spot, not a missing row |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | **PASS** | §7.2. No level claimed above evidence anywhere in this report |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Cross-OS | **NOT TESTED** | Everything ran on macOS. No CI run exists for this feature; the manifest states the same |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | **PASS** | Dev Summary §11 records the eleven mutations each reverted and the file confirmed byte-identical by checksum |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate proven able to fail | **PASS** | `flow-reads-no-trigger-body --selftest` **15/15**, and it **discriminates**: against this file's pre-edit state it exits 1, against the shipped state 0. `verify-build-config.py` PASS |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | An OPEN assumption blocks deployment where it could be closed | **FAIL — reviewer action required** | 10 OPEN rows. Seven are not closeable (they need the table or a live run). **Three are closeable in DEV today by a human** — A-FIN-03, A-TR-13, A-DS-1 — so this row is red until the V4 step runs or the reviewer records `OVERRIDE` per row |
| [C-TECH-059](../../constraints/technology/technology-constraints.md#L129) | Learning substrate never destroyed | **PASS** | Artifact dir unique; `generate-known-failure-modes.py --check` current at 447 entries; findings appended below |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | Length limits | **PASS** | `field-length-limits` per manifest, 257 flow descriptions ≤ 256 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | **Environment state verified LIVE, and a metadata assertion is inadmissible for a trigger** | **FAIL** | I ran four live reads. Two privilege absences **fail**; the result table is **absent**; and the observed-effect assertion has not been performed by anyone. **I make no trigger claim from `callbackregistration`** — clause (a) forbids it, and the shipped `message: 3` reading *Modified* live is admissible only for the enumeration, not for firing |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | Credential ≠ identity ≠ permission | **PASS** | My own live reads authenticated and returned data as `svc_grantapplications` against `REV-GrantApplications-DEV` |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | The TAD is a checked specification | **FAIL** | `tad-coverage` exit 0 for §3.1's 174 column specs (8 deferred, owned). **But the gate reads the schema table, not Appendix A** — and Appendix A is where D-11 lives. This is a real gap in the gate's reach, stated rather than absorbed |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Source-derived counts (SOFT) | **WARN** | 11 pre-existing fragile literal counts, none introduced here. D-15 is a fresh instance in a **gate's own summary line** |
| [C-TECH-068](../../constraints/technology/technology-constraints.md#L138) | Negative access results need live-verified controls | **NOT TESTED** | No access test run this cycle. `no-trustee-in-column-security-profile` exit 0 (4 membership lists, 2 settings files) — source side only |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Plurality and (table, column) identity | **PASS** | `source-reader-plurality` per manifest; `code-app-column-bindings` OK over 101 files against 63 forbidden columns across 9 tables |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Column security protects a stored value, not a projection | **PASS** | `field-security-coverage` exit 0, 68 secured pairs, the two standing warnings unchanged. The result table adds no secured column |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | A declared property must reach the creation path | **PASS with a recorded gap** | `declared-property-reaches-creation-path` exit 0; the one `IsAuditEnabled`-on-lookup-body gap carries owner `development-agent` and is latent |
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) | Metadata writes are PUT, never PATCH | **PASS** | `metadata-write-verbs` per manifest, 73 calls across 36 scripts |

**Gates I re-ran myself, with exit codes:** `flow-trigger-body-isolation` 0 · `--selftest` 0 (15/15) · `column-security-membership` 0 · `role-privilege-ownership` 0 · `superseded-column-writers` 0 · `domain-invariants` 0 · `code-app-column-bindings` 0 · `field-security-coverage` 0 · `assumption-markers` 0 · `assumption-register` 0 · `tad-coverage` 0 · `improvement-log` 0 · `improvement-log --check` 0 · `digest --check` 0 · `audited-tables` 0 · `constraint-verifiers` 0. **Sixteen of sixteen exit 0.**

---

## 6. Provisioning Verification

Live reads against `REV-GrantApplications-DEV` (`https://orge2b20d13.crm17.dynamics.com/`) as `svc_grantapplications`, by me, 2026-08-28.

| Item (TAD §12 / §6.1.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundstatisticsrequest` exists | Present | `entity` FetchXML | **PASS** — `objecttypecode 10,788` |
| `rev_roundfinance` exists | Present | same query | **PASS** — `objecttypecode 10,787` |
| `rev_roundstatisticsresult` exists | Present | same query | **FAIL — ABSENT.** §12.3 step 3 has not run |
| `REV Trustee` → request table | Read + Write (Global) | `roleprivileges` ⋈ `role` ⋈ `privilege` | **PASS** — both bound at mask 8 |
| `REV Trustee` → result table | Read only | same | **UNEVALUABLE** — no table, so no privilege exists |
| `REV Service Automation` → request table | Read **only** | same | **FAIL** — Read bound *and* Write still bound (D-12) |
| `REV Service Automation` → result table | Read + Write | same | **UNEVALUABLE** — no table |
| `prvReadWorkflow` on `REV Trustee` | Absent | same | **FAIL** — bound at mask 8 (D-12) |
| Result-table auditing | `IsAuditEnabled=true` | — | **UNEVALUABLE** — no table |
| Trigger fires (observed effect) | `rev_computedon` changes | — | **NOT PERFORMED** — impossible; the flow's first read is the absent table |

**`prvWriterev_roundstatisticsrequest` on `REV Trustee` is bound and must stay bound.** I checked both halves against role source before reporting, because a privilege named without its role is half a fact: it is deliberate at [`REV Trustee.xml:252`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L252) — the trustee writes the ask — and stale only on the service role at [`REV Service Automation.xml:166`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L166). **Revoking it from the trustee role would break Refresh Figures for every trustee.**

---

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

Closing precondition stated as its own fact, separately from status, and answered fresh this cycle.

| ID | Claim | Status per §10 | Closing precondition | Exists yet? | Verified by me | Result |
|---|---|---|---|---|---|---|
| A-FLOW-01, -02, -04, -05 | Power Apps trigger / `Response` / `prvReadWorkflow` sufficiency | SUPERSEDED | — | — | Confirmed superseded: **zero** `Response` actions in the definition; trigger is `OpenApiConnectionWebhook` | **CLOSED, correctly** |
| A-FLOW-03 | `Secure Outputs` semantics | OPEN | A live flow run | **No** | `secureData.properties:["outputs"]` set on the applicant-reading action | Correctly OPEN |
| A-FLOW-06 | `$expand` as a literal `List rows` key | OPEN | A designer save / live run | **No** | Parameter present as specified | Correctly OPEN |
| A-FLOW-07 | Entity set + primary id, flow side | OPEN | The table existing | **No — I verified** | Six literals consistent with `schema.ts` | Correctly OPEN |
| A-RESULT-1 | `EntitySetName` = `rev_roundstatisticsresults` | OPEN | The table existing | **No — I verified** | Marker present at the element | Correctly OPEN |
| A-RES-1 | App's copy of both names | OPEN | The table existing | **No — I verified** | Written once, referenced from `ENTITY_SETS` | Correctly OPEN |
| A-LAND-3 | Three proportions' shape | OPEN | OQ-039 + a populated response | **No** | Inferred shape marked at `types.ts:305` | Correctly OPEN |
| A-LAND-4 | Break-type total row shape | OPEN | A real `breakTypeProfile` | **No** — and see D-11: nothing computes it | Marked at `roundStatistics.ts:287` | Correctly OPEN |
| A-FIN-03 | Decimal control classid | OPEN | **A human in the maker portal — DEV exists** | **YES** | Marker present (grepped, 1 occurrence) — but **the gate never checked it**, D-14 | **C-TECH-058 red** |
| A-TR-13 | Multiselect wire shape | OPEN | **One live read as a signed-in user — DEV exists** | **YES** | Fail-safe path confirmed in `odata.ts` | **C-TECH-058 red** |
| A-DS-1 | `muted` vs `quiet` visually distinct | OPEN | **One V4 sign-in — DEV exists** | **YES** | Two classes, two backgrounds, 1.07:1 apart | **C-TECH-058 red** |

**Orphans (`C-TECH-052`): none.** `assumption-markers` exit 0 across 14 OPEN rows in 4 documents, and I found no hand-authored contract in this feature without a register row.

**Three rows are closeable in DEV today and are not closed.** That is [C-TECH-058](../../constraints/technology/technology-constraints.md#L128)'s exact condition — the environment is the means of closing a guess, not a reason to defer it. All three close in the same single V4 sign-in that A-R39 already schedules.

### 7.2 Verification levels achieved

| Component | Level claimed (§11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Flow: trigger, guard, freshness read, five write-backs | V2 | **V2** | `pac solution pack` both types exit 0; hosted Solution Checker 0/0/0/0/0, correlation `0f491b73-d337-4c61-884d-15112c677329` | **CONFIRMED** |
| `subscriptionRequest/message: 3` | E1 live | **E1** | `stringmap`: 2 = Deleted, 3 = Modified. Admissible for the enumeration **only** | **CONFIRMED** |
| `rev_roundstatisticsresult` + 4 attributes + key | V2 | **V2** | Packs; `root-components-resolve` 70 components; **absent from DEV — I verified** | **CONFIRMED** |
| Code App result read + age-bound freshness | V2 | **V2** | 662/662 re-run by me, exit 0 | **CONFIRMED** |
| Freshness predicate | V4 by mutation | **V4 by mutation** | Four mutants; the survivor (null stamp aging as `0`) was fixed and re-killed. Current code returns `NaN` for a null stamp — I read it | **CONFIRMED — the strongest result in the revision** |
| `flow-reads-no-trigger-body` gate | V4 by mutation | **V4 by mutation** | `--selftest` 15/15; discriminates against the pre-edit file | **CONFIRMED** |
| Rollout order | V1 | **V1** | `verify-pipeline-config.py` PASS, 104 steps. Steps 3–9 are live actions nobody has taken | **CONFIRMED** |
| Whole ADR-038 mechanism | — | **V0 end-to-end** | Never executed. The table it depends on does not exist | **NOT REACHED** |

- Idempotency re-run: **N/A** — no deploy has occurred.
- **V4 designer open + save: NOT PERFORMED.** Owner: reviewer / pipeline-agent, at §12.3 step 6, designer only.
- Cross-OS (C-TECH-054): **NOT TESTED** — macOS only.
- Warnings triaged (C-TECH-055) / diagnostics removed (C-TECH-056): **PASS** — 98 warnings, 0 untriaged.

**No level in this report rests on a metadata assertion about the trigger.** [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) clause (a) rules out `statecode`, a `callbackregistration`'s existence, `createdon`, `scope`, `runas` and a Resubmit — six findings each added one field to that list and each was defeated by the next incident.

---

## 8. The five dispatch items, answered

**1. The flow reads nothing from its trigger body — PASS (V2).** Zero occurrences of `triggerBody`, `triggerOutputs`, `@triggerBody`, `rev_triggeredon`, `modifiedby`, `owninguser` or `modifiedonbehalfby` anywhere in the 81 KB definition. The trigger's own action name `When_a_refresh_is_requested` appears **exactly once** — its declaration — so no action references it. Every value the flow uses comes from its own four `ListRecords` queries. Gate exit 0; selftest 15/15; discriminates against the pre-edit file.

**2. The result is composed from an enumerated field list — PASS (V2).** [`Compose_response_body`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1076) writes all **6** top-level keys and all **14** metric keys by name through `concat`. **The key set equals §3.3's exactly** — I compared both sets element by element; no extra key, no missing key. Every reference to the applicant collection is inside `length(...)` or a `Filter array`'s `from`; the filter results are consumed only as `length(body(...))`. **Nothing serialises a row anywhere**, and both writes flatten to `item/<column>` — the shape that writes nothing while succeeding if nested.

**3. The write-boundary split — PASS in source, FAIL in DEV.** Source is exactly §6.1.1: trustee Read+Write on the request table and **Read only** on the result table; service identity Read on request and Read+Write on result; no Create, no Delete for either; no `prvReadWorkflow` on `REV Trustee`. **But none of it is enforced in DEV.** The result table does not exist, so the trustee's Read-only privilege has no subject, and both stale grants are still bound Global — I read all of it live. **IMP-0401 is closed in source only.** The audit half of that finding is separately sound: `rev_resultjson`'s `IsAuditEnabled=0` is a documented decision resting on the split making the service identity the only writer, not a repeat of the flag the old design left off.

**4. Freshness is an age bound — PASS (V2).** [`isCurrent`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts#L469) is one comparison: `ageInSeconds(read.computedOn, now) <= (read.document?.staleAfterSeconds ?? NaN)`. A null stamp yields `NaN`, an unparseable stamp yields `NaN`, an absent document yields no bound, and a null bound yields `NaN` — every "cannot tell" fails the same operator. **No request identity exists anywhere in the mechanism.** There is no fallback bound, which is the fail-safe direction. 43/43 tests pass, and the one mutation that survived the first pass is fixed and re-killed.

**5. A-R48 is recorded as accepted, not silently mitigated — PASS.** [A-R48](../architecture/trustee-portal-visual-refresh-architecture.md#L3081) is titled *"ACCEPTED RESIDUAL"*, states *"Accepted, not mitigated"*, and explicitly refuses to present `staleAfterSeconds` as a control: *"this document declines to present a rate limit as a confidentiality boundary."* [§6.3.4](../architecture/trustee-portal-visual-refresh-architecture.md#L2009) gives the same position at length and says why suppression would not help. **It is correctly recorded**, and it carries a live reviewer decision — *accept, or set `S` large* — which is item 1 in §9.

---

## 9. Recommendations

**Fix D-11 before any phase acceptance, not before deploying.** Two small edits: mark FR-058 partial and FR-059/FR-060 undelivered in Appendix A, and add an owned, dated `contract/tad-deferrals.json` entry for the four `null` metrics. Whether to **build** them is a sizing question that A-R28 already routes to commercial-agent — do not fold it in here.

**Then run §12.3 in order.** Step 1 (capture and reconcile the live definition) has been done; steps 3–9 have not. Step 7's observed-effect assertion is the one that decides whether this design works at all, and nothing cheaper substitutes for it.

**Close the three closeable assumptions in the same V4 sign-in.** A-FIN-03, A-TR-13 and A-DS-1 all close in one private-window session that A-R39 already requires. That clears C-TECH-058 without an override.

**Answer OQ-042 or leave it unseeded.** Unseeded is the fail-safe and needs no deployment. The only reason to set `S` is A-R48.

**Re-test scope for v5:** the §12.2 V5 row assigned to me (read `rev_resultjson` live, assert the key set and leaf types), the gender-distribution reconciliation against an admin tally (A-R45 — a non-empty chart is not sufficient), latency (A-R36), and the two privilege absence read-backs after step 8.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0451 | `approved-document-internally-inconsistent` | rework | A traceability matrix row naming a response field is not evidence the field is populated — grep the composing expression for a literal `null` before reading an Appendix A row as coverage, and pair every undelivered requirement with a dated deferral entry. |
| IMP-0452 | `gate-reassures-wrongly` | friction | `verify-assumption-markers.py` exits 0 while silently skipping any OPEN row whose `Where` path is percent-encoded — resolve the path or FAIL, because a row the gate cannot read is a row nothing checks. |
| IMP-0453 | `hand-maintained-count-drifts-from-source` | friction | `verify-role-privilege-ownership.py` counts removal comment occurrences, not distinct (role, privilege) pairs, so a second explanatory comment inflates the number a reviewer reconciles against the design document. |
| IMP-0454 | `approved-document-internally-inconsistent` | friction | TAD §3.3's `status` enumeration names five values where the system produces seven — `error` from the flow's failure path and `pending` synthesised by the app — so §6.3.3's V5 key-set assertion reads two legitimate divergences as failures. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
