/**
 * The round hero — "This round" on the Round overview. Card app only (TAD trustee-portal-design-2
 * §13.2, WI-0081). Design: `RoundOverview.jsx` `RoundHero` (lines 21-49).
 *
 *   - A section with ONE `<h2>` whose accessible name stays "This round" (ADR-062 decision 2);
 *     its visible text is the §13.7 sentence "Open from {opened} to {closed}" / "Open since
 *     {opened}", or the plain heading when there is no open date.
 *   - The white badge: "Round" and the round key, as the first `<dt>`/`<dd>` of the round's
 *     definition list; Opened and (only when there is one) Closed follow as a small definition
 *     list, so the calendar reads exactly as the first app's Definitions do (the contract tests
 *     find "1 Aug 2026" and "Closed" as their own text).
 *   - The kit's close-date progress bar is REPLACED by the ADR-065 application-share bar
 *     (reviewer R13, R15): this round's applications as a share of this round plus the seeded
 *     pre-portal count. The bar is `aria-hidden`; its lines are the content.
 */
import { useId } from "react";
import type { HistoricApplications, RoundFinance } from "../dataverse/types";
import { formatDate, NOT_RECORDED } from "../domain/format";
import { Eyebrow, HeadingText } from "../components/Panel";
import { roundHeroSentence } from "./sentences";
import { shareBar } from "./shareBar";
import styles from "../styles/cards.module.css";

export function RoundHero({
  round,
  received,
  history,
}: {
  round: RoundFinance;
  /** `applicationsReceived.count` from the statistics response, or null while it is absent. */
  received: number | null;
  history: HistoricApplications | null;
}) {
  const headingId = useId();
  const bar = shareBar(received, history);
  const key = round.roundKey ?? NOT_RECORDED;
  return (
    <section className={styles.hero} aria-labelledby={headingId} data-print="block" data-hero="round">
      <dl className={styles.heroBadge}>
        <div className={styles.heroBadgeGroup}>
          <dt className={styles.heroBadgeLabel}>Round</dt>
          <dd className={key.length > 3 ? `${styles.heroBadgeValue} ${styles.heroBadgeValueLong}` : styles.heroBadgeValue}>
            {key}
          </dd>
        </div>
      </dl>
      <div className={styles.heroText}>
        <div className={styles.heroHeader}>
          <Eyebrow tone="purple">This round</Eyebrow>
          <h2 id={headingId} className={styles.heroHeading}>
            <HeadingText
              heading="This round"
              sentence={roundHeroSentence(round.roundOpenedOn, round.roundClosedOn)}
            />
          </h2>
        </div>
        <div className={styles.heroBody}>
          {bar.fill === null ? null : (
            <div className={styles.shareTrack} aria-hidden="true" data-print="hide">
              <div
                className={styles.shareFill}
                data-share={String(bar.fill)}
                style={{ width: `${String(bar.fill * 100)}%` }}
              />
            </div>
          )}
          {bar.lines.length === 0 ? null : (
            <ul className={styles.shareLines}>
              {bar.lines.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          )}
          <dl className={styles.heroDates}>
            <div className={styles.heroDate}>
              <dt>Opened</dt>
              <dd>{formatDate(round.roundOpenedOn)}</dd>
            </div>
            {round.roundClosedOn === null ? null : (
              <div className={styles.heroDate}>
                <dt>Closed</dt>
                <dd>{formatDate(round.roundClosedOn)}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </section>
  );
}
