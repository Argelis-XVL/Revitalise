# Environment variable definitions - no XML declaration, no comment, in the `.xml` files

Every other component type in this solution source ships its `.xml` file with a leading
`<?xml version="1.0" encoding="utf-8"?>` declaration and a long header comment explaining the
component. **These three files cannot carry either.** This file exists to hold that explanation
instead, and to record why it had to move here.

## What's in this folder

```
environmentvariabledefinitions/
  rev_ProcessOwnerUpn/environmentvariabledefinition.xml
  rev_ServiceMailbox/environmentvariabledefinition.xml
  rev_IntakeAllowedClientId/environmentvariabledefinition.xml
  rev_SpoSignedAcceptanceUrl/environmentvariabledefinition.xml   <- added 2026-08-18 (WBS 0.4-R)
  rev_GrantAdminAppUrl/environmentvariabledefinition.xml         <- added 2026-08-20
  rev_DocuSignAccountId/environmentvariabledefinition.xml        <- added 2026-09-06 (wbs:3.2)
  rev_DocuSignAcceptanceTemplateId/environmentvariabledefinition.xml <- added 2026-09-06 (wbs:3.2)
  rev_SpoSiteUrl/environmentvariabledefinition.xml                <- added 2026-09-06 (wbs:3.4)
```

**`rev_DocuSignAccountId`** and **`rev_DocuSignAcceptanceTemplateId`** (added 2026-09-06,
`wbs:3.2`, EX-006/EX-007) are read by `REV | Acceptance | Create Envelope`. A DocuSign account
and its templates both live inside one DocuSign tenant, so both values are deployment values by
the same C-TECH-047 reasoning as every other row in this file — a later environment pointed at a
different DocuSign account needs its own account ID and its own template ID, never the DEV
values copied across. Both are `isrequired=1`: the flow cannot build an envelope with either
missing. Neither has a `<defaultvalue>` here, for the same reason none of the others do — the
current value is set by hand for DEV as a `post_deploy` step
(`config/revitalise-grant-automation-pipeline.yml`), same pattern as `rev_GrantAdminAppUrl`.

**`rev_SpoSignedAcceptanceUrl`** (added 2026-08-18) holds the server-relative URL of the
SharePoint library containing signed acceptance PDFs (ADR-014, ADR-G01). One library per
environment inside a single designated site, so the value differs per environment and is never
committed (C-TECH-047). **Now read by `REV | Acceptance | Completion` (wbs:3.4, added
2026-09-06)** — the `folderPath` for the Create file action that uploads the signed PDF.
`isrequired` changed from `0` to `1` on 2026-09-06: the flow cannot pick a library to upload
into without it, the same reasoning as the DocuSign pair below.

**`rev_SpoSiteUrl`** (added 2026-09-06, `wbs:3.4`) holds the absolute URL of THIS environment's
designated SharePoint site — the `dataset` (site address) for the same Create file action.
Paired with `rev_SpoSignedAcceptanceUrl` above: the site is one value, the library path inside
it is another, because `provisioning/sharepoint/ensure-site.ps1` provisions one site collection
PER environment (never a site shared across environments), so both values are environment
specific even though the two libraries sit inside what the TAD calls "the single designated
site" conceptually. `isrequired` is `1`, for the same reason as `rev_SpoSignedAcceptanceUrl`.
**No example URL appears in this file's own description** — see the paragraph below on why an
illustrative SharePoint URL is not safe to write here.

**`rev_GrantAdminAppUrl`** (added 2026-08-20) holds the base URL of the REV Grant
Administration app for the environment, up to and including the `appid` parameter. The daily
summary appends `&pagetype=entitylist&etn=rev_application&viewid=<id>` to it so each
"waiting for you now" line is a link straight into the right view. The view ids come from the
solution's own `SavedQueries` and are the same in every environment; the host and the `appid`
are both assigned per environment, which is why the whole prefix is a deployment value.
`isrequired` is `0`: leave it empty and the summary still sends, with the view names as plain
text and a line telling the reader how to turn them into links.

**Its description carries no example URL, deliberately.** The first draft included an
illustrative organisation address. The `no-hardcoded-environment-values` gate greps ALL of
solution source case-INSENSITIVELY for the organisation-host pattern, so an example address is
indistinguishable from a real one and the build failed - and then failed a second time on this
very paragraph, when it first quoted the example it was warning about. The description now says
where to copy the value from instead of showing its shape. An example that cannot be written is
a small price for a gate that cannot be talked around.

**This file's rule was learned the hard way a second time.** The definition was first authored
with the project's usual 19-line header comment. `verify-source-parses.py` passed (it is valid
XML), `pac solution pack` exited 0, and the solution import then failed with
`0x80040216 - An unexpected error occurred` at `ImportXml.GetComponentsList`, naming nothing.
Four import attempts and a bisection down to a single component identified it. The rule at the
top of this file already said so. See `IMP-0045`.

