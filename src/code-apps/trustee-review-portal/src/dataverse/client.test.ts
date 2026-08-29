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
const getContext = vi.fn();

vi.mock("@microsoft/power-apps/data", () => ({
  getClient: () => ({ executeAsync, retrieveMultipleRecordsAsync, retrieveRecordAsync }),
  // Only Rev_applicationsService and Rev_applicantsService import these (their tables carry
  // multi-select option sets). None of this app's own `select` allow-lists name one, so a
  // pass-through is enough to let those generated services load in this test.
  serializeMultiSelectPicklistFields: (record: unknown) => record,
  deserializeMultiSelectPicklistFields: (record: unknown) => record,
}));

vi.mock("@microsoft/power-apps/app", () => ({ getContext: () => getContext() as unknown }));

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

  it("routes each of the seven registered entity sets to a distinct call, all through retrieveMultipleRecordsAsync", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    // count-coupled by design (C-TECH-067): this app reads seven Dataverse tables, one entry
    // per table in READ_SERVICES. An eighth would be a new call site requiring its own
    // service and its own test, not a count this file could derive without importing
    // client.ts's private map. **The count was stale at five when the sixth was added**
    // (`rev_roundstatisticsrequests`, 2026-08-27) because the loop below only exercised the
    // tables it listed — corrected here along with the seventh.
    //
    // SIX of the seven are backed by a GENERATED per-table service. One leans on a
    // hand-written stand-in, deliberately:
    //
    //   - `rev_roundfinances` (`roundFinanceReadService.ts`, A-LAND-1 CLOSED) — the generated
    //     service now exists and the two are proven identical; swapping them is a deliberate
    //     separate cleanup, not a defect fix.
    //
    // `rev_roundstatisticsresults` (`A-RES-1`) closed the same way 2026-08-29 (`IMP-0485`,
    // TAD §12.3 step 9): the table now exists live, `pa app add data-source` generated
    // `Rev_roundstatisticsresultsService`, and the stand-in file was deleted rather than left
    // to be swapped later — unlike `rev_roundfinances`, this table never had a period where a
    // generated service existed alongside an undeleted stand-in.
    //
    // What this test asserts for all seven is the one thing that must be true of every one of
    // them: the read goes through the `"Dataverse"`-type data source path
    // (`retrieveMultipleRecordsAsync`) and NOT through the generic connector's `executeAsync`,
    // which resolved its organisation URL as null for a real signed-in trustee (IMP-0224).
    const registered = [
      "rev_applications",
      "rev_reviews",
      "rev_applicants",
      "systemusers",
      "rev_roundfinances",
      "rev_roundstatisticsrequests",
      "rev_roundstatisticsresults",
    ];
    for (const entityName of registered) {
      await listRecords({ entityName, select: ["x"] });
    }
    const tables = retrieveMultipleRecordsAsync.mock.calls.map((call) => call[0] as string);
    expect(tables).toEqual(registered);
    expect(executeAsync).not.toHaveBeenCalled();
  });

  it("sends an explicit top when the caller asks for a bounded probe, and clamps it to the cap", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    // TAD §5.4 step 1 asks rev_roundfinance with `top 2`: one row is the expected case and
    // two is enough to know the answer is "ambiguous".
    await listRecords({ entityName: "rev_roundfinances", select: ["rev_name"], top: 2 });
    const [, probe] = retrieveMultipleRecordsAsync.mock.calls.at(-1) as [string, { top: number }];
    expect(probe.top).toBe(2);

    // An explicit top can only ever narrow the read, never widen it past what this app is
    // willing to hold in a browser.
    await listRecords({ entityName: "rev_applications", select: ["rev_name"], top: 5000 });
    const [, clamped] = retrieveMultipleRecordsAsync.mock.calls.at(-1) as [string, { top: number }];
    expect(clamped.top).toBe(MAX_ROWS + 1);
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
  const ORG_URL = "https://org.crm.dynamics.com";

  beforeEach(() => {
    // Resolved once per module (getOrgUrl caches), so every test in this file's process gets
    // a valid org URL unless a specific test overrides it below.
    getContext.mockResolvedValue({ app: { dataverseOrgUrl: ORG_URL } });
  });

  it("uses the GENERIC connector's UpdateOnlyRecordWithOrganization with If-Match and the resolved org URL, so it can never create a row and never resolves org as null", async () => {
    executeAsync.mockResolvedValue({ success: true, data: {} });
    await updateRecord({
      entityName: "rev_reviews",
      recordId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      item: { rev_verdict1: 1 },
    });
    expect(retrieveMultipleRecordsAsync).not.toHaveBeenCalled();
    expect(retrieveRecordAsync).not.toHaveBeenCalled();
    const operation = lastOperation();
    // The plain `UpdateOnlyRecord`/`UpdateRecord` operations resolve their organisation
    // through the connector's per-user OAuth connection, which came back `null` for a real
    // signed-in trustee ("Invalid organization URL 'null' provided") — this asserts the app
    // never regresses to either. The generated typed service's own `update()` cannot send
    // `If-Match` at all (IMP-0210), so using it would make "never create a review row"
    // depend on a privilege being absent instead of on the request.
    expect(operation.tableName).toBe("commondataserviceforapps");
    expect(operation.operationName).toBe("UpdateOnlyRecordWithOrganization");
    expect(operation.parameters.If_Match).toBe("*");
    expect(operation.parameters.organization).toBe(ORG_URL);
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
