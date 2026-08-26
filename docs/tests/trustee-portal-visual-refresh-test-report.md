# Test Report — Trustee Portal Visual Refresh and Round-Statistics Landing Screen

**Feature Slug:** `trustee-portal-visual-refresh`
**Artifact:** `build/artifacts/revitalise-grant-automation-20260825-1/`
**Dev Summary under test:** `docs/development/trustee-portal-visual-refresh-dev-summary.md`
**TAD under test:** `docs/architecture/trustee-portal-visual-refresh-architecture.md` (Revision 2)
**SDD:** `docs/plans/revitalise-grant-automation-plan.md`, Amendments A-02 (APPROVED 2026-08-24) and A-03 (APPROVED 2026-08-25, incl. Resolution continued)
**Date:** 2026-08-25
**WBS:** `6.1`, `6.3`, `6.9` (+ `0.4` per the build manifest) — see §9 defect D-08, three documents state three different scopes
**Model tier:** `strategic`, escalated per `config/models.yml` → `agents.test-agent.escalate_to_strategic_when` (security/compliance test layer is the primary concern)
**Status:** **FAIL**

**Harness mode declared (per `skills/how-to-verify-a-platform-contract.md` §3):** a live cert-based
Dataverse route to DEV (`https://orge2b20d13.crm17.dynamics.com`) **was available and was used**. No
call was refused. Every `V3`/`V4` statement in §7.2 below that says "confirmed live by test-agent"
was re-queried by this session against DEV, not read from the Dev Summary.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — provisioning (Pester) | 876 | 875 | 0 | 1 |
| Unit + Integration — Code App (Vitest, 16 files) | 246 | 246 | 0 | 0 |
| End-to-End | 0 | 0 | 0 | 0 — not executable, see §7.2 |
| Regression — repo gate scripts re-run | 17 | 17 | 0 | 0 |
| Security | 9 | 7 | 2 | 0 |
| Accessibility | 4 | 4 | 0 | 0 |
| Performance | 0 | 0 | 0 | 0 — N/A, no target exists (NFR-022 / OQ-020) |
| Provisioning — live DEV queries | 14 | 14 | 0 | 0 |
| Platform Contract | 4 | 0 | 4 | 0 — all four A-FLOW rows remain OPEN |
| Verification Level | 9 | 8 | 1 | 0 |
| Compliance / Constraint | 33 | 33 | 0 | 0 — 1 SOFT warning, counted as passed |
| **Total** | **1212** | **1204** | **7** | **1** |

Static suites executed by test-agent, not taken from the Dev Summary:

- `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1` → **875 passed, 0 failed, 1 skipped**, 82.18s, exit 0.
- `npm run typecheck` / `npm run lint` / `npm test` in `src/code-apps/trustee-review-portal` → clean; **246/246 in 16 files**, exit 0.
- 17 repository gate scripts re-run individually with bare exit codes captured per `skills/how-to-apply-constraints.md` Step 3 — all exit 0. Full list in §5.

**The two suite numbers disagree with the Dev Summary and the disagreement is in our favour.** Dev
Summary §9 line 150 reports *"874 passed, 1 failed (pre-existing … the improvement-log backlog
trigger)"*. That failure is gone: `scripts/verify-improvement-log.py --check` now exits 0 (9 unread,
0 blockers unread, 31 reviewer-deferred). Recorded as defect D-07 so no reader carries a phantom
failure forward.

---

## 2. Requirement Coverage

Traced against the **built artifact and the live DEV environment**, not against the Dev Summary's
claims. `PARTIAL` means some named element of the requirement is delivered and some is not.

✅ **Read every FR/NFR/OQ number below as belonging to `docs/plans/revitalise-grant-automation-plan.md`** —
which is now the only document allocating them. The collision that made this warning necessary was
**resolved on 2026-08-26** (defect D-09, closed): `revitalise-form-field-corrections-plan.md` was
retired and its requirements merged into the grant-automation plan as Amendment A-04 under
FR-070–FR-077 / NFR-030–NFR-032 / US-020–US-023 / OQ-040–OQ-048. The identifiers used below are
unaffected and unchanged.

