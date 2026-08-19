# Model-Driven Apps — Design Conventions

**Populated 2026-08-19** from the shipped
`src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/`. The
App Structure and Business Process Flow sections below were still `[Your App Name]` /
`[Area 1 — e.g. Work Items]` scaffolding, in a file `architect-agent` loads on every
activation and `development-agent` loads for any MDA work. The design rules were always real
and are unchanged.

## What MDAs Are Used For

Process-driven internal UIs: task management, case handling, approval workflows, data entry,
compliance review, and administration. MDAs are the default UI for Dataverse-backed applications.

## App Structure

There is **one** model-driven app: `rev_grantadministration`, display name
**REV Grant Administration**. This is the shipped site map, read back from source.

```
REV Grant Administration                     (AppModules/rev_grantadministration/)
└── Area: Grant Administration               rev_area_grantadmin
    ├── Group: Casework                      rev_group_casework
    │   ├── Applications                     rev_application  → AllApplications / ActiveApplications
    │   ├── Borderline - Awaiting Review     rev_application  → BorderlineAwaitingReview
    │   ├── Under Review - Incomplete Scoring rev_application → UnderReviewIncompleteScoring
    │   ├── Auto-rejected Applications       rev_application  → AutoRejectedApplications
    │   └── Applicants                       rev_applicant    → ActiveApplicants
    ├── Group: Configuration                 rev_group_configuration
    │   └── Settings                         rev_setting      → AllSettings
    └── Group: Operations                    rev_group_operations
        └── Error Log                        rev_errorlog     → UnresolvedErrors
```

⚠️ **`rev_grant` is not in the site map.** The grant table shipped in WBS 0.4 with an
`Entity.xml`, a main form and three saved queries (`AllGrants`, `AwaitingAcceptance`,
`AcceptanceSigned`), and no `SubArea` referencing it — so none of that is reachable from the
app's navigation. Adding a table is therefore **two** changes, not one, and nothing currently
gates the second: `verify-forms-and-views-reachable.py` checks that FormXml and SavedQueries
are reachable from `Entity.xml` at *pack* time, which is a different question from whether a
human can reach them in the *app*. Recorded 2026-08-19.

**The four-area template this section used to show does not describe this app.** One area,
three groups. Do not create areas to match a diagram.

## Business Process Flows

**This solution ships no BPF, deliberately.** Application lifecycle is driven by the
`rev_applicationstatus` / `rev_grantstatus` option sets plus the scoring and intake cloud
flows, with the monthly trustee panel as an out-of-system decision point. A BPF would put a
second, competing state machine beside the one the flows already enforce.

Where a future entity does get one, the rule below still applies — one BPF per entity with a
meaningful lifecycle, and its stages must map to that entity's status option set rather than
inventing a parallel vocabulary.

## Form Design Rules

- Each table has **one canonical Main Form**; do not create multiple main forms unless role isolation requires it
- All forms use **tabs** for logical grouping; no endless single-column scrolling
- Required fields are marked; tooltips explain compliance-critical fields
- Read-only fields for system-managed values (audit columns, calculated values)
- Related records shown via **Sub-grids** on the main form, not separate views

## Views — Mandatory Set Per Table

Every custom table must have at minimum:

| View | Filter |
|---|---|
| Active `<TableName>s` | statecode = Active |
| My Open `<TableName>s` | statecode = Active AND ownerid = current user |
| All `<TableName>s` | No filter — admin use |

## JavaScript Web Resources

Use sparingly. Permitted for:
- Client-side field formatting (e.g. masking sensitive data on display)
- Complex form UX that cannot be expressed as a Business Rule
- Calling a custom API action from a ribbon button

Prohibited:
- Directly querying Dataverse from JS (use custom API actions or Power Automate instead)
- Business logic that belongs in a server-side plugin or flow

All JS web resources must pass ESLint with the project ruleset before commit.

## Accessibility

All MDAs must meet WCAG 2.1 Level AA.
Power Platform's default MDA shell meets most baseline requirements.
Custom web resources are the primary accessibility risk — see `skills/accessibility-checklist.md`.
