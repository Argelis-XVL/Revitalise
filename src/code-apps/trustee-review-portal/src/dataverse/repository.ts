/**
 * The repository. The whole app's view of Dataverse.
 *
 * Nothing above `src/dataverse/` knows that OData exists, that columns are called
 * `rev_*`, or that an option set is a number. When per-table typed models become
 * reachable (see README.md §1), this file and `client.ts` change and nothing else does.
 *
 * Two rules hold everywhere in here:
 *
 *   1. Every read names its columns explicitly, from the allow-lists in `schema.ts`.
 *      There is no `$select`-everything path and no fallback that widens a query.
 *   2. A null column is reported as null. It is never back-filled from another source,
 *      and a column hidden by column security is never re-fetched by another route
 *      (`knowledge/technology/code-apps.md` → Data Access & Auth). If it is not
 *      readable, the screen says "not available".
 */
import { getRecord, listRecords, updateRecord } from "./client";
import { resolveCurrentUser } from "./identity";
import {
  andFilters,
  asAffirmativeBoolean,
  asGuid,
  asNullableBoolean,
  asNumber,
  asNumberArray,
  asString,
  odataGuid,
} from "./odata";
import { fetchRoundStatistics } from "./roundStatistics";
import {
  APPLICANT_DETAIL_COLUMNS,
  APPLICATION_DETAIL_COLUMNS,
  APPLICATION_LIST_COLUMNS,
  ENTITY_SETS,
  PRIMARY_KEYS,
  REVIEW_COLUMNS,
  ROUND_FINANCE_COLUMNS,
  VERDICT_NOTES_MAX_LENGTH,
} from "./schema";
import { slotColumns } from "../domain/slots";
import { visibleForReview } from "../domain/visibility";
import type {
  ApplicationDetail,
  ApplicationSummary,
  CurrentUser,
  OpenRoundResult,
  RawRow,
  ReviewRow,
  RoundFinance,
  RoundStatisticsResponse,
  SaveVerdictInput,
  TrusteeRepository,
} from "./types";

/**
 * The server-side half of the fail-closed conjunction (TAD §5.5).
 *
 * `rev_eligibleforround eq true` — an affirmative equality, never `ne false`, which
 * would let a null through.
 */
const ELIGIBLE_FILTER = "rev_eligibleforround eq true";

/** Default ordering: highest circumstance score first, then the reference. */
const LIST_ORDER_BY = "rev_circumstancescore desc,rev_name asc";

/**
 * The open-round filter (TAD §5.4 step 1). An affirmative equality, like
 * `ELIGIBLE_FILTER` above and for the same reason: `ne false` would let a null through,
 * and a round nobody has marked open is not an open round.
 */
const OPEN_ROUND_FILTER = "rev_isopen eq true";

/**
 * `top 2`, exactly as TAD §5.4 step 1 specifies.
 *
 * One row is the expected case; two is enough to know the answer is "ambiguous", and a
 * third would not change that verdict. FR-057 is confirmed on the reviewer's own words —
 * one round at a time, once a month — and an invariant a requirement asserts is asserted
 * here rather than assumed (TAD §5.1 point 4).
 */
const OPEN_ROUND_PROBE = 2;

function mapSummary(row: RawRow): ApplicationSummary | null {
  const id = asGuid(row[PRIMARY_KEYS.application]);
  if (id === null) return null; // A row with no id cannot be opened or written to.
  return {
    id,
    reference: asString(row.rev_name) ?? "(no reference)",
    circumstanceScore: asNumber(row.rev_circumstancescore),
    exceptionalCircumstance: asNumber(row.rev_exceptionalcircumstance),
    preferredStart: asString(row.rev_breakstart),
    preferredEnd: asString(row.rev_breakend),
    status: asNumber(row.rev_status),
    reviewRound: asString(row.rev_reviewround),
    eligibleForRound: asAffirmativeBoolean(row.rev_eligibleforround),
    redactionReleased: asAffirmativeBoolean(row.rev_redactionreleased),
    // EF-43 — read at list time now; see APPLICATION_LIST_COLUMNS in schema.ts.
    groupLinkage: asString(row.rev_grouplinkage),
    amountRequested: asNumber(row.rev_amountrequested),
  };
}

