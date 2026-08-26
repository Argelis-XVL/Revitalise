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
 *   3. Every diagnostic state, and the asynchronous behaviour §8.3 specifies.
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
    expect(gender?.querySelectorAll("svg rect")).toHaveLength(genderSeries.length);
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
    expect(screen.getByRole("status").textContent).toContain(
      "The round's figures have loaded.",
    );
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
