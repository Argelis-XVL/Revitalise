# REVScoringCalculateAndFlag-8F1C2A44-1002-4B7A-9E21-0A1B2C3D4E02.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every action, trigger, parameter and schema property - exceeding it blocks the flow from being saved in the designer at all. The condensed descriptions actually shipped in this file keep the essential fact and citation; the full reasoning that used to live there is preserved here, keyed by the same JSON path, so none of the domain detail this project treats as load-bearing documentation is lost.

## `/properties/definition/description`

REV | Scoring | Calculate & Flag. Serves FR-011 (circumstance score; maximum 60, confirmed in revision 0.3 - see Calculate_circumstance_score), FR-012 (invert the life-satisfaction answer), FR-013 (configured Likert point values), FR-014 (Auto-pass / Borderline / Auto-reject against configured thresholds), FR-015 (income flag, evaluated separately from the score), FR-016 (special-category data excluded from the calculation), FR-017 (thresholds changeable without touching this flow), FR-018 (an override is never overwritten), FR-019 (Borderline routed to a human), FR-020 (Auto-reject leaves the active list), FR-022 (no automated outcome when a scored answer is missing).

FR-016 IS ENFORCED STRUCTURALLY, NOT BY INTENTION. The Dataverse trigger delivers the whole row, so the guarantee is that no expression anywhere in this definition references rev_narrativeraw, rev_otherconditionraw, rev_conditionprofile or rev_supportrecipientconditionprofile. That is a grep-able property, and config/revitalise-grant-automation-build.yml has a build step that fails if any of those four column names appears in this file. Special-category data therefore cannot influence an automated outcome (SDD FR-016, DUAA 2025 position).

IDEMPOTENT: re-running recalculates the same score from the same answers, and the override guard means a re-run can never overwrite a decision the process owner has taken (TAD section 5.2).

## `/properties/definition/triggers/When_an_application_is_created/description`

Row created on rev_application only - not modified. A modified trigger would re-score the row every time the process owner edited it, and would fight the override guard. RUNS AS THE FLOW OWNER, not the modifying user: if the process owner creates an application by hand in the model-driven app, the scoring must still be able to write an error-log row on failure, and she holds no create privilege on rev_errorlog. CONFIRM ON FIRST IMPORT: the numeric value of subscriptionRequest/runas below expresses 'Flow owner' and is one of the values listed in Dev Summary section 7 as written from convention rather than validated.

## `/properties/definition/actions/Stop_if_the_process_owner_has_overridden_this_application/description`

FR-018 short-circuit, and it is the FIRST action on purpose. A named human's decision outranks the automation, so the flow exits before it reads configuration or computes anything - there is no path from here to a write that could overwrite an override. On a create trigger this is normally false; it exists because the flow must stay safe to re-run by hand (TAD section 5.2).

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/description`

Every number this flow decides with comes from a rev_setting row read at RUN TIME, retrieved by alternate key on rev_name. Nothing is bound at import and nothing is a literal - that is what FR-017 and NFR-019 buy: the board changes a threshold by editing a row in the model-driven app, and auditing on rev_setting evidences the change against the decisions it affected. config/revitalise-grant-automation-build.yml fails the build if a threshold key name ever appears next to a numeric literal in this folder.

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/actions/Setting_LikertPointMap/description`

FR-013. Maps each rev_likertresponse option value to its point value. Value 1 ('None of the time') scores 5 and value 5 ('All of the time') scores 1, because the score measures need rather than wellbeing: all ten questions are positively worded, so a frequent occurrence is a good thing and contributes fewer points. The option LABELS were corrected to that frequency wording in revision 0.3; the values and this mapping did not change.

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/actions/Setting_FeelingScaleInversion/description`

FR-012. The inversion is a lookup map, not arithmetic in the flow, so a change to the scale's direction or its number of points is a configuration change. REVISION 0.3: this map now has ELEVEN entries keyed 0 to 10, matching rev_feelingscaleanswer's conversion from a five-option picklist to a whole number 0-10. It expresses 10 minus the raw answer, which is what the Automation Solution Design specifies for Q1.

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/actions/Setting_IncomeBandUpperBoundMap/description`

Maps each rev_incomeband option value to the top of that band, so the band can be compared with the configured ceiling. This is a FIELD MAPPING, which NFR-019 puts in the process owner's hands rather than a developer's - if the form's income bands change, this row changes and this flow does not. The sentinel -1 means 'not stated', which produces income flag 3 rather than a guess.

## `/properties/definition/actions/Score_and_flag/actions/Collect_wellbeing_answers/description`

THE TEN Likert answers paired with their question number. TEN, NOT ELEVEN - corrected in the schema revision pass. The raw export proves the form asks eleven scored questions in total: one life-satisfaction question (column 95, rev_feelingscaleanswer) plus seven SWEMWBS statements (columns 96 to 102) plus three 'last year' questions (columns 103 to 105). Seven plus three is ten Likert columns, and rev_wellbeinganswer11 has been removed from the table. The previous twelve-field array scored a column that held no question.

Carrying the number in the array is what lets the score breakdown name each answer - Logic Apps gives no loop index for an Apply to each. This array is also the completeness check below, so there is one definition of 'the scored answers' rather than two that could drift apart: adding or removing a scored question means editing this array and nothing else in this flow.

## `/properties/definition/actions/Score_and_flag/actions/Find_missing_wellbeing_answers/description`

"MISSING" NOW MEANS "MISSING OR UNUSABLE" - WIDENED IN REVISION 0.8 (test report D-014, TC-317). The filter used to be emptiness alone, so an answer that was PRESENT but not a key of LikertPointMap sailed through this gate and reached the scoring loop, where the map lookup returned null and the numeric cast threw - failing the run with the application already created and unscored. The fail-closed design that FR-022 exists to provide did not actually cover the case it was written for.

The immediate instance of that was "Not sure", and revision 0.8 fixes THAT properly by making it a real answer worth 0.5 points rather than by rejecting it - it is a valid choice a real applicant makes, not malformed input. This widened filter is the SECOND half of the fix and is the part that matters next time: the flow no longer assumes the set of storable answers equals the set of scoreable answers. Any future scale change, any option added in the maker portal without a matching map key, and any value the website sends that the map does not know now routes to a human with the question number named, instead of throwing.