function mapDetail(
  row: RawRow,
  applicantType: number | null,
): ApplicationDetail | null {
  const summary = mapSummary(row);
  if (summary === null) return null;
  return {
    ...summary,
    redactedNarrative: asString(row.rev_narrativeredacted),
    scoreBreakdown: asString(row.rev_scorebreakdown),
    breakType: asNumber(row.rev_breaktype),
    breakLocation: asString(row.rev_breaklocation),
    providerPreference: asString(row.rev_providerpreference),
    // amountRequested comes from `summary` above (EF-43) — not re-read here.
    additionalAmountRequested: asNumber(row.rev_additionalamountrequested),
    exceptionalFundingRequested: asAffirmativeBoolean(row.rev_exceptionalfundingrequested),
    costs: asNumber(row.rev_costs),
    redactedCareSupportDescription: asString(row.rev_caresupportdescriptionredacted),
    redactedCareProvidedExample: asString(row.rev_careprovidedexampleredacted),
    redactedOtherCareProvidedType: asString(row.rev_othercareprovidedtyperedacted),
    // TAD §3.2 — unconditional structured facts, not gated by redactionReleased. See
    // types.ts for why: neither is a redacted counterpart of a secured source.
    careProvidedType: asNumberArray(row.rev_careprovidedtype),
    careHoursPerWeek: asNumber(row.rev_carehoursperweek),
    applicantType,
    // Amendment A-05, Group A (TAD §3.2.2/§7.1b) — unconditional structured facts, the
    // same basis as the care-support pair above. Never gated by redactionReleased.
    incomeFlag: asNumber(row.rev_incomeflag),
    incomeBand: asNumber(row.rev_incomeband),
    savingsOver6000: asNullableBoolean(row.rev_savingsover6000),
    conditionProfile: asNumberArray(row.rev_conditionprofile),
    supportRecipientConditionProfile: asNumberArray(row.rev_supportrecipientconditionprofile),
    helperDeclarationConsent: asNullableBoolean(row.rev_helperdeclarationconsent),
    helperDeclarationConsentDate: asString(row.rev_helperdeclarationconsentdate),
    // Amendment A-05 / ADR-031 (TAD §3.2.2, FR-079) — gated by redactionReleased, exactly
    // like the three redacted care-support columns above. See domain/visibility.ts.
    redactedUnableToFundExplanation: asString(row.rev_unabletofundexplanationredacted),
    redactedOtherCondition: asString(row.rev_otherconditionredacted),
    redactedSupportRecipientOtherCondition: asString(
      row.rev_supportrecipientotherconditionredacted,
    ),
    redactedExceptionalFundingDetail: asString(row.rev_exceptionalfundingdetailredacted),
    redactedOtherExceptionalCircumstance: asString(row.rev_otherexceptionalcircumstanceredacted),
  };
}

/**
 * One `rev_roundfinance` row (WBS 6.9, FR-057, FR-058, FR-063).
 *
 * Total by construction — no branch returns null and no field is defaulted. Every measure
 * is `asNumber`, so an unset column stays `null` all the way to the screen, which renders
 * it as words rather than as a zero. These are hand-typed figures on a manual cadence:
 * "nobody has entered the amount committed yet" and "the amount committed is zero" are
 * different facts about a charity's finances, and rule 2 of this file's header — a null
 * column is reported as null, never back-filled — is the whole reason they stay different.
 */
