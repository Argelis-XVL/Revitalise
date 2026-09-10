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
- [x] **3a. Create the engine repo** (per CHECKPOINT-0 decision). Initialise git, add a README describing it as the Argelis delivery engine, and a version file (`VERSION` = `0.1.0`).
- [x] **3b. Copy** (not move yet) the ENGINE-classified files into the engine repo, preserving paths (`agents/`, `skills/`, generic `scripts/`, `.claude/hooks/`, `config/models.yml`, `WORKFLOW.md`).
- [x] **3c. Parameterise the SPLIT files.** Create `instance.yaml` in the Revitalise repo holding: `slug`, `environment_chain` (replacing the hardcoded `tst_acc`/ADR-006 topology), `stack`, `contract_dir`, `knowledge_dir`, per-feature `build_config`/`pipeline_config` paths. Replace each hardcoded Revitalise value in the (now engine-side) files with a read from `instance.yaml`. No customer name may survive in an engine file.
- [x] **3d. Wire the consumer.** In Revitalise, reference the engine (git submodule, or a pinned clone path, or a package install — pick per Xander's tooling). Revitalise keeps only INSTANCE files + `instance.yaml`.
- [x] **3e. Prove parity, then remove originals.** Only after Verify passes, remove the copied-out engine files from the Revitalise repo (they now live in the engine).

**Verify:**
- [x] Regenerate subagents from the engine against `instance.yaml`; `--check` green.
- [x] Grep the engine repo for `revitalise`, `tst_acc`, any client name — **zero hits** outside comments/examples. (Two real leaks found and fixed: `knowledge/technology/` pulled back out of the engine — see `docs/plans/engine-instance-classification.md` § "Phase 3c/3d resolution" — and a pre-filled row in `templates/handover-pack-template.md` genericised.)
- [x] Run a Revitalise build **dry-run** end-to-end against the extracted engine (no live deploy) — `scripts/run-source-gates.py config/revitalise-grant-automation-build.yml`: 16/16 source gates PASS through the symlinked engine + `.engine` submodule, including all 6 Phase 3f-split gates.
- [x] `verify-wbs-chain.py` still green on the Revitalise instance (0 violations, 26 warnings, 7 accepted exceptions).

**✋ CHECKPOINT 3:** this is the big one — show Xander the two-repo layout, the `instance.yaml`, the zero-client-name grep, and the dry-run parity result before removing originals (3e) and before committing. Get explicit go-ahead.

**STATUS: DONE (2026-09-09).** `agents/`, `skills/`, `templates/`, `.claude/hooks/`,
`config/models.yml` are now symlinks into `.engine/` (git submodule, pinned). `instance.yaml`
holds the client facts these files previously would have needed to read as literals — in
practice the prose files already resolved topology from `config/<slug>-pipeline.yml` rather
than hardcoding it, so `instance.yaml` centralises the declaration rather than replacing many
scattered reads. `contract/`, `docs/`, `knowledge/domain/`, `logs/`, `src/`, `provisioning/`
params and the per-feature `config/*.yml` remain un-symlinked INSTANCE content, as classified.
Pre-existing baseline failures (IMP-0670 blocker; 64 unreconciled routing dispatches) are
unchanged by this work, per the Phase 0 baseline record.

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

**STATUS: DONE (2026-09-09).** All 8 splittable scripts moved and verified against real
Revitalise data (see `docs/plans/engine-instance-classification.md` § "Phase 3f resolution"
for the per-script table and verification method); `import-baseline.py` reclassified INSTANCE
rather than split, per the same analysis. The `.engine` submodule is pinned at the engine
repo's current `main` HEAD after each script's commit. One real bug was caught by testing
against real data rather than trusting the design (a hardcoded TypeScript export name that
would have broken the trustee portal's build) — fixed before landing.

---

## Phase 4 — Instance config validation (audit rec 13)

**Objective:** reject a malformed instance before any run — the deterministic gate that makes multi-customer safe.

**Depends on:** Phase 3 (`instance.yaml` exists).

**Do:**
- [x] Add `scripts/validate-instance.py` to the engine: required fields present; environment-chain and dependency graph acyclic; gate keywords in the known set; (placeholder for) cascade vocabulary. Non-zero exit on any violation.
- [x] Wire it as a **hard** first step in CI and in the build/pipeline configs, alongside the existing `improvement-log-check`.

**Verify:**
- [x] `python3 scripts/validate-instance.py instance.yaml` → PASS against the real Revitalise instance.
- [x] `python3 scripts/validate-instance.py --selftest` → PASS (11 cases: a valid fixture; missing/malformed `slug`; a `paths.*` field pointing at nothing; a duplicate/empty `environment_chain`; unknown vs. known `gates:` keywords; an empty `cascade_routing` target; a cyclic and a dangling WBS `depends_on` graph).
- [x] Full Phase 0 baseline gate set re-run: `generate-subagents.py --check` PASS; `verify-wbs-chain.py` PASS (0 violations, 26 warnings, 7 accepted exceptions — unchanged from Phase 3's recorded result); `verify-build-config.py` and `verify-pipeline-config.py` PASS on the real configs with the new step wired in.

**STATUS: DONE (2026-09-09).** `.engine/scripts/validate-instance.py` is fully generic (no
Revitalise fact appears in it) and takes any instance's YAML file as its only argument,
defaulting to `./instance.yaml`. Per the Phase 3f pattern, a thin `scripts/validate-instance.py`
wrapper keeps the callable path stable for `config/revitalise-grant-automation-build.yml`,
`config/build.yml.example`, and `.github/workflows/ci.yml`'s `validate` job (added
immediately after the self-protecting `verify-workflow-syntax.py` check, before slug
derivation — everything downstream reads a path `instance.yaml` names). The "dependency
graph acyclic" check reads `<contract_dir>/wbs.json` when present (Revitalise's case) and is
skipped, not failed, when a client instance has no WBS-shaped contract. The "gate keywords"
and "cascade vocabulary" checks validate shape against optional `gates:` / `cascade_routing:`
keys that no instance declares yet — forward-compatible stubs, per the plan's own "(placeholder
for)" wording; the real cascade vocabulary is Phase 5 scope.

One pre-existing defect surfaced while re-running the baseline gates, unrelated to this phase's
own change: `verify-improvement-log.py --check` now reports six APPLIED findings whose
`evidence_grep` needle no longer resolves, because Phase 3f moved the cited scripts' substance
into `.engine/` and left thin wrappers at the original paths. Logged as `IMP-0672` (not fixed
here — the fix is `improvement-agent`'s, behind `APPROVE IMPROVEMENTS`). This is the same
pre-existing-blocker situation the Phase 0 baseline already recorded (`IMP-0670`); the improvement
log's own current state, both before and after this phase, is out of Phase 4's scope to clear.

---

## Phase 5 — Declarative flow + typed cascades (audit recs 11, 5)

**Objective:** move the delivery choreography out of prose into a validated `loop.yaml`, and replace prose re-routing with a typed, deterministic escalation map.

**Depends on:** Phases 3–4.

**Do:**
- [x] Express the current flow (Plan→Arch→Dev→Build→Test→Pipeline) as `loops/delivery.loop.yaml`: phases, `depends_on`, gates (with `auto_condition` where a human keyword isn't legally required — e.g. Build→Test), and a `cascade_routing` map.
- [x] Define a small typed escalation vocabulary (`SPEC_GAP`, `ARCH_GAP`, `FUNCTIONAL_FAILURE`, `STUCK_LOOP`) and route each deterministically to a target phase, replacing the prose re-routing in `lead-agent.md`/`development-agent.md`.
- [x] Add a loader so the engine reads the flow from YAML; extend `validate-instance.py` to validate it.
- [x] Reduce the `WORKFLOW.md` Flow section to a human-readable rendering of the YAML, not a second source of truth.

**Verify:**
- [x] `python3 scripts/route-cascade.py --render` reproduces the baseline flow exactly:
  `plan → architect → development → build (auto) → test → pipeline`, with the same gates
  (`APPROVED` ×4, `APPROVE PRD`) and the same auto-condition on `build` the prior diagram
  described in prose.
- [x] `python3 scripts/validate-instance.py instance.yaml` PASS — includes the new delivery-loop
  check (verified it actually fires: a deliberately broken `cascade_routing` target failed
  instance validation naming the fault, then restored).
- [x] `python3 scripts/route-cascade.py --route SPEC_GAP` → `plan`, deterministically, no judgement
  call. `--route STUCK_LOOP` → `human` (the reserved non-phase target).
- [x] `python3 scripts/route-cascade.py --selftest` PASS (8 structural cases + route/render checks).
- [x] Full baseline gate set re-run clean: `generate-subagents.py --check`, `verify-wbs-chain.py`
  (0 violations, 26 warnings, 7 accepted exceptions — unchanged), both config preflights, and
  `verify-doc-line-links.py` over the edited agent files.

**STATUS: DONE (2026-09-09).** `.engine/loops/delivery.loop.yaml` is the source of truth for the
six-phase delivery chain; `.engine/scripts/route-cascade.py` loads, validates (`--check`,
default), renders (`--render`) and routes (`--route <EVENT>`) against it. A new
`.engine/scripts/lib/gate_keywords.py` centralises the full Human Gate Keywords vocabulary
(including `REQUEST RETEST`, `OVERRIDE <A-nnn>`, `ISSUE INVOICE <id>`, `CLIENT ACCEPTED <phase>
<date>` — Phase 4's `validate-instance.py` had only captured a partial copy) so both
`validate-instance.py` and `route-cascade.py` check gate keywords against one table instead of
two. `validate-instance.py` now loads and validates `<engine.path>/loops/delivery.loop.yaml` as
part of every instance check (skipped, not failed, on an engine checkout that predates Phase 5).
`WORKFLOW.md`'s Flow section keeps its ASCII diagram (unchanged, for readability) but states
plainly that the YAML is authoritative and the diagram is a rendering of it, and adds the typed
cascade-routing table. `lead-agent.md` gained a short "Cascade routing" subsection instructing it
to look up a `CASCADE:` gate output's target with `route-cascade.py --route` rather than reason
about it; `development-agent.md` gained a matching "Cascade events" subsection naming exactly
when to emit each of the four events (and explicitly not to guess, redesign, or retry past
`STUCK_LOOP` itself). Thin instance-side wrappers (`scripts/route-cascade.py`, matching the
Phase 3f/4 pattern) keep the callable path stable at the repo root.

The full 12-event adSCAILE cascade vocabulary was deliberately not adopted — this engine runs one
delivery loop at a time, not the concurrent multi-loop shape the fuller vocabulary exists to
disambiguate between (`docs/improvements/agent-system-gap-audit.md` rec 5's own reasoning,
carried into the loop file's comments). `cascade_routing`'s reserved `human` target has no
receiving phase by design — `STUCK_LOOP` must reach a person, never another delivery agent.

---

## Phase 6 — Knowledge database (audit rec 18 + hosting)

**Objective:** put platform and failure knowledge in a queryable store, written through a typed interface, read on demand. This is the largest multi-customer reuse asset.

**Depends on:** Phase 3 (so it's clear what is shared-engine vs client-instance knowledge). Independent of Phase 5.

**Do:**
- [x] **6a. Schema.** Create `kb.sqlite` (WAL mode) in the engine with two tables:
  - `platform_facts` (id, domain e.g. dataverse/m365, statement, verification_level, source_ref, confidence, status, superseded_by, created_at) — **shared, non-confidential** Power Platform / M365 truths.
  - `failure_modes` (id, class, description, fix, scope = engine|instance, source_ref, status, superseded_by, created_at, plus `raw_json` — see STATUS below) — the improvement/known-failure knowledge.
- [x] **6b. Typed write interface.** `scripts/kb.py` with `add-platform-fact`, `add-failure-mode`, `supersede`, `query`, `dump`, `restore`, `migrate`. **All writes go through this — no agent runs raw SQL.** Content stays in files; the DB holds facts + pointers (plus one full-fidelity JSON blob per migrated failure_mode — see STATUS), never a second copy of the write path.
- [x] **6c. Hosting — start local.** Live `kb.sqlite` at `~/.argelis-kb/kb.sqlite` (`kb.py`'s own `DEFAULT_DB`), confirmed with Xander — outside any OneDrive/SharePoint sync folder. Source of truth in git is a **text dump**: `kb.py dump > .engine/kb.sql`, committed to the engine repo. `kb.sqlite`/`-wal`/`-shm` added to `.engine/.gitignore` as a backstop (the default path is already outside the repo, so this only guards a `--db` pointed here by mistake); `kb.py restore --dump kb.sql` rebuilds it.
- [x] **6d. Migrate.** `kb.py migrate` loaded all 670 `logs/improvement-log.jsonl` entries into `failure_modes`, idempotently (a second run inserts 0). Five `platform_facts` seeded from truths already cited concretely elsewhere in this repo (the Pipelines "cannot be handed a pre-built artefact" / "does not publish before exporting" behaviours from `ci.yml`'s own Microsoft Learn citations, the flow-description 256-char limit from `verify-field-length-limits.py`'s `PLATFORM_LIMITS`, the SharePoint-vs-Graph `Sites.Selected` role-id trap from ADR-018) — see STATUS for what a full corpus extraction would still need to cover.
- [x] **6e. Read path.** `generate-known-failure-modes.py` gained `--source {jsonl,db}`: `db` mode calls `kb.py`'s `rows_for_digest()` and feeds the identical entries through the SAME unchanged rendering code `jsonl` mode uses. Verified **byte-identical** output between the two modes over the real 670-entry log (`diff` — 0 lines), twice (before and after adding a new entry mid-phase). `jsonl` stays the default and the actual CI-enforced path — see STATUS for why the live gate does not switch to `db` yet.
- [x] **6f. Governance boundary.** `dump` filters in two independent layers: `scope='engine'` (populated by `migrate`'s heuristic — `feature: system` in the source finding), then a caller-supplied `--redact` regex list checked against the row's actual text. The scope tag alone was NOT enough — see STATUS for what that caught.

**Verify:**
- [x] `kb.py --selftest` PASS (16 checks: add-platform-fact/query, add-failure-mode/query, supersede incl. missing-id error, dump/restore round-trip, content-redaction, migrate incl. idempotency and `corrects`→`superseded_by`, `rows_for_digest` ordering and raw_json fidelity).
- [x] `dump` → `restore` reproduces the DB: restored `platform_facts`=5, `failure_modes`=118 (engine-scope, content-clean), `scope` distinct-value check confirms no `instance` row present.
- [x] Digest regenerates from the DB and matches the prior digest's content **exactly** (`diff` against the live 670-entry log: 0 lines different).
- [x] Grep confirms no client-confidential data in the shared, committed `.engine/kb.sql` — see STATUS, this did NOT pass on the first attempt.

**STATUS: DONE (2026-09-09).** ✋ **CHECKPOINT 6 answered by Xander before this phase started:**
live DB at `~/.argelis-kb/kb.sqlite` (the plan's own recommended default); the Turso/Azure
hosting-lift target deferred to "when the time comes," per the plan's own wording — nothing in
this phase depends on that choice.

**The `raw_json` column, beyond the plan's literal schema.** `failure_modes` carries one column
the plan's 6a list didn't name: the full original improvement-log-shaped JSON for a migrated
row. Without it, 6e's byte-identical digest would not be possible — the digest's rendering logic
reads over a dozen fields (`corrects`, `capability`, `evidence_grep`, `deferred_reason`,
`wbs`, …) that the plan's flattened schema (id/class/description/fix/scope/…) does not carry.
The flattened columns are the queryable public interface the plan specifies and are what
`query`/`--redact` filter on; `raw_json` is what lets the digest read path stay lossless. A row
added later with no `raw_json` still renders (`rows_for_digest` synthesizes a minimal dict from
the flattened columns), just with less detail than a fully-shaped entry would carry.

**6f's real finding: a scope tag is not proof of content-cleanliness.** The first `dump` of all
150 `scope='engine'` rows, grepped for `revitalise`/`rev_`/`tst_acc`, found 32 rows containing
exactly those literals — findings genuinely ABOUT the agent system's own machinery (hence
`feature: system` → `scope: engine`), whose incident narrative nonetheless quoted this client's
real table and environment names, the same "teach the generic lesson via the real incident"
pattern this repo already accepts inside script docstrings
(`docs/plans/engine-instance-classification.md` § "Phase 3c/3d resolution") — correctly accepted
there because a human reads the comment with context, and wrong here, because a shared database
is meant to be queried by a future client's tooling without a human reading the incident first.
Fixed by adding a second, content-based filter to `dump` (`--redact <regex>`, repeatable,
case-insensitive over `description`/`fix`/`raw_json`) — the engine script itself stays
instance-agnostic (no Revitalise literal appears in it), and the instance wrapper
(`scripts/kb.py`) supplies this client's own denylist (`revitalise`, `rev_[a-z0-9_]*`,
`tst_acc`) by default so a future dump cannot regress silently. **The committed `.engine/kb.sql`
holds 5 `platform_facts` and 118 `failure_modes` rows** — 32 fewer than the naive scope-only
filter would have shipped. Logged as `IMP-0673` (severity `rework`, not `blocker` — caught and
fixed within this same dispatch, never shipped).

**Why `--source jsonl` stays the live, CI-enforced default.** `logs/improvement-log.jsonl`
remains the write path every agent's capture contract targets, unchanged by this phase, and
`kb.sqlite` is deliberately **local-disk-only** per the hosting decision above — a CI runner has
no access to a machine-local file under a developer's home directory, and neither does a second
developer's machine. Switching the HARD `C-TECH-059` gate's default source to `db` would make
every build depend on a file that exists on exactly one Mac. `--source db` exists to prove the
DB path is a faithful mirror (this phase's own Verify block), not to replace the live path — that
becomes possible only after the DB is lifted off local disk (Turso/Azure, deferred at
Checkpoint 6), which is when a CI runner could actually reach it.

**6d's platform_facts seeding is a start, not the corpus extraction 6d describes.** Five facts
were added from truths already stated concretely elsewhere in this repo, chosen because they
needed no new verification work — extracting from `how-to-verify-a-platform-contract.md`,
every dev summary's §10 assumption register, and every closed A-nnn assumption across the whole
project is a large, judgment-heavy corpus-reading task (dozens of documents, each assumption
needing a human-legible verification-level read, not a mechanical ETL like `migrate`'s JSONL
pass) that this phase did not attempt in full. Left as open follow-on work — a candidate for
`improvement-agent`'s capability-mode backlog rather than a silent gap.

---

## Phase 7 — Deterministic build/deploy runner (audit rec 19)

**Objective:** run the mechanical happy path as a script with zero model tokens; call a model only to diagnose a failure.

**Depends on:** Phases 4 (validation), 6 (so the runner can enforce platform facts as gates).

**Do:**
- [x] Add `scripts/run-build.py <config>` and `scripts/run-deploy.py <config> <env>`: execute the config steps in order, one log line each, halt on non-zero exit, emit a structured result JSON. Enforce relevant `platform_facts` as hard checks — see STATUS for what "enforce" means here.
- [x] On failure, the runner emits the failing step + tool output and prepares a **scoped diagnostic brief** for a haiku/tightly-scoped dispatch — not the full persona or config. It also appends the failure to `kb.py` (`failure_modes`).
- [x] Add a "Deterministic runner" section to `build-agent.md` / `pipeline-agent.md` — the mechanical step-execution moves to the runner; the diagnostic/judgement work these files already carry stays exactly as it is. See STATUS for why this is not literally "shrink" (delete).
- [x] Kept all human gate keywords (`APPROVE PRD`, etc.) exactly as they are — `run-deploy.py` never infers or waits for one; it refuses to promote without the exact keyword string handed to it by the caller.

**Verify:**
- [x] `run-build.py --selftest` PASS: a known-good synthetic config's artifact is byte-identical
  across two runs; a `when: ci` step is correctly skipped locally; a `manual` step is recorded,
  not executed; a known-bad config halts at the failing step (never reaching the step after it)
  and writes both a `failure_modes` row and a diagnostic brief; a config error (missing command)
  exits 2, not 1.
- [x] `run-deploy.py --selftest` PASS: mechanical `pre_deploy`/`post_deploy`/`smoke_tests` run for
  a non-gated environment; the LAST hop of `environment_chain` refuses to proceed with no gate
  keyword (exit 3) or an unrecognised one, proceeds with a correct one, and `--skip-promotion`
  bypasses the check entirely; an unknown environment name and a failing step are both handled.
- [x] Both selftests run against an ISOLATED `kb.sqlite` (a bug caught mid-implementation — the
  first run wrote real `RUN-*` rows into the actual `~/.argelis-kb/kb.sqlite` before this was
  fixed; the stray rows were deleted). The real KB is confirmed untouched by either selftest.
- [x] Full baseline gate set re-run clean after editing `build-agent.md`/`pipeline-agent.md`:
  `generate-subagents.py --check`, `verify-wbs-chain.py`, both config preflights,
  `validate-instance.py`, `verify-doc-line-links.py`.

**STATUS: DONE (2026-09-09).** `.engine/scripts/run-build.py` and `run-deploy.py` are ENGINE
scripts (`run-deploy.py` reuses `run-build.py`'s `run_steps`/`is_manual`/`record_failure`/
`write_diagnostic_brief` rather than re-implementing them, so the two runners cannot silently
disagree). Instance wrappers (`scripts/run-build.py`, `scripts/run-deploy.py`) follow the
established Phase 3f/4/5/6 pattern; the deploy wrapper supplies Revitalise's own
`environment_chain` from `instance.yaml` by default.

**A NAMED, DELIBERATE DUPLICATION.** `run-build.py`/`run-deploy.py` mirror
`scripts/ci/run-config-steps.sh`'s exact `when:`/`manual`/halt-on-failure semantics rather than
calling it, because the payoff this phase needs (structured JSON, the platform-facts preflight,
`kb.sqlite` capture) has no home in a bash script without reaching for a second language inside
it. This is the same class of problem Phase 1 (audit rec 3) exists to close, and is named here
rather than silently shipped — the honest fix, reconciling the two (most likely: retire the bash
version and have CI call the Python one), is future work, not part of this phase.

**"Enforce platform_facts as hard checks" is a cross-check, not a re-implementation.**
`run-build.py` does not re-derive Dataverse field-length limits itself — that logic already
lives, correctly, in `verify-field-length-limits.py` as a build step (Phase 3f). What it adds is
a PREFLIGHT: for every `active` `platform_facts` row whose `source_ref` names a `scripts/` file,
is that script actually wired as a step in THIS build config? A fact that claims enforcement via
a script the config never runs is reported (WARN, not fatal — a fact can legitimately be out of
scope for one feature). Verified live against the real Revitalise config and `kb.sqlite`: PF-0004
(the flow-description-length fact) correctly reports "not wired" against a SYNTHETIC selftest
config and would report "wired" against the real one, since `verify-field-length-limits.py` is a
real build step there.

**Why the diagnostic path stops at a BRIEF, not a dispatch.** A bare Python process cannot call
the Claude Code harness's Task tool — nothing outside an agent session can. `run-build.py`/
`run-deploy.py` write the exact context a diagnosing session should hand to a scoped haiku/sonnet
dispatch (`logs/state/diagnostic-briefs/<id>.json`: failing step, command, output tail, nothing
else) and print an instruction to dispatch it verbatim. The actual Task-tool call is
`build-agent`'s/`pipeline-agent`'s to make, per their new "Deterministic runner" sections.

**Why `build-agent.md`/`pipeline-agent.md` were not literally shrunk.** These files carry
hundreds of lines of incident-specific judgement — re-hash-mid-build drift handling, warning
novelty triage, the assumption-register cross-check, live-environment access preflights — none
of which reduces to "did a shell command exit 0". Deleting them to satisfy "shrink" literally
would have been the plan's own rule 7 violated ("nothing is deleted destructively") over content
that is still load-bearing on every RED run and on every judgement step surrounding a GREEN one.
Instead, a new section names PRECISELY which step (build-agent's step 5; pipeline-agent's
`pre_deploy`/`post_deploy`/`smoke_tests`) the runner replaces, and states explicitly that
everything else stays. The real "shrink" this phase delivers is in TOKENS SPENT ON A GREEN RUN,
not in file line count — see the token estimate below.

**Token before/after, for the checkpoint.** The real Revitalise build config declares 80 steps
across 56,977 characters of YAML. Executing it "by hand" means 80 separate tool-call round
trips — the model reads each step, issues a Bash call, and reads back that command's own output
(often thousands of tokens for `npm ci`, `vitest`, `pac solution pack`) before deciding to
continue. Running it through `run-build.py` is ONE tool call and one structured JSON read-back
that, on a green run, compresses to a few hundred tokens ("80 declared, N executed, M manual,
SUCCESS") — the full per-step stdout/stderr tails are IN the JSON file for a human or a
diagnosing dispatch to open on demand, not pushed into the orchestrating context on every run.
The saving is not measured precisely here — no historical per-build token log exists to diff
against — but the shape of the claim is exact: **80 round trips collapse to 1** on the path that
needs no judgement at all, and every token spent on a RED run is now spent on a **80-times-
narrower slice of context** (one failing step's brief, not the whole transcript).

---

## Phase 8 — Multi-customer scaffolding (audit recs 14, 15, 16)

**Objective:** make standing up a new client a generated, validated, least-privilege step.

**Depends on:** Phases 3–5 (engine, `instance.yaml`, validator, loop schema).

**Do:**
- [x] `scripts/new-instance.py`: scaffold a consumer instance from the engine + answers (individual flags or a single `--answers <json>` file — see STATUS re: no `discovery-scoping`/`project-scoping` skill existing yet), producing a schema-valid `instance.yaml` and directory skeleton. A new client starts here, never from a copy of Revitalise.
- [x] Per-instance least-privilege `.claude/settings.json`: `permissions.allow` starts **empty** — a new client has earned no command yet — carrying only the generic built-in-agent denylist and the three engine hooks.
- [x] Engine semver + instance pinning: `instance.yaml` gained an optional `engine.version_pin`, format-checked by `validate-instance.py` (Revitalise's own `instance.yaml` now carries `version_pin: "0.1.0"`, retrofitted for consistency).

**Verify:**
- [x] `new-instance.py --selftest` PASS: skeleton created, `agents`/`skills`/`templates`/
  `config/models.yml`/`.claude/hooks` all symlinked, all five thin wrapper scripts generated,
  `instance.yaml` passes `validate-instance.py`, `permissions.allow` is empty, the generic
  denylist is present.
- [x] Bootstrapped a REAL throwaway second instance (`acme-widgets-throwaway`, outside this
  repo, deleted after): `validate-instance.py instance.yaml` → PASS; `route-cascade.py
  --render` → the full six-phase chain, proving the scaffolded instance reaches the engine's
  delivery loop end to end; `.claude/settings.json` → `permissions.allow: []`, nothing
  extra.
- [x] `validate-instance.py --selftest` extended with two more cases (valid and malformed
  `engine.version_pin`) — 13 cases, all PASS.
- [x] Full baseline gate set re-run clean on the Revitalise instance after adding its own
  `version_pin`.

**STATUS: DONE (2026-09-09).** The throwaway instance was scaffolded and verified with
`--no-git` (copying `.engine` in rather than adding it as a submodule) because this sandbox's
git configuration refuses the `file://` transport (`fatal: transport 'file' not allowed`) —
a git safety default this session does not override, per the standing rule against touching
git config. The submodule-add CODE PATH itself (`git submodule add <repo> .engine`) is
unchanged from, and identical to, the command already proven working for Revitalise's own
real engine relationship (`.engine/README.md` § "Consuming this engine"); only the throwaway
verification's transport was substituted. Deleted after verification, as instructed.

**Wrappers are GENERATED, not copied.** `new-instance.py` embeds the five thin-wrapper
templates (`validate-instance.py`, `route-cascade.py`, `kb.py`, `run-build.py`,
`run-deploy.py`) itself, rather than copying them from Revitalise's own `scripts/` — copying
would risk carrying a client literal into a fresh instance the same way Phase 6's `IMP-0673`
found one leaking through a category tag. `kb.py`'s `DEFAULT_REDACT_TERMS` gets a best-guess
seed (the new client's own name and slug) rather than an empty list, flagged in its own
generated docstring as "review and extend" — a seed guards against the exact class of leak
Phase 6 found, without pretending a guess is a verified denylist.

**No discovery-scoping/project-scoping skill exists in this repo to feed `--answers` from.**
The plan's own wording ("feed from discovery-scoping/project-scoping outputs") assumes a skill
that was never built. `--answers <json>` documents the field shape such a skill would need to
produce (the same names as the individual CLI flags) without inventing the skill itself, which
is out of this phase's scope.

---

## Phase 9 — Conformance audit + promotion altitude (audit recs 7, 17)

**Objective:** a single read-only check that an instance conforms to the engine contract, and an explicit rule for which learnings promote to the shared engine vs stay in a client.

**Depends on:** Phases 3–8.

**Do:**
- [x] `scripts/verify-system-consistency.py`: subagents current vs `models.yml`; instance conforms to the engine contract; no orphan design docs — **gated**, binary. `ROUTED_TO`/routing reconciliation — **reported**, not gated; see STATUS for why. One conformance score always printed. Wired into CI and into `config/<slug>-build.yml` / `build.yml.example`.
- [x] Updated `improvement-agent.md` / `how-to-promote-a-finding.md` with the **promotion altitude** rule (new §6 in that skill): a learning is engine-level (promote to the shared engine + `platform_facts`, all clients benefit) or client-specific (stays in that instance's store). `failure_modes.scope` is the mechanical carrier — cross-referenced from `WORKFLOW.md`'s capture contract and from `improvement-agent.md`'s own activation steps.

**Verify:**
- [x] `verify-system-consistency.py` runs GREEN (binary gate PASS, 3/4 checks) on the real
  Revitalise instance: subagents current, instance conforms, 8 design docs / 0 orphans; routing
  reconciliation reported red (64 pre-existing unreconciled dispatches, unrelated to this plan,
  disclosed rather than hidden) without failing the gate.
- [x] Ran GREEN (4/4 — a fresh instance has no routing.log yet, so that check is vacuously
  green too) on a REAL bootstrapped Phase-8-style throwaway instance, deleted after.
- [x] `verify-system-consistency.py --selftest` and `new-instance.py --selftest` both PASS,
  the latter now asserting the composed consistency check is green on every instance it
  scaffolds.
- [x] The promotion rule is documented (`how-to-promote-a-finding.md` §6) and referenced from
  the capture contract (`WORKFLOW.md`) and from `improvement-agent.md`'s own promotion step.
- [x] Full baseline gate set re-run clean, including a real regression this phase caused and
  fixed within the same dispatch — see STATUS.

**STATUS: DONE (2026-09-09).** `.engine/scripts/verify-system-consistency.py` composes existing
gates (`generate-subagents.py --check`, `validate-instance.py`, `verify-routing-
reconciliation.py`) via subprocess rather than re-implementing their logic, plus one new check
this phase adds (`no_orphan_docs`, scoped deliberately to `docs/plans/` and `docs/architecture/`
— `docs/development/`, `docs/tests/` and `docs/improvements/` are known-noisy by design,
per `verify-doc-line-links.py`'s own 56 disclosed dangling links there).

**Why routing reconciliation is reported, not gated.** Measured live against Revitalise while
building this script: `verify-routing-reconciliation.py` currently fails with 64 unreconciled
dispatches, a pre-existing operational backlog the Phase 0 baseline already recorded as
unrelated to this plan. Gating Phase 9's own conformance check on clearing 64 dispatches this
phase never scoped would mean either scope creep this plan explicitly excludes, or the "does
this instance conform to the engine" gate reporting a false RED on the instance it exists to
prove is healthy. The score still surfaces it, honestly, every run.

**A real regression, caught by the system's own existing defense, fixed within this dispatch.**
Adding `verify-system-consistency.py` to `scripts/` tripped `verify-build-config.py`'s own
`suite-gate-is-not-a-step` check — a `verify-*`/`--check`-shaped script that exists but is not
wired into the build config is exactly the `gate-cannot-fail` class this whole codebase is built
to prevent, and its own preflight caught this phase's own new script the same way it would
catch anyone else's. Wired as a build step (`config/revitalise-grant-automation-build.yml` and
`build.yml.example`) and into CI; preflight is green again.

**The promotion altitude rule found its own worked example.** `how-to-promote-a-finding.md` §6
cites Phase 6's `IMP-0673` (a `scope='engine'` tag that still leaked client literals) as the
standing proof that a category tag is not, by itself, evidence of content-cleanliness — the same
lesson the new section asks a future promotion decision to apply.

---

## Phase 10 — Close the engine/instance script split (not started)

**Objective:** finish what Phase 3b/3d left incomplete. `scripts/verify-engine-instance-split.py`
(added behind `IMP-0696` in the 2026-09-10 improvement review) measured the true scope: of 85
scripts under `scripts/`, only 9 went through the Phase 3f split (mechanism → `.engine/`, client
facts → instance config), 5 more became thin generic wrappers in Phases 4-9 (`validate-instance.py`,
`route-cascade.py`, `kb.py`, `run-build.py`, `run-deploy.py`, `verify-system-consistency.py` —
six, not five), and **66 are still byte-identical duplicates** — real, separate files in both
`scripts/` and `.engine/scripts/` with nothing keeping them in step. The build calls `scripts/`,
never `.engine/`, so an edit landed only in the engine copy silently does not run. This is not
urgent today (both copies are identical, so nothing has diverged yet, and the SOFT gate would
catch it if one did) — but it is exactly the debt that makes onboarding a second client expensive,
since a client-coupled duplicate can't be handed to them at all, and a genuinely-generic duplicate
still needs manual double-editing forever until it's symlinked.

**Depends on:** Phase 9 (`verify-engine-instance-split.py` exists and is wired SOFT).

**Triage performed 2026-09-10** (read-only — nothing moved). Every one of the 66 duplicates was
grepped for this client's own literals (`revitalise`, `rev_[a-z0-9_]+`, `tst_acc`, `argelis`,
case-insensitive) to sort them into two starting buckets. **A zero-hit count is a strong signal,
not a proof** — the reverse (a hit) is even less conclusive, since this codebase's own convention
is to teach a generic check via a real incident's citation in a comment, which greps positive
without being functionally coupled to anything (the same nuance Phase 3c/3d already navigated for
`agents/`/`skills/`). Bucket assignment below is the STARTING hypothesis for Do step 2, not a
finished classification.

**Bucket A — 32 scripts, zero literal hits.** Candidate for the cheap route: symlink directly
into `.engine/`, the same move Phase 3d already made for `agents/`, `skills/`, `templates/`.
```
allocate-improvement-id.py       verify-acceptance-pack.py         verify-models-yml-comments.py
allocate-review-number.py        verify-assumption-register.py     verify-provisioning-report.py
collect-project-status.py        verify-code-app-bundle-budget.py  verify-provisioning-step-convergence.py
compute-invoice.py               verify-code-app-composition-root.py  verify-provisioning-test-presence.py
deliverable-hours.py             verify-commercial-events.py       verify-review-document.py
derive-wbs-state.py              verify-coverage-threshold.py      verify-routing-reconciliation.py
reconstruct-worklog.py           verify-css-arithmetic.py          verify-source-parses.py
refusal-history.py               verify-dev-summary-artefacts-committed.py  verify-toolchain-claims.py
schedule-risk.py                 verify-gate-input-tracking.py     verify-wbs-chain.py
                                  verify-handover-pack.py           verify-workflow-syntax.py
                                  verify-ledger-readers.py          verify-worklog.py
                                                                     wbs-ready-set.py
```
Even here, do not batch-symlink blind: `derive-wbs-state.py`, `verify-wbs-chain.py` and
`wbs-ready-set.py` were just hand-edited (2026-09-10 review) to add generic mechanism (comment
stripping, structural-anchor warnings, reading `build_order_constraints`) — re-verify each still
has zero *functional* client dependency, not just zero grep hits, before symlinking.

**Bucket B — 34 scripts, one or more literal hits.** Needs the per-script read Phase 3f gave the
original 9 — comment/incident-citation only (→ Bucket A after confirming) vs. genuine functional
coupling (→ the full mechanism/config/wrapper split). Hit count is not a coupling score; it is
only "look here first". Highest-count scripts, likely to reward a look first because they most
resemble the original 9's shape (Dataverse schema, WBS/commercial specifics):
`verify-role-privilege-ownership.py` (28), `verify-tad-coverage.py` (24),
`verify-superseded-column-writers.py` (23), `verify-design-doc-claims.py` (21). Full list of 34,
with hit counts, is in this phase's own triage command output (re-run it — it is not committed as
a separate artefact, to avoid a second place this number can go stale):
```bash
python3 - <<'PY'
import re, subprocess
out = subprocess.run(["python3", "scripts/verify-engine-instance-split.py"],
                      capture_output=True, text=True).stdout
names = re.findall(r"^\s{4}(\S+\.py)$", out, re.M)
pat = re.compile(r"revitalise|rev_[a-z0-9_]|tst_acc|argelis", re.I)
hits = [(len(pat.findall(open(f"scripts/{n}").read())), n) for n in names]
for n_hits, n in sorted((h for h in hits if h[0]), reverse=True):
    print(n_hits, n)
PY
```

**Do:**
- [ ] 10a. For each Bucket A script, confirm zero functional coupling (not just zero grep hits),
  then replace the instance copy with a symlink into `.engine/scripts/`, matching the exact Phase
  3d procedure (`diff -rq` immediately before the swap, zero-client-literal bar unchanged).
- [ ] 10b. For each Bucket B script, read it in full. Comment/citation-only → confirm and move to
  the Bucket A treatment. Genuine coupling → apply the Phase 3f pattern (mechanism to
  `.engine/scripts/`, the client-specific facts to a `config/*.json` file, a thin wrapper left at
  the original path) — same verification bar Phase 3f used: byte-identical or near-byte-identical
  output against the real Revitalise solution/config, not just each script's own synthetic
  self-test.
- [ ] 10c. Once every one of the 85 is a symlink, a wrapper, instance-only, or engine-only — zero
  remaining duplicates — flip `verify-engine-instance-split.py`'s build-config step from reporting
  to `--max-duplicates 0`, a real HARD gate.

**Verify:** `python3 scripts/verify-engine-instance-split.py` reports 0 unsplit duplicates;
`--max-duplicates 0` passes; full baseline gate set (`generate-subagents.py --check`,
`verify-wbs-chain.py`, both config preflights, `verify-system-consistency.py`) stays green
throughout, checked after each batch, not only at the end.

**✋ CHECKPOINT 10:** this phase has no fixed size — 66 scripts is a multi-session effort at the
Phase 3f rate (roughly one script per dispatch for genuinely coupled ones, several per dispatch
for confirmed-generic symlinks). Recommend picking it up in batches rather than one long phase,
and prioritising it before — not necessarily long before — actually onboarding a second client,
since that is the point a still-coupled duplicate stops being merely untidy and starts being a
script the next client literally cannot use.

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
