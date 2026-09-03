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

function renderPage(overrides = {}) {
  const repository = makeRepository(overrides);
  const view = renderWithProviders(
    <ApplicationDetailPage
      applicationId={APPLICATION_ID}
      fallbackReference="REV-2026-001"
      user={makeUser()}
    />,
    repository,
  );
  return { repository, container: view.container };
}

describe("ApplicationDetailPage", () => {
  it("shows one h1 and the eight FR-035 panels as h2s, in reading order (Amendment A-05)", async () => {
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
    // free-text companion to that structured data, not a screen of its own. Financial
    // eligibility / condition and circumstance / helper-referee-emergency contact are
    // Amendment A-05's three further board-pack groups (SDD §7.1b), added after the
    // structured pair and before the staff recommendation.
    expect(panels).toEqual([
      "Anonymised narrative",
      "Circumstance score",
      "Holiday details",
      "Care-support description",
      "Financial eligibility",
      "Condition and circumstance",
      "Helper, referee and emergency contact",
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

/**
 * Revision 11 (2026-09-02, wbs:6.8) — reviewer items 6, 7 and 8, which are one change to this
 * screen's opening three elements: `<h1>` first, no "Back to the list", "Print this case" alone
 * in the row beneath the title.
 *
 * These are DOM-ORDER and DOM-PRESENCE assertions, not visual ones, and that is the strongest
 * form available here: jsdom computes no layout (`styles/layout.test.ts`'s own header states the
 * limit in full), but "the title is pushed down by the elements above it" is a question about
 * source order, which `compareDocumentPosition` answers exactly.
 */
describe("ApplicationDetailPage — Revision 11, the title and the action row", () => {
  it("renders the h1 BEFORE the action row, so its position does not move with that row (item 6)", async () => {
    renderPage();
    const heading = await screen.findByRole("heading", { level: 1 });
    const print = screen.getByRole("button", { name: /print this case/i });
    const row = print.closest("div");
    expect(row).not.toBeNull();
    // DOCUMENT_POSITION_FOLLOWING (4): the row comes after the heading. Before this revision
    // the two were the other way round, which is the defect the reviewer reported.
    expect(heading.compareDocumentPosition(row!) & Node.DOCUMENT_POSITION_FOLLOWING).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });

  it("renders no 'Back to the list' control anywhere on the screen (item 7)", async () => {
    // A documented REVERSAL of App.tsx's Revision 7 decision, not a correction of it — see this
    // page's own Revision 11 header. The route back is the persistent nav bar's "Applications
    // list" tab, which this page does not render and App.test.tsx covers.
    renderPage();
    await screen.findByRole("heading", { level: 1 });
    expect(screen.queryByRole("button", { name: /back to the list/i })).toBeNull();
  });

  it("leaves exactly one control in the action row, and it is the print one (item 8)", async () => {
    renderPage();
    const print = await screen.findByRole("button", { name: /print this case/i });
    const row = print.closest("div");
    expect(row?.querySelectorAll("button")).toHaveLength(1);
    // The row is still hidden on paper — a print control that prints itself is FR-039's own
    // invariant, and it survives the row losing a button.
    expect(row?.getAttribute("data-print")).toBe("hide");
  });
});
