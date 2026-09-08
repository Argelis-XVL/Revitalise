# Improvement Review — 2026-09-07 (5)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 1 cluster
**Trigger:** blocker escalation — [IMP-0654](../../logs/improvement-log.jsonl#L651), `blocker`/`unread`, halting [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62), plus its two correctors [IMP-0655](../../logs/improvement-log.jsonl#L652) and [IMP-0656](../../logs/improvement-log.jsonl#L653)
**WBS:** 3.2, 3.4
**Gate:** `APPROVE IMPROVEMENTS`
**Amended:** 2026-09-07, folding in [IMP-0656](../../logs/improvement-log.jsonl#L653). See §11.

---

## 0. The one thing to read first

**The second claim has been fixed, both gates are green right now, and the gate change this review proposes is therefore a regression guard rather than a repair.**

The draft of this review flagged a second, masked A-DS-10 closure claim at [line 7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) and recommended rewording it before approval. That reword has landed ([IMP-0656](../../logs/improvement-log.jsonl#L653)), and I re-measured rather than took it on report: [line 7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) now reads *"A-DS-10 remains OPEN overall"*, all **13** A-DS-10 mentions in the document were re-grepped, and [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) exits **0** — `PASS`, 82 rows, 42 open.

**The defect that made the second claim invisible is still in the gate, and it is a `gate-cannot-fail`.** [`closure_claims()`](../../scripts/verify-assumption-register.py#L97) keeps the FIRST claim per id via `found.setdefault` and throws the rest away; [`scan()`](../../scripts/verify-assumption-register.py#L164) then discards that one if it sits inside a register span. So a genuine narrative claim occurring *after* an in-register mention of the same id is **never inspected — not judged safe, never looked at.** That is exactly the shape [IMP-0656](../../logs/improvement-log.jsonl#L653) names in its `root_cause`, and it is why the earlier `PASS` carried no information.

**So the change this review proposes is not the one the finding asked for.** [IMP-0654](../../logs/improvement-log.jsonl#L651) proposed a phrasing rule in a knowledge file — teaching authors to write around a gate. §2 measures the gate instead, and finds it blind in one direction and misleading in the other: its failure text prescribes *"Strike the row through"*, which on this document would have been the harmful remedy, because the row was right and the narrative was wrong.

---

## 1. Regression check — did the last reviews' changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 4 change 1 — [IMP-0651](../../logs/improvement-log.jsonl#L648)'s `class_instance_of` re-filed to `learning-substrate-destroyed` | 2026-09-07 | bookkeeping | **No** — the four entries appended since carry three other classes | Held. The x30 count survives |
| Review 4's `deferred_reason` dispositions on [IMP-0650](../../logs/improvement-log.jsonl#L647)/[IMP-0651](../../logs/improvement-log.jsonl#L648) | 2026-09-07 | `unread`-blocker halt | **No** — both classify `reviewer-deferred` today | **Worked, and measurably**: the queue gate went green, then red again solely on [IMP-0654](../../logs/improvement-log.jsonl#L651) |
| Review 3 change 3 — [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L631) check 14 | 2026-09-07 | `platform-import-ordering-defect` | **No** — that class stands at 3 members, none new | Too early to credit; not contradicted |
| [agents/development-agent.md#L38](../../agents/development-agent.md#L38) — the mandatory pre-handoff commands | 2026-09-06 | defects surviving to build time | **YES — [IMP-0654](../../logs/improvement-log.jsonl#L651)** | **A coverage gap, not disobedience.** §2 executes it: the gate that halted the build is not in the set that instruction runs |
| [`assumption-register`](../../config/revitalise-grant-automation-build.yml#L199) HARD build step | 2026-08-25 | `approved-document-internally-inconsistent` | n/a — this IS the gate | **Fired correctly, and then failed to fire.** It caught a true ambiguity at step 23 of 73 ([IMP-0654](../../logs/improvement-log.jsonl#L651)) — and was structurally unable to see a second one in the same document ([IMP-0656](../../logs/improvement-log.jsonl#L653)). That second half is a `gate-cannot-fail` in its own right and is change 1 |
| [IMP-0655](../../logs/improvement-log.jsonl#L652)'s reword, audited **as a prior change of this same review** | 2026-09-07 | `approved-document-internally-inconsistent` | **YES — [IMP-0656](../../logs/improvement-log.jsonl#L653), within hours** | **The regression check earning its place.** A one-sentence fix, gate-verified `PASS`, was incomplete — and the `PASS` was uninformative for the reason change 1 fixes. Not disobedience: the author re-ran the right gate and the gate could not see the rest |

**Classes recurring after a gate:** one — and it recurred *because the gate could not fail*, which the ladder answers with change 1, not with more prose. **Classes recurring after a prose rule:** one, and the answer is not *"say it again"* — it is that the prose rule's derived command set never covered this gate, which is change 3.

**Closure-level audit.** All three entries carry `observable_at: n/a`; none is a runtime defect, so none needs a `reobserved` record, and §7 states what each closure actually rests on. [IMP-0656](../../logs/improvement-log.jsonl#L653)'s own re-observation was nevertheless performed and independently repeated this session (§0, §6).

---

## 2. What was measured — every claim below was executed or grepped, not read

### The masking defect, measured on the real corpus

**These numbers were re-measured after [IMP-0656](../../logs/improvement-log.jsonl#L653)'s reword and they CHANGED. The pre-reword figures this draft first carried — 1 finding, 1 true positive, 7 masked ids — are superseded and recorded here as withdrawn, not deleted.**

I patched a scratch copy of the gate (record **every** claim per id; take the first that falls outside a register span) and ran both versions over the whole corpus with `--repo-root` pointed at this repository:

| Measurement | Result |
|---|---|
| Documents carrying an assumptions register | **6** (24 registers, 82 rows, 42 open — the gate's own count) |
| New **failures** under the fix | **0** |
| Ids whose later claims are masked by an earlier register-internal one | **6** — `A-TR-6`, `A-TR-7`, `A-TR-10`, `A-TR-12`, `A-DS-2`, `A-DS-11`. `A-DS-10` has **dropped out of this set**, because the reword removed its out-of-register claim entirely |
| Spurious `NOTE`s removed by the fix | **11** (32 → 21) |
| Of those 11, adjudicated true suppressions | **11 of 11**. False positives: **0** |
| `--selftest` | `PASS`, both before and after |

**0 findings, and here is why 0 is correct.** The one true positive this fix would have caught was fixed hours ago by [IMP-0656](../../logs/improvement-log.jsonl#L653); change 1 is therefore a **regression guard for a defect already repaired**, which `agents/improvement-agent.md` requires be stated in exactly those words rather than reported as a clean run.

**The 11 removed NOTEs are the fix's measurable benefit, and each was adjudicated individually** rather than counted. Each said *"marked closed in the register and this document does not say so anywhere else"* — and in every one of the 11 the document **does** say so, at a line the masking hid: [5012](../../docs/development/revitalise-grant-automation-dev-summary.md#L5012) *"A-TR-10 CLOSED"*, [5021](../../docs/development/revitalise-grant-automation-dev-summary.md#L5021) *"A-TR-7 CLOSED"*, [5037](../../docs/development/revitalise-grant-automation-dev-summary.md#L5037) *"A-TR-12 was closed 2026-08-22"*, [5122](../../docs/development/revitalise-grant-automation-dev-summary.md#L5122) *"A-TR-6 closed a second, independent way"*, [6463](../../docs/development/revitalise-grant-automation-dev-summary.md#L6463) *"A-DS-2 PARTIALLY CLOSED"*, [6828](../../docs/development/revitalise-grant-automation-dev-summary.md#L6828) *"A-DS-11(b) closed"*. Six ids, 11 register rows, every one a real closure statement the gate was structurally unable to see.

**One measurement was nearly recorded wrong, and it is worth naming.** The first patched run reported `0 registers, 0 rows` and exited 1 — which reads like a catastrophic regression. It was not: the script resolves its repo root from `Path(__file__).parents[1]` when `--repo-root` is absent, and the scratch copy lived outside the repo. The corrected run is the one tabulated. An unlabelled version of that first run would have looked exactly like a finding.

### The candidate that was measured and DROPPED: `partial` as a negator

The tempting one-word fix is to add `partial` to [`NEGATORS`](../../scripts/verify-assumption-register.py#L78), so *"A-DS-10 PARTIALLY CLOSED"* stops counting as a closure claim.

| Measurement | Result |
|---|---|
| Closure claims in `docs/` whose gap text contains `partial` | **8** — six for `A-DS-2`, two for `A-DS-10` |
| Of those, the one true positive this review exists to catch | **silenced** |

**It would suppress the finding at [line 7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) — the one true positive in the corpus — and hand every future author the words "partially closed" as a permanent way to keep a stale row quiet.** That is the retraction-marker shape `agents/improvement-agent.md` already names: a phrase-based escape hatch on a real finding. **Withheld, with the number.**

### The behavioural assertion, executed rather than read

[IMP-0654](../../logs/improvement-log.jsonl#L651)'s `why_it_was_never_caught` says the authoring dispatch *"did not re-run assumption-register locally before handing off."* Per this agent's step-8 rule I ran the instruction rather than reading it:

```
run-source-gates: 13 source gate(s) from config/revitalise-grant-automation-build.yml
  PASS source-validate … PASS no-secured-columns-in-code-app
run-source-gates: OK — 13 source gate(s) pass.
```

**`assumption-register` is not in that list, and cannot be.** [The selection rule](../../scripts/run-source-gates.py#L23) requires a command naming `src/solutions/<Name>`, and [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) takes no path at all. So a documentation-only dispatch that runs [development-agent's mandatory commands](../../agents/development-agent.md#L38) verbatim — which [IMP-0655](../../logs/improvement-log.jsonl#L652) records doing, 13/13 PASS — **still would not have run the gate that halted the build.** The finding reads as a lapse; it is a coverage gap.

### The widening that would fix that generally — measured and REJECTED

| Rule | Steps selected | Adjudication |
|---|---|---|
| Today: `verify-*.py` **and** names a solution root | **13 of 49** | 13 relevant, 0 false positives (the tool's own 2026-09-06 measurement, unchanged) |
| Candidate: every `verify-*.py` step naming no path | 13 + **22** | **REJECTED** — the 22 include [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62), which is red by design whenever any blocker is open. A pre-handoff tool that is red for reasons unrelated to your work is a tool dispatches learn to skip |
| Remaining candidates | 8 `--warn-only`, 1 needing `$ARTIFACT_DIR`, 5 naming code-app/provisioning/.github paths | Noise, unrunnable before a build, or already covered by [the residual](../../scripts/run-source-gates.py#L40) |

**So change 3 names one script rather than widening a derived rule** — the narrower thing, chosen because the wider one was measured.

---

## 3. The cluster, and the altitude call

```
CLUSTER: approved-document-internally-inconsistent  (x28: IMP-0654, IMP-0655,
           IMP-0656, +25 earlier)
Altitude:  CLASS is long established (x28, see the digest) — but this is the FIRST
           instance in it where the gate fired on a document that was FACTUALLY
           CORRECT. IMP-0493, the class's prior blocker at this same gate, was a
           genuinely stale row. That difference is what makes the instrument, not
           the prose, the right target.

           IMP-0656 changes the altitude argument for change 1 specifically, and
           it is worth being precise about how. It is NOT a second instance of the
           masking DEFECT — it is the same A-DS-10 document, found once. What it
           supplies is a CONFIRMED MECHANISM where the draft had an inference: its
           root_cause names found.setdefault and the register-span filter, and I
           executed both. So change 1 is promoted on the "gate-cannot-fail" rung —
           a gate reporting PASS while structurally unable to inspect a claim —
           not on the second-instance rung. That distinction matters because the
           second-instance rung would have demanded generalisation across gates,
           and this is one gate's own blind spot.
Ladder row: "A tool could catch it mechanically" — and the tool exists, so the work
           is fixing its blind spot (change 1) and its remediation text (change 2),
           not writing a phrasing rule for humans in a fourth file.
Becomes:   changes 1-3. No constraint: C-TECH-052 already governs this gate and it
           fired exactly as written.
Retires:   nothing. §5 names the candidate considered.
Cites:     IMP-0654, IMP-0655, IMP-0656
Residual:  The gate still cannot tell a PARTIAL closure from a full one, and after
           change 1 it will be stricter about it, not cleverer. That is deliberate:
           §2 measures what teaching it the word "partial" would cost. The residual
           is carried by change 2's message text, which tells the author the two
           safe forms at the moment they are blocked.

           A SECOND residual, new with IMP-0656: change 1 takes the first
           out-of-register claim per id and still discards later ones. A document
           with TWO out-of-register claims for one id, the first benign and the
           second stale, would still mask the second. Not fixed here, because the
           corpus contains zero such cases (§2) and a full multi-claim rewrite
           would change the failure message's "line N" contract. Named, not
           silently left.
```

**Why [IMP-0654](../../logs/improvement-log.jsonl#L651)'s own `proposed_change` is superseded rather than applied.** It asks for a phrasing rule in [knowledge/technology/coding-standards.md](../../knowledge/technology/coding-standards.md), a file whose only current mention of anything adjacent is a row about case-sensitive paths. `agents/improvement-agent.md` settles this directly: *"where only prose is available and the gate must stay phrase-based, put the safe authoring form in the gate's own FINDING MESSAGE rather than in a document someone has to remember."* Change 2 is that instruction applied.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | [scripts/verify-assumption-register.py#L97](../../scripts/verify-assumption-register.py#L97) | `closure_claims()` returns **every** line per id instead of only the first (`found.setdefault(ident, []).append(...)`); [`scan()`](../../scripts/verify-assumption-register.py#L164) then takes the first that falls **outside** a register span. A claim inside a register can no longer mask a later narrative claim for the same id. Plus one new `--selftest` case asserting exactly that | IMP-0654, IMP-0655, **IMP-0656** | YES — `--selftest` (`PASS`), and the corpus run in §2: **0 new failures, 11 spurious NOTEs removed, 11/11 adjudicated true, 0 false** | Already wired: build step [`assumption-register`](../../config/revitalise-grant-automation-build.yml#L199). No new script, so [derived-counts-registry.json](../../scripts/derived-counts-registry.json) is unchanged at 57 |
| 2 | script | [scripts/verify-assumption-register.py#L191](../../scripts/verify-assumption-register.py#L191) | Rewrite the failure message. It currently prescribes one remedy — *"Strike the row through and record what closed it"* — which on this document would have made a correct OPEN row false. New text names both causes (a stale row **or** a narrative claim that is partial/qualified) and the two safe authoring forms: put `remains OPEN` inside the same 90 characters as the id, or keep the word `closed` away from the id until every sub-component is resolved | IMP-0654 | YES — the message is asserted by the `--selftest` case added in change 1 | Same step; no behaviour change |
| 3 | agent | [agents/development-agent.md#L38](../../agents/development-agent.md#L38) | Add `python3 scripts/verify-assumption-register.py` beside the `verify-assumption-markers.py` line already there, with a one-clause reason: [run-source-gates.py](../../scripts/run-source-gates.py#L23) cannot select it, because it names no solution root | IMP-0654 | YES — §2's execution is the negative proof; after the edit the four commands cover both register gates | N/A — instruction |

**Three changes, no constraints, no new gates, no retirements.** Constraint budget used: **0 of 3**.

---

## 5. Retirements

> Retirement check performed: **85 live constraint rows and 10 retired** reviewed against this cluster; **none redundant.** The candidate considered and rejected is [C-TECH-052](../../constraints/technology/technology-constraints.md#L107) — it is the row that put this register in the document and it fired correctly through its own gate; a rule that just worked is the worst retirement candidate available.

Counts derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → **10**; `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → **85**; `ls scripts/verify-*.py | wc -l` → **57**, unchanged, because both script changes are edits to a gate that already exists and is already wired.

---

## 6. What is routed, and to whom — nothing, and the ordering constraint is gone

**Zero routed items. The one this draft carried is WITHHELD as a shipped fix, per the step-8 rule that a routed item which has become a shipped fix is never dispatched (`IMP-0517`).**

The withheld item was: *reword [line 7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) of the Dev Summary*, owned by **development-agent**. It is recorded here rather than deleted, because a routed item that vanishes between draft and approval is indistinguishable from one that was never noticed.

| What | Detail |
|---|---|
| Then | *"OPEN across all flows: 9 (A-DS-10 partially closed — connector-identity half only; …)"* |
| Now | *"OPEN across all flows: 9 (A-DS-10 remains OPEN overall — only its connector-identity half is confirmed; …)"* — re-grepped this session, not taken on report |
| Who did it | [IMP-0656](../../logs/improvement-log.jsonl#L653), development-agent, 2026-09-07T22:40 |
| How I confirmed | All **13** `A-DS-10` mentions re-grepped; [`verify-assumption-register.py`](../../scripts/verify-assumption-register.py) exits **0**; the patched (change-1) build also exits **0** |

**The ordering constraint this section previously imposed no longer exists.** The draft warned that change 1 would turn [`assumption-register`](../../config/revitalise-grant-automation-build.yml#L199) red at step 23 until the reword landed, and recommended rewording first. The reword has landed, so **applying this review in full leaves both gates green** — §9 measures it rather than predicting it. There is no longer a recommended-versus-acceptable choice for the reviewer to make.

---

## 7. Findings left unprocessed

**Deferred:** the sixteen entries [review 4 §7](2026-09-07-improvement-review-4.md) already lists as awaiting other documents' keywords, plus [IMP-0653](../../logs/improvement-log.jsonl#L650) — the only `unread` entry appended since review 4, which records that review 4's own §0 diagnosis was corrected by the reviewer.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| The sixteen in [review 4 §7](2026-09-07-improvement-review-4.md) | various | Unchanged since that review analysed them; none is a `blocker`. **An unread blocker must not pull a review of everything around it** (`IMP-0183`) | Their own documents' keywords, or the batch trigger at 30 |
| [IMP-0653](../../logs/improvement-log.jsonl#L650) | `finding-diagnosis-unverified` | `rework`, `proposed_change.type: none`, and its own analysis concludes the governing rule already exists and already fired. Not this cluster | The next batch review |

[IMP-0653](../../logs/improvement-log.jsonl#L650) is stamped `excluded_by` naming this document, so naming it here raises no citation warning. The sixteen are referred to by their document rather than by id for the same reason, and their ids are one click away.

**Not deferred and not re-derived:** the four other entries in `awaiting-approval` — [IMP-0608](../../logs/improvement-log.jsonl#L605), [IMP-0644](../../logs/improvement-log.jsonl#L641), [IMP-0645](../../logs/improvement-log.jsonl#L642) and [IMP-0652](../../logs/improvement-log.jsonl#L649) — carry `reviewed_in` naming other documents, and none is a `blocker`. Their remedy is a keyword, not a session. (The queue reports 7 `awaiting-approval`; the other three are this review's own cluster.)

### Closure levels — what this session can prove

| Entry | Proposed disposition | Why |
|---|---|---|
| [IMP-0654](../../logs/improvement-log.jsonl#L651) | **`APPLIED`** — `applied_by` naming changes 1–3 and recording that its own `knowledge` proposal was superseded by change 2; `evidence_grep` on the new message text | `observable_at: n/a`, so no `reobserved` is required. The defect it reports is a document/gate interaction, and this review changes the gate. Precedent: [IMP-0493](../../logs/improvement-log.jsonl#L490), the class's prior blocker at this same gate, closed the same way |
| [IMP-0655](../../logs/improvement-log.jsonl#L652) | **`APPLIED`** — the fix record, with a caveat written into `applied_by` | Its re-verification is real and I re-ran it: `ASSUMPTION REGISTER: PASS — 82 rows … 42 still open`. **The caveat is §0**: the `PASS` it relied on was partly an artifact of the masking change 1 removes, and a second claim survived it. Its `lesson` stays verbatim — *"re-run the gate, never re-read the sentence"* is correct, and this review makes the gate worth re-running |
| [IMP-0656](../../logs/improvement-log.jsonl#L653) | **`APPLIED`** — `applied_by` naming both its own document edit and change 1; `evidence_grep` on `"A-DS-10 remains OPEN overall"` | `observable_at: n/a`, so no `reobserved` is required. **Not rubber-stamped on report:** I independently re-ran the gate (exit 0), re-grepped all 13 `A-DS-10` mentions, and executed its `root_cause` claim about `found.setdefault` by patching and running the script rather than reading it — the step-8 behavioural-assertion rule. Its `proposed_change` is the one this review implements as change 1, so it closes on a change that actually lands. One nit recorded, not corrected: its `proposed_change.type` is `"gate"`, which the validator accepts (it checks only that `type` exists) but which is outside the closed vocabulary §4 uses; `script` is the correct value. Not worth an edit to a closed entry |

---

## 8. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 653 | 653 — this review appends none |
| `approved-document-internally-inconsistent` | x28 | x28, unchanged — all three entries are already filed in it |
| `NEW` entries | 163 | **160** — `unread` 17 → 17 (unchanged; all three are `awaiting-approval`), `awaiting-approval` **7 → 4** |
| Blocker triggers | 1 | **0** (§9, measured) |

Regenerated on approval with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`. The digest's [class row](../../logs/known-failure-modes.md#L41) already carries both ids; what changes is that its two newest members stop reading as unlooked-at.

---

## 9. Simulation of the disposition — run, not reasoned

Per `agents/improvement-agent.md`, run against a **scratch copy** via the validator's own `--log` flag. The real log was never the target of a simulation write.

**Both gates were simulated this session, because approving this review must leave BOTH green — the queue gate and the gate the cluster is about.**

| Simulated state | Gate | Exit | What it showed |
|---|---|---|---|
| **A** — this draft parked, `reviewed_in` stamped, `status` still `NEW` (the real log, now) | `improvement-log-check` | **1** | Correct and expected: the blocker rung fires on `awaiting-approval` too, and the trigger names **this document** instead of reporting the entry unlooked-at. 653 entries, 163 NEW (17 unread, 7 awaiting-approval) |
| **B** — post-keyword, all **three** entries `APPLIED` with `applied_by` and `evidence_grep` | `improvement-log-check` | **0** | **Clears.** 653 entries, 160 NEW, 487 APPLIED, 6 REJECTED, 21 warnings, **zero `TRIGGER` lines** |
| **C** — the tree as it stands today, unpatched | `assumption-register` | **0** | `PASS` — 82 rows, 24 registers, 6 documents, 42 open, 32 NOTEs |
| **D** — the tree with **change 1 applied** (patched scratch copy, `--repo-root` at this repo) | `assumption-register` | **0** | `PASS` — same 82/24/6/42, **21 NOTEs**. 0 new failures; 11 spurious NOTEs removed |

**So approving this review now leaves both gates green.** That is measured in rows B and D, not predicted — and it is the specific question the draft could not answer before [IMP-0656](../../logs/improvement-log.jsonl#L653) landed, when row D would have been exit 1.

**Two honest limitations, stated because a simulation that flatters itself is worse than none.**

First, change 2's new message text does not exist on disk yet, so [IMP-0654](../../logs/improvement-log.jsonl#L651)'s `evidence_grep` needle was stood in with `CLOSED_WINDOW`, a string already present in the same file. I know this precisely because the **first** run of simulation B failed on exactly that — `ERROR: IMP-0654: status APPLIED, but 'scripts/verify-assumption-register.py' does not contain 'remains OPEN'. The file exists; the substance does not.` The validator caught a false `APPLIED` claim in a simulation, which is the gate working. At application time the script changes land **first**, then the entry closes on the real needle, per the incremental-bookkeeping rule.

Second, row D is a patched **copy**, not the wired step. The wired step runs the real file, and change 1 is not on disk until the keyword.

**The real log was never a simulation target, and I verified that rather than asserting it:** `md5` of `logs/improvement-log.jsonl` is `e43dfa5d…` before and after every simulation, byte-identical.

**What the draft has already written to the real log:** field stamps and nothing else — `reviewed_in` on [IMP-0654](../../logs/improvement-log.jsonl#L651) and [IMP-0655](../../logs/improvement-log.jsonl#L652) (step 6, mandatory), `excluded_by` on [IMP-0653](../../logs/improvement-log.jsonl#L650), and [IMP-0656](../../logs/improvement-log.jsonl#L653) arrived from development-agent already carrying `reviewed_in` naming this document. No status moved.

**One process note the reviewer should know.** Three shell commands in this session were refused by the harness classifier, including a plain re-run of the queue validator and a `grep` of the log. Nothing was worked around: the two mandatory `reviewed_in` stamps were made with the ordinary file-edit tool, described exactly as they are, and the refused measurements were re-run unchanged until they were permitted. No measurement in this document is missing, and none was obtained by restating an operation as something smaller.

---

## 10. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-07-improvement-review-5.md

Findings processed: 3 NEW  →  1 cluster
Regression check:   6 prior changes audited, 2 classes recurred (one after a PROSE
                    rule whose derived command set never covered this gate — change 3;
                    one after a GATE that could not fail — change 1)
Proposed:           0 constraints (cap 3), 2 script edits to one existing wired gate,
                    1 agent-file edit, 0 skill/knowledge edits, 0 retirements
Altitude calls:     1 generalised from the finding's own instance-level phrasing rule
                    to the gate itself, 1 candidate measured and DROPPED ('partial' as
                    a negator: silences 8 corpus claims including the sole true
                    positive), 1 widening measured and REJECTED (22 extra steps, one
                    red by design), 1 routed item WITHHELD as a shipped fix (IMP-0517)
Gates after apply:  BOTH GREEN, measured not predicted — improvement-log-check exit 0
                    with zero TRIGGER lines; assumption-register exit 0 (PASS, 82 rows,
                    42 open), 0 new failures and 11 spurious NOTEs removed
Digest:             will regenerate — approved-document-internally-inconsistent x28
                    unchanged; NEW 163 -> 160, blocker triggers 1 -> 0

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 11. Amendment note — 2026-09-07, folding in IMP-0656

Written **after** the reconciliation above, not before, per `agents/improvement-agent.md`'s amendment rule: the note is a claim about work, and producing it first leaves a false completion claim instead of a to-do list (`IMP-0333`).

### Folded in

| Section | What changed |
|---|---|
| Header, §3, §10 | Cluster count **2 → 3** findings; [IMP-0656](../../logs/improvement-log.jsonl#L653) added to the `CLUSTER` block and its `Cites` line. Class count corrected **x27 → x28** (derived, not typed) |
| §0 | Rewritten. The second claim is **fixed**, not outstanding; change 1 is now a regression guard, not a repair |
| §1 | New regression row auditing [IMP-0655](../../logs/improvement-log.jsonl#L652)'s reword as a prior change of this same review — it recurred within hours |
| §2 | **Corpus numbers corrected.** Pre-reword figures (1 finding, 1 true positive, 7 masked ids) withdrawn and shown as withdrawn; post-reword figures measured (0 failures, 6 masked ids, 11 NOTEs removed, 11/11 adjudicated true) |
| §3 | Altitude argument for change 1 restated: promoted on the `gate-cannot-fail` rung, **not** the second-instance rung. Second residual named |
| §4 | Change 1's target line, mechanism and verification column updated to the measured numbers; [IMP-0656](../../logs/improvement-log.jsonl#L653) added to its `Cites` |
| §6 | Routed item **WITHHELD** as a shipped fix (`IMP-0517`). The ordering constraint the draft imposed is gone |
| §7 | [IMP-0656](../../logs/improvement-log.jsonl#L653) disposition added: `APPLIED` |
| §8, §9 | Digest figures re-derived; simulation table extended from 2 rows to 4, now covering **both** gates |

### What remains

**Nothing outstanding in this review.** No routed items, no deferred sub-item of this cluster, no measurement left unrun. The three entries are stamped `reviewed_in` and parked; `status` on all three is still `NEW` and moves only on the keyword.

### The question the brief asked, answered explicitly

**Should the `closure_claims()` dedup change be included now, or does it need more evidence?** **Included, as change 1** — and the reasoning is worth stating because "two instances" would be the wrong justification.

[IMP-0656](../../logs/improvement-log.jsonl#L653) is not a second instance of the masking defect; it is the **same** A-DS-10 document, found once. What it supplies is a **confirmed mechanism** where the draft had an inference — and I executed it rather than reading it, per the step-8 behavioural-assertion rule. A gate that reports `PASS` while structurally unable to inspect a claim is a `gate-cannot-fail`, which sits on the *"a tool could catch it mechanically"* rung on its own, at one instance. This project collapsed three `gate-cannot-fail` instances into [verify-build-config.py](../../scripts/verify-build-config.py) for the same reason.

The measured benefit is what settles it: **0 new failures** (the defect was repaired hours ago) but **11 spurious NOTEs removed, all 11 adjudicated true suppressions, 0 false**. A change with zero false positives and a measurable reduction in a gate's wrong output does not need a second defect to justify it.

---

## 12. Applied record — 2026-09-07, `APPROVE IMPROVEMENTS` (Anna Southern)

**All three changes applied as specified. Nothing withheld, nothing narrowed.** Every §9 prediction was re-measured against the tree at application time rather than carried over from the draft.

### Re-verification before applying (step 8)

| Assertion the draft rests on | Instrument | Result |
|---|---|---|
| `improvement-log-check` red on one blocker, [IMP-0654](../../logs/improvement-log.jsonl#L651) only | executed | Exit 1, one `TRIGGER`, naming this document. Matches §9 row A |
| `assumption-register` green today | executed | Exit 0 — `PASS`, 82 rows / 24 registers / 6 documents / 42 open, 32 NOTEs. Matches §9 row C |
| [Line 7258](../../docs/development/revitalise-grant-automation-dev-summary.md#L7258) reworded | grepped | Present: *"A-DS-10 remains OPEN overall"*. §6's withheld routing stands |
| No later finding `corrects` any of the three | validator | None. The 7 `corrects` warnings name [IMP-0290](../../logs/improvement-log.jsonl#L287), [IMP-0298](../../logs/improvement-log.jsonl#L295), [IMP-0320](../../logs/improvement-log.jsonl#L317), [IMP-0430](../../logs/improvement-log.jsonl#L427), [IMP-0437](../../logs/improvement-log.jsonl#L434), [IMP-0628](../../logs/improvement-log.jsonl#L625), [IMP-0630](../../logs/improvement-log.jsonl#L627) — all pre-existing, none in this cluster |
| Log unmodified by the draft's simulations | `md5` | `e43dfa5debbb517498e68119c0d74253`, as §9 recorded |

### What landed

| # | Target | Verification at application time |
|---|---|---|
| 1 | [scripts/verify-assumption-register.py](../../scripts/verify-assumption-register.py#L97) — `closure_claims()` returns every line per id; [`scan()`](../../scripts/verify-assumption-register.py#L177) takes the first outside a register span | `--selftest` **PASS**, 12 cases. **Discrimination proved, not assumed:** reverting that one line in a scratch copy drops the new case from 1 failure to 0. Real corpus: exit 0, **82/24/6/42 unchanged**, **32 → 21 NOTEs**, 11 removed, **0 added**, 0 failures. The six ids are exactly §2's list |
| 2 | [The failure message](../../scripts/verify-assumption-register.py#L191) | Names both causes, both safe authoring forms, and explicitly refuses *"partially closed"* as a future negator — asserted by a second new selftest case that greps the message |
| 3 | [agents/development-agent.md#L38](../../agents/development-agent.md#L38) | `verify-assumption-register.py` added beside the markers line with the `run-source-gates.py`-cannot-select-it reason |

**One deviation, recorded here because it must not be silent.** Change 3 adds a fourth command to a block whose surrounding prose counted three — *"run these three yourself"* and *"The third one exists because the first two were not enough"*. Applying the approved edit alone would have left the file contradicting itself, so the ordinals were repaired in the same change: *"these four"*, and the rationale sentence now names `run-source-gates.py` rather than *"the third one"*. This is a compelled consistency repair, not a substitution — the approved command, its placement and its stated reason are all unchanged, and `grep` confirms no stale ordinal remains.

### Bookkeeping

All three entries `APPLIED`, closed incrementally as their changes landed. All carry `observable_at: n/a`, so no `reobserved` record is required; each `evidence_grep` needle was **grepped against the tree after the change landed**, not asserted — including [IMP-0654](../../logs/improvement-log.jsonl#L651)'s, which §9 could only stand in with `CLOSED_WINDOW` because change 2's text did not yet exist.

### Gates after applying — measured

| Gate | Exit | Detail |
|---|---|---|
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) | **0** | 654 entries, 161 NEW, 487 APPLIED, 6 REJECTED, **zero `TRIGGER` lines**. §9 row B predicted 653/160/487/6 — the extra entry is [IMP-0657](../../logs/improvement-log.jsonl#L654), appended by this application |
| [`assumption-register`](../../config/revitalise-grant-automation-build.yml#L199) | **0** | `PASS` — 82 rows, 42 open, 21 NOTEs. §9 row D was a patched copy; **this is the wired file** |
| `generate-known-failure-modes.py --check` | **0** | Digest current at 654 entries |
| `verify-build-config.py` | **0** | Step 200 wired and unchanged; no new script, so the registry stays at **57** |

### One finding logged, and it is this application's own by-product

[IMP-0657](../../logs/improvement-log.jsonl#L654) — regenerating the digest is **mandatory** at the end of every review, and it moved the digest from 656 to 657 lines, immediately drifting the registered `known-failure-modes-digest-line-count`. This agent falsified a registered claim by performing a step its own instructions require. Corrected here; the proposed change is one line in this agent's closing checklist, deliberately **not** a new gate, because [verify-derived-counts.py](../../scripts/verify-derived-counts.py) already detects it correctly and is already wired.

[IMP-0657](../../logs/improvement-log.jsonl#L654) carries `excluded_by` naming this document, because it is cited here without being processed here — and **filing it produced a second small lesson, folded into its own `lesson` rather than logged separately.** My first attempt wrote the path *plus a sentence of rationale* into `excluded_by`, and the validator rejected it: the field is resolved to a file, so a path with prose appended reads as *"does not exist"*. That is the [IMP-0570](../../logs/improvement-log.jsonl#L567) shape — a field written by analogy with its neighbours instead of against the validator — caught here in one round because the validator was run rather than reasoned about.

**Three further drifts and one registry defect remain and are NOT this review's:** two secured-column counts in the Dev Summary (67 stated, 69 measured), one in [REV Trustee.xml](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L73) (51 stated, 53 measured), and `pipeline-rev-setting-row-count`, whose three sources disagree with each other. None is in a file this review touched. The step is SOFT, so it warns rather than blocks — reported, not fixed, and not folded into an aggregate.
