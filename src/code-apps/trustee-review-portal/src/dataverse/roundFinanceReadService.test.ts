/**
 * The `rev_roundfinances` stand-in read service — A-LAND-1.
 *
 * What this proves is narrow and it is the only thing worth proving here: that the
 * stand-in makes the SAME call a generated per-table service makes — the
 * `"Dataverse"`-type data source path — against the entity-set name `schema.ts` holds, and
 * that it does not touch the generic connector's `executeAsync`.
 *
 * That last part is the point. Reads were migrated off the generic connector in `IMP-0224`
 * because it resolved its Dataverse organisation URL as `null` for a real signed-in trustee
 * and no CLI flag fixes the non-table form of that data source. A stand-in written the
 * obvious way — `executeAsync({ connectorOperation: { operationName: "ListRecords" } })` —
 * would have compiled, passed every unit test, and failed live in exactly the way this app
 * has already lost a day to. So the transport is asserted, not assumed.
 *
 * What this does NOT prove: that the call succeeds. It cannot, until
 * `pa app add data-source --table rev_roundfinance` regenerates `dataSourcesInfo` with an
 * entry for this table. The failure mode is a thrown error the landing screen already
 * renders as a diagnostic — see `roundFinanceReadService.ts` for the whole assumption.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const executeAsync = vi.fn();
const retrieveMultipleRecordsAsync = vi.fn();
const retrieveRecordAsync = vi.fn();

vi.mock("@microsoft/power-apps/data", () => ({
  getClient: () => ({ executeAsync, retrieveMultipleRecordsAsync, retrieveRecordAsync }),
  serializeMultiSelectPicklistFields: (record: unknown) => record,
  deserializeMultiSelectPicklistFields: (record: unknown) => record,
}));

const { Rev_roundfinancesStandInService } = await import("./roundFinanceReadService");
const { ENTITY_SETS } = await import("./schema");

beforeEach(() => {
  executeAsync.mockReset();
  retrieveMultipleRecordsAsync.mockReset();
  retrieveRecordAsync.mockReset();
});

describe("Rev_roundfinancesStandInService", () => {
  it("lists through the Dataverse-type data source path, never the generic connector", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await Rev_roundfinancesStandInService.getAll({ select: ["rev_name"], top: 2 });
    expect(retrieveMultipleRecordsAsync).toHaveBeenCalledWith(ENTITY_SETS.roundFinance, {
      select: ["rev_name"],
      top: 2,
    });
    expect(executeAsync).not.toHaveBeenCalled();
  });

  it("reads one row through the same path", async () => {
    retrieveRecordAsync.mockResolvedValue({ success: true, data: {} });
    await Rev_roundfinancesStandInService.get("an-id", { select: ["rev_name"] });
    expect(retrieveRecordAsync).toHaveBeenCalledWith(ENTITY_SETS.roundFinance, "an-id", {
      select: ["rev_name"],
    });
    expect(executeAsync).not.toHaveBeenCalled();
  });

  it("takes its data source name from schema.ts rather than spelling it again", () => {
    // The entity-set name is platform-assigned (E1, read back live 2026-08-25, IMP-0316).
    // One place in this app writes it, so there is one place to correct if a future table
    // pluralises differently.
    expect(ENTITY_SETS.roundFinance).toBe("rev_roundfinances");
  });

  it("passes options through untouched, including no options at all", async () => {
    retrieveMultipleRecordsAsync.mockResolvedValue({ success: true, data: [] });
    await Rev_roundfinancesStandInService.getAll();
    expect(retrieveMultipleRecordsAsync).toHaveBeenCalledWith(ENTITY_SETS.roundFinance, undefined);
  });
});
