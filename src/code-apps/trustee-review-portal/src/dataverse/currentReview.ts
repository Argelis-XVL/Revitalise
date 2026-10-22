/**
 * Which review row is "the review" for an application — portal TAD trustee-portal-design-2
 * ADR-086 point 2 (SDD A-14, FR-116, wbs:6.3).
 *
 * `rev_review` is N:1 against `rev_application` and has no alternate key, so an application can
 * carry more than one review row. "The review" means the newest: latest `rev_paneldate`, a null
 * panel date ranked OLDEST, ties broken by `rev_reviewid` (ascending, so the answer is the same
 * on every read). ONE function decides it, and every reader calls it — the dialog's own read
 * (`repository.getReviewForApplication`), the list's verdict state (`domain/ownVerdict.ts`) and
 * the group verdict planner (`domain/groupVerdict.ts`) — so the list, the dialog and a group run
 * can never pick different rows for the same application.
 *
 * Pure, no connector import, so domain code and tests can use it directly.
 */
import { sameRecord } from "./odata";
import type { ReviewRow } from "./types";

function panelTime(row: ReviewRow): number {
  if (row.panelDate === null) return Number.NEGATIVE_INFINITY;
  const time = Date.parse(row.panelDate);
  return Number.isNaN(time) ? Number.NEGATIVE_INFINITY : time;
}

/** Newest first, null panel date last, then review id ascending. */
export function compareReviewsNewestFirst(left: ReviewRow, right: ReviewRow): number {
  const byDate = panelTime(right) - panelTime(left);
  if (byDate !== 0 && !Number.isNaN(byDate)) return byDate;
  return left.id.localeCompare(right.id, "en-GB");
}

/**
 * The current review for `applicationId` among `rows`, or `null` when none of them belongs to it.
 * Rows for other applications are ignored, so a list-wide read can be passed whole.
 */
export function currentReviewFor(
  applicationId: string,
  rows: readonly ReviewRow[],
): ReviewRow | null {
  const mine = rows.filter((row) => row.applicationId !== null && sameRecord(row.applicationId, applicationId));
  if (mine.length === 0) return null;
  return [...mine].sort(compareReviewsNewestFirst)[0] ?? null;
}