The check is deliberately "is it a key of the map" rather than a hardcoded range 1 to 6, so it stays correct when the board changes the map (FR-017).

## `/properties/definition/actions/Score_and_flag/actions/Withhold_the_outcome_when_a_scored_answer_is_missing/description`

FR-022 and NFR-018. Incomplete data must not produce a spurious automated rejection, so the application goes to Under Review with NO score written at all - rev_circumstancescore is left null on purpose, because a partial score displayed next to a status looks like a judgement and is not one. The breakdown says exactly which answers were absent so the process owner can chase the right thing.

WIDENED IN REVISION 0.8 FROM "ABSENT" TO "ABSENT OR UNUSABLE", ON ALL ELEVEN SCORED ANSWERS. The gate had two conditions and both tested only for emptiness, so an answer that was PRESENT but had no configured point value passed straight through to a numeric cast that threw - the exact mechanism by which test report D-014 lost an application. The third condition added here does for the life-satisfaction answer what the widened Find_missing_wellbeing_answers filter does for the other ten: it withholds when the answer is not a key of FeelingScaleInversion. D-014's verified fact 6 is why this one is not theoretical - the live form's life-satisfaction field is type='number' step='any', so 7.5 is a value it can really send, and 7.5 is not a key of an eleven-entry map keyed 0 to 10.

Both checks are "is it a key of the map" rather than a hardcoded range, so they stay correct when the board changes the configuration (FR-017) instead of quietly contradicting it.

## `/properties/definition/actions/Score_and_flag/actions/Withhold_the_outcome_when_a_scored_answer_is_missing/actions/Tell_the_process_owner_an_answer_is_missing/description`

NFR-018 requires 100% of these to reach a human, and a queue nobody opens does not achieve that - so this is pushed, not just filed in the Under Review - Incomplete Scoring view. Carries the reference and the question numbers only: no name, no condition, no narrative.

SINCE 2026-08-21 THIS ACTION IS THE FALLBACK, NOT THE MESSAGE. `Tell_the_process_owner_an_answer_is_missing_card` posts the Adaptive Card ahead of it and this HTML message runs only on `Failed` / `TimedOut` / `Skipped`. The two carry the same facts. See the card section at the end of this file.

## `/properties/definition/actions/Score_and_flag/actions/Parse_likert_point_map/description`

MOVED AHEAD OF THE FR-022 COMPLETENESS GATE IN REVISION 0.8. It used to run after the gate, which meant the gate could only ask whether an answer was PRESENT, not whether it was USABLE. The gate now also checks that each answer is a key of this map, so the map has to be parsed first. Nothing downstream changed order: Parse_feeling_scale_inversion still runs after the gate, so the whole scoring chain remains strictly after it and a withheld application is still terminated before any score is computed.

## `/properties/definition/actions/Score_and_flag/actions/Parse_feeling_scale_inversion/description`

ALSO MOVED AHEAD OF THE FR-022 GATE IN REVISION 0.8, for the same reason as Parse_likert_point_map. The life-satisfaction answer has exactly the same unmappable-value exposure as the ten wellbeing answers - Invert_the_feeling_scale_answer casts a map lookup, and test report D-014 verified fact 6 records that the live form's field 133 is type='number' min='0' max='10' step='any', so 7.5 is something the form can genuinely produce. Widening the gate for the ten answers and not for this one would have left the identical hole open for a different reason.

## `/properties/definition/actions/Initialise_likert_points/description`

FLOAT, NOT INTEGER, SINCE REVISION 0.8. 'Not sure' is worth 0.5 points (LikertPointMap key 6), so the running subtotal is not necessarily a whole number: an ODD number of 'Not sure' answers leaves a half point. An integer variable here would either reject the increment or silently truncate every half point, which would understate the need of exactly the applicants least able to answer the questions confidently. The total is rounded ONCE, at the end, in Round_the_circumstance_score - never per answer, which would lose up to five points across ten answers.

BOTH VARIABLES ARE DECLARED AT THE TOP LEVEL, AND MUST BE. Power Automate allows `Initialize variable` only at the top level of a flow - never inside a Scope, a condition, an Apply to each or a Switch. Nesting one packs cleanly, imports cleanly and reports the flow as present, and then the designer refuses to turn the flow on: the save fails with the initialize action flagged. That is a class this project has already paid for twice - `Initialise_likert_points` and `Initialise_breakdown_lines` sat inside `Score_and_flag` from the first Phase 1 commit through the 2026-08-21 deploy, and the reviewer had to lift them by hand in the DEV designer on each of the two activations before the flow would turn on. The hand fix does not survive the next import, because the import overwrites the definition from this source. Fixed at source on 2026-08-21.

WHAT THE MOVE COST, AND WHY IT COSTS NOTHING. Both initial values are constants (`0` and `""`), so neither declaration depends on anything the scope reads - moving them ahead of `Score_and_flag` cannot change a value. The one real dependency was ordering: the pair used to sit behind the FR-022 gate, so the loop that mutates them could not start until `Withhold_the_outcome_when_a_scored_answer_is_missing` had passed. `Score_each_wellbeing_answer` now carries that `runAfter` directly, so the gate still stands between a missing answer and any scoring work. Declaring a variable that a terminated run never reads is free.

## `/properties/definition/actions/Initialise_breakdown_lines/description`

Holds the human-readable score breakdown that `Record_this_answer_in_the_breakdown` appends one line to per answer, and that `Compose_score_breakdown` writes to `rev_scorebreakdown` (FR-035). Empty string, not null: `AppendToStringVariable` on an uninitialised or null string variable fails at run time. Declared at the top level for the reason above.

## `/properties/definition/actions/Score_and_flag/actions/Score_each_wellbeing_answer/description`

FR-013 and FR-011. CONCURRENCY IS PINNED TO 1 BECAUSE THIS LOOP MUTATES SHARED VARIABLES. Power Automate parallelises Apply to each by default, and with parallel repetitions two increments can read the same value and one is lost - producing a score that is quietly too low. At ten iterations there is nothing to gain from parallelism and a wrong score is a wrong decision about a person.

## `/properties/definition/actions/Score_and_flag/actions/Score_each_wellbeing_answer/actions/Add_the_configured_points_for_this_answer/description`

