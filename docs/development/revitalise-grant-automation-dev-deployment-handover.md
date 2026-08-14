# Handover — First DEV Deployment of a Hand-Authored Power Platform Solution

**Feature:** Revitalise Grant Application Automation (Phase 1)
**Date:** 2026-08-14
**Author:** development-agent (live session with Xander Lykopoulos)
**Status:** DEV deployment COMPLETE and verified. All four flows open and save in the designer.
**Companion documents:** `docs/development/revitalise-grant-automation-dev-summary.md` (§2.7 records
the same incidents against the revision history); `knowledge/technology/dataverse.md` and
`knowledge/technology/power-automate.md` (the durable, project-independent lessons);
`constraints/technology/technology-constraints.md` (C-TECH-049/050/051).

> **⚠ Addendum, 2026-08-14, same day.** This document's "COMPLETE and verified" status covered
> import and designer-save of the four **flows**. It did not cover the four **tables**: none had
> any views or forms, and `rev_setting` had zero rows, none of which any step in §2 or §5 checks for
> (§5's queries list `environmentvariabledefinitions`, `appmodules`, `sitemaps` and `workflows` —
> `savedquery` and `systemform` are absent from that list). Root cause, fix and live-DEV verification
> evidence are in Dev Summary **revision 1.0 (D-018, D-019, D-020)**. The transferable lesson in §6
> holds exactly as written: this was another plausible-looking hand-authored shape (missing
> `<FormXml />`/`<SavedQueries />` markers) that packed clean and imported clean, found only by
> checking what the platform actually created rather than trusting the packer's silence.

---

## 1. Why this document exists

Getting this solution into DEV took **fifteen `pac solution import` attempts**. Every failure was a
real defect in hand-authored source, each one individually small, and each one discoverable only by
running the import for real. None were caught by `pac solution pack`, the 640-test Pester suite, the
XML/JSON well-formedness gates, or the two existing source-consistency checks — all of which passed
throughout.

The purpose of this handover is that **the next feature, and the next environment, should not cost
fifteen attempts**. Section 2 is the corrected process. Section 3 is what changed in the repo so the
lessons are enforced rather than remembered. Section 4 is the outstanding work with exact commands.
Section 5 is the honest list of what is still unproven.

The single most useful sentence in this document, if you read nothing else:

> **A successful `pac solution pack` proves layout, not content. A successful import proves the
> component was accepted, not that it works. A component that imports can still be unopenable in
> the designer. Verify each of those three things separately, by execution.**

---

## 2. The corrected process for deploying to a fresh environment

This is the order that works. Steps 1–3 were the missing prerequisites that turned a "just import
it" task into a fifteen-attempt investigation.

### Step 0 — Prerequisites (one-off per tenant)

| What | How | Notes |
|---|---|---|
| Provisioning app registration | Manual, in Entra (`REV-MS-Provisioning`) | App ID `077f1f90-3218-4a06-bc90-887464353aa7` |
| Certificate auth (never a secret) | `provisioning/entra/create-self-signed-cert.ps1`, upload `.cer` to the app registration | C-TECH-044. Thumbprint → `PROVISION_CERT_THUMBPRINT` env var; app id → `PROVISION_APP_ID` |
| Dataverse API permission | `Dynamics CRM / user_impersonation`, delegated | Verified working live via `WhoAmI` |
| Application User in the target environment | Power Platform admin centre → Environment → Settings → Users + permissions → Application users → New | **This is required and easy to miss.** Give it System Administrator for provisioning |
| Entra security groups | **Created manually by the reviewer** | Graph app permissions (`Group.Create`, `GroupMember.ReadWrite.All`) could not be consented in this tenant, so `ensure-groups.ps1` is marked SKIPPED in `pipeline.yml` with the rationale recorded |

### Step 1 — Create the schema Dataverse will not accept from a solution import

```bash
export PROVISION_APP_ID="<app id>"
export PROVISION_CERT_THUMBPRINT="<thumbprint>"
pwsh -NoProfile -File provisioning/dataverse/ensure-schema.ps1 -Env dev
```

