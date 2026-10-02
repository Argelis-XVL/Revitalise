/**
 * WI-0005 — the detail screen follows the Trustee Pack verbatim: every section in the Pack's
 * order, and inside every section every row in the Pack's order with the Pack's label.
 *
 * `PACK_PAGES_1_2` below is a TRANSCRIPTION of `docs/Import/3. Round 4 - Individual
 * Applications.pdf` pages 1-2, taken from `pdftotext -layout` output on 2026-09-30 and checked
 * against the rendered pages. It is deliberately a second, independent copy of the labels: the
 * spec (`applicationDetailLayout.ts`) is what the screen renders, and this is what the spec is
 * held to. Editing a label, moving a row or dropping one in the spec fails here, naming the row.
 * Change this transcription only when the Pack itself changes, and cite the new source.
 *
 * `APPROVED_DEVIATIONS` below is the second half of the specification: the rows the reviewer
 * approved that the Pack does NOT print (code review, 2026-09-30, Xander Lykopoulos, "Approved
 * with the above changes"). Each carries the decision quoted verbatim. The spec's Pack rows must
 * equal the transcription, and its non-Pack rows must equal this list, in position — so a row can
 * be neither added outside the Pack nor dropped from it without one of these tests naming it.
 */
import { describe, expect, it } from "vitest";
import {
  APPLICATION_DETAIL_LAYOUT,
  TRUSTEE_PACK_SECTIONS,
  isRowVisible,
} from "./applicationDetailLayout";
import type { DetailCell, DetailRow, DetailSection } from "./applicationDetailLayout";
import { RESTRICTED_VALUE_TEXT } from "./fieldCatalogue";
import { TRUSTEE_RESTRICTED_FIELD_CATALOGUE } from "../generated/trusteeRestrictedFieldCatalogue";
import { makeDetail } from "../test/harness";
import type { ApplicationDetail } from "../dataverse/types";

interface TranscribedSection {
  heading: string;
  groups: { heading: string | null; labels: string[] }[];
}

const PACK_PAGES_1_2: TranscribedSection[] = [
  {
    // p.1 — "Revitalise Grants – Month 4 Application Panel, INDIVIDUAL- Summary"
    heading: "Summary",
    groups: [
      {
        heading: null,
        labels: [
          "Application ID",
          "Are you?",
          "Overall Current Circumstance Score (Out of 60, 60 as worst)",
          "Start Date",
          "End Date",
          "Individual Total Amount Requesting Revitalise inc. Exceptional Funding",
          "Exceptional Funding Amount",
        ],
      },
    ],
  },
  {
    heading: "Application Details",
    groups: [
      {
        heading: null,
        labels: [
          "Type of Break",
          "Location of Activity",
          "Start Date",
          "End Date",
          "Accommodation or Activity Cost",
          "Travel Costs",
          "Other Costs",
          "Total Estimated Cost",
          "Amount Requesting Revitalise Individual",
          "Exceptional Amount Requested",
          "Exceptional Circumstance",
          "Please briefly explain how this break would benefit you",
          "Please briefly explain why you’re unable to fund this break yourself?",
        ],
      },
    ],
  },
  {
    heading: "About Applicant",
    groups: [
      {
        heading: null,
        labels: [
          "Are you?",
          "Do you or the person you support have a disability as defined by the Equality Act 2010?",
          "Please select all conditions or illnesses that apply?",
          "Brief Confirmation",
          "As a carer, what type of care and support do you personally provide?",
          "Brief Description of Care Support Received or Provided",
          "As a carer, on average how many hours of support do you provide a week?",
        ],
      },
    ],
  },
  {
    // p.2
    heading: "Current Circumstances",
    groups: [
      {
        heading: null,
        labels: [
          "Overall Current Circumstances Score (Out of 60)",
          "Overall, how satisfied are you with your life nowadays? (0 being not at all)",
        ],
      },
      {
        heading: "In the last 2 weeks…",
        labels: [
          "I’ve been feeling optimistic about the future",
          "I’ve been feeling useful",
          "I’ve been feeling relaxed",
          "I’ve been dealing with problems well",
          "I’ve been thinking clearly",
          "I’ve been feeling close to other people",
          "I’ve been able to make up my own mind about things",
        ],
      },
      {
        heading: "In the last year…",
        labels: [
          "Go out and do something you enjoy",
          "Enjoy other people’s company",
          "Have a break when you’ve needed one",
        ],
      },
    ],
  },
  {
    heading: "Financial Eligibility",
    groups: [
      {
        heading: null,
        labels: [
          "Do you currently receive means tested benefits?",
          "Benefit Provider",
          "Are you currently working?",
          "Approximate Household Income",
          "If you have significant care costs, please briefly explain",
          "Do you savings over £6,000?",
        ],
      },
    ],
  },
];

