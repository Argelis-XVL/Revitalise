# Setting Row Descriptions — Full Rationale (D-021)

**Widened 2026-08-21.** `rev_setting.rev_description` is now `MaxLength="1000"` and its format
is `textarea`, so it renders as a growing box rather than a one-line strip. The shortened
descriptions below are kept as they are — they were written to be readable, not merely to fit —
and the full rationale stays here regardless of what the column allows.

**Why this file exists.** `rev_setting.rev_description` had `MaxLength="500"`
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

`scripts/verify-field-length-limits.py` gates this at build time (`config/<slug>-build.yml` →
`field-length-limits`, `C-TECH-060`) so the omission cannot recur silently. It reads the limit
from `Entities/rev_setting/Entity.xml` rather than hardcoding 500, and it also checks `key`
against `rev_name` (100) and `value` against `rev_value` (4000) — neither of which the earlier
`setting-description-length` gate looked at.

---

## LikertPointMap

Maps a wellbeing answer's option VALUE to circumstance points (FR-013). Position 1 ('None of the time' on rev_likertresponse, 'Strongly Disagree' on rev_agreementresponse) scores 5 and position 5 ('All of the time' / 'Strongly Agree') scores 1 — all ten wellbeing questions are worded positively, so a frequent occurrence or an agreement means better wellbeing and therefore less need. ONE MAP SERVES BOTH OPTION SETS AND IS DELIBERATELY NOT DUPLICATED. Revision 0.8 split the three 'Thinking about the last year' questions onto rev_agreementresponse, but the scoring flow looks this map up by the numeric option value — outputs('Parse_likert_point_map')?[string(item()?['response'])] — and never knows which option set the answer came from. Both scales use the same ordinals 1 to 6 with the same direction, so a second map would only be a second place for the same numbers to drift out of step. The name is kept for that reason. KEY "6" ('Not sure') = 0 SINCE 2026-08-20, CONFIRMED WITH EMILY (PROCESS OWNER). A 'Not sure' answer now contributes nothing. THIS SUPERSEDES THE DERIVATION THAT FOLLOWS, WHICH IS KEPT BECAUSE IT IS EVIDENCE, NOT BECAUSE IT STILL GOVERNS: the reconstruction below required 0.5, so with 0 the flow no longer reproduces the 25 published hand-scores - row 25 scores 4 where it was scored 9. That is a deliberate change of policy, not a regression, and any future attempt to reconcile against that export must start from this sentence. NOTE ALSO that the map now holds NO fractional value, so the half-point handling in Round_the_circumstance_score can never fire; it stays as a guard. THE ORIGINAL DERIVATION, FOR THE RECORD: key "6" = 0.5 was new in revision 0.8 AND IS DERIVED FROM GROUND TRUTH, NOT CHOSEN. docs/Import/Book(Sheet1).csv row 25 is a real application that answered 'Not sure' to all ten wellbeing questions and was scored 9 by hand: the life-satisfaction raw answer of 6 contributes 10-6=4 through FeelingScaleInversion, leaving exactly 5 points to be shared by 10 'Not sure' answers — 0.5 each, with no remainder. Reconstructing all 25 rows of that CSV with this map reproduces every published score exactly. THIS IS THE ONLY NON-INTEGER VALUE IN THE MAP and it is why the scoring flow accumulates points in a FLOAT variable and rounds once at the end before writing the int column rev_circumstancescore — see Round_the_circumstance_score. The board can change 0.5 here without a solution change, but a value that is neither a whole number nor a half would BREAK THE ROUNDING STEP, not merely read oddly: since revision 0.9 Round_the_circumstance_score resolves the half point by adding 0.25 to the total before formatting it, and that offset is exact ONLY while .0 and .5 are the only fractional totals that can arise (test report D-015). ScoringInvariants.Tests.ps1 asserts that condition on this very row, so such an edit fails the suite instead of quietly mis-scoring an applicant. UNCHANGED FROM REVISION 0.3: keys 1 to 5, their values, and their direction.

## AgeRangeLabelMap

Maps the age-band labels the live application form actually sends to rev_agerange option values (2=18 to 24 .. 8=75 and over, 9=Not known). The live form asks an age band directly (field 26, optional) and does NOT ask for a date of birth, so this map - not AgeBandMap - is the primary route to rev_agerange. Labels are matched case-insensitively after trimming. Option 1 (Under 18) has no label because the form gates on an 18-or-over declaration. If Alex renames a label on the form this row is what changes, not the flow.

## MaxCircumstanceScore

Maximum attainable circumstance score, used to render a score as 'n out of N': 10 wellbeing answers x 5 points (50) plus the inverted life-satisfaction answer at up to 10 = 60 (FR-011). BACK TO 60 IN REVISION 0.3, AND NO LONGER AN OPEN ITEM — the reviewer confirmed the life-satisfaction question is the 0-to-10 scale its source documents describe, so rev_feelingscaleanswer became a whole number 0-10, FeelingScaleInversion became an eleven-entry map keyed 0-10, and this row returned to 60. Revision 0.2 had briefly set it to 55 because that question had been built as a five-option picklist. 60 is the figure the raw export header uses ('Overall Circumstance Score (out of 60)'), the figure the Automation Solution Design v0.5 states ('Total = sum of all question scores (max 60)'), and the figure this scoring flow can now actually produce. THIS UNBLOCKS KnockoutThreshold AND THE BORDERLINE BAND (SDD OQ-001, OQ-002): those are absolute scores and the board now knows the scale they sit on.

## IncomeBandUpperBoundMap

