/**
 * The detail screen — WBS 6.3 and 6.4 together, plus the FR-038 direct-read guard.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ApplicationDetailPage } from "./ApplicationDetailPage";
import { APPLICATION_DETAIL_LAYOUT, isRowVisible } from "../domain/applicationDetailLayout";
import {
  APPLICATION_ID,
  makeDetail,
  makeRepository,
  makeReview,
  makeUser,
  renderWithProviders,
} from "../test/harness";

function renderPage(
  overrides = {},
  groupProps: { groupCode?: string | null; onBackToGroup?: (() => void) | null } = {},
) {
  const repository = makeRepository(overrides);
  const view = renderWithProviders(
    <ApplicationDetailPage
      applicationId={APPLICATION_ID}
      fallbackReference="REV-2026-001"
      user={makeUser()}
      groupCode={groupProps.groupCode}
      onBackToGroup={groupProps.onBackToGroup}
    />,
    repository,
  );
  return { repository, container: view.container };
}

describe("ApplicationDetailPage", () => {
  it("shows one h1, then the Pack's five sections, the staff recommendation and the verdict, as h2s in that order (WI-0005)", async () => {
    renderPage();
    // Wait for the PANELS, not the h1: the h1 renders immediately from the reference the
    // list already knew, so waiting on it proves nothing about the fetch.
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 2 }).length).toBeGreaterThan(0);
    });
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Application REV-2026-001");
    const panels = screen.getAllByRole("heading", { level: 2 }).map((h) => h.textContent);
    // The order is the reading order AND the print order — nothing reorders for print. The
    // section list comes from the spec, whose own test pins it to the PDF; this asserts the
    // screen renders the spec and nothing else in between.
    expect(panels).toEqual([
      ...APPLICATION_DETAIL_LAYOUT.map((section) => section.heading),
      "Staff recommendation",
      "Your verdict",
    ]);
    expect(panels.slice(0, 5)).toEqual([
      "Summary",
      "Application Details",
      "About Applicant",
      "Current Circumstances",
      "Financial Eligibility",
    ]);
  });

  it("renders every section's rows, sub-headings and labels exactly as the spec lists them (WI-0005)", async () => {
    const { container } = renderPage();
    await waitFor(() => {
      expect(container.querySelector('dt[data-field="S1"]')).not.toBeNull();
    });
    for (const section of APPLICATION_DETAIL_LAYOUT) {
      const heading = screen.getByRole("heading", { level: 2, name: section.heading });
      const panel = heading.closest("section");
      expect(panel, section.heading).not.toBeNull();
      // Every row id and sub-heading in document order, compared to the spec's own sequence.
      const rendered = Array.from((panel as HTMLElement).querySelectorAll("dt, h3")).map((el) =>
        el.tagName === "H3" ? `h3:${el.textContent ?? ""}` : `${el.getAttribute("data-field") ?? ""}:${el.textContent ?? ""}`,
      );
      const expected = section.groups.flatMap((group) => [
        ...(group.heading === null ? [] : [`h3:${group.heading}`]),
        ...group.rows
          .filter((row) => isRowVisible(row, makeDetail()))
          .map((row) => `${row.id}:${row.label}`),
      ]);
      expect(rendered, section.heading).toEqual(expected);
    }
  });

  it("renders the reviewer's conditional 'other' rows directly after D11 and A3 only when 'Other' is chosen (WI-0005 review)", async () => {
    const { container } = renderPage({
      getApplication: () =>
        Promise.resolve(
          makeDetail({ exceptionalCircumstance: 4, conditionProfile: [3, 10], supportRecipientConditionProfile: [2] }),
        ),
    });
    await waitFor(() => {
      expect(container.querySelector('dt[data-field="D11a"]')).not.toBeNull();
    });
    const ids = Array.from(container.querySelectorAll("dt[data-field]")).map((el) => el.getAttribute("data-field"));
    expect(ids[ids.indexOf("D11") + 1]).toBe("D11a");
    expect(ids[ids.indexOf("A3") + 1]).toBe("A3a");
    // The person supported did not tick "Other", so their note is not shown.
    expect(ids).not.toContain("A3b");
    expect(ids.slice(0, 3)).toEqual(["S0a", "S0b", "S1"]);
  });

  it("omits the conditional rows when 'Other' is not chosen", async () => {
    const { container } = renderPage();
    await waitFor(() => {
      expect(container.querySelector('dt[data-field="D11"]')).not.toBeNull();
    });
    for (const id of ["D11a", "A3a", "A3b"]) {
      expect(container.querySelector(`dt[data-field="${id}"]`), id).toBeNull();
    }
  });

  it("offers a 'Back to group …' route only when opened from a group (EF-04/EF-43, Revision 14)", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 2 }).length).toBeGreaterThan(0);
    });
    // Opened from the flat list (this test's default `renderPage`) — no group to go back to.
    expect(screen.queryByRole("button", { name: /back to group/i })).toBeNull();
  });

  it("renders 'Back to group RA' and calls onBackToGroup when opened from that group", async () => {
    const onBackToGroup = vi.fn();
    renderPage({}, { groupCode: "RA", onBackToGroup });
    const button = await screen.findByRole("button", { name: /back to group ra/i });
    await userEvent.click(button);
    expect(onBackToGroup).toHaveBeenCalledTimes(1);
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
