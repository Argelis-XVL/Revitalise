/**
 * The shell — landmarks, the signed-in line, and navigation across the three screens.
 *
 * FR-056 changed the entry state: the app opens on the LANDING screen, not on the case
 * list. Every test below that used to start on the list now navigates there first, which
 * is the assertion FR-056 actually needs — "trustees have a clear starting point instead of
 * landing directly inside case data" is only true if the first paint is not the case data.
 */
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { App } from "./App";
import { makeRepository, makeUser, renderWithProviders } from "./test/harness";

/** FR-056's first hop: landing -> list. */
async function openTheList(): Promise<void> {
  await userEvent.click(
    await screen.findByRole("button", { name: /open the applications list/i }),
  );
  await waitFor(() => {
    expect(screen.getByRole("table")).toBeInTheDocument();
  });
}

describe("App", () => {
  it("opens on the landing screen, not inside case data (FR-056)", async () => {
    renderWithProviders(<App />, makeRepository());
    expect(
      await screen.findByRole("heading", { level: 1, name: /round overview/i }),
    ).toBeInTheDocument();
    // The point of FR-056: no case list on the first paint.
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("provides a skip link and a main landmark for it to target", async () => {
    renderWithProviders(<App />, makeRepository());
    const skip = screen.getByRole("link", { name: /skip to the applications/i });
    expect(skip).toHaveAttribute("href", "#main");
    expect(document.querySelector("main")?.id).toBe("main");
    await openTheList();
  });

  it("shows one h1 on the landing screen and one on the list", async () => {
    renderWithProviders(<App />, makeRepository());
    await waitFor(() => {
      expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    });
    await openTheList();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Applications under review",
    );
  });

  it("brands every view with the charity's logo, named rather than decorative", async () => {
    // NFR-026. The logo lives in the shell header, so one placement covers all three views;
    // `alt` is the organisation's name because this identifies the charity whose money the
    // round distributes, which is content, not decoration (WCAG 1.1.1). An `alt=""` here
    // would leave a screen-reader user with no idea whose portal they are in.
    renderWithProviders(<App />, makeRepository());
    const logo = screen.getByRole("img", { name: /revitalise/i });
    expect(logo).toBeInTheDocument();
    await openTheList();
    expect(screen.getByRole("img", { name: /revitalise/i })).toBeInTheDocument();
  });

  it("names the signed-in trustee", async () => {
    renderWithProviders(<App />, makeRepository());
    expect(await screen.findByText(/signed in as kevin trustee/i)).toBeInTheDocument();
  });

  it("says so when the host did not give a name", async () => {
    renderWithProviders(
      <App />,
      makeRepository({ getCurrentUser: () => Promise.resolve(makeUser({ fullName: null })) }),
    );
    expect(await screen.findByText(/your name was not available/i)).toBeInTheDocument();
  });

  it("explains that cases are still readable when the trustee record is unconfirmed", async () => {
    renderWithProviders(
      <App />,
      makeRepository({
        getCurrentUser: () =>
          Promise.resolve(
            makeUser({ systemUserId: null, unresolvedReason: "No user record matches you." }),
          ),
      }),
    );
    // waitFor, not findByRole: the note is present from the first paint carrying an
    // interim "still working out who you are" reason, so finding a note proves nothing.
    // The assertion is on the RESOLVED reason.
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent("No user record matches you.");
    });
    const note = screen.getByRole("note");
    expect(note).toHaveTextContent(/read cases, but not record a verdict/i);
    // The point of the message: it must not read as a lockout.
    expect(note).toHaveTextContent(/still readable/i);
  });

  it("reports a failed identity query as a reason rather than as a blank line", async () => {
    renderWithProviders(
      <App />,
      makeRepository({ getCurrentUser: () => Promise.reject(new Error("Identity query broke.")) }),
    );
    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent("Identity query broke.");
    });
  });

  it("walks the whole FR-056 chain: landing to list to case and back again", async () => {
    renderWithProviders(<App />, makeRepository());
    await openTheList();

    await userEvent.click(
      screen.getByRole("button", { name: /REV-2026-001, open the full case/i }),
    );
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Application REV-2026-001",
      );
    });
    // The list's h1 is replaced, not duplicated — one h1 per view (WCAG 2.4.6).
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);

    // Revision 11 (2026-09-02, wbs:6.8), reviewer item 7 — the route back is now the nav bar's
    // "Applications list" tab and nothing else. The detail screen's own "Back to the list"
    // button is removed as redundant with it, which REVERSES the decision this file's Revision 7
    // section records (`ApplicationDetailPage`'s own Revision 11 header carries the reversal).
    // This step is what proves the removal left no dead end behind: the chain still walks back.
    expect(screen.queryByRole("button", { name: /back to the list/i })).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: /applications list/i }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
        "Applications under review",
      );
    });

    // And back up to the landing screen — ADR-040's persistent nav bar, which replaced the
    // list view's old contextual "Back to the round overview" button. Without a way back the
    // list would be a dead end and the round's figures would be unreachable without reloading.
    await userEvent.click(
      screen.getByRole("button", { name: "Round overview" }),
    );
    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Round overview");
    });
  });

  describe("ADR-040 — the persistent view-switching nav bar (Revision 7, IMP-0510)", () => {
    it("names the two always-reachable screens, on every view, in a landmark of its own", async () => {
      renderWithProviders(<App />, makeRepository());
      const nav = await screen.findByRole("navigation", { name: /screen navigation/i });
      expect(
        within(nav).getByRole("button", { name: "Round overview" }),
      ).toBeInTheDocument();
      expect(
        within(nav).getByRole("button", { name: /Applications list/i }),
      ).toBeInTheDocument();
      // The third control is NOT here on the landing view any more — reviewer item 5,
      // Revision 9. Its own test below carries the reasoning; this one records that the bar
      // no longer names every screen at all times, which is what ADR-040 originally decided.
    });

    it("marks the current view with aria-current, and only the current view", async () => {
      renderWithProviders(<App />, makeRepository());
      const nav = await screen.findByRole("navigation", { name: /screen navigation/i });
      expect(within(nav).getByRole("button", { name: "Round overview" })).toHaveAttribute(
        "aria-current",
        "page",
      );
      expect(
        within(nav).getByRole("button", { name: /Applications list/i }),
      ).not.toHaveAttribute("aria-current");

      await openTheList();
      expect(within(nav).getByRole("button", { name: /Applications list/i })).toHaveAttribute(
        "aria-current",
        "page",
      );
      expect(within(nav).getByRole("button", { name: "Round overview" })).not.toHaveAttribute(
        "aria-current",
      );
    });

    /**
     * REVIEWER ITEM 5 (Revision 9, 2026-09-01, wbs:6.9) — THIS TEST REPLACES THE A-R55 ONE IT
     * IS WRITTEN OVER, AND THE REPLACEMENT IS THE RECORD OF A REVERSED DECISION.
     *
     * What was asserted here until Revision 9: "Application detail" is present on every view,
     * carries `aria-disabled="true"` until a case is open, and shows a visible "Open a case
     * first" caption while it is. That was ADR-040 / A-R55's designed behaviour.
     *
     * The reviewer saw it on the live DEV portal and asked for the control to be ABSENT from
     * the bar on the landing and list screens instead. `App.tsx`'s Revision 9 header states
     * what that gives up (a persistent bar; a constant tab-stop count) and why no accessible
     * behaviour goes with it (the control never navigated, and a control that is not rendered
     * needs no explanation of why it does nothing).
     *
     * The assertions below are therefore the INVERSE of the ones they replace, deliberately —
     * a reversed decision needs a test that fails if the old behaviour comes back, not a
     * deleted test.
     */
    it("shows Application detail ONLY on the detail view (reviewer item 5, reverses A-R55)", async () => {
      renderWithProviders(<App />, makeRepository());
      const nav = await screen.findByRole("navigation", { name: /screen navigation/i });
      // Landing: absent entirely. Not disabled, not captioned — not rendered.
      expect(
        within(nav).queryByRole("button", { name: /Application detail/i }),
      ).not.toBeInTheDocument();
      expect(within(nav).queryByText(/open a case first/i)).not.toBeInTheDocument();

      // List: still absent. The reviewer named both screens the case is not open on.
      await openTheList();
      expect(
        within(nav).queryByRole("button", { name: /Application detail/i }),
      ).not.toBeInTheDocument();

      await userEvent.click(
        screen.getByRole("button", { name: /REV-2026-001, open the full case/i }),
      );
      // Detail: present, and marked as the current view — `aria-current` is what states that
      // to assistive technology, so the fill colour is never the only carrier (WCAG 1.4.1).
      await waitFor(() => {
        expect(
          within(nav).getByRole("button", { name: /Application detail/i }),
        ).toHaveAttribute("aria-current", "page");
      });
      expect(
        within(nav).getByRole("button", { name: /Application detail/i }),
      ).not.toHaveAttribute("aria-disabled");
    });

    it("moves laterally from the detail screen to the applications list", async () => {
      renderWithProviders(<App />, makeRepository());
      await openTheList();
      await userEvent.click(
        screen.getByRole("button", { name: /REV-2026-001, open the full case/i }),
      );
      await screen.findByRole("heading", { level: 1, name: /Application REV-2026-001/i });

      const nav = screen.getByRole("navigation", { name: /screen navigation/i });
      await userEvent.click(within(nav).getByRole("button", { name: /Applications list/i }));
      await waitFor(() => {
        expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
          "Applications under review",
        );
      });
    });
  });

  it("sets a distinct document title per view", async () => {
    renderWithProviders(<App />, makeRepository());
    // The landing title names the round, so two rounds are distinguishable in a browser
    // history or a printed header (WCAG 2.4.2).
    await waitFor(() => {
      expect(document.title).toBe("Round overview — 2026-Q4 — Trustee Review Portal");
    });
    await openTheList();
    await waitFor(() => {
      expect(document.title).toBe("Applications under review — Trustee Review Portal");
    });
    await userEvent.click(
      await screen.findByRole("button", { name: /REV-2026-001, open the full case/i }),
    );
    await waitFor(() => {
      expect(document.title).toBe("Application REV-2026-001 — Trustee Review Portal");
    });
  });
});
