/**
 * The detail panels — WBS 6.3. The withheld-narrative state is the important one: it is
 * the ONLY state reachable today, so it has to be right and it has to look deliberate.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  CareSupportPanel,
  ConditionProfilePanel,
  FinancialEligibilityPanel,
  HelperRefereeContactPanel,
  HolidayPanel,
  NarrativePanel,
  ScorePanel,
  StaffRecommendationPanel,
} from "./CasePanels";
import { StateMessage } from "./Panel";
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

  it("shows the type of break as text, from rev_breaktype (Amendment A-02)", () => {
    render(<HolidayPanel detail={makeDetail({ breakType: 4 })} />);
    expect(screen.getByText("Respite Care Facility stay")).toBeInTheDocument();
  });

  it("shows an unset break type as 'Not set', not a blank cell", () => {
    render(<HolidayPanel detail={makeDetail({ breakType: null })} />);
    expect(screen.getByText("Not set")).toBeInTheDocument();
  });

  it("shows one combined total-funding-requested figure, not two itemised ones (Amendment A-02/OQ-031)", () => {
    render(
      <HolidayPanel
        detail={makeDetail({
          amountRequested: 1200,
          additionalAmountRequested: 300,
          exceptionalFundingRequested: true,
          costs: 999, // distinct from the 1200+300 total, so the two figures can't collide
        })}
      />,
    );
    expect(screen.getByText(/1,500/)).toBeInTheDocument();
    expect(screen.getByText("Yes")).toBeInTheDocument();
  });

  it("shows the base amount alone, and 'No', when no exceptional funding was requested", () => {
    render(
      <HolidayPanel
        detail={makeDetail({
          amountRequested: 1200,
          additionalAmountRequested: null,
          exceptionalFundingRequested: false,
        })}
      />,
    );
    expect(screen.getByText(/1,200/)).toBeInTheDocument();
    expect(screen.getByText("No")).toBeInTheDocument();
  });

  it("still shows the total-costs figure alongside the total requested (TAD §3.1, FR-060)", () => {
    render(<HolidayPanel detail={makeDetail({ costs: 1500 })} />);
    expect(screen.getByText(/1,500/)).toBeInTheDocument();
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

describe("CareSupportPanel — the structured pair and applicant-type context (TAD §3.2, Amendment A-02/OQ-032)", () => {
  it("shows applicant type, type of care provided and hours of support per week", () => {
    render(
      <CareSupportPanel
        detail={makeDetail({
          applicantType: 2,
          careProvidedType: [1, 7],
          careHoursPerWeek: 4,
        })}
      />,
    );
    expect(screen.getByText("A carer applying on behalf of a disabled person")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Personal care (washing, dressing, toileting, feeding); Emotional support and companionship",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("35 - 59 hours")).toBeInTheDocument();
  });

  it("labels an absent multiselect and an absent band rather than leaving the cell empty", () => {
    render(
      <CareSupportPanel
        detail={makeDetail({ applicantType: null, careProvidedType: null, careHoursPerWeek: null })}
      />,
    );
    expect(screen.getAllByText("Not set")).toHaveLength(2); // applicant type + hours band
    expect(screen.getByText("Not recorded")).toBeInTheDocument(); // the joined multiselect
  });

  it("renders the structured fields UNCONDITIONALLY — not gated by redactionReleased, unlike the free-text trio", () => {
    // The whole point of TAD §3.2: these three are structured facts, not redacted
    // counterparts of a secured source, so the withheld gate must not hide them.
    render(
      <CareSupportPanel
        detail={makeDetail({
          redactionReleased: false,
          applicantType: 1,
          careProvidedType: [3],
          careHoursPerWeek: 2,
        })}
      />,
    );
    expect(screen.getByText("A disabled person")).toBeInTheDocument();
    expect(screen.getByText("Medication management (administering, reminding, organizing)")).toBeInTheDocument();
    expect(screen.getByText("10 - 19 hours")).toBeInTheDocument();
    // The free-text trio must still be withheld, unaffected by the structured fields.
    expect(screen.getByRole("note")).toHaveTextContent(/withheld/i);
  });
});

describe("FinancialEligibilityPanel — Amendment A-05, TAD §3.2.2/§3.2.3, ADR-031/ADR-032", () => {
  it("shows the three unconditional structured facts", () => {
    render(
      <FinancialEligibilityPanel
        detail={makeDetail({ incomeFlag: 1, incomeBand: 3, savingsOver6000: true })}
      />,
    );
    expect(screen.getByText("Within income ceiling")).toBeInTheDocument();
    expect(screen.getByText("20,000 to 29,999 GBP")).toBeInTheDocument();
    expect(screen.getByText("Yes")).toBeInTheDocument();
  });

  it("labels an absent income flag/band as 'Not set' and an absent savings answer as 'Not recorded'", () => {
    render(
      <FinancialEligibilityPanel
        detail={makeDetail({ incomeFlag: null, incomeBand: null, savingsOver6000: null })}
      />,
    );
    expect(screen.getAllByText("Not set")).toHaveLength(2);
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
  });

  it("renders the three Group B restricted rows, never a value, and never a secured query", () => {
    render(<FinancialEligibilityPanel detail={makeDetail()} />);
    // Every restricted row shares one sentence (ADR-032) — assert the count, not any one
    // column's own label, so this test does not need to name a secured column either.
    expect(screen.getAllByText(/protected by column-level security/i)).toHaveLength(3);
  });

  it("withholds the free-text row when release is not affirmatively true", () => {
    render(
      <FinancialEligibilityPanel
        detail={makeDetail({
          redactionReleased: false,
          redactedUnableToFundExplanation: "SENTINEL-EXPLANATION",
        })}
      />,
    );
    expect(screen.getByRole("note")).toHaveTextContent(/withheld/i);
    expect(screen.queryByText(/SENTINEL-EXPLANATION/)).toBeNull();
  });

  it("renders the free text once release is affirmative and populated", () => {
    render(
      <FinancialEligibilityPanel
        detail={makeDetail({
          redactionReleased: true,
          redactedUnableToFundExplanation: "Could not afford the deposit.",
        })}
      />,
    );
    expect(screen.getByText("Could not afford the deposit.")).toBeInTheDocument();
  });

  it("gives the panel a heading, so the print hierarchy survives", () => {
    render(<FinancialEligibilityPanel detail={makeDetail()} />);
    expect(
      screen.getByRole("heading", { level: 2, name: /financial eligibility/i }),
    ).toBeInTheDocument();
  });
});

describe("ConditionProfilePanel — Amendment A-05, TAD §3.2.2, ADR-031", () => {
  it("shows both condition-profile multiselects, joined and labelled", () => {
    render(
      <ConditionProfilePanel
        detail={makeDetail({ conditionProfile: [1, 7], supportRecipientConditionProfile: [3] })}
      />,
    );
    expect(
      screen.getByText("Vision (for example blindness or partial sight); Mental health"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Mobility (for example walking short distances or climbing stairs)"),
    ).toBeInTheDocument();
  });

  it("labels an absent multiselect as 'Not recorded' rather than a blank cell", () => {
    render(
      <ConditionProfilePanel
        detail={makeDetail({ conditionProfile: null, supportRecipientConditionProfile: null })}
      />,
    );
    expect(screen.getAllByText("Not recorded")).toHaveLength(2);
  });

  it("renders no restricted row at all — this board-pack group has none (ADR-032)", () => {
    render(<ConditionProfilePanel detail={makeDetail()} />);
    expect(screen.queryByText(/protected by column-level security/i)).toBeNull();
  });

  it("withholds all four free-text rows when release is not affirmatively true", () => {
    render(
      <ConditionProfilePanel
        detail={makeDetail({
          redactionReleased: false,
          redactedOtherCondition: "SENTINEL-A",
          redactedSupportRecipientOtherCondition: "SENTINEL-B",
          redactedExceptionalFundingDetail: "SENTINEL-C",
          redactedOtherExceptionalCircumstance: "SENTINEL-D",
        })}
      />,
    );
    expect(screen.getByRole("note")).toHaveTextContent(/withheld/i);
    expect(screen.queryByText(/SENTINEL-/)).toBeNull();
  });

  it("renders all four free texts once release is affirmative and populated", () => {
    render(
      <ConditionProfilePanel
        detail={makeDetail({
          redactionReleased: true,
          redactedOtherCondition: "Other condition text.",
          redactedSupportRecipientOtherCondition: "Recipient condition text.",
          redactedExceptionalFundingDetail: "Funding detail text.",
          redactedOtherExceptionalCircumstance: "Circumstance text.",
        })}
      />,
    );
    expect(screen.getByText("Other condition text.")).toBeInTheDocument();
    expect(screen.getByText("Recipient condition text.")).toBeInTheDocument();
    expect(screen.getByText("Funding detail text.")).toBeInTheDocument();
    expect(screen.getByText("Circumstance text.")).toBeInTheDocument();
  });

  it("gives the panel a heading, so the print hierarchy survives", () => {
    render(<ConditionProfilePanel detail={makeDetail()} />);
    expect(
      screen.getByRole("heading", { level: 2, name: /condition and circumstance/i }),
    ).toBeInTheDocument();
  });
});

describe("HelperRefereeContactPanel — Amendment A-05, TAD §3.2.3, ADR-032", () => {
  it("shows the four unconditional helper facts", () => {
    render(
      <HelperRefereeContactPanel
        detail={makeDetail({
          helperOrganisation: "Local carers' charity",
          helperRelationship: "Sister",
          helperDeclarationConsent: true,
          helperDeclarationConsentDate: "2026-07-01T00:00:00Z",
        })}
      />,
    );
    expect(screen.getByText("Local carers' charity")).toBeInTheDocument();
    expect(screen.getByText("Sister")).toBeInTheDocument();
    expect(screen.getByText("Yes")).toBeInTheDocument();
    expect(screen.getByText("1 Jul 2026")).toBeInTheDocument();
  });

  it("renders a missing helper declaration as 'Not recorded', distinct from an explicit No", () => {
    render(<HelperRefereeContactPanel detail={makeDetail({ helperDeclarationConsent: null })} />);
    expect(screen.getAllByText("Not recorded").length).toBeGreaterThan(0);
    expect(screen.queryByText("No")).toBeNull();
  });

  it("renders all eight Group B restricted rows, never a value, and never a secured query", () => {
    render(<HelperRefereeContactPanel detail={makeDetail()} />);
    expect(screen.getAllByText(/protected by column-level security/i)).toHaveLength(8);
  });

  it("gives the panel a heading, so the print hierarchy survives", () => {
    render(<HelperRefereeContactPanel detail={makeDetail()} />);
    expect(
      screen.getByRole("heading", { level: 2, name: /helper, referee and emergency contact/i }),
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

/**
 * ADDED Revision 4 (2026-08-27) — TAD §8.5 point 1. NOTHING ABOVE THIS BLOCK WAS MODIFIED.
 *
 * The four panels that render the redaction state machine now select a `StateMessage` tone
 * from the state's own `kind`, so `withheld` and `released-empty` are visually distinct.
 * Every assertion above already pins the WORDS of both states — `:166` the exact
 * `released-empty` sentence, `:178-181` that it does not contain "withheld" — and those are
 * untouched. What no assertion above can see is the two states rendering as the SAME BOX,
 * which is a defect a restyle can introduce with every word and every role still correct,
 * and which would tell a trustee something false about Art. 9 data.
 *
 * WRITTEN AS A RELATION, NOT AS A CLASS NAME. Vitest processes no CSS, so a CSS-Module class
 * arrives as an opaque hashed string. Each panel's note is compared against a bare
 * `StateMessage` rendered with the tone it is SUPPOSED to have — which pins the mapping
 * (a swap fails) and the distinctness (a collapse fails) without naming any class inside
 * `components/ds`, whose class names are a conversion of an external artefact and will be
 * re-diffed against it.
 */
