# REVNarrativeScrubFreeText-8F1C2A44-1011-4B7A-9E21-0A1B2C3D4E11.json — design notes

`REV | Narrative | Scrub Free-Text`, Automation #5 (`wbs:5.3`, review half of `wbs:5.4`). TAD rev 20 §5.5 and §5.5.1:
`ADR-071` (direct identifiers), `ADR-072` (generative prompt stage: **built, including its run action since Iteration 4
(2026-10-06), and shipped off**), `ADR-073` (postcode register) and `ADR-074` (settings and guard rails). Rules:
`docs/development/revitalise-redaction-rules.md` v0.3. Oracle: `src/tests/narrative/redaction_reference.py` → *FLOW
MODEL* and its rev 20 sections.

Every `description` in the JSON is capped at 256 characters by the designer; the reasoning lives here,
keyed by action name.

---

## What it does, in order

| Stage | Actions | Rule |
|---|---|---|
| Run only for status 6 (Eligible for Panel) | `Stop_unless_eligible_for_panel` | TAD §5.5 |
| Re-read the row; stop if released | `Get_the_application`, `Stop_if_already_released` | rules §7a rule 1 |
| **Settings, once** (rev 20): every `rev_setting` row, kept to `Redaction*` in the flow; each row's save time | `Read_redaction_settings`, `Filter_redaction_settings`, `Select_redaction_setting_times`, `Find_setting_*` | TAD §5.5.1, `ADR-074` |
| Threshold, auto-release and its staleness | `Compose_threshold*`, `Filter_settings_saved_after_auto_release`, `Compose_auto_release` | NFR-017, `ADR-071` item 8, `ADR-074` item 5 |
| Prompt configuration and calibration | `Compose_prompt_stage_on`, `Compose_prompt_category_labels`, `Filter_prompt_category_rows`, `Select_prompt_categories`, `Filter_invalid_prompt_categories`, `Select_prompt_category_lines`, `Select_prompt_labels`, `Compose_prompt_config`, `Select_calibrated_labels`, `Filter_calibrated_labels`, `Filter_prompt_settings_saved_after_calibration`, `Compose_prompt_calibrated`, `Compose_prompt_runs`, `Compose_prompt_label_codes` | `ADR-074` items 1, 2, 4, 5; `ADR-072` items 3, 6, 8 |
| Word lists: floor plus valid additions | `Compose_kin_words`, `Compose_kin_tails`, `Compose_practice_suffixes`, `Compose_street_words`, `Compose_practice_words`; per key `Find_setting_<key>`, `Select_lines_<key>`, `Filter_entries_<key>`, `Filter_bad_entries_<key>`, `Select_forms_<key>`; then `Compose_word_list_checks`, `Compose_word_list_extras`, `Select_extra_kin_tails`, `Compose_word_lists` | `ADR-074` items 3–4 |
| **Postcode register, once** | `List_postcode_districts`, `Compose_register_rows`, `Select_register_codes`, `Compose_postcode_register`, `Compose_register_shape_table` | `ADR-073` items 1–2 |
| Per column: skip empty, keep a non-empty counterpart | `For_each_column`, `Scrub_the_column_if_it_has_text`, `Keep_or_scrub_the_column` | rules §7, §7a rules 2–3 |
| Windows of ≤ 5,000 with a 200 overlap | `Scan_the_column_in_windows` (Until), `Compose_window_end`, `Compose_window_text` | rules §5.4 |
| Stage 1: entity extraction, type → code, refinement | `Extract_entities_from_the_window`, `Select_extractor_entities`, `Select_extractor_ages`, `Select_practice_suffix_trials`, `Select_extractor_spans`, `Refine_each_name` | `ADR-071` items 1, 4; `ADR-074` item 3 |
| Stage 2: UK phone and postcode shapes; register-confirmed postcodes | `Detect_shapes_in_the_window`: the shape actions, then `Select_register_trials`, `Filter_register_hits`, `Select_register_candidates`, `Filter_register_spans`, `Select_register_spans` | `ADR-071` item 3, `ADR-073` items 3–7 |
| **Stage 3: generative prompt** (only when on and configured) | `Use_the_prompt_on_the_window`: `Compose_prompt_request`, `Run_the_redaction_prompt` (failure: `Record_a_prompt_call_failure`), `Compose_prompt_answer`, `Compose_prompt_answer_usable`, `Check_the_prompt_answer` → `Parse_the_prompt_answer`, `Validate_the_prompt_answer` (Scope), the state actions, `Join_the_prompt_answer_paths`; `Join_the_prompt_call_paths` | `ADR-072` items 4–9, `ADR-074` items 1–2 |
| The prompt result joins the column, or becomes its reason | `Compose_spans_with_prompt`, `Compose_reasons_with_prompt` (in `Finish_the_column`) | `ADR-072` items 6, 8 |
| Merge on offsets | `Merge_each_span` (sequential), `Close_the_last_span` | rules §5.2 |
| Rebuild in one pass | `Select_rebuild_pieces`, `Compose_redacted_text` | `ADR-071` item 5; rules §5.3 |
| Residue checks | `Select_residue_*`, `Compose_residue_strings`, `Select_residue_district_positions`, `Filter_residue_street_words`, `Filter_residue_practice_words`, `Compose_residue_reasons` | `ADR-071` item 6, `ADR-073` item 5, `ADR-074` item 3 |
| Write only what fits | `Write_or_hold_the_column`, `Write_the_counterpart` (Switch, one write per counterpart) | rules §7 (4,000) |
| Decide once per record | `Compose_lowest_score` … `Compose_decision`, `Write_the_decision` | rules §7, `ADR-071` items 7–8 |
| Tell the process owner | `Tell_the_process_owner_if_review_is_needed` (card, then HTML fallback) | FR-030, NFR-018 |
| Any failure: hold and alert | `Find_the_failed_action`, `Describe_the_failure`, `Hold_the_record_for_review`, `Alert_on_failure` | NFR-018, FR-010 |

