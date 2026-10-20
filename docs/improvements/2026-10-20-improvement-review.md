# Improvement Review — 2026-10-20

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` → 1 cluster (IMP-1143 only — narrowed by the reviewer mid-draft, relayed by lead-agent 2026-10-20: *"Narrow it to IMP-1143"*)
**Trigger:** reviewer request — `verify-improvement-log.py --check` warned that IMP-1143, corrected by IMP-1145, was unprocessed
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-20 (rows 1-2). See §8.
**WBS:** system work, `wbs:system`, not billable. The finding itself belongs to wbs:2.4 and 2.7.

---

## Summary

One knowledge change is proposed: the domain business rules and the glossary still say an application over the income ceiling is rejected whatever its score, and they say nothing about the three other automatic-rejection rules. The approved SDD (Amendment A-10 revision 2, approved 2026-10-19) now states all of them, so the knowledge file is rewritten to match it and cites it.

The build was not going to fail on this finding. The warning says it would, but I ran the build's own command and it passes (details at the end). Processing the finding still matters, because the warning stays lit until a review handles it.

## What has been built

Nothing yet. This is a draft. What it proposes:

1. **The income rule in the knowledge file matches the approved SDD** — [business-rules.md L33](knowledge/domain/business-rules.md#L33) says *"An application over the income ceiling is rejected regardless of score"*. The approved rule is narrower: only an applicant who does not receive means-tested benefits is rejected on income, a benefits Yes is never rejected on income, and no band given is not rejected ([FR-015](docs/plans/revitalise-grant-automation-plan.md#L1788)). The finding's own proposed wording (rejection for an applicant *in work*) was withdrawn by the reviewer the same afternoon. This draft uses the approved SDD text, not the finding's.

2. **The three other rejection rules get a row each** — amount over the limit for the type of break with no exceptional request ([FR-102](docs/plans/revitalise-grant-automation-plan.md#L1796)), savings over £6,000 ([FR-103](docs/plans/revitalise-grant-automation-plan.md#L1797)), and Revitalise funding in the last 12 months ([FR-104](docs/plans/revitalise-grant-automation-plan.md#L1798)). The last one was built under EF-34 with no requirement behind it, which is what the finding found. FR-104 now states it.

3. **The open DPO question covers all the rules, not only the score threshold** — [BR-S10](knowledge/domain/business-rules.md#L36) names only "rejection at the threshold". [OQ-005](docs/plans/revitalise-grant-automation-plan.md#L2874) was re-dated by A-10 to cover the flow carrying FR-102 to FR-105.

4. **The glossary's "Income ceiling" entry is corrected the same way** — [glossary.md L21](knowledge/domain/glossary.md#L21).

## Elements changed

| File | Change |
|---|---|
| `knowledge/domain/business-rules.md` | BR-S05 and BR-S07 rewritten, BR-S10 widened, BR-S12 to BR-S14 added |
| `knowledge/domain/glossary.md` | "Income ceiling" entry rewritten |

## What is still open

**Every other unread finding waits for a later review.** IMP-1139 to IMP-1142 and IMP-1144 to IMP-1158 are outside this review by your instruction. Two of them are blockers already fixed in source and waiting on a DEV re-run (IMP-1139, IMP-1156); neither halts a build.

**IMP-1145 overlaps this change.** Its knowledge half is what row 1 applies, since it supplied the corrected wording. Its other half (a rule for plan-agent about which screens a persona can open) is not in this review, so IMP-1145 stays unread.

**Review 2026-10-17 is still parked at its gate** with IMP-1137 and IMP-1138. It needs its own keyword; this review does not touch it.

## What you need to decide

Nothing beyond the keyword.

---

## 1. Regression check

The last review applied is 2026-10-16-2 (13 rows, row 13 withheld). None of its rows targeted IMP-1143's class (`stale-claim-contradicting-rechecked-source`), and none of the other 12 classes recurs in this one-finding scope.

| Prior change | Applied | Class it targeted | Recurred in this scope? | Verdict |
|---|---|---|---|---|
| Rows 1–13 of 2026-10-16-2 | 2026-10-17 | provenance, parallel dispatch, ADR supersession, engine publish, census, guid syntax, create-only POST, write outputs, class-defences, per-line log edits | NO | Not audited further here; the narrowed scope cannot show a recurrence |

**Changes whose class recurred after a *prose* fix:** none in scope.
**Changes whose class recurred after a *gate*:** none in scope.

## 2. Clusters and promotion decisions

```
CLUSTER: stale-claim-contradicting-rechecked-source  (x1 here: IMP-1143)
Altitude:   INSTANCE — the defect is two stale rows in this client's own domain knowledge
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge
Becomes:    knowledge/domain/business-rules.md + knowledge/domain/glossary.md, rewritten to cite
            the approved SDD FRs (FR-014, FR-015, FR-102, FR-103, FR-104, OQ-005)
