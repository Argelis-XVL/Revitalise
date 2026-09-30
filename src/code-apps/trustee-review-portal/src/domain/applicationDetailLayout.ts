/**
 * The individual application detail screen, section by section and row by row, in the Trustee
 * Pack's own order and with the Pack's own labels — WI-0005 (EF-04), wbs:6.8.
 *
 * ## This file IS the specification the screen renders from
 *
 * `CasePanels.tsx`'s `DetailSectionPanel` renders exactly what is listed here, in this order,
 * and nothing else; `ApplicationDetailPage.tsx` renders `APPLICATION_DETAIL_LAYOUT` in order.
 * `applicationDetailLayout.test.ts` pins every section heading and every row label against a
 * transcription of the source PDF, and `ApplicationDetailPage.test.tsx` asserts the rendered
 * screen matches this spec. So a future edit cannot move, drop or relabel a row without a
 * test naming the row.
 *
 * Source: `docs/Import/3. Round 4 - Individual Applications.pdf`, pages 1-2 (one application;
 * page 3 starts the next). Labels are copied character for character, including the Pack's
 * curly apostrophes (U+2019), its ellipses (U+2026), and its own wording where it is
 * ungrammatical ("Do you savings over £6,000?"). The PDF's "fi"/"fl" ligatures are font
 * artefacts and are written as plain letters. The row-by-row map to Dataverse columns, with the
 * reason for every row that is not a plain value, is
 * `docs/development/trustee-portal-pack-field-map.md`; row ids (S1, D5, …) are shared with it.
 *
 * ## Why the earlier fixes failed, stated so it is not repeated
 *
 * Revisions 12-14 (see the headers of `CasePanels.tsx` and `ApplicationDetailPage.tsx`)
 * reordered PANELS against the Pack's section order, but the panels were this app's own
 * groupings, with their own field sets and labels. No pass ever listed the Pack's rows one by
 * one, so rows inside a section stayed missing, relabelled or in another section (the
 * "unable to fund" answer sat under Financial Eligibility; the Pack prints it in Application
 * Details). The fix is to render from the Pack's row list, not to move panels again.
 *
 * ## Rows the Pack shows that a trustee cannot read
 *
 * Three rows are secured columns in `REV_TrusteeRestricted` and have a restricted-catalogue
 * entry (FR-078, ADR-032): they render in their Pack position with the restricted text,
 * and are never requested. No secured column is named in this file
 * (`no-secured-columns-in-code-app`). The care-costs explanation (F5) was a fourth until the
 * reviewer's 2026-09-30 decision gave it a redacted twin; it now renders that twin, withheld
 * until released, like the Pack's other free-text answers.
 *
 * ## The reviewer's approved deviations from the Pack (code review, 2026-09-30)
 *
 * The reviewer approved the Pack-verbatim screen "with the above changes". Every row that is not
 * a Pack row carries `approvedDeviation`, quoting the decision, and the spec test lists them
 * explicitly, so a deviation cannot be added or dropped silently:
 *
 *   - Status and Review round at the TOP of the Summary section;
 *   - the redacted "other exceptional circumstance" directly after D11, shown only when D11 is
 *     "Other (please specify)";
 *   - the redacted "other condition" notes directly after A3, each shown only when its own
 *     condition profile includes "Other (please specify)".
 *
 * Everything else this screen once showed outside the Pack (the score breakdown text, the
 * provisional date text, the income flag, the exceptional-funding flag, the exceptional-funding
 * detail, the care example and other-care type) was removed: "The other columns we don't
 * need." The portal-only section that held them is gone.
 */
import {
  AGREEMENT_RESPONSE_LABELS,
  APPLICANT_TYPE_LABELS,
  APPLICATION_STATUS_LABELS,
  BREAK_TYPE_LABELS,
  CARE_HOURS_BAND_LABELS,
  CARE_PROVIDED_TYPE_LABELS,
  CONDITION_PROFILE_LABELS,
  EXCEPTIONAL_CIRCUMSTANCE_LABELS,
  INCOME_BAND_LABELS,
  LIKERT_RESPONSE_LABELS,
  LIFE_SATISFACTION_LABELS,
  optionLabel,
  optionLabels,
  WELLBEING_QUESTION_HEADINGS,
} from "../dataverse/schema";
import type { ApplicationDetail, WellbeingQuestionNumber } from "../dataverse/types";
import {
  NOT_RECORDED,
  formatAmount,
  formatDate,
  formatScore,
  formatText,
  formatYesNo,
  totalFundingRequested,
} from "./format";
import { redactedTextState } from "./visibility";
import type { RedactedTextState } from "./visibility";

