# Project Management Requirements — Re-design on the Contracted WBS

**Author:** lead-agent, live session with Xander Lykopoulos
**Date:** 2026-08-18
**Status:** DESIGN — nothing implemented. Implementation edits `agents/`, `constraints/`, `skills/` and
`CLAUDE.md`, which only `improvement-agent` may do, behind `APPROVE IMPROVEMENTS`.
**Supersedes:** `docs/improvements/2026-08-17-project-management-agent-design.md`. That design was
drafted before the Work Breakdown Structure and the signed Service Agreement were available; it
treated the WBS as a *budget denominator*. Both documents are now in `docs/Import/`, and they make the
WBS something else entirely. §0 explains what changed and why the earlier design is not simply
extended.
**Evidence base:** `docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx` (61 tasks, read via a
stdlib xlsx parse), `docs/Import/Revitalise - Service Agreement - Application Process Automation -
v1.3 (Signed).pdf` (5 pages, read via ToUnicode CMap decode), `src/solutions/RevitaliseGrantAutomation/`,
`docs/plans/revitalise-grant-automation-plan.md` §10, `logs/{build,pipeline,routing}.log`,
`logs/improvement-log.jsonl`.

---

## 0. Executive summary

Yesterday's design asked the WBS one question: *how many hours were quoted, so we can measure burn?*
Reading the actual workbook and the signed agreement together, that framing is wrong in a way that
matters.

**The WBS is not a reference document. It is four things at once:**

| The WBS is… | Because | Consequence |
|---|---|---|
| the **contractual specification** | Build Terms B1 names the Work Breakdown Structure as part of the Agreed Specification, alongside the Automation Solution Design, the Solution Architecture and *the phase acceptance record* — and *"where these conflict, the most recently accepted version prevails"* | keeping it true is a contractual obligation, not admin. The warranty is measured against it |
| the **work queue** | 61 tasks, each with `Depends On`, `Phase`, `Deliverable` — a dependency graph | it can *drive* the development system rather than describe it afterwards |
| the **progress record** | a hand-maintained `Status` column | it is the only statement of project state, and nothing verifies it |
| the **actuals ledger** | it already has `Actual Hours` and `Delta` columns | the instrument exists. **All 61 rows are empty.** |

And the agreement fixes the commercial frame the earlier design had to guess at: **time-and-materials
at €120/hour excl. VAT, invoiced monthly in arrears, payment within 14 days**, against a five-phase
fee schedule totalling **292 hours / €35,040**, with **60-day warranty from each phase's Acceptance**,
**ten business days of hypercare** after each go-live, per-phase liability capped at the fees paid for
that phase, and support after handover explicitly out of scope.

Two of yesterday's open decisions are answered by the contract rather than by preference: the basis is
T&M (decision 1), and defect rework inside a warranty window is free (decision 2) — not because it is
good client relations, but because clause B4 says so.

**Reading the two documents against the repository surfaced five live defects, all with numbers:**

1. The approved SDD §10 misstates the commercial baseline: **106–160 hours over 7 automations**
   against a contract of **292 hours over 9**, with the phase membership wrong as well. Anything
   built on §10 is wrong.
2. WBS task **0.4 is marked `Done`** and its own description names seven Dataverse tables plus an
   Anonymised Statistic snapshot. The solution source contains **four** tables — Applicant,
   Application, Error Log, Setting. Review, Grant, Provider, Bank Account, Payment and the snapshot
   do not exist.
3. Task **1.2's deliverable exists in the repository** (`docs/development/revitalise-grant-automation-form-validation-spec.md`)
   and its Status is **blank**. So the drift runs in both directions.
4. **Phase 1 is contractually due 25 September with 0 of its 13 tasks started**, while Phase 2 — due
   16 October — has 8 tasks `Done`. Phase 0 is due in **ten days** with two tasks `Partially done`.
5. The Service Agreement and the WBS **disagree**: Phase 3 is priced at 100 hours against a WBS range
   of 39–61; Phase 4 is priced at 26 hours against 29–47, and **automation #8 (Finance: Provider,
   Bank Account & Payment — 5 tasks, 13–21 h, ≈€1,560–2,520) is in the WBS but in neither the
   agreement's scope list nor its fee schedule.**

None of these are visible to any agent in the current system, because no agent reads a commercial
document and nothing joins a contract line to a commit.

**The re-design in one sentence:** the **WBS task id becomes the join key of the entire system** —
every plan, architecture, dev summary, test report, build, deploy, log line, work session and invoice
line declares it — and three new agents own the plan of record, the money, and acceptance/handover,
with a generated WBS state file replacing the hand-maintained Status column as the answer to *"where
are we"*.

**One action is urgent and independent of everything else.** The signed Service Agreement is sitting
untracked in the working tree (`git status` shows `??`). It contains the day rate, the total contract
value, an IBAN, a BIC and both parties' tax numbers. This repository lives in a SharePoint library
named after the client. Do not `git add` it. §4.3 has the placement rules.

---

## Part 1 — Ground truth

### 1.1 What the Service Agreement fixes