| FR ID | Requirement (source: parent SDD) | Test Case(s) | Result |
|---|---|---|---|
| FR-035 | Detail view: redacted narrative, score breakdown, break type + "other" specifier, preferred dates, location, total funding requested incl. exceptional, applicant-type context, care-support context, staff recommendation | TC-035a…f | **PARTIAL** — see below |
| FR-039 | Print/offline export reusing FR-035's field list | TC-039 | **PARTIAL** — inherits FR-035's gaps; brand print-reset present, `computedOn` not applicable yet (no figures) |
| FR-056 | Landing screen as navigation shell | TC-056 | **NOT DELIVERED** — `LandingPage.tsx` absent from the tree and from the built bundle |
| FR-057 | Statistics auto-scoped to the single open round, no selector | TC-057 | **NOT DELIVERED** — no landing screen; `rev_roundfinance` live but holds **0 rows** |
| FR-058 | Total applications received, date round opened, average per day | TC-058a/b | **PARTIAL (flow source only)** — `applicationsReceived` authored; `applicationsPerDay` explicit `null`; flow not deployed |
| FR-059 | Exceptional-circumstance counts, % citing any, average exceptional amount | TC-059 | **NOT DELIVERED** — `exceptionalCircumstanceMix` / `exceptionalFundingSummary` both explicit `null` |
| FR-060 | Break-type breakdown: count, avg cost, avg grant, % of cost, total row | TC-060 | **NOT DELIVERED** — `breakTypeProfile` explicit `null` |
| FR-061 | Gender, ethnic-group, age-range, applicant-type distributions | TC-061a…d | **NOT DELIVERED** — all four `null`; `ethnicGroupDistribution` permanently `null` by design (A-R24, no column exists) |
| FR-062 | Three wellbeing "last year" distributions, life-satisfaction 0–10, three headline proportions | TC-062a…c | **NOT DELIVERED** — all `null`; the three proportions additionally blocked on OQ-039 (TAD-only) |
| FR-063 | Round financial position + charity capacity figures | TC-063 | **PARTIAL** — all 13 columns live and audited in DEV; no UI reads them, no row exists |
| NFR-026 | Full-viewport-width, brand-consistent rendering | TC-N26a/b | **PARTIAL** — full-width half delivered; **brand half explicitly unmet** (`theme.ts` ships Fluent's own default ramp as a declared placeholder, A-R26) |
| NFR-024 | Accessibility (WCAG 2.1 AA per TAD ADR-020) | TC-N24a…d | **PASS for what exists** — contrast ratios documented in `theme.ts`, three-state care panel tested; charts not built so ADR-029's table-first rule is untested |
| NFR-001, NFR-003 | No secured column released; no identifying attribute in a trustee view | TC-SEC-01…04 | **PASS** — confirmed live, §6 |
| NFR-013 | Data minimisation | TC-SEC-05 | **PASS** — the flow selects only `rev_applicationid`; the app binds only `IsSecured=0` columns |
| NFR-019 | Thresholds tunable without a developer | TC-N19 | **NOT EXERCISED** — the `rev_setting` read is not built in this flow version |
| NFR-021 | Scale to ≥250/yr | TC-N21 | **NOT EXERCISED** — no volume in DEV |
| NFR-022 | Performance | — | **N/A** — the SDD records NFR-022 as "NOT SPECIFIED" pending OQ-020. No threshold exists to test against, and none is invented here |

**FR-035 in detail — this is the largest coverage gap and it is wider than the Dev Summary declares.**
TAD §3.2 line 303 lists what ships *"now, with no schema change and no security change"*. Measured
against `APPLICATION_DETAIL_EXTRA_COLUMNS` (`src/code-apps/trustee-review-portal/src/dataverse/schema.ts` line 98):

| TAD §3.2 element | Column | Bound in the app? |
|---|---|---|
| Type of break | `rev_breaktype` | ✅ yes (schema.ts:101) |
| The "other" break specifier | `rev_otherbreaktype` | ❌ **no** — undeclared gap |
| Preferred dates | *no column exists* | ❌ **unbuildable** — see D-04 |
| Break location | `rev_breaklocation` | ✅ yes |
| Total funding requested | `rev_amountrequested` | ⚠️ **partial** — bound (schema.ts:104) and labelled *"Amount requested"*, which is honest |
| …plus the additional amount | `rev_additionalamountrequested` | ❌ **no** — undeclared gap |
| …plus the exceptional flag | `rev_exceptionalfundingrequested` | ❌ **no** — undeclared gap |
| Applicant-type context | `rev_applicanttype` (on `rev_applicant`) | ❌ no — declared in Dev Summary §7 |
| Structured care pair | `rev_careprovidedtype` | ❌ no — declared in Dev Summary §7 |
| Structured care pair | `rev_carehoursperweek` | ❌ no — declared in Dev Summary §7 |
| Three redacted care columns | `rev_*redacted` ×3 | ✅ **yes** — bound, gated, tested, live |

So 3 of 11 elements are delivered, 1 partially, and 7 absent — of which the Dev Summary declares
3. **The screen does not display a misleading total**: the label is *"Amount requested"*, not
*"Total funding requested"*, verified at `src/components/CasePanels.tsx` line 112. That is the
difference between a coverage gap and a wrong number, and it is a coverage gap.

**FR-035's redacted half is genuinely and completely delivered**, which is the part ADR-027's
amendment asked for: exactly the three `…redacted` columns are bound, none of their secured sources
is, the `rev_redactionreleased` gate is reused unchanged, and the three-state rendering (withheld /
released-empty / released) is asserted by name in `src/components/CasePanels.test.tsx`.

---

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| TC-PC-01 | Platform Contract | A-FLOW-01 closed: the Power Apps trigger / `Response` shape accepted by the designer | CLOSED | **OPEN** — flow absent from DEV, no designer save has occurred | P3 |
| TC-PC-02 | Platform Contract | A-FLOW-02 closed: minimum privilege to invoke | CLOSED | **OPEN** — no invocation attempted | P3 |
| TC-PC-03 | Platform Contract | A-FLOW-03 closed: `Secure Outputs` actually hides row data from run history | CLOSED | **OPEN** — no run has occurred | P3 |
| TC-PC-04 | Platform Contract | A-FLOW-04 closed: connection reference binds to a Power-Apps-triggered flow | CLOSED | **OPEN** — no import/activation | P3 |
| TC-VL-05 | Verification Level | Flow reaches V3 (accepted by the target) | V3 | **V2** — confirmed absent from DEV by live query with a positive control | P3 |
| TC-SEC-06 | Security | The new flow writes `rev_errorlog` and calls the Failure Alert on failure, per TAD §5.1 | Failure path present | **Absent** — no error branch, no `runAfter` on `Failed`, no Response on the failure path | **P2** |
| TC-SEC-07 | Security | Values interpolated into a privileged OData `$filter` and into hand-built JSON are escaped | Escaped or provably safe | **Unescaped** — `rev_name` concatenated raw | P3 |

---

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-01** | **P2** | The build manifest asserts packaged content that does not exist: `manifest.json` line 10 says the packaged working tree *"includes the trustee-portal-visual-refresh changes (rev_roundfinance table, **LandingPage/charts UI**, …)"*. No `LandingPage*`, chart, or `RoundStatistics*` file exists anywhere under `src/code-apps/trustee-review-portal/src`, and the built bundle in the artifact contains none. The Dev Summary is correct; the manifest — the provenance record that travels with the artifact and that pipeline-agent and acceptance-agent read — is not. Class: `no-assertion-on-shipped-content` | TC-ART-01 |
| **D-02** | **P2** | The new flow has no failure path, contrary to the approved TAD. TAD §5.1 line 639 specifies *"`rev_errorlog` row + `REV | Ops | Failure Alert` … **and** a non-`ok` `status` in the response"*, and the §5.1 flowchart (line 655) draws `R0 & R1 & R2 -.-> ERR`. The built flow has no `rev_errorlog` write, no Failure Alert call, and no `runAfter` branch on `Failed`/`TimedOut`/`Skipped` anywhere. Because every action runs `runAfter: Succeeded` only, a failure of `List_the_open_round` or `List_applications_in_round` terminates the flow with **no `Response` action reached at all** — the caller gets a bare failure, the screen cannot render TAD §3.3's "figures unavailable" diagnostic state from a status code, and nothing is recorded. Not declared in Dev Summary §7 | TC-SEC-06 |
| D-03 | P3 | FR-035's structured half is unwired and the declared gap is narrower than the actual gap: `rev_otherbreaktype`, `rev_additionalamountrequested` and `rev_exceptionalfundingrequested` are absent from the app and absent from Dev Summary §7's list of known limitations (which names only the other three) | §2 table |
| D-04 | P3 | TAD §3.2 line 303 lists *"preferred dates"* under "Deliverable now, with no schema change". **No preferred/holiday date column exists** anywhere in the solution — every date column on `rev_application` is a consent, decision, panel, payment, snapshot, DOB or last-contact date. Third instance of `requirement-names-data-the-solution-cannot-supply` (after `IMP-0293`, `IMP-0296`). Needs an SDD/schema decision, not a code fix | TC-035d |
| D-05 | P3 | An admin-writable value is concatenated unescaped into an OData `$filter` executed on the **service identity's** connection, and into a hand-built JSON document. `rev_roundfinance.rev_name` (Text 100, REV Admin writable) reaches `$filter` at flow JSON line 123 and the response body at line 172 with no escaping: an apostrophe breaks the filter, a double-quote produces invalid JSON the app's type guard will reject. Blast radius is narrow — admin-only input, and the filter targets a table the service identity already reads in full — but this is the one privileged read path the feature adds | TC-SEC-07 |
| D-06 | P4 | Two literal `A-nnn` placeholders left unresolved in the Dev Summary where the id is `A-FLOW-02`: §2 line 51 and §6 line 115. `scripts/verify-assumption-markers.py` passes because it resolves §10 rows' `Where` targets only, so nothing mechanical catches a placeholder in prose | TC-PC-02 |
| D-07 | P4 | Dev Summary §9 line 150's suite figures are stale: it reports 874 passed / 1 failed against a measured 875 passed / 0 failed / 1 skipped | §1 |
| D-08 | P3 | Three documents state three different WBS scopes for one build. Dev Summary line 8: `6.1`, `6.3`, **`6.5`**, `6.9`. `manifest.json` line 3: `6.1`, `6.3`, `6.9`, **`0.4`**. The dispatch handoff: `6.1`, `6.3`, `6.9` + `0.4` addendum. No `6.5` deliverable is evidenced in Dev Summary §11. The WBS id is the join key between commit, contract line and invoice — `pm-agent`/`commercial-agent`'s to reconcile, not test-agent's to fix (`C-COM-002`) | TC-ART-02 |
| D-09 | P3 | Cross-document identifier collision. `FR-056`–`FR-064`, `NFR-026`–`NFR-028` and `OQ-031`–`OQ-039` are independently allocated **twice**: by approved Amendments A-02/A-03 in `docs/plans/revitalise-grant-automation-plan.md`, and by the DRAFT `docs/plans/revitalise-form-field-corrections-plan.md`, whose line 11 claims it continues the numbering "so no identifier is reused". Same ids, different requirements — e.g. `FR-062` is wellbeing distributions in one and care-hours bands in the other. Every traceability claim in this report therefore names its source document. `plan-agent`'s to resolve. ✅ **RESOLVED 2026-08-26 by plan-agent — CLOSED.** The form-field-corrections SDD was retired to a superseded stub and its requirements merged into `revitalise-grant-automation-plan.md` as **Amendment A-04**, renumbered to `FR-070`–`FR-077`, `NFR-030`–`NFR-032`, `US-020`–`US-023` and `OQ-040`–`OQ-048`. The grant-automation plan is now the sole allocator of requirement identifiers for this solution; the ids used in this report are unchanged. `scripts/verify-requirement-id-uniqueness.py` exits 0 with 0 identifiers allocated more than once. Downstream citations were remapped in the form-field TAD, the grant-automation dev summary and test report, and `src/tests/solutions/IntakeContract.Tests.ps1`. | §2 |

**No P1 defect was raised.** Nothing that has been built is functionally wrong: the schema is
correct and live, the security controls are correct and live, and the code app compiles, lints and
passes its full suite.

---

## 5. Constraint & Compliance Verification

Scope filter per `agents/test-agent.md`: rows whose `Scope` column names `test-agent` — **27
technology + 6 domain = 33 rows, 32 HARD + 1 SOFT**. Gate scripts were run individually with the
exit code captured bare (`out=$(...); rc=$?`), never through a pipe.

> **Scope conflict, reported rather than resolved.** `constraints/README.md` line 77 makes test-agent
> *"final verifier — all HARD + SOFT"* of **every** active row (44 technology + 16 domain), which is
> broader than the per-row `Scope` cells. This report evaluates the 33 rows that name test-agent and
> additionally records the six rows the dispatch asked about that do not (C-TECH-050/055/061/074,
> C-DOM-020/021). The mismatch between the README matrix and the Scope cells is a constraint-file
> defect, not a judgement for this gate.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-TECH-001 | No hardcoded secrets | PASS | `secret-scan` step uses `gitleaks detect --source . --no-git --config .gitleaks.toml` (build config line 244) — `--no-git` present, so `IMP-0002`'s hole is closed; build manifest records PASS |
| C-TECH-004 | Inputs validated and sanitised | PASS (with residual) | The new flow **accepts no input parameters at all** (flow JSON lines 28–39), so it has no caller-steerable surface. Code-review residual: D-05's unescaped internal concatenation. No malformed-input security test exists in this project |
| C-TECH-006 | Authentication enforced on non-public routes | PASS (design evidence) | Trigger is `type: Request, kind: PowerApp` on a solution-aware flow — platform-brokered caller identity, **not** an anonymous HTTP endpoint with an embedded key. No unauthenticated-request test executed: the flow is not deployed |
| C-TECH-014 | Unit-test coverage meets the threshold | PASS | Threshold is 80% line (PowerShell) and 80% statements/lines (TS) per `knowledge/technology/coding-standards.md` lines 129–133. Build manifest records 81.81% Pester and 94.44% code app. **Both numbers recorded, per `IMP-0132`** — test-agent independently re-confirmed the pass counts (875 / 246) but not the coverage percentages |
| C-TECH-040 | Roles via group teams only in Test/Acc/Prd | PASS | Unchanged by this dispatch; no deployment beyond DEV. DEV's direct-assignment model is by design |
| C-TECH-042 | Provisioning idempotent; convergence declared | PASS | `verify-provisioning-step-convergence` green in build. Dev Summary §5 records a second live run: exit 0, 459 `EXISTS`, 0 `FAILED`. **Per this row's own amendment, that all-`EXISTS` run is cited as convergence evidence only, never as evidence the write path works** — the write path is evidenced instead by test-agent's live reads in §6 |
| C-TECH-045 | Connectors comply with DLP; no group mixing | PASS (structural) | TAD §4 lists the connector set: **Dataverse only** (`shared_commondataserviceforapps`), no new connector. The Power-Apps-trigger-beside-Dataverse policy question is declared as an owned manual pipeline prerequisite before the first push — `config/revitalise-grant-automation-pipeline.yml` lines 804–808, `owner: reviewer (tenant DLP administrator)`. **The tenant policy itself is not readable from this repository and has not been read** |
| C-TECH-046 | Out-of-box roles never modified | PASS | Only `REV *` roles changed. `git diff` touches `REV Trustee`, `REV Admin`, `REV Service Automation` and nothing else. The design explicitly refused the `App Opener` OOB-role route (TAD §6.1) |
| C-TECH-048 | Code App data access via CLI-generated data source only | PASS | No MSAL/token code added. The design chose `pa app add flow` over an HTTP trigger with an embedded SAS key precisely to satisfy this row (TAD §1.2). The verb has not yet been run — the flow is not live — so nothing is generated yet either |
| C-TECH-051 | No fabricated ids for platform-assigned components | PASS | `verify-solution-root-components.py` → 66 root components, every one has a definition on disk, nothing on disk undeclared, exit 0. `rev_roundfinance`'s `EntitySetName` and `PrimaryIdAttribute` were **read back live**, not authored — §6 |
| C-TECH-052 | Unvalidated Assumptions Register + `A-nnn` markers in source | PASS | `verify-assumption-markers.py` → PASS, 10 OPEN rows each carrying its marker, exit 0. `verify-assumption-register.py` → PASS, 43 rows / 17 registers, exit 0. A-FLOW-02's marker confirmed at `REV Trustee.xml` line 247. Residual: D-06's two prose placeholders, which this gate's design does not read |
| C-TECH-053 | Report only the verification level actually executed | **PASS, and it is why this run is FAIL** | §7.2. Every level in Dev Summary §11 was re-confirmed or corrected against live DEV. One claim is corrected: see §7.2's flow row |
| C-TECH-054 | Scripts run on the CI runner's OS | PASS (narrow) | No new script. `ensure-schema-helpers.psm1` / `ensure-schema.ps1` diffs add no OS-specific API (no `Cert:`, `Get-CimInstance`, drive letter or backslash path). **Not executed on the CI runner: CI has never run on this project (`IMP-0165`)**, so this is source review, not V6 |
| C-TECH-056 | Diagnostic components removed and recorded | PASS | Dev Summary §11 declares none created. Independently checked live: DEV holds no `rev_*` probe table and `rev_roundfinance` holds **0 rows**, so no diagnostic row was left behind |
| C-TECH-057 | Every gate proven able to fail | PASS | `verify-build-config.py` → all seven checks OK, exit 0, exemptions named not silent |
| C-TECH-058 | An OPEN §10 assumption blocks deployment where it could be closed | **TRIGGERED — not violated** | Four rows OPEN (A-FLOW-01…04). No deployment has occurred, so the rule is not breached. It **does** gate the handoff to pipeline-agent: see §8 |
| C-TECH-059 | Learning substrate never destroyed | PASS | `generate-known-failure-modes.py --check` → current, 320 entries, exit 0. Artifact directory is per-build and unique |
| C-TECH-060 | No shipped text value exceeds its governing limit | PASS | `verify-field-length-limits.py` → 175 flow descriptions within 256 chars, 86 declared limits read from `Entities/`, exit 0. The new flow's long reasoning correctly lives in `.notes.md`, not in a `description` |
| C-TECH-064 | Environment state source cannot express, verified LIVE | PASS | §6 — 14 live DEV queries. Org `isauditenabled=True`, retention 2192 days; `rev_roundfinance.IsAuditEnabled=True`; 51 field permissions enumerated; profile membership enumerated on **both** axes |
| C-TECH-065 | A credential that authenticates is not an authorised identity | PASS | `WhoAmI` against DEV returned a real `UserId` (`3a1a3937-…`), so the provisioning identity is recognised by **this** org, not merely accepted by the directory. The *Power Apps code apps* per-environment toggle is declared as an owned prerequisite (`prerequisite_id: code-apps-feature`) |
| C-TECH-066 | TAD schema/access tables are a checked specification | PASS | `verify-tad-coverage.py` → 148 column specs across 11 table blocks all exist or carry an owned dated deferral (9 deferred); 18 trustee-visible columns sit on tables `REV Trustee` can read; exit 0 |
| **C-TECH-067** | **SOFT** — tests derive counts from source | **WARNING** | 10 fragile-literal warnings from `source-derived-test-counts` remain, reviewer-pre-accepted per the build dispatch. `IMP-0315` records that this dispatch generalised four locations; the residual ten are carried, not closed |
| C-TECH-068 | Negative access result requires live-verified controls | PASS (not exercised) | No access test was run in this dispatch. The precondition script is declared in the pipeline. §6 confirms the two membership axes are enumerable and that a positive control now exists (see D-note in §6) |
| C-TECH-069 | Readers survive a second instance; identity is (table, column) | PASS | `verify-source-reader-plurality.py` → 36 readers plurality-safe, exit 0. `IMP-0321` records the substring-matching false positive this feature's `…redacted` naming exposed in `schema.test.ts`, corrected to whole-identifier matching |
| C-TECH-070 | `IsSecured` protects a stored value, never a projection | PASS | `verify-field-security-coverage.py` → 67 secured columns all released by a profile, exit 0, with the two standing platform warnings (5 lookup name companions, 1 Money `_base`). **This feature correctly used `Decimal`, not `Money`, for all seven `rev_roundfinance` measures** — confirmed live: all seven report `AttributeType=Decimal`. Note the platform added `rev_isopenname` (Virtual) beside `rev_isopen`; harmless here, the table holds no personal data |
| C-TECH-071 | A declared property is only delivered if the builder emits it | PASS | `declared-property-reaches-creation-path` green in build. Independently confirmed live: all 13 authored attributes carry `IsAuditEnabled=True` and the three redacted columns carry `IsSecured=False, IsAuditEnabled=True` — the declared properties did reach the platform |
| C-TECH-073 | Metadata writes are `PUT` with the whole object, never `PATCH` | PASS | `metadata-write-verbs` green in build; no metadata write added by this dispatch |
| C-DOM-004 | Personal data must not be written to application logs | **PASS, with a stated limit** | `domain-invariants` exit 0. The new flow sets `Secure Outputs` on its one personal-data read — **verified by reading the authored JSON, lines 134–140** — and correctly omits it from the `Respond` actions so the non-personal aggregate stays auditable. **Two limits, both material:** (1) no gate anywhere can observe this — `secureData` appears nowhere in `scripts/`, confirmed independently, so `verify-flow-definition-language.py` names four checks and none of them is Secure Outputs; (2) whether the property actually hides run-history data for a hand-authored flow is **A-FLOW-03, still OPEN**. Evidence level: **V1, manual inspection of source.** Pre-existing exposure on two other flows is `EX-004`, reviewer-risk-accepted, expiring 2026-10-16 |
| C-DOM-010 | CUD on sensitive entities audit-logged | PASS | Live: org `isauditenabled=True`, `rev_roundfinance.IsAuditEnabled=True`, all 13 attributes `IsAuditEnabled=True`, all three redacted columns `IsAuditEnabled=True`. **Cited with `C-TECH-064`'s live half, as `C-DOM-032` requires** — not from source flags alone |
| C-DOM-011 | Audit records include timestamp, actor, action, entity id, before/after | PASS (platform-provided) | Dataverse's own audit store supplies the schema; retention confirmed live at 2192 days ≈ 6 years. No custom audit writer added by this dispatch |
| C-DOM-030 | No special-category column influences an automated outcome | PASS | `domain-invariants` → 20 special-category columns verified, register ↔ FR-016 gate in sync (20 names), exit 0. The new flow feeds no eligibility or scoring outcome — it emits counts |
| C-DOM-031 | Register columns carry `IsSecured=1` | PASS | 16 secured, 4 documented exceptions, all four printed by the gate. The three new `…redacted` columns are correctly **not** register entries — they are redactions of registered columns, and their sources remain secured (confirmed live, §6) |
| C-DOM-032 | Register columns carry `IsAuditEnabled=1` | PASS | 20 / 20 enabled. Two non-register attributes with auditing off are reported by the gate, not failed: `rev_applicant.rev_fullname`, `rev_application.rev_costs` |

**Rows the dispatch asked about that do not name test-agent in Scope**, recorded for completeness
under `constraints/README.md` line 77: C-TECH-050 PASS (schema created by `ensure-schema.ps1`, not
by import — confirmed live); C-TECH-055 PASS (44 warnings, 0 untriaged per the manifest;
`rev_roundfinance`'s two `forms-and-views-reachable` warnings now carry a rationale at Dev Summary
line 199, and test-agent re-ran that script — same 10 warnings, exit 0); C-TECH-061 PASS
(`verify-improvement-log.py --check` exit 0, 0 blockers unread); C-TECH-074 PASS per the build's
`code-app-audit`; C-DOM-020 PASS (five narrow additive grants, service identity read-only, confirmed
live); C-DOM-021 PASS (the elevation lives in a connection reference no caller can substitute, and
the flow takes no parameters).

**No constraint row in this project mentions Secure Outputs.** It is enforced only as `C-DOM-004`
evidence, and by no script. That is the substance of `IMP-0320` and `IMP-0322`.

---

## 6. Provisioning Verification

Every row below was re-queried live against DEV (`https://orge2b20d13.crm17.dynamics.com`) by
test-agent in this session. Cert-based app-only auth, `WhoAmI` = `3a1a3937-e897-f111-b8dc-7ced8d43e87d`.

| Item (TAD §12 / §6.1) | Expected | Verified Via | Result |
|---|---|---|---|
| `rev_roundfinance` table | Exists, OrganizationOwned | `EntityDefinitions(LogicalName='rev_roundfinance')` | **PASS** — `OwnershipType=OrganizationOwned` |
| Its entity set name | Platform-assigned, **not** hand-authored | same | **PASS** — `EntitySetName=rev_roundfinances`, `PrimaryIdAttribute=rev_roundfinanceid`. Closes TAD §12.2's "do not hand-author it" row |
| Its 13 attributes | 13 authored | `…/Attributes?$select=LogicalName,AttributeType,IsAuditEnabled` | **PASS** — 15 `rev_*` returned = 13 authored + `rev_roundfinanceid` (PK) + `rev_isopenname` (platform Virtual companion). All 13 authored present, all `IsAuditEnabled=True` |
| All seven measures are `Decimal`, not `Money` | `Decimal` | same | **PASS** — C-TECH-070 clause 2 honoured |
| Alternate key on `rev_name` | Present **and `Active`** | `?$expand=Keys($select=EntityKeyIndexStatus)` | **PASS** — `rev_roundfinance_name`, `EntityKeyIndexStatus=Active`. `Pending` would not enforce uniqueness (`IMP-0044`); it is Active |
| Table auditing | `IsAuditEnabled=True` | `?$select=IsAuditEnabled` | **PASS** — `True`. A-R30 closed |
| Org audit switches | On, 6-year retention | `organizations?$select=isauditenabled,auditretentionperiodv2` | **PASS** — `True`, 2192 days |
| 3 redacted columns on `rev_application` | Present, `IsSecured=0`, `IsAuditEnabled=1` | `EntityDefinitions(LogicalName='rev_application')/Attributes` | **PASS** — all three, `secured=False`, `audit=True`, matching TAD §3.2.1 exactly |
| The 3 redacted columns must **not** be in `REV_TrusteeRestricted` | Absent | `fieldpermissions?$filter=_fieldsecurityprofileid_value eq <id>` | **PASS** — none present. This is TAD §12.1's third mandatory verification, and it is the mirror-image failure §6.2 names |
| Their secured sources still secured | Present in the profile | same | **PASS** — `rev_caresupportdescription`, `rev_careprovidedexample`, `rev_othercareprovidedtype`, plus `rev_gender`, all `canread=4` |
| Profile membership — **both axes** | No trustee; a service principal present | `systemuserprofiles_association` **and** `teamprofiles_association` | **PASS** — 0 direct users, 1 team: `REV-PP-GrantApplications-Service-DEV`. No trustee on either axis. **This also closes `IMP-0221`'s concern**: a positive control now exists, so the privileged gender read has an identity that can actually perform it |
| `REV Trustee` privileges | + `prvReadrev_roundfinance`, + `prvReadWorkflow` | `roles(<id>)/roleprivileges_association` | **PASS** — both present live |
| `REV Service Automation` | + `prvReadrev_roundfinance`, read-only | same | **PASS** — present; no create/write/delete added |
| `REV Admin` | + Create/Read/Write on `rev_roundfinance` | same | **PASS** — all three present, no Delete, no Assign, no Share |

**A false positive I checked and discarded rather than reporting.** DEV shows `prvReadWorkflow` on
`REV Admin` and `REV Service Automation` as well as on `REV Trustee`, which the TAD grants only to
the trustee. `git show HEAD:` on both role files confirms both already carried it before this
dispatch; only `REV Trustee`'s is new. TAD §6.1 is accurate.

**Two live facts that gate the feature and are correctly declared, not defects:**

- **`rev_roundfinance` holds 0 rows.** TAD §12 declares the first row a manual `post_deploy` step
  and says the landing screen shows nothing without it. Nothing to fix; nothing to test end-to-end.
- **`REV | Scoring | Daily Summary` is currently `statecode=0` (Draft/off)** in DEV while Intake,
  Failure Alert and Calculate & Flag are `statecode=1`. Out of this WBS's scope; noted because it is
  one of `EX-004`'s two flows, and while it is off that exception's live exposure is smaller than the
  record implies.

---

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Per the template's own instruction (`IMP-0219`), each row's **closing precondition is recorded
separately from its status** and answered fresh at the start of this cycle rather than inherited from
the Dev Summary's narrative.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-FLOW-01 | Hand-authored `kind: "PowerApp"` trigger and `Response` shapes are well-formed and the designer will save them | OPEN | Flow imported into an environment **and** a human opens it in the Power Automate designer and saves it | **Environment yes, flow no.** Live query of `workflows?$filter=category eq 5` returns 7 flows; `REV | Portal | Round Statistics` is **not** among them | **Confirmed still OPEN.** The absence is conclusive, not a visibility artefact: the same query returns the other four `REV` flows, which is the positive control `skills/how-to-verify-a-platform-contract.md` §11 requires | **OPEN** |
| A-FLOW-02 | `prvReadWorkflow` at Global is sufficient and not excessive to invoke the flow | OPEN | Grant it and nothing else, then invoke as a real trustee | Grant exists live; flow does not, so no invocation is possible | **Confirmed still OPEN.** The grant half is live-verified (§6); the sufficiency half is untestable until the flow exists | **OPEN** |
| A-FLOW-03 | `Secure Outputs` hides row data from run history for a hand-authored flow | OPEN | One real run, then read its run history as an owner | No run has occurred — flow not deployed | **Confirmed still OPEN.** The property **is** present in source (flow JSON lines 134–140) and correctly scoped to the one row-reading action; that its *effect* matches the designer checkbox is unproven | **OPEN** |
| A-FLOW-04 | The `rev_SharedDataverse` connection reference binds to a Power-Apps-triggered flow as it does to the other four | OPEN | Same designer-save step as A-FLOW-01 | No import/activation | **Confirmed still OPEN** | **OPEN** |

**Orphan check (`C-TECH-052`).** No orphans. `verify-assumption-markers.py` resolves every OPEN row's
`Where` target to a real file containing the row's own id — 10 OPEN rows across 4 documents, exit 0 —
and A-FLOW-02's marker was additionally confirmed by hand at `REV Trustee.xml` line 247. Note that
this row's *old* wording made test-agent's manual grep the enforcement mechanism; that clause was
replaced by the script on 2026-08-25, so the script is cited here rather than the grep.

**Two rows the Dev Summary says the session closed — both confirmed closed by test-agent, live:**
`rev_roundfinance`'s `EntitySetName`/`PrimaryIdAttribute` (read back: `rev_roundfinances` /
`rev_roundfinanceid`) and A-FIN-02's `decimal` attribute branch (all seven measures report
`AttributeType=Decimal` live). Both closures are genuine.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| `rev_roundfinance` + 13 attributes + alternate key | **V4** | **V4 — confirmed** | Live `EntityDefinitions` read by test-agent: 13 authored attributes, `EntityKeyIndexStatus=Active`, `EntitySetName=rev_roundfinances` | **PASS** |
| 3 redacted columns on `rev_application` | **V4** | **V4 — confirmed** | Live read: all three present, `IsSecured=False`, `IsAuditEnabled=True` | **PASS** |
| Role privilege grants (3 roles) | **V4** | **V4 — confirmed** | Live `roleprivileges_association` on all three roles | **PASS** |
| Table auditing on `rev_roundfinance` | **V4** | **V4 — confirmed** | Live `IsAuditEnabled=True`, plus org switch `True` and retention 2192 | **PASS** |
| `REV \| Portal \| Round Statistics` flow | **V2** | **V2 — confirmed, and confirmed it is not V3** | `pac solution check` 0/0/0/0/0 (artifact log, correlation `c7bda0ae-…`); flow present in the packed zip at 8954 bytes; **absent from DEV** by live query with a positive control | **PASS on the claim** |
| `pa app list-flows` / `pa app add flow` mechanism | **V3 (connectivity), not V4** | **Accepted as claimed; not re-executed** | test-agent did not re-run the CLI verb. The claim is a connectivity result, correctly scoped by the Dev Summary itself | **PASS on the claim** |
| ADR-026 brand theme | **V2** | **V2 — confirmed** | `npm run typecheck` / `lint` / `test` clean, 246/246, run by test-agent. No live Code App push | **PASS** |
| FR-035 redacted-column UI (`CareSupportPanel`) | **V2** | **V2 — confirmed** | 246/246 including the three-state care-panel assertions; `verify-code-app-column-bindings.py` exit 0 — 56 authored files reference none of 63 forbidden columns | **PASS** |
| **The artifact's own manifest** | *(claims LandingPage/charts UI packaged)* | **Claim is false** | No `LandingPage*` / chart / `RoundStatistics*` file exists in the tree or the built bundle | **FAIL — D-01** |

