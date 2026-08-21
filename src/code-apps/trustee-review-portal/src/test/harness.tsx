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
  ReviewRow,
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
