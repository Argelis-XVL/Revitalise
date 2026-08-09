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
