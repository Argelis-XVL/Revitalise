/**
 * The group table (EF-43) — rendering and row-click navigation, in isolation from the page
 * that composes it (`GroupsListPage.test.tsx` covers the derivation-and-integration path,
 * since EF-43 Δ5 moved this component there from `ApplicationsListPage`; this file covers
 * the component's own markup and accessible names, unchanged by that move).
 */
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { GroupsTable } from "./GroupsTable";
import type { GroupSummary } from "../domain/groups";
import { makeSummary } from "../test/harness";

function group(overrides: Partial<GroupSummary> = {}): GroupSummary {
  return {
    code: "RA",
    memberCount: 4,
    totalRequested: 1400,
    sharedStart: "2026-10-05T00:00:00Z",
    sharedEnd: "2026-10-12T00:00:00Z",
    members: [makeSummary({ groupLinkage: "RA" })],
    ...overrides,
  };
}

describe("GroupsTable", () => {
  it("renders one row per group with the four fixed columns and no cost column", () => {
    render(<GroupsTable groups={[group()]} onOpen={vi.fn()} />);
    const table = screen.getByRole("table");
    const headers = within(table).getAllByRole("columnheader").map((h) => h.textContent);
    expect(headers).toEqual(["Group", "Members", "Group total requested", "Shared dates"]);
    expect(within(table).queryByText(/cost/i)).toBeNull();
  });

  it("shows the member count and the summed requested total", () => {
    render(<GroupsTable groups={[group({ memberCount: 4, totalRequested: 1400 })]} onOpen={vi.fn()} />);
    const table = screen.getByRole("table");
    expect(within(table).getByText("4")).toBeInTheDocument();
    expect(within(table).getByText("£1,400.00")).toBeInTheDocument();
  });

  it("shows the group's requested total as 'Not recorded' when no member has one", () => {
    render(<GroupsTable groups={[group({ totalRequested: null })]} onOpen={vi.fn()} />);
    expect(screen.getByText("Not recorded")).toBeInTheDocument();
  });

  it("opens the group when its row control is activated by keyboard, not only by click", async () => {
    const onOpen = vi.fn();
    const theGroup = group();
    render(<GroupsTable groups={[theGroup]} onOpen={onOpen} />);
    const button = screen.getByRole("button", { name: /group ra, open the group's applications/i });
    button.focus();
    await userEvent.keyboard("{Enter}");
    expect(onOpen).toHaveBeenCalledWith(theGroup);
  });

  it("uses a real button for row navigation, not a fragment link", () => {
    // The same regression `ApplicationsTable.tsx`'s own header warns against — the supplied
    // mockup's `<a href="#" onClick={preventDefault}>` pattern is refused here too.
    render(<GroupsTable groups={[group()]} onOpen={vi.fn()} />);
    const control = screen.getByRole("button", { name: /group ra/i });
    expect(control.tagName).toBe("BUTTON");
    expect(control).toHaveAttribute("type", "button");
  });

  it("pluralises the caption correctly for one group and for many", () => {
    const { rerender } = render(<GroupsTable groups={[group()]} onOpen={vi.fn()} />);
    expect(screen.getByText("1 group of linked applications.")).toBeInTheDocument();
    rerender(<GroupsTable groups={[group({ code: "RA" }), group({ code: "43" })]} onOpen={vi.fn()} />);
    expect(screen.getByText("2 groups of linked applications.")).toBeInTheDocument();
  });
});
