/**
 * A stand-in for the generated `Rev_roundfinancesService` — which now EXISTS, and still
 * is not wired in. Read this before changing anything here.
 *
 * ## A-LAND-1 — CLOSED (E1), 2026-08-26. History kept below; only this paragraph is new.
 *
 * `pa app add data-source --connector dataverse --table rev_roundfinance -u <org-url> -c
 * <connection-id>` was run 2026-08-26, in response to `IMP-0329`'s own gate
 * (`scripts/verify-code-app-data-sources.py`) reporting `rev_roundfinances` registered in
 * `READ_SERVICES` but absent from the generated config the SDK actually resolves against.
 * `power.config.json` and `.power/schemas/appschemas/dataSourcesInfo.ts` now carry a real
 * `rev_roundfinances` entry (`dataSourceType: "Dataverse"`, `primaryKey:
 * "rev_roundfinanceid"` — matching live metadata exactly), and
 * `src/generated/services/Rev_roundfinancesService.ts` exists and is committed. Compared
 * directly against this file: its `getAll`/`get` are the identical
 * `getClient(dataSourcesInfo).retrieve…Async("rev_roundfinances", …)` calls this stand-in
 * makes — the guess below is confirmed correct, not merely unfalsified. **This module is
 * left in place and `client.ts`'s `READ_SERVICES` entry unswapped**, deliberately: the
 * registration alone already makes both paths resolve identically for a real signed-in
 * user, and swapping to the generated class plus deleting this file is a one-line-plus-
 * deletion cleanup a registration-only dispatch did not bundle in. The "How to remove this
 * file" section below is now accurate as written, not aspirational.
 *
 * ## A-LAND-1 (GUESS, E2) — the original entry, kept for history
 *
 * `client.ts` resolves every read through `READ_SERVICES`, a map from entity-set name to
 * the GENERATED per-table typed service that reads it, and `readServiceFor()` throws a
 * named error rather than routing wrong for an entity set that is not in the map. TAD §5.4
 * therefore states plainly that `rev_roundfinance` "must be registered in the app's
 * `READ_SERVICES` map with its generated per-table service".
 *
 * **There was no generated service to register.** `pa app add data-source --connector
 * dataverse --table rev_roundfinance -u <org-url> -c <connection-id>` had not been run:
 * `power.config.json`'s `databaseReferences.default.cds.dataSources` held four entries
 * (`applications`, `reviews`, `applicants`, `users`) and this table was not among them, and
 * neither was it among the four `"dataSourceType": "Dataverse"` entries in the generated
 * `.power/schemas/appschemas/dataSourcesInfo.ts`. The table itself went live in DEV
 * 2026-08-25 (`IMP-0316`); the app's binding to it followed 2026-08-26, above.
 *
 * So this module was built to make the gap **one file wide and honest**, instead of leaving
 * the landing screen unable to compile or silently reading through a transport that is
 * known to be broken for this app.
 *
 * ## What this is, exactly
 *
 * The generated per-table services are thin. Read
 * `src/generated/services/Rev_applicationsService.ts`: `getAll(options)` is
 * `getClient(dataSourcesInfo).retrieveMultipleRecordsAsync<T>(dataSourceName, options)`
 * and nothing else, where `dataSourceName` is the entity-set name. This module makes that
 * same call against the same client with the same options type. It is not a
 * reimplementation of a transport — it is the same one call, with the generated wrapper
 * absent.
 *
 * Two things follow, and both matter more than the code:
 *
 *   1. **It routes through the `"Dataverse"`-type data source path, not the generic
 *      connector.** That is deliberate and it is the whole reason this shape was chosen
 *      over the obvious alternative. `client.ts`'s `updateRecord` still uses the GENERIC
 *      `commondataserviceforapps` connector, and reads were migrated OFF it in `IMP-0224`
 *      because it resolved its Dataverse organisation URL as `null` for a real signed-in
 *      trustee and no CLI flag fixes the non-table form of that data source. Reaching for
 *      `executeAsync({ connectorOperation: { operationName: "ListRecords", ... } })` here
 *      would have compiled, passed every unit test, and failed live in exactly the way
 *      this app has already lost a day to. See `src/dataverse/README.md` §1.
 *   2. **It will still fail at runtime until the CLI verb is run**, because
 *      `dataSourcesInfo` has no `rev_roundfinances` entry for the SDK to resolve. That
 *      failure surfaces as a thrown error, which `listRecords` wraps as a `DataverseError`,
 *      which the landing screen renders as "the round record could not be read" — a
 *      diagnostic state the screen already has to handle for a missing privilege anyway.
 *      It degrades honestly and it degrades that one region only. It does not fabricate a
 *      round, and it does not take the FR-058..FR-062 figures down with it.
 *
 * ## How to remove this file — the cheapest verification, per `C-TECH-052`
 *
 *     pa app add data-source --connector dataverse --table rev_roundfinance \
 *         -u <org-url> -c <connection-id>
 *
 * Then, in `client.ts`'s `READ_SERVICES`, replace `Rev_roundfinancesStandInService` with
 * the generated `Rev_roundfinancesService` and delete this file. That is a one-line change
 * plus a deletion, which is the property this module was shaped to have.
 *
 * Two things to check while doing it, neither of which this file can assert:
 *   - `pa app add data-source` rewrites `power.config.json`. That file's binding has
 *     broken this app before (risk A-R34), so pass `-u`/`--org-url` explicitly and read
 *     `logs/known-failure-modes.md` first rather than after.
 *   - Confirm the regenerated `dataSourcesInfo` entry's `primaryKey` reads
 *     `rev_roundfinanceid`, which is what live metadata reported on 2026-08-25.
 *
 * Nothing generated is hand-edited by any of this, and no token is acquired anywhere in
 * it, so `C-TECH-048` holds: data access stays on a first-party managed data source.
 */
import { getClient } from "@microsoft/power-apps/data";
import type { IOperationResult } from "@microsoft/power-apps/data";
import { dataSourcesInfo } from "../../.power/schemas/appschemas/dataSourcesInfo";
import type { IGetAllOptions, IGetOptions } from "../generated/models/CommonModels";
import { ENTITY_SETS } from "./schema";
import type { RawRow } from "./types";

/**
 * The data-source name the SDK resolves, which for a `"Dataverse"`-type source is the
 * entity-set name — the same value the generated services hold in their own private
 * `dataSourceName` (E1, grepped equal for all four tables, `client.ts`'s `READ_SERVICES`
 * comment). Taken from `ENTITY_SETS` rather than re-spelt, so there is exactly one place
 * in this app where this name is written.
 */
const DATA_SOURCE_NAME: string = ENTITY_SETS.roundFinance;

/**
 * Structurally identical to the `ReadService` interface `client.ts` resolves against, and
 * to the two methods of a generated per-table service that this app actually calls.
 */
export const Rev_roundfinancesStandInService = {
  getAll(options?: IGetAllOptions): Promise<IOperationResult<RawRow[]>> {
    return getClient(dataSourcesInfo).retrieveMultipleRecordsAsync<RawRow>(
      DATA_SOURCE_NAME,
      options,
    );
  },

  get(id: string, options?: IGetOptions): Promise<IOperationResult<RawRow>> {
    return getClient(dataSourcesInfo).retrieveRecordAsync<RawRow>(DATA_SOURCE_NAME, id, options);
  },
};
