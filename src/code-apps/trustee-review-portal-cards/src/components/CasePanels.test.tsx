/**
 * The card-layout detail panels — Design 2.0, card app only (TAD trustee-portal-design-2,
 * ADR-055..059; WI-0057..WI-0075). What each ROW shows is tested in
 * `domain/applicationDetailLayout.test.ts` (byte-identical to the first app's); which DISPLAY a
 * row takes is tested in `domain/applicationDetailDisplay.test.ts`. This file tests how each
 * display renders: its markup contract (`<dt>`/`<dd>` inside a `<dl>`, `data-field`, one `<h2>`,
 * `<h3>` sub-blocks), its words, and the three redaction states.
 *
 * The withheld state is still the important one: it is the ONLY redacted state reachable today.
 */
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DetailSectionPanel, StaffRecommendationPanel } from "./CasePanels";
import { makeDetail } from "../test/harness";
import { APPLICATION_DETAIL_LAYOUT } from "../domain/applicationDetailLayout";
import type { DetailCell, DetailSection } from "../domain/applicationDetailLayout";
import { RESTRICTED_VALUE_TEXT } from "../domain/fieldCatalogue";
import {
  RELEASED_EMPTY_EXPLANATION,
  WITHHELD_EXPLANATION,
  WITHHELD_EXPLANATION_FIRST_SENTENCE,
  redactedTextState,
} from "../domain/visibility";
import type { ApplicationDetail } from "../dataverse/types";

/** Text a screen reader gets from an element: its text with every `aria-hidden` subtree removed. */
function accessibleText(element: Element): string {
  const clone = element.cloneNode(true) as Element;
  clone.querySelectorAll('[aria-hidden="true"]').forEach((node) => {
    node.remove();
  });
  return clone.textContent ?? "";
}

/** A one-row section, so each test controls exactly one cell. */
function oneRow(cell: (detail: ApplicationDetail) => DetailCell, id = "T1"): DetailSection {
  return {
    id: "test",
    heading: "Test section",
    origin: "pack",
    groups: [{ heading: null, rows: [{ id, label: "Test label", cell }] }],
  };
}

function renderRow(cell: (detail: ApplicationDetail) => DetailCell, detail = makeDetail(), id = "T1") {
  return render(<DetailSectionPanel section={oneRow(cell, id)} detail={detail} />);
}

function packSection(id: string): DetailSection {
  const section = APPLICATION_DETAIL_LAYOUT.find((s) => s.id === id);
  if (section === undefined) throw new Error(`no section ${id}`);
  return section;
}

function renderSection(id: string, detail: ApplicationDetail) {
  return render(<DetailSectionPanel section={packSection(id)} detail={detail} />);
}

describe("DetailSectionPanel — structure (WI-0069, WI-0075)", () => {
  it("renders the section heading as the card's one h2, inside a labelled section", () => {
    renderRow(() => ({ kind: "value", text: "x" }));
    const heading = screen.getByRole("heading", { level: 2, name: "Test section" });
    expect(screen.getAllByRole("heading", { level: 2 })).toHaveLength(1);
    const section = heading.closest("section");
    expect(section?.getAttribute("aria-labelledby")).toBe(heading.id);
    expect(section?.getAttribute("data-print")).toBe("block");
  });

  it("renders every row as a dt/dd pair inside a dl, the dt carrying the row id", () => {
    const { container } = renderRow(() => ({ kind: "value", text: "The value" }));
    const term = container.querySelector("dt");
    expect(term).toHaveTextContent("Test label");
    expect(term).toHaveAttribute("data-field", "T1");
    expect(term?.nextElementSibling?.tagName).toBe("DD");
    expect(term?.nextElementSibling).toHaveTextContent("The value");
    expect(term?.closest("dl")).not.toBeNull();
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
    expect(screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent)).toEqual([
      "In the last 2 weeks…",
    ]);
    const sequence = Array.from(container.querySelectorAll("dt, h3")).map(
      (el) => el.getAttribute("data-field") ?? el.textContent,
    );
    expect(sequence).toEqual(["G1", "In the last 2 weeks…", "G2"]);
  });

  it("puts a decorative eyebrow above each Pack card's h2, hidden from assistive technology", () => {
    const { container } = renderSection("application-details", makeDetail());
    const eyebrow = container.querySelector("section > div > p");
    expect(eyebrow).toHaveTextContent("The break");
    expect(eyebrow).toHaveAttribute("aria-hidden", "true");
    expect(eyebrow?.getAttribute("data-print")).toBe("hide");
    expect(eyebrow?.compareDocumentPosition(screen.getByRole("heading", { level: 2 })) ?? 0).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });
});

