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
 * A-TR-12 — CLOSED 2026-08-22 (E1). The `./app` export surface of
 * `@microsoft/power-apps` 1.3.0 is exactly `setConfig`, `getContext` and the
 * `IConfig`/`IContext` types — read from the installed
 * `node_modules/@microsoft/power-apps/dist/app/index.d.ts`, which is the package's own
 * declaration of its API and therefore ground truth rather than a guess. There is no
 * `initialize` and nothing else initialiser-shaped, so `setConfig` called once before the
 * tree renders IS the contract, and the shape below was right.
 *
 * Worth keeping for the method rather than the answer: this sat open as an E2 guess since
 * this file was authored, and the register said it needed "the Power Apps host in a
 * browser". It needed one `cat` of a .d.ts already on disk (IMP-0199).
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
