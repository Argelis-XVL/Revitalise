# Domain Constraints

**Owner:** Domain Owner / Compliance Lead
**Checked by:** plan-agent, architect-agent, development-agent, test-agent

These constraints encode the non-negotiable and advisory rules of the business domain.
They are derived from regulations, legal obligations, internal policy, and contractual commitments.

> **Sections 1–3 are the universal privacy, audit and access-control rules** inherited from the
> system scaffolding. They are real and in force, but note that most are verified by a document
> section rather than by a script — see the coverage note under *Retired Constraints*.
> **Section 4 is this project's own domain**, written 2026-08-19 and backed by an executable gate.
> Add rows freely. Never renumber or remove rows — mark retired constraints with `status: retired`.

---

## How to Read This File

| Column | Meaning |
|---|---|
| ID | Stable identifier — never changes |
| Constraint | What the rule requires |
| Severity | `HARD` = gate blocker if violated · `SOFT` = warning, human decides |
| Scope | Which agents must actively check this constraint |
| Source | Regulation, policy document, or decision that mandates this rule |
| Verify By | How an agent or reviewer confirms compliance |

---

## Section 1: Data & Privacy Constraints

| ID | Constraint | Severity | Scope | Source | Verify By |
|---|---|---|---|---|---|
| C-DOM-001 | Personal data must be classified before any entity is designed or implemented | HARD | plan-agent, architect-agent | GDPR Art. 30 | TAD §3 data classification column is fully populated |
| C-DOM-002 | A lawful basis for processing personal data must be documented for every data entity that holds PII | HARD | plan-agent, architect-agent | GDPR Art. 6 | SDD §7 lists lawful basis per entity |
| C-DOM-003 | Retention period must be defined for every data entity; automated deletion or archival must be implemented | HARD | architect-agent, development-agent | Internal data policy | TAD §3 includes retention period; Dev Summary §3 confirms implementation |
| C-DOM-004 | Personal data must not be written to application logs | HARD | development-agent, test-agent | GDPR Art. 5(1)(f) | `rev_errorlog` holds no column from the special-category register — asserted by the `domain-invariants` build step, which fails if a registered column appears on an entity other than the one the register declares; plus the log-output test |
| C-DOM-005 | A subject access request (SAR) path must exist for every system that holds PII | SOFT | architect-agent | GDPR Art. 15 | TAD §4 includes SAR integration or documents explicit exemption |
| C-DOM-006 | A right-to-erasure path must exist unless retention is legally mandated | SOFT | architect-agent | GDPR Art. 17 | TAD §4 documents erasure mechanism or legal retention exception |

---

## Section 2: Audit & Traceability Constraints

| ID | Constraint | Severity | Scope | Source | Verify By |
|---|---|---|---|---|---|
| C-DOM-010 | All create, update, and delete operations on sensitive entities must be audit-logged | HARD | architect-agent, development-agent, test-agent | Internal audit policy | TAD §6 specifies audit log design; integration test confirms log entries |
| C-DOM-011 | Audit log records must include: timestamp (UTC), actor, action, affected entity ID, before/after values | HARD | development-agent, test-agent | Internal audit policy | Dev Summary §6 maps each log entry to this schema; test validates format |
| C-DOM-012 | Audit logs must be append-only and not deletable by application-level users | HARD | architect-agent | Internal audit policy | TAD §6 documents the append-only mechanism |
| C-DOM-013 | Audit log retention must meet the longer of the regulatory requirement or internal policy | SOFT | architect-agent | Domain-specific regulation | TAD §3 retention period ≥ policy minimum |

---

## Section 3: Access Control Constraints

| ID | Constraint | Severity | Scope | Source | Verify By |
|---|---|---|---|---|---|
| C-DOM-020 | Principle of least privilege must be applied: each role may only access data and functions it requires | HARD | architect-agent, development-agent | Internal security policy | TAD §6 role/permission matrix is complete; security test confirms no privilege escalation |
| C-DOM-021 | Privileged actions (bulk delete, export, admin config) must require elevated authorisation | HARD | architect-agent, development-agent | Internal security policy | TAD §6 documents elevated auth mechanism; security test validates |
| C-DOM-022 | Role assignments must be documented and reviewable | SOFT | architect-agent | Internal audit policy | TAD §6 includes role definition table |

---

## Section 4: Charitable Respite Grant Administration — Special-Category Data

**Written 2026-08-19** (`docs/improvements/2026-08-19-improvement-review.md`), replacing the
scaffolding's two `[PLACEHOLDER]` rows.

Until this date `C-DOM-030` read *"[PLACEHOLDER] Replace with your first domain-specific
constraint"*, was **HARD**, was in `architect-agent`'s scope, and its `Verify By` was
*"[Verification method]"*. A HARD constraint whose rule text is a placeholder can never be
violated, so it always passed — through every gate of every feature this project has shipped
(`IMP-0035`, `blocker`). `skills/how-to-apply-constraints.md` had no outcome between PASS and
VIOLATION for a rule that cannot be assessed; it now has `UNEVALUABLE`, and a HARD
`UNEVALUABLE` row blocks the gate.