/** What one row's value cell holds. */
export type DetailCell =
  /** A short value on one line. */
  | { kind: "value"; text: string }
  /** Free text whose line breaks matter. Never gated — only non-redacted columns use it. */
  | { kind: "long-text"; text: string }
  /** A `…redacted` answer, gated by `redactionReleased` (`domain/visibility.ts`). */
  | { kind: "redacted"; state: RedactedTextState }
  /**
   * A secured column the trustee cannot read and this app never requests. `catalogueKey` names
   * its build-derived restricted-catalogue entry (`src/generated/trusteeRestrictedFieldCatalogue.ts`)
   * where one exists; `null` where the column is secured but outside the catalogue.
   */
  | { kind: "restricted"; catalogueKey: string | null };

export interface DetailRow {
  /**
   * Row id shared with the field map: S/D/A/C/F + the Pack's own row number. A reviewer-approved
   * row that is not in the Pack takes the id of the Pack row it follows plus a letter (D11a,
   * A3a) or, at the top of the Summary, S0a/S0b.
   */
  readonly id: string;
  /** The label exactly as printed in the Pack (or, for a deviation row, this app's own label). */
  readonly label: string;
  readonly cell: (detail: ApplicationDetail) => DetailCell;
  /**
   * When present, the row renders only when this returns true. Used only by reviewer-approved
   * conditional rows; every Pack row is always rendered, answered or not.
   */
  readonly visible?: (detail: ApplicationDetail) => boolean;
  /** Set on every row that is NOT a Pack row: the reviewer's decision, quoted. */
  readonly approvedDeviation?: string;
}

/** Whether a row renders for this application. */
export function isRowVisible(row: DetailRow, detail: ApplicationDetail): boolean {
  return row.visible === undefined ? true : row.visible(detail);
}

export interface DetailGroup {
  /** A sub-heading the Pack prints inside a section ("In the last 2 weeks…"), or `null`. */
  readonly heading: string | null;
  readonly rows: readonly DetailRow[];
  /**
   * Set when `heading` is NOT printed by the Pack but was approved by the reviewer: the decision,
   * quoted. A group carrying it is a visual split of the Pack group before it — its rows are
   * still that Pack group's rows, in the Pack's order, which is how the transcription test reads
   * them.
   */
  readonly headingDeviation?: string;
}

export interface DetailSection {
  readonly id: string;
  /** The Pack's section heading, verbatim. */
  readonly heading: string;
  /** Every section is one of the Pack's five; kept as a field so a future non-Pack section must say so. */
  readonly origin: "pack";
  readonly groups: readonly DetailGroup[];
}

/* ------------------------------------------------------------------------------------- *
 * Cell builders — small, so each row below reads as one line of the Pack.
 * ------------------------------------------------------------------------------------- */

function value(text: string): DetailCell {
  return { kind: "value", text };
}

function redacted(detail: ApplicationDetail, text: string | null): DetailCell {
  return { kind: "redacted", state: redactedTextState(detail.redactionReleased, text) };
}

/**
 * The Pack prints ONE row where the form asks one of two questions depending on who is
 * applying ("Do you…" to a disabled applicant, "Does the person you support…" to a carer), and
 * each answer has its own column. At most one is normally answered, so the row shows whichever
 * is; if both are, it shows both, labelled, rather than silently choosing one.
 */
function eitherPerson(
  own: string | null,
  supported: string | null,
  separator = "; ",
): string | null {
  if (own === null && supported === null) return null;
  if (supported === null) return own;
  if (own === null) return supported;
  return `You: ${own}${separator}The person you support: ${supported}`;
}

function yesNoOrNull(answer: boolean | null): string | null {
  return answer === null ? null : formatYesNo(answer);
}

function blankToNull(text: string | null): string | null {
  return text === null || text.trim().length === 0 ? null : text;
}

/** `OptionSets/rev_exceptionalcircumstance.xml` and `rev_conditionprofile.xml`: "Other (please specify)". */
const EXCEPTIONAL_CIRCUMSTANCE_OTHER = 4;
const CONDITION_PROFILE_OTHER = 10;

const DECISION_STATUS_AT_TOP =
  "Rev_status and rev_reviewround can be shown at the top. in the summary section.";
const DECISION_OTHER_EXCEPTIONAL =
  "otherexceptionale circumstance redacted should go with D11 if in D11 other is selected.";
const DECISION_WELLBEING_SECTIONS =
  "Create more white space for the sections of the wellbeing answers. Make it three distinct " +
  "sections with more white space in between the sections.";
const DECISION_OTHER_CONDITION =
  "The same goes for otherconditionredacted and supportrecipientotherconditionredacted This one " +
  "has to be shown if other is selected in conditionprofile A3";

