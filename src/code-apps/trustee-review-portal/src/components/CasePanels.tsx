/**
 * The panels of an application detail screen — WBS 6.3, FR-035, SDD US-012 AC-2/AC-7,
 * FR-078, FR-079.
 *
 * CORRECTED, Amendment A-05 pass (2026-08-27) — this comment previously said "these four
 * [narrative, score, holiday, staff recommendation] are exactly what FR-035 names, and
 * nothing else," which was already out of step with `CareSupportPanel` before this pass and
 * is now out of step with three more panels this pass adds
 * (`FinancialEligibilityPanel`/`ConditionProfilePanel`/`HelperRefereeContactPanel`) —
 * exactly the `stale-comment-contradicts-source` class `IMP-0330` names, and exactly the
 * kind of drift Amendment A-05's own reversal makes worth stating in full rather than
 * patching around: it names *every* board-pack field, not a screen kept deliberately
 * narrower than the printed pack (SDD §7.1b, TAD §0.0). Every panel below still renders
 * only what a named requirement asks for; the requirement itself just grew.
 *
 * ## Revision 4 (2026-08-27) — TWO TONES WIRED, AND NOTHING ELSE ON THIS SCREEN CHANGED
 *
 * TAD §8.5 point 1. Four panels below render the redaction state machine with an identical
 * two-branch shape — `NarrativePanel`, `CareSupportPanel`, `FinancialEligibilityPanel`,
 * `ConditionProfilePanel` — and the non-released branch covers TWO states that are not the
 * same fact. `withheld` means the trustee is not permitted to see it; `released-empty` means
 * nothing has been scrubbed into the field yet. Each now selects its own `StateMessage`
 * tone, so the two are visually distinct: rendering either as one undifferentiated grey box
 * asserts something false about UK GDPR Art. 9 data, and `domain/visibility.ts:98-106`
 * records why `released-empty` is not the same fact as "nothing recorded".
 *
 * `WITHHELD_OR_EMPTY_TONE` below is the whole of the change. NO state machine is opened: not
 * one file under `src/domain/` is touched, `visibility.ts`'s discriminated union is read
 * exactly as before, and the FR-078 catalogue rows still spread into the SAME `Definitions`
 * list as real values — because a restricted row and a real value must read the same way to
 * a screen reader, which is what `Definitions`' `<dl>`/`<dt>`/`<dd>` markup buys and what
 * `CasePanels.test.tsx:282-286` / `:417-419` check by counting those rows.
 *
 * The tone is deliberately NOT applied to the two `StateMessage`s outside that state machine
 * (`ScorePanel`'s missing breakdown, `StaffRecommendationPanel`'s missing recommendation).
 * `quiet`'s entire job is to be distinguishable from `muted` WITHIN one panel's redaction
 * state machine; spending it on unrelated panels would dilute the distinction §8.5 point 1
 * exists to protect.
 */
import {
  APPLICANT_TYPE_LABELS,
  APPLICATION_STATUS_LABELS,
  BREAK_TYPE_LABELS,
  CARE_HOURS_BAND_LABELS,
  CARE_PROVIDED_TYPE_LABELS,
  CONDITION_PROFILE_LABELS,
  INCOME_BAND_LABELS,
  INCOME_FLAG_LABELS,
  optionLabel,
  optionLabels,
} from "../dataverse/schema";
import type { ApplicationDetail } from "../dataverse/types";
import {
  formatAmount,
  formatDate,
  formatDateRange,
  formatScore,
  formatText,
  formatYesNo,
  totalFundingRequested,
} from "../domain/format";
import { FIELD_CATALOGUE_GROUPS, restrictedFieldsForGroup } from "../domain/fieldCatalogue";
import {
  careSupportState,
  conditionFreeTextState,
  financialFreeTextState,
  narrativeState,
} from "../domain/visibility";
import styles from "../styles/app.module.css";
import { Definitions, MultilineText, Panel, StateMessage } from "./Panel";
import type { StateMessageTone } from "./Panel";

/**
 * The tone for the non-released branch of a redaction state machine — TAD §8.5 point 1.
 *
 * One function, used by all four panels that render that branch, so the mapping cannot
 * drift between them and a reader can check it in one place. `withheld` is the filled grey
 * panel; `released-empty` is the lighter, unfilled one. The parameter type is the two
 * non-released members of `visibility.ts`'s own unions, so adding a fourth state there
 * would be a compile error here rather than a silently-defaulted box.
 */
function withheldOrEmptyTone(kind: "withheld" | "released-empty"): StateMessageTone {
  return kind === "withheld" ? "muted" : "quiet";
}

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
        <StateMessage
          heading={state.heading}
          explanation={state.explanation}
          tone={withheldOrEmptyTone(state.kind)}
        />
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

