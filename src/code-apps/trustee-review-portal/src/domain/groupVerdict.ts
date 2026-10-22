/**
 * A group verdict — portal TAD trustee-portal-design-2 ADR-087 (SDD A-14, FR-118, FR-119;
 * US-012 AC-12; wbs:6.3; WI-0148).
 *
 * A group is the set of loaded applications sharing a `rev_grouplinkage` value
 * (`domain/groups.ts`, EF-43). One verdict is recorded in the signed-in trustee's OWN slot on every
 * member they can record on, and nowhere else. Each member's slot is resolved separately with the
 * dialog's own rule (`resolveSlot`), because a trustee can be trustee 1 on one member's review and
 * trustee 2 on another's. The review for each member is chosen by `currentReviewFor`, the same
 * function the dialog and the list use.
 *
 * Three phases, all pure except the executor's injected `save`:
 *
 *   1. `planGroupVerdict` — the PREVIEW: members to write (review id + own slot) and members
 *      skipped, each with a reason in plain words. Nothing is written.
 *   2. `replanForConfirm` — at confirm, the member reviews are read again, FRESH, and planned
 *      again. The write set is the preview's targets that are STILL writable; one that dropped out
 *      is skipped with its new reason; one that became writable after the preview is NOT written,
 *      because the trustee did not confirm it.
 *   3. `executeGroupVerdict` — one ordinary `saveVerdict` per target, ONE AT A TIME. A failure is
 *      recorded and the run continues. Each member's outcome comes ONLY from its own write result
 *      (R-D2-18): recorded, skipped (with reason) or failed (with the error message).
 *
 * Notes follow the single dialog's EF-05 rule — required for Defer and Reject, optional for
 * Approve, capped at `VERDICT_NOTES_MAX_LENGTH` — decided by the reviewer 2026-10-22 ("Yes, group
 * defer or reject require notes as well. Saved to all individual applications."). The same text
 * is written to every member's own notes column. An Approve with no note sends NO notes column, so
 * a member's existing note is kept (ADR-087 point 6; A-TR-20).
 */
import { VERDICT_LABELS, VERDICT_NOTES_MAX_LENGTH, VERDICT_VALUES, optionLabel } from "../dataverse/schema";
import { currentReviewFor } from "../dataverse/currentReview";
import type { ApplicationSummary, CurrentUser, ReviewRow, SaveVerdictInput, VerdictSlot } from "../dataverse/types";
import { resolveSlot } from "./slots";

export interface GroupVerdictTarget {
  readonly application: ApplicationSummary;
  readonly reviewId: string;
  readonly slot: VerdictSlot;
}

export interface GroupVerdictSkip {
  readonly application: ApplicationSummary;
  /** Plain words, completing "skipped: …". */
  readonly reason: string;
}

export interface GroupVerdictPlan {
  readonly targets: readonly GroupVerdictTarget[];
  readonly skipped: readonly GroupVerdictSkip[];
}

/** The member's target when it can be written, else why not, in the words ADR-087 point 3 gives. */
function skipReason(
  application: ApplicationSummary,
  review: ReviewRow | null,
  user: CurrentUser,
): { target: GroupVerdictTarget } | { reason: string } {
  const resolution = resolveSlot(review, user);
  switch (resolution.kind) {
    case "writable":
      // `review` is non-null whenever the resolution is writable.
      return { target: { application, reviewId: (review as ReviewRow).id, slot: resolution.slot } };
    case "no-review-row":
      return { reason: `there is no review record for ${application.reference} yet` };
    case "not-assigned":
      return { reason: `you are not one of the two trustees on ${application.reference}` };
    case "finalised":
      return { reason: `the round for ${application.reference} has been finalised` };
    case "unknown-user":
      return { reason: `the portal could not confirm who you are, so ${application.reference} is read-only` };
  }
}

/** The preview (ADR-087 point 3). Members keep their given order. */
export function planGroupVerdict(
  members: readonly ApplicationSummary[],
  reviewRows: readonly ReviewRow[],
  user: CurrentUser,
): GroupVerdictPlan {
  const targets: GroupVerdictTarget[] = [];
  const skipped: GroupVerdictSkip[] = [];
  for (const application of members) {
    const result = skipReason(application, currentReviewFor(application.id, reviewRows), user);
    if ("target" in result) targets.push(result.target);
    else skipped.push({ application, reason: result.reason });
  }
  return { targets, skipped };
}

/** The wording for a member that became writable after the preview (ADR-087 point 4). */
export const NOT_CONFIRMED_REASON =
  "not included when you confirmed — run the group verdict again to include it";

/**
 * The write set at confirm (ADR-087 point 4): the preview's targets that are STILL writable on a
 * fresh read, each with its fresh review id and slot. Everything else in the group is skipped:
 * with its new reason when it dropped out, with `NOT_CONFIRMED_REASON` when it was not a preview
 * target but is writable now, and with its reason otherwise.
 */
export function replanForConfirm(
  preview: GroupVerdictPlan,
  members: readonly ApplicationSummary[],
  freshRows: readonly ReviewRow[],
  user: CurrentUser,
): GroupVerdictPlan {
  const previewed = new Set(preview.targets.map((target) => target.application.id));
  const fresh = planGroupVerdict(members, freshRows, user);
  const freshTargets = new Map(fresh.targets.map((target) => [target.application.id, target]));
  const targets: GroupVerdictTarget[] = [];
  const skipped: GroupVerdictSkip[] = [];
  for (const application of members) {
    const target = freshTargets.get(application.id);
    if (previewed.has(application.id) && target !== undefined) {
      targets.push(target);
      continue;
    }
    if (target !== undefined) {
      skipped.push({ application, reason: NOT_CONFIRMED_REASON });
      continue;
    }
    const reason = fresh.skipped.find((skip) => skip.application.id === application.id)?.reason;
    skipped.push({ application, reason: reason ?? "it could not be planned" });
  }
  return { targets, skipped };
}

