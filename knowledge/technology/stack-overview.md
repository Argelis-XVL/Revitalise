# Stack Overview — Power Platform

**Populated 2026-08-19** from the shipped solution's own `Other/Solution.xml`. Until then the
Publisher Convention block below still read `[Your Project Name]` / `[prefix]` under a banner
saying *"Set your publisher prefix once — agents use it for all schema name generation"* —
while roughly 200 `rev_`-prefixed components had already shipped. This is `architect-agent`'s
first loaded file on every activation.

## Platform Components in Use

| Component | Purpose | In Scope |
|---|---|---|
| Dataverse | Relational data store, business rules, column security | ✅ |
| Model-Driven Apps (MDA) | Process-driven internal UIs (cases, tasks, admin) | ✅ |
| Power Apps Code Apps | Custom UIs built with React + Vite + TypeScript — **preferred over Canvas Apps** | ✅ |
| Power Automate (Cloud Flows) | Process automation, approvals, notifications, integrations | ✅ |
| Microsoft Entra ID | App registrations, service principals, security groups (cross-cutting) | ✅ |
| SharePoint Online | Signed-acceptance document library (one site shared across environments — ADR-G01) | ✅ |
| Microsoft Teams | 1:1 chat notification to the process owner (TAD ADR-015). **No team is provisioned and no Teams app package is installed** in Phase 1 | ✅ (connector only) |
| Canvas Apps | Freeform low-code UI builder — use only when Code Apps are not viable | ❌ |
| Power Pages | External web portals | ❌ — the public application form is a WordPress form posting to the intake flow, not Power Pages |
| Power BI | Analytics and reporting | ❌ (not in Phases 1–3) |

## Solution Strategy

- All customisations ship inside a **single publisher-prefixed solution** per functional domain
- Solutions are **Unmanaged** in Dev and **Managed** in Test / Acc / Prd
- Source is stored unpacked via `pac solution unpack` and committed to `src/solutions/<SolutionName>/`
- No manual changes in any non-Dev environment — all changes flow through the pipeline
- Components that **cannot ship in a solution** (Entra app registrations, security groups,
  SharePoint sites, Teams, group-team role bindings, app sharing) are managed by idempotent
  scripts in `provisioning/`, executed via `pipeline.yml` `tenant_prerequisites` (gate:
  `APPROVE TENANT`) and per-environment `post_deploy` blocks — see
  `knowledge/technology/build-and-deploy.md` → Provisioning & Post-Deployment Configuration

## Publisher Convention

**These are the live values.** They are not a suggestion to be filled in — they are read back
from `src/solutions/RevitaliseGrantAutomation/Other/Solution.xml`, which is the source of
truth. All agents derive schema names from the prefix.

```
Publisher Display Name:  Revitalise Respite Holidays
Publisher Unique Name:   revitalise
Publisher Prefix:        rev              ← every table, column, option set and role
Option Value Prefix:     10000            ← option-set values are 10000nn, not arbitrary
Solution Unique Name:    RevitaliseGrantAutomation
Solution Display Name:   Revitalise Grant Automation
Solution Version:        1.0.0.0
```

Schema names therefore look like `rev_application`, `rev_conditionprofile`,
`rev_grantstatus`, `REV Admin`. Roles and field security profiles use the **upper-case**
`REV ` display prefix (`REV Admin`, `REV Service Automation`, `REV_TrusteeRestricted`); tables
and columns use lower-case `rev_`. Both appear throughout `knowledge/technology/` as
`[PREFIX]` and `[prefix]` respectively.

## Environment Chain

**Test and Acceptance are ONE environment** (TAD **ADR-006**, `Adopted`). The four-row chain
this table used to show — Dev / Test / Acc / Prd, with an `APPROVE ACC` gate — describes a
topology this project does not have and has not had since 2026-08-12.

| Environment | Config key | Type | Solution State | Approvals Required |
|---|---|---|---|---|
| Dev | `dev` | Development | Unmanaged | None — DEV is derived from git |
| Test / Acceptance | `tst_acc` | Sandbox | Managed | Build + test-agent `APPROVED` |
| Production | `prd` | Production | Managed | `APPROVE PRD` |

The config keys are the exact strings used by `config/<slug>-pipeline.yml` → `environments`,
by the GitHub Environments in `.github/workflows/ci.yml`, and by the `-Env` parameter of every
provisioning script (`dev` / `test` / `prd` — note the script parameter uses `test`, not
`tst_acc`, for the combined environment).

## Toolchain

| Tool | Version | Purpose |
|---|---|---|
| PAC CLI | Latest stable (≥ 1.44) | Pack, unpack, import, export, solution checker, `pac code` (Code Apps), `pac admin` |
| Node.js | LTS | Code Apps build runtime + PAC CLI |
| Vite | Latest stable | Code Apps bundler |
| React | 18+ | Code Apps UI framework |
| TypeScript | 5+ | Code Apps language |
| PowerShell | 7+ | CI/CD scripts |
| Microsoft Graph PowerShell | Latest stable | Entra groups, app registrations, Teams provisioning |
| PnP.PowerShell | Latest stable | SharePoint site provisioning and templates |
| Power Platform Admin PowerShell | Latest stable | App sharing, admin operations (`Set-AdminPowerAppRoleAssignment`) |
| GitHub Actions | — | CI/CD pipeline |
| EasyRepro | Latest | MDA UI functional testing |
| Playwright | Latest | Code Apps E2E testing |
