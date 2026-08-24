/**
 * The print stylesheet — WBS 6.5, FR-039, TAD §8.
 *
 * TAD §8: "an export that leaks a column the screen hides would be a disclosure, not an
 * accessibility defect." The guarantee is structural — printing renders the same DOM
 * through the same repository call — and these assertions pin the two ways that
 * guarantee could be broken later:
 *
 *   1. a print rule that REVEALS something hidden on screen, and
 *   2. a second query or a print-only data path anywhere in the app.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const APP_ROOT = resolve(__dirname, "..", "..");
const PRINT_CSS = readFileSync(join(__dirname, "print.css"), "utf8");

function sourceFiles(directory: string, found: string[] = []): string[] {
  for (const entry of readdirSync(directory)) {
    const full = join(directory, entry);
    if (statSync(full).isDirectory()) {
      if (["generated", "node_modules", "dist", "coverage"].includes(entry)) continue;
      sourceFiles(full, found);
      continue;
    }
    if (entry.endsWith(".ts") || entry.endsWith(".tsx")) found.push(full);
  }
  return found;
}

describe("print.css", () => {
  it("scopes every rule to @media print", () => {
    // A rule outside the print block would change the screen, which is not what a print
    // stylesheet is for.
    const withoutComments = PRINT_CSS.replace(/\/\*[\s\S]*?\*\//g, "");
    const firstBrace = withoutComments.indexOf("{");
    expect(withoutComments.slice(0, firstBrace)).toContain("@media print");
  });

  it("hides interactive chrome and reveals nothing", () => {
    expect(PRINT_CSS).toContain('[data-print="hide"]');
    expect(PRINT_CSS).toMatch(/\[data-print="hide"\]\s*\{\s*display:\s*none/);
    // The dangerous direction: no rule may turn a hidden element back on.
    expect(PRINT_CSS).not.toMatch(/display:\s*(block|inline|flex|table|inline-block)\s*!important/);
    expect(PRINT_CSS).not.toMatch(/visibility:\s*visible/);
    expect(PRINT_CSS).not.toMatch(/content:\s*attr\(/);
  });

  it("keeps the heading hierarchy and the table header on every page", () => {
    // WCAG 1.3.1 / 1.3.2 in print: headings stay with their content and a multi-page
    // table still says which column is which.
    expect(PRINT_CSS).toMatch(/thead\s*\{\s*display:\s*table-header-group/);
    expect(PRINT_CSS).toMatch(/h1,\s*\n?\s*h2,\s*\n?\s*h3/);
  });

  it("prints the withheld-narrative state as prominently as it displays", () => {
    // A trustee working from paper must be able to see that a narrative was withheld
    // rather than missing by accident.
    expect(PRINT_CSS).toContain('[data-print="state"]');
  });

  it("keeps a sort header and a row's reference readable as text on paper", () => {
    expect(PRINT_CSS).toMatch(/th button/);
    expect(PRINT_CSS).toMatch(/td button/);
  });

  it("does not reorder content, so print order equals reading order", () => {
    expect(PRINT_CSS).not.toMatch(/\border:\s*-?\d/);
    expect(PRINT_CSS).not.toContain("flex-direction: column-reverse");
    expect(PRINT_CSS).not.toContain("direction: rtl");
  });
});

describe("there is no print-only data path", () => {
  const files = sourceFiles(join(APP_ROOT, "src"));

  it("found the source to scan", () => {
    expect(files.length).toBeGreaterThan(10);
  });

  it("uses the browser's own print, with no export or download route", () => {
    // An export built by hand is a second projection of the data, and a second chance to
    // include a column the screen hides. `window.print()` cannot widen the query.
    const offences: string[] = [];
    for (const file of files) {
      const content = readFileSync(file, "utf8");
      if (file.endsWith(".test.ts") || file.endsWith(".test.tsx")) continue;
      for (const pattern of [
        /createObjectURL/,
        /download\s*=/,
        /new Blob\(/,
        /toCSV|toCsv|buildCsv/,
        /XLSX|jspdf|pdfmake/i,
      ]) {
        if (pattern.test(content)) offences.push(`${file} matches ${String(pattern)}`);
      }
    }
    expect(offences).toEqual([]);
  });

  it("declares exactly one column allow-list per read, shared by screen and print", () => {
    // If a print path existed it would need its own allow-list. There is only one place
    // per read function where `select` is built from the caller's request, and schema.ts
    // is the only place columns are named. (Was literal `$select:` when reads went through
    // the generic connector's raw OData parameters; the typed per-table services take a
    // plain `select` array and build `$select=` internally — IMP-0208/IMP-0209/IMP-0224.)
    const clientSource = readFileSync(join(APP_ROOT, "src", "dataverse", "client.ts"), "utf8");
    // Two: one in listRecords, one in getRecord. A third would be a new read path.
    expect(clientSource.match(/select: \[\.\.\.request\.select\]/g)?.length).toBe(2);
  });
});
