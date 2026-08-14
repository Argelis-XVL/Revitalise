# Setting Row Descriptions — Full Rationale (D-021)

**Why this file exists.** `rev_setting.rev_description` has `MaxLength="500"`
(`src/solutions/RevitaliseGrantAutomation/Entities/rev_setting/Entity.xml`). Four of the
eleven `dataverse.settingRows` descriptions in `dev-scoring-settings.json`, `test-settings.json`
and `prd-settings.json` were written in this project's normal, verbose documentation style —
fine as JSON commentary, fatal as a Dataverse column value. Discovered live, running
`seed-settings.ps1 -Env dev` against `REV-GrantApplications-DEV` for the first time
(2026-08-14): 4 of 11 rows failed with
`"The length of the 'rev_description' attribute of the 'rev_setting' entity exceeded the
maximum allowed length of '500'."` — 7 rows had already been written by the time the failures
were reported, so the fix additionally had to be safe to re-run (it is: the alternate-key
upsert in `seed-settings.ps1` makes every row idempotent regardless of how many succeeded on a
prior attempt).

This is the same failure class, same root cause, and same fix shape as the flow-description
length defect (C-TECH-049, `docs/development/revitalise-grant-automation-dev-deployment-
handover.md` §3.2 #7): a platform field-length limit neither `pac solution pack` nor a mocked
Pester test can see, because the mocked Web API in `DataverseScripts.Tests.ps1` accepts any
string the test hands it. Each shortened `rev_description` keeps the essential fact and its
FR/NFR/OQ/defect citation, plus a pointer back to this file; the reasoning that made each
value what it is stays here, in full, exactly as originally written.

`scripts/verify-setting-description-length.py` gates this at build time (`config/<slug>-
build.yml` → `setting-description-length`) so the omission cannot recur silently.

---

## LikertPointMap

Maps a wellbeing answer's option VALUE to circumstance points (FR-013). Position 1 ('None of the time' on rev_likertresponse, 'Strongly Disagree' on rev_agreementresponse) scores 5 and position 5 ('All of the time' / 'Strongly Agree') scores 1 — all ten wellbeing questions are worded positively, so a frequent occurrence or an agreement means better wellbeing and therefore less need. ONE MAP SERVES BOTH OPTION SETS AND IS DELIBERATELY NOT DUPLICATED. Revision 0.8 split the three 'Thinking about the last year' questions onto rev_agreementresponse, but the scoring flow looks this map up by the numeric option value — outputs('Parse_likert_point_map')?[string(item()?['response'])] — and never knows which option set the answer came from. Both scales use the same ordinals 1 to 6 with the same direction, so a second map would only be a second place for the same numbers to drift out of step. The name is kept for that reason. KEY "6" ('Not sure') = 0.5 IS NEW IN REVISION 0.8 AND IS DERIVED FROM GROUND TRUTH, NOT CHOSEN. docs/Import/Book(Sheet1).csv row 25 is a real application that answered 'Not sure' to all ten wellbeing questions and was scored 9 by hand: the life-satisfaction raw answer of 6 contributes 10-6=4 through FeelingScaleInversion, leaving exactly 5 points to be shared by 10 'Not sure' answers — 0.5 each, with no remainder. Reconstructing all 25 rows of that CSV with this map reproduces every published score exactly. THIS IS THE ONLY NON-INTEGER VALUE IN THE MAP and it is why the scoring flow accumulates points in a FLOAT variable and rounds once at the end before writing the int column rev_circumstancescore — see Round_the_circumstance_score. The board can change 0.5 here without a solution change, but a value that is neither a whole number nor a half would BREAK THE ROUNDING STEP, not merely read oddly: since revision 0.9 Round_the_circumstance_score resolves the half point by adding 0.25 to the total before formatting it, and that offset is exact ONLY while .0 and .5 are the only fractional totals that can arise (test report D-015). ScoringInvariants.Tests.ps1 asserts that condition on this very row, so such an edit fails the suite instead of quietly mis-scoring an applicant. UNCHANGED FROM REVISION 0.3: keys 1 to 5, their values, and their direction.

## AgeRangeLabelMap

Maps the age-band labels the live application form actually sends to rev_agerange option values (2=18 to 24 .. 8=75 and over, 9=Not known). The live form asks an age band directly (field 26, optional) and does NOT ask for a date of birth, so this map - not AgeBandMap - is the primary route to rev_agerange. Labels are matched case-insensitively after trimming. Option 1 (Under 18) has no label because the form gates on an 18-or-over declaration. If Alex renames a label on the form this row is what changes, not the flow.

## MaxCircumstanceScore

Maximum attainable circumstance score, used to render a score as 'n out of N': 10 wellbeing answers x 5 points (50) plus the inverted life-satisfaction answer at up to 10 = 60 (FR-011). BACK TO 60 IN REVISION 0.3, AND NO LONGER AN OPEN ITEM — the reviewer confirmed the life-satisfaction question is the 0-to-10 scale its source documents describe, so rev_feelingscaleanswer became a whole number 0-10, FeelingScaleInversion became an eleven-entry map keyed 0-10, and this row returned to 60. Revision 0.2 had briefly set it to 55 because that question had been built as a five-option picklist. 60 is the figure the raw export header uses ('Overall Circumstance Score (out of 60)'), the figure the Automation Solution Design v0.5 states ('Total = sum of all question scores (max 60)'), and the figure this scoring flow can now actually produce. THIS UNBLOCKS KnockoutThreshold AND THE BORDERLINE BAND (SDD OQ-001, OQ-002): those are absolute scores and the board now knows the scale they sit on.

## IncomeBandUpperBoundMap

Maps each rev_incomeband option value to the top of that band, so the band selected on the form can be compared with IncomeCeiling (FR-015). NFR-019 puts field mappings in the process owner's hands: if the form's income bands change, this row changes and REV | Scoring | Calculate & Flag does not. Option 5 (40,000 GBP or more) is unbounded and carries a sentinel above any realistic ceiling. Option 6 (Prefer not to say) carries -1, which the flow turns into income flag 3 'Not stated - cannot assess' rather than a guess. NOT a pending value: these bounds are the definition of the option set, not a board criterion.