describe("fact tiles (WI-0060) and A3's chips (WI-0061)", () => {
  it("renders a value as a tile, and an absent value in the absent state with the same words", () => {
    const { container } = renderSection("application-details", makeDetail({ breakType: null, breakLocation: "Devon" }));
    const d2 = container.querySelector('dt[data-field="D2"]')?.parentElement;
    expect(d2?.getAttribute("data-absent")).toBeNull();
    const d11 = container.querySelector('dt[data-field="D11"]')?.parentElement;
    expect(d11?.getAttribute("data-absent")).toBe("true");
    expect(d11?.querySelector("dd")).toHaveTextContent("Not recorded");
    // Tiles are divs wrapping one dt + one dd, inside one dl grid.
    expect(d2?.parentElement?.tagName).toBe("DL");
  });

  it("renders one profile's conditions as unlabelled chips", () => {
    const { container } = renderSection("about-applicant", makeDetail({ conditionProfile: [3, 8] }));
    const dd = container.querySelector('dt[data-field="A3"]')?.nextElementSibling as HTMLElement;
    expect(within(dd).getAllByRole("listitem")).toHaveLength(2);
    expect(dd).not.toHaveTextContent("You:");
  });

  it("keeps a carer's two profiles apart as two labelled chip rows", () => {
    const { container } = renderSection(
      "about-applicant",
      makeDetail({ conditionProfile: [3], supportRecipientConditionProfile: [2, 8] }),
    );
    const dd = container.querySelector('dt[data-field="A3"]')?.nextElementSibling as HTMLElement;
    expect(dd).toHaveTextContent("You:");
    expect(dd).toHaveTextContent("The person you support:");
    expect(within(dd).getAllByRole("list")).toHaveLength(2);
    expect(within(dd).getAllByRole("listitem")).toHaveLength(3);
  });

  it("shows A3 as an absent tile when neither profile is answered", () => {
    const { container } = renderSection("about-applicant", makeDetail());
    const tile = container.querySelector('dt[data-field="A3"]')?.parentElement;
    expect(tile?.getAttribute("data-absent")).toBe("true");
    expect(tile?.querySelector("dd")).toHaveTextContent("Not recorded");
  });
});

describe("the cost receipt (WI-0062)", () => {
  it("lists D5-D10 in Pack order under 'Costs', with D8 as the marked total", () => {
    const { container } = renderSection(
      "application-details",
      makeDetail({ accommodationCost: 850, travelCost: 120, otherCost: null, costs: 1000 }),
    );
    const block = container.querySelector('[data-display-group="costs"]') as HTMLElement;
    expect(within(block).getByRole("heading", { level: 3 })).toHaveTextContent("Costs");
    const ids = Array.from(block.querySelectorAll("dt")).map((dt) => dt.getAttribute("data-field"));
    expect(ids).toEqual(["D5", "D6", "D7", "D8", "D9", "D10"]);
    const total = block.querySelector('dt[data-field="D8"]')?.parentElement;
    expect(total?.getAttribute("data-total")).toBe("true");
    expect(block.querySelector('dt[data-field="D5"]')?.nextElementSibling).toHaveTextContent("£850");
    const d7 = block.querySelector('dt[data-field="D7"]')?.nextElementSibling;
    expect(d7).toHaveTextContent("Not recorded");
    expect(d7?.getAttribute("data-absent")).toBe("true");
  });
});

