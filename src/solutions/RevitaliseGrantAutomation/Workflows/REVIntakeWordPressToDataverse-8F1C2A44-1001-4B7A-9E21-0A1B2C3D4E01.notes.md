# REVIntakeWordPressToDataverse-8F1C2A44-1001-4B7A-9E21-0A1B2C3D4E01.json - full action/trigger descriptions

Power Automate enforces a hard limit (256 characters) on the `description` field of every action, trigger, parameter and schema property - exceeding it blocks the flow from being saved in the designer at all. The condensed descriptions actually shipped in this file keep the essential fact and citation; the full reasoning that used to live there is preserved here, keyed by the same JSON path, so none of the domain detail this project treats as load-bearing documentation is lost.

## `/properties/definition/description`

REV | Intake | WordPress to Dataverse. Serves FR-007 (create the application record automatically), FR-008 (unique reference REV-YYYY-NNN plus submission timestamp), FR-009 (Teams notification carrying applicant name and reference), FR-010 (record the failure and alert, so no submission is silently lost), and - since TAD rev 11 - FR-083 to FR-093 (SDD Amendment A-08): the website's NATIVE Gravity Forms entry payload is accepted as sent and translated inside the flow (ADR-051), every applicant-entered answer is stored and nothing the form or plugin generates is (ADR-051 item 12). Also derives rev_agerange (from the age band the form asks) and rev_locationarea / local authority / city from the postcode at write time (FR-027). NOT IN THIS RELEASE: the FR-023 duplicate-grant check call. REV | Duplicate | QBO Check is Automation #7 and is deferred (Dev Summary section 7); the call site is marked below so it is added rather than rediscovered. IDEMPOTENCY: rev_sourcesubmissionid (= the entry `id`) is an alternate key and is checked before any write, so a replayed or retried webhook cannot create a second application (TAD section 5.1). The full design record for the rev 11 rework is the section "TAD rev 11 - the website's native entry payload" at the end of this file.

## `/properties/definition/parameters/rev_IntakeAllowedClientId/metadata/description`

Environment variable. The application (client) ID of the rev-wordpress-intake registration. The website sends this value as the fixed header x-rev-client-id on every webhook call, and the first action compares the two. TAD rev 14 (ADR-011, 2026-10-02): this is the SECOND control (NFR-008, C-TECH-006); the FIRST is the signed callback URL described on the trigger below. A client ID is a public identifier, not a secret, so a plain environment variable is correct - and the header therefore stops only a caller who has the URL but has not seen the website's webhook configuration. The registration is kept only as the source of this value; its client secret is no longer used by anything and is to be revoked by the reviewer/Wanstor. SUPERSEDED (rev 10 wording, retained): "the PRIMARY control is the trigger's Entra ID authentication parameter ... the trigger's Allowed users field takes the SERVICE PRINCIPAL OBJECT ID of the same registration."

## `/properties/definition/triggers/manual/description`

The one public endpoint in the solution. TAD rev 14 (ADR-011 re-decided 2026-10-02): THE TRIGGER MODE IS ANYONE, DECLARED IN THIS DEFINITION as inputs.triggerAuthenticationType = "All". That is the value the platform's own designer wrote into the live DEV definition when the reviewer chose 'Anyone' (read from REV-GrantApplications-DEV workflow.clientdata, 2026-10-02, first key of the trigger's inputs). The rev 2-era claim that Microsoft publishes no workflow-definition property for this setting is refuted by that read. Declaring it here makes every import reproduce the setting instead of relying on a platform default. Whether an import actually honours the declared value is A-INT-11, closed by the next DEV import followed by verify-live-flow-definitions.py --env dev and a read-only look at 'Who can trigger the flow?' in the designer (look, never save). FIRST CONTROL: the signed callback URL. A caller must present the URL with its sig query value, a signature the platform issues and checks; a missing or wrong sig is rejected by the platform before this definition runs (A-INT-12, measured by provisioning/entra/verify-intake-endpoint-auth.ps1). The URL is therefore a credential: held only as a CI secret (INTAKE_ENDPOINT_URL_TEST / _PRD), never printed or logged, and compared by SHA-256 hash before and after every import (ADR-011 intervention 4, A-INT-13). SECOND CONTROL: the x-rev-client-id header check, the first action below. WHY THE ROUTE CHANGED: Gravity Forms webhook headers are static values, so the Entra bearer token the rev 10 route depended on (it expires within the hour) could not be refreshed. The authorization header is still deliberately NOT surfaced into trigger outputs - there is no IncludeAuthorizationHeadersInOutputs on this trigger.

ADR-011 IS RE-DECIDED (TAD rev 14, 2026-10-02): the signed callback URL (trigger mode Anyone) plus the x-rev-client-id header check. Basis, the reviewer's statement: "I changed the trigger to anyone to receive a url with sig value. I added the client ID in the header of the webook so that the conditional step still works. So the trigger needs to stay as it is right now." The reviewer accepted the lower assurance: the caller is now identified by possession of the URL and the header value, not by an Entra identity (NFR-008 trace, TAD section 7). What the decision does NOT establish: that the website has posted to this URL since the change and been accepted - no V-level is claimed for the route until one website submission and the two rejection probes have run (V5). SUPERSEDED (rev 10, retained): "ADR-011 IS DECIDED (TAD rev 10, 2026-09-25): the Entra client-credentials route". Under rev 10 'Anyone' was recorded as a defect; under rev 14 it is the decided mode.

RUN HISTORY IS SECURED (ADR-051 item 7, A-INT-01): runtimeConfiguration.secureData.properties = ["outputs"] on this trigger, so the body - every answer, including special-category ones, plus the ip and user_agent the website still sends - is hidden in run history. Before rev 11 nothing in this flow was secured and every answer was readable for 28 days by anyone with access to the flow.

CONCURRENCY IS CAPPED AT 1 ON PURPOSE: the applicant match-or-create step below is read-then-write, so two simultaneous submissions from the same person could otherwise create two applicant rows. At around 200 applications a year serialising costs nothing.

