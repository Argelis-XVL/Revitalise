# Test Report — Revitalise Grant Automation (TAD rev 13 in DEV: ADR-053, ADR-054, D-01 regression, wbs:4.2/4.3)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260927-2/
**Date:** 2026-09-28
**Status:** PARTIAL — APPROVED 2026-09-28 (Xander Lykopoulos, relayed by lead-agent)
**WBS:** `4.2` (Appendix C field map, schema), `4.3` (intake flow). Neither task's test-results deliverable (`4.5`) is claimed by this report.
**Scope:** TAD rev 13 (ADR-053, ADR-054), the D-01 fix from [Test Report 20260927-1](revitalise-grant-automation-test-report-20260927-1.md) as a regression check, and TAD §12.4 step 7 (the final DEV import). Tier: strategic, because the feature carries a P1 from its previous cycle.
**Harness mode:** Auto Mode. No provisioning certificate. Every live read went through `pac env fetch` on the active `svc_grantapplications` DEV profile (FetchXML, read-only). Nothing was written to any environment.

---

## Summary

**PARTIAL: what build-agent imported into DEV is exactly what was built and tested, and the D-01 fix holds live. Nothing has yet run end to end.** The live intake definition matches source with zero differences. The live caller check refuses every caller except the right client id, in all 28 cases I evaluated. The ADR-053 widths and the ADR-054 refresh logic in DEV are what TAD rev 13 specifies. No P1 or P2 is open.

**Waiting on you:** the V4 designer open-and-save, and step 8's metadata GET, which closes A-INT-10 and the open governance finding. While you are in the designer, please also read the trigger's "Who can trigger the flow?" setting. That is the one new defect (D-05, P3): nothing ever sets or checks it in DEV.

---

## What was verified

