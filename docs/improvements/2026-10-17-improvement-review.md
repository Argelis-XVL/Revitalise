# Improvement Review — 2026-10-17

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 3 `NEW` → 3 clusters (the 1 unread at dispatch; 1 reviewer-deferred entry whose approved return condition this deploy met; 1 logged by this review. The 2 fixed-in-flight entries were processed by an earlier review and are named in §5, not re-derived)
**Trigger:** post-deploy batch — pipeline-agent's PARTIAL (V3) scoped DEV deploy of build `revitalise-grant-automation-20261017-1`, [pipeline.log L353](logs/pipeline.log#L353)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** DRAFT, parked at its gate. Nothing applied.
**WBS:** system work, `wbs:system`, not billable. The findings belong to wbs:5.3 and 5.6, as each entry records.

---

## Summary

Four changes are proposed: a small tool that builds a partial DEV import pack from a build, the deploy instruction that names it, a correction to one platform fact, and one line in this agent's own instructions. No new constraints and no retirements. The tool matters most: partial DEV pushes have been assembled by hand six times in nine days, and today's hand-built pack was rejected because a search pattern matched text inside an XML comment.

Nothing needs a decision from you. The draft writes down the partial DEV push you have already approved several times; it does not widen it.

## What has been built

Nothing yet. This is a draft. What it proposes:

1. **A tool builds the partial DEV pack, so nobody assembles it by hand** — new `scripts/scoped-repack.py`; today's hand-built attempt at [pipeline.log L350](logs/pipeline.log#L350). Partial pushes from a build or the working tree appear at [L330](logs/pipeline.log#L330), [L334](logs/pipeline.log#L334), [L337](logs/pipeline.log#L337), [L340](logs/pipeline.log#L340), [L345](logs/pipeline.log#L345) and [L349](logs/pipeline.log#L349). The build's own settings file holds 438 XML comments, and two of them mention the connection-references section by name. That is what today's pattern matched. The tool reads the file so that comments are skipped, refuses any pack that does not parse, and records which build each pack came from.

