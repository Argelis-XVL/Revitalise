# Test Report — Revitalise Grant Automation (Narrative Scrubbing, flow 1011 and the two prompts)

**Feature Slug:** revitalise-grant-automation
**Artifact:** build/artifacts/revitalise-grant-automation-20261016-3/
**Date:** 2026-10-16
**Status:** FAIL
**WBS:** `wbs:5.3`, `wbs:5.6`, plus `CO-009` (spelling, approved, unbilled) · **Items:** none carried
**Design tested against:** SDD Amendment A-09 (FR-026 as amended, FR-094 to FR-101, US-025); TAD rev 23 (`ADR-075` with its two errata, `ADR-076`); Dev Summary Iterations 9 and 10 with addenda 10.10 and 10.11.

> **This report does not approve the build.** It names the artifact, so `verify-artifact-provenance.py` will now
> exit 0 for it, but that script checks only that a report *names* a build, not what the report concluded (see
> Findings). Read the Status line above.

## Summary

The packaged flow is exactly the source, the two prompts are in both zips with the ids DEV holds, and every check
that decides what is written (P1, P2, P3, the spelling rule, the four rule rows) passes against bad stand-in answers.
**One disclosure control is missing:** the flow's 14 Dataverse writes do not hide their outputs from run history,
and a Dataverse "Update a row" returns the row, which carries all 12 raw narrative answers. The test that should
catch it cannot, because its stand-in for a write returns nothing. The fix is small; the decision on the scoped DEV
deploy is yours (below).

## What has been tested

1. **The artifact is the source, and the placeholders are gone** — [flow JSON](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1210).
   Both zips unzipped: all 11 flow definitions parse equal to source, the managed zip says `Managed 1`, the unmanaged
   `0`. The flow carries no `PENDING-A-NS` placeholder, names the rewrite prompt and the spelling prompt once each,
   and no longer calls the rev 20 prompt. 97 actions, 0 `Until`, 0 `result()`.
