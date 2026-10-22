/**
 * CARD APP (Design 2.0 Revision 2, TAD trustee-portal-design-2 §13.3, WI-0091):
 * `ApplicationsList.jsx` lines 92-111 — eyebrow and title, the filters card, the print action
 * row, then the table or the state message; "Record verdict" opens the dialog in place.
 *
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
 *
 * ## Revision 9 (2026-09-01, wbs:6.9) — reviewer items 4 and 6 reach this screen too
 *
 * The "Print this list" control moved off `.verdictActions` and onto `.actionRow`, the same
 * class the detail screen's pair now uses: the reviewer named the DETAIL screen's buttons, but
 * this row sits under the identical nav bar with the identical mismatch, and fixing one and
 * not the other is how two screens drift apart. This screen is also item 6's named example —
 * nav bar → filters → print control → results caption → table — and every step of that
 * sequence now sits on `app.module.css`'s two-token rhythm. No markup below changed for item
 * 6; the spacing is entirely in the stylesheet, which is what keeps it consistent.
 *
 * ## EF-43 Δ5 — the group table is REMOVED from this screen entirely
 * (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 50, "today" column, 2026-09-25)
 *
 * `GroupsTable`, the `groups` memo (`deriveGroups(allRows)`) and the `onOpenGroup` prop that
 * used to sit above the filter bar are all gone. The reviewer's own words: "the group
 * applications table should be removed from the application list screen so that screen only
 * has individual applications" — reported alongside "not enough white space" between that
 * table and the filter bar below it, and "weird to have a table, a set of filters and then
 * another table". The group table now has its own screen, `pages/GroupsListPage.tsx`, reached
 * from the nav bar's own "Group applications" tab (`App.tsx`'s "EF-43 Δ5" header) — this page
 * no longer has any route to it at all, which is the fix rather than a regression.
 *
 * ## SDD A-14, FR-116/FR-117 — own verdict on the button, and what awaits it (ADR-086)
 *
 * One review read serves the whole list (`useReviewIndex`, chunks of 25 ids), and each row's
 * review is chosen by `currentReviewFor` — the same function the dialog's own read uses. The
 * button shows the trustee's own verdict (`ApplicationsTable`). Above the table a polite status
 * line counts the applications awaiting the trustee's verdict over EVERY row loaded, before the
 * trustee's own filters; the "Show only applications awaiting my verdict" filter ANDs with the
 * others and the existing "N of M shown" caption reports the result. Loading: "Counting your
 * verdicts…", filter disabled. Failed: "Your verdict status could not be loaded." — never a
 * number — filter disabled, and every button reads Record verdict (the dialog does its own
 * read). User not identified: no line, no filter; the identity message stands.
 */
