// ESLint flat config.
//
// DEVIATION from knowledge/technology/coding-standards.md, which names
// `src/code-apps/<slug>/.eslintrc.json`: ESLint 9 removed `.eslintrc.*` support
// entirely, so the eslintrc form cannot be used with any supported ESLint. Recorded
// rather than silently changed.
import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    // Generator output from `pac code add-data-source`. Not hand-edited, and
    // src/generated/services/MicrosoftDataverseService.ts does not parse.
    ignores: ["dist/**", "coverage/**", "src/generated/**", ".power/**"],
  },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  // `configs.flat["recommended-latest"]`, not `configs["recommended-latest"]`: in
  // eslint-plugin-react-hooks 7.1.1 the top-level configs are still eslintrc-shaped
  // (`plugins` as an array of strings), which ESLint 10 rejects outright with
  // "A config object has a 'plugins' key defined as an array of strings". The flat
  // variants live one level down.
  reactHooks.configs.flat["recommended-latest"],
  {
    languageOptions: {
      globals: { ...globals.browser },
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // coding-standards.md: "No `any` types — use `unknown` with type guards".
      "@typescript-eslint/no-explicit-any": "error",
      // coding-standards.md: "No console.log in production code".
      "no-console": ["error", { allow: ["warn", "error"] }],
      "@typescript-eslint/consistent-type-imports": "error",
    },
  },
  {
    files: ["**/*.test.ts", "**/*.test.tsx", "src/test/**"],
    rules: {
      "@typescript-eslint/no-non-null-assertion": "off",
    },
  },
  {
    files: ["*.config.ts", "*.config.js"],
    ...tseslint.configs.disableTypeChecked,
  },
);
