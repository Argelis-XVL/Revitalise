# Improvement Review — 2026-09-01 (6)

**Status: APPLIED — 2026-09-01, on `APPROVE IMPROVEMENTS`.** All three changes are on disk. One
deviation from the approving instruction — `IMP-0557` deferred rather than closed `APPLIED` — is
recorded in §10 and was not silent.

**Mode:** capability, reviewer-directed. **WBS:** `wbs:system`, non-billable.
**Authorising artefact:** [`2026-08-31-improvement-review-9.md` §2](2026-08-31-improvement-review-9.md#L54),
plus the reviewer's instruction to build the three changes it withheld.

---

## 0. Headline

**The hook works, live, and the evidence is a real refusal — not a passing self-test.** A genuine
`build-agent` dispatch was refused on two attempts against two protected directories, and a
genuine `improvement-agent` dispatch wrote the same directory unimpeded. Review 9's withdrawal
condition — *"if the hook does not fire, or `agent_type` is absent in practice, A1 and A2 are
withdrawn"* ([review 9 §2.3](2026-08-31-improvement-review-9.md#L107)) — is not met. Nothing is
withdrawn.

Three harness properties the official documentation does **not** state were settled by executing
them, and all three had to hold or the design was dead:

| Property | Docs | Measured |
|---|---|---|
| Does a project-level `PreToolUse` hook fire inside a **dispatched subagent**? | silent | **Yes** — 4 fires recorded from 2 different dispatches |
| Does a `hooks` block added to `.claude/settings.json` take effect **in the same session**? | silent on the timing guarantee | **Yes** — registered at 15:58, first fire at 15:58, no restart |
| Is `agent_type` the subagent **definition name**? | documented as present "in subagents" | **Yes** — observed literally as `improvement-agent` and `build-agent` |

This is the V0 → executed step [review 9 §2.3](2026-08-31-improvement-review-9.md#L100) demanded
and could not take itself.

---

## 1. Scope, and what this review deliberately did not touch

This is a narrow, reviewer-directed dispatch to finish one withheld change. It is **not** a pass
over the queue.

`verify-improvement-log.py --check` at activation: **exit 0**, 122 NEW — **4 unread**
(`IMP-0549`, `IMP-0550`, `IMP-0551`, `IMP-0552`), 0 awaiting-approval, 118 reviewer-deferred, 5
warnings. **All four unread findings are excluded from this review**, stated rather than silently
capped per the no-silent-caps rule. None of them touches WS-A: three are class
`finding-diagnosis-unverified`, one `hand-maintained-count-drifts-from-source`, one
`wrong-artefact-cited-as-evidence`, all severity `friction`, and **none carries `corrects`
against anything this review acts on**. The unread trigger therefore remains live after this
review and a queue pass is still owed.

The five `corrects` warnings (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`, `IMP-0437`) were
read. None names A1, A2, A3 or review 9.

---

## 2. Regression check — review 9's own changes

| Prior change | Held? |
|---|---|
| F1 `scripts/allocate-review-number.py` | **Yes.** This review's filename was claimed with it, not computed. It returned `2026-09-01-improvement-review-6.md` and wrote the reserving stub |
| F2 claim the filename at step 6 | **Yes** — followed here; the name was claimed before the draft, not at gate time |
| F3 `;` not `&&`, label every measurement | **Yes** — every measurement in this review is labelled and unchained. The `ls constraints/.fixture-probe-2.md` that was *expected* to fail is reported as its own labelled line precisely because `IMP-0542`'s shape is an absent measurement reading as a zero |
| A1/A2/A3 | **Withheld by review 9**, and this review is the change that resolves them |

No finding in any of those classes has appeared since. The class this review closes an instance
of, `declared-policy-not-mechanically-enforced`, stands at **24 entries** — the largest class in
the log, and the reason a prose declaration was the wrong altitude for this rule.

---

## 3. The changes

### A1 — [`.claude/hooks/protect-system-rules.py`](../../.claude/hooks/protect-system-rules.py) (new)

A `PreToolUse` hook that denies when **all three** hold: `agent_id` is present, `agent_type` is
not `improvement-agent`, and the resolved write target is under `agents/`, `constraints/`,
`skills/` or `knowledge/`. The decision is a pure function
([`decide()`, L84](../../.claude/hooks/protect-system-rules.py#L84)) so the self-test exercises the
real path and not a copy of it; paths are resolved through `os.path.realpath`
([`protected_path()`, L66](../../.claude/hooks/protect-system-rules.py#L66)) so `src/../agents/x.md`
and a symlink into a protected directory are both caught.

**Deny form:** exit 0 with `hookSpecificOutput.permissionDecision = "deny"`
([L143](../../.claude/hooks/protect-system-rules.py#L143)). The exit-2-and-stderr form exists and
was not used: the JSON form carries a `permissionDecisionReason` that reaches the blocked agent
intact, and the reason text is doing real work here — it tells the refused agent to log a finding
rather than route around the refusal, which the fixture confirms it obeyed.

`MultiEdit` was added to the matcher beyond review 9's three tools. It is the same class of
operation and omitting it would have been a hole in the rule as approved, not a narrowing of it.

### A2 — [`.claude/settings.json`](../../.claude/settings.json)

A `hooks` key ([L2](../../.claude/settings.json#L2)) merged **alongside** the existing
`permissions` block. Review 9 §2.2 described the file as having *"`permissions.allow` and no
`hooks` key"*; that was true when review 9 was drafted and is no longer — WS-E landed a
`permissions.deny` block with four `Agent()` entries at 12:09:57 the same day. **This was a merge,
verified as such:** `git diff --stat` reports **19 insertions, 0 deletions**, the 4 `deny` entries
and 11 `allow` entries survive byte-for-byte, and the file parses.

The §2.4 collision hazard is therefore closed by sequencing rather than by luck: WS-E finished
before this dispatch began, and this dispatch read the file's current contents before writing.

### A3 — [`agents/improvement-agent.md#L12`](../../agents/improvement-agent.md#L12) — **APPLIED**

Inserted after line 13, naming A1 as the enforcement and stating its limits. The text below is what
is on disk:

> **Since 2026-09-01 that is enforced, not merely declared.**
> `.claude/hooks/protect-system-rules.py` is a `PreToolUse` hook that refuses `Edit`, `Write`,
> `MultiEdit` and `NotebookEdit` against those four directories from any **dispatched** subagent
> whose `agent_type` is not `improvement-agent`. Two limits are deliberate, and a reader who does
> not know both will over-trust the control: it does **not** bind the root session or the human —
> `agent_id` is absent for both, so `lead-agent` and the reviewer keep write access to all four
> directories — and it does **not** cover `Bash`, so it is a refused route, not an impossible
> write. Proven by live fixture, not read from documentation: improvement review 6, 2026-09-01.

---

## 4. The live fixture — what was actually run, and what it returned

Review 9 made this an **apply-time obligation**
([§2.3, L106](2026-08-31-improvement-review-9.md#L106)), and it is the only reason A1 and A2 are on
disk before the keyword: **the hook cannot be observed firing unless it is registered.** The
undertaking given at the gate was that a refusal would revert A2's `hooks` key and delete A1; the
keyword arrived, so both stand.

**Step 0 — V1, before anything live.** `--selftest`: **23 assertions, 0 failed**. It proves it can
fail: deleting the `agent_id` guard from a copy made exactly the 2 root-session assertions go red,
21 passed / 2 failed. Real stdin round-trip produced the deny JSON on stdout for a `build-agent`
payload and **0 bytes** for an `improvement-agent` payload.

**A self-test proves nothing about the harness**, which is the whole point of what follows.

**Step 1 — the allow half.** This dispatch (`improvement-agent`) used the `Write` tool to create
`agents/.fixture-probe.md`. It succeeded. The hook fired and recorded:

```json
{"agent_id":"ae4ba1c7eb82305b6","agent_type":"improvement-agent","tool_name":"Write",
 "permission_mode":"auto","file_path":".../agents/.fixture-probe.md","deny":false,
 "reason":"improvement-agent — permitted"}
```

That single line settles all three undocumented properties at once: the hook **fired inside a
dispatch**, from a `hooks` block added **minutes earlier in this same session**, and `agent_type`
came through as the definition name.

**Step 2 — the deny half.** A real `build-agent` dispatch was told to attempt exactly two calls,
once each, and explicitly forbidden to retry or to route around a refusal. Both were refused.
Verbatim, as returned to it:

> BLOCKED by .claude/hooks/protect-system-rules.py: this is a dispatched build-agent subagent
> attempting Edit against agents/, which only improvement-agent may write
> (agents/improvement-agent.md#L12). Do not retry, do not route around this, and do not edit the
> rule file yourself. Record the change you wanted as a finding in logs/improvement-log.jsonl per
> skills/how-to-log-an-improvement.md and let an improvement review apply it behind APPROVE
> IMPROVEMENTS.

> BLOCKED by .claude/hooks/protect-system-rules.py: this is a dispatched build-agent subagent
> attempting Write against constraints/, which only improvement-agent may write
> (agents/improvement-agent.md#L12). …

**Step 3 — corroborated against disk, not against the fixture's own report.** A subagent's account
of being blocked is a claim; these are the measurements:

| Labelled measurement | Result |
|---|---|
| `grep -n 'PROBE-LINE' agents/.fixture-probe.md` | `PROBE-LINE: untouched` — the Edit did not land |
| `ls -la constraints/.fixture-probe-2.md` | `No such file or directory` — the Write did not land |
| hook dump, all fires | 4 rows: `improvement-agent`/`Write`/**allow**, `build-agent`/`Edit`/**deny**, `build-agent`/`Write`/**deny**, `improvement-agent`/`Edit`/**allow** |

**Step 4 — cleanup.** `agents/.fixture-probe.md` deleted; the dump file deleted, which is what
turns dumping off. `git status` over the four rule directories shows no fixture residue.

**How to re-prove this after a harness upgrade**, because that is when it will silently stop
working: `touch .claude/hooks/.fixture-dump.jsonl`, dispatch any non-`improvement-agent` subagent
at a file under `agents/`, read the file back. The dump path is inert unless that file exists and
its writer is wrapped so that an unwritable dump can never change a decision.

**One measurement worth recording against the third honest limit.** `permission_mode` came through
as `auto` on all four fires, and the hook still fired and still denied. That does not disprove
[§2.3's sandbox caveat](2026-08-31-improvement-review-9.md#L109) — a mode that bypasses the
permission classifier entirely was not tested and cannot be tested from inside a dispatch — but it
does narrow it: auto-mode alone does not defeat this control.

---

## 5. The honest limits, restated — the control is narrower than the sentence it enforces

Review 9 named three. This review adds a **fourth**, found while writing A1, and it is the one most
likely to be forgotten:

1. **Dispatched agents only.** `agent_id` is absent for the root session, and `lead-agent` *is* the
   root session. The human and the main conversation keep write access. Deliberate — but it means
   the enforced rule is *"no dispatched subagent but improvement-agent"*, not *"nobody but
   improvement-agent"*.
2. **Not a sandbox.** Narrowed but not removed by the `permission_mode: auto` observation above.
3. **The four rule directories only.** `scripts/`, `config/` and `contract/` are uncovered, because
   delivery agents legitimately write some of those.
4. **Write tools only — `Bash` is not covered.** `sed -i`, a heredoc or a python one-liner from a
   dispatched agent is not stopped. Matching a path out of an arbitrary shell command was
   considered and **rejected on this project's own measured evidence**: it is the phrase-matching
   instrument measured at 48–100% false five times across three reviews. All four limits are
   written into the hook's own docstring, where the next person to read the file will meet them.

---

## 6. Findings

| Finding | Disposition |
|---|---|
| `IMP-0556` (appended by this review, `capability: true`) | Records the three undocumented harness properties and the re-proof procedure, so no future session re-derives them from documentation that does not contain them. `reviewed_in` stamped at draft time |
| `IMP-0557` (appended by this review) | The four warnings §1's own honesty produced — see below. Third instance of `gate-fires-on-nothing` at the same predicate; a fourth prose exemption is what the altitude rule forbids, so the proposed remedy is a **declared `excluded_by` field** mirroring `appended_by`. Not applied here: it is a queue-mechanics change, outside this dispatch's reviewer-directed scope |
| `IMP-0558` (appended by this review) | The STALE-HEADER check in `verify-review-document.py` passed a DRAFT header above an Applied section — see §10. Remedy proposed (a fail-closed status allowlist), **not applied**: a gate change needs its own corpus measurement |
| `IMP-0549`–`IMP-0552` (unread) | **Excluded** — out of scope for a reviewer-directed capability dispatch; see §1. The unread trigger stays live |

**Naming those four ids cost 4 warnings, and the ids stay named.** Stating the exclusions took the
validator's warning count from 5 to 9: `check_missing_stamps()` reports each excluded id as *"cited
by 1 review document and carries NO `reviewed_in`"*. The review did the required thing and the gate
read it as an omission, because *"cited in order to declare it out of scope"* is a citation position
that predicate does not model. **The silent cap is the worse defect**, so the ids remain. `IMP-0557`
records it; the other 5 warnings are pre-existing `corrects` edges naming nothing in this review.

## 7. Anti-bloat and scope accounting

**0 new constraints** (cap 3). This change is a script, not a constraint row — the most mechanical
home available, per the anti-bloat rule that a script beats a constraint row beats a paragraph. A
`C-` row saying "only improvement-agent may edit the rules" would have been a fifth `Verify By`
nobody executes; the hook is executed on every write in the repository.

**Retirement considered.** Candidate examined and **rejected**: the declaration at
[`agents/improvement-agent.md#L12`](../../agents/improvement-agent.md#L12) is not retired by A1 —
A3 keeps it and annotates it, because the hook binds dispatched agents only and the prose is what
governs the root session and the human. Retiring the sentence would leave the un-enforced half of
the rule stated nowhere. Live constraint rows: **82**; retired: **10**; both derived, not typed.

**`ls scripts/verify-*.py | wc -l` = 54, unchanged.** This review adds no script to `scripts/`. A1
is a harness hook, not a gate: it belongs in `.claude/hooks/` because that is the only place the
harness reads hooks from, and it is not a `verify-*.py` invoked by a build step.

---

## 8. Routed work

**None.** Nothing is handed to another agent by this review.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-01-improvement-review-6.md

Findings processed: 3 (IMP-0556, IMP-0557, IMP-0558 — all appended by this review)  →  3 clusters
                    4 unread EXCLUDED and reported (IMP-0549..0552) — trigger stays live
Regression check:   4 prior changes audited (review 9 F1/F2/F3 + the A-cluster), 0 classes recurred
Proposed:           0 constraints (cap 3), 1 harness hook + 1 settings registration,
                    0 skill/knowledge edits, 1 agent-file edit, 0 retirements
Altitude calls:     1 generalised from prose declaration to executed enforcement
                    (class declared-policy-not-mechanically-enforced, 24 entries)
Live fixture:       PASSED — build-agent REFUSED on agents/ and constraints/, verified on disk;
                    improvement-agent ALLOWED. Nothing withdrawn.
Digest:             will regenerate

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

## 10. Applied record — 2026-09-01, `APPROVE IMPROVEMENTS`

**Step 8 re-verification ran before anything was written.** `verify-improvement-log.py --check`
exit 0, 554 entries; **no `corrects` or `contests` edge names `IMP-0556` or `IMP-0557`**, checked
by walking every entry's edges rather than by reading the warning text. `agents/improvement-agent.md`
line 12 was re-read and was byte-identical to what A3 was drafted against — no concurrent write.
The hook's self-test was re-run green and `.claude/settings.json` still showed `+19, -0`.

The reviewer independently re-verified the fixture before approving, invoking the hook directly with
fabricated `PreToolUse` JSON across all four cases (`build-agent`/protected → deny, matching the
quoted refusal exactly; `improvement-agent`/protected → allow; root session → allow;
`build-agent`/`src` → allow). **That is the strongest form of confirmation this review has** — the
one measurement not taken by the agent that wanted it to pass.

| # | Change | File | Verification |
|---|---|---|---|
| **A1** | `PreToolUse` hook denying protected writes from non-`improvement-agent` dispatches | [`.claude/hooks/protect-system-rules.py`](../../.claude/hooks/protect-system-rules.py) (new) | `--selftest` **23 assertions, 0 failed**; negative control (guard deleted) turns exactly the 2 root-session assertions red; **live fixture** §4; reviewer's independent 4-case re-verification |
| **A2** | `hooks` block registering A1, **merged** beside WS-E's `permissions.deny` | [`.claude/settings.json#L2`](../../.claude/settings.json#L2) | Parses; `+19 insertions, 0 deletions`; 4 `deny` + 11 `allow` entries intact |
| **A3** | The declaration at line 12 now names its enforcement and both its limits | [`agents/improvement-agent.md#L12`](../../agents/improvement-agent.md#L12) | Needle `protect-system-rules.py` present. **The edit itself passed through the hook as `improvement-agent`** — a fifth live fire, confirming in the real path that the control does not block its own user |

**Bookkeeping, incremental.** `IMP-0556` → `APPLIED` as A3 landed, with an `evidence_grep` pointing
at `permissionDecision` **in the hook** rather than at any sentence this review wrote (`IMP-0208`).
Digest regenerated once, at the end: `--check` **exit 0**.

### One deviation from the approving instruction, stated because it must never be silent

**`IMP-0557` was NOT closed `APPLIED`.** The approval said to close both findings; `IMP-0556` was
closed, and `IMP-0557` was left `NEW` with the `deferred_reason` and `revisit_when` this document
drafted and the pre-gate simulation proved green.

The reason is one measurement: `grep -c excluded_by scripts/verify-improvement-log.py` returns
**0**. `IMP-0557`'s proposed change — a declared `excluded_by` field — is not on disk, was outside
this reviewer-directed dispatch's scope, and nothing in this review implements it. `APPLIED` would
be a claim above the evidence, and its `evidence_grep` needle could only have matched a sentence
this review wrote — the exact construction that closed `IMP-0208` on nothing while the defect was
still live for a real user three days later. An honest open entry beats a closed one nobody fixed.

The queue is unharmed by the choice: `deferred_reason` is the validator's own named second
discharge, so the entry classifies as `reviewer-deferred` rather than `awaiting-approval`, and the
gate reports **0 awaiting-approval** with exit 0. Nothing is left red. If the intent was to close it
regardless, that is a one-line reversal — but it should be a decision taken in view of the grep,
not inherited from a draft.

### A gate that should have caught this document and did not — `IMP-0558`

Applying this review produced a third finding, and it is the most useful thing in it. Two scripted
attempts to flip the status header from DRAFT to APPLIED **silently matched nothing** (the line
wrapping had changed), leaving a `**Status: DRAFT … no finding has moved to APPLIED**` header
sitting above a fully populated §10. That is precisely `IMP-0204`'s defect, and
[`scripts/verify-review-document.py`](../../scripts/verify-review-document.py) exists to catch it —
its own OK line advertises *"no status header contradicts an Applied section"*. **It returned exit
0.** Reproduced deterministically on a scratch copy afterwards rather than asserted: DRAFT header
plus Applied section, **exit 0, OK**.

The cause is vocabulary, not logic:
[`AWAITING_RE`, L197](../../scripts/verify-review-document.py#L197) matches the literal word
`AWAITING` and nothing else, and `DRAFT` is a synonym it does not model. The corpus hid it —
**24** review documents use an AWAITING-shaped header and **0** used DRAFT, so this document was
the first to reach the gate in wording the gate cannot see. The proposed remedy is an **allowlist
that fails closed** rather than a sixth synonym, because subtracting known-innocent shapes is wrong
by construction on the shapes nobody has met yet. Not applied here — it is a gate change needing
its own corpus measurement across all 35 review documents.

Two smaller lessons, both cheap: a `sed`/`str.replace` header rewrite must assert that it matched,
because a no-match is silent; and **a gate's OK line is a claim about what it tested, not about
what is true.**

**One defect this draft committed and the log gate caught.**

**The disposition was simulated before parking, and the simulation caught a second defect.** On a
scratch copy: `IMP-0556` → `APPLIED` with an `evidence_grep` needle pointing at
`permissionDecision` in the hook itself — the mechanism, not a sentence this review wrote
(`IMP-0208`) — and `IMP-0557` left `NEW` with a `deferred_reason` and a `revisit_when`, which is
the gate's own named second discharge rather than the bare-`revisit_when` red light of `IMP-0516`.
First run: **FAILED** — `evidence_grep` must be an object, and the draft had it as a string.
Corrected and re-run: **exit 0**, 123 NEW / 4 unread / 0 awaiting-approval, no trigger left
standing except the pre-existing unread four. The real log was never written to; only the scratch
copy moved.

**One defect this draft committed and the log gate caught.** `IMP-0557` was first appended
carrying `reviewed_in` against a document that did not yet name it. The validator refused the log:
*"a review that WROTE a finding has not thereby PROCESSED it … no keyword can dispose of it and
the entry is unreachable."* Fixed at the document, not at the stamp — §6 now names it. Recording
this because a gate that fires and is obeyed is the only evidence a gate works.
