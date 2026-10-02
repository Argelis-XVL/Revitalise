/**
 * React Query hooks over the repository.
 *
 * `coding-standards.md`: React Query for all Dataverse data fetching, no raw fetch in
 * components. Every hook here goes through `useRepository()`, so a test injects a fake
 * and the component tree is exercised without a connector.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { UseMutationResult, UseQueryResult } from "@tanstack/react-query";
import { useRepository } from "../app/RepositoryContext";
import type {
  ApplicationDetail,
  ApplicationSummary,
  CurrentUser,
  OpenRoundResult,
  ReviewRow,
  RoundStatisticsResponse,
  SaveVerdictInput,
} from "../dataverse/types";

export const queryKeys = {
  applications: ["applications"] as const,
  application: (id: string) => ["application", id] as const,
  review: (applicationId: string) => ["review", applicationId] as const,
  currentUser: ["current-user"] as const,
  openRound: ["open-round"] as const,
  roundStatistics: ["round-statistics"] as const,
};

export function useApplications(): UseQueryResult<ApplicationSummary[], Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.applications,
    queryFn: () => repository.listApplicationsForReview(),
  });
}

export function useApplication(
  applicationId: string | null,
): UseQueryResult<ApplicationDetail | null, Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.application(applicationId ?? ""),
    queryFn: () => repository.getApplication(applicationId ?? ""),
    enabled: applicationId !== null,
  });
}

export function useReview(
  applicationId: string | null,
): UseQueryResult<ReviewRow | null, Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.review(applicationId ?? ""),
    queryFn: () => repository.getReviewForApplication(applicationId ?? ""),
    enabled: applicationId !== null,
  });
}

/**
 * The signed-in user.
 *
 * `retry: false` on purpose. `resolveCurrentUser` never rejects — an unresolved user is
 * a valid result carrying its own reason — so a retry would only delay showing that
 * reason.
 */
export function useCurrentUser(): UseQueryResult<CurrentUser, Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.currentUser,
    queryFn: () => repository.getCurrentUser(),
    retry: false,
    staleTime: Infinity,
  });
}

/**
 * The open round, read directly by the trustee (WBS 6.9, FR-057, FR-063).
 *
 * `staleTime: 0` and `refetchOnMount: "always"` per TAD §5.3: the instruction is live
 * figures, and a trustee returning from a case is opening the screen again. The global
 * default in `main.tsx` is a 30-second stale window, which is right for a case list and
 * wrong here, so both queries on this screen override it.
 *
 * The tuning lever, recorded rather than pre-applied (TAD §5.3): if latency makes this
 * painful in practice, raising `staleTime` is a one-line change, kept honest by the
 * `computedOn` stamp that is on screen either way.
 */
export function useOpenRound(): UseQueryResult<OpenRoundResult, Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.openRound,
    queryFn: () => repository.getOpenRound(),
    staleTime: 0,
    refetchOnMount: "always",
  });
}

/**
 * Every FR-058..FR-062 figure, from `REV | Portal | Round Statistics` (WBS 6.9).
 *
 * `retry: false`, deliberately, against the global default of one retry. Two reasons, and
 * the second is the real one: this is a flow invocation that reads the whole round's rows,
 * so a retry doubles the wait before a trustee is told anything; and TAD §5.3 already
 * names the explicit retry — a visible **Refresh figures** control. A silent automatic
 * retry competes with it and makes the screen slower to be honest.
 *
 * A non-`ok` `status` is a successful RESULT, not an error, so it never reaches this
 * setting at all — the diagnostic wording for it is chosen in `domain/landing.ts`.
 */
export function useRoundStatistics(): UseQueryResult<RoundStatisticsResponse, Error> {
  const repository = useRepository();
  return useQuery({
    queryKey: queryKeys.roundStatistics,
    queryFn: () => repository.getRoundStatistics(),
    staleTime: 0,
    refetchOnMount: "always",
    retry: false,
  });
}

export function useSaveVerdict(
  applicationId: string,
): UseMutationResult<void, Error, SaveVerdictInput> {
  const repository = useRepository();
  const client = useQueryClient();
  return useMutation({
    mutationFn: (input: SaveVerdictInput) => repository.saveVerdict(input),
    onSuccess: async () => {
      // Re-read the row rather than patching the cache: what Dataverse stored is the
      // only version that matters, and a business rule or plugin may have changed it.
      await client.invalidateQueries({ queryKey: queryKeys.review(applicationId) });
    },
  });
}
