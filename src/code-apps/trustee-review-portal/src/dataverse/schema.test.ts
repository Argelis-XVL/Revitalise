/**
 * The disclosure gate — the reason this feature exists.
 *
 * `rev_application` carries Article 9 special-category free-text columns that must never
 * reach a trustee. The forbidden set is NOT hand-listed here: it is RE-DERIVED at test
 * time from `IsSecured=1` in the solution's own `Entity.xml`, so a column secured
 * tomorrow is forbidden tomorrow with no edit to this file. That is the invariant form
 * `knowledge/technology/coding-standards.md` asks for in preference to a restated list.
 *
 * The forbidden names are also never written as literals in this file — they are read
 * from source at runtime. `IMP-0024`: a negative-test fixture for a scanner must not be
 * a literal in the scanned tree, or the scanner finds its own test.
 *
 * What this proves: no file in this app names a secured column. What it does NOT prove:
 * that the connector would refuse to return one. That control is elsewhere and is not
 * ours — `REV Trustee` is deliberately not a member of the `REV_TrusteeRestricted`
 * column-security profile, and non-membership IS the control (`IMP-0153`).
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  APPLICATION_DETAIL_COLUMNS,
  APPLICATION_LIST_COLUMNS,
  APPLICATION_STATUS_LABELS,
  ENTITY_SETS,
  optionLabel,
  REVIEW_COLUMNS,
  VERDICT_LABELS,
  VERDICT_NOTES_MAX_LENGTH,
  VERDICT_VALUES,
} from "./schema";

/** This app's own root — three levels up from src/dataverse/. */
const APP_ROOT = resolve(__dirname, "..", "..");
/** The repository root, three levels above src/code-apps/<slug>/. */
const REPO_ROOT = resolve(APP_ROOT, "..", "..", "..");
const APPLICATION_ENTITY_XML = join(
  REPO_ROOT,
  "src",
  "solutions",
  "RevitaliseGrantAutomation",
  "Entities",
  "rev_application",
  "Entity.xml",
);

const SKIP_DIRECTORIES = new Set([
  "node_modules",
  "dist",
  "coverage",
  ".power",
  // Generator output from `pac code add-data-source`. Not authored here, not editable,
  // and independently verified to contain no `rev_` reference at all.
  "generated",
]);

const SCANNED_EXTENSIONS = [".ts", ".tsx", ".css", ".json", ".md", ".html", ".js"];

function collectFiles(directory: string, found: string[] = []): string[] {
  for (const entry of readdirSync(directory)) {
    const full = join(directory, entry);
    if (statSync(full).isDirectory()) {
      if (SKIP_DIRECTORIES.has(entry)) continue;
      collectFiles(full, found);
      continue;
    }
    if (SCANNED_EXTENSIONS.some((extension) => entry.endsWith(extension))) found.push(full);
  }
  return found;
}

/**
 * Every `IsSecured=1` column on `rev_application`, read from solution source.
 *
 * Throws rather than returning an empty set if the file cannot be read or yields no
 * secured columns: an empty forbidden set would make this whole suite a gate that
 * cannot fail, which is this project's most frequently recorded defect class.
 */
function securedApplicationColumns(): string[] {
  const xml = readFileSync(APPLICATION_ENTITY_XML, "utf8");
  const secured: string[] = [];
  for (const chunk of xml.split("<attribute ").slice(1)) {
    const body = chunk.split("</attribute>")[0] ?? "";
    const logicalName = /<LogicalName>([a-z0-9_]+)<\/LogicalName>/.exec(body)?.[1];
    const isSecured = /<IsSecured>(\d)<\/IsSecured>/.exec(body)?.[1];
    if (logicalName !== undefined && isSecured === "1") secured.push(logicalName);
  }
  if (secured.length === 0) {
    throw new Error(
      `No IsSecured=1 columns were found in ${APPLICATION_ENTITY_XML}. Either the path is ` +
        "wrong or the parser no longer matches the file's shape — either way this gate is " +
        "not checking anything and must be fixed, not skipped.",
    );
  }
  return secured;
}