describe("answer cards — the three redaction states (WI-0063, FR-079)", () => {
  const redactedRow = (released: boolean, text: string | null) =>
    renderRow((d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, text) }), makeDetail({ redactionReleased: released }));

  it("renders withheld as a note with the pill and ONLY the first sentence, and never the text", () => {
    redactedRow(false, "Secret");
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent("Withheld until released");
    expect(within(note).getByText(WITHHELD_EXPLANATION_FIRST_SENTENCE)).toBeInTheDocument();
    expect(note.textContent).not.toContain(WITHHELD_EXPLANATION);
    expect(screen.queryByText("Secret")).toBeNull();
    expect(note.getAttribute("data-print")).toBe("state");
  });

  it("renders released-empty as its own note, with its full explanation, not as withheld", () => {
    redactedRow(true, null);
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent("Nothing recorded");
    expect(note).toHaveTextContent(RELEASED_EMPTY_EXPLANATION);
    expect(note).not.toHaveTextContent(/withheld/i);
  });

  it("renders released text through MultilineText, with no note", () => {
    const { container } = redactedRow(true, "An anonymised answer\nwith a line break");
    expect(container.querySelector("dd p")?.textContent).toBe("An anonymised answer\nwith a line break");
    expect(screen.queryByRole("note")).toBeNull();
  });

  it("gives withheld and released-empty different tones, the right way round", () => {
    const first = redactedRow(false, null);
    expect(screen.getByRole("note").getAttribute("data-tone")).toBe("withheld");
    first.unmount();
    redactedRow(true, null);
    expect(screen.getByRole("note").getAttribute("data-tone")).toBe("quiet");
  });

  it("keeps both states a note, never an alert", () => {
    for (const released of [false, true]) {
      const { unmount } = redactedRow(released, null);
      expect(screen.getByRole("note")).toBeInTheDocument();
      expect(screen.queryByRole("alert")).toBeNull();
      unmount();
    }
  });

  it("renders a redacted cell as an answer card whatever row id it has (ADR-058)", () => {
    const { container } = renderRow(
      (d) => ({ kind: "redacted", state: redactedTextState(d.redactionReleased, "Secret") }),
      makeDetail({ redactionReleased: false }),
      "D1", // a FACT row's id
    );
    expect(container.querySelector('[data-display-group="answers"]')).not.toBeNull();
    expect(screen.queryByText("Secret")).toBeNull();
  });

  it("groups a section's answers under 'In their words'", () => {
    const { container } = renderSection("application-details", makeDetail());
    const block = container.querySelector('[data-display-group="answers"]') as HTMLElement;
    expect(within(block).getByRole("heading", { level: 3 })).toHaveTextContent("In their words");
    expect(Array.from(block.querySelectorAll("dt")).map((dt) => dt.getAttribute("data-field"))).toEqual(["D12", "D13"]);
  });
});

describe("restricted rows (WI-0067, FR-078)", () => {
  it("gives every restricted dd the full restricted text, shows the pill, and states the text once", () => {
    const { container } = renderSection("financial-eligibility", makeDetail());
    const block = container.querySelector('[data-display-group="restricted"]') as HTMLElement;
    expect(within(block).getByRole("heading", { level: 3 })).toHaveTextContent("Not visible to trustees");
    const dds = Array.from(block.querySelectorAll("dd"));
    expect(dds).toHaveLength(3);
    for (const dd of dds) {
      expect(accessibleText(dd)).toBe(RESTRICTED_VALUE_TEXT);
      expect(dd).toHaveTextContent("Restricted");
    }
    const visibleNotes = Array.from(block.querySelectorAll("p")).filter((p) => p.textContent === RESTRICTED_VALUE_TEXT);
    expect(visibleNotes).toHaveLength(1);
    expect(visibleNotes[0]).toHaveAttribute("aria-hidden", "true");
  });

  it("renders a restricted cell as a restricted row whatever row id it has", () => {
    const { container } = renderRow(() => ({ kind: "restricted", catalogueKey: null }), makeDetail(), "D1");
    expect(accessibleText(container.querySelector("dd") as HTMLElement)).toBe(RESTRICTED_VALUE_TEXT);
  });

  it("orders Financial Eligibility as facts, then restricted, then the free-text answer", () => {
    const { container } = renderSection("financial-eligibility", makeDetail());
    const kinds = Array.from(container.querySelectorAll("[data-display-group]")).map((el) =>
      el.getAttribute("data-display-group"),
    );
    expect(kinds).toEqual(["tiles", "restricted", "answers"]);
  });
});