## Why it is built like this

**No variable ever holds text** (`ADR-071` item 5). Variables are `windowStart`, `spans` (offsets, a
one-character code and a score), `merged`, the merge cursor, `scores`, `reasons` (fixed codes), flags,
and rev 20's `promptState` (`''`, `error` or `invalid`) and `promptSpans` (offsets). Variable actions
cannot be secured at all, so this is the only way to keep them out of the run history.
`test_scrub_flow_definition.py → RunHistoryAndVariables` and `PromptStageInTheShippedFlow` run a narrative
carrying a made-up word through the flow, including a prompt answer that quotes it, and assert that word
appears in no variable assignment, and in no action's inputs or outputs unless that action's
`secureData` hides them. That test found one unsecured action during this build
(`Select_prompt_occurrence_counts`, whose input rows carry the quotes); it is secured.

**Codes, not labels, travel through the flow.** `N` name, `F` family member, `G` GP practice, `S`
address, `P` phone, `E` email, `0`–`8` an age band. `Compose_label_text` turns a code into its label
only in the rebuild. Precedence is the position in `012345678NFPEGS`: `indexOf()` is case-insensitive,
so no two codes differ only by case.

**A shape, register or prompt span carries score 2**, above every real extractor score (0 to 1): a
merged span takes the lowest score of its parts, so none of them lowers it, and a span that is only one
of them is left out of the record confidence (`Compose_record_confidence` → null at 2).

**The residue checks read a skeleton, not the redacted text.** `Compose_skeleton_text` is the rebuild
with `|` where each label goes. `[GP PRACTICE]` contains the word *practice*, so checking the
redacted text would send every record with a practice to review for its own label. The district check
reads the skeleton too, so a district inside a replaced span never trips it.

**Every expression is total under eager `if()`.** `knowledge/technology/power-automate.md` records
both answers to whether `if()` evaluates its untaken branch. So every `substring()` is bounded with
`min`/`max`, every slice reads a padded string, `range()` never gets a count below 1, and array
access goes through `first(skip(…))`. The simulator evaluates `if()` eagerly and throws where the
platform documents a throw.

