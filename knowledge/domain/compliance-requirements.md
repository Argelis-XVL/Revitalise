# Compliance Requirements — The Non-Negotiables

**Populated 2026-08-18** (`IMP-0034`). Sources as listed in `knowledge/domain/overview.md`.

Loaded by **architect-agent** on activation and by **plan-agent** at the compliance step. Each row
is a control that must be satisfied before a release, with the thing that actually verifies it.
Where the verification is a person rather than a command, that is stated — a control verified only
by someone remembering to look is the weakest kind this project has, and `C-TECH-049`'s history is
the evidence.

---

## 1. Blocking controls

| # | Control | Source | Verified by |
|---|---|---|---|
| CR-01 | **Special-category data never reaches a trustee.** Identity and health-identifying columns are hidden from the trustee role by a column-security profile; the free-text narrative is AI-redacted before trustee review | DPIA R1; SDD NFR-001; data model §FLS | `scripts/verify-field-security-coverage.py` build gate (every `IsSecured=1` column is released by a profile, and no profile releases an unsecured column). ⚠️ It does **not** verify the *set* of columns is the right set — that is a human judgement against the access matrix |
| CR-02 | **Special-category data never influences the automated score.** No expression in the scoring flow references a special-category column | SDD FR-016 (HARD); DUAA 2025 | `no-special-category-data-in-scoring` build gate. HARD; a false PASS here was found once and is the reason `verify-build-config.py` exists (`IMP-0007`) |
| CR-03 | **Bank and payment data behind the finance role only**; the administrator role has no access | SDD NFR-002; DPIA R5 | Role and profile definitions in solution source; ⚠️ no gate asserts the negative (that admin has *no* privilege). Human check against the access matrix |
| CR-04 | **No personal data in any operational log** — run status, error message, record reference only | SDD NFR-012, NFR-016 | Human review of every flow's error path and of the Error Log schema. ⚠️ No gate |
| CR-05 | **Automated retention by status plus trigger date, running at least monthly**, with cascade from Application | SDD NFR-010; Data Governance §4 | Native Dataverse bulk-delete jobs, configured per environment. ⚠️ Environment configuration, not solution source — it is invisible to every build gate and must be verified in the environment |
| CR-06 | **UK region and UK residency across every component**, including Dataverse, AI Builder, DocuSign, QuickBooks and the SharePoint library. Zero transfers outside the UK | SDD NFR-009; DPIA action A5 | ⚠️ **OPEN — TAD risk A-R19.** To be verified at environment setup and recorded as evidence. Not currently evidenced anywhere |
| CR-07 | **Lawful basis documented for every entity holding PII** | `C-DOM-002` (HARD) | SDD §7.2 lists it per entity; any new entity must be added there before it is designed |
| CR-08 | **Personal data classified before any entity is designed** | `C-DOM-001` (HARD) | TAD §3 classification column fully populated, per entity, with a tier |
| CR-09 | **Erasure reaches every copy** — Dataverse, signed-PDF library, DocuSign, QuickBooks — including referees, helpers, group members and emergency contacts, with legal-hold carve-outs reported to the requester | SDD FR-049, FR-051, FR-052 | ⚠️ The helper flow is **not built**. Currently a design commitment only |
| CR-10 | **Audit every create, update and delete** on a record holding personal data, with timestamp, actor, affected record and before/after values | SDD NFR-014 | `provisioning/dataverse/ensure-auditing.ps1`; per-environment configuration |

---

## 2. Controls that are open, and what that means

Naming these is the point of this section. Each is a commitment made in an approved document that
nothing yet satisfies. A release that claims compliance without stating these is claiming a level
it has not reached — the `C-TECH-053` failure applied to compliance rather than to components.

| Gap | Status | Consequence if not closed |
|---|---|---|
| **No SAR extract mechanism** (FR-053) | Accepted as a known gap at the architecture gate; `C-DOM-005`; TAD risk A-R22 | An Article 15 request cannot be answered from the system. Statutory default is one month and **no internal SLA exists**, so test-agent has no threshold to test |
| **DUAA automated-decision position** (DPIA §8) | DPO confirmation outstanding | Auto-rejection may need to route to the process owner instead of closing. Configuration, not rebuild — but it is a live compliance question |
| **Health free-text retained 6 years** (SDD OQ-006) | DPO minimisation decision open | The design allows earlier redaction as configuration |
| **UK residency evidence** (NFR-009, DPIA A5) | Open | Residency is currently assumed, and the DPIA action that requires evidencing it is unclosed |
| **Column security replacing manual separation** | DPO sign-off required before build (data model §FLS) | The control is *stronger* than the manual one it replaces but *different*. Fallback if physical separation is required: a separate trustee-facing table populated with permitted fields only |
| **Ethnic group is collected** (SDD OQ-027) | Facts changed and the DPO needs to know | The live form collects it (export col 150). `rev_ethnicgroup` is deliberately **absent** from the schema pending DPO input, so the question is now "should we keep collecting it, and on what basis" |
| **Abandoned website drafts** | No DPO position | Save-and-continue means partially completed applications holding special-category data sit on the website platform. They appear in **neither** the retention schedule nor the RoPA |
| **Application data exports in `docs/Import/`** | ⚠️ **Unresolved and it outranks the rest** | If `Application Data Export.xlsx` holds real applicant data, special-category health data is sitting in a git-tracked folder. Flagged in the 2026-08-18 PM redesign as decision D-8. Settle whether it is real or synthetic |
| **Role-membership review cadence** | `[TBC]` | Quarterly or per panel round is the working assumption |
| **Second processor (Jan)** | Under consideration, unassigned | The RoPA processor record would need updating |

---

## 3. What to do when a compliance control cannot be verified mechanically

Say so, in the gate output, naming the control. Do not report a control as satisfied because it is
designed. The distinction this project learned the expensive way:

- **Designed** — it is in the TAD.
- **Built** — the component exists in source.
- **Deployed** — the target accepted it (V3).
- **Working** — a human exercised it (V4) or it ran end to end (V5).

`C-TECH-053` forbids reporting a level not executed. CR-05, CR-06 and CR-10 are all
**environment configuration** and therefore invisible to every build gate in this repo: they can
be *designed* and *deployed* and still not be *working*, and no amount of green CI will tell you.