describe("Current Circumstances: score bar, scale and answer list (WI-0064..WI-0066)", () => {
  it("shows C1 as '{n} / 60' with a bar filled to n/60", () => {
    const { container } = renderSection("current-circumstances", makeDetail({ circumstanceScore: 42 }));
    const dd = container.querySelector('dt[data-field="C1"]')?.nextElementSibling as HTMLElement;
    expect(accessibleText(dd)).toBe("42 / 60");
    const fill = dd.querySelector('[aria-hidden="true"] > span') as HTMLElement;
    expect(fill.style.width).toBe("70%");
  });

  it("shows C1 as 'Not recorded' when there is no score", () => {
    const { container } = renderSection("current-circumstances", makeDetail({ circumstanceScore: null }));
    const dd = container.querySelector('dt[data-field="C1"]')?.nextElementSibling as HTMLElement;
    expect(accessibleText(dd)).toBe("Not recorded");
  });

  it("shows C2 as eleven points with the answer filled, and the value in text", () => {
    renderSection("current-circumstances", makeDetail({ lifeSatisfaction: 7 }));
    const scale = screen.getByRole("img", { name: "Answer: 7 out of 10" });
    const points = Array.from(scale.querySelectorAll("span"));
    expect(points.map((p) => p.textContent)).toEqual(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]);
    expect(points.filter((p) => p.getAttribute("data-selected") === "true").map((p) => p.textContent)).toEqual(["7"]);
    // The print copy of the same sentence exists and is hidden from the accessibility tree.
    const printCopy = scale.parentElement?.querySelector('[data-print="scale-value"]');
    expect(printCopy).toHaveTextContent("Answer: 7 out of 10");
    expect(printCopy).toHaveAttribute("aria-hidden", "true");
  });

  it("shows 'Not recorded' instead of the points when C2 is unanswered", () => {
    const { container } = renderSection("current-circumstances", makeDetail({ lifeSatisfaction: null }));
    expect(screen.queryByRole("img")).toBeNull();
    expect(container.querySelector('dt[data-field="C2"]')?.nextElementSibling).toHaveTextContent("Not recorded");
  });

  it("shows the C3-C12 answers in pills, 'Not recorded' in italic where unanswered", () => {
    const { container } = renderSection(
      "current-circumstances",
      makeDetail({ wellbeingAnswers: { 1: 1, 2: null, 3: null, 4: null, 5: null, 6: null, 7: null, 8: null, 9: null, 10: null } }),
    );
    const c4 = container.querySelector('dt[data-field="C4"]')?.nextElementSibling?.firstElementChild;
    expect(c4).toHaveTextContent("Not recorded");
    expect(c4?.getAttribute("data-absent")).toBe("true");
    const c3 = container.querySelector('dt[data-field="C3"]')?.nextElementSibling?.firstElementChild;
    expect(c3?.getAttribute("data-absent")).toBeNull();
    expect(screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent)).toEqual([
      "Life satisfaction",
      "In the last 2 weeks…",
      "In the last year…",
    ]);
  });
});

