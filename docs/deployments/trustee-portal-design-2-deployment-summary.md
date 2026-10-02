# Deployment Summary — Trustee Portal Design 2.0: the card-layout Code App

**Feature Slug:** trustee-portal-design-2
**Artifact:** build/artifacts/trustee-portal-design-2-20261001-2/
**Date:** 2026-10-01
**Scope:** DEV only (TAD §9.3: the business picks one app before any promotion). wbs:6.3, UNBILLED.
**Status:** PARTIAL — DEPLOYED (V3) to DEV. The new app is not yet in the solution, the share has not run, and V4 is outstanding (all three belong to the reviewer).

---

## Summary

Both trustee apps are live in DEV. The first app was re-pushed with this feature's contract changes. The new card-layout app was pushed for the first time and got its own appId, `b0483396-a875-4c1f-8580-296d433edb4a`. The first app's appId and record were not touched by that push. One surprise: the push did **not** put the new app into the `RevitaliseGrantAutomation` solution, so the reviewer has to add it in the maker portal. The CanView share and the side-by-side V4 are also still waiting on the reviewer.

## Environment Results

| Environment | Deployed At | Status | Live version (`pac solution list`, queried when?) | Notes |
|---|---|---|---|---|
| DEV | 2026-10-01 09:39–09:43 UTC | PARTIAL (V3) | unmanaged, unchanged by this dispatch (no import) | two Code App pushes, one idempotency re-push, flow re-read |
| TST/ACC | not deployed | NOT DEPLOYED by this feature | `RevitaliseGrantAutomation` 1.0.0.4, managed, queried 2026-10-01 09:45 UTC | out of scope per TAD §9.3 |
| PRD | not deployed | NOT DEPLOYED | solution absent, queried 2026-10-01 09:45 UTC | out of scope |

Production guard: not run, because this deploy did not reach PRD. `verify-improvement-log.py --check --target-env dev` exit 0 (0 deploy-open blockers, 1 governance blocker).

## Assumption register override (C-TECH-058)

