/**
 * The panels of an application detail screen — WBS 6.3, FR-035, SDD US-012 AC-2/AC-7,
 * FR-078, FR-079.
 *
 * ## Revision 15 — WI-0005 (EF-04) re-opened a THIRD time: rows, not panels (2026-09-30)
 *
 * **Everything from "Revision 13" down to "Revision 4" below is history.** Those revisions
 * moved this file's own panels (`NarrativePanel`, `ScorePanel`, `HolidayPanel`,
 * `ConditionProfilePanel`, `CareSupportPanel`, `CurrentCircumstancesPanel`,
 * `FinancialEligibilityPanel`) into the Trustee Pack's section order, but each panel kept its
 * own field set and labels, so the Pack's rows were still missing, relabelled or in the wrong
 * section. The reviewer's third raise: "the fields in the subsections" must follow the PDF
 * too, and Application Details was "missing quite a few columns".
 *
 * Those seven panels are REMOVED. The screen now renders `domain/applicationDetailLayout.ts`,
 * the Pack's own row list, through ONE component, `DetailSectionPanel`, so no panel owns a field
 * set any more. What each removed panel showed is accounted for row by row in
 * `docs/development/trustee-portal-pack-field-map.md`. `StaffRecommendationPanel` stays: it is
 * the review row's field, not an application field, and the Pack has no section for it.
 *
 * Kept from Revision 4, unchanged in meaning: a redacted row's withheld and released-empty
 * states are both notes, never alerts, and take DIFFERENT tones (`withheldOrEmptyTone`), and a
 * restricted row renders in the same `<dl>` as real values, so a screen reader reads both the
 * same way (FR-078, TAD §8.5 points 1-2).
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
 * ## Revision 13 — EF-04 re-opened, `docs/plans/emily-review-feedback-2026-09-plan.md`
 *
 * The reviewer's live check (Anna Southern, row 6 of the post-deployment feedback sheet under
 * `docs/Import/`) found the screen did not actually match the delivered pack, despite Revision 12's
 * comment claiming it did. The cause was the plan's own paraphrase at line 1054 losing a
 * distinction the source PDF keeps: **"Current Circumstances" in the pack (p.2) is the score's
 * question-level breakdown — "Overall, how satisfied are you...", "In the last 2 weeks...",
 * "In the last year..." — never the condition/illness fields.** Revision 12 mapped
 * `ConditionProfilePanel` ("Condition and circumstance") to that pack section by name
 * resemblance; the actual PDF places condition/illness questions in "About Applicant" (p.1,
 * alongside "please select all conditions or illnesses that apply"), ahead of the care-support
 * questions that continue onto p.2, and keeps the score breakdown in its own section, well
 * after About Applicant.
 *
 * Two fixes, both mechanical once the PDF was actually opened (checked page-by-page, not the
 * paraphrase) rather than guessed from the plan's summary line:
 *
 * 1. **The score breakdown is split out of `ScorePanel` into a new `CurrentCircumstancesPanel`**
 *    and moved down, after the About Applicant pair — it was rendered inside `ScorePanel`
 *    itself, second on the page, which is exactly what EF-07 separately flagged ("wellbeing
 *    answers not moved down"). `ScorePanel` keeps the score/status/round Definitions only, and
 *    stays where the Summary section's own score line belongs — early, before Application
 *    Details.
 * 2. **`ConditionProfilePanel` now renders BEFORE `CareSupportPanel`**, not after: the PDF's
 *    About Applicant section asks the condition/illness questions first and the care-support
 *    questions second (p.1 into p.2), so the two panels' relative order reverses from Revision
 *    12.
 *
 * `CurrentCircumstancesPanel`'s content is unchanged from what `ScorePanel` rendered before —
 * `detail.scoreBreakdown` verbatim — so this revision is an ORDER fix only. Whether that field
 * carries real per-question labels (EF-24) is a separate, backend-side gap this revision does
 * not touch.
 *
 * ## Revision 14 — EF-04 re-opened a SECOND time: Revision 13's own claim was falsified live
 * (`docs/Import/FeedbackDeployment_20-09-2026.xlsx` row 6, "today" column, 2026-09-25)
 *
 * Revision 13's header above asserts `ScorePanel` "stays where the Summary section's own score
 * line belongs — early, before Application Details" and calls that the fix. The reviewer's live
 * check of the deployed screen found it still wrong: `ApplicationDetailPage.tsx` rendered
 * `NarrativePanel` — a portal-only addition with no section in the pack at all — ahead of
 * `ScorePanel`, so nothing resembling the pack's Summary table was the first thing on the page.
 * Re-checked against the PDF itself (p.1, not the plan's paraphrase, per this file's own
 * Revision 13 discipline): the pack's Summary table (`docs/Import/3. Round 4 - Individual
 * Applications.pdf` p.1, heading "...INDIVIDUAL- Summary") is a named, titled section, and this
 * screen's equivalent panel was headed "Circumstance score" — a label describing its one
 * Definitions row, not the section it stands in for.
 *
 * Two fixes, both here: (1) this panel's heading changes to **"Summary"**; (2)
 * `ApplicationDetailPage.tsx` now renders it FIRST, ahead of `NarrativePanel` — see that file's
 * own Revision 14 header for the render-order half of this fix.
 *
 * **Deliberately NOT widened to the pack's full Summary row set** (Application ID, "Are you?",
 * Start/End Date, Individual Total Amount, Exceptional Funding Amount). Three independent
 * reasons, not one judgement call: Application ID is already the `<h1>` (`ApplicationDetailPage`
 * Revision 11's own reasoning for not duplicating the reference); Start/End Date and the total
 * funding figure already render in `HolidayPanel` ("Application Details"), and the pack itself
 * repeats them across sections, so mirroring that repetition here would be a second dev-time
 * decision, not a forced one; and the Exceptional Funding Amount row cannot be added at all
 * without reversing OQ-031 — `types.ts`'s own `additionalAmountRequested` doc comment records
 * the reviewer's explicit answer that this figure is "never rendered as a separate itemised
 * line". The reviewer's own complaint was "Summary panel is missing at the top of the screen",
 * which this fix answers directly: score/status/round now reads as a Summary, first. Widening
 * the field set is a distinct, larger question this dispatch does not decide unasked.
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
import { RESTRICTED_VALUE_TEXT } from "../domain/fieldCatalogue";
import { isRowVisible } from "../domain/applicationDetailLayout";
import type { DetailCell, DetailSection } from "../domain/applicationDetailLayout";
import type { ApplicationDetail } from "../dataverse/types";
import { formatDate } from "../domain/format";
import styles from "../styles/app.module.css";
import { Definitions, MultilineText, Panel, StateMessage } from "./Panel";
import type { StateMessageTone } from "./Panel";

/**
 * The tone for the non-released states of a redacted row — TAD §8.5 point 1.
 *
 * One function, so the mapping cannot drift between rows and a reader can check it in one
 * place. `withheld` is the filled grey note; `released-empty` is the lighter, unfilled one.
 */