/**
 * The care-support description — the structured care-support pair and applicant-type
 * context, plus the free-text companion to the structured fields (FR-035, TAD §3.2,
 * §3.2.1, WBS 6.3, Amendment A-02/OQ-032).
 *
 * Three column families, two different visibility rules, in one panel because they are
 * one topic to a trustee reading a case:
 *
 *   - `applicantType`, `careProvidedType`, `careHoursPerWeek` — structured facts,
 *     `IsSecured=0` in their own right, rendered UNCONDITIONALLY (same basis as
 *     `amountRequested` on `HolidayPanel`). Applicant type is placed here rather than on
 *     its own panel because it is what makes the structured pair legible: whether the
 *     signed-in trustee is reading about care the applicant PROVIDES to someone else, or
 *     about their own needs, changes what "type of care provided" means.
 *   - the three `…redacted` free-text columns — the gated companion, unchanged from
 *     before this pass. Their secured sources are never named in this app (`schema.ts`).
 *
 * The gated half keeps its own three first-class states, exactly like `NarrativePanel`:
 * `withheld` and `released-empty` are both rendered as a note rather than an empty box,
 * and `released-empty` is reachable even once release is affirmed — see
 * `domain/visibility.ts` → `careSupportState`. The structured half does not participate
 * in that gate at all — see `types.ts`'s `careProvidedType`/`careHoursPerWeek`/
 * `applicantType` for why.
 */
export function CareSupportPanel({ detail }: { detail: ApplicationDetail }) {
  const state = careSupportState(detail);
  return (
    <Panel heading="Care-support description">
      <Definitions
        items={[
          { label: "Applicant type", value: optionLabel(APPLICANT_TYPE_LABELS, detail.applicantType) },
          {
            label: "Type of care provided",
            value: formatText(optionLabels(CARE_PROVIDED_TYPE_LABELS, detail.careProvidedType)),
          },
          {
            label: "Hours of support per week",
            value: optionLabel(CARE_HOURS_BAND_LABELS, detail.careHoursPerWeek),
          },
        ]}
      />
      {state.kind === "released" ? (
        <>
          <h3 className={styles.fieldHeading}>Care-support description</h3>
          <MultilineText text={formatText(state.description)} />
          <h3 className={styles.fieldHeading}>Example of care provided</h3>
          <MultilineText text={formatText(state.example)} />
          <h3 className={styles.fieldHeading}>Other care provided</h3>
          <MultilineText text={formatText(state.otherType)} />
        </>
      ) : (
        <StateMessage
          heading={state.heading}
          explanation={state.explanation}
          tone={withheldOrEmptyTone(state.kind)}
        />
      )}
    </Panel>
  );
}

/**
 * Financial eligibility (Amendment A-05, TAD §3.2.2/§3.2.3, ADR-031/ADR-032, WBS 6.3, SDD
 * §7.1b).
 *
 * Three column families, exactly like `CareSupportPanel` above, and the same reason: one
 * board-pack topic to a trustee reading a case.
 *
 *   - income flag/band, savings over £6,000 — structured facts, `IsSecured=0`, rendered
 *     UNCONDITIONALLY, same basis as `amountRequested` on `HolidayPanel`.
 *   - the restricted-state rows (benefit status, benefit provider, employment status) —
 *     from the build-derived field catalogue, NEVER a fetched column (ADR-032). Rendered
 *     via the same `Definitions` component as every value above them, because FR-078 asks
 *     for the field to be named, not hidden — a restricted row and a real value read the
 *     same way to a screen reader.
 *   - the redacted free-text row — gated by `redactionReleased`, the same three first-class
 *     states as `NarrativePanel`/`CareSupportPanel`. See `domain/visibility.ts` →
 *     `financialFreeTextState`.
 */
export function FinancialEligibilityPanel({ detail }: { detail: ApplicationDetail }) {
  const state = financialFreeTextState(detail);
  const restricted = restrictedFieldsForGroup(FIELD_CATALOGUE_GROUPS.financialEligibility);
  return (
    <Panel heading="Financial eligibility">
      <Definitions
        items={[
          { label: "Income flag", value: optionLabel(INCOME_FLAG_LABELS, detail.incomeFlag) },
          { label: "Income band", value: optionLabel(INCOME_BAND_LABELS, detail.incomeBand) },
          { label: "Savings over £6,000", value: formatYesNo(detail.savingsOver6000) },
          ...restricted,
        ]}
      />
      {state.kind === "released" ? (
        <>
          <h3 className={styles.fieldHeading}>Why unable to fund the break</h3>
          <MultilineText text={formatText(state.unableToFundExplanation)} />
        </>
      ) : (
        <StateMessage
          heading={state.heading}
          explanation={state.explanation}
          tone={withheldOrEmptyTone(state.kind)}
        />
      )}
    </Panel>
  );
}