- **Idempotency (V3 re-run):** **PASS as convergence evidence only.** Dev Summary §5 records a second
  live `ensure-schema.ps1 -Env dev`: exit 0, 459 `EXISTS`, 0 `FAILED`. Per `C-TECH-042`'s own
  amendment an all-`EXISTS` run proves the read and the comparison and nothing about the write path —
  so the write path is evidenced here by §6's live reads instead, which is the stronger evidence and
  the reason this row is not carried on the script's exit code.
- **V4 designer/editor open + save:** **NOT PERFORMED.** No named owner has opened the new flow in the
  Power Automate designer, because the flow has never been imported into any environment. This is the
  single step that closes A-FLOW-01, A-FLOW-03 and A-FLOW-04 together.
- **Cross-OS (`C-TECH-054`):** **N-A / source review only.** No new script; the two modified
  provisioning files add no OS-specific API. Not executed on the CI runner — CI has never run on this
  project (`IMP-0165`).
- **Warnings triaged (`C-TECH-055`) and diagnostic components removed (`C-TECH-056`):** **PASS.** 44
  warnings, 0 untriaged; `rev_roundfinance`'s two `forms-and-views-reachable` warnings now carry a
  recorded rationale, and test-agent re-ran that script independently — same 10 warnings, 22 checks,
  11 entities, exit 0. No diagnostic component exists in DEV (`rev_roundfinance` holds 0 rows).