interface ApprovedDeviation {
  id: string;
  /** Where it sits: the id of the row it directly follows, or "top" (first rows of the section). */
  after: string;
  section: string;
  label: string;
  /** Always rendered, or only when a condition holds. */
  conditional: boolean;
  /** The reviewer's words, verbatim (2026-09-30). */
  decision: string;
}

const APPROVED_DEVIATIONS: ApprovedDeviation[] = [
  // "4. Rev_status and rev_reviewround can be shown at the top. in the summary section."
  {
    id: "S0a",
    after: "top",
    section: "Summary",
    label: "Status",
    conditional: false,
    decision: "Rev_status and rev_reviewround can be shown at the top. in the summary section.",
  },
  {
    id: "S0b",
    after: "S0a",
    section: "Summary",
    label: "Review round",
    conditional: false,
    decision: "Rev_status and rev_reviewround can be shown at the top. in the summary section.",
  },
  // "otherexceptionale circumstance redacted should go with D11 if in D11 other is selected."
  {
    id: "D11a",
    after: "D11",
    section: "Application Details",
    label: "Other exceptional circumstance",
    conditional: true,
    decision: "otherexceptionale circumstance redacted should go with D11 if in D11 other is selected.",
  },
  // "The same goes for otherconditionredacted and supportrecipientotherconditionredacted This
  //  one has to be shown if other is selected in conditionprofile A3"
  {
    id: "A3a",
    after: "A3",
    section: "About Applicant",
    label: "Other condition notes",
    conditional: true,
    decision:
      "The same goes for otherconditionredacted and supportrecipientotherconditionredacted This one " +
      "has to be shown if other is selected in conditionprofile A3",
  },
  {
    id: "A3b",
    after: "A3a",
    section: "About Applicant",
    label: "Other condition notes (the person you support)",
    conditional: true,
    decision:
      "The same goes for otherconditionredacted and supportrecipientotherconditionredacted This one " +
      "has to be shown if other is selected in conditionprofile A3",
  },
];

function allRows(): { section: string; row: DetailRow }[] {
  return APPLICATION_DETAIL_LAYOUT.flatMap((section) =>
    section.groups.flatMap((group) => group.rows.map((row) => ({ section: section.heading, row }))),
  );
}

/**
 * The spec as the Pack would print it: approved deviation rows dropped, and a group whose heading
 * is an approved deviation (not printed by the Pack) folded back into the Pack group before it —
 * so the transcription above is compared to the Pack's own rows, sub-headings and order, untouched.
 */
function shape(sections: readonly DetailSection[]): TranscribedSection[] {
  return sections.map((section) => {
    const groups: TranscribedSection["groups"] = [];
    for (const group of section.groups) {
      const labels = group.rows
        .filter((row) => row.approvedDeviation === undefined)
        .map((row) => row.label);
      const previous = groups.at(-1);
      if (group.headingDeviation !== undefined && previous !== undefined) {
        previous.labels.push(...labels);
      } else {
        groups.push({ heading: group.heading, labels });
      }
    }
    return { heading: section.heading, groups };
  });
}

