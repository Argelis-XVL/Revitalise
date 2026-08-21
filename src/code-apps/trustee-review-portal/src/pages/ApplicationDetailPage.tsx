/**
 * One application in full — WBS 6.3 and 6.4.
 *
 * FR-035, SDD US-012 AC-2 and AC-4. The panel order IS the reading order and the print
 * order: narrative, score, holiday details, staff recommendation, then the verdict.
 * Nothing here reorders content for print, so what a screen reader announces and what
 * comes off the printer are the same sequence (WCAG 1.3.2).
 */
import { Button, Spinner } from "@fluentui/react-components";
import type { CurrentUser } from "../dataverse/types";
import {
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
        <Button className={styles.tallTarget} onClick={onBack}>
          Back to the list
        </Button>
        <Button
          className={styles.tallTarget}
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
        <div className={styles.errorBox} role="alert">
          <h2 className={styles.panelHeading}>Could not load this case</h2>
          <p>{application.error.message}</p>
          <Button
            className={styles.tallTarget}
            onClick={() => {
              void application.refetch();
            }}
          >
            Try again
          </Button>
        </div>
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