**This must run before the first solution import into any new environment** (C-TECH-050). Microsoft
documents Entities, Attributes, Global OptionSets, Security Roles and Field Security Profiles as
unsupported to create from scratch via solution import; this script creates them via the Web API
instead. It is idempotent — a clean re-run reports **244 `EXISTS`, 1 `CREATED`** (the always-running
"Publish all customizations" step) and **0 `FAILED`**. Anything else needs investigating before you
proceed.

Settings live in `provisioning/deploymentSettings/dev-schema-settings.json` — deliberately **not**
named `dev-settings.json`, because several other scripts and their tests rely on
`Get-ProvisioningSettings -Env dev` throwing "file not found" as the signal that DEV has no
group-team bindings scripted against it. That invariant is load-bearing; don't "fix" it.

### Step 2 — Reconcile live-assigned ids into source

Dataverse assigns its own ids to the components created in Step 1. Read them back and put the real
values in source (C-TECH-051):

```bash
# Roles
GET {env}/api/data/v9.2/roles?$filter=name eq 'REV Admin'&$select=roleid,name
# Field security profile
GET {env}/api/data/v9.2/fieldsecurityprofiles?$filter=name eq 'REV_TrusteeRestricted'&$select=fieldsecurityprofileid,name
```

Update `Roles/*/*.xml`, `Other/FieldSecurityProfiles.xml`, and the matching `<RootComponent>` entries
in `Other/Solution.xml`. **Note this makes those files DEV-specific.** TST/ACC and PRD will assign
their own ids on first creation there — which is exactly why `bind-roles-to-groups.ps1` looks roles
up *by name*, and why promotion to those environments is via Pipelines rather than by re-importing
this same source. Re-run Step 2 per environment, or (better, where the component type allows it)
reference by `schemaName` and skip the problem entirely.

### Step 3 — Run the build gates locally

```bash
python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation
python3 scripts/verify-field-security-coverage.py src/solutions/RevitaliseGrantAutomation
python3 scripts/verify-workflow-description-length.py src/solutions/RevitaliseGrantAutomation   # NEW
pwsh -NoProfile -Command "Invoke-Pester -Path src/tests"
```

All four must pass. Expected: 33 root components; 34 secured columns, 1 reviewed exemption;
4 flow definitions within the description limit; 640 Pester tests passing, 1 skipped.

### Step 4 — Pack and import

```bash
pac solution pack --zipfile /tmp/RevitaliseGrantAutomation.zip \
  --folder src/solutions/RevitaliseGrantAutomation --packagetype Unmanaged

pac solution import --path /tmp/RevitaliseGrantAutomation.zip \
  --environment https://orge2b20d13.crm17.dynamics.com/ \
  --async --max-async-wait-time 60 --force-overwrite --publish-changes --activate-plugins
```

A full clean import takes **60–100 seconds**, plus ~20–45s to publish. Anything failing in under
40 seconds failed early, at a structural stage.

### Step 5 — Verify by execution, not by exit code

Three separate things to check, because passing one does not imply the others:

```bash
# (a) Did the components actually get created? Query them.
GET {env}/api/data/v9.2/environmentvariabledefinitions?$filter=startswith(schemaname,'rev_')
GET {env}/api/data/v9.2/appmodules?$filter=uniquename eq 'rev_grantadministration'
GET {env}/api/data/v9.2/sitemaps?$filter=sitemapnameunique eq 'rev_grantadministration'
GET {env}/api/data/v9.2/workflows?$filter=startswith(name,'REV')&$select=name,statecode

# (b) Is it idempotent? Re-run the same import. It must succeed again cleanly.
# (c) Can a human actually USE it? Open every flow in the designer and press Save.
```

**Step 5(c) is not optional and cannot be automated away.** Three of the fifteen failures were
invisible to (a) and (b): the solution imported, the flow existed and was queryable, and the flow
still could not be opened or saved by a maker. See §3.2.

### Diagnosing a failure

`pac solution import` returns a terse one-line reason. Get the real detail:

```bash
# Full per-component detail, including which component and which field
pac env fetch --xmlFile importjob-query.xml    # FetchXML over importjob, selecting `data`

# For a generic "An unexpected error occurred", the stack trace names the failing handler
GET {env}/api/data/v9.2/asyncoperations(<async-op-guid>)?$select=message,friendlymessage,statuscode
```

The `asyncoperations.message` field carries a full .NET stack trace. `ImportAppModulesHandler`,
`SourceControlHandler`, `ImportRootComponentsHandler` in that trace tell you which component type is
failing even when the message itself says nothing useful.

**And when a component's shape is the question: build one for real, then look at it.** Create a
minimal instance via the Web API (or the maker portal, for a model-driven app), then
`pac solution export` + `pac solution unpack` and read how the platform serialises it. This resolved
four of the six blockers faster than any amount of documentation research or error-message iteration.

---

## 3. The fifteen failures, and what now prevents each one

### 3.1 Solution-import failures (six root causes)

| # | Symptom | Root cause | Prevented by |
|---|---|---|---|
| 1 | `An error occurred while importing Field Security Profile: Object reference not set to an instance of an object` | `description` was a child element, should be an attribute; every `FieldPermission` child used fabricated lowercase names (`entityname`/`attributelogicalname`/`cancreate`…) instead of the real `EntityName`/`AttributeName`/`CanRead`/`CanUpdate`/`CanCreate`, and `CanReadUnmasked` was missing entirely. Case-sensitive lookups on nonexistent names → null → NRE | Ground-truth export comparison; `verify-field-security-coverage.py` regex updated to the real element names |
| 2 | `Cannot import security role with Id [...] and name [REV Admin]. A security role with the same name but different Id already exists` | Hand-authored source declared fabricated GUIDs; `ensure-schema.ps1` had already created the roles with Dataverse-assigned ones. Roles match strictly by id | **C-TECH-051**; Step 2 of §2 |
| 3 | `The SiteMapName in the AppModuleSiteMap is null or empty`, then `Sitemap XML is missing while importing a new sitemap` | Three successive wrong guesses at `AppModuleSiteMap.xml`: a missing name field, then a fabricated `<SiteMapXml>` wrapper element, then a CDATA-encoding theory. The real shape has `<SiteMap>` as a *direct child*, `LocalizedNames` for the display name, no `sitemapid` at all, plus four boolean elements | Ground truth via Web-API-created sitemap + export/unpack. Recorded in `dataverse.md` |
| 4 | `An unexpected error occurred` → NRE in `ImportAppModulesHandler.GetParameterXPath()` | `AppModule.xml`: almost every element wrong — invented `<name>`/`<url>`/`<descriptions>`, lowercase instead of PascalCase, `AppModuleRoles` instead of `AppModuleRoleMaps`, wrong `NavigationType`/`FormFactor` defaults, and a fabricated `id` on the sitemap reference where the real form uses `schemaName` | Ground truth from the model-driven app **the user built manually** in DEV, exported and unpacked. `verify-solution-root-components.py` regex updated to PascalCase `<UniqueName>` |
| 5 | `Invalid component type provided 10371` from `SolutionComponentTypeMap.RetrievePlatformName` | This Dataverse version's root-components resolver doesn't recognise connection references as a declarable `RootComponent` type at all — despite them being ordinary components. The long-ignored "root components are not defined in customizations" pack warning was this, all along | `RootComponent` declarations removed (components still ship from `Customizations.xml`); type excluded in `verify-solution-root-components.py` with the reason |
| 6 | `Failed to find environment variables with schema name(s) 'rev_ProcessOwnerUpn'` | Environment variable definitions were at flat `EnvironmentVariables/<name>.xml` per a decompiled-source claim that described an **older `pac` version**. Real layout (pac 2.4.1) is `environmentvariabledefinitions/<name>/environmentvariabledefinition.xml`. The files packed silently as unregistered blobs | Ground truth via Web API + export/unpack; `verify-solution-root-components.py` updated. See `environmentvariabledefinitions/README.md` |

