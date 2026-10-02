/**
 * Supplies the repository to the tree.
 *
 * The point of the indirection is testability: every test renders the real components
 * against a fake `TrusteeRepository` and never touches the connector. The app has
 * exactly one production implementation, injected once at the root.
 */
import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { TrusteeRepository } from "../dataverse/types";

const RepositoryContext = createContext<TrusteeRepository | null>(null);

export function RepositoryProvider({
  repository,
  children,
}: {
  repository: TrusteeRepository;
  children: ReactNode;
}) {
  return <RepositoryContext.Provider value={repository}>{children}</RepositoryContext.Provider>;
}

export function useRepository(): TrusteeRepository {
  const repository = useContext(RepositoryContext);
  if (repository === null) {
    throw new Error("useRepository was called outside a RepositoryProvider.");
  }
  return repository;
}
