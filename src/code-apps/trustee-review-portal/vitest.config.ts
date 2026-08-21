import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Vitest loads vitest.config.ts in preference to vite.config.ts and does NOT merge
// the two, so the react plugin is declared here as well. Deliberate duplication:
// vite.config.ts is kept in exactly the shape code-apps.md prescribes.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: false,
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    server: {
      deps: {
        // `tabster` (Fluent UI v9's focus-management layer) publishes a CJS `main`, an
        // ESM `module`, and no `exports` map, and its SWC-generated CJS defeats Node's
        // named-export detection:
        //
        //   $ node --input-type=module -e "console.log(Object.keys(await import('tabster')))"
        //   [ '__esModule', 'default', 'module.exports' ]
        //
        // Externalised, that fails EVERY test that renders any Fluent component with
        // "The requested module 'tabster' does not provide an export named
        // 'createTabster'". Inlining `@fluentui/*` — the IMPORTER, not just tabster —
        // makes Vite transform the import and resolve the ESM build. Vite's dev and
        // build paths already do this, which is why only the test runner broke.
        //
        // NOTE the un-anchored regex: `inline` matches the resolved module PATH, so an
        // anchored `/^@fluentui\//` never matches an absolute node_modules path. That
        // cost two rounds here.
        inline: [/@fluentui\//],
      },
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json-summary", "lcov"],
      reportsDirectory: "./coverage",
      // Scope is `src/code-apps/<slug>/src/**` per
      // knowledge/technology/coding-standards.md -> "Test Coverage".
      include: ["src/**"],
      // Exclusions, each with a reason (the TypeScript analogue of
      // config/coverage-exclusions.json's priced-exclusion rule):
      exclude: [
        // Generator output from `pac code add-data-source`. Never hand-edited,
        // never imported by this app (see src/dataverse/README.md), and one of
        // its files does not parse at all.
        "src/generated/**",
        // Test harness itself.
        "src/test/**",
        "src/**/*.test.ts",
        "src/**/*.test.tsx",
        // Bootstrap: composition root with no branching. Exercised only by
        // loading the app in the Power Apps host, which is a V4/V5 step.
        "src/main.tsx",
        // Type-only module: it compiles to an empty module, so every line v8 counts as
        // "uncovered" is an interface or a comment. Including it measures documentation
        // density, not test coverage.
        "src/dataverse/types.ts",
      ],
      thresholds: {
        statements: 80,
        lines: 80,
      },
    },
  },
});