function mapRoundFinance(row: RawRow): RoundFinance {
  return {
    roundKey: asString(row.rev_name),
    isOpen: asAffirmativeBoolean(row.rev_isopen),
    roundOpenedOn: asString(row.rev_roundopenedon),
    roundClosedOn: asString(row.rev_roundclosedon),
    amountCommitted: asNumber(row.rev_amountcommitted),
    peopleSupported: asNumber(row.rev_peoplesupported),
    individualsSupported: asNumber(row.rev_individualssupported),
    peopleReachedByGroupGrants: asNumber(row.rev_peoplereachedbygroupgrants),
    grantGivingCapacity: asNumber(row.rev_grantgivingcapacity),
    suggestedMaximumSpend: asNumber(row.rev_suggestedmaximumspend),
    monthlyDisbursement: asNumber(row.rev_monthlydisbursement),
    remainingLegacyFund: asNumber(row.rev_remaininglegacyfund),
    figuresAsAt: asString(row.rev_figuresasat),
  };
}

function mapReview(row: RawRow): ReviewRow | null {
  const id = asGuid(row[PRIMARY_KEYS.review]);
  if (id === null) return null;
  return {
    id,
    reference: asString(row.rev_name),
    round: asString(row.rev_round),
    panelDate: asString(row.rev_paneldate),
    staffRecommendation: asString(row.rev_staffrecommendation),
    trustee1Id: asGuid(row._rev_trustee1_value),
    trustee2Id: asGuid(row._rev_trustee2_value),
    verdict1: asNumber(row.rev_verdict1),
    verdict2: asNumber(row.rev_verdict2),
    notes1: asString(row.rev_notes1),
    notes2: asString(row.rev_notes2),
    finalisedOn: asString(row.rev_finalisedon),
  };
}

/** Raised when a list came back truncated, so the UI can say so rather than mislead. */
export class TruncatedListError extends Error {
  constructor(limit: number) {
    super(
      `This round returned more than ${String(limit)} applications, which is more than this ` +
        "screen will show. Ask the process owner to narrow the round before deciding from " +
        "this list — it is not complete.",
    );
    this.name = "TruncatedListError";
  }
}

/**
 * The applicant-type context for the detail screen (TAD §3.2, WBS 6.3,
 * Amendment A-02/OQ-032). `IsSecured=0`; unconditional, like the structured care-support
 * pair. Same failure discipline throughout this file: a failed or missing read degrades to
 * `null` and is never retried by another route (`code-apps.md` → Data Access & Auth).
 *
 * The region column this function used to also resolve was read here until EF-02
 * (2026-09-17) secured it and confirmed trustees see no location at all. It is now
 * absent from `APPLICANT_DETAIL_COLUMNS` and from this function's return value — its
 * name is deliberately not written here (`no-secured-columns-in-code-app`, HARD).
 */
async function resolveApplicantDetail(
  applicantId: string | null,
): Promise<number | null> {
  if (applicantId === null) return null;
  let row: RawRow | null;
  try {
    row = await getRecord({
      entityName: ENTITY_SETS.applicant,
      recordId: odataGuid(applicantId),
      select: APPLICANT_DETAIL_COLUMNS,
    });
  } catch {
    return null;
  }
  if (row === null) return null;
  return asNumber(row.rev_applicanttype);
}