float(), NOT int(), SINCE REVISION 0.8. This single cast was the mechanism of test report D-014: int() on the map value threw whenever the value was not a whole number, and threw on an empty string whenever the lookup missed. LikertPointMap key 6 ('Not sure') is 0.5, so int() would now fail on a perfectly valid answer that a real applicant gave - row 25 of docs/Import/Book(Sheet1).csv is such an application. The missed-lookup case is handled upstream instead: Find_missing_wellbeing_answers now withholds the outcome for any answer that is not a key of the map, so by the time this expression runs the lookup is guaranteed to hit.

## `/properties/definition/actions/Score_and_flag/actions/Compose_question_text/description`

EF-07/EF-24 (2026-09-17). Emily's own feedback and the delivered trustee pack both give the target format for the breakdown as prose - "I've been feeling optimistic about the future · None of the time" - not "Wellbeing answer 3: response 2 = 4 points". `Record_this_answer_in_the_breakdown` needs the question's own wording to build that, and this Compose is a static lookup from question number (1-10) to text, so the loop can read `outputs('Compose_question_text')?[string(item()?['question'])]` without a Setting row.

WHY A LITERAL MAP AND NOT A rev_setting ROW. Every other configurable value in this flow (thresholds, point maps) is a `rev_setting` row because FR-017 puts THOSE in the board's hands - they are business rules that change without a code change. Question wording is not a business rule; it is the schema's own text, and it already has one authoritative source: each `rev_wellbeinganswerN` column's `displayname` in `Entities/rev_application/Entity.xml`. The ten strings here were copied verbatim from those ten displaynames on 2026-09-17. If a question's wording ever changes on the form, the correct fix is to update Entity.xml and this map together in one change - not to make wording a runtime configuration surface for a value that only ever changes with a code deployment anyway (the form itself has to change too).

WHY QUESTION NUMBER RATHER THAN OPTION VALUE. This map is keyed the same way `Collect_wellbeing_answers` already keys each answer - by question number 1 to 10 - so the loop's existing `item()?['question']` is the lookup key with no extra transformation.

## `/properties/definition/actions/Score_and_flag/actions/Compose_frequency_response_labels/description`

EF-07/EF-24 (2026-09-17). `rev_likertresponse`'s own six option labels (None of the time, Rarely, Some of the time, Often, All of the time, Not sure), copied verbatim from `OptionSets/rev_likertresponse.xml`, keyed by option value as a string ('1' to '6'). Backs questions 1-7 only - the seven SWEMWBS statements, which the live form and the delivered pack both present on the frequency scale. Never used for questions 8-10: see `Compose_agreement_response_labels` and gap M-02 in the review-feedback plan for why the two scales must not be conflated.

WHY A LITERAL COPY RATHER THAN READING THE OPTION SET AT RUN TIME. Dataverse does not expose picklist option labels to a flow through the Web API response for a plain field read - the trigger delivers the numeric option value only. Re-deriving the label would need a metadata call this flow does not otherwise make, for six strings that only change if the option set's labels are edited in the maker portal, which is already a deployment event this solution's build gates would need to catch elsewhere. Copying the labels here is the same trade-off `Compose_question_text` makes, for the same reason.

## `/properties/definition/actions/Score_and_flag/actions/Compose_agreement_response_labels/description`

EF-07/EF-24 (2026-09-17). `rev_agreementresponse`'s own six option labels (Strongly Disagree, Disagree, Neutral, Agree, Strongly Agree, Not sure), copied verbatim from `OptionSets/rev_agreementresponse.xml`, keyed by option value as a string ('1' to '6'). Backs questions 8-10 only - the three "last year" statements, answered on the agreement scale per the delivered pack and the option set's own description (added revision 0.8, because these three questions were originally and wrongly labelled with `rev_likertresponse`'s frequency wording - see that option set's Descriptions for the full history). See `Compose_frequency_response_labels` for why the labels are copied rather than read from Dataverse metadata at run time.

## `/properties/definition/actions/Score_and_flag/actions/Score_each_wellbeing_answer/actions/Record_this_answer_in_the_breakdown/description`

REWRITTEN FOR EF-07/EF-24 (2026-09-17). FR-035: the breakdown is what evidences the score to a trustee. Until this change each line named the question NUMBER, the response option VALUE and the points it contributed - "Wellbeing answer 3: response 2 = 4 points" - which is exactly the wording Emily's feedback and the reviewer's live check both called out as unreadable to someone who has not memorised the schema. The delivered trustee pack confirms the target format verbatim: "I've been feeling optimistic about the future · None of the time" - question text, a middle dot, the answer's own label. No points and no raw values in the line at all.

WHY POINTS WERE DROPPED FROM THIS LINE, NOT JUST RELABELLED. The pack's own example has no points in it. The circumstance score total and the "out of 60" framing remain in `Compose_score_breakdown`'s preamble, so the trustee still sees what the application scored - just not a running per-line arithmetic ledger the pack itself does not show. Nothing about the actual point calculation changes: `likertPoints` still accumulates in `Add_the_configured_points_for_this_answer` exactly as before, from the same `LikertPointMap` lookup, unaffected by this action's rewrite.

WHY TWO LABEL MAPS AND A CONDITIONAL, NOT ONE. Gap M-02, now evidenced (revision 4 of the review-feedback plan): questions 1-7 (the seven SWEMWBS statements) are answered on the frequency scale (`rev_likertresponse` - None of the time … All of the time), and questions 8-10 (the three "last year" statements) are answered on the agreement scale (`rev_agreementresponse` - Strongly Disagree … Strongly Agree). The two scales share the same six ordinal values (1-6, with 6 always "Not sure") but not the same words, and picking the wrong map for a question would print a label the applicant never saw. `lessOrEquals(int(string(item()?['question'])), 7)` is the same boundary `Collect_wellbeing_answers`, the option set XML files and the Entity.xml field descriptions all already draw between the two groups - it is not a new distinction, only the first place this flow's OUTPUT TEXT has to act on it.