Maps each rev_incomeband option value to the top of that band, so the band selected on the form can be compared with IncomeCeiling (FR-015). NFR-019 puts field mappings in the process owner's hands: if the form's income bands change, this row changes and REV | Scoring | Calculate & Flag does not. Option 5 (40,000 GBP or more) is unbounded and carries a sentinel above any realistic ceiling. Option 6 (Prefer not to say) carries -1, which the flow turns into income flag 3 'Not stated - cannot assess' rather than a guess. NOT a pending value: these bounds are the definition of the option set, not a board criterion.

## ExceptionalCircumstanceLabelMap

Added 2026-08-17, form-field-corrections pass (W1). Maps the live form's four exceptional-circumstance labels to rev_exceptionalcircumstance option values, following AgeRangeLabelMap's pattern exactly: read by alternate key in `Read_exceptional_circumstance_label_map`, matched case-insensitively after trimming in `Map_exceptional_circumstance_label`, resolved to the matched option or `null` in `Derive_exceptional_circumstance`. `null` (not a guess) is what FR-064 requires when the sent label matches nothing here — the mismatch is then named in `rev_intakereviewnote` rather than silently dropped. This map exists because the column itself was misclassified for one full day (2026-08-16): a Boolean conversion that read raw export column 128 (a genuine Yes/No, held by rev_exceptionalfundingrequested) instead of column 129, this column's real four-option radio. If Alex renames a label on the form, this row is what changes, not the flow — same governance as AgeRangeLabelMap.

## EmploymentStatusLabelMap

Added 2026-08-17, form-field-corrections pass (W2). Maps the live form's five employment-status labels to rev_employmentstatus option values (renamed from rev_currentlyworking, which was a Boolean — the live form has always asked five options, confirmed against the live page 2026-08-17). Same three-action pattern as AgeRangeLabelMap. Option 3, "No, unable to work due to disability/health/caring responsibilities", is why rev_employmentstatus is secured (REV_TrusteeRestricted) unlike its unsecured financial neighbours rev_incomeband/rev_savingsover6000/rev_significantcarecosts — a disability disclosure, not a financial fact, on the same basis as rev_receivesbenefits.

## CareHoursBandLabelMap

Added 2026-08-17, form-field-corrections pass (W5). Maps the live form's five care-hours band labels to rev_carehoursperweek option values, replacing the integer the column was built as against a five-band question. THE BAND 4 VALUE WAS CORRECTED TWICE THIS SESSION: the form-field-corrections plan's revision 1.0 read the live form's "35 – 59 hours" as a likely typo for the standard census banding and recorded "35 - 50 hours"; three independent re-fetches of the live form, then the reviewer directly, confirmed "35 – 59 hours" is what the form actually sends. Kept AS SENT, overlap with band 5 ("50+") across 50–59 hours included — this is V-10 in the change request to Alex and is UNRESOLVED; the map does not paper over it by choosing a cleaner boundary. Matched case- AND dash-insensitively (`replace(replace(x,'–','-'),'—','-')` on both the sent value and the map's own label) because this exact drift — an en-dash in one source, a hyphen in another, describing the same band — is what produced the band-4 misreading in the first place.

## RoundStatisticsMoneyMeasureMinimumPopulation

Added 2026-08-28, TAD Revision 6 (ADR-039 and OQ-043 answer). A disclosure control on the four money-average measures (`averageAmountRequested`, `averageCost` on FR-059/FR-060): if a measure's own population falls below this threshold, the figure is withheld (`null` in the payload), and only the count is shown. Set to 5 per reviewer decision on 2026-08-28. **This is a disclosure control, not a tunable variable like the FR-062 thresholds or `RoundStatisticsStaleAfterSeconds`.** The three thresholds exist to let the process owner respond to lived experience (scoring works different than expected, board decides to tweak a boundary); this population minimum exists for a compliance reason (§6.3.5: statistics over a small group are inherently identifiable). Changing it is a reviewer decision, exercised once at seeding time.

**Why every environment must seed this row:** an absent row withholds all four money measures (which is a safe default for a statistic you did not decide to publish), but it is **not the approved behaviour** per TAD §6.3.5's decision that k = 5. If DEV seeds it and TST/ACC does not, or vice versa, the same round renders differently in two environments. The deployment scripts must seal this value across all three.

**On RoundStatisticsStaleAfterSeconds — corrected 2026-08-30, IMP-0511.** This paragraph previously
said the unseeded state was "correct, fail-safe" and equivalent to "always recompute." That
description was itself wrong: `isCurrent()` compares against `staleAfterSeconds ?? NaN`, and any
comparison against `NaN` is `false` in JavaScript, so an unseeded row does not reproduce
"recompute and show" — it reproduces "recompute and never show any result, ever, including one
this cycle's own poll just watched complete." The round-statistics feature was dark to every
trustee from the moment it shipped until this was found, confirmed live 2026-08-30 (a genuinely
fresh, `Complete`, real-data `rev_roundstatisticsresult` still carried `"staleAfterSeconds":null`).

**OQ-042 is answered: 300 seconds, reviewer decision (Emily) 2026-08-30, DEV seeded the same day
as an urgent operational fix (`wbs:6.9`).** This is the workaround, not the durable fix — the
durable question (whether the poll loop should keep reusing `isCurrent()`'s staleness comparison
for "is the document my own trigger just produced current" at all) is `architect-agent`'s call, per
`docs/improvements/2026-08-30-improvement-review-2.md` §0, not decided here. TST/ACC and PRD carry
the same `300` value in their settings files now and pick it up at their own next promotion
(`promote_mode:manual`) — they were not pushed live by this change. Until a TST/ACC or PRD
promotion runs `seed-settings.ps1`, those two environments remain in the unseeded, dark state this
correction describes, which is a real, current divergence from DEV, not a hypothetical one.
