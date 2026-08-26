/**
 * `REV | Portal | Round Statistics` — the invocation, and the parse.
 *
 * Everything FR-058..FR-062 shows comes through here and through nothing else. Two halves,
 * deliberately separated because they have very different evidence behind them:
 *
 *   `parseRoundStatisticsResponse` — a pure function over a JSON string. Fully specified
 *                                   by TAD §3.3, fully unit-tested, no platform contract.
 *   `fetchRoundStatistics`        — the invocation. A hand-authored guess at a generated
 *                                   shape that does not exist yet. A-LAND-2.
 *
 * ## Why the landing screen must not compute any of this itself
 *
 * Stated here because this file is where somebody would be tempted. The app can already
 * read `rev_application` and `rev_applicant`, so several of these figures LOOK computable
 * in the browser. They are not, and TAD §1.1 is the argument:
 *
 *   - The gender distribution is impossible client-side. That column is `IsSecured=1` and
 *     inside `REV_TrusteeRestricted`, so a trustee reads null for every row and a browser
 *     tally returns nothing (obstacle A).
 *   - FR-058's received population is WIDER than FR-038 lets a trustee see. The platform
 *     would permit the read — `prvReadrev_application` is Global — which makes computing
 *     it client-side worse, not better: it means putting out-of-remit application rows on
 *     the wire to a trustee's device to be counted and discarded (obstacle B).
 *   - A mixed model is the real trap. FR-060 and FR-062 genuinely could be computed here
 *     from columns the trustee may see, and the result would be a screen whose tiles have
 *     different denominators and nothing to reconcile them: FR-058 counting the received
 *     population beside a break-type table counting the eligible-and-released one. Both
 *     numbers correct, the screen lying. That is the
 *     `hand-maintained-count-drifts-from-source` class this project has recorded eight
 *     times (TAD §1.2).
 *
 * So: one call, one population, one instant. The landing screen reads no application or
 * applicant row at all, and `src/pages/LandingPage.tsx` has no path that could.
 *
 * ## A-LAND-2 (GUESS, E2) — the invocation shape
 *
 * `pa app add flow --flow-id <id>` has never been run against this app. `power.config.json`
 * declares one connection reference and four table data sources, and no flow; there is no
 * `RoundStatisticsService.ts` under `src/generated/services/`. The flow itself is not live
 * in any environment either, so there is nothing for the verb to read a definition from —
 * TAD §9 makes the flow a BUILD-TIME dependency of the app for exactly this reason.
 *
 * What is being guessed, precisely:
 *
 *   1. **That the generated service exposes a static no-argument `Run()`** returning an
 *      `IOperationResult`-shaped result. TAD §1.2 and §2 both describe it that way from
 *      Microsoft's own documentation (E2), and every generated per-table service in
 *      `src/generated/services/` returns `IOperationResult<T>` (E1 for that half).
 *   2. **The property name the response text arrives under.** The flow responds with one
 *      `Text` output carrying one JSON document (TAD §3.3), so `Run()`'s payload is an
 *      object with one string property whose NAME is chosen in the flow designer and is
 *      not knowable from here. `extractResponseText` below accepts the payload as a bare
 *      string or under any single string property rather than betting on one name.
 *
 * Cheapest verification, once the flow exists in DEV:
 *
 *     pa app list-flows
 *     pa app add flow --flow-id <id>
 *
 * then replace `missingFlowService` as this file's default with the generated service,
 * reconcile `extractResponseText` against the generated model's actual output property,
 * and delete whichever branch turned out to be unnecessary. `power.config.json` is
 * rewritten by that verb, which is where this app's binding has broken before (A-R34), so
 * read `logs/known-failure-modes.md` before running it.
 *
 * Until then the default service REJECTS rather than returning anything, and the landing
 * screen renders "round figures are unavailable" — the same diagnostic it must already
 * render for a flow that is off, unshared or DLP-blocked. Nothing is faked and no figure
 * is invented; the screen is honest about having none.
 */
import { asNumber, asString } from "./odata";
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
 * Distinct from `DataverseError` on purpose: that names a connector read, this names a
 * flow invocation, and a trustee reading "could not load records" about a missing flow
 * would be told the wrong thing about the wrong system.
 */
export class RoundStatisticsError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RoundStatisticsError";
  }
}

/**
 * The one method this app calls on the generated flow service.
 *
 * Declared here rather than imported, because the file it would be imported from does not
 * exist yet. When it does, the generated class satisfies this structurally and this
 * interface can go.
 */
export interface RoundStatisticsFlowService {
  /**
   * Typed as `unknown` rather than as `IOperationResult<T>` deliberately: the generated
   * result shape is the half of A-LAND-2 that is genuinely unknown, and declaring it here
   * would put a guess in the type system where `extractResponseText` can no longer be
   * honest about it. That function accepts the `IOperationResult` envelope and the bare
   * payload, and fails loudly for anything else.
   */
  Run(): Promise<unknown>;
}

