# Domain Constraints

**Owner:** Domain Owner / Compliance Lead
**Checked by:** plan-agent, architect-agent, development-agent, test-agent

These constraints encode the non-negotiable and advisory rules of the business domain.
They are derived from regulations, legal obligations, internal policy, and contractual commitments.

> 📝 **To customise:** Replace the placeholder examples below with constraints specific to your domain.
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
| C-DOM-004 | Personal data must not be written to application logs | HARD | development-agent, test-agent | GDPR Art. 5(1)(f) | Code review checklist item confirmed; log-output test passes |
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

## Section 4: [DOMAIN PLACEHOLDER — e.g. Regulatory / Industry-Specific]

> Replace this section with constraints specific to your regulated domain.
> Examples: financial crime controls, clinical data rules, payment card constraints, employment law requirements.

| ID | Constraint | Severity | Scope | Source | Verify By |
|---|---|---|---|---|---|
| C-DOM-030 | [PLACEHOLDER] Replace with your first domain-specific constraint | HARD | architect-agent | [Regulation / policy] | [Verification method] |
| C-DOM-031 | [PLACEHOLDER] Replace with your second domain-specific constraint | SOFT | development-agent | [Regulation / policy] | [Verification method] |

---

## Retired Constraints

| ID | Constraint (summary) | Retired | Reason |
|---|---|---|---|
| — | — | — | — |

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
