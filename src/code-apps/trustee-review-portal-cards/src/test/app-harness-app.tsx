/**
 * REAL-BROWSER mount of the WHOLE card-layout app on mock data — Playwright and the fidelity
 * screenshots only, never shipped (Vite builds `index.html` only; this is a second entry, like
 * `detail-harness.html`). Design 2.0 Revision 2, TAD trustee-portal-design-2 §13.
 *
 * The mock data mirrors the design kit's own (`ui_kits/trustee-review-portal/Shared.jsx` →
 * `APPLICATIONS`, `RoundOverview.jsx`) so a screenshot of this harness and a screenshot of the kit
 * can be compared side by side: seven applications in round 5, two groups, the same distributions
 * and money figures. It goes through the app's real composition — `App`, the Fluent provider, the
 * query client, the repository context — with an in-memory repository, so every screen renders the
 * same markup it renders in Power Apps. No network, no Power Apps host.
 */
import { FluentProvider } from "@fluentui/react-components";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";
import { App } from "../App";
import { RepositoryProvider } from "../app/RepositoryContext";
import { ToastProvider } from "../app/toast";
import { brandTheme } from "../theme";
import type {
  ApplicationDetail,
  ApplicationSummary,
  Distribution,
  RoundStatisticsResponse,
  TrusteeRepository,
} from "../dataverse/types";
import "../styles/ds-tokens.css";
import "../styles/brand.css";
import "../styles/print.css";

const ROUND = "5";
const TRUSTEE = "11111111-1111-4111-8111-111111111111";

function summary(
  id: string,
  reference: string,
  score: number | null,
  exceptional: number | null,
  start: string,
  end: string,
  status: number,
  group: string | null,
  requested: number | null,
): ApplicationSummary {
  return {
    id,
    reference,
    circumstanceScore: score,
    exceptionalCircumstance: exceptional,
    preferredStart: `${start}T00:00:00Z`,
    preferredEnd: `${end}T00:00:00Z`,
    status,
    reviewRound: ROUND,
    eligibleForRound: true,
    redactionReleased: false,
    groupLinkage: group,
    amountRequested: requested,
  };
}

// Shared.jsx APPLICATIONS + REQUESTED, mapped onto the option sets: 6 Eligible for Panel,
// 3 Borderline, 5 Under Review, 4 Auto-reject; exceptional 1 Palliative care, 2 Carer breakdown.
const APPLICATIONS: ApplicationSummary[] = [
  summary("a1", "REV-2026-1057", 60, 1, "2026-10-05", "2026-10-12", 6, "GRP-014", 1000),
  summary("a2", "REV-2026-1060", 21, null, "2026-10-17", "2026-10-19", 3, null, null),
  summary("a3", "REV-2026-1061", 20, 2, "2026-12-07", "2026-12-14", 5, "GRP-014", 850),
  summary("a4", "REV-2026-1068", 10, null, "2026-10-05", "2026-10-09", 4, null, null),
  summary("a5", "REV-2026-1065", null, null, "2026-11-09", "2026-11-16", 6, "GRP-017", 1200),
  summary("a6", "REV-2026-1072", 44, 2, "2026-11-09", "2026-11-16", 6, "GRP-017", 1100),
  summary("a7", "REV-2026-1074", 38, null, "2026-10-05", "2026-10-12", 5, "GRP-014", 900),
];

function detailOf(row: ApplicationSummary): ApplicationDetail {
  return {
    ...row,
    redactedNarrative: null,
    breakType: 1,
    breakLocation: "Seaside cottage, Northumberland",
    accommodationCost: 850,
    travelCost: 120,
    otherCost: 30,
    additionalAmountRequested: 250,
    costs: 1000,
    redactedCareSupportDescription: null,
    careProvidedType: null,
    careHoursPerWeek: null,
    applicantType: 1,
    incomeBand: 1,
    savingsOver6000: false,
    conditionProfile: [3, 10],
    supportRecipientConditionProfile: null,
    helperDeclarationConsent: null,
    helperDeclarationConsentDate: null,
    redactedUnableToFundExplanation: null,
    redactedOtherCondition: null,
    redactedSupportRecipientOtherCondition: null,
    redactedOtherExceptionalCircumstance: null,
    redactedCareCostsExplanation: null,
    hasEqualityActDisability: true,
    supportRecipientHasEqualityActDisability: null,
    redactedDisabilityImpactDescription: null,
    redactedSupportRecipientDisabilityImpactDescription: null,
    lifeSatisfaction: 2,
    wellbeingAnswers: { 1: 2, 2: 3, 3: 1, 4: 2, 5: 3, 6: 2, 7: 4, 8: 2, 9: 4, 10: 1 },
  };
}

function distribution(population: number, rows: [number, number][]): Distribution {
  return {
    population,
    categories: rows.map(([value, count]) => ({
      value,
      count,
      percentage: Math.round((count / population) * 1000) / 10,
    })),
  };
}

