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

---

## Alternate Keys — including on lookup columns

*Recorded 2026-08-19 from a live DEV verification (`IMP-0044`). Closed assumption A-G01.*

An alternate key **can** target a lookup column. Proven on `rev_grant.rev_applicationid`,
which is what enforces one grant per application (ADR-G02).

Two things follow, and the second one bites:

1. **Order matters when creating them by script.** A key on a lookup column cannot be created
   before the relationship that creates that column — Dataverse returns `0x80040203`. In
   `provisioning/dataverse/ensure-schema.ps1`, relationships are section 3 and alternate keys
   are section 4, and a static test asserts that order (`IMP-0043`). A mocked API test cannot
   catch this: a mocked `POST` succeeds regardless of what exists.

2. **The index is built ASYNCHRONOUSLY, and while it is building the key enforces nothing.**
   Straight after creation the key reports `EntityKeyIndexStatus = Pending`. A `Pending` key
   does **not** reject a duplicate and does **not** work for an upsert. Wait for `Active`:

   ```
   GET [Organization URI]/api/data/v9.2/EntityDefinitions(LogicalName='rev_grant')
       ?$expand=Keys($select=LogicalName,EntityKeyIndexStatus)
   ```

   Do not treat a uniqueness constraint as live, or use the key as an upsert target, until
   that field reads `Active`. "The create succeeded" is the platform's opinion about its own
   call, not a statement that the constraint is in force (`C-TECH-053`).

## Column Security Protects a Stored Value, Never a Projection of It

*The general rule the next two sections are both instances of. Recorded 2026-08-24
(`IMP-0257`), and `C-TECH-070` is its enforceable form.*

Dataverse maintains automatic companion columns that carry a **copy or projection** of another
column's value. Column security applies to the stored value, and a projection of that value sits
outside its reach. Two are known on this project, both verified live with
`CanBeSecuredForRead = False`:

| Shape | Automatic companion | What leaks |
|---|---|---|
| `Money` column | `<name>_base` | the same number, converted to base currency |
| `Lookup` column | `<lookup>name` | the **related row's primary name value** |

So before relying on column security for a confidentiality claim, ask **what the companion
actually contains.** For a lookup that means asking what the TARGET table's primary name holds:

- `rev_applicant`, `rev_grant`, `rev_bankaccount` have autonumber or masked primary names, so
  their companions yield only a pseudonymous reference (`REV-A-00001`, `GR-2026-00001`).
- **`rev_provideridname` yields the provider's real organisation name.** The only control on it
  is the table privilege (NFR-002: Finance-only Read). Confirm that before granting any new role
  Read on `rev_bankaccount` or `rev_payment`.

Read securability rather than assuming it:

```
GET EntityDefinitions(LogicalName='<t>')/Attributes?$select=LogicalName,AttributeType,IsSecured,CanBeSecuredForRead,CanBeSecuredForCreate,CanBeSecuredForUpdate
```

**A lookup column itself is fully securable** — `CanBeSecuredForRead/ForCreate/ForUpdate` all
`True`, verified live 2026-08-24. A field permission failing on a lookup is therefore never a
platform limit; it is a delivery gap under `C-TECH-071`, and treating the two as the same thing
is what made `IMP-0255` cost a day. The genuinely unsecurable shapes are the **primary name
attribute** (`0x8004f501`, it cannot be secured at all) and the **projections above**.

## Money Columns Cannot Be Secured — Use Decimal for a Restricted Amount

*Recorded 2026-08-19, verified live on `rev_grant.rev_amountawarded` (`IMP-0047`).*

**A Money column is two columns.** Dataverse creates an automatic companion,
`<name>_base`, holding the same value converted to the organisation's base currency, plus
`transactioncurrencyid` and `exchangerate` on the table.

The `_base` twin has `CanBeSecuredForRead = False`. It **cannot** be added to a column
security profile. So:

> Column security on a Money field does not protect the value. Anyone with table Read can
> read `<name>_base` and get the same number.

This is a silent failure: the profile accepts the primary column, the build's
`field-security-coverage` gate passes, the Dev Summary records the column as secured, and the
value is readable anyway.

**For an amount that must be restricted, use `Decimal`, not `Money`.** A single-currency
organisation gains nothing from `Money` — no conversion is happening — and loses the ability
to secure the value. Reach for `Money` only when multi-currency conversion is genuinely
required, and then treat the amount as unprotectable and control access at the table or
record level instead.

## Changing a Column's Data Type After It Has Shipped

Applied 2026-08-18 from `logs/improvement-log.jsonl` (IMP-0017) — proposed when it happened,
never written down until this review. Both steps below were discovered by execution; no
Microsoft document describes the sequence.

**A type change is not importable.** Solution import rejects `Picklist` → `String`/`Boolean`
outright: *"Attribute rev_helperrelationship is a Picklist, but a String type was specified."*
There is no in-place conversion.

**The follow-up delete is blocked by any form that references the column** — the delete returns
`400` while a `systemform` still names it, and the error does not say so plainly.

The working procedure, in order:

1. **Transitional import** that removes the control from every form referencing the column,
   leaving the column itself in place.
2. **Delete the column** via the Web API, now that no form depends on it.
3. **Recreate it at the correct type** via the Web API (`C-TECH-050`: attributes are created via
   the API, never assumed creatable by a first solution import).
4. Re-add the control to the form in the next ordinary import.

Budget three imports for one type change, and prefer getting the type right before the first
deploy — `skills/how-to-verify-a-platform-contract.md` exists because guessing it is what
produced this incident.

## Reading Metadata Through the Web API — Four Confirmed Limits

*Verified live against DEV 2026-08-24 (`IMP-0261`), closing an assumption `ensure-schema.ps1`'s
own header had carried unverified since it was written.*

The metadata endpoints support a **narrower OData surface** than the data endpoints, and the
difference is not signalled by the error.

| Works / fails | Detail |
|---|---|
| ✅ Alternate-key addressing | `RelationshipDefinitions(SchemaName='x')?$select=SchemaName` **works.** This was an open caveat in `ensure-schema.ps1`; it is confirmed |
| ❌ Complex property in `$select` | `CascadeConfiguration` in `$select` returns **HTTP 400**, not 404. Omit `$select` entirely and read it off the full response |
| ❌ `startswith()` on Metadata Entities | Unsupported outright (`0x8006088a`). Filter by exact equality, or address by alternate key |
| ❌ `Privileges` as an expand | Not an expandable navigation property on `EntityMetadata` (`0x80060888`). Query the `privileges` entity set instead |

**The rule of thumb that matters, because it is the one that misleads:**

> On a metadata GET, a bare 400 usually means your **projection** is illegal — not that the
> thing is missing. Retry without `$select` before concluding absence.

A 400 from an illegal projection reads exactly like a relationship being absent. `ensure-schema.ps1`'s
`Test-RevResourceExists` is safe here because it treats **only** 404 as absence and rethrows
everything else — but an ad-hoc verification query written by hand has no such guard, and one in
this session read as all nine relationships being missing when every one of them existed.