Also fixed en route, in the same investigation: `<Format>` casing across 13 ntext columns (lowercase
in XML, PascalCase in the Web API — the *same* semantic field, two conventions); picklist
`GlobalOptionSet@odata.bind` requiring a raw GUID, not the documented `Name=` alternate key; nine
security-role privilege depth/name corrections (`prvReadSystemUser` doesn't exist — it's
`prvReadUser`; some privileges don't support `Basic` depth; two don't exist at all in this version);
`RelationshipRoleType` being `0`/`1` not `1`/`2`; calculated columns having no working
`SourceType`/`Formula` shape (shipped as plain writable columns, to be converted by hand);
`<LookupTypes>` being fabricated for plain N:1 lookups.

### 3.2 Designer-save failures — the class that survives a successful import

These three are the reason §2 Step 5(c) exists. Every one of them imported cleanly, was queryable
via the Web API, and still left a flow no human could open or edit.

| # | Symptom | Root cause | Prevented by |
|---|---|---|---|
| 7 | Flow won't open — "description of the action truncate error message exceeded its description character length limit" | **62 `description` fields across all four flows exceeded Power Automate's hard 256-character limit**, up to 6,696 characters. This project's verbose documentation style is correct for an XML comment and fatal in a flow field | **C-TECH-049** + `scripts/verify-workflow-description-length.py`, wired into `build.yml` as `workflow-description-length` |
| 8 | `Flow save failed with code 'InvalidStaticResultName' ... static result 'Write_error_log_row' ... cannot be null or empty` | A stray hand-authored `runtimeConfiguration.staticResult` block with `staticResultOptions: "Disabled"` and no `name`. Looks inert; isn't. Unique to one action, nothing else in the solution used it | `power-automate.md` — omit the key entirely when Static Results aren't in use |
| 9 | `Flow save failed with code 'InvalidConcurrencyConfiguration' ... concurrency control is not supported when the workflow contains actions of type 'response' without the operationOptions flag set to 'asynchronous'` | The intake trigger caps `concurrency.runs: 1` (deliberately — the applicant match-or-create is read-then-write). Power Automate then requires `"operationOptions": "asynchronous"` on **every** `Response` action. Five needed it | `power-automate.md` |

**Where the 62 long descriptions went.** Not deleted. Each flow now has a companion
`Workflows/<FlowName>.notes.md` holding the full original text, keyed by JSON path. The flow keeps a
≤256-character description carrying the essential fact plus its FR/NFR/ADR citation and a pointer to
the notes file. Two Pester tests that asserted on that prose — including the D-001 assertions that
couple the intake trigger's documented Entra auth control to `verify-intake-endpoint-auth.ps1` —
were repointed at the notes file, so the coupling those tests protect is intact.

### 3.3 A bug this project introduced into itself, worth naming

`Get-ProvisioningCertificate` used `Get-ChildItem -Path 'Cert:\...'`. The `Cert:` PSDrive is
**Windows-only**, so every provisioning script would have failed on the macOS/Linux CI runner. Fixed
to the cross-platform `X509Store` API. Found only because provisioning was finally run for real, on
a Mac. **Anything that has only ever run on one OS is unproven on the others** — the CI runner is
Linux and no provisioning script had ever executed there.

---

## 4. Outstanding work, with commands

