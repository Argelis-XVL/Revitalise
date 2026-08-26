/**
 * Test harness: renders real components against a FAKE repository.
 *
 * What this proves and what it does not, stated here so no test result is read as more
 * than it is: these tests exercise this app's own logic and markup. They prove nothing
 * whatsoever about what the Dataverse connector returns, because the connector is not
 * involved. `IMP-0111` is the trap to avoid — a test written from the same assumption as
 * the code locks the assumption in rather than verifying it. So no test here asserts a
 * platform contract; the platform contracts are all in the assumptions register instead.
 */
import { FluentProvider, webLightTheme } from "@fluentui/react-components";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { RenderResult } from "@testing-library/react";
import type { ReactElement } from "react";
import { RepositoryProvider } from "../app/RepositoryContext";
import { ToastProvider } from "../app/toast";
import type {
  ApplicationDetail,
  ApplicationSummary,
  CurrentUser,
  Distribution,
  ReviewRow,
  RoundFinance,
  RoundStatisticsMetrics,
  RoundStatisticsResponse,
  SaveVerdictInput,
  TrusteeRepository,
} from "../dataverse/types";

export const TRUSTEE_1_ID = "11111111-1111-4111-8111-111111111111";
export const TRUSTEE_2_ID = "22222222-2222-4222-8222-222222222222";
export const OTHER_USER_ID = "33333333-3333-4333-8333-333333333333";
export const APPLICATION_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
export const REVIEW_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

export function makeSummary(overrides: Partial<ApplicationSummary> = {}): ApplicationSummary {
  return {
    id: APPLICATION_ID,
    reference: "REV-2026-001",
    circumstanceScore: 42,
    region: { kind: "known", value: 9 }, // South West

    preferredStart: "2026-10-05T00:00:00Z",
    preferredEnd: "2026-10-12T00:00:00Z",
    status: 6,
    reviewRound: "2026-Q4",
    eligibleForRound: true,
    redactionReleased: false,
    ...overrides,
  };
}

export function makeDetail(overrides: Partial<ApplicationDetail> = {}): ApplicationDetail {
  return {
    ...makeSummary(),
    redactedNarrative: null,
    scoreBreakdown: "Wellbeing 20\nCare hours 12\nFinancial 10",
    breakType: null,
    breakLocation: "Coastal, Devon",
    providerPreference: "Accessible cottage",
    amountRequested: 1200,
    costs: 1500,
    redactedCareSupportDescription: null,
    redactedCareProvidedExample: null,
    redactedOtherCareProvidedType: null,
    ...overrides,
  };
}

export function makeReview(overrides: Partial<ReviewRow> = {}): ReviewRow {
  return {
    id: REVIEW_ID,
    reference: "REV-R-00001",
    round: "2026-Q4",
    panelDate: "2026-10-01T00:00:00Z",
    staffRecommendation: "Staff support this application.",
    trustee1Id: TRUSTEE_1_ID,
    trustee2Id: TRUSTEE_2_ID,
    verdict1: null,
    verdict2: null,
    notes1: null,
    notes2: null,
    finalisedOn: null,
    ...overrides,
  };
}

export function makeUser(overrides: Partial<CurrentUser> = {}): CurrentUser {
  return {
    systemUserId: TRUSTEE_1_ID,
    fullName: "Kevin Trustee",
    entraObjectId: "44444444-4444-4444-8444-444444444444",
    unresolvedReason: null,
    ...overrides,
  };
}

/** The round key both landing-screen fakes below share, so reconciliation passes. */
export const OPEN_ROUND_KEY = "2026-Q4";

/** One `rev_roundfinance` row with every FR-063 measure entered (WBS 6.9). */
export function makeRoundFinance(overrides: Partial<RoundFinance> = {}): RoundFinance {
  return {
    roundKey: OPEN_ROUND_KEY,
    isOpen: true,
    roundOpenedOn: "2026-08-01T00:00:00Z",
    roundClosedOn: null,
    amountCommitted: 41000,
    peopleSupported: 128,
    individualsSupported: 96,
    peopleReachedByGroupGrants: 32,
    grantGivingCapacity: 250000,
    suggestedMaximumSpend: 60000,
    monthlyDisbursement: 20000,
    remainingLegacyFund: 175000,
    figuresAsAt: "2026-08-20T00:00:00Z",
    ...overrides,
  };
}

function distribution(
  population: number,
  categories: [number, number, number | null][],
): Distribution {
  return {
    population,
    categories: categories.map(([value, count, percentage]) => ({ value, count, percentage })),
  };
}

