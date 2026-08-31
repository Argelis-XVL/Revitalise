/**
 * The landing screen — FR-056..FR-063, TAD §5.3, §5.4, §8.3.
 *
 * Three groups of assertion, in order of how much they matter:
 *
 *   1. **This screen reads no application or applicant row.** The last block asserts it
 *      directly, because it is the mechanism TAD §1.1 and §6.3 rest on and the one thing
 *      here that a well-meaning change could quietly break.
 *   2. **A null metric renders as nothing.** Not a zero, not a heading with an empty body.
 *      This is the state the flow's first version actually produces for all but one metric,
 *      so it is the default fake rather than an edge case.
 *   3. Every diagnostic state, and the asynchronous behaviour §8.3 specifies — including
 *      a refresh running over figures already on screen, which is a DIFFERENT state from
 *      a first load and was previously covered by no assertion at all. That gap is why
 *      this suite was green while a reviewer watched the button do nothing visible.
 */
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { LandingPage } from "./LandingPage";
import {
  makeAllMetrics,
  makeRepository,
  makeRoundFinance,
  makeRoundStatistics,
  renderWithProviders,
} from "../test/harness";
import { APPLICANT_TYPE_LABELS } from "../dataverse/schema";
import { NOT_SHOWN } from "../domain/format";
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

/** The figures-are-here state: an `ok` response with every metric populated. */
const everything: Partial<TrusteeRepository> = {
  getRoundStatistics: () =>
    Promise.resolve(makeRoundStatistics({ metrics: makeAllMetrics() })),
};

describe("LandingPage — the shell (FR-056, FR-057)", () => {
  it("names the open round in its one h1, once the round is known", async () => {
    renderLanding();
    // The h1 is present from the first paint reading just "Round overview" — the round's
    // name is not known until the direct read lands, and a heading that appears late is
    // worse than one that gains a name. So the assertion is on the RESOLVED heading.
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Round overview");
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Round overview — 2026-Q4",
      );
    });
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("offers a nav to the applications list", async () => {
    renderLanding();
    const nav = screen.getByRole("navigation", { name: /portal sections/i });
    expect(nav).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /open the applications list/i }),
    ).toBeInTheDocument();
  });

  it("offers no round selector of any kind, and says why (FR-057)", async () => {
    renderLanding();
    await screen.findByRole("heading", { level: 1 });
    // FR-057 is confirmed on the reviewer's own words: one round at a time, once a month.
    // A trustee who expects a selector should learn from the screen why there is none.
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    expect(screen.getByText(/there is no round to choose/i)).toBeInTheDocument();
  });

  it("shows the round's calendar from the direct read (FR-058's open date)", async () => {
    renderLanding();
    expect(await screen.findByText("1 Aug 2026")).toBeInTheDocument();
    // A round that has not closed shows no closed row rather than an empty one.
    expect(screen.queryByText("Closed")).not.toBeInTheDocument();
  });

  it("shows the closed date when the round has one", async () => {
    renderLanding({
      getOpenRound: () =>
        Promise.resolve({
          kind: "one",
          round: makeRoundFinance({ roundClosedOn: "2026-08-31T00:00:00Z" }),
        }),
    });
    expect(await screen.findByText("Closed")).toBeInTheDocument();
  });
});

