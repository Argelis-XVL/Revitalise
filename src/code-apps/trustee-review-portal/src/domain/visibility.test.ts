/**
 * The fail-closed conjunction (TAD §5.5) — the tests that matter most in this app.
 *
 * These assert OUR logic, not a platform contract. The question "does Dataverse return
 * `true` or `"true"` for a bit column through this connector" is deliberately NOT
 * asserted here: it is an open assumption, and a test written from the same guess as the
 * code would lock the guess in rather than verify it (`IMP-0111`). What is asserted is
 * that anything short of an affirmative true keeps the case hidden.
 */
import { describe, expect, it } from "vitest";
import {
  RELEASED_EMPTY_HEADING,
  WITHHELD_HEADING,
  isVisibleForReview,
  redactedTextState,
  visibleForReview,
} from "./visibility";
import type { ApplicationSummary } from "../dataverse/types";

function row(overrides: Partial<ApplicationSummary>): ApplicationSummary {
  return {
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    reference: "REV-2026-001",
    circumstanceScore: 30,
    exceptionalCircumstance: null,
    preferredStart: null,
    preferredEnd: null,
    status: 6,
    reviewRound: "2026-Q4",
    eligibleForRound: true,
    redactionReleased: false,
    groupLinkage: null,
    amountRequested: null,
    ...overrides,
  };
}

describe("isVisibleForReview — FR-038, TAD §5.5", () => {
  it("shows a case only when it is affirmatively eligible for the round", () => {
    expect(isVisibleForReview(row({ eligibleForRound: true }))).toBe(true);
  });

  it("hides a case whose eligibility is false", () => {
    expect(isVisibleForReview(row({ eligibleForRound: false }))).toBe(false);
  });

  it("hides a case whose eligibility flag is missing entirely", () => {
    // The shape a row takes when the column is absent from the response — which is what
    // an unmapped or newly-added column looks like. Cast at the boundary because the
    // mapped type does not admit `undefined`; the runtime does.
    const missing = { ...row({}) } as Partial<ApplicationSummary>;
    delete missing.eligibleForRound;
    expect(isVisibleForReview(missing as ApplicationSummary)).toBe(false);
  });

  it("keeps only eligible rows out of a mixed set, in order", () => {
    const rows = [
      row({ id: "1".repeat(8) + "-1111-4111-8111-111111111111", reference: "A", eligibleForRound: true }),
      row({ id: "2".repeat(8) + "-2222-4222-8222-222222222222", reference: "B", eligibleForRound: false }),
      row({ id: "3".repeat(8) + "-3333-4333-8333-333333333333", reference: "C", eligibleForRound: true }),
    ];
    expect(visibleForReview(rows).map((r) => r.reference)).toEqual(["A", "C"]);
  });
});

describe("redactedTextState — one gate per answer (WI-0005); the withheld state is first-class", () => {
  it("withholds the text when release is false, even if text is present", () => {
    const state = redactedTextState(false, "Released too early would be a leak");
    expect(state.kind).toBe("withheld");
    // The text must not travel inside the withheld state in any form.
    expect(JSON.stringify(state)).not.toContain("leak");
  });

  it("withholds the text when the release flag is not an affirmative true", () => {
    // The mapper coerces absent / null / "true" to false before this point; this pins that the
    // gate itself also reads anything short of `true` as "no".
    const notTrue = "true" as unknown as boolean;
    expect(redactedTextState(notTrue, "text").kind).toBe("withheld");
  });

  it("reports released-but-empty as its own state, not as withheld and not as text", () => {
    const state = redactedTextState(true, null);
    expect(state.kind).toBe("released-empty");
    if (state.kind === "released-empty") expect(state.heading).toBe(RELEASED_EMPTY_HEADING);
  });

  it("treats a whitespace-only value the same as empty", () => {
    expect(redactedTextState(true, "   \n ").kind).toBe("released-empty");
  });

  it("returns the text once, and only once, release is affirmative and the text is non-blank", () => {
    expect(redactedTextState(true, "An anonymised answer")).toEqual({
      kind: "released",
      text: "An anonymised answer",
    });
  });

  it("gives withheld and released-empty different headings, so they can never read as one state", () => {
    const withheld = redactedTextState(false, null);
    const empty = redactedTextState(true, null);
    expect(withheld.kind === "withheld" && withheld.heading).toBe(WITHHELD_HEADING);
    expect(empty.kind === "released-empty" && empty.heading).toBe(RELEASED_EMPTY_HEADING);
    expect(WITHHELD_HEADING).not.toBe(RELEASED_EMPTY_HEADING);
  });
});