function wellbeing(
  detail: ApplicationDetail,
  question: WellbeingQuestionNumber,
  labels: Readonly<Record<number, string>>,
): DetailCell {
  const answer = detail.wellbeingAnswers[question];
  return value(answer === null ? NOT_RECORDED : optionLabel(labels, answer));
}

/* ------------------------------------------------------------------------------------- *
 * The Pack's five sections, in the Pack's order.
 * ------------------------------------------------------------------------------------- */

/** Pack p.1, "Revitalise Grants – Month 4 Application Panel, INDIVIDUAL- Summary". */
const SUMMARY: DetailSection = {
  id: "summary",
  heading: "Summary",
  origin: "pack",
  groups: [
    {
      heading: null,
      rows: [
        {
          id: "S0a",
          label: "Status",
          cell: (d) => value(optionLabel(APPLICATION_STATUS_LABELS, d.status)),
          approvedDeviation: DECISION_STATUS_AT_TOP,
        },
        {
          id: "S0b",
          label: "Review round",
          cell: (d) => value(formatText(d.reviewRound)),
          approvedDeviation: DECISION_STATUS_AT_TOP,
        },
        // The Pack's printed value (e.g. 92964) is the website's entry number; the reviewer ruled
        // 2026-09-30 that Application ID "is the rev number (e.g. REV-2026-1057) of the
        // application table" — `rev_name`, the reference trustees also see in the <h1> and list.
        { id: "S1", label: "Application ID", cell: (d) => value(d.reference) },
        {
          id: "S2",
          label: "Are you?",
          cell: (d) => value(optionLabel(APPLICANT_TYPE_LABELS, d.applicantType)),
        },
        {
          id: "S3",
          label: "Overall Current Circumstance Score (Out of 60, 60 as worst)",
          cell: (d) => value(formatScore(d.circumstanceScore)),
        },
        // S4/S5 and D3/D4: intake stopped writing these two columns when the form lost its
        // date pickers; WI-0010 (deferred) restores them. Until then the grant admin fills them
        // by hand on the application form (reviewer, 2026-09-30), and they read "Not recorded"
        // where nobody has. The applicant's typed provisional date is not shown ("Don't show the
        // dates"), and no longer read.
        { id: "S4", label: "Start Date", cell: (d) => value(formatDate(d.preferredStart)) },
        { id: "S5", label: "End Date", cell: (d) => value(formatDate(d.preferredEnd)) },
        {
          id: "S6",
          label: "Individual Total Amount Requesting Revitalise inc. Exceptional Funding",
          cell: (d) =>
            value(formatAmount(totalFundingRequested(d.amountRequested, d.additionalAmountRequested))),
        },
        {
          id: "S7",
          label: "Exceptional Funding Amount",
          cell: (d) => value(formatAmount(d.additionalAmountRequested)),
        },
      ],
    },
  ],
};

/** Pack p.1, "Application Details". */
const APPLICATION_DETAILS: DetailSection = {
  id: "application-details",
  heading: "Application Details",
  origin: "pack",
  groups: [
    {
      heading: null,
      rows: [
        {
          id: "D1",
          label: "Type of Break",
          cell: (d) => value(optionLabel(BREAK_TYPE_LABELS, d.breakType)),
        },
        { id: "D2", label: "Location of Activity", cell: (d) => value(formatText(d.breakLocation)) },
        { id: "D3", label: "Start Date", cell: (d) => value(formatDate(d.preferredStart)) },
        { id: "D4", label: "End Date", cell: (d) => value(formatDate(d.preferredEnd)) },
        {
          id: "D5",
          label: "Accommodation or Activity Cost",
          cell: (d) => value(formatAmount(d.accommodationCost)),
        },
        { id: "D6", label: "Travel Costs", cell: (d) => value(formatAmount(d.travelCost)) },
        { id: "D7", label: "Other Costs", cell: (d) => value(formatAmount(d.otherCost)) },
        { id: "D8", label: "Total Estimated Cost", cell: (d) => value(formatAmount(d.costs)) },
        {
          id: "D9",
          label: "Amount Requesting Revitalise Individual",
          cell: (d) => value(formatAmount(d.amountRequested)),
        },
        {
          id: "D10",
          label: "Exceptional Amount Requested",
          cell: (d) => value(formatAmount(d.additionalAmountRequested)),
        },
        {
          id: "D11",
          label: "Exceptional Circumstance",
          // An absent category is normal (no exceptional funding asked for), so it reads as
          // "Not recorded", never as the option map's "Not set".
          cell: (d) =>
            value(
              d.exceptionalCircumstance === null
                ? NOT_RECORDED
                : optionLabel(EXCEPTIONAL_CIRCUMSTANCE_LABELS, d.exceptionalCircumstance),
            ),
        },
        {
          id: "D11a",
          label: "Other exceptional circumstance",
          cell: (d) => redacted(d, d.redactedOtherExceptionalCircumstance),
          visible: (d) => d.exceptionalCircumstance === EXCEPTIONAL_CIRCUMSTANCE_OTHER,
          approvedDeviation: DECISION_OTHER_EXCEPTIONAL,
        },
        {
          id: "D12",
          label: "Please briefly explain how this break would benefit you",
          // The narrative. Intake writes this question's answer to the secured narrative
          // column; the trustee reads only its redacted counterpart.
          cell: (d) => redacted(d, d.redactedNarrative),
        },
        {
          id: "D13",
          label: "Please briefly explain why you’re unable to fund this break yourself?",
          cell: (d) => redacted(d, d.redactedUnableToFundExplanation),
        },
      ],
    },
  ],
};