/**
 * The default, and the honest one until `pa app add flow` has run — see A-LAND-2 above.
 *
 * Rejects with a message written for the person who will read it in DEV, not for a
 * trustee: the screen replaces it with its own wording (`src/domain/landing.ts`), so the
 * detail here costs a trustee nothing and saves whoever is wiring the flow up a search.
 */
export const missingFlowService: RoundStatisticsFlowService = {
  Run(): Promise<never> {
    return Promise.reject(
      new RoundStatisticsError(
        "The round-statistics flow is not bound to this app. `pa app add flow --flow-id " +
          "<id>` has not been run, so there is no generated service to call — see " +
          "src/dataverse/roundStatistics.ts (A-LAND-2). The flow must exist and be on in " +
          "the environment first; TAD §9 makes it a build-time dependency of the app.",
      ),
    );
  },
};

/** True for one of the five statuses TAD §3.3 names. */
export function isKnownStatus(status: string): status is KnownRoundStatisticsStatus {
  return (KNOWN_ROUND_STATISTICS_STATUSES as readonly string[]).includes(status);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Pulls the JSON document out of whatever `Run()` resolved with.
 *
 * Three accepted shapes, in order, and a named failure for anything else:
 *
 *   1. a bare string — the document itself;
 *   2. `{ success, data }` — unwrapped, then re-examined (so an `IOperationResult`
 *      wrapping either of the other two shapes works);
 *   3. an object with exactly one own property holding a non-empty string — the `Respond
 *      to a Power App or flow` output, under whatever name the flow gave it.
 *
 * Shape 3 is why this accepts "exactly one" rather than searching a list of likely names.
 * A guess at the name would be silently wrong for any other name; a guess at the COUNT is
 * a property of the design — TAD §3.3 chose one text output carrying one JSON document
 * precisely so there is nothing else in there — and it fails loudly the day that stops
 * being true.
 */
export function extractResponseText(payload: unknown): string {
  if (typeof payload === "string") {
    if (payload.trim().length === 0) {
      throw new RoundStatisticsError(
        "The round-statistics flow returned an empty response body.",
      );
    }
    return payload;
  }

  if (isRecord(payload)) {
    if ("success" in payload && typeof payload.success === "boolean") {
      if (!payload.success) {
        const message =
          isRecord(payload.error) && typeof payload.error.message === "string"
            ? payload.error.message
            : "The round-statistics flow reported a failure and gave no reason.";
        throw new RoundStatisticsError(message);
      }
      return extractResponseText(payload.data);
    }

    const stringValues = Object.values(payload).filter(
      (value): value is string => typeof value === "string" && value.trim().length > 0,
    );
    const only = stringValues[0];
    if (stringValues.length === 1 && only !== undefined) return only;

    throw new RoundStatisticsError(
      `The round-statistics flow returned ${String(stringValues.length)} text outputs; this ` +
        "screen expects exactly one, carrying the whole JSON document (TAD §3.3).",
    );
  }

  throw new RoundStatisticsError(
    "The round-statistics flow returned no readable response body.",
  );
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

function parseExceptionalFundingSummary(raw: unknown): ExceptionalFundingSummary | null {
  if (!isRecord(raw)) return null;
  const anyCount = asNumber(raw.anyCount);
  if (anyCount === null) return null;
  return {
    population: asNumber(raw.population),
    anyCount,
    anyPercentage: asNumber(raw.anyPercentage),
    averageAmountRequested: asNumber(raw.averageAmountRequested),
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
    averageCost: asNumber(raw.averageCost),
    averageAmountRequested: asNumber(raw.averageAmountRequested),
    percentageOfCost: asNumber(raw.percentageOfCost),
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
    averageCost: asNumber(raw.averageCost),
    averageAmountRequested: asNumber(raw.averageAmountRequested),
    percentageOfCost: asNumber(raw.percentageOfCost),
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
    // Hard-coded, never parsed. FR-061's ethnicity half has no data source and never has
    // (TAD §3.4, A-R24, SDD OQ-027). If the response ever carried a value here it would be
    // a defect in the flow, and discarding it is the correct response to that — this app
    // must not become the first thing to render an Article 9 category the charity has not
    // decided to collect.
    ethnicGroupDistribution: null,
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
    populationReceived: asNumber(document.populationReceived),
    metrics: parseMetrics(document.metrics),
  };
}

/**
 * Invokes the flow and parses what comes back.
 *
 * The service is a parameter with a default rather than a hard-wired import, which is what
 * keeps A-LAND-2 to one line: the swap when the generated service arrives is to this
 * default, and every test exercises the real parse against an injected fake instead of
 * mocking a module.
 */
export async function fetchRoundStatistics(
  service: RoundStatisticsFlowService = missingFlowService,
): Promise<RoundStatisticsResponse> {
  let payload: unknown;
  try {
    payload = await service.Run();
  } catch (caught) {
    if (caught instanceof RoundStatisticsError) throw caught;
    throw new RoundStatisticsError(
      caught instanceof Error
        ? caught.message
        : "The round-statistics flow could not be reached.",
    );
  }
  return parseRoundStatisticsResponse(extractResponseText(payload));
}
