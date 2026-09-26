/**
 * The group applications table (EF-43) — this app's second, entity-level table, rendered on
 * its own screen, `pages/GroupsListPage.tsx`.
 *
 * **EF-43 Δ5 (2026-09-25): no longer stacked above `ApplicationsListPage`'s own list.** It
 * used to render there, above that screen's filter bar and individual table; the reviewer's
 * live check found the stack confusing and asked for a separate screen instead (see
 * `GroupsListPage.tsx`'s own header for the full reasoning and the exact words). This
 * component's own markup and props are UNCHANGED by that move — same `groups`/`onOpen` props,
 * same table — only which page renders it changed.
 *
 * A native `<table>`, the same choice `ApplicationsTable.tsx` documents at length and for the
 * same reason: `<th scope="col">`/`<th scope="row">` give a screen reader row/column
 * announcement for free, and this table's rows are exactly as clickable-to-navigate as that
 * one's — same `.rowLink` button pattern, same reasoning against an `<a href="#">` regression.
 *
 * The field list is fixed and small by the plan's own decision (`domain/groups.ts`'s header):
 * group code, member count, group total requested, and the shared dates. No sort controls —
 * unlike the individual list, this table is not FR-034's sortable/filterable surface and the
 * plan names no such requirement for it; a handful of groups does not need one. (`GroupsListPage`
 * does offer a filter BAR, reused from the individual screen — that narrows which rows feed
 * `deriveGroups` before this component ever renders, which is a different thing from this
 * table sorting or filtering its own columns.)
 */
import { formatAmount, formatDateRange } from "../domain/format";
import type { GroupSummary } from "../domain/groups";
import styles from "../styles/app.module.css";

export function GroupsTable({
  groups,
  onOpen,
}: {
  groups: readonly GroupSummary[];
  onOpen: (group: GroupSummary) => void;
}) {
  return (
    <div className={styles.tableScroll}>
      <table className={styles.table}>
        <caption>
          {groups.length} group{groups.length === 1 ? "" : "s"} of linked applications.
        </caption>
        <thead>
          <tr>
            <th scope="col">
              <span className={styles.plainHeader}>Group</span>
            </th>
            <th scope="col" className={styles.numeric}>
              <span className={styles.plainHeader}>Members</span>
            </th>
            <th scope="col" className={styles.numeric}>
              <span className={styles.plainHeader}>Group total requested</span>
            </th>
            <th scope="col">
              <span className={styles.plainHeader}>Shared dates</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {groups.map((group) => (
            <tr key={group.code}>
              <th scope="row">
                <button
                  type="button"
                  className={styles.rowLink}
                  aria-label={`Group ${group.code}, open the group's applications`}
                  onClick={() => {
                    onOpen(group);
                  }}
                >
                  {group.code}
                </button>
              </th>
              <td className={styles.numeric}>{group.memberCount}</td>
              <td className={styles.numeric}>{formatAmount(group.totalRequested)}</td>
              <td>{formatDateRange(group.sharedStart, group.sharedEnd)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
