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
  ReviewRow,
  SaveVerdictInput,
} from "../dataverse/types";

export const queryKeys = {
  applications: ["applications"] as const,
  application: (id: string) => ["application", id] as const,
  review: (applicationId: string) => ["review", applicationId] as const,
  currentUser: ["current-user"] as const,
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
