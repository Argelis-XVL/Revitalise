# Improvement Review — 2026-09-07 (3)

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 1 cluster
**Trigger:** blocker escalation — [IMP-0649](../../logs/improvement-log.jsonl#L646), `blocker`/`unread`, plus [IMP-0637](../../logs/improvement-log.jsonl#L634), which the queue gate names as corrected-but-unprocessed
**WBS:** 3.2, 3.3, 3.4
**Gate:** `APPROVE IMPROVEMENTS`

---

## 0. The one thing to read first

**The platform fact is confirmed and the fix is already half-built — but the finding's own wording over-states it, and the reliable route is wired for DEV only, so the next deploy to Test or Production will hit this same wall with nothing to catch it.**

[IMP-0649](../../logs/improvement-log.jsonl#L646) asks for a knowledge entry saying unmanaged solution import *"cannot reliably ADD a new FieldPermission entry to an EXISTING Field Security Profile in this org, regardless of column age."* The first half is proven. **The word "cannot" is not:** six prior commits added 36 column permissions to an already-existing profile and every one of them imported successfully (§2). Written verbatim, that entry would tell every future agent to bypass solution import for all column-permission work, against 70 permissions that got there by solution import and are managed by it today.

**And there is already a constraint covering this** — [C-TECH-050](../../constraints/technology/technology-constraints.md#L92) — which says these components are created via the Web API *"on first creation in any environment."* The gap is the words "first creation." So this review proposes **no new constraint**; it widens the one that exists.

---

## 1. Regression check — did the last review's changes work?

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| [agents/development-agent.md#L402](../../agents/development-agent.md#L402) — *"Wiring ONE gate to a baseline does not cover the invariant — grep for the siblings"* | 2026-09-07 (review 2) | `hard-gate-has-no-scoped-override-path` | **NO** | **Working — and exercised by this review** |
| [`improvement-log-check`](../../config/revitalise-grant-automation-build.yml#L62) build step | 2026-08-24 (review 26) | `learning-substrate-destroyed` | **NO new instance** | The gate fired correctly again — it is what surfaced [IMP-0637](../../logs/improvement-log.jsonl#L634) |

**The change is on disk and all five entries in its class are closed.** The class has [six recorded members](../../logs/improvement-log.jsonl#L634) — `IMP-0638`, `IMP-0639`, `IMP-0641`, `IMP-0642`, `IMP-0643` — and every one reads `APPLIED`. No new instance has been appended since the keyword landed.

**More usefully than the absence of a recurrence: this review is the first dispatch to actually follow that rule, and it changed the proposal.** Change 3 below wires a new check into a gate that is already `HARD`. Following review 2's instruction — grep for the other encodings before reporting the wiring as handled — is what turned up the need for the two [config/gate-baselines.json](../../config/gate-baselines.json) entries that come with it. Without them the new check would open red on debt this review does not own and halt the next build at step 3. **That is the rule working on its first real outing, not a claim that prose fixes work.**

**Classes recurring after a prose fix:** none. **Classes recurring after a gate:** none. No `gate-cannot-fail` finding is logged; logging one would be false.

**Closure-level audit.** All three entries in scope are `observable_at: V3` — visible only against a live target import. §7 states plainly which of them this session can and cannot close, and none is proposed for closure on source state alone.

---

## 2. What was measured, because the finding's own root cause does not survive it

The finding's factual claims all check out against the log, and I read them there rather than taking them from the finding's prose.

| Claim | Where I checked it | Result |
|---|---|---|
| The first import failed on Field Security Profile with a null-reference | [logs/pipeline.log#L155](../../logs/pipeline.log#L155) | **Confirmed** — async `f79e8d1b`, failed after 3m13s |
| The phase-2 retry failed **identically** with the column already live | [logs/pipeline.log#L160](../../logs/pipeline.log#L160) | **Confirmed** — async `de66128e`; the log itself records that this disproves the column-age theory |
| The Web API write is what fixed it | [logs/pipeline.log#L161](../../logs/pipeline.log#L161) | **Confirmed** — reviewer ran `ensure-schema.ps1 -Env dev` out of band |
| The re-import then succeeded, twice | [logs/pipeline.log#L162](../../logs/pipeline.log#L162) | **Confirmed** — async `3b1989aa` + idempotency re-run `24464caf`, both clean |
| That route exists in the provisioning script | [ensure-schema.ps1#L913](../../provisioning/dataverse/ensure-schema.ps1#L913) | **Confirmed** — a real `POST` to the `fieldpermissions` entity set |

**So [IMP-0637](../../logs/improvement-log.jsonl#L634)'s root cause is correctly disproved.** Its two-phase workaround was reasoned from a single failure with one variable held constant, and the second failure isolated that variable and killed it. That much of [IMP-0649](../../logs/improvement-log.jsonl#L646) stands exactly as written.

### But its replacement root cause over-generalises, and this is the load-bearing measurement

I checked every commit that has ever touched the profile file, and whether the profile it added permissions to already existed in the parent commit:

| Commit | Date | Profiles in parent | Permissions added | Imported? |
|---|---|---|---|---|
| `45dee74` | 2026-08-31 | 2 | +1 | **Yes** — [pipeline.log#L61](../../logs/pipeline.log#L61) records clean imports that day |
| `fc5fb1d` | 2026-08-24 | 1 | +16 | **Yes** |
| `80a8a79` | 2026-08-19 | 1 | +12 | **Yes** — and all 51 live permissions were then confirmed to match source exactly, both directions ([pipeline-config note](../../config/revitalise-grant-automation-pipeline.yml#L709)) |
| `35521fb` | 2026-08-17 | 1 | +3 | **Yes** |
| `1faf2b4` | 2026-08-16 | 1 | +4 | **Yes** |
| `4226d51` | 2026-08-14 | 1 | +1 | **Yes** |
| `26eae73` | 2026-08-14 | 0 | +34 | first creation — [C-TECH-050](../../constraints/technology/technology-constraints.md#L92)'s existing case |

**Six commits added 36 permissions to an already-existing profile and every one imported.** So the mechanism is **intermittent, not absolute**, and the honest statement of the platform fact is the one change 1 records. This is why the finding's `proposed_change` is not applied verbatim: "cannot" would have been written into a knowledge file as a platform law, and the next agent to read it would have routed 70 working permissions around solution import on the strength of two consecutive failures on one column.

### The mechanical candidate the earlier finding asked for — measured and dropped

[IMP-0637](../../logs/improvement-log.jsonl#L634)'s `proposed_change` asks for a source-diff gate flagging a change that introduces a new secured attribute together with its new permission. Run against the real corpus of 7 commits, the broad form fires on **7 of 7 with 1 true positive (14%)**; narrowed to "adds a permission to a profile that already existed", it fires on **6 of 7 with 1 true positive (17%)**.

**That is this repository's five-times-measured over-broad-gate shape arriving from a new direction, and a design measured like that is dropped rather than shipped with an exemption.** The reason is structural, not tunable: adding a column permission is the *normal* case in this solution and the failure is intermittent, so no property of the diff separates the seven commits. The measurement goes into change 1's text so the next agent does not re-propose it.

---

## 3. The cluster, and the altitude call

```
CLUSTER: platform-import-ordering-defect  (x3: IMP-0637, IMP-0647, IMP-0649)
Altitude:   LAW — a confirmed platform behaviour, reproduced twice with the candidate
            variable isolated on the second attempt. Skipping ahead of the
            "wait for a second instance" rule is justified under
            skills/how-to-promote-a-finding.md §4: severity is blocker and the
            mechanism is a platform law.
Ladder row: "A platform law, or a third instance" -> a constraint row
            AND "the cause is general and a human needs to know it" -> knowledge/
Becomes:    (1) knowledge/technology/dataverse.md — the platform fact, worded to the
                evidence, with the failure signature and the working route
            (2) C-TECH-050 AMENDED — "first creation" widened to any fieldpermissions
                row, including an addition to an already-existing profile
            (3) scripts/verify-pipeline-config.py — the amended Verify By, made
                mechanical: every environment receiving a solution that declares
                FieldPermissions must invoke the Web API provisioning path
Retires:    nothing in constraints/ — C-TECH-050 is widened, not replaced. Two LOG
            LESSONS are superseded and must be corrected in place, see §4
Cites:      IMP-0637, IMP-0647, IMP-0649
Residual:   The gate checks that the RELIABLE ROUTE IS WIRED. It cannot predict whether
            any given import will hit the defect — the measurement in §2 shows nothing
            in the source diff distinguishes the failing change from six successful
            ones. So a DEV import can still fail exactly as it did on 2026-09-07; what
            this closes is the case where it fails in TST or PRD with no route wired to
            recover. Naming that limit is the point: this is a mitigation, not a fix,
            and the platform defect itself is Microsoft's.
```

### Why no new constraint

[C-TECH-050](../../constraints/technology/technology-constraints.md#L92) already requires these components to be created via the Dataverse Web API and already names *"pipeline step order in `pipeline.yml`"* in its `Verify By`. Its scope is *"on first creation in any environment"* — and the whole content of this cluster is that the rule does not stop at first creation. Adding a second row saying almost the same thing about the same file is how a constraint set reaches 85 rows; the amendment is the correct altitude and it keeps the constraint budget at **0 of 3 used**.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | [`knowledge/technology/dataverse.md`](../../knowledge/technology/dataverse.md#L99) | Add a bullet to the solution-import section recording the confirmed platform behaviour, its two-failure signature, the Web API route that works, and the two measurements that bound it — that 36 permissions imported fine across six commits, and that the source-diff gate is 14–17% precise | IMP-0637, IMP-0649 | NO — narrative platform contract | N/A |
| 2 | constraint-amendment | [`constraints/technology/technology-constraints.md`](../../constraints/technology/technology-constraints.md#L92) | Widen `C-TECH-050` from *"on first creation in any environment"* to any `fieldpermissions` row, including an addition to an already-existing profile; extend its `Verify By` to require the provisioning step in **every** environment section rather than only before the first import | IMP-0649 | YES — change 3 is its executable half | N/A |
| 3 | script | [`scripts/verify-pipeline-config.py`](../../scripts/verify-pipeline-config.py#L631) | New check: if the solution source declares any `<FieldPermission>`, every environment section must invoke `ensure-schema.ps1`. Ships with two [`config/gate-baselines.json`](../../config/gate-baselines.json) entries for the `tst_acc` and `prd` findings, owned and dated, so the already-`HARD` step does not go red on debt this review does not own | IMP-0649 | YES — `python3 scripts/verify-pipeline-config.py config/revitalise-grant-automation-pipeline.yml` | **already wired** — `pipeline-config-preflight`, HARD, at [config/revitalise-grant-automation-build.yml#L57](../../config/revitalise-grant-automation-build.yml#L57) |

**Constraint budget:** 0 of 3 used.

### Change 3's corpus measurement, and why it needs baselines

The corpus is the three declared environments. The check finds **2 findings, both true positives:**

| Environment | `ensure-schema.ps1` invocations | Verdict |
|---|---|---|
| [`dev`](../../config/revitalise-grant-automation-pipeline.yml#L576) | 7 — at [L538](../../config/revitalise-grant-automation-pipeline.yml#L538), [L622](../../config/revitalise-grant-automation-pipeline.yml#L622), [L634](../../config/revitalise-grant-automation-pipeline.yml#L634), [L663](../../config/revitalise-grant-automation-pipeline.yml#L663), [L765](../../config/revitalise-grant-automation-pipeline.yml#L765), [L789](../../config/revitalise-grant-automation-pipeline.yml#L789), [L864](../../config/revitalise-grant-automation-pipeline.yml#L864) | **PASS** |
| [`tst_acc`](../../config/revitalise-grant-automation-pipeline.yml#L1676) | **0** | **TRUE POSITIVE** |
| [`prd`](../../config/revitalise-grant-automation-pipeline.yml#L1957) | **0** | **TRUE POSITIVE** |

**This is a document contradicting the tree, and the document is the one this change edits.** [knowledge/technology/dataverse.md#L96](../../knowledge/technology/dataverse.md#L96) already says the provisioning script *"must run against every new environment before the first solution import into it — DEV, TST/ACC and PRD alike."* Every one of the seven invocations is `-Env dev`. So the rule was written down, was never implemented for two of the three environments, and nothing reads it.

**The consequence, stated as a conclusion rather than left as evidence:** the one route known to survive this platform defect exists in DEV only. A promotion to Test or Production that carries a new column permission has no route wired to recover, and the reviewer's out-of-band terminal is currently the entire mitigation. **Wiring those two steps is delivery work in a file this agent does not own and an operation that authenticates to a live environment, so §6 routes it — with the measurement attached and the conclusion drawn.**

### The two log lessons that must be corrected, not just superseded

Both are the reason this cluster is worth a review rather than a note. [The digest](../../logs/known-failure-modes.md) is generated from the `lesson` field, so a wrong lesson left in place is actively taught to every future agent:

- **[IMP-0637](../../logs/improvement-log.jsonl#L634)'s lesson** prescribes the two-phase split as the remedy. That remedy was tried and **failed** ([pipeline.log#L160](../../logs/pipeline.log#L160)). Its second half — that the coverage gates scan the profile XML with a regex and so do not respect XML comments — is independently true, was verified by the dispatch that wrote it, and is **retained**.
- **[IMP-0647](../../logs/improvement-log.jsonl#L644)'s lesson** states the two-phase workaround *"is genuinely closeable"* and that phase 2 is *"a same-day mechanical restoration."* It was written at 04:00 on source-gate and Pester evidence — V1 — about an outcome that is `observable_at: V3`, and the phase-2 import failed at 05:45, ninety minutes later. The source restoration did land; **the import of it did not**, and the entry does not distinguish those.

Neither correction changes a rule, so neither counts against the budget. Both are bookkeeping on this log's own content and both are listed in §8 as pending the keyword.

---

## 5. Retirements

> Retirement check performed: 85 live constraint rows and 10 retired reviewed for redundancy against this cluster; **none currently redundant**, because [C-TECH-050](../../constraints/technology/technology-constraints.md#L92) is the only row covering this mechanism and change 2 widens it rather than replacing it. No instance gate exists for this class to retire — it was undefended.

Counts derived, not typed: `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` → 10; `grep -rh '^| C-' constraints/ --include='*.md' | wc -l` → 85. Change 3 adds no new `verify-*.py` file, so the `57` script count in [scripts/derived-counts-registry.json](../../scripts/derived-counts-registry.json) is unchanged and `verify-build-config.py`'s suite-gate rung has nothing new to find.

**The real retirement here is a lesson, not a rule** — the two-phase import workaround, retired by §4 after one live disproof.

---

## 6. What is routed, and to whom

**One item, and I am reporting it rather than dispatching it. Re-measured at application time and STILL OPEN — 7 invocations, all `-Env dev`, 0 in either other environment, unchanged. It is now logged as `IMP-0652` so it cannot be lost between sessions, and `logs/routing.log` confirms no dispatch has been made for it.**

**Wire the Web API provisioning path into the `tst_acc` and `prd` pipeline sections.** Owner: **development-agent** (config) with **pipeline-agent** to execute. The measurement is in §4 and is not disputed: 7 invocations, all `-Env dev`, 0 in either other environment. This is the operational half of change 2, it authenticates to live environments, and per this agent's own boundary rule it is handed over rather than authored here. The two `gate-baselines.json` entries change 3 ships are what keep the build green until it lands — they are dated and owned, not a waiver.

**Nothing else is routed.** [verify-derived-counts.py](../../scripts/verify-derived-counts.py) is SOFT and still reports the same 4 drifted claims and 1 registry defect that review 2 measured and routed; I re-ran it and re-measured all five rather than passing on the gate's word. Three have moved further (`67` vs a source that now reads **69**, `51` vs **53**, `651` vs **655**), which confirms they are live in-flight work rather than stale debt, and **none is caused by this review**. No new finding is logged for them: the gate names all five on every run, and a finding restating a live gate's output is duplicate bookkeeping.

---

## 7. Findings left unprocessed

**Deferred:** IMP-0611, IMP-0612, IMP-0613, IMP-0614, IMP-0615, IMP-0617, IMP-0618, IMP-0620, IMP-0625, IMP-0626, IMP-0631, IMP-0632, IMP-0635, IMP-0636, IMP-0646, IMP-0648

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| `IMP-0611`, `IMP-0612`, `IMP-0613`, `IMP-0614`, `IMP-0615`, `IMP-0617`, `IMP-0618`, `IMP-0620`, `IMP-0625`, `IMP-0626`, `IMP-0631`, `IMP-0632` | various | **Already analysed** by [2026-09-06-improvement-review-3.md](2026-09-06-improvement-review-3.md), which never stamped `reviewed_in`. They need that document's keyword, **not a second analysis** | That document's gate is answered |
| `IMP-0635`, `IMP-0636`, `IMP-0646`, `IMP-0648` | `activation-rule-overridden-by-draft-reasoning`, `harness-blocks-destructive-call`, `figure-restated-not-cited`, `source-comment-overstates-log-evidence` | Genuinely unread, none `blocker`, none in this cluster. An unread blocker must not pull a review of everything around it | The next batch review, or the batch trigger at 30 |

Each is stamped `excluded_by` naming this document, so this disclosure does not raise a citation warning per id.

### Closure levels — what this session can and cannot prove

All three processed entries are `observable_at: V3`. **This session holds no credential for the DEV environment** and cannot run a live query, so:

| Entry | Proposed disposition | Why |
|---|---|---|
| [IMP-0649](../../logs/improvement-log.jsonl#L646) | ~~**APPLIED** on the keyword~~ → **LEFT OPEN**, `deferred_reason` + `revisit_when` | **This prediction was wrong and the validator caught it at application time.** The draft reasoned that the V3 re-observation was available from the reviewer's action at [pipeline.log#L162](../../logs/pipeline.log#L162). It is not usable as one: this finding's `ts` is 06:15 and that success is 06:10, so the citation restates the finding's own report rather than re-testing it, and `verify-improvement-log.py` refuses it by exactly that reasoning. The rule changes are applied regardless; see §11 |
| [IMP-0637](../../logs/improvement-log.jsonl#L634) | **REJECTED**, with a reason | Its root cause is disproved and its prescribed remedy failed live. Rejecting it is the accurate record; its one true sub-lesson is carried forward into change 1 rather than lost |
| [IMP-0647](../../logs/improvement-log.jsonl#L644) | **APPLIED** with a corrected lesson | What it records — the source restoration and the empty-baseline code path — did happen and is verified at V1. Only its claim about the *import* is wrong, and change 1 corrects it |

**One thing this review explicitly does not claim.** [pipeline.log#L162](../../logs/pipeline.log#L162) itself records that a live query confirming the permission row is present *"NOT YET VERIFIED LIVE BY QUERY."* The reviewer confirmed it in the maker portal, which is V4 by observation but not by query. **So the permission's presence rests on a human's reading of a portal screen, not on a `fieldpermissions` query anyone can re-run** — and that query is the natural next check, unperformed. I am not treating it as done.

---

## 8. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 646 | 646 (+1 if the routed §6 finding is logged on approval) |
| Recurring classes (x≥2) | `platform-import-ordering-defect` at x3, all `NEW` | x3, all processed |
| Digest lines | 655 | regenerates — two corrected lessons replace one that prescribed a failed remedy |

Regenerated on approval with `python3 scripts/generate-known-failure-modes.py`, confirmed with `--check`. **The digest is the read path, and it currently carries a lesson telling the next agent to use a workaround that has been proven not to work.** That is the single most valuable line of this review.

---

## 9. Simulation of the disposition — run, not reasoned

Per `agents/improvement-agent.md`, I ran the queue gate against a **scratch copy** of the log with this review's dispositions applied, using the validator's own `--log` flag so the real file is never written.

| Simulated disposition | Gate exit | What it showed |
|---|---|---|
| This draft parked — `reviewed_in` stamped on all three, `status` still `NEW` | **1** | Correct and expected: the blocker rung fires on `awaiting-approval` as well as `unread`, and it now names *this* document instead of reporting the entry unlooked-at |
| Same, checking whether IMP-0637's correction warning clears | **1, warning still present** | **The simulation corrected this review's own plan** — see below |

**What the simulation caught, and it is the reason the step exists.** I had assumed stamping `reviewed_in` on [IMP-0637](../../logs/improvement-log.jsonl#L634) would clear the `corrected by IMP-0649, and no review has processed it` warning. **It does not.** Reading [check_corrections()](../../scripts/verify-improvement-log.py#L1824) after the simulation disagreed with me shows why: the `processed_in` map is built by scanning the **review documents on disk** for processing citations, never from the entry's own field. So that warning clears when a review document *cites* the entry as processed — which is what §3's `Cites:` line and §4's table now do — and not when the field is stamped.

**Both facts matter and they are separate:** the field is what moves the entry out of `unread`, and the citation is what clears the correction warning. Reading the source is what produced my wrong answer; running the gate produced the right one.

**Confirmed against the real log after this document was written**, not left as a prediction:

| | Before this draft | After |
|---|---|---|
| `unread` | 19 | **16** |
| `awaiting-approval` | 3 | **6** — `IMP-0637`, `IMP-0647`, `IMP-0649` joined |
| `IMP-0637` correction warning | present | **cleared** |
| Gate exit | 1, on an **unread** blocker | 1, on a blocker **parked at this document's gate**, named by path |

The exit code is unchanged and that is correct — the blocker rung fires on `awaiting-approval` as well as `unread`, so it clears on the keyword and not before. **What changed is what the queue now says about these three findings:** they read as analysed and waiting for a decision rather than as findings nobody has opened.

**A refusal I did not route around.** My first simulation attempt copied the scratch file over `logs/improvement-log.jsonl` before running the gate, and the harness refused it. That refusal was correct — the command overwrote the real log — and per `skills/how-to-promote-a-finding.md` §4 the response is additive, not a workaround: the validator accepts `--log <path>`, which answers the same question without writing anything. I verified afterward that the refused command executed nothing (646 entries, `IMP-0649` unmodified). **No finding is logged against the refusal;** the control did its job and the operation had a legitimate route.

---

## 10. Gate — ANSWERED

```
IMPROVEMENT REVIEW APPLIED — docs/improvements/2026-09-07-improvement-review-3.md

Findings processed: 3 NEW  →  1 cluster
Regression check:   2 prior changes audited, 0 classes recurred
Applied:            0 constraints (cap 3), 1 constraint amendment, 1 gate check,
                    1 knowledge edit, 0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to law, 1 mechanical candidate measured
                    and DROPPED (14-17% precision), 2 log lessons corrected in place
Entries moved:      IMP-0637 REJECTED, IMP-0647 APPLIED,
                    IMP-0649 LEFT OPEN (deferred_reason — V3 re-observation unavailable)
Logged:             IMP-0652, the tst_acc/prd wiring gap, routed not dispatched
Digest:             regenerated — 649 entries, 643 lessons, 656 lines.
                    'two-phase' now appears 0 times; the disproved remedy is no longer taught
```

---

## 11. Applied record

**Status: APPLIED 2026-09-07 under `APPROVE IMPROVEMENTS`, sent by the reviewer (Xander Lykopoulos) in their own turn.** All three changes in §4 are on disk.

**One disposition changed under re-verification, and it is the first thing to read.** The draft proposed closing [IMP-0649](../../logs/improvement-log.jsonl#L646) as `APPLIED`. It is instead **left open with a `deferred_reason`**, because `scripts/verify-improvement-log.py` refused the closure and was right to. Details in the deviation table below.

| # | Change | Applied | Entries moved |
|---|---|---|---|
| 1 | [knowledge/technology/dataverse.md](../../knowledge/technology/dataverse.md#L100) — the platform fact, **narrowed** | **YES** | IMP-0649 (record), IMP-0647 |
| 2 | [C-TECH-050](../../constraints/technology/technology-constraints.md#L92) widened past "first creation" | **YES** | IMP-0649 (record) |
| 3 | [verify-pipeline-config.py](../../scripts/verify-pipeline-config.py#L532) check 14 + 2 [gate-baselines](../../config/gate-baselines.json) entries | **YES** | IMP-0649 (record) |
| 4 | IMP-0637 and IMP-0647 lessons corrected in the log | **YES** | IMP-0637 → `REJECTED`, IMP-0647 → `APPLIED` |
| 5 | A new finding for the tst_acc/prd wiring gap, per §6 | **YES** | `IMP-0652` appended |

### Deviations from the approved draft — all three recorded here, in the entry, and in the gate output

| What changed | Why it was compelled |
|---|---|
| **[IMP-0649](../../logs/improvement-log.jsonl#L646) left `NEW` + `deferred_reason`, not `APPLIED`** | Its `observable_at` is `V3`. The draft's re-observation cited [pipeline.log#L162](../../logs/pipeline.log#L162) at 06:10 — but this finding's own `ts` is **06:15**, so it was written *after* the success it reports, and the validator rejects that as *"a copy of the original report, not a re-test of it."* No honest V3 re-observation was available: this session holds no DEV credential, and the only thing it re-ran (check 14) is V1. Compounding it, that same log line says in its own words the row is **"NOT YET VERIFIED LIVE BY QUERY"** — §7 had already flagged this. The rule changes are all applied; only the entry stays open, with `revisit_when` naming the live `fieldpermissions` query and who can run it |
| **Change 1 narrowed: "cannot" → "has failed live twice, and is intermittent, not absolute"** | The §2 measurement: six commits added 36 permissions to an already-existing profile and every one imported; 70 live permissions arrived by solution import. The specific false positives this removes are those six commits, which the verbatim wording would have condemned. Both measurements are written into the bullet itself |
| **The source-diff gate WITHHELD** | 14% precision broad (7 findings / 1 true), 17% narrowed (6 / 1). Dropped rather than exempted; the measurement is recorded in the knowledge bullet so it is not re-proposed |

### Change 3, measured before and after baselining

Run against the real corpus of three declared environments **before** the baselines were added: **2 findings, both true positives** — `tst_acc` 0 invocations, `prd` 0, against `dev`'s 7. That is also the proof the check *can* fail. After the two owned, dated baselines: `PIPELINE CONFIG PREFLIGHT: PASS`, exit 0, with both findings still printed as `ACCEPTED` and no orphan-baseline warning. The gate reports 1/3 environments wired.

Entries rejected, with reasons:

| Finding | Rejected because |
|---|---|
| IMP-0637 | Root cause disproved by IMP-0649 and its prescribed two-phase remedy failed live. Its one true sub-lesson — the coverage gates read the profile XML by regex and do not respect XML comments — is carried into change 1 rather than discarded. Its `lesson` field was **corrected in place**, not merely superseded, because the digest is generated from that field |

### Verification run at application time

`python3 scripts/verify-improvement-log.py --check` → **0 errors** (649 entries). The one remaining FAIL is the blocker rung naming `IMP-0650`/`IMP-0651`, which belong to [review 4](2026-09-07-improvement-review-4.md) and are not this review's scope. `python3 scripts/generate-known-failure-modes.py` → 649 entries, 643 teaching lessons, 656 lines; `--check` confirms current. **`two-phase` now appears 0 times in the digest** — the disproved remedy is no longer taught, which was this review's single most valuable line.
