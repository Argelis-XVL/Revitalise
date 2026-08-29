/**
 * The landing screen — FR-056 (the navigation shell) and FR-057..FR-063 (its content).
 * WBS 6.1 and 6.9.
 *
 * ## What it does, in three steps — TAD §5.4
 *
 *   1. Reads `rev_roundfinance` with `rev_isopen eq true`, `top 2`, on the trustee's own
 *      privileges. One row is expected; zero and two-or-more are diagnostic states of
 *      their own, evaluated here, client-side, before the flow is called at all.
 *   2. Reads the round statistics — TAD §5.4 step 2 as superseded by §5.3.1. **Nothing is
 *      invoked**: `roundStatistics.ts` reads `rev_roundstatisticsresult`, and only if that
 *      document is older than its own `staleAfterSeconds` does it write `rev_triggeredon` on
 *      `rev_roundstatisticsrequest` and poll. No arguments and no steerable input, because
 *      the flow reads nothing from its trigger body (§1.5 point 4).
 *   3. Reconciles the two round keys. On a mismatch neither half is shown, because a
 *      financial position from one round beside application figures from another would
 *      look entirely normal and be wrong. **Revision 5 makes this matter MORE, not less:**
 *      with one shared result row the document a trustee reads may have been computed for
 *      someone else's ask, so this reconciliation is the only thing that catches a finance
 *      row that changed in between.
 *
 * All three decisions live in `domain/landing.ts` and are unit-tested there. This file
 * renders the decision and does not make it.
 *
 * ## What this screen must never do
 *
 * **It reads no application or applicant row.** Not for a count, not for a percentage, not
 * as a "helpful" fallback when the flow is unavailable. Every FR-058..FR-062 figure comes
 * from the flow response and there is no other path to one in this component — see
 * `dataverse/roundStatistics.ts`'s header for the three obstacles that make client-side
 * computation either impossible (the gender distribution), a disclosure (FR-058's received
 * population), or a screen whose tiles have different denominators. Getting that backwards
 * would silently defeat the reasoning TAD §1.1 and §6.3 rest on, which is a correctness
 * bug and not a matter of taste.
 *
 * **It offers no round selector**, ever (FR-057, confirmed: one round at a time, once a
 * month). The screen shows whichever round `rev_isopen` names.
 *
 * ## Accessibility — TAD §8.3
 *
 * One `<h1>`; a `<nav>` to the list; `<h2>` per section and `<h3>` per chart, so the
 * hierarchy is flat and correct beneath the heading; the shell's existing skip link and
 * `<main id="main">` untouched; a unique page title through the existing `usePageTitle`.
 * The figures arrive after the page does, so the statistics region is a live region with
 * `aria-busy`, and the **Refresh figures** control is a real `<button>` whose accessible
 * name does not change between states.
 *
 * A refresh is reported in BOTH channels, because the two states of this screen are not
 * the same state: the panel Spinners cover a first load, and an inline Spinner beside the
 * button covers a refresh over figures already on screen — where React Query reports
 * `isFetching` and not `isPending`, so nothing keyed on the panel's own phase fires at
 * all. `liveStatus` carries the same distinction in text. Diagnostics go through
 * `StateMessage`, which is
 * `role="note"` and not `role="alert"` — these are the designed states of the screen and
 * an alert would interrupt a screen-reader trustee to tell them something expected.
 *
 * ## Revision 4 — the buttons are the design system's; Fluent's `Spinner` stays
 *
 * TAD §2.1.4. Both controls become `ds/Button` — **Open the applications list** is
 * `primary` and **Refresh figures** is `secondary`, which is what the supplied
 * `RoundOverview.jsx:11-12` mockup shows and what the two controls are: one is the screen's
 * purpose, the other is a re-read of what is already there. Neither carries
 * `styles.tallTarget` any more, because every `ds/Button` size declares `min-height: 44px`
 * itself (WCAG 2.5.5).
 *
 * **Both `Spinner`s stay Fluent's**, in all three places: the design system ships no spinner,
 * and a spinner's value is the `role`/`aria-live` wiring and the label placement rather than
 * the animation. Nothing else about this screen's asynchronous contract moved — the live
 * region, `aria-busy`, the four-state `liveStatus` and the never-renamed **Refresh figures**
 * accessible name are all exactly as they were.
 */
import { Spinner } from "@fluentui/react-components";
import { Button } from "../components/ds";
import { RoundFinancePanel } from "../components/RoundFinancePanel";
import { RoundStatistics } from "../components/RoundStatistics";
import { Definitions, Panel, StateMessage } from "../components/Panel";
import { formatDate, formatDateTime } from "../domain/format";
import { deriveLandingView } from "../domain/landing";
import type { QueryPhase } from "../domain/landing";
import { useOpenRound, useRoundStatistics } from "../hooks/queries";
import { usePageTitle } from "../hooks/usePageTitle";
import styles from "../styles/app.module.css";

