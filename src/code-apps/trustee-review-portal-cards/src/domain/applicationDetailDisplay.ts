/**
 * How each Trustee Pack row is PRESENTED in the card-layout app — ADR-058 of
 * `docs/architecture/trustee-portal-design-2-architecture.md` (wbs:6.3, unbilled).
 *
 * ## Why this is a separate file and not a field on `DetailRow`
 *
 * The design handoff (`Designsystem/Design-2.0/design_handoff_application_detail/README.md`,
 * "Implementation approach") proposes an optional `display` field on `DetailRow`. ADR-058 moves it
 * here instead: `applicationDetailLayout.ts` is the file that holds the Pack contract (45 rows,
 * their labels, their sections, their Pack order), and it must stay byte-identical in both apps so
 * the parity gate (`scripts/verify-code-app-variant-parity.py`) can hold that contract in ONE
 * place. This file exists only in `trustee-review-portal-cards`, and it is on the gate's
 * allow-list. So the work item's clause "extend `DetailRow` with a `display` hint" is met by the
 * TAD's chosen mechanism, not by the literal edit (recorded in the Dev Summary).
 *
 * ## What a display hint can and cannot do
 *
 *   - It picks a LOOK for a row. It never moves a row out of its Pack section, never drops one and
 *     never relabels one: the renderer iterates `APPLICATION_DETAIL_LAYOUT` and only groups each
 *     layout group's visible rows by display (ADR-057).
 *   - It can never turn a protected row into a plain value. `displayOf()` decides from the CELL
 *     first: a `redacted` cell is always an answer card and a `restricted` cell is always a
 *     restricted row, whatever this map says (TAD risk R-D2-5). The map's own test also asserts it.
 *
 * ## The raw values a few displays need
 *
 * Four displays show something a formatted string cannot carry: the score badge and the score bar
 * need the NUMBER (a bar width is score/60), the 0–10 scale needs the answer as an integer, the
 * status pill needs the option value to choose its tone, and the condition chips need the labels
 * as a list. Those accessors live here, keyed by row id, so no JSX names a row. Each reads exactly
 * the column that row's own `cell()` already reads in the layout file, and nothing else: no new
 * column is requested, logged or exported (WI-0061 clause 2 for A3, the Art. 9 row).
 */
import { CONDITION_PROFILE_LABELS, optionLabel } from "../dataverse/schema";
import type { ApplicationDetail } from "../dataverse/types";
import type { DetailCell, DetailRow } from "./applicationDetailLayout";
import { isRowVisible } from "./applicationDetailLayout";
import { NOT_AVAILABLE, NOT_RECORDED } from "./format";

/** ADR-058's display vocabulary. A row with no entry in `ROW_DISPLAY` renders as `"fact"`. */
export type Display =
  | "fact"
  | "cost"
  | "costTotal"
  | "answer"
  | "scale"
  | "likert"
  | "restricted"
  | "score"
  | "status"
  | "chips";

/**
 * Row id → display, from the README's mapping table (lines 35-41). Rows absent from this map are
 * facts: S0b, S1, S2, S4-S7 (hero chips), D1-D4, D11, A1, A2, A5, A7, F4, F6 (fact tiles).
 */
export const ROW_DISPLAY: Readonly<Record<string, Display>> = {
  // Summary — the hero.
  S0a: "status",
  S3: "score",
  // Application Details.
  D5: "cost",
  D6: "cost",
  D7: "cost",
  D8: "costTotal",
  D9: "cost",
  D10: "cost",
  D11a: "answer",
  D12: "answer",
  D13: "answer",
  // About Applicant. A3 is a fact tile whose value renders as chips (WI-0061).
  A3: "chips",
  A3a: "answer",
  A3b: "answer",
  A4: "answer",
  A6: "answer",
  // Current Circumstances.
  C1: "score",
  C2: "scale",
  C3: "likert",
  C4: "likert",
  C5: "likert",
  C6: "likert",
  C7: "likert",
  C8: "likert",
  C9: "likert",
  C10: "likert",
  C11: "likert",
  C12: "likert",
  // Financial Eligibility.
  F1: "restricted",
  F2: "restricted",
  F3: "restricted",
  F5: "answer",
};

