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
  /**
   * rev_additionalamountrequested — the exceptional-funding top-up (FR-035, FR-059, TAD §3.2).
   * Combined with `amountRequested` into FR-035's single "total funding requested" figure via
   * `domain/format.ts`'s `totalFundingRequested()` — never rendered as a separate itemised
   * line, per the reviewer's OQ-031 answer ("no itemised cost breakdown").
   */
  additionalAmountRequested: number | null;
  /**
   * rev_exceptionalfundingrequested (TAD §3.2) — display context for the total above, so the
   * figure is "explicable rather than just larger". Does not gate the arithmetic.
   */
  exceptionalFundingRequested: boolean;
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
  /**
   * rev_careprovidedtype — the STRUCTURED care-support pair's first half (FR-035, TAD
   * §3.2). A multiselect picklist, `IsSecured=0`, deliberately trustee-visible: "the type
   * and volume of caregiving is what the funding decision weighs, not anyone's identity"
   * (the column's own authored description). NOT gated by `redactionReleased` — that gate
   * exists only for the three `…redacted` free-text columns above; this is a structured
   * fact read unconditionally, the same basis as `amountRequested`. See `A-TR-13`
   * (`odata.ts`) for the wire-shape guess this reads through.
   */
  careProvidedType: number[] | null;
  /**
   * rev_carehoursperweek — the structured pair's second half (FR-035, TAD §3.2).
   * `OptionSets/rev_carehoursband.xml`'s five bands. `IsSecured=0`, unconditional, same
   * basis as `careProvidedType` above.
   */
  careHoursPerWeek: number | null;
  /**
   * rev_applicant.rev_applicanttype — the applicant-type context FR-035 names (TAD §3.2):
   * disabled person / carer applying on behalf of a disabled person / carer applying for
   * themselves. `IsSecured=0` on `rev_applicant`, read only for the detail screen (the list
   * screen has no use for it — FR-034 does not ask for it there), unconditional like the
   * structured care-support pair above.
   */
  applicantType: number | null;

  /* ----------------------------------------------------------------------------------- *
   * Amendment A-05 (TAD §3.2.2/§3.2.3, ADR-031, ADR-032, WBS 6.3, SDD §7.1b) — every
   * further board-pack field. Two families, both unconditional (not gated by
   * `redactionReleased`) and both `IsSecured=0` on `rev_application`:
   *   - "Group A" structured facts, read and rendered the same way `careProvidedType` is.
   *   - the five further `…redacted` counterparts ADR-031 adds, which ARE gated by
   *     `redactionReleased` — see `financialFreeTextState`/`conditionFreeTextState` in
   *     `domain/visibility.ts`, the same three-state pattern `careSupportState` already
   *     uses for the three above.
   * The eleven secured "Group B" columns (benefit status, employment status, and the
   * helper/referee/emergency-contact identity columns) are DELIBERATELY ABSENT from this
   * interface and from every query in this app — ADR-032. Their restricted state comes
   * from the build-derived field catalogue (`domain/fieldCatalogue.ts`), never a fetched
   * column, so there is no field here for them to occupy.
   * ----------------------------------------------------------------------------------- */

  /** rev_incomeflag — Personal (Art. 6), unconditional. */
  incomeFlag: number | null;
  /** rev_incomeband — Personal (Art. 6), unconditional. */
  incomeBand: number | null;
  /**
   * rev_savingsover6000 — Personal (Art. 6), unconditional. Tri-state: several sibling
   * columns in this same family document that an absent answer is normal and must stay
   * distinguishable from an explicit "No" — see `asNullableBoolean` (`dataverse/odata.ts`).
   */
  savingsOver6000: boolean | null;
  /**
   * rev_conditionprofile — the applicant's own condition categories (Special category,
   * Art. 9; trustee-visible by design, §7.1a). Multi-select, unconditional, same basis as
   * `careProvidedType` above.
   */
  conditionProfile: number[] | null;
  /** rev_supportrecipientconditionprofile — the support recipient's, same basis. */
  supportRecipientConditionProfile: number[] | null;
  /** rev_helperorganisation — Personal (Art. 6), not identity, unconditional. */
  helperOrganisation: string | null;
  /** rev_helperrelationship — Personal (Art. 6), not identity, unconditional. */
  helperRelationship: string | null;
  /** rev_helperdeclarationconsent — tri-state, same reasoning as `savingsOver6000`. */
  helperDeclarationConsent: boolean | null;
  /** rev_helperdeclarationconsentdate. */
  helperDeclarationConsentDate: string | null;

  /**
   * rev_unabletofundexplanationredacted (ADR-031) — the redacted counterpart of a Personal
   * (Art. 6), NOT special-category, secured financial free-text source. Gated by
   * `redactionReleased`, same as every other `…redacted` field on this interface.
   */
  redactedUnableToFundExplanation: string | null;
  /**
   * rev_otherconditionredacted (ADR-031) — the redacted counterpart of the applicant's own
   * secured "other condition" free text.
   */
  redactedOtherCondition: string | null;
  /**
   * rev_supportrecipientotherconditionredacted (ADR-031) — the redacted counterpart of the
   * support recipient's equivalent secured free text — special-category data about a third
   * party.
   */
  redactedSupportRecipientOtherCondition: string | null;
  /** rev_exceptionalfundingdetailredacted (ADR-031). */
  redactedExceptionalFundingDetail: string | null;
  /** rev_otherexceptionalcircumstanceredacted (ADR-031). */
  redactedOtherExceptionalCircumstance: string | null;
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