THE OLD "VALUE 6 = 0.5 POINTS" NAMING EXCEPTION NO LONGER APPLIES AND IS NOT CARRIED FORWARD. It existed to stop a fractional point value from looking like a typo next to whole numbers - but this line no longer prints points at all, and separately, EF-23 (2026-09-17) removed the fractional value from `LikertPointMap` itself ('Not sure' is now 0, not 0.5 - see `Round_the_circumstance_score`'s own description). Both reasons for the exception are gone; "Not sure" now prints as a label like any other value, from whichever of the two maps the question's scale selects, with no special case.

## `/properties/definition/actions/Score_and_flag/actions/Invert_the_feeling_scale_answer/description`

FR-012. A lower reported life satisfaction produces a higher score, because the score reflects need rather than wellbeing. THE SCALE IS 0 TO 10 AND THE CONTRIBUTION IS 10 MINUS THE RAW ANSWER (revision 0.3): a raw 0 - the worst self-reported wellbeing - contributes 10 points, and a raw 10 contributes 0. That is what the Automation Solution Design v0.5 specifies for Automation #2 Q1: "Q1 ('How are you feeling?') is inverted (0/10 feeling = 10 points)". Until revision 0.3 this expression inverted a FIVE-point picklist through a five-entry map, which produced at most 5 points and was the whole reason the attainable maximum looked like 55. The expression itself is unchanged, because the inversion has always been a table lookup rather than arithmetic - what changed is the map it reads (eleven entries, keyed 0 to 10) and the type of the column it reads. A raw answer of 0 is a real answer and maps to key '0'; a NULL answer never reaches here, because the FR-022 completeness gate above withholds the outcome first.

## `/properties/definition/actions/Score_and_flag/actions/Calculate_circumstance_score/description`

FR-011. TEN wellbeing answers at up to 5 points each (50) plus the inverted life-satisfaction answer at up to 10, gives a 0 to 60 range - and that range is a consequence of the configuration, not a constant in this flow, which is why MaxCircumstanceScore is read from a setting row rather than written here.

THE MAXIMUM IS 60 AND IS NO LONGER OPEN (revision 0.3). Revision 0.2 had reduced it to 55 because the life-satisfaction question was built as a five-option picklist; the reviewer has confirmed the question is the 0-to-10 scale its source documents describe, so 10 + (10 x 5) = 60 - the figure the raw export header has always used ('Overall Circumstance Score (out of 60)') and the figure the Automation Solution Design v0.5 states ('Total = sum of all question scores (max 60)'). Three things moved together to make that true rather than asserted: rev_feelingscaleanswer became a whole number 0-10, FeelingScaleInversion became an eleven-entry map keyed 0-10, and MaxCircumstanceScore returned to 60 in both settings files. This UNBLOCKS SDD OQ-001 and OQ-002 - the threshold score and the borderline band are ABSOLUTE scores, and the scale they sit on is now fixed at 0 to 60.

## `/properties/definition/actions/Score_and_flag/actions/Round_the_circumstance_score/description`

NEW IN REVISION 0.8; THE ROUNDING MECHANISM CORRECTED IN REVISION 0.9 (test report D-015) - SEE THE LAST THREE PARAGRAPHS, AND NOTE THAT WHAT THIS DESCRIPTION USED TO SAY ABOUT 'F0' WAS FALSE. THE EXACT TOTAL CAN NOW BE FRACTIONAL AND rev_circumstancescore IS AN int COLUMN.

WHY A FRACTION IS POSSIBLE AT ALL: 'Not sure' is worth 0.5 points (LikertPointMap key 6), so an ODD number of 'Not sure' answers among the ten leaves a half point. The one worked example in the ground-truth data - row 25 of docs/Import/Book(Sheet1).csv - answered 'Not sure' to all TEN questions and therefore totalled a whole number (10 x 0.5 = 5), which is why the fractional case is not visible in the sample and had to be reasoned about rather than read off.

THE RULE: ROUND HALF UP (away from zero), so 37.5 becomes 38 and 20.5 becomes 21. Half up is the only case that can ever arise - the fractional part is either .0 or exactly .5 and nothing else - so the rule is fully determined by one decision and is simple to explain to a trustee. BOTH examples are given deliberately: 37.5 alone is the example that hid D-015 for a whole revision, because it is one of the halves that the broken expression happened to get right.

WHY UP RATHER THAN DOWN, STATED SO IT CAN BE OVERRULED: a HIGHER score means GREATER need in this scale, and Derive_status returns Auto-reject at or BELOW the threshold score. Rounding up therefore resolves the half point in the applicant's favour. Rounding down would let a rounding artefact - on the answers of an applicant who was least certain about their own wellbeing - be the thing that knocked them out. The cost is a systematic upward bias of at most 0.5 points on a 60-point scale, applied only to applicants with an odd number of 'Not sure' answers.

THIS IS A JUDGEMENT CALL, NOT A DERIVATION, AND THE REVIEWER MUST CONFIRM IT. The CSV does not settle it: every published total in it is a whole number, and the only 'Not sure' row is whole by coincidence, so there is no evidence of how the process owner rounds by hand. Two alternatives were considered and rejected for now: (a) change rev_circumstancescore to a decimal column and store 37.5 exactly - the most faithful option, rejected as a larger schema change touching the column type, the views, the daily summary and the trustee pack, and worth doing deliberately rather than as a side effect of this fix; (b) truncate - rejected as (a) silently biased against the same applicants and (b) indistinguishable from the bug it replaces. See the Dev Summary revision 0.8.

NOTHING IS LOST EITHER WAY: Compose_score_breakdown records the EXACT unrounded total alongside the rounded one, so a reviewer can always see what was rounded and by how much.

WHY formatNumber AND NOT round(): the Logic Apps expression language this flow is written in has no round(), ceiling() or floor() function, so there is no rounding function to call and the rounding has to be built out of formatting. formatNumber's 'F0' specifier is .NET standard numeric formatting - the equivalent of value.ToString('F0') - and int() over its string output is an unambiguous conversion, whereas int() applied directly to 37.5 would rely on undocumented truncation behaviour of a cast.

CORRECTION, REVISION 0.9 - WHAT THIS DESCRIPTION USED TO CLAIM ABOUT 'F0' WAS FALSE, AND WAS NEVER EXECUTED (test report D-015, P2). Until revision 0.9 the expression was int(formatNumber(outputs('Calculate_circumstance_score'), 'F0')) and this paragraph asserted that 'F0' rounds half AWAY FROM ZERO. It does not. Executed on .NET 10.0.10 - the same major family pac 2.4.1 reports - (0.5).ToString('F0') is 0, (2.5) is 2, (20.5) is 20, (30.5) is 30, while (1.5) is 2, (21.5) is 22 and (37.5) is 38. .NET formats a double at an exact midpoint by rounding HALF TO EVEN, so it agrees with half up only when the whole part is ODD. Math.Round(20.5, 0) with no MidpointRounding argument returns 20 for the same reason. THE HARM WAS SPECIFIC AND SILENT: with the TST/ACC values in force (threshold score at or below 20, borderline band 21 to 30) an exact total of 20.5 was stored as 20, and Derive_status - correctly reading the stored number since revision 0.8 - returned 4 Auto-reject, where the approved rule stores 21 and returns 3 Borderline. That is A HUMAN REVIEW SILENTLY SKIPPED: the identical harm the revision 0.8 Derive_status fix was written to prevent, reintroduced one action upstream, while Compose_score_breakdown told the trustee in plain English that halves are rounded UP. Nothing threw and nobody was alerted, because 20.5 is a perfectly scoreable total.

HOW THE + 0.25 FIXES IT, AND WHY IT IS EXACT RATHER THAN NEARLY RIGHT: the offset moves the value OFF the midpoint before the formatter ever sees it, so the formatter's midpoint mode stops mattering instead of having to be trusted. The only fractional parts that can occur are .0 and exactly .5, so there are exactly two cases: X.0 + 0.25 = X.25, which formats to X (unchanged); and X.5 + 0.25 = X.75, which formats to X+1 (half up, unambiguously, on any rounding mode). 0.25 is strictly inside the open interval (0, 0.5), so it can never carry a whole total up to the next integer nor leave a half total short of the midpoint. 0.25 and 0.5 are both exact binary fractions, so no floating-point representation error is introduced - 20.5 + 0.25 is exactly 20.75, not 20.749999. VERIFIED BY EXECUTION over EVERY total this flow can produce (0.0 to 60.0 in steps of 0.5 - 121 values) and under BOTH .NET numeric types, because decimal.ToString('F0') rounds half AWAY FROM ZERO where double rounds half TO EVEN: zero mismatches against the approved rule either way. The fix is therefore correct whichever numeric type the Power Automate runtime uses and whichever midpoint mode a future runtime version adopts. That is the whole point of it - it REMOVES the dependency rather than betting on it, which is what the previous version did.

WHAT THE OFFSET DEPENDS ON, SO IT CANNOT DRIFT: + 0.25 is sound ONLY because 0.5 is the only non-integer value in LikertPointMap. That is not left as a comment - ScoringInvariants.Tests.ps1 asserts it directly ('holds 0.5 as the ONLY non-integer value'), and the D-015 suite in the same file re-executes .NET's own formatting through the offset READ OUT OF THIS EXPRESSION for every reachable total, so deleting the offset, or changing it to a value outside (0, 0.5), fails the suite immediately rather than waiting for a person to re-derive .NET's rounding mode by hand. IF A FUTURE CHANGE INTRODUCES A POINT VALUE THAT IS NEITHER A WHOLE NUMBER NOR A HALF (0.25, say), BOTH THE OFFSET AND THIS DESCRIPTION STOP BEING TRUE, and those two tests are what will say so.

## `/properties/definition/actions/Score_and_flag/actions/Derive_income_flag/description`

FR-015. Deliberately SEPARATE from the circumstance score: 1 within the ceiling, 2 above it, 3 not stated, 4 qualifies on means-tested benefits. An applicant above the income ceiling is identified independently and is not silently penalised in their need score - which is also what keeps the two decisions auditable apart.

OPTION 4 ADDED EF-28b/M-04, 2026-09-17 - THE FIX FOR THE MAJORITY, NOT AN EXCEPTION. Round 4 shows the live form suppresses rev_incomeband, rev_employmentstatus and rev_savingsover6000 ENTIRELY once the applicant answers Yes to means-tested benefits: 57 of 57 benefits-Yes applications blank on all three, 6 of 6 benefits-No applications populated on all three. Before this option existed, every one of those 57 read option 3, "Not stated - cannot assess" - which is the opposite of true for them. Receiving a means-tested benefit is itself the evidence of eligibility; the system was recording that it could not tell.

WHY rev_receivesbenefits IS CHECKED FIRST, NOT rev_incomeband. `if(equals(triggerOutputs()?['body/rev_receivesbenefits'], true), 4, ...)` runs before `Resolve_income_band_upper_bound` is even consulted. Order matters: testing the income band first would send every blank band to option 3 regardless of the benefit answer, reproducing exactly today's wrong behaviour. Testing benefits first and short-circuiting means a benefits-Yes application never falls through to "not stated" at all.

WHY A DISTINCT VALUE RATHER THAN FOLDING IT INTO OPTION 1. Option 1, "Within income ceiling", asserts a comparison against IncomeCeiling that was never made for these applications - a trustee or auditor reading it would reasonably assume income WAS measured. Keeping the routes apart also answers a question the funders ask directly (how many qualified on benefits versus on income), and it matters for EF-46: when the income ceiling moves, applications that qualified on benefits are unaffected by the change, which is only visible if the two routes were never merged.

DELIBERATELY THE ONE AND ONLY PLACE rev_receivesbenefits IS READ IN THIS FLOW. SDD section 7.1 classifies benefit status at the highest restriction tier, alongside health data, specifically so it does not drive an automated decision unreviewed - and FR-016's own HARD build gate enforces that for the CIRCUMSTANCE SCORE (`ScoringInvariants.Tests.ps1`'s "no special-category column reaches the automated score" describe block). This is a narrower, dated, reviewer-settled exception for the INCOME FLAG only: `rev_receivesbenefits` must never appear in `Score_each_wellbeing_answer`, `Invert_the_feeling_scale_answer`, `Calculate_circumstance_score`, `Round_the_circumstance_score` or `Derive_status` - a dedicated test asserts exactly that boundary, separately from the one asserting where it IS authorised to appear.

