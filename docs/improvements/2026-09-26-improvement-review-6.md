# Improvement Review — 2026-09-26 (6): WS-W2 and WS-W3, closing items one at a time and carrying them through every handoff

**Agent:** improvement-agent (tier `strategic`)
**Mode:** capability mode. Authorising artefact: [capability design, WS-W parts W2 and W3](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L263). The reviewer settled S-1 to S-5 in that document; S-3 (*"items are closed like PBIs: mandatory re-check after each item before the next"*, [design L473](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L473)) is the decision this review implements. It is not re-asked.
**Scope:** W2 (the close-out loop, the one new constraint, the reopen escalation) and W3 (item ids in every handoff, typed evidence per transition, the manifest's `items` list, the Deployment Summary's Items table and per-item `DEPLOYMENT INCOMPLETE`). W4 to W7 are drafted by a sibling dispatch and are not touched here.
**Builds on:** W1 as landed ([review 2026-09-26 (1)](docs/improvements/2026-09-26-improvement-review.md#L69)), WS-X as applied ([review 2026-09-26 (3)](docs/improvements/2026-09-26-improvement-review-3.md#L136)) and Group 1 as applied in the working tree ([review 2026-09-26 (4)](docs/improvements/2026-09-26-improvement-review-4.md#L256)).
**Findings processed:** 4 NEW → 6 clusters (two capability clusters with no finding behind them, plus four findings this review logged from what its own measurements showed)
**Trigger:** capability mode
**WBS:** `wbs:system`. System work on the rules, outside the contracted WBS, not billable ([C-COM-002](constraints/commercial/commercial-constraints.md#L35))
**Gate:** `APPROVE IMPROVEMENTS` — **APPROVED 2026-09-26.** Authorisation record: authorised_by Xander Lykopoulos (the reviewer; git user Xander Lykopoulos); relayed_by lead-agent, quoted verbatim from his own conversation turns in that session. Decision turn: *"Approved for W2, W3 and D-W3-a (agent may add to git for this purpose)"*. Keyword turn: *"APPROVE IMPROVEMENTS for W2, W3"*. Read as: D-W3-a = build-agent may `git add` (stage, index only, never commit) the manifest it wrote, in its own future runs. It is not permission for this apply to stage anything. The artefacts this act produces are the changes listed in section 8.
**Status:** ~~DRAFT. Parked at the gate. Nothing applied.~~ ~~APPLYING~~ **APPLIED 2026-09-27 in full (phases 1 and 2), working tree only, no commit** (reviewer: *"Wait until group 1 has landed. And all items of the plan are processed. Then we do 1 big commit."*). Phase 1 (everything except `lib/work_items.py` and `agents/lead-agent.md`, which the concurrent W4–W7 apply also edits) and phase 2 (those two, after W4–W7 reported) are recorded in section 8. All four findings this review processed are `APPLIED`.

---

## Summary

Items can now be closed one at a time and followed from the plan to the environment, but three of the rules W1 shipped for checking a deploy would have let the board lie. The worst one: in a scratch run, the ledger marked an item as deployed to DEV on the strength of a solution import alone, although the item also needed the Code App push. That is exactly how the trustee-portal changes went missing twice, now one level up. This review fixes those rules at the same time as it wires the loop, and it aligns them with the post-deploy check pipeline-agent already runs.

**Waiting on you:** one decision (D-W3-a: may build-agent stage its manifest in git, without committing, so an item can be marked packaged at build time), then `APPROVE IMPROVEMENTS`.

## What this review proposes

1. **development-agent closes every item before it starts the next** ([development-agent Steps section](agents/development-agent.md#L228)). Re-read the item's source, trace each acceptance clause to a line, record the test runs, and move the item to `built` through the ledger tool. Anything unfinished is deferred with a reason the reviewer reads at the code-review gate. The close-out is serial even when sub-agents built in parallel.

2. **One new HARD constraint makes the loop a gate, not a habit** ([Section 7 of the technology constraints](constraints/technology/technology-constraints.md#L115)). A development gate cannot pass while an item it carried is neither `built` nor `deferred`; test-agent checks the same at `packaged`. The check is the scoped mode W1 built for this purpose.

3. **Item ids travel in every handoff, beside the WBS ids** ([Handoff Contract](agents/WORKFLOW.md#L604)). Each hop passes on only the items it actually moved. lead-agent dispatches by id, and the routing reconciliation reports a delivery dispatch that carries WBS ids but no item ids.

4. **Each hop moves its own items, on its own evidence.** build-agent writes the built items into the manifest and marks them packaged ([build-agent step 8](agents/build-agent.md#L137)). test-agent reopens the items that fail. pipeline-agent marks each item deployed only when every part of it has a successful write record for that environment, and otherwise reports that item as `DEPLOYMENT INCOMPLETE` ([pipeline-agent environment block](agents/pipeline-agent.md#L428)).

5. **The deploy evidence rule reads the same records the post-deploy check reads** ([W1 resolver](.engine/scripts/lib/work_items.py#L619), [WS-X grammar](scripts/verify-post-deploy-completeness.py#L73)). One shared module holds the grammar. A record for the Code App push has to name the push command, not just the build. And an environment only owes the parts its own pipeline config declares.

6. **An item reopened twice escalates development-agent to the strategic tier** ([development-agent escalation list](config/models.yml#L134)).

### Elements added

| Element | What it is |
|---|---|
| `C-TECH-079` | The one new constraint row (W2) |
| `.engine/scripts/lib/deploy_markers.py` | The single copy of the write-marker grammar and the pipeline-config component vocabulary |
| development-agent → *Close-out: one item at a time* | The per-item loop |
| pipeline-agent → *Items: which work items reached this environment* | The per-item deploy record and `DEPLOYMENT INCOMPLETE` |
| Dev Summary *Work Items* record, Deployment Summary *Items* | Where the reviewer reads the close-out and the deploy result per item |
| routing reconciliation CHECK 3 | Reports a delivery dispatch with `wbs:` and no `items:` |

### Elements changed

| Element | Change |
|---|---|
| `lib/work_items.py` deploy-record resolver | Shared grammar (60 of 60 success markers, was 18); the component's own command must appear; per-environment owed set |
| `verify-work-items.py --scope` | Evidence drift on an item outside the scope becomes a note, not a failure |
| `verify-post-deploy-completeness.py` | Imports the shared grammar; the instance copy becomes a thin wrapper |
| Handoff lines in WORKFLOW, README, development, build, test and pipeline agents | `| items:` appended |
| pipeline-agent report-back block | Every write marker names the build it belongs to |
| `config/models.yml` | One escalation condition for development-agent |

## What is still open

**The Code App push can be declared only where the pipeline config declares it.** The dev environment declares it as an operation; test/acceptance and production carry the app inside the managed solution. So an item owes the push in dev and owes only the deploy command further up the chain. That is the config's statement, read mechanically, and it is correct only as long as the config is.

**A code-review revision that moves an item's traced lines reopens that item.** Its evidence stops resolving, so the scoped check fails until it is reopened and closed again. Reopens are counted, so two revisions of the same item escalate development-agent. I think that is the right signal, but it is new and should be watched.

**Nothing re-runs a recorded test command, and nothing checks a reviewer's quote against the chat.** Both are records, not measurements, as W1 already states.

**The ledger is empty until the W4 intake lands.** Every rule here is vacuous until pm-agent writes the first item. The routing check starts on the apply date for that reason.

## What you need to decide

### Git

**D-W3-a. May build-agent stage (`git add`, never commit) the manifest it just wrote, so the items in it can be marked packaged at build time?**

**Problem** — The ledger refuses a manifest that is not in git's index, and build-agent never stages one, so no item can reach packaged, and therefore no item can reach deployed, until you next commit.
**Suggested fix** — build-agent stages only `$ARTIFACT_DIR/manifest.json`, a file `.gitignore` already re-includes and every one of your commits already carries (68 of 68 manifests on disk are tracked).
**What happens if you don't** — Items stay `built` after a successful build and deploy until a commit, and then somebody has to replay every packaged and deployed transition by hand, which nothing schedules. The board would understate every deploy between commits.
[the measured refusal, logged as a finding](logs/improvement-log.jsonl) · [W1 resolver](.engine/scripts/lib/work_items.py#L575)

---

D-W3-a blocks only the build-agent step 8a text and the packaged half of the pipeline flow. Everything else stands either way.

---

## 0. Where this review departs from the design text, and why

Each row was re-measured against the tree before it was written here.

| # | Design says | This review specifies | Why |
|---|---|---|---|
| 1 | Verify By: `verify-work-items.py --check --scope <handoff-items>` ([design L284](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L284)) | `--scope <items> --at-least built` | Executed: `--scope` without `--at-least` checks only that the ids exist ([verify-work-items.py L93](.engine/scripts/verify-work-items.py#L93)). The state check needs the flag |
| 2 | `deployed:<env>`: "a `logs/pipeline.log` line for that artifact + env names each component" ([design L302](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L302)) | The component's **own command literal** must be in the SUCCEEDED marker, read from the pipeline config through the same table WS-X uses | Executed in a scratch ledger: an item needing the push reached `deployed:dev` on two records that both matched the import line. W1's resolver compares env, needle and success mark, never the component |
| 3 | (silent on grammar) | The resolver reads markers with **WS-X's grammar**, from one shared module | Measured over `logs/pipeline.log`: W1's two literals accept **18** SUCCEEDED markers; WS-X's grammar accepts **60**, and every one of the 18 is among them. The 42 missed lines are the `WRITE_ATTEMPTED —` and `-- SUCCEEDED` spellings |
| 4 | "the item id appears in `<artifact>/manifest.json` → `items[]`" ([design L301](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L301)) | …and the manifest is **staged** before the transition (D-W3-a) | Executed: untracked manifest → `REFUSED [EVIDENCE] … is not tracked`; the same file after `git add` → accepted |
| 5 | "deploy-record for **every** component the item touches" | Every component **this environment's config declares**; `deploy` when none of the item's components apply there | The real config declares `operation:code-app-push` in dev only (test/acceptance and production deploy through `pac pipeline deploy`). Read literally, a Code App item could never reach test/acceptance |
| 6 | Files list omits `agents/test-agent.md` and `agents/README.md` ([design L365](docs/improvements/2026-09-26-capability-design-deploy-first-learning-and-item-closure.md#L365)) | Both gain the `items:` handoff line | Only lead-agent reads `WORKFLOW.md`. Every other agent learns its handoff format from its own file, and test-agent's handoff to pipeline-agent is a hop items must cross ([test-agent L136](agents/test-agent.md#L136)) |

Two premises measured true, nothing to change: `verify-build-manifest-note.py` has no closed key set, so an `items` key cannot fail it (grepped), and `paths.pipeline_config` is already a required, validated `instance.yaml` key ([validate-instance.py L118](.engine/scripts/validate-instance.py#L118)), so the resolver's new dependency needs nothing from W6.

---

## 1. Regression check — the prior changes W2 and W3 build on

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| W1 ledger: write tool, verifier, five evidence resolvers ([review (1) change table](docs/improvements/2026-09-26-improvement-review.md#L208)) | 2026-09-26 | capability, no class | **Yes, before first use.** Three of its evidence rules measure wrong at W3's draft time: the deploy grammar (18 of 60), the component never compared, a scoped check that fails on other items' drift | **Mechanism right, three rules wrong.** Corrected in this review (clusters 3 to 5) before any item exists, so nothing needs migrating |
| WS-X: a stage may not claim SUCCESS with a declared post-deploy operation not run ([review (3) change 2](docs/improvements/2026-09-26-improvement-review-3.md#L136)) | 2026-09-26 | `pipeline-dispatch-stops-before-declared-post-deploy` | **Yes, on another surface.** W1's ledger would have accepted "the item is deployed" on the import alone, which is the same failure one level up (cluster 4). No deploy has run since WS-X, so the gate itself has not been exercised | **The gate is right; it did not cover a second reader.** This review makes the second reader use the gate's grammar and table rather than add a third |
| Group 1, development-agent step 4: stamp `fixed_in_flight` ([review (4) row 10](docs/improvements/2026-09-26-improvement-review-4.md#L272)) | 2026-09-26 (working tree) | `build-blocked-by-the-finding-it-remediates` | Too early. No build has run since | Leave alone |

**Changes whose class recurred after a *prose* fix:** none.
**Changes whose class recurred after a *gate*:** WS-X's class, on a surface the gate never read. Logged as a new finding in the `wrong-artefact-cited-as-evidence` class rather than as `gate-cannot-fail`, because WS-X's gate fires correctly on everything it reads.

---

## 2. Clusters and promotion decisions

```
CLUSTER: work-item-close-out-loop  (capability — design WS-W §W2)
Altitude:   ENGINE — the loop, the constraint and the escalation name no client fact; the ledger
            path, id prefix and environment chain come from instance.yaml
Ladder row: "an agent had the information and still did the wrong thing" (the reviewer's
            instruction existed only in chat) + "a tool could catch it mechanically" (the
            scoped check exists and is made HARD at the development gate)
Becomes:    development-agent *Close-out* section + gate lines; C-TECH-079; one models.yml
            escalation condition; the Dev Summary's *Work Items* record
Retires:    nothing — no rule governed item closure before
Cites:      design WS-W §W2; IMP-0784 (as corrected by IMP-0788), IMP-0803, IMP-0824,
            IMP-0879 (as corrected by IMP-0907), IMP-0885, IMP-0911
Residual:   test-run and reviewer-verdict evidence are records, not re-executions; a clause can
            be traced to a line that does not in fact implement it — the reviewer's code review
            is still the only check of meaning
```

```
CLUSTER: items-through-every-handoff  (capability — design WS-W §W3)
Altitude:   ENGINE — handoff grammar, the manifest key and the per-item deploy record are generic;
            the component vocabulary is read from the instance's own pipeline config
Ladder row: "the order of steps was wrong" (items fell out between agents) + "a tool could
            catch it mechanically" (the ledger refuses a transition whose evidence does not resolve)
Becomes:    Handoff Contract + README line; `| items:` on every delivery handoff; build-agent
            step 8a and manifest key; test-agent reopen on failure; pipeline-agent *Items*
            section, gate line, marker build name; Deployment Summary *Items*; routing
            reconciliation CHECK 3 (report only)
Retires:    nothing
Cites:      design WS-W §W3; IMP-0912
Residual:   an agent that omits `| items:` from a handoff is caught only by the routing report,
            and only for dispatches lead-agent logged; a HANDOFF line is gate output, not a file
```

```
CLUSTER: two-invocation-paths-disagree  (x1 new: IMP-0909; class x14 recorded)
Altitude:   CLASS, ENGINE — the property is "one log line, one parser"; the grammar names the
            platform CLI's verbs only, the precedent WS-X set
Ladder row: "second instance → generalise" — the class is recorded 14 times; the remedy is one
            module both readers import, never a copied regex
Becomes:    .engine/scripts/lib/deploy_markers.py; lib/work_items.py and
            verify-post-deploy-completeness.py import it
Retires:    the two private copies of the grammar
Cites:      IMP-0909
Residual:   verify-provisioning-report.py reads a deliberately NARROWER grammar (only
            `WRITE ATTEMPTED:`), measured and documented in its own docstring. It answers a
            different question (preflight pairing) and is left alone
```

```
CLUSTER: wrong-artefact-cited-as-evidence  (x1 new: IMP-0910; class x9 recorded)
Altitude:   CLASS, ENGINE — "an evidence rule that names what was deployed must match the
            thing named" holds for any stack; the literal per component is read from the
            instance's pipeline config
Ladder row: "a tool could catch it mechanically"
Becomes:    the deploy-record resolver requires the component's own command in the marker, and
            an environment owes only the components its config declares
Retires:    nothing
Cites:      IMP-0910
Residual:   an item that declares too FEW components (a Code App change declared as `deploy`
            only) is marked deployed on the import. What must be deployed is declared by the
            agent that closed the item; the close-out loop's step 4 asks for it, nothing proves it
```

```
CLUSTER: hard-gate-red-on-pre-existing-debt  (x1 new: IMP-0911; class x3 recorded)
Altitude:   CLASS, ENGINE — a scoped HARD check fails on its scope only
Ladder row: "a tool could catch it mechanically" — the verifier's scope semantics
Becomes:    verify-work-items.py: with --scope, evidence drift on an out-of-scope item is a NOTE
            naming the item
Retires:    nothing
Cites:      IMP-0911
Residual:   write-borne failures on any line (SCHEMA, ID, REF, FOLD, COVERAGE, AUTHOR, AMEND)
            stay global — they mean the ledger cannot be folded honestly for anyone, and the
            write tool refuses every one of them, so they arise only from a hand-appended line or
            a cross-machine merge
```

```
CLUSTER: gate-scope-mismatch  (x1 new: IMP-0912; class x25 recorded)
Altitude:   INSTANCE of a general rule already stated — "a gate's input exists when the gate
            runs"; the remedy is a step, not a new gate
Ladder row: "the order of steps was wrong"
Becomes:    build-agent step 8a stages the manifest before the packaged transition (D-W3-a)
Retires:    nothing
Cites:      IMP-0912
Residual:   git's index lock: a concurrent session holding it makes `git add` fail; build-agent
            reports the refused transition and the build stands
```

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | constraint | `constraints/technology/technology-constraints.md`, Section 7, new row after `C-TECH-078` ([L148](constraints/technology/technology-constraints.md#L148)) | `C-TECH-079`, wording in 3.1 | design WS-W §W2, §W3; IMP-0784, IMP-0803, IMP-0824, IMP-0879, IMP-0885, IMP-0910, IMP-0911 | YES — `python3 scripts/verify-work-items.py --check --scope <ids> --at-least built` | N/A |
| 2 | script | `.engine/scripts/lib/deploy_markers.py` (new, engine) | The marker grammar and component vocabulary, moved from WS-X (3.2) | IMP-0909 | YES — exercised by both self-tests in rows 3–4 and 6 | N/A — a library |
| 3 | script | `.engine/scripts/lib/work_items.py` | deploy-record resolver: shared grammar, component literal, owed set per environment; optional `config` key; fixture repo gains a pipeline config (3.3) | IMP-0909, IMP-0910 | YES — `python3 scripts/verify-work-items.py --selftest` | N/A — a library |
| 4 | script | `.engine/scripts/verify-work-items.py` | `--scope` demotes out-of-scope drift to a note; nine new fixtures (3.4) | IMP-0911, IMP-0910 | YES — `--selftest` | already wired — SOFT `work-items` ([build config L156](config/revitalise-grant-automation-build.yml#L156)); HARD at the development gate through row 1 |
| 5 | script | `.engine/scripts/work-items.py` | Self-test fixtures and docstring use the pipeline-config labels (3.3) | IMP-0910 | YES — `python3 scripts/work-items.py --selftest` | N/A — a write tool |
| 6 | script | `.engine/scripts/verify-post-deploy-completeness.py`; `scripts/verify-post-deploy-completeness.py` | Engine copy imports the grammar from row 2, behaviour unchanged; instance copy becomes a thin wrapper (3.5) | IMP-0909 | YES — `--selftest` (13 fixtures unchanged) and the real-log audit still 5 findings, 5 true | already wired — SOFT `post-deploy-completeness` ([L141](config/revitalise-grant-automation-build.yml#L141)) |
| 7 | script | `scripts/verify-routing-reconciliation.py` + byte-identical `.engine/` copy | CHECK 3, report only (3.6) | design WS-W §W3 | YES — `--selftest` | already wired — SOFT `routing-reconciliation` ([L134](config/revitalise-grant-automation-build.yml#L134)) |
| 8 | agent | `agents/development-agent.md` | Step 5 pointer; new *Close-out* section; gate `ITEMS` lines; `| items:` on the handoff (3.7) | design §W2; IMP-0824, IMP-0885 | N/A — instruction change | N/A |
| 9 | agent | `agents/build-agent.md` | Step 8a; manifest `items` key and paragraph; On Success line and handoff (3.8) | design §W3; IMP-0912 | N/A — instruction change | N/A |
| 10 | agent | `agents/pipeline-agent.md` | *Items* section; one Stage 1 gate line; marker names the build; PM handoffs carry `items:` (3.9) | design §W3; IMP-0910 | N/A — instruction change | N/A |
| 11 | agent | `agents/test-agent.md` | Handoffs carry `items:`; failing items reopened before handing back (3.10) | design §W3 | N/A — instruction change | N/A |
| 12 | agent | `agents/lead-agent.md` | *How Delegation Happens*: carry `items:` beside `wbs:` (3.11) | design §W3 | N/A — instruction change | N/A |
| 13 | agent | `agents/WORKFLOW.md` | *Handoff Contract*: `| items:` and the hop-by-evidence table (3.12) | design §W3 | N/A — instruction change | N/A |
| 14 | agent | `agents/README.md` | *Handoff Format*: one line (3.12) | design §W3 | N/A — instruction change | N/A |
| 15 | template | `templates/dev-summary-template.md` | New *Work Items* record (numbered 12) and one checklist line (3.13) | design §W2 | N/A — template text | N/A |
| 16 | template | `templates/deployment-summary-template.md` | New *Items* section (3.13) | design §W3 | N/A — template text | N/A |
| 17 | other | `config/models.yml` + regenerate `.claude/agents/` | One `development-agent.escalate_to_strategic_when` bullet (3.14) | design §W2 | YES — `python3 scripts/generate-subagents.py --check` | N/A |
| 18 | other | the capability design, end of §W2 and §W3 | One APPLIED pointer line each, at apply time | — | N/A | N/A |

**Constraint budget:** 1 of 3 used.

### 3.1 `C-TECH-079`, exact wording

> | C-TECH-079 | **A work item moves on evidence, not on a claim, and no gate passes with an item it carried left open.** Every transition past `ready` is written by `scripts/work-items.py`, never by hand, and carries the evidence that transition names: `source-lines` for every acceptance clause plus a green `test-run` for `built`; an `artifact-manifest` whose `items` lists the item for `packaged`; a `deploy-record` for every component the target environment owes, each on a `WRITE ATTEMPTED … SUCCEEDED` marker naming that component's own command, for `deployed:<env>`; a `reviewer-verdict` in the reviewer's own words for `verified:<env>` and `done`. A development gate also requires every item its dispatch carried to be `built` or `deferred` with a reason; the test gate requires every item its handoff carried to be at least `packaged` | HARD | development-agent, test-agent | Capability design 2026-09-26, WS-W §W2 and §W3; reviewer decision S-3 (items are closed like PBIs). `IMP-0784` as corrected by `IMP-0788` (live gaps were read against a task whose evidence names a different artefact; the components with the gaps belonged to no accepted task, so nothing carried them), `IMP-0803` (a brief asked to verify a view never built), `IMP-0824` and `IMP-0885` (a screen claimed delivered twice from a paraphrase, contradicted live twice), `IMP-0879` as corrected by `IMP-0907` (DEV deploys ended at the import and the Code App was never pushed; two of the three it names), `IMP-0910` (the ledger itself accepted a push on an import line until this row's evidence rule), `IMP-0911` (a scoped check went red on another item's drift). The common mechanism: "done" meant tests passed, and nothing carried the item between agents | `python3 scripts/verify-work-items.py --check --scope <the dispatch's items> --at-least built` exits 0 at the development gate, and `--at-least packaged` at the test gate. The evidence half is enforced at write time by the tool, which refuses a transition whose evidence does not resolve, and re-checked on every build by the SOFT step `work-items`. A dispatch carrying no `items:` passes and says so |

### 3.2 `lib/deploy_markers.py` (new, engine)

Moved verbatim from [WS-X](scripts/verify-post-deploy-completeness.py#L62): `OPERATION_EVIDENCE`, `DEFAULT_DEPLOY_EVIDENCE`, `ATTEMPTED`, `OUTCOME`, `MANUAL`, `norm()`, `succeeded_markers()`, `ConfigError`, `checkable()`. Added:

- `succeeded_command(line) -> str | None`: the command half of one marker when its **first** outcome token is `SUCCEEDED`, else `None`. `succeeded_markers()` becomes a loop over it.
- `component_literals(config, env) -> dict[str, list[str]]`: `{"deploy": <the environment's deploy literals>}` plus every `(label, evidence)` pair `checkable()` returns. The labels are exactly WS-X's, `operation:<name>` and `script:<file>`, plus `deploy`.
- `all_labels(config) -> set[str]`: the union over every environment, so an unknown label can be told apart from one this environment does not owe.

No `--check` text, no `main`: it is a module under `lib/`, outside `verify-build-config.py`'s suite rung.

### 3.3 `lib/work_items.py` and `work-items.py`

- `EVIDENCE_KEYS["deploy-record"]` optional set gains `config` ([L88](.engine/scripts/lib/work_items.py#L88)). `load_context` reads `paths.pipeline_config`.
- **Resolver** ([L619](.engine/scripts/lib/work_items.py#L619)): a line resolves when `succeeded_command(line)` is not `None`, the env is in `env_of_line(line)` (unchanged: 60 of 60 success markers carry an env it reads), `contains` is in the line, **and one of `component_literals(config, env)[component]` is in the command half**. No readable pipeline config → refused, naming the key. A label unknown to every environment → refused, listing the labels the config declares.
- **Owed set** ([L520](.engine/scripts/lib/work_items.py#L520)): for `deployed:<env>`, the components owed are the item's components that `component_literals(config, env)` declares, or `["deploy"]` when none of them apply there.
- `build_fixture_repo` gains a two-environment pipeline config and `paths.pipeline_config`. Fixture component names in both self-tests move from `solution-import`/`code-app-push` to `deploy`/`operation:code-app-push`. The ledger holds no events, so nothing migrates.

### 3.4 `verify-work-items.py`

With `--scope`, an `EVIDENCE` re-resolution failure on an item **outside** the scope is reported as `NOTE — out of scope: <id> evidence drifted — <message>`. Every failure a bad write causes stays global. New fixtures, each in the failing direction too:

(a) out-of-scope drift → exit 0 and a note; (b) in-scope drift → `EVIDENCE`; (c) the IMP-0910 reproduction, a push record on an import line → `EVIDENCE`; (d) a record in each of the three marker spellings resolves; (e) a marker whose first outcome is `REFUSED` and a later `SUCCEEDED` → refused; (f) a component the environment does not declare is not owed; (g) an item whose components all fall outside the environment owes `deploy`; (h) an unknown label → refused; (i) no pipeline config → refused.

### 3.5 `verify-post-deploy-completeness.py`

The engine copy replaces its private definitions with `from deploy_markers import …`, after putting its own `lib/` on the path the way [work-items.py](.engine/scripts/work-items.py#L63) does. Its 13 fixtures run unchanged. The instance copy becomes a thin wrapper in the [`scripts/work-items.py`](scripts/work-items.py#L1) pattern, so `verify-engine-instance-split.py` reports it `WRAPPER` instead of an unsplit duplicate. **Regression proof at apply:** the real-log audit must still report 5 findings, all 5 true, WS-X's own measurement.

### 3.6 `verify-routing-reconciliation.py`, CHECK 3 (report only)

A `ROUTED_TO`, `RESUMED` or `RE-DISPATCHED` line to development-, build-, test- or pipeline-agent, dated on or after `ITEMS_REQUIRED_FROM` (the apply date), that carries a numeric `wbs:` tag and no `items:` tag is printed and counted. **It never changes the exit code.** When `logs/work-items.jsonl` does not exist the check prints one note and skips, so an instance with no ledger hears nothing. Fixtures: before the cutoff → silent; after, with `items:` → clean; after, without → one report, exit unchanged; a plan-agent line → silent; no ledger → note only.

**Corpus measured now:** 38 delivery dispatch lines since 2026-09-15 carry a numeric `wbs:` tag (development 25, pipeline 5, test 4, build 4) and none carries `items:`. With the cutoff at the apply date the check reports **0, and 0 is correct**: the convention starts then. As a can-it-fire run with the cutoff moved to 2026-09-15 it reports all 38, and each is literally true. None is a defect, because no ledger existed, which is exactly why the cutoff is the apply date.

### 3.7 `agents/development-agent.md`

**Step 5** ([L33](agents/development-agent.md#L33)) gains at its end: *"— and **close each work item the dispatch carries before you start the next** (see *Close-out: one item at a time* below)."*

**New section**, inserted after *Steps and Inline Skills* and before *Build & Pipeline Config Output* ([L253](agents/development-agent.md#L253)):

> ## Close-out: one item at a time, before the next
>
> **Added 2026-09-26 (capability design WS-W §W2; reviewer decision S-3: items are closed like
> PBIs).** Applies whenever your dispatch carries `items:<id,…>`. Each id is a work item in
> `logs/work-items.jsonl`, and its state moves only through `python3 scripts/work-items.py`, only when
> the evidence for the move resolves. **An item is closed before the next one is started.** Sub-agents
> may build in parallel; the close-out is serial and yours, including for work a sub-agent did.
>
> Per item, in the order the dispatch lists them:
>
> 1. **Re-read the item, then open its source.** `python3 scripts/work-items.py export --format json
>    --scope <id>` gives its acceptance clauses and `source_ref`. Open the source itself — the
>    spreadsheet row, the PDF page, the plan line — never a paraphrase of it (`IMP-0824`, `IMP-0885`).
>    An item still `new` moves to `ready` first; the tool refuses that without clauses and a source.
> 2. **Trace every clause to a line.** One evidence object per clause:
>    `{"kind":"source-lines","clause":<index>,"file":"<path>","line":<n>,"contains":"<one-line fragment>"}`.
>    A clause with no line is not done. Pick a fragment specific to the clause's behaviour, so it moves
>    only when the behaviour does.
> 3. **Run the item's own tests and the gates for what it touched**, each recorded as
>    `{"kind":"test-run","command":"<exact command>","exit":0,"at":"<YYYY-MM-DD>"}`. Where solution source
>    changed, `run-source-gates.py` is one of them. A red run is not evidence: fix, re-run, record the
>    green one.
> 4. **Declare what must be deployed for the item to be live:** `python3 scripts/work-items.py link <id>
>    --components <label,…> --by development-agent`, labels from the pipeline config (`deploy`,
>    `operation:<name>`, `script:<file>`; pipeline-agent → *Items*). A Code App change declared without
>    its push operation will be reported deployed on the import alone.
> 5. **Close it:** `python3 scripts/work-items.py transition <id> built --evidence <file> --by
>    development-agent`. **Only then take the next item.**
> 6. **An item you cannot finish is deferred, never skipped:** `python3 scripts/work-items.py defer <id>
>    --reason "<what blocks it, and what would unblock it>" --by development-agent`. It goes first in
>    your gate's item table, as a decision for the reviewer.
>
> Before your gate:
>
> ```bash
> python3 scripts/verify-work-items.py --check --scope <every id the dispatch carried> --at-least built ; echo "exit=$?"
> ```
>
> Exit 0 is `C-TECH-079`'s development half. Anything else is `BLOCKED`. A note naming an item
> **outside** your scope whose evidence drifted is not yours to fix; name it in your gate output.
>
> **A code-review revision that changes an item's traced lines reopens it** — `work-items.py reopen
> <id> --reason "code review: <what changed>" --by development-agent` — and steps 2 to 5 run again.
> Reopens are counted, and two escalate this agent (`config/models.yml`).
>
> **A dispatch carrying no `items:`** runs as before, and your gate says `ITEMS: none carried`. Items are
> created at intake, not here.

**Gate** ([L333-L339](agents/development-agent.md#L333)): after the `VERIFICATION SUMMARY` block, a new block:

```
ITEMS: <n> carried | built <n> | deferred <n> | scope check exit <n>
<python3 scripts/work-items.py export --format table --scope <ids>>
Deferred (needs your decision): <id — reason> | none
Out-of-scope items whose evidence drifted: <id> | none
```

**Handoff** ([L348](agents/development-agent.md#L348)) gains `| items:<ids now built>`. Deferred ids are not passed on.

### 3.8 `agents/build-agent.md`

**New step 8a**, after step 8 ([L137](agents/build-agent.md#L137)):

> 8a. **Package the work items the handoff carried** — only when it carries `items:`. Before writing
>     the manifest, keep the ids that are `built` (`python3 scripts/verify-work-items.py --check --scope
>     <ids> --at-least built` names any that are not); those go in the manifest's `items` list, and any
>     other id is left out and named in your gate output. After the manifest is written and
>     `verify-build-manifest-note.py` is green, stage it — **index only, never a commit** — and move each
>     listed item to `packaged`:
>
>     ```bash
>     git add -- "$ARTIFACT_DIR/manifest.json"
>     python3 scripts/work-items.py transition <id> packaged --evidence <file> --by build-agent
>     ```
>
>     with `{"kind":"artifact-manifest","manifest":"<$ARTIFACT_DIR>/manifest.json"}`. The tool refuses an
>     unstaged manifest, because evidence another session cannot see is not evidence (`IMP-0912`). A
>     refused transition or a held index lock does not fail the build: name the item and the refusal.

**Artifact Manifest** ([L254](agents/build-agent.md#L254)): the JSON gains `"items": ["<work-item id>", "..."],` after `"wbs"`, and this paragraph after the `wbs`/`soft_gates` bullets:

> **`items` is mandatory when the handoff carried `items:`, and `[]` otherwise.** It lists exactly the
> ids that were `built` when this build started, and it is the evidence every `packaged` transition
> cites — so an id is here only if its work is in this artifact.

**On Success** ([L378-L385](agents/build-agent.md#L378)): a line `Items packaged: <n> — <ids> | not packaged: <id — reason> | none` after `Steps not executed`, and the handoff gains `| items:<ids now packaged>`.

### 3.9 `agents/pipeline-agent.md`

**Report-back block** ([L271](agents/pipeline-agent.md#L271)): the marker line becomes `WRITE ATTEMPTED: <script> -Env <env> (build <artifact directory name>) — SUCCEEDED | FAILED <error> | REFUSED <classifier reason>`, and one sentence follows the block: *"Name the build in every `WRITE ATTEMPTED` marker — provisioning script, solution import or code push. It is what ties a write to its artifact, and a work item's deploy record resolves on it."* Measured: 5 of the 9 success markers since 2026-09-24 name no build ([example](logs/pipeline.log#L209)).

**New section**, after *(a) is derived from source, never hand-written* and before *Stage 1* ([L474](agents/pipeline-agent.md#L474)):

> ### Items: which work items reached this environment
>
> **Added 2026-09-26 (capability design WS-W §W3).** Applies when the handoff carries `items:` — the ids
> in the artifact manifest's `items` list. After this environment's writes and the post-deploy check
> in *Logging*, and before the stage line, for each id:
>
> 1. **Build one record per component the item owes here:** `{"kind":"deploy-record","env":"<env>",
>    "component":"<label>","contains":"<artifact directory name>"}`. The labels are the pipeline
>    config's: `deploy` (this environment's deploy command), `operation:<name>` and `script:<file>` (its
>    `post_deploy` entries). An item owes the labels it declares that this environment also declares,
>    or `deploy` when none of them apply here.
> 2. `python3 scripts/work-items.py transition <id> deployed:<env> --evidence <file> --by pipeline-agent`.
>    A record resolves only on a `WRITE ATTEMPTED … SUCCEEDED` marker naming the environment, the
>    artifact **and that component's own command** — an import never discharges a push (`IMP-0910`).
> 3. **A refusal is `DEPLOYMENT INCOMPLETE` for that item, not a failed deploy.** The item stays
>    `packaged`, and its row names each missing component and who owns running it. Any item reported
>    this way makes the stage word `PARTIAL`, by the rule in *Logging*: something the delivery carried
>    is still outstanding. Nothing is halted, retried or rolled back.
>
> This is the item-level half of the post-deploy check and reads the same markers with the same
> grammar (`lib/deploy_markers.py`). *Logging* asks whether each declared operation ran in this
> dispatch; this asks whether each carried item received every part of itself. **`verified:<env>` is
> never yours** — only the reviewer's own words move an item there.

**Stage 1 gate block** ([L486](agents/pipeline-agent.md#L486)): after the `Post-deploy steps:` line, `Items: <n> carried / <n> deployed:<env> / <n> DEPLOYMENT INCOMPLETE — <id: missing components, owner> | none carried`.

**After a successful DEV deploy** ([L609-L610](agents/pipeline-agent.md#L609)): both handoffs gain `| items:<ids now deployed:dev>`.

### 3.10 `agents/test-agent.md`

*Gate* ([L136](agents/test-agent.md#L136)): the `APPROVED` handoff gains `| items:<ids the build handoff carried>`. The `REVISION` handoff ([L143](agents/test-agent.md#L143)) gains `| items:<ids of the failing items>`, preceded by: *"Before handing back, reopen each failing item: `python3 scripts/work-items.py reopen <id> --reason "test report <path>: <failing case>" --by test-agent`. An item that failed its test is not done, and the board must say so."*

### 3.11 `agents/lead-agent.md`, *How Delegation Happens* only

After the paragraph at [L100-L101](agents/lead-agent.md#L100):

> **And carry the work-item ids.** Where the work is items in `logs/work-items.jsonl`, the dispatch
> prompt and the `ROUTED_TO` reason both carry `items:<id,…>` beside `wbs:` — ids only, never the items'
> text, which the receiving agent reads from the ledger. A paraphrase of an item's acceptance is how a
> screen was twice reported delivered and twice found wrong (`IMP-0824`). `verify-routing-reconciliation.py`
> reports a development, build, test or pipeline dispatch that carries `wbs:` and no `items:`.

### 3.12 `agents/WORKFLOW.md`, *Handoff Contract* only; `agents/README.md`, *Handoff Format* only

WORKFLOW.md, after the artifact example ([L617-L621](agents/WORKFLOW.md#L617)):

> Append `| items:<id,id,…>` whenever the work carries items from `logs/work-items.jsonl` — after
> `artifact:` when both are present. Ids only; the receiving agent reads each item with
> `scripts/work-items.py export --scope <ids>`. **Each agent passes on the ids it actually moved**, and
> each move needs its own evidence (`C-TECH-079`):
>
> | Hop | Moves the item to | On evidence |
> |---|---|---|
> | development-agent → build-agent | `built` | `source-lines` for every acceptance clause, plus a green `test-run` |
> | build-agent → test-agent | `packaged` | `artifact-manifest` whose `items` lists the id |
> | test-agent → pipeline-agent | (unchanged; a failing item is reopened and returned on `REVISION`) | the Test Report |
> | pipeline-agent → PM agents | `deployed:<env>` | a `deploy-record` per component the environment owes |
> | lead-agent, from the reviewer's words | `verified:<env>`, `done` | `reviewer-verdict` |
>
> ```
> HANDOFF | from:build-agent | to:test-agent | feature:my-feature | status:READY | doc:docs/development/my-feature-dev-summary.md | artifact:build/artifacts/my-feature-20250414-3/ | items:WI-0012,WI-0013
> ```

README.md, after *"Append `| artifact:<path>` when a build artifact exists."* ([L117](agents/README.md#L117)): *"Append `| items:<ids>` when the work carries work items — see `agents/WORKFLOW.md` → Handoff Contract."*

### 3.13 Templates

**`templates/dev-summary-template.md`**, a new *Work Items* record after *Verification Evidence* (numbered 11 there) and before *Findings Logged* ([L116](templates/dev-summary-template.md#L116)). It is numbered 12 so no existing section renumbers:

```
## 12. Work Items — close-out record (C-TECH-079)
<!-- One block per item the dispatch carried. "No items carried" is a valid entry. Every row is
     copied from the evidence passed to `scripts/work-items.py transition <id> built` — this is the
     reviewer's view of that evidence, never a substitute for it. -->

| Item | External id | Source (`source_ref`) | State |
|---|---|---|---|

| Item | Clause (literal, from `acceptance`) | Implemented at (`file:line`) |
|---|---|---|

| Item | Test or gate command | Exit |
|---|---|---|

Scope check: `python3 scripts/verify-work-items.py --check --scope <ids> --at-least built` → exit <n>
Deferred: <id — reason> | none
```

and in the checklist: `- [ ] Every carried work item is built or deferred, each clause traced to a line (C-TECH-079)`.

**`templates/deployment-summary-template.md`**, new section between *Verification* and *Deployment Warnings Triaged* ([L77](templates/deployment-summary-template.md#L77)):

```
## Items
<!-- One row per work item in the artifact manifest's `items` list, per environment. An item missing
     any owed component's deploy record is DEPLOYMENT INCOMPLETE: it stays `packaged` and the stage is
     PARTIAL. `verified:<env>` is recorded only from the reviewer's own words, never here. -->

| Environment | Item | External id | Components owed here | Deploy record (pipeline.log line per component) | State after this deploy |
|---|---|---|---|---|---|
| <env> | <id> | <external> | deploy, operation:<name> | L<n>, L<n> | deployed:<env> / DEPLOYMENT INCOMPLETE — missing <component>, owner <who> |
```

### 3.14 `config/models.yml`

Under `development-agent.escalate_to_strategic_when` ([L134](config/models.yml#L134)), a fourth bullet: `- An in-scope work item has been reopened two or more times (the Reopens column of python3 scripts/work-items.py export --format table --scope <items>)`. Then `python3 scripts/generate-subagents.py`, and `--check` must report current.

### 3.15 Which sections of shared files this review edits, so applies can be serialised

| File | Sections this review edits | Also edited by | Order |
|---|---|---|---|
| `agents/WORKFLOW.md` | *Handoff Contract* only | Group 1 (Learning Loop, applied); Group 2 (Processing triggers) | independent sections; anchor on the heading |
| `agents/pipeline-agent.md` | *The report-back block* marker line; new *Items* section before *Stage 1*; one line in the Stage 1 gate block; *After a successful DEV deploy* handoffs | Group 1 (*Before you dispatch ANOTHER agent*, applied); WS-X (*Logging*, applied, not touched here); **Group 2 (pre-flight, and a closing `NEXT:` line in the gate output)** | **after Group 2**: its `NEXT:` line goes at the end of the Stage 1 block, this review's `Items:` line goes mid-block, anchored on the `Post-deploy steps:` line |
| `agents/lead-agent.md` | *How Delegation Happens*, after the `wbs:` paragraph | Group 1 (routing table, applied); Group 2 (post-deploy routing); **W4–W7 sibling** (closing report, verdict recording) | anchor on the paragraph text; apply after whichever sibling lands first |
| `agents/build-agent.md` | step 8a (new); *Artifact Manifest* JSON and one paragraph; *On Success* | Group 1 (step 7b, applied) | independent |
| `agents/development-agent.md` | step 5; new *Close-out* section; *Gate* | Group 1 (*Fixing what a finding describes*, applied) | independent |
| `templates/deployment-summary-template.md` | new *Items* section before *Deployment Warnings Triaged* | **Group 2 (WS-U)** | after Group 2; anchor on the heading |
| `scripts/verify-routing-reconciliation.py` (+ engine) | new CHECK 3 only | **Group 2 (WS-U post-deploy reconciliation)** | **after Group 2**, anchored on function names, never line numbers |
| `constraints/technology/technology-constraints.md` | one new row after `C-TECH-078` | Group 1 (`C-TECH-061` amendment, applied) | independent. **Re-grep for the next free id at apply time**: two siblings are live, and `C-TECH-079` is free as of this draft |

Everything else this review touches (`lib/`, the two ledger scripts, `verify-post-deploy-completeness.py`, `test-agent.md`, `README.md`, the dev-summary template, `models.yml`) has no other editor in the plan.

---

## 4. Retirements

Nothing is retired. The design's two retirement candidates belong to WS-U and WS-T. For W2 and W3 I checked the rows nearest in subject: [C-TECH-053](constraints/technology/technology-constraints.md#L108) (report only the level executed) governs components and reports, not item state; [C-COM-005](constraints/commercial/commercial-constraints.md#L43) (a WBS status is a claim) governs contracted tasks, which the ledger references and never copies. Both stay.

> Retirement check performed: 86 live constraints (10 retired, derived by `grep '^| ~~C-'`), none currently redundant with `C-TECH-079`, because no existing row governs an item's state or its handoff.

---

## 5. Findings left unprocessed

**Deferred:** IMP-0862, IMP-0887, IMP-0891, IMP-0892, IMP-0893, IMP-0894, IMP-0895, IMP-0896, IMP-0897, IMP-0898, IMP-0899, IMP-0900, IMP-0901, IMP-0902, IMP-0916

The queue gate reports 14 `unread` entries, none about work items or handoffs. They wait for the post-deploy batch or the next defect review. I did not stamp `excluded_by` on them: three sibling dispatches are appending to the same file right now, and this line already declares their scope for the whole document. The five findings the new constraint cites (IMP-0784, IMP-0803, IMP-0824, IMP-0879, IMP-0885) are `reviewer-deferred` with their own reasons; citing them justifies a row and changes none of their dispositions.

**Two later findings correct entries the constraint cites, and both were read before the wording above was written.** IMP-0788 corrects IMP-0784 (the live gaps belonged to no accepted task, not to the task first blamed); IMP-0907 corrects IMP-0879 (one of its three deploys failed at the import and owed no push). The constraint's rationale states each finding as corrected. IMP-0788 now names this review in `reviewed_in`. IMP-0907 does not, and the queue gate will keep one reminder warning on IMP-0879 because of that: adding this review to an entry that is already `APPLIED` makes the gate read this parked draft as approved and report its own four entries as left behind. I did it, measured those four false warnings, and reverted it byte-for-byte. That conflict is logged as IMP-0916 and deferred to the next batch, since it is a queue-gate defect outside W2 and W3.

| Finding | Class | Why deferred | Revisit when |
|---|---|---|---|
| the 14 unread | various | outside WS-W2/W3 | the next post-deploy batch |
| IMP-0916 | `gate-defect` | a queue-gate defect found while drafting, outside WS-W2/W3 | the next post-deploy batch |

**Disposition of this review's own four findings:** IMP-0909, IMP-0910, IMP-0911, IMP-0912 carry `reviewed_in` naming this document and stay `NEW`, so they read `awaiting-approval`. None is a blocker and all are `observable_at: V1`, so each can be **CLOSED** at apply with an `evidence_grep` needle in the changed file.

---

## 6. Digest impact

| | Before this draft | After this draft |
|---|---|---|
| Log entries | 903 | 912 (5 by this review, of which 4 are processed here and 1 deferred; 4 by sibling dispatches in the same window) |
| Distinct lessons | 894 | 903 |
| Recurring classes | 70 | 70 |
| Digest bytes | 114,959 | 114,992 |

Validator run first, then `python3 scripts/generate-known-failure-modes.py`. Applying this review moves four entries to `APPLIED` and adds no new lesson.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-26-improvement-review-6.md

Findings processed: 4 NEW  →  6 clusters
Regression check:   3 prior changes audited, 1 classes recurred
Proposed:           1 constraints (cap 3), 6 gates/scripts, 0 skill/knowledge edits,
                    7 agent-file edits, 2 template edits, 2 other,
                    0 retirements
Altitude calls:     3 generalised from instance to class, 1 left as notes
Digest:             will regenerate — 903 lessons, 70 recurring classes
Decisions open:     D-W3-a

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied

**Phase 1 applied 2026-09-27, working tree only, no commit and no staging.** Every file was re-read immediately before its edit and each edit was anchored on heading or paragraph text, not on this draft's line numbers. Before applying, I re-ran the queue gate: no entry appended since the draft carries `corrects` against IMP-0909 to IMP-0912. Phase 1 covers everything except `.engine/scripts/lib/work_items.py` and `agents/lead-agent.md`, which the concurrent W4–W7 apply (review -5) also edits.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 1 | `C-TECH-079`, wording as in 3.1 | `constraints/technology/technology-constraints.md`, after `C-TECH-078`; the id was re-checked free at apply (live rows 86 → 87) | — |
| 2 | `lib/deploy_markers.py` | `.engine/scripts/lib/deploy_markers.py` (new) | IMP-0909 waits for phase 2, when `lib/work_items.py` imports it too |
| 4 | Scope demotion plus six fixtures in both directions. The deploy-record fixtures (c) to (i) of 3.4 land in phase 2 with the resolver they test | `.engine/scripts/verify-work-items.py` | IMP-0911 |
| 6 | Engine copy imports the shared grammar; instance copy is now a wrapper | `.engine/scripts/verify-post-deploy-completeness.py`, `scripts/verify-post-deploy-completeness.py` | — |
| 7 | Routing reconciliation **CHECK 4** (renumbered: Group 2 added its own check 3), report only, skipped with a note when there is no ledger | `scripts/verify-routing-reconciliation.py` and its byte-identical `.engine/` copy | — |
| 8 | Step 5 pointer, *Close-out* section, gate `ITEMS` block, handoff | `agents/development-agent.md` | — |
| 9 | Step 8a, manifest `items` key and paragraph, On Success line, handoff | `agents/build-agent.md` | IMP-0912 |
| 10 | Marker build name, *Items* section, Stage 1 gate line, PM handoffs | `agents/pipeline-agent.md` | — |
| 11 | Handoffs carry `items:`; failing items reopened on `REVISION` | `agents/test-agent.md` | — |
| 13 | `items:` and the hop-by-evidence table | `agents/WORKFLOW.md` → *Handoff Contract* | — |
| 14 | One line | `agents/README.md` → *Handoff Format* | — |
| 15 | *Work Items* record (numbered 12) and one checklist line | `templates/dev-summary-template.md` | — |
| 16 | *Items* section before *Deployment Warnings Triaged* | `templates/deployment-summary-template.md` | — |
| 17 | Escalation bullet; subagents regenerated (only `.claude/agents/development-agent.md` changed) | `config/models.yml`, which is a symlink into `.engine/config/`, so it lands in the engine repository | — |

**One deviation, in change 10, recorded here and in the gate output.** The approved text put the build name on the `WRITE ATTEMPTED:` line only. `verify-provisioning-report.py` pairs a `WRITE BEGUN:` line with its `WRITE ATTEMPTED:` line by the text before the dash. I executed its `operation_key()` on both forms: with the name on one line only the pair does not match, so every write would be reported as a dangling `WRITE BEGUN:`; with the name on both lines it matches. So the name goes on both lines, and the added paragraph says why. This keeps the approved intent (every marker names its build) and removes 100% of the false dangling reports the literal wording would have caused, on every write from now on.

**What was executed, and what it returned:**

- `verify-post-deploy-completeness.py --selftest`: **13 of 13**, through both the wrapper and the engine copy. The real-log audit since 2026-01-01 produced output **byte-identical** to the pre-change run: 5 findings over 49 success lines, WS-X's 5 of 5 true. Can-it-fail: a mutant of the shared module that accepts any first outcome is killed by the selftest (`run but REFUSED`).
- `verify-work-items.py --selftest`: OK, including the six new scope fixtures. `--check` on this repo: 0 items, 0 failures, 1 note (no ledger yet; correct).
- `verify-routing-reconciliation.py --selftest`: OK with six new CHECK 4 fixtures. A mutant that treats every dispatch as carrying `items:` is killed. On the real log: skipped with a note, because there is no ledger. With a scratch empty ledger it reports 0, with 173 earlier dispatches out of scope. With the cutoff moved to 2026-09-15 it reports the **38** measured at draft time. The exit code is identical with and without those 38 reports, so CHECK 4 never changes it.
- `verify-build-config.py` on the build config: exit 0. `verify-engine-instance-split.py`: exit 0, 96 scripts, 27 split/wrapper (25 after W1; this review's wrapper is one of the two added since). `verify-derived-counts.py`: 11 of 11. `verify-doc-line-links.py`: exit 0. `generate-subagents.py --check`: current. `verify-gate-input-tracking.py`: exit 0.
- Engine literal sweep of every line phase 1 added to the engine: 0 client literals (positive control: 4 hits in `scripts/kb.py`).
- `verify-improvement-log.py --check`: exit 0. IMP-0909 and IMP-0910 now warn as "left behind", because this review has closed two entries. That is expected until phase 2 closes them.

**Phase 2 (pending W4–W7):** the `lib/work_items.py` resolver, owed set and fixture repo (change 3), the `work-items.py` fixtures (change 5), the deploy-record fixtures in `verify-work-items.py`, `agents/lead-agent.md` → *How Delegation Happens* (change 12), the design pointers (change 18), closing IMP-0909 and IMP-0910, and the final digest regeneration. The digest was already regenerated once after the phase-1 closures (`--check`: current, 912 entries).

### Phase 2, applied 2026-09-27 after W4–W7 reported

The shared files were re-read immediately before editing. W4–W7 had changed `lib/work_items.py` in three places (`export_table()`, a `TRACKERS` constant, a docstring section), none of them in the evidence code, and `work-items.py`'s self-test (30 of 30). I edited around both.

| # | Change | Applied at | Entries moved to APPLIED |
|---|---|---|---|
| 3 | deploy-record resolver on the shared grammar, with the component's own literal required and the owed set per environment; optional `config` key; `Context.pipeline()` reads `paths.pipeline_config`; the fixture repo gains a pipeline config and five more marker lines; the old private literals are removed | `.engine/scripts/lib/work_items.py` | IMP-0909 (with changes 2 and 6), IMP-0910 |
| 4 (rest) | 13 new deploy-record and owed-set fixtures (3.4 cases c to i, with the failing direction of each); existing fixtures moved to the pipeline-config labels | `.engine/scripts/verify-work-items.py` | (IMP-0910) |
| 5 | Docstring evidence table and usage use the labels; fixtures moved to `deploy` / `operation:code-app-push`; one new fixture, a push claimed on the import line | `.engine/scripts/work-items.py` | (IMP-0910) |
| 12 | *How Delegation Happens*: carry `items:` beside `wbs:` | `agents/lead-agent.md` | — |
| 18 | One APPLIED pointer line each at the end of §W2 and §W3 | the capability design | — |
| hygiene | The W1 review's `design §4` link (`#L437`) was dangling because sibling edits had moved §4. **I dropped the line number rather than re-pointing it**, per `skills/how-to-report-to-the-reviewer.md` rule 1, third row: a long-lived design document cited from another document is cited by section only, because a re-pointed number rots again at the next edit | `docs/improvements/2026-09-26-improvement-review.md` | — |

**What was executed, and what it returned:**

- `work-items.py --selftest`: **31 of 31** OK (W4–W7's 30 plus one new). `verify-work-items.py --selftest`: **62 of 62** OK, 0 FAIL.
- **Can-it-fail (three mutants of the new code, each killed):**
  - resolver with the component-literal test removed: fails the IMP-0910 fixture;
  - owed set reverted to "every declared component": fails the two `test_acc` owed-set fixtures;
  - shared grammar accepting any first outcome: fails the FAILED-line and first-outcome-REFUSED fixtures.
- **Real corpus, through the real `instance.yaml` and pipeline config:**
  - the shared grammar reads **60 of 60** SUCCEEDED markers, and all 60 carry an environment the resolver reads (the old literals read 18);
  - the config yields 11 labels: `deploy`, `operation:code-app-push` and nine `script:` labels;
  - for build `…-20260925-3` in dev, a `deploy` record **resolves** and an `operation:code-app-push` record is **refused**. This is exactly the dispatch WS-X flags as having written SUCCEEDED without the push, now also refused by the ledger;
  - a push record on the push's own 2026-09-25 20:04 marker resolves;
  - a push claimed for test/acceptance is refused as not declared there.
- `verify-post-deploy-completeness.py --selftest`: **13 of 13**. Real-log audit since 2026-01-01: output **byte-identical** to the pre-change run, **5 findings, 5 true**.
- `verify-routing-reconciliation.py --selftest`: OK; instance and engine copies byte-identical.
- `verify-work-items.py --check`: 0 items, 0 failures (no ledger yet).
- `verify-engine-instance-split.py`: exit 0, 96 scripts, 27 split/wrapper.
- `verify-derived-counts.py`: 11 of 11.
- `generate-subagents.py --check`: current.
- `verify-improvement-log.py --check`: exit 0, 912 entries; no warning names IMP-0909 to IMP-0912.
- Digest `--check`: current, 912 entries.
- `verify-build-config.py`: exit 0.
- `verify-review-document.py` on this document: OK.
- `verify-doc-line-links.py` (the build's default scope): exit 0. Over `docs/improvements`: 58 dangling links, **none in any 2026-09-26 document**. All are in historical reviews the build step does not cover.
- Engine literal sweep of every phase-2 line added to engine files: 0 client literals.

**Not verified here:** nothing ran against a live environment, and no work item exists yet (the ledger is written by the W4 intake), so the loop, step 8a's `git add` and the per-item deploy record have run only in fixtures and against the real log. The level reached is V1.