/** Pack pp.1-2, "About Applicant". */
const ABOUT_APPLICANT: DetailSection = {
  id: "about-applicant",
  heading: "About Applicant",
  origin: "pack",
  groups: [
    {
      heading: null,
      rows: [
        {
          id: "A1",
          label: "Are you?",
          cell: (d) => value(optionLabel(APPLICANT_TYPE_LABELS, d.applicantType)),
        },
        {
          id: "A2",
          label:
            "Do you or the person you support have a disability as defined by the Equality Act 2010?",
          cell: (d) =>
            value(
              eitherPerson(
                yesNoOrNull(d.hasEqualityActDisability),
                yesNoOrNull(d.supportRecipientHasEqualityActDisability),
              ) ?? NOT_RECORDED,
            ),
        },
        {
          id: "A3",
          label: "Please select all conditions or illnesses that apply?",
          cell: (d) =>
            value(
              eitherPerson(
                optionLabels(CONDITION_PROFILE_LABELS, d.conditionProfile),
                optionLabels(CONDITION_PROFILE_LABELS, d.supportRecipientConditionProfile),
              ) ?? NOT_RECORDED,
            ),
        },
        {
          id: "A3a",
          label: "Other condition notes",
          cell: (d) => redacted(d, d.redactedOtherCondition),
          visible: (d) => (d.conditionProfile ?? []).includes(CONDITION_PROFILE_OTHER),
          approvedDeviation: DECISION_OTHER_CONDITION,
        },
        {
          id: "A3b",
          label: "Other condition notes (the person you support)",
          cell: (d) => redacted(d, d.redactedSupportRecipientOtherCondition),
          visible: (d) => (d.supportRecipientConditionProfile ?? []).includes(CONDITION_PROFILE_OTHER),
          approvedDeviation: DECISION_OTHER_CONDITION,
        },
        {
          id: "A4",
          label: "Brief Confirmation",
          cell: (d) =>
            redacted(
              d,
              eitherPerson(
                blankToNull(d.redactedDisabilityImpactDescription),
                blankToNull(d.redactedSupportRecipientDisabilityImpactDescription),
                "\n\n",
              ),
            ),
        },
        {
          id: "A5",
          label: "As a carer, what type of care and support do you personally provide?",
          cell: (d) => value(formatText(optionLabels(CARE_PROVIDED_TYPE_LABELS, d.careProvidedType))),
        },
        {
          id: "A6",
          label: "Brief Description of Care Support Received or Provided",
          cell: (d) => redacted(d, d.redactedCareSupportDescription),
        },
        {
          id: "A7",
          label: "As a carer, on average how many hours of support do you provide a week?",
          cell: (d) =>
            value(
              d.careHoursPerWeek === null
                ? NOT_RECORDED
                : optionLabel(CARE_HOURS_BAND_LABELS, d.careHoursPerWeek),
            ),
        },
      ],
    },
  ],
};

