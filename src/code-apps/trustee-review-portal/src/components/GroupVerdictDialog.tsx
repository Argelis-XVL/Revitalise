/**
 * Recording one verdict for a whole group — portal TAD trustee-portal-design-2 ADR-087 (SDD A-14,
 * FR-118, FR-119; US-012 AC-12; wbs:6.3; WI-0148).
 *
 * Choose → preview → confirm → result, in one Fluent dialog (focus trap, Escape, focus return —
 * the same primitive as `VerdictDialog`, WCAG 2.1.2 / 2.4.3).
 *
 *   - **Choose.** Approve, Defer or Reject, and notes. Notes follow the single dialog's EF-05 rule
 *     (required for Defer and Reject, optional for Approve), checked BEFORE anything is written,
 *     so a missing note records nothing. The same notes go to every member's review row.
 *   - **Preview.** From the review index the group page already holds: "Approve will be recorded
 *     on 3 of 4 applications. 1 skipped: …". The confirm button reads "Record Approve on 3
 *     applications" and is disabled at zero. Cancel writes nothing.
 *   - **Confirm.** The member reviews are read again, fresh (not from cache), and re-planned
 *     (`replanForConfirm`); then one ordinary save per target, one at a time, while the dialog
 *     shows "Recording 2 of 3…" and cannot be dismissed.
 *   - **Result.** FR-119's sentence, then one line per member. The review index and every
 *     member's per-application review are invalidated, so the buttons show the new verdict.
 */
import {
  Dialog,
  DialogActions,
  DialogBody,
  DialogContent,
  DialogSurface,
  DialogTitle,
  Field,
  Radio,
  RadioGroup,
  Spinner,
  Textarea,
} from "@fluentui/react-components";
import { useQueryClient } from "@tanstack/react-query";
import { useId, useState } from "react";
import { useRepository } from "../app/RepositoryContext";
import { VERDICT_NOTES_MAX_LENGTH, VERDICT_VALUES } from "../dataverse/schema";
import type { ApplicationSummary, CurrentUser, ReviewRow } from "../dataverse/types";
import {
  confirmLabel,
  executeGroupVerdict,
  groupNotesProblem,
  notesToSend,
  outcomeLine,
  planGroupVerdict,
  previewSentence,
  replanForConfirm,
  resultSentence,
} from "../domain/groupVerdict";
import type { GroupVerdictOutcome } from "../domain/groupVerdict";
import { queryKeys } from "../hooks/queries";
import styles from "../styles/app.module.css";
import { Button, Notice } from "./ds";

const VERDICT_OPTIONS = [
  { value: VERDICT_VALUES.approve, label: "Approve" },
  { value: VERDICT_VALUES.defer, label: "Defer" },
  { value: VERDICT_VALUES.reject, label: "Reject" },
];

type Phase =
  | { kind: "choose" }
  | { kind: "running"; done: number; total: number }
  | { kind: "result"; outcomes: GroupVerdictOutcome[] }
  | { kind: "error"; message: string };

