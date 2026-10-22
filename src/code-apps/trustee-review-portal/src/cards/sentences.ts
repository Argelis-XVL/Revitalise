/**
 * The computed headline sentences — ADR-062 B, TAD trustee-portal-design-2 §13.7 (reviewer R8,
 * "Approve all (Recommended)"; R16 for the Round progress wording). Card app only.
 *
 * Every function returns the visible sentence, or `null` when the sentence cannot be stated
 * truthfully — then the card shows its existing plain heading instead (§13.7 "Plain heading
 * when"). Each sentence is rendered `aria-hidden`; the card's `<h2>` keeps the plain heading as
 * its accessible name, so a screen reader hears exactly today's headings.
 *
 * Numbers use `formatCount`, money `formatAmount`, dates `formatDate` — the app's own formatting,
 * as §13.7 requires. No sentence ever prints a figure the flow withholds (k = 5): the two figures
 * the exceptional-circumstance sentence reads are not withheld today, and the one withheld figure
 * on that card (the average) is never in it.
 */
import { formatAmount, formatCount, formatDate } from "../domain/format";

const DAY_MS = 86_400_000;

/** A timestamp's UTC calendar day, as a whole-day index. `formatDate` renders in UTC too. */
function utcDay(iso: string): number | null {
  const time = Date.parse(iso);
  if (Number.isNaN(time)) return null;
  const date = new Date(time);
  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()) / DAY_MS;
}

/**
 * *d* (R16, §13.7): the calendar days the round has been open, counted INCLUSIVELY in UTC, from
 * the open date to the end date — today while the round is open (no close date, or one later than
 * today), the close date once it has passed. `null` when the open date is missing, unreadable or
 * after today (the sentence then falls back to "{n} applications in this round").
 */
export function daysOpen(openedOn: string | null, closedOn: string | null, now: Date): number | null {
  if (openedOn === null) return null;
  const open = utcDay(openedOn);
  if (open === null) return null;
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()) / DAY_MS;
  if (open > today) return null;
  const close = closedOn === null ? null : utcDay(closedOn);
  const end = close === null || close > today ? today : close;
  return end - open + 1;
}

function applications(n: number): string {
  return n === 1 ? "1 application" : `${formatCount(n)} applications`;
}

/** Round progress: "{n} applications in the last {d} days" and its edge cases. */
export function roundProgressSentence(
  count: number | null,
  openedOn: string | null,
  closedOn: string | null,
  now: Date,
): string | null {
  if (count === null) return null;
  if (count === 0) return "No applications yet";
  const days = daysOpen(openedOn, closedOn, now);
  if (days === null) return `${applications(count)} in this round`;
  return `${applications(count)} in the last ${days === 1 ? "day" : `${formatCount(days)} days`}`;
}

/** Exceptional circumstances: "1 in {N} applications cite an exceptional circumstance". */
export function exceptionalSentence(anyCount: number | null, population: number | null): string | null {
  if (anyCount === null || population === null || population === 0) return null;
  if (anyCount === 0) return "No application cites an exceptional circumstance";
  if (anyCount === population) return "Every application cites an exceptional circumstance";
  const ratio = population / anyCount;
  const rounded = Math.round(ratio);
  const prefix = Number.isInteger(ratio) ? "" : "About ";
  return `${prefix}1 in ${formatCount(rounded)} applications cite an exceptional circumstance`;
}

/** This round (hero): "Open from {opened} to {closed}" / "Open since {opened}". */
export function roundHeroSentence(openedOn: string | null, closedOn: string | null): string | null {
  if (openedOn === null) return null;
  if (closedOn === null) return `Open since ${formatDate(openedOn)}`;
  return `Open from ${formatDate(openedOn)} to ${formatDate(closedOn)}`;
}

/** Group detail (hero): "{total} requested together". */
export function groupTotalSentence(total: number | null): string | null {
  return total === null ? null : `${formatAmount(total)} requested together`;
}

/** Fixed sentences for the cards that always carry content when rendered (§13.7). */
export const WHO_APPLIED_SENTENCE = "The people behind the applications";
export const LEVEL_OF_NEED_SENTENCE = "How applicants have been feeling";

/**
 * The "Round {name}" eyebrow on the list and group screens (§13.7): the filter's selected round;
 * with "All rounds available to you", the one round the loaded rows share; otherwise none. No
 * new query — it reads the rows the screen already has.
 */
export function roundEyebrow(selectedRound: string, rows: readonly { reviewRound: string | null }[]): string | null {
  if (selectedRound !== "") return `Round ${selectedRound}`;
  const rounds = new Set(rows.map((row) => row.reviewRound).filter((round): round is string => round !== null && round !== ""));
  if (rounds.size !== 1) return null;
  const [only] = [...rounds];
  return only === undefined ? null : `Round ${only}`;
}
