# Implementation Plan — generalising the Argelis delivery system

**For:** a Claude Code session working in the Revitalise repo (and a new engine repo it will help create).
**Goal:** turn a single-project agent system into a reusable, more deterministic multi-customer engine — by (1) separating engine from instance, (2) moving coordination and mechanical execution into declarative config + scripts, and (3) putting hard-won knowledge into a queryable store.
**Companion:** `docs/improvements/agent-system-gap-audit.md` — the audit this plan implements. Recommendation numbers below (rec N) refer to that report.

---

## How to use this plan (execution protocol — read first)

You are executing this plan **one phase at a time**, in order. The order encodes dependencies; do not skip ahead.

1. **Work on a branch.** `git switch -c generalise-engine` in the Revitalise repo before Phase 1. Commit at the end of every phase with a message naming the phase.
2. **One phase per dispatch where possible.** At the start of each phase, create a task list (`TaskCreate`) for its steps. Mark them done as you go.
3. **Run the phase's Verify block before you consider it done.** If any check is red, stop and report — do not proceed to the next phase over a failing check. This is the repo's own rule (`WORKFLOW.md` → gates).
4. **STOP at every ✋ CHECKPOINT.** These are points where a human (Xander) must approve, supply a decision, or provide a credential. Present what you did, what the Verify block showed, and the specific decision needed. Wait for his reply before continuing.
5. **Rule edits go behind `APPROVE IMPROVEMENTS`.** Edits under `agents/`, `constraints/`, `skills/`, `knowledge/` are the improvement-agent's job and are blocked for other dispatched agents by `.claude/hooks/protect-system-rules.py`. When a phase edits those, route through improvement-agent and expect the `APPROVE IMPROVEMENTS` gate.
6. **Keep the capture contract.** When a step teaches you something (a second attempt, reality contradicting a doc, a gate that fired), append to `logs/improvement-log.jsonl` per `skills/how-to-log-an-improvement.md` and regenerate the digest. The plan's own frictions belong there too.
7. **Nothing is deleted destructively.** Move-and-supersede, never `rm`. Extractions copy first, verify, then remove the original in a later step once the new location is proven.

### ✋ Decisions required from Xander before Phase 3 (gather these when you reach the checkpoints, don't guess)

