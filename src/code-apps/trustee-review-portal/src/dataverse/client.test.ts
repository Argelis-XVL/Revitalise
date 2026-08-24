/**
 * The connector boundary, with the Power Apps SDK mocked.
 *
 * What this proves: that `listRecords`/`getRecord` route through the resolved per-table
 * typed service (`retrieveMultipleRecordsAsync`/`retrieveRecordAsync`) with the request
 * shape this app intends, that `updateRecord` still goes through the GENERIC connector's
 * `executeAsync` unchanged, and that every failure shape becomes a `DataverseError` with a
 * message a trustee can read rather than an unhandled rejection.
 *
 * What it does NOT prove: that the connector or the typed services accept any of it, or
 * return the row shapes handled below. Those are open assumptions (A-TR-8, A-TRM-3) and are
 * deliberately not asserted here — asserting a guess is how a guess becomes permanent
 * (`IMP-0111`).
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const executeAsync = vi.fn();
const retrieveMultipleRecordsAsync = vi.fn();
const retrieveRecordAsync = vi.fn();

vi.mock("@microsoft/power-apps/data", () => ({
  getClient: () => ({ executeAsync, retrieveMultipleRecordsAsync, retrieveRecordAsync }),
  // Only Rev_applicationsService and Rev_applicantsService import these (their tables carry
  // multi-select option sets). None of this app's own `select` allow-lists name one, so a
  // pass-through is enough to let those generated services load in this test.
  serializeMultiSelectPicklistFields: (record: unknown) => record,
  deserializeMultiSelectPicklistFields: (record: unknown) => record,
}));

const { DataverseError, getRecord, listRecords, MAX_ROWS, normaliseRow, updateRecord } =
  await import("./client");

interface Operation {
  connectorOperation: {
    tableName: string;
    operationName: string;
    parameters: Record<string, unknown>;
  };
}

function lastOperation(): Operation["connectorOperation"] {
  const call = executeAsync.mock.calls.at(-1);
  if (call === undefined) throw new Error("executeAsync was never called");
  return (call[0] as Operation).connectorOperation;
}

beforeEach(() => {
  executeAsync.mockReset();
  retrieveMultipleRecordsAsync.mockReset();
  retrieveRecordAsync.mockReset();
});

describe("listRecords", () => {
  it("resolves the per-table typed service by entity set, not the generic connector", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await listRecords({
      entityName: "rev_applications",
      select: ["rev_name", "rev_status"],
      filter: "rev_eligibleforround eq true",
      orderBy: "rev_name asc",
    });
    expect(executeAsync).not.toHaveBeenCalled();
    expect(retrieveMultipleRecordsAsync).toHaveBeenCalledWith("rev_applications", {
      select: ["rev_name", "rev_status"],
      filter: "rev_eligibleforround eq true",
      orderBy: ["rev_name asc"],
      top: MAX_ROWS + 1,
    });
  });

  it("splits a comma-joined orderBy into one fragment per array element", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await listRecords({
      entityName: "rev_applications",
      select: ["rev_name"],
      orderBy: "rev_circumstancescore desc,rev_name asc",
    });
    const [, options] = retrieveMultipleRecordsAsync.mock.calls.at(-1) as [string, { orderBy: string[] }];
    expect(options.orderBy).toEqual(["rev_circumstancescore desc", "rev_name asc"]);
  });

  it("routes each of the four known entity sets to a distinct call, all through retrieveMultipleRecordsAsync", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    // count-coupled by design (C-TECH-067): this app has exactly four generated read
    // services (READ_SERVICES in client.ts), one per Dataverse table it reads. A fifth
    // would be a new call site requiring its own generated service and its own test, not
    // a count this file could derive without importing client.ts's private map.
    for (const entityName of ["rev_applications", "rev_reviews", "rev_applicants", "systemusers"]) {
      await listRecords({ entityName, select: ["x"] });
    }
    const tables = retrieveMultipleRecordsAsync.mock.calls.map((call) => call[0] as string);
    expect(tables).toEqual(["rev_applications", "rev_reviews", "rev_applicants", "systemusers"]);
  });

  it("rejects an entity set with no registered read service, rather than silently mis-routing", async () => {
    await expect(
      listRecords({ entityName: "not_a_real_table", select: ["x"] }),
    ).rejects.toThrow(/No generated read service is registered/);
  });

  it("omits an absent filter and orderby rather than sending an empty one", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    const [, options] = retrieveMultipleRecordsAsync.mock.calls.at(-1) as [string, Record<string, unknown>];
    expect(options).not.toHaveProperty("filter");
    expect(options).not.toHaveProperty("orderBy");
  });

  it("asks for one more row than it will show, so truncation can be detected", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    const [, options] = retrieveMultipleRecordsAsync.mock.calls.at(-1) as [string, { top: number }];
    expect(options.top).toBe(MAX_ROWS + 1);
  });

  it("reports truncation and trims to the cap rather than showing a silent subset", async () => {
    const rows = Array.from({ length: MAX_ROWS + 1 }, (_unused, index) => ({ i: index }));
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: rows });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.truncated).toBe(true);
    expect(result.rows).toHaveLength(MAX_ROWS);
  });

  it("does not report truncation at exactly the cap", async () => {
    const rows = Array.from({ length: MAX_ROWS }, (_unused, index) => ({ i: index }));
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: rows });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.truncated).toBe(false);
    expect(result.rows).toHaveLength(MAX_ROWS);
  });

  it("accepts a bare payload as well as an IOperationResult wrapper", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ value: [{ rev_name: "A" }] });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([{ rev_name: "A" }]);
  });

  it("accepts a bare array", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [{ rev_name: "A" }] });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([{ rev_name: "A" }]);
  });

  it("returns no rows for a payload it does not recognise, rather than throwing", async () => {
    // `data: undefined` (never a non-array truthy value): Rev_applicationsService.getAll's
    // own generated body does `result.data?.forEach(...)` before this ever reaches client.ts,
    // so a non-array `data` throws inside the generated service itself, not here — the shape
    // client.ts must tolerate on this path is "no rows came back", not "rows came back
    // malformed".
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: undefined });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([]);
  });

  it("turns a reported failure into a readable DataverseError carrying the status", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({
      success: false,
      error: { message: "Privilege check failed.", status: 403 },
    });
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toMatchObject({ name: "DataverseError", message: "Privilege check failed.", status: 403 });
  });

  it("still produces a message when the connector reports a failure with no reason", async () => {
    // The shape that would otherwise reach a trustee as an empty toast.
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: false });
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toThrow(/ListRecords\(rev_applications\) failed/);
  });

  it("turns a thrown error into a DataverseError", async () => {
    retrieveMultipleRecordsAsync.mockRejectedValue(new Error("Network down."));
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toBeInstanceOf(DataverseError);
  });

  it("turns a thrown non-Error into a DataverseError with a fallback message", async () => {
    retrieveMultipleRecordsAsync.mockRejectedValue("just a string");
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toThrow("just a string");
  });
});

describe("normaliseRow", () => {
  it("unwraps a dynamicProperties bag", () => {
    expect(normaliseRow({ dynamicProperties: { rev_name: "A" } })).toEqual({ rev_name: "A" });
  });
  it("passes a flat row through unchanged", () => {
    expect(normaliseRow({ rev_name: "A" })).toEqual({ rev_name: "A" });
  });
  it("returns an empty row for a non-object", () => {
    expect(normaliseRow(null)).toEqual({});
    expect(normaliseRow("x")).toEqual({});
  });
});

describe("getRecord", () => {
  it("sends a get request against the resolved typed service with the id and column allow-list", async () => {
    retrieveRecordAsync.mockResolvedValue({ success: true, data: { rev_name: "A" } });
    await getRecord({
      entityName: "rev_applications",
      recordId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      select: ["rev_name"],
    });
    expect(executeAsync).not.toHaveBeenCalled();
    expect(retrieveRecordAsync).toHaveBeenCalledWith(
      "rev_applications",
      "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      { select: ["rev_name"] },
    );
  });

  it("returns null for a 404 thrown by the call, rather than surfacing an error", async () => {
    retrieveRecordAsync.mockRejectedValue({ message: "Not found", status: 404 });
    expect(
      await getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).toBeNull();
  });

  it("returns null for a 404 reported as a resolved failure, not only a thrown one (A-TRM-3)", async () => {
    retrieveRecordAsync.mockResolvedValue({
      success: false,
      error: { message: "Not found", status: 404 },
    });
    expect(
      await getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).toBeNull();
  });

  it("throws for any other failure thrown by the call", async () => {
    retrieveRecordAsync.mockRejectedValue({ message: "Denied", status: 403 });
    await expect(
      getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).rejects.toMatchObject({ status: 403 });
  });

  it("throws for any other failure reported as a resolved failure, not only a thrown one", async () => {
    retrieveRecordAsync.mockResolvedValue({
      success: false,
      error: { message: "Denied", status: 403 },
    });
    await expect(
      getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).rejects.toMatchObject({ status: 403 });
  });

  it("returns null when the payload is not a row", async () => {
    retrieveRecordAsync.mockResolvedValue({ success: true, data: null });
    expect(
      await getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).toBeNull();
  });
});

describe("updateRecord", () => {
  it("still uses the GENERIC connector's UpdateOnlyRecord with If-Match, so it can never create a row", async () => {
    executeAsync.mockResolvedValue({ success: true, data: {} });
    await updateRecord({
      entityName: "rev_reviews",
      recordId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      item: { rev_verdict1: 1 },
    });
    expect(retrieveMultipleRecordsAsync).not.toHaveBeenCalled();
    expect(retrieveRecordAsync).not.toHaveBeenCalled();
    const operation = lastOperation();
    // `UpdateRecord` is the connector's UPSERT, and the generated typed service's own
    // `update()` cannot send `If-Match` at all (IMP-0210). Using either would make "never
    // create a review row" depend on a privilege being absent instead of on the request.
    expect(operation.tableName).toBe("commondataserviceforapps");
    expect(operation.operationName).toBe("UpdateOnlyRecord");
    expect(operation.parameters.If_Match).toBe("*");
    expect(operation.parameters.item).toEqual({ rev_verdict1: 1 });
  });

  it("throws a readable error when the write is refused", async () => {
    executeAsync.mockResolvedValue({ success: false, error: { message: "Read-only." } });
    await expect(
      updateRecord({ entityName: "rev_reviews", recordId: "x", item: {} }),
    ).rejects.toThrow("Read-only.");
  });

  it("throws a readable error when the write throws", async () => {
    executeAsync.mockRejectedValue(new Error("Timeout."));
    await expect(
      updateRecord({ entityName: "rev_reviews", recordId: "x", item: {} }),
    ).rejects.toThrow("Timeout.");
  });
});
