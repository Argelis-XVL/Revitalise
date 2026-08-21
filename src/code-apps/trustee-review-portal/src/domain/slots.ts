/**
 * Verdict slot mapping (WBS 6.4, FR-037) — the design of decision capture.
 *
 * `rev_review` carries two named trustee slots. The signed-in user is compared against
 * `rev_trustee1` and `rev_trustee2`, and that comparison decides which pair of columns
 * they may write:
 *
 *   trustee 1  ->  rev_verdict1 / rev_notes1
 *   trustee 2  ->  rev_verdict2 / rev_notes2
 *   neither    ->  the row is READ-ONLY to them
 *
 * This is presentation, not authorisation. Dataverse roles and column security are the
 * control (`knowledge/technology/code-apps.md` → Data Access & Auth); a wrong answer
 * here shows the wrong control, it does not grant access. What it must never do is
 * offer a write path that does not exist — the `REV Trustee` role holds no
 * `prvCreaterev_review`, so when there is no review row the screen says so plainly and
 * offers nothing to click.
 */
import { VERDICT_LABELS } from "../dataverse/schema";
import { sameRecord } from "../dataverse/odata";
import type { CurrentUser, ReviewRow, VerdictSlot } from "../dataverse/types";

export type SlotResolution =
  | {
      kind: "no-review-row";
      heading: string;
      explanation: string;
    }
  | {
      kind: "unknown-user";
      heading: string;
      explanation: string;
    }
  | {
      kind: "not-assigned";
      heading: string;
      explanation: string;
    }
  | {
      kind: "finalised";
      slot: VerdictSlot;
      verdict: number | null;
      notes: string | null;
      heading: string;
      explanation: string;
    }
  | {
      kind: "writable";
      slot: VerdictSlot;
      verdict: number | null;
      notes: string | null;
    };

/** The columns a given slot writes. The only place this mapping is stated. */
export function slotColumns(slot: VerdictSlot): { verdict: string; notes: string } {
  return slot === "trustee1"
    ? { verdict: "rev_verdict1", notes: "rev_notes1" }
    : { verdict: "rev_verdict2", notes: "rev_notes2" };
}

function existingFor(review: ReviewRow, slot: VerdictSlot): {
  verdict: number | null;
  notes: string | null;
} {
  return slot === "trustee1"
    ? { verdict: review.verdict1, notes: review.notes1 }
    : { verdict: review.verdict2, notes: review.notes2 };
}

/**
 * Resolves what the signed-in user may do with a review row.
 *
 * The order of the checks is the design. "No review row" is answered before anything
 * about the user, because with no row there is nothing to say about slots; and identity
 * is answered before assignment, because "we could not work out who you are" and "you
 * are not on this panel" are different problems with different fixes and must not be
 * shown as the same message.
 */
export function resolveSlot(
  review: ReviewRow | null,
  user: CurrentUser,
): SlotResolution {
  if (review === null) {
    return {
      kind: "no-review-row",
      heading: "No review record for this round",
      explanation:
        "No review record has been created for this application, so there is nowhere to " +
        "record a verdict yet. Review records are created by the process owner ahead of the " +
        "panel — trustees cannot create one. Ask the process owner to prepare this round.",
    };
  }

  if (user.systemUserId === null) {
    return {
      kind: "unknown-user",
      heading: "Could not confirm who you are signed in as",
      explanation:
        (user.unresolvedReason ?? "Your user record could not be matched.") +
        " Until that is resolved the review record is read-only, because the portal cannot " +
        "tell which of the two trustee slots is yours.",
    };
  }

  let slot: VerdictSlot | null = null;
  if (sameRecord(review.trustee1Id, user.systemUserId)) {
    slot = "trustee1";
  } else if (sameRecord(review.trustee2Id, user.systemUserId)) {
    slot = "trustee2";
  }

  if (slot === null) {
    return {
      kind: "not-assigned",
      heading: "You are not one of the two trustees on this review",
      explanation:
        "This review record names two trustees, and you are not either of them, so it is " +
        "read-only to you. You can still read the whole anonymised case. If you should be " +
        "on this panel, ask the process owner to assign you.",
    };
  }

  const existing = existingFor(review, slot);

  if (review.finalisedOn !== null) {
    return {
      kind: "finalised",
      slot,
      verdict: existing.verdict,
      notes: existing.notes,
      heading: "This round has been finalised",
      explanation:
        "The process owner has finalised this round, so the recorded verdicts have already " +
        "been applied to the grant records and can no longer be changed here. Your recorded " +
        "verdict is shown below" +
        (existing.verdict === null
          ? ", and no verdict was recorded against your slot."
          : `: ${VERDICT_LABELS[existing.verdict] ?? String(existing.verdict)}.`),
    };
  }

  return { kind: "writable", slot, verdict: existing.verdict, notes: existing.notes };
}
