# Trustee Portal — individual application: Trustee Pack field map (WI-0005, wbs:6.8)

**What this is.** Every row the Trustee Pack prints for one individual application, in the
Pack's order, mapped to the Dataverse column that holds it, to what the portal showed before this
pass, and to what it shows now. It is the checklist for WI-0005: you should not have to list
fields yourself. Check this table against the PDF instead.

**Updated after code review (2026-09-30).** The reviewer (Xander Lykopoulos) answered the six
decisions and approved "with the above changes". Those answers are applied below: status and
review round at the top of the Summary, three conditional "other" notes, F5 shown from a new
redacted twin, and the portal-only section removed. They are listed together in
[Approved deviations](#approved-deviations-from-the-pack).

**Source.** [`docs/Import/3. Round 4 - Individual Applications.pdf`](../Import/3.%20Round%204%20-%20Individual%20Applications.pdf),
pages 1–2. Page 3 starts the next application (ID 92973), which confirms that pages 1–2 are one
application. Labels are copied character for character, including the Pack's own wording where it
is ungrammatical (F6).

**Where the order lives in code.** The screen renders
[`applicationDetailLayout.ts`](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L569)
and nothing else. Its test holds an independent transcription of these two PDF pages
([`applicationDetailLayout.test.ts#L29`](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.test.ts#L29))
and fails, naming the section, if a row moves, is dropped or is relabelled. A second test checks
that the rendered screen matches the spec
([`ApplicationDetailPage.test.tsx#L63`](../../src/code-apps/trustee-review-portal/src/pages/ApplicationDetailPage.test.tsx#L63)).
Row ids (S1, D5, …) are the same in this table and in the code.

**Column ground truth.** The `IsSecured` flags come from
[`Entities/rev_application/Entity.xml`](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_application/Entity.xml),
and "which question writes which column" comes from the intake flow's `Normalise_payload`. The
restricted rows were checked against `REV_TrusteeRestricted` in
[`FieldSecurityProfiles.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml).
"Before" cites `CasePanels.tsx` at commit `9ded0a2`, the version before this pass.

## Counts

| | Rows |
|---|---|
| **Rows the Pack prints (pages 1–2)** | **45** |
| Rendered in the Pack's position, with the Pack's label | 45 |
| — read from a column a trustee can read | 42 |
| — of those, withheld until the anonymised text is released (D12, D13, A4, A6, F5) | 5 |
| — of those, filled by the grant admin by hand until the form has date pickers (S4, S5, D3, D4; WI-0010) | 4 |
| — rendered as "Restricted": secured, never requested (F1, F2, F3) | 3 |
| **Added this pass** (the row did not exist on the screen before) | **26** |
| Kept, moved and/or relabelled | 19 |
| **Approved deviations** (non-Pack rows the reviewer placed inside Pack sections) | **5**: S0a, S0b, D11a, A3a, A3b (3 of them conditional) |
| **Not shown by ruling** (WI-0011, or the 2026-09-30 personal-data ruling) | **0**: pages 1–2 print none of those fields |
| **Gaps for you** | **3**: secured (F1, F2, F3), by design. F5's twin also needs one live schema run before it can be read (see below) |

Columns added to the portal's read: 13 (12 existing columns plus the new twin
`rev_carecostsexplanationredacted`). Removed: 8 (`rev_providerpreference`, `rev_scorebreakdown`,
`rev_provisionaldate`, `rev_exceptionalfundingrequested`, `rev_incomeflag`,
`rev_exceptionalfundingdetailredacted`, `rev_careprovidedexampleredacted`,
`rev_othercareprovidedtyperedacted`).

## The map

Action key: **ADD** = new row. **MOVE** = was in another section. **RELABEL** = now the Pack's
label. **GAP** = see "Gaps" below.

### Summary (Pack p.1, "…INDIVIDUAL- Summary")

| Row | Pack label (verbatim) | Dataverse column | Before this pass | Now | Action |
|---|---|---|---|---|---|
| S1 | Application ID | `rev_name` (the pseudonymous reference, REV-YYYY-NNN). **Reviewer 2026-09-30: "ApplicationID is the rev number … of the application table"** | `<h1>` only, no row | [L225](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L225) | ADD. Decided: `rev_name`, not the website entry number the Pack prints |
| S2 | Are you? | `rev_applicant.rev_applicanttype` | "Applicant type", in Care-support description (L257) | [L227](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L227) | ADD (the Pack repeats it at A1) |
| S3 | Overall Current Circumstance Score (Out of 60, 60 as worst) | `rev_circumstancescore` | "Score", Summary (L195) | [L232](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L232) | RELABEL |
| S4 | Start Date | `rev_breakstart` | half of "Preferred dates", Application Details (L425) | [L239](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L239) | ADD. GAP (empty column, WI-0010) |
| S5 | End Date | `rev_breakend` | the other half of "Preferred dates" (L425) | [L240](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L240) | ADD. GAP (empty column, WI-0010) |
| S6 | Individual Total Amount Requesting Revitalise inc. Exceptional Funding | `rev_amountrequested` + `rev_additionalamountrequested` | "Total funding requested", Application Details (L431) | [L242](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L242) | MOVE + RELABEL |
| S7 | Exceptional Funding Amount | `rev_additionalamountrequested` | not shown (OQ-031) | [L248](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L248) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |

### Application Details (Pack p.1)

| Row | Pack label (verbatim) | Dataverse column | Before this pass | Now | Action |
|---|---|---|---|---|---|
| D1 | Type of Break | `rev_breaktype` | "Type of break" (L423) | [L267](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L267) | RELABEL |
| D2 | Location of Activity | `rev_breaklocation` | "Break location" (L428) | [L271](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L271) | RELABEL |
| D3 | Start Date | `rev_breakstart` | half of "Preferred dates" (L425) | [L272](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L272) | RELABEL (split). GAP (WI-0010) |
| D4 | End Date | `rev_breakend` | the other half (L425) | [L273](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L273) | RELABEL (split). GAP (WI-0010) |
| D5 | Accommodation or Activity Cost | `rev_accommodationcost` | not shown (OQ-031) | [L275](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L275) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |
| D6 | Travel Costs | `rev_travelcost` | not shown (OQ-031) | [L279](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L279) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |
| D7 | Other Costs | `rev_othercost` | not shown (OQ-031) | [L280](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L280) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |
| D8 | Total Estimated Cost | `rev_costs` (Dataverse's calculated sum of D5–D7) | "Total costs" (L440) | [L281](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L281) | RELABEL |
| D9 | Amount Requesting Revitalise Individual | `rev_amountrequested` | only inside the combined total (L431) | [L283](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L283) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |
| D10 | Exceptional Amount Requested | `rev_additionalamountrequested` | only inside the combined total (L431) | [L288](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L288) | ADD. **Reverses OQ-031**, confirmed by the reviewer 2026-09-30: "Agreed. Keep the fields to match the PDF." |
| D11 | Exceptional Circumstance | `rev_exceptionalcircumstance` | on the list screen only; not on this screen | [L293](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L293) | ADD |
| D12 | Please briefly explain how this break would benefit you | `rev_narrativeredacted` (the anonymised copy; intake writes this question to the secured narrative) | "Anonymised narrative" panel, 2nd on the page (L159) | [L312](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L312) | MOVE + RELABEL. Withheld until released |
| D13 | Please briefly explain why you’re unable to fund this break yourself? | `rev_unabletofundexplanationredacted` | "Why unable to fund the break", in **Financial eligibility** (L321) | [L319](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L319) | MOVE + RELABEL. Withheld until released |

### About Applicant (Pack pp.1–2)

| Row | Pack label (verbatim) | Dataverse column | Before this pass | Now | Action |
|---|---|---|---|---|---|
| A1 | Are you? | `rev_applicant.rev_applicanttype` | "Applicant type", Care-support description (L257) | [L338](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L338) | MOVE + RELABEL |
| A2 | Do you or the person you support have a disability as defined by the Equality Act 2010? | `rev_hasequalityactdisability` or `rev_supportrecipienthasequalityactdisability` (the form asks one or the other; both are panel-visible by your 2026-09-25 ruling) | not shown | [L343](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L343) | ADD |
| A3 | Please select all conditions or illnesses that apply? | `rev_conditionprofile` or `rev_supportrecipientconditionprofile` | two rows, "Condition profile" and "Support recipient condition profile", in Condition and circumstance (L352, L356) | [L355](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L355) | MOVE + RELABEL (two rows merged into the Pack's one) |
| A4 | Brief Confirmation | `rev_disabilityimpactdescriptionredacted` or `rev_supportrecipientdisabilityimpactdescriptionredacted` | not shown | [L380](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L380) | ADD. Withheld until released (intake never writes these anonymised copies) |
| A5 | As a carer, what type of care and support do you personally provide? | `rev_careprovidedtype` | "Type of care provided" (L259) | [L393](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L393) | RELABEL |
| A6 | Brief Description of Care Support Received or Provided | `rev_caresupportdescriptionredacted` | "Care-support description" (L270) | [L398](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L398) | RELABEL. Withheld until released |
| A7 | As a carer, on average how many hours of support do you provide a week? | `rev_carehoursperweek` | "Hours of support per week" (L263) | [L403](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L403) | RELABEL |

Where the form asks about the applicant **and** about the person they support, A2–A4 show
whichever was answered. If both were answered, the row shows both, labelled "You:" and "The person
you support:", rather than silently choosing one.

### Current Circumstances (Pack p.2)

| Row | Pack label (verbatim) | Dataverse column | Before this pass | Now | Action |
|---|---|---|---|---|---|
| C1 | Overall Current Circumstances Score (Out of 60) | `rev_circumstancescore` | Summary only | [L427](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L427) | ADD (the Pack repeats it) |
| C2 | Overall, how satisfied are you with your life nowadays? (0 being not at all) | `rev_feelingscaleanswer` (the answer as entered, never the scoring inversion) | only inside the free-text score breakdown (L221) | [L432](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L432) | ADD |
| — | *sub-heading* In the last 2 weeks… | — | — | h3 | ADD |
| C3 | I’ve been feeling optimistic about the future | `rev_wellbeinganswer1` (frequency scale) | only inside the score breakdown | [L447](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L447) | ADD |
| C4 | I’ve been feeling useful | `rev_wellbeinganswer2` | same | [L452](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L452) | ADD |
| C5 | I’ve been feeling relaxed | `rev_wellbeinganswer3` | same | [L457](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L457) | ADD |
| C6 | I’ve been dealing with problems well | `rev_wellbeinganswer4` | same | [L462](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L462) | ADD |
| C7 | I’ve been thinking clearly | `rev_wellbeinganswer5` | same | [L467](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L467) | ADD |
| C8 | I’ve been feeling close to other people | `rev_wellbeinganswer6` | same | [L472](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L472) | ADD |
| C9 | I’ve been able to make up my own mind about things | `rev_wellbeinganswer7` | same | [L477](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L477) | ADD |
| — | *sub-heading* In the last year… | — | — | h3 | ADD |
| C10 | Go out and do something you enjoy | `rev_wellbeinganswer8` (agreement scale) | same | [L487](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L487) | ADD |
| C11 | Enjoy other people’s company | `rev_wellbeinganswer9` | same | [L492](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L492) | ADD |
| C12 | Have a break when you’ve needed one | `rev_wellbeinganswer10` | same | [L497](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L497) | ADD |

### Financial Eligibility (Pack p.2)

| Row | Pack label (verbatim) | Dataverse column | Before this pass | Now | Action |
|---|---|---|---|---|---|
| F1 | Do you currently receive means tested benefits? | `rev_receivesbenefits`, **secured** (`REV_TrusteeRestricted`) | "Receives Means-Tested Benefits", restricted, 4th in the panel (L316) | [L516](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L516) | RELABEL, reorder. GAP (secured) |
| F2 | Benefit Provider | `rev_benefitprovider`, **secured** | "Benefit Provider", restricted (L316) | [L521](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L521) | reorder. GAP (secured) |
| F3 | Are you currently working? | `rev_employmentstatus`, **secured** | "Employment Status", restricted (L316) | [L526](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L526) | RELABEL, reorder. GAP (secured) |
| F4 | Approximate Household Income | `rev_incomeband` | "Income band", 2nd in the panel (L314) | [L531](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L531) | RELABEL, reorder |
| F5 | If you have significant care costs, please briefly explain | `rev_carecostsexplanationredacted`, the **new** redacted twin of the secured `rev_carecostsexplanation` (reviewer 2026-09-30: "Show … as a narrativescrubbed version, like other columns. Add the column to the datamodel.") | not shown | [L537](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L537) | ADD. Withheld until released. Needs the live schema run below |
| F6 | Do you savings over £6,000? | `rev_savingsover6000` | "Savings over £6,000" (L315) | [L545](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L545) | RELABEL (the Pack's own wording kept) |

## Approved deviations from the Pack

These rows are not in the Pack. The reviewer placed them inside the Pack's sections on
2026-09-30, and the spec test pins each one to its decision and its position.

| Row | Label | Column | Where | When shown | Now | Reviewer's decision (verbatim) |
|---|---|---|---|---|---|---|
| S0a | Status | `rev_status` | top of Summary | always | [L211](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L211) | "Rev_status and rev_reviewround can be shown at the top. in the summary section." |
| S0b | Review round | `rev_reviewround` | Summary, after S0a | always | [L217](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L217) | same |
| D11a | Other exceptional circumstance | `rev_otherexceptionalcircumstanceredacted` (withheld until released) | directly after D11 | only when D11 is "Other (please specify)" | [L305](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L305) | "otherexceptionale circumstance redacted should go with D11 if in D11 other is selected." |
| A3a | Other condition notes | `rev_otherconditionredacted` (withheld until released) | directly after A3 | only when the applicant's own condition profile includes "Other (please specify)" | [L366](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L366) | "The same goes for otherconditionredacted and supportrecipientotherconditionredacted This one has to be shown if other is selected in conditionprofile A3" |
| A3b | Other condition notes (the person you support) | `rev_supportrecipientotherconditionredacted` (withheld until released) | after A3a | only when the supported person's condition profile includes "Other (please specify)" | [L373](../../src/code-apps/trustee-review-portal/src/domain/applicationDetailLayout.ts#L373) | same |

**One reading to confirm.** A3 shows either the applicant's own conditions or the supported
person's. Each "other" note is therefore shown when **its own** profile includes Other. A3a follows
the applicant's profile and A3b follows the supported person's.

**Removed, "The other columns we don't need":** the provisional date text, the
exceptional-funding flag, the exceptional-funding detail, the care example, the other-care type,
the score breakdown text and the income flag. "Provider preference" was removed earlier in this
item. None is shown, and none is requested any more. The "Further details (not in the Trustee
Pack)" section is gone.

## Gaps: rows the portal cannot fill

**Secured columns (3): F1, F2, F3.** Each is a secured column in `REV_TrusteeRestricted`, which no
trustee is a member of. Each renders in its Pack position as "Restricted — this field is protected
by column-level security and is not requested by this app." This is deliberate (ADR-032; the
earlier board-pack comparison recorded benefit status as "never shown to trustees"). No security
was changed.

**F5 needs one live schema run before deployment.** The new twin `rev_carecostsexplanationredacted`
is in `Entity.xml`, but this project creates columns through `ensure-schema.ps1`, not through
solution import (C-TECH-050). Until that run has created the column in an environment, the
portal's read of the whole case fails there, not only F5. The run therefore comes **before** the
code-app push (Dev Summary, REVIEWER ACTION REQUIRED). Like every twin, it stays empty until the
narrative-scrubbing automation (#5, deferred) is extended to write it.

**Start/End Date (S4, S5, D3, D4) are filled by hand for now.** Reviewer 2026-09-30: "Don't show
the dates. The grant admin can fill the dates manually now, while we wait for the form to have the
start and end dates." The applicant's typed date text is no longer shown. The rows read
`rev_breakstart` / `rev_breakend`, and **Break Start** and **Break End** are on the grant admin
app's application main form and editable (`disabled="false"`). The app includes `rev_application`
with no form restriction. Checked in solution source, not live.

## Overlapping deferred items

- **WI-0010 (Start/End Date). Stays deferred** (reviewer, 2026-09-30). The detail screen shows
  Start Date and End Date in the Pack's positions; the grant admin fills them by hand until the
  form captures two dates. The applications **list** screen still says "Preferred dates"; it is
  outside this item's scope.
- **WI-0008 (wellbeing Q&A).** Placement is done: the answers are in Current Circumstances, after
  About Applicant, with only the score in the Summary. This pass also renders the **actual
  questions and answers** (C2–C12) straight from the answer columns, not from the scoring flow's
  breakdown text. WI-0008 was deferred because it waited on that breakdown text, so it may now be
  closeable without the scoring-flow change. **Reviewer, 2026-09-30: "Yes WI-0008 can be closed
  after this is build."** It moves to `built` in this pass on the C2–C12 source lines.
