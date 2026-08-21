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
import type { ApplicationDetail, ApplicationSummary } from "../dataverse/types";

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

export type NarrativeState =
  | { kind: "released"; text: string }
  | { kind: "released-empty"; heading: string; explanation: string }
  | { kind: "withheld"; heading: string; explanation: string };

/**
 * What the narrative panel shows.
 *
 * Three states, all first-class. `withheld` is not an error and not an empty box: it is
 * the designed state of the control, and it says so in words.
 */
export function narrativeState(
  detail: Pick<ApplicationDetail, "redactionReleased" | "redactedNarrative">,
): NarrativeState {
  if (detail.redactionReleased !== true) {
    return {
      kind: "withheld",
      heading: "Anonymised narrative withheld",
      explanation:
        "This narrative has not been released for trustee review yet. Every narrative is " +
        "withheld until the process owner has checked the anonymisation and released it, so " +
        "this is the expected state rather than a fault. The rest of the case — the " +
        "circumstance score, the score breakdown and the holiday details — is complete and " +
        "can be decided from.",
    };
  }
  const text = detail.redactedNarrative;
  if (text === null || text.trim().length === 0) {
    return {
      kind: "released-empty",
      heading: "No narrative recorded",
      explanation:
        "This narrative has been released for trustee review, but no anonymised text was " +
        "recorded against the application.",
    };
  }
  return { kind: "released", text };
}
