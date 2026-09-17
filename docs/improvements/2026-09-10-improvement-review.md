# Improvement Review — 2026-09-10

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 31 `NEW` → 9 clusters
**Trigger:** 7 unread blocker entries + batch trigger crossed (33 against a threshold of 30)
**Gate:** `APPROVE IMPROVEMENTS`
**Revision 1** (2026-09-10) — corrects the baseline-pin cluster after reviewer challenge; see §0.

---

## 0. The one thing to read first

**Three of the critical findings describe problems that have already been fixed since they were logged, and this review's first draft got one of them wrong.** The evidence rules for the two payment-capture tasks were rewritten on 2026-09-09 and [the file records both rewrites itself](../../contract/evidence-map.json#L530).

### Correction, revision 1: the baseline pin was genuinely fixed, not reflexively re-pinned

The first draft claimed the contract-baseline check went green because someone re-pinned the file by reflex, and that "the reflex is the defect, and it is still there." **That is wrong, and the reviewer was right to challenge it.**

Verified directly rather than taken on report: [`pmsources.py` gained `wbs_content_fingerprint()`](../../scripts/lib/pmsources.py#L180), which hashes the parsed task data instead of the raw file bytes, and [`import-baseline.py` uses it for the workbook's lock entry](../../scripts/import-baseline.py#L279). The lock file records the method per source — the workbook reads `"parsed task content … not the raw file"`, while the signed agreement deliberately keeps its raw-file hash because there the bytes *are* the signed artefact. That landed in commit `a1ae2e5` on 2026-09-09, roughly 22 hours after the finding was written and before this review was dispatched. **The mechanism changed. Nobody re-pinned anything.**

The reason the first draft missed it is worth recording, because it is a rule working exactly as written and producing a wrong answer: [activation step 2](../../agents/improvement-agent.md#L104) says not to read `APPLIED` entries, on the grounds that the digest already carries their lessons. The entry recording this fix is `APPLIED`, so it was never read, and nothing in the unread queue pointed at it — it carries no `corrects` field naming the older finding, and no entry anywhere does.

### And the check that should have caught that has a hole in it

Following the correction turned up a second, worse thing. The fix entry's own proposed change was **two** things: the script change, and a note in a skill file recording when to hash bytes versus parsed content. The script half landed. **The skill half never did** — that file contains no such note. The entry is closed anyway, its `applied_by` naming only the script half.

It passed because it carries **no citation at all**, and the queue gate only checks a citation that exists and misses. An entry closed with no citation is reported nowhere: this one produces zero output from the gate, so every reader saw a clean entry. Logged as `IMP-0697` and folded into row 1.

**The single most consequential measurement in this review is in cluster A.** A critical finding proposed re-pointing six broken evidence citations to the engine directory. Measured one at a time: **four resolve there and two do not**, and the two fail for two *different* reasons, neither of which the finding named. That proposal is narrowed rather than applied as written, and the narrowing is described in full below.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`run-source-gates.py`](../../scripts/run-source-gates.py) 13 → 16 gates | 2026-09-08 | `live-environment-value-in-evidence-comment` | NO | **Working.** No new instance in this batch |
| [`agents/development-agent.md`](../../agents/development-agent.md#L45) scope correction | 2026-09-08 | same | NO | **Working** |
| [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md) in-source marker rule | 2026-09-08 | same | NO | Working — leave alone |
| [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) registry, wired SOFT | earlier | `hand-maintained-count-drifts-from-source` | **YES — x37** | **The gate exists, is wired, and its output is still unread.** Third consecutive review recording this |
| [`kb.py`](../../scripts/kb.py#L48) `--redact` denylist applied automatically at dump time | 2026-09-09 | `scope-tag-does-not-imply-content-clean` | NO | **Working.** Verified by execution — `dump` injects the denylist when no `--redact` is passed |

**Changes whose class recurred after a prose fix:** none new this cycle.

**Changes whose class recurred after a gate:** `hand-maintained-count-drifts-from-source`, at x37. The gate fires correctly and its findings land in an aggregate nobody reads. This review does **not** propose a new gate for it — the gate is right and the read path is the gap, which [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L468) already addresses by putting `verify-derived-counts.py` in this agent's own closing checklist.

### A note on the previous review's own scope claim

The [2026-09-08 review](2026-09-08-improvement-review-2.md) reported that its dispatch brief asked for classes that were almost entirely absent from its scope. **The same shape appeared in this dispatch's brief and was measured rather than assumed.** The brief described roughly a dozen items; the queue held 29 unread. Every id the brief named was checked against the log, and the brief's characterisation held in each case — including its explicit warning that the six false-citation entries are older and separate from the seven critical ones, which is correct.

---

## 2. Clusters and promotion decisions

Nine clusters account for all 30 findings.

```
CLUSTER: engine-split-left-instance-gate-red + evidence-grep-broken-by-relocation
         (x5: IMP-0672, IMP-0678, IMP-0679, IMP-0684, IMP-0697)
Altitude:  CLASS, and ENGINE per skill §6 — "a citation naming a path plus a substring cannot
           tell relocation from absence" is true in any client's repo
Ladder row: "a tool could catch it mechanically" + "second instance → generalise"
Becomes:   verify-improvement-log.py reports THREE outcomes, not one; 4 citations re-pointed;
           2 adjudicated individually; one missing declaration line added
Retires:   nothing
Cites:     IMP-0672, IMP-0678, IMP-0679, IMP-0684, IMP-0697
Residual:  A citation whose substance was REWORDED in place is still undetectable — the gate
           cannot know a paraphrase preserves meaning. That case is reported, never auto-fixed.
           And no gate can tell that an applied_by describes only HALF of a proposed change;
           row 1 narrows that gap by checking the citation's target, not the prose.
```

**This is where the review's one narrowing lives.** The critical finding proposed: when a citation misses at `scripts/<name>.py`, look in `.engine/scripts/<name>.py`, then re-point all six. Measured individually:

| Citation | Resolves in `.engine/scripts/`? | Actual mechanism |
|---|---|---|
| IMP-0047, IMP-0247, IMP-0349, IMP-0638 | **Yes** | Relocated by the Phase 3f split — the proposal works |
| IMP-0338 | **No — nowhere in the repo** | The client-specific column name was *deliberately stripped* from the engine copy by the split's zero-client-literal rule. Confirmed by `git log -S` against the split commit |
| IMP-0470 | **No** | The substance survives **reworded** in the instance file — [line 25 says "plain argparse usage error"](../../scripts/verify-code-app-column-bindings.py#L25) where the citation expects an older sentence |

So the corrected count is **four true positives out of six**, and there are **three** mechanisms, not one. The follow-up finding caught two of the three; the stripped-literal case is identified here for the first time. Applying the original proposal verbatim would have left two entries broken while reporting them fixed — which is the exact failure the finding was logged to prevent.

```
CLUSTER: WBS evidence-rule integrity  (x3: IMP-0675, IMP-0680, IMP-0695)
Altitude:  CLASS for the mechanism (ENGINE), INSTANCE for the rules themselves (client data)
Ladder row: "a tool could catch it mechanically"
Becomes:   derive-wbs-state.py strips comments before matching and FAILS when a rule's only
           match is inside one; verify-wbs-chain.py warns on a directory-glob rule whose
           pattern carries no structural anchor
Retires:   nothing
Cites:     IMP-0675, IMP-0680, IMP-0695
Residual:  Nothing measures whether a rule is satisfiable only by the deliverable. That is a
           judgement, and the gate can only flag the SHAPE that has failed twice.
```

Two of these three describe rules that have **already been rewritten** — the contract file records both rewrites in its own notes. What has not changed is that [`derive-wbs-state.py`](../../scripts/derive-wbs-state.py) still matches a bare substring against file text with no comment handling at all, so the same rule shape can regress again tomorrow. A task read as complete for weeks on an XML comment stating the role had *no* privilege on the table the rule was proving.

```
CLUSTER: architect authoring defaults  (x2: IMP-0685, IMP-0692)
Altitude:  CLASS — both are "the agent file offers exactly one path and it is the wrong one"
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:   agents/architect-agent.md — two decision steps: author-new vs amend-approved, and
           decision vs check
Retires:   nothing
Cites:     IMP-0685, IMP-0692
Residual:  Neither is gateable. Whether an approved document already covers a feature is a
           reading, not a match.
```

Confirmed by grep: the agent file contains **no** occurrence of "amend" or any equivalent. One dispatch wrote a full architecture document that had to be discarded because an approved one already covered the area and carried the open question as a numbered row. A second superseded an approved section to match an evidence rule — treating a *check* as though it were a *decision*.

```
CLUSTER: secured-column surface completeness  (x4: IMP-0687, IMP-0688, IMP-0689, IMP-0690)
Altitude:  CLASS — four faces of "the column-security gates check what exists, not what is missing"
Ladder row: "second instance → generalise" (the omitted-column half is its THIRD instance)
Becomes:   one skill rule + three extensions to gates that already own this area — no new script
Retires:   the instance-patch pattern behind IMP-0337 / IMP-0338 / IMP-0688
Cites:     IMP-0687, IMP-0688, IMP-0689, IMP-0690
Residual:  The rollup check fires on nothing today — there is no rollup in the solution, verified
           by grep. That is deliberate: it is a guard placed before the first instance, not after.
```

All four premises verified: no `AppendTo` rule exists in any skill file; the coverage gate checks only the direction that catches an invented column; neither copy of the field-security gate mentions rollups; and the reachability gate's summary line reports only columns that already have a control.

```
CLUSTER: prose contradicting a corrected source  (x3: IMP-0677, IMP-0681, IMP-0686)
Altitude:  INSTANCE ×3 — three unrelated files, one shared shape, nothing joins them
Ladder row: "one instance, cause is general, a human needs to know it"
Becomes:   three targeted edits
Retires:   nothing
Cites:     IMP-0677, IMP-0681, IMP-0686
Residual:  No gate compares a prose claim against the file that settles it, and none is proposed —
           this repository has measured prose-reading gates at 48–100% false, five times.
```

The sharpest of the three: [`agents/pm-agent.md` line 59](../../agents/pm-agent.md#L59) still instructs the PM agent to park corrections against a document revision that [`contract/README.md` line 34](../../contract/README.md#L34) records as permanently cancelled. The agent file tells the agent to do the one thing that cannot work.

```
CLUSTER: three-file drift, stale counts, untriaged warnings  (x4: IMP-0666, IMP-0667,
         IMP-0668, IMP-0669)
Altitude:  INSTANCE for the test scope, CLASS-ALREADY-KNOWN for the count
Ladder row: "a tool could catch it mechanically" for the first; knowledge line for the rest
Becomes:   the settings test compares all three environment files, not two; two knowledge notes
Retires:   nothing
Cites:     IMP-0666, IMP-0667, IMP-0668, IMP-0669
Residual:  Nothing diffs a summary document's cited test count against what the build printed.
           Proposed as a knowledge line, not a gate — the citation is free prose.
```

The settings test is cheaper to fix than the finding assumed: [the file already loads the third environment's settings](../../src/tests/provisioning/DeploymentSettings.Tests.ps1#L21) for a different assertion, so only the comparison set widens.

```
CLUSTER: generated-file targeting and the dependency graph  (x2: IMP-0676, IMP-0683)
Altitude:  CLASS — "fix it where it is READ" versus "fix it where it is GENERATED"
Ladder row: "a tool could catch it mechanically"
Becomes:   wbs-ready-set.py reads the build-order constraints file and reports an added edge
           separately from a contracted one
Retires:   nothing
Cites:     IMP-0676, IMP-0683
Residual:  The added edge is a delivery judgement, not a contract term. Reporting the two
           separately is what keeps a non-contractual edge from being quoted as contractual.
```

Fully confirmed against the files: the accepted task graph records one dependency for the task in question and not the second one; the delivery-parameters file carries the missing edge **and** [a note saying the queue script does not read it](../../contract/delivery-parameters.json#L80). Both copies of the queue script were checked and neither reads that key. The queue is therefore answering with a known-wrong readiness today.

```
CLUSTER: baseline pin on a synced path  (x1: IMP-0682 — ALREADY RESOLVED by IMP-0691)
Altitude:  n/a — no change proposed; the defect was fixed before this review was dispatched
Ladder row: none reached. The ladder is for findings that still need a home
Becomes:   NOTHING in scripts/. IMP-0682 closes as resolved-by-IMP-0691. The one genuinely
           unlanded piece is IMP-0691's OWN skill note, folded into row 17
Retires:   proposed row 17 of draft 1, withdrawn — its premise measured false
Cites:     IMP-0682, IMP-0691, IMP-0697
Residual:  --check still prints only "STALE" and no parsed diff, which was the second half of
           IMP-0682's proposal. Deliberately NOT proposed — see below.
```

**This cluster proposes no change, and that is the corrected result.** Draft 1 proposed rewriting the pin to hash parsed content. Measured against the tree: that is exactly what the code already does, and has done since before this review was dispatched. Applying the row would have been re-doing finished work while claiming credit for it.

**On the half that genuinely is not done.** The older finding also asked that a stale check print *which* tasks, hours or dependencies changed rather than only the word `STALE`. Confirmed absent — [the check collects stale paths and prints their names](../../scripts/import-baseline.py#L320). But its stated purpose was to tell a harmless metadata drift apart from a real edit, **and a parsed-content hash means a harmless drift no longer makes the check stale at all.** The wolf-crying is gone; what remains is a smaller, unevidenced convenience for a scenario nobody has hit since the fix landed. Per the ladder's exclusion of *"it would be cleaner"* and *"it might happen"*, it is recorded here as residual with a return condition rather than proposed: **revisit if the check ever goes stale and a reader cannot tell from the output what actually changed.**

**Precedent for the disposition.** This is the same call already made twice in this review for the two evidence rules rewritten on 2026-09-09 — the instance is closed by work that landed before the review, the general lesson is what carries forward, and the entry closes rather than being re-derived next cycle.

```
CLUSTER: engine-generalisation singletons  (x6: IMP-0670, IMP-0671, IMP-0673, IMP-0674,
         IMP-0693, IMP-0694, plus IMP-0696 logged by this review)
Altitude:  mixed — see the table in §3
Ladder row: various
Becomes:   two skill clauses, one agent step, one gate fix, one sweep, one new gate
Retires:   nothing
Cites:     IMP-0670, IMP-0671, IMP-0673, IMP-0674, IMP-0693, IMP-0694, IMP-0696
Residual:  IMP-0673's lesson is ALREADY promoted in two places and needs no further change —
           recorded here so the entry can close rather than be re-derived next cycle.
```

Two entries in this cluster have had their instance resolved since they were written: the implementation plan the capability-mode finding says is untracked now [exists as a tracked document](IMPLEMENTATION-PLAN.md), and the shared-database default the selftest finding describes now takes a path parameter with the real default as fallback in the engine copy. In both cases the **general rule** remains unwritten, which is what is proposed.

### The finding this review logged itself

Deciding which copy of each script to edit produced a measurement worth recording, so it is logged as `IMP-0696` and processed here rather than left for next cycle.

**The engine migration left most scripts as byte-identical duplicates rather than wrappers.** Of the nine scripts this review proposes to change, **seven are identical twins** of a copy under `.engine/scripts/`, one is a genuine split, and one is instance-only. `.engine` is a git submodule. The build config invokes `scripts/<name>.py`, never the engine path — **so a change applied only to the engine copy would not run, while both files still parse and both still pass their own selftests.** Nothing measures which pairs are still unsplit; the delivery-parameters note rediscovered this for one script by hand.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/verify-improvement-log.py` + engine twin | Report three outcomes for a missed citation: relocated to the engine copy, substance absent everywhere, or present-but-reworded. **Also report an `APPLIED` entry dated after the citation requirement that carries no citation at all, and one whose citation names a different file from its own stated target** | IMP-0672, IMP-0678, IMP-0684, IMP-0697 | YES — `python3 scripts/verify-improvement-log.py --check` | already wired — `improvement-log-check`, [build config L80](../../config/revitalise-grant-automation-build.yml#L80) |
| 2 | other | `logs/improvement-log.jsonl` | Re-point 4 citations to the engine copy; adjudicate the 2 that do not resolve there individually | IMP-0678, IMP-0684 | YES — same command | N/A |
| 3 | other | `docs/plans/engine-instance-classification.md` | Add the one-line id-allocation declaration the uniqueness gate requires | IMP-0679 | YES — `python3 scripts/verify-requirement-id-uniqueness.py` | already wired |
| 4 | script | `scripts/derive-wbs-state.py` + engine twin | Strip XML/HTML and `#` comments before matching; FAIL when a rule's only match is in a comment | IMP-0680 | YES — `python3 scripts/derive-wbs-state.py` | already wired — PM gates |
| 5 | script | `scripts/verify-wbs-chain.py` + engine twin | Warn on an evidence rule combining a wildcard path with a pattern carrying no structural anchor | IMP-0680, IMP-0675 | YES — `python3 scripts/verify-wbs-chain.py` | already wired — PM gates |
| 6 | agent | `agents/architect-agent.md` + engine twin | Two steps: author-new vs amend-approved, and decision vs check when an ADR supersedes an approved section | IMP-0685, IMP-0692 | N/A — instruction change | N/A |
| 7 | skill | `skills/how-to-model-a-data-schema.md` | Lookup-privilege rule: a settable lookup needs Read + AppendTo on the target and Append on the referencing table | IMP-0687 | N/A — instruction change | N/A |
| 8 | script | `scripts/verify-tad-coverage.py` + engine twin | Add a reported source-to-document direction as a WARNING, with a per-table "describes a subset" opt-out | IMP-0688 | YES — `python3 scripts/verify-tad-coverage.py` | already wired — [L297](../../config/revitalise-grant-automation-build.yml#L297) |
| 9 | script | `scripts/verify-field-security-coverage.py` (engine half) | Report any rollup or calculated column deriving from a secured column; fail where the deriving column is itself unsecured | IMP-0689 | YES — `--selftest` plus the real corpus | already wired — `field-security-coverage` |
| 10 | script | `scripts/verify-forms-and-views-reachable.py` + engine twin | Summary line also names secured columns on tables with no main form, as an explicitly out-of-scope count | IMP-0690 | YES — run and read the summary line | already wired — [L306](../../config/revitalise-grant-automation-build.yml#L306) |
| 11 | agent | `agents/pm-agent.md` | Replace the cancelled-revision paragraph with the no-further-revision rule and the routing table | IMP-0681 | YES — `grep -c "outstanding for v0.6"` returns 0 outside errata | N/A |
| 12 | knowledge | `knowledge/domain/business-rules.md` | Narrow the business rule to the flow only; record that the commercial half was settled by the decision file | IMP-0677 | N/A | N/A |
| 13 | knowledge | `knowledge/technology/dataverse.md` | State that column-security profile membership is per-environment config, and give the command to read it | IMP-0686 | N/A | N/A |
| 14 | script | `src/tests/provisioning/DeploymentSettings.Tests.ps1` | Extend key-parity to all three environment settings files, naming accepted exceptions explicitly | IMP-0666 | YES — Pester run | already wired — `unit-tests` |
| 15 | knowledge | `knowledge/technology/code-apps.md` | Pre-triage the coverage sourcemap notice; require a cited test count to be re-measured at the revision citing it | IMP-0667, IMP-0668, IMP-0669 | N/A | N/A |
| 16 | script | `scripts/wbs-ready-set.py` + engine twin | Read the build-order constraints file; report an added edge separately from a contracted one | IMP-0676, IMP-0683 | YES — `python3 scripts/wbs-ready-set.py` | already wired — PM gates |
| 17 | skill | `skills/how-to-verify-a-platform-contract.md` | Three clauses: re-evaluate an assumption register after a deploy lands; a selftest must not write to a shared default resource; **hash raw bytes only when the bytes are the signed artefact, and parsed content for any container format a sync platform rewrites** | IMP-0670, IMP-0674, IMP-0691 | N/A — instruction change | N/A |
| 18 | script | `scripts/verify-shipped-content.py` + engine twin | Pair each site map with its own app module; add a two-app fixture | IMP-0693 | YES — `--selftest` with the new fixture | already wired — [L315](../../config/revitalise-grant-automation-build.yml#L315) |
| 19 | agent | `agents/improvement-agent.md` + engine twin | In capability mode, resolve every cited plan to a tracked path, or transcribe it as that phase's first deliverable | IMP-0671 | N/A — instruction change | N/A |
| 20 | other | `docs/plans/`, `docs/architecture/` | Fourth-instance sweep: drop line numbers from cross-document design citations in one pass | IMP-0694 | YES — `python3 scripts/verify-doc-line-links.py` | already wired |
| 21 | script | `scripts/verify-engine-instance-split.py` (new) | Report each `scripts/` ↔ `.engine/scripts/` pair as duplicate, wrapper, instance-only or engine-only; WARNING while the migration is in flight | IMP-0696 | YES — `--selftest` plus the real corpus | **SOFT (`--warn-only`)** — to be added to the build config in the same change |

**Row 17 carries a change that belongs to an already-closed entry.** The skill clause is `IMP-0691`'s own unlanded proposed change, not new work invented here — it is picked up because that entry closed on its script half alone and nothing else will now write it.

**Constraint budget: 0 of 3 used.** No new constraint row is proposed. Every item above lands in a script, a skill, an agent file or a knowledge page — the more mechanical homes the ladder prefers, and the constraint set already stands at 85 live rows.

### One row needs its wiring called out

Row 22 is the only genuinely new script. Per this agent's own rule, an unwired `verify-*.py` in `scripts/` is a red preflight, so it is wired in the same change — **SOFT**, because it reports a migration state that is legitimately in progress and a HARD gate would open red on work no dispatch owns.

---

## 4. Retirements

> Retirement check performed: 85 live constraint rows reviewed at class level against this batch's nine clusters; **none currently redundant**, because every proposed change extends a gate that already exists rather than replacing a rule, and no constraint in the set is superseded by any of them.

One retirement is real but is not a constraint row: **row 8 retires the instance-patch pattern** behind the omitted-column class, which has now been paid three times as three separate document corrections. Replacing it with the reported source-to-document direction is what the altitude rule requires on a third instance.

Derived at draft time, not retyped: **10 retired** and **85 live** constraint rows; **58** `verify-*.py` scripts in `scripts/`, which row 22 would make 59.

---

## 5. Findings left unprocessed

**Deferred:** none

All 29 unread entries were processed, plus the two this review logged itself (`IMP-0696`, `IMP-0697`).

**One `APPLIED` entry was read despite activation step 2, and it changed a conclusion.** `IMP-0691` is closed, so the step-2 rule excluded it from scope and draft 1 got the baseline-pin cluster wrong as a direct result. It was read after a reviewer challenge. It is cited, not processed — its status does not move — and the general problem it exposes is logged as `IMP-0697` and processed here.

**Two states were deliberately excluded from scope**, per this agent's activation step 2:

| State | Count | Why excluded | Where they are parked |
|---|---|---|---|
| `awaiting-approval` | 4 | A review already processed them and is parked at its own gate. The remedy is the keyword against **that** document, not a second review | IMP-0608 → [2026-09-05 review (2)](2026-09-05-improvement-review-2.md); IMP-0644, IMP-0645 → [2026-09-07 review (2)](2026-09-07-improvement-review-2.md); IMP-0652 → [2026-09-07 review (3)](2026-09-07-improvement-review-3.md) |
| `reviewer-deferred` | 143 | Each carries a reason a human accepted | On their own entries |

The four parked entries carry an `excluded_by` field naming this review, so declaring them here does not read as an unstamped processing claim. The 143 deferred entries are described as a class and not enumerated, which is why they need no such field.

---

## 6. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 692 | 694 |
| Distinct lessons | 686 | 688 |
| Recurring classes (x≥2) | 52 | 53 |

To be regenerated with `python3 scripts/generate-known-failure-modes.py` at apply time and confirmed with `--check`. Regenerating drifts a registered size claim, so `python3 scripts/verify-derived-counts.py` runs in the same change.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-10-improvement-review.md

Findings processed: 31 NEW  →  9 clusters
Regression check:   5 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 10 gates/scripts, 5 skill/knowledge edits,
                    3 agent-file edits, 0 retirements
Altitude calls:     6 generalised from instance to class, 2 left as notes
Withdrawn:          1 proposed change (row 17 of draft 1) — premise measured false
Digest:             will regenerate — 688 lessons, 53 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

Applied 2026-09-10 on `APPROVE IMPROVEMENTS`. **19 entries closed, 5 left open with a reason, 1 change withheld.**

| # | Change | Entries moved to APPLIED |
|---|---|---|
| 1 | `verify-improvement-log.py` + twin — three-way citation outcome, plus the no-citation check | IMP-0672, IMP-0678, IMP-0684, IMP-0697 |
| 2 | 6 citations re-pointed (4 relocated, 2 adjudicated individually) | — |
| 3 | `engine-instance-classification.md` id-allocation line | IMP-0679 |
| 4 | `derive-wbs-state.py` + twin — comment stripping, comment-only refusal | IMP-0680 |
| 5 | `verify-wbs-chain.py` + twin — `WEAK EVIDENCE RULE` warning | IMP-0675 |
| 6 | `architect-agent.md` — author-new vs amend; decision vs check | IMP-0685, IMP-0692 |
| 7 | `how-to-model-a-data-schema.md` — lookup privileges | *(IMP-0687 deferred)* |
| 8 | `verify-tad-coverage.py` + twin — source-to-TAD direction | IMP-0688 |
| 9 | `verify-field-security-coverage.py` (engine) — derived-column leak | *(IMP-0689 deferred)* |
| 10 | `verify-forms-and-views-reachable.py` + twin — out-of-scope count | IMP-0690 |
| 11 | `pm-agent.md` — no-v0.6 rule | IMP-0681 |
| 12 | `business-rules.md` — BR-F07 narrowed | IMP-0677 |
| 13 | `dataverse.md` — profile membership location | IMP-0686 |
| 14 | `DeploymentSettings.Tests.ps1` — three-file key parity | IMP-0666 |
| 15 | `code-apps.md` — two triage notes | IMP-0668, IMP-0669 *(IMP-0667 deferred)* |
| 16 | `wbs-ready-set.py` + twin — build-order edges; `_wiring_gap` re-dated | IMP-0683 *(IMP-0676 deferred)* |
| 17 | `how-to-verify-a-platform-contract.md` — three clauses | IMP-0674, IMP-0691 *(IMP-0670 deferred)* |
| 18 | `verify-shipped-content.py` + twin — per-app site-map pairing | IMP-0693 |
| 19 | `improvement-agent.md` — capability-mode plan resolution; count 57→59 | IMP-0671 |
| 20 | `#Lnnn` sweep + the sweep rule | IMP-0694 |
| 21 | `verify-engine-instance-split.py` (new) + SOFT wiring + history section | IMP-0696 |
| — | Closed on work that landed before this review | IMP-0673, IMP-0682, IMP-0695 |

### Withheld, and why

**The evidence-map-versus-ADR cross-check (`IMP-0695`'s proposal) was not built.** Its instance is
fixed — the rule was rewritten on 2026-09-09 — but the proposed general gate reads prose semantics
to decide whether an ADR rejected a path, and that instrument has measured 48–100% false five times
in this repository. Building it would have shipped a sixth. The partial mitigation is row 5's
weak-rule warning, which catches the *shape* rather than the *supersession*.

### Narrowed, and the false positives the narrowing removes

Three changes were narrowed by measurement rather than applied as written. Each names what it removed.

1. **Row 2 — the citation re-point.** The finding asked for all six to be re-pointed into the
   engine directory. Measured one at a time: four resolve there; `IMP-0338`'s literal was *stripped*
   by the split's zero-literal rule (confirmed by `git log -S` against the split commit) and now
   points at the architecture document that carries it; `IMP-0470`'s substance survives *reworded*
   and now names the current wording. Applying it verbatim would have pointed two entries at text
   that is not there.

2. **Row 1's no-citation check — redesigned twice, on the corpus.** First cut: **20 findings, 3 true
   positives** — 17 were the 2026-08-21 cohort the existing "110 entries predate the requirement"
   note already exempts by name, because the date boundary was `<` where it had to be `<=`. Second
   cut: **3 findings, 1 true positive** — two were `type: none` / `target: n/a` closures, which by
   construction have no artefact to cite. Final: **1 finding, 1 true positive**, and it is
   `IMP-0691`, the entry that motivated the check. The selftest passed at every stage; only the
   corpus run caught either error.

3. **Row 8's new direction reports 60 columns across 4 tables, and the subset declarations are
   ROUTED, not applied.** Marking a table as deliberately-a-subset is an edit to an approved
   architecture document, which belongs to `architect-agent` — applying it here would be precisely
   the ownership inversion row 6 was written to stop. Routed with the measurement.

### Left open, with a reason — 5 entries

None of these could be re-observed at the level their defect was visible at, and a document saying
a thing is fixed is not that observation.

| Finding | Level | Change landed? | Why still open |
|---|---|---|---|
| IMP-0667 | V2 | yes | the re-observation needs the code-app test suite; `npx` exits 127 here |
| IMP-0670 | V3 | yes | needs a real test cycle against a live environment |
| IMP-0676 | V4 | yes, and proven by execution | needs a signed-in user to see the form render |
| IMP-0687 | V4 | yes | the finance role does not exist in source yet |
| IMP-0689 | V4 | yes, fixture-proven | no rollup exists to observe; the guard precedes the first instance |

### Verification actually executed

Both polarities were proven for every new check, because a green selftest is not evidence a gate is
correct:

- **Comment-only evidence rule** — rejected on the fixture reproducing the 8.2 regression; a real
  granted privilege still matches. All 61 derived task statuses unchanged.
- **Weak-rule warning** — 7 findings on the real map, all 7 defensible (5 strong, 2 moderate), gate
  still passes.
- **Derived-column leak** — 0 on the real corpus, which is correct because no rollup exists;
  positive fixture proves it fires.
- **Out-of-scope secured columns** — reproduces this finding's own predicted figure exactly:
  16 columns on 2 tables under `--committed-only`.
- **Per-app site-map pairing** — two-app fixture shows the old cross-join would have produced 2
  false failures; single-app corpus unchanged.
- **Engine/instance split gate** — 4 states distinguished, both exit paths proven,
  mtime-insensitivity proven. Corpus: **85 scripts, 66 unsplit duplicates**.
- **Settings key parity** — 41 tests, 40 passed, 1 skipped, 0 failed; failure polarity proven
  separately.
- Log: **0 errors, 0 triggers, 694 entries**. Digest regenerated and `--check` current.
  `verify-derived-counts.py`: **10 of 10 claims match**. Build-config preflight: exit 0.
- All 7 edited scripts confirmed **in sync with their engine twins**.

**Not verified:** nothing was run against a live environment, and no V3/V4 observation was made —
hence the five open entries above.

### Known at draft time, to be honoured at apply time

0. **IMP-0682 closes as resolved by IMP-0691's fix, not by anything this review does.** Its `applied_by` must name commit `a1ae2e5` and `pmsources.wbs_content_fingerprint()`, and its citation must point at [the lock file's own record of the method](../../contract/source-lock.json) — never at this document.
1. **Row 2 is a narrowing, not the proposal as written.** Four citations re-point to the engine copy; the two that do not resolve there are adjudicated individually and the deviation is recorded on the entry, here, and in the gate output.
2. **Every applied entry needs a citation pointing at the change itself**, not at this document. The disposition simulation confirmed that citations aimed at the review document fail, which is correct behaviour — a review document is not the applied change.
3. **Seven of the nine scripts are byte-identical twins.** Each script change states which copy it lands in, and a change that lands only in the engine copy does not run.
