# Solution Architecture — Grant Application Process Automation Programme

> **Archived source document.** Saved per `skills/how-to-intake-external-documents.md`
> Principle 3 (source supplied as a conversation attachment, not a repo file).
> Original file: `Revitalise-Solution-Architecture-v0.3.pdf` — transcribed to Markdown
> without change of substance; layout and pagination removed.
>
> | Field | Value |
> |---|---|
> | Client | Revitalise |
> | Prepared by | Xander Lykopoulos — Argelis Consultancy |
> | Deliverable | Solution architecture document (WBS 0.1) |
> | Version | v0.3 — Draft for review |
> | Date | July 2026 |
> | Status | Draft · Confidential |
> | Received | 2026-07-10 |

Overall solution approach, environment strategy, naming conventions, component map,
integration architecture, and ALM packaging strategy.

---

## 1. Purpose and scope

This document is the solution architecture for the Revitalise grant application automation
programme. It is the first deliverable of Phase 0 (Platform Foundation & Governance, WBS task
0.1) and the technical foundation that every subsequent automation is built on. It fixes the
decisions that are expensive to change later: how the platform is structured, how work moves
from build to live, how things are named, and how the parts fit together.

It covers six areas, matching the WBS 0.1 definition: **overall solution approach, environment
strategy (dev/prod), naming conventions, component map, integration architecture, and
the solution packaging strategy for ALM**.

**In plain terms:** Before building anything, we agree how the system is laid out and how we
move it safely from a testing area into live use. This document is that agreement. It keeps the
seven automations consistent, maintainable by non-developers, and safe to change without
breaking what already works.

### Related documents

| Document | Role | Status |
|---|---|---|
| Solution Overview (v0.1) | Business case, scope, ROI — for Revitalise leadership | Draft |
| Automation Solution Design (v0.4) | Per-automation build specifications and estimates | Draft |
| Work Breakdown Structure (v0.4) | Task-level plan, hours, dependencies, phasing | Draft |
| This document — Solution Architecture (v0.3) | Technical foundation: environments, naming, components, integration, ALM | Draft |
| Downstream Phase 0 deliverables (0.2–0.8) | Environments, security model, ALM runbook, data governance — build on this document | Planned |

### Out of scope for this document

- Detailed security and permissions matrix — produced as WBS 0.5 (Security model document).
- The data retention schema is set in Section 8. GDPR operational detail (DPIA, record of
  processing, DLP configuration) is completed in WBS 0.7 (Data governance framework).
- Step-by-step deployment procedures — produced as WBS 0.6 (ALM runbook). This document
  sets the strategy; the runbook operationalises it.
- Per-automation logic and field-level design — held in the Solution Design v0.4.

---

## 2. Overall solution approach

The solution automates the grant journey from application submission to trustee decision and
acceptance, on the Microsoft 365 and Power Platform stack Revitalise already owns. Nothing is
sent, approved, or published without Emily confirming it — the automations replace the data
handling, not the decision-making.

### Architecture principles

Five principles govern every design decision. They carry forward the four principles set in the
Solution Design and add one for this foundation layer.

| Principle | What it means in practice |
|---|---|
| Low-code, no custom code | Power Automate cloud flows, Power Apps, and SharePoint configuration only. No VBA, no macros, no scripts running on anyone's laptop. |
| Maintainable by non-developers | Thresholds, templates, and mappings live in configuration (a Settings list, environment variables, templates) so Emily or a future admin can adjust them without editing a flow. |
| Cloud-native and portable | Data lives in SharePoint Online. No local file dependencies and no 'single source of truth on one laptop' risk. |
| AI only where it earns its place | AI Builder is used for free-text anonymisation, where rule-based find-and-replace fails. Everywhere else, simpler tools do the job. |
| Governed foundation first | Environments, DLP, service identity, naming, and ALM are established in Phase 0 before any automation is built, so every later component inherits a consistent, controlled structure. |

### Platform stack

