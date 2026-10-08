# Test Report — Narrative Scrubbing (Automation #5), build 20261007-3

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261007-3/
**Date:** 2026-10-07
**WBS:** wbs:5.3, 5.4, 5.6. This report is test evidence for those tasks. It is **not** the task 5.7 sign-off, which needs a live calibration run.
**Status:** FAIL (one open HARD defect, a missing register row; no defect found in the flow, the form, the view or the package)

**Conclusion.** Nothing in the shipped source is wrong: 199 narrative tests, 1,339 Pester tests, 790 + 888 Code App tests, 19 of 19 source gates and 76 further build-gate commands all pass when re-run here, and the packed flow is byte-identical to source. The run is FAIL for one reason: the flow is built to the exact edge of Power Automate's nesting limit, and the way that limit is counted is a platform guess that has no row in the assumptions register ([C-TECH-052](../../constraints/technology/technology-constraints.md#L107), defect D-1). The fix is one register row and one source marker; no change to the packed solution is needed. Everything else is PARTIAL by nature: nothing has been imported, so the highest level confirmed is V2 plus simulated execution.

---

## 1. Test Summary

All counts are from runs made by test-agent on 2026-10-07 against the working tree, not copied from the build log. The build's own figures match.

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit — narrative logic and flow definition (`python3 -m unittest discover -s src/tests/narrative`) | 199 | 199 | 0 | 0 |
| Unit — Pester, all of `src/tests` (285 s) | 1,340 | 1,339 | 0 | 1 |
| Coverage gate (`verify-coverage-threshold.py`, on a fresh report from my Pester run) | 1 | 1 (91.57% of lines, 2,304 of 2,516, against 80%) | 0 | 0 |
| Unit — Code App vitest, `trustee-review-portal` | 790 | 790 | 0 | 0 |
| Unit — Code App vitest, `trustee-review-portal-cards` | 888 | 888 | 0 | 0 |
| Static — `tsc --noEmit`, both apps | 2 | 2 | 0 | 0 |
| Source gates (`run-source-gates.py`) | 19 | 19 | 0 | 0 |
| Further build-gate commands re-run from `run-build-result.json` (python gates and grep gates) | 76 | 76 | 0 | 0 |
| Packed artefact inspection (unzip both packages) | 12 checks | 12 | 0 | 0 |
| Mutation probes of my own on the shipped flow | 9 effective | 9 caught | 0 | 0 |
| Integration / End-to-End / Performance | — | — | — | not run: nothing is imported, no flow has run on the platform |
| Security | static and simulated only | pass | 0 | live half needs DEV (section 8) |
| Accessibility | — | — | — | platform-rendered form tab; needs a V4 look (section 8) |
| Provisioning (TAD §12 items on a live org) | — | — | — | not run: needs DEV. No new provisioning script in this change |
| Cross-OS | — | — | — | NOT VERIFIED on the CI runner; all runs here and in the build were macOS |

My first two mutation probes (settings prefix, auto-release comparison) edited description text and not logic, so they survived. That was my error, not a gap: I redid both against the real expressions and they were caught. The table counts only the 9 mutations that changed behaviour.

### 1.1 What the mutation probes showed

I changed one thing at a time in a copy of the flow file, ran all 199 narrative tests, and restored the file (md5 identical before and after). All 9 were caught: run-action `recordId` changed (77 failures); `secureData` removed from the run action (2); trigger filter removed (18); decision write pointed at `rev_status` (243); settings filter prefix broken (222); stale and on swapped (212); auto-release needs `false` (212); prompt `Narrative` input made constant (3); review-required column misnamed (3). No survivor.

## 2. Requirement Coverage

