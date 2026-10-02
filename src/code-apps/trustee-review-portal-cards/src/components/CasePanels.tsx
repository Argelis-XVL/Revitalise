/**
 * The panels of an application detail screen — WBS 6.3, FR-035, SDD US-012 AC-2/AC-7,
 * FR-078, FR-079.
 *
 * ## Card layout (Design 2.0) — THIS APP ONLY (`trustee-review-portal-cards`)
 *
 * TAD `docs/architecture/trustee-portal-design-2-architecture.md`, ADR-055..059 (wbs:6.3,
 * unbilled). This file is on the parity gate's allow-list: it is the one place the two apps'
 * detail screens are allowed to differ, and everything it renders still comes from the same
 * `APPLICATION_DETAIL_LAYOUT` (byte-identical in both apps).
 *
 * `DetailSectionPanel` renders each layout GROUP as before — the Pack sub-heading as an `<h3>`,
 * the group's `data-section`/`data-group` wrapper — but instead of one `<dl>` per group it
 * partitions the group's visible rows by DISPLAY (`domain/applicationDetailDisplay.ts`, ADR-058)
 * and renders each display group with its own small component: `FactTiles`, `CostReceipt`,
 * `AnswerCards`, `ScoreBar`, `LifeScale`, `AnswerList`, `RestrictedList`. The Summary section
 * renders as `SummaryHero` instead of a panel. Rows are never hard-coded here: a row's id,
 * label, cell and visibility all come from the spec, and its display from the map.
 *
 * WHAT THIS CHANGES ABOUT ORDER, AND ONLY HERE (ADR-057, reviewer R1): within a section, rows are
 * grouped by display type, so DOM order is Pack order WITHIN each display group rather than
 * across the whole section. Every row is still present, labelled verbatim, in its Pack section.
 * `pages/ApplicationDetailPage.test.tsx` states the new contract; the first app's contract and
 * its tests are unchanged.
 *
 * Unchanged in meaning from the first app (its own header, Revisions 4-15, is the history): a
 * redacted row's withheld and released-empty states are both notes, never alerts, and look
 * different; a restricted row is a `<dt>`/`<dd>` pair whose `<dd>` carries the restricted text,
 * so a screen reader reads it the same way as a value; `redactedTextState()` alone decides the
 * redaction state and no component here reads a column.
 */
import type { DetailSection } from "../domain/applicationDetailLayout";
import type { DisplayGroup } from "../domain/applicationDetailDisplay";
import {
  GROUP_HEADING,
  HERO_SECTION_ID,
  SECTION_EYEBROW,
  SPACIOUS_SECTIONS,
  STAFF_RECOMMENDATION_EYEBROW,
  partitionRows,
} from "../domain/applicationDetailDisplay";
import type { ApplicationDetail } from "../dataverse/types";
import { formatDate } from "../domain/format";
import styles from "../styles/detail.module.css";
import { Definitions, MultilineText, StateMessage } from "./Panel";
import { AnswerCards } from "./detail/AnswerCards";
import { AnswerList } from "./detail/AnswerList";
import { CostReceipt } from "./detail/CostReceipt";
import { DetailPanel } from "./detail/DetailPanel";
import { FactTiles } from "./detail/FactTiles";
import { LifeScale } from "./detail/LifeScale";
import { RestrictedList } from "./detail/RestrictedList";
import { ScoreBar } from "./detail/ScoreBar";
import { SummaryHero } from "./detail/SummaryHero";

/** One display group's rows, through the component for its kind. */
function DisplayGroupContent({ group, detail }: { group: DisplayGroup; detail: ApplicationDetail }) {
  switch (group.kind) {
    case "tiles":
      return <FactTiles rows={group.rows} detail={detail} />;
    case "costs":
      return <CostReceipt rows={group.rows} />;
    case "answers":
      return <AnswerCards rows={group.rows} />;
    case "score":
      return <ScoreBar rows={group.rows} detail={detail} />;
    case "scale":
      return <LifeScale rows={group.rows} detail={detail} />;
    case "likert":
      return <AnswerList rows={group.rows} />;
    case "restricted":
      return <RestrictedList rows={group.rows} />;
    case "status":
      // A status row outside the hero (only a test builds one) renders as a plain tile.
      return <FactTiles rows={group.rows} detail={detail} />;
  }
}

function DisplayBlock({ group, detail }: { group: DisplayGroup; detail: ApplicationDetail }) {
  const heading = GROUP_HEADING[group.kind];
  return (
    <div className={styles.block} data-display-group={group.kind}>
      {heading === undefined ? null : <h3 className={styles.subHeading}>{heading}</h3>}
      <DisplayGroupContent group={group} detail={detail} />
    </div>
  );
}

/**
 * One section of the detail screen, rendered from its spec. The Summary section is the hero;
 * every other section is a card with its eyebrow, the Pack heading as its `<h2>`, and each layout
 * group partitioned into display groups (ADR-057, ADR-058).
 *
 * `data-field` on every row's `<dt>` carries the row id shared with the field map. A row with a
 * `visible` predicate (D11a, A3a, A3b) is omitted when `isRowVisible()` returns false — inside
 * `partitionRows`, exactly as in the first app.
 */
export function DetailSectionPanel({
  section,
  detail,
}: {
  section: DetailSection;
  detail: ApplicationDetail;
}) {
  if (section.id === HERO_SECTION_ID) {
    return <SummaryHero section={section} detail={detail} />;
  }
  return (
    <DetailPanel
      heading={section.heading}
      eyebrow={SECTION_EYEBROW[section.id]}
      spacious={SPACIOUS_SECTIONS.has(section.id)}
    >
      {section.groups.map((group, index) => (
        <div
          key={group.heading ?? `group-${String(index)}`}
          className={group.heading === null ? styles.group : `${styles.group} ${styles.groupHeaded}`}
          data-section={section.id}
          data-group={group.heading ?? ""}
        >
          {group.heading === null ? null : (
            <h3 className={styles.subHeading}>{group.heading}</h3>
          )}
          {partitionRows(section.id, group.rows, detail).map((displayGroup) => (
            <DisplayBlock key={displayGroup.kind} group={displayGroup} detail={detail} />
          ))}
        </div>
      ))}
    </DetailPanel>
  );
}

/** The staff recommendation, which lives on the review row (FR-035). Content unchanged (WI-0070). */
export function StaffRecommendationPanel({
  staffRecommendation,
  panelDate,
  loading,
}: {
  staffRecommendation: string | null;
  panelDate: string | null;
  loading: boolean;
}) {
  return (
    <DetailPanel heading="Staff recommendation" eyebrow={STAFF_RECOMMENDATION_EYEBROW}>
      {loading ? (
        <p>Loading the review record…</p>
      ) : staffRecommendation === null ? (
        <StateMessage
          heading="No staff recommendation recorded"
          explanation={
            "No staff recommendation has been written against this application's review " +
            "record. The rest of the case can still be decided from."
          }
        />
      ) : (
        <>
          <MultilineText text={staffRecommendation} />
          {panelDate === null ? null : (
            <Definitions items={[{ label: "Panel date", value: formatDate(panelDate) }]} />
          )}
        </>
      )}
    </DetailPanel>
  );
}
