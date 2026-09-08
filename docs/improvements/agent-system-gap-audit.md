# Gap Audit — Revitalise agent system vs. the adSCAILE reference framework

**Scope:** read-only comparison of the running Claude Code system in `…/Repository/Revitalise` (orchestrator + subagents + skills + scripts) against the documented reference framework **adSCAILE 1.2** (adesso SE), supplied as seven `.docx` role transcripts plus the 49-page `adSCAILE-Manual_v1.0.pdf`.
**Date:** 2026-09-05. **Nothing was modified.** No agent, skill, or script was run against either system.

A note on the asymmetry, kept throughout: adSCAILE is *written intent for a reusable framework other teams adopt*; the Revitalise system is *one running implementation for one signed engagement*. Several places where they differ are not the implementation falling short — they are a single-project build correctly declining framework machinery it doesn't yet need. I flag those as **Divergence**, not **Gap**, and say which way I think the call should go.

One honest limit up front: the reference is a distilled wiki export and two diagrams (a sequence diagram p.12, a loop-overview p.20) whose content is lost to text extraction. Where the manual points at material it doesn't contain ("Loop-Integration-Guide §1", full schemas, the dashboard), I mark the point aspirational rather than treating it as a specification.

---

## 1. Executive summary

**The single biggest structural difference** is where coordination lives. adSCAILE's thesis (Designprinzip 9, "Determinismus statt Heuristik"; Prinzip 3, "Koordination liegt in deterministischem, prüfbarem Code, nicht in Prompts", Manual p.40, 42) is to move task-readiness, gate evaluation, and escalation routing **out of prompts into a substrate** — an MCP server holding a task graph, gates, and typed cascades in SQLite. In the Revitalise system that coordination lives in **markdown prose** (`CLAUDE.md` + `agents/WORKFLOW.md` + `agents/lead-agent.md`) interpreted by an LLM router. That is a legitimate choice — the manual explicitly sanctions "Stufe 0, dateibasiert" with no substrate (p.26) — but the system has visibly hit the exact pains the substrate exists to remove, and is paying for them in prose and round-trips.

The five gaps that matter most:

1. **No handover / compaction-survival hook (High).** The reference's single cheapest upgrade is `context-preserve.sh` (PreCompact) + `context-recovery.sh` (PostCompact); the manual says this alone often justifies moving off file-only mode (p.26). Your only hook is a write-guard (`.claude/hooks/protect-system-rules.py`). Meanwhile the largest section of `WORKFLOW.md` — the "fourth case / fifth case" saga about dispatches that die or stall and lose mid-task context across sessions — is precisely the failure a handover hook is designed to prevent. You have the pain; the reference has the fix; it is one hook pair.

2. **Operative rules and forensic history are fused in the same files (High, tokens + routing clarity).** adSCAILE separates *design-time rationale* (append-only ADRs, decision-log) from *runtime operative rules* (the `loop.yaml`), deliberately (Manual p.16, p.45). Your `agents/lead-agent.md` is ~3,700 words, of which the actual routing table is ~30 lines; the rest is accreted `IMP-nnnn` post-mortem narrative that a **haiku-tier** router must parse on every session. You already have the right home for that narrative — `docs/improvements/agent-instruction-history.md` — but the story is *also* inlined in the operative file.

3. **Coordination rules are triplicated across four files (Medium, tokens).** The Session-Boundaries rule, the improvement-capture contract, and the reporting rules each appear in `CLAUDE.md`, `WORKFLOW.md`, and `lead-agent.md` (and models.yml for the first). `CLAUDE.md` is auto-loaded every turn (~3.2K tokens); lead-agent then loads WORKFLOW + the digest + its own file (~14K tokens) before routing one request. Your own `models.yml` "Token Rules" forbid exactly this; the practice violates the stated intent.

4. **No typed escalation channel (Medium).** adSCAILE has 12 typed cascade events (SPEC_GAP, ARCH_GAP, FUNCTIONAL_FAILURE, STUCK_LOOP…) that route deterministically to a receiving phase (Manual p.14). Your cross-stage escalation (development-agent → architect/RE) is handled as prose re-routing by lead-agent, which is the heuristic path the reference structurally excludes as an anti-pattern (p.43).

5. **Serial-only delivery, and it's serial because there's no substrate to make parallel safe (Medium).** The reference parallelises via workers that share no state and coordinate only through the server (Manual p.9–13; arc42 runs "12 chapters parallel", p.22). Your flow is strictly linear, worktree isolation is disabled (the dir is empty) and lead-agent rungs 2 and 5 actively forbid concurrent dispatch over shared uncommitted state after it caused defects (IMP-0400, IMP-0531/0532). The serialization is a rational response to *not having* the substrate's isolation model.

