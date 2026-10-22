/**
 * The signed-in trustee's OWN verdict on one application — portal TAD trustee-portal-design-2
 * ADR-086 point 3 (SDD A-14, FR-116, FR-117; US-012 AC-11; wbs:6.3).
 *
 * Built on `resolveSlot` (`domain/slots.ts`), the one place that decides which of
 * `rev_verdict1`/`rev_verdict2` is the signed-in trustee's, so the list's button and the verdict
 * dialog cannot disagree about whose slot is whose. The OTHER trustee's slot is never read here:
 * a row where only the other trustee has decided is still awaiting this trustee.
 *
 *   decided  — this trustee's own slot holds a verdict (`finalised` says whether the round is
 *              locked, which only changes the button's accessible wording)
 *   awaiting — the row is writable to this trustee and their own slot is empty (counted by the
 *              list's "awaiting your verdict" line, and kept by its filter)
 *   none     — no review row, not one of the two trustees, user unknown, or finalised with the
 *              own slot empty: nothing this trustee can or did record
 */
import { VERDICT_STATE_LABELS, optionLabel } from "../dataverse/schema";
import type { CurrentUser, ReviewRow } from "../dataverse/types";
import { resolveSlot } from "./slots";

export type OwnVerdictState =
  | { kind: "decided"; verdict: number; finalised: boolean }
  | { kind: "awaiting" }
  | { kind: "none" };

export function ownVerdictState(review: ReviewRow | null, user: CurrentUser): OwnVerdictState {
  const resolution = resolveSlot(review, user);
  if (resolution.kind === "writable") {
    return resolution.verdict === null
      ? { kind: "awaiting" }
      : { kind: "decided", verdict: resolution.verdict, finalised: false };
  }
  if (resolution.kind === "finalised" && resolution.verdict !== null) {
    return { kind: "decided", verdict: resolution.verdict, finalised: true };
  }
  return { kind: "none" };
}

/** The verdict's tone, for the button. A value outside 1 to 3 is neutral (ADR-086 point 4). */
export type VerdictTone = "approved" | "deferred" | "rejected" | "neutral";

export function verdictTone(verdict: number): VerdictTone {
  switch (verdict) {
    case 1:
      return "approved";
    case 2:
      return "deferred";
    case 3:
      return "rejected";
    default:
      return "neutral";
  }
}

/**
 * The button's visible word for a decided verdict: "Approved", "Deferred", "Rejected", or — for
 * an option value this app does not know — the option label, which is "Unknown (n)", never blank.
 */
export function verdictStateWord(verdict: number): string {
  return optionLabel(VERDICT_STATE_LABELS, verdict);
}

/**
 * The button's accessible name for a decided verdict. It CONTAINS the visible word (WCAG 2.5.3)
 * and says whether the verdict can still be changed.
 */
export function decidedVerdictAriaLabel(verdict: number, finalised: boolean, reference: string): string {
  return finalised
    ? `${verdictStateWord(verdict)} — your verdict on ${reference}. Open to view it`
    : `${verdictStateWord(verdict)} — your verdict on ${reference}. Open to view or change it`;
}

/** How many of `states` await this trustee's verdict (FR-117). */
export function countAwaiting(states: readonly OwnVerdictState[]): number {
  return states.filter((state) => state.kind === "awaiting").length;
}
