/**
 * The two places this app calls the Power Apps data SDK: one for reads, one for the write.
 *
 * **Reads** (`listRecords`, `getRecord`) go through the four generated PER-TABLE typed
 * services under `src/generated/services/` (`Rev_applicationsService`, `Rev_reviewsService`,
 * `Rev_applicantsService`, `SystemusersService`) via their `getAll()` / `get()` methods.
 *
 * **The write** (`updateRecord`) stays on the hand-rolled GENERIC connector call it always
 * used: `getClient(dataSourcesInfo).executeAsync({ connectorOperation: {...} })` against the
 * `commondataserviceforapps` data source, sending `UpdateOnlyRecordWithOrganization` with
 * `If-Match: *`. See "Why the write stays here" below `updateRecord`.
 *
 * Why reads and the write are on two different transports (IMP-0208, IMP-0209, IMP-0210,
 * IMP-0224 — full history in `src/dataverse/README.md` §1):
 *
 *   - The GENERIC connector data source (`commondataserviceforapps`, `dataSourceType:
 *     "Connector"` in the generated `dataSourcesInfo.ts`) resolves its Dataverse
 *     organisation URL through the app's per-user "Microsoft Dataverse" OAuth connection
 *     when the PLAIN (non-`WithOrganization`) operation is called. That resolution came back
 *     `null` for a real signed-in trustee — "Invalid organization URL 'null' provided".
 *   - **This is not a platform defect (IMP-0191 is CORRECTED by IMP-0359+1).** Microsoft's
 *     own reference implementation
 *     (`github.com/microsoft/PowerAppsCodeApps`, `samples/DataverseConnector/src/dataverse/
 *     client.ts`) never calls a plain connector operation: it resolves the org URL once from
 *     `getContext().app.dataverseOrgUrl` (present on the installed SDK's own
 *     `IAppContext` — `@microsoft/power-apps/dist/app/App.Types.d.ts`) and passes it
 *     explicitly to the `…WithOrganization` variant of every call. `getOrgUrl()` below
 *     mirrors that exactly, and `UpdateOnlyRecordWithOrganization` was already declared in
 *     this app's own generated `dataSourcesInfo.ts` — unused until now.
 *   - The four PER-TABLE data sources (`rev_applications`, `rev_reviews`, `rev_applicants`,
 *     `systemusers`; `dataSourceType: "Dataverse"`) do **not** go through that connector or
 *     its OAuth binding at all. Read from the installed `@microsoft/power-apps@1.3.0`
 *     package's own shipped source (`dist/internal/data/core/data/executors/
 *     dataverseDataOperationExecutor.js`, `_getDataverseDataSourceInfo` /
 *     `getDatabaseReferences`): the instance URL for a `"Dataverse"`-type source is read
 *     from the app's own launch-time runtime metadata
 *     (`metadataClient.getAppDataSourceConfigsAsync()`), never from a connector's org-url
 *     header. It is therefore structurally immune to the defect above and needs no
 *     `getOrgUrl()` fix — which is the architectural reason this app routes reads through
 *     these services rather than the generic connector at all.
 *
 * The four per-table services were reachable once `-u/--org-url` was supplied to
 * `pa app add data-source --table <t>` (IMP-0208, IMP-0209) and already compile cleanly —
 * unlike `src/generated/services/MicrosoftDataverseService.ts` (the GENERIC connector's own
 * generated service), which still does not parse (a genuine `pac code add-data-source`
 * generator bug: it emits a parameter/property literally named
 * `MSCRM.IncludeMipSensitivityLabel`, copied verbatim from the connector's OpenAPI header
 * name — valid there, not as a JS identifier). Nothing generated is hand-edited either way;
 * this app calls the connector through the raw `getClient(dataSourcesInfo).executeAsync()`
 * escape hatch instead of that class's typed static methods.
 */