/**
 * React Query state -> the phase `deriveLandingView` reasons about.
 *
 * `isError` is checked BEFORE `isPending`, which matters on a failed refresh: React Query
 * keeps the previous data, and showing yesterday's figures under a stamp nobody re-read
 * would be a partial screen. TAD §5.3 is explicit that a failed call means one diagnostic
 * panel and no figures.
 */
function phaseOf(query: { isPending: boolean; isError: boolean }): QueryPhase {
  if (query.isError) return "error";
  if (query.isPending) return "loading";
  return "loaded";
}

export function LandingPage({ onOpenList }: { onOpenList: () => void }) {
  const round = useOpenRound();
  const statistics = useRoundStatistics();

  // Not memoised, on purpose. `deriveLandingView` is a pure switch over two small objects
  // and it allocates the diagnostic strings it chooses; memoising it would mean listing
  // both whole query objects as dependencies, which changes identity on every render
  // anyway. `ApplicationsListPage` memoises because it sorts and filters a 500-row list;
  // there is nothing of that shape here.
  const view = deriveLandingView(
    {
      phase: phaseOf(round),
      ...(round.data === undefined ? {} : { result: round.data }),
      ...(round.error === null ? {} : { errorMessage: round.error.message }),
    },
    {
      phase: phaseOf(statistics),
      ...(statistics.data === undefined ? {} : { response: statistics.data }),
      ...(statistics.error === null ? {} : { errorMessage: statistics.error.message }),
    },
  );

  const title =
    view.roundName === null ? "Round overview" : `Round overview — ${view.roundName}`;
  usePageTitle(title);

  const busy = statistics.isFetching;

  /**
   * A refresh running over content that is ALREADY on screen.
   *
   * This is the state neither full-panel Spinner below covers. Both render only while
   * their own half has nothing to show — `kind === "loading"`, which is React Query's
   * `isPending`, and `isPending` is false for the rest of the session once a first load
   * has succeeded. **Refresh figures** therefore sets `isFetching` and nothing else, and
   * before this the screen went completely silent for the whole round trip.
   *
   * Keyed on `kind !== "loading"` rather than on `!isPending` so the invariant is the one
   * that actually matters: this indicator appears exactly when the corresponding panel
   * Spinner does not, so one read never draws two spinners. It consequently also covers a
   * refresh over a DIAGNOSTIC panel — a retry after a failed call, which was equally
   * silent and is the state the **Refresh figures** wording in every §5.3 diagnostic
   * invites a trustee to act on.
   */
  const refreshing =
    (round.isFetching && view.finance.kind !== "loading") ||
    (statistics.isFetching && view.statistics.kind !== "loading");

  /**
   * What the live region says. Four states, not three.
   *
   * `view.statistics.kind` is a statement about what is ON SCREEN, so during a re-fetch
   * over existing figures it stays `"figures"` and this region went on asserting "have
   * loaded" for the whole round trip: true about the figures being displayed, false about
   * whether they are being replaced, which is the half a trustee pressed the button to
   * learn.
   *
   * Two deliberate choices. `"loading"` is tested FIRST, so a genuine first load still
   * says "Loading" rather than "Refreshing". And the new branch keys on `busy`
   * (`statistics.isFetching`) rather than on `refreshing` above, because this text is the
   * statistics region's own and must not speak for the round record's separate read — it
   * is the same value as this region's `aria-busy`, so the text and the attribute can
   * never disagree.
   *
   * `aria-busy="true"` lets assistive technology defer presenting a live-region change
   * until it is false, so the "Refreshing…" wording is not relied on to interrupt: its job
   * is that a trustee reading the region mid-refresh — or hearing it batched on
   * completion — is never told the figures are settled while they are not.
   *
   * ## Revision 5 (ADR-038, TAD §8.3) — the arrival announcement states the STAMP, not the
   * action, and this is the one screen-level change Revision 5 requires
   *
   * Inside the freshness window (§5.3.1) **Refresh figures** legitimately returns without
   * recomputing anything: `fetchRoundStatistics` finds a document younger than
   * `staleAfterSeconds` and renders it, writing nothing and triggering nothing. So this
   * region cannot say *"Figures refreshed"* — it would be **false in the common case** once
   * `staleAfterSeconds` is seeded, and a trustee acting on it would believe a stale-but-valid
   * figure had just been recomputed. The one wording this screen must not use is any phrase
   * implying the button always causes work.
   *
   * It says *"Figures are current as at <stamp>."* instead, which is true whether the button
   * caused a computation, found a fresh one somebody else caused, or was never pressed at
   * all. The stamp is `computedOn` — the same value the visible freshness line and the
   * printed pack carry (§3.3 property 5), through the same `formatDateTime`, so the
   * announcement and the text on screen can never disagree about when. A trustee who wants
   * to know whether anything *changed* reads that stamp; that is why §3.3 keeps it on screen.
   */
  const liveStatus =
    view.statistics.kind === "loading"
      ? "Loading the round's figures."
      : busy
        ? "Refreshing the round's figures…"
        : view.statistics.kind === "figures"
          ? `Figures are current as at ${formatDateTime(view.statistics.response.computedOn)}.`
          : "The round's figures are not available.";

  return (
    <>
      <h1>{title}</h1>

      {/* FR-057, stated rather than implied. A trustee who expects a round selector should
          learn from the screen why there is none, not conclude one is missing. */}
      <p className={styles.hint}>
        This portal shows the one grant round currently open for review. There is no round
        to choose.
      </p>

      {/* Chrome, not content: a navigation control is interactive and prints as a dead
          grey box, so it is hidden on paper like the list's own action bar (FR-039). */}
      <nav aria-label="Portal sections" className={styles.landingNav} data-print="hide">
        <Button variant="primary" onClick={onOpenList}>
          Open the applications list
        </Button>
      </nav>

      {/*
        Outside the live region on purpose: a control that re-renders inside a `role="status"`
        region gets its own changes announced, which is noise rather than information. Its
        accessible name is "Refresh figures" in every state — a name that changed to
        "Refreshing…" would be a different control to a screen reader every time it was used.
        Not disabled while in flight, because disabling a focused button drops focus.
      */}
      <div className={styles.refreshBar} data-print="hide">
        <Button
          variant="secondary"
          onClick={() => {
            void round.refetch();
            void statistics.refetch();
          }}
        >
          Refresh figures
        </Button>

        {/*
          The inline idiom `VerdictSection.tsx:42` already establishes — a `size="tiny"`
          labelled Spinner — and not a new visual pattern: no overlay, no skeleton, and
          nothing that replaces the button, so the control the trustee just pressed does
          not move or vanish under the pointer while they are still on it.

          It sits inside `.refreshBar`, which means OUTSIDE the live region for the same
          reason the button is: it re-renders on its own schedule, and a spinner mounting
          and unmounting inside `role="status"` is announced as noise. `data-print="hide"`
          on the bar already covers it on paper.

          Its label repeats the button's own wording rather than naming which of the two
          reads is in flight (WCAG 3.2.4): the trustee pressed one control and is owed one
          answer about it, not a running commentary on a direct read and a flow call.
        */}
        {refreshing ? (
          <Spinner
            size="tiny"
            label="Refreshing the round's figures…"
            labelPosition="after"
          />
        ) : null}
      </div>

      {/* The direct read's own outcome — the round's identity and calendar (FR-057,
          FR-058's open date). One diagnostic covers this block and the financial position
          block below it, because both come from the same single row. */}
      {view.finance.kind === "loading" ? (
        <Spinner label="Loading the round record…" labelPosition="below" />
      ) : view.finance.kind === "diagnostic" ? (
        <StateMessage
          heading={view.finance.message.heading}
          explanation={view.finance.message.explanation}
        />
      ) : (
        <Panel heading="This round">
          <Definitions
            items={[
              { label: "Round", value: view.finance.round.roundKey ?? "Not recorded" },
              { label: "Opened", value: formatDate(view.finance.round.roundOpenedOn) },
              ...(view.finance.round.roundClosedOn === null
                ? []
                : [{ label: "Closed", value: formatDate(view.finance.round.roundClosedOn) }]),
            ]}
          />
        </Panel>
      )}

      {/*
        TAD §8.3: the statistics region is a live region, so a screen-reader trustee is told
        when the figures are loading and told again when they arrive. A visual skeleton
        announces nothing on its own. `aria-busy` covers the in-flight state including an
        explicit refresh, whose result is therefore announced through this same region.
      */}
      <div
        className={styles.statisticsRegion}
        role="status"
        aria-busy={busy}
        data-print="block"
      >
        <p className={styles.srOnly}>{liveStatus}</p>

        {view.statistics.kind === "loading" ? (
          <Spinner label="Computing the round's figures…" labelPosition="below" />
        ) : view.statistics.kind === "diagnostic" ? (
          <StateMessage
            heading={view.statistics.message.heading}
            explanation={view.statistics.message.explanation}
          />
        ) : (
          <RoundStatistics response={view.statistics.response} />
        )}
      </div>

      {view.finance.kind === "figures" ? (
        <RoundFinancePanel round={view.finance.round} />
      ) : null}
    </>
  );
}
