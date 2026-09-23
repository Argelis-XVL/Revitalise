# Quick View Form — real FormXml shapes (ground truth, read live from DEV)

**Read 2026-09-23 by identity-agent, read-only, against REV-GrantApplications-DEV
(`svc_grantapplications@revitalise.org.uk`, `pac auth select --index 2`).** Feeds EF-01, EF-38,
EF-36 (assumption-register rows A-LOC-1, A-ATYPE-1, A-AGE-1 in
`docs/development/revitalise-grant-automation-dev-summary.md`).

## Route that actually works — correction to the prior handoff

The handoff suggested `pac power-fx run`. **That does not work for this.** `pac power-fx run`
is a standalone Power Fx formula REPL (Abs/Filter/Sort/etc.) — it is not connected to Dataverse
tables even with an active `pac auth` profile selected; `SystemForms` is not a recognised name in
it, and there is no `Connect-DataverseTable`-style command to add one. Confirmed live:
`CountRows(SystemForms)` → `'SystemForms' isn't recognized`.

**The route that works is `pac env fetch --xmlFile <path>`** (FetchXML against the live
environment, read-only, no `--environment` needed once a profile is selected — it uses the
active `pac auth` profile). This is the same tool `ensure-schema.ps1`-adjacent investigation used
for the pre-state check in IMP-0245. Two gotchas hit along the way:

- `<fetch top="N">` cannot be combined with paging — Dataverse's own fetch executor returns
  `The top attribute can't be specified with paging attribute page`. Omit `top`; page in FetchXML
  is applied automatically by `pac env fetch` and truncation wasn't a problem at this row count.
- `like` filters DO work against `formxml` (an ntext column) — `%quickview%` and `%5C5600E0%`
  both matched correctly. No special escaping was needed beyond ordinary FetchXML.

## systemform `type` option set — real values, not guessed

Confirmed live via `stringmap` is NOT queryable this way (`objecttypecode` on `stringmap` wants
an integer object-type-code, not the `systemform` schema name — that lookup was not pursued
further because the more direct route below worked immediately). Instead, confirmed by fetching
`systemform` rows filtered `type eq 6` and reading the `type` column back as its label:

```xml
<fetch>
  <entity name="systemform">
    <attribute name="name" /><attribute name="objecttypecode" />
    <attribute name="type" /><attribute name="formid" />
    <filter><condition attribute="type" operator="eq" value="6" /></filter>
  </entity>
</fetch>
```

Every row returned had `type = "Quick View Form"` (57 rows, out-of-box tables — Contact,
Account, Knowledge Article, etc., plus this solution's own custom tables e.g. "Round Finance",
"Anonymised Statistic", "Approval Request", "Approval Step" already have OOB-style Information
quick view forms). **`type=6` is confirmed live as Quick View Form's real option-set value** in
this environment — matches the documented Microsoft value, no drift found.

## Shape 1 — a Quick View Form's own FormXml (the entry point form)

Example pulled: "contact card" on `Contact` (`formid 707fc57b-c5e6-471b-a180-e37ed28a38e2`).
A Quick View Form's FormXml is a normal `<form>`/`<tabs>`/`<tab>`/`<columns>`/`<sections>`/`<rows>`/
`<cell>`/`<control>` tree, structurally identical to a Main form's, with two differences:

- `<form hasmargin="false" shownavigationbar="false">` — both attributes present, set to false.
- `<ancestor id="{<own-formid>}" />` as the form's first child, immediately inside `<form>`,
  before `<tabs>`. The ancestor id is the Quick View Form's OWN formid (self-reference), not the
  host form's.

Each field is an ordinary `<control>` (e.g. `classid="{4273EDBD-AC1D-40d3-9FB2-095C621B552D}"` for
a text field, `datafieldname="fullname"`) — read-only rendering is enforced by the platform when
the form is hosted as a quick view, not by anything in this FormXml itself. Full example saved at
`docs/development/quick-view-form-formxml-reference.md` (this file, below) is the exact XML pulled;
raw dump also left in the scratch fetch output if development-agent wants to re-pull it — this
summary already carries what's load-bearing.

## Shape 2 — embedding a Quick View Form on a parent form (`quickviewcontrol`)

Found by searching `systemform.formxml LIKE '%5C5600E0%'` (the quickviewcontrol classid) — 4
out-of-box hosts matched: Account main form (both variants) and Social Profile main form (both
variants). Pulled Account's main form (`formid 8448b78f-8f42-454e-8e2a-f8196b0419af`), which
embeds Contact's "Primary Contact" quick view on the `primarycontactid` lookup field. The exact
control, verbatim from the live FormXml:

```xml
<control id="contactquickform"
         classid="{5C5600E0-1D6E-4205-A272-BE80DA87FD42}"
         datafieldname="primarycontactid"
         disabled="false">
  <parameters>
    <QuickForms>&lt;QuickFormIds&gt;&lt;QuickFormId entityname="contact"&gt;29DE27BC-A257-4F29-99CF-BAB4A84E688F&lt;/QuickFormId&gt;&lt;/QuickFormIds&gt;</QuickForms>
    <ControlMode>Edit</ControlMode>
  </parameters>
</control>
```

Load-bearing details for building EF-01/EF-38/EF-36 from this:

- **`classid` is the fixed platform GUID for the Quick View control**:
  `{5C5600E0-1D6E-4205-A272-BE80DA87FD42}`. This is not schema-specific; use it verbatim.
- **`datafieldname` is the LOOKUP field on the host form's entity that points at the source
  record** — here `primarycontactid` (Account → Contact lookup). For Application →
  Applicant, this is whatever lookup field the Application form already carries to the
  Applicant record (check the TAD/existing Application FormXml for its logical name — this
  wasn't re-derived here, it's schema-specific to this solution, not the platform shape).
- **`<QuickForms>` is a URL-encoded-entity-escaped XML STRING, not real nested XML** — the
  `&lt;`/`&gt;` escaping is exactly as shown; it decodes to
  `<QuickFormIds><QuickFormId entityname="contact">29DE27BC-...</QuickFormId></QuickFormIds>`.
  The GUID inside is the target Quick View Form's own `formid` (i.e. the Quick View Form built
  per Shape 1 above) and `entityname` is that quick view form's target entity's logical name
  (`contact` here → would be `rev_applicant` or equivalent for this solution).
- `<ControlMode>Edit</ControlMode>` was present on this OOB example; the option set for this
  parameter and whether `Edit` vs another value affects read-only rendering was not investigated
  further — worth a quick check before copying verbatim if edit-ability matters for EF-01/EF-38/
  EF-36 (the assumption register frames these as read-only display, so this may need
  confirmation or may not matter — flagging rather than guessing).
- The `<control>` sits inside an ordinary `<cell>`/`<row>`/`<section>` exactly like any other
  field control — no special parent wrapper beyond the normal form tree.

## What was NOT investigated (explicitly out of scope for this pass)

- Whether `ControlMode` other than `Edit` exists/matters.
- The Application form's actual lookup field name to Applicant (schema-specific — development-
  agent should pull this from the existing `rev_application` FormXml already in
  `src/solutions/RevitaliseGrantAutomation/Entities/rev_application/FormXml/`, not from here).
- `tst_acc`/`prd` — this was read against DEV only, per the read-only/DEV-only instruction in the
  handoff. No writes were made anywhere.
