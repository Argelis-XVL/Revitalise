/**
 * The detail panels — WBS 6.3, rebuilt by WI-0005 (Revision 15) around ONE spec-driven
 * component. What each row shows is tested in `domain/applicationDetailLayout.test.ts`; this
 * file tests how `DetailSectionPanel` renders each KIND of cell, plus the staff recommendation.
 *
 * The withheld state is still the important one: it is the ONLY redacted state reachable
 * today, so it has to be right and it has to look deliberate.
 */
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DetailSectionPanel, StaffRecommendationPanel } from "./CasePanels";
import { StateMessage } from "./Panel";
import { makeDetail } from "../test/harness";
import type { DetailCell, DetailSection } from "../domain/applicationDetailLayout";
import { RESTRICTED_VALUE_TEXT } from "../domain/fieldCatalogue";
import { redactedTextState } from "../domain/visibility";
import type { ApplicationDetail } from "../dataverse/types";

/** A one-row section, so each test controls exactly one cell. */
function oneRow(cell: (detail: ApplicationDetail) => DetailCell, heading = "Test section"): DetailSection {
  return {
    id: "test",
    heading,
    origin: "pack",
    groups: [{ heading: null, rows: [{ id: "T1", label: "Test label", cell }] }],
  };
}

function renderRow(cell: (detail: ApplicationDetail) => DetailCell, detail = makeDetail()) {
  return render(<DetailSectionPanel section={oneRow(cell)} detail={detail} />);
}

describe("DetailSectionPanel — structure", () => {
  it("renders the section heading as the panel's h2, so the print hierarchy survives", () => {
    renderRow(() => ({ kind: "value", text: "x" }));
    expect(screen.getByRole("heading", { level: 2, name: "Test section" })).toBeInTheDocument();
  });

  it("renders every row as a dt/dd pair carrying the row id", () => {
    const { container } = renderRow(() => ({ kind: "value", text: "The value" }));
    const term = container.querySelector("dt");
    expect(term).toHaveTextContent("Test label");
    expect(term).toHaveAttribute("data-field", "T1");
    expect(term?.nextElementSibling?.tagName).toBe("DD");
    expect(term?.nextElementSibling).toHaveTextContent("The value");
  });

  it("renders a Pack sub-heading as an h3 BEFORE its rows, and none where the group has none", () => {
    const section: DetailSection = {
      id: "grouped",
      heading: "Grouped",
      origin: "pack",
      groups: [
        { heading: null, rows: [{ id: "G1", label: "First", cell: () => ({ kind: "value", text: "1" }) }] },
        {
          heading: "In the last 2 weeks…",
          rows: [{ id: "G2", label: "Second", cell: () => ({ kind: "value", text: "2" }) }],
        },
      ],
    };
    const { container } = render(<DetailSectionPanel section={section} detail={makeDetail()} />);
    const subheadings = screen.getAllByRole("heading", { level: 3 });
    expect(subheadings.map((h) => h.textContent)).toEqual(["In the last 2 weeks…"]);
    // Document order: G1's term, then the sub-heading, then G2's term.
    const sequence = Array.from(container.querySelectorAll("dt, h3")).map(
      (el) => el.getAttribute("data-field") ?? el.textContent,
    );
    expect(sequence).toEqual(["G1", "In the last 2 weeks…", "G2"]);
  });
});

