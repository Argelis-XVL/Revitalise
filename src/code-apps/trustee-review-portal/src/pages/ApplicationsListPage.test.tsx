/**
 * The summary list — WBS 6.2, FR-034, US-012 AC-1, US-013 AC-1/AC-2/AC-3.
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ApplicationsListPage } from "./ApplicationsListPage";
import {
  makeRepository,
  makeSummary,
  makeUser,
  renderWithProviders,
} from "../test/harness";

function rows() {
  return [
    makeSummary({
      id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      reference: "REV-2026-001",
      circumstanceScore: 55,
      status: 6,
      reviewRound: "2026-Q4",
      region: { kind: "known", value: 9 },
    }),
    makeSummary({
      id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      reference: "REV-2026-002",
      circumstanceScore: 12,
      status: 3,
      reviewRound: "2026-Q3",
      region: { kind: "unavailable" },
    }),
  ];
}

function renderPage(repositoryOverrides = {}, onOpen = vi.fn()) {
  const repository = makeRepository({
    listApplicationsForReview: () => Promise.resolve(rows()),
    ...repositoryOverrides,
  });
  const result = renderWithProviders(
    <ApplicationsListPage user={makeUser()} onOpenApplication={onOpen} />,
    repository,
  );
  return { repository, onOpen, ...result };
}

describe("ApplicationsListPage — the data-only view", () => {
  it("renders a real table with the four FR-034 columns plus the decision control", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    const headers = within(table).getAllByRole("columnheader");
    expect(headers).toHaveLength(6);
    // Asserted by accessible name per column rather than on exact textContent: a sort
    // header's text carries its state and its next action too, and pinning the whole
    // string would make an improvement to that wording read as a regression.
    for (const name of [
      /^Application,/,
      /^Circumstance score/,
      /^Region,/,
      /^Preferred dates,/,
      /^Status,/,
      /^Decision$/,
    ]) {
      expect(within(table).getByRole("columnheader", { name })).toBeInTheDocument();
    }
  });

  it("renders each sort control as a real button inside its header cell", async () => {
    // TAD §8 names this explicitly: "sort controls as real buttons". A div with a click
    // handler is not reachable by keyboard and is not announced as actionable.
    renderPage();
    const table = await screen.findByRole("table");
    const scoreHeader = within(table).getByRole("columnheader", { name: /circumstance score/i });
    expect(within(scoreHeader).getByRole("button")).toBeInTheDocument();
  });

  it("reports the sorted state through aria-sort, not through the arrow glyph", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    const scoreHeader = within(table).getByRole("columnheader", { name: /circumstance score/i });
    // Default sort is score descending — highest score first, which is what a trustee
    // comparing cases wants.
    expect(scoreHeader).toHaveAttribute("aria-sort", "descending");
    const referenceHeader = within(table).getByRole("columnheader", { name: /application/i });
    expect(referenceHeader).toHaveAttribute("aria-sort", "none");
  });

  it("flips the sort direction when the same header is activated by keyboard", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    const scoreHeader = within(table).getByRole("columnheader", { name: /circumstance score/i });
    within(scoreHeader).getByRole("button").focus();
    await userEvent.keyboard("{Enter}");
    expect(scoreHeader).toHaveAttribute("aria-sort", "ascending");
  });

  it("sorts the rows, highest score first by default", async () => {
    renderPage();
    await screen.findByRole("table");
    const rowHeaders = screen.getAllByRole("rowheader");
    expect(rowHeaders[0]).toHaveTextContent("REV-2026-001");
    expect(rowHeaders[1]).toHaveTextContent("REV-2026-002");
  });

  it("filters by round, and the filter applies to the whole set rather than a page", async () => {
    renderPage();
    await screen.findByRole("table");
    await userEvent.selectOptions(screen.getByLabelText(/review round/i), "2026-Q3");
    await waitFor(() => {
      expect(screen.getAllByRole("rowheader")).toHaveLength(1);
    });
    expect(screen.getByRole("rowheader")).toHaveTextContent("REV-2026-002");
  });

  it("offers only the rounds present in the data — never a configured list", async () => {
    // The REV Trustee role can read neither rev_setting nor an environment variable
    // value, so the rounds must come from the rows themselves.
    renderPage();
    await screen.findByRole("table");
    const select = screen.getByLabelText(/review round/i);
    expect(within(select).getAllByRole("option").map((o) => o.textContent)).toEqual([
      "All rounds available to you",
      "2026-Q4",
      "2026-Q3",
    ]);
  });

  it("says so when the filters match nothing, instead of showing an empty table", async () => {
    renderPage();
    await screen.findByRole("table");
    await userEvent.type(screen.getByLabelText(/reference contains/i), "NOTHING-MATCHES");
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent(/no applications match these filters/i);
    });
    expect(screen.queryByRole("table")).toBeNull();
  });

  it("renders a known region as its label, and an unreadable one as text", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    expect(within(table).getByText("South West")).toBeInTheDocument();
    // Never a blank cell: a blank would read as "nothing recorded" when the truth is
    // "the portal could not read the applicant row".
    expect(within(table).getByText("Not available")).toBeInTheDocument();
  });

  it("offers a region filter for the regions present, and applies it", async () => {
    renderPage();
    await screen.findByRole("table");
    const select = screen.getByLabelText(/^region$/i);
    expect(within(select).getAllByRole("option").map((o) => o.textContent)).toEqual([
      "All regions",
      "South West",
    ]);
    await userEvent.selectOptions(select, "9");
    await waitFor(() => {
      expect(screen.getAllByRole("rowheader")).toHaveLength(1);
    });
    expect(screen.getByRole("rowheader")).toHaveTextContent("REV-2026-001");
  });

  it("ships no region filter at all when no region is readable", async () => {
    // A control that cannot work is worse than an absent one.
    renderPage({
      listApplicationsForReview: () =>
        Promise.resolve([makeSummary({ region: { kind: "unavailable" } })]),
    });
    await screen.findByRole("table");
    expect(screen.queryByLabelText(/^region$/i)).toBeNull();
  });

  it("shows the status as text", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    // Scoped to the table: the same labels also appear as options in the status filter.
    expect(within(table).getByText("Eligible for Panel")).toBeInTheDocument();
    expect(within(table).getByText("Borderline")).toBeInTheDocument();
  });

  it("opens the full case from the reference button", async () => {
    const onOpen = vi.fn();
    renderPage({}, onOpen);
    await screen.findByRole("table");
    await userEvent.click(screen.getByRole("button", { name: /REV-2026-001, open the full case/i }));
    expect(onOpen).toHaveBeenCalledTimes(1);
  });

  it("lets a trustee record a verdict without leaving the list (US-013 AC-3)", async () => {
    renderPage();
    await screen.findByRole("table");
    await userEvent.click(
      screen.getByRole("button", { name: /record verdict for REV-2026-001/i }),
    );
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent(/record a verdict for REV-2026-001/i);
    expect(within(dialog).getByRole("radio", { name: "Approve" })).toBeInTheDocument();
  });

  it("announces the visible count in a live region, and captions the table", async () => {
    renderPage();
    const table = await screen.findByRole("table");
    expect(screen.getByText("Showing 2 of 2 applications.")).toBeInTheDocument();
    expect(within(table).getByText("2 applications under review.")).toBeInTheDocument();
  });
});

describe("ApplicationsListPage — states that are not a list", () => {
  it("shows a loading state", () => {
    renderPage({ listApplicationsForReview: () => new Promise(() => undefined) });
    expect(screen.getByText(/loading the applications under review/i)).toBeInTheDocument();
  });

  it("surfaces a load failure in the page with a retry, never a blank screen", async () => {
    renderPage({
      listApplicationsForReview: () => Promise.reject(new Error("Connector unavailable.")),
    });
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/could not load the applications/i);
    expect(alert).toHaveTextContent("Connector unavailable.");
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });

  it("explains an empty round rather than showing an empty table", async () => {
    renderPage({ listApplicationsForReview: () => Promise.resolve([]) });
    const note = await screen.findByRole("note");
    expect(note).toHaveTextContent(/no applications are available to you/i);
    expect(note).toHaveTextContent(/normal between panels/i);
  });
});
