# Commercial Constraints

**Owner:** Engagement Owner (Argelis Consultancy)
**Checked by:** pm-agent, commercial-agent, acceptance-agent

These encode the rules of the **engagement** rather than the domain or the platform. They are in
their own file deliberately: putting a rate card and an invoice rule into
`constraints/domain/domain-constraints.md` would drag them into scope for plan-agent,
architect-agent, development-agent and test-agent, none of which should be checking one.

Source documents: `docs/Import/Revitalise - Service Agreement … v1.3 (Signed).pdf`,
`docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx`, `docs/Import/baseline-lock.yml`,
`docs/Import/incorporated-terms.md`.

---

## How to Read This File

| Column | Meaning |
|---|---|
| ID | Stable identifier — never changes |
| Constraint | What the rule requires or prohibits |
| Severity | `HARD` = gate blocker · `SOFT` = warning, human decides |
| Scope | Which agents must actively check it |
| Rationale | The finding or contract clause behind it |
| Verify By | The mechanically executable check |

---

## Section 1: Hours and invoicing

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-COM-001 | No hour is billable without (a) at least one evidence reference that resolves to a real log line, commit or file — or an explicit `source: human-declared` — **and** (b) a recorded `confirmed_by` human confirmation | HARD | commercial-agent | An agent that can originate a billable hour can originate an invoice. Evidence span is a lower bound on elapsed time and no bound at all on billable attention. `IMP-0032`: 61 empty `Actual Hours` rows six weeks into a T&M engagement | `scripts/verify-worklog.py` invariants 4–5 + `src/tests/fixtures/known-bad/worklog/` |
| C-COM-002 | No delivery work proceeds, and no hour is billed, against a WBS task id absent from the locked baseline, unless an approved change order in `contract/change-orders/` covers it. Work tagged `system` is out of contractual scope and never billable | HARD | pm-agent, commercial-agent | WBS v0.5 is the customer-accepted Agreed Specification (D-5, Build Terms B1). Work outside it is either a change order or unbilled. `IMP-0031`: build order was set by conversation, not by the contract | `scripts/verify-wbs-chain.py`, `scripts/verify-worklog.py` |
| C-COM-003 | A confirmed session appears on at most one issued invoice. An issued invoice or acceptance record is immutable and is corrected only by a new document referencing it | HARD | commercial-agent, acceptance-agent | `logs/pipeline.log` records five DEV deploys, four for one feature in five hours. A per-deploy accounting trigger without this bills that afternoon four times. D-7: 64 hours are already invoiced with the split unrecorded | `scripts/verify-worklog.py` invariants 6, 9 |
| C-COM-004 | No fee figure, hourly rate, bank detail or currency amount appears in any tracked file in this repository | HARD | pm-agent, commercial-agent, acceptance-agent | D-3, the reviewer's decision: *"Hours for the baseline is perfect."* The repository lives in a SharePoint library named after the client; a rate in git history cannot be withdrawn | `scripts/verify-worklog.py` invariant 10; `scripts/report-baseline-drift.py` §4 scans `docs/ contract/ agents/ skills/ constraints/ templates/ config/` |

## Section 2: Claims about completion

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-COM-005 | A task's completion is **derived from evidence**. The WBS `Status` column is recorded as a claim and compared, never treated as fact, and a task may not be reported complete while any deliverable its own row names is absent | HARD | pm-agent | `IMP-0030`: task 0.4 was marked `Done` with five of the eight tables it names absent, while 1.2's deliverable existed against a blank status. Same class as `exit-zero-does-not-mean-created` (x4) | `scripts/derive-wbs-state.py`, `scripts/verify-wbs-chain.py` + `src/tests/fixtures/known-bad/wbs-chain/` |
| C-COM-006 | No client-facing document claims a verification level above the level actually reached, and **V6 (client accepted) is recorded only from an explicit dated `CLIENT ACCEPTED` input naming the person who accepted** | HARD | acceptance-agent, commercial-agent | `C-TECH-053` applied to a contract. `IMP-0012`: three components imported cleanly, were queryable, and no maker could open them. Warranty, the liability cap and the support boundary all hang off the acceptance date | `scripts/verify-acceptance-pack.py` |
| C-COM-007 | No variance against an estimate is computed or reported for a phase that is still open | HARD | pm-agent, commercial-agent | `IMP-0065`: 64 invoiced hours against a 68–106 estimate was read as efficient delivery. The work was simply unfinished, and the wrong inference was written into the committed baseline | `scripts/compute-invoice.py` (emits `why_no_variance`), `scripts/verify-acceptance-pack.py` |

## Section 3: The baseline itself

| ID | Constraint | Severity | Scope | Rationale | Verify By |
|---|---|---|---|---|---|
| C-COM-008 | The commercial baseline is generated from the contractual sources and hash-pinned. No document restates contracted hours, fees, phase membership or dates — documents cite the generated baseline | HARD | pm-agent | `IMP-0029`: the APPROVED SDD §10 stated 106–160 hours over 7 automations against a signed 292 over 9, with the phase membership wrong, and everything downstream inherited it | `scripts/import-baseline.py --check`, `scripts/report-baseline-drift.py` §3 |
| C-COM-009 | A source document in `docs/Import/` is never edited. A correction to an accepted specification is a new version, re-approved behind `APPROVE BASELINE` | HARD | pm-agent | WBS v0.5 is customer-accepted under B1 (D-5). Editing it in place would silently change what was agreed. `IMP-0064` | `contract/source-lock.json` hashes; `scripts/import-baseline.py --check` |
| C-COM-010 | An accepted violation of a commercial gate carries an owner, a reason, a clearing action and a dated expiry, and is re-reported on every run. An unowned, undated or expired exception fails its gate | HARD | pm-agent | A gate switched off because reality violates it is `gate-cannot-fail` (x6) arriving by the front door. `EX-001` and `EX-002` are live today | `scripts/verify-wbs-chain.py` exception validation + `src/tests/fixtures/known-bad/wbs-chain/exception-expired.json`, `exception-unowned.json` |

---

## Retired Constraints

| ID | Constraint (summary) | Retired | Reason |
|---|---|---|---|
| — | — | — | — |

---

## Constraint Violation Response

HARD: stop, list the violated IDs under `CONSTRAINT CHECK`, emit `BLOCKED`, do not proceed until the
check re-runs clean or an exception is recorded per `C-COM-010`.

SOFT: document it in the gate output as a warning with a proposed mitigation, and proceed — the
reviewer makes the call.

**One exception to "stop":** a commercial gate never halts, retries or rolls back a build or a deploy
(PM-R30). Delivery continues; the commercial finding is reported.