2. **The two prompts ship, and DEV holds them under the same ids** — `customizations.xml` in both zips has three
   `AIModel` elements and `solution.xml` three type-401 root rows. A read-only `pac env fetch` of `msdyn_aimodel` in
   DEV returned *REV Narrative Rewrite Prompt* and *REV Narrative Spelling Prompt* under exactly the two ids the flow
   calls. The packer's "root components are not defined" line for these is the standing accepted warning
   ([Dev Summary §4.11](../development/revitalise-narrative-scrubbing-dev-summary.md#L941)).
3. **The checks hold against bad model answers** — [`P2TheRewriteAddsNoWord`](../../src/tests/narrative/test_scrub_flow_definition.py#L227),
   [`P1NoFoundIdentifierSurvives`](../../src/tests/narrative/test_scrub_flow_definition.py#L277),
   [`SpellingAcceptedWordByWord`](../../src/tests/narrative/test_scrub_flow_definition.py#L293),
   [`RuleRows`](../../src/tests/narrative/test_scrub_flow_definition.py#L498).
   A rewrite that adds a name, number or sentence is not written; an extractor value left in the text is not
   written; a spelling answer is taken word by word and never changes a label, a capital or a replaced word; an
   absent or malformed rule row stops the record before any AI call. 184 narrative tests, 0 failures.
4. **The four rule rows are in DEV and were not overwritten** — [create path](../../provisioning/dataverse/seed-settings.ps1#L253),
   [real-exception test](../../src/tests/provisioning/DataverseScripts.Tests.ps1#L346).
   My read-only fetch shows `RedactionNeutralTerms`, `RedactionTitles`, `RedactionNameRules` and `RedactionLabels`
   with created and modified both 16:05 UTC, which agrees with the lead's two runs (first CREATED, second left
   unchanged). The artifact's `provisioning/` is byte-identical to the tree for the seed script, the common module
   and the three settings files.
5. **The shipping default reaches the approved outcome** — [`test_absent_threshold_and_auto_release_hold_every_record`](../../src/tests/narrative/test_scrub_flow_definition.py#L358).
   With only the four seeded rows (no auto-release row), a column is written and the record goes to Emily's review
   with `auto-release-off`. Before the seed, every record is held and nothing is called
   ([test](../../src/tests/narrative/test_scrub_flow_definition.py#L364)), which is the blackout `ADR-076` records.
6. **Tests print no narrative text** — the full narrative suite writes 285 bytes to the console (the summary lines
   only). The canary text stays inside the assertions.

## Elements tested

| Element | How | Result |
|---|---|---|
| Both zips vs source (11 flows) | unzip, parse, compare | Equal |
| AI prompt components | zip `customizations.xml`, `solution.xml`; DEV `msdyn_aimodel` read | Present, ids match |
| Narrative suite (`unittest`) | `python3 -m unittest discover -s src/tests/narrative -p 'test*.py'` | 184 passed, 0 failed |
| Pester: `DataverseScripts`, `DeploymentSettings`, `ProvisioningCommon`, `NarrativeRedaction` | `Invoke-Pester` | 186 passed, 0 failed, 1 skipped |
| Source gates | `python3 scripts/run-source-gates.py config/revitalise-grant-automation-build.yml` | 19 of 19 PASS |
| Flow-language gate | `python3 scripts/verify-flow-definition-language.py src/solutions/RevitaliseGrantAutomation` | exit 0, checks 1–17 |
| Assumption gates | `verify-assumption-markers.py`, `verify-assumption-register.py` | exit 0, exit 0 |
| Independent run-history audit | my own walk of every action that sees text, against `secureData` | **14 writes without secured outputs** |
| Mutant: the write stand-in returns the row | scratch copy of the suite only | `test_every_action_that_sees_text_hides_it` fails on `Write_rev_narrativeredacted` and `Write_the_decision` outputs |

## 1. Test Summary

| Layer | Run | Passed | Failed | Skipped |
|---|---|---|---|---|
| Unit (narrative suite, flow simulator with stand-in prompts) | 184 | 184 | 0 | 0 |
| Unit (Pester, seed and settings) | 187 | 186 | 0 | 1 |
| Integration (source gates + flow-language gate) | 20 | 20 | 0 | 0 |
| Artifact equality (zips vs source, components, ids) | 6 | 6 | 0 | 0 |
| End-to-End (a real DEV run of the flow) | 0 | 0 | 0 | 1 — not possible: the flow is not imported |
| Regression (other 10 flows unchanged in the zip) | 1 | 1 | 0 | 0 |
| Security (run history, prompt injection, fail-closed rows) | 4 | 3 | **1** | 0 |
| Accessibility | 0 | 0 | 0 | N-A: no screen changed |
| Performance (A-NS-33, 5,000 characters in one call) | 0 | 0 | 0 | 1 — needs a DEV run |
| Provisioning (four rows in DEV, live read) | 1 | 1 | 0 | 0 |
| **Total** | 403 | 401 | **1** | 3 |

## 2. Requirement Coverage

All results below are at V1 (flow simulator with stand-in prompts) unless the row says otherwise. Whether the real
model writes good text is `wbs:5.7`'s question and needs a live run.

| Requirement | Test case(s) | Result |
|---|---|---|
| FR-026 (labels incl. `[EMAIL]`; names follow FR-095) | `FlowAgreesWithModelOnCorpus`, canary run (labels `[ADDRESS]`, `[EMAIL]`, `[GP PRACTICE]`, age band) | PASS (V1) |
| FR-094 neutral words | [`UserStory25`](../../src/tests/narrative/test_neutral_terms.py#L291), `test_the_gendered_check_is_the_row` | PASS (V1, stand-in follows the rows) |
| FR-095 names to *They*; *my husband Derek* → *my partner* | `UserStory25`, `Names` | PASS (V1) |
| FR-096 added words and titles | `UserStory25`, `Filter_residue_titles` tests (*Ms Smith* held, *MS* not) | PASS (V1) |
| FR-097 words joined by *and* | `UserStory25` (*my partner and child*) | PASS (V1) |
| FR-098 grammar | `UserStory25` (*They receive PIP and require care*) | PASS (V1) |
| FR-099 spelling, separate step (`CO-009`) | `SpellingAcceptedWordByWord` | PASS (V1) |
| FR-100 a correction never undoes a label | spelling refused at the word; P2 holds a rewrite | PASS (V1), see observation O-1 |
| FR-101 gendered word left → review | `Filter_residue_gendered_words`, `test_each_residue_check_writes_and_holds` | PASS (V1) |
| US-025 AC-1 to AC-10 | `UserStory25.test_the_acceptance_criteria_examples` plus the classes above | PASS (V1); AC-9 see O-1 |
| NFR-012 / C-DOM-004 no narrative in run history | `RunHistoryAndVariables` | **FAIL** — defect D-1 |
| `ADR-076` rows fail closed, seeded once | `RuleRows`, Pester create-only tests, DEV read | PASS (V1; seed V3) |
| `IMP-0511` fail-safe default reaches success | `test_absent_threshold_and_auto_release_hold_every_record` | PASS |

## 3. Failed Tests

| Test ID | Layer | Description | Expected | Actual | Severity |
|---|---|---|---|---|---|
| T-SEC-1 | Security | Independent audit of `secureData` on every action that sees text, plus the mutant run above | Every write that carries text hides inputs and outputs (TAD §5.5, rev 22: *"Every action carrying text has `secureData` on inputs and outputs"*) | 14 `UpdateOnlyRecord` actions hide outputs nowhere; the suite's own run-history test fails once the write stand-in returns the row | P1 |

## 4. Defects Raised

| Defect ID | Severity | Description | Linked Test |
|---|---|---|---|
| D-1 | **P1** (HARD `C-DOM-004`) | **The flow's Dataverse writes leave the application row in run history.** [`Write_rev_narrativeredacted`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L1696) and its 11 siblings secure inputs only; [`Write_the_decision`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2172) and [`Hold_the_record_for_review`](../../src/solutions/RevitaliseGrantAutomation/Workflows/REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json#L2280) secure nothing. The connector reference lists "Update a row" as returning the row object, the same as "Get a row", and the flow's identity can read the 12 raw narrative columns, so a run would keep them for 28 days, outside column security. The intake flow already secures both sides of its writes on the same table. The test misses it because its [write stand-in returns `{}`](../../src/tests/narrative/test_scrub_flow_definition.py#L127). Fix: add `outputs` to `secureData` on all 14 writes, and make the stand-in return the row. Not a regression: the rev 20 flow already in DEV has the same gap. DEV holds synthetic data only | T-SEC-1 |

**Observations, not defects:**

- **O-1. US-025 AC-9 says a correction that would change a label is "withheld and flagged".** The approved `ADR-075`
  item 4 instead refuses that one word and writes the rest, with no flag. The label is never changed, so FR-100's aim
  holds; the wording of AC-9 and the TAD differ. Confirm the TAD reading, or ask plan-agent to align AC-9.
- **O-2. `ADR-075`'s "What a person sees by default" paragraph still says that with no settings rows the prompts run
  and columns are written.** `ADR-076` consequence 6 (later, approved) says the opposite, and the build follows
  `ADR-076`. Wording only; architect-agent's to correct.
- **O-3. The artifact was packed from an uncommitted tree** (manifest: 24 dirty paths at commit `790faa5`). The flow,
  `customizations.xml` and `provisioning/` in the artifact equal the working tree today, so the provenance holds as of
  this report; commit before any promotion.

## 5. Constraint & Compliance Verification

| Constraint ID | Description | Result | Evidence |
|---|---|---|---|
| [C-DOM-004](../../constraints/domain/domain-constraints.md#L37) | No personal data written to logs (run history is a log, [power-automate.md](../../knowledge/technology/power-automate.md#L337)) | **VIOLATION** | D-1: 14 write actions without secured outputs; the log-output test cannot fail on them. `domain-invariants` itself PASS |
| C-DOM-010 | Sensitive operations audited | PASS | No new table or column; `rev_setting` and `rev_application` audited per TAD §5.5.1; `domain-invariants` PASS |
| C-DOM-011 | Audit record schema | PASS | Unchanged platform audit; no new audited surface |
| C-DOM-030 | No special-category column drives scoring | PASS | `no-special-category-data-in-scoring` PASS |
| C-DOM-031 | Special-category columns secured | PASS | `domain-invariants`, `field-security-coverage` PASS |
| C-DOM-032 | Special-category columns audited | PASS | `domain-invariants` PASS |
| C-TECH-001 | No hardcoded secrets | PASS | Changed files carry no credential; `no-hardcoded-environment-values` PASS |
| C-TECH-004 | Inputs validated | PASS | Rule rows validated fail-closed (`RuleRows`); narrative treated as data and P2 bounds the rewrite to input words |
| C-TECH-006 | Authentication on operations | PASS | Every connector call uses `$authentication`; no new route |
| C-TECH-014 | Coverage threshold | PASS | Build `coverage-threshold` step exit 0 (manifest) |
| C-TECH-040 | Group-team role assignment | PASS | Not touched by this build |
| C-TECH-042 | Idempotent provisioning | PASS (V3) | Seed run twice in DEV: CREATED, then left unchanged; my read shows created = modified |
| C-TECH-045 | DLP-compliant connectors | PASS (static) | Same three connectors as the rev 20 flow already in DEV; no new connector |
| C-TECH-046 | Out-of-box roles untouched | PASS | Not touched |
| C-TECH-048 | Code Apps via generated data source | PASS | Not touched |
| C-TECH-051 | No fabricated platform ids | PASS (V3) | Prompt ids copied from the DEV export and re-read live from `msdyn_aimodel` |
| [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) | Every guessed platform contract registered | **VIOLATION** | One orphan: the flow and its test assume a Dataverse write returns nothing worth hiding; no register row (D-1) |
| C-TECH-053 | Level reported = level executed | PASS | Dev Summary claims V2 for the flow; confirmed V2. Seed V3 confirmed. Nothing claimed above that |
| C-TECH-054 | Runs on the CI OS | PASS (static) | `seed-settings.ps1` uses no OS-specific API; run on macOS pwsh 7, not on the ubuntu runner |
| C-TECH-056 | Diagnostic components removed | PASS | None created; my DEV calls were two read-only fetches |
| C-TECH-057 | Gates able to fail | PASS | Build preflight: negative-test coverage OK |
| [C-TECH-058](../../constraints/technology/technology-constraints.md#L128) | OPEN assumption blocks where closeable | PASS for DEV | A-NS-8, 12, 15, 22, 33, 34, 35 close only by a DEV run, so they do not block the DEV deploy; they block TST/ACC until closed |
| C-TECH-059 | Learning substrate kept | PASS | Own artifact directory; I wrote nothing into it |
| C-TECH-060 | Text within length limits | PASS | `field-length-limits` PASS; the narrative suite's 8,192-character expression test passes; 4,000-character counterpart guarded in `Compose_column_outcome` |
| C-TECH-064 | Environment state verified live | deferred-to-pipeline | The four rows verified live here; flow state after import is the deploy's to read |
| C-TECH-065 | Authorised identity | PASS | Live reads as the DEV service identity succeeded |
| C-TECH-066 | TAD tables as checked spec | PASS | `tad-coverage` unaffected; no schema change |
| C-TECH-068 | Negative access evidence | PASS | No negative access claim made |
| C-TECH-069 | Readers survive a second instance | PASS | Source gates PASS (three `AIModel` instances read) |
| C-TECH-070 | `IsSecured` where securable | PASS | `field-security-coverage` PASS |
| C-TECH-071 | Declared properties emitted | PASS | Pester: create path is a POST carrying the row's fields |
| C-TECH-073 | Metadata writes are PUT | PASS | No metadata write in this change |
| C-TECH-078 | Rendered geometry measured | PASS | No UI change |
| C-TECH-079 | Items move on evidence | PASS | No item carried |
| C-TECH-067 (SOFT) | Counts derived from source | PASS | The label-set test reads `Compose_constants`; no hand-typed count added |

## 6. Provisioning Verification

| Item | Expected | Verified via | Result |
|---|---|---|---|
| `RedactionNeutralTerms`, `RedactionTitles`, `RedactionNameRules`, `RedactionLabels` in DEV | Present, created once, never overwritten | `pac env fetch` on `rev_setting`, read-only | PASS (V3). Values not re-compared to the settings file in this read |
| Two prompt components in DEV | Present under the flow's ids | `pac env fetch` on `msdyn_aimodel`, read-only | PASS |
| `RedactionAutoRelease` absent in DEV | Fail-safe: every record to review | same fetch | PASS (absent) |

## 7. Platform Contract & Verification-Level Audit

### 7.1 Assumption register closure

| Assumption ID | Claim | Status per Dev Summary | Closing precondition | Exists yet? | Verified by test-agent | Result |
|---|---|---|---|---|---|---|
| A-NS-31 | Prompt inputs and outputs as exported | CLOSED 2026-10-16 ([L1795](../development/revitalise-narrative-scrubbing-dev-summary.md#L1795)) | DEV export | Yes | Ids and both components confirmed in zips and live | CLOSED |
| A-NS-38 | POST creates once, never overwrites | OPEN ([L1850](../development/revitalise-narrative-scrubbing-dev-summary.md#L1850)) | Two seed runs in DEV | **Yes, done 18:06** | Live read: four rows, created = modified | **CLOSED (V3)**; the register row should be updated |
| A-NS-33 | 5,000 characters rewritten whole, `finishReason` `stop` | OPEN ([L1549](../development/revitalise-narrative-scrubbing-dev-summary.md#L1549)) | A DEV run of the imported flow | No (not imported) | — | Open; closes on the DEV run |
| A-NS-8 | Both prompts answer `stop` | OPEN | DEV run | No | — | Open |
| A-NS-34 | A failed call becomes `ai-error` / `prompt-error` | OPEN | DEV run with the extractor failing | No | — | Open |
| A-NS-35 | `replace()` is case-sensitive | OPEN | One DEV test Compose | DEV yes; needs a test flow | — | Open; cheap to close in DEV |
| A-NS-15 | `sort()` ascending | OPEN | One DEV test Compose | As above | — | Open |
| A-NS-12 | `secureData` hides the AI calls in run history | OPEN | DEV run | No | Static: present both ways on all three AI calls | Open; **widen to cover the writes (D-1)** |
| A-NS-22 | Auto-release stale after a settings edit | OPEN | DEV run | No | — | Open |
| *(orphan)* | A Dataverse write's outputs need no hiding | **No row** | DEV run: read a write's outputs in run history | No | Contradicted by the connector reference and the intake flow's own practice | **Orphan — D-1** |

### 7.2 Verification levels achieved

| Component | Level claimed | Level confirmed | Evidence | Result |
|---|---|---|---|---|
| Flow 1011 (rev 23, 97 actions) | V2 | V2 | Packed, both zips equal source | PASS at V2 |
| Rewrite and spelling prompt components | V2 in the artifact; exist in DEV | V2 + live existence | zips; `msdyn_aimodel` read | PASS |
| Seed script, create-only rows | V3 (lead's DEV runs) | V3 | Live read of the four rows | PASS |
| Flow import, designer save, run | — | V3 to V5 not reached | Not imported | Not reached |

- Idempotency: seed re-run → PASS (V3). Flow import re-run: not executed.
- V4 designer open-and-save, then `verify-live-flow-definitions.py --env dev` (`IMP-1020`): not executed; owner the reviewer, after the import.
- Cross-OS: PASS (static), see C-TECH-054.
- Warnings: 5 of 5 triaged in the manifest, 0 untriaged. Diagnostic components: none.

**What the post-deploy DEV run must still prove** (synthetic data only):

1. One run on a short synthetic narrative: both prompt calls succeed and return `stop` (A-NS-8), and the written copy follows the rows.
2. One run on a 5,000-character synthetic narrative: the rewrite returns the whole text with `stop` (A-NS-33).
3. P1, P2 and P3 on real model answers: one text that repeats an extractor value elsewhere (held, `identifier-survived`), one with a gendered word the model leaves (written and held), one prompt-injection line asking the model to add a name (held, `rewrite-invalid`).
4. Run history: every pane of the extractor, both prompts and **every write** shows no narrative text (A-NS-12, D-1).
5. One run with the extractor failing: the run succeeds and the column is `ai-error` (A-NS-34).
6. Designer open-and-save of the flow, then the live-definition check (V4).

## 8. Recommendations

1. Fix D-1 before any further deploy: `outputs` on `secureData` for the 14 writes, and the write stand-in returning the row so the canary test can fail. Rebuild and re-test; the re-test is short (this report's equality and audit steps).
2. Then deploy the new artifact to DEV as approved (flow 1011 and the two prompts) and run the six checks above.
3. Mark A-NS-38 closed in the register, from the 18:06 evidence.
4. Do not promote beyond DEV until A-NS-8, 12, 33 and 34 are closed by the DEV run.

## What you need to decide

**Fix the run-history gap before the scoped DEV deploy, or deploy this build to DEV first?**

**Problem** — 14 writes in the flow would keep the raw narratives in run history, and this report therefore fails the build.
**Suggested fix** — have development-agent add the setting on the 14 writes and fix the test stand-in, then rebuild and re-test before deploying.
**What happens if you don't** — DEV holds synthetic data and its current flow already has the same gap, so a DEV-only deploy exposes nothing real; but this exact artifact must never reach TST/ACC or PRD, and deploying it needs a recorded exception because this gate is blocked.
[D-1](#4-defects-raised)

---

**Which reading of AC-9 is right: refuse the one word, or hold the whole copy?**

**Problem** — US-025 AC-9 says the copy is withheld and flagged; the approved TAD refuses only that word and writes the rest.
**Suggested fix** — confirm the TAD reading (the label is never changed either way) and let plan-agent align AC-9.
**What happens if you don't** — acceptance of `wbs:5.6` can be challenged on the wording; nothing is disclosed.
[O-1](#4-defects-raised)

---

Verification: 184 narrative tests and 186 Pester tests, 0 failures; 19 of 19 source gates; flow-language gate green;
both zips equal source; two read-only DEV reads. **Not verified:** any import, designer save or run of flow 1011
(V3 to V5), any real model answer, and the seeded row values against the settings file.

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED` | `REQUEST RETEST`

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-1133](../../logs/improvement-log.jsonl) | `no-assertion-on-shipped-content` | rework | A run-history test is only as good as its stand-in: a stubbed Dataverse write must return the row, and a write to a table holding text secures its outputs too |
| [IMP-1134](../../logs/improvement-log.jsonl) | `gate-reassures-wrongly` | rework | A test report naming a build is not approval of it; the provenance check must read the report's Status, not only that it mentions the artifact |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`
