# Test Report — Revitalise Grant Automation (intake accepts the website's native payload, wbs:4.2/4.3)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20260927-1/
**Date:** 2026-09-27
**Status:** FAIL
**WBS:** `4.2` (Appendix C field map, label maps), `4.3` (intake flow, schema). Neither task's test-results deliverable (`4.5`) is claimed by this report.
**Scope:** SDD Amendment A-08 (FR-083 to FR-093, US-024), TAD rev 11 (ADR-051, ADR-052, Appendix C, §12.3/§12.4). Tier: strategic (security/compliance cycle), per the dispatch.
**Harness mode:** Auto Mode. No provisioning certificate used. Live reads were made through `pac env fetch` on the active `svc_grantapplications` DEV profile (FetchXML, read-only).

---

## Summary

**FAIL, on one P1 defect that is older than this rework.** The intake flow's caller check is the wrong way round ([flow JSON L365](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L365)). The charity website, sending the right client id, gets a 401. Any caller sending a wrong or missing client id gets through. It has been in source since the flow's first commit and is live in DEV today. Everything the rework itself changed tested correct once that check is reversed: 9 of 9 fixture cases match their expected values exactly, and 654 of 666 "not answered" runs are clean.

**Waiting on you:** nothing, unless you approve deploying with this open. The fix is development-agent's: two actions move to the other branch, and three Pester assertions that pin the defect are rewritten. One thing to tell Alex now: if he tests against DEV today, a valid token will still get `{"error":"unauthorised"}`. That comes from this defect, not from his token.

---

## What was verified

