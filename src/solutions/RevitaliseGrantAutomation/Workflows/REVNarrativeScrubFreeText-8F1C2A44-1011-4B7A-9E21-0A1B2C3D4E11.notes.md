# REV | Narrative | Scrub Free-Text — maker notes

**Automation #5 · `wbs:5.3` (the flow), `wbs:5.6` (the client's rules), spelling under `CO-009` (approved, unbilled) ·
TAD rev 22, `ADR-075` (approved 2026-10-16), amended by rev 30, `ADR-082` (approved 2026-10-21) · rebuilt in Iteration 9
and changed in Iteration 14 of
[the narrative Dev Summary](../../../../docs/development/revitalise-narrative-scrubbing-dev-summary.md).**

This is a rebuild, not an edit. The rev 20 flow (313 actions: windows, shape detectors, kinship refinement, a merge loop,
a prompt used as a detector, and a failure diagnosis inside every container) is in git history. The rev 22 flow had
90 actions; with TAD rev 23 (`ADR-076`, Iteration 10) it had 97; with Iteration 11 (name fragments, 2026-10-19) it had
100; with TAD rev 25 (`ADR-078`, Iteration 12) it had 97; **with TAD rev 29 (practice names the extractor misses,
Iteration 13) it had 100; **with TAD rev 30 (`ADR-082`, Iteration 14: one extractor call per batch of columns, one prompt that
rewrites and corrects spelling) it has 109, nested at most 6 deep, no `Until` and no `result()`**. The ceiling the definition
test holds is now **125 actions and 6 levels** (the platform allows 500 and 8): a change that would cross it goes back to the
reviewer with what it proposes to remove. *Previously read: "100 is the ceiling the definition test holds: the next addition
must remove something."*
Rev 23 moved the rules Emily may change out of the rewrite prompt into four `rev_setting` rows (below).

## What it does, in the order a maker reads it

