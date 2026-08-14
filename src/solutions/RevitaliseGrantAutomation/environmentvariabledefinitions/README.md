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
```

Three environment variable **definitions only** — no `<defaultvalue>`. Every value is
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