import { Spinner } from "@fluentui/react-components";
import { Button, Notice } from "../components/ds";
import { useMemo, useState } from "react";
import { useToast } from "../app/toast";
import type { ApplicationSummary, CurrentUser } from "../dataverse/types";
import {
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
import { useApplications, useReviewIndex } from "../hooks/queries";
import { currentReviewFor } from "../dataverse/currentReview";
import { countAwaiting, ownVerdictState } from "../domain/ownVerdict";
import type { OwnVerdictState } from "../domain/ownVerdict";
import type { AwaitingFilterAvailability } from "../components/ApplicationFilters";
import { usePageTitle } from "../hooks/usePageTitle";
import styles from "../styles/app.module.css";
import { Eyebrow } from "../components/Panel";
import { roundEyebrow } from "../cards/sentences";

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

  // ADR-086: one review read for every loaded row; the trustee's own verdict per row from it.
  const userKnown = user.systemUserId !== null;
  const applicationIds = useMemo(() => (userKnown ? allRows.map((row) => row.id) : []), [allRows, userKnown]);
  const reviewIndex = useReviewIndex(applicationIds);
  const stateById = useMemo(() => {
    const map = new Map<string, OwnVerdictState>();
    if (reviewIndex.data === undefined) return null;
    for (const row of allRows) {
      map.set(row.id, ownVerdictState(currentReviewFor(row.id, reviewIndex.data), user));
    }
    return map;
  }, [allRows, reviewIndex.data, user]);
  const verdictStateFor = (row: ApplicationSummary): OwnVerdictState =>
    stateById?.get(row.id) ?? { kind: "none" };
  const isAwaiting = useMemo(
    () =>
      stateById === null
        ? undefined
        : (row: ApplicationSummary) => stateById.get(row.id)?.kind === "awaiting",
    [stateById],
  );
  const awaitingCount = stateById === null ? null : countAwaiting([...stateById.values()]);
  const awaitingAvailability: AwaitingFilterAvailability = !userKnown
    ? "hidden"
    : stateById === null
      ? "disabled"
      : "available";

  const rows = useMemo(
    () => projectRows(allRows, filters, sort, isAwaiting),
    [allRows, filters, sort, isAwaiting],
  );

  // Revision 10 (2026-09-02, wbs:6.8), reviewer item 6 — this screen's own `<h1>`, moved here
  // from the shell's `<header>` (`App.tsx`). It now sits under the persistent nav bar, in the
  // same position `LandingPage` and `ApplicationDetailPage` already render theirs, and it is
  // repeated in EVERY early-return branch below so the title is on screen in every state this
  // page can be in — exactly as it was when the shell rendered it unconditionally.
  const heading = <h1>Applications under review</h1>;

  if (applications.isLoading) {
    return (
      <>
        {heading}
        <Spinner label="Loading the applications under review…" labelPosition="below" />
      </>
    );
  }

  if (applications.isError) {
    // Toast plus an in-page message: the toast is the notification, the panel is what a
    // trustee returning to the tab an hour later still sees (code-apps.md → Error
    // Handling; never a blank screen).
    return (
      <>
        {heading}
        {/* `role="alert"` comes FROM HERE, not from the component (§8.5 point 6). `.errorBox`
          adds only the red boundary that keeps a failure visually distinct from a note; the
          fill, radius and padding are `Notice`'s, so the two classes declare no property in
          common and the result does not depend on which stylesheet the bundler emits first. */}
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
            "Nothing is currently marked as eligible for a review round that you can see. " +
            "Applications appear here only once the process owner has marked them eligible " +
            "for the round, so an empty list is normal between panels."
          }
        />
      </>
    );
  }

  const caption =
    rows.length === allRows.length
      ? `${String(allRows.length)} applications under review.`
      : `${String(rows.length)} of ${String(allRows.length)} applications shown by the current filters.`;

  const eyebrow = roundEyebrow(filters.round ?? "", allRows);
  return (
    <>
      {/* The "Round {name}" eyebrow above the title (ADR-062, TAD §13.7), from the filter or the
          loaded rows — no new query. */}
      <div className={styles.titleGroup}>
        {eyebrow === null ? null : <Eyebrow>{eyebrow}</Eyebrow>}
        {heading}
      </div>

      <ApplicationFilters
        filters={filters}
        rounds={rounds}
        statuses={statuses}
        onChange={setFilters}
        awaiting={awaitingAvailability}
      />

      {/* FR-117: counted over every row loaded, before the trustee's own filters. Polite, so a
          count that changes after a save is announced without interrupting. Never a number
          when the index could not be read. */}
      {!userKnown ? null : (
        <p role="status" aria-live="polite" className={styles.awaitingStatus}>
          {reviewIndex.isError
            ? "Your verdict status could not be loaded."
            : awaitingCount === null
              ? "Counting your verdicts…"
              : awaitingCount === 0
                ? "None awaiting your verdict"
                : `${String(awaitingCount)} awaiting your verdict`}
        </p>
      )}

      {/* Announced, not just drawn: a filter change that silently reduces the list is
          invisible to a screen-reader user (WCAG 4.1.3). Worded differently from the
          table's own <caption> on purpose — the caption describes the table when it is
          read, this announces the CHANGE, and identical text in two places is read
          twice. */}
      <p aria-live="polite" className={styles.srOnly}>
        Showing {rows.length} of {allRows.length} applications.
      </p>

      <div className={styles.actionRow} data-print="hide">
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
          verdictStateFor={verdictStateFor}
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
