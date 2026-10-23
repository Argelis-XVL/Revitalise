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

**Update 2026-09-27 (TAD rev 11, ADR-051 item 3).** One alias row added: `Carer breakdown/urgent need` -> 2, the wording the website actually sends beside the option label `Carer breakdown or urgent need`. An alias row, never a widened normalisation, so ADR-024's *never guess the nearest value* keeps its meaning. Label maps are now read from `Normalise_payload`'s output, not straight from the trigger body.

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

**2026-10-02 (TAD rev 15, `ADR-067` C9):** `REV | Acceptance | Create Envelope` now calls
`AddReminders` on the DocuSign **draft**, before the envelope is sent, not after a single
create-and-send call. The row and its `[3,7]` reading are unchanged.

## AcceptanceEmailApplicant / AcceptanceEmailReferee

**Added 2026-10-02, TAD rev 15 (`ADR-068` item 3, item 4), `wbs:3.2`.** Each signer gets their own
DocuSign email. `REV | Acceptance | Create Envelope` reads both rows and sets them on each signer
with the connector's `UpdateEnvelopeRecipient` (`emailNotificationSubject`,
`emailNotificationBody`).

- **Shape.** `dataType` `JSON`, value `{"subject": "...", "body": "..."}`.
- **`{grantReference}`** anywhere in the subject or body is replaced with the grant's reference
- **`{applicationReference}`, `{applicantName}`, `{refereeName}`** (added 2026-10-04) are replaced the same way: the application's reference, the applicant's full name (first + last when the full name is empty) and the referee's first + last name (Referee Name when those are empty). A `\n` in the JSON string is a line break in the DocuSign email.
  (`rev_grant.rev_name`, a pseudonymous reference per `ADR-013`). Nothing else is substituted: no
  name, no amount.
