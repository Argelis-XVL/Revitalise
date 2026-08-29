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
  onBack,
}: {
  applicationId: string;
  /** The reference already known from the list, so the heading is right before the fetch lands. */
  fallbackReference: string;
  user: CurrentUser;
  onBack: () => void;
}) {
  const application = useApplication(applicationId);
  const review = useReview(applicationId);
  const reference = application.data?.reference ?? fallbackReference;
  usePageTitle(`Application ${reference}`);

  return (
    <>
      <div className={styles.verdictActions} data-print="hide">
        <Button variant="secondary" onClick={onBack}>
          Back to the list
        </Button>
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

      <h1>Application {reference}</h1>

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
