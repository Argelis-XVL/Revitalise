/**
 * Composition root.
 *
 * Provider order is deliberate:
 *   PowerProvider   — the SDK is configured before anything can call a connector
 *   FluentProvider  — supplies the design tokens the CSS module reads
 *   QueryClient     — caching and retries around the repository
 *   ToastProvider   — needs Fluent's context to render a Toaster
 *   Repository      — the single production implementation, injected once
 */
import { FluentProvider } from "@fluentui/react-components";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { RepositoryProvider } from "./app/RepositoryContext";
import { ToastProvider } from "./app/toast";
import { PowerProvider } from "./PowerProvider";
import { dataverseRepository } from "./dataverse/repository";
import { brandTheme } from "./theme";
import "./styles/print.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // A trustee reading a case in a meeting should not have the ground move under
      // them; a refetch happens on an explicit action, not on window focus.
      refetchOnWindowFocus: false,
      staleTime: 30_000,
      retry: 1,
    },
  },
});

const container = document.getElementById("root");
if (container === null) throw new Error("No #root element to mount into.");

createRoot(container).render(
  <StrictMode>
    <PowerProvider>
      <FluentProvider theme={brandTheme}>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <RepositoryProvider repository={dataverseRepository}>
              <App />
            </RepositoryProvider>
          </ToastProvider>
        </QueryClientProvider>
      </FluentProvider>
    </PowerProvider>
  </StrictMode>,
);