/**
 * A mean over one of the three nullable money columns, together with the population it was
 * computed over (ADR-039, TAD §3.3 property 8, Revision 6).
 *
 * All three money columns (`rev_costs`, `rev_amountrequested`, `rev_additionalamountrequested`)
 * are `RequiredLevel` `None`, so the presence subset a mean is computed over can differ from
 * the `count` beside it in the same row. Property 8: *"the reader's natural assumption — that
 * `averageCost` is the mean over the `count` beside it — is the one thing that will silently be
 * false."* So a money average is never a bare number: `value` never appears without the
 * `population` it was divided by, in the same object, so the two can never be separated by a
 * rendering choice.
 *
 * `population` is typed nullable because this is a WIRE type — what an unvalidated document
 * could in principle contain — not a post-parse guarantee. `parseMoneyMeasure` in
 * `roundStatistics.ts` never returns an object with a null `population`: a `value` with no
 * usable denominator is dropped entirely (the whole measure becomes `null`, the same "malformed
 * entry is dropped rather than rendered as a zero" rule `parseCategory` already applies), because
 * rendering `value` without its denominator on screen is exactly what property 8 forbids.
 *
 * A `null` `MoneyMeasure` — the object, not a field on it — means the measure's own population
 * fell below `k` (`RoundStatisticsMoneyMeasureMinimumPopulation`, seeded 5, TAD §6.3.5) and was
 * deliberately withheld: not an error, not a zero, and the row's `count` still renders.
 */
export interface MoneyMeasure {
  value: number;
  population: number | null;
}

/** FR-059 — the exceptional-funding half. */
export interface ExceptionalFundingSummary {
  population: number | null;
  anyCount: number;
  anyPercentage: number | null;
  /** ADR-039 shape (Revision 6) — `null` below `k`, TAD §6.3.5. */
  averageAmountRequested: MoneyMeasure | null;
}

/** FR-060 — one break type's row. */
export interface BreakTypeRow {
  value: number;
  count: number;
  /** ADR-039 shape (Revision 6) — each money measure gated on its OWN population, TAD §6.3.5. */
  averageCost: MoneyMeasure | null;
  averageAmountRequested: MoneyMeasure | null;
  /** A ratio of two sums over a single both-present subset (TAD §3.3 property 8), not two
   *  independently-filtered ones — so it carries a THIRD population, its own. */
  percentageOfCost: MoneyMeasure | null;
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
  /** ADR-039 shape (Revision 6) — same gating as `BreakTypeRow`'s, TAD §6.3.5. */
  averageCost: MoneyMeasure | null;
  averageAmountRequested: MoneyMeasure | null;
  percentageOfCost: MoneyMeasure | null;
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
   * FR-061's ethnicity half — a distribution like the three above it, as of TAD §0.11.
   *
   * **This type used to be the literal `null` type, and the change is deliberate.** The
   * old comment claimed there was no column to aggregate and never had been; TAD §0.11
   * (Revision 8, 2026-08-31) records that as false — the ethnic-group option set is
   * captured on the applicant today, and the reviewer risk-accepted rendering it as a
   * percentage of the round's applications on the same reasoning already accepted for
   * gender, age range and applicant type. So this key now parses like its three siblings
   * and stays `null` whenever the response does not carry it.
   *
   * Two boundaries the type cannot state and this comment therefore does:
   *
   *   - **DEV only.** TAD §0.11 point 3 scopes the build to DEV; promotion to TST/ACC or
   *     PRD stays gated on the DPIA sign-off tracked as OQ-030 (`EX-005`,
   *     `contract/known-exceptions.json`). In any environment where the flow has not been
   *     changed, this arrives `null` and the screen renders nothing — unchanged behaviour.
   *   - **Counts only ever reach the browser.** The underlying column is secured and this
   *     app never reads it; the distribution is aggregated inside
   *     `REV | Portal | Round Statistics` by an identity that is a profile member, exactly
   *     as the gender distribution already is (TAD §1.1 obstacle A, §6.3).
   */
  ethnicGroupDistribution: Distribution | null;
  wellbeingLastYear: WellbeingLastYear | null;
  lifeSatisfactionDistribution: Distribution | null;
  highHoursCareProportion: ProportionMetric | null;
  lowLifeSatisfactionProportion: ProportionMetric | null;
  unableToTakeBreakProportion: ProportionMetric | null;
}