/** Pack p.2, "Current Circumstances" — the score, then the answers it is computed from. */
const CURRENT_CIRCUMSTANCES: DetailSection = {
  id: "current-circumstances",
  heading: "Current Circumstances",
  origin: "pack",
  groups: [
    {
      heading: null,
      rows: [
        {
          id: "C1",
          label: "Overall Current Circumstances Score (Out of 60)",
          cell: (d) => value(formatScore(d.circumstanceScore)),
        },
      ],
    },
    {
      // WI-0008 review (2026-09-30): the life-satisfaction answer is the first of the three
      // wellbeing sub-sections, so it gets a heading of its own. The Pack prints C2 in the same
      // table as C1 with no heading; the rows and their order are unchanged.
      heading: "Life satisfaction",
      headingDeviation: DECISION_WELLBEING_SECTIONS,
      rows: [
        {
          id: "C2",
          label: "Overall, how satisfied are you with your life nowadays? (0 being not at all)",
          cell: (d) =>
            value(
              d.lifeSatisfaction === null
                ? NOT_RECORDED
                : optionLabel(LIFE_SATISFACTION_LABELS, d.lifeSatisfaction),
            ),
        },
      ],
    },
    {
      heading: "In the last 2 weeks…",
      rows: [
        {
          id: "C3",
          label: "I’ve been feeling optimistic about the future",
          cell: (d) => wellbeing(d, 1, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C4",
          label: "I’ve been feeling useful",
          cell: (d) => wellbeing(d, 2, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C5",
          label: "I’ve been feeling relaxed",
          cell: (d) => wellbeing(d, 3, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C6",
          label: "I’ve been dealing with problems well",
          cell: (d) => wellbeing(d, 4, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C7",
          label: "I’ve been thinking clearly",
          cell: (d) => wellbeing(d, 5, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C8",
          label: "I’ve been feeling close to other people",
          cell: (d) => wellbeing(d, 6, LIKERT_RESPONSE_LABELS),
        },
        {
          id: "C9",
          label: "I’ve been able to make up my own mind about things",
          cell: (d) => wellbeing(d, 7, LIKERT_RESPONSE_LABELS),
        },
      ],
    },
    {
      heading: "In the last year…",
      rows: [
        {
          id: "C10",
          label: WELLBEING_QUESTION_HEADINGS.rev_wellbeinganswer8 ?? "",
          cell: (d) => wellbeing(d, 8, AGREEMENT_RESPONSE_LABELS),
        },
        {
          id: "C11",
          label: WELLBEING_QUESTION_HEADINGS.rev_wellbeinganswer9 ?? "",
          cell: (d) => wellbeing(d, 9, AGREEMENT_RESPONSE_LABELS),
        },
        {
          id: "C12",
          label: WELLBEING_QUESTION_HEADINGS.rev_wellbeinganswer10 ?? "",
          cell: (d) => wellbeing(d, 10, AGREEMENT_RESPONSE_LABELS),
        },
      ],
    },
  ],
};

/** Pack p.2, "Financial Eligibility". */
const FINANCIAL_ELIGIBILITY: DetailSection = {
  id: "financial-eligibility",
  heading: "Financial Eligibility",
  origin: "pack",
  groups: [
    {
      heading: null,
      rows: [
        {
          id: "F1",
          label: "Do you currently receive means tested benefits?",
          cell: () => ({ kind: "restricted", catalogueKey: "benefit-status" }),
        },
        {
          id: "F2",
          label: "Benefit Provider",
          cell: () => ({ kind: "restricted", catalogueKey: "benefit-provider" }),
        },
        {
          id: "F3",
          label: "Are you currently working?",
          cell: () => ({ kind: "restricted", catalogueKey: "employment-status" }),
        },
        {
          id: "F4",
          label: "Approximate Household Income",
          cell: (d) =>
            value(d.incomeBand === null ? NOT_RECORDED : optionLabel(INCOME_BAND_LABELS, d.incomeBand)),
        },
        {
          id: "F5",
          label: "If you have significant care costs, please briefly explain",
          // The redacted twin, added to the data model by reviewer decision 2026-09-30 ("Show
          // [the secured care-costs column; its name is never written in this app] as a narrativescrubbed version, like other columns"). The
          // secured source is never requested.
          cell: (d) => redacted(d, d.redactedCareCostsExplanation),
        },
        {
          id: "F6",
          label: "Do you savings over £6,000?",
          cell: (d) => value(formatYesNo(d.savingsOver6000)),
        },
      ],
    },
  ],
};

/** The Pack's five sections, in the Pack's order. */
export const TRUSTEE_PACK_SECTIONS: readonly DetailSection[] = [
  SUMMARY,
  APPLICATION_DETAILS,
  ABOUT_APPLICANT,
  CURRENT_CIRCUMSTANCES,
  FINANCIAL_ELIGIBILITY,
];

/**
 * The whole screen, in render order: the Pack's five sections. The portal-only section this
 * screen had between WI-0005's first pass and its code review is gone — the reviewer placed the
 * rows worth keeping (status, review round, the "other" notes) inside the Pack sections above,
 * and ruled the rest out.
 */
export const APPLICATION_DETAIL_LAYOUT: readonly DetailSection[] = TRUSTEE_PACK_SECTIONS;
