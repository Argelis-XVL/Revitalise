# Deployment Summary — <Feature Name>

**Feature Slug:** <slug>
**Artifact:** build/artifacts/<slug>-<YYYYMMDD>-<n>/
**Date:** <YYYY-MM-DD>

---

## Environment Results
<!-- QUERY THE ENVIRONMENTS YOU ARE NOT DEPLOYING TO, NOT ONLY THE ONE YOU ARE (IMP-0596).
     TST/ACC and PRD promotion is `promote_mode: manual` — it happens in the Power Platform
     Pipelines UI, outside any dispatched agent session, so NOTHING in this repository records it
     unless a session is specifically asked to look. A row inherited from the last summary is a
     claim about live state that no one has checked.

     Before writing this table, run for each environment this feature could have reached:

         pac solution list --environment <env url>

     and record the version and managed/unmanaged state you actually got back. Where a
     promotion has happened since the previous summary, say so and date it; where you did not
     query an environment, write "not queried" rather than "not attempted" — they are different
     claims and only one of them is about the environment.

     IMP-0596: a summary stated "Promotion beyond DEV not attempted" — true of the dispatch, and
     read as a statement about ACC. A live query the next day found the solution already there at
     1.0.0.3, Managed, promoted manually and undocumented. -->
| Environment | Deployed At | Status | Live version (`pac solution list`, queried when?) | Notes |
|---|---|---|---|---|
| Test | | SUCCESS / FAILED / NOT QUERIED | | |
| Acc | | SUCCESS / FAILED / NOT QUERIED | | |
| Prd | | SUCCESS / FAILED / NOT QUERIED | | |

## Tenant-Level Operations
<!-- Every operation executed under the APPROVE TENANT gate (C-TECH-041).
     Reference pipeline.yml tenant_prerequisites block. "None" if not applicable. -->

| Operation | Script | Result (CREATED / EXISTS / FAILED) | Approved Via |
|---|---|---|---|

## Environment Prerequisites (C-TECH-050, C-TECH-051)
<!-- Per environment: everything the deploy could not create, only update — run BEFORE that
     environment's first deploy (pipeline.yml environment_prerequisites, TAD §12.1). Plus
     reconciliation of platform-assigned ids. "N/A — not this environment's first deploy"
     is a valid entry; "skipped" is not. -->

| Environment | Step | Result (CREATED / EXISTS / FAILED) | Ids reconciled |
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

## Verification (C-TECH-053)
<!-- Three separate checks per environment, because passing one does not imply the others.
     (c) is a human step with a named owner and cannot be automated away — three failures on
     this repo's first deployment passed (a) and (b) and still could not be opened. -->

| Environment | (a) Components queried | (b) Deploy re-run clean | (c) Opened + saved by | Level reached |
|---|---|---|---|---|
| Test | <n>/<n> | PASS / FAIL | <name, date> | V3 / V4 |
| Acc | | | | |
| Prd | | | | |

<!-- Name every component still outstanding at (c). An environment with outstanding V4 items
     is DEPLOYED, not VERIFIED — say so here rather than rounding up. -->

## Deployment Warnings Triaged (C-TECH-055)
| Environment | Warning | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|

## Rollback Availability
<!-- Confirm previous artifact version and rollback command are known. -->
Previous artifact: `build/artifacts/<slug>-<previous>/`
Rollback command: `<!-- from pipeline.yml rollback_command -->`

## Issues Encountered
<!-- Any deviations from the pipeline.yml plan during this deployment -->

---

## Findings Logged

Every finding raised while producing this document, per
`skills/how-to-log-an-improvement.md`. `none` is a valid answer; an empty section is not.

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-nnnn | `<class_instance_of>` | friction / rework / blocker | <the imperative sentence that reached the digest> |

Digest regenerated: YES / NO — `python3 scripts/generate-known-failure-modes.py`