THE DECIDING RULE IS RECORDED, NOT JUST APPLIED. `Compose_scoring_audit` writes out which of the four options fired and why, so an application scored under today's rules stays explicable even after the income ceiling or the benefit-suppression behaviour on the live form changes.

## `/properties/definition/actions/Score_and_flag/actions/Derive_status/description`

FR-014. 4 Auto-reject at or below the threshold score, 3 Borderline inside the band, 2 Auto-pass above it. Threshold score is evaluated so that a misconfigured band - lower set below the threshold score - can never let a below-threshold application through as Borderline. Every boundary is a configured value.

EVALUATED AGAINST THE ROUNDED SCORE SINCE REVISION 0.8, AND THAT CHOICE IS LOAD-BEARING. The status must be derived from the SAME number that is written to rev_circumstancescore, or the record contradicts itself: a trustee would read a score and an outcome that cannot be reconciled, and the score breakdown could not explain the decision. It is not a cosmetic difference. With a borderline lower bound of 37, an exact total of 36.5 is NOT >= 37 and would fall through to Auto-pass, while the 37 actually stored IS in the band and is Borderline - a human review that would have been skipped. Rounding once, before this expression, removes that class of disagreement entirely.

EF-34 (added 2026-09-22): A SECOND, INDEPENDENT AUTO-REJECT PATH, EVALUATED FIRST. `rev_receivedfundingbefore` is Yes AND `rev_morethan12monthsago` is No -> auto-reject (status 4), regardless of the circumstance score. This is checked BEFORE the score threshold, deliberately: it is a categorical eligibility fact about the applicant (funding received too recently), not a measurement of current need, so it takes precedence the same way `Withhold_the_outcome_when_a_scored_answer_is_missing` already gates the whole scope before any score-based rule runs. The order is the control that makes the auto-reject reason DETERMINISTIC when both this rule and the score threshold would reject the same application - see `Derive_autoreject_reason` below, which records only the rule that actually fired.

