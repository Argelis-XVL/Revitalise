# Solution Design Document — Revitalise Grant Application Process Automation

> **Source:** adopted from `docs/architecture/revitalise-grant-automation-source-architecture.md` on 2026-07-10 by plan-agent (intake mode).
> Original author: Xander Lykopoulos — Argelis Consultancy. See Adoption Report in gate log.
>
> **Intake note:** the adopted source is a *solution architecture* document (Solution Architecture v0.3), not a requirements
> document. The two requirements-bearing sources it references — Solution Overview v0.1 (business case/ROI) and
> Automation Solution Design v0.4 (per-automation logic, field-level design, estimates) — were **NOT provided**.
> This SDD is therefore adopted at **flow/architecture altitude**: functional requirements and user-story acceptance
> criteria are derived from the source's end-to-end data flow (§6), retention/erasure schema (§8) and compliance
> guardrails (§8). Per-automation field-level detail is a known gap recorded in §9, not authored here.

**Feature Slug:** revitalise-grant-automation
**Requested By:** Revitalise (UK charity) — via Xander Lykopoulos, Argelis Consultancy
**Date:** 2026-07-10
**Status:** DRAFT

---

## 1. Business Context
<!-- DERIVED from source §1 Purpose and scope and §2 Overall solution approach. The business case, scope rationale and ROI live in Solution Overview v0.1, which was not provided (see §9 OQ-01). -->

Revitalise, a UK charity, runs a grant application process that today handles applicant personal data — including
special-category health and disability information — through manual, laptop-bound handling. The programme automates the
grant journey from application submission through scoring, anonymisation, trustee decision and acceptance, on the
Microsoft 365 and Power Platform stack Revitalise already owns.

The automation replaces the **data handling**, not the **decision-making**: nothing is sent, approved or published
without the grants manager confirming it. The objective is a consistent, maintainable, cloud-native and compliant
process that removes single-laptop dependency and enforces the charity's published retention and lawful-basis position
by design. This SDD covers the Phase 0 governed foundation and the seven automations the architecture describes.

## 2. Objectives
<!-- DERIVED from source §2 architecture principles and §6 end-to-end flow. -->

- Automate the end-to-end grant journey (submission → scoring → anonymisation → trustee decision → signed acceptance) on Microsoft 365 / Power Platform, with no custom code (low-code only).
- Keep the process maintainable by non-developers: thresholds, templates and mappings held in configuration, not flow logic.
- Make the solution cloud-native and portable: SharePoint Online as the single system of record; no local-file dependency.
- Enforce Revitalise's published data-retention and lawful-basis position automatically, and preserve human decision-making on all outcomes affecting applicants.
- Establish a governed Phase 0 foundation (environments, DLP, service identity, naming, ALM) before any automation is built.

## 3. Scope
<!-- PRESENT — source §1 (out of scope), §2 (solution boundary) and §5 (component map: "if it is not on this list, it is not part of the solution"). In-scope functional detail is expressed as the seven numbered automations by reference; per-automation logic resides in Solution Design v0.4 (not provided). -->

