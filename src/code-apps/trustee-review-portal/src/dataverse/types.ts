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
  /**
   * rev_caresupportdescriptionredacted — the free-text companion to the structured
   * care-support fields (FR-035, TAD §3.2.1, WBS 6.3). Gated by `redactionReleased`
   * exactly like `redactedNarrative`; the app never binds the secured source this
   * redacts (see `src/dataverse/README.md` §3 and `schema.ts`).
   */
  redactedCareSupportDescription: string | null;
  /** rev_careprovidedexampleredacted — same gate, same shape, TAD §3.2.1. */
  redactedCareProvidedExample: string | null;
  /** rev_othercareprovidedtyperedacted — same gate, same shape, TAD §3.2.1. */
  redactedOtherCareProvidedType: string | null;
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

/* ------------------------------------------------------------------------------------- *
 * The landing screen (WBS 6.9) — one directly-read row, and one flow response.
 *
 * Two data shapes, two different trust levels, and the screen must never blend them:
 *
 *   `RoundFinance`             — a `rev_roundfinance` row, read by the TRUSTEE'S OWN
 *                                session (TAD §5.4 step 1). Hand-maintained figures whose
 *                                freshness is `figuresAsAt`.
 *   `RoundStatisticsResponse`  — the response of `REV | Portal | Round Statistics`,
 *                                computed by a PRIVILEGED identity over rows this app
 *                                never sees (TAD §1.1, §3.3). Freshness is `computedOn`,
 *                                which is seconds old.
 *
 * TAD §8.3: "the two freshness statements sit side by side and must not be confused."
 * Keeping them on two separate types is the first half of making that true.
 * ------------------------------------------------------------------------------------- */

/**
 * One `rev_roundfinance` row — the open round's calendar (FR-057, FR-058) and the
 * charity's financial position (FR-063). TAD §3.5's thirteen attributes.
 *
 * Every measure is nullable and a null is reported as null. These figures are typed by a
 * person on some cadence, so an unset one means "nobody has entered it", which is a
 * different fact from zero and must never be rendered as zero.
 */
export interface RoundFinance {
  /**
   * rev_name — the round key, and the value `RoundStatisticsResponse.roundKey` is
   * reconciled against (TAD §5.4 step 3). `null` makes reconciliation impossible, which
   * the screen treats as a mismatch rather than as a pass.
   */
  roundKey: string | null;
  /** rev_isopen, re-read from the row rather than assumed from the server filter. */
  isOpen: boolean;
  /** rev_roundopenedon — FR-058's "date the round opened". Entered, never derived. */
  roundOpenedOn: string | null;
  /** rev_roundclosedon — set once a round closes. */
  roundClosedOn: string | null;
  /** The eight FR-063 measures. Decimal or Whole Number; never Money (TAD §3.5). */
  amountCommitted: number | null;
  peopleSupported: number | null;
  individualsSupported: number | null;
  peopleReachedByGroupGrants: number | null;
  grantGivingCapacity: number | null;
  suggestedMaximumSpend: number | null;
  monthlyDisbursement: number | null;
  remainingLegacyFund: number | null;
  /**
   * rev_figuresasat — the date the eight measures above are current as of, and the ONLY
   * thing they are current as of. It does not describe any FR-058..FR-062 figure.
   */
  figuresAsAt: string | null;
}

/**
 * What the `rev_isopen eq true` read found (TAD §5.4 step 1, `top 2`).
 *
 * Zero and two-or-more are first-class RESULTS, not errors: FR-057 asserts that exactly
 * one round is open, and "an invariant a requirement asserts should be asserted in code"
 * (TAD §5.1 point 4). A read that FAILS still throws — that is a different thing from a
 * read that succeeded and found the wrong number of rows, and the screen says so
 * differently.
 */
export type OpenRoundResult =
  | { kind: "one"; round: RoundFinance }
  | { kind: "none" }
  | { kind: "ambiguous"; count: number };

/**
 * The five statuses TAD §3.3 names.
 *
 * `RoundStatisticsResponse.status` is deliberately typed as a bare `string`, NOT as this
 * union: the flow is a separately-deployed artefact that can emit a sixth value this
 * build has never heard of, and a union would make the compiler assert something about
 * another system's behaviour that nothing here can enforce. The screen branches on the
 * known values and has a real fallback for everything else.
 */
export const KNOWN_ROUND_STATISTICS_STATUSES = [
  "ok",
  "no-open-round",
  "ambiguous-round",
  "truncated",
  "threshold-unset",
] as const;

export type KnownRoundStatisticsStatus = (typeof KNOWN_ROUND_STATISTICS_STATUSES)[number];

/** One category of a distribution. TAD §3.3 point 2: the source integer, never a label. */
export interface CategoryCount {
  /**
   * The option-set integer as the response carried it. Resolved to text through this
   * app's own transcribed maps in `schema.ts`, with `Unknown (n)` on drift — never
   * through a label the response might also have carried.
   */
  value: number;
  count: number;
  /** `null` when the response omitted it. Never computed here from count/population. */
  percentage: number | null;
}

/**
 * A single-series distribution. TAD §3.3 point 1: every one carries its own denominator,
 * because "a percentage whose denominator is not on the page is not auditable".
 *
 * There is no second series, second column or comparison bar anywhere in this type.
 * FR-061's benchmark clause is withdrawn (TAD §0.1 item 4, ADR-029 as amended), so a
 * distribution is one observed set of counts and nothing else.
 */
export interface Distribution {
  population: number | null;
  categories: CategoryCount[];
}

/** FR-058 — the round's received count. */
export interface ApplicationsReceived {
  count: number;
}

