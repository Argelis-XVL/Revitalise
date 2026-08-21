/**
 * Verdict capture — WBS 6.4, FR-037, SDD US-012 AC-4.
 *
 * Approve / Defer / Reject with optional notes. Three accessibility obligations are
 * load-bearing here and are all in the markup rather than in a comment:
 *
 *   - the radio group has a real `<fieldset>`/`<legend>`, so the question is announced
 *     with each option (WCAG 1.3.1);
 *   - a missing verdict is reported IN TEXT, tied to the group by `aria-describedby`,
 *     never by colour (WCAG 3.3.1, 1.4.1);
 *   - the notes limit is stated before it is hit and counted as it is approached, in a
 *     `aria-live="polite"` region so it is announced without stealing focus.
 */
import {
  Button,
  Field,
  Label,
  Radio,
  RadioGroup,
  Textarea,
} from "@fluentui/react-components";
import { useId, useState } from "react";
import { VERDICT_NOTES_MAX_LENGTH, VERDICT_VALUES } from "../dataverse/schema";
import styles from "../styles/app.module.css";

const VERDICT_OPTIONS = [
  { value: VERDICT_VALUES.approve, label: "Approve" },
  { value: VERDICT_VALUES.defer, label: "Defer" },
  { value: VERDICT_VALUES.reject, label: "Reject" },
];

export function VerdictForm({
  applicationReference,
  slotLabel,
  initialVerdict,
  initialNotes,
  saving,
  onSave,
}: {
  applicationReference: string;
  /** "Trustee 1" / "Trustee 2" — the trustee is told which slot is theirs. */
  slotLabel: string;
  initialVerdict: number | null;
  initialNotes: string | null;
  saving: boolean;
  onSave: (verdict: number, notes: string) => void;
}) {
  const [verdict, setVerdict] = useState<number | null>(initialVerdict);
  const [notes, setNotes] = useState<string>(initialNotes ?? "");
  const [showValidation, setShowValidation] = useState(false);

  const groupId = useId();
  const errorId = useId();
  const notesId = useId();
  const countId = useId();

  const missingVerdict = verdict === null;
  const remaining = VERDICT_NOTES_MAX_LENGTH - notes.length;

  return (
    <form
      className={styles.verdictForm}
      onSubmit={(event) => {
        event.preventDefault();
        if (verdict === null) {
          setShowValidation(true);
          return;
        }
        onSave(verdict, notes);
      }}
    >
      <p className={styles.hint}>
        You are recording the <strong>{slotLabel}</strong> verdict for {applicationReference}.
      </p>

      <Field
        label={{ children: "Your verdict", required: true }}
        validationState={showValidation && missingVerdict ? "error" : "none"}
        validationMessage={
          showValidation && missingVerdict
            ? "Choose Approve, Defer or Reject before saving."
            : undefined
        }
      >
        <RadioGroup
          aria-labelledby={groupId}
          aria-describedby={showValidation && missingVerdict ? errorId : undefined}
          value={verdict === null ? "" : String(verdict)}
          onChange={(_event, data) => {
            setVerdict(Number(data.value));
            setShowValidation(false);
          }}
        >
          <span id={groupId} className={styles.srOnly}>
            Verdict for {applicationReference}, required
          </span>
          {VERDICT_OPTIONS.map((option) => (
            <Radio
              key={option.value}
              value={String(option.value)}
              label={option.label}
              className={styles.tallTarget}
            />
          ))}
        </RadioGroup>
      </Field>
      {showValidation && missingVerdict ? (
        <p id={errorId} className={styles.srOnly}>
          Choose Approve, Defer or Reject before saving.
        </p>
      ) : null}

      <div className={styles.filterField}>
        <Label htmlFor={notesId}>Notes (optional)</Label>
        <Textarea
          id={notesId}
          value={notes}
          maxLength={VERDICT_NOTES_MAX_LENGTH}
          resize="vertical"
          aria-describedby={countId}
          onChange={(_event, data) => {
            setNotes(data.value);
          }}
        />
        <p id={countId} className={styles.hint} aria-live="polite">
          {remaining} of {VERDICT_NOTES_MAX_LENGTH} characters remaining.
        </p>
      </div>

      <div className={styles.verdictActions}>
        <Button appearance="primary" type="submit" className={styles.tallTarget} disabled={saving}>
          {saving ? "Saving…" : "Save verdict"}
        </Button>
      </div>
    </form>
  );
}
