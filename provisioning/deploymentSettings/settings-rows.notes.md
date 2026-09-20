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

Maps each rev_incomeband option value to the top of that band, so the band selected on the form can be compared with IncomeCeiling (FR-015). NFR-019 puts field mappings in the process owner's hands: if the form's income bands change, this row changes and REV | Scoring | Calculate & Flag does not. NOT a pending value: these bounds are the definition of the option set, not a board criterion.

**EF-29, re-seeded 2026-09-17.** Emily's mail body and her attachment's *Income Values* sheet both gave the same four bands the live form asks (`docs/Import/2026-09-11-live-application-form-capture.md` §2), matching what this row already needed to become: Under £15,000 / £15,000–£24,999 / £25,000–£34,999 / Over £35,000. The old five-band, £10,000-boundary map (`{1:9999,2:19999,3:29999,4:39999,5:999999999,6:-1}`) was a placeholder — no client had confirmed the bands when it was seeded — and its option 6, *Prefer not to say*, was dropped in the same option-set edit rather than kept as a sixth entry: the live form never offered it, so no real application can ever hold it, and M-07's own rule is that trimming an option set is safe only *before* any application exists. Safe at the point this was done because DEV and Acceptance held demo data only. Option 4 (Over £35,000) is unbounded and carries a sentinel above any realistic ceiling, the same pattern the old option 5 used. The `-1` sentinel for "not stated" is now produced entirely by `Resolve_income_band_upper_bound`'s own empty-value branch (see the flow), not by a map entry — there is no longer an option whose *meaning* is "prefer not to say," only an absent answer.

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

## RoundStatisticsHistoryStartDate / RoundStatisticsHistoryPriorApplicationCount

Added 2026-09-19, `wbs:6.10`, TAD ADR-049 (Revision 9), FR-080/FR-082, Amendment A-07. Two
settings the flow's new all-history, month-by-month application-count recompute reads, on the
same `rev_setting` mechanism as every other threshold this screen uses (ADR-010, NFR-019).