**Where you already meet or beat the reference intent:**

- **The self-learning loop is an edge the manual has no equivalent for.** `improvement-log.jsonl` → `improvement-agent` (opus, behind `APPROVE IMPROVEMENTS`) → durable edits to `agents/`/`constraints/`/`skills/` → regenerated `known-failure-modes.md` read at activation. adSCAILE records decisions (ADRs, decision-log) but describes no automated loop that feeds failures back into agent instructions.
- **The commercial spine is entirely outside the reference's scope and is a real edge for a consultancy.** WBS-task-id as the join key across delivery/PM/commercial/acceptance, hours-only discipline, evidence-derived task state, warranty clock (`WORKFLOW.md` → Commercial Loop, `verify-wbs-chain.py`). adSCAILE is purely an engineering framework.
- **Model-to-task fit is explicit and single-sourced** (`config/models.yml` → generated `.claude/agents/*.md` pins; lead/config=haiku, delivery=sonnet, improvement=opus) with documented escalation triggers. The reference is deliberately model-agnostic; your concrete pinning is more actionable, not less.
- **You found and use the *actual* enforcement seam.** lead-agent rung 6 + `settings.json permissions.deny` (measured live, with a control) and the PreToolUse rule-dir guard (with fixture-dump proof) are empirical where the manual's capability-enforcement (P13) is asserted and, for local stdio, admitted to be default-off (p.43).

---

## 2. Reference model (distilled from adSCAILE 1.2)

### 2.1 Principles and structure, with source

**Mission / values.** "Der Mensch orchestriert, die KI setzt um" (Manual p.4, "Kompakt"). Five pillars (p.5): agentic loops, two contexts (greenfield/brownfield), dual claim of rigour + flexibility resolved by *"Flexibilität am Rand, Stringenz im Kern"*, composable toolkit, one shared versioned knowledge base. Seven values as an "A before B" manifesto (Tabelle 1, p.5) — most relevant here: **deterministic coordination before prompt-driven guessing**, **explicit checkable contracts before implicit convention**, **errors as visible data before silent failure**, **human orchestrates, AI implements before full autonomy**.

**Substrate (the coordination core).** Optional MCP server, SQLite/WAL, single source of truth (Manual p.8–9). Mechanism split — *"Tools mutieren den Zustand. Resources zeigen den Zustand. Hooks erzwingen Invarianten"* (p.10). Worker/substrate model: workers know nothing of each other, coordinate only through the server; heartbeat ≤60s or the session is dead and reservations free (p.10). Eleven inherited features incl. declarative loops, deterministic task graph, gates, cascades, boundary contracts, KB/artifact registry, decision-log, handover/resume, audit, resilience/idempotency, capability enforcement (p.8–9).

**Task graph.** `pending → ready → claimed → in_progress → done/failed/abandoned`; a task is `ready` only when all predecessors are `done`, computed in SQL on every `task.complete`, no separate scheduler; atomic claim; cross-loop `depends_on_task_ids` (Manual p.13).

**Gates.** Declarative approval points, `auto` (deterministic `auto_condition`, e.g. `no_open_cascades`) or `human`; a successor phase starts only when predecessor gates are approved/overridden; `gate.override` **forces** a decision-log entry — no silent override (Manual p.13–14).

**Cascades (typed escalation).** 12 valid emit types (SPEC_GAP, ARCH_GAP, INFEASIBILITY, MERGE_CONFLICT, INTEGRATION_FAILURE, STUCK_LOOP, FUNCTIONAL_FAILURE, DEPENDENCY_VULN, MISSING_DEPENDENCY, SECURITY_FAILURE, WORKTREE_UNAVAILABLE, DETERMINISM_BROKEN); routed by a `cascade_routing` map in the loop YAML, intra- or cross-loop; events stay open until the receiver resolves them; **no push — consumers poll** (Manual p.14).

**Boundary contracts.** `from/to/produces/consumes` YAML validated by the substrate before a successor phase starts; a loop without one is isolated (Manual p.14).

**Knowledge & audit.** KB holds pointers + SHA-256 + supersede chain, never blobs; `artifact.latest` answers "current version of X" deterministically (p.15–16). Append-only immutable audit (before/after per mutation) + decision-log (rationale + supersede), explicitly separated from git ADRs — audit answers *what/who/when*, decision-log answers *why* (p.16–17).