- **Engine repo:** name, host (GitHub/GitLab/Azure DevOps), and whether it lives in the same OneDrive-synced tree or on local disk + remote. *(Recommendation: a real git remote, cloned to local disk — not a second OneDrive folder — so the engine isn't sync-coupled to one client.)*
- **Knowledge DB hosting** (Phase 6): confirm the start-local-then-lift path, and which lift target (Turso vs Azure) when the time comes.
- **Any credentials** (provisioning, remotes) stay reviewer-held per the repo's existing rule — the plan will stop and ask rather than embedding them.

---

## Phase 0 — Baseline & classification (no functional changes)

**Objective:** capture a green baseline so later regressions are visible, and decide on paper which files are *engine* (reusable) vs *instance* (Revitalise-specific). Nothing moves yet.

**Depends on:** nothing.

**Do:**
- [ ] Confirm clean git state; create branch `generalise-engine`.
- [ ] Run every existing gate and record the result as the baseline:
  - `python3 scripts/generate-subagents.py --check`
  - `python3 scripts/verify-improvement-log.py --check`
  - `python3 scripts/verify-routing-reconciliation.py`
  - `python3 scripts/verify-wbs-chain.py`
  - the repo's CI entrypoint if one runs locally
- [ ] Produce `docs/plans/engine-instance-classification.md`: a table of every top-level path with a column **ENGINE / INSTANCE / SPLIT**. Guidance:
  - ENGINE: `agents/` (personas + generated), `skills/`, `scripts/` (the generic verifiers/generators), `.claude/hooks/`, `config/models.yml`, `WORKFLOW.md`, the hook.
  - INSTANCE: `contract/`, `docs/` (Revitalise docs), `config/revitalise-grant-automation-*.yml`, `knowledge/domain/`, `logs/`, `provisioning/` if client-specific, `Designsystem/`, `src/`.
  - SPLIT: files that contain both — flag every place a Revitalise-specific fact sits in an otherwise-engine file (the `tst_acc`/ADR-006 topology in `WORKFLOW.md`, the slug in agent files, Power-Platform-specific assumptions inside "general" skills). These are the parameterisation targets for Phase 3.

**Verify:** all baseline gates recorded (green or with known reasons); classification doc reviewed for completeness (every top-level entry classified).

**✋ CHECKPOINT 0:** show Xander the classification table and the SPLIT list. He confirms the engine/instance boundary before anything moves.

---

## Phase 1 — Hygiene: de-fuse and de-duplicate (audit recs 2, 3, 4)

**Objective:** make operative files thin and single-sourced, so the engine/instance split in Phase 3 is clean. You cannot cleanly extract an engine while client history and duplicated rules are tangled into operative files.

**Depends on:** Phase 0.

**Do (behind `APPROVE IMPROVEMENTS`, via improvement-agent):**
- [ ] Move accreted `IMP-nnnn` narrative out of `agents/lead-agent.md`, `build-agent.md`, `pipeline-agent.md`, `development-agent.md`, `improvement-agent.md` into `docs/improvements/agent-instruction-history.md` (it already exists). Leave each operative file: the rule, plus a one-line link to the history entry. Start with `lead-agent.md` (it is on the hot path of every request).
- [ ] Pick one canonical home for each triplicated rule and replace the copies with a path reference:
  - **Session Boundaries** — canonical in `WORKFLOW.md`; `CLAUDE.md`, `lead-agent.md`, `models.yml` link to it.
  - **Improvement-capture contract** — canonical in `WORKFLOW.md`; others link.
  - **Reporting rules** — canonical in `skills/how-to-report-to-the-reviewer.md`; others link.
- [ ] Trim `CLAUDE.md`: move the "Supplied assets" and measurement-drift essays to a `docs/` reference page, keep a one-line pointer. `CLAUDE.md` is auto-loaded every turn — it should hold only per-turn operative rules.

**Verify:**
- `python3 scripts/generate-subagents.py --check` green.
- Grep each moved rule appears in exactly one canonical file (plus links).
- Word count of `lead-agent.md` materially down from ~3,744 (target: operative core + links).
- Full gate set from Phase 0 still green.

**✋ CHECKPOINT 1:** `APPROVE IMPROVEMENTS` for the rule edits. Commit.

---

## Phase 2 — Handover / compaction hook (audit rec 1)

**Objective:** stop losing mid-task context when a session compacts or a dispatch dies — the pain behind the whole "fourth/fifth case" in `WORKFLOW.md`. Orthogonal to the split, done early because every later phase benefits.

**Depends on:** Phase 1 (so the hook lands in a tidy `.claude/hooks/`). Can run in parallel with Phase 1 if needed.

**Do:**
- [ ] Add `.claude/hooks/context-preserve.py` (PreCompact): write a scoped handover snapshot (current task, doc paths, open gate, WBS ids) to `logs/handover/<session>.json`.
- [ ] Add `.claude/hooks/context-recovery.py` (PostCompact / SessionStart): read the latest handover for the scope and inject it into the next turn.
- [ ] Wire both in `.claude/settings.json` under the matching hook events. Add `logs/handover/` (gitignored).
- [ ] Give each hook a `--selftest`, matching the existing `protect-system-rules.py` convention.

**Verify:** `--selftest` passes for both; a manual PreCompact writes a snapshot; a recovery reads it back. Existing gates green.

**✋ CHECKPOINT 2:** brief Xander; commit.

---

## Phase 3 — Split engine from instance + parameterise (audit recs 10, 12)

**Objective:** the structural core. Extract the reusable engine into its own repo; turn Revitalise into a thin consumer that installs the engine and holds only its own data; move every client-specific value into one `instance.yaml`.

**Depends on:** Phases 0 (classification) and 1 (hygiene). This is the highest-risk phase — go slowly, verify at each sub-step.

**Do:**
- [ ] **3a. Create the engine repo** (per CHECKPOINT-0 decision). Initialise git, add a README describing it as the Argelis delivery engine, and a version file (`VERSION` = `0.1.0`).
- [ ] **3b. Copy** (not move yet) the ENGINE-classified files into the engine repo, preserving paths (`agents/`, `skills/`, generic `scripts/`, `.claude/hooks/`, `config/models.yml`, `WORKFLOW.md`).
- [ ] **3c. Parameterise the SPLIT files.** Create `instance.yaml` in the Revitalise repo holding: `slug`, `environment_chain` (replacing the hardcoded `tst_acc`/ADR-006 topology), `stack`, `contract_dir`, `knowledge_dir`, per-feature `build_config`/`pipeline_config` paths. Replace each hardcoded Revitalise value in the (now engine-side) files with a read from `instance.yaml`. No customer name may survive in an engine file.
- [ ] **3d. Wire the consumer.** In Revitalise, reference the engine (git submodule, or a pinned clone path, or a package install — pick per Xander's tooling). Revitalise keeps only INSTANCE files + `instance.yaml`.
- [ ] **3e. Prove parity, then remove originals.** Only after Verify passes, remove the copied-out engine files from the Revitalise repo (they now live in the engine).

**Verify:**
- Regenerate subagents from the engine against `instance.yaml`; `--check` green.
- Grep the engine repo for `revitalise`, `tst_acc`, any client name — **zero hits** outside comments/examples.
- Run a Revitalise build **dry-run** end-to-end against the extracted engine (no live deploy) — it resolves config, runs gates, produces the same artifact layout as the baseline.
- `verify-wbs-chain.py` still green on the Revitalise instance.

**✋ CHECKPOINT 3:** this is the big one — show Xander the two-repo layout, the `instance.yaml`, the zero-client-name grep, and the dry-run parity result before removing originals (3e) and before committing. Get explicit go-ahead.

---

## Phase 3f — Generalize the nine client-coupled verifiers

**Added 2026-09-09**, after Phase 3b's classification pass turned up 9 scripts that are
mostly-generic mechanism wrapped around a small amount of client-specific data (table names,
column lists, document shapes). Not folded into audit rec 9's later dead-gate cleanup — that
pass is about *retiring* things nobody uses; this is about *keeping* active, valuable gates
while relocating their reusable core, which is a different operation. Confirmed with Xander
2026-09-09: table/column *names* are client-specific, but the defect classes these scripts
catch are generic and will recur at another Power Platform client, so the mechanism belongs in
the engine.

**Objective:** for each of the 9 scripts left in Revitalise from Phase 3b, split it into (a) a
generic checking mechanism, moved to the engine, parameterised to take its client-specific facts
as input, and (b) a small instance-side config file holding those facts. The instance keeps a
thin wrapper at the original script path so every existing caller (`config/*-build.yml`,
`config/*-pipeline.yml`, other scripts, CI) keeps working unchanged.

**Depends on:** Phase 3b (done — the classification exists). Does **not** depend on Phase 3c/3d/3e
being complete — but *does* need a minimal, scoped-down piece of 3d brought forward: the engine
must be reachable from Revitalise as `.engine/` (git submodule) so the instance-side wrappers can
import the engine's generic checkers. This is added now, scoped **only** to enabling these 9
imports — it is not the full symlink-everything consumer wiring, which stays behind Checkpoint 3.

**The pattern** (confirmed against `verify-field-length-limits.py`, which already separates
`PLATFORM_LIMITS` — a cited table of Dataverse's own fixed limits, pure platform knowledge — from
one 3-line client mapping, `SETTING_ROW_COLUMNS`): the checking mechanism reads structure
(schema, flow JSON, code app manifest) and applies a rule; the only client-specific surface is
a small named table of facts the mechanism needs. That table becomes a config file; the mechanism
becomes a CLI flag away from generic.

**Do, per script** (engine mechanism / instance config / instance wrapper):

- [ ] `verify-field-length-limits.py` → engine keeps schema-reading + `PLATFORM_LIMITS` as-is;
  `SETTING_ROW_COLUMNS` moves to `config/field-length-mappings.yml`.
- [ ] `verify-field-security-coverage.py` → engine keeps the coverage-check mechanism; the
  secured-field list + rationale moves to `config/field-security-coverage.yml`.
- [ ] `verify-code-app-column-bindings.py` → engine keeps the binding-vs-security mechanism; the
  column/rationale list moves to the same config family.
- [ ] `generate-trustee-field-catalogue.py` → engine gets a generic
  `generate-restricted-field-catalogue.py` (the ADR-032 pattern: derive a restricted-field
  catalogue at build time instead of hand-typing it); `PROFILE_NAME`, `ENTITY_NAME`, and the
  column list move to `config/restricted-field-catalogue.yml`.
- [ ] `verify-flow-definition-language.py` → engine keeps the flow-JSON defect-pattern checks;
  `_ERRORLOG_TABLE` and any other named table/column move to config.
- [ ] `verify-flow-trigger-body-isolation.py` → engine keeps the isolation-check mechanism;
  `_TRIGGER_COLUMN` / `_RESULT_COLUMN_PARAMETER` move to config.
- [ ] `dump-entity-attributes.py` → already generic; moves to the engine as-is. Only its
  self-test fixture referenced real Revitalise columns — give the engine copy a synthetic
  fixture instead.
- [ ] `import-baseline.py` → engine keeps the "verify a signed baseline two independent ways"
  arithmetic cross-check; the specific document names/shape (which PDF, phase-row locations)
  move to an instance-side manifest.
- [ ] `verify-domain-invariants.py` → read in full before splitting (not yet fully read as of
  this plan revision); provisional design is a generic "undecidable/placeholder rule detector"
  in the engine + whatever Revitalise-specific rule logic remains in the instance, calling the
  engine's checker as a library.

**Wiring, so everything still works together:**
- [ ] Add the engine as a git submodule at `.engine/` in Revitalise, pinned to the commit
  containing Phase 3b's migration.
- [ ] Each instance-side wrapper script keeps the **exact original filename and path** under
  `scripts/`, so no reference in `config/revitalise-grant-automation-build.yml`,
  `config/revitalise-grant-automation-pipeline.yml`, or any other script needs to change. The
  wrapper imports the engine's generic module from `.engine/scripts/`, loads the instance config
  file, and calls the engine function — same CLI contract (args, exit codes, output format) as
  before the split.

**Verify:**
- Every one of the 9 gates, re-run against the current Revitalise solution source, produces
  **byte-identical output** to its pre-split run (same PASS/FAIL, same violation list).
  `derive-wbs-state.py`/`verify-wbs-chain.py` and the full baseline gate set from Phase 0 stay
  green.
- Grep the engine copies for `revitalise`, `rev_`, or any other client-specific literal —
  zero hits outside comments/examples.
- Grep the instance wrappers — each is short (import + config load + call), no checking logic
  duplicated locally.

**✋ CHECKPOINT 3f:** show Xander the before/after for one worked example
(`verify-field-length-limits.py`), confirm the submodule pin, and confirm the byte-identical
verify results, before treating the migration as done. Commit both repos.

---

## Phase 4 — Instance config validation (audit rec 13)

**Objective:** reject a malformed instance before any run — the deterministic gate that makes multi-customer safe.

**Depends on:** Phase 3 (`instance.yaml` exists).

**Do:**
- [ ] Add `scripts/validate-instance.py` to the engine: required fields present; environment-chain and dependency graph acyclic; gate keywords in the known set; (placeholder for) cascade vocabulary. Non-zero exit on any violation.
- [ ] Wire it as a **hard** first step in CI and in the build/pipeline configs, alongside the existing `improvement-log-check`.

**Verify:** valid `instance.yaml` → exit 0; a deliberately broken copy → exit non-zero naming the fault. CI runs it.

**✋ CHECKPOINT 4:** brief; commit.

---

## Phase 5 — Declarative flow + typed cascades (audit recs 11, 5)

**Objective:** move the delivery choreography out of prose into a validated `loop.yaml`, and replace prose re-routing with a typed, deterministic escalation map.

**Depends on:** Phases 3–4.

**Do:**
- [ ] Express the current flow (Plan→Arch→Dev→Build→Test→Pipeline) as `loops/delivery.loop.yaml`: phases, `depends_on`, gates (with `auto_condition` where a human keyword isn't legally required — e.g. Build→Test), and a `cascade_routing` map.
- [ ] Define a small typed escalation vocabulary (`SPEC_GAP`, `ARCH_GAP`, `FUNCTIONAL_FAILURE`, `STUCK_LOOP`) and route each deterministically to a target phase, replacing the prose re-routing in `lead-agent.md`/`development-agent.md`.
- [ ] Add a loader so the engine reads the flow from YAML; extend `validate-instance.py` to validate it.
- [ ] Reduce the `WORKFLOW.md` Flow section to a human-readable rendering of the YAML, not a second source of truth.

**Verify:** loaded loop reproduces the baseline flow exactly; `validate-instance.py` passes; a simulated `SPEC_GAP` routes to the RE/plan phase deterministically.

**✋ CHECKPOINT 5:** brief; commit.

---

## Phase 6 — Knowledge database (audit rec 18 + hosting)

**Objective:** put platform and failure knowledge in a queryable store, written through a typed interface, read on demand. This is the largest multi-customer reuse asset.

**Depends on:** Phase 3 (so it's clear what is shared-engine vs client-instance knowledge). Independent of Phase 5.

**Do:**
- [ ] **6a. Schema.** Create `kb.sqlite` (WAL mode) in the engine with two tables:
  - `platform_facts` (id, domain e.g. dataverse/m365, statement, verification_level, source_ref, confidence, status, superseded_by, created_at) — **shared, non-confidential** Power Platform / M365 truths.
  - `failure_modes` (id, class, description, fix, scope = engine|instance, source_ref, status, superseded_by, created_at) — the improvement/known-failure knowledge.
- [ ] **6b. Typed write interface.** `scripts/kb.py` with `add-fact`, `supersede`, `query`, `dump`. **All writes go through this — no agent runs raw SQL** (this is the reference's rule: mutations only through the typed interface). Content stays in files; the DB holds facts + pointers, never blobs.
- [ ] **6c. Hosting — start local.** Live `kb.sqlite` on **local disk, outside any OneDrive/SharePoint sync folder** (e.g. `~/.argelis-kb/kb.sqlite`). Source of truth in git is a **text dump**: `kb.py dump > kb.sql`, committed to the engine repo. Add `kb.sqlite` (binary) to `.gitignore`; restore with `sqlite3 kb.sqlite < kb.sql`.
  > **Do not place the live `.sqlite` in OneDrive, SharePoint, or Azure Files** — sync/SMB file-locking corrupts SQLite. Only the `.sql` dump is synced/committed.
- [ ] **6d. Migrate.** Load existing `logs/improvement-log.jsonl` / `known-failure-modes.md` into `failure_modes`; extract verified platform contracts (from `how-to-verify-a-platform-contract.md`, dev summaries, the A-nnn assumptions) into `platform_facts`.
- [ ] **6e. Read path.** Add a `kb.py query` the agents call for the current task, and regenerate the `known-failure-modes.md` digest **from the DB** so the existing read path keeps working.
- [ ] **6f. Governance boundary.** Shared `kb.sqlite` carries **engine + platform** knowledge only. Client-specific facts stay in that client's instance repo (its own small store). `failure_modes.scope` enforces the split.

**Verify:** `kb.py add-fact`/`query`/`supersede` round-trip; `dump` → `restore` reproduces the DB; digest regenerates from the DB and matches the prior digest's content; grep confirms no client-confidential data in the shared DB.

**✋ CHECKPOINT 6:** confirm the local-disk location and the hosting-lift decision (Turso/Azure) for later. Brief; commit the `.sql` dump.

---

## Phase 7 — Deterministic build/deploy runner (audit rec 19)

**Objective:** run the mechanical happy path as a script with zero model tokens; call a model only to diagnose a failure.

**Depends on:** Phases 4 (validation), 6 (so the runner can enforce platform facts as gates).

**Do:**
- [ ] Add `scripts/run-build.py <instance>` and `scripts/run-deploy.py <instance> <env>`: execute the config steps in order, one log line each, halt on non-zero exit, emit a structured result JSON. Enforce relevant `platform_facts` (e.g. Dataverse field-length limits) as hard checks.
- [ ] On failure, the runner emits the failing step + tool output and dispatches a **scoped diagnostic** agent (haiku or a tightly-scoped sonnet) with just that context — not the full persona or config. It also appends the failure to `kb.py` (`failure_modes`).
- [ ] Shrink `build-agent.md` / `pipeline-agent.md` from orchestrators to **diagnosers** (invoked only on the failure path). Templated summaries from the runner's structured output; model-written notes only when non-mechanical.
- [ ] Keep all human gate keywords (`APPROVE PRD`, etc.) exactly as they are — those are decisions, not execution.

**Verify:** a known-good build produces a byte-identical artifact via the runner with **no model dispatch**; a seeded failure triggers the diagnostic path and writes a `failure_modes` row; the deployment summary is produced from structured output.

**✋ CHECKPOINT 7:** brief with the token before/after (runner vs agent dispatch); commit.

---

## Phase 8 — Multi-customer scaffolding (audit recs 14, 15, 16)

**Objective:** make standing up a new client a generated, validated, least-privilege step.

**Depends on:** Phases 3–5 (engine, `instance.yaml`, validator, loop schema).

**Do:**
- [ ] `scripts/new-instance.py`: scaffold a consumer instance from the engine + a discovery questionnaire (feed from `discovery-scoping`/`project-scoping` outputs), producing a schema-valid `instance.yaml` and directory skeleton. A new client starts here, never from a copy of Revitalise.
- [ ] Per-instance least-privilege `.claude/settings.json`: each instance grants only the tools/paths/commands that client needs (its `permissions.allow` is instance-scoped).
- [ ] Engine semver + instance pinning: each instance records the engine version it targets; engine changes are additive/backward-compatible.

**Verify:** bootstrap a throwaway second instance; `validate-instance.py` passes; it runs a trivial loop end-to-end against the engine; its settings grant nothing extra.

**✋ CHECKPOINT 8:** brief; commit. (Delete the throwaway instance after.)

---

## Phase 9 — Conformance audit + promotion altitude (audit recs 7, 17)

**Objective:** a single read-only check that an instance conforms to the engine contract, and an explicit rule for which learnings promote to the shared engine vs stay in a client.

**Depends on:** Phases 3–8.

**Do:**
- [ ] `scripts/verify-system-consistency.py`: subagents current vs `models.yml`; every `ROUTED_TO` closed; no orphan docs; instance conforms to engine contract. Binary gate + a short conformance score. Wire into CI.
- [ ] Update `improvement-agent.md` / `how-to-promote-a-finding.md` with the **promotion altitude** rule: a learning is engine-level (promote to the shared engine + `platform_facts`, all clients benefit) or client-specific (stays in that instance's store). `failure_modes.scope` is the mechanical carrier.

**Verify:** the consistency check runs green on the Revitalise instance and on the Phase-8 throwaway; the promotion rule is documented and referenced from the capture contract.

**✋ CHECKPOINT 9:** final review — the engine + one clean instance + a knowledge DB + a deterministic runner all green. Merge `generalise-engine`.

---

## Rec → phase map

| Rec | Title | Phase |
|---|---|---|
| 1 | Handover/compaction hook | 2 |
| 2 | De-fuse narrative from operative files | 1 |
| 3 | De-duplicate coordination rules | 1 |
| 4 | Trim always-on CLAUDE.md | 1 |
| 5 | Typed escalation vocabulary | 5 |
| 7 | Conformance self-audit | 9 |
| 10 | Split engine from instance | 3 |
| — | Generalize the 9 client-coupled verifiers (added 2026-09-09, not in the original audit) | 3f |
| 11 | Declarative loop.yaml flow | 5 |
| 12 | Parameterise client-specific values | 3 |
| 13 | Instance config validator | 4 |
| 14 | New-client bootstrap | 8 |
| 15 | Per-instance least-privilege grants | 8 |
| 16 | Engine semver + pinning | 8 |
| 17 | Promotion altitude for learnings | 9 |
| 18 | SQLite knowledge store + hosting | 6 |
| 19 | Deterministic build/deploy runner | 7 |

## What this deliberately does NOT do

- **No hosted MCP substrate / HTTP server / tenancy in this plan.** That's the next rung (adSCAILE Stufe 2), justified only when you run multiple clients' sessions *concurrently* and file-based coordination stops being enough. The phases above are Stufe 0–1 and get you the reuse without the server. When concurrency bites, the knowledge DB (Phase 6) and the loop schema (Phase 5) are the on-ramp — lift `kb.sqlite` to Turso/Azure and wrap the engine's coordination in the substrate.
- **No determinising of judgment.** Routing varied intents and diagnosing novel failures stay with models. Determinism is for coordination, execution, and validation — "Stringenz im Kern, Flexibilität am Rand."
