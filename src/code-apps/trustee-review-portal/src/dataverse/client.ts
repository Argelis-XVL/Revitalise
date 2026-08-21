/**
 * The ONE place this app calls the Power Apps data SDK.
 *
 * Why this file exists at all, rather than importing the generated service:
 * `src/generated/services/MicrosoftDataverseService.ts` does not parse — two of its
 * methods declare a parameter named `MSCRM.IncludeMipSensitivityLabel`, and a `.` is
 * not legal in a TypeScript identifier. 963 tsc errors, and esbuild stops at the first.
 * Full reproduction in src/dataverse/README.md §2.
 *
 * So this file does what that file would have done: it calls `getClient` from
 * `@microsoft/power-apps/data` with the GENERATED `dataSourcesInfo`, and sends the same
 * `connectorOperation` payload shape. Nothing generated is edited and nothing generated
 * is reimplemented. `C-TECH-048` holds — the managed connector data source added by
 * `pac code add-data-source` is the only data path, with no token handling anywhere.
 */
import { getClient } from "@microsoft/power-apps/data";
import { dataSourcesInfo } from "../../.power/schemas/appschemas/dataSourcesInfo";
import type { RawRow } from "./types";

/**
 * The data source key in the generated `dataSourcesInfo`, which is also what the SDK
 * calls `tableName` on a connector operation. It is the DATA SOURCE, not a Dataverse
 * table: the Dataverse table travels in `parameters.entityName`.
 *
 * E1 — read out of the generated
 * `.power/schemas/appschemas/dataSourcesInfo.ts`, whose single top-level key this is.
 */
const DATA_SOURCE = "commondataserviceforapps";

/** Standard OData headers the connector operations take as explicit parameters. */
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
 * one. Cheapest verification: run the app in the Power Apps host once and log the
 * unwrapped result of a single ListRecords call.
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
 * A-TR-9 (GUESS, E2) — the generated model types a list item as
 * `EntityItem { dynamicProperties?: Record<string, unknown> }` while the Dataverse
 * connector's own responses are flat row objects. Rather than pick one, this accepts
 * both: a `dynamicProperties` object is unwrapped, anything else is taken as the row.
 * Cheapest verification: log `Object.keys()` of one returned item against DEV.
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

function client() {
  // Generator output, passed to the SDK unchanged. It satisfies the SDK's
  // `DataSourcesInfo` type structurally, so no cast is needed — worth stating, because a
  // cast here would hide a real generator/SDK mismatch after a version bump.
  return getClient(dataSourcesInfo);
}

export interface ListRecordsRequest {
  /** The Dataverse ENTITY SET name (plural), e.g. `rev_applications`. See schema.ts. */
  entityName: string;
  /** OData `$select`. Always an explicit allow-list — never omitted. */
  select: readonly string[];
  /** OData `$filter`. */
  filter?: string;
  /** OData `$orderby`. */
  orderBy?: string;
}

/**
 * Lists rows through the connector's `ListRecords` operation.
 *
 * `select` is mandatory by type. An unbounded `$select` on this table would pull
 * columns the trustee has no business receiving even when column security would null
 * them, and it would make a future column an accidental disclosure.
 */
export async function listRecords(request: ListRecordsRequest): Promise<ListResult> {
  const parameters: Record<string, unknown> = {
    entityName: request.entityName,
    accept: ACCEPT_JSON,
    $select: request.select.join(","),
    $top: MAX_ROWS + 1,
  };
  if (request.filter !== undefined) parameters.$filter = request.filter;
  if (request.orderBy !== undefined) parameters.$orderby = request.orderBy;

  let raw: unknown;
  try {
    raw = await client().executeAsync<Record<string, unknown>, unknown>({
      connectorOperation: {
        tableName: DATA_SOURCE,
        operationName: "ListRecords",
        parameters,
      },
    });
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

/** Reads one row by id through the connector's `GetItem` operation. */
export async function getRecord(request: GetRecordRequest): Promise<RawRow | null> {
  let raw: unknown;
  try {
    raw = await client().executeAsync<Record<string, unknown>, unknown>({
      connectorOperation: {
        tableName: DATA_SOURCE,
        operationName: "GetItem",
        parameters: {
          prefer: PREFER_REPRESENTATION,
          accept: ACCEPT_JSON,
          entityName: request.entityName,
          recordId: request.recordId,
          $select: request.select.join(","),
        },
      },
    });
  } catch (caught) {
    const { message, status } = errorMessageOf(caught, "Could not load the record.");
    if (status === 404) return null;
    throw new DataverseError(message, status);
  }
  const payload = unwrap<unknown>(raw, `GetItem(${request.entityName})`);
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
 * `UpdateOnlyRecord` with `If-Match: *` is used deliberately in preference to
 * `UpdateRecord`, which the connector documents as an UPSERT. This app must never
 * create a `rev_review` row: the `REV Trustee` role holds no `prvCreaterev_review`, and
 * "never create" is enforced by the REQUEST rather than left to depend on a privilege
 * being absent. If the row is gone, this fails instead of quietly inserting one.
 *
 * A-TR-10 (GUESS, E3) — `If-Match: *` as the update-only guard is documented
 * Dataverse Web API behaviour and is not observed through the CONNECTOR from a Code
 * App. Cheapest verification: save a verdict against DEV once `rev_review` exists,
 * then attempt the same save against a deleted id and confirm it errors rather than
 * creating a row.
 */
export async function updateRecord(request: UpdateRecordRequest): Promise<void> {
  let raw: unknown;
  try {
    raw = await client().executeAsync<Record<string, unknown>, unknown>({
      connectorOperation: {
        tableName: DATA_SOURCE,
        operationName: "UpdateOnlyRecord",
        parameters: {
          prefer: PREFER_REPRESENTATION,
          accept: ACCEPT_JSON,
          If_Match: "*",
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
  unwrap<unknown>(raw, `UpdateOnlyRecord(${request.entityName})`);
}
