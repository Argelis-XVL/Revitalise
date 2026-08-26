/**
 * FR-063 — the round's financial position, read DIRECTLY from `rev_roundfinance`.
 *
 * No flow in the path (ADR-028). This is the one block on the landing screen whose figures
 * come from the trustee's own session, and it is deliberately as literal a reading of the
 * reviewer's *"grab that directly from dataverse"* as the feature contains.
 *
 * ## Why every row renders even when its figure is absent
 *
 * The statistics blocks beside this one do the opposite: a `null` metric there renders as
 * nothing at all. The difference is not an inconsistency, it is the two facts being
 * different.
 *
 * A `null` in the flow response means a figure was never computed — there is no field
 * anywhere that someone has left empty, so a heading over "Not recorded" would invent a
 * gap. A `null` here means a person has not yet typed a number into a row that exists.
 * That gap is real, a trustee needs to see it (otherwise the screen reads as though the
 * charity has no legacy fund rather than as though nobody has entered it), and someone can
 * act on it. This is `src/domain/format.ts`'s own long-standing rule applied to a third
 * case: "a missing value renders as words, never as a blank cell", and "'Not available' and
 * 'Not recorded' are NOT interchangeable."
 *
 * ## The as-at date, and why it is stated even when it is missing
 *
 * TAD §3.5: these figures are typed by a person on some cadence, and "a figure without an
 * as-at date invites a trustee to read last month's capacity as today's." So the statement
 * is unconditional — when `rev_figuresasat` is empty the block says the date is missing
 * rather than saying nothing, because silence here reads as currency.
 *
 * It is also visually and textually distinct from the statistics region's `computedOn`
 * stamp, which is the requirement TAD §8.3 states in its own words: "the two freshness
 * statements sit side by side and must not be confused... each block carries its own dated
 * statement." One line covering both would be wrong about one of them — these figures are
 * as fresh as a person's last data entry, the ones beside them are seconds old.
 */
import { Definitions, Panel } from "./Panel";
import { formatAmount, formatCount, formatDate } from "../domain/format";
import type { RoundFinance } from "../dataverse/types";
import styles from "../styles/app.module.css";

export function RoundFinancePanel({ round }: { round: RoundFinance }) {
  return (
    <Panel heading="The round's financial position">
      {/*
        Distinct from the statistics stamp by wording ("as at" versus "computed on"), by
        position (inside this panel, not above the region), and by class. It prints, like
        the other stamp — FR-039.
      */}
      <p className={styles.freshnessManual} data-print="stamp">
        {round.figuresAsAt === null
          ? "These figures are entered by hand and carry no as-at date, so how current they " +
            "are is not known from this screen. Ask the process owner before relying on them."
          : `These figures are entered by hand and are as at ${formatDate(round.figuresAsAt)}. ` +
            "The application figures above were computed just now."}
      </p>

      <Definitions
        items={[
          // The round's own position.
          { label: "Committed or spent to date", value: formatAmount(round.amountCommitted) },
          { label: "People supported", value: formatCount(round.peopleSupported) },
          { label: "Individuals supported", value: formatCount(round.individualsSupported) },
          {
            label: "People reached by group grants",
            value: formatCount(round.peopleReachedByGroupGrants),
          },
          {
            label: "Suggested maximum spend for this round",
            value: formatAmount(round.suggestedMaximumSpend),
          },
          { label: "Monthly disbursement", value: formatAmount(round.monthlyDisbursement) },
          // Charity-level rather than round-scoped, and labelled as such. Amendment A-03
          // Finding 3 established the distinction; a trustee reading "capacity" as this
          // round's budget would be reading the wrong number.
          {
            label: "Grant-giving capacity (charity-wide)",
            value: formatAmount(round.grantGivingCapacity),
          },
          {
            label: "Remaining legacy fund (charity-wide)",
            value: formatAmount(round.remainingLegacyFund),
          },
        ]}
      />
    </Panel>
  );
}