/**
 * The display a row actually renders with. The CELL decides first, so no map entry — present,
 * missing or wrong — can render a redacted or restricted row as a value (ADR-058, R-D2-5). The
 * converse also holds: a value cell mapped to `answer` or `restricted` renders as a plain fact
 * rather than borrowing a protected look it has no state for.
 */
export function displayOf(row: DetailRow, cell: DetailCell): Display {
  if (cell.kind === "redacted") return "answer";
  if (cell.kind === "restricted") return "restricted";
  const mapped = ROW_DISPLAY[row.id] ?? "fact";
  return mapped === "answer" || mapped === "restricted" ? "fact" : mapped;
}

/**
 * A DISPLAY GROUP — the unit ADR-057's order contract is stated over. Rows in one display group
 * render together as one block (one tile grid, one receipt, one answer grid, …); inside a display
 * group they stay in Pack order.
 *
 * `fact` and `chips` share the `tiles` group: A3's chips are a tile in the same grid as A1, A2,
 * A5 and A7 (README line 39). `cost` and `costTotal` share `costs`: D8 stays between D7 and D9
 * (ADR-057 decision 3).
 */
export type DisplayGroupKind =
  | "score"
  | "status"
  | "tiles"
  | "costs"
  | "answers"
  | "scale"
  | "likert"
  | "restricted";

export function groupKindOf(display: Display): DisplayGroupKind {
  switch (display) {
    case "fact":
    case "chips":
      return "tiles";
    case "cost":
    case "costTotal":
      return "costs";
    case "answer":
      return "answers";
    case "scale":
      return "scale";
    case "likert":
      return "likert";
    case "restricted":
      return "restricted";
    case "score":
      return "score";
    case "status":
      return "status";
  }
}

/**
 * The fixed order of display groups in each Pack section (ADR-057 decision 2(c)), taken from the
 * design reference (`reference/ApplicationDetail.jsx.txt`): facts, then costs, then the free-text
 * answers; in Financial Eligibility the restricted rows come before the one free-text answer.
 */
export const SECTION_GROUP_ORDER: Readonly<Record<string, readonly DisplayGroupKind[]>> = {
  summary: ["score", "status", "tiles"],
  "application-details": ["tiles", "costs", "answers"],
  "about-applicant": ["tiles", "answers"],
  "current-circumstances": ["score", "scale", "likert"],
  "financial-eligibility": ["tiles", "restricted", "answers"],
};

/** For a section this map does not name (only tests build one): every kind, in a stable order. */
const DEFAULT_GROUP_ORDER: readonly DisplayGroupKind[] = [
  "score",
  "status",
  "tiles",
  "costs",
  "scale",
  "likert",
  "restricted",
  "answers",
];

export function groupOrderFor(sectionId: string): readonly DisplayGroupKind[] {
  const declared = SECTION_GROUP_ORDER[sectionId] ?? [];
  // Any kind a section does not declare still renders, after the declared ones, so a future row
  // mapped to an unexpected display is shown rather than silently dropped.
  return [...declared, ...DEFAULT_GROUP_ORDER.filter((kind) => !declared.includes(kind))];
}

/** Sub-headings the display groups carry (reviewer R2, "Approve all"). Real `<h3>`s, not spec rows. */
export const GROUP_HEADING: Readonly<Partial<Record<DisplayGroupKind, string>>> = {
  costs: "Costs",
  answers: "In their words",
  restricted: "Not visible to trustees",
};

/** One visible row, resolved once: its cell and the display it renders with. */
export interface ResolvedRow {
  readonly row: DetailRow;
  readonly cell: DetailCell;
  readonly display: Display;
}

export interface DisplayGroup {
  readonly kind: DisplayGroupKind;
  readonly rows: readonly ResolvedRow[];
}

/**
 * Partition one layout group's VISIBLE rows into display groups, in the section's fixed group
 * order, each group's rows in Pack order. Conditional rows (D11a, A3a, A3b) are filtered by
 * `isRowVisible()` exactly as in the first app; a visible one lands in its own display group in
 * Pack order, which is directly after its trigger row whenever both share a group (ADR-057 (d)).
 */
