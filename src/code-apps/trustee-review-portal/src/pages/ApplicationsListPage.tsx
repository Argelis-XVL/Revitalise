/**
 * The applications summary list — WBS 6.2.
 *
 * FR-034, SDD US-012 AC-1, US-013 AC-1/AC-2/AC-3/AC-4. A trustee who prefers a
 * data-only view can do the whole job from this screen: read the numbers, sort and
 * filter across the complete round, record a verdict, and print it.
 *
 * ## Revision 4 — the four things that changed, and the eight that could not (TAD §2.2)
 *
 * Changed: the filter controls and the action buttons are the design system's, the table's
 * rule and type take its treatment (all of that is in the two components below and in
 * `app.module.css`), and the error box plus the two state messages render through
 * `ds/Notice`'s visual treatment.
 *
 * NOT changed, because §2.2.1 lists each of these as a behaviour the supplied mockup does
 * not have and this screen must not lose:
 *
 *   - **Filtering and sorting are client-side over the COMPLETE round.** `domain/listView.ts`
 *     is untouched and every function in it keeps its signature; the four `useMemo`s below
 *     are byte-identical to before this pass. **There is no paging control in the redesign,
 *     because there is no paging** — a server-paged sort sorts a page, which is a different
 *     and wrong behaviour (SDD US-013 AC-2).
 *   - **The 500-row cap fails loudly, through the generic error state, with no special-case
 *     branch.** Its message tells the trustee the list is NOT COMPLETE, which is the whole
 *     point, so the error state must not be "improved" into something implying a retry will
 *     fix it.
 *   - **The loading state keeps Fluent's `Spinner`** — the design system ships none (§2.1.4).
 *   - **The error state keeps `role="alert"`, its `<h2>`, the error's own message, its Try
 *     again button and the toast beside it.** `ds/Notice` supplies NO role at all, so the
 *     role is passed in from here (§8.5 point 6): an error a screen reader is never told
 *     about is a worse outcome than an unstyled one. The `<h2>` is passed as a child rather
 *     than through `Notice`'s `title` prop, which renders a `<p>` — the heading level is part
 *     of what §2.2.1 says survives.
 *   - **TWO distinct empty states stay distinct**, and both keep `role="note"` (the
 *     `StateMessage` default). Collapsing them tells a trustee their filters are wrong when
 *     the round is empty, or the reverse.
 *   - **The live region and the caption that switches wording with it** both stay.
 *   - **The print control keeps `data-print="hide"`** and the invariant in its comment.
 */
import { Spinner } from "@fluentui/react-components";
import { Button, Notice } from "../components/ds";
import { useMemo, useState } from "react";
import { useToast } from "../app/toast";
import type { ApplicationSummary, CurrentUser } from "../dataverse/types";
import {
  deriveRegions,
  deriveRounds,
  deriveStatuses,
  nextSort,
  projectRows,
} from "../domain/listView";
import type { Filters, SortKey, SortState } from "../domain/listView";
import { DEFAULT_SORT, EMPTY_FILTERS } from "../domain/listView";
import { ApplicationFilters } from "../components/ApplicationFilters";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { StateMessage } from "../components/Panel";
import { VerdictDialog } from "../components/VerdictDialog";
import { useApplications } from "../hooks/queries";
import { usePageTitle } from "../hooks/usePageTitle";
import styles from "../styles/app.module.css";

