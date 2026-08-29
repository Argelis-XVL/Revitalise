/**
 * The verdict form's GROUP SEMANTICS and its submit contract — WBS 6.4, FR-037.
 *
 * WHY THIS FILE WAS ADDED IN REVISION 4. The form's behaviour is exercised end to end by
 * `VerdictSection.test.tsx` and nothing in that coverage moved. What was NOT asserted
 * anywhere is the pair of properties that made this pass decline to adopt `ds/Radio`:
 *
 *   1. **The three radios share one `name` attribute.** `name` is what the BROWSER uses to
 *      make three inputs one radio group — it is the source of single-selection, of arrow-key
 *      traversal and of the roving tabindex that makes the group one tab stop
 *      (WCAG 1.3.1, 2.1.1, 4.1.2). Fluent's `RadioGroup` publishes it through React context
 *      (`contexts/RadioGroupContext.js`) and only Fluent's own `Radio` consumes it, so a bare
 *      `<input type="radio">` in that slot renders `name={null}` on all three.
 *   2. **Exactly one is checked when a verdict is already recorded.** `checked` is derived
 *      from the group's `value` through the same context, so a component that does not read
 *      it leaves the group uncontrolled — `initialVerdict` would never pre-select the saved
 *      verdict, and a reset to `""` would leave the previous selection drawn on screen.
 *
 * MEASURED, NOT ASSUMED (dispatch instruction; `@fluentui/react-components` 9.74.6,
 * 2026-08-27). Three of each rendered inside one `<RadioGroup value="2">`:
 *
 *   | child           | `name` on the three inputs                            | `checked`              |
 *   |-----------------|-------------------------------------------------------|------------------------|
 *   | Fluent `Radio`  | `["radiogroup-r1", "radiogroup-r1", "radiogroup-r1"]` | `[false, true, false]` |
 *   | `ds/Radio`      | `[null, null, null]`                                  | `[false, false, false]`|
 *
 * So `ds/Radio` does NOT compose inside Fluent's `RadioGroup`, Fluent's `Radio` stays, and
 * TAD §2.1.4's replacement of `Radio` is the one item in that table this pass could not
 * carry out. The two tests below are what makes that a guard rather than a comment: they
 * assert the PROPERTIES, not the implementation, so they pass with Fluent's `Radio` today and
 * would pass with a future `ds/Radio` that reads the group context — and fail with one that
 * does not, whoever swaps it in and for whatever reason.
 */
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { VerdictForm } from "./VerdictForm";
import { VERDICT_LABELS, VERDICT_VALUES } from "../dataverse/schema";
import { makeRepository, renderWithProviders } from "../test/harness";

function renderForm(overrides: Partial<Parameters<typeof VerdictForm>[0]> = {}) {
  const onSave = vi.fn();
  renderWithProviders(
    <VerdictForm
      applicationReference="REV-2026-001"
      slotLabel="Trustee 1"
      initialVerdict={null}
      initialNotes={null}
      saving={false}
      onSave={onSave}
      {...overrides}
    />,
    makeRepository(),
  );
  return { onSave };
}

function radios(): HTMLInputElement[] {
  // The generic parameter rather than a cast: `checked` is an `HTMLInputElement` property and
  // the whole point of these tests is that the three elements really are native radio inputs.
  return screen.getAllByRole<HTMLInputElement>("radio");
}

describe("VerdictForm — the radio group is a real radio group", () => {
  it("renders every verdict the option set declares, inside one radiogroup", () => {
    // BOTH SIDES COME FROM `schema.ts`'s VERDICT_LABELS, which is this app's transcription of
    // `OptionSets/rev_reviewverdict.xml` (C-TECH-067). Hand-typing `toHaveLength(3)` and the
    // three literal labels would have made this test assert the option set's CURRENT size from
    // a second, weaker source — so a fourth verdict would break the test rather than be covered
    // by it, which is the wrong way round.
    const expected = Object.values(VERDICT_LABELS);
    renderForm();
    expect(screen.getByRole("radiogroup")).toBeInTheDocument();
    expect(radios()).toHaveLength(expected.length);
    for (const name of expected) {
      expect(screen.getByRole("radio", { name })).toBeInTheDocument();
    }
  });

  it("gives all three inputs ONE shared, non-empty name attribute", () => {
    // The property the browser needs, not the one ARIA needs: `role="radiogroup"` on the
    // wrapper tells a screen reader these belong together, and the shared `name` is what
    // actually makes them mutually exclusive and one tab stop. Both are required; only one
    // of them is visible in the accessibility tree.
    renderForm();
    const names = radios().map((radio) => radio.getAttribute("name"));
    expect(new Set(names).size, `saw ${JSON.stringify(names)}`).toBe(1);
    expect(names[0]).not.toBeNull();
    expect(names[0]).not.toBe("");
  });

  it("pre-selects exactly one radio when a verdict was already recorded", () => {
    // The controlled half. A group whose children do not read the group's `value` renders
    // all three unchecked here, and a trustee returning to a case they had already decided
    // would be shown an empty form over a saved verdict.
    renderForm({ initialVerdict: VERDICT_VALUES.defer });
    expect(radios().filter((radio) => radio.checked)).toHaveLength(1);
    expect(screen.getByRole("radio", { name: "Defer" })).toBeChecked();
  });

  it("keeps selection mutually exclusive when a second option is chosen", async () => {
    // The consequence of the shared `name`, asserted as behaviour rather than as an
    // attribute: without it all three could be checked at once.
    renderForm({ initialVerdict: VERDICT_VALUES.approve });
    await userEvent.click(screen.getByRole("radio", { name: "Reject" }));
    expect(radios().filter((radio) => radio.checked)).toHaveLength(1);
    expect(screen.getByRole("radio", { name: "Reject" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Approve" })).not.toBeChecked();
  });
});

describe("VerdictForm — the save control submits the form (ds/Button's type default)", () => {
  it("is a submit button, so the form's own validation runs", async () => {
    // `ds/Button` defaults to `type="button"` — correct for every other call site in this app
    // and WRONG here, so `VerdictForm` passes `type="submit"` explicitly and the component
    // spreads `rest` after its default so the override takes. If that default ever won, this
    // form would stop validating: the missing-verdict check lives in `onSubmit`.
    const { onSave } = renderForm();
    const save = screen.getByRole("button", { name: /save verdict/i });
    expect(save).toHaveAttribute("type", "submit");

    await userEvent.click(save);
    // No verdict chosen, so nothing is saved and the reason is stated in TEXT rather than by
    // colour (WCAG 3.3.1, 1.4.1).
    expect(onSave).not.toHaveBeenCalled();
    expect(
      screen.getAllByText(/choose approve, defer or reject before saving/i).length,
    ).toBeGreaterThan(0);
  });

  it("saves once a verdict is chosen", async () => {
    const { onSave } = renderForm();
    await userEvent.click(screen.getByRole("radio", { name: "Approve" }));
    await userEvent.click(screen.getByRole("button", { name: /save verdict/i }));
    expect(onSave).toHaveBeenCalledWith(VERDICT_VALUES.approve, "");
  });
});
