/**
 * The Summary hero — WI-0057 (card, badge, heading), WI-0058 (status pill), WI-0059 (fact
 * chips). It replaces the Summary panel (README line 31) and renders the SAME nine rows the
 * Summary panel renders — S0a, S0b, S1-S7 — from the same spec rows; the hero adds no row
 * (TAD §3, "Personal data on screen").
 *
 * STRUCTURE, and why each part is where it is:
 *
 *   - It is still the Summary SECTION: a `<section aria-labelledby>` with ONE `<h2>` and
 *     `data-print="block"`. The `<h2>` is the design's heading ("{score} out of 60 circumstance
 *     points" / "Not scored yet", reviewer R2) and it begins with the Pack's section heading as
 *     visually hidden text, so a screen reader's heading list still reads "Summary: …".
 *   - The score badge is S3's `<dt>`/`<dd>`. Its visible label is "Score"; the Pack's full S3
 *     label is kept in the `<dt>` as visually hidden text (README line 69).
 *   - Row 1 is the status pill (S0a, whose `<dt>` "Status" is visually hidden — the pill IS the
 *     value) followed by the S0b, S1, S2 chips; row 2 is S4-S7. Which row a chip sits in is data
 *     (`HERO_FIRST_ROW`), not JSX.
 *   - S6's chip reads the shortened label (reviewer R3); the Pack label stays in its `<dt>` as
 *     visually hidden text (ADR-059 decision 3).
 */
import { useId } from "react";
import type { ApplicationDetail } from "../../dataverse/types";
import type { DetailSection } from "../../domain/applicationDetailLayout";
import type { ResolvedRow } from "../../domain/applicationDetailDisplay";
import {
  CHIP_LABEL,
  HERO_FIRST_ROW,
  SCORE_BADGE_LABEL,
  SECTION_EYEBROW,
  badgeValue,
  badgeValueIsLong,
  heroHeading,
  isAbsentText,
  numberOf,
  partitionRows,
  statusToneOf,
  statusOf,
} from "../../domain/applicationDetailDisplay";
import styles from "../../styles/detail.module.css";
import { EyebrowLine } from "./DetailPanel";
import { plainText } from "./cellText";

function ScoreBadge({ resolved, detail }: { resolved: ResolvedRow; detail: ApplicationDetail }) {
  const { row, cell } = resolved;
  const value = badgeValue(numberOf(row.id, detail));
  const absent = numberOf(row.id, detail) === null;
  return (
    <div className={styles.badgeGroup}>
      <dt data-field={row.id} className={styles.badgeLabel}>
        <span aria-hidden="true">{SCORE_BADGE_LABEL}</span>
        <span className={styles.srOnly}>{row.label}</span>
      </dt>
      <dd
        className={
          badgeValueIsLong(value) ? `${styles.badgeValue} ${styles.badgeValueLong}` : styles.badgeValue
        }
      >
        {absent ? (
          <>
            <span aria-hidden="true">{value}</span>
            {/* The dash is a picture of "none"; a screen reader hears the cell's own words. */}
            <span className={styles.srOnly}>{plainText(cell)}</span>
          </>
        ) : (
          value
        )}
      </dd>
    </div>
  );
}

function StatusPill({ resolved, detail }: { resolved: ResolvedRow; detail: ApplicationDetail }) {
  const { row, cell } = resolved;
  return (
    <div
      className={styles.statusPill}
      data-tone={statusToneOf(statusOf(row.id, detail))}
      data-print="tile"
    >
      <dt data-field={row.id} className={styles.srOnly}>
        {row.label}
      </dt>
      <dd>
        <span className={styles.statusDot} aria-hidden="true" />
        {plainText(cell)}
      </dd>
    </div>
  );
}

function FactChip({ resolved }: { resolved: ResolvedRow }) {
  const { row, cell } = resolved;
  const shortLabel = CHIP_LABEL[row.id];
  const text = plainText(cell);
  return (
    <div className={styles.chip} data-print="tile">
      <dt data-field={row.id} className={styles.chipLabel}>
        {shortLabel === undefined ? (
          row.label
        ) : (
          <>
            <span aria-hidden="true">{shortLabel}</span>
            <span className={styles.srOnly}>{row.label}</span>
          </>
        )}
      </dt>
      <dd className={styles.chipValue} data-absent={isAbsentText(text) ? "true" : undefined}>
        {text}
      </dd>
    </div>
  );
}

export function SummaryHero({
  section,
  detail,
}: {
  section: DetailSection;
  detail: ApplicationDetail;
}) {
  const headingId = useId();
  const groups = section.groups.flatMap((group) => partitionRows(section.id, group.rows, detail));
  const rowsOf = (kind: string) => groups.filter((g) => g.kind === kind).flatMap((g) => g.rows);
  const scoreRows = rowsOf("score");
  const statusRows = rowsOf("status");
  const chipRows = rowsOf("tiles");
  const firstRowChips = chipRows.filter((r) => HERO_FIRST_ROW.has(r.row.id));
  const secondRowChips = chipRows.filter((r) => !HERO_FIRST_ROW.has(r.row.id));
  const firstScore = scoreRows[0];
  const score = firstScore === undefined ? null : numberOf(firstScore.row.id, detail);
  const eyebrow = SECTION_EYEBROW[section.id];

  return (
    <section
      className={styles.hero}
      aria-labelledby={headingId}
      data-print="block"
      data-section={section.id}
    >
      {scoreRows.length === 0 ? null : (
        <dl className={styles.badge}>
          {scoreRows.map((resolved) => (
            <ScoreBadge key={resolved.row.id} resolved={resolved} detail={detail} />
          ))}
        </dl>
      )}
      <div className={styles.heroText}>
        <div className={styles.heroHeader}>
          {eyebrow === undefined ? null : <EyebrowLine eyebrow={eyebrow} />}
          <h2 id={headingId} className={styles.heroHeading}>
            {/* The space is outside the hidden span: an accessible name joins the parts as they
                are, and a line-start space collapses on screen. */}
            <span className={styles.srOnly}>{section.heading}:</span> {heroHeading(score)}
          </h2>
        </div>
        {statusRows.length + firstRowChips.length === 0 ? null : (
          // ApplicationDetail.jsx:120-123: the pill and the first FactChips block are two items
          // of one wrapping row, and the chips wrap as ONE unit — so at narrow widths the pill
          // sits alone on its line rather than sharing it with "Review round".
          <div className={styles.heroRowOne}>
            {statusRows.length === 0 ? null : (
              <dl className={styles.pillList}>
                {statusRows.map((resolved) => (
                  <StatusPill key={resolved.row.id} resolved={resolved} detail={detail} />
                ))}
              </dl>
            )}
            {firstRowChips.length === 0 ? null : (
              <dl className={styles.chipRow}>
                {firstRowChips.map((resolved) => (
                  <FactChip key={resolved.row.id} resolved={resolved} />
                ))}
              </dl>
            )}
          </div>
        )}
        {secondRowChips.length === 0 ? null : (
          <dl className={styles.chipRow}>
            {secondRowChips.map((resolved) => (
              <FactChip key={resolved.row.id} resolved={resolved} />
            ))}
          </dl>
        )}
      </div>
    </section>
  );
}
