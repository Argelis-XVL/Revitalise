# Dev Summary Document — Trustee Portal: org-url-null read-path fix

**Feature Slug:** trustee-portal-org-url-fix
**WBS:** [6.1](../../contract/wbs.json#L902)-[6.5](../../contract/wbs.json#L970) — Trustee Review Portal (defect fix within already-accepted scope, not new scope)
**TAD Reference:** `docs/architecture/revitalise-grant-automation-architecture.md` (ADR-003, §12, C-TECH-048)
**Related, not modified by this session:** `docs/development/trustee-portal-dataverse-service-migration-dev-summary.md` (the 2026-08-23 investigation that scoped this exact migration and stopped short of implementing it — this dispatch is the "future, explicitly-scoped task" it named)
**Date:** 2026-08-23
**Status:** DRAFT

---

## 1. Implementation Summary

Fixed the live defect the reviewer (XLykopoulos@revitalise.org.uk) reported today: every Dataverse
read in the REV Trustee Review Portal Code App failed with `"Invalid organization URL 'null'
provided"` for a real signed-in trustee. Two candidate directions were investigated per the
dispatch instruction; the evidence for each is in
[client.ts:1-38](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L1) and
[IMP-0226](#findings-logged):

- **Direction 1 (fix the generic connector data source directly) is a confirmed dead end, not
  merely untried.** The new `pa` CLI's `app add data-source --connector dataverse` hard-requires
  `--table` (verified: exit code 2, "Missing required option --table"). The older `pac code
  add-data-source -env <org-url>` DOES run against the generic (non-table) form — after clearing
  a stray `pac --non-interactive` process left by the VS Code Power Platform extension holding
  the shared MSAL token cache, the third instance of the class IMP-0216 diagnosed — but the
  regenerated `dataSourcesInfo.ts` still carries empty `tableId`/`version`/`primaryKey` for
  `commondataserviceforapps`, and the org URL string appears nowhere in the file. A
  `dataSourceType: "Connector"` entry structurally has no field to hold one. This diagnostic
  regeneration was reverted (`git checkout --`) after reading it (C-TECH-056).
- **Direction 2 (migrate reads to the four already-generated typed services) is the fix applied
  here.** `client.ts`'s `listRecords`/`getRecord` now dispatch by entity-set name to
  `Rev_applicationsService`, `Rev_reviewsService`, `Rev_applicantsService` and
  `SystemusersService`'s `getAll()`/`get()`. Read from the installed
  `@microsoft/power-apps@1.3.0` package's own shipped source
  (`dataverseDataOperationExecutor.js`), a `dataSourceType: "Dataverse"` entry resolves its
  instance URL from the app's own launch-time runtime metadata
  (`metadataClient.getAppDataSourceConfigsAsync()`) — never from the shared "Microsoft Dataverse"
  OAuth connection's org-url header the generic connector depends on. This is a **structural**
  reason reads on this path are immune to the defect, not an incidental one.

The write path (`saveVerdict` → `updateRecord`) is **unchanged** — still the generic connector's
`executeAsync` + `UpdateOnlyRecord` + `If-Match: '*'` — per `IMP-0210`: the generated services'
`update()` has no way to send `If-Match` and would silently turn "update" into "upsert",
reopening a closed assumption (`A-TR-10`). `repository.ts`, `identity.ts`, `schema.ts`,
`odata.ts` and `types.ts` are **completely unchanged**: only `client.ts`'s internals moved,
exactly as `src/dataverse/README.md`'s original §1 predicted ("this file and client.ts change
and nothing else does").

**Verification reached is V2/V3, not V4 — this is not reported as fixed.** No session working on
this repository has host/browser access to sign in as a real trustee. §11 states exactly what is
and is not proven, and the reviewer's exact next step.

## 2. Components Changed / Created

| Component | Type | Change Description | FR Reference |
|---|---|---|---|
| [src/dataverse/client.ts](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts) | Code App data layer | `listRecords`/`getRecord` now route to the four generated per-table typed services (`Rev_applicationsService`, `Rev_reviewsService`, `Rev_applicantsService`, `SystemusersService`) via a `READ_SERVICES` dispatch table, keyed by entity-set name. `ListRecordsRequest`/`GetRecordRequest`/`UpdateRecordRequest` public shapes unchanged. `updateRecord` unchanged (generic connector, `UpdateOnlyRecord` + `If-Match: '*'`). Added a dual-path 404→null check in `getRecord` (`A-TRM-3`) since the typed path's failure shape (thrown vs. resolved) had not been observed. | FR-034, FR-035, FR-037, FR-038, FR-039 |
| [src/dataverse/client.test.ts](../../src/code-apps/trustee-review-portal/src/dataverse/client.test.ts) | Unit tests | Rewritten to mock `retrieveMultipleRecordsAsync`/`retrieveRecordAsync` (the typed-service SDK calls) instead of asserting `listRecords`/`getRecord` go through `executeAsync`. `updateRecord`'s tests are unchanged in substance — same assertions, same shape, now also assert `retrieveMultipleRecordsAsync`/`retrieveRecordAsync` were **not** called. Added tests for the four-table dispatch, the unregistered-entity-set failure, the comma-split `orderBy`, and both failure shapes (thrown vs. resolved) for 404 and non-404. | — |
| [src/styles/print.test.ts](../../src/code-apps/trustee-review-portal/src/styles/print.test.ts) | Structural test | The "exactly one column allow-list per read" invariant (line ~102) matched the literal `$select:` string, which no longer appears in `client.ts` (the typed services take a plain `select` array; the SDK builds `$select=` internally). Updated the regex to match the new call-site literal `select: [...request.select]`, preserving the same invariant — still exactly 2 matches, one per read function. | — |
| [src/dataverse/README.md](../../src/code-apps/trustee-review-portal/src/dataverse/README.md) | Documentation | §1 rewritten from "the generic connector typing is what this app uses, by choice" to the actual post-fix state: reads on the typed services, write on the generic connector, with the structural reason and an explicit "not yet V4-verified" statement pointing at this document. | — |

No entity, security role, provisioning script, or pipeline config changed. `power.config.json`
and `.power/schemas/**` are unchanged (the diagnostic regeneration described in §1/IMP-0226 was
reverted, not committed).

## 3. Data Model Changes

None.

## 4. Automation / Workflow Changes

None.

## 5. Configuration & Provisioning Changes

None. No new data source was added — the four typed services this fix consumes were already
generated and committed by the 2026-08-22 dispatch (`IMP-0208`/`IMP-0209`).

## 6. Security Controls Implemented

No security control changed; two existing ones were carried forward deliberately and are worth
naming because this exact fix could plausibly have weakened either:

- **The `$select` allow-list discipline** (`src/dataverse/README.md` §1, reason 1). The generated
  services' `IGetAllOptions.select`/`IGetOptions.select` are *optional* — this app's own
  `ListRecordsRequest.select`/`GetRecordRequest.select` stay *mandatory* in `client.ts`
  ([client.ts:236-238](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L236),
  [client.ts:290-297](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L290)),
  so every call site is still compiler-forced to name its columns. This is exactly what
  `docs/development/trustee-portal-dataverse-service-migration-dev-summary.md`'s `A-TRM-2` row
  flagged as the risk to guard against; it is closed by construction here.
- **The `rev_review` never-create guard** (`IMP-0210`, `A-TR-10`). The write stays on
  `UpdateOnlyRecord` + `If-Match: '*'`; the generated `update()` was not adopted for any of the
  four tables, for consistency, even though the write-safety risk is specific to `rev_review`.

`REV_TrusteeRestricted` non-membership as the control on the special-category narrative column is
unaffected — no new column, query, or `$select` was added anywhere in this app.

## 7. Known Limitations / Deferred Items

- **Not V4-verified.** See §11. The reviewer needs to re-run the original reproduction (sign in as
  a real trustee) and confirm the three originally-failing calls now succeed.
- **Direction 1 is now closed as unfixable via CLI**, not merely deprioritised — see `IMP-0226`.
  No future dispatch should re-attempt regenerating the generic connector's data source as a fix
  for this symptom class.
- The four generated services' `create()`/`update()`/`delete()` methods remain uncalled by this
  app for all four tables (unchanged from the prior investigation's finding).
- One Vite build warning, triaged in §11: the production bundle crossed the 500 kB chunk-size
  advisory threshold, because the four generated services (and their `serializeMultiSelectPicklistFields`/`deserializeMultiSelectPicklistFields` imports) are now actually
  bundled rather than dead code. Accepted, not resolved — see §11.

## 8. Build Instructions

No change to `config/<slug>-build.yml` is needed. This app's existing build steps
(`npm run typecheck`, `npm run lint`, `npm test`, `npm run build`) already cover this change;
no new artifact type, provisioning script, or platform limit was introduced.

## 9. Test Guidance

- `npm test` inside `src/code-apps/trustee-review-portal` — 233/233 passing (16 files).
- The tests that matter most for this fix are in `client.test.ts`'s `listRecords`/`getRecord`
  describe blocks: they assert reads call `retrieveMultipleRecordsAsync`/`retrieveRecordAsync`
  and never `executeAsync`, and that `updateRecord`'s tests assert the reverse.
- **What these tests cannot prove**: that the real `@microsoft/power-apps` runtime, inside the
  actual Power Apps host, resolves the per-table `"Dataverse"`-type data sources correctly for a
  real signed-in trustee. That is the V4 step in §11 — test-agent (or the reviewer) should not
  read a green `npm test` as closing this defect.

## 10. Unvalidated Assumptions Register (C-TECH-052)

This document continues the `A-TRM-n` sequence started by
`docs/development/trustee-portal-dataverse-service-migration-dev-summary.md`, which explicitly
said to fold forward rather than start a third sequence once the migration it scoped was
implemented. `A-TRM-1` and `A-TRM-2` are that document's own rows, referenced here as closed;
`A-TRM-3` is new to this dispatch.

| ID | Claim (one sentence) | Where in source | Evidence | Why not verified further | Cheapest verification | Status |
|---|---|---|---|---|---|---|
| A-TRM-1 | The generated services' `update()` sends a plain `PATCH` with no `If-Match`, so it cannot replace `updateRecord()`'s update-only guard. | [client.ts:264-284](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L264) (comment) | E1 — installed `@microsoft/power-apps@1.3.0` shipped source (`IMP-0210`) | N/A | N/A | **CLOSED — negative, from the prior investigation.** Acted on here: the write path was left untouched. |
| A-TRM-2 | Migrating reads to the generated services is mechanically compatible with this app's `$select` allow-lists, but the generated `IGetAllOptions.select`/`IGetOptions.select` are optional where this app's own types must stay mandatory. | [client.ts:220-223](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L220), [client.ts:271-273](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L271) | E1 — both are this app's own committed source | N/A | N/A | **CLOSED by construction.** `ListRecordsRequest.select`/`GetRecordRequest.select` stay `readonly string[]`, mandatory, unchanged from before this fix. |
| A-TRM-3 | A 404 from the typed per-table `get()` call may surface as either a THROWN error or a resolved `{ success: false, error: { status: 404 } }` — which shape the SDK actually uses for a missing row has not been observed live. | [client.ts:279-292](../../src/code-apps/trustee-review-portal/src/dataverse/client.ts#L279) (comment on `getRecord`) | E2 — inferred from the generic connector's own previously-observed (thrown) behaviour plus the installed SDK's executor source, which catches internally for most failures (`dataverseDataOperationExecutor.js`'s `_executeNativeDataverseOperation`) | No host/browser access from this session to request a genuinely deleted id against DEV as a signed-in trustee | Sign in as a trustee, open an application whose id is then deleted directly in Dataverse, and confirm the screen renders "not found" rather than an error toast | OPEN |

Both branches of A-TRM-3 are handled defensively in code (`client.ts`'s `getRecord` checks for a
404 status on both the thrown-exception path and the `unwrap`-thrown-`DataverseError` path), so
the row is informational rather than a blocking gap — whichever shape the SDK actually uses, the
behaviour is correct. It stays open because it has not been *observed*, per `C-TECH-052`'s own
rule that a row is closed by execution, never by the code being defensive enough to not need it.

## 11. Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)

### Verification level reached

| Component | Level reached | Environment / OS | Evidence (command + observed result) |
|---|---|---|---|
| `client.ts` reads (typed-service dispatch) | **V2** (packages) | macOS, this Mac | `npm run build` — `vite build` succeeds, 2275 modules transformed, bundle emitted |
| `client.ts` reads — unit contract | **V1/V2-adjacent, mocked** (not V3) | macOS, Vitest + mocked `@microsoft/power-apps/data` | `npm test` — 233/233 passing; `client.test.ts`'s `listRecords`/`getRecord` describe blocks assert the exact `retrieveMultipleRecordsAsync`/`retrieveRecordAsync` call shape against a **mock**, not a live Dataverse connection |
| `client.ts` write path (`updateRecord`) | **Unchanged from prior verification** | — | Not re-verified live this session; its own tests (unchanged in substance) still pass, and `A-TR-10`'s prior V5 closure (positive + negative control against DEV, 2026-08-22/23) is unaffected because this file's write code path did not change |
| The architectural claim itself — that `dataSourceType: "Dataverse"` resolves its org URL independently of the connector's OAuth binding | **E1** (platform-produced artefact: the installed SDK's own shipped source), **not V-anything** — this is the evidence scale (§2 of the verification skill), not the execution scale | This Mac, `node_modules/@microsoft/power-apps@1.3.0` | Read `dataverseDataOperationExecutor.js`'s `_getDataverseDataSourceInfo`/`getDatabaseReferences`: instance URL comes from `metadataClient.getAppDataSourceConfigsAsync()` (launch-time runtime metadata), never from a connector org-url header |
| Direction 1 (generic connector fixable via CLI) | **Ruled out at E1**, live | This Mac, `pa` 1.0.0 / `pac` 2.4.1 | `pa app add data-source --connector dataverse -c <id> -u <org-url>` (no `--table`): exit 2, "Missing required option --table". `pac code add-data-source -a shared_commondataserviceforapps -c <id> -env <org-url>`: ran to completion (after clearing a stray `pac` process, IMP-0226), regenerated `dataSourcesInfo.ts`, but `tableId`/`version`/`primaryKey` stayed empty and the org URL string appears nowhere in the file — reverted, not committed |
| **The live defect itself — a real signed-in trustee's read succeeding** | **NOT REACHED. V4 not performed.** | — | No host/browser access from this session. **This is the level that matters and it is the one not reached — see the box below.** |

> **This fix is not reported as fixing the live symptom, because it has not been observed to.**
> Per `IMP-0224`'s own finding (which this fix responds to), a clean CLI exit, a clean `tsc`/
> `eslint` run, and 233 passing unit tests are exactly the kind of evidence that was **already
> shown insufficient once** for this exact defect class. What is different this time, and why
> there is a real basis for confidence beyond "it compiles": the architectural claim above (E1,
> read from the SDK's own shipped source) gives a *mechanism*, not just an *absence of the old
> symptom in a test* — the typed per-table path was never observed to depend on the same
> connector binding that failed, at any point in this investigation or the ones before it.
>
> **What the reviewer needs to do to close this**: sign in to the REV Trustee Review Portal as a
> real trustee (the same reproduction IMP-0224 used, XLykopoulos@revitalise.org.uk or any trustee
> account) after this fix is deployed, and confirm all three of the originally-failing calls now
> succeed: the systemuser lookup by Entra object id, the systemuser lookup by domain name (if the
> first fails), and the `rev_applications` list. If all three succeed, close `IMP-0224` (status
> `NEW` → `APPLIED`) with `reobserved: {level: "V4", by: "<name>", ts: "<when>", rerun: "the
> original three-call reproduction", result: "all three succeeded"}` — per `IMP-0225`'s own rule
> that a runtime defect at observable_at ≥ V2 may not close on a needle into prose alone.

### Tool warnings triaged (C-TECH-055)

| Warning | Source step | Resolved / Accepted | Rationale if accepted |
|---|---|---|---|
| `eslint`: 4× `@typescript-eslint/no-unnecessary-type-assertion` on the `READ_SERVICES` map's `as unknown as ReadService` casts | `npm run lint`, first pass | **Resolved** | The casts were unnecessary — TypeScript's structural typing already accepts the generated service classes as `ReadService` by their `getAll`/`get` shape. Removed. |
| `eslint`: 1× `@typescript-eslint/no-unsafe-return` on a mock-calls `.map()` in the new "routes each of the four" test | `npm run lint`, first pass | **Resolved** | Added an explicit `as string` cast on `call[0]`, which `vi.fn().mock.calls` types as `any[]`. |
| Vite: "Some chunks are larger than 500 kB after minification" | `npm run build` | **Accepted** | The bundle grew from including the four generated services (`Rev_applicationsService` etc.) and their `serializeMultiSelectPicklistFields`/`deserializeMultiSelectPicklistFields` imports, which were previously dead code excluded by tree-shaking. This is a Vite advisory threshold, not a Code App platform limit — no host-imposed bundle-size limit is documented for Code Apps. Code-splitting is a reasonable future optimisation but is out of scope for a defect fix; not needed to close `IMP-0224`. |

No warnings from `tsc --noEmit` (clean on every run) or from `pac`/`pa` CLI calls beyond the ones
already recorded as findings (`IMP-0226`).

### Diagnostic components created and removed (C-TECH-056)

| Component | Environment | Purpose | Removed (date / how) |
|---|---|---|---|
| Regenerated `.power/schemas/appschemas/dataSourcesInfo.ts` (via `pac code add-data-source -a shared_commondataserviceforapps -c f31ddadfbe874e50a34054df668e75cf -env https://orge2b20d13.crm17.dynamics.com`) | DEV (`REV-GrantApplications-DEV`), local generated file only — no live Dataverse component was created | Ground-truth check: does the older CLI's `-env` flag embed an organisation URL anywhere in the generic connector's generated data source, settling whether Direction 1 is fixable | 2026-08-23, `git checkout -- src/code-apps/trustee-review-portal/.power/schemas/appschemas/dataSourcesInfo.ts` immediately after reading the diff (never committed) |

No live Dataverse, Entra, or SharePoint component was created or modified by this session. The
one stray process killed (`pac --non-interactive`, PID 62791, the VS Code Power Platform
extension's own bundled binary) was a pre-existing background process on this machine, not a
component this dispatch created — killing it is the discriminating remedy `IMP-0216` already
established, and the extension restarts it on next use.

---

## Findings Logged

| Finding | Class | Severity | Lesson (one line) |
|---|---|---|---|
| [IMP-0226](../../logs/improvement-log.jsonl) | `platform-contract-guessed-not-groundtruthed` | friction | No CLI flag on either Power Apps CLI can fix the generic (non-table) connector data source's org-url-null defect — a `dataSourceType: "Connector"` entry has no field to hold a resolved org URL, so a clean CLI exit proves the schema was refreshed, not that anything was fixed; also, a stray `pac --non-interactive` process (including the one bundled inside the VS Code Power Platform extension) can hang a THIRD distinct `pac` subcommand, per `IMP-0215`/`IMP-0216`'s already-generalised discriminator. |
| [IMP-0227](../../logs/improvement-log.jsonl) | `v3-does-not-imply-v4` | blocker | Migrating a Code App's generic-connector reads to its already-generated per-table typed services is a one-file change when the hand-rolled wrapper's public signatures are kept stable — but a clean build/lint/test run is V2/V3 evidence only, and this defect (`IMP-0224`) was only ever observable at V4, so this entry stays open pending a real signed-in trustee re-running the original reproduction. |

Digest regenerated: YES — `python3 scripts/generate-known-failure-modes.py` (224 entries, 224
distinct lessons, 459 lines)

**Note on `logs/improvement-log.jsonl` gate state**: `python3 scripts/verify-improvement-log.py`
reports 9 pre-existing errors (`IMP-0210`, `IMP-0212`, `IMP-0215`–`IMP-0218`, `IMP-0221`,
`IMP-0224`, `IMP-0225`) missing the `observable_at` field a concurrent session's schema change
(`IMP-0225`, review 16) now requires retroactively for blocker/rework entries appended on or
after 2026-08-23. These predate this dispatch and are not introduced by it — both `IMP-0226` and
`IMP-0227` pass the check cleanly on their own. Retrofitting the 9 pre-existing entries is a
cross-cutting cleanup outside this defect fix's scope and is left for whoever owns review 16.

---

## Code Review Checklist

- [x] All FR IDs covered — FR-034/035/037/038/039 read paths fixed; no FR scope change
- [x] No hardcoded secrets
- [ ] Security controls from TAD §6 implemented — n/a, none changed; existing controls (allow-list, update-only guard) preserved, see §6
- [ ] Every TAD §12 item has an idempotent provisioning script wired into `config/<slug>-pipeline.yml` — n/a, no provisioning change
- [ ] Role assignments via group teams only — n/a, no role change
- [x] No hardcoded environment-specific IDs/URLs — checked by grep against every changed file (C-TECH-047); none found
- [x] Every guessed platform contract is in §10 **and** commented `A-nnn` in source (C-TECH-052)
- [x] Where an environment existed, ground truth was used instead of a guess — both CLI directions tested live rather than assumed (IMP-0226)
- [ ] Every platform limit the packer/compiler does not enforce has a build gate — n/a, no new platform limit introduced
- [x] Verification levels in §11 are the levels actually executed, not the levels expected (C-TECH-053) — explicitly capped at V2/V3, V4 named as NOT performed
- [x] Scripts run on the CI runner's OS — n/a, no new scripts
- [x] Every tool warning triaged in §11 (C-TECH-055); no diagnostic components left in the solution (C-TECH-056)
- [ ] Accessibility requirements met — n/a, no UI change
- [x] No dead code or debug statements
- [x] Unit tests written — client.test.ts rewritten for the new read path; 233/233 passing

## Hours Proposal (development-agent.md → "Propose actual hours while you still know them")

Proposed against **[WBS 6.5](../../contract/wbs.json#L970)** ("Share app to trustee role + access
test") — this is the access-test defect the task itself is: XLykopoulos's live V4 test under 6.5
is what surfaced `IMP-0224`, and this dispatch is the fix for that same test's finding, not new
feature scope.

**Note before the figure**: this is warranty-adjacent rework following an incomplete prior fix
(`IMP-0208`/`IMP-0209` were marked `APPLIED` on V2/V3 evidence that `IMP-0224` and `IMP-0225`
both found insufficient). Whether it is billable, and against which basis, is a `commercial-agent`
decision under `contract/delivery-parameters.json`'s estimating rule — this is a proposal, not a
booking, and `logs/worklog.jsonl` is not written by this agent.

- **Evidence**: investigation (CLI ground-truthing both directions, reading the installed SDK's
  executor source, the diagnostic regeneration and revert) plus implementation (one file rewrite,
  test rewrite, README update) plus verification (typecheck/lint/test/build cycles) — this
  session's tool-call record.
- **Proposed actual**: **2.5 h**, `system` flag: **no** (client-facing defect fix, not tooling on
  `agents/`/`skills`/`scripts/`).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
