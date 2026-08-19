# Project Management Agent — Design (billable hours on DEV deploy + on-demand status)

**Author:** lead-agent, live session with Xander Lykopoulos
**Date:** 2026-08-17
**Status:** **SUPERSEDED 2026-08-18** by `docs/improvements/2026-08-18-project-management-system-redesign.md`. The WBS workbook and the
signed Service Agreement arrived after this was written; they make the WBS the contractual Agreed
Specification and the work queue, not a budget denominator, and they falsify the phase ranges this
document builds on (SDD §10's 106–160 h / 7 automations against a contract of 292 h / 9). Read the
redesign instead; this is kept for the reasoning in §2.1–§2.4, which the redesign carries forward.

**Original status:** DESIGN — nothing implemented. Implementation edits `agents/`, `constraints/`, `skills/`
and `CLAUDE.md`, which only `improvement-agent` may do, behind `APPROVE IMPROVEMENTS`
(`agents/WORKFLOW.md` → Human Gate Keywords).
**Scope:** a new `pm-agent` that (a) accounts for billable hours when a feature reaches the DEV
environment, and (b) answers a status query directly from chat.
**Revision 2 (same session):** the reviewer offered to add the pre-project quoting workbook
(`Revitalise-WBS-Grant-Automation-v0.4.xlsx`) to `docs/Import/`. That makes a task-level agreed
baseline available where revision 1 had only a phase range transcribed into the SDD. New: §2.6,
§3.10, two scripts/config files, two decisions, and a reordered build sequence.
**Evidence base:** `logs/build.log`, `logs/pipeline.log`, `logs/routing.log`,
`logs/improvement-log.jsonl`, `git log`, `docs/plans/revitalise-grant-automation-plan.md` §10,
`config/models.yml`, `constraints/README.md`.

---

## 0. Executive summary

The request is two capabilities that share one substrate.

**Billable hours.** This repository does not record hours. It records, with timestamps, *evidence
that work happened*: 9 commits, 30+ dated `routing.log` lines, 8 dated `build.log` entries, 5 dated
`pipeline.log` entries, 26 timestamped findings. That is enough to **propose** work sessions
deterministically and never enough to **assert** billable hours — the agent works while you do
something else, and you work where the repo cannot see you (Emily's walkthroughs, Wanstor chasing,
the maker portal). So the design is: a script reconstructs candidate sessions from evidence, you
confirm or adjust them behind a gate, and only confirmed lines enter an append-only ledger. **No
hour is billable without a resolving evidence reference and a recorded human confirmation.**

**Status.** Status is already latent in the same logs plus the documents' own status lines, and this
project has an unusually sharp definition of "done" that a status agent must not blur: the
verification levels V2–V5 in `agents/WORKFLOW.md`. Both live features currently stand at **V3
(accepted by the target, content confirmed by query)** with **V4 (a human opened and saved it)**
outstanding. A status agent that reports those as "deployed ✅" would be committing this project's
single most expensive recorded mistake in a new place.

Three design consequences fall out, and they are the whole of it:

1. **Hours are proposed by a script and authorised by you.** The agent never computes a total by
   hand and never invents a session. `scripts/verify-billing-ledger.py` fails the gate if an
   evidence reference does not resolve to a real log line or commit.
2. **A DEV deploy is an accounting *trigger*, not a billing event.** `logs/pipeline.log` shows
   **five** DEV deploys, four of them for one feature on one afternoon. Billing per deploy would
   invoice that afternoon four times. The ledger's `statement` field and a non-overlap invariant are
   what make a repeated trigger safe.
3. **A statement discloses the verification level it is billing against.** V3 work is billed as V3
   work. This is `C-TECH-053` applied to an invoice.

The billing loop runs **alongside** the delivery flow, exactly like the learning loop — never inside
it. A billing failure must not be able to halt a deploy.

**And a fourth, added in revision 2.** The quoting workbook is the commercial authority, and adding it
to `docs/Import/` converts the weakest part of this design into its strongest. Without it the system
can only ask *"are we over the phase range?"*. With it, every hour maps to a quoted task **or it does
not** — and unmapped work is either a chargeable change order or internal rework, a distinction worth
more than everything else in this document combined. It also answers, mechanically, whether the WBS
0.2–0.7 provisioning work already done here was ever quoted (§2.6b).

---

## Part 1 — What the repo already has

### 1.1 The two requests

| # | Request | Trigger | Output |
|---|---|---|---|
| A | "list the hours I can bill to the customer" | a feature reaches the DEV environment | a draft billable-hours statement, gated |
| B | "queried directly from the chat for a status update" | you ask, any time | a status block in chat, no gate, read-only |

B must be **cheap** (it will be asked often) and **read-only** (it must never mutate delivery state).
A must be **auditable** (it ends up in front of a customer).

### 1.2 The evidence that already exists, on real data

Reconstructing 2026-08-16 and 2026-08-17 from what is on disk today, with a 90-minute idle gap:

| Session | Evidence in the repo | Span | Feature |
|---|---|---|---|
| 08-16 A | `build.log` 16:14 (build #5) · `pipeline.log` 16:46, 17:17, 17:55 | 16:14→17:55 = 1.68h | revitalise-grant-automation |
| 08-16 B | `pipeline.log` 21:09 · `git` 1faf2b4 21:26 | 21:09→21:26 = 0.28h | revitalise-grant-automation |
| 08-17 A | `build.log` 16:10 (build #6) | single point = 0.00h | revitalise-form-field-corrections |
| 08-17 B | `git` 35521fb 20:35 · `pipeline.log` 20:45 · `git` 6f84354 21:15 | 20:35→21:15 = 0.67h | revitalise-form-field-corrections + system |

The reconstruction is genuinely useful and obviously incomplete. 08-16 session A's span is 1.68h, and
the `build.log` entry for build #5 describes decompilation-grade diagnostic work, a BLOCKED-then-
UNBLOCKED secret-scan incident and three stale test assertions fixed — that did not happen inside
1.68 hours of human attention, and the first log line is written *after* the work that produced it.
08-17 session A is a single timestamp with a span of zero.

**This is the central fact of the design.** Evidence span is a **lower bound on elapsed time** and
elapsed time is **neither bound on billable human time**. The script's job is to hand you a
pre-filled line with its evidence attached; your job is to set the number. That division is why the
gate exists, and why it cannot be automated away — the same shape as V4 in
`agents/pipeline-agent.md`.

### 1.3 The budget baseline that already exists

`docs/plans/revitalise-grant-automation-plan.md` §10 carries a real bottom-up estimate:

- **106–160 build hours**, midpoint 133, for the seven automations only
- per-automation hours (#1 Form validation … #7 Duplicate check) with T-shirt sizes
- per-phase: Phase 1 **38–58h**, Phase 2 16–22h, Phase 3 44–66h, Phase 4 8–14h
- an explicit carve-out: the range **excludes** WBS 0.1–0.7 (environments, service account, tables,
  roles, connector policy, retention jobs) — and §10's own warning that Phase 0 is treated as
  "not our problem" by the source estimate

So burn-against-estimate is computable on day one, and the carve-out is exactly the thing that will
cause a commercial argument later. The statement should show WBS 0.x work on its own lines, against
"no source estimate", rather than silently inflating the 106–160 figure.

This is the **weakest** part of the design as first written, and §2.6 replaces it: the estimate above
is a phase range transcribed into an SDD, whereas the document the customer was actually quoted from
is a task-level workbook that this repository has never held.

### 1.4 What is missing

Everything commercial. `grep -ril 'billab|invoice|timesheet|rate card'` across the repo returns
nothing. There is no rate card, no ledger, no client/engagement identity, no notion of billable
versus written-off, and no route in `agents/lead-agent.md` for either request.

---

## Part 2 — The five problems that decide the design

### 2.1 Hours cannot be derived, only proposed

Covered in §1.2. The consequence is a two-file split that must not be blurred:

| | Written by | Authority |
|---|---|---|
| candidate sessions | `scripts/reconstruct-worklog.py`, deterministic, no model | a **proposal**, disposable, lives in the scratchpad |
| `logs/worklog.jsonl` | `pm-agent`, **only after `APPROVE TIMESHEET`** | the ledger of record |

The reconstruction script must never write to the ledger. If it could, the system would be
generating its own invoices.

### 2.2 A DEV deploy is not a billing event

`logs/pipeline.log`, verbatim dates: `08-16 16:46`, `08-16 17:17`, `08-16 17:55`, `08-16 21:09`,
`08-17 20:45`. Four DEV deploys of `revitalise-grant-automation` in five hours, each a legitimate
`SUCCESS`, each fixing something the previous one revealed.

If "deployed to DEV" meant "raise a bill", that afternoon is billed four times. Therefore:

- the DEV deploy triggers **accounting** — reconstruct, present, confirm — not invoicing
- a session, once written, carries `statement: null` until an issued statement claims it
- `scripts/verify-billing-ledger.py` fails if any session id appears on more than one issued
  statement, and if any two sessions on one date overlap
- statements are issued on a **period or phase** boundary, on your instruction, not per deploy

Accounting per deploy and issuing per period is also the cheaper habit, and it is this project's own
lesson: *"The fifteen-attempt DEV import produced one document, written afterwards, from memory.
Fifteen entries written as they happened would have cost nothing and lost nothing."*
(`skills/how-to-log-an-improvement.md` §1).

### 2.3 Billing "complete" at V3 is a claim this system forbids

`agents/WORKFLOW.md` → Verification levels states what each stage may claim. Pipeline deploy claims
**V3 accepted**; only a named human opening and saving each component reaches **V4 usable**.

Both live features are at V3 with V4 explicitly outstanding — `pipeline.log` 08-17 20:45 says so in
its own words: *"Level reached: V3. V4 (human open-and-save + REV Trustee-role read confirming
D-1/D-6) outstanding — cannot be performed by this session."*

`IMP-0012` is the finding that makes this a rule rather than pedantry: three components imported
cleanly, were queryable, and could not be opened or saved by a maker. A statement claiming "Automation
#1 delivered" against V3 evidence is the invoice version of that failure. The design therefore states
the level per deliverable on the statement, and `C-COM-002` blocks the word "complete" above the
level actually reached.

This is not a reason to withhold billing. V3 work is real work and is billable as such. It is a
reason to bill it accurately, which is also the position that survives a customer challenge.

### 2.4 Rework attribution is a commercial decision, and the repo already knows which work was rework

`logs/improvement-log.jsonl` carries `severity: friction|rework|blocker` and `cost` in concrete units
per finding — 26 entries today. That makes it mechanically possible to identify hours spent on
internally-caused rework: the classid guess (`IMP-0014`), the packer-contract guesses (`IMP-0011`,
x4 in its class), the gate that could not fail (x6).

The system must not decide what to do about that. It must **surface** it, apply the policy you declare
in `config/billing.yml` → `rework_policy`, and disclose the result. Three defensible policies exist
(`billable`, `non_billable`, `billable_with_disclosure`); picking one is a commercial decision, so it
is config, not code. The default in the design is `non_billable` because it is the position that
cannot embarrass you, and because a written-off line that says *"3.5h — internal rework, not
charged"* is worth more in a client relationship than 3.5h of margin.

### 2.5 This repository may be visible to the customer, and the governance model has no route for this request

Two problems, both structural.

**(a) Placement of commercial data.** The working directory is
`OneDrive-SharedLibraries-ArgelisConsultancy/Revitalise Respite Holidays - …`. A SharePoint shared
library named after the client is a plausible place for the client to have access. Rate cards, margin,
and written-off internal-rework lines are Argelis-internal. The design therefore keeps
`config/billing.local.yml` (rates) and `logs/worklog.jsonl` (raw ledger, including write-offs)
**out of git**, commits `config/billing.yml.example`, and commits only **issued** statements plus a
hash manifest of the ledger lines they claim — enough to prove the audit trail without publishing the
internals. If the library turns out to be Argelis-only, this is one `.gitignore` line to reverse; the
reverse mistake is not reversible.

**(b) No route exists for adding a capability.** `agents/lead-agent.md` → Routing has eight rows.
"Add a new capability to the system itself" is not one of them, and `agents/improvement-agent.md` →
Activation Triggers is entirely finding-driven — it converts *defects* into rules. Yet only
`improvement-agent`, behind `APPROVE IMPROVEMENTS`, may edit `agents/`, `constraints/`, `skills/` and
`knowledge/`. So a request to add `pm-agent` has no legal path through the system as written. Logged
as **IMP-0027**; the fix is one routing row and one trigger row, in §3.9.

### 2.6 The commercial authority is a document this repository has never seen

`docs/plans/revitalise-grant-automation-plan.md` §10 names it and records its own blind spot in the
same sentence:

> **Basis:** the source document's own bottom-up estimate, midpoint 133 hours, detailed at task level
> in the accompanying WBS workbook (`Revitalise-WBS-Grant-Automation-v0.4.xlsx`, **not present in
> `docs/Import/`**).

That workbook is the document the customer was quoted from. Everything commercial in this design was,
until now, resting on a **phase range transcribed into an SDD** — 38–58h for Phase 1 — when a
**task-level agreed baseline** exists one folder away from the repository. Adding it to `docs/Import/`
is the single highest-value input to this design, and it changes three things qualitatively rather
than incrementally.

**(a) Scope change becomes detectable.** Without a task-level baseline, the only question the system
can ask is *"are we over the phase range?"* — which surfaces an overrun after it has happened and
cannot distinguish its two causes. With one, every confirmed session maps to a quoted task **or it
does not**, and work that maps to nothing quoted is one of exactly two things:

| Unmapped billable work | What it is | What you do |
|---|---|---|
| the customer asked for something not in the quote | **change order** — chargeable extra | raise it *before* the statement, not after |
| we caused it ourselves | **internal rework** — `rework_policy` decides | write off, or disclose |

Today the design lumps both into "budget burn". That distinction is the most commercially valuable
output the agent can produce, and it is impossible without the workbook.

**(b) It settles an open item on the plan, not just on this design.** §10 carries an unresolved ⚠️ in
its own words: *"The 106–160 hour range covers the seven automations only … The source treats 'Phase 0
setup' as part of #2 and #4. **The architect should confirm whether that provisioning work is inside
or outside the range before the estimate is committed.**"* WBS 0.2 (environments), 0.3 (service
account + CA exception), 0.4 (tables), 0.5 (roles + field security) and 0.7 (retention, connector
policy) is work that has substantially **already been done** on this project. Whether it was quoted
determines whether it is billable. A task-level workbook answers that mechanically; §10's prose
cannot.

**(c) Completion can be measured against what was sold.** Status today can say "two features at V3".
With a baseline it can say "11 of 34 quoted tasks at V4, 6 at V3" — against the scope the customer
agreed to. With one guard: **percent-complete by hours booked is a lie generator.** A task counts as
complete at the verification level its deliverable requires (`C-COM-002`), never because hours were
spent on it.

Three cautions, all of which the design must handle rather than assume away:

1. **A quote is a baseline only if it is the version the customer was quoted from.** `v0.4` is what
   §10 names; whether that is the quoted version, or the latest internal revision, is not something
   the repo can determine. The baseline is pinned by version **and content hash**, and an issued
   statement keeps citing the version that was current when it was issued.
2. **A quote states what was promised, never what was done.** It cannot seed the ledger with actuals.
   It sets the denominator, not the numerator — the open question from §5 about already-invoiced hours
   is unaffected.
3. **A quoting workbook usually carries internal columns.** Day rates, cost basis, margin, discount.
   Committing the raw file to a repository that may be client-visible (§2.5a) publishes those. The
   design commits a *normalised, redacted* baseline and treats the raw workbook the same way it
   treats the rate card.

---

## Part 3 — Design

### 3.1 `agents/pm-agent.md` — the Project Management Agent

**Tier:** `standard` for `BILLING`, de-escalated to `mechanical` for `STATUS`.
Two modes, one file, and a hard boundary: **pm-agent never writes to a delivery artefact, never
approves another agent's gate, and cannot mark work complete.** It reports and it accounts.

```
Mode STATUS   (no gate)     read-only over generated snapshots  → chat block
Mode BILLING  (two gates)   reconstruct → confirm → issue       → docs/billing/<period>-billable-hours.md
```

Activation, mode STATUS:
```
0. Run scripts/collect-project-status.py           (deterministic snapshot, JSON + markdown)
1. Load skills/how-to-report-project-status.md
2. Emit the status block. Every number traceable to the snapshot. No level claimed above evidence.
```

Activation, mode BILLING:
```
0. Read logs/known-failure-modes.md — the sections on declaring success apply directly to billing
1. Read config/billing.yml (+ billing.local.yml if present) — the commercial contract as config
2. Run scripts/reconstruct-worklog.py --since <last-billed-date> → candidates in the scratchpad
3. Run scripts/verify-billing-ledger.py — the existing ledger must be clean BEFORE adding to it
4. Load skills/how-to-account-for-billable-time.md; classify, apply rework_policy, mark non-billable
5. Run scripts/compute-billable-hours.py → totals, rounding, budget burn (never compute by hand)
6. Emit the BILLABLE HOURS gate block; wait for APPROVE TIMESHEET
7. On approval: append confirmed sessions to logs/worklog.jsonl, draft the statement from template
8. Wait for ISSUE STATEMENT <id>; on receipt set statement:<id>, status:BILLED, lock, commit
9. Append findings to logs/improvement-log.jsonl; regenerate the digest
```

`config/models.yml` gains:

```yaml
  pm-agent:
    tier: standard
    rationale: >
      Status reporting is rule-following over a generated snapshot. Deciding what is billable
      is not: it attributes rework, applies a commercial policy, and produces a document that
      goes to a customer. A wrong answer is expensive to reverse in a way a wrong routing
      decision is not — an issued statement can only be corrected by a second statement.
    de_escalate_to_mechanical_when:
      - Mode is STATUS and scripts/collect-project-status.py exited 0
    escalate_to_strategic_when:
      - An already-issued statement must be corrected (credit note)
      - The customer has disputed a line
      - Attribution of rework between internal defect and scope change is contested
      - Reconstructed hours and your declared hours disagree by more than 20% on any session
      - A statement's total would exceed the SDD §10 phase estimate's high bound
```

`de_escalate_to_mechanical_when` is a new key in `models.yml`; the file today has only
`escalate_to_strategic_when`.

### 3.2 `config/billing.yml` — the commercial contract as config

Structure committed as `billing.yml.example`; rates in the gitignored `billing.local.yml`.

```yaml
engagement:
  client:            "Revitalise Respite Holidays"
  supplier:          "Argelis Consultancy"
  contract_basis:    time_and_materials      # | fixed_fee_per_deliverable | capped_tm
  approver:          "Xander Lykopoulos"
  currency:          GBP
  vat:               { applies: false, note: "reverse charge / NL-UK — confirm" }

rate_card:                                    # billing.local.yml
  consultancy:       { rate: 0,  description: "requirements, workshops, client calls" }
  development:       { rate: 0,  description: "build, schema, flows, forms, code" }
  deployment:        { rate: 0,  description: "environment prep, imports, verification" }
  project_management:{ rate: 0,  description: "planning, reporting, coordination" }
  travel:            { rate: 0,  billable: false }

rounding:
  increment_hours:   0.25
  rule:              nearest                  # | up
  min_session_hours: 0.25
  max_hours_per_day: 10                       # invariant, not a target

policy:
  rework_policy:     non_billable             # | billable | billable_with_disclosure
                                              # applies to sessions whose evidence is an
                                              # improvement-log finding with severity rework|blocker
                                              # and an internal root_cause
  non_billable_features: [sar-lifecycle]      # the template/demo feature in routing.log — excluded
                                              # explicitly, never by silent omission
  system_work:       non_billable_with_disclosure
                                              # work on this multi-agent system itself (agents/,
                                              # skills/, constraints/, scripts/) — tooling, not
                                              # deliverable. 3 of 9 commits are this.
  disclose_non_billable: true                 # written-off lines appear on the statement at 0.00

budget:
  baseline: config/wbs-baseline.yml            # generated from the quoted workbook — §3.10.
                                               # This file is the authority. Do NOT retype hours here.
  fallback:                                    # used ONLY while no baseline exists
    source: "docs/plans/revitalise-grant-automation-plan.md#10-effort-estimate"
    total:  { low: 106, high: 160, midpoint: 133, excludes: "WBS 0.1–0.7 (Phase 0 setup)" }
    phases:
      phase_1: { automations: ["#1 Form validation", "#4 Intake", "#2 Scoring"], low: 38, high: 58 }
      phase_2: { automations: ["#3 Acceptance workflow"],                        low: 16, high: 22 }
      phase_3: { automations: ["#5 Anonymisation", "#6 Trustee portal"],         low: 44, high: 66 }
      phase_4: { automations: ["#7 Duplicate check"],                            low: 8,  high: 14 }

deliverable_map:                              # feature slug → quoted WBS task ids (§3.10)
  revitalise-grant-automation:       { phase: phase_1, automations: ["#1", "#4", "#2"], wbs: [] }
  revitalise-form-field-corrections: { phase: phase_1, automations: ["#1"], wbs: [],
                                       note: "corrections after V4 review — may be unquoted" }
scope:
  unmapped_billable: change_order_required     # a billable session mapping to no quoted task must
                                               # carry scope: change_order + reason, or be written off.
                                               # Enforced by verify-billing-ledger.py invariant 10.

evidence_sources:
  - { kind: git,   path: "." }
  - { kind: log,   path: logs/build.log }
  - { kind: log,   path: logs/pipeline.log }
  - { kind: log,   path: logs/routing.log }
  - { kind: jsonl, path: logs/improvement-log.jsonl, field: ts }
session:
  idle_gap_minutes:  90
  lead_in_minutes:   45        # work precedes its first log line; a floor, never a ceiling
  attribute_by:      ["log feature field", "changed paths", "explicit human override"]

statements:
  numbering: "ST-{YYYY}-{MM}"
  issue_on:  period            # | phase | on_request
  output_dir: docs/billing/
```

### 3.3 `logs/worklog.jsonl` — the ledger of record

Append-only, one JSON object per line, same discipline as `improvement-log.jsonl`: never rewrite,
never reorder. Written by `pm-agent` only, only after `APPROVE TIMESHEET`.

```json
{"id":"WL-0007","date":"2026-08-16","start":"15:30","end":"18:00","hours":2.5,
 "feature":"revitalise-grant-automation","work_type":"development",
 "activity":"build #5: live pac solution check, secret-scan relocation, 3 stale schema assertions fixed",
 "deliverables":["#1 Form validation"],"wbs":null,
 "evidence":["logs/build.log:2026-08-16 16:14","logs/pipeline.log:2026-08-16 16:46"],
 "evidence_span_hours":1.68,"source":"reconstructed",
 "billable":true,"non_billable_reason":null,
 "confirmed_by":"Xander Lykopoulos","confirmed_at":"2026-08-17T22:10",
 "statement":null,"status":"CONFIRMED"}
```

| Field | Why it is not optional |
|---|---|
| `evidence` | every entry must resolve to a real log line or commit — the anti-fabrication hook |
| `evidence_span_hours` | keeps the machine's observation and your number visibly separate |
| `source` | `reconstructed` \| `human-declared` (meetings, calls, portal work the repo cannot see) |
| `confirmed_by` / `confirmed_at` | no confirmation, no bill (`C-COM-001`) |
| `statement` | `null` → `ST-nnnn`; the double-billing guard |
| `status` | `CONFIRMED` → `BILLED`; `BILLED` lines are immutable |

`human-declared` sessions have no resolving evidence by definition. They are legitimate and they are
the honest hole in the scheme: the ledger records them as such, and `verify-billing-ledger.py`
reports their share of each statement so that a statement which is 80% un-evidenced is visible as
that, rather than passing as reconstructed fact.

### 3.4 Four scripts — because in this repo a script beats a constraint row beats a paragraph

`constraints/README.md` item 5 and `agents/improvement-agent.md` anti-bloat limit 4 both say it, and
`C-TECH-049` is the proof: the rule worked when the script was written, not when the row was added.

| Script | Reads | Writes | Job |
|---|---|---|---|
| `scripts/reconstruct-worklog.py` | git, the three action logs, improvement-log `ts`, doc mtimes | scratchpad JSON + markdown table | cluster timestamps into candidate sessions; attribute to feature; classify work type; report `evidence_span` and `proposed` separately; **never touches the ledger** |
| `scripts/compute-billable-hours.py` | `worklog.jsonl`, `billing.yml` | stdout JSON + markdown | all arithmetic: rounding per policy, totals per work type / feature / phase / rate, budget burn vs §10, non-billable subtotals. **No agent adds hours by hand** |
| `scripts/verify-billing-ledger.py` | `worklog.jsonl`, `billing.yml`, `docs/billing/*.md` | exit code + report | the gate. `--check` for CI |
| `scripts/collect-project-status.py` | docs' status lines, the three logs, Dev Summary §10, pipeline level lines, improvement-log counts, ledger totals | stdout JSON + markdown | the status snapshot, so STATUS mode is cheap and cannot hallucinate |

`verify-billing-ledger.py` invariants — every one of these fails the gate:

1. ids unique and sequential; dates ISO; `hours > 0`; `hours ≤ max_hours_per_day` per date
2. no two sessions overlap on the same date
3. every `evidence` reference **resolves** — the named log line exists at that timestamp, or the
   commit exists. An unresolvable reference is a fabricated hour, and this is the billing form of
   `exit-zero-does-not-mean-created` (x3 in the digest)
4. `confirmed_by` non-empty on every line
5. no session id on more than one issued statement; `status: BILLED` lines byte-identical to the
   hash recorded when the statement was issued
6. `work_type` exists in the rate card; `feature` not in `non_billable_features`
7. statement totals **recomputed** and compared to the numbers printed in the statement markdown
8. `source: human-declared` share reported per statement
9. no session dated in the future; no session before the engagement start

**It ships with known-bad fixtures.** `scripts/fixtures/billing/` gets one ledger per invariant, each
of which must fail, plus one clean ledger which must pass; CI runs the fixture suite. The most
recurring class in `logs/known-failure-modes.md` is `gate-cannot-fail` at **x6** — including a HARD
compliance gate that was a silent no-op from the day it was written (`IMP-0007`). A billing gate
introduced without proof that it can fail would be the seventh, in the one place that reaches a
customer.

### 3.5 The two chat outputs

**Mode STATUS** — this is what "queried directly from the chat" produces. Illustrative, populated
from today's real logs except the hours, which no ledger has yet:

```
PROJECT STATUS — Grant Application Process        as of 2026-08-17 22:10
Phase 1 of 4 · Form validation, Intake, Scoring

Feature                              Stage   Level   Last activity
revitalise-grant-automation          DEV     V3      2026-08-16 21:09  pipeline
revitalise-form-field-corrections    DEV     V3      2026-08-17 20:45  pipeline

To reach V4: human open-and-save of the Application form; REV Trustee-role read (D-1/D-6)
To reach TST/ACC: manual Deploy in the Pipelines UI (ADR-007) — not automatable, your click
Blockers      WBS 0.3 service account CA exception — Wanstor — open since 2026-08-10 (7d)
              rev_breaktype / rev_applicanttype orphaned option values — maker portal — 1d
Assumptions   0 OPEN  (A-001 closed 2026-08-16)
Findings      26 NEW in improvement-log — ≥10 threshold reached, improvement-agent is due
Hours         0.00 confirmed · 4.75h of candidates unconfirmed · budget Phase 1 38–58h
Next action   your V4 open-and-save, then APPROVE TIMESHEET for the 4.75h of candidates
```

Rules, from `skills/how-to-report-project-status.md`: report the level reached, never a level above
it; a document existing is not progress (`IMP-0012`); every blocker names an owner and an age;
estimate and actual are never in the same column without labels.

**Mode BILLING** — the gate block:

```
BILLABLE HOURS — DRAFT  ST-2026-08          docs/billing/2026-08-billable-hours.md
Trigger: DEV deploy of revitalise-form-field-corrections, 2026-08-17 20:45, level reached V3

Candidates from evidence: 4 sessions   evidence span 2.63h → proposed 4.75h (span + lead_in)
 WL?  date        span         proposed  type         activity                                    evidence
  1   2026-08-16  16:14–17:55     2.50h  development  build #5, secret-scan, 3 stale assertions   build.log, pipeline.log×3
  2   2026-08-16  21:09–21:26     1.00h  deployment   option-set + type-change deploy             pipeline.log, git:1faf2b4
  3   2026-08-17  16:10           0.75h  development  build #6, FR-016 gate + description defect  build.log
  4   2026-08-17  20:35–21:15     0.50h  deployment   schema delta + intake flow + forms          git:35521fb, pipeline.log
Proposed non-billable: 0.00h            System work (agents/, skills/, scripts/): 1 session flagged
Unresolvable evidence refs: 0           Overlaps with existing ledger: 0        Future-dated: 0
Budget: Phase 1 38–58h · 0.00h billed to date + 4.75h proposed = 4.75h · 12% of low bound
Verification: all deliverables at V3; V4 outstanding. Statement states the level; claims no completion.
CONSTRAINT CHECK  Commercial HARD: 3/3  violations: NONE   Overall: PASS
IMPROVEMENT LOG: 0 entries appended — none  |  digest regenerated: YES

These numbers are a floor derived from timestamps, not a record of your attention. Edit any line
— hours, type, billable flag — or add sessions the repo cannot see (calls, portal work, Emily's
walkthrough) as human-declared.
Respond APPROVE TIMESHEET to write 4 sessions to logs/worklog.jsonl, or HOLD.
Then ISSUE STATEMENT ST-2026-08 to lock them and produce the customer document.
```

That last paragraph is load-bearing. It is the difference between a tool that helps you invoice and a
tool that invents invoices.

### 3.6 Gates and keywords

`agents/WORKFLOW.md` → Human Gate Keywords gains two rows:

| Gate | Proceed | Pause / Revise |
|---|---|---|
| **Confirm billable hours into the ledger** | **`APPROVE TIMESHEET`** | `HOLD` |
| **Issue a statement to the customer** | **`ISSUE STATEMENT <id>`** | `HOLD` |

Two keywords rather than one, because they authorise different things. `APPROVE TIMESHEET` writes to
an internal append-only ledger — reversible in practice by a correcting entry. `ISSUE STATEMENT` is
outward-facing and irreversible: once a statement is issued it is immutable, and a mistake is
corrected only by a second statement that references the first. That asymmetry is the same one
`APPROVE TENANT` and `APPROVE PRD` already encode.

`STATUS` mode has no gate. It writes nothing.

### 3.7 Constraints — a new file, three rows

Billing rules are not Revitalise's domain rules and not the platform's technology rules. Putting them
in `domain-constraints.md` would drag them into scope for plan/architect/development/test agents,
which is wrong: none of those agents should be checking a rate card. `constraints/README.md`'s
directory structure already anticipates additional files per concern area.

**New:** `constraints/commercial/commercial-constraints.md` · IDs `C-COM-nnn` · Owner: Engagement
Owner (Argelis) · Checked by: `pm-agent` only.

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| `C-COM-001` | No hour may be billed without (a) at least one evidence reference that resolves to a real log line or commit, or an explicit `source: human-declared`, **and** (b) a recorded `confirmed_by` human confirmation | HARD | pm-agent | An agent that can originate a billable hour can originate an invoice. Evidence span is a lower bound on elapsed time and no bound at all on billable attention (§1.2) | `scripts/verify-billing-ledger.py` invariants 3–4 + fixtures |
| `C-COM-002` | A statement may not describe a deliverable as complete, delivered, or accepted above the verification level actually reached, as recorded in `logs/pipeline.log` | HARD | pm-agent | `C-TECH-053` applied to an invoice. `IMP-0012`: three components imported cleanly, were queryable, and no maker could open them. Both live features are V3 with V4 outstanding | `scripts/collect-project-status.py` cross-check of claimed vs logged level |
| `C-COM-003` | A confirmed session may appear on at most one issued statement; an issued statement is immutable and is corrected only by a new statement that references it | HARD | pm-agent | Five DEV deploys, four for one feature in five hours (§2.2). A per-deploy trigger without this rule bills that afternoon four times | `scripts/verify-billing-ledger.py` invariants 5, 7 |

Three rows, which is also the `improvement-agent` per-review cap. `constraints/README.md` needs
three edits: the directory-structure block, the ID-format block, and the which-agents-check-which
matrix.

### 3.8 Two skills

| Skill | Contents |
|---|---|
| `skills/how-to-account-for-billable-time.md` | evidence → session → work type → rounding; the span-is-a-floor rule; what must **never** be billed (agent wall-clock you were not present for · time already on an issued statement · estimated-but-not-performed work · internal rework where policy says non-billable); how to record off-repo work as `human-declared`; how to disclose a write-off; how to split a session across two features so the parts sum to the whole |
| `skills/how-to-report-project-status.md` | the status block format; report the level reached, never above it; a document's existence is not progress; blockers carry an owner and an age; estimate and actual are labelled; what to say when the answer is "nothing moved since you last asked" |

Both loaded inline at the step that needs them, per `CLAUDE.md` → When Delegating.

### 3.9 Learning-loop and routing integration

`pm-agent` writes findings like every other agent. Its highest-value trigger is the one
`skills/how-to-log-an-improvement.md` already ranks first: **any human correction of agent output.**
Every time you raise a proposed 2.50h to 4.00h, that is a calibration signal for
`reconstruct-worklog.py`'s `lead_in_minutes` and for the work-type classifier. Three such corrections
in the same direction is a config change, not three corrections.

Three new classes, which must be added to the `SECTIONS` routing table in
`scripts/generate-known-failure-modes.py` or they land in the digest's *Unrouted* section:

```python
    (
        "before-billing",
        "Before you bill an hour or report status",
        ("billable-hour-without-resolving-evidence",
         "status-claimed-above-verification-level",
         "session-billed-twice",
         "reconstruction-underestimates-attention"),
    ),
```

`agents/lead-agent.md` → Routing gains four rows:

| User Intent | Route To |
|---|---|
| Billable hours, timesheet, invoice, "what can I bill" | `pm-agent` (**billing mode**) |
| Status update, progress, "where are we", "what is blocked" | `pm-agent` (**status mode**) |
| A DEV deploy completed | `pm-agent` (**billing mode**), after the pipeline log line |
| **Request to add a new capability to this system** | `improvement-agent` (**capability mode**) |

`agents/improvement-agent.md` → Activation Triggers gains one row — *"the reviewer requests a new
system capability; the authorising artefact is a design document in `docs/improvements/`"* — and the
anti-bloat limits gain a carve-out: a capability review is not a defect review, so limit 1 ("every new
constraint cites the `IMP-` ids that justify it") is satisfied by citing the design document plus the
findings the design draws on. Without this, §2.5(b) recurs on the next capability request.

`agents/pipeline-agent.md` gains one step at the end of a successful DEV stage:

```
HANDOFF | from:pipeline-agent | to:pm-agent | feature:<slug> | status:READY | doc:<pipeline.log line>
```

with one explicit rule: **a billing or status failure never halts, retries, or rolls back a deploy.**
The commercial loop is a side branch, drawn the way the learning loop is drawn in
`agents/WORKFLOW.md`:

```
pipeline-agent, on DEV deploy success ──► pm-agent (BILLING)
                                              │
                                    reconstruct → present
                                              │
                                    [APPROVE TIMESHEET]
                                              ▼
                                    logs/worklog.jsonl  (append-only, confirmed)
                                              │
                                    [ISSUE STATEMENT <id>]
                                              ▼
                                    docs/billing/<period>-billable-hours.md   (immutable)

you, any time ──► pm-agent (STATUS) ──► scripts/collect-project-status.py ──► chat block
```

### 3.10 The quoted baseline — intake, normalisation, and the four things it changes

**Provenance.** The workbook lands in `docs/Import/` like every other externally-authored source, and
is never read at billing time. It is intaked **once** into a committed, diffable, machine-readable
baseline, pinned to the source by content hash:

```yaml
# config/wbs-baseline.yml — GENERATED by scripts/import-wbs-baseline.py. Do not hand-edit.
source:
  file:              docs/Import/Revitalise-WBS-Grant-Automation-v0.4.xlsx
  version:           v0.4
  sha256:            <64 hex>            # re-derived by --check; a silent workbook edit fails CI
  quoted_to_customer: true
  quote_date:        2026-07-17
  quoted_total_agreed: null              # the number on the accepted quote, if one exists
tasks:
  - { id: "0.2", name: "Environment setup + UK residency verification",
      phase: phase_0, automation: null, low: 0, high: 0, in_quoted_total: false }
  - { id: "1.1", name: "…", phase: phase_1, automation: "#1", low: 0, high: 0, in_quoted_total: true }
totals:
  quoted:     { low: 0, high: 0 }        # sum of in_quoted_total tasks
  all_tasks:  { low: 0, high: 0 }
reconciliation:
  sdd_section_10:  { low: 106, high: 160 }
  matches_quoted:  null                  # computed; a mismatch is a finding, not a rounding note
```

**No new dependency.** `openpyxl` and `pandas` are both absent from this machine's Python, and the
build gates run in CI on the standard library. `.xlsx` is a zip of XML, so
`scripts/import-wbs-baseline.py` reads it with `zipfile` + `xml.etree` over `xl/worksheets/sheet1.xml`
and `xl/sharedStrings.xml` — about sixty lines, no install, and it cannot break a build by pinning a
version. Fallback if the workbook's layout resists that: export one sheet to CSV and parse the CSV,
which is already the convention in `docs/Import/` — both existing `.xlsx` files sit next to a
hand-exported `(Sheet1).csv` sibling. The script has a `--check` mode, exactly like
`generate-known-failure-modes.py`, so a workbook that changes without the baseline being regenerated
is caught rather than silently ignored.

**Redaction.** If the workbook carries day rates, cost basis, margin or discount columns, the
generated baseline takes `id`, `name`, `phase`, `automation`, `low`, `high`, `in_quoted_total` and
nothing else, and the raw workbook is treated as `billing.local.yml` is — out of git (§2.5a). Hours
and quoted price are things the customer has already seen; your cost basis is not.

**What it changes:**

| # | Change | Where |
|---|---|---|
| 1 | `billing.yml` stops carrying transcribed hours; `budget.baseline` points at the generated file, and the §10 phase ranges demote to `fallback`, used only until the baseline exists | §3.2 |
| 2 | A confirmed session gains `wbs: ["1.1","1.2"]` and, when it maps to nothing quoted, `scope: change_order` with a reason | §3.3 |
| 3 | `verify-billing-ledger.py` gains **invariant 10**: every billable session maps to ≥1 baseline task **or** carries `scope: change_order` with a non-empty reason. Unmapped, unflagged billable work fails the gate | §3.4 |
| 4 | `verify-billing-ledger.py` gains **invariant 11**: `reconciliation.matches_quoted` must be resolved. If the workbook's quoted total does not match SDD §10's 106–160, the SDD misquotes the commercial baseline and that is a finding, not a footnote | §3.4 |

**No fourth constraint.** Invariants 10 and 11 are deliberately script checks rather than
`C-COM-004`/`005`. The improvement-agent's cap is three constraints per review, and anti-bloat limit 4
prefers the most mechanical home available — *"a script beats a constraint row beats a paragraph"*.
`C-COM-001..003` stay as they are.

**The statement gains a quoted-vs-actual table**, which is the part a customer actually reads:

```
QUOTED VS ACTUAL — baseline Revitalise-WBS-Grant-Automation-v0.4.xlsx (sha 9f2c…), quoted 2026-07-17

WBS   Task                                     Quoted      Booked   Level   Status
0.4   Dataverse tables to the data model         8–12h       9.50h    V3     within quote
1.1   Form validation — specification            4–6h        4.75h    V4     within quote
1.2   Form validation — build + validate         8–12h      13.25h    V3     ⚠ over high bound
—     Option-set corrections after V4 review       —         3.50h    V3     CHANGE ORDER (pending)
—     Multi-select classid diagnosis + fix         —         2.00h     —     internal rework, not charged
                                              ────────    ────────
Phase 1 quoted 38–58h                          38–58h      33.00h            57–87% of range
```

**The status block gains one line**: `Scope  11 of 34 quoted tasks at V4 · 6 at V3 · 2 change orders
pending your approval`. Counted at verification level, never by hours booked.

**Intake governance — the same gap as IMP-0027, one folder over.**
`skills/how-to-intake-external-documents.md` is declared *"Used by plan-agent and architect-agent"*,
and its two checklists are SDD- and TAD-shaped. A commercial baseline maps to neither, so no agent
currently owns it — dropping the workbook into `docs/Import/` today would leave it unread by anything.
Two small edits fix it, and the skill's four principles (*adopt don't author · gaps become open items
· provenance is mandatory · same gates, same rigour*) transfer to a quote verbatim:

- `agents/pm-agent.md` gains a third mode, **BASELINE INTAKE**, gated by `APPROVE BASELINE`
- `skills/how-to-intake-external-documents.md` gains a *Commercial Baseline Intake Checklist
  (pm-agent)*: task id · task name · low/high hours · phase · automation/FR link · in-quoted-total
  flag, with `MISSING` on any of the first three being gate-blocking

**One knock-on outside this design.** Adding the file makes §10's *"not present in `docs/Import/`"*
false, and the ⚠️ Phase-0 question answerable. That is capture trigger 2 — *reality contradicted a
document in this repo* — so it is logged, and `plan-agent` is routed to revise §10 to state whether
WBS 0.x provisioning is inside or outside the quoted range. Do not let `pm-agent` quietly answer a
question the SDD reserved for the architect.

---

## Part 4 — File-by-file change list

**New — 18 files**

| Path | What |
|---|---|
| `agents/pm-agent.md` | the agent, three modes, tier + de-escalation, activation, gates, logging |
| `config/billing.yml.example` | committed structure of the commercial contract (§3.2) |
| `config/billing.local.yml` | rates and client identity — **gitignored** (§2.5a) |
| `config/wbs-baseline.yml` | **generated** from the quoted workbook; the commercial baseline (§3.10) |
| `scripts/import-wbs-baseline.py` | stdlib `.xlsx` → baseline yml, hash-pinned, `--check` mode (§3.10) |
| `constraints/commercial/commercial-constraints.md` | `C-COM-001…003`, owner Engagement Owner |
| `skills/how-to-account-for-billable-time.md` | the accounting procedure and its prohibitions |
| `skills/how-to-report-project-status.md` | the status procedure and its honesty rules |
| `scripts/reconstruct-worklog.py` | evidence → candidate sessions (never writes the ledger) |
| `scripts/compute-billable-hours.py` | all arithmetic, rounding, budget burn |
| `scripts/verify-billing-ledger.py` | 9 invariants, `--check`, the gate |
| `scripts/collect-project-status.py` | the status snapshot |
| `scripts/fixtures/billing/` | one known-bad ledger per invariant + one clean; proves the gate can fail |
| `templates/billable-hours-statement-template.md` | the customer-facing statement |
| `templates/status-report-template.md` | written status report, for when chat output must become a document |
| `logs/worklog.jsonl` | the ledger — **gitignored**, created empty |
| `logs/pm.log` | one line per pm-agent action, existing log format |
| `docs/billing/README.md` | what is committed here and what deliberately is not |

**Edited — 12 files**

| Path | Change |
|---|---|
| `CLAUDE.md` | repo layout additions; a short **Commercial Rules** block (hours are evidence-based and human-confirmed; nothing is billed twice; issued statements are immutable; the baseline is generated, not retyped) |
| `agents/WORKFLOW.md` | roster row; three gate keywords; the commercial-loop diagram; `logs/pm.log` in the logging table; `to:pm-agent` noted as valid |
| `skills/how-to-intake-external-documents.md` | a third checklist — *Commercial Baseline Intake (pm-agent)* (§3.10) |
| `docs/plans/revitalise-grant-automation-plan.md` | §10: remove *"not present in `docs/Import/`"*, answer the ⚠️ Phase-0 question. **By plan-agent, not by this change** — routed separately |
| `agents/lead-agent.md` | four routing rows (§3.9) |
| `agents/pipeline-agent.md` | handoff to pm-agent after a successful DEV stage, with the never-blocks rule |
| `agents/improvement-agent.md` | capability-mode trigger + the anti-bloat carve-out for capability reviews |
| `config/models.yml` | `pm-agent` entry; the new `de_escalate_to_mechanical_when` key |
| `constraints/README.md` | directory structure, ID format, agent×constraint matrix |
| `scripts/generate-known-failure-modes.py` | the `before-billing` SECTIONS entry (§3.9) |
| `.github/workflows/ci.yml` | `verify-billing-ledger.py --check` + the fixture suite in the validate job |
| `.gitignore` | `config/billing.local.yml`, `logs/worklog.jsonl`, `docs/billing/drafts/` |

Count: 18 new (14 of substance + 4 stubs/logs), 12 edited.

---

## Part 5 — Decisions I need from you

Seven, and only the first two block implementation.

| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | **Contract basis** | `time_and_materials` · `fixed_fee_per_deliverable` · `capped_tm` (T&M capped per phase) | `capped_tm` — and the workbook may already answer this. If the customer accepted a quoted total, the basis is capped or fixed and the cap is the workbook's own number, not a range transcribed into the SDD. Set `quoted_total_agreed` in the baseline and the question closes itself |
| 2 | **Rework caused by our own defect** | `non_billable` · `billable` · `billable_with_disclosure` | `non_billable`, disclosed at 0.00 on the statement. The system can identify these mechanically from the improvement log; a visible write-off is worth more than the margin |
| 3 | **Is this git repository visible to Revitalise?** | yes · no · unsure | Assume **yes** until confirmed. Rates and write-offs stay in gitignored files; only issued statements are committed. One line to reverse if the answer is no |
| 4 | **Work on this multi-agent system itself** (3 of 9 commits) | billable as tooling · non-billable · disclosed at 0.00 | `non_billable_with_disclosure`. It is real work and it is not what they bought; showing it at 0.00 makes the point better than hiding it |
| 5 | **Statement cadence** | monthly · per phase · on request | Monthly, with accounting on every DEV deploy. Accounting little and often is this project's own lesson (§2.2); issuing monthly is what finance departments expect |
| 6 | **Is `v0.4` the version the customer was quoted from?** | yes · no, it was `v0.n` · there was no formal quote, only an estimate | Needed before the baseline is pinned. If there was no accepted quote, the workbook is an *estimate* baseline and every over-bound line is a conversation, not a breach |
| 7 | **Does the workbook carry internal cost / margin / day-rate columns?** | yes · no · unsure | If yes or unsure, the generated baseline takes hours only and the raw workbook stays out of git. Interacts with decision 3 — the leak is not reversible |

Decisions 3–5 have safe defaults and can be changed in `billing.yml` later. Decisions 1 and 2 shape
what `compute-billable-hours.py` computes, so I need them before writing it. Decisions 6 and 7 are
needed at baseline intake, which is now step 2 of the build order.

One thing I cannot recover and will need from you once: **the engagement start date and any hours
already invoiced to Revitalise before today.** The reconstruction can only see 2026-08-09 onward
(`git log` starts there; `routing.log`'s 2026-04 lines are the `sar-lifecycle` template feature, which
`non_billable_features` excludes). Anything before 08-09, and anything already billed, has to be
seeded into the ledger as `human-declared` with `status: BILLED` — otherwise the first statement will
propose hours you have already charged for.

---

## Part 6 — Recommended order

Each step is independently useful, and nothing in it can bill anything until step 5.

| # | Step | Why here |
|---|---|---|
| 1 | `collect-project-status.py` + `how-to-report-project-status.md` + `pm-agent.md` STATUS mode | Delivers request B on its own. Read-only, no commercial decisions, no gates. Usable the day it lands |
| 2 | **The workbook into `docs/Import/`, `import-wbs-baseline.py`, `config/wbs-baseline.yml`, BASELINE INTAKE mode** | Ahead of `billing.yml`, because the baseline is what `billing.yml` should point at rather than duplicate. It is also independently useful the moment it exists: the quoted-vs-actual denominator, the SDD §10 reconciliation, and the answer to the Phase-0 ⚠️ all arrive with it, before a single hour is accounted |
| 3 | `billing.yml.example` + your answers to decisions 1–2 | The contract has to exist before anything can be classified against it |
| 4 | `reconstruct-worklog.py`, output to the scratchpad only | You can eyeball it against your own memory of 08-16 before anything writes a ledger |
| 5 | `verify-billing-ledger.py` **and its fixtures**, wired into CI | The gate exists before the thing it guards. This ordering is the direct lesson of `gate-cannot-fail` x6 |
| 6 | `compute-billable-hours.py`, `worklog.jsonl`, BILLING mode, the statement template, `C-COM-001…003` | Request A. Nothing here can produce a number the gate has not already been proven able to reject |
| 7 | Routing rows, the pipeline handoff, `CLAUDE.md`, the digest SECTIONS entry, `improvement-agent` capability mode, the intake-skill checklist | Wiring. Last, because the capability is worth wiring only once it works |

Steps 1 and 4 are also the cheap test of the whole idea: if the reconstruction of 08-16 looks
plausible to you, the design is sound; if it looks nothing like your day, `lead_in_minutes` and the
clustering need calibration before anything is built on top of it.

Step 2 is the one that pays for itself before anything else is built. Even with no ledger, no rate card
and no statement, a pinned baseline tells you today whether the WBS 0.2–0.7 provisioning work already
done on this project was inside the quote — which is the largest open commercial question on the
engagement, and the one §10 explicitly declined to answer.

---

## Part 7 — What this design does not do

- It does not compute what you *should* charge. It accounts for what evidence shows and you confirm.
- It does not decide whether unquoted work is chargeable. It flags a `change_order` candidate and
  hands you the quoted baseline it failed to match. Raising it with the customer is yours.
- It does not treat a quote as a record of work. The baseline sets the denominator only (§2.6 caution 2).
- It does not see off-repo work. Meetings, calls, portal clicks and thinking-in-the-shower enter as
  `human-declared` and are marked as such, including on the statement's evidence share.
- It does not decide completion. `pm-agent` reads the level from `pipeline.log`; only your V4
  open-and-save moves it, exactly as today.
- It does not track anyone else's time. Single-supplier engagement, one approver.
- It does not raise invoices, touch accounting software, or send anything to anyone. It produces a
  markdown statement in `docs/billing/`. Sending it stays a human act.
- It does not make the first statement correct without you seeding pre-08-09 and already-invoiced
  hours (§5).

---

## Gate

```
SYSTEM CAPABILITY DESIGN — docs/improvements/2026-08-17-project-management-agent-design.md

Capability:   pm-agent — billable-hours accounting on DEV deploy + on-demand status,
              against the quoted WBS baseline
New files:    18   Edited files: 12   New constraints: 3 (C-COM-001…003, cap 3 respected)
New gates:    APPROVE TIMESHEET, ISSUE STATEMENT <id>, APPROVE BASELINE
Decisions:    7 open — 1 (contract basis) and 2 (rework policy) block implementation;
              6 (quoted version) and 7 (internal columns) block baseline intake
Governance:   this request has no route in the system as written — IMP-0027, fix in §3.9.
              Commercial baseline intake has no owner either — fix in §3.10
Knock-on:     plan §10 states the workbook is "not present in docs/Import/" and leaves the
              Phase-0 scope question to the architect. Adding the file makes the first stale
              and the second answerable — route to plan-agent, not pm-agent
IMPROVEMENT LOG: 1 entry appended — IMP-0027  |  digest regenerated: YES

Answer decisions 1 and 2, then respond APPROVE IMPROVEMENTS to implement,
or APPROVE IMPROVEMENTS step 1 only to take the status half first.
Add the workbook to docs/Import/ and answer 6 and 7 to take step 2 first — recommended,
it is the cheapest step with the largest commercial payoff.
```