The asymmetry that produced this was structural rather than careless. 32 of the 47 findings in
`logs/improvement-log.jsonl` come from `build-agent` and `pipeline-agent`, so the learning loop
only ever fed the technology constraints — which grew to 40 rows and nine executable gates
while this file stayed at the vendor template. The domain knowledge itself was populated on
2026-08-18 (`IMP-0034`); the domain *constraints* were not.

**These three rows are derived, not invented.** Each restates a rule already approved elsewhere
in this repository — SDD FR-016, SDD §7.1, TAD §3.1/§3.3, NFR-014 — and promotes it from prose
into something a script decides. The column list lives once, in
`constraints/domain/special-category-register.yml`, and is read at check time by both the gate
and the FR-016 build step, so the two cannot drift (the discipline `C-TECH-060` established for
length limits, applied to a column list).

| ID | Constraint | Severity | Scope | Source | Verify By |
|---|---|---|---|---|---|
| C-DOM-030 | No special-category or safeguarding column may influence an automated eligibility or scoring outcome. Every such column is listed in `constraints/domain/special-category-register.yml`, which is the **single** source of that list — the scoring flow's bar and the register are the same list, asserted equal on every build | HARD | architect-agent, development-agent, build-agent, test-agent | SDD FR-016; UK GDPR Art. 9 / Art. 22; Data (Use and Access) Act 2025 position recorded in the SDD; DPIA | `domain-invariants` build step — `python3 scripts/verify-domain-invariants.py src/solutions/<Name> --register constraints/domain/special-category-register.yml --build-config config/<slug>-build.yml` exits 0, **and** the `no-special-category-data-in-scoring` build step exits 0. Negative tests: `src/tests/build/BuildGates.Tests.ps1` |
| C-DOM-031 | Every column in the special-category register carries `<IsSecured>1</IsSecured>`, unless the register records an explicit `secured: exception` with a written reason and a named owner. Exceptions are reported on every build — a documented exception stays visible, it does not become invisible | HARD | architect-agent, development-agent, test-agent | SDD §7.1 data classification; TAD §3.1/§3.3; UK GDPR Art. 5(1)(f), Art. 32 | `domain-invariants` build step exits 0. Four exceptions exist today, all four printed by the gate on every run and all four marked ⚠️ unconfirmed in the register |
| C-DOM-032 | Every column in the special-category register carries `<IsAuditEnabled>1</IsAuditEnabled>`. There is no exception route: special-category data with no audit trail cannot answer *who saw this, and when* | HARD | architect-agent, development-agent, test-agent | NFR-014; internal audit policy; UK GDPR Art. 5(2) accountability — this is what `C-DOM-010` and `C-DOM-011` assert in prose, made decidable | `domain-invariants` build step exits 0. The gate additionally **reports** every other attribute in the solution with auditing off (two today: `rev_applicant.rev_fullname`, `rev_application.rev_costs`) so an exclusion is a visible decision rather than a silence. **THIS IS A SOURCE CHECK AND SAYS NOTHING ABOUT THE LIVE ENVIRONMENT.** Dataverse auditing needs `organizations.isauditenabled` AND the table's own `IsAuditEnabled`, and neither is settable from solution source — entity-level `IsAuditEnabled` is absent from every `Entity.xml`. A column flag under two switches that are off records nothing. The live half is `C-TECH-064`, and this row may not be cited as evidence for `C-DOM-010` or `C-DOM-011` without it |

> **What these three do not cover.** Payment controls, the human-review route for an automated
> adverse outcome (Art. 22), retention enforcement, and the referee/emergency-contact
> collection question flagged as ⚠️ in `knowledge/domain/business-rules.md` BR-A06 are all
> real domain obligations with no constraint row and no gate. They are not listed here as
> unverifiable prose, because `constraints/README.md` rule 5 forbids that; they are recorded
> as the next domain-constraint work in the 2026-08-19 improvement review, and the
> three-per-review cap is what defers them, not an assessment that they matter less.

---

## Retired Constraints

| ID | Constraint (summary) | Retired | Reason |
|---|---|---|---|
| — | — | — | — |

**Coverage note, 2026-08-19.** Nothing in this file has been retired, but the reason is worth
recording rather than leaving as a clean-looking empty table. Of the 13 rows in Sections 1–3,
**none** has a mechanically executable `Verify By`: every one resolves to "TAD §n documents…",
"Dev Summary §n confirms…" or "code review checklist". They are not wrong and they are not
retired — the obligations are real — but under
`agents/improvement-agent.md` anti-bloat limit 4 they are, today, closer to comments than to
constraints. The three Section 4 rows are the first in this file with a script behind them.
Converting Sections 1–3 to mechanical verification is the standing candidate carried into the
next review, and it is a larger job than a retirement: several of them (audit-log schema,
retention enforcement, least privilege) need a live environment to assert against, not a
static gate.

---

## Constraint Violation Response

When a HARD domain constraint is violated, the agent must:

1. Stop production of the current document or code
2. List the violated constraint IDs in the gate output under `CONSTRAINT CHECK`
3. Emit `BLOCKED` status
4. Do not proceed until the violation is resolved and the constraint check re-runs clean

When a SOFT domain constraint is violated, the agent must:

1. Document the violation in the gate output under `CONSTRAINT CHECK` as a warning
2. Include a brief explanation of why the constraint could not be met, or a proposed mitigation
3. Proceed to gate — the human reviewer makes the final call
