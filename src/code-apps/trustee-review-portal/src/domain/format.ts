import { LOCATION_AREA_LABELS, optionLabel } from "../dataverse/schema";
import type { MoneyMeasure, RegionValue } from "../dataverse/types";

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

/**
 * What a money average looks like when its own population fell below the disclosure
 * threshold and was withheld (ADR-039, TAD §3.3 property 8, §6.3.5).
 *
 * Deliberately NOT `NOT_RECORDED`. That word asserts nobody entered a value, and here that
 * is false: the underlying `rev_costs` / `rev_amountrequested` / `rev_additionalamountrequested`
 * figures may be fully populated — the mean over them is withheld because too FEW of them
 * are, a population question, not a data-entry one. `NOT_AVAILABLE` is equally wrong for a
 * different reason: it is this app's word for "the signed-in role cannot read this column",
 * and these three columns are `IsSecured=0` — the trustee's role is not what withheld this
 * figure. So a third, neutral word, used for a money measure and nothing else: a deliberate
 * release decision, not a permissions gap and not an absence of data.
 */
export const NOT_SHOWN = "Not shown";

export function formatText(value: string | null | undefined): string {
  if (value === null || value === undefined) return NOT_RECORDED;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : NOT_RECORDED;
}

/**
 * A tri-state yes/no answer (Amendment A-05's financial-eligibility and helper-declaration
 * columns) — "Yes", "No", or `NOT_RECORDED`. `null` is its own state here, not a synonym
 * for "No": several of the source columns' own descriptions say an absent value is normal
 * (e.g. a helper declaration is "collected only when a helper is involved"), so this must
 * not use the same true/false ternary `HolidayPanel` uses for `exceptionalFundingRequested`,
 * which has no third state to lose.
 */
export function formatYesNo(value: boolean | null | undefined): string {
  if (value === null || value === undefined) return NOT_RECORDED;
  return value ? "Yes" : "No";
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
 * A timestamp, date AND time, in UTC (WBS 6.9).
 *
 * `formatDate` above is not a substitute here, and the difference is the point. The
 * landing screen's `computedOn` stamp is seconds old under the live design (TAD §1.2), so
 * a date alone would render two loads five hours apart as the same statement. "What was
 * true when" is the number that matters to a board, and it is the only durable record of
 * what they saw once it reaches the printed pack (TAD §6.4).
 *
 * UTC, and labelled as such, because the response's own stamp is `utcNow()` and silently
 * shifting it into the reader's local zone would make two trustees in two time zones
 * disagree about when the same figures were computed.
 */
export function formatDateTime(iso: string | null | undefined): string {
  if (iso === null || iso === undefined || iso.trim().length === 0) return NOT_RECORDED;
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return iso;
  const formatted = new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  }).format(parsed);
  return `${formatted} UTC`;
}

/**
 * A whole count (WBS 6.9). Thousands separated, because a four-digit application count
 * read aloud in a meeting should not need counting digits.
 */
export function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return NOT_RECORDED;
  return new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 }).format(value);
}

/**
 * A percentage the RESPONSE computed (WBS 6.9) — never one computed here.
 *
 * One decimal place, which is what the source figures carry. A null renders as words, not
 * as `0%`: on this screen a zero is a finding and an absence is an absence (TAD §3.3
 * point 3), and `0%` would assert that nobody in the round fell into a category that may
 * simply never have been counted.
 */
export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return NOT_RECORDED;
  return `${new Intl.NumberFormat("en-GB", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value)}%`;
}

/**
 * A rate to two decimal places — FR-058's applications per day. Not a count and not a
 * percentage; 14.47 applications a day is neither.
 */
export function formatRate(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return NOT_RECORDED;
  return new Intl.NumberFormat("en-GB", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
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
 * One of ADR-039's four money measures (TAD §3.3 property 8, §6.3.5), rendered with its own
 * denominator IN THE SAME STRING as its value — never a separate cell, never a tooltip, so the
 * two can never be visually separated. `formatValue` supplies the value's own unit (an amount
 * or a percentage); this function supplies the "and this many applications" half every measure
 * needs to be auditable.
 *
 * A `null` measure — the object, not a field on it — renders as `NOT_SHOWN`: a deliberate
 * suppression (the measure's own population fell below the disclosure threshold, TAD §6.3.5),
 * never `NOT_RECORDED`, never `0`/`£0.00`/`0%`, and never a blank cell. The row's `count` is
 * rendered elsewhere and is unaffected — only the money figure is withheld.
 */
function formatMoneyMeasure(
  measure: MoneyMeasure | null,
  formatValue: (value: number) => string,
): string {
  if (measure === null) return NOT_SHOWN;
  return `${formatValue(measure.value)} (over ${formatCount(measure.population)} applications)`;
}

/** A money-measure whose `value` is a GBP amount — `averageCost`, `averageAmountRequested`. */
export function formatMoneyMeasureAmount(measure: MoneyMeasure | null): string {
  return formatMoneyMeasure(measure, formatAmount);
}

/** A money-measure whose `value` is a percentage (0-100) — `percentageOfCost`. */
export function formatMoneyMeasurePercentage(measure: MoneyMeasure | null): string {
  return formatMoneyMeasure(measure, formatPercentage);
}

/**
 * FR-035's "total funding requested for the grant round" (TAD §3.2, Amendment A-02/OQ-031) —
 * `rev_amountrequested` plus `rev_additionalamountrequested`, summed UNCONDITIONALLY, per the
 * TAD's own wording: "with the `rev_exceptionalfundingrequested` flag so the total is
 * explicable rather than just larger" — the flag is display context, not an arithmetic gate.
 * Safe to sum unconditionally because `rev_additionalamountrequested` is only ever populated
 * when exceptional funding was actually requested.
 *
 * `null` only when BOTH source columns are null — one populated and the other absent sums as
 * if the absent one were zero, never as "not recorded" for the whole figure.
 */
export function totalFundingRequested(
  amountRequested: number | null | undefined,
  additionalAmountRequested: number | null | undefined,
): number | null {
  const hasAmount = amountRequested !== null && amountRequested !== undefined;
  const hasAdditional = additionalAmountRequested !== null && additionalAmountRequested !== undefined;
  if (!hasAmount && !hasAdditional) return null;
  return (hasAmount ? amountRequested : 0) + (hasAdditional ? additionalAmountRequested : 0);
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
