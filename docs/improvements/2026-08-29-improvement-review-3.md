# Improvement Review — 2026-08-29 (review 43)

**Agent:** improvement-agent (tier `strategic`)
**Status:** **APPLIED 2026-08-30** — 7 of 8 changes on disk; change 3 withheld by reviewer
decision (they chose a third option, outside the two offered). See §10.
**Findings processed:** 12 `NEW` → 5 clusters
**Trigger:** unread `blocker` ([`IMP-0493`](../../logs/improvement-log.jsonl)) **and** the ≥10 batch trigger, both firing on the same run of [`verify-improvement-log.py --check`](../../scripts/verify-improvement-log.py#L1113)
**Gate:** `APPROVE IMPROVEMENTS`

---

## Summary

**Eleven unread entries, and the one `blocker` among them needs no rule change — its artefact defect was fixed by a parallel dispatch while this review was being drafted, and the HARD gate that caught it now runs clean.** Eight changes are proposed across five clusters: zero new constraint rows, one constraint amendment, three gate edits, two skill edits, one knowledge line, one agent-file generalisation and one template column. A twelfth finding, [`IMP-0495`](../../logs/improvement-log.jsonl), was logged by this review and is deferred.

**One thing the reviewer needs before the queued build-agent re-dispatch:** [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) will **still be red** when this gate opens, and that is by design — see §7. The remedy is the keyword, not another session.

**Scope excluded, per the no-silent-caps rule.** 89 entries sit at `reviewer-deferred` and were not read; 0 sat at `awaiting-approval`; 0 at `already-fixed`; 0 at `approved-not-applied`. `APPLIED` and `REJECTED` entries were not read — the digest already carries their lessons.

---

## 1. Regression check — did reviews 41 and 42's changes work?

Ten changes across the two reviews applied earlier today. Every executable claim below is a **run**, not a re-read, per [`improvement-agent.md` L150](../../agents/improvement-agent.md#L150).

| Prior change | From | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [`WORKFLOW.md` L110](../../agents/WORKFLOW.md#L110) fourth-case evidence vocabulary | r41 ch1 | `dispatched-agent-stalls-silently` | NO | Working — leave alone. Prose change, so a recurrence escalates to a gate |
| [`pipeline-agent.md` L191](../../agents/pipeline-agent.md#L191) per-operation `WRITE BEGUN:` | r41 ch2 | `learning-substrate-destroyed` | NO — but **untested**: no pipeline-agent dispatch has run since | Unproven, not working. `IMP-0484` is correctly still open on exactly this |
| [`verify-provisioning-report.py`](../../scripts/verify-provisioning-report.py#L96) learns `WRITE BEGUN:` | r41 ch3 | `learning-substrate-destroyed` | NO | **Working.** Re-run: `PASS — 11 entries judged (1 with a provisioning write, all carrying a preflight result); 21 predate the convention` |
| [`C-TECH-065`](../../constraints/technology/technology-constraints.md#L135) fourth rung | r41 ch4 | `learning-substrate-destroyed` | NO | Working — verified by ch3's command, exit 0 |
| [`verify-code-app-data-sources.py`](../../scripts/verify-code-app-data-sources.py#L113) reads the shared register | r42 ch1 | `gate-cannot-fail` | NO | **Working.** Re-run: `OK — 7 registration(s), 7 Dataverse source(s) declared`, exit 0, no `--allow` |
| [`build.yml` L1293](../../config/revitalise-grant-automation-build.yml#L1293) + [`gate-baselines.json`](../../config/gate-baselines.json) | r42 ch2 | `gate-cannot-fail` | **YES — [`IMP-0492`](../../logs/improvement-log.jsonl)** | **Incomplete at the time; now correct.** See below |
| [`C-TECH-053`](../../constraints/technology/technology-constraints.md#L108) deploy-side rung | r42 ch3 | `v3-does-not-imply-v4` | NO | Working — leave alone |
| [`verify-dev-summary-artefacts-committed.py`](../../scripts/verify-dev-summary-artefacts-committed.py#L1) (SOFT) | r42 ch4 | `no-assertion-on-shipped-content` | NO | **Working, and it is finding things.** Re-run: `12 finding(s) — 7 documents, 219 distinct cited paths, 228 judged`, exit 0 under `--warn-only` |
| [`how-to-verify-a-platform-contract.md` L392](../../skills/how-to-verify-a-platform-contract.md#L392) V-level rule | r42 ch5 | `no-assertion-on-shipped-content` | NO | Working — leave alone |
| [`improvement-agent.md` L125](../../agents/improvement-agent.md#L125) stamp `reviewed_in` at draft time | r42 ch6 | `learning-substrate-destroyed` | NO | **Working — and this review is its first test.** See below |

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** none. r42 ch2's recurrence ([`IMP-0492`](../../logs/improvement-log.jsonl)) is a recurrence against the review's *change table*, not against a gate that failed to fire.

### r42 ch2 — the recurrence, and why it is already closed on disk

`IMP-0492` records that retiring the `--allow` flag touched the code and the one call site and **not** the config comment eleven lines above it, which still told the next agent to use the retired flag. Checked live: [`build.yml` L1306–L1313](../../config/revitalise-grant-automation-build.yml#L1306) now reads *"do not reach for an inline flag: `--allow` was RETIRED on 2026-08-29 and is now a usage error"* and points at the register instead. **The instance is fixed; the generalisation is not**, and that is what change 8 proposes.

### r42 ch6 — the stamp rule, tested here for the first time

Review 42 moved `reviewed_in` from approval time to draft time. Review 41 was written in the same hour and predates the change, which is why [`IMP-0489`](../../logs/improvement-log.jsonl) still carries no stamp today. **This review is the first to run under the new rule, and it stamps all twelve entries as part of writing this draft** — status stays `NEW`, nothing else moves. That is the change's regression test, and it passes.

Reading review 41's residual warning also produced a new finding: the warning names review 41 as having *cited* `IMP-0489`, and review 41 names it once, as an id-allocation watermark. That is [`IMP-0495`](../../logs/improvement-log.jsonl), §5.

---

## 2. Clusters and promotion decisions

```
CLUSTER: gate-invocation-omits-required-arg  (x2: IMP-0479, IMP-0494)
Altitude:   CLASS — second instance of ONE property, and IMP-0494 says so itself
Ladder row: "second instance of the same class_instance_of → generalise"
Becomes:    agents/build-agent.md's On Activation section names TWO placeholders where it
            had one: <build-config-slug> (the config file actually named in the dispatch)
            and <feature-slug> (the feature the dispatch is for), and states once that
            they differ whenever a build config is shared across features
Retires:    nothing — no instance gate existed; both instances were agent-file ambiguity
Cites:      IMP-0479, IMP-0494, IMP-0470
Residual:   NOT mechanically enforced. Nothing machine-readable carries "the feature this
            dispatch is for", so no gate can compare the resolved artifact directory
            against it. A third instance justifies giving the manifest a declared
            build_config field and having verify-build-manifest-note.py read THAT instead
            of deriving the path from a slug — which is the real general fix, and it is
            too large to bolt onto a second instance.
```

```
CLUSTER: approved-document-internally-inconsistent  (x3: IMP-0481, IMP-0482, IMP-0493)
Altitude:   SPLIT — one class name, three different mechanisms, and only two need a change
Ladder row: "a tool could catch it mechanically" (IMP-0481) · "an agent had the
            information and still did the wrong thing" (IMP-0482) · "nothing" (IMP-0493)
Becomes:    IMP-0481 → verify-tad-coverage.py compares the two status populations by
            MEMBERSHIP, both directions, suppressible through the existing register
            IMP-0482 → skills/how-to-report-to-the-reviewer.md's conclusion-first rule
            binds TABLE CELLS, not only sections
            IMP-0493 → nothing. The HARD gate caught it, correctly, and it is fixed
Retires:    nothing
Cites:      IMP-0481, IMP-0482, IMP-0493, IMP-0422, IMP-0428
Residual:   IMP-0482 stays PROSE and will stay prose. The measurable form of "a cell's
            opening verdict contradicts its closing verdict" is phrase-based, and this
            repository has measured that instrument five times at 48%–100% false
            (IMP-0422), with IMP-0428 the case of a wired gate going red on the erratum
            written to satisfy it. A corrected cell contains strictly MORE of the
            superseded wording than an uncorrected one, so the polarity inverts. No gate.
```

```
CLUSTER: gate-reassures-wrongly  (x2: IMP-0478, IMP-0483)
Altitude:   IMP-0478 CLOSED — already on disk. IMP-0483 INSTANCE → mechanical
Ladder row: "a tool could catch it mechanically"
Becomes:    IMP-0478 → nothing; review 40 change 12 shipped it, verified at
            verify-improvement-log.py L916
            IMP-0483 → verify-flow-definition-language.py's check-7 exception records the
            hidden-descendant count it was GRANTED against, and fails on growth past a
            margin, so a suppression cannot silently widen
Retires:    nothing
Cites:      IMP-0478, IMP-0483, IMP-0477
Residual:   Change 3 turns the build RED on one existing exception unless the reviewer
            re-adjudicates it. That is an open decision and it is put in §5, not decided
            here. The margin is a number somebody has to choose, and a margin chosen to
            keep today's tree green is a waiver with arithmetic on it.
```

```
CLUSTER: declared-policy-not-mechanically-enforced + platform-state-divergence
         (x2: IMP-0480, IMP-0489)
Altitude:   Both INSTANCE, both answered by WIDENING an existing rule rather than adding one
Ladder row: "one instance, the cause is general and a human needs to know it"
Becomes:    IMP-0480 → C-TECH-064 AMENDED: a rev_setting row carrying a DISCLOSURE
            CONTROL is environment state for this rule's purposes, and is read back live
            before any report states the control is in force
            IMP-0489 → one line in knowledge/technology/code-apps.md
Retires:    nothing
Cites:      IMP-0480, IMP-0489, IMP-0082, IMP-0490
Residual:   C-TECH-064's Verify By is a live query and no agent session in this repository
            can authenticate to DEV. The amendment makes the obligation explicit and names
            who discharges it; it does not make it runnable from here. IMP-0480 stays OPEN
            with a revisit_when for exactly that reason (§5).
```

```
CLUSTER: the improvement-review procedure's own gaps  (x2: IMP-0491, IMP-0492)
Altitude:   Both INSTANCE, both an incomplete INSTRUCTION rather than a wrong one
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    IMP-0491 → templates/improvement-review-template.md gains a Wiring column,
            required on every row of type `script`
            IMP-0492 → skills/how-to-promote-a-finding.md's retirement rule gains a
            repo-wide-grep step, generalising the assumption-closure rule that already
            exists in how-to-verify-a-platform-contract.md to capability retirement
Retires:    nothing
Cites:      IMP-0491, IMP-0492, IMP-0380, IMP-0374
Residual:   Neither is mechanically enforced. verify-review-document.py could read the
            Wiring column, but a review parked at its gate has proposed no wiring yet, so
            the check would need to distinguish a draft from an applied document — one
            instance does not justify building that.
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | [`build-agent.md` L38](../../agents/build-agent.md#L38) and [L46](../../agents/build-agent.md#L46) | Replace the single bare `<slug>` with **`<build-config-slug>`** (step 1, the config file named in the dispatch) and **`<feature-slug>`** (step 3, `resolve-artifact-dir.py --feature`), and state once that they differ whenever a config is shared. The [manifest-note command at L320](../../agents/build-agent.md#L320) gains the `--build-config` flag in the same breath | IMP-0479, IMP-0494, IMP-0470 | N/A — instruction change | N/A — no new script |
| 2 | script | [`verify-tad-coverage.py` L819](../../scripts/verify-tad-coverage.py#L819) | `check_response_contract` compares the status populations by **membership**, both directions reported separately: a **flow-produced** value absent from the TAD enumeration is a contract breach; an **enumerated** value nothing produces is a dead diagnostic. Suppressible only through [`gate-baselines.json`](../../config/gate-baselines.json), which this script already loads. **Measured: 2 findings, 1 document, 2 true positives, 0 false — see §6** | IMP-0481 | YES — `--selftest` plus the corpus run in §6 | Already wired HARD at [`build.yml` L644](../../config/revitalise-grant-automation-build.yml#L644); no new step |
| 3 | script | [`verify-flow-definition-language.py` L441](../../scripts/verify-flow-definition-language.py#L441) | Each `_CHECK7_EXCEPTIONS` record gains `hides_at_declaration`, and the [L592 block](../../scripts/verify-flow-definition-language.py#L592) **fails** when the live count exceeds it by more than a declared margin, instead of printing a sentence only a reader who knows the old number can act on | IMP-0483, IMP-0477 | YES — `--selftest` plus the corpus run in §6 | Already wired HARD at [`build.yml` L1005](../../config/revitalise-grant-automation-build.yml#L1005); no new step. **Reviewer decision required — §5** |
| 4 | skill | [`how-to-report-to-the-reviewer.md` L116](../../skills/how-to-report-to-the-reviewer.md#L116) | The conclusion-first rule binds **table cells**: the retain-the-superseded-text convention is for narrative, and inside a matrix cell the current verdict is rewritten in place with the history moved after it. A reader scans leading verdicts and stops | IMP-0482 | N/A — instruction change; deliberately not a gate, see cluster 2's Residual | N/A |
| 5 | constraint-amendment | [`C-TECH-064`](../../constraints/technology/technology-constraints.md#L134) | Name `rev_setting` rows carrying a **disclosure control** — a threshold whose absence changes what is published — inside this row's live-verification scope. A settings-file entry plus a Pester assertion is source-side evidence and the flow's fail-safe is silent, so an unseeded threshold and a genuinely small population render identically | IMP-0480, IMP-0082 | Partly — the query is mechanical, the environment is not reachable from here | N/A |
| 6 | knowledge | [`code-apps.md` L374](../../knowledge/technology/code-apps.md#L374) | Before reusing a documented `-c <connection-id>`, confirm it live with `pa connection list -e <env-id> --json`. A maker's OAuth connection is deleted and recreated without notice and no document here self-updates; two ids this repository records across four documents are both gone | IMP-0489 | N/A — knowledge line | N/A |
| 7 | template | [`improvement-review-template.md` L53](../../templates/improvement-review-template.md#L53) | A **Wiring** column on the Proposed changes table, required for every row of type `script`: `HARD` \| `SOFT (--warn-only)` \| `SUITE_GATE_EXEMPT + reason` \| `already wired`. A gate row with it blank is an incomplete proposal, because [`verify-build-config.py`](../../scripts/verify-build-config.py)'s suite-gate rung makes an unwired `verify-*.py` a red preflight | IMP-0491 | N/A — template change. This table dogfoods it | N/A |
| 8 | skill | [`how-to-promote-a-finding.md` L96](../../skills/how-to-promote-a-finding.md#L96) | The retirement rule gains a grep step: retiring a flag, a script mode or a convention requires a repo-wide search for its literal token, and **every instruction to use it** is rewritten in the same change — not only the implementation and its call sites | IMP-0492, IMP-0380, IMP-0374 | Partly — the grep is a command; whether every hit was rewritten is a judgement | N/A |

**Constraint budget:** **0 of 3 used.** One amendment to an existing row; no new rows.

---

## 4. Retirements

> Retirement check performed: **80 live constraint rows and 10 already-retired rows reviewed** (derived, not typed: `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 80; `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10). **None is currently redundant.**

The nearest candidate was examined and rejected. [`C-TECH-064`](../../constraints/technology/technology-constraints.md#L134) and [`C-TECH-065`](../../constraints/technology/technology-constraints.md#L135) both govern evidence about a live environment, and change 5 widens the first. They do not overlap: `C-TECH-064` is about **verifying state after a deploy**, `C-TECH-065` about **recording a write as it happens**. Merging them would produce one row nobody could hold in mind, which is the outcome the retirement rule exists to prevent.

Change 3 is a retirement-adjacent act and is not one: it does not retire the three check-7 exceptions, it makes them re-adjudicable. Their `expires: 2026-09-30` is untouched.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0495

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| [`IMP-0495`](../../logs/improvement-log.jsonl) | `gate-fires-on-nothing` | One instance, and it is a **WARNING** that resolves itself the moment this review stamps `IMP-0489`. [`verify-improvement-log.py` L1469](../../scripts/verify-improvement-log.py#L1469) records four prior narrowings of this exact predicate and argues against adding a fifth exemption shape; dropping the `elsewhere` half is the right fix and it risks losing `IMP-0154`'s original coverage, which needs a corpus measurement across all **48** review documents to settle | a second review document quotes a finding id as a value and draws the same false warning — or any review measures the processing-position-only predicate across the corpus and shows no coverage loss |

**The warning that produced this finding is already gone,** and that is the point: stamping `IMP-0489` with *this* review — the one that actually processed it — cleared it. The mechanism that mis-fired is still there and will mis-fire on the next review that quotes an id as a number.

### The eleven that WERE processed, and their state on approval

**Nine take a change.** Two take none, and both are closed rather than deferred:

| Finding | Disposition on approval | Why |
|---|---|---|
| [`IMP-0478`](../../logs/improvement-log.jsonl) | **`APPLIED`** — no change by this review | Its own `proposed_change` says *"APPLIED by improvement review 40 change 12"*, and that is true on disk: `contests_clause` is validated at [`verify-improvement-log.py` L916](../../scripts/verify-improvement-log.py#L916), and the log carries exactly 1 `contests` edge. `observable_at` is V1, so re-reading the tree is the reproduction. This is bookkeeping that review 40 did not finish (`IMP-0033`) |
| [`IMP-0493`](../../logs/improvement-log.jsonl) | **`APPLIED`** — no change by this review | See immediately below |

### `IMP-0493` — the blocker, and the artefact defect checked live rather than assumed

**The defect it names is GONE, and I watched it go.** The dispatch that routed this review warned that a parallel development-agent dispatch was fixing [`trustee-portal-visual-refresh-dev-summary.md` L1884](../../docs/development/trustee-portal-visual-refresh-dev-summary.md#L1884) concurrently, and that the state had to be checked rather than assumed in either direction. Both readings were true, ninety seconds apart:

| When | What line 1884's `A-RES-1` row said | `verify-assumption-register.py` |
|---|---|---|
| First read, this session | `\| OPEN \|` | not yet run |
| After the file's mtime moved to **21:36:29** | `\| **CLOSED (E1)** \|` | **exit 0** — `PASS — 65 row(s) across 17 register(s) in 5 document(s); 33 still open, and none of them is contradicted by its own document`, plus 26 NOTEs |

[`routing.log` L397](../../logs/routing.log#L397) independently records the same event at 21:37 — *"A-RES-1 register row corrected at dev-summary.md:1884 (OPEN -> CLOSED (E1)), single-cell diff confirmed"* — so the observation is corroborated by the dispatch that made it, not only by this session's two greps.

So the row now agrees with the same document's L952, L967, L1959 and L2689, the HARD build gate at [`build.yml` L452](../../config/revitalise-grant-automation-build.yml#L452) is green, and `IMP-0493`'s `proposed_change.type` is `none` — it proposed a document edit by development-agent and nothing else. There is nothing for `APPROVE IMPROVEMENTS` to approve about it, which is why it closes rather than parking.

**`observable_at` is V1**, so [`how-to-promote-a-finding.md` L165](../../skills/how-to-promote-a-finding.md#L165)'s `reobserved` requirement does not bind — but the observation was made anyway and is recorded on the entry, because the closure evidence here is an independently-run HARD gate over a file another dispatch edited, not a sentence this review wrote (`IMP-0208`, `IMP-0224`).

### Reported, not fixed — one delivery defect and two documents this review does not own

Three things measured during this review belong to delivery agents, not to the rules, and are named here rather than silently fixed (`C-COM-002`):

- **`RoundStatistics%` settings rows are absent from DEV** (`IMP-0480`). Neither the `k = 5` disclosure threshold nor the freshness bound exists, so the flow's fail-safe yields `k = 999999999` and withholds every money measure while reporting `status: "ok"`. `observable_at` **V5**. Owner: pipeline-agent's `post_deploy` seeding step (TAD 12.3). **`IMP-0480` therefore stays OPEN on approval** with a `revisit_when` naming the live query — closing it on a constraint amendment would be `IMP-0208` again.
- **The TAD's status enumeration is wrong in two directions** (`IMP-0481`, measured in §6). `error` is emitted by the flow and absent from the enumeration; `threshold-unset` is enumerated and emitted by nothing. Both are one-line edits to [`trustee-portal-visual-refresh-architecture.md` L1271](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L1271) and both belong to architect-agent. Change 2 registers them with an owner and an expiry rather than failing the build over them.
- **Appendix A's FR-059 and FR-060 rows still lead with a superseded verdict** (`IMP-0482`). Verified live: [L3845](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3845) opens *"**PARTIAL, and the split is exact.**"* and states `averageAmountRequested` is *"**NOT delivered**"*, then carries *"**UPDATE 2026-08-28 … DELIVERED IN FULL**"* roughly 1,400 characters later in the same cell. [L3846](../../docs/architecture/trustee-portal-visual-refresh-architecture.md#L3846) is the same shape. Change 4 fixes the convention; the two rows are architect-agent's to rewrite.

---

## 6. Measurement — the corpus runs, and the one design the corpus changed

### Change 2 — the obvious design is 33% false, and the corpus is what says so

The natural reading of `IMP-0481` is *"compare the two sets"*. Run against the real tree, that produces **3 findings, 2 true, 1 false**:

| Value | Direction | Verdict |
|---|---|---|
| `error` | produced, not enumerated | **TRUE** — the flow emits it; the TAD enumeration omits it |
| `threshold-unset` | enumerated, not produced | **TRUE** — `IMP-0481`'s own finding, confirmed |
| `pending` | produced, not enumerated | **FALSE** — synthesised by [`roundStatistics.ts`](../../src/code-apps/trustee-review-portal/src/dataverse/roundStatistics.ts) while polling. It is an app-local state, never a value the flow's response body carries |

The two populations are not the same kind of thing. `status_values_produced` unions **flow literals** with **app-assigned statuses**, and the TAD enumeration describes only the **response body**. So the corrected design asks the undeclared-producer question of the **flow set alone** and the dead-diagnostic question of the **union** — and `pending` leaves by construction rather than by exemption:

**Re-measured: 2 findings, 1 document, 2 true positives, 0 false.**

This is the fourth time in this repository that running a gate against the corpus changed its design rather than confirming it (`IMP-0319`, `IMP-0422`, review 29 cluster C, and this). A `--selftest` written by the same author in the same sitting could not have found it.

### Change 2 — and why it does not turn the build red

Both true positives are pre-existing documentation debt in a document this review does not own, and [`build.yml` L644](../../config/revitalise-grant-automation-build.yml#L644) runs this gate HARD with no `--warn-only`. Wiring the check without a suppression path is `hard-gate-red-on-pre-existing-debt` (`IMP-0439`, `IMP-0477`) for the third time. [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py) **already loads** [`gate_baseline`](../../scripts/lib/gate_baseline.py), so both instances go into [`gate-baselines.json`](../../config/gate-baselines.json) with `owner: architect-agent`, a clearing action naming the one-line TAD edit, and a dated `expires`. The register suppresses the FAIL and never the report, and an expired entry fails.

### Change 3 — the numbers, and the decision they force

Run live against `src/solutions/RevitaliseGrantAutomation`, all three check-7 exceptions are reported and suppressed, exit 0:

| Flow | Containers | Hidden descendants, **today** |
|---|---|---|
| `REVIntakeWordPressToDataverse` / `Create_the_application` | 2 | **6** |
| `REVPortalRoundStatistics` / `Compute_statistics` | 1 | **167** |
| `REVScoringCalculateAndFlag` / `Score_and_flag` | 3 | **12** |

The middle row is the finding. The Dev Summary records the same exception at *"84 more actions than when it was declared"*, which puts its declared blast radius at **83** — it has more than doubled, and every one of the ~140 actions Revision 6 added is inside the hidden subtree, including all thirteen `Compose_*_sum` actions carrying `A-FLOW-11`, the feature's one unverified platform contract.

**This is the open decision, and it is the reviewer's, not mine.** Recording `hides_at_declaration: 83` and failing on growth makes the build **red today**. Recording `167` makes it green and launders the growth into the baseline. The two honest options:

- **(a) Re-declare.** Set `hides_at_declaration: 167`, `declared: 2026-08-29`, and shorten `expires`. The growth is acknowledged and re-owned by a person on a date; the build stays green; the mechanism is live from the next action added.
- **(b) Hold the line.** Set `hides_at_declaration: 83`. The build goes red until `result()` descends into `Switch_on_open_round_count`, which is the exception's own stated clearing action.

**I have not chosen.** Per [`improvement-agent.md` L77](../../agents/improvement-agent.md#L77), an open decision that changes what gets built blocks the part that depends on it: the *mechanism* (the field, the margin comparison, the failure message) is proposed and the *values* are not. Say (a) or (b) with the keyword and change 3 applies in full; say nothing and change 3 is withheld and reported as withheld.

### Change 1 — verified by execution, not by reading

Both instances re-checked against the current agent file rather than trusted from their findings, per [`improvement-agent.md` L150](../../agents/improvement-agent.md#L150):

- [`build-agent.md` L46](../../agents/build-agent.md#L46) reads `resolve-artifact-dir.py --feature <slug>`, and [L38](../../agents/build-agent.md#L38) reads `config/<slug>-build.yml`. **One placeholder, two meanings** — `IMP-0494` confirmed.
- [`build-agent.md` L320](../../agents/build-agent.md#L320) reads `verify-build-manifest-note.py "$ARTIFACT_DIR"` with no flag. `--help` confirms `--build-config BUILD_CONFIG` exists — `IMP-0479` confirmed, and the flag it names is real.

### The interval, again

[`IMP-0405`](../../logs/improvement-log.jsonl) says a `deferred_reason`'s factual clauses perish between a gate opening and a keyword arriving. This review's own drafting window contained a live example: `IMP-0493`'s artefact defect went from present to fixed **inside this session**, at 21:36:29, between one grep and the next. Every factual clause in §5's dispositions is re-verified at apply time before it is written, and change 3's two numbers are re-run.

---

## 7. `C-TECH-061` after this gate opens — and what the queued build will see

**It stays RED, and the remedy is the keyword.** This matters because a `build-agent` re-dispatch is queued behind this review, and [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L141) is **step 3 of 74** — it halts the build in about a second, which is exactly what `IMP-0285` moved it there to do.

Stamping `reviewed_in` moves all twelve entries from `unread` to `awaiting-approval`. Both of [`verify-improvement-log.py`](../../scripts/verify-improvement-log.py)'s failing rungs count that state:

| Rung | Before this review | After the stamp | After `APPROVE IMPROVEMENTS` |
|---|---|---|---|
| [Blocker at `unread`](../../scripts/verify-improvement-log.py#L1064) | **FAIL** — `IMP-0493` | clears | clear |
| [Blocker at `awaiting-approval`](../../scripts/verify-improvement-log.py#L1081) | clear | **FAIL** — `IMP-0493` | clears — `IMP-0493` closes `APPLIED` |
| [Batch trigger, `unread` + `awaiting` ≥ 10](../../scripts/verify-improvement-log.py#L1113) | **FAIL** — 11 | **FAIL** — 12 | clears — 1 remains (`IMP-0495`, `reviewer-deferred`) |

The middle row is deliberate. [L1092](../../scripts/verify-improvement-log.py#L1092) says it plainly: *"This stays a FAIL because a stalled review must not go quiet — but the remedy is a keyword, not a session (`IMP-0154`)."*

**What this review did NOT do, and why.** It would have been one edit to write a `deferred_reason` onto all twelve and take the queue green without the gate. That is the shape [`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) itself rules out — *"a recorded `deferred_reason` is a reviewer's decision"* — and nine of the twelve carry a real proposed change, so deferring them would be recording a decision nobody made in order to unblock a build. [`improvement-agent.md` L132](../../agents/improvement-agent.md#L132) is explicit that at draft time `status` stays `NEW`.

**On approval the queue goes to 1 pending, and `C-TECH-061` goes green** — 12 entries close or defer with a reason, and `IMP-0495` alone remains at `reviewer-deferred`, which the batch trigger does not count.

---

## 8. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 491 | **492** |
| Distinct lessons | 490 | **491** (1 `REJECTED` entry excluded) |
| Recurring classes (x≥2) | 39 | **39** — `IMP-0495`'s class `gate-fires-on-nothing` goes x7 → x8; no new class |
| Digest lines | 585 | **585** — the new lesson lands in a section already at its 20-line cap, so it is indexed by class rather than rendered |

**Already regenerated, and this is not a deviation.** `IMP-0495` is a finding appended to the log, and `CLAUDE.md`'s learning rule requires validator-then-generator at append time — not at approval. So `python3 scripts/generate-known-failure-modes.py` has run and `--check` reports *"logs/known-failure-modes.md is current (492 entries)"*. What is **not** on disk is every change in §3; the digest reflects the log, and the log legitimately carries one new finding.

**Script count check.** `ls scripts/verify-*.py | wc -l` → **52**, unchanged: this review adds no new script and edits two existing ones. The figure is registered as `improvement-agent-verify-script-count` in [`derived-counts-registry.json`](../../scripts/derived-counts-registry.json) and needs no update.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-29-improvement-review-3.md

Findings processed: 12 NEW  →  5 clusters
Regression check:   10 prior changes audited, 1 class recurred
Proposed:           0 constraints (cap 3), 1 constraint amendment, 2 gates/scripts,
                    3 skill/knowledge edits, 1 agent-file edits, 1 template edits,
                    0 retirements
Altitude calls:     1 generalised from instance to class, 2 left as notes
Digest:             will regenerate — 491 lessons, 39 recurring classes

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Change 3 needs a value with the keyword: `(a)` re-declare at 167, or `(b)` hold at 83 and accept a red build.** Without one, change 3 is withheld and reported as withheld.

---

## 10. Applied

**APPLIED 2026-08-30. Seven of the eight proposed changes are on disk; change 3 was WITHHELD by
reviewer decision.** `verify-improvement-log.py --check` exits **0** — 0 unread, 0
awaiting-approval, 92 reviewer-deferred — so both triggers are clear and
[`C-TECH-061`](../../constraints/technology/technology-constraints.md#L131) is green.

| # | Change | Applied | Entries closed |
|---|---|---|---|
| 1 | [`build-agent.md`](../../agents/build-agent.md#L38) — `<build-config-slug>` / `<feature-slug>` split, plus `--build-config` on the manifest-note command | YES | `IMP-0479`, `IMP-0494` → APPLIED |
| 2 | [`verify-tad-coverage.py`](../../scripts/verify-tad-coverage.py#L739) — assertion (e) compares by membership, both directions | YES | `IMP-0481` → APPLIED |
| 3 | `verify-flow-definition-language.py` — `hides_at_declaration` + growth margin | **WITHHELD** | `IMP-0483` → `reviewer-deferred` |
| 4 | [`how-to-report-to-the-reviewer.md`](../../skills/how-to-report-to-the-reviewer.md#L113) — conclusion-first binds table cells | YES | `IMP-0482` → APPLIED |
| 5 | [`C-TECH-064`](../../constraints/technology/technology-constraints.md#L134) — disclosure controls are environment state | YES | `IMP-0480` stays OPEN (V5) |
| 6 | [`code-apps.md`](../../knowledge/technology/code-apps.md#L366) — confirm a connection id live before reusing it | YES | `IMP-0489` → APPLIED |
| 7 | [`improvement-review-template.md`](../../templates/improvement-review-template.md#L52) — `Wiring` column | YES | `IMP-0491` → APPLIED |
| 8 | [`how-to-promote-a-finding.md`](../../skills/how-to-promote-a-finding.md#L88) — retirement greps for instructions, not just call sites | YES | `IMP-0492` → APPLIED |
| — | no change (bookkeeping review 40 left open) | — | `IMP-0478` → APPLIED |
| — | no change (artefact fixed by another dispatch) | — | `IMP-0493` → APPLIED |
| — | deferred as drafted | — | `IMP-0495` → `reviewer-deferred` |

### Change 3 was withheld, and the reason is a THIRD option — not an unanswered question

§6 offered the reviewer two values: **(a)** re-declare at `hides_at_declaration: 167`, or **(b)**
hold at `83` and accept a red build. **The reviewer rejected both** and chose neither-of-the-above:
fix the failure-diagnosis gap for real and retire the exception outright
([`routing.log` 2026-08-30 10:13](../../logs/routing.log)). Change 3 is therefore **superseded, not
unanswered** — applying either offered value would have written a number into the tree that the
accepted plan then deleted. Nothing in `verify-flow-definition-language.py` was touched by this
review.

**That separate dispatch landed while this one was applying, and its result is measured, not
assumed.** The file's mtime moved to `2026-08-30 10:33:35` mid-session; the
`REVPortalRoundStatistics` / `Compute_statistics` key is gone from `_CHECK7_EXCEPTIONS`; and a live
run over `src/solutions/RevitaliseGrantAutomation` exits **0** reporting **two** exceptions where
there were three — `REVIntakeWordPressToDataverse` at 6 hidden descendants and
`REVScoringCalculateAndFlag` at 12 — cleared on the shape's own merits rather than by suppression.

**`IMP-0483`'s class half is still open, and it is deferred rather than closed for that reason.**
Both surviving exceptions still print *"if this number has grown since the exception was declared,
the fail-loud claim resting on it is weaker than it was"* — the exact sentence the finding was
logged about — and neither declares a blast radius or fails on growth. One instance is fixed; the
mechanism is neither built nor rejected.

### Three deviations from the approved wording, all compelled by measurement

Recorded here, in each entry's `applied_by`, and in the gate output, per the NARROW-AND-REPORT rule.

1. **Change 1's stated rationale was wrong and was corrected by running the script.** `IMP-0479`
   said the missing flag makes the gate judge the note against an empty SOFT-step list.
   [`verify-build-manifest-note.py` L293](../../scripts/verify-build-manifest-note.py#L293) instead
   emits `NO BUILD CONFIG` and returns, and its `--selftest` carries the fixture *"a manifest naming
   a feature with no build config fails rather than reporting OK → exit 1"*. The failure is **loud**.
   The instruction records the measured behaviour, not the finding's claim — the `IMP-0426` shape,
   caught by executing rather than re-reading.
2. **Change 2's (e2) is guarded on a non-empty flow set, and two selftest fixtures were wrong.**
   Unguarded, (e2) reports *every* enumerated value the moment the `Workflows/` glob comes back
   empty — the structural floor read in the other direction. Separately, the shared fixture
   enumerated four statuses its flow never composed, and
   `status-value-the-APP-synthesises-and-the-contract-does-not-enumerate` was **passing for the
   wrong reason** ((e2) firing on `ok` under `flow=None`); under change 2 an app-synthesised status
   is legitimately not required in the enumeration, so that case is now a VALID control. A
   fixture green for a reason other than the one it names is the `IMP-0319` shape.
3. **Change 2 also makes baselined findings visible, because they were not.**
   [`gate-baselines.json`](../../config/gate-baselines.json) promises a suppression hides the FAIL
   and never the report; measured, this gate was dropping suppressed statuses silently. They now
   print by name with owner, expiry and clearing action. Relatedly the dead `status:pending` entry
   was **removed** rather than left: `pending` now leaves by construction so its key can never be
   claimed, and an unclaimable entry is not harmless — `load_baselines` fails on any expired entry
   whether or not it was ever claimed, verified by running it against `2026-10-01`.

### Measurement — change 2 against the real corpus

With the baseline disabled: **2 findings, 1 document, 2 true positives, 0 false.**

| Value | Direction | Verdict |
|---|---|---|
| `error` | composed by the flow, not enumerated | **TRUE** — already covered by review 38's `status:error` entry |
| `threshold-unset` | enumerated, produced by nothing | **TRUE** — new `status-unproduced:threshold-unset` entry, owner `architect-agent`, expires 2026-09-30 |
| `pending` | app-synthesised | **removed by construction** — not a finding under the split design |

Selftest: **33 cases green**, including a new single-caused negative fixture for (e2).
Corpus run: **exit 0**, both findings reported and suppressed.
[`verify-build-config.py`](../../scripts/verify-build-config.py) preflight: **OK**.
[`verify-constraint-verifiers.py`](../../scripts/verify-constraint-verifiers.py): **PASS**, 92 paths
across 80 rows resolve. Constraint rows: **80 live / 10 retired**, unchanged — change 5 is an
amendment. `ls scripts/verify-*.py | wc -l` → **52**, unchanged, so
[`derived-counts-registry.json`](../../scripts/derived-counts-registry.json) needs no edit.
Digest regenerated: **492 entries, 491 lessons, 585 lines** — exactly as §8 predicted.
