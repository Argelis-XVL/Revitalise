# Deployment Summary — <Feature Name>

**Feature Slug:** <slug>
**Artifact:** build/artifacts/<slug>-<YYYYMMDD>-<n>/
**Date:** <YYYY-MM-DD>

---

## Environment Results
| Environment | Deployed At | Status | Notes |
|---|---|---|---|
| Test | | SUCCESS / FAILED | |
| Acc | | SUCCESS / FAILED | |
| Prd | | SUCCESS / FAILED | |

## Tenant-Level Operations
<!-- Every operation executed under the APPROVE TENANT gate (C-TECH-041).
     Reference pipeline.yml tenant_prerequisites block. "None" if not applicable. -->

| Operation | Script | Result (CREATED / EXISTS / FAILED) | Approved Via |
|---|---|---|---|

## Post-Deployment Configuration
<!-- Results of every post_deploy step per environment (group teams, role bindings,
     document locations, Teams app install, app sharing). -->

| Environment | Step | Result (CREATED / EXISTS / FAILED) |
|---|---|---|

## Post-Deployment Smoke Tests
<!-- Results per environment. Reference pipeline.yml smoke_tests block. -->

| Environment | Test | Result |
|---|---|---|

## Rollback Availability
<!-- Confirm previous artifact version and rollback command are known. -->
Previous artifact: `build/artifacts/<slug>-<previous>/`
Rollback command: `<!-- from pipeline.yml rollback_command -->`

## Issues Encountered
<!-- Any deviations from the pipeline.yml plan during this deployment -->
