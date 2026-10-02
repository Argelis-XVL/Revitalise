/**
 * "Who am I" resolution.
 *
 * Every platform contract this module depends on is unverified (A-TR-11), so these tests
 * assert only what this app does with each ANSWER — never that the answer is what the
 * host or the connector will give. The valuable half is the failure paths: an unresolved
 * identity must come back as a result carrying a reason, never as a thrown error and
 * never as a silent null.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";

const getContext = vi.fn();
const listRecords = vi.fn();

vi.mock("@microsoft/power-apps/app", () => ({ getContext: () => getContext() as unknown }));
vi.mock("./client", () => ({
  listRecords: (...args: unknown[]) => listRecords(...args) as unknown,
}));

const { resolveCurrentUser } = await import("./identity");

const OBJECT_ID = "44444444-4444-4444-8444-444444444444";
const SYSTEM_USER_ID = "11111111-1111-4111-8111-111111111111";

function hostContext(user: Record<string, unknown>) {
  return { app: {}, host: {}, user };
}

beforeEach(() => {
  getContext.mockReset();
  listRecords.mockReset();
});

describe("resolveCurrentUser", () => {
  it("resolves by Entra object id, filtering on a bare guid", async () => {
    getContext.mockResolvedValue(
      hostContext({ fullName: "Kevin Trustee", objectId: OBJECT_ID, userPrincipalName: "k@example" }),
    );
    listRecords.mockResolvedValue({
      rows: [{ systemuserid: SYSTEM_USER_ID, fullname: "Kevin Trustee" }],
      truncated: false,
    });

    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBe(SYSTEM_USER_ID);
    expect(user.fullName).toBe("Kevin Trustee");
    expect(user.unresolvedReason).toBeNull();

    const request = listRecords.mock.calls[0]?.[0] as { entityName: string; filter: string };
    expect(request.entityName).toBe("systemusers");
    expect(request.filter).toBe(`azureactivedirectoryobjectid eq ${OBJECT_ID}`);
  });

  it("prefers the object id and does not fall back once it has succeeded", async () => {
    getContext.mockResolvedValue(
      hostContext({ objectId: OBJECT_ID, userPrincipalName: "k@example" }),
    );
    listRecords.mockResolvedValue({
      rows: [{ systemuserid: SYSTEM_USER_ID }],
      truncated: false,
    });
    await resolveCurrentUser();
    expect(listRecords).toHaveBeenCalledTimes(1);
  });

  it("falls back to the sign-in name when the host gives no object id", async () => {
    getContext.mockResolvedValue(hostContext({ userPrincipalName: "kevin@example.org" }));
    listRecords.mockResolvedValue({ rows: [{ systemuserid: SYSTEM_USER_ID }], truncated: false });
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBe(SYSTEM_USER_ID);
    const request = listRecords.mock.calls[0]?.[0] as { filter: string };
    expect(request.filter).toBe("domainname eq 'kevin@example.org'");
  });

  it("tries the sign-in name after the object id finds nothing", async () => {
    getContext.mockResolvedValue(
      hostContext({ objectId: OBJECT_ID, userPrincipalName: "kevin@example.org" }),
    );
    listRecords
      .mockResolvedValueOnce({ rows: [], truncated: false })
      .mockResolvedValueOnce({ rows: [{ systemuserid: SYSTEM_USER_ID }], truncated: false });
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBe(SYSTEM_USER_ID);
    expect(listRecords).toHaveBeenCalledTimes(2);
  });

  it("refuses to guess when more than one user record matches", async () => {
    // Guessing between two matches is how one trustee overwrites another's verdict.
    getContext.mockResolvedValue(hostContext({ objectId: OBJECT_ID }));
    listRecords.mockResolvedValue({
      rows: [{ systemuserid: SYSTEM_USER_ID }, { systemuserid: "22222222-2222-4222-8222-222222222222" }],
      truncated: false,
    });
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.unresolvedReason).toMatch(/more than one user record/i);
  });

  it("reports no match with a reason naming what was tried", async () => {
    getContext.mockResolvedValue(hostContext({ objectId: OBJECT_ID }));
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.unresolvedReason).toMatch(/no user record matches your entra id account/i);
  });

  it("reports a lookup that failed, without throwing", async () => {
    getContext.mockResolvedValue(hostContext({ objectId: OBJECT_ID }));
    listRecords.mockRejectedValue(new Error("Privilege check failed."));
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.unresolvedReason).toContain("Privilege check failed.");
  });

  it("reports a row with no usable id rather than accepting it", async () => {
    getContext.mockResolvedValue(hostContext({ objectId: OBJECT_ID }));
    listRecords.mockResolvedValue({ rows: [{ fullname: "No id here" }], truncated: false });
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.unresolvedReason).toMatch(/carries no id/i);
  });

  it("says the host told it nothing when neither identifier is present", async () => {
    getContext.mockResolvedValue(hostContext({ fullName: "Anon" }));
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.fullName).toBe("Anon");
    expect(user.unresolvedReason).toMatch(/did not tell this app who is signed in/i);
    expect(listRecords).not.toHaveBeenCalled();
  });

  it("says it may not be running inside Power Apps when the host context fails", async () => {
    getContext.mockRejectedValue(new Error("no host"));
    const user = await resolveCurrentUser();
    expect(user.systemUserId).toBeNull();
    expect(user.unresolvedReason).toMatch(/may not be running inside power apps/i);
  });

  it("ignores an object id that is not a guid rather than putting it in a filter", async () => {
    getContext.mockResolvedValue(hostContext({ objectId: "not-a-guid" }));
    const user = await resolveCurrentUser();
    expect(user.entraObjectId).toBeNull();
    expect(user.systemUserId).toBeNull();
    expect(listRecords).not.toHaveBeenCalled();
  });
});
