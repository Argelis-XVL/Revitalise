# Business Rules — Charitable Respite Grant Administration

**Populated 2026-08-18** (`IMP-0034`). Sources as listed in `knowledge/domain/overview.md`.

Rules are stated as constraints. Each cites the requirement or source that mandates it. A rule
marked ⚠️ is **not yet confirmed by the party who owns it** — treat it as the current working
position, not as settled, and do not build a gate on it without saying so.

---

## Applicant and Application Rules

| Rule | Detail |
|---|---|
| BR-A01 | An Applicant is stored **once** and may hold many Applications. A repeat applicant is one Applicant row with two Applications — matched on email plus name at intake |
| BR-A02 | The Applicant's **primary name column is the pseudonymised ID** (`REV-A-00001`), never the person's name (TAD ADR-013) |
| BR-A03 | An Application carries the reference (`REV-2026-001` format), the current status, the break request, the financial answers, the eleven wellbeing answers and the per-block consents |
| BR-A04 | `rev_agerange` is derived from date of birth and `rev_locationarea` from postcode **at write time**, so trustees see the derived band and never the raw value (FR-027) |
| BR-A05 | A replayed or duplicated intake webhook **updates** the existing Application rather than creating a second one — the form submission id is an alternate key |
| BR-A06 | Referee and emergency-contact details are **not** collected at intake. They are collected on a separate form sent after board approval. ⚠️ **Who completes that form — the applicant relaying, or the third parties self-reporting — is unspecified** and materially changes the build |
| BR-A07 | An Application with a missing scored answer gets **no automated outcome**: status becomes *Under Review* and it routes to the process owner (FR-022) |

## Scoring Rules

| Rule | Detail |
|---|---|
| BR-S01 | The circumstance score runs **0 to 60** = 10 (life satisfaction) + 10 × 5 (Likert items). Documents stating 55 are superseded (Dev Summary rev 0.3) |
| BR-S02 | The life-satisfaction answer is **inverted**: reported 0 scores 10 points. Low wellbeing means high need |
| BR-S03 | Each Likert answer maps by option **value**, position 1 → 5 points down to position 5 → 1 point. *Not sure* → **0.5**, the only non-integer value |
| BR-S04 | All ten Likert questions are worded **positively**, so value 1 is the highest-need answer. This was verified against each question text individually, not assumed |
| BR-S05 | The **knockout threshold** and **income ceiling** are held in Settings and adjustable by the process owner without editing a flow. ⚠️ **The board has not set the threshold value**; PRD seeding is blocked by design until it does (SDD OQ-001, OQ-002) |
| BR-S06 | *Borderline* means **within 5 points** of the knockout threshold, and every borderline case is reviewed by the process owner |
| BR-S07 | An application over the income ceiling is rejected **regardless of score** |
| BR-S08 | **Disability data, health-condition data and the free-text narrative must not influence the score.** HARD (FR-016, DUAA). Enforced by the `no-special-category-data-in-scoring` build gate — the guarantee is that no expression in the scoring flow *references* a special-category column |
| BR-S09 | The process owner may **override any automated outcome**, and does not re-score by hand |
| BR-S10 | ⚠️ Whether automatic rejection at the threshold stands without further human review is a **DPO decision under DUAA 2025** and is open. If tightened, auto-reject routes to the process owner instead of closing |
| BR-S11 | The £6,000 savings figure is the live form's own wording and is **fixed in a column label rather than configurable**. ⚠️ Confirm it is current before go-live; changing it later means changing form and label together |

## Panel Review Rules

| Rule | Detail |
|---|---|
| BR-R01 | A Review is **one Application in front of one monthly panel round**, with an attempt number (first, second or third) |
| BR-R02 | **Two trustees** are assigned per Review, as Dataverse User lookups — not a custom table |
| BR-R03 | **Both trustee verdicts must be approve** for the Application to move to approved |
| BR-R04 | An Application may be reviewed across up to **three attempts**; the **third rejection closes it** |
| BR-R05 | A trustee **never** sees identifying data. Column security on the trustee role — not app design — is the control that guarantees it |
| BR-R06 | Trustees never touch the tables directly; they read through an app whose loadable columns the security profile decides |
| BR-R07 | The free-text narrative is **AI-redacted before** it reaches a trustee. Below **85% confidence** the case is flagged for the process owner's manual review |

