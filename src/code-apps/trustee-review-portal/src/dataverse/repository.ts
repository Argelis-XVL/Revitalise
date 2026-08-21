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
import { andFilters, asAffirmativeBoolean, asGuid, asNumber, asString, odataGuid } from "./odata";
import {
  APPLICANT_REGION_COLUMNS,
  APPLICATION_DETAIL_COLUMNS,
  APPLICATION_LIST_COLUMNS,
  ENTITY_SETS,
  PRIMARY_KEYS,
  REVIEW_COLUMNS,
  VERDICT_NOTES_MAX_LENGTH,
} from "./schema";
import { slotColumns } from "../domain/slots";
import { visibleForReview } from "../domain/visibility";
import type {
  ApplicationDetail,
  ApplicationSummary,
  CurrentUser,
  RawRow,
  RegionValue,
  ReviewRow,
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
 * How many applicant ids go into one `$filter`.
 *
 * An OR-joined GUID filter is ~45 characters per id, so the 500-row cap would produce a
 * 22KB query string. Chunking keeps every request comfortably short; 50 is arbitrary but
 * bounded, and a normal round needs one request.
 */
const APPLICANT_LOOKUP_CHUNK = 50;

function mapSummary(row: RawRow, region: RegionValue): ApplicationSummary | null {
  const id = asGuid(row[PRIMARY_KEYS.application]);
  if (id === null) return null; // A row with no id cannot be opened or written to.
  return {
    id,
    reference: asString(row.rev_name) ?? "(no reference)",
    circumstanceScore: asNumber(row.rev_circumstancescore),
    region,
    preferredStart: asString(row.rev_breakstart),
    preferredEnd: asString(row.rev_breakend),
    status: asNumber(row.rev_status),
    reviewRound: asString(row.rev_reviewround),
    eligibleForRound: asAffirmativeBoolean(row.rev_eligibleforround),
    redactionReleased: asAffirmativeBoolean(row.rev_redactionreleased),
  };
}

function mapDetail(row: RawRow, region: RegionValue): ApplicationDetail | null {
  const summary = mapSummary(row, region);
  if (summary === null) return null;
  return {
    ...summary,
    redactedNarrative: asString(row.rev_narrativeredacted),
    scoreBreakdown: asString(row.rev_scorebreakdown),
    breakType: asNumber(row.rev_breaktype),
    breakLocation: asString(row.rev_breaklocation),
    providerPreference: asString(row.rev_providerpreference),
    amountRequested: asNumber(row.rev_amountrequested),
    costs: asNumber(row.rev_costs),
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

function chunk<T>(items: readonly T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size));
  }
  return chunks;
}

/**
 * Resolves each applicant id to a region (FR-034, FR-027).
 *
 * Two columns, one table, joined client-side on `_rev_applicantid_value` rather than by
 * `$expand`. `$expand` would need the lookup's NAVIGATION PROPERTY name, which is a
 * platform contract this project has not ground-truthed — and getting it wrong returns a
 * row with the region silently absent, which is indistinguishable from an applicant who
 * has no region. A second query with an explicit id filter has no such failure mode.
 *
 * A failure here degrades the region column to `unavailable` and NOTHING else: the
 * applications list must still work when the `REV Trustee` role's new
 * `prvReadrev_applicant` has not reached the environment yet. It is not re-queried by
 * another route and it is not back-filled (`code-apps.md` → Data Access & Auth).
 */
async function resolveRegions(
  applicantIds: readonly string[],
): Promise<Map<string, RegionValue>> {
  const regions = new Map<string, RegionValue>();
  if (applicantIds.length === 0) return regions;

  for (const ids of chunk(applicantIds, APPLICANT_LOOKUP_CHUNK)) {
    const filter = ids.map((id) => `${PRIMARY_KEYS.applicant} eq ${odataGuid(id)}`).join(" or ");
    let rows: RawRow[];
    try {
      const result = await listRecords({
        entityName: ENTITY_SETS.applicant,
        select: APPLICANT_REGION_COLUMNS,
        filter,
      });
      rows = result.rows;
    } catch {
      // Deliberately swallowed, and deliberately NOT retried by another route. Every id
      // in this chunk stays absent from the map, which the caller renders as
      // "Not available" — the honest answer.
      continue;
    }
    for (const row of rows) {
      const id = asGuid(row[PRIMARY_KEYS.applicant]);
      if (id === null) continue;
      const value = asNumber(row.rev_locationarea);
      regions.set(id, value === null ? { kind: "not-recorded" } : { kind: "known", value });
    }
  }
  return regions;
}

/** The region for one application row, from a resolved map. Absent means unreadable. */
function regionFor(row: RawRow, regions: Map<string, RegionValue>): RegionValue {
  const applicantId = asGuid(row._rev_applicantid_value);
  if (applicantId === null) return { kind: "unavailable" };
  return regions.get(applicantId) ?? { kind: "unavailable" };
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

    // Resolve regions only for rows that survive the conjunction, so no applicant row is
    // read on account of a case the trustee may not see.
    const eligible = rows.filter((row) => asAffirmativeBoolean(row.rev_eligibleforround));
    const applicantIds = [
      ...new Set(
        eligible
          .map((row) => asGuid(row._rev_applicantid_value))
          .filter((id): id is string => id !== null),
      ),
    ];
    const regions = await resolveRegions(applicantIds);

    const mapped = eligible
      .map((row) => mapSummary(row, regionFor(row, regions)))
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
    const regions = await resolveRegions(applicantId === null ? [] : [applicantId]);
    const detail = mapDetail(row, regionFor(row, regions));
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
};