**The verification level this feature actually reached, stated once and plainly:**

> **The schema half of this feature is V4 in DEV, independently confirmed by test-agent's own live
> queries. The flow is V2 — packaged and Solution-Checker-clean, never imported anywhere. The Code
> App changes are V2 — compiled, linted and unit-tested, never pushed. Nothing in this feature has
> reached V3, V4 or V5 in the Code App or the flow, and no end-to-end execution of any FR-057–FR-063
> behaviour has occurred or can occur until the flow is live and `rev_roundfinance` holds a row.**

---

## 8. Recommendations

**1. Fix D-01 and D-02 before anything is imported.** Both are cheap and both are in
development-agent's hands. D-02 is the more important of the two: the flow is the one new privileged
component, and adding its `rev_errorlog` + Failure Alert branch is far cheaper now, while nothing
depends on it, than after `pa app add flow` has generated a typed service against its current shape.

**2. Then treat the DEV import as the assumption sweep, not as a deployment.** All four A-FLOW rows
close at the same moment — one import plus one human designer save. `skills/how-to-verify-a-platform-contract.md`
§6 is explicit that the register is closed in one pass when the environment appears, not one failure
at a time, and TAD §12.2 already sequences this row **first, before any other `wbs:6.9` work**.

**3. `C-TECH-058` gates the handoff to pipeline-agent and the reviewer must choose the route.** Four
OPEN rows block deployment into any environment where they could be closed. For DEV this is circular:
the import *is* the means of closing them. The rule's own escape is an explicit
`OVERRIDE A-FLOW-01`, `OVERRIDE A-FLOW-02`, `OVERRIDE A-FLOW-03`, `OVERRIDE A-FLOW-04` recorded with
reasons in the Deployment Summary. For TST/ACC and PRD the rows are not overridable on the same
reasoning — by then DEV will have settled them.

