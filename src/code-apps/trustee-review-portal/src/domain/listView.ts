/**
 * Sorting, filtering and round derivation for the applications list (WBS 6.2, FR-034).
 *
 * All of it is pure and operates on the COMPLETE set of applications the trustee may
 * see, which is why the repository fetches the whole round in one query. SDD US-013
 * AC-2 requires that "the ordering and filtering apply to all applications under
 * review" — a server-paged sort would apply to a page, which is a different and wrong
 * behaviour.
 */
import { APPLICATION_STATUS_LABELS, LOCATION_AREA_LABELS, optionLabel } from "../dataverse/schema";
import type { ApplicationSummary } from "../dataverse/types";
import { dateSortKey, formatRegion } from "./format";

export type SortKey = "reference" | "score" | "region" | "dates" | "status";
export type SortDirection = "asc" | "desc";

export interface SortState {
  key: SortKey;
  direction: SortDirection;
}

/** Highest score first: the order a trustee comparing cases actually wants. */
export const DEFAULT_SORT: SortState = { key: "score", direction: "desc" };

export interface Filters {
  /** `null` means every round the trustee can see. */
  round: string | null;
  /** `null` means every status. */
  status: number | null;
  /** `null` means every region. Only regions actually present are offered. */
  region: number | null;
  /** Inclusive bounds. `null` means unbounded. */
  scoreMin: number | null;
  scoreMax: number | null;
  /** Free text, matched against the application reference only. */
  text: string;
}

export const EMPTY_FILTERS: Filters = {
  round: null,
  status: null,
  region: null,
  scoreMin: null,
  scoreMax: null,
  text: "",
};

/**
 * The rounds a trustee can choose between.
 *
 * Derived from the `rev_reviewround` values present on the rows they can already see —
 * NOT from configuration. The `REV Trustee` role holds neither `prvReadrev_setting` nor
 * `prvReadEnvironmentVariableValue`, so `rev_setting` and environment-variable values
 * are both unreadable to this app. The data is the only available source, and it is
 * also the correct one: a round with no visible applications is not a round this
 * trustee has anything to do with.
 */
export function deriveRounds(rows: readonly ApplicationSummary[]): string[] {
  const seen = new Set<string>();
  for (const row of rows) {
    if (row.reviewRound !== null) seen.add(row.reviewRound);
  }
  // Descending, so the most recent round label sorts to the top for the usual
  // year-first naming. Locale-aware to keep it stable across environments.
  return [...seen].sort((a, b) => b.localeCompare(a, "en-GB"));
}

/** The statuses actually present, so the filter never offers an empty choice. */
export function deriveStatuses(
  rows: readonly ApplicationSummary[],
): { value: number; label: string }[] {
  const seen = new Set<number>();
  for (const row of rows) {
    if (row.status !== null) seen.add(row.status);
  }
  return [...seen]
    .sort((a, b) => a - b)
    .map((value) => ({ value, label: optionLabel(APPLICATION_STATUS_LABELS, value) }));
}

/**
 * The regions actually present, so the filter never offers an empty choice.
 *
 * Rows whose region is unreadable or unrecorded contribute nothing — filtering by a
 * region is a question only rows with a known region can answer.
 */
export function deriveRegions(
  rows: readonly ApplicationSummary[],
): { value: number; label: string }[] {
  const seen = new Set<number>();
  for (const row of rows) {
    if (row.region.kind === "known") seen.add(row.region.value);
  }
  return [...seen]
    .sort((a, b) => a - b)
    .map((value) => ({ value, label: optionLabel(LOCATION_AREA_LABELS, value) }));
}

export function applyFilters(
  rows: readonly ApplicationSummary[],
  filters: Filters,
): ApplicationSummary[] {
  const needle = filters.text.trim().toLowerCase();
  return rows.filter((row) => {
    if (filters.round !== null && row.reviewRound !== filters.round) return false;
    if (filters.status !== null && row.status !== filters.status) return false;
    if (filters.region !== null) {
      // A row with no readable region is excluded by a region filter rather than being
      // quietly kept: it cannot be shown to satisfy the question that was asked.
      if (row.region.kind !== "known" || row.region.value !== filters.region) return false;
    }
    if (filters.scoreMin !== null) {
      if (row.circumstanceScore === null || row.circumstanceScore < filters.scoreMin) return false;
    }
    if (filters.scoreMax !== null) {
      if (row.circumstanceScore === null || row.circumstanceScore > filters.scoreMax) return false;
    }
    if (needle.length > 0 && !row.reference.toLowerCase().includes(needle)) return false;
    return true;
  });
}

/** Nulls last, whichever direction is asked for. An absent value is not "smallest". */
function compareNullable(
  a: number | string | null,
  b: number | string | null,
  direction: SortDirection,
): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  const base =
    typeof a === "string" && typeof b === "string" ? a.localeCompare(b, "en-GB") : Number(a) - Number(b);
  return direction === "asc" ? base : -base;
}

function sortValue(row: ApplicationSummary, key: SortKey): number | string | null {
  switch (key) {
    case "reference":
      return row.reference;
    case "score":
      return row.circumstanceScore;
    case "region":
      // Sorted by the region's LABEL, so the order is alphabetical as read rather than
      // by the option set's arbitrary numbering. Unreadable and unrecorded sort last.
      return row.region.kind === "known" ? formatRegion(row.region) : null;
    case "dates":
      return dateSortKey(row.preferredStart);
    case "status":
      return row.status === null ? null : optionLabel(APPLICATION_STATUS_LABELS, row.status);
  }
}

export function applySort(
  rows: readonly ApplicationSummary[],
  sort: SortState,
): ApplicationSummary[] {
  // Stable tie-break on the reference, so equal scores keep a predictable order and the
  // table does not reshuffle between renders.
  return [...rows].sort((left, right) => {
    const primary = compareNullable(sortValue(left, sort.key), sortValue(right, sort.key), sort.direction);
    if (primary !== 0) return primary;
    return left.reference.localeCompare(right.reference, "en-GB");
  });
}

/** Filter then sort, in that order. The order the trustee sees on screen. */
export function projectRows(
  rows: readonly ApplicationSummary[],
  filters: Filters,
  sort: SortState,
): ApplicationSummary[] {
  return applySort(applyFilters(rows, filters), sort);
}

/** What clicking a sort header does: same key flips direction, new key starts sensibly. */
export function nextSort(current: SortState, key: SortKey): SortState {
  if (current.key === key) {
    return { key, direction: current.direction === "asc" ? "desc" : "asc" };
  }
  // A score is most useful highest-first; text and dates read best ascending.
  return { key, direction: key === "score" ? "desc" : "asc" };
}

/** The `aria-sort` value for a column header (WCAG 4.1.2). */
export function ariaSortFor(sort: SortState, key: SortKey): "ascending" | "descending" | "none" {
  if (sort.key !== key) return "none";
  return sort.direction === "asc" ? "ascending" : "descending";
}