**Array against array is one cross-product `Select`, never a nested loop.** `Select_shape_trials` set the
pattern: every candidate position against every shape, over `range(0, candidates × shapes)`. Rev 20 uses
it three more times: the register shapes (`Select_register_trials`), the effective practice suffixes
against each Organization value (`Select_practice_suffix_trials`, which is what lets that list grow
from a setting), and each prompt quote's occurrences (`Select_prompt_trials`).

### Rev 20: settings (`ADR-074`)

**Every row is read, and the filter is in the flow.** `Read_redaction_settings` has no `$filter`, so a
new `Redaction*` row joins the guard rails without a flow change. Names are compared lower-cased, so the
result does not depend on whether `equals()` is case-sensitive. `PostcodeRegionMap` and every other
non-`Redaction` row is dropped by `Filter_redaction_settings` before anything reads a save time; a
mutation that drops that filter fails 208 tests.

**A save time is read for every `Redaction*` row, and a row without one fails the run.**
`Select_redaction_setting_times` calls `ticks()` on `modifiedon` with no fallback, on purpose: a missing
time would otherwise make the staleness check silently pass. A failed run holds the record and alerts.

**Word lists: one malformed line voids the whole row.** `Filter_bad_entries_<key>` flags a line that is
not 2 to 40 characters of a–z, space, hyphen and apostrophe, or that has no letter at all (a refinement
of `ADR-074` item 4, in the fail-closed direction: `--` would otherwise be a valid "word" that
normalises to nothing). Each valid entry is put into the form of the text it is compared with
(`Select_forms_<key>`): kinship words and practice suffixes as the name normaliser leaves them (a hyphen
becomes a space), street and practice words as the residue word string reads text (hyphen and
apostrophe become spaces). `union()` keeps the floor first and adds each new entry once.

**Prompt categories are sorted by label** (`sort(…, 'label')`, `A-NS-15`), so `Categories` and
`AllowedLabels` do not depend on the order Dataverse returns rows in. `$orderby` was not used because no
flow in this solution uses it on *List rows*; `sort()` is already in use here.

### Rev 20: the register (`ADR-073`)

**Read once, joined into one string.** `Compose_postcode_register` holds `|AB1|AB10|…|` (about 15,000
characters, no applicant text, so not secured) and an `ok` flag: at least 3,000 rows. A failed read is
handled: `Compose_register_rows` runs after `Failed` too and coalesces to an empty list, so a failed read
becomes `postcode-register-unavailable` and not a failed run. Measured 2026-10-06, read-only: DEV holds
3,394 rows and the entity set name is `rev_citysettlementregisters` (E1).

**A district is a district only on its own.** `Select_register_trials` rejects a district shape followed
by ` 9AA` (an inward code), so `LS6` in `LS6 2AB` is part of the postcode, which the rev 19 shape owns.
The cue words are read from the whole column text, 12 characters each side, normalised as the name
context is, so a cue in the previous window still counts.

### Rev 20: the prompt stage (`ADR-072`, built to TAD §12.6.1)