| # | Task | Blocked by | Command / location |
|---|---|---|---|
| 1 | **Remove the diagnostic-only app from the solution in DEV** | Nothing — do this before any real export | The user's `rev_GrantApplications` app was added to `RevitaliseGrantAutomation` as a component for ground-truth diagnostics (§3.1 #4). `RemoveSolutionComponent` rejected every parameter form tried and `solutioncomponent` doesn't support `DELETE`, so do it in the maker portal: Solutions → RevitaliseGrantAutomation → remove the GrantApplications app. **It would otherwise ship to TST/ACC and PRD** |
| 2 | Convert the two calculated columns by hand | Nothing | `rev_applicant.rev_fullname` = `CONCAT(rev_firstname, " ", rev_lastname)`; `rev_application.rev_costs` = `rev_accommodationcost + rev_travelcost + rev_othercost`. Shipped as plain writable columns because no hand-authored `SourceType`/`Formula` shape imports. Maker portal, then re-verify the intake flow still cannot write them |
| 3 | Configure the intake trigger's Entra ID authentication | Alex's integration route (ADR-011) | **The primary security control on the one public endpoint, and it is not expressible in solution source.** Trigger → "Who can trigger the flow?" → `Specific users in my tenant`, Allowed users = the **service principal object id** of `rev-wordpress-intake`. Then `provisioning/entra/verify-intake-endpoint-auth.ps1` must return 401/403. Full detail in `REVIntakeWordPressToDataverse-*.notes.md` |
| 4 | Remaining scripted Entra provisioning | Graph consent limitation | Deploy app registrations ×3 (dev/tstacc/prd), intake client. May need the reviewer to do these manually, as with the security groups |
| 5 | Clean up the unused second certificate | Nothing | Thumbprint `5A31C6C7F5154CE50D7997946750EA8EE816E4F2` was generated when the original's password was thought lost. The original (`A6F94E...E7FE`) is in use. Remove the unused one from the app registration |
| 6 | Bind group teams to security roles in TST/ACC and PRD | Those environments existing | `provisioning/dataverse/bind-roles-to-groups.ps1` — looks roles up by name, so it is id-independent |
| 7 | Install + configure Pipelines | — | Install into `REV_Pipeline_Host`; configure pipeline + 2 stages (Deploy to TST/ACC, Deploy to PRD) |
| 8 | Promote to TST/ACC then PRD | 1–7 | Then produce the Deployment Summary (C-TECH-032) |

**Before the first import into TST/ACC or PRD, re-read §2 Steps 1–2.** `ensure-schema.ps1` must run
there first, and the role/profile ids in source are DEV's. This is the single most likely place for
the next round of avoidable failures.

---

## 5. Still unproven — do not mistake this for finished

DEV deployment being complete narrows the risk list from §7.1 of the Dev Summary considerably, but
these remain untested by execution:

- **No flow has ever run.** Import and designer-save are proven; execution is not. The intake
  endpoint has never received a request, the scoring flow has never scored a row, no Teams message
  has ever been sent, no error-log row has ever been written by the failure handler.
- **`pac solution check` has still never been run** (Dev Summary §7.1, and `dataverse.md` requires it
  before every build).
- **No managed-solution import has been attempted.** DEV took unmanaged. TST/ACC and PRD take
  managed, which is a different code path with its own failure modes.
- **Alternate-key retrieval, `subscriptionRequest/runas: 4`, the `BulkDelete` `QueryExpression`
  serialisation, the field-security-profile→team navigation property, and the
  `rev_applicantid@odata.bind` casing** are all still written from convention (Dev Summary §7.1
  items 4–9). Import does not exercise any of them; only a real run does.
- **Entra permission GUIDs remain `{{PLACEHOLDER}}` tokens.** Scripts fail fast while one remains, so
  this cannot be forgotten silently — but it also means the Entra scripts have not run.
- **The `hint` element shape** in `environmentvariabledefinition.xml` is inferred from `description`'s
  confirmed shape, not observed — the live test object never populated it.

---

## 6. The transferable lesson

Every one of the fifteen failures came from the same source: **a plausible guess about a platform
contract, committed to source, and validated only by something that could not detect it being
wrong.** `pac solution pack` validated layout and passed. The Pester suite validated internal
consistency and passed. The XML gates validated well-formedness and passed. All three were working
correctly; none of them could see the actual defect.

The pattern that broke the cycle, every time, was the same: **stop guessing and create the thing for
real** — via the Web API or the maker portal — **then look at how the platform itself represents it.**
It cost minutes and settled questions that repeated import attempts and documentation research had
not.

The corollary for the next feature: when hand-authoring solution source ahead of a live environment
is unavoidable, mark every guessed shape explicitly as a guess (this project did, in
`§7.1` — and every item that table flagged as unvalidated *did* turn out to be wrong), and treat
"first real environment exists" as the trigger to go and check all of them at once, rather than
discovering them one import at a time.
