/**
 * One application in full — WBS 6.3 and 6.4.
 *
 * FR-035 (Amendment A-05 wording), SDD US-012 AC-2, AC-4, AC-7, AC-8, AC-9. The panel order
 * IS the reading order and the print order: narrative, score, holiday details, care-support
 * description (structured pair, applicant-type context and the redacted free text),
 * financial eligibility, condition and circumstance, helper/referee/emergency contact, staff
 * recommendation, then the verdict. Nothing here reorders content for print, so what a
 * screen reader announces and what comes off the printer are the same sequence (WCAG
 * 1.3.2). Corrected 2026-08-27, twice now in the same pass — this comment had fallen out of
 * step with the panel list below it before Amendment A-05 landed too
 * (`stale-comment-contradicts-source`, IMP-0330's class), so it is stated in full order here
 * rather than patched a third time later.
 *
 * ## Revision 4 — buttons and the error box; `Spinner` and the panel order stay
 *
 * TAD §2.1.4: the three Fluent `Button`s become `ds/Button` — **Back to the list** and
 * **Print this case** are `secondary` (the supplied `ApplicationDetail.jsx:23-24` shows both
 * that way, and neither is the screen's purpose), **Try again** is `primary` because it is
 * the one action the error state exists to offer. Fluent's `Spinner` stays; the design system
 * ships none.
 *
 * The error box renders through `ds/Notice`'s treatment WITH `role="alert"` PASSED IN FROM
 * HERE — the same §8.5 point 6 decision the applications list makes, applied to the second
 * of the app's three error boxes so the two do not diverge visually. Its `<h2>` is a child
 * rather than `Notice`'s `title` prop, which renders a `<p>`.
 *
 * ## Revision 9 (2026-09-01, wbs:6.9) — reviewer item 4, the button row's own class
 *
 * "Back to the list" / "Print this case" moved off `.verdictActions` and onto `.actionRow`.
 * The two buttons, their variants and their order are all unchanged; what changed is that the
 * row now takes the persistent nav bar's own gutter and alignment instead of the verdict
 * form's, which is why it rendered out of line under "Round overview" / "Applications list".
 * `app.module.css`'s `.actionRow` carries the measurement.
 *
 * ## Revision 11 (2026-09-02, wbs:6.8) — reviewer items 6, 7 and 8, which are one change to
 * this screen's opening three elements
 *
 * **Item 6 — the `<h1>` renders FIRST.** "Application REV-2026-XXXX" was pushed down the page
 * by the `.actionRow` above it, so the title's position moved with whatever that row happened
 * to contain. It is now the first thing in the fragment, which is the position `LandingPage`
 * has always used and the one `ApplicationsListPage` was moved to in Revision 10 (`App.tsx`'s
 * own Revision 10 section is the same fix on the third screen). All three screens now open
 * `<h1>` → controls, directly under the persistent nav bar.
 *
 * **Item 7 — "Back to the list" is REMOVED, AND THAT REVERSES A RECORDED DECISION.** `App.tsx`'s
 * Revision 7 header states, twice, that ADR-040's persistent nav bar "does **not** replace
 * `ApplicationDetailPage`'s own 'back to the list' — that stays as a second, faster route back
 * from the one screen deepest in the flow." The reviewer has now asked for it removed as
 * redundant with the bar's own "Applications list" tab. That is their call about their own
 * product, and it is recorded here as a REVERSAL — the same way Revision 9's item 5 recorded its
 * reversal of ADR-040's "disabled, not hidden" — rather than left as a silent contradiction
 * between `App.tsx`'s header and this file. `development-agent` carries it into the Dev Summary
 * for the TAD to amend.
 *
 * **What it costs, stated so it is not discovered later:** one click. The route back is the nav
 * bar's "Applications list" tab, which is on screen at all times, carries `aria-current`, and is
 * two tab stops from the top of `<main>`. No accessible behaviour rests on the removed control —
 * it duplicated a route rather than providing one — and the screen keeps exactly one `<h1>` and
 * one action row either way.
 *
 * **The `onBack` PROP IS REMOVED ENTIRELY, not left unused.** It was this component's only
 * consumer, so leaving it would be an unused destructured binding — `@typescript-eslint`'s
 * `no-unused-vars` is on for this project and would flag it — and, worse, a prop a caller must
 * still supply for a behaviour that no longer exists reads as a live contract. `App.tsx`'s own
 * call site drops the `onBack={…}` closure in the same change; nothing else passed one.
 *
 * **Item 8 — "Print this case" moves under the title**, as the whole of a single-button
 * `.actionRow`. That class is unchanged and still shares `.viewNav`'s gutter (Revision 9 item
 * 4); it simply has one child now instead of two.
 */
