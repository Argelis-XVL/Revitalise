/**
 * `ownVerdictState` — the signed-in trustee's own verdict (portal TAD trustee-portal-design-2
 * ADR-086 point 3; SDD A-14, FR-116, FR-117; US-012 AC-11).
 */
import { describe, expect, it } from "vitest";
import {
  countAwaiting,
  decidedVerdictAriaLabel,
  ownVerdictState,
  verdictStateWord,
  verdictTone,
} from "./ownVerdict";
import { TRUSTEE_1_ID, TRUSTEE_2_ID, makeReview, makeUser } from "../test/harness";
import { VERDICT_VALUES } from "../dataverse/schema";

describe("ownVerdictState", () => {
  it("is 'decided' when the trustee's OWN slot holds a verdict — slot 1 or slot 2", () => {
    expect(ownVerdictState(makeReview({ verdict1: VERDICT_VALUES.approve }), makeUser())).toEqual({
      kind: "decided",
      verdict: VERDICT_VALUES.approve,
      finalised: false,
    });
    expect(
      ownVerdictState(makeReview({ verdict2: VERDICT_VALUES.reject }), makeUser({ systemUserId: TRUSTEE_2_ID })),
    ).toEqual({ kind: "decided", verdict: VERDICT_VALUES.reject, finalised: false });
  });

  it("reads 'awaiting' when only the OTHER trustee has decided — the other slot is never read", () => {
    const review = makeReview({ verdict2: VERDICT_VALUES.approve, verdict1: null });
    expect(ownVerdictState(review, makeUser({ systemUserId: TRUSTEE_1_ID }))).toEqual({ kind: "awaiting" });
  });

  it("is 'decided' with finalised=true after finalisation, and 'none' when finalised with the own slot empty", () => {
    expect(
      ownVerdictState(makeReview({ verdict1: VERDICT_VALUES.defer, finalisedOn: "2026-10-20T00:00:00Z" }), makeUser()),
    ).toEqual({ kind: "decided", verdict: VERDICT_VALUES.defer, finalised: true });
    expect(ownVerdictState(makeReview({ finalisedOn: "2026-10-20T00:00:00Z" }), makeUser())).toEqual({ kind: "none" });
  });

  it("is 'none' with no review row, for a user on neither slot, and for an unidentified user", () => {
    expect(ownVerdictState(null, makeUser())).toEqual({ kind: "none" });
    expect(
      ownVerdictState(makeReview(), makeUser({ systemUserId: "99999999-9999-4999-8999-999999999999" })),
    ).toEqual({ kind: "none" });
    expect(
      ownVerdictState(makeReview({ verdict1: 1 }), makeUser({ systemUserId: null, unresolvedReason: "x" })),
    ).toEqual({ kind: "none" });
  });

  it("counts only the awaiting states", () => {
    expect(
      countAwaiting([
        { kind: "awaiting" },
        { kind: "decided", verdict: 1, finalised: false },
        { kind: "none" },
        { kind: "awaiting" },
      ]),
    ).toBe(2);
    expect(countAwaiting([])).toBe(0);
  });
});

describe("the verdict word, tone and accessible name", () => {
  it("says what was decided, and never blanks an unknown value", () => {
    expect([1, 2, 3].map(verdictStateWord)).toEqual(["Approved", "Deferred", "Rejected"]);
    expect(verdictStateWord(7)).toBe("Unknown (7)");
    expect([1, 2, 3, 7].map(verdictTone)).toEqual(["approved", "deferred", "rejected", "neutral"]);
  });

  it("contains the visible word (WCAG 2.5.3) and says whether it can still be changed", () => {
    expect(decidedVerdictAriaLabel(1, false, "REV-2026-001")).toBe(
      "Approved — your verdict on REV-2026-001. Open to view or change it",
    );
    expect(decidedVerdictAriaLabel(3, true, "REV-2026-001")).toBe(
      "Rejected — your verdict on REV-2026-001. Open to view it",
    );
  });
});