describe("LandingPage — a null metric renders as nothing at all (TAD §3.3 point 3)", () => {
  it("shows the one figure the flow's first version emits, and no section for the rest", async () => {
    renderLanding();
    expect(await screen.findByText("Applications received")).toBeInTheDocument();
    expect(screen.getByText("434")).toBeInTheDocument();

    // Every other metric is null today. None of them gets a heading, an empty table, or a
    // zero — a heading that never has content is worse than no heading.
    for (const heading of [
      "Exceptional circumstances",
      "Type of break",
      "Who applied in this round",
      "Level of need",
    ]) {
      expect(screen.queryByRole("heading", { name: heading })).not.toBeInTheDocument();
    }
    expect(screen.queryByText("Applications per day")).not.toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
    expect(screen.queryByText("0%")).not.toBeInTheDocument();
  });

  it("renders the whole contract once the flow starts emitting it, with no code change", async () => {
    renderLanding(everything);
    for (const heading of [
      "Round progress",
      "Exceptional circumstances",
      "Type of break",
      "Who applied in this round",
      "Level of need",
    ]) {
      expect(await screen.findByRole("heading", { name: heading })).toBeInTheDocument();
    }
    // FR-061's three delivered distributions, each as its own chart.
    for (const chart of ["Gender", "Age range", "Applicant type"]) {
      expect(screen.getByRole("heading", { level: 3, name: chart })).toBeInTheDocument();
    }
    // FR-062's two.
    expect(
      screen.getByRole("heading", { level: 3, name: /wellbeing question 8/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 3, name: /life satisfaction/i }),
    ).toBeInTheDocument();
  });

  it("never renders an ethnicity section, in either state (A-R24)", async () => {
    // FR-061's ethnicity half has no data source and never has. There is no heading for it
    // to be empty under, because a section that is permanently absent should not exist.
    renderLanding(everything);
    await screen.findByRole("heading", { name: "Who applied in this round" });
    expect(screen.queryByText(/ethnic/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/ethnicity/i)).not.toBeInTheDocument();
  });

  it("renders no benchmark, second series or comparison column on any chart", async () => {
    // FR-061's benchmark clause is withdrawn (TAD §0.1 item 4). Every chart is one
    // observed distribution: three columns, and one bar per row.
    const { container } = renderLanding(everything);
    const gender = (await screen.findByRole("heading", { level: 3, name: "Gender" })).closest(
      "section",
    );
    expect(gender?.querySelectorAll("thead th")).toHaveLength(3);
    expect(container.textContent).not.toMatch(/benchmark/i);
    const genderSeries = makeAllMetrics().genderDistribution?.categories ?? [];
    // Scoped to `[role="img"]` — DistributionChart's own accessible bar chart, ADR-029 —
    // rather than every `<rect>` in the section. Fix 3 (2026-08-27) adds a SECOND,
    // `aria-hidden` Recharts bar chart alongside it (RoundStatisticsCharts.tsx), whose
    // SVG draws its own clip-path `<rect>` as an implementation detail unrelated to
    // series count; a blanket `svg rect` count would fail on that incidental element
    // rather than on an actual second series, which this assertion still guards against.
    expect(gender?.querySelectorAll('[role="img"] rect')).toHaveLength(genderSeries.length);
  });

  it("renders FR-060's total row only when the response carried one", async () => {
    renderLanding(everything);
    expect(await screen.findByRole("rowheader", { name: "All types" })).toBeInTheDocument();

    const metrics = makeAllMetrics();
    const profile = metrics.breakTypeProfile;
    if (profile === null) throw new Error("expected a break-type profile");
    renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(
          makeRoundStatistics({
            metrics: { ...metrics, breakTypeProfile: { ...profile, total: null } },
          }),
        ),
    });
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { name: "Type of break" })).toHaveLength(2);
    });
  });

  it("renders FR-062's three proportions as absent while OQ-039 is unanswered", async () => {
    renderLanding(everything);
    await screen.findByRole("heading", { name: "Level of need" });
    // The three thresholds are unstated (OQ-039, A-R29), so the flow emits null and the
    // screen offers nothing — not a zero, and not a control to set a threshold.
    expect(screen.queryByText(/high-hours care/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/unable to take a break/i)).not.toBeInTheDocument();
  });

  it("renders the three proportions with their own denominators once they arrive", async () => {
    renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(
          makeRoundStatistics({
            metrics: {
              ...makeAllMetrics(),
              highHoursCareProportion: { population: 400, count: 90, percentage: 22.5 },
            },
          }),
        ),
    });
    expect(await screen.findByText(/carers providing high-hours care/i)).toBeInTheDocument();
    expect(screen.getByText("22.5% (90 of 400)")).toBeInTheDocument();
  });
});