function withheldOrEmptyTone(kind: "withheld" | "released-empty"): StateMessageTone {
  return kind === "withheld" ? "muted" : "quiet";
}

/** One row's value cell. Every branch renders words; none renders an empty cell. */
function CellValue({ cell }: { cell: DetailCell }) {
  switch (cell.kind) {
    case "value":
      return <>{cell.text}</>;
    case "long-text":
      return <MultilineText text={cell.text} />;
    case "restricted":
      return <>{RESTRICTED_VALUE_TEXT}</>;
    case "redacted":
      return cell.state.kind === "released" ? (
        <MultilineText text={cell.state.text} />
      ) : (
        <StateMessage
          heading={cell.state.heading}
          explanation={cell.state.explanation}
          tone={withheldOrEmptyTone(cell.state.kind)}
        />
      );
  }
}

/**
 * One section of the detail screen — a Pack section or the trailing portal-only one — rendered
 * from its spec in `domain/applicationDetailLayout.ts`: the heading as the panel's `<h2>`, each
 * Pack sub-heading as an `<h3>`, and each row as one `<dt>`/`<dd>` pair in spec order.
 *
 * `data-field` carries the row id shared with the field map, so the order test and a reviewer
 * holding the map can both find a row without matching on its label. A row with a `visible`
 * predicate (the reviewer's conditional "other" rows) is omitted when it returns false; every
 * Pack row has none, so a Pack row is always rendered.
 *
 * Each group is a `.detailGroup`, spaced from the previous one by a whole sub-section step,
 * clearly more than the gap between two rows (WI-0008 review, 2026-09-30: "Now it show the
 * section title … directly under the last question"). That was the defect: each Pack sub-heading
 * is its group's first child, so `.fieldHeading:first-child` zeroed its top margin and nothing
 * else separated the groups.
 */
export function DetailSectionPanel({
  section,
  detail,
}: {
  section: DetailSection;
  detail: ApplicationDetail;
}) {
  return (
    <Panel heading={section.heading}>
      {section.groups.map((group, index) => (
        <div
          key={group.heading ?? `group-${String(index)}`}
          className={styles.detailGroup}
          data-section={section.id}
          data-group={group.heading ?? ""}
        >
          {group.heading === null ? null : (
            <h3 className={styles.fieldHeading}>{group.heading}</h3>
          )}
          <dl className={`${styles.definitions} ${styles.packDefinitions}`}>
            {group.rows.filter((row) => isRowVisible(row, detail)).map((row) => (
              <div key={row.id} style={{ display: "contents" }}>
                <dt data-field={row.id}>{row.label}</dt>
                <dd>
                  <CellValue cell={row.cell(detail)} />
                </dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
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