| Requirement | Test case(s) | Result |
|---|---|---|
| FR-026 redacted copy with category labels ([plan](../plans/revitalise-grant-automation-plan.md#L1380)) | Corpus loop, 20 samples × both string semantics × `{}` and full settings (`test_each_sample_alone_in_the_narrative_column_both_string_semantics`, [L173](../../src/tests/narrative/test_scrub_flow_definition.py#L173)); 8 postcode samples | Covered in simulation. Not run on the platform |
| FR-027 age band and region | Age band: corpus. **Place half deferred by reviewer decision D-1** ([rules §12](../development/revitalise-redaction-rules.md#L651), 2026-10-06): a town on its own is kept | Covered as designed; the place half is a recorded deferral, not a gap |
| FR-028 keep region, dates, circumstances | Corpus expected outputs keep them | Covered in simulation |
| FR-029 withhold below threshold ([plan](../plans/revitalise-grant-automation-plan.md#L1383)) | `test_threshold_boundary_and_forms`, `test_absent_settings_hold_every_record` ([L218](../../src/tests/narrative/test_scrub_flow_definition.py#L218)); columns `rev_redactionconfidence`, `rev_redactionreviewrequired` present in the packed solution | Covered in simulation. The threshold row is not seeded by design, so every record is held (designed safe state) |
| FR-030 review, correct, release | Review Required view filter read directly; sitemap entry; form tab with 12 read-only raw and 12 editable redacted controls plus the three decision fields (parsed by me: 27 controls, no duplicate ids, every bound column exists) | Covered at V2. The tab and the view have never been opened by a person |
| FR-031 raw text readable by admin and service only | Column security profile unchanged; no trustee column added; `no-secured-columns-in-code-app` gates | Covered by the existing control. Live proof is C-TECH-064 / C-TECH-068, post-deploy |
| NFR-012 / C-DOM-004 no text in logs | Canary tests `RunHistoryAndVariables` (`test_every_action_that_sees_text_hides_it`, `test_no_variable_ever_holds_text`, `test_the_notification_carries_reference_and_codes_only`); my run-action mutation (secure data removed) fails 2 tests | Covered in simulation. `A-NS-12` (does `secureData` really hide it in run history) is OPEN |
| NFR-017 / NFR-019 tunables in `rev_setting` | `Rev20Settings`, `WordListSettings`, guard-rail tests; my filter mutation fails 222 tests | Covered in simulation |
| NFR-018 fail closed | `FailClosedPaths` (extractor, unreadable answer, unmapped type, over-length, prompt on and misconfigured) | Covered in simulation |
| NFR-009 UK residency | Not met: all three environments are in Switzerland ([IMP-1063](../../logs/improvement-log.jsonl), parked at the customer by the reviewer). The prompt stage, the only cross-region path, ships OFF | Known, decided to park. Not a build defect. See section 5, C-TECH-061 note |
| ADR-071, ADR-072 | Reason codes, residue checks, prompt validation (23 answer shapes) | Covered in simulation |
| ADR-073 register | `Rev20Register` (`test_the_postcode_table_row_by_row`, short or failed register fails closed) | Covered in simulation. `A-NS-21` (one read returns all 3,394 rows) OPEN |
| ADR-074 settings | Additions only, malformed row ignored whole, any edit stales auto-release | Covered in simulation. `A-NS-22` (`modifiedon` format) OPEN |
| TD-008 columns | `tad-coverage` exit 0; type lock updated; `TD-008` deleted from the deferrals file | PASS |

### 2.1 The configuration defaults the TAD declares fail-safe (IMP-0511, blocker class)

The TAD names two: no `RedactionAutoRelease` row (every record held, [TAD §5.5](../architecture/revitalise-grant-automation-architecture.md#L1232), "What a person sees") and no `RedactionPromptStage` row (stage off, rev 19 behaviour). The approved outcome under the first is: the redacted copy is written, the record appears in the process owner's review list with `auto-release-off`, one card is posted, and she releases by hand.

- **Reaches that outcome under the exact unseeded default:** `_compare` ([L162](../../src/tests/narrative/test_scrub_flow_definition.py#L162)) runs the shipped flow with `{}` settings for all 20 corpus samples and asserts the written counterpart equals the expected text, the decision write (`released` false, `reviewrequired` true, confidence) equals the model's, and `bool(notices) == review_required`. `test_absent_settings_hold_every_record` ([L218](../../src/tests/narrative/test_scrub_flow_definition.py#L218)) asserts the reasons, `released` false and one card.
- **I confirmed it independently** with a probe on a record containing a name, a phone number and a postcode, with no settings: counterpart `My carer [NAME] visits. Call [PHONE]. We live at [ADDRESS].`, `released` false, `reviewrequired` true, reasons `threshold-missing-or-invalid, auto-release-off`, one card.
- **The list the person opens matches:** [RedactionReviewRequired.xml](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/SavedQueries/RedactionReviewRequired.xml) filters `reviewrequired = 1` and `released <> 1`, and the flow writes both explicitly on every run, so the view and the writer agree.
- **Stage off:** `test_the_stage_does_not_run_when_off_or_misconfigured` ([L607](../../src/tests/narrative/test_scrub_flow_definition.py#L607)); my probe with `RedactionPromptStage = on` and nothing else gives `prompt-config-invalid` and `uncalibrated-stage:prompt`, and the run action is not called.

No test is pinning a defect here: the asserted outcome matches the design sentence. The only residual is that this outcome has never been seen by a person in the Review Required view (section 8).

## 3. Failed Tests

None.

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-1 | P1 by rule (HARD [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) orphan); practical size: one documentation row | The flow nests containers **8 deep**, and its deepest actions (for example `Select_prompt_items`, under `Validate_the_prompt_answer`) sit inside all 8. `PlatformLimits` ([L704](../../src/tests/narrative/test_scrub_flow_definition.py#L704), assertion at [L748](../../src/tests/narrative/test_scrub_flow_definition.py#L748)) counts containers and passes at 8. Whether the platform counts the 8th container's children as a ninth level is a platform contract, taken from documentation (E2) and never confirmed. It has **no register row** (the register stops at `A-NS-25`), no `A-nnn` marker, and the notes file states it as fact ([notes.md#L155](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md#L155)). No other flow in the solution has more than 5 enclosing containers, so nothing already imported shares the edge. The same row should carry the flow's size: 344,007 bytes against 255,516 for the largest flow already live. Both the register gate and the marker gate pass, because they read rows that exist; neither can see a guess that was never entered | none can exist: this is a platform answer |
| D-2 | P3 | A stray `q.xml` sits untracked at the repository root, a leftover diagnostic `pac env fetch` query on `msdyn_aitemplate`. It is not in the package (checked) but it is repository litter from an investigation. Delete or ignore it | n/a |
| D-3 | P3 | **None of this feature's source is committed.** The flow, its notes and metadata, the Review Required view, the card, the rules and prompt documents, and all new narrative tests are untracked or modified; the manifest records 51 dirty paths and `source_commit` is `55d366a`, which holds none of them. The package cannot be traced to a commit until they are. This also sweeps in the sibling dispatch's Code App changes (vitest 3.2.7 to 5.0.3, lockfile rewrite; `IMP-1072`), which my test run covers (790 and 888 pass) but which are outside this feature's scope | n/a |

D-1 is the only item that stops this report from being PARTIAL. The retest after the fix is cheap: add the row, add the marker, rerun the register and marker gates.

## 5. Constraint & Compliance Verification

Scope: rows naming test-agent that this change touches. Rows outside this change are not re-judged.

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data in logs | PASS (simulation) | Canary tests, and my `secureData` mutation fails 2 tests. Live half: `A-NS-12` |
| [C-DOM-010](../../constraints/domain/domain-constraints.md#L47) / [C-DOM-011](../../constraints/domain/domain-constraints.md#L48) | Audit of sensitive-entity writes | PASS (source) | Both new columns `IsAuditEnabled=1`; `audited-tables` gate exit 0. Live audit switch is C-TECH-064, post-deploy |
| [C-DOM-030](../../constraints/domain/domain-constraints.md#L92) | No special-category column influences scoring | PASS | `no-special-category-data-in-scoring` and `domain-invariants` exit 0; the new flow is not a scoring flow |
| [C-DOM-031](../../constraints/domain/domain-constraints.md#L93) / [C-DOM-032](../../constraints/domain/domain-constraints.md#L94) | Register columns secured and audited | PASS | `field-security-coverage`, `domain-invariants` exit 0; `IsSecured` unchanged on every free-text column; the two new columns are a score and a flag, not secured, audited |
| [C-TECH-001](../../constraints/technology/technology-constraints.md#L34) | No secrets | PASS | `secret-scan` exit 0 in the build |
| [C-TECH-004](../../constraints/technology/technology-constraints.md#L37) | Inputs validated | PASS (simulation) | 23 prompt answer shapes; malformed settings ignored whole |
| [C-TECH-014](../../constraints/technology/technology-constraints.md#L52) | Coverage threshold | PASS | 91.57% of lines, measured by me on my own report (Pester's command figure is 75.71%, a different number, now labelled as such) |
| [C-TECH-045](../../constraints/technology/technology-constraints.md#L87) | DLP-compliant connectors | PASS (source) | The flow uses `shared_commondataserviceforapps` (including the two AI Builder operations) and `shared_teams`, both already bound by other flows. No new connector |
| [C-TECH-051](../../constraints/technology/technology-constraints.md#L93) | No fabricated platform ids | PASS | The AI model id `122be8e0-…` is the export's own, identical in `Solution.xml`, `Customizations.xml`, the flow's `recordId` and both packed zips. The view id follows the live-proven `rev_sub_autopass` pattern |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Guessed contracts in the register | **FAIL** | D-1. Register and marker gates exit 0 (22 OPEN `A-NS` rows, markers present); one orphan found by reading, not by gate |
| [C-TECH-053](../../constraints/technology/technology-constraints.md#L108) | Level claimed equals level reached | PASS (claims) / PARTIAL (reach) | Dev Summary §4.11 claims V1, V2, E1 and "simulator", and says V3 to V5 are not reached. I confirm exactly that |
| [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) | Scripts run on the CI OS | NOT VERIFIED | Python stdlib and Pester only, no OS-specific API in the two changed scripts (diff read), but never executed on the Linux runner |
| [C-TECH-055](../../constraints/technology/technology-constraints.md#L110) | Tool warnings triaged | PASS | Manifest: 5 warnings, 5 accepted, 0 untriaged. Solution Checker: Critical 0, High 0, Medium 15 (14 on this flow, 1 standing), each a `flow-avoid-recursive-loop`. The false-positive reasoning holds up: the trigger filters `rev_status` only, the 10 `NoTriggerLoop` tests pass, and my own mutations (trigger filter removed, decision write pointed at `rev_status`) are both caught |
| [C-TECH-056](../../constraints/technology/technology-constraints.md#L111) | No diagnostic components shipped | PASS | No diagnostic action in the 306; the only AI model in the package is the prompt. Every live call was a read. `q.xml` (D-2) is repository litter, not a component |
| [C-TECH-057](../../constraints/technology/technology-constraints.md#L127) | Every gate can fail | PASS | New root-component branch and after-deploy branch each have positive and negative tests (Pester 1,339 pass); my mutations show the narrative gates fail on breakage |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumptions block deployment | **PASS for the DEV import, BLOCKS later environments** | Section 7.3. No `OVERRIDE` needed for DEV |
| [C-TECH-060](../../constraints/technology/technology-constraints.md#L130) | Text length limits | PASS | `field-length-limits` exit 0 (one 369-character description was found and fixed by development-agent); longest expression 3,661 of 8,192 |
| [C-TECH-064](../../constraints/technology/technology-constraints.md#L134) | Live state verified after deploy | NOT RUN | Nothing deployed. Source half: `audited-tables` exit 0 |
| [C-TECH-066](../../constraints/technology/technology-constraints.md#L136) | TAD is a checked specification | PASS | `tad-coverage` and `tad-coverage-cards` exit 0 (203 column specs, 5 deferred, TD-008 cleared) |
| [C-TECH-067](../../constraints/technology/technology-constraints.md#L137) | Counts derived from source | PASS | `source-derived-test-counts` and `derived-counts` gates ran exit 0; the 86-root-component and 12-control figures are read from source |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) | Secured-column shapes | PASS | New columns are a plain decimal and a plain bit, unsecured; no change to a secured shape |
| [C-TECH-079](../../constraints/technology/technology-constraints.md#L149) | Work items move on evidence | PASS for this feature | No items carried. `verify-work-items.py` reports one failure, `WI-0009`, whose evidence needle is gone from `CasePanels.tsx`. That file is unchanged since 2026-09-30 and is not touched here, so it is not a regression from this build (soft gate in the build, exit 0) |

**Governance note, not a constraint failure for DEV.** [IMP-1063](../../logs/improvement-log.jsonl) (residency, `governance` lane) is open. C-TECH-061 would hold the production deploy while it stands. NFR-009 is measured NOT MET, parked at the customer by the reviewer, and the stage that would move text across regions is off.

## 6. Provisioning Verification

Not run: no environment holds this build. No new TAD §12 item is introduced by this change. Two things the DEV import relies on, both stated in the Dev Summary: `ensure-schema.ps1` runs before the import and creates the two new columns from `Entity.xml` (TAD §12.1), and the flow imports switched off and is bound and switched on by a person. The new after-deploy check for the AI model (`msdyn_aimodels(<id>)`) is the only live provisioning check this change adds; its Pester test passes in both directions.

## 7. Platform Contract & Verification-Level Audit (C-TECH-052, C-TECH-053)

### 7.1 Assumption register closure

Closing precondition for **every** open row is the same fact, stated once: *this build has not been imported into DEV.* DEV exists. Rows are grouped by what actually closes them (read from each row's own "cheapest verification" column, Dev Summary [§2.10](../development/revitalise-narrative-scrubbing-dev-summary.md#L416), [§3.10](../development/revitalise-narrative-scrubbing-dev-summary.md#L666), [§4.10](../development/revitalise-narrative-scrubbing-dev-summary.md#L901), Iteration 1 [§10](../development/revitalise-narrative-scrubbing-dev-summary.md#L149)).

| Assumption ID(s) | Claim (short) | Status per Dev Summary | Closing precondition | Does it exist yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-NS-6, A-NS-7, A-NS-17 | Form: duplicate read-only controls with id `<field>1`; side-by-side layout; Decimal control renders and saves | OPEN | Import to DEV, open the form in the designer and on a record, save, re-export | DEV exists; build not imported | Form parsed: 27 controls, ids unique, 12 raw controls `disabled="true"`, every column exists. Rendering unverifiable | OPEN |
| A-NS-9 | AI model component imports and keeps its id, so `recordId` resolves | OPEN | The import, then the after-deploy check prints `PASS — AI model …` | Same | Id identical in all five places; both zips hold the block and the type-401 root component. The claim names TST/ACC and PRD too, so its cross-environment half closes only there | OPEN |
| A-NS-1, 2, 3, 4, 5, 12, 13, 15, 16, 18, 19, 21, 22, 24 | Flow behaviour on the platform: extractor type strings and offsets, 5,000-character limit, US-format detection, `secureData`, action shape and output path, `sort`/`take`/`lastIndexOf`/`split` semantics, register read size, `modifiedon` format, loop failure naming | OPEN | One flow run in DEV on a test application (and a few test `Compose` actions) | Same | Simulated under both string semantics; mutations caught. Nothing about the platform | OPEN |
| A-NS-8, A-NS-10, A-NS-20 | Prompt answer: `finishReason` values, JSON in `text`, 16,000 + 5,000 character input | OPEN | A DEV prompt run (rows R2–R5), which needs the reviewer to switch the stage on with synthetic data | Same | 23 answer shapes simulated; the run action's names and answer path were checked by development-agent against the designer-saved action (E1) and I re-ran those tests | OPEN |
| A-NS-23 | A prompt can be created and run with *Move data across regions* off | OPEN | TST/ACC (DEV's setting was already on, so DEV cannot answer it) | **No**: the closing environment holds no build | n/a | OPEN, not closeable before TST/ACC |
| A-NS-25 | Run action operation, `recordId` and the answer path | CLOSED (E1, 2026-10-07) | Designer-saved action read from DEV | Yes | `test_the_run_action_matches_the_designer_saved_action`, `test_the_answer_path_is_the_one_the_designer_writes` pass; both path mutations fail | CLOSED at E1; never run |
| **ORPHAN** | Container nesting limit counted as containers (8 deep), and flow size | **no row** | A DEV import and a designer save | DEV exists | Section 4, D-1 | **DEFECT** |

All five rows the caller named (A-NS-8, 9, 10, 20, 23) are OPEN as stated; A-NS-25 is CLOSED as stated. The register and marker gates report 78 OPEN rows across the repository with every marker present.

### 7.2 Verification levels achieved

| Component | Level claimed (Dev Summary §4.11) | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Scrubbing flow (306 actions) | V1, executed in simulator | V1 + simulator; **V2 confirmed** for the packed copy | Packed flow md5 `193bccb8…` identical in the unmanaged zip, the managed zip and source | Confirmed |
| AI model (prompt) component | E1 (export) and V2 | V2 | Both zips: one `<AIModels>` block, one `type="401"` root component, id `122be8e0-…`, `Managed` 0 and 1 as expected | Confirmed |
| Form tab, view, sitemap entry, two columns | V2 | V2 | Packed `customizations.xml` holds `tab_narrativescrubbing` in both zips; the view and sitemap parsed | Confirmed |
| Run action and answer path | E1 (designer-saved, never run) | E1 | Fixture and tests re-run | Confirmed, never run |
| Solution Checker | Medium 15, triaged | Confirmed | Log read: Critical 0, High 0, Medium 15, Low 0 | Confirmed |
| Anything at V3, V4 or V5 | Not claimed | None | Nothing imported | PARTIAL |

- Idempotency: deploy re-run against an already-deployed target: NOT RUN (nothing deployed).
- V4 designer open and save, then re-read live ([IMP-1020](../../logs/improvement-log.jsonl)): NOT PERFORMED. Owner: the reviewer. This flow is the largest in the solution and the form tab uses an unproven duplicate-control id; both are exactly the shape that has failed to save before.
- Cross-OS (C-TECH-054): NOT VERIFIED on the CI runner.
- Warnings triaged (C-TECH-055) and diagnostic components removed (C-TECH-056): PASS, with D-2 noted.

### 7.3 C-TECH-058: which rows need an `OVERRIDE`

**Before a DEV import: none.** Each OPEN row's own "cheapest verification" names a DEV import, a designer check or a DEV run as the check, and the 2026-10-05 amendment of [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) says such a row does not block the DEV deploy; pipeline-agent records it as measured by the deploy. Applied to the five rows you named:

| Row | DEV import | Why |
|---|---|---|
| A-NS-9 | No override | Its check is the import and the after-deploy check. Its TST/ACC and PRD half is a later-environment matter |
| A-NS-8, A-NS-10, A-NS-20 | No override | Check is a DEV prompt run; the stage ships off, so the import neither exercises nor depends on them. They are not closed by the import alone: they need the reviewer's R2–R5 steps |
| A-NS-23 | No override | **Cannot be closed in DEV** (the setting was already on there), so DEV is not "an environment in which it could be closed". It is the one row I expect to need an `OVERRIDE A-NS-23` at the **TST/ACC** step, because the amendment's carve-out is written for DEV only, unless the reviewer widens it |

**Later environments:** every row above blocks TST/ACC and PRD until closed in DEV (A-NS-23 until closed in TST/ACC), as the amendment says.

D-1's new row, once added, falls in the same class: its check is the DEV import and designer save.

## 8. Checks that need DEV, left for post-deploy

1. Import this build into DEV and read the after-deploy output: `PASS — AI model 122be8e0-… exists`; the solution shows *REV Narrative Redaction Prompt* once.
2. Open the scrubbing flow in the designer, save, and re-read it live (`verify-live-flow-definitions.py --env dev`). Confirm `Run_the_redaction_prompt` shows the prompt by name with three inputs filled. This is also the check for D-1.
3. Open the Application form's Narrative Scrubbing tab as the grant admin: raw left read-only, redacted right editable, labels above, the three decision fields, save, reopen (A-NS-6, A-NS-7, A-NS-17).
4. Open *Redaction - Review Required* from the navigation; confirm it opens.
5. Set one synthetic test application to Eligible for Panel with corpus sample S08 in the narrative (Dev Summary §2.9), with no settings seeded. Expect a written counterpart, `released` No, `reviewrequired` Yes, reasons `threshold-missing-or-invalid` and `auto-release-off`, no `postcode-register-unavailable`, one card, and run history showing no text. This closes most of the A-NS flow rows and is the live version of the section 2.1 outcome.
6. Confirm the flow's connection identity can read the secured raw columns. If it cannot, it reads empty text and scrubs nothing; the record stays withheld, but silently (C-TECH-064, C-TECH-068).
7. Do not set `RedactionPromptStage` in DEV until the reviewer decides to run R2–R5; then A-NS-8, 10 and 20 close.
8. Check A-NS-23 in TST/ACC before the import that brings the prompt there.

## 9. Recommendations

- Development-agent: add the register row for the nesting rule and flow size (suggested id `A-NS-26`, E2, where-in-source: the `PlatformLimits` test file, check: the DEV import and a designer save), put the marker at the assertion, and correct [notes.md#L155](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md#L155) to say "counted as containers, unconfirmed". No flow change and no repack is required, so build-agent need not be re-run unless the lead wants a fresh manifest.
- Commit the feature's source before the pipeline stage (D-3), separately from the sibling Code App changes if possible, so the artifact's provenance line points at a commit that contains it.
- Delete `q.xml` (D-2).
- If the flow ever needs one more container inside the prompt stage, the notes already say it breaks the limit. Treat that as a refactor trigger, not a tweak.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1092 | `platform-contract-guessed-not-groundtruthed` | friction | A platform limit the flow is built exactly to, and the way the limit is counted, is a platform contract: register it before the import, and do not read two green gates as proof it has a row. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
