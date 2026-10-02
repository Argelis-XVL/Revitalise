/**
 * Group-of-applications derivation for the Trustee Portal (EF-43).
 *
 * `docs/plans/emily-review-feedback-2026-09-plan.md` §4.3 (EF-42/EF-43) and §4.6 — the
 * reviewer explicitly waived the normal `C-COM-002` change-order step for this item on
 * 2026-09-18 ("send the grouped applications in trustee portal... to development-agent
 * already. Skipping commercial-agent."). There is no WBS task id for this item — WBS 6.2
 * specifies only the single flat applications list this module sits above.
 *
 * All pure, all operating on the same complete `ApplicationSummary[]` the flat list already
 * reads — `domain/listView.ts`'s own reasoning applies unchanged: the fetch is the
 * expensive part, and every derivation from it belongs here rather than behind a second
 * query.
 *
 * ## What is deliberately NOT here
 *
 * - **No validation, normalising or `GP`-prefix enforcement of `rev_grouplinkage`.** EF-42
 *   §2g decided the code stays a manual, free-text field — "a groups table and generated
 *   codes are scope creep for this engagement and belong to a later version" — and EF-43
 *   inherits that decision unchanged: "nothing in EF-42 or EF-43 should quietly start fixing
 *   it." Grouping is an EXACT STRING MATCH on the raw value, typos and all, which is the
 *   plan's own accepted risk (mitigated only by surfacing `memberCount`, below).
 * - **No group total holiday/activity cost.** The plan's own worked example: in four of five
 *   sample groups, every member's own cost field carries the WHOLE trip's cost, so summing
 *   double-counts (Group RA sums to £8,300 against a published £2,075); in the fifth the
 *   members split it and the sum is correct. No formula recovers the true figure from the
 *   member rows, and no other authoritative source exists in this app's data model (checked:
 *   `ApplicationSummary`/`ApplicationDetail` carry only the per-application `rev_costs`
 *   field). So `GroupSummary` below has no cost field at all, by decision — not an oversight.
 */
import type { ApplicationSummary } from "../dataverse/types";

/** One row of the group table (EF-43) — the group-level fields the plan fixes, and no more. */
export interface GroupSummary {
  /** The raw `rev_grouplinkage` value, exactly as the admin typed it. Never normalised. */
  code: string;
  /**
   * The number of applications sharing this code. Deliberate, per the plan's own
   * rationale: "so a mistyped/split group is visible at a glance" — a group of four
   * showing as a group of three because of a typo should look wrong immediately.
   */
  memberCount: number;
  /**
   * The sum of the members' own `amountRequested` fields — confirmed safe by the reviewer
   * 2026-09-17 ("Group total requested is the sum of the members' individual requests").
   * Derived, nothing stored. `null` only when NOT ONE member has a recorded amount — the
   * same "absent input, absent output" rule `totalFundingRequested` in `format.ts` uses,
   * rather than rendering a sum of nothing as `£0.00`.
   */
  totalRequested: number | null;
  /**
   * The group's shared start date.
   *
   * JUDGEMENT CALL (not settled by the plan): the plan calls this "the shared start and end
   * dates", presented as though every member necessarily agrees. Nothing enforces that in
   * the data — `rev_breakstart`/`rev_breakend` are per-application fields with no shared-group
   * constraint — so this is not guaranteed literal agreement. Fallback chosen: the EARLIEST
   * start across members with a recorded date (`null` if none have one). When all members
   * genuinely agree, earliest-of-one-value is that value, so the common case is unaffected;
   * a genuine disagreement renders as the spanning range rather than an arbitrary member's
   * date or a silent blank.
   */
  sharedStart: string | null;
  /** The LATEST end date across members with a recorded date — the mirror of `sharedStart`. */
  sharedEnd: string | null;
  /** The group's member applications, in the order they appear in the source list. */
  members: ApplicationSummary[];
}

/** `true` for a `rev_grouplinkage` value that actually links applications into a group. */
function hasGroupCode(row: ApplicationSummary): row is ApplicationSummary & { groupLinkage: string } {
  return row.groupLinkage !== null && row.groupLinkage.trim().length > 0;
}

/** The earliest of the given ISO date strings, ignoring absent ones. `null` if none are present. */
function earliest(dates: readonly (string | null)[]): string | null {
  let best: { iso: string; time: number } | null = null;
  for (const iso of dates) {
    if (iso === null || iso.trim().length === 0) continue;
    const time = new Date(iso).getTime();
    if (Number.isNaN(time)) continue;
    if (best === null || time < best.time) best = { iso, time };
  }
  return best === null ? null : best.iso;
}

/** The latest of the given ISO date strings, ignoring absent ones. `null` if none are present. */
function latest(dates: readonly (string | null)[]): string | null {
  let best: { iso: string; time: number } | null = null;
  for (const iso of dates) {
    if (iso === null || iso.trim().length === 0) continue;
    const time = new Date(iso).getTime();
    if (Number.isNaN(time)) continue;
    if (best === null || time > best.time) best = { iso, time };
  }
  return best === null ? null : best.iso;
}

/** Sums the members' `amountRequested`. `null` when none of them carry a value. */
function sumRequested(members: readonly ApplicationSummary[]): number | null {
  const present = members
    .map((member) => member.amountRequested)
    .filter((value): value is number => value !== null);
  if (present.length === 0) return null;
  return present.reduce((total, value) => total + value, 0);
}

/**
 * Every group present in `rows`, one row per DISTINCT `rev_grouplinkage` value.
 *
 * Rows with no code (`null` or blank) contribute no group and are left for the flat
 * applications list to show on its own — that half of the plan's design is unchanged.
 *
 * **What "above/filters" means depends on the CALLER, and that changed under EF-43 Δ5
 * (2026-09-25).** This function itself does no filtering of its own; it only groups whatever
 * `rows` it is given. `ApplicationsListPage` (the flat list) never called this function at all
 * once EF-43 Δ5 moved the group table off that screen. `GroupsListPage` — the group table's
 * own screen now — calls it with rows ALREADY narrowed by that screen's own filter bar,
 * because a filter set there is expected to filter the groups it shows, the same way the flat
 * list's filter bar filters applications; see `GroupsListPage.tsx`'s own header for why that
 * is the opposite of what an EARLIER version of this comment said ("the group table sits
 * ABOVE the individual list, it does not replace or filter it") — that sentence described the
 * old, now-removed embedded design, where one filter bar drove two independent tables and
 * filtering one could not be allowed to silently filter the other.
 *
 * Sorted by code (locale-aware), so the table has a stable, predictable order rather than
 * "whatever order the rows happened to arrive in" — the same reasoning `deriveRounds` in
 * `listView.ts` already applies to round labels.
 */
export function deriveGroups(rows: readonly ApplicationSummary[]): GroupSummary[] {
  const byCode = new Map<string, ApplicationSummary[]>();
  for (const row of rows) {
    if (!hasGroupCode(row)) continue;
    const existing = byCode.get(row.groupLinkage);
    if (existing === undefined) {
      byCode.set(row.groupLinkage, [row]);
    } else {
      existing.push(row);
    }
  }
  return [...byCode.entries()]
    .map(([code, members]) => ({
      code,
      memberCount: members.length,
      totalRequested: sumRequested(members),
      sharedStart: earliest(members.map((member) => member.preferredStart)),
      sharedEnd: latest(members.map((member) => member.preferredEnd)),
      members,
    }))
    .sort((left, right) => left.code.localeCompare(right.code, "en-GB"));
}
