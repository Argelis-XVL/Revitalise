/**
 * Dataverse schema facts this app depends on, in one place.
 *
 * Every entity-set name and primary-key name below is stamped with the evidence
 * behind it. `E1` means an artefact the platform itself produced; anything weaker
 * carries an `A-nnn` assumption id and a row in Dev Summary §10.
 */

/** Entity set names — what the connector's `entityName` parameter takes. */
export const ENTITY_SETS = {
  /**
   * E1 — read live from REV-GrantApplications-DEV on 2026-08-21:
   *   EntityDefinitions(LogicalName='rev_application')
   *     ?$select=LogicalName,EntitySetName,PrimaryIdAttribute
   *   -> EntitySetName=rev_applications, PrimaryIdAttribute=rev_applicationid
   */
  application: "rev_applications",

  /**
   * A-TR-6 CLOSED, E1 — confirmed twice independently: the 2026-08-22 DEV import's
   * live `EntityDefinitions(LogicalName='rev_review')?$select=EntitySetName` query
   * (`rev_reviews`, 55 attributes — logged in the Dev Summary's WBS 6.1-6.5 revision),
   * and `pa app add data-source --connector dataverse --table rev_review -u <org-url>
   * -c <connection-id>` against the same environment, which echoes the platform's own
   * `entitySetName` in `power.config.json`'s `databaseReferences.default.cds
   * .dataSources.reviews` — also `rev_reviews`. The original guess was correct, and is
   * no longer a guess.
   */
  review: "rev_reviews",

  /**
   * E1 — same live query, 2026-08-21:
   *   rev_applicant -> EntitySetName=rev_applicants, PrimaryIdAttribute=rev_applicantid
   *
   * Read for ONE column only: `rev_locationarea`, which is where FR-034's "region"
   * comes from. There is no region column on `rev_application`, and `rev_breaklocation`
   * is the break's location, which is a different thing.
   */
  applicant: "rev_applicants",

  /**
   * E1 — same query, 2026-08-21:
   *   systemuser -> EntitySetName=systemusers, PrimaryIdAttribute=systemuserid
   */
  systemUser: "systemusers",

  /**
   * E1 — NOT hand-authored. Read live from REV-GrantApplications-DEV on 2026-08-25 by
   * the first `ensure-schema.ps1 -Env dev` run that created this table, and recorded in
   * `logs/improvement-log.jsonl` as `IMP-0316`:
   *   EntityDefinitions(LogicalName='rev_roundfinance')
   *     ?$select=EntitySetName,PrimaryIdAttribute
   *   -> EntitySetName=rev_roundfinances, PrimaryIdAttribute=rev_roundfinanceid
   *
   * TAD §12.2 carried this as an explicit "do not hand-author it" GUESS row. It is
   * CLOSED: the naive pluralisation happened to be what the platform assigned, which is
   * a fact that was read back rather than a guess that was trusted.
   *
   * Read DIRECTLY by the trustee's own session (TAD §5.4 step 1) — the only table on the
   * landing screen that is. Every FR-058..FR-062 figure comes from the flow instead, and
   * the landing screen reads no application or applicant row at all.
   */
  roundFinance: "rev_roundfinances",
} as const;

/** Primary key column names. */
export const PRIMARY_KEYS = {
  /** E1 — live metadata, 2026-08-21. */
  application: "rev_applicationid",
  /** A-TR-6 CLOSED, E1 — same closure as ENTITY_SETS.review above. */
  review: "rev_reviewid",
  /** E1 — live metadata, 2026-08-21. */
  applicant: "rev_applicantid",
  /** E1 — live metadata, 2026-08-21. */
  systemUser: "systemuserid",
  /**
   * E1 — live metadata, 2026-08-25 (`IMP-0316`). Declared for completeness; the landing
   * screen deliberately does NOT select it. Nothing on that screen opens, links to or
   * writes a round record, so its id is a column the app has no use for — see
   * `ROUND_FINANCE_COLUMNS`.
   */
  roundFinance: "rev_roundfinanceid",
} as const;

/**
 * Columns requested for the applications list (WBS 6.2, FR-034).
 *
 * This is an ALLOW-LIST, not a convenience. A column absent from here is a column
 * this screen cannot show, cannot sort by, cannot filter on and cannot print.
 * `rev_eligibleforround` and `rev_redactionreleased` are selected because the app
 * re-asserts the fail-closed conjunction client-side (TAD §5.5) rather than trusting
 * the server filter alone.
 */