describe("the redaction states are visually distinct, and mapped the right way round", () => {
  /** The class attribute of the one `role="note"` a fresh render produced. */
  function toneClassOf(element: React.ReactElement): string {
    const { unmount } = render(element);
    const value = screen.getByRole("note").getAttribute("class") ?? "";
    unmount();
    return value;
  }

  const MUTED = () => toneClassOf(<StateMessage heading="H" explanation="E" tone="muted" />);
  const QUIET = () => toneClassOf(<StateMessage heading="H" explanation="E" tone="quiet" />);

  /**
   * Each panel in both non-released states. The `released-empty` fixtures rely on
   * `makeDetail`'s defaults, where every redacted column is already null — so affirming
   * release is the whole of what each one says.
   */
  const PANELS = [
    {
      name: "NarrativePanel",
      withheld: <NarrativePanel detail={makeDetail({ redactionReleased: false })} />,
      empty: <NarrativePanel detail={makeDetail({ redactionReleased: true })} />,
    },
    {
      name: "CareSupportPanel",
      withheld: <CareSupportPanel detail={makeDetail({ redactionReleased: false })} />,
      empty: <CareSupportPanel detail={makeDetail({ redactionReleased: true })} />,
    },
    {
      name: "FinancialEligibilityPanel",
      withheld: <FinancialEligibilityPanel detail={makeDetail({ redactionReleased: false })} />,
      empty: <FinancialEligibilityPanel detail={makeDetail({ redactionReleased: true })} />,
    },
    {
      name: "ConditionProfilePanel",
      withheld: <ConditionProfilePanel detail={makeDetail({ redactionReleased: false })} />,
      empty: <ConditionProfilePanel detail={makeDetail({ redactionReleased: true })} />,
    },
  ];

  it("gives withheld and released-empty different treatments in all four panels", () => {
    for (const panel of PANELS) {
      expect(toneClassOf(panel.withheld), `${panel.name} withheld`).not.toBe(
        toneClassOf(panel.empty),
      );
    }
  });

  it("maps withheld to the muted tone and released-empty to the quiet one, not the reverse", () => {
    const muted = MUTED();
    const quiet = QUIET();
    // The reference tones must themselves differ, or the two assertions below would both
    // pass against one collapsed treatment and prove nothing.
    expect(muted).not.toBe(quiet);
    for (const panel of PANELS) {
      expect(toneClassOf(panel.withheld), `${panel.name} withheld -> muted`).toBe(muted);
      expect(toneClassOf(panel.empty), `${panel.name} released-empty -> quiet`).toBe(quiet);
    }
  });

  it("keeps both states a note, never an alert, in all four panels", () => {
    // Unchanged from before this pass and asserted again here because the tone wiring is the
    // change that could have reached for `role="alert"` to make the two states differ. An
    // alert would interrupt a screen-reader trustee on EVERY navigation to tell them
    // something entirely expected (`Panel.tsx`'s own reasoning).
    for (const panel of PANELS) {
      for (const state of [panel.withheld, panel.empty]) {
        const { unmount } = render(state);
        expect(screen.getByRole("note"), panel.name).toBeInTheDocument();
        expect(screen.queryByRole("alert"), panel.name).toBeNull();
        unmount();
      }
    }
  });
});