WHY A MISSING `rev_morethan12monthsago` DOES NOT TRIGGER THE REJECTION. The compound condition uses `equals(..., false)`, not `not(equals(..., true))`: a null (the question genuinely never answered, or asked-but-skipped) evaluates neither branch as true, so the application falls through to the ordinary score-based rules rather than being auto-rejected on incomplete data. This mirrors FR-022's philosophy (absent data must never manufacture a decision) without reusing its withhold-the-whole-outcome mechanism, because a missing 12-month answer does not also make the CIRCUMSTANCE SCORE unusable the way a missing wellbeing answer does.

RESOLVES THE OPEN DPO QUESTION (BR-S10). The walkthrough previously blocked this rule pending confirmation that automatic rejection can stand without per-case human review under the Data (Use and Access) Act 2025. The reviewer settled this 2026-09-22: "The conflict is not applicable because all items get checked by a human, regardless of their automatic scoring." Every Auto-reject, on either path, is still visible to and checked by the process owner on the Casework tab - nothing about this rule removes that.

## `/properties/definition/actions/Score_and_flag/actions/Derive_autoreject_reason/description`

EF-45 (2026-09-22). The single place that decides WHY an application was Auto-rejected, written to `rev_autorejectreason` alongside `rev_status` in the same `Write_score_and_status` call - so the two can never disagree about whether a reason exists. Returns `null` for every status other than 4, using the SAME bare `@if(...)` (no `@{}` string-template wrapper) that the intake flow already ships for a Dataverse write field that must be null rather than the string `"null"` - see e.g. `rev_email`/`rev_dateofbirth` in `REVIntakeWordPressToDataverse`'s deep-insert body. That is ground truth already proven live on this platform, not a fresh guess for this action.

WHY THE ORDER MATTERS HERE TOO, NOT JUST IN `Derive_status`. If both EF-34's 12-month rule and the score threshold would reject the same application, `Derive_status` already picked ONE path (the 12-month rule, checked first) - this action re-runs the SAME condition rather than trying to infer which path fired from the status value alone, so the reason text always matches the rule that actually produced the 4. The alternative (branching on some stored "which rule fired" flag) would be a second encoding of the same decision and could drift from `Derive_status` under a future edit to either action.

`Compose_scoring_audit` reuses this action's output for its own status-4 line, rather than duplicating the score-threshold text a second time - see that action's own description.

## `/properties/definition/actions/Score_and_flag/actions/Compose_score_breakdown/description`

FR-011 and FR-035. Trustee-visible evidence of how the score was reached. Contains ONLY the scored answers, the points, the totals and the thresholds applied - no narrative, no condition data, no identity. It also records the thresholds in force at the time of scoring, so a later threshold change cannot make a historic decision look wrong.

SPLIT IN TWO, EF-44 (2026-09-17), AND WHY ONE COLUMN WAS DOING TWO JOBS. EF-07/EF-24 ask for the trustee-facing breakdown to read as prose - question text and the applicant's own answer label, e.g. "I've been feeling optimistic about the future: response 1 = 5 points" - and to move away from Application Details on the review screen. The walkthrough separately asked for the threshold-and-status audit trail to move OUT of the Trustee Portal entirely, into an admin-only column, because `KnockoutThreshold` (now Threshold score), `BorderlineBandLower/Upper` and `IncomeCeiling` are all seeded PROVISIONAL and the moment any of them changes, an application scored under the old value becomes inexplicable from its own record unless the value it was scored against is written down somewhere the trustee never sees and nobody is tempted to "helpfully" update. Those are two different artefacts for two different audiences, and `rev_scorebreakdown` was doing both jobs. `Compose_score_breakdown` now writes ONLY the trustee-facing half; `Compose_scoring_audit` (new) writes the admin-only half to the new `rev_scoringaudit` column, described below. EF-07/EF-24's question-text rewrite (2026-09-17) is now built too - see `Record_this_answer_in_the_breakdown`'s own description for the exact format and the two-scale label lookup.

WHAT MOVED OUT, AND WHY THE "EXACT TOTAL BEFORE ROUNDING" TEXT DID NOT MOVE WITH IT (EF-23, 2026-09-17). The threshold values, the status rule that fired and the income flag derived all moved to `Compose_scoring_audit`. The old "Exact total before rounding = ... halves are rounded UP" passage was NOT carried over to either action: `LikertPointMap` has held no fractional value since 2026-08-20 ('Not sure' = 0, not 0.5), so `Calculate_circumstance_score` and `Round_the_circumstance_score` are now always identical and there is nothing left to round or to explain. Writing the passage into either half would describe a code path that can no longer execute. `Round_the_circumstance_score` itself is kept as a permanent guard against the map ever reintroducing a half-point value - see its own description - so if that ever happens, THIS is the description that will need a corresponding passage restored, in whichever of the two artefacts is judged the right home for it at the time.

## `/properties/definition/actions/Score_and_flag/actions/Compose_scoring_audit/description`