export const APPLICATION_LIST_COLUMNS = [
  PRIMARY_KEYS.application,
  "rev_name", // E1 — PrimaryNameAttribute. Pseudonymous reference (ADR-013), never a person's name.
  "rev_circumstancescore",
  "rev_status",
  "rev_breakstart",
  "rev_breakend",
  "rev_reviewround",
  "rev_eligibleforround",
  "rev_redactionreleased",
  // The applicant lookup, selected ONLY so the region can be resolved (below). The
  // applicant row itself is read for one column; nothing else about the applicant
  // reaches this app.
  "_rev_applicantid_value",
] as const;

/**
 * Extra columns for the detail screen (WBS 6.3, FR-035): redacted narrative, score
 * breakdown, holiday details, and the three redacted care-support columns.
 *
 * The trustee-visible narrative binds `rev_narrativeredacted` ONLY. The raw
 * special-category narrative column is not named here, not named anywhere else in
 * this app, and must never be added — see src/dataverse/README.md §3.
 *
 * The three `…redacted` care-support columns (TAD §3.2.1) are the same shape: each
 * has a secured free-text source that is never named in this app, and each is safe
 * to bind because it is `IsSecured=0` on `rev_application`. Gated by
 * `rev_redactionreleased`, same as the narrative — see `domain/visibility.ts`.
 */
export const APPLICATION_DETAIL_EXTRA_COLUMNS = [
  "rev_narrativeredacted",
  "rev_scorebreakdown",
  "rev_breaktype",
  "rev_breaklocation",
  "rev_providerpreference",
  "rev_amountrequested",
  "rev_costs",
  "rev_caresupportdescriptionredacted",
  "rev_careprovidedexampleredacted",
  "rev_othercareprovidedtyperedacted",
] as const;

export const APPLICATION_DETAIL_COLUMNS = [
  ...APPLICATION_LIST_COLUMNS,
  ...APPLICATION_DETAIL_EXTRA_COLUMNS,
] as const;

/**
 * Columns requested from `rev_review` (WBS 6.3 staff recommendation, WBS 6.4 verdicts).
 *
 * Lookups are selected by their OData value form (`_<column>_value`), which is how a
 * lookup's target id is returned when it is not expanded.
 *
 * A-TR-7 (GUESS, E3) — the `_<lookup>_value` `$select` form is the documented
 * Dataverse Web API shape and is used throughout this project's provisioning scripts,
 * but it has not been observed through the CONNECTOR from a Code App. Cheapest
 * verification: run the app against DEV once `rev_review` exists and log the returned
 * key set for one row.
 */
export const REVIEW_COLUMNS = [
  PRIMARY_KEYS.review,
  "rev_name",
  "rev_round",
  "rev_paneldate",
  "rev_verdict1",
  "rev_verdict2",
  "rev_notes1",
  "rev_notes2",
  "rev_staffrecommendation",
  "rev_finalisedon",
  "_rev_applicationid_value",
  "_rev_trustee1_value",
  "_rev_trustee2_value",
] as const;

/**
 * Columns read from `rev_applicants`. TWO, and this list must stay at two.
 *
 * `rev_applicant` is a Tier 4 table carrying twelve `IsSecured=1` identifying columns.
 * The `REV Trustee` role was granted table Read on 2026-08-21 (WBS 6.1) purely so
 * FR-034's region column is reachable, with column security completely unchanged — so
 * the twelve secured columns still mask to nothing for a trustee. This app narrows
 * further, to the primary key and the region, because "the role could not read it
 * anyway" is a second line of defence and not a reason to ask.
 */
export const APPLICANT_REGION_COLUMNS = [
  PRIMARY_KEYS.applicant,
  "rev_locationarea",
] as const;

/**
 * Columns read from `rev_roundfinances` for the landing screen (WBS 6.9, FR-057, FR-058,
 * FR-063). TAD §3.5's thirteen attributes, in that document's own order, and nothing else.
 *
 * The primary key is deliberately absent. Every other allow-list in this file starts with
 * its table's id because the screen opens, links to or writes that row; nothing on the
 * landing screen does any of those to a round record, so asking for the id would widen a
 * read for no reader.
 *
 * `rev_isopen` is selected even though the server filter already tests it, for the same
 * reason `APPLICATION_LIST_COLUMNS` selects both halves of the fail-closed conjunction:
 * the app can then state what it actually received rather than what it asked for.
 */
