# Dev Summary Document — <Feature Name>

**Feature Slug:** <slug>
**TAD Reference:** docs/architecture/<slug>-architecture.md
**Date:** <YYYY-MM-DD>
**Status:** DRAFT | APPROVED

---

## 1. Implementation Summary
<!-- What was built, in plain language -->

## 2. Components Changed / Created
| Component | Type | Change Description | FR Reference |
|---|---|---|---|

## 3. Data Model Changes
<!-- Tables / fields / migrations applied. Reference TAD §3 -->

## 4. Automation / Workflow Changes
<!-- Async processes, jobs, event handlers implemented -->

## 5. Configuration & Provisioning Changes
| Key | Environment | Notes |
|---|---|---|

### Provisioning Scripts
<!-- One row per TAD §12 item. Scripts live in provisioning/; every script is
     idempotent (C-TECH-042) and wired into config/<slug>-pipeline.yml. -->

| Script | Purpose | Pipeline Block (tenant_prerequisites / post_deploy:<env>) | Idempotency Check |
|---|---|---|---|

## 6. Security Controls Implemented
<!-- Map each TAD §6 security control to its implementation.
     Include the TAD §6.1 role/group bindings: roles in the solution,
     group teams + role association in provisioning scripts (C-TECH-040). -->

## 7. Known Limitations / Deferred Items

## 8. Build Instructions
<!-- Used by build-agent. Must be complete enough to populate config/<slug>-build.yml -->

## 9. Test Guidance
<!-- Edge cases, known risks, required test data setup. Read by test-agent. -->

---

## Code Review Checklist
- [ ] All FR IDs covered
- [ ] No hardcoded secrets
- [ ] Security controls from TAD §6 implemented
- [ ] Every TAD §12 item has an idempotent provisioning script wired into `config/<slug>-pipeline.yml` (C-TECH-042)
- [ ] Role assignments via group teams only — no direct user assignments in Test/Acc/Prd (C-TECH-040)
- [ ] No hardcoded environment-specific IDs/URLs — environment variables or deployment settings (C-TECH-047)
- [ ] Accessibility requirements met (if UI)
- [ ] No dead code or debug statements
- [ ] Unit tests written

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