EF-44 (2026-09-17). Admin-only companion to `Compose_score_breakdown` above - see that description for why the column was split and what stayed behind. Written to the new `rev_scoringaudit` column (`ntext`, `IsSecured=0`, deliberately absent from every Trustee Portal select list - the Trustee Portal reads `rev_scorebreakdown` only).

WHAT IT RECORDS, AND WHY EACH PART IS THERE. (1) Which of `Derive_status`'s outcomes fired - for status 4, this is now `Derive_autoreject_reason`'s own text (EF-34/EF-45, 2026-09-22), covering both the 12-month rule and the score threshold, rather than a second hand-written description of the threshold case that could drift from the one written to `rev_autorejectreason`. (2) Which of `Derive_income_flag`'s four outcomes fired, including the EF-28b/M-04 benefits route - see that action's own description for why a fourth outcome exists and why it is evaluated first. (3) All four PROVISIONAL settings (`KnockoutThreshold`, `BorderlineBandLower`, `BorderlineBandUpper`, `IncomeCeiling`) as they stood at the moment of scoring, not as they read now - this is the part that makes the column an AUDIT trail rather than a duplicate of the breakdown, and the reason it has to exist before OQ-001/002/003 are settled rather than after: once the board confirms real values, every application scored under today's placeholders needs its own record of what those placeholders were.

RUNS AFTER `Compose_score_breakdown` AND `Derive_autoreject_reason`. Ordering against `Compose_score_breakdown` has no computational effect - the two Compose actions read disjoint outputs - but keeping the trustee-facing artefact first in the definition mirrors which one a maker opening this flow in the designer should read first to understand what a trustee sees. The dependency on `Derive_autoreject_reason` is load-bearing: this action's own status-4 text is `outputs('Derive_autoreject_reason')`, so it cannot run before that output exists.

## `/properties/definition/actions/Score_and_flag/actions/Write_score_and_status/description`

One write, at the end, once everything is computed - so a failure part-way through leaves the application unscored rather than half-scored. FR-020 is satisfied by writing status 4: the Active Applications view filters rev_status ne 4, so the application leaves the working list without any data being moved or hidden irreversibly.

EF-45 (2026-09-22): `rev_autorejectreason` is written in this SAME call, from `Derive_autoreject_reason`'s output - never a separate write. Writing it anywhere else would reopen exactly the failure this action's own "one write, at the end" design already prevents for every other column: a status of 4 with no reason recorded, if the run failed between two writes.

## `/properties/definition/actions/Score_and_flag/actions/Route_borderline_applications_to_the_process_owner/description`

FR-019 and NFR-018: 100% of Borderline outcomes must receive human judgement before they progress. The Borderline - Awaiting Review view is the queue; this message is what makes sure someone knows the queue has something in it. Carries the reference, the score and the income flag - not the applicant's name, because unlike FR-009 there is no requirement here that needs it.

## `/properties/definition/actions/Alert_on_failure/description`

