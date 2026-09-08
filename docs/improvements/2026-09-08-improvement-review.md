# Improvement Review — 2026-09-08 (1)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 `NEW` → 1 cluster
**Trigger:** blocker escalation — [IMP-0661](../../logs/improvement-log.jsonl#L658), `blocker`/`unread`, halting the [`assumption-register`](../../scripts/verify-assumption-register.py) step at 23 of 73 ([`logs/build.log#L103`](../../logs/build.log#L103))
**WBS:** 3.2, 3.3, 3.4
**Gate:** `APPROVE IMPROVEMENTS` — **APPROVED and APPLIED 2026-09-08.** See §7.

---

## 0. The one thing to read first

**The finding's own diagnosis is wrong, and I disproved it by running the gate rather than reading it.** [IMP-0661](../../logs/improvement-log.jsonl#L658) blames the authoring dispatch for not running [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py#L81) before handoff. The dispatch did run it, and recorded the run: [IMP-0659](../../logs/improvement-log.jsonl#L656)'s `applied_by` lists `verify-assumption-register.py PASS` among four gates. That claim is true.

**What actually happened is an ordering defect, and it is structural rather than careless.** The text that tripped the gate is the `VERIFICATION SUMMARY` block at [dev-summary#L7342](../../docs/development/revitalise-grant-automation-dev-summary.md#L7342) — the block whose *content is the report of the gate run*. A block that records "I ran these four commands and they passed" cannot be written before those commands run. So the last edit a dispatch makes to the Dev Summary is, by construction, an edit no local gate has ever seen. The four mandatory commands at [development-agent.md#L37-L42](../../agents/development-agent.md#L37) are correctly placed and were correctly obeyed; they simply cannot cover the paragraph that describes them.

**This is therefore not the residual review 5 named, and not a repeat of the masking defect.** Review 5 fixed the gate so it records every closure claim per id, and that fix is what *caught* this one. The gate worked. Nothing is wrong with it.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 5 change 1 — [`closure_claims()`](../../scripts/verify-assumption-register.py#L81) records every claim per id | 2026-09-07 22:23 | `approved-document-internally-inconsistent` (gate blind to a masked claim) | **No.** The class recurred, the *blind spot* did not | **The change worked, and I proved it discriminatively.** On a scratch copy with [L7342](../../docs/development/revitalise-grant-automation-dev-summary.md#L7342) reverted to the defective wording, the gate at `HEAD` (pre-review-5) exits **0**; the gate on disk (post-review-5) exits **1** and names the line. The build halt is the fix doing its job |
| Review 5 change 2 — failure message names both causes and both safe forms | 2026-09-07 | prescriptive-remedy-makes-a-correct-row-false | No | Not exercised adversarially; not contradicted |
| Review 5 change 3 — [`verify-assumption-register.py`](../../agents/development-agent.md#L39) statically named in the mandatory command block | 2026-09-07 | defects surviving to build time | **Superficially yes — but it was OBEYED** | **Not a prose failure.** The command ran and passed. What defeated it is that the offending text was written afterwards. A recurrence after a prose change is normally evidence of wrong altitude; here it is evidence of wrong *position in the sequence*, which is a different ladder row |
| Review 6 change — the runner prints what it does **not** cover | 2026-09-08 07:30 | coverage read as completeness | Too early | [`run-source-gates.py --list`](../../scripts/run-source-gates.py) executed this session: 16 of 73 steps selected, and `assumption-register` is correctly printed in the `NOT covered` list. Consistent with review 6 §2 |

**Closure-evidence audit.** Both entries in scope carry `observable_at: "n/a"`, so no `reobserved` record is required or claimable. The defect is a document-text property, verified by running the gate, which I did.

---

## 2. The measurement that settles it

Run against a scratch tree, with only [L7342](../../docs/development/revitalise-grant-automation-dev-summary.md#L7342) reverted to the wording [IMP-0661](../../logs/improvement-log.jsonl#L658) quotes:

| Gate version | Source | Result on the defective text |
|---|---|---|
| Post-review-5 (on disk, mtime 2026-09-07 22:23) | `scripts/verify-assumption-register.py` | **exit 1** — `FAILED — 1 stale row(s) of 26 open` |
| Pre-review-5 | `git show HEAD:scripts/verify-assumption-register.py` | **exit 0** — `PASS … none of them is contradicted by its own document` |

The sharpened gate was already on disk at 22:23; the authoring dispatch is timestamped 23:00 and reported PASS. Both facts can only be true together if the offending line did not exist when the gate ran. That is the ordering defect, established by execution rather than inference.

**A second, weaker reading was considered and rejected.** The masking residual review 5 named — *"two out-of-register claims for one id, the first benign, the second stale"* ([`verify-assumption-register.py#L93`](../../scripts/verify-assumption-register.py#L93)) — would also produce a PASS followed by a halt. It does not apply: the earlier out-of-register mention at [L7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) contains no closure word at all after review 5's own edit, so it consumes no slot, and the post-review-5 gate demonstrably fails on the defective text with that line present.

---

## 3. Cluster and disposition

```
CLUSTER: approved-document-internally-inconsistent  (x2: IMP-0661, IMP-0662)
Altitude:  ORDER — the mandatory verification runs before the document text that reports it
           is written. First instance of THIS cause; the two earlier instances in the same
           class had different causes (gate blind spot, since fixed mechanically).
Ladder row: "The ORDER of steps was wrong" -> a step-order fix in agents/
Becomes:   one edit to agents/development-agent.md steps 8-9
Retires:   nothing (see section 4)
Cites:     IMP-0661, IMP-0662
Residual:  stated in section 3.2
```

### 3.1 Change 1 — the four mandatory commands are re-run after the Dev Summary is final

**Target:** [`agents/development-agent.md`](../../agents/development-agent.md#L99), step 9.

Step 8 keeps the four commands where they are. Step 9 gains the ordering rule: the Dev Summary's revision block reports the run, so the run is repeated once the block is written, and it is the **second** run whose result the block records. One sentence, naming the mechanism, so the next agent knows why the repetition is not redundant.

Proposed text for step 9:

> 9. Save both documents — then **re-run the four commands from step 8 and report the SECOND
>    run's result**, because the Dev Summary's own `VERIFICATION SUMMARY` block reports those
>    commands and is therefore written after them. The last edit to the document is, by
>    construction, an edit no local gate has yet seen. `IMP-0661` is that edit costing a build:
>    step 8's four gates ran and passed, the revision block was written afterwards, and
>    `assumption-register` halted the build at step 23 of 73 on the block itself.
>    Present gate output — wait for `APPROVED`

### 3.2 Residual, stated rather than left silent

A dispatch that edits the document after the *second* run defeats this exactly as the first run was defeated. Nothing mechanical closes that, because the only reader of the finished document is the build gate, and inserting a third run moves the boundary without removing it. The residual costs one build cycle, which is what this finding cost. **A second instance after this change is the evidence that would justify a mechanical home** — most plausibly a handoff wrapper that runs the gates and refuses if the document's mtime is later than the run.

### 3.3 What is WITHHELD, and why

[IMP-0661](../../logs/improvement-log.jsonl#L658)'s own `proposed_change` — *"add an explicit pre-handoff step: … run verify-assumption-register.py locally"* — is **withheld as already-present and premise-disproved**. That step exists at [development-agent.md#L39](../../agents/development-agent.md#L39), was added by review 5, and was obeyed. Applying it would add a duplicate line whose stated justification I have just measured to be false.

[IMP-0662](../../logs/improvement-log.jsonl#L659) proposes no change, correctly. Its document fix is already on disk and the gate exits 0 on the current tree — re-run this session: `PASS — 82 row(s) across 24 register(s) in 6 document(s); 42 still open`.

---

## 4. Retirements

Retirement check performed. **10** rows stand retired against **85** live, derived with `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` and its `^| C-` counterpart. No constraint row is made redundant by this review: the only rule in scope, [C-TECH-052](../../constraints/technology/technology-constraints.md#L107), is the one doing the work.

**One candidate considered and rejected, for a reason this review strengthens.** Review 6 §4 already weighed retiring review 5's static naming of [`verify-assumption-register.py`](../../agents/development-agent.md#L39) in the mandatory block, and kept it because the runner cannot select a gate that takes no path. This review adds a second reason to keep it: that command is precisely the one that would have caught this defect had it run last. Retiring it now would remove the instrument this review is repositioning.

**No new constraints (cap 3, used 0), no new scripts, no new gates.** The gate this class needs already exists and already fired.

---

## 5. Findings left unprocessed

**Deferred:** none.

**Scope, stated because the no-silent-caps rule applies to the queue itself.** This is a blocker dispatch; the trigger scopes it to the unread blocker and the entry carrying `corrects` against it. Excluded by state:

- **19 other `unread` entries**, none of them `blocker`. [`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py)'s own state breakdown is the authoritative list. Following review 6's precedent I have deliberately not re-listed the ids here: naming them would mint a fresh citation warning per id against entries this review did not process, and none is stamped by this review.
- **4 `awaiting-approval` entries** — IMP-0608, IMP-0644, IMP-0645, IMP-0652 — which have documents and need a keyword, not a session.
- **139 `reviewer-deferred` entries**, each carrying a reason a human accepted. [IMP-0274](../../logs/improvement-log.jsonl#L271) still names no `revisit_when`; reported, not fixed, not this dispatch's scope.

---

## 6. Verification

Executed this session, each labelled, none chained with `&&`:

| Check | Result |
|---|---|
| `verify-assumption-register.py` on the current tree | **exit 0** — 82 rows / 24 registers / 6 documents / 42 open |
| Same gate on the reverted defective text | **exit 1**, naming the line — proves it can fail |
| `git show HEAD:` gate on the same defective text | **exit 0** — proves review 5's change is what catches it |
| `run-source-gates.py --list` on the build config | 16 of 73 selected; `assumption-register` correctly in the `NOT covered` list |
| Queue simulation on a scratch copy of the log | blocker `TRIGGER` **clears** with both entries `APPLIED`; the only remaining error is the not-yet-applied `evidence_grep` needle |

**Not verified:** nothing was packaged, deployed or run against a live environment; this review reaches **V1** and claims no more. The proposed change is an agent-instruction edit whose effect is only observable on the next dispatch that writes a Dev Summary.

---

## 7. Applied — 2026-09-08

**One change applied, exactly as approved; one proposal withheld as already-withheld in the draft.**

| Item | Disposition | Where |
|---|---|---|
| Change 1 — step 9 re-runs step 8's four commands and reports the SECOND run | **APPLIED verbatim** as the text drafted in §3.1 | [`agents/development-agent.md#L99`](../../agents/development-agent.md#L99) |
| [IMP-0661](../../logs/improvement-log.jsonl#L658)'s own `proposed_change` (add a pre-handoff run) | **WITHHELD** — premise-disproved and already present at [development-agent.md#L39](../../agents/development-agent.md#L39) | recorded in the entry's `applied_by` |
| [IMP-0661](../../logs/improvement-log.jsonl#L658), [IMP-0662](../../logs/improvement-log.jsonl#L659) | `status: APPLIED`, `applied_by` set, `evidence_grep` needle on the new step-9 text | [`logs/improvement-log.jsonl`](../../logs/improvement-log.jsonl) |

No narrowing was required — the approved wording measured correct on re-verification, so this is a clean APPLY rather than a NARROW-AND-REPORT.

**Re-verification performed before applying, per activation step 8.** Step 8's four commands are at [L37-L42](../../agents/development-agent.md#L37) and step 9 was at [L99](../../agents/development-agent.md#L99), as §3.1 asserted. [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) was **executed**, not read: exit **0**, `PASS — 82 row(s) across 24 register(s) in 6 document(s); 42 still open`. [`logs/build.log#L103`](../../logs/build.log#L103) reads `halted at step 23/73`, matching the applied text. §4's retirement figures re-measured unchanged at **10** retired against **85** live. No finding appended since the draft carries `corrects` against either entry in scope — the only `corrects` naming [IMP-0661](../../logs/improvement-log.jsonl#L658) is [IMP-0662](../../logs/improvement-log.jsonl#L659), which is in scope.

**§5's queue figures were stale by one review and are corrected here rather than in place, because the draft's numbers are what the reviewer approved.** At draft time: 19 `unread`, 4 `awaiting-approval`. Measured at apply time: **2** `unread` ([IMP-0663](../../logs/improvement-log.jsonl#L660), [IMP-0664](../../logs/improvement-log.jsonl#L661)) and **24** `awaiting-approval`. The movement is [2026-09-08-improvement-review-2.md](2026-09-08-improvement-review-2.md), a concurrent sibling that processed the intervening entries. Nothing in this review's scope changed; no routed-work table exists in this review, so nothing was handed on stale.

**Post-application state.** [`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py) exits **0**, and the blocker `TRIGGER` this review was written to clear is **gone** (0 `TRIGGER` lines). Seven warnings remain, none in this review's scope; two of them are [IMP-0663](../../logs/improvement-log.jsonl#L660) and [IMP-0664](../../logs/improvement-log.jsonl#L661) needing a `reviewed_in` stamp from review 2, not from here.