describe("no secured column is named anywhere in this app", () => {
  const forbidden = securedApplicationColumns();
  const files = collectFiles(join(APP_ROOT, "src")).concat(
    collectFiles(APP_ROOT).filter((f) => !relative(APP_ROOT, f).includes("/")),
  );

  it("found the secured columns to check against", () => {
    // A positive control. If solution source ever stops declaring secured columns, this
    // fails here rather than letting the scan below pass vacuously.
    expect(forbidden.length).toBeGreaterThan(0);
  });

  it("found files to scan", () => {
    expect(files.length).toBeGreaterThan(10);
  });

  it("names no secured column in any query, type, comment or stylesheet", () => {
    const offences: string[] = [];
    for (const file of files) {
      const content = readFileSync(file, "utf8");
      for (const column of forbidden) {
        if (content.includes(column)) {
          offences.push(`${relative(APP_ROOT, file)} names the secured column ${column}`);
        }
      }
    }
    expect(offences).toEqual([]);
  });

  it("binds the trustee-visible narrative column, and only that one", () => {
    // The positive half: proving absence of the raw column means nothing unless the
    // redacted one is actually bound.
    const detail = APPLICATION_DETAIL_COLUMNS.join(",");
    expect(detail).toContain("rev_narrativeredacted");
    const narrativeColumns = APPLICATION_DETAIL_COLUMNS.filter((c) => c.includes("narrative"));
    expect(narrativeColumns).toEqual(["rev_narrativeredacted"]);
  });
});

describe("column allow-lists", () => {
  it("selects everything FR-034 names on the summary list", () => {
    for (const column of [
      "rev_circumstancescore",
      "rev_breakstart",
      "rev_breakend",
      "rev_status",
    ]) {
      expect(APPLICATION_LIST_COLUMNS).toContain(column);
    }
  });

  it("selects both halves of the fail-closed conjunction so it can be re-asserted", () => {
    expect(APPLICATION_LIST_COLUMNS).toContain("rev_eligibleforround");
    expect(APPLICATION_LIST_COLUMNS).toContain("rev_redactionreleased");
  });

  it("selects everything FR-035 names on the detail screen", () => {
    for (const column of ["rev_narrativeredacted", "rev_scorebreakdown", "rev_breaklocation"]) {
      expect(APPLICATION_DETAIL_COLUMNS).toContain(column);
    }
  });

  it("selects the staff recommendation and both verdict slots from the review row", () => {
    for (const column of [
      "rev_staffrecommendation",
      "rev_verdict1",
      "rev_verdict2",
      "rev_notes1",
      "rev_notes2",
      "_rev_trustee1_value",
      "_rev_trustee2_value",
    ]) {
      expect(REVIEW_COLUMNS).toContain(column);
    }
  });

  it("has no duplicate columns in any allow-list", () => {
    for (const list of [APPLICATION_LIST_COLUMNS, APPLICATION_DETAIL_COLUMNS, REVIEW_COLUMNS]) {
      expect(new Set(list).size).toBe(list.length);
    }
  });
});

describe("option-set labels", () => {
  it("labels every verdict FR-037 names", () => {
    expect(optionLabel(VERDICT_LABELS, VERDICT_VALUES.approve)).toBe("Approve");
    expect(optionLabel(VERDICT_LABELS, VERDICT_VALUES.defer)).toBe("Defer");
    expect(optionLabel(VERDICT_LABELS, VERDICT_VALUES.reject)).toBe("Reject");
  });

  it("never returns an empty string, for any input", () => {
    expect(optionLabel(APPLICATION_STATUS_LABELS, null)).toBe("Not set");
    expect(optionLabel(APPLICATION_STATUS_LABELS, undefined)).toBe("Not set");
    expect(optionLabel(APPLICATION_STATUS_LABELS, 12345)).toBe("Unknown (12345)");
    expect(optionLabel({}, 1)).toBe("Unknown (1)");
  });
});

describe("schema constants", () => {
  it("uses plural entity set names for the connector's entityName", () => {
    expect(ENTITY_SETS.application).toBe("rev_applications");
    expect(ENTITY_SETS.systemUser).toBe("systemusers");
  });

  it("caps notes at the length the column declares in solution source", () => {
    const xml = readFileSync(
      join(
        REPO_ROOT,
        "src",
        "solutions",
        "RevitaliseGrantAutomation",
        "Entities",
        "rev_review",
        "Entity.xml",
      ),
      "utf8",
    );
    // Re-derived from source rather than restated: if the column is widened, this tells
    // us instead of silently truncating a trustee's notes.
    const notesChunk = xml
      .split("<attribute ")
      .find((chunk) => chunk.includes("<LogicalName>rev_notes1</LogicalName>"));
    expect(notesChunk).toBeDefined();
    const maxLength = /<MaxLength>(\d+)<\/MaxLength>/.exec(notesChunk ?? "")?.[1];
    expect(Number(maxLength)).toBe(VERDICT_NOTES_MAX_LENGTH);
  });
});