**4. Do not let the O(n) landing screen reach a higher environment unmeasured.** NFR-022 has no
target because OQ-020 is open, so no performance test can fail. That is a gap in the requirement, not
a clean result, and A-R36 already names the measurement method.

**5. Three items belong to other agents, not to a retest.** D-08's WBS scope disagreement
(`pm-agent`/`commercial-agent`), D-09's duplicated requirement identifiers (`plan-agent`), and D-04's
"preferred dates" with no column (`plan-agent`/`architect-agent`). None of them is fixable by
development-agent and none should hold a retest.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0324 | `no-assertion-on-shipped-content` | rework | A build manifest's free-text provenance note is an unchecked claim about shipped content — diff its named artefacts against the tree before trusting it, because nothing else does |
| IMP-0325 | `declared-policy-not-mechanically-enforced` | rework | A TAD-specified failure path (error-log row + alert) is enforced by no gate: grep every new flow for a `runAfter` on `Failed` before calling its error handling built |
| IMP-0326 | `requirement-names-data-the-solution-cannot-supply` | friction | Third instance — before writing "deliverable now, with no schema change" in a TAD, resolve every named field to a column that exists on disk |
| IMP-0327 | `identifier-namespace-collision-across-documents` | rework | Two SDDs in `docs/plans/` independently allocate FR-056–064 / NFR-026–028 / OQ-031–039 to different requirements; no gate compares identifier namespaces across plan documents |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` → 324 entries, 486 lines, `--check` exit 0.

### One consequence of these four entries, reported rather than left to be discovered

**Appending them crossed the improvement log's batch trigger, so `verify-improvement-log.py --check`
now exits 1 and the next build of this solution will fail at its `improvement-log-check` step.**
The unread queue went from 9 to 13 against a trigger of 10:

```
TRIGGER: 13 NEW entries awaiting closure — 13 unread, 0 awaiting-approval (batch trigger is 10)
  IMP-0311, IMP-0312, IMP-0313, IMP-0314, IMP-0315, IMP-0316, IMP-0317,
  IMP-0319, IMP-0321, IMP-0324, IMP-0325, IMP-0326, IMP-0327
verify-improvement-log: FAILED — 1 problem(s) across 324 entry(ies)
```

This is the gate working, not the gate breaking: there genuinely are 13 unprocessed findings and 4
of them are this report's. It is recorded here because `C-TECH-061` is not in test-agent's scope and
nothing else in this cycle would surface it. **An improvement review is now due before the next
build**, and per `IMP-0183` the review must process the *unread* subset only — two of the 13
(`IMP-0316`, `IMP-0319`) are already cited by improvement review 2 and need a `reviewed_in` stamp
rather than a second review.

The queue was **not** cleared by softening any of these four findings. Marking a finding deferred to
get a gate green is the shape `IMP-0264` forbids — the legitimate responses are all additive.
