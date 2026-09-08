# Engine / Instance classification — Phase 0

Part of `IMPLEMENTATION-PLAN.md` (generalise-engine branch). Read-only classification;
nothing has been moved. Baseline gate results are recorded below for comparison after
later phases.

## Baseline gate results (2026-09-08, branch `generalise-engine`, off `main`)

| Gate | Result | Notes |
|---|---|---|
| `python3 scripts/generate-subagents.py --check` | **PASS** (exit 0) | `.claude/agents` current, 18 files |
| `python3 scripts/verify-improvement-log.py --check` | **FAIL** (exit 1) | 1 blocker in state `unread`, no `deferred_reason`: **IMP-0670** (C-TECH-058 — an OPEN, closeable section-10 assumption shipped to DEV 2026-09-07 with no Deployment Summary OVERRIDE recorded). Per `agents/WORKFLOW.md` this routes to improvement-agent **immediately**, independent of this plan. Also 5 unread, 4 awaiting-approval, several stale `corrects` chains flagged as warnings. |
| `python3 scripts/verify-routing-reconciliation.py` | **FAIL** (exit 1) | 64 unreconciled dispatches (dispatched, never closed by GATE_RECEIVED/BLOCKED/STALLED) since 2026-08-31, mostly on `trustee-portal-visual-refresh` and `docusign-trigger-flow`; 1 unknown WBS tag (`wbs:6.9`, routing.log:410) naming no task in `contract/wbs.json`. |
| `python3 scripts/verify-wbs-chain.py` | **FAIL** (exit 2) | `logs/state/wbs-state.json` is stale — 21 files under `contract/`/`src/solutions/` are newer than the cached state. Self-correcting: `python3 scripts/derive-wbs-state.py` then re-run. |
| CI entrypoint (`.github/workflows/ci.yml`) | not run | Requires pushing/triggering CI; not run locally. |

**These three failures pre-date this plan and are unrelated to it** — they reflect the live delivery system's own state (an unactioned deployment blocker, a backlog of unreconciled dispatches, a stale derived-state cache). They are recorded here as the baseline only; Phase 0 does not fix them, per "no functional changes."

## Top-level path classification

| Path | Class | Notes |
|---|---|---|
| `agents/` | ENGINE | Persona files + `WORKFLOW.md`; contains Revitalise-specific narrative and the ADR-006 `tst_acc` topology → **SPLIT** target for Phase 1/3 |
| `skills/` | ENGINE | Generic how-to files; spot-check needed for Power-Platform-only assumptions embedded in "general" skills (audit's SPLIT concern) |
| `scripts/` | SPLIT | Generic verifiers/generators (`generate-subagents.py`, `verify-improvement-log.py`, model logic) are ENGINE; WBS/contract-specific scripts (`wbs-ready-set.py`, `derive-wbs-state.py`, `verify-wbs-chain.py`) are INSTANCE-shaped but reusable — needs a file-by-file pass in Phase 3 |
| `.claude/hooks/` | ENGINE | `protect-system-rules.py` is generic (paths are the 4 rule dirs, not client-specific) |
| `.claude/agents/` | ENGINE (generated) | Regenerated from `config/models.yml` by the engine's generator; not hand-edited |
| `.claude/settings.json`, `.claude/settings.local.json` | INSTANCE | Client-specific permission allowlist (pac/az/pwsh/graph) |
| `config/models.yml` | ENGINE | Model tiers + escalation triggers; no client facts found |
| `config/revitalise-grant-automation-build.yml`, `…-pipeline.yml`, `gate-baselines.json` | INSTANCE | Per-feature, per-client |
| `CLAUDE.md` | SPLIT | Header config block is instance data (project_name, domain, environments); the "Repository Layout" and "Supplied assets" essays are engine-shaped narrative that should move to docs (audit rec 4) |
| `contract/` | INSTANCE | The commercial spine: `wbs.json`, `service-agreement.json`, acceptance/invoices/change-orders — entirely Revitalise's signed engagement |
| `docs/` | INSTANCE | Revitalise SDD/TAD/dev-summary/test-report/deployment content; `docs/improvements/` is mixed — the failure-analysis/design docs are engine-shaped rationale, the per-feature improvement reviews are instance history |
| `knowledge/domain/` | INSTANCE | Revitalise/charity domain reference |
| `knowledge/technology/` | ENGINE-leaning | Platform (Dataverse/Power Platform) facts are reusable across any Power Platform client — candidate for the shared `platform_facts` store (Phase 6) |
| `logs/` | INSTANCE | All of it — `improvement-log.jsonl`, `worklog.jsonl`, `routing.log`, `known-failure-modes.md` are this engagement's history. (The *generator scripts* that produce `known-failure-modes.md` are ENGINE; the generated file is INSTANCE.) |
| `provisioning/` | SPLIT | Idempotent scripts (entra/dataverse/sharepoint/teams provisioning patterns) are largely ENGINE-shaped mechanics; the parameters they're run with (`dev-scoring-settings.json`, site names, tenant ids) are INSTANCE |
| `Designsystem/` | INSTANCE | Supplied client asset, per `CLAUDE.md` "Supplied assets" rule; owned by architect-agent |
| `src/` | INSTANCE | The actual Revitalise Power Platform solution |
| `templates/` | ENGINE | Generic document templates (SDD/TAD/dev-summary/test-report/deployment-summary/improvement-review) |
| `build/` | INSTANCE (gitignored) | Exports/artifacts |
| `README.md` | SPLIT | Likely a mix of generic "how this system works" and Revitalise-specific quickstart — needs a read in Phase 1 |
| `testResults.xml` | INSTANCE | Test run output, should probably be gitignored rather than classified |
| `node_modules/` | — | Should already be gitignored; not part of either engine or instance source |

## SPLIT files requiring line-level attention in Phase 3 (parameterisation targets)

- `agents/WORKFLOW.md` — ADR-006 `tst_acc`/environment-topology hardcode
- `agents/lead-agent.md`, other persona files — the project slug (`revitalise-grant-automation`) appears in routing examples and file-path references
- `CLAUDE.md` — the entire `⚙️ Project Configuration` YAML block is instance data by design; it's already isolated at the top, which helps
- `skills/*.md` — needs a grep pass for Power-Platform-specific assumptions inside otherwise-generic skills (not yet done; flagged as open in the audit, carried forward here)

## Open item carried into Checkpoint 0

`verify-routing-reconciliation.py` also flagged `wbs:6.9` (routing.log:410) as naming no task in `contract/wbs.json` — the same "unscoped work" class of problem the commercial constraints (C-COM-002) require routing to commercial-agent. Noting it here since this classification pass surfaced it; not actioned by this plan.
