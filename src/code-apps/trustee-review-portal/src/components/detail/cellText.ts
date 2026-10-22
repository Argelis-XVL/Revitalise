/**
 * The text of a NON-protected cell, for the displays that show a plain value (tiles, chips, the
 * cost receipt, the answer pills). `displayOf()` routes every `redacted` cell to `AnswerCards` and
 * every `restricted` cell to `RestrictedList` before any of those displays is chosen, so the two
 * protected branches here are unreachable by construction. They still return the protected
 * wording rather than an empty string, so a future routing mistake shows the restricted or
 * withheld words — never a blank, and never a value (TAD R-D2-5).
 */
import type { DetailCell } from "../../domain/applicationDetailLayout";
import { RESTRICTED_VALUE_TEXT } from "../../domain/fieldCatalogue";
import { WITHHELD_HEADING } from "../../domain/visibility";

export function plainText(cell: DetailCell): string {
  switch (cell.kind) {
    case "value":
    case "long-text":
      return cell.text;
    case "restricted":
      return RESTRICTED_VALUE_TEXT;
    case "redacted":
      return cell.state.kind === "released" ? cell.state.text : WITHHELD_HEADING;
  }
}
