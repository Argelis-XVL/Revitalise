/**
 * Slot mapping — WBS 6.4. All five outcomes, including the two that must offer no write
 * path at all.
 */
import { describe, expect, it } from "vitest";
import { resolveSlot, slotColumns } from "./slots";
import {
  makeReview,
  makeUser,
  OTHER_USER_ID,
  TRUSTEE_1_ID,
  TRUSTEE_2_ID,
} from "../test/harness";

describe("slotColumns", () => {
  it("maps trustee 1 to the first verdict and notes pair", () => {
    expect(slotColumns("trustee1")).toEqual({ verdict: "rev_verdict1", notes: "rev_notes1" });
  });

  it("maps trustee 2 to the second verdict and notes pair", () => {
    expect(slotColumns("trustee2")).toEqual({ verdict: "rev_verdict2", notes: "rev_notes2" });
  });
});

describe("resolveSlot", () => {
  it("gives trustee 1 a writable slot with their existing verdict and notes", () => {
    const resolution = resolveSlot(
      makeReview({ verdict1: 2, notes1: "Defer for now." }),
      makeUser({ systemUserId: TRUSTEE_1_ID }),
    );
    expect(resolution).toEqual({
      kind: "writable",
      slot: "trustee1",
      verdict: 2,
      notes: "Defer for now.",
    });
  });

  it("gives trustee 2 the second slot, not the first", () => {
    const resolution = resolveSlot(
      makeReview({ verdict2: 1, notes2: "Support." }),
      makeUser({ systemUserId: TRUSTEE_2_ID }),
    );
    expect(resolution).toEqual({
      kind: "writable",
      slot: "trustee2",
      verdict: 1,
      notes: "Support.",
    });
  });

  it("makes the row read-only for a user who is neither trustee", () => {
    const resolution = resolveSlot(makeReview(), makeUser({ systemUserId: OTHER_USER_ID }));
    expect(resolution.kind).toBe("not-assigned");
    if (resolution.kind !== "not-assigned") throw new Error("unreachable");
    // The message must say they can still read the case — read access is unaffected.
    expect(resolution.explanation).toMatch(/read/i);
  });

  it("matches a trustee whose id differs only in case and braces", () => {
    // Not cosmetic. If the lookup value arrived brace-wrapped or upper-case and the
    // comparison were a raw string equality, a real trustee would get a read-only screen
    // and nothing would report an error.
    const resolution = resolveSlot(
      makeReview({ trustee1Id: `{${TRUSTEE_1_ID.toUpperCase()}}` }),
      makeUser({ systemUserId: TRUSTEE_1_ID }),
    );
    expect(resolution.kind).toBe("writable");
  });

  it("never matches a slot when both sides are null", () => {
    // Two unassigned slots must not make an unidentified user "both trustees".
    const resolution = resolveSlot(
      makeReview({ trustee1Id: null, trustee2Id: null }),
      makeUser({ systemUserId: TRUSTEE_1_ID }),
    );
    expect(resolution.kind).toBe("not-assigned");
  });

  it("reports no review row as its own state, with no write path", () => {
    const resolution = resolveSlot(null, makeUser());
    expect(resolution.kind).toBe("no-review-row");
    if (resolution.kind !== "no-review-row") throw new Error("unreachable");
    // The REV Trustee role holds no prvCreaterev_review, so the message must point at
    // the process owner rather than offer the trustee an action.
    expect(resolution.explanation).toMatch(/process owner/i);
    expect(resolution.explanation).toMatch(/cannot create/i);
  });

  it("reports an unresolved identity separately from being unassigned, and carries the reason", () => {
    const resolution = resolveSlot(
      makeReview(),
      makeUser({ systemUserId: null, unresolvedReason: "No user record matches your Entra ID account." }),
    );
    expect(resolution.kind).toBe("unknown-user");
    if (resolution.kind !== "unknown-user") throw new Error("unreachable");
    expect(resolution.explanation).toContain("No user record matches your Entra ID account.");
  });

  it("answers the missing review row before anything about the user", () => {
    // Order matters: with no row there is nothing to say about slots or identity.
    expect(resolveSlot(null, makeUser({ systemUserId: null })).kind).toBe("no-review-row");
  });

  it("locks a finalised round read-only while still showing what was recorded", () => {
    const resolution = resolveSlot(
      makeReview({ verdict1: 3, notes1: "Reject.", finalisedOn: "2026-10-02T09:00:00Z" }),
      makeUser({ systemUserId: TRUSTEE_1_ID }),
    );
    expect(resolution.kind).toBe("finalised");
    if (resolution.kind !== "finalised") throw new Error("unreachable");
    expect(resolution.slot).toBe("trustee1");
    expect(resolution.verdict).toBe(3);
    expect(resolution.explanation).toContain("Reject");
  });
});
