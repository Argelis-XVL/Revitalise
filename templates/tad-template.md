# Technical Architecture Document — <Feature Name>

**Feature Slug:** <slug>
**SDD Reference:** docs/plans/<slug>-plan.md
**Date:** <YYYY-MM-DD>
**Status:** DRAFT | APPROVED

---

## 1. Architecture Overview
<!-- High-level approach. Why this design? What alternatives were rejected? -->

## 2. Component Diagram
<!-- Load skills/how-to-document-architecture.md before completing §2–§3 -->
<!-- Use Mermaid or ASCII. Minimum: context diagram + component diagram -->

```mermaid
graph LR
  A[Component A] --> B[Component B]
```

## 3. Data Model
<!-- Load skills/how-to-model-a-data-schema.md and skills/data-classification.md -->

### Entities
| Entity | Purpose | Classification |
|---|---|---|

### Relationships
<!-- FK references, cardinality, cascade behaviour -->

### Migration Strategy
<!-- How schema changes are applied across environments -->

## 4. Integration Design
| Integration | Direction | Protocol | Auth Method |
|---|---|---|---|

<!-- A REQUEST/RESPONSE CONTRACT GIVEN AS A WORKED JSON EXAMPLE IS NOT A SPECIFICATION UNTIL
     ALL FOUR OF THESE ARE TRUE. Tick them before this section is approved.

     [ ] Every output and parameter is NAMED explicitly — including the trigger's or response
         action's OWN output name. "One Text output carrying one JSON document" names nothing;
         the client author has to invent an identifier and the flow author has to guess it.
     [ ] Every enumerated status/enum value has its stated wording. A value that appears only
         in an enum comment, with no row in the wording table, is undecided.
     [ ] Where two fields name the SAME fact, say which is authoritative — or mark the
         redundancy deliberate and say why.
     [ ] Where a value is obtainable from two sources (a direct table read AND the response),
         say which one a client uses.

     WHY THIS IS A CHECKLIST AND NOT A NOTE (IMP-0331, IMP-0302, IMP-0158 — third instance of
     "approved document internally inconsistent"). A worked example reads as COMPLETE because
     every key present in it looks resolved, even where what the key MEANS was never decided.
     An approved, revision-2 response contract passed review with all four of these open; all
     four surfaced only when someone had to type the contract into TypeScript, and each became
     a judgement call made alone by one implementer that the other could legitimately disagree
     with. No gate checks this — a check comparing a jsonc block against its own prose tables
     would be prose-matching regex number six — so the catch is here, at authoring time. -->

## 5. Automation / Workflow Design
<!-- Load skills/how-to-design-a-workflow.md -->
<!-- Describe async processes, triggers, scheduled jobs. Include flowchart. -->

## 6. Security Design
<!-- Load skills/compliance-checklist.md §1.2 and §1.3 -->
<!-- Load knowledge/technology/security-model.md for role/team/group design -->

| Concern | Control | Where Applied |
|---|---|---|
| Authentication | | |
| Authorisation | | |
| Data at rest | | |
| Data in transit | | |
| Audit logging | | |
| App registrations / API permissions | | |

### 6.1 Security Role & Group Mapping
<!-- Mandatory for any feature touching security. One row per persona (C-TECH-040). -->

| Persona | Entra Security Group | Dataverse Group Team | Security Role(s) | App Access |
|---|---|---|---|---|

## 7. Non-Functional Decisions
| NFR ID | Decision | Rationale |
|---|---|---|

## 8. Accessibility
<!-- Load skills/accessibility-checklist.md for any UI components -->

## 9. Deployment Topology
| Environment | Method | Notes |
|---|---|---|
| Dev | | |
| Test | | |
| Acc | | |
| Prd | | |

## 10. Architecture Decision Records
<!-- One ADR per significant choice. Format: Context / Decision / Consequences -->

### ADR-001: <Title>
**Context:** …  **Decision:** …  **Consequences:** …

## 11. Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

## 12. Provisioning & External Dependencies
<!-- Every component that CANNOT ship in the solution: app registrations, admin consent,
     security groups, SPO sites, teams, Teams app catalog entries, group-team role
     bindings, app sharing. Each row maps to a script in provisioning/ and a block in
     config/<slug>-pipeline.yml. Scope: "tenant" → tenant_prerequisites (APPROVE TENANT);
     "per-env" → post_deploy. All scripts idempotent (C-TECH-042). -->

| Item | Type | Tool / Script | Scope | Gate |
|---|---|---|---|---|

### 12.1 Environment Prerequisites — before the FIRST deploy into any environment
<!-- Components the target platform will NOT create from a deploy/import, and state that must
     exist before the first one. On Power Platform this is C-TECH-050: Entities/Attributes,
     Global OptionSets, Security Roles and Field Security Profiles are documented as
     unsupported to create from scratch via solution import — they are created via the
     Web API first, then import can manage them.

     This is PER ENVIRONMENT, not per feature: it runs again for DEV, TST/ACC and PRD.
     Each row maps to an idempotent script in provisioning/ and to the
     `environment_prerequisites` block in config/<slug>-pipeline.yml. Getting this wrong is
     the single most likely source of avoidable first-import failures. -->

| Item | Why a deploy cannot create it | Script | Runs before | Re-run per environment? |
|---|---|---|---|---|

### 12.2 Platform Contract Verification Plan
<!-- Load skills/how-to-verify-a-platform-contract.md.

     Any component whose serialisation, layout, limits, or id assignment must be
     hand-authored ahead of a live environment. For each, state how ground truth will be
     obtained (create a minimal real instance → export/unpack → copy the shape exactly), and
     which values the platform assigns rather than accepts (C-TECH-051).

     If no environment exists yet, this table becomes the development-agent's Unvalidated
     Assumptions Register (Dev Summary §10) and is closed in one sweep when the first
     environment appears — before the first deploy, not one failure at a time. -->

| Component | Hand-authored? | Ground-truth method | Platform-assigned values | Verified at |
|---|---|---|---|---|

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