describe("LandingPage — the four ADR-039 money measures, {value, population} (Revision 6, TAD §6.3.5)", () => {
  it("shows a money measure's own population beside its value, in the same cell", async () => {
    // The fixture's row 1 deliberately gives `averageCost` a population (298) that DIFFERS
    // from the row's own `count` (300) — TAD §3.3 property 8, the exact case a reader's
    // "the denominator is the count beside it" assumption gets wrong.
    renderLanding(everything);
    await screen.findByRole("heading", { name: "Type of break" });
    const cell = screen.getByText(/£1,500\.00/);
    expect(cell.textContent).toContain("298");
    expect(cell.textContent).not.toBe("£1,500.00");
  });

  it("renders a below-threshold row as count-present, money-absent — never zero, never blank", async () => {
    // The fixture's row 2 ("Day trips or outings") is the below-k shape TAD §3.3 shows
    // literally: count real, all three money measures withheld.
    renderLanding(everything);
    await screen.findByRole("heading", { name: "Type of break" });
    const row = screen.getByRole("rowheader", { name: "Day trips or outings" }).closest("tr");
    if (row === null) throw new Error("expected the break-type row to have a parent <tr>");
    const cells = Array.from(row.querySelectorAll("td"));
    expect(cells[0]?.textContent).toBe("3");
    expect(cells[1]?.textContent).toBe(NOT_SHOWN);
    expect(cells[2]?.textContent).toBe(NOT_SHOWN);
    expect(cells[3]?.textContent).toBe(NOT_SHOWN);
    for (const cell of cells) {
      expect(cell.textContent).not.toBe("£0.00");
      expect(cell.textContent).not.toBe("0%");
      expect(cell.textContent).not.toBe("");
    }
  });

  it("explains the withholding in the break-type table's own caption, without naming the threshold", async () => {
    // `k` lives in `rev_setting`, is read only by the flow, and never travels in the
    // response — so this screen has no number to name (TAD §6.3.5).
    renderLanding(everything);
    const section = (await screen.findByRole("heading", { name: "Type of break" })).closest(
      "section",
    );
    const caption = section?.querySelector("caption");
    expect(caption?.textContent).toMatch(/shown only where enough applications/i);
    expect(caption?.textContent).not.toMatch(/\b5\b/);
  });

  it("shows the exceptional-funding average with its own population, and explains the withholding beside it", async () => {
    renderLanding(everything);
    await screen.findByText("Average exceptional funding requested");
    const value = screen.getByText(/£780\.00/);
    expect(value.textContent).toContain("39");
    expect(
      screen.getByText(/average exceptional funding requested is shown only where/i),
    ).toBeInTheDocument();
  });

  it("renders the exceptional-funding average as withheld, not as zero, when its own measure is null", async () => {
    renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(
          makeRoundStatistics({
            metrics: {
              ...makeAllMetrics(),
              exceptionalFundingSummary: {
                population: 434,
                anyCount: 4,
                anyPercentage: 0.9,
                averageAmountRequested: null,
              },
            },
          }),
        ),
    });
    const term = await screen.findByText("Average exceptional funding requested");
    const dd = term.closest("div")?.querySelector("dd");
    expect(dd?.textContent).toBe(NOT_SHOWN);
    expect(screen.queryByText("£0.00")).not.toBeInTheDocument();
  });
});

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

