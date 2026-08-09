# Model-Driven Apps — Design Conventions

> 📝 **Populate the App Structure section below with your project's site map.**
> Keep the design rules — they apply to all Power Platform MDA projects.

## What MDAs Are Used For

Process-driven internal UIs: task management, case handling, approval workflows, data entry,
compliance review, and administration. MDAs are the default UI for Dataverse-backed applications.

## App Structure

> 📝 Replace the example below with your project's site map areas and tables.

```
[Your App Name]
├── Site Map
│   ├── Area: [Area 1 — e.g. Work Items]     ([Tables in this area])
│   ├── Area: [Area 2 — e.g. Records]         ([Tables in this area])
│   ├── Area: [Area 3 — e.g. Configuration]   (Lookups, settings — restricted roles)
│   └── Area: [Area 4 — e.g. Administration]  (Admin only)
├── Main Forms      ← one per table; complex tables may have role-specific forms
├── Quick View Forms ← for embedded related record summaries
├── Views           ← Active, My Open, By Status — defined per table
├── Dashboards      ← per role
└── Business Process Flows ← for lifecycle-managed entities
```

## Business Process Flows

> 📝 Define one BPF per entity with a meaningful lifecycle (status progression).

| BPF Name | Table | Stages |
|---|---|---|
| [Entity] Lifecycle | [prefix]_[entity] | [Stage 1] → [Stage 2] → [Stage 3] → [Final] |

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
