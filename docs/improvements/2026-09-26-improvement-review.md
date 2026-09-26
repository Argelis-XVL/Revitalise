# Improvement Review — 2026-09-26 (1): WS-W1, the work-item ledger

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode. Authorising artefact: [capability design, WS-W part W1](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L236). The reviewer settled S-1 to S-5 in that document's §6 (S-4: local ledger, not Azure DevOps; S-5: an engine standard reusable at other clients). This review does not reopen them.
**Findings processed:** 0 `NEW` → 1 cluster (capability, no finding behind it, per [improvement-agent.md L55-L85](agents/improvement-agent.md#L55))
**Scope:** W1 only. That covers the schema, the `work-items.py` write tool, the `verify-work-items.py` verifier, the one module both of them read, and thin instance wrappers. No agent file, `WORKFLOW.md`, template, `instance.yaml`, `models.yml` or constraint is touched. Those belong to W2–W6.
**Commercial:** system work, non-billable, no WBS task ([C-COM-002](constraints/commercial/commercial-constraints.md#L35)).
**Gate:** `APPROVE IMPROVEMENTS` — **APPROVED and APPLIED 2026-09-26.** Authorisation record: Xander Lykopoulos (the reviewer; git user Xander Lykopoulos), in his own conversation turn, quoted verbatim by lead-agent to this dispatch: *"D-7 as as json file for now. / D-w1-a agreed / D-w1-b agreed / Approve improvements"*. Read as: D-7 = JSONL canonical, no SQLite; D-W1-a = contract items referenced, not copied; D-W1-b = legacy manifests accepted with a visible `legacy` mark and a count. The keyword covers this review only. What landed is in §10.

---

## Summary

This document specifies the work-item ledger in enough detail to build it: the store, the event schema, the state machine, the four kinds of evidence, the command-line surface, the concurrency rule, and each check the verifier makes. It proposes five scripts, one SOFT build step and a one-line pointer in the design document. It proposes no constraint, agent-file or skill change.

Three things wait on you: **D-7** (JSONL or SQLite as the store; I recommend JSONL, with the evidence below), **D-W1-a** (link contract epics and features by reference instead of copying them in) and **D-W1-b** (how to treat the 68 build manifests that predate item lists).

---

## 0. Where this review departs from the design text, and why

Four places. I re-measured each one against the tree before writing it here. All four keep the design's intent.

| # | Design says | This review specifies | Why |
|---|---|---|---|
| 1 | The allocator *"re-reads the maximum immediately before writing"* ([design L257-L260](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L257)) | **Allocate and append inside one lock** (`flock` plus a single `O_APPEND` write), exactly as [`allocate-improvement-id.py` L93-L125](.engine/scripts/allocate-improvement-id.py#L93) does | The design's wording is the method that [improvement-agent.md L315](agents/improvement-agent.md#L315) records failing seven times. The same stale clause still sits in the capture contract at [WORKFLOW.md L372](agents/WORKFLOW.md#L372). I logged that as a new finding and did not edit it, because Group 1 is editing `WORKFLOW.md` right now |
| 2 | Contract epics and features are *"generated one-way"* from `wbs.json` ([design L245](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L245)) | **Referenced, never copied.** An item's `parent` may be `wbs:6.8` or `co:CO-007`, and the contract files resolve those at read time | `contract/wbs.json` carries hours on every task. A copy is a second place a baseline can drift ([C-COM-008](constraints/commercial/commercial-constraints.md#L51)), and it needs a sync step that nothing would schedule. **Decision D-W1-a** |
| 3 | A single `verified` state | **`verified:<env>`**, one per environment in the chain | The design's own task list says *"Verified in DEV"*. Being verified in `dev` is not being verified in `prd`, and a single state cannot hold both facts |
| 4 | *"Tasks under a PBI mirror the chain"* | The chain-mirror tasks become **a view the export derives**, not rows in the ledger. `task` rows exist only for genuinely separate work | Stored mirror tasks would be a second record of the PBI's own state. That is the "same meaning implemented twice" class that produced the 64 h and 84 h invoiced figures stated at the same time (the `worklog.py` history in [verify-ledger-readers.py L1-L20](.engine/scripts/verify-ledger-readers.py#L1)) |

Two premises measured true, with nothing to change: no ledger or item-state store exists (`logs/work-items*` is absent, and a repo grep for `work-items|work_items` returns only the design itself), and kb.py's hosting rule does forbid a live SQLite file in a synced tree ([kb.py L45-L50](.engine/scripts/kb.py#L45)).

---

## 1. Regression check — the prior changes W1 inherits

A capability review proposes no rule that replaces an earlier one. The fair audit is of the two earlier mechanisms that W1 copies, because copying a mechanism that failed would carry the failure over.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| `allocate-improvement-id.py` (lock-held allocate-and-append), and the 2026-09-20 sweep of its instructions | 2026-08-28 / 2026-09-20 | `duplicate-improvement-id-race` | **Yes, as an instruction, not as a duplicate id.** No duplicate id since. The superseded read-then-write wording survives in one live instruction ([WORKFLOW.md L372](agents/WORKFLOW.md#L372)) and was copied into the W1 design text. Logged as IMP-0901 | **The mechanism works, and its instruction sweep is incomplete.** W1 copies the mechanism and not the wording |
| `scripts/lib/worklog.py` as the only reader of the hours ledger, guarded by `verify-ledger-readers.py` | 2026-08-23 | `two-invocation-paths-disagree` | No (log searched from 2026-09-20: no new member) | **Working.** W1 copies the pattern: one module folds the ledger, and every reader imports it |

**Changes whose class recurred after a *prose* fix:** the instruction residue above. It is prose by nature, and the correction is a one-clause edit, proposed in IMP-0901.
**Changes whose class recurred after a *gate*:** none.

---

## 2. Cluster

```
CLUSTER: work-item-ledger  (capability — design WS-W §W1; no finding behind it)
Altitude:   ENGINE — every rule below holds in any client repo; the only instance facts
            (id prefix, environment chain, contract location) are read from instance.yaml
            with engine defaults, so W1 runs before W6 adds the keys
Ladder row: "a tool could catch it mechanically" — a typed write path plus a verifier,
            the most mechanical home available
Becomes:    .engine/scripts/lib/work_items.py, .engine/scripts/work-items.py,
            .engine/scripts/verify-work-items.py, two thin wrappers in scripts/, one SOFT build step
Retires:    nothing — item state has never had a home, so nothing is superseded
Cites:      design WS-W §W1 (store, types, hierarchy, fields, states, write path) and §W3 (evidence kinds)
Residual:   the lock serialises one machine only; test-run evidence is a recorded claim, not
            re-executed; a reviewer's verdict quote cannot be checked against chat; the hours
            ledger's money scan does not cover logs/ (see §3.9)
```

---

## 3. Specification

### 3.1 Files and where each one lives

| File | Repo | What it is |
|---|---|---|
| `.engine/scripts/lib/work_items.py` | engine | **The one module that parses, folds, resolves evidence and locks.** Nothing else reads the ledger |
| `.engine/scripts/work-items.py` | engine | The write tool. Imports the module. Adds `lib/` to its path the way [verify-worklog.py L47](.engine/scripts/verify-worklog.py#L47) does, so it never needs an instance copy of `lib/` |
| `.engine/scripts/verify-work-items.py` | engine | The verifier. Imports the same module |
| `scripts/work-items.py`, `scripts/verify-work-items.py` | instance | Thin wrappers in the [validate-instance.py](scripts/validate-instance.py#L1) pattern. `verify-engine-instance-split.py` will report both as `WRAPPER` |
| `logs/work-items.jsonl` | instance | The ledger. **Not created by W1.** W6 scaffolds it, and until then an absent ledger reads as zero items |

**A trap in the wrapper for `work-items.py`:** it must not contain the literal text `--check`. [verify-build-config.py L808](scripts/verify-build-config.py#L808) treats any `scripts/*.py` containing that string as a gate that has to be wired. The write tool has no check mode, so this is only a wording rule.

### 3.2 Event schema (`schema_version: 1`)

One JSON object per line, append-only, written only by the tool. **The schema is closed: an unknown key is an error.** That closure is what guarantees *"no hours, rates or amounts in the ledger"* ([design L248](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L248)), because no such field can be added.

| Field | On which events | Rule |
|---|---|---|
| `schema_version` | all | `1` |
| `id` | all | `<PREFIX>-nnnn`. `PREFIX` comes from `instance.yaml → work_items.id_prefix`, default `WI` |
| `ts` | all | `YYYY-MM-DDTHH:MM`, the improvement log's convention. Set by the tool |
| `by` | all | An agent name, taken from `agents/*.md` and `.claude/agents/*.md` at run time (18 today), or `reviewer` |
| `at_commit` | all | `HEAD` when written, plus `dirty: true` if the tree was dirty. Set by the tool, and kept for audit |
| `event` | all | `created` · `transition` · `reopen` · `defer` · `link` |
| `type` | `created` | `epic` · `feature` · `pbi` · `task` · `bug` |
| `title` | `created` | Must not be empty |
| `parent` | `created`, `link` | A ledger id, `wbs:<task id>` (resolved in `contract/wbs.json`) or `co:<CO-nnn>` (resolved in `contract/change-orders/`) |
| `external_id` | `created`, `link` | Optional, for example `EF-04`. A duplicate among open items is a NOTE, not an error, because an item can legitimately be split |
| `source_ref` | `created`; required on `pbi`/`bug` | `path#L12`, `path!Sheet1:R12` or `path#p3`. The path must exist. **The source itself, never a paraphrase of it** |
| `acceptance` | `created`, `link` | A **list** of literal clauses copied from the source. Required on `pbi`/`bug` before `ready`. Amendable only in `new`, `ready` or `reopened` |
| `wbs` | `created`, `link` | Optional list of WBS ids. Each must exist in `wbs.json` when that file exists |
| `change_order` | `created`, `link` | Optional `CO-nnn` |
| `components` | `created`, `link` | A list of strings naming what gets deployed, for example `solution-import` or `code-app-push`. Required before any `deployed:<env>`. W1 enforces no vocabulary; the stack pack can add one later |
| `to_state` | `transition` | One of the states in §3.3 |
| `evidence` | `transition`, optional on `reopen` | A list of typed objects (§3.4) |
| `reason` | `defer`, `reopen` | Required and must not be empty |

### 3.3 Types, hierarchy and states

**Allowed parents:** a `pbi` sits under a `feature` or `epic` in the ledger, or under `wbs:` or `co:`. A `bug` sits under any of those or under a `pbi`. A `task` sits under a `pbi` or `bug`. A `feature` sits under an `epic`. An `epic` has no parent. Cycles are an error. On an instance with a contract, the export derives epics (phase) and features (WBS task) from `wbs.json`, so ledger rows of type `epic`/`feature` are only for instances without one, or for intake-created groupings.

**States for `pbi` and `bug`.** `<env>` is taken in order from `instance.yaml → environment_chain` (here `dev → tst_acc → prd`). When no chain is declared, any env name is accepted and order is not enforced.

| From | To | Evidence required | Who |
|---|---|---|---|
| `new` | `ready` | none, but `acceptance` and `source_ref` must be present | any |
| `ready` or `reopened` | `built` | `source-lines` covering **every** acceptance clause, plus at least one `test-run` | any |
| `built` | `packaged` | `artifact-manifest` | any |
| `packaged`, or `verified:<env N-1>` | `deployed:<env N>` | one `deploy-record` per declared component, for that env | any |
| `deployed:<env>` | `verified:<env>` | `reviewer-verdict` naming that env | `reviewer`, or `lead-agent` recording the reviewer's words (design D-8) |
| `verified:<any env>` | `done` | `reviewer-verdict` | the same two |
| any state except `done` | `deferred` | none, but `reason` is required | any |
| `built` and above, `done`, `deferred` | `reopened` | none, but `reason` is required. Add a `reviewer-verdict` when the reopen is on the reviewer's word | any |
| `reopened` | `ready` or `built` | as for those rows | any |

`task` rows have the states `new → done` and `deferred`, with `reason` required on defer. Epics and features have no transitions: their state is rolled up from their children at export time. **The reopen count is the number of `reopen` events.** W2's escalation rule reads that count and W1 stores nothing extra for it.

### 3.4 Evidence kinds and how each one resolves

The resolvers live once, in the module. **The tool runs them before it appends, and refuses a transition whose evidence does not resolve.** The verifier runs them again later (§3.6).

| Kind | Shape | Resolves when |
|---|---|---|
| `source-lines` | `{kind, clause, file, line, contains}` | `file` exists, and `contains` (one line, no newline, the improvement log's needle rule) occurs in it. `clause` is an index into `acceptance`. `line` is advisory: if the needle has moved, that is a NOTE and not a failure |
| `test-run` | `{kind, command, exit, at}` | `command` is not empty, `exit == 0` and `at` is a valid ISO date. **This is a recorded claim, not a re-run**, the same stance as the design's WS-T (*"arbitrary commands are not a gate's business"*) |
| `artifact-manifest` | `{kind, manifest, legacy?}` | The manifest is tracked, parses, and its `items[]` contains the item id. **For a manifest with no `items` key at all, the check depends on D-W1-b** |
| `deploy-record` | `{kind, env, component, file, contains}` | Some line of `file` (default `logs/pipeline.log`) contains all of: `WRITE ATTEMPTED:`, `— SUCCEEDED`, the needle, and the env. That is the grammar at [pipeline-agent.md L259](agents/pipeline-agent.md#L259) |
| `reviewer-verdict` | `{kind, name, date, quote, env?}` | `name` is not empty and is not an agent name, `date` is ISO and not later than the event, and `quote` is not empty. Nothing can check the quote against chat, the same limit as [C-COM-006](constraints/commercial/commercial-constraints.md#L44)'s acceptance record |

**How the env is recognised: I enumerated the corpus before choosing the rule, because the check rejects anything it does not recognise.** `logs/pipeline.log` has 18 lines that match `WRITE ATTEMPTED: … — SUCCEEDED`, in two formats. **8** carry a bracket tag (`[DEV]`). **10** use an ISO-timestamp prefix and name the env only in the text as `-Env dev`. The tags themselves vary: `[TST_ACC]` ×2 and `[TST/ACC]` ×1. So the resolver accepts **either** a bracket tag, upper-cased with `/` turned into `_`, **or** an `-Env <env>` token. A rule based on the tag alone would have rejected 10 of the 18 real success lines.

### 3.5 The write tool (`work-items.py`)

```
work-items.py add --type pbi --title "…" --parent wbs:6.8 --external-id EF-04 \
    --source-ref "docs/Import/X.xlsx!Sheet1:R12" --acceptance "…" [--acceptance "…"] \
    [--wbs 6.8] [--change-order CO-007] [--components solution-import,code-app-push] --by pm-agent
                                                  # prints the allocated id
work-items.py transition WI-0001 built --evidence ev.json --by development-agent
work-items.py reopen     WI-0001 --reason "…" [--evidence ev.json] --by lead-agent
work-items.py defer      WI-0001 --reason "…" --by development-agent
work-items.py link       WI-0001 [--parent …] [--external-id …] [--wbs …] [--change-order …] \
                                 [--components …] [--acceptance … (new/ready/reopened only)] --by …
work-items.py export --format json|table|csv [--scope WI-0001,WI-0002] [--state …] [--out PATH]
work-items.py --selftest
common:  --ledger PATH (default <paths.logs_dir>/work-items.jsonl)   --instance PATH (default ./instance.yaml)
exit:    0 written · 1 refused (illegal transition, evidence does not resolve, schema) · 2 usage   (kb.py's convention)
```

- **Every write is one critical section.** Take `flock` on an `O_APPEND` descriptor, read and fold the whole ledger, validate the event against the folded state, run its evidence resolvers, then write one line, `fsync` and release the lock. The fold happens **inside** the lock for a second reason besides unique ids: two sessions moving the same item from the same state must serialise, and the second one must be refused, not silently applied.
- **`export --format json`** is the input for W5. **`--format table`** is the markdown item table for W4's closing report. **`--format csv`** is W7's interface. Its shape was checked against [Microsoft Learn: import work items from CSV](https://learn.microsoft.com/azure/devops/boards/queries/import-work-items-from-csv): new items need `Work Item Type` and `Title`, carry no `ID`, and **cannot set `State` on import**; hierarchy is expressed by indenting across `Title 1…Title N` columns; the Scrum type names are `Epic`, `Feature`, `Product Backlog Item`, `Task`, `Bug`. So the CSV writes the ledger id and the ledger state into `Tags`. Level reached: V1, document-verified and not run against a real Azure Boards project.

### 3.6 The verifier (`verify-work-items.py`)

| Check | Fails when |
|---|---|
| `SCHEMA` | A line does not parse, a required field is missing, an enum value is unknown, a key is unknown, or `schema_version` is not 1 |
| `ID` | There is more than one `created` per id, or an event names an id that was not created earlier in the file. Both line numbers are named |
| `REF` | A `parent`, `wbs` or `change_order` does not resolve, a parent type is not allowed, there is a cycle, or a `source_ref` path is missing |
| `FOLD` | Replaying the events in file order hits an illegal transition, or an env is out of chain order |
| `EVIDENCE` | A transition lacks the evidence kinds §3.3 requires, or an item that is **not** `done` has evidence that no longer resolves at `HEAD` |
| `COVERAGE` | A `built` transition does not cover every acceptance clause |
| `AUTHOR` | `verified:<env>` or `done` was written by someone other than `reviewer`/`lead-agent`, or `by` is not a known name |
| `AMEND` | `acceptance` or `source_ref` was changed outside `new`/`ready`/`reopened` |
| `SCOPE` | With `--scope IDS --at-least STATE`: a scoped item is missing, or is below that state and not `deferred`. This is the hook W2's development gate uses |
| NOTE only | A `done` item whose evidence has since drifted (code moves on after closure), moved `source-lines`, duplicate `external_id`s, a count of `legacy` evidence, or an absent ledger (*"0 items; expected until pm-agent intake, W4"*) |

Modes: `--check` · `--scope … --at-least …` · `--warn-only` · `--json` · `--ledger PATH` · `--selftest`.

### 3.7 Self-test fixtures (both scripts, built at run time)

`work-items.py --selftest` covers: add allocates `WI-0001` on an absent ledger; the maximum id is taken from the whole file, not the last line; an **8-way concurrent `add`** gives 8 distinct, contiguous ids (the allocator's own fixture); a **2-way concurrent `transition` of one item from the same state** gives exactly one success and one refusal; each illegal transition in §3.3 is refused; `built` without full clause coverage is refused; an unknown key is refused; a `--by` that is not an agent is refused; `acceptance` amended after `built` is refused; all three `export` formats produce output, and the CSV has no `ID` or `State` column.

`verify-work-items.py --selftest` covers each check in §3.6 in both directions, and each evidence kind resolving and not resolving. That includes deploy-record lines in both real formats, the `[TST/ACC]` variant, a `— FAILED` line (rejected), and a manifest whose `items[]` lacks the id (rejected).

### 3.8 The real-corpus measurement to run at apply time, before wiring

- **The ledger itself: 0 findings, and 0 is correct**, because the file does not exist until W4 intake.
- **The resolvers against real artefacts:** the deploy-record resolver over the 18 real success lines (expected: an env resolves on 18 of 18); the manifest resolver over the 68 tracked manifests (expected: 68 without `items`, handled as D-W1-b decides); the source-lines resolver against one real `src/` file.
- **A scratch ledger** (not committed) holding three real items from the 2026-09-20 feedback sheet, including EF-43, taken as far as their evidence reaches. The design's acceptance test belongs to W4/D-6, but this proves that the resolvers stop where the evidence stops.
- **An engine literal sweep of the new engine files**, using kb.py's redact terms (client name, table prefix, this client's env key). The expected result is 0 hits. The fixtures use generic env names.

### 3.9 Residuals, stated so nobody over-trusts this

- **One machine only.** `flock` does not coordinate two machines syncing this path, or two git branches. A duplicate id is **caught** by `ID`, not prevented. That is the allocator's own residual ([allocate-improvement-id.py L31](.engine/scripts/allocate-improvement-id.py#L31)).
- **The `test-run` and `reviewer-verdict` quotes are records, not measurements.** Both are V1.
- **The money scan does not cover `logs/`.** [C-COM-004](constraints/commercial/commercial-constraints.md#L37) is enforced by a scan of `docs/ contract/ agents/ skills/ constraints/ templates/ config/` for `€` amounts ([report-baseline-drift.py L86](.engine/scripts/report-baseline-drift.py#L86)). Literal acceptance text will carry client figures: measured, 10 of 513 text cells in the 2026-09-20 feedback sheet contain `£` amounts. These are grant thresholds, not fees, with the same status as the five `docs/plans/` files that already hold `£500`. The closed schema prevents any hours or rate *field*. Extending the scan to the ledger means editing an existing script, which is outside W1 and listed as follow-on work.
- **The single-reader guard is not yet generalised.** `verify-ledger-readers.py` guards `worklog.jsonl` only. Until it is extended, "only the module reads the ledger" is a convention for `work-items.jsonl`. That is also follow-on work (an existing script).
- **Windows has no `fcntl`.** The `O_APPEND` write still prevents partial lines, and the id race falls back to being caught, as it does for the allocator.

---

## 4. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | script | `.engine/scripts/lib/work_items.py` (engine) | The single parser, fold, evidence resolvers and lock (§3.2–§3.4) | design WS-W §W1, §W3 | YES — exercised by both self-tests below | N/A — a library, not a gate |
| 2 | script | `.engine/scripts/work-items.py` (engine) | The write tool (§3.5) | design WS-W §W1 | YES — `python3 .engine/scripts/work-items.py --selftest` | N/A — a write tool with no check mode. The `verify-build-config.py` suite rung only looks at `verify-*` files and files containing `--check` |
| 3 | script | `.engine/scripts/verify-work-items.py` (engine) | The verifier (§3.6) | design WS-W §W1, §W3 | YES — `python3 .engine/scripts/verify-work-items.py --selftest` | Wired through its wrapper, row 5 |
| 4 | script | `scripts/work-items.py` (instance) | Thin wrapper. Must not contain the text `--check` (§3.1) | design WS-W Files | YES — `python3 scripts/work-items.py --selftest`; `verify-engine-instance-split.py` reports it as `WRAPPER` | N/A — not a gate |
| 5 | script | `scripts/verify-work-items.py` (instance) | Thin wrapper | design WS-W Files | YES — `python3 scripts/verify-work-items.py --selftest` | `SOFT (--warn-only)` — a new step `work-items` after `commercial-events` at [config/revitalise-grant-automation-build.yml L140](config/revitalise-grant-automation-build.yml#L140) |
| 6 | other | the capability design, end of §W1 | One line: *"W1 is specified in `2026-09-26-improvement-review.md` §3, which supersedes this section's allocator sentence and hierarchy-source bullet."* | — | N/A | N/A |

**Why row 5 is SOFT and not HARD.** The ledger is under `logs/`, which the design's WS-S puts in the `governance` lane, and settled decision S-1 says governance must not stop a deploy. A malformed ledger line halting a build would reintroduce exactly the complaint this design exists to remove. The step still runs on every build, so the ledger's health shows in a log a human reads. W2 makes the *scoped* check HARD at the development gate, where it belongs. `SUITE_GATE_EXEMPT` does not fit, because the input exists at build time ([improvement-agent.md L570-L573](agents/improvement-agent.md#L570)).

**Constraint budget:** 0 of 3 used. W2's one new row cites `verify-work-items.py --check --scope`, which this review builds.

**Order when applied (two repositories).** Rows 1–3 go on branch `deploy-first-learning-and-item-closure` in `.engine`, as the brief says, not on engine `main`. Push that branch first and confirm with `git -C .engine branch -r --contains HEAD`. Then rows 4–6 and the submodule pointer go in the instance commit. Before closing, run `verify-build-config.py` on the build config, `verify-engine-instance-split.py` and `verify-derived-counts.py` (the verify-script count goes up by one). **The build config is also a target for the parallel WS-X draft**, so row 5 is a one-step insert made by re-reading the file at apply time.

---

## 5. Retirements

Nothing is retired. Item state has never had a home, so nothing is superseded. The two candidates the design names ([design §4](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L437)) belong to WS-U and WS-T, not W1.

> Retirement check performed: the design's two candidates reviewed; neither is in W1's scope, and no live constraint row governs item state.

---

## 6. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901

The queue gate reports 12 `unread`, 1 `awaiting-approval` (IMP-0855, parked on its own document) and 214 `reviewer-deferred`. None of the 12 unread concerns work items. They are gate-scope, intake-payload, TAD and pipeline-hygiene findings for the next defect review or the post-deploy batch (WS-U). IMP-0901 is this dispatch's own finding: its `WORKFLOW.md` half is Group 1's file, and this review corrects only its design-text half (§0 row 1). I did not stamp `excluded_by` on the unread entries. That would mean rewriting log lines while Group 1 is appending to the same file, and the line above already declares their scope.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0901 | `duplicate-improvement-id-race` | its fix is one clause in `WORKFLOW.md`, which Group 1 is editing now | Group 1's review is applied |
| the 12 unread | various | outside WS-W1 | the next defect review or post-deploy batch |

---

## 7. What you need to decide

### Store

**D-7. Should the ledger's canonical store be JSONL, with SQLite at most a generated index?**

**Problem** — SQLite would give indexed queries, but this repository sits in a synced SharePoint folder, where kb.py's own rule says a live SQLite file gets corrupted, and moving the file outside the repo would hide it from remote and fresh-clone sessions.
**Suggested fix** — JSONL canonical, as specified above. The evidence: all three existing ledgers here are JSONL with a validator (`improvement-log` 897 lines, `commercial-events` 11, `worklog` 3), and no SQLite file is tracked; the 3.6 MB improvement log parses in 11.4 ms, while a feedback round of about 50 items at about 8 events each is roughly 400 lines; the lock-plus-append pattern already has an 8-way concurrency fixture passing; JSONL shows in a git diff the reviewer can read, and SQLite does not.
**What happens if you don't** — Choosing SQLite means putting the database outside every synced tree for every client, and giving up remote sessions' view of item state. Choosing it inside the tree risks corruption that surfaces as lost items, not as an error.
[design D-7](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L495) · [kb.py hosting rule](.engine/scripts/kb.py#L45)

---

### Hierarchy

**D-W1-a. Should contract epics and features be referenced (`wbs:6.8`, `co:CO-007`) instead of generated into the ledger?**

**Problem** — The design says to generate them one-way from `wbs.json`, but that file carries hours on every task, and a generated copy needs a sync step nothing schedules.
**Suggested fix** — Reference them. The ledger stores items only; the export derives phase and task names from the contract files at read time.
**What happens if you don't** — A copied WBS drifts from the contract the first time a change order amends it, which is the baseline-restatement failure the Commercial Rules forbid.
[design L245](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L245)

---

### Evidence

**D-W1-b. Should an item be allowed to reach `packaged` on a build manifest that predates item lists, if the evidence is marked `legacy`?**

**Problem** — All 68 tracked build manifests lack an `items` list, which W3 introduces. Under a strict rule, no historical item can pass `packaged`, so the D-6 backfill would show items as merely `built` even where the pipeline log proves they were deployed.
**Suggested fix** — Accept `legacy: true` only on a manifest with **no** `items` key at all, have the verifier count every such case as a visible NOTE, and reject it on any manifest that has the key.
**What happens if you don't** — Backfilled items stop at `built` until they are rebuilt. That is honest, but the board then understates real deployments, and the acceptance test cannot tell "never deployed" from "deployed before W3".
[§3.4](docs/improvements/2026-09-26-improvement-review.md#L128)

---

D-7 blocks nothing else in W1. If you choose SQLite, §3.1, §3.5 and §3.9 change and the rest stands. D-W1-a and D-W1-b change one resolver each.

---

## 8. Digest impact

| | Before | After this draft |
|---|---|---|
| Log entries | 896 | 897 (IMP-0901 appended by this dispatch) |
| Digest bytes | 136,984 (design §1) | 137,083 |

Regenerated with `python3 scripts/generate-known-failure-modes.py` after the validator passed. Applying the review changes no log entry, because no finding is closed by W1.

---

## 9. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review.md

Findings processed: 0 NEW  →  1 clusters
Regression check:   2 prior changes audited, 1 classes recurred
Proposed:           0 constraints (cap 3), 5 gates/scripts, 0 skill/knowledge edits,
                    0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class, 0 left as notes
Digest:             will regenerate — 888 lessons, unchanged by apply

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 10. Applied

Applied 2026-09-26, after re-verifying the tree. No finding added since the draft (IMP-0902 to IMP-0907) names or corrects anything in W1, and every premise in §0 and §3.4 was re-measured by running the new code against the real corpus (below).

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `.engine/scripts/lib/work_items.py` | engine `a21593d`, branch `deploy-first-learning-and-item-closure` (pushed; `git -C .engine branch -r --contains HEAD` lists `origin/deploy-first-learning-and-item-closure`) | none — a capability, no finding behind it |
| 2 | `.engine/scripts/work-items.py` | engine `a21593d` | none |
| 3 | `.engine/scripts/verify-work-items.py` | engine `a21593d` | none |
| 4 | `scripts/work-items.py` (wrapper; contains no `--check` text) | the instance commit carrying this section, with the submodule pointer bump to `7977bf7` | none |
| 5 | `scripts/verify-work-items.py` (wrapper) plus the SOFT `work-items` step after `commercial-events` in `config/revitalise-grant-automation-build.yml`, with the config re-read immediately before the insert | the same instance commit | none |
| 6 | One-line APPLIED pointer at the end of the design's §W1 | the same instance commit | none |
| 7 | `agents/improvement-agent.md` L551 verify-script count, 65 → 66 (lead-agent's instruction; see below) | engine `7977bf7` | none |

**What was executed, and what it returned:**

- `python3 scripts/work-items.py --selftest`: **29 of 29 OK**, exit 0. This includes an 8-way concurrent `add` (8 distinct, contiguous ids) and a 2-way same-state transition race (exactly one success, one refusal).
- `python3 scripts/verify-work-items.py --selftest`: **43 of 43 OK**, exit 0. The first run failed one fixture whose expectation I had written wrong: a deploy record naming another env is an `EVIDENCE` failure for `deployed:dev`, not a `FOLD` failure. The code was right, the fixture expectation was corrected, and the assertion stays in the suite.
- **Can-it-fail proof (mutation):** three mutants of the module, each killed by at least one of the two self-tests: the `— SUCCEEDED` requirement removed; clause coverage disabled; the lock removed.
- `python3 scripts/verify-work-items.py --check` on this repo: **0 events, 0 items, 0 failures, 1 note**, exit 0. **0 is correct**: `logs/work-items.jsonl` does not exist until pm-agent's intake (W4) writes it.
- **Real corpus, resolvers:**
  - The deploy-record env rule resolves a chain env on **18 of 18** real success lines in `logs/pipeline.log`.
  - The manifest resolver over the **68** tracked manifests: all 68 are refused unmarked and accepted with `legacy: true` (D-W1-b).
  - A real `source-lines` needle resolves, and a moved line is reported as a NOTE, as specified.
  - The context read from `instance.yaml`: prefix `WI`, chain `dev → tst_acc → prd`, 18 agents, 61 WBS tasks, 9 change orders.
- **Real corpus, one real item end to end (scratch ledger, not committed):** EF-43, from row 50 of the 2026-09-20 feedback sheet.
  - It reached `ready`, `built` (both clauses traced to the portal source) and `packaged`. `packaged` was refused unmarked and accepted with `legacy`. It then reached `deployed:dev` on the two real 2026-09-25 write records (import and code push).
  - `verified:dev` **was refused** because no reviewer verdict exists.
  - A reopen quoting the sheet's reviewer column (*"Partly done, but not adjusted based on feedback from the 20th of September"*) left it `reopened`, with 1 reopen.
  - The verifier over that ledger: 6 events, 0 failures, 1 legacy note. The ledger stopped exactly where the evidence stopped.
- `verify-build-config.py` on the build config: exit 0. **Positive control:** the same check on the pre-change config fails with `suite-gate-is-not-a-step` naming `verify-work-items.py`, and does not name `scripts/work-items.py`. So the wiring is necessary, and the wrapper stays outside the check's net.
- `verify-engine-instance-split.py`: exit 0, **94 scripts: 61 duplicate, 25 split/wrapper** (was 23; the two new wrappers).
- **Engine literal sweep** of the three new engine files for the client name, table prefix and this client's env key: 1 hit found (a docstring naming this client's env tag spelling), which was rewritten; after that, 0 hits. Positive control: 4 hits in `scripts/kb.py`.
- Also run: `verify-improvement-log.py --check` exit 0; `verify-gate-input-tracking.py` exit 0; `verify-doc-line-links.py` exit 0.

**One addition beyond the draft's change table, on lead-agent's instruction:**

- **The count at [improvement-agent.md L551](agents/improvement-agent.md#L551) was changed from 65 to 66** (`verify-*.py` scripts), re-derived with `ls scripts/verify-*.py | wc -l`. That line is the registered claim `improvement-agent-verify-script-count`, and the agent file requires a review that adds a gate to update it in the same change. The original brief forbade touching agent files in W1; lead-agent then asked for this one figure explicitly. This is the only agent-file change.
- Committed on the engine branch as `7977bf7`, pushed, and confirmed by `branch -r --contains HEAD`.
- `verify-derived-counts.py`: **exit 0, 11 of 11 registered claims match**. It reported this one drift before the fix.

**Level reached (C-TECH-053):**

- V1 for the ledger mechanism: well-formed, self-tested, and run against the real corpus.
- Nothing in any environment was touched.
- The CSV export's Azure Boards shape is document-verified only and has not been imported into a real project.

**Not done here, by scope:** W2–W7. No ledger file was created, no item was ingested (the D-6 backfill is W4), and no agent file other than that one registered figure, no template, `instance.yaml` or constraint was changed. Improvement-log entries moved to `APPLIED`/`REJECTED`: **none**, because this review processed no finding. IMP-0901 stays `unread` for the batch after Group 1.