1. **The imported flow is the built flow** ([flow JSON](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L53)). DEV's `workflow.clientdata` parses equal to source, definition and connection references alike, with 0 differences. The packed file is byte-identical to source in both the unmanaged and the managed zip (sha256 `ed2b5158…`). The flow was modified at 21:03 UTC, which matches the import.
2. **D-01 stays fixed, in DEV** ([caller check L365](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L365)). The 401 and the Cancelled stop sit in the branch the condition selects for rejection, and the else branch is empty. I evaluated the live condition with my own evaluator, independent of development-agent's: 4 allowed-id states (set, empty, blank, null) × 7 header states (right, wrong, absent, empty, blank, right with a trailing space, upper-cased). The right header with the id set is admitted, and the other 27 are refused. `Normalise_payload` runs only after that check succeeds. DEV's `rev_IntakeAllowedClientId` has a current value, set 2026-09-25, so the website is not refused by the fail-closed branch.
3. **No applicant answer is cut, and short columns refuse rather than truncate (ADR-053)** ([length notes L517](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L517)). I mapped every text column the live flow writes to its Entity.xml type and width. All 24 long-text columns are written whole at 1,048,576, with no guard. All 18 writes into the 10 guarded short columns have a guard no wider than the column. The one `take()` left caps the staff review note at 1,990 characters plus a marker, inside its 2,000 column ([L2680](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2680)).
4. **A returning applicant keeps what they didn't re-answer, as rev 13 narrows it (ADR-054)** ([Refresh L2744](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2744)). The 5 straight-through columns use `coalesce`. The 10 derived columns are gated on their raw source key: title, applicant type, gender, ethnic group, age range (with date of birth), contact method, and the four postcode-derived columns on postcode. The lookup's `$select` ([L2706](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2706)) names all 15 columns the refresh reads back, so none comes back empty and silently clears a value.
5. **The Application form in DEV is the packed form, and it is published.** It has 115 controls, identical to the packed `customizations.xml` in field, control class and `auto`. All 11 retyped columns carry the multi-line control with `auto="true"`. `publishedon` is 21:03 UTC, so the publish-before-delete lag recorded today is not in play.
6. **Security, settings and schema are intact after the import.** The five secured recreated columns still have one `REV_TrusteeRestricted` row and one System Administrator row each (10 rows, create/read/update Allowed), the same as the step-5 result. All 18 settings rows the flow reads equal `dev-scoring-settings.json`, value for value. All 24 long-text columns exist: one aggregate query names each one and would error on an unknown name, and a deliberately malformed query did error. Organisation auditing is on. The solution is `1.0.0.0`, unmanaged, matching the artifact.
7. **The import deactivated no flow.** Six flows are Activated and four are Draft, the same split as the recorded 2026-09-25 state ([pipeline.log](../../logs/pipeline.log#L222)).

---

## What this lets me claim, and what it does not

**Can claim: V3 for the flow, the form, the field permissions and the settings.** DEV accepted exactly what was built, and the shipped logic is right when evaluated as it stands in DEV.

**Cannot claim: anything executed.** No application has been created in DEV since 2026-09-25 09:32. `flowrun` holds no run of the intake flow, while it does hold 1 to 51 runs for each of seven other flows. So nothing, not even a refused call, has reached the definition since the import. Running it needs the website's client-credentials token, which I don't hold, so I did not construct a call. I also cannot read column metadata (MaxLength, IsSecured, RequiredLevel), which needs your certificate.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — [IntakeContract.Tests.ps1](../../src/tests/solutions/IntakeContract.Tests.ps1#L1156), re-run by test-agent | 156 | 156 | 0 | 0 |
| Regression — build's full Pester run (cited, not re-run: [Dev Summary §11](../development/revitalise-grant-automation-dev-summary.md#L11597)) | 1236 | 1235 | 0 | 1 |
| Integration — live definition vs packed vs source | 3 | 3 | 0 | 0 |
| Integration — ADR-053 text writes vs Entity.xml width | 42 | 41 | 0 | 1 (below) |
| Integration — ADR-054 refresh columns and lookup coverage | 15 | 15 | 0 | 0 |
| Security — caller check, live condition, 4 × 7 cases | 28 | 28 | 0 | 0 |
| Security — trigger-level "Who can trigger" in DEV | 1 | 0 | 0 | 1 — out of reach (D-05) |
| End-to-End — authenticated POST in DEV (V5) | 0 | 0 | 0 | all — needs the website's token |
| Accessibility | — | — | — | N/A — no custom screen; 11 platform controls change type, seen at V4 |
| Performance | — | — | — | N/A — no NFR threshold touched |
| Provisioning — live DEV reads (flows, form, field permissions, settings, env var, columns, solution, org audit) | 8 | 8 | 0 | 0 |
| Compliance — source gates re-run bare | 10 | 10 | 0 | 0 |

The skipped ADR-053 row is `rev_sourcesubmissionid` (100 characters, no guard). The website generates it, not the applicant, so it is outside §C.10's scope. I note it and don't raise it: an over-long entry id would fail the write with a 500 and an alert.

## 2. Requirement Coverage

| FR / ADR | Requirement | Test Case(s) | Result |
|---|---|---|---|
| NFR-008 / C-TECH-006 | Only the charity website may call the endpoint | 28 live-condition cases | **PASS** for the in-flow gate (V3); the platform-level setting is not verified in DEV (D-05) |
| ADR-053 | Free text stored whole; structured text refused into a note | 42 write cells vs Entity.xml | **PASS** (V3 definition); A-INT-10 open on the 13 widened columns |
| ADR-054 | Refresh preserves only on genuine silence | 15 columns, gate key per column, `$select` coverage | **PASS** (V3 definition); O-6 below |
| FR-084 | Blank → empty, no default | Unit suite (D-02 cases) | **PASS** (V1); unchanged this cycle |
| FR-007 | Record created automatically on submission | — | **Not run** — V5 needs an authenticated POST |
| TAD §12.4 step 7 | Target-state solution in DEV | Definition, form, permissions, settings | **PASS** (V3) |

## 3. Failed Tests

None.

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-05** | P3 | **Nothing sets or reads back the intake trigger's "Who can trigger the flow?" setting in DEV.** The manual step and the [verify-intake-endpoint-auth.ps1](../../provisioning/entra/verify-intake-endpoint-auth.ps1#L1) smoke test exist for TST/ACC and PRD only. No DEV endpoint variable is declared, and the pipeline note still says it is unverified because ["no environment exists yet"](../../config/revitalise-grant-automation-pipeline.yml#L1998). DEV has since taken many imports, and it is the environment the website developer was given. The live definition carries no auth property, and no flow in DEV does, so I cannot tell whether an import resets the setting. Graded P3, not higher: the second gate is verified live and refuses any caller without the right client id, and DEV holds test data only. Fix: read the setting back in the designer now. Then development-agent adds the step and the smoke test to [environments.dev](../../config/revitalise-grant-automation-pipeline.yml#L595) and registers "import preserves the setting" as an assumption row | Security — trigger-level |

**Observations — not defects, for your judgement:**

- **O-6: an over-long re-answer keeps the old value on four applicant columns.** For phone, both address lines and town, the rev 13 guard turns an answered but over-long value into empty. The refresh's `coalesce` then keeps the stored value ([L2758](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2758)), while the note says the new answer "was not stored". ADR-054 assumes that for these columns "the raw answer and the write value are the same thing", but the guard makes that untrue. It is the same answered-versus-silent mix-up rev 13 fixed for the derived columns, at far lower stakes. Postcode is safe, because an over-long postcode is refused with a 400 first.
- **O-7: one TAD §3 row still says the helper's organisation and relationship are unsecured.** Source, DEV and the rest of the TAD follow the 2026-09-17 reclassification that secured them ([FieldSecurityProfiles.xml L556](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L556)). Only the TAD §3 classification row is stale.
- **O-4 is unchanged, and its exception expires on 2026-09-30.** The failure alert still passes the platform's own error text unsecured. It predates this work.
- **Until step 8 closes A-INT-10, long answers are a live risk in DEV.** If an import does not raise an existing long-text column's limit, those 13 columns are still 2,000 or 4,000 characters in DEV. The flow no longer cuts answers, so a longer answer would fail the write with a 500. Consider holding long test entries from the website until step 8 has run.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-004 | No personal data in logs | PASS | Length notes name the field and limit, never the value ([L517](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L517)); O-4 noted |
| C-DOM-010 | Audit on sensitive CRUD | PASS | Organisation `isauditenabled` Yes, live; column flags in source. Live table and column flags need a metadata read (step 8) |
| C-DOM-011 | Audit record fields | PASS | Platform audit, unchanged |
| C-DOM-030 | No special-category column in scoring | PASS | `verify-domain-invariants.py` rc 0 |
| C-DOM-031 | Special-category columns secured unless excepted | PASS | `domain-invariants` rc 0; field permissions live on all five recreated secured columns |
| C-DOM-032 | Special-category columns audited | PASS | `domain-invariants` rc 0 (source) |
| C-TECH-001 | No secrets in source | PASS | Build secret scan; the allowed client id is a public identifier and is not in the repo |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Input validated before persistence | PASS | 10 guards within column width; 24 long-text columns whole; O-6 noted |
| [C-TECH-006](../../constraints/technology/technology-constraints.md#L39) | Authentication on non-public routes | PASS — in-flow gate | 28/28 live-condition cases. Platform-level setting not verified in DEV (D-05); every non-matching caller reaching the definition gets 401 |
| C-TECH-014 | Coverage threshold | PASS | Build unit-tests step green, coverage at or above 80% ([build.log](../../logs/build.log)) |
| C-TECH-040 | Roles via group teams (Test/Acc/Prd) | PASS | No role touched |
| C-TECH-042 | Provisioning idempotent | PASS | Second `ensure-schema.ps1 -Env dev` run: EXISTS, 0 FAILED (reviewer) |
| C-TECH-045 | DLP / connectors | PASS | No new connector |
| C-TECH-046 | OOB roles untouched | PASS | — |
| C-TECH-048 | Code App data access | PASS | No Code App change |
| C-TECH-051 | No fabricated platform ids | PASS | Field-permission ids are platform-assigned (new ids after recreation) |
| C-TECH-052 | Every guess registered | PASS | `verify-assumption-markers.py` and `verify-assumption-register.py` rc 0; D-05 proposes one missing row |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Report only the level executed | PASS | Dev Summary claims V1 plus V3 reads; confirmed V3 above the claim; V4 deferred-to-pipeline |
| C-TECH-054 | CI scripts cross-OS | PASS | No new CI script |
| C-TECH-056 | Diagnostic components removed | PASS | None created; the transitional package was superseded by step 7 |
| C-TECH-057 | Gates proven able to fail | PASS | No new gate; five mutants fail 8 tests (Dev Summary) |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumption blocks deploy where closeable | deferred-to-pipeline — evidence available after step 8 (A-INT-08, A-INT-10) and the first authenticated POST (A-INT-01 to 05, 09) | **Blocks promotion to TST/ACC until they close or you record `OVERRIDE`** |
| C-TECH-059 | Learning substrate kept | PASS | Own artifact directory; log appended |
| C-TECH-060 | Shipped text within limits | PASS | Review note 1,990 plus marker ≤ 2,000; build `field-length-limits` |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Environment state verified live after deploy | deferred-to-pipeline — the import was out-of-band, so DEV's `verification:` block has not run | Read here: org audit, 10 field permissions, 18 settings. Trigger-auth setting has no DEV step (D-05) |
| C-TECH-065 | Identity probe before trust | PASS | `pac org who`: svc_grantapplications on REV-GrantApplications-DEV |
| C-TECH-066 | TAD tables are a checked spec | PASS | `verify-tad-coverage.py` rc 0; O-7 is a row the gate does not compare |
| C-TECH-068 | Negative access evidence only on live controls | PASS | No negative access claim |
| C-TECH-069 | Readers survive a second instance | PASS | Build step |
| C-TECH-070 | Secured only where securable | PASS | Secured columns are text |
| C-TECH-071 | Declared property reaches creation | PASS | Field permissions on all five recreated secured columns imply `IsSecured` arrived; step 8 reads it directly |
| C-TECH-073 | Metadata writes are PUT | PASS | None authored; A-INT-10's remedy names PUT |
| C-TECH-078 | Geometry measured in a browser | PASS | No geometry claim made here |
| C-TECH-079 | Work items move on evidence | PASS | None carried |
| C-TECH-067 (SOFT) | Counts derived from source | WARNING | Pre-existing count literals |

Compliance: CR-01 holds for the five recreated secured columns at V3. Trustee-restricted access is unchanged, with one System Administrator and one `REV_TrusteeRestricted` row each.

## 6. Provisioning Verification

| Item (TAD §12.4) | Expected | Verified Via | Result |
|---|---|---|---|
| Step 7 import | Target-state solution live | Definition equality; `solution` 1.0.0.0 | PASS |
| 11 recreated columns + 13 widened | Exist | Aggregate FetchXML over all 24 | PASS for existence; width and `IsSecured` are step 8 |
| Five secured columns' field permissions | 10 rows, Allowed ×3 | `fieldpermission` ⋈ `fieldsecurityprofile` | PASS (unchanged since step 5) |
| Application main form | 11 multi-line controls, `auto="true"`, published | `systemform` read vs packed | PASS |
| Flow states | No deactivation | `workflow` statecode vs 2026-09-25 record | PASS (6 Activated, 4 Draft) |
| 18 intake settings rows | Equal to source | FetchXML, value for value | PASS |
| `rev_IntakeAllowedClientId` value | Set | `environmentvariablevalue` | PASS (set 2026-09-25); equality to the website's client id not checkable here |
| Trigger "Who can trigger the flow?" in DEV | Specific users, Allowed users = intake service principal | — | **Not verified** — no DEV step (D-05) |
| MaxLength / IsSecured / RequiredLevel | 1,048,576; five secured; None on two columns | — | **Reserved for step 8** |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Re-evaluated fresh, because an import landed after the Dev Summary was written.

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| [A-INT-01 to 05](../development/revitalise-grant-automation-dev-summary.md#L11250) | Trigger and action securing, parsing, key existence, multi-select | OPEN | An authenticated POST in DEV (IN-01 to IN-08) | Flow yes; a caller with the token, **no** | The definition carrying each shape is live and equals source | OPEN — deferred-to-pipeline |
| A-INT-06 | Unseen-route labels match the website | OPEN | The website posts one entry per route | No | — | OPEN — must close before TST/ACC |
| A-INT-08 | `RequiredLevel` None reaches DEV by import | OPEN | Metadata GET after import | Import yes; certificate **no** | — | OPEN — step 8 |
| [A-INT-09](../development/revitalise-grant-automation-dev-summary.md#L11586) | Stored choices round-trip through the refresh | OPEN | Two IN-01 posts, the second omitting phone and contact method | Flow yes; token **no** | Lookup `$select` covers every read-back column | OPEN — deferred-to-pipeline |
| [A-INT-10](../development/revitalise-grant-automation-dev-summary.md#L11587) | Import raises an existing long-text column's MaxLength | OPEN | Step 8 metadata GET on the 13 columns | Import yes; certificate **no** | **Not attempted, by instruction** | OPEN — step 8, reviewer only |

No orphan, by the gates. D-05 proposes one new row: "an import preserves the trigger's auth setting".

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Intake flow | V1 plus expression evaluation | **V3**: live definition equals source; caller check and refresh evaluated as they stand in DEV | `workflow.clientdata` | Confirmed above the claim |
| Packages | V2 (build) | V2: flow byte-identical to source in both zips | sha256 | Confirmed |
| Application form | V1 | **V3**: 115 controls identical, published | `systemform` | Confirmed above the claim |
| Field permissions, settings | V3 read | V3 | FetchXML | Confirmed |
| Column widths and securing | — | none | Needs the certificate | Step 8 |
| Flow end to end | none | none | No run in `flowrun`, no new application | V5 deferred-to-pipeline |

- Idempotency: not performed. test-agent makes no writes, and build-agent's import was a single run.
- V4 designer open and save (intake flow, Application form): **not performed**, deferred-to-pipeline. Owner: the reviewer.
- Cross-OS (C-TECH-054): N/A, no new CI script.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS. Build: 8 warnings, 1 resolved, 7 accepted, 0 untriaged.

## 8. Recommendations

1. **In one designer session on DEV: open and save the intake flow, read its trigger card, and open the Application form.** That session is V4. The trigger card answers D-05: mode "Specific users in my tenant", with Allowed users set to the intake service principal's object id.
2. **Run step 8 before the website sends long answers.** It closes A-INT-10, A-INT-08 and the open governance finding. If the 13 columns read 2,000 or 4,000, apply the width by GET, then PUT.
3. **Then the first authenticated website POST (IN-01, IN-01 again with omissions).** That is V5 and closes A-INT-01 to 05 and 09. Do not promote to TST/ACC before these close or an `OVERRIDE` is recorded.
4. **Route D-05 to development-agent, and O-6/O-7 to architect-agent at the next TAD revision.** None of them needs a rebuild of this artifact.

---

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-09-28  **Response:** `APPROVED`

**Result PARTIAL accepted, with these explicitly still open:** A-INT-10 and IMP-0934 (step 8, the reviewer's metadata GET), A-INT-08 (step 8), and A-INT-01 to 05 and A-INT-09 (the first authenticated website POST). They stay open under C-TECH-058, and promotion to TST/ACC waits for them to close or for a recorded `OVERRIDE`. Approval covers pipeline-agent's DEV post-deploy work only.

*Source of the approval:* relayed by lead-agent, quoting the reviewer's own turn in the lead session verbatim: *"Approved"*. test-agent did not see that turn itself.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0943 | `stale-claim-contradicting-rechecked-source` | friction | Read the trigger's "Who can trigger" setting back after every import into an environment that exposes the intake, DEV included. |
| IMP-0944 | `approved-document-internally-inconsistent` | friction | When a column's security classification changes, rewrite its TAD §3 row in the same change. |
| IMP-0945 | `approved-document-internally-inconsistent` | friction | Where a normalise step can turn an answer into null, gate preserve-on-omission on the raw input. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

Verification: 156 Pester tests re-run, 0 failed; 10 source gates rc 0; 28 caller-check cases; 42 write cells and 15 refresh columns checked against the live definition; 12 live DEV reads. **Not verified:** any run of the flow (V5), V4, the trigger's platform-level setting in DEV, column MaxLength/IsSecured/RequiredLevel (step 8), and whether the allowed client id equals the website's registration.