/**
 * Condition and circumstance (Amendment A-05, TAD §3.2.2, ADR-031, WBS 6.3, SDD §7.1b).
 *
 * Distinct from `CareSupportPanel`: that panel is the applicant's own caregiving role
 * toward someone else (FR-035, Amendment A-02); this one is the applicant's — and the
 * support recipient's — OWN condition categories, plus the free-text elaboration behind
 * the exceptional-circumstance category. No restricted-state rows here: every secured
 * column this board-pack group touches is free text with a redacted counterpart (ADR-031),
 * not a Group B identity column.
 */
export function ConditionProfilePanel({ detail }: { detail: ApplicationDetail }) {
  const state = conditionFreeTextState(detail);
  return (
    <Panel heading="Condition and circumstance">
      <Definitions
        items={[
          {
            label: "Condition profile",
            value: formatText(optionLabels(CONDITION_PROFILE_LABELS, detail.conditionProfile)),
          },
          {
            label: "Support recipient condition profile",
            value: formatText(
              optionLabels(CONDITION_PROFILE_LABELS, detail.supportRecipientConditionProfile),
            ),
          },
        ]}
      />
      {state.kind === "released" ? (
        <>
          <h3 className={styles.fieldHeading}>Other condition notes</h3>
          <MultilineText text={formatText(state.otherCondition)} />
          <h3 className={styles.fieldHeading}>Support recipient other condition notes</h3>
          <MultilineText text={formatText(state.supportRecipientOtherCondition)} />
          <h3 className={styles.fieldHeading}>Exceptional funding detail</h3>
          <MultilineText text={formatText(state.exceptionalFundingDetail)} />
          <h3 className={styles.fieldHeading}>Other exceptional circumstance</h3>
          <MultilineText text={formatText(state.otherExceptionalCircumstance)} />
        </>
      ) : (
        <StateMessage
          heading={state.heading}
          explanation={state.explanation}
          tone={withheldOrEmptyTone(state.kind)}
        />
      )}
    </Panel>
  );
}

/**
 * Helper, referee and emergency contact (Amendment A-05, TAD §3.2.3, ADR-032, WBS 6.3, SDD
 * §7.1b).
 *
 * The four unsecured helper facts render as ordinary values. The eight identity columns —
 * helper/referee name, email, phone, plus emergency-contact name and phone — are Group B:
 * `IsSecured=1`, inside `REV_TrusteeRestricted`, and NEVER queried (ADR-032). Their rows
 * come entirely from the build-derived catalogue, in the same `Definitions` list as the
 * four real values above them — a restricted row and a real value are announced the same
 * way to a screen reader, which is the point of FR-078's "explicit... rather than an empty
 * value or by omitting the field."
 */
export function HelperRefereeContactPanel({ detail }: { detail: ApplicationDetail }) {
  const restricted = restrictedFieldsForGroup(
    FIELD_CATALOGUE_GROUPS.helperRefereeEmergencyContact,
  );
  return (
    <Panel heading="Helper, referee and emergency contact">
      <Definitions
        items={[
          { label: "Helper organisation", value: formatText(detail.helperOrganisation) },
          { label: "Helper relationship", value: formatText(detail.helperRelationship) },
          {
            label: "Helper declaration given",
            value: formatYesNo(detail.helperDeclarationConsent),
          },
          {
            label: "Helper declaration date",
            value: formatDate(detail.helperDeclarationConsentDate),
          },
          ...restricted,
        ]}
      />
    </Panel>
  );
}

/**
 * Holiday details (FR-035).
 *
 * "Total funding requested" is `rev_amountrequested` + `rev_additionalamountrequested`,
 * combined by `totalFundingRequested()` per FR-035's adopted wording (TAD §3.2, Amendment
 * A-02/OQ-031: *"total requested funding for that grant round, including any exceptional
 * funding requested"*) — ONE figure, not the itemised accommodation/travel/other breakdown
 * the reviewer declined. "Includes exceptional funding" renders the
 * `rev_exceptionalfundingrequested` flag alongside it, so the total is explicable rather
 * than just larger, exactly as the TAD asks. `rev_costs` is retained as a separate line: it
 * is TAD §3.1's own FR-060 column (the round-level cost aggregate), not part of FR-035's
 * adopted wording, and removing already-shown information was not asked for.
 */
export function HolidayPanel({ detail }: { detail: ApplicationDetail }) {
  return (
    <Panel heading="Holiday details">
      <Definitions
        items={[
          { label: "Type of break", value: optionLabel(BREAK_TYPE_LABELS, detail.breakType) },
          {
            label: "Preferred dates",
            value: formatDateRange(detail.preferredStart, detail.preferredEnd),
          },
          { label: "Break location", value: formatText(detail.breakLocation) },
          { label: "Provider preference", value: formatText(detail.providerPreference) },
          {
            label: "Total funding requested",
            value: formatAmount(
              totalFundingRequested(detail.amountRequested, detail.additionalAmountRequested),
            ),
          },
          {
            label: "Includes exceptional funding",
            value: detail.exceptionalFundingRequested ? "Yes" : "No",
          },
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
