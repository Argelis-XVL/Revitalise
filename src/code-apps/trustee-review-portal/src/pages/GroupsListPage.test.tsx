/**
 * The group applications screen — EF-43 Δ5
 * (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 50, 2026-09-25).
 *
 * This is the screen `ApplicationsListPage.test.tsx`'s own "the group table (EF-43)" describe
 * block used to cover, before the reviewer asked for the group table to move to its own
 * screen. The behaviour proved here is the same behaviour, minus the "shown above the
 * individual list" framing that no longer applies, plus this screen's own filter bar and two
 * empty states, which are new.
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { GroupsListPage } from "./GroupsListPage";
import { makeRepository, makeSummary, renderWithProviders } from "../test/harness";

function renderPage(repositoryOverrides = {}, onOpenGroup = vi.fn()) {
  const repository = makeRepository(repositoryOverrides);
  const result = renderWithProviders(<GroupsListPage onOpenGroup={onOpenGroup} />, repository);
  return { repository, onOpenGroup, ...result };
}

describe("GroupsListPage", () => {
  it("has its own title, distinct from the individual list's", async () => {
    renderPage({
      listApplicationsForReview: () =>
        Promise.resolve([makeSummary({ id: "a", reference: "REV-2026-010", groupLinkage: "RA" })]),
    });
    expect(
      await screen.findByRole("heading", { level: 1, name: "Group applications" }),
    ).toBeInTheDocument();
  });

  it("says so when nothing visible carries a group code, distinct from a filter mismatch", async () => {
    renderPage({
      listApplicationsForReview: () =>
        Promise.resolve([makeSummary({ id: "a", reference: "REV-2026-001", groupLinkage: null })]),
    });
    const note = await screen.findByRole("note");
    expect(note).toHaveTextContent(/no groups in this round/i);
  });

  it("renders the group table with the plan's own field set", async () => {
    const grouped = () => [
      makeSummary({ id: "a", reference: "REV-2026-010", groupLinkage: "RA", amountRequested: 350 }),
      makeSummary({ id: "b", reference: "REV-2026-011", groupLinkage: "RA", amountRequested: 350 }),
    ];
    renderPage({ listApplicationsForReview: () => Promise.resolve(grouped()) });
    const table = await screen.findByRole("table");
    expect(screen.getByRole("button", { name: /group ra/i })).toBeInTheDocument();
    expect(within(table).getByText("2")).toBeInTheDocument(); // member count
    expect(within(table).getByText("£700.00")).toBeInTheDocument(); // summed requested
  });

  it("opens the group detail page when a group row is activated", async () => {
    const grouped = () => [
      makeSummary({ id: "a", reference: "REV-2026-010", groupLinkage: "RA" }),
      makeSummary({ id: "b", reference: "REV-2026-011", groupLinkage: "RA" }),
    ];
    const onOpenGroup = vi.fn();
    renderPage({ listApplicationsForReview: () => Promise.resolve(grouped()) }, onOpenGroup);
    await userEvent.click(await screen.findByRole("button", { name: /group ra/i }));
    expect(onOpenGroup).toHaveBeenCalledTimes(1);
    expect(onOpenGroup.mock.calls[0]?.[0]).toMatchObject({ code: "RA", memberCount: 2 });
  });

  it("offers its own filter bar, and filtering it changes which groups appear", async () => {
    // Unlike the old embedded design (`domain/groups.ts`'s own header, describing the
    // now-removed constraint), THIS screen's filter bar is expected to filter its own
    // groups — see `GroupsListPage.tsx`'s own header for why that constraint no longer
    // applies once each table has its own screen and its own filter state.
    const grouped = () => [
      makeSummary({
        id: "a",
        reference: "REV-2026-010",
        groupLinkage: "RA",
        reviewRound: "2026-Q3",
      }),
      makeSummary({
        id: "b",
        reference: "REV-2026-011",
        groupLinkage: "RA",
        reviewRound: "2026-Q3",
      }),
      makeSummary({
        id: "c",
        reference: "REV-2026-020",
        groupLinkage: "RB",
        reviewRound: "2026-Q4",
      }),
      makeSummary({
        id: "d",
        reference: "REV-2026-021",
        groupLinkage: "RB",
        reviewRound: "2026-Q4",
      }),
    ];
    renderPage({ listApplicationsForReview: () => Promise.resolve(grouped()) });
    await screen.findByRole("table");
    expect(screen.getByRole("button", { name: /group ra/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /group rb/i })).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText(/review round/i), "2026-Q4");
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /group ra/i })).toBeNull();
    });
    expect(screen.getByRole("button", { name: /group rb/i })).toBeInTheDocument();
  });

  it("says so when the filters match no group, distinct from 'no groups at all'", async () => {
    const grouped = () => [
      makeSummary({
        id: "a",
        reference: "REV-2026-010",
        groupLinkage: "RA",
        reviewRound: "2026-Q3",
      }),
      makeSummary({
        id: "b",
        reference: "REV-2026-011",
        groupLinkage: "RA",
        reviewRound: "2026-Q3",
      }),
    ];
    renderPage({ listApplicationsForReview: () => Promise.resolve(grouped()) });
    await screen.findByRole("table");
    await userEvent.selectOptions(screen.getByLabelText(/review round/i), "2026-Q3");
    // Then narrow with a round that exists on NO row — proves the "filters match nothing"
    // message, not the "no groups exist" one, since a group genuinely exists in this round set.
    await userEvent.type(screen.getByLabelText(/application reference contains/i), "NOTHING-MATCHES");
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent(/no groups match these filters/i);
    });
  });
});
