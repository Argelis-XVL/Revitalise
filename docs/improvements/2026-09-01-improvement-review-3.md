# Improvement Review — WS-E: exclude generic built-in agents from routing

**Date:** 2026-09-01
**Mode:** capability (`agents/improvement-agent.md` L62-L80)
**Authorising artefact:** `docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md` §WS-E (L151-L168)
**Scope:** WS-E only. `wbs:system`, non-billable (`C-COM-002`).
**Status:** **APPLIED 2026-09-01.** All three changes are on disk. See §13 for the applied record,
including the reviewer's override of §3's recommendation and the FleetView caveat that remains open.

**Filename note (2026-09-01).** This draft was first written to
`docs/improvements/2026-09-01-improvement-review.md`. Three dispatches — this one, the
reconciliation-cutoff dispatch, and WS-B's — independently computed that same path on the same day;
WS-B's draft (Improvement Review 10) is the one that survived there, and this document was
re-persisted here unchanged in substance. **No measurement in this document was re-derived after the
collision** — every figure and every run below predates it. This is a live instance of
`concurrent-session-same-file-write`, the same class as `IMP-0539`/`IMP-0541`; it is logged in §10.

---

## 1. Headline — WS-E's central assumption is wrong, in the system's favour

WS-E's *Mechanical verification* clause (L161-L164) says **"none purely mechanical is available if
the harness has no per-repo subagent allowlist — in that case this is prose-only."** It asks that
this be confirmed rather than assumed.

**Confirmed, and the answer is the opposite of the one the workstream expected: a per-repo
mechanical block exists, it is documented, and I executed it.** `permissions.deny` in
`.claude/settings.json` accepts an `Agent(<name>)` matcher, and a denied dispatch is refused by the
harness, not discouraged by prose. So WS-E does **not** need the prose-only exception it pre-authorised.

Two consequences follow, and the second is the more important one:

- WS-E ships as a **HARD harness control** plus a prose rung, not as prose alone.
- `agents/lead-agent.md` L113-L117 currently asserts, as a general principle, that **"Nothing sits
  between an agent and the Task tool, so these are prose and will stay prose."** That sentence is
  now measurably false, and it is load-bearing — it is the stated reason five rules in that section
  were left unenforced. It is corrected in the same change (below), because leaving it would create
  an `approved-document-internally-inconsistent` defect, this repo's third-largest class at
  [x25](../../logs/known-failure-modes.md#L38).

---

## 2. The measurement

Not documentation-reading — execution, per `agents/improvement-agent.md`
[L149-L164](../../agents/improvement-agent.md#L149). Three isolated headless runs in the scratchpad,
Claude Code `2.1.100`:

| # | Setup | Prompt | Result |
|---|---|---|---|
| A | `permissions.deny: ["Agent(Explore)","Agent(Plan)","Agent(general-purpose)"]` | dispatch `subagent_type: Explore` | **REFUSED** — *"a project-level permission rule `Agent(Explore)` is explicitly denying it"* |
| B | `permissions.deny: []` (control) | same prompt, same dir shape | **SUCCEEDED** — Explore dispatched and returned the file contents |
| C | deny `general-purpose` + `claude`, plus a local `probe-agent` | dispatch `probe-agent`; then plain non-agent work | **BOTH ALLOWED** — project agents and ordinary work unaffected |

Run B is the discriminator. Without it, run A only proves that *some* model declined *something*;
with it, the deny rule is the sole variable and it is the cause. Run C is the safety proof: the deny
does not leak onto this repository's own 18 agents.

**Level reached: V4** (`C-TECH-053`) — observed live, in the harness that will enforce it, not parsed
and not inferred.

**Supporting doc confirmation** (secondary to the runs above): `Agent(<name>)` deny is documented at
[code.claude.com/docs/en/permissions](https://code.claude.com/docs/en/permissions) §"Agent (subagents)"
and [sub-agents](https://code.claude.com/docs/en/sub-agents) §"Restricting Subagent Use".
Parameter-form matching — `Agent(subagent_type:Explore)` — is **not** exemplified in the docs, so
this change uses only the named form.

**Robustness:** `.claude/settings.json` is tracked (`git ls-files .claude/`), so removing the deny
shows up in a diff. `.claude/settings.local.json` is gitignored at
[`.gitignore:41`](../../.gitignore#L41) and *cannot* re-enable a denied agent — deny takes precedence
over allow at every scope.

---

## 3. The one place I depart from WS-E's literal wording, and why

WS-E asks that **all four** generic built-ins be excluded. **I propose denying two and permitting
two,** and I want this visible rather than buried, because it is a deviation from the approved
requirement and the reviewer may simply override it.

| Agent | Tool grant | Can it produce unconstrained delivery artefacts? | Proposed |
|---|---|---|---|
| `claude` | `*` | **Yes** — full Edit/Write | **DENY** |
| `general-purpose` | `*` | **Yes** — full Edit/Write | **DENY** |
| `Explore` | all *except* Agent, Artifact, ExitPlanMode, Edit, Write, NotebookEdit | **No** — read-only | permit |
| `Plan` | same read-only grant | **No** — read-only | permit |

WS-E's stated harm is that a generic dispatch *"silently skips every constraint check, tier pin,
gate keyword, and improvement-log capture."* That harm requires the agent to **write** — a
constraint check, a gate keyword and an improvement-log entry are all about artefacts reaching disk.
`Explore` and `Plan` cannot write anything; their output returns to a caller that is itself a
properly-dispatched project agent still bound by every rule. Denying them removes a genuinely useful
read-only fan-out search and buys no enforcement.

This is the anti-bloat instinct applied to a permission list: **deny what can cause the harm, not
what merely shares a category with it.** If the reviewer prefers the literal WS-E scope, it is a
two-string edit to the same array and I will apply it on request — say so with the keyword.

**One risk I cannot fully close:** `claude` is described in this harness's roster as *"FleetView's
default when no agent name is typed."* Test C showed ordinary work unaffected in Claude Code, but I
have not tested FleetView. If this repository is ever driven from FleetView, `Agent(claude)` may need
to come back out. Flagged, not resolved.

---

## 4. Proposed changes (3) — AS DRAFTED

> **Read §13 for what is actually on disk.** This section is retained in its pre-approval form, per
> this repository's erratum convention: a correction shows what changed rather than overwriting it.
> **The reviewer overrode §3 and chose all four agents**, so Change 1's array below (two names) and
> Change 2's rung text below (*"deliberately left available"*) are **NOT** what was applied.

### Change 1 — the mechanical control

`.claude/settings.json`, adding a `deny` array alongside the existing `allow`:

```json
"deny": [
  "Agent(general-purpose)",
  "Agent(claude)"
]
```

**Superseded at application — all four names were applied.** See §13.

### Change 2 — the prose rung, covering all four

`agents/lead-agent.md`, a new item **6** at the end of *"What a dispatch gets wrong that nothing can
see"* ([L108](../../agents/lead-agent.md#L108)), following the section's established shape — the
rule, the evidence, and what is enforced versus what is not:

> 6. **Delivery and PM work never routes to a generic built-in agent** — `claude`,
>    `general-purpose`, `Explore`, `Plan`. They are reachable through the same Task-tool mechanism
>    as this project's 18 agents and share none of its machinery: no tier pin, no constraint check,
>    no gate keyword, no improvement-log capture. A dispatch to one produces work that looks
>    delivered and was never gated.
>
>    **The two that can write are blocked by the harness, not by this paragraph.**
>    `.claude/settings.json` denies `Agent(general-purpose)` and `Agent(claude)`; a dispatch to
>    either is refused at the tool call. `Explore` and `Plan` are deliberately left available: their
>    tool grants exclude Edit/Write/NotebookEdit, so they cannot produce an ungated artefact, and
>    they are useful as read-only search inside a properly dispatched agent. **Using one for
>    research is fine; using one to decide, design or deliver is the mis-route this rung names, and
>    that half is prose.**
>
>    No instance has occurred: 209 `ROUTED_TO` lines in `logs/routing.log` name only project agents.
>    This rung is preventive, and it is written down because the failure mode is silence — a
>    mis-route to a generic agent raises no error and leaves no distinguishing trace.

### Change 3 — correct the section preamble's now-false claim

`agents/lead-agent.md` [L113-L117](../../agents/lead-agent.md#L113). Current text:

> Nothing sits between an agent and the Task tool, so these are prose and will stay prose — the
> standing mechanical control is the *dispatched* agent's own tier self-check…

Replacement, keeping the erratum convention this repo uses (the withdrawn claim stays visible):

> **Erratum 2026-09-01 (this review, WS-E):** this section read *"Nothing sits between an agent and
> the Task tool, so these are prose and will stay prose."* That is false and was never tested.
> `permissions.deny` in `.claude/settings.json` accepts an `Agent(<name>)` matcher and refuses the
> dispatch at the tool call — measured live, three runs with a control. Rung 6 uses it. The
> remaining rungs stay prose because each turns on a *parameter or premise* of a dispatch
> (`model:`, `isolation:`, the truth of a cited fact, whether another dispatch is mid-edit), and
> `permissions.deny` matches on the agent NAME only. **The distinction to carry forward: which
> agent is dispatched is mechanically constrainable; what the brief claims is not.**

---

## 5. Withheld, and retirement

**Withheld — a gate asserting the deny entries are present in `.claude/settings.json`.** Considered
and rejected on this project's own anti-bloat rule. The file is tracked and 15 lines long, so a
removal is visible in any diff; a 55th `verify-*.py` would guard a JSON array against an edit that
review already catches. If the deny is ever found removed without a review, that is the second
instance and the gate becomes justified.

**Retirement candidates: none found, and I checked.** WS-E adds a permission entry and two prose
blocks; it supersedes no existing rule, no constraint row and no script. Nothing in
`constraints/` addresses subagent selection today. Derived at draft time, not retyped:

```
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   →  10 retired
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   →  82 live
ls scripts/verify-*.py | wc -l                             →  54 (unchanged — this review adds no script)
```

**Constraint cap: 0 of 3 used.** The enforcement is a harness permission, which is a more mechanical
home than a constraint row — a row whose `Verify By` read *"open settings.json and look"* would be a
comment (`agents/improvement-agent.md` [L393](../../agents/improvement-agent.md#L393)).

---

## 6. Regression check — did review 8's changes hold?

| Question | Answer |
|---|---|
| Any finding in review 8's classes since? | **No.** Its changes were the `C-TECH-061` rule-text correction and the build step reorder. The 3 unread findings are `concurrent-session-same-file-write` (×2) and `finding-diagnosis-unverified` — neither class |
| Did the ≥30 threshold behave? | **Yes, measured.** `verify-improvement-log.py --check` exits **OK** at 3 unread / 0 awaiting-approval. At the old ≥10 it would still be green here, but the erratum's stated reason — a single dispatch logging 30 findings — is unrelated to today's count |
| Was any change prose where a gate was possible? | Review 8's change 1 was prose (a rule-text correction) and correctly so; the script was already authoritative over the sentence |

---

## 7. Findings — what this review did and did not touch

**This review processes no pre-existing `IMP-` findings and stamps no `reviewed_in`.** It is
capability mode: the authorising artefact is the design document, and WS-E cites no findings as its
trigger (`agents/improvement-agent.md` [L73-L76](../../agents/improvement-agent.md#L73)). One finding
is *logged by* this review from its own experience — see §10.

**Queue state at draft time**, per `verify-improvement-log.py --check` — 539 entries, 118 NEW:

| State | Count | Disposition |
|---|---|---|
| `unread` | 3 — `IMP-0539`, `IMP-0540`, `IMP-0541` | **excluded from this dispatch's scope; see below** |
| `awaiting-approval` | 0 | — |
| `reviewer-deferred` | 115 | left; each carries an accepted reason |
| `already-fixed` | 0 | — |

**One item needs the reviewer's attention and is not mine to fix.** All three unread entries are
cited by **`2026-08-31-improvement-review-7.md` and `-8.md`** and carry **no `reviewed_in`** — the
`IMP-0488` defect exactly: two reviews analysed them and neither stamped them, so the queue reports
them as *"nothing records that anyone has looked at these."* Stamping them belongs to whoever owns
reviews 7 and 8, not to a WS-E dispatch, and I have not touched them.

**This is not currently blocking anything.** The gate exits **OK**: none is `blocker` severity
(`rework`, `friction`, `friction`) and 3 is far below the ≥30 batch trigger review 8 installed. The
gate's own warning prose about *"the next build fails on it"* is generic text, not today's verdict.

---

## 8. Concurrency check, as the dispatch required

`agents/lead-agent.md` was modified in the working tree when this dispatch opened. Checked before
starting, per the brief: the diff is **one line** — the improvement-trigger threshold moving from
`≥10 NEW` to `≥30 unread/awaiting-approval`. That is review 8's WS-I change, uncommitted but applied.
It is not a live concurrent edit, and it does not touch the section WS-E modifies (L108-L219 versus
L258). Proceeding was safe.

**The file-level check passed and the collision happened anyway, one directory over.** I checked the
file WS-E *edits* and not the file WS-E *writes* — and the review-document filename is the one
every concurrent review computes identically from the date. See §10.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review-3.md

Findings processed: 0 pre-existing NEW  →  0 clusters (capability mode: authorised by design doc
                    WS-E, not by IMP- ids; 3 unread excluded and reported, 115 reviewer-deferred
                    left). 1 finding logged by this review from its own experience — IMP-0547 (§10)
Regression check:   3 prior changes audited (review 8), 0 classes recurred
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    2 agent-file edits, 1 config edit (.claude/settings.json), 0 retirements
Altitude calls:     1 raised from prose to a mechanical harness control, 4 prose rungs left as prose
                    (correctly — they match on brief content, which no matcher can reach)
Digest:             ALREADY REGENERATED at draft time for IMP-0547 — 544 entries, 613 lines,
                    --check current. The proposed changes close no finding, so approval adds nothing
Sequencing:         .claude/settings.json is shared with improvement review 9's WS-A (IMP-0546).
                    Must not be applied concurrently with it — see §11

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Two things to decide with the keyword:**

1. **Two denies or four?** §3 proposes denying only the write-capable pair. Say "all four" and I
   extend the array.
2. **FleetView.** If this repo is ever driven from FleetView, `Agent(claude)` may need to stay
   allowed (§3, last paragraph). Untested by me.

---

## 10. Finding logged by this review — the review-filename collision

Three dispatches on 2026-09-01 independently computed
`docs/improvements/2026-09-01-improvement-review.md` and wrote to it; two drafts were lost, and this
one was recovered only because its author was still live and holding the content in context. The
reconciliation dispatch's draft may not have been.

**This is the third instance of `concurrent-session-same-file-write`** (`IMP-0539`, `IMP-0541`), and
by the altitude rule in `skills/how-to-promote-a-finding.md` §2 a third instance may not get another
instance patch. But note what distinguishes it from the first two: those were two sessions editing a
shared *existing* file. This one is **a deterministic name collision** — every improvement review
derives its own output path from the date alone, so N concurrent reviews on one day always collide,
and `Write` overwrites without warning. The per-dispatch suffix (`-2`, `-3`) is assigned by whoever
notices second.

**I am not proposing the fix in this review.** WS-E's scope is the routing control, the
3-constraint cap and the design-doc requirement ids are WS-E's, and a filename-allocation mechanism
belongs with the same class of work as `scripts/allocate-improvement-id.py` — which exists precisely
because ids had this defect (`IMP-0080`) and solved it by allocation rather than by derivation. The
finding records the class and names that precedent; the fix is a separate dispatch.

**Logged as `IMP-0547`** — appended, validated and digested at draft time (not deferred to approval),
per the Learning Rules. Id allocated with `scripts/allocate-improvement-id.py`, never from `tail -1`;
the log had moved from 539 to 543 entries while this dispatch ran, which is the same concurrency the
finding describes.

- `class_instance_of`: `concurrent-session-same-file-write` · `severity`: `rework` · `observable_at`: V4
- `proposed_change.type`: `script` — allocate review filenames instead of deriving them, on the
  `allocate-improvement-id.py` precedent. **Not built here**; it is a separate dispatch.

```
python3 scripts/verify-improvement-log.py --check      → OK, 544 entries, exit 0
python3 scripts/generate-known-failure-modes.py        → wrote 544 entries, 613 lines
python3 scripts/generate-known-failure-modes.py --check → current
```

---

## 11. Blocking hazard for whoever applies this — `.claude/settings.json` is now contested

**Do not apply this review's Change 1 and improvement review 9's WS-A changes concurrently.**

`IMP-0546`, logged by review 9 *after* this dispatch began, records that WS-A's open mechanism
decision resolved to **neither** option its design-doc Files line predicted. It is not a
`generate-subagents.py` change; it is **a PreToolUse hook plus `.claude/settings.json`** — which is
this review's Change 1 file. The capability design document's parallel-safe groups table placed WS-A
and WS-E in different groups precisely because it believed they shared no file. That premise is now
false, and review 9 §8 already carries the same instruction from its side.

This is worth stating plainly because the two changes are not merely co-located, they are
*compatible and adjacent*: WS-A adds a hook keyed on agent type, WS-E adds a `permissions.deny`
array, and both land in the same small JSON object. Applied concurrently by two sessions, the second
write silently discards the first — the identical mechanism as §10, one file over.

**Sequence them.** Either dispatch may go first; the second must re-read `.claude/settings.json`
before writing rather than applying its drafted JSON blind.

---

## 12. The improvement log is RED right now, and not from this review

Reported, not fixed — the entry belongs to another live dispatch and may still be mid-write.

`python3 scripts/verify-improvement-log.py --check` **exited OK at 544 entries** immediately after
this review appended `IMP-0547`. It now **FAILS at 545**, and all five problems are in a single
entry appended afterwards by improvement review 2's dispatch:

```
ERROR: IMP-0548: missing required field(s): detected_by, why_it_was_never_caught, lesson, proposed_change
ERROR: IMP-0548: severity 'improvement' is not one of ['blocker', 'friction', 'rework']
ERROR: IMP-0548: evidence_grep must be an object {"file":…,"contains":…}, got str
ERROR: IMP-0548: reobserved must be an object, got str
verify-improvement-log: FAILED — 5 problem(s) across 545 entry(ies)
```

`IMP-0547` is clean and there are no duplicate ids (checked directly, 545 ids, 0 repeats).

**This matters beyond tidiness: `C-TECH-061` is HARD, and this gate runs as the `improvement-log-check`
step of `config/<slug>-build.yml` and in CI's `validate` job.** Until `IMP-0548` is corrected, **every
build fails in about one second** — which is the cheap version of this failure, but it is still red.
`logs/known-failure-modes.md` is also now stale (generated at 544).

This is `IMP-0369`'s exact shape — an agent appending a malformed entry and not noticing, because
regenerating the digest is not validation. Whoever owns review 2 should run the validator and fix
the four field errors; the id and the content look fine, only the schema is wrong.

---

## 13. Applied record — 2026-09-01

`APPROVE IMPROVEMENTS` received with an explicit reviewer decision on the §3 open question.

### Re-verification performed before applying (step 8)

| Check | Result |
|---|---|
| `verify-improvement-log.py --check` | **OK, exit 0**, 545 entries. §12's RED snapshot was a transient mid-write read of a concurrent dispatch's append; `IMP-0548` is now well-formed. **§12 stands as written** — it records what was true when read, and the resolution is noted here rather than by deleting it |
| §11's `.claude/settings.json` contention with WS-A | **CLEARED, and confirmed against disk rather than the document.** `.claude/hooks/` does not exist; `.claude/settings.json` carried no `hooks` block and was clean in `git status`; review 9 L9 reads *"DRAFT — nothing in this document is on disk."* Nothing from WS-A landed. **The hazard remains live in the other direction** — see "Forward hazard" below |
| Is the `Agent(<name>)` deny still the right mechanism? | Yes, and it was re-confirmed at apply time by the strongest evidence available — see "Verification executed" |

### Changes applied (3)

| # | File | What |
|---|---|---|
| 1 | `.claude/settings.json` | `permissions.deny` added with **all four** agent names. The 11 existing `allow` entries are preserved unchanged (verified: 11 in, 11 out) |
| 2 | `agents/lead-agent.md` | New rung **6** in *"What a dispatch gets wrong that nothing can see"* |
| 3 | `agents/lead-agent.md` | Erratum correcting the section preamble's false *"Nothing sits between an agent and the Task tool"* claim |

### Reviewer override — recorded because it went against this review's recommendation

§3 recommended denying **two** agents (`claude`, `general-purpose`) and permitting `Explore` and
`Plan`, on the ground that neither can write and both are useful for read-only search. **The reviewer
chose all four,** matching WS-E's original literal wording.

Applied as decided, not as recommended. This is the plain case the improvement-agent's own step 8
names: *the enforcement wording is what the human approved*, so the array carries four names and the
rung teaches the simple rule — **no generic agent, for anything.** The cost is real and is stated in
rung 6 rather than buried here: this repository has given up read-only fan-out search deliberately.
Reverting to the two-agent form is a two-string edit and the reasoning is preserved in §3; it should
not be re-derived.

### FleetView caveat — OPEN, and deliberately recorded in two places

**`Agent(claude)` may need to be reverted if this repository is ever driven from FleetView.**
`claude` is that client's default agent when no name is typed. Ordinary work and project-agent
dispatch were both verified unaffected **in Claude Code**; **FleetView was not tested and I have no
way to test it.** This is written into `agents/lead-agent.md` rung 6 as well as here, because a
caveat that lives only in a review document is one the next person will not find.

### Verification executed — V4, and better evidence than the pre-approval runs

The pre-approval measurement was three isolated headless runs in a scratch directory (§2). At apply
time the control was confirmed **in this repository, against this session**, by the harness itself:
immediately after `.claude/settings.json` was written, the session's own agent roster dropped all
four names, reporting *"The following agent types are no longer available: Explore, Plan, claude,
general-purpose."*

That is stronger than any test I could have designed — it is the enforcement acting on the live
session that installed it, in the real repo rather than a fixture. **Level V4** (`C-TECH-053`).

```
python3 -c "json.load(open('.claude/settings.json'))"   → parses; deny=4 names, allow=11 preserved
grep -c "Nothing sits between" agents/lead-agent.md     → 1 (the erratum's own quotation only)
grep -n "^[0-9]\. \*\*" agents/lead-agent.md            → rungs 1-6, list intact
python3 scripts/verify-improvement-log.py --check       → OK, exit 0, 545 entries
python3 scripts/generate-known-failure-modes.py --check → current
```

### Bookkeeping

- **`IMP-0547` stays `NEW` with a `deferred_reason` and a `revisit_when`** — deliberately not closed.
  Its fix is already drafted as **change F1 of improvement review 9**
  (`scripts/allocate-review-number.py`, the same allocator precedent this finding cites). Building it
  here would be one change implemented twice, which `config/models.yml` L12 already records as a paid
  cost (`IMP-0310`). A bare `revisit_when` would have left the entry reading `awaiting-approval`
  forever (`IMP-0516`), so the deferral carries a reason and a named return condition.
  **It also corroborates F1:** review 9 §4.2 counts **two** filename collisions; this is a **third**,
  and the first three-way one. F1 should be measured against 3 instances, not 2.
- **No finding is closed by this review**, so no `reobserved` was required.
- **No constraint row added** (0 of 3), **no script added** (`ls scripts/verify-*.py | wc -l` → 54,
  unchanged), **no retirement** — all as drafted.

### Forward hazard — for whoever applies improvement review 9

**`.claude/settings.json` now contains this review's `deny` block.** Review 9's change A2 adds a
`hooks` block to the same file and was drafted against the *previous* contents. Whoever applies it
must **re-read the file and merge**, not write its drafted JSON blind. §11's warning is not
discharged by this application — it has simply reversed direction.
