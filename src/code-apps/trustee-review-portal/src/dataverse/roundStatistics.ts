/**
 * `REV | Portal | Round Statistics` — the invocation, and the parse.
 *
 * Everything FR-058..FR-062 shows comes through here and through nothing else. Two halves,
 * deliberately separated because they have very different evidence behind them:
 *
 *   `parseRoundStatisticsResponse` — a pure function over a JSON string. Fully specified
 *                                   by TAD §3.3, fully unit-tested, no platform contract.
 *   `fetchRoundStatistics`        — the read-then-maybe-trigger cycle. Rewritten
 *                                   2026-08-28 for ADR-038 — see below.
 *
 * ## Why this is two rows and not a flow call (IMP-0359, IMP-0365, ADR-038)
 *
 * The flow used to be invoked directly (a PowerApps trigger, `shared_logicflows`,
 * synchronous request/response). That connector reproducibly crashed this Code App's boot —
 * "The app didn't start correctly" — on two independent, private-session-verified attempts,
 * with no fix found in this app's own source and no equivalent failure documented anywhere
 * in Microsoft's own code-apps samples or docs. **The app's only connector is Dataverse and
 * must stay that way**: adding a new connector TYPE is the operation that killed ADR-030;
 * adding a TABLE on the connector already there was performed on this app without incident.
 *
 * The flow's trigger is a Dataverse row-trigger on `rev_roundstatisticsrequest` — a single,
 * ever-present row (`provisioning/dataverse/seed-round-statistics-request.ps1`, key
 * `CURRENT`) neither this app nor the flow's own security role has a create privilege on, by
 * design.
 *
 * ## Revision 5 — the ask and the answer are on two DIFFERENT tables (ADR-038, TAD §3.9)
 *
 * The single-table shape this replaces carried both. That left `REV Trustee` holding Global
 * Write on the one row every trustee's figures come from, with `IsAuditEnabled=0` on the
 * document itself — so **the one overwrite that mattered left no audit trail at all**
 * (§3.9.1). Column-level write control cannot fix it: securing the column would either
 * require a trustee in a field-security profile (which `no-trustee-in-column-security-profile`
 * forbids and ADR-002 exists to prevent) or fail `no-secured-columns-in-code-app`. A table
 * boundary was the only remaining control, and it is the least bypassable one in this model.
 *
 * So, in this file:
 *
 *   - the app **WRITES** `rev_triggeredon` on `rev_roundstatisticsrequest` — through the
 *     exact same generic-connector `UpdateOnlyRecordWithOrganization` path `client.ts`'s
 *     `updateRecord` already proves solid for Save Verdict, never `shared_logicflows`, and
 *     never the typed path (TAD §5.4's Revision 5 note: the two paths live under different
 *     keys and one can work while the other is broken);
 *   - the app **READS** the answer from `rev_roundstatisticsresult` — a table it holds Read
 *     and no Write on — through the `"Dataverse"`-type per-table path every other screen
 *     uses, which is structurally immune to the org-url-null defect that write path once had
 *     (see `client.ts`'s header for the full comparison).
 *
 * TAD §3.3's response contract is **byte-for-byte the same document**; only its transport
 * moved, and one top-level field was added to it (`staleAfterSeconds`).
 *
 * ## And "fresh" is now an AGE, not "newer than the write I just made"
 *
 * The draft this replaces asked *"did MY request's cycle finish?"* — request identity, with
 * an `isFresh` flag threaded through a return type to stop a null `computedOn` reading as
 * current. `isCurrent` below asks *"is the document younger than its own
 * `staleAfterSeconds`?"* instead. One expression, no flag, no request id anywhere in the
 * mechanism — which is how TAD §6.3.1 answers the cross-request-contamination question by
 * design rather than by assurance. A mount inside the freshness window writes nothing and
 * triggers nothing; a poll is satisfied by a computation ANOTHER trustee's click started.
 *
 * If nothing current arrives by the last poll, the screen is told plainly rather than shown
 * stale figures: `status: "pending"`, routed through the same `parseRoundStatisticsResponse`
 * every other response goes through, so it needs no bespoke object shape.
 */
