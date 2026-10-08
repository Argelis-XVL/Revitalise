# Dev Summary Document — Narrative Scrubbing (Automation #5)

**Feature slug:** `revitalise-grant-automation` (shared build configuration; see Iteration 2 §8)
**TAD reference:** `docs/architecture/revitalise-grant-automation-architecture.md`, rev 19 (§5.5, `ADR-071`, `ADR-072`) for Iterations 1–2; rev 20 (§5.5.1, §12.6.1, `ADR-073`, `ADR-074`) for Iteration 3
**Items:** none carried

| Iteration | Date | WBS | Status |
|---|---|---|---|
| 1 — rules v0.1, corpus, harness, review tab | 2026-10-05 | `wbs:5.1`, `5.2`, `5.4` (tab) | **APPROVED 2026-10-06** (Xander Lykopoulos, *"Approved development work"*) |
| 2 — the scrubbing flow, the `TD-008` columns, the Review Required view, rules v0.2 | 2026-10-06 | `wbs:5.3`, `5.4` (flagging and view), `5.1` (rules v0.2) | **APPROVED 2026-10-06** (*"Code review approved."*, `logs/routing.log` 20:45), with Iteration 3 — [jump to Iteration 2](#iteration-2--the-scrubbing-flow-2026-10-06) |
| 3 — postcode register, tunable settings with guard rails, the prompt stage up to the DEV boundary, rules v0.3 | 2026-10-06 | `wbs:5.3`, `5.6` (settings the process owner tunes), `5.4` (new review reasons) | **APPROVED 2026-10-06** (with Iteration 2) — [jump to Iteration 3](#iteration-3--register-settings-and-the-prompt-stage-2026-10-06) |
| 4 — build blocker `IMP-1082`, the coverage reading, the prompt component and its run action | 2026-10-06 | `wbs:5.3` (component, run action), `5.4` (form test) | **APPROVED 2026-10-07** (*"Approved on dev summary"*); six changes after approval, one affecting the prompt component, listed under *Approval (Iteration 4)* — [jump to Iteration 4](#iteration-4--build-fix-and-the-prompt-run-action-2026-10-06) |

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
| `RedactionPromptCategory.Name`, `.FamilyMember`, `.GpPractice`, `.Address`, `RedactionKinshipWordsExtra`, `RedactionPracticeSuffixesExtra`, `RedactionStreetWordsExtra`, `RedactionPracticeWordsExtra` | all | **New, none seeded** (`ADR-074` item 7). Absent leaves rev 19 behaviour. Synthetic example texts and each row's description are in [the prompt document §5](revitalise-redaction-prompt.md#5-r5-the-settings-rows-when-the-stage-is-to-be-switched-on-in-dev-reviewer) |
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
| A-NS-23 | In DEV (`crm17`) with *Move data across regions* unticked, a prompt can be created, given a model, saved inside the solution and exported; if not, building the component needs a residency act and is an `ARCH_GAP` | `src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json` | E2 only | Needs R0 and R1 | R1 itself, with R0's setting state recorded ([prompt document §3](revitalise-redaction-prompt.md#3-r1-create-the-prompt-in-dev-reviewer-interactive-maker-session)) | OPEN |
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
| [`revitalise-redaction-prompt.md#L113`](revitalise-redaction-prompt.md#L113) | Prompt document | Status updated; section 6 records what the export showed | 5.3 |

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

**What the export showed, and what was not adopted** (full table in [the prompt document §6](revitalise-redaction-prompt.md#L113)):

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