2. **The deploy instructions name the tool and say where a partial push may go** — [pipeline-agent.md L81](agents/pipeline-agent.md#L81) covers builds that skip unchanged apps, but nothing covers a pack holding only some of a build's components. The new bullet says: use the tool, DEV only, name the tool's record in the log line. Promotion must treat such a push as partial. Today's build is marked as a full build, while only three of its components reached DEV.

3. **The platform note about flows turning off on import is corrected** — [power-automate.md L529](knowledge/technology/power-automate.md#L529). It says an import over a running flow always switches it off. Today's import left the running scrub flow on, and so did the 16 October import. The tool printed the same "deactivated and replaced" message every time. The note will say both outcomes have happened, and that the only safe check is the flow's state read before and after.

4. **The post-deploy review re-checks deferred findings that were waiting for a deploy** — [improvement-agent.md L92](agents/improvement-agent.md#L92). The flow-state finding behind item 3 was waiting for exactly today's observation, and nothing would have reopened it: the review queue counts a deferred finding as dealt with. 16 of 299 deferred findings wait on "the next import" or "the next deploy".

## Elements added

| Element | Where |
|---|---|
| Partial-pack tool with self-test | `scripts/scoped-repack.py` (new, this repository only) |
| Bullet: partial DEV push uses the tool | [pipeline-agent.md, after L91](agents/pipeline-agent.md#L92) |
| Bullet: post-deploy scope includes deploy-keyed deferrals | [improvement-agent.md, after L94](agents/improvement-agent.md#L92) |

## Elements changed

| Element | Change |
|---|---|
| [power-automate.md fact (h)](knowledge/technology/power-automate.md#L529) | "always Draft" becomes "observed both ways; read the state before and after" |
| [IMP-1137, log L1133](logs/improvement-log.jsonl#L1133) | gains `corrects: IMP-1102`, so the digest flags the old lesson next to the new one |

---

## 1. Regression check — did the last review's changes work?

The last applied review is [2026-10-16-improvement-review-2.md, applied record](docs/improvements/2026-10-16-improvement-review-2.md#L384), applied 2026-10-17 at about 10:21. Twelve rows applied, one withheld. The only findings logged since are IMP-1137 (new class) and IMP-1138 (this review).

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| 1–3: C-TECH-030 wording, status-aware provenance check, lead runs it first | 2026-10-17 | `gate-scope-mismatch` | NO. The lead ran `verify-artifact-provenance --env dev` before dispatching and got PASS ([routing.log L1466](logs/routing.log#L1466)); re-run by this review: exit 0. The DEV deploy that two days of halts were about went ahead | **Working** |
| 4: forbidden git commands named in parallel briefs | 2026-10-17 | `concurrent-session-same-file-write` | NO. This dispatch's own brief carried the wording ("no git stash … do not touch the git index") | **Working** (one observation) |
| 5: superseding ADR lists reviewer decisions | 2026-10-17 | `approved-document-internally-inconsistent` | NO. No ADR superseded since | No opportunity |
| 6: engine push to the branch containing the parent | 2026-10-17 | `agent-instructions-describe-a-topology-that-changed` | NO. `git -C .engine branch -r --contains HEAD` lists `origin/deploy-first-learning-and-item-closure` | **Working** |
| 7: census splits reviewed fixed-in-flight entries | 2026-10-17 | `gate-reassures-wrongly` | NO. The lead's brief for this review read the two entries correctly as "already reviewed and deferred; do not re-derive" | **Working** |
| 8: engine GUID check matches the project copy | 2026-10-17 | `gate-fires-on-nothing` | NO. Lead re-ran guid-syntax exit 0 | Working |
| 9, 10: two knowledge lines | 2026-10-17 | `platform-contract-guessed-not-groundtruthed`, `no-assertion-on-shipped-content` | NO | No opportunity |
| 11: class-defence row for counts in prose | 2026-10-17 | `hand-maintained-count-drifts-from-source` | NO. `verify-derived-counts.py` exit 0, 11 of 11, re-run by this review after regenerating the digest | Working |
| 12: change log rows by per-line edit | 2026-10-17 | `harness-blocks-destructive-call` | NO. This review stamped two rows by per-line edit, no refusal | Working |

**Changes whose class recurred after a prose fix:** none. **After a gate:** none. No closure in that review was made at a lower level than its finding's `observable_at`: the one V3 closure (IMP-1131) carried a DEV re-run.

---

## 2. Clusters and promotion decisions

```
CLUSTER: scoped-pack-hand-built  (x1: IMP-1137)
Altitude:   CLASS. One logged failure, but the practice it failed in has six measured instances
            in nine days (pipeline.log L330, L334, L337, L340, L345, L349), all hand-built, and
            the failure mechanism is general: 438 comments in the build's customizations.xml, 2
            quoting <connectionreferences> (measured in build 20261017-1, both zips).
Ladder row: "A tool could catch it mechanically" -> a script. Not a gate: nothing to check at
            build time, because the input is chosen at deploy time.
Becomes:    scripts/scoped-repack.py (row 1) + pipeline-agent.md bullet naming it (row 2).
Retires:    nothing; no tool or rule existed (grepped scripts/, .engine/scripts/, provisioning/,
            agents/, knowledge/, constraints/, the pipeline config: 0 hits for repack or for a
            component-subset pack).
Cites:      IMP-1137
Residual:   (a) The tool proves the pack parses and holds the artifact's exact bytes (V1). Whether
            pac imports it is V3, seen at the next partial push. (b) Promotion's "newest deployed,
            unscoped" check stays a read of pipeline.log by pipeline-agent, as today. Row 2 tells it
            how to read a partial push; no gate. (c) Instance-only (skill section 6): the property
            holds for any Dataverse solution, but no second client has met it, so it stays here.
```

```
CLUSTER: import-changes-flow-statecode  (x1 + 1 counter-observation: IMP-1102, IMP-1137)
Altitude:   INSTANCE, knowledge correction. IMP-1102 was deferred by the reviewer with
            revisit_when "the next scoped import over an Activated flow records pre- and
            post-statecode in pipeline.log". Met: pipeline.log L348 (1011 Activated before) and
            L352 (1011 Activated after). 1009 also read Activated after the 2026-10-16 import
            (L345, before-state not recorded). One flow went Draft (1008, L335); one stayed on.
            pac printed "deactivated and replaced" in all three.
Ladder row: "One instance, general cause, a human needs to know it" -> knowledge line, corrected.
Becomes:    power-automate.md fact (h) rewritten (row 3); IMP-1137 gains corrects: IMP-1102 so
            the digest shows the old lesson beside its correction (the generator's
            corrections_of()). Rewritten text:
            "(h) An import over an Activated flow can leave it Draft, and pac's message does not
            say which. pac printed 'the original workflow definition has been deactivated and
            replaced' on every scoped DEV import measured. 1008 went Activated to Draft
            (2026-10-09) and 1011 stayed Activated (2026-10-17) (IMP-1102, IMP-1137). The cause is
            unconfirmed. An untested candidate: the 1008 import also added an environment
            variable its trigger reads, with no value set. Read the live statecode before AND
            after every import, record both, and say in the brief who turns a Draft flow back on."
Retires:    nothing.
Cites:      IMP-1102, IMP-1137
Residual:   The cause stays unconfirmed. The candidate is written as untested, per skill section 4
            ("an argued mechanism is not a confirmed one").
```

```
CLUSTER: stale-deferral-uncaught-across-sessions  (x1 here: IMP-1138; class now x10)
Altitude:   INSTRUCTION. The class's recorded defence (verify-pipeline-config.py check 14)
            covers blocked_on notes in the pipeline config, not revisit_when on log entries, so
            this is not a duplicate. A gate would read revisit_when prose. That is the
            phrase-reading shape this project has measured at 48-100% false, so no gate.
Ladder row: "The order of steps was wrong" -> the post-deploy batch's scope.
Becomes:    improvement-agent.md, new bullet after the Scope bullet (L92-94):
            "- **Scope also includes every `reviewer-deferred` entry whose `revisit_when` waits
            on an import or deploy of the deployed feature.** The deploy that triggered the batch
            is the observation those entries wait for, and the census counts them as discharged.
            Re-measure each against this deploy's `logs/pipeline.log` lines. CLOSE it with
            `reobserved` where the condition is met; otherwise say so in one line (`IMP-1138`:
            16 of 299 deferred entries matched on 2026-10-17)."
Retires:    nothing.
Cites:      IMP-1138
Residual:   The selector is read by an agent, not a parser. Measured selector (Python regex over
            revisit_when, "next|after" within 40 characters of "import|deploy|scoped"): 16 of 299.
            Hits: IMP-0243, 0597, 0670, 0804, 0866, 0867, 0879, 0906, 0922, 0933, 0943, 0969,
            0971, 1095, 1098, 1102. A deferral worded differently is missed.
```

**Duplicate check (skill §3a):** no `APPLIED` entry shares `scoped-pack-hand-built` or `import-changes-flow-statecode`. Nothing is redone.

**Premises grepped at draft time (step 6):**
- IMP-1137 says no tool exists: confirmed, 0 hits in five trees.
- Its regex mechanism: confirmed in the artifact's customizations.xml, 2 comments quoting the element.
- Its "1011 stayed Activated": confirmed at [pipeline.log L352](logs/pipeline.log#L352).
- Its "earlier scoped pushes were also hand-built": confirmed, six packs, listed above.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `scripts/scoped-repack.py` (new, instance-only) | `--artifact <dir> --component <id>… --out <zip>`. Reads the artifact's unmanaged solution zip and refuses a managed one. Keeps the named RootComponents and their elements and files. Removes every other component element by a comment- and CDATA-aware scan, so the kept bytes are identical to the source. Fail-closed: refuses when an id is missing, when the output does not parse, when a kept file differs from the source, or when a component type has files it does not know. The allow-list is set from the real artifact's file list at apply time. Writes `<out>.provenance.json`: source zip sha256, out sha256, ids, per-file sha256. Must not contain the literal `--check`. Docstring cites IMP-1137 | IMP-1137 | YES — `--selftest`, including today's case: a comment quoting `<connectionreferences>` before `<AIModels>` must give a pack that parses with the AI model kept. Then a corpus run on build 20261017-1 with today's three ids: parses; kept elements byte-identical | N/A, a tool and not a gate: not named `verify-*` and no `--check`, so the suite-gate rung at [verify-build-config.py L829](scripts/verify-build-config.py#L829) does not select it. Its input exists only at deploy time |
| 2 | agent | [pipeline-agent.md, new bullet before L92](agents/pipeline-agent.md#L92) | *"**A component-scoped push (some of an artifact's solution components, not all) is built with `python3 scripts/scoped-repack.py`, never by hand, and goes to the first environment only** (`IMP-1137`). The script refuses a pack that does not parse and writes a sidecar with the artifact zip's hash and each kept file's hash; name the sidecar in the `WRITE BEGUN` line. Treat the push as scoped in the next bullet's check, whatever the artifact's manifest says."* Generic text, no client literal | IMP-1137 | N/A — instruction change | N/A |
| 3 | knowledge | [power-automate.md fact (h), L529](knowledge/technology/power-automate.md#L529) | The rewritten text in cluster 2. That file has uncommitted edits from another session; it is re-read at apply and only the (h) bullet changes | IMP-1102, IMP-1137 | YES — needle `IMP-1102, IMP-1137` (0 today) | N/A |
| 4 | agent | [improvement-agent.md, new bullet after L94](agents/improvement-agent.md#L92) | The bullet in cluster 3 | IMP-1138 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used. [C-TECH-030](constraints/technology/technology-constraints.md#L71) already says "every deployment uses an artifact build-agent produced", and the sidecar is what lets a partial pack show it came from one.

**Where rows land:** row 1 (`scripts/`) and row 3 (`knowledge/`) are in this repository. Rows 2 and 4 are in the `.engine` submodule: engine commit pushed first to the branch holding `HEAD~1`, checked with `git -C .engine branch -r --contains HEAD`, then the pointer bump here.

---

## 4. Retirements

> Retirement check performed: 88 live constraint rows, 10 retired (derived with the anchored grep). I re-read C-TECH-030 because rows 1–2 sit beside it. It is not redundant: it is the only build-to-deploy rule, and row 2 depends on it. No other row touches what this batch changes. None retired.

---

## 5. Findings left unprocessed

**Deferred:** IMP-1095, IMP-1098

| Finding | Class | Why not processed here | Revisit when |
|---|---|---|---|
| IMP-1095 | `platform-contract-guessed-not-groundtruthed` | Processed and reviewer-deferred by an earlier review. Today's import happened, but its condition is a designer save by the reviewer, which pipeline.log does not record ([L353](logs/pipeline.log#L353): "reviewer V4 steps open") | the reviewer opens REV \| Narrative \| Scrub Free-Text in the DEV designer after its next import and it saves (unchanged; half met, the import happened) |
| IMP-1098 | same | same | same |

Excluded by state, per activation step 2: 296 other reviewer-deferred entries. Under row 4, 13 of the 16 deploy-keyed ones enter scope at the next post-deploy batch for their feature. The other three are IMP-1102 (here) and IMP-1095/1098 (above).

---

## 6. Digest impact

| | Before (dispatch) | After this draft | After apply (predicted) |
|---|---|---|---|
| Log entries | 1133 | 1134 (IMP-1138 appended) | 1134 |
| Distinct lessons | 1111 | 1112 | 1112 |
| Recurring classes (x≥2) | unchanged | `stale-deferral-uncaught-across-sessions` x9 → x10 | unchanged |
| Digest lines | 632 | 632 | about 632 |

The digest was regenerated at draft time because this review appended a finding and stamped two rows. `--check` is current and `verify-derived-counts.py` is OK, 11 of 11. On apply, IMP-1137's `corrects` puts the correction marker beside IMP-1102's lesson.

---

## Information only — not part of this review

**The work-item check's one failure is a code change from 30 September, not live work.** `verify-work-items.py` exits 1 on one item: WI-0009 (verified:dev) cites `<Panel heading="Application Details">` in [CasePanels.tsx](src/code-apps/trustee-review-portal/src/components/CasePanels.tsx#L190), and that line is no longer in the file. `git log -S` puts its removal in commit `4eb731e` (2026-09-30, "Trustee Portal fixes and updates to layout"), where headings became data-driven (`heading={section.heading}`, L190). The file has no uncommitted changes, so this is not another session's edit in progress. The check is wired `--warn-only` at [build config L193](config/revitalise-grant-automation-build.yml#L193), so it blocks nothing. Re-anchoring the evidence is pm-agent's or development-agent's work, not this review's. Nothing was logged for it.

## What is still open

**The tool exists only after approval, and its first real use is the next partial DEV push.** That push is the first time pac imports a pack the tool built (V3).

**The two narrative-flow findings still wait on your designer save** of the scrub flow in DEV, after today's import (§5).

## What you need to decide

Nothing. Rows 1–2 write down the partial DEV push you approved on 17 October ("approved for scoped deploy", [routing.log L1466](logs/routing.log#L1466)) and earlier. They do not let it go beyond DEV.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-17-improvement-review.md

Findings processed: 3 NEW  →  3 clusters
Regression check:   12 prior changes audited, 0 classes recurred
Proposed:           0 constraints (cap 3), 1 gates/scripts, 1 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 2 left as notes
Digest:             will regenerate — ~1112 lessons, recurring classes unchanged

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Planned dispositions

The applied record is written here **after** `APPROVE IMPROVEMENTS`, not before. Each disposition follows the entry's `observable_at`.

| Disposition | Entry | Closure |
|---|---|---|
| CLOSE → APPLIED (V1, `evidence_grep`) | IMP-1137 | `scripts/scoped-repack.py` · `IMP-1137`; plus `corrects: "IMP-1102"` |
| CLOSE → APPLIED (V3, `reobserved`) | IMP-1102 | `knowledge/technology/power-automate.md` · `IMP-1102, IMP-1137`. `reobserved`: level V3, by pipeline-agent, ts 2026-10-17T08:31, rerun = scoped `pac solution import` over Activated flow 1011 in DEV with the state read before and after ([L348](logs/pipeline.log#L348), [L352](logs/pipeline.log#L352)), result = Activated before and after, same pac message. This is the observation its approved `revisit_when` named; `deferred_reason` removed on closure |
| CLOSE → APPLIED (V1, `evidence_grep`) | IMP-1138 | `agents/improvement-agent.md` · `IMP-1138` |
| Not processed (§5) | IMP-1095, IMP-1098 | — |

Verification at draft time:
- `verify-improvement-log.py --check`: exit 0. 0 unread; IMP-1137 and IMP-1138 awaiting approval; IMP-1102 still reviewer-deferred, now also stamped with this review.
- Simulation on a scratch copy, with all three closures and the `corrects` field: census 0 unread, 0 awaiting approval. The schema accepted every field, `reobserved` included. The only errors were the three needles whose content does not exist until rows 1, 3 and 4 land (expected), 0 of any other kind. The real log was byte-identical before and after.
- `verify-artifact-provenance.py` on build 20261017-1 `--env dev`: PASS.
- Digest regenerated; `--check` current. `verify-derived-counts.py`: 11 of 11.

Not verified: the tool itself (unwritten until approval) and whether pac accepts its output (V3, at the next partial push).
