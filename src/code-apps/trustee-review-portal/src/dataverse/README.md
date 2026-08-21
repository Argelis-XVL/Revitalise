# `src/dataverse/` — the one place this app talks to Dataverse

Everything in the app above this folder talks to the **repository interface** in
`repository.ts`. Nothing else in `src/` imports `client.ts`, `schema.ts` or the Power
Apps SDK. That is the design rule, and it exists for two reasons.

## 1. Only the generic connector typing exists

`pac code add-data-source -a shared_commondataserviceforapps -c <connection>` generates the
**generic Dataverse connector surface**, not per-table typed models. Verified on
2026-08-21 with pac 2.4.1: `grep -c rev_` across every file the command produced returns
**0**. There is no `rev_applicationService`.

The typed-per-table route needs `pac code list-tables` / `pac code list-datasets` to resolve a
dataset for the connection. Both fail against this connection with an empty error body (`{}`),
on three different dataset forms — organisation URL, organisation unique name, environment id.
Per `agents/development-agent.md` → *Hand-Authoring Platform Artefacts* rule 2, three failed
guesses is well past the point of stopping, so the typed route is recorded as an **open
assumption** rather than guessed at further.

So this folder owns our row interfaces and our OData shapes by hand. When per-table typed
models become reachable, the swap is `client.ts` + `schema.ts` — one boundary, not the app.

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
