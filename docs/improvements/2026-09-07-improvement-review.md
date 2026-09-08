# Improvement Review — 2026-09-07

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 2 clusters
**Trigger:** blocker escalation — [IMP-0638](../../logs/improvement-log.jsonl#L635) and [IMP-0640](../../logs/improvement-log.jsonl#L637), both `blocker`/`unread`, blocking the `revitalise-grant-automation` build at its `improvement-log-check` step
**WBS:** 3.2, 3.4, 3.4 (phase-1 DocuSign two-import workaround)
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**The fix is real and I re-verified it by execution. But stamping this draft cannot clear the build — only approval can.** The blocker rung of [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py#L124) passes only on *"zero `NEW` entries of severity `blocker` in state `unread` **or** `awaiting-approval`"*, and a stamped-but-unapproved entry is `awaiting-approval`. I simulated both dispositions rather than reasoning about it:

| Simulated disposition | Gate exit |
|---|---|
| This draft parked — `reviewed_in` stamped, `status` still `NEW` | **1** (trigger now reads *"in state `awaiting-approval`"*) |
| Full closure — `status: APPLIED`, `corrects`, `reobserved`, `evidence_grep` | **0** |

So the answer to *"re-run `--check` and confirm it exits 0"* is: **it exits 1 now, by design, and exits 0 the moment the keyword lands.** I have not claimed otherwise anywhere in this document. The real log is byte-unchanged by the simulation; both scratch copies were written to the scratchpad.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) build step + `check_suite_gates_are_steps()` in [`verify-build-config.py`](../../scripts/verify-build-config.py) — [IMP-0285](../../logs/improvement-log.jsonl#L282)'s class fix | 2026-08-24 (review 26) | `learning-substrate-destroyed` | **YES — [IMP-0640](../../logs/improvement-log.jsonl#L637)** | **The gate worked.** See below — this is not `gate-cannot-fail` |
| [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md) — `manifest-narrates-its-own-disposition` and siblings | 2026-09-06 | 3 classes | NO | Working — leave alone |

**The distinction that decides this review's altitude.** [IMP-0285](../../logs/improvement-log.jsonl#L282)'s gate **fired exactly as designed**: it caught the unclosed blocker at step 3 of 72 in about a second, where the founding instance burned a full nine-minute build before failing at step 39. The recurrence is therefore *not* a defect in the detection — it is that nothing tells the **fixing** dispatch to close the finding it just fixed. So this does not escalate to a new gate; it lands on the agent file of the agent that skipped the write.

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** `learning-substrate-destroyed` — and the gate **did** fire, so no `gate-cannot-fail` finding is logged. Logging one would be false.

**Closure-level audit.** [IMP-0638](../../logs/improvement-log.jsonl#L635) is `observable_at` **V2** and is closed on a V2 re-observation I performed myself — the gate that refused the build, re-run against the real solution root. [IMP-0639](../../logs/improvement-log.jsonl#L636) and [IMP-0640](../../logs/improvement-log.jsonl#L637) are V1 and close on source state.

---

## 2. Clusters and promotion decisions

```
CLUSTER: hard-gate-has-no-scoped-override-path  (x2: IMP-0638, IMP-0639)
Altitude:   INSTANCE — and deliberately so; see the corpus measurement below
Ladder row: "a tool could catch it mechanically" — already satisfied; the tool is
            scripts/lib/gate_baseline.py and the instance is now wired to it
Becomes:    NOTHING NEW. The fix already landed (IMP-0639) and I re-verified it by
            execution. IMP-0638 closes APPLIED against it; IMP-0639 closes APPLIED
            carrying corrects:IMP-0638 — the link whose absence caused IMP-0640.
Retires:    nothing
Cites:      IMP-0638, IMP-0639
Residual:   The gate is now wired, but NOTHING asserts that the next HARD gate needing a
            scoped exception will be wired before a dispatch depends on it. That residual
            is accepted, not fixed — the measurement below is why.
```

**The generalisation I considered and am NOT proposing, with the number that killed it.** [IMP-0638](../../logs/improvement-log.jsonl#L635)'s own `why_it_was_never_caught` invites a gate asserting that every HARD build-step script is wired to [`gate-baselines.json`](../../config/gate-baselines.json). Measured before proposing, per this repo's rule that a proposal's premise is established by a query:

- **7 of 57** `scripts/verify-*.py` import `lib.gate_baseline` — `verify-build-config`, `verify-code-app-data-sources`, `verify-field-security-coverage`, `verify-provisioning-test-presence`, `verify-pipeline-config`, `verify-tad-coverage`, `verify-superseded-column-writers`.
- Only **4** gates have an actual baseline entry: `field-security-coverage`, `pipeline-config`, `provisioning-test-presence`, `tad-coverage`.
- And the premise is not even mechanically expressible against this config: [`revitalise-grant-automation-build.yml`](../../config/revitalise-grant-automation-build.yml) carries **no per-step `severity` key** — `HARD`/`SOFT` appear 28 and 13 times, in comments and prose, not as a field a gate could read per step.

Such a gate would fire on roughly **50 correctly-unwired scripts on day one**. Most gates *should* have no override path — a scoped waiver on a security gate is a liability, not a feature. This is the fail-closed case my instructions name: enumerate the corpus before choosing the set. Wiring is correctly **demand-driven**, and seven demands in is not evidence of a systemic gap.

```
CLUSTER: learning-substrate-destroyed  (x1 here: IMP-0640; 2nd instance of the subclass)
Altitude:   CLASS — second instance of "a fix landed without the write action that closes
            its own finding's log entry". Founding instance: IMP-0285.
Ladder row: "An agent had the information and still did the wrong thing" → agent-file edit
Becomes:    agents/development-agent.md § Improvement Capture (after L368) gains the
            closure obligation: a dispatch that fixes what a prior finding describes closes
            or defers THAT entry (and stamps `corrects` on the fixing entry), and verifies
            with the standalone `--check` before reporting the fix as verified.
Retires:    nothing
Cites:      IMP-0640, IMP-0285
Residual:   NO GATE CAN CATCH THIS, and I am not proposing one. Whether entry N fixes
            finding M is a semantic judgement about two prose fields; verify-improvement-log
            checks a proposed_change's TYPE, never its content (IMP-0423). The mechanical
            half already exists and already fired — the improvement-log-check step. This
            edit shortens the loop from "a later build discovers it" to "the fixing dispatch
            notices it", and that is all it does.
```

**Subclass count verified, not assumed.** `learning-substrate-destroyed` has 29 members, so I measured the specific mechanism rather than the class label: scanning every entry's `what`/`root_cause`/`lesson` for the fix-and-closure-are-separate-write-actions mechanism returns exactly **[IMP-0285](../../logs/improvement-log.jsonl#L282) and [IMP-0640](../../logs/improvement-log.jsonl#L637)**. Second instance confirmed — which is what licenses the class-level edit rather than a note.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | [`agents/development-agent.md`](../../agents/development-agent.md#L368) | § Improvement Capture gains the closure obligation: fixing the code a prior finding describes closes or defers **that finding's own entry** and stamps `corrects` on the fixing entry; verify with standalone `verify-improvement-log.py --check`, not only the gate the fix targeted | IMP-0640, IMP-0285 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

No script, constraint, skill or knowledge change is proposed. The delivery-side fix this review was convened over **already exists on disk**; this review's job is the bookkeeping that closes it plus the one instruction that stops the third instance.

### Log bookkeeping this review performs (not a rule change, but it is a write)

| Entry | Disposition | Fields moved |
|---|---|---|
| [IMP-0638](../../logs/improvement-log.jsonl#L635) | **APPLIED** | `status`, `applied_by` (naming IMP-0639's wiring), `reobserved` (V2), `evidence_grep` |
| [IMP-0639](../../logs/improvement-log.jsonl#L636) | **APPLIED** | `status`, `applied_by`, **`corrects: IMP-0638`** — the missing link, `evidence_grep` |
| [IMP-0640](../../logs/improvement-log.jsonl#L637) | **APPLIED** | `status`, `applied_by` (naming change 1), `evidence_grep` |

---

## 4. Retirements

> Retirement check performed: 95 constraint rows reviewed, none currently redundant — derived, not typed: **10** retired rows (`grep -rh '^| ~~C-'`) and **85** live rows across `constraints/`. Nothing in this cluster's area is superseded; no constraint was added, so nothing displaced one.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0611, IMP-0612, IMP-0613, IMP-0614, IMP-0615, IMP-0617, IMP-0618, IMP-0620, IMP-0625, IMP-0626, IMP-0631, IMP-0632, IMP-0635, IMP-0636, IMP-0637

**Scope declared, not silently capped.** The queue holds **18** `unread` entries. This dispatch was convened by an unread `blocker`, and an unread blocker must not pull a review of everything around it ([IMP-0183](../../logs/improvement-log.jsonl)) — so I processed the 3 entries in the blocker's own two clusters and excluded the other 15, stamping each with `excluded_by` naming this document so the exclusion is machine-readable rather than a citation-stamp warning per id.

States excluded from scope, per activation step 2:

| State | Count | Why not in scope |
|---|---|---|
| `awaiting-approval` | 1 — IMP-0608 | Already processed by another review and parked at its own gate. The remedy is a keyword against **that** document, not a second derivation |
| `reviewer-deferred` | 136 | Each carries a `deferred_reason` a human accepted. One, IMP-0274, carries no `revisit_when` — reported, not touched |
| `unread`, outside the blocker's clusters | 15 | Named on the `Deferred:` line above |

**One boundary observation, logged here rather than as a finding.** [IMP-0639](../../logs/improvement-log.jsonl#L636) records `development-agent` editing [`verify-field-security-coverage.py`](../../scripts/verify-field-security-coverage.py#L151) and [`gate-baselines.json`](../../config/gate-baselines.json#L84) — and `scripts/` and `config/` both appear in [improvement-agent's own Outputs table](../../agents/improvement-agent.md#L371) as *"the changes themselves"*, i.e. behind `APPROVE IMPROVEMENTS`. I am **not** logging this as a finding, for two measured reasons: the dispatch was reviewer-approved, and [`gate-baselines.json`](../../config/gate-baselines.json) is by design written by delivery agents (its entries require an owner, an expiry and a clearing action, none of which improvement-agent could supply for a phase-2 dispatch). The grey area is the gate *wiring*, not the baseline entry. Flagged for the reviewer as a scope question; if the answer is that gate wiring is improvement-agent-only, that is a one-line addition to `development-agent.md` and I will take it as feedback on this draft.

**One `corrects` warning I checked and it does not touch this review.** [IMP-0632](../../logs/improvement-log.jsonl) carries `corrects` against IMP-0628 and IMP-0630, both processed by [2026-09-06-improvement-review-2.md](2026-09-06-improvement-review-2.md). I scanned every entry for `corrects` naming IMP-0638, IMP-0639 or IMP-0640: **none**. Nothing appended since the fix contradicts it.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 637 | 637 (no new entry appended) |
| `NEW` entries | 155 | 152 |
| `unread` blockers | 2 | 0 |
| Digest lines | 650 | regenerated at apply time |

Regenerated with `python3 scripts/generate-known-failure-modes.py` and confirmed current with `--check` **after** approval, not before.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-07-improvement-review.md

Findings processed: 3 NEW  →  2 clusters
Regression check:   2 prior changes audited, 1 class recurred (gate fired correctly)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 0 skill/knowledge edits,
                    1 agent-file edit, 0 retirements
Altitude calls:     1 generalised from instance to class, 1 left as an instance on a
                    measured corpus (7 of 57 scripts wired — a "wire them all" gate would
                    fire on ~50 correct ones)
Digest:             will regenerate — 637 entries, 152 NEW after closure

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Approved by Xander Lykopoulos, 2026-09-07, in his own message against this document.** Applied in full; nothing was withheld and nothing was narrowed.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | [`agents/development-agent.md`](../../agents/development-agent.md#L372) — new § *"Fixing what a finding describes does NOT close that finding — that is a second write action"* under Improvement Capture | working tree, 2026-09-07 | IMP-0640 |
| — | Log bookkeeping only: `corrects: IMP-0638` stamped on IMP-0639; V2 `reobserved` on IMP-0638 | working tree, 2026-09-07 | IMP-0638, IMP-0639 |

Entries rejected, with reasons: **none.**

### Re-verification performed at apply time, after the keyword

The keyword approves a draft; it does not freeze the tree. Re-measured before applying:

| Re-verified | Instrument | Result |
|---|---|---|
| Nothing appended since the draft carries `corrects` against IMP-0638/0639/0640 | full-log scan | none — clear |
| Max log id unchanged before any write | re-read | `IMP-0640` — no concurrent session |
| The gate's **behaviour** (not its source) | **executed** `verify-field-security-coverage.py` | exit 0, `UNREADABLE (BASELINED)` |
| The whole source suite | **executed** `run-source-gates.py` | 13/13 PASS |
| Each entry still carried its step-6 `reviewed_in` | asserted in the write script | held for all three |

### Closing state

| Check | Exit |
|---|---|
| `verify-improvement-log.py` (schema, authoritative) | **0** |
| `verify-improvement-log.py --check` (the blocking gate) | **0** — 637 entries, 152 NEW, 480 APPLIED |
| `generate-known-failure-modes.py --check` | **0** — digest current at 651 lines |
| `verify-review-document.py --only <this file>` | **0** |

The `--check` result matches the pre-approval simulation exactly (scratch copy B → exit 0), which is what the simulation was for. **The `improvement-log-check` blocker on `revitalise-grant-automation` is cleared; the build may be re-dispatched at wbs:3.2/3.3/3.4.**

One standing item, unchanged by this review: the baseline entry for `rev_grant.rev_escalatedon` **expires 2026-09-14**. It clears by deletion — not re-dating — once the phase-2 dispatch restores the `FieldPermission`.