/**
 * The whole `REV | Portal | Round Statistics` response — TAD §3.3.
 *
 * One JSON document, parsed and validated by `roundStatistics.ts` rather than trusted.
 *
 * **Revision 5 (ADR-038) moved where those bytes travel and changed nothing else about
 * them.** The document used to arrive in a `Respond to a Power App or flow` Text output;
 * it now arrives in `rev_roundstatisticsresult.rev_resultjson`, an `ntext` column. A
 * Dataverse text column can hold nothing but text, so "one JSON string" stops being a
 * deliberate conservatism — chosen because the structured-output contract was unverified —
 * and becomes the only available shape. The type guard below is doing exactly the same job
 * over exactly the same bytes, and TAD §12.2's structured-output verification row is closed
 * as moot rather than carried.
 *
 * One field is added by Revision 5 and no field is removed: `staleAfterSeconds`, beside
 * `metrics` and never inside it (`metrics` gains no key and loses none).
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
  /**
   * The age at which this document stops counting as current, in seconds — TAD §3.3
   * property 7, ADR-038. Compared against `now − computedOn` by `roundStatistics.ts`.
   *
   * ## `null` here means "always recompute". It does NOT mean "absent, render nothing"
   *
   * This is **the one field in this contract where a null is not an absence.** TAD §3.3
   * point 3 — *"an unavailable metric is `null`, never `0`; the screen renders no section for
   * a null"* — is a rule about **metrics**. This is not a metric. It is a tunable, and its
   * null has its own meaning: *no bound, so no document is ever fresh, so every mount asks
   * for a fresh computation.*
   *
   * That direction is deliberate and it is the fail-safe one. The opposite default —
   * treating an unbounded age as fresh — would put a figure of **unknown age in front of a
   * board**, which is the failure this whole screen's freshness stamp exists to prevent. A
   * null therefore reproduces Revision 2's behaviour exactly (recompute on every mount):
   * slower, never wrong.
   *
   * **It is null in the shipping configuration**, and that is not a placeholder. No
   * `rev_setting` row named `RoundStatisticsStaleAfterSeconds` exists in
   * REV-GrantApplications-DEV (confirmed 2026-08-28); its value is **OQ-042**, open, whose
   * own default if unanswered is *leave the row unseeded*. Nothing in this app supplies a
   * number for it, guesses one, or falls back to one: the flow reads `rev_setting` and hands
   * the bound over **with the document it bounds**.
   *
   * ## Why it travels in the response rather than being read here
   *
   * The app *cannot* read it. `REV Trustee` deliberately holds no `prvReadrev_setting`,
   * recorded as intentional in the role source, and TAD §5.2's design position depends on
   * that staying true. Handing the bound over inside the document also removes a drift
   * surface by construction: a bound read from a different place than the timestamp it is
   * compared against is two facts that can disagree, and this is one fact.
   *
   * On a first-ever mount, or after a failed computation, there is no parseable document and
   * therefore no bound at all — and the app treats that result as **stale**, which is the
   * same fail-safe as a null.
   */
  staleAfterSeconds: number | null;
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
   * Every FR-058..FR-062 figure, from `REV | Portal | Round Statistics` (TAD §5.4 step 2,
   * as superseded by §5.3.1).
   *
   * No arguments, by design, and under Revision 5 that is a property of the mechanism rather
   * than a promise about it: the flow is Dataverse-row-triggered and **reads nothing from
   * its trigger body** (TAD §1.5 point 4, §6.3.1), so there is no round key, filter or
   * column list a caller could steer. Resolves for any `status` the flow reports, including
   * a non-`ok` one, and for the synthetic `pending` this app raises when its own poll bound
   * is reached — the caller decides what to render. Rejects when the read or the parse
   * failed.
   */
  getRoundStatistics(): Promise<RoundStatisticsResponse>;
}
