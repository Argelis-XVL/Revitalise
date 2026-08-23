# Dev Summary Document — Trustee Portal: generated Dataverse services migration (investigation)

**Feature Slug:** trustee-portal-dataverse-service-migration
**WBS:** [6.1](../../contract/wbs.json#L902) — "Design the trustee Dataverse app + security role" (new, separate work against this task, per reviewer instruction)
**TAD Reference:** `docs/architecture/revitalise-grant-automation-architecture.md` (ADR-003, §12, C-TECH-048)
**Related, NOT modified by this session:** `docs/development/revitalise-grant-automation-dev-summary.md` (in flight, moving to Build in a different session — this document is deliberately separate so as not to collide with it)
**Date:** 2026-08-23
**Status:** DRAFT — **migration NOT performed**, stopped after verification per the dispatch's own explicit instruction

---

## 1. Implementation Summary

**No source file changed.** The task was to replace `src/code-apps/trustee-review-portal/src/dataverse/client.ts` / `repository.ts`'s hand-rolled generic-connector calls with the four generated typed services (`Rev_applicationsService`, `Rev_reviewsService`, `Rev_applicantsService`, `SystemusersService`) committed under `src/code-apps/trustee-review-portal/src/generated/`. The dispatch named three risks to verify before switching and explicitly authorised stopping if any showed a real regression.

Risk 2 (the generated `update()`'s write semantics) is now **ground-truthed, negative, and structural** — not an unresolved unknown that a future session could close later. The generated service's `update()` method has no code path that can send `If-Match: *`, so it cannot enforce this app's "never create a `rev_review` row" requirement the way the current hand-rolled `updateRecord()` does. Per the dispatch's own instruction, this is treated as a reason to stop, not to work around silently. See §10 row `A-TRM-1`.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| — | — | None. No file under `src/code-apps/trustee-review-portal/` was edited. | — |

## 3. Data Model Changes

None.

## 4. Automation / Workflow Changes

None.

## 5. Configuration & Provisioning Changes

None. `power.config.json` and the generated `.power/schemas/` files (owned by the other in-flight session) were read but not touched.

## 6. Security Controls Implemented

None changed. The existing controls this investigation depended on and left untouched:
- The `$select` allow-list discipline in `client.ts` / `schema.ts` (unchanged).
- `REV_TrusteeRestricted` non-membership as the control on `rev_narrativeraw` (unchanged, not implicated by this investigation).
- `updateRecord()`'s `UpdateOnlyRecord` + `If-Match: *` write guard (unchanged — this is the control the investigation confirmed the generated path cannot replicate).

## 7. Known Limitations / Deferred Items

- The four generated typed services remain committed, unused, and structurally sound for **reads** (see §10 `A-TRM-2`) — a future, explicitly-scoped task could migrate `listApplicationsForReview` / `getApplication` / `getReviewForApplication` to the generated `getAll()` / `get()` calls while leaving `saveVerdict`'s write on the existing hand-rolled `executeAsync` + `UpdateOnlyRecord` + `If-Match: *` path unchanged (see §"What you need to decide" in the report). This was not started here: it is a repository-wide call-site change to reviewed, tested code, which the source README already named as a reviewer decision, not a side effect of a connectivity fix.
- The generated services' `update()` method (used by none of this app's call sites) stays uncalled for all four tables — not only `rev_review` — for consistency, even though the write-safety concern is specific to `rev_review`. `rev_application`/`rev_applicant`/`systemuser` are read-only in this app today, so their `update()` methods are simply unused code, not a live risk.

## 8. Build Instructions

Not applicable. No artifact output changed, so `config/revitalise-grant-automation-build.yml` (owned by the other in-flight session) was not touched and no new build config is produced by this dispatch.

## 9. Test Guidance

Not applicable. The existing 228 app tests / 835 repository tests are untouched and were not re-run, because no source they exercise changed (C-TECH-053 — reporting only the level actually executed).

## 10. Unvalidated Assumptions Register (C-TECH-052)

This document uses its own `A-TRM-n` id sequence (Trustee-Review-Migration), deliberately distinct from the canonical `A-TR-n` register in `docs/development/revitalise-grant-automation-dev-summary.md` §10, which this session was told not to edit. If a future session applies any part of this migration, fold these rows into that canonical register rather than maintaining two.

| ID | Claim (one sentence) | Where in source | Evidence | Why not verified further | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-TRM-1 | The generated services' `update(id, changedFields)` (e.g. `Rev_reviewsService.update`) sends a plain Dataverse Web API `PATCH` with no `If-Match` header, and its public signature has no parameter through which one could be supplied — it therefore cannot be used to replace `updateRecord()`'s `UpdateOnlyRecord` + `If-Match: *` guard against `rev_review`. | `src/code-apps/trustee-review-portal/src/generated/services/Rev_reviewsService.ts:27-34`; the same shape holds for the other three generated services' `update()`. | **E1** — read directly from the installed `@microsoft/power-apps@1.3.0` package (the exact version pinned in `src/code-apps/trustee-review-portal/package.json`), not documentation: `dist/data/Data.types.d.ts:14` (the `updateRecordAsync` type has exactly three parameters, no headers/options); `dist/internal/data/core/data/executors/connectorDataOperationExecutor.js:53-63` and `dist/internal/data/core/data/executors/dataverseDataOperationExecutor.js:66-80` (both executors' `updateRecordAsync` call `dataClient.updateDataAsync` with no header argument); `dist/internal/data/core/runtimeClient/runtimeDataClient.js:90-113` (issues a plain `PATCH`) and its header builder at `runtimeDataClient.js:254-320` (`_mergePreferHeaders`/`_createHeaders` never sets `If-Match`, and there is no `config.headers` input in this call path to carry one). | Nothing cheaper is available — this already reads the exact shipped implementation for the exact pinned SDK version, which is stronger evidence than a live call would add (a live PATCH would only reconfirm the same absence; the finding is structural, not probabilistic). | **CLOSED — negative.** The generated `update()` path is unsafe for `rev_review` writes as-is. |
| A-TRM-2 | Migrating **reads** (`getAll`/`get`) to the generated services would be mechanically compatible with this app's `$select` allow-lists, but loses compiler-level enforcement that every call site supplies one. | `src/code-apps/trustee-review-portal/src/generated/models/CommonModels.ts:6-25` (`IGetAllOptions.select?: string[]`, optional) vs. `src/code-apps/trustee-review-portal/src/dataverse/client.ts:149-150` (`ListRecordsRequest.select: readonly string[]`, mandatory). | **E1** — both are this app's own already-committed source; no external evidence needed. | Relevant only if a future task actually attempts the reads-only migration. | If attempted: keep `select` a required field on any new call wrapper around the generated `getAll()`/`get()`, rather than relying on every call site remembering to pass it. | OPEN — informational, blocks nothing today since no reads were migrated. |

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

