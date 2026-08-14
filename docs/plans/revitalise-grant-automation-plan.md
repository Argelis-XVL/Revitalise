# Solution Design Document — Revitalise Grant Application Automation

**Feature Slug:** revitalise-grant-automation
**Requested By:** Revitalise (Emily, process owner), design authored by Xander Lykopoulos / Argelis Consultancy
**Date:** 2026-08-09
**Status:** APPROVED · **Amendment A-01 PROPOSED 2026-08-13 — see below, NOT yet approved**

---

> ## 📌 Amendment A-01 — PROPOSED, awaiting plan-agent and process-owner approval
>
> **Raised by:** development-agent, 2026-08-13, during the revision 0.8 fix cycle.
> **Status: PROPOSED. This amendment is NOT approved and nothing below it has been rewritten
> as though it were.** The body of this SDD is unchanged apart from three clearly marked
> annotations that point here (FR-013, its acceptance criterion, and §9 OQ-002).
>
> ### Why this is an amendment block and not an edit
>
> This SDD is `plan-agent`'s artefact and carries **Status: APPROVED**, gated on a human
> `APPROVED` per `agents/plan-agent.md` and `agents/WORKFLOW.md`. `agents/WORKFLOW.md` defines
> no procedure for amending an approved upstream document, and `development-agent` has no
> authority to re-issue one — so silently correcting the requirement text would have bypassed
> the plan gate and made an approved document say something no one approved. The evidence is
> recorded here instead, the original wording is left visible, and the amendment is routed for
> approval. **Requested action: `lead-agent` should route this to `plan-agent` to fold into a
> revision 0.6 of this SDD and re-gate it.**
>
> ### New evidence
>
> `docs/Import/Book(Sheet1).csv` (received 2026-08-13; windows-1252 encoded) contains **25 real
> applications**, each with the published *"Overall Current Circumstance Score (Out of 60, 60 as
> most severe)"* the process owner arrived at by hand and the **eleven answers** that produced
> it. This is the first ground truth for the scoring methodology; every previous statement about
> it in this SDD came from prose in the source documents.
>
> Reconstructing the score from the answers reproduces the published total **exactly on all 25
> rows**. The reconstruction is asserted permanently, against the shipped configuration rather
> than against a copy of it, by
> `src/tests/solutions/ScoringInvariants.Tests.ps1` → *"OQ-002 — the scoring configuration
> reproduces 25 REAL hand-scored applications exactly"*.
>
> **Total = (10 − life_satisfaction_raw) + Σ points(7 SWEMWBS answers) + Σ points(3 "last year" answers)**
> where `points = {1:5, 2:4, 3:3, 4:2, 5:1, 6:0.5}` and ordinal position 1 is the highest-need
> answer on both response scales.
>
> Three competing readings were tested against the same data and fail, so the direction is
> established rather than assumed: reversing the agreement scale reproduces 7 of 24 rows,
> removing the point inversion 3 of 24, and dropping the life-satisfaction inversion 4 of 24.
>
> ### What it resolves, and what it does not
>
> | Item | Effect |
> |---|---|
> | **OQ-002** — exact scoring methodology | **RESOLVED by evidence.** The inversion, the point mapping and the full answer set are now fixed and test-asserted. |
> | **FR-013** — as written, names only an agree/disagree scale | **PARTLY WRONG, and this is test-report D-009.** Corrected wording proposed below. |
> | **FR-022** — behaviour "to be confirmed under OQ-002" | **Behaviour confirmed and strengthened.** See below. |
> | **OQ-001** — knockout cut-off and borderline band | **STILL OPEN. This amendment does NOT resolve it** — see the note below, which matters. |
>
> #### ⚠️ OQ-001 is not resolved, and was mis-scoped in the request that led to this work
>
> This fix cycle was commissioned as "resolve OQ-001 (exact scoring weights)". **OQ-001 is not
> the scoring weights.** As written in §9 it asks *"Where should the knockout cut-off score sit,
> and how wide is the borderline band Emily reviews by hand?"* — the **scoring weights are
> OQ-002**. The CSV settles OQ-002 and cannot settle OQ-001: it contains scores and answers but
> **no accept/reject outcomes**, so there is nothing in it from which a cut-off could be
> inferred. OQ-001 remains a **board/Emily decision** and stays open. (The mix-up is traceable:
> comments added in revision 0.3 claim that settling the 0-to-60 range "unblocks SDD OQ-001 and
> OQ-002". Unblocking is not resolving, and only OQ-002 is now resolved.)
>
> **What the new evidence does change about OQ-001, and the board needs to know it:** the
> reachable floor of a fully answered application has moved **from 10 down to 5**. "Not sure" is
> worth 0.5 points, so ten "Not sure" answers plus maximum reported life satisfaction total 5.
> Any knockout threshold at or below 5 was previously unreachable and now is not.
>
> ### Two substantive findings behind the amendment
>
> **1. The ten generic wellbeing questions do not share one response scale.** The seven SWEMWBS
> items (*"…over the last 2 weeks"*) are answered **None of the time / Rarely / Some of the time
> / Often / All of the time**. The three *"Thinking about the last year, have you been able
> to…"* questions are answered **Strongly disagree / Disagree / Neutral / Agree / Strongly
> agree**. Across all 25 rows the two label sets are **disjoint apart from "Not sure"**. The
> ordinal values coincide, so **no score changes** — but the three questions had been storing
> and displaying frequency labels, which mislabelled the evidence a trustee reads.
>
> **2. "Not sure" is a real sixth answer worth 0.5 points, not an error.** The live form offers
> it. Row 25 answered "Not sure" to all ten questions and scored **9**: life-satisfaction raw 6
> contributes 10−6=4, leaving exactly 5 points across 10 answers — 0.5 each, no remainder. It
> had been unstorable, which is test-report **D-014** (a real applicant's submission could be
> accepted and then lost when the scoring flow threw). The correct remedy is to make it a valid
> scoreable answer, not to reject and flag it.
>
> ### Proposed replacement wording for FR-013
>
> > **FR-013** — The system SHALL convert each wellbeing response to its configured point value
> > by the response's **ordinal position**, WHEN calculating the circumstance score, SO THAT the
> > charity's agreed need criteria are applied identically to every application. The ten
> > wellbeing questions use **two response scales with a shared set of ordinal values**: the
> > seven SWEMWBS items use a frequency scale (1 = *None of the time* … 5 = *All of the time*)
> > and the three "last year" questions use an agreement scale (1 = *Strongly Disagree* … 5 =
> > *Strongly Agree*). Position 1 is the highest-need answer on both and SHALL score the
> > configured maximum, because every one of the ten questions is worded positively. A sixth
> > response, **"Not sure"**, is a valid answer on every one of the ten questions and SHALL
> > score **0.5 points**.
>
> **Proposed replacement acceptance criterion:** *Given a wellbeing answer at ordinal position 1
> — "None of the time" on a SWEMWBS item, or "Strongly Disagree" on a "last year" question —
> when the score is calculated, then it contributes the configured maximum points for that
> question; and given an answer of "Not sure", then it contributes 0.5 points.*
>
> ### One consequence requiring a decision, not a correction
>
> A total can now be **fractional** (an odd number of "Not sure" answers gives an X.5), while
> `rev_circumstancescore` is a whole-number column. Revision 0.8 **rounds half up**, in the
> applicant's favour, and records the exact unrounded total in the score breakdown. **The data
> does not determine this rule** — every published total in the CSV is a whole number and the
> one "Not sure" row is whole by coincidence — so it is a judgement call flagged for the
> reviewer in the Dev Summary revision 0.8, not a derived fact. The alternative is to store the
> score as a decimal.
>
> ### FR-022 — confirmed and strengthened
>
> FR-022's DERIVED behaviour is confirmed as correct and its implementation was **widened**: the
> withhold gate previously tested only whether an answer was *absent*, so an answer that was
> present but had no configured point value passed the gate and reached a cast that threw. It
> now withholds for an answer that is absent **or** not a key of the point map. No requirement
> text change is proposed — this is the implementation catching up with what FR-022 already says.

---

> **Source:** adopted from `docs/Import/Revitalise-Automation-Solution-Design-v0.5.docx` on 2026-08-09 by plan-agent (intake mode).
> Original author: Xander Lykopoulos — Argelis Consultancy (v0.5 Draft, 14 July 2026).
> Read via a plain-text extraction of the same content. See Adoption Report in gate log.
>
> **Supporting sources** (received 2026-08-09, used for §1, §7, §8 and §9 only — no functional requirements were created from them beyond the cross-cutting retention/erasure behaviour they mandate):
> - `docs/Import/Revitalise-Process-Flow-v0.1.html` — Process Flow v0.1, July 2026 (Draft, for discussion)
> - `docs/Import/Revitalise-DPIA-v0.1.docx` — Data Protection Impact Assessment v0.1, 15 July 2026 (**Concept — for DPO review**)
> - `docs/Import/Revitalise-RoPA-v0.1.docx` — Record of Processing Activities v0.1, 15 July 2026 (**Concept — for DPO review**)
> - `docs/Import/Revitalise-Data-Governance-Framework-v0.2.docx` — Data Governance Framework v0.2, 15 July 2026 (Draft)
> - `docs/Import/Revitalise-Security-Model-v0.1.docx` — Security Model v0.1, 15 July 2026 (Draft) — used for business-level persona/role facts only
>
> **Deliberately not adopted into this SDD** (they belong to the architecture intake that follows):
> `docs/Import/Revitalise-Solution-Architecture-v0.4.docx`, `docs/Import/Revitalise-ALM-Runbook-v0.1.docx`, `docs/Import/Revitalise-Governance-Runbook-v0.1.docx`.

> ⚠️ **Reader's note.** The DPIA and RoPA that underpin §7 of this document are both at
> **"Concept draft — for DPO review"** status. They are not signed off. Three specific DPO
> decisions (OQ-004, OQ-005, OQ-006) gate build on the current design basis. This SDD may be
> approved as a statement of requirements, but build must not start on the field-level-security
> and 6-year-retention basis until those three decisions are recorded.

---

## 1. Business Context

Revitalise is a charity that awards respite-holiday grants to unpaid carers and the disabled
people they care for. The grant application process today runs across ten high-level steps and
consumes roughly **four hours of staff time per successful grant**, almost all of it carried by
one person — Emily, the process owner.

The cost is concentrated in manual data handling, not in decision-making:

- **60% of processing time is spent chasing applicants for missing information.** Applicants have
  a low average literacy level (around age-12 reading equivalent) and are applying while under
  strain, so forms arrive part-completed and each one generates several follow-up contacts.
- **Every application is scored by hand.** Emily converts wellbeing answers into a score out of 60,
  including an inverted scale on one question and Likert mapping on others.
- **Applications are moved between systems by hand.** Emily logs into the website, exports
  submissions to Excel and imports them into a master spreadsheet, in batches, creating delay
  between submission and assessment.
- **Trustee packs are anonymised by hand.** Before each monthly board cycle Emily strips names,
  contact details, addresses, ages and gender references, and scrubs free-text narratives where
  applicants refer to themselves, family members, places or clinicians. Find-and-replace misses
  indirect references such as "my husband John" or "our GP at the Riverside Practice". This takes
  three to four hours per cycle, twelve cycles a year.
- **Trustees receive a static mail-merged Word pack** plus a master spreadsheet. It is hard to
  navigate at 20+ applications, one trustee (Kevin) wants a stripped data-only view while others
  want the narrative, and decisions come back as scattered emails that Emily collates manually.
- **Acceptance forms are built in Canva, exported as PDF and emailed.** Dual signature is required
  (applicant plus referee or GP). Average return time is five days; some run to weeks.
- **Duplicate-grant checking is a manual email-address lookup.** Manageable at 68 cumulative
  grants; unreliable as volume grows across years.

The current run rate is 68 grants in roughly four months, against a planning assumption of ~200
grants per year. The process does not scale, and it carries a single-point-of-failure risk: the
master spreadsheet is effectively "Emily's laptop is the source of truth".

Alongside the efficiency problem there is a compliance problem. The process handles
**special-category health and disability data about people in vulnerable circumstances, at scale**,
plus bank details and financial hardship information. The manual anonymisation control depends on
one person doing a careful job under time pressure, and a single missed name in a trustee pack is a
personal-data breach. A DPIA is required under UK GDPR Article 35 for this processing.

---

## 2. Objectives

*(DERIVED — the source states outcomes and savings but does not list objectives explicitly.)*

1. **Cut staff handling time per successful grant from ~4 hours to under 1 hour**, releasing
   approximately 330 staff hours per year at ~200 grants/year.
2. **Prevent incomplete applications at source** rather than chasing them afterwards, targeting a
   60–70% reduction in incomplete submissions.
3. **Make assessment consistent and evidenced** by calculating the circumstance score
   automatically against criteria the charity controls, while keeping a human able to review and
   override every outcome.
4. **Replace manual anonymisation with a platform-enforced control** so that trustee review is
   anonymous by design, with human review of anything the automated redaction is unsure about.
5. **Give trustees one place to review cases and record decisions**, serving both the data-only
   and narrative-reading preferences from the same source, with an offline fallback so no trustee
   is excluded.
6. **Remove chasing from grant acceptance** by issuing pre-populated dual-signature acceptance
   documents with automatic reminders and escalation.
7. **Establish a single, governed system of record** with automatic retention and erasure, so no
   record depends on someone remembering to delete it, and remove the spreadsheet dependency.
8. **Keep the whole solution inside Revitalise's published data-protection position** — UK data
   residency, least privilege, documented lawful bases, and an auditable trail.
9. **Leave the solution maintainable by a non-developer** — thresholds, templates and mappings
   adjustable by Emily or a future administrator without code.

---

## 3. Scope

### In Scope

Seven automations, in the source's priority order:

| # | Automation | Business outcome |
|---|---|---|
| 1 | Form Validation & Completeness | Incomplete applications cannot be submitted |
| 2 | Scoring Engine | Circumstance score, status flags and daily summary calculated automatically |
| 3 | Acceptance Workflow (DocuSign) | Pre-populated dual-signature acceptance with reminders and escalation |
| 4 | Website → System-of-Record Intake | Submissions become records automatically, with a reference number |
| 5 | AI-Assisted Anonymisation & Trustee Pack Preparation | Free-text narratives redacted with human review of low-confidence cases |
| 6 | Trustee Review Portal | One place for trustees to review anonymised cases and record verdicts |
| 7 | Duplicate-Grant Check (QuickBooks) | Prior grants flagged before assessment |

Plus the cross-cutting behaviour mandated by the Data Governance Framework, DPIA and RoPA:

- Automated retention and deletion by outcome and trigger date, across every system holding a copy.
- On-demand right-to-erasure handling with legal-hold carve-outs.
- Subject access request fulfilment.
- Retention/erasure evidence logging.
- A 30-minute walkthrough with Emily per automation (included in the build effort).

### Out of Scope

Carried over from the source, unchanged:

- **Payment process automation** (company card, provider payments) — involves financial controls
  and provider agreements, not technology.
- **Impact reporting automation** — already handled by Ian's existing dashboard.
- **Grants management system evaluation or replacement** — a separate decision if Revitalise
  outgrows the platform.
- **Formal staff training programme** — each automation includes a 30-minute walkthrough only.
- **Historical data migration** beyond the current application round. Migration of the current
  round is scoped inside Automation #4 setup.
- **Power BI dashboards** — dropped in v0.5; a possible later enhancement, not this scope.
- **Full QuickBooks API integration** for duplicate checking — the fallback cross-reference
  approach is in scope; full API integration is a later enhancement.

Out of scope for **this document** specifically (deliberate boundary, not a gap):

- Technical architecture, data model, table schemas, flow internals, security-role configuration
  and deployment topology — these belong to the Technical Architecture Document produced by the
  architect-agent from `docs/Import/Revitalise-Solution-Architecture-v0.4.docx`.
- Release and operations procedure — covered by the ALM Runbook and Governance Runbook.

---

## 4. Functional Requirements

Requirements are written at business/functional level. Where a requirement names an external
system a business user interacts with (Teams, DocuSign, QuickBooks) that naming is retained from
the source because it is part of the agreed business process; no data model or automation internals
are specified here.

### A. Application form validation & completeness (Automation #1)

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | The system SHALL prevent submission of a grant application WHEN any mandatory field (full name, date of birth, postcode, financial situation, preferred holiday dates, provider preference) is empty, SO THAT incomplete applications are never created and staff time is not spent chasing them. | High |
| FR-002 | The system SHALL display plain-English, field-specific guidance and validation messages WHEN an applicant leaves a mandatory field empty or enters a value that fails validation, SO THAT applicants can correct their own answers without contacting the charity. | High |
| FR-003 | The system SHALL present financial detail questions only WHEN an income band has been selected, and carer questions only WHEN the applicant has indicated they are travelling with a carer, SO THAT applicants are not asked questions irrelevant to their circumstances. | Medium |
| FR-004 | The system SHALL display a completion-progress indicator throughout the application, SO THAT applicants can see how much remains and are less likely to abandon partway. | Medium |
| FR-005 | The system SHALL allow an applicant to save a partially completed application and resume it later, SO THAT applicants who need help mid-application do not lose their answers. | Medium |
| FR-006 | The system SHALL present a summary of all answers with a per-section edit option before final submission, SO THAT applicants can correct mistakes before the application enters the process. | Medium |

### B. Intake into the system of record (Automation #4)

| ID | Requirement | Priority |
|---|---|---|
| FR-007 | The system SHALL create a grant application record automatically WHEN an applicant submits the online application form, SO THAT no manual export-and-import step is required and assessment can begin immediately. | High |
| FR-008 | The system SHALL assign every new application a unique reference in the format `REV-YYYY-NNN` and record its submission timestamp WHEN the application record is created, SO THAT each application can be identified unambiguously in correspondence, reporting and audit. | High |
| FR-009 | The system SHALL notify the process owner via Microsoft Teams with the applicant name and application reference WHEN a new application record is created, SO THAT new applications are picked up without anyone polling the website. | Medium |
| FR-010 | The system SHALL record the failure and alert the process owner WHEN an incoming submission cannot be turned into an application record, SO THAT no application is silently lost. | High |

### C. Scoring engine (Automation #2)

| ID | Requirement | Priority |
|---|---|---|
| FR-011 | The system SHALL calculate a circumstance score out of 60 from the applicant's wellbeing answers WHEN an application record is created, SO THAT scoring is consistent and no longer performed by hand. | High |
| FR-012 | The system SHALL invert the applicant's reported feeling answer so that a lower reported feeling produces a higher score, WHEN calculating the circumstance score, SO THAT the score reflects need rather than positivity. | High |
| FR-013 | The system SHALL convert each Likert wellbeing response to its configured point value (Strongly Disagree = 5, Disagree = 4, Neutral = 3, Agree = 2, Strongly Agree = 1) WHEN calculating the circumstance score, SO THAT the charity's agreed need criteria are applied identically to every application. ⚠️ **This wording is now known to be incomplete — see Amendment A-01 (PROPOSED) at the top of this document, and test-report D-009.** The agree/disagree labels are correct for only **three** of the ten wellbeing questions; the other seven use a frequency scale, and a sixth response ("Not sure", 0.5 points) is missing entirely. Left as originally approved pending plan-agent re-issue; replacement wording is proposed in A-01. | High |
| FR-014 | The system SHALL set the application status to Auto-pass, Borderline or Auto-reject by comparing the circumstance score against the configured knockout threshold and borderline band WHEN the score has been calculated, SO THAT staff attention goes only to the cases that need human judgement. | High |
| FR-015 | The system SHALL evaluate the applicant's financial answers against the configured income ceiling and record the outcome as a separate eligibility flag WHEN an application is scored, SO THAT applications outside the financial eligibility criteria are identified independently of the circumstance score. | High |
| FR-016 | The system SHALL exclude disability data, health-condition data and the free-text narrative from the circumstance score calculation, SO THAT special-category data does not influence an automated outcome. | High |
| FR-017 | The system SHALL allow the process owner to change the knockout threshold, the borderline band and the income ceiling without any change to the automation logic, SO THAT the board can adjust criteria without developer involvement. | High |
| FR-018 | The system SHALL allow the process owner to override the automatically assigned status on any application and SHALL record that an override was made, WHEN the process owner disagrees with the automated outcome, SO THAT a named human remains accountable for every outcome. | High |
| FR-019 | The system SHALL route every application with status Borderline to the process owner for manual review before it progresses, SO THAT marginal cases receive human judgement rather than an automated verdict. | High |
| FR-020 | The system SHALL remove applications with status Auto-reject from the active working list into a separate rejected list WHEN the status is set, SO THAT the active list shows only applications requiring action. | Medium |
| FR-021 | The system SHALL send the process owner a daily summary stating how many applications were scored, how many were auto-rejected and how many are borderline awaiting review, SO THAT the process owner has oversight without opening the system. | Medium |
| FR-022 | The system SHALL withhold a final automated outcome and route the application to the process owner WHEN any answer required by the scoring methodology is absent, SO THAT incomplete data cannot produce a spurious automated rejection. *(DERIVED — see Interpretations; behaviour to be confirmed under OQ-002.)* | High |

### D. Duplicate-grant check (Automation #7)

| ID | Requirement | Priority |
|---|---|---|
| FR-023 | The system SHALL check each new application against the charity's historical grant payment records in QuickBooks WHEN the application record is created, SO THAT previously funded applicants are identified before assessment rather than after. | Medium |
| FR-024 | The system SHALL flag the application as a possible duplicate and record the prior grant reference, date and amount WHEN a match is found against the applicant's identifying details, SO THAT staff can investigate before a second grant is awarded. | Medium |
| FR-025 | The system SHALL record "no prior grants found" against the application WHEN the check completes without a match, SO THAT the check is evidenced as having run. | Low |

### E. Anonymisation and trustee pack preparation (Automation #5)

| ID | Requirement | Priority |
|---|---|---|
| FR-026 | The system SHALL produce a redacted copy of each free-text narrative in which detected personal identifiers are replaced with category labels (`[NAME]`, `[FAMILY MEMBER]`, `[GP PRACTICE]`, `[ADDRESS]`, `[PHONE]`) WHEN an application becomes eligible for trustee review, SO THAT trustees can weigh a real case without learning whose it is. | High |
| FR-027 | The system SHALL replace specific ages with an age band and specific locations with a region in all trustee-visible content, SO THAT an applicant cannot be identified from quasi-identifiers left in the text. | High |
| FR-028 | The system SHALL retain region, preferred dates, circumstance score, holiday preferences and general condition information in trustee-visible content WHEN redacting, SO THAT trustees keep the information they need to reach a funding decision. | High |
| FR-029 | The system SHALL flag a redacted narrative for manual review and SHALL withhold it from trustees WHEN the redaction confidence falls below the configured threshold (initially 85%), SO THAT no unreviewed low-confidence redaction reaches the board. | High |
| FR-030 | The system SHALL allow the process owner to review, correct and release a flagged redaction WHEN a narrative has been flagged, SO THAT a human confirms every uncertain redaction before disclosure to trustees. | High |
| FR-031 | The system SHALL make the original unredacted narrative readable only to the administrator role and the service identity, SO THAT raw special-category free-text is not disclosed beyond those who need it. | High |
| FR-032 | The system SHALL generate a per-application anonymised document containing the redacted narrative, score breakdown, holiday details and staff recommendation, SO THAT trustees who cannot use the review portal are not excluded from the decision. | Medium |
| FR-033 | The system SHALL allow trustee-pack preparation to be run on demand by the process owner and SHALL also run it on a schedule ahead of each board meeting, SO THAT the pack is ready without anyone remembering to start it. | Medium |

### F. Trustee review portal (Automation #6)

| ID | Requirement | Priority |
|---|---|---|
| FR-034 | The system SHALL present trustees with a sortable and filterable summary list of the applications under review showing circumstance score, region, preferred dates and status, SO THAT a trustee who prefers a data-only view can work entirely from one screen. | High |
| FR-035 | The system SHALL provide a per-application detail view showing the redacted narrative, the score breakdown, holiday details and the staff recommendation, SO THAT trustees who prefer to read the case have the full anonymised picture. | High |
| FR-036 | The system SHALL withhold applicant identifying information from every trustee-facing view, SO THAT trustee review is anonymous by design rather than by manual preparation. | High |
| FR-037 | The system SHALL allow a trustee to record a verdict of Approve, Defer or Reject with optional notes against each application under review, SO THAT decisions are captured in structured form during the meeting instead of by email afterwards. | High |
| FR-038 | The system SHALL restrict trustee access to the applications that are eligible for review in the current round, SO THAT trustees do not see cases outside their remit. | High |
| FR-039 | The system SHALL provide a print or offline export of the trustee views, SO THAT trustees who prefer to read away from a screen are not disadvantaged. | Medium |
| FR-040 | The system SHALL apply the recorded trustee verdicts to the corresponding grant records and initiate the acceptance workflow for approved applications WHEN the process owner confirms "Finalise decisions" after the board meeting, SO THAT the meeting's outcome is enacted in one controlled, auditable step. | High |

### G. Grant acceptance (Automation #3)

| ID | Requirement | Priority |
|---|---|---|
| FR-041 | The system SHALL create an acceptance document pre-populated with the applicant's name, grant amount, holiday provider, dates and conditions and route it for electronic signature via DocuSign WHEN an application status is set to Approved, SO THAT staff no longer build and email acceptance forms by hand. | High |
| FR-042 | The system SHALL route the acceptance document for two signatures in sequence — the applicant first, then the referee or GP — SO THAT the dual-signature requirement is satisfied without manual coordination. | High |
| FR-043 | The system SHALL send automatic signature reminders three days and seven days after issue WHEN an acceptance document remains unsigned, SO THAT the average five-day return time reduces without staff chasing. | High |
| FR-044 | The system SHALL notify the process owner with the applicant's details WHEN an acceptance document remains unsigned fourteen days after issue, SO THAT stalled acceptances are escalated rather than forgotten. | High |
| FR-045 | The system SHALL set the grant status to "Acceptance Signed" and link the completed signed document to the grant record WHEN both signatures have been received, SO THAT the signed evidence is filed automatically and remains auditable. | High |
| FR-046 | The system SHALL support a manual print-sign-scan acceptance route recorded against the grant record WHEN an applicant cannot sign electronically, SO THAT non-digital applicants are not excluded from receiving a grant. | Medium |
| FR-047 | The system SHALL issue acceptance documents for a batch of approved applications in a single run WHEN multiple grants are approved at one board meeting, SO THAT a full board round can be issued without per-application handling. | Medium |

### H. Retention, erasure and information rights (cross-cutting)

| ID | Requirement | Priority |
|---|---|---|
| FR-048 | The system SHALL delete the full application record and all records dependent on it automatically WHEN the retention period for its outcome has elapsed — six years from final payment date for a paid grant, twelve months from decision date for a rejected application, six months from last contact for a withdrawn or incomplete application — SO THAT personal data is not kept longer than Revitalise's published schedule allows. | High |
| FR-049 | The system SHALL delete or purge every linked copy held outside the system of record, including the signed acceptance document and the signature envelope, WHEN the parent record is deleted, SO THAT no copy of a deleted record survives. | High |
| FR-050 | The system SHALL retain the financial record required by the charity's finance policy WHEN the associated personal record is otherwise deleted, SO THAT the Charities Act 2011 financial-record duty is met. | High |
| FR-051 | The system SHALL locate and delete, on demand, all data held about a named individual — including any referee, helper, group member or emergency contact captured with their application — WHEN an erasure request is received and no legal hold applies, SO THAT the right to erasure under UK GDPR Article 17 can be honoured. | High |
| FR-052 | The system SHALL report to the requester which data cannot yet be deleted and why WHEN a legal-hold carve-out applies to an erasure request, SO THAT the response matches the published Privacy Notice. | High |
| FR-053 | The system SHALL produce a complete extract of the data held about a named individual WHEN a subject access request is received, SO THAT the charity can answer the request within the statutory period. | High |
| FR-054 | The system SHALL log every retention deletion run and every erasure action with the record reference, data type, date and rule applied, and SHALL hold no personal data in that log, SO THAT the charity can evidence compliance without creating a further copy of personal data. | High |
| FR-055 | The system SHALL retain irreversibly anonymised statistical records that carry no identifiers and cannot be linked back to a person indefinitely, SO THAT outcome reporting survives deletion of the underlying personal data. | Medium |

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-001 | Special-category fields (health and disability condition profiles, "other condition" free-text, benefit status, ethnic group where captured) SHALL be readable only by the administrator role and the service identity. | Security |
| NFR-002 | Bank account and payment data SHALL be readable only by the finance role; the administrator role SHALL have no access to it (separation of duties). | Security |
| NFR-003 | Applicant, helper and support-recipient identifying attributes SHALL never be delivered to a trustee-facing view — the control SHALL be enforced by the platform, not by manual preparation. | Security |
| NFR-004 | Multi-factor authentication SHALL be enforced for every staff, trustee and service-identity sign-in. | Security |
| NFR-005 | Access to each environment SHALL be gated by membership of a named security group before any role permission applies. | Security |
| NFR-006 | Every connection to an external system SHALL be owned by a non-personal service identity, so access survives staff changes and is governed centrally. | Security |
| NFR-007 | Only the approved connector set SHALL be permitted; all other connectors SHALL be blocked in both the development and production environments. | Security |
| NFR-008 | The application-intake endpoint SHALL accept submissions only from the authenticated charity website. | Security |
| NFR-009 | 100% of processing, storage and backup SHALL remain in the UK region across every component, including the redaction service, signature service and finance system. Zero transfers outside the UK. Verified at environment setup. | Compliance |
| NFR-010 | Retention SHALL be enforced automatically by status and trigger date (6 years / 12 months / 6 months per FR-048), with the enforcement run occurring at least monthly; irreversibly anonymised statistics are retained indefinitely. No deletion SHALL depend on a person remembering to act. | Compliance |
| NFR-011 | The backup and point-in-time restore window SHALL sit within the retention period of the records it covers, and all backups SHALL remain in the UK region, so a deleted record cannot survive indefinitely inside a backup. | Compliance |
| NFR-012 | No personal data SHALL be written to operational logs; operational logging is limited to run status, error message and record reference. | Compliance |
| NFR-013 | Only the fields needed to assess, decide, pay and report on a grant SHALL be collected (data minimisation, UK GDPR Article 5(1)(c)). | Compliance |
| NFR-014 | Every create, update and delete on a record holding personal data SHALL be recorded with timestamp (UTC), actor, action, affected record identifier, and before/after values. | Audit |
| NFR-015 | Access to the trustee review view SHALL be logged, recording which user opened it and when. | Audit |
| NFR-016 | The retention and erasure evidence log SHALL be retained as a durable record and SHALL contain no personal data. | Audit |
| NFR-017 | Automated redaction with a confidence below 85% SHALL be routed to human review; the threshold SHALL be adjustable after launch without redesign. | Compliance |
| NFR-018 | 100% of Borderline scoring outcomes and 100% of low-confidence redactions SHALL receive human review before they progress or are disclosed. | Compliance |
| NFR-019 | The process owner SHALL be able to change scoring thresholds, the income ceiling, the redaction confidence threshold, document templates and field mappings without developer involvement and without changing automation logic. | Maintainability |
| NFR-020 | Applicant-facing guidance, labels and error messages SHALL be written for a reading age of approximately 12. | Usability |
| NFR-021 | The solution SHALL support approximately 200 applications per year with headroom to at least 250 per year, and a cumulative grant history of at least 300 records, without redesign. | Scalability |
| NFR-022 | **Performance / response-time thresholds — NOT SPECIFIED in any source document.** No page-load, flow-completion or intake-latency target is stated. See OQ-020. | Performance |
| NFR-023 | **Availability / uptime target — NOT SPECIFIED in any source document.** See OQ-021. | Availability |
| NFR-024 | **Accessibility standard — NOT NAMED in any source document.** No WCAG level or equivalent is committed to, despite an applicant population of disabled people and unpaid carers with low average literacy. See OQ-022. | Accessibility |
| NFR-025 | **Subject access and erasure response-time target — NOT SPECIFIED as an internal SLA.** The capability is designed (FR-051 to FR-053) but no turnaround commitment is recorded. See OQ-023. | Compliance |

> NFR-022 to NFR-025 are recorded as explicit gaps rather than invented thresholds. They must be
> answered before the test-agent can write verifiable test cases for those categories.

---

## 6. User Stories

### US-001: Submit a complete application first time
**As an** applicant (or a helper acting for one), **I want** the form to tell me what is missing as I
go, **so that** I can submit a complete application without a chain of follow-up emails.

**Acceptance Criteria:**
- Given a mandatory field is empty, when I try to submit, then submission is blocked and the field is identified. → FR-001
- Given I have left a mandatory field empty, when the message appears, then it is written in plain English and explains why the answer is needed. → FR-002
- Given I have not selected an income band, when I view the form, then the financial detail questions are not shown. → FR-003
- Given I am partway through, when I look at the form, then I can see how much of it remains. → FR-004
- Given I have answered every question, when I reach the end, then I see a summary of my answers and can edit any section before submitting. → FR-006

### US-002: Pause and come back
**As an** applicant who needs help from someone else to finish, **I want** to save my progress,
**so that** I do not have to start again.

**Acceptance Criteria:**
- Given I have partly completed the form, when I choose to save and continue later, then my answers are preserved and I can resume them. → FR-005
- Given I have resumed a saved application, when I complete it, then I see the same pre-submission summary and edit option as a single-sitting applicant. → FR-006

### US-003: Accept a grant without a printer
**As a** successful applicant, **I want** to sign my acceptance electronically, **so that** my grant
is confirmed quickly and I am not held up by post.

**Acceptance Criteria:**
- Given my application has been approved, when the decision is finalised, then I receive an acceptance document already filled in with my name, amount, provider and dates. → FR-041
- Given I have signed, when my signature is recorded, then the document is routed to my referee or GP for the second signature. → FR-042
- Given I have not signed, when three days and then seven days have passed, then I receive a reminder. → FR-043
- Given both signatures are complete, when the last one is received, then my grant record shows "Acceptance Signed" and the signed document is attached to it. → FR-045
- Given I cannot sign electronically, when I ask for a paper route, then a print-sign-scan acceptance can be recorded against my grant. → FR-046

### US-004: Know what is held about me and have it removed
**As an** applicant, **I want** to ask what data Revitalise holds about me and to have it deleted,
**so that** I stay in control of my personal and health information.

**Acceptance Criteria:**
- Given I make a subject access request, when the process owner actions it, then a complete extract of the data held about me can be produced. → FR-053
- Given I request erasure and no legal hold applies, when the request is actioned, then my data is deleted from the system of record and from every linked copy. → FR-051, FR-049
- Given part of my data is held under the six-year financial-record duty, when I request erasure, then I am told which data cannot yet be deleted and why. → FR-052, FR-050
- Given my record reaches the end of its retention period, when the retention run executes, then it is deleted without anyone requesting it. → FR-048

### US-005: Applications arrive by themselves
**As** Emily, the process owner, **I want** submissions to become records automatically,
**so that** I stop exporting spreadsheets and applications stop waiting in a queue.

**Acceptance Criteria:**
- Given an applicant submits the form, when the submission is received, then an application record exists without any manual step. → FR-007
- Given a new record is created, when I look at it, then it carries a unique `REV-YYYY-NNN` reference and its submission timestamp. → FR-008
- Given a new record is created, when it lands, then I receive a Teams notification with the applicant name and reference. → FR-009
- Given a submission fails to create a record, when the failure occurs, then it is recorded and I am alerted. → FR-010

### US-006: The score is calculated, but the judgement stays mine
**As** Emily, **I want** the circumstance score and status calculated automatically against criteria
I control, **so that** I only spend time on the cases that need a human.

**Acceptance Criteria:**
- Given a new application record, when it is created, then a circumstance score out of 60 is calculated from the wellbeing answers. → FR-011
- Given the applicant reported a low feeling score, when the score is calculated, then that answer contributes more points, not fewer. → FR-012
- Given a Likert answer of "Strongly Disagree", when the score is calculated, then it contributes the configured maximum points for that question. → FR-013 ⚠️ *Incomplete — "Strongly Disagree" is the position-1 answer on only three of the ten questions. Replacement criterion proposed in Amendment A-01.*
- Given the score is calculated, when it is compared to the threshold, then the application is flagged Auto-pass, Borderline or Auto-reject. → FR-014
- Given the applicant's finances exceed the income ceiling, when the application is scored, then a separate income eligibility flag is set. → FR-015
- Given an application contains health-condition data and a free-text narrative, when the score is calculated, then neither influences the score. → FR-016
- Given the board changes the cut-off, when I update the threshold, then the change takes effect without a developer editing anything. → FR-017
- Given I disagree with an automated status, when I override it, then the new status applies and the override is recorded. → FR-018
- Given an application is Borderline, when it is flagged, then it waits for my review before progressing. → FR-019
- Given applications were auto-rejected, when I open my active list, then they are not in it. → FR-020
- Given a day's applications have been scored, when the daily summary arrives, then it states how many were scored, auto-rejected and are awaiting my review. → FR-021
- Given a scored answer is missing, when the application is processed, then no final automated outcome is set and the case comes to me. → FR-022

### US-007: I stop anonymising by hand, but I keep the last word
**As** Emily, **I want** narratives redacted automatically with anything uncertain flagged to me,
**so that** I save three to four hours per board cycle without risking a missed name reaching a trustee.

**Acceptance Criteria:**
- Given an application becomes eligible for trustee review, when redaction runs, then personal identifiers in the free-text narrative are replaced with category labels. → FR-026
- Given a narrative mentions a specific age or place, when redaction runs, then they are generalised to an age band and a region. → FR-027
- Given redaction has run, when a trustee reads the case, then region, dates, score, holiday preferences and general condition information are still present. → FR-028
- Given redaction confidence is below the configured threshold, when the narrative is processed, then it is flagged to me and withheld from trustees. → FR-029
- Given a narrative is flagged, when I review and release it, then trustees can see it. → FR-030
- Given I need the original text, when I open the record, then I can read the unredacted narrative and no one outside the administrator role can. → FR-031
- Given the board meeting is approaching, when the schedule fires or I trigger it, then pack preparation runs. → FR-033

### US-008: Enact the board's decisions in one step
**As** Emily, **I want** to turn the meeting's verdicts into actions with one confirmation,
**so that** I stop collating decisions from emails and re-keying them.

**Acceptance Criteria:**
- Given trustees recorded verdicts during the meeting, when I confirm "Finalise decisions", then the verdicts are applied to the grant records. → FR-037, FR-040
- Given approved applications exist, when I finalise decisions, then acceptance documents are issued for them. → FR-040, FR-041
- Given fifteen grants were approved at one meeting, when I finalise decisions, then all fifteen are issued in the same run. → FR-047

### US-009: Chasing signatures is not my job
**As** Emily, **I want** reminders and escalation handled automatically, **so that** acceptances stop
sitting unsigned for weeks.

**Acceptance Criteria:**
- Given an acceptance is unsigned, when three and seven days pass, then reminders are sent without my involvement. → FR-043
- Given an acceptance is still unsigned after fourteen days, when the escalation triggers, then I am notified with the applicant's details. → FR-044
- Given both signatures arrive, when they complete, then the status and the signed document are filed automatically. → FR-045

### US-010: Catch a repeat grant before it is paid
**As** Emily, **I want** prior grants flagged automatically, **so that** duplicate awards are caught
as volumes grow beyond what I can remember.

**Acceptance Criteria:**
- Given a new application, when it is created, then it is checked against historical grant payments. → FR-023
- Given a prior grant is found, when the check completes, then the application is flagged as a possible duplicate with the prior grant's reference, date and amount. → FR-024
- Given no prior grant is found, when the check completes, then "no prior grants found" is recorded on the application. → FR-025

### US-011: Retention happens without me
**As** Emily, **I want** records deleted on schedule automatically, **so that** the charity's retention
promise does not depend on me remembering.

**Acceptance Criteria:**
- Given a rejected application reaches twelve months from its decision date, when the retention run executes, then the full record is deleted. → FR-048
- Given a grant record is deleted, when deletion completes, then the signed document and signature envelope copies are also removed. → FR-049
- Given a record is deleted, when the run completes, then the deletion is logged with the record reference, data type, date and rule, and the log holds no personal data. → FR-054
- Given anonymised statistics exist, when personal records are deleted, then the statistics remain available for reporting. → FR-055

### US-012: Review real cases without learning who they are
**As a** trustee, **I want** to read the anonymised case and record my verdict in one place,
**so that** I can decide properly without a static Word pack and without seeing personal identities.

**Acceptance Criteria:**
- Given I open the review view, when it loads, then I see the applications under review with score, region, dates and status, and can sort and filter them. → FR-034
- Given I select an application, when the detail opens, then I see the redacted narrative, score breakdown, holiday details and staff recommendation. → FR-035
- Given I am a trustee, when any view loads, then no applicant, helper or support-recipient identifying information is present anywhere in it. → FR-036, FR-031
- Given I have read a case, when I decide, then I can record Approve, Defer or Reject with optional notes. → FR-037
- Given applications outside the current round exist, when I open the review view, then they are not available to me. → FR-038

### US-013: A stripped, data-only view
**As** Kevin, a trustee who works from the numbers, **I want** scores, region, dates and status only,
**so that** I can compare cases at a glance without reading narratives.

**Acceptance Criteria:**
- Given I prefer a data-only view, when I open the summary list, then I can review score, region, dates and status without opening a narrative. → FR-034
- Given I am working from the summary list, when I sort or filter it, then the ordering and filtering apply to all applications under review. → FR-034
- Given I use only the summary view, when I reach a decision, then I can record my verdict from there. → FR-037
- Given I want a copy to work from offline, when I export, then I get the same stripped content with no identifying information. → FR-039, FR-036

### US-014: An offline fallback so no trustee is excluded
**As a** trustee who cannot or will not use the portal, **I want** an anonymised document pack,
**so that** I can still take part in the decision.

**Acceptance Criteria:**
- Given pack preparation has run, when I request the fallback, then I receive a per-application anonymised document with the redacted narrative, score breakdown, holiday details and staff recommendation. → FR-032
- Given I have the document pack, when I read it, then it contains no applicant identifying information. → FR-032, FR-027
- Given I prefer to print from the portal, when I use the print option, then the same anonymised content is produced. → FR-039

### US-015: Finance sees payments, and nothing it does not need
**As** finance staff recording disbursements, **I want** access limited to bank and payment data,
**so that** I can do my job without handling applicants' health information.

**Acceptance Criteria:**
- Given I hold the finance role, when I open the solution, then I can reach bank account and payment records. → NFR-002
- Given I hold the finance role, when I open any application record, then the applicant's unredacted health narrative is not readable by me. → FR-031, NFR-001
- Given an application was flagged as a possible duplicate, when I prepare a disbursement, then the flag and the prior grant details are visible on the record. → FR-024
- Given a grant record reaches the end of its retention period, when deletion runs, then the financial record required by the finance policy is retained. → FR-050

---

## 7. Compliance & Regulatory Considerations

### 7.0 Status of the underlying compliance artefacts — read this first

| Artefact | Version | Status | Consequence |
|---|---|---|---|
| Data Protection Impact Assessment | v0.1, 15 Jul 2026 | **Concept draft — for DPO review. NOT signed off.** Outcome and residual-risk acceptance left open; the sign-off table (DPO, controller, processor) is empty. | UK GDPR Art. 35 requires the DPIA to be completed before go-live. Its five closing actions (A1–A5) are unclosed. |
| Record of Processing Activities | v0.1, 15 Jul 2026 | **Concept draft — for DPO review. NOT signed off.** | The Art. 30 register is not yet the charity's own record; content must be transferred into Revitalise's RoPA template and confirmed. |
| Data Governance Framework | v0.2, 15 Jul 2026 | Draft | Retention and erasure policy is written but awaits the same DPO confirmations. |
| Security Model | v0.1, 15 Jul 2026 | Draft — "DPO sign-off is the gate on this model" | The trustee field-level-security control is explicitly gated on DPO sign-off. |
| Privacy Notice | updated 20 Feb 2026 | Published (Revitalise's own) | Source of the lawful bases and retention periods used throughout. |

Revitalise is the **data controller**. Argelis Consultancy is the **processor** and builder, acting
on Revitalise's instruction. AI Builder (redaction), DocuSign (signing) and QuickBooks Online
(financial record) act as sub-processors, all within the UK. The named service identity
`svc-grantautomation` owns the external connections; it is not a personal login.

### 7.1 Data classification (satisfies C-DOM-001 at plan level)

| Tier | Examples in this solution | Data subjects | Handling |
|---|---|---|---|
| **Special category (UK GDPR Art. 9)** | Applicant and support-recipient condition profiles; "other condition" free-text; health/disability free-text in the narrative; benefit status; ethnic group where captured | Applicants; cared-for / support-recipients | Highest restriction. Administrator role and service identity only. Never shown to trustees. Free-text redacted before trustee review. |
| **Personal (UK GDPR Art. 6)** | Name, address, postcode, email, phone, date of birth, bank details; helper, referee, group-member and emergency-contact identity | Applicants; helpers; referees; group members; emergency contacts | Restricted. Identity attributes hidden from trustees; bank details behind the finance role only. |
| **Pseudonymised** | Pseudonymised reference (e.g. `REV-A-00001`), age range, location area, costs, scores, redacted narrative | Applicants | Still personal data. Visible to trustees. Follows the parent record's retention clock. |
| **Anonymised** | Snapshot statistics: age range, location area, condition areas, outcome, amount — no identifiers, never linked back | None | Not personal data. May be kept indefinitely. |
| **Operational (non-personal)** | Flow error log, run history — run status, error messages, record references only | None | No personal data. Short operational retention, separate from the personal-data schedule. |

Trustees and finance/admin staff are themselves data subjects: tenant account identity, the verdict
a trustee records, and the audit trail of staff actions.

### 7.2 Lawful basis per data grouping (satisfies C-DOM-002)

The lawful bases are **Revitalise's own**, taken from its Privacy Notice (20 Feb 2026). This SDD
records them; it does not set them.

| Data grouping / entity | Personal data — Art. 6 basis | Special category — Art. 9 condition | Notes |
|---|---|---|---|
| Applicant (identity, contact, DOB) | Art. 6 — necessary to assess and administer the grant | n/a | Per Privacy Notice |
| Application (wellbeing and financial answers, circumstance score, narrative) | Art. 6 — necessary to assess and administer the grant | Art. 9(2)(b) social protection; Art. 9(2)(h) health and social care | Health free-text and disability data are processed to assess eligibility and need only; they do not feed the automated score |
| Support-recipient / cared-for person (identity where given, condition profile) | Art. 6 — necessary to assess the grant | Art. 9(2)(b) and 9(2)(h) | Condition profile visible to trustees; identity is not |
| Helper acting for an applicant (name, email, phone) | Art. 6 — necessary to administer the application | n/a | No special-category data |
| Referees, group members, emergency contacts | Art. 6 — necessary to administer and verify the application | n/a | In scope of erasure requests (FR-051) |
| Review (trustee verdict, notes, trustee identity) | Art. 6 — necessary to decide which grants to fund | n/a | Trustee identity is staff/officer processing |
| Grant (award, provider, dates, conditions, signed acceptance) | Art. 6 — necessary to administer and evidence the grant; retention under the Charities Act 2011 duty | n/a | Signed PDF retained with the record |
| Bank Account, Payment | Art. 6 — necessary to pay the grant and meet financial-record duties | n/a | Finance role only; administrator role has no access |
| Provider | **Not classified in any source document** | — | See OQ-026. Likely organisation data with named contacts; classification and basis must be settled at TAD stage |
| Anonymised Statistic snapshot | Not personal data — outside Art. 6 | n/a | No identifiers, not linkable |
| Error Log (operational) | Not personal data — outside Art. 6 | n/a | Run status, error message, record reference only |

### 7.3 UK GDPR obligations and how the design addresses them

| Article | Obligation | Position in this design |
|---|---|---|
| **Art. 5(1)(a)** lawfulness, fairness, transparency | Processing must be fair and explained | Applicants informed via the Privacy Notice (20 Feb 2026); no separate consultation planned |
| **Art. 5(1)(b)** purpose limitation | Use only for stated purposes | Data used only to assess, decide, pay and report; anonymised statistics carry no identifiers and cannot be linked back |
| **Art. 5(1)(c)** data minimisation | Collect only what is necessary | Only fields needed to assess and pay a grant are collected (NFR-013). Health free-text and disability data do not feed the automated score (FR-016) |
| **Art. 5(1)(e)** storage limitation | Keep no longer than necessary | Automated retention by status and trigger date (FR-048, NFR-010). ⚠️ Six-year retention of the health free-text is the open DPO decision OQ-006 |
| **Art. 5(1)(f)** integrity and confidentiality | Appropriate security | Least privilege, field-level restriction of identity columns, separation of duties on bank data, UK residency, connector restriction (NFR-001 to NFR-009) |
| **Art. 5(2)** accountability | Demonstrate compliance | Native field-change auditing of every create/update/delete (NFR-014); app-access logging (NFR-015); retention/erasure evidence log (FR-054, NFR-016) |
| **Art. 6** lawful basis | Documented per entity | §7.2 above |
| **Art. 9** special-category condition | Art. 9 condition required | Art. 9(2)(b) social protection and Art. 9(2)(h) health and social care, per the Privacy Notice |
| **Art. 15** right of access | SAR fulfilment | Complete extract producible for a named individual (FR-053). ⚠️ No internal response-time SLA recorded — OQ-023 |
| **Art. 17** right to erasure | Erasure path with carve-outs | On-demand erasure across the system of record and every linked copy including referees, helpers, group members and emergency contacts (FR-051); legal-hold carve-out disclosed to the requester (FR-052) |
| **Art. 30** records of processing | Art. 30(1) controller record and Art. 30(2) processor record | Both drafted in the RoPA v0.1 — **concept status, not confirmed**; published DPO contact details still outstanding (OQ-009) |
| **Art. 32** security of processing | Technical and organisational measures | Least privilege; field-level column restriction; separation of duties; MFA and Conditional Access; UK residency; connector policy; native auditing; automated retention and deletion |
| **Art. 35** DPIA | Required for high-risk processing | DPIA exists at v0.1 concept status. It is required here because the solution processes special-category health data about people in vulnerable circumstances, at scale, and uses automated processing to screen applications |

### 7.4 Data (Use and Access) Act 2025 — automated decision-making

The DUAA 2025 has been in force since 5 February 2026 and bears directly on this design.

The scoring flow calculates the circumstance score from the wellbeing answers, applies the knockout
threshold and income ceiling the process owner controls, and sets the status to auto-pass,
borderline or auto-reject. Disability data, health-condition data and the free-text narrative do
**not** feed the score. Emily does not re-score by hand; she reviews the borderline cases the flow
flags, can adjust the threshold, and can override any outcome. Trustees make the funding decision on
eligible applications.

**The open question is whether automatic rejection at the threshold, with that oversight and
override, meets Revitalise's automated-decision position under the DUAA 2025.** This is a DPO
decision (OQ-005). If a stronger form of human review is required before any rejection stands, the
design can route auto-reject outcomes through the process owner instead of closing them
automatically — a configuration change within the current design, not a rebuild. This SDD's
FR-014, FR-018, FR-019 and FR-022 are written so that either position can be adopted without
changing the requirement set.

### 7.5 Charities Act 2011 — retention duty

The six-year retention period on successful grants, including the health free-text, follows the
**Charities Act 2011 financial-record duty** as stated in Revitalise's Privacy Notice. This creates
a direct tension with Article 5(1)(c) minimisation, because the health free-text is retained for the
full six years alongside the financial record. The design allows the special-category free-text to
be redacted earlier if the DPO prefers tighter minimisation — a configuration change, not a rebuild.
That choice is DPO decision OQ-006. The financial record itself is retained under the finance policy
even where the personal record is otherwise deleted (FR-050), and erasure requests are answered with
an explicit statement of what is held under legal hold (FR-052).

### 7.6 Retention schedule (as adopted)

| Data / outcome | Trigger | Retention | Then |
|---|---|---|---|
| Successful grant — full record including health free-text | Status = Grant Paid, from final payment date | 6 years | Delete full record |
| Unsuccessful application | Status = Rejected, from decision date | 12 months | Delete full record |
| Withdrawn / incomplete | Status = Withdrawn / Incomplete, from last contact | 6 months | Delete full record |
| Monitoring & evaluation (pseudonymised) | Follows parent grant record | Same as record | Delete with record |
| Signed acceptance PDF | Attached to grant record | 6 years (with record) | Delete with record |
| Financial record (name, amount, date) | Status = Grant Paid | 6 years | Per finance policy |
| Irreversibly anonymised statistics | No identifiers; not linkable | Indefinite | Retain |
| Operational error log (non-personal) | Run completion | Short operational retention | Delete |

### 7.7 Risks to individuals (adopted from DPIA §6–§7)

| # | Risk to individuals | Inherent | Residual after designed controls |
|---|---|---|---|
| R1 | A trustee identifies an applicant from data that should be redacted (field-level security gap or incomplete redaction) | High | Low |
| R2 | Special-category health data exposed to someone without a need to see it (role misconfiguration) | High | Low |
| R3 | An applicant is wrongly rejected by the automated score without meaningful human review | High | **Medium — pending DPO confirmation (OQ-005)** |
| R4 | Health free-text kept longer than necessary on granted records (6-year retention) | Medium | **Medium — DPO decision open (OQ-006)** |
| R5 | Bank or payment details accessed by someone outside the finance role | Medium | Low |
| R6 | Data processed or stored outside the UK, breaching the residency commitment | Medium | Low |
| R7 | An erasure request is not honoured across every system holding a copy | Medium | Low |
| R8 | The service account is compromised, exposing the whole dataset through its broad access | Medium | Low |
| R9 | A leaver keeps access after their role ends | Medium | Low |

**Two risks remain at Medium and both are waiting on the DPO, not on the build.** R3 and R4 are the
gate-relevant compliance risks for this feature.

### 7.8 The three open DPO decisions — gate-relevant

These are DPIA §9 actions A1–A3, repeated identically in the Security Model §9, the Data Governance
Framework §8 and the RoPA §9. All four documents state that build must not proceed on the current
basis until they are recorded.

| Decision | What is being asked | Effect if answered differently |
|---|---|---|
| **A1 / OQ-004** | Confirm that field-level (column) security is an acceptable trustee control **in place of** the manual, single-key-holder anonymisation the documented process currently mandates | The automated control is stronger but *different*. If physical separation is required instead, the fallback is a separate trustee-facing store populated only with permitted fields and kept in sync — more to maintain, and a change the architect must design |
| **A2 / OQ-005** | Confirm that automatic rejection at the threshold, with the process owner's oversight and override, satisfies Revitalise's automated-decision position under the DUAA 2025 | If stronger human review is required, auto-reject outcomes route through the process owner rather than closing automatically — a configuration change, but it changes the process and the test set |
| **A3 / OQ-006** | Confirm that six-year retention of the health free-text on granted records is preferred over earlier minimisation | If earlier minimisation is preferred, the free-text is redacted before the six-year point — a configuration change, but it changes the retention requirement and its verification |

Two further DPIA closing actions are open: **A4** — confirm expected application volume and the
role-review cadence (process owner; OQ-007, OQ-008); and **A5** — verify UK residency and backup
arrangements at environment setup (builder / Wanstor; OQ-018, OQ-019).

### 7.9 Universal controls checklist (`skills/compliance-checklist.md` §1)

| Control | Status at plan stage |
|---|---|
| 1.1 Personal data identified and classified | ✅ §7.1 — four tiers plus operational; Provider entity unclassified (OQ-026) |
| 1.1 Lawful basis documented | ✅ §7.2 per entity |
| 1.1 Data minimisation | ✅ NFR-013, FR-016 |
| 1.1 Retention defined per entity; automated deletion | ✅ §7.6, FR-048, NFR-010. ⚠️ health free-text period is OQ-006 |
| 1.1 Personal data not written to logs | ✅ NFR-012 |
| 1.1 Encryption in transit / at rest | ➡️ Architecture-level; to be evidenced in the TAD |
| 1.1 SAR path exists | ✅ FR-053. ⚠️ no response-time SLA (OQ-023) |
| 1.1 Right-to-erasure path exists | ✅ FR-051, FR-052 |
| 1.1 Privacy impact assessed | ⚠️ DPIA exists at **concept draft** status — not signed off |
| 1.2 CRUD on sensitive entities logged | ✅ NFR-014 |
| 1.2 Log record content (timestamp, actor, action, entity, before/after) | ✅ NFR-014 |
| 1.2 Tamper-evident / append-only audit log | ➡️ Architecture-level (C-DOM-012, architect scope) |
| 1.2 Audit retention meets the longer of regulation or policy | ➡️ Architecture-level (C-DOM-013, architect scope) |
| 1.3 Least privilege | ✅ NFR-001 to NFR-003; three roles only |
| 1.3 Role assignments documented and reviewed | ⚠️ Documented; review cadence is **TBC** (OQ-008) |
| 1.3 Privileged actions require elevated authorisation | ➡️ Architecture-level (C-DOM-021, architect scope) |
| 1.3 MFA for privileged access | ✅ NFR-004; scoped Conditional Access exception for the service identity |
| 1.3 Session timeout | ➡️ Architecture-level; not stated in any source |
| 1.4 Change management via pipeline | ➡️ ALM Runbook (out of scope for this SDD) |
| 1.5 Dependency and supply chain | ➡️ Architecture / build stage |

> `knowledge/domain/compliance-requirements.md` is an unpopulated template in this repository, so no
> project-specific domain controls could be applied on top of the universal set. The compliance
> content above is drawn entirely from the source documents. See Adoption Report open items.

---

## 8. Assumptions & Dependencies

### Licensing and platform

1. Revitalise has, or will procure, an M365 Business Premium subscription.
2. Because the agreed data model is Dataverse (a premium data source), every person who uses an app
   over the custom tables needs a per-user premium entitlement: the maker/service account, plus a
   seat for Emily. Trustees are billed pay-as-you-go per active user per round.
3. The service account additionally needs a premium automation entitlement for the standalone
   scheduled and webhook automations (website intake, DocuSign, QuickBooks, retention helper) that
   run outside the app context.
4. Power BI Pro is **not** required — the trustee portal is a Dataverse app, not a Power BI report.
5. Automated redaction credits are expected to be covered by the credits bundled with each premium
   seat, **to be confirmed** — and confirmed before the 1 November 2026 seeded-credit change.
6. Recurring licence cost is roughly £750–1,000/year at list pricing, or about £370–500/year at
   nonprofit pricing. All licences are Revitalise's; none are carried by Argelis. Nonprofit
   eligibility (via TechSoup or a Microsoft partner) and the current M365 tier are to be confirmed
   before build. Figures were verified against Microsoft sources on 14 July 2026 and should be
   re-verified before procurement.
7. DocuSign is procured separately by Revitalise (from ~£8/user/month; standard plan sufficient)
   and must be in place before the acceptance workflow goes live.
8. Standard connectors (SharePoint, Outlook, Teams, HTTP, DocuSign, QuickBooks Online) carry no
   additional cost.

### External systems and third parties

9. The website form plugin exposes a webhook, a REST API, or structured email. Gravity Forms — the
   likely plugin — provides a REST API v2 and a Webhooks add-on, so no migration is needed. **If a
   different plugin without any of these is in use, migration adds 4–8 hours.**
10. Alex (website designer) is available to build the form to the supplied field-by-field
    specification and to implement the intake integration. Emily is to arrange the introduction.
11. The existing Canva acceptance form is available as the template to replicate.
12. QuickBooks Online is the edition in use and grant payments carry a searchable applicant
    identifier. Not yet confirmed — the design leads with the lower-effort cross-reference fallback
    for exactly this reason.
13. **WBS 0.3 — the service account and its scoped Conditional Access exception — is outstanding and
    currently waiting on Wanstor, Revitalise's IT provider.** This is the one dependency that is
    already late and it blocks the automations that run unattended. Wanstor has no access to grant
    data by design.

### Governance and people

14. **DPO sign-off on the three decisions in §7.8 is a precondition for build on the current design
    basis.** All four governance documents state this independently.
15. The DPIA and RoPA must be completed and signed by Revitalise as controller; Argelis's drafts are
    a processor's proposal, not the charity's record.
16. Emily is confirmed as process owner and the named DPO is current — to be confirmed before
    sign-off. A second processor (Jan) is under consideration and not yet assigned; a second staff
    seat would be needed if he also processes applications.
17. The scoring methodology and the anonymisation rules are confirmed by Emily before build begins.
18. The board decides the cut-off score and income ceiling. The design is configurable, so these can
    be set later without rework.
19. **Trustee adoption is a change-management risk, not a technical one.** Some trustees may resist
    moving from email attachments to a portal; the source expects at least one round of trustee
    feedback after the initial demo, and reconciling different trustees' expectations takes time.
    The offline document fallback (FR-032, FR-039) exists so that no trustee is excluded if adoption
    is partial.
20. Build effort assumes an **experienced Power Platform consultant**. A developer new to the
    platform should add 25–30%.
21. Build effort includes requirements clarification with Emily, build, client walkthrough, feedback
    processing, rework, and testing with real application data.
22. Annual savings projections assume ~200 grants/year. The current run rate (68 grants in ~4 months)
    suggests this is conservative.

### Companion artefacts already produced (context, not adopted into this SDD)

23. `docs/Import/Revitalise-Solution-Architecture-v0.4.docx` — feeds the architect-agent intake that
    runs after this SDD is approved.
24. `docs/Import/Revitalise-ALM-Runbook-v0.1.docx` — release and promotion procedure.
25. `docs/Import/Revitalise-Governance-Runbook-v0.1.docx` — role handover, review cadence,
    joiner-and-leaver procedure, operational failure monitoring.
26. `docs/Import/Revitalise-Security-Model-v0.1.docx` (WBS 0.5), `Revitalise-Data-Governance-Framework-v0.2.docx`,
    `Revitalise-DPIA-v0.1.docx` and `Revitalise-RoPA-v0.1.docx` (WBS 0.7) — the compliance set §7 draws on.
27. `Revitalise-WBS-Grant-Automation-v0.4.xlsx` — task-level breakdown with low/high hour estimates,
    dependencies and phasing. Referenced by the source but **not present in `docs/Import/`**; it is
    the basis of the §10 estimate and should be supplied.
28. `Grant Application Data Model v0.2` and Revitalise's Privacy Notice (20 February 2026) are
    referenced throughout the compliance set but are not in the repository.

---

## 9. Open Questions

Thirty open items were carried out of the source set. The volume is itself a signal: this design is
well documented but not yet decided, and six of these items sit with people outside the delivery
team.

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-001 | Where should the knockout cut-off score sit, and how wide is the borderline band Emily reviews by hand? | Board / Emily | Before Automation #2 build |
| | ⚠️ **STILL OPEN.** Amendment A-01 does **not** resolve this, despite being commissioned as though it would — `Book(Sheet1).csv` holds scores and answers but no accept/reject outcomes, so no cut-off can be inferred from it. This is a board decision. **What did change:** the reachable floor of a fully answered application dropped from **10 to 5** (see A-01), so thresholds at or below 5 are now reachable where they were not. | | |
| OQ-002 | Confirm the exact scoring methodology: the feeling-scale inversion, the Likert point mapping, and the required behaviour when a scored answer is missing (see FR-022) | Emily | Before Automation #2 build |
| | ✅ **RESOLVED BY EVIDENCE — see Amendment A-01 (PROPOSED)** at the top of this document. 25 real hand-scored applications reproduce exactly under the recorded methodology, asserted permanently in `src/tests/solutions/ScoringInvariants.Tests.ps1`. Two corrections came with it: the ten wellbeing questions use **two** response scales, not one, and **"Not sure"** is a valid answer worth 0.5 points. Formal closure awaits plan-agent re-issue of FR-013. | | |
| OQ-003 | What is the income ceiling value, and does an income-only failure reject outright or flag for review? | Board / Emily | Before Automation #2 build |
| OQ-004 | **DPO decision (DPIA A1):** is field-level column security an acceptable trustee control in place of the manual, single-key-holder anonymisation? | DPO | **Before build starts** |
| OQ-005 | **DPO decision (DPIA A2):** does automatic rejection at the threshold, with oversight and override, satisfy Revitalise's automated-decision position under the DUAA 2025? | DPO | **Before build starts** |
| OQ-006 | **DPO decision (DPIA A3):** is six-year retention of the health free-text preferred over earlier minimisation? | DPO | **Before build starts** |
| OQ-007 | Confirm the expected number of applications per round and per year, so the scale of processing is on record (DPIA §2.2 TBC) | Emily | Before DPIA sign-off |
| OQ-008 | Confirm the role-membership review cadence — quarterly, or at the start of each panel round? | Emily / DPO | Before DPIA sign-off |
| OQ-009 | Confirm the published DPO contact details for the RoPA | Revitalise | Before RoPA finalisation |
| OQ-010 | Confirm the named DPO is current, that Emily is the accepted process owner, and whether a second processor (Jan) is assigned | Revitalise | Before sign-off |
| OQ-011 | Finalise the anonymisation rules: exactly which fields are stripped, which are generalised (age → band, location → region), and what stays | Emily / DPO | Before Automation #5 build |
| OQ-012 | Is the print-and-post route sufficient for applicants who cannot sign digitally, and who records the paper acceptance? | Emily | Before Automation #3 build |
| OQ-013 | Will all trustees move to the portal, or do some need the document pack for the first few cycles? | Emily / trustees | Before Automation #6 build |
| OQ-014 | Confirm the website form plugin (Gravity Forms assumed) and which integration method it exposes — webhook, REST pull, or structured email | Alex / Emily | Before Automation #4 build |
| OQ-015 | Confirm the QuickBooks edition (Online vs Desktop) and whether grant payment records carry a searchable applicant email or name | Revitalise finance | Before Automation #7 build |
| OQ-016 | Do TRIP (legacy) or Donorfy records also need to be checked for prior grants? | Emily | Before Automation #7 build |
| OQ-017 | Confirm redaction credit coverage under the bundled per-seat credits, nonprofit licensing eligibility, and the current M365 tier — before the 1 Nov 2026 seeded-credit change | Revitalise | Before build |
| OQ-018 | **WBS 0.3 — service account and scoped Conditional Access exception, outstanding with Wanstor.** When will it be delivered? | Wanstor | **Blocking; already outstanding** |
| OQ-019 | Does Revitalise run a third-party M365 backup tool, or rely on native platform backup alone? (DPIA A5) | Revitalise / Wanstor | At environment setup |
| OQ-020 | What performance / response-time thresholds apply? None are stated anywhere in the source set (NFR-022) | Emily / architect | Before test design |
| OQ-021 | What availability or uptime target applies, and are there periods (board cycle, application round) where downtime is unacceptable? (NFR-023) | Emily | Before test design |
| OQ-022 | **Which accessibility standard applies?** No standard is named in any source, despite an applicant population of disabled people and unpaid carers with a ~age-12 average reading level. WCAG 2.2 AA would be the conventional answer (NFR-024) | Revitalise / Emily | Before Automation #1 build |
| OQ-023 | What internal turnaround target applies to subject access and erasure requests? (NFR-025) | DPO / Emily | Before go-live |
| OQ-024 | Have trustees agreed to use the portal, and who owns that conversation? | Emily | Before Automation #6 build |
| OQ-025 | Is a second staff premium seat needed for Jan if he also processes applications? | Revitalise | Before procurement |
| OQ-026 | How is the Provider entity classified, and what is its lawful basis? No source document covers it (§7.2) | DPO / architect | At TAD stage |
| OQ-027 | Is ethnic group actually captured? Every source qualifies it as "where captured" — if it is not collected, the Art. 9 surface narrows | Emily / DPO | Before DPIA sign-off |
| OQ-028 | Confirm that no historical data migration beyond the current application round is required | Emily | Before Automation #4 build |
| OQ-029 | The project's own domain knowledge files (`knowledge/domain/overview.md`, `regulations.md`, `glossary.md`, `business-rules.md`) are unpopulated templates. Who populates them, and when? Until then every downstream agent works from the source documents alone | Lead / domain owner | Before architecture |
| OQ-030 | The DPIA outcome and residual-risk acceptance are not recorded and the sign-off table is empty. When will the DPIA be formally concluded? | DPO / Revitalise | **Before go-live (Art. 35)** |

---

## 10. Effort Estimate

**Size:** **L** by build effort (2–4 person-weeks) — **XL** as a delivery programme (four phases
across roughly twelve calendar weeks, seven components, three external integrations).
**Range:** **106–160 build hours** ≈ **14–21 person-days** (at 7.5 h/day) ≈ 2.7–4.0 person-weeks.
**Basis:** the source document's own bottom-up estimate, midpoint 133 hours, detailed at task level
in the accompanying WBS workbook (`Revitalise-WBS-Grant-Automation-v0.4.xlsx`, not present in
`docs/Import/`).

### Per-automation breakdown (source hours → T-shirt size)

| # | Automation | Source hours | Size | Notes |
|---|---|---|---|---|
| 1 | Form validation & completeness | 12–18 | S | Specification written for Alex, who builds; validation by the consultant |
| 2 | Scoring engine | 16–24 | S–M | Arithmetic is trivial; the data model, option sets, views and edge-case testing are not |
| 3 | Acceptance workflow (DocuSign) | 16–22 | S–M | Template replication plus external procurement dependency |
| 4 | Website → system-of-record intake | 10–16 | S | Foundation for #2, #3, #5, #6; build alongside #1 |
| 5 | AI-assisted anonymisation | 30–46 | M | Largest single item; human-in-the-loop step and threshold tuning drive the range |
| 6 | Trustee review portal | 14–20 | S–M | Expect at least one round of trustee feedback after the demo |
| 7 | Duplicate-grant check | 8–14 | S | Cross-reference fallback approach, not full API integration |
| | **Total** | **106–160** | **L** | |

### Phasing (adopted from the source)

| Phase | Automations | Hours | Size | Cumulative annual saving |
|---|---|---|---|---|
| Phase 1 (weeks 1–4) | #1 Form validation, #4 Intake, #2 Scoring | 38–58 | M | ~215 hours/year |
| Phase 2 (weeks 5–6) | #3 Acceptance workflow | 16–22 | S–M | ~255 hours/year |
| Phase 3 (weeks 7–12) | #5 Anonymisation, #6 Trustee portal | 44–66 | M–L | ~320 hours/year |
| Phase 4 (when needed) | #7 Duplicate check | 8–14 | S | ~330 hours/year |

### Assumptions behind the estimate

- Estimates include requirements clarification with Emily, build, client walkthrough, feedback
  processing, rework, and testing with real application data.
- They assume an **experienced Power Platform consultant**. A developer new to the platform adds
  25–30% (→ 133–208 hours).
- They assume the form plugin exposes a webhook, REST API or structured email. Plugin migration adds
  4–8 hours.
- The move to the Dataverse data model is build-cost-neutral to slightly faster, so these hours
  hold; it raises the recurring licence bill, not the build.
- Return: ~330 staff hours/year at ~200 grants/year — roughly 2.5× year-one ROI at the 133-hour
  midpoint, rising to ~410 hours/year (3.1×) at 250 grants/year.

### Estimate risks and uncertainty

⚠️ **The 106–160 hour range covers the seven automations only.** The governance and security
documents describe platform work that sits outside it and is not separately costed here: environment
setup and UK-residency verification (WBS 0.2), the service account and Conditional Access exception
(WBS 0.3), building the Dataverse tables to the data model (WBS 0.4), configuring the three security
roles and the field-level security profile (WBS 0.5), the connector policy, the retention bulk-delete
jobs and the cross-system retention/erasure helper flow (WBS 0.7). The source treats "Phase 0 setup"
as part of #2 and #4. **The architect should confirm whether that provisioning work is inside or
outside the range before the estimate is committed.**

⚠️ **Complexity multipliers from `skills/how-to-estimate-effort.md` that apply but are not visibly
priced into the source range:** strict regulatory compliance (1.25×), high security classification —
special-category health plus financial data (1.25×), unclear requirements (1.5×, and thirty open
questions remain), and integration with a not-yet-confirmed external system (1.5× for QuickBooks and
the form plugin). The source's ranges absorb ordinary variability and it explicitly removed
double-counted contingency in v0.4. Applied literally, these multipliers would push the upper bound
well past 160 hours. The recommended position is to hold 106–160 hours as the working estimate for an
experienced consultant on a confirmed design, and to **re-confirm it once OQ-002, OQ-004 to OQ-006,
OQ-014 and OQ-015 are closed.**

⚠️ **OQ-004, OQ-005 and OQ-006 must be resolved before this estimate can be confirmed.** Each
is described as a configuration change rather than a rebuild, so none should move the total
materially — but a different answer on OQ-004 (physical separation required instead of field-level
security) means a separate trustee-facing store kept in sync, which is a design change the architect
must size, not a configuration change.

---

## Appendix A — Traceability Matrix (FR → US)

Test cases are added by the test-agent; this matrix is the coverage baseline.

| FR | User story / acceptance criterion |
|---|---|
| FR-001 | US-001 AC-1 |
| FR-002 | US-001 AC-2 |
| FR-003 | US-001 AC-3 |
| FR-004 | US-001 AC-4 |
| FR-005 | US-002 AC-1 |
| FR-006 | US-001 AC-5, US-002 AC-2 |
| FR-007 | US-005 AC-1 |
| FR-008 | US-005 AC-2 |
| FR-009 | US-005 AC-3 |
| FR-010 | US-005 AC-4 |
| FR-011 | US-006 AC-1 |
| FR-012 | US-006 AC-2 |
| FR-013 | US-006 AC-3 |
| FR-014 | US-006 AC-4 |
| FR-015 | US-006 AC-5 |
| FR-016 | US-006 AC-6 |
| FR-017 | US-006 AC-7 |
| FR-018 | US-006 AC-8 |
| FR-019 | US-006 AC-9 |
| FR-020 | US-006 AC-10 |
| FR-021 | US-006 AC-11 |
| FR-022 | US-006 AC-12 |
| FR-023 | US-010 AC-1 |
| FR-024 | US-010 AC-2, US-015 AC-3 |
| FR-025 | US-010 AC-3 |
| FR-026 | US-007 AC-1 |
| FR-027 | US-007 AC-2, US-014 AC-2 |
| FR-028 | US-007 AC-3 |
| FR-029 | US-007 AC-4 |
| FR-030 | US-007 AC-5 |
| FR-031 | US-007 AC-6, US-012 AC-3, US-015 AC-2 |
| FR-032 | US-014 AC-1, AC-2 |
| FR-033 | US-007 AC-7 |
| FR-034 | US-012 AC-1, US-013 AC-1, AC-2 |
| FR-035 | US-012 AC-2 |
| FR-036 | US-012 AC-3, US-013 AC-4 |
| FR-037 | US-012 AC-4, US-013 AC-3, US-008 AC-1 |
| FR-038 | US-012 AC-5 |
| FR-039 | US-013 AC-4, US-014 AC-3 |
| FR-040 | US-008 AC-1, AC-2 |
| FR-041 | US-003 AC-1, US-008 AC-2 |
| FR-042 | US-003 AC-2 |
| FR-043 | US-003 AC-3, US-009 AC-1 |
| FR-044 | US-009 AC-2 |
| FR-045 | US-003 AC-4, US-009 AC-3 |
| FR-046 | US-003 AC-5 |
| FR-047 | US-008 AC-3 |
| FR-048 | US-004 AC-4, US-011 AC-1 |
| FR-049 | US-004 AC-2, US-011 AC-2 |
| FR-050 | US-004 AC-3, US-015 AC-4 |
| FR-051 | US-004 AC-2 |
| FR-052 | US-004 AC-3 |
| FR-053 | US-004 AC-1 |
| FR-054 | US-011 AC-3 |
| FR-055 | US-011 AC-4 |

NFR-001 to NFR-003 are additionally exercised by US-012 AC-3 and US-015 AC-1, AC-2.
NFR-022 to NFR-025 have no acceptance criteria by design — they are recorded gaps (OQ-020 to OQ-023).

---

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-10  **Response:** `APPROVED`