**Handover / resilience.** `context-preserve.sh` (PreCompact) writes a snapshot via `handover.write`; `context-recovery.sh` reloads it post-compaction (p.16). Idempotency keys, retry budgets → STUCK_LOOP, heartbeats, auto-snapshots, resume tokens (p.17).

**Maturity ladder** (Manual p.26): **BASE** (file-only, substrate optional) · **MIDDLE** (one loop on substrate, stdio) · **TIP** (multiple loops, HTTP, cross-loop deps, dashboard). Rule of thumb: substrate pays off at multiple parallel sessions/loops; *"Der Compaction-Schutz allein rechtfertigt oft den Schritt zu Stufe 1."*

**Six loop families** (Manual p.18–25): RE, Architecture (arc42, `architecture_v6`), Development (TDD, the template loop), Testing (risk→coverage→design→automate→execute→triage→release), PM (meta-orchestrator — **PoC only, on Cowork**), Deploy (**PoC only, on opencode**).

**13 design principles** (Manual p.40–43): agnostic; workflows attached via YAML not code; central MCP orchestration in deterministic code not prompts; central versioned KB; validation at every seam; YAML contracts for gates/escalation; hook-validated outputs; observability/audit by default; **determinism over heuristic, fail-closed in the hot path**; **errors as data not exceptions**; resilience/idempotency; additive backward-compatible evolution; least-privilege capability enforcement. Explicitly excludes seven anti-patterns incl. *tool ordering by few-shot prompt*, *routing by confidence score*, *silent failure*, *all agents can call all tools* (p.43).

The seven `.docx` files are spoken role intros (RE/Anke, Architecture/Frank, Design/Dennis, Development/Immo, Testing/Julian, PM/Elisabeth, Intro/Andrea). They add two things the PDF states more precisely: the **human-in-the-loop is confined to named gates** (Design: "exactly two places where a human decides — framework at the start, screen-by-screen release at the end", `adSCAILE_DESIGN-en.docx`), and **the substrate carries only escalations and reports out of a loop; everything else stays in the loop** (`adSCAILE_PROJECTMANAGEMENT-en.docx`, `adSCAILE_INTRO-en.docx`).

### 2.2 Ambiguities / aspirational parts of the reference

- **The substrate is optional, not prescribed.** "Brauche ich zwingend den MCP-Server? Nein" (FAQ p.44). So "adopt a substrate" is *not* what the reference tells you to do — it tells you to grow into one when multi-session/multi-loop consistency is needed. Judging your file-based system as "missing the substrate" would misread the reference.
- **PM-Loop and Deploy-Loop are PoC** (p.22–23, FAQ p.44). The "meta-orchestrator PM" is aspirational; a lean Cowork PoC exists.
- **Capability enforcement is default-off for stdio** and there is "kein automatischer Transport-Branch im Code" (P13, p.43). In the common local mode, the reference's own least-privilege guarantee is largely unenforced.
- **Pointer-level references.** Full loop schema, Loopsmith, dashboard, the two figures — named, not specified in the manual. Treated as aspirational.
- **No quantitative targets.** The reference makes *no* speed, token, or cost claims. On dimensions (a) speed and (c) tokens it offers principles (determinism, on-demand resources, handover), not numbers — so my deltas there compare *mechanisms*, not benchmarks.

---

## 3. My inventory (Revitalise, real paths)

### 3.1 Agents — two layers

`.claude/agents/*.md` are thin **generated** Claude Code subagents (frontmatter pins model; body is a generated stub) produced by `scripts/generate-subagents.py` from `config/models.yml`. `agents/*.md` are the fat **persona / knowledge** files the dispatched agent reads. Model tiers resolve via `models.yml`: `mechanical=haiku`, `standard=sonnet`, `strategic=opus`.

| Agent | Tier (model) | Purpose | Persona size (words) |
|---|---|---|---|
| lead-agent | mechanical (haiku) | Route request to a delivery/PM agent; answer general questions | **3,744** |
| plan-agent | standard (sonnet) | SDD (business/functional, no tech) | 1,350 |
| architect-agent | standard (sonnet) | TAD (arc42-ish) from SDD | 2,413 |
| development-agent | standard (sonnet) | Implement per TAD; **fans out** to sub-agents | 3,556 |
| — data/backend/frontend/automation/identity/m365 | standard (sonnet) | Per-feature specialist slices | (generated stubs) |
| — config-agent | mechanical (haiku) | Env config/flags, rule-following | (generated stub) |
| test-agent | standard (sonnet) | Validate build vs SDD/TAD; Test Report | 1,778 |
| build-agent | standard (sonnet) | Package per `<slug>-build.yml` | 4,047 |
| pipeline-agent | standard (sonnet) | Deploy through env chain | 4,811 |
| pm-agent | standard (sonnet) | Plan of record, WBS state from evidence | 1,011 |
| commercial-agent | standard (sonnet) | Hours, change orders, invoices | 1,272 |
| acceptance-agent | standard (sonnet) | Phase acceptance, warranty clock, handover | 1,078 |
| improvement-agent | **strategic (opus)** | The only agent that edits the rules, behind `APPROVE IMPROVEMENTS` | **6,057** |

