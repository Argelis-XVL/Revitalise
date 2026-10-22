/**
 * The group detail hero — card app only (TAD trustee-portal-design-2 §13.5, WI-0097). Design:
 * `GroupScreens.jsx` lines 57-60 over `Shared.jsx` `HeroBand` (lines 31-49) and `FactChips`
 * (51-62).
 *
 *   - ONE `<h2>`, accessible name "Group summary" (the existing heading); visible text the §13.7
 *     sentence "{total} requested together", or the plain heading when the total is null.
 *   - FOUR chips, as the kit draws them (GroupScreens.jsx:59): Group code, Members, Group total
 *     requested, Shared dates. TAD §13.5 names "the four facts as chips".
 *   - The white 120px badge repeats the member count, as the kit's does. It is decorative and
 *     `aria-hidden`, and its "Members" label is generated content with empty alternative text
 *     (`.heroBadgeLabelMembers::before`), so each fact is still in the DOM and the
 *     accessibility tree exactly ONCE — the property the contract test
 *     `GroupDetailPage.test.tsx` pins with `getByText("Members")`.
 */
import { useId } from "react";
import type { GroupSummary } from "../domain/groups";
import { formatAmount, formatDateRange } from "../domain/format";
import { Eyebrow, HeadingText } from "../components/Panel";
import { groupTotalSentence } from "./sentences";
import styles from "../styles/cards.module.css";

export function GroupHero({ group }: { group: GroupSummary }) {
  const headingId = useId();
  const count = String(group.memberCount);
  return (
    <section
      className={`${styles.hero} ${styles.heroWrap}`}
      aria-labelledby={headingId}
      data-print="block"
      data-hero="group"
    >
      <div className={styles.heroBadge} aria-hidden="true">
        <div className={styles.heroBadgeGroup}>
          <p className={`${styles.heroBadgeLabel} ${styles.heroBadgeLabelMembers}`} />
          <p
            className={
              count.length > 3
                ? `${styles.heroBadgeValue} ${styles.heroBadgeValueLong}`
                : `${styles.heroBadgeValue} ${styles.heroBadgeValueGroup}`
            }
          >
            {count}
          </p>
        </div>
      </div>
      <div className={styles.heroText}>
        <div className={styles.heroHeader}>
          <Eyebrow tone="purple">Group summary</Eyebrow>
          <h2 id={headingId} className={styles.heroHeading}>
            <HeadingText heading="Group summary" sentence={groupTotalSentence(group.totalRequested)} />
          </h2>
        </div>
        <dl className={styles.chipRow}>
          {[
            { label: "Group code", value: group.code },
            { label: "Members", value: count },
            { label: "Group total requested", value: formatAmount(group.totalRequested) },
            { label: "Shared dates", value: formatDateRange(group.sharedStart, group.sharedEnd) },
          ].map((fact) => (
            <div key={fact.label} className={styles.chip} data-print="tile">
              <dt className={styles.chipLabel}>{fact.label}</dt>
              <dd className={styles.chipValue}>{fact.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
