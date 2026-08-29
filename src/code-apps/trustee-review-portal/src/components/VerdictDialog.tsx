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
 *
 * ## Revision 4 — the Close button becomes `ds/Button`; EVERY `Dialog*` PART STAYS
 *
 * TAD §2.1.4 is unusually blunt about this row and it is worth restating rather than
 * paraphrasing: a dialog is focus-trap, restore-focus, `aria-modal` and Escape handling, and
 * "hand-rolling one to match a mockup that contains no dialog would be the single largest
 * accessibility regression available in this pass". The supplied
 * `ui_kits/trustee-review-portal/` contains no dialog of any kind. So the only change here is
 * the Close button's own styling, plus the error box taking `ds/Notice`'s treatment with
 * `role="alert"` passed in from this call site (§8.5 point 6) — the same shape the list and
 * the detail screen use, so the app's three error boxes stay one visual idea.
 */
import {
  Dialog,
  DialogActions,
  DialogBody,
  DialogContent,
  DialogSurface,
  DialogTitle,
} from "@fluentui/react-components";
import { Button, Notice } from "./ds";
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
              <Notice tone="muted" role="alert" className={styles.errorBox}>
                <p>Could not load the review record for this application.</p>
                <p>{review.error.message}</p>
              </Notice>
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
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}
