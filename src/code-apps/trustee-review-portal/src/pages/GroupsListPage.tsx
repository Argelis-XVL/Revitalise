/**
 * The group applications screen — EF-43 Δ5.
 * (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 50, "today" column, 2026-09-25)
 *
 * The reviewer's own words, in full, because they settle this screen's shape: "Create a
 * separate screen for group applications, that is a copy of the screen for individual
 * applications... The group applications screen should have the screen title, the filter bar
 * and the table with group applications." This file is exactly that — a structural copy of
 * `ApplicationsListPage.tsx`, not a new design: the same `<h1>` position, the same loading /
 * error / empty states, the same `ApplicationFilters` bar, the same `.actionRow` print
 * control pattern — with `GroupsTable` standing in for `ApplicationsTable` and no verdict
 * dialog, because a group row opens `GroupDetailPage` rather than recording a decision
 * directly.
 *
 * **The filter bar filters the SAME underlying `ApplicationSummary[]` the flat list reads,
 * BEFORE grouping — `deriveGroups(filteredRows)`, not `deriveGroups(allRows)`.** This is the
 * one place this file's behaviour is not a byte-for-byte copy of `ApplicationsListPage`'s,
 * and it is deliberate rather than an oversight: `domain/groups.ts`'s own comment on the OLD,
 * now-removed embedded design says filtering must NOT affect which groups exist, because that
 * table and the individual list's own filter bar shared one screen and one set of filter
 * state — filtering the list to answer one question must not silently also filter the group
 * table answering a different one. That constraint is gone now that each table has its OWN
 * filter bar and its own screen: a "Review round" filter set on the group screen should filter
 * GROUPS by round, the same way it filters applications on the individual screen, or the
 * control would be inert on this page while doing something on the other. `ApplicationFilters`
 * and `Filters` are reused whole rather than invented a second time (round, status, score
 * range, reference text all apply to the members feeding `deriveGroups`) — `rounds`/`statuses`
 * are still derived from the COMPLETE `allRows`, exactly as the individual screen does, so the
 * options offered never depend on the filter state that is about to narrow them.
 *
 * No sort control and no `ApplicationFilters`' "Application reference contains" field renamed:
 * `GroupsTable` itself has never offered column sorting (its own header says why — a handful
 * of groups does not need FR-034's machinery), and the text filter still matches an
 * application's own reference, which is the field `deriveGroups` reads to decide which of the
 * matching applications' groups appear — filtering to "REV-2026-010" shows the group that
 * application belongs to, not a group whose CODE contains that text.
 */
import { Spinner } from "@fluentui/react-components";
import { Button, Notice } from "../components/ds";
import { useMemo, useState } from "react";
import { deriveRounds, deriveStatuses, projectRows } from "../domain/listView";
import type { Filters } from "../domain/listView";
import { DEFAULT_SORT, EMPTY_FILTERS } from "../domain/listView";
import { deriveGroups } from "../domain/groups";
import type { GroupSummary } from "../domain/groups";
import { ApplicationFilters } from "../components/ApplicationFilters";
import { GroupsTable } from "../components/GroupsTable";
import { StateMessage } from "../components/Panel";
import { useApplications } from "../hooks/queries";
import { usePageTitle } from "../hooks/usePageTitle";
import styles from "../styles/app.module.css";

export function GroupsListPage({
  onOpenGroup,
}: {
  onOpenGroup: (group: GroupSummary) => void;
}) {
  usePageTitle("Group applications");
  const applications = useApplications();
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);

  // Same memoisation reasoning as `ApplicationsListPage`: a fresh `[]` every render would
  // make `rounds`/`statuses`/`groups` recompute on every keystroke in a filter box.
  const allRows = useMemo(() => applications.data ?? [], [applications.data]);
  const rounds = useMemo(() => deriveRounds(allRows), [allRows]);
  const statuses = useMemo(() => deriveStatuses(allRows), [allRows]);
  // `DEFAULT_SORT` is passed through only because `projectRows` needs a `SortState` to sort
  // by — this screen offers no sort control of its own (see this file's own header), so the
  // fixed default is a harmless, unobserved intermediate step before `deriveGroups`.
  const filteredRows = useMemo(
    () => projectRows(allRows, filters, DEFAULT_SORT),
    [allRows, filters],
  );
  const groups = useMemo(() => deriveGroups(filteredRows), [filteredRows]);
  // Distinct from `groups.length === 0`, which is also true when filters simply exclude
  // every group — this is "does the round have any groups AT ALL", read off the UNFILTERED
  // rows, so the two empty states below tell the trustee the right one of two different facts
  // (the same distinction `ApplicationsListPage` already draws between its own two empty
  // states — "no applications at all" vs. "filters match nothing").
  const anyGroupsExist = useMemo(() => deriveGroups(allRows).length > 0, [allRows]);

  const heading = <h1>Group applications</h1>;

  if (applications.isLoading) {
    return (
      <>
        {heading}
        <Spinner label="Loading the group applications…" labelPosition="below" />
      </>
    );
  }

  if (applications.isError) {
    return (
      <>
        {heading}
        {/* `role="alert"` passed in from here, same reasoning as `ApplicationsListPage`'s own
            error state (§8.5 point 6). */}
        <Notice tone="muted" role="alert" className={styles.errorBox}>
          <h2 className={styles.panelHeading}>Could not load the group applications</h2>
          <p>{applications.error.message}</p>
          <Button
            variant="primary"
            onClick={() => {
              void applications.refetch();
            }}
          >
            Try again
          </Button>
        </Notice>
      </>
    );
  }

  if (allRows.length === 0) {
    return (
      <>
        {heading}
        <StateMessage
          heading="No applications are available to you"
          explanation={
            "Nothing is currently marked as eligible for a review round that you can see, so " +
            "there is nothing to group. Applications appear here only once the process owner " +
            "has marked them eligible for the round."
          }
        />
      </>
    );
  }

  return (
    <>
      {heading}

      <ApplicationFilters
        filters={filters}
        rounds={rounds}
        statuses={statuses}
        onChange={setFilters}
      />

      <p aria-live="polite" className={styles.srOnly}>
        Showing {groups.length} group{groups.length === 1 ? "" : "s"}.
      </p>

      <div className={styles.actionRow} data-print="hide">
        <Button
          variant="secondary"
          onClick={() => {
            window.print();
          }}
        >
          Print this list
        </Button>
      </div>

      {groups.length === 0 ? (
        anyGroupsExist ? (
          <StateMessage
            heading="No groups match these filters"
            explanation="Clear or widen the filters above to see the groups under review again."
          />
        ) : (
          <StateMessage
            heading="No groups in this round"
            explanation={
              "Nothing currently visible to you carries a group code. Groups are formed " +
              "manually, so an application not yet linked to others is normal — it still " +
              "appears on the individual applications list."
            }
          />
        )
      ) : (
        <GroupsTable groups={groups} onOpen={onOpenGroup} />
      )}
    </>
  );
}