18 generated subagents total; 12 persona files + `WORKFLOW.md` (4,019 w) + `README.md`.

### 3.2 Skills (23, flat `.md` read by path, not Claude Code SKILL.md folders)

Loaded on demand at point of use. Biggest: `how-to-verify-a-platform-contract.md` (5,655 w), `how-to-log-an-improvement.md` (3,989), `how-to-promote-a-finding.md` (2,269), `how-to-report-to-the-reviewer.md` (2,050), `accessibility-checklist.md` (1,739), `how-to-intake-external-documents.md` (1,575), `how-to-apply-constraints.md` (1,564). These are genuinely lazy-loaded, which is the right pattern.

### 3.3 Slash commands, MCP, hooks, permissions, config

- **Slash commands:** none (`.claude/commands` absent).
- **MCP servers:** **no `.mcp.json` in the repo.** The system defines no project MCP server — the coordination substrate is git + scripts + logs, not a server.
- **Hooks:** one — `.claude/hooks/protect-system-rules.py` (PreToolUse on Edit/Write/NotebookEdit/MultiEdit). Denies a *dispatched* subagent (not the root session) writing under `agents/`/`constraints/`/`skills/`/`knowledge/` unless it is improvement-agent. Documents four honest limits (root session exempt; not a sandbox; only 4 dirs; write-tools only, not Bash).
- **Permissions** (`.claude/settings.json`): `deny` blocks the four generic agents `Agent(claude|general-purpose|Explore|Plan)`; `allow` is a specific bash/WebFetch allowlist. `settings.local.json` adds `pac`/`az`/`pwsh`/graph allowances.
- **Model config:** `config/models.yml` (25 KB) — single source of truth, tiers + `escalate_to_strategic_when`/`de_escalate_to_mechanical_when`, prompt-caching notes, token-volume table. Regenerated into subagent frontmatter by `scripts/generate-subagents.py`.
- **Deterministic gate layer:** **75 python scripts** in `scripts/`; per-feature `config/revitalise-grant-automation-build.yml` (**57 KB**) and `…-pipeline.yml` (**151 KB**); `gate-baselines.json` (16 KB). This is where the real "coordination in code" lives.
- **Worktrees:** `.claude/worktrees/` exists but is **empty** — worktree isolation is deliberately unused (lead-agent rung 2).

### 3.4 How routing actually works

Human → lead-agent (haiku). lead-agent reads `WORKFLOW.md` + `known-failure-modes.md` on activation, then: (1) matches intent against a markdown routing table; (2) for delivery work, resolves the request to WBS task ids via `scripts/wbs-ready-set.py` — unquoted scope goes to commercial-agent *first*; (3) dispatches via the Task tool `subagent_type:<name>`, applying a `model:` override if an escalation condition is met; (4) logs a `ROUTED_TO` line that must be closed by a terminal line. Gates are **keywords a human types** (`APPROVED`, `APPROVE PRD`, `APPROVE IMPROVEMENTS`, `CLIENT ACCEPTED …`). Handoffs are a fixed 5-field line + doc path, never pasted content. Max 3 revision cycles per gate, then `BLOCKED`.

---

## 4. Dimension-by-dimension comparison

### (a) Speed of delivery — **Gap (Medium)** + one **Edge**

