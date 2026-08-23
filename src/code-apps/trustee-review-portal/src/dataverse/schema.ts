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
 * breakdown and holiday details.
 *
 * The trustee-visible narrative binds `rev_narrativeredacted` ONLY. The raw
 * special-category narrative column is not named here, not named anywhere else in
 * this app, and must never be added — see src/dataverse/README.md §3.
 */
export const APPLICATION_DETAIL_EXTRA_COLUMNS = [
  "rev_narrativeredacted",
  "rev_scorebreakdown",
  "rev_breaktype",
  "rev_breaklocation",
  "rev_providerpreference",
  "rev_amountrequested",
  "rev_costs",
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

/** OptionSets/rev_breaktype.xml is a placeholder set; labels are resolved leniently. */
export const BREAK_TYPE_LABELS: Readonly<Record<number, string>> = {};

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
