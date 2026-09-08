# Improvement Review — 2026-09-08 (2)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 19 `NEW` (all `unread`) → 7 clusters
**Trigger:** reviewer request (via lead-agent)
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**Two of the three priorities the dispatch brief set do not exist in this review's scope, and the third is one finding.** The brief asked for the gate-defect / gate-cannot-fail / gate-reassures-wrongly classes first, then remaining `blocker` entries. Measured against the queue: of the 19 `unread` findings, exactly **one** is a gate class ([`gate-invocation-omits-required-arg`](../../logs/improvement-log.jsonl#L608)), and **zero** are `blocker`.

The 18 other `NEW` gate-class findings are all `reviewer-deferred` — each carries a `deferred_reason` a human already accepted — and [activation step 2](../../agents/improvement-agent.md#L98) says to leave those alone and report them as deferred. The 39 `NEW` blockers divide the same way: 38 are `reviewer-deferred`, and the one that is not is [IMP-0661](../../logs/improvement-log.jsonl#L658), which is `awaiting-approval` against [2026-09-08-improvement-review.md](2026-09-08-improvement-review.md) — a review already parked at its own gate. [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py) says so in terms: *"DO NOT run another review and DO NOT re-derive the analysis."*

**So the single most useful thing in this document is not a proposed change. It is that one blocker is waiting on a keyword against a different document, and this review cannot clear it.**

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`run-source-gates.py`](../../scripts/run-source-gates.py) 13 → 16 gates + uncovered list | 2026-09-08 | `live-environment-value-in-evidence-comment` | NO | **Working.** Re-executed: reports 16 source gates of 73 steps and names 57 uncovered |
| [`agents/development-agent.md`](../../agents/development-agent.md#L45) scope correction | 2026-09-08 | same | NO | **Working**, but its `Verify By` was unsatisfiable — see below |
| [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L363) in-source marker rule | 2026-09-08 | same | NO | Working — leave alone |
| [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) registry, wired [SOFT](../../config/revitalise-grant-automation-build.yml#L222) | earlier | `hand-maintained-count-drifts-from-source` | **YES — x36** | **The gate exists, is wired, and its output is unread.** See cluster C |

**Changes whose class recurred after a prose fix:** the artifact-directory conflation ([reviews 40 and 43](2026-09-05-improvement-review.md), three prose edits) recurred a fourth time. Per the regression rule that is wrong-altitude evidence and calls for a gate — and the gate the finding proposes measures 41% false. Cluster F.

**Changes whose class recurred after a gate:** `hand-maintained-count-drifts-from-source`. The gate fired correctly and nobody read it. Cluster C.

### A prior review's own `Verify By` was unsatisfiable by construction

Review 6 change 2 declared its verification as *"`grep -c 'every HARD gate over the source you just wrote'` must return 0"*. Executed today it returns **1**, and the change is nonetheless correct and fully applied: the hit is inside the change's own erratum, which retains the withdrawn wording per this repository's documentation-correction convention.

This is the prose-polarity trap this project has measured five times ([`IMP-0422`, `IMP-0428`](../../skills/how-to-report-to-the-reviewer.md#L155)) arriving one position further out — not in a gate that reads prose, but in **a review's own verification criterion**. A corrected file contains strictly *more* of the offending phrase than the defective one, so a phrase-absence criterion can only ever be met by a file nobody has corrected. Recorded as a new finding rather than a change; the rule against phrase-based *gates* exists, and the rule against phrase-based *`Verify By` clauses* is its obvious extension awaiting a second instance.

---

## 2. Clusters and promotion decisions

**Seven cluster blocks account for 16 of the 19 findings. The other three are dispositioned, and here is where**, so the arithmetic is closeable rather than implied:

| Finding | Class | Where it is dispositioned |
|---|---|---|
| [IMP-0631](../../logs/improvement-log.jsonl#L628) | `verification-level-overstated` (x1) | Change 4 — a single instance, but a crisp platform fact, and it edits the same file and the same table as cluster A. Not folded into cluster A's class |
| [IMP-0646](../../logs/improvement-log.jsonl#L643) | `figure-restated-not-cited` (x1) | §5, **withheld** — already fixed, and its premise has since reversed |
| [IMP-0648](../../logs/improvement-log.jsonl#L645) | `source-comment-overstates-log-evidence` (x1) | §5, **routed** to development-agent and left open; re-measured and confirmed still real |

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x58; here x4: IMP-0613, IMP-0614, IMP-0615, IMP-0620)
Altitude:   CLASS — but three of the four are INSTANCES OF RULES THE TARGET FILE ALREADY STATES
Ladder row: "a platform law, or a third instance" → the existing skill, extended, not a new section
Becomes:    skills/how-to-verify-a-platform-contract.md — two rows in the existing governing-artefact
            table, one clause on the existing negative-claim rule, one genuinely new sub-case
Retires:    nothing
Cites:      IMP-0613, IMP-0614, IMP-0615, IMP-0620
Residual:   None of this is gateable and the findings say so. A DocuSign template's configured role
            names exist only inside DocuSign; no CLI or Web API route reaches them. The rule depends
            on being read.
```

**The load-bearing finding here is that the file already says most of this.** Three of the four entries propose *adding a rule*, and [§2's governing-artefact rule](../../skills/how-to-verify-a-platform-contract.md#L68) and [§2's negative-claim rule](../../skills/how-to-verify-a-platform-contract.md#L158) already state both properties in full generality. What is genuinely missing is narrower: two rows in an existing table, one clause naming a new domain, and one real gap — the evidence scale has no notion of a contract that is **unreachable at every level from this session**, which is what a connector parameter marked `dynamic` is.

Applying the rule proposed in cluster E to this very batch is what produced that finding, and it changed three dispositions.

```
CLUSTER: stale-claim-contradicting-rechecked-source  (x6; here x2: IMP-0617, IMP-0618)
Altitude:   INSTANCE for one, LAW-BY-ABSENCE for the other
Ladder row: "an agent had the information and still did the wrong thing" → agent file
Becomes:    agents/pm-agent.md — re-run the gate before writing a known-exceptions waiver
Retires:    nothing
Cites:      IMP-0617
Residual:   IMP-0618's fact (a DocuSign template's own reminder cadence) lives outside this
            repository and outside every connector call this project has made. No change proposed;
            the TAD amendment routes to architect-agent.
```

Re-measured by execution: [`wbs-ready-set.py`](../../scripts/wbs-ready-set.py) reports tasks 3.3 and 3.4 with `unmet_dependencies=[]`, so the predecessor waiver that was requested would have waived a gate that is not firing. Deliberately **not** proposed as a gate: an exception's `matches` field is free text, and a gate reading it for semantics is the instrument measured at 48–100% false.

```
CLUSTER: hand-maintained-count-drifts-from-source  (x36; here x3: IMP-0625, IMP-0626, IMP-0657)
Altitude:   CLASS, already generalised once — this is a READ-PATH failure, not a gate gap
Ladder row: "the system's own memory failed" → a read-path change
Becomes:    agents/improvement-agent.md — verify-derived-counts.py joins the closing checklist
Retires:    nothing
Cites:      IMP-0625, IMP-0626, IMP-0657
Residual:   The gate stays SOFT and stays wired --warn-only. Three of the four live drifts are in
            delivery documents this review does not own; they route out.
```

The Pester half is closed: the fix derived the count from source, was re-run green (45/45), and was proven to generalise on a scratch tree. The remaining half is that **the gate works and its output is unread.** Executed this session, [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py) fails with **4 drifted claims and 1 registry defect** — the digest line count the finding predicted, plus three nobody has caught: two secured-column figures in the Dev Summary saying 67 against a measured 69, and one in `REV Trustee.xml` saying 51 against 53.

```
CLUSTER: premise-in-the-improvement-pipeline-never-measured  (IMP-0632, IMP-0660, and IMP-0653/IMP-0635 as evidence)
Altitude:   CLASS — 2 instances that changed an outcome, 2 more where the existing rule caught it
Ladder row: "an agent had the information and still did the wrong thing" → agent file
Becomes:    agents/improvement-agent.md step 6 — the grep obligation extends to the findings being
            processed, at DRAFT time, not only to this agent's own rationale at APPLY time
Retires:    nothing
Cites:      IMP-0632, IMP-0660
Residual:   No gate reads a proposed_change's content and none reasonably could — the validator
            checks the field's TYPE only. This clause is the only control, and it is prose.
```

The existing [step-8 clause](../../agents/improvement-agent.md#L152) is scoped to *this agent's own* assertions. The same failure happens one position upstream, in a finding's `proposed_change`, written mid-incident by an agent under no obligation to grep the file it proposes to change — and it is caught at apply time, which is late. Two of four findings in one prior batch failed this; one approved change's wording filtered a config by a severity field that config does not carry.

**This review is its own fourth instance, in three places**, which is why the clause belongs at step 6: cluster A's premise (a skill needs new rules) was wrong, cluster F's proposed gate measures 41% false, and one routed item had already been fixed. All three were found by grepping before drafting, not after approval.

```
CLUSTER: harness-blocks-destructive-call  (x15; here x1: IMP-0636)
Altitude:   INSTANCE — a documented claim is over-confident and should claim less
Ladder row: "an agent had the information and still did the wrong thing" → agent file
Becomes:    agents/pipeline-agent.md — the pac-credential-path exemption is observed, not guaranteed
Retires:    nothing
Cites:      IMP-0636
Residual:   The refusal boundary is still not isolated to one condition, and this change does not
            isolate it. It stops the document predicting an outcome it cannot predict.
```

**Stated explicitly because of this class's history:** this is **not** a bypass proposal. It makes the document claim *less*, not the classifier observe *less*. Nothing is relocated to a broader-permissioned session and nothing is described as smaller than it is — the change adds a caveat that an identical `pac solution import` against the same org was allowed on 2026-09-05 and refused on 2026-09-07. [Improvement review 21](2026-08-23-improvement-review-6.md) proposed an actual bypass in this class and had to be rejected; the distinction is that the legitimate response is additive, and this one is.

```
CLUSTER: wrong-artefact-cited-as-evidence  (x6; here x1: IMP-0612)
Altitude:   LAW — a platform tool's output label is wrong, verified against a live query
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge
Becomes:    knowledge/technology/build-and-deploy.md — pac's printed "Import ID" is the
            asyncoperationid, never the importjobid
Retires:    nothing
Cites:      IMP-0612
Residual:   No gate. Nothing in the repository can distinguish the two guid classes after the fact;
            the check is a live importjobs query at the moment of writing the log line.
```

```
CLUSTER: gate-invocation-omits-required-arg  (x4: IMP-0470, IMP-0479, IMP-0494, IMP-0611)
Altitude:   CLASS, and the altitude rule FORBIDS a fourth prose patch
Ladder row: "second instance of the same class → generalise. Instance patches are forbidden here."
Becomes:    NOTHING THIS REVIEW APPLIES — the proposed gate is withheld on measurement
Retires:    nothing
Cites:      IMP-0611
Residual:   The class stays undefended, and this is stated rather than papered over.
```

**The gate the finding proposes measures 41% false before it is written.** It asks `resolve-artifact-dir.py` to warn when a resolved feature-slug has no prior manifest history under a build config another slug does. Enumerated against the real corpus of 69 artifact directories: `revitalise-grant-automation` — identical to the build config's own `feature:` field, and the exact string whose use was the defect — is the **most common legitimate feature slug in the tree, at 28 of 69 directories**. Any check keyed on that equality fires on 28 legitimate builds.

This is the fail-closed case where enumerating the corpus *is* the design, and the enumeration rejects the design. Three prose patches already exist for this class and the altitude rule forbids a fourth. The honest disposition is an open entry and a decision for the reviewer.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L68) | Two rows in the existing governing-artefact table — a connection reference's *declared-in-this-release* state cites `Other/Customizations.xml`'s `<connectionreferences>`, never the TAD's target-state connector table; a platform-assigned role identifier cites the artefact's own configuration, never a requirement document's description of signing order | IMP-0613, IMP-0615 | N/A — instruction change | N/A |
| 2 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L158) | One clause extending the existing negative-claim rule from a solution's attribute set to a **connector's full action/trigger catalogue**: a negative answer from one action's parameter list answers only *"does THIS action do X"* | IMP-0620 | N/A — instruction change | N/A |
| 3 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L54) | New sub-case under the E table: a connector parameter documented as **`dynamic`** resolves per-instance in the designer only — no E1 route exists from any CLI or Web API, so the static shape is at best E2 and the dynamic half is a mandatory named pre-activation V4 step. Plus the drifted *"×52"* in [§2](../../skills/how-to-verify-a-platform-contract.md#L234) re-measured to ×58 | IMP-0614 | N/A — instruction change | N/A |
| 4 | skill | [`skills/how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L414) | Name `pac solution check` in the **V2** row and add the caution that the Solution Checker is a static analyser over a packaged zip and is never evidence of V3 — V3 needs an import/deploy of the same content in [`logs/pipeline.log`](../../logs/pipeline.log) | IMP-0631 | N/A — instruction change | N/A |
| 5 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L124) | Step 6: the *"grep it"* obligation extends to the `proposed_change` and stated instance counts of every finding this review processes, at draft time | IMP-0632, IMP-0660 | N/A — instruction change | N/A |
| 6 | agent | [`agents/improvement-agent.md`](../../agents/improvement-agent.md#L462) | `python3 scripts/verify-derived-counts.py` joins the *before you close* block, with the reason that regenerating the digest mechanically drifts a registered claim. Plus the note that `excluded_by` is a **path** field, resolved to a file, so appended prose fails as *"does not exist"* | IMP-0657 | YES — the command is in the block | N/A |
| 7 | agent | [`agents/pm-agent.md`](../../agents/pm-agent.md#L64) | Before writing a [`contract/known-exceptions.json`](../../contract/known-exceptions.json) entry that waives a described gate violation, re-run the gate and record its actual current output in the entry's `reason` | IMP-0617 | N/A — instruction change | N/A |
| 8 | agent | [`agents/pipeline-agent.md`](../../agents/pipeline-agent.md#L273) | The pac-credential-path exemption is **observed, not guaranteed**: a prior success by the same tool against the same org is not predictive, and step 3a's search for a native `pac` verb does not guarantee non-refusal when the verb *is* `pac` | IMP-0636 | N/A — instruction change | N/A |
| 9 | knowledge | [`knowledge/technology/build-and-deploy.md`](../../knowledge/technology/build-and-deploy.md#L197) | `pac solution import`'s printed *"Import ID"* is the **asyncoperationid**, not the `importjobid`; resolve the real one with a live `importjobs` query filtered on `solutionname` + `createdon` before citing any id as evidence of a specific import | IMP-0612 | N/A — instruction change | N/A |
| 10 | skill | [`skills/how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L345) | Under *After appending*: any programmatic rewrite of the log must use `json.dumps(..., ensure_ascii=False)` — the default escapes non-ASCII and silently breaks every `evidence_grep` needle containing an em-dash | (this review) | YES — 4 of 351 needles carry non-ASCII | N/A |

**Constraint budget: 0 of 3 used.** No new constraint is proposed. Every cluster either had no mechanical home (clusters A, B-half, E, G), was already gated (cluster C), or had its proposed gate disproved on measurement (cluster F).

Row 10 comes from this review's own simulation rather than from a finding, and is flagged as such: rewriting the log through `json.dumps` at default settings converted two live `evidence_grep` needles to `—` escapes and made the gate report a false claim against a correctly-applied entry. A finding will be appended for it.

---

## 4. Retirements

> Retirement check performed: **85 active constraint rows** reviewed (10 already retired, derived with `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l`), **none currently redundant.**

The check was mechanical and it produced a measured false-positive rate worth recording. Scanning every active row's `Verify By` for a named `verify-*.py` that does not exist on disk returned **3 findings, 0 true positives**: [`C-TECH-076`](../../constraints/technology/technology-constraints.md#L146) names `verify-css-line-height.py` only in a *"renamed from"* history clause, and the two deleted length-limit gates appear only inside [`C-TECH-049`](../../constraints/technology/technology-constraints.md#L157)'s own retirement note.

That is the polarity trap again: **a correctly-retired row contains more mentions of the dead script than a live row does.** The detector is therefore not proposed as a gate. The ground is already covered properly by [`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py), which asserts on path existence rather than on prose and reports PASS today — 119 paths named by 85 active rows all resolve.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0611, IMP-0648

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [IMP-0611](../../logs/improvement-log.jsonl#L608) | `gate-invocation-omits-required-arg` | Fourth instance. The altitude rule forbids a fourth prose patch, and the gate its own `proposed_change` names measures 28 false positives in a 69-directory corpus. Stays open rather than closed on a change that would cry wolf | a gate design is found that keys on the dispatch's own declared feature identity rather than on manifest history, or a fifth instance arrives |
| [IMP-0648](../../logs/improvement-log.jsonl#L645) | `source-comment-overstates-log-evidence` | Routed to development-agent as a source-comment correction; not closable by this review, which cannot verify the corrected comment | the stale phase-1 header comment is corrected and the correction is committed |

**States excluded from this review's scope, per activation step 2:** 139 `reviewer-deferred` (each carries a `deferred_reason` a human accepted) and 6 `awaiting-approval` (each already has a review document parked at its own gate — [IMP-0608](../../logs/improvement-log.jsonl), [IMP-0644](../../logs/improvement-log.jsonl), [IMP-0645](../../logs/improvement-log.jsonl), [IMP-0652](../../logs/improvement-log.jsonl), [IMP-0662](../../logs/improvement-log.jsonl), and the blocker [IMP-0661](../../logs/improvement-log.jsonl#L658) → [2026-09-08-improvement-review.md](2026-09-08-improvement-review.md)). These are not deferrals by this review and are not stamped as such; they were already dispositioned.

### Withheld — proposed by a finding, disproved before drafting

| Item | Why withheld |
|---|---|
| A cross-check gate on [`resolve-artifact-dir.py`](../../scripts/resolve-artifact-dir.py) | 28 of 69 artifact directories legitimately carry the build config's own `feature:` string as their feature slug. 41% false on day one |
| [IMP-0646](../../logs/improvement-log.jsonl#L643)'s comment correction | **Already fixed, and its premise has reversed.** The comment it describes is gone from `FieldSecurityProfiles.xml` (0 hits on `identically twice\|attempts 1\|failed twice\|twice`), and `logs/pipeline.log` now holds **two** matching FAILED entries, so *"twice"* would have become correct. Withheld and reported, never dispatched |

### Routed out — re-measured and confirmed valid

| Item | Owner | Evidence it is still real |
|---|---|---|
| Stale phase-1 header comment, `FieldSecurityProfiles.xml` ~L467–475 | development-agent | Read today: still says *"Twelve columns in THIS phase-1 build variant"* and *"temporarily UNRELEASED here"*. Executed [`verify-field-security-coverage.py`](../../scripts/verify-field-security-coverage.py): **PASS, 69 secured columns, 0 baselined findings** — phase 2 has landed, so the comment is stale |
| 3 drifted derived counts in delivery documents | development-agent | Executed [`verify-derived-counts.py`](../../scripts/verify-derived-counts.py): Dev Summary L4611 and L4768 say 67 against a measured 69; `REV Trustee.xml` L73 says 51 against 53 |
| 1 registry defect — `pipeline-rev-setting-row-count` | development-agent | The three deployment-settings files disagree with each other (18 / 16 / 16), so there is no single truth to compare the claim against |
| TAD §5.9's reminder mechanism is stale | architect-agent | Reviewer configured reminders natively on the DocuSign template at 2 and 5 days; the TAD describes a flow-scheduled 3-and-7-day cadence |

---

## 6. Digest impact

All four figures measured, not estimated. The digest was **regenerated at draft time**, because two findings were appended and the standing obligation in `CLAUDE.md` applies to any agent that appends one — validator first, then generator.

| | Before | After |
|---|---|---|
| Log entries | 659 | **661** (two findings appended) |
| Distinct lessons | 653 | **655** |
| Recurring classes (x≥2) | 52 | **52** (both new findings are singleton classes) |
| Digest lines | 662 | **664** |

Confirmed current: `generate-known-failure-modes.py --check` reports both the digest and the appendix current at 661 entries.

### The regeneration drifted a registered count, live, exactly as cluster C predicts

Regenerating the digest moved it from 662 to 664 lines, which immediately falsified the registered claim `known-failure-modes-digest-line-count` at [`generate-known-failure-modes.py` L46](../../scripts/generate-known-failure-modes.py#L46) — *"the digest is 661 lines"* against a measured 664.

**This is not incidental to the review; it is the review's own evidence.** The drift was created by the one step every review is *required* to perform, it is reported only into a SOFT aggregate nobody reads, and it is precisely the coupling change 6 exists to name. It is left uncorrected deliberately: correcting it is part of applying change 6, and nothing may be applied before the keyword. It is SOFT and blocks no build.

### Two findings appended by this review

| Finding | Class | Why it exists |
|---|---|---|
| [IMP-0663](../../logs/improvement-log.jsonl#L660) | `verify-by-criterion-inverted-by-correction-convention` | Review 6 change 2's `Verify By` asserts the absence of a phrase, which this repository's correction convention makes unsatisfiable — see §1 |
| [IMP-0664](../../logs/improvement-log.jsonl#L661) | `serialisation-default-invalidates-evidence-needle` | `json.dumps` at default settings escapes non-ASCII and silently breaks `evidence_grep` needles — found by this review's own simulation, and the reason for change 10 |

Both are `unread` by design: this review appended them and did not process them, so no `reviewed_in` is stamped. They are the queue's only two `unread` entries after this review.

---

## 7. Simulation — what this disposition actually clears

Run before parking, on a scratch copy, with the real log restored and confirmed byte-identical by `diff`:

| | Before | After |
|---|---|---|
| `unread` | **19** | **2** (only the two findings this review appended) |
| `awaiting-approval` | 6 | 25 |
| `reviewer-deferred` | 139 | 139 |
| Citation-stamp WARNINGs from this batch | 15 | **0** |
| Gate exit | FAILED — 1 problem | FAILED — 1 problem |

The `after` column is **measured on disk**, not simulated: `reviewed_in` was stamped on all 19 entries at draft time per [activation step 6](../../agents/improvement-agent.md#L124), which is the one piece of bookkeeping that belongs to drafting rather than approval. `status` stays `NEW` and no `applied_by` exists yet. The 19 stamped rows are the only lines that changed — verified by `diff` against a pre-stamp backup at 38 changed lines, 19 rows × 2.

**The gate still fails after this review, and that is correct.** The one remaining problem is the pre-existing blocker trigger on [IMP-0661](../../logs/improvement-log.jsonl#L658), which only the keyword against [its own review document](2026-09-08-improvement-review.md) can clear. This review cannot clear it and does not claim to.

The first simulation run reported a *second* problem — an `evidence_grep` failure against [IMP-0564](../../logs/improvement-log.jsonl) — which was an artefact of the simulation harness, not of the disposition. Confirmed by re-running with `ensure_ascii=False`, after which it disappears. That is change 10.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-08-improvement-review-2.md

Findings processed: 19 NEW  →  7 clusters
Regression check:   4 prior changes audited, 1 class recurred (after a gate that fired and was unread)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 6 skill/knowledge edits,
                    4 agent-file edits, 0 retirements
Altitude calls:     3 generalised from instance to class, 4 left as notes, 2 withheld on measurement
Digest:             regenerated at draft time — 655 lessons, 52 recurring classes, 664 lines

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 9. Applied — 2026-09-08

**All 10 changes applied as drafted. No narrowing was required.** Three items were withheld or left open, each measured and named below; one finding was added to scope mid-application.

| # | Change | Where | Entries moved to APPLIED |
|---|---|---|---|
| 1 | Two rows in the governing-artefact table — connection references cite `Customizations.xml`; a platform-assigned role identifier cites the artefact's own config | [`how-to-verify-a-platform-contract.md`](../../skills/how-to-verify-a-platform-contract.md#L82) | IMP-0613, IMP-0615 |
| 2 | The negative-claim rule extended to a connector's full action/trigger catalogue | [same, §2](../../skills/how-to-verify-a-platform-contract.md#L211) | IMP-0620 |
| 3 | A `dynamic` connector parameter has **no E1 route** — the scale runs out, and the dynamic half becomes a mandatory pre-activation V4 step. Plus `×52` → `×58` | [same, §2](../../skills/how-to-verify-a-platform-contract.md#L68) | IMP-0614 |
| 4 | `pac solution check` named in the **V2** row, plus a subsection: the Solution Checker never evidences V3, and V4's absence below V3 is not a FAIL | [same, §5](../../skills/how-to-verify-a-platform-contract.md#L479) | IMP-0631 |
| 5 | Step 6 gains *"grep the premises of every finding you are processing"* — the tracked-file grep obligation extended to findings' `proposed_change` and instance counts, at **draft** time | [`improvement-agent.md`](../../agents/improvement-agent.md#L136) | IMP-0632, IMP-0660 |
| 6 | `verify-derived-counts.py` joins the *before you close* block unconditionally; two field shapes (`excluded_by` is a path; `ensure_ascii=False`) | [`improvement-agent.md`](../../agents/improvement-agent.md#L495) | IMP-0657, **IMP-0665**, IMP-0664 |
| 7 | Never write a known-exceptions waiver without re-running the gate; the source-complete trap named | [`pm-agent.md`](../../agents/pm-agent.md#L74) | IMP-0617 |
| 8 | The pac-credential-path exemption is **observed, not guaranteed** | [`pipeline-agent.md`](../../agents/pipeline-agent.md#L288) | IMP-0636 |
| 9 | `pac`'s printed *"Import ID"* is the asyncoperationid, never the `importjobid` | [`build-and-deploy.md`](../../knowledge/technology/build-and-deploy.md#L212) | — (see below) |
| 10 | Any scripted rewrite of the log uses `ensure_ascii=False` | [`how-to-log-an-improvement.md`](../../skills/how-to-log-an-improvement.md#L349) | IMP-0664 |
| — | No change required; lesson recorded for the digest | — | IMP-0618, IMP-0635, IMP-0653 |

### One finding ADDED to scope during application, and why that was not silent

[IMP-0665](../../logs/improvement-log.jsonl) was appended **at 10:05, after this draft was parked**, by a concurrent `improvement-agent` session applying [review 1](2026-09-08-improvement-review.md). Its class is `mandatory-closing-step-dirties-a-registered-derived-count` — **the same mechanism as IMP-0657**, logged independently five days later by a different session.

It was closed against change 6 rather than left `unread`, because leaving a finding unread whose fix has just landed is what re-summons a strategic-tier dispatch onto settled work. That is a scope addition beyond the approved draft and is reported here and in the gate output rather than taken quietly.

### Withheld and left open — three items, each with its measurement

| Item | Disposition | The measurement that forced it |
|---|---|---|
| A cross-check gate on `resolve-artifact-dir.py` ([IMP-0611](../../logs/improvement-log.jsonl)) | **WITHHELD**, entry left `NEW` with a `revisit_when` | 28 of 69 directories under `build/artifacts/` legitimately carry the build config's own `feature:` string. 41% false, and the altitude rule forbids a fourth prose patch |
| [IMP-0612](../../logs/improvement-log.jsonl)'s closure | **Change APPLIED, entry left open** | `observable_at` is **V3** and the closure needle would point into `knowledge/` — a prose needle proves only that the lesson was written down. Re-observing needs a live `importjobs` query, and this session has no credentialled route |
| [IMP-0646](../../logs/improvement-log.jsonl)'s comment correction | **WITHHELD as already-fixed** | The comment is gone from `FieldSecurityProfiles.xml` (0 hits), and `logs/pipeline.log` now holds **two** matching FAILED entries, so its *"twice"* would have become correct |

**Change 10 was applied to the drafted target, so no substitution stands.** The rule is in `how-to-log-an-improvement.md` §3 for anyone appending by script, and additionally in `improvement-agent.md` for the whole-file rewrite only this agent performs.

### Re-verification performed before applying, per activation step 8

- **No `corrects` warning names any entry in scope.** The five that exist are pre-existing, against IMP-0290/0298/0320/0430/0437, none of which this review processes.
- **Executed rather than read:** `wbs-ready-set.py --json` (tasks 3.3/3.4 both `unmet_dependencies=[]`, confirming change 7's premise); `verify-field-security-coverage.py` (PASS, 69 secured columns, 0 baselined — confirming the routed item is real); `verify-derived-counts.py` (3 drifts + 1 registry defect, all routed).
- **Re-observed rather than accepted on report:** Pester re-run today on `EnsureSchema.Tests.ps1` — **45 passed, 0 failed, 20.08s**, zero `Should -Be 68` literals remaining. Recorded as `reobserved` at V2 on IMP-0625 and IMP-0626.
- **Deferral premises re-measured at apply time:** the 28-of-69 figure and the stale phase-1 comment both confirmed unchanged.
- **A concurrent session was detected and checked for collision.** Review 1 was applied at ~10:45 and touched `agents/development-agent.md`; this review touches none of the same files. `agents/improvement-agent.md` was last modified 2026-09-04, so nothing was clobbered. Every log write in this application asserts that the id set is unchanged before writing, after the first whole-file rewrite silently risked exactly that.

### Post-application state

`verify-improvement-log.py --check` exits **0** — `OK (schema + triggers)`, **0 `unread`**, and the blocker `TRIGGER` this review reported as open is **gone**, cleared by review 1's own application. The digest is current at **662 entries, 665 lines, 656 teaching lessons**. `verify-derived-counts.py` — newly in this agent's closing checklist by change 6 — reports the digest line count **correct** and three drifts remaining in delivery documents, all routed to development-agent.
