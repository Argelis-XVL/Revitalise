# Improvement Review — 2026-09-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 2 clusters
**Trigger:** blocker escalation — two unread `blocker`-severity entries (IMP-0813, IMP-0814)
**Gate:** `APPROVE IMPROVEMENTS`

**Scope.** This review processes the two unread blockers only. Eight other unread entries
(IMP-0798 … IMP-0803, IMP-0811, IMP-0812) are declared out of scope in §5 and stamped
`excluded_by` naming this document — one unread blocker must not pull a review of everything
around it (`IMP-0183`).

---

## 0. What the reviewer needs to know first

**Stamping these two entries as "reviewed" does NOT unblock the build.** The blocker rung of
`scripts/verify-improvement-log.py` fires on `unread` **and** on `awaiting-approval` alike
(STATE 2 of 4, `scripts/verify-improvement-log.py#L1373`), and `improvement-log-check` is a HARD
step with no `--warn-only` at `config/revitalise-grant-automation-build.yml#L80`. The gate goes
green only when these entries move to `APPLIED`/`REJECTED` under `APPROVE IMPROVEMENTS`, or when
the reviewer authors a `deferred_reason` on each. Simulated, not inferred — see §6.

---

## 1. Regression check — did the last review's changes work?

Audited: `docs/improvements/2026-09-20-improvement-review-3.md` (the previous review).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `agents/improvement-agent.md` — the read-the-maximum-by-hand instruction replaced by `allocate-improvement-id.py --append` | 2026-09-20 | `duplicate-improvement-id-race` | NO — 0 new instances; ids IMP-0811…IMP-0814 allocated without collision | Working — leave alone |
| `skills/how-to-log-an-improvement.md` — `corrects` carries a bare id, never prose | 2026-09-20 | `resolved-field-carries-prose` | NO — 0 new instances | Working — leave alone |
| `scripts/verify-flow-definition-language.py` check 8 — flow-wide action-name uniqueness | 2026-09-20 | `platform-contract-guessed-not-groundtruthed` | NO | Working — leave alone |
| The IMP-0804/IMP-0805/IMP-0807 branch-rename fixes in the round-statistics flow | 2026-09-20 | `rename-leaves-unreachable-branch-output` | **APPARENTLY yes (IMP-0813) — and on re-measurement, NO** | See §2, cluster 1 |

**Changes whose class recurred after a prose fix:** none.
**Changes whose class recurred after a gate:** none.

**The fourth row is the instructive one.** IMP-0813 was logged under
`rename-leaves-unreachable-branch-output`, which would have made it the third instance of a class
fixed two days ago and would have put a constraint row on the table. It is not that class. The
string `Set trailing 2` (with a space) appears nowhere in the working tree and in no commit —
`git log -S"Set trailing"` and `git log -S"Set trailing 2"` both return nothing, and the source
flow defines `Set_trailing_1` … `Set_trailing_6` with underscores
(`src/solutions/RevitaliseGrantAutomation/Workflows/REVPortalRoundStatistics-8F1C2A44-1005-4B7A-9E21-0A1B2C3D4E05.json#L2950`).
There is no source-side rename, so nothing was left dangling by one. The defect is in the live DEV
copy only.

**A second regression-check observation, on the loop itself.** The identical situation arose on
2026-09-20 with IMP-0804 and the loop handled it correctly end to end: `logs/routing.log` records
`ROUTED_TO:improvement-agent` at 20:26, the keyword relayed at 21:20, the queue clear at 21:35 and
the build re-dispatched at 21:36. The defence works where it is read. See cluster 2 for where it
was not read.

---

## 2. Clusters and promotion decisions

```
CLUSTER: live-definition-drifts-from-source  (x1: IMP-0813)
Altitude:   INSTANCE — one occurrence, one environment, one flow. Re-measured out of the
            class it was filed under (see §1, row 4).
Ladder row: "One instance, but the cause is general and a human needs to know it"
            → a line in the relevant knowledge file. NOT a constraint, NOT a gate: no gate
            can read a live Power Automate definition, and the mechanism by which DEV drifted
            is unknown — an argued mechanism is not evidence (how-to-promote-a-finding §4).
Becomes:    one diagnostic line in knowledge/technology/build-and-deploy.md: when a designer
            save names an action that is not in source, establish whether the name ever
            existed in source (git log -S) BEFORE hunting a rename; where it never did, the
            live definition has drifted and the remedy is re-import from source.
Retires:    nothing
Cites:      IMP-0813
Residual:   Nothing detects this drift in advance. A live definition is only ever observed
            when a human opens the designer, and this review proposes no mechanism to change
            that — proposing one would be speculation about a cause nobody has established.
```

