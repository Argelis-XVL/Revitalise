/**
 * The connector boundary, with the Power Apps SDK mocked.
 *
 * What this proves: that this app sends the operation and parameters it intends to, and
 * that every failure shape becomes a `DataverseError` with a message a trustee can read
 * rather than an unhandled rejection.
 *
 * What it does NOT prove: that the connector accepts any of it, or returns either of the
 * two row shapes handled below. Those are open assumptions (A-TR-8, A-TR-9) and are
 * deliberately not asserted here — asserting a guess is how a guess becomes permanent
 * (`IMP-0111`).
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const executeAsync = vi.fn();

vi.mock("@microsoft/power-apps/data", () => ({
  getClient: () => ({ executeAsync }),
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
});

describe("listRecords", () => {
  it("sends ListRecords against the generated data source, not against a table", () => {
    executeAsync.mockResolvedValue({ success: true, data: { value: [] } });
    return listRecords({
      entityName: "rev_applications",
      select: ["rev_name", "rev_status"],
      filter: "rev_eligibleforround eq true",
      orderBy: "rev_name asc",
    }).then(() => {
      const operation = lastOperation();
      // `tableName` is the DATA SOURCE key from dataSourcesInfo; the Dataverse table
      // travels in parameters.entityName.
      expect(operation.tableName).toBe("commondataserviceforapps");
      expect(operation.operationName).toBe("ListRecords");
      expect(operation.parameters).toMatchObject({
        entityName: "rev_applications",
        $select: "rev_name,rev_status",
        $filter: "rev_eligibleforround eq true",
        $orderby: "rev_name asc",
      });
    });
  });

  it("omits an absent filter and orderby rather than sending an empty one", async () => {
    executeAsync.mockResolvedValue({ success: true, data: { value: [] } });
    await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(lastOperation().parameters).not.toHaveProperty("$filter");
    expect(lastOperation().parameters).not.toHaveProperty("$orderby");
  });

  it("asks for one more row than it will show, so truncation can be detected", async () => {
    executeAsync.mockResolvedValue({ success: true, data: { value: [] } });
    await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(lastOperation().parameters.$top).toBe(MAX_ROWS + 1);
  });

  it("reports truncation and trims to the cap rather than showing a silent subset", async () => {
    const rows = Array.from({ length: MAX_ROWS + 1 }, (_unused, index) => ({ i: index }));
    executeAsync.mockResolvedValue({ success: true, data: { value: rows } });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.truncated).toBe(true);
    expect(result.rows).toHaveLength(MAX_ROWS);
  });

  it("does not report truncation at exactly the cap", async () => {
    const rows = Array.from({ length: MAX_ROWS }, (_unused, index) => ({ i: index }));
    executeAsync.mockResolvedValue({ success: true, data: { value: rows } });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.truncated).toBe(false);
    expect(result.rows).toHaveLength(MAX_ROWS);
  });

  it("accepts a bare payload as well as an IOperationResult wrapper", async () => {
    executeAsync.mockResolvedValue({ value: [{ rev_name: "A" }] });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([{ rev_name: "A" }]);
  });

  it("accepts a bare array", async () => {
    executeAsync.mockResolvedValue({ success: true, data: [{ rev_name: "A" }] });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([{ rev_name: "A" }]);
  });

  it("returns no rows for a payload it does not recognise, rather than throwing", async () => {
    executeAsync.mockResolvedValue({ success: true, data: "nonsense" });
    const result = await listRecords({ entityName: "rev_applications", select: ["rev_name"] });
    expect(result.rows).toEqual([]);
  });

  it("turns a reported failure into a readable DataverseError carrying the status", async () => {
    executeAsync.mockResolvedValue({
      success: false,
      error: { message: "Privilege check failed.", status: 403 },
    });
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toMatchObject({ name: "DataverseError", message: "Privilege check failed.", status: 403 });
  });

  it("still produces a message when the connector reports a failure with no reason", async () => {
    // The shape that would otherwise reach a trustee as an empty toast.
    executeAsync.mockResolvedValue({ success: false });
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toThrow(/ListRecords\(rev_applications\) failed/);
  });

  it("turns a thrown error into a DataverseError", async () => {
    executeAsync.mockRejectedValue(new Error("Network down."));
    await expect(
      listRecords({ entityName: "rev_applications", select: ["rev_name"] }),
    ).rejects.toBeInstanceOf(DataverseError);
  });

  it("turns a thrown non-Error into a DataverseError with a fallback message", async () => {
    executeAsync.mockRejectedValue("just a string");
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
  it("sends GetItem with the record id and the column allow-list", async () => {
    executeAsync.mockResolvedValue({ success: true, data: { rev_name: "A" } });
    await getRecord({
      entityName: "rev_applications",
      recordId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      select: ["rev_name"],
    });
    const operation = lastOperation();
    expect(operation.operationName).toBe("GetItem");
    expect(operation.parameters).toMatchObject({
      recordId: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      $select: "rev_name",
    });
  });

  it("returns null for a 404 rather than surfacing an error", async () => {
    executeAsync.mockRejectedValue({ message: "Not found", status: 404 });
    expect(
      await getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).toBeNull();
  });

  it("throws for any other failure", async () => {
    executeAsync.mockRejectedValue({ message: "Denied", status: 403 });
    await expect(
      getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).rejects.toMatchObject({ status: 403 });
  });

  it("returns null when the payload is not a row", async () => {
    executeAsync.mockResolvedValue({ success: true, data: null });
    expect(
      await getRecord({ entityName: "rev_applications", recordId: "x", select: ["rev_name"] }),
    ).toBeNull();
  });
});

describe("updateRecord", () => {
  it("uses UpdateOnlyRecord with If-Match, so it can never create a row", async () => {
    executeAsync.mockResolvedValue({ success: true, data: {} });
    await updateRecord({
      entityName: "rev_reviews",
      recordId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      item: { rev_verdict1: 1 },
    });
    const operation = lastOperation();
    // `UpdateRecord` is the connector's UPSERT. Using it would make "never create a
    // review row" depend on a privilege being absent instead of on the request itself.
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
