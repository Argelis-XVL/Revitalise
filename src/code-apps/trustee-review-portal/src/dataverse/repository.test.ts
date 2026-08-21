/**
 * The repository, with the connector mocked out.
 *
 * What this proves: the repository asks for the columns it is allowed to ask for, drops
 * anything the fail-closed conjunction excludes, and writes exactly two columns chosen
 * by slot.
 *
 * What it does NOT prove: anything about what the Dataverse connector actually returns
 * or accepts. The mock answers whatever this file tells it to. Every platform contract
 * involved is in the assumptions register instead of being asserted here — a test
 * written from the same guess as the code locks the guess in (`IMP-0111`).
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";

const listRecords = vi.fn();
const getRecord = vi.fn();
const updateRecord = vi.fn();

vi.mock("./client", () => ({
  listRecords: (...args: unknown[]) => listRecords(...args) as unknown,
  getRecord: (...args: unknown[]) => getRecord(...args) as unknown,
  updateRecord: (...args: unknown[]) => updateRecord(...args) as unknown,
  MAX_ROWS: 500,
}));

vi.mock("./identity", () => ({
  resolveCurrentUser: () =>
    Promise.resolve({
      systemUserId: null,
      fullName: null,
      entraObjectId: null,
      unresolvedReason: "mocked",
    }),
}));

const { dataverseRepository, TruncatedListError } = await import("./repository");
const { VERDICT_VALUES, VERDICT_NOTES_MAX_LENGTH } = await import("./schema");

const APPLICATION_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const APPLICANT_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc";
const REVIEW_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";

interface ListCall {
  entityName: string;
  select: readonly string[];
  filter?: string;
  orderBy?: string;
}

function lastListCall(): ListCall {
  const call = listRecords.mock.calls.at(-1);
  if (call === undefined) throw new Error("listRecords was never called");
  return call[0] as ListCall;
}

beforeEach(() => {
  listRecords.mockReset();
  getRecord.mockReset();
  updateRecord.mockReset();
});

describe("listApplicationsForReview", () => {
  it("asks the server for eligible rows only, by affirmative equality", () => {
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    return dataverseRepository.listApplicationsForReview().then(() => {
      const call = lastListCall();
      expect(call.entityName).toBe("rev_applications");
      expect(call.filter).toBe("rev_eligibleforround eq true");
      // `ne false` would let a null through. This asserts the shape, not just the intent.
      expect(call.filter).not.toContain("ne false");
    });
  });

  it("always names its columns — there is no select-everything path", () => {
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    return dataverseRepository.listApplicationsForReview().then(() => {
      const call = lastListCall();
      expect(call.select.length).toBeGreaterThan(0);
      expect(call.select).toContain("rev_circumstancescore");
    });
  });

  it("drops a row the SERVER returned that is not affirmatively eligible", async () => {
    // The client-side half of the conjunction, tested by making the server lie. This is
    // the case a wrong `$filter` would produce, and it must not reach the screen.
    listRecords.mockResolvedValue({
      rows: [
        { rev_applicationid: APPLICATION_ID, rev_name: "GOOD", rev_eligibleforround: true },
        {
          rev_applicationid: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
          rev_name: "BAD-FALSE",
          rev_eligibleforround: false,
        },
        { rev_applicationid: "dddddddd-dddd-4ddd-8ddd-dddddddddddd", rev_name: "BAD-MISSING" },
        {
          rev_applicationid: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
          rev_name: "BAD-NULL",
          rev_eligibleforround: null,
        },
      ],
      truncated: false,
    });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows.map((r) => r.reference)).toEqual(["GOOD"]);
  });

  it("drops a row with no id rather than rendering an unopenable case", async () => {
    listRecords.mockResolvedValue({
      rows: [{ rev_name: "NO-ID", rev_eligibleforround: true }],
      truncated: false,
    });
    expect(await dataverseRepository.listApplicationsForReview()).toEqual([]);
  });

  it("reports a truncated list as an error instead of showing a partial round", async () => {
    listRecords.mockResolvedValue({ rows: [], truncated: true });
    await expect(dataverseRepository.listApplicationsForReview()).rejects.toBeInstanceOf(
      TruncatedListError,
    );
  });

  it("never sources the region from the break location", async () => {
    // rev_breaklocation is the HOLIDAY's location, not the applicant's region. Filling
    // region from it would be a wrong answer dressed up as a complete screen.
    listRecords
      .mockResolvedValueOnce({
        rows: [
          {
            rev_applicationid: APPLICATION_ID,
            rev_name: "REV-2026-001",
            rev_eligibleforround: true,
            rev_breaklocation: "Coastal, Devon",
            _rev_applicantid_value: APPLICANT_ID,
          },
        ],
        truncated: false,
      })
      .mockResolvedValueOnce({ rows: [{ rev_applicantid: APPLICANT_ID }], truncated: false });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.region).toEqual({ kind: "not-recorded" });
  });

  it("reports a redaction flag that is absent as not released", async () => {
    listRecords.mockResolvedValue({
      rows: [{ rev_applicationid: APPLICATION_ID, rev_name: "X", rev_eligibleforround: true }],
      truncated: false,
    });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.redactionReleased).toBe(false);
  });
});

describe("getApplication", () => {
  it("returns null for a case that is not eligible, even when its id is known", async () => {
    // FR-038 on the direct-read path: knowing an id must not be a way around the round.
    getRecord.mockResolvedValue({
      rev_applicationid: APPLICATION_ID,
      rev_name: "REV-2026-001",
      rev_eligibleforround: false,
      rev_narrativeredacted: "should never be reachable",
    });
    expect(await dataverseRepository.getApplication(APPLICATION_ID)).toBeNull();
  });

  it("returns null when the row is absent", async () => {
    getRecord.mockResolvedValue(null);
    expect(await dataverseRepository.getApplication(APPLICATION_ID)).toBeNull();
  });

  it("maps the narrative and the score breakdown when the case is eligible", async () => {
    getRecord.mockResolvedValue({
      rev_applicationid: APPLICATION_ID,
      rev_name: "REV-2026-001",
      rev_eligibleforround: true,
      rev_redactionreleased: true,
      rev_narrativeredacted: "Redacted text.",
      rev_scorebreakdown: "Wellbeing 20",
      rev_circumstancescore: 42,
    });
    const detail = await dataverseRepository.getApplication(APPLICATION_ID);
    expect(detail?.redactedNarrative).toBe("Redacted text.");
    expect(detail?.scoreBreakdown).toBe("Wellbeing 20");
    expect(detail?.circumstanceScore).toBe(42);
  });

  it("refuses an id that is not a guid rather than sending it to the connector", async () => {
    await expect(dataverseRepository.getApplication("' or 1 eq 1")).rejects.toThrow(/Not a GUID/);
    expect(getRecord).not.toHaveBeenCalled();
  });
});

describe("getReviewForApplication", () => {
  it("filters by the application lookup's OData value form", () => {
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    return dataverseRepository.getReviewForApplication(APPLICATION_ID).then(() => {
      const call = lastListCall();
      expect(call.entityName).toBe("rev_reviews");
      expect(call.filter).toContain(`_rev_applicationid_value eq ${APPLICATION_ID}`);
    });
  });

  it("returns null when no review row exists — a first-class state, not an error", async () => {
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    expect(await dataverseRepository.getReviewForApplication(APPLICATION_ID)).toBeNull();
  });

  it("maps both trustee lookups and both verdict slots", async () => {
    listRecords.mockResolvedValue({
      rows: [
        {
          rev_reviewid: REVIEW_ID,
          rev_name: "REV-R-00001",
          _rev_trustee1_value: "11111111-1111-4111-8111-111111111111",
          _rev_trustee2_value: "22222222-2222-4222-8222-222222222222",
          rev_verdict1: 1,
          rev_notes2: "Second trustee note.",
          rev_staffrecommendation: "Support.",
        },
      ],
      truncated: false,
    });
    const review = await dataverseRepository.getReviewForApplication(APPLICATION_ID);
    expect(review?.trustee1Id).toBe("11111111-1111-4111-8111-111111111111");
    expect(review?.trustee2Id).toBe("22222222-2222-4222-8222-222222222222");
    expect(review?.verdict1).toBe(1);
    expect(review?.verdict2).toBeNull();
    expect(review?.notes2).toBe("Second trustee note.");
  });
});

describe("saveVerdict", () => {
  it("writes exactly the two columns of the trustee-1 slot", async () => {
    updateRecord.mockResolvedValue(undefined);
    await dataverseRepository.saveVerdict({
      reviewId: REVIEW_ID,
      slot: "trustee1",
      verdict: VERDICT_VALUES.approve,
      notes: "  Support.  ",
    });
    expect(updateRecord).toHaveBeenCalledTimes(1);
    const request = updateRecord.mock.calls[0]?.[0] as {
      entityName: string;
      recordId: string;
      item: Record<string, unknown>;
    };
    expect(request.entityName).toBe("rev_reviews");
    expect(request.recordId).toBe(REVIEW_ID);
    expect(Object.keys(request.item).sort()).toEqual(["rev_notes1", "rev_verdict1"]);
    expect(request.item.rev_verdict1).toBe(VERDICT_VALUES.approve);
    expect(request.item.rev_notes1).toBe("Support.");
  });

  it("writes the trustee-2 columns for the trustee-2 slot, and nothing of trustee 1", async () => {
    updateRecord.mockResolvedValue(undefined);
    await dataverseRepository.saveVerdict({
      reviewId: REVIEW_ID,
      slot: "trustee2",
      verdict: VERDICT_VALUES.reject,
      notes: "",
    });
    const request = updateRecord.mock.calls[0]?.[0] as { item: Record<string, unknown> };
    expect(Object.keys(request.item).sort()).toEqual(["rev_notes2", "rev_verdict2"]);
    expect(request.item.rev_verdict2).toBe(VERDICT_VALUES.reject);
    // Empty notes clear the column rather than storing an empty string.
    expect(request.item.rev_notes2).toBeNull();
  });

  it("never writes any other column on the review row", async () => {
    updateRecord.mockResolvedValue(undefined);
    await dataverseRepository.saveVerdict({
      reviewId: REVIEW_ID,
      slot: "trustee1",
      verdict: VERDICT_VALUES.defer,
      notes: "x",
    });
    const request = updateRecord.mock.calls[0]?.[0] as { item: Record<string, unknown> };
    for (const forbidden of [
      "rev_outcome",
      "rev_finalisedon",
      "rev_staffrecommendation",
      "rev_trustee1",
      "rev_trustee2",
      "rev_nonqualificationreason",
      "rev_paneldate",
    ]) {
      expect(request.item).not.toHaveProperty(forbidden);
    }
  });

  it("stops over-length notes before the round trip", async () => {
    await expect(
      dataverseRepository.saveVerdict({
        reviewId: REVIEW_ID,
        slot: "trustee1",
        verdict: VERDICT_VALUES.approve,
        notes: "x".repeat(VERDICT_NOTES_MAX_LENGTH + 1),
      }),
    ).rejects.toThrow(new RegExp(String(VERDICT_NOTES_MAX_LENGTH)));
    expect(updateRecord).not.toHaveBeenCalled();
  });

  it("refuses a review id that is not a guid", async () => {
    await expect(
      dataverseRepository.saveVerdict({
        reviewId: "not-a-guid",
        slot: "trustee1",
        verdict: 1,
        notes: "",
      }),
    ).rejects.toThrow(/Not a GUID/);
    expect(updateRecord).not.toHaveBeenCalled();
  });
});

describe("region resolution — FR-034, FR-027", () => {
  function applicationRow(overrides: Record<string, unknown> = {}) {
    return {
      rev_applicationid: APPLICATION_ID,
      rev_name: "REV-2026-001",
      rev_eligibleforround: true,
      _rev_applicantid_value: APPLICANT_ID,
      ...overrides,
    };
  }

  it("reads the region from rev_applicants, asking for exactly two columns", async () => {
    listRecords
      .mockResolvedValueOnce({ rows: [applicationRow()], truncated: false })
      .mockResolvedValueOnce({
        rows: [{ rev_applicantid: APPLICANT_ID, rev_locationarea: 9 }],
        truncated: false,
      });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.region).toEqual({ kind: "known", value: 9 });

    const applicantCall = listRecords.mock.calls[1]?.[0] as ListCall;
    expect(applicantCall.entityName).toBe("rev_applicants");
    // Two columns and no more: rev_applicant carries twelve secured identifying columns
    // and this app has no business naming any of them.
    expect([...applicantCall.select]).toEqual(["rev_applicantid", "rev_locationarea"]);
    expect(applicantCall.filter).toBe(`rev_applicantid eq ${APPLICANT_ID}`);
  });

  it("reports a region the applicant row does not carry as not-recorded", async () => {
    listRecords
      .mockResolvedValueOnce({ rows: [applicationRow()], truncated: false })
      .mockResolvedValueOnce({
        rows: [{ rev_applicantid: APPLICANT_ID, rev_locationarea: null }],
        truncated: false,
      });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.region).toEqual({ kind: "not-recorded" });
  });

  it("reports the region as unavailable when the applicant read FAILS, and still lists the case", async () => {
    // The state to expect until the REV Trustee role's new prvReadrev_applicant reaches
    // the environment. A trustee must still get their list.
    listRecords
      .mockResolvedValueOnce({ rows: [applicationRow()], truncated: false })
      .mockRejectedValueOnce(new Error("Privilege check failed."));
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows).toHaveLength(1);
    expect(rows[0]?.region).toEqual({ kind: "unavailable" });
  });

  it("reports the region as unavailable when the applicant row is simply absent", async () => {
    listRecords
      .mockResolvedValueOnce({ rows: [applicationRow()], truncated: false })
      .mockResolvedValueOnce({ rows: [], truncated: false });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.region).toEqual({ kind: "unavailable" });
  });

  it("reports the region as unavailable, and asks for nothing, when there is no applicant lookup", async () => {
    listRecords.mockResolvedValueOnce({
      rows: [applicationRow({ _rev_applicantid_value: null })],
      truncated: false,
    });
    const rows = await dataverseRepository.listApplicationsForReview();
    expect(rows[0]?.region).toEqual({ kind: "unavailable" });
    expect(listRecords).toHaveBeenCalledTimes(1);
  });

  it("reads no applicant row on account of a case the trustee may not see", async () => {
    // The fail-closed conjunction is applied BEFORE the applicant lookup, so an
    // ineligible case cannot cause a read against its applicant.
    const hiddenApplicant = "dddddddd-dddd-4ddd-8ddd-dddddddddddd";
    listRecords
      .mockResolvedValueOnce({
        rows: [
          applicationRow(),
          applicationRow({
            rev_applicationid: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
            rev_eligibleforround: false,
            _rev_applicantid_value: hiddenApplicant,
          }),
        ],
        truncated: false,
      })
      .mockResolvedValueOnce({
        rows: [{ rev_applicantid: APPLICANT_ID, rev_locationarea: 7 }],
        truncated: false,
      });
    await dataverseRepository.listApplicationsForReview();
    const applicantCall = listRecords.mock.calls[1]?.[0] as ListCall;
    expect(applicantCall.filter).not.toContain(hiddenApplicant);
    expect(applicantCall.filter).toContain(APPLICANT_ID);
  });

  it("asks for each applicant once, however many applications they have", async () => {
    listRecords
      .mockResolvedValueOnce({
        rows: [
          applicationRow(),
          applicationRow({ rev_applicationid: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee" }),
        ],
        truncated: false,
      })
      .mockResolvedValueOnce({
        rows: [{ rev_applicantid: APPLICANT_ID, rev_locationarea: 7 }],
        truncated: false,
      });
    await dataverseRepository.listApplicationsForReview();
    const applicantCall = listRecords.mock.calls[1]?.[0] as ListCall;
    expect(applicantCall.filter?.match(/ or /g) ?? []).toHaveLength(0);
  });

  it("chunks the applicant filter rather than building one enormous query string", async () => {
    // 120 distinct applicants at a chunk size of 50 is three requests. An OR-joined
    // filter over all of them would be several kilobytes of URL.
    const applications = Array.from({ length: 120 }, (_unused, index) => {
      const hex = index.toString(16).padStart(2, "0");
      return applicationRow({
        rev_applicationid: `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaa${hex}`,
        _rev_applicantid_value: `cccccccc-cccc-4ccc-8ccc-cccccccccc${hex}`,
      });
    });
    listRecords.mockResolvedValueOnce({ rows: applications, truncated: false });
    listRecords.mockResolvedValue({ rows: [], truncated: false });
    await dataverseRepository.listApplicationsForReview();
    // 1 application call + 3 applicant chunks.
    expect(listRecords).toHaveBeenCalledTimes(4);
  });

  it("resolves the region on the detail path too", async () => {
    getRecord.mockResolvedValue(applicationRow({ rev_narrativeredacted: "text" }));
    listRecords.mockResolvedValue({
      rows: [{ rev_applicantid: APPLICANT_ID, rev_locationarea: 2 }],
      truncated: false,
    });
    const detail = await dataverseRepository.getApplication(APPLICATION_ID);
    expect(detail?.region).toEqual({ kind: "known", value: 2 });
  });

  it("reads no applicant row for an ineligible case on the detail path", async () => {
    getRecord.mockResolvedValue(applicationRow({ rev_eligibleforround: false }));
    expect(await dataverseRepository.getApplication(APPLICATION_ID)).toBeNull();
    expect(listRecords).not.toHaveBeenCalled();
  });
});

describe("the app has no create or delete path at all", () => {
  // Asserted against the REAL client.ts on disk, not against the mock above. Importing
  // the module here would resolve to the mock and the assertion would describe the
  // fixture rather than the app — a gate that cannot fail.
  const source = readFileSync(join(__dirname, "client.ts"), "utf8");

  it("read the real client source", () => {
    expect(source).toContain("export async function listRecords");
  });

  it("declares no create operation", () => {
    // The REV Trustee role holds no prvCreaterev_review by design. The app must not have
    // a create call to reach for by accident, so the client surface omits one entirely.
    expect(source).not.toMatch(/export (async )?function \w*[Cc]reate/);
    expect(source).not.toContain('operationName: "CreateRecord"');
  });

  it("declares no delete operation", () => {
    expect(source).not.toMatch(/export (async )?function \w*[Dd]elete/);
    expect(source).not.toContain('operationName: "DeleteRecord"');
  });

  it("uses the update-only connector operation, not the upsert", () => {
    // `UpdateRecord` is documented as an upsert. Using it would make "never create a
    // review row" depend on a privilege being absent instead of on the request.
    expect(source).toContain('operationName: "UpdateOnlyRecord"');
    expect(source).not.toContain('operationName: "UpdateRecord"');
  });
});
