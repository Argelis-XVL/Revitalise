# Improvement Review 8 — WS-O second half, and IMP-0561 re-measured (2026-09-01)

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`~~ → **APPLIED 2026-09-01.** All three items are on
disk. See §6, the applied record.

**Why a new document rather than an amendment to review 7:** review 7 is `APPLIED`. Appending
unapproved proposals to it would produce a document whose status header contradicts its body —
precisely the defect the status-token allowlist shipped in review 7 exists to catch. A parked
proposal gets its own document.

---

## 0. Conclusion first

**Item 1 is ready to apply and measures well.** The `WORKFLOW.md` narrative extraction is drafted,
10.0% smaller, all five needles intact, and a **genuinely fresh root session** answered three
mandatory-rule questions correctly against the draft.

**Item 2 dissolved on measurement. `IMP-0561` is FALSE and I am asking you to reject it, not fix
it.** The gate it accuses has been correct all along. My original measurement read an exit status
through a pipe — the exact defect this repository's instructions name in the file I had rewritten
four hours earlier.

---

## Item 1 — WS-O for `agents/WORKFLOW.md`

### What it does

Moves the incident narrative out of the dispatch-death section (lines 61–268, **208 of 529 lines**)
into [`agent-instruction-history.md`](docs/improvements/agent-instruction-history.md), alongside the
`improvement-agent.md` material relocated in review 7. Every rule keeps its imperative voice and its
position; only justification moves.

### Measurements

| Property | Before | After |
|---|---|---|
| Size | 32,435 B / 529 lines | **29,176 B / 485 lines** |
| Reduction | — | **3,259 B, 10.0%** |
| `evidence_grep` needles into the file | 5 | **5 intact, 0 broken** |
| Heading count | — | **identical** |
| Gate-keyword table rows | 16 | **16** |

The needle check ran **before** any text was moved. All five (`IMP-0172`, `IMP-0291`, `IMP-0357`,
`IMP-0490`, `IMP-0520`) are section headings or rule text rather than narrative, which is why the
technique applies cleanly here.

### The fixture — and why it is a different fixture from review 7's

Review 7 held this half back on the grounds that `WORKFLOW.md`'s reader is `lead-agent` — the **root
session** — rather than a bounded dispatch, so it could not inherit review 7's subagent fixture. So
this one is a root session: a scratch tree containing `CLAUDE.md`, `agents/lead-agent.md` and the
**draft** `WORKFLOW.md`, with a fresh `claude -p` session started in it. It loaded `CLAUDE.md`,
announced *"Lead Agent ready"*, and answered:

| Question | Answer |
|---|---|
| Must I state anything in a dispatch prompt about long-running steps? | **Correct** — quoted the required blockquote verbatim and noted the reason must accompany it |
| May I resume with `SendMessage` and pass a model override? | **Correct** — "No", with the no-`model`-parameter reason and `IMP-0399` |
| Is an empty `pipeline.log` + unchanged mtime sufficient evidence no live write happened? | **Correct** — "No", cited the medium-decides rule, `IMP-0484`, and named the idempotent live probe |

It returned the canary `CANARY-WSO-8842` planted at the end of the scratch digest, which is what
distinguishes reading the files from confabulating plausible answers.

**What this fixture does NOT prove.** It does not reproduce context pressure — a real root session
carries a long conversation this probe does not have — and no fixture I can construct does. The
property measured is the one at risk from a text edit: whether the rewritten wording still compels
the rules. It does.

### Residual

The relocation adds ~150 lines to `agent-instruction-history.md`. That file is read on demand, never
at activation, so the bytes leave every session's fixed cost and land somewhere nothing loads by
default — the same contract the digest's appendix operates under.

---

## Item 2 — `IMP-0561` is withdrawn, not fixed

### What the finding claimed

That `scripts/verify-review-document.py --only <bare filename>` exits 0 having checked nothing — "a
gate that checked nothing reporting clean", logged as `gate-cannot-fail`.

### What it actually does

| Invocation | Exit |
|---|---|
| bare filename (bad argument) | **2** |
| full path, document has findings | **1** |
| full path, clean document | **0** |

Three distinct codes, all correct. The source has carried `return 2` in that branch all along.

### How the false finding happened

The original measurement was:

```bash
python3 scripts/verify-review-document.py ... | tail -3; echo "exit=$?"   # reports TAIL's status
```

`$?` after a pipe is the **last** command's status, so it reported `tail`'s 0. Re-run redirecting to
a file instead, the same invocation reports 2.

**This is the defect named verbatim in `agents/improvement-agent.md`** — *"Never read a command's
exit status through a pipe. `cmd | tail` gives you `tail`'s status, which is 0 almost always"* — and
I committed it while rewriting that very file, four hours after re-authoring that sentence. It is
the same shape as `IMP-0542`, where an agent that had read `IMP-0007`'s lesson at activation chained
greps with `&&` anyway. Knowing the rule does not prevent it; the shell being used as a notepad
rather than as a gate is when it happens.

It was caught only because this dispatch opened the source to write the fix and found the fix
already there — which is step 8's *"where the assertion is about a script's BEHAVIOUR, EXECUTE it"*,
the step the original finding skipped because it believed it already had an execution result.

### Blast radius — measured, and it is zero

`--only` appears in **8** places, all inside review documents recording their own self-check. **Six
documents claim a `--only` self-verification.** Re-run with the correct full-path form, **all six
exit 0** — so no false clean was ever recorded. The wired build step
([`build.yml:111`](config/revitalise-grant-automation-build.yml#L111)) uses the **directory** form
with `--warn-only` and never touched the branch.

**But the finding is not harmless**, which is the reason this needs a keyword rather than a
shrug: its lesson text is rendering **right now** in
[`known-failure-modes-appendix.md`](logs/known-failure-modes-appendix.md), telling every future
reader to work around a defect that does not exist. A false lesson in a generated read path is worse
than no lesson.

### Proposed

1. `IMP-0561` → `REJECTED`, with a `rejected_reason` recording the pipe mis-measurement.
2. Regenerate the digest so the false lesson stops rendering. (`REJECTED` findings are excluded from
   the digest by design — *"a REJECTED finding must stop teaching"*.)
3. **No code change.** The proposed fix is already the code's behaviour.

`IMP-0564` is appended and carries `corrects: IMP-0561`, so the queue gate now surfaces the
contradiction to any review that opens either.

---

## Item 3 — the appendix drops the "this lesson was disproved" warning

**Found while verifying item 2's own remedy**, which is the only reason it surfaced: I regenerated
the digest expecting `IMP-0561`'s false lesson to now carry a `⚠ CORRECTED by IMP-0564` marker, and
it did not.

### The defect

[`render()`](scripts/generate-known-failure-modes.py) emits a `⚠ CORRECTED by <id>` / `⚠ CONTESTED
by <id>` sub-line beneath any lesson a later finding contradicts. **`render_appendix()` does not.**
Its `emit()` writes the lesson and its ids and nothing else.

Because the appendix is where every lesson the per-section cap excludes actually lives, **a
disproved lesson that falls past the cap loses its warning entirely and reads as authoritative.**

### Measured

| | Digest | Appendix |
|---|---|---|
| `CORRECTED` markers rendered | 10 | **0** |
| `CONTESTED` markers rendered | 1 | **0** |

**10 lessons carrying a correction or contest marker render ONLY in the appendix**, unmarked:
`IMP-0298`, `IMP-0326`, `IMP-0328`, `IMP-0425`, `IMP-0428`, `IMP-0430`, `IMP-0437`, `IMP-0438`,
`IMP-0539`, `IMP-0561`.

### Why nothing caught it

The generator's selftest asserts every capped lesson *appears* in the appendix — a **presence**
check. Nothing compares what the two renderers say *about* the same lesson, so an annotation present
in one and absent in the other is invisible. Same shape as `IMP-0563`: a second renderer did not
inherit the first one's guarantees.

### Proposed

Factor the marker emission into one helper called by **both** `emit()` functions, and add the
assertion that would have caught it — a **comparison between the renderers**, not a presence check
inside either: every lesson carrying a `corrects`/`contests` marker renders that marker in whichever
file it appears in.

Logged as `IMP-0565`. Proposed, not applied.

**Note the interaction with item 2:** rejecting `IMP-0561` removes it from both files, since
`REJECTED` findings stop teaching. That fixes one of the ten. The other nine need item 3.

---

## 2. Anti-bloat accounting

| Limit | This review |
|---|---|
| New constraints (cap 3) | **0** |
| Retirement considered | **Yes** — `IMP-0561`'s lesson is the retirement candidate, and item 2 is the mechanism |
| New scripts | **0** — verify-script count stays 55 |
| Mechanical verification | Item 1: needle check, size, structure, root-session fixture. Item 2: three exit paths executed directly, no pipe |

---

## 3. Findings

| Finding | State |
|---|---|
| `IMP-0564` | Appended. Corrects `IMP-0561`; records the pipe-status trap as a second instance of the knew-the-rule-anyway shape |
| `IMP-0565` | Appended. The appendix drops correction/contest markers — item 3 |
| `IMP-0561` | Proposed `REJECTED` — **not moved**, awaiting the keyword |

---

## 4. What you need to decide

**Approve item 1 — apply the `WORKFLOW.md` narrative extraction?**

**Problem** — `agents/WORKFLOW.md` carries 208 lines of incident narrative in its dispatch-death section, loaded by the root session at every session start.
**Suggested fix** — Apply the drafted rewrite: 10.0% smaller, five of five needles intact, root-session fixture green.
**What happens if you don't** — The second half of an approved workstream stays undone and the file keeps growing with each dispatch-death variant.
[`agents/WORKFLOW.md`](agents/WORKFLOW.md)

---

**Approve item 2 — reject `IMP-0561` and regenerate the digest?**

**Problem** — `IMP-0561` is false; the gate it accuses is correct, and its lesson is currently teaching a workaround for a defect that does not exist.
**Suggested fix** — Mark it `REJECTED` with the mis-measurement recorded, and regenerate so it stops rendering.
**What happens if you don't** — A false lesson stays in the generated read path, and a future review may "fix" a gate that is already right.
[`logs/known-failure-modes-appendix.md`](logs/known-failure-modes-appendix.md)

---

**Approve item 3 — make the appendix render correction markers?**

**Problem** — The appendix drops the `⚠ CORRECTED` / `⚠ CONTESTED` warnings the digest shows, so 10 disproved or disputed lessons currently read as authoritative in the file readers are sent to for capped detail.
**Suggested fix** — One shared marker helper called by both renderers, plus a selftest that compares the two rather than checking presence inside either.
**What happens if you don't** — Nine lessons (ten, minus the one item 2 removes) keep teaching conclusions a later finding has already contradicted, in the exact place the digest tells people to look.
[`scripts/generate-known-failure-modes.py`](scripts/generate-known-failure-modes.py)

---

## 5. Verification executed

| Check | Result |
|---|---|
| `verify-improvement-log.py` (bare) | **OK** — 561 entries |
| Needle check against the draft | **5 of 5 intact** |
| Draft size | 32,435 → 29,176 B (**−10.0%**) |
| Root-session fixture | **PASS**, canary returned |
| `--only` exit paths, no pipe | **2 / 1 / 0**, all correct |
| Six `--only`-claiming documents re-verified | **all exit 0** — no false clean ever recorded |

**Level: V1** throughout, plus **V4-equivalent** for item 1's fixture (a real session read the draft
and behaved correctly).

**Not verified:** context-pressure behaviour of a long-running root session against the shortened
file. No fixture reproduces it and I am not claiming it.

---

## 6. Applied record — 2026-09-01, on `APPROVE IMPROVEMENTS`

Re-verified before writing, per step 8: no `corrects` entry named anything acted on here, the draft
was byte-identical to the one measured, and all 5 needles re-checked against the live 562-entry log.

### Item 1 — `agents/WORKFLOW.md`

Applied from the scratch draft. **32,435 → 29,176 bytes, 529 → 485 lines (−10.0%).** Needles
re-checked **against the live file after the write**: 5 of 5 intact. The narrative landed in
[`agent-instruction-history.md`](docs/improvements/agent-instruction-history.md) under a new
*"From `agents/WORKFLOW.md`"* part, and the draft's two pointers to *The fourth case* resolve to a
real section. That file's header was updated — it now carries material from two agent files, not one.

### Item 2 — `IMP-0561` → `REJECTED`

`rejected_reason` records the three measured exit codes (2 / 1 / 0), the pipe-status cause, and the
zero blast radius. **The false lesson is gone from both read paths** — `grep` returns 0 in the digest
and 0 in the appendix.

### Item 3 — one marker helper, two renderers

`correction_markers()` extracted and called by `render()`'s `emit()` **and both appendix emit paths**
(Part 2 capped lessons, Part 3 truncated lessons); `corrections_of()` / `contests_of()` are now
computed inside `render_appendix()`, where they were absent.

| | Before | After |
|---|---|---|
| Appendix `⚠ CORRECTED` | 0 | **12** |
| Appendix `⚠ CONTESTED` | 0 | **3** |
| Digest | 10 / 1 | 10 / 1 (unchanged) |

**Mutation-tested, which is the part that matters.** Reverting *only* the appendix half and re-running
the new assertion fails with **9 unmarked lessons named** — exactly the nine this document predicted
would remain after item 2 removed the tenth. That is a can-it-fail proof against the real defect
rather than a synthetic fixture.

The new assertion is deliberately a **comparison between the two renderers**. Every pre-existing
assertion checked a property inside one of them, which is why a marker present in `render()` and
absent from `render_appendix()` satisfied all of them.

### Bookkeeping

`IMP-0564` and `IMP-0565` closed `APPLIED` with `evidence_grep` needles. `IMP-0562` and `IMP-0563`
remain `NEW` — appended by review 7, not processed here. One derived count this review drifted (the
digest line count, 622 → 621, because a rejected finding stops teaching) corrected; the other five
drifts are pre-existing delivery-side counts and are not this review's.
