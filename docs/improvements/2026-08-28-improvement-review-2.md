# Improvement Review 32 — 2026-08-28

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `unread` → 2 clusters
**Trigger:** two unread `blocker` entries — [`agents/WORKFLOW.md` L254](../../agents/WORKFLOW.md#L254),
*"immediately — do not batch"*. Dispatched at
[`logs/routing.log` L321](../../logs/routing.log#L321), in parallel with the delivery dispatch at
[L320](../../logs/routing.log#L320).
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** ~~DRAFT — nothing in this document is on disk~~ — **APPLIED 2026-08-28.** The reviewer
(Xander Lykopoulos) sent `APPROVE IMPROVEMENTS`. Both dispositions are on disk, the digest is
regenerated, and the blocker trigger is clear. §9 records what landed and the **one wording
correction re-verification forced** — `IMP-0401`'s approved text asserted a fact that had stopped
being true between the gate opening and the keyword arriving.
**Scope note:** blocker-only, deliberately. 43 further `unread` and 51 `reviewer-deferred` entries are
untouched — including the four siblings from the same corrective sequence as the two in scope
(`IMP-0399`, `IMP-0400`, `IMP-0402`, `IMP-0403`), all `friction`, and `IMP-0404`, which this review
logged about itself. §5 names the boundary and why it was not widened ([`how-to-promote-a-finding.md` L105](../../skills/how-to-promote-a-finding.md#L105),
and [`agents/improvement-agent.md` L119](../../agents/improvement-agent.md#L119) — a dispatch
instruction to process everything does not widen this scope, and this one did not ask).
**WBS:** both findings carry `wbs:6.9`. The review itself is system work, not billable
([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)). No figure is restated
anywhere below (D-3, [`C-COM-004`](../../constraints/commercial/commercial-constraints.md#L44)).

---

## Summary

**This review proposes no change to any rule, script, constraint or agent file.** Both blockers resolve
to recorded deferrals: one because the thing it reported is already remedied and its proposed rule edit
belongs with two siblings still in the queue, the other because the remedy is a delivery dispatch that
was running while this review was written, and the gate the finding really asks for cannot honestly be
measured against a tree that dispatch is rewriting.

**Two things the reviewer should not misread.** This review does not unblock the halted build — the
batch trigger stays lit and [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131)
stays red on it. And the live DEV exposure is **not** closed by approving this document; §5 says who
closes it and what has to be observed.

---

## 1. Regression check — did the last review's changes work?

Review 31 applied six changes earlier today
([its applied record](2026-08-28-improvement-review.md#L436)). All six are on disk and none of the
classes they targeted has recurred in the six entries appended since.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 1 — digest generator runs the structural schema check ([`generate-known-failure-modes.py` L303](../../scripts/generate-known-failure-modes.py#L303)) | 2026-08-28 | `gate-reassures-wrongly` | NO | Working — `--check` clean over 400 entries |
| 2 — [`allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py) | 2026-08-28 | `learning-substrate-destroyed` (duplicate ids) | NO — six entries appended since, `IMP-0398`…`IMP-0403`, no collision | Working |
| 3/3a/3b/3c — validator named before the generator in the skill, seven agent files and `CLAUDE.md` | 2026-08-28 | `declared-policy-not-mechanically-enforced` | Class recurred ×2 (`IMP-0399`, `IMP-0402`) — on **other** rungs, neither about the log-append path | Working on its own rung; see the note below |
| 4 — log repair (six `observable_at` values, one severity, two reallocated ids) | 2026-08-28 | schema integrity | NO — the six new entries all validate | Working |
| 5/6 — `knowledge/technology/code-apps.md`, connector-boot risk and Fluent contrast | 2026-08-28 | `code-apps-new-connector-blocks-boot` | NO | Working — and change 5's write-then-poll lesson is what the approved ADR-038 was built on |

**The load-bearing row is not review 31's, it is review 27's, and it is why cluster A needs no new
rule.** Review 27 change 5 put a self-check clause into
[`scripts/generate-subagents.py` L214](../../scripts/generate-subagents.py#L214), emitted into all 18
generated files ([`architect-agent.md` L32](../../.claude/agents/architect-agent.md#L32)). Class
`dispatched-below-required-tier` recurred today — and **that clause is what caught it**: the agent
re-derived its own tier, found its own `ROUTED_TO` line silent on escalation, and stopped before
authoring ([`logs/routing.log` L315](../../logs/routing.log#L315)). A recurrence caught pre-authoring
at zero rework is a control working, not a control missing.

**On the `declared-policy-not-mechanically-enforced` recurrences.** Seventeen instances now
([digest L37](../../logs/known-failure-modes.md#L37)), two of them appended after review 31 and both in
the batch, not here. The template's rule — a class recurring after a *prose* fix escalates to a gate —
applies to that class as a whole and is a batch-review decision, not a blocker-dispatch one. Named
rather than quietly skipped; §5 carries it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: dispatched-below-required-tier  (x1 verified: IMP-0398; x2 by class name, IMP-0290 REJECTED
           as disproved by IMP-0298)
Altitude:   INSTANCE — and deliberately not promoted. The class's one workable control already exists
            and fired on this very instance.
Ladder row: "An agent had the information and still did the wrong thing → an agent-file or skill edit"
            (how-to-promote-a-finding.md L24). Considered and NOT taken this review.
Becomes:    Nothing on disk. IMP-0398 gets a recorded deferral: the instance is remedied (the corrected
            opus dispatch ran, routing.log L316, and the TAD it produced was approved at L319), and its
            proposed_change — a reinforcement to agents/lead-agent.md's delegation section — is one of
            THREE unread findings proposing an edit to that same section (IMP-0398, IMP-0399,
            IMP-0400). One edit now, two later, is the churn the anti-bloat limits exist to prevent.
Retires:    Nothing.
Cites:      IMP-0398 (class history: IMP-0290, IMP-0298).
Residual:   The dispatcher-side check stays unmechanised, and IMP-0398's own why_it_was_never_caught
            explains why no script can close it: nothing in scripts/ sits between an agent and the Task
            tool. So the standing control is the DISPATCHED agent's self-check, which is downstream of
            the mistake — it costs a re-dispatch cycle every time rather than preventing one. That is
            the residual, and it is the whole content of the lead-agent.md edit being deferred.
```

```
CLUSTER B: gate-scope-mismatch  (x3: IMP-0003, IMP-0382, IMP-0401)
Altitude:   CLASS — third instance and a blocker, so the ladder permits a constraint row outright
            (how-to-promote-a-finding.md L23, L152). Not taken THIS review, on measurement grounds.
Ladder row: "A tool could catch it mechanically → a script plus a build gate" (L20), which is the right
            home. IMP-0401's proposed constraint names a genuinely checkable property: for every table
            a Code App writes, no column written solely by a flow sits on it; and IsAuditEnabled=1 on
            any column a non-service persona can write.
Becomes:    Nothing on disk. IMP-0401 gets a recorded deferral naming the delivery dispatch already in
            motion (routing.log L320) as the remedy for the instance, and a revisit_when tied to that
            dispatch landing AND being observed — because observable_at is V5 and no closure evidence
            exists yet (improvement-agent.md L231-L238).
            Why the gate is not wired now, stated as a measurement problem rather than a preference:
            agents/improvement-agent.md L342 requires every gate to be run over the real corpus with
            its precision adjudicated finding-by-finding before it is wired. The corpus here is the
            role XML, the entity XML, the flow definition and the app's call sites — the exact four
            things the parallel dispatch is rewriting right now, per ADR-038. A precision figure
            measured against this hour's tree would describe a tree that no longer exists, which is
            IMP-0319's failure mode with the timing inverted. Waiting also buys the gate both fixtures
            for free: the pre-split tree is a real known-bad, the post-split tree a real known-good.
Retires:    Nothing.
Cites:      IMP-0401 (class: IMP-0003, IMP-0382).
Residual:   THREE, and the third is the one that matters.
            (1) The lesson is already published — digest L109 carries it, so nothing about this
            deferral leaves the next agent uninformed; what is deferred is enforcement, not knowledge.
            (2) The class's other unread member, IMP-0382, is in the batch, so the generalisation the
            altitude rule wants will be assembled from two entries in two dispatches rather than one.
            (3) Deploying ADR-038 does NOT make the tree clean for the gate this cluster describes.
            TAD §3.9.2 keeps rev_status, rev_resultjson and rev_computedon declared on the request
            table as UNUSED rather than deleting them, for reasons argued from IMP-0017 and IMP-0019.
            So after the fix ships, a trustee-writable column with IsAuditEnabled=0 still stands on a
            table the app writes — read by nothing, written by nothing, and a true positive for the
            proposed gate as worded. The gate therefore needs the retained-and-unused case designed
            in from the start, and this is exactly the design detail a rushed wiring would have missed.
```

---

## 3. Proposed changes

**None to any rule, script, constraint, skill or agent file.** What follows is log bookkeeping only.

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | log disposition | [`logs/improvement-log.jsonl` L395](../../logs/improvement-log.jsonl#L395) | `IMP-0398` gains `deferred_reason`, `revisit_when` and `reviewed_in`. `status` stays `NEW`; state becomes `reviewer-deferred` ([`verify-improvement-log.py` L866](../../scripts/verify-improvement-log.py#L866)) | IMP-0398 | **YES** — `verify-improvement-log.py --check` drops both ids from the blocker trigger or it does not |
| 2 | log disposition | [`logs/improvement-log.jsonl` L398](../../logs/improvement-log.jsonl#L398) | `IMP-0401` gains the same three fields, the `revisit_when` naming the observation that closes a V5 exposure | IMP-0401 | **YES** — same command |

**Constraint budget: 0 of 3 used.** Cluster B's constraint is the one the ladder would allow, and
[anti-bloat limit 4](../../agents/improvement-agent.md#L288) is what stops it landing this hour: its
`Verify By` would have to name a script that does not exist, measured against a corpus being rewritten.
A constraint row whose check is unwritten is a comment.

### What each deferral will say

Written out here because a `deferred_reason` is the durable half of this review and the reviewer is
approving its wording, not just its existence.

**`IMP-0398`** — *"Instance remedied before this review opened: the corrected `model:opus` dispatch ran
(routing.log L316) and the TAD it produced was approved (L319), so nothing about this dispatch remains
to fix. Not closed as APPLIED, because nothing was applied. The proposed `agents/lead-agent.md`
delegation-section reinforcement is deferred rather than dropped: `IMP-0399` and `IMP-0400`, both
unread in the batch, each propose an edit to that same section, and three separate edits to one section
across three reviews is what the anti-bloat limits exist to prevent. Note also that the control that
actually caught this — review 27 change 5's self-check clause in `scripts/generate-subagents.py` —
worked as designed at zero rework, so the deferred edit is a second, softer belt on the dispatcher
side, not the missing control."*
**`revisit_when`** — *"the batch review of the remaining unread queue, where `IMP-0399` and `IMP-0400`
sit; all three land as one consolidated edit to `agents/lead-agent.md`'s delegation section, or the
reviewer decides that the dispatched-agent self-check is sufficient and all three are closed together."*

**`IMP-0401`** — *"The remedy is a delivery dispatch already in motion, not a rule: development-agent
was dispatched at strategic tier for `wbs:6.9` (routing.log L320) to implement approved ADR-038's table
split — `rev_roundstatisticsresult` carrying the answer with trustee Read only, the request table
reduced to the ask. The exposure is NOT closed by that dispatch being sent, and this entry stays open
until it is observed closed; `observable_at` is V5 and no `reobserved` evidence exists. Verified live on
disk while writing this: `prvWriterev_roundstatisticsrequest` still Global on REV Trustee
(`Roles/REV Trustee/REV Trustee.xml:252`), `rev_resultjson` still `IsAuditEnabled=0`
(`Entities/rev_roundstatisticsrequest/Entity.xml:111`), and `rev_roundstatisticsresult` does not exist
in source at all. The proposed write-side constraint and gate are deferred on measurement grounds, not
merits — see improvement review 32 cluster B: the corpus the gate must be measured against is the four
artefacts that dispatch is rewriting."*
**`revisit_when`** — *"the ADR-038 dispatch lands and is observed: `rev_roundstatisticsresult` exists in
source with REV Trustee holding Read and NOT Write, the portal reads the aggregate from that table, and
the live DEV privilege set has been read back after the manual revoke TAD §12.1 names as a `post_deploy`
step (`ensure-schema.ps1` grants and revokes nothing — its own convergence note at line 748, and
A-R49). Re-observation needs an identity that can query DEV, which this review had none. Note when
closing: TAD §3.9.2 retains the three answer columns on the request table as UNUSED, so the closure to
assert is 'the aggregate a trustee's screen renders is no longer trustee-writable', never 'no
trustee-writable unaudited column remains'."*

---

## 4. Retirements

**No retirements, and the audit was run.** Derived, never typed — **10 retired, 80 live** — via
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` and its live-row twin
([`agents/improvement-agent.md` L278](../../agents/improvement-agent.md#L278)).

**Nearest candidate considered and rejected.** The read-side column-confidentiality family —
[`C-TECH-069`](../../constraints/technology/technology-constraints.md#L140),
[`C-TECH-070`](../../constraints/technology/technology-constraints.md#L141),
[`C-TECH-071`](../../constraints/technology/technology-constraints.md#L142) — is where cluster B's
write-side rule would eventually sit beside, and it was checked for overlap on the chance that a
general write-side rule could absorb one of them. It cannot: all three are read-side or
property-transmission rules with live `Verify By` scripts, and IMP-0401's own
`why_it_was_never_caught` is precisely that none of them has write in scope. Adding a fourth member
later subtracts nothing from the three.

Since this review adds no rule, no row is made redundant by it.

---

## 5. Findings left unprocessed, and what you need to decide

No silent caps. This dispatch was scoped to the two unread blockers and processed exactly those.

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| `IMP-0402`, `IMP-0403` | `declared-policy-not-mechanically-enforced`, `platform-fact-groundtruthed` | Appended at 13:42 and 13:44, minutes after `IMP-0401`, by the same architect session — but `friction`, not `blocker`, so outside the trigger that summoned this review. Both are consistent with `IMP-0401`; `IMP-0403` in particular already corrects the "the platform cannot do column-level write control" claim that `IMP-0401`'s own root cause states correctly | The batch review |
| 40 further `unread` entries | various | The still-open batch, which the reviewer has not authorised. Reading them here is `IMP-0183`'s defect exactly: one unread blocker pulling a pass over settled work | The batch review |
| 51 `reviewer-deferred` entries | various | Each carries an accepted `deferred_reason`; one, `IMP-0274`, has no `revisit_when`, which the gate reports and which is a batch-review item | The batch review |
| `IMP-0404` | `gate-reassures-wrongly` | Logged BY this review, about the gate that checked it: [`verify-review-document.py` L238](../../scripts/verify-review-document.py#L238) evaluates prose one physical line at a time, so a foreign document's section reference wrapped away from the noun that identifies it is reported as a dangling self-reference. Cost one draft iteration. Not fixed here — this dispatch proposed no script changes, and the fix needs re-measuring over all 37 documents because the same line-scoping may be hiding real `LOST-DEFERRAL` instances | A review authorised to change that script |

**Does the deferred `agents/lead-agent.md` reinforcement from `IMP-0398` still need to happen at all,
or is the dispatched-agent self-check enough?**

My recommendation is to let it wait for the batch, where `IMP-0399` and `IMP-0400` propose edits to the
same section, and to decide all three as one consolidated change.

The trade-off is real, though: the self-check that caught this is *downstream* of the mistake, so it
converts a wrong-tier dispatch into a wasted round-trip rather than preventing one. Three round-trips
were spent on this TAD today. If you would rather pay for the dispatcher-side reminder now, say so and
it is a five-line edit — but it is prose on a rung where prose has already been tried, and the honest
prediction is that it helps less than the consolidated version would.

**Should the write-side gate that `IMP-0401` asks for be authorised now, or after the ADR-038 dispatch
lands?**

My recommendation is after, and cluster B states the measurement reason rather than a preference: the
gate's corpus is being rewritten this hour, and a precision figure measured now would describe a tree
that no longer exists.

Waiting is not free. Until that gate exists, nothing in this repository asks *"does a persona hold
Write on a table carrying a column only a service identity should author?"* — every column gate here is
read-side, which is `IMP-0401`'s whole point, and the next table that carries a request and an answer
together will be caught by a human or not at all. If you want it sooner, the cheapest honest version is
a `scripts/` gate wired after the split lands and measured against both trees, which is what the
deferral schedules anyway.

**One thing that is not a decision, but must not be lost: the live DEV exposure is still live.**

Approving this document changes nothing in DEV. `rev_resultjson` remains trustee-writable and
unaudited, and the closure needs both the ADR-038 split deployed and the manual privilege revoke named
as a `post_deploy` step in TAD §12.1, because `ensure-schema.ps1` grants privileges and revokes none.
The `revisit_when` in §3 names that observation; nobody has performed it.

---

## 6. Verification executed for this review

| Check | Command | Result |
|---|---|---|
| Log state breakdown read before any finding | `python3 scripts/verify-improvement-log.py --check` | 95 NEW: 44 unread, 0 awaiting-approval, 51 reviewer-deferred, 0 already-fixed. FAILED on 2 triggers — blocker ×2, batch ×44. Now 96 NEW / 45 unread, after this review's own `IMP-0404` |
| Digest current before editing | `python3 scripts/generate-known-failure-modes.py --check` | Current, 400 entries; regenerated to 401 after appending `IMP-0404` |
| Generated agent files current | `python3 scripts/generate-subagents.py --check` | Current, 18 files |
| Review-document consistency | `python3 scripts/verify-review-document.py --reviews-dir docs/improvements` | 4 pre-existing findings in reviews dated 08-21, 08-22 and 08-25. **None in this document**; this review neither introduces nor repairs them |
| `IMP-0401`'s exposure, on disk | `grep -n prvWriterev_roundstatisticsrequest` + `Entity.xml` read | Both confirmed live: role XML line 252, `IsAuditEnabled=0` at Entity.xml line 111, no `rev_roundstatisticsresult` anywhere in source |
| `IMP-0398`'s remedy, in the record | `grep -n 2026-08-28 logs/routing.log` | Confirmed: L315 halt, L316 escalated re-dispatch, L319 approval of the resulting TAD |
| The revoke claim, ground-truthed rather than repeated | `grep -n -i revoke provisioning/dataverse/ensure-schema.ps1` | Confirmed at [line 748](../../provisioning/dataverse/ensure-schema.ps1#L748) — a declared, unresolved convergence gap, owner `development-agent` |

**Level reached: V1 for everything above** ([`C-TECH-053`](../../constraints/technology/technology-constraints.md#L123)).
Every check reads source or logs. **Not verified, and named because it is the gap that matters:** no
live DEV observation was made or attempted — this session holds no credential for that environment, and
the two connected MCP servers are unauthenticated. So every statement here about DEV is an inference
from source plus the pipeline log, which is exactly why `IMP-0401` is not being closed.

---

## 7. Digest impact

| | Before | Predicted after |
|---|---|---|
| Log entries | 401 | 401 |
| Distinct lessons | 400 | 400 |
| Recurring classes (x≥2) | 37 | 37 |
| Digest lines | 502 | 502 |

The "before" column is **measured, after** this review appended `IMP-0404` about itself and regenerated
the digest — 401 entries, 400 lessons, 502 lines, 37 recurring classes. Appending a finding is not
applying a change, so that one edit is on disk already; nothing else is.

**The two dispositions are a digest no-op, and the mechanism is named rather than hoped for:** the
digest selects on `status in {NEW, APPLIED}`
([`generate-known-failure-modes.py` L356](../../scripts/generate-known-failure-modes.py#L356)), and a
recorded deferral leaves `status: NEW`. Both lessons are therefore already published — `IMP-0401`'s is
at [digest L109](../../logs/known-failure-modes.md#L109) — which is the single strongest argument that
deferring enforcement does not defer learning. Predicted, not asserted: the generator runs again at
application and §9 will carry the measured figures, per `IMP-0198`.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-28-improvement-review-2.md

Findings processed: 2 NEW  →  2 clusters
Regression check:   6 prior changes audited, 1 class recurred (caught by the existing control)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 2 recorded as deferrals with triggers
Digest:             will regenerate — 400 lessons, 37 recurring classes (no delta expected)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied

`APPROVE IMPROVEMENTS` received 2026-08-28 from the reviewer (Xander Lykopoulos), approving this
document as drafted.

| # | Change | Applied | Entries dispositioned |
|---|---|---|---|
| 1 | `IMP-0398` gains `deferred_reason`, `revisit_when`, `reviewed_in`. Approved wording applied **verbatim** — re-verification confirmed every claim in it still holds (`routing.log` L316/L319 unchanged; `IMP-0399` and `IMP-0400` both still `unread`) | 2026-08-28 | `IMP-0398` → `reviewer-deferred`, `status` stays `NEW` |
| 2 | `IMP-0401` gains the same three fields, **one clause corrected** — see below | 2026-08-28 | `IMP-0401` → `reviewer-deferred`, `status` stays `NEW` |
| 3 | Digest regenerated | 2026-08-28 | 401 entries, 400 lessons, 502 lines, 37 recurring classes — exactly the §7 prediction for the two dispositions |
| 4 | `IMP-0405` appended and the digest regenerated again — the capture trigger the deviation below fired | 2026-08-28 | 402 entries, 401 lessons, 502 lines, 37 recurring classes |

**Measured after application:** `verify-improvement-log.py --check` goes from 2 triggers to 1. The
blocker trigger is **gone**; unread 45 → 43, reviewer-deferred 51 → 53. The surviving trigger is the
batch (43 unread), which belongs to the concurrent batch-review dispatch, not here.

### The one deviation from the approved wording, and why it was compelled

**`IMP-0401`'s approved `deferred_reason` asserted that `rev_roundstatisticsresult` "does not exist in
source at all". Between the gate opening and the keyword arriving, it came to exist.** The parallel
`development-agent` dispatch ([`routing.log` L320](../../logs/routing.log#L320)) landed the source half
of ADR-038 while this review sat at its gate. Writing the approved sentence verbatim would have put a
false statement into the durable record, which is the one thing
[activation step 8](../../agents/improvement-agent.md#L128) exists to prevent.

Applied as a **narrowing, not a substitution**, per
[the third branch](../../agents/improvement-agent.md#L150) — the intent is untouched and the specific
false clause is named and replaced with the measurement that displaced it:

| Approved clause | Measured at application | Disposition |
|---|---|---|
| `prvWriterev_roundstatisticsrequest` still Global on REV Trustee | TRUE — [`REV Trustee.xml` L252](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L252) | Kept verbatim |
| `rev_resultjson` still `IsAuditEnabled=0` | TRUE — [`Entity.xml` L111](../../src/solutions/RevitaliseGrantAutomation/Entities/rev_roundstatisticsrequest/Entity.xml#L111) | Kept verbatim |
| `rev_roundstatisticsresult` does not exist in source at all | **FALSE** — the folder exists, untracked, and REV Trustee holds `prvRead` with no `prvWrite` on it ([`REV Trustee.xml` L266](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L266)) | **Corrected**, and the correction flagged inside the field itself |

This is logged as `IMP-0405`: a review proposing **no** changes still carries perishable content,
because a `deferred_reason` is evidence, and activation step 8 is framed around a proposed change's
premise rather than a deferral's clauses. `IMP-0275` is the same hazard on the proposal side.

**The intent survives intact, and the deferral is if anything better supported than when it was
approved.** Nothing is deployed: the portal still resolves the aggregate from the request table
([`schema.ts` L70](../../src/code-apps/trustee-review-portal/src/dataverse/schema.ts#L70), whose own
comment at L74 records that the result table is absent from DEV), and the last DEV deploy is
[`pipeline.log` 2026-08-27 21:01](../../logs/pipeline.log). So the live exposure this blocker reported
is **fully intact**, `observable_at` is V5, and no re-observation was possible from this session. The
entry stays open, which is what the approved disposition asked for. `revisit_when` was applied
**verbatim** — its clause 1 is now satisfied and the rest is not, and rewriting an approved trigger
because part of it came true is not this agent's call to make.

### Residual — one warning this review created and deliberately did not clear

Naming other findings in §5 (which the no-silent-caps rule requires) makes this document a citer of
`IMP-0382`, `IMP-0399`, `IMP-0400`, `IMP-0402`, `IMP-0403` and `IMP-0404`, so the log gate now warns
that each is cited without a `reviewed_in` stamp — `IMP-0154`'s rule. **Not stamped, on instruction:**
the dispatch applying this review was told not to touch entries outside its own two, because a batch
review is live on the same file. `IMP-0404` is the awkward one — this review wrote it, so
[`appended_by`](../../scripts/verify-improvement-log.py#L410) rather than `reviewed_in` is its correct
field, and it is left to whoever processes it. Six warnings, no errors.