import { getContext } from "@microsoft/power-apps/app";
import { getClient } from "@microsoft/power-apps/data";
import type { IOperationResult } from "@microsoft/power-apps/data";
import { dataSourcesInfo } from "../../.power/schemas/appschemas/dataSourcesInfo";
import type { IGetAllOptions, IGetOptions } from "../generated/models/CommonModels";
import { Rev_applicantsService } from "../generated/services/Rev_applicantsService";
import { Rev_applicationsService } from "../generated/services/Rev_applicationsService";
import { Rev_reviewsService } from "../generated/services/Rev_reviewsService";
import { Rev_roundstatisticsrequestsService } from "../generated/services/Rev_roundstatisticsrequestsService";
import { Rev_roundstatisticsresultsService } from "../generated/services/Rev_roundstatisticsresultsService";
import { SystemusersService } from "../generated/services/SystemusersService";
import { Rev_roundfinancesStandInService } from "./roundFinanceReadService";
import type { RawRow } from "./types";

/**
 * The GENERIC connector data source key, used only by `updateRecord` below. It is a data
 * SOURCE name, not a Dataverse table: the table travels in `parameters.entityName`.
 */
const DATA_SOURCE = "commondataserviceforapps";

/** Standard OData headers the generic connector's operations take as explicit parameters. */
const ACCEPT_JSON = "application/json";
const PREFER_REPRESENTATION = "return=representation";

/**
 * Upper bound on rows fetched for one round.
 *
 * A trustee round is tens of applications. The cap exists so a misconfigured round
 * cannot hang the screen — and the app asks for `MAX_ROWS + 1` so it can TELL the
 * trustee the list was truncated rather than quietly showing a subset. A silently
 * short list on a decision screen is the worst available failure.
 */
export const MAX_ROWS = 500;

export interface ListResult {
  rows: RawRow[];
  /** True when more rows exist than were returned. Surfaced in the UI, never swallowed. */
  truncated: boolean;
}

/** An error from the connector, shaped for display. */
export class DataverseError extends Error {
  readonly status: number | undefined;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "DataverseError";
    this.status = status;
  }
}

interface OperationResultLike {
  success: boolean;
  data?: unknown;
  error?: unknown;
}

function isOperationResultLike(value: unknown): value is OperationResultLike {
  return (
    typeof value === "object" &&
    value !== null &&
    "success" in value &&
    typeof value.success === "boolean"
  );
}

function errorMessageOf(error: unknown, fallback: string): { message: string; status?: number } {
  if (error instanceof Error) return { message: error.message };
  if (typeof error === "object" && error !== null) {
    const bag = error as { message?: unknown; status?: unknown };
    const message = typeof bag.message === "string" ? bag.message : fallback;
    const status = typeof bag.status === "number" ? bag.status : undefined;
    return status === undefined ? { message } : { message, status };
  }
  if (typeof error === "string" && error.length > 0) return { message: error };
  return { message: fallback };
}

/**
 * Unwraps `IOperationResult<T>` and turns a failure into a thrown `DataverseError`.
 *
 * A-TR-8 (GUESS, E2) — `@microsoft/power-apps` 1.3.0 declares
 * `executeAsync` as returning `IOperationResult<T>` with `success: boolean` and
 * `data: T`, and ships an `isOperationResult` type guard, which implies the runtime can
 * hand back a bare payload instead. Both shapes are accepted here rather than assuming
 * one. Still open for the GENERIC connector's `executeAsync` (used only by `updateRecord`
 * below); CLOSED for the typed per-table `getAll`/`get` calls below — their executor
 * (`dataverseDataOperationExecutor.js`) always returns the `{success, data, error}` shape,
 * confirmed by reading the installed package's own shipped source, 2026-08-23.
 */
function unwrap<T>(result: unknown, operation: string): T {
  if (isOperationResultLike(result)) {
    if (!result.success) {
      const { message, status } = errorMessageOf(
        result.error,
        `${operation} failed and the connector gave no reason.`,
      );
      throw new DataverseError(message, status);
    }
    return result.data as T;
  }
  return result as T;
}

