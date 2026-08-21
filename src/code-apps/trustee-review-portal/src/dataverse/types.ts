/**
 * Row interfaces owned by this app.
 *
 * `pac code add-data-source` produced only the generic connector surface, so these are
 * hand-written (see src/dataverse/README.md). Every field is optional-or-null on the
 * raw shapes, because a column can be absent for two very different reasons that the
 * app must not conflate:
 *
 *   - the column is empty, or
 *   - column security hid it from the signed-in trustee.
 *
 * Both render as unavailable. Neither is compensated for and neither is re-queried by
 * another route (`knowledge/technology/code-apps.md` → Data Access & Auth).
 */

/** A row exactly as the connector hands it back: an untyped bag. */
export type RawRow = Record<string, unknown>;

/** The applicant's region, or the reason there isn't one. See `ApplicationSummary`. */
export type RegionValue =
  | { kind: "known"; value: number }
  | { kind: "not-recorded" }
  | { kind: "unavailable" };

/** One application on the summary list (WBS 6.2). */
export interface ApplicationSummary {
  /** rev_applicationid */
  id: string;
  /** rev_name — the pseudonymous reference (ADR-013). Never a person's name. */
  reference: string;
  /** rev_circumstancescore. `null` = not scored yet, or not readable. */
  circumstanceScore: number | null;
  /**
   * The applicant's region (FR-034, FR-027), from `rev_applicant.rev_locationarea`.
   *
   * Three states, kept distinct because they mean different things to a trustee and
   * because collapsing them is how "you may not see this" gets rendered as "nothing
   * recorded":
   *
   *   `known`        — an option-set value, rendered as its region label.
   *   `not-recorded` — the applicant row was read and carries no region.
   *   `unavailable`  — the applicant row could not be read at all. Rendered as
   *                    "Not available" and NEVER back-filled from another column.
   *                    `rev_breaklocation` is the BREAK's location and is not a
   *                    substitute; using it would be exactly the client-side
   *                    compensation `code-apps.md` forbids.
   *
   * `unavailable` is the state to expect until the `REV Trustee` role — amended on
   * 2026-08-21 to add `prvReadrev_applicant` at Global read-only — is actually deployed.
   * The list screen must keep working in that state, so a failure to read applicants
   * degrades this field and nothing else.
   */
  region: RegionValue;
  /** rev_breakstart — ISO date string as returned. */
  preferredStart: string | null;
  /** rev_breakend — ISO date string as returned. */
  preferredEnd: string | null;
  /** rev_status — the option-set value, resolved to text at render time. */
  status: number | null;
  /** rev_reviewround. Drives the round selector; never read from config. */
  reviewRound: string | null;
  /** rev_eligibleforround — strictly `true` to be visible at all (TAD §5.5). */
  eligibleForRound: boolean;
  /** rev_redactionreleased — strictly `true` before any narrative is shown. */
  redactionReleased: boolean;
}

/** One application on the detail screen (WBS 6.3). */
export interface ApplicationDetail extends ApplicationSummary {
  /**
   * rev_narrativeredacted — the ONLY narrative column this app ever binds.
   *
   * `null` here means "nothing to show", which is a different question from "may this
   * be shown". Release is decided by `redactionReleased`, never by whether this
   * happens to hold text.
   */
  redactedNarrative: string | null;
  /** rev_scorebreakdown — evidences the score (FR-035). */
  scoreBreakdown: string | null;
  /** Holiday details (FR-035). */
  breakType: number | null;
  breakLocation: string | null;
  providerPreference: string | null;
  amountRequested: number | null;
  costs: number | null;
}

/** A `rev_review` row for one application and round. */
export interface ReviewRow {
  /** rev_reviewid */
  id: string;
  reference: string | null;
  /** rev_round */
  round: string | null;
  panelDate: string | null;
  /** rev_staffrecommendation (FR-035). */
  staffRecommendation: string | null;
  /** _rev_trustee1_value — a systemuserid, or null when the slot is unassigned. */
  trustee1Id: string | null;
  /** _rev_trustee2_value */
  trustee2Id: string | null;
  verdict1: number | null;
  verdict2: number | null;
  notes1: string | null;
  notes2: string | null;
  /** rev_finalisedon — set by REV | Portal | Finalise Decisions. Locks the round. */
  finalisedOn: string | null;
}

/** The signed-in user, resolved to the identity `rev_review` lookups compare against. */
export interface CurrentUser {
  /** systemuserid, or null when it could not be resolved. */
  systemUserId: string | null;
  /** Display name from the Power Apps host, for the "signed in as" line. */
  fullName: string | null;
  /** Entra object id from the host context, used to find the systemuser row. */
  entraObjectId: string | null;
  /**
   * Why `systemUserId` is null, when it is. Surfaced to the user verbatim, because
   * "you cannot record a verdict" without a reason is not an acceptable dead end.
   */
  unresolvedReason: string | null;
}

/** Which verdict slot the signed-in trustee owns on a given review row. */
export type VerdictSlot = "trustee1" | "trustee2";

export interface SaveVerdictInput {
  reviewId: string;
  slot: VerdictSlot;
  verdict: number;
  /** Optional per FR-037. Empty string clears the notes. */
  notes: string;
}

/** The whole data surface of this app. Everything above `src/dataverse/` uses this. */
export interface TrusteeRepository {
  /**
   * Every application the signed-in trustee may see, across all rounds they can reach.
   * The fail-closed conjunction is applied server-side AND re-asserted client-side.
   */
  listApplicationsForReview(): Promise<ApplicationSummary[]>;
  getApplication(applicationId: string): Promise<ApplicationDetail | null>;
  /** `null` when no review row exists for the application — a first-class state. */
  getReviewForApplication(applicationId: string): Promise<ReviewRow | null>;
  saveVerdict(input: SaveVerdictInput): Promise<void>;
  getCurrentUser(): Promise<CurrentUser>;
}
