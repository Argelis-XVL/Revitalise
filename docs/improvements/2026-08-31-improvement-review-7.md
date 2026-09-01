# Improvement Review — 2026-08-31 (7)

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability, per [`agents/improvement-agent.md#L64`](../../agents/improvement-agent.md#L64)
**Authorising artefact:** [`docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md`](2026-08-31-capability-design-agent-system-optimisation.md) — workstreams **WS-D**, **WS-J**, **WS-L** (Parallel-safe dispatch Group 1)
**Findings processed:** 2 `unread` (`IMP-0537`, `IMP-0538`) → 2 clusters
**Gate:** `APPROVE IMPROVEMENTS`
**wbs:** system (non-billable, `C-COM-002`)
**Status:** **APPLIED 2026-08-31** — all four changes are on disk; `IMP-0537` and `IMP-0538` are
closed with `deferred_reason` + `revisit_when` (not `APPLIED`, see §7). Applied under
`APPROVE IMPROVEMENTS` after the step-8 re-verification recorded in §2.1 and §9.

---

## 0. Headline — three of this dispatch's four assigned requirements are withdrawn on measurement

The scope's own premises were measured before anything was drafted, per
[`agents/improvement-agent.md#L152`](../../agents/improvement-agent.md#L152) ("where the assertion is
about a script's BEHAVIOUR, EXECUTE it"). Three did not survive:

| Assigned requirement | Measured result | Disposition |
|---|---|---|
| WS-D req. 1 — tier-mismatch check against `GATE_RECEIVED` model identity | **0** of 105 `GATE_RECEIVED` lines in `logs/routing.log` carry any model identity | **WITHHELD** — the gate could never fire |
| WS-D req. 1, `lead-agent` half (the doc's own open decision) | `lead-agent` is never dispatched as a subagent: its 2 `ROUTED_TO:lead-agent` lines are self-bookkeeping, not dispatches (§2.1) | **STRUCTURAL — confirmed unenforceable.** §2.1 |
| WS-D req. 2 — mechanical stall gate | The gate **already exists and already runs on every build**, reporting 31 findings nobody reads | **REDIRECTED** — §2.2 |
| WS-J — "every resume attempt has failed" | 13 resume attempts, **1 incident** recording 3 failures; ≥6 with positive evidence of success | **NARROWED** — §3 |

Only **WS-L** survived its premise intact, and it lands one rung lower than the design document
proposed, for the reason in §4.

**Constraints proposed: 0 of 3.** WS-D and WS-L each budgeted 1; neither is spent, and §5 says why.

---

## 1. Scope and state accounting (no silent caps)

`python3 scripts/verify-improvement-log.py --check` — run at activation, before any finding was
read, per [`agents/improvement-agent.md#L97`](../../agents/improvement-agent.md#L97):

```
535 entries (114 NEW, 419 APPLIED, 2 REJECTED), 5 warning(s)
NEW breakdown: 2 unread, 0 awaiting-approval, 112 reviewer-deferred, 0 already-fixed
```

- **Processed:** `IMP-0537`, `IMP-0538` — the only two entries in state `unread`, both named in the
  dispatch brief, both read in full.
- **Excluded — 112 `reviewer-deferred`:** each carries a `deferred_reason` a human accepted. Not
  re-derived, per [`agents/improvement-agent.md#L104`](../../agents/improvement-agent.md#L104).
- **Excluded — `APPLIED` / `REJECTED`:** the digest carries their lessons.
- **The gate's 5 `corrects` warnings** (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`, `IMP-0437`)
  name no finding this review acts on. Checked, not inherited.

**Workstreams in the design document NOT touched by this dispatch:** WS-A, WS-B, WS-C, WS-E, WS-F,
WS-G, WS-H, WS-I, WS-K, WS-M. Groups 2–8 are separate dispatches.

### The one scope collision this dispatch could not resolve

`IMP-0537`'s own `proposed_change` targets **`agents/lead-agent.md`**, and so does the next rung
that [`agents/WORKFLOW.md#L202`](../../agents/WORKFLOW.md#L202) already names for this class. That
file belongs to **Groups 2 and 3** (WS-I, WS-E), which the design document sequences as separate,
possibly concurrent dispatches. Editing it here is exactly the two-live-writers hazard the design
document's own preamble forbids.

**So the lead-agent half of `IMP-0537` is deferred to Group 2, named, not silently dropped.** It is
recorded as a `deferred_reason` with a `revisit_when` on the entry (§7), and Group 2's dispatch
brief should carry it.

---

## 1b. Regression check — did the last review's change work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 6 change 1 — `agents/architect-agent.md` gains a "run `verify-design-doc-claims.py` before your gate output" step | 2026-08-31 | `gate-fires-on-nothing` (`IMP-0428`, `IMP-0535`) | **No** — no finding in that class since | Too recent to credit. Applied hours ago; the next architect-agent dispatch is its first real test. Recorded, not claimed as working. |

**The audit that matters for this dispatch is the one on `dispatched-agent-stalls-silently`**, and
it is the reason cluster A exists:

| Prior change | Applied | Prose or gate? | Recurred since? | Verdict |
|---|---|---|---|---|
| `IMP-0357` / review 33 — WORKFLOW.md fifth case, "recognise the stall signature" | 2026-08-28 | **prose** | Yes — `IMP-0520` | Wrong altitude |
| `IMP-0520` / review 48 — WORKFLOW.md L177-203, "preempt it in the dispatch prompt" | 2026-08-31 | **prose** | Yes — `IMP-0537`, **the same day** | Wrong altitude, second time |
| Review 27 change 6 — `scripts/verify-routing-reconciliation.py` + the `routing-reconciliation` build step | ~2026-08-25 | **gate** | The class recurred, and **the gate DID fire** — it reports the 19:32 pipeline-agent dispatch among 31 unreconciled | **Mis-scoped, not broken.** See below |

The third row is the one the Regression Check table in
[`agents/improvement-agent.md#L356`](../../agents/improvement-agent.md#L356) asks about directly:
*"If yes after a gate — did the gate run?"* It ran, on every build, and it caught this. What it
cannot do is prevent the stall — it is a **post-hoc reconciliation** gate, and the stall happens
inside a live session no gate can reach. Its finding then exits 0 under `--warn-only` and is read by
nobody, which is why two prose fixes were written for a class that already had a working detector.
That is a `gate-scope-mismatch`, and §2.2 is its remedy.

---

## 2. Cluster A — `dispatched-agent-stalls-silently`

```
CLUSTER: dispatched-agent-stalls-silently  (x5: IMP-0291, IMP-0300, IMP-0357, IMP-0520, IMP-0537)
Altitude:  CLASS — 5th instance, 2nd since the prose fix of 2026-08-31
Ladder row: "second instance -> generalise"; the mechanical home already exists
Becomes:   two corrections to agents/WORKFLOW.md (changes 1 and 2). No new script.
Retires:   the "mechanical half is deliberately not proposed here" paragraph, WORKFLOW.md L145-149
Cites:     IMP-0537 (design doc WS-D)
Residual:  the dispatch-prompt checklist itself remains prose in a file this dispatch must
           not touch (agents/lead-agent.md, Group 2). Nothing here closes that.
```

### 2.0 The instance count in the brief is wrong, and it is wrong three times over

The design document says the class *"has recurred **8 times**"*
([WS-D](2026-08-31-capability-design-agent-system-optimisation.md), Problem part 2). `IMP-0537`'s
own text calls itself *"the class's 8th recorded instance."*
[`agents/WORKFLOW.md#L179`](../../agents/WORKFLOW.md#L179) says *"the class at x7."*

**Measured against the log: 5.**

```
IMP-0291  2026-08-25  APPLIED      IMP-0520  2026-08-31  APPLIED
IMP-0300  2026-08-25  APPLIED      IMP-0537  2026-08-31  NEW
IMP-0357  2026-08-26  APPLIED
```

[`logs/known-failure-modes.md#L55`](../../logs/known-failure-modes.md#L55) — the generated digest,
the one count in this system nobody hand-types — agrees: **x5**.

This does **not** change the conclusion. Five instances with two failed prose fixes is past the
altitude rule's threshold either way. But three documents carry a hand-typed count that drifted
from its generated source, which is `hand-maintained-count-drifts-from-source` (x30, the 4th-largest
class in the digest) landing inside the very paragraph that argues about altitude. Change 2 fixes
the one instance in a file this dispatch owns.

### 2.1 The `lead-agent` tier check is STRUCTURALLY unenforceable — the design document's open decision, answered

The design document asks this explicitly and says to answer it plainly rather than ship a gate that
can never fire. The answer is **no, it cannot be enforced**, for two independent reasons, both
measured:

1. **`lead-agent` is never dispatched as a subagent.** `grep -c 'ROUTED_TO:lead-agent'
   logs/routing.log` → **2**, against 208 `ROUTED_TO` lines — and reading both is what settles it.
   [`routing.log:66`](../../logs/routing.log#L66) and [`routing.log:67`](../../logs/routing.log#L67)
   are dated 2026-08-17 and 2026-08-18 and read `ROUTED_TO:lead-agent (design, no route existed)`
   and `ROUTED_TO:lead-agent (design)`. Both are lead-agent **recording that it handled a capability
   request itself because no routing row covered it** — a bookkeeping notation, not a Task-tool
   dispatch. Neither spawned a pinned invocation, so neither carries or could carry a resolved model
   identity. `lead-agent` remains the root conversation loaded via `CLAUDE.md`; a script cannot
   observe the model a live conversation runs on. This is a property of the harness, not a gap in
   the tooling.

   > **Correction, made at application time (step 8).** The draft of this section asserted **0**
   > such lines. That figure was never measured: the shell command that produced it was `&&`-chained
   > after a `grep -c` which matched nothing, exited 1, and aborted the chain — so the lead-agent
   > count never ran and its *absent* output was recorded as a zero. This is the `IMP-0007` pattern
   > (*"the `! grep … && echo` gate pattern turns EVERY grep failure into a PASS"*),
   > [`logs/known-failure-modes.md#L85`](../../logs/known-failure-modes.md#L85), committed by the
   > agent that had read that line at activation. Logged as `IMP-0542` — the id was re-read from the
   > log's current maximum at append time, not reserved at draft time, because two other sessions
   > appended `IMP-0540` and `IMP-0541` while this review sat at its gate (`IMP-0312`, `IMP-0080`).
   > **The withhold in §0 and the
   > conclusion of this section are unchanged** — reason 2 below is the load-bearing one and
   > re-measures identically — but the sentence was wrong and is corrected rather than quietly kept.

2. **Even for agents that *are* dispatched, the identity is not recorded.** Of **105**
   `GATE_RECEIVED` lines, **0** name any model or tier — re-measured at application time, unchanged
   from the draft's finding though the denominator moved from 103 as dispatches closed. Tier appears
   on 43 `ROUTED_TO` lines — the *dispatcher's stated intent*, never the *resolved identity* — which
   is the wrong side of the comparison the requirement asks for.

So the check as specified compares a value that exists against one that never does. **WS-D
requirement 1 is withheld in full.** The additive alternative — start recording resolved model
identity on `GATE_RECEIVED` lines so the corpus exists in six months — is a convention change for
the reviewer, not a defect fix, and is offered in §6 rather than taken.

### 2.2 WS-D requirement 2 asks for a gate that already exists, runs on every build, and is ignored

The requirement is *"a **pre-dispatch** check … that scans the dispatched agent's own **final
message** for the stall signature."* Two problems, and the second is the useful one.

**First, the requirement is self-contradictory as written.** A pre-dispatch check cannot read a
final message that does not exist yet. The readable form is post-dispatch.

**Second — and this is the finding — the post-dispatch detector was built ten days ago.**

- [`scripts/verify-routing-reconciliation.py`](../../scripts/verify-routing-reconciliation.py)
  exists, and its docstring names this exact class: *"Third instance of class
  `dispatched-agent-stalls-silently`, so the altitude rule … forbids a fourth prose patch."*
- It is **wired as a build step**:
  [`config/revitalise-grant-automation-build.yml:246`](../../config/revitalise-grant-automation-build.yml#L246),
  `python3 scripts/verify-routing-reconciliation.py --warn-only`. Verified by parsing the config's
  70 steps, not by grep alone.
- **Executed this session, it reports 31 unreconciled dispatches** — including
  `[2026-08-31 19:32] pipeline-agent [trustee-portal-visual-refresh]`, which is the very dispatch
  family `IMP-0537` was logged against — and **exits 0**, because `--warn-only` is what makes it
  SOFT.

So the class does not lack a mechanical detector. It has one that fires correctly on every build and
prints into a 70-step log where nobody reads it. Adding a *second* gate for the same class would be
the instance patch the altitude rule forbids, aimed at a class the ladder has already served.

**Why `--warn-only` is not simply flipped to HARD:** 31 pre-existing unreconciled dispatches would
red every build immediately — `hard-gate-red-on-pre-existing-debt` (x2, `IMP-0439`, `IMP-0477`), and
the [`IMP-0181`](../../logs/improvement-log.jsonl) precedent the script's own docstring invokes.
That is a threshold-and-cutoff decision, and it is offered to the reviewer in §6, not taken here.

**What this review changes instead** is the thing that made the gate invisible: `WORKFLOW.md` still
tells its reader the gate does not exist.

### Change 1 — `agents/WORKFLOW.md` L145-149: retire a paragraph that describes a capability the system now has

[`agents/WORKFLOW.md#L145`](../../agents/WORKFLOW.md#L145) currently reads:

> **The mechanical half is deliberately not proposed here.** `logs/routing.log` carries 99
> `ROUTED_TO` lines against 9 `GATE_RECEIVED`, and only three agents use the terminal marker at
> all, so a reconciliation gate over that history would emit roughly ninety false positives. It
> can only work forward from a cutoff — the `IMP-0181` precedent — and that is a convention
> decision for the reviewer, not a defect fix.

Every clause of that is now stale. The gate was built, it works forward from a cutoff exactly as
predicted, and the counts it cites (99/9) are measured today at **208/105**. This is
`agent-instructions-describe-a-topology-that-changed` (x6) — the class where a retired or superseded
statement keeps instructing the next reader, which
[`skills/how-to-promote-a-finding.md#L88`](../../skills/how-to-promote-a-finding.md#L88) calls the
costliest kind of stale reference.

**Proposed replacement (literal diff):**

```diff
-**The mechanical half is deliberately not proposed here.** `logs/routing.log` carries 99
-`ROUTED_TO` lines against 9 `GATE_RECEIVED`, and only three agents use the terminal marker at
-all, so a reconciliation gate over that history would emit roughly ninety false positives. It
-can only work forward from a cutoff — the `IMP-0181` precedent — and that is a convention
-decision for the reviewer, not a defect fix.
+**The mechanical half EXISTS — read it before you reconcile by hand.**
+`scripts/verify-routing-reconciliation.py` closes every `ROUTED_TO` against a later
+`GATE_RECEIVED` / `STALLED` / `BLOCKED` / `HANDOFF_RECEIVED` naming the same agent and feature,
+working forward from a cutoff per the `IMP-0181` precedent. It is wired as the
+`routing-reconciliation` step of `config/<slug>-build.yml` and runs on every build.
+
+**It is `--warn-only`, so it exits 0 and blocks nothing.** Run it yourself when told a dispatch
+is stuck — it names the unclosed line for you, which is faster than reading the log:
+
+```bash
+python3 scripts/verify-routing-reconciliation.py
+```
+
+Its reading is not zero and has not been zero for some time: **31 unreconciled, 2 in flight,
+76 closed** of 109 in-scope dispatches as of 2026-08-31. A non-zero reading here is a queue of
+dispatches whose artefacts nobody verified — it is not noise, and it is not a build problem.
+Whether the batch half should ever go HARD is a threshold decision for the reviewer
+(improvement review 7 §6), not something this gate should decide by growing teeth on its own.
```

**Mechanically verifiable?** Yes, and by execution, not by reading:
`python3 scripts/verify-routing-reconciliation.py` — the paragraph's factual claims are exactly its
output. **Cites:** `IMP-0537`, `IMP-0291`, `IMP-0300`.

### Change 2 — `agents/WORKFLOW.md` L179: correct the drifted instance count

```diff
-**Added 2026-08-31, `IMP-0520` — the class at x7.** Everything above tells the dispatcher how to
+**Added 2026-08-31, `IMP-0520`.** Everything above tells the dispatcher how to
```

And at [`agents/WORKFLOW.md#L202`](../../agents/WORKFLOW.md#L202), the trigger the class has now
tripped:

```diff
-**If it recurs an eighth time, the honest next rung is a dispatch-prompt checklist in
-`agents/lead-agent.md`'s activation sequence — not another paragraph here.**
+**It recurred (`IMP-0537`, 2026-08-31, hours after this paragraph was applied), so the rung is
+now due: a dispatch-prompt checklist in `agents/lead-agent.md`'s activation sequence — not
+another paragraph here.** That file is owned by a different workstream group; improvement review
+7 §1 records why this dispatch did not write it and where it is carried.
```

**Why the bare count is deleted rather than corrected to `x5`:** hand-typing it again is how it
drifted. [`logs/known-failure-modes.md`](../../logs/known-failure-modes.md) generates this figure
from the log and is the single read path for it; a prose file should cite the class name and let the
digest carry the count. This is the same rule as
[`agents/improvement-agent.md#L381`](../../agents/improvement-agent.md#L381) ("never hand-type the
retired count — derive it").

**Cites:** `IMP-0537`. **Mechanically verifiable?** Yes — after this change no hand-typed instance
count for this class remains in `agents/WORKFLOW.md`:
`grep -c 'class at x' agents/WORKFLOW.md` → 0.

---

## 3. Cluster B — WS-J, resume vs. fresh dispatch. **Premise disproved; narrowed.**

WS-J's stated problem is that *"**every** `SendMessage` resume attempt on a parked
improvement-agent or architect-agent session **recorded in this project's history** has failed."*

**Measured against `logs/routing.log`: false.**

| Measurement | Result |
|---|---|
| Lines recording a resume attempt | **13** |
| Lines recording a resume **failure** | **1** — `routing.log:334`, one incident, three attempts, all 2026-08-28 |
| Resumes with positive downstream evidence of success | **≥6** — `routing.log:151, 157, 160, 174, 175, 203`; each applied a review or wrote a change order that is on disk today |
| Resumes that reached the agent but failed for a *different* reason | **1** — `routing.log:317` |

That last row is the interesting one. `routing.log:317` records a resume that **succeeded** in
reaching the agent and failed for an unrelated cause: *"SendMessage has no model parameter, so
resuming the existing (standard-tier) invocation with one silently no-opped instead of re-pinning
it."* The agent replied — it caught the problem itself and held. That is direct evidence against the
"resume never works" premise and direct evidence for a narrower, true rule.

**Adopting WS-J's literal wording would discard a working mechanism in 12 of 13 recorded cases**,
and would replace each cheap resume with a full fresh dispatch that re-reads every knowledge,
constraint and template file — the exact cost `CLAUDE.md` → Token Rules exists to avoid.

Per [`agents/improvement-agent.md#L221`](../../agents/improvement-agent.md#L221) this is
**NARROW-AND-REPORT**: the intent (stop paying for resumes that cannot work) survives; the literal
wording measures as wrong. The narrowing removes named false positives — the six successful resumes
above — and keeps the two conditions under which a resume genuinely cannot work.

### Change 3 — `agents/WORKFLOW.md`, new subsection after the fourth case's rule 2 (L134-135)

Rule 2 currently reads *"Re-dispatch fresh from the current session. Do not wait on, or try to
resume, a dispatch in a session this one cannot see."* That is correct and stays. The addition
distinguishes the case it does not cover — a session this one **can** see:

```diff
 2. **Re-dispatch fresh from the current session.** Do not wait on, or try to resume, a dispatch
    in a session this one cannot see.
+
+   **But a resume of a session this one CAN see is cheap and usually works — measured, not
+   assumed.** `logs/routing.log` records 13 resume attempts: one incident of three failures
+   (`No transcript found for agent ID`, `routing.log:334`, all 2026-08-28) against at least six
+   whose applied output is on disk today. Resume is the default for a parked agent you dispatched
+   yourself in this session; it keeps that agent's loaded context and skips a full re-read.
+
+   **Two conditions, and only these two, make a fresh dispatch mandatory:**
+
+   1. **You need a different tier.** `SendMessage` has **no `model` parameter**, so an override
+      passed to a resume silently no-ops and the agent keeps running on the tier it was spawned
+      with. On 2026-08-28 this was caught only because the agent re-derived its own tier and
+      refused to author under it (`routing.log:317`, `IMP-0399`). A tier change is always a fresh
+      Agent-tool dispatch with `model:` set at spawn.
+   2. **The transcript is gone** — another top-level session, a reboot, or a resume that returns
+      `No transcript found for agent ID`. Do not retry the resume; dispatch fresh, carrying the
+      doc path.
+
+   A failed resume costs one round trip and names its own remedy, so it is not a thing to
+   pre-emptively avoid — it is a thing to stop retrying once it has answered.
```

**Cites:** design document WS-J; `IMP-0399` (`routing.log:317`), `routing.log:334`.
**Mechanically verifiable?** **No — and this is stated rather than overclaimed**, exactly as WS-J
itself asks. No script can observe a resume attempt: `SendMessage` calls leave no repository trace,
and the 13 lines measured above exist only because `lead-agent` chose to narrate them. This is a
prose change to a prose rule, and the honest residual is that its compliance is unobservable.

---

## 4. Cluster C — `IMP-0538`, concurrent pipeline writers. **Lease deferred; the reader-side half taken.**

```
CLUSTER: concurrent-pipeline-dispatch-mislabels-shared-operation-id  (x1: IMP-0538)
Altitude:  INSTANCE — first recorded member of a new class
Ladder row: "one instance, cause is general, a human needs to know it" -> an agent-file line
Becomes:   agents/pipeline-agent.md, one paragraph (change 4)
Retires:   nothing
Cites:     IMP-0538 (design doc WS-L)
Residual:  no lock exists, so two concurrent live writers remain possible. Named in §6.
```

**What WS-L asks for is a lease file and a HARD constraint. This review proposes neither yet, and
the reason is the project's own measurement discipline, not caution for its own sake.**

[`agents/improvement-agent.md#L454`](../../agents/improvement-agent.md#L454) requires every new gate
to be run against the **real corpus** before wiring, with true/false positive counts reported. A
concurrency lock's corpus is *pairs of simultaneous live dispatches against one environment*. That
corpus has exactly one member — `IMP-0538` itself — and it cannot be replayed. A fixture simulating
two dispatches (WS-L's proposed verification) tests the lock against its author's own model of the
hazard, which is precisely what
[`agents/improvement-agent.md#L466`](../../agents/improvement-agent.md#L466) says fixtures cannot do.

**And the specific key `IMP-0538` proposes for the lock is already measurably unreliable.**
Its `proposed_change` is *"grep `logs/pipeline.log` for an unclosed `WRITE_BEGUN` on the same
feature/environment."* Measured on the live log:

```
WRITE_BEGUN    12
WRITE_ATTEMPTED 15
```

The markers do not pair. A detector keyed on "unclosed `WRITE_BEGUN`" reads a log where attempts
already outnumber begins by three, so its very first run would misclassify existing history. That is
the `gate-fires-on-nothing` / `gate-scope-mismatch` shape, and finding it is what the measurement
step is for. **A lock protecting a real DEV environment is the last place to ship an unmeasured
heuristic**, and the second-order failure — an agent that skips a legitimate write because a
phantom lease said someone else was working — is worse than the mislabelled log line that started
this.

So this review takes the half that is evidenced by the one instance we actually have, which is
`IMP-0538`'s own `lesson`: **a pipeline.log line is not evidence of your own work.**

### Change 4 — `agents/pipeline-agent.md`, appended to the `WRITE BEGUN:` convention (after L214)

[`agents/pipeline-agent.md#L212`](../../agents/pipeline-agent.md#L212) currently offers exactly one
reading of a dangling marker: *"A dangling `WRITE BEGUN:` is **not** a failure … it is the death
signature this convention exists to preserve."* `IMP-0538` is the case where it was neither a death
nor this dispatch's own work — it was **another live writer**, and the current text admits no such
reading.

```diff
 A dangling `WRITE BEGUN:` is **not** a failure and the gate does not treat it as one — it is the
 death signature this convention exists to preserve. Reconcile it by verifying live state, per
 `agents/WORKFLOW.md` → *the fourth case*, rule 1.
+
+**A dangling marker has a SECOND reading, and you cannot tell the two apart from the log: a
+dispatch that is still alive right now.** `logs/pipeline.log` has no lease, no lock and no
+append-time identity, so two live dispatches reconciling the same build write into it
+interleaved, and neither can see the other (`agents/WORKFLOW.md` → *the fourth case*: another
+top-level session's dispatch cannot be enumerated from here).
+
+On 2026-08-31 this produced a **factually wrong line**: a `WRITE ATTEMPTED` for a solution import
+naming the PUBLISH step's GUID as the import id, written by a session that was not the one running
+the import (`IMP-0538`). No damage followed only because both writers' operations were idempotent,
+which is luck, not a control.
+
+So, before you act on a dangling `WRITE BEGUN:` for the same feature and environment:
+
+1. **Check whether the OS process is still alive** before concluding anything died —
+   `ps -p <pid>`, or `pgrep -fl pac`. `IMP-0538`'s import process was still running normally at
+   the moment its dispatch was declared dead.
+2. **Re-query the live artefact immediately before AND after your own write** — for a Code App,
+   `canvasapps` `appversion` / `lastmodifiedtime` / `lastpublishtime`; for a solution, the
+   component itself. **A `logs/pipeline.log` line claiming success is not evidence, even when it
+   looks like your own work** — that is exactly the line that was wrong.
+3. **Never re-attribute an operation id you did not capture yourself.** Take every id from the
+   command's own output in this dispatch, never from a log line you found already written.
+
+**There is no lock, and this paragraph is not one.** It is the reader-side half only. Whether
+`logs/pipeline.log` gains a real lease is an open decision recorded in improvement review 7 §6.
```

**Cites:** `IMP-0538`. **Mechanically verifiable?** Partly, and stated honestly: steps 1–3 are
procedure, not assertions a script can check. The claim this paragraph makes *about the log* is
executable — `grep -c WRITE_BEGUN logs/pipeline.log` (12) vs `grep -c WRITE_ATTEMPTED` (15) — which
is why the paragraph asserts a property of the log rather than a phrase to look for.

---

## 5. Constraints and retirements

**Constraints proposed: 0 of 3.** WS-D budgeted 1 and WS-L budgeted 1; **both go unspent.**

- **WS-D's row is withheld** because the rule it would enforce (§2.1) has no observable input. A
  constraint whose `Verify By` cannot run is a comment
  ([`skills/how-to-promote-a-finding.md#L37`](../../skills/how-to-promote-a-finding.md#L37)).
- **WS-L's row is deferred** (§4) until the lease it would enforce exists and has been measured.
  A HARD row citing a script nobody has written is the same defect from the other end.

**Retirement considered, per the standing obligation.** One candidate found and taken:
[`agents/WORKFLOW.md#L145-L149`](../../agents/WORKFLOW.md#L145) — the "mechanical half is
deliberately not proposed here" paragraph, retired by **change 1**, replaced by a pointer to the
gate that now does the job. This is a *capability* retirement rather than a constraint retirement, so
it follows [`skills/how-to-promote-a-finding.md#L80`](../../skills/how-to-promote-a-finding.md#L80)'s
procedure (note it, name the replacement, grep for other instructions using the retired claim) and
not `constraints/README.md`'s.

**Grep for the retired claim elsewhere, per that skill's step 4** — to be run at application, with
every hit classified implementation / call site / instruction / history:

```bash
grep -rn 'mechanical half\|roughly ninety false positives' . \
  --include='*.md' --include='*.py' --include='*.yml' \
  --exclude-dir=.git --exclude-dir=node_modules
```

**No constraint row is added, amended or retired by this review.** Current figures, derived
([`agents/improvement-agent.md#L383`](../../agents/improvement-agent.md#L383)), not typed:

```bash
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   # 10 retired
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   # 82 live
ls scripts/verify-*.py | wc -l                             # 54 — unchanged; this review adds no script
```

---

## 6. Open decisions this review deliberately did not take

Four, each needing a reviewer judgement rather than a measurement. None is a silent cap.

1. **Should `routing-reconciliation` ever go HARD, and from what cutoff?** It reports 31 unreconciled
   today, so flipping it reds every build (§2.2). This is the same shape as WS-I's C-TECH-061
   threshold question — **recommend deciding both together in Group 2**, not separately here.
2. **Should `GATE_RECEIVED` lines record resolved model identity?** If they did, the WS-D tier check
   becomes buildable in a few months once a corpus exists. Today it cannot fire (§2.1). This is a
   logging-convention change, additive and cheap.
3. **Does `logs/pipeline.log` get a real lease?** (§4.) If yes, it needs a design that does not key
   on the unreliable `WRITE_BEGUN` pairing, and it must be measured before wiring.
4. **The `agents/lead-agent.md` dispatch-prompt checklist** — `IMP-0537`'s own proposed change and
   the rung `WORKFLOW.md` names as due. **Deferred to Group 2 on file-ownership grounds, not on
   merit** (§1).

---

## 7. Log bookkeeping

**Stamped at draft time** per [`agents/improvement-agent.md#L126`](../../agents/improvement-agent.md#L126) —
this is the only thing this document has changed on disk:

| Finding | `reviewed_in` | `status` | Disposition on approval |
|---|---|---|---|
| `IMP-0537` | this document | stays `NEW` | changes 1, 2 applied; **lead-agent half deferred** with `deferred_reason` + `revisit_when` naming Group 2 |
| `IMP-0538` | this document | stays `NEW` | change 4 applied; **lease deferred** with `deferred_reason` + `revisit_when` |

Neither entry is closed to `APPLIED`. Both are `observable_at: V3`, and
[`agents/improvement-agent.md#L308`](../../agents/improvement-agent.md#L308) refuses a closure
without a `reobserved` field naming who re-ran the reproduction. The reproduction for `IMP-0537` is
*a future dispatch not stalling*; for `IMP-0538` it is *two concurrent dispatches not colliding*.
Neither can be observed in this session. **An honest open entry beats a closed one nobody tested**
(`IMP-0224`, `IMP-0225`).

Each therefore carries a `deferred_reason` — the gate's own named second discharge — and **not a
bare `revisit_when`**, which for a non-blocker still classifies as `awaiting-approval` and for a
blocker is a permanent red light (`IMP-0516`). Neither entry is `blocker` severity (`friction`,
`rework`), so no blocker rung is at stake; the dispositions above were simulated against a scratch
copy of the log before this gate opened, per
[`agents/improvement-agent.md#L332`](../../agents/improvement-agent.md#L332).

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-31-improvement-review-7.md

Findings processed: 2 NEW  →  2 clusters  (+1 cluster from the design doc with no finding: WS-J)
Regression check:   4 prior changes audited, 1 class recurred (twice after prose, once past a
                    gate that fired correctly and was read by nobody)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    4 agent-file edits, 1 retirement
Altitude calls:     1 generalised from instance to class, 2 withheld on disproved premises
Digest:             will regenerate — no lesson count change (no entry closes)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**IMPROVEMENT LOG:** 0 entries appended — none | digest regenerated: NO (nothing to regenerate;
no status moves at draft time)

---

## 9. Applied record (step 8)

Applied 2026-08-31 under `APPROVE IMPROVEMENTS`, after re-verification. **Every perishable
measurement in this document was re-run unchained before its change was applied**, per
`agents/improvement-agent.md` step 8 and `IMP-0405`.

| # | Target | On disk | Re-verified before applying |
|---|---|---|---|
| 1 | `agents/WORKFLOW.md` — fourth case, "mechanical half" paragraph retired | YES | `verify-routing-reconciliation.py` re-run: **31 unreconciled, 2 in flight, 76 closed of 109** — unchanged from the draft |
| 2 | `agents/WORKFLOW.md` — `x7` count removed, rung recorded as due | YES | class count re-measured: **5**, unchanged |
| 3 | `agents/WORKFLOW.md` — resume rule, after the fourth case's rule 2 | YES | 13 resume attempts / 1 failure incident, unchanged |
| 4 | `agents/pipeline-agent.md` — second reading of a dangling `WRITE BEGUN:` | YES | `WRITE_BEGUN` **12** vs `WRITE_ATTEMPTED` **15**, unchanged |

**One assertion did NOT survive re-verification, and it was this review's own.** §2.1 claimed
**0** `ROUTED_TO:lead-agent` lines; the true figure is **2**, and the draft's figure had never been
measured — an `&&`-chained `grep -c` exited 1 and dropped the command. §2.1 now carries the
correction inline and the defect is logged as `IMP-0542`. **The withhold is unchanged**: reading
both lines shows they are lead-agent self-bookkeeping, not dispatches, and the load-bearing reason
(0 of 105 `GATE_RECEIVED` lines carry a model identity) re-measured identically. `GATE_RECEIVED`
moved 103 → 105 between draft and application; both figures are corrected in place.

**A second correction, inherited rather than committed here.** `IMP-0539` (the review-filename
collision) was itself corrected by `IMP-0540` while this review sat at its gate: Group 2 had not
yet written its file, so nothing was overwritten and the collision was **latent, not realised**.
`IMP-0537`'s `deferred_reason` was written citing the original account and amended to the corrected
one before the digest was regenerated. This is exactly the interval `agents/improvement-agent.md`
step 8 exists for — the log grew from 536 to 539 entries during this application.

**Not applied, and why:** WS-D req. 1 (withheld, §2.1), WS-D req. 2's second gate (redirected —
the gate exists, §2.2), WS-J's literal wording (narrowed, §3), WS-L's lease and constraint row
(deferred, §4). **0 of 3 constraints used. 0 scripts added** — `ls scripts/verify-*.py | wc -l`
remains **54**, so the count registered in `scripts/derived-counts-registry.json` needs no update.
