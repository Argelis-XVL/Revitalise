/**
 * Power Apps SDK initialisation.
 *
 * `knowledge/technology/code-apps.md` says to "keep the generated `PowerProvider.tsx`
 * wrapping the component tree in main.tsx". There is no generated one:
 * `pac code init --displayName "<name>"` on pac 2.4.1 exits 0 and creates exactly ONE
 * file, `power.config.json`. It scaffolds no React, no package.json and no
 * PowerProvider. Verified 2026-08-21 by running it. So this file is hand-authored, and
 * `code-apps.md`'s claim that init "wires the dev script" is wrong for this version.
 *
 * A-TR-12 (GUESS, E2) — what initialisation the host actually requires. The
 * public surface of `@microsoft/power-apps` 1.3.0 offers `setConfig(config)` and
 * `getContext()`, and nothing else that looks like an initialiser; `setConfig` is
 * therefore called once before the tree renders. Cheapest verification: compare against
 * a Microsoft-authored Code App template's own PowerProvider.tsx, or run this app in the
 * host and confirm connector calls resolve.
 *
 * Deliberately NOT gating render on `getContext()`: identity is resolved through the
 * repository as a normal query, so a host that cannot answer produces a readable
 * in-page state and a toast rather than a blank screen (`code-apps.md` → Error
 * Handling). A provider that awaits an unverified promise before its first paint is the
 * blank screen.
 */
import { setConfig } from "@microsoft/power-apps/app";
import type { ReactNode } from "react";

let configured = false;

function configureOnce(): void {
  if (configured) return;
  configured = true;
  setConfig({});
}

export function PowerProvider({ children }: { children: ReactNode }) {
  configureOnce();
  return <>{children}</>;
}

/** Exposed for tests only, so the module-level guard cannot leak between cases. */
export function __resetPowerProviderForTests(): void {
  configured = false;
}
