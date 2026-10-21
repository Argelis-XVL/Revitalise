# Dev Summary Document — Narrative Scrubbing (Automation #5)

**Feature slug:** `revitalise-grant-automation` (shared build configuration; see Iteration 2 §8)
**TAD reference:** `docs/architecture/revitalise-grant-automation-architecture.md`, rev 19 (§5.5, `ADR-071`, `ADR-072`) for Iterations 1–2; rev 20 (§5.5.1, §12.6.1, `ADR-073`, `ADR-074`) for Iteration 3; **rev 22 (§5.5, §5.5.1, `ADR-075`, §12.6.1) for Iteration 9; rev 23 (`ADR-076`) for Iterations 10 and 11; rev 25 (`ADR-078`, and the record of Iteration 11) for Iteration 12**
**Items:** none carried

| Iteration | Date | WBS | Status |
|---|---|---|---|
| 1 — rules v0.1, corpus, harness, review tab | 2026-10-05 | `wbs:5.1`, `5.2`, `5.4` (tab) | **APPROVED 2026-10-06** (Xander Lykopoulos, *"Approved development work"*) |
| 2 — the scrubbing flow, the `TD-008` columns, the Review Required view, rules v0.2 | 2026-10-06 | `wbs:5.3`, `5.4` (flagging and view), `5.1` (rules v0.2) | **APPROVED 2026-10-06** (*"Code review approved."*, `logs/routing.log` 20:45), with Iteration 3 — [jump to Iteration 2](#iteration-2--the-scrubbing-flow-2026-10-06) |
| 3 — postcode register, tunable settings with guard rails, the prompt stage up to the DEV boundary, rules v0.3 | 2026-10-06 | `wbs:5.3`, `5.6` (settings the process owner tunes), `5.4` (new review reasons) | **APPROVED 2026-10-06** (with Iteration 2) — [jump to Iteration 3](#iteration-3--register-settings-and-the-prompt-stage-2026-10-06) |
| 4 — build blocker `IMP-1082`, the coverage reading, the prompt component and its run action | 2026-10-06 | `wbs:5.3` (component, run action), `5.4` (form test) | **APPROVED 2026-10-07** (*"Approved on dev summary"*); six changes after approval, one affecting the prompt component, listed under *Approval (Iteration 4)* — [jump to Iteration 4](#iteration-4--build-fix-and-the-prompt-run-action-2026-10-06) |
| 5 — the failure diagnosis moves inside the column loop (designer save refused, `IMP-1098`) | 2026-10-09 | `wbs:5.3` | **Awaiting code review** — [jump to Iteration 5](#iteration-5--the-failure-diagnosis-moves-inside-the-column-loop-2026-10-09) |
| 7 — first live DEV run: `substring()` started at the string length (`IMP-1109`) | 2026-10-12 | `wbs:5.3` | **Awaiting code review** — [jump to Iteration 7](#iteration-7--substring-never-starts-at-the-string-length-2026-10-12) |
| 8 — the client's Anonymisation Key: neutral terms, grammar, free-text question scope; rules v0.4; flow unchanged (`CASCADE: ARCH_GAP`) | 2026-10-14 | `wbs:5.6`, `5.1` | **Answered by TAD rev 22 and SDD A-09 (2026-10-16); superseded by Iteration 9** — [jump to Iteration 8](#iteration-8--the-clients-anonymisation-key-2026-10-14) |
| 9 — the flow rebuilt to TAD rev 22: extractor labels, rewrite prompt, spelling prompt, checks P1/P2/P3; 313 → 90 actions; rules v0.5 | 2026-10-16 | `wbs:5.3`, `5.6`, `CO-009` (spelling) | **APPROVED 2026-10-16** (*"Approved"*, relayed by lead-agent); build held — [jump to Iteration 9](#iteration-9--the-flow-rebuilt-to-tad-rev-22-2026-10-16) |
| 10 — TAD rev 23 (`ADR-076`): the rewrite rules move to four `rev_setting` rows, which are also checks P2 and P3; create-only seed; 97 actions; rules v0.6; **the two prompts exported from DEV and copied in (`A-NS-31` closed)** | 2026-10-16 | `wbs:5.6`, `5.3` | **Awaiting code review** — [jump to Iteration 10](#iteration-10--the-rewrite-rules-move-to-settings-tad-rev-23-2026-10-16) |
| 11 — DEV synthetic run of 2026-10-19: a hyphenated surname fragment leaked; name spans widened and a P3 name-fragment check; *Dr* kept outside the label; name rules reordered with the writer's own name; a punctuation fidelity hold; rules v0.7; 100 actions | 2026-10-19 | `wbs:5.3`, `5.6` | **APPROVED 2026-10-19** (*"Approved to build."*, with Iteration 12) — [jump to Iteration 11](#iteration-11--name-fragments-name-rules-and-punctuation-2026-10-19) |
| 12 — TAD rev 25 (`ADR-078`): the flow never releases; every scrubbed record is flagged and carded; `RedactionAutoRelease` retired; threshold seeded create-only at 0.85; SDD A-11: the writer's own name does not count as another person; rules v0.8; 97 actions | 2026-10-19 | `wbs:5.3`, `5.4`, `5.6` | **APPROVED 2026-10-19** (*"Approved to build."*, with Iteration 11); **12.9 fix after the DEV designer refused to save: APPROVED 2026-10-20** (*"Approved"*) — [jump to Iteration 12](#iteration-12--the-process-owner-releases-every-record-tad-rev-25-2026-10-19) |
| 13 — TAD rev 29 (`ADR-075` item 2, "Decided: label"): a GP practice the extractor misses is labelled from its capitalised suffix; rules v0.9; 100 actions | 2026-10-20 | `wbs:5.3`, `5.6` | **Awaiting code review** — [jump to Iteration 13](#iteration-13--a-gp-practice-the-extractor-misses-is-labelled-tad-rev-29-2026-10-20) |
| 14 — TAD rev 30 (`ADR-082`): one extractor call per batch of columns, one prompt that rewrites and corrects spelling (declared near-spelling pairs), action ceiling 125; rules v1.0; 109 actions | 2026-10-21 | `wbs:5.3`, `5.6` | **Awaiting code review** — [jump to Iteration 14](#iteration-14--one-extractor-call-per-batch-one-prompt-for-rewrite-and-spelling-tad-rev-30-2026-10-21) |

> **Iteration 1 is kept as approved.** Where it says the flow and the `TD-008` columns are not built, Iteration 2
> below supersedes it: both are built.
>
> **Iterations 2 and 3 are kept as written.** Where Iteration 3 says the prompt run action and component are not built,
> Iteration 4 supersedes it: both are built, and the stage still ships off.
>
> **Iteration 2 is kept as written, with its flow links re-pointed to the current file.** Where it says the prompt stage is
> designed and not built, that `RedactionPromptCalibrated` means `true`, or that a postcode without its space only goes to
> review, Iteration 3 supersedes it.

# Iteration 1 — rules, corpus and review tab (2026-10-05, APPROVED 2026-10-06)

**WBS:** `wbs:5.1` (rules, done), `wbs:5.2` (corpus and harness done; live run pending), `wbs:5.4` (review tab only; partial), `wbs:5.3` (**not built**, CASCADE ARCH_GAP)
**Date:** 2026-10-05 · **Author:** development-agent (strategic tier, per dispatch) · **Items:** none carried

**Reviewer decisions this iteration implements:**

> *"Start with the PII data and the labels in the free text and make sure the logic is correct. Then we can add additonal fields based on additional information from Emily."* (Xander Lykopoulos, 2026-10-05)

> *"Right now the redacted narative columns are not visible on the application form. Maybe good to add those so that the grant admin can review and edit them accordingly. Maybe best to create a separate tab for that purpose called "narrative scrubbing" in which all the free text fields are shown in the left side of the section(s) and all the redacted text on the right side. The sections can be categorised to create groups of fields for ease of processing."* (Xander Lykopoulos, 2026-10-05, relayed mid-dispatch)

---

## 1. Implementation Summary

Three things are delivered:

- **The redaction rules, v0.1** ([`docs/development/revitalise-redaction-rules.md`](revitalise-redaction-rules.md)). They cover direct identifiers only, and indirect identifiers have a marked extension point. Their executable form is [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py).
- **A 20-sample synthetic corpus, 44 logic tests and a live-run scorer** for `wbs:5.2`.
- **A "Narrative Scrubbing" tab** on the Application main form, where the grant admin reviews and edits redactions side by side with the raw text (`wbs:5.4`, FR-030).

**The scrubbing flow (`wbs:5.3`) is not built.** Ground-truthing showed that the approved TAD's design does not fit the platform:
- The "AI Builder prebuilt PII model" it names does not exist in this tenant.
- The nearest prebuilt detects phone numbers and addresses only in US format.
- Power Automate cannot host the UK-format rules, because its expressions have no regular expressions.

That is an architecture decision, so it is raised as `CASCADE: ARCH_GAP` and not designed here. Ground-truthing also found that all three project environments are hosted in Switzerland, against NFR-009 ([IMP-1063](../../logs/improvement-log.jsonl)).

## 2. Components Changed / Created

| Component | Change | WBS |
|---|---|---|
| [`docs/development/revitalise-redaction-rules.md`](revitalise-redaction-rules.md) | New: rules v0.1 | 5.1 |
| [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py) | New: reference implementation (oracle) of the rules | 5.1, 5.2 |
| [`src/tests/narrative/test_redaction_reference.py`](../../src/tests/narrative/test_redaction_reference.py) | New: 44 tests | 5.2 |
| [`src/tests/narrative/corpus/narratives.json`](../../src/tests/narrative/corpus/narratives.json) | New: 20 synthetic narratives with gold spans and expected output | 5.2 |
| [`src/tests/narrative/score_live_run.py`](../../src/tests/narrative/score_live_run.py) | New: scores a live AI Builder run per category | 5.2 |
| [`src/tests/narrative/NarrativeRedaction.Tests.ps1`](../../src/tests/narrative/NarrativeRedaction.Tests.ps1) | New: Pester wrapper, so the suite runs in the HARD `unit-tests` step | 5.2 |
| `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/FormXml/main/{6a6004bd-…}.xml` | New tab `tab_narrativescrubbing`, after Casework | 5.4 |
| [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) | IMP-1063 to IMP-1069 | — |

## 3. Data Model Changes

**None.** In particular:

- **`IsSecured` is unchanged on every column.** The special-category register's exceptions block, which Automation #5 must re-read before touching any free-text column, was re-read. The raw columns stay in `REV_TrusteeRestricted`. **Proposed register note** (improvement-agent applies it, because `constraints/` is not this agent's to edit): *"2026-10-05, Automation #5 v0.1 (development-agent): IsSecured unchanged on every free-text column; trustees read only the …redacted counterparts, released per record."*
- **`TD-008` columns (`rev_redactionconfidence`, `rev_redactionreviewrequired`) are NOT built.** Their only writer is the `wbs:5.3` flow, which is held on the ARCH_GAP. Built now, they would be empty columns on a review tab that nothing fills. `TD-008`'s own clearing condition says they are built with the flow that writes them, and its expiry (2026-11-27) stands.

## 4. Automation / Workflow Changes

**No flow is created.** The flow's logic is fully specified and tested in the reference implementation. The stages are window, detect, refine, merge, replace from the end, plan the writes, and decide. `wbs:5.3` builds it once the detector-hosting decision is made (rules §9.1).

### The Narrative Scrubbing tab (`wbs:5.4`, FR-030)

The tab sits on the main form after Casework. Each two-column section (`columns="11"`, labels on top) has one row per pair: the **raw column on the left, read-only on this tab**, and its **redacted counterpart on the right, editable**.

| Section | Raw (left, read-only) → redacted (right, editable) |
|---|---|
| **Applicant's own account** | Narrative; Other condition notes; Disability impact description |
| **Person supported** | Other condition notes; Disability impact description |
| **Care and support** | Care support description; Care provided example; Other care provided |
| **Finance and exceptional circumstances** | Why unable to fund the break; Care or medical costs explanation; Exceptional funding detail; Other exceptional circumstance |
| **Review and release** | `rev_redactionreleased` (Redaction Released) |

Design notes:

- **All 12 pairs that exist are on the tab.** The brief said the TD-010 disability-impact pairs are unbuilt and should be left as follow-ups. They are built (both raw and redacted are in `Entity.xml`, and TD-010 is gone from `contract/tad-deferrals.json`), so they are included ([IMP-1068](../../logs/improvement-log.jsonl)).
- **"Benefit statement"** (the brief's example group) has no redacted counterpart. `rev_benefitprovider` is free text but secured without a counterpart, so it is not on this tab and is never trustee-visible. Giving it a counterpart is TAD schema work.
- **The raw columns already appear on other tabs**, editable. Each therefore gets a second control here, with id `<field>1` and `disabled="true"`. Read-only applies to this tab only (A-NS-6).
- **Labels are each column's own display name**, so the `shipped-content` label check holds without overrides.
- **Column security decides who sees the left side.** A user outside `REV_TrusteeRestricted` sees the raw controls withheld by the platform. The form adds no access.
- **Follow-ups once `TD-008` lands:** add `rev_redactionconfidence` and `rev_redactionreviewrequired` to *Review and release*, and a "Review Required" view (`wbs:5.4`'s other half).

### The correctness trap: a re-run must not overwrite the admin

The rule is in rules §7a and tested in `RerunNeverOverwritesAHuman` (5 tests; 2 mutations caught):
1. A **released** record is never touched.
2. Otherwise only an **empty** counterpart is written, so a correction always survives.
3. If any counterpart was kept, the flow **cannot release** the record (`kept-existing-counterpart`).
4. **Clearing a counterpart is how the admin asks for a re-scrub.**

A per-column "manually edited" marker was considered and rejected. It needs a column per pair, which is 12 new columns, or a JSON column. It also still leaves the flow unable to tell its own earlier output from an untouched default. Treating every existing value as human-owned needs no schema, and it fails in the safe direction.

## 5. Configuration & Provisioning Changes

None. No deployment settings, environment variables or provisioning scripts.

### Provisioning Scripts

None.

## 6. Security Controls Implemented

| Control | How |
|---|---|
| Raw text never reaches a trustee (FR-031, NFR-001) | Unchanged column security; the tab exposes nothing new to any role |
| Fail closed (NFR-018, TAD §5.5) | Every error, missing threshold, unknown type, over-length output, empty detection set and kept counterpart sends the record to review with `released = false` (rules §7; 13 decision tests) |
| No raw text in logs or notifications (NFR-012) | The decision object holds only flags, a score and fixed reason codes. A test checks every sample's decision against every word of its input |
| Threshold adjustable without redesign (NFR-017) | Read from `rev_setting` `RedactionConfidenceThreshold` at run time; tested with three values and no code change |
| Human correction preserved (FR-030) | Rules §7a, as above |

## 7. Known Limitations / Deferred Items

1. **`wbs:5.3` flow: not built.** `CASCADE: ARCH_GAP`. Detector hosting (rules §9.1: custom AI Builder entity extraction / plug-in / external service / 100% manual review), the 4,000-character counterparts against 1,048,576-character sources, and the TAD's non-existent prebuilt PII model ([IMP-1064](../../logs/improvement-log.jsonl)).
2. **Live AI Builder run (`wbs:5.2`): not run.** This session has read-only DEV access and no route to invoke a model. See REVIEWER ACTION REQUIRED in the gate output.
3. **NFR-009: all three environments are hosted in Switzerland (`crm17`).** [IMP-1063](../../logs/improvement-log.jsonl) is a governance-lane blocker. It needs a reviewer and DPO decision before production.
4. **`TD-008` columns, the "Review Required" view and the `rev_setting` threshold row:** built with `wbs:5.3`/`5.4`.
5. **Indirect identifiers:** after Emily's input (rules §10).
6. **The tab is not deployed.** Import is pipeline-agent's, and V4 (open and save in the designer) is still to do.

## 8. Build Instructions

This change **amends the existing `config/revitalise-grant-automation-build.yml`**, with the same CI slug. It does not need its own configuration: the tab is part of the `RevitaliseGrantAutomation` solution, and the new tests are picked up by the existing HARD `unit-tests` step (`src/tests/**/*.Tests.ps1`). **No step was added or changed.** `python3` must be on the runner's PATH, as it already is for every `scripts/verify-*.py` step. The pipeline declares the component as `deploy` (solution import); no `post_deploy` step is needed.

## 9. Test Guidance

- **Logic:** `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'` (44 tests).
- **Live run:** rules §11.4. Report recall per label, for the model alone and with the rules. Expect `[PHONE]` and `[ADDRESS]` to come from the rules, not the model.
- **Tab (V4):**
  1. Open an Application as the grant admin. The Narrative Scrubbing tab shows 4 paired sections plus Review and release.
  2. The left column is read-only and the right column is editable.
  3. Edit a redacted field, save and reopen: the edit persists.
  4. Open the same record as a user outside `REV_TrusteeRestricted`: the left side is withheld.
  5. Confirm the designer opens and saves the form without errors (A-NS-6, A-NS-7).

## 10. Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-1 | The prebuilt model returns `type` strings `PersonName`, `Organization`, `PhoneNumber`, `StreetAddress`, `ZipCode`, `Email`, `Age`, `City`, …; any other string forces review rather than being kept | `src/tests/narrative/redaction_reference.py` | E3 (docs show display names, examples `DateTime`/`Organization`) | No model invocation from this session | Live run of the corpus: `score_live_run.py` lists every type string returned; mapped ones redact, an unknown one shows **UNMAPPED** | OPEN |
| A-NS-2 | `startIndex`/`length` count UTF-16 code units, so an emoji before an entity shifts them by one per emoji | `src/tests/narrative/redaction_reference.py` | E4 | as A-NS-1 | Live run of S16: with `--offsets utf16` S16 matches, and with `codepoints` it does not | OPEN |
| A-NS-3 | Input above 5,000 characters is rejected (not silently truncated), so windowing is required | `src/tests/narrative/redaction_reference.py` | E2 (limit only; behaviour unstated) | as A-NS-1 | One call with 5,001 characters (error expected) and one with 5,000 (success expected) | OPEN |
| A-NS-4 | The prebuilt model does not detect UK phone numbers or UK addresses (documented US-format only), so the rules layer is required for `[PHONE]`/`[ADDRESS]` | `src/tests/narrative/redaction_reference.py` | E2 | as A-NS-1 | Live run: model-only recall for PHONE/ADDRESS on S01, S08, S09, S10; if near 100% the rule layer is redundant | OPEN |
| A-NS-5 | Language `en` is the right input for UK English narratives | `src/tests/narrative/score_live_run.py` | E2 ("English") | as A-NS-1 | Live run with `en`; one comparison run with `en-GB` if the action accepts it | OPEN |
| A-NS-6 | A second body control bound to a field already on the form is accepted with id `<field>1` and `disabled="true"`, and stays read-only on this tab only, with the first instance still editable | `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/FormXml/main/{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml` | E3 (designer convention); live system forms repeat ids instead (E1) | No import in this dispatch; 428 live main forms scanned, none with a `<field>1` duplicate | Import to DEV, then open in the designer, save, and re-export: the ids survive. On the form, the raw field is read-only on this tab and editable on Support Needs | OPEN |
| A-NS-7 | `columns="11"` with `celllabelposition="Top"` renders the pair side by side at full tab width | `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/FormXml/main/{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml` | E1 for each attribute separately (live system forms); not seen together | No import in this dispatch | V4: open the tab and check raw left, redacted right, labels above | OPEN |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Redaction logic (reference) | **Executed (unit)** | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: 44 OK. Six mutations each failed the suite (rules §11.3) |
| Pester wrapper | Executed | macOS, local | `Invoke-Pester -Path src/tests/narrative/NarrativeRedaction.Tests.ps1`: 2/2 passed |
| AI Builder contract | E1 read (schema only), **no V-level** | DEV, read-only | `pac env fetch` on `msdyn_aitemplate`, `msdyn_aimodel` and `msdyn_aiconfiguration`; the model was never invoked |
| Narrative Scrubbing tab | **V2** | macOS, local | `run-source-gates.py`: 19/19 PASS. `pac solution pack … --packagetype Unmanaged` completed, and the packed `customizations.xml` contains `tab_narrativescrubbing` and `rev_narrativeraw1 … disabled="true"` |
| Environment region | E1 (URL) + E2 (mapping) | tenant | `pac admin list`: DEV, ACC, PRD and the pipeline host are all `*.crm17.dynamics.com`; Microsoft datacenter-regions page: crm17 = CHE |

**V3, V4 and V5 are not reached for anything.** No import, no designer session, no flow run.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| Local `pac solution pack` (this dispatch) | pack-unmanaged | No warnings emitted | — |
| Standing warning, shared step `pack-managed` / `pack-unmanaged` | shared config | Accepted (unchanged) | Triaged at [revitalise-grant-automation-dev-summary.md#L7814](revitalise-grant-automation-dev-summary.md#L7814) |
| Standing warning, shared step `lint` | shared config | Accepted (unchanged) | Triaged at [revitalise-grant-automation-dev-summary.md#L10323](revitalise-grant-automation-dev-summary.md#L10323) |
| Standing warnings, `code-app-install`, `-cards`, `code-app-unit-tests` | shared config | Accepted (unchanged; this change touches no Code App) | Triaged at [revitalise-grant-automation-dev-summary.md#L4893](revitalise-grant-automation-dev-summary.md#L4893) |
| Standing warning, `code-app-audit` | shared config | Accepted (unchanged) | Triaged at [revitalise-grant-automation-dev-summary.md#L7521](revitalise-grant-automation-dev-summary.md#L7521) |
| Standing warnings, `code-app-unit-tests-cards`, `code-app-build`, `code-app-build-cards` | shared config | Accepted (unchanged) | Triaged at [trustee-portal-design-2-dev-summary.md#L487](trustee-portal-design-2-dev-summary.md#L487), [#L490](trustee-portal-design-2-dev-summary.md#L490), [#L484](trustee-portal-design-2-dev-summary.md#L484) |

### Diagnostic components created and removed (C-TECH-056)

None. Every live call was a read (`pac env fetch`, `pac admin list`, `pac env list`, `pac org who`). The packed zip was written to the session scratch directory, outside the repository.

## 12. Work Items — close-out record (C-TECH-079)

No items carried.

### Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.1 | 3.25 h | Rules document; platform ground truth (AI Builder catalogue, region) |
| 5.2 | 2.75 h | Corpus, 44 tests, scorer, wrapper. The live run is still to come and is not in this figure |
| 5.4 | 1.25 h | Narrative Scrubbing tab; re-run rule and its tests. The "Review Required" view and flagging are still to come |
| system | 0.5 h | Seven findings (IMP-1063 to IMP-1069) |

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1063 | `stale-claim-contradicting-rechecked-source` | blocker (governance lane) | All three REV environments are on crm17 (CHE). NFR-009 requires GBR (crm11). Measure residency; do not assume it |
| IMP-1064 | `platform-contract-guessed-not-groundtruthed` | rework | AI Builder has no prebuilt PII model here. The prebuilt entity extractor is US-format only for phone and address, and takes at most 5,000 characters |
| IMP-1065 | `capability-established` | friction | The AI Builder catalogue and IO schema, and live FormXml shapes, are E1-readable through `pac env fetch` |
| IMP-1066 | `tad-narrative-omits-an-already-existing-column` | friction | There are 12 raw/redacted pairs on rev_application, and TAD §3.1 lists 11. Derive the scope from Entity.xml |
| IMP-1067 | `wrong-artefact-cited-as-evidence` | friction | evidence-map says REVAnonymise; the TAD says REV \| Narrative \| Scrub Free-Text |
| IMP-1068 | `dispatch-brief-asserts-unverified-fact` | friction | The TD-010 disability-impact pairs are built; the TAD and the brief say they are not |
| IMP-1069 | `stale-claim-contradicting-rechecked-source` | friction | rev_agerange's shipped description still says the band comes from date of birth |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist
- [x] All FR IDs covered — FR-026, FR-027 (ages; places by D-1), FR-028, FR-029, FR-030 (review tab and re-run rule), FR-031, FR-079 in the rules. Flow-side coverage waits for `wbs:5.3`
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — column security unchanged
- [x] Every TAD §12 item has an idempotent provisioning script — n/a, no provisioning
- [x] Role assignments via group teams only — n/a
- [x] No hardcoded environment-specific IDs/URLs — none in source
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source
- [x] Where an environment existed, ground truth was used instead of a guess (AI Builder catalogue, live FormXml)
- [x] Every platform limit the packer does not enforce has a build gate — the 5,000-character input and 4,000-character counterpart limits are enforced by the reference tests; the flow inherits them in `wbs:5.3`
- [x] Verification levels in §11 are the levels actually executed
- [x] Scripts run on the CI runner's OS — Python stdlib and Pester only
- [x] Every tool warning triaged in §11; no diagnostic components left
- [ ] Accessibility requirements met — model-driven form; checked at V4
- [x] No dead code or debug statements
- [x] Unit tests written
- [x] Every carried work item is built or deferred — none carried

## Approval (Iteration 1)
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-06  **Response:** *"Approved development work"* (logged in `logs/routing.log`, 2026-10-06 09:00)

---

# Iteration 2 — the scrubbing flow (2026-10-06)

**WBS:** `wbs:5.3` (the flow), `wbs:5.4` (the `TD-008` columns, the review section, the Review Required view, the
process-owner message), `wbs:5.1` (rules v0.2) · **Date:** 2026-10-06 · **Author:** development-agent, strategic tier
(dispatch: *"a custom security control over Art. 9 free text and introduces a new integration pattern"*) · **Status:** DRAFT
· **Items:** none carried

**Reviewer decisions this iteration implements** (Xander Lykopoulos, 2026-10-06, verbatim, `logs/routing.log`):

> *"Approve architecture"* — TAD rev 19, including the acknowledgement of the carried SOFT `C-DOM-005`.
> *"Agreed"* — rules D-1, D-2 and D-3 accepted as drafted; D-4 (NHS numbers, National Insurance numbers, dates of birth)
> referred to Emily.

**Held to the dispatch's limits:** nothing under `src/code-apps/` is touched; the generative prompt stage is designed and
**not built**, so it cannot run; no environment setting is read or written, so *Move data across regions* stays as it is;
residency (`IMP-1063`) is not decided here.

## 2.1 Implementation Summary

- **`REV | Narrative | Scrub Free-Text` is built**, as TAD rev 19 §5.5 and `ADR-071` describe
  ([flow](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json),
  [design notes](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md)).
  When an application becomes Eligible for Panel it scrubs all twelve free-text columns into their redacted counterparts,
  then decides once per record whether it may be released. With no settings seeded, every record is held for the process
  owner, which is the intended state until `wbs:5.7`.
- **The detection runs without regular expressions.** The AI Builder entity extractor finds names, organisations, streets,
  emails and ages. The flow itself finds UK phones and postcodes by their shape, turns a name next to a kinship word into
  `[FAMILY MEMBER]` and an organisation ending in a practice word into `[GP PRACTICE]`, and checks what it is about to write
  for anything a detector missed.
- **The flow was executed before it exists anywhere.** Its shipped JSON runs in a small simulator over the 20-sample corpus
  and every fail-closed path, and agrees with the Python flow model on every write, reason and score. Ten deliberate
  breakages of the JSON were each caught.
- **`TD-008` is built and deleted**: `rev_redactionconfidence` and `rev_redactionreviewrequired` exist, sit read-only in the
  tab's *Review and release* section, and drive a new **Review Required** view, linked from the app's navigation and from
  the flow's Teams message.
- **The rules are v0.2**: D-1 to D-4 recorded, the shapes, residue checks and in-flow refinement written down, the five new
  reason codes and the four settings documented ([rules](revitalise-redaction-rules.md)).

## 2.2 Components Changed / Created

| Component | Type | Change | FR / WBS |
|---|---|---|---|
| [`Workflows/REVNarrativeScrubFreeText-…-1011-….json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json) | Cloud flow (new) | 209 actions; Dataverse row trigger on `rev_status`; off at import like every flow here | FR-026–FR-031, FR-079 · 5.3, 5.4 |
| [`….json.data.xml`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json.data.xml), [`….notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md) | Flow metadata, design notes (new) | Same shape as `REVSafeguardingActionCompletion` | 5.3 |
| [`Other/Solution.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L283) | Root component | The flow added | 5.3 |
| [`Entities/rev_application/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L2154) | Two columns (new) | `rev_redactionconfidence` (Decimal 0–1, 4 places), `rev_redactionreviewrequired` (Yes/No) | FR-029, FR-030 · 5.4 |
| `Entities/rev_application/Entity.xml` | 13 descriptions corrected | The counterparts said their writer was deferred and that *"nothing has written to it yet"*; `rev_narrativeredacted` said its length matched the raw column's (4,000 against 1,048,576) | — |
| [`Entities/rev_application/SavedQueries/RedactionReviewRequired.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/SavedQueries/RedactionReviewRequired.xml) | View (new) | *Review Required*: review required and not released | FR-030 · 5.4 |
| [`AppModuleSiteMap.xml`](../../src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml#L189) | Navigation | *Redaction - Review Required* | 5.4 |
| `FormXml/main/{6a6004bd-…}.xml` | Form | *Review and release* gains both new columns, read-only | 5.4 |
| [`config/attribute-type-lock.json`](../../config/attribute-type-lock.json#L115) | Gate input | Both new columns' types locked | — |
| [`contract/tad-deferrals.json`](../../contract/tad-deferrals.json#L30) | Gate input | `TD-008` deleted on its own clearing condition | — |
| [`docs/development/cards/redaction-review-card.json`](cards/redaction-review-card.json) | Readable card | The Teams card, byte-equal to what ships | 5.4 |
| [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py#L478) | Oracle | *FLOW MODEL* section: the flow, step for step, in Python | 5.3 |
| [`test_flow_model.py`](../../src/tests/narrative/test_flow_model.py) | Tests (new, 43) | The model against the corpus: shapes, residue, refinement, merge, decision, prompt validation | 5.3 |
| [`wdl_sim.py`](../../src/tests/narrative/wdl_sim.py), [`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py) | Simulator, tests (new, 29) | Executes the shipped JSON and compares it with the model | 5.3 |
| [`score_live_run.py`](../../src/tests/narrative/score_live_run.py) | Scorer | Third layer: the model plus the flow, which is what production runs | 5.2 |
| [`docs/development/revitalise-redaction-rules.md`](revitalise-redaction-rules.md) | Rules v0.2 | Sections 4.4, 6a–6c, 7, 7b, 9, 11, 12 | 5.1 |

## 2.3 Data Model Changes

Two columns on `rev_application`, both on the TAD §3.1 rows that `TD-008` deferred, both created by the existing
`ensure-schema.ps1` from `Entity.xml` (its `decimal` and `bit` branches), neither secured, both audited:

| Column | Type | Written by | Read by |
|---|---|---|---|
| `rev_redactionconfidence` | Decimal, 4 places, 0 to 1 | the flow: the lowest extractor score of any span it redacted; empty when there is none | the tab, the view |
| `rev_redactionreviewrequired` | Yes/No, default No | the flow: Yes whenever the record has any reason to review, and on any failure | the view |

**Column security is unchanged** on every free-text column. **Proposed register note** for
`constraints/domain/special-category-register.yml` (improvement-agent applies it; `constraints/` is not this agent's):
*"2026-10-06, Automation #5 iteration 2 (development-agent): IsSecured unchanged on every free-text column; the scrub
flow reads them through a secured row read and writes only the ...redacted counterparts."* Neither new column is
special-category data, so neither needs a register row.

## 2.4 Automation / Workflow Changes

The stage map, and the reason for every shape, is in the [design notes](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md). In short:

1. **Only status 6 runs it** ([`Stop_unless_eligible_for_panel`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L82)); a released record is never touched ([`Stop_if_already_released`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L424)).
2. **The four settings are read once, and absent is safe** ([`Read_redaction_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L455)). None is seeded.
3. **Per column**: skip an empty one; keep a non-empty counterpart and add `kept-existing-counterpart` ([`Keep_or_scrub_the_column`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2069)); otherwise scan it in windows of at most 5,000 characters ([`Scan_the_column_in_windows`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2152)).
4. **Per window**: the extractor ([`Extract_entities_from_the_window`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2195)), name refinement ([`Refine_each_name`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2467)), and the shapes ([`Detect_shapes_in_the_window`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2604)). A failed call, or an answer with no entity array, is `ai-error` for the column, never *no entities*.
5. **Merge, rebuild, check, write**: one sequential pass over the spans sorted by offset ([`Merge_each_span`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3480)), one `Select` to rebuild, the residue checks on a label-free skeleton ([`Compose_residue_reasons`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3966)), then one write per counterpart if it fits 4,000 characters ([`Write_the_counterpart`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L4016)).
6. **Decide once** ([`Compose_decision`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L4537)), write the flag, the review flag and the score ([`Write_the_decision`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L4551)), and post the reference and reason codes to the process owner when the record is held.
7. **Any failure** holds the record for review ([`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5636)) and alerts with the failed action's name and error code, never the platform's message.

**The prompt stage (`ADR-072`) is designed, not built.** Its AI model is a solution component whose shape must be copied
from a DEV export first (`A-NS-9`), and this session cannot write to DEV. The seam is in place (every detector appends to
one span array), the validation rule is in the reference and tested (`validate_prompt_items`), and if anyone sets
`RedactionPromptStage` to `on` the flow adds `prompt-error:<column>` and holds the record (`Note_the_prompt_stage` (removed in Iteration 3)).

**To scrub a column again**, the grant admin clears its counterpart and resubmits the flow's latest run. The flow re-reads
the row.

## 2.5 Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `rev_setting` `RedactionConfidenceThreshold`, `RedactionAutoRelease`, `RedactionPromptStage`, `RedactionPromptCalibrated` | all | **None seeded, deliberately.** Absent is the safe value for all four (rules §7). `wbs:5.7` sets the first two after calibration; the last two wait for the residency decision. **Rewritten by Iteration 3 §3.5 (TAD rev 20, `ADR-074`):** eight more keys, `RedactionPromptCalibrated` now holds a label list rather than `true`, and an edit to any `Redaction*` row stops auto-release |
| `rev_ProcessOwnerUpn`, `rev_GrantAdminAppUrl` | all | Existing environment variables, reused |
| Connection references `rev_SharedDataverse`, `rev_SharedTeams` | all | Existing. The AI Builder action runs on the Dataverse connector, so no new connector or DLP change (`A-NS-13`) |

### Provisioning Scripts

None new. `ensure-schema.ps1` creates the two columns from `Entity.xml` on its next run, before the import, as it does for
every column. The flow imports switched off and is bound and switched on by a person (TAD §12.1), like every flow here.

## 2.6 Security Controls Implemented

| Control | How | Proven by |
|---|---|---|
| Raw text never reaches a trustee (FR-031, NFR-001) | Column security unchanged; the flow writes only counterparts; trustees see counterparts only once released | Unchanged security model |
| Nothing is released without the process owner until calibration (`ADR-071` item 8) | `auto-release-off` unless `RedactionAutoRelease` is `true` | `test_absent_settings_hold_every_record` |
| Fail closed on every path (NFR-018) | ai-error, unreadable answer, incomplete scan, over-length, unmapped type, kept counterpart, residue, missing threshold, prompt on: all hold the record; a run failure holds it too | `FailClosedPaths` (18 tests) |
| No text in run history, variables, notifications or the alert (`C-DOM-004`, NFR-012) | `secureData` on the trigger, the row read, the extractor call and every text-bearing `Compose`, `Select` and `Filter`; variables hold offsets, codes, scores and fixed reason codes only | `RunHistoryAndVariables`: a made-up word in the narrative appears in no variable, no unsecured action input or output, no message |
| A human correction survives a re-run (rules §7a) | Released rows untouched; a non-empty counterpart is neither scanned nor written | `test_released_record_is_never_touched`, `test_kept_counterpart_is_not_rewritten_and_not_scanned` |
| Prompt injection cannot add text (`ADR-072` item 7) | Stage not built; its validation keeps the label from the flow's map and every other character from the source | `PromptValidation` |

## 2.7 Known Limitations / Deferred Items

1. **Nothing is deployed, and the flow has never run on the platform.** Import is pipeline-agent's; binding and switching it
   on is a person's (TAD §12.1).
2. **The AI Builder action's shape is a guess** (`A-NS-13`, `A-NS-16`): no flow in DEV uses an AI Builder action
   (`workflow.clientdata` searched 2026-10-06), and this session cannot create one. If either guess is wrong the flow
   holds every record with `ai-error`; it cannot release anything on a wrong guess.
3. **The live corpus run (`wbs:5.2`) is still not run.** The scorer now reports the flow's layer too.
4. **The prompt stage (`ADR-072`)** waits for its AI model to be created in DEV and for the residency decision.
5. **D-4 is open with Emily.** Until she answers, NHS and National Insurance numbers and dates of birth are not labelled; an
   NHS number (ten digits) still trips `residual-digit-run`.
6. **Over-triggering is measured, not tuned**: 1 of 20 correct outputs trips a residue check (S04, *"will drive us"*).
   `wbs:5.6`/`5.7` tune it.
7. **A failure inside the column loop may be named only by its wrapper in the alert** when a later column succeeds
   (`A-NS-19`). The alert's run link still reaches the failed action.
8. **`contract/evidence-map.json` still names the flow `REVAnonymise`** (`IMP-1067`); its owner corrects it.

## 2.8 Build Instructions

**This amends the existing `config/revitalise-grant-automation-build.yml` (same CI slug); no step is added or changed.**
The flow, columns, view, form and sitemap are part of the `RevitaliseGrantAutomation` solution and are covered by the steps
already wired over it. The 72 new tests run inside the HARD `unit-tests` step through
`src/tests/narrative/NarrativeRedaction.Tests.ps1`, which discovers every `test_*.py`. The platform limits the packer does
not enforce (expression length 8,192, nesting depth 8, 500 actions per flow) are asserted for **every** flow in the solution
by `PlatformLimits`, and the 256-character description limit by the existing `field-length-limits` step. The pipeline needs
no new step: `ensure-schema` already runs before the import.

### Warnings this feature's build will show (shared configuration)

| Warning | Step | Triaged at |
|---|---|---|
| `pac solution pack`: *"Following root components are not defined in customizations"* (entity relationships and environment variable definitions) — re-observed in this dispatch's local pack | `pack-managed`, `pack-unmanaged` | [revitalise-grant-automation-dev-summary.md#L1677](revitalise-grant-automation-dev-summary.md#L1677) |
| Standing warning, `lint` | `lint` | [revitalise-grant-automation-dev-summary.md#L10323](revitalise-grant-automation-dev-summary.md#L10323) |
| Standing warnings, `code-app-install`, `-cards`, `code-app-unit-tests` | shared | [revitalise-grant-automation-dev-summary.md#L4893](revitalise-grant-automation-dev-summary.md#L4893) |
| Standing warning, `code-app-audit` — **currently a failure, not a warning** (`IMP-1072`, new advisories against an unchanged lockfile) | `code-app-audit` | Out of this dispatch's scope by instruction; handled separately with the reviewer |
| Standing warnings, `code-app-unit-tests-cards`, `code-app-build`, `code-app-build-cards` | shared | [trustee-portal-design-2-dev-summary.md#L487](trustee-portal-design-2-dev-summary.md#L487), [#L490](trustee-portal-design-2-dev-summary.md#L490), [#L484](trustee-portal-design-2-dev-summary.md#L484) |

## 2.9 Test Guidance

- **Logic and definition:** `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'` — 116 tests.
- **What the simulator does not prove:** the AI Builder action's real shape and output (`A-NS-13`, `A-NS-16`), `sort()`
  (`A-NS-15`), the platform's string functions (`A-NS-18`), and anything about run time. It proves the JSON's logic under
  the strictest reading of each uncertain semantic.
- **First DEV run (after import, bind, switch on):** set one test application's status to Eligible for Panel with corpus
  sample S08 in the narrative. Expect `rev_narrativeredacted` = *"We live at [ADDRESS] in a ground floor flat with a ramp."*
  only if the extractor returns *14 Elm Road, Leeds* as a street; otherwise `residual-street-word` and the record held. Either
  way: `rev_redactionreleased` = No, `rev_redactionreviewrequired` = Yes, reasons including `threshold-missing-or-invalid`
  and `auto-release-off`, one Teams card to the process owner, and the run history showing no narrative text in any pane.
- **Then:** an application with a non-empty counterpart (kept, not rewritten); a released one (one read, nothing written);
  `RedactionPromptStage` = `on` (`prompt-error`, held).
- **V4:** open the Application form's Narrative Scrubbing tab, confirm the two new read-only fields, save; open *Redaction -
  Review Required* from the navigation.

## 2.10 Unvalidated Assumptions Register (C-TECH-052)

Rows for ids already in Iteration 1's register restate them with this iteration's source location; the rest are new. The
TAD's own verification plan (§12.6) names `A-NS-8` to `A-NS-14`; `A-NS-8`, `A-NS-10`, `A-NS-11` and `A-NS-14` concern the
prompt stage, which is not built, so they guard nothing in source yet and are not rows here.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-1 | The extractor's `type` strings are the PascalCase names in `Compose_extractor_type_codes`; a string not in the map makes the record `unmapped-entity-type` rather than being kept | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No model invocation from this session | Live corpus run: `score_live_run.py` lists every type string; a mapped one redacts, an unknown one shows UNMAPPED and the flow holds the record | OPEN |
| A-NS-2 | `startIndex`/`length` count the same units as `substring()` (UTF-16), so a span after an emoji lands on the right characters, and text without one is unaffected | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E4 | as A-NS-1 | DEV run of S16: *"Feeling 😊 since [FAMILY MEMBER], my wife,…"*; and S02 (no emoji) exact | OPEN |
| A-NS-3 | A call with more than 5,000 characters is rejected, so the windows are needed; one of exactly 5,000 succeeds | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (limit only) | as A-NS-1 | One DEV call with 5,001 characters (error) and one with 5,000 (success) | OPEN |
| A-NS-5 | Language `en` is right for UK English narratives | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 | as A-NS-1 | Live corpus run with `en` | OPEN |
| A-NS-9 | The prompt's AI model exports, packs and imports as a solution component; until its shape is copied from DEV the stage is not built, and switching it on holds every record | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No DEV write in this session | Maker creates the prompt in DEV inside the solution; export and unpack; copy the component (TAD §12.6) | OPEN |
| A-NS-12 | `secureData` on the extractor action hides its inputs and outputs in run history and does not stop the call running | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (E1 for `Select` and Dataverse actions here) | No run | One DEV run: the action succeeds, and its run-history panes show *secured* to a maker | OPEN |
| A-NS-13 | The action is `aibuilderpredict_entityextraction` on the Dataverse connector with parameters `item/requestv2/text` and `item/requestv2/language`; if wrong, the call fails and the column is `ai-error`, never released | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E4 (no flow in DEV uses an AI Builder action: `workflow.clientdata` searched 2026-10-06) | No DEV write in this session | Maker adds *Extract entities from text with the standard model* to a DEV test flow, saves, exports; diff the action with this one | OPEN |
| A-NS-15 | `sort(variables('spans'), 'start')` exists in Power Automate and sorts ascending by the number in `start`; spans out of order would merge wrongly | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (workflow definition language reference) | No run | One DEV test `Compose` over `[{start:10},{start:2},{start:7}]`: 2, 7, 10 | OPEN |
| A-NS-16 | The entity array is at `body/responsev2/predictionOutput/results` (or `…/result/entities`), and when it is at neither the flow reads null and makes the column `ai-error` rather than *no entities* | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E4 | as A-NS-13 | The same DEV test run: read the action's output body; then the first real run of S01 writes *[NAME]* and *[PHONE]* | OPEN |
| A-NS-17 | The Decimal control classid `{C3EBB6DA-…}` on `rev_redactionconfidence` renders a numeric field and the form saves | `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/FormXml/main/{6a6004bd-bba9-498b-8ca4-fafdd254bded}.xml` | E1 that DEV stores it (rev_payment and rev_roundfinance forms, read 2026-10-06); E3 that it renders | No import in this dispatch | V4: open the tab, see a number field, save | OPEN |
| A-NS-18 | `take()` on a string returns its first n characters (all of it when shorter), and `lastIndexOf()` returns -1 when the space is absent and for an empty string; otherwise the window step fails and the run is held | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 | No run | One DEV test `Compose`: `take('abcde', 3)`, `take('ab', 3)`, `lastIndexOf('abc', ' ')`, `lastIndexOf('', ' ')` | OPEN |
| A-NS-19 | `result()` of the column loop still lists a failed iteration after later ones succeed, so the alert names the failed action; when it does not, the alert names a wrapper and the run link is the route | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E4 | No run | In DEV, make the first column's write fail and a later one succeed; read the alert's action name | OPEN |

## 2.11 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic | **V1, and executed in a simulator** — not a V-level on the platform | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: 116 OK. The shipped JSON agrees with the model on all 20 samples alone and spread over the twelve columns, under case-sensitive and case-insensitive string functions, with `if()` evaluating both branches |
| Proof the tests can fail | — | macOS, local | 10 of 10 mutations of the flow JSON and 8 of 8 mutations of the model each failed the suite (rules §11.3) |
| Solution with the flow, columns, view, form, sitemap | **V2** | macOS, local | `run-source-gates.py`: 19/19 PASS. `verify-tad-coverage.py`: OK. `pac solution pack --packagetype Unmanaged`: complete; the packed zip holds the flow, both columns and the view |
| Pester wrapper | Executed | macOS, local | `Invoke-Pester src/tests/narrative/NarrativeRedaction.Tests.ps1`: 2/2 |
| AI Builder action shape | **No level** | DEV, read-only | `pac env fetch` over `workflow.clientdata LIKE '%aibuilderpredict%'`: no rows. Both models (`EntityExtraction`, `GptPromptEngineering`) confirmed present and managed |

**V3, V4 and V5 are not reached for anything.**

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| *"Following root components are not defined in customizations"* (local `pac solution pack`, this dispatch) | pack-unmanaged | Accepted (unchanged) | Standing; triaged at [revitalise-grant-automation-dev-summary.md#L1677](revitalise-grant-automation-dev-summary.md#L1677). This change adds no relationship or environment variable |
| Shared-step warnings | shared config | Accepted (unchanged) | See §2.8 |

### Diagnostic components created and removed (C-TECH-056)

None. Every live call was a read (`pac env fetch` on `workflow`, `msdyn_aitemplate`, `msdyn_aimodel`, `systemform`). The
packed zip was written to the session scratch directory.

## 2.12 Work Items — close-out record (C-TECH-079)

No items carried.

### Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 5.5 h | The flow (209 actions), its notes, the flow model, the simulator and 72 tests |
| 5.4 | 1.5 h | Two columns, form section, view, navigation, decision write, the Teams card |
| 5.1 | 0.5 h | Rules v0.2: D-1 to D-4 recorded, sections 4.4, 6a–6c, 7, 7b, 9 |
| system | 0.25 h | Three findings |

---

## Findings Logged (Iteration 2)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1073 | `capability-established` | friction | A hand-authored flow can be executed locally from its JSON with `wdl_sim.py` and compared with an oracle, before any environment exists |
| IMP-1074 | `gate-fired` | friction | Inside a loop, `result()` descent may not reach the failed leaf when a later iteration succeeds; keep the run link in the alert |
| IMP-1075 | `stale-claim-contradicting-rechecked-source` | friction | When a column's writer lands, correct its shipped description in the same change; a stated MaxLength must match the attribute's own |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist (Iteration 2)
- [x] All FR IDs covered — FR-026, FR-027, FR-028, FR-029, FR-030, FR-031, FR-079 in the flow; FR-027's place half deferred by D-1
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — column security unchanged; run history secured and tested
- [x] Every TAD §12 item has an idempotent provisioning script — no new item; the columns go through `ensure-schema.ps1`
- [x] Role assignments via group teams only — n/a
- [x] No hardcoded environment-specific IDs/URLs — environment variables; the view id is a solution component id
- [x] Every guessed platform contract is in §2.10 **and** commented `A-nnn` in source
- [x] Where an environment existed, ground truth was used instead of a guess — DEV searched for an AI Builder action; none exists, so `A-NS-13`/`A-NS-16` stay open with a reviewer action
- [x] Every platform limit the packer does not enforce has a build gate — `PlatformLimits` over every flow, inside `unit-tests`
- [x] Verification levels in §2.11 are the levels actually executed
- [x] Scripts run on the CI runner's OS — Python stdlib only
- [x] Every tool warning triaged in §2.11; no diagnostic components left
- [ ] Accessibility requirements met — model-driven form and view; checked at V4
- [x] No dead code or debug statements
- [x] Unit tests written
- [x] Every carried work item is built or deferred — none carried

## Approval (Iteration 2)
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`

---

# Iteration 3 — register, settings and the prompt stage (2026-10-06)

**WBS:** `wbs:5.3` (register, settings reads, prompt stage), `wbs:5.6` (the settings the process owner tunes after Emily's
review), `wbs:5.4` (new reasons in the review list) · **Date:** 2026-10-06 · **Author:** development-agent, strategic tier
(dispatch: *"custom privacy control over special-category data"*) · **Status:** DRAFT · **Items:** none carried

**Reviewer decision this iteration implements** (Xander Lykopoulos, 2026-10-06, verbatim, `logs/routing.log` 15:25):

> *"Data residency question is parked at customer. But, this doesn't have to block build. The outcome of that question is not
> effecting what we need to build. It will effect the location of the environments. So proceed with building the end-to-end
> flow with extractor and prompt + checks as currently designed. That design is defensible for being thorough with the
> narrative scrubbing."*

Recorded as approval of TAD rev 20 (`ADR-073`, `ADR-074` Accepted). **No residency decision exists**, so the prompt stage
ships off and *Move data across regions* is not touched. Nothing under `src/code-apps/` was touched (a sibling dispatch owns it).

## 3.1 Implementation Summary

- **The postcode register is in the flow** ([`List_postcode_districts`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1897), [`Select_register_candidates`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2792)).
  It is read once per run. "LS62AB" is now replaced, where before it only went to review. "We are in LS6 area" is replaced,
  while "the M62" and "vitamin B12" stay as written and send the record to review. A missing register fails closed.
- **The redaction settings are data-driven, with guard rails** ([`Read_redaction_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L455), [`Compose_word_lists`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1881)).
  The process owner can add kinship words, practice suffixes, street words and practice words without a deploy, and cannot
  remove the tested ones. A malformed row is ignored as a whole and named in the review reasons. Any edit to a redaction
  setting stops auto-release until she confirms again. **No setting row is seeded.**
- **The prompt stage is built up to the line in TAD §12.6.1** ([`Use_the_prompt_on_the_window`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2872)).
  Its inputs come from the category rows, and every answer is validated before use. Malformed, unusable or partly wrong
  answers fail closed. What is missing is the one action that calls the prompt, because the prompt must first be created in
  DEV by a person (R1). Until then, switching the stage on gives `prompt-error` on every column.
- **Everything was executed before it exists anywhere.** The shipped JSON runs in the simulator against the model over the
  TAD's postcode and settings tables row by row, 8 new corpus samples and 23 shapes of prompt answer, under both string
  semantics. 20 deliberate breakages of the JSON and 6 of the model were each caught (rules §11.3).

## 3.2 Components Changed / Created

| Component | Type | Change | FR / WBS |
|---|---|---|---|
| [`Workflows/REVNarrativeScrubFreeText-…-1011-….json`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json) | Cloud flow | 209 → 303 actions: settings with save times, word lists, register, register shapes, district residue, prompt stage and validation, failure descent regenerated | FR-026–FR-031, NFR-017, NFR-019 · 5.3, 5.6 |
| [`….notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md) | Design notes | Rewritten for rev 20, including the seam and the depth limit | 5.3 |
| `….json.data.xml` | Flow metadata | Comment only: TAD rev 20 | — |
| [`docs/development/revitalise-redaction-prompt.md`](revitalise-redaction-prompt.md) | New | The fixed prompt template, R0/R1/R5 steps, synthetic category texts | 5.3 |
| [`docs/development/revitalise-redaction-rules.md`](revitalise-redaction-rules.md) | Rules v0.3 | §6a.1 register, §6b district, §7 settings and reasons rewritten per `ADR-074`, §7b, §7c, §11 | 5.1, 5.6 |
| [`src/tests/narrative/redaction_reference.py`](../../src/tests/narrative/redaction_reference.py) | Oracle | Rev 20 sections: register, settings, word lists, guard rails, prompt stage | 5.3 |
| [`test_flow_model.py`](../../src/tests/narrative/test_flow_model.py) | Tests | 43 → 80 | 5.3 |
| [`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py) | Tests | 29 → 49, including the prompt stand-in splice | 5.3 |
| [`wdl_sim.py`](../../src/tests/narrative/wdl_sim.py) | Simulator | `toUpper()`, `ticks()` | — |
| [`corpus/narratives.json`](../../src/tests/narrative/corpus/narratives.json) | Corpus | `samples_rev20`: 8 synthetic postcode samples | 5.2 |
| [`score_live_run.py`](../../src/tests/narrative/score_live_run.py) | Scorer | The flow layer uses the seed register | 5.2 |

## 3.3 Data Model Changes

**None.** No column, view, form or role changes. The flow reads two existing tables through privileges the service role
already holds: `REV Service Automation` has Global read on the register ([line 221](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L221))
and on settings ([line 233](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Service%20Automation/REV%20Service%20Automation.xml#L233)).
`IsSecured` is unchanged on every free-text column, so no special-category register row is proposed.

## 3.4 Automation / Workflow Changes

The stage map, and the reason for every shape, is in the [design notes](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md). In short:

1. **Settings are read once, every row, and filtered in the flow** ([`Filter_redaction_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L481)). Each row's save time is read with `ticks()`; a row without one fails the run, which holds the record. Auto-release is `on` only when its row says `true` and was saved last ([`Compose_auto_release`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L609)).
2. **Word lists are floor plus valid additions** ([`Compose_word_list_checks`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1827)). The practice-suffix list can now grow because the GP check is an entity × suffix cross product ([`Select_practice_suffix_trials`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2329)) rather than a fixed chain of `endsWith`.
3. **The register is read once and joined into one string** ([`Compose_postcode_register`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1947)); a failed read is handled, not a failed run. Per window, candidates are tried against the register shapes ([`Select_register_trials`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2746)). After the rebuild, a confirmed district left in the text is a reason ([`Select_residue_district_positions`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3903)).
4. **The prompt stage runs per window only when on and configured** ([`Compose_prompt_runs`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L770)). It builds the three inputs ([`Compose_prompt_request`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2891)), reads the answer from the seam ([`Compose_prompt_answer`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2908), empty in this build), and validates it in a Scope whose failure means invalid ([`Validate_the_prompt_answer`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2989)). The column takes the prompt spans only if every window's answer was usable and valid ([`Compose_spans_with_prompt`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3400)).
5. **The decision gains four record reasons** ([`Compose_record_reasons`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L4503)): `auto-release-stale`, `prompt-config-invalid`, `postcode-register-unavailable`, `redaction-setting-invalid:<key>`; and one column reason, `residual-district`.

**Three deviations from the TAD's wording, each in the fail-closed direction or neutral, each tested:**

- **Occurrences of a prompt quote are found with `split()` and `join()`, not `nthIndexOf()`.** No flow here uses
  `nthIndexOf()`, so its TAD row `A-NS-11` would have stayed unverifiable. `split()` is already used in this flow. Its
  semantics are pinned as `A-NS-24`, and the model uses the same left-to-right, non-overlapping rule.
- **A word-list line must also contain a letter.** Otherwise `--` passes `ADR-074` item 4's character rule and becomes an
  entry that matches everywhere.
- **Prompt categories are sorted by label in the flow (`sort()`), not by `$orderby`.** No flow here uses `$orderby` on
  *List rows*, and `sort()` is already in use (`A-NS-15`).

**One Iteration 2 defect fixed.** The Iteration 2 flow added `prompt-error` to a column whose extractor had failed, where the
model said `ai-error` only. No test combined the two. The prompt reason now sits inside the column's success branch, and
`PromptStage.test_an_extractor_failure_column_has_no_prompt_reason` pins it.

**The flow is at the platform's nesting limit of 8.** The validation Scope sits at depth 8. The R1 change adds a leaf action,
not a container, so it fits. Any further container inside the prompt stage fails `PlatformLimits`.

## 3.5 Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `RedactionPromptCategory.Name`, `.FamilyMember`, `.GpPractice`, `.Address`, `RedactionKinshipWordsExtra`, `RedactionPracticeSuffixesExtra`, `RedactionStreetWordsExtra`, `RedactionPracticeWordsExtra` | all | **New, none seeded** (`ADR-074` item 7). Absent leaves rev 19 behaviour. Synthetic example texts and each row's description are in [the prompt document §5](revitalise-redaction-prompt.md) |
| `RedactionAutoRelease` | all | Unchanged key; now also needs to be saved after every other `Redaction*` row |
| `RedactionPromptCalibrated` | all | Now a label list, e.g. `NAME, ADDRESS`; `true` no longer calibrates |
| `rev_citysettlementregister` | all | Read, not written. Seeded by the existing `seed-city-settlement-register.ps1` `post_deploy` step; DEV holds 3,394 rows (E1) |

### Provisioning Scripts

None new, none changed. No `Redaction*` row is in any `settingRows` file (checked: `provisioning/` and `config/` hold no
`Redaction` string).

## 3.6 Security Controls Implemented

| Control | How | Proven by |
|---|---|---|
| An edit to the redaction rules reaches no trustee unseen (`ADR-074` item 5, `A-R85`) | `auto-release-stale` and calibration staleness, from each row's save time | `AutoReleaseGuard`, `Rev20Settings.test_auto_release_guard` |
| A setting can add, never remove (`ADR-074` item 3) | `union(floor, valid additions)`; the floor constants are compared with the model | `WordListSettings`, `DefinitionConstants`; the "replaces the floor" mutation fails 46 tests |
| A malformed setting is not partly trusted (`ADR-074` item 4) | Whole row ignored, floor applies, reason names the key | `test_a_malformed_row_is_ignored_whole_and_named` |
| Only `Redaction*` rows count | Filtered in the flow; a newer non-`Redaction` row is in every simulated read | the filter-removal mutation fails 208 tests |
| The register cannot weaken detection (`ADR-073` item 3) | It only adds spans; full postcodes never consult it | `test_full_postcode_with_its_space_is_replaced_without_the_register` |
| A missing register fails closed (`ADR-073` item 2) | Fewer than 3,000 rows or a failed read: `postcode-register-unavailable` | `test_a_failed_or_short_register_read_fails_closed_without_failing_the_run` |
| No narrative text reaches a query (`ADR-073` item 7) | The register read has no filter; the lookup is `contains()` in memory | the mock asserts no `$filter` on the register read |
| The prompt cannot add or alter text (`ADR-072` item 7) | Labels from the flow's map; every other character from the source | `test_an_injected_instruction_can_only_over_redact` |
| A partly wrong prompt answer is not partly trusted (`ADR-072` item 6) | One bad item in any window discards the column's prompt result | 23 answer shapes, flow against model |
| Prompt input and output never in run history (`ADR-072` item 9, `C-DOM-004`) | `secureData` on every action that sees a window, a quote or an answer | canary test through the stand-in run action; it found one unsecured action, now fixed |

## 3.7 Known Limitations / Deferred Items

1. **The prompt run action and the prompt component are not built.** They wait for a person to create the prompt in DEV
   (TAD §12.6.1 R1). See REVIEWER ACTION REQUIRED in the gate output. Until then a switched-on stage fails closed.
2. **Nothing is deployed, and no flow has run on the platform.** Same as Iteration 2.
3. **Five new platform guesses are open** (§3.10): the register page size, `modifiedon`'s format, the prompt's output
   contract and inputs, and `split()`'s semantics. Each fails closed if wrong.
4. **`5.3`'s proposed hours across Iterations 2 and 3 now exceed the task's accepted range** (`contract/wbs.json`); that is
   for commercial-agent to assess, not decided here.
5. **D-4 (NHS numbers and similar) is still with Emily**; the word lists are the place her answers on words can land without a deploy.

## 3.8 Build Instructions

**This amends the existing `config/revitalise-grant-automation-build.yml` (same CI slug); no step is added or changed.** The
flow is part of the `RevitaliseGrantAutomation` solution. The 57 new tests (173 in total) run inside the HARD `unit-tests` step
through `NarrativeRedaction.Tests.ps1`. The expression-length, nesting and action-count limits are asserted for every flow by
`PlatformLimits`. The new flow sits at 303 actions (limit 500), nesting depth 8 (limit 8) and a longest expression of 3,661
characters (limit 8,192). Description lengths are checked by the existing `field-length-limits` step. The pipeline needs no new step.

### Warnings this feature's build will show (shared configuration)

| Warning | Step | Triaged at |
|---|---|---|
| `pac solution pack`: *"Following root components are not defined in customizations"* — re-observed in this dispatch's local pack, unchanged | `pack-managed`, `pack-unmanaged` | [revitalise-grant-automation-dev-summary.md#L1677](revitalise-grant-automation-dev-summary.md#L1677) |
| Standing warning, `lint` | `lint` | [revitalise-grant-automation-dev-summary.md#L10323](revitalise-grant-automation-dev-summary.md#L10323) |
| Standing warnings, `code-app-install`, `-cards`, `code-app-unit-tests` | shared | [revitalise-grant-automation-dev-summary.md#L4893](revitalise-grant-automation-dev-summary.md#L4893) |
| `code-app-audit`, `-cards` — **provisional**: 0 vulnerabilities in both apps when read at the end of this dispatch, but the lockfiles are being changed by the sibling dispatch for `IMP-1072` | `code-app-audit` | The sibling dispatch's Dev Summary |
| Standing warnings, `code-app-unit-tests-cards`, `code-app-build`, `code-app-build-cards` | shared | [trustee-portal-design-2-dev-summary.md#L487](trustee-portal-design-2-dev-summary.md#L487), [#L490](trustee-portal-design-2-dev-summary.md#L490), [#L484](trustee-portal-design-2-dev-summary.md#L484) |

## 3.9 Test Guidance

- **Logic and definition:** `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'` — 173 tests.
- **What the simulator does not prove:** the register's real page size (`A-NS-21`), `modifiedon`'s real format (`A-NS-22`),
  anything about the prompt's real behaviour (`A-NS-8`, `A-NS-10`, `A-NS-20`), and `split()`'s case-sensitivity (`A-NS-24`).
- **First DEV run after import, still with no setting rows:** an application with "We moved to LS62AB, we are in LS6 area"
  in the narrative writes *"We moved to [ADDRESS], we are in [ADDRESS] area"*. The reasons are `threshold-missing-or-invalid`
  and `auto-release-off`, with no `postcode-register-unavailable`, which proves the register read (`A-NS-21`).
- **Then, synthetic data only:** add `RedactionStreetWordsExtra` = `wynd`, and a narrative "off Mill Wynd" gets
  `residual-street-word`. Add `RedactionAutoRelease` = `true` *before* that row, and the reason is `auto-release-stale`
  (`A-NS-22`). A value `wynd\n7th` gives `redaction-setting-invalid:RedactionStreetWordsExtra`.

## 3.10 Unvalidated Assumptions Register (C-TECH-052)

New rows, and rows whose source location changed in this iteration. Iteration 2's other rows stand as written. `A-NS-11`
(`nthIndexOf()`) is not used, so it guards nothing in source and is not a row. `A-NS-14` concerns a run that is not part of
this build.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-8 | A completed prompt run returns `finishReason` `stop` (any case); any other value means the answer is unusable and the column is `prompt-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (Azure OpenAI convention) | No prompt exists; running one needs R2–R4 | DEV run of one corpus sample (`stop` expected) and one text built to trip moderation (another value) | OPEN |
| A-NS-9 | The prompt is a solution component; until its shape is copied from a DEV export there is no run action, and a running stage is `prompt-error` on every column | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | Needs R1 (an interactive maker session) | R1, then export and unpack: the component appears; and the stand-in splice is replaced by the exported action | OPEN |
| A-NS-10 | The prompt's `text` is a JSON array that `json()` parses; prose or fenced JSON fails the parse and is `prompt-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | as A-NS-8 | The same DEV run: one well-formed answer (parses) and one forced to prose (fails, `prompt-error`) | OPEN |
| A-NS-15 | `sort(array, '<property>')` sorts ascending by that property, for the merge (`start`) and the prompt categories (`label`); otherwise spans merge wrongly and categories reorder | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 | No run | One DEV test `Compose` over `[{start:10},{start:2}]` and `[{label:'NAME'},{label:'ADDRESS'}]` | OPEN |
| A-NS-20 | The prompt takes three named text inputs and returns `text` and `finishReason`; the run action passes `Categories`, `AllowedLabels` and `Narrative` by name | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (template inputs E1) | Needs R1 | R1's export: read the action's parameter names and the output schema | OPEN |
| A-NS-21 | *List rows* on the register with only `$select` returns all 3,394 rows in one response; if it returns fewer than 3,000, every record gets `postcode-register-unavailable` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (5,000 default page); **E1 that DEV holds 3,394 rows and the set name is `rev_citysettlementregisters`** (`pac env fetch`, 2026-10-06) | No flow run | First DEV run (§3.9): no `postcode-register-unavailable` and "LS62AB" replaced | OPEN |
| A-NS-22 | *List rows* returns `modifiedon` as ISO 8601 that `ticks()` reads; a changed save moves it and an unchanged save does not; a row without it fails the run | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No run | DEV test (§3.9): edit a row after `RedactionAutoRelease`, see `auto-release-stale`; save `RedactionAutoRelease` unchanged, still stale | OPEN |
| A-NS-23 | In DEV (`crm17`) with *Move data across regions* unticked, a prompt can be created, given a model, saved inside the solution and exported; if not, building the component needs a residency act and is an `ARCH_GAP` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 only | Needs R0 and R1 | R1 itself, with R0's setting state recorded ([prompt document §3](revitalise-redaction-prompt.md)) | OPEN |
| A-NS-24 | `split()` is case-sensitive and finds occurrences left to right without overlap, in the units `length()` and `substring()` use; otherwise a quote's offsets are wrong and a span lands on other characters | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (`split` documented; case and overlap not stated) | No run | One DEV test `Compose`: `length(split('Ann ann Ann', 'Ann'))` = 3 and `length(split('aaa', 'aa'))` = 2 | OPEN |

## 3.11 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic, rev 20 | **V1, and executed in a simulator**, not a V-level on the platform | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: 173 OK (44 + 80 + 49) |
| Proof the tests can fail | — | macOS, local | 20 of 20 non-equivalent JSON mutations and 6 of 6 model mutations fail the suite; 2 equivalent mutants named (rules §11.3); files restored byte for byte (md5) |
| Solution with the changed flow | **V2** | macOS, local | `run-source-gates.py`: 19/19 PASS; `verify-flow-definition-language.py`: OK, no check-7 exception; `pac solution pack --packagetype Unmanaged`: complete, the packed flow holds the register read, the seam and the validation Scope |
| Pester wrapper | Executed | macOS, local | `Invoke-Pester src/tests/narrative/NarrativeRedaction.Tests.ps1`: 2/2 |
| Register and settings in DEV | E1 read, **no V-level** | DEV, read-only | `pac env fetch`: 3,394 register rows; set names `rev_citysettlementregisters`, `rev_settings`; no `Redaction*` row |

**V3, V4 and V5 are not reached for anything.**

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| *"Following root components are not defined in customizations"* (local pack, this dispatch) | pack-unmanaged | Accepted (unchanged) | Standing; see §3.8. This change adds no relationship or environment variable |
| `pac env fetch --xml '<inline>'` crashed with `System.Xml.XmlException` | diagnostic read | Resolved | Re-run with `--xmlFile`, which works; logged as a capability |

### Diagnostic components created and removed (C-TECH-056)

None. Every live call was a read (`pac env fetch` on `rev_citysettlementregister`, `entity` and `rev_setting`). The packed zip
and the mutation backups were written to the session scratch directory.

## 3.12 Work Items — close-out record (C-TECH-079)

No items carried (architect checked the ledger: none exist for narrative scrubbing).

### Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 5.25 h | Register, settings reads, prompt stage and validation in the flow; the model; 57 tests; 26 mutations |
| 5.6 | 1.25 h | The tunable word lists and guard rails the process owner uses after Emily's review; rules §7c |
| 5.4 | 0.25 h | Four new review reasons and their wording in rules §7 |
| system | 0.25 h | Three findings |

---

## Findings Logged (Iteration 3)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1078 | `capability-established` | friction | An entity set name and row counts are readable with `pac env fetch --xmlFile` over the `entity` table; the inline `--xml` form crashes pac |
| IMP-1079 | `gate-fired` | friction | A Select's run-history inputs are its whole from-array: secure it when the rows carry text, even if it projects numbers |
| IMP-1080 | `oracle-comparison-covers-only-enumerated-combinations` | friction | A flow-versus-oracle suite proves agreement only on the combinations it lists; mutate each new rule and cross each stage with each failure path |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist (Iteration 3)
- [x] All FR IDs covered — FR-026 to FR-031 (postcode register, prompt stage to its boundary), NFR-017, NFR-019 (tunables in `rev_setting`)
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — §3.6; the `rev_setting` audit and Admin-only edit are unchanged
- [x] Every TAD §12 item has an idempotent provisioning script — no new item
- [x] Role assignments via group teams only — n/a
- [x] No hardcoded environment-specific IDs/URLs — none added
- [x] Every guessed platform contract is in §3.10 **and** commented `A-nnn` in source
- [x] Where an environment existed, ground truth was used instead of a guess — register size and set name read from DEV; the prompt cannot be (R1)
- [x] Every platform limit the packer does not enforce has a build gate — `PlatformLimits` (depth now at 8 of 8), `field-length-limits`
- [x] Verification levels in §3.11 are the levels actually executed
- [x] Scripts run on the CI runner's OS — Python stdlib only
- [x] Every tool warning triaged in §3.11; no diagnostic components left
- [ ] Accessibility requirements met — no UI change in this iteration
- [x] No dead code or debug statements — two guards are redundant by design and named (rules §11.3)
- [x] Unit tests written
- [x] Every carried work item is built or deferred — none carried

## Approval (Iterations 2 and 3)
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-06  **Response:** *"Code review approved."* (logged in `logs/routing.log`, 2026-10-06 20:45)

---

# Iteration 4 — build fix and the prompt run action (2026-10-06)

**WBS:** `wbs:5.3` (the prompt component and its run action), `wbs:5.4` (the form test the review tab broke) · **Date:**
2026-10-06 · **Author:** development-agent, strategic tier (dispatch: *"custom privacy control over special-category
data"*, `logs/routing.log` 21:10) · **Status:** APPROVED 2026-10-07, with post-approval changes listed at the end · **Items:** none carried

**Reviewer actions this iteration builds on** (Xander Lykopoulos, 2026-10-06, verbatim, `logs/routing.log` 20:45 and 20:57):

> *"Ok prompt is in the solution now. I created the three text inputs but they don't hold data."* (TAD §12.6.1 R1)
> *"move data accross regions is on."* · *"The setting was already on"* (R0 for DEV)

**Held to the dispatch's limits:** the prompt was not run; no setting row was written; the only live calls were reads
and one solution export. The stage still ships off.

## 4.1 Implementation Summary

- **The build blocker `IMP-1082` is fixed by correcting the test, not the form.** The form matches the approved
  Iteration 1 design: the raw column stays editable on its own tab, and the Narrative Scrubbing tab shows a read-only copy.
  The test counted every control for a column and expected one. It now checks the rule it was written for: exactly one
  control a grant admin can type into, and any other copy read-only and on the scrubbing tab
  ([IntakeContract.Tests.ps1#L1590](../../src/tests/solutions/IntakeContract.Tests.ps1#L1590)).
- **The coverage drop did not happen.** The build compared two different numbers. 75.70% is Pester's figure for
  commands; 82.79% was the gate's figure for lines. The gate itself, run on that build's own report, passes at 91.57%. The
  test runner now says which figure it prints ([Invoke-Tests.ps1#L162](../../src/tests/Invoke-Tests.ps1#L162)).
- **The prompt is now part of the solution, copied exactly from DEV**
  ([Customizations.xml#L69](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L69),
  [Solution.xml#L290](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L290)). Two checks that had
  never seen this kind of component now know it: the source check and the after-deploy check.
- **The flow calls the prompt** ([`Run_the_redaction_prompt`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2908)).
  It replaces the empty placeholder, as the Iteration 3 tests had rehearsed. The input and output names come from the
  export. **The call's wiring was checked on 2026-10-07** against a *Run a prompt* action the reviewer saved in the DEV
  test flow: the operation, the prompt id and the three parameter names match exactly. The reviewer then added a step
  reading each of the action's outputs, and the designer's own expressions put the answer exactly where the flow reads
  it. Nothing needed correcting. The stage still ships off.

## 4.2 Components Changed / Created

| Component | Type | Change | WBS |
|---|---|---|---|
| [`IntakeContract.Tests.ps1#L1590`](../../src/tests/solutions/IntakeContract.Tests.ps1#L1590), [`#L1606`](../../src/tests/solutions/IntakeContract.Tests.ps1#L1606) | Test | "Exactly one control" becomes "exactly one editable control; any copy read-only, on the scrubbing tab, id `<field>1`"; a new test pins all 12 raw controls on the tab | 5.4 |
| [`Invoke-Tests.ps1#L162`](../../src/tests/Invoke-Tests.ps1#L162) | Test runner | The printed coverage says it is the command figure, not the gated line figure | — |
| [`Other/Customizations.xml#L69`](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L69) | AI model component (new) | `<AIModels>` block, byte for byte from the DEV export | 5.3 |
| [`Other/Solution.xml#L290`](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L290) | Root component | `type="401"`, as exported | 5.3 |
| [`REVNarrativeScrubFreeText-…json#L2908`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2908) | Cloud flow | `Run_the_redaction_prompt`, `Record_a_prompt_call_failure` ([#L2944](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2944)), `Compose_prompt_answer` reads the action ([#L2958](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2958)), `Join_the_prompt_call_paths` ([#L3351](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3351)); 303 → 306 actions | 5.3 |
| [`….notes.md`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md) | Design notes | The run action replaces "the seam"; marker table updated | 5.3 |
| [`scripts/verify-solution-root-components.py#L50`](../../scripts/verify-solution-root-components.py#L50) | Build gate | Knows type 401 and where its definition lives ([#L137](../../scripts/verify-solution-root-components.py#L137)) | system |
| [`provisioning/dataverse/verify-solution-components.ps1#L381`](../../provisioning/dataverse/verify-solution-components.ps1#L381) | After-deploy check | Checks the AI model exists by id; without this branch the first post-deploy run would have failed on "no live-check implemented" | 5.3 |
| [`BuildGates.Tests.ps1#L192`](../../src/tests/build/BuildGates.Tests.ps1#L192), [`VerifySolutionComponents.Tests.ps1#L219`](../../src/tests/provisioning/VerifySolutionComponents.Tests.ps1#L219) | Tests | Both new branches, both directions | — |
| [`src/tests/narrative/test_prompt_component.py`](../../src/tests/narrative/test_prompt_component.py) | Tests (new, 14) | Component against the prompt document; the run action and its answer path against the component and against the designer-saved definitions | 5.3 |
| [`src/tests/narrative/fixtures/run-a-prompt-action.json`](../../src/tests/narrative/fixtures/run-a-prompt-action.json) | Test fixture (new) | The DEV designer's saved *Run a prompt* action and its five output expressions (2026-10-07); test values removed | 5.3 |
| [`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py) | Tests | The stand-in splice removed: the mock answers the real operation, checks the id and the input names, and wraps the answer at the body path the flow reads; three new tests | 5.3 |
| [`revitalise-redaction-prompt.md#L166`](revitalise-redaction-prompt.md#L166) | Prompt document | Status updated; section 6 records what the export showed | 5.3 |

## 4.3 Data Model Changes

**None.** No column, view, role or form change. `IsSecured` is unchanged everywhere, so no special-category register row
is proposed.

## 4.4 Automation / Workflow Changes

**The run action** sits after `Compose_prompt_request`. It sends `Categories`, `AllowedLabels` and the window as
`Narrative` to the prompt, which it names by the prompt's id from the export. Both its inputs and outputs are hidden from
run history. If the call fails, `promptState` becomes `error` and the column is `prompt-error`. A join step ends both
paths, the same shape the extractor already uses. `Compose_prompt_answer` reads `text` and `finishReason` from the
answer. The validation that follows is the Iteration 3 code, unchanged.

**The flow is still at the platform's nesting limit of 8, and still passes it.** All three new actions are leaves.

**What the export showed, and what was not adopted** (full table in [the prompt document, section A2 (was §6 until 2026-10-16)](revitalise-redaction-prompt.md#L166)):

| # | Drift from the prompt document | Adopted? |
|---|---|---|
| 1 | The prompt builder put a space on each side of each input token | Yes. It is harmless, and `test_the_exact_drift_from_the_document_is_the_recorded_drift` pins exactly this, so any other drift fails the build |
| 2 | The builder's output setting is **text**, not JSON | **Kept as text — reviewer decision D-1 = (a), 2026-10-07** (*"thanks for clarifying: output is set to text."*). The template itself asks for JSON, and the flow parses the text with `json()`. A reply in code fences fails safe but loses recall |
| 3 | Content moderation did not appear in the 2026-10-06 export | **Settled.** The reviewer confirmed Low (*"Content moderation low."*, 2026-10-07) and re-published the prompt at 08:38. The 2026-10-07 export carries `contentModerationLevel: Low`, and the component was re-copied from it. `test_model_settings_as_exported` now asserts it |
| 4 | `Categories` has a test value, `Sample` | No effect at run time |

**R0 for DEV:** *Move data across regions* was already on before R1. So R1 shows a prompt can be created with the setting
on. It does not show whether one can be created with it off, which is the state TST/ACC and PRD keep (`A-NS-23`, still
OPEN). `ADR-072` item 3 assumed DEV's setting was off; it was not ([IMP-1086](../../logs/improvement-log.jsonl)).

## 4.5 Configuration & Provisioning Changes

| Key | Environment | Notes |
|---|---|---|
| `RedactionPromptStage` | all | **Still not seeded.** The stage ships off. `test_no_setting_row_switches_the_stage_on_in_any_shipped_file` checks `provisioning/` and `config/` |
| Connection references | all | None new. The prompt runs on the existing Dataverse connection (`rev_SharedDataverse`) |

### Provisioning Scripts

[`verify-solution-components.ps1`](../../provisioning/dataverse/verify-solution-components.ps1#L381) gains a branch for
the new component type. It is a read, and its behavioural test is in `VerifySolutionComponents.Tests.ps1`. No new
script, so none of the three new-script companion checks applies.

## 4.6 Security Controls Implemented

| Control | How | Proven by |
|---|---|---|
| The window and the answer never reach run history (`ADR-072` item 9, [C-DOM-004](../../constraints/domain/domain-constraints.md#L37)) | `secureData` on inputs and outputs of the run action | `test_a_prompt_answer_never_reaches_run_history_unsecured` (now through the real action); the "outputs unsecured" mutation fails 2 tests |
| A failed or misread call never lets text through (`ADR-072` item 8) | Failure sets `prompt-error`; a null answer is unusable | `test_an_answer_at_another_body_path_fails_closed` (3 wrong paths) |
| The prompt can only point, not write (`ADR-072` item 7) | Unchanged Iteration 3 validation | 23 answer shapes, now through the real action |
| The stage stays off until a residency decision (`ADR-072` item 3) | No `Redaction*` row seeded | the seed test above |

## 4.7 Known Limitations / Deferred Items

1. **The run action's shape is now ground truth, but it has never been executed.** On 2026-10-07 the reviewer saved
   *Run a prompt*, and then a step for each of its five outputs, in the DEV test flow (`logs/routing.log`; read with
   `pac env fetch`). Both match the flow (§4.11). What a real answer contains (`finishReason`'s values, JSON in `text`)
   is still `A-NS-8` and `A-NS-10`, and needs a run (R2–R5).
2. **No prompt run in any environment.** TAD §12.6.1 R2–R5 still stand.
3. **The pack warns that the AI model is "not defined in customizations"**, as it does for relationships and environment
   variables. It does the same when repacking DEV's own export, and the packed zip holds the component. Triaged in §4.11.
4. **`A-NS-23` cannot be answered in DEV** (the setting was already on). It should be checked in TST/ACC before the
   import that brings the prompt there.

## 4.8 Build Instructions

**This amends the existing `config/revitalise-grant-automation-build.yml` (same CI slug); no step is added or changed.**
The new tests run inside the existing HARD `unit-tests` step. The type-401 knowledge is in the existing
`root-components-resolve` step's script.

### Warnings this feature's build will show (shared configuration)

| Warning | Step | Triaged at |
|---|---|---|
| `pac solution pack`: *"Following root components are not defined in customizations"* — **one new line**, `Type='AIModel'` | `pack-managed`, `pack-unmanaged` | §4.11 below; the existing lines at [revitalise-grant-automation-dev-summary.md#L1677](revitalise-grant-automation-dev-summary.md#L1677) |
| `lint` (live Solution Checker): **Medium 15**, all `flow-avoid-recursive-loop` — 1 standing on `REVSafeguardingActionCompletion`, **14 new** on this feature's flow | `lint` | The 1: [revitalise-grant-automation-dev-summary.md#L10323](revitalise-grant-automation-dev-summary.md#L10323). The 14: §4.11 below |
| Standing warnings, `code-app-install`, `-cards`, `code-app-unit-tests` | shared | [revitalise-grant-automation-dev-summary.md#L4893](revitalise-grant-automation-dev-summary.md#L4893) |
| `code-app-audit`, `-cards` | shared | Green in build 20261006-3 after the `IMP-1081` fix; no code-app file touched here |
| Standing warnings, `code-app-unit-tests-cards`, `code-app-build`, `code-app-build-cards` | shared | [trustee-portal-design-2-dev-summary.md#L487](trustee-portal-design-2-dev-summary.md#L487), [#L490](trustee-portal-design-2-dev-summary.md#L490), [#L484](trustee-portal-design-2-dev-summary.md#L484); the card app's chunk advisory also has its own row in §4.11 |

## 4.9 Test Guidance

- **Narrative logic, definition and component:** `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'` —
  199 tests (189 at approval, plus the 10 trigger-loop tests added after it).
- **Full suite:** `pwsh -NoProfile -File src/tests/Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 0 -OutputPath <dir>`,
  then `python3 scripts/verify-coverage-threshold.py <dir>/coverage.xml --threshold 80 --exclusions config/coverage-exclusions.json`.
- **After import to DEV (V3/V4):** the solution shows *REV Narrative Redaction Prompt* once, not twice. The after-deploy
  check prints `PASS — AI model 122be8e0-… exists`. Open the flow in the designer: `Run_the_redaction_prompt` shows
  the prompt by name with three inputs filled. Save.

## 4.10 Unvalidated Assumptions Register (C-TECH-052)

Rows new in this iteration, or whose evidence changed. Earlier rows stand as written.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-9 | The component copied from the DEV export packs, imports into TST/ACC and PRD, and keeps the same id there, so the run action's `recordId` resolves; if not, every call fails and the column is `prompt-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | **E1 for the shape** (DEV export, 2026-10-06); V2 local pack of both types holds it; import not done | No import in this dispatch | The next import: the after-deploy check's `PASS — AI model …`; open the flow in the designer and see the prompt resolved | OPEN |
| A-NS-13 | The extractor action is `aibuilderpredict_entityextraction` with `item/requestv2/text` and `item/requestv2/language`; if wrong, the column is `ai-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | **E1 for the shape**: the reviewer's DEV flow *TestAIBuilder* (read 2026-10-06) has exactly this operation and these parameters. No run read | The run's output is in run history, which `pac env fetch` cannot read | Read *TestAIBuilder*'s latest run in the maker portal: the action succeeded, and the output shows where the entities are (`A-NS-16`) | OPEN |
| A-NS-20 | One call accepts 16,000 characters of categories plus a 5,000-character window; if not, the call fails and the column is `prompt-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | **E1 for the names and the parameter form**: the export's run specification, and the DEV designer's saved action (`item/requestv2/Categories`, `/AllowedLabels`, `/Narrative`, 2026-10-07). The length is E3 | Needs a run | A DEV run with the longest category rows (R2–R5) | OPEN |
| A-NS-23 | With *Move data across regions* off, a prompt can be created, saved and run in a `crm17` environment; if not, using the stage outside DEV needs a residency act | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | **Unanswerable in DEV**: R0 found the setting already on there (2026-10-06) | DEV's setting was never off | In TST/ACC (setting off): import, then open the prompt in the maker portal and check a model is shown and it saves | OPEN |
| ~~A-NS-25~~ | ~~The run action is `aibuilderpredict_customprompt` with `recordId`, and the answer is at `body/responsev2/predictionOutput/text` and `…/finishReason`~~ **CLOSED (E1, 2026-10-07)** — the DEV designer's saved *Run a prompt* action has this operation, `recordId` (the component id, no braces) and the three `item/requestv2/` names; the designer's own expressions for its outputs read `body/responsev2/predictionOutput/text` and `…/finishReason`, the same keys the flow reads. Pinned by `test_the_run_action_matches_the_designer_saved_action` and `test_the_answer_path_is_the_one_the_designer_writes` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E1 (designer-saved definition; never run) | — | — | CLOSED |
| A-NS-26 | The platform counts the flow's container nesting as 8 (the limit) and does not count the leaf actions inside the 8th container as a ninth level; the flow is also 344,007 bytes against 255,516 for the largest flow already live, and no size limit is hit. If the platform counts the leaves, the flow still packs and imports, then the designer or the save refuses it (or marks it invalid), and the scrubbing stage cannot be edited or turned on until `Validate_the_prompt_answer` is flattened, which is a flow change and a new build | `src/tests/narrative/test_scrub_flow_definition.py` (the flow JSON cannot carry a comment; the guess is the `PlatformLimits` depth assertion) | E2 only (documentation, *Limits of automated, scheduled, and instant flows*) | No import of this flow yet | In DEV: import, open the flow in the designer and save, then re-read it live (`verify-live-flow-definitions.py --env dev`); a clean save with all actions present closes both halves | OPEN |

## 4.11 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Form test (`IMP-1082`) | Executed | macOS, local | `Invoke-Pester -Path src/tests/solutions/IntakeContract.Tests.ps1`: 160/160. Five form mutations each fail the new tests; form restored byte for byte (md5) |
| Full Pester suite | Executed | macOS, local | `Invoke-Tests.ps1 -CodeCoverage -CoverageThreshold 0`: **1,339 passed, 0 failed, 1 skipped** |
| Coverage | Gate executed | macOS, local | `verify-coverage-threshold.py … --threshold 80`: **91.57% of lines, exit 0** (this tree); 91.57%, exit 0 on build 20261006-3's own report |
| Prompt component | **E1 (export) and V2** | DEV read-only; macOS | `pac solution export` + `unpack`; `pac solution pack` Managed and Unmanaged: both zips hold `<AIModels>` and the type-401 root component. **Re-exported 2026-10-07** after `pac env fetch` on `msdyn_aiconfiguration` showed a new run configuration published at 08:38. The only configuration difference was `contentModerationLevel: Low`, plus the new configuration id and iteration. Re-copied, and both package types re-packed with it |
| Run action shape, inputs and outputs | **E1** (designer-saved definitions, never run) | DEV read-only | `pac env fetch` on `workflow` `9f2f0627-…` clientdata, 2026-10-07, read twice: (1) host, `recordId` and the three parameter names equal `Run_the_redaction_prompt`'s; (2) the five output expressions the designer wrote — `…?['body/responsev2/predictionOutput/text']`, `…/finishReason`, `…/predictionOutput`, `…/responsev2`, `body(…)` — put `text` and `finishReason` at the keys `Compose_prompt_answer` reads. The flow keeps the standard `body()?[…]` form; the keys are compared one by one. No source change needed. The two path mutations fail the new test |
| Run action and flow logic | **V1, executed in the simulator**; not a V-level on the platform | macOS, local | 189 narrative tests OK. 9 mutations of the run action (id, answer path, reason path, unsecured output, no failure record, input renamed, inputs swapped, no join, failure not marked) each fail the suite; file restored (md5) |
| Gates for the new type | Executed | macOS, local | `verify-solution-root-components.py`: PASS, 86 root components; its new test and the after-deploy check's new test pass in both directions |
| Source gates | V1 | macOS, local | `run-source-gates.py`: 19/19 PASS, after one fix (the run action's description was 369 characters against the 256 limit) |
| No trigger loop (after approval, `IMP-1090`) | **V1, over the definition**; the Solution Checker report is the V2 input | macOS, local | `NoTriggerLoop` in `test_scrub_flow_definition.py`, 10 tests OK. Two mutations of the **flow file itself** each fail it: `item/rev_status` added to `Hold_the_record_for_review` (2 failures), `rev_redactionreleased` added to the trigger filter (4 failures); file restored (md5 identical). Six more mutations run inside the class (whole-row write, unfiltered trigger, a cross-flow loop with the safeguarding flow, an unclassified Dataverse operation, a trigger condition) |

**V3, V4 and V5 are not reached for anything in this iteration.**

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `pac solution pack`: *"Following root components are not defined in customizations: Type='AIModel', Id='{122be8e0-…}'"* | pack-managed, pack-unmanaged | Accepted | The packer reports it for an inline AI model the same way it reports the standing relationship and environment variable lines. **Repacking DEV's own export gives the identical line**, and both packed zips contain the component. It is the packer's view of this type, not a source defect |
| `field-length-limits`: the run action's description at 369 characters | source gate | Resolved | Shortened to 227 |
| `pac env fetch`: *"The top attribute can't be specified with paging attribute page"* | diagnostic read | Resolved | Re-run without `top` |
| `pac solution check` (build 20261007-2): **Critical 0, High 0, Medium 15, Low 0**, every result `flow-avoid-recursive-loop`. **14 are on this flow**, one per Dataverse write: the 12 `Write_rev_…redacted` actions under `Write_the_counterpart`, `Write_the_decision` and `Hold_the_record_for_review`. The 15th is the standing `REVSafeguardingActionCompletion` result ([revitalise-grant-automation-dev-summary.md#L10323](revitalise-grant-automation-dev-summary.md#L10323)) | lint | Accepted (false positive, proven) | **The flow cannot trigger itself.** The trigger fires only on an update that names `rev_status` (`filteringattributes: "rev_status"`, no trigger conditions). The 14 actions write only the 12 `…redacted` columns, `rev_redactionconfidence`, `rev_redactionreleased` and `rev_redactionreviewrequired`, never `rev_status`. No other flow listens on those columns, so there is no loop through another flow either. The checker flags every write to the trigger's own table and ignores the filter: it still flags the safeguarding flow after its trigger was filtered (`IMP-0948`). **Evidence:** the SARIF from the build's Results URL, read 2026-10-07 (its 14 action names match the flow's 14 writes one for one), and the `NoTriggerLoop` tests in [test_scrub_flow_definition.py](../../src/tests/narrative/test_scrub_flow_definition.py), which fail if any write names a column the trigger listens on, if the filter is removed, if a write to `rev_applications` is added or removed, or if two flows form a loop (*Verification level* above). **The flow is not changed** |
| Vite *"Some chunks are larger than 500 kB"*, card app: JS **845.81 kB** (845,809 bytes), CSS 148.64 kB | `code-app-build-cards` (shared configuration) | Accepted, standing | The same byte count as `measured_bytes` in `src/code-apps/trustee-review-portal-cards/bundle-budget.json` (max 871,100), and `code-app-bundle-budget-cards` passed in build 20261007-2. This feature touches no code-app file. Triaged at [trustee-portal-design-2-dev-summary.md#L484](trustee-portal-design-2-dev-summary.md#L484) |

### Diagnostic components created and removed (C-TECH-056)

None. Every live call was a read (`pac env fetch` on `msdyn_aimodel`, `workflow`, `entity`) or the solution export,
which changes nothing in DEV. The export, the unpacked tree and the packed zips are in the session scratch directory.

## 4.12 Work Items — close-out record (C-TECH-079)

No items carried.

### Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 2.5 h | Export and ground truth, the component, the run action and its checks against the designer's definitions, 17 new tests, 9 mutations, the after-deploy branch. Hours on `wbs:5.3` above the accepted range are the reviewer's unbilled decision, recorded as `EX-010` / `CE-0018` |
| 5.4 | 0.5 h | The form test fix and its 5 mutations |
| system | 0.5 h | The root-components gate, the runner label, six findings |

---

## Findings Logged (Iteration 4)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1083 (fixes IMP-1082) | `test-coupled-to-absolute-counts` | friction | When a form gains a second control for a column, assert one editable control, not a raw count, and run the full suite before review |
| IMP-1084 | `output-shape-defeats-the-reader` | friction | The unit-tests step prints command coverage; only the coverage-threshold step's line figure is comparable |
| IMP-1085 | `platform-fact-groundtruthed` | friction | An AI Builder prompt exports as type 401 inline in Customizations.xml; its run action's shape lives only in a flow that calls it |
| IMP-1086 | `reality-contradicted-repo-document` | friction | DEV's cross-region setting was already on, so `A-NS-23` must be checked where it is off |
| IMP-1087 | `platform-fact-groundtruthed` | friction | Save, don't run: a maker-saved action in a DEV test flow gives an action's input shape; add a Compose to capture its output path |
| IMP-1088 | `live-definition-drifts-from-source` | friction | Every prompt-builder publish creates a new run configuration; re-check `msdyn_aiconfiguration` before shipping a copied component |
| IMP-1091 (fixes IMP-1090; after approval) | `untriaged-tool-warning` | friction | `flow-avoid-recursive-loop` fires once per write to the trigger's table and ignores the filter; decide it from the filter against the written columns |

`IMP-1082` is stamped `fixed_in_flight` (V1, the IntakeContract file at exit 0). Digest regenerated: YES.

---

## Code Review Checklist (Iteration 4)
- [x] All FR IDs covered — FR-026–FR-031 unchanged; the prompt stage now has its call
- [x] No hardcoded secrets
- [x] Security controls from TAD §6 implemented — §4.6
- [x] Every TAD §12 item has an idempotent provisioning script — no new item; the after-deploy check is extended
- [x] Role assignments via group teams only — n/a
- [x] No hardcoded environment-specific IDs/URLs — the `recordId` is a solution component id, carried by the import, like the view id; `no-hardcoded-environment-values` passes
- [x] Every guessed platform contract is in §4.10 **and** commented `A-nnn` in source
- [x] Where an environment existed, ground truth was used instead of a guess — the component, its inputs and outputs, the entity set, the extractor action and the run action's inputs and answer path were read from DEV
- [x] Every platform limit the packer does not enforce has a build gate — description length (`field-length-limits`, which caught one), nesting (`PlatformLimits`)
- [x] Verification levels in §4.11 are the levels actually executed
- [x] Scripts run on the CI runner's OS — Python stdlib and Pester
- [x] Every tool warning triaged in §4.11; no diagnostic components left
- [ ] Accessibility requirements met — no UI change
- [x] No dead code or debug statements — the stand-in splice was removed from the tests
- [x] Unit tests written
- [x] Every carried work item is built or deferred — none carried

## Approval (Iteration 4)
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-10-07  **Response:** *"Approved on dev summary"* (`logs/routing.log`, 2026-10-07)

The approval was given while the Compose 3–7 comparison was in progress. Everything below changed **after** it:

| # | Change after approval | Changes behaviour? |
|---|---|---|
| 1 | `A-NS-25` struck through as CLOSED (E1): the designer's own output expressions match the keys `Compose_prompt_answer` reads | No. Register and evidence only |
| 2 | Fixture `run-a-prompt-action.json` gains the five designer output expressions; new test `test_the_answer_path_is_the_one_the_designer_writes` (both path mutations fail it) | No. Tests only |
| 3 | The `description` text of `Run_the_redaction_prompt` and `Compose_prompt_answer` in the flow JSON reworded (no A-NS-25 guess left) | No. Descriptions are not executed; expressions unchanged |
| 4 | **The prompt component re-copied** from a fresh export (2026-10-07). The reviewer had re-published it at 08:38: the new active run configuration id is `96b4155b-…`, the iteration number is 2, and the settings now carry `contentModerationLevel: Low`. Template, inputs, outputs, model and temperature are identical to the approved copy | **Yes, for the prompt only.** The shipped component now states moderation Low explicitly, matching R1 and the reviewer's confirmation. The flow's logic is unchanged |
| 5 | `test_model_settings_as_exported` asserts moderation Low (it asserted moderation was absent) | No. Tests only |
| 6 | Notes, prompt document §6, this section's drift rows 2–3, D-1 recorded | No. Documents only |
| 7 | **Build 20261007-2 BLOCKED on 14 Solution Checker results (`IMP-1090`).** Triaged as proven false positives in §4.11; 10 new `NoTriggerLoop` tests in `test_scrub_flow_definition.py`; §4.8 and §4.9 updated | No. Tests and documents only; **the flow file is unchanged** |
| 8 | §4.11 gains this feature's citing row for the card app's 845.81 kB chunk advisory (`C-TECH-055`, 2026-08-30 amendment) | No. Documents only |
| 9 | **D-1 of test report 20261007-3 fixed.** New register row `A-NS-26` (E2) in §4.10, source marker at `PlatformLimits` in `test_scrub_flow_definition.py`, and the notes file's "platform's limit" wording restated as an assumption | No. Documents and a test comment only; **the flow file is unchanged** (md5 `193bccb83cd7c0f0139fae9edddea4ce`) |

---

# Iteration 5 — the failure diagnosis moves inside the column loop (2026-10-09)

**WBS:** `wbs:5.3` (the flow's failure path, NFR-018, FR-010); dispatch carried `5.4` and `5.6`, which this fix does not
change · **Date:** 2026-10-09 · **Author:** development-agent, strategic tier (dispatch: *"no existing pattern in the
codebase for this"*) · **Status:** awaiting code review · **Items:** none carried

## 5.1 Summary

The reviewer could not save the flow in the DEV designer: the failure handler at the top of the flow read the results of
steps inside the column loop, which the platform forbids. The diagnosis now runs inside the loop iteration that failed
and is carried out in a variable, a new gate (check 12) fails any flow that reads into a loop from outside it, and the
alert the operator gets is unchanged in form. Nothing is deployed; the designer save (V4) is the next check.

## 5.2 What has been built

1. **Every container inside the column loop has a three-step catch beside it**
   ([`Rethrow_the_failure_inside_Scrub_the_column_if_it_has_text`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5374),
   [`Record_the_failure_inside_Write_the_counterpart`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5135)).
   It runs only when that container failed, in the same iteration. It records which child failed first and its error
   code, then fails on purpose so the run still fails and the record is still held. A loop cannot use *Terminate*, so
   the re-raise is an `int()` of the recorded step name, which always throws (`A-NS-27`). There are 16 such catches.
2. **The top level follows the record inwards instead of reading into the loop**
   ([`Follow_the_failure_inward`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5665),
   [`Set_failure_detail_from_For_each_column`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5722)).
   It starts at the loop body's failed step, which it may read, and moves to the step each catch recorded until it
   reaches a step with no record: the action that failed. Taking the first record would be wrong.
   `Detect_shapes_in_the_window` still runs after an earlier window step fails, fails as a result, and records first.
3. **A failure the flow already handles is never reported or re-raised**
   ([`Find_the_failed_step_inside_Validate_the_prompt_answer`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3527),
   [`_handled_by_design`](../../src/tests/narrative/failure_catches.py#L74)). `Validate_the_prompt_answer` failing *is*
   the designed "invalid answer" path, so it gets a diagnostic query only. The catches also skip the extractor call, the
   prompt call and the parse, whose failures are reasons, not failed runs.
4. **The shape is generated, and the tests fail if the JSON differs**
   ([`failure_catches.py`](../../src/tests/narrative/failure_catches.py#L253)). The notes said the old descent was
   generated, but no generator was in the repository. This one is, and `--write` reproduces the shipped file.
5. **Check 12 fails any flow that reads into a loop from outside it**
   ([`check12_findings`](../../scripts/verify-flow-definition-language.py#L217), wired at
   [#L420](../../scripts/verify-flow-definition-language.py#L420) inside the existing HARD `flow-definition-language`
   build step). It forbids every crossing, one level included, which no flow in the solution needs. An Until's own
   condition may name its body. **On the source before this fix it exits 1 with 17 findings, all in this flow, the
   reviewer's offender first. After the fix it exits 0 over all 11 flows.**

## 5.3 Elements added

| Element | Where | WBS |
|---|---|---|
| `failureTrail` (array) and `failureCursor` (string) variables | [flow JSON#L126](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L126) | 5.3 |
| 16 catches (Find, Record, Rethrow: 48 actions) and 1 diagnostic query inside the loop; the follow-inward Until at the top | flow JSON | 5.3 |
| Generator | [`src/tests/narrative/failure_catches.py`](../../src/tests/narrative/failure_catches.py#L1) | 5.3 |
| 10 tests, `FailureDiagnosisInsideLoops` | [`test_scrub_flow_definition.py#L1072`](../../src/tests/narrative/test_scrub_flow_definition.py#L1072) | 5.3 |
| Check 12 and its known-bad fixture | [`verify-flow-definition-language.py#L217`](../../scripts/verify-flow-definition-language.py#L217), [`CrossLoopReference.json`](../../src/tests/fixtures/known-bad/flow-cross-loop-reference/CrossLoopReference.json) | system |

## 5.4 Elements changed

| Element | Change | WBS |
|---|---|---|
| `Describe_the_failure`, case `For_each_column` | The 46-action nested Switch tree that read into the loop is replaced by eight actions (an Until holds three of them) that read only `result('For_each_column')` and the variables | 5.3 |
| Flow size | 296 → 309 actions; deepest nesting still 8 (no container added inside the loop) | 5.3 |
| [Notes, "The failure descent"](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md#L161) | Rewritten for the new shape; `A-NS-19` narrowed, `A-NS-27` added | 5.3 |

**Build configuration:** this amends `config/revitalise-grant-automation-build.yml` (same CI slug). No step is added or
changed: check 12 runs inside `flow-definition-language`, the tests inside `unit-tests`. No data model, form, security
role or provisioning change, so no special-category register row is proposed.

## 5.5 What is still open

**The designer save has not been done.** The import accepted the old shape without validating it, so only an open and
save in the DEV designer (V4) shows this one is accepted. The save may also show the next defect hidden behind this one:
the platform reports only the first invalid reference. `A-NS-26` (nesting 8) is still open for the same reason.

**A failure inside a window repeats that window.** When a window step fails, the step that moves to the next window is
skipped, so the Until runs the same window again, up to its limit of 250, calling AI Builder each time, if the platform
continues an Until after a failed iteration. This was true before this change and is not changed here. Stopping the
scan once `failureTrail` is not empty is one expression; it is left for a decision because it changes what later columns
in a failing run do. **Closed in Iteration 6** (the reviewer decided: fix it).

## 5.6 Unvalidated Assumptions Register (C-TECH-052)

Rows new in this iteration, or whose meaning changed. Earlier rows stand as written.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-19 | `result()` of a loop still lists a failed iteration after later ones succeed. It now matters only for a failure directly in the column loop's body, and for the catches beside `Scan_the_column_in_windows`, `Refine_each_name` and `Merge_each_span`. A deeper failure is recorded inside its own iteration. If wrong, the alert names a wrapper and the run link is the route | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E4 | No run | In DEV, make the first column's write fail and a later column succeed: the alert names the write | OPEN |
| A-NS-27 | An expression that throws at run time fails its action, so the catch's `Rethrow_the_failure_inside_*` fails the iteration, the loop and the run, and the designer's save does not evaluate `int()` of a non-numeric value in advance. If the save does evaluate it, the save is refused naming that action. If a failed action did not fail its iteration, a failed column would be scrubbed partly and the record decided instead of held | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (expression failures fail the action, *Handle errors and exceptions*); the simulator runs the stricter "last action decides" reading | No run; no designer save of this shape | V4: open and save in the DEV designer (a refusal naming a `Rethrow_` action answers the second half). V5: one DEV run with a failing write: the run shows `Rethrow_the_failure_inside_Write_the_counterpart` Failed, the record held, one alert naming the write | OPEN |

## 5.7 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Check 12, before the fix | Executed | macOS, local | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` on the pre-fix flow: **exit 1, 17 findings**, the first `Find_the_failed_step_inside_Scrub_the_column_if_it_has_text` → `result('Scrub_the_column_if_it_has_text')`, the reviewer's error. Other 10 flows: 0 findings |
| Check 12, after the fix | Executed | macOS, local | Same command: exit 0, checks 1–12 OK over 11 flows. `--selftest`: engine 29/29, wrapper 10/10, including the known-bad fixture flagged once and a planted refused shape flagged |
| Flow logic | **V1, executed in the simulator**; not a V-level on the platform | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: **209 tests OK** (199 before). A failure at each of 9 depths inside the loop and one in the prompt answer check each name the leaf, hold the record and alert once; every designed failure (extractor, all 23 prompt answers) records nothing and alerts nothing |
| Generator | V1 | macOS, local | `python3 src/tests/narrative/failure_catches.py`: the shipped definition is the generated one |
| Related Pester suites | Executed | macOS, local | `NarrativeRedaction.Tests.ps1`, `BuildGates.Tests.ps1`, `DeploymentSettings.Tests.ps1`: 171 passed, 0 failed, 1 skipped. The full suite was not run |
| Source gates | V1 | macOS, local | `run-source-gates.py config/revitalise-grant-automation-build.yml`: 19/19 PASS |

**V2 to V5 are not reached.** Nothing was packed, imported or saved. No tool warning was emitted by any command above.
No diagnostic component was created in any environment: this dispatch made no live call.

## 5.8 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 2.0 h | The redesign, the generator, 10 tests, notes and this section |
| system | 0.5 h | Check 12, its fixture and selftest, `IMP-1098` |

## Findings Logged (Iteration 5)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1098](../../logs/improvement-log.jsonl#L1094) | `platform-contract-guessed-not-groundtruthed` | blocker, stamped `fixed_in_flight` (V1) | Never read an action inside a loop from outside it; diagnose inside the iteration and carry the result out in a variable. A clean Draft import proves nothing about save |

---

# Iteration 6 — every loop ends after a failure (2026-10-09)

**WBS:** `wbs:5.3` (the flow's failure path, NFR-018, FR-010) · **Date:** 2026-10-09 · **Author:** development-agent,
strategic tier (dispatch: *"no existing pattern"*) · **Status:** awaiting code review · **Items:** none carried

## 6.1 Summary

The reviewer decided the open item from Iteration 5 must be fixed: *"definitely make sure the flow is not going to stay
stuck in a loop."* Every loop in the flow now ends as soon as something inside it fails, whether or not the platform
would go on to another iteration, and no AI Builder call is made after that point. The run still fails, holds the record
and alerts once. Nothing is deployed or committed; the designer save (V4) is still the next check.

## 6.2 What has been built

1. **The window scan stops at the window that failed**
   ([`Scan_the_column_in_windows`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2212), [`Stop_after_a_failure_in_Scan_the_column_in_windows`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3781)).
   A new leaf runs after the window's last step when that step did not succeed, sets a new `failureSeen` flag
   ([#L162](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L162)), then fails on purpose so the failure is not read as handled. The scan's condition reads
   `failureSeen` and `failureTrail`, so the loop ends after the failed iteration on either platform behaviour.
2. **Later columns do nothing once a failure is seen**
   ([`Scrub_the_column_if_it_has_text`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2104), [`Stop_after_a_failure_in_For_each_column`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5446)).
   This is the decision the dispatch asked for: no window, no AI Builder call and no write for any later column.
   Columns written before the failure stay written, as before, and the record is held as a whole; a resubmission
   re-scrubs everything.
3. **The shape check and the prompt can no longer run after an unrecorded failure**
   ([`Detect_shapes_in_the_window`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2811), [`Use_the_prompt_on_the_window`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L3135)). The shape check used to
   run after *any* skipped extractor step, so a failed `Compose_window_entities` let the prompt be called and the window
   advance with nothing recorded. It now also needs the window text and the extractor answer step. The prompt is also
   skipped once the extractor has failed on the column, because that column's prompt result is never used.
4. **Every bound is explicit and justified**
   ([notes, "Every loop ends"](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md#L199)). The window scan also ends once the extractor fails on the column (up to 249
   wasted windows before). The failure-diagnosis loop's count is 6, derived by the generator from the deepest chain of
   recorded containers ([`recorded_depth`](../../src/tests/narrative/failure_catches.py#L216)), down from 16, with a 2-minute timeout (was 5); it also ends if a
   step inside it fails. A timed-out diagnosis still holds and alerts ([`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L5874)).
5. **Check 13 holds the rule for every flow**
   ([`check13_findings`](../../scripts/verify-flow-definition-language.py#L287), wired at [#L538](../../scripts/verify-flow-definition-language.py#L538)). Every Until must state `count` and `timeout`, and an
   Until that calls out must have a failure exit. **On the source before this fix it flags the window scan, alone;
   after it, exit 0 over all 11 flows (2 Until loops).** It proves the exit is wired, not that it fires; the tests prove
   that.

## 6.3 Elements added

| Element | Where | WBS |
|---|---|---|
| `failureSeen` variable; 2 stop leaves + 2 rethrows (generated) | [flow JSON#L162](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L162) | 5.3 |
| Generator: stop leaves, derived diagnosis bound, exit assertions | [`failure_catches.py#L151`](../../src/tests/narrative/failure_catches.py#L151) | 5.3 |
| Simulator switch for both loop behaviours | [`wdl_sim.py#L212`](../../src/tests/narrative/wdl_sim.py#L212) | 5.3 |
| 11 tests, `EveryLoopEndsAfterAFailure` | [`test_scrub_flow_definition.py#L1226`](../../src/tests/narrative/test_scrub_flow_definition.py#L1226) | 5.3 |
| Check 13 and 4 selftest assertions | [`verify-flow-definition-language.py#L287`](../../scripts/verify-flow-definition-language.py#L287) | system |

## 6.4 Elements changed

| Element | Change | WBS |
|---|---|---|
| `Scan_the_column_in_windows` expression | Also ends on `columnFailed`, `failureSeen` or a non-empty `failureTrail` | 5.3 |
| `Scrub_the_column_if_it_has_text` condition | Also requires no failure seen | 5.3 |
| `Detect_shapes_in_the_window` runAfter, `Use_the_prompt_on_the_window` condition | As item 3 | 5.3 |
| `Follow_the_failure_inward` | Count 16 → 6 (derived), timeout PT5M → PT2M, ends if a move fails | 5.3 |
| `Hold_the_record_for_review` runAfter | Adds `TimedOut` | 5.3 |
| [`test_a_consequential_failure_recorded_first_does_not_hide_the_cause`](../../src/tests/narrative/test_scrub_flow_definition.py#L1162) | The shipped flow no longer produces a consequential failure, so the test restores the old runAfter to keep the chain-following proven, and checks the shipped flow names the cause | 5.3 |
| Flow size | 309 → 314 actions; nesting still 8 | 5.3 |

**Build configuration:** amends `config/revitalise-grant-automation-build.yml` (same CI slug); no step added. Check 13
runs inside `flow-definition-language`, the tests inside `unit-tests`. `config/revitalise-grant-automation-pipeline.yml`
was not touched. No data model, security or provisioning change, so no special-category register row.

## 6.5 What is still open

**The designer save has not been done.** As in Iteration 5: only an open and save in the DEV designer (V4) shows the
platform accepts this shape. The new rethrows use `int(string(variables('failureSeen')))`, which is the same bet as
`A-NS-27`: the save must not evaluate it ahead of the run.

**What the platform does after a failed iteration is still unknown, and no longer matters.** Both readings are
simulated and every new test runs under both. A DEV run with a failing window (V5) would show which one is true.

**Refine_each_name and Merge_each_span still finish their items after a failed one** on a platform that keeps
iterating. They are bounded by their input and make no call, so they were left as they are.

## 6.6 Unvalidated Assumptions Register (C-TECH-052)

No new row. `A-NS-27` now also covers `Rethrow_the_stop_in_*` (notes, assumptions table). The platform's
continue-or-stop behaviour after a failed iteration is not an assumption: the design is tested under both answers.

## 6.7 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Check 13, before the fix | Executed | macOS, local | `--selftest` puts the old window expression back in memory: **1 finding, the window scan, check 13b** |
| Flow-language gate | Executed | macOS, local | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation`: exit 0, checks 1–13 OK over 11 flows. `--selftest`: engine 29/29, wrapper 14/14 |
| Flow logic | **V1, simulator** | macOS, local | `cd src/tests/narrative && python3 -m unittest discover -p 'test_*.py'`: **220 tests OK** (209 before). A failure at each of 10 window steps, at a later window, while recording an extractor failure, directly in the column loop and inside the diagnosis loop: under both behaviours the scan ends at that window, 0 AI Builder calls follow, the record is held and one alert names the step. With the old exit the same failure runs 250 iterations and over 100 AI calls; with the old shape-check runAfter the prompt runs after the failure |
| Generator | V1 | macOS, local | `python3 src/tests/narrative/failure_catches.py`: the shipped definition is the generated one |
| Pester suites | Executed | macOS, local | `NarrativeRedaction.Tests.ps1`, `BuildGates.Tests.ps1`, `DeploymentSettings.Tests.ps1`: 171 passed, 0 failed, 1 skipped |
| Source gates | V1 | macOS, local | `run-source-gates.py config/revitalise-grant-automation-build.yml`: 19/19 PASS |

**V2 to V5 are not reached.** Nothing was packed, imported, saved or run. No tool warning was emitted. No live call was
made, so no diagnostic component exists.

## 6.8 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 1.5 h | The stop design, generator change, 11 tests, notes and this section |
| system | 0.5 h | Check 13, its selftest, the simulator switch, `IMP-1099` |

## Findings Logged (Iteration 6)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1099](../../logs/improvement-log.jsonl#L1095) | `platform-contract-guessed-not-groundtruthed` | rework | A loop whose progress step runs only on success needs a failure exit that works whether or not the platform continues after a failed iteration; test it with multi-iteration input under both readings |

# Iteration 7 — substring() never starts at the string length (2026-10-12)

**WBS:** `wbs:5.3` · **Date:** 2026-10-12 · **Author:** development-agent, standard tier · **Status:** awaiting code review ·
**Items:** none carried · Nothing deployed, committed or re-built; `config/revitalise-grant-automation-pipeline.yml` untouched.

## 7.1 Summary

The first live DEV run failed in the finish step of a column with `InvalidTemplate`: the `substring` start index must be
less than the string length (249). The text's last merged span ended on its last character, so the tail
`substring(raw, lastMergedEnd)` started at the length, which the platform refuses (aka.ms/logicexpressions#substring:
start >= 0 and < length, also with a length and on an empty string). The simulator allowed it, which is why 236 tests
passed. Both are fixed, and the same defect was found in four more places that the lenient simulator also let through.

## 7.2 What has been changed

1. **Simulator** (`wdl_sim.f_substring`) now throws for start >= length, with or without a length, and on `''`.
   With it, **273 failures and 30 errors** appeared across the suite, all from one lenient read in `Compose_window_end`
   and, once that was fixed, three more: `Select_register_candidates`, `Compose_merge_step` (two reads) and the rebuild
   gap reads. Nothing else in the other 10 flows uses `substring` on text that can end at the length (checked: their
   uses start at fixed or loop-bounded positions).
2. **Flow.** Every read from `Compose_raw_text` that could start at its length now uses
   `substring(concat(raw, ' '), start, sub(length(raw), start))` (the tail with `start` clamped by `min`), and
   `Select_extractor_spans` clamps `start` and `length` to the text. Details and rule table:
   [notes, "substring() never starts at the string length"](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md).
3. **Model** (`redaction_reference.extractor_spans`) clamps the same way, so flow and model still agree on the corpus.
4. **Tests** (new [`test_text_end_spans.py`](../../src/tests/narrative/test_text_end_spans.py), 5 tests): the simulator's
   substring boundary (start == length, empty string, with length); a text ending in an email plus a full stop, with the
   entity ending on the last character, overrunning by 1, overrunning by 500 and stopping short, each agreeing with the
   model, redacting the address and leaving nothing after it but the full stop; both `Compose_redacted_text` and
   `Compose_skeleton_text` succeed; an entity wholly past the end is harmless. The shipped flow before this change
   fails the first of these under the corrected simulator.
5. **Not added:** a static check in `verify-flow-definition-language.py` for an unguarded two-argument `substring`. It needs
   a reviewer decision on noise (the guarded idiom is a `concat(x, ' ')` source, which a regex can match, but any
   other safe form would be flagged). Proposed in `IMP-1109`.

## 7.3 Still open

The live run has not been repeated: this is **V1 (simulator, now matching the documented platform rule)**, not V3. A DEV
re-import and a run over `TESTDATA-TD-13` is the check. Source line anchors in Iterations 5 and 6 point at the flow as it
was; the file moved by a few lines.

## 7.4 Unvalidated Assumptions Register (C-TECH-052)

No new row. The platform rule is documented, not assumed. `if()` stays eager in the simulator on purpose.

## 7.5 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Simulator rule | Executed | macOS, local | strict `f_substring`: 273 failures + 30 errors before the flow fix, all traced to the five reads above |
| Flow logic | **V1, simulator** | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test*.py'`: **245 tests OK** (240 before the new file; 236 on the lead's count) |
| Generator | V1 | macOS, local | `python3 src/tests/narrative/failure_catches.py`: the shipped definition is the generated one |
| Flow-language gate | Executed | macOS, local | `verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation`: exit 0, checks 1-13 OK, 11 flows |
| Pester | Executed | macOS, local | `NarrativeRedaction.Tests.ps1`: 2 passed, 0 failed |
| Source gates | V1 | macOS, local | `run-source-gates.py config/revitalise-grant-automation-build.yml`: 19/19 PASS (one description first went over 256 chars and was shortened) |

## Findings Logged (Iteration 7)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1109 | `simulator-more-lenient-than-platform` | rework | A test double needs each documented range rule checked against the platform page, one test per boundary, and test data must put entities at both text boundaries |

# Iteration 8 — the client's Anonymisation Key (2026-10-14)

**WBS:** `wbs:5.6` (rules adjusted from the client's input), `wbs:5.1` (the free-text question mapping), `wbs:5.3`
(the flow: **not changed**, see 8.5) · **Date:** 2026-10-14 · **Author:** development-agent, strategic tier ·
**Status:** awaiting code review, and an architecture decision · **Items:** none carried · Nothing deployed, committed or
built. The flow JSON, its notes and `config/revitalise-grant-automation-build.yml` are untouched in this iteration (the
uncommitted Iteration 7 edits to them stand as they were).

## 8.1 Summary

The client's two spreadsheets are now the specification: gendered and relationship words become neutral ones, and the
result must read correctly. The rules, the reference implementation and 24 new tests say exactly what the output must
be. **The flow cannot produce it under the approved architecture**, so this iteration ends in an architecture gap
rather than a flow change. Trustees still see the Iteration 7 output until the architect decides where the new stage runs.

## 8.2 What has been built

1. **The key is the rule, and the old "an unnamed relationship stays" is reversed** —
   [rules 3.2](revitalise-redaction-rules.md#L173), [rules 10.1](revitalise-redaction-rules.md#L554), decision
   [D-5](revitalise-redaction-rules.md#L787). Reviewer, 2026-10-14: *"1. follow the key file"*. "My mum" now becomes
   "my parent", "my husband Derek" becomes "my partner [FAMILY MEMBER]".
2. **The output reads correctly where a replacement breaks it** — [rules 10.1.2](revitalise-redaction-rules.md#L596),
   [`_agree`](../../src/tests/narrative/redaction_reference.py#L1450), [`_her_form`](../../src/tests/narrative/redaction_reference.py#L1435).
   Reviewer: *"2. Yes also add spell checking and auto correct that for readability"*. *She is* becomes *they are*; *her*
   becomes *them* or *their* depending on the next word. Spell-checking the applicant's own words is not built (8.6, item 1).
3. **The specification is executable** — [`neutral_rewrites`](../../src/tests/narrative/redaction_reference.py#L1467),
   [`apply_with_rewrites`](../../src/tests/narrative/redaction_reference.py#L1505),
   [`test_neutral_terms.py`](../../src/tests/narrative/test_neutral_terms.py#L53). Neutral words are found on the source
   text beside the identifier labels, and a neutral word inside a label is dropped. Every change is applied from the end
   of the text, as before.
4. **The client's four examples are tests, without copying their text** —
   [`ClientExamples`](../../src/tests/narrative/test_neutral_terms.py#L277), [rules 10.1.4](revitalise-redaction-rules.md#L617).
   They may be real applications, so the tests read them from the spreadsheet rather than copy them. No key word survives
   in any of the four. Where the oracle's wording differs from the client's, each difference is pinned and given a
   reason. Most are slips like *they is*, and two are first names, which stay `[NAME]`.
5. **The 15 free-text questions are mapped to columns** — [rules 2.1a](revitalise-redaction-rules.md#L121),
   [`FREE_TEXT_QUESTIONS`](../../src/tests/narrative/redaction_reference.py#L1532). Twelve are the twelve columns already
   scrubbed. **Three have no redacted counterpart**: *Benefit provider*, *source of additional funding* and *Awaiting
   decision from*. Adding counterparts is schema work for the architect, and none is built.

## 8.3 Elements added

| Element | Where |
|---|---|
| Rules v0.4: 2.1a, 10.1 (10.1.1 to 10.1.5), D-5, D-6 | [`revitalise-redaction-rules.md`](revitalise-redaction-rules.md#L554) |
| *NEUTRAL TERMS* section: `KEY_ROWS`, `KEY_DEVIATIONS`, `NEUTRAL_TERMS`, `neutral_rewrites`, `apply_with_rewrites`, `redact_and_neutralise`, `gendered_residue`, `FREE_TEXT_QUESTIONS` | [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py#L1309) |
| 24 tests. 4 read the key spreadsheet and 2 read the examples spreadsheet, and each skips if its file is missing (both are committed) | [`test_neutral_terms.py`](../../src/tests/narrative/test_neutral_terms.py) |

## 8.4 Elements changed

| Element | Change |
|---|---|
| Rules 3.2, first bullet | "An unnamed relationship stays" becomes "stays, in a neutral word". The old text is kept as *Previously read* |
| `redact_column`, `merge`, the flow model, the shipped flow | **Unchanged.** The new stage is separate, so the 245 existing tests are still about the flow as it ships |

## 8.5 Why the flow is not changed: the architecture gap

```
CASCADE: ARCH_GAP — TAD ADR-071 item 5 and ADR-072 item 7 let the scrub write only a label from the flow's own map plus source text copied unchanged; the client's key needs neutral words, verb agreement and an inserted "my", which neither the deterministic rebuild nor the prompt (which may supply no text, and is off) is allowed to produce
```

- **Word-for-word substitution would fit the platform.** The flow already finds words at word boundaries for the prompt
  quotes, and a neutral word could be one more entry in the label map. That still means changing what the TAD says a
  label is, because a neutral word has no brackets and a trustee cannot tell it was rewritten.
- **The grammar part does not fit.** Agreeing a verb (*relies* to *rely*) builds new text out of the applicant's own
  word. Choosing *them* or *their* for *her* needs a word list that is a guess, and a second verb after *and* cannot be
  agreed by any word list ([pinned limit](../../src/tests/narrative/test_neutral_terms.py#L179)). In Power Automate
  this is a per-word loop over every window, and nothing like it exists in the approved design.
- **Three designs for the architect, none chosen:** (a) a deterministic neutral-word stage in the flow, accepting a
  stated grammar error rate; (b) the generative prompt rewrites, which reverses `ADR-072` item 7's no-text guarantee
  and is blocked on residency anyway; (c) the C# plug-in `ADR-071` rejected, which needs a language-palette decision.
  Whichever is chosen also needs a review check behind it: [`gendered_residue`](../../src/tests/narrative/redaction_reference.py#L1523)
  is the candidate, with a reason code such as `residual-gendered-term`.

## 8.6 Open questions for the reviewer

The meeting notes behind the key are in Granola, which this session could not open (the connector is not authorised).
Nothing below is taken from the meeting. Each item is a question, and the oracle's current answer is what the tests pin.

1. **General spell-checking is a change-order decision, not built.** It is in no `wbs:5.x` task ([C-COM-002](../../constraints/commercial/commercial-constraints.md#L35)),
   so lead-agent sends it to commercial-agent. For sizing: it changes the applicant's own words, so it needs either the
   prompt stage writing text (design (b) above) or a dictionary component the TAD does not have. Either way it is an
   architecture decision as well as a change order.
2. **Key row 4 says *him* becomes *their*.** The oracle writes *them*, as the client's own examples do. Confirm.
3. **Key row 7 says *hers* becomes *their*.** The oracle writes *theirs*. Confirm.
4. **First names.** The client's examples turn *Ahmad* and *Kizzy* into *They*. The key has no row for names, and FR-026
   says `[NAME]`, so the oracle writes `[NAME]`. Should a name become *They* instead? If so, FR-026 changes.
5. **Plurals and words the key does not list.** The oracle also replaces plurals (*sons* becomes *children*, *women*
   becomes *people*). It leaves alone *grandmother*, *stepson*, *auntie*, *niece*, *nephew*, *mummy*, *lady*, and the titles
   *Mr*, *Mrs*, *Ms* and *Miss* (rules 3.2 keeps titles: "Mrs [NAME]"). Should these be added?
6. **A second verb after *and* stays unagreed** ("they receive PIP and requires care"). Acceptable, or must design (a) be
   ruled out for it?
7. **Example 2 adds a full stop the applicant did not write** ("agony. They soothes"). The oracle does not. That is
   editing, so it falls under item 1.
8. **The two spreadsheets are now in git, and the examples may be real applications.** You committed both in `ffb42ef`
   during this dispatch, so the example tests run in CI. The examples hold first names and health details (dementia,
   PTSD). If they are real, that is personal data in git history, and the test-data rule says none comes from a real
   application ([rules 11.1](revitalise-redaction-rules.md#L659)).
   Please confirm whether they are real or made up. Neither file is listed in
   [`docs/Import/MANIFEST.yml`](../Import/MANIFEST.yml) yet. Adding them is plan-agent's intake step.
9. **Three questions have no redacted counterpart** (8.2, item 5). Two of their columns are not secured. Neither portal
   shows them today, but any role that can read the application table can read them. Should they get counterparts?
10. **SDD wording.** FR-026 lists only bracketed labels. The SDD's business context ([plan line 1189](../plans/revitalise-grant-automation-plan.md#L1189)) already said Emily
   strips "gender references" by hand. An FR-026 amendment would make the SDD say what is now decided.

## 8.7 Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-28 | Key row 34, *"Brief confirmation13"*, is the carer-route question the intake reads as `brief_confirmation_2` into `rev_supportrecipientdisabilityimpactdescription`. If it is a different field, one scrubbed column is not in the client's list and one listed question may have no counterpart | `src/tests/narrative/redaction_reference.py` | E3: the only other *Brief confirmation* in TAD Appendix C is `brief_confirmation`, row 31; "13" matches no key in the 2026-09-25 payload sample | The meeting notes are not available | Ask Emily which form field "Brief confirmation13" is. Either answer is one row in rules 2.1a | OPEN |

## 8.8 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Neutral-term oracle | Executed (specification only, not a platform artefact) | macOS, local | `python3 -m unittest test_neutral_terms` in `src/tests/narrative`: **24 tests OK**, both spreadsheets present |
| Whole narrative suite | V1 for the flow (unchanged) | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test*.py'`: **269 tests OK** (245 before) |
| The tests can fail | Executed | macOS, local | Six mutations, each caught: agreement off (11 failures), *her* always *their* (3), *her* always *them* (3), a rewrite kept inside a label (1), apostrophe not part of a word (3), capitals copied from the source (3) |
| Flow | Not changed | — | 8.5 |

No tool warnings arose. No diagnostic component was created.

## 8.9 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.6 | 2.5 h | Rules 10.1, the oracle stage, 24 tests, the example comparison |
| 5.1 | 0.5 h | Rules 2.1a: 15 questions traced to the intake map and `Entity.xml` |

## Findings Logged (Iteration 8)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1110 | `client-input-reverses-approved-rule` | rework | A rule saying what is deliberately kept must be checked against the SDD's description of today's manual process, not only against the FRs |

---

# Iteration 9 — the flow rebuilt to TAD rev 22 (2026-10-16)

**WBS:** `wbs:5.3` (the flow), `wbs:5.6` (the client's rules, the grammar), `CO-009` (spelling: approved, unbilled; proposed
task 5.8) · **Date:** 2026-10-16 · **Author:** development-agent, strategic tier (`logs/routing.log` 12:09: custom
disclosure controls on special-category text) · **Status:** awaiting code review · **Items:** none carried · Nothing
deployed, built or committed. `config/revitalise-grant-automation-build.yml` and `config/revitalise-grant-automation-pipeline.yml`
are unchanged (this amends the shared configuration; no step added).

**Design:** TAD rev 22, `ADR-075` with its two errata; SDD Amendment A-09 (FR-026 as amended, FR-094 to FR-101, US-025,
OQ-054 to OQ-056). **Two reviewer rulings arrived during this dispatch and are built** (both relayed by lead-agent,
2026-10-16): *"My husband Derek becoms partner. not family member. the word husband is leading in this pattern."* and
*"Keep the family member label for now. I am expecting one more itteration on the labels after Emily has tested."* The SDD
(FR-095, OQ-054) and the TAD (`ADR-075` erratum 2) were corrected the same day by plan-agent and architect-agent.

## 9.1 Summary

The scrub flow is rebuilt, not edited: **313 actions become 90, nesting 8 becomes 5, and there is no `Until` and no
`result()` left.** The extractor labels what it finds, one prompt rewrites the labelled text (the client's key, names to
*They*, the grammar), a second corrects spelling, and three fixed checks decide what is written. **It cannot run yet:** the
two prompts must first be created in DEV by you (decision 1), so do not deploy this build until then.

## 9.2 What has been built

1. **The model never receives a value the extractor found** — [`Select_labelled_pieces`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1197),
   [`labelled_text`](../../src/tests/narrative/redaction_reference.py#L719), [`test_the_model_never_receives_a_value_the_extractor_found`](../../src/tests/narrative/test_scrub_flow_definition.py#L198).
   Each extractor span is replaced by its label and the text rebuilt by offset before the rewrite prompt is called. A span
   inside another is dropped; two that overlap without nesting hold the column ([`Select_overlap_trials`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1164)).
2. **Whatever the models answer, a column is written only when checks P1 and P2 pass** —
   [`Filter_surviving_identifiers`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1410) (P1), [`Filter_added_words`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1431) (P2),
   [`Compose_column_outcome`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1631). P1: no extractor value is left in the final text. P2: every word the rewrite
   wrote was in its input, or on the flow's closed list ([`closed_words`](../../src/tests/narrative/redaction_reference.py#L752)), so a model cannot add a name, a phone
   number or a sentence. Proven against bad stand-in models: [`P2TheRewriteAddsNoWord`](../../src/tests/narrative/test_scrub_flow_definition.py#L227),
   [`P1NoFoundIdentifierSurvives`](../../src/tests/narrative/test_scrub_flow_definition.py#L272).
3. **The spelling answer is taken word by word, never as a whole** — [`Select_spelling_words`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1348),
   [`take_correction`](../../src/tests/narrative/redaction_reference.py#L1036), [`SpellingAcceptedWordByWord`](../../src/tests/narrative/test_scrub_flow_definition.py#L288). A different word count discards it; a capitalised
   word, a label, punctuation, a closed-list word, or a correction that would bring back a gendered word (*sun* to *son*)
   is refused at that word. A failed spelling call writes the rewrite uncorrected, with no reason code.
4. **The client's rules are the oracle, at A-09 and the reviewer's corrections** — [`neutral_rewrite`](../../src/tests/narrative/redaction_reference.py#L1537),
   [`_name_pass`](../../src/tests/narrative/redaction_reference.py#L1442), [`NEUTRAL_TERMS`](../../src/tests/narrative/redaction_reference.py#L1281), [`Names`](../../src/tests/narrative/test_neutral_terms.py#L214), [`UserStory25`](../../src/tests/narrative/test_neutral_terms.py#L283). Names become
   *They* (two different people keep `[NAME]`; *Dr [NAME]* stays); **"my husband Derek" becomes "my partner"**; *him* is
   *them*, *hers* *theirs*, *herself* *themself*; the added words and their counterparts; titles removed; a second verb after
   *and* agrees. Against the client's four examples the only differences left are the client's own grammar slips,
   capitals and *them* for a possessive *her* — no name and no *themself* difference any more.
5. **The label set is in one place, ready for the change after Emily's test** — [`Compose_constants`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L233),
   [`LABEL_BY_CODE`](../../src/tests/narrative/redaction_reference.py#L525), [`test_the_label_set_is_read_from_one_place`](../../src/tests/narrative/test_scrub_flow_definition.py#L620). No other action spells a label; P2's
   closed list must hold every label word; a test fails until flow and oracle agree. `[FAMILY MEMBER]` stays in the set by
   your decision, although no rule now produces it.
6. **One failure handler instead of 16 catch triplets and a failure descent** — [`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2280),
   [`End_the_run_as_failed`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2343), [`TheFailureHandler`](../../src/tests/narrative/test_scrub_flow_definition.py#L488). Any failure inside the scope holds the record,
   alerts once with the run link and ends the run as Failed; a failed extractor or prompt call inside a column is a reason
   code, not a failed run. Tested by making each of 26 actions inside the column fail in turn.
7. **The flow-language gate's selftest no longer depends on action names the rebuild removed** —
   [`_UNTIL_FIXTURE`](../../scripts/verify-flow-definition-language.py#L341),
   [planted check-12 read](../../scripts/verify-flow-definition-language.py#L482). Four selftest assertions went red because
   they mutated the old flow's `Scan_the_column_in_windows` and `Follow_the_failure_inward`; the checks themselves read no
   action names and are unchanged. Now 15 of 15.

## 9.3 Elements added

| Element | Where | WBS |
|---|---|---|
| The rev 22 flow (90 actions) and its maker notes | [flow JSON](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1), [notes](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md) | 5.3, 5.6, CO-009 |
| Rev 22 flow model: `label_spans`, `labelled_text`, `accept_spelling`, `validate_rewrite`, `surviving_identifiers`, `residue_kinds`, `flow_scrub_record` | [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py#L480) | 5.3 |
| Two prompt templates (rewrite; spelling) and the R1 steps | [`revitalise-redaction-prompt.md`](revitalise-redaction-prompt.md) §1–§4 | 5.6, CO-009 |
| `corpus_support.py`: the simulated extractor and the prompt stand-ins | [`corpus_support.py`](../../src/tests/narrative/corpus_support.py) | 5.3 |
| `test_solution_flows.py`: the platform-limit and trigger-loop tests, moved unchanged | [`test_solution_flows.py`](../../src/tests/narrative/test_solution_flows.py) | 5.3 |
| Check-13 selftest fixture | [`verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py#L341) | system |

## 9.4 Elements changed

| Element | Change | WBS |
|---|---|---|
| Flow size | 313 → **90 actions**; nesting 8 → 5; no `Until`, no `result()`. The TAD estimated *about 75–80*: the 10 above it are the threshold parse kept in its own Compose (an expression limit, below), two Selects for the neutral-terms row, the unmapped-type filter, and the separate age Select | 5.3 |
| Neutral-term oracle | Brought to A-09: names to *They*, the corrected relationship rule, `themself`, standalone *his*, added words, second-verb agreement, possessive key words (*my wife's* → *my partner's*) | 5.6 |
| Rules | v0.4 → [v0.5](revitalise-redaction-rules.md): §3, §4.4, §6b–§6c, §7, §7b, §7c, §10.1 rewritten; D-7 and D-8 recorded | 5.6 |
| [`test_scrub_flow_definition.py`](../../src/tests/narrative/test_scrub_flow_definition.py#L1) | Rewritten for rev 22 (52 tests) | 5.3 |
| [`test_neutral_terms.py`](../../src/tests/narrative/test_neutral_terms.py#L1), `test_prompt_component.py`, `test_narrative_test_data.py`, `score_live_run.py` | Brought to rev 22; the rev 20 detector component's own tests stand | 5.3, 5.6 |
| `src/tests/data/narrative-test-data.json` | One `_rev22` note: its expectations are the rev 20 output and are stale (9.5) | 5.3 |
| Removed | `test_flow_model.py`, `failure_catches.py` (the generator of the catches that no longer exist), `test_text_end_spans.py` (its boundary rule is in every new read: `concat(raw, ' ')`) | 5.3 |

**Two gate results worth knowing.** The narrative suite's platform-limit test caught a generated threshold expression of
12,701 characters against the 8,192 limit, which no other gate checks; it is now split. And the `flow-definition-language`
gate passes over the new flow with checks 1 to 13.

## 9.5 What is still open

**The two prompts do not exist yet.** The run actions carry the placeholders `PENDING-A-NS-31-REWRITE-PROMPT-ID` and
`PENDING-A-NS-31-SPELLING-PROMPT-ID`, never an invented id. Imported now, the flow would replace DEV's working rev 20
flow with a Draft that cannot be saved or run (decision 1).

**The seeded test data's expected texts are the rev 20 output.** [`narrative-test-data.json`](../../src/tests/data/narrative-test-data.json)
now says so in a `_rev22` note. In rev 22 the text comes from the model, and TD-14 (10,456 characters) is no longer scrubbed
at all (`too-long`). They are regenerated once the prompts exist, for `wbs:5.7`.

**V2 at most.** The solution packs locally; nothing has been imported, saved in the designer or run. The prompts' quality is `wbs:5.7`'s question;
these tests prove the checks hold against bad answers, not that good answers come back.

**Check P1 is case-blind, as `ADR-075` item 5 states.** A name that is also an ordinary word ("Will"), found once by the
extractor, also stops a column where the word is used as a verb. That column goes to Emily by hand: the safe direction.

## 9.6 Unvalidated Assumptions Register (C-TECH-052)

Rows new in this iteration, and the current status of earlier rows the rebuild touches. Rows not listed stand as written.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| ~~A-NS-31~~ | The two prompt components (rewrite: inputs `Narrative`, `ExtraTerms`; spelling: input `Text`) export and import with the solution in the same shape as the rev 20 one, and each run action passes its inputs by these names and reads `text` and `finishReason` at `responsev2/predictionOutput`. If not, every call fails and every column is `prompt-error` (held, nothing written) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E1 for one prompt's shape and run action (DEV export and designer save, 2026-10-07); E3 for the two new ones | They do not exist; creating them is your R1 | R1, then export and unpack: replace the two placeholders with the exported ids; read the run specifications | CLOSED — VERIFIED 2026-10-16 by the DEV export (10.10) |
| A-NS-33 | One rewrite call on a 5,000-character labelled text returns the whole text with `finishReason` `stop`. If it is cut off, the finish reason is not `stop` and the column is `prompt-error` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No prompt exists | One DEV run on a synthetic 5,000-character text | OPEN |
| A-NS-34 | An action that runs after a FAILED connector call can read its `body()`, and the answer path on it is null, so the column becomes `ai-error` or `prompt-error`. If the platform instead throws, that Compose fails, the run fails and the record is held (the safe direction) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (the rev 20 register read used the same pattern; never seen to fail) | No run | One DEV run with the extractor failing (for example no AI credits on a test environment): the run Succeeds and the record shows `ai-error` | OPEN |
| A-NS-35 | `replace()` is case-sensitive, so the spelling rule's "starts with a lower-case letter" and "keeps its first letter" tests are exact. If it were not, a capitalised word could be corrected | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (the function reference states it) | No run | One DEV test `Compose`: `length(replace('abc', 'A', ''))` is 3 | OPEN |
| A-NS-8 | Revised: a completed run of either new prompt returns `finishReason` `stop`; any other value is unusable (rewrite: `prompt-error`; spelling: the rewrite stands) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No prompt exists | As A-NS-33 | OPEN |
| A-NS-15 | Revised: `sort(array, 'start')` and `sort(array, 'score')` sort ascending by that number (the rebuild and the lowest score) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 | No run | One DEV test `Compose` over `[{start:10},{start:2}]` | OPEN |
| A-NS-12 | Unchanged claim, still in source: `secureData` on the extractor and on both prompt calls hides their inputs and outputs in run history | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No run | As before | OPEN |
| A-NS-22 | Unchanged claim, still in source (`Filter_settings_saved_after_auto_release`) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | No run | As before | OPEN |
| A-NS-9 | The rev 20 detector prompt's run action. **No longer called**; its component stays in the solution (decision 2), and A-NS-31 replaces this row for the new prompts | — | — | — | — | WITHDRAWN |
| A-NS-10 | The detector prompt's JSON answer. The new prompts answer plain text | — | — | — | — | WITHDRAWN |
| A-NS-18 | `take()`/`lastIndexOf()` for windows. No windows any more | — | — | — | — | WITHDRAWN |
| A-NS-19 | `result()` of a loop. The flow has no `result()` | — | — | — | — | WITHDRAWN |
| A-NS-20 | The detector prompt's three inputs and their length. Replaced by A-NS-31 and A-NS-33 | — | — | — | — | WITHDRAWN |
| A-NS-23 | Creating a prompt with *Move data across regions* off. The setting is on in DEV, TST/ACC and PRD (reviewer statements, 2026-10-16; TAD `A-NS-32a`) | — | — | — | — | WITHDRAWN |
| A-NS-24 | `split()` occurrences for prompt quotes. Quote validation is gone | — | — | — | — | WITHDRAWN |
| A-NS-26 | Nesting 8 deep. The flow nests 5 | — | — | — | — | WITHDRAWN |
| A-NS-27 | The `int()` rethrows. They are gone | — | — | — | — | WITHDRAWN |

TAD `A-NS-29` (an array read by a computed index) does not apply: every such read is `first(skip(…))`.

## 9.7 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic | **V1, simulator** with stand-in prompts | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test*.py'`: **170 tests OK** (269 before; most covered removed stages, ADR-075's gate table) |
| The tests can fail | Executed | macOS, local | Seven mutations of the flow, each caught: P2 removed from the write (13 failures), P1 removed (6), the spelling answer taken whole (4), the gendered-word refusal removed (1), the raw text sent to the model (86 failures and errors), `secureData` dropped from one Select (1), contained spans kept (12) |
| Flow-language gate | Executed | macOS, local | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation`: exit 0, checks 1–13, 11 flows, 0 Until loops. `--selftest`: exit 0, wrapper 15/15 |
| Pester wrapper | Executed | macOS, local | `NarrativeRedaction.Tests.ps1`: 2 passed, 0 failed |
| Source gates | V1 | macOS, local | `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml`: 19 of 19 PASS (second run in the gate output) |
| Pack | **V2** | macOS, local, pac CLI | `pac solution pack --packagetype Unmanaged` to a scratch folder: exit 0, no warning; the packed flow is 104,013 bytes (the rev 20 one was 344,007) and still carries the two `A-NS-31` placeholders |

**V3 to V5 are not reached.** Nothing was imported, saved or run; the pack was to a scratch folder and is not a build artefact. No tool warning was emitted by any command above.
No live call was made in this dispatch, so no diagnostic component exists.

## 9.8 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 5.5 h | The rebuilt flow, the flow model, 52 flow tests, the stand-ins, the notes |
| 5.6 | 2.0 h | The neutral-term oracle to A-09 and the two corrections, rules v0.5, the rewrite template |
| CO-009 | 1.0 h | The spelling prompt, its template and the word-by-word acceptance with its tests |
| system | 0.5 h | The gate selftest fixtures, two findings |

## 9.9 What you need to decide

**Create the two prompts in DEV before this build is deployed (TAD §12.6.1 R1)**

**Problem** — the flow calls two prompts that do not exist, so its run actions carry placeholders.
**Suggested fix** — follow [section 3 of the prompt document](revitalise-redaction-prompt.md); development-agent then exports them and replaces the placeholders.
**What happens if you don't** — a deploy replaces DEV's working flow with one that cannot be saved or run, and no record is scrubbed until the ids are in.
[`Run_the_rewrite_prompt`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1235)

---

**Remove or re-use the rev 20 detector prompt**

**Problem** — *REV Narrative Redaction Prompt* is still a component of the solution, and nothing calls it.
**Suggested fix** — remove it from the solution when the two new prompts are copied in; re-using it as the rewrite prompt is also possible, but its inputs differ.
**What happens if you don't** — it ships, unused, to TST/ACC and PRD.
[prompt document §5](revitalise-redaction-prompt.md)

---

**Confirm two readings of `ADR-075` this build made**

**Problem** — (a) item 6's closed list does not include *a* and *an*, which "an uncle" → "a relative" needs; I added them. (b) The TAD retires the *practice suffixes* list, while item 2 says entities map "as now"; I kept the fixed suffix list in the flow and retired only the setting row.
**Suggested fix** — confirm both, or say which to change (each is one constant and a test).
**What happens if you don't** — nothing breaks: neither can disclose anything; (a) otherwise holds such columns as `rewrite-invalid`, (b) otherwise sends every organisation's name to the prompt unlabelled.
[`closed_words`](../../src/tests/narrative/redaction_reference.py#L752)

---

Verification: 170 narrative tests, 0 failures; seven flow mutations each caught; flow-language gate and its selftest green; 19 of 19 source gates; a local pack (V2) with no warning.
**Not verified:** any import, designer save or run (V3–V5), and the two prompts, which do not exist yet.

## Findings Logged (Iteration 9)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1121](../../logs/improvement-log.jsonl) | `gate-fired` | friction | An expression that needs one intermediate value more than twice gets that value in its own Compose; only the narrative suite checks the 8,192 limit |
| [IMP-1122](../../logs/improvement-log.jsonl) | `gate-proof-bound-to-live-artefact` | friction | A gate's selftest mutates a fixture it owns, never a live flow's action names; and a selftest no build runs proves nothing |
| IMP-1098 (existing) | — | blocker, `fixed_in_flight` re-stamped | Its evidence needle named an action the rebuild removed; re-stamped to the rev 22 shape, which has no reference into the loop at all |

---

# Iteration 10 — the rewrite rules move to settings (TAD rev 23, 2026-10-16)

**WBS:** `wbs:5.6` (rules the process owner tunes), `wbs:5.3` (the flow) · **Date:** 2026-10-16 · **Author:**
development-agent, strategic tier (same transcript as Iteration 9) · **Status:** awaiting code review · **Items:** none
carried · Nothing deployed, built, exported or committed. **Design:** TAD rev 23, `ADR-076`, approved 2026-10-16 (*"Approved
for revision 23"*). It answers the reviewer's correction of approved Iteration 9: *"I noticed in the rewrite prompt there are
quite some rules in there. We agreed that those rules would be set as settings on the settings table. So that Emily can
change these without me changing the prompts or workflows."* Iteration 9 stays approved; this changes it as the ADR's table
lists. This amends the shared build configuration (no step added); the pipeline configuration changes only in three step
descriptions.

## 10.1 Summary

The key, the titles, the name rules and the labels now live in four `rev_setting` rows Emily edits. The rewrite prompt reads
them as four inputs, and **the same rows are the lists checks P2 and P3 use**, derived in one action, so the prompt and the
checks cannot drift apart. A missing or malformed row stops the scrub of the record and names the row. The deploy creates
the four rows once in each environment and never overwrites them. **Waiting on you:** the R1b re-edit of the rewrite prompt in
DEV (decision 1), then the export.

## 10.2 What has been built

1. **Four rows feed the prompt and the checks from one place** — [`Compose_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L811),
   [`run_context`](../../src/tests/narrative/redaction_reference.py#L1037), [`test_the_four_prompt_inputs_are_the_rows_as_written`](../../src/tests/narrative/test_scrub_flow_definition.py#L498).
   `Compose_settings` turns the validated rows into the prompt's `NeutralTerms`, `Titles`, `NameRules` and `Labels`, P2's
   allowed words (the right side of each key line, the words of each label) and P3's gendered words and titles. The flow
   keeps fixed only what no rule chooses: the extractor's labels and the grammar set (*are, were, have, do, go*, their
   *-n't* forms, *my, a, an*).
2. **Every row fails closed** — [`Select_neutral_term_lines`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L736),
   [`Filter_neutral_targets_that_are_terms`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L762), [`Select_title_lines`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L775),
   [`Select_label_lines`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L788), [`Filter_columns_to_scrub`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L911), [`RuleRows`](../../src/tests/narrative/test_scrub_flow_definition.py#L498). Absent, blank, a line
   without one `=`, a neutral word that is also a word to replace, a title over 10 letters, a label not in capitals: each gives
   `redaction-setting-invalid:<key>`, and no extractor or prompt call is made for the record. `none` is an intended empty list.
3. **A title is its own residue check, with its capitals** — [`Filter_residue_titles`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1610). *Ms Smith* is held, *MS*
   (the condition) is not. It uses `replace()`, which is case-sensitive, not `contains()`, so it holds under either string
   semantics: the tests run both (TAD `A-NS-37` does not arise).
4. **The deploy seeds the rows once and then leaves them alone** — [`seed-settings.ps1`](../../provisioning/dataverse/seed-settings.ps1#L224),
   [the seeded rows](../../provisioning/deploymentSettings/test-settings.json#L617),
   [create-only tests](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L298). A row marked `createOnly` that exists is
   reported `EXISTS — left unchanged` and never written; an absent one is created with `If-None-Match: *`, so a row made in
   the meantime is refused by Dataverse instead of overwritten. The seed values are TAD `ADR-076`'s, held once in
   [`SEED_ROWS`](../../src/tests/narrative/redaction_reference.py#L1329) and asserted equal in all three settings files.
5. **The rewrite template is the fixed contract only, with four slots** — [prompt document §1](revitalise-redaction-prompt.md#L13),
   [R1b steps](revitalise-redaction-prompt.md#L87). The spelling prompt is unchanged.

## 10.3 Elements added

| Element | Where | WBS |
|---|---|---|
| Four `Find_setting_*` reads (three more), `Select_neutral_term_lines`, `Filter_neutral_targets_that_are_terms`, `Select_title_lines`, `Select_label_lines`, `Filter_residue_titles` | flow JSON | 5.3, 5.6 |
| `parse_neutral_terms`, `parse_titles`, `parse_labels`, `parse_name_rules`, `SEED_ROWS`, `SEED_CONTEXT` | [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py#L925) | 5.6 |
| Four `createOnly` rows | `dev-scoring-settings.json`, `test-settings.json`, `prd-settings.json` | 5.6 |
| Create-only mode (`-ExtraHeaders` on `Invoke-DataverseApi` was added here and removed again in 10.11) | `seed-settings.ps1`, `provisioning-common.ps1` | 5.6 |
| 9 flow tests (`RuleRows` and two others), 1 seed-equality test, 3 Pester tests | test files above | 5.3, 5.6 |
| Reason code `residual-title:<column>` | flow, rules §6b | 5.6 |

## 10.4 Elements changed

| Element | Change | WBS |
|---|---|---|
| Flow size | 90 → **97 actions**, nesting still 5. The TAD estimated about 95: the extra two are the neutral-word cross-check and the labels row's validation | 5.3 |
| `Compose_constants` | Keeps only the grammar set and the extractor's label words in `closedWords`; `genderedWords` removed | 5.3 |
| `Run_the_rewrite_prompt` | `ExtraTerms` → `NeutralTerms`, `Titles`, `NameRules`, `Labels` | 5.3 |
| `RedactionNeutralTermsExtra` | Retired; a leftover row is ignored | 5.6 |
| Oracle | `neutral_rewrite` takes the rows (the stand-in model follows the rows it is given); `NEUTRAL_TERMS` gains *mummies*, *daddies* | 5.6 |
| Rules | v0.5 → v0.6: §6b, §7c, §10.1 | 5.6 |
| Prompt document | §1 rewritten (rev 23 template, R1b); §3 marked done; §4 waits for R1b | 5.6 |
| Pipeline config | Three seed step descriptions: the four create-only rows; "36 rows" corrected to 40 | 5.6 |

## 10.5 What is still open

**The rewrite prompt in DEV is the rev 22 one.** Until R1b, its inputs (`Narrative`, `ExtraTerms`) do not match the flow's.
Do not export before R1b (prompt document §4 step 0).

**Before the first deploy that seeds the rows, every record is held** with `redaction-setting-invalid` for all four rows
(`ADR-076` consequence 6). The deploy itself creates them, so this lasts only from the import to the end of that deploy's
post-deploy steps.

**The pipeline preflight is red for reasons outside this change.** `verify-pipeline-config.py` reports four DEV steps whose
`blocked_on` notes are 15 to 17 days old (limit 14). It reports the same four on the tree without this iteration's edits.
They are pipeline-agent's to re-test.

## 10.6 Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-36 | A keyed `PATCH` with `If-None-Match: *` creates a missing `rev_setting` row and returns 412 for an existing one, changing nothing. If it updated instead, the first deploy after a race could overwrite one of Emily's rows; the probe before it already skips every existing row | `provisioning/dataverse/seed-settings.ps1` | E2 (Dataverse Web API, upsert with update prevented) | No live run in this dispatch | In DEV: run the create-only seed twice, editing one row by hand between runs; the second run reports `EXISTS — left unchanged` and the edit stays | OPEN |
| A-NS-35 | Revised: `replace()` is case-sensitive; the spelling rule and now the title check rely on it | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 | No run | As before; and a run on "I have MS" is not held for a title | OPEN |
| ~~A-NS-31~~ | Revised: the rewrite prompt's inputs are now `Narrative`, `NeutralTerms`, `Titles`, `NameRules`, `Labels` (after R1b); the spelling prompt's `Text` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 | R1b not done | R1b, then export and read the run specification | CLOSED — VERIFIED 2026-10-16 by the DEV export (10.10) |

TAD `A-NS-37` (`contains()` case-sensitive) is not relied on: the title check uses `replace()`.

## 10.7 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic | V1, simulator | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test*.py'`: **180 tests OK** (170 in Iteration 9) |
| The tests can fail | Executed | macOS, local | 13 flow mutations, each caught: Iteration 9's seven, plus the rule-row gate removed from `Filter_columns_to_scrub` (28 failures), the title check emptied (4), P2's list ignoring the rows (62 + 1 error), the prompt's `NeutralTerms` not from the row (52), the gendered list not from the row (2), the neutral-word cross-check off (1) |
| Seed script | Executed (mocked Web API) | macOS, pwsh 7, Pester 5.7.1 | `DataverseScripts.Tests.ps1`, `DeploymentSettings.Tests.ps1`, `ProvisioningCommon.Tests.ps1`, `ScriptContract.Tests.ps1`, `NarrativeRedaction.Tests.ps1`: **635 passed, 0 failed, 1 skipped** |
| Flow-language gate | Executed | macOS, local | exit 0, checks 1–13 |
| Pack | **V2** | macOS, pac CLI | `pac solution pack --packagetype Unmanaged` to a scratch folder: exit 0, no warning |

**V3 to V5 are not reached**, and the seed script has not run against any environment. No tool warning was emitted. No live
call was made, so no diagnostic component exists.

## 10.8 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.6 | 2.0 h | The four rows: parsing, guard rails, seed values in three files, the create-only seed and its tests, rules v0.6, the rev 23 template |
| 5.3 | 1.5 h | The flow changes, 9 flow tests, six new mutations, notes |
| system | 0.25 h | Two findings |

## 10.9 What you need to decide

**Re-edit the rewrite prompt in DEV (R1b)**

**Problem** — the rewrite prompt in DEV still has the rev 22 template and its `ExtraTerms` input, which the flow no longer passes.
**Suggested fix** — follow [R1b](revitalise-redaction-prompt.md#L87) (remove `ExtraTerms`, add four inputs, paste the rev 23 template); then development-agent exports both prompts.
**What happens if you don't** — the export copies the wrong prompt and every rewrite call fails, so every column is `prompt-error` and nothing is written.
[`Run_the_rewrite_prompt`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1210)

---

Verification: 180 narrative tests and 635 Pester tests, 0 failures; 13 flow mutations each caught; flow-language gate green;
19 of 19 source gates; a local pack (V2) with no warning. **Not verified:** any import, designer save or run (V3–V5), and the
create-only seed against a real environment (`A-NS-36`).

## Findings Logged (Iteration 10)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1126](../../logs/improvement-log.jsonl) | `shared-working-tree-mutated-to-measure-a-baseline` | friction | While another dispatch may be writing the tree, never `git stash` to measure a baseline; use `git show` to a copy, or a separate worktree |
| [IMP-1127](../../logs/improvement-log.jsonl) | `hand-maintained-count-drifts-from-source` | friction | A pipeline step description names what it seeds, not how many rows |

## 10.10 Addendum — the two prompts exported and copied in (2026-10-16)

**R1b is done** (reviewer, verbatim: *"ok prompt is edited and saved."*); the spelling prompt was not changed. This addendum
does the prompt document §4 steps. Nothing deployed or committed; the rev 20 detector component is left in place.

1. **Both components are now in source, exactly as exported** — [`Customizations.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/Customizations.xml#L72),
   [what the export showed](revitalise-redaction-prompt.md#L172), [`TheTwoNewComponents`](../../src/tests/narrative/test_prompt_component.py#L194).
   A read-only `pac solution export` of `RevitaliseGrantAutomation` from DEV (14:37 UTC), unpacked to a scratch folder.
   The two `AIModel` elements and their two `RootComponent type="401"` rows are copied unchanged; the rev 20 component in the
   export is byte-identical to the one in source. The configurations are not newer than the export (`IMP-1088`): rewrite
   14:36, spelling 11:51.
2. **The flow names the exported ids** — the placeholders are replaced by `e853d7c8-dd36-4917-951f-50108a812fc4` (rewrite)
   and `763cff31-d653-416b-a52f-7e6f400bce21` (spelling), each once.
3. **Every input and output matches** — the decoded run specifications require exactly `Narrative`, `NeutralTerms`,
   `Titles`, `NameRules`, `Labels` (rewrite) and `Text` (spelling), and return `text` and `finishReason`. Each also has the
   prompt builder's optional `additionalContext`, as the rev 20 prompt does; the flow does not pass it. GPT-4.1 mini,
   temperature 0, moderation Low, output text.
4. **The template you typed is word for word the document's** — the only differences are the prompt builder's: a space each
   side of every input token, and one newline at the end. The test pins exactly that, so any other change fails.
5. **One gate false positive, fixed** — [`LEGACY_SHAPE_TOKEN`](../../scripts/verify-guid-syntax.py#L220). The GUID gate's
   backstop scan read the exported JSON `{"type":"inputVariable","id":"Labels"}` (and `Titles`) as a malformed GUID,
   because six-letter names make it exactly 36 characters. It now ignores a token with a double quote; the known-bad fixture
   still fails. The engine's copy needs the same line (finding below).

**`A-NS-31` is closed:**

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-31 | The two prompt components export with the solution in the same shape as the rev 20 one, and each run action passes its inputs by the exported names and reads `text` and `finishReason` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | **E1**: DEV export of 2026-10-16, run specifications decoded; the answer path is the designer-saved one (E1, 2026-10-07) | — | — | CLOSED — VERIFIED (export, 2026-10-16) |

**Still open:** the import (V3) and a designer open-and-save (V4) of the flow with the new ids; a DEV run of each prompt
(`A-NS-8`, `A-NS-33`); the create-only seed against DEV (`A-NS-36`). **Outside this change:** the
`verify-pipeline-config` CI test (`BuildGates.Tests.ps1`) fails on the four stale DEV `blocked_on` notes of 10.5.

**Verification (this addendum):** 184 narrative tests OK (180 before; 4 new component tests); Pester `BuildGates`,
`NarrativeRedaction`, `DataverseScripts`, `DeploymentSettings`: 254 passed, 1 failed (the stale-note test above), 1 skipped;
19 of 19 source gates; managed and unmanaged packs exit 0 with no warning (V2). One live read: the export and a `pac env
fetch` of `msdyn_aiconfiguration`, both read-only.

**Hours:** 5.3, 0.75 h (export, copy, tests, documents); system, 0.25 h (the GUID scan fix and its finding).

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1128](../../logs/improvement-log.jsonl) | `gate-fires-on-nothing` | friction | A length-only GUID shape scan matches exported prompt JSON by coincidence; exclude characters no GUID contains |

## 10.11 Addendum — the create-only seed failed in DEV, and is fixed (2026-10-16)

**What happened.** You ran `pwsh -NoProfile -File provisioning/dataverse/seed-settings.ps1 -Env dev` (PowerShell 7.6.7,
macOS). The four create-only rows failed with `{"error":{"code":"0x80060891","message":"A record with the specified key
values does not exist in rev_setting entity"}}`. Nothing was written for them; the other rows were unaffected.

1. **The cause is the create call, not the 404 check** — [the create path](../../provisioning/dataverse/seed-settings.ps1#L253).
   I measured what pwsh 7.6.7 throws for that exact 404 (a local server returning DEV's body):
   `Microsoft.PowerShell.Commands.HttpResponseException`, `Response.StatusCode` 404. The script reads that correctly, and the
   same path has created rows in DEV before. So the probe found the rows absent, and it was the create that failed: a
   keyed `PATCH` with `If-None-Match: *` through the alternate key, which Dataverse answered 404 instead of creating
   (`A-NS-36` is wrong).
2. **The create is now a `POST` to the entity set** — it can only create, so it cannot overwrite your row either. If the
   POST is refused, the script looks again: a row that exists now is `EXISTS — left unchanged (createOnly; created
   meanwhile)`; otherwise the run fails with the POST's own error. `-ExtraHeaders` is removed from `Invoke-DataverseApi`
   again.
3. **A test now throws the real exception** — [`createOnly: with the REAL pwsh 7 exception …`](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L346).
   It builds the measured `HttpResponseException` with a 404, instead of the harness's own error object, and checks the row
   is created by `POST`. Two more tests check: no keyed `PATCH` and no `If-None-Match` on a create; a refused POST is EXISTS
   when the row is there and FAILED when it is not.

**Re-run, for you** (same shell, `PROVISION_APP_ID` and `PROVISION_CERT_THUMBPRINT` exported):

```bash
pwsh -NoProfile -File provisioning/dataverse/seed-settings.ps1 -Env dev
```

Expected: `CREATED — Setting row 'RedactionNeutralTerms'`, `'RedactionTitles'`, `'RedactionNameRules'`, `'RedactionLabels'`;
every other row `EXISTS — value upserted`; exit 0. A second run should report the four as `EXISTS — left unchanged
(createOnly)`, which closes `A-NS-38`. Check afterwards (read-only):

```bash
pac env fetch --xml "<fetch><entity name='rev_setting'><attribute name='rev_name'/><attribute name='modifiedon'/><filter><condition attribute='rev_name' operator='like' value='Redaction%'/></filter></entity></fetch>"
```

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| ~~A-NS-36~~ | A keyed `PATCH` with `If-None-Match: *` creates a missing `rev_setting` row | — | **Wrong**: answered 404 / 0x80060891 in DEV for all four rows (your run, 2026-10-16) | — | — | CLOSED — WRONG (DEV run, 2026-10-16) |
| A-NS-38 | A `POST` to `rev_settings` creates a missing row, and is refused when a row with the same `rev_name` exists (the alternate key `rev_setting_name`), so a create-only row is never overwritten. If the second half is wrong, a race could create a duplicate name, which the alternate key forbids | `provisioning/dataverse/seed-settings.ps1` | E2 (Dataverse create; alternate keys are unique). The create half is how every other script here creates rows | No DEV write by an agent | Your re-run above, then a second run: CREATED then EXISTS | OPEN |

**Files changed after 16:58** (so the build's result can be read as provisional for them):
`provisioning/dataverse/seed-settings.ps1`, `provisioning/common/provisioning-common.ps1` (the `-ExtraHeaders` removal),
`src/tests/provisioning/DataverseScripts.Tests.ps1`, this document, `logs/improvement-log.jsonl` and the regenerated
`logs/known-failure-modes.md` / `-appendix.md`. No flow, solution or settings file changed. The TAD's `A-NS-36` row is
architect-agent's to mark wrong.

**Verification:** Pester `DataverseScripts`, `DeploymentSettings`, `ProvisioningCommon`, `ScriptContract`: 634 passed, 0
failed, 1 skipped (12 seed-settings tests, 4 create-only). The real exception shape was measured locally; nothing was sent
to DEV in this addendum. **Hours:** 5.6, 0.75 h.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1131](../../logs/improvement-log.jsonl) | `platform-contract-guessed-not-groundtruthed` | rework | A create-only Dataverse write is a POST to the entity set; If-None-Match on an alternate-key PATCH was answered 404 here |

## 10.12 Addendum — test report 20261016-3, defect D-1: the writes now hide the row they return (2026-10-16)

**What test-agent found** ([test report, D-1](../tests/revitalise-grant-automation-test-report-20261016-3.md)): the 12
counterpart writes secured their inputs only, and `Write_the_decision` and `Hold_the_record_for_review` secured nothing.
"Update a row" returns the updated row, the flow's identity can read the 12 raw narratives, so a run would have kept them in
run history for 28 days, outside column security (`C-DOM-004`). The run-history test missed it because its write stand-in
returned nothing. The rev 20 flow had the same gap.

1. **All 14 writes hide inputs and outputs** — [`Write_rev_narrativeredacted`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1696) and its 11 siblings,
   [`Write_the_decision`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2184), [`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2300). Only `runtimeConfiguration` and the
   description changed on those 14 actions; no other action changed, and the flow is still 97 actions.
2. **The test double now returns the row, as the connector does** — [the write stand-in](../../src/tests/narrative/test_scrub_flow_definition.py#L135). With it, the canary
   run-history test fails on the old flow: removing `outputs` from one counterpart write, from the decision write, or from the
   hold each makes it fail (3 mutations, each caught).
3. **A static test covers the same property** — [`test_every_dataverse_read_and_write_of_the_application_is_secured_both_ways`](../../src/tests/narrative/test_scrub_flow_definition.py#L696).
   All 15 actions on `rev_applications` hide their outputs; the 14 writes also hide their inputs.

**Every action that receives or returns narrative-bearing data, checked:**

| Action | What it carries | Secured |
|---|---|---|
| Trigger `When_an_application_status_changes` | the changed row | outputs (unchanged) |
| `Get_the_application` | returns the row: 12 raw narratives | outputs (its inputs are ids only) |
| `Extract_entities_from_the_column` | the raw column in, entity values out | inputs and outputs |
| `Run_the_rewrite_prompt`, `Run_the_spelling_prompt` | the labelled text and the rewrite | inputs and outputs |
| 12 × `Write_rev_*redacted` | the written text in, **the row out** | inputs and outputs (**was inputs only**) |
| `Write_the_decision`, `Hold_the_record_for_review` | flags in, **the row out** | inputs and outputs (**was nothing**) |
| `Read_redaction_settings`, `List_postcode_districts` | `rev_setting` rows (synthetic rules only, `A-R87`) and outward codes | not secured: no narrative |
| `Tell_the_process_owner_card`, `Tell_the_process_owner`, `Alert_on_failure` | the reference, reason codes, the run link | not secured: no narrative (tested) |
| Every Compose, Select and Filter that sees text (25) | text or entity values | secured; checked by the canary run, which now also reads every write's returned row |

The canary run checks the whole list dynamically: every action record, both ways, under a normal run and a failed write.

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-39 | An `UpdateOnlyRecord` on `rev_applications` returns the updated row, including columns it did not write, and `secureData` on its outputs hides that row in run history. If the outputs are not secured, a maker reading the run sees the raw narratives | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (connector reference: "Update a row" returns the row; test report D-1); the intake flow secures both sides of its writes | No DEV run | One DEV run on synthetic data: open a `Write_rev_*` action in run history and see *secured* on both panes | OPEN |

**Not changed:** the spelling rule (test report O-1 waits for the reviewer).

**Verification:** narrative suite 185 tests OK (184 before; 1 new static test; the stand-in change makes the existing canary
test able to fail); 3 mutations caught; flow-language gate, source gates, pack — see the gate output. **Hours:** 5.3,
0.5 h.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1136](../../logs/improvement-log.jsonl) | `simulator-more-lenient-than-platform` | rework | A Dataverse write returns the row: secure its outputs, and make every test double return what the connector returns |

---

# Iteration 11 — name fragments, name rules and punctuation (2026-10-19)

**WBS:** `wbs:5.3` (the flow), `wbs:5.6` (the client's rules, the `RedactionNameRules` row) · **Date:** 2026-10-19 ·
**Author:** development-agent · **Status:** awaiting code review · **Items:** none carried · Nothing built, deployed,
exported or committed; no write to any environment. **Authority:** reviewer, 2026-10-19, verbatim: *"Yes please, process the
suggested changes"* (relayed by lead-agent with the DEV evidence below). This amends the shared build configuration: no step
added, no step changed. The pipeline configuration is unchanged.

**Evidence it answers** (lead-agent, `pac env fetch` of DEV, 2026-10-19, on the seeded synthetic cases TD-13 to TD-15 of
[`narrative-test-data.json`](../../src/tests/data/narrative-test-data.json); no real applicant text): *"My name is they-Reed"*;
*"they at [GP PRACTICE] reviews"* for *"Dr Adeyemi at …"*; *"Our child [NAME] who is …"*; *"I am they"* twice; full stops and
commas missing in five columns.

## 11.1 Summary

A surname fragment reached a trustee-facing column, and no check saw it. It now cannot: a name is labelled whole when the
extractor finds only part of it, and anything still joined to a label holds the record. *Dr* stays outside the label, the
name rules now say what to do with the writer's own name and which rule wins, and a rewrite that drops punctuation is held.
**Waiting on you:** a maker edit of one settings row in DEV (decision 1), and whether to try the one-clause prompt change
for punctuation (decision 2).

## 11.2 What has been built

1. **A name is labelled whole when the extractor finds only part of it** — [`Select_entity_ages`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1078),
   [`Select_spans`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1111), [`all_spans`](../../src/tests/narrative/redaction_reference.py#L739),
   [`NameFragments`](../../src/tests/narrative/test_scrub_flow_definition.py#L511).
   A person's name span now takes in one fragment joined to it on each side: a hyphen and letters after it (*Holloway-Reed*),
   an apostrophe and two or more letters after it, or letters and a hyphen or apostrophe before it (*O'Brien*, *Mary-Ann*).
   The possessive *'s* is never taken in, so *[NAME]'s* still reads as a possessive. With the DEV extractor answer for TD-13
   the rewrite now receives *"My name is [NAME] and …"*, and *Reed* is in no prompt input and no written column.
2. **Anything still joined to a label holds the record** — [`Filter_spans_with_a_joined_fragment`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1675),
   [`Compose_column_outcome`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1696), [`joined_spans`](../../src/tests/narrative/redaction_reference.py#L753), [`final_joint`](../../src/tests/narrative/redaction_reference.py#L763).
   New residue reason `residual-name-fragment:<column>`: written and held, like every residue. It looks in two places: the
   column before labelling (any label, so a second fragment such as *Smith-Jones-Brown* or *[PHONE]-ext* is caught), and the
   final text (so a model that writes *[NAME]-Reed* is caught). The first is the one that matters for DEV's case, because the
   model turned *[NAME]-Reed* into *they-Reed*, which has no label left to look next to.
3. **"Dr" stays outside the label** — same two actions, field `trim`; [`test_a_dr_title_stays_outside_the_label`](../../src/tests/narrative/test_scrub_flow_definition.py#L565).
   A name span that starts with *Dr*, *Dr.* or *Doctor* is shortened past it, so the prompt sees *Dr [NAME]* and its "keep
   [NAME] after Dr" rule can apply. The DEV output fits the extractor having included *Dr* in the name: the title disappeared
   and the prompt applied its one-person rule. That cannot be confirmed from DEV, because the extractor's answer is secured in
   run history; the trim makes the result the same either way.
4. **The name rules say which rule wins, and cover the writer's own name** — [seed value](../../src/tests/narrative/redaction_reference.py#L1434),
   [`dev-scoring-settings.json`](../../provisioning/deploymentSettings/dev-scoring-settings.json#L313), [`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json#L633),
   [`prd-settings.json`](../../provisioning/deploymentSettings/prd-settings.json#L693), [`_name_pass`](../../src/tests/narrative/redaction_reference.py#L1691).
   The row now lists its rules in the order they apply: the writer's own name keeps `[NAME]`; *Dr [NAME]* stays; a name
   straight after a relationship word goes **even when other people are named** (the old order let "two or more people"
   win, which is why *Our child [NAME]* kept the name); then two or more people; then *they*. Each rule has a worked
   example written with labels only. The expected-output model the tests use follows the same order, so the tests no longer
   pin the old one.
5. **A rewrite that drops punctuation is held** — [`Compose_check_texts`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1406),
   [`dropped_punctuation`](../../src/tests/narrative/redaction_reference.py#L1237), [`PunctuationFidelity`](../../src/tests/narrative/test_scrub_flow_definition.py#L579).
   The flow cannot lose punctuation itself: the labelled text copies everything between labels, and a spelling correction is
   taken only when it keeps the word's end punctuation ([`Select_spelling_words`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1368)). So the rewrite model
   dropped it. New fidelity reason `rewrite-dropped-punctuation:<column>`: written and held when the rewrite has at least two
   fewer of `. , ; : ! ?` than its input and more than 10% fewer. One mark fewer is not held, so removing a title written *Mr.*
   does not hold a record. The cure is in the prompt (decision 2).
6. **The DEV cases are tests** — [`SeededCasesSeenInDev`](../../src/tests/narrative/test_scrub_flow_definition.py#L598), [`Names`](../../src/tests/narrative/test_neutral_terms.py#L251).
   TD-13 and TD-15's own text, with the extractor answers the DEV output implies, run through the shipped flow: no *Reed*
   anywhere, *Dr [NAME] at [GP PRACTICE] reviews …*, *Our child, who is [AGE 35 to 44], …*, and *I am [NAME] and since my
   stroke …*. The expectations in `narrative-test-data.json` are not regenerated (`wbs:5.7` owns that).

## 11.3 Elements added

| Element | Where | WBS |
|---|---|---|
| `Select_raw_classes`, `Compose_raw_classes` (the column's letters as `A`), `Filter_spans_with_a_joined_fragment` | flow JSON | 5.3 |
| Fields `trim`, `fwd`, `back` on `Select_entity_ages`; `inputPunct`, `rewritePunct` on `Compose_check_texts` | flow JSON | 5.3 |
| Reasons `residual-name-fragment:<column>`, `rewrite-dropped-punctuation:<column>` | flow, rules §6b and §7 | 5.3 |
| `dr_trim`, `joined_after`, `joined_before`, `joined_spans`, `final_joint`, `dropped_punctuation`, `_self_name` | [`redaction_reference.py`](../../src/tests/narrative/redaction_reference.py#L739) | 5.3, 5.6 |
| 9 flow tests (3 classes), 4 name tests | test files above | 5.3, 5.6 |
| Proposed prompt clause R1c, with a synthetic test-pane script | [prompt document §6](revitalise-redaction-prompt.md#L245) | 5.6 |

## 11.4 Elements changed

| Element | Change | WBS |
|---|---|---|
| Flow size | 97 → **100 actions** (the ceiling the definition test holds), nesting still 5 | 5.3 |
| `Select_entities`, `Select_spans` | The offset clamp moved from `Select_spans` to `Select_entities`, unchanged, so the widening can read clamped offsets | 5.3 |
| `Compose_column_outcome` | Runs after the new filter; two reasons added after `residual-title` and `rewrite-dropped-text` | 5.3 |
| `RedactionNameRules` seed | 6 lines → 7, reordered, worked examples; the same text in all three settings files | 5.6 |
| Expected-output model | Relationship word before two-or-more-people; the writer's own name keeps `[NAME]` | 5.6 |
| Rules | v0.6 → [v0.7](revitalise-redaction-rules.md#L17): §6b, [§6c.1](revitalise-redaction-rules.md#L467), §7, §10.1.3 | 5.6 |
| Flow notes | Action count, the label row, P3 and fidelity | 5.3 |

## 11.5 What is still open

**The DEV `RedactionNameRules` row is still the old one.** The row is create-only, so no deploy will change it, and no
script here updates an existing row. Decision 1 gives the maker steps. Until then the DEV prompt keeps answering *"I am
they"*. If the row already exists in TST/ACC it needs the same edit there; a first deploy that creates it uses the new text.

**The TAD and the SDD need a record amendment, and the build should wait for it.** This iteration adds to `ADR-075` item 2
(name spans are trimmed and widened before labelling) and item 7 (two new hold reasons), and changes the `RedactionNameRules`
seed text quoted in `ADR-076`. FR-095 does not mention the writer's own name. You approved the mechanism; architect-agent
and plan-agent record it. No other design changes.

**The flow in DEV is still the Iteration 10 one.** The span widening, the two checks and the *Dr* trim reach DEV only with
the next build and deploy.

## 11.6 Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-40 | On the platform, `first()` and `last()` of a string return its first and last character, and `indexOf()` / `lastIndexOf()` of a one-character non-letter string return its position, so the widening counts a fragment's letters. If `first()` of a string returned something else, the widening would be 0 and P3 `name-fragment` would still hold the record | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 (workflow expression reference: `first`, `last`, `indexOf`, `lastIndexOf` take a string); the simulator implements the stricter reading and runs both string semantics | No DEV run of this flow version | After the deploy, re-run TD-13 in DEV: `rev_narrativeredacted` starts *"My name is [NAME] and"* with no *Reed*, and no `residual-name-fragment` reason | OPEN |

## 11.7 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic | V1, simulator | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: **198 tests OK** (185 before) |
| The tests can fail | Executed | macOS, local | 7 flow mutations, each caught by the new tests: forward widening off (7 failures), backward off (6), *Dr* trim off (9), input-side fragment check off (1), output-side check off (2), punctuation reason off (1), apostrophe rule loosened to one letter (2) |
| Settings and seed script | Executed (mocked Web API) | macOS, pwsh 7, Pester 5.7.1 | `NarrativeRedaction.Tests.ps1`, `DeploymentSettings.Tests.ps1`, `DataverseScripts.Tests.ps1`: **125 passed, 0 failed, 1 skipped** |
| Source gates | V1 | macOS, local | 19 of 19; `field-length-limits` first failed on four new action descriptions over the 256-character designer limit, shortened, then green |
| Pack | **V2** | macOS, pac CLI | `pac solution pack --packagetype Unmanaged` to a scratch folder: exit 0, no warning |

**V3 to V5 are not reached.** No tool warning was emitted. No live call was made, so no diagnostic component exists.

## 11.8 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 2.25 h | The widening, the two checks and the trim in the flow; 9 flow tests; 7 mutations; notes |
| 5.6 | 0.75 h | The name-rules seed in three files, the expected-output model, rules v0.7, the R1c proposal and test script |
| system | 0.25 h | Three findings |

## 11.9 What you need to decide

**1. Update the `RedactionNameRules` row in DEV by hand**

**Problem** — the row is create-only, so the new rules reach DEV only by a maker edit; no repo script updates an existing row.
**Suggested fix** — in make.powerapps.com, **REV-GrantApplications-DEV**, **Tables**, **Setting**, open the row whose Name is `RedactionNameRules`, replace its Value with the seven lines below exactly, and save. If `RedactionAutoRelease` is `true` in DEV, then open that row, set it to `false`, save, set it back to `true`, and save, so it is again the newest Redaction row.
**What happens if you don't** — DEV keeps writing *"I am they"* and keeping names after relationship words. If you save this row and do not re-save `RedactionAutoRelease`, every DEV record is held with `auto-release-stale`, which is the intended guard (an edit to the rules reaches no trustee until the owner confirms again), not a fault.
[seed value](../../provisioning/deploymentSettings/dev-scoring-settings.json#L313)

```text
When [NAME] is the writer's own name, as in "I am [NAME]", "I'm [NAME]" or "my name is [NAME]", keep [NAME].
Keep [NAME] after Dr: "Dr [NAME] reviews my medication" stays as it is.
When [NAME] comes straight after a relationship word, remove it and keep the neutral word, even when the text names other people: "my husband [NAME]" becomes "my partner", and "our son [NAME], who is [AGE 35 to 44]," becomes "our child, who is [AGE 35 to 44],".
Otherwise, keep [NAME] when the text names two or more different people.
If the text is about one named person, write they, them or their in place of [NAME], as the sentence needs, and make the verb agree: "[NAME] visits me." becomes "They visit me."
A name inside the name of a GP practice is part of [GP PRACTICE].
Mum or Dad used as a name, as in "Mum helps me", becomes "my parent".
```

Check afterwards (read-only):

```bash
pac env fetch --xml "<fetch><entity name='rev_setting'><attribute name='rev_name'/><attribute name='rev_value'/><attribute name='modifiedon'/><filter><condition attribute='rev_name' operator='in'><value>RedactionNameRules</value><value>RedactionAutoRelease</value></condition></filter></entity></fetch>"
```

Expected: `RedactionNameRules` starts *"When [NAME] is the writer's own name"*; if auto-release is on, `RedactionAutoRelease`'s
`modifiedon` is later than `RedactionNameRules`'s.

---

**2. Try the one-clause punctuation change in the rewrite prompt (R1c)**

**Problem** — the rewrite model drops full stops and commas; the template says not to add punctuation but never says to keep it.
**Suggested fix** — follow [prompt document §6](revitalise-redaction-prompt.md#L245): test the current prompt with the synthetic text there, add one clause, test again, and tell development-agent the two answers; development-agent then exports it.
**What happens if you don't** — records whose rewrite loses two or more marks are held for review instead of released, and shorter losses (one full stop) reach trustees.
[prompt document §6](revitalise-redaction-prompt.md#L245)

---

Verification: 198 narrative tests and 125 Pester tests, 0 failures; 7 flow mutations each caught; 19 of 19 source gates; a
local pack (V2) with no warning. **Not verified:** any import, designer save or run of this flow version (V3 to V5), and how
the live model answers the new name rules or the proposed clause.

## Findings Logged (Iteration 11)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1139](../../logs/improvement-log.jsonl) | `partial-extractor-span-leaks-joined-name-fragment` | **blocker** (fixed in this dispatch, stamped) | Never trust an extractor span as a word boundary: widen a name over a joined fragment and hold any label still joined to letters |
| [IMP-1140](../../logs/improvement-log.jsonl) | `name-rule-order-conflict-and-title-inside-span` | rework | State the order of rules a prompt reads, in the row itself, and make the expected-output model apply that order |
| [IMP-1141](../../logs/improvement-log.jsonl) | `rewrite-model-drops-punctuation` | rework | Tell an LLM rewrite what must survive, not only what not to add, and count it after the call |


---

# Iteration 12 — the process owner releases every record (TAD rev 25, 2026-10-19)

**WBS:** `wbs:5.3` (the flow), `wbs:5.4` (the flag and the process owner's card), `wbs:5.6` (rules and settings) ·
**Date:** 2026-10-19 · **Author:** development-agent · **Status:** awaiting code review, together with Iteration 11 ·
**Items:** none carried · Nothing built, deployed, exported or committed; one read-only `pac env fetch` of DEV.
**Design:** TAD rev 25, `ADR-078`, approved by the reviewer 2026-10-19 (relayed by lead-agent), on the reviewer's words:
*"All records should be checked by the process owner regardless. So, we don't need that setting at all."* It also records
Iteration 11's changes, so Iteration 11's request for a TAD amendment is answered. **And SDD Amendment A-11**, approved the
same day: OQ-054 case (e), *"I am Sam and Pat helps me"* becomes *"I am [NAME] and they help me"*. The shared build
configuration is unchanged; the pipeline configuration changes in one comment.

## 12.1 Summary

The flow no longer releases anything. It writes the counterparts as before, marks every scrubbed application *review
required*, and sends the process owner one card per application; only she sets *Redaction Released*. The auto-release
setting and its timestamp guard are gone, and the confidence threshold stays as a hint, seeded at 0.85. The writer's own
name no longer counts as a second person. **Waiting on you:** one line of the `RedactionNameRules` row in DEV (decision 1).

## 12.2 What has been built

1. **No flow action writes the release gate** — [`Write_the_decision`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2222), [`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2318),
   [`test_no_flow_action_writes_the_release_gate`](../../src/tests/narrative/test_scrub_flow_definition.py#L369).
   Both writes drop `rev_redactionreleased`; it keeps its default, false, until the process owner sets it.
   `rev_redactionreviewrequired` is true on every scrubbed application and in the failure handler. A run can no longer undo
   a release made while it ran. `Stop_if_already_released` is unchanged.
2. **Every scrubbed application reaches the process owner** — [`Tell_the_process_owner_card`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2258),
   [`test_no_reason_still_waits_for_the_process_owner_with_a_card`](../../src/tests/narrative/test_scrub_flow_definition.py#L358),
   [readable card](cards/redaction-review-card.json).
   The `If` around the card is removed; the card runs after the decision write, and the HTML fallback keeps its run-after.
   Heading *"Narrative ready for your review"*; the Reasons fact shows the codes, or *"None found by the checks"*. Still
   reference and codes only.
3. **`RedactionAutoRelease` is retired** — [`Read_redaction_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L550), [`Compose_settings`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L786),
   [`Filter_record_reasons`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2196), [`test_a_retired_setting_row_is_ignored`](../../src/tests/narrative/test_scrub_flow_definition.py#L490),
   [`test_an_edit_to_a_rule_row_needs_no_reconfirmation`](../../src/tests/narrative/test_scrub_flow_definition.py#L741).
   Gone: its find, the *saved after every other row* filter, `autoRelease`, and the reasons `auto-release-off` and
   `auto-release-stale`. `modifiedon` is no longer selected, so an edit to a rule row needs no re-save. A leftover row,
   even `true`, changes nothing. Every other reason is unchanged and still decides per column what is written; at record
   level it is a hint.
4. **The threshold is seeded once, at 0.85** — [`dev-scoring-settings.json`](../../provisioning/deploymentSettings/dev-scoring-settings.json#L329),
   [`test-settings.json`](../../provisioning/deploymentSettings/test-settings.json#L649), [`prd-settings.json`](../../provisioning/deploymentSettings/prd-settings.json#L709).
   `createOnly`, so the deploy creates it where absent and never overwrites it. **DEV is unaffected:** read today, the DEV
   row `RedactionConfidenceThreshold` is `0.85`, last modified 2026-10-08 18:44; no `RedactionAutoRelease` row exists in DEV.
5. **The writer's own name is not a second person** (SDD A-11) — [seed line 4](../../src/tests/narrative/redaction_reference.py#L1418),
   [`_name_pass`](../../src/tests/narrative/redaction_reference.py#L1681), [the example as a test](../../src/tests/narrative/test_neutral_terms.py#L258).
   Line 4 now reads *"… two or more different people other than the writer."*, in all three settings files.
6. **The expected-output model, the seeded test data and the scorer say the same** — [`flow_scrub_record`](../../src/tests/narrative/redaction_reference.py#L1325),
   [`decide`](../../src/tests/narrative/redaction_reference.py#L402), [`test_every_expected_record_waits_for_the_process_owner`](../../src/tests/narrative/test_narrative_test_data.py#L163),
   [`test_a_record_the_flow_released_fails`](../../src/tests/narrative/test_narrative_test_data.py#L173).
   `narrative-test-data.json`: `withThresholdAndAutoRelease` became `withThreshold`, `released` is false and review required
   true in every expected record, and `auto-release-off` left the expected reasons. A shape change only: no expected text
   was regenerated (`wbs:5.7`). The scorer now fails a live record the flow released.

## 12.3 Elements changed

| Element | Change | WBS |
|---|---|---|
| Flow | 100 → **97 actions**: `Find_setting_RedactionAutoRelease`, `Filter_settings_saved_after_auto_release` and the `If` removed; the card and fallback moved up a level | 5.3, 5.4 |
| `Entity.xml` | Descriptions of `rev_redactionreleased` and `rev_redactionreviewrequired` ([L2144](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L2144), [L2183](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml#L2183)); no schema change | 5.4 |
| Review Required view | Description only; same id and filter | 5.4 |
| Pipeline config | The `createOnly` comment names the fifth row and the retired one ([L587](../../config/revitalise-grant-automation-pipeline.yml#L587) and two copies) | 5.6 |
| Rules | v0.7 → [v0.8](revitalise-redaction-rules.md#L17): §4.4, §7 items 1, 3, 4, 6, the reason table, the settings table, §7a, §7c; "held" becomes "flagged" | 5.6 |
| Prompt document | [§6](revitalise-redaction-prompt.md#L245): what happens without R1c | 5.6 |
| Test data | `narrative-test-data.json` and its README, as item 6 | 5.3 |
| Tests | 6 tests rewritten, 5 added | 5.3, 5.4 |

**Iteration 11 is superseded in one place:** its decision 1 told you to re-save `RedactionAutoRelease` after editing the
name rules. That step no longer exists.

## 12.4 What is still open

**The SDD amendment for FR-029, FR-030 and FR-095 is plan-agent's**, in parallel; nothing here edits the SDD.
`constraints/domain/special-category-register.yml` still calls the threshold *"the RedactionConfidenceThreshold gate"*;
TAD `ADR-078` leaves that wording to its owner.

**More Teams messages.** One card per scrubbed application per run, including those with no hint (TAD `A-R97`).

## 12.5 Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| ~~A-NS-22~~ | *List rows* returns `modifiedon` as ISO 8601 that `ticks()` reads | — | — | — | — | CLOSED — WITHDRAWN 2026-10-19: `ADR-078` removed the only reader (`Filter_settings_saved_after_auto_release`), and `modifiedon` is no longer selected |

## 12.6 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| Flow logic | V1, simulator | macOS, local | `python3 -m unittest discover -s src/tests/narrative -p 'test_*.py'`: **202 tests OK** |
| The tests can fail | Executed | macOS, local | 4 flow mutations, each caught: the release written again (79 failures), review required only with a reason (18), the card only with a reason (18), the failure handler writing the release (2) |
| Settings, seed script, script contract | Executed (mocked Web API) | macOS, pwsh 7, Pester 5.7.1 | `NarrativeRedaction`, `DeploymentSettings`, `DataverseScripts`, `ScriptContract`: **575 passed, 0 failed, 1 skipped** |
| Source gates | V1 | macOS, local | 19 of 19. `shipped-content` first failed: the readable card in `docs/development/cards/` no longer matched the shipped card; regenerated from the flow, then green |
| Pack | **V2** | macOS, pac CLI | unmanaged pack to a scratch folder: exit 0, no warning |
| DEV settings | Read only | `pac env fetch`, DEV | Threshold row `0.85` (2026-10-08 18:44); no `RedactionAutoRelease` row; `RedactionNameRules` already holds Iteration 11's text (saved 2026-10-19 12:51) |

**V3 to V5 are not reached.** No tool warning. No write to any environment, so no diagnostic component.

## 12.7 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 1.0 h | Flow, model, test data, scorer, tests, mutations |
| 5.4 | 0.5 h | The card, the review flag, view and column descriptions |
| 5.6 | 0.5 h | Threshold seed in three files, A-11 rule and test, rules v0.8, prompt §6, pipeline comment |
| system | 0.25 h | One finding |

## 12.8 What you need to decide

**1. Change line 4 of the `RedactionNameRules` row in DEV**

**Problem** — the DEV row holds Iteration 11's text, saved by you at 12:51; SDD A-11 changes line 4, and the row is create-only.
**Suggested fix** — in make.powerapps.com, **REV-GrantApplications-DEV**, **Tables**, **Setting**, open `RedactionNameRules`, replace its Value with the seven lines below, and save. No other row needs saving: auto-release is retired.
**What happens if you don't** — in DEV, a text naming the writer and one other person keeps `[NAME]` for the other person instead of *they*. Nothing is disclosed either way.
[seed value](../../provisioning/deploymentSettings/dev-scoring-settings.json#L313)

```text
When [NAME] is the writer's own name, as in "I am [NAME]", "I'm [NAME]" or "my name is [NAME]", keep [NAME].
Keep [NAME] after Dr: "Dr [NAME] reviews my medication" stays as it is.
When [NAME] comes straight after a relationship word, remove it and keep the neutral word, even when the text names other people: "my husband [NAME]" becomes "my partner", and "our son [NAME], who is [AGE 35 to 44]," becomes "our child, who is [AGE 35 to 44],".
Otherwise, keep [NAME] when the text names two or more different people other than the writer.
If the text is about one named person, write they, them or their in place of [NAME], as the sentence needs, and make the verb agree: "[NAME] visits me." becomes "They visit me."
A name inside the name of a GP practice is part of [GP PRACTICE].
Mum or Dad used as a name, as in "Mum helps me", becomes "my parent".
```

Check afterwards (read-only): `pac env fetch --xml "<fetch><entity name='rev_setting'><attribute name='rev_value'/><filter><condition attribute='rev_name' operator='eq' value='RedactionNameRules'/></filter></entity></fetch>"` — line 4 ends *"other than the writer."*

---

Verification: 202 narrative tests and 575 Pester tests, 0 failures; 4 flow mutations each caught; 19 of 19 source gates;
a local pack (V2) with no warning. **Not verified:** any import, designer save or run of this flow version (V3 to V5), and
how the live model applies the changed line 4.

## Findings Logged (Iteration 12)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1147](../../logs/improvement-log.jsonl) | `flow-change-misses-companion-artefacts` | friction | When an action is removed or a card changes, grep its name and heading across docs/ and open registers: a retired-word grep cannot find those companions |

## Approval (Iterations 11 and 12)

**APPROVED 2026-10-19.** Reviewer, Xander Lykopoulos, verbatim, relayed by lead-agent: *"Approved to build."* This covers
Iterations 11 and 12 together and accepts the SOFT warning `C-TECH-067` (eight literal counts in pre-existing provisioning
tests; none in this change).

**Decision 12.8.1 is done.** The DEV `RedactionNameRules` row now holds the exact seven-line A-11 value of section 12.8.
Lead-agent wrote it at the reviewer's request (*"Run the redaction rules for me"*) with a `pac power-fx run` `Patch` on
`rev_setting`, and verified it with a read-back `pac env fetch` (`modifiedon` 2026-10-19 14:49 local). No other row was
changed; auto-release is retired, so no re-save follows. Iteration 11's decision 1 is answered by the same write.

**Found while doing it:** `pac power-fx run --environment <url>` does reach Dataverse tables by logical name
(`rev_setting`), which `docs/development/quick-view-form-formxml-reference.md` says it does not, and on this machine's
locale its arguments are separated by `;`. Logged as a finding (below) for the knowledge base; this document does not
change the reference file.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1149](../../logs/improvement-log.jsonl) | `pac-power-fx-reaches-dataverse-tables` | friction | `pac power-fx run --environment <url>` can Patch and read table rows by logical name; on this locale separate arguments with `;`; verify with a read-back `pac env fetch` |


## 12.9 Addendum — the designer refused to save the flow: a Compose may not secure its outputs (2026-10-20)

**What happened** (relayed by lead-agent): build `20261019-1` imported into DEV, the scrub flow landed in Draft, and the
reviewer's designer open-and-save failed, verbatim: *"Flow save failed with code 'InvalidSecureDataConfiguration' and
message 'The secureData configuration of workflow action 'Compose_raw_classes' of type 'Compose' at line '1' and column
'41325' is not valid. These values: 'outputs' are not supported in 'properties'.'"* (0x80060467). `Compose_raw_classes` is
Iteration 11's action. I gave it the Select/Query shape, `["inputs", "outputs"]`; every other Compose in the eleven flows
has `["inputs"]`.

1. **The fix: `["inputs"]` only** — [`Compose_raw_classes`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1034). A Compose's outputs are its inputs, so it stays
   secured; the run-history test already treats it that way and passes. One property and the description changed, nothing
   else.
2. **The build now fails on this shape, in every flow** — [check 18](../../scripts/verify-flow-definition-language.py#L388) of the
   flow-definition gate (a HARD build step, in the group *shapes that import but do not save*), and
   [`test_no_compose_in_any_flow_secures_outputs`](../../src/tests/narrative/test_scrub_flow_definition.py#L898) over all
   `Workflows/*.json`. **Proven both ways:** before the fix the gate failed with exactly one finding, naming
   `Compose_raw_classes`, and the test failed on the defect (re-applied in memory); after the fix both pass. The gate's
   selftest now has a bad Compose beside two look-alikes that must not be flagged (a Compose with `["inputs"]`, a Select
   with both): 23 of 23.
3. **Why nothing caught it before DEV:** the rule is enforced only by the designer save (V4). Pack (V2) and import (V3)
   both accepted it, and no check read `secureData` by action type.

**Re-test needed after the next build and DEV import:** open the flow in the designer and save it (V4), then turn it on.

**Verification:** narrative suite 203 tests OK; Pester `BuildGates` and `NarrativeRedaction` 133 passed, 0 failed; gate
`exit 0` and selftest OK; 19 of 19 source gates; unmanaged pack exit 0, no warning (V2). **Not verified:** the designer save
itself (V4). **Hours:** 5.3, 0.5 h (fix, check, test).

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1156](../../logs/improvement-log.jsonl) | `compose-securedata-outputs-refused-by-designer` | **blocker** (fixed in this dispatch, stamped) | A Compose secures `inputs` only; `outputs` imports but the designer refuses to save (0x80060467). Check 18 now fails the build |

**Approval (addendum 12.9): APPROVED 2026-10-20.** Reviewer, Xander Lykopoulos, verbatim, relayed by lead-agent:
*"Approved"*. This also accepts the SOFT warning `C-TECH-067` again (pre-existing provisioning-test literals; none in this
change). Still open: the designer open-and-save (V4) after the next build and DEV import.


## 12.10 Addendum — DEV re-run of build 20261020-1: a missed GP practice, and the self-name rule (2026-10-20)

**WBS:** `wbs:5.3`, `wbs:5.6` · **Status:** awaiting code review · Synthetic seeded records only; no write to DEV.
Reviewer asked to start both (relayed by lead-agent).

### 1. "Moorside Medical Centre" was written, flagged, not labelled — the extractor, not the flow

**The flow labels the practice when the extractor returns it** — [`test_td13_the_gp_practice_is_labelled_beside_dr_name`](../../src/tests/narrative/test_scrub_flow_definition.py#L648).
The shipped flow, run on TD-13's own text with a PersonName (`Dr Adeyemi` or `Adeyemi`) and an Organization
`Moorside Medical Centre`, gives *"… Dr [NAME] at [GP PRACTICE] reviews my medication every three months."* under both
string semantics, with no reason. The Iteration 11 fields (`trim`, `fwd`, `back`, [`Select_spans`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1084)) apply to
PersonName spans only, and the two spans do not touch.

**The DEV text is reproduced only when the extractor does not return the practice** — [`test_td13_an_extractor_that_misses_the_practice_is_flagged`](../../src/tests/narrative/test_scrub_flow_definition.py#L667).
No Organization, a truncated one (`Moorside Medical`) or an over-long one (`Moorside Medical Centre reviews`) each give
exactly the DEV result: the practice is written, and `residual-practice-word` flags the column. A `Location` type would also
add `unmapped-entity-type`, which the DEV card did not show. So the extractor answered the same text differently from the
day before. This is inferred, not measured: the extractor's answer is secured in run history.

**Nothing reached a trustee.** The record is review-required and the process owner releases every record (`ADR-078`). But a
practice name sits in a written counterpart with only a flag on it. Decision 2 below proposes the safeguard.

### 2. The self-name rule covers "Fenella is the name my friends use for me"

[`_self_name`](../../src/tests/narrative/redaction_reference.py#L1655), [the test](../../src/tests/narrative/test_neutral_terms.py#L258),
[seed](../../provisioning/deploymentSettings/dev-scoring-settings.json#L317).
Line 1 of `RedactionNameRules` is the reviewer's wording, in all three settings files. The expected-output model now also
keeps `[NAME]` in *"[NAME] is the name …"*, *"[NAME] is what … call me"* and *"… call(s) me [NAME]"*. *"Pat is the name of
my carer"* is still a third person. **TAD `ADR-076`'s quoted seed needs the same erratum (architect-agent).** Lead-agent
writes the DEV row after you confirm the wording; nothing was written to DEV here.

### Outside this change: a new flow fails the narrative suite

`test_solution_flows.NoTriggerLoop` (3 tests) fails on `REVFinanceCapturePayment`, a flow written today at 15:24 by
another dispatch: it is on a self-trigger loop. It is not narrative work and this addendum does not touch it; its owner
needs to know before the next build, because the narrative suite is in the HARD `unit-tests` step.

### Verification

Narrative suite: 206 tests, every narrative-scrubbing test OK; the 3 failures are the trigger-loop tests above. Pester
`DeploymentSettings` and `DataverseScripts`: 135 passed, 0 failed, 1 skipped. 19 of 19 source gates; field-length limits,
assumption markers and register, build config exit 0. **Not verified:** the extractor's live answer for this column, and how
the live model applies the new line 1. **Hours:** 5.3, 0.5 h (reproduction, tests); 5.6, 0.25 h (line 1, model, test).

## 12.11 What you need to decide

**1. Confirm line 1 of `RedactionNameRules`, so lead-agent can write the DEV row**

**Problem** — DEV still reads *"they is the name my friends use for me"*.
**Suggested fix** — confirm this exact seven-line value; lead-agent writes it to DEV.
**What happens if you don't** — the DEV prompt keeps turning the writer's own name into *they* in sentences like this one.
[seed value](../../provisioning/deploymentSettings/dev-scoring-settings.json#L317)

```text
When [NAME] is the writer's own name, keep [NAME]. This includes "I am [NAME]", "I'm [NAME]", "my name is [NAME]" and any sentence where the writer says [NAME] is what they are called, such as "[NAME] is the name my friends use for me".
Keep [NAME] after Dr: "Dr [NAME] reviews my medication" stays as it is.
When [NAME] comes straight after a relationship word, remove it and keep the neutral word, even when the text names other people: "my husband [NAME]" becomes "my partner", and "our son [NAME], who is [AGE 35 to 44]," becomes "our child, who is [AGE 35 to 44],".
Otherwise, keep [NAME] when the text names two or more different people other than the writer.
If the text is about one named person, write they, them or their in place of [NAME], as the sentence needs, and make the verb agree: "[NAME] visits me." becomes "They visit me."
A name inside the name of a GP practice is part of [GP PRACTICE].
Mum or Dad used as a name, as in "Mum helps me", becomes "my parent".
```

---

**2. Choose a safeguard for a GP practice the extractor misses**

**Problem** — when the extractor misses a practice, its name is written into the counterpart with only a flag.
**Suggested fix** — (b): do not write the column when a capitalised practice suffix (*Surgery*, *Medical Centre*, *Health Centre*, *Medical Practice*, *Group Practice*, *Family Practice*) is left in the final text, with the new reason `practice-name-survived:<column>`. That is about one action, matched case-sensitively, so *"had surgery"* and *"the practice nurse"* still write. The alternative (a) labels the capitalised phrase before such a suffix as `[GP PRACTICE]`: more useful text, about three to four actions. Either needs architect-agent to record it in `ADR-075`.
**What happens if you don't** — the practice name stays in the written counterpart until the process owner removes it during her review of every record; nothing reaches a trustee unreviewed.
[the flagged case](../../src/tests/narrative/test_scrub_flow_definition.py#L667)

---

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1170](../../logs/improvement-log.jsonl) | `extractor-misses-gp-practice-written-with-flag-only` | rework | A practice name the extractor misses is written with only a flag; a capitalised practice suffix left in the text should stop the write or be labelled |
| [IMP-1171](../../logs/improvement-log.jsonl) | `self-name-rule-too-narrow` | rework | State a prompt rule as the rule, give phrasings as examples, and mirror the wider rule in the oracle |

**Approval (addendum 12.10): APPROVED 2026-10-20.** Reviewer, Xander Lykopoulos, verbatim, relayed by lead-agent:
*"Approved"*. This also accepts the SOFT warning `C-TECH-067` again (pre-existing provisioning-test literals; none in this
change).

**Decision 12.11-1 is done.** At your confirmation (*"Confirm the wording"*), lead-agent wrote the seven-line
`RedactionNameRules` value of section 12.11 to the DEV `rev_setting` row with a `pac power-fx run` `Patch` at
2026-10-20 15:21 local, and verified it by read-back. Nothing else in DEV was changed.

**Decision 12.11-2: you chose to label the capitalised phrase before a practice suffix as `[GP PRACTICE]`.** Lead-agent
relayed this as "option B". In section 12.11 that labelling route is the one written second, as "(a)"; the "(b)" there was
not-written. **What is recorded here is the labelling route, as you described it.** Architect-agent records it in
`ADR-075` first, and it is **not implemented yet**: it waits for that record and a new dispatch. Until then, a missed
practice is written and flagged (`residual-practice-word`), and the process owner reviews every record.


---

# Iteration 13 — a GP practice the extractor misses is labelled (TAD rev 29, 2026-10-20)

**WBS:** `wbs:5.3` (the flow), `wbs:5.6` (the practice-words row) · **Date:** 2026-10-20 · **Author:** development-agent ·
**Status:** awaiting code review · **Items:** none carried · Nothing built, deployed or committed; no call to any
environment. **Design:** TAD rev 29, `ADR-075` item 2 *"Decided: label"* (`IMP-1170`), approved by the reviewer, verbatim:
*"LAbel the name and approved for development"*. It answers decision 12.11-2.

## 13.1 Summary

A GP practice name is now labelled before the rewrite even when the extractor misses it. That was the DEV case of TD-13,
where *Moorside Medical Centre* was written with only a flag. The flow finds each capitalised practice suffix and walks
back over the name before it. It is at **100 actions, the ceiling**: three Selects added, nothing raised. No new reason
code, no setting added.

## 13.2 What has been built

1. **The suffix list is one place, including the process owner's extra words** — [`Compose_settings.practiceSuffixes`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L838).
   The six built-in suffixes, plus each valid `RedactionPracticeWordsExtra` entry with each word capitalised (*walk in
   clinic* becomes *Walk In Clinic*). An invalid extra row gives the six only, as P3's list already does.
2. **Each suffix occurrence is found case-sensitively** — [`Select_practice_suffix_hits`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1335).
   Positions come from splitting the column on the suffix, and each one is confirmed with `replace()`, which is
   case-sensitive (`A-NS-35`). So *had surgery* never matches, whichever way the platform's `split()` treats case. There must be
   a space or the start before, and a non-letter or the end after. At most 25 occurrences of one suffix per column are
   labelled; a later one stays flagged by `residual-practice-word`.
3. **The name before it is walked back** — [`Select_practice_words`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1363), [`Select_practice_spans`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1397).
   The walk goes back over up to four words while each is *St*, *St.* or a capitalised name word (letters with an internal
   apostrophe or hyphen allowed), and stops at a lower-case word, a digit, other punctuation or the start. Zero words
   gives no span. Each span is `[GP PRACTICE]` with no score, so the record's confidence is still the extractor's alone,
   and no P1 value.
4. **The spans join the extractor's, after them** — [`Filter_labelled_spans`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1446). The existing containment and
   overlap rules apply unchanged: *Dr Patel's Surgery* contains the extractor's *Patel*, which is dropped; an equal
   extractor Organization is kept once; a partial overlap holds the column.
5. **The reference model and the tests say the same** — [`practice_spans`](../../src/tests/narrative/redaction_reference.py#L808),
   [`PracticeNamesTheExtractorMisses`](../../src/tests/narrative/test_scrub_flow_definition.py#L824),
   [TD-13 with the Organization missing, truncated or over-long](../../src/tests/narrative/test_scrub_flow_definition.py#L968).
   The tests cover the TAD's five worked examples, the negatives (*had surgery*, *the practice nurse*, *a health centre*,
   a sentence-initial *Surgery*, *the Surgery*), the stops, the four-word cap, a partial overlap, an equal Organization and
   an extra-row suffix. TD-13's disability column now reads *"… Dr [NAME] at [GP PRACTICE] reviews …"* with no reason,
   whatever the extractor did with the practice. Iteration 12.10's test that pinned the old flag-only behaviour is replaced.
   Rules: [§6c.2](revitalise-redaction-rules.md#L534), v0.9.

## 13.3 Elements

| Element | Change | WBS |
|---|---|---|
| Flow | 97 → **100 actions**: `Select_practice_suffix_hits`, `Select_practice_words`, `Select_practice_spans`; `Compose_settings.practiceSuffixes`; `Filter_labelled_spans` reads both span lists; `Filter_unmapped_entities` runs after the new Selects | 5.3 |
| Reference | `PRACTICE_SUFFIXES`, `capitalise_words`, `practice_name_word`, `practice_spans`; `label_spans` takes the suffix list; `RunContext.practice_suffixes` | 5.3, 5.6 |
| Tests | 7 flow tests added, 1 replaced | 5.3 |
| Notes, rules | Flow notes; rules v0.9 §6c.2 | 5.3, 5.6 |

Every new expression is under the 8,192-character limit (longest 1,742). The new actions secure inputs and outputs; none
of them is a Compose.

## 13.4 What is still open

**No new platform assumption.** `split`, `take`, `join`, `skip`, `div` and `mod` are already used in this flow. Case is
confirmed with `replace()` (`A-NS-35`), and positions do not depend on `split()`'s case semantics. `A-NS-40` still covers
`first()`/`last()`.

**The simulator is slower:** the narrative suite takes about 70 seconds, up from 25, because each column now runs about
150 extra items in Python. On the platform that is 150 items per column, small next to the existing per-character Selects.

## 13.5 Verification Evidence

| Component | Level reached | Evidence |
|---|---|---|
| Flow logic | V1, simulator | Narrative suite **212 tests OK**, both string semantics. Without the other workstream's trigger-loop tests the result is the same (they pass now: 3 of 212) |
| The tests can fail | Executed | 4 flow mutations, each caught: practice spans not joined (24 failures), the four-word cap ignored (2), the capital-letter test removed (13), the after-boundary check off (2). One equivalent mutation was discarded |
| Gates | V1 | 19 of 19 source gates; field-length limits; flow-definition self-tests; assumption markers and register; build config: all exit 0 |
| Pester | Executed | `NarrativeRedaction`, `BuildGates`: 133 passed, 0 failed |
| Pack | **V2** | Unmanaged pack exit 0, no warning |

**Not verified:** import, designer save and a DEV run of this flow version (V3 to V5).

## 13.6 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 2.0 h | Three Selects within the expression and action limits, the reference model, 7 tests, 4 mutations |
| 5.6 | 0.25 h | Extra-row suffixes, rules v0.9 |
| system | 0.25 h | One finding |

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1176](../../logs/improvement-log.jsonl) | `empty-createarray-in-flow-expression` | friction | In a flow expression an empty array is `json('[]')`, never `createArray()` with no argument |


# Iteration 14 — one extractor call per batch, one prompt for rewrite and spelling (TAD rev 30, 2026-10-21)

**WBS:** `wbs:5.3` (the flow), `wbs:5.6` (spelling, `CO-009`, approved unbilled) · **Date:** 2026-10-21 · **Author:**
development-agent · **Status:** awaiting code review · **Items:** none carried · Nothing built, deployed, exported or
committed; no call to any environment. **Design:** TAD rev 30, [`ADR-082`](../architecture/revitalise-grant-automation-architecture.md) (approved by the reviewer 2026-10-21,
verbatim *"Approved"*, relayed by lead-agent), on his decisions D1 to D3. Sub-agent fan-out not performed: the flow, its
reference model, its tests and the two documents change one contract together, so splitting them would have meant passing the
whole contract between agents twice.

## 14.1 Summary

The flow now asks the extractor once per batch of columns instead of once per column, and one prompt both rewrites and
corrects spelling. A typical application is one extractor call where there were about five, and the spelling call is gone.
The flow is **109 actions, 6 levels deep**; the ceiling is **125**. **Waiting on you:** after the new flow is in DEV, apply the
new prompt wording (R1d) yourself, in that order; the exact text is in the prompt document.

## 14.2 What has been built

1. **The extractor is called once per batch of columns, up to 5,000 characters** — [`For_each_plan_column`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L921), [`For_each_batch`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L968), [`Extract_entities_from_the_batch`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1064).
   The chosen columns are packed in their fixed order (a column joins the open batch when the batch, the two-line-feed
   separator and the column total at most 5,000; otherwise it opens the next). The plan is a fourth variable holding column
   names and numbers only ([`Initialise_batch_plan`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L163)). With no column chosen the loop runs zero times and no call is made. Both numbers are in
   [`Compose_constants`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L251).
2. **Each entity goes back to its column by offset, and anything that straddles two columns holds both** — [`Select_batch_layout`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1038), [`Filter_column_entities`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1147), [`Select_column_entities`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1164), [`Select_overlap_trials`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1467).
   An entity belongs to every column it touches, rebased to it; one inside the separator belongs to none. A labelled entity that
   runs across a boundary gives `overlapping-identifiers` and no write in each column it touches. It does so even where a
   larger span in that column contains it (fail closed); that is slightly stricter than the ADR's wording and costs nothing but
   a held column.
3. **A failed call marks every column of its batch `ai-error`** — [`Compose_batch_entities`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1098) is null, and each column then reaches the existing
   `ai-error` branch. Other batches go on.
4. **One prompt rewrites and corrects spelling; the spelling call is gone** — [`Compose_rewrite`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1576), [`Compose_final_text`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1599). The answer is
   split at the first `###CORRECTIONS###`: the text before it is the rewrite, the lines after it are the corrections the model
   declares. `Run_the_spelling_prompt`, `Compose_spelling` and `Select_spelling_words` are removed. The template wording is in
   [the prompt document, section 1](revitalise-redaction-prompt.md#L20), with your steps in [R1d](revitalise-redaction-prompt.md#L129).
5. **Check P2 accepts a corrected word only as a declared, validated near-spelling pair** — [`Select_valid_corrections`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1644), [`Filter_added_words`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1686).
   A pair is valid when the wrong word is an input word as written there and starts lower case, the right word starts with the
   same letter, the lengths differ by at most two, both are letters, the wrong word is not a closed-list word and the right word
   is not a gendered word. A word the model changes without declaring it, or beyond that, stops the column being written.
   **Lost, as `ADR-082` says:** the old rule proved *where* a corrected word sat; this one cannot.
6. **The reference model and the tests say the same** — [`plan_batches`](../../src/tests/narrative/redaction_reference.py#L1215), [`map_entities`](../../src/tests/narrative/redaction_reference.py#L1240), [`split_answer`](../../src/tests/narrative/redaction_reference.py#L1257), [`valid_corrections`](../../src/tests/narrative/redaction_reference.py#L1282),
   [`SpellingDeclaredPairs`](../../src/tests/narrative/test_scrub_flow_definition.py#L304), [`BatchedExtraction`](../../src/tests/narrative/test_scrub_flow_definition.py#L420), [the size and depth test](../../src/tests/narrative/test_scrub_flow_definition.py#L1223). The old word-by-word spelling
   tests and `accept_spelling` are replaced, not kept. Rules [v1.0](revitalise-redaction-rules.md#L17) and [section 4.4a](revitalise-redaction-rules.md#L342); the flow [notes](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.notes.md) describe the new parts.

## 14.3 Elements

| Element | Change | WBS |
|---|---|---|
| Flow | 100 → **109 actions**, nesting 5 → 6: +`Initialise_batch_plan`; +`For_each_plan_column`, `Compose_batch_step`, `Append_batch_plan`; +`For_each_batch`, `Filter_batch_columns`, `Select_batch_texts`, `Compose_batch_joined`, `Select_batch_layout`; the extractor call and its answer move up a level and are renamed; +`Filter_column_entities`, `Select_column_entities`; +`Select_valid_corrections`; −`Run_the_spelling_prompt`, `Compose_spelling`, `Select_spelling_words`. `Compose_constants` gains `batchLimit`, `separator`, `correctionsMark`; `Compose_check_texts` gains `inputCase`. The two nested loops are sequential | 5.3 |
| Reference | `plan_batches`, `batch_layout`, `map_entities`, `split_answer`, `valid_corrections`, `input_case_words`; `scrub_column` and `flow_scrub_record` take no spelling prompt; `accept_spelling`, `take_correction` removed | 5.3, 5.6 |
| Tests | 7 spelling tests replaced by 11 (`SpellingDeclaredPairs`), 12 new (`BatchedExtraction`), size and depth 125 and 6, an 8,192-character check on every expression, 4 variables, prompt-component tests for the rev 30 template | 5.3, 5.6 |
| Prompt document | Section 1 now holds the rev 30 template and the R1d steps; the rev 23 template is kept in 1.2 (the solution still exports it); section 2 marked retired | 5.6 |
| Rules, notes | Rules v1.0; flow notes | 5.1, 5.3 |
| Not touched | `Other/Customizations.xml` and `Other/Solution.xml` (the spelling component stays until you delete it in DEV); the solution's pipeline and build configuration; the settings rows | — |

Every expression is under the 8,192-character limit (the longest new one is the pair rule, [`Select_valid_corrections`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1644)). Every
description is within the designer's 256 characters. All new actions that carry narrative text secure their inputs and outputs
(`Compose` actions secure inputs only).

## 14.4 What is still open

**Deployment order matters, and only in DEV.** Import the flow first, apply R1d second. The new flow with the old prompt writes
the rewrite with no spelling correction and no blackout. The new prompt with the old flow holds every column. TST/ACC and PRD
receive both in one solution.

**Two small departures from `ADR-082`'s wording, for you to accept or reverse.** (a) The valid corrections are carried to P2 as
the output of `Select_valid_corrections`, not as a property of `Compose_check_texts`: the pair rule needs the case-kept input
text that `Compose_check_texts` computes, so the Select has to run after it. (b) The rewrite is trimmed at both ends, where the
ADR says trailing white space; there is no trailing-only trim in the language, and a leading blank is not narrative.

**The cost of merging the prompts is unmeasured.** A correction the model makes that the pair rule refuses now stops that
column, where two calls left the slip as written. The `wbs:5.7` scoring run counts it (`A-NS-43`).

**Not designed, as `ADR-082` says:** where the AI Builder event table keeps the text of every call (`A-NS-45`). Batching neither
fixes nor worsens it. No dispatched agent puts real applicant text through DEV before you decide.

**The change-scoped build does not shrink here yet.** `run-build.py --plan --changed-since last-green` plans 101 of 102 steps
now, because the working tree also holds uncommitted work from other items (Capture Payment, the code apps' package files,
four build manifests). Scoping will help once those are committed.

## 14.5 Unvalidated Assumptions Register (C-TECH-052)

| ID | Claim (one sentence — BOTH directions if it is a conditional) | Where in source | Evidence | Why not verified | Cheapest verification (BOTH directions) | Status |
|---|---|---|---|---|---|---|
| A-NS-41 | The extractor's `startIndex` and `length` count UTF-16 characters of the whole joined text, the separators and a CRLF inside a column included and unmodified, so `substring(joined, start, length)` is the column's own text. If they did not, labels would land on the wrong characters; P1 still fails closed (`identifier-survived`, not written) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (`A-NS-2` held for one column, E1); the simulator counts the same way | No DEV run of this flow version | DEV, synthetic text only: join two or three columns, one with CRLF, a name at a known offset in each; compare every entity's value with the substring at its offset | OPEN |
| A-NS-42 | A cloud flow with a `Foreach` inside a `Foreach` saves in the designer when an inner action reads an action of the enclosing iteration, and `take(range(0, max(n, 1)), n)` is accepted as the outer array. If refused: `CASCADE: ARCH_GAP` (fallback: closed-form batching, no nesting) | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (check 12's measured refusal of 2026-10-09 is for a reference from outside a loop) | No import | Import into DEV and open and save the flow once (V4) | OPEN |
| A-NS-43 | One call to the rewrite prompt returns `finishReason` `stop`, the corrected text and, when it corrected anything, a `###CORRECTIONS###` line and `wrong=>right` lines, often enough that `rewrite-invalid` from an undeclared or refused correction is rare. If it does not, a measured rate goes to you | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E3 (the form is untried; `A-NS-8`, `A-NS-33` are the same call's other contracts) | R1d not applied | The `wbs:5.7` scoring run on the synthetic corpus: count those `rewrite-invalid` and the share of seeded misspellings corrected | OPEN |
| A-NS-44 | A joined call is billed 20 credits per started 1,000 characters of the whole text, separators included. If it were billed per column, batching would save nothing | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E1 (one column, `IMP-1189`); E2 (rate table) | No batch call yet | After the first DEV batch call, read `msdyn_aievent.msdyn_creditconsumed` and compare with 20 × ceil(length / 1,000) | OPEN |
| A-NS-45 | `msdyn_aievent` keeps the raw input of every AI Builder call, so applicant text persists in a Dataverse table (`IMP-1190`, TAD `A-R105`): who can read it and for how long is unknown | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E1 (measured in DEV) | Open, not designed | Read the table's role scope and retention in DEV; decide retention and a PRD bulk delete as its own decision | OPEN |

Re-stated, not changed: `A-NS-8`, `A-NS-33`, `A-NS-34` now sit on `Compose_rewrite` and `Compose_batch_entities`; `A-NS-35` (`replace()` is case-sensitive) now carries the pair rule's two case tests as well as the title check; `A-NS-12`, `A-NS-13`, `A-NS-16`, `A-NS-5` sit on the batch call; `A-NS-31` stays closed (the id and inputs are unchanged).

## 14.6 Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

| Component | Level reached | Evidence |
|---|---|---|
| Flow logic | V1, simulator | Narrative suite **232 tests OK**, both string semantics; the flow and the reference model agree on writes, reasons and decision for every case, including batches, the straddle, a CRLF and a failed batch |
| The tests can fail | Executed | 7 flow mutations, each caught: crosses never set (2 failures), P2 ignoring declared pairs (10), first letter not compared (2), wrong word need not be an input word (2), gendered right word allowed (1), batch limit 5,001 (3), separator not counted in the offsets (5). One equivalent mutation discarded |
| Gates | V1 | 19 of 19 source gates (field-length limits, flow-definition-language checks 1 to 18 incl. 12 and 18, assumption gates); build configuration verifier |
| Pester | Executed | `NarrativeRedaction`: 2 passed, 0 failed (it runs the whole narrative suite) |

**Not verified:** import, designer save and a DEV run of this flow version (V3 to V5), the live model's use of the new template, the extractor's offsets over a joined text and the billing of a joined call.

## 14.7 Hours proposal (for commercial-agent, behind `APPROVE TIMESHEET`; not a booking)

| WBS | Proposed | Evidence |
|---|---|---|
| 5.3 | 6.0 h | Batch plan, nested loop, offset mapping, merged answer and pair rule in a 109-action flow within the expression and description limits; reference model; 26 tests; 7 mutations |
| 5.6 | 1.25 h | Merged template and R1d steps, rules v1.0, prompt-component tests |
| system | 0.25 h | One finding |

## 14.8 What you need to decide

**1. Apply the new prompt wording in DEV (R1d), after the new flow is imported**

**Problem** — the prompt must also correct spelling and reply in the form the flow reads, and only you can edit it in DEV.
**Suggested fix** — import the new flow into **REV-GrantApplications-DEV**, then follow [R1d](revitalise-redaction-prompt.md#L129): paste the first template in [section 1](revitalise-redaction-prompt.md#L20) into **REV Narrative Rewrite Prompt**, keep the five inputs and the settings, run the synthetic test text there, and tell development-agent.
**What happens if you don't** — the flow still works, but writes the rewrite without spelling correction. **If you do it before the flow is in DEV**, every column is held until the flow arrives.

**2. Delete REV Narrative Spelling Prompt in DEV, later**

**Problem** — the component is no longer called but is still in the solution source.
**Suggested fix** — do nothing now. After R1d and the refreshed export, development-agent tells you when its source reference can go in the same commit, and you delete it in DEV.
**What happens if you don't** — nothing breaks; it stays as an unused component.

**3. Accept or reverse the two small departures in 14.4**

**Problem** — the valid corrections reach P2 from `Select_valid_corrections` rather than from `Compose_check_texts`, and the rewrite is trimmed at both ends.
**Suggested fix** — accept both; neither changes what is written or held.
**What happens if you don't** — architect-agent amends `ADR-082` item 6 and this flow follows.

---

Verification: 232 narrative tests OK, 7 of 7 flow mutations caught, 19 of 19 source gates. **Not verified:** any import, designer save or run of this flow version, or the live model on the new template.

## 14.9 Addendum: sort() over mixed Integer and Float (IMP-1198; wbs:5.3)

**What failed.** DEV run of build 20261021-3 on application 1086: four of five columns processed; one failed at `Compose_column_outcome` with InvalidTemplate, "`sort` expects the sortBy parameter of an object array to reference a parameter that is the same type for each object".

**Confirmed from the definition** (run history is secured; column content was not inspected). `Compose_column_outcome.scores` sorts `body('Filter_labelled_spans')` by `score`. Extractor spans take `float(...)` in `Select_entities`; the practice-suffix spans in `Select_practice_spans` took the integer literal `2` (TAD rev 29). A column holding both therefore mixed Float and Integer. It fits the symptom (one column in five) and is consistent with the evidence; the failing column's content was not read, so this is the diagnosis the definition supports, not an observation of that run.

**Fix.** `Select_practice_spans` score `2` becomes `"@float(2)"`. One line. Every span in `Filter_labelled_spans` now carries a Float score.

**Other sort/min/max checked, no change needed.** The other `sort` is on `start` (all integers: `max(sub(...))`, `int(...)`). `min(union(variables('scores'), createArray(2)))` in `Filter_record_reasons` and `Compose_decision` is `min` over a plain number array, which the platform accepts mixed; it is not the object-array rule.

**Why 232 tests passed.** `wdl_sim.f_sort` used Python `sorted()`, which compares int and float freely. It now raises `WdlError` when the sortBy values are not one type, as the platform does.

**Tests.** `test_iteration_14_an_extractor_span_and_a_practice_span_in_one_column_sort_on_one_type` (a PersonName the extractor found plus a practice suffix it did not, one column) and `test_iteration_14_the_sim_rejects_a_sort_over_mixed_integer_and_float`. With the fix reverted, `PracticeNamesTheExtractorMisses` reports 8 failures across 4 tests (the new case and three earlier tests that had been passing over the defect); with the fix, OK.

**Verification.** 234 narrative tests OK; `run-source-gates.py` 19 source gates run; assumption-markers and assumption-register PASS. **Not verified:** any import or run of the corrected flow, and `sort()` on the platform with a Float `2.0` in a real run (`A-NS-15` stays OPEN).

**For you to do.** Rebuild and re-import to DEV, then re-run application 1086. Finding: IMP-1198 (diagnosis), IMP-1199 (simulator gap, `fixes: IMP-1198`).

### Addendum: the rewrite prompt keeps full stops (IMP-1202, 2026-10-21)

The rewrite model dropped sentence full stops (`msdyn_aievent` shows it since 2026-10-19, same with the rev 23 and rev 30 templates). The reviewer replaced *"do not add punctuation,"* in the closing paragraph with *"; keep every punctuation mark exactly where it is, including the full stop at the end of every sentence and after a label; do not add punctuation;"* in DEV and confirmed it on application 1086.

**Changed here (document and test only; no build, deploy or commit).** Section 1 of [the prompt document](revitalise-redaction-prompt.md) carries the new sentence and a source-of-truth note; `test_the_rev30_template_is_the_exported_one_plus_exactly_the_spelling_changes` now allows exactly this sentence as a fourth edit and asserts it is present. Section 6's R1c note is superseded in substance by this wording.

**Source of truth.** DEV is the source of truth for the prompt until the next export. **The reviewer re-exports `REV Narrative Rewrite Prompt` from DEV before the ACC promotion build**; `Other/Customizations.xml` holds the older template until then, and the export test moves to section 1 at that point.

**Corpus or unit assertion: not added.** Full-stop loss happens inside the model; the simulator and unit tests replay canned answers, so an assertion on written columns would test the fixture, not the prompt. The flow's existing guard (`rewrite-dropped-punctuation`, more than 10% fewer marks, held for the process owner) already counts punctuation on real output; the only real check is the `wbs:5.7` scoring run, which should report the punctuation-count flag rate.

## Findings Logged (Iteration 14)

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1193](../../logs/improvement-log.jsonl) | `scoped-build-plan-covers-the-whole-dirty-tree` | friction | Before promising a fast DEV-only build, read the `--plan` count: unrelated uncommitted work widens a change-scoped plan to nearly every step |

