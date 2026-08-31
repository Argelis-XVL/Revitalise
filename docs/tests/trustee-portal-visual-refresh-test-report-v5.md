# Test Report (v5) — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** trustee-portal-visual-refresh
**Artifact:** `build/artifacts/trustee-portal-visual-refresh-20260828-3/`
**WBS:** `6.9` — not one of the 61 base tasks; made a covered id by [CO-001](../../contract/change-orders/CO-001.md#L30), so [C-COM-002](../../constraints/commercial/commercial-constraints.md#L35) is satisfied
**Date:** 2026-08-28
**Supersedes:** [v4](trustee-portal-visual-refresh-test-report-v4.md) — this cycle tests TAD Revision 6 (ADR-039 and the `k = 5` gate), which v4 predates
**Status: FAIL** — and the reason has completely changed since v4

---

## 0. Read this first

**The Revision 6 work is sound, and I verified its structure myself rather than reading the claim.** All four money measures compose; the `k = 5` threshold is enforced by an expression on every one of them, not by a sentence in a document; and the empty-group `NaN` failure that would have taken all thirteen metrics off the screen is removed at source, in the right order. **v4's headline failure (D-11) is substantively closed** — the three requirements are delivered and the deferral register agrees.

**The FAIL is now entirely environment-side, and none of it is new.** `rev_roundstatisticsresult` still does not exist in DEV, both stale Global privileges are still bound, and the `k` row that carries the approved disclosure value is seeded in no environment at all. I read all four facts live. **D-12 is the same open P2 defect v4 raised**, and three assumptions that a single DEV sign-in would close are still open.

**The honest ceiling is unchanged: V2, plus three live queries against DEV that I ran myself, covering seven checks.** Nothing in this feature has ever executed. `xml()` and `xpath()` have never run on this tenant, which is the one contract the whole money mechanism rests on.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (code app, re-run by me) | 676 | 676 | 0 | 0 |
| Unit / Integration (Pester, re-run by me) | 995 | 994 | 0 | 1 |
| Integration (flow contract, re-run by me) | 47 | 47 | 0 | 0 |
| Integration (flow structure, derived by me) | 12 | 12 | 0 | 0 |
| End-to-End (V5) | 0 | — | — | **all — no environment** |
| Regression | 676 | 676 | 0 | 0 |
| Security / disclosure control | 14 | 12 | 2 | 0 |
| Accessibility | 3 | 3 | 0 | — |
| Performance | 0 | — | — | **all — A-R36, needs V5** |
| Provisioning (live E1 reads) | 5 | 1 | 4 | 0 |
| Compliance / constraint | 33 | 25 | 3 | 4 |
| **Total executed** | **2461** | **2446** | **9** | **5** |

The constraint row is 33 rows in scope (6 domain, 27 technology), of which 4 are unevaluable and **1 is a SOFT warning** counted in neither the passed nor the failed column.

`npx vitest run` → **676 passed / 38 files, exit 0**, and `Invoke-Tests.ps1` → **994 passed / 0 failed / 1 skipped in 138.7 s**. Both re-run by me and both match [manifest.json](../../build/artifacts/trustee-portal-visual-refresh-20260828-3/manifest.json) exactly. **I did not restate a single figure from the manifest without re-running it**, which is the difference between this table and a summary.

The four provisioning failures and the two security failures overlap: they are three live facts, counted once per layer because each layer asks a different question of them.

---

## 2. Requirement Coverage

Derived by me from [TAD Appendix A](../architecture/trustee-portal-visual-refresh-architecture.md#L3833) against what the shipped flow actually composes — I read the composing expression for every row rather than trusting the matrix, which is exactly the check v4 established.

| FR ID | Requirement | Test case / evidence | Result |
|---|---|---|---|
| FR-057 | One open round, no selector | App direct-reads `rev_roundfinance`; flow asserts the same invariant in [`Switch_on_open_round_count`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L309) with explicit zero / ambiguous branches | **PASS** (V2) |
| FR-058 | Total received · round-open date · average per day | [`Compose_applications_per_day`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1210) composes a real figure; denominator convention carried as an open question, not guessed | **PASS** (V2) — was PARTIAL in v4 |
| FR-059 | Exceptional-circumstance counts · total and % citing any · average exceptional funding | All four fields compose. [`Compose_exceptionalfunding_average_amount`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1210) emits `{value, population}` over its own presence subset | **PASS** (V2) — was FAIL in v4 |
| FR-060 | Break-type breakdown, four measures + total row | Counts plus all three money measures on all five rows **and** the total row, each with its own denominator. [`Compose_breaktype_rows`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1217) | **PASS** (V2) — was FAIL in v4 |
| FR-061 | Gender · age-range · applicant-type · ethnic group | First three computed; `ethnicGroupDistribution` null and acquitted by the coverage gate against its Appendix A marker | **PASS as designed** (V2) |
| FR-062 | Wellbeing · life satisfaction · three proportions | Both distributions computed; three proportions null pending OQ-039 | **PASS as designed** (V2) |
| FR-063 | Round finance figures | Direct trustee read of `rev_roundfinance` | **PASS** (V2) |
| NFR-013 | Nothing persisted | Correctly withdrawn in Revision 5 | **PASS** |
| NFR-021, NFR-022 | Latency | Not measured. Needs V5 | **NOT TESTED** |
| NFR-024, NFR-026 | Accessibility, brand | Table semantics checked in source; no screen has ever been rendered | **PARTIAL — see §7.2** |

**The three requirements v4 failed on are genuinely delivered.** `python3 scripts/verify-tad-coverage.py` exits 0 and reports **0 undelivered-requirement entries**, and [`contract/tad-deferrals.json`](../../contract/tad-deferrals.json#L48) records UR-001, UR-002 and UR-003 all cleared with dated reasons. **D-11 is closed** apart from one presentation residue, D-18 below.

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-PROV-06 | Provisioning / live | `rev_roundstatisticsresult` exists in DEV | Present | **ABSENT** — `entity` query returns only `rev_roundstatisticsrequest` (10,788), `rev_roundfinance` (10,787) and `rev_setting` (10,632) | P2 (carried, D-12) |
| T-SEC-04 | Security / live | `prvReadWorkflow` absent from `REV Trustee` in DEV | Not bound | **Bound, mask 8 (Global)**, `roleprivilegeid ea54378b-87a0-f111-b8de-70a8a5079a1b` — byte-identical to v4 | P2 (carried, D-12) |
| T-SEC-05 | Security / live | `prvWriterev_roundstatisticsrequest` absent from `REV Service Automation` in DEV | Not bound | **Bound, mask 8**, `roleprivilegeid 83a7aa39-40a2-f111-b8de-7ced8d43e1b4` — byte-identical to v4 | P2 (carried, D-12) |
| T-PROV-08 | Provisioning / live | The `k` disclosure control is seeded in DEV | `RoundStatisticsMoneyMeasureMinimumPopulation = 5` | **NO ROW** — a `rev_setting` query on `RoundStatistics%` returns nothing at all | P3 (D-16) |

**Neither privilege has moved since v4 — same ids, same masks.** [TAD §12.3](../architecture/trustee-portal-visual-refresh-architecture.md#L3806) step 8 is the step that clears them and it has not run. I re-read them rather than carrying v4's result forward, because a live fact is only true for the date it was read.

**`prvWriterev_roundstatisticsrequest` on `REV Trustee` is bound and must stay bound.** I checked the role half before reporting the privilege half: it is deliberate — the trustee writes the refresh request — and stale only on the service role. Revoking it from the trustee would break Refresh Figures for every trustee.

---

## 4. Defects Raised

| Defect ID | Severity | Description | Owner |
|---|---|---|---|
| **D-12** | **P2** | **Carried unchanged from v4.** The write boundary is not enforced in DEV: two stale Global privileges live and the result table absent. Correct in source; unconverged in the environment. Sequenced at [§12.3](../architecture/trustee-portal-visual-refresh-architecture.md#L3806) step 8 | pipeline-agent |
| D-16 | P3 | **The `threshold-unset` status is declared and never emitted.** [TAD §3.3](../architecture/trustee-portal-visual-refresh-architecture.md#L1271) enumerates it and the app fully implements it ([types.ts:304](../../src/code-apps/trustee-review-portal/src/dataverse/types.ts#L304), [landing.ts:143](../../src/code-apps/trustee-review-portal/src/domain/landing.ts#L143), tested); the flow contains **zero** occurrences. With the `k` row absent in DEV (T-PROV-08) the first live run emits `status: ok` with all four money measures withheld — **indistinguishable from a genuine below-threshold round**, which is the one state the diagnostic exists to separate | architect-agent · development-agent |
| D-17 | P3 | **The flow's declared failure-diagnosis exception now hides 167 actions.** `verify-flow-definition-language.py` prints the number and warns that growth weakens the fail-loud claim resting on it; the Dev Summary recorded it at *84 more than when declared*. Every new ADR-039 action sits inside it, so a failure in the one mechanism carrying an unverified platform contract reaches the alert as a wrapper message naming nothing. Owned and dated 2026-09-30, so not a gate violation — but the risk profile changed with Revision 6 and the exception was not re-examined | development-agent |
| D-18 | P3 | **Two Appendix A rows lead with a superseded verdict.** [FR-059](../architecture/trustee-portal-visual-refresh-architecture.md#L3845) opens *"PARTIAL, and the split is exact… `averageAmountRequested` remains a literal `null`"* and [FR-060](../architecture/trustee-portal-visual-refresh-architecture.md#L3846) opens *"PARTIAL, and mostly still open… Three remain literal `null`"* — each corrected by appending *"UPDATE: DELIVERED IN FULL"* at the end of the same cell rather than rewriting the opening claim. A reader scanning the matrix reads the first verdict. This is the mirror image of v4's D-11 and the same class of harm | architect-agent |

**No defect was found in the flow's arithmetic, the `k` gate, the guards, the app's parser, the role source or the schema.** D-12 is environment convergence; D-16 and D-18 are contract and document precision; D-17 is diagnosability.

---

## 5. Constraint & Compliance Verification

Rows where Scope includes `test-agent`, both files, HARD and SOFT. **Every gate below was re-run by me**, not read from the manifest.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in application logs | **PASS** | `domain-invariants` exit 0; the error document carries status and timestamps only, no row data |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) | CUD on sensitive entities audit-logged | **PARTIAL** | Source flags correct; the live table switch is unverifiable — the table does not exist |
| [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit record schema | **PARTIAL** | Same reason |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences scoring | **PASS** | `domain-invariants` exit 0. This feature adds no scoring path |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) | Register columns carry `IsSecured=1` | **PASS** | `domain-invariants` exit 0, 4 pre-existing exceptions printed as designed |
| [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns carry `IsAuditEnabled=1` | **PASS** | `domain-invariants` exit 0 — 20/20 enabled, 4 documented exceptions |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No hardcoded secrets | **PASS** | No credential in any artefact I read; three money columns and the setting key are the only new literals |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated | **PASS** | The flow consumes no trigger input at all (gate check A, below). `parseMoneyMeasure` drops any measure lacking a numeric population |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Auth enforced | **PASS** | Entra + host-brokered identity, unchanged; no new endpoint |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | **PASS** | 676/676 re-run by me; manifest records 83.1% (1711/2059) against 80%. **Figure checked, not pass count** |
| [C-TECH-040](../../constraints/technology/technology-constraints.md#L82) | Group teams only above DEV | **PASS** | No direct assignment added |
| [C-TECH-042](../../constraints/technology/technology-constraints.md#L84) | Idempotent + convergence + removal owes a revoke and an absence read-back | **FAIL (live), PASS (source)** | `role-privilege-ownership` exit 0, **2 distinct removals correctly counted by (role, privilege)** — v4's D-15 is fixed. The live half fails and is expected to — D-12 |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | DLP connector groups | **PASS** | Every connector on both sides is `shared_commondataserviceforapps` |
| [C-TECH-046](../../constraints/technology/technology-constraints.md#L88) | No OOB role modified | **PASS** | Three custom roles only, 95 table privileges |
| [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | Code Apps use CLI-generated data sources | **PARTIAL** | `code-app-data-sources` exits **1** bare and passes only with the declared `--allow`, which carries a reason, an owner and a clearing condition. The escape hatch is correctly used, not abused; clears at §12.3 step 9 |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform ids | **PASS** | The entity-set-name rows still record their guess as a guess |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Assumptions registered with a source marker | **PASS** | `assumption-markers` exit 0 — **19 OPEN rows, every one carrying its marker**; `assumption-register` exit 0, 63 rows. **No orphans.** A-FLOW-11's marker is at every `Compose_*_sum`, which I confirmed by reading them |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | **PASS** | §7.2. No level in this report rests on anything I did not execute |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Cross-OS | **NOT TESTED** | Everything ran on macOS. No CI run exists for this feature |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | Diagnostic components removed | **PASS** | Dev Summary §11 records each mutation reverted |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate proven able to fail | **PASS** | `flow-trigger-body-isolation --selftest` **20/20** (grown from 15/15 with the new actions); `verify-build-config.py` PASS, 67 steps, 52 gates, all with negative-test coverage |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | An OPEN assumption blocks deployment where it could be closed | **FAIL — reviewer action required** | **Three rows are closeable in DEV today and are still open**, unchanged since v4: A-FIN-03, A-TR-13, A-DS-1. All three close in the single V4 sign-in A-R39 already schedules |
| [C-TECH-059](../../constraints/technology/technology-constraints.md#L129) | Learning substrate never destroyed | **PASS** | Artifact directory unique; `generate-known-failure-modes.py --check` current at 476 entries |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | Length limits | **PASS** | Per manifest; no new description exceeds 256 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state verified LIVE | **FAIL** | I ran three live queries covering seven checks. The result table is **absent**, two privilege absences **fail**, the `k` row is **absent**, and the observed-effect assertion has not been performed by anyone. **I make no trigger claim from `callbackregistration`** — clause (a) forbids it |
| [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | Credential ≠ identity ≠ permission | **PASS** | My reads authenticated and returned data as `svc_grantapplications` against `REV-GrantApplications-DEV` |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | The TAD is a checked specification | **PASS with a narrowed gap** | `tad-coverage` exit 0 over 174 column specs and **129 Appendix A rows** — the gate now reaches Appendix A, which is what v4 recorded as missing. It still **counts** status values rather than comparing the two sets, which is how D-16 survives it |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Source-derived counts (SOFT) | **WARN** | 3 pre-existing prose/source count drifts, none introduced here |
| [C-TECH-068](../../constraints/technology/technology-constraints.md#L138) | Negative access results need live-verified controls | **NOT TESTED** | No access test run this cycle |
| [C-TECH-069](../../constraints/technology/technology-constraints.md#L140) | Plurality and (table, column) identity | **PASS** | `code-app-column-bindings` OK over 101 files, 63 forbidden columns, 9 tables |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Column security protects a stored value, not a projection | **PASS** | 68 secured pairs unchanged. **The three money columns are `IsSecured=0` and none is securable in full** — which is precisely why `k` exists rather than column security |
| [C-TECH-071](../../constraints/technology/technology-constraints.md#L142) | A declared property must reach the creation path | **PASS with a recorded gap** | Unchanged from v4 — the one `IsAuditEnabled`-on-lookup-body gap carries owner `development-agent` and is latent. Revision 6 adds no declared property |
| [C-TECH-073](../../constraints/technology/technology-constraints.md#L143) | Metadata writes are PUT, never PATCH | **PASS** | Per manifest; this feature adds no metadata write |

**Gates I re-ran myself, with exit codes:** `tad-coverage` 0 · `improvement-log` 0 · `improvement-log --check` 0 · `digest --check` 0 · `assumption-markers` 0 · `assumption-register` 0 · `superseded-column-writers` 0 · `domain-invariants` 0 · `role-privilege-ownership` 0 · `flow-definition-language` 0 · `flow-trigger-body-isolation` 0 · `--selftest` 0 (20/20) · `build-config` 0 · `pipeline-config` 0 · `audited-tables` 0 · `code-app-column-bindings` 0 · `code-app-data-sources` **1 bare / 0 with the declared allow**. **Sixteen of seventeen exit 0**, and the seventeenth is the documented escape hatch.

---

## 6. Provisioning Verification

Live reads against `REV-GrantApplications-DEV` as `svc_grantapplications`, by me, 2026-08-28.

| Item (TAD §12) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundstatisticsrequest` exists | Present | `entity` FetchXML | **PASS** — `objecttypecode 10,788` |
| `rev_roundfinance` exists | Present | same query | **PASS** — `objecttypecode 10,787` |
| `rev_roundstatisticsresult` exists | Present | same query | **FAIL — ABSENT.** §12.3 step 3 has not run |
| `RoundStatisticsMoneyMeasureMinimumPopulation` seeded | `5` | `rev_setting` FetchXML on `RoundStatistics%` | **FAIL — NO ROW.** Seeded 5 in all three settings files and asserted by Pester; present in no environment |
| `prvReadWorkflow` on `REV Trustee` | Absent | `roleprivileges` ⋈ `role` ⋈ `privilege` | **FAIL** — bound at mask 8 |
| `prvWriterev_roundstatisticsrequest` on `REV Service Automation` | Absent | same | **FAIL** — bound at mask 8 |
| `prvWriterev_roundstatisticsrequest` on `REV Trustee` | **Bound** | same | **PASS** — deliberate; must not be revoked |
| Trigger fires (observed effect) | `rev_computedon` changes | — | **NOT PERFORMED** — impossible; the flow's first read is the absent table |

**The `k` row's absence is disclosed, not hidden** — the Dev Summary flags it and says a first live look showing no money figures is not evidence of a defect. I verified it live because a disclosed intention and an environment fact are two different things, and this is the fourth time on this project that gap has mattered.

---

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

Closing precondition stated as its own fact, separately from status, and answered fresh this cycle.

| ID | Claim | Status per §10 | Closing precondition | Exists yet? | Verified by me | Result |
|---|---|---|---|---|---|---|
| A-FLOW-08 | Which mechanism sums a variable-length subset | **RESOLVED** | An architecture decision | — | ADR-039 decides it; 13 sums built on the decided shape | **CLOSED, correctly** |
| A-FLOW-11 | `xml()` over a hand-built string and `xpath(…,'sum(…)')` on this tenant | OPEN | A live run | **No — I verified** | Marker present at every `Compose_*_sum`; expression shape matches ADR-039 exactly | Correctly OPEN |
| A-FLOW-12 | FR-060's *"including exceptional funding"* reading | OPEN | One reviewer sentence | n/a | Both money columns summed per row via `coalesce`, so the reading is implemented and reversible in one expression | Correctly OPEN |
| A-FLOW-09 | `applicationsPerDay` denominator convention | OPEN | One reviewer sentence | n/a | Marker present; deliberately left open by Revision 6 rather than picked | Correctly OPEN |
| A-FLOW-10 | `ticks()` over a date-only column | OPEN | The first live run | **No** | Guarded so neither branch can throw | Correctly OPEN |
| A-FLOW-03, -06 | `Secure Outputs`, `$expand` literal | OPEN | A live run | **No** | Present as specified | Correctly OPEN |
| A-FLOW-07, A-RESULT-1, A-RES-1 | Entity set + primary id for the result table | OPEN | The table existing | **No — I verified** | Literals consistent across flow, `schema.ts` and `READ_SERVICES` | Correctly OPEN |
| A-LAND-3, A-LAND-4 | Proportion and total-row shapes | OPEN | A populated response | **No** | A-LAND-4 is now closer — the total row has real money fields to observe | Correctly OPEN |
| A-FIN-03 | Decimal control classid | OPEN | **A human in the maker portal — DEV exists** | **YES** | Still OPEN, unchanged since v4 | **C-TECH-058 red** |
| A-TR-13 | Multiselect wire shape | OPEN | **One live read as a signed-in user — DEV exists** | **YES** | Still OPEN, unchanged since v4 | **C-TECH-058 red** |
| A-DS-1 | `muted` vs `quiet` visually distinct | OPEN | **One V4 sign-in — DEV exists** | **YES** | Still OPEN, unchanged since v4 | **C-TECH-058 red** |

**Orphans (`C-TECH-052`): none.** `assumption-markers` exit 0 across 19 OPEN rows in 4 documents, and I found no hand-authored contract in the Revision 6 work without a register row. **A-FLOW-11 and A-FLOW-12 were both added in the same change that created the thing they describe**, which is the register working as intended.

**Three rows are closeable in DEV today and were closeable in DEV a cycle ago.** That is [C-TECH-058](../../constraints/technology/technology-constraints.md#L128)'s exact condition, and it is the one item on this report that has not moved at all since v4.

### 7.2 Verification levels achieved

| Component | Level claimed (§11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| The ~140 new money-measure actions | V1 + expression-level evaluation | **V2** | `pac solution pack` both types; hosted Solution Checker 0/0/0/0/0, correlation `5e85b101-b3b2-4847-b843-f620eb90b89c` | **CONFIRMED — above the claim** |
| The `k = 5` gate, structurally | V1 | **V2, and V4-by-inspection on ordering** | I derived the `runAfter` graph myself: `Switch_on_open_round_count` runs after `Compose_money_minimum_population`, so `k` exists before any measure composes | **CONFIRMED** |
| XPath 1.0 `sum()` semantics | E1 by measurement against a conformant engine | **E1, narrowly** | Admissible for the *language*, not for the *Logic Apps wrapper*. The document says so itself | **CONFIRMED as narrowed** |
| Flow contract regression test | V1 | **V1** | 47/47 re-run by me, including *"applies the k threshold to the money measures and to NOTHING else"* | **CONFIRMED** |
| Code App money rendering + parser | V2 | **V2** | 676/676 re-run by me, exit 0 | **CONFIRMED** |
| Break-type table semantics | — | **V2 (source)** | `<th scope="col">`, `<th scope="row">`, `<tfoot>`; a withheld measure renders `"Not shown"`, never blank, never `£0.00` | **CONFIRMED in source only** |
| `rev_roundstatisticsresult` + attributes | V2 | **V2** | Packs; **absent from DEV — I verified** | **CONFIRMED** |
| Whole ADR-038 / ADR-039 mechanism | — | **V0 end-to-end** | Never executed. The table it depends on does not exist | **NOT REACHED** |

- Idempotency re-run: **N/A** — no deploy has occurred.
- **V4 designer open + save: NOT PERFORMED.** Owner: reviewer / pipeline-agent, at §12.3 step 6.
- Cross-OS (C-TECH-054): **NOT TESTED** — macOS only.
- Warnings triaged (C-TECH-055): **PASS** — 137 warnings, 0 untriaged.
- **Artifact reproducibility:** the manifest records **107 uncommitted paths** and states plainly that `source_commit` does not fully describe the artifact. Both new `Entity.xml` files are untracked. The manifest is honest about this; I am repeating it because it means this artifact cannot be rebuilt from a commit.

---

## 8. The four dispatch items, answered

**1. Appendix A matches what shipped — PASS, with one presentation residue.** All three requirements are delivered and I confirmed each by reading its composing expression, not its matrix row. The deferral register agrees and the coverage gate reports zero undelivered entries. **What is left is D-18:** the FR-059 and FR-060 rows still *open* with the old PARTIAL verdict and correct themselves only at the end of the cell.

**2. The `k = 5` threshold is structurally enforced — PASS (V2).** It is an expression on every one of the thirteen money composes: `less(length(<its own presence subset>), outputs('Compose_money_minimum_population'))` → the JSON literal `null`. The row's `count` is written independently from its own `Filter array`, so [TAD §3.3's worked example](../architecture/trustee-portal-visual-refresh-architecture.md#L1306) — count 3 published, all three money measures null — is reproduced by construction. **The ordering holds**: I derived the dependency graph rather than reading the document. **And the fail-safe is real** — an absent, empty or non-numeric setting yields `999999999`, a threshold no round can reach under the 1000-row page cap, so every measure is withheld. `k` binds these four measures and nothing else, which the contract test asserts directly.

**3. The `NaN` guard is present and correctly ordered — PASS (V2).** Two failure modes, both removed at source rather than watched for. The empty-node-set case: [`Compose_breaktype1_cost_sum`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L1414) emits **no `<v>` element at all** when the subset is empty, so `sum(/r/v)` sees an empty node set. The empty-element case: the presence `Filter array` excludes null money values upstream, so no blank `<v>` is ever built. The division is then guarded twice — an `empty()` short-circuit before any arithmetic, and `max(length(…), 1)` inside it. **The subtlest part is correct too:** the requested-amount filter admits a row where only one of the two money columns is populated, and the `Select` handles it with `float(coalesce(…, 0))` on both halves, so the `add()` cannot meet a null. `percentageOfCost` adds a third guard against a near-zero cost denominator.

**4. The v4 spot-checks still hold — PASS.** Trigger-body isolation passes checks **A1, A2, A3 and B1** over the now-193-action definition, with 5 personal-data entity sets derived from source; the selftest is 20/20 and can still fail. Enumerated composition is check B1 and it is green. The write-boundary split is correct in source — and, as in v4, unconverged in DEV. **One v4 defect is fixed:** the privilege-removal gate now counts distinct (role, privilege) pairs and reports **2**, matching the design.

---

## 9. Recommendations

**Run [§12.3](../architecture/trustee-portal-visual-refresh-architecture.md#L3806) in order — that is the whole of what stands between this feature and a real verdict.** Steps 3 through 9 have still not been taken. Step 7's observed-effect assertion is the one that decides whether the design works at all, and nothing cheaper substitutes for it.

**Seed `k` in the same pass that creates the table.** It is one `rev_setting` row and it is already in all three settings files. Until it exists, a correct screen and a misconfigured screen look identical.

**Close the three closeable assumptions in one DEV sign-in.** A-FIN-03, A-TR-13 and A-DS-1 have now been open across two test cycles with the environment available throughout. That single session clears C-TECH-058 without an override.

**Fix D-18 with two edits, not two paragraphs.** Rewrite the FR-059 and FR-060 opening verdicts rather than appending to them.

**Decide whether the flow should emit `threshold-unset` (D-16).** The app already handles it. Emitting it costs one condition and turns a silently plausible screen into an explained one. The alternative — deleting it from the enumeration — is also coherent, but leaves nothing distinguishing an unseeded control from a small round.

**Re-test scope for v6:** the §12.2 V5 row assigned to me (read `rev_resultjson` live and assert the key set and leaf types), A-FLOW-11's three-shape test with a deliberately seeded round, the gender reconciliation against an admin tally, latency, and the two privilege absence read-backs after step 8.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0480 | `declared-policy-not-mechanically-enforced` | rework | A disclosure threshold seeded in every settings file is not a control until a row exists in the environment — query the setting live before reporting a minimum-cell-size rule as in force, because an unseeded threshold and a genuinely small population produce the same screen. |
| IMP-0481 | `approved-document-internally-inconsistent` | friction | A status enumeration is a two-way contract: check that every declared value has a producer as well as that every produced value is declared, because a gate that COUNTS values on each side passes over a diagnostic state nothing can ever emit. |
| IMP-0482 | `approved-document-internally-inconsistent` | friction | Correct a traceability row by rewriting its opening verdict, never by appending an UPDATE to the end of the same cell — a reader scanning a matrix reads the first verdict, which is the same harm the appended correction was written to repair. |
| IMP-0483 | `gate-reassures-wrongly` | friction | A declared failure-diagnosis exception must be re-examined whenever the code it covers grows: this flow's exception hid 167 actions after Revision 6 added ~140, so the one mechanism carrying an unverified platform contract fails into a wrapper message naming nothing. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
