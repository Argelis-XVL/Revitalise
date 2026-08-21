/**
 * The panels of an application detail screen — WBS 6.3, FR-035, SDD US-012 AC-2:
 * redacted narrative, score breakdown, holiday details, staff recommendation.
 *
 * These four are exactly what FR-035 names, and nothing else. The screen is deliberately
 * narrow: every additional column on a trustee-facing surface is a disclosure decision,
 * and one that was not asked for is one nobody has signed off.
 */
import { APPLICATION_STATUS_LABELS, optionLabel } from "../dataverse/schema";
import type { ApplicationDetail } from "../dataverse/types";
import {
  formatAmount,
  formatDate,
  formatDateRange,
  formatScore,
  formatText,
} from "../domain/format";
import { narrativeState } from "../domain/visibility";
import { Definitions, MultilineText, Panel, StateMessage } from "./Panel";

/**
 * The anonymised narrative.
 *
 * Binds `rev_narrativeredacted` and nothing else. The withheld state is not an error and
 * not an empty box — it is the designed and, today, the ONLY reachable state, because
 * automation #5 (narrative scrubbing) is deferred so nothing is ever released. That is
 * the safety basis `contract/known-exceptions.json` → `EX-003` rests on, so it is built
 * and tested as a first-class state.
 */
export function NarrativePanel({ detail }: { detail: ApplicationDetail }) {
  const state = narrativeState(detail);
  return (
    <Panel heading="Anonymised narrative">
      {state.kind === "released" ? (
        <MultilineText text={state.text} />
      ) : (
        <StateMessage heading={state.heading} explanation={state.explanation} />
      )}
    </Panel>
  );
}

/** The circumstance score and the breakdown that evidences it (FR-035). */
export function ScorePanel({ detail }: { detail: ApplicationDetail }) {
  return (
    <Panel heading="Circumstance score">
      <Definitions
        items={[
          { label: "Score", value: formatScore(detail.circumstanceScore) },
          { label: "Status", value: optionLabel(APPLICATION_STATUS_LABELS, detail.status) },
          { label: "Review round", value: formatText(detail.reviewRound) },
        ]}
      />
      {detail.scoreBreakdown === null ? (
        <StateMessage
          heading="No score breakdown recorded"
          explanation="The scoring automation has not written a breakdown for this application yet."
        />
      ) : (
        <MultilineText text={detail.scoreBreakdown} />
      )}
    </Panel>
  );
}

/** Holiday details (FR-035). */
export function HolidayPanel({ detail }: { detail: ApplicationDetail }) {
  return (
    <Panel heading="Holiday details">
      <Definitions
        items={[
          {
            label: "Preferred dates",
            value: formatDateRange(detail.preferredStart, detail.preferredEnd),
          },
          { label: "Break location", value: formatText(detail.breakLocation) },
          { label: "Provider preference", value: formatText(detail.providerPreference) },
          { label: "Amount requested", value: formatAmount(detail.amountRequested) },
          { label: "Total costs", value: formatAmount(detail.costs) },
        ]}
      />
    </Panel>
  );
}

/** The staff recommendation, which lives on the review row (FR-035). */
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
    <Panel heading="Staff recommendation">
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
    </Panel>
  );
}