import { Spinner } from "@fluentui/react-components";
import { Button, Notice } from "../components/ds";
import type { CurrentUser } from "../dataverse/types";
import {
  CareSupportPanel,
  ConditionProfilePanel,
  FinancialEligibilityPanel,
  HelperRefereeContactPanel,
  HolidayPanel,
  NarrativePanel,
  ScorePanel,
  StaffRecommendationPanel,
} from "../components/CasePanels";
import { StateMessage } from "../components/Panel";
import { VerdictSection } from "../components/VerdictSection";
import { useApplication, useReview } from "../hooks/queries";
import { usePageTitle } from "../hooks/usePageTitle";
import styles from "../styles/app.module.css";

export function ApplicationDetailPage({
  applicationId,
  fallbackReference,
  user,
}: {
  applicationId: string;
  /** The reference already known from the list, so the heading is right before the fetch lands. */
  fallbackReference: string;
  user: CurrentUser;
}) {
  const application = useApplication(applicationId);
  const review = useReview(applicationId);
  const reference = application.data?.reference ?? fallbackReference;
  usePageTitle(`Application ${reference}`);

  return (
    <>
      {/* Item 6: the title is FIRST, so its position under the nav bar does not move with
          whatever the action row below it happens to contain. */}
      <h1>Application {reference}</h1>

      {/* Items 7 and 8: one button, not two. "Back to the list" is removed as redundant with
          the persistent nav bar's "Applications list" tab — a documented reversal of `App.tsx`'s
          Revision 7 decision, see this file's Revision 11 header. */}
      <div className={styles.actionRow} data-print="hide">
        <Button
          variant="secondary"
          onClick={() => {
            // FR-039 / US-014 AC-3.
            window.print();
          }}
        >
          Print this case
        </Button>
      </div>

      {application.isLoading ? (
        <Spinner label="Loading the case…" labelPosition="below" />
      ) : application.isError ? (
        <Notice tone="muted" role="alert" className={styles.errorBox}>
          <h2 className={styles.panelHeading}>Could not load this case</h2>
          <p>{application.error.message}</p>
          <Button
            variant="primary"
            onClick={() => {
              void application.refetch();
            }}
          >
            Try again
          </Button>
        </Notice>
      ) : application.data === null || application.data === undefined ? (
        // The fail-closed conjunction on the direct-read path (FR-038): an application
        // that is not eligible for the round is not readable even by id.
        <StateMessage
          heading="This application is not available to you"
          explanation={
            "It is not marked as eligible for a review round you can see. That may be " +
            "because the round has closed, or because it was never released to the panel."
          }
        />
      ) : (
        <>
          <NarrativePanel detail={application.data} />
          <ScorePanel detail={application.data} />
          <HolidayPanel detail={application.data} />
          <CareSupportPanel detail={application.data} />
          <FinancialEligibilityPanel detail={application.data} />
          <ConditionProfilePanel detail={application.data} />
          <HelperRefereeContactPanel detail={application.data} />
          <StaffRecommendationPanel
            staffRecommendation={review.data?.staffRecommendation ?? null}
            panelDate={review.data?.panelDate ?? null}
            loading={review.isLoading}
          />
          <VerdictSection
            application={application.data}
            review={review.data ?? null}
            user={user}
            loading={review.isLoading}
          />
        </>
      )}
    </>
  );
}
