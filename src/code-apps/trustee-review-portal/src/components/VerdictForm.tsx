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
 *
 * ## Revision 4 — `Button` becomes `ds/Button`. `Radio` DOES NOT, AND HERE IS THE MEASUREMENT
 *
 * TAD §2.1.4 anticipates that `Radio` and `RadioGroup` are the risky pair and keeps
 * `RadioGroup`; the dispatch asked for `ds/Radio` to be adopted **only if it composes inside
 * it**. It does not. Ground-truthed against `@fluentui/react-components` 9.74.6 on
 * 2026-08-27 by rendering three of each inside one `<RadioGroup value="2">`:
 *
 *   | rendered inside `RadioGroup value="2"` | `name` attribute on the three inputs | `checked` |
 *   |---|---|---|
 *   | Fluent `Radio`  | `["radiogroup-r1", "radiogroup-r1", "radiogroup-r1"]` | `[false, true, false]` |
 *   | `ds/Radio`      | `[null, null, null]`                                  | `[false, false, false]` |
 *
 * `RadioGroup` publishes `name` and the derived `checked` through **React context**
 * (`contexts/RadioGroupContext.js`), and only Fluent's own `Radio` consumes it
 * (`useRadio.js` → `useRadioGroupContextValue_unstable`). A bare `<input type="radio">`
 * reads no context, so two things break at once, and the second is the dangerous one:
 *
 *   1. **The shared `name` is gone.** `name` is what the BROWSER uses to make three inputs
 *      one radio group — it is the source of single-selection, of arrow-key traversal and of
 *      the roving tabindex that makes a group one tab stop. Without it there are three
 *      independent checkboxes-shaped-like-radios, all three checkable at once, each its own
 *      tab stop (WCAG 1.3.1, 2.1.1, 4.1.2).
 *   2. **The controlled `checked` is gone**, so `RadioGroup`'s `value` prop is disconnected —
 *      while its root `onChange` still fires for any bubbled radio change
 *      (`useRadioGroup.js`). The verdict would appear to register on the first click and then
 *      diverge from state: `initialVerdict` would never pre-select the saved verdict, and
 *      resetting to `""` would leave the old selection drawn on screen.
 *
 * So Fluent's `Radio` STAYS, with Fluent's `RadioGroup`, `Field`, `Label` and `Textarea`
 * around it. `styles.tallTarget` stays on each one for the same reason: unlike `ds/Button`,
 * Fluent's `Radio` carries no 44px guarantee of its own. The group semantics are now pinned
 * by a test rather than by this comment — see `VerdictSection.test.tsx`.
 */
import {
  Field,
  Label,
  Radio,
  RadioGroup,
  Textarea,
} from "@fluentui/react-components";
import { Button } from "./ds";
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
        {/*
          `type="submit"` is passed explicitly and overrides `ds/Button`'s `type="button"`
          default — the component spreads `rest` AFTER that default precisely so a genuine
          submit button stays expressible (`ds/Button.tsx:80-89`). This form's `onSubmit` is
          where the missing-verdict validation lives, so a button that did not submit would
          silently skip it.
        */}
        <Button variant="primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save verdict"}
        </Button>
      </div>
    </form>
  );
}