**`RoundStatisticsHistoryStartDate` (Date).** The earliest month `historicApplicationsByMonth`
covers. Every calendar month from this date to the current month gets one entry — this is what
makes the loop's iteration count a function of elapsed time rather than of the number of
applications the charity has ever received (§5.1.3's load-bearing structural argument). Unseeded
is a defined, fail-safe state: `months` is emitted as an empty array and `trackingStartDate` is
`null`, never an error and never a guessed range (§5.1.3 point 1). **Unlike
`RoundStatisticsStaleAfterSeconds`, this is not a value the process owner should set
experimentally** — a wrong value silently shifts every month boundary the feature will ever show,
for the life of the solution (ADR-049 Consequences).

**`RoundStatisticsHistoryPriorApplicationCount` (Whole Number).** The number of applications the
charity received before `RoundStatisticsHistoryStartDate` — so a total this screen ever prints is
not silently missing a known-nonzero earlier population. Unlike `RoundStatisticsStaleAfterSeconds`
and `RoundStatisticsMoneyMeasureMinimumPopulation`, **`0` is a legitimate, fully seeded value
here** — it means "tracking starts at the beginning of the charity's own history," not "unseeded."
The unseeded state is distinguished by row absence, not by the value `0`: absent while
`RoundStatisticsHistoryStartDate` IS seeded sets `understatedTotal: true` — the one combination
that could otherwise silently omit a known-nonzero pre-tracking population from a total the screen
prints (§5.1.3 point 2). Both absent, or both seeded: `understatedTotal: false` (§5.1.3 point 3).

**Seed values — OQ-050, answered by the reviewer 2026-09-19: `RoundStatisticsHistoryStartDate =
2026-02-16`, `RoundStatisticsHistoryPriorApplicationCount = 0`.** Seeded in DEV by this dispatch
(`wbs:6.10`); TST/ACC and PRD carry the same rows in their settings files now and pick them up at
each environment's own next promotion (`promote_mode:manual`), on the same pattern
`RoundStatisticsStaleAfterSeconds` and `EscalationDays` already established — not pushed live by
this dispatch, which is DEV only.

**Why every environment must eventually seed both, not just the start date.** An environment that
seeds `RoundStatisticsHistoryStartDate` alone — for example TST/ACC or PRD between this dispatch
and their own next promotion — renders `months` in full but `understatedTotal: true` until
`RoundStatisticsHistoryPriorApplicationCount` is seeded too. That is the fail-safe direction
(§5.1.3 point 2's own text: "historic totals are not silently understated"), not a defect, but a
real, current, and temporary divergence between DEV and the other two environments until they are
promoted — the same class of divergence `RoundStatisticsStaleAfterSeconds`'s own note above
records.

## RoundStatisticsMonthlyAnomalyThresholdPercent

Added 2026-09-19, `wbs:6.10`, TAD ADR-050 (Revision 10), FR-081, Amendment A-07 — OQ-049's
answer. The third `rev_setting` row `historicApplicationsByMonth`'s per-month loop reads, on the
same mechanism as `RoundStatisticsHistoryStartDate`/`RoundStatisticsHistoryPriorApplicationCount`
above and `RoundStatisticsStaleAfterSeconds`.

**What it drives.** Each month's `anomaly` flag: `true` when that month's application count
deviates from its own trailing six-month mean by more than this percentage, `false` when it does
not, `null` when the comparison cannot be made yet (fewer than six trailing months of history, or
this row itself unseeded — §5.1.3 point 4's fail-safe). Unlike the two history settings above, a
wrong value here is lower-stakes: it mistunes which months get flagged, a sensitivity question
correctable at any time with no implication for the historical record itself (ADR-050
Consequences, negative part 1).

**Seed value — OQ-049, answered by the reviewer 2026-09-19 (plan Addendum): `50`.** Unlike
`RoundStatisticsHistoryStartDate`'s seed, this one was already known when ADR-050 was written, so
it is seeded in DEV by this dispatch (`wbs:6.10`) rather than left pending a further reviewer
answer. TST/ACC and PRD carry the same row in their settings files now and pick it up at each
environment's own next promotion (`promote_mode:manual`) — not pushed live by this dispatch, which
is DEV only. Until that promotion runs `seed-settings.ps1`, those two environments render every
month's `anomaly` as `null` (the unseeded fail-safe), the same class of temporary,
`promote_mode:manual`-driven divergence `RoundStatisticsStaleAfterSeconds`'s own note above and
`RoundStatisticsHistoryStartDate`'s note records for their rows.

**Why `0` is a legitimate seed value here, unlike `RoundStatisticsMoneyMeasureMinimumPopulation`.**
A `0%` threshold flags every month with any non-zero deviation from its trailing mean — a real,
if aggressive, business choice, not a value the mechanism confuses with "unseeded." The unseeded
state is distinguished by row absence, exactly as `RoundStatisticsHistoryPriorApplicationCount`
already establishes for its own zero-is-valid Whole Number.

## EscalationDays

Added 2026-09-06, `wbs:3.3`, DEV only per EX-006/EX-007. Set to 14 per TAD §5.9's own literal
("escalation to the process owner with the applicant's details at 14 days", FR-044). Read by
`REV | Acceptance | Reminders & Escalation` with a coalesce fallback to the same literal `14` if
this row is ever absent (A-DS-6 — a deliberate resilience choice, not a silent invented figure,
since the fallback IS the TAD's own stated value; see the wbs:3.3 Dev Summary revision).

**MIRRORED 2026-09-08.** This row was DEV-only when first added, on the same DocuSign-licence
dependency (EX-006/EX-007) that keeps the wbs:3.2/3.3/3.4 flows themselves DEV-only. The reviewer
confirmed the DEV-only *scoping* was never meant to extend to this settings row: EX-006/EX-007
gate promoting the DocuSign automation *flows*, not seeding a configuration value that those flows
read. `test-settings.json` and `prd-settings.json` now carry the same `EscalationDays` row and will
pick it up at each environment's own next promotion (`promote_mode:manual`) — this is a data-sync
correction, not a change to either exception's scope.

## ReminderDays

**MIRRORED 2026-09-08**, same correction and same rationale as `EscalationDays` above:
`test-settings.json` and `prd-settings.json` now carry this row too, closing the gap where they had
silently diverged from DEV since 2026-09-06.

**IMP-0618 RESOLVED 2026-09-06.** This paragraph previously said `ReminderDays` was deliberately
NOT seeded anywhere, because the reviewer had stated that reminders are configured natively on
the DocuSign template itself (2 and 5 days) — a real contradiction against TAD §5.9's "3 and 7
days" wording. The reviewer's explicit follow-up decision reverses that: **if a dynamic,
per-envelope override path exists in the connector, use it and discard the template's static
values entirely — the seeded table wins.**

Checked directly against the connector reference (`learn.microsoft.com/connectors/docusign/`,
re-fetched 2026-09-06): the envelope-creation action `REV | Acceptance | Create Envelope` uses
(`SendEnvelope`, operationId of "Create envelope using template with recipients") has **no**
notification/reminder parameter at all — only `accountId`, `status`, `templateId`, `signers`,
`emailSubject`, `emailBody`. But a **separate**, documented action exists: `Add reminders for an
envelope` (operationId `AddReminders` — `accountId`, `envelopeId`, `reminderEnabled`,
`reminderDelay`, `reminderFrequency`, `expireAfter`), callable once the envelope exists. This IS
the dynamic per-envelope override path the reviewer asked about — just not a parameter on the
create action itself, a follow-up call to it.

`REV | Acceptance | Create Envelope` (wbs:3.2) now calls `AddReminders` immediately after
`Create_and_send_the_envelope` succeeds, reading this row (A-DS-11, that flow's own Dev Summary
revision). **Setting the envelope-level reminder cadence this way overrides whatever the template
itself has configured** — DocuSign's own model treats envelope-level notification settings as
taking precedence over template-configured ones (E2/E3: well-known platform behaviour, not yet
confirmed live against this specific tenant/template) — so the template's static 2/5-day setting
becomes moot the moment this ships; the reviewer does not need to reconfigure or disable it
himself, though he may wish to for clarity when next editing the template.

**One shape mismatch, honestly recorded, not smoothed over:** `AddReminders`'s parameters are a
`reminderDelay` (days after send to the FIRST reminder) and a `reminderFrequency` (days between
EVERY reminder thereafter) — not two independent fixed days. `[3,7]` is read as
`reminderDelay=3`, `reminderFrequency=4` (7-3), which reproduces "day 3, day 7" as the first two
firings but does **not** stop repeating every 4 days after that the way "reminders at 3 and 7
days" reads literally. This is a genuine platform-shape constraint (the connector has no
"send exactly N reminders then stop" primitive short of `expireAfter`, which voids the whole
envelope rather than only stopping reminders), not a guess — recorded as part of `A-DS-11` in the
wbs:3.2 Dev Summary revision, open for the reviewer to accept or to ask for a different resolution
(e.g. a smaller `reminderFrequency`, or accepting the repeat as a feature rather than a defect,
since an unsigned envelope arguably SHOULD keep reminding until WBS 3.3's escalation takes over
at day 14).
