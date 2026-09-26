# Capability Design — Deploy-First Learning Loop and Item Closure (2026-09-26)

**Status:** DRAFT — not authorised. Requires `APPROVE IMPROVEMENTS` per workstream group (§3).
**Scope:** `system` only. Non-billable, outside the contracted WBS ([`C-COM-002`](constraints/commercial/commercial-constraints.md)).
**Altitude:** **ENGINE.** Every mechanism below is written for reuse at other clients; only data and
path lists are INSTANCE, and those are read from [`instance.yaml`](instance.yaml). Reviewer instruction,
2026-09-26: *"design it to a standard so i can use the entire system at other clients too."*
**Authorising basis:** capability mode, per [`agents/improvement-agent.md` L55-L85](agents/improvement-agent.md#L55).
**Source:** reviewer feedback of 2026-09-26 and the read-only audit of the 13 development sessions of
2026-09-18 → 2026-09-26 performed in the commissioning session. The feedback, verbatim in substance:

> Improvement agent is too strict, blocking quick deployments. Split improvement agent on technical
> blockers to deploy and prose in the files that is blocking. Technical blockers have to be resolved
> instantly. Blockers on prose (like governance, security, compliance and old decisions, etc.)
> postpone improvement run to after deployment. Make a rule to run a batched improvement agent run
> after every deployment.
>
> Although plans are made to process work, not all the work gets processed. Design a mechanism in
> which it is mandatory after finishing an item to go back on itself and check if that item is
> really finished and then go to the next item. It has to process the items as if they are PBI's
> that need proper closing.

**Relationship to earlier designs — read before applying:**

| Earlier artefact | What this document does to it |
|---|---|
| [2026-08-31 design, WS-I](docs/improvements/2026-08-31-capability-design-agent-system-optimisation.md#L244), clause 1: *"`C-TECH-061`'s blocker half stays HARD and immediate, unchanged"* | **Narrowed by WS-S.** Only the `deploy`-lane blocker half stays HARD. WS-I's batch-half change stands |
| [`agents/WORKFLOW.md` L418-L433](agents/WORKFLOW.md#L418) — *"The named exception: a scoped local fix"* and its sentence *"An agent must not write its own `deferred_reason` to clear its own build"* | **Kept for deferrals; complemented by WS-T** for the `deploy` lane. A fix is not a deferral — see WS-T's argument |
| [`IMPLEMENTATION-PLAN.md` Phase 11](docs/improvements/IMPLEMENTATION-PLAN.md#L679) (audit viewer, not started) | **Extended, not duplicated.** WS-W5 builds Phase 11's export + viewer skeleton with the work board as its **first view**, and answers Checkpoint 11's hosting question |
| [`IMPLEMENTATION-PLAN.md` Phase 8](docs/improvements/IMPLEMENTATION-PLAN.md#L475) (`new-instance.py`, `validate-instance.py`) | **Extended by WS-W6** — new `instance.yaml` keys, scaffolded and validated |
| [2026-09-01 design, WS-N](docs/improvements/2026-09-01-capability-design-operating-cost-reduction.md#L48) (digest lesson length) | **Complemented by WS-Z** — WS-N bounds lesson length; WS-Z bounds *which sections* an agent reads |

---

## 0. Conclusion first

**Two defects, one root each.**

1. **The queue gate treats every blocker as a build blocker.** Severity says *how bad*, never *what is
   blocked*. A malformed reference in a governance record and a live import failure have the same
   power to halt a build. Fix: a derived **lane** (`deploy` | `governance`) on every blocker; only an
   open `deploy` blocker halts a build; a `deploy` blocker is fixed in the dispatch that found it; every
   `governance` finding waits for **one batched improvement run after each deployment**.
2. **Work items have no state of their own.** Items exist as table rows in prose plans; handoffs carry
   WBS ids, not item ids; "done" means unit tests pass (V1/V2), not visible in DEV (V4). Items fall out
   at agent boundaries unseen. Fix: an **engine-standard work-item ledger** (Epic/Feature/PBI/Task/Bug),
   a **mandatory per-item close-out loop**, item ids carried through every handoff, and a local
   **work board** as the first view of Phase 11's viewer.

Eight workstreams, WS-S to WS-Z. **One new constraint row** is proposed (WS-W2); one existing row is
amended (`C-TECH-061`); two retirement candidates are named (§4).

---

## 1. Premises measured before drafting

Window: `ts >= 2026-09-15` in the logs; session transcripts 2026-09-18 → 2026-09-26. Every figure is
reproducible from the command beside it except the transcript figures, which come from the Claude Code
session transcripts of this project (13 sessions) and are not in the repository — **re-measure what you
can; treat the transcript figures as reviewer-supplied context.**

| Claim | Measured | Command / source |
|---|---|---|
| Blockers halt builds regardless of what they are about | 37 blockers logged in window. Hand classification (a hypothesis — **re-classify before building on it**): **20 deploy-affecting** (0734, 0737, 0738, 0763, 0769, 0777, 0781, 0782, 0804, 0813, 0816, 0820, 0821, 0824, 0831, 0852, 0866, 0871, 0874, 0883), **12 governance/process** (0745, 0757, 0767, 0772, 0780, 0784, 0787, 0791, 0814, 0835, 0838, 0843), **5 repository hygiene** (0794, 0845, 0850, 0888, 0889) | `python3 -c "import json;[print(r['id'],r['class']) for r in map(json.loads,open('logs/improvement-log.jsonl')) if r['ts']>='2026-09-15' and r['severity']=='blocker']"` |
| Builds halted by the queue alone | 3 in window: [build.log L121](logs/build.log#L121), [L123](logs/build.log#L123), [L125](logs/build.log#L125); plus build-agent HANDOFF lines to improvement-agent with `status:BLOCKED` | `grep -n "improvement-log-check" logs/build.log \| grep -E "FAILED\|BLOCKED"` |
| A build is halted by the finding describing the defect it was sent to fix | 5 recorded instances: IMP-0285, IMP-0800, [IMP-0804](logs/improvement-log.jsonl#L801), [IMP-0814](logs/improvement-log.jsonl#L810), [IMP-0816](logs/improvement-log.jsonl#L812) | `grep -n "build-blocked-by-the-finding-it-remediates\|IMP-0814" logs/build.log logs/improvement-log.jsonl` |
| improvement-agent costs more than deployment | Window dispatches: development 52, **improvement 39**, build 32, architect 13, **pipeline 10**. Whole-project share 27.2%; 40% of it blocker-triggered | `python3 scripts/report-dispatch-share.py`; routing.log `ROUTED_TO\|RESUMED\|RE-DISPATCHED` counted for `[2026-09-15` onward |
| The reviewer's time goes to keywords | 22 × "approve improvements"; 52 of 162 reviewer messages (32%) are approval keywords | transcripts |
| Blocker class is not usable for routing | 110 distinct free-text `class` values across 204 blockers | `python3 -c "import json,collections;print(len({r['class'] for r in map(json.loads,open('logs/improvement-log.jsonl')) if r['severity']=='blocker'}))"` |
| Items fall out between agents | EF-43 built and tested 2026-09-18 ([dev-summary L279](docs/development/emily-review-2026-09-18-dev-summary.md#L279)); three DEV pipeline dispatches then stopped at solution import and never ran `pac code push` ([IMP-0879](logs/improvement-log.jsonl#L875)). Reviewer, 2026-09-25: *"Not one single item of the feedback from the 20th has been processed."* | pipeline.log; transcripts |
| "Delivered" claims rest on paraphrase, not on the live screen | EF-04 claimed delivered twice, contradicted live twice ([IMP-0824](logs/improvement-log.jsonl#L820), [IMP-0885](logs/improvement-log.jsonl#L881)); a brief asked to verify a view never built ([IMP-0803](logs/improvement-log.jsonl#L800)); wbs-state `complete` contradicted live ([IMP-0784](logs/improvement-log.jsonl#L781)) | as linked |
| The close-out rule exists only in chat | Reviewer, 2026-09-22: *"Process items 1 for 1. Check after completion of an item if it really is completed."* No agent file, skill or gate carries it | `grep -rn -i "close-out\|per item" agents/ skills/` |
| No item-level state exists | [evidence-map.json](contract/evidence-map.json) is per WBS task (61); the feedback plan holds EF-01…EF-46 as rows of a 1,606-line document ([plan L1037](docs/plans/emily-review-feedback-2026-09-plan.md#L1037)) | `wc -l docs/plans/emily-review-feedback-2026-09-plan.md` |
| The digest is the largest static read | 136,984 bytes (~34k tokens) read at step 0 by build-agent ([L64](agents/build-agent.md#L64)), pipeline-agent ([L56](agents/pipeline-agent.md#L56)) and lead-agent; its *Unrouted* section alone is L564-L777 (27%) | `wc -c logs/known-failure-modes.md; grep -n "^## " logs/known-failure-modes.md` |
| Batch-threshold prose has drifted | `≥30` hand-typed in [lead-agent.md L305](agents/lead-agent.md#L305) and [improvement-agent.md L51](agents/improvement-agent.md#L51); the script's floor is `TRIGGER_BATCH = 45` and adaptive ([L224](scripts/verify-improvement-log.py#L224), [L251](scripts/verify-improvement-log.py#L251)) | `grep -n "≥30" agents/*.md` |

**Two-copy hazard (applies to every script change below).** `scripts/verify-improvement-log.py` and
most other gates are byte-identical duplicates in `scripts/` and `.engine/scripts/`
([Phase 10](docs/improvements/IMPLEMENTATION-PLAN.md#L582)). The build runs `scripts/`. Land each script
change in the engine copy **and** make the instance copy identical (or a symlink, if Phase 10 has landed
for that file), and run `python3 scripts/verify-engine-instance-split.py` before closing.

---

## 2. Workstreams

### WS-S — Derive a lane for every blocker; only `deploy` blockers halt a build

**Problem.** [`C-TECH-061`](constraints/technology/technology-constraints.md#L131) and
[`check_triggers()`](scripts/verify-improvement-log.py#L1305) fail on any `unread` or `awaiting-approval`
blocker. The build runs this as HARD step [`improvement-log-check`](config/revitalise-grant-automation-build.yml#L80),
and lead-agent treats any non-zero exit as a dispatch blocker ([lead-agent.md L326-L331](agents/lead-agent.md#L326)).

**Requirement.**
1. **New finding field `defect_in`** — a list of repo-relative paths (or `live:<env>`) naming *the
   artefact that is broken*, not the file the proposed rule change would edit. Required on every
   `blocker` appended after the cutover date; documented in
   [`skills/how-to-log-an-improvement.md`](skills/how-to-log-an-improvement.md). Rationale:
   [IMP-0816](logs/improvement-log.jsonl#L812)'s `proposed_change.target` is `scripts/…` while its defect is
   a flow in `src/` — `target` cannot carry the lane.
2. **Lane is derived, never typed.** `lane = deploy` when any `defect_in` entry matches
   `instance.yaml → improvement.deploy_paths`, or is `live:<env>`, or `observable_at ∈ {V3, V4}`.
   Otherwise `lane = governance`. A blocker with no `defect_in` derives `deploy` (fail-safe: a missing
   field can never downgrade a blocker). An agent may add `lane_override: deploy` (raise); **no field
   can lower a lane.**
3. **Default `deploy_paths` for this instance** (engine ships an empty default; `new-instance.py`
   prompts for it): `src/`, `provisioning/`, `config/*-build.yml`, `config/*-pipeline.yml`,
   `provisioning/deploymentSettings/`, `build/`. Everything else — `docs/`, `agents/`, `constraints/`,
   `skills/`, `knowledge/`, `logs/`, `contract/`, `templates/` — is `governance`.
4. **Gate behaviour** in `verify-improvement-log.py --check`:
   - `unread` + `deploy` blocker → **FAIL** (unchanged in substance).
   - `awaiting-approval` blocker (either lane) → **NOTE, exit 0.** A review document exists; the
     keyword is a queue fact, not a build input ([build.log L121](logs/build.log#L121) is the instance).
   - `governance` blocker in any state → **NOTE, exit 0**, counted toward the post-deploy batch (WS-U).
   - The census line prints lane counts: `N blockers: d deploy-open, g governance, f fixed-in-flight`.
5. **Amend `C-TECH-061`** to read *"no `deploy`-lane blocker at `status: NEW` in state `unread`"*, cite
   this document and the IMP ids in §1, and retain the withdrawn wording visibly (house style).
6. **lead-agent / build-agent / pipeline-agent text** that says "a blocker halts" is updated to "a
   `deploy`-lane blocker halts": [lead-agent.md L297-L345](agents/lead-agent.md#L297),
   [build-agent.md L108-L128](agents/build-agent.md#L108), [pipeline-agent.md L112-L131](agents/pipeline-agent.md#L112),
   [WORKFLOW.md L389-L392](agents/WORKFLOW.md#L389) and the Processing-triggers table
   [L398-L406](agents/WORKFLOW.md#L398).

**Mechanical verification.** `--selftest` gains cases: (a) unread blocker, `defect_in: [src/…]` → exit 1;
(b) unread blocker, `defect_in: [docs/…]` → exit 0 + NOTE; (c) unread blocker, no `defect_in` → exit 1;
(d) `defect_in: [docs/…]`, `observable_at: V4` → exit 1; (e) awaiting-approval deploy blocker → exit 0;
(f) a `lane_override: governance` value is rejected as a schema error. Then run against the real log and
report the lane census as a measured line in the review document.

**Files.** `scripts/verify-improvement-log.py` (+ engine copy), `skills/how-to-log-an-improvement.md`,
`constraints/technology/technology-constraints.md` (row amendment), `instance.yaml` (+ WS-W6 validator),
the four agent files above.

---

### WS-T — Technical blockers are fixed on the spot: a `fixed-in-flight` discharge

**Problem.** A delivery agent that finds and fixes a `deploy` defect cannot clear its own finding
([WORKFLOW.md L430](agents/WORKFLOW.md#L430), [IMP-0717](logs/improvement-log.jsonl#L714)); the fix then
waits for a review and the reviewer's keyword. That is the mechanism behind every
build-blocked-by-its-own-fix instance in §1.

**Why this is not the self-deferral IMP-0717 forbids.** A deferral says *"not fixing now"* — a judgement
only the reviewer may make. `fixed-in-flight` says *"fixed, and here is the re-run that proves it"* — a
fact a script can check. The rule behind the defect (the class generalisation in `proposed_change`) is
**not** discharged: it goes to the post-deploy batch like any governance item.

**Requirement.**
1. New state in [`classify()`](scripts/verify-improvement-log.py#L1284): **`fixed-in-flight`**, reached
   when a `deploy`-lane blocker carries `fixed_in_flight: {commit, rerun, exit: 0, at}` **and** an
   `evidence_grep` whose needle is present in the fixed file. The gate verifies (i) `commit` exists and
   is an ancestor of `HEAD` (`git merge-base --is-ancestor`), (ii) `exit == 0`, (iii) the needle
   resolves. It does **not** execute `rerun` (arbitrary commands are not a gate's business); the string
   is kept for the post-deploy reviewer.
2. `fixed-in-flight` does **not** fail the build and **is** counted in the post-deploy batch. It closes
   to `APPLIED` or `REJECTED` only there.
3. Any agent may write `fixed_in_flight` on a `deploy`-lane blocker **it or its dispatcher logged in the
   same feature**. No agent may write it on a `governance` blocker (schema error).
4. WORKFLOW.md's "named exception" section keeps its deferral rule verbatim and gains one paragraph
   pointing to this discharge; pipeline-agent's "Before you dispatch ANOTHER agent" section
   ([L112-L131](agents/pipeline-agent.md#L112)) changes its remedy from "route to improvement-agent" to
   "fix, stamp `fixed_in_flight`, re-run the gate, then dispatch".

**Mechanical verification.** Selftest: (a) deploy blocker + valid `fixed_in_flight` + resolving needle →
state `fixed-in-flight`, exit 0; (b) commit not an ancestor → exit 1; (c) needle absent → exit 1;
(d) `fixed_in_flight` on a governance blocker → schema error; (e) `fixed-in-flight` entries appear in the
batch count.

**Files.** `scripts/verify-improvement-log.py` (+ engine copy), `skills/how-to-log-an-improvement.md`,
`agents/WORKFLOW.md`, `agents/pipeline-agent.md`, `agents/build-agent.md`, `agents/development-agent.md`
([L363](agents/development-agent.md#L363) — "Fixing what a finding describes does NOT close that finding"
gains the `fixed_in_flight` route).

---

### WS-U — One batched improvement run after every deployment

**Problem.** Triggers today ([WORKFLOW.md L398-L406](agents/WORKFLOW.md#L398),
[improvement-agent.md L45-L53](agents/improvement-agent.md#L45)): feature completes · reviewer asks · batch
threshold · **any unread blocker, immediately** · capability request. The blocker rung pre-empts delivery
and generated 40% of improvement dispatches.

**Requirement.**
1. **New trigger, replacing "feature completes":** *every pipeline-agent Deployment Summary, whatever its
   outcome (SUCCESS, FAILED, PARTIAL), to any environment, is followed by exactly one batched
   improvement run.* Scope of the batch: every `unread` entry, every `governance` blocker, every
   `fixed-in-flight` entry.
2. **"Any unread blocker → immediately" is narrowed** to `deploy`-lane blockers that the finding agent
   could **not** fix in flight (WS-T). Governance blockers never trigger an immediate run.
3. **The batch runs alongside delivery, not in front of it.** lead-agent dispatches it in the background
   right after the Deployment Summary and may dispatch the next delivery work in parallel.
4. **Batches never stack.** If the previous batch's review is still waiting for the keyword when the next
   deployment finishes, the new batch **extends that same review document** (a new section) instead of
   opening a second one — one keyword per open review, never several.
5. The batch-threshold rung stays as a safety valve but only *requests* a batch at the next routing
   decision; it never fails a build (WS-I already made it so at build time; this extends it to routing).
6. pipeline-agent's gate output gains a last line: `NEXT: improvement-agent (post-deploy batch) — <n>
   findings queued`.
7. **Soft reconciliation:** `scripts/verify-routing-reconciliation.py` reports any `[PIPELINE]` summary
   line in `logs/pipeline.log` with no `ROUTED_TO:improvement-agent` (or `RESUMED:`) carrying
   `trigger:post-deploy` before the next `[PIPELINE]` line of the same feature. **Report, never halt.**

**Mechanical verification.** `verify-routing-reconciliation.py --selftest` gains a synthetic
pipeline.log/routing.log pair: one deploy followed by a batch → clean; one deploy with none → one report
line; exit 0 in both. After the first real deploy under the new rule, the review document quotes the
reconciliation output.

**Files.** `agents/WORKFLOW.md`, `agents/lead-agent.md` ([L297-L306](agents/lead-agent.md#L297)),
`agents/improvement-agent.md` ([L45-L91](agents/improvement-agent.md#L45)), `agents/pipeline-agent.md`,
`templates/deployment-summary-template.md`, `scripts/verify-routing-reconciliation.py` (+ engine copy).

---

### WS-V — Production guard for governance findings

**Problem.** Postponing governance/security/compliance prose to after deployment is safe for `dev` and
`tst_acc`. This instance holds special-category data (disability, health); a production promotion with an
unreviewed security-governance blocker is not.

**Requirement.** Before any deploy to the **last** environment in `instance.yaml → environment_chain`
(engine-generic; `prd` here), pipeline-agent's pre-flight requires zero `governance` blockers in state
`unread` or `awaiting-approval`. Reviewer-deferred ones pass. Never applies to earlier environments.

**Mechanical verification.** `verify-improvement-log.py --check --target-env <env>`: exit 1 only when
`<env>` is the chain's last element and a governance blocker is open. Selftest both directions.

**Files.** `scripts/verify-improvement-log.py` (+ engine copy), `agents/pipeline-agent.md` pre-flight,
`config/pipeline.yml.example` (engine), this instance's pipeline config `prd` block.

---

### WS-W — Engine-standard work-item ledger and the mandatory close-out loop

Seven parts. W1–W4 are the core; W5 is the board; W6 is multi-client scaffolding; W7 is a deliberate stub.

#### W1 — Ledger, schema and write path (ENGINE mechanism, INSTANCE data)

- **Canonical store:** `logs/work-items.jsonl`, append-only, one event per line. **Not SQLite.** The
  reviewer suggested SQLite like the engine's knowledge store; [`kb.py`](scripts/kb.py)'s own hosting
  rule forbids a live `.sqlite` inside a OneDrive/SharePoint-synced tree (file-locking corrupts it), and
  moving it outside the repo would hide it from remote sessions and concurrent sessions. SQLite remains
  available as a *generated* local index (kb.py's `migrate` pattern), never as the store. See D-7.
- **Types (Scrum vocabulary, so an Azure Boards or Jira import stays possible):** `epic`, `feature`,
  `pbi`, `task`, `bug`.
- **Hierarchy source:** where the instance has `paths.contract_dir` with a `wbs.json`, epics (phases)
  and features (WBS tasks, change orders) are **generated one-way** from it and never hand-created —
  [`C-COM-008`](constraints/commercial/commercial-constraints.md) forbids restating a baseline. Without a
  contract, epics/features are created at intake. No hours, rates or amounts in the ledger.
- **Event fields:** `schema_version`, `id`, `ts`, `by` (agent name or `reviewer`), `event`
  (`created | transition | reopen | defer | link`), `type`, `parent`, `title`, `external_id` (e.g.
  `EF-04`), `source_ref` (file#Lnn or spreadsheet+row — **the source, not a paraphrase**),
  `acceptance` (literal text copied from the source), `wbs`, `change_order`, `to_state`, `evidence`
  (list of typed objects, W3), `reason` (defer/reopen).
- **States (PBI and bug):** `new → ready → built → packaged → deployed:<env> → verified → done`, plus
  `deferred` and `reopened`. Tasks under a PBI mirror the chain (*Built, Packaged, Deployed to DEV,
  Verified in DEV*) so the board shows where each item stands.
- **Write path:** one CLI, `work-items.py` (`add`, `transition`, `reopen`, `defer`, `link`, `export`,
  `--selftest`), modelled on `kb.py`: **no agent appends JSON by hand.** Ids from an allocator that
  re-reads the maximum immediately before writing (concurrent sessions — the IMP-0080 lesson); prefix
  from `instance.yaml → work_items.id_prefix` (default `WI`).

#### W2 — The mandatory close-out loop (development-agent), and the one new constraint

Inserted into [`agents/development-agent.md`](agents/development-agent.md) between *Steps and Inline
Skills* ([L228](agents/development-agent.md#L228)) and *Gate* ([L327](agents/development-agent.md#L327)):

> **Per item, in ledger order, before starting the next item:**
> 1. Re-read the item's `acceptance` and open its `source_ref` — the spreadsheet row, the PDF page, the
>    plan line. Never work from a paraphrase ([IMP-0824](logs/improvement-log.jsonl#L820)).
> 2. Write one row per acceptance clause: clause → `file:line` that implements it. A clause with no line
>    is not done.
> 3. Run the item's own tests and the gates for the components it touched; record command + exit code.
> 4. `work-items.py transition <id> built --evidence …`. Only then take the next item.
> 5. At the end of the dispatch, reconcile: every in-scope item is `built` or `deferred` with a reason
>    the reviewer can read. Report the item table in the gate output.

Building may still fan out to sub-agents in parallel; **the close-out is serial and owned by
development-agent**, including for work a sub-agent did.

**One new constraint row** (technology): *"No work item reaches `built`, `packaged`, `deployed` or
`verified` without the evidence kinds W3 names for that transition, and no development gate passes with
an in-scope item in neither `built` nor `deferred`."* HARD at the development gate; Verify By:
`python3 scripts/verify-work-items.py --check --scope <handoff-items>`. Cites IMP-0784, IMP-0803,
IMP-0824, IMP-0879, IMP-0885.

**Reopen escalation.** Add to [`config/models.yml`](config/models.yml#L129) → `development-agent.escalate_to_strategic_when`:
*"an in-scope item has been reopened two or more times."* Regenerate subagents
(`python3 scripts/generate-subagents.py`).

#### W3 — Items travel through every handoff; each transition has typed evidence

- **Handoff contract** ([WORKFLOW.md L589](agents/WORKFLOW.md#L589)): append `| items:<id,id,…>` the
  same way `| artifact:` is appended. lead-agent dispatches by item ids; `verify-routing-reconciliation.py`
  reports a delivery dispatch with `wbs:` but no `items:` (report only).
- **Evidence kinds (engine-generic; the stack pack defines what satisfies each):**

  | Transition | Evidence kind | Checked by `verify-work-items.py` as |
  |---|---|---|
  | `built` | `source-lines` (one per acceptance clause) + `test-run` | each `file:line` exists; test command + exit 0 recorded |
  | `packaged` | `artifact-manifest` | the item id appears in `<artifact>/manifest.json` → `items[]` |
  | `deployed:<env>` | `deploy-record` for **every** component the item touches, including post-deploy operations | a `logs/pipeline.log` line for that artifact + env names each component; for this stack, a code-app item needs the `code-app-push` record, not only the import |
  | `verified` | `reviewer-verdict` | `by: reviewer`, a date and the reviewer's own words — same rule as [`C-COM-006`](constraints/commercial/commercial-constraints.md)'s acceptance record; never inferred |

- **build-agent** writes `items[]` into the manifest from the handoff; **pipeline-agent**'s Deployment
  Summary gains an *Items* table (item → components → deploy record), and any item in the artifact
  without a full deploy record is reported as `DEPLOYMENT INCOMPLETE` for that item (report; the item
  stays `packaged`, visible on the board).

#### W4 — Intake and reporting

- **Owner of the ledger: `pm-agent`** (it already owns task state derived from evidence). Any list of
  work — a feedback spreadsheet, plan rows, change-order parts — is ingested by pm-agent into items
  **before** development is dispatched. `skills/how-to-intake-external-documents.md` gains the step.
- **Reviewer verdicts:** when the reviewer reports "EF-04 still open" or "EF-07 done" in chat, lead-agent
  records it (`reopen` / `transition verified`) quoting the reviewer. The board never writes back.
- **lead-agent's closing report** for any delivery run ends with the item table from
  `work-items.py export --table --scope <items>`; anything short of `verified` is named as such.

#### W5 — The work board, as the first view of Phase 11

- Implement [Phase 11](docs/improvements/IMPLEMENTATION-PLAN.md#L679) steps 11a/11b **minimally**: the
  engine export script (shells out to `work-items.py export --json`, per Phase 11's "never re-implement a
  number" constraint) and the static viewer template with **one view — the work board**. Other Phase 11
  views stay not-started.
- Board content: hierarchy tree; per-PBI chain with evidence links; filters (state, feature, external
  id, reopened); highlights for **stuck** items (`packaged` with no `deployed:<env>` after the next
  pipeline run; `reopened ≥ 2`; `deferred` without reason).
- Opens from disk (`file://`), no server, no CDN. Answers [Checkpoint 11](docs/improvements/IMPLEMENTATION-PLAN.md#L757)
  decision (1): static file. Decision (2) (trend windows) stays open; the board needs none.

#### W6 — Multi-client scaffolding

- `instance.yaml` gains:
  ```yaml
  work_items:
    id_prefix: WI
    tracker: none          # W7 — only `none` is valid until an adapter exists
  improvement:
    deploy_paths: [src/, provisioning/, "config/*-build.yml", "config/*-pipeline.yml", build/]
  ```
- `.engine/scripts/new-instance.py` scaffolds an empty `logs/work-items.jsonl` and both keys (prompting
  for `deploy_paths`); `validate-instance.py` validates them; both `--selftest`s gain cases.

#### W7 — Tracker adapter: interface only

`tracker: none` is the only accepted value. `work-items.py export --format csv` emits Scrum-typed rows a
client's Azure Boards or Jira could import. **No adapter is built** until a client needs one (reviewer,
2026-09-26: no live querying; the client neither views nor edits items). When one is built: ledger
pushes one way; only reviewer verdicts are read back; gates never read the tracker.

**Mechanical verification (WS-W as a whole).**
- `python3 .engine/scripts/work-items.py --selftest` — schema, illegal transitions refused, allocator
  under two simulated concurrent writers, `export` formats.
- `python3 scripts/verify-work-items.py --selftest` — each evidence kind: resolving and non-resolving.
- **Real-corpus run (the acceptance test of this workstream):** pm-agent ingests the EF items of
  `docs/Import/FeedbackDeployment_20-09-2026.xlsx` (both columns) as items with their true states. The
  board must show EF-43 and the trustee-portal items as they actually stood on 2026-09-25, **not** as
  the dev summaries claimed. If the board says `done` where the reviewer said "not done", WS-W has failed.
- `validate-instance.py` and `new-instance.py --selftest` pass with the new keys; a throwaway instance
  scaffolds an empty ledger.

**Files.** New: `.engine/scripts/work-items.py`, `.engine/scripts/verify-work-items.py`,
`.engine/scripts/export-audit-data.py` (minimal), `.engine/templates/audit-viewer.html` (board view),
thin instance wrappers. Changed: `agents/development-agent.md`, `agents/pm-agent.md`,
`agents/lead-agent.md`, `agents/build-agent.md`, `agents/pipeline-agent.md`, `agents/WORKFLOW.md`
(handoff), `templates/dev-summary-template.md`, `templates/deployment-summary-template.md`,
`skills/how-to-intake-external-documents.md`, `config/models.yml`, `instance.yaml`,
`.engine/scripts/new-instance.py`, `scripts/validate-instance.py`, `constraints/technology/technology-constraints.md` (one row).

---

### WS-X — Every declared post-deploy operation actually ran (first slice of WS-W)

**Problem.** [IMP-0879](logs/improvement-log.jsonl#L875): the pipeline config declares `post_deploy:
operation: code-app-push` ([L1097](config/revitalise-grant-automation-pipeline.yml#L1097)), and three DEV
dispatches ended at solution import. This is the single mechanism behind "the trustee portal changes are
not deployed", twice. It is cheap and independent of the ledger, so it lands first.

**Requirement.** Adopt IMP-0879's own proposal: a check that, for each feature + environment, fails a
pipeline run's success claim when the config declares a `post_deploy` operation and the same dispatch's
`logs/pipeline.log` record does not name it. pipeline-agent may not write `SUCCESS` while the check
reports a gap; it writes `PARTIAL` and lists the missing operation.

**Mechanical verification.** Selftest on a synthetic config + log pair (declared-and-run → clean;
declared-not-run → report); real run over the current `pipeline.log` must flag the three historical
dispatches IMP-0879 names.

**Files.** `scripts/verify-pipeline-config.py` (+ engine copy) or a new sibling, `agents/pipeline-agent.md`.

---

### WS-Y — Remove the hand-typed batch threshold

**Requirement.** Replace `≥30` in [lead-agent.md L305](agents/lead-agent.md#L305) and
[improvement-agent.md L51](agents/improvement-agent.md#L51) with a pointer to `batch_threshold()`, as
`C-TECH-061` already does. Register the sentence in `scripts/derived-counts-registry.json` if any figure
remains.

**Mechanical verification.** `grep -rn "≥30\|>= *30" agents/` returns nothing; `verify-derived-counts.py` passes.

---

### WS-Z — Agents read only their digest section

**Problem.** The ~34k-token digest is read whole at step 0 by build-agent, pipeline-agent and lead-agent;
each needs one or two of its moment sections ([digest headings](logs/known-failure-modes.md#L110)).

**Requirement.** `generate-known-failure-modes.py` emits stable anchors per moment section and a
`--section <moment>` print mode. Step 0 of build-agent reads *Before you execute a build config* +
*Operating constraints*; pipeline-agent reads *Before you declare a deploy…* + *Before you run something
on a machine…* + *Operating constraints*; lead-agent reads *Recurring classes* only. The *Unrouted*
section (27%) is assigned sections by the generator or moved to the appendix. The full file remains
the reference.

**Mechanical verification.** `generate-known-failure-modes.py --check` and `--selftest` pass; the review
document records bytes read at step 0 per agent, before and after, as measured pairs.

**Files.** `scripts/generate-known-failure-modes.py` (+ engine copy), `agents/build-agent.md` L64,
`agents/pipeline-agent.md` L56, `agents/lead-agent.md` (knowledge to load), `CLAUDE.md` step 3.

---

## 3. Sequencing and parallel-safe groups

| Group | Workstreams | Why together | Order |
|---|---|---|---|
| 1 | WS-S, WS-T, WS-Y | same gate script, same WORKFLOW/lead-agent sections, same constraint row | **first** — unblocks deploys |
| 2 | WS-U, WS-V | Processing triggers, pipeline-agent pre-flight; depends on lanes from Group 1 | after Group 1 |
| 3 | WS-X, then WS-W (W1 → W2/W3 → W4 → W5 → W6 → W7) | pipeline-agent + new ledger scripts; WS-X is the independent first slice | WS-X may run in parallel with Group 2; WS-W after Group 2 (shares pipeline-agent.md and WORKFLOW.md) |
| 4 | WS-Z | generator + step-0 lines only | independent — any time |

**Each group is one review document and one `APPROVE IMPROVEMENTS`.** The keyword is never sent in the
same dispatch as the review request.

---

## 4. Anti-bloat accounting

| Limit ([improvement-agent.md L407](agents/improvement-agent.md#L407)) | This design |
|---|---|
| New constraints cite IMP ids | One new row (WS-W2), citing IMP-0784, IMP-0803, IMP-0824, IMP-0879, IMP-0885 |
| Max 3 new constraints per review | 1 new; `C-TECH-061` is an amendment |
| Retirement considered | **Candidate 1:** the "feature completes → improvement-agent" trigger row (replaced by WS-U). **Candidate 2:** the IMP-0717 sentence's scope — narrowed to deferrals, with `fixed-in-flight` covering fixes. Neither is a constraint row; check `constraints/` for a live row these supersede and retire it in place if one exists |
| Verify By is mechanical | every workstream above names a command |

---

## 5. What this document deliberately does not touch

- **The improvement-agent tier.** Cost is reduced by shrinking what reaches it (lanes, one batch per
  deploy), not by moving it down a tier — consistent with [`config/models.yml`](config/models.yml) and the
  2026-09-01 design.
- **The commercial loop.** No gate here halts a build on a commercial or reporting fact; hours and money
  stay out of the ledger.
- **Other Phase 11 views** (trend charts, audit export for external auditors) — not started, unchanged.
- **Any external tracker.** W7 is interface only.

---

## 6. Decisions

### Settled by the reviewer, 2026-09-26 (do not re-ask)

| # | Decision |
|---|---|
| S-1 | Split blockers: technical ones are resolved instantly; prose/governance/security/compliance/old-decision blockers wait until after deployment |
| S-2 | A batched improvement run after every deployment |
| S-3 | Items are closed like PBIs: mandatory re-check after each item before the next |
| S-4 | Local ledger, not Azure DevOps: *"If we don't do live querying anyway, then better keep it local all together."* The client neither views nor edits items |
| S-5 | Engine standard: reusable at other clients; client trackers optional per instance |

### Open — recommendation first

**D-1. `fixed-in-flight` for `deploy` blockers (WS-T).** Recommend **yes**: it is the only change that
removes the build-blocked-by-its-own-fix class, and the gate checks it mechanically. It narrows the
IMP-0717 rule to deferrals.

**D-2. Production guard (WS-V).** Recommend **yes**: governance findings never block `dev`/`tst_acc`, but
must be reviewed or deferred before `prd`. This is the commissioning session's addition, not the
reviewer's words.

**D-3. `deploy_paths` default (WS-S §3).** Recommend the list as written. Adding `contract/` would make
commercial records build-blocking again; leave it out.

**D-4. Batch runs alongside delivery (WS-U §3).** Recommend **yes, in parallel**, with the no-stacking
rule. The alternative — next build waits for the batch keyword — reintroduces the block this design removes.

**D-5. Work-board data bundle committed or gitignored (W5).** Recommend **gitignored and regenerated on
demand** (one command): concurrent sessions would otherwise conflict on a generated JSON on every
transition. The viewer template is an engine file either way.

**D-6. Backfill (WS-W acceptance test).** Recommend ingesting the 2026-09-20 and 2026-09-25 feedback
spreadsheet items as the first real corpus. It doubles as the proof that the board tells the truth.

**D-7. JSONL instead of SQLite as the canonical store (W1).** Recommend **JSONL canonical, SQLite only as
a generated index**, for the kb.py hosting reason stated in W1. Overturn only if the ledger will live
outside the synced tree for every instance.

**D-8. Who records `verified`.** Recommend **the reviewer only**, recorded by lead-agent from the
reviewer's own words.

---

## 7. Verification reached

None — this is a draft design. Nothing in `agents/`, `constraints/`, `skills/`, `knowledge/`, `scripts/`
or `config/` has been changed. The figures in §1 were measured on 2026-09-26 against this tree and the
session transcripts; the blocker-lane split in §1 is a hand classification to be re-derived by WS-S's own
census.
