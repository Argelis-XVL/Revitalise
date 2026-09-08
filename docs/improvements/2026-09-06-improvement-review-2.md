# Improvement Review — 2026-09-06 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 4 `NEW` → 3 clusters
**Trigger:** blocker escalation — `IMP-0627`, `IMP-0628`, `IMP-0629`, `IMP-0630`, all `unread`,
all severity `blocker`, all from the `revitalise-grant-automation-20260906-3` build session
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** DRAFT — nothing applied. `reviewed_in` stamped at step 6; `status` stays `NEW`.
**WBS:** `wbs:3.2,3.3,3.4`

**Conclusion first.** All four findings are real, all four were correct when logged, and **none of
them describes a defect still present in the build**. The incident they record is closed: the
`lint` step genuinely passed. What remains is four durable, additive rule changes — and they are
the only thing this gate is asking about.

The four entries are dispositioned as **reviewer-accepted deferrals** (`deferred_reason` +
`revisit_when` + `reviewed_in`), which is what clears
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1146)'s blocker trigger and
therefore the build's own
[`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) step. That
bookkeeping is applied. The rule changes in §3 are **not**, and need the keyword.

**One proposal is disproved and is withheld** — `IMP-0628` asks for behaviour
[`run-with-timeout.sh` L50–L58](../../scripts/run-with-timeout.sh#L50) already has. §3 change 2 is
the narrower thing the re-measurement actually exposed.

---

## 1. The evidence, re-measured — not taken from the manifest's narration

Every row below was read from the file named, this session. None is quoted from
[`manifest.json`](../../build/artifacts/revitalise-grant-automation-20260906-3/manifest.json)'s
`improvement_log_disposition` field, because a manifest narrating a finding's disposition is
precisely what `IMP-0630` is about.

| Claim | Instrument | Result |
|---|---|---|
| The `lint` step really passed | read `solution-checker/pac-solution-check-stdout.log` directly | `Correlation ID: 1487f052-6381-4cb3-958b-8a397ce0f720`, `Status: Finished`, severity table `0 0 0 0 0`, `REAL_EXIT_CODE:0` |
| That artifact postdates `IMP-0629` | `ls -laT` on the artifact directory | stdout log mtime **22:52:58**; `IMP-0629`'s own `ts` is **22:50**. The evidence is two minutes younger than the finding that refused the earlier claim |
| The withdrawn claim is genuinely withdrawn | read [`logs/routing.log` L579 and L580](../../logs/routing.log#L579) | L579 asserts correlation id `7e0df86f-…`; L580 records lead-agent withdrawing it as uncorroborated and re-running in the foreground. The withdrawal is in the record, not only in the manifest |
| `IMP-0628`'s proposed change is already present | read [`run-with-timeout.sh` L47–L58](../../scripts/run-with-timeout.sh#L47) | TERM, then a **10-second grace poll**, then `kill -KILL`. "Re-probe and escalate to KILL from inside the wrapper" is not a change — it is the existing behaviour |
| `IMP-0627`'s premise about `pipeline-agent.md` | `grep -n 'Reviewer-Executed\|REVIEWER ACTION'` on both agent files | **True.** [`agents/pipeline-agent.md` L99](../../agents/pipeline-agent.md#L99) has the section and [L188](../../agents/pipeline-agent.md#L188) the block; [`agents/build-agent.md`](../../agents/build-agent.md) has **0 hits** for either |
| `IMP-0630`'s instance count | `class_instance_of` of `IMP-0610`, read from the log | **False as written.** `IMP-0610` is `stale-deferral-uncaught-across-sessions`, not this class. The class is `IMP-0517`, `IMP-0605`, `IMP-0630` — a **third** instance, not a fourth. The digest agrees at [L68](../../logs/known-failure-modes.md#L68) |
| A new constraint is needed for `IMP-0630` | read [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) | **No.** The rule already exists, is HARD, and says exactly this. The defect is *when* it runs — step 3 of 73 — not whether it exists |

**Level reached: V1.** Everything above is a read of source, config, logs and artifacts on disk.
Nothing was packed, imported or run in an environment. The `lint` result itself is V2 evidence
produced by another session and read here, not re-executed.

---

## 2. Clusters and promotion decisions

```
CLUSTER: harness-blocks-destructive-call  (x2 new: IMP-0627, IMP-0628)
Altitude:  CLASS at x14 overall — but the ladder's normal answer does NOT apply here
Ladder row: skills/how-to-promote-a-finding.md §4, first heading — "a harness refusal is a
           control, not a defect in the pipeline". No promotion may make the classifier
           observe less. Both refusals were CORRECT and stay
Becomes:   two additive changes, neither of which touches the classifier's view of anything.
           (a) agents/build-agent.md gains the Reviewer-Executed Operations section
           pipeline-agent.md already has, so the FIRST refusal produces a handover block
           instead of a retry. (b) run-with-timeout.sh reaps its own process GROUP, so it
           stops manufacturing the orphan in the first place
Retires:   nothing
Cites:     IMP-0627, IMP-0628
Residual:  change (b) cannot help IMP-0627 AT ALL, and that is the honest limit. Pid 23362 was
           VS Code's own bundled pac binary — a foreign process the wrapper never started and
           has no business signalling. That half of the class stays permanently reviewer-owned,
           which is why (a) exists
```

```
CLUSTER: unverifiable-reviewer-claim-contradicted-by-artifact  (x1: IMP-0629)
Altitude:  INSTANCE for the incident, CLASS for the procedure — the cross-check that caught it
           was performed on initiative and is written down nowhere
Ladder row: "An agent had the information and still did the wrong thing" → a skill edit
Becomes:   one paragraph in skills/how-to-verify-a-platform-contract.md: before writing a
           status from a quoted result, diff the claim's CHRONOLOGY against the log, not only
           its existence against the artifact directory
Retires:   nothing
Cites:     IMP-0629
Residual:  the check is a judgement, not a gate, and no gate is proposed. A gate reading a
           dispatch prompt's prose for evidential weight is the shape this project has measured
           at 48–100% false five times. The instrument that actually settled this incident was
           a filesystem mtime, and mtimes are already what build-agent is told to trust
```

```
CLUSTER: routed-work-not-reverified-at-apply-time  (x1: IMP-0630)
Altitude:  CLASS — third instance (IMP-0517, IMP-0605, IMP-0630). IMP-0605's own applied_by
           said "A third makes it a constraint row", and this is the third
Ladder row: "A platform law, or a third instance" → a constraint row — EXCEPT that the row
           already exists. C-TECH-061 is HARD and states the rule verbatim
Becomes:   a THIRD enforcement path, named additively in C-TECH-061's own idiom: the same
           check re-run as the LAST build step, so a blocker logged during the build cannot
           be narrated away in a manifest written after it
Retires:   nothing
Cites:     IMP-0517, IMP-0605, IMP-0630
Residual:  a second run of the same command catches a blocker logged DURING the build; it does
           nothing about one logged after the last step and before the manifest write. That
           window is seconds, and closing it would need the gate to read the manifest, which
           is a different and larger design
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/build-agent.md` | Add a **Reviewer-Executed Operations** section modelled on [`agents/pipeline-agent.md` L99](../../agents/pipeline-agent.md#L99), with a `REVIEWER ACTION REQUIRED` block carrying the exact command and the query that proves the outcome. Scoped to the stray/orphaned `pac` remedy: on the **first** refusal, emit the block and stop — never retry the same kill | IMP-0627, IMP-0628 | N/A — instruction change | N/A |
| 2 | script | `scripts/run-with-timeout.sh` | In `run_with_poll`, start the child in its own process group and send TERM/KILL to the **group** (`kill -TERM -$pgid`), not to `$pid` alone. `IMP-0628` observed `pac` at pid 71450 under wrapper 71449: killing the intermediate left the grandchild holding the MSAL token cache | IMP-0628 | YES — `bash scripts/run-with-timeout.sh --selftest`, plus a new case asserting no descendant survives a forced timeout | N/A — not a `verify-*.py` gate; already invoked by the `lint` step |
| 3 | skill | `skills/how-to-verify-a-platform-contract.md` | One paragraph under the verification-levels table: when asked to record a status from a **quoted or reported** result, cross-check the claim's timestamp against `logs/improvement-log.jsonl` entries for the same step and feature. A claimed success predating a later logged failure of that step is grounds to refuse and escalate | IMP-0629 | N/A — procedure text | N/A |
| 4 | other | `config/revitalise-grant-automation-build.yml` | Add `improvement-log-check-final` as the **last** step, after [`package-provisioning` L747](../../config/revitalise-grant-automation-build.yml#L747), running the identical command to [step 3 L62](../../config/revitalise-grant-automation-build.yml#L62), HARD | IMP-0630 | YES — `python3 scripts/verify-build-config.py config/revitalise-grant-automation-build.yml` | This IS the wiring |
| 5 | constraint-amendment | `constraints/technology/technology-constraints.md` | [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131)'s `Verify By` cell gains the third path, in the row's own existing "named additively (`IMP-0308`)" idiom: the `improvement-log-check-final` step, with one sentence saying why the first run is not sufficient — it fires before the build can log a blocker of its own | IMP-0517, IMP-0605, IMP-0630 | YES — the same `verify-build-config.py` run as change 4 | N/A — amends an existing wired row |

**Constraint budget: 0 of 3 used.** No new constraint is proposed, and that is a finding rather
than restraint: `IMP-0630`'s own `proposed_change` asks for a HARD row requiring build-agent to
re-run the check before writing `PASSED`, and [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131)
already **is** that row. Adding a second would be the 56-rows-and-zero-retirements failure this
agent's anti-bloat limits exist to prevent.

### The withheld proposal, and why it is withheld rather than narrowed

`IMP-0628` proposes: *"After sending TERM and before exiting, sleep briefly and re-check for the
same pid; if still alive, send KILL directly from within the wrapper."*

[`run-with-timeout.sh` L50–L58](../../scripts/run-with-timeout.sh#L50) has done exactly that since
it was written. The proposal is **not wrong about the goal** — an orphan did survive — it is wrong
about the mechanism, and applying it literally would have produced a no-op change plus a review
document claiming a fix. Change 2 is the NARROW form that preserves the intent: the escalation
exists and targets the wrong thing. It signals `$pid`, and `IMP-0628`'s own evidence names a
grandchild (71450) under a bash intermediate (71449).

**The false positive this narrowing names:** "the wrapper does not escalate to KILL" — a premise
that reads exactly like a measurement in the finding's prose and is disproved by nine lines of the
script it names.

### Why change 2 is additive, stated honestly

The tell in `skills/how-to-promote-a-finding.md` §4 is *"if a proposal's advantage disappears once
the operation is stated honestly."* Stated honestly, change 2 is: **a timeout wrapper reaps the
process group it itself started, at the moment it gives up.** That is ordinary process hygiene, the
wrapper already signals that tree at [L57](../../scripts/run-with-timeout.sh#L57), and its value is
independent of any classifier. It routes **nothing** around the refusals in `IMP-0627` or
`IMP-0628`: pid 23362 was a foreign VS Code process the wrapper never started, and pid 71450 was
already orphaned by the time the agent tried to kill it. Both of those kills would still be
refused, and both should be.

---

## 4. Regression check — did the last review's changes work?

The prior review is
[`docs/improvements/2026-09-06-improvement-review.md`](2026-09-06-improvement-review.md), applied
the same day.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| [`scripts/run-source-gates.py`](../../scripts/run-source-gates.py) — derives and runs the source-only gate set | `gate-defect` | **NO** new instance in the log | Gate exists and ran; the 20260906-3 build reached step 73 with all source gates green |
| [`agents/development-agent.md` L35](../../agents/development-agent.md#L35) — the runner made mandatory | `gate-defect` | NO | Prose change, one review old — too early to call. Watch |
| [`special-category-register.yml`](../../constraints/domain/special-category-register.yml#L308) — the `rev_escalatedon` row | `protected-path-blocks-documented-workflow` | NO | Working — `domain-invariants` green |
| `IMP-0605` / `IMP-0610` disposition: *"no gate; process discipline. A third makes it a constraint row"* | `routed-work-not-reverified-at-apply-time` | **YES — `IMP-0630` is the third instance** | **The prose fix did not hold.** Escalated here to a mechanical path (change 4), which is what the regression table's second row prescribes |

**Changes whose class recurred after a *prose* fix: one** — the row above, and it is escalated to a
build step rather than restated.
**Changes whose class recurred after a *gate*: none.** No `gate-cannot-fail` in this batch. The
opposite, in fact: `verify-improvement-log.py` fired correctly and on time, and `IMP-0630` exists
*because* it fired.

---

## 5. Findings left unprocessed

**States excluded from this review's scope, per `agents/improvement-agent.md` activation step 2**
(measured by `python3 scripts/verify-improvement-log.py --check`, which reported 148 `NEW`:
15 `unread`, 1 `awaiting-approval`, 132 `reviewer-deferred`, 0 `already-fixed`):

| State | Count | Disposition |
|---|---|---|
| `unread`, severity `blocker` | 4 | **This review's scope** — IMP-0627, IMP-0628, IMP-0629, IMP-0630 |
| `unread`, severity `rework`, same build | 1 | IMP-0631 — **not processed.** It concerns the manifest's `verification_level: V3` claim against a `pac solution check` that proves V2, which is a different mechanism from anything above. Stamped `excluded_by` naming this document, so the exclusion is declared rather than silent |
| `unread`, non-blocker, other | 10 | IMP-0611–0615, IMP-0617, IMP-0618, IMP-0620, IMP-0625, IMP-0626. **Not processed.** The trigger is the unread *blocker*; pulling ten settled-severity entries into a blocker dispatch is `IMP-0183` |
| `awaiting-approval` | 1 | IMP-0608 — parked on [`2026-09-05-improvement-review-2.md`](2026-09-05-improvement-review-2.md). **The remedy is the keyword against THAT document, not a session here.** Not re-derived |
| `reviewer-deferred` | 132 | Left as deferred; each carries a reviewer-accepted `deferred_reason` |

**One entry was appended by this review and is deliberately left `unread`: `IMP-0632`** (severity
`friction`, `corrects: IMP-0628, IMP-0630`). It records the two premises that failed
re-measurement in §1, and it carries `appended_by` naming this document so the citation check can
tell logging from processing. It is **not** processed here — a review must not adjudicate its own
finding — so it goes to whichever review next reads the queue. Its two `corrects` warnings are
visible in the gate output and are the mechanism working: they tell the approver to read `IMP-0632`
before applying change 2, which is exactly the narrowing §3 already describes.

### The four in scope, and why each is deferred rather than closed

None of the four moves to `APPLIED` or `REJECTED`, and the reasoning is the same in every case:
**`APPLIED` would be false** — no rule change is on disk, because §3 needs the keyword — **and
`REJECTED` would be false too**, because every one of them was correct when logged and its lesson
belongs on the digest read path. A deferral with an owner and a return condition is what an honest
non-closure looks like in this schema.

`observable_at` is `V2` for `IMP-0627`, `IMP-0628` and `IMP-0629`. No `reobserved` field is written
for any of them, and none could honestly be: re-observing them would mean re-creating a classifier
refusal on purpose. That is the second reason none of the three is closed.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0627 | `harness-blocks-destructive-call` | Incident closed by the reviewer clearing pid 23362 directly. The durable half — build-agent's missing handover block — is change 1 and needs the keyword | The keyword is answered against this document, either way; or a further instance is logged against build-agent |
| IMP-0628 | `harness-blocks-destructive-call` | Same incident, same closure. Its literal proposal is **disproved** (§3) and is not applied; the narrowed form is change 2 | As above; or an orphaned `pac` survives a `run-with-timeout.sh` timeout after change 2 lands |
| IMP-0629 | `unverifiable-reviewer-claim-contradicted-by-artifact` | Superseded by the `1487f052` artifact, verified here by direct read. The refusal it records was correct and is not withdrawn. The durable half is change 3 | As above; or a manifest status is again written from a quoted result with no artifact |
| IMP-0630 | `routed-work-not-reverified-at-apply-time` | The immediate instance is discharged by this review's dispositions on the three above. The durable half is changes 4 and 5. Its own instance count is corrected in §1 | As above; or a fourth instance of the class is logged |

### Routed work — nothing to route

Re-measured before writing this line, per activation step 8. Every defect the four findings name is
either closed by an event that has already happened, or is a change in §3 of this document. **No
row is handed to another agent**, and none is withheld-as-stale, because there is none.

---

## 6. Retirements

> Retirement check performed: **10 retired** and **85 live** constraint rows reviewed (derived, not
> typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10;
> `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 85). **None retired.**
> The candidate considered was [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131)
> itself — change 5 amends it, and a row that has now failed to prevent three instances of one class
> is a fair retirement question. It is **kept**: the row did not fail, its single enforcement point
> did. Retiring it would remove the only written statement of the rule the third path enforces.
> `scripts/verify-*.py` count unchanged at **57** — this review adds no gate.