export function partitionRows(
  sectionId: string,
  rows: readonly DetailRow[],
  detail: ApplicationDetail,
): DisplayGroup[] {
  const buckets = new Map<DisplayGroupKind, ResolvedRow[]>();
  for (const row of rows) {
    if (!isRowVisible(row, detail)) continue;
    const cell = row.cell(detail);
    const display = displayOf(row, cell);
    const kind = groupKindOf(display);
    const bucket = buckets.get(kind) ?? [];
    bucket.push({ row, cell, display });
    buckets.set(kind, bucket);
  }
  return groupOrderFor(sectionId)
    .map((kind) => ({ kind, rows: buckets.get(kind) ?? [] }))
    .filter((group) => group.rows.length > 0);
}

/* ------------------------------------------------------------------------------------- *
 * Panel copy (reviewer R2, "Approve all"). Decorative: rendered `aria-hidden`.
 * ------------------------------------------------------------------------------------- */

export interface Eyebrow {
  readonly text: string;
  /** `brand` is the Verdict panel's pink; every other eyebrow is the purple. */
  readonly tone: "purple" | "brand";
}

export const SECTION_EYEBROW: Readonly<Record<string, Eyebrow>> = {
  summary: { text: "Summary", tone: "purple" },
  "application-details": { text: "The break", tone: "purple" },
  "about-applicant": { text: "Who they are", tone: "purple" },
  "current-circumstances": { text: "How they are doing", tone: "purple" },
  "financial-eligibility": { text: "Money", tone: "purple" },
};

export const STAFF_RECOMMENDATION_EYEBROW: Eyebrow = { text: "From the team", tone: "purple" };
export const VERDICT_EYEBROW: Eyebrow = { text: "Your decision", tone: "brand" };

/**
 * Sections whose blocks sit a whole sub-section step apart (32px) rather than the panel's 20px:
 * Current Circumstances keeps WI-0008's "three distinct sections with more white space".
 */
export const SPACIOUS_SECTIONS: ReadonlySet<string> = new Set(["current-circumstances"]);

/* ------------------------------------------------------------------------------------- *
 * The Summary hero.
 * ------------------------------------------------------------------------------------- */

/** The Pack section rendered as the hero instead of a panel (README line 31). */
export const HERO_SECTION_ID = "summary";

/**
 * The chip label shown on screen where it differs from the Pack label. The Pack label stays in
 * the `<dt>` as visually hidden text, so assistive technology still reads it (reviewer R3,
 * "Shortened label"; ADR-059 decision 3).
 */
export const CHIP_LABEL: Readonly<Record<string, string>> = {
  S6: "Total requested inc. exceptional funding",
};

/** The visible label of the score badge. The Pack's S3 label is kept for assistive technology. */
export const SCORE_BADGE_LABEL = "Score";

/**
 * Which chip row a hero fact sits in: row 1 carries the status pill and S0b, S1, S2 (README line
 * 70); every other hero fact is in row 2.
 */
export const HERO_FIRST_ROW: ReadonlySet<string> = new Set(["S0b", "S1", "S2"]);

/** The hero heading (reviewer R2). Design copy, not a Pack label. */
export function heroHeading(score: number | null): string {
  return score === null ? "Not scored yet" : `${String(score)} out of 60 circumstance points`;
}

/** The badge value: the score, or an em dash when there is none (README line 68). */
export function badgeValue(score: number | null): string {
  return score === null ? "—" : String(score);
}

/** The badge sets a value longer than three characters smaller (README line 68). */
export function badgeValueIsLong(value: string): boolean {
  return value.length > 3;
}

/* ------------------------------------------------------------------------------------- *
 * Raw-value accessors, keyed by row id. Each reads the column its row's `cell()` reads.
 * ------------------------------------------------------------------------------------- */

/** The top of the circumstance score (Pack: "Out of 60"). */
export const SCORE_MAX = 60;