/**
 * FR-058 — applications per day.
 *
 * The flow's first version always emits this as `null`, so the section it drives renders
 * as ABSENT today: not zero, not an error, and not a heading with an empty body.
 */
export interface ApplicationsPerDay {
  value: number;
  openedOn: string | null;
  days: number | null;
}

/** FR-059 — the exceptional-funding half. */
export interface ExceptionalFundingSummary {
  population: number | null;
  anyCount: number;
  anyPercentage: number | null;
  averageAmountRequested: number | null;
}

/** FR-060 — one break type's row. */
export interface BreakTypeRow {
  value: number;
  count: number;
  averageCost: number | null;
  averageAmountRequested: number | null;
  percentageOfCost: number | null;
}

/**
 * FR-060's total row.
 *
 * TAD §3.3 shows this as `"total": { }` — an empty object with no field named. Its
 * populated shape is genuinely unspecified, so this type mirrors a data row with no
 * category and every field optional, and the screen renders only the fields that arrive.
 * See A-LAND-4.
 */
export interface BreakTypeTotal {
  count: number | null;
  averageCost: number | null;
  averageAmountRequested: number | null;
  percentageOfCost: number | null;
}

export interface BreakTypeProfile {
  population: number | null;
  rows: BreakTypeRow[];
  total: BreakTypeTotal | null;
}

/** FR-062 — one of the three "last year" agreement-scale questions. */
export interface WellbeingQuestion {
  /** The source column name, used to pick this question's heading. */
  column: string;
  population: number | null;
  categories: CategoryCount[];
}

export interface WellbeingLastYear {
  questions: WellbeingQuestion[];
}

/**
 * FR-062's three headline proportions — high-hours care, low life satisfaction, unable to
 * take a break.
 *
 * A-LAND-3 (GUESS, E3) — TAD §3.3 shows all three as `null` and never shows a populated
 * one, so this shape is inferred from what a proportion needs to be auditable on the same
 * terms as every other figure on this screen: a numerator, a denominator and the
 * percentage the response computed. All three are `null` until OQ-039 supplies the three
 * thresholds (TAD §5.2, A-R29), so nothing in this build has ever rendered one.
 */
export interface ProportionMetric {
  population: number | null;
  count: number | null;
  percentage: number | null;
}

/**
 * The `metrics` object of TAD §3.3, field for field.
 *
 * Every member is nullable and **every one of them is `null` today** except
 * `applicationsReceived`. That is the point: TAD §3.3 point 3 — "an unavailable metric is
 * `null`, never `0`. A zero is a finding; a null is an absence." The screen renders no
 * section for a null.
 */
export interface RoundStatisticsMetrics {
  applicationsReceived: ApplicationsReceived | null;
  applicationsPerDay: ApplicationsPerDay | null;
  exceptionalCircumstanceMix: Distribution | null;
  exceptionalFundingSummary: ExceptionalFundingSummary | null;
  breakTypeProfile: BreakTypeProfile | null;
  genderDistribution: Distribution | null;
  ageRangeDistribution: Distribution | null;
  applicantTypeDistribution: Distribution | null;
  /**
   * FR-061's ethnicity half. Typed as `null` and nothing else, on purpose.
   *
   * There is no column to aggregate and there never has been: the field was deliberately
   * never built, and collecting it needs a DPO decision on an Article 9 special category
   * (TAD §3.4, risk A-R24, SDD OQ-027). The response contract declares the key and always
   * emits `null`; typing it `null` makes it structurally impossible for this app to grow
   * a section that renders it, which is stronger than a comment asking nobody to.
   */
  ethnicGroupDistribution: null;
  wellbeingLastYear: WellbeingLastYear | null;
  lifeSatisfactionDistribution: Distribution | null;
  highHoursCareProportion: ProportionMetric | null;
  lowLifeSatisfactionProportion: ProportionMetric | null;
  unableToTakeBreakProportion: ProportionMetric | null;
}

/**
 * The whole `REV | Portal | Round Statistics` response — TAD §3.3.
 *
 * One `Text` output carrying one JSON document, parsed and validated by
 * `roundStatistics.ts` rather than trusted. The flow chose that shape deliberately so the
 * design rests on no unverified structured-output contract (TAD §3.3, §12.2).
 */
export interface RoundStatisticsResponse {
  /**
   * The flow's own verdict on whether its figures are safe to show. Verbatim, including a
   * value this build does not recognise.
   *
   * TAD §3.3 point 4: anything other than `"ok"` means the screen renders the diagnostic
   * state and **no figures at all** — never a partial screen, never a zero.
   */
  status: string;
  /** Reconciled against `RoundFinance.roundKey` before any figure is rendered. */
  roundKey: string | null;
  /** `utcNow()` captured once, before the flow's first read. Displayed, and printed. */
  computedOn: string | null;
  /** FR-058's received population — every application in the round, unfiltered. */
  populationReceived: number | null;
  metrics: RoundStatisticsMetrics;
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
  /**
   * The one open round, read directly by the trustee (WBS 6.9, TAD §5.4 step 1).
   *
   * Resolves for zero, one or many rows — the count is the answer, not an error. Rejects
   * only when the read itself failed.
   */
  getOpenRound(): Promise<OpenRoundResult>;
  /**
   * Every FR-058..FR-062 figure, from `REV | Portal | Round Statistics` (TAD §5.4 step 2).
   *
   * No arguments, by design: the flow takes no input parameters at all, so there is no
   * round key, filter or column list a caller could steer (TAD §1.2). Resolves for any
   * `status` the flow reports, including a non-`ok` one — the caller decides what to
   * render. Rejects when the invocation or the parse failed.
   */
  getRoundStatistics(): Promise<RoundStatisticsResponse>;
}