```
CLUSTER: build-blocked-by-the-finding-it-remediates  (x2: IMP-0814, and IMP-0285 on 2026-08-24)
Altitude:   CLASS — second instance. But the two instances are filed under two different
            classes (IMP-0285 as `learning-substrate-destroyed`, IMP-0814 as
            `gate-cannot-fail`), neither of which names the pattern, so the recurrence is
            invisible to the clustering step the altitude rule runs on.
Ladder row: "The ORDER of steps was wrong" — not "a tool could catch it mechanically".
            The tool exists, is wired, and fired correctly; IMP-0814 says so itself.
Becomes:    one instruction line in agents/pipeline-agent.md, cross-referencing the canonical
            statement already in agents/lead-agent.md rather than restating it.
Retires:    nothing
Cites:      IMP-0814, IMP-0285
Residual:   This closes the one dispatcher measured doing it. It does NOT bind a session that
            dispatches a delivery agent without reading any agent file — see the open decision
            in §5, which is outside this agent's edit remit.
```

**Why no new gate for cluster 2, stated plainly.** IMP-0814's own `proposed_change` proposes none,
and re-measurement agrees: `agents/lead-agent.md#L320` already says *"Run it BEFORE dispatching
`build-agent` or `pipeline-agent`, not after"*, `#L325` says *"READ ITS EXIT CODE, NOT ITS
NARRATIVE. Anything other than 0 blocks the dispatch"*, and `#L328` already covers this exact case
— *"A blocker at `awaiting-approval` fails by design"*. Proposing a preflight would be proposing
hygiene that is already written down, which is the tell `agents/improvement-agent.md#L153` names.

**What actually happened instead.** `logs/routing.log` contains **zero** entries dated 2026-09-21
or 2026-09-22. The 2026-09-22 build dispatch was made by pipeline-agent directly
(`logs/pipeline.log`, the 09:35 entry), not routed through lead-agent, so lead-agent's preflight was
never executed and the dispatch is unlogged. The rule is effective; it binds one agent and the
dispatch was made by another.

**One finding's stated reasoning did not survive re-measurement, and this is recorded because the
decision it supported was independently right.** IMP-0814 rules out the scoped-local-fix exception
partly on the ground that IMP-0813's class *"already has 2 prior instances, IMP-0805/IMP-0807 — a
recurring pattern"*. That premise is false: IMP-0813 is not that class (§1). Condition 1 of the
exception was therefore satisfiable. Conditions 2 and 3 were not — the fix is unverified and an
agent may not author its own `deferred_reason` (`agents/WORKFLOW.md#L430`) — so routing to this
review was the correct action for a partly wrong reason. This is the pattern
`agents/improvement-agent.md#L188` names: a false premise supporting a correct decision is never
exercised and so is never disproved.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | `knowledge/technology/build-and-deploy.md` | When a Power Automate designer save names an action absent from source, run `git log -S"<action name>"` before hunting a rename; no hit in any commit means the live definition has drifted and the remedy is re-import from source, not a source-side fix | IMP-0813 | N/A — knowledge line | N/A |
| 2 | agent | `agents/pipeline-agent.md` | Before dispatching `build-agent` (or any delivery agent) from this agent's own session, run `python3 scripts/verify-improvement-log.py --check` and read `$?`; non-zero blocks the dispatch, and a blocker describing the very defect the build would fix is the case to look for. Cross-references `agents/lead-agent.md`'s canonical statement rather than restating it | IMP-0814, IMP-0285 | N/A — instruction change | N/A |
| 3 | other | `logs/improvement-log.jsonl` | Correct `class_instance_of` on two entries so a third instance clusters: IMP-0813 `rename-leaves-unreachable-branch-output` → `live-definition-drifts-from-source`; IMP-0814 `gate-cannot-fail` → `build-blocked-by-the-finding-it-remediates` | IMP-0813, IMP-0814 | YES — `python3 scripts/verify-improvement-log.py --check` | N/A |

**Constraint budget:** 0 of 3 used.

**Row 3 is the change that matters most and it looks like bookkeeping.** `class_instance_of` is
what the altitude rule counts. Left as filed, IMP-0813 inflates a class that was defended two days
ago to three instances (which reads as a failed fix), and IMP-0814 adds a 52nd member to
`gate-cannot-fail` — a class meaning *"a gate reported PASS while checking nothing"* — for an
incident in which the gate did exactly its job. A third occurrence of the build-blocked-by-its-own-
fix pattern would again fail to cluster, and clustering is the only mechanism that would escalate it.

---

## 4. Retirements