/** S3 and C1 are both `rev_circumstancescore`. */
const NUMBER_OF_ROW: Readonly<Record<string, (detail: ApplicationDetail) => number | null>> = {
  S3: (d) => d.circumstanceScore,
  C1: (d) => d.circumstanceScore,
  C2: (d) => d.lifeSatisfaction,
};

/** The numeric value behind a score or scale row, or `null` when there is none. */
export function numberOf(rowId: string, detail: ApplicationDetail): number | null {
  const read = NUMBER_OF_ROW[rowId];
  return read === undefined ? null : read(detail);
}

/** The score bar's fill, as a fraction 0..1. Clamped, so an out-of-range score cannot overflow. */
export function scoreFraction(score: number | null): number {
  if (score === null) return 0;
  return Math.min(Math.max(score / SCORE_MAX, 0), 1);
}

/** The C2 scale's eleven points (`rev_feelingscaleanswer`, Whole Number 0-10). */
export const SCALE_POINTS: readonly number[] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

/**
 * The scale's text equivalent (WI-0065 clause 2, README line 22). Takes the row cell's own label
 * — `optionLabel(LIFE_SATISFACTION_LABELS, …)` in the layout — so the words come from the label
 * map, never from a second formatting of the number.
 */
export function scaleAnswerText(label: string): string {
  return `Answer: ${label} out of 10`;
}

/**
 * The status tones now live in the shared card-only module `cards/statusTone.ts` (TAD §13.3),
 * used by the detail hero, the applications list and the group members table. Re-exported here
 * so the detail screen's imports and tests read the same map.
 */
export { STATUS_TONE_BY_VALUE, statusToneOf } from "../cards/statusTone";
export type { StatusTone } from "../cards/statusTone";

/** The S0a status, as the option value the tone is chosen from. */
export function statusOf(rowId: string, detail: ApplicationDetail): number | null {
  return rowId === "S0a" ? detail.status : null;
}

/** Re-exported so the tone test can check every key against the enumeration it claims to read. */
export { STATUS_LABELS } from "../cards/statusTone";

/** One labelled row of condition chips. `owner` is null when only one profile is answered. */
export interface ChipRow {
  readonly owner: string | null;
  readonly labels: readonly string[];
}

function conditionLabels(values: readonly number[] | null): string[] {
  return (values ?? []).map((value) => optionLabel(CONDITION_PROFILE_LABELS, value));
}

/**
 * A3's chips. Mirrors the layout's `eitherPerson()` exactly: one profile → one unlabelled row;
 * both → two rows labelled "You" and "The person you support" (WI-0061 clause 1); neither → no
 * rows, and the tile shows its absent state with the cell's own "Not recorded".
 */
const CHIP_ROWS_OF_ROW: Readonly<Record<string, (detail: ApplicationDetail) => ChipRow[]>> = {
  A3: (d) => {
    const own = conditionLabels(d.conditionProfile);
    const supported = conditionLabels(d.supportRecipientConditionProfile);
    if (own.length === 0 && supported.length === 0) return [];
    if (supported.length === 0) return [{ owner: null, labels: own }];
    if (own.length === 0) return [{ owner: null, labels: supported }];
    return [
      { owner: "You", labels: own },
      { owner: "The person you support", labels: supported },
    ];
  },
};

export function chipRowsOf(rowId: string, detail: ApplicationDetail): ChipRow[] {
  const read = CHIP_ROWS_OF_ROW[rowId];
  return read === undefined ? [] : read(detail);
}

/**
 * The words this app puts in a value position to mean "nothing here". `"Not set"` is
 * `optionLabel()`'s own null result (`dataverse/schema.ts`), which exports no constant for it;
 * `"Not scored"` is `formatScore()`'s. A fact whose text is one of these renders in the tile's
 * absent state (WI-0060 clause 2) — the words are unchanged, only their look.
 */
export const ABSENCE_TEXTS: readonly string[] = [NOT_RECORDED, NOT_AVAILABLE, "Not set", "Not scored"];

export function isAbsentText(text: string): boolean {
  return ABSENCE_TEXTS.includes(text);
}
