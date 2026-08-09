# Power Apps Code Apps — Design Conventions

> Power Apps Code Apps are code-first apps (React + Vite + TypeScript) that run on the
> Power Apps host: the platform provides authentication, connector access, and governance;
> you provide the code. They are the **preferred UI choice** over Canvas Apps when custom
> or complex UX is required.
>
> ⚠️ Code Apps are **not** PCF controls and **not** web resources — do not use
> `pac pcfpush` or copy build output into `WebResources/`. The toolchain is `pac code`.

## When to Use a Code App vs. MDA vs. Canvas App

| Scenario | Preferred Choice |
|---|---|
| Process-driven internal workflow (cases, tasks, approvals) | Model-Driven App |
| Custom UX, complex layouts, or code-heavy interactions | **Power Apps Code App** ✅ |
| Simple data entry form for external or field users | Power Apps Code App (first preference) or Canvas App |
| Quick prototype / no TypeScript experience on team | Canvas App (fallback only) |

> Licensing note: Code Apps require Power Apps Premium licences for end users —
> confirm licensing before choosing this path in the TAD.

## Toolchain

| Command | Purpose |
|---|---|
| `pac code init --displayName "<App Name>"` | Initialise the app (creates `power.config.json`, wires the dev script) |
| `pac code add-data-source -a <apiId> -c <connectionId>` | Generate typed models/services for a connector (Dataverse, SharePoint, Office 365, …) |
| `pac code push` | Build and publish the app to the connected environment |
| `npm run dev` | Local dev — runs `pac code run` alongside the Vite dev server; test via the Power Apps player URL it prints |

Requires PAC CLI ≥ 1.44 and Node LTS. The Power Apps SDK (`@microsoft/power-apps`)
must be initialised before the app renders — keep the generated `PowerProvider.tsx`
wrapping the component tree in `main.tsx`.

## Project Structure

Each Code App lives in `src/code-apps/<app-slug>/`:

```
src/code-apps/<app-slug>/
├── src/
│   ├── components/        ← React components
│   ├── hooks/             ← custom hooks wrapping generated services
│   ├── pages/             ← route-level components
│   ├── generated/         ← models/services from `pac code add-data-source` (committed)
│   ├── types/             ← additional TypeScript types
│   ├── PowerProvider.tsx  ← Power Apps SDK initialisation (generated)
│   ├── App.tsx
│   └── main.tsx
├── power.config.json      ← created by `pac code init` (committed)
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Data Access & Auth

- All data access goes through **connector data sources** added with
  `pac code add-data-source` — the generated services are typed against the live schema.
- Authentication is the **signed-in user's identity**, brokered by the Power Apps host
  and the user's connections. No MSAL code, no tokens, no credentials in the app for
  standard connectors (`C-TECH-048`).
- Because calls run as the user, **Dataverse security roles and column security apply
  automatically** — never build client-side authorisation logic to compensate for a
  missing role design (see `security-model.md`).
- Calling a custom external API is the only case that needs an app registration +
  MSAL — see `knowledge/technology/entra-id.md`, and isolate that code in one module.

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| App folder name | `<app-slug>` (kebab-case) | `case-portal`, `onboarding-app` |
| App display name | `[PREFIX] <App Name>` | `PROJ Case Portal` |
| React component files | PascalCase `.tsx` | `CaseDetailPanel.tsx` |
| Hook files | camelCase `.ts`, `use` prefix | `useCases.ts` |
| Type files | camelCase `.ts` | `caseTypes.ts` |
| Route paths | kebab-case | `/case-detail/:id` |

## Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    host: "::",
    port: 3000,          // the Power Apps local host expects port 3000
  },
  build: {
    outDir: "dist",
    sourcemap: false,    // never ship sourcemaps to a shared environment
  },
});
```

## ALM — How a Code App Moves Through Environments

1. **Dev**: `pac code push` publishes the app to the Dev environment for iteration.
2. **Solution**: add the code app to the feature solution in Dev — it is a solution
   component and travels in the **managed solution** through Test/Acc/Prd like every
   other component. Connection references and environment variables resolve per
   environment via deployment settings (see `build-and-deploy.md`).
3. **Fallback**: if solution support for code apps is not yet enabled on your tenant,
   the pipeline `post_deploy` block runs `pac code push` against each target
   environment using the deployment service principal — document this deviation in
   the TAD §9 deployment topology.
4. **Sharing**: share the app with the persona's **Entra security group** as a
   `post_deploy` step (see `security-model.md` → App Access) — never with individual
   users in Test/Acc/Prd.

## Design Rules

### State Management
- Use **React Query** (`@tanstack/react-query`) around the generated connector
  services for caching, retries, and invalidation
- Avoid global state libraries (Redux, Zustand) unless the app complexity requires them
- Keep component state local; lift to context only when shared across multiple subtrees

### TypeScript
- Strict mode enabled (`"strict": true` in `tsconfig.json`)
- No `any` types — use `unknown` with type guards instead
- Do not hand-edit files in `src/generated/` — re-run `pac code add-data-source` on schema change

### Styling
- Use **CSS Modules** or **Tailwind CSS** — one approach per project, set in `stack-overview.md`
- No inline styles except for dynamic/computed values
- Fluent UI v9 (`@fluentui/react-components`) for components that must match Power Platform visual language

### Accessibility
- All Code Apps must meet WCAG 2.1 Level AA
- Use semantic HTML elements; ARIA attributes only when native semantics are insufficient
- Keyboard navigation must work end-to-end before code review

### Error Handling
- All connector calls wrapped in try/catch; errors surfaced to the user via a
  toast/notification, not a blank screen
- Log errors to `[prefix]_flowexceptionlog` (via a Power Automate cloud flow) for
  server-side traceability

## Testing

See `knowledge/technology/testing-tools.md` for the full test stack.

Summary:
- **Unit**: Vitest + React Testing Library — test components in isolation with mocked
  generated services
- **Integration**: Vitest against a real Test environment
- **E2E**: Playwright — automate the full app flow in a browser against the Test environment
