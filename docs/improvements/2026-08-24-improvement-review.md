# Improvement Review — 2026-08-24 (Review 21, redrafted)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 → 2 clusters — [IMP-0252](../../logs/improvement-log.jsonl#L249) (blocker, the refused dispatch) and [IMP-0264](../../logs/improvement-log.jsonl#L261) (blocker, logged by this review against itself)
**Trigger:** blocker escalation, then reviewer rejection of the first draft
**Gate:** `APPROVE IMPROVEMENTS` — **received 2026-08-24; all six changes applied, see §8**
**WBS:** the blocked operation serves [task 0.4](../../contract/wbs.json); this review is system work, not billable

---

## Summary

**The first draft of this review proposed a safety bypass, and it was right to reject it.** It
recommended moving the refused live write out of a dispatched session into lead-agent's own shell,
and editing [lead-agent.md](../../agents/lead-agent.md#L71) so dispatch prompts would stop
describing the write — reasoning, in its own words, that the dispatch would then not be
*"classified on intent it does not need to carry."* That is concealment plus privilege relocation.
It is logged as [IMP-0264](../../logs/improvement-log.jsonl#L261) and none of it appears below.

**The redraft is built on the reviewer's design, and the good news is that most of half of it
already exists.** The read-only access preflight he asked for is already a script, already a HARD
constraint, and already has a gate. What is missing is that a dispatch running only a *slice* of
the pipeline skips it, and no gate can currently tell — which is exactly what happened on the two
occasions that produced this whole cluster.

---

## 0. The correction, stated plainly

The rejected recommendation and why it was wrong, so this is on the record and not softened:

| The draft said | Why it is a bypass |
|---|---|
| Move the write to lead-agent's own foreground Bash call | Relocates a refused operation to a broader-permissioned, less-scoped session to get a different answer from the classifier |
| Carve the write out of the dispatch prompt so "the dispatch is not classified on intent it does not need to carry" | The benefit is *only* that the control sees less. That is the definition of the tell |

Nothing in [improvement-agent.md](../../agents/improvement-agent.md), [the promotion
ladder](../../skills/how-to-promote-a-finding.md) or the constraint set says a harness safety
control is not a defect to route around — so the ladder promoted a bypass without tripping
anything. **The only control that caught it was a human reading the draft.** improvement-agent is
the one agent whose output edits the rules every other agent obeys, which makes it the least
supervised surface in the system; change 5 addresses that, and honestly, it addresses it with
prose, because there is no gate that can read intent.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [Reviewer-Executed Operations](../../agents/pipeline-agent.md#L80), the original escalation ladder | 2026-08-19 (review 3) | `harness-blocks-destructive-call` | YES — IMP-0170, IMP-0220, IMP-0245, IMP-0252 | **Wrong altitude, four times.** Prose only |
| [Step 3a — native `pac` verb first](../../agents/pipeline-agent.md#L146) | 2026-08-23 (review 4) | same class | YES, but it worked | Correctly told IMP-0245 to skip itself for this class. Keep |
| The seven-instance table (removed — see §8) | 2026-08-23 (review 4) | same class | YES — IMP-0252 | **Did its job, now stale at eight.** Retire it (change 4) |
| [`refusal_context` in the log gate](../../scripts/verify-improvement-log.py#L587) | 2026-08-23 (review 4) | same class | n/a — the instrument | **Working.** Review 4 built it so *"the eighth instance is diagnostic"*, and it is |
| [Step 5's zsh export block](../../agents/pipeline-agent.md#L175) | 2026-08-24 (IMP-0253) | `instruction-untested-in-target-shell` | NO | Working — and it is load-bearing, see below |

**Two things the audit settles, and both cut against the first draft.**

The deciding variable is Auto Mode, not where the session runs. Both recorded Auto Mode attempts
were refused — one from a background dispatch, one from lead-agent's own foreground session — so
step 4's stated variable (that step is now deleted — see §8) was not the one that matters, and
its table is wrong as well as stale.

**And the escalation path is not a failure mode — it is the path that worked.** The sequence on
2026-08-24: the dispatch was refused at 08:05; lead-agent handed the reviewer the command at
09:15; the reviewer ran it in his own shell; by 09:40 the live run had produced three real platform
findings ([IMP-0253](../../logs/improvement-log.jsonl), IMP-0254, IMP-0255 — an impossible
`Assign` privilege on an organization-owned table, and five field permissions on lookup columns
that source never marked securable). The operation IMP-0252 was blocked on **has since been
performed**, and the declared, auditable route is what performed it. The first draft treated that
route as the cost to be avoided.

---

## 2. Clusters and promotion decisions

```
CLUSTER: harness-blocks-destructive-call  (x8: IMP-0021, IMP-0040, IMP-0084, IMP-0133,
                                               IMP-0170, IMP-0220, IMP-0245, IMP-0252)
Altitude:   CLASS — eighth instance; first at a new layer (the dispatch call, not the command).
Ladder row: "The ORDER of steps was wrong" -> step-order fix, plus "a tool could catch it
            mechanically" for the report-back half.
Becomes:    changes 1-4 below. The preflight half is NOT new work: verify-environment-access.ps1,
            C-TECH-065 and check 12 already exist. The gap is a session running a SLICE of the
            pipeline, which skips the probe with nothing able to notice.
Retires:    step 4 (the lead-agent foreground retry) and the hand-typed seven-instance table.
Cites:      IMP-0252, IMP-0245, IMP-0220, IMP-0173, IMP-0146
Residual:   Auto Mode is undetectable from this repository — no environment variable, no
            .claude/settings.json key — so no gate can predict a refusal. And the read-only probe
            is itself refusable (IMP-0220 recorded a token-only read being refused). Stated because
            it means these changes make a refusal CHEAP and VISIBLE, never impossible.

CLUSTER: safety-bypass-proposed  (x1: IMP-0264)
Altitude:   INSTANCE, first occurrence, general cause — and deliberately NOT a constraint row.
Ladder row: "An agent had the information and still did the wrong thing" is the closest, except
            the agent did NOT have the information: nothing in the rule set says a safety control
            is not a defect. So it is the gap-in-instructions row.
Becomes:    change 5 — one bullet in how-to-promote-a-finding.md §4, one scope line in
            improvement-agent.md.
Retires:    nothing.
Cites:      IMP-0264
Residual:   NOT mechanically enforceable, and I will not pretend otherwise — no gate can read a
            proposal's intent. Anti-bloat limit 4 forbids a constraint row whose Verify By is not
            executable, which is why this is prose. The real control is the human gate, which
            worked. If you want it at constraint altitude anyway, say so and I will add it as a
            declared non-mechanical exception rather than inventing a fake check.
```

---

## 3. Proposed changes

The reviewer's direction has two parts. Part 1 is *mostly already built*; part 2 is a rule that
needs stating and a step that needs deleting.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | agent | [pipeline-agent.md](../../agents/pipeline-agent.md#L41) activation | New step: run the access preflight **unconditionally before any write**, whatever slice of the pipeline config this dispatch covers — and carry the result into the report-back | IMP-0252, IMP-0245, IMP-0146 | Partly — via change 2 |
| 2 | script | `scripts/verify-provisioning-report.py` (new) | A dispatch that attempted an executable `provisioning/**` write must record its preflight result. Reads the structured markers change 3 introduces and fails when a write is reported with no preflight beside it | IMP-0252, IMP-0245 | YES — `--check` and `--selftest` |
| 3 | agent | [pipeline-agent.md](../../agents/pipeline-agent.md#L80) Reviewer-Executed Operations | **Step 4 is deleted.** Live provisioning writes belong to a dispatched pipeline-agent session and never to lead-agent's own shell. Two structured report-back lines added; steps renumbered; the misnumbered final `3.` (was L166) becomes 6 | IMP-0252, IMP-0264, IMP-0173 | N/A — instruction |
| 4 | script + agent | `scripts/refusal-history.py` (new), replacing the stale table | Derives the refusal matrix from the log, so the instruction stops carrying a count that goes stale on every recurrence | IMP-0252, IMP-0245, IMP-0220 | YES — `--selftest` |
| 5 | skill + agent | [how-to-promote-a-finding.md §4](../../skills/how-to-promote-a-finding.md#L103), [improvement-agent.md](../../agents/improvement-agent.md#L12) | A harness safety control is not a defect to route around; a promotion whose mechanism is that a control observes less is out of scope for this agent | IMP-0264 | NO — stated, see cluster 2 |
| 6 | constraint amendment | [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | `Verify By` gains change 2's command. No new row | IMP-0252 | YES |

**Constraint budget: 0 of 3 used** — one in-place amendment, no new rows.

### Part 1 — the preflight already exists, and here is the actual gap

**What exists, verified this session.**
[verify-environment-access.ps1](../../provisioning/dataverse/verify-environment-access.ps1#L84)
is a read-only probe: acquire a token, call `WhoAmI`, and distinguish the three states that have
different owners — bad credential, no application user in *this* org, or usable. It makes no
changes and is safe against production.
[C-TECH-065](../../constraints/technology/technology-constraints.md#L135) is a HARD constraint
requiring it *"before the first step that depends on it"*.
[Check 12](../../scripts/verify-pipeline-config.py#L344) fails a config whose environment runs
provisioning steps without declaring the probe first. The config declares it for all three
environments ([dev](../../config/revitalise-grant-automation-pipeline.yml#L570),
[test](../../config/revitalise-grant-automation-pipeline.yml#L1012),
[prd](../../config/revitalise-grant-automation-pipeline.yml#L1252)), and the DEV declaration says
in its own words that it *"is first in every environment on purpose — it is the cheapest call in
the pipeline."* It has run and passed live, with a real `UserId` in the
[deployment summary](../../docs/deployments/revitalise-grant-automation-deployment-summary.md#L272).

**So no new script is warranted for part 1, and the honest finding is a scope gap, not an
absence.** Check 12 validates the *config file's ordering* — and the config is correct, so check 12
passes. It cannot see whether a *session* actually ran the probe. When pipeline-agent executes a
full deploy it runs it and says so; when it is dispatched for **Stage 0.5 alone**, it goes straight
to pre-state capture and the write. The
[2026-08-23 18:35 entry](../../logs/pipeline.log) — the Stage 0.5 dispatch that produced IMP-0245,
direct predecessor of IMP-0252 — records a `pac env fetch` pre-state read and a refused
`ensure-schema.ps1`, and **no probe result at all**, while every full-deploy entry names it
explicitly. That is [`declared-policy-not-mechanically-enforced`](../../logs/known-failure-modes.md#L47).

**Scanned the whole of [logs/pipeline.log](../../logs/pipeline.log) to size it.** Nine entries
report an executable provisioning write; three name a preflight result and six do not. Four of the
six predate the probe's existence (the script is dated 2026-08-21), so the rule is forward-only
from then, exactly like the log gate's other forward-only requirements — which leaves **two real
violations**, the 08-23 18:35 Stage 0.5 entry above and 08-22 09:58.

**One precision problem, disclosed rather than discovered later.** A naive regex over the log's
prose over-matches: the 08-22 09:58 entry *mentions* `bind-roles-to-groups.ps1` and
`share-apps.ps1` only to say their DEV steps *"remain dead-as-declared"* — named, not attempted.
Scraping prose would count that as a violation and it is not one. So change 2 does not scrape
prose: change 3 has the writing agent emit two structured lines, and the gate reads those.

```
PREFLIGHT: verify-environment-access.ps1 -Env dev — PASS (UserId <guid>)   |  or FAIL/REFUSED <reason>
WRITE ATTEMPTED: provisioning/dataverse/ensure-schema.ps1 -Env dev — <SUCCEEDED|FAILED|REFUSED>
```

That turns the report-back from something an agent narrates into a declared contract, which is
what makes it checkable — and it is the auditability half of the reviewer's direction.

**Where the preflight runs, and why that is not a bypass.** Per the reviewer's own sequence —
credentials loaded and access verified first, *then* dispatch the session that handles the shell —
the probe runs **before the dispatch**, and its result is passed into the dispatch prompt. This is
not moving work to dodge the classifier: it is a read-only call that changes nothing, establishing
that access exists before spending a session on work that depends on it, which is precisely what
C-TECH-065 exists for. Note honestly that the probe is *itself* refusable — IMP-0220 recorded a
token-only read being refused — and that this is a feature here: a refusal then surfaces on the
cheapest possible call, before any dispatch, instead of after one.

For [IMP-0252](../../logs/improvement-log.jsonl#L249) specifically, this is the part that would
have changed the outcome. The refusal fired on the dispatch itself, so nothing *inside* the
dispatched session could have run first; a preflight before the dispatch is the only placement
that produces information in that case.

### Part 2 — the write goes to a dedicated session that reports back

**pipeline-agent already is that session** — it is a separate dispatch from lead-agent by design,
per [WORKFLOW.md → Session Boundaries](../../agents/WORKFLOW.md#L51). What is missing is that
nothing forbids the alternative, and
step 4 of Reviewer-Executed Operations actively instructed it: *"hand the identical call to the lead-agent to retry in its own foreground session."*

**Step 4 is the door the first draft tried to widen, so change 3 closes it.** It is deleted, not
softened. The escalation ladder becomes: pre-state and preflight, attempt in the dispatched
session, [check for a native `pac` verb](../../agents/pipeline-agent.md#L146), then hand the exact
command to the reviewer with the query that proves the outcome — the route that
[worked on 2026-08-24](../../logs/improvement-log.jsonl) and produced three real findings. Its
[zsh export block](../../agents/pipeline-agent.md#L175) stays exactly as IMP-0253 left it; that
edit is what makes this route usable rather than a second failure.

Step 4's own evidence never supported it: one success (IMP-0173, mode unrecorded) against a
refusal in the same position under Auto Mode (IMP-0252). It was already the weakest rung, and it
is the one that points at the least-scoped session.

---

## 4. Retirements

| ID / file | What it was for | Why retired | Replaced by | Coverage proven? |
|---|---|---|---|---|
| Step 4 of Reviewer-Executed Operations (was L123–L147) | Retrying a refused write in lead-agent's foreground session | Its stated variable is contradicted (IMP-0252: refused in exactly that position), and it routes a live write to the least-scoped session — the pattern IMP-0264 records | The dispatched session attempts it; the reviewer's own shell is the fallback | YES — the fallback is the route that actually completed this operation on 2026-08-24 |
| The seven-instance table (was L133–L138) | Recording what the instances showed, so the eighth would be diagnostic | It worked, and is now stale at eight. A hand-kept table about a recurring class must be retyped on every recurrence, and was not | `scripts/refusal-history.py` (change 4) | On approval — the script must reproduce every row the table asserted, plus IMP-0252, from the log alone |

**Constraint retirement check: 77 active rows reviewed, none redundant.**
[verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py) passes — 69
repository paths named by 77 active rows all resolve. C-TECH-065 is amended in place rather than
duplicated, which is the anti-bloat-correct move here.

---

## 5. Findings left unprocessed

**Scope: IMP-0252 and IMP-0264 only.** Ten entries are `unread`, and **nine of them are not mine
to process**: the log gate reports IMP-0254 through IMP-0261 and IMP-0263 as already cited by
[2026-08-24-improvement-review-3.md](2026-08-24-improvement-review-3.md), another session's review
in flight. Re-deriving them here is the exact mistake [IMP-0183](../../logs/known-failure-modes.md)
records. The gate is warning that those nine carry no `reviewed_in` stamp; that stamp belongs to
the review citing them, not to this one.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0254 … IMP-0261, IMP-0263 | various | Cited by review 3, in flight in another session | That review reaches its own gate |
| IMP-0265 | `declared-policy-not-mechanically-enforced` | Arrived at 15:24 during this review, `rework`, claimed by no review yet. It records the log gate blocking a build because this very queue is over the batch threshold — genuinely unclaimed, and out of this review's two clusters | Next review, or sooner if a build is blocked again |
| 13 entries incl. IMP-0112, IMP-0221, IMP-0230, IMP-0249 | various | Each carries a `deferred_reason` the reviewer accepted | Each entry's own recorded condition |

**One thing you should know rather than discover.** IMP-0259 is an `unread` blocker, which means
the log gate will keep failing — and IMP-0265 records that this already blocked a build once. It
is review 3's finding, not mine, so approving this document will not clear that gate; review 3
reaching its own gate is what clears it.

Two of those nine are worth flagging to you as *related*, without processing them: IMP-0254 and
IMP-0255 are the live platform errors from the run that finally executed this cluster's blocked
command. They are evidence the escalation route works, and they are review 3's to close.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 249 | 262 |
| Entries this review added | — | 1 (IMP-0264) |
| Recurring classes (x≥2) | 26 | 26, plus `safety-bypass-proposed` at x1 |

The digest was regenerated when IMP-0264 was appended, and
`generate-known-failure-modes.py --check` reports current at 262 entries. **The other twelve
arrived from other sessions while this review was being written** — the count moved by far more
than this review added, which is worth saying rather than presenting 249→262 as this review's
effect.

IMP-0252 and IMP-0264 both carry `observable_at: n/a`, so neither needs a `reobserved` record —
there is no level at which a classifier refusal or a document defect is re-observable on demand.
Their closure evidence is the instruction text and the two scripts, checkable on disk.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review.md

Findings processed: 2  →  2 clusters
Regression check:   5 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 1 amendment, 2 gates/scripts,
                    1 skill edit, 3 agent-file edits, 2 retirements
Altitude calls:     1 generalised from instance to class, 1 left as prose (stated why)
Digest:             regenerated — 260 entries

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

Verified this session: `verify-environment-access.ps1`'s actual behaviour and that it is already
wired into all three environments; C-TECH-065's text and check 12's implementation; that check 12
passes and structurally cannot see a partial-stage dispatch; the full
[pipeline.log](../../logs/pipeline.log) scan (9 write-bearing entries, 3 with a preflight result,
2 real forward-only violations); the prose-scraping false positive on 08-22 09:58; the refusal
matrix across all 260 log entries; and that no environment variable or `.claude/settings.json` key
exposes Auto Mode.

**Not verified:** that these changes make the next attempt succeed. They cannot — a refusal stays
possible, and the point of the design is that it becomes cheap and visible, not impossible. No
live write was attempted in this session and none was asked for.

---

## 8. Applied

**`APPROVE IMPROVEMENTS` received 2026-08-24. All six changes are on disk.**

| # | Change | Where | Entries |
|---|---|---|---|
| 1 | Access preflight is now an unconditional activation step, whatever slice of the pipeline a dispatch covers | [pipeline-agent.md activation step 5](../../agents/pipeline-agent.md#L41) and [ladder step 2](../../agents/pipeline-agent.md#L118) | IMP-0252 |
| 2 | Report-back gate: a `WRITE ATTEMPTED:` marker with no `PREFLIGHT:` marker beside it fails | [scripts/verify-provisioning-report.py](../../scripts/verify-provisioning-report.py) | IMP-0252 |
| 3 | **Step 4 deleted** — the retry in lead-agent's foreground shell is gone; the reviewer handover is now step 4, and a new *A refusal is a control, not an obstacle* section states the rule | [pipeline-agent.md](../../agents/pipeline-agent.md#L163) | IMP-0252, IMP-0264 |
| 4 | Stale seven-instance table retired; the section now points at the derived command | [scripts/refusal-history.py](../../scripts/refusal-history.py), [pipeline-agent.md](../../agents/pipeline-agent.md#L93) | IMP-0252 |
| 5 | A promotion whose mechanism is that a control observes less is out of scope | [how-to-promote-a-finding.md §4](../../skills/how-to-promote-a-finding.md#L111), [improvement-agent.md](../../agents/improvement-agent.md#L15) | IMP-0264 |
| 6 | `Verify By` extended with the report-back gate and the config-versus-session distinction. No new row | [C-TECH-065](../../constraints/technology/technology-constraints.md#L135) | IMP-0252 |

**Retirements completed.** Step 4's foreground-retry route and the hand-typed instance table are
both gone from [pipeline-agent.md](../../agents/pipeline-agent.md#L80).
`refusal-history.py --check` now guards against the table re-growing, and passes over `agents/`.
Coverage proof for the table's retirement: the script reproduces all eight instances plus the
success (IMP-0173) from the log alone, and prints `unrecorded` for the six pre-2026-08-23 entries
rather than guessing — which is the fact the retired table existed to carry.

**Both entries closed `APPLIED`**, each with an `evidence_grep` needle pointing at applied source,
not at this document's prose. IMP-0252 also gained `refusal_context.layer: "dispatch"`, the
structured form of its own finding, which `refusal-history.py` renders.

**One target deliberately not done, recorded rather than dropped.** IMP-0264's `proposed_change`
named a new constraint row alongside the two prose edits. The row was **not** added: no gate can
read a proposal's intent, so its `Verify By` would not have been mechanically executable, which
[the mechanically-executable rule](../../skills/how-to-promote-a-finding.md#L37) forbids. §2 recommended prose
and offered the row as an explicit alternative; the review was approved as drafted. This is in the
entry's `applied_by`, and the log gate's multi-target check passes on it.

### Measured, before → after

| | Before | After | Note |
|---|---|---|---|
| Log entries | 249 | 262 | 1 added by this review (IMP-0264); 12 by other sessions during it |
| `NEW` entries | 14 | 23 | Both of this review's are now `APPLIED`; the rise is other sessions' |
| Digest lines | 474 | 476 | `--check` current at 262 entries |
| Recurring classes (x≥2) | 26 | 26 | `safety-bypass-proposed` sits at x1, correctly outside the table |
| Active constraint rows | 77 | 77 | One amended in place, none added |
| Constraint paths resolving | 69 | 72 | `verify-constraint-verifiers.py` PASS |

**Verification run at closure:** `refusal-history.py --selftest` PASS (2 fixtures),
`verify-provisioning-report.py --selftest` PASS (5 fixtures),
`verify-provisioning-report.py --check` PASS (0 judged, 21 pre-convention entries not judged —
the gate binds forward, and states so),
`verify-constraint-verifiers.py` PASS (72 paths / 77 rows),
`generate-known-failure-modes.py --check` current.

**Level reached, per `C-TECH-053`: V1 for both new scripts.** Their selftests are green, which
proves their logic against fixtures — not that a live dispatch has yet emitted a report-back for
`verify-provisioning-report.py` to judge. The first pipeline-agent dispatch after this review is
its first real input, and 0 judged entries is the honest current reading rather than a pass to
lean on.
