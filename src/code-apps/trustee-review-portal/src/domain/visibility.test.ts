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
import { careSupportState, isVisibleForReview, narrativeState, visibleForReview } from "./visibility";
import type { ApplicationSummary } from "../dataverse/types";

function row(overrides: Partial<ApplicationSummary>): ApplicationSummary {
  return {
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    reference: "REV-2026-001",
    circumstanceScore: 30,
    region: { kind: "unavailable" },
    preferredStart: null,
    preferredEnd: null,
    status: 6,
    reviewRound: "2026-Q4",
    eligibleForRound: true,
    redactionReleased: false,
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

describe("narrativeState — the withheld state is first-class", () => {
  it("withholds the narrative when release is false, even if text is present", () => {
    // The state Automation #5 being deferred puts every application in today, and the
    // reason `EX-003` judged this safe to build ahead of DPO sign-off. Text present and
    // release false must still withhold: release is the gate, not emptiness.
    const state = narrativeState({
      redactionReleased: false,
      redactedNarrative: "Some redacted text that must not be shown.",
    });
    expect(state.kind).toBe("withheld");
    if (state.kind !== "withheld") throw new Error("unreachable");
    expect(state.heading).toMatch(/withheld/i);
    expect(state.explanation.length).toBeGreaterThan(0);
    expect(state.explanation).not.toContain("Some redacted text");
  });

  it("withholds the narrative when the release flag is missing", () => {
    const state = narrativeState({
      redactionReleased: undefined as unknown as boolean,
      redactedNarrative: "text",
    });
    expect(state.kind).toBe("withheld");
  });

  it("reports released-but-empty as its own state, not as withheld and not as text", () => {
    expect(narrativeState({ redactionReleased: true, redactedNarrative: null }).kind).toBe(
      "released-empty",
    );
    expect(narrativeState({ redactionReleased: true, redactedNarrative: "   " }).kind).toBe(
      "released-empty",
    );
  });

  it("returns the text once, and only once, release is affirmative", () => {
    const state = narrativeState({
      redactionReleased: true,
      redactedNarrative: "Redacted narrative.",
    });
    expect(state).toEqual({ kind: "released", text: "Redacted narrative." });
  });
});

/**
 * The care-support description panel's three states (FR-035, TAD §3.2.1, WBS 6.3).
 * Same fail-closed gate as `narrativeState` — reused, not re-implemented — plus the
 * `released-empty` state a single-field narrative never needed: release can be
 * affirmed while none of the three columns has been scrubbed yet, and that must not
 * render as "nothing was recorded".
 */
describe("careSupportState — withheld, released-empty and released", () => {
  function detail(overrides: {
    redactionReleased?: boolean;
    redactedCareSupportDescription?: string | null;
    redactedCareProvidedExample?: string | null;
    redactedOtherCareProvidedType?: string | null;
  }) {
    return {
      redactionReleased: false,
      redactedCareSupportDescription: null,
      redactedCareProvidedExample: null,
      redactedOtherCareProvidedType: null,
      ...overrides,
    };
  }

  it("withholds the panel when release is not affirmatively true, even with text present", () => {
    const state = careSupportState(
      detail({
        redactionReleased: false,
        redactedCareSupportDescription: "Text that must not be shown.",
      }),
    );
    expect(state.kind).toBe("withheld");
    if (state.kind !== "withheld") throw new Error("unreachable");
    expect(state.heading).toMatch(/withheld/i);
    expect(state.explanation).not.toContain("Text that must not be shown");
  });

  it("withholds the panel when the release flag is missing", () => {
    const state = careSupportState(detail({ redactionReleased: undefined }));
    expect(state.kind).toBe("withheld");
  });

  it("reports released-but-all-three-empty as its own state, not withheld and not text", () => {
    const state = careSupportState(detail({ redactionReleased: true }));
    expect(state.kind).toBe("released-empty");
    if (state.kind !== "released-empty") throw new Error("unreachable");
    // The exact sentence TAD §3.2.1 requires — true whether the source was empty or
    // simply not yet scrubbed, and it must appear verbatim.
    expect(state.explanation).toBe(
      "No redacted care-support description is available for this application.",
    );
  });

  it("treats a whitespace-only value the same as empty, for all three fields", () => {
    const state = careSupportState(
      detail({
        redactionReleased: true,
        redactedCareSupportDescription: "   ",
        redactedCareProvidedExample: "\n",
        redactedOtherCareProvidedType: "",
      }),
    );
    expect(state.kind).toBe("released-empty");
  });

  it("returns released with all three texts once release is affirmative and populated", () => {
    const state = careSupportState(
      detail({
        redactionReleased: true,
        redactedCareSupportDescription: "Description.",
        redactedCareProvidedExample: "Example.",
        redactedOtherCareProvidedType: "Other.",
      }),
    );
    expect(state).toEqual({
      kind: "released",
      description: "Description.",
      example: "Example.",
      otherType: "Other.",
    });
  });

  it("returns released, not released-empty, when only one of the three fields has text", () => {
    // Once any field has genuine content, release has visibly already run for this
    // application — a blank sibling is trustworthy as "not recorded", not "not yet
    // scrubbed". The released-empty message would be false to show here.
    const state = careSupportState(
      detail({ redactionReleased: true, redactedCareSupportDescription: "Description only." }),
    );
    expect(state.kind).toBe("released");
  });
});