## Grant and Acceptance Rules

| Rule | Detail |
|---|---|
| BR-G01 | A Grant is created **when an Application succeeds**, and is the anchor for Payment |
| BR-G02 | The Grant holds the acceptance-agreement field group (signature status, signed date, signed-PDF link) and the impact-report field group |
| BR-G03 | The acceptance document is pre-populated with the applicant's name, amount, provider, dates and conditions (FR-041) |
| BR-G04 | Two signatures are required **in sequence**: the **applicant first**, then the referee or GP (FR-042) |
| BR-G05 | Reminders at **3 and 7 days**; escalation to the process owner at **14 days** unsigned (FR-043, FR-044) |
| BR-G06 | On both signatures, the Grant status becomes **Acceptance Signed** and the signed PDF is linked (FR-045) |
| BR-G07 | A **manual print-sign-scan route** must be recordable against the Grant for applicants who cannot sign electronically (FR-046) |
| BR-G08 | Acceptance documents can be issued for a **batch** of grants approved at one meeting (FR-047) |
| BR-G09 | The signed PDF is the **only** document that leaves Dataverse. It lives in one SharePoint library, referenced by URL from the Grant (TAD ADR-014) |
| BR-G10 | The signed PDF is **not** protected by Dataverse column security, so the **library ACL is the only control** keeping it from the trustee role |
| BR-G11 | The impact report is due **one month after the holiday end date** |
| BR-G12 | `rev_finalpaymentdate` on the Grant **starts the six-year retention clock** |
| BR-G13 | ⚠️ Grant status values: the approved TAD §4 states **Awarded · Acceptance Issued · Acceptance Signed · Paid**. The earlier data model states *granted, issued, cancelled, withdrawn*. **The TAD wins**; the disagreement is recorded here rather than resolved silently |

## Finance Rules

| Rule | Detail |
|---|---|
| BR-F01 | **Bank data lives in exactly one place** — the Bank Account table. Never duplicated onto a Payment row, never left on the Applicant |
| BR-F02 | Bank Account and Payment are readable by the **finance role only**. The administrator role has **no access at all** — separation of duties, defence in depth (NFR-002) |
| BR-F03 | A Payment names **one Payee**: a Bank Account, being either a provider account or an applicant reimbursement |
| BR-F04 | The Provider record holds **no finance data** — its account lives in Bank Account |
| BR-F05 | A provider account persists while the provider is active and is reused across grants. An **applicant reimbursement account is purged with the payment it served**, so bank details never outlive the disbursement |
| BR-F06 | A proposed Payment is matched against QuickBooks on holiday provider (via the Grant), holiday dates and grant reference, and a possible double-pay is **flagged before issue** |
| BR-F07 | ⚠️ Automation #8 (Provider / Bank Account / Payment) has **no functional requirement behind it** in the approved SDD (TAD §3.5 conflict 2). It must be authorised as a scope addition or descoped before hours are booked to it |

## Retention and Erasure Rules

| Rule | Detail |
|---|---|
| BR-D01 | Retention keys off **status plus trigger date on one record**, not on four copies |
| BR-D02 | Review, Grant and Payment **cascade** from Application, so deleting the Application removes the whole case in one operation |
| BR-D03 | Retention runs **automatically and at least monthly**. No record depends on anyone remembering |
| BR-D04 | Erasure locates data across Applicant, Application, Review, Grant, Payment, the signed-PDF library, DocuSign and QuickBooks — **including** referees, helpers, group members and emergency contacts |
| BR-D05 | A legal-hold carve-out (the six-year financial duty, or safeguarding) is **retained and reported to the requester** — never silently applied |
| BR-D06 | The anonymised snapshot is written **at outcome, before the source record is purged**, holds no identifiers and is **never linked back**. A view alone would not survive the purge |
| BR-D07 | **No personal data in any operational log.** Run status, error message and record reference only (NFR-012, NFR-016) |
