/**
 * The landing screen's two freshness statements — TAD §8.3.
 *
 * Split out of `LandingPage.test.tsx` VERBATIM by ADR-066 of
 * `docs/architecture/trustee-portal-design-2-architecture.md` (Revision 3): no assertion here
 * changed in the move. The card-layout app words these two statements differently by reviewer
 * decision (R11, R12), so it carries its own copy of this file asserting its own wording and the
 * same properties, while `LandingPage.test.tsx` stays identical in both apps and keeps every
 * other Round overview assertion binding on both.
 */
import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LandingPage } from "./LandingPage";
import { makeRepository, makeRoundFinance, renderWithProviders } from "../test/harness";
import type { TrusteeRepository } from "../dataverse/types";

function renderLanding(overrides: Partial<TrusteeRepository> = {}) {
  return renderWithProviders(
    <LandingPage
      onOpenList={() => {
        /* navigation is the shell's job; asserted in App.test.tsx */
      }}
    />,
    makeRepository(overrides),
  );
}

describe("LandingPage — the two freshness statements (TAD §8.3)", () => {
  it("shows the flow's computedOn stamp with its own denominator", async () => {
    renderLanding();
    expect(
      await screen.findByText(/round figures computed on 25 aug 2026, 13:05 utc/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/over 434 applications received in this round/i),
    ).toBeInTheDocument();
  });

  it("shows FR-063's as-at date separately, and never as one statement covering both", async () => {
    renderLanding();
    const manual = await screen.findByText(/entered by hand and are as at 20 aug 2026/i);
    const computed = screen.getByText(/round figures computed on/i);
    // Two distinct elements with distinct wording. One "as at" line covering both would be
    // wrong about one of them: these figures are a person's last data entry, the ones
    // beside them are seconds old.
    expect(manual).not.toBe(computed);
    expect(manual.textContent).toContain("computed just now");
  });

  it("says the as-at date is missing rather than letting silence read as currency", async () => {
    renderLanding({
      getOpenRound: () =>
        Promise.resolve({ kind: "one", round: makeRoundFinance({ figuresAsAt: null }) }),
    });
    expect(await screen.findByText(/carry no as-at date/i)).toBeInTheDocument();
  });

  it("marks both stamps for the print stylesheet, so a printed pack carries computedOn", async () => {
    // TAD §6.4: with nothing persisted server-side, the printed pack is the only durable
    // record of the figures a board saw.
    const { container } = renderLanding();
    await screen.findByText(/round figures computed on/i);
    const stamps = container.querySelectorAll('[data-print="stamp"]');
    expect(stamps).toHaveLength(2);
    expect(
      Array.from(stamps).some((stamp) => stamp.textContent?.includes("computed on")),
    ).toBe(true);
  });
});
