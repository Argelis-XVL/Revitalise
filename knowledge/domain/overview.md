# Domain Overview — Charitable Respite Grant Administration

**Populated 2026-08-18** by improvement-agent from `logs/improvement-log.jsonl` → `IMP-0034`,
which recorded that this file and five others were still unedited scaffolding templates while the
real domain knowledge sat in documents no agent was instructed to read.

**Sources, in precedence order.** Where they disagree, the higher one wins and the disagreement
is named rather than silently resolved:

1. `docs/plans/revitalise-grant-automation-plan.md` — **APPROVED** SDD
2. `docs/architecture/revitalise-grant-automation-architecture.md` — **APPROVED** TAD
3. `docs/Import/Revitalise-DPIA-v0.1.docx`, `Revitalise-RoPA-v0.1.docx`,
   `Revitalise-Data-Governance-Framework-v0.2.docx` — the controller's own governance record
4. `docs/Import/grant-application-data-model-v0.2.md`,
   `Revitalise-Automation-Solution-Design-v0.5.docx`, `Revitalise-Solution-Architecture-v0.4.docx`

**This file carries no hours, fees, phase membership or dates.** Those live only in the
contractual baseline (`docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx` and the signed
Service Agreement) and are cited, never restated — `IMP-0029` recorded a `blocker` in which an
approved document restated them wrongly and every downstream document inherited it.

---

## What This Platform Covers

Revitalise is a UK charity that awards grants so disabled people and their carers can take a
respite holiday. The platform administers the grant lifecycle end to end: a public application
form, automated eligibility scoring, a monthly trustee panel decision, an electronically signed
acceptance, payment to the holiday provider, and the impact report afterwards. It replaces a
process run on spreadsheets, email and manual anonymisation by one process owner.

| Domain / Module | Core Activity |
|---|---|
| Intake | Public form submission lands as an Application, matched to an Applicant, referenced and acknowledged |
| Scoring | Circumstance score computed from the wellbeing answers; knockout threshold and income ceiling applied; outcome flagged auto-pass / borderline / auto-reject |
| Anonymisation | Identity columns hidden by column security; free-text narrative AI-redacted before trustees see it |
| Panel review | Two trustees per Application per monthly round record a verdict; both approvals are needed |
| Acceptance | Acceptance document issued for two signatures in sequence; signed PDF filed against the Grant |
| Finance | Provider, bank account and payment records; duplicate-payment check before issue |
| Governance | Automated retention by status and trigger date; erasure with legal-hold carve-out; anonymised statistics retained for reporting |

---

## Key Actors

From `Revitalise-Data-Governance-Framework-v0.2.docx` §2 and `Revitalise-RoPA-v0.1.docx` §2.

| Role | Who | Responsibility |
|---|---|---|
| Data controller | Revitalise | Owns the lawful bases, retention periods and the Privacy Notice |
| Data Protection Officer | Revitalise's DPO (named as Rebecca Young in the data model; **confirm currency before relying on it**) | Signs off retention of special-category data, the column-security approach replacing manual separation, and the automated-decision position |
| Process owner | Emily (Revitalise) | Day-to-day owner of the grant process. Sets the scoring threshold, reviews every borderline case, reviews flagged anonymisation, handles erasure requests, can override any automated outcome |
| Trustees | Revitalise board, incl. Kevin | Make the funding decision on eligible applications. Two per Application per round. Never see identity |
| Finance | A 0.5 finance role | Records providers, bank accounts and payments. Sole holder of bank data — the administrator role has none |
| Applicant | Disabled person or their carer | Submits the application; signs the acceptance; may act through a helper |
| Referee / GP | Third party | Provides the second acceptance signature |
| Website designer | Alex (external) | Owns the WordPress form and its webhook |
| Solution builder / processor | Xander Lykopoulos — Argelis | Configures retention, backup and DLP to match the controller's policy |
| Service identity | `svc-grantautomation` | Runs the flows and owns the connections. Not a personal login |
| IT provider | Wanstor | Tenant administration, Conditional Access, joiner/leaver process |

**Open:** a second processor (Jan) is under consideration and not yet assigned
(`Data-Governance-Framework-v0.2` §2).

---

## Core Entities

Detail in `knowledge/domain/data-entities.md`. In one line each:

| Entity | Description |
|---|---|
| Applicant | The person, stored once across every application they make. Holds the pseudonymised ID trustees see instead of a name |
| Application | One form submission and the spine of the process. Carries the circumstance score |
| Review | One Application in front of one monthly panel; two trustee verdicts |
| Grant | Created when an Application succeeds. Holds the award, the acceptance agreement and the impact report |
| Provider | A holiday provider such as Havens. Contact only — no finance data |
| Bank Account | Every account the charity pays into, held once. Finance role only |
| Payment | A disbursement against a Grant. Finance role only |
| Anonymised Statistic | Non-personal outcome snapshot, deliberately unlinked, retained indefinitely |
| Error Log | Operational only. No personal data, ever |

---

## Regulatory Context

- **UK GDPR / Data Protection Act 2018** — the whole platform processes personal data, including
  Article 9 special-category health and disability data.
- **Data (Use and Access) Act 2025 (DUAA)** — governs the automated-decision position on
  threshold-based auto-rejection. **The DPO has not yet confirmed it.**
- **Charities Act 2011** — the six-year financial-record duty, which is why a successful grant's
  record is kept for six years and why erasure carries a legal-hold carve-out.
- **Equality Act 2010** — the applicant population is disabled by definition; accessibility of
  the applicant-facing form and the trustee app is a requirement, not a preference.

Detail in `knowledge/domain/regulations.md`.

---

## The Non-Negotiables

Full list with verification in `knowledge/domain/compliance-requirements.md`. The four that block
any release:

1. **Special-category data never reaches a trustee.** Column security hides identity; the
   narrative is redacted before trustee review.
2. **Special-category data never influences the automated score.** Disability, health-condition
   data and the free-text narrative do not feed the circumstance score (SDD FR-016, DUAA
   position). Enforced mechanically by the `no-special-category-data-in-scoring` build gate.
3. **Bank and payment data sit behind the finance role alone** — the administrator role has no
   access at all (SDD NFR-002, separation of duties).
4. **No personal data in any operational log** (SDD NFR-012).