Four environment variable **definitions only** — no `<defaultvalue>`. Every value is
environment specific and is injected at import time from
`provisioning/deploymentSettings/pac-import-<env>.json` (C-TECH-031, C-TECH-047), so the
managed artifact carries no environment URL, mailbox or tenant identifier at all.

- **rev_ProcessOwnerUpn** - the user Teams 1:1 notifications are sent to: new application
  (FR-009), Borderline awaiting review (FR-019), daily summary (FR-021) and failure alerts
  (FR-010). Held as an environment variable rather than in the flow so that a change of process
  owner is a deployment setting, not a solution change (C-TECH-047).
- **rev_ServiceMailbox** - the Microsoft 365 mailbox the automations send from and fall back to
  when the Teams connector is unavailable (TAD section 4). Per-environment value: in TST/ACC
  this is a test mailbox, in PRD it is the service account mailbox.
- **rev_IntakeAllowedClientId** - the Entra application (client) ID of the WordPress site, the
  only caller the intake endpoint accepts (NFR-008, C-TECH-006). A client ID is a public
  identifier, not a secret, so it is a plain environment variable and NOT a secret-type variable
  (TAD section 6.3, ADR-011).

## Directory, file name and shape - all three are ground truth, not a guess

Rewritten complete 2026-08-14. The original files lived flat at
`EnvironmentVariables/<schemaname>.xml`, on the strength of a decompiled-source claim that
`EnvVariablesProcessor` reads only that folder and "does not look at an
`environmentvariabledefinitions/` folder at all." That claim held up right through
`pac solution pack`, which produced no warning specific to this component beyond the generic
"root components are not defined in customizations" pack-time warning present since this
project's very first pack and left uninvestigated as background noise - which turned out to be
this exact bug the whole time. It surfaced only once a live import reached a Workflow that binds
to one of these variables: **"Failed to find environment variables with schema name(s)
'rev_ProcessOwnerUpn'."** Dataverse genuinely had no definition by that name, because
`SolutionPackagerLib` had silently swept the flat-folder file into the package as an anonymous,
unregistered blob instead of a real component.

Confirmed by creating a real environment variable definition directly via the Web API (POST
`environmentvariabledefinitions` - the entity is not on the
create-via-solution-import-unsupported list, see `ensure-schema.ps1`'s header), then
`pac solution export` + `pac solution unpack` against pac CLI 2.4.1: the real, current layout is
`environmentvariabledefinitions/<schemaname>/environmentvariabledefinition.xml` - lowercase,
plural, one folder per variable - exactly the layout the original comment dismissed as
superseded. pac's own unpack behaviour changed at some point after that decompiled read was
taken; nothing about the underlying platform reasoning was wrong, only which version of the
packer it described.

**Second bug, found immediately after fixing the first:** moving the files into the correct
folder surfaced a *new* failure, even earlier in the import (before any per-component result
appears) - `System.InvalidOperationException: The specified node cannot be inserted as the valid
child of this node, because the specified node is the wrong type`, thrown inside
`Microsoft.Crm.Tools.ImportExportPublish.SourceControlHandler.ImportEntityFromFile`. Every other
component type in this solution is handled by its own dedicated processor and tolerates a
leading XML declaration plus a long header comment without issue; `SourceControlHandler` is
evidently the generic fallback used for component types (like this one) with no dedicated
per-file processor, and it does not tolerate that same preamble. The real exported file (from
the same live diagnostic export above) confirmed this directly: it has **no XML declaration and
no comment at all** - it starts straight at `<environmentvariabledefinition ...>`. The three
files in this folder were rewritten to match that exactly, which is why this explanation lives
here instead of at the top of each file.

## The element shape inside each file

- No `<environmentvariabledefinitionid>`. Dataverse assigns it on creation, the same as every
  other id this project has hit this exact pattern for (Role, FieldSecurityProfile, sitemapid,
  appmoduleid) - never declared in source.
- `<description>` and `<displayname>` are not flat text. Both carry a `default` ATTRIBUTE plus a
  nested `<label description="..." languagecode="1033" />` child - the same localizable-label
  convention as `LocalizedNames` elsewhere in this solution, just spelled differently for this
  component.
- `<hint>` is inferred to follow the same `default` + `<label>` shape, since it is the same kind
  of user-facing text as `description` - the live-created test object never populated `hint`, so
  a real export never confirmed this one directly. If a future import ever complains about hint
  specifically, this is the assumption to revisit first.
- No `<RootComponentBehavior>` and no duplicated `introducedversion`/`IntroducedVersion` pair.
  Neither appears in a real export; `<introducedversion>` (lowercase) appears exactly once.