function cellOf(id: string, detail: ApplicationDetail): DetailCell {
  for (const section of APPLICATION_DETAIL_LAYOUT) {
    for (const group of section.groups) {
      const row = group.rows.find((candidate) => candidate.id === id);
      if (row !== undefined) return row.cell(detail);
    }
  }
  throw new Error(`No row ${id}`);
}

function textOf(id: string, overrides: Partial<ApplicationDetail> = {}): string {
  const cell = cellOf(id, makeDetail(overrides));
  if (cell.kind === "value" || cell.kind === "long-text") return cell.text;
  throw new Error(`Row ${id} is a ${cell.kind} cell, not a value`);
}

describe("the Pack's sections and rows, verbatim and in order (WI-0005)", () => {
  it("has the Pack's five sections, in the Pack's order", () => {
    expect(TRUSTEE_PACK_SECTIONS.map((s) => s.heading)).toEqual(
      PACK_PAGES_1_2.map((s) => s.heading),
    );
  });

  // One assertion per section, so a failure names the section that drifted.
  for (const [index, transcribed] of PACK_PAGES_1_2.entries()) {
    it(`renders "${transcribed.heading}" with exactly the Pack's rows, labels and sub-headings, in order`, () => {
      expect(shape(TRUSTEE_PACK_SECTIONS.slice(index, index + 1))[0]).toEqual(transcribed);
    });
  }

  it("covers all 45 rows the Pack prints for one application", () => {
    const count = TRUSTEE_PACK_SECTIONS.flatMap((s) => s.groups)
      .flatMap((g) => g.rows)
      .filter((r) => r.approvedDeviation === undefined).length;
    const transcribed = PACK_PAGES_1_2.flatMap((s) => s.groups).flatMap((g) => g.labels).length;
    expect(count).toBe(transcribed);
    // Count-coupled BY DESIGN (C-TECH-067) to the source PDF, not to this repository's source:
    // pages 1-2 print 7 + 13 + 7 + 12 + 6 = 45 rows. Change it only if the Pack changes.
    expect(transcribed).toBe(45);
  });

  it("renders the five Pack sections and nothing else — no portal-only section (reviewer, 2026-09-30)", () => {
    expect(APPLICATION_DETAIL_LAYOUT).toEqual(TRUSTEE_PACK_SECTIONS);
    expect(APPLICATION_DETAIL_LAYOUT.map((s) => s.heading)).not.toContain(
      "Further details (not in the Trustee Pack)",
    );
  });

  it("numbers every Pack row by its Pack position, so the field map's ids line up", () => {
    const prefixes = ["S", "D", "A", "C", "F"];
    TRUSTEE_PACK_SECTIONS.forEach((section, index) => {
      const ids = section.groups
        .flatMap((g) => g.rows)
        .filter((r) => r.approvedDeviation === undefined)
        .map((r) => r.id);
      expect(ids).toEqual(ids.map((_, n) => `${prefixes[index]}${String(n + 1)}`));
    });
  });

  it("gives every row on the screen a unique id", () => {
    const ids = APPLICATION_DETAIL_LAYOUT.flatMap((s) => s.groups)
      .flatMap((g) => g.rows)
      .map((r) => r.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe("the reviewer's approved deviations from the Pack (code review, 2026-09-30)", () => {
  it("has exactly the approved non-Pack rows, each quoting its decision, and no others", () => {
    const actual = allRows()
      .filter(({ row }) => row.approvedDeviation !== undefined)
      .map(({ section, row }) => ({
        id: row.id,
        section,
        label: row.label,
        conditional: row.visible !== undefined,
        decision: row.approvedDeviation,
      }));
    expect(actual).toEqual(
      APPROVED_DEVIATIONS.map(({ id, section, label, conditional, decision }) => ({
        id,
        section,
        label,
        conditional,
        decision,
      })),
    );
  });

  it("places each deviation exactly where the decision puts it", () => {
    for (const deviation of APPROVED_DEVIATIONS) {
      const section = APPLICATION_DETAIL_LAYOUT.find((s) => s.heading === deviation.section);
      const ids = (section?.groups ?? []).flatMap((g) => g.rows).map((r) => r.id);
      const at = ids.indexOf(deviation.id);
      if (deviation.after === "top") {
        expect(at, deviation.id).toBe(0);
      } else {
        expect(ids[at - 1], deviation.id).toBe(deviation.after);
      }
    }
  });

  it("gives every Pack row no visibility condition — a Pack row always renders, answered or not", () => {
    for (const { row } of allRows()) {
      if (row.approvedDeviation === undefined) expect(row.visible, row.id).toBeUndefined();
    }
  });

  it("shows the other-exceptional-circumstance note only when D11 is 'Other (please specify)'", () => {
    const row = allRows().find(({ row: r }) => r.id === "D11a")?.row as DetailRow;
    expect(isRowVisible(row, makeDetail({ exceptionalCircumstance: 4 }))).toBe(true);
    for (const other of [null, 1, 2, 3]) {
      expect(isRowVisible(row, makeDetail({ exceptionalCircumstance: other })), String(other)).toBe(false);
    }
  });

  it("shows each other-condition note only when ITS OWN condition profile includes 'Other'", () => {
    const own = allRows().find(({ row: r }) => r.id === "A3a")?.row as DetailRow;
    const supported = allRows().find(({ row: r }) => r.id === "A3b")?.row as DetailRow;
    expect(isRowVisible(own, makeDetail({ conditionProfile: [3, 10] }))).toBe(true);
    expect(isRowVisible(own, makeDetail({ conditionProfile: [3] }))).toBe(false);
    expect(isRowVisible(own, makeDetail({ conditionProfile: null }))).toBe(false);
    expect(isRowVisible(supported, makeDetail({ supportRecipientConditionProfile: [10] }))).toBe(true);
    expect(isRowVisible(supported, makeDetail({ conditionProfile: [10] }))).toBe(false);
  });

  it("gates every deviation's free text like every other redacted answer", () => {
    for (const id of ["D11a", "A3a", "A3b"]) {
      const cell = cellOf(id, makeDetail({ redactionReleased: false }));
      expect(cell.kind === "redacted" && cell.state.kind, id).toBe("withheld");
    }
  });
});

describe("approved sub-headings the Pack does not print (WI-0008 review, 2026-09-30)", () => {
  // "Create more white space for the sections of the wellbeing answers. Make it three distinct
  //  sections with more white space in between the sections. Now it show the section title "in
  //  the last two weeks" directly under the last question."
  const DECISION =
    "Create more white space for the sections of the wellbeing answers. Make it three distinct " +
    "sections with more white space in between the sections.";

  it("has exactly one approved sub-heading, 'Life satisfaction', quoting its decision", () => {
    const approved = APPLICATION_DETAIL_LAYOUT.flatMap((s) =>
      s.groups
        .filter((g) => g.headingDeviation !== undefined)
        .map((g) => ({ section: s.heading, heading: g.heading, decision: g.headingDeviation })),
    );
    expect(approved).toEqual([
      { section: "Current Circumstances", heading: "Life satisfaction", decision: DECISION },
    ]);
  });

  it("splits Current Circumstances into the score, then three headed wellbeing sub-sections", () => {
    const section = APPLICATION_DETAIL_LAYOUT.find((s) => s.heading === "Current Circumstances");
    expect(
      section?.groups.map((g) => ({ heading: g.heading, ids: g.rows.map((r) => r.id) })),
    ).toEqual([
      { heading: null, ids: ["C1"] },
      { heading: "Life satisfaction", ids: ["C2"] },
      { heading: "In the last 2 weeks\u2026", ids: ["C3", "C4", "C5", "C6", "C7", "C8", "C9"] },
      { heading: "In the last year\u2026", ids: ["C10", "C11", "C12"] },
    ]);
  });
});

describe("restricted rows — rendered in position, never requested (FR-078, ADR-032)", () => {
  it("renders the three Group B financial rows restricted, each with a real catalogue key", () => {
    const keys = new Set(TRUSTEE_RESTRICTED_FIELD_CATALOGUE.map((entry) => entry.key));
    for (const [id, key] of [
      ["F1", "benefit-status"],
      ["F2", "benefit-provider"],
      ["F3", "employment-status"],
    ] as const) {
      expect(cellOf(id, makeDetail())).toEqual({ kind: "restricted", catalogueKey: key });
      expect(keys.has(key)).toBe(true);
    }
  });

  it("renders the care-costs explanation from its REDACTED twin, gated — reviewer, 2026-09-30", () => {
    // "3. Show [the secured care-costs column; its name is never written in this app] as a narrativescrubbed version, like other columns. Add
    //  the column to the datamodel."
    const withheld = cellOf("F5", makeDetail({ redactionReleased: false, redactedCareCostsExplanation: "x" }));
    expect(withheld.kind === "redacted" && withheld.state.kind).toBe("withheld");
    expect(
      cellOf("F5", makeDetail({ redactionReleased: true, redactedCareCostsExplanation: "Carer costs" })),
    ).toEqual({ kind: "redacted", state: { kind: "released", text: "Carer costs" } });
  });

  it("uses the one restricted wording everywhere", () => {
    expect(RESTRICTED_VALUE_TEXT).toMatch(/restricted/i);
  });
});

describe("row values — the rows this pass added or re-sourced", () => {
  it("shows the itemised costs and both amounts as separate rows (reverses OQ-031)", () => {
    const overrides = {
      accommodationCost: 4000,
      travelCost: 2000,
      otherCost: 1000,
      costs: 7000,
      amountRequested: 500,
      additionalAmountRequested: 250,
    };
    expect(textOf("D5", overrides)).toBe("£4,000.00");
    expect(textOf("D6", overrides)).toBe("£2,000.00");
    expect(textOf("D7", overrides)).toBe("£1,000.00");
    expect(textOf("D8", overrides)).toBe("£7,000.00");
    expect(textOf("D9", overrides)).toBe("£500.00");
    expect(textOf("D10", overrides)).toBe("£250.00");
    expect(textOf("S6", overrides)).toBe("£750.00");
    expect(textOf("S7", overrides)).toBe("£250.00");
  });

  it("shows Start Date and End Date as two rows, from the two date columns", () => {
    const overrides = { preferredStart: "2026-08-01T00:00:00Z", preferredEnd: "2026-08-11T00:00:00Z" };
    expect(textOf("S4", overrides)).toBe("1 Aug 2026");
    expect(textOf("S5", overrides)).toBe("11 Aug 2026");
    expect(textOf("D3", overrides)).toBe("1 Aug 2026");
    expect(textOf("D4", overrides)).toBe("11 Aug 2026");
  });

  it("reads 'Not recorded' for an absent date — the grant admin fills Start/End by hand (reviewer, 2026-09-30)", () => {
    // "Don't show the dates. The grant admin can fill the dates manually now, while we wait for
    //  the form to have the start and end dates." The typed provisional date is not shown.
    const overrides = { preferredStart: null, preferredEnd: null };
    expect(textOf("S4", overrides)).toBe("Not recorded");
    expect(textOf("D4", overrides)).toBe("Not recorded");
  });

  it("shows Status and Review round at the top of the Summary", () => {
    expect(textOf("S0a", { status: 6 })).toBe("Eligible for Panel");
    expect(textOf("S0b", { reviewRound: "2026-Q4" })).toBe("2026-Q4");
  });

  it("labels the exceptional circumstance, and reads 'Not recorded' when none was asked for", () => {
    expect(textOf("D11", { exceptionalCircumstance: 1 })).toBe("Palliative care");
    expect(textOf("D11", { exceptionalCircumstance: null })).toBe("Not recorded");
  });

  it("shows whichever Equality Act answer the form asked, and both when both are answered", () => {
    expect(textOf("A2", { hasEqualityActDisability: true })).toBe("Yes");
    expect(textOf("A2", { supportRecipientHasEqualityActDisability: false })).toBe("No");
    expect(textOf("A2", {})).toBe("Not recorded");
    expect(
      textOf("A2", { hasEqualityActDisability: true, supportRecipientHasEqualityActDisability: false }),
    ).toBe("You: Yes; The person you support: No");
  });

  it("shows the condition categories of whoever the form asked about", () => {
    expect(textOf("A3", { conditionProfile: [3] })).toBe(
      "Mobility (for example walking short distances or climbing stairs)",
    );
    expect(textOf("A3", { supportRecipientConditionProfile: [6, 7] })).toBe("Memory; Mental health");
  });

  it("gates Brief Confirmation like every other redacted answer", () => {
    const withheld = cellOf(
      "A4",
      makeDetail({ redactionReleased: false, redactedDisabilityImpactDescription: "Anonymised" }),
    );
    expect(withheld.kind === "redacted" && withheld.state.kind).toBe("withheld");
    const released = cellOf(
      "A4",
      makeDetail({ redactionReleased: true, redactedDisabilityImpactDescription: "Anonymised" }),
    );
    expect(released).toEqual({ kind: "redacted", state: { kind: "released", text: "Anonymised" } });
  });

  it("places the two narrative-style answers in Application Details, gated (D12, D13)", () => {
    for (const id of ["D12", "D13"]) {
      const cell = cellOf(id, makeDetail({ redactionReleased: false }));
      expect(cell.kind === "redacted" && cell.state.kind, id).toBe("withheld");
    }
    expect(
      cellOf("D12", makeDetail({ redactionReleased: true, redactedNarrative: "Benefit" })),
    ).toEqual({ kind: "redacted", state: { kind: "released", text: "Benefit" } });
    expect(
      cellOf("D13", makeDetail({ redactionReleased: true, redactedUnableToFundExplanation: "Why" })),
    ).toEqual({ kind: "redacted", state: { kind: "released", text: "Why" } });
  });

  it("shows the life-satisfaction answer as entered, and each wellbeing answer on its own scale", () => {
    const answers = { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 1, 8: 1, 9: 4, 10: 5 } as const;
    const overrides = { lifeSatisfaction: 1, wellbeingAnswers: answers };
    expect(textOf("C1", { circumstanceScore: 59 })).toBe("59");
    expect(textOf("C2", overrides)).toBe("1");
    // 1-7: the frequency scale.
    expect(textOf("C3", overrides)).toBe("None of the time");
    expect(textOf("C4", overrides)).toBe("Rarely");
    expect(textOf("C8", overrides)).toBe("Not sure");
    expect(textOf("C9", overrides)).toBe("None of the time");
    // 8-10: the agreement scale — never labelled with a frequency word.
    expect(textOf("C10", overrides)).toBe("Strongly Disagree");
    expect(textOf("C11", overrides)).toBe("Agree");
    expect(textOf("C12", overrides)).toBe("Strongly Agree");
  });

  it("reads 'Not recorded' for an unanswered wellbeing question, never 'Not set'", () => {
    expect(textOf("C3")).toBe("Not recorded");
    expect(textOf("C2")).toBe("Not recorded");
  });

  it("shows the household income band and the savings answer", () => {
    expect(textOf("F4", { incomeBand: 1 })).toBe("Under £15,000");
    expect(textOf("F6", { savingsOver6000: false })).toBe("No");
    expect(textOf("F6", { savingsOver6000: null })).toBe("Not recorded");
  });
});

describe("rows the reviewer ruled out stay out ('The other columns we don't need')", () => {
  it("shows none of the removed extras anywhere on the screen", () => {
    const labels = allRows().map(({ row }) => row.label);
    for (const removed of [
      "Provider preference",
      "Provisional date (as entered on the form)",
      "Exceptional funding requested",
      "Exceptional funding detail",
      "Other care provided",
      "Example of care provided",
      "Score breakdown (from the scoring automation)",
      "Income flag",
    ]) {
      expect(labels, removed).not.toContain(removed);
    }
  });
});