// RoundOverview.jsx's mock figures.
const STATISTICS: RoundStatisticsResponse = {
  status: "ok",
  roundKey: ROUND,
  computedOn: "2026-09-30T15:42:00Z",
  staleAfterSeconds: null,
  populationReceived: 48,
  metrics: {
    applicationsReceived: { count: 48 },
    applicationsPerDay: { value: 0.81, openedOn: "2026-09-01", days: 59 },
    exceptionalCircumstanceMix: distribution(48, [[1, 5], [2, 4], [3, 2], [4, 1]]),
    exceptionalFundingSummary: {
      population: 48,
      anyCount: 12,
      anyPercentage: 25,
      averageAmountRequested: { value: 640, population: 12 },
    },
    breakTypeProfile: {
      population: 48,
      rows: [
        {
          value: 1,
          count: 30,
          averageCost: { value: 1500, population: 30 },
          averageAmountRequested: { value: 1100, population: 30 },
          percentageOfCost: { value: 73.3, population: 30 },
        },
        { value: 2, count: 3, averageCost: null, averageAmountRequested: null, percentageOfCost: null },
      ],
      total: null,
    },
    genderDistribution: distribution(48, [[1, 26], [2, 19], [3, 2], [4, 0], [5, 1]]),
    ageRangeDistribution: distribution(48, [[1, 1], [2, 3], [3, 5], [4, 6], [5, 8], [6, 10], [7, 9], [8, 5], [9, 1]]),
    applicantTypeDistribution: distribution(48, [[1, 29], [2, 12], [3, 7]]),
    ethnicGroupDistribution: distribution(48, [[1, 34], [2, 6], [3, 4], [4, 2], [5, 1], [6, 1]]),
    wellbeingLastYear: {
      questions: [
        ["rev_wellbeinganswer8", [10, 21, 25, 29, 13, 2]],
        ["rev_wellbeinganswer9", [8, 19, 27, 31, 12, 3]],
        ["rev_wellbeinganswer10", [6, 15, 23, 35, 19, 2]],
      ].map(([column, shares]) => ({
        column: column as string,
        population: 48,
        categories: (shares as number[]).map((percentage, index) => ({
          value: index + 1,
          count: Math.round((percentage / 100) * 48),
          percentage,
        })),
      })),
    },
    lifeSatisfactionDistribution: distribution(48, [
      [0, 2], [1, 1], [2, 3], [3, 5], [4, 6], [5, 9], [6, 8], [7, 6], [8, 4], [9, 2], [10, 2],
    ]),
    circumstanceScoreDistribution: distribution(48, [[1, 4], [3, 18], [5, 15], [8, 11]]),
    highHoursCareProportion: null,
    lowLifeSatisfactionProportion: null,
    unableToTakeBreakProportion: null,
    historicApplicationsByMonth: { priorApplicationCount: 715, understatedTotal: false },
  },
};

const repository: TrusteeRepository = {
  listApplicationsForReview: () => Promise.resolve(APPLICATIONS),
  getApplication: (id) => Promise.resolve(detailOf(APPLICATIONS.find((a) => a.id === id) ?? APPLICATIONS[0]!)),
  getReviewForApplication: () =>
    Promise.resolve({
      id: "r1",
      reference: "REV-R-00001",
      round: ROUND,
      panelDate: null,
      staffRecommendation: null,
      trustee1Id: TRUSTEE,
      trustee2Id: "22222222-2222-4222-8222-222222222222",
      verdict1: null,
      verdict2: null,
      notes1: null,
      notes2: null,
      finalisedOn: null,
    }),
  saveVerdict: () => Promise.resolve(),
  getCurrentUser: () =>
    Promise.resolve({
      systemUserId: TRUSTEE,
      fullName: "Emily Sheardown",
      entraObjectId: "44444444-4444-4444-8444-444444444444",
      unresolvedReason: null,
    }),
  getOpenRound: () =>
    Promise.resolve({
      kind: "one",
      round: {
        roundKey: ROUND,
        isOpen: true,
        roundOpenedOn: "2026-09-01T00:00:00Z",
        roundClosedOn: "2026-09-30T00:00:00Z",
        amountCommitted: 50000,
        peopleSupported: 1000,
        individualsSupported: null,
        peopleReachedByGroupGrants: 200,
        grantGivingCapacity: 70000,
        suggestedMaximumSpend: 550000,
        monthlyDisbursement: null,
        remainingLegacyFund: 100000,
        figuresAsAt: "2026-09-26T00:00:00Z",
      },
    }),
  getRoundStatistics: () => Promise.resolve(STATISTICS),
};

const root = document.getElementById("root");
if (root === null) throw new Error("app harness: #root missing");

createRoot(root).render(
  <FluentProvider theme={brandTheme}>
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ToastProvider>
        <RepositoryProvider repository={repository}>
          <App />
        </RepositoryProvider>
      </ToastProvider>
    </QueryClientProvider>
  </FluentProvider>,
);