> Retirement check performed: 86 live constraint rows reviewed (10 already retired, derived with
> `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), none currently redundant. This
> review adds no constraint and no gate, so it supersedes nothing; the nearest candidate,
> `C-TECH-061`, is the rule that fired correctly in both clusters and is doing the job it was
> written for.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0798, IMP-0799, IMP-0800, IMP-0801, IMP-0802, IMP-0803, IMP-0811, IMP-0812

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0798 | `gate-reassures-wrongly` | not a blocker; out of this review's blocker-only scope | the next scheduled review |
| IMP-0799 | `test-hardcodes-container-descent-depth` | not a blocker | the next scheduled review |
| IMP-0800 | `stale-claim-contradicting-rechecked-source` | not a blocker, but see the note below | the next scheduled review |
| IMP-0801 | `stale-claim-contradicting-rechecked-source` | not a blocker; corrects IMP-0800 | processed together with IMP-0800 |
| IMP-0802 | `untriaged-tool-warning` | not a blocker | the next scheduled review |
| IMP-0803 | `dispatch-brief-asserts-unverified-fact` | not a blocker | the next scheduled review |
| IMP-0811 | `triaged-warning-cites-no-local-row` | not a blocker | the next scheduled review |
| IMP-0812 | `credential-not-on-the-machine-that-needs-it` | not a blocker; and its premise is already contradicted by `logs/pipeline.log`'s 09:35 entry, which records `pac org who` succeeding in a later session | a session establishes whether the hang recurs |

**IMP-0800 carries a standing gate WARNING** — it is corrected by IMP-0801 and no review has
processed it, and the gate's own message asks for it to be processed rather than deferred. It is a
WARNING, not one of the counted problems, so it does not block the build today. It is named here
rather than silently left.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 810 | 810 |
| Distinct lessons | 734 digest lines | regenerated at application |
| Recurring classes (x≥2) | `gate-cannot-fail` 51, `rename-leaves-unreachable-branch-output` 3 | `gate-cannot-fail` 50, `rename-leaves-…` 2, `build-blocked-by-the-finding-it-remediates` 1 (2 once IMP-0285 is linked), `live-definition-drifts-from-source` 1 |

**Disposition simulated, not inferred.** Both runs were executed against a scratch copy of the log
and the real file was restored and confirmed byte-identical with `diff`.

- **With only `reviewed_in` stamped** (this draft's state): exit **1**, blocker TRIGGER still
  naming IMP-0813 and IMP-0814. The blocker rung fires on `awaiting-approval` exactly as on
  `unread`.
- **With both entries closed** (post-approval state): the blocker **TRIGGER clears**. The run still
  exits 1 on two `evidence_grep` errors, and that is the simulation being honest rather than a
  problem — the needles point at file edits that this draft has deliberately not made yet.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-22-improvement-review.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   4 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    1 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 734 lessons, 2 class corrections

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Authorisation record** (`agents/WORKFLOW.md` → *"What channel a keyword must arrive through"*):

| Field | Value |
|---|---|
| `authorised_by` | Xander Lykopoulos |
| `relayed_by` | the dispatching coordinator session, quoting his own conversation turn |
| Keyword | `APPROVE IMPROVEMENTS`, verbatim |
| Artefact | the three changes below |

A first relay of this keyword was **refused** before this one: it named no human and did not state
it was quoted, which `agents/WORKFLOW.md#L581` lists among the forms that stay refused. The second
relay named the reviewer and stated the quotation, and was accepted.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `knowledge/technology/build-and-deploy.md` — new subsection *"A designer error naming an action that is not in source: establish whether it EVER was"* under *Diagnosing a Failed Import*: the `git log -S` diagnostic, the underscore/space spelling trap, and the statement that no gate reads a live flow definition | working tree, uncommitted | none — see the deviation below |
| 2 | `agents/pipeline-agent.md` — new subsection *"Before you dispatch ANOTHER agent to fix what a finding describes"* at the end of *On Activation*: run the queue gate and read `$?` before dispatching `build-agent`, with the self-referential blocker named as the case to look for, pointing at `agents/lead-agent.md`'s canonical statement rather than restating it | working tree, uncommitted | IMP-0814 |
| 3 | `logs/improvement-log.jsonl` — `class_instance_of` corrected on both entries: IMP-0813 → `live-definition-drifts-from-source`, IMP-0814 → `build-blocked-by-the-finding-it-remediates` | working tree, uncommitted | IMP-0814 |

### Deviation from the draft: IMP-0813 is DEFERRED, not APPLIED

**The draft's §0 and §6 both described the post-approval state as "both entries closed". One of them
could not be closed, and this is recorded here, on the entry, and in the gate output.**

IMP-0813's `observable_at` is **V4** — the defect was only ever visible when a human opened the
designer. `scripts/verify-improvement-log.py` refuses a V4 closure without a `reobserved` record
naming who re-ran the reproduction and what they saw, and **nobody has: the flow in DEV is still
corrupted.** Closing it would have been a claim, not a result. So change 1 is applied and the entry
stays `NEW` with a reviewer-approved `deferred_reason` and a `revisit_when` naming the observation
that would close it — the gate's own named second discharge, and the same disposition IMP-0804
received on 2026-09-20.

**This clears the blocker rung either way**, which is the practical point: the deferral is not a
weaker outcome for the build, only an honest one for the record.

### Verification after applying

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **exit 0** — 8 unread, 0 awaiting-approval, 179 reviewer-deferred; blocker TRIGGER cleared |
| `generate-known-failure-modes.py --check` | exit 0 — digest current, 810 entries |
| `verify-derived-counts.py` | exit 0 — 10 registered claims match, after correcting the digest line count this review's own regeneration drifted (733 → 736, in both the instance and `.engine` copies) |
| `verify-class-defences.py` | exit 0 — 4 defences, 25 references resolved |
| `verify-review-document.py` | exit 0 |
| `verify-engine-instance-split.py` | exit 0 |

**Not verified, and it is the thing that matters most:** the DEV flow itself. Nothing in this
session can read or repair a live Power Automate definition.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| none | — |