import { listRecords, updateRecord } from "./client";
import { asNumber, asString } from "./odata";
import {
  ENTITY_SETS,
  ROUND_STATISTICS_REQUEST_COLUMNS,
  ROUND_STATISTICS_RESULT_COLUMNS,
} from "./schema";
import type {
  ApplicationsPerDay,
  ApplicationsReceived,
  BreakTypeProfile,
  BreakTypeRow,
  BreakTypeTotal,
  CategoryCount,
  Distribution,
  ExceptionalFundingSummary,
  KnownRoundStatisticsStatus,
  MoneyMeasure,
  ProportionMetric,
  RoundStatisticsMetrics,
  RoundStatisticsResponse,
  WellbeingLastYear,
  WellbeingQuestion,
} from "./types";
import { KNOWN_ROUND_STATISTICS_STATUSES } from "./types";

/**
 * A failure of the statistics call or of its response, shaped for display.
 *
 * Distinct from `DataverseError` on purpose: that names a connector read, this names the
 * round-statistics request/response cycle, and a trustee reading "could not load records"
 * about a request row would be told the wrong thing about the wrong system.
 */
export class RoundStatisticsError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RoundStatisticsError";
  }
}

/** True for one of the five statuses TAD §3.3 names. */
export function isKnownStatus(status: string): status is KnownRoundStatisticsStatus {
  return (KNOWN_ROUND_STATISTICS_STATUSES as readonly string[]).includes(status);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * One category. Both `value` and `count` are required — a category with no option-set
 * value cannot be labelled and a category with no count is not a count — so a malformed
 * entry is DROPPED rather than rendered as a zero.
 */
function parseCategory(raw: unknown): CategoryCount | null {
  if (!isRecord(raw)) return null;
  const value = asNumber(raw.value);
  const count = asNumber(raw.count);
  if (value === null || count === null) return null;
  return { value, count, percentage: asNumber(raw.percentage) };
}

function parseCategories(raw: unknown): CategoryCount[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map(parseCategory)
    .filter((category): category is CategoryCount => category !== null);
}

/**
 * A distribution, or `null` for an absence.
 *
 * `null` is returned for an absent metric AND for one that arrives with no usable
 * category — including TAD §3.3's own `"categories": [ ]`. Both mean there is nothing to
 * show, and the screen renders no section at all for a null (TAD §3.3 point 3). The
 * alternative — a heading over an empty table — reads as "we counted and found none",
 * which for a metric that was never computed is false.
 */
function parseDistribution(raw: unknown): Distribution | null {
  if (!isRecord(raw)) return null;
  const categories = parseCategories(raw.categories);
  if (categories.length === 0) return null;
  return { population: asNumber(raw.population), categories };
}

function parseApplicationsReceived(raw: unknown): ApplicationsReceived | null {
  if (!isRecord(raw)) return null;
  const count = asNumber(raw.count);
  if (count === null) return null;
  return { count };
}

function parseApplicationsPerDay(raw: unknown): ApplicationsPerDay | null {
  if (!isRecord(raw)) return null;
  const value = asNumber(raw.value);
  if (value === null) return null;
  return { value, openedOn: asString(raw.openedOn), days: asNumber(raw.days) };
}

/**
 * One of the four ADR-039 money measures — `{ value, population }` — or `null` for an absence.
 *
 * **A bare number is REJECTED, not coerced.** Before Revision 6 every one of these four fields
 * was a plain `number | null`, and a flow still on that shape would hand this parser a bare
 * `1500` rather than an object. Accepting it as `{ value: 1500, population: null }` would put a
 * mean on screen with no denominator beside it — exactly what TAD §3.3 property 8 exists to
 * prevent, and a materially worse failure than showing nothing, because it looks correct. A
 * shape mismatch is therefore treated the same way a malformed category already is: dropped
 * rather than guessed at.
 *
 * **A `population` that fails to parse drops the whole measure, not just the field.** `value`
 * without a real denominator on the page is not auditable, so this mirrors `parseCategory`'s own
 * rule (`value`/`count` both required or the whole entry is discarded) rather than defaulting
 * the population to `null` and rendering a bare figure. See `MoneyMeasure`'s own doc in
 * `types.ts` for why the TYPE still allows `population: number | null` even though this parser
 * never actually returns one that way.
 */
function parseMoneyMeasure(raw: unknown): MoneyMeasure | null {
  if (!isRecord(raw)) return null;
  const value = asNumber(raw.value);
  const population = asNumber(raw.population);
  if (value === null || population === null) return null;
  return { value, population };
}

function parseExceptionalFundingSummary(raw: unknown): ExceptionalFundingSummary | null {
  if (!isRecord(raw)) return null;
  const anyCount = asNumber(raw.anyCount);
  if (anyCount === null) return null;
  return {
    population: asNumber(raw.population),
    anyCount,
    anyPercentage: asNumber(raw.anyPercentage),
    // ADR-039 (Revision 6) — below k (TAD §6.3.5) the flow omits this field or sends it
    // `null`, and `parseMoneyMeasure` treats a bare number the SAME way (§3.3 property 8):
    // dropped rather than rendered as a figure with no denominator.
    averageAmountRequested: parseMoneyMeasure(raw.averageAmountRequested),
  };
}

function parseBreakTypeRow(raw: unknown): BreakTypeRow | null {
  if (!isRecord(raw)) return null;
  const value = asNumber(raw.value);
  const count = asNumber(raw.count);
  if (value === null || count === null) return null;
  return {
    value,
    count,
    // ADR-039 (Revision 6). A break type below k costed applications arrives as
    // `count` present and all three of these `null` — TAD §3.3's own example row — and that
    // is intended, not an error (§6.3.5).
    averageCost: parseMoneyMeasure(raw.averageCost),
    averageAmountRequested: parseMoneyMeasure(raw.averageAmountRequested),
    percentageOfCost: parseMoneyMeasure(raw.percentageOfCost),
  };
}

/**
 * FR-060's total row, or `null`.
 *
 * A-LAND-4 (GUESS, E3) — TAD §3.3 shows `"total": { }`, an empty object naming no field,
 * so the populated shape is inferred to mirror a data row minus its category. A total in
 * which every field is absent is returned as `null`: a total row of four blanks tells a
 * trustee nothing and looks like a rendering fault.
 */
function parseBreakTypeTotal(raw: unknown): BreakTypeTotal | null {
  if (!isRecord(raw)) return null;
  const total: BreakTypeTotal = {
    count: asNumber(raw.count),
    // ADR-039 (Revision 6) — same `{ value, population }` shape and the same k-gate as the
    // per-row measures above; TAD §3.3's example shows the total row's three money measures
    // gated on k exactly like a data row's (§6.3.5).
    averageCost: parseMoneyMeasure(raw.averageCost),
    averageAmountRequested: parseMoneyMeasure(raw.averageAmountRequested),
    percentageOfCost: parseMoneyMeasure(raw.percentageOfCost),
  };
  const hasAnything = Object.values(total).some((field) => field !== null);
  return hasAnything ? total : null;
}

function parseBreakTypeProfile(raw: unknown): BreakTypeProfile | null {
  if (!isRecord(raw)) return null;
  const rows = Array.isArray(raw.rows)
    ? raw.rows.map(parseBreakTypeRow).filter((row): row is BreakTypeRow => row !== null)
    : [];
  if (rows.length === 0) return null;
  return {
    population: asNumber(raw.population),
    rows,
    total: parseBreakTypeTotal(raw.total),
  };
}

function parseWellbeingQuestion(raw: unknown): WellbeingQuestion | null {
  if (!isRecord(raw)) return null;
  const column = asString(raw.column);
  if (column === null) return null;
  const categories = parseCategories(raw.categories);
  if (categories.length === 0) return null;
  return { column, population: asNumber(raw.population), categories };
}

function parseWellbeingLastYear(raw: unknown): WellbeingLastYear | null {
  if (!isRecord(raw) || !Array.isArray(raw.questions)) return null;
  const questions = raw.questions
    .map(parseWellbeingQuestion)
    .filter((question): question is WellbeingQuestion => question !== null);
  if (questions.length === 0) return null;
  return { questions };
}

/**
 * One of FR-062's three headline proportions, or `null`. See A-LAND-3 on `types.ts`.
 *
 * Requires either the percentage or both halves of the fraction. A proportion with
 * neither is not a proportion, and all three are `null` today anyway (OQ-039).
 */
function parseProportion(raw: unknown): ProportionMetric | null {
  if (!isRecord(raw)) return null;
  const percentage = asNumber(raw.percentage);
  const count = asNumber(raw.count);
  const population = asNumber(raw.population);
  if (percentage === null && (count === null || population === null)) return null;
  return { population, count, percentage };
}

function parseMetrics(raw: unknown): RoundStatisticsMetrics {
  const bag = isRecord(raw) ? raw : {};
  return {
    applicationsReceived: parseApplicationsReceived(bag.applicationsReceived),
    applicationsPerDay: parseApplicationsPerDay(bag.applicationsPerDay),
    exceptionalCircumstanceMix: parseDistribution(bag.exceptionalCircumstanceMix),
    exceptionalFundingSummary: parseExceptionalFundingSummary(bag.exceptionalFundingSummary),
    breakTypeProfile: parseBreakTypeProfile(bag.breakTypeProfile),
    genderDistribution: parseDistribution(bag.genderDistribution),
    ageRangeDistribution: parseDistribution(bag.ageRangeDistribution),
    applicantTypeDistribution: parseDistribution(bag.applicantTypeDistribution),
    // Parsed like its three siblings above as of TAD §0.11 (Revision 8, 2026-08-31). This
    // line used to hard-code `null` and discard whatever the response carried, on the claim
    // that FR-061's ethnicity half had no data source; that claim is false and the reviewer
    // risk-accepted rendering the distribution, DEV-scoped, with promotion to TST/ACC/PRD
    // still gated on OQ-030 (EX-005). A response that does not carry the key still yields
    // `null` here, through the same shared contract as every other distribution.
    ethnicGroupDistribution: parseDistribution(bag.ethnicGroupDistribution),
    wellbeingLastYear: parseWellbeingLastYear(bag.wellbeingLastYear),
    lifeSatisfactionDistribution: parseDistribution(bag.lifeSatisfactionDistribution),
    highHoursCareProportion: parseProportion(bag.highHoursCareProportion),
    lowLifeSatisfactionProportion: parseProportion(bag.lowLifeSatisfactionProportion),
    unableToTakeBreakProportion: parseProportion(bag.unableToTakeBreakProportion),
  };
}

/**
 * Parses and validates the response document — TAD §3.3.
 *
 * `status` is the only required field, and it is required absolutely: it is the flow's own
 * verdict on whether its figures are safe to show, and a response without one cannot be
 * rendered either way round. Everything else degrades to `null`, because a null is an
 * absence the screen knows how to render and a fabricated zero is a finding.
 *
 * Also the vehicle for the synthetic `{"status":"pending"}` document `fetchRoundStatistics`
 * builds below when no fresh cycle has finished yet — deliberately routed through this same
 * function rather than a hand-built `RoundStatisticsResponse` object, so "pending" gets the
 * identical null-metrics shape every other non-`ok` status already gets, for free.
 */
export function parseRoundStatisticsResponse(text: string): RoundStatisticsResponse {
  let document: unknown;
  try {
    document = JSON.parse(text);
  } catch {
    throw new RoundStatisticsError(
      "The round-statistics flow returned a response this screen could not read as JSON.",
    );
  }

  if (!isRecord(document)) {
    throw new RoundStatisticsError(
      "The round-statistics flow returned a JSON value that is not a document.",
    );
  }

  const status = asString(document.status);
  if (status === null) {
    throw new RoundStatisticsError(
      "The round-statistics flow returned a document with no status, so this screen " +
        "cannot tell whether its figures are safe to show. No figures are shown.",
    );
  }

  return {
    status,
    roundKey: asString(document.roundKey),
    computedOn: asString(document.computedOn),
    // ADR-038. `null` here does NOT mean "absent, render nothing" — it means ALWAYS
    // RECOMPUTE, which is the fail-safe direction and the shipping default (no
    // `RoundStatisticsStaleAfterSeconds` row exists; OQ-042). Nothing in this file supplies
    // a fallback number, and nothing may: treating an unbounded age as fresh would put a
    // figure of unknown age in front of a board. See `types.ts` on this field.
    staleAfterSeconds: asNumber(document.staleAfterSeconds),
    populationReceived: asNumber(document.populationReceived),
    metrics: parseMetrics(document.metrics),
  };
}

/**
 * rev_name of the one row each of these two tables will ever hold (Entity.xml, seed
 * scripts). The same key on both, by design — TAD §3.9.3 copies the result table's shape,
 * including its alternate key, from the request table.
 */
const ROW_KEY = "CURRENT";

/**
 * The synthetic document raised when the poll bound is reached — TAD §5.3.1 step 4.
 *
 * Routed through `parseRoundStatisticsResponse` rather than hand-built as a
 * `RoundStatisticsResponse` object, deliberately: `pending` then inherits the identical
 * null-metrics, null-`staleAfterSeconds`, null-`roundKey` shape every other non-`ok` status
 * already gets, for free, and it can never drift from the contract as the contract grows.
 * Adding `staleAfterSeconds` in Revision 5 needed no edit here, which is the property.
 */
const PENDING_DOCUMENT = JSON.stringify({ status: "pending" });

/** Milliseconds between polls, and the number of polls, after writing the trigger. */
const POLL_INTERVAL_MS = 2000;
const MAX_POLLS = 6;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * One read of `rev_roundstatisticsresult`: the stamp, and the document that stamp belongs to.
 *
 * `document` is `null` for a row that carries no `rev_resultjson`, or one whose JSON is not
 * a §3.3 document. That is not an error here and must not be: TAD §3.3's closing paragraph
 * says that on a first-ever mount, or after a failed computation, *"there is no parseable
 * document and therefore no bound, and the app treats the result as stale."* The parse
 * failure is swallowed at THIS layer for exactly that reason, and `RoundStatisticsError`
 * still reaches the screen for the one case that is genuinely a person's problem — a result
 * row that does not exist.
 *
 * There is no request id and no "did MY cycle finish" flag on this type, and there is not
 * meant to be: TAD §6.3.1 row 3 answers the cross-request-contamination question with the
 * ABSENCE of a request identity in the mechanism rather than with an assurance about one, so
 * the absence is the design and not an omission.
 */
interface ResultRead {
  /** `rev_computedon` — the flow's own "I finished at". The only input to freshness. */
  computedOn: string | null;
  /** `rev_resultjson` parsed, or `null` when there is nothing parseable on the row. */
  document: RoundStatisticsResponse | null;
}

/**
 * Reads the single result row by its fixed key — the same "filter, don't hardcode a GUID"
 * pattern `repository.ts`'s `getOpenRound()` uses for `rev_roundfinance`.
 *
 * A missing row is a provisioning gap (the seed script has not run in this environment) and
 * is reported as a `RoundStatisticsError` a person can act on, naming the script. It is NOT
 * folded into `pending`: "the service is still working" and "nobody has provisioned the row
 * the service writes to" are different facts, and one of them is fixed by waiting.
 */
async function readResultRow(): Promise<ResultRead> {
  const { rows } = await listRecords({
    entityName: ENTITY_SETS.roundStatisticsResult,
    select: ROUND_STATISTICS_RESULT_COLUMNS,
    filter: `rev_name eq '${ROW_KEY}'`,
    top: 1,
  });
  const row = rows[0];
  if (row === undefined) {
    throw new RoundStatisticsError(
      "No round-statistics result row exists yet. Run " +
        "provisioning/dataverse/seed-round-statistics-result.ps1 against this environment.",
    );
  }
  const resultJson = asString(row.rev_resultjson);
  let document: RoundStatisticsResponse | null = null;
  if (resultJson !== null) {
    try {
      document = parseRoundStatisticsResponse(resultJson);
    } catch {
      // Deliberately swallowed — see `ResultRead`. An unparseable document has no bound, so
      // it can never be current, so it is stale and the cycle below asks for a new one.
      document = null;
    }
  }
  return { computedOn: asString(row.rev_computedon), document };
}

/**
 * The document's age in seconds, or **`NaN`** when there is no timestamp to age.
 *
 * `NaN` rather than `null` is the whole trick, and it is what makes `isCurrent` below a
 * single expression: every comparison against `NaN` is `false`, so "no stamp" and "too old"
 * are rejected by the same operator rather than by a guard in front of it.
 */
function ageInSeconds(computedOn: string | null, now: number): number {
  return computedOn === null ? Number.NaN : (now - Date.parse(computedOn)) / 1000;
}

/**
 * **Is the document on the row young enough to render?** TAD §5.3.1, ADR-038 — and this one
 * expression is the whole of the freshness rule.
 *
 * ## Why it is an age and not an identity
 *
 * The design this replaces asked *"is there a result newer than the write **I** just
 * made?"* — request identity. This asks *"is there a result younger than
 * `staleAfterSeconds`?"* — an age bound. Three consequences, all deliberate:
 *
 *   - **A poll is satisfied by whoever caused the computation** (§5.3.1 step 3). A
 *     computation another trustee's click started, finishing inside the window, satisfies
 *     this. Twelve trustees opening the board screen in the same minute therefore cause ONE
 *     traverse of the Art. 9 columns rather than twelve — a privacy improvement as much as a
 *     load one (§6.4).
 *   - **There is no per-request state anywhere for a request to contaminate**, which is how
 *     §6.3.1 answers the cross-request question by design rather than by assurance.
 *   - **It cannot express the null-check bug the previous draft had.** That draft tested
 *     `computedOn !== null` alone and would have shown a stale document as current the
 *     moment a poll timed out over an older non-null timestamp; it needed an explicit
 *     `isFresh` flag threaded through a return type to be safe. Here `null` fails the test
 *     and an old timestamp fails the test **in the same comparison** — so the bug has no
 *     shape to take, and there is no flag to forget to check.
 *
 * ## Every fail-safe collapses into one operator
 *
 * `<=` is `false` if either side is `NaN`, and every "we cannot tell" arrives as a `NaN`:
 *
 *   - `computedOn` null (never computed) → `NaN` age → **stale**;
 *   - `computedOn` unparseable → `Date.parse` → `NaN` age → **stale**;
 *   - no parseable document (first-ever mount, failed computation) → no bound → `NaN`
 *     → **stale** (TAD §3.3's closing paragraph);
 *   - `staleAfterSeconds` null (the shipping default — the `rev_setting` row is unseeded,
 *     OQ-042) → `NaN` bound → **stale**, i.e. recompute on every mount, which is Revision
 *     2's behaviour exactly and the fail-safe direction (§3.3 property 7).
 *
 * There is no fallback bound anywhere in this file. An unbounded age treated as fresh would
 * put a figure of unknown age in front of a board.
 */
function isCurrent(
  read: ResultRead,
  now: number,
): read is ResultRead & { document: RoundStatisticsResponse } {
  return ageInSeconds(read.computedOn, now) <= (read.document?.staleAfterSeconds ?? Number.NaN);
}

/**
 * Writes `rev_triggeredon` on the single `rev_roundstatisticsrequest` row — TAD §5.3.1
 * step 2. The ask, and nothing else.
 *
 * ## Two properties of this write that are not free to change
 *
 * **1. It goes through the GENERIC-connector `updateRecord` path**
 * (`UpdateOnlyRecordWithOrganization`), which is the path already proven solid live for Save
 * Verdict — never the typed per-table service. TAD §5.4's Revision 5 note is explicit that
 * the two paths live under different keys in `dataSourcesInfo.ts`, that one can work while
 * the other is broken, and that a fix to either is evidence only about the key the call site
 * actually uses. Moving this write to the typed path would discard the only live evidence
 * this app has about it.
 *
 * **2. The value written is read by NOBODY** — not the flow, not this app. TAD §6.3.1 row 2
 * makes that a checkable property (the column name must not appear in the flow definition at
 * all), and `ROUND_STATISTICS_REQUEST_COLUMNS` no longer selects it. It exists only as a
 * change for the row trigger to fire on, so the timestamp's value carries no meaning and
 * nothing downstream compares against it. That is precisely why it is generated here and
 * thrown away rather than returned.
 *
 * The row is resolved by its fixed alternate key, and its id is the only column this app
 * still reads from the request table.
 */
async function requestRecomputation(): Promise<void> {
  const { rows } = await listRecords({
    entityName: ENTITY_SETS.roundStatisticsRequest,
    select: ROUND_STATISTICS_REQUEST_COLUMNS,
    filter: `rev_name eq '${ROW_KEY}'`,
    top: 1,
  });
  const row = rows[0];
  if (row === undefined) {
    throw new RoundStatisticsError(
      "No round-statistics request row exists yet. Run " +
        "provisioning/dataverse/seed-round-statistics-request.ps1 against this environment.",
    );
  }
  const id = asString(row.rev_roundstatisticsrequestid);
  if (id === null) {
    throw new RoundStatisticsError("The round-statistics request row has no id.");
  }
  await updateRecord({
    entityName: ENTITY_SETS.roundStatisticsRequest,
    recordId: id,
    item: { rev_triggeredon: new Date().toISOString() },
  });
}

/**
 * The round statistics — TAD §5.4 step 2 as superseded by §5.3.1, ADR-038.
 *
 * No arguments, and under Revision 5 that is a property of the design rather than a promise
 * about it: the flow is row-triggered and reads nothing from its trigger body (§1.5 point 4).
 *
 * Four steps, in this order, and step 1 is the one that is new:
 *
 *   1. **Read the result row.** If the document on it is younger than its own
 *      `staleAfterSeconds`, return it. **Write nothing. Trigger nothing.** No flow run, no
 *      privileged read, no traverse of the Art. 9 columns — a mount inside the freshness
 *      window is one row read, the cheapest this screen has been in any revision.
 *   2. **Otherwise ask.** Write `rev_triggeredon` on the request row.
 *   3. **Poll the result row** up to `MAX_POLLS × POLL_INTERVAL_MS` (12s at today's
 *      settings) and accept the FIRST read that is current — **whoever caused it.**
 *   4. **Timeout → `pending`.** Never the stale document presented as current.
 *
 * `now` is re-read per comparison rather than captured once, and that is correct here where
 * the previous design's captured timestamp was correct there: an age bound is a question
 * about the present moment, and a `now` captured before a 12-second poll would judge the
 * last poll's document against the first poll's clock.
 *
 * **What this cannot tell apart, stated rather than discovered** (A-R47): a trigger that was
 * never registered, a computation slower than the poll bound, and a flow writing a document
 * this app cannot parse all reach the screen as `pending`. None of the three is fixable in
 * this app — TAD §12.3 step 7's observed-effect assertion is where the first is caught, and
 * §12.2's live key-set assertion is where the third is. This function must not grow a
 * heuristic that guesses between them, and in particular must not branch on the result row's
 * `rev_status`: an Error recorded by some earlier computation is not evidence about the one
 * now in flight, and reading it that way is request identity through the back door.
 */
export async function fetchRoundStatistics(): Promise<RoundStatisticsResponse> {
  // Step 1 — TAD §5.3.1. The document is returned as parsed, including a non-`ok` status:
  // the flow's own verdict is the document's job to carry (§3.3 point 4) and the screen's to
  // render, so nothing here throws for one.
  const onMount = await readResultRow();
  if (isCurrent(onMount, Date.now())) return onMount.document;

  // Step 2.
  await requestRecomputation();

  // Step 3.
  for (let attempt = 0; attempt < MAX_POLLS; attempt++) {
    await sleep(POLL_INTERVAL_MS);
    const polled = await readResultRow();
    if (isCurrent(polled, Date.now())) return polled.document;
  }

  // Step 4.
  return parseRoundStatisticsResponse(PENDING_DOCUMENT);
}
