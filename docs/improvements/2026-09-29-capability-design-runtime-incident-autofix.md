# Capability Design — Runtime Incident Lane: from a logged error to a reviewed fix (2026-09-29)

**Status:** DRAFT — not authorised. Requires the open decisions in §7 answered, then `APPROVE IMPROVEMENTS`
per phase (§5).
**Scope:** mostly `system` (non-billable, outside the contracted WBS). **One product slice** — the
parallel branch in `REV | Ops | Failure Alert` and three `rev_errorlog` columns (WS-IR1) — touches the
delivered solution and therefore needs a change-order decision first ([`C-COM-002`](constraints/commercial/commercial-constraints.md#L35); decision D-4).
**Altitude:** **ENGINE** for the lane (intake, triage, gate, verify, close). **INSTANCE** for the two
adapters that know this platform: the emitter (a Power Automate branch) and the reader (a Dataverse query).
Both adapters sit behind a small interface so another client's stack plugs in its own.
**Authorising basis:** capability mode, per [`agents/improvement-agent.md` L55-L85](agents/improvement-agent.md#L55).
**Source:** reviewer request, 2026-09-29, verbatim:

> Design a system add on that runs in parallel to the error logging which send a message to this agent
> system so it can trouble shoot and fix the problem automatically. The only stage gate would be a human
> in the loop verifying the proposed change before its build and deployed.

**Relationship to earlier designs — read before applying:**

| Earlier artefact | What this document does to it |
|---|---|
| 2026-09-26 design, WS-W (work-item ledger) | **Used, not changed.** Every incident becomes a `bug` item. Reviewer decision D-8 (only the reviewer's verdict makes an item verified/done) is **kept** — the lane stops at `deployed:<env>` plus recurrence evidence |
| 2026-09-26 design, WS-T (`fixed_in_flight`) and WS-U (post-deploy batch) | **Used, not changed.** An incident deploy is a pipeline result like any other and feeds the next post-deploy batch |
| `loops/delivery.loop.yaml` → `cascade_routing` | **Used, not changed.** A runtime defect enters as `FUNCTIONAL_FAILURE`; `SPEC_GAP`, `ARCH_GAP` and `STUCK_LOOP` leave the lane and go to a human, exactly as today |
| [`agents/WORKFLOW.md` → Human Gate Keywords](agents/WORKFLOW.md#L530) | **Extended** with one keyword, `APPROVE FIX INC-<n>`. For incident-lane changes only, it replaces `APPROVED` (Dev, Test) and `APPROVE PRD` — the reviewer's "only stage gate" instruction. All other work keeps every existing gate |
| `logs/state/diagnostic-briefs/` (build-agent's failing-step brief) | **Not touched.** That is a build-time aid for a dispatch already running; this lane starts from a *runtime* error in a live environment |

No earlier design on this subject exists: `grep -rliE 'rev_errorlog|runtime (error|failure)|self-?heal|auto-?remediat' docs/improvements/*.md`
returns only failure-analysis documents about build incidents, none about a runtime lane.

---

## 0. Conclusion first

**The lane is a pull request factory with one human gate.** A flow fails → `REV | Ops | Failure Alert`
does what it does today (error-log row, Teams card to the process owner) **and, on a parallel branch that
can never delay or break that**, opens a GitHub issue carrying ids only. A GitHub Actions job picks the
issue up, reads and redacts the error, and runs this agent system headless: reproduce the failure in a
test, fix it, build it offline, and open a draft pull request with a plain-language diagnosis. **Nothing
touches an environment until a named reviewer approves that pull request with `APPROVE FIX INC-<n>`.**
Merge then runs the existing CI chain DEV → TST/ACC → PRD, and the lane watches for the same error to
come back.

**Four things make "automatic" safe enough to run unattended:**

1. **The job that thinks holds no deployment credentials; the job that deploys does no thinking.**
   Diagnosis runs with read-only, error-log-only access. Deploy credentials exist only in jobs that start
   after the approval.
2. **A fix may only touch an allow-listed set of paths.** Flow definitions, Code App source, tests.
   Never schema, security roles, tenant objects, CI, gates or agent rules. Anything else becomes a
   diagnosis for a human, not a pull request.
3. **No free text from a live environment reaches a prompt unredacted.** The intake form is public, so
   an error message can carry text an applicant typed. It is reduced to an allow-list of tokens and
   framed as data.
4. **The loop is bounded.** One incident per error fingerprint, a daily run cap, three fix attempts, then
   `STUCK_LOOP` to a human — the rule the delivery loop already has.

**Nine workstreams, WS-IR1 to WS-IR9. Three new constraint rows are proposed (§6), none retired.**
Five open decisions (§7); **D-3 (data protection) blocks enabling the lane in TST/ACC and PRD**, not in DEV.

---

## 1. Premises measured before drafting

| # | Premise | Measured | Command |
|---|---|---|---|
| P1 | Every flow in the solution routes its failures through one child flow | **True — 9 of 9** flows call `REV \| Ops \| Failure Alert`. One emitter branch there covers the whole solution | `grep -il '8f1c2a44-1004-4b7a-9e21-0a1b2c3d4e04' src/solutions/RevitaliseGrantAutomation/Workflows/*.json \| grep -vi failurealert \| wc -l` |
| P2 | The Failure Alert flow can take a parallel branch without affecting its caller | **True.** `Respond_to_calling_flow` runs after the two Teams actions and the fallback email only; a branch off `Write_error_log_row` that is not in that `runAfter` list neither delays nor fails the response | `python3 -c` over the flow's `actions[*].runAfter` (Failure Alert JSON, `Write_error_log_row`) |
| P3 | The error text is free text and can carry third-party input | **True.** Input `text_2` is "the platform error text"; its own description says it "MUST NOT contain personal data" — an instruction to callers, not a filter. Platform validation errors can echo a field value, and the intake flow is fed by a public web form | Failure Alert trigger schema, `text_2` |
| P4 | There is no "failing action" or "error code" input — only a message | **True.** Inputs are flow name, run id, message, record reference, severity, run link. A stable fingerprint needs a failing-action field (WS-IR1 adds it as optional) | same schema |
| P5 | The record reference is pseudonymous, not anonymous | **True**, recorded as risk A-R12, flagged for DPO confirmation | [TAD §5.14](docs/architecture/revitalise-grant-automation-architecture.md) |
| P6 | The repository is on GitHub and CI already deploys per environment with its own identity | **True.** `origin` is `github.com/Argelis-XVL/Revitalise`; `ci.yml` has jobs `build`, `stage-dev`, `promote-tst-acc`, `promote-prd`, each environment authenticating as its own federated identity; the `prd` GitHub Environment's required-reviewer rule **is** today's `APPROVE PRD` | [`.github/workflows/ci.yml` L869](.github/workflows/ci.yml#L869), comment block L155-L160 |
| P7 | CI cannot run the agent system today | **True.** `ci.yml` does not check out the `.engine` submodule and holds no model API key, so `agents/`, `skills/` and the hooks would be dangling symlinks in a runner | `grep -niE 'submodule\|claude-code-action\|ANTHROPIC' .github/workflows/ci.yml` → no match |
| P8 | Agent sessions cannot write to Dataverse schema | **True, by design.** `PROVISION_APP_ID` / `PROVISION_CERT_THUMBPRINT` are reviewer-held; every recent pipeline line records them absent | `grep -c 'CONFIRMED ABSENT' logs/pipeline.log` |
| P9 | PRD has never been deployed | **True.** No `[PRD]` stage line in `logs/pipeline.log`. Near-term incidents will come from DEV and TST/ACC | `grep -c '\] \[PRD\] ' logs/pipeline.log` → 0 |
| P10 | The work-item ledger already has a type for this | **True.** `bug` is a chain type whose parent may be a `wbs` task | `.engine/scripts/lib/work_items.py` → `TYPES`, `CHAIN_TYPES` |

**Not measured, and named so nobody builds on it:** whether the flow owner's licence covers the premium
HTTP action (the intake flow's HTTP *trigger* is premium, which suggests yes — **unverified, check the
licence**); the exact input names of `anthropics/claude-code-action` (**verify against its README at
build time**, per [`C-TECH-053`](constraints/technology/technology-constraints.md#L108)); and whether the
tenant has an Azure Key Vault for secret-type environment variables.

---

## 2. How it works, end to end

```
 LIVE ENVIRONMENT (dev | tst_acc | prd)                    GITHUB (private repo)
 ───────────────────────────────────────                   ──────────────────────────────────────────────
 any REV flow fails
   └─► REV | Ops | Failure Alert
         ├─ Write_error_log_row ──────────┐
         │    ├─ Teams card to process    │  (unchanged)
         │    │  owner / fallback email   │
         │    └─ Respond_to_calling_flow  │
         │                                │
         └─ [NEW, parallel] Notify ───────┼──► issue "INC: <flow> / <action>"      (ids only, label incident)
              (its failure only marks     │         │
               the row; never alerts,     │         ▼
               never fails the caller)    │    incident-triage.yml   ── NO deploy credentials ──
                                          │      1 intake: schema, bot author, fingerprint,
 rev_errorlog row ◄── read-only, ─────────┼────── dedup, storm cap, transient?, eligible?
 (this table only)    one table only      │      2 read + redact the error text
                                          │      3 headless lead-agent → development/automation-agent
                                          │        reproduce in a test → fix → offline build (V2)
                                          │      4 draft PR incident/INC-<n> + docs/incidents/INC-<n>.md
                                          │         │
                                          │         ▼
                                          │    ╔══════════════════════════════════════════╗
                                          │    ║  THE ONE HUMAN GATE                      ║
                                          │    ║  reviewer reads diagnosis + diff + tests ║
                                          │    ║  approves PR + comments APPROVE FIX INC-n║
                                          │    ╚══════════════════════════════════════════╝
                                          │         │ merge
                                          │         ▼
 dev ◄──────── tst_acc ◄──────── prd ◄────┴──── ci.yml chain (existing jobs) — halts on any red check
                                                    │
                                                    ▼
                                               recurrence watch → closes to deployed:prd, or reopens
```

**The incident's states** (one record per incident in `logs/incidents/INC-<n>.jsonl`, append-only, one
line per transition; `<n>` is the GitHub issue number, so no id allocation is needed):

| State | Meaning | Next |
|---|---|---|
| `received` | Issue opened, payload valid | `duplicate` · `transient-watch` · `diagnosing` · `human` |
| `duplicate` | An open incident has the same fingerprint; its count went up | — (issue closed, linked) |
| `transient-watch` | Throttling / timeout / 5xx class; no agent run unless it recurs past the threshold | `diagnosing` · `closed-no-action` |
| `diagnosing` | Headless run in progress | `awaiting-approval` · `human` |
| `human` | Not fixable inside the lane (§4) or a cascade to plan/architect/human; diagnosis posted | — (lane stops) |
| `awaiting-approval` | Draft PR open with diagnosis, diff, green offline tests | `deploying` · `rejected` · `revising` |
| `revising` | Reviewer asked for changes on the PR; counts as a cycle | `awaiting-approval` · `human` (3rd cycle = `STUCK_LOOP`) |
| `deploying` | Merged; CI chain running | `watching` · `deploy-failed` |
| `watching` | Deployed to the environment the error came from, and beyond; waiting for recurrence | `deployed` · `revising` (recurred) |
| `deployed` | Watch window passed clean. The `bug` item sits at `deployed:<env>` with the watch as evidence | reviewer verdict → `verified` / `done` (D-8, unchanged) |

---

## 3. Workstreams

Each requirement has an id (`IR-nn`) and a **Verify by** that is a command or a test, per the anti-bloat
rule that a requirement nobody can execute is not a requirement.

### WS-IR1 — Emit: a parallel branch in `REV | Ops | Failure Alert` (INSTANCE, product slice)

- **IR-01** A new branch `Notify_incident_lane` runs after `Write_error_log_row` **Succeeded**, in
  parallel with `Alert_process_owner_with_a_card`, and is **not** in `Respond_to_calling_flow`'s
  `runAfter`. *Verify by:* a Pester contract test in `src/tests/solutions/` asserting both facts on the
  flow JSON.
- **IR-02** The branch POSTs to the GitHub issues API for this repository with a body containing **only**:
  error-log row id, environment key (`dev`/`tst_acc`/`prd`), flow display name, run id, failing action,
  severity, occurred-on. **No error text, no record reference, no run link.** *Verify by:* contract test
  asserting the body's key set equals that list.
- **IR-03** Three new columns on `rev_errorlog`: `rev_failingaction` (text), `rev_incidentstatus`
  (choice: not-sent / sent / send-failed / disabled), `rev_incidentref` (text, the issue URL). The branch
  writes the status; on failure it writes `send-failed` and stops — **it never calls Failure Alert (no
  recursion) and never raises its own alert**. *Verify by:* contract test on the branch's `runAfter`
  shape; the schema change is applied by `ensure-schema.ps1` with the reviewer-held credential (P8).
- **IR-04** One new **optional** input `text_6` "Failing action" on Failure Alert. Optional for the same
  reason `text_5` was: a required input would break a caller not yet updated. Callers fill it from the
  `result()` filter the known-failure-modes digest already prescribes (filter for the Failed child, recurse
  into nested scopes). *Verify by:* contract test that `text_6` is not in `required`, plus one caller
  updated per flow as touched (the WBS 0.10 pattern).
- **IR-05** A per-environment feature flag, environment variable `rev_IncidentLaneEnabled` (default
  **off** in `tst_acc` and `prd` until D-3 is answered). Off → the branch writes `disabled` and exits.
  The GitHub token lives in a secret-type environment variable (Key Vault-backed if the tenant has one —
  see §1). *Verify by:* `deploymentSettings` test asserting the default per environment.
- **IR-06** The token is a **fine-grained personal access token of a dedicated bot account, scoped to
  this one repository, Issues: read & write only** — nothing else. Rotation ≤ 180 days with a named owner
  ([`C-TECH-044`](constraints/technology/technology-constraints.md#L86)). A leaked token can open issues;
  it cannot read code or trigger a deploy.

**Transport alternatives, not chosen:** the GitHub *connector* (avoids premium HTTP but its OAuth
connection carries far broader repo scope); a CI job **polling** `rev_errorlog` on a schedule (no token in
the tenant at all, but it is not "sending a message", and adds latency). The poll is kept as the
**reconciler** in IR-12 — it sweeps up rows marked `send-failed`.

### WS-IR2 — Receive: incident intake and triage (ENGINE)

`.github/workflows/incident-triage.yml`, triggered on `issues: opened` with label `incident`.

- **IR-07** **Author check first**: the job exits unless the issue author is the configured bot account.
  A collaborator cannot hand the agent a task by opening an issue. *Verify by:* workflow-syntax test
  asserting the `if:` guard; selftest with a non-bot author → no agent step runs.
- **IR-08** `scripts/incident-intake.py` validates the body against a closed JSON schema (unknown key =
  reject, same rule as the work-item ledger), computes a **fingerprint** = hash of (flow name, failing
  action, error *shape* — digits, GUIDs and quoted strings replaced by placeholders, computed after the
  redaction step of IR-10), and:
  - **dedup** — an open incident with that fingerprint gets a comment and a count; the new issue is closed
    as a duplicate;
  - **storm cap** — at most `incident_lane.max_runs_per_day` agent runs per day (instance.yaml; suggested 5).
    Over the cap, incidents are recorded and queued, not dropped;
  - **transient class** — throttling (429), timeouts, 502/503/504 and connector-unavailable go to
    `transient-watch` and only proceed after `transient_threshold` occurrences in `transient_window`
    (suggested 3 in 1 hour). A platform blip must not produce a code change;
  - **eligibility** — see §4; ineligible goes straight to `human` with a short triage note.
  *Verify by:* `python3 scripts/incident-intake.py --selftest` (dedup, cap, transient, schema rejection).
- **IR-09** The incident is resolved to a WBS task **by lookup, not judgement**: failing flow file →
  `contract/evidence-map.json` → task id. No match → the incident is still diagnosed, but the PR is
  labelled `unquoted` and commercial-agent is told ([`C-COM-002`](constraints/commercial/commercial-constraints.md#L35)).
  A `bug` work item is added with `source_ref` = the issue URL. *Verify by:* selftest over the nine flows'
  file names.

### WS-IR3 — Read and redact (INSTANCE reader, ENGINE redactor)

- **IR-10** The triage job reads the one `rev_errorlog` row by id through a **dedicated read-only
  identity per environment**: a federated app registration (no secret, same pattern as CI's deploy
  identities) bound to a custom security role **"REV Incident Reader": read on `rev_errorlog` only,
  organisation scope, nothing else**. It cannot read an application, an applicant or run history.
  Creating the registrations and role is a tenant operation behind `APPROVE TENANT`.
- **IR-11** `scripts/redact-error-text.py` reduces the message to an **allow-list**, not a deny-list:
  kept are the flow's own action names, `rev_*` schema names, HTTP status codes, platform error codes
  (`0x8004…`, `InvalidTemplate`, …) and a fixed vocabulary of platform phrases. Everything else becomes
  `[redacted]`. The raw text is never written to the issue, the PR, a log or the repository. *Verify by:*
  `--selftest` with fixtures that include an email address, a postcode, a name and an injected
  instruction ("ignore previous instructions…") — all four must come out as `[redacted]`.
- **IR-12** A scheduled reconciler (same workflow, daily) queries rows with `rev_incidentstatus =
  send-failed` or rows newer than the last run with `not-sent` while the flag is on, and opens their
  issues. A failed notify is therefore delayed, never lost.

### WS-IR4 — Diagnose and propose (ENGINE)

- **IR-13** The runner checks out the repository **with the `.engine` submodule** (read-only deploy key
  for `Agent-Delivery-System`) and runs Claude Code headless via `anthropics/claude-code-action`, with the
  project's `.claude/agents/` and `CLAUDE.md` so the same agents, gates and hooks apply as locally. The
  prompt is one handoff line plus the incident record path — never the error text inline:
  `INCIDENT | id:INC-<n> | env:<env> | wbs:<id> | items:<WI-id> | record:logs/incidents/INC-<n>.jsonl | cascade:FUNCTIONAL_FAILURE`.
- **IR-14** One new routing row in [`agents/lead-agent.md`](agents/lead-agent.md#L20): *Runtime incident
  (an `INCIDENT |` line) → `development-agent`, carrying `CASCADE: FUNCTIONAL_FAILURE`* — which development-agent
  fans out to `automation-agent` (flows) or `frontend-agent` (Code App) as today. No plan or architect
  hop: the lane assumes the approved SDD and TAD are right. If the diagnosis finds they are not, the agent
  emits `CASCADE: SPEC_GAP` / `ARCH_GAP`, the incident goes to `human`, and the normal delivery flow takes
  it from there.
- **IR-15** **Reproduce first.** The fix pass must first add a test that fails for the incident's
  fingerprint (Pester contract test for a flow, vitest for the Code App), then make it pass. A PR without
  a new failing-then-passing test is not opened; the incident goes to `human` with the diagnosis only.
  *Verify by:* `scripts/verify-incident-fix-scope.py` (IR-16) checks the PR adds or changes at least one
  file under `src/tests/` or `*.test.ts(x)`.
- **IR-16** `scripts/verify-incident-fix-scope.py` — a HARD check on every `incident/*` branch. The diff
  may touch only `src/solutions/**/Workflows/*.json` (and their `.notes.md`), `src/code-apps/**/src/**`,
  `src/tests/**`, `docs/incidents/**`, `logs/incidents/**`. Anything under `Entities/`, `Other/`
  (security roles, field security, customizations), `provisioning/`, `config/`, `.github/`, `scripts/`,
  `agents/`, `constraints/`, `skills/`, `knowledge/` or `.engine` fails it. Proposed as a new constraint
  (§6). *Verify by:* its own `--selftest`.
- **IR-17** The run executes the feature's existing build config **offline** — packing, unit and
  contract tests, source gates (V1/V2). No `pac` auth, no environment URL. *Verify by:* the triage job
  has no `environment:` key and no deploy secrets in scope; a workflow-syntax test asserts both.
- **IR-18** Output is a **draft PR** from `incident/INC-<n>` and `docs/incidents/INC-<n>.md`, written to
  [`skills/how-to-report-to-the-reviewer.md`](skills/how-to-report-to-the-reviewer.md)'s shape: what
  failed in plain language, root cause with the source line, the fix, what the new test proves, what was
  **not** verified (always: live behaviour), blast radius (which other flows share the changed action),
  and the roll-forward plan. Tool use in the run is allow-listed (`Read`, `Edit`, `Write`, and `Bash`
  limited to the test and build commands); no network tools.

### WS-IR5 — The one human gate (ENGINE)

- **IR-19** The gate is a PR approval **plus** a comment `APPROVE FIX INC-<n>` from a member of the
  configured reviewer team. Both are needed: the approval is what branch protection can enforce, the
  keyword is what [the relay rules](agents/WORKFLOW.md#L567) and the record need (verbatim keyword, named
  human). The bot cannot approve its own PR (GitHub refuses author approval).
- **IR-20** Before merge, a check job writes the approval record to `logs/incidents/INC-<n>.jsonl`:
  `authorised_by`, `keyword`, `pr`, `head_sha`, `target_envs`, `ts`. Because a PRD deploy is one of the
  four acts that leave this repository, the record states in one line what is about to be deployed where
  ([`agents/WORKFLOW.md` L597](agents/WORKFLOW.md#L597)).
- **IR-21** **The approval is bound to the commit.** A push to the branch after approval dismisses it
  (branch protection "dismiss stale approvals"), and the check job refuses if `head_sha` differs from the
  approved commit. The reviewer approves exactly what ships.
- **IR-22** Anything the reviewer writes other than the keyword is a revision request: the lane
  re-dispatches with the PR comments as input, counts a cycle, and on the **third** cycle emits
  `STUCK_LOOP` and stops ([`agents/WORKFLOW.md` → Revision Cap](agents/WORKFLOW.md#L672)).

### WS-IR6 — Build and deploy (INSTANCE wiring over the existing `ci.yml`)

- **IR-23** Merge to `main` runs the existing `ci.yml` chain unchanged for DEV and TST/ACC. Every
  existing HARD gate still runs; any red gate halts the chain.
- **IR-24** **PRD, per the reviewer's instruction, needs no second click for an incident fix** — see
  D-2. Implemented as: the `promote-prd` job, when the merged commit carries a valid IR-20 record, runs in
  a GitHub Environment `prd-incident` whose protection is (a) deployment branch = `main` only and (b) a
  first step that verifies the approval record against the GitHub API (reviewer-team member, keyword,
  `head_sha`). `prd-incident` gets its own federated credential on the PRD deploy identity (tenant
  operation, `APPROVE TENANT`). Normal delivery keeps `prd` and its required reviewers — `APPROVE PRD` is
  not weakened for anything except an approved incident fix.
- **IR-25** PRD is reached only by the **same artefact** that passed DEV and TST/ACC (the existing
  provenance check), and only if the incident's reproduction test passed on it.
- **IR-26** **Roll-forward, not rollback.** A managed solution cannot be re-imported at a lower version,
  so "undo" is a revert commit at a higher version through the same lane. The diagnosis document names
  the revert in advance; a revert of an approved incident fix may itself be approved with one keyword.

### WS-IR7 — Verify and close (ENGINE)

- **IR-27** After each environment's deploy, a lane step queries `rev_errorlog` (the IR-10 reader) for
  the fingerprint from runs **started after** the deploy time. Watch window: `incident_lane.watch` =
  the later of 7 days or 20 runs of the failing flow (instance.yaml). A recurrence reopens the incident
  as a failed cycle (IR-22's count).
- **IR-28** A clean window moves the `bug` item to `deployed:<env>` with a `deploy-record` and a
  `no-recurrence` evidence object, and marks the source error-log rows resolved with the PR link. It does
  **not** move the item to `verified` or `done` — only the reviewer's words do that (D-8). The issue
  stays open with one line: "no recurrence in <window>; reply *verified* to close".
- **IR-29** Each closed incident appends **one finding** to the improvement log, so the learning loop
  hears about runtime defects too. CI never allocates an `IMP-` id: the allocator's lock is local to one
  machine and local sessions append concurrently (see the capture contract's *Which id* row). CI writes
  `logs/incidents/INC-<n>.finding.json`; the next local lead-agent session imports pending findings with
  `allocate-improvement-id.py --append`. *Verify by:* `verify-improvement-log.py` rejects a finding with
  no allocated id; a new check reports pending incident findings older than 7 days (report only).

### WS-IR8 — Safety rails (ENGINE)

- **IR-30** **Two kill switches, either sufficient:** the environment variable in IR-05 and a repository
  variable `INCIDENT_LANE_ENABLED`. Off stops agent runs; the error-log row and the Teams card to the
  process owner are unaffected, because the lane never replaced them.
- **IR-31** **Cost bound:** per-run `--max-turns`, the daily cap of IR-08, and model tier from
  `config/models.yml` (triage and intake are scripts, not models; diagnosis runs on the development
  agents' default tier; escalation conditions apply unchanged).
- **IR-32** **Secrets separation, stated as a test:** the triage workflow's jobs have no `environment:`
  and reference no `ENV_URL_*`, `APP_ID`, `PROVISION_*` secret. *Verify by:* an extension of
  `scripts/verify-workflow-syntax.py`.

Threats this lane adds, and what stops each:

| Threat | Stopped by |
|---|---|
| An applicant types an instruction into the public form; it surfaces in an error message and steers the agent | IR-11 allow-list redaction; text framed as data; IR-16 path allow-list; IR-17 no credentials; the human gate |
| Someone opens a fake incident issue to get code written | IR-07 bot-author check; IR-08 closed schema |
| The agent weakens a gate or the CI file to get its fix through | IR-16 forbids `.github/`, `scripts/`, `agents/`, `constraints/`, `skills/`, `config/`, `.engine` |
| A leaked GitHub token | IR-06 scope (issues only, one repo); storm cap; rotation |
| An error storm burns budget or floods the reviewer | IR-08 dedup + daily cap + transient class |
| Personal data leaves the tenant | IR-02 ids-only message; IR-10 one-table reader; IR-11 redaction; D-3 before TST/ACC and PRD |
| A fix approved, then quietly changed before merge | IR-21 approval bound to `head_sha` |

### WS-IR9 — Commercial and reporting hooks (ENGINE)

- **IR-33** Commercial-agent reads `logs/incidents/` like any other evidence. A defect in a phase with a
  `CLIENT ACCEPTED` record inside its 60-day window is **warranty** (non-billable); before acceptance it
  belongs to the task found by IR-09; after warranty it is a change-order decision. The lane never decides
  this and never blocks on it ([`C-COM-006`](constraints/commercial/commercial-constraints.md#L44)). Hours
  only, no money.
- **IR-34** Reviewer-facing notices go to **Argelis, not the client**: GitHub notifications, plus an
  optional Teams webhook to an Argelis channel. The client's process owner keeps receiving exactly the
  alert they receive today.

---

## 4. What the lane will not fix, and what it does instead

Deliberately narrow. Every row below is a known way this project's work has needed a human or a
reviewer-held credential.

| Failure kind | Why not automatic | The lane does |
|---|---|---|
| Expired or broken connection, expired secret (e.g. the intake client secret, risk A-R68) | The fix is a credential rotation, not a code change | `human`, with the connection or credential named |
| Schema or security-role change needed | Needs `ensure-schema.ps1` with the reviewer-held credential (P8); outside IR-16 | `human`, with the proposed schema delta written up |
| Tenant, Entra, SharePoint, Teams objects | `APPROVE TENANT` territory | `human` |
| Designer-only fixes (dynamic-schema resolution, connection binding) | No CLI or API route exists | `human`, with the exact designer steps |
| Bad input data from the website | Not a defect in what we built; possibly a spec question | `human`, flagged as a possible `SPEC_GAP` |
| Throttling, timeouts, platform outage | No code change fixes a platform blip | `transient-watch` (IR-08) |
| The fix would change requirements or architecture | Cascade rule | `CASCADE: SPEC_GAP` / `ARCH_GAP` → `human` |
| A failure that never reaches Failure Alert (a 401 at the platform gate before the flow runs; a flow switched off; a Code App error in the browser) | Nothing is logged, so nothing is sent | Out of scope for this design; named in §8 |

---

## 5. Sequencing — three phases, each behind its own `APPROVE IMPROVEMENTS`

| Phase | Contents | Environments | Gated on |
|---|---|---|---|
| **A — Diagnose only** | IR-01…IR-13, IR-30…IR-32. The lane opens issues, triages and posts a diagnosis; **no PRs** | DEV | D-1, D-4, D-5; tenant ops for IR-10 (`APPROVE TENANT`) |
| **B — Propose fixes** | IR-14…IR-22, IR-27…IR-29, IR-33, IR-34. Draft PRs; merges deploy DEV → TST/ACC through the existing gates | DEV, then TST/ACC | Phase A running cleanly for 10 incidents or 2 weeks, whichever first |
| **C — One-gate PRD** | IR-23…IR-26. `prd-incident` environment and credential | PRD | **D-2 and D-3**; at least one completed Phase B incident |

Parallel-safe: WS-IR1 (product slice, development-agent) and WS-IR2/IR3 (engine scripts,
improvement-agent) share no files and no gate. WS-IR4 edits `agents/lead-agent.md` and must not run in
parallel with another dispatch editing it.

---

## 6. Anti-bloat accounting

**Three new constraint rows — the per-review cap — and each cites this document's requirement ids:**

| Proposed | Rule | Severity | Verify by |
|---|---|---|---|
| `C-TECH-080` | An `incident/*` branch touches only the allow-listed paths | HARD | `python3 scripts/verify-incident-fix-scope.py` (IR-16) |
| `C-TECH-081` | A deploy of an incident fix beyond DEV carries an approval record bound to the deployed commit | HARD | the IR-20/IR-24 check step (IR-21) |
| `C-DOM-034` | No free text read from a live environment enters a prompt, an issue, a PR or a tracked file except through the allow-list redactor | HARD | `python3 scripts/redact-error-text.py --selftest` + a grep gate over `docs/incidents/` and `logs/incidents/` for the redactor's marker being the only non-allow-listed token |

**Retirement obligation:** none found. Nothing existing does this job, so there is nothing to retire; the
lane reuses the ledger, the cascade vocabulary, the CI chain and the capture contract instead of adding
parallel versions of them.

---

## 7. Decisions

### Settled by the reviewer, 2026-09-29 (do not re-ask)

- **One human gate** — approval of the proposed change before it is built and deployed. This design
  implements exactly one *stage* gate. Two human touches remain that are **not** stage gates and block
  nothing: the reviewer's later *verified* (D-8, which closes a work item) and anything the lane hands to
  `human` because it is outside §4's scope.

### Settled by the reviewer, 2026-10-05 (do not re-ask)

- **A reviewer-directed hotfix carries two obligations; the override itself stays the reviewer's.**
  Decided as decision D-1 of [improvement review 2026-10-05](docs/improvements/2026-10-05-improvement-review.md#L215),
  answer "agreed with suggested" (Xander Lykopoulos, relayed 2026-10-05 10:41). Basis: eighteen hotfix
  imports reached DEV on 2026-10-03/04 with every gate skipped and no lesson logged (IMP-1038, second
  instance of IMP-0981's class). Any session that imports to an environment "by reviewer instruction,
  gates overridden":
  - **(a)** runs `python3 scripts/run-source-gates.py` over the source it is about to import, before the
    first import, and records in its `logs/pipeline.log` line which gates were red (or `0 red`);
  - **(b)** logs each surprise to `logs/improvement-log.jsonl` (capture contract) before the session ends,
    not afterwards.

  The override is not narrowed: a red gate is recorded, it does not stop the hotfix. **Status of this
  bullet:** a recorded decision inside a DRAFT design. Nothing enforces it until the lane's Phase A is
  approved; until then it binds by being read here and in the 2026-10-05 review's D-1 record.

### Open — recommendation first

| # | Decision | Recommendation | Blocks |
|---|---|---|---|
| D-1 | Does "before it's built" allow the **offline** build and tests to run before approval? | **Yes.** They touch no environment and give you a green build and a failing-then-passing test to approve, instead of a bare diff | Phase A |
| D-2 | Does `APPROVE FIX INC-<n>` also authorise **PRD**, replacing `APPROVE PRD` for incident fixes? | **Yes, as you asked — with IR-21 (bound to the commit), IR-25 (same artefact that passed TST/ACC) and IR-26 (roll-forward named in advance).** The alternative, keeping `APPROVE PRD` as a second click, is safer and contradicts your instruction | Phase C |
| D-3 | May **redacted** error text from TST/ACC and PRD leave the tenant (to GitHub runners and the model provider)? | **Ask the Client's DPO, and amend the DPIA before switching it on there.** Until then, run the lane in DEV only, where the data is synthetic. The ids-only message (IR-02) is safe everywhere; the read-and-redact step is the new processing | Phase C, and TST/ACC in Phase B |
| D-4 | Is the product slice (Failure Alert branch, three columns, reader role) billable? | **Absorb it as non-billable Argelis tooling** — it lowers our warranty cost, and the Client's alerting is unchanged. Still route it through commercial-agent so the decision is recorded ([`C-COM-002`](constraints/commercial/commercial-constraints.md#L35)) | Phase A (WS-IR1) |
| D-5 | Who is on the reviewer team whose approval counts (IR-19), and which bot account opens issues (IR-06)? | The two reviewers named in `logs/pipeline.log` (Anna Southern, Xander Lykopoulos) as the team; a new dedicated GitHub account for the bot, owned by Argelis | Phase A |

---

## 8. Verification reached

**Executed while drafting:** the ten premises in §1, each by the command shown (P1: 9 of 9 flows call
Failure Alert; P2: the runAfter graph read from the flow JSON; P7: no submodule checkout or model key in
`ci.yml`; P9: 0 PRD stage lines). Id namespaces `IR-nn`, `INC-` and `WS-IR` checked unused across
`docs/`, `agents/`, `constraints/`, `scripts/`. Highest existing constraint ids read: `C-TECH-079`,
`C-DOM-033`, so the three proposed ids are free.

**Not verified:** anything live — no issue was opened, no workflow run, no flow edited. The HTTP licence,
the `claude-code-action` inputs and Key Vault availability are unverified (§1). The redactor's allow-list
has not been tested against real platform error messages from this solution; Phase A should collect ten
before Phase B.

**Known gaps this design does not close:** failures that never reach Failure Alert (§4, last row). A
heartbeat check — "has each scheduled flow run in its expected window?" — would catch a flow that stopped
running; it is a natural next design, not part of this one.