| Part | Actions | What it does |
|---|---|---|
| Start | `Stop_unless_eligible_for_panel`, `Initialise_reasons`, `Initialise_scores`, `Initialise_any_scrubbed`, `Initialise_batch_plan` | Runs only when the status becomes Eligible for Panel (6). Four variables, none of which ever holds text (`batchPlan` holds column names and numbers) |
| Read once | `Get_the_application`, `Stop_if_already_released`, `Compose_constants`, `Read_redaction_settings`, `Filter_redaction_settings`, eight `Find_setting_*`, `Select_street_word_lines`, `Select_practice_word_lines`, `Select_neutral_term_lines`, `Select_neutral_term_targets`, `Filter_neutral_targets_that_are_terms`, `Select_title_lines`, `Select_label_lines`, `Compose_threshold_number`, `Compose_settings`, `List_postcode_districts`, `Select_register_codes`, `Compose_postcode_register` | A released record is never touched. The constants; the threshold (a review hint, `ADR-078`), the kill switch and the street and practice lists; **the four rule rows, validated, and turned by `Compose_settings` into the prompt's four inputs and checks P2's and P3's lists (one source, `ADR-076` item 2)**; the postcode register (only for `residual-district`) |
| Choose the columns | `Select_column_reasons`, `Filter_columns_to_scrub` | A column is scrubbed only with raw text, an EMPTY counterpart (the grant admin's text is never overwritten) and at most 5,000 characters, and only when **all four rule rows are valid** and `RedactionPromptStage` is not `off` |
| Plan the batches (`For_each_plan_column`, sequential) | `Compose_batch_step`, `Append_batch_plan` | **Next fit** (`ADR-082` item 1): the chosen columns, in their fixed order, get a batch number so that a batch's texts and the two-line-feed separators between them total at most 5,000 characters (the extractor's per-call limit; both numbers are in `Compose_constants`). A column opens the next batch when it does not fit; none is split. Each plan entry is `{raw, red, batch, used}`: names and numbers only |
| Per batch (`For_each_batch`, sequential) | `Filter_batch_columns`, `Select_batch_texts`, `Compose_batch_joined`, `Select_batch_layout`, `Extract_entities_from_the_batch`, `Compose_batch_entities` | **One extractor call per batch** (usually one per application: five columns of about 1,200 characters in all, 33 credits where five calls cost about 100). The columns' raw text, exactly as stored, is joined by two line feeds; `Select_batch_layout` gives each column its `start` and `end` in the joined text. If the call did not answer, every column of the batch is `ai-error`, nothing sent to the prompt, nothing written; other batches are unaffected. With no column chosen the loop runs zero times and **no call is made** |
| Per column (`For_each_column`, sequential, **inside the batch loop**) | the If `Label_rewrite_and_check_the_column`; first `Filter_column_entities`, `Select_column_entities` | Each entity that **touches** the column is rebased to it (and clamped, `A-NS-2`), with `crosses` when it runs into a neighbour. An entity wholly inside the separator touches no column and is dropped. **A labelled entity that crosses a boundary holds both columns** (`overlapping-identifiers`, not written): it rides on its own diagonal cell of `Select_overlap_trials` as a `P` |
| — label | `Set_any_scrubbed`, `Select_entities`, `Select_raw_classes`, `Compose_raw_classes`, `Select_entity_ages`, `Select_spans`, `Select_practice_suffix_hits`, `Select_practice_words`, `Select_practice_spans`, `Filter_unmapped_entities`, `Filter_labelled_spans`, `Select_overlap_trials`, `Filter_kept_spans`, `Select_labelled_pieces`, `Compose_labelled_text` | Each entity gets its code (rules 4.2: a GP practice only by its suffix, an age as its band). **A person's name** (Iteration 11) is trimmed past a leading *Dr*, *Dr.* or *Doctor*, so the prompt sees "Dr [NAME]", and widened over one fragment joined by a hyphen or apostrophe on each side (*Holloway-Reed*, *O'Brien*; never the possessive *'s*): `Select_entity_ages` fields `trim`, `fwd`, `back`, read from the letter classes in `Compose_raw_classes`. **A GP practice the extractor missed** (TAD rev 29): each case-sensitive capitalised practice suffix (*Surgery*, *Medical Centre*, *Health Centre*, *Medical Practice*, *Group Practice*, *Family Practice*, plus `RedactionPracticeWordsExtra` capitalised; `Compose_settings.practiceSuffixes`), at most 25 per suffix per column, becomes a `[GP PRACTICE]` span back over at most four capitalised words or *St*/*St.*; the spans join the extractor's after them in `Filter_labelled_spans`, so containment and overlap apply as before. A span inside another is dropped; two that overlap without nesting hold the column. The labelled text is rebuilt by offset, so **the model never receives a value the extractor found** |
| — rewrite and spell | `Run_the_rewrite_prompt`, `Compose_rewrite`, `Compose_final_text` | **One prompt, one call per column** (`ADR-082` item 4). It corrects spelling first, then applies the client's key, names to *They*, the grammar, and labels what the extractor missed. `Compose_rewrite` splits the answer at the first `###CORRECTIONS###` (below). `Compose_final_text` is a one-line alias of the rewrite |
| — check | `Compose_check_texts`, `Select_valid_corrections`, `Filter_surviving_identifiers` (P1), `Filter_added_words` (P2), the residue actions (P3, including `Filter_spans_with_a_joined_fragment`), `Compose_column_outcome`, `Set_reasons`, `Set_scores` | P1 and P2 decide whether the column is written; P3 writes it and holds the record |
| — write | `Write_the_column`, `Write_the_counterpart` (a `Switch`, 12 cases) | One `UpdateOnlyRecord` per counterpart, each naming its column (TAD §5 write-shape rule). Kept as twelve plain cases on purpose (`ADR-075`) |
| Decide and tell | `Filter_record_reasons`, `Compose_decision`, `Write_the_decision`, `Tell_the_process_owner_card` (fallback `Tell_the_process_owner`) | **The flow never releases (`ADR-078`).** `rev_redactionreviewrequired` = true and the lowest score on every scrubbed record; `rev_redactionreleased` is never written. One Teams card per scrubbed record, *Narrative ready for your review*, with the reference and the reason codes as hints (*None found by the checks* when there are none). Only the process owner releases |
| Failure handler | `Hold_the_record_for_review`, `Compose_run_link`, `Alert_on_failure`, `End_the_run_as_failed` | Runs when `Scrub_free_text` fails or times out: hold, alert with the run link, end the run as Failed. The alert does not name the failed step; open the run (secured) |