- **Reference:** parallelism is native — the task graph makes independent tasks `ready` together, workers claim concurrently, HTTP transport enables true multi-session parallelism, cross-loop deps resolve in one SQL query (Manual p.13, p.26–27); arc42 runs 12 chapters in parallel (p.22). Isolation is structural: workers share no state, so parallel work can't corrupt shared files.
- **Mine:** strictly serial Plan→Arch→Dev→Build→Test→Pipeline (`WORKFLOW.md` → Flow). The only fan-out is development-agent → data/backend/frontend/… sub-agents. Worktree isolation is off; lead-agent rungs 2 & 5 forbid concurrent dispatch over shared uncommitted working-tree state, after IMP-0400 (a worktree that couldn't see uncommitted state) and IMP-0531/0532 (a build gate tripping on a file a concurrent dispatch was still editing).
- **Delta:** the reference removes the *cause* of your serialization — shared mutable state — by construction. Your real critical-path cost is not the linear stages (human `APPROVED` gates serialize both systems equally) but the **round-trips from silent dispatch deaths** (`WORKFLOW.md` "fourth/fifth case"): a stalled cross-session dispatch forces manual live-state reconciliation. The substrate's heartbeat + atomic claim + task-state make that a query, not an investigation. Adopting the *isolation discipline* (commit between hops, or a substrate-style claim) is the mechanism that would let you parallelise safely. **Edge:** your model-tier routing means the serial chain runs each stage on the cheapest adequate model — a cost-speed lever the agnostic reference doesn't specify.

### (b) Length & cost of reviews — **Edge (rigor)** + **Gap (Medium, narrative weight)**

- **Reference:** reviews are gates + audit; depth is risk-scaled *declaratively* — Testing derives coverage targets from `risk_class` (PRAM-lite, Manual p.23); `adscaile-audit` yields a binary gate + 0–100 conformance score, CI-able (p.26). Rationale for a decision lives in the decision-log/ADRs, **not** in the operative loop.
- **Mine:** review depth is genuinely risk-matched and, per-artefact, *sharper* than anything the manual details — verification levels V2–V6 (`WORKFLOW.md`), mutation-testing a "structurally impossible" bug before believing the claim, and a real-browser check for rendered SVG geometry because "the arithmetic checks out" is not evidence (`how-to-review-code.md`, IMP-0415/0590). That's an edge.
- **Delta:** the cost isn't the checks — it's **verbosity that doesn't change a decision, fused into the operative files.** adSCAILE keeps *why* (ADR/decision-log) separate from *what to do now* (loop.yaml). You inline every `IMP-nnnn` post-mortem into the agent file that the agent must execute: lead-agent's operative content is a ~30-line table wrapped in ~3,700 words of history. Reviews/instructions are heavy relative to the work because the reader re-derives context every time. Diff-based vs whole-file isn't the issue (your gates already run against sources); **narrative-vs-operative separation is.**

### (c) Token usage — **Gap (High)**

- **Reference:** coordination state lives in the substrate and is read **on demand** as resources (`tasks://ready`, `gates://waiting`, polled), not carried in context (Manual p.10, p.40). Agent files are thin (name/description/tools + focused instructions, p.28). Rationale is out-of-context in ADRs.
- **Mine:** `CLAUDE.md` (~3.2K tokens) auto-loads every turn and itself contains long essays (the "Supplied assets / measurement-drift" block). lead-agent then loads `WORKFLOW.md` (~5.3K) + the digest + its own file (~5K) — **14K tokens to route one request on a haiku agent.** Skills *are* lazy-loaded (good). Biggest estimated sinks, in order: **(1)** accreted IMP-narrative across lead/build/pipeline/development/improvement persona files (20K+ words of history that is operative-file resident); **(2)** triplication — Session-Boundaries appears in `CLAUDE.md` + `WORKFLOW.md` + `lead-agent.md` + `models.yml`; improvement-capture in three; reporting rules in three; **(3)** `CLAUDE.md`'s always-on prose. *(Estimates — I did not instrument token counts; sizes are word counts × ~1.33.)*
- **Delta:** your own `models.yml` "Token Rules" (front-load stable context, never re-read, reference by path) state the reference's intent exactly; the giant narrative files break it. The fix is the reference's own separation, and you already have the destination file (`docs/improvements/agent-instruction-history.md`).

### (d) Architecture — **Parity/Edge on model-fit; Gap on missing handover layer + coordination diffusion**

- **Reference:** three clean mechanism layers (tools/resources/hooks) + substrate/worker split + declarative composable loops; one coordination point; additive evolution (Manual p.10, p.40–43).
- **Mine:** orchestrator (haiku) → delivery (sonnet) → dev sub-specialists → business spine (pm/commercial/acceptance) → improvement-agent (opus) → 75 scripts as the deterministic gate layer → 1 guard hook. **Model-to-task fit is strong and single-sourced** — an edge over the agnostic reference. The two-agent-directory pattern (generated thin pins from `models.yml` + fat personas) is sound.
- **Delta / gaps:** (1) **No handover/compaction layer** — the reference's standard resilience hook is absent; this is the same gap as (a)'s round-trip cost, seen structurally. (2) **Coordination logic is diffuse** — spread across `CLAUDE.md`/`WORKFLOW.md`/`lead-agent.md`/`models.yml` with overlap, which is a soft single-source violation (the reference keeps the loop definition in one inspectable, diffable, validatable YAML, p.9). (3) **Complexity SPOFs:** the 151 KB `pipeline.yml` and 75 scripts are your "coordination in code" (which the reference praises) but concentrated in artefacts no one can eyeball; the reference would push much of that into declarative loop YAML with `auto_condition` gates. This is parity-of-intent, divergence-of-form — and for a Power Platform delivery the script-and-YAML form is defensible.

### (e) Agent routing — **Divergence (Medium)** + **Edge**

- **Reference:** routing is deterministic — `cascade_routing` maps and DAG deps in YAML; confidence-score routing and few-shot tool ordering are named anti-patterns and structurally excluded (Manual p.43).
- **Mine:** an LLM (haiku) matches a markdown table, then resolves to WBS ids via script. Triggers are mostly distinct; double-firing risk is low (linear flow). Two soft spots: the catch-all "General project question → answer directly" leaves an LLM to decide *whether* a request needs routing (the heuristic the reference warns against), and cross-stage escalation is prose re-routing rather than a typed channel. **Edge:** you already found and *mechanically closed* one silent mis-route class — generic built-in agents — via `permissions.deny`, measured with a control (rung 6). That's the reference's "all agents can call all tools" anti-pattern, caught empirically.
- **Delta:** for varied consulting inputs, some router flexibility is warranted, so a full YAML router would be over-fitting. But the WBS-id resolution is your deterministic backbone — leaning on it harder (route by resolved id, shrink the prose the router reads) moves you toward the reference's determinism where it's cheap, without giving up the flexibility you actually need.

### (f) Optimisation synthesis

Covered as recommendations in §5. In short: two high-value quick wins (handover hook; de-fuse narrative from operative files), two token-hygiene wins (de-duplicate; trim always-on `CLAUDE.md`), one structural option (typed escalation vocabulary), and one "not yet" (a substrate — only if you go multi-session/multi-project).

---

## 5. Prioritised recommendations

Sorted by impact-to-effort. "Source" says whether the idea is the reference's or original to this audit. Effort S/M/L.

| # | Recommendation | Source | Dimension(s) | Expected impact | Effort | Risk | Files to touch |
|---|---|---|---|---|---|---|---|
| 1 | **Add a PreCompact/PostCompact handover hook** — snapshot mid-task context to a KB file on compaction, reload after. Adapt the reference's `context-preserve.sh`/`context-recovery.sh`. | adSCAILE (Manual p.16, p.26) | Speed, Architecture | High (kills the silent-death round-trips) | S | Low | new `.claude/hooks/*`, `.claude/settings.json`, a `logs/handover/` dir |
| 2 | **Move accreted `IMP-nnnn` narrative out of operative agent files** into `docs/improvements/agent-instruction-history.md`; leave each agent file the operative rule + a one-line link. | adSCAILE ADR/decision-log split (p.16) + your own IMP-0059 intent | Tokens, Reviews, Routing | High (lead-agent ~3,700→~800 w; every dispatch lighter) | M | Low (behind `APPROVE IMPROVEMENTS`) | `agents/lead-agent.md`, `build-agent.md`, `pipeline-agent.md`, `development-agent.md`, `improvement-agent.md` |
| 3 | **De-duplicate Session-Boundaries / improvement-capture / reporting** to one canonical home each; the other files link by path. | Original (enforces your `models.yml` Token Rules) | Tokens, Architecture | Med-High | M | Low | `CLAUDE.md`, `WORKFLOW.md`, `lead-agent.md`, `models.yml` |
| 4 | **Trim always-on `CLAUDE.md`** — the "Supplied assets" and measurement-drift essays are reference material, not per-turn operative rules; move to a doc, keep a pointer. | adSCAILE on-demand resources (p.10) | Tokens | Med (every turn) | S | Low | `CLAUDE.md`, `docs/` |
| 5 | **Introduce a small typed escalation vocabulary** (SPEC_GAP, ARCH_GAP, FUNCTIONAL_FAILURE, STUCK_LOOP) that maps deterministically to a re-route target, replacing prose re-routing in the delivery chain. | adSCAILE cascades (p.14) | Routing, Speed | Med | M | Med (needs a routing convention + maybe a script) | `WORKFLOW.md`, `lead-agent.md`, a `scripts/route-cascade.py` |
| 6 | **Route non-obvious requests through the resolved WBS id, not the prose catch-all** — make "answer directly" the narrow exception. | adSCAILE determinism (P9, p.42) | Routing | Med | S | Low | `lead-agent.md` routing table |
| 7 | **Add a conformance-style self-audit** — a read-only script giving a binary "system-consistent" gate + a score (subagents current vs models.yml, every `ROUTED_TO` closed, no orphan docs). | adSCAILE `adscaile-audit` (p.26) | Architecture, Reviews | Med | M | Low | new `scripts/verify-system-consistency.py`, `ci.yml` |
| 8 | **Remove the unused `.claude/worktrees/` dir** and the worktree language it implies, or document why it stays. | Original | Architecture | Low | S | Low | `.claude/worktrees/` |
| 9 | **Audit whether all 75 scripts / every step of the 151 KB `pipeline.yml` still fire** — retire dead gates. *(Estimate — I can't see firing history from here.)* | Original | Tokens, Reviews, Speed | Med (if dead weight exists) | L | Med | `scripts/`, `config/*-pipeline.yml` |

Deliberately **not** recommended: adopting the MCP substrate now. The manual sanctions file-only "Stufe 0" (FAQ p.44) and the substrate pays off at multiple parallel sessions/loops or multi-project isolation (p.26). Revisit only if Revitalise becomes multi-session-concurrent or you run several client repos off one coordination core — then it's the right move, and recommendations 1 and 5 are the on-ramp.

---

## 6. What I'd do first

1. **The handover hook (rec 1).** Highest impact-to-effort in the list. Your single largest body of hard-won rules — the entire "fourth/fifth case" in `WORKFLOW.md` — exists to cope with dispatches that lose context or die silently. The reference treats that as a solved problem with a two-hook pattern it calls the cheapest reason to leave file-only mode. You're carrying the cost in prose and manual reconciliation; convert it to a hook.

2. **De-fuse narrative from operative rules (rec 2), starting with `lead-agent.md`.** It's a mechanical-tier router forced to parse strategic-tier history on every session. Separating the "why" into the history doc you already maintain is exactly the ADR/decision-log discipline the reference is built on — and it directly relieves the token and routing-clarity gaps at once. Do lead-agent first because it's on the hot path of every request.

3. **De-duplicate the three triplicated rule-sets (rec 3).** Once narrative is out, the remaining overlap across `CLAUDE.md`/`WORKFLOW.md`/`lead-agent.md` is the next-largest always-loaded weight, and collapsing it to one canonical home each enforces the Token Rules your own `models.yml` already states. Low risk, and it makes the system easier to keep consistent — which is the thing your whole learning loop is spending effort to protect.

All three are the reference's own principles pointed at your actual, evidenced pains — not framework machinery adopted for its own sake.

---

## 7. Generalisation & determinism roadmap (for multi-customer reuse)

Added after the audit, in response to: *make it more deterministic and reusable across customers.* Going multi-customer flips one earlier verdict — the deterministic core is exactly what the reference says serving multiple projects is *for* (Manual p.26 maturity ladder; p.33 Mandantenfähigkeit). The organising idea: today the repo fuses the reusable **engine** (agents, skills, scripts, `WORKFLOW.md`, `models.yml`), the per-customer **instance** (`contract/`, `config/<slug>-*.yml`, WBS, `logs/`), and client facts leaking into "general" files (the ADR-006 `tst_acc` topology in `WORKFLOW.md`, the slug everywhere, Power Platform assumptions inside "general" skills). Determinism and generalisation are the same move: turn per-customer variation into **data the engine validates** instead of **prose an LLM interprets**.

| # | Recommendation | Source | Primarily improves | Effort | Risk |
|---|---|---|---|---|---|
| 10 | **Split engine from instance** — versioned framework package/repo; each customer a thin consumer repo holding only its own `contract/`/`config/`/`docs/`/`knowledge/`. | adSCAILE engine-pack extraction, consumer-repo layout (Manual p.12, p.28) | Generalisation (foundational) | L | Med |
| 11 | **Declarative `loop.yaml` flow** the engine validates, replacing the prose Flow + hardcoded topology; deterministic `auto_condition` gates where a human isn't legally required. | Declarative loops P1/P2, gate auto_condition (p.9, p.13, p.27) | Determinism + Generalisation | L | Med |
| 12 | **Parameterise all client-specific values into one `instance.yaml`** (slug, env chain, stack, paths); kill the ADR-006 `tst_acc` hardcode. No customer name survives in an engine file. | P1 agnostic / config-not-code (p.40) | Determinism + Generalisation | M | Low |
| 13 | **Instance config validator** that rejects a malformed instance before any run (fields, DAG acyclicity, gate keywords, cascade vocab); non-zero exit blocks. | `loop.register` Pydantic validation + `adscaile-audit` (p.9, p.26) | Determinism | M | Low |
| 14 | **New-client bootstrap** that scaffolds an instance from the engine + a discovery questionnaire (Loopsmith analog) — a client starts from a generated, valid instance, not a copy of Revitalise. | Loopsmith (p.9, p.27) | Generalisation | M | Low |
| 15 | **Per-instance least-privilege capability grants** — each client's `settings.json` grants only what that client needs. | P13 least-privilege (p.43) | Determinism + isolation | M | Low |
| 16 | **Engine semver + instance pinning** — additive, backward-compatible engine changes; old clients keep running. | P12 additive evolution (p.43) | Generalisation / safety | S–M | Low |
| 17 | **Promotion altitude for the learning loop** — decide which improvements are engine-level (all clients benefit) vs client-specific. | Your `how-to-promote-a-finding` + ADR/decision-log split (p.16) | Determinism of scope | M | Med |
| 18 | **SQLite knowledge store** — a `platform_facts` registry (shared, non-confidential, the biggest reuse asset) + a `failure_modes` registry, structured facts + pointers (not blobs), written only through a typed script interface, read on demand. | adSCAILE KB + artifact registry + decision-log (p.15–17) | Tokens, Generalisation, Reviews | M–L | Med |
| 19 | **Deterministic build/deploy runner** — mechanical happy path runs as a script with zero model tokens; a scoped model call diagnoses only failures; templated summaries. | adSCAILE Deploy-Loop minimalism + P9 (p.23, p.42); your `models.yml` re-tiering note | Tokens (large), Speed | M | Med |

### 7.1 Where to host the knowledge DB

The gotcha that governs the answer: **the live `.sqlite` file must not sit in OneDrive, SharePoint, or Azure Files.** SQLite is single-writer, and its documentation warns against network/sync filesystems — the sync client locks or copies the file mid-write and corrupts it. Only a *text dump* of the DB belongs in sync or git.

Match the host to how many sessions write at once (the BASE/MIDDLE/TIP ladder, Manual p.26):

- **Now (BASE):** live `kb.sqlite` on the dev machine's **local disk**, outside any synced folder; source of truth in git is a `.sql` dump (`.dump` → commit; restore with `sqlite3 … < kb.sql`). Zero infra, git is the backup. Limit: unreachable from cloud/Cowork sessions and single-machine.
- **Then (MIDDLE/TIP):** when you need it live from Cowork, a second machine, or concurrent writers, put SQLite behind a small endpoint — **Turso/libSQL** (managed, free tier, zero-ops; the lightest lift) or a self-hosted **Azure Container App** running the adSCAILE MCP substrate (SQLite behind typed tools over HTTP, `/t/<tenant>/mcp` routing, p.28–33). Keep the `.db` on the container's local disk, not Azure Files.
- **Governance boundary:** the shared DB holds **platform + engine** knowledge only (non-confidential, freely hostable). Client-specific facts stay in that client's instance repo. That split (rec 17) doubles as your AVG/confidentiality line.

**Default:** local file + git `.sql` dump now; lift to Turso the day you want it from Cowork or a second machine; self-hosted Azure/substrate only when clients run concurrently and need tenant isolation in code.

### 7.2 Sequencing note

The hygiene recs (2, 3, 4) are now **prerequisites**, not nice-to-haves — you can't cleanly split engine from instance while client history and duplicated rules are fused into operative files. Order: **de-fuse & de-dup (2–3) → split engine/instance (10) → parameterise (12) → validate (13) → declarative flow (11) + knowledge DB (18) + runner (19) → bootstrap/isolation (14–16) → conformance & promotion (7, 17).** The handover hook (1) is orthogonal and worth doing early. The step-by-step build order, with per-phase verification and human checkpoints, is in the companion file **`IMPLEMENTATION-PLAN.md`**.

### 7.3 The line to hold

Determinise the *coordination* (which task is ready, which gate is open, where an escalation routes, whether an instance config is valid, executing a known build) — not the *judgment* (routing varied consulting intents, diagnosing a novel platform failure, reviewing an unfamiliar contract). That's the reference's own "Stringenz im Kern, Flexibilität am Rand," and it's where your real token spend belongs.