describe("LandingPage — §0.10.2 (Revision 7, IMP-0510): the 'figures' subheading", () => {
  it("shows a plain h2 above the statistics, only once the figures are available", async () => {
    renderLanding();
    const heading = await screen.findByRole("heading", {
      level: 2,
      name: "Figures of this round",
    });
    expect(heading).toBeInTheDocument();
    // It sits ABOVE RoundStatistics's own freshness line, which is the first thing
    // RoundStatistics itself renders — so the heading must precede that text in the DOM.
    const freshness = screen.getByText(/round figures computed on/i);
    expect(
      heading.compareDocumentPosition(freshness) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("does not render the heading while the figures are loading or diagnostic", async () => {
    renderLanding({
      getRoundStatistics: () => new Promise(() => {}), // never resolves — stays "loading"
    });
    await screen.findByText(/computing the round's figures/i);
    expect(
      screen.queryByRole("heading", { level: 2, name: "Figures of this round" }),
    ).not.toBeInTheDocument();
  });

  it("does not render the heading when the flow reports a diagnostic state", async () => {
    renderLanding({
      getRoundStatistics: () => Promise.reject(new Error("The flow is not bound to this app.")),
    });
    // The diagnostic state renders through `ds/Notice` (role="note"), not a heading element.
    await screen.findByText("Round figures are unavailable");
    expect(
      screen.queryByRole("heading", { level: 2, name: "Figures of this round" }),
    ).not.toBeInTheDocument();
  });
});

describe("LandingPage — FR-063, read directly from rev_roundfinance", () => {
  it("shows all eight measures, labelling the two that are charity-wide", async () => {
    renderLanding();
    await screen.findByRole("heading", { name: /the round's financial position/i });
    for (const label of [
      "Committed or spent to date",
      "People supported",
      "Individuals supported",
      "People reached by group grants",
      "Suggested maximum spend for this round",
      "Monthly disbursement",
    ]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
    // Amendment A-03 Finding 3: these two describe the charity's overall position, not this
    // round's budget. A trustee reading "capacity" as the round's budget reads the wrong
    // number.
    expect(screen.getByText("Grant-giving capacity (charity-wide)")).toBeInTheDocument();
    expect(screen.getByText("Remaining legacy fund (charity-wide)")).toBeInTheDocument();
  });

  it("renders a measure nobody has entered as words, never as zero", async () => {
    renderLanding({
      getOpenRound: () =>
        Promise.resolve({
          kind: "one",
          round: makeRoundFinance({ remainingLegacyFund: null, peopleSupported: null }),
        }),
    });
    await screen.findByRole("heading", { name: /the round's financial position/i });
    // Unlike a null flow metric, this row STAYS: a person has left a field empty in a row
    // that exists, a trustee needs to see that, and somebody can act on it. "£0" would say
    // the charity has no legacy fund left.
    expect(screen.getAllByText("Not recorded").length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText("£0.00")).not.toBeInTheDocument();
  });
});

describe("LandingPage — asynchronous states (TAD §8.3)", () => {
  it("announces the figures as loading through a live region, not a silent skeleton", async () => {
    renderLanding();
    // `role="status"` with `aria-busy` — a visual spinner alone announces nothing to a
    // screen-reader trustee.
    const region = screen.getByRole("status");
    expect(region).toHaveAttribute("aria-busy", "true");
    expect(region.textContent).toContain("Loading the round's figures.");
    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "false");
    });
    // Revision 5 (TAD §8.3): the arrival announcement states the STAMP, not the action.
    expect(screen.getByRole("status").textContent).toContain("Figures are current as at");
  });

  it("announces the stamp and never claims a refresh happened (TAD §8.3, ADR-038)", async () => {
    // Inside the freshness window `fetchRoundStatistics` returns the document already on the
    // result row without writing or triggering anything, so "Figures refreshed" would be
    // FALSE in the common case — and a trustee acting on it would believe a stale-but-valid
    // figure had just been recomputed. The one wording this screen must not use is any
    // phrase implying the button always causes work.
    renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(makeRoundStatistics({ computedOn: "2026-08-25T13:05:11Z" })),
    });
    await screen.findByText(/round figures computed on/i);

    const announced = screen.getByRole("status").textContent ?? "";
    // The stamp itself, rendered through the same `formatDateTime` as the visible freshness
    // line and the printed pack, so the two can never disagree about when.
    expect(announced).toContain("Figures are current as at 25 Aug 2026, 13:05 UTC.");
    expect(announced).not.toMatch(/refreshed/i);
    expect(announced).not.toMatch(/recalculated/i);
    expect(announced).not.toMatch(/updated/i);

    // And it survives pressing the button, which is the case that matters: the announcement
    // is identical whether the press caused a computation or found one already fresh.
    await userEvent.click(screen.getByRole("button", { name: "Refresh figures" }));
    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "false");
    });
    expect(screen.getByRole("status").textContent).toContain("Figures are current as at");
    expect(screen.getByRole("status").textContent).not.toMatch(/refreshed/i);
  });

  it("renders pending as a note, not an alert — a running computation must not interrupt", async () => {
    // TAD §8.3's Revision 5 bullet: "`pending` is a diagnostic state, not an error state" —
    // it joins the other four rendered through `StateMessage` with `role="note"`, because a
    // computation still running is not something to interrupt a screen-reader trustee about.
    // `fetchRoundStatistics` raises this status itself when its poll bound is reached.
    renderLanding({
      getRoundStatistics: () => Promise.resolve(makeRoundStatistics({ status: "pending" })),
    });
    const note = await screen.findByRole("note");
    expect(note).toHaveTextContent("Figures are being recalculated");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    // No figures at all beside it (TAD §3.3 point 4) — `pending` is not a partial screen.
    expect(screen.queryByText(/round figures computed on/i)).not.toBeInTheDocument();
    // And the wording does not tell a trustee who never pressed anything that they asked:
    // under ADR-038 a stale mount triggers a recomputation just as often as the button does.
    expect(note.textContent ?? "").not.toMatch(/a refresh was requested/i);
  });

  it("offers a Refresh figures button whose accessible name never changes", async () => {
    let statisticsCalls = 0;
    let roundCalls = 0;
    renderLanding({
      getOpenRound: () => {
        roundCalls += 1;
        return Promise.resolve({ kind: "one", round: makeRoundFinance() });
      },
      getRoundStatistics: () => {
        statisticsCalls += 1;
        return Promise.resolve(makeRoundStatistics());
      },
    });
    await screen.findByText(/round figures computed on/i);
    expect(roundCalls).toBe(1);
    expect(statisticsCalls).toBe(1);

    await userEvent.click(screen.getByRole("button", { name: "Refresh figures" }));
    await waitFor(() => {
      expect(statisticsCalls).toBe(2);
    });
    // Both halves are re-read, because reconciliation compares them and refreshing one
    // would compare a new response against an old row.
    expect(roundCalls).toBe(2);
    // Same name after the refresh: a control renamed to "Refreshing…" is a different
    // control to a screen reader every time it is used.
    expect(screen.getByRole("button", { name: "Refresh figures" })).toBeInTheDocument();
  });

  it("keeps the refresh control outside the live region", async () => {
    renderLanding();
    await screen.findByText(/round figures computed on/i);
    const button = screen.getByRole("button", { name: "Refresh figures" });
    expect(screen.getByRole("status").contains(button)).toBe(false);
  });
});

describe("LandingPage — diagnostic states (TAD §5.3)", () => {
  it("says no round is open, and does not call the round ambiguous", async () => {
    renderLanding({ getOpenRound: () => Promise.resolve({ kind: "none" }) });
    expect(await screen.findByText("No round is open")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /financial position/i })).not.toBeInTheDocument();
  });

  it("says the round is ambiguous for two open rows rather than picking one", async () => {
    renderLanding({ getOpenRound: () => Promise.resolve({ kind: "ambiguous", count: 2 }) });
    expect(await screen.findByText("More than one round is open")).toBeInTheDocument();
    expect(screen.getByText(/2 grant rounds are marked as open/i)).toBeInTheDocument();
  });

  it("reports each named flow status with its own wording, and no figures", async () => {
    const cases: [string, RegExp][] = [
      ["no-open-round", /found no grant round marked as open/i],
      ["ambiguous-round", /found more than one grant round/i],
      ["truncated", /more applications than the statistics service will summarise/i],
      ["threshold-unset", /missing a threshold it needs/i],
    ];
    for (const [status, wording] of cases) {
      const { unmount } = renderLanding({
        getRoundStatistics: () => Promise.resolve(makeRoundStatistics({ status })),
      });
      expect(await screen.findByText(wording)).toBeInTheDocument();
      expect(screen.queryByText("Applications received")).not.toBeInTheDocument();
      unmount();
    }
  });

  it("handles a status this build has never seen, including one from a later flow version", async () => {
    renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(makeRoundStatistics({ status: "flow-error", metrics: makeAllMetrics() })),
    });
    expect(await screen.findByText("Round figures are unavailable")).toBeInTheDocument();
    expect(screen.getByText(/does not recognise \("flow-error"\)/i)).toBeInTheDocument();
    // "No figures, no zeros" — even though this response carried a full metrics object.
    expect(screen.queryByRole("heading", { name: "Who applied in this round" })).not.toBeInTheDocument();
    expect(screen.queryByText("Applications received")).not.toBeInTheDocument();
  });

  it("handles a call that rejects rather than returning a status at all", async () => {
    renderLanding({
      getRoundStatistics: () => Promise.reject(new Error("The flow is not bound to this app.")),
    });
    expect(await screen.findByText(/the flow is not bound to this app/i)).toBeInTheDocument();
    // The finance half is unaffected: the two reads degrade independently.
    expect(screen.getByRole("heading", { name: /financial position/i })).toBeInTheDocument();
  });

  it("shows neither half when the two round keys disagree", async () => {
    renderLanding({
      getRoundStatistics: () => Promise.resolve(makeRoundStatistics({ roundKey: "2026-Q3" })),
    });
    const notes = await screen.findAllByText(/the round changed while these figures/i);
    expect(notes).toHaveLength(2);
    expect(screen.queryByRole("heading", { name: /financial position/i })).not.toBeInTheDocument();
    expect(screen.queryByText("Applications received")).not.toBeInTheDocument();
  });

  it("renders every diagnostic as a note, never as an alert", async () => {
    renderLanding({
      getOpenRound: () => Promise.resolve({ kind: "none" }),
      getRoundStatistics: () => Promise.resolve(makeRoundStatistics({ status: "truncated" })),
    });
    await screen.findByText("No round is open");
    expect(screen.getAllByRole("note")).toHaveLength(2);
    // `role="alert"` would interrupt a screen-reader trustee on every navigation to tell
    // them something entirely expected (Panel.tsx's own reasoning, TAD §8.3).
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});

