# Glossary — Charitable Respite Grant Administration

**Populated 2026-08-18** (`IMP-0034`). Sources as listed in `knowledge/domain/overview.md`.

---

## Domain Terms

| Term | Definition |
|---|---|
| **Acceptance agreement** | The document an applicant signs to accept a grant. Two signatures in sequence: the applicant, then the referee or GP. Replaces a Canva form posted out by hand. Field group on **Grant** |
| **Anonymised statistic** | A non-personal outcome snapshot (age range, location area, condition areas, outcome, amount) written at outcome and deliberately **not** linked to its source record, so it survives the retention purge |
| **Auto-pass / Borderline / Auto-reject** | The three outcomes the scoring flow sets. *Borderline* means within 5 points of the knockout threshold and is always reviewed by the process owner |
| **Break** | The respite holiday itself — its type, location, dates, accommodation, travel and other costs |
| **Circumstance score** | The applicant's need score, **0 to 60**, calculated from the eleven wellbeing answers. Higher means greater need |
| **Confirmation screen** | The pre-submission summary of the application, with edit-per-section |
| **Exceptional funding** | A request for an award outside the standard basis, with its own free-text justification |
| **Group reference** | Links applications made together as a group. Field group on **Application** |
| **Helper** | Someone completing the application on the applicant's behalf. Name, email, phone, organisation, relationship. Field group on **Application** |
| **Impact report** | The applicant's report after the break. Due one month after the holiday end date. Field group on **Grant** |
| **Income ceiling** | The means-test income limit, above which an application is rejected regardless of score. Held in **Settings**, adjustable by the process owner |
| **Knockout threshold** | The minimum circumstance score. Held in **Settings**, adjustable by the process owner. **The board has not yet set its value** |
| **Panel / board round** | The monthly trustee meeting at which applications are decided. An application may be reviewed across up to three attempts; the third rejection closes it |
| **Payee** | The single Bank Account a Payment is made to — either a provider's account or an applicant reimbursement |
| **Pseudonymised ID** | The applicant reference (`REV-A-00001` format) that trustees see **instead of** a name. It is the primary name column on **Applicant**, by design (TAD ADR-013) |
| **Redaction / scrubbing** | AI Builder PII detection over the free-text narrative, replacing detected entities with category labels before trustee review. Below 85% confidence the case is flagged for manual review |
| **Referee** | The third party providing the second acceptance signature. Collected on a **separate form after board approval**, not at intake |
| **Reimbursement account** | An applicant's own bank account, used only when a provider will not take a charity payment. Purged with the payment it served |
| **Respite** | A break for a disabled person and/or their carer — the thing the grant funds |
| **Support recipient** | The cared-for person, where that is not the applicant. Their condition profile is visible to trustees; their identity is not. Field group on **Application** |
| **SWEMWBS** | Short Warwick-Edinburgh Mental Wellbeing Scale — seven of the eleven wellbeing questions use its published wording and frequency scale. **Whether Revitalise holds a licence to report against national norms is unconfirmed**; nothing in the build depends on it |
| **Trustee** | A board member who reviews eligible applications and records a verdict. Two per Application per round; both must approve |
| **Wellbeing answers** | Eleven scored questions: one ONS life-satisfaction question (0–10 whole number), the seven SWEMWBS items, and three Revitalise "last year" questions |

---

## Scoring Terms

| Term | Definition |
|---|---|
| **Feeling-scale inversion** | The life-satisfaction answer is inverted: a reported 0 scores 10 points, because low wellbeing means high need |
| **Likert mapping** | Each wellbeing answer's option **value** maps to points, position 1 scoring 5 down to position 5 scoring 1. *Not sure* scores 0.5 — the only non-integer, and load-bearing for the rounding rule |
| **Maximum score** | **60** = 10 (life satisfaction) + 10 × 5 (the ten Likert items). Settled in Dev Summary revision 0.3; earlier documents saying 55 are superseded |

---

## Platform Terms (common to all Power Platform projects)

| Term | Definition |
|---|---|
| **BPF** | Business Process Flow — a guided, staged process in a Model-Driven App |
| **Column (field-level) security** | A Dataverse profile controlling read/update per column. Here it is the control that replaces the process owner's manual anonymisation |
| **Connection Reference** | A named pointer to a connection; allows environment-specific credentials without changing flow logic |
| **Environment Variable** | A named configuration value set per environment; replaces hardcoded URLs or settings |
| **MDA** | Model-Driven App — Power Platform UI driven by the Dataverse data model |
| **Managed Solution** | A solution locked for editing — deployed to Test, Acc and Prd |
| **Publisher Prefix** | This project uses `rev_` on every custom schema name |
| **SLA** | Service Level Agreement — time target for completing an action. **No SAR or availability SLA exists in any source for this project** |
| **Unmanaged Solution** | A solution open for editing — used in Dev only |
| **V1–V6** | This system's verification ladder: well-formed, packaged, accepted, openable-and-saveable by a human, executed end-to-end, and (proposed) Client accepted. See `constraints/technology/technology-constraints.md` → C-TECH-053 |