/**
 * Normalises one returned row.
 *
 * A-TR-9 CLOSED for the typed per-table read path, E1 — the installed
 * `@microsoft/power-apps@1.3.0` package's own `retrieveMultipleRecordsAsync`
 * (`dataverseDataOperationExecutor.js`) returns `dataverseResponse?.data?.value || []`: a
 * flat array of plain OData row objects, never a `dynamicProperties` wrapper. Confirmed
 * against the generated model shapes too (`Rev_reviewsModel.ts` etc. type every column,
 * including `_<lookup>_value` forms, as direct properties). The `dynamicProperties`
 * branch below is retained defensively — it is what the row shape WOULD need if a future
 * SDK version wrapped it, and it is free to keep — but it is no longer a live guess for
 * this app's actual traffic.
 */
export function normaliseRow(item: unknown): RawRow {
  if (typeof item !== "object" || item === null) return {};
  const bag = item as { dynamicProperties?: unknown };
  if (typeof bag.dynamicProperties === "object" && bag.dynamicProperties !== null) {
    return bag.dynamicProperties as RawRow;
  }
  return item as RawRow;
}

function normaliseRows(payload: unknown): RawRow[] {
  if (Array.isArray(payload)) return payload.map(normaliseRow);
  if (typeof payload === "object" && payload !== null) {
    const bag = payload as { value?: unknown };
    if (Array.isArray(bag.value)) return bag.value.map(normaliseRow);
  }
  return [];
}

/** The generic connector client, used only by `updateRecord`. See file header. */
function writeConnectorClient() {
  // Generator output, passed to the SDK unchanged. It satisfies the SDK's
  // `DataSourcesInfo` type structurally, so no cast is needed — worth stating, because a
  // cast here would hide a real generator/SDK mismatch after a version bump.
  return getClient(dataSourcesInfo);
}

let cachedOrgUrl: string | undefined;

/**
 * Resolves the Dataverse org URL from the Power SDK context, the same source and the same
 * cache-once pattern Microsoft's own `samples/DataverseConnector` uses. Needed only by the
 * write below — the per-table read services resolve their own org URL from runtime metadata
 * and never call this.
 */
async function getOrgUrl(): Promise<string> {
  if (cachedOrgUrl !== undefined) return cachedOrgUrl;
  const context = await getContext();
  const orgUrl = context.app.dataverseOrgUrl;
  if (orgUrl === undefined || orgUrl === "") {
    throw new DataverseError(
      "The Power Apps host did not provide a Dataverse organisation URL, so this change " +
        "could not be saved.",
    );
  }
  cachedOrgUrl = orgUrl;
  return orgUrl;
}

/** The subset of a generated per-table service's static surface reads need. */
interface ReadService {
  getAll(options?: IGetAllOptions): Promise<IOperationResult<unknown[]>>;
  get(id: string, options?: IGetOptions): Promise<IOperationResult<unknown>>;
}

/**
 * Entity-set name -> the typed service that reads it.
 *
 * E1 for the first four — each key is the generated service's own private
 * `dataSourceName` (e.g. `Rev_applicationsService.ts`'s `'rev_applications'`), which is
 * also the entity-set name `schema.ts`'s `ENTITY_SETS` already uses as every caller's
 * `entityName`. Grepped equal for all four tables, 2026-08-23.
 *
 * **The fifth entry is still the hand-written stand-in, not the generated service — and
 * that is now a choice, not a gap.** `pa app add data-source --connector dataverse --table
 * rev_roundfinance -u <org-url> -c <connection-id>` was run 2026-08-26 (`IMP-0329`'s own
 * gate, `scripts/verify-code-app-data-sources.py`, found the entity set undeclared and named
 * this exact command). `.power/schemas/appschemas/dataSourcesInfo.ts` now carries a real
 * `"rev_roundfinances"` entry, `dataSourceType: "Dataverse"`, `primaryKey:
 * "rev_roundfinanceid"` — matching live metadata exactly — and `Rev_roundfinancesService.ts`
 * is generated and committed. **A-LAND-1 is CLOSED (E1)**: its `getAll`/`get` are the
 * identical `getClient(dataSourcesInfo).retrieve…Async("rev_roundfinances", …)` calls
 * `roundFinanceReadService.ts` already made — read both files side by side to confirm. The
 * stand-in therefore now resolves for a real signed-in user exactly as the generated service
 * would; swapping this entry for `Rev_roundfinancesService` and deleting
 * `roundFinanceReadService.ts` remains a one-line-plus-a-deletion cleanup (its own header
 * still describes the swap), not a defect fix — left for the reviewer rather than bundled
 * into a registration-only dispatch.
 */
