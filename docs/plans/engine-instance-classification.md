# Engine / Instance classification — Phase 0

Part of [docs/improvements/IMPLEMENTATION-PLAN.md](../improvements/IMPLEMENTATION-PLAN.md) (generalise-engine branch), which implements [docs/improvements/agent-system-gap-audit.md](../improvements/agent-system-gap-audit.md). Read-only classification;
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

## Phase 3f resolution (2026-09-09): the 9 client-coupled scripts

Nine `scripts/*.py` were held back from the Phase 3b engine copy pending a mechanism/data
split decision. Resolved as follows — see `docs/improvements/IMPLEMENTATION-PLAN.md` Phase 3f
for the design and per-script verification:

| Script | Resolution |
|---|---|
| `dump-entity-attributes.py` | Split — engine copy already fully generic, only its self-test was instance-coupled |
| `verify-field-length-limits.py` | Split — mechanism to engine, one column-mapping config to instance |
| `verify-field-security-coverage.py` | Split — mechanism (Dataverse platform knowledge) to engine, one exemption config to instance |
| `verify-code-app-column-bindings.py` | Split — forbidden-column derivation to engine, required-columns config to instance |
| `generate-trustee-field-catalogue.py` | Split — renamed `generate-restricted-field-catalogue.py` in the engine, this app's field manifest (incl. the exported TypeScript names, which are NOT free to rename) to instance config |
| `verify-domain-invariants.py` | Split — register-consistency mechanism (fully generic sensitive-data governance) to engine, register path + build-step name to instance |
| `verify-flow-definition-language.py` | Split — checks 1-4/6 moved with zero config (pure platform facts); check 5 config-driven; check 7's mechanism moved, its live dated exceptions stayed as instance config |
| `verify-flow-trigger-body-isolation.py` | Split — trigger isolation + PII-taint-fixpoint analysis to engine; the one ADR-039 architecture-approved regex exemption became a pluggable, instance-declared exempt-template mechanism |
| `import-baseline.py` | **Not split — reclassified INSTANCE.** After a full read, ~90% specific narrative about one signed contract (exact filenames, a negotiated hour gap with the reviewer's exact quoted words, a warranty-terms reconciliation full of specific document versions). The genuinely reusable parts (PDF extraction, WBS parsing, sha256 pinning, the two-way arithmetic cross-check) were already in `scripts/lib/pmsources.py`, copied to the engine in Phase 3b. Forcing a further split would mean building a templating system for arbitrary future contract clauses to serve a script whose entire value is its record of one negotiation. |

Every split script was verified against the real Revitalise solution/flows/config, not just its
own synthetic self-test: byte-identical or near-byte-identical output (differences limited to
dropped `IMP-nnnn`/`C-nnn` citation text, disclosed per script), with `verify-flow-trigger-body-isolation.py` byte-identical outright. One real bug was caught this way — a hardcoded TypeScript export name that would have broken the trustee portal's actual build — fixed before landing.

## Phase 3c/3d resolution (2026-09-09): instance.yaml + symlink wiring

`instance.yaml` created at the repo root — the single declaration of slug, stack,
`environment_chain` ([dev, tst_acc, prd]), contract/knowledge paths and per-feature config
paths. The ENGINE-classified top-level items (`agents/`, `skills/`, `templates/`,
`.claude/hooks/`, `config/models.yml`) were already byte-identical to their `.engine/`
copies (confirmed by `diff -rq` immediately before the swap), so they were replaced with
symlinks into `.engine/` rather than kept as duplicated copies — this **is** Phase 3d/3e's
"Revitalise keeps only INSTANCE files" for these five items. `agents/WORKFLOW.md` moved with
`agents/` as part of the same directory symlink.

Two real defects were caught by the Phase 3 checkpoint's own verify bar ("grep the engine for
`revitalise`/`tst_acc`/any client name — zero hits outside comments/examples") and fixed in the
engine repo before this was called done:

1. **`knowledge/technology/*.md`** was copied to the engine verbatim in Phase 3b before being
   generalised. 9 of its 13 files contain real Revitalise Dataverse schema
   (`rev_application`, `rev_grantadministration`, `rev_roundstatisticsrequest`, etc.), not
   platform-generic facts — this had already been flagged in this document as "ENGINE-leaning
   ... candidate for the shared `platform_facts` store (Phase 6)," not cleared for the
   engine's zero-client-name bar. Pulled back out of the engine (`knowledge/` removed from
   `.engine`); Revitalise's own `knowledge/technology/` is unchanged and un-symlinked, and every
   agent/skill reference to that path still resolves there. Proper genericisation stays Phase 6
   scope.
2. **`templates/handover-pack-template.md`** had a Monitoring-and-Alerting table row pre-filled
   with Revitalise's actual error-log table and failure-alert flow names, not a placeholder — a
   fresh client filling in this template would have seen live Revitalise data. Replaced with
   `<error log table>` / `<failure alert flow>` placeholders, consistent with the template's
   other fill-in-the-blank rows.

The remaining ~218 grep hits for `rev_`/`revitalise`/`tst_acc` across the engine's `scripts/`,
`skills/`, `agents/` are inside docstrings, `WHY THIS EXISTS` incident narratives, and synthetic
test fixtures (`rev_thing`, `rev_a`, `rev_b` as generic placeholder names) — the accepted
"comments/examples" exception, and the established pattern throughout this codebase of teaching
a generic check via the real incident that motivated it. Not actioned as out of Phase 3 scope.

**Verify (re-run after the fix):**
- `python3 scripts/generate-subagents.py --check` — PASS through the symlinks.
- `python3 scripts/verify-wbs-chain.py` — PASS (0 violations; the Phase 0 staleness is gone
  now that `derive-wbs-state.py` was re-run).
- `verify-improvement-log.py` / `verify-routing-reconciliation.py` — same pre-existing
  failures as the Phase 0 baseline (IMP-0670 blocker; the 64 unreconciled dispatches),
  unchanged by this work.

**Not done (deliberately, still behind Checkpoint 3):** `contract/`, `docs/`,
`knowledge/domain/`, `logs/`, `src/`, `provisioning/` parameters, and `config/<slug>-*.yml`
remain un-symlinked INSTANCE content, as classified. No engine file was hand-edited in the
Revitalise repo — all fixes landed in the engine repo and were pulled in via the submodule pin.

## Open item carried into Checkpoint 0

`verify-routing-reconciliation.py` also flagged `wbs:6.9` (routing.log:410) as naming no task in `contract/wbs.json` — the same "unscoped work" class of problem the commercial constraints (C-COM-002) require routing to commercial-agent. Noting it here since this classification pass surfaced it; not actioned by this plan.