## The three checks (`ADR-075` items 5 to 7)

| Check | Action | Rule | On a hit |
|---|---|---|---|
| **P1** — no found identifier survives | `Filter_surviving_identifiers` | Every labelled value, normalised (lower case; punctuation, apostrophes and brackets to spaces), searched at word boundaries in the final text | `identifier-survived`, **not written** |
| **P2** — the rewrite added no word | `Filter_added_words` | Every word of the rewrite (labels removed) must be a word of its input, a closed-list word (`Compose_settings.closedPipe`: the fixed grammar set and extractor labels of `Compose_constants.closedWords`, **plus the neutral words of `RedactionNeutralTerms` and the words of `RedactionLabels`**), a plural form of an input word (`rely` from `relies`), **or the corrected half of a declared correction that passed the pair rule** (`Select_valid_corrections`, below) | `rewrite-invalid`, **not written** |
| **P3** — residue | `Select_residue_*`, `Filter_residue_*` | On the final text with every label replaced by a bar character: a 9-digit run, a postcode shape, `@`, a street word, a practice word, an age phrase, a register district, **a word `RedactionNeutralTerms` replaces**, **a `RedactionTitles` title with its capitals** (`Filter_residue_titles`), and **a label with letters joined to it by a hyphen or apostrophe** (Iteration 11, `name-fragment`): in the column before labelling (`Filter_spans_with_a_joined_fragment`, any kept span) or in the final text (`\|-A`, `\|'AA`, `A-\|`, `A'\|` on the letter classes; after an apostrophe two letters or more, so *[NAME]'s* does not trip it) | `residual-<kind>` (`gendered-term`, `title`, `name-fragment`, …), written, record flagged |

A rewrite more than 10% shorter in words than its input is written and flagged (`rewrite-dropped-text`): fidelity, not
privacy. So is a rewrite with at least two fewer `. , ; : ! ?` than its input and more than 10% fewer
(`rewrite-dropped-punctuation`, Iteration 11; counts `inputPunct` and `rewritePunct` in `Compose_check_texts`). A rewrite over 4,000 characters is not written (`redacted-exceeds-4000`).

**The merged answer, and the declared pair** (`ADR-082` items 5 and 6). The prompt answers with the rewritten text and, only
if it corrected a word, a line holding exactly `###CORRECTIONS###` and one `wrong=>right` line per correction.
`Compose_rewrite` splits at the **first** delimiter: the text before it, trimmed, is the rewrite (`text`), each line after
it is a declared correction (`corrections`); no delimiter means no corrections; `finishReason` must be `stop`. A line that
is not `word=>word` is ignored. `Select_valid_corrections` turns each declared line into its right word, lower case, or
`''`, and **P2 accepts a word it did not get from the input only if it is one of those**. A line is valid when **all** hold:
`wrong` is a word of the labelled input *as written there* (`Compose_check_texts.inputCase`, case kept; `replace()` is
case-sensitive, `A-NS-35`) and starts with a lower-case letter; `right` starts with the same letter; their lengths differ by
at most 2; both are letters with an optional internal hyphen or apostrophe (no brackets); `wrong` is not a closed-list word;
`right` is not a gendered word. **Why that cannot let an added word through:** a word outside the input, the closed list and
the plural forms is accepted only as a near-spelling of a lower-case word already in the text, a change of at most two letters.
Names, streets and numbers are labelled before the model sees the text or start with a capital, so they cannot be the
corrected half of a valid pair. **Lost, stated plainly:** the old rule proved *where* a corrected word sat; the pair rule
cannot, because a rewrite changes word counts, so a valid corrected word may appear anywhere and more than once. A word the
model changes without declaring it, or beyond the rule, is `rewrite-invalid` and the column is not written; with two calls
the slip was left as written. How often that happens is unmeasured (`A-NS-43`, the `wbs:5.7` scoring run).

**Deployment order for the prompt (read before importing).** Deploy this flow first, edit the prompt second
([prompt document §1](../../../../docs/development/revitalise-redaction-prompt.md), R1d). The new flow with the old prompt
writes the rewrite with no spelling correction and no blackout. The new prompt with the old flow holds every column: the old
flow reads the delimiter line's words as added words.

## The label set is in one place

`Compose_constants.labels` is the only place in the flow that spells a label. Every other action reads it
(`outputs('Compose_constants')?['labels']?['N']`, …). The reviewer expects one more change to the labels after Emily has
tested (2026-10-16); that change is: edit `labels` here, edit `LABEL_BY_CODE` in `src/tests/narrative/redaction_reference.py`,
and add any new label word to `closedWords`. `test_the_label_set_is_read_from_one_place` fails until all three agree.
`[FAMILY MEMBER]` stays in the set by that decision, although no rule produces it any more.

## Settings (TAD §5.5.1, rev 23; rev 25 `ADR-078`)

| Row | Effect | Absent |
|---|---|---|
| `RedactionConfidenceThreshold` | Below it: the hint `below-threshold`. Seeded create-only at `0.85` (`ADR-078` item 5); never a release gate | The hint `threshold-missing-or-invalid` |
| `RedactionPromptStage` | `off` is the kill switch: nothing is scrubbed, `prompt-stage-off` | The prompts run |
| `RedactionStreetWordsExtra`, `RedactionPracticeWordsExtra` | Added to P3's lists | The built-in list |
| **`RedactionNeutralTerms`** | `word = neutral word` (or `= first or second`) per line: the prompt's `NeutralTerms`; P2's neutral words; P3's gendered words | **Nothing is scrubbed**: `redaction-setting-invalid:RedactionNeutralTerms` |
| **`RedactionTitles`** | One title per line: the prompt's `Titles`; P3's title check | The same, for this key |
| **`RedactionNameRules`** | Plain-word rules for `[NAME]`: the prompt's `NameRules` only | The same |
| **`RedactionLabels`** | `[LABEL] = what it covers`: the prompt's `Labels`; P2's label words | The same |

The four rule rows are required (a list meant to be empty is the line `none`), validated each run, and a malformed one
stops the scrub of the record as an absent one does (`ADR-076` item 5). They are seeded once per environment by
`seed-settings.ps1` (`createOnly`) and are the process owner's from then on. A malformed street or practice row is
ignored as a whole and named. The retired rows (`RedactionPromptCalibrated`, `RedactionPromptCategory.*`,
`RedactionKinshipWordsExtra`, `RedactionPracticeSuffixesExtra`, `RedactionNeutralTermsExtra` and, since rev 25,
`RedactionAutoRelease`) are not read, and a leftover one changes nothing. `modifiedon` is no longer read (`ADR-078`):
an edit to any row needs no re-confirmation. *Previously read: saving a row after `RedactionAutoRelease` made
auto-release stale.*

## What is never in run history

Every action whose inputs or outputs carry narrative text has `secureData` (`test_every_action_that_sees_text_hides_it`).
**That includes all 14 writes, on both sides** (test report 20261016-3, D-1): "Update a row" returns the updated row, which
holds the 12 raw narratives (`A-NS-39`).
No variable ever holds text: `reasons` holds codes, `scores` numbers, `anyScrubbed` a flag, `batchPlan` column names and numbers (`ADR-082`: the joined text and the entities live in `Compose` and `Select` actions that secure their inputs, and the Selects and the extractor call their outputs too). The Teams card and the alert
carry the application reference and reason codes only.

## Platform rules this flow follows (each one cost a defect before)

| Rule | Where | Source |
|---|---|---|
| A `substring()` start must be below the string length, also with a length | every read from the raw text uses `concat(raw, ' ')` as its source | `IMP-1109` |
| Nothing outside a loop reads an action inside it | the column outcome is carried out in `reasons` and `scores`; the batch count and the plan are read by `variables()` | `IMP-1098`, check 12 |
| A `Foreach` inside a `Foreach` reads actions of its **enclosing** iteration (`Compose_batch_entities`, `Select_batch_layout`): inside-out, not what check 12 forbids, **not yet saved in a designer** | `For_each_column` inside `For_each_batch` | `A-NS-42`, open |
| `range()` is never given 0; `take(range(0, max(n, 1)), n)` is the empty array for `n = 0` | `For_each_batch`'s `foreach` | the simulator's strict reading (`range` below 1 throws); `A-NS-42` covers the save |
| One variable per `InitializeVariable`; a `SetVariable` never reads its own variable | `Compose_column_outcome` computes, `Set_*` assigns | `IMP-0821`, `IMP-0816` |
| An update is `UpdateOnlyRecord`; a `Switch` has cases | `Write_rev_*` | `IMP-1095` |
| `first(skip(x, n))`, never `x[n]` with a computed `n` | the overlap and rebuild Selects | TAD `A-NS-29` (so not needed) |

## Open assumptions in this file (register: Dev Summary Iteration 9, §9.6)

| Id | Where | The guess |
|---|---|---|
| ~~A-NS-31~~ | `Run_the_rewrite_prompt` | **Closed 2026-10-16** by the DEV export after R1b: the run action names the exported id and passes the exported input names (prompt document §4a). Rev 30 changes the template, not the id or the inputs; the refreshed export after R1d re-confirms it |
| A-NS-33 | `Compose_rewrite` | A 5,000-character rewrite comes back whole with a normal stop |
| A-NS-8 | `Compose_rewrite` | A completed run's `finishReason` is `stop` |
| A-NS-34 | `Compose_batch_entities`, `Compose_rewrite` | After a failed call, `body()` is readable and the answer path is null |
| A-NS-35 | `Select_valid_corrections`, `Filter_residue_titles` | `replace()` is case-sensitive (the pair rule's lower-case-first-letter and *as written there* tests and the title check rely on it; the title check uses it instead of `contains()`, so TAD `A-NS-37` does not arise) |
| A-NS-12, A-NS-13, A-NS-16, A-NS-5 | `Extract_entities_from_the_batch`, `Compose_batch_entities` | The extractor's operation, language, answer paths and secured history, unchanged from rev 20 |
| A-NS-41 | `Select_batch_layout`, `Filter_column_entities`, `Select_column_entities` | The extractor's `startIndex` and `length` count UTF-16 characters of the **whole** joined text, the separators and a CRLF inside a column included and unmodified |
| A-NS-42 | `For_each_batch`, `For_each_column`, `Compose_batch_entities` | A `Foreach` inside a `Foreach` saves in the designer when an inner action reads an action of the enclosing iteration |
| A-NS-43 | `Compose_rewrite`, `Select_valid_corrections` | The merged prompt returns the corrected text, then a `###CORRECTIONS###` line and `wrong=>right` lines, often enough that `rewrite-invalid` from an undeclared or refused correction is rare |
| A-NS-44 | `Extract_entities_from_the_batch` | A joined call is billed 20 credits per started 1,000 characters of the whole text, separators included |
| A-NS-45 | `Extract_entities_from_the_batch` | `msdyn_aievent` keeps the input of every AI Builder call (`IMP-1190`): open, not designed, not made worse by batching |
| A-NS-15 | `Select_labelled_pieces`, `Compose_column_outcome` | `sort(array, 'start' / 'score')` sorts ascending by that number |
| A-NS-21 | `List_postcode_districts` | One page holds the register. (`A-NS-22`, `modifiedon` is ISO 8601, is withdrawn with `Filter_settings_saved_after_auto_release` by `ADR-078`) |
