/**
 * The detail screen — WBS 6.3 and 6.4 together, plus the FR-038 direct-read guard.
 *
 * CARD-LAYOUT APP (Design 2.0, TAD trustee-portal-design-2). This file is on the parity gate's
 * allow-list: its DOM-order case is replaced by ADR-057's order contract (below); every other
 * case is the first app's, unchanged, plus the page-order and sub-heading cases WI-0071 and
 * WI-0069 need.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ApplicationDetailPage } from "./ApplicationDetailPage";
import { APPLICATION_DETAIL_LAYOUT, isRowVisible } from "../domain/applicationDetailLayout";
import { SECTION_GROUP_ORDER, partitionRows } from "../domain/applicationDetailDisplay";
import {
  APPLICATION_ID,
  makeDetail,
  makeRepository,
  makeReview,
  makeUser,
  renderWithProviders,
} from "../test/harness";

/** Text a screen reader gets from an element: its text with every `aria-hidden` subtree removed. */
function accessibleText(element: Element): string {
  const clone = element.cloneNode(true) as Element;
  clone.querySelectorAll('[aria-hidden="true"]').forEach((node) => {
    node.remove();
  });
  return clone.textContent ?? "";
}

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
  it("shows one h1, then the Summary hero, the Pack's four other sections, the staff recommendation and the verdict, as h2s in that order (WI-0071)", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 2 }).length).toBeGreaterThan(1);
    });
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Application REV-2026-001");
    const names = screen.getAllByRole("heading", { level: 2 }).map((h) => accessibleText(h));
    // The hero's h2 is the design heading, prefixed for assistive technology with the Pack's own
    // section heading; every other h2 is the Pack heading verbatim. Nothing reorders for print.
    expect(names[0]?.startsWith(`${APPLICATION_DETAIL_LAYOUT[0]?.heading ?? ""}: `)).toBe(true);
    expect(names.slice(1)).toEqual([
      ...APPLICATION_DETAIL_LAYOUT.slice(1).map((section) => section.heading),
      "Staff recommendation",
      "Your verdict",
    ]);
    expect(names.slice(1, 5)).toEqual([
      "Application Details",
      "About Applicant",
      "Current Circumstances",
      "Financial Eligibility",
    ]);
  });

  /**
   * ADR-057 — THE ORDER CONTRACT OF THIS APP, replacing the first app's "renders every section's
   * rows … exactly as the spec lists them" case (reviewer R1: "If the fields are grouped in the
   * same sections. It basically is the same only better readable."). Per section:
   *   (a) the rendered row ids are exactly the spec's visible rows — none missing, none extra —
   *       and every label is the spec's, verbatim, to assistive technology;
   *   (b) within each display group, row ids are in Pack order;
   *   (c) the display groups appear in the section's fixed order from applicationDetailDisplay.ts;
   *   (d) is the conditional-rows case below.
   * The ONE property given up is cross-group order, and only in this app.
   */
  for (const [name, detail] of [
    ["defaults", makeDetail()],
    ["every conditional row", makeDetail({ exceptionalCircumstance: 4, conditionProfile: [3, 10], supportRecipientConditionProfile: [2, 10] })],
  ] as const) {
    it(`renders every section's rows exactly once, labelled verbatim, in Pack order within each display group, groups in the fixed order (ADR-057 (a)-(c), ${name})`, async () => {
      const { container } = renderPage({ getApplication: () => Promise.resolve(detail) });
      await waitFor(() => {
        expect(container.querySelector('dt[data-field="S1"]')).not.toBeNull();
      });
      for (const section of APPLICATION_DETAIL_LAYOUT) {
        const root = container.querySelector(
          section.id === "summary" ? `section[data-section="${section.id}"]` : `[data-section="${section.id}"]`,
        )?.closest("section");
        expect(root, section.id).not.toBeNull();
        const terms = Array.from((root as HTMLElement).querySelectorAll("dt[data-field]"));
        const rendered = terms.map((dt) => dt.getAttribute("data-field") ?? "");
        const visible = section.groups.flatMap((group) => group.rows.filter((row) => isRowVisible(row, detail)));
        // (a) none missing, none extra, each label verbatim.
        expect([...rendered].sort(), section.id).toEqual(visible.map((row) => row.id).sort());
        for (const dt of terms) {
          const row = visible.find((r) => r.id === dt.getAttribute("data-field"));
          expect(accessibleText(dt), row?.id).toBe(row?.label);
        }
        // (b) and (c), for each layout group the section has.
        const packOrder = visible.map((row) => row.id);
        const order = SECTION_GROUP_ORDER[section.id] ?? [];
        for (const group of section.groups) {
          const expectedGroups = partitionRows(section.id, group.rows, detail);
          const renderedByGroup = expectedGroups.map((g) =>
            rendered.filter((id) => g.rows.some((r) => r.row.id === id)),
          );
          renderedByGroup.forEach((ids, index) => {
            expect(ids, `${section.id} ${expectedGroups[index]?.kind ?? ""}`).toEqual(
              [...ids].sort((a, b) => packOrder.indexOf(a) - packOrder.indexOf(b)),
            );
          });
          const positions = expectedGroups.map((g) => order.indexOf(g.kind));
          expect(positions, section.id).toEqual([...positions].sort((a, b) => a - b));
          // The groups also appear in that order in the DOM.
          const firstIndex = renderedByGroup.map((ids) => rendered.indexOf(ids[0] ?? ""));
          expect(firstIndex, section.id).toEqual([...firstIndex].sort((a, b) => a - b));
        }
      }
    });
  }

  it("keeps the Pack sub-headings as h3s, and adds only the three approved new ones", async () => {
    const { container } = renderPage();
    await waitFor(() => {
      expect(container.querySelector('dt[data-field="C3"]')).not.toBeNull();
    });
    const h3 = screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent);
    for (const heading of APPLICATION_DETAIL_LAYOUT.flatMap((s) => s.groups.map((g) => g.heading))) {
      if (heading !== null) expect(h3, heading).toContain(heading);
    }
    const approved = new Set(["Costs", "In their words", "Not visible to trustees"]);
    const packHeadings = new Set(APPLICATION_DETAIL_LAYOUT.flatMap((s) => s.groups.map((g) => g.heading)));
    expect(h3.filter((text) => !packHeadings.has(text) && !approved.has(text ?? ""))).toEqual([]);
  });

  it("renders the reviewer's conditional 'other' rows only when 'Other' is chosen, in their trigger row's section, first in its answers (ADR-057 (d))", async () => {
    const { container } = renderPage({
      getApplication: () =>
        Promise.resolve(
          makeDetail({ exceptionalCircumstance: 4, conditionProfile: [3, 10], supportRecipientConditionProfile: [2] }),
        ),
    });
    await waitFor(() => {
      expect(container.querySelector('dt[data-field="D11a"]')).not.toBeNull();
    });
    // D11 is a fact and D11a an answer, so they are in different display groups; D11a is the
    // first answer of Application Details, as it follows D11 directly in the Pack.
    const sectionOf = (id: string) => container.querySelector(`dt[data-field="${id}"]`)?.closest("section");
    expect(sectionOf("D11a")).toBe(sectionOf("D11"));
    expect(sectionOf("A3a")).toBe(sectionOf("A3"));
    const answersOf = (id: string) =>
      Array.from(
        container.querySelector(`dt[data-field="${id}"]`)?.closest('[data-display-group="answers"]')?.querySelectorAll("dt") ?? [],
      ).map((dt) => dt.getAttribute("data-field"));
    expect(answersOf("D11a")[0]).toBe("D11a");
    expect(answersOf("A3a")[0]).toBe("A3a");
    // The person supported did not tick "Other", so their note is not shown.
    expect(container.querySelector('dt[data-field="A3b"]')).toBeNull();
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
