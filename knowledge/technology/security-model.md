# Dataverse Security Model — Roles, Teams, Group Binding

> 📝 Replace `[PREFIX]`/`[prefix]` with your project's publisher prefix (from `stack-overview.md`).
> This file defines how access is designed and provisioned. The **role definitions** ship in
> the solution; the **role assignments** (group teams) are per-environment configuration
> applied by pipeline `post_deploy` steps.

## Security Layers (outermost first)

| Layer | Controls | Where Managed |
|---|---|---|
| Environment security group | Who can access the environment at all | Power Platform admin center (per env) |
| Business units | Data ownership boundaries | Solution design — keep flat unless required |
| **Security roles** | Table privileges (CRUD + depth) | Solution component (`SecurityRoles/`) |
| **Group teams** | Role assignment via Entra security groups | Per-environment config (post_deploy) |
| Column security profiles | Field-level access on Tier 3/4 columns | Solution component — see `dataverse.md` |
| Record sharing | Exceptional per-record access | Avoid as a design mechanism; audit when used |

## Security Role Design Rules

- **Never modify out-of-box roles** — copy into a `[PREFIX]` role and adjust (`C-TECH-046`).
- Naming: `[PREFIX] <Persona>` — e.g. `[PREFIX] Case Worker`, `[PREFIX] Compliance Reviewer`.
- **Base + additive pattern**: one `[PREFIX] Base User` role with the minimum shared
  privileges (read reference data, app access); persona roles add on top. Users get
  base + persona — never a single monolithic role.
- Least privilege per table: prefer `User`-level depth; widen to `Business Unit` /
  `Organization` only with a documented reason in TAD §6.
- Every custom table in the feature must appear in at least one persona role — a table
  no role can read is a defect, not a default.
- Roles are solution components: they travel in the managed solution and are versioned
  with the feature. Shared base roles live in the `[PREFIX]_Base` solution
  (see `coding-standards.md` → Solution Layering).

## A Table's OwnershipType Decides Which Privileges Can Exist

**Read live from DEV across all ten custom tables on 2026-08-24. This is a platform law, not a
project convention.**

| OwnershipType | Privileges Dataverse creates | Never created |
|---|---|---|
| `UserOwned` | Create, Read, Write, Delete, Append, AppendTo, **Assign, Share** | — |
| `OrganizationOwned` | Create, Read, Write, Delete, Append, AppendTo | **Assign, Share** |

An organization-owned table has no individual owner, so there is nothing to assign to or share
from. Requesting `prvAssign<table>` or `prvShare<table>` for one fails outright — *"privilege
'prvAssignrev_provider' does not exist in this environment"* — and takes the whole role binding
with it.

**`Delete` DOES exist on an organization-owned table.** Conflating the two is what makes this
easy to get wrong: `rev_anonymisedstatistic`'s role block withholds Delete as well, but that is
a deliberate policy choice under `C-DOM-021`, not a platform limit. Copying that block as if it
described the platform is how you arrive at the wrong rule for the right-looking reason.

Before writing or copying a role's privilege block for a custom table, read the table's own
ownership rather than the neighbouring table's block:

```
GET EntityDefinitions(LogicalName='<table>')?$select=OwnershipType
GET privileges?$filter=endswith(name,'<table>')&$select=name
```

The second query lists exactly what the environment will accept. Note `Privileges` is **not** an
expandable navigation property on `EntityMetadata` (`0x80060888`) — query the `privileges`
entity set, never `$expand`.

Mechanically enforced by `scripts/verify-role-privilege-ownership.py` (build step
`role-privilege-ownership`), which derives the allowed set from each table's own declared
`OwnershipType` rather than a transcribed list. Origin: `IMP-0254` (the live failure),
`IMP-0256` (the ground truth that settled it).

## Canonical Persona Mapping

Every feature that touches security defines this table in TAD §6.1:

| Persona | Entra Security Group | Dataverse Group Team | Security Role(s) | App Access |
|---|---|---|---|---|
| Case Worker | `[PREFIX]-CaseWorkers-<Env>` | `[PREFIX] Case Workers` | `[PREFIX] Base User` + `[PREFIX] Case Worker` | MDA: `[PREFIX]_App` |
| Reviewer | `[PREFIX]-Reviewers-<Env>` | `[PREFIX] Reviewers` | `[PREFIX] Base User` + `[PREFIX] Reviewer` | MDA + Code App |