export type NotesProblem = "required" | "too-long" | null;

/** EF-05, applied before anything is written (ADR-087 point 2). */
export function groupNotesProblem(verdict: number, notes: string): NotesProblem {
  if (notes.length > VERDICT_NOTES_MAX_LENGTH) return "too-long";
  const required = verdict === VERDICT_VALUES.defer || verdict === VERDICT_VALUES.reject;
  if (required && notes.trim() === "") return "required";
  return null;
}

/**
 * The notes to send: the trimmed text when there is any; ABSENT for an Approve with no note, so
 * the member's stored note is kept (ADR-087 point 6). Defer and Reject always carry their note.
 */
export function notesToSend(notes: string): string | undefined {
  const trimmed = notes.trim();
  return trimmed === "" ? undefined : trimmed;
}

export type GroupVerdictOutcome =
  | { readonly kind: "recorded"; readonly application: ApplicationSummary }
  | { readonly kind: "skipped"; readonly application: ApplicationSummary; readonly reason: string }
  | { readonly kind: "failed"; readonly application: ApplicationSummary; readonly message: string };

/**
 * Write the plan (ADR-087 point 5): one `save` per target, one after another. A failure is
 * recorded and the run continues; a member is "recorded" only when ITS OWN write resolved.
 * Skipped members are reported in group order with the targets.
 */
export async function executeGroupVerdict(
  members: readonly ApplicationSummary[],
  plan: GroupVerdictPlan,
  verdict: number,
  notes: string | undefined,
  save: (input: SaveVerdictInput) => Promise<void>,
  onProgress?: (done: number, total: number) => void,
): Promise<GroupVerdictOutcome[]> {
  const results = new Map<string, GroupVerdictOutcome>();
  for (const skip of plan.skipped) {
    results.set(skip.application.id, { kind: "skipped", application: skip.application, reason: skip.reason });
  }
  let done = 0;
  for (const target of plan.targets) {
    onProgress?.(done + 1, plan.targets.length);
    const input: SaveVerdictInput = { reviewId: target.reviewId, slot: target.slot, verdict };
    if (notes !== undefined) input.notes = notes;
    try {
      await save(input);
      results.set(target.application.id, { kind: "recorded", application: target.application });
    } catch (error) {
      results.set(target.application.id, {
        kind: "failed",
        application: target.application,
        message: error instanceof Error ? error.message : String(error),
      });
    }
    done += 1;
  }
  return members
    .map((member) => results.get(member.id))
    .filter((outcome): outcome is GroupVerdictOutcome => outcome !== undefined);
}

function plural(count: number, noun: string): string {
  return `${String(count)} ${noun}${count === 1 ? "" : "s"}`;
}

/** "1 skipped: you are not one of the two trustees on REV-A-00123" — reasons joined by "; ". */
function skippedClause(skipped: readonly { reason: string }[]): string {
  return `${String(skipped.length)} skipped: ${skipped.map((skip) => skip.reason).join("; ")}`;
}

/** The preview sentence (ADR-087 point 3). */
export function previewSentence(plan: GroupVerdictPlan, verdict: number): string {
  const total = plan.targets.length + plan.skipped.length;
  const label = optionLabel(VERDICT_LABELS, verdict);
  const head = `${label} will be recorded on ${String(plan.targets.length)} of ${plural(total, "application")}.`;
  return plan.skipped.length === 0 ? head : `${head} ${skippedClause(plan.skipped)}.`;
}

/** The confirm button's label: "Record Approve on 3 applications". */
export function confirmLabel(plan: GroupVerdictPlan, verdict: number): string {
  return `Record ${optionLabel(VERDICT_LABELS, verdict)} on ${plural(plan.targets.length, "application")}`;
}

/** The result sentence in FR-119's form: "3 recorded, 1 skipped: …, 1 failed: REV-…". */
export function resultSentence(outcomes: readonly GroupVerdictOutcome[]): string {
  const recorded = outcomes.filter((o) => o.kind === "recorded").length;
  const skipped = outcomes.filter((o): o is Extract<GroupVerdictOutcome, { kind: "skipped" }> => o.kind === "skipped");
  const failed = outcomes.filter((o): o is Extract<GroupVerdictOutcome, { kind: "failed" }> => o.kind === "failed");
  const parts = [`${String(recorded)} recorded`];
  if (skipped.length > 0) parts.push(skippedClause(skipped));
  if (failed.length > 0) {
    parts.push(`${String(failed.length)} failed: ${failed.map((o) => o.application.reference).join(", ")}`);
  }
  return parts.join(", ");
}

/** One line per member for the result list. */
export function outcomeLine(outcome: GroupVerdictOutcome): string {
  switch (outcome.kind) {
    case "recorded":
      return `${outcome.application.reference}: recorded`;
    case "skipped":
      return `${outcome.application.reference}: skipped — ${outcome.reason}`;
    case "failed":
      return `${outcome.application.reference}: failed — ${outcome.message}`;
  }
}
