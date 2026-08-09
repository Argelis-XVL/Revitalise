# Coding Standards — Power Platform

> 📝 Replace `[prefix]` and `[PREFIX]` throughout with your project's publisher prefix.
> Set the prefix in `knowledge/technology/stack-overview.md` → Publisher Convention.

## Naming

| Element | Convention | Example |
|---|---|---|
| Solution | `[PREFIX]_<Domain>` | `PROJ_CaseManagement`, `HR_Onboarding` |
| Table schema name | `[prefix]_<entityname>` | `[prefix]_case`, `[prefix]_party` |
| Column schema name | `[prefix]_<columnname>` | `[prefix]_status`, `[prefix]_assignedto` |
| Flow name | `[PREFIX] <Domain> - <Action> - <Trigger>` | `[PREFIX] Cases - Escalate - On Status Change` |
| Web resource | `[prefix]_/<feature>/<filename>` | `[prefix]_/cases/statusValidation.js` |
| Code App folder | `<app-slug>` (kebab-case) | `case-portal`, `onboarding-app` |
| Code App solution component | `[PREFIX]_<AppSlug>` | `PROJ_CasePortal` |
| Code App env var | `VITE_<SCREAMING_SNAKE>` | `VITE_DATAVERSE_URL`, `VITE_API_BASE` |
| Environment variable | `[prefix]_<SettingName>` (PascalCase after prefix) | `[prefix]_ApiBaseUrl`, `[prefix]_NotifyChannel` |
| Connection reference | `[prefix]_Shared<Service>` | `[prefix]_SharedDataverse`, `[prefix]_SharedEmail` |
| Cloud flow action names | Descriptive verb-noun | "Get Active Cases", "Update Record Status" |

## Solution Layering

- One solution per functional domain
- Shared base components (lookup tables, base security roles) in `[PREFIX]_Base` solution
- Never create cross-solution dependencies at runtime — only `[PREFIX]_Base` may be a dependency

## Power Automate

- All action names in English, verb-noun format, no abbreviations
- Every flow has a description explaining its purpose, trigger, and owner team
- Use **variables** at the top of the flow for all values referenced more than once
- Compose actions for data transformations instead of inline expressions where readability suffers
- No plain-text passwords or secrets in flow inputs — use environment variables or Key Vault

## TypeScript / React (Power Apps Code Apps)

- **TypeScript strict mode** on for all Code Apps (`"strict": true` in `tsconfig.json`)
- No `any` types — use `unknown` with type guards
- ESLint + Prettier enforced; config in `src/code-apps/<slug>/.eslintrc.json`
- One component per file; filename matches the exported component name (PascalCase)
- React Query for all Dataverse data fetching — no raw `fetch` calls in components
- Fluent UI v9 for Platform-aligned components; CSS Modules or Tailwind for layout/custom styles (set once per project)
- No `console.log` in production code — use the error logging flow instead
- All Dataverse calls wrapped in try/catch with user-visible error feedback

## JavaScript Web Resources (MDA only)

- ESLint enforced; config in `src/.eslintrc.json`
- No `console.log` in production code
- All Xrm API calls wrapped in try/catch with user-visible error handling
- Functions documented with JSDoc headers
- One web resource per feature concern — no monolithic files
- Prefer a Code App over a complex JS web resource for any new UX

## Business Rules

- Use descriptive condition and action names
- Document the FR ID this rule implements in the description field
- Rules scoped to **Entity** scope only (not All Forms) unless cross-form enforcement is required

## Version Control

- Branch naming: `feature/<slug>`, `fix/<slug>`, `release/<version>`
- Commit messages: `[<ticket-id>] <imperative verb> <what>` e.g. `[PROJ-142] Add status column to Case table`
- Never commit `.zip` files — only unpacked source
- `build/exports/` and `build/artifacts/` are gitignored

## What Never Goes in Source Control

- `.zip` solution files (build outputs)
- Client secrets, passwords, API keys
- Personal connection configurations
- Environment-specific URLs hardcoded in flows