Retires:    nothing
Cites:      IMP-1143
Residual:   nothing links a knowledge row to the requirement or open question it depends on, so
            the next amendment to FR-014 can leave these rows stale again. The finding's proposed
            gate (compare the flow's rejection conditions with the SDD FR set) is not proposed:
            one instance, and the rule set is now stated in one FR (FR-014).
```

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | [business-rules.md L31–L37](knowledge/domain/business-rules.md#L31) | **BR-S05** becomes: *"The knockout threshold, the borderline band, the income ceiling and the amount limit for each type of break are held in Settings, and the savings and prior-funding rules each have an on/off switch; the process owner changes them without editing a flow (FR-017). ⚠️ The board has not set the threshold value; PRD seeding is blocked by design until it does (SDD OQ-001, OQ-002)"*. **BR-S07** becomes: *"An applicant who does not receive means-tested benefits and whose income band is above the income ceiling is auto-rejected, whatever the score. Employment status is not read. A benefits Yes is never rejected on income, and no band given is not rejected (FR-014, FR-015, A-10 rev 2)"*. **BR-S10**: "at the threshold" becomes "by any FR-014 rule (OQ-005, re-dated by A-10 to the first PRD deploy carrying FR-102 to FR-105)". New rows: **BR-S12** *"A request over the limit for its type of break, with no exceptional funding request, is auto-rejected: over £500 for Holiday accommodation, Respite Care Facility stay and Other, over £100 for Day trips or outings and Activity or Experience; each limit is a setting, and the limit itself passes (FR-102)"*; **BR-S13** *"Savings over £6,000 (a Yes) is auto-rejected for every applicant while the savings switch is on, the default (FR-103, BR-S11)"*; **BR-S14** *"Revitalise funding within the last 12 months is auto-rejected while the prior-funding switch is on, the default (FR-104; built under EF-34 before any FR stated it)"* | IMP-1143 | YES — needle `BR-S14` in `knowledge/domain/business-rules.md` (0 today) | N/A |
| 2 | knowledge | [glossary.md L21](knowledge/domain/glossary.md#L21) | "Income ceiling" becomes: *"The means-test income limit. An applicant not on means-tested benefits whose income band is above it is auto-rejected (BR-S07). Held in Settings, adjustable by the process owner"* | IMP-1143 | YES — needle `not on means-tested benefits whose income band` in `knowledge/domain/glossary.md` (0 today) | N/A |

**Constraint budget:** 0 of 3 used.

## 4. Retirements

> Retirement check performed: 88 live constraint rows, 10 retired (derived with the registered grep). None touches the auto-reject rules or the domain knowledge rows changed here, so none is redundant because of this change.

## 5. Findings left unprocessed

**Deferred:** IMP-1139, IMP-1140, IMP-1141, IMP-1142, IMP-1144, IMP-1145, IMP-1146, IMP-1147, IMP-1148, IMP-1149, IMP-1150, IMP-1151, IMP-1152, IMP-1153, IMP-1154, IMP-1155, IMP-1156, IMP-1157, IMP-1158

| Finding | Why deferred | Revisit when |
|---|---|---|
| All of the above | the reviewer narrowed this review to IMP-1143 on 2026-10-20 | the next review dispatched for the unread queue |

IMP-1157 and IMP-1158 were logged by this dispatch before the scope changed. They stay unread, with no `reviewed_in`.

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 1154 | 1154 |
| Distinct lessons | unchanged by this review | unchanged |
| Recurring classes (x≥2) | unchanged | unchanged |

Regenerated at apply with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`.

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-20-improvement-review.md

Findings processed: 1 NEW  →  1 clusters
Regression check:   13 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 2 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 1 left as notes
Digest:             will regenerate — lessons unchanged, recurring classes unchanged

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

On approval: rows 1 and 2 land, then IMP-1143 moves to `APPLIED` with `applied_by` naming rows 1–2 and `evidence_grep` `{"file": "knowledge/domain/business-rules.md", "contains": "BR-S14"}`. `observable_at` is `n/a`, so no `reobserved` is needed.

**Verification.** I ran `python3 scripts/verify-improvement-log.py --check`, the build's own `improvement-log-check` step. It exited 0 with IMP-1143 unprocessed, and the `unit-tests` Pester block runs the same command. So the warning's claim that the next build fails was false: IMP-1143 is not a blocker, and 16 unread plus 2 fixed-in-flight is below the batch threshold of 45. Not verified: the full build and the Pester suite, which this draft did not run.

## 8. Applied

Approved 2026-10-20: the reviewer wrote *"Approve improvement"*, relayed by lead-agent as `APPROVE IMPROVEMENTS`. Before applying, I re-checked the tree. The target rows were unchanged since the draft, and no new entry carries `corrects` naming IMP-1143. IMP-1145 was read before drafting, and its wording is the one applied.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `knowledge/domain/business-rules.md`: BR-S05 and BR-S07 rewritten, BR-S10 widened, BR-S12 to BR-S14 added, as drafted | working tree, uncommitted | IMP-1143 (`evidence_grep` needle `BR-S14`, 1 match) |
| 2 | `knowledge/domain/glossary.md`: "Income ceiling" rewritten, as drafted | working tree, uncommitted | IMP-1143 |

No entry rejected. No other finding touched.

**One consequential edit, not a rule change.** Regenerating the digest made it 633 lines, so `verify-derived-counts.py` reported the sentence *"the digest is 632 lines"* at line 46 of `generate-known-failure-modes.py` as drifted. I corrected it to 633 in both copies, `scripts/` and `.engine/scripts/`, which are byte-identical again. The agent rules say the review whose regeneration causes this drift corrects it. Gates after apply: `verify-improvement-log.py` schema exit 0, `--check` exit 0 with 0 warnings, digest `--check` current (1157 entries), `verify-derived-counts.py` exit 0, `verify-class-defences.py` exit 0. Nothing is committed yet. The `.engine` edit needs its own commit and push, before the pointer bump.