### In Scope
- **Data (SharePoint Online):** Grant Applications list, Settings list, Grant History list, Trustee Packs library, and the defined list views (Pending, Rejected, Borderline, Anonymisation – Review Required).
- **Orchestration (Power Automate):** nine cloud flows — Intake (#4); Scoring Calculate & Flag and Daily Summary (#2); Acceptance Create Envelope, Reminders & Escalation, and Completion (#3); Anonymisation Generate Trustee Pack (#5); Portal Finalise Decisions (#6); Duplicate QBO Check (#7). Plus the Governance Retention & Erasure Sweep flow (§8).
- **Experience & intelligence:** SharePoint trustee review page; Power Apps decision-capture form (#6); DocuSign acceptance template (#3); Word narrative-PDF template (#5); AI Builder pre-built PII model for narrative anonymisation (#5).
- **Governance:** DEV and PROD environments (Dataverse-enabled), each behind an Entra ID security group; service account (svc-grantautomation); environment-level DLP policy; the RevitaliseGrantAutomation solution; ALM promotion (managed solution, Power Platform Pipelines).
- **Compliance enforcement:** status-driven retention sweep, right-to-erasure execution, immutable deletion log, least-privilege access to special-category fields.

### Out of Scope
- The WordPress application form itself (external system; automation #1 is validation at source, owned outside the solution boundary).
- Detailed security & permissions matrix (produced as WBS 0.5, Security model document).
- Operational GDPR detail — DPIA, record of processing, DLP configuration (WBS 0.7, Data governance framework).
- Step-by-step deployment procedures (WBS 0.6, ALM runbook — this SDD/architecture sets strategy only).
- Per-automation logic and field-level design (Solution Design v0.4 — not provided).
- Power BI reporting (deliberately avoided in favour of SharePoint list views + Power Apps form, per the v0.4 scope reduction; remains a later option).

## 4. Functional Requirements
<!-- DERIVED at flow altitude from source §6 (end-to-end data flow), §8 (retention/erasure) and §8 (compliance guardrails). Testable statements exist in the source, so §4 is satisfied; field-level detail (exact scoring formula, field validations, exact anonymisation rules) lives in Solution Design v0.4 (not provided) — see §9 OQ-02. -->

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | The system SHALL create a Grant Applications record with a unique reference in the format REV-YYYY-NNN WHEN an application is received from the WordPress intake, SO THAT every application is uniquely traceable. | High |
| FR-002 | The system SHALL degrade to a scheduled REST pull or a structured-email intake WHEN the WordPress HTTP webhook is unavailable, SO THAT intake continues without a single point of failure. | Medium |
| FR-003 | The system SHALL catch malformed or duplicate intake payloads and surface them to the grants manager via Microsoft Teams WHEN a payload cannot be processed, SO THAT failures are visible rather than silent. | High |
| FR-010 | The system SHALL calculate an application score and set status to Auto-pass, Borderline or Auto-reject against the Settings-list thresholds WHEN a Grant Applications item is created, SO THAT applications are triaged consistently. | High |
| FR-011 | The system SHALL treat the scoring knockout as a non-binding flag only and SHALL NOT reject an application by solely automated means, SO THAT no solely-automated decision is made on special-category data. | High |
| FR-012 | The system SHALL record a logged human confirmation by the grants manager WHEN an application is rejected, SO THAT human review of every rejection is auditable (DUAA 2025 / Privacy Notice "humans decide"). | High |
| FR-013 | The system SHALL produce a daily scoring summary WHEN the scheduled daily trigger fires, SO THAT the grants manager sees the day's triage state. | Low |
| FR-020 | The system SHALL query QuickBooks Online (read-only) by applicant name/email as a child flow WHEN a Grant Applications item is created, SO THAT potential duplicate grants are flagged. | Medium |
| FR-021 | The system SHALL fall back to a quarterly export into the Grant History list WHEN the live QBO query is unavailable, SO THAT duplicate checking survives connector loss. | Low |
| FR-030 | The system SHALL generate an anonymised trustee pack (anonymised Excel + per-application PDFs) to the Trustee Packs library WHEN an approved application is prepared for the board, SO THAT trustees review without seeing identifying data. | High |
| FR-031 | The system SHALL apply rule-based identifier stripping plus AI Builder narrative scrubbing to free-text narratives WHEN generating a trustee pack, SO THAT personal data in free text is removed. | High |
| FR-032 | The system SHALL flag any anonymisation result below the Settings confidence threshold for grants-manager review WHEN scrubbing narratives, SO THAT low-confidence redactions are human-checked before release. | High |
| FR-040 | The system SHALL allow trustees to record Approve / Defer / Reject with notes via the Power Apps decision form embedded in the SharePoint review page, SO THAT decisions are captured against each anonymised application. | High |
| FR-041 | The system SHALL update the Grant Applications master list and trigger DocuSign for approved grants WHEN the grants manager clicks Finalise Decisions, SO THAT board outcomes are applied under a single human action. | High |
| FR-050 | The system SHALL create a DocuSign envelope from the acceptance template WHEN an application status becomes Approved, SO THAT the acceptance letter is routed for signature. | High |
| FR-051 | The system SHALL send reminders and escalate WHEN a signature is outstanding (scheduled / DocuSign event), SO THAT acceptances are not stalled. | Medium |
| FR-052 | The system SHALL write the signed PDF and set status "Acceptance Signed" back to SharePoint WHEN the DocuSign envelope is completed, SO THAT the record reflects a completed acceptance. | High |
| FR-060 | The system SHALL run a monthly retention & erasure sweep that deletes records with their attachments WHEN their status and date have passed the defined retention period, SO THAT retention is enforced without manual action. | High |
| FR-061 | The system SHALL retain a successful grant record (including health free-text and signed acceptance PDF) for 6 years from final payment date, then delete, SO THAT the Charities Act 2011 financial-record period is met. | High |
| FR-062 | The system SHALL delete an unsuccessful application 12 months from decision date, SO THAT rejected applicants' data is not over-retained. | High |
| FR-063 | The system SHALL delete a withdrawn/incomplete application 6 months from last contact, SO THAT abandoned applications are not over-retained. | High |
| FR-064 | The system SHALL write an immutable deletion-log entry (record reference, data type, date, rule applied) containing no personal data WHEN any record is deleted, SO THAT deletions are accountable under UK GDPR Article 5(2). | High |
| FR-065 | The system SHALL execute a right-to-erasure request on demand for a single applicant reference — locating data across Grant Applications, Trustee Packs, DocuSign and QuickBooks (including referees, helpers, group members, emergency contacts), honouring legal-hold carve-outs and informing the requester which data cannot yet be deleted — SO THAT UK GDPR Article 17 requests are fulfilled. | High |
| FR-070 | The system SHALL hold the knockout threshold, income ceiling and confidence threshold in the Settings list editable by the grants manager, SO THAT thresholds change without editing a flow. | Medium |
| FR-071 | The system SHALL restrict special-category fields to read access by the service account and the grants-manager role only, exposing trustees to the anonymised view exclusively, SO THAT least-privilege applies to health data. | High |

## 5. Non-Functional Requirements
<!-- DERIVED. Residency, retention timing, sweep cadence, resilience/fallback and maintainability thresholds ARE stated in the source and are measurable. Performance, availability and volume thresholds are NOT stated → recorded as Open Questions (OQ-04). -->

| ID | Requirement | Category |
|---|---|---|
| NFR-001 | All Power Platform environments, AI Builder, DocuSign and QuickBooks Online connections SHALL keep processing within the UK — zero data transfers outside the UK (verified at 0.2 environment setup and integration build). | Compliance / Residency |
| NFR-002 | The retention schedule SHALL be enforced automatically to the published periods: successful grant 6 years from final payment; unsuccessful 12 months from decision; withdrawn/incomplete 6 months from last contact; anonymised statistics indefinite. Enforced by a monthly sweep. | Compliance / Retention |
| NFR-003 | Special-category (health/disability) fields SHALL be accessible only to the service account and the grants-manager role (least privilege). | Security |
| NFR-004 | All external connections SHALL be owned by the service account (svc-grantautomation), not a personal login, authenticated per the integration register (OAuth / shared secret / service mailbox). | Security |
| NFR-005 | Every inbound integration (WordPress, DocuSign, QuickBooks Online) SHALL have a documented fallback such that no single external dependency can halt the pipeline. | Availability / Resilience |
| NFR-006 | Configuration values (thresholds, URLs, service mailbox) SHALL be held in the Settings list and environment variables; no flow SHALL be edited at deployment time. | Maintainability |
| NFR-007 | PROD SHALL receive the solution as a managed (locked) package only; no direct edits; rollback SHALL be re-import of the prior retained managed .zip. | Compliance / ALM |
| NFR-008 | ⚠️ Intake-to-record latency and end-to-end processing time — **threshold not stated in source** (OQ-04). | Performance (unmeasured) |
| NFR-009 | ⚠️ Availability / uptime target for the live automations — **threshold not stated in source** (OQ-04). | Availability (unmeasured) |
| NFR-010 | ⚠️ Expected application volume / throughput — **threshold not stated in source** (OQ-04). | Scalability (unmeasured) |

## 6. User Stories
<!-- DERIVED from the named actors and the happy-path flow (source §6) plus the retention/erasure schema (§8). Acceptance criteria are grounded in the flow and retention rules; field-level acceptance detail is deferred to Solution Design v0.4 (OQ-02). -->

Actors: **Applicant**, **Grants Manager** (referred to as "Emily" in the source), **Trustee**, **Service account** (svc-grantautomation), **DPO** (Rebecca Young).

### US-001: Application intake
**As an** applicant, **I want** my submitted form to become a tracked application, **so that** my request enters the grant process reliably.
**Acceptance Criteria:**
- Given a validated WordPress submission, when the intake flow runs, then a Grant Applications item is created with a REV-YYYY-NNN reference. *(FR-001)*
- Given the HTTP webhook is unavailable, when a submission is due, then intake proceeds via scheduled REST pull or structured email. *(FR-002)*
- Given a malformed or duplicate payload, when intake processes it, then the grants manager is notified via Teams and the payload does not fail silently. *(FR-003)*

### US-002: Triage and human decision
**As a** grants manager, **I want** applications scored and flagged, **so that** I can triage consistently while retaining the decision.
**Acceptance Criteria:**
- Given a new Grant Applications item, when scoring runs, then status is set to Auto-pass / Borderline / Auto-reject against the Settings thresholds. *(FR-010)*
- Given a knockout condition, when scoring completes, then the outcome is a flag only and no rejection occurs by solely automated means. *(FR-011)*
- Given an application is rejected, when I confirm the rejection, then a human-confirmation event is logged. *(FR-012)*

### US-003: Duplicate check
**As a** grants manager, **I want** new applications checked against past grants, **so that** duplicate funding is flagged.
**Acceptance Criteria:**
- Given a new item, when the child flow runs, then QuickBooks Online is queried read-only by name/email and a duplicate flag is set where matched. *(FR-020)*
- Given QBO is unavailable, when duplicate checking is needed, then the quarterly Grant History export is used as fallback. *(FR-021)*

### US-004: Anonymised trustee pack
**As a** grants manager, **I want** an anonymised pack generated, **so that** trustees review without seeing identifying data.
**Acceptance Criteria:**
- Given an approved-for-board application, when anonymisation runs, then an anonymised Excel + per-application PDFs are written to the Trustee Packs library. *(FR-030)*
- Given free-text narratives, when scrubbing runs, then rule-based stripping and AI Builder scrubbing are both applied. *(FR-031)*
- Given a scrub result below the confidence threshold, when the pack is generated, then the item is flagged for my review (Anonymisation – Review Required view). *(FR-032)*

### US-005: Trustee decision capture
**As a** trustee, **I want** to record my decision on each anonymised application, **so that** the board outcome is captured.
**Acceptance Criteria:**
- Given the review page, when I open an application, then I can record Approve / Defer / Reject with notes via the embedded Power Apps form. *(FR-040)*

### US-006: Finalise decisions
**As a** grants manager, **I want** to apply the board's decisions in one action, **so that** outcomes flow to acceptance.
**Acceptance Criteria:**
- Given completed trustee decisions, when I click Finalise Decisions, then the master list updates and DocuSign is triggered for approved grants. *(FR-041, FR-050)*

### US-007: Acceptance signing
**As a** grants manager, **I want** approved grants routed for dual e-signature, **so that** acceptances complete and are recorded.
**Acceptance Criteria:**
- Given status becomes Approved, when the acceptance flow runs, then a DocuSign envelope is created from the acceptance template. *(FR-050)*
- Given an outstanding signature, when the reminder schedule fires, then reminders/escalations are sent. *(FR-051)*
- Given the envelope is completed, when the completion event fires, then the signed PDF and "Acceptance Signed" status are written to SharePoint. *(FR-052)*

### US-008: Automated retention
**As a** data controller (Revitalise), **I want** records deleted at end of their retention period, **so that** data is not over-retained.
**Acceptance Criteria:**
- Given the monthly sweep, when a record's status and date have passed its retention period, then the record and its attachments are deleted. *(FR-060, FR-061, FR-062, FR-063)*
- Given any deletion, when it occurs, then an immutable deletion-log entry with no personal data is written. *(FR-064)*

### US-009: Right to erasure
**As an** applicant exercising Article 17, **I want** my data erased on request, **so that** my rights are honoured.
**Acceptance Criteria:**
- Given an erasure request for a reference, when the sweep is run on demand, then all of the individual's data across Grant Applications, Trustee Packs, DocuSign and QuickBooks is located and deleted except legal-hold carve-outs, and the requester is told what cannot yet be deleted. *(FR-065)*

### US-010: Threshold configuration
**As a** grants manager, **I want** to adjust thresholds myself, **so that** the process adapts without a developer.
**Acceptance Criteria:**
- Given the Settings list, when I change the knockout threshold, income ceiling or confidence threshold, then scoring and anonymisation use the new values without any flow being edited. *(FR-070)*

## 7. Compliance & Regulatory Considerations
<!-- PRESENT — source §8 is explicit on UK GDPR, DUAA 2025 and Charities Act 2011. FLAGGED FOR REVIEWER per intake checklist: the specific UK GDPR Article 6 lawful-basis sub-condition is not stated in the source (OQ-06); it is documented here only as far as the source states it. -->

Revitalise is the **data controller** and owns the retention periods and lawful-basis analysis; this solution implements
its published Privacy Notice (updated 20 February 2026) — it does not set policy. The source is explicit that the
solution processes **special-category** health and disability data.

**Lawful basis per PII-holding data entity (as stated by the source):**

| Data entity | Personal data held | Art 6 basis | Special-category condition | Retention basis |
|---|---|---|---|---|
| Grant Applications | Applicant PII + special-category health/disability free-text + referees, helpers, group members, emergency contacts | UK GDPR Article 6 *(specific sub-condition not stated — OQ-06)* | Article 9(2)(b) social protection; Article 9(2)(h) health & social care | 6y successful (Charities Act 2011) / 12m rejected / 6m withdrawn |
| Trustee Packs (library) | Pseudonymised — linkable by reference; still personal data | Follows parent record | Follows parent record | Same clock as parent grant record |
| Grant History (list) | Financial: name, amount, date | Article 6 | n/a | 6y (Charities Act / finance policy) |
| Signed acceptance PDF | Applicant identity + signature | Follows grant record | n/a | 6y with record |
| Deletion log | None (reference + metadata only) | n/a | n/a | Accountability record (Art 5(2)) |
| Irreversibly anonymised statistics | None (not linkable) | Outside UK GDPR | n/a | Indefinite |

**Regulatory obligations designed in (source §8):**
- **UK GDPR Article 5(2) (accountability):** immutable deletion log.
- **UK GDPR Article 17 (erasure):** on-demand sweep with legal-hold carve-outs.
- **UK GDPR Article 15 (SAR):** implied — the same locate-across-systems capability supports subject access *(confirm — OQ-07)*.
- **DUAA 2025 (in force 5 Feb 2026):** no solely-automated decisions on special-category data; every rejection carries logged human confirmation.
- **Charities Act 2011:** 6-year financial-record retention drives the successful-grant period.
- **Data residency:** all processing kept within the UK.
- **Least privilege on health data:** service account + grants-manager role only; trustees see anonymised view only.

**DPO sign-off (recommended before go-live, per source):** Revitalise's DPO (Rebecca Young) should confirm (a) that
logged human confirmation of every rejection satisfies the DUAA 2025 automated-decision position, and (b) that 6-year
retention of the health free-text remains preferred over earlier minimisation. *(OQ-08)* This SDD sets requirements; it
is not legal advice.

> **Reviewer flag:** §7 is adopted from the source's stated compliance position. It has **not** been independently
> validated against a populated domain-compliance knowledge base — that base is an unpopulated placeholder in this repo
> (see System Findings). DPIA, record of processing and DLP configuration are deferred to WBS 0.7.

## 8. Assumptions & Dependencies
<!-- PRESENT — source §10 (assumptions), §9 (licensing dependencies), §2 (external dependencies). -->

**Assumptions**
- Revitalise runs Microsoft 365 Business Premium (standard connectors + SharePoint Online included).
- A Power Automate Premium licence is procured for the service account (HTTP trigger + premium connectors DocuSign, QBO); one per-user licence covers all production flows including the retention sweep.
- M365 administrator access is available to create environments, the service account, DLP and Conditional Access exceptions.
- The WordPress form plugin supports a webhook, REST API or structured email (else the fallback intake applies).
- Business Premium provides basic Purview retention labels; status-aware retention/erasure is enforced by the sweep flow, not Purview. Native event-based retention (E5 / Purview Suite) is not licensed.
- DocuSign and QuickBooks retention settings can be configured to match the published schedule; UK data residency is available for all connectors.

**Dependencies**
- **External systems (only three):** WordPress (application intake), DocuSign (acceptance signatures), QuickBooks Online (duplicate-grant checks). SharePoint Online is the integration hub; external systems never talk to each other directly.
- **DocuSign licensing** must be in place before the acceptance workflow (#3) goes live.
- **AI Builder / narrative anonymisation (#5)** runs on Copilot Credits (AI Builder not in Business Premium; standalone add-on closed to new buyers). Seeded credits are due to end **1 November 2026** — the ongoing route must be confirmed before #5 goes live.
- Downstream Phase 0 deliverables 0.2–0.8 (environments, service account, SharePoint architecture, security model, ALM runbook, data governance) build on the adopted architecture.

## 9. Open Questions
<!-- Populated with every MISSING/gap item from the intake. GATE-BLOCKING items are labelled explicitly; none are gate-blocking (all mandatory checklist sections are PRESENT or DERIVED). -->

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-01 | Solution Overview v0.1 (business case, scope, ROI, priorities) was not provided — needed to confirm §1/§2 and requirement prioritisation. **Not gate-blocking** (business context derivable from architecture). | Argelis / Revitalise | Before architecture intake |
| OQ-02 | Automation Solution Design v0.4 (per-automation logic, field-level design, field validations, exact scoring & anonymisation rules, per-automation estimates) was not provided — needed to elaborate FR detail, field-level acceptance criteria and calibrated effort. **Not gate-blocking** (testable flow-level statements exist). | Argelis | Before development |
| OQ-03 | WBS v0.4 (task-level hours, dependencies, phasing) was not provided — needed to calibrate §10 effort. | Argelis | Before development |
| OQ-04 | NFR thresholds not stated: intake-to-record latency, end-to-end processing time, availability/uptime target, expected application volume/throughput (NFR-008/009/010). | Revitalise / Argelis | Before architecture sign-off |
| OQ-05 | Licensing figures marked "verify": Power Automate Premium cost, Purview add-on cost, Microsoft nonprofit pricing, and the AI Builder / Copilot Credits ongoing route (seeded credits end 1 Nov 2026). | Revitalise (procurement, WBS 0.2) | Before #5 go-live |
| OQ-06 | The specific UK GDPR Article 6 lawful-basis sub-condition for applicant data is not stated in the source (only "Article 6" plus the Article 9 conditions). | DPO (Rebecca Young) | Before go-live |
| OQ-07 | SAR (Article 15) path is only implied by the erasure/locate capability — confirm whether an explicit subject-access route is required. | DPO (Rebecca Young) | Before go-live |
| OQ-08 | DPO sign-off on (a) logged human confirmation of rejections satisfying the DUAA 2025 automated-decision position and (b) 6-year retention of health free-text vs earlier minimisation. | DPO (Rebecca Young) | Before go-live |
| OQ-09 | Tenant default region confirmation for UK data residency (deferred to WBS 0.2). | Argelis (WBS 0.2) | Environment setup |

## 10. Effort Estimate
<!-- DERIVED via skills/how-to-estimate-effort.md. This is an SDD-altitude, order-of-magnitude estimate ONLY: the authoritative per-automation estimates live in the absent Solution Design v0.4 / WBS v0.4 (OQ-02, OQ-03). -->

**Size:** XL (> 4 weeks — a programme, not a single feature; broken into WBS phases by the source)

**Range:** ≈ 40–70 developer-days across Phase 0 foundation + the seven automations, most likely toward the upper half given the compliance and integration load. **Uncalibrated** — see assumptions.

**Basis of estimate:** 9 Power Automate flows (10 including the retention sweep), 3 SharePoint lists + 1 library + views, 1 Power Apps decision form, 3 external integrations (WordPress webhook, DocuSign, QBO) each with a fallback, AI Builder anonymisation, Word/DocuSign templates, 2 managed environments, DLP, service identity, and ALM (Power Platform Pipelines + Git backup).

**Complexity multipliers applied (per the effort skill):**
- Strict regulatory compliance required — 1.25×
- High security classification (special-category health data) — 1.25×
- Integration with a poorly-documented external system (WordPress webhook capability uncertain) — 1.5×
- Unclear requirements (per-automation detail in absent v0.4) — 1.5×

**Assumptions:** single maker (Xander), synthetic data available in DEV, no blocking licence procurement delays, WordPress plugin supports one of webhook/REST/email.

> ⚠️ Open questions OQ-02 and OQ-03 must be resolved before this estimate can be confirmed — the calibrated figures exist in Solution Design v0.4 / WBS v0.4, which were not provided.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