/**
 * Every metric populated — the state the flow's LATER versions are expected to reach.
 *
 * Deliberately not the default below. TAD §3.3's first version emits
 * `applicationsReceived` and `null` for everything else, so the default fake is that
 * state and a test wanting figures asks for them explicitly. A default that showed
 * everything would have hidden the null-handling the screen has to get right on day one.
 */
export function makeAllMetrics(
  overrides: Partial<RoundStatisticsMetrics> = {},
): RoundStatisticsMetrics {
  return {
    applicationsReceived: { count: 434 },
    applicationsPerDay: { value: 14.47, openedOn: "2026-08-01", days: 30 },
    exceptionalCircumstanceMix: distribution(434, [
      [1, 6, 1.4],
      [2, 18, 4.1],
    ]),
    exceptionalFundingSummary: {
      population: 434,
      anyCount: 41,
      anyPercentage: 9.4,
      averageAmountRequested: 780,
    },
    breakTypeProfile: {
      population: 434,
      rows: [
        {
          value: 1,
          count: 300,
          averageCost: 1500,
          averageAmountRequested: 1100,
          percentageOfCost: 73.3,
        },
        {
          value: 2,
          count: 134,
          averageCost: 400,
          averageAmountRequested: 300,
          percentageOfCost: 75,
        },
      ],
      total: {
        count: 434,
        averageCost: 1160,
        averageAmountRequested: 853,
        percentageOfCost: 73.5,
      },
    },
    genderDistribution: distribution(434, [
      [1, 260, 59.9],
      [2, 150, 34.6],
      [3, 24, 5.5],
    ]),
    ageRangeDistribution: distribution(434, [
      [5, 120, 27.6],
      [6, 200, 46.1],
    ]),
    applicantTypeDistribution: distribution(434, [
      [1, 210, 48.4],
      [2, 180, 41.5],
      [3, 44, 10.1],
    ]),
    ethnicGroupDistribution: null,
    wellbeingLastYear: {
      questions: [
        {
          column: "rev_wellbeinganswer8",
          population: 400,
          categories: [
            { value: 1, count: 100, percentage: 25 },
            { value: 4, count: 300, percentage: 75 },
          ],
        },
      ],
    },
    lifeSatisfactionDistribution: distribution(420, [
      [2, 100, 23.8],
      [7, 320, 76.2],
    ]),
    highHoursCareProportion: null,
    lowLifeSatisfactionProportion: null,
    unableToTakeBreakProportion: null,
    ...overrides,
  };
}

/**
 * The response the flow's FIRST version actually produces: `status: "ok"`,
 * `applicationsReceived`, and `null` for every other metric (TAD §3.3).
 */
export function makeRoundStatistics(
  overrides: Partial<RoundStatisticsResponse> = {},
): RoundStatisticsResponse {
  return {
    status: "ok",
    roundKey: OPEN_ROUND_KEY,
    computedOn: "2026-08-25T13:05:11Z",
    populationReceived: 434,
    metrics: {
      ...makeAllMetrics(),
      applicationsPerDay: null,
      exceptionalCircumstanceMix: null,
      exceptionalFundingSummary: null,
      breakTypeProfile: null,
      genderDistribution: null,
      ageRangeDistribution: null,
      applicantTypeDistribution: null,
      wellbeingLastYear: null,
      lifeSatisfactionDistribution: null,
    },
    ...overrides,
  };
}

export interface FakeRepository extends TrusteeRepository {
  saved: SaveVerdictInput[];
}

/**
 * A repository whose every method is overridable. Defaults are the boring happy path so
 * each test states only what it is actually about.
 */
export function makeRepository(overrides: Partial<TrusteeRepository> = {}): FakeRepository {
  const saved: SaveVerdictInput[] = [];
  const base: TrusteeRepository = {
    listApplicationsForReview: () => Promise.resolve([makeSummary()]),
    getApplication: () => Promise.resolve(makeDetail()),
    getReviewForApplication: () => Promise.resolve(makeReview()),
    saveVerdict: (input) => {
      saved.push(input);
      return Promise.resolve();
    },
    getCurrentUser: () => Promise.resolve(makeUser()),
    getOpenRound: () => Promise.resolve({ kind: "one", round: makeRoundFinance() }),
    getRoundStatistics: () => Promise.resolve(makeRoundStatistics()),
  };
  return { ...base, ...overrides, saved };
}

export function renderWithProviders(
  ui: ReactElement,
  repository: TrusteeRepository,
): RenderResult {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <FluentProvider theme={webLightTheme}>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <RepositoryProvider repository={repository}>{ui}</RepositoryProvider>
        </ToastProvider>
      </QueryClientProvider>
    </FluentProvider>,
  );
}
