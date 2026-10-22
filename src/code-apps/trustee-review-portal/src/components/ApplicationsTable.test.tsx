/**
 * The verdict button shows the signed-in trustee's OWN verdict — SDD A-14, FR-116 (portal TAD
 * trustee-portal-design-2 ADR-086 point 4; US-012 AC-11; WI-0147).
 *
 * jsdom computes no CSS, so the tone is asserted through the button's `data-verdict-tone` and its
 * tone class; the colours themselves are pinned by `styles/ds-tokens.test.ts`.
 *
 * Accessibility, asserted directly rather than by an axe run (no axe dependency is installed in
 * this app; recorded in the Dev Summary): every button is a real <button>, its accessible name
 * CONTAINS its visible text (WCAG 2.5.3), and the verdict word is always present, so colour is
 * never the only carrier (WCAG 1.4.1).
 */
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ApplicationsTable } from "./ApplicationsTable";
import { DEFAULT_SORT } from "../domain/listView";
import type { OwnVerdictState } from "../domain/ownVerdict";
import type { ApplicationSummary } from "../dataverse/types";
import { makeSummary } from "../test/harness";

const ROWS: ApplicationSummary[] = [
  makeSummary({ id: "a1", reference: "REV-A-1" }),
  makeSummary({ id: "a2", reference: "REV-A-2" }),
  makeSummary({ id: "a3", reference: "REV-A-3" }),
  makeSummary({ id: "a4", reference: "REV-A-4" }),
  makeSummary({ id: "a5", reference: "REV-A-5" }),
  makeSummary({ id: "a6", reference: "REV-A-6" }),
];

const STATES: Record<string, OwnVerdictState> = {
  a1: { kind: "decided", verdict: 1, finalised: false },
  a2: { kind: "decided", verdict: 2, finalised: false },
  a3: { kind: "decided", verdict: 3, finalised: true },
  a4: { kind: "awaiting" },
  a5: { kind: "none" },
  a6: { kind: "decided", verdict: 9, finalised: false },
};

function renderTable(onRecordVerdict = vi.fn(), verdictStateFor?: (row: ApplicationSummary) => OwnVerdictState) {
  render(
    <ApplicationsTable
      rows={ROWS}
      sort={DEFAULT_SORT}
      onSort={vi.fn()}
      onOpen={vi.fn()}
      onRecordVerdict={onRecordVerdict}
      caption="Test applications."
      verdictStateFor={verdictStateFor ?? ((row) => STATES[row.id] ?? { kind: "none" })}
    />,
  );
  return onRecordVerdict;
}

function decisionButton(reference: string): HTMLElement {
  const row = screen.getByRole("button", { name: `${reference}, open the full case` }).closest("tr") as HTMLElement;
  const buttons = within(row).getAllByRole("button");
  return buttons[buttons.length - 1] as HTMLElement;
}

describe("ApplicationsTable — own verdict on the existing button (FR-116)", () => {
  it("shows one row per verdict with its word, its tone and an accessible name containing the word", () => {
    renderTable();
    const cases = [
      ["REV-A-1", "Approved", "approved", "Approved — your verdict on REV-A-1. Open to view or change it"],
      ["REV-A-2", "Deferred", "deferred", "Deferred — your verdict on REV-A-2. Open to view or change it"],
      ["REV-A-3", "Rejected", "rejected", "Rejected — your verdict on REV-A-3. Open to view it"],
    ] as const;
    for (const [reference, word, tone, name] of cases) {
      const button = decisionButton(reference);
      expect(button.tagName).toBe("BUTTON");
      expect(button).toHaveTextContent(word);
      expect(button).toHaveAccessibleName(name);
      expect(button.getAttribute("aria-label")).toContain(button.textContent ?? "\u0000");
      expect(button.getAttribute("data-verdict-tone")).toBe(tone);
      expect(button.className).toMatch(/verdictButton/);
      expect(button).not.toHaveTextContent("Record verdict");
    }
  });

  it("reads Record verdict on an awaiting row and on a row with nothing to record", () => {
    renderTable();
    for (const reference of ["REV-A-4", "REV-A-5"]) {
      const button = decisionButton(reference);
      expect(button).toHaveTextContent("Record verdict");
      expect(button).toHaveAccessibleName(`Record verdict for ${reference}`);
      expect(button.getAttribute("data-verdict-tone")).toBeNull();
    }
  });

  it("shows an unknown option value's label in the neutral style, never blank", () => {
    renderTable();
    const button = decisionButton("REV-A-6");
    expect(button).toHaveTextContent("Unknown (9)");
    expect(button.getAttribute("data-verdict-tone")).toBe("neutral");
    expect(button.className).not.toMatch(/verdictButton/);
  });

  it("opens the same dialog from a decided row as from an awaiting one", async () => {
    const onRecordVerdict = renderTable();
    await userEvent.click(decisionButton("REV-A-1"));
    await userEvent.click(decisionButton("REV-A-4"));
    expect(onRecordVerdict.mock.calls.map((call) => (call[0] as ApplicationSummary).reference)).toEqual([
      "REV-A-1",
      "REV-A-4",
    ]);
  });

  it("reads Record verdict on every row when no verdict state is supplied", () => {
    render(
      <ApplicationsTable
        rows={ROWS}
        sort={DEFAULT_SORT}
        onSort={vi.fn()}
        onOpen={vi.fn()}
        onRecordVerdict={vi.fn()}
        caption="Test applications."
      />,
    );
    expect(screen.getAllByRole("button", { name: /^Record verdict for / })).toHaveLength(ROWS.length);
  });
});