describe("LandingPage — Fix 3, the charts and KPI tiles alongside the tables (2026-08-27)", () => {
  it("draws a chart beside every FR-061 distribution, without disturbing its table", async () => {
    renderLanding(everything);
    const gender = (await screen.findByRole("heading", { level: 3, name: "Gender" })).closest(
      "section",
    );
    // The new visual sits inside the SAME section as the existing accessible table —
    // one heading, two renderings of the same data (this file's DistributionChart
    // `visual` slot). It is `aria-hidden`, so it never competes with the table for a
    // screen-reader trustee's attention.
    const decorative = gender?.querySelector('[aria-hidden="true"][data-print="chart"]');
    expect(decorative).not.toBeNull();
    expect(gender?.querySelector("table")).not.toBeNull();
  });

  it("draws applicant type as a pie with a legend naming all three categories", async () => {
    renderLanding(everything);
    const applicantType = (
      await screen.findByRole("heading", { level: 3, name: "Applicant type" })
    ).closest("section");
    const legend = applicantType?.querySelector("ul");
    expect(legend).not.toBeNull();
    for (const label of Object.values(APPLICANT_TYPE_LABELS)) {
      expect(legend?.textContent).toContain(label);
    }
  });

  it("shows a combined wellbeing comparison chart above the per-question breakdowns", async () => {
    renderLanding(everything);
    const heading = await screen.findByRole("heading", {
      level: 3,
      name: "Wellbeing, last year (all questions)",
    });
    expect(heading).toBeInTheDocument();
    // Its own heading, distinct from any per-question one — no ambiguous `getByRole`
    // match against "Wellbeing question 8, last year" below it.
    expect(
      screen.getByRole("heading", { level: 3, name: /wellbeing question 8/i }),
    ).toBeInTheDocument();
  });

  it("shows no wellbeing comparison chart when the flow sent no wellbeing questions", async () => {
    // The default fake (TAD §3.3's first-version response): every FR-061/FR-062 metric
    // is null, including `wellbeingLastYear`. No heading for a chart with nothing behind
    // it — the same absence rule every other figure on this screen follows.
    renderLanding();
    await screen.findByRole("heading", { level: 1 });
    expect(
      screen.queryByRole("heading", { name: /wellbeing, last year \(all questions\)/i }),
    ).not.toBeInTheDocument();
  });

  it("renders the Round 4 KPI figures as real text, not as an image with nothing behind it", async () => {
    // StatTileRow (components/Panel.tsx) is a styling change over `Definitions`, not an
    // accessibility one: the same label appears with the same formatted value, so a
    // screen reader announces exactly what it announced before this pass.
    renderLanding();
    await screen.findByText("Applications received");
    expect(screen.getByText("434").closest("dd")).not.toBeNull();

    renderLanding();
    await screen.findByRole("heading", { name: /the round's financial position/i });
    expect(screen.getByText("Committed or spent to date").closest("dt")).not.toBeNull();
  });

  it("never draws a gender/age chart with a second bar per category (the withdrawn benchmark)", async () => {
    // Reiterated at the RoundStatisticsCharts level, not just DistributionChart's own
    // table: the new Recharts visual must not quietly reintroduce the withdrawn
    // FR-061 benchmark comparison either.
    renderLanding(everything);
    const age = (await screen.findByRole("heading", { level: 3, name: "Age range" })).closest(
      "section",
    );
    const ageSeries = makeAllMetrics().ageRangeDistribution?.categories ?? [];
    // One bar per category in the ACCESSIBLE chart (role="img") — Recharts' own
    // decorative figure is asserted separately, in isolation, in
    // RoundStatisticsCharts.test.tsx.
    expect(age?.querySelectorAll('[role="img"] rect')).toHaveLength(ageSeries.length);
  });
});

describe("LandingPage — what it must never read", () => {
  it("reads no application or applicant row, in any state", async () => {
    // The mechanism the whole design rests on (TAD §1.1, §5.4, §6.3). Computing any figure
    // client-side from rows the trustee's own session can see would defeat the
    // obstacle-A/obstacle-B reasoning silently: the gender distribution would be empty, and
    // FR-058's received count would mean putting out-of-remit rows on the wire.
    let applicationReads = 0;
    renderLanding({
      ...everything,
      listApplicationsForReview: () => {
        applicationReads += 1;
        return Promise.resolve([]);
      },
      getApplication: () => {
        applicationReads += 1;
        return Promise.resolve(null);
      },
      getReviewForApplication: () => {
        applicationReads += 1;
        return Promise.resolve(null);
      },
    });
    await screen.findByRole("heading", { name: "Who applied in this round" });
    expect(applicationReads).toBe(0);
  });

  it("offers no suppression or grouping control on any chart (NFR-027 withdrawn)", async () => {
    // TAD §6.3's final paragraph: the reviewer accepted the low-count disclosure risk with
    // no control, twice. Every row carries its denominator; that is the whole of it.
    const { container } = renderLanding({
      getRoundStatistics: () =>
        Promise.resolve(
          makeRoundStatistics({
            metrics: {
              ...makeAllMetrics(),
              genderDistribution: {
                population: 434,
                categories: [
                  { value: 1, count: 428, percentage: 98.6 },
                  { value: 3, count: 6, percentage: 1.4 },
                ],
              },
            },
          }),
        ),
    });
    await screen.findByRole("heading", { level: 3, name: "Gender" });
    // The low-count row is shown as it is, with its denominator beside it.
    expect(screen.getByRole("rowheader", { name: "Non-binary" })).toBeInTheDocument();
    expect(container.textContent).not.toMatch(/suppress|combined|other\/small/i);
  });
});