const READ_SERVICES: Readonly<Record<string, ReadService>> = {
  rev_applications: Rev_applicationsService,
  rev_reviews: Rev_reviewsService,
  rev_applicants: Rev_applicantsService,
  systemusers: SystemusersService,
  rev_roundfinances: Rev_roundfinancesStandInService,
  // Added 2026-08-27 (IMP-0359, IMP-0365) — the generated service exists (`pa app add
  // data-source --connector dataverse --table rev_roundstatisticsrequest`), unlike
  // rev_roundfinances above, which still leans on a hand-written stand-in.
  rev_roundstatisticsrequests: Rev_roundstatisticsrequestsService,
  // Added 2026-08-28 (ADR-038, TAD §5.4's Revision 5 note: "two table data sources, not
  // one"), CLOSED 2026-08-29 (`IMP-0485`, TAD §12.3 step 9): `rev_roundstatisticsresult` now
  // exists live in DEV (confirmed by `pipeline.log`'s 2026-08-29 read-only query —
  // `EntitySetName=rev_roundstatisticsresults`, `PrimaryIdAttribute=
  // rev_roundstatisticsresultid`), so `pa app add data-source --connector dataverse --table
  // rev_roundstatisticsresult -u https://orge2b20d13.crm17.dynamics.com -c
  // 8b4307acb81d4463be4fd96792363f2f --non-interactive` was run from this app's root. It
  // echoed both platform-assigned names exactly as the app's own `schema.ts` guessed —
  // A-RESULT-1, A-FLOW-07 and A-RES-1 all close at E1 on this one run — and generated
  // `src/generated/{models,services}/Rev_roundstatisticsresults*`, which this entry now
  // points at. The interim stand-in (`roundStatisticsResultReadService.ts`) is deleted in the
  // same change, matching how `rev_roundstatisticsrequests` above was handled: this table
  // never had a period where a generated service existed alongside an undeleted stand-in.
  //
  // NOTE ON THE CONNECTION ID: `8b4307acb81d4463be4fd96792363f2f` is NOT the
  // `f31ddadfbe874e50a34054df668e75cf` connection every earlier `pa app add data-source` call
  // in this app's history used (rev_roundfinance, the original four tables). That connection
  // no longer exists in this environment as of 2026-08-29 — `pa connection list` shows only
  // two live Dataverse connections, both created 2026-08-26, neither matching the documented
  // id. This does not change how any table resolves at runtime: a `"Dataverse"`-type source
  // is bound per-signed-in-user at app-run time from launch metadata, never from the
  // connection id used to generate it (`knowledge/technology/code-apps.md` → "Invalid
  // organization URL" section, step 3). Logged as `IMP-0489` because a document in this repo
  // was contradicted by live state, not because anything here is at risk.
  rev_roundstatisticsresults: Rev_roundstatisticsresultsService,
};

/** Looks up the typed read service for an entity set, or fails loudly rather than routing wrong. */
function readServiceFor(entityName: string): ReadService {
  const service = READ_SERVICES[entityName];
  if (service === undefined) {
    throw new DataverseError(
      `No generated read service is registered for entity set "${entityName}". Add it to ` +
        "READ_SERVICES in client.ts, alongside its generated service under src/generated/services/.",
    );
  }
  return service;
}

