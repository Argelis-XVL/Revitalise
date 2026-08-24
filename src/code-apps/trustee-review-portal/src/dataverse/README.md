# `src/dataverse/` — the one place this app talks to Dataverse

Everything in the app above this folder talks to the **repository interface** in
`repository.ts`. Nothing else in `src/` imports `client.ts`, `schema.ts` or the Power
Apps SDK. That is the design rule, and it exists for two reasons.

## 1. Reads use the four typed per-table services; the write stays on the generic connector

**Updated 2026-08-23 — reads migrated (IMP-0224); the generic connector was never fixable for
this app.** Full history:

`pac code add-data-source -a shared_commondataserviceforapps -c <connection>` (old `pac` CLI, no
org URL flag) generated only the generic Dataverse connector surface, and `pac code list-tables`
/ `list-datasets` failed against this connection on three dataset forms — both confirmed
2026-08-21. That was read as "the typed-per-table route is unreachable here" and left as an open
assumption (`A-TR-6` at the time). It was the wrong conclusion, not just an unresolved one
(`IMP-0208`, `IMP-0209`): the newer `pa` CLI's `app add data-source --connector dataverse --table
<logical-name> -u <org-url> -c <connection-id>` **does** resolve a per-table dataset against this
exact connection, once the organisation URL is passed explicitly. Run 2026-08-22 for
`rev_application`, `rev_review`, `rev_applicant` and `systemuser`: all four succeeded, produced
real per-table models and services (`src/generated/models/Rev_reviewsModel.ts` etc.), and none
of the four carries the `MSCRM.IncludeMipSensitivityLabel` parse defect in §2 below.

**That fix did not fix this app**, because `client.ts` at the time still called the GENERIC
connector data source (`commondataserviceforapps`) for every read, and regenerating the four
PER-TABLE datasets never touched it. A real signed-in trustee (XLykopoulos, 2026-08-23) hit the
identical "Invalid organization URL 'null' provided" error the day after IMP-0208/IMP-0209 were
marked APPLIED — IMP-0224 diagnosed why: `-u`/`--org-url` is a flag on `pa app add data-source
--table <t>` with **no equivalent for the generic (non-table) form of the same command**, which
still requires `--table` in non-interactive mode (verified live, exit code 2, "Missing required
option --table") and cannot be regenerated with an explicit org URL any way this project has
found. The older `pac code add-data-source -env <org-url>` flag exists but hangs indefinitely on
this toolchain rather than completing (verified live, 2026-08-23 — a new instance of the `pac`
CLI hang class first recorded in IMP-0215).

**So `client.ts`'s reads (`listRecords`, `getRecord`) now route through the four generated typed
services** (`Rev_applicationsService`, `Rev_reviewsService`, `Rev_applicantsService`,
`SystemusersService`) via `getAll()`/`get()`, keeping `client.ts`'s own `ListRecordsRequest`/
`GetRecordRequest` types (and therefore `repository.ts` and `identity.ts`) completely unchanged
— only `client.ts`'s internals moved, exactly as this section originally predicted they would.
This is not merely a different CLI incantation that happened to work: read from the installed
`@microsoft/power-apps@1.3.0` package's own shipped source
(`dist/internal/data/core/data/executors/dataverseDataOperationExecutor.js`), a `"Dataverse"`
-type data source resolves its instance URL from the app's own **launch-time runtime metadata**
(`metadataClient.getAppDataSourceConfigsAsync()`), never from the shared "Microsoft Dataverse"
OAuth connection's org-url header that fails for the generic connector. The two data source
kinds are structurally different transports, not the same one with a different setting.

**The write (`saveVerdict` → `updateRecord`) stays on the generic connector's hand-rolled
`executeAsync` + `UpdateOnlyRecord` + `If-Match: *`**, unchanged, for the reason recorded against
`IMP-0210`/`A-TR-10`: the generated services' `update()` method has no headers parameter at any
layer and issues a plain `PATCH`, which Dataverse treats as an upsert — it cannot enforce "never
create a `rev_review` row" the way the current write does, and `client.test.ts`/`repository.test.ts`
assert on that exact shape. This app's `$select` allow-list discipline (every read names its
columns; there is no `select`-everything path) is preserved at the same two call sites in
`client.ts` — `listRecords`/`getRecord`'s own `select` parameters stay mandatory even though the
generated `IGetAllOptions.select`/`IGetOptions.select` are optional, which is what keeps the
allow-list compiler-enforced rather than a convention every call site has to remember.

**Not yet V4-verified.** Everything above is V2/V3 (compiles, packages, passes unit tests against
a mocked SDK) plus E1 platform-fact evidence (the installed package's own shipped source). No
session working on this repository has host/browser access to sign in as a real trustee — see
`docs/development/trustee-portal-org-url-fix-dev-summary.md` §11 for exactly what is and is not
proven, and the steps for whoever can perform that check next.

## 2. The generated service does not compile

`src/generated/services/MicrosoftDataverseService.ts` is committed exactly as
`pac code add-data-source` wrote it, and it **cannot be imported**. Two of its methods —
`ListRecordsWithOrganization` and `GetItemWithOrganization` — declare a parameter named
`MSCRM.IncludeMipSensitivityLabel`, and a `.` is not legal in a TypeScript identifier.

Reproduced 2026-08-21, pac 2.4.1, TypeScript 5.9.3:

```
$ npx tsc --noEmit --strict --skipLibCheck src/generated/services/MicrosoftDataverseService.ts
src/generated/services/MicrosoftDataverseService.ts(496,168): error TS1005: ',' expected.
... 963 errors

$ npx esbuild --format=esm src/generated/services/MicrosoftDataverseService.ts
✘ [ERROR] Expected ")" but found "."
```

A module-level parse failure cannot be worked around by importing only the good methods, and
the file must not be hand-edited (`knowledge/technology/code-apps.md` → TypeScript). So
`client.ts` calls `getClient(dataSourcesInfo)` from `@microsoft/power-apps/data` — the same SDK
entry point the generated service uses — passing the same `connectorOperation` payload shape,
and consuming the **generated** `dataSourcesInfo`. Nothing is reimplemented and nothing
generated is edited.

`C-TECH-048` is satisfied: data access is through the managed connector data source added by
`pac code add-data-source`, with no token acquisition, no MSAL and no credential handling.

The broken file stays committed as ground truth and is excluded from `tsconfig.json`,
`eslint.config.js` and the coverage scope, each with a comment pointing here.

## 3. What must never appear in this folder

`rev_application` carries an Article 9 special-category free-text column that the trustee
role must never read. It appears in **no** query, type, `$select`, fallback or comment
anywhere in this app, and `src/dataverse/schema.test.ts` asserts that — building the forbidden
column name from fragments at runtime so the test itself does not contain the literal
(`IMP-0024`).

The control is not this code. The control is that `REV Trustee` is deliberately **not** a
member of the `REV_TrusteeRestricted` column-security profile, so the column reads as null for
a trustee regardless of what any client asks for. Non-membership *is* the control
(`IMP-0153`). Nothing here compensates for it, and nothing here should ever be changed in a
way that assumes it.
