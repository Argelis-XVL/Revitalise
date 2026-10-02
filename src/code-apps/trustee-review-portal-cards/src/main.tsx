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
// Screen first, then print. brand.css holds the brand values Fluent's one-ramp theme has no
// token for — the heading font, the 44px title, and the secondary/accent colours (NFR-026).
//
// ds-tokens.css publishes the design system's token vocabulary that `components/ds/*` and
// `styles/ds.module.css` read (ADR-033/034, with ADR-037's five contrast corrections applied).
// ORDER MATTERS: tokens before the print reset, so `print.css`'s `@media print` block is still
// the last word on paper. `src/test/harness.tsx` imports the same three files in the same
// change, so the two module graphs cannot diverge (A-R38).
import "./styles/ds-tokens.css";
import "./styles/brand.css";
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
