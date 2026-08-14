# Dataverse — Reference

> 📝 The `[prefix]_` shown throughout this file is your project's publisher prefix.
> Set it in `knowledge/technology/stack-overview.md` → Publisher Convention, then use it consistently.

## Table Conventions

| Convention | Rule |
|---|---|
| Schema name prefix | `[prefix]_` (publisher prefix — e.g. `proj_`, `hr_`, `crm_`) |
| Display name | Title Case, no abbreviations |
| Plural name | Defined explicitly (not auto-generated) |
| Primary name column | `[prefix]_name` — always populated, human-readable identifier |
| Ownership | User/Team owned for work records; Organisation owned for lookup/reference data |

## Mandatory Columns on Every Custom Table

| Column | Type | Purpose |
|---|---|---|
| `[prefix]_name` | Single line of text | Primary name, required |
| `createdon` | DateTime | System-managed, audit |
| `createdby` | Lookup (systemuser) | System-managed, audit |
| `modifiedon` | DateTime | System-managed, audit |
| `modifiedby` | Lookup (systemuser) | System-managed, audit |
| `statecode` | State | Active / Inactive |
| `statuscode` | Status | Sub-status per state |

## Audit Logging

- Enable auditing at **environment level** and **table level** for all tables with sensitive data
- Enable **field-level auditing** for: status columns, assigned user, high-classification columns
- Audit log retention period must meet the longer of: regulatory requirement or business policy
- Never disable auditing via code or configuration without explicit compliance sign-off

> 📝 Define which tables require auditing in `knowledge/domain/compliance-requirements.md`.

## Security Roles & Group Teams

Security role design, the persona → Entra group → group team → role mapping, and app
sharing rules live in `knowledge/technology/security-model.md`. Roles ship in the
solution; role **assignments** (group teams) are per-environment `post_deploy` config.

## Column Security Profiles

Apply column security profiles to all Tier 3 / Tier 4 columns (see `skills/data-classification.md`):

| Profile Name | Applies To | Permitted Roles |
|---|---|---|
| `[PREFIX]_[Sensitive]` | [Columns of this type] | [Roles that may access] |
| `[PREFIX]_[Restricted]` | [Columns of this type] | [Roles that may access] |

> 📝 Define your column security profiles in `knowledge/domain/compliance-requirements.md`.

## Relationships

- Use **N:N relationships** via relationship tables (not manual junction tables) for M:M
- All 1:N relationships must define **cascade behaviour** explicitly:
  - Parental: cascade delete only when child records have no regulatory retention obligation
  - Referential: preserve child on parent delete — use for records with compliance retention

## Restrict Delete Rule

> ⛔ Enable **Restrict Delete** on all tables with a regulatory retention period.
> This prevents accidental deletion of records that must be retained for compliance.
> Define which tables require this in `knowledge/domain/compliance-requirements.md`.

## Business Rules

Use Dataverse Business Rules for:
- Simple field validation (required conditions, range checks)
- Show/hide fields based on status

Use Power Automate for:
- Multi-step or cross-table logic
- External system calls
- Timed or event-driven processes

Do not use JavaScript for logic that can be expressed as a Business Rule.

## Solution Checker

Run `pac solution check` before every build. Zero Critical or High severity issues permitted.
Exceptions must be documented in `docs/architecture/<slug>-architecture.md §11`.

## Solution Import: What Cannot Be Created From Scratch, and What Gets Its Own Id

Learned live, the hard way, deploying a hand-authored solution to a real environment for the
first time (Revitalise Grant Application Automation, revision 1.0 - see that project's Dev
Summary §2.7 for the full incident-by-incident account). If a real `pac solution unpack` of an
already-working component is available, trust it over this section.

- **Entities/Attributes, Global OptionSets, Security Roles and Field Security Profiles are
  documented by Microsoft as unsupported to create from scratch via solution import.** Create
  them once, per environment, via the Dataverse Web API (metadata endpoints for the first two,
  ordinary `roles`/`fieldsecurityprofiles`/`fieldpermissions` entity sets for the other two),
  *then* solution import can manage and update them. `provisioning/dataverse/ensure-schema.ps1`
  is the reusable pattern: idempotent (`EXISTS`/`CREATED`/`FAILED` per resource), safe to
  re-run, and it must run against every new environment before the first solution import into
  it — DEV, TST/ACC and PRD alike.
- **A component created this way gets a Dataverse-assigned id, not the one your hand-authored
  source declares.** Roles, Field Security Profiles, app-specific sitemaps and model-driven
  apps all fall into this trap: fabricate a GUID in source, and the *next* solution import
  either fails outright (`Cannot import security role ... with the same name but different Id
  already exists` - roles are matched strictly by id) or silently tolerates the mismatch
  without ever adopting your fabricated id (Field Security Profiles reconcile by name instead -
  a landmine, not a pass). Read the real id back live (`GET .../roles?$filter=name eq '...'`,
  etc.) and use it in source. Where the component type supports referencing by `schemaName`
  instead of `id` (e.g. an `AppModuleComponent` pointing at the app's own sitemap), prefer
  that — it sidesteps the whole problem, since there is then no id to keep in sync at all.
- **A hand-authored component's XML shape is a guess until it survives a real import.** The
  "obvious" shape for AppModule.xml, AppModuleSiteMap.xml, FieldSecurityProfiles.xml and
  EnvironmentVariableDefinition files was wrong in specific, non-obvious ways every time —
  wrong element casing, an invented wrapper element, a field that's actually an XML attribute
  not a child element, a folder layout that changed between `pac` versions. **When a real
  environment exists, get ground truth instead of guessing twice**: create a minimal instance
  of the component directly (Web API, or the maker portal for things like model-driven apps),
  then `pac solution export` + `pac solution unpack` it to see exactly how the platform
  serialises it — this resolves ambiguity faster than repeated import-error-message iteration.
- **A component type your `RootComponents` declaration doesn't actually need to (or is even
  allowed to) reference.** Connection references (component type `10371`) triggered `Invalid
  component type provided 10371` from `SolutionComponentTypeMap.RetrievePlatformName` when
  declared as a `RootComponent` in one live Dataverse version, despite being an entirely
  ordinary component everywhere else — the actual component still ships correctly from its
  definition in `Other/Customizations.xml`; it just cannot also be tracked as a named root
  component of the solution in that version. If a `RootComponent` declaration for a type
  produces this error, remove the declaration rather than the component.
