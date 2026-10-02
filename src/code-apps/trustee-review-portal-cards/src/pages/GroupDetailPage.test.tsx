/**
 * The group detail page (EF-43).
 *
 * The one assertion this file exists to make load-bearing: the circumstance-score /
 * "Current Circumstances" section an individual application's own detail page shows
 * (`CasePanels.tsx`'s `ScorePanel`, heading "Summary" as of Revision 14) is ABSENT here — the
 * plan's own settled decision (`docs/plans/emily-review-feedback-2026-09-plan.md` §4.3,
 * the 12-of-12 worked example). See `GroupDetailPage.tsx`'s header for why this is proved
 * by assertion rather than by "the component is never imported".
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { GroupDetailPage } from "./GroupDetailPage";
import type { GroupSummary } from "../domain/groups";
import { makeRepository, makeSummary, makeUser, renderWithProviders } from "../test/harness";

function group(overrides: Partial<GroupSummary> = {}): GroupSummary {
  return {
    code: "RA",
    memberCount: 2,
    totalRequested: 700,
    sharedStart: "2026-10-05T00:00:00Z",
    sharedEnd: "2026-10-12T00:00:00Z",
    members: [
      makeSummary({ id: "a", reference: "REV-2026-010", groupLinkage: "RA" }),
      makeSummary({ id: "b", reference: "REV-2026-011", groupLinkage: "RA" }),
    ],
    ...overrides,
  };
}

function renderPage(theGroup = group(), onOpenApplication = vi.fn()) {
  const repository = makeRepository();
  const result = renderWithProviders(
    <GroupDetailPage group={theGroup} user={makeUser()} onOpenApplication={onOpenApplication} />,
    repository,
  );
  return { onOpenApplication, ...result };
}

describe("GroupDetailPage", () => {
  it("titles the page with the group code", () => {
    renderPage();
    expect(screen.getByRole("heading", { level: 1, name: /group ra/i })).toBeInTheDocument();
  });

  it("renders the group's own fixed summary fields, and no cost field", () => {
    renderPage(group({ code: "RA", memberCount: 2, totalRequested: 700 }));
    expect(screen.getByText("Group code")).toBeInTheDocument();
    expect(screen.getByText("RA")).toBeInTheDocument();
    expect(screen.getByText("Members")).toBeInTheDocument();
    expect(screen.getByText("Group total requested")).toBeInTheDocument();
    expect(screen.getByText("£700.00")).toBeInTheDocument();
    expect(screen.getByText("Shared dates")).toBeInTheDocument();
    // Deliberately absent — see `domain/groups.ts`'s header on why no group cost figure
    // is invented.
    expect(screen.queryByText(/group total.*cost/i)).toBeNull();
  });

  it("lists the member applications with their normal summary fields", () => {
    renderPage();
    const table = screen.getByRole("table");
    expect(within(table).getByText("REV-2026-010")).toBeInTheDocument();
    expect(within(table).getByText("REV-2026-011")).toBeInTheDocument();
  });

  it("does NOT render the circumstance score / score breakdown section (settled: 12-of-12 worked example)", () => {
    renderPage();
    // `CasePanels.tsx`'s `ScorePanel` — heading "Summary" as of Revision 14 — must not
    // appear. Exact name match, so this does not collide with this page's OWN "Group summary"
    // panel heading below.
    expect(screen.queryByRole("heading", { name: "Summary" })).toBeNull();
    expect(screen.queryByText(/no score breakdown recorded/i)).toBeNull();
    expect(screen.queryByText(/current circumstances/i)).toBeNull();
  });

  it("opens a member's individual application detail page from the member table", async () => {
    const onOpenApplication = vi.fn();
    renderPage(group(), onOpenApplication);
    await userEvent.click(
      screen.getByRole("button", { name: /REV-2026-010, open the full case/i }),
    );
    expect(onOpenApplication).toHaveBeenCalledTimes(1);
    expect(onOpenApplication.mock.calls[0]?.[0]).toMatchObject({ reference: "REV-2026-010" });
  });

  it("still offers Record verdict on a member row, same as the flat list", async () => {
    renderPage();
    await userEvent.click(
      screen.getByRole("button", { name: /record verdict for REV-2026-010/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent(/record a verdict for REV-2026-010/i);
  });

  it("sets the document title to the group", async () => {
    renderPage();
    await waitFor(() => {
      expect(document.title).toBe("Group RA — Trustee Review Portal");
    });
  });
});