| Term | Value | Where it lands in the design |
|---|---|---|
| Parties | Argelis Consultancy (Xander Lykopoulos), NL · Revitalise Respite Holidays, charity 02044219 | `contract/service-agreement.yml` |
| Authorised contact | Janine Tregelles, CEO | the only person whose acceptance counts |
| Basis | **Time-and-materials, €120/hour excl. VAT** | answers decision 1; rate is the only figure needing protection |
| Invoicing | **monthly in arrears**, hours worked in the preceding calendar month | invoice cadence is contractual, not a preference |
| Payment terms | 14 days from invoice date | ages an unpaid invoice in status output |
| Currency | EUR; invoice to `accounts@revitalise.org.uk`; no PO required | `contract/service-agreement.yml` |
| Fee schedule | P0 58 h €6,960 · P1 54 h €6,480 · P2 54 h €6,480 · P3 100 h €12,000 · P4 26 h €3,120 · **total 292 h / €35,040** | the per-phase budget, and the per-phase liability cap |
| Milestone dates | Kick-off 4 Jul (complete) · **P0 28 Aug** · P1 25 Sep · P2 16 Oct · P3 27 Nov · **Completion 11 Dec 2026** | the schedule the system must measure against |
| Agreed Specification (B1) | Automation Solution Design + Solution Architecture + **WBS** + **phase acceptance record**; most recently accepted version prevails | makes WBS accuracy contractual; names an artefact that does not exist |
| Warranty (B4) | **60 days from Acceptance of the phase**; final phase until the later of 60 days and two trustee board cycles, max 150 days; **hypercare = 10 business days after each go-live** | the warranty clock, §7 |
| Liability (B11) | per phase: fees paid for that phase; total: total fees paid | per-phase accounting is not optional |
| Excluded (B8) | M365, Power Platform, Dataverse, Power Automate, Power Apps, AI Builder, DocuSign, QuickBooks Online, WordPress + form plugin | a defect in these is not warranty work |
| Excluded (scope) | licence procurement and cost · **the WordPress form build itself** (client's designer; consultant supplies spec + testing only) · day-to-day grant admin · **ongoing operation, monitoring, support or maintenance after handover** | handover is a hard commercial boundary, §7 |
| Runbooks (B10) | Governance Runbook, ALM Runbook | handover deliverables |
| Precedence | Service Agreement → Build Terms v1.0 → General Terms v1.3 | both referenced documents are **absent** from the repo — see decision D-4 |

### 1.2 What the WBS contains

Three sheets. `Summary` (9 automations, hours, task counts, annual hours saved, dependencies),
`WBS Detail` (61 tasks), `Phase Timeline` (5 phases, durations, milestones, go/no-go gates).

`WBS Detail` columns: `Task ID · Automation # · Automation Name · Task · Description · Hours (Low) ·
Hours (High) · Depends On · Phase · Deliverable · Status · Actual Hours · Delta`.

| | |
|---|---|
| Tasks | **61**, ids `0.1`–`0.10`, `1.1`–`8.5` |
| Automations | **9** — #0 Platform Foundation & Governance … #8 Finance |
| Hours | **177–277** (SA schedules 292) |
| Dependency edges | `Depends On` populated on 49 of 61 tasks — a usable DAG |
| Deliverable named | on all 61 — and 7 of them are literally *"Test results / sign-off"* |
| `Status` | 16 `Done` · 2 `Partially done` · 1 `In progress` · **42 blank** |
| `Actual Hours` | **0 of 61 populated** |
| `Delta` | **0 of 61 populated** |

The last two lines are the design's starting point. Somebody built the right instrument and it has
never been used once — which is exactly what happened to `logs/improvement-log.jsonl`'s predecessor
and to the `Actual` half of every estimate this system has produced.

### 1.3 Phase-level reconciliation, computed

| Phase | Due | SA hours | SA fee | WBS lo–hi | Tasks | Done | Part. | Blank | Flag |
|---|---|---|---|---|---|---|---|---|---|
| Phase 0 | **28 Aug** | 58 | €6,960 | 32–52 | 9 | 8 | 1 | 0 | +6 h over detail high (inside 37–61 once 0.10 is counted) |
| Phase 1 | 25 Sep | 54 | €6,480 | 36–54 | 13 | 0 | 0 | **13** | at the high bound, nothing started |
| Phase 2 | 16 Oct | 54 | €6,480 | 36–54 | 13 | 8 | 1 | 4 | at the high bound |
| Phase 3 | 27 Nov | **100** | €12,000 | 39–61 | 15 | 0 | 0 | 15 | **SA is +39 h above the WBS high** |
| Phase 4 | 11 Dec | **26** | €3,120 | 29–47 | 10 | 0 | 0 | 10 | **SA is −3 h below the WBS low; #8 unquoted** |
| 0.10 | spread | — | — | 5–9 | 1 | 0 | 1 | 0 | instrumentation, executed across P1–P4 |

Tasks currently marked `Done` are worth **51–79 quoted hours (€6,120–€9,480)** of the 292 contracted.
Nothing in the repository confirms or refutes that number, because no hours have ever been recorded.

---

## Part 2 — Five defects the documents expose today

Each is stated with its evidence, why nothing caught it, and the requirement that fixes it. This is
the same discipline `logs/improvement-log.jsonl` applies to build failures, applied to the commercial
layer for the first time.

### 2.1 The approved SDD misstates the commercial baseline

`docs/plans/revitalise-grant-automation-plan.md` §10 — an **APPROVED** document — says:

| | SDD §10 | Contract + WBS v0.5 | Error |
|---|---|---|---|
| Total | 106–160 h | **292 h contracted** (WBS 177–277) | understates the low bound by 186 h |
| Automations | 7 (#1–#7) | **9** (#0–#8) | omits #0 Platform Foundation (37–61 h) and #8 Finance (13–21 h) |
| Phase 1 | #1 Form validation, #4 Intake, #2 Scoring | **#3 DocuSign, #1 Form validation** | wrong membership → wrong due date per automation |
| Phase 0 | "excluded from the range; the architect should confirm" | **58 h, €6,960, due 28 Aug** | the carve-out §10 flagged as unresolved is in fact a priced, dated, contracted phase |

**Why nothing caught it.** §10 was intaked from an earlier source document. `skills/how-to-intake-external-documents.md`
asks whether §10 is *present*, never whether it is *true against the contract* — and at the time there
was no contract in the repo to check it against. The SDD then passed its gate and became the number
every downstream document inherited.

**Fix:** PM-R01, PM-R02. §10 stops carrying transcribed hours and cites `contract/wbs.yml`. A script
fails if any repo document restates baseline hours that disagree with the locked baseline.

### 2.2 The `Status` column is a claim nothing verifies — and it is wrong in both directions

**Over-claim.** Task `0.4` — *"Dataverse solution & table schema build … build the seven Dataverse
tables (Applicant, Application, Review, Grant, Provider, Bank Account, Payment) plus the Anonymised
Statistic snapshot"* — Status: **`Done`**.

`src/solutions/RevitaliseGrantAutomation/Entities/` contains four: `rev_applicant`, `rev_application`,
`rev_errorlog`, `rev_setting`. `rev_review`, `rev_grant`, `rev_provider`, `rev_bankaccount`,
`rev_payment` and the snapshot table do not exist. (`rev_provider` exists only as a *column* on
`rev_application`; `rev_payment` and `rev_bankaccount` appear only as forward references in
`Roles/REV Admin/REV Admin.xml` and `Other/FieldSecurityProfiles.xml` — privileges on tables that
aren't there, which also puts `0.5 Done` partly in doubt.)

**Under-claim.** Task `1.2` *"Write form specification"*, deliverable *"Form specification brief"* —
Status: **blank**. `docs/development/revitalise-grant-automation-form-validation-spec.md` exists and is
exactly that deliverable.

**Why nothing caught it.** The Status column is typed by a human into a workbook outside the
repository, and the repository has no idea the column exists. This is `exit-zero-does-not-mean-created`
(x3 in `logs/known-failure-modes.md`) in a spreadsheet: *"marked Done"* is a claim, and this project
has already learned three times that a claim of creation must be verified by querying for the thing.

**Fix:** PM-R05, PM-R06. `Status` becomes **generated** into `logs/state/wbs-state.yml` from repository
and environment evidence, with the hand-typed value retained as `claimed_status` and any disagreement
raised. The workbook stops being the source of truth for progress and becomes a rendering of it.

### 2.3 `Actual Hours` and `Delta` exist and have never been populated

0 of 61 rows. The engagement is T&M: hours are the invoice. Six weeks in, with 16 tasks marked done
and ~€6,120–9,480 of quoted work claimed complete, there is **no record of a single hour worked** —
in the workbook, the repository, or anywhere else this system can see.

**Fix:** PM-R10 to PM-R13 — the worklog ledger from the superseded design, now keyed by WBS task, with
`Actual Hours`/`Delta` written back into the workbook rendering rather than typed.

### 2.4 The build order does not match the contracted order

| | Contractually due | Task state today |
|---|---|---|
| Phase 0 | **28 August — ten days** | 8 Done, `0.7` and `0.10` Partially done |
| Phase 1 | 25 September | **0 of 13 started** — and gated on the Client provisioning DocuSign (SA: "target mid-September") |
| Phase 2 | 16 October | 8 Done, `4.1` In progress, 4 blank — all four are Emily walkthroughs, feedback and sign-off tasks |

Phase 2 is over half built while Phase 1, due three weeks earlier, has not begun. The four remaining
Phase 2 tasks are precisely the client-facing acceptance ones, which is how a phase reaches 60%
"built" and 0% *accepted* — and Acceptance is what starts the warranty and permits the invoice
narrative to say "delivered".

**Why nothing caught it.** No agent knows the contract exists. `lead-agent` routes whatever the
reviewer asks for next; there is no queue, no dependency graph and no date.

**Fix:** PM-R07 to PM-R09 — the ready-set queue over the WBS DAG, and a schedule-risk report that
compares remaining quoted hours per phase against days to its contractual date.

### 2.5 The two contractual documents disagree with each other

Build Terms B1 makes the WBS **and** the Solution Architecture **and** the acceptance record jointly
the Agreed Specification, with *"the most recently accepted version prevails"*. So a disagreement
between them is not a filing error; it is a live ambiguity about what was bought.

| Disagreement | Size | Reading |
|---|---|---|
| Phase 3: SA 100 h vs WBS 39–61 h | **+39 h ≈ €4,680** | the fee schedule was not derived from WBS v0.5. Either it carries contingency the WBS does not show, or it was priced from an earlier breakdown |
| Phase 4: SA 26 h vs WBS 29–47 h | −3 h | SA 26 h equals automation **#7's high bound exactly** — so Phase 4 was priced as #7 alone |
| **#8 Finance not in the SA** | 5 tasks, 13–21 h, **≈€1,560–€2,520** | present in the WBS, absent from SA §02's seven scope bullets and from the fee schedule. On the current documents it is **unquoted work** |
| WBS v0.5 dated 16 Aug, SA v1.3 signed 9 Aug | — | under B1's "most recently accepted" rule, has v0.5 been *accepted*? If yes, it is now part of the Agreed Specification and its content prevails over the earlier breakdown behind the fee schedule |

**This is not the system's call and the design must not let an agent make it.** What the system owes
you is that the disagreement is visible, quantified, and raised before an hour is booked to #8 —
because on today's documents those hours have no fee line to sit on.

**Fix:** PM-R03, PM-R04 (baseline lock + drift report), PM-R14 (change orders), and constraint
`C-COM-002`.

---

## Part 3 — Project management requirements

The requirements asked for, numbered, each with a mechanical verification. A requirement whose
`Verify By` is *"someone remembers to look"* is a comment — `constraints/README.md` item 5.

### Baseline and scope

| # | Requirement | Verify By |
|---|---|---|
| **PM-R01** | The commercial baseline is derived from the contractual sources, never retyped. `contract/wbs.yml` and `contract/service-agreement.yml` are **generated** from the workbook and the agreement and carry the source's `sha256`. | `scripts/import-baseline.py --check` exits non-zero when a source changed without regeneration |
| **PM-R02** | No document in the repository restates baseline hours, fees, phase membership or dates. Documents cite the baseline by path and key. | `scripts/verify-baseline-citations.py` greps for numeric hour/fee patterns in `docs/**` and fails on any that disagrees with the baseline |
| **PM-R03** | The baseline is **locked**: `contract/baseline-lock.yml` records the version and hash of every source it derives from, plus the date each was accepted. A new source version requires `APPROVE BASELINE`. | lock file hash comparison in CI |
| **PM-R04** | Every disagreement between the Service Agreement, the WBS, the Solution Architecture and the SDD is enumerated in a **drift report** with its size in hours and euros. Unresolved drift is reported at every gate, never silently carried. | `scripts/report-baseline-drift.py`; non-empty output is a WARN in every PM gate block |
| **PM-R05** | A WBS task's progress is **generated from evidence**, not asserted. The human-entered value is preserved as `claimed_status` and compared. | `scripts/derive-wbs-state.py` writes `logs/state/wbs-state.yml`; disagreements listed |
| **PM-R06** | A task may not be reported `complete` while any deliverable its own `Deliverable` column names is absent from the repository or the environment. | `scripts/verify-wbs-chain.py` — the 0.4 case is its first fixture |

### Queue and schedule

| # | Requirement | Verify By |
|---|---|---|
| **PM-R07** | Work enters the development flow **by WBS task id**. A request that maps to no task is either matched to one, or raised as a change-order candidate before work starts. | `lead-agent` routing gate; `C-COM-002` |
| **PM-R08** | The system computes the **ready set** — tasks whose `Depends On` are satisfied and which are not complete — and proposes the next unit of work from it, respecting phase order and contractual dates. | `scripts/wbs-ready-set.py`; output is deterministic given the state file |
| **PM-R09** | Schedule risk is quantified per phase: remaining quoted hours vs working days to the contractual date at a declared capacity, with client-side dependencies named as blockers with an owner and an age. | `scripts/schedule-risk.py`; included in every status report |

### Time and money

| # | Requirement | Verify By |
|---|---|---|
| **PM-R10** | No hour is billable without (a) at least one evidence reference that resolves to a real log line, commit or deploy record, or an explicit `human-declared` source, **and** (b) a recorded human confirmation. | `C-COM-001`; `scripts/verify-worklog.py` + known-bad fixtures |
| **PM-R11** | Every work session declares one or more WBS task ids, and its hours allocate across them summing to the session total. | `verify-worklog.py` invariant |
| **PM-R12** | All arithmetic — rounding, per-phase totals, VAT, burn against the fee schedule — is computed by script. No agent adds hours by hand. | `scripts/compute-invoice.py` emits both JSON and the markdown the invoice embeds; the verify script recomputes and compares |
| **PM-R13** | A session appears on at most one issued invoice. Issued invoices are immutable; a correction is a new document referencing the original. | `verify-worklog.py` invariants; `C-COM-003` |
| **PM-R14** | Work outside the locked baseline is billable only under an approved change order in `contract/change-orders/`, which records the WBS tasks added, hours, fee and the date the Client agreed. | `C-COM-002`; `verify-worklog.py` rejects unmapped billable sessions without a change-order reference |
| **PM-R15** | A defect against the Agreed Specification raised inside a phase's warranty window is classified **non-billable warranty work**. The window is computed from the phase acceptance record, never asserted. | `scripts/warranty-clock.py`; classification recorded per session |
| **PM-R16** | Work on this multi-agent system itself (`agents/`, `skills/`, `constraints/`, `scripts/`, `templates/`) is tagged `system` and is non-billable, disclosed at 0.00. | work-type classifier + `verify-worklog.py` |

### Acceptance and warranty

| # | Requirement | Verify By |
|---|---|---|
| **PM-R17** | Each phase produces a **phase acceptance record** — the artefact Build Terms B1 names and the repository does not have — listing every task, its deliverable, the verification level reached, and open items. | `templates/phase-acceptance-template.md`; `scripts/verify-acceptance-pack.py` |
| **PM-R18** | The verification ladder gains **V6 — Client accepted**. No agent may set it: it is recorded only from an explicit `CLIENT ACCEPTED <phase> <date>` input naming the person who accepted. | `verify-acceptance-pack.py` refuses a V6 claim with no dated human input |
| **PM-R19** | An acceptance pack may not be assembled for a phase while any task in it is below the verification level its deliverable requires (V5 for anything with a test-report deliverable, V4 for anything a maker must open). | `verify-acceptance-pack.py` |
| **PM-R20** | The system knows, for any date, which phases are in **hypercare** (10 business days from go-live), in **warranty** (60 days from Acceptance; final phase per B4's extended rule), and out of both. | `scripts/warranty-clock.py --as-of` |

### Handover

| # | Requirement | Verify By |
|---|---|---|
| **PM-R21** | A handover pack is produced per phase and consolidated at Completion, covering: what was built and where, owner per component, licence inventory with renewal dates, monitoring and alerting, escalation path, credential locations, open items with their warranty expiry, and the two runbooks B10 names. | `templates/handover-pack-template.md`; `scripts/verify-handover-pack.py` |
| **PM-R22** | Every credential, certificate and app registration the solution depends on is listed with its **holder** and a transfer action. A dependency held only in an individual's personal keystore is a HARD handover blocker. | `verify-handover-pack.py` cross-checks against `provisioning/` and the capability lines in `logs/known-failure-modes.md` |
| **PM-R23** | The handover pack states what is **not** included after handover, quoting the agreement's exclusions, so the boundary is on the record the Client signs. | template section, checked present |

### Auditability

| # | Requirement | Verify By |
|---|---|---|
| **PM-R24** | Every delivery artefact declares the WBS task ids it serves: SDD sections, TAD components, dev summaries, test cases, build manifests, deploy log lines, work sessions, invoice lines. | `scripts/verify-wbs-chain.py` — fails on an artefact with no task |
| **PM-R25** | The chain is verified in **both** directions. A task claiming completion with no artefact is an *unevidenced claim*; an artefact serving no task is *unquoted work*. Both are reported, neither is inferred away. | same script, two report sections |
| **PM-R26** | Commercial state changes — baseline locks, change orders, acceptances, invoice issues, overrides — are append-only and timestamped, with the human who authorised each. | `logs/commercial-events.jsonl`, append-only; `verify-worklog.py` cross-checks that every issued invoice and acceptance has an event |
| **PM-R27** | Client-facing documents state the verification level they are claiming and never a level above the evidence. | `verify-acceptance-pack.py`, `verify-worklog.py` |

### Reporting

| # | Requirement | Verify By |
|---|---|---|
| **PM-R28** | A status update is answerable from chat at any time, in one screen, from generated state only — no document reading, no inference. | `scripts/collect-project-status.py` exits 0 and the agent's output contains no number absent from its JSON |
| **PM-R29** | Every status figure is traceable: phase, quoted hours, booked hours, level reached, days to contractual date, blockers with owner and age. | snapshot schema |
| **PM-R30** | Reporting never blocks delivery. A failure in any PM script or gate cannot halt, retry or roll back a build or a deploy. | pipeline-agent handoff is fire-and-forget; CI job is non-gating for the deploy path |

---

## Part 4 — Folder structure

### 4.1 What the new documents break

| # | Problem | Evidence |
|---|---|---|
| 1 | **A signed contract with an IBAN is in a folder called `Import`, untracked.** One `git add .` puts the day rate, the €35,040 total, `NL59 BUNQ 2198 0309 34`, the BIC and both VAT numbers into git history in a repository that lives in a SharePoint library named after the client. | `git status` → `?? docs/Import/Revitalise - Service Agreement … (Signed).pdf` |
| 2 | **`docs/Import/` mixes four unrelated classes** with different owners, sensitivities and intake agents: contractual (SA, WBS), requirements (Solution Design, data model), compliance (DPIA, RoPA, Security Model, Governance Framework), data samples (2 xlsx + 2 csv of real application data). | 17 files, one flat folder |
| 3 | **No manifest.** Nothing records which source was intaked, by whom, into which artefact, at which version — so an unread source is indistinguishable from an absent one, which is how the WBS sat outside the repo while §10 quoted it. | absence |
| 4 | **No home for client-facing outputs.** Acceptance records, invoices, change orders, status reports and handover packs have nowhere to live, and the acceptance record is a contractual artefact under B1. | absence |
| 5 | **`logs/` is about to become three things.** Action logs (one line per action), the findings ledger, a generated digest — plus, now, generated state and a money ledger. | `logs/` |

### 4.2 Proposed structure

```
contract/                          ← NEW. The commercial spine.
  README.md                        ← what is here, what is committed, what must never be
  service-agreement.yml            ← GENERATED: parties, basis, rate ref, phases (hours/fee/date),
                                     warranty rules, caps, exclusions, precedence
  wbs.yml                          ← GENERATED: 61 tasks — id, automation, phase, task, deliverable,
                                     low, high, depends_on
  baseline-lock.yml                ← version + sha256 + accepted_on per source document
  rate.local.yml                   ← €120/h, bank details, VAT numbers   [GITIGNORED]
  change-orders/CO-001.md          ← one per approved scope change
  acceptance/PA-phase0.md          ← phase acceptance records (the B1 artefact)
  invoices/INV-2026-08.md          ← monthly invoices, immutable once issued
  handover/                        ← per-phase and final handover packs

docs/Import/                       ← KEPT at this path (see 4.3), gains:
  MANIFEST.yml                     ← file → class → sha256 → intaked_by → target artefact → version

logs/
  state/                           ← NEW: generated state, never hand-edited
    wbs-state.yml                  ← derived task status + claimed_status + disagreements
    warranty.yml                   ← per-phase hypercare / warranty windows
    baseline-drift.md              ← the drift report (PM-R04)
  worklog.jsonl                    ← confirmed work sessions            [GITIGNORED]
  commercial-events.jsonl          ← append-only authorisation record    [GITIGNORED]
  pm.log                           ← one line per PM action
  build.log  pipeline.log  routing.log  improvement-log.jsonl  known-failure-modes.md

docs/reports/                      ← client-facing status reports (written form of the chat block)
```

**`docs/Import/` is deliberately not renamed.** `docs/sources/` with subfolders would be cleaner, and
it costs **57 path references across 10 files** — the SDD (15), the Dev Summary (15), the Test Report
(7), the TAD (6), the form-validation spec (3), four others — all in approved documents, plus two
PowerShell test files that assert against those paths. A rename is a large diff across approved
artefacts for a cosmetic gain, and `MANIFEST.yml` delivers the actual benefit (classification,
provenance, intake ownership) at zero reference cost. Recommend deferring the rename to a quiet moment
and doing it as its own change, or never.

`MANIFEST.yml` classifies each of the 17 files as `contractual | requirements | compliance |
data-sample`, and records for each: `sha256`, `intaked_by` (agent), `target` (the artefact that adopted
it), `source_version`, and `contains_client_pii` / `contains_commercial_terms` flags. The two
application-data exports are real applicant data in a git-tracked folder — flagging that is not this
design's job to fix, but a manifest that does not say so is not a manifest.

### 4.3 Sensitivity: what is committed, what is not, what leaves the repository

| Class | Examples | Placement | Why |
|---|---|---|---|
| **Never in git** | signed SA pdf, `rate.local.yml`, IBAN/BIC/VAT, `worklog.jsonl`, `commercial-events.jsonl`, draft invoices | working tree only, gitignored, or outside the repo | the repo may be client-visible; a rate card and bank details in git history cannot be withdrawn |
| **Committed, no figures** | `wbs.yml`, `service-agreement.yml` (phase hours/fees are figures the Client already agreed and signed), `baseline-lock.yml`, `wbs-state.yml`, drift report | `contract/`, `logs/state/` | the audit trail must survive; the Client has seen every number in it |
| **Committed, client-facing** | issued invoices, acceptance records, change orders, handover packs | `contract/` | these are documents the Client receives; committing them *is* the audit trail |
| **Committed, internal** | worklog **hashes** referenced by an issued invoice | inside the invoice document | proves the ledger behind a figure without publishing the ledger |

The judgement call in row 2 is deliberate: the per-phase fee schedule is in a document the Client
signed, so committing it publishes nothing new. The hourly rate is in the same document — but it is
also the number that would appear in every future quote, so it stays in `rate.local.yml` and the
committed baseline refers to it as `rate_ref: contract/rate.local.yml`. If you would rather keep the
whole fee schedule out too, that is one flag in the generator (decision D-3).

---

## Part 5 — Agents

### 5.1 Three new agents, and why not one

Yesterday's design proposed a single `pm-agent` with modes. The contract argues for three, on the
oldest control principle there is: **the agent that reports progress should not be the agent that
bills for it, and neither should be the agent that declares a phase accepted.** Each of the three also
has a different tier, a different gate, and a different failure cost.

| Agent | Owns | Tier | Gates | Cost of being wrong |
|---|---|---|---|---|
| **`pm-agent`** | the plan of record: baseline intake, WBS state, ready set, schedule risk, status reporting, drift | `standard`; `mechanical` for a status query answered from a fresh snapshot | `APPROVE BASELINE` | a wrong status costs a conversation |
| **`commercial-agent`** | hours, warranty classification, change orders, invoices, burn against the fee schedule | `standard`; `strategic` on the escalations below | `APPROVE TIMESHEET`, `ISSUE INVOICE <id>`, `APPROVE CHANGE ORDER <id>` | a wrong invoice reaches the Client's finance inbox |
| **`acceptance-agent`** | the phase acceptance record, the V6 level, the warranty clock, the handover pack | `standard` | `CLIENT ACCEPTED <phase> <date>`, `APPROVE HANDOVER` | a wrong acceptance date moves a 60-day warranty and a liability cap |

`commercial-agent` escalates to `strategic` when: an issued invoice must be corrected · the Client
disputes a line · warranty-versus-change-order classification is contested · a phase would exceed its
SA fee schedule · reconstructed and declared hours disagree by more than 20% on any session.

**Why not five.** Baseline intake could be its own agent; so could reporting. Both are folded into
`pm-agent` because they read the same state and produce no outward-facing artefact. **Why not one.**
Because `ISSUE INVOICE` and `CLIENT ACCEPTED` are the two irreversible, client-facing acts in this
system, and putting them behind the same agent that also reports "how are we doing" removes the only
independent check on either.

### 5.2 Changes to existing agents

| Agent | Change | Why |
|---|---|---|
| **`lead-agent`** | **Resolve every incoming request to WBS task ids before routing.** A request matching no task routes to `commercial-agent` for a change-order decision, not to `plan-agent`. Four new routing rows (status / hours / acceptance / capability). Log lines gain `wbs:`. | this single edit is what makes the delivery flow contract-driven (§8). It is also the fix for §2.4 |
| **`plan-agent`** | §10 cites `contract/wbs.yml`; never restates hours. Traceability matrix gains a **WBS task** column beside FR ids. Intake checklist gains "does this contradict the locked baseline?" | fixes §2.1 at the source |
| **`architect-agent`** | Every TAD component and every §12 prerequisite declares the WBS tasks it serves. | the chain hop from spec to design (PM-R24) |
| **`development-agent`** | Dev Summary declares `wbs:` ids per component; §10 assumption rows name the task they threaten; the summary proposes **actual hours per task** as evidence for `commercial-agent` to confirm (it knows what it just did — nobody else will remember) | fixes §2.3 at the moment the information exists |
| **`test-agent`** | Test cases map to WBS deliverables. Seven WBS deliverables are literally *"Test results / sign-off"* — the test report **is** that deliverable, and it produces the V5 evidence `acceptance-agent` needs. | makes acceptance assemblable rather than narrative |
| **`build-agent`** | Manifest and log line carry `wbs:` ids. | chain hop |
| **`pipeline-agent`** | DEV-deploy success emits handoffs to `pm-agent` and `commercial-agent` naming the WBS deliverables landed and the level reached. **Fire-and-forget: a PM failure never halts a deploy** (PM-R30). | the trigger from the original request |
| **`improvement-agent`** | Capability mode (carried from the superseded design). Findings gain an optional `wbs` and `commercial_impact` field, so a defect with money attached ranks accordingly. | a warranty-classified defect is a finding with a euro value |
| **`scripts/generate-known-failure-modes.py`** | New `SECTIONS` entry — *"Before you bill an hour, accept a phase, or report status"* — routing the classes `baseline-restated-not-cited`, `work-order-not-driven-by-contract`, `instrument-exists-never-used`, `billable-hour-without-resolving-evidence` and `status-claimed-above-verification-level`. Without it a commercial lesson lands in the digest's *Unrouted* section. | a class with no section reaches no agent at the moment it applies |
| **`WORKFLOW.md`** | Roster rows; the V-ladder gains **V6 Client accepted**; six new gate keywords; a *Commercial loop* diagram beside the Learning loop; `logs/pm.log` in the logging table. | — |
| **`CLAUDE.md`** | Repo layout; a **Commercial Rules** block: work enters by WBS id · hours need evidence and confirmation · the baseline is generated, never retyped · issued invoices and acceptance records are immutable · nothing claims a level above its evidence. | the rules every agent inherits |
| **`skills/how-to-intake-external-documents.md`** | Third checklist — *Commercial Baseline Intake (pm-agent)*. | a commercial source currently has no owning agent (IMP-0028) |
| **`skills/how-to-estimate-effort.md`** | When a contracted baseline exists, the estimate is the baseline's task range; T-shirt sizing applies only to work with no quoted task — which is by definition a change-order candidate. | stops the system inventing a second estimate beside a contractual one |

### 5.3 New skills

| Skill | Contents |
|---|---|
| `skills/how-to-account-for-billable-time.md` | evidence → session → WBS task → work type → warranty classification → rounding; what may never be billed; how off-repo work is declared; how a write-off is disclosed |
| `skills/how-to-report-project-status.md` | the status block; report the level reached, never above; a document's existence is not progress; blockers carry owner and age; quoted and actual are always labelled |
| `skills/how-to-run-a-phase-acceptance.md` | assembling the pack, the V5→V6 boundary, what an acceptance record may and may not assert, how open items are carried with their warranty expiry |
| `skills/how-to-hand-over.md` | the pack's sections, the credential-holder rule, the exclusions quote, per-phase versus final |

---

## Part 6 — Auditability

### 6.1 The chain

One identifier joins the whole engagement. Every arrow below is a machine-checkable link, not a
narrative claim:

```
Service Agreement §03 phase  ──(fee, date, warranty, liability cap)
        │
        ▼
WBS task id  0.4 / 1.2 / 6.3 …  ──(hours low-high, deliverable, depends_on)
        │
        ├──► SDD FR-nnn ──► TAD component ──► dev summary section
        │                                        │
        │                                        ▼
        │                              commit · build manifest · deploy log line   [V2/V3]
        │                                        │
        │                                        ▼
        │                              test report case                            [V5]
        │                                        │
        ▼                                        ▼
work session (hours, evidence)          phase acceptance record   [V4 → V6, client-signed]
        │                                        │
        ▼                                        ▼
monthly invoice line                     warranty window opens (60d) + liability cap fixed
        │                                        │
        └────────────────► logs/commercial-events.jsonl ◄──────────┘
                            (append-only: who authorised what, when)
```

### 6.2 The two orphan classes, and why both must be reported

`scripts/verify-wbs-chain.py` walks the chain in both directions and refuses to infer either gap away:

| Direction | Orphan | Means | Today's instance |
|---|---|---|---|
| task → artefact | a task claims completion, nothing implements it | **unevidenced claim** | `0.4 Done` with five of eight named tables absent (§2.2) |
| artefact → task | an artefact exists, no task covers it | **unquoted work** | `#8 Finance` privileges already in `REV Admin.xml` and `FieldSecurityProfiles.xml` while #8 is unquoted (§2.5) |

The second is the commercially valuable one and it is the one a hand-written check never finds, for the
same reason `IMP-0013`'s hand-written component list omitted `savedquery` and `systemform`: *a
hand-written list encodes what you already suspected. A derived list cannot.* The task list comes from
`contract/wbs.yml`; the artefact list is derived from the repository.

### 6.3 Ledgers and their rules

| File | Written by | Rule |
|---|---|---|
| `logs/worklog.jsonl` | `commercial-agent`, only after `APPROVE TIMESHEET` | append-only; every session carries resolving evidence, WBS ids, `confirmed_by`; `BILLED` lines immutable |
| `logs/commercial-events.jsonl` | all three PM agents | append-only; one line per authorised commercial act — baseline lock, change order, acceptance, invoice issue, override — each naming the human and the keyword used |
| `contract/invoices/`, `contract/acceptance/`, `contract/change-orders/` | `commercial-agent` / `acceptance-agent` | documents, immutable once issued; corrections are new documents referencing the original |
| `logs/state/*` | scripts | **generated**; never hand-edited; `--check` in CI |

### 6.4 Gates that can fail

Every verify script ships with **known-bad fixtures** under `scripts/fixtures/pm/`, one per invariant,
each of which must fail, plus one clean set that must pass — and CI runs the fixture suite.

This is not defensive over-engineering. `gate-cannot-fail` is the most recurrent class in
`logs/known-failure-modes.md` at **x6**, including a HARD compliance gate that was a silent no-op from
the day it was written (`IMP-0007`) and a secret scan that reported PASS over none of the delivered
files (`IMP-0002`). A commercial gate introduced without proof that it can fail would be the seventh
instance, in the one place that produces documents a Client relies on.

---

## Part 7 — Handover

### 7.1 The contract makes handover a commercial boundary, not a courtesy

SA §02: *"Ongoing operation, monitoring, support or maintenance after handover"* is **excluded** unless
separately agreed in writing. B10 names the **Governance Runbook** and the **ALM Runbook** as the
operational runbooks. So the moment the handover pack is accepted, unbilled help stops being an
obligation and becomes either goodwill or a new engagement — and the pack is the document that fixes
where that line falls.

### 7.2 The pack

Per phase, and consolidated at Completion (11 December):

| Section | Content | Source |
|---|---|---|
| What was built | every WBS task in the phase, its deliverable, where it lives, level reached | `wbs-state.yml` |
| Ownership | component → owner (Revitalise / Argelis / Alex / Wanstor / third party) | TAD §12 + manifest |
| Licences | product, seats, cost owner, **renewal date** | SA exclusions list — licences are the Client's cost |
| Monitoring | `rev_errorlog`, `REVOpsFailureAlert`, the monitoring view, AI Builder credit and licence-renewal alerts | WBS `0.9`, already built |
| Escalation | who to call, in what order, for what | Governance Runbook (WBS `0.8`) |
| **Credentials** | every certificate, app registration and service account, **with its holder** | §7.3 |
| Open items | defects, assumptions and drift still open, each with its **warranty expiry date** | assumption register + `warranty.yml` |
| Warranty | per-phase acceptance date, hypercare end, warranty end, and what warranty does not cover (B8's platform list) | `warranty.yml` + SA |
| **Not included** | the agreement's exclusions, quoted | SA §02 |

### 7.3 The credential problem the system already knows about and nobody has connected to the contract

`logs/known-failure-modes.md`, *Capabilities established in earlier sessions*:

> The provisioning certificate is in this Mac's CurrentUser/My keychain (thumbprint
> A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE, app id 077f1f90-3218-4a06-bc90-887464353aa7).

That is recorded as a **capability**, and as a capability it is correct — it stopped the reviewer having
to re-teach it (`IMP-0022`). As a **handover item** it is a single point of failure the Client cannot
operate: a certificate in one consultant's personal keystore, bound to an app registration with write
access to their production Dataverse. On 11 December that either transfers or becomes an outage waiting
for a phone call.

Hence **PM-R22**: a dependency held only in an individual's personal keystore is a HARD handover
blocker, and `verify-handover-pack.py` reads the capability lines out of the digest to find them. The
system's own memory becomes the input to its exit plan.

### 7.4 Warranty and hypercare as a live clock

`scripts/warranty-clock.py --as-of <date>` answers the one question that decides whether an incoming
defect is free: **which window is this phase in?**

| Window | Rule | Effect on an incoming defect |
|---|---|---|
| Hypercare | 10 business days from phase go-live | priority attention, non-billable |
| Warranty | 60 calendar days from **Acceptance** (final phase: later of 60 days and two trustee board cycles, max 150) | non-billable if it is a defect against the Agreed Specification |
| Out of both | — | billable, or a new engagement |
| Third-party platform (B8) | M365 / Power Platform / DocuSign / QBO / WordPress | **never** warranty work, whatever the window |

Getting this wrong costs money in one direction and goodwill in the other, which is why it is computed
from the acceptance record rather than remembered.

---

## Part 8 — Integration with the automatic development system

### 8.1 The loop

Today the flow starts from whatever the reviewer types. With the baseline in place it starts from the
contract, and closes back onto it:

```
contract/wbs.yml + service-agreement.yml   (locked baseline)
        │
        ▼
pm-agent: ready set  ──►  next unit of work = 1..n WBS tasks, phase-ordered, dates respected
        │
        ▼
lead-agent  ──(feature slug + wbs: ids)──►  plan ─► architect ─► development ─► build ─► test
        │                                                                                  │
        │                                                                          [APPROVED]
        │                                                                                  ▼
        │                                                                            pipeline → DEV
        │                                                                                  │
        │      ┌───────────────────────────────────────────────────────────────────────────┤
        │      ▼                                        ▼                                  │
        │  pm-agent: derive wbs-state          commercial-agent: propose sessions           │
        │      │  (evidence, not claims)               │  [APPROVE TIMESHEET]               │
        │      │                                       ▼                                    │
        │      │                                logs/worklog.jsonl                          │
        │      ▼                                       │                                    │
        └── ready set recomputed                       │           phase complete? ─────────┘
                                                       │                   │
                                       month end       │                   ▼
                                            ▼          │       acceptance-agent: pack  [V5 → V6]
                              commercial-agent: invoice │                   │
                                  [ISSUE INVOICE]       │        [CLIENT ACCEPTED <phase> <date>]
                                            │           │                   ▼
                                            ▼           ▼          warranty clock starts
                                    contract/invoices/          acceptance record committed
                                                                          │
                                                             final phase? ▼  [APPROVE HANDOVER]
                                                                    contract/handover/
```

### 8.2 What the ready set actually computes

Deterministic, no model involved:

1. read `contract/wbs.yml` (61 tasks, `depends_on`) and `logs/state/wbs-state.yml` (derived state)
2. `ready = { t : t not complete AND all depends_on complete }`
3. order by phase, then by contractual date, then by number of downstream dependents
4. drop tasks blocked by a **client-side** dependency and list them separately with owner and age —
   e.g. Phase 1's `3.1`–`3.7` cannot finish without DocuSign, which the SA puts on the Client
5. group the top of the queue into one feature slug where tasks share an automation and a deliverable

Run against today's state this produces a specific and uncomfortable answer: finish `0.7` and `0.10`
before 28 August, then **Phase 1 (13 tasks, 36–54 h) due 25 September** — not more Phase 2 work.

### 8.3 What stays automatic, and what cannot

| Step | Automatic? | Why |
|---|---|---|
| baseline intake | no — `APPROVE BASELINE` | a baseline is a contractual fact; hashing the wrong workbook version poisons everything downstream |
| ready set, drift, schedule risk, WBS state | **yes** | pure functions of committed state |
| plan → architect → dev → build → test → deploy | unchanged, existing gates | this design adds `wbs:` ids and changes nothing else |
| session proposal from evidence | **yes** | a proposal is not a claim |
| hours confirmed | no — `APPROVE TIMESHEET` | evidence span is a floor on elapsed time and no bound on billable attention |
| change order | no — `APPROVE CHANGE ORDER` | it is a commercial negotiation |
| invoice issued | no — `ISSUE INVOICE` | outward-facing and irreversible |
| **client acceptance** | **never** | V6 is an act by Janine Tregelles. No agent may infer it from any amount of green |
| handover released | no — `APPROVE HANDOVER` | it moves the support boundary |

The pattern is the one this project already uses: everything derivable is derived, and every act with a
consequence outside the repository has a keyword in front of it.

### 8.4 The two edits that make it contract-driven rather than contract-aware

Everything else in this document is machinery. These two are the change:

1. **`lead-agent` resolves a request to WBS task ids before it routes.** No id, no delivery flow —
   the request goes to `commercial-agent` as a change-order candidate first. This is what stops the
   system building Phase 2 in August because that is what was asked for.
2. **`pipeline-agent`'s DEV-deploy success feeds `pm-agent` and `commercial-agent`.** State is derived
   and hours are proposed at the moment the evidence exists, not reconstructed from memory at month
   end. This project's own lesson: *"The fifteen-attempt DEV import produced one document, written
   afterwards, from memory. Fifteen entries written as they happened would have cost nothing."*

---

## Part 9 — Scripts, constraints, gates

### 9.1 Scripts

All stdlib Python — `openpyxl` and `pandas` are absent and the CI gates run without installs. `.xlsx`
is a zip of XML (`zipfile` + `xml.etree` over `xl/worksheets/*.xml` and `xl/sharedStrings.xml`); the
signed PDF decodes via its fonts' `ToUnicode` CMaps. Both were proven during this session — the numbers
in Part 1 came out of them.

| Script | Job | Mode |
|---|---|---|
| `import-baseline.py` | workbook + agreement → `contract/wbs.yml`, `service-agreement.yml`, `baseline-lock.yml` | `--check` |
| `report-baseline-drift.py` | SA ↔ WBS ↔ TAD ↔ SDD disagreements, in hours and euros | report |
| `derive-wbs-state.py` | repo + environment evidence → `logs/state/wbs-state.yml`, with `claimed_status` compared | `--check` |
| `wbs-ready-set.py` | the DAG → next work, client-blocked tasks listed separately | report |
| `schedule-risk.py` | remaining quoted hours vs working days to each contractual date | report |
| `verify-wbs-chain.py` | both orphan directions (PM-R24, PM-R25) | gate |
| `reconstruct-worklog.py` | evidence → candidate sessions, scratchpad only, **never writes the ledger** | proposal |
| `compute-invoice.py` | all arithmetic: rounding, per-phase totals, VAT, burn vs fee schedule | report |
| `verify-worklog.py` | ledger invariants incl. resolving evidence, no double-bill, WBS mapping, warranty classification | gate |
| `warranty-clock.py` | hypercare / warranty / out, per phase, `--as-of` | report |
| `verify-acceptance-pack.py` | V-level floor per deliverable; V6 only from dated human input | gate |
| `verify-handover-pack.py` | required sections; credential holders; personal-keystore blocker | gate |
| `collect-project-status.py` | the one snapshot the status block is rendered from | report |
| `fixtures/pm/` | one known-bad input per invariant + one clean set; run by CI | proof |

### 9.2 Constraints — three, in a new file

`constraints/commercial/commercial-constraints.md` · IDs `C-COM-nnn` · Owner: Engagement Owner
(Argelis) · Checked by: the three PM agents only. Commercial rules do not belong in
`domain-constraints.md`: that would put a rate card in scope for `plan-agent`, `architect-agent`,
`development-agent` and `test-agent`, none of which should be checking one.

| ID | Constraint | Severity | Verify By |
|---|---|---|---|
| `C-COM-001` | No hour is billable without at least one evidence reference that resolves to a real log line, commit or deploy record — or an explicit `human-declared` source — **and** a recorded `confirmed_by` human confirmation. | HARD | `verify-worklog.py` + fixtures |
| `C-COM-002` | No delivery work proceeds, and no hour is billed, against a WBS task id absent from the locked baseline, unless an approved change order in `contract/change-orders/` covers it. Work tagged `system` is out of contractual scope and non-billable. | HARD | `verify-wbs-chain.py`, `verify-worklog.py` |
| `C-COM-003` | A confirmed session appears on at most one issued invoice; an issued invoice or acceptance record is immutable and is corrected only by a new document referencing it. | HARD | `verify-worklog.py` |

**The fourth candidate is deliberately a script invariant, not a row.** "No client-facing document may
claim a verification level above the evidence" lives in `verify-acceptance-pack.py` and
`verify-worklog.py`. The `improvement-agent` cap is three constraints per review, and anti-bloat limit 4
prefers the most mechanical home available — *a script beats a constraint row beats a paragraph*. This
project's own proof is `C-TECH-049`, which became effective when
`verify-workflow-description-length.py` was written, not when the row was added.

`constraints/README.md` needs three edits: the directory-structure block, the ID-format block, and the
which-agents-check-which matrix.

### 9.3 Gate keywords

| Gate | Proceed | Pause |
|---|---|---|
| Lock a new baseline version | `APPROVE BASELINE` | `HOLD` |
| Confirm hours into the ledger | `APPROVE TIMESHEET` | `HOLD` |
| Accept unquoted scope as chargeable | `APPROVE CHANGE ORDER <id>` | `HOLD` |
| Issue a monthly invoice | `ISSUE INVOICE <id>` | `HOLD` |
| Record client acceptance of a phase | `CLIENT ACCEPTED <phase> <date>` | — |
| Release a handover pack | `APPROVE HANDOVER` | `HOLD` |

Two of these are not approvals but **facts the system cannot derive**: `APPROVE BASELINE` fixes which
document version is contractual, and `CLIENT ACCEPTED` records an act by the Client's authorised
contact. An agent that infers either has invented a contract term.

### 9.4 The verification ladder gains one rung

`agents/WORKFLOW.md`'s ladder stops at V5 — internally executed. The contract needs one more, because
warranty, the liability cap and the support boundary all hang off it:

| Level | Claim | Evidence | Who can set it |
|---|---|---|---|
| V2 | packaged | the packer accepted the layout | build-agent |
| V3 | accepted | components exist and re-deploy cleanly | pipeline-agent |
| V4 | usable | a named person opened and saved each one | pipeline-agent, naming the person |
| V5 | executed | end-to-end with real inputs and observed outputs | test-agent |
| **V6** | **client accepted** | **a dated acceptance record signed by the Client's authorised contact** | **nobody — recorded from `CLIENT ACCEPTED` only** |

---

## Part 10 — Build order

Nothing here can bill, accept or hand over anything until step 6. Each step is useful alone.

| # | Step | Delivers | Why here |
|---|---|---|---|
| 1 | `import-baseline.py` + `contract/` + `APPROVE BASELINE` + `MANIFEST.yml` + the gitignore rules | the locked baseline; the IBAN and rate out of harm's way | everything else reads this, and step 1's gitignore lines are the urgent bit (§0) |
| 2 | `report-baseline-drift.py` + `derive-wbs-state.py` + `verify-wbs-chain.py` + fixtures | the five defects in Part 2 become a standing report instead of a one-off reading | pays for itself immediately: it tells you today whether `0.4 Done` and the #8 gap are still true |
| 3 | `collect-project-status.py` + `wbs-ready-set.py` + `schedule-risk.py` + `pm-agent` STATUS | *"where are we"* from chat, and *"what should I build next"* answered by the contract | read-only, no commercial decisions, no gates. Also the fix for §2.4, ten days before the Phase 0 date |
| 4 | `wbs:` ids threaded through `lead-agent`, plan, architect, dev, test, build, pipeline | the audit chain, and the contract-driven queue (§8.4) | after step 3, because the chain verifier needs the state file to check against |
| 5 | `verify-worklog.py` **and its fixtures**, in CI | the gate exists before the thing it guards | the direct lesson of `gate-cannot-fail` x6 |
| 6 | `reconstruct-worklog.py`, `compute-invoice.py`, `worklog.jsonl`, `commercial-agent`, `C-COM-001…003`, invoice template | billable hours, change orders, monthly invoices | nothing can produce a figure the gate has not been proven able to reject |
| 7 | `warranty-clock.py`, `verify-acceptance-pack.py`, `acceptance-agent`, V6, acceptance template | phase acceptance and the warranty clock | needed before the first phase is accepted — Phase 0 is due 28 August |
| 8 | `verify-handover-pack.py`, handover template, the credential audit | handover | needed before 11 December, and the credential transfer needs lead time |

Steps 1–3 are three days of work at most and would have caught all five defects in Part 2. Step 7 has a
hard date: **Phase 0 is contractually due 28 August**, and accepting it without an acceptance record
starts a 60-day warranty from a date nobody wrote down.

---

## Part 11 — Decisions needed

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **D-1** | **Phase 3: SA 100 h vs WBS 39–61 h (+39 h ≈ €4,680)** | the SA carries deliberate contingency · the SA was priced from an earlier breakdown · the WBS understates #5/#6 | You must answer this; the system will not guess. Whichever it is, record it in `baseline-lock.yml` as `phase_3_variance_reason` so no later reader re-derives the question |
| **D-2** | **#8 Finance: 5 tasks, 13–21 h, ≈€1,560–2,520, in the WBS, not in the agreement** | change order · absorb inside Phase 4's 26 h · descope #8 | Change order, before any hour is booked to `8.x`. Two of #8's tables are already forward-referenced in shipped role XML, so the work has partly started |
| **D-3** | Does the committed baseline carry the **per-phase fee schedule**, or only hours? | fees + hours (recommended) · hours only, fees in `rate.local.yml` | Fees + hours. The Client signed those figures, so committing them publishes nothing. The **hourly rate** stays in `rate.local.yml` either way |
| **D-4** | **Build Terms v1.0 and General Terms v1.3 are incorporated by reference and absent from the repo.** B1, B4, B8, B9, B10 and B11 are quoted in the SA, but the underlying clauses are not available to check. | add both to `docs/Import/` (recommended) · rely on the SA's summaries | Add them. The warranty rule, the exclusions list and the liability cap are all things the system will compute against |
| **D-5** | **Has WBS v0.5 been *accepted*** by the Client, or is it an internal working revision? | accepted → it is part of the Agreed Specification under B1 · internal → the fee schedule's breakdown prevails | This determines whether D-1 and D-2 are ambiguities or simply unquoted work. It is the single most consequential fact in this document |
| **D-6** | Capacity assumption for schedule risk | hours/week you can commit | Needed by `schedule-risk.py`. Phase 1 is 36–54 h with 38 days to its date |
| **D-7** | Hours worked before 2026-08-18, and anything already invoiced | seed as `human-declared` / `BILLED` | Without this the first invoice re-proposes hours you have already charged, and the €6,120–9,480 of `Done` work has no actuals at all |
| **D-8** | Are the two application-data exports in `docs/Import/` real applicant data? | yes → they are special-category health data in a git-tracked folder · synthetic | Flagged, not fixed, by this design. If real, it is a DPIA matter and outranks everything above |

D-5 blocks D-1 and D-2. D-6 and D-7 block the first invoice. D-3 and D-4 are wanted at step 1.

---

## Part 12 — What this design does not do

- It does not resolve the contract-versus-WBS disagreements. It quantifies them and puts them in front
  of you (D-1, D-2, D-5).
- It does not decide whether unquoted work is chargeable. It refuses to bill it silently.
- It does not declare anything accepted. V6 comes from Janine Tregelles via `CLIENT ACCEPTED`, and no
  quantity of passing tests substitutes.
- It does not raise invoices or send anything. It writes markdown into `contract/invoices/`.
- It does not know hours you did not record. Off-repo work — Emily's walkthroughs, chasing Wanstor,
  maker-portal clicks — enters as `human-declared` and is disclosed as such.
- It does not fix the data-protection question in D-8, or the fact that `0.4` is marked `Done`. It makes
  both impossible to keep not noticing.
- It does not rename `docs/Import/`. That costs 57 references across 10 approved documents for a
  cosmetic gain.

---

## Gate

```
SYSTEM CAPABILITY DESIGN — docs/improvements/2026-08-18-project-management-system-redesign.md
Supersedes docs/improvements/2026-08-17-project-management-agent-design.md

Baseline read:   WBS v0.5 — 61 tasks, 9 automations, 177–277 h, 0 rows with actual hours
                 SA v1.3 (signed 9 Aug) — T&M €120/h, 292 h, €35,040, 5 phases, 60-day warranty
Requirements:    30 (PM-R01…R30), each with a mechanical verification
New agents:      3 — pm-agent, commercial-agent, acceptance-agent
Changed:         8 agents + WORKFLOW.md + CLAUDE.md + 2 skills
New files:       contract/ (7), logs/state/ (3), 14 scripts, 4 skills, 4 templates, fixtures
Constraints:     3 (C-COM-001…003, cap respected; the 4th candidate is a script invariant)
New gates:       APPROVE BASELINE · APPROVE TIMESHEET · APPROVE CHANGE ORDER · ISSUE INVOICE ·
                 CLIENT ACCEPTED <phase> <date> · APPROVE HANDOVER
Ladder:          V6 Client accepted added
Defects found:   5, all quantified — SDD §10 wrong by 186 h · 0.4 Done vs 4 of 8 tables ·
                 0 of 61 actual-hour rows · Phase 1 0/13 tasks due 25 Sep · #8 unquoted €1,560–2,520
Decisions:       8 open — D-5 (is WBS v0.5 accepted?) blocks D-1 and D-2
Urgent:          the signed SA is untracked in the working tree and contains an IBAN and the day rate.
                 Do not git add it. Step 1 of Part 10 fixes this in one commit.

Respond APPROVE IMPROVEMENTS to implement in the Part 10 order,
or APPROVE IMPROVEMENTS steps 1-3 to take the baseline, the drift report and status first.
```
