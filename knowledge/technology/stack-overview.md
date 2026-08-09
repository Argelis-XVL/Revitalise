# Stack Overview — Power Platform

> 📝 **Populate the Publisher Convention section below before starting any features.**
> Set your publisher prefix once — agents use it for all schema name generation.

## Platform Components in Use

| Component | Purpose | In Scope |
|---|---|---|
| Dataverse | Relational data store, business rules, column security | ✅ |
| Model-Driven Apps (MDA) | Process-driven internal UIs (cases, tasks, admin) | ✅ |
| Power Apps Code Apps | Custom UIs built with React + Vite + TypeScript — **preferred over Canvas Apps** | ✅ |
| Power Automate (Cloud Flows) | Process automation, approvals, notifications, integrations | ✅ |
| Microsoft Entra ID | App registrations, service principals, security groups (cross-cutting) | ✅ |
| SharePoint Online | Document storage for Dataverse, collaboration sites | [✅ / ❌ — set per project] |
| Microsoft Teams | Notifications, approvals, surfacing apps as tabs | [✅ / ❌ — set per project] |
| Canvas Apps | Freeform low-code UI builder — use only when Code Apps are not viable | [✅ / ❌ — set per project] |
| Power Pages | External web portals | [✅ / ❌ — set per project] |
| Power BI | Analytics and reporting | [✅ / ❌ — set per project] |

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

> 📝 **Set these values once for your project. All agents derive schema names from the prefix.**

```
Publisher Display Name:  [Your Project Name]
Publisher Prefix:        [prefix]          ← short lowercase, e.g. "proj", "crm", "hr"
Solution Unique Name:    [PREFIX]_<Domain> ← e.g. PROJ_CaseManagement, HR_Onboarding
```

## Environment Chain

| Environment | Type | Solution State | Approvals Required |
|---|---|---|---|
| Dev | Development | Unmanaged | None |
| Test | Test | Managed | Build + test-agent APPROVED |
| Acc | UAT | Managed | APPROVE ACC |
| Prd | Production | Managed | APPROVE PRD |

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