No component was authored, changed, or packaged this session, so the V1–V6 execution ladder does not apply to shippable output. What was reached is the platform-contract **evidence** ladder (`skills/how-to-verify-a-platform-contract.md` §2) for the specific question this dispatch was told to answer:

| Question | Level reached | Evidence (command / file read + observed result) |
|---|---|---|
| Does the generated `update()` honour `If-Match: *`? | **E1** (platform/vendor-produced artefact: the installed SDK's own shipped source for the exact pinned version) — **not V5**, no live PATCH was sent against DEV | Read `node_modules/@microsoft/power-apps/dist/data/Data.types.d.ts`, `.../internal/data/core/data/executors/{connector,dataverse}DataOperationExecutor.js`, `.../internal/data/core/runtimeClient/runtimeDataClient.js` inside `src/code-apps/trustee-review-portal/`. Result: no code path sets `If-Match`; the public `updateRecordAsync(tableName, recordId, changes)` signature carries no headers parameter at all. |
| Are the four generated services' `update()` implementations the same shape? | E1, by inspection | `grep -n "public static async update" src/code-apps/trustee-review-portal/src/generated/services/*.ts` — all four call the identical `client.updateRecordAsync(...)` pattern. |

### Tool warnings triaged (C-TECH-055)

None emitted. No build, lint, or test command was run, because no source file changed (running them would only reconfirm the pre-existing state already recorded in `docs/development/revitalise-grant-automation-dev-summary.md`'s most recent revision — 228/228 app tests, 97.78% coverage — which this session did not touch).

### Diagnostic components created and removed (C-TECH-056)

None. The finding came entirely from reading already-committed generated source and the installed npm package under `node_modules/`; no live Dataverse call was made and no component was created in any environment.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| IMP-0210 | `platform-fact-groundtruthed` | blocker | To verify a Power Apps Code App generated service's write semantics (headers, method), read the installed `@microsoft/power-apps` package's own shipped source under `node_modules/@microsoft/power-apps/dist/` for the exact pinned version — never assume symmetry with a hand-rolled connector-operation call. The generated `updateRecordAsync(tableName, id, changes)` has a fixed 3-argument signature with no headers parameter and issues a plain `PATCH`; it cannot send `If-Match` and so cannot enforce update-only semantics the way `executeAsync({connectorOperation: {operationName: "UpdateOnlyRecord", parameters: {If_Match: "*", ...}}})` does. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py`

---

## Code Review Checklist

- [x] No hardcoded secrets (nothing written)
- [x] No FR/security control regressed — nothing changed
- [x] Every guessed platform contract is in §10 **and** the evidence level is stated (C-TECH-052) — none are guesses; both rows are E1
- [x] Ground truth used instead of a guess (§skill §3) — read the installed SDK source rather than assuming the generated path mirrors the hand-rolled one
- [x] Verification levels in §11 are the levels actually executed (C-TECH-053)
- [x] Every tool warning triaged (C-TECH-055) — none emitted
- [ ] Not applicable: unit tests, accessibility, provisioning scripts, role assignments — no code changed

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** decision requested — see gate output, not a code-review `APPROVED`
