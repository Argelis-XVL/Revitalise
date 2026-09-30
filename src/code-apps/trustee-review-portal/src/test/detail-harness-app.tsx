/**
 * REAL-BROWSER mount for the application detail screen's sections — Playwright only, never
 * shipped. WI-0005 (2026-09-30).
 *
 * `detail-harness.html` is a second Vite entry beside `visual-harness.html`: not referenced by
 * `index.html`, and not an input of the production build (Vite builds `index.html` only), so
 * nothing here reaches `dist/`.
 *
 * Why it exists: WI-0005 made the Trustee Pack's own questions the row labels (the longest is
 * 87 characters) and gave the rows their own grid tracks (`app.module.css`'s `.packDefinitions`).
 * Whether a long label wraps inside its track, and whether the page scrolls sideways on a
 * phone, is geometry, and jsdom computes none (`C-TECH-078`). So this mounts every section of
 * `APPLICATION_DETAIL_LAYOUT`, inside the app's own `.page` container and stylesheets, with
 * long real-shaped values, and `application-detail-layout.visual.spec.ts` measures it.
 *
 * Rendered twice: once released (long free text in the value cells), once withheld (a note
 * box in every redacted cell), because the two put different content in the same track.
 */
import { createRoot } from "react-dom/client";
import { DetailSectionPanel } from "../components/CasePanels";
import { APPLICATION_DETAIL_LAYOUT } from "../domain/applicationDetailLayout";
import type { ApplicationDetail } from "../dataverse/types";
import styles from "../styles/app.module.css";
import "../styles/ds-tokens.css";
import "../styles/brand.css";

const LONG =
  "This break is a vital escape from the cycle of treatments, pain, and side effects that " +
  "have kept me confined to my home. It is a chance to reset after so much hardship, and to " +
  "spend time with my family in a way that my illness has not allowed.";

function fixture(released: boolean, id: string): ApplicationDetail {
  return {
    id,
    reference: "REV-2026-001",
    circumstanceScore: 59,
    exceptionalCircumstance: 4, // "Other" — so D11a renders and is measured
    preferredStart: "2026-08-01T00:00:00Z",
    preferredEnd: "2026-08-11T00:00:00Z",
    status: 6,
    reviewRound: "2026-Q4",
    eligibleForRound: true,
    redactionReleased: released,
    groupLinkage: null,
    amountRequested: 500,
    redactedNarrative: LONG,
    breakType: 1,
    breakLocation: "Alarcha Hotels & Resort 5 * Side, Antalya, a long unbroken-location-name-to-wrap",
    accommodationCost: 4000,
    travelCost: 2000,
    otherCost: 1000,
    additionalAmountRequested: 250,
    costs: 7000,
    redactedCareSupportDescription: LONG,
    careProvidedType: [1, 2, 4],
    careHoursPerWeek: 3,
    applicantType: 1,
    incomeBand: 1,
    savingsOver6000: false,
    conditionProfile: [3, 8, 7, 10], // includes "Other" — so A3a renders
    supportRecipientConditionProfile: [2, 10], // and A3b
    helperDeclarationConsent: null,
    helperDeclarationConsentDate: null,
    redactedUnableToFundExplanation: LONG,
    redactedOtherCondition: LONG,
    redactedSupportRecipientOtherCondition: LONG,
    redactedOtherExceptionalCircumstance: LONG,
    redactedCareCostsExplanation: LONG,
    hasEqualityActDisability: true,
    supportRecipientHasEqualityActDisability: false,
    redactedDisabilityImpactDescription: LONG,
    redactedSupportRecipientDisabilityImpactDescription: null,
    lifeSatisfaction: 1,
    wellbeingAnswers: { 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1 },
  };
}

const root = document.getElementById("root");
if (root === null) throw new Error("detail harness: #root missing");

createRoot(root).render(
  <div className={styles.page}>
    <main id="main">
      <div id="released">
        {APPLICATION_DETAIL_LAYOUT.map((section) => (
          <DetailSectionPanel key={section.id} section={section} detail={fixture(true, "r")} />
        ))}
      </div>
      <div id="withheld">
        {APPLICATION_DETAIL_LAYOUT.map((section) => (
          <DetailSectionPanel key={section.id} section={section} detail={fixture(false, "w")} />
        ))}
      </div>
      {/* A marker Playwright waits on so it never measures mid-mount. */}
      <div data-testid="harness-ready">ready</div>
    </main>
  </div>,
);
