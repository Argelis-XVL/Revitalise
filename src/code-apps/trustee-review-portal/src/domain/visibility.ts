/**
 * The fail-closed conjunction (TAD §5.5), as pure functions.
 *
 * Trustee visibility is a conjunction of two conditions:
 *   `rev_eligibleforround = true`  AND  `rev_redactionreleased = true`
 *
 * The default state of a new narrative is WITHHELD, and a flow failure therefore fails
 * closed (NFR-018). Automation #5 (narrative scrubbing) is deferred by reviewer
 * decision, so nothing is released today and the narrative panel always renders its
 * withheld state. That is correct behaviour, not a defect — it is the safety basis
 * `contract/known-exceptions.json` → `EX-003` rests on.
 *
 * Both functions require an affirmative `true`. Absent, null, false, and a column
 * hidden by column security are all "no".
 */
import type { ApplicationSummary } from "../dataverse/types";

/**
 * Whether a case may appear to a trustee at all (FR-038).
 *
 * Applied client-side even though the same condition is in the server-side `$filter`.
 * Not redundancy for its own sake: the server filter is one string in one function, and
 * a case leaking into a trustee's list is the failure this whole feature exists to
 * prevent. Two independent checks, one of them unit-tested without a network.
 */
export function isVisibleForReview(row: Pick<ApplicationSummary, "eligibleForRound">): boolean {
  return row.eligibleForRound === true;
}

/** Narrows a list of rows to those a trustee may see. */
export function visibleForReview<T extends Pick<ApplicationSummary, "eligibleForRound">>(
  rows: readonly T[],
): T[] {
  return rows.filter((row) => isVisibleForReview(row));
}

/**
 * What one redacted free-text answer shows — WI-0005 (2026-09-30).
 *
 * ## Why this is one function per ANSWER, where there used to be four per PANEL
 *
 * Before WI-0005 the detail screen grouped its redacted free text by panel, so the gate was
 * written four times (`narrativeState`, `careSupportState`, `financialFreeTextState`,
 * `conditionFreeTextState`), each deciding for a whole panel at once. The Trustee Pack puts
 * each of those answers on its OWN row, in a different section from its old panel-mates (the
 * "why unable to fund" answer is in Application Details, not Financial Eligibility), so the
 * decision now has to be made per row. The rule itself is unchanged, and so are the three
 * states: `redactionReleased` must be an affirmative `true` (absent, null, false and a
 * column hidden by column security are all "no"), and released-but-blank is its own state,
 * never rendered as withheld and never as an empty box (`TAD §8.5 point 1`).
 *
 * Automation #5 (scrubbing) is deferred, so `withheld` is the only state reachable today —
 * the safety basis `EX-003` rests on. It is built and tested as a first-class state.
 */
export type RedactedTextState =
  | { kind: "released"; text: string }
  | { kind: "released-empty"; heading: string; explanation: string }
  | { kind: "withheld"; heading: string; explanation: string };

/** The withheld wording, shared by every redacted row so the rows read as one rule. */
export const WITHHELD_HEADING = "Withheld until released";
export const WITHHELD_EXPLANATION =
  "This answer has not been released for trustee review yet. Every free-text answer is " +
  "withheld until the process owner has checked its anonymisation and released it, so this " +
  "is the expected state rather than a fault.";

/** The released-but-blank wording. */
export const RELEASED_EMPTY_HEADING = "Nothing recorded";
export const RELEASED_EMPTY_EXPLANATION =
  "This answer has been released for trustee review, but no anonymised text was recorded " +
  "for it.";

export function redactedTextState(
  redactionReleased: boolean,
  text: string | null,
): RedactedTextState {
  if (redactionReleased !== true) {
    return { kind: "withheld", heading: WITHHELD_HEADING, explanation: WITHHELD_EXPLANATION };
  }
  if (text === null || text.trim().length === 0) {
    return {
      kind: "released-empty",
      heading: RELEASED_EMPTY_HEADING,
      explanation: RELEASED_EMPTY_EXPLANATION,
    };
  }
  return { kind: "released", text };
}
