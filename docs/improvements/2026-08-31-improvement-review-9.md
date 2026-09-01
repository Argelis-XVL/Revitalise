# Improvement Review — 2026-08-31 (9)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability, per [`agents/improvement-agent.md#L64`](../../agents/improvement-agent.md#L64)
**Authorising artefact:** [`docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md`](2026-08-31-capability-design-agent-system-optimisation.md) — workstreams **WS-A** ([L39](2026-08-31-capability-design-agent-system-optimisation.md#L39)), **WS-H** ([L210](2026-08-31-capability-design-agent-system-optimisation.md#L210)) and **WS-F** ([L172](2026-08-31-capability-design-agent-system-optimisation.md#L172)) — Parallel-safe dispatch Groups 4 and 6, folded into one dispatch because WS-H appears in both
**Findings processed:** 5 → 4 clusters
**Gate:** `APPROVE IMPROVEMENTS`
**wbs:** system (non-billable, [`C-COM-002`](../../constraints/commercial/commercial-constraints.md))
**Status:** **APPLIED 2026-09-01** — approved with WS-A explicitly scoped to **future work only**.
Four changes on disk (F1, F2, F3, H1); three withheld by the approval's own terms (A1, A2, A3).
See §10 for the applied record and §11 for what was withheld and why.

**Filename reserved at draft start, not computed at gate time.** Two other dispatches are live in
this repository right now. `2026-08-31-improvement-review-9.md` was created as a stub in this
dispatch's first minutes precisely so neither of them would compute it as "the next unused
number" — which is the defect [`IMP-0541`](../../logs/improvement-log.jsonl) describes and §4
proposes to mechanise.

---

## 0. Headline — the design document's three assigned requirements, measured

| Workstream | Requirement as written | Measured result | Disposition |
|---|---|---|---|
| **WS-A** | Scope generated subagent definitions so non-`improvement-agent` agents cannot Edit/Write `agents/`, `constraints/`, `skills/`, `knowledge/` | Both mechanisms the design document offered are **structurally incapable** of expressing it. A third one exists and does. | **REDIRECTED** — §2 |
| **WS-H** | Split `improvement-agent` into a strategic discovery phase and a standard/sonnet apply phase | The apply phase qualifies as mechanical in **8 of 58** reviews, and **0 of the 24 since 2026-08-24**. Its stated cost driver was removed hours ago by review 8. | **WITHHELD** — §3 |
| **WS-F** | Compare the finding-id sets of two concurrent reviews and flag overlap | **135** same-day review-document pairs exist in this project's history. **0** share a finding id — including WS-F's own motivating incident. The gate could never fire. | **WITHHELD as specified, REDIRECTED** — §4 |

One workstream survives in a form its own Files line did not anticipate; one is withdrawn with the
measurement recorded where the question will next be asked; one is redirected onto the resource
that actually collides. **Net: 1 new script, 1 new hook, 3 agent-file edits, 1 config comment,
0 new constraints.**

---

## 1. Regression check — did the last reviews' changes work?

The two immediately previous reviews are [review 7](2026-08-31-improvement-review-7.md) (Group 1:
WS-D/WS-J/WS-L) and [review 8](2026-08-31-improvement-review-8.md) (Group 2: WS-I/WS-M). Both are
recorded `APPLIED 2026-08-31`.

| Question | Answer |
|---|---|
| Has any finding in either review's class appeared since? | **Yes, one.** Review 7's own application produced [`IMP-0542`](../../logs/improvement-log.jsonl), class `measurement-never-ran-recorded-as-zero` — a review document asserting a measurement that never executed. It is processed here (§5, cluster C), which is what its `revisit_when` asked for. |
| Was that change prose, or a mechanical gate? | **Prose**, and it is the *only* control: [`agents/improvement-agent.md#L143`](../../agents/improvement-agent.md#L143)'s re-verify-before-apply step is what caught it. Escalating it to a gate is not possible — nothing can read a document's asserted measurement back against the command that produced it. §5 promotes it one rung instead, to a concrete shell discipline stated at the point of use. |
| Did a gate exist and not fire? | **No gate applies.** Review 7 added no gate; review 8 changed `TRIGGER_BATCH` from 10 to 30 in [`scripts/verify-improvement-log.py#L211`](../../scripts/verify-improvement-log.py#L211), verified on disk in this review and now load-bearing in §3. |
| Did the closure evidence match the level the defect was visible at? | **Yes.** `IMP-0542` is `observable_at: V1` and was observed by re-running the dropped `grep -c` unchained. No V2+ defect was closed by either review on a document assertion. |

**One recurrence, correctly caught by the one control that could catch it.** That is the regression
check's best available outcome for a class with no mechanical home.

---

## 2. WS-A — the requirement is sound; both proposed mechanisms are impossible, and a third is not

**WS-A's own open decision** ([L54](2026-08-31-capability-design-agent-system-optimisation.md#L54)):
*"whether tool scoping is expressed as a Claude Code subagent-definition field or as a
settings-level allowlist — confirm the mechanism before implementing."* The brief instructed that
this be confirmed rather than assumed. It was. **Both named options are ruled out, for different
reasons.**

### 2.1 What was confirmed

| Mechanism | Verdict | Why |
|---|---|---|
| Subagent-definition field (`tools:` / `disallowedTools:` in `.claude/agents/<name>.md` frontmatter) | **Cannot express the requirement** | Both fields are **tool-name granularity with no path awareness.** They can say "`build-agent` may not use Edit"; they cannot say "may use Edit, but not against `agents/**`". Since every delivery agent's job is writing `src/` and `config/`, a bare Edit denial is not a narrowing of the rule — it is the removal of the agent. |
| Settings-level rule (`permissions.deny` in `.claude/settings.json`) | **Cannot express the requirement** | Path globs *are* supported — `Edit(agents/**)` is valid syntax. But `permissions` rules apply to **all subagents identically**; there is no per-subagent variant. `deny: ["Edit(agents/**)"]` would therefore block `improvement-agent` — the one agent that must have that access — as surely as it blocks `build-agent`. |
| **`PreToolUse` hook keyed on `agent_type`** | **Expresses it exactly** | The hook fires for tool calls made *inside* a subagent, and its stdin JSON carries `agent_type` (the subagent's name) and `agent_id` (present **only** inside a subagent). A hook can therefore read both the calling agent and `tool_input.file_path` and deny on the combination — which is precisely "who" × "which path". |

**Consequence for the brief's generator warning.** The brief asked that
`scripts/generate-subagents.py` be run once after both WS-A's and WS-H's source changes rather than
twice. That concern dissolves: **WS-A touches neither the generator nor `.claude/agents/*.md`**, because
the frontmatter cannot carry this rule. WS-H is withheld (§3) and does not touch them either. The
generator is not run by this review at all, and `--check` is reported unchanged below.

### 2.2 What is proposed

**Change A1 — new file `.claude/hooks/protect-system-rules.py`.** A `PreToolUse` hook on
`Edit|Write|NotebookEdit` that denies the call when *all three* hold:

1. `agent_id` is present in the hook input (the call is from a dispatched subagent, not the root session),
2. `agent_type` is not `improvement-agent`,
3. the resolved `tool_input.file_path` is under `agents/`, `constraints/`, `skills/` or `knowledge/`.

**Change A2 — a `hooks` block in `.claude/settings.json`** registering A1. The file currently has
`permissions.allow` and no `hooks` key, so this is an addition, not an edit to existing content.

**Change A3 — one sentence in [`agents/improvement-agent.md#L12`](../../agents/improvement-agent.md#L12)**,
where "You are the only agent that edits `agents/`, `constraints/`, `skills/` and `knowledge/`"
currently stands as an unenforced declaration, recording that it is now enforced by A1 for
dispatched agents and *not* for the root session — so no future reader mistakes the scope.

### 2.3 The three honest limits, stated because they are real

- **This binds dispatched agents only.** `agent_id` is absent for the main session, and
  `lead-agent` *is* the main session — [review 7 §2.1](2026-08-31-improvement-review-7.md) established
  that it is never a Task dispatch. The root conversation and the human keep write access to all four
  directories. That is correct behaviour, but it means the control is narrower than "nobody but
  improvement-agent", and the sentence in A3 says so.
- **The evidence is V0, and must reach V1 before this is called enforcement.** Every fact in §2.1 comes
  from documentation, read by a delegated lookup. Nothing has been executed. This is exactly the shape
  [`agents/improvement-agent.md#L152`](../../agents/improvement-agent.md#L152) names — an assertion about
  behaviour settled by reading rather than running — and `IMP-0426` is what it costs. **The fixture
  dispatch WS-A itself demands** ([L50](2026-08-31-capability-design-agent-system-optimisation.md#L50):
  *"a fixture dispatch attempting an out-of-scope edit from e.g. `build-agent` is refused by the
  harness, not merely discouraged by prose"*) **is an apply-time obligation of this change, not an
  optional extra.** If the hook does not fire, or `agent_type` is absent in practice, A1 and A2 are
  withdrawn at apply time and reported, not shipped with a passing selftest standing in for a live run.
- **A hook is not a sandbox.** A subagent running under a permission mode that bypasses the classifier
  would not be stopped. The generator emits no `permissionMode`, so no project agent is in that state
  today — but this control's strength is "the dispatch is refused", not "the write is impossible".

### 2.4 A collision the design document's own groups table does not carry

WS-A is in **Group 4** ([L386](2026-08-31-capability-design-agent-system-optimisation.md#L386)) on the
strength of its stated Files line: `scripts/generate-subagents.py`, `.claude/agents/*.md`. Its real
mechanism touches **`.claude/settings.json`** — which is **WS-E's** file
([L165](2026-08-31-capability-design-agent-system-optimisation.md#L165)), and WS-E is running
concurrently right now.

The groups table is computed from each workstream's *assumed* mechanism, and WS-A's mechanism was an
explicitly open decision. **A groups table cannot be correct about a workstream whose file set depends
on a decision the table was drawn before making.** This is logged (§5, cluster D) and is the reason
changes A1/A2 must not be applied concurrently with WS-E's dispatch.

---

## 3. WS-H — withheld: the apply phase is not mechanical, and its cost driver is already gone

WS-H proposes moving `improvement-agent`'s apply phase to standard/sonnet, holding the WITHHOLD and
NARROW-AND-REPORT branches at strategic. Three measurements were taken before drafting. All three
point the same way.

### 3.1 How often would the de-escalation actually be safe to take?

Counting across all 58 real review documents on disk (excluding this one's own stub), for the three
markers that force a judgement call at apply time — a withhold/narrow/deviation, a routed-work row, or
a `deferred_reason` whose factual clauses must be re-verified:

| Measurement | Count |
|---|---|
| Reviews containing a withhold / narrow / deviation | **36 / 58** |
| Reviews containing routed-work language | **29 / 58** |
| Reviews containing a `deferred_reason` | **35 / 58** |
| **Reviews containing none of the three — i.e. a purely mechanical apply** | **8 / 58 (14%)** |
| Of those 8, how many are dated on or after 2026-08-24 | **0** |

All eight qualifying reviews are from 2026-08-20, 08-21 and 08-23 — the period before the WITHHOLD,
NARROW-AND-REPORT and routed-work-re-verification branches were added to
[`agents/improvement-agent.md#L143`](../../agents/improvement-agent.md#L143) at all. **The tier split
would have fired on none of the last 24 reviews.** A de-escalation that is never taken is not a saving;
it is a branch that has to be reasoned about at every dispatch and never pays.

### 3.2 The apply phase is where this agent's defects actually live

Of **111** findings logged by `improvement-agent`, **34** (31%) arise in or around the apply /
re-verify phase. Twelve are the specific shape "the apply step made a judgement and got it wrong, or
nearly did", and **every one of them was caught by a strategic-tier agent executing step 8**:

`IMP-0275` (a HARD gate applied against correct code, disproved between draft and keyword) ·
`IMP-0335` (approved wording unimplementable as written) · `IMP-0405` (an approved `deferred_reason`
that had become false in the interval) · `IMP-0426` (a root cause settled by reading a script instead
of running it) · `IMP-0517` (a routed change that would have undone an explicit reviewer decision) ·
`IMP-0542` (an absent measurement recorded as a zero, caught **today**, during review 7's own apply).

WS-H's safety argument is that WITHHOLD and NARROW-AND-REPORT escalate back. But the finding above is
not that these branches are hard to *execute* — it is that **recognising you are in one is the
judgement**. `IMP-0517` looked like an ordinary routed row until the TAD was re-read for an unrelated
reason. `IMP-0542` looked like a zero. A tier that is asked to notice when it is out of its depth,
in a phase where 12 recorded near-misses were all invisible until re-measured, is being asked for the
capability the split is trying not to pay for.

### 3.3 The stated cost driver was removed before this dispatch began

WS-H's problem statement is *"On 2026-08-28 alone this was ~7 strategic-tier dispatches in one day."*
Those dispatches were summoned by `C-TECH-061`'s batch trigger firing at ten `NEW` entries against a
single `development-agent` gate output that logged thirty.
**[Review 8](2026-08-31-improvement-review-8.md) raised that threshold to 30 hours ago** — verified on
disk in this review at [`scripts/verify-improvement-log.py#L211`](../../scripts/verify-improvement-log.py#L211)
(`TRIGGER_BATCH = 30`) and in the `C-TECH-061` row at
[`constraints/technology/technology-constraints.md#L131`](../../constraints/technology/technology-constraints.md#L131).

The queue right now stands at **3 unread, 0 awaiting-approval** against a trigger of 30. The condition
that produced seven dispatches in a day no longer exists, and it was fixed at the rung that caused it
rather than at the rung that paid for it.

### 3.4 What is proposed instead

**Change H1 — record the measurement where the question gets asked.** Extend the `rationale` string of
[`config/models.yml#L203`](../../config/models.yml#L203)'s `improvement-agent` block with the §3.1 and
§3.2 figures and the date, so the next reader proposing this split reads the answer rather than
re-deriving it. **Inside the string value, not as a YAML comment** — that file's own header
([L12](../../config/models.yml#L12)) records `IMP-0310` as one change applied twice for exactly that
mistake, and the `rationale` key is one the generator does not propagate either way, so this is a
human-facing note by design.

`escalate_to_strategic_when: [Always. This agent has no lower tier.]` at
[`config/models.yml#L216`](../../config/models.yml#L216) and
[`agents/improvement-agent.md#L3`](../../agents/improvement-agent.md#L3) **stand unchanged.** WS-H would
have retired both; withheld, they remain true.

**No new tier key, no generator change, no new agent file.** The design document's open decision for
WS-H — whether an apply-tier agent re-dispatches strategic or halts and reports — does not arise, and is
recorded as moot rather than answered.

---

## 4. WS-F — the proposed check measures zero on the entire corpus; the collision is a different resource

### 4.1 The measurement that withdraws the mechanism as specified

WS-F proposes *"a cheap pre-check [that] compares the finding-id sets each is scoped to process and
flags any overlap."* Run against every same-day pair of review documents this project has ever
produced:

| Measurement | Count |
|---|---|
| Distinct review documents referenced by a `reviewed_in` stamp | **54** |
| Same-day review-document pairs | **135** |
| Pairs sharing **one or more** finding ids | **0** |

**Zero, across thirteen days and 135 pairs — including WS-F's own motivating incident.** The
2026-08-28 reviews 3 and 4 that WS-F cites processed **45** and **16** findings respectively, and the
two sets are disjoint. Today's reviews 7 and 8 processed **3** and **0**.

This is the tell [`agents/improvement-agent.md#L481`](../../agents/improvement-agent.md#L481) names:
*"Where a gate reports 0 findings against a corpus you know contains an instance, that is the tell.
Do not record it as a clean run."* The corpus contains at least two real collisions and the proposed
design reports neither. **Wiring it would have taught everyone that this check cries nothing.**

### 4.2 Why it measures zero — and what the two real collisions actually contended over

The finding-id sets cannot overlap, structurally. A defect-driven review's scope is *"every `unread`
entry"* ([`agents/improvement-agent.md#L97`](../../agents/improvement-agent.md#L97)) — so two concurrent
defect-driven reviews would overlap **totally**, not partially, and no script is needed to predict
that. A capability-mode review's scope is a set of workstreams and frequently processes **no findings
at all** (review 8: zero). Either way the finding-id set is the wrong object.

The two collisions in the record contended over files:

- **2026-08-28, reviews 3 and 4** — both needed `scripts/verify-improvement-log.py`. Review 4 found the
  crash and **deliberately declined to fix it**, recording in `IMP-0423` that *"editing another live
  dispatch's files to unblock my own verification is exactly how two sessions clobber each other."*
  The convention worked. The residual cost was a duplicate finding pair (`IMP-0423` / `IMP-0424`)
  reconciled by review 5.
- **2026-08-31, reviews 7 and 8** — both computed the same **output filename**. Per
  [`IMP-0540`](../../logs/improvement-log.jsonl), which `corrects` `IMP-0539`, nothing was in fact
  overwritten: review 8 had not yet written any file, so review 7's write was the only write. **A
  near-miss, not a loss** — and this review is premised on the corrected fact, not on `IMP-0539`'s
  original "silently overwritten" claim.

Source-file contention is already governed by the design document's own Parallel-safe groups table
(imperfectly — §2.4). **The review filename is governed by nothing.**

### 4.3 What is proposed instead

**Change F1 — new script `scripts/allocate-review-number.py`.** The review-filename analogue of
[`scripts/allocate-improvement-id.py`](../../scripts/allocate-improvement-id.py), which exists because
the identical race on `logs/improvement-log.jsonl`'s id space **failed as prose six times**
(`IMP-0080`, `IMP-0301`, `IMP-0312`, `IMP-0339`, `IMP-0375`, `IMP-0369`) before being mechanised. The
same class has now reached a second resource (`IMP-0539`, `IMP-0541`), and
[`skills/how-to-promote-a-finding.md#L44`](../../skills/how-to-promote-a-finding.md#L44)'s altitude rule
forbids answering that with a third paragraph of prose.

The race closes more cheaply here than it did there: the *claim* is creating the file, so
`os.open(path, O_CREAT|O_EXCL)` is atomic at the filesystem level and **no lock is needed** — the loser
of the race gets `FileExistsError` and retries at the next number. The script scans
`docs/improvements/` for the date's highest review number, claims the next one by exclusive creation,
writes a reserved stub, and prints the path. Roughly 60 lines, with a `--selftest` carrying a
concurrency fixture, mirroring the allocator it is modelled on.

**Residual, stated:** `O_EXCL` is atomic per filesystem. It cannot coordinate two machines syncing the
same SharePoint path — the same residual `allocate-improvement-id.py` records for `flock`. That case
stays *caught rather than prevented*.

**Change F2 — [`agents/improvement-agent.md#L406`](../../agents/improvement-agent.md#L406)**, the Outputs
table's Review document row: the filename is claimed by `scripts/allocate-review-number.py` **at draft
start (step 6), not computed at gate time**, and a dispatch told it has concurrent siblings uses the
name its brief assigned. This is `IMP-0539`'s and `IMP-0541`'s own proposed change, placed at the row
that names the file.

**Change F3 — [`agents/improvement-agent.md#L454`](../../agents/improvement-agent.md#L454)**, the corpus-
measurement section: batch measurements with `;` and never `&&`, and print a label per measurement,
because `grep -c` exits 1 on no-match and silently drops every later command in an `&&` chain — so an
absent measurement reads exactly like a zero. This is [`IMP-0542`](../../logs/improvement-log.jsonl)'s
proposed change, deferred to this dispatch by its own `revisit_when`, and it is `IMP-0007`'s pattern
aimed at a review's own evidence rather than at a build gate. **Every measurement in this document was
taken under that discipline**, which is why §3 and §4 carry labelled counts rather than a narrative.

**No new constraint row.** F1 is a script; F2 and F3 are agent-file edits at the point of use. WS-F's
*"or 1 if made HARD at dispatch time"* is declined: a HARD gate on filename collision would have to run
in a dispatcher that is the root session, where nothing enforces it.

---

## 5. Findings processed

5 findings → **4 clusters**. Scope per
[`agents/improvement-agent.md#L97`](../../agents/improvement-agent.md#L97): the queue's 3 `unread`
entries, plus one `reviewer-deferred` entry whose `revisit_when` names this dispatch by name, plus
`IMP-0546` appended by this review (§2.4).

All five carry `reviewed_in` naming this document, stamped at draft time per
[`agents/improvement-agent.md#L125`](../../agents/improvement-agent.md#L125) — so the queue reports them
as `awaiting-approval` rather than as findings nobody has opened (`IMP-0488`). Nothing else has moved:
`status` stays `NEW` and no `applied_by` exists. The queue now reads **0 unread, 7
awaiting-approval** against a batch trigger of 30 — both `C-TECH-061` rungs green.

```
CLUSTER: concurrent-session-same-file-write  (x2: IMP-0539, IMP-0541)
Altitude:  CLASS — second resource to hit a race the first resource already mechanised
Ladder row: "second instance of the same class_instance_of → generalise" +
           "a tool could catch it mechanically"
Becomes:   scripts/allocate-review-number.py (F1) + agents/improvement-agent.md Outputs row (F2)
Retires:   nothing — the review filename had no allocator to retire
Cites:     IMP-0539, IMP-0541, and IMP-0080's six-instance chain as the precedent
Residual:  O_EXCL is per-filesystem; two machines syncing one SharePoint path are not
           coordinated. Same residual allocate-improvement-id.py records for flock.
```

```
CLUSTER: finding-diagnosis-unverified  (x1: IMP-0540)
Altitude:  INSTANCE — no change. IMP-0540 corrects IMP-0539 and is load-bearing as evidence,
           not as a defect needing its own fix
Ladder row: "one instance, specific, no general mechanism" → stays a log note
Becomes:   nothing. Its correction is honoured in §4.2 — this review is premised on
           "near-miss", not on IMP-0539's withdrawn "silently overwritten"
Retires:   nothing
Cites:     IMP-0540
Residual:  the general class (a lead-agent diagnosis logged without checking the dispatched
           agent's own account) has prior members and no mechanical home; nothing here
           changes that.
```

```
CLUSTER: gate-cannot-fail  (x1: IMP-0542)
Altitude:  INSTANCE, promoted one rung — an agent that had read this exact pattern in the
           digest committed it anyway, which is the ladder's "had the information and still
           did the wrong thing" row
Ladder row: "an agent had the information and still did the wrong thing" → agent-file edit
Becomes:   agents/improvement-agent.md corpus-measurement section (F3)
Retires:   nothing
Cites:     IMP-0542, IMP-0007
Residual:  nothing reads a review document's asserted measurements back against the commands
           that produced them, and nothing can. Step 8 plus a human reading the draft stays
           the only control.
```

```
CLUSTER: groups-table-stale-on-an-open-decision  (x1: new, logged by this review)
Altitude:  INSTANCE — first occurrence, no change to any rule
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:   §2.4 of this document plus one new log entry; no rule change
Retires:   nothing
Cites:     the design document's own Group 4 row vs WS-A's resolved mechanism
Residual:  no gate can check a markdown groups table against a mechanism decided later.
```

**States excluded, per the no-silent-caps rule.** `awaiting-approval`: **0**. `already-fixed`: **0**.
`reviewer-deferred`: **115**, left alone as reviewed deferrals — except `IMP-0542`, processed here
because its `revisit_when` fired. `APPLIED` (419) and `REJECTED` (2) not read; the digest carries them.

---

## 6. Retirement candidates considered

The obligation at [`agents/improvement-agent.md#L373`](../../agents/improvement-agent.md#L373) is to
name a candidate or state that none was found. Derived, not typed:
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10 retired**; `grep -rh '^| C-'` → **82
live**.

**One candidate was examined and rejected.** Had WS-H been adopted, both
[`agents/improvement-agent.md#L3`](../../agents/improvement-agent.md#L3) ("no lower tier") and
[`config/models.yml#L216`](../../config/models.yml#L216) ("Always. This agent has no lower tier.") would
have been retired as false. WS-H is withheld on measurement, so both statements remain true and
**neither is retired.** No constraint row in `constraints/` is touched by this review, and none was
found stale in the areas it reads.

---

## 7. Anti-bloat and scope accounting

| Limit | This review |
|---|---|
| Max 3 new constraints | **0 proposed** |
| Every new constraint cites its ids | n/a — none |
| Retirement considered | Yes — §6, one candidate examined, rejected with a reason |
| `Verify By` mechanically executable | F1 ships with `--selftest`; A1's verification is a live fixture dispatch (§2.3) and is **not** claimed until it runs |
| Files this review touches | `.claude/hooks/protect-system-rules.py` (new), `.claude/settings.json`, `agents/improvement-agent.md`, `config/models.yml`, `scripts/allocate-review-number.py` (new) |
| Files it was expected to touch and does not | `scripts/generate-subagents.py`, `.claude/agents/*.md` — see §2.1 |

`ls scripts/verify-*.py | wc -l` → **54**, unchanged: F1 is an `allocate-*`, not a `verify-*`, so the
`improvement-agent-verify-script-count` entry in
[`scripts/derived-counts-registry.json#L114`](../../scripts/derived-counts-registry.json#L114) needs no
update.

---

## 8. Routed work and coordination — read before approving

| Item | Owner | Why it is not fixed here |
|---|---|---|
| **A1/A2 must not be applied while the WS-E dispatch is live** | the dispatcher | Both write `.claude/settings.json`. §2.4. This is the same hazard the groups table exists to prevent, arriving through a gap in how the table was computed. |
| **WS-E can be told what this review confirmed** | the dispatcher | `permissions.deny` accepts `Agent(Explore)`, `Agent(Plan)`, `Agent(general-purpose)` — so WS-E's exclusion of generic built-ins **is** mechanically enforceable, contrary to its own hedge at [L161](2026-08-31-capability-design-agent-system-optimisation.md#L161). There is no *allowlist* form; deny-by-name only. Relayed as information; **not** actioned here, because it is WS-E's file. |
| **The V0→V1 fixture dispatch for A1** | this review, at apply time | §2.3. It cannot run before the hook exists. |

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-9.md

Findings processed: 5 NEW  →  4 clusters
Regression check:   2 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 2 gates/scripts, 0 skill/knowledge edits,
                    3 agent-file edits, 0 retirements
Altitude calls:     2 generalised or promoted from instance, 2 left as notes
Digest:             will regenerate — 5 lessons, 1 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied record — 2026-09-01

Step 8 re-verification ran before anything was written. `verify-improvement-log.py --check` exit 0
(545 entries); **no `corrects` warning names any of this review's five findings.** Two premises were
re-measured and both held: `TRIGGER_BATCH = 30` at
[`scripts/verify-improvement-log.py#L211`](../../scripts/verify-improvement-log.py#L211), and the
`agents/improvement-agent.md` anchors at the Outputs row and the corpus-measurement heading were
byte-exact. The only uncommitted change to that file was review 8's own 10→30 threshold edit at
line 60 — not a concurrent write.

| # | Change | File | Verification |
|---|---|---|---|
| **F1** | `allocate-review-number.py` — claims `<date>-improvement-review[-N].md` by `os.open(O_CREAT\|O_EXCL)`. No lock: here the claim and the create are one operation | [`scripts/allocate-review-number.py`](../../scripts/allocate-review-number.py) (new) | `--selftest` **exit 0, 16 assertions**, including **12 concurrent claims yielding 12 distinct numbers** — the fixture fails if `O_EXCL` is removed. Real corpus via `--peek`: returns `-10` for 2026-08-31 (1–9 exist) and `-4` for 2026-09-01 (1–3 exist); the neighbouring capability-design document is correctly not counted |
| **F2** | Outputs row names the command; new section requires claiming at **step 6**, not gate time | [`agents/improvement-agent.md#L406`](../../agents/improvement-agent.md#L406) | Needle present |
| **F3** | New subsection: `;` not `&&`, label every measurement, plus never read an exit status through a pipe | [`agents/improvement-agent.md`](../../agents/improvement-agent.md) corpus-measurement section | Needle present |
| **H1** | The WS-H measurement recorded in the `rationale` **string** | [`config/models.yml#L203`](../../config/models.yml#L203) | YAML parses; `rationale` 2,684 chars; `generate-subagents.py --check` **exit 0, 18 files current** — confirming the rationale is human-facing and does not propagate, as intended |

**Bookkeeping, incremental.** `IMP-0539`, `IMP-0540`, `IMP-0541` closed `APPLIED` as F1+F2 landed;
`IMP-0542` closed as F3 landed; `IMP-0546` left `NEW` with a `deferred_reason` and a `revisit_when`
(first instance, `proposed_change` type `none` — there is no rule change to close against). Queue
after: **0 unread, 3 awaiting-approval**, validator exit 0.

**Two needles deliberately do not point at prose this review wrote** (`IMP-0208`): `IMP-0539`'s
points at `os.O_CREAT | os.O_EXCL` and `IMP-0540`'s at `def claim(` — the mechanism, not a sentence
about it.

**One withdrawn claim carried forward, not quietly dropped.** `IMP-0539`'s *"silently overwritten …
left no file on disk"* is marked WITHDRAWN in its own `applied_by`, per `IMP-0540`. The change is
premised on the near-miss.

## 11. Withheld — WS-A, all three changes

The approval scoped WS-A to **future work only**: *"PreToolUse hook, nothing applied to
`.claude/settings.json` or the generator this round."* Accordingly:

| Change | Status | Why |
|---|---|---|
| **A1** `.claude/hooks/protect-system-rules.py` | **WITHHELD** | Scoped out by the approval |
| **A2** `hooks` block in `.claude/settings.json` | **WITHHELD** | Scoped out by the approval. **`.claude/settings.json` was never opened for writing by this dispatch** |
| **A3** enforcement sentence at [`agents/improvement-agent.md#L12`](../../agents/improvement-agent.md#L12) | **WITHHELD** | A3's approved wording records that the rule *"is now enforced by A1"*. With A1 withheld that sentence is **false**, and applying approved wording whose premise has been removed is the `IMP-0405` shape. Withheld rather than silently reworded — the enforcement wording is what was approved |

**The §2.4 hazard resolved without action.** WS-E completed and wrote `.claude/settings.json` at
12:09:57 (a `permissions.deny` block with four `Agent()` entries, alongside the original 11 allow
entries). Because A1/A2 were withheld, the predicted collision did not occur. Verified by fresh read
after WS-E landed: `git diff --stat .claude/settings.json` shows **+6 lines, all WS-E's**.

**WS-A's evidence level is unchanged at V0 for the hook mechanism.** One half did rise: the live
agent roster directly confirms per-subagent tool scoping is real and is **tool-name granularity with
no path expression** — project agents show *All tools*, `statusline-setup` shows *Read, Edit*, and
`Explore`/`Plan` show *All tools except … Edit, Write, NotebookEdit*. That is observation, not
documentation. **The `agent_type`-in-`PreToolUse` half remains unexecuted**, and §2.3's rule stands:
if the hook does not fire, or `agent_type` is absent in practice, A1 and A2 are withdrawn and
reported rather than shipped on a passing selftest.

**WS-E's own hedge is now disproved, and it landed the enforcement.** WS-E doubted a mechanical form
existed ([L161](2026-08-31-capability-design-agent-system-optimisation.md#L161)); `permissions.deny`
accepts `Agent(<name>)`, and the four generic agents are now denied.
