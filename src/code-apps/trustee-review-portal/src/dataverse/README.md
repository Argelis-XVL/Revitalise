# `src/dataverse/` — the one place this app talks to Dataverse

Everything in the app above this folder talks to the **repository interface** in
`repository.ts`. Nothing else in `src/` imports `client.ts`, `schema.ts` or the Power
Apps SDK. That is the design rule, and it exists for two reasons.

## 1. The generic connector typing is what this app uses — by choice, not by necessity

**Updated 2026-08-22 — the "unreachable" claim below is CORRECTED.** `pac code add-data-source
-a shared_commondataserviceforapps -c <connection>` (old `pac` CLI, no org URL flag) generates
only the generic Dataverse connector surface, and `pac code list-tables` / `list-datasets`
failed against this connection on three dataset forms — both confirmed 2026-08-21. That was
read as "the typed-per-table route is unreachable here" and left as an open assumption
(`A-TR-6` at the time).

It was the wrong conclusion, not just an unresolved one (`IMP-0208`, `IMP-0209`). The newer `pa`
CLI's `app add data-source --connector dataverse --table <logical-name> -u <org-url> -c
<connection-id>` **does** resolve a per-table dataset against this exact connection, once the
organisation URL is passed explicitly — the old CLI's failure was never about the table route
being closed, it was the same "Invalid organization URL 'null'" defect this whole file's §2
describes, one layer up the toolchain. Run 2026-08-22 for `rev_application`, `rev_review`,
`rev_applicant` and `systemuser`: all four succeeded, produced real per-table models and
services (`src/generated/models/Rev_reviewsModel.ts` etc.), and none of the four carries the
`MSCRM.IncludeMipSensitivityLabel` parse defect in §2 below — confirmed by grep, not assumed.
`power.config.json`'s `databaseReferences.default.cds.dataSources` now names all four real
tables, replacing the `account` table used as a connection smoke test the day before
(`IMP-0208`).

**This app still does not consume those typed services.** `client.ts` and `repository.ts`
below are unchanged, and continue to call the generic `ListRecords` / `GetItem` /
`UpdateOnlyRecord` connector operations by hand. That is now a **choice being carried forward**
rather than a forced one, for three reasons, recorded so the next dispatch does not have to
re-derive them: (1) the hand-rolled layer already enforces this app's central security rule —
every read names an explicit `$select` allow-list, never `$select`-everything — and the
generated services' `IGetAllOptions.select` would need the exact same discipline re-applied at
every call site, with no test yet proving it is; (2) the generated `update()` method's write
semantics (plain upsert vs. this app's deliberate `UpdateOnlyRecord` + `If-Match: *` — see §3 of
`client.ts`'s header and `A-TR-10`, CLOSED against the hand-rolled path with a live positive and
negative control) have not been observed for the generated client, and swapping to it would
reopen a closed assumption; (3) it is a repository-wide refactor of already-reviewed, tested
code, which is a decision for the reviewer, not a side effect of fixing a broken connection. If
a future task swaps to the typed services, start from `IGetAllOptions` in
`src/generated/models/CommonModels.ts` — it already supports `select`/`filter`/`orderBy`, so the
allow-list discipline is expressible, just not yet applied.

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
