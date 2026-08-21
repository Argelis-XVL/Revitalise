/**
 * Recording a verdict without leaving the summary list — SDD US-013 AC-3.
 *
 * Kevin's requirement is that a trustee who works from the numbers can "record my
 * verdict from there", meaning from the list. So the list gets the same verdict control
 * the detail screen has, in a modal — the same `VerdictSection`, the same slot
 * resolution, the same repository call. Two verdict paths with two implementations would
 * be two chances to write the wrong column.
 *
 * Fluent's `Dialog` supplies the focus trap, the Escape handler and the return of focus
 * to the trigger (WCAG 2.1.2, 2.4.3).
 */
import {
  Button,
  Dialog,
  DialogActions,
  DialogBody,
  DialogContent,
  DialogSurface,
  DialogTitle,
} from "@fluentui/react-components";
import type { ApplicationSummary, CurrentUser } from "../dataverse/types";
import { useReview } from "../hooks/queries";
import styles from "../styles/app.module.css";
import { VerdictSection } from "./VerdictSection";

export function VerdictDialog({
  application,
  user,
  onClose,
}: {
  application: ApplicationSummary;
  user: CurrentUser;
  onClose: () => void;
}) {
  const review = useReview(application.id);

  return (
    <Dialog
      open
      modalType="modal"
      onOpenChange={(_event, data) => {
        if (!data.open) onClose();
      }}
    >
      <DialogSurface data-print="hide">
        <DialogBody>
          <DialogTitle>Record a verdict for {application.reference}</DialogTitle>
          <DialogContent>
            {review.isError ? (
              <div className={styles.errorBox} role="alert">
                <p>Could not load the review record for this application.</p>
                <p>{review.error.message}</p>
              </div>
            ) : (
              <VerdictSection
                application={application}
                review={review.data ?? null}
                user={user}
                loading={review.isLoading}
              />
            )}
          </DialogContent>
          <DialogActions>
            <Button className={styles.tallTarget} onClick={onClose}>
              Close
            </Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}