export function ApplicationsListPage({
  user,
  onOpenApplication,
}: {
  user: CurrentUser;
  onOpenApplication: (application: ApplicationSummary) => void;
}) {
  usePageTitle("Applications under review");
  const toast = useToast();
  const applications = useApplications();
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [sort, setSort] = useState<SortState>(DEFAULT_SORT);
  const [verdictFor, setVerdictFor] = useState<ApplicationSummary | null>(null);

  // Memoised, not `applications.data ?? []` inline: a fresh [] on every render makes it
  // a new dependency every render, so the three useMemos below would recompute the
  // rounds, the statuses and the whole sort on every keystroke in a filter box.
  const allRows = useMemo(() => applications.data ?? [], [applications.data]);
  const rounds = useMemo(() => deriveRounds(allRows), [allRows]);
  const statuses = useMemo(() => deriveStatuses(allRows), [allRows]);
  const regions = useMemo(() => deriveRegions(allRows), [allRows]);
  const rows = useMemo(() => projectRows(allRows, filters, sort), [allRows, filters, sort]);

  if (applications.isLoading) {
    return <Spinner label="Loading the applications under review…" labelPosition="below" />;
  }

  if (applications.isError) {
    // Toast plus an in-page message: the toast is the notification, the panel is what a
    // trustee returning to the tab an hour later still sees (code-apps.md → Error
    // Handling; never a blank screen).
    return (
      // `role="alert"` comes FROM HERE, not from the component (§8.5 point 6). `.errorBox`
      // adds only the red boundary that keeps a failure visually distinct from a note; the
      // fill, radius and padding are `Notice`'s, so the two classes declare no property in
      // common and the result does not depend on which stylesheet the bundler emits first.
      <Notice tone="muted" role="alert" className={styles.errorBox}>
        <h2 className={styles.panelHeading}>Could not load the applications</h2>
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
    );
  }

  if (allRows.length === 0) {
    return (
      <StateMessage
        heading="No applications are available to you"
        explanation={
          "Nothing is currently marked as eligible for a review round that you can see. " +
          "Applications appear here only once the process owner has marked them eligible " +
          "for the round, so an empty list is normal between panels."
        }
      />
    );
  }

  const caption =
    rows.length === allRows.length
      ? `${String(allRows.length)} applications under review.`
      : `${String(rows.length)} of ${String(allRows.length)} applications shown by the current filters.`;

  return (
    <>
      <ApplicationFilters
        filters={filters}
        rounds={rounds}
        statuses={statuses}
        regions={regions}
        onChange={setFilters}
      />

      {/* Announced, not just drawn: a filter change that silently reduces the list is
          invisible to a screen-reader user (WCAG 4.1.3). Worded differently from the
          table's own <caption> on purpose — the caption describes the table when it is
          read, this announces the CHANGE, and identical text in two places is read
          twice. */}
      <p aria-live="polite" className={styles.srOnly}>
        Showing {rows.length} of {allRows.length} applications.
      </p>

      <div className={styles.verdictActions} data-print="hide">
        {/* §2.2.2 item 2 names this control `secondary`. */}
        <Button
          variant="secondary"
          onClick={() => {
            // FR-039 / US-013 AC-4. The print path renders THIS DOM, resolved through the
            // same repository call — never a wider query. See styles/print.css.
            window.print();
          }}
        >
          Print this list
        </Button>
      </div>

      {rows.length === 0 ? (
        <StateMessage
          heading="No applications match these filters"
          explanation="Clear or widen the filters above to see the applications under review again."
        />
      ) : (
        <ApplicationsTable
          rows={rows}
          sort={sort}
          caption={caption}
          onSort={(key: SortKey) => {
            setSort((current) => nextSort(current, key));
          }}
          onOpen={onOpenApplication}
          onRecordVerdict={(application) => {
            if (user.systemUserId === null) {
              toast.showError(
                "Cannot record a verdict yet",
                user.unresolvedReason ??
                  "The portal could not confirm which trustee you are signed in as.",
              );
            }
            // The dialog is opened either way: it explains the problem in place rather
            // than leaving the trustee with a toast and no context.
            setVerdictFor(application);
          }}
        />
      )}

      {verdictFor === null ? null : (
        <VerdictDialog
          application={verdictFor}
          user={user}
          onClose={() => {
            setVerdictFor(null);
          }}
        />
      )}
    </>
  );
}
