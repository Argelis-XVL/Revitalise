# Improvement Review — 2026-09-01 (5)

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`~~ → **APPLIED 2026-09-01.** The one proposed change is
on disk and WS-G is withheld in full. See section 10 for the applied record, including one field
correction made openly and the reason for it.
**Scope:** WS-G only, from
[the capability design document](2026-08-31-capability-design-agent-system-optimisation.md#L189).
`wbs:system`, non-billable ([`C-COM-002`](../../constraints/commercial/commercial-constraints.md#L35)).
**Filename:** claimed at draft start with
[`scripts/allocate-review-number.py`](../../scripts/allocate-review-number.py#L1), not computed.

---

## 1. Summary

**WS-G should not be built, and the test it asked for is what shows why.** Registering the three
skills natively works — a Task-tool-dispatched subagent resolved a probe `SKILL.md` and returned
its canary, twice out of twice — but WS-G also requires *removing* the hand-written "Load X" prose,
and that half converts a mandatory instruction into an optional one: across three trials where a
subagent was handed a task squarely inside a skill's trigger description and no prose telling it to
load anything, it invoked the skill **zero times**, and in two of those trials it reached for the
prose path instead.

What is waiting on you: approve the single one-paragraph rule in section 5 that records why this
class of substitution is off the table, or tell me to leave even that out.

---

## 2. Premises re-measured before drafting

The dispatch asked me to check WS-G's own premises rather than trust them. Two of three fail.

| WS-G's premise | Measured 2026-09-01 | Verdict |
|---|---|---|
| "`.claude/skills/` is empty" | The directory **does not exist**. `.claude/` holds `agents/`, `worktrees/`, `settings.json`, `settings.local.json` | Effectively true, immaterial |
| "`how-to-verify-a-platform-contract.md` (referenced from 10 files)" | **7** files under `agents/`; **60** files repository-wide excluding `.git`. Commands: `grep -rl 'how-to-verify-a-platform-contract' agents/ \| wc -l` and the same over `.` | **Wrong.** No population gives 10 |
| "hand-written 'Load X' prose duplicated inside every agent file" | Not duplication. They are **conditional, point-of-use triggers** bound to distinct moments, and several are bound to numbered sections of a 572-line file | **Wrong, and this is the load-bearing one** |

The third row is the one that decides the workstream, so here is the evidence rather than a
summary of it. These are not one repeated line:

- [`agents/build-agent.md#L216`](../../agents/build-agent.md#L216) — "before building"
- [`agents/pipeline-agent.md#L298`](../../agents/pipeline-agent.md#L298) — "before any deployment stage"
- [`agents/architect-agent.md#L172`](../../agents/architect-agent.md#L172) — "before running the constraint check"
- [`agents/development-agent.md#L64`](../../agents/development-agent.md#L64) — at the point of hand-authoring a platform artefact, and at
  [`#L221`](../../agents/development-agent.md#L221) the same skill's sweep procedure only
- [`agents/build-agent.md#L125`](../../agents/build-agent.md#L125) — one numbered section of that skill, not the file

A native skill description is a topical trigger. It can say *what a skill is about*; it cannot say
*perform this before the constraint-check block of your gate output*, and it cannot address one
numbered section of a 572-line document.

---

## 3. The test WS-G asked for, and what it showed

WS-G names one decision it could not make: whether native Skill-tool discovery composes with this
project's Task-tool dispatch model, and it says to test on one skill first. I tested it by
executing, not by reading — two temporary probe skills with canary strings, four fresh `claude -p`
sessions spawned from Bash, and the probes deleted afterwards.

| Test | Method | Result |
|---|---|---|
| Does a fresh top-level session discover a project skill? | Fresh `claude -p`, asked to list its skills | **Yes** — probe present |
| Does a **Task-dispatched project subagent** resolve and load it? | Fresh session dispatching a `config-agent` subagent, told to invoke the probe | **Yes** — canary returned verbatim, Skill call succeeded, no error |
| Does a subagent invoke it **unprompted**, when the task matches the description and no prose says to load it? | 3 trials, `config-agent` subagent, realistic reviewer-report task, canary marker planted in the skill body | **No — 0 of 3.** In 2 of 3 the agent cited the *prose* path instead |
| Does the tool grant get in the way? | Read the generated subagent frontmatter | No — no `tools:` key in any of the 18 files, so all receive the Skill tool |

**The third row is the finding.** WS-G's stated mechanical verification is *"each agent file's own
activation step still resolves to the same content by a different path; no agent's behaviour
changes, only how the file is discovered."* That clause would have **passed** — the content does
still resolve when asked for. It measures the wrong property. The property that changes is whether
it resolves *when nobody asks*, and that went from guaranteed to zero.

This project already paid for that distinction once. The principle is written down at
[`agents/improvement-agent.md#L646`](../../agents/improvement-agent.md#L646): *"A rule in
`CLAUDE.md` that appears in no activation sequence is a rule that depends on remembering."* It is
there because an agent that knew the reporting rule wrote a long report without loading the file,
and the reviewer had to ask why.

One further defect, independent of invocation: a `SKILL.md` wrapper must either duplicate the
canonical text — a second copy of 1,044 lines across three skills, free to drift — or point at
`skills/X.md`, in which case the agent performs exactly the same read as today and nothing was
saved.

---

## 4. Clusters

```
CLUSTER A: WS-G's premises do not survive measurement  (x2: IMP-0553, IMP-0554)
Altitude:  CLASS for the general lesson, WITHHOLD for the workstream. IMP-0553 is a stale count
           (class finding-diagnosis-unverified); IMP-0554 is the substitution itself
           (class output-shape-defeats-the-reader, the same class as the report-format failure
           the activation-sequence principle was written for).
Ladder row: "an agent had the information and still did the wrong thing" -> a skill edit.
           NOT a constraint: there is no value to assert on, only the shape of a proposal, and
           this repository has measured phrase-based gates over prose at 48-100% false five
           times (IMP-0422, IMP-0428).
Becomes:   one paragraph in skills/how-to-promote-a-finding.md's "What is not evidence for
           promotion" section. WS-G itself is withheld in full - no .claude/skills/ tree, no
           agent-file edits, nothing removed.
Retires:   nothing in constraints/. WS-G's own requirement is what this review retires, and it
           is recorded as WITHHELD rather than deferred, because its premise was measured false
           rather than left unmeasured.
Cites:     IMP-0553, IMP-0554
Residual:  the removal half is what was measured false. Adding the wrappers ALONGSIDE the prose
           is harmless and was not tested for value, only for mechanism - it would put 23 skill
           descriptions into every dispatch's context for no measured benefit, so it is not
           proposed either. If a future dispatch wants it, the mechanism is proven and the
           removal is the part that must stay untouched.
```

```
CLUSTER B: harness behaviour settled by execution  (x1: IMP-0555)
Altitude:  capability, not defect. Nothing failed.
Ladder row: "a capability was established and could be lost again" -> a capability lesson in
           the digest.
Becomes:   the log entry and the regenerated digest. No file change.
Retires:   nothing.
Cites:     IMP-0555
Residual:  the elective-invocation figure is 0 of 3 on one model tier, not a general law. It is
           enough to disprove "no behaviour changes"; it is not enough to claim a rate. A
           dispatch that ever wants to rely on elective invocation must re-measure it.
```

---

## 5. The one change proposed

**File:** [`skills/how-to-promote-a-finding.md#L134`](../../skills/how-to-promote-a-finding.md#L134),
in the "What is not evidence for promotion" section, after the existing ordinary exclusions.

```markdown
- **A proposal whose mechanism is that a MANDATORY step becomes an ELECTIVE one.** An
  instruction an agent is told to execute and an affordance an agent may choose to use are
  not the same guarantee, and a proposal that swaps one for the other is usually presented as
  a discovery improvement rather than as a removal.

  Measured 2026-09-01, on the native Claude Code Skills proposal in
  `docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md`: a
  Task-dispatched subagent asked to load a registered skill did so 2 of 2 times, and a
  subagent given a task squarely inside that skill's trigger description with no prose
  telling it to load anything did so **0 of 3 times** - reaching for the hand-written "Load X"
  line in its own agent file in 2 of the 3. The proposal's own mechanical verification
  ("no agent's behaviour changes, only how the file is discovered") would have passed, because
  it measured whether the content still resolves when asked for rather than whether it
  resolves when nobody asks.

  **So: where a proposal claims no behaviour changes, name the property that would differ if
  it were wrong, and measure THAT.** Additive registration is fine; deleting the activation
  step is the harm. This is the same principle as `agents/improvement-agent.md`'s
  "a rule that appears in no activation sequence is a rule that depends on remembering".
```

Cited by: `IMP-0554`, with `IMP-0070` as the prior instance of the cost.

**Why prose and not a gate.** The thing to detect is a proposal's intent, which no regex reads,
and the phrase-based approximation is the instrument this repository has measured five times at
48–100% false. The file's own "What is not evidence for promotion" section already carries one rule
of exactly this kind for exactly this reason.

---

## 6. Regression check

The previous review is [WS-E's](2026-09-01-improvement-review-3.md#L364), applied earlier today
with three changes.

| Question | Answer |
|---|---|
| Has any finding in that class appeared since? | No. And better than that — **its change was observed working, live, by accident.** My first probe attempted a `general-purpose` subagent dispatch and a fresh session refused it: *"The Agent tool with subagent_type general-purpose has been denied by your project permission settings."* That is an independent re-observation of [`.claude/settings.json#L5`](../../.claude/settings.json#L5) at V5 |
| Prose or mechanical gate? | Mechanical — a harness-level `permissions.deny` matcher, which is why it could be observed refusing rather than inferred |
| Did the gate run? | Yes, unprompted, against a dispatch I did not intend as a test of it |
| Did closure evidence match the level the defect was visible at? | Yes. That review closed on an executed refusal, not on a document |

Recorded in `IMP-0555` alongside the skills measurement.

---

## 7. Anti-bloat and scope accounting

| Limit | This review |
|---|---|
| Max 3 new constraints | **0 proposed.** Nothing here has a value to assert on |
| Every constraint cites its ids | n/a — none proposed |
| Retirement considered | Checked. **No constraint row is a retirement candidate** from this cluster; 10 rows are already retired against 82 live (`grep -rh '^\| ~~C-' constraints/ --include='*.md' \| wc -l`). What this review retires is WS-G's requirement itself |
| Scripts added | **0.** 54 `verify-*.py` scripts, unchanged |
| No silent caps | See below |

**States excluded from this review's scope, and why.** The log holds 124 `NEW` entries. I read
only what this dispatch is scoped to. 117 are `reviewer-deferred` — left alone and reported as
deferred, of which one (`IMP-0274`) still names no `revisit_when`. 0 are `awaiting-approval` from
other reviews. **4 are `unread` and belong to other workstreams' dispatches: `IMP-0549`,
`IMP-0550`, `IMP-0551`, `IMP-0552`.** I did not process them.

**But two of those four matter to this review's altitude, and they are unclaimed.** `IMP-0550` and
`IMP-0551` are both `finding-diagnosis-unverified` against *this same design document* — a
workstream premise written from a commit subject line, and a threshold computed against the wrong
denominator. `IMP-0553` makes **three instances of the same class against one document**. The
altitude rule says a third instance is not answered with a third instance patch, so the correct
output is one change covering how this design document's premises are treated — and that change
belongs to whichever dispatch processes those two entries, not to this one, which is scoped to WS-G
and must not write into another workstream's territory. **Routed, not fixed — this review did not
process either of them, and neither is in scope in this document.** Re-measure before acting on it:
all three were appended today and any of them may be superseded.

---

## 8. What you need to decide

**Approve the one-paragraph rule in section 5, or drop it and take the withhold alone?**

**Problem** — WS-G is disproved and will be withheld either way, but nothing currently stops the
same substitution being proposed again from the same reasonable-looking premise.
**Suggested fix** — apply the single paragraph; it costs one screen of one skill file and cites a
measurement rather than an opinion.
**What happens if you don't** — the withhold is recorded only in this review and in the log, and
the next agent reading WS-G will re-run the same four probe sessions to reach the same answer.
[`skills/how-to-promote-a-finding.md#L134`](../../skills/how-to-promote-a-finding.md#L134)

---

**Verification executed:** 5 fresh `claude -p` sessions (1 top-level discovery, 1 subagent
discovery, 3 elective-invocation trials — one session per trial); `verify-improvement-log.py
--check` exit 0 over 552 entries; `verify-review-document.py --only` exit 0 on this document;
`verify-doc-line-links.py` exit 0; `generate-known-failure-modes.py --check` exit 0 after
regenerating for the three appended findings, per the Learning Rules' validator-then-generator
order. Both probe skill directories were created and deleted, with `git status .claude/` confirming
only the pre-existing `settings.json` modification remains, and `git diff -U0` on the log confirming
the stamping rewrite touched no line outside today's appends.

**Not verified:** whether native registration composes with `.claude/agents/` files that DO carry a
scoped `tools:` key — none currently do, and WS-A was redirected, so the question is hypothetical
today and would need re-testing if tool scoping ever lands. The elective-invocation rate was
measured on one model tier only. No claim is made about a rate; the claim is only that it is not
guaranteed.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review-5.md

Findings processed: 3 NEW  →  2 clusters
Regression check:   3 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as notes
Withheld:           WS-G in full — premise measured false, not merely unmeasured
Digest:             ALREADY REGENERATED at draft time (552 entries, 550 lessons) because three
                    findings were appended — 1 new capability lesson, 0 new recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied record — 2026-09-01

`APPROVE IMPROVEMENTS` received, approving the draft as written: WS-G withheld in full, one
paragraph landing.

### Re-verification performed before applying (step 8)

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **OK, exit 0**, 552 entries, max id 555 — unchanged from draft time. No entry appended in the interval, and no `corrects` field anywhere names any of the three this review processed |
| Routed item re-measured | `IMP-0550` and `IMP-0551` are **still `unread` and still unclaimed**, and this review did not process them — they are out of scope here. Not shipped, not decided by the reviewer, not superseded, so the routing stands and is handed on as written |
| WS-G taken by another review since? | No. Only the design document, review 7's non-scope list, and this document mention it |
| Target file changed since the draft? | No — `skills/how-to-promote-a-finding.md` unmodified since 2026-08-31 22:10, and its section 4 heading is still at L134 |
| Derived counts | 10 retired / 82 live constraint rows, 54 `verify-*.py` scripts — all unchanged, and this review adds none of any kind |
| `.claude/skills/` still absent? | Yes — confirmed absent before and after the re-observation probe |

### Changes applied (1)

| # | File | What |
|---|---|---|
| 1 | [`skills/how-to-promote-a-finding.md#L197`](../../skills/how-to-promote-a-finding.md#L197) | New final bullet in section 4: *"A proposal whose mechanism is that a MANDATORY step becomes an ELECTIVE one"*, carrying the 2-of-2 versus 0-of-3 measurement and the reason the proposal's own verification clause would have passed |

### Withheld, and it is the larger half of this review

**WS-G is not built.** No `.claude/skills/` tree was created; no `"Load X"` line was removed from
any agent file; no agent file was edited at all. The premise was measured **false**, not merely
left unmeasured, which is why this is recorded as withheld rather than deferred.

### One field correction, made openly

`IMP-0554` was appended with `observable_at: "V5"` and was corrected to `"n/a"` at application
time, with the reason recorded in a `field_correction` field on the entry itself.

**Why it is recorded rather than just fixed.** `V5` described the level of the *measurement* this
review executed — five live sessions — not the level at which the *defect* was observable, and
`observable_at` means the latter. The defect is a design document's verification clause measuring
the wrong property; it was caught before anything was built, so it has no runtime symptom. **The
correction also removes the reobservation requirement that `verify-improvement-log.py` enforces at
V2 and above, and a field change that clears a gate must never be invisible** — so it is stated
here, in the entry, and in this sentence rather than left for someone to notice in a diff.

### Disposition of the three findings

| Finding | Disposition | Why |
|---|---|---|
| `IMP-0553` | **Left `NEW`** with a `deferred_reason` and a `revisit_when` | It proposed no change of its own, and its correct remedy is at class altitude. Answering it alone would be the third instance patch the altitude rule forbids. Left open deliberately so the dispatch that takes `IMP-0550`/`IMP-0551` sees three instances, not two — neither of those two is processed here, and both are out of scope in this document. A `deferred_reason` is the gate's own named discharge, so this parks honestly without holding a trigger open |
| `IMP-0554` | **`APPLIED`**, needle on the new bullet's text | The rule that prevents recurrence is on disk |
| `IMP-0555` | **`APPLIED`**, with a genuine `reobserved` record | See below |

### The reobservation was re-run, not asserted

`IMP-0555` is a V5 capability entry, and closing one on a prose needle is exactly the shape
`IMP-0208` was wrongly closed on. So the original reproduction step was **executed again** at
application time: the probe skill was re-created, a fresh `claude -p` session dispatched a
`config-agent` subagent via the Agent tool, and the subagent reported `PROBE-PRESENT`, a successful
Skill call, and the canary string verbatim. The probe was deleted again afterwards, with
`git status .claude/` confirming only the pre-existing `settings.json` modification remains.

Note what that record says: **capability confirmed present**, not *symptom gone*. A capability entry
has no symptom to lose, and the record says so rather than borrowing the wording of a defect closure.

### Verification executed at application time

`verify-improvement-log.py --check` exit 0 (552 entries, 122 NEW / 428 APPLIED / 2 REJECTED, the
same 5 pre-existing warnings and no new ones); `verify-review-document.py --only` exit 0;
`verify-doc-line-links.py` exit 0; `generate-known-failure-modes.py --check` exit 0 after the final
regeneration. The disposition was **simulated on a scratch copy of the log and gated there before
the real file was touched**, and the real log was confirmed byte-identical to its pre-simulation
backup with `diff -q` before applying.

**Not verified:** the elective-invocation figure remains 0 of 3 on one model tier. It is enough to
disprove *"no behaviour changes"*; it is not a rate, and this review makes no claim that it is one.
