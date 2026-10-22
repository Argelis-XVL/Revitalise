/**
 * The landing screen's two freshness statements — CARD APP wording (ADR-066 decision 1; reviewer
 * R11 "Design wording", R12 "Use the pill"). The first app's copy of this file asserts its own
 * wording; this one asserts the card app's wording AND the same four properties: two distinct
 * elements, the denominator kept on the page, the missing as-at date said rather than implied,
 * and both stamps marked for print. `LandingPage.freshness.test.tsx` is presentation (ADR-066).
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

describe("LandingPage — the two freshness statements (TAD §8.3, card wording ADR-066)", () => {
  it("shows the flow's computedOn stamp as 'Computed on {date} at {time}', with its own denominator", async () => {
    renderLanding();
    expect(await screen.findByText("Computed on 25 Aug 2026 at 13:05 UTC")).toBeInTheDocument();
    expect(screen.getByText(/over 434 applications\s+received in this round/i)).toBeInTheDocument();
  });

  it("shows FR-063's as-at date separately, after the 'Entered by hand' pill, never as one statement covering both", async () => {
    renderLanding();
    const manual = await screen.findByText(/these figures are as at 20 aug 2026/i);
    const computed = screen.getByText(/computed on/i);
    expect(manual).not.toBe(computed);
    expect(manual.textContent).toContain("computed just now");
    expect(manual.textContent?.startsWith("Entered by hand")).toBe(true);
    expect(manual.textContent).not.toMatch(/are entered by hand and/i);
  });

  it("says the as-at date is missing rather than letting silence read as currency", async () => {
    renderLanding({
      getOpenRound: () =>
        Promise.resolve({ kind: "one", round: makeRoundFinance({ figuresAsAt: null }) }),
    });
    expect(await screen.findByText(/carry no as-at date/i)).toBeInTheDocument();
  });

  it("marks both stamps for the print stylesheet, so a printed pack carries computedOn", async () => {
    const { container } = renderLanding();
    await screen.findByText(/computed on/i);
    const stamps = container.querySelectorAll('[data-print="stamp"]');
    expect(stamps).toHaveLength(2);
    expect(Array.from(stamps).some((stamp) => stamp.textContent?.includes("Computed on"))).toBe(true);
  });
});