FR-010. Passes the application REFERENCE, never the row. A scoring failure leaves the application at status Submitted with no score, which is the safe resting state: it appears in the active list as unactioned rather than silently carrying a wrong outcome (NFR-018 fail-closed).

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/actions/Read_scoring_configuration/description`

ONE List rows call reads all eight rev_setting rows the calculation needs. It replaces eight
chained Get-a-row-by-id actions, each of which put an alternate-key expression
(`rev_name='LikertPointMap'`) in the Row ID field. The Dataverse Web API accepts that form -
`GET rev_settings(rev_name='LikertPointMap')` was verified working against DEV on 2026-08-20,
and the `rev_setting_name` key index reports Active - but the connector's Get-a-row-by-id
operation does not: Row ID takes a GUID. The two invocation paths disagree, and the flow failed
on its very first action, before any write, on all eleven runs of its first live test. The
symptom was eleven identical error-log rows reading only "An action failed. No dependent
actions succeeded."

Beyond correctness, this is one network round trip instead of eight sequential ones. The eight
reads were chained (each `runAfter` the previous), each carrying a four-attempt exponential
retry, so a slow environment paid that latency eight times over on every single application.

The eight values are extracted by eight Filter array actions named `Setting_<Key>`, running in
parallel off this one read. A Filter array ACTION is used rather than an inline expression
because the workflow definition language has no `filter()` function - `first()`, `union()` and
`skip()` exist, filtering does not. The same construct is already used in this flow by
`Find_missing_wellbeing_answers`. Each consumer then reads
`first(body('Setting_<Key>'))?['rev_value']`.

## `/properties/definition/actions/Score_and_flag/actions/Read_configuration/actions/Fail_if_a_setting_row_is_missing/description`

THIS GUARD EXISTS BECAUSE THE CHANGE ABOVE REMOVED A FAILURE MODE THAT WAS PROTECTING US.
Get-a-row-by-id returns 404 when the row is absent, so a missing rev_setting row failed the run
loudly. List rows returns a SHORT ARRAY instead: `first()` over an empty result is null,
`int(null)` is 0, and the flow would carry on and score every applicant against a threshold of
zero. A plausible wrong score is worse than no score - it is indistinguishable from a real one
on the record, and FR-022 already establishes that this flow withholds rather than guesses.

So the row count is asserted before any value is read: fewer than eight and the run terminates
Failed, which is what `REV | Ops | Failure Alert` listens for, and the error names the count it
found and points at `provisioning/dataverse/seed-settings.ps1`. Eight is the number of rows the
`$filter` above names; if a setting is added to that filter, this number moves with it.

## `/properties/definition/triggers/When_an_application_is_created` - subscriptionRequest/runas

`runas` is 3 (flow owner), not 4. This is not cosmetic. With 4 the trigger packs, imports and
reports `statecode=1 / statuscode=2` (Activated) while creating NO webhook subscription: Dataverse
holds zero `callbackregistration` rows for `rev_application`, no run is ever attempted, and the
run history is empty because there is nothing to record. Verified live on 2026-08-20 across three
saves at 4 - including one at `scope` 1 with rows owned by the flow owner, which rules out
ownership - and the registration appeared the moment the value became 3.

The check that distinguishes a registered trigger from an activated-but-dead one:

    GET callbackregistrations?$filter=entityname eq 'rev_application'

Read it as an identity holding System Administrator, or a zero may mean you cannot see the rows
rather than that none exist. `provisioning/dataverse/seed-test-data.ps1` runs this check in its
pre-flight and refuses to load test data when it returns nothing.

## `/properties/definition/actions/Compose_run_link/description`

An explicit action rather than an expression buried in the child-flow call, so the link is
visible in the designer and can be inspected in a run's outputs when it comes out wrong:

    concat('https://make.powerautomate.com/environments/', workflow()?['tags']?['environmentName'],
           '/flows/', workflow()?['name'], '/runs/', workflow()?['run']?['name'])

Both parts are runtime values, so no environment variable and no hardcoded host is involved.
It has to be built in the CALLER: `workflow()` inside `REV | Ops | Failure Alert` returns the
child flow's own identity, not the caller's, which is why the child cannot construct its own
inbound link and takes it as the `text_5` input instead.

## `/properties/definition/actions/Score_and_flag/actions/Withhold_the_outcome_when_a_scored_answer_is_missing/actions/List_the_missing_question_numbers/description`

Added 2026-08-20, after TD-07 was the last of twelve test cases still failing. The breakdown text
built its list of missing question numbers with
`join(json(string(select(body('Find_missing_wellbeing_answers'), item()?['question']))), ', ')`.
There is no `select()` EXPRESSION in the workflow definition language - Select is a data-operation
ACTION, the same family as the Filter array already used here - and `item()` is only meaningful
inside such an action. It was the only `select(` in the entire solution.

WHY IT SURVIVED SO LONG, AND WHY TD-08 PASSED WHILE TD-07 FAILED. The call sits in the taken
branch of `if(greater(length(...), 0), join(...), 'none')`. TD-08 omits the life-satisfaction
answer and no wellbeing answer, so the length is 0 and the `'none'` branch is taken - and it
succeeded. TD-07 omits wellbeing answer 7, so the length is 1 and the join branch is taken - and
it failed. That pair is also the evidence that `if()` here evaluates only the branch it takes:
an eager `if()` would have failed both.

The list is now projected by this Select action and joined from its output. `string()` is applied
inside the projection so `join` receives strings rather than integers.

## The two Adaptive Cards - added 2026-08-21

Covers `/properties/definition/actions/Score_and_flag/actions/Route_borderline_applications_to_the_process_owner/actions/Notify_borderline_card/description`
and `/properties/definition/actions/Score_and_flag/actions/Withhold_the_outcome_when_a_scored_answer_is_missing/actions/Tell_the_process_owner_an_answer_is_missing_card/description`,
and the `Notify_borderline` fallback beside the first.

WHAT CHANGED AND WHY. Both notifications were HTML `PostMessageToConversation` messages, and
both had the same two problems: the facts arrived as one paragraph of `<br/>`-separated lines,
and neither told the reader where to go except by naming a view to find by hand. The reviewer
read them and could not use them. Each is now an Adaptive Card whose facts sit in a `FactSet`
with `separator` and `spacing` between the blocks, and whose `Action.OpenUrl` buttons open the
application itself and the queue it belongs to.

THE RECORD BUTTON IS THE POINT. `&pagetype=entityrecord&etn=rev_application&id=` plus
`triggerOutputs()?['body/rev_applicationid']` opens THIS application, not the list containing
it - the list button is kept second because the process owner's next question after judging one
is usually "what else is waiting". Both URLs are assembled from the same two-lifetime split the
daily summary uses: the view id comes from this solution's own `Entities/rev_application/SavedQueries/`
and is identical in every environment, and the host and `appid` come from `rev_GrantAdminAppUrl`
(C-TECH-047). Nothing in the payload is a literal host.

THE PATTERN IS COPIED, NOT INVENTED. `IMP-0125` records the verified shape - operationId
`PostCardToConversation` on `shared_teams`, `poster` / `location` / `body/recipient` exactly as
the HTML action uses them, and the card passed as a JSON STRING in `body/messageBody` - and it
says to keep the HTML message behind each card, on `runAfter` `Failed` / `TimedOut` / `Skipped`,
until a second card has been seen working. These are the second and third cards, so the
fallbacks stay: `Notify_borderline` and `Tell_the_process_owner_an_answer_is_missing` now carry
the same facts as HTML, with guarded anchors instead of buttons.

`Stop_run_incomplete_answers` therefore runs after `Succeeded` OR `Skipped` on the HTML
fallback. Skipped is the normal path - it means the card sent. If BOTH the card and the fallback
fail, the terminate is skipped, `Score_and_flag` fails and `Alert_on_failure` fires, which is the
same fail-loud behaviour the single HTML action had.

THE CARDS ARE ALSO FILES. `docs/development/cards/borderline-card.json` and
`docs/development/cards/withheld-outcome-card.json` hold them indented and readable; the strings
in this definition are those files minified. Nothing asserts the two agree - edit one and the
other is stale, silently. Logged as a finding rather than patched here.

AN UNSET `rev_GrantAdminAppUrl` IS VISIBLE IN THE CARD, NOT SILENT. The variable is
`isrequired=0` and no script in this repo writes its value (IMP-0101: DEV held four definitions
and zero values on 2026-08-20). So each card's guidance line carries
`if(empty(parameters('rev_GrantAdminAppUrl')), ' The buttons below need the Grant Administration
App URL environment variable set for this environment.', '')` - the reader is told why a button
does not work instead of being handed a dead one with no explanation. `if()` here evaluates only
the branch it takes, proven by the TD-07/TD-08 pair above, so the unused branch costs nothing.
The HTML fallbacks drop to plain view names by the same guard.

THE INCOME FLAG IS NOW ACTUALLY IN THE MESSAGE. `Route_borderline_applications_to_the_process_owner`
has always said it carries "reference, score and income flag"; the message carried the first two
and the borderline band. The card carries all four, with the flag rendered as words - Within the
ceiling / Above the ceiling / Not stated - because `1`, `2` and `3` mean nothing to the reader.

## `/properties/definition/parameters/rev_GrantAdminAppUrl`

Added to this flow 2026-08-21; the definition already shipped, added 2026-08-20 for the daily
summary. Base URL of the REV Grant Administration app up to and including `appid`, assigned per
environment, never committed (C-TECH-047, and see
`src/solutions/RevitaliseGrantAutomation/environmentvariabledefinitions/README.md` for why its
own description carries no example URL). Three actions in this solution now read it, and it is
worth treating as a real deployment precondition rather than an optional nicety: set the
environment variable's CURRENT VALUE, never its default, or the next import silently discards it
(IMP-0121).