1. **The caller check rejects the website and admits everyone else** — [flow JSON L365–L406](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L365). The condition reads *"header is not the allowed id"*, and the 401 sits in the branch that runs when that condition is **false**. An independent executor of the flow definition (test-agent's own, scratch) gives: right header → 401 Cancelled, no write; wrong header → 201, applicant and application created; no header → 201. The live DEV definition, read from `workflow.clientdata`, has exactly the same shape, and `rev_IntakeAllowedClientId` holds a value there (set 2026-09-25).
2. **The rework's own logic is correct once the check is reversed.** With only that one change made in memory, all nine cases in [intake-payloads.json](../../src/tests/data/intake-payloads.json#L576) return their expected HTTP status and every expected column value. As shipped, all nine return the wrong status (eight get 401; IN-04, the wrong-header case, gets 201).
3. **"Not answered" is one state (ADR-051 item 11), with one exception** — [TAD ADR-051](../../docs/architecture/revitalise-grant-automation-architecture.md#L2349). Every one of the 111 sample keys was sent six ways: absent, null, `""`, whitespace, `[]` and `false`. That makes 666 runs. None threw and none was rejected, except the four required keys, which gave 400 in every shape. Every conditional key's absence left its column empty with no drift note. Every always-shown key's absence was named in the note. The one exception is `age_range`, which writes 9 ("Not known") instead of leaving the field empty (D-02 below).
4. **The transfer rule holds (FR-083).** No form-generated key reaches a column. Removing `form_id`, `date_created`, `post_id`, `source_url`, payment and transaction keys, `total_estimated_cost`, `address_country`, `address_state_province`, `name_middle` or `name_suffix` changes no written value. `rev_submittedon` is the receipt time even when `date_created` is set to 2001. `rev_privacynoticeacceptedon`, `rev_breakstart` and both redacted counterparts are never written.
5. **Labels and aliases resolve, and unknown labels are flagged, not guessed (36 of 37).** `Mr.`, `Mrs.`, `  mR.  `, `Prefer to self-describe`, the en-dashed and hyphenated income bands, `Carer breakdown/urgent need`, and the three other-funding answers (awaiting → 3 with `rev_receivingotherfunding` null) all resolve. `Lord`, `Bereavement`, `Maybe`, `Sometimes` and `Carrier pigeon` each leave the column empty and add one sentence to the note. The one failure is an unknown `age_range` label (D-02).
6. **ADR-052 is built as designed, in source, in the package and live in DEV.** The two Equality Act answers are `IsSecured=0`, audited, with a `secured: exception` register row, an owner and a reason. The two descriptions are `IsSecured=1` in `REV_TrusteeRestricted`. Live in DEV, both have a `REV_TrusteeRestricted` field permission and the System Administrator row Dataverse adds only to secured columns, and the Equality Act answers have neither. Both redacted counterparts exist as columns in DEV and are empty on all 21 rows. The scoring flow references none of the six columns.
7. **DEV schema and settings match source** (the reviewer's two script runs). All nine new `rev_application` columns exist (an aggregate FetchXML over each one returns 0 values across 21 rows). `rev_otherfundingstatus` has exactly 1 Yes · 2 No · 3 Applied and awaiting decision. All 18 `rev_setting` rows the flow reads are present, and each equals `dev-scoring-settings.json` value for value.

---

## What this combination lets me claim, and what it does not

**Can claim — V3 for the schema half and the settings half, verified directly in DEV.** Columns, option set, the two field permissions and the 18 map rows are live and correct.

**Cannot claim — anything about this build's flow, forms or solution-carried changes in DEV.** The live intake flow is the 2026-09-25 version: no `Normalise_payload`, last modified 2026-09-25 18:02. So A-INT-01 to 05 and 08 cannot be executed, V4 (open and save in the designer) cannot be performed, and V5 (a real POST end to end) cannot be run. All three follow the DEV import, which comes after this gate. **And D-01 blocks four of them even after import.** A correctly authenticated POST with the right header stops at the caller check, before `Normalise_payload` runs, so A-INT-02 to 05 cannot be observed until D-01 is fixed. Only A-INT-01, the hidden trigger body, could be seen on the rejected run.

---

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — `IntakeContract.Tests.ps1`, re-run by test-agent | 106 | 106 | 0 | 0 |
| Regression — build's full Pester run (cited, not re-run: [build.log L142](../../logs/build.log#L142)) | 1186 | 1185 | 0 | 1 |
| Integration — the 9 fixture cases through an independent executor of the shipped definition | 9 | 0 | 9 | 0 |
| Integration — the same 9, caller check reversed in memory (the rework's own logic) | 9 | 9 | 0 | 0 |
| Integration — not-answered sweep, 111 keys × 6 shapes (caller check reversed) | 666 | 654 | 12 | 0 |
| Integration — labels, aliases, values, transfer rule (TC-L01–L37) | 37 | 36 | 1 | 0 |
| End-to-End — live POST in DEV (V5) | 0 | 0 | 0 | all — this flow version is not in DEV |
| Security — caller check (right / wrong / no header), OData quote-doubling, run-history securing audit | 5 | 2 | 3 | 0 |
| Accessibility | — | — | — | N/A — no custom screen; seven platform-rendered main-form controls, checked at V4 |
| Performance | — | — | — | N/A — no NFR threshold touched |
| Provisioning — live DEV reads (settings, columns, field permissions, option set, flow version) | 5 | 5 | 0 | 0 |
| Compliance — source gates re-run bare (domain-invariants, field-security-coverage, assumption-markers, assumption-register, column-security-membership, tad-coverage) | 6 | 6 | 0 | 0 |

The 12 sweep failures are 6 × `age_range` (D-02) and 6 × `preferred_contact_method` writing `""` rather than nothing (observation O-2). **106 green Pester tests sit beside a P1:** three of them assert that the rejection lives in the `else` branch, which is the defect ([IntakeContract.Tests.ps1 L316–L336](../../src/tests/solutions/IntakeContract.Tests.ps1#L316)).

## 2. Requirement Coverage

| FR ID | Requirement | Test Case(s) | Result |
|---|---|---|---|
| FR-007 | Record created automatically on submission | IN-01 through the shipped definition | **FAIL** — the website's own call is rejected 401 (D-01) |
| NFR-008 / C-TECH-006 | Only the charity website may call the endpoint | Caller check, 3 header variants | **FAIL** — inverted (D-01) |
| FR-083 | Store what the applicant entered, nothing generated; entry id the one exception | Sweep (metadata keys change nothing), TC-L30–L34 | **PASS** at source (V2); V5 deferred |
| FR-084 | Blank or unseen → empty, no default | Sweep 666 runs, TC-L22–L24 | **FAIL (P3)** — `age_range` writes 9 (D-02); every other key PASS |
| FR-085 | Hear-about-us, every ticked option, plus "other" wording | IN-01, TC-L16–L17 | **PASS** (V2) |
| FR-086 / FR-087 | The two Equality Act answers stored | IN-01, IN-06, TC-L20–L21 | **PASS** (V2); columns live in DEV (V3) |
| FR-088 / FR-089 | The two descriptions stored, secured | IN-01, IN-06; live field permissions | **PASS** (V2 write; V3 schema) |
| FR-090 | Someone helping; consents only when Yes | IN-06, IN-08, TC-L22 | **PASS** (V2) |
| FR-091 | Provisional date stored as written | TC-L18–L19 | **PASS** (V2) — see D-03 for length |
| FR-092 | Three-way other-funding answer | TC-L10–L14 | **PASS** (V2); option values live (V3) |
| FR-093 | Middle name, suffix, state not stored (OQ-053) | Sweep: those keys change nothing | **PASS** — not transferred, not built |
| FR-016 / C-DOM-030 | None of the four read by scoring | grep of every flow; `domain-invariants` | **PASS** |
| FR-035 (ADR-052 schema half) | Equality Act answers trustee-readable; descriptions only via redacted counterparts | Source, packed customizations.xml, live field permissions | **PASS** at V3 for schema; the portal binding is `wbs:6.3` and not tested here |
| US-024 AC-1 to AC-11 | — | As above | AC-3 **FAIL** (D-02); AC-1, 2, 4–11 **PASS** at V2 |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| SEC-01 | Security | Website's call, right `x-rev-client-id` | Passes the check, 201 | 401 Cancelled, nothing written | P1 |
| SEC-02 | Security | Wrong `x-rev-client-id` (IN-04) | 401 | 201, applicant + application created | P1 |
| SEC-03 | Security | No `x-rev-client-id` | 401 | 201, records created | P1 |
| SW-age | Integration | `age_range` absent / null / `""` / `[]` / `false` | `rev_agerange` empty | 9 ("Not known") | P3 |
| TC-L36 | Integration | Unknown `age_range` label | Empty plus a note | Note written, **and** 9 | P3 |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| **D-01** | **P1** | The caller check `Reject_caller_that_is_not_the_charity_website` is inverted ([L365](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L365)). Every real submission is refused, and the in-flow barrier admits any caller that is not the website. Fix: move `Respond_401_unauthorised` and `Stop_run_unauthorised` into the true branch, or drop the `not`. Rewrite the three Pester assertions that read `.else.actions` as a behavioural test: a matching header reaches `Normalise_payload`, a wrong or absent one reaches the 401. Also correct the safety argument in [verify-intake-endpoint-auth.ps1](../../provisioning/entra/verify-intake-endpoint-auth.ps1), which relies on the same wrong reading. The smoke test's verdict is unaffected. | SEC-01–03, all 9 fixture cases |
| **D-02** | P3 | `Derive_age_range` falls back to the constant 9 when no label matched and there is no date of birth ([L1080](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L1080)). That writes a default for a blank answer, against [FR-084](../../docs/plans/revitalise-grant-automation-plan.md#L1556), and a value for an unknown label, against ADR-024. It also makes "left blank" indistinguishable from "Prefer not to say". Fix: final fallback `null`. The TAD keeps the fallback "unchanged" (ADR-051 consequence 9), and the SDD approved later the same day forbids it, so the SDD governs. | SW-age, TC-L36 |
| D-03 | P3 | No text answer is length-checked before the write. `rev_provisionaldate` is 200 characters behind an uncapped free-text field, and `rev_helpername` (100) now joins five name parts. An over-long answer fails `Create_application`, so the run returns 500, the failure alert fires, and no application is created. ADR-051 item 6 intends that nothing except the four required facts rejects. Fix: truncate each TEXT answer to its column's MaxLength in `Normalise_payload`, with a note. | Inspection (the executor mocks Dataverse and cannot show it) |
| D-04 | P4 | Two schema descriptions cite the wrong requirement: `rev_provisionaldate` says FR-084 (should be FR-091), `rev_otherfundingstatus` says FR-085 (should be FR-092) ([Entity.xml L2562](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L2562)). | Source read |

**Observations — not defects, for the reviewer's judgement:**

- **O-1 — a returning applicant's stored details can be cleared.** `Refresh_existing_applicant` ([L2733](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json#L2733)) is an update. A "not answered" value there is sent as null, which clears the stored phone, address line 2 and so on. ADR-051 item 11 says *"the column is not written"*. That holds on a create but not on this update. Whether the latest submission should win is a design question.
- **O-2 — `preferred_contact_method` not answered writes `""`** to the multi-select rather than omitting it. It is almost certainly harmless, but that is unverified.
- **O-3 — TAD Appendix C is internally inconsistent in two places.** §C.2 JOIN says "two TEXT parts" while §C.1 joins five. Two stray lines from §C.1's count check are repeated after §C.1a. Neither changes the build.
- **O-4 — the failure path passes the platform's own error text, unsecured, to the failure alert.** That text can quote a value. This predates the rework and sits in the check-7 exception area that expires 2026-09-30.
- **O-5 — Alex and DEV.** DEV runs the pre-rework flow with the same inverted check and a client id set. A correct test call from Alex today is refused.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| C-DOM-004 | No personal data in logs | PASS | `rev_errorlog` receives the entry id and the action name only; O-4 noted |
| C-DOM-010 | Audit on sensitive CRUD | PASS (source); live per-column flag deferred-to-pipeline | All 9 new columns `IsAuditEnabled=1` in source and the packed zip. Live table/org switches are C-TECH-064's, after import |
| C-DOM-011 | Audit record fields | PASS | Platform audit, unchanged by this build |
| C-DOM-030 | No SC column in scoring | PASS | `verify-domain-invariants.py` rc 0; 0 references to the six columns in the scoring flow |
| C-DOM-031 | SC columns secured unless a documented exception | PASS | 19 secured, 6 exceptions printed with owner and reason; the two raw descriptions secured live (field permission rows) |
| C-DOM-032 | SC columns audited | PASS | 25/25 |
| C-TECH-001 | No secrets in source | PASS | Build secret-scan; fixtures carry no credential |
| C-TECH-004 | Input validated before persistence | PASS | Four facts reject, everything else goes to a note; 666-run sweep shows no throw; `'` doubled in every OData filter (injection-shaped id and email tested). D-03 is a gap in the same area, graded P3 |
| **C-TECH-006** | **Authentication enforced on non-public routes** | **VIOLATION** | D-01. The in-flow barrier that ADR-011 keeps "so a misconfigured trigger still leaves one barrier standing" admits every caller except the website. The platform-level control is unverified in DEV this cycle |
| C-TECH-014 | Coverage threshold | PASS | 82.46%, [build.log L142](../../logs/build.log#L142) |
| C-TECH-040 | Roles via group teams | PASS | No role assignment touched |
| C-TECH-042 | Provisioning idempotent | PASS | No provisioning logic changed (`ensure-intake-client.ps1` header only) |
| C-TECH-045 | DLP / connectors | PASS | No new connector |
| C-TECH-046 | OOB roles untouched | PASS | — |
| C-TECH-048 | Code App data access | PASS | No Code App change |
| C-TECH-051 | No fabricated platform ids | PASS | FSP id unchanged; option values author-chosen as the TAD says |
| C-TECH-052 | Every guess has a register row and marker | PASS | `verify-assumption-markers.py` rc 0 (38 OPEN rows); A-INT-01–08 present |
| C-TECH-053 | Report only the level executed | PASS | Dev Summary claims V1 and says V4 not performed, which is accurate. V3/V4/V5 for the flow: deferred-to-pipeline |
| C-TECH-054 | CI scripts cross-OS | PASS | No new CI script |
| C-TECH-056 | Diagnostic components removed | PASS | None created; test-agent's reads wrote nothing |
| C-TECH-057 | Gates proven able to fail | PASS | No new gate; FR-016 alternation extended under existing negative tests |
| C-TECH-058 | OPEN assumption blocks deploy where closeable | deferred-to-pipeline — A-INT-01–05, 08, evidence available after the DEV import | A-INT-06 must close before TST/ACC |
| C-TECH-059 | Learning substrate kept | PASS | Own artifact directory; log appended |
| C-TECH-060 | Shipped text within limits | PASS | Build `field-length-limits`; note capped at 1,990 + ` [trunc]` = 1,998 ≤ 2,000 |
| C-TECH-064 | Live environment state verified after deploy | deferred-to-pipeline | No deploy of this build yet |
| C-TECH-065 | Identity probe before trust | PASS | `pac` reports `Connected as svc_grantapplications … REV-GrantApplications-DEV` on every read |
| C-TECH-066 | TAD tables are a checked spec | PASS | `verify-tad-coverage.py` rc 0, 41 trustee-visible; TD-010 cleared |
| C-TECH-068 | Negative access evidence only on live controls | PASS | No negative access result claimed this cycle |
| C-TECH-069 | Readers survive a second instance | PASS | Build `source-reader-plurality` |
| C-TECH-070 | Secured only where securable | PASS | Both secured columns are multiline text |
| C-TECH-071 | Declared property reaches creation | PASS | Build step; `IsSecured` confirmed reaching DEV for both descriptions |
| C-TECH-073 | Metadata writes are PUT | PASS | None authored; A-INT-08's remedy names PUT |
| C-TECH-078 | Geometry measured in a browser | PASS | No geometry claim |
| C-TECH-079 | Work items move on evidence | PASS | None carried; none to reopen |
| C-TECH-067 (SOFT) | Counts derived from source | WARNING | Pre-existing literals, including the scoring suite's 34 |

Compliance: CR-01 (special-category data never reaches a trustee) holds for the two descriptions at V3. For the two Equality Act answers, trustee exposure is the approved decision (ADR-052), not a breach. CR-02 holds. CR-04 holds, with O-4 noted.

## 6. Provisioning Verification

| Item (TAD §12.4) | Expected | Verified Via | Result |
|---|---|---|---|
| Global option set `rev_otherfundingstatus` | 1 Yes · 2 No · 3 Applied and awaiting decision | `stringmap` FetchXML, DEV | PASS |
| Nine `rev_application` columns (two conditional not built) | Exist | Aggregate FetchXML naming each column, DEV (21 rows, 0 values) | PASS |
| `REV_TrusteeRestricted` create/read/update on the two descriptions; not on the Equality Act answers | 2 rows, Allowed ×3 | `fieldpermission` ⋈ `fieldsecurityprofile`, DEV | PASS (plus Dataverse's own System Administrator rows) |
| Special-category register, four rows | 2 exceptions + 2 required | Source; `domain-invariants` rc 0 | PASS |
| NFR-031 necessity record in the two Equality Act descriptions | Present | Entity.xml and packed customizations.xml | PASS |
| Two redacted counterparts, schema now, writer later | Exist, empty, never written by intake | FetchXML DEV; executor | PASS |
| Main-form controls | 7 | Packed customizations.xml | PASS (V2); V3/V4 after import |
| `RequiredLevel` None on `rev_dateofbirth`, `rev_email` | None | Packed zip shows None | V2 only — A-INT-08 |
| 18 intake `rev_setting` rows | Equal to source | FetchXML DEV, value for value | PASS (18/18) |
| Trigger "Specific users" + second gate per environment | Set and verified | — | Not verified in DEV this cycle; second gate is D-01 |

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Re-evaluated fresh this cycle: no import of this build has landed since the Dev Summary was written (live flow modified 2026-09-25).

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| [A-INT-01](../development/revitalise-grant-automation-dev-summary.md#L11250) | Trigger `secureData outputs` hides the body | OPEN | This flow version in DEV + one POST | DEV yes; version **no** | Source and package carry it | OPEN — deferred-to-pipeline. Observable even on a D-01 rejection |
| A-INT-02 | Per-action `secureData` hides data; 90 actions | OPEN | Same run past the caller check | No, and **blocked by D-01** | 90 of 138 actions secured; the 48 unsecured carry no applicant value except the entry id (by design) and O-4 | OPEN |
| A-INT-03 | `isFloat`/`isInt`/`float` en-GB behave, never throw | OPEN | DEV run with IN-05 | No, blocked by D-01 | Executor agrees under eager `if()`: that is not a platform level | OPEN |
| A-INT-04 | `contains(triggerBody(), item())` tests key existence | OPEN | DEV run with IN-05 | No, blocked by D-01 | Executor: drift note correct for all 40 always-shown keys, silent for every conditional key | OPEN |
| A-INT-05 | Map-filter multi-select yields a de-duplicated list | OPEN | DEV run with IN-01/05/06 | No, blocked by D-01 | Executor: `1,4` with a duplicate label; null when nothing matches | OPEN |
| A-INT-06 | Unseen-route labels are what the website sends | OPEN | Alex posts one entry per route | No | — | OPEN — **must close before TST/ACC** |
| A-INT-07 | *(withdrawn)* | WITHDRAWN | — | — | Omission handled: IN-07 plus the 666-run sweep | Withdrawal confirmed |
| A-INT-08 | `RequiredLevel` None reaches DEV by import | OPEN | After import, a metadata GET | No (import pending) | Packed zip shows None | OPEN — needs the provisioning certificate, below |

No orphan: `verify-assumption-markers.py` rc 0. The dispatch named A-INT-01–08 "in the TAD". The TAD's §12.3 holds 01–07, and 08 exists only in the Dev Summary.

**REVIEWER ACTION REQUIRED (after the DEV import, for A-INT-08 only; needs `PROVISION_APP_ID` / `PROVISION_CERT_THUMBPRINT`, which this session does not hold):**

```
GET EntityDefinitions(LogicalName='rev_applicant')/Attributes(LogicalName='rev_dateofbirth')?$select=RequiredLevel   -> None
GET EntityDefinitions(LogicalName='rev_applicant')/Attributes(LogicalName='rev_email')?$select=RequiredLevel         -> None
```

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Intake flow JSON | V1 | **V2** — the packed definition is byte-for-byte equal to source | Unzipped managed zip | Confirmed, but carries D-01 |
| Schema (9 columns, option set, 2 field permissions) | V1 | **V3** in DEV (provisioning route) | FetchXML reads above | Confirmed above the claim |
| Settings rows | V1 | **V3** in DEV, 18/18 equal to source | FetchXML | Confirmed above the claim |
| Forms, `RequiredLevel`, FSP-by-solution | V1 | V2 | Packed customizations.xml | V3 deferred-to-pipeline |
| Flow end to end | none | none | — | V5 deferred-to-pipeline, and blocked by D-01 |

- Idempotency: N/A this cycle — no deploy run by test-agent. Whether the reviewer's two script runs were repeated is not recorded.
- V4 designer open + save: **not performed** — deferred-to-pipeline (needs the import).
- Cross-OS (C-TECH-054): N/A — no new CI script.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS — build triaged 5/5; none created.

## 8. Recommendations

1. **Fix D-01 before anything is imported.** It is a two-action move plus a test rewrite. Without it, the DEV import delivers a flow that refuses Alex and cannot close A-INT-02 to 05.
2. **Fix D-02 and D-04 in the same pass.** Each is one line. Take D-03 if the reviewer wants it now. Otherwise record it as a known risk: an over-long answer loses the application, with an alert.
3. **Tell Alex (O-5)** that a 401 with `{"error":"unauthorised"}` from DEV is our defect, so he does not spend time on his token.
4. **Then retest with `REQUEST RETEST`** against the next artifact. Scope: the caller check (behavioural), the age-range fallback, and a re-run of this report's executor cases. After import, pipeline-agent runs IN-01 to IN-08 in DEV. That run is what closes A-INT-01 to 05, and the metadata GET above closes A-INT-08.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0926 | `test-asserts-the-defect` | rework | Test a guarding If by evaluating its condition with a passing and a rejected value; never assert only which branch holds the rejection. |
| IMP-0927 | `approved-document-internally-inconsistent` | friction | A fallback the TAD keeps "unchanged" is not exempt from a later requirement that forbids defaults; test every key's not-answered shape. |
| IMP-0928 | `live-verification-capability` | friction | Under Auto Mode, `pac env fetch` on the active profile still reads rows, attribute existence, field permissions and a flow's live definition. |
| IMP-0929 | `dispatch-brief-asserts-unverified-fact` | friction | Resolve a brief's named register or digest section before relying on it. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

Verification: 106 Pester tests re-run; 6 source gates re-run bare, all rc 0; 721 executor runs (9 + 9 + 666 + 37); 7 live DEV FetchXML reads. **Not verified:** anything about this flow version in DEV (not imported), V4, V5, the trigger's platform-level authentication setting in DEV, `RequiredLevel` live, and platform behaviour for `""` on a multi-select and for over-length text (the executor mocks Dataverse).
