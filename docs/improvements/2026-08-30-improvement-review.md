# Improvement Review — 2026-08-30 (review 44)

**Agent:** improvement-agent (tier `strategic`)
**Status:** **APPLIED 2026-08-30** — `APPROVE IMPROVEMENTS` received; all 4 changes on disk. One
deviation and one entry left deliberately open; both in §11.
**Findings processed:** 4 NEW → 4 clusters
**Trigger:** unread `blocker` [`IMP-0499`](../../logs/improvement-log.jsonl), per [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L1064)'s STATE-1 rung
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

**The blocker's artefact defect is already fixed on disk — a parallel dispatch landed the two
missing rows at 11:22 while this review was being drafted, and I verified them rather than
taking them on faith. What remains is the class half, and it is the sixth instance.**

Four changes are proposed: zero new constraint rows, one constraint amendment, one agent-file
schema addition, one agent-file sentence, one knowledge line. The mechanical gate that
[`IMP-0323`](../../logs/improvement-log.jsonl) asked for in its `revisit_when` is **deferred with a
named precondition, because I measured its input and the input does not exist yet** — see §6.

**What the reviewer needs before the queued build re-dispatch:**
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) **is red now and stays
red until the keyword arrives.** Stamping `reviewed_in` does not clear a `blocker` — the gate
fails on `unread` *and* `awaiting-approval` alike
([`verify-improvement-log.py` L123](../../scripts/verify-improvement-log.py#L123)). Only moving
`IMP-0499` out of `NEW` clears it, and that happens on approval. See §7.

**Scope excluded, per the no-silent-caps rule.** 92 entries sit at `reviewer-deferred` and were
not read; 0 at `awaiting-approval`; 0 at `already-fixed`. `APPLIED` and `REJECTED` were not read —
the digest carries their lessons. This dispatch was scoped to `IMP-0499`; I also processed the
three other `unread` entries ([`IMP-0496`](../../logs/improvement-log.jsonl),
[`IMP-0497`](../../logs/improvement-log.jsonl), [`IMP-0498`](../../logs/improvement-log.jsonl))
because leaving them unread only defers the next batch trigger, and all three are one-line
dispositions.

---

## 1. Regression check — did review 43's changes work?

Every claim below is a **run**, not a re-read, per
[`improvement-agent.md` L150](../../agents/improvement-agent.md#L150).

| Prior change | From | Class it targeted | Recurred? | Verdict |
|---|---|---|---|---|
| [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py) prints baselined status findings by name | r43 ch2 | `gate-reassures-wrongly` | NO | **Working.** Re-run: both suppressed findings now print with owner, expiry and clearing action. This is the half of `IMP-0497` already fixed |
| [`verify-flow-definition-language.py`](../../scripts/verify-flow-definition-language.py) check-7 exception retired | r43 ch3 (withheld; replaced by source fix) | `gate-cannot-fail` | NO | **Working.** Re-run: exit 0, `REVPortalRoundStatistics` carries no exception; the 2 remaining are on other, untouched flows and print in full |
| [`verify-code-app-data-sources.py`](../../scripts/verify-code-app-data-sources.py) reads the shared register | r42 ch1 | `gate-cannot-fail` | NO | **Working.** Re-run: `OK — 7 registration(s), 7 Dataverse source(s) declared`, exit 0 |
| [`improvement-agent.md` L125](../../agents/improvement-agent.md#L125) stamp `reviewed_in` at draft time | r42 ch6 | `learning-substrate-destroyed` | NO | Working — this review stamps all four entries as part of drafting |
| [`build-agent.md` L60](../../agents/build-agent.md#L60) two placeholders for a shared build config | r43 ch1 | `gate-invocation-omits-required-arg` | NO | Working — this build resolved `build/artifacts/trustee-portal-visual-refresh-20260830-1/` correctly |

**Recurred after a prose change:** none. **Recurred after a gate:** none.

**One class did recur, and against nothing — because nothing was ever built for it.**
`untriaged-tool-warning` is now ×6. That is cluster A, and it is not a regression of review 43;
it is `IMP-0323`'s unactioned `revisit_when` coming due for the third time.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: untriaged-tool-warning  (x6: IMP-0177, IMP-0214, IMP-0323, IMP-0393, IMP-0411,
                                        IMP-0499 — 1 new this review)
Altitude:   CLASS — sixth instance, and the third closed by hand-adding a Dev Summary row,
            which skills/how-to-promote-a-finding.md L44 forbids from the second instance on
Ladder row: "a tool could catch it mechanically" — BLOCKED on its input not existing.
            Falls back to "an agent had the information and still did the wrong thing"
Becomes:    (change 1) build-agent.md's manifest schema gains a declared warnings_detail[]
                       carrying {step, signature, status, triaged_in} — the input the diff
                       gate needs, which build-agent is already improvising in 4 manifests
            (change 2) C-TECH-055 amended to say WHICH Dev Summary: the current feature's own
Retires:    nothing
Cites:      IMP-0177, IMP-0214, IMP-0323, IMP-0393, IMP-0411, IMP-0499
Residual:   THE GATE IS NOT BUILT, and §6 is the measurement that says why. The raw warning
            stream is gitignored (build/artifacts/** except manifest.json), and the one
            tracked surrogate takes 5 different shapes across 9 key names in 22 manifests.
            Deferred with a precondition, not dropped: revisit when 3 manifests carry the
            declared warnings_detail[]. That is a real trigger, unlike IMP-0323's "next
            improvement review", which fired three times and produced nothing.
```

```
CLUSTER B: platform-fact-groundtruthed  (x1: IMP-0496)
Altitude:   INSTANCE — one instance, cause is general, a human needs to know it
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge/
Becomes:    (change 3) a note in knowledge/technology/power-automate.md
Retires:    nothing
Cites:      IMP-0496
Residual:   PREMISE PARTLY WRONG, corrected here rather than at application time. The entry's
            proposed_change says to add the note "under the existing result()/IMP-0109
            material". Measured: knowledge/technology/power-automate.md contains ZERO
            occurrences of `result(` and no IMP-0109 reference across its 444 lines. There is
            no existing material to sit under, so the note is written as a new subsection.
            The assumption itself stays OPEN as A-FLOW-13; a knowledge line does not close it.
```

```
CLUSTER C: gate-reassures-wrongly  (x1 new: IMP-0497)
Altitude:   LOG NOTE — the entry proposes its own deferral and I agree with it
Ladder row: "one instance, specific, no general mechanism" → stays a log note
Becomes:    nothing on disk. Deferred with a measured deferred_reason
Retires:    nothing
Cites:      IMP-0497
Residual:   The open half is REAL and I re-measured it live for this draft:
            `grep -rln "note_claimed|\.unused" scripts/ --include='*.py' | grep -v lib/`
            returns NOTHING — zero callers outside the library. So a baseline whose debt has
            been paid is reported by nobody and waits on its expiry date. No incident yet;
            second instance decides between the entry's two candidate altitudes.
```

```
CLUSTER D: agent-instructions-describe-a-topology-that-changed  (x1: IMP-0498)
Altitude:   INSTANCE → agent file. The information existed and was not acted on
Ladder row: "an agent had the information and still did the wrong thing" → agents/
Becomes:    (change 4) one sentence in development-agent.md's Sub-Agents section
Retires:    nothing
Cites:      IMP-0498, IMP-0143, IMP-0470
Residual:   NOT mechanically enforceable, and the entry says so correctly: a Task-tool
            dispatch is a prompt, never a file, so no gate can assert one occurred. This
            change makes the omission VISIBLE in the gate output; it cannot prevent it.
```

---

## 3. Proposed changes

| # | Type | Target | What |
|---|---|---|---|
| 1 | agent | [`agents/build-agent.md` L251](../../agents/build-agent.md#L251) | Add `warnings_detail[]` to the declared manifest schema: one object per warning-producing step, `{step, signature, status, triaged_in}`, where `triaged_in` is the document **and line** carrying the rationale |
| 2 | constraint amendment | [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) | Name which Dev Summary: *"the Dev Summary of the feature being built"*, and state that a rationale living in another feature's document satisfies the rule only via a citing row in this one |
| 3 | knowledge | [`knowledge/technology/power-automate.md`](../../knowledge/technology/power-automate.md) | New subsection: `result()` is documented for `Scope`/`For_each`/`Until` only; `Switch`/`If` are neither confirmed nor denied; points at `A-FLOW-13` |
| 4 | agent | [`agents/development-agent.md` L86](../../agents/development-agent.md#L86) | One sentence: where a dispatch names a sub-agent and the work is judged inseparable, say so in the gate output — *"sub-agent fan-out not performed — reason"* |

**No new constraint rows** (cap 3, used 0). Change 2 is an amendment to an existing row.

---

## 4. Retirements

**Checked, and I am naming no candidate.** Derived, not typed:
`grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10 retired**;
`grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → **80 live**.

`C-TECH-055` was the obvious candidate — six instances of one class is often a sign the rule is
wrong. It is not: the rule **fired correctly** this build and caught a real omission. What is
wrong is that it fires at step 68 of 68 and depends on an agent remembering. That is an argument
for the gate in §6, not for retiring the row.

---

## 5. Findings left unprocessed

93 at `reviewer-deferred`, listed in full by
[`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py). One of them,
[`IMP-0274`](../../logs/improvement-log.jsonl), still carries **no `revisit_when`** — a deferral
with no trigger to come back is a decision never to do it. Flagged, not fixed: it is outside this
dispatch's scope and needs a reviewer decision, not an agent's.

**One finding was logged BY this review and is not counted in the 4 processed above.**
[`IMP-0500`](../../logs/improvement-log.jsonl) records §6's measurement — a declared manifest
schema with 22 non-conforming instances — so that evidence lives in the log the digest reads, not
only in this document. It is appended already `reviewer-deferred`, with a `revisit_when` naming a
countable precondition (three manifests carrying the new shape), because its constructive half
**is** change 1 and awaits this same keyword. It forms no new cluster; it is cluster A's evidence.

---

## 6. Measurement — why the gate IMP-0323 asked for is not in this review

`IMP-0323` named the mechanical home precisely: *"nothing diffs a build step's warning output
against the Dev Summary's Tool warnings triaged table."* I tried to build it and **measured the
input first**, per [`improvement-agent.md` L406](../../agents/improvement-agent.md#L406).

**Fact 1 — the raw warning stream is not committed.**
[`.gitignore` L10](../../.gitignore#L10) excludes `build/artifacts/**`, with a single exception at
[L12](../../.gitignore#L12) for `manifest.json`. No committed artefact carries what a build step
actually printed.

**Fact 2 — the one tracked surrogate is free-form prose in five shapes.** Measured across all
**22 tracked manifests**:

| Shape of the `warnings` block | Manifests |
|---|---|
| `warnings: null` / absent | 6 |
| `warnings.detail` = LIST | 6 |
| `warnings.detail` = STRING | 4 |
| counts only, no detail | 3 |
| separate `warnings_detail[]` list | 3 |

and the keys used inside `warnings{}` across the corpus are **nine distinct names**: `accepted`,
`accepted_preexisting`, `accepted_reviewer_soft`, `accepted_this_dispatch`, `detail`,
`notes_triaged_not_warnings`, `resolved`, `total`, `untriaged`.

**Fact 3 — a schema is already declared, and nothing enforces it.**
[`build-agent.md` L251](../../agents/build-agent.md#L251) declares
`"warnings": { "total", "resolved", "accepted", "untriaged" }`. The corpus uses nine keys. And
`warnings_detail[]` — the only field that would make the diff possible — **is not in the declared
schema at all**, yet build-agent has invented a near-miss version of it in 3 manifests.

**So the gate would have to diff one hand-written prose field against a hand-written prose
table.** That is the *assert-on-phrases* instrument this project has now measured five times at
48%–100% false ([`IMP-0422`](../../logs/improvement-log.jsonl),
[`IMP-0428`](../../logs/improvement-log.jsonl)), and
[`improvement-agent.md` L454](../../agents/improvement-agent.md#L454) says to assert on **values**
wherever a value exists. Today no value exists.

**And the one value that does exist is disqualified.** `warnings.untriaged` is an integer, and a
gate asserting it is `0` would read **build-agent's own conclusion about its own work** — not
independent evidence. That is a `gate-reassures-wrongly` in the making, which is the class
`IMP-0497` recorded in this same batch.

**Therefore: change 1 builds the input, and the gate is deferred behind it.** Once three
manifests carry a conforming `warnings_detail[]`, the diff is a value comparison — `step` +
`signature` against the table's rows — and it can be measured against a real corpus the way this
project requires. Wiring it as HARD today would also go red against 22 legacy manifests over work
no current dispatch owns, which is exactly the mistake
[`gate-baselines.json`](../../config/gate-baselines.json) exists to prevent
(`IMP-0439`, `IMP-0320`).

---

## 7. `C-TECH-061` after this gate opens — and what the queued build will see

**Red, and it cannot be otherwise until the keyword arrives.**

[`verify-improvement-log.py` L123](../../scripts/verify-improvement-log.py#L123) requires *"zero
`NEW` entries of severity `blocker` in state `unread` **or** `awaiting-approval`"*. Stamping
`reviewed_in` on `IMP-0499` moves it from STATE 1 to STATE 2
([L1064](../../scripts/verify-improvement-log.py#L1064),
[L1081](../../scripts/verify-improvement-log.py#L1081)) — **the same exit code, a different
message**. That is deliberate: a blocker parked at a gate is still a blocker.

So the sequence is fixed, and there is no way to shorten it:

1. This gate opens. `C-TECH-061` red — STATE 2, naming this document as the remedy.
2. Reviewer sends `APPROVE IMPROVEMENTS`.
3. `IMP-0499` closes `APPLIED` (its `observable_at` is `n/a`, so no `reobserved` is required —
   and the closure is honest: the two rows are on disk and I read them).
4. `C-TECH-061` exits 0. **Then** build-agent re-dispatches.

**Dispatching build-agent before step 2 will fail at the `improvement-log-check` step**, ~1s in,
exactly as it is designed to.

---

## 8. Digest impact

**Already regenerated**, because this review appended `IMP-0500` and the log changed:
**497 entries, 496 distinct teaching lessons, 588 lines**, and
`generate-known-failure-modes.py --check` reports it current.

[`logs/known-failure-modes.md` L52](../../logs/known-failure-modes.md#L52) now carries
`untriaged-tool-warning` at **×6** — one of the most-recurred classes on the project, and the
`x{n}` marker is precisely the signal the digest header describes as *"the system telling you a
general gate is missing where an instance patch was applied."*

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-30-improvement-review.md

Findings processed: 4 NEW  →  4 clusters
Regression check:   5 prior changes audited, 0 classes recurred against them
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 knowledge edit,
                    2 agent-file edits, 1 constraint amendment, 0 retirements
Altitude calls:     1 generalised from instance to class (cluster A), 1 deferred with a
                    named precondition (the diff gate), 2 left as instance/log notes
Digest:             REGENERATED — 497 entries, 496 lessons, untriaged-tool-warning at x6

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 11. Applied — 2026-08-30

All four changes are on disk. Re-verification per
[`improvement-agent.md` L144](../../agents/improvement-agent.md#L144) found **no `corrects` entry
naming any of the four findings**, and every premise re-measured true except one, corrected below.

| # | Landed at | Verified |
|---|---|---|
| 1 | [`agents/build-agent.md` L251](../../agents/build-agent.md#L251) — `warnings_detail[]` in the declared manifest schema, plus the three authoring rules beneath it | Schema block and prose present |
| 2 | [`C-TECH-055`](../../constraints/technology/technology-constraints.md#L110) — amended to name the current feature's own Dev Summary; a rationale elsewhere counts only via a citing row here | [`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py) PASS — 94 paths across 80 active rows resolve |
| 3 | [`knowledge/technology/power-automate.md`](../../knowledge/technology/power-automate.md) — new subsection on `result()`'s documented scope, and the nesting-caveat trap | Written as a **new** subsection, per the corrected premise below |
| 4 | [`agents/development-agent.md` L104](../../agents/development-agent.md#L104) — the `sub-agent fan-out not performed — <reason>` gate-output line | Present in the Sub-Agents section |

### Deviation — one, and it is an addition to approved text

Change 2's approved wording covered *which* Dev Summary. Applying it, `C-TECH-055`'s `Verify By`
was found to cite **Dev Summary §7**, which is *"Known Limitations / Deferred Items"* in
[`templates/dev-summary-template.md` L39](../../templates/dev-summary-template.md#L39) and has
never held a warnings table. The warnings table is
[§11, *"Verification Evidence (C-TECH-053, C-TECH-055, C-TECH-056)"*](../../templates/dev-summary-template.md#L91)
— the section that names this very row. Corrected §7 → §11 in the same edit, citing the template
rather than either Dev Summary, because the template is the authority and the parent feature's
table sits under an appended feature heading rather than a numbered §11. **This is beyond the
approved wording**, which is why it is recorded here, in `IMP-0499`'s `applied_by`, and in the gate
output.

### `IMP-0496` is APPLIED-but-OPEN, and that is the honest state

Change 3 landed; the entry did **not** close.
[`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) refused it and is right to:
`observable_at` is `V2`, and the only needle available was a prose match on the knowledge file —
*the sentence this review had just written*. That is precisely the shape that closed `IMP-0208`
while the defect was still live ([`IMP-0224`](../../logs/improvement-log.jsonl),
[`IMP-0225`](../../logs/improvement-log.jsonl)). The needle was **removed** rather than kept,
following [`IMP-0497`](../../logs/improvement-log.jsonl)'s precedent of carrying none rather than
one that reports the whole finding as shipped.

It now sits `reviewer-deferred` with a `revisit_when` naming who can close it and how:
`A-FLOW-13` needs a designer save with no validation error (V2) **and** one live run failing inside
`Condition_page_cap` (V5), against DEV — which no agent session in this repository can perform.
A knowledge note does not close a platform assumption.

### Closures

`IMP-0499` **APPLIED** — the artefact half was verified on disk, not taken on faith: both rows are
present in the current feature's Dev Summary at
[L2118](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L2118) (`glob@10.5.0`)
and [L2119](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L2119) (Keyborg),
each Accepted with the rationale carried forward. `observable_at` is `n/a`, so no `reobserved` is
required. `IMP-0498` **APPLIED**. `IMP-0497` and `IMP-0500` remain deferred as drafted.

### Gate results after application

`verify-improvement-log.py --check` **OK** — 497 entries, 95 NEW, 401 APPLIED, 1 REJECTED, 0
unread, 0 awaiting-approval. **`C-TECH-061` exits 0; the queued build-agent re-dispatch is
unblocked.** Digest regenerated: **497 entries, 496 lessons, 588 lines**, `--check` current.
`verify-derived-counts.py` reports **3 drifted claims (SOFT)** — all three are secured-column
counts in delivery documents, pre-existing, untouched by this review and not its to fix.

No script was added, so the `improvement-agent-verify-script-count` figure is unchanged.

---

## 10. On-disk state at draft time

**Superseded by §11 — this section records the state at DRAFT time and is kept as written.**

**Nothing in this document is on disk.** The four entries carry `reviewed_in` naming this
document — stamped at draft time per
[`improvement-agent.md` L125](../../agents/improvement-agent.md#L125) — and their `status` remains
`NEW`. No `applied_by` exists yet.

An `Applied` section is added to this document at application time, not now: the heading itself is
what [`verify-review-document.py`](../../scripts/verify-review-document.py#L467) reads as the claim
that changes have landed, and this draft tripped that check on its first run for carrying one over
an `AWAITING` header. Caught by the gate, not by review.
