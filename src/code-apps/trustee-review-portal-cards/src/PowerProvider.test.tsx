/**
 * SDK initialisation.
 *
 * Two things are worth pinning: the SDK is configured before the tree renders, and it is
 * configured ONCE however many times the provider mounts (React 18 StrictMode mounts
 * every component twice in development).
 */
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const setConfig = vi.fn();
vi.mock("@microsoft/power-apps/app", () => ({
  setConfig: (config: unknown) => setConfig(config) as unknown,
}));

const { PowerProvider, __resetPowerProviderForTests } = await import("./PowerProvider");

beforeEach(() => {
  setConfig.mockReset();
  __resetPowerProviderForTests();
});

describe("PowerProvider", () => {
  it("configures the SDK and renders its children", () => {
    render(
      <PowerProvider>
        <p>child</p>
      </PowerProvider>,
    );
    expect(setConfig).toHaveBeenCalledTimes(1);
    expect(screen.getByText("child")).toBeInTheDocument();
  });

  it("configures the SDK only once across repeated mounts", () => {
    render(
      <PowerProvider>
        <p>a</p>
      </PowerProvider>,
    );
    render(
      <PowerProvider>
        <p>b</p>
      </PowerProvider>,
    );
    expect(setConfig).toHaveBeenCalledTimes(1);
  });

  it("renders children rather than gating the first paint on the host", () => {
    // Deliberate: identity is resolved as a normal query, so a host that cannot answer
    // produces a readable in-page state instead of a blank screen. A provider that
    // awaited an unverified promise before its first paint IS the blank screen.
    render(
      <PowerProvider>
        <p>visible immediately</p>
      </PowerProvider>,
    );
    expect(screen.getByText("visible immediately")).toBeInTheDocument();
  });
});