| Layer | Technology | Responsibility |
|---|---|---|
| Experience | WordPress form, Power Apps, Power BI / SharePoint pages, DocuSign | Where people interact — applicants, Emily, trustees, signatories |
| Orchestration | Power Automate cloud flows | The logic: intake, scoring, anonymisation, notifications, packaging |
| Intelligence | AI Builder (pre-built PII model) | Detecting personal data in free-text narratives |
| Data | SharePoint Online lists & document libraries | The system of record for applications, settings, history, and packs |
| Integration | Standard & premium connectors, webhook (HTTP) | The pipes between systems |
| Identity & governance | Microsoft Entra ID, service account, DLP, Conditional Access | Who and what is allowed to do what |

### Solution boundary

Everything inside the Microsoft 365 tenant is built and owned within a single Power Platform
solution (see Section 7). Three systems sit outside that boundary and are reached through
connectors: the WordPress website (application intake), DocuSign (acceptance signatures), and
QuickBooks Online (duplicate-grant checks). These are the only external dependencies.

---

## 3. Environment strategy

A two-environment model — Development and Production — gives a safe place to build and test,
separated from the live system Emily and the trustees rely on. This is the minimum responsible
separation for a solution that handles applicant personal data.

| Environment | Purpose | Data | Access |
|---|---|---|---|
| Development (DEV) | Build and test all flows, lists, apps, and templates. Iterate with Emily using sample and anonymised test data. | Synthetic / test applications only — no real applicant PII | Xander (maker) + service account |
| Production (PROD) | The live system. Receives real applications and runs the live automations. | Real applicant data, governed under the data governance framework (0.7) | Service account runs flows; Emily & trustees use outputs |

### Environment configuration

- **Type:** both are managed Power Platform environments with a Dataverse database enabled
  (required for solution deployment, environment variables, and connection references).
- **Region:** United Kingdom, to keep applicant data in-region for data-protection alignment.
  Confirm the tenant's default region during 0.2.
- **Security groups:** each environment is restricted to a dedicated Entra ID security group, so
  only intended makers and the service account can access it.
- **Solution handling:** DEV holds the unmanaged solution (editable). PROD receives it as a
  managed solution (locked, deployed only through the promotion process).

### Data Loss Prevention (DLP)

An environment-level DLP policy governs which connectors may be used and prevents data
flowing between business and non-business connector groups. The policy is defined in detail in
the data governance work (0.7); the architectural stance is set here.

| Connector group | Connectors | Rule |
|---|---|---|
| Business | SharePoint, Office 365 Outlook, Microsoft Teams, Approvals, AI Builder, Word Online (Business), DocuSign, QuickBooks Online | Permitted; may share data with each other |
| Blocked | Consumer social, personal storage, and any connector not required by the solution | Blocked in both environments |

**Note on the HTTP trigger:** The WordPress webhook uses a request/HTTP trigger, which is a
premium capability and can carry DLP implications. It is scoped to the intake flow only and
secured (Section 6). If tenant DLP blocks it, the fallback is the scheduled REST-API pull or
structured-email intake described in the Solution Design.

### Licensing implications

- Revitalise runs Microsoft 365 Business Premium, which carries standard connectors only. A
  Power Automate Premium licence is therefore required on the service account for the HTTP
  trigger and premium connectors (DocuSign, QuickBooks Online).