THE PAYLOAD IS THE WEBSITE'S NATIVE ENTRY (ADR-051, TAD rev 9-11). The schema declares the website's own keys (TAD Appendix C C.1) for documentation and designer tokens only; schema validation stays OFF, deliberately, because with it on one unexpected type would reject the whole submission (ADR-024). `required` names id, name_first, name_last and address_postcode - the same four facts the old contract required under submission_id, first_name, last_name and postcode. The old hand-designed contract (submission_id, first_name, wellbeing_answer_1 as an option value 1-6, and so on) is gone: no sender ever sent it. Its history - the full_name split, the revision 0.3 removal of the referee and emergency-contact fields (collected on a separate post-approval form, Automation #3), the wellbeing_answer_11 off-by-one - is in git history of this file and in the Dev Summary; none of those fields reappears in the native payload either.

## `/properties/definition/triggers/manual/inputs/schema/properties/*` - the old contract's per-field notes (SUPERSEDED 2026-09-27, TAD rev 11)

Eleven sections stood here, one per scored answer (wellbeing_answer_1..10 and feeling_scale_answer), each describing an OPTION VALUE the sender was asked to send. The native payload sends LABELS instead ("Rarely", "Strongly agree") and the schema no longer declares those properties. What those notes established still holds and moved:

- The seven two-week items resolve through LikertResponseLabelMap to rev_likertresponse (1 None of the time .. 5 All of the time, 6 Not sure - 'Not sure' is a real answer worth 0.5 points in scoring, revision 0.8). The three last-year items resolve through AgreementResponseLabelMap to rev_agreementresponse (1 Strongly Disagree .. 5 Strongly Agree, 6 Not sure). Both maps are rev_setting rows (TAD Appendix C C.4); the option values - and therefore scoring - are unchanged.
- The life-satisfaction answer is still a WHOLE NUMBER 0 TO 10, never inverted or rescaled here (the inversion lives in the scoring flow's FeelingScaleInversion). The website sends it as a numeric string ("5"); Normalise_payload applies the INT rule: isInt and 0 <= x <= 10, otherwise null plus a note. The form allows decimals, so "7.5" becomes null plus a note and scoring is withheld (FR-022).
- A missing scored answer still withholds scoring rather than rejecting the application.

## `/properties/definition/actions/Reject_caller_that_is_not_the_charity_website/description`

NFR-008 and C-TECH-006, SECOND CONTROL. TAD rev 14 (ADR-011): the first control is the signed callback URL - a request that reaches this action has already presented a valid sig, because the platform rejects a missing or wrong one before the definition runs. This check compares the x-rev-client-id header with rev_IntakeAllowedClientId before any Dataverse write. TRUE means reject: the allowed id is unset, or the header does not equal it - so an absent header is refused under every configuration and the action fails closed. The TRUE branch responds 401 {"error":"unauthorised"} and then Terminates Cancelled, not Failed, so a scanner never pages the process owner. The header value is a public identifier, so on its own this check stops only a caller who holds the URL without having seen the website's webhook configuration; the URL is the real credential (TAD risk A-R71). The rejection is deliberately terse - it tells an unauthorised caller nothing about the schema, the tenant or the tables. SUPERSEDED (rev 10, retained): "a request that reaches this action has ALREADY had its bearer token validated by the platform".

THE BRANCHES, STATED ONCE AND TESTED BY EVALUATION (corrected 2026-09-27, Test Report D-01, P1). The condition is TRUE when the caller must be REFUSED: `or( empty(trim(coalesce(rev_IntakeAllowedClientId, ''))), not(equals(coalesce(header x-rev-client-id, ''), rev_IntakeAllowedClientId)) )`. The TRUE branch holds `Respond_401_unauthorised` then `Stop_run_unauthorised` (Terminate, Cancelled); the else branch is empty, so an admitted caller falls through to `Normalise_payload`, whose runAfter waits on this action Succeeding. Until this correction the two actions sat in the ELSE branch under the `not(equals(...))` condition alone: the website, sending the RIGHT id, was refused 401, and any caller sending a wrong or no id was admitted. It was in source from the flow's first commit and live in DEV; the Pester assertions of the time read the rejection out of `.else.actions` and so asserted the defect (IMP-0926). They are replaced by cases that evaluate this condition against a matching, a wrong, an empty and an absent header and follow the branch the result selects (src/tests/solutions/IntakeContract.Tests.ps1, 'D-01').

THE FIRST OPERAND IS NEW WITH THE CORRECTION, AND IT IS WHAT MAKES 'fails closed' TRUE. The parameter's defaultValue is "". Without the empty-id test, an environment where rev_IntakeAllowedClientId was never set would compare '' with '' for a caller sending no header, and ADMIT it. With it, an unset or blank allowed id refuses every caller. That is the intended failure mode: a missing configuration value must cost availability (a 401 the smoke test and Alex both see), never the barrier.

## `/properties/definition/actions/Reject_incomplete_payload/description`

C-TECH-004 and ADR-051 item 6: validate before any write. REJECTION IS UNCHANGED IN KIND: a 400 is returned, logged (rev_errorlog via REV | Ops | Failure Alert, severity Warning) and alerted ONLY when id, name_first, name_last or address_postcode is empty after trimming - read from Normalise_payload, which applied the not-answered rule, so a key that is absent, null, "" or [] all count as empty. Nothing else rejects: a bad label, a non-numeric amount, an out-of-range life-satisfaction answer or a missing always-shown key each produce an empty column plus one sentence on rev_intakereviewnote (ADR-051 item 10). The eleven scored answers are NOT required: a submission missing one is a valid application whose SCORING is withheld and routed to a human (FR-022) - rejecting it at the boundary would lose the application entirely, which is the outcome FR-010 exists to prevent. The 400 body names the four keys under the website's own names so Alex can fix the integration.

## `/properties/definition/actions/Create_the_application/actions/Return_the_existing_reference_if_this_is_a_replay/description`

A replayed webhook returns the reference it created the first time and writes nothing. Deliberately an UPDATE-FREE path: TAD section 5.1 says a replay 'updates rather than duplicates', but by the time a replay arrives the process owner may already have overridden the status (FR-018), and silently overwriting her decision with the original payload would be worse than a no-op. The reviewer should confirm this reading - it is the one place this flow narrows the TAD (Dev Summary section 7, decision D-2).

## `/properties/definition/actions/Create_the_application/actions/Read_age_range_label_map/description` (SUPERSEDED 2026-08-21, IMP-0112)

This action no longer exists at this path. It read the map from the live form's own age-range labels to rev_agerange option values by a Get-a-row-by-id call with an alternate-key Row ID (`rev_name='AgeRangeLabelMap'`) - the shape the Dataverse connector rejects (IMP-0112). It was folded into the single `Read_configuration` scope's `ListRecords` call, and the equivalent extractor is now `Create_the_application/actions/Read_configuration/actions/Setting_AgeRangeLabelMap`, documented under the IMP-0112 fix note above. The original reasoning stands unchanged: the live application form asks an age BAND directly and does not ask for a date of birth at all, so the band it sends is the primary source for rev_agerange and the date-of-birth derivation below is only a fallback for a future form version that supplies one.

## `/properties/definition/actions/Create_the_application/actions/Compute_age_in_years/description`

Exact completed years, not a tick-division approximation: subtract the birth year, then subtract one more if the birthday has not yet occurred this year. Band boundaries matter, so an off-by-one at the end of a band would put a person in the wrong reporting group. Returns -1 when no usable date of birth was supplied, which the next step turns into 'Not known' rather than a guess.

## `/properties/definition/actions/Create_the_application/actions/Match_age_bands/description`

The AgeBandMap rows are held in ASCENDING maxAge order and this action preserves that order, so the first match is the narrowest band that contains the age. That ordering requirement is stated in the setting's own description - if someone re-orders the JSON, the derivation silently degrades, which is why it is documented at both ends.

## `/properties/definition/actions/Create_the_application/actions/Derive_age_range/description`

FR-084 and ADR-051 item 11: "not answered" is one state, and it is an EMPTY column. The order is unchanged - the band the applicant chose on the form (`Map_age_range_label`, the primary route, because the live form asks a band and not a date of birth), then the band derived from a date of birth when one was sent (`Match_age_bands`). What changed on 2026-09-27 (Test Report D-02, P3) is the last step: when neither route yields a band, the result is `null`, where it used to be the constant 9 (Not known). The constant wrote a default for a blank answer, which FR-084 forbids, and a value for an unrecognised label, which FR-077 / ADR-024 forbid; it also made "left blank" indistinguishable from "Prefer not to say", which is a real answer and is the ONLY route to 9 now (`AgeRangeLabelMap` maps that label to 9). An unrecognised label still produces a sentence on `rev_intakereviewnote` from `Derive_intake_review_note`, which fires on "a non-empty raw value was sent AND the derivation resolved to null" - so the note is now accompanied by an empty column, as for every other label-mapped field. TAD ADR-051 consequence 9 keeps this fallback "unchanged"; the SDD's FR-084, approved later the same day, forbids it, and the SDD governs (Test Report D-02). Downstream: `REV | Portal | Round statistics` counts `rev_agerange` 1..9, so an unanswered age is in no bucket - the same as an unanswered gender already is.

## `/properties/definition/actions/Create_the_application/actions/Compute_postcode_prefixes/description`

Two candidates, because UK postcode areas are one or two letters and the two-letter reading must win. 'BT1' must resolve to Northern Ireland on 'BT', not to the West Midlands on 'B'. Logic Apps has no regular expressions, so the digits are not stripped - the two-letter then one-letter fallback below achieves the same result without one.

## `/properties/definition/actions/Create_the_application/actions/Find_existing_applicant/description`

**`$select` widened 2026-09-27 (TAD rev 13, ADR-054):** besides the id and name it now reads the fifteen stored values `Refresh_existing_applicant` preserves on omission; see that action's section. Matches on email plus name when an email address was collected. The live form only asks for an email address when the applicant picks Email as their preferred contact method, so when there is no email the match falls back to name plus postcode - the only identity the form guarantees. Every value is read from Normalise_payload (already trimmed; email lower-cased) and every interpolated value is wrapped in coalesce(..., '') before replace() doubles its quotes (C-TECH-005), so the expression is total whether or not if() evaluates its untaken branch (knowledge/technology/power-automate.md, IMP-0378/IMP-0412). Inputs and outputs are secured: the filter carries a name, an email and a postcode.

## `/properties/definition/actions/Create_the_application/actions/Create_or_refresh_the_applicant/description`

One person, one applicant row. On a repeat application the derived columns and rev_lastcontactdate are refreshed rather than a second row being created - which matters because rev_lastcontactdate drives the six-month withdrawn/incomplete retention clock, and a stale value would delete a live case early.

## `/properties/definition/actions/Create_the_application/actions/Create_or_refresh_the_applicant/actions/Refresh_existing_applicant/description`

Deliberately does not rewrite rev_firstname, rev_lastname or rev_email - those three are what this applicant was MATCHED on, so rewriting them is either a no-op or, if the values differed, evidence the match was wrong. rev_privacynoticeacceptedon is not written here and, since TAD rev 11, not written anywhere (ADR-051 item 12): the form has no privacy-notice question, so the old coalesce(privacy_notice_accepted_on, utcNow()) stamped a date nobody entered. Existing rows keep their value; nothing is back-filled or cleared. rev_title, rev_applicanttype, rev_gender and rev_ethnicgroup now come from their Derive_* label-map actions (they were integers in the old contract and are labels in the native payload). ~~A column whose answer was not given is written as null (existing refresh behaviour, unchanged by this rework).~~ **Superseded 2026-09-27 by TAD rev 13 `ADR-054`** (Test Report O-1: that null erased what a returning applicant had given before).

**ADR-054, as narrowed in TAD rev 13 — preserve on omission, keyed on the SOURCE ANSWER.** Every column this action writes except `rev_lastcontactdate` now sends the stored value when this submission did not answer the question, and the new value otherwise. The stored value is read from `Find_existing_applicant`, whose `$select` was widened to exactly the fifteen columns read back here (`IntakeContract.Tests.ps1` derives that list from these expressions and fails on any column read back but not selected, because an unselected column reads as null and would silently clear what the change exists to keep).
- **Five straight-through columns** (`rev_phone`, `rev_addressline`, `rev_addressline2`, `rev_towncity`, `rev_postcode`): `coalesce(<normalised answer>, <stored>)`. The normalised answer is null exactly when ADR-051 item 11 says "not answered", so the plain coalesce is the rule. It also keeps the stored phone when a new one is refused as over-length by the structured guard (ADR-053 point 4); the note records the refusal.
- **Ten derived columns**: `if(empty(coalesce(<source answer>, '')), <stored>, <derived>)` - gated on the answer that FEEDS the derivation, never on the derivation's own output. A derivation returns null both when its input was not answered and when the input was answered but could not be resolved (an unknown label; a postcode the register cannot place). Only the first means "keep". So an unrecognised re-answered title writes null plus its note, as `Create_application` does, and a NEW postcode the register cannot resolve writes the new postcode beside the unresolved local-authority status instead of the old council. Sources: `rev_title`<-`title`, `rev_applicanttype`<-`applicant_type`, `rev_gender`<-`gender`, `rev_ethnicgroup`<-`ethnic_group`, `rev_preferredcontactmethod`<-`preferred_contact_method` (the flow normalises the contact answer into ONE key; TAD ADR-054 speaks of "three raw keys", which is the three ticked options inside that one answer - "not answered" is that key null), `rev_agerange`<-`age_range` AND `date_of_birth` (kept only when both are blank), and the four postcode-derived columns <- `postcode`. Because `postcode` is one of the four required facts, those four are in practice always re-derived; the gate is still the postcode, so the rule does not depend on that.
- **The named limitation is TAD risk A-R69**: a deliberate blank re-answer is indistinguishable from not answered, so the old value is kept.
- **The stored-value shapes are A-INT-09** (Dev Summary section 10): a choice reads back as its integer and a multi-select as its comma-separated value string, which is what this UpdateRecord writes. Every secured column read back is readable through `REV_TrusteeRestricted` (CanRead 4), the same membership that lets this flow write them.

## `/properties/definition/actions/Create_the_application/actions/Create_or_refresh_the_applicant/else/actions/Create_new_applicant/description`

rev_name is an autonumber (REV-A-nnnnn) and is NOT set here. ADR-013: the primary name column holds the pseudonymised reference, never the person's name, so the name never leaks into a lookup, a related-record pane, a search result or an audit summary. rev_fullname IS set here (and in Refresh_existing_applicant): trim(first + ' ' + last). It is a PLAIN writable nvarchar, not calculated - the calculated form was rejected by solution import on 2026-08-14 and the planned maker-portal conversion never happened; an earlier version of this note wrongly assumed it was calculated, so the column stayed empty. Refresh writes it too, so existing applicants with an empty value are backfilled on their next submission. IF the column is ever converted to calculated, REMOVE both writes: a write to a calculated column fails the create. rev_privacynoticeacceptedon is no longer written (ADR-051 item 12 - see Refresh_existing_applicant). rev_dateofbirth keeps its guarded write, but Normalise_payload emits date_of_birth as a literal null because the live form has no date-of-birth question (TAD Appendix C C.3); the column's RequiredLevel moved to None in the same change (ADR-051 item 9), and so did rev_email's, because email is collected only when Email is a chosen contact method.

WRITE SHAPE (TAD rev 14 section 5 rule, 2026-10-02): this action writes its 20 columns as flat item/<column> parameters beside entityName, never as a nested item object. The Power Automate designer binds only the flat form to the table's columns and writes back only what it bound, so a designer save of the intake flow at 08:51 UTC on 2026-10-02 emptied this action in DEV while the flat Refresh_existing_applicant kept every column. Converted key for key, expressions unchanged; no lookup bind is involved.

## `/properties/definition/actions/Create_the_application/actions/Create_application/description`

FR-007 and FR-008. rev_name is an autonumber (REV-{DATETIMEUTC:yyyy}-{SEQNUM:3}) and is therefore NOT set here - the REV-YYYY-NNN format FR-008 requires is enforced by the column, not by this flow, so it cannot drift. rev_status is set to 1 Submitted; the scoring flow moves it from there. rev_submittedon is Normalise_payload's received_at (utcNow(), evaluated once) - FR-008's submission timestamp is our receipt time, never the form's date_created (ADR-051 item 12, TAD Appendix C C.6). Every consent date (*consentdate, and rev_supportrecipientageconfirmationdate) is the same received_at, written only when its consent is true (SDD OQ-052). Multi-select choice columns take a comma-separated list of option values.

rev_costs (Total Cost) IS written by Create_application: the sum of rev_accommodationcost + rev_travelcost + rev_othercost over the components that are present, and NULL when all three are null (a blank is UNKNOWN, never zero - ADR-039, which REVPortalRoundStatistics relies on). It is a PLAIN writable money column, not calculated: the calculated form was rejected by solution import on 2026-08-14 and the conversion never happened, so an earlier assumption that it was calculated left it empty on every intake row (second instance of the IMP-1033 class). The payload's total_estimated_cost is not transferred (TAD Appendix C). IF the column is ever converted to calculated, REMOVE this write in the same change: a write to a calculated column fails the create. There is no application refresh path, so Create_application is the only writer. No backfill of existing rows (reviewer decision 2026-10-03).

THE TRANSFER RULE (ADR-051 item 12, the reviewer's words): "Keep all data that is actively requested from the user ... Only transfer what is actually filled in by the user of the form." So every applicant-entered answer in TAD Appendix C C.1 is written, including seven columns that are new in this change (rev_someonehelping, rev_hasequalityactdisability, rev_disabilityimpactdescription, rev_supportrecipienthasequalityactdisability, rev_supportrecipientdisabilityimpactdescription, rev_provisionaldate, rev_otherfundingstatus), and the first writes ever to rev_careprovidedtype, rev_othercareprovidedtype, rev_careprovidedexample, rev_hearaboutus and rev_otherhearaboutus. Nothing the form or plugin generates is written (C.6). rev_receivingotherfunding is still written (Yes -> true, No -> false, awaiting a decision -> null) beside the new three-way rev_otherfundingstatus.

NO LONGER WRITTEN, because the native payload cannot supply them (TAD Appendix C C.3): rev_supportrecipientname (never asked, spec M-10), rev_breakstart / rev_breakend (only the free-text provisional_date exists, now stored in rev_provisionaldate), rev_providerpreference (no such question). The two redacted counterparts rev_disabilityimpactdescriptionredacted and rev_supportrecipientdisabilityimpactdescriptionredacted (ADR-052) are NEVER written by intake - Automation #5 fills them once extended. The form-calculated total_estimated_cost is not transferred; rev_costs is instead computed by the flow from the three components (see the Create_application note above).

WRITE SHAPE - FLAT (TAD rev 14 section 5 rule; A-INT-15 closed 2026-10-02): all 81 columns are flat item/<column> keys, including the one lookup bind item/rev_applicantid@odata.bind. The key is the one the designer itself wrote in the reviewer's throwaway DEV flow TEST_Binding (workflow d630108d-52be-f111-aaae-7ced8d43e87d, read-only pac env fetch of clientdata): {"entityName": "rev_applications", "item/rev_applicantid@odata.bind": "/rev_applicants('00000000-0000-0000-0000-000000000001')"}. The designer quotes the GUID; this source keeps the unquoted /rev_applicants(<guid>) from @concat, which is valid OData key syntax and ran successfully on 2026-09-29. A designer save no longer empties this action.

SECURED COLUMNS WRITTEN HERE - the list is exhaustive and asserted by IntakeContract.Tests.ps1: rev_intakereviewnote, rev_helpername, rev_helperemail, rev_helperphone, rev_helperorganisation, rev_helperrelationship, rev_consentexplanation, rev_otherconditionraw, rev_disabilityimpactdescription, rev_caresupportdescription, rev_supportrecipientotherconditionraw, rev_supportrecipientdisabilityimpactdescription, rev_othercareprovidedtype, rev_careprovidedexample, rev_receivesbenefits, rev_benefitprovider, rev_employmentstatus, rev_carecostsexplanation, rev_unabletofundexplanation, rev_otherexceptionalcircumstance, rev_exceptionalfundingdetail, rev_narrativeraw and rev_groupmembernames. The service identity can write these only because REV Service Accounts is a member of REV_TrusteeRestricted, which grants cancreate on every one - a secured column missing from that profile fails this create with a permission error (FR-031, NFR-001). The two Equality Act answers are deliberately UNSECURED (ADR-052: released to trustees, secured: exception register rows). Inputs and outputs are secured in run history (ADR-051 item 7).

## `/properties/definition/actions/Create_the_application/actions/DEFERRED_call_duplicate_grant_check/description`

CALL SITE PLACEHOLDER, NOT DEAD CODE. FR-023 requires the QuickBooks duplicate-grant check to run when the application record is created, and this is the point at which it runs. REV | Duplicate | QBO Check is Automation #7 and is deferred out of this release (Dev Summary section 7), together with the QuickBooks connection reference, its DLP business-group entry and the rev_duplicateflag column family. This Compose exists so the insertion point is unambiguous when Automation #7 is built; it writes nothing and costs one action. Remove it in the same change that adds the child-flow call.

## `/properties/definition/actions/Create_the_application/actions/Notify_process_owner_of_new_application/description`

FR-009 requires the applicant NAME and the reference, so unlike every other notification in this solution this message deliberately carries personal data. ADR-015 is the control: it goes to the process owner's 1:1 chat as the Flow bot, so it reaches one named recipient rather than every member of a channel. No narrative, no condition data, no contact details, no date of birth.

## `/properties/definition/actions/Create_the_application/actions/Respond_201_created/description`

Responds success even if the Teams notification failed, on purpose: the application record exists, so the applicant's submission succeeded, and returning an error would make Alex's site retry and tell the applicant something went wrong when nothing did. A failed notification is caught by the scope's failure branch and logged instead.

## `/properties/definition/actions/Alert_on_failure/description`

FR-010: no submission is silently lost. Passes the entry id (Normalise_payload's submission_id) as the record reference so the failed submission can be identified and re-sent - and passes nothing else from the payload, because the payload contains special-category data (NFR-012, C-DOM-004). The entry id is the one generated value this flow keeps (ADR-051 item 12), and it is not personal data, which is why this action, Log_incomplete_payload and the replay guard are the only consumers of Normalise_payload left unsecured.

## `/properties/definition/actions/Respond_500_intake_failed/description`

Tells Alex's site to retry with the SAME entry id - which is safe because of the idempotency guard at the top of the scope. Returns no diagnostic detail: the applicant must never see a raw technical error, and the endpoint must not describe its internals to an unauthenticated observer.

## Form-field-corrections pass, 2026-08-17 — FR-064 label-map derivations

Three new label-map chains were added between `Derive_location_area` and `Find_existing_applicant`, one per Choice column this pass reshapes: `Read_exceptional_circumstance_label_map` / `Map_exceptional_circumstance_label` / `Derive_exceptional_circumstance`; the same three-action shape for `employment_status` and `care_hours_per_week`. All three follow `Read_age_range_label_map`'s existing pattern exactly - a `rev_setting` row read by alternate key, a `Query` action matching the sent label against the map, a `Compose` action resolving to the matched option or `null`. `null`, not a guessed value, is the FR-064 behaviour: an unmatched label leaves the column empty rather than picking a nearest option.

**Normalisation goes further than `Read_age_range_label_map` needed.** Age-range labels ("18-24") never varied by dash character. The care-hours bands do - this session's own D-4 correction was triggered by exactly that: "10 – 19 hours" (en-dash) and "10 - 19 hours" (hyphen) describing the same band from different sources. `Map_exceptional_circumstance_label` and `Map_care_hours_band_label` therefore normalise both the incoming value and the map's own label through `replace(replace(x, '–', '-'), '—', '-')` before the case-insensitive, trimmed comparison. `Map_employment_status_label` only needed trim/case-fold - none of its five labels contain a dash.

**Scope of the normalisation is deliberately narrower than the SDD's stated rule (FR-064).** The SDD also calls for collapsing internal runs of whitespace. WDL has no direct string-collapse function short of a `split`/`join` round trip that does not actually collapse repeated separators, and the practical risk is low for server-generated form values, so this was not built. Disclosed here rather than silently dropped or built fragile.

## Form-field-corrections pass, 2026-08-17 — `preferred_contact_method` (array field)

Deliberately NOT built on the same label-map pattern as the three fields above. A per-item Setting-map lookup inside a `Select` action's mapping expression would need a nested `filter()`/`item()` call whose scoping this session had no live environment to verify - exactly the kind of guess `skills/how-to-verify-a-platform-contract.md` says to avoid rather than commit unverified (C-TECH-052). Since Email/Phone/Post are three fixed, structural values with no realistic wording drift, `Normalise_contact_method_labels` (a `Select` doing only `toLower(trim(item()))` - a single, unambiguous `item()` scope) feeds three plain `contains()` checks in `Derive_preferred_contact_method`, unioned and joined into the comma-separated option-value list `rev_preferredcontactmethod` expects. Trade-off recorded in the Dev Summary: less config-driven than the other three fields, but built from functions already proven elsewhere in this exact flow rather than a new, unverified shape.

## Form-field-corrections pass, 2026-08-17 — `Derive_intake_review_note` and `rev_intakereviewnote`

FR-064 requires a mismatched label to be recorded, not just silently dropped. `Derive_intake_review_note` checks the three label-map fields only (not `preferred_contact_method`, which cannot mismatch - any label not Email/Phone/Post simply contributes nothing to the union): for each, if a non-empty raw value was sent AND its `Derive_*` action resolved to `null`, a sentence naming the field and the raw value is appended. Built from `if`/`concat`/`and`/`not`/`empty`/`equals`/`trim` only - every one already used elsewhere in this exact flow (e.g. `Reject_incomplete_payload`, `Derive_age_range`) - rather than the inline `filter()` function, for the same C-TECH-052 reason as the contact-method note above. Written to the new secured column `rev_intakereviewnote` on every run, including when empty (an empty string overwrite is harmless and keeps the mapping simple).

## Form-field-corrections pass, 2026-08-17 — removals from `Create_application`

`rev_travellingwithcarer`, `rev_carername` and `rev_carersupport` are removed from the item map along with their trigger-schema properties and their columns (FR-063, SDD D-5): the live form has never asked these three questions, so the mappings were always dead code writing `null`/`false` to columns nothing populated. `rev_carehoursperweek` gains a real mapping for the first time - it existed as a schema column since 2026-08-16 but nothing in this flow wrote to it until this pass.

## IMP-0112 fix, 2026-08-21 — the six label/band maps move into one `Read_configuration` scope

`/properties/definition/actions/Create_the_application/actions/Read_configuration/description`

Every label/band map this flow reads - AgeBandMap, PostcodeRegionMap, AgeRangeLabelMap, ExceptionalCircumstanceLabelMap, EmploymentStatusLabelMap, CareHoursBandLabelMap - used to be read by six separate Get-a-row-by-id actions, each with an alternate-key expression (`rev_name='...'`) in the Row ID field. The Web API accepts that shape and the alternate key itself reports Active, so it looked verified; the CONNECTOR rejects it outright. This is the identical defect `REVScoringCalculateAndFlag` had: it failed on its first action on all eleven runs of its first live test before being fixed the same way (`ScoringInvariants.Tests.ps1`'s 'FR-017 / NFR-019' Describe block). Fixed here by the same recipe: one `ListRecords` call filtered on all six names at once (`Read_intake_configuration`), a row-count guard (`Fail_if_a_setting_row_is_missing`), and one `Query` extractor per key (`Setting_<Key>`) that every downstream consumer reads via `first(body('Setting_<Key>'))?['rev_value']` instead of `outputs('Read_<Key>_map')?['body/rev_value']`. The whole group sits inside its own `Read_configuration` Scope, matching the scoring flow's shape exactly, so `Describe_the_failure` below needed the same nested-scope descent that flow already has (IMP-0109) — without it, a failure inside this scope would report only the generic wrapper message, not the action that actually failed.

`/properties/definition/actions/Create_the_application/actions/Read_configuration/actions/Read_intake_configuration/description`

FR-017 (no threshold/map is a literal in the definition), FR-027 (age range and location area derivation) and FR-064 (label-map derivation with an audit trail on mismatch) all depend on these six rows. One `ListRecords` call against `rev_settings` with `$filter` naming all six `rev_name` values, `$select` limited to `rev_name,rev_value`, replaces what were six chained `GetItem` calls each carrying `recordId: "rev_name='<Key>'"` - the shape `scripts/verify-flow-definition-language.py` now rejects on every build (C-TECH-052).

`/properties/definition/actions/Create_the_application/actions/Read_configuration/actions/Fail_if_a_setting_row_is_missing/description`

Get-a-row-by-id 404ed on a missing row, which is unambiguous. List rows returns a short array instead: `first()` on it yields `null`, and every downstream `Derive_*` (age range, location area, exceptional circumstance, employment status, care-hours band) would silently produce a plausible-looking wrong value instead of failing. This guard requires the read to return exactly 6 rows before any `Setting_<Key>` extractor runs, and terminates the run as `Failed` (not `Cancelled`) so `REV | Ops | Failure Alert` records it - the same reasoning as the scoring flow's own `Fail_if_a_setting_row_is_missing`.

`/properties/definition/actions/Describe_the_failure/description`

Before this fix, `Create_the_application` had no nested scope of its own, only flat actions, so `Describe_the_failure` could safely treat `first(body('Find_the_failed_action'))` as the leaf action. Now that `Read_configuration` is itself a nested `Scope`, a failure inside it makes `result('Create_the_application')`'s failed child the SCOPE, not the leaf - and `result()` on a scope returns a generic wrapper message ("An action failed. No dependent actions succeeded.") rather than the real error (IMP-0109, already documented as the reason `REVScoringCalculateAndFlag`'s own `Describe_the_failure` is an `If`, not a plain `Scope`). This action is now the same shape as that one: when the failed child's name is `Read_configuration`, it descends one level via `result('Read_configuration')` to find the actual failed leaf and builds `failureDetail` from that; otherwise the outer failed child IS the leaf, exactly as before.

## EF-35, 2026-09-22 — `support_recipient_age_confirmation` / `..._date` accepted ahead of the form

Emily's plan item EF-35 asks for a carer's confirmation that the person they support is 18 or
over, mirroring the applicant's own age-confirmation declaration. The upstream WordPress form
does not ask this question yet - it is Alex's to add - but the reviewer's instruction (2026-09-17)
was to build the Revitalise-side data model now rather than wait, so nothing further is needed
from this project the day the form ships.

Two new trigger-schema properties, `support_recipient_age_confirmation` (boolean) and
`support_recipient_age_confirmation_date` (string), sit next to the existing
`age_confirmation_consent` pair and bind to two new columns on `rev_application`,
`rev_supportrecipientageconfirmation` and `rev_supportrecipientageconfirmationdate`, following
that exact pair's shape (bit + UserLocal datetime, no default value). This is the same
`Create_application` item map the removals above changed - no new action, no new scope, one more
line in an existing mapping block.

**This is a known and dated gap, not a guess.** `support_recipient_age_confirmation` is accepted
by this flow and will not be sent by the live form until Alex ships the question - exactly the
shape the form-validation spec's M-10 exists to record ("accepted by the intake, never sent by
the live form"), and it is recorded there as of 2026-09-22 with Alex named as the owner who closes
it, following the precedent `IMP-0744` set for how this project notes that kind of gap rather than
leaving it implicit. Nothing breaks in the meantime: the property is simply absent from every
payload until then, and the mapped column stays null, distinguishable from a false confirmation
because the column carries no default value.

**Update 2026-09-27 (TAD rev 11).** The native payload has no key for this question yet (TAD Appendix C C.3: *"Keep both internal names and map them when the key appears. Its key name is unknown until then."*). So the internal name `support_recipient_age_confirmation` survives in `Normalise_payload`, emitted as a literal null rather than read from a guessed key, and its date is `received_at` when it is true. When Alex ships EF-35 and the key name is known, mapping it is a one-line change in `Normalise_payload` (BOOL rule) plus one row in TAD Appendix C.

## `/properties/definition/actions/Create_the_application/actions/Find_local_authority_register_row/description`

wbs:0.11 (CO-003), TAD `grant-admin-app-architecture.md` S5. ListRows against the sibling wbs:4.6
register (`rev_localauthorityregister`), filtered on its alternate key `rev_name` = the outward
code already computed by `Compute_outward_code` above - the identical value `rev_locationarea`'s
own derivation already reads, so no second postcode-parsing logic is introduced. NEVER
Get-a-row-by-id on an alternate key (IMP-0112, confirmed live on this connector) - `ListRecords` +
`$filter` only, the same shape `Find_existing_applicant` above already uses.

**A-GAA-01 (Dev Summary §10): the register's entity set name is guessed.** `rev_localauthorityregister`
does not exist in source yet - `wbs:4.6` is a parallel, separately-evidenced dispatch building it
at the same time as this one, and this dispatch was explicitly told not to touch it. There is
therefore no real environment or exported customization to ground-truth the plural entity-set name
against. `rev_localauthorityregisters` (English regular pluralisation, matching every other entity
in this solution - `rev_applicant` -> `rev_applicants`, `rev_grant` -> `rev_grants`) is the guess
recorded here and in Dev Summary §10. If wrong, the fix is a one-line `entityName` change in this
action, and the failure mode is loud (a live 404/`EntityNotFound` on first run against a seeded
environment), not silent.

**Runs whether or not the register is yet seeded** (TAD S5, S9): zero rows found here is handled
identically to a genuine miss by `Derive_local_authority_status` below - not a flow error, and not
distinguishable from "register not seeded yet" from this flow's point of view. That is deliberate;
see the TAD's own sequencing note (S8/S9) on why this is still not the recommended deploy order.

## `/properties/definition/actions/Create_the_application/actions/Derive_local_authority_status/description`

**A-GAA-02 (Dev Summary §10): the register's own `rev_resolutionstatus` numeric option values are
guessed.** This expression's branches compare against `100001`/`100002`/`100003` on the REGISTER's
own `rev_localauthorityresolutionstatus` option set (wbs:4.6, `postcode-lookup-architecture.md` §3),
which — like the register table itself — does not exist in source or any environment yet. The
numbers are taken directly from that sibling TAD's own stated design, not independently verified
against a built option set. If wrong, the failure mode is a silent MIS-MAPPING (e.g. a `Resolved`
register row read as `Not Known`), not a loud error — this is why it is tracked here rather than
assumed safe merely because the two TADs agree with each other on paper.

TAD S5's decision table, and TAD S3's collapsing rule. No register row found, or a row found with
the REGISTER's own `rev_resolutionstatus = NI Pending Licence` (100003 on the register's
`rev_localauthorityresolutionstatus` option set - a DIFFERENT option set from this column's own
`rev_localauthoritystatus`), both collapse to this column's `Not Known` (100003) - the register's
internal reason for a miss is never surfaced here, only the fact that it is unresolved (TAD ADR-002).
A row found with `Multi-Authority` (100002 on the register's own option set) maps straight through
to this column's `Multi-Authority` (100002). `Resolved` (100001) maps straight through to `Resolved`
(100001). The three numeric values happen to coincide across both option sets for `Resolved` and
`Multi-Authority` (both TADs assigned them the same numbers) - this expression does NOT rely on
that coincidence for `NI Pending Licence`, which maps to a *different* number (register 100003 ->
this column also 100003, but via an explicit branch, not because the two option sets are the same
option set. They are not; see S3 of the TAD and this option set's own file header for why a shared
option set was rejected).

## `/properties/definition/actions/Create_the_application/actions/Derive_local_authority/description`

FR-252/FR-253: `rev_localauthority` is null on every non-`Resolved` status (`Multi-Authority`,
`Not Known`, and the pre-processing blank state before this flow ever runs). The register row's
own `rev_localauthorityname` is copied across only when `Derive_local_authority_status` resolved
to 100001 (`Resolved`) - never for a null/ambiguous/ambiguous-miss case, so a blank
`rev_localauthority` is always traceable to one of those three honest states, never a guess.

## `/properties/definition/actions/Create_the_application/actions/Lookup_city_register/description`

wbs:4.7 (CO-007, EF-03), TAD `city-derivation-architecture.md` S5.2. `ListRecords` against the new
`rev_citysettlementregister` table (built in this SAME dispatch, unlike the sibling
`rev_localauthorityregister` above which is a parallel dispatch's own table), filtered on its
alternate key `rev_name` = the same outward code `Compute_outward_code` already derived, so the
intake lookup never re-derives outward-code logic a second way. NEVER Get-a-row-by-id on an
alternate key (IMP-0112) - `ListRecords` + `$filter` only, the same shape
`Find_local_authority_register_row`/`Find_existing_applicant` above already use.

**A-CSR-01 (Dev Summary §10): the register's entity set name is guessed**, per the same class of
guess `Entities/rev_citysettlementregister/Entity.xml`'s own header already flags — Dataverse
assigns the entity set name and no environment exists yet to read it back from. Unlike the sibling
register's A-GAA-01, the TABLE itself is not in question here (it exists in source, in this same
dispatch); only the platform's own pluralisation of it (`rev_citysettlementregisters`, English
regular pluralisation matching every other entity in this solution) is unverified. If wrong, the
failure mode is loud (a live 404/`EntityNotFound` on first run against a seeded environment), not
silent — cheapest verification per the Entity.xml header: `EntityDefinitions(LogicalName=
'rev_citysettlementregister')?$select=EntitySetName` after the first DEV prerequisite run.

Inserted immediately after `Derive_location_area` (TAD S5.2's stated sequencing point), NOT after
`Find_local_authority_register_row`/`Derive_local_authority` above - the two registers are
independent siblings (SDD §3/§8) and neither's lookup depends on the other's outcome; the ordering
in this flow is incidental (both happen to sit between `Compute_outward_code` and the label-map
`Query` actions) rather than a dependency.

## `/properties/definition/actions/Create_the_application/actions/Derive_city/description`

TAD S5.2. `@if(greater(length(...), 0), first(...)?['rev_cityname'], null)` - never guesses; a miss
(zero rows from `Lookup_city_register`) resolves to `null`, exactly as `Derive_location_area`'s own
established house style never guesses a region and `Derive_local_authority`'s own null-on-non-
Resolved rule above never guesses an authority. Unlike `Derive_local_authority_status`, there is no
intermediate status value to compute first (ADR-002: this register carries no resolution-status
column) - a miss is read directly off `Lookup_city_register`'s own row count.

`Derive_intake_review_note` (below) reads this action's output directly for its fourth `concat()`
clause (ADR-004) and `Create_or_refresh_the_applicant` reads it for `rev_derivedcity` - both gained
a `Derive_city` dependency in their `runAfter`/expression in this same dispatch.

## TAD rev 11 — the website's native entry payload (ADR-051, ADR-052, Appendix C), 2026-09-27

`wbs:4.2` (the field map is TAD Appendix C) and `wbs:4.3` (this flow). Contracted rework, not a
change order (reviewer, 2026-09-25: *"Yes the rework falls in those tasks"*). The source of truth
for every key, internal name, column and rule below is TAD Appendix C; this section records how the
flow implements it and where the implementation had to choose.

### Why the flow changed at all

The trigger schema used to be a contract of our own, derived from the charity's Excel export before
any sender existed. The first real payload (`docs/Import/2026-09-25-website-intake-payload-sample.json`,
a Gravity Forms entry object) matches none of it: keys are generated from question wording, answers
are display labels, numbers are strings, multi-selects are arrays of labels, hidden questions arrive
as `""`, `[]` or `false`, there is no date of birth, and `first_name`, `last_name`, `postcode` and
`submission_id` are all absent - so every real submission would have been rejected with a 400. The
reviewer's instruction was that the flow accepts **this** payload.

### The shape: one normalise step, then the existing flow

- **`Normalise_payload`** (a Compose, immediately after the caller gate, outside the scope because
  the 400 check reads it) is **the only action that reads an answer key from `triggerBody()`**. It
  emits an object under the flow's internal names (`first_name`, `postcode`, `receives_benefits`,
  ...), so every downstream expression is `outputs('Normalise_payload')?['x']`. A wording change on
  the website is a one-property edit here. `IntakeContract.Tests.ps1` asserts that no other action
  reads an answer key from the body.
- The only other `triggerBody()` reader is `Find_missing_payload_keys`, which tests key
  **existence** (`contains(triggerBody(), item())`, `A-INT-04`) and never reads a value.
- **Not answered is one state** (ADR-051 item 11): an absent key, `null`, `""` after trimming, `[]`
  and - for anything that is not a shown consent - `false` all produce null, so the column is not
  written. It does not matter which of these Alex settles on for unseen questions.

### The type rules (TAD Appendix C C.2), as built

| Rule | Expression shape | Note on failure |
|---|---|---|
| TEXT | `trim(string(coalesce(x,'')))`; not-answered -> null | - |
| EMAIL | TEXT, lower-cased (the existing behaviour) | - |
| BOOL | the JSON boolean as sent, else null | yes, if a non-boolean value arrived |
| GATED | the boolean only when `is_someone_helping_you_complete_this_application` is "Yes", else null | yes, as BOOL |
| YESNO | "Yes"/"No" (case-insensitive) -> true/false, else null | yes, naming the value |
| MONEY | strip `£` and spaces, then `isFloat(x,'en-GB')` -> `float(x,'en-GB')` | yes, naming the value |
| INT | `isInt(x)` and 0 <= x <= 10 -> `int(x)` (life satisfaction only) | yes, naming the value |
| JOIN | the three helper-name parts (prefix, first, last), in order, skipping empties, into `rev_helpername`. Middle name and suffix are no longer read (reviewer instruction 2026-10-05, wbs:4.2/4.3); the trigger schema no longer declares `helpers_name_middle` or `helpers_name_suffix`, and the website may still send them empty | - |
| MULTI | the array as sent; a lone string is wrapped into a one-item array | per unmatched label |

**Every expression is total under both readings of `if()`.** This repository records both "if()
evaluates only the branch it takes" (`IMP-0124`) and "evaluates all three arguments" (`IMP-0378`),
unresolved (`knowledge/technology/power-automate.md`). So nothing that throws is ever reachable on an
untaken branch: `float()` and `int()` are fed `if(isFloat(x), x, '0')` / `if(isInt(x), x, '-1')`,
`trim()` and `toLower()` only ever see `string(coalesce(x,''))`, and `formatDateTime()` in the
date-of-birth fallback only ever sees `coalesce(dob, '2000-01-01')`. `A-INT-03` is the open
assumption that `isFloat`/`isInt`/`float(...,'en-GB')` behave as documented at run time.

**Residual, stated rather than hidden:** `Normalise_payload` sits outside `Create_the_application`,
so if it ever failed at run time the run would fail with no `REV | Ops | Failure Alert` call and the
website would get a non-2xx with no body. It is built from total expressions for exactly that
reason, and the website retries with the same id, which the idempotency guard makes safe.

### Label resolution (ADR-051 items 3 and 4)

- **Single-select** - title, applicant type, gender, ethnic group, the ten wellbeing answers, break
  type, income band and other-funding status - uses the existing `Setting_<Key>` + `Map_<field>_label`
  Query + `Derive_<field>` Compose shape, with ADR-024's normalisation (trim, case-fold, dash-fold)
  applied to both sides. Where the form's wording differs from an option label, **the map carries an
  alias row** (`Mr.` -> 3, `Prefer to self-describe` -> 4, `Carer breakdown/urgent need` -> 2); the
  normalisation is never widened to absorb a difference, so "never guess the nearest value" keeps
  its meaning. An unmatched label leaves the column empty and adds a note sentence.
- **Multi-select with an option set** - both condition profiles, care provided type, hear-about-us -
  **filters the map, never loops over the payload**: `Normalise_<Map>_labels` (Select),
  `Normalise_<field>_items` (Select), `Map_<field>_options` (Query over the map), 
  `Select_<field>_option_values` (Select - the projection the expression language has no function
  for; the TAD's four-action description needed this fifth action to project map entries to option
  values), `Derive_<field>` (`join(union(x, x), ',')`, null when empty) and
  `Find_unmatched_<field>_labels` (Query over the payload array). Each `item()` has exactly one
  scope. `A-INT-05`.
- **Preferred contact method** keeps its existing three-`contains` mechanism, now fed from
  `Normalise_payload`.
- **Configuration is 18 `rev_setting` rows**, read by the one existing `ListRecords` call (6 existing
  + 12 new label maps). `Fail_if_a_setting_row_is_missing` requires 18: **the 12 rows must be seeded
  in each environment before, or with, this flow version**, or every submission stops with
  `ConfigurationIncomplete` (ADR-051 consequence 3). No Get-a-row-by-id with an alternate key was
  introduced (IMP-0112; `flow-definition-language` check 2).

### Key drift (ADR-051 item 5)

`Expected_payload_keys` holds, as a literal in the definition, the answer keys of the questions
every applicant sees on every route (TAD Appendix C C.1a - 40 keys). `Find_missing_payload_keys`
lists the ones this body does not carry, and the note names those keys, never a value. A
conditional key the sender omits is not drift, because omission is legitimate (item 11). A
rename of a conditional key is indistinguishable from the question not being shown; the route test
entries (`A-INT-06`) catch that, not the flow.

### The review note (ADR-051 item 10)

`rev_intakereviewnote` is the single place every non-fatal finding is written, in the existing
sentence style: type-rule failures (from `Normalise_payload`'s `type_rule_notes_*` properties),
single-select labels with no matching option, unmatched multi-select labels, a city-register miss
(existing) and missing always-shown keys. It is built in two Compose actions so no expression
approaches the 8,192-character expression limit, then **truncated to 1,990 characters plus
` [trunc]`** (the column holds 2,000). Null when there is nothing to say. The column is a secured
special-category register column, so quoting a raw condition label into it adds no exposure.

### Run history is secured (ADR-051 item 7)

- The trigger sets `secureData: ["outputs"]` (`A-INT-01`).
- **Every action whose inputs or outputs carry an applicant value sets `secureData` itself**, because
  Microsoft documents that the protection does NOT propagate through a Compose: *"If a downstream
  action explicitly uses the hidden outputs from the Compose, Parse JSON, or Response actions as
  inputs, Azure Logic Apps doesn't hide this downstream action's inputs or outputs"*
  (learn.microsoft.com/azure/logic-apps/logic-apps-securing-a-logic-app, "Secure data in run
  history by using obfuscation", read 2026-09-27). The rule applied, and asserted by the Pester
  suite, is the transitive closure: an action that reads `Normalise_payload` (for anything but the
  entry id), `triggerBody()`, or the output of an already-secured action is secured.
- **Compose and Response take `["inputs"]` only.** The same page lists Compose, Parse JSON and
  Response under *Secure Outputs - unsupported* and says their Secure Inputs setting "also hides
  these actions' outputs". ADR-051 item 7 names `["inputs","outputs"]` for `Normalise_payload`; that
  combination is not offered for a Compose, so `["inputs"]` is used, which hides both. Query, Select
  and the connector actions take `["inputs","outputs"]`.
- **Not securable:** `If`, `Scope`, `Terminate`, `InitializeVariable`, `SetVariable` (the same
  list). The two conditions read only the four required keys and the applicant-match count.
- **Deliberately unsecured:** the entry id is not personal data, so the replay guard, the 200
  response, `Log_incomplete_payload` and `Alert_on_failure` stay readable - which keeps a failed or
  rejected submission identifiable from run history. `Find_the_failed_action` is secured because
  `result()` over the scope returns child actions' inputs and outputs.
- *Consequence:* a failed run can no longer be debugged by reading values in run history. Replay the
  sanitised DEV fixture instead. The failure path already recorded only the action name and error
  (NFR-012).

### Not transferred (TAD Appendix C C.6)

Never referenced by any action: `form_id`, `post_id`, `date_created`, `date_updated`, `is_starred`,
`is_read`, `source_url`, `currency`, every `payment_*` and `transaction_*` key, `is_fulfilled`,
`created_by`, `status`, `source_id`, `ip`, `user_agent`, the form-calculated `total_estimated_cost`,
the hidden fixed-value `address_country` and `address_state_province`, and - until Alex confirms the
sub-fields are shown (SDD OQ-053, `TD-011`) - `name_middle` and `name_suffix`. The single exception
to "nothing generated is kept" is the entry `id`, kept as `rev_sourcesubmissionid` only as the
duplicate key and shown to no persona.

### Assumptions this section depends on (Dev Summary §10)

`A-INT-01` (trigger secureData honoured), `A-INT-02` (secured actions hide their own data, and the
Compose non-propagation above), `A-INT-03` (isFloat/isInt/float behaviour), `A-INT-04`
(`contains()` on an object tests key existence), `A-INT-05` (the map-filter multi-select yields the
option list the connector writes), `A-INT-06` (the label strings for routes the sample left empty).
All close in one DEV run replaying the fixture and its variants; none is claimed at any V-level yet.

### TAD rev 13 (ADR-053) — free text is widened, never cut; structured text over its width is refused into a note (2026-09-27)

**This supersedes the D-03 section immediately below, which is kept only so the change is visible.** The reviewer rejected the cut (*"Just make the columns that hold text bigger… because this way, it is not registered somewhere for the grant administrator"*). What the flow does now:
- **No answer is cut anywhere.** `take()` is gone from `Normalise_payload`. The 24 free-text answers of TAD Appendix C C.10 feed Memo columns at the platform ceiling (1,048,576): 13 were already Memo and had their MaxLength raised; 11 were String and are retyped to Memo on the same logical name. `helper_name` is joined whole. The entry id is not applicant text and has no guard.
- **The ten structured answers keep their String width and gain a refusal, not a cut** (TAD Appendix C C.2, rev 13): `first_name`, `last_name`, `email`, `phone`, `address_line`, `address_line2`, `town_city`, `postcode` (rev_applicant) and `helper_email`, `helper_phone` (rev_application). A trimmed value longer than its column becomes null, and `length_notes_1` adds `"<field>: longer than <n> characters, so this answer was not stored."` - the field and the limit, never the value. **Consequence to know:** `first_name`, `last_name` and `postcode` are three of the four required facts, so an over-length one makes `Reject_incomplete_payload` answer 400 (logged and alerted) instead of the write failing with a 500. The application is still not created - the TAD's guard turns an unannounced loss into an announced rejection, not into a stored application.
- **The DEV retype is a one-time operation outside this definition** (TAD 12.4, eight steps, DEV only; TST/ACC and PRD create the columns as Memo on first import). The flow is type-agnostic: it writes the same strings whether the column is String or Memo, so it is the same definition before, during and after the sequence.

### ~~Test Report 2026-09-27-1 revision — D-03: every text answer is cut to its column, and the cut is noted~~ (SUPERSEDED by TAD rev 13, above)

**What failed.** No text answer was length-checked before the write. `rev_provisionaldate` is 200
characters behind an uncapped free-text field, `rev_helpername` (100) joined five name parts (three since 2026-10-05), and the
same was true of every other text column written from `Normalise_payload` (35 answers in all). An
over-long answer failed `Create_application` or `Create_new_applicant`, the run returned 500, the
failure alert fired, and **the application was lost** - the one outcome ADR-051 item 6 and FR-010
exist to prevent, and the opposite of `Reject_incomplete_payload`'s philosophy that only the four
required facts may stop an application.

**What changed, and where.** Each of those answers now ends `take(<the trimmed value>, n)` inside
`Normalise_payload`, where `n` is the MaxLength of the column it is written to (the smaller, where
one answer feeds two columns). Not answered is untouched: the `null` branch of each `if()` is the
same as before (FR-084). `helper_name` is cut after the five parts are joined, so the column holds
the join. `email` is cut after `toLower`. **The cut is inside `Normalise_payload`, not at the write,
on purpose**: `first_name`, `last_name`, `email` and `postcode` also feed `Find_existing_applicant`,
and a cut applied only at the write would match an untruncated value against a truncated stored one,
so a returning applicant with an over-long name would never be matched and would be duplicated on
every submission.

**The note.** `length_notes_1` and `length_notes_2` (new `Normalise_payload` keys, split so neither
expression approaches Power Automate's 8,192-characters-per-expression limit) carry one sentence per
cut answer - `"<field>: longer than <n> characters; the first <n> were kept."` - and
`Compose_intake_review_note_part_1` concatenates them after the type-rule notes, into
`rev_intakereviewnote` like every other non-fatal finding (ADR-051 item 10). The sentence names the
field and the limit and **never quotes the answer**: the kept text is already on the record, and many
of these fields are special-category free text.

**Units.** `length()`/`take()` on a string and Dataverse's nvarchar/ntext MaxLength both count UTF-16
code units, the same basis the existing `take(..., 1990)` on the review note already relies on. The
one edge is a surrogate pair (an emoji) straddling the cut, which `take()` can split; the stored text
then ends in one unpaired code unit. That costs one character of a free-text answer that was already
too long, and it is recorded here rather than guarded.

**Tests.** `IntakeContract.Tests.ps1` → *"D-03 (2026-09-27)"* derives the cap for every answer from
`Entity.xml` independently of the flow and fails if an answer written straight to a text column has
no `take()`, a larger one than its column, or no matching sentence; and a separate block asserts no
expression in any flow of the solution exceeds 8,192 characters
(https://learn.microsoft.com/power-automate/limits-and-config, read 2026-09-27).

## Check-7 clearance, 2026-09-30

Describe_the_failure is now a Switch on the failed child name. Besides Read_configuration it descends result() into Create_or_refresh_the_applicant and Return_the_existing_reference_if_this_is_a_replay (Find_the_failed_step_inside_<container>, then Set_failure_detail_from_<container>). Every new Query is secureData inputs/outputs because those containers read and write applicant data. Any other failed child falls to the default branch, unchanged. Source-level only, not yet observed in a DEV run.
