# Solution Design Document — <Feature Name>

**Feature Slug:** <slug>
**Requested By:** <name / team>
**Date:** <YYYY-MM-DD>
**Status:** DRAFT | APPROVED

---

## 1. Business Context
<!-- Why is this feature needed? What problem does it solve? -->

## 2. Objectives
- <Objective 1>

## 3. Scope
### In Scope
- <item>
### Out of Scope
- <item>

## 4. Functional Requirements
<!-- Load skills/how-to-write-requirements.md before completing this section -->

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | The system SHALL… | High / Med / Low |

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-001 | | Performance / Security / Compliance / Accessibility |

## 6. User Stories
### US-001: <Title>
**As a** <role>, **I want** <goal>, **so that** <benefit>.

**Acceptance Criteria:**
- Given <precondition>, when <action>, then <expected result>

## 7. Compliance & Regulatory Considerations
<!-- Load skills/compliance-checklist.md §1 and knowledge/domain/compliance-requirements.md -->

## 8. Assumptions & Dependencies
- <assumption>

## 9. Open Questions
| # | Question | Owner | Due |
|---|---|---|---|

## 10. Effort & Baseline

<!--
  CHANGED 2026-08-19. This section used to ask for "**Range:** <low>–<high> days" and nothing
  else, and that is how IMP-0029 (blocker) happened: an APPROVED SDD stated 106–160 build
  hours over 7 automations against a signed baseline of 292 hours over 9, and every downstream
  document inherited the wrong figure.

  An SDD does not own hours, fees, phase membership or dates. The contractual baseline does —
  docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx and the signed Service Agreement.
  So this section CITES the baseline and records only what the SDD genuinely owns: a
  relative size, and the assumptions behind it.

  Load skills/how-to-estimate-effort.md before completing this section.
-->

**Size (this feature only):** XS / S / M / L / XL
**Drivers of that size:** <what makes it that size — new integration, regulated data, unknown platform contract, …>
**Assumptions:** <key assumptions; anything that would change the size if wrong>

**Baseline reference — cited, never restated:**

| | |
|---|---|
| WBS task id(s) | <e.g. 1.3, 1.4 — the ids this feature delivers> |
| Baseline document | `docs/Import/<WBS file>` (authoritative for hours, phase and dates) |
| Contracted phase | <as stated by the baseline — do not infer it> |

> Do **not** write an hours figure, a fee, a phase membership or a delivery date into this
> document. If the reader needs one, they read the baseline. If the baseline and this feature
> disagree about scope, say so here as a discrepancy and route it — do not resolve it by
> writing a new number (`IMP-0029`, `IMP-0031`).

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