- AI Builder is not included in Business Premium, and the standalone add-on is closed to new
  buyers. Narrative anonymisation (#5) therefore runs on Copilot Credits — a point to confirm,
  as seeded credits are due to end 1 November 2026.
- Trustee portal — delivered on SharePoint list views + a Power Apps form to avoid Power BI
  Pro licensing, per the v0.4 scope reduction. Power BI remains a later option.
- The full licensing model — components, licence types, indicative cost, and the
  retention-enforcement route — is set out in Section 9 (Licensing).

---

## 4. Naming conventions

Consistent naming is what keeps a low-code solution readable a year later, when someone other
than the builder needs to find, understand, or change a component. The conventions below apply
to every artefact in the solution. The publisher prefix is 'rev'.

### Environments and solution

| Element | Convention | Example |
|---|---|---|
| Environment | Revitalise – Grant Automation (\<ENV\>) | Revitalise – Grant Automation (DEV) / (PROD) |
| Publisher | Argelis Consultancy, prefix 'rev' | Prefix: rev · Display: Argelis Consultancy |
| Solution (unique) | RevitaliseGrantAutomation | RevitaliseGrantAutomation |
| Solution (display) | Revitalise Grant Automation | Revitalise Grant Automation |

### Power Automate flows

Pattern: **REV | \<Automation\> | \<Action\>**. The automation segment ties each flow back to its
number in the Solution Design and WBS, so the whole set sorts and groups logically.

| Flow name | Automation | Trigger |
|---|---|---|
| REV \| Intake \| WordPress to SharePoint | #4 Intake | HTTP webhook (fallback: scheduled / email) |
| REV \| Scoring \| Calculate & Flag | #2 Scoring | SharePoint item created |
| REV \| Scoring \| Daily Summary | #2 Scoring | Scheduled (daily) |
| REV \| Acceptance \| Create Envelope | #3 DocuSign | SharePoint status = Approved |
| REV \| Acceptance \| Reminders & Escalation | #3 DocuSign | Scheduled / DocuSign event |
| REV \| Acceptance \| Completion | #3 DocuSign | DocuSign envelope completed |
| REV \| Anonymisation \| Generate Trustee Pack | #5 Anonymisation | Manual / scheduled pre-board |
| REV \| Portal \| Finalise Decisions | #6 Portal | Manual (Emily) after board |
| REV \| Duplicate \| QBO Check | #7 Duplicate check | SharePoint item created (child flow) |

### SharePoint, connections and columns

| Element | Convention | Example |
|---|---|---|
| Site | Revitalise Grant Management — /sites/grants | https://\<tenant\>.sharepoint.com/sites/grants |
| List / library | Title Case, business-friendly | Grant Applications · Settings · Grant History · Trustee Packs |
| Internal column | PascalCase, no spaces | TotalScore · ApplicationStatus · IncomeFlag · ReferenceNumber |
| Application reference | REV-YYYY-NNN | REV-2026-014 |
| Connection reference | rev-\<Service\> | rev-sharepoint · rev-docusign · rev-qbo · rev-outlook |
| Environment variable | rev_\<Purpose\> | rev_TrusteePackLibrary · rev_ServiceMailbox · rev_DefaultThreshold |
| Service account | svc-\<purpose\>@\<domain\> | svc-grantautomation@revitalise.org |

**Why environment variables and connection references:** Both are what make the solution
portable. Connection references mean a flow points to 'the SharePoint connection' rather than a
hard-wired login, so it re-binds cleanly in PROD. Environment variables hold anything that differs
between DEV and PROD (URLs, the service mailbox, default thresholds) so no flow is edited
during deployment.

---

## 5. Component map

Every component in the solution, grouped by layer and mapped to the automation it serves. This
is the master inventory: if it is not on this list, it is not part of the solution.

### Data components (SharePoint Online)

| Component | Type | Purpose | Serves |
|---|---|---|---|
| Grant Applications | List | System of record: one item per application, with score, status and flags | All |
| Settings | List | Knockout threshold, income ceiling, confidence threshold — editable by Emily | #2, #5 |
| Grant History | List | Historical grants for duplicate checking (QBO export target) | #7 |
| Trustee Packs | Library | Generated anonymised Excel + per-application PDFs | #5, #6 |
| List views | Views | Pending · Rejected · Borderline · Anonymisation – Review Required | #2, #5, #6 |

### Orchestration components (Power Automate)

Nine cloud flows, all named per Section 4. See the naming table for triggers; full logic is in the
Solution Design.

- Intake, Scoring (Calculate & Flag), Scoring (Daily Summary), Acceptance (Create Envelope,
  Reminders & Escalation, Completion), Anonymisation (Generate Trustee Pack), Portal
  (Finalise Decisions), Duplicate (QBO Check).

### Experience & intelligence components

| Component | Technology | Purpose | Serves |
|---|---|---|---|
| Application form | WordPress (external) | Applicant-facing form with validation and conditional logic | #1, #4 |
| Trustee review page | SharePoint page + list views | Trustees browse anonymised applications and record decisions | #6 |
| Decision capture form | Power Apps | Approve / Defer / Reject with notes, embedded in the review page | #6 |
| Acceptance template | DocuSign template | Personalised acceptance letter for dual e-signature | #3 |
| Narrative PDF template | Word template | Per-application anonymised PDF via Populate a Word template | #5 |
| PII detection | AI Builder (pre-built model) | Detects personal data in free-text narratives | #5 |

### Governance components

- DEV and PROD environments (Dataverse-enabled), each behind an Entra ID security group.
- Service account (svc-grantautomation) that owns and runs the production flows and connections.
- Environment-level DLP policy; Conditional Access exception for the service account
  (documented in 0.3 / 0.5).
- The RevitaliseGrantAutomation solution itself, holding all flows, connection references,
  environment variables, and the AI model reference.

---

## 6. Integration architecture

The solution integrates three external systems with the Microsoft 365 core. SharePoint Online is
the hub: applications land there, every automation reads from and writes to it, and it is the single
source of truth. The table below is the integration register — direction, connector, licence tier,
and how each connection is trusted.

| Integration | Direction | Connector | Tier | Trigger / method | Auth |
|---|---|---|---|---|---|
| WordPress → SharePoint | Inbound | Request (HTTP) / REST / email | Premium* | Webhook on submit; fallbacks: scheduled REST pull or parsed email | Shared secret / service mailbox |
| DocuSign | Bi-directional | DocuSign | Premium | Outbound: create envelope on approval. Inbound: completion event | OAuth (service account) |
| QuickBooks Online | Inbound (read) | QuickBooks Online | Premium | Query by name/email on new item; fallback: quarterly export to Grant History | OAuth (read-only) |
| Microsoft 365 (email/Teams) | Outbound | Outlook / Teams | Standard | Notifications, summaries, escalations | Service account |
| AI Builder | Internal | AI Builder | Premium | PII detection call within the anonymisation flow | Environment credits |
| Word / Excel generation | Internal | Word Online (Business) | Standard | Populate a Word template → PDF; anonymised Excel | Service account |

\* The HTTP trigger is premium. Where the WordPress plugin cannot send a webhook, the
architecture degrades gracefully to a scheduled REST pull or a structured-email trigger without
changing any downstream component.

### End-to-end data flow

The happy path, from submission to signed acceptance:

- Applicant submits the WordPress form (validated at source, automation #1).
- Intake flow creates a Grant Applications item with a REV-YYYY-NNN reference (#4).
- Scoring flow calculates the score and sets status Auto-pass / Borderline / Auto-reject
  against the Settings thresholds (#2). The duplicate check runs as a child flow (#7).
- Emily reviews; approved applications are anonymised — rule-based stripping plus AI Builder
  narrative scrubbing, with anything below the confidence threshold flagged for her review (#5).
- The trustee pack (anonymised Excel + PDFs) is generated to the Trustee Packs library and
  surfaced on the SharePoint review page (#5, #6).
- Trustees record Approve / Defer / Reject in the Power Apps form; Emily clicks Finalise
  Decisions, which updates the master list and triggers DocuSign for approved grants (#6, #3).
- DocuSign routes the acceptance letter for dual signature, sends reminders, and on completion
  writes the signed PDF and 'Acceptance Signed' status back to SharePoint (#3).

### Integration principles

- SharePoint is the hub — external systems never talk to each other directly, only through it.
  This keeps each integration independently replaceable.
- Every integration has a documented fallback (Section 6 table), so no single external
  dependency can stop the pipeline.
- All external connections are owned by the service account, not a personal login, so they
  survive staff changes and are governed centrally.
- Error handling on every inbound flow: malformed or duplicate payloads are caught and
  surfaced to Emily via Teams rather than failing silently.

---

## 7. Solution packaging and ALM strategy

Application Lifecycle Management (ALM) is how changes move from build to live, safely and
repeatably. The whole solution is packaged as one Power Platform solution and promoted from
DEV to PROD as a managed solution — never edited directly in production.

### Packaging model

| Aspect | Decision |
|---|---|
| Unit of deployment | A single solution — RevitaliseGrantAutomation — containing all flows, connection references, environment variables, the AI model reference, and (where solution-aware) the app and templates. |
| DEV | Holds the unmanaged (editable) solution. All building and iteration happens here. |
| PROD | Receives the managed (locked) solution. No direct edits; changes only arrive through a new managed import. |
| Connection references | Used for every connector so connections are set once per environment, not baked into each flow. |
| Environment variables | Hold every value that differs between DEV and PROD (URLs, service mailbox, default thresholds), set at import time. |

### Dev → Prod promotion

- Build and test in DEV against synthetic data until the change is signed off.
- Export the solution from DEV as managed, with the version incremented (Section: versioning).
- Import into PROD; map connection references to the service-account connections and set
  environment variables for the PROD values.
- Smoke-test in PROD with a single controlled application, then enable the live triggers.

**Recommended tooling:** Power Platform Pipelines (built into the Power Platform, no extra
licence) to run the export/import promotion with one click and an audit trail. For a solution of this
size this is preferred over a full Azure DevOps pipeline; source is still backed up as below.

### Versioning and source control

- **Version scheme:** major.minor.build (e.g. 1.0.0.x). Minor increments for new automations,
  build increments for fixes.
- **Backup:** each released managed solution package (.zip) is retained in the Trustee-separate
  'Solution Packages' library / Argelis project store, tagged with its version and release date.
- **Source of truth:** the unpacked solution is committed to an Azure DevOps Git repository so
  every change is diffable and recoverable, per Argelis practice.

### Rollback

- Because PROD only ever receives managed solutions, rolling back is re-importing the previous
  managed package — the retained .zip for the prior version.
- Data (SharePoint lists) is unaffected by solution rollback; only logic and configuration revert.
- A pre-deployment checklist and rollback steps are formalised in the ALM runbook (WBS 0.6).

**What this buys Revitalise:** A change can be built, tested, and shipped without touching the
live system, and undone in minutes if something is wrong. The live grant process is never the
place where mistakes are discovered.

---

## 8. Data retention and deletion

This section sets how the solution enforces Revitalise's retention policy. Personal data —
including the special-category health and disability information the application form collects — is
held only as long as Revitalise's published schedule allows, then securely deleted or irreversibly
anonymised. The periods below implement Revitalise's Privacy Notice (updated 20 February
2026) as published; Revitalise is the data controller and owns those periods.

**Source of truth:** This schema implements the retention schedule and lawful-basis analysis in
Revitalise's published Privacy Notice (UK GDPR Article 6, plus Article 9(2)(b) social protection
and 9(2)(h) health and social care for special-category data). It translates those periods into
enforceable technical rules — it does not change them. Operational GDPR detail (DPIA, record
of processing, DLP configuration) is completed in the Data Governance framework, WBS 0.7.

### Retention schedule (as implemented)

Each application record carries a status and key dates. The retention clock is driven by status
plus date and enforced automatically, so no record depends on someone remembering to delete it.

| Data / outcome | System trigger (status + date) | Retention | Then |
|---|---|---|---|
| Successful grant — full record incl. health free-text | Status = Grant Paid; from final payment date | 6 years | Delete full record |
| Unsuccessful application | Status = Rejected; from decision date | 12 months | Delete full record |
| Withdrawn / incomplete | Status = Withdrawn / Incomplete; from last contact | 6 months | Delete full record |
| Monitoring & evaluation (pseudonymised, linked by reference) | Follows its parent grant record | Same as record | Delete with record |
| Signed acceptance PDF | Attached to the grant record | 6 years (with record) | Delete with record |
| Financial record (name, amount, date) — QuickBooks | Status = Grant Paid | 6 years | Per finance policy |
| Irreversibly anonymised statistics | No identifiers; not linkable | Indefinite | Retain |

**Policy as published:** Per Revitalise's current policy, the full successful-grant record —
including the health and disability free-text — is retained for the 6-year financial-record period
(Charities Act 2011). The architecture is built so special-category free-text can be redacted
earlier if Revitalise's DPO later opts for tighter minimisation; that is a configuration change, not a
rebuild.

### How deletion is enforced

- **Scheduled sweep flow (primary):** a Power Automate flow, REV | Governance | Retention &
  Erasure Sweep, runs monthly, finds records whose status and date have passed the retention
  period, and deletes them with their attachments. This flow — not Purview — is what enforces
  the schedule, because Business Premium cannot run event-based retention. It extends the
  orchestration layer of the component map and reuses the service account's Premium licence,
  so it adds no recurring cost (see Section 9).
- **Purview retention labels (backstop):** basic labels applied to the Grant Applications list and
  Trustee Packs library as a time-based safety net, so nothing survives well past its period even
  if the flow is paused. Business Premium supports basic retention labels only; the status-aware,
  event-based enforcement is done by the sweep flow, not Purview.
- **Deletion log:** every deletion writes to an immutable log (record reference, data type, date,
  rule applied) for accountability under UK GDPR Article 5(2). The log holds no personal data itself.
- **Reconciled copies:** deletion accounts for the systems that hold copies — SharePoint
  backups (cleared on the next backup-rotation cycle), DocuSign (envelope purge set to match),
  and QuickBooks (retained under the finance policy). Backup interaction is confirmed in 0.7.

### Pseudonymised versus anonymised data

The trustee pack strips direct identifiers, but wherever a record stays linkable to an applicant by
reference number it is pseudonymised — still personal data under UK GDPR, and it follows the
same retention clock as its grant record. Only data that is aggregated and irreversibly stripped of
identifiers (not linkable back to a person) is treated as anonymised and kept indefinitely for
reporting. The sweep flow deletes pseudonymised monitoring data together with its parent record.

### Right to erasure

Erasure requests (UK GDPR Article 17) are handled by the same sweep flow, run on demand for
a single applicant reference.

- Locates all of an individual's data across the Grant Applications list, Trustee Packs, DocuSign,
  and QuickBooks by reference / identifier — including referees, helpers, group members, and
  emergency contacts captured with the application.
- Honours legal-hold carve-outs: data required for the 6-year Charities Act / financial duty or for
  safeguarding is retained, and the requester is told which data cannot yet be deleted —
  matching the Privacy Notice's stated position.
- Logs the request and the action taken.

### Compliance guardrails built into the design

Three constraints are designed in so the automation stays inside Revitalise's published position
and current UK law (the Data (Use and Access) Act 2025, in force 5 February 2026).

- **No solely-automated decisions on special-category data.** The scoring knockout is a flag
  only. A rejection is confirmed by Emily and that human review is logged. This preserves the
  Privacy Notice's 'humans decide' statement and the safeguards the DUAA 2025 keeps for
  decisions that use health data.
- **UK data residency.** The Power Platform environments, AI Builder, DocuSign, and
  QuickBooks Online connections are configured to keep processing within the UK, matching
  the 'no transfers outside the UK' commitment. Residency is verified during environment setup
  (0.2) and integration build.
- **Least-privilege access to health data.** Special-category fields are readable only by the
  service account and Emily's role; trustees receive the anonymised view only — enforced by
  the security model (0.5).

**Recommended DPO sign-off:** Because this touches special-category data and the DUAA
2025 rules on automated decisions, Revitalise's DPO (Rebecca Young) should confirm two
points before go-live: that logged human confirmation of every rejection satisfies their
automated-decision position, and that 6-year retention of the health free-text remains their
preference over earlier minimisation. This document sets the technical schema; it is not legal
advice.

---

## 9. Licensing

Revitalise runs Microsoft 365 Business Premium. This section sets out what that plan already
covers, what the automation needs on top of it, and the one recurring cost the design deliberately
avoids. Figures are indicative planning estimates; Revitalise qualifies for Microsoft nonprofit
pricing and should confirm all amounts against a current quote at procurement (WBS 0.2).

### What Business Premium already covers

SharePoint Online, Outlook and Teams, Power Apps, and Power Automate with standard
connectors are all included, and so are basic Purview retention labels. That covers most of the
build. Three things sit outside the plan: premium connectors, AI Builder, and event-based
retention. Each is addressed below.

### Licensing register

| Component / need | In Business Premium? | Indicative cost | Note |
|---|---|---|---|
| Power Automate — standard connectors | Yes | Included | SharePoint, Outlook, Teams, Approvals — the bulk of the flows. |
| **Power Automate Premium — service account** | No | ≈ £150–180 / yr (one account, verify) | Enables the HTTP intake trigger, DocuSign, and QuickBooks Online. One per-user licence on the service account covers every production flow, including the retention sweep. |
| AI Builder — narrative anonymisation (#5) | No | Via Copilot Credits (verify) | Standalone add-on closed to new buyers. Seeded credits are due to end 1 Nov 2026 — confirm the ongoing route before #5 goes live. |
| Basic Purview retention labels | Yes | Included | Manual / default-library labels as a time-based safety net behind the sweep flow. |
| **Event-based Purview retention** | No (E5 / add-on) | Avoided by design | Would need M365 E5 or the Purview Suite for Business Premium add-on (≈ $10 per user / month, verify). Not licensed; the sweep flow does this job instead. |
| DocuSign — acceptance signing (#3) | No (third party) | Per DocuSign plan | Procured separately; must be in place before the acceptance workflow goes live. |

### Retention enforcement: the licensing choice

Enforcing the retention schedule (Section 8) needs status-aware, event-based deletion, which
Business Premium does not provide natively. Two routes were considered:

- **Custom Power Automate sweep flow (chosen).** A one-off build that reuses the service
  account's existing Premium licence, so it adds no recurring licence cost. The effort sits in
  Phase 0 (build and test), and Revitalise owns the rules and can adjust them without a vendor.
- **Purview Suite for Business Premium add-on (not chosen).** Would enable native
  event-based retention and broader compliance tooling, but is priced per user, per month
  (≈ $10, verify) across every licensed user — a recurring cost that scales with headcount to
  serve a single automation's need.

Decision: retention and erasure are enforced by the sweep flow. The Purview Suite add-on
remains available later if Revitalise wants native records management across the wider tenant,
but it is not required for this solution.

**Indicative figures — confirm before purchase:** The amounts above are planning estimates.
Licence prices vary by agreement and change over time, and Revitalise qualifies for Microsoft
nonprofit pricing. Treat every figure marked "verify" as unconfirmed and check it against a
current Microsoft quote at procurement (WBS 0.2). The AI Builder / Copilot Credits route and the
1 November 2026 seeded-credit deadline should be confirmed before automation #5 goes live.

---

## 10. Assumptions and dependencies

- Revitalise runs Microsoft 365 Business Premium (standard connectors and SharePoint Online
  included). Premium capability is added per Section 9, not assumed in the base plan.
- A Power Automate Premium licence is procured for the service account (HTTP trigger +
  premium connectors), per Section 9.
- M365 administrator access is granted to create environments, the service account, DLP, and
  Conditional Access exceptions.
- The WordPress form plugin supports a webhook, REST API, or structured email (else the
  email/scheduled fallback applies).
- DocuSign licensing is procured before the acceptance workflow goes live.
- Narrative anonymisation (#5) runs on Copilot Credits, since AI Builder is not in Business
  Premium and its add-on is closed to new buyers. The ongoing credit route is confirmed before
  #5 goes live (seeded credits end 1 November 2026).
- Business Premium provides basic Purview retention labels; status-aware retention and erasure
  are enforced by the sweep flow (Section 8). Native event-based retention (E5 / Purview Suite)
  is not licensed.
- DocuSign and QuickBooks retention settings can be configured to match the published
  schedule; UK data residency is available for all connectors.

---

## 11. Next steps

This document unblocks the rest of Phase 0. In WBS order:

| WBS | Task | Depends on this document |
|---|---|---|
| 0.2 | Power Platform environment setup (DEV/PROD, DLP, security groups, managed solution) | Environment strategy, naming, ALM |
| 0.3 | Service account setup and credential store | Naming, identity approach |
| 0.4 | SharePoint site architecture (lists, content types, permissions) | Component map, naming |
| 0.5 | Security & permissions model | Component map, integration register |
| 0.6 | ALM & deployment runbook | Packaging & ALM strategy (Section 7) |
| 0.7 | Data governance & compliance (DPIA, record of processing) | Retention schema (Section 8), DLP stance |

*Prepared by Xander Lykopoulos · Argelis Consultancy · Architectuur tussen ambitie en IT*
