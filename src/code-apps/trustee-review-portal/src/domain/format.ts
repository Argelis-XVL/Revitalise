import { LOCATION_AREA_LABELS, optionLabel } from "../dataverse/schema";
import type { RegionValue } from "../dataverse/types";

/**
 * Display formatting.
 *
 * One rule runs through all of it: a missing value renders as words, never as a blank
 * cell. On a decision screen a blank is ambiguous — it could mean "nothing recorded" or
 * "you are not allowed to see this", and those are very different facts. Every helper
 * here returns a non-empty string.
 */

/** What an absent value looks like. Used everywhere, so it reads consistently. */
export const NOT_RECORDED = "Not recorded";

/**
 * What a value the signed-in trustee cannot read looks like.
 *
 * Used where a column is expected but is not reachable by this role. It is not an
 * error state and not an empty box — see WCAG 1.4.1: the fact is carried by text.
 */
export const NOT_AVAILABLE = "Not available";

export function formatText(value: string | null | undefined): string {
  if (value === null || value === undefined) return NOT_RECORDED;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : NOT_RECORDED;
}

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return "Not scored";
  return String(value);
}

/** en-GB, day-month-year. The audience is UK trustees reading dates aloud in a meeting. */
export function formatDate(iso: string | null | undefined): string {
  if (iso === null || iso === undefined || iso.trim().length === 0) return NOT_RECORDED;
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return iso;
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

/**
 * Preferred dates as one readable phrase (FR-034).
 *
 * Written as a range in words rather than two adjacent cells, so it survives the print
 * stylesheet and reads correctly to a screen reader in one pass.
 */
export function formatDateRange(
  start: string | null | undefined,
  end: string | null | undefined,
): string {
  const hasStart = start !== null && start !== undefined && start.trim().length > 0;
  const hasEnd = end !== null && end !== undefined && end.trim().length > 0;
  if (!hasStart && !hasEnd) return NOT_RECORDED;
  if (hasStart && !hasEnd) return `From ${formatDate(start)}`;
  if (!hasStart && hasEnd) return `Until ${formatDate(end)}`;
  return `${formatDate(start)} to ${formatDate(end)}`;
}

/**
 * An applicant's requested amount, as returned by Dataverse (FR-035, holiday details).
 *
 * This formats runtime applicant data. It holds no fee, no rate and no literal amount,
 * which is what `C-COM-004` forbids in a tracked file.
 */
export function formatAmount(value: number | null | undefined): string {
  if (value === null || value === undefined) return NOT_RECORDED;
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * The region, as text (FR-034).
 *
 * Three inputs, three different sentences. "Not available" and "Not recorded" are NOT
 * interchangeable here: the first says the portal could not read the applicant row, the
 * second says it read it and there was no region. Collapsing them would tell a trustee
 * that a region is missing when in fact it is withheld.
 */
export function formatRegion(region: RegionValue): string {
  switch (region.kind) {
    case "known":
      return optionLabel(LOCATION_AREA_LABELS, region.value);
    case "not-recorded":
      return NOT_RECORDED;
    case "unavailable":
      return NOT_AVAILABLE;
  }
}

/** A sortable key for a date that may be absent. Absent sorts last in both directions. */
export function dateSortKey(iso: string | null | undefined): number | null {
  if (iso === null || iso === undefined || iso.trim().length === 0) return null;
  const parsed = new Date(iso);
  return Number.isNaN(parsed.getTime()) ? null : parsed.getTime();
}