describe("the Summary hero (WI-0057..WI-0059)", () => {
  const summary = (detail: ApplicationDetail) => renderSection("summary", detail);

  it("replaces the Summary panel: one labelled section, one h2 that still says 'Summary' to a screen reader", () => {
    summary(makeDetail({ circumstanceScore: 42 }));
    const heading = screen.getByRole("heading", { level: 2 });
    expect(heading).toHaveAccessibleName("Summary: 42 out of 60 circumstance points");
    expect(heading.closest("section")?.getAttribute("aria-labelledby")).toBe(heading.id);
  });

  it("reads 'Not scored yet' and a dash badge when there is no score, and the badge still speaks words", () => {
    const { container } = summary(makeDetail({ circumstanceScore: null }));
    expect(screen.getByRole("heading", { level: 2 })).toHaveAccessibleName("Summary: Not scored yet");
    const badge = container.querySelector('dt[data-field="S3"]')?.nextElementSibling as HTMLElement;
    expect(badge).toHaveTextContent("—");
    expect(accessibleText(badge)).toBe("Not scored");
  });

  it("labels the badge 'Score' on screen and keeps the Pack's S3 label for assistive technology", () => {
    const { container } = summary(makeDetail({ circumstanceScore: 42 }));
    const dt = container.querySelector('dt[data-field="S3"]') as HTMLElement;
    expect(accessibleText(dt)).toBe("Overall Current Circumstance Score (Out of 60, 60 as worst)");
    expect(dt.querySelector('[aria-hidden="true"]')).toHaveTextContent("Score");
  });

  it("shows S6's shortened chip label and keeps the Pack label in the dt", () => {
    const { container } = summary(makeDetail());
    const dt = container.querySelector('dt[data-field="S6"]') as HTMLElement;
    expect(dt.querySelector('[aria-hidden="true"]')).toHaveTextContent("Total requested inc. exceptional funding");
    expect(accessibleText(dt)).toBe("Individual Total Amount Requesting Revitalise inc. Exceptional Funding");
  });

  it("renders the status pill with its tone and the status in words", () => {
    const { container } = summary(makeDetail({ status: 6 }));
    const pill = container.querySelector('dt[data-field="S0a"]')?.parentElement as HTMLElement;
    expect(pill.getAttribute("data-tone")).toBe("eligible");
    expect(pill.querySelector("dd")).toHaveTextContent("Eligible for Panel");
  });

  it("puts the pill and S0b, S1, S2 in the first chip row and S4-S7 in the second", () => {
    const { container } = summary(makeDetail());
    const rows = Array.from(container.querySelectorAll("section dl")).slice(1);
    // ApplicationDetail.jsx:120-123: the pill and the first chip block are separate items of
    // one wrapping row, so the chips wrap as a unit; the second chip row follows.
    expect(rows.map((dl) => Array.from(dl.querySelectorAll("dt")).map((dt) => dt.getAttribute("data-field")))).toEqual([
      ["S0a"],
      ["S0b", "S1", "S2"],
      ["S4", "S5", "S6", "S7"],
    ]);
    const pillList = rows[0]!;
    const firstChips = rows[1]!;
    expect(pillList.parentElement).toBe(firstChips.parentElement);
  });

  it("renders exactly the Summary section's nine rows, no more", () => {
    const { container } = summary(makeDetail());
    const ids = Array.from(container.querySelectorAll("dt[data-field]")).map((dt) => dt.getAttribute("data-field"));
    expect([...ids].sort()).toEqual(["S0a", "S0b", "S1", "S2", "S3", "S4", "S5", "S6", "S7"].sort());
  });
});

describe("StaffRecommendationPanel (WI-0070 — content unchanged, restyled as a card)", () => {
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
    expect(screen.getByRole("heading", { level: 2, name: "Staff recommendation" })).toBeInTheDocument();
    expect(screen.getByText("From the team")).toHaveAttribute("aria-hidden", "true");
  });

  it("explains an absent recommendation without implying the case is incomplete", () => {
    render(<StaffRecommendationPanel staffRecommendation={null} panelDate={null} loading={false} />);
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/no staff recommendation/i);
    expect(note).toHaveTextContent(/can still be decided/i);
  });

  it("shows a loading state rather than an empty panel", () => {
    render(<StaffRecommendationPanel staffRecommendation={null} panelDate={null} loading />);
    expect(screen.getByText(/loading the review record/i)).toBeInTheDocument();
  });
});