export function GroupVerdictDialog({
  groupCode,
  members,
  reviewRows,
  user,
  onClose,
}: {
  groupCode: string;
  members: readonly ApplicationSummary[];
  /** The group page's review index — the preview's input. */
  reviewRows: readonly ReviewRow[];
  user: CurrentUser;
  onClose: () => void;
}) {
  const repository = useRepository();
  const queryClient = useQueryClient();
  const [verdict, setVerdict] = useState<number | null>(null);
  const [notes, setNotes] = useState("");
  const [showValidation, setShowValidation] = useState(false);
  const [phase, setPhase] = useState<Phase>({ kind: "choose" });
  const notesId = useId();
  const countId = useId();
  const groupLabelId = useId();

  const preview = planGroupVerdict(members, reviewRows, user);
  const notesProblem = verdict === null ? null : groupNotesProblem(verdict, notes);
  const notesRequired = verdict === VERDICT_VALUES.defer || verdict === VERDICT_VALUES.reject;
  const running = phase.kind === "running";

  async function confirm() {
    if (verdict === null || notesProblem !== null) {
      // EF-05 before any write: a missing note records nothing.
      setShowValidation(true);
      return;
    }
    setPhase({ kind: "running", done: 0, total: preview.targets.length });
    try {
      // ADR-087 point 4: read again, fresh — straight from the repository, not the cache.
      const fresh = await repository.listReviewsForApplications(members.map((member) => member.id));
      const plan = replanForConfirm(preview, members, fresh, user);
      setPhase({ kind: "running", done: 0, total: plan.targets.length });
      const outcomes = await executeGroupVerdict(
        members,
        plan,
        verdict,
        notesToSend(notes),
        (input) => repository.saveVerdict(input),
        (done, total) => {
          setPhase({ kind: "running", done, total });
        },
      );
      setPhase({ kind: "result", outcomes });
    } catch (error) {
      // Only the fresh read can land here: a failed WRITE is a per-member outcome, never thrown.
      setPhase({
        kind: "error",
        message: error instanceof Error ? error.message : String(error),
      });
    } finally {
      await queryClient.invalidateQueries({ queryKey: queryKeys.reviewIndexRoot });
      await Promise.all(
        members.map((member) => queryClient.invalidateQueries({ queryKey: queryKeys.review(member.id) })),
      );
    }
  }

  return (
    <Dialog
      open
      modalType="modal"
      onOpenChange={(_event, data) => {
        // Not dismissable while writes run (ADR-087 point 5).
        if (!data.open && !running) onClose();
      }}
    >
      <DialogSurface data-print="hide">
        <DialogBody>
          <DialogTitle>Record a verdict for the whole group {groupCode}</DialogTitle>
          <DialogContent>
            {phase.kind === "running" ? (
              <div role="status" aria-live="polite">
                <Spinner
                  size="tiny"
                  labelPosition="after"
                  label={`Recording ${String(Math.max(phase.done, 1))} of ${String(phase.total)}…`}
                />
              </div>
            ) : phase.kind === "result" ? (
              <div role="status" aria-live="polite">
                <p className={styles.awaitingStatus}>{resultSentence(phase.outcomes)}</p>
                <ul>
                  {phase.outcomes.map((outcome) => (
                    <li key={outcome.application.id}>{outcomeLine(outcome)}</li>
                  ))}
                </ul>
              </div>
            ) : phase.kind === "error" ? (
              <Notice tone="muted" role="alert" className={styles.errorBox}>
                <p>Nothing was recorded: the review records could not be read again before writing.</p>
                <p>{phase.message}</p>
              </Notice>
            ) : (
              <form
                className={styles.verdictForm}
                onSubmit={(event) => {
                  event.preventDefault();
                  void confirm();
                }}
              >
                <p className={styles.hint}>
                  Your verdict is recorded in your own trustee slot on each application in this group,
                  and nowhere else. The same notes are saved on every application.
                </p>
                <Field
                  label={{ children: "Your verdict for the group", required: true }}
                  validationState={showValidation && verdict === null ? "error" : "none"}
                  validationMessage={
                    showValidation && verdict === null ? "Choose Approve, Defer or Reject before recording." : undefined
                  }
                >
                  <RadioGroup
                    aria-labelledby={groupLabelId}
                    value={verdict === null ? "" : String(verdict)}
                    onChange={(_event, data) => {
                      setVerdict(Number(data.value));
                      setShowValidation(false);
                    }}
                  >
                    <span id={groupLabelId} className={styles.srOnly}>
                      Verdict for every application in group {groupCode}, required
                    </span>
                    {VERDICT_OPTIONS.map((option) => (
                      <Radio key={option.value} value={String(option.value)} label={option.label} className={styles.tallTarget} />
                    ))}
                  </RadioGroup>
                </Field>
                <Field
                  className={styles.filterField}
                  label={{ htmlFor: notesId, children: notesRequired ? "Notes" : "Notes (optional)", required: notesRequired }}
                  validationState={showValidation && notesProblem !== null ? "error" : "none"}
                  validationMessage={
                    showValidation && notesProblem === "required"
                      ? "Notes are required when the verdict is Defer or Reject."
                      : showValidation && notesProblem === "too-long"
                        ? `Notes are limited to ${String(VERDICT_NOTES_MAX_LENGTH)} characters.`
                        : undefined
                  }
                >
                  <Textarea
                    id={notesId}
                    value={notes}
                    maxLength={VERDICT_NOTES_MAX_LENGTH}
                    resize="vertical"
                    aria-describedby={countId}
                    onChange={(_event, data) => {
                      setNotes(data.value);
                      if (data.value.trim() !== "") setShowValidation(false);
                    }}
                  />
                  <p id={countId} className={styles.hint} aria-live="polite">
                    {VERDICT_NOTES_MAX_LENGTH - notes.length} of {VERDICT_NOTES_MAX_LENGTH} characters remaining.
                  </p>
                </Field>
                {verdict === null ? null : (
                  <p role="status" aria-live="polite" className={styles.hint}>
                    {previewSentence(preview, verdict)}
                  </p>
                )}
                <div className={styles.verdictActions}>
                  <Button variant="primary" type="submit" disabled={verdict !== null && preview.targets.length === 0}>
                    {verdict === null ? "Record verdict" : confirmLabel(preview, verdict)}
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
          <DialogActions>
            {running ? null : (
              <Button variant="secondary" onClick={onClose}>
                {phase.kind === "choose" ? "Cancel" : "Close"}
              </Button>
            )}
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
}