**The run action (Iteration 4, 2026-10-06).** The reviewer created *REV Narrative Redaction Prompt* in DEV
inside the solution (TAD §12.6.1 R1). Its component is copied from the DEV export into
`Other/Customizations.xml` (`A-NS-9`), and `Run_the_redaction_prompt` names it by the id in that export.
The input names (`Categories`, `AllowedLabels`, `Narrative`) and output names (`text`, `finishReason`) are
E1 from the export's run specification (`A-NS-20`). The action's operation id
(`aibuilderpredict_customprompt`), its `recordId` parameter and the `item/requestv2/<input>` form match the
*Run a prompt* action a maker saved in the DEV designer on 2026-10-07 (E1;
`src/tests/narrative/fixtures/run-a-prompt-action.json`). The answer path, `body` → `responsev2` →
`predictionOutput` → `text` / `finishReason`, is the one the designer itself wrote for this action's outputs
in the same test flow on 2026-10-07 (E1; the fixture's `outputs_read_by_the_designer`). The flow keeps its
standard `body()?[…]` form; `test_the_answer_path_is_the_one_the_designer_writes` compares the two key by key.
A null answer is still `prompt-error`. A failed call sets `promptState` to `error` and
`Join_the_prompt_call_paths` ends both paths, the same shape as the extractor's. The stage still ships off:
no `RedactionPromptStage` row is seeded. `test_prompt_component.py` ties the action to the component and the
component to the template in `docs/development/revitalise-redaction-prompt.md`.

**Validation is a Scope whose failure means invalid.** The workflow definition language has no type
test, so an answer that is not an array of objects (an object, a string, `null`, an item that is a
string) makes an action inside `Validate_the_prompt_answer` fail. That failure is handled
(`Compose_prompt_state_if_malformed`) and becomes `prompt-output-invalid`, which is what `ADR-072` item 6
asks for. An unparseable answer fails `Parse_the_prompt_answer` instead, which is `prompt-error`, as item 8
asks. `Join_the_prompt_answer_paths` ends every path in one succeeding action.

**Occurrences come from `split()`, not `nthIndexOf()`.** The TAD names `nthIndexOf()` (`A-NS-11`), which no
flow here uses. The k-th occurrence's offset is `length(join(take(split(window, quote), k), quote))`:
`split` and `join` are already used in this flow, and the occurrences are left to right without overlap
(`A-NS-24`). The reference model uses the same rule.

**`promptState` is per column, and error wins.** `Record_an_unusable_prompt_answer` and
`Record_an_unparseable_prompt_answer` set `error`; an invalid answer sets `invalid` only when the state
is still empty. At the end of the column, prompt spans are used only when the state is empty, so one bad
window discards the column's whole prompt result (`ADR-072` item 6). A column whose extractor failed is
`ai-error` only; its prompt result is not reported.

**Two guards are deliberately redundant**, and the mutation run shows each as an equivalent mutant: the
`ok` term in a prompt trial (a failing item already has zero occurrences), and the window-level discard in
`Compose_prompt_spans_after_window` (the column-level state discards them anyway). Both are kept as defence
in depth inside a privacy control.

**Nesting depth is now 8, which is the documented limit, counted as containers.** `Validate_the_prompt_answer` sits at depth 8 and its
failure-descent branch too. **Assumption `A-NS-26` (documentation only, not yet confirmed):** the platform is taken to count
containers and not the leaf actions inside the 8th; if it counts those leaves too, the flow imports but cannot be saved in the
designer. The DEV import and a designer open-and-save settle it. **Any further container inside it, or inside `Check_the_prompt_answer`, breaks
the limit**: `PlatformLimits` fails the build if it does.

### The failure descent

`Describe_the_failure` is regenerated from the action tree, one case per container child at every level,
so `verify-flow-definition-language.py` check 7 finds no undescended container. The generator reproduced
the Iteration 2 tree byte for byte before it was used for rev 20.

**A container with no container children gets no Switch** (2026-10-08). The generator emitted a
`Describe_the_failure_inside_<X>` Switch with `cases: {}` and only a default at every leaf container;
the designer refuses to save a Switch without a case ("add a valid case"). Those ten Switches are
replaced by their default `Set_failure_detail_from_<X>` action, which takes the Switch's `runAfter`.
The `Find_the_failed_step_inside_<X>` descent check 7 needs is unchanged.

**Writes use `UpdateOnlyRecord` (*Update a row*), not `UpdateRecord`** (2026-10-08). `UpdateRecord`
is now the connector's *Upsert a row*; every write here targets the trigger row, so an update-only
write is the honest shape and fails rather than creating a row if it is gone. `Reset_prompt_state`
sets `@string('')`: a literal `""` reads as a missing value to the designer's flow checker.

**One write per counterpart (`Write_the_counterpart`).** A Dataverse update names its columns
statically, as flat `item/<column>` keys (the TAD §5 write-shape rule), so a loop over columns
cannot write a column chosen at run time. A 12-case Switch is the smallest shape that can.

**The failure alert carries the action name and error code, never the platform's message.** An AI
Builder or Dataverse error could quote the input. The run link in the alert is how an operator
reads the rest.

## Re-running

The trigger is a status change to Eligible for Panel. To scrub again (for example after the grant
admin clears a counterpart, rules §7a rule 4), **resubmit the latest run** from the flow's run
history: the flow re-reads the row, so the resubmission sees the cleared column. A released record is
never touched.

## Assumptions marked in this file (Dev Summary §3.10 of `docs/development/revitalise-narrative-scrubbing-dev-summary.md`)

| Id | Where | Claim |
|---|---|---|
| A-NS-1 | `Compose_extractor_type_codes` | The extractor's `type` strings are the PascalCase names in the map |
| A-NS-2 | `Select_extractor_spans` | `startIndex` counts in the same units as `substring()` |
| A-NS-3 | `Compose_window_end` | A 5,001-character call is rejected, so windows are needed |
| A-NS-5 | `Extract_entities_from_the_window` | `en` is the right language for UK English |
| A-NS-8 | `Compose_prompt_answer_usable` | A normal stop is `finishReason` `stop` |
| A-NS-9 | `Run_the_redaction_prompt` | The component copied from the DEV export imports into TST/ACC and PRD with the same id |
| A-NS-10 | `Parse_the_prompt_answer` | The answer's `text` is JSON that `json()` parses |
| A-NS-12 | `Extract_entities_from_the_window` | `secureData` on the AI Builder action hides both panes |
| A-NS-13 | `Extract_entities_from_the_window` | Operation `aibuilderpredict_entityextraction`, parameters `item/requestv2/text` and `item/requestv2/language` |
| A-NS-15 | `Merge_each_span`, `Select_prompt_category_lines` | `sort(array, '<property>')` exists and sorts ascending |
| A-NS-16 | `Compose_window_entities` | The entity array is at `responsev2/predictionOutput/results` (or `…/result/entities`); null at both is ai-error |
| A-NS-18 | `Compose_window_end` | `take()` accepts a string; `lastIndexOf()` returns -1 when absent |
| A-NS-19 | `Describe_the_failure*` | `result()` of a loop shows a failed iteration after later ones succeed |
| A-NS-20 | `Run_the_redaction_prompt` | One call accepts 16,000 characters of categories plus a 5,000-character window (names and parameter form: E1) |
| A-NS-21 | `List_postcode_districts` | One *List rows* response holds all 3,394 register rows |
| A-NS-22 | `Select_redaction_setting_times` | `modifiedon` is ISO 8601, `ticks()` reads it, and a changed save moves it |
| A-NS-23 | `Run_the_redaction_prompt` | The prompt can be created, saved and run with *Move data across regions* unticked; unanswered, because DEV's setting was already on (R0), so open for TST/ACC and PRD |
| A-NS-24 | `Select_prompt_item_counts` | `split()` is case-sensitive and finds occurrences left to right without overlap |

**If A-NS-13 or A-NS-16 is wrong, the flow fails closed.** A wrong operation fails the call, which is
`ai-error` for the column. A wrong output path reads null, which `Handle_the_extractor_answer`
treats as `ai-error`, never as *no entities*. **If A-NS-21 is wrong** (a page shorter than the
register), fewer than 3,000 rows arrive and every record gets `postcode-register-unavailable`.
**If A-NS-22 is wrong** (no `modifiedon`, or a format `ticks()` rejects), the run fails and the record
is held.

## What is NOT here

- **A prompt run.** The stage ships off, and no run has been made in any environment (TAD §12.6.1 R2–R5).
- **Indirect identifiers** (rules §10), after Emily's input.
- **Seeded settings.** No `Redaction*` row is seeded by any deploy (`ADR-074` item 7). Absent is the safe
  value for every row.
