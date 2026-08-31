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

## Column-level WRITE control EXISTS, and is already used here

*Recorded 2026-08-28 (`IMP-0403`). A dispatch brief asserted the opposite as the basis for a TAD
revision, and it was ground-truthed against this repository's own source and found false.*

**`FieldPermission` carries `CanRead`, `CanUpdate` AND `CanCreate`.** All three are authored in
this solution — `Other/FieldSecurityProfiles.xml:112-114`, for every one of its secured columns —
and `provisioning/dataverse/ensure-schema.ps1:894-910` reconciles `cancreate` / `canread` /
`canupdate` live against the environment. So *"Dataverse role privileges are table-level;
column-level write control does not exist"* is wrong twice over: the capability exists, and this
project already depends on it.

**Where it genuinely is unusable, the reason is OURS, not the platform's.** A column a **Code App
must read** cannot use it, for two project-specific reasons:

1. `CanUpdate` governs only `IsSecured=1` columns, and releasing a secured column to a trustee
   requires the trustee team **inside a field security profile** — which
   `no-trustee-in-column-security-profile` forbids, and which is `ADR-002`'s whole control.
2. A secured column on a table the app queries fails `no-secured-columns-in-code-app`.

**Never write *"the platform cannot"* where *"our own HARD gates forbid"* is the true statement.**
The resulting design is identical; the sentence is not. One is a permanent constraint a reader will
stop questioning, the other is a decision this project made and could revisit — and a brief that
states the first when the second is true removes an option nobody chose to remove.

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

## Reading DATA Through the Web API — a Null Column Is OMITTED, Not Returned as Null

*Verified live 2026-08-28 (`IMP-0435`, `blocker`). This is the DATA side of the section above and
it bites harder, because the failure mode is a terminating error rather than a wrong value.*

**`$select` names what you asked for, not what comes back.** Dataverse omits a null-valued column
from the response body entirely — there is no `"rev_resultjson": null` property to read, the
property is simply absent. On its own that is benign and well-known.

**Every provisioning script in this repository sets `Set-StrictMode -Version Latest`, and that
turns the absence into a terminating `PropertyNotFoundException`.** Not `$null`. Not a warning. A
throw, caught by whatever `catch` surrounds it, which is how a seeding script reported `FAILED` on
the one path it exists to serve — the *normal first run*, when the column it reads has never been
written.

Either contract alone is harmless. Multiplied, the **absent-value case is the common case** and it
is the only one that throws.

```powershell
# WRONG — throws under StrictMode whenever the column is empty, which is most of the time
$before = Invoke-DataverseApi -Method GET -Path "$keyPath`?`$select=rev_resultjson"
if ([string]::IsNullOrEmpty($before.rev_resultjson)) { ... }

# RIGHT — ask whether the property exists before reading it
$hadContent = ($before.PSObject.Properties.Name -contains 'rev_resultjson') -and
              -not [string]::IsNullOrEmpty($before.rev_resultjson)
```

Guard **every optional-column read** this way. A column that is mandatory, or a primary name
column, cannot be null and needs no guard — which is why this is a habit for optional reads rather
than a blanket rule, and why it is not mechanically gated: telling "this variable holds an API
response" from "this variable is a request body I just built" needs dataflow analysis. Measured
before deciding: a regex over `provisioning/` found 6 candidate sites, 2 real and 4 false.

### And the test fake must OMIT the property, not set it to `$null`

This is the half that makes the defect invisible to its own test:

```powershell
# A fake that PASSES while the real API throws — do not write this
@{ rev_resultjson = $null }

# A fake that reproduces the platform — the property is not there at all
@{ }
```

A null-valued fake exercises a code path the live service never produces. Reproducing the
**absence** is the assertion; anything else tests the mock. The worked example lives in
`src/tests/provisioning/DataverseScripts.Tests.ps1`'s `seed-round-statistics-test-data.ps1` block.

## When an ADR Moves Columns Off a Table but RETAINS Them, Sweep What Describes the TABLE

ADR-038 moved `rev_status`, `rev_resultjson` and `rev_computedon` from
`rev_roundstatisticsrequest` to `rev_roundstatisticsresult` and — because a live metadata delete
was out of scope — **kept the superseded columns on the request table**. The sweep that followed
was scoped to the moved *columns*: their attribute descriptions, the roles, the flow's write
actions, the app's select lists. Prose that describes the **table's role** names those columns
without being a read or a write of them, so nothing looked at it.

Three shipped artefacts went on saying the answer lives on the request table for three days after
the move (`IMP-0448`):

| Artefact | What it said |
|---|---|
| the **entity-level** `<Description>` in `Entities/rev_roundstatisticsrequest/Entity.xml` | *"the flow writes rev_status, rev_resultjson and rev_computedon when it finishes"* — contradicting its own attribute descriptions eight lines below |
| the global option set `rev_roundstatisticsrequeststatus`'s `<Description>` | *"State of the single rev_roundstatisticsrequest row's most recent computation cycle"* |
| the flow's `notes.md` §5 | *"rev_roundstatisticsrequest.rev_status documents DefaultValue=2 … the seeded row's resting state"* |

**So the checklist after any retain-in-place column move is four items, not one:** the attribute
descriptions, the **entity-level** description, any **option set** description scoped to the old
table, and the flow's **notes**. `scripts/verify-superseded-column-writers.py` covers the code
half — a `.ps1` or a `Workflows/*.json` that writes a marked column — and nothing covers the prose
half.

### And there is no gate for the prose half, deliberately — it was built and measured blind

The obvious gate is *"no `<Description>` may assert a marked column is written on the entity
carrying the marker."* Measured against the two texts of the same description:

| Text | Findings |
|---|---|
| defective — *"the flow writes rev_status, rev_resultjson and rev_computedon when it finishes"* | **3** |
| corrected — *"the flow writes rev_status, rev_resultjson and rev_computedon **on rev_roundstatisticsresult, never on the table it triggers on**…"* | **3** |

**Identical.** This repository's correction style *retains* the wording it withdraws and appends
the negation, so a phrase gate cannot tell a false claim from its own retraction — it is not
merely inverted, it is blind. That is the sixth measured instance of the shape `IMP-0422` records,
and the reason the rule is *assert on values, not on phrases*: here the subject is prose about
prose and there is no value to assert on.

**So this is a human checklist, and the trigger is the ADR, not the gate.** The reviewer's
standing decision (2026-08-28) is that the descriptions stay as they are, naming the columns while
stating the truth about them — the alternative, forbidding the column names in prose to make a
value gate possible, buys enforcement by constraining how documentation may be written.