[C-TECH-058](../../constraints/technology/technology-constraints.md#L128) blocks a deploy past an OPEN row that the deploy could close. [Dev Summary §10](../development/trustee-portal-design-2-dev-summary.md#L197) has exactly nine OPEN rows, and the [test report's decision box](../tests/trustee-portal-design-2-test-report.md#L186) proposed overriding exactly those nine.

**Accepted:** `OVERRIDE A-TR-14 A-TR-15 A-TR-16 A-TR-17 A-CRD-1 A-CRD-2 A-CRD-3 A-CRD-4 A-CRD-5`. Reason: "closes only by the first DEV push".
- authorised_by: reviewer (session account Anna Southern), 2026-10-01
- relayed_by: lead-agent (routing.log 2026-10-01 11:34)
- verbatim turn 1: "Agree with suggested fix for open items"
- verbatim turn 2: "Approved and override"
- Why pipeline-agent accepted words that do not list the ids: the turns answer a single proposal that names all nine rows and gives one reason, and the register holds no other OPEN row. Nothing is left for the words to mean.

**Outcome of re-running the test report's §7.1 after the push:**

| Row | Result | Evidence |
|---|---|---|
| A-TR-14 | **CLOSED, true.** The platform assigned a new appId on first push from `appId: null`, and pac wrote it into `power.config.json` itself. The first app's id and record were unchanged by that push. An idempotency re-push hit the same new id, with no third app. | `pac code list` shows 2 apps; canvasapp `70869c95…` appversion stayed at 2026-10-01T09:39:19Z (its own push) through both `-cards` pushes; [pipeline.log L279](../../logs/pipeline.log#L279), [L281](../../logs/pipeline.log#L281) |
| A-TR-15 | **CLOSED, false (refuted).** The push did not add the second app to the solution. The first app's component is kept. No canvasapp row and no solutioncomponent in any solution exists for `b0483396…`, read at +1, +2 and +3 min and after the re-push. | type-300 rows for `RevitaliseGrantAutomation`: 1 before, 1 after. IMP-1008 |
| A-TR-16 | OPEN. The share has not run. | reviewer step below |
| A-TR-17 | OPEN, avoidable. The new app is outside the solution, so it cannot travel by accident. | — |
| A-CRD-1 | OPEN. Static half holds: the first app's `power.config.json` and canvasapp were unchanged by the `-cards` pushes. Needs both apps opened signed in. | reviewer V4 |
| A-CRD-2..5 | OPEN. Need the Power Apps host. | reviewer V4 |

## Tenant-Level Operations

None. No `APPROVE TENANT` operation was in scope.

## Environment Prerequisites (C-TECH-050, C-TECH-051)

| Environment | Step | Result | Ids reconciled |
|---|---|---|---|
| DEV | `verify-environment-access.ps1 -Env dev` | FAIL: `PROVISION_APP_ID` / `PROVISION_CERT_THUMBPRINT` not set (reviewer-held). pac profile `svc_grantapplications@revitalise.org.uk` → REV-GrantApplications-DEV used for every write | `b0483396-a875-4c1f-8580-296d433edb4a` read back from the push and from `pac code list`, never invented |
| DEV | code-apps feature toggle | EXISTS: enabled since 2026-08-22, proven again by two successful pushes | — |

Excluded because no credential was available: `ensure-schema.ps1`, `reconcile-flow-statecodes.ps1`, `share-apps.ps1` (owner: reviewer). None is needed for this diff, because no schema-shaping source changed.

## Post-Deployment Configuration

| Step | Result |
|---|---|
| Solution import (`alm.stage_dev_command`) | **SKIPPED, no-op.** The unzipped managed and unmanaged trees and `provisioning/` are byte-identical to build `revitalise-grant-automation-20260930-6`, imported 2026-09-30 20:08. No item owes `deploy`. The live flow re-read below confirms there was no drift to correct. Precedent: build 20260930-5. Not re-importing also avoids `--force-overwrite` deactivating flows (IMP-0113). |
| First app `pac code push` | DONE. Same appId `70869c95…`; appversion 2026-09-30T18:08:51Z → 2026-10-01T09:39:19Z. [L277](../../logs/pipeline.log#L277) |
| `-cards` `pac code push` ([config](../../config/revitalise-grant-automation-pipeline.yml#L1194)) | DONE: new app `b0483396…`, then an idempotent re-push. **Solution membership NOT achieved**; maker-portal fallback owed (see below). |
| `-cards` CanView share ([config](../../config/revitalise-grant-automation-pipeline.yml#L1214)) | NOT RUN. Owner: reviewer (admin centre; IMP-0186 breaks the scripted route on this Mac) |
| `verify-live-flow-definitions.py --env dev` | PASS: 10 of 10 flows match source, none modified after the 2026-09-30 18:04 UTC import. [L283](../../logs/pipeline.log#L283) |

`verify-post-deploy-completeness.py --env dev --pending`: exit 0. Its two checkable entries ran; the share is manual and cannot be read from the log.

## Verification (C-TECH-053)

| Environment | (a) Components queried | (b) Re-run clean | (c) Opened + saved by | Level reached |
|---|---|---|---|---|
| DEV | 2 / 2 Code Apps exist (`pac code list`); solution membership 1 / 2 | PASS (`-cards` re-push, same id) | outstanding: reviewer opens both apps | DEPLOYED (V3) |

(a) is derived from the artifact, not hand-written: `code-app/` and `code-app-cards/` each diffed identical to the `dist/` that was pushed. The solution half is unchanged and was not re-imported.

## Items

All 51 carried items (WI-0055 … WI-0105) owe only `operation:code-app-push`. Each moved to `deployed:dev` on the deploy record `{"env":"dev","component":"operation:code-app-push","contains":"trustee-portal-design-2-20261001-2"}`, which resolves on [L277](../../logs/pipeline.log#L277) / [L279](../../logs/pipeline.log#L279). No item is DEPLOYMENT INCOMPLETE by the ledger's rule.

WI-0079's acceptance also names sharing and the side-by-side check. Neither is a declared component of the item, so neither blocks `deployed:dev`, but both are outstanding (reviewer). `verified:dev` is the reviewer's to give.

## Deployment Warnings Triaged (C-TECH-055)

None new. The pushes and fetches emitted no warnings. The build's six warnings are triaged in Dev Summary §11.

## Rollback Availability

DEV only. The first app goes back by re-pushing the previous bundle (`build/artifacts/revitalise-grant-automation-20260930-6/code-app`) from its folder. The card app sits outside every solution, so removing it is one maker-portal delete (Apps → REV Trustee Review Portal (Card layout) → Delete). It has never left DEV.

## Issues Encountered

- **The new app did not land in the solution (A-TR-15 refuted).** IMP-0223's "push registers it" was observed after the first app had been added by hand on 2026-08-22 (IMP-0193). The first app's canvasapp `createdtime` (07:17 UTC) comes four hours before its solution component (11:28 UTC). The DEV config note calling this "SETTLED" is therefore wrong; the correction is proposed in IMP-1008.
- pac rewrote `src/code-apps/trustee-review-portal-cards/power.config.json` without a trailing newline. Content is correct, and the parity gate passes. **Uncommitted**, as is the rest of the card app (test report O-2).

## Reviewer actions

**1. Add the card app to the solution.** In the maker portal: DEV → Solutions → Revitalise Grant Automation → Add existing → App → Code app → *REV Trustee Review Portal (Card layout)* (look under "Outside Dataverse" if it is not listed) → Add.
Verify afterwards (zsh, the reviewer's own terminal):
```
cat > /tmp/sc.xml <<'EOF'
<fetch><entity name="solutioncomponent"><attribute name="objectid"/><attribute name="componenttype"/><filter><condition attribute="componenttype" operator="eq" value="300"/></filter><link-entity name="solution" from="solutionid" to="solutionid"><filter><condition attribute="uniquename" operator="eq" value="RevitaliseGrantAutomation"/></filter></link-entity></entity></fetch>
EOF
pac env fetch --xmlFile /tmp/sc.xml
```
Expect two rows: `70869c95-92e5-442f-b5b9-44b3d3e549f6` and `b0483396-a875-4c1f-8580-296d433edb4a`.

**2. Share the card app, CanView, with the REV Trustees group team.** Use the same team as the first app, in the admin centre (admin.powerplatform.microsoft.com → Environments → DEV → Resources → Apps → *REV Trustee Review Portal (Card layout)* → Share). Then check the role assignment there. The portal confirms the click, not the outcome. After that, add a `dataverse.apps` entry for `b0483396-a875-4c1f-8580-296d433edb4a` (type code, shareWith the trustee group) to `provisioning/deploymentSettings/dev-settings.json`, which has no `apps` block yet.

**3. V4.** A trustee opens both apps side by side and reads the same application in each, in a private window (IMP-0365). That closes A-CRD-1..5 and gives the business its choice.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-1008 | `platform-contract-guessed-not-groundtruthed` | friction | On this tenant `pac code push --solutionName` does not put a new Code App into the named solution; read solutioncomponents by objectid after a first push and use maker-portal Add existing if it is absent. |

Digest regenerated: YES. `verify-improvement-log.py` OK (schema), `--check --target-env dev` exit 0.

Findings queued for the post-deploy batch: 30 (30 unread + 0 fixed-in-flight).
