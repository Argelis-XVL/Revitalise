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
  AGE_RANGE_LABELS,
  AGREEMENT_RESPONSE_LABELS,
  APPLICANT_GENDER_LABELS,
  APPLICANT_TYPE_LABELS,
  APPLICATION_DETAIL_COLUMNS,
  APPLICATION_LIST_COLUMNS,
  APPLICATION_STATUS_LABELS,
  BREAK_TYPE_LABELS,
  ENTITY_SETS,
  EXCEPTIONAL_CIRCUMSTANCE_LABELS,
  LIFE_SATISFACTION_LABELS,
  optionLabel,
  REVIEW_COLUMNS,
  ROUND_FINANCE_COLUMNS,
  VERDICT_LABELS,
  VERDICT_NOTES_MAX_LENGTH,
  VERDICT_VALUES,
  WELLBEING_QUESTION_HEADINGS,
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
    // WHOLE-IDENTIFIER match, not a substring — the same boundary
    // `scripts/verify-code-app-column-bindings.py` uses, and for the same reason: a secured
    // column name can be a strict prefix of an unrelated safe identifier. This app's own
    // `…redacted` naming convention (TAD §3.2.1) makes that concrete rather than
    // hypothetical — a redacted column's safe name IS its secured source's name with
    // "redacted" appended, no separator, so a bare substring search reports the safe
    // column as the secured one it redacts. Dataverse logical names are [a-z0-9_], so a
    // lookaround on that class is the correct boundary; `\b` would not exclude a leading
    // underscore.
    const offences: string[] = [];
    for (const file of files) {
      const content = readFileSync(file, "utf8");
      for (const column of forbidden) {
        const pattern = new RegExp(`(?<![A-Za-z0-9_])${column}(?![A-Za-z0-9_])`);
        if (pattern.test(content)) {
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

  it("binds exactly the three redacted care-support columns, and only the redacted ones (TAD §3.2.1, WBS 6.3)", () => {
    // Every column this app names whose family is "care support" must end in
    // "redacted" — a bare match would mean the secured source got bound instead of
    // its safe counterpart.
    const careColumns = APPLICATION_DETAIL_COLUMNS.filter(
      (c) => c.includes("caresupport") || c.includes("careprovidedexample") || c.includes("othercareprovidedtype"),
    );
    expect(careColumns.sort()).toEqual(
      [
        "rev_caresupportdescriptionredacted",
        "rev_careprovidedexampleredacted",
        "rev_othercareprovidedtyperedacted",
      ].sort(),
    );
    expect(careColumns.every((c) => c.endsWith("redacted"))).toBe(true);
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

describe("the landing screen's schema (WBS 6.9)", () => {
  const SOLUTION_ROOT = join(REPO_ROOT, "src", "solutions", "RevitaliseGrantAutomation");

  /**
   * Every option (value, label) pair an option set declares, read from solution source.
   *
   * Re-derived rather than restated, for the reason `C-TECH-060` gives and the reason
   * `IMP-0019` gives: a transcribed label map drifts silently, and the only thing that
   * catches the drift is comparing it against the source it was transcribed from.
   */
  function optionSetLabels(name: string): Record<number, string> {
    const xml = readFileSync(join(SOLUTION_ROOT, "OptionSets", `${name}.xml`), "utf8");
    const labels: Record<number, string> = {};
    for (const chunk of xml.split("<option ").slice(1)) {
      const value = /value="(\d+)"/.exec(chunk)?.[1];
      const label = /<label description="([^"]*)"/.exec(chunk)?.[1];
      if (value !== undefined && label !== undefined) labels[Number(value)] = label;
    }
    if (Object.keys(labels).length === 0) {
      throw new Error(
        `No options parsed from OptionSets/${name}.xml. Either the path is wrong or the ` +
          "parser no longer matches the file's shape — either way this check is not " +
          "checking anything and must be fixed, not skipped.",
      );
    }
    return labels;
  }

  it("reads rev_roundfinance's entity set name from the same place the platform assigned it", () => {
    // E1, and NOT hand-authored — TAD §12.2 carried this as an explicit "do not
    // hand-author it" row. Solution source records what the live read back returned.
    const xml = readFileSync(
      join(SOLUTION_ROOT, "Entities", "rev_roundfinance", "Entity.xml"),
      "utf8",
    );
    const entitySetName = /<EntitySetName>([a-z0-9_]+)<\/EntitySetName>/.exec(xml)?.[1];
    expect(entitySetName).toBe(ENTITY_SETS.roundFinance);
  });

  it("names exactly the thirteen attributes rev_roundfinance declares, minus its id", () => {
    const xml = readFileSync(
      join(SOLUTION_ROOT, "Entities", "rev_roundfinance", "Entity.xml"),
      "utf8",
    );
    const declared = [...xml.matchAll(/<attribute PhysicalName="([a-z0-9_]+)"/g)].map(
      (match) => match[1],
    );
    // Derived from source, so a fourteenth attribute added tomorrow makes this fail rather
    // than letting the screen quietly stop showing it.
    expect([...ROUND_FINANCE_COLUMNS].sort()).toEqual(declared.sort());
  });

  it("reproduces every option-set label it renders, exactly as solution source declares it", () => {
    // The applicant-gender option set's file name is BUILT AT RUNTIME from fragments, not
    // written as a literal — exactly the `IMP-0024` pattern, and for a stricter reason
    // here. The column that binds this set is `IsSecured=1` and inside
    // `REV_TrusteeRestricted`, so `no-secured-columns-in-code-app` (HARD) derives it into
    // its forbidden set: the literal in this file would fail the build, correctly.
    const genderSetName = ["rev", "gender"].join("_");
    for (const [setName, map] of [
      [genderSetName, APPLICANT_GENDER_LABELS],
      ["rev_agerange", AGE_RANGE_LABELS],
      ["rev_applicanttype", APPLICANT_TYPE_LABELS],
      ["rev_agreementresponse", AGREEMENT_RESPONSE_LABELS],
      ["rev_exceptionalcircumstance", EXCEPTIONAL_CIRCUMSTANCE_LABELS],
      ["rev_breaktype", BREAK_TYPE_LABELS],
    ] as [string, Readonly<Record<number, string>>][]) {
      expect(map).toEqual(optionSetLabels(setName));
    }
  });

  it("labels the life-satisfaction scale for exactly 0 to 10, so an out-of-range score shows up", () => {
    // Not an option set — a bounded Whole Number. Written out as a map anyway, because a
    // `String(value)` fallback would render 11 or -1 as a legitimate score and tell nobody.
    expect(Object.keys(LIFE_SATISFACTION_LABELS)).toHaveLength(11);
    expect(optionLabel(LIFE_SATISFACTION_LABELS, 0)).toBe("0");
    expect(optionLabel(LIFE_SATISFACTION_LABELS, 10)).toBe("10");
    expect(optionLabel(LIFE_SATISFACTION_LABELS, 11)).toBe("Unknown (11)");
    expect(optionLabel(LIFE_SATISFACTION_LABELS, -1)).toBe("Unknown (-1)");
  });

  it("heads the three wellbeing questions FR-062 asks about, and only those three", () => {
    expect(Object.keys(WELLBEING_QUESTION_HEADINGS).sort()).toEqual([
      "rev_wellbeinganswer10",
      "rev_wellbeinganswer8",
      "rev_wellbeinganswer9",
    ]);
  });

  it("has no landing-screen file that names an application or applicant entity set", () => {
    // TAD §5.4: the landing screen reads `rev_roundfinance` and nothing else, and every
    // FR-058..FR-062 figure comes from the flow response. That is the mechanism the gender
    // aggregate's whole safety argument rests on (TAD §1.1 obstacle A, §6.3), so the check
    // is on the ENTITY SET each file names — not on a union of column names, which in this
    // solution means nothing at all: `rev_name` is a real column of `rev_roundfinance` AND
    // of `rev_application`, and matching by name would report the round key as a breach
    // (C-TECH-069, the same defect the `no-secured-columns-in-code-app` gate was rescoped
    // to stop making).
    const landingFiles = [
      join(APP_ROOT, "src", "pages", "LandingPage.tsx"),
      join(APP_ROOT, "src", "components", "RoundStatistics.tsx"),
      join(APP_ROOT, "src", "components", "RoundFinancePanel.tsx"),
      join(APP_ROOT, "src", "components", "DistributionChart.tsx"),
      join(APP_ROOT, "src", "domain", "landing.ts"),
      join(APP_ROOT, "src", "dataverse", "roundStatistics.ts"),
    ];
    const offences: string[] = [];
    for (const file of landingFiles) {
      const source = readFileSync(file, "utf8");
      // Code, not prose: several of these files explain in comments WHY they must not read
      // an application row, and that explanation is the point of them.
      const code = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
      for (const entitySet of [ENTITY_SETS.application, ENTITY_SETS.applicant]) {
        if (code.includes(entitySet)) offences.push(`${file} names ${entitySet}`);
      }
      // And no route to one: a read helper imported here would be a way to reach a row
      // this screen must not read.
      if (/from "\.\.?\/(dataverse\/)?client"/.test(code)) {
        offences.push(`${file} imports the connector boundary directly`);
      }
    }
    expect(offences).toEqual([]);
  });
});