- **The subject must stay within 100 characters** after that replacement (DocuSign's limit). A longer
  subject stops the flow before any draft is created.
- **The referee's body states the access-code rule**, for example *"Open the agreement with the last
  6 numbers of your phone number"*. It must never contain the digits themselves (`ADR-068` item 4).
- **No fallback.** A missing row, or one with an empty subject or body, makes the flow alert the
  process owner and stop. It does not fall back to the applicant's wording, because that wording
  tells the reader a referee signature follows theirs.

**Values per environment.** DEV and TST/ACC carry **provisional test wording** written by
development-agent, marked as such in each row's description. PRD carries the pending token
`{{PENDING_ACCEPTANCE_EMAIL_WORDING}}` in both rows, so `seed-settings.ps1 -Env prd` aborts before
any write rather than emailing real applicants test text. **The wording is Emily's to supply**
(`ADR-068` item 3); replace all three environments' values when she does.

## TitleLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. `Mr.` is E1. Every title carries a trailing-full-stop alias row.

## ApplicantTypeLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. Was an integer in the old contract. `A disabled person` is E1.

## GenderLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. `Prefer to self-describe` is an alias of option 4, `Describes themselves another way`. Equality monitoring only.

## EthnicGroupLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. Equality monitoring only; never read by scoring (C-DOM-030). `White` is E1.

## LikertResponseLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. The seven two-week wellbeing items. `Rarely`, `Often`, `All of the time` are E1. The option values - and therefore LikertPointMap scoring - are unchanged.

## AgreementResponseLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. The three last-year wellbeing items. `Neutral` and `Strongly agree` are E1; the option label `Strongly Agree` differs only by case.

## BreakTypeLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. `Day trips or outings` is E1.

## IncomeBandLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. The form's own wording (`Under £15,000 per year`, en-dashed ranges) as alias rows, then the four option labels.

## HearAboutUsLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. Multi-select, first writer ever for `rev_hearaboutus`. `Google search` and the healthcare-professional label are E1.

## ConditionProfileLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. Serves both condition-profile multi-selects. Option 9's long form is carried twice, once per apostrophe (`'` and `’`), because which one the form sends is unverified.

## CareProvidedTypeLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. Multi-select, first writer ever for `rev_careprovidedtype`. Six short forms from the capture are alias rows.

## OtherFundingStatusLabelMap

Added 2026-09-27, TAD rev 11 (`ADR-051` item 3, `wbs:4.3`). The website sends its native Gravity Forms entry, whose answers are display labels rather than option values, so the intake flow resolves each one through this row (`Setting_<Key>` -> `Map_<field>_label` or the multi-select map filter -> `Derive_<field>`), after trim, case-fold and dash-fold on both sides. Values are TAD Appendix C §C.4 verbatim. Only the labels marked E1 there appeared in the 2026-09-25 sample; the rest are E3 from the 2026-09-11 live-form capture and are `A-INT-06` until Alex posts one test entry per route. A mismatch never guesses: the column is left empty and the label is named in `rev_intakereviewnote`. The fix for a mismatch is a re-seed of this row, not a flow change. Policy/reference data, identical in every environment (DeploymentSettings.Tests.ps1). The intake's row-count guard is now 18. New option set `rev_otherfundingstatus` (1 Yes, 2 No, 3 Applied and awaiting decision). `rev_receivingotherfunding` is still written beside it.


---

# Description history removed 2026-10-23 (WI-0152)
The `description` of every row in the three settings files was rewritten in plain language for the process owner (CO-012). The previous developer-facing descriptions are kept here verbatim, so nothing is lost. Where the three environment files differed, each variant is shown with the file name. Rows whose description is identical everywhere are shown once.

## Previous description: LikertPointMap
Maps a wellbeing answer's option VALUE to circumstance points (FR-013). Position 1 scores 5, position 5 scores 1. Key "6" ('Not sure') = 0, CHANGED FROM 0.5 on 2026-08-20 and confirmed with Emily (process owner). This supersedes the D-014 derivation from the hand-scored export; the map now holds no fractional value, so the half-point rounding can never fire. Full record: provisioning/deploymentSettings/settings-rows.notes.md#LikertPointMap.

## Previous description: FeelingScaleInversion
Inverts the life-satisfaction answer rev_feelingscaleanswer, a whole number 0 to 10, so that a lower reported satisfaction scores more points (FR-012). This is 10 minus the raw answer, expressed as a lookup map so the direction of the scale is configuration rather than arithmetic inside the flow. REPLACED IN REVISION 0.3: it was a five-entry map over a five-option picklist. The Automation Solution Design v0.5 specifies exactly this for Automation #2 Q1 — "inverted (0/10 feeling = 10 points)".

## Previous description: KnockoutThreshold
- **dev-scoring-settings.json:** Circumstance score at or below which the application status becomes Auto-reject. PROVISIONAL VALUE — same figure already accepted for TST/ACC (test-settings.json) — the board's figure is SDD OQ-001.
- **test-settings.json:** Circumstance score at or below which the application status becomes Auto-reject. PROVISIONAL TEST VALUE in TST/ACC — the board's figure is SDD OQ-001.
- **prd-settings.json:** Circumstance score at or below which the application status becomes Auto-reject. Board decision, SDD OQ-001.

## Previous description: BorderlineBandLower
- **dev-scoring-settings.json:** Lower bound (inclusive) of the Borderline review band. PROVISIONAL VALUE — same figure already accepted for TST/ACC (test-settings.json) — SDD OQ-002.
- **test-settings.json:** Lower bound (inclusive) of the Borderline review band. PROVISIONAL TEST VALUE in TST/ACC — SDD OQ-002.
- **prd-settings.json:** Lower bound (inclusive) of the Borderline review band. Board decision, SDD OQ-002.

## Previous description: BorderlineBandUpper
- **dev-scoring-settings.json:** Upper bound (inclusive) of the Borderline review band; a score above it becomes Auto-pass. PROVISIONAL VALUE — same figure already accepted for TST/ACC (test-settings.json) — SDD OQ-002.
- **test-settings.json:** Upper bound (inclusive) of the Borderline review band; a score above it becomes Auto-pass. PROVISIONAL TEST VALUE in TST/ACC — SDD OQ-002.
- **prd-settings.json:** Upper bound (inclusive) of the Borderline review band; a score above it becomes Auto-pass. Board decision, SDD OQ-002.

## Previous description: IncomeCeiling
- **dev-scoring-settings.json:** Annual household income ceiling in GBP. PROVISIONAL VALUE — same figure already accepted for TST/ACC (test-settings.json) — SDD OQ-003.
- **test-settings.json:** Annual household income ceiling in GBP. PROVISIONAL TEST VALUE in TST/ACC — SDD OQ-003.
- **prd-settings.json:** Annual household income ceiling in GBP. Board decision, SDD OQ-003.

## Previous description: AgeBandMap
Maps an age in whole years to a rev_agerange option value (1=Under 18 .. 8=75 and over). Fixed reference data. Option 9 (Not known) is the fallback when no date of birth was supplied and is therefore not in the map.

## Previous description: AgeRangeLabelMap
Maps the age-band labels the live form actually sends to rev_agerange (2=18-24 .. 8=75+, 9=Not known). The live form asks an age band directly, NOT a date of birth, so this map — not AgeBandMap — is the primary route to rev_agerange. Matched case-insensitively after trimming. Option 1 (Under 18) has no label (form gates on 18+). Full derivation kept in provisioning/deploymentSettings/settings-rows.notes.md#AgeRangeLabelMap (D-021).

## Previous description: ExceptionalCircumstanceLabelMap
Maps the exceptional-circumstance labels the live form sends to rev_exceptionalcircumstance option values (FR-064, form-field-corrections pass). Matched case-insensitively after trimming. An unmatched label leaves the column empty rather than guessing - see rev_intakereviewnote. Full derivation: settings-rows.notes.md#ExceptionalCircumstanceLabelMap.

## Previous description: EmploymentStatusLabelMap
Maps the employment-status labels the live form sends to rev_employmentstatus option values (FR-064, form-field-corrections pass). Matched case-insensitively after trimming. An unmatched label leaves the column empty rather than guessing. Full derivation: settings-rows.notes.md#EmploymentStatusLabelMap.

## Previous description: CareHoursBandLabelMap
Maps the care-hours band labels the live form sends to rev_carehoursperweek option values (FR-064, form-field-corrections pass). Matched case- and dash-insensitively after trimming - the live form and other sources render band 2's dash differently. An unmatched label leaves the column empty. Full derivation: settings-rows.notes.md#CareHoursBandLabelMap.

## Previous description: TitleLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_title option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. The trailing full stops are ALIAS rows (the website sends 'Mr.'), never a normalisation. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#TitleLabelMap.

## Previous description: ApplicantTypeLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_applicanttype option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#ApplicantTypeLabelMap.

## Previous description: GenderLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_gender option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. 'Prefer to self-describe' is the form's wording for option 4 (an alias row). Equality monitoring only; never read by scoring. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#GenderLabelMap.

## Previous description: EthnicGroupLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_ethnicgroup option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Equality monitoring only; never read by scoring (C-DOM-030). Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#EthnicGroupLabelMap.

## Previous description: LikertResponseLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_likertresponse option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Used by the seven two-week wellbeing answers (rev_wellbeinganswer1-7). Option values feed LikertPointMap unchanged. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#LikertResponseLabelMap.

## Previous description: AgreementResponseLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_agreementresponse option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Used by the three last-year wellbeing answers (rev_wellbeinganswer8-10). The option labels' capital A/D differ only by case, which the match folds. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#AgreementResponseLabelMap.

## Previous description: BreakTypeLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_breaktype option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#BreakTypeLabelMap.

## Previous description: IncomeBandLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_incomeband option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. The first three are the form's wording (alias rows, en dashes as captured; the match dash-folds both sides); the option labels follow. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#IncomeBandLabelMap.

## Previous description: HearAboutUsLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_hearaboutus option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Multi-select: the flow filters this map by the ticked labels (ADR-051 item 4). Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#HearAboutUsLabelMap.

## Previous description: ConditionProfileLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_conditionprofile option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. Both condition-profile multi-selects (applicant and person supported). Option 9 carries two alias rows, one per apostrophe form, because which one the form sends is unverified. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#ConditionProfileLabelMap.

## Previous description: CareProvidedTypeLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_careprovidedtype option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. The six short forms at the end are alias rows from the 2026-09-11 live-form capture. Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#CareProvidedTypeLabelMap.

## Previous description: OtherFundingStatusLabelMap
ADR-051 item 3 (TAD rev 11, wbs:4.3). Maps the website's native answer labels to rev_otherfundingstatus option values; matched after trim, case-fold and dash-fold (ADR-024) and never guessed - an unmatched label leaves the column empty and is named in rev_intakereviewnote. rev_receivingotherfunding is still written beside it (Yes true, No false, awaiting null). Labels for routes the 2026-09-25 sample left empty are E3 from the 2026-09-11 live-form capture (A-INT-06); re-seed on a mismatch. Full rationale: settings-rows.notes.md#OtherFundingStatusLabelMap.

## Previous description: PostcodeRegionMap
Maps the uppercased alphabetic prefix of a UK outward code to a rev_locationarea option value (1=North East .. 12=Northern Ireland). Longest prefix wins, so match SW before S. Fixed reference data. Option 13 (Not known) is the fallback for an unrecognised or absent postcode and is therefore not in the map.

## Previous description: MaxCircumstanceScore
Maximum attainable circumstance score, for rendering 'n out of N': 10 wellbeing answers x 5 (50) plus the inverted life-satisfaction answer up to 10 = 60 (FR-011). Confirmed 60, not 55 — life-satisfaction is the 0-10 scale its source describes; matches the raw export header and Automation Solution Design v0.5. Unblocks KnockoutThreshold and the Borderline band (SDD OQ-001/002). Full derivation kept in provisioning/deploymentSettings/settings-rows.notes.md#MaxCircumstanceScore (D-021).

## Previous description: IncomeBandUpperBoundMap
EF-29 (2026-09-17): re-seeded to Emily's four confirmed bands (Under 15,000 / 15,000-24,999 / 25,000-34,999 / Over 35,000), replacing the placeholder five-band, 10,000-boundary map and its 'Prefer not to say' sentinel. Maps each rev_incomeband option to the top of that band, compared against IncomeCeiling (FR-015). NFR-019: if the form's income bands change, this row changes, not the scoring flow. Option 4 (Over 35,000) is unbounded with a sentinel above any realistic ceiling. Full derivation kept in provisioning/deploymentSettings/settings-rows.notes.md#IncomeBandUpperBoundMap (D-021).

## Previous description: RoundStatisticsMoneyMeasureMinimumPopulation
Minimum population for money-average measures on trustee landing screen; below this value is withheld, only count shown (TAD §6.3.5, OQ-043). Disclosure control, not tunable: reviewer decision 2026-08-28. Absent row withholds all four money measures (fail-safe but not approved behaviour); unseeded divergence between environments. See settings-rows.notes.md#RoundStatisticsMoneyMeasureMinimumPopulation.

## Previous description: EscalationDays
- **dev-scoring-settings.json:** Days an acceptance envelope may sit unsigned before REV | Acceptance | Reminders & Escalation notifies the process owner (FR-044, TAD 5.9). Added 2026-09-06 for wbs:3.3, DEV only per EX-006/EX-007. MIRRORED into test-settings.json/prd-settings.json on 2026-09-08 per reviewer confirmation that all three environments' rev_setting rows must agree at 18 — EX-006/EX-007 still scope the wbs:3.2/3.3/3.4 DocuSign FLOWS themselves to DEV only pending Revitalise's own DocuSign licence; this row is configuration data, not a flow promotion.
- **test-settings.json:** Days an acceptance envelope may sit unsigned before REV | Acceptance | Reminders & Escalation notifies the process owner (FR-044, TAD 5.9). Added to DEV 2026-09-06 for wbs:3.3 (EX-006/EX-007); mirrored here 2026-09-08 per reviewer confirmation that all three environments' rev_setting rows must agree at 18 — seeded for TST/ACC at this environment's own next promotion (promote_mode:manual). EX-006/EX-007 still scope the wbs:3.2/3.3/3.4 DocuSign FLOWS themselves to DEV only pending Revitalise's own DocuSign licence; this row is configuration data, not a flow promotion.
- **prd-settings.json:** Days an acceptance envelope may sit unsigned before REV | Acceptance | Reminders & Escalation notifies the process owner (FR-044, TAD 5.9). Added to DEV 2026-09-06 for wbs:3.3 (EX-006/EX-007); mirrored here 2026-09-08 per reviewer confirmation that all three environments' rev_setting rows must agree at 18 — seeded for PRD at this environment's own next promotion (promote_mode:manual). EX-006/EX-007 still scope the wbs:3.2/3.3/3.4 DocuSign FLOWS themselves to DEV only pending Revitalise's own DocuSign licence; this row is configuration data, not a flow promotion.

## Previous description: ReminderDays
- **dev-scoring-settings.json:** IMP-0618 RESOLVED 2026-09-06: reviewer decision - the seeded table drives the reminder cadence dynamically, discarding the DocuSign template's own static 2/5-day configuration entirely. [first, second] reminder day (FR-043, TAD 5.9). Read by REV | Acceptance | Create Envelope (wbs:3.2), which calls the DocuSign connector's AddReminders action once per envelope right after creation - not read by wbs:3.3, which remains escalation-only. See settings-rows.notes.md#ReminderDays for the delay/frequency shape mismatch this produces.
- **test-settings.json:** IMP-0618 RESOLVED 2026-09-06: reviewer decision - the seeded table drives the reminder cadence dynamically, discarding the DocuSign template's own static 2/5-day configuration entirely. [first, second] reminder day (FR-043, TAD 5.9). Read by REV | Acceptance | Create Envelope (wbs:3.2), which calls the DocuSign connector's AddReminders action once per envelope right after creation - not read by wbs:3.3, which remains escalation-only. Added to DEV 2026-09-06; mirrored here 2026-09-08 per reviewer confirmation (same EX-006/EX-007 DEV-only scoping applies to the flow itself, not to this settings row). See settings-rows.notes.md#ReminderDays for the delay/frequency shape mismatch this produces.
- **prd-settings.json:** IMP-0618 RESOLVED 2026-09-06: reviewer decision - the seeded table drives the reminder cadence dynamically, discarding the DocuSign template's own static 2/5-day configuration entirely. [first, second] reminder day (FR-043, TAD 5.9). Read by REV | Acceptance | Create Envelope (wbs:3.2), which calls the DocuSign connector's AddReminders action once per envelope right after creation - not read by wbs:3.3, which remains escalation-only. Added to DEV 2026-09-06; mirrored here 2026-09-08 per reviewer confirmation (same EX-006/EX-007 DEV-only scoping applies to the flow itself, not to this settings row). See settings-rows.notes.md#ReminderDays for the delay/frequency shape mismatch this produces.

## Previous description: AcceptanceEmailApplicant
- **dev-scoring-settings.json:** TAD rev 15, ADR-068 item 3 (wbs:3.2): the applicant's own DocuSign email, JSON {subject, body}. Read by REV | Acceptance | Create Envelope and set with UpdateEnvelopeRecipient. {grantReference} is replaced with the grant reference (ADR-013); the subject must stay within 100 characters after that. No row, no subject or no body -> the flow alerts and sends nothing. PROVISIONAL TEST WORDING, not Emily's: replace with the wording Emily supplies. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.
- **test-settings.json:** TAD rev 15, ADR-068 item 3 (wbs:3.2): the applicant's own DocuSign email, JSON {subject, body}. Read by REV | Acceptance | Create Envelope and set with UpdateEnvelopeRecipient. {grantReference} is replaced with the grant reference (ADR-013); the subject must stay within 100 characters after that. No row, no subject or no body -> the flow alerts and sends nothing. PROVISIONAL TEST WORDING, not Emily's: replace with the wording Emily supplies. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.
- **prd-settings.json:** TAD rev 15, ADR-068 item 3 (wbs:3.2): the applicant's own DocuSign email, JSON {subject, body}. Read by REV | Acceptance | Create Envelope and set with UpdateEnvelopeRecipient. {grantReference} is replaced with the grant reference (ADR-013); the subject must stay within 100 characters after that. No row, no subject or no body -> the flow alerts and sends nothing. PRD withheld behind a pending token until Emily supplies the wording, so seed-settings.ps1 aborts rather than emailing applicants test text. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.

## Previous description: AcceptanceEmailReferee
- **dev-scoring-settings.json:** TAD rev 15, ADR-068 items 3-4 (wbs:3.2): the referee's own DocuSign email, JSON {subject, body}. The body must state the access-code RULE (the last 6 numbers of your phone number) and never the digits. {grantReference} is replaced with the grant reference; subject within 100 characters. No row -> the flow alerts and sends nothing. PROVISIONAL TEST WORDING, not Emily's: replace with the wording Emily supplies. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.
- **test-settings.json:** TAD rev 15, ADR-068 items 3-4 (wbs:3.2): the referee's own DocuSign email, JSON {subject, body}. The body must state the access-code RULE (the last 6 numbers of your phone number) and never the digits. {grantReference} is replaced with the grant reference; subject within 100 characters. No row -> the flow alerts and sends nothing. PROVISIONAL TEST WORDING, not Emily's: replace with the wording Emily supplies. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.
- **prd-settings.json:** TAD rev 15, ADR-068 items 3-4 (wbs:3.2): the referee's own DocuSign email, JSON {subject, body}. The body must state the access-code RULE (the last 6 numbers of your phone number) and never the digits. {grantReference} is replaced with the grant reference; subject within 100 characters. No row -> the flow alerts and sends nothing. PRD withheld behind a pending token until Emily supplies the wording, so seed-settings.ps1 aborts rather than emailing applicants test text. See settings-rows.notes.md#AcceptanceEmailApplicant--AcceptanceEmailReferee.

## Previous description: RoundStatisticsStaleAfterSeconds
- **dev-scoring-settings.json:** Freshness window (seconds) for the trustee landing screen's Refresh figures control (TAD §5.3.1, OQ-042). Reviewer decision (Emily) 2026-08-30, urgent fix for IMP-0511: unseeded left staleAfterSeconds null in every response document, so isCurrent()'s NaN comparison never returns true and no computed result was ever shown, including one this cycle's own poll just watched complete. 300 sits inside the two OQ-042 boundaries (above the ~12s poll bound, below a board-meeting length). Tunable, not a disclosure control like RoundStatisticsMoneyMeasureMinimumPopulation. See settings-rows.notes.md#RoundStatisticsStaleAfterSeconds.
- **test-settings.json:** Freshness window (seconds) for the trustee landing screen's Refresh figures control (TAD §5.3.1, OQ-042). Reviewer decision (Emily) 2026-08-30, urgent fix for IMP-0511: unseeded left staleAfterSeconds null in every response document, so isCurrent()'s NaN comparison never returns true and no computed result was ever shown, including one this cycle's own poll just watched complete. 300 sits inside the two OQ-042 boundaries (above the ~12s poll bound, below a board-meeting length). Tunable, not a disclosure control like RoundStatisticsMoneyMeasureMinimumPopulation. See settings-rows.notes.md#RoundStatisticsStaleAfterSeconds. Seeded here for TST/ACC at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.
- **prd-settings.json:** Freshness window (seconds) for the trustee landing screen's Refresh figures control (TAD §5.3.1, OQ-042). Reviewer decision (Emily) 2026-08-30, urgent fix for IMP-0511: unseeded left staleAfterSeconds null in every response document, so isCurrent()'s NaN comparison never returns true and no computed result was ever shown, including one this cycle's own poll just watched complete. 300 sits inside the two OQ-042 boundaries (above the ~12s poll bound, below a board-meeting length). Tunable, not a disclosure control like RoundStatisticsMoneyMeasureMinimumPopulation. See settings-rows.notes.md#RoundStatisticsStaleAfterSeconds. Seeded here for PRD at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.

## Previous description: RoundStatisticsHistoryStartDate
- **dev-scoring-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. The earliest month the all-history month-by-month application count covers. Unseeded is a valid, fail-safe state: months is emitted empty and trackingStartDate null, never an error (§5.1.3 point 1). A wrong value silently shifts every month boundary the feature will ever show — not a value to set experimentally. See settings-rows.notes.md#RoundStatisticsHistoryStartDate.
- **test-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. The earliest month the all-history month-by-month application count covers. Unseeded is a valid, fail-safe state (§5.1.3 point 1); a wrong value silently shifts every month boundary. See settings-rows.notes.md#RoundStatisticsHistoryStartDate. Seeded here for TST/ACC at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.
- **prd-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. The earliest month the all-history month-by-month application count covers. Unseeded is a valid, fail-safe state (§5.1.3 point 1); a wrong value silently shifts every month boundary. See settings-rows.notes.md#RoundStatisticsHistoryStartDate. Seeded here for PRD at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.

## Previous description: RoundStatisticsHistoryPriorApplicationCount
- **dev-scoring-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. Applications received before RoundStatisticsHistoryStartDate, so the screen never silently understates the charity's total history. 0 is a genuine seeded value here, not an unseeded sentinel — Whole Number legitimately seeds to zero. Unseeded (while the start date IS seeded) sets understatedTotal true (§5.1.3 point 2). See settings-rows.notes.md#RoundStatisticsHistoryPriorApplicationCount.
- **test-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. Applications received before RoundStatisticsHistoryStartDate; 0 is a genuine seeded value, not an unseeded sentinel. Unseeded while the start date IS seeded sets understatedTotal true (§5.1.3 point 2). See settings-rows.notes.md#RoundStatisticsHistoryPriorApplicationCount. Seeded here for TST/ACC at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.
- **prd-settings.json:** FR-080/FR-082, TAD ADR-049 §5.1.3, OQ-050 answer, reviewer decision 2026-09-19. Applications received before RoundStatisticsHistoryStartDate; 0 is a genuine seeded value, not an unseeded sentinel. Unseeded while the start date IS seeded sets understatedTotal true (§5.1.3 point 2). See settings-rows.notes.md#RoundStatisticsHistoryPriorApplicationCount. Seeded here for PRD at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.

## Previous description: RoundStatisticsMonthlyAnomalyThresholdPercent
- **dev-scoring-settings.json:** FR-081, TAD ADR-050 §5.1.3 part 3, OQ-049 answer, reviewer decision 2026-09-19 (plan Addendum). A month is flagged anomalous when its count deviates from its own trailing six-month mean by more than this percentage. Unseeded, or fewer than six trailing months of history exist yet, sets anomaly null on that month (fail-safe, §5.1.3 point 4) — never a guessed flag, never a computation error. Lower-stakes than the two history settings above: a wrong value here mistunes which months get flagged, a sensitivity question correctable at any time with no history implication. See settings-rows.notes.md#RoundStatisticsMonthlyAnomalyThresholdPercent.
- **test-settings.json:** FR-081, TAD ADR-050 §5.1.3 part 3, OQ-049 answer, reviewer decision 2026-09-19 (plan Addendum). A month is flagged anomalous when its count deviates from its own trailing six-month mean by more than this percentage. Unseeded, or fewer than six trailing months of history exist yet, sets anomaly null on that month (fail-safe, §5.1.3 point 4). Lower-stakes than the two history rows above: a wrong value here mistunes which months get flagged, correctable at any time with no history implication. See settings-rows.notes.md#RoundStatisticsMonthlyAnomalyThresholdPercent. Seeded here for TST/ACC at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.
- **prd-settings.json:** FR-081, TAD ADR-050 §5.1.3 part 3, OQ-049 answer, reviewer decision 2026-09-19 (plan Addendum). A month is flagged anomalous when its count deviates from its own trailing six-month mean by more than this percentage. Unseeded, or fewer than six trailing months of history exist yet, sets anomaly null on that month (fail-safe, §5.1.3 point 4). Lower-stakes than the two history rows above: a wrong value here mistunes which months get flagged, correctable at any time with no history implication. See settings-rows.notes.md#RoundStatisticsMonthlyAnomalyThresholdPercent. Seeded here for PRD at this environment's own next promotion (promote_mode:manual) — not pushed live by this dispatch, which is DEV only.

## Previous description: LocalAuthorityRegisterMultiAuthorityThresholdPercent
- **dev-scoring-settings.json:** wbs:4.6 (CO-004), TAD postcode-lookup-architecture.md S13 (OQ-200), reviewer decision 2026-09-23 (Anna Southern), CO-004 TAD Revision 2. Same value as test-settings.json/prd-settings.json (DEV should score identically to TST/ACC/PRD — see this file's own top-level comment). An outward code is flagged Multi-Authority when a second local authority holds AT LEAST this percentage of its live unit postcodes; otherwise it resolves to the modal authority. Read by provisioning/dataverse/seed-local-authority-register.ps1 at the start of every harvest run.
- **test-settings.json:** wbs:4.6 (CO-004), TAD postcode-lookup-architecture.md S13 (OQ-200), reviewer decision 2026-09-23 (Anna Southern), CO-004 TAD Revision 2. An outward code is flagged Multi-Authority when a second local authority holds AT LEAST this percentage of its live unit postcodes; otherwise it resolves to the modal authority. Read by provisioning/dataverse/seed-local-authority-register.ps1 at the start of every harvest run - if this row is unseeded, the harvester fails the run with a named reason and writes nothing rather than inventing a threshold (TAD S13's own stated default).
- **prd-settings.json:** wbs:4.6 (CO-004), TAD postcode-lookup-architecture.md S13 (OQ-200), reviewer decision 2026-09-23 (Anna Southern), CO-004 TAD Revision 2. An outward code is flagged Multi-Authority when a second local authority holds AT LEAST this percentage of its live unit postcodes; otherwise it resolves to the modal authority. Read by provisioning/dataverse/seed-local-authority-register.ps1 at the start of every harvest run - if this row is unseeded, the harvester fails the run with a named reason and writes nothing rather than inventing a threshold (TAD S13's own stated default).

## Previous description: RedactionNeutralTerms
Narrative scrubbing (TAD ADR-076): the client's Anonymisation Key. One 'word = neutral word' per line ('word = first or second' where the sentence decides). Feeds the rewrite prompt, check P2 (right side) and the gendered residue check (left side). Synthetic examples only: never paste text from an application into this row.

## Previous description: RedactionTitles
Narrative scrubbing (TAD ADR-076): titles the rewrite prompt removes, one per line, 1 to 10 letters with an optional full stop. Also the title residue check, matched with the capitals as written. Write 'none' for no titles. Synthetic examples only: never paste text from an application into this row.

## Previous description: RedactionNameRules
Narrative scrubbing (TAD ADR-076): how the rewrite prompt handles [NAME], one rule per line in plain words. Feeds the prompt only. Synthetic examples only: never paste text from an application into this row.

## Previous description: RedactionLabels
Narrative scrubbing (TAD ADR-076): the labels the rewrite prompt may write, '[LABEL] = what it covers', one per line, the label in capitals in square brackets. Feeds the prompt and check P2. Synthetic examples only: never paste text from an application into this row.

## Previous description: RedactionConfidenceThreshold
Narrative scrubbing (TAD ADR-078, FR-029, wbs:5.4): an application whose lowest extractor score is below this value gets the hint below-threshold on the process owner's card. A review signal only: the flow never releases, she releases every application. 0.85, 85 or 85% all mean 85%. Created once, then the process owner's; wbs:5.7 calibrates it.

## Previous description: AmountLimitHolidayAccommodation
Largest amount, in whole pounds, that can be requested for Holiday accommodation without ticking the exceptional funding request. A request over this, with no exceptional funding, becomes Auto-reject (SDD A-10, FR-102, FR-017). Enter digits only, for example 500: a value with a pound sign or a decimal point stops scoring with an alert. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: AmountLimitDayTripsOrOutings
Largest amount, in whole pounds, that can be requested for Day trips or outings without ticking the exceptional funding request. A request over this, with no exceptional funding, becomes Auto-reject (SDD A-10, FR-102, FR-017). Enter digits only, for example 100: a value with a pound sign or a decimal point stops scoring with an alert. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: AmountLimitActivityOrExperience
Largest amount, in whole pounds, that can be requested for an Activity or Experience without ticking the exceptional funding request. A request over this, with no exceptional funding, becomes Auto-reject (SDD A-10, FR-102, FR-017). Enter digits only, for example 100: a value with a pound sign or a decimal point stops scoring with an alert. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: AmountLimitRespiteCareFacilityStay
Largest amount, in whole pounds, that can be requested for a Respite Care Facility stay without ticking the exceptional funding request. A request over this, with no exceptional funding, becomes Auto-reject (SDD A-10, FR-102, FR-017). Enter digits only, for example 500: a value with a pound sign or a decimal point stops scoring with an alert. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: AmountLimitOther
Largest amount, in whole pounds, that can be requested for a break type of Other without ticking the exceptional funding request. A request over this, with no exceptional funding, becomes Auto-reject (SDD A-10, FR-102, FR-017). Enter digits only, for example 500: a value with a pound sign or a decimal point stops scoring with an alert. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: SavingsRuleEnabled
Whether an application whose applicant answered Yes to savings over 6,000 pounds becomes Auto-reject (SDD A-10, FR-103, FR-017). Enter true or false and nothing else: any other value stops scoring with an alert rather than switching the rule off. Create-only: the process owner edits it in the app and a deploy never overwrites it.

## Previous description: PriorFundingRuleEnabled
Whether an application whose applicant was funded by Revitalise before, and answered No to that funding being more than 12 months ago, becomes Auto-reject (SDD A-10, FR-104, FR-017, EF-34). Enter true or false and nothing else: any other value stops scoring with an alert rather than switching the rule off. Create-only: the process owner edits it in the app and a deploy never overwrites it.
