/**
 * The detail panels — WBS 6.3. The withheld-narrative state is the important one: it is
 * the ONLY state reachable today, so it has to be right and it has to look deliberate.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  CareSupportPanel,
  HolidayPanel,
  NarrativePanel,
  ScorePanel,
  StaffRecommendationPanel,
} from "./CasePanels";
import { makeDetail } from "../test/harness";

describe("NarrativePanel", () => {
  it("renders the withheld state as a note with an explanation, not an empty box", () => {
    render(<NarrativePanel detail={makeDetail({ redactionReleased: false })} />);
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/withheld/i);
    // "Not an error": an alert would interrupt a screen-reader user on every navigation
    // to tell them something entirely expected.
    expect(screen.queryByRole("alert")).toBeNull();
    // The explanation must tell the trustee the rest of the case is still decidable.
    expect(note).toHaveTextContent(/circumstance score/i);
  });

  it("does not render narrative text when release is false, even if text is present", () => {
    render(
      <NarrativePanel
        detail={makeDetail({
          redactionReleased: false,
          redactedNarrative: "SENTINEL-NARRATIVE-TEXT",
        })}
      />,
    );
    expect(screen.queryByText(/SENTINEL-NARRATIVE-TEXT/)).toBeNull();
  });

  it("renders the narrative once released", () => {
    render(
      <NarrativePanel
        detail={makeDetail({ redactionReleased: true, redactedNarrative: "Redacted story." })}
      />,
    );
    expect(screen.getByText("Redacted story.")).toBeInTheDocument();
    expect(screen.queryByRole("note")).toBeNull();
  });

  it("distinguishes released-but-empty from withheld", () => {
    render(
      <NarrativePanel detail={makeDetail({ redactionReleased: true, redactedNarrative: null })} />,
    );
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/no narrative recorded/i);
    expect(note).not.toHaveTextContent(/withheld/i);
  });

  it("gives the panel a heading, so the print hierarchy survives", () => {
    render(<NarrativePanel detail={makeDetail()} />);
    expect(screen.getByRole("heading", { level: 2, name: /anonymised narrative/i })).toBeInTheDocument();
  });
});

describe("ScorePanel", () => {
  it("shows the score, the status as text and the breakdown", () => {
    render(<ScorePanel detail={makeDetail({ circumstanceScore: 42, status: 6 })} />);
    expect(screen.getByText("42")).toBeInTheDocument();
    // Status is text, never colour alone (WCAG 1.4.1).
    expect(screen.getByText("Eligible for Panel")).toBeInTheDocument();
    expect(screen.getByText(/Wellbeing 20/)).toBeInTheDocument();
  });

  it("says so when there is no breakdown rather than showing a blank", () => {
    render(<ScorePanel detail={makeDetail({ scoreBreakdown: null })} />);
    expect(screen.getByRole("note")).toHaveTextContent(/no score breakdown/i);
  });

  it("shows an unscored application as not scored, not as zero", () => {
    render(<ScorePanel detail={makeDetail({ circumstanceScore: null })} />);
    expect(screen.getByText("Not scored")).toBeInTheDocument();
  });
});

describe("HolidayPanel", () => {
  it("shows the preferred dates as a readable range", () => {
    render(<HolidayPanel detail={makeDetail()} />);
    expect(screen.getByText("5 Oct 2026 to 12 Oct 2026")).toBeInTheDocument();
  });

  it("labels an absent holiday field rather than leaving the cell empty", () => {
    render(<HolidayPanel detail={makeDetail({ breakLocation: null, providerPreference: null })} />);
    expect(screen.getAllByText("Not recorded").length).toBeGreaterThan(0);
  });
});

describe("CareSupportPanel — the three states FR-035/TAD §3.2.1 requires", () => {
  it("renders the withheld state as a note, not an empty box", () => {
    render(<CareSupportPanel detail={makeDetail({ redactionReleased: false })} />);
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/withheld/i);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("does not render any of the three redacted texts when release is false", () => {
    render(
      <CareSupportPanel
        detail={makeDetail({
          redactionReleased: false,
          redactedCareSupportDescription: "SENTINEL-DESCRIPTION",
          redactedCareProvidedExample: "SENTINEL-EXAMPLE",
          redactedOtherCareProvidedType: "SENTINEL-OTHER",
        })}
      />,
    );
    expect(screen.queryByText(/SENTINEL-/)).toBeNull();
  });

  it("renders the exact released-but-empty sentence when release is true but nothing has been scrubbed yet", () => {
    render(
      <CareSupportPanel
        detail={makeDetail({
          redactionReleased: true,
          redactedCareSupportDescription: null,
          redactedCareProvidedExample: null,
          redactedOtherCareProvidedType: null,
        })}
      />,
    );
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(
      "No redacted care-support description is available for this application.",
    );
    expect(note).not.toHaveTextContent(/withheld/i);
  });

  it("renders all three redacted texts once released and populated", () => {
    render(
      <CareSupportPanel
        detail={makeDetail({
          redactionReleased: true,
          redactedCareSupportDescription: "Needs support with daily routine.",
          redactedCareProvidedExample: "Help with medication.",
          redactedOtherCareProvidedType: "Overnight supervision.",
        })}
      />,
    );
    expect(screen.getByText("Needs support with daily routine.")).toBeInTheDocument();
    expect(screen.getByText("Help with medication.")).toBeInTheDocument();
    expect(screen.getByText("Overnight supervision.")).toBeInTheDocument();
    expect(screen.queryByRole("note")).toBeNull();
  });

  it("gives the panel a heading, so the print hierarchy survives", () => {
    render(<CareSupportPanel detail={makeDetail()} />);
    expect(
      screen.getByRole("heading", { level: 2, name: /care-support description/i }),
    ).toBeInTheDocument();
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