export interface ListRecordsRequest {
  /** The Dataverse ENTITY SET name (plural), e.g. `rev_applications`. See schema.ts. */
  entityName: string;
  /** OData `$select`. Always an explicit allow-list — never omitted. */
  select: readonly string[];
  /** OData `$filter`. */
  filter?: string;
  /** OData `$orderby`, comma-separated (e.g. `"rev_circumstancescore desc,rev_name asc"`). */
  orderBy?: string;
  /**
   * OData `$top`. Omit for this app's default of `MAX_ROWS + 1`, which is what makes
   * truncation detectable on the list read.
   *
   * Supply it only when the caller wants a bounded PROBE rather than a page, and reads the
   * returned row count as its answer. `getOpenRound` is the one such caller: TAD §5.4
   * step 1 asks `rev_roundfinance` with `top 2`, because one row is the expected case and
   * "two rows means the screen says the round is ambiguous" — a third open round would not
   * change that verdict, so there is nothing to gain by fetching it.
   *
   * `truncated` below stays relative to `MAX_ROWS` and is therefore always `false` for a
   * small explicit `top`. That is correct for a probe and wrong for a page: a caller that
   * passes an explicit `top` is asserting that it interprets the count itself, and must
   * not rely on `truncated` to tell it there were more rows.
   */
  top?: number;
}

/**
 * Lists rows through the resolved typed service's `getAll()`.
 *
 * A-TRM-2 (OPEN, E1) — `select` is mandatory by type — deliberately narrower than the
 * generated `IGetAllOptions.select` (`src/generated/models/CommonModels.ts`), which is
 * optional. An unbounded read on this table would pull columns the trustee has no
 * business receiving even when column security would null them, and it would make a
 * future column an accidental disclosure. This wrapper is the only thing that keeps that
 * allow-list discipline compiler-enforced now that the generated services themselves do
 * not require it. If a future migration ever calls the generated `getAll()`/`get()`
 * directly instead of through this wrapper, that compiler-level enforcement is lost — see
 * docs/development/trustee-portal-dataverse-service-migration-dev-summary.md §10.
 */
export async function listRecords(request: ListRecordsRequest): Promise<ListResult> {
  const options: IGetAllOptions = {
    select: [...request.select],
    // Clamped, so an explicit `top` can only ever narrow the read, never widen it past
    // the cap this app is willing to hold in a browser.
    top: Math.min(request.top ?? MAX_ROWS + 1, MAX_ROWS + 1),
  };
  if (request.filter !== undefined) options.filter = request.filter;
  if (request.orderBy !== undefined) {
    // The generated service's $orderby takes one fragment per array element, joined with
    // commas by the SDK itself (stringQueryOptions.js) — this app's own callers still pass
    // one comma-joined string (schema.ts / repository.ts are unchanged), so split it here.
    options.orderBy = request.orderBy
      .split(",")
      .map((fragment) => fragment.trim())
      .filter((fragment) => fragment.length > 0);
  }

  let raw: unknown;
  try {
    raw = await readServiceFor(request.entityName).getAll(options);
  } catch (caught) {
    const { message, status } = errorMessageOf(caught, "Could not load records.");
    throw new DataverseError(message, status);
  }

  const rows = normaliseRows(unwrap<unknown>(raw, `ListRecords(${request.entityName})`));
  if (rows.length > MAX_ROWS) {
    return { rows: rows.slice(0, MAX_ROWS), truncated: true };
  }
  return { rows, truncated: false };
}

export interface GetRecordRequest {
  entityName: string;
  recordId: string;
  select: readonly string[];
}

/**
 * Reads one row by id through the resolved typed service's `get()`.
 *
 * A-TRM-3 (GUESS, E2) — a 404 is treated as "no such row" (returns `null`) regardless of
 * whether the SDK surfaces it as a THROWN error (checked first) or as a resolved
 * `{ success: false, error: { status: 404 } }` (checked second, via `unwrap`'s thrown
 * `DataverseError`). Both branches exist because which shape the typed per-table
 * `retrieveRecordAsync` actually uses for a missing row has not been observed live — the
 * generic connector's `GetItem` (this function's previous implementation) was observed to
 * throw, but the typed path's executor
 * (`dataverseDataOperationExecutor.js`'s `_executeNativeDataverseOperation`) catches
 * internally and resolves rather than rejects for most failures. Handling both costs
 * nothing and cannot silently swallow a real error, since anything that is not a 404
 * still becomes a thrown `DataverseError` either way. Cheapest verification: request a
 * known-deleted id against DEV once signed in as a trustee and confirm the screen renders
 * "not found" rather than an error toast.
 */