export const dataverseRepository: TrusteeRepository = {
  async listApplicationsForReview(): Promise<ApplicationSummary[]> {
    const { rows, truncated } = await listRecords({
      entityName: ENTITY_SETS.application,
      select: APPLICATION_LIST_COLUMNS,
      filter: ELIGIBLE_FILTER,
      orderBy: LIST_ORDER_BY,
    });
    if (truncated) throw new TruncatedListError(rows.length);

    const eligible = rows.filter((row) => asAffirmativeBoolean(row.rev_eligibleforround));
    const mapped = eligible
      .map((row) => mapSummary(row))
      .filter((row): row is ApplicationSummary => row !== null);
    // Client-side re-assertion of the conjunction. Deliberately not trusting the filter
    // alone: see domain/visibility.ts.
    return visibleForReview(mapped);
  },

  async getApplication(applicationId: string): Promise<ApplicationDetail | null> {
    const row = await getRecord({
      entityName: ENTITY_SETS.application,
      recordId: odataGuid(applicationId),
      select: APPLICATION_DETAIL_COLUMNS,
    });
    if (row === null) return null;
    // The conjunction is checked BEFORE the applicant row is read: a case the trustee may
    // not see must not cause a read against its applicant either (FR-038).
    if (!asAffirmativeBoolean(row.rev_eligibleforround)) return null;
    const applicantId = asGuid(row._rev_applicantid_value);
    const applicantType = await resolveApplicantDetail(applicantId);
    const detail = mapDetail(row, applicantType);
    if (detail === null || !detail.eligibleForRound) return null;
    return detail;
  },

  async getReviewForApplication(applicationId: string): Promise<ReviewRow | null> {
    const filter = andFilters(`_rev_applicationid_value eq ${odataGuid(applicationId)}`);
    const { rows } = await listRecords({
      entityName: ENTITY_SETS.review,
      select: REVIEW_COLUMNS,
      filter,
      orderBy: "rev_paneldate desc",
    });
    const first = rows[0];
    if (first === undefined) return null;
    return mapReview(first);
  },

  async saveVerdict(input: SaveVerdictInput): Promise<void> {
    const columns = slotColumns(input.slot);
    const notes = input.notes.trim();
    if (notes.length > VERDICT_NOTES_MAX_LENGTH) {
      throw new Error(
        `Notes are limited to ${String(VERDICT_NOTES_MAX_LENGTH)} characters.`,
      );
    }
    // Exactly two columns, chosen by the slot. Nothing else on the row is written —
    // TAD §3.1: "Trustees write verdict and notes only".
    await updateRecord({
      entityName: ENTITY_SETS.review,
      recordId: odataGuid(input.reviewId),
      item: {
        [columns.verdict]: input.verdict,
        [columns.notes]: notes.length > 0 ? notes : null,
      },
    });
  },

  getCurrentUser(): Promise<CurrentUser> {
    return resolveCurrentUser();
  },

  /**
   * The open round, read directly by the trustee's own session — TAD §5.4 step 1.
   *
   * The row COUNT is the answer, which is why nothing here throws for zero or many. TAD
   * §5.4: "2 rows means the screen says the round is ambiguous and links to the list,
   * rather than picking one." Note this is evaluated here, client-side, against the direct
   * read — it is a different thing from the flow's own `ambiguous-round` status, which the
   * flow reaches independently and which the screen can show without this one firing.
   *
   * The only read on the landing screen. `rev_application` and `rev_applicant` are not
   * touched, so this screen cannot leak an application column, cannot hit the 500-row cap
   * and does not slow down as the charity grows (TAD §5.4).
   */
  async getOpenRound(): Promise<OpenRoundResult> {
    const { rows } = await listRecords({
      entityName: ENTITY_SETS.roundFinance,
      select: ROUND_FINANCE_COLUMNS,
      filter: OPEN_ROUND_FILTER,
      orderBy: "rev_name asc",
      top: OPEN_ROUND_PROBE,
    });
    if (rows.length === 0) return { kind: "none" };
    if (rows.length > 1) return { kind: "ambiguous", count: rows.length };
    const first = rows[0];
    if (first === undefined) return { kind: "none" };
    return { kind: "one", round: mapRoundFinance(first) };
  },

  /**
   * Every FR-058..FR-062 figure — TAD §5.4 step 2, as superseded by §5.3.1 (ADR-038).
   *
   * No arguments, and there is nothing to pass: the flow is Dataverse-row-triggered and
   * **reads nothing from its trigger body** (TAD §1.5 point 4), so a trustee can cause this
   * one question to be asked and no other. Delegated whole to `roundStatistics.ts` — which
   * now reads `rev_roundstatisticsresult` and writes `rev_roundstatisticsrequest` — because
   * that transport has already been replaced twice, and confining it to one module is what
   * kept each replacement a one-line change here.
   *
   * **This layer adds no second read**, and `repository.test.ts` asserts that: everything on
   * the landing screen that is not `rev_roundfinance` comes through the delegate, which is
   * what makes "the landing screen reads no application or applicant row" (TAD §5.4)
   * checkable rather than intended.
   */
  getRoundStatistics(): Promise<RoundStatisticsResponse> {
    return fetchRoundStatistics();
  },
};
