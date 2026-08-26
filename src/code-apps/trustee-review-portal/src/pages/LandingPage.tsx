/**
 * The landing screen — FR-056 (the navigation shell) and FR-057..FR-063 (its content).
 * WBS 6.1 and 6.9.
 *
 * ## What it does, in three steps — TAD §5.4
 *
 *   1. Reads `rev_roundfinance` with `rev_isopen eq true`, `top 2`, on the trustee's own
 *      privileges. One row is expected; zero and two-or-more are diagnostic states of
 *      their own, evaluated here, client-side, before the flow is called at all.
 *   2. Calls `REV | Portal | Round Statistics`. No arguments — the flow takes no input
 *      parameters, so a trustee can cause this one question to be asked and no other.
 *   3. Reconciles the two round keys. On a mismatch neither half is shown, because a
 *      financial position from one round beside application figures from another would
 *      look entirely normal and be wrong.
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
 * name does not change between states. Diagnostics go through `StateMessage`, which is
 * `role="note"` and not `role="alert"` — these are the designed states of the screen and
 * an alert would interrupt a screen-reader trustee to tell them something expected.
 */
import { Button, Spinner } from "@fluentui/react-components";
import { RoundFinancePanel } from "../components/RoundFinancePanel";
import { RoundStatistics } from "../components/RoundStatistics";
import { Definitions, Panel, StateMessage } from "../components/Panel";
import { formatDate } from "../domain/format";
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
  const liveStatus =
    view.statistics.kind === "loading"
      ? "Loading the round's figures."
      : view.statistics.kind === "figures"
        ? "The round's figures have loaded."
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
        <Button className={styles.tallTarget} appearance="primary" onClick={onOpenList}>
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
          className={styles.tallTarget}
          onClick={() => {
            void round.refetch();
            void statistics.refetch();
          }}
        >
          Refresh figures
        </Button>
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
