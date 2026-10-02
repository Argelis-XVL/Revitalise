/**
 * Error and confirmation messages.
 *
 * `knowledge/technology/code-apps.md` → Error Handling: every connector error is
 * surfaced through a toast, never a blank screen. Fluent's `Toaster` renders into an
 * `aria-live` region, which is also what WCAG 4.1.3 asks for on a status message — so
 * "a verdict was saved" is announced, not only drawn (TAD §8).
 */
import {
  Toast,
  ToastBody,
  ToastTitle,
  Toaster,
  useId,
  useToastController,
} from "@fluentui/react-components";
import { createContext, useCallback, useContext, useMemo } from "react";
import type { ReactNode } from "react";

export interface ToastApi {
  /** A failure the trustee needs to know about. Assertive: it interrupts. */
  showError: (title: string, detail?: string) => void;
  /** A confirmation. Polite: it waits for a gap in what the reader is doing. */
  showSuccess: (title: string, detail?: string) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const toasterId = useId("rev-toaster");
  const { dispatchToast } = useToastController(toasterId);

  const showError = useCallback(
    (title: string, detail?: string) => {
      dispatchToast(
        <Toast>
          <ToastTitle>{title}</ToastTitle>
          {detail === undefined ? null : <ToastBody>{detail}</ToastBody>}
        </Toast>,
        { intent: "error", politeness: "assertive", timeout: -1 },
      );
    },
    [dispatchToast],
  );

  const showSuccess = useCallback(
    (title: string, detail?: string) => {
      dispatchToast(
        <Toast>
          <ToastTitle>{title}</ToastTitle>
          {detail === undefined ? null : <ToastBody>{detail}</ToastBody>}
        </Toast>,
        { intent: "success", politeness: "polite" },
      );
    },
    [dispatchToast],
  );

  const api = useMemo<ToastApi>(() => ({ showError, showSuccess }), [showError, showSuccess]);

  return (
    <ToastContext.Provider value={api}>
      {/* An error toast has timeout -1: it stays until dismissed, because a failed save
          that vanishes on its own is a failure the trustee never learns about. */}
      <Toaster toasterId={toasterId} position="top-end" data-print="hide" />
      {children}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  const api = useContext(ToastContext);
  if (api === null) throw new Error("useToast was called outside a ToastProvider.");
  return api;
}