---

## 7. Digest impact

Measured, not predicted, by regenerating against the log carrying this review's dispositions.

| | Before this session | After the dispositions | After approval |
|---|---|---|---|
| Log entries | 628 | **629** | 629 |
| Recurring classes (x≥2) | 48 | 48 | 48 |

The dispositions add `deferred_reason`, `revisit_when` and `reviewed_in` fields and move no
`status`, so the four entries simply move from the digest's `unread` census line to the
`reviewer-deferred` one. The 629th entry is `IMP-0632`, appended by this review — it adds one
lesson and its class sits at ×1, so the recurring-class count is unchanged. Approval changes four
statuses to `APPLIED`, which relocates their lessons within the digest without adding or removing
any.

The digest was regenerated after the append, validator first per `CLAUDE.md`'s learning rules:
`verify-improvement-log.py --check` exit **0**, then `generate-known-failure-modes.py`, then
`--check` exit **0**.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-06-improvement-review-2.md

Findings processed: 4 NEW  →  3 clusters
Regression check:   4 prior changes audited, 1 class recurred (after a prose fix)
Proposed:           0 constraints (cap 3), 1 constraint amendment, 1 gates/scripts,
                    1 skill/knowledge edits, 1 agent-file edits, 1 other, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as a note,
                    1 withheld as disproved (see section 3)
Digest:             regenerated and current — 629 entries, 48 recurring classes
Log appended:       IMP-0632 (friction) — two of the four findings carried a premise
                    that failed re-measurement; see section 3

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```