## Group Teams — Binding a Role to a Security Group

The **only** approved role-assignment mechanism in Test/Acc/Prd (`C-TECH-040`):
Entra security group → Dataverse **group team** (type *AAD Security Group*) → security role.
Direct user-to-role assignments are permitted in Dev only.

Group teams are **not solution components** — create them per environment in a
`post_deploy` step. Web API pattern (idempotent — query by name first):

```http
POST [org-url]/api/data/v9.2/teams
{
  "name": "[PREFIX] Case Workers",
  "teamtype": 2,
  "azureactivedirectoryobjectid": "<entra-group-object-id>",
  "membershiptype": 0,
  "businessunitid@odata.bind": "/businessunits(<root-bu-id>)"
}
```

Then associate the role (look up the role ID **by name in the target environment** —
role GUIDs differ per environment):

```http
POST [org-url]/api/data/v9.2/teams(<team-id>)/teamroles_association/$ref
{ "@odata.id": "[org-url]/api/data/v9.2/roles(<role-id>)" }
```

`teamtype: 2` = AAD Security Group. `membershiptype: 0` = Members and guests.
Membership then syncs from Entra automatically — the pipeline never manages individual users.

## App Access

| App Type | How Access Is Granted |
|---|---|
| Model-Driven App | Associate the app with the persona security roles (solution-aware); users reach it via role |
| Code App / Canvas App | Share the app with the persona's **Entra security group** (post_deploy step — `Set-AdminPowerAppRoleAssignment` or Power Apps portal) |
| Flows | Owned by the service principal; co-owner group only where operationally required |

## Column Security Profiles

Defined in `dataverse.md`. Add the **group team** (not individual users) as the member
of each column security profile so field-level access follows the same group mapping.

## `rev_setting` carries TWO kinds of key, and the table cannot tell them apart

`NFR-019` established one mechanism — a `rev_setting` row read on every flow invocation — and the
design reused it for a control of a different kind, because the mechanism fitted. Two kinds now
live side by side, indistinguishable in the schema, in the seed script and in the settings table a
process owner sees:

| Kind | Who may change it | Examples |
|---|---|---|
| **Free tunable** (`NFR-019`) | the process owner, without a developer and without a deployment | `FR-062`'s three thresholds, `RoundStatisticsStaleAfterSeconds` |
| **A recorded risk decision** | **the reviewer only** — lowering it widens a confidentiality boundary | `RoundStatisticsMoneyMeasureMinimumPopulation` |

**Rule: a key of the second kind names its deciding open question in its own description.** That is
the only signal available at the point where someone is editing the rows.

**`RoundStatisticsMoneyMeasureMinimumPopulation` is k=5 by explicit reviewer risk decision**
(`OQ-043`, TAD S0.9.1). It is **not** a tunable like the three thresholds beside it: lowering it
releases money averages over smaller groups of applicants and needs a reviewer decision, not a
settings edit.

**Seed 5 in every environment.** An absent row withholds the four money measures — fail-safe, but
not the approved behaviour — and a DEV/TST divergence renders the same round differently per
environment, which reads as a data bug and is a configuration one.

**Not mechanically enforced, and this is the known gap** (`IMP-0469`). No gate distinguishes a key
that encodes a risk decision from one that encodes a preference; the seed script treats all of them
as reference data. The mechanical form is a `classification` field on every `settingRows` entry
across the three `deploymentSettings` files plus a build check — **delivery work under
`provisioning/`, flagged as a follow-up by the reviewer on 2026-08-28 and deliberately not built by
improvement review 40**, which does not author changes to the seed payload shape.

## Verification (test-agent)

The provisioning test layer must assert, per environment:

1. Group team exists with the correct `azureactivedirectoryobjectid`
   (`GET /teams?$filter=name eq '...'`).
2. Team has exactly the roles from TAD §6.1 (`GET /teams(<id>)/teamroles_association`).
3. No direct user role assignments for feature roles in Test/Acc/Prd
   (`GET /roles(<id>)/systemuserroles_association` returns only service accounts, if any).
4. A member of the group can access the app; a non-member cannot (E2E security test).

## References

- `knowledge/technology/entra-id.md` — creating the security groups
- `knowledge/technology/dataverse.md` — column security profiles, audit
- `constraints/technology/technology-constraints.md` §5 — C-TECH-040, C-TECH-042, C-TECH-046