describe("DetailSectionPanel — each cell kind renders words, never an empty cell", () => {
  it("renders long text with its line breaks preserved", () => {
    const { container } = renderRow(() => ({ kind: "long-text", text: "Line one\nLine two" }));
    expect(container.querySelector("dd p")?.textContent).toBe("Line one\nLine two");
  });

  it("renders a restricted row as the restricted text, in the same dl as real values (FR-078)", () => {
    const { container } = renderRow(() => ({ kind: "restricted", catalogueKey: "benefit-status" }));
    expect(container.querySelector("dl dd")).toHaveTextContent(RESTRICTED_VALUE_TEXT);
  });

  it("renders a restricted row with no catalogue entry the same way", () => {
    const { container } = renderRow(() => ({ kind: "restricted", catalogueKey: null }));
    expect(container.querySelector("dl dd")).toHaveTextContent(RESTRICTED_VALUE_TEXT);
  });

  it("renders a withheld redacted row as a note with an explanation, and never the text", () => {
    renderRow((d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, "Secret") }), makeDetail({ redactionReleased: false }));
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/withheld/i);
    expect(note).toHaveTextContent(/expected state/i);
    expect(screen.queryByText("Secret")).toBeNull();
  });

  it("renders a released-but-empty redacted row as its own note, not as withheld", () => {
    renderRow((d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, null) }), makeDetail({ redactionReleased: true }));
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/nothing recorded/i);
    expect(note).not.toHaveTextContent(/withheld/i);
  });

  it("renders a released redacted row's text once release is affirmative", () => {
    const { container } = renderRow(
      (d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, "An anonymised answer") }),
      makeDetail({ redactionReleased: true }),
    );
    expect(within(container.querySelector("dd") as HTMLElement).getByText("An anonymised answer")).toBeInTheDocument();
    expect(screen.queryByRole("note")).toBeNull();
  });
});

/**
 * TAD §8.5 point 1, carried over from Revision 4: `withheld` and `released-empty` must look
 * different, and the right way round. Written as a RELATION, not a class name: Vitest processes
 * no CSS, so each rendered note is compared against a bare `StateMessage` rendered with the tone
 * it is supposed to have — a swap fails and a collapse fails, without naming a class inside
 * `components/ds`.
 */
describe("the redaction states are visually distinct, and mapped the right way round", () => {
  function toneClassOf(element: React.ReactElement): string {
    const { unmount } = render(element);
    const value = screen.getByRole("note").getAttribute("class") ?? "";
    unmount();
    return value;
  }

  const redactedRow = (released: boolean) => (
    <DetailSectionPanel
      section={oneRow((d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, null) }))}
      detail={makeDetail({ redactionReleased: released })}
    />
  );

  it("maps withheld to the muted tone and released-empty to the quiet one, and they differ", () => {
    const muted = toneClassOf(<StateMessage heading="H" explanation="E" tone="muted" />);
    const quiet = toneClassOf(<StateMessage heading="H" explanation="E" tone="quiet" />);
    expect(muted).not.toBe(quiet);
    expect(toneClassOf(redactedRow(false))).toBe(muted);
    expect(toneClassOf(redactedRow(true))).toBe(quiet);
  });

  it("keeps both states a note, never an alert", () => {
    // An alert would interrupt a screen-reader trustee on every navigation to announce
    // something entirely expected (`Panel.tsx`'s own reasoning).
    for (const released of [false, true]) {
      const { unmount } = render(redactedRow(released));
      expect(screen.getByRole("note")).toBeInTheDocument();
      expect(screen.queryByRole("alert")).toBeNull();
      unmount();
    }
  });
});

describe("StaffRecommendationPanel", () => {
  it("shows the recommendation and the panel date", () => {
    render(
      <StaffRecommendationPanel
        staffRecommendation="Staff support this application."
        panelDate="2026-10-01T00:00:00Z"
        loading={false}
      />,
    );
    expect(screen.getByText("Staff support this application.")).toBeInTheDocument();
    expect(screen.getByText("1 Oct 2026")).toBeInTheDocument();
  });

  it("explains an absent recommendation without implying the case is incomplete", () => {
    render(
      <StaffRecommendationPanel staffRecommendation={null} panelDate={null} loading={false} />,
    );
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/no staff recommendation/i);
    expect(note).toHaveTextContent(/can still be decided/i);
  });

  it("shows a loading state rather than an empty panel", () => {
    render(<StaffRecommendationPanel staffRecommendation={null} panelDate={null} loading />);
    expect(screen.getByText(/loading the review record/i)).toBeInTheDocument();
  });
});