export const ROUND_FINANCE_COLUMNS = [
  "rev_name", // The round key. Compared to the flow response's `roundKey` — TAD §5.4 step 3.
  "rev_isopen",
  "rev_roundopenedon",
  "rev_roundclosedon",
  // FR-063's eight measures. Decimal and Whole Number, never Money (TAD §3.5, C-TECH-070).
  "rev_amountcommitted",
  "rev_peoplesupported",
  "rev_individualssupported",
  "rev_peoplereachedbygroupgrants",
  "rev_grantgivingcapacity",
  "rev_suggestedmaximumspend",
  "rev_monthlydisbursement",
  "rev_remaininglegacyfund",
  // The as-at date for the eight measures above, and ONLY for those. The FR-058..FR-062
  // figures beside them carry the flow response's own `computedOn` stamp instead, and the
  // two must never be presented as one statement of freshness (TAD §8.3).
  "rev_figuresasat",
] as const;

/** Columns read from `systemusers` to resolve the signed-in trustee. */
export const SYSTEM_USER_COLUMNS = [
  PRIMARY_KEYS.systemUser,
  "fullname",
  "domainname",
  "azureactivedirectoryobjectid",
] as const;

/**
 * `rev_notes1` / `rev_notes2` are ntext MaxLength=2000 in
 * Entities/rev_review/Entity.xml. Dataverse rejects a longer value at write time;
 * the UI stops it before the round trip and tells the trustee the limit.
 */
export const VERDICT_NOTES_MAX_LENGTH = 2000;

/**
 * Option-set labels, transcribed from this project's own solution source rather than
 * read from OData formatted-value annotations.
 *
 * Why not the annotations: `Prefer: odata.include-annotations` behaviour through the
 * connector is a platform contract this app has not ground-truthed, and a screen that
 * silently renders a blank status when an annotation is missing is worse than one that
 * renders the number it actually received. `optionLabel()` never returns an empty
 * string.
 *
 * Drift is possible in one direction: solution import RELABELS matching option values
 * but does not delete values the new source omits (`IMP-0019`), so the live set can be
 * a superset of this map. That case renders as "Unknown (<value>)", which is a visible
 * prompt to re-transcribe rather than a silent blank.
 */
export const APPLICATION_STATUS_LABELS: Readonly<Record<number, string>> = {
  1: "Submitted",
  2: "Auto-pass",
  3: "Borderline",
  4: "Auto-reject",
  5: "Under Review",
  6: "Eligible for Panel",
  7: "Approved",
  8: "Rejected",
  9: "Withdrawn",
  10: "Incomplete",
  11: "Grant Paid",
};

/** OptionSets/rev_reviewverdict.xml — the three verdicts FR-037 names. */
export const VERDICT_VALUES = {
  approve: 1,
  defer: 2,
  reject: 3,
} as const;

export const VERDICT_LABELS: Readonly<Record<number, string>> = {
  [VERDICT_VALUES.approve]: "Approve",
  [VERDICT_VALUES.defer]: "Defer",
  [VERDICT_VALUES.reject]: "Reject",
};

/**
 * OptionSets/rev_locationarea.xml — the regions FR-027 generalises a postcode into.
 * Transcribed from solution source, same reasoning as the status labels above.
 */
export const LOCATION_AREA_LABELS: Readonly<Record<number, string>> = {
  1: "North East",
  2: "North West",
  3: "Yorkshire and the Humber",
  4: "East Midlands",
  5: "West Midlands",
  6: "East of England",
  7: "London",
  8: "South East",
  9: "South West",
  10: "Wales",
  11: "Scotland",
  12: "Northern Ireland",
  13: "Not known",
};

/**
 * OptionSets/rev_breaktype.xml — the five break types FR-060 breaks the round down by.
 * Transcribed from solution source on 2026-08-25, same reasoning as the status labels.
 *
 * This map was `{}` until WBS 6.9 needed it. The option set had five real authored
 * options the whole time; the empty map was a stale placeholder, and every value it was
 * asked about rendered as `Unknown (n)` — visibly wrong rather than silently wrong, which
 * is why it was safe to leave and worth fixing now.
 */
export const BREAK_TYPE_LABELS: Readonly<Record<number, string>> = {
  1: "Holiday accommodation (hotel, cottage, caravan, holiday park)",
  2: "Day trips or outings",
  3: "Activity or Experience (e.g. theatre, concert, attraction)",
  4: "Respite Care Facility stay",
  5: "Other (please specify)",
};

/**
 * OptionSets/rev_exceptionalcircumstance.xml — FR-059's exceptional-circumstance mix.
 * Transcribed from solution source, 2026-08-25.
 */
export const EXCEPTIONAL_CIRCUMSTANCE_LABELS: Readonly<Record<number, string>> = {
  1: "Palliative care",
  2: "Carer breakdown or urgent need",
  3: "Severe financial hardship",
  4: "Other (please specify)",
};