export async function getRecord(request: GetRecordRequest): Promise<RawRow | null> {
  let raw: unknown;
  try {
    raw = await readServiceFor(request.entityName).get(request.recordId, {
      select: [...request.select],
    });
  } catch (caught) {
    const { message, status } = errorMessageOf(caught, "Could not load the record.");
    if (status === 404) return null;
    throw new DataverseError(message, status);
  }

  let payload: unknown;
  try {
    payload = unwrap<unknown>(raw, `GetItem(${request.entityName})`);
  } catch (caught) {
    if (caught instanceof DataverseError && caught.status === 404) return null;
    throw caught;
  }
  if (typeof payload !== "object" || payload === null) return null;
  return normaliseRow(payload);
}

export interface UpdateRecordRequest {
  entityName: string;
  recordId: string;
  /** Column-to-value map. Only ever the columns this app is entitled to write. */
  item: Record<string, unknown>;
}

/**
 * Updates one existing row.
 *
 * Why the write stays on the GENERIC connector rather than the generated
 * `Rev_reviewsService.update()`: `UpdateOnlyRecord` with `If-Match: *` is used
 * deliberately in preference to a plain upsert. This app must never create a
 * `rev_review` row: the `REV Trustee` role holds no `prvCreaterev_review`, and "never
 * create" is enforced by the REQUEST rather than left to depend on a privilege being
 * absent. If the row is gone, this fails instead of quietly inserting one.
 *
 * IMP-0210 (E1, CLOSED) — read from the installed `@microsoft/power-apps@1.3.0`
 * package's own shipped source: the generated service's `update(id, changedFields)` has a
 * fixed three-argument signature with no headers parameter at any layer and issues a
 * plain `PATCH`, which Dataverse treats as an UPSERT. It cannot enforce this guard, so it
 * must not replace this call — see `knowledge/technology/code-apps.md` → "The generated
 * services cannot send custom headers on a write" and `client.test.ts`'s
 * *"so it can never create a row"* test, which asserts this exact shape.
 *
 * A-TR-10 (GUESS, E3) — `If-Match: *` as the update-only guard is documented
 * Dataverse Web API behaviour and is not observed through the CONNECTOR from a Code
 * App. Cheapest verification: save a verdict against DEV once `rev_review` exists,
 * then attempt the same save against a deleted id and confirm it errors rather than
 * creating a row.
 *
 * Uses `UpdateOnlyRecordWithOrganization`, not the plain `UpdateOnlyRecord` this call used
 * before: the plain operation resolves its organisation through the connector's per-user
 * OAuth connection, which returned `null` for a real signed-in trustee
 * ("Invalid organization URL 'null' provided"). The `WithOrganization` variant takes the
 * org URL as an explicit parameter instead, resolved once by `getOrgUrl()` from
 * `getContext().app.dataverseOrgUrl` — the same mechanism Microsoft's own
 * `samples/DataverseConnector` reference app uses for every connector call. See the file
 * header for the full comparison.
 */
export async function updateRecord(request: UpdateRecordRequest): Promise<void> {
  const organization = await getOrgUrl();
  let raw: unknown;
  try {
    raw = await writeConnectorClient().executeAsync<Record<string, unknown>, unknown>({
      connectorOperation: {
        tableName: DATA_SOURCE,
        operationName: "UpdateOnlyRecordWithOrganization",
        parameters: {
          prefer: PREFER_REPRESENTATION,
          accept: ACCEPT_JSON,
          If_Match: "*",
          organization,
          entityName: request.entityName,
          recordId: request.recordId,
          item: request.item,
        },
      },
    });
  } catch (caught) {
    const { message, status } = errorMessageOf(caught, "Could not save the change.");
    throw new DataverseError(message, status);
  }
  unwrap<unknown>(raw, `UpdateOnlyRecordWithOrganization(${request.entityName})`);
}
