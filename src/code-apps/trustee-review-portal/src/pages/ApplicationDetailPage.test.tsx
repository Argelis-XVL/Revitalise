/**
 * The detail screen — WBS 6.3 and 6.4 together, plus the FR-038 direct-read guard.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ApplicationDetailPage } from "./ApplicationDetailPage";
import {
  APPLICATION_ID,
  makeDetail,
  makeRepository,
  makeReview,
  makeUser,
  renderWithProviders,
} from "../test/harness";

function renderPage(overrides = {}, onBack = vi.fn()) {
  const repository = makeRepository(overrides);
  renderWithProviders(
    <ApplicationDetailPage
      applicationId={APPLICATION_ID}
      fallbackReference="REV-2026-001"
      user={makeUser()}
      onBack={onBack}
    />,
    repository,
  );
  return { repository, onBack };
}

describe("ApplicationDetailPage", () => {
  it("shows one h1 and the five FR-035 panels as h2s, in reading order", async () => {
    renderPage();
    // Wait for the PANELS, not the h1: the h1 renders immediately from the reference the
    // list already knew, so waiting on it proves nothing about the fetch.
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 2 }).length).toBeGreaterThan(0);
    });
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Application REV-2026-001");
    const panels = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    // The order is the reading order AND the print order — nothing reorders for print.
    // Care-support description sits next to Holiday details (WBS 6.3): it is the
    // free-text companion to that structured data, not a screen of its own.
    expect(panels).toEqual([
      "Anonymised narrative",
      "Circumstance score",
      "Holiday details",
      "Care-support description",
      "Staff recommendation",
      "Your verdict",
    ]);
  });

  it("uses the reference already known from the list before the fetch lands", () => {
    renderPage({ getApplication: () => new Promise(() => undefined) });
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("REV-2026-001");
    expect(screen.getByText(/loading the case/i)).toBeInTheDocument();
  });

  it("refuses a case the repository will not return, and explains why (FR-038)", async () => {
    renderPage({ getApplication: () => Promise.resolve(null) });
    const note = await screen.findByRole("note");
    expect(note).toHaveTextContent(/not available to you/i);
    expect(screen.queryByRole("heading", { level: 2, name: /anonymised narrative/i })).toBeNull();
  });

  it("surfaces a load failure with a retry rather than a blank screen", async () => {
    renderPage({ getApplication: () => Promise.reject(new Error("Read failed.")) });
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not load this case/i);
    expect(alert).toHaveTextContent("Read failed.");
  });

  it("goes back to the list", async () => {
    const { onBack } = renderPage();
    await userEvent.click(screen.getByRole("button", { name: /back to the list/i }));
    expect(onBack).toHaveBeenCalledTimes(1);
  });

  it("offers a print control for the same content it displays (FR-039)", async () => {
    const print = vi.fn();
    vi.stubGlobal("print", print);
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /print this case/i }));
    // There is no separate print renderer and no second query: printing prints THIS DOM.
    expect(print).toHaveBeenCalledTimes(1);
    vi.unstubAllGlobals();
  });

  it("shows the withheld narrative state, which is the only state reachable today", async () => {
    renderPage({ getApplication: () => Promise.resolve(makeDetail({ redactionReleased: false })) });
    await waitFor(() => {
      expect(screen.getAllByRole("note").some((n) => /withheld/i.test(n.textContent ?? ""))).toBe(
        true,
      );
    });
  });

  it("shows the staff recommendation from the review row, not from the application", async () => {
    renderPage({
      getReviewForApplication: () =>
        Promise.resolve(makeReview({ staffRecommendation: "Staff recommend approval." })),
    });
    expect(await screen.findByText("Staff recommend approval.")).toBeInTheDocument();
  });

  it("still renders the case when there is no review row, with no write path", async () => {
    renderPage({ getReviewForApplication: () => Promise.resolve(null) });
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 2, name: /your verdict/i })).toBeInTheDocument();
    });
    expect(screen.queryByRole("radio")).toBeNull();
    expect(
      screen.getAllByRole("note").some((n) => /no review record/i.test(n.textContent ?? "")),
    ).toBe(true);
  });
});
