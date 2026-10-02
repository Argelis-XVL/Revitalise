/**
 * The landing screen — FR-056 (the navigation shell) and FR-057..FR-063 (its content).
 * WBS 6.1 and 6.9.
 *
 * ## CARD APP (Design 2.0 Revision 2, TAD trustee-portal-design-2 §13.2; WI-0080..WI-0090)
 *
 * Presentation from `ui_kits/trustee-review-portal/RoundOverview.jsx`, content and behaviour
 * from this file as the first app has it (ADR-061). What changes here: the title and its
 * intro paragraph are one 8px group, both action buttons sit in ONE `ActionRow` (flex, wrap,
 * 12px), and "This round" is the round hero (`cards/RoundHero.tsx`: badge, the §13.7 sentence,
 * Opened/Closed and the ADR-065 application-share bar). What does NOT change, and is held by
 * the first app's `LandingPage.test.tsx` (contract): the `<h1>`, the FR-057 sentence, the
 * "Portal sections" nav, the Refresh control's unchanging name and its place outside the
 * live region, the live region itself, and every diagnostic state.
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
import { StateMessage } from "../components/Panel";
import { RoundHero } from "../cards/RoundHero";
import { formatDateTime } from "../domain/format";
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
  const refreshing =
    (round.isFetching && view.finance.kind !== "loading") ||
    (statistics.isFetching && view.statistics.kind !== "loading");
  const liveStatus =
    view.statistics.kind === "loading"
      ? "Loading the round's figures."
      : busy
        ? "Refreshing the round's figures…"
        : view.statistics.kind === "figures"
          ? `Figures are current as at ${formatDateTime(view.statistics.response.computedOn)}.`
          : "The round's figures are not available.";
  const figures = view.statistics.kind === "figures" ? view.statistics.response : null;
  const openRound = view.finance.kind === "figures" ? view.finance.round : null;

  return (
    <>
      {/* PageTitle + intro, 8px apart (RoundOverview.jsx lines 207-210). */}
      <div className={styles.titleGroup}>
        <h1>{title}</h1>
        <p className={styles.titleIntro}>
          This portal shows the one grant round currently open for review. There is no round
          to choose.
        </p>
      </div>

      {/* One ActionRow for both buttons (lines 211-214). The "Portal sections" nav and the
          refresh bar stay two elements: the nav is a landmark the contract tests find by name,
          and the refresh control must stay OUTSIDE the live region below. */}
      <div className={styles.landingActions} data-print="hide">
        <nav aria-label="Portal sections" className={styles.landingNav}>
          <Button variant="primary" onClick={onOpenList}>
            Open the applications list
          </Button>
        </nav>
        <div className={styles.refreshBar}>
          <Button
            variant="secondary"
            onClick={() => {
              void round.refetch();
              void statistics.refetch();
            }}
          >
            Refresh figures
          </Button>
          {refreshing ? (
            <Spinner
              size="tiny"
              label="Refreshing the round's figures…"
              labelPosition="after"
            />
          ) : null}
        </div>
      </div>

      {view.finance.kind === "loading" ? (
        <Spinner label="Loading the round record…" labelPosition="below" />
      ) : view.finance.kind === "diagnostic" ? (
        <StateMessage
          heading={view.finance.message.heading}
          explanation={view.finance.message.explanation}
        />
      ) : (
        <RoundHero
          round={view.finance.round}
          received={figures?.metrics.applicationsReceived?.count ?? null}
          history={figures?.metrics.historicApplicationsByMonth ?? null}
        />
      )}

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
          <RoundStatistics
            response={view.statistics.response}
            roundOpenedOn={openRound?.roundOpenedOn ?? null}
            roundClosedOn={openRound?.roundClosedOn ?? null}
          />
        )}
      </div>
      {view.finance.kind === "figures" ? (
        <RoundFinancePanel round={view.finance.round} />
      ) : null}
    </>
  );
}