/**
 * The applicant-gender distribution's labels (FR-061) — five options, transcribed from the
 * global option set in this solution's own `OptionSets/` directory on 2026-08-25.
 *
 * **The option set's own file name, and the column that binds it, are deliberately not
 * written anywhere in this app.** That column is `IsSecured=1` and sits inside
 * `REV_TrusteeRestricted`, so `no-secured-columns-in-code-app` (HARD) derives it into its
 * forbidden set and naming it here would fail the build — correctly, because this app must
 * never ask for it. Nor does it: the distribution is counted inside
 * `REV | Portal | Round Statistics` by an identity that IS a profile member, and only
 * counts reach the browser (TAD §1.1 obstacle A, §6.3).
 *
 * So this map is not a query and cannot become one. It labels integers that arrive in a
 * response body, which is the only form of this data the app ever holds.
 */
export const APPLICANT_GENDER_LABELS: Readonly<Record<number, string>> = {
  1: "Female",
  2: "Male",
  3: "Non-binary",
  4: "Describes themselves another way",
  5: "Prefer not to say",
};

/**
 * OptionSets/rev_agerange.xml — FR-061's age-range distribution. Nine options,
 * transcribed 2026-08-25. Unsecured, unlike the gender set above.
 */
export const AGE_RANGE_LABELS: Readonly<Record<number, string>> = {
  1: "Under 18",
  2: "18 to 24",
  3: "25 to 34",
  4: "35 to 44",
  5: "45 to 54",
  6: "55 to 64",
  7: "65 to 74",
  8: "75 and over",
  9: "Not known",
};

/**
 * OptionSets/rev_applicanttype.xml — FR-061's applicant-type distribution, and the exact
 * three-way category FR-061 spells out in words. Transcribed 2026-08-25.
 */
export const APPLICANT_TYPE_LABELS: Readonly<Record<number, string>> = {
  1: "A disabled person",
  2: "A carer applying on behalf of a disabled person",
  3: "A carer applying for yourself",
};

/**
 * OptionSets/rev_agreementresponse.xml — the scale the three "last year" wellbeing
 * questions use (FR-062). Transcribed 2026-08-25.
 *
 * This is the AGREEMENT scale, not the frequency scale. `rev_wellbeinganswer8`, `9` and
 * `10` bind this set; the seven SWEMWBS items bind `rev_likertresponse` instead, which
 * FR-062 does not ask about. Amendment A-01 establishes that split on hard evidence and
 * solution source already reflects it (TAD §5.2) — labelling an agreement answer with a
 * frequency label would be the silently-wrong rendering `IMP-0019` exists to prevent.
 */
export const AGREEMENT_RESPONSE_LABELS: Readonly<Record<number, string>> = {
  1: "Strongly Disagree",
  2: "Disagree",
  3: "Neutral",
  4: "Agree",
  5: "Strongly Agree",
  6: "Not sure",
};

/**
 * FR-062's life-satisfaction distribution (`rev_feelingscaleanswer`, Whole Number 0-10).
 *
 * Not an option set — a bounded integer — so the "label" is the number itself. It is
 * written out as a map anyway, for one reason: `optionLabel` renders anything outside the
 * declared set as `Unknown (n)`, so a response carrying 11 or -1 shows up as visibly
 * wrong instead of being rendered as a legitimate score. A `String(value)` fallback would
 * accept any integer and tell nobody.
 */
export const LIFE_SATISFACTION_LABELS: Readonly<Record<number, string>> = {
  0: "0",
  1: "1",
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  8: "8",
  9: "9",
  10: "10",
};

/**
 * The three "last year" wellbeing questions FR-062 asks for, in the order the landing
 * screen renders them, with the heading each is given.
 *
 * Keyed by the `column` name the flow response carries for each question (TAD §3.3's
 * `wellbeingLastYear.questions[].column`). A question whose column is not in this map
 * still renders — under its own raw column name — because dropping a question the flow
 * chose to send would be a silent omission on a screen whose whole job is completeness.
 */
export const WELLBEING_QUESTION_HEADINGS: Readonly<Record<string, string>> = {
  rev_wellbeinganswer8: "Wellbeing question 8, last year",
  rev_wellbeinganswer9: "Wellbeing question 9, last year",
  rev_wellbeinganswer10: "Wellbeing question 10, last year",
};

/**
 * Renders an option-set value as text, always. Colour is never the only carrier of
 * meaning in this app (WCAG 1.4.1), so every status and verdict goes through here.
 */
export function optionLabel(
  labels: Readonly<Record<number, string>>,
  value: number | null | undefined,
): string {
  if (value === null || value === undefined) return "Not set";
  return labels[value] ?? `Unknown (${String(value)})`;
}
