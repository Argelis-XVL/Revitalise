# Technical Architecture Document — Revitalise Grant Application Automation

**Feature Slug:** revitalise-grant-automation
**SDD Reference:** docs/plans/revitalise-grant-automation-plan.md (APPROVED 2026-08-10)
**Date:** 2026-08-10
**Status:** APPROVED
**Revision:** rev 1 — 2026-08-10. Reviewer decisions applied to ADR-003 (Code App confirmed), ADR-006
(three environments: DEV, TST/ACC, PRD), §6.1 (group-team pattern confirmed), §6.5 (audit retention
confirmed at 6 years), role-membership review cadence (confirmed at 6 months), and §4.2 (SAR mechanism
reframed as a proposal and carried forward as an accepted open item).
**Revision:** rev 2 — 2026-08-12. **ADR-007 closed to Power Platform Pipelines** by explicit reviewer
decision, superseding this TAD's own recommendation of pac CLI + GitHub Actions; §9.2 rewritten as the
GitHub-Actions/Pipelines responsibility boundary; **ADR-021 added**, resolving C-TECH-044 to a GitHub OIDC
federated credential with **one deploy identity per environment** (three app registrations, one federated
credential each); §6.7 and the §6 security table corrected (the deploy registrations are required either
way); **§12 gains four tenant prerequisites** — a custom pipelines host, pipeline/stage configuration,
Managed Environment status on TST/ACC and PRD (a licence cost), and pipelines access assignment. §9.1 and
ADR-006 are unaffected: the topology is unchanged and there are still two promotion hops.
**Revision:** rev 3 — 2026-08-27. **SDD Amendment A-05** (`wbs:6.3`). §3.1 gains the **five new
`…redacted` counterpart columns** on `rev_application` (delta TAD `ADR-031`) and explicit rows for the
financial-eligibility, benefit/employment and helper-context columns FR-035 now surfaces. §7's **NFR-001
row is corrected** — it named the two condition profiles as members of `REV_TrusteeRestricted` and they
are not, and never were (A-05 Finding 3; verified live in DEV 2026-08-27). §7's **NFR-003 row is
strengthened** by `ADR-032`: the trustee portal never selects a secured column at all, so FR-078's
restricted state is rendered rather than queried. **No column's classification, `IsSecured` value or
profile membership changes in this revision** — the five new columns are additions, and the two
corrections describe what was already true. The full design is in the delta TAD,
`docs/architecture/trustee-portal-visual-refresh-architecture.md` **Revision 3**, §3.2.2 and §3.2.3.
**Revision:** rev 4 — 2026-09-06. **CO-002 scope decision** (`wbs:3.2`, no new WBS task): the four
DocuSign Grant Referee (Signer 2) anchor tabs Title/Address/Town-City/Postcode are **not** modelled
in Dataverse — `rev_application` gains no `referee_*` columns, no referee entity is created, and
automation #1's intake form gains no referee-facing step. §5.8–5.10 and **ADR-043** record the
decision and its basis. No column's classification or the data model in §3.1 changes.
**Revision:** rev 5 — 2026-09-09. **§3.5 conflict 2 RESOLVED — the payment capture form is
authorised** (`wbs:8.3`), by reviewer approval of `docs/plans/revitalise-payment-capture-plan.md`
(FR-150–FR-154, NFR-150, US-030). The **form** half of Automation #8 now has requirements behind
it; the **`REV | Finance | Capture Payment` flow** does not, and stays unauthorised and unbuilt —
§3.5 and §5.11 state the split. §3.1's `rev_bankaccount` and `rev_payment` blocks gain the
**lookup-name-projection** consequence of `C-TECH-070`(3) and the previously omitted column
`rev_payment.rev_paymentstatus`. §6.1's **Finance persona App Access changes to a separate
model-driven app** (`ADR-044`); §6.2's Finance role row gains the **Grant and Provider privileges
FR-150/FR-151 require and the approved row omitted**. §9 and §12 gain the new app module and its
two per-environment configuration rows. **`ADR-044`–`ADR-047` added.** **No column is added,
altered or reclassified, no `IsSecured` value changes and no profile membership changes in this
revision** — the surface binds columns WBS 8.1 already delivered. Acceptance of `wbs:8.3` is
gated on `wbs:8.2` (the Finance security role, which does not exist) — see `ADR-047` and §6.2.1.
**Revision:** rev 6 — 2026-09-09. **Reviewer decisions on the rev-5 gate applied.** (1) **`ADR-044`
is REJECTED by the reviewer** — the finance surface is **not** a separate app; it is an area inside
the existing `REV Grant Administration` model-driven app, which is what §6.1's approved App Access
cell always said. `ADR-044` is retained with `Status: Rejected` and superseded by **`ADR-048`**,
which records the area design and the defence-in-depth this choice gives up. §6.1's cell is
**restored**; §9.4, §12.1, §12.2 and Appendix A are re-derived from the area design, not
patched. (2) **§6.2's two Finance-role privilege corrections are CONFIRMED** by the reviewer
(Provider: add Create; Grant: add Read + AppendTo) — §6.2 and §6.2.1 items 2 and 3 are unchanged in
content and now read *confirmed* rather than *flagged for confirmation*. (3) **The
`REV | Finance | Capture Payment` flow is OPEN, DEFERRED BY REVIEWER DECISION** — not authorised,
not descoped, not resolved; §3.5 conflict 2, §5.11 and risk **A-R56** carry it in that state and no
task is opened for it. **`wbs:8.3`'s evidence rule in `contract/evidence-map.json` is now wrong**:
it names a separate app directory that this revision has decided will never exist. The corrected
rule is specified in §9.4 for `pm-agent`, which owns that file. **No column is added, altered or
reclassified, no `IsSecured` value changes and no profile membership changes in this revision.**
**Revision:** rev 7 — 2026-09-10. **`ADR-046` corrected against what shipped, and SDD OQ-151
resolved as far as architecture may resolve it** (`wbs:8.3`; test report **D-02**, TC-07/TC-08).
(1) **`ADR-046`'s Decision named two interventions and its own Consequences named one.** The
shipped Bank Account form carries one — the column `<Description>` — so the Decision is amended to
one and the *"labelled instruction beside the control"* half is **struck, not deferred**: it never
shipped, it has no ground-truthed shape in this solution (no shipped form here contains a
label-only cell or a WebResource control), and it would add nothing the description does not.
(2) **`ADR-046a` is added**, stating the FR-154 naming convention for **both** payee types — the
provider case the shipped description already illustrated, and the **applicant reimbursement** case
it was silent on, which is the only case FR-154 exists for. The applicant convention is the **grant
reference**, derived from `ADR-013`'s existing pseudonymous reference rather than invented. It
carries a description-only build specification for `development-agent`. (3) **SDD OQ-151 is
re-scoped and re-dated, not silently answered**: its architectural half is closed by `ADR-046a`; the
business half narrows to *confirm-or-replace* and moves from the unmeetable *"before build"* to
**before `wbs:8.2` deploys** — the date the exposure actually becomes live. (4) **A new §12.2 row
names a contract this ADR had been assuming**: whether Unified Interface renders a
column description as visible help text or only as a hover tooltip. As a tooltip, FR-154's shipped
control is effectively nothing, and that is now stated rather than implied. **No column is added,
altered or reclassified, no `IsSecured` value changes and no profile membership changes in this
revision** — the one source change specified is a `<Description>` edit.

**Revision:** rev 8 — 2026-09-10. **Reviewer confirmed `ADR-046a`'s applicant-reimbursement nickname
convention as proposed.** The business half of SDD OQ-151 that rev 7 re-scoped to *confirm-or-replace*
is answered: the convention ships as designed — `REV-2026-001 - reimbursement` (the grant reference,
per `ADR-013`), no replacement. `ADR-046a`'s Status line and Consequences are updated from *pending
confirmation* to *reviewer-confirmed*, and **SDD OQ-151 is closed**, not merely re-scoped: Appendix A's
traceability row now records the confirmation and its date rather than an open due date. No source,
schema or build specification changes — `ADR-046a`'s build specification for `development-agent`
already matched what is now confirmed.

---

> **Source:** adopted from `docs/Import/Revitalise-Solution-Architecture-v0.4.docx` on 2026-08-10 by architect-agent (intake mode).
> Original author: Xander Lykopoulos — Argelis Consultancy (v0.4 Draft for review, 14 July 2026, revised 15 July 2026).
> Read via a plain-text extraction of the same content. See Adoption Report in gate log.
>
> **Supporting source — authoritative for §6 Security Design and §6.1** (received 2026-08-10):
> - `docs/Import/Revitalise-Security-Model-v0.1.docx` — Security Model v0.1, 15 July 2026 (Draft, WBS 0.5).
>   This is the deliverable the Solution Architecture named but left to be written; §6 adopts it in preference
>   to the architecture's summary treatment wherever the two differ in detail.
>
> **Cited for context only** (not adopted as TAD content — see the user's scope decision recorded in the Adoption Report):
> - `docs/Import/Revitalise-ALM-Runbook-v0.1.docx` — cited in §9 for the promotion procedure and connection-reference / environment-variable inventory.
> - `docs/Import/Revitalise-Data-Governance-Framework-v0.2.docx` — cited in §3 for cascade-delete behaviour and the classification tiers, cross-checked against SDD §7.1/§7.6.
> - `docs/Import/Revitalise-DPIA-v0.1.docx`, `docs/Import/Revitalise-RoPA-v0.1.docx` — already adopted into SDD §7; cited in §11 only.
> - `docs/Import/Revitalise-Governance-Runbook-v0.1.docx` — day-2 operations; not TAD content.
>
> ⚠️ **Reader's note — three gates sit above this document.**
> 1. **DPO sign-off (SDD OQ-004/005/006)** gates build on the field-level-security basis this TAD adopts.
>    ADR-002 is `Adopted (conditional)` for that reason.
> 2. **WBS 0.3 — the service account `svc-grantautomation` and its scoped Conditional Access exception — is
>    outstanding with Wanstor** (SDD OQ-018). Every unattended automation in §5 depends on it. It is carried
>    forward as a blocking dependency in §12.
> 3. **Resolved at the architecture gate on 2026-08-10 (Xander Lykopoulos):** the trustee portal is a
>    **Code App** and Canvas App is descoped (ADR-003, now `Adopted`); the environment topology is
>    **three environments — DEV, TST/ACC, PRD** (ADR-006, now `Adopted`); the §6.1 group-team binding
>    pattern is confirmed as derived. Audit retention is confirmed at 6 years and the role-membership
>    review cadence at 6 months.
> 4. ~~**Two decisions remain open and are not blocking this gate:** the ALM tooling (ADR-007) and the
>    intake channel / endpoint-trust route (ADR-011).~~ → **ADR-007 IS NOW CLOSED (2026-08-12):
>    Power Platform Pipelines, by explicit reviewer decision, superseding this TAD's own recommendation
>    of pac CLI + GitHub Actions.** See §9.2 and ADR-007. It brings **two new tenant prerequisites**
>    (a custom pipelines host; Managed Environment status on TST/ACC and PRD, which carries a licence
>    cost) — both added to §12. **ADR-011 remains open.** ADR-021 was added at the same time, resolving
>    C-TECH-044 to a GitHub OIDC federated credential with one deploy identity per environment.
> 5. **One accepted open item** carried forward to development-agent: no SAR extract mechanism is built or
>    agreed. §4.2 records a *proposed* approach only. Accepted as a known gap by the reviewer on
>    2026-08-10 (C-DOM-005, SOFT).
>
> ⚠️ **Knowledge-base gap.** `knowledge/domain/data-entities.md`, `knowledge/domain/compliance-requirements.md`,
> `knowledge/technology/stack-overview.md` (Publisher Convention), `platform.md`, `dataverse.md` (column-security
> profile table), `build-and-deploy.md`, `entra-id.md`, `sharepoint.md` and `teams.md` are unpopulated template
> placeholders in this repository. No project-specific technology decision was taken from them. The one exception
> is **`knowledge/technology/security-model.md`, which IS populated** — its Group Teams pattern and Canonical
> Persona Mapping are real platform decisions and §6.1 is built on them. Where a placeholder file left a gap,
> this TAD relies on the source documents plus general Power Platform practice and says so at the point of use.
> Carried forward from SDD OQ-029.

---

## 1. Architecture Overview

The solution automates the grant journey from application submission to trustee decision and signed
acceptance on the Microsoft 365 / Power Platform stack Revitalise already owns. It automates the **data
handling, not the decision-making**: scoring is automatic with the process owner's oversight and override,
and trustees make the funding decision.

**Dataverse is the system of record and the integration hub.** Applications land in Dataverse, every
automation reads from and writes to it, and external systems never talk to each other directly. One
document — the signed DocuSign PDF — lives outside Dataverse, in a SharePoint library, linked by URL from
the Grant record.

### 1.1 Architecture principles (adopted from source §2)

| Principle | What it means here |
|---|---|
| Low-code, no custom code | Power Automate cloud flows, Power Apps and Dataverse configuration only. No macros, no scripts on anyone's laptop. |
| Maintainable by non-developers | Thresholds, templates and mappings live in configuration — a Dataverse `Setting` table plus environment variables — so the process owner can adjust them without editing a flow (NFR-019). |
| Cloud-native and portable | Data lives in Dataverse. No local file dependency, no "single source of truth on one laptop". |
| AI only where it earns its place | AI Builder redacts only the free-text narratives a trustee must read. Structured identifiers are hidden by column security, not by AI. |
| Governed foundation first | Environments, DLP, service identity, the data model and its security roles, naming and ALM are established before any automation is built, so every later component inherits a controlled structure. |

### 1.2 Why this design — and what was rejected

| Chosen | Rejected alternative | Why |
|---|---|---|
| Dataverse as system of record | SharePoint lists (the v0.3 baseline) | Relational integrity, cascade delete, native status-aware bulk-delete retention, column-level security and native field-change auditing. SharePoint could not enforce the retention schedule or the trustee control. Cost: Dataverse is a premium data source, so per-user premium entitlements are needed (ADR-001). |
| Field-level (column) security for trustee anonymisation | Manual anonymisation by one person per board cycle | Removes 3–4 hours per cycle and removes the single-missed-name breach risk. It is a *stronger but different* control, so it is gated on DPO sign-off (ADR-002). |
| Native Dataverse bulk delete + cascade | Custom retention sweep flow; Purview Suite event-based retention | Native, status-aware, configured once, logged as a system job, no extra licence. A light helper flow covers only what the native job cannot reach (ADR-004, ADR-005). |
| **Code App** for the trustee portal | Canvas App (out-of-palette, **rejected**); Model-Driven App; Power BI report; static mail-merged Word pack | Live secured data, decision capture written back to the Review table, no Power BI Pro licence. **Application type confirmed as a Code App by the reviewer on 2026-08-10 — ADR-003.** |
| Single solution, DEV → PROD as managed | Editing in production | One version number describes the live system; rollback is re-importing the prior managed package (§9). |

### 1.3 Solution boundary

Everything inside the Microsoft 365 tenant ships in **one Power Platform solution**,
`RevitaliseGrantAutomation`, publisher prefix `rev`. Four systems sit outside that boundary and are reached
through connectors: the **WordPress / Gravity Forms website** (application intake), **DocuSign** (acceptance
signatures), **QuickBooks Online** (duplicate-grant checks), and **SharePoint Online** (the signed-PDF
library, inside the tenant but outside the Dataverse store).

> **Naming conventions are adopted from source §4 unchanged**: publisher prefix `rev`; solution
> `RevitaliseGrantAutomation`; environments `Revitalise – Grant Automation (DEV)` / `(PROD)`; flows
> `REV | <Automation> | <Action>`; tables singular PascalCase; connection references `rev-<Service>`;
> environment variables `rev_<Purpose>`; service account `svc-grantautomation@revitalise.org`.
> `knowledge/technology/stack-overview.md` → Publisher Convention is an unpopulated placeholder; it should be
> populated with `rev` / `RevitaliseGrantAutomation` so downstream agents derive schema names consistently.

---

## 2. Component Diagram

### 2.1 Context diagram (C4 L1)

```mermaid
graph LR
  APP["Applicant / helper"] -->|"completes form"| WP["WordPress + Gravity Forms<br/>(external, out-of-palette)"]
  WP -->|"webhook / REST pull"| SYS["Revitalise Grant Automation<br/>(Power Platform solution)"]
  EMILY["Process owner (Emily)<br/>REV Admin"] -->|"reviews, overrides, finalises"| SYS
  FIN["Finance staff<br/>REV Finance"] -->|"records payments"| SYS
  TRU["Trustees<br/>REV Trustee"] -->|"reads redacted case, records verdict"| SYS
  SYS -->|"envelope, reminders"| DS["DocuSign<br/>(external)"]
  DS -->|"completion event, signed PDF"| SYS
  SYS -->|"read-only query"| QBO["QuickBooks Online<br/>(external)"]
  SYS -->|"signed PDF"| SPO["SharePoint Online<br/>signed-acceptance library"]
  SYS -->|"notifications, summaries, alerts"| TEAMS["Microsoft Teams / Outlook"]
  SYS -->|"PII detection call"| AIB["AI Builder<br/>prebuilt PII model"]
  SIGN["Referee / GP"] -->|"second signature"| DS
```

### 2.2 Component diagram (C4 L2)

```mermaid
graph TB
  subgraph EXP["Experience layer"]
    FORM["Application form<br/>WordPress / Gravity Forms<br/>OUT-OF-PALETTE"]
    PORTAL["Trustee portal<br/>Code App (confirmed)<br/>ADR-003"]
    MDA["Grant Administration app<br/>Model-Driven App"]
    PAYFORM["Payment capture surface<br/>MDA form, finance role"]
  end
  subgraph ORCH["Orchestration layer — Power Automate"]
    F1["REV | Intake"]
    F2["REV | Scoring | Calculate & Flag"]
    F3["REV | Scoring | Daily Summary"]
    F4["REV | Duplicate | QBO Check"]
    F5["REV | Narrative | Scrub Free-Text"]
    F6["REV | Narrative | Trustee Pack (derived)"]
    F7["REV | Portal | Finalise Decisions"]
    F8["REV | Acceptance | Create Envelope"]
    F9["REV | Acceptance | Reminders & Escalation"]
    F10["REV | Acceptance | Completion"]
    F11["REV | Finance | Capture Payment"]
    F12["REV | Retention | Retention & Erasure Helper"]
    F13["REV | Ops | Failure Alert (child)"]
  end
  subgraph DATA["Data layer — Dataverse"]
    T["Applicant · Application · Review · Grant<br/>Provider · BankAccount · Payment<br/>AnonymisedStatistic · ErrorLog · Setting"]
    CSP["Column security profile<br/>REV_TrusteeRestricted"]
    BD["Recurring bulk-delete jobs<br/>6y / 12m / 6m + orphan sweep"]
  end
  subgraph GOV["Identity & governance"]
    ENTRA["Entra ID groups<br/>env + role groups"]
    SVC["svc-grantautomation<br/>+ CA exception"]
    DLP["Environment DLP policy"]
    AUD["Native field-change auditing<br/>+ app-access logging"]
  end

  FORM --> F1
  F1 --> T
  T --> F2 --> T
  F2 -.-> F4
  F3 --> TEAMS2["Teams / Outlook"]
  T --> F5 --> AIB2["AI Builder"]
  F5 --> T
  F6 --> WORD["Word Online (Business)"]
  PORTAL --> T
  MDA --> T
  PAYFORM --> T
  PORTAL --> F7 --> T
  F7 --> F8 --> DS2["DocuSign"]
  DS2 --> F10 --> SPO2["SharePoint library"]
  F9 --> DS2
  F11 --> T
  F4 --> QBO2["QuickBooks Online"]
  F12 --> T
  F12 --> DS2
  BD --> T
  CSP --> T
  F1 -.->|"on error"| F13
  F2 -.->|"on error"| F13
  F5 -.->|"on error"| F13
  F8 -.->|"on error"| F13
  F13 --> T
  ENTRA --> GT["Dataverse group teams<br/>carry security roles"]
  GT --> T
  SVC --> ORCH
  DLP --> ORCH
  AUD --> T
```

### 2.3 Sequence — happy path, submission to signed acceptance

```mermaid
sequenceDiagram
  participant A as Applicant
  participant W as WordPress form
  participant I as REV Intake flow
  participant D as Dataverse
  participant S as REV Scoring flow
  participant E as Process owner
  participant N as REV Narrative flow
  participant AI as AI Builder
  participant T as Trustee portal
  participant P as REV Finalise Decisions
  participant DS as DocuSign
  participant SP as SharePoint

  A->>W: Completes validated form (FR-001..FR-006)
  W->>I: Webhook POST (fallback: scheduled REST pull)
  I->>D: Create Application + Applicant, assign reference (FR-007, FR-008)
  I->>E: Teams notification, name + reference (FR-009)
  D-->>S: Row created trigger
  S->>D: Score 0-60, status, income flag (FR-011..FR-016)
  S->>E: Borderline routed for review (FR-019, FR-022)
  E->>D: Reviews / overrides, marks eligible for panel (FR-018)
  D-->>N: Row updated trigger
  N->>AI: Detect PII in free-text narrative
  AI-->>N: Entities + confidence
  N->>D: Write redacted narrative; flag if below threshold (FR-026..FR-029)
  E->>D: Reviews and releases flagged redactions (FR-030)
  T->>D: Trustee reads redacted case, column security filters identity (FR-034..FR-038)
  T->>D: Records Approve / Defer / Reject (FR-037)
  E->>P: "Finalise decisions"
  P->>D: Apply verdicts, create Grant rows, write anonymised snapshot (FR-040, FR-055)
  P->>DS: Create envelope, dual signature in sequence (FR-041, FR-042)
  DS->>DS: Reminders day 3 and 7; escalate day 14 (FR-043, FR-044)
  DS-->>SP: Signed PDF stored, URL written to Grant (FR-045)
```

---

## 3. Data Model

Ten Dataverse tables (the source's seven personal/process tables, plus the Anonymised Statistic snapshot,
the Error Log, and the Setting configuration table), one SharePoint document library, and no other store.
Classification uses the four-tier scale in `skills/data-classification.md`, cross-referenced to the
UK GDPR tier used by SDD §7.1, the Security Model §3 and the Data Governance Framework §3 (all three agree).

### Entities

| Entity | Table | Purpose | UK GDPR tier (source) | Classification (`skills/data-classification.md`) | Retention (C-DOM-003) |
|---|---|---|---|---|---|
| Applicant | `rev_applicant` | The person, stored once; carries the pseudonymised ID | Special category + personal | **Tier 4 — Restricted** | Deleted with its last Application (derived orphan sweep — see §3.4) |
| Application | `rev_application` | The spine: one row per submission; folds support recipient, helper, group, referee, emergency contact | Special category + personal | **Tier 4 — Restricted** | 6 years from final payment (Grant Paid) / 12 months from decision (Rejected) / 6 months from last contact (Withdrawn, Incomplete) |
| Review | `rev_review` | One row per monthly panel attempt; trustee verdicts | Pseudonymised + staff identity | **Tier 3 — Confidential** | Cascade with Application |
| Grant | `rev_grant` | Created on success; folds acceptance and impact report; links the signed PDF | Personal + financial | **Tier 4 — Restricted** | Cascade with Application (6 years) |
| Provider | `rev_provider` | Reusable holiday providers | **Not classified in any source** | **Tier 2 — Internal (DERIVED — see §3.2)** | Reference data; retained while active, reviewed annually. No personal-data clock. |
| Bank Account | `rev_bankaccount` | Every account paid into, held once; finance role only | Personal — financial | **Tier 4 — Restricted** | Cascade with Applicant. Earlier purge after payment reconciliation is an open decision (§3.4) |
| Payment | `rev_payment` | Disbursements; the duplicate check matches these rows | Personal — financial | **Tier 4 — Restricted** | Cascade with Grant. The QuickBooks financial record is retained separately under the finance policy (FR-050) |
| Anonymised Statistic | `rev_anonymisedstatistic` | Non-personal outcome snapshot, no identifiers, never linked back | Anonymised — not personal data | **Tier 2 — Internal** | Indefinite (FR-055) |
| Error Log | `rev_errorlog` | Operational failure capture across all flows | Operational — non-personal | **Tier 2 — Internal** | 90 days (DERIVED — source says only "short operational retention") |
| Setting | `rev_setting` | Thresholds, Likert point map, redaction threshold, income ceiling — editable by the process owner | Non-personal configuration | **Tier 2 — Internal** | Indefinite; changes audited |
| Round Finance | `rev_roundfinance` | Trustee Portal Visual Refresh (delta TAD, ADR-028, WBS 6.9): one row per review round — the round's open/close calendar and its charity-level finance figures, entered by hand. No relationship to any other table; scopes no application visibility | Non-personal, no data subject | **Tier 2 — Internal** | Indefinite. Not personal data — out of scope of erasure (FR-051) and subject access (FR-053) |
| Round Statistics Request | `rev_roundstatisticsrequest` | Trustee Portal Visual Refresh (delta TAD Revision 5, ADR-038, section 3.9, WBS 6.9): one row, ever — the trustee's ask for a fresh round-statistics computation. Reduced to the ask from Revision 5: three columns (`rev_status`, `rev_resultjson`, `rev_computedon`) are unused and stay declared with superseding descriptions rather than deleted, see delta TAD section 3.9.2. No relationship to any other table | Non-personal, no data subject | **Tier 2 — Internal** | Indefinite. Not personal data — out of scope of erasure (FR-051) and subject access (FR-053) |
| Round Statistics Result | `rev_roundstatisticsresult` | Trustee Portal Visual Refresh (delta TAD Revision 5, ADR-038, section 3.9, WBS 6.9): one row, ever — the flow's answer to the round-statistics ask, split off `rev_roundstatisticsrequest` so a trustee's Write privilege on the ask can never reach the answer. No relationship to any other table | Non-personal, no data subject | **Tier 2 — Internal** | Indefinite. Not personal data — out of scope of erasure (FR-051) and subject access (FR-053) |
| Grant History *(conditional)* | `rev_granthistory` | QuickBooks cross-reference fallback only — see ADR-017 | Personal | **Tier 3 — Confidential** | 6 years, aligned to the QBO financial record |

### 3.1 Key attributes and the controls each carries

Only attributes that drive a control, a requirement or a relationship are listed. Every table additionally
carries the platform columns required by `knowledge/technology/dataverse.md`: `rev_name` (primary),
`createdon`, `createdby`, `modifiedon`, `modifiedby`, `statecode`, `statuscode`.

**`rev_applicant` — Tier 4**

| Attribute | Type | Classification | Control |
|---|---|---|---|
| `rev_name` | Autonumber `REV-A-00001` | Tier 2 | **Primary name column is the pseudonymised ID, never the person's name** (ADR-013) |
| `rev_fullname` | Text | Tier 4 | Column security: `REV_TrusteeRestricted` — Admin + Service only |
| `rev_email`, `rev_phone` | Text | Tier 4 | Column security — Admin + Service only |
| `rev_addressline`, `rev_postcode` | Text | Tier 4 | Column security — Admin + Service only |
| `rev_dateofbirth` | Date | Tier 4 | Column security — Admin + Service only |
| `rev_agerange` | Choice | Tier 3 | Derived from DOB at intake; trustee-visible (FR-027) |
| `rev_locationarea` | Choice | Tier 3 | Derived from postcode at intake; trustee-visible (FR-027) |
| `rev_ethnicgroup` | Choice | Tier 4 (Art. 9) | Column security. **Only if actually captured — SDD OQ-027 open** |
| `rev_lastcontactdate` | Date | Tier 2 | Drives the 6-month withdrawn/incomplete retention clock |

**`rev_application` — Tier 4**

| Attribute | Type | Classification | Control |
|---|---|---|---|
| `rev_name` | Autonumber, reference | Tier 2 | **Format conflict — see §3.5.** SDD FR-008 requires `REV-YYYY-NNN`; source §4 specifies `GA-2026-00001` |
| `rev_applicantid` | Lookup → Applicant | — | Parental, cascade delete |
| `rev_submittedon` | DateTime (UTC) | Tier 2 | FR-008 |
| `rev_status` | Choice | Tier 2 | Submitted · Auto-pass · Borderline · Auto-reject · Under Review · Eligible for Panel · Approved · Rejected · Withdrawn · Incomplete · Grant Paid. Drives every retention clock (FR-048) |
| `rev_circumstancescore` | Whole number 0–60 | Tier 3 | Written by the scoring flow only; trustee-visible (FR-011) |
| `rev_scorebreakdown` | Multiline text | Tier 3 | Trustee-visible; evidences the score (FR-035) |
| `rev_incomeflag` | Choice | Tier 3 | Separate from the circumstance score (FR-015) |
| `rev_statusoverridden`, `rev_overriddenby`, `rev_overriddenon`, `rev_overridereason` | Bool / Lookup / DateTime / Text | Tier 2 | Named human accountability for every outcome (FR-018) |
| `rev_wellbeinganswer1..n`, `rev_incomeband`, `rev_financialanswers` | Choice / Text | Tier 3 | Trustee-visible; the only inputs to the score (FR-013, FR-016) |
| `rev_narrativeraw`, `rev_otherconditionraw` | Multiline text | **Tier 4 (Art. 9)** | Column security — **Admin + Service only. Never reaches a trustee** (FR-031, NFR-001) |
| `rev_narrativeredacted` | Multiline text | Tier 3 | Written by the narrative flow; trustee-visible (FR-026) |
| `rev_redactionconfidence` | Decimal | Tier 2 | Compared against the `Setting` threshold, initially 85% (FR-029, NFR-017) |
| `rev_redactionreviewrequired`, `rev_redactionreleased` | Bool | Tier 2 | Human-in-the-loop gate; trustee visibility requires `released = true` (FR-029, FR-030) |
| `rev_conditionprofile` | Multi-select choice | Tier 4 (Art. 9) | **Trustee-visible by design** — condition is relevant, identity is not (Security Model §5) |
| `rev_supportrecipientname`, `rev_helpername/email/phone`, `rev_refereename/email/phone`, `rev_emergencycontactname/phone` | Text | Tier 4 | Column security — Admin + Service only. Referee and emergency contact are **DERIVED** into the profile; the source names only helper and support-recipient identity |
| `rev_supportrecipientconditionprofile` | Multi-select choice | Tier 4 (Art. 9) | Trustee-visible, identity hidden (Security Model §5) |
| `rev_grouplinkage` | Text / Lookup | Tier 3 | Trustee-visible |
| `rev_breakstart`, `rev_breakend`, `rev_amountrequested`, `rev_costs` | Date / Currency | Tier 3 | Trustee-visible (FR-028, FR-034) |
| `rev_duplicateflag`, `rev_priorgrantref`, `rev_priorgrantdate`, `rev_priorgrantamount`, `rev_duplicatecheckedon` | Bool / Text / Date / Currency / DateTime | Tier 3 | FR-023, FR-024, FR-025. Visible to Finance on the record (US-015 AC-3) |
| `rev_decisiondate` | Date | Tier 2 | Drives the 12-month rejected clock |
| `rev_eligibleforround`, `rev_reviewround` | Bool / Text | Tier 2 | Scopes trustee visibility to the current round (FR-038) |
| `rev_sourcesubmissionid` | Text, alternate key | Tier 2 | **Idempotency guard on intake** — a replayed webhook cannot create a second row (§5.1) |
| `rev_caresupportdescriptionredacted`, `rev_careprovidedexampleredacted`, `rev_othercareprovidedtyperedacted` | Multiline text | Tier 3 | **Trustee Portal Visual Refresh (delta TAD, ADR-027 amended, WBS 6.3).** Redacted counterparts of the three secured columns immediately below; trustee-visible once `rev_redactionreleased` is true. `IsSecured=0` — same class as `rev_narrativeredacted`. Written by `REV \| Narrative \| Scrub Free-Text` once extended (Automation #5, deferred); empty on every row until then |
| `rev_careprovidedexample`, `rev_caresupportdescription`, `rev_othercareprovidedtype` | Multiline text | **Tier 4** | Column security: `REV_TrusteeRestricted` — Admin + Service only. Unchanged by the redacted counterparts above — the source free text stays secured (ADR-027) |
| `rev_unabletofundexplanationredacted`, `rev_exceptionalfundingdetailredacted`, `rev_otherexceptionalcircumstanceredacted`, `rev_otherconditionredacted`, `rev_supportrecipientotherconditionredacted` | Multiline text | Tier 3 | **SDD Amendment A-05 / delta TAD ADR-031, `wbs:6.3`.** Redacted counterparts of the five secured free-text columns immediately below; trustee-visible once `rev_redactionreleased` is true (FR-079). `IsSecured=0` — same class as `rev_narrativeredacted`. Written by `REV \| Narrative \| Scrub Free-Text` once extended (Automation #5, deferred); empty on every row until then |
| `rev_unabletofundexplanation`, `rev_exceptionalfundingdetail`, `rev_otherexceptionalcircumstance`, `rev_supportrecipientotherconditionraw` | Multiline / text | **Tier 4** | Column security: `REV_TrusteeRestricted` — Admin + Service only, **verified live 2026-08-27**. Unchanged by the counterparts above; the source free text stays secured (ADR-031). `rev_otherconditionraw` carries the same control and is listed with `rev_narrativeraw` above |
| `rev_receivesbenefits`, `rev_benefitprovider`, `rev_employmentstatus` | Choice / Text | **Tier 4 (Art. 9)** | Column security: `REV_TrusteeRestricted` — Admin + Service only, verified live 2026-08-27. Named on the trustee detail screen by FR-035 (A-05) and rendered as a **restricted state**, never a value: the app selects none of them (FR-078, ADR-032) |
| `rev_savingsover6000` | Choice / Bool | Tier 3 | `IsSecured=0`. Trustee-visible by design (FR-035, A-05) — financial eligibility context, alongside `rev_incomeflag` and `rev_incomeband` above |
| `rev_helperorganisation`, `rev_helperrelationship`, `rev_helperdeclarationconsent`, `rev_helperdeclarationconsentdate` | Text / Choice / Bool / Date | Tier 3 | `IsSecured=0`, and deliberately so — helper *context* is not helper *identity*. Trustee-visible (FR-035, A-05). The helper's name, email and phone are Tier 4 and listed above |

**`rev_review` — Tier 3:** `rev_name` (`REV-R-00001`), `rev_applicationid` (parental), `rev_paneldate`,
`rev_round`, `rev_trustee1`/`rev_trustee2` (lookup → systemuser), `rev_verdict1`/`rev_verdict2`
(Approve · Defer · Reject), `rev_notes1`/`rev_notes2`, `rev_staffrecommendation`, `rev_outcome`,
`rev_nonqualificationreason` (Choice: Circumstance score below threshold · Applicant under 18 ·
Applicant not UK-based · Other — see note below), `rev_finalisedon`. Trustees write verdict and
notes only (FR-037); all other columns are read-only to them.

> **AMENDMENT (PROPOSED), 2026-08-16 — `rev_nonqualificationreason` added.** Not part of the
> originally approved TAD; added from the Dev Summary's Task 2 raw-export audit
> (`revitalise-grant-automation-dev-summary.md`, "Finding 2"). The charity's own back-office
> export (raw column 8, "Reason for Non-Qual") has no home anywhere in the approved design — not
> in the already-built Phase 1 scoring engine, and not in `rev_review` as originally specified.
> Placed here on the reviewer's explicit instruction ("keep that together") rather than as a new
> column on `rev_application`, alongside the *staff-facing* `rev_outcome`/`rev_notes1`/`rev_notes2`
> this table already carries. **Two things this does NOT do, flagged for whoever builds Automation
> #6 / Phase 3:** (1) it does not build an automated capture path — nothing in the Phase-1 scoring
> flow writes this column yet, so age- and UK-residency-based non-qualification still has no
> automated check at all (only the score-threshold case is inferable from
> `rev_circumstancescore`/`rev_scorebreakdown`); (2) the three option values given are a
> reasonable first cut from the charity's own annotation ("too low overall circumstance score, age
> being under 18, location of applicant not in the UK") and are a PLACEHOLDER in the same sense as
> `rev_title`/`rev_breaktype`/etc. — confirm with the process owner before Phase 3 build.

**`rev_grant` — Tier 4:** `rev_name` (`GR-2026-00001`), `rev_applicationid` (parental),
`rev_providerid` (referential), `rev_amountawarded`, `rev_status` (Awarded · Acceptance Issued ·
Acceptance Signed · Paid), `rev_holidaystart`/`rev_holidayend`, `rev_conditions`,
`rev_docusignenvelopeid`, `rev_acceptanceissuedon`, `rev_acceptancesignedon`, `rev_signedpdfurl`,
`rev_manualacceptancerecorded` + `rev_manualacceptancenote` (FR-046), `rev_impactreport`,
`rev_finalpaymentdate` (starts the 6-year clock).

**`rev_provider` — Tier 2 (derived):** `rev_name` (provider organisation name), `rev_contactemail`
and `rev_contactphone` (**role-based mailbox / switchboard only — see §3.2**), `rev_addressline`,
`rev_region`, `rev_active`.

**`rev_bankaccount` — Tier 4:** `rev_name` (account nickname / masked last four — **never the full
account number**), `rev_applicantid` (parental), `rev_accountholdername`, `rev_sortcode`,
`rev_accountnumber`, `rev_active`. **Every column except `rev_name` sits in the `REV_FinanceOnly`
column security profile** — `rev_name` is this table's primary name attribute, and Dataverse does not
permit field-level security on a primary name under any circumstances (0x8004f501, ground-truthed
2026-08-23 against a live create call; see §6's note below the security table). This is a platform
limit with no privacy consequence: the value is never the full account number. The Admin role has no
table privilege at all on this table regardless, so this remains defence in depth (NFR-002).
Also `rev_providerid` (referential) and `rev_payeetype` — **7 of this table's 8 columns are
`IsSecured=1`**, every one except `rev_name`.

> **Amended rev 5 (`wbs:8.3`, FR-154) — the "no privacy consequence" sentence above is true only
> while a convention nothing enforces is followed, and WBS 8.3 builds the surface where the value
> is typed.** `rev_name` is plain text, `ApplicationRequired`, 100 characters, and it is
> **projected onto every Payment row** through `rev_payment.rev_bankaccountid`: a lookup's
> automatic `<lookup>name` companion reports `CanBeSecuredForRead=False`, so securing the lookup
> hides the GUID and never the text (`C-TECH-070`(3)). For a *provider* account a nickname is
> naturally non-identifying ("Sunrise Lodge - main"); for an **applicant reimbursement** account
> the natural thing to type is the applicant's name, and that would attribute a bank account to a
> named person for every holder of Read on Bank Account **or** Payment. FR-154 forbids it,
> `ADR-046` states plainly that the control is documentation rather than enforcement, and
> **`ADR-046a` (rev 7, reviewer-confirmed rev 8) states the convention itself for both payee types —
> the grant reference for an applicant reimbursement account, the organisation name for a provider
> account.** *Previously read (rev 5): "SDD OQ-151 asks the business for the convention to use
> instead" — rev 7 re-scoped that to a confirm-or-replace due before `wbs:8.2` deploys; rev 8 records
> the reviewer's confirmation of the default as proposed, and SDD OQ-151 is now closed.* Today the only
> principal holding
> that Read is the service identity (§6.2), so the exposure is latent, not live — it opens when
> WBS 8.2 grants a persona Read on Payment without `REV_FinanceOnly` membership.

**`rev_payment` — Tier 4:** `rev_name` (`PAY-2026-00001`), `rev_grantid` (parental),
`rev_bankaccountid` (referential), `rev_providerid` (referential), `rev_amount`, `rev_paymentdate`,
`rev_method`, `rev_qboreference`, `rev_isfinalpayment`, `rev_paymentstatus` (Pending · Issued ·
Cleared · Cancelled — **added to this narrative in rev 5; the column has existed in
`Entity.xml` since WBS 8.1 and this list had omitted it**). **9 of this table's 10 columns are
`IsSecured=1`**, every one except `rev_name`.

> **Two rev-5 notes, both platform facts rather than design choices.** (1) `rev_name` is an
> **autonumber** (`PAY-{DATETIMEUTC:yyyy}-{SEQNUM:5}`), so although it is unsecurable for the same
> primary-name reason as Bank Account's, it **cannot carry an identity** — no user can type into
> it. The unsecurable-value risk on the finance tables is `rev_bankaccount.rev_name` alone.
> (2) `rev_amount` is **`decimal`, not `money`** — which is correct and must stay that way: a Money
> column's automatic `_base` twin reports `CanBeSecuredForRead=False` and would republish the
> amount to anyone holding table Read (`C-TECH-070`(2)).

**`rev_anonymisedstatistic` — Tier 2:** `rev_name` (`STAT-2026-00001`), `rev_agerange`,
`rev_locationarea`, `rev_conditionareas`, `rev_outcome`, `rev_amountawarded`, `rev_decisionmonth`,
`rev_snapshotdate`. **Deliberately carries no lookup and no reference to Applicant or Application** — a
foreign key or a stored reference number would make it pseudonymised rather than anonymised, and it would
then inherit the parent's retention clock instead of being retained indefinitely (Data Governance
Framework §3; SDD §7.1).

**`rev_errorlog` — Tier 2:** `rev_name` (`ERR-...`), `rev_flowname`, `rev_runid`, `rev_errormessage`,
`rev_recordreference` (text, **not a lookup**), `rev_occurredon`, `rev_severity`, `rev_resolved`,
`rev_resolvednote`. Holds run status, error message and record reference only — no personal data
(NFR-012, FR-010, FR-054).

**`rev_setting` — Tier 2:** `rev_name` (setting key), `rev_value`, `rev_datatype`, `rev_description`,
`rev_effectivefrom`. Seeded keys: `KnockoutThreshold`, `BorderlineBandLower`, `BorderlineBandUpper`,
`IncomeCeiling`, `RedactionConfidenceThreshold`, `LikertPointMap`, `FeelingScaleInversion`,
`ReminderDays`, `EscalationDays`, `PackScheduleDay`. Auditing is enabled on this table because a
threshold change is decision-relevant evidence (FR-017, NFR-019).

**`rev_roundfinance` — Tier 2 (Trustee Portal Visual Refresh, delta TAD, ADR-028, WBS 6.9):**
`rev_name` (the round key, alternate key so a round cannot be entered twice), `rev_isopen`
(FR-057 — which round the landing screen shows), `rev_roundopenedon` (FR-058's "date the round
opened" — entered, not derived), `rev_roundclosedon` (nullable, for the per-day average once a
round closes), `rev_amountcommitted`, `rev_peoplesupported`, `rev_individualssupported`,
`rev_peoplereachedbygroupgrants`, `rev_grantgivingcapacity` (charity-level, not round-scoped),
`rev_suggestedmaximumspend`, `rev_monthlydisbursement`, `rev_remaininglegacyfund` (charity-level,
not round-scoped) — all seven measures FR-063 — and `rev_figuresasat` (the date those seven
measures are current as of). No column secured: charity-level aggregate figures with no data
subject. Not personal data; out of scope of erasure (FR-051) and subject access (FR-053). No
relationship to any other table — this is not a `Round` entity and scopes no application
visibility (delta TAD §3.5). **Trustee-visible (FR-057, FR-063)** — read directly by the
`REV Trustee` role, which holds `prvReadrev_roundfinance` at Global (Roles/REV Trustee/
REV Trustee.xml).

**`rev_roundstatisticsrequest` — Tier 2 (Trustee Portal Visual Refresh, delta TAD Revision 5, ADR-038, section 3.9, WBS 6.9):** From Revision 5 the whole request is `rev_name` (fixed key `CURRENT`, alternate key so a second row is impossible) and `rev_triggeredon` (written by the trustee's "Refresh figures" control; the column the Dataverse row trigger fires on) — both **trustee-visible (Read and Write)**, held by `REV Trustee` at Global (`prvReadrev_roundstatisticsrequest`, `prvWriterev_roundstatisticsrequest`, Roles/REV Trustee/REV Trustee.xml). `rev_status`, `rev_resultjson` and `rev_computedon` are UNUSED from Revision 5 and retained in source with superseding descriptions rather than deleted (delta TAD section 3.9.2) — the live columns of these names moved to the new result table below, written by nothing and read by nothing here. No column secured. No relationship to any other table.

**`rev_roundstatisticsresult` — Tier 2 (Trustee Portal Visual Refresh, delta TAD Revision 5, ADR-038, section 3.9, WBS 6.9):** `rev_name` (fixed key `CURRENT`, alternate key so a second row is impossible), `rev_status` (the flow's own verdict, reusing the existing global option set rev_roundstatisticsrequeststatus rather than a new one — a cosmetic naming mismatch the TAD accepts, delta TAD section 3.9.2), `rev_resultjson` (the JSON document delta TAD section 3.3 specifies; not audited — a re-derivable snapshot regenerated on every trigger) and `rev_computedon` (written by the flow the instant it finishes; the only input to the freshness decision) are all **trustee-visible (Read only)**, held by `REV Trustee` at Global (`prvReadrev_roundstatisticsresult`, Roles/REV Trustee/REV Trustee.xml) — a trustee can request a computation and can never author one. No column secured. No relationship to any other table.

### 3.2 Provider classification — DERIVED, reviewer confirmation required

**No source document classifies the Provider entity.** The Solution Architecture describes it only as
"reusable holiday providers"; the Security Model §3 tier table, the Data Governance Framework §3 inventory
and SDD §7.2 all omit it (SDD OQ-026 records the gap and assigns it to the TAD stage).

**Derived classification: Tier 2 — Internal. Not personal data. No Art. 6 basis required.**

Reasoning, stated so a reviewer can overturn it:
1. The entity's described purpose is organisational — the holiday provider a grant is spent with. It holds
   no data subject: no applicant, helper, referee or trustee attribute appears in it.
2. The access matrix supports this reading: Provider is the only table a trustee has **no** access to while
   Finance has read access — the pattern of commercial reference data, not personal data.
3. It is not in the erasure sweep in the Data Governance Framework §Right to erasure, which lists
   Applicant, Application, Review, Grant and Payment. A table holding personal data would have to be.

**The derivation carries one binding design condition:** `rev_provider` must hold **no named individual**.
Contact details are captured as a role-based mailbox and switchboard number (`bookings@provider.example`),
never a person. If the reviewer or DPO confirms that named provider contacts are required, Provider
**reclassifies to Tier 3 — Confidential**, needs an Art. 6 basis (6(1)(b) contract performance, or 6(1)(f)
legitimate interests) added to SDD §7.2, and must be added to the erasure locate-step in §5.12.

> **Flagged for reviewer confirmation. SDD OQ-026 remains open until answered.**

### 3.3 Relationships and cascade behaviour

Cascade behaviour is load-bearing here: the retention design (ADR-004) depends on deleting one parent row
and having the whole case follow. Adopted from the Data Governance Framework §4 and Solution Architecture §8.

| Parent | Child | Cardinality | Type | Delete behaviour | Why |
|---|---|---|---|---|---|
| Applicant | Application | 1:N | **Parental** | Cascade delete | Erasure runs from a single applicant reference and must remove the whole case (DGF §Right to erasure) |
| Applicant | Bank Account | 1:N | **Parental** | Cascade delete | *DERIVED* — no source states it; without it, Tier 4 bank details survive erasure |
| Application | Review | 1:N | **Parental** | Cascade delete | "Review, Grant and Payment rows hang off the Application through cascade-delete relationships" (DGF §4) |
| Application | Grant | 1:N | **Parental** | Cascade delete | As above |
| Grant | Payment | 1:N | **Parental** | Cascade delete | *DERIVED* — the source says Payment hangs off the Application; parenting it to Grant is the normalised form and the cascade still reaches it transitively via Application → Grant → Payment |
| Provider | Grant | 1:N | **Referential, Restrict Delete** | Provider survives; cannot be deleted while grants reference it | Reference data must not disappear from historical records |
| Provider | Payment | 1:N | **Referential, Restrict Delete** | As above | As above |
| Bank Account | Payment | 1:N | **Referential** | Payment survives a bank-account purge | Supports the "purge bank details early" option in §3.4 without destroying the payment record |
| Review | systemuser (trustee) | N:1 | **Referential** | Verdict survives the trustee's account being disabled | A leaver must not erase the board's decision record |
| Anonymised Statistic | — | — | **None, by design** | Never deleted | A relationship would make it linkable and therefore personal data |
| Error Log | — | — | **None, by design** | Deleted on its own 90-day clock | Reference held as text, so no dangling lookup after the parent is deleted |

> ⚠️ **Documented deviation from `knowledge/technology/dataverse.md`.** That file states "Enable **Restrict
> Delete** on all tables with a regulatory retention period" and "Referential: preserve child on parent
> delete — use for records with compliance retention". Applied literally, that rule would **block the entire
> retention design**, because here the regulatory obligation is to *delete* at the end of the period, not to
> preserve. Parental cascade is therefore used on the Applicant/Application spine, and the guardrails against
> accidental deletion are: (a) the bulk-delete jobs run against an explicit status-plus-date query, never an
> unfiltered one; (b) Purview basic labels as a time-based backstop; (c) the pre-delete Anonymised Statistic
> check in §5.12; (d) Restrict Delete retained on Provider, where preservation genuinely is the requirement.
> Recorded for reviewer acknowledgement.

### 3.4 Two retention gaps found in the source design — DERIVED remediation

**Gap 1 — orphaned Applicant rows survive retention.** The retention bulk-delete jobs query
**Application** by status and date. Deleting an Application cascades to Review, Grant and Payment, but
**the Applicant row is the parent, so it is not deleted**. An applicant whose only application is deleted
would leave a `rev_applicant` row holding full name, address, date of birth and — where captured — ethnic
group, indefinitely. That breaches FR-048 ("delete the full application record"), NFR-010 and
Art. 5(1)(e).
**Remediation (DERIVED):** a fourth recurring bulk-delete job, or a step in the Retention & Erasure helper
flow, deletes `rev_applicant` rows that have **no remaining child Application**. Listed in §12 as a
provisioning item. Flagged for reviewer confirmation — no source document covers it.

**Gap 2 — Bank Account has no retention rule.** No source document states a retention period or a delete
trigger for `rev_bankaccount`, and the DGF erasure sweep names Applicant, Application, Review, Grant and
Payment but not Bank Account. Sort code and account number are Tier 4.
**Remediation (DERIVED):** parent Bank Account to Applicant with cascade delete, so it is removed by both
the retention cascade and erasure. **Open decision for the DPO and finance:** whether bank details should be
purged earlier — as soon as the final payment is reconciled — which would be materially better data
minimisation (Art. 5(1)(c)) than holding them for six years. The Referential relationship from Bank Account
to Payment is chosen specifically so that this option stays open without a schema change.

### 3.5 Conflicts between the SDD and the architecture source — reviewer decision needed

| # | SDD (approved, upstream) | Architecture source | Recommendation |
|---|---|---|---|
| 1 | FR-008: reference format `REV-YYYY-NNN` | §4: Application autonumber `GA-2026-00001`; Applicant `REV-A-00001` | **Adopt the SDD** — `rev_application.rev_name` = `REV-2026-001`. Keep `REV-A-00001` for the Applicant pseudonymised ID; the two serve different purposes and both are needed. Reviewer to confirm. |
| 2 | §3 Out of scope: "Payment process automation"; seven automations only | Component map and §4 include **automation #8 Finance** — `REV | Finance | Capture Payment` flow and a payment capture form | ✅ **RESOLVED 2026-09-09 (rev 5) — SPLIT, and the two halves went opposite ways.** **The payment capture FORM is AUTHORISED** by reviewer approval of `docs/plans/revitalise-payment-capture-plan.md`, which supplies the FR layer this row said was missing: **FR-150** (one finance surface over Provider, Bank Account and Payment), **FR-151** (Grant, payee account and amount required), **FR-152** (QuickBooks reference), **FR-153**/**FR-154** (the two data-entry rules the unsecurable values force), **NFR-150** and **US-030**. It is `wbs:8.3`, inside the customer-accepted WBS — `docs/Import/baseline-lock.yml` records the reviewer's D-2 answer that Automation #8 needs no change order — and its design is §6.1, §6.2.1, §9, §12 and `ADR-045`–`ADR-048` (`ADR-044` was proposed and **rejected** — rev 6). **The `REV \| Finance \| Capture Payment` FLOW is OPEN — DEFERRED BY REVIEWER DECISION 2026-09-09 (rev 6).** The reviewer answered *"decide later"*: the flow is **not** authorised, **not** descoped and **not** resolved. It still has no FR, it is not an accepted WBS task in its own right, no task id is opened for it, and nothing is built toward it. Its cost while deferred is a **compliance gap, not merely an automation gap** — `rev_grant.rev_finalpaymentdate` stays unwritten and the six-year retention clock never starts (§5.11, risk **A-R56**). *Previously read (rev 5): reviewer decision still required on the flow alone — authorise as a scope addition or descope. Before that (rev 4): the tables, role and a minimal surface are required by US-015 AC-1 and NFR-002 and are retained, the flow has no FR, reviewer to authorise or descope — undivided.* |
| 3 | FR-023: duplicate check runs "WHEN the application record is created" | §4: `REV | Duplicate | QBO Check` triggered by "Payment row created (child flow)" | **Adopt the SDD trigger** (check at intake, so the flag is available before assessment) **and** retain a second invocation before payment issue, which is what the source's end-to-end flow describes. One child flow, two call sites. |
| 4 | §3 Out of scope: "Full QuickBooks API integration… the fallback cross-reference approach is in scope" | §6: QBO connector query is primary; quarterly export to a Grant History table is the fallback | A single read-only query is not "full API integration". **Adopt the source's primary** (connector query) with the Grant History table as the documented fallback (ADR-017). `rev_granthistory` is built only if the fallback is adopted — SDD OQ-015/OQ-016. |

### Migration Strategy

- **Schema is a solution component.** Every table, column, choice, relationship, security role and column
  security profile ships inside `RevitaliseGrantAutomation`. No schema change is ever made directly in a
  non-DEV environment (§9).
- **Source of truth:** the solution is exported from DEV, unpacked with `pac solution unpack` and committed
  to `src/solutions/RevitaliseGrantAutomation/` so every schema change is diffable and recoverable.
- **Forward-only, additive changes.** New columns are added nullable first, backfilled by a one-off flow or
  data import, then made business-required. Choice options are added, never renumbered or removed while rows
  reference them. Columns are never renamed in place: add → copy → deprecate → drop across two releases.
- **Data migration is limited to the current application round** (SDD scope; delivered inside Automation #4
  setup, SDD OQ-028). Historical grants are not migrated; prior-grant history is reached through QuickBooks
  (ADR-017).
- **Non-production data.** DEV holds synthetic and anonymised test data only — no real applicant PII
  (source §3). Tier 3 and Tier 4 columns must never hold real values outside PROD (C-TECH-007,
  development-agent / pipeline-agent scope).
- **Retention configuration is not a solution component.** The recurring bulk-delete jobs, the column
  security profile *membership*, group teams and the audit retention setting are per-environment
  configuration applied by `post_deploy` provisioning (§12).

---

## 4. Integration Design

Six external touchpoints plus three in-tenant Microsoft services. **Dataverse is the hub — external systems
never talk to each other directly, only through it** — so each integration is independently replaceable, and
every one has a documented fallback so no single external dependency can stop the pipeline (source §6).

| Integration | Direction | Protocol / Connector | Tier | Trigger / method | Auth method | Fallback |
|---|---|---|---|---|---|---|
| **WordPress / Gravity Forms → Dataverse** | Inbound | Request (HTTP) trigger; or Gravity Forms REST API v2; or parsed structured email | **Premium** | Webhook POST on form submit | **Bearer token / shared secret held in a Key Vault-backed secret environment variable — see §6.3.** Caller restricted to the charity website (NFR-008) | Scheduled REST pull (service-account-initiated, reverses the trust direction) or structured-email trigger — no downstream component changes |
| **DocuSign** | Bi-directional | DocuSign connector | Premium | Outbound: create envelope on approval. Inbound: envelope-completed event | OAuth 2.0, service account owns the connection | Manual print-sign-scan route recorded on the Grant record (FR-046) |
| **QuickBooks Online** | Inbound (read only) | QuickBooks Online connector | Premium | Query by applicant name / email at intake, re-checked before payment issue | OAuth 2.0, **read-only scope** | Quarterly export into `rev_granthistory` + Power Automate cross-reference (ADR-017) |
| **AI Builder (prebuilt PII detection model)** | Internal | AI Builder connector, invoked from `REV \| Narrative \| Scrub Free-Text` | Premium | Synchronous call within the redaction flow | Environment AI Builder credits; runs as the service account | Human-only redaction: every narrative routes to the process owner for manual review (degraded, not broken) |
| **SharePoint Online — signed-acceptance library** | Outbound (write) + read | SharePoint connector | Standard | Store signed PDF on envelope completion; URL written to `rev_grant.rev_signedpdfurl` | Service account connection | Attach the PDF as a Dataverse note/annotation on the Grant row |
| **Microsoft Teams** | Outbound | Microsoft Teams connector | Standard | New-application notification, daily summary, escalation, failure alert | Service account, posts as Flow bot | Outlook email to the service mailbox recipient |
| **Microsoft 365 Outlook** | Outbound | Office 365 Outlook connector | Standard | Applicant and referee correspondence, summaries, escalations | Service account (`rev_ServiceMailbox`) | — |
| **Word Online (Business)** | Internal | Word Online (Business) connector | Standard | Populate the anonymised trustee-pack template → PDF (FR-032) | Service account | Print/export from the trustee portal (FR-039) |
| **Approvals** | Internal | Approvals connector | Standard | Optional: route flagged redactions (FR-030) and Borderline reviews (FR-019) as approvals rather than Teams messages | Service account | Teams message + a Dataverse view |

### 4.1 Integration controls

- **TLS 1.2 or higher on every hop** (C-TECH-003). All connectors and the HTTP trigger are HTTPS-only;
  the Power Platform enforces this and it is not configurable downward.
- **Every external connection is owned by the service account**, never a personal login, so access survives
  staff changes and is governed centrally (NFR-006, Security Model §2). Connections are bound through the
  four connection references `rev-dataverse`, `rev-docusign`, `rev-qbo`, `rev-outlook` (ALM Runbook §3), so
  no flow is edited at deployment time.
- **DLP connector policy** (C-TECH-045) — see §6.4 for the complete classified list, including two
  connectors the source's business group omits.
- **Error handling on every inbound flow**: malformed or duplicate payloads are caught, written to
  `rev_errorlog` and surfaced to the process owner via Teams rather than failing silently (FR-010).
- **UK residency** must be verified per integration at setup, not assumed: the Power Platform environments,
  AI Builder, DocuSign and QuickBooks Online (NFR-009, DPIA action A5, SDD OQ-018/OQ-019). Recorded as a
  §12 gate item and a §11 risk — no source document evidences it as verified.
- **Idempotency at the boundary**: `rev_application.rev_sourcesubmissionid` is an alternate key, so a
  replayed webhook or a re-run REST pull updates rather than duplicates.

### 4.2 Subject access request path — ⚠️ NO AGREED MECHANISM (C-DOM-005, open item)

> ⚠️ **This section describes a *proposal*, not a design decision. There is no built or agreed SAR
> mechanism.** The reviewer confirmed this on 2026-08-10 and accepted it as a known gap to close during or
> before development (SOFT warning C-DOM-005, accepted-risk path). **Carried forward to development-agent as
> an open item.** Nothing downstream should treat the approach below as settled.

**What the sources contain.** The Data Governance Framework and the architecture source both design the
*erasure* locate-step — across Applicant, Application, Review, Grant, Payment, the signed-PDF library,
DocuSign and QuickBooks — and SDD FR-053 requires "a complete extract of the data held about a named
individual". **No source document describes a SAR mechanism, and no component is assigned to produce the
extract.**

**Proposed approach, for agreement before development completes.** The `REV | Retention | Retention & Erasure
Helper` flow could gain a third, manually triggered mode — *SAR extract* — reusing the same locate-step and
writing the located rows to a protected file delivered to the process owner rather than deleting them:
generated by the service account, the run written to the retention/erasure evidence log with actor and
timestamp (FR-054), and the working extract deleted once delivered. This is the lowest-cost route because the
locate logic already has to exist for erasure (FR-051), but it is **one option among several** — a
purpose-built export, a Dataverse advanced-find plus documented manual procedure, or an MDA-driven extract
would all satisfy FR-053.

**What must be settled to close this item:**
1. Which mechanism is built, and whether it is automated or a documented manual procedure.
2. The delivery and protection route for the extract file — no source addresses it.
3. Whether the extract must cover the copies outside Dataverse (signed-PDF library, DocuSign, QuickBooks) as
   the erasure locate-step does. FR-053 says "all data held about a named individual", which implies yes.
4. The internal turnaround target — **there is no SAR SLA in any source** (SDD OQ-023, NFR-025), so the
   test-agent has no measurable threshold to test against even once a mechanism exists.

Recorded as risk **A-R22** and referenced in §5.12 mode 3, which is likewise marked as proposed.

---

## 5. Automation / Workflow Design

**Thirteen cloud flows**: the ten the source's naming table and component map define, the light retention and
erasure helper the source demotes the custom sweep to, the `REV | Ops | Failure Alert` child flow, and one
**derived** flow the source's own inventory cannot accommodate (§5.6). Plus **four native Dataverse recurring
bulk-delete jobs**, which are environment configuration and not flows at all (§12).

Every flow: runs as the service account; validates its input before processing; calls
`REV | Ops | Failure Alert` from its configured error path; retries transient external failures with
exponential back-off to a capped retry count; and writes no personal data to any log (NFR-012).

| # | Flow | Automation | Trigger | Requirements served |
|---|---|---|---|---|
| 1 | `REV \| Intake \| WordPress to Dataverse` | #4 | HTTP webhook (fallback: scheduled REST pull / email) | FR-007, FR-008, FR-009, FR-010 |
| 2 | `REV \| Scoring \| Calculate & Flag` | #2 | Dataverse row created — Application | FR-011–FR-016, FR-019, FR-020, FR-022 |
| 3 | `REV \| Scoring \| Daily Summary` | #2 | Scheduled, daily | FR-021 |
| 4 | `REV \| Duplicate \| QBO Check` | #7 | Child flow — called from #1 and from #11 | FR-023, FR-024, FR-025 |
| 5 | `REV \| Narrative \| Scrub Free-Text` | #5 | Dataverse row updated — status becomes Eligible for Panel | FR-026–FR-031 |
| 6 | `REV \| Narrative \| Trustee Pack` **(DERIVED)** | #5 | Scheduled ahead of the board meeting **+** manual | FR-032, FR-033 |
| 7 | `REV \| Portal \| Finalise Decisions` | #6 | Manual, process owner, after the board meeting | FR-037, FR-040, FR-047, FR-055 |
| 8 | `REV \| Acceptance \| Create Envelope` | #3 | Application/Grant status becomes Approved | FR-041, FR-042 |
| 9 | `REV \| Acceptance \| Reminders & Escalation` | #3 | Scheduled daily + DocuSign event | FR-043, FR-044 |
| 10 | `REV \| Acceptance \| Completion` | #3 | DocuSign envelope completed | FR-045 |
| 11 | `REV \| Finance \| Capture Payment` | #8 ⚠️ | Manual, finance role | **UNBUILT — open, deferred by reviewer decision (rev 6).** Still no FR. The *form* half of #8 was authorised as `wbs:8.3` in rev 5 (FR-150–FR-154); this **flow** was not, and the reviewer deferred the authorise-or-descope decision on 2026-09-09. See §3.5 conflict 2 and §5.11 |
| 12 | `REV \| Retention \| Retention & Erasure Helper` | cross-cutting | Scheduled monthly (after the bulk-delete jobs) + manual on demand | FR-049–FR-055 |
| 13 | `REV \| Ops \| Failure Alert` | cross-cutting | Child flow — called from the error path of flows 1–12 | FR-010, NFR-012, NFR-016 |

### 5.1 `REV | Intake | WordPress to Dataverse`

Event-driven. Validates the payload against the agreed field map before any write. **Idempotency guard:**
the Gravity Forms submission ID is written to `rev_application.rev_sourcesubmissionid`, an alternate key, so
a replayed or duplicated webhook updates the existing row instead of creating a second application.
Matches or creates the Applicant on email plus name (so a repeat applicant is one Applicant row with two
Applications), derives `rev_agerange` from date of birth and `rev_locationarea` from postcode at write time
(FR-027), assigns the reference (FR-008), posts the Teams notification (FR-009), and calls the duplicate
check child flow (FR-023). Any failure writes `rev_errorlog` and alerts the process owner (FR-010) — no
submission is silently lost.

### 5.2 `REV | Scoring | Calculate & Flag`

```mermaid
flowchart TD
  A([Application row created]) --> B{All scored answers present?}
  B -- No --> C["Status = Under Review<br/>route to process owner<br/>no automated outcome (FR-022)"]
  B -- Yes --> D["Invert feeling-scale answer (FR-012)"]
  D --> E["Map Likert answers to points<br/>from Setting.LikertPointMap (FR-013)"]
  E --> F["Sum to circumstance score 0-60<br/>write score breakdown (FR-011)"]
  F --> G["Evaluate income against<br/>Setting.IncomeCeiling → income flag (FR-015)"]
  G --> H{Score vs Setting thresholds}
  H -- "above band" --> I["Status = Auto-pass"]
  H -- "within band" --> J["Status = Borderline<br/>route to process owner (FR-019)"]
  H -- "below knockout" --> K["Status = Auto-reject<br/>move out of active view (FR-020)"]
  I --> L([Await process-owner action])
  J --> L
  K --> L
  C --> L
```

Health-condition data, disability data and the free-text narrative are **not read** by this flow — enforced
by the flow reading a named column list, not the whole row (FR-016, DUAA 2025 position). Thresholds come
from `rev_setting`, never from flow logic (FR-017, NFR-019). Idempotent: re-running recalculates the same
score from the same answers and does not overwrite a status the process owner has overridden
(`rev_statusoverridden = true` short-circuits the write, FR-018).

### 5.3 `REV | Scoring | Daily Summary`

Scheduled daily. Counts applications scored, auto-rejected and Borderline-awaiting-review in the period and
sends one Teams message to the process owner (FR-021). Carries **counts only, no applicant identifiers** —
a deliberate narrowing, because a summary posted to a chat is the easiest place for personal data to leak.
Safe to run twice: it reads and reports, it does not write.

### 5.4 `REV | Duplicate | QBO Check`

Child flow, two call sites: at intake (FR-023, per the SDD) and before payment issue (per the source's
end-to-end flow). Queries QuickBooks Online read-only by applicant name and email. On a match, writes
`rev_duplicateflag`, `rev_priorgrantref`, `rev_priorgrantdate`, `rev_priorgrantamount` (FR-024); on no
match, records "no prior grants found" with `rev_duplicatecheckedon` so the check is evidenced as having run
(FR-025). If QuickBooks is unreachable, the flow records the failure and flags the application as
*check pending* — it never reports a false "no prior grants found".

### 5.5 `REV | Narrative | Scrub Free-Text` — the human-in-the-loop control

```mermaid
flowchart TD
  A([Application status → Eligible for Panel]) --> B["Read raw narrative +<br/>other-condition notes (Tier 4)"]
  B --> C["AI Builder prebuilt PII model:<br/>detect entities + confidence"]
  C --> D["Replace detected identifiers with<br/>category labels [NAME] [FAMILY MEMBER]<br/>[GP PRACTICE] [ADDRESS] [PHONE] (FR-026)"]
  D --> E["Generalise ages → age band,<br/>places → region (FR-027)"]
  E --> F["Write redacted narrative;<br/>retain region, dates, score,<br/>preferences, condition info (FR-028)"]
  F --> G{"Confidence ≥ Setting.<br/>RedactionConfidenceThreshold (85%)?"}
  G -- No --> H["Flag for manual review;<br/>released = false;<br/>WITHHELD from trustees (FR-029)"]
  H --> I["Process owner reviews, corrects,<br/>releases (FR-030)"]
  I --> J([Visible to trustees])
  G -- Yes --> J
  C -.->|"AI Builder error / no credits"| K["Failure Alert;<br/>route 100% to manual review<br/>(degrade, never disclose)"]
```

The raw narrative is read by this flow and by the Admin role only; it is never written to a log, never
passed to a notification, and never reaches a trustee column (FR-031, NFR-001). Trustee visibility is a
conjunction of two conditions — `rev_eligibleforround = true` **and** `rev_redactionreleased = true` — so
the default state of a new narrative is *withheld*, and a flow failure fails closed (NFR-018).

### 5.6 `REV | Narrative | Trustee Pack` — DERIVED, +1 to the source's inventory

The source's ten-flow inventory has no component for FR-032 (per-application anonymised document) or FR-033
(pack preparation runs **on demand by the process owner and on a schedule**), yet the integration register
does list Word Online (Business) for exactly that purpose. A single Power Automate flow can carry only one
trigger, and flow #5 already uses a Dataverse row-updated trigger, so the on-demand and scheduled paths
cannot live inside it.

**Derived: an eleventh business flow** with a scheduled trigger ahead of each board meeting plus a manual
trigger, which generates the per-application anonymised Word/PDF document — redacted narrative, score
breakdown, holiday details, staff recommendation — for the trustees who cannot or will not use the portal
(FR-032, FR-039, US-014). It reads only released, trustee-permitted columns, so the offline pack cannot
contain more than the portal does.

> **Flagged as an interpretation:** it takes the source's flow count from ten to eleven business flows
> (thirteen including the helper and the failure-alert child flow). Reviewer confirmation requested.

### 5.7 `REV | Portal | Finalise Decisions`

Manual, process owner, after the board meeting — one controlled, auditable step (FR-040). Reads the verdicts
from `rev_review`, applies them to the Application and Grant records, creates Grant rows for approvals, and
triggers flow #8 for the whole approved batch in a single run (FR-047). **Also writes the Anonymised
Statistic snapshot** (FR-055 — see §5.13). Guarded against double-execution by a `rev_finalisedon` stamp on
the Review row: a second run over an already-finalised round is a no-op.

### 5.8–5.10 Acceptance flows (#3)

**Create Envelope** — on status Approved, builds the DocuSign envelope from the template, pre-populated with
applicant name, grant amount, provider, dates and conditions, and routes it for **two signatures in
sequence**: applicant first, then referee or GP (FR-041, FR-042). Writes `rev_docusignenvelopeid` and
`rev_acceptanceissuedon`. **The Grant Referee (Signer 2)'s own Title, Address, Town/City and Postcode
anchor tabs are deliberately left for the referee to complete during signing, not pre-populated from
Dataverse — see ADR-043.**
**Reminders & Escalation** — scheduled daily, plus DocuSign events. Reminders at **3 and 7 days**
(`Setting.ReminderDays`), escalation to the process owner with the applicant's details at **14 days**
(`Setting.EscalationDays`) (FR-043, FR-044). Idempotent: a reminder-sent stamp prevents a duplicate on a
re-run.
**Completion** — on envelope completed, sets Grant status to *Acceptance Signed*, stores the signed PDF in
the SharePoint library and writes its URL to `rev_grant.rev_signedpdfurl` (FR-045). The manual
print-sign-scan route (FR-046) is recorded directly on the Grant record through the Model-Driven App — no
flow, by design, because it is a human-attested exception.

### 5.11 `REV | Finance | Capture Payment`

⚠️ **OPEN — DEFERRED BY REVIEWER DECISION, 2026-09-09 (rev 6). Unauthorised and unbuilt.** The
reviewer was asked to authorise this flow as a scope addition or descope it, and answered
**"decide later"**. That is a deliberate deferral, not a resolution and not a descope: the flow has
no FR behind it, no WBS task id of its own, **no task is opened for it and nothing is built toward
it**. It stays on this page in exactly this state until the reviewer decides.

What changed on 2026-09-09 is only that the **form** beside it was authorised as `wbs:8.3`
(FR-150–FR-154), so the two are no longer one undivided question. *Previously read (rev 5): still
unauthorised and unbuilt, reviewer decision on the flow still open.*

Manual, finance role. It would have recorded the Provider, Bank Account and Payment rows,
re-invoked the duplicate check before issue, and set `rev_grant.rev_finalpaymentdate` on the final
payment.

**The first of those three is now delivered without it** — the WBS 8.3 form records all three row
types by hand. The other two are not, and the second one matters:

- **The duplicate-payment re-check before issue is not performed.** That is Automation #7 / FR-023's
  second call site, and verifying it is `wbs:8.5`.
- **`rev_grant.rev_finalpaymentdate` is never written, so the six-year retention clock never
  starts for any grant.** The form captures `rev_payment.rev_isfinalpayment` on the Payment row and
  nothing propagates it to the Grant. This flow was the only thing designed to make that hop, so
  descoping it leaves a **compliance gap, not merely an automation gap** — the retention design in
  §3.4 and ADR-004 keys off that date. Carried as risk **A-R56** and named in §3.5 conflict 2's
  **deferred** reviewer decision, because it is the fact that should decide it. **The deferral does
  not close this gap and does not reduce it** — it leaves it open with no owner and no date. The
  only interim mitigation is that a process owner can set `rev_finalpaymentdate` by hand on the
  Grant; nothing prompts anyone to, and no gate detects that nobody did.

### 5.12 `REV | Retention | Retention & Erasure Helper`

Two confirmed modes plus one proposed mode. The **native recurring bulk-delete jobs are the primary retention
control** (ADR-004); this flow is the residual that covers only what the native job cannot reach.
⚠️ **Mode 3 (SAR extract) is a proposal, not an agreed design — see §4.2. It is an accepted open item carried
to development-agent, not a committed component of this flow.**

```mermaid
flowchart TD
  subgraph M1["Mode 1 — monthly, scheduled after the bulk-delete jobs"]
    A1([Monthly schedule]) --> A2["Verify an Anonymised Statistic snapshot<br/>exists for each row about to be deleted (FR-055)"]
    A2 --> A3["Delete orphaned Applicant rows<br/>with no remaining Application (DERIVED — §3.4 gap 1)"]
    A3 --> A4["Purge matching DocuSign envelopes (FR-049)"]
    A4 --> A5["Apply the QuickBooks finance-retention<br/>carve-out — retain, do not delete (FR-050)"]
    A5 --> A6["Write the retention evidence log:<br/>record ref, data type, date, rule — no personal data (FR-054)"]
  end
  subgraph M2["Mode 2 — on demand, erasure request"]
    B1([Process owner triggers with applicant reference]) --> B2["Locate across Applicant, Application, Review,<br/>Grant, Payment, Bank Account, signed-PDF library,<br/>DocuSign, QuickBooks — incl. referee, helper,<br/>group member, emergency contact (FR-051)"]
    B2 --> B3{Legal hold applies?}
    B3 -- Yes --> B4["Retain the carve-out; report to the requester<br/>what cannot be deleted and why (FR-052)"]
    B3 -- No --> B5["On-demand bulk delete by applicant reference;<br/>cascade removes the case (FR-051)"]
    B4 --> B6["Log request + action taken (FR-054)"]
    B5 --> B6
  end
  subgraph M3["Mode 3 — SAR extract — PROPOSED ONLY, not agreed (§4.2)"]
    C1([SAR received]) --> C2["Reuse the locate step; produce a complete<br/>extract for the named individual (FR-053)"]
    C2 --> C3["Deliver to the process owner; log the run;<br/>delete the working extract"]
  end
```

### 5.13 Who writes the Anonymised Statistic snapshot — DERIVED

The source's access matrix says the service account "Writes" the Anonymised Statistic table, but **no flow in
the source's inventory writes it**, and FR-055 requires the statistics to survive deletion of the underlying
personal data. Derived assignment:
1. `REV | Portal | Finalise Decisions` writes the snapshot at decision (outcome = Approved / Deferred /
   Rejected), so reporting is current rather than end-of-life.
2. `REV | Finance | Capture Payment` updates the amount on final payment.
3. `REV | Retention | Retention & Erasure Helper` **verifies a snapshot exists before any record is
   deleted** — the safety net that makes FR-055 true even if step 1 failed.
The snapshot carries no lookup and no reference number (§3.1), so it is genuinely anonymised and is not
touched by erasure.

### 5.14 `REV | Ops | Failure Alert`

Child flow called from the configured `run after has failed / timed out` path of every other flow. Writes one
`rev_errorlog` row — flow name, run ID, error message, record reference, timestamp, severity — and posts a
Teams alert to the process owner. **Holds no personal data** (NFR-012, NFR-016). Native Power Automate run
history and Dataverse field-change auditing back it up (source §5, Security Model §8).

> ⚠️ **Compliance note on `rev_recordreference`.** The Security Model §3 and the Data Governance Framework §3
> both classify the Error Log as non-personal because it holds "record references only". A reference that
> resolves to a living person is strictly **pseudonymised personal data**, not anonymous. The mitigations
> designed in are: a short 90-day operational retention (derived — the sources say only "short"), Tier 2
> handling with no trustee access, and no name, contact detail or narrative fragment ever written to the
> message. Flagged for DPO confirmation; recorded as risk A-R12.

---

## 6. Security Design

**Authoritative source: `Revitalise-Security-Model-v0.1.docx` (WBS 0.5).** Where it and the Solution
Architecture differ in detail, the Security Model is adopted. Checked against
`skills/compliance-checklist.md` §1.2 (Audit Logging) and §1.3 (Access Control).

| Concern | Control | Where applied |
|---|---|---|
| **Authentication** | Entra ID sign-in with **MFA for every staff, trustee and service-identity sign-in** (NFR-004). Staff and trustees use their own tenant accounts. The service account `svc-grantautomation` signs in with MFA and holds a **documented, scoped Conditional Access exception** so unattended flows are not blocked by an interactive-sign-in policy (Security Model §7) | Entra ID / Conditional Access (tenant). Provisioned in WBS 0.3 — **outstanding with Wanstor** |
| | The one public endpoint is the intake HTTP trigger. It accepts submissions **only from the authenticated charity website** (NFR-008, C-TECH-006) — bearer token / shared secret validated in the first flow action, request rejected before any Dataverse write | `REV \| Intake` flow; secret held per §6.3 |
| **Authorisation — outer gate** | Membership of a per-environment **Entra ID security group** is required to reach the environment at all, before any role permission applies (NFR-005). Group membership is the outer gate; the security role is the inner one (Security Model §7) | Power Platform admin centre, per environment |
| **Authorisation — inner gate** | Dataverse security roles, assigned **only through Entra-group-backed group teams** in PROD (C-TECH-040). Four roles — see §6.1 and §6.2 | Solution component (roles) + `post_deploy` config (group teams) |
| **Authorisation — column level** | Two column security profiles: `REV_TrusteeRestricted` hides every identifying column from the Trustee role so identity **never reaches the trustee app**; `REV_FinanceOnly` restricts all Bank Account and Payment columns to the Finance role, with one platform-forced exception — see the note directly below. This is the control that replaces manual anonymisation (ADR-002) | Solution component; profile *membership* applied per environment |

> **Exception to "all", ground-truthed 2026-08-23, not a design gap.** `rev_bankaccount.rev_name` and
> `rev_payment.rev_name` — each table's primary name attribute — are **not** in `REV_FinanceOnly`.
> Dataverse rejects `IsSecured=1` on any table's primary name attribute outright (`0x8004f501`, "The
> field 'rev_name' is not securable"), confirmed by a live `ensure-schema.ps1 -Env dev` run against
> DEV; this is a hard platform limit, not a configuration choice, and it holds regardless of what this
> section's prose says elsewhere. It carries no privacy consequence: both values are a plain reference
> (an account nickname/masked last four, or an autonumber payment reference), never the account
> number, sort code, amount or any other sensitive value — those stay on separate columns, still
> `IsSecured=1` and released only through `REV_FinanceOnly`. See
> `src/solutions/RevitaliseGrantAutomation/Entities/rev_bankaccount/Entity.xml` and the sibling
> `rev_payment/Entity.xml` for the full ground-truth record.
| **Separation of duties** | The Admin role holds **no Bank Account or Payment table privilege at all** — bank details sit behind one role and one role only (NFR-002, Security Model §4). Conversely the Finance role holds no Applicant or Application privilege, so finance staff never handle health data (US-015 AC-2) | Security role definitions |
| **Data at rest** | Dataverse platform encryption at rest (Microsoft-managed keys), **UK region** environments. SharePoint Online encryption at rest for the signed PDFs, same region. Tier 4 columns additionally protected by column security profiles (`skills/data-classification.md` — encryption at rest mandatory for Tier 3+) | Dataverse + SharePoint Online, UK region (NFR-009) |
| **Data in transit** | **TLS 1.2 or higher on every hop** (C-TECH-003) — all connectors, the HTTP trigger, DocuSign, QuickBooks and AI Builder calls are HTTPS-only and not configurable downward | Platform-enforced |
| **Data residency** | 100% of processing, storage and backup in the UK across every component including AI Builder, DocuSign and QuickBooks. Zero transfers outside the UK. **Verified at environment setup, not assumed** (NFR-009, DPIA A5) | §12 gate item; risk A-R19 |
| **Audit logging** | Native Dataverse **field-change auditing** enabled at environment and table level on all ten tables: every create, update and delete with timestamp (UTC), actor, action, record identifier and before/after values (NFR-014, C-DOM-010, C-DOM-011). **App-access logging** records which user opened the trustee app and when (NFR-015). Native Power Automate run history for flow execution | Dataverse (env + table setting, `post_deploy`) |
| **Audit integrity** | See §6.5 — the platform audit store is append-only and the application Admin role is deliberately separated from audit administration (C-DOM-012) | Role design + tenant admin separation |
| **Retention / erasure evidence log** | Bulk-delete runs are recorded as Dataverse system jobs; the consolidated evidence log (record reference, data type, date, rule applied) holds **no personal data** (FR-054, NFR-016) | System jobs + `REV \| Retention` helper flow |
| **Operational logging** | `rev_errorlog` + `REV \| Ops \| Failure Alert`: run status, error message, record reference only. **No personal data in any log** (NFR-012, C-DOM-004 — development-agent scope) | `rev_errorlog` table |
| **Privileged actions** | See §6.6 (C-DOM-021) | Tenant admin separation + logged, evidenced runs |
| **Secrets** | See §6.3 (C-TECH-002) | Key Vault-backed secret environment variable |
| **App registrations / API permissions** | The **solution runtime uses no app registration** — every connection is an OAuth connection owned by the `svc-grantautomation` user account (NFR-006). App registrations are needed only for **CI/CD and provisioning**, and are required regardless of ADR-007's outcome: `rev-grantautomation-deploy-dev` / `-tstacc` / `-prd` (one per environment, Dataverse application user in its own environment only, one OIDC federated credential each, no client secret) and `REV-MS-Provisioning` (Graph + PnP, certificate-based). Permissions and justification in §6.7 (C-TECH-043, C-TECH-044) | Entra ID; §12 tenant prerequisites |
| **Connector governance** | Environment-level DLP policy on **both** environments (NFR-007, C-TECH-045) — see §6.4 | Power Platform admin centre |
| **Session management** | **Not specified in any source.** Derived: rely on Entra ID token lifetime with a Conditional Access **sign-in frequency** control for the Admin and Finance personas, and disable persistent browser sessions on unmanaged devices. Value proposed: 8 hours. **Flagged for reviewer — SDD §7.9 records session timeout as an unaddressed architecture-level item** | Conditional Access (tenant) |

### 6.1 Security Role & Group Mapping

**This table is gate-blocking (TAD Intake Checklist; C-TECH-040 has nothing to bind without it).**

✅ **Status: DERIVED — confirmed by the reviewer (Xander Lykopoulos) on 2026-08-10.** The binding pattern
below is accepted as-is; no change to the mapping table was required.

**The Dataverse *group team* layer is DERIVED, not stated in the source.** The Security Model §7 describes
Entra ID security groups **gating each environment**, and §4 describes three Dataverse security roles, but it
never names the construct that connects the two — it implies trustees hold the role as individual tenant
users ("Trustees… are internal tenant users (Dataverse User lookups)"), which in PROD would be a **direct
user-to-role assignment and a HARD violation of C-TECH-040**.

The derivation is **not** invented: `knowledge/technology/security-model.md` **is populated** in this
repository and states the pattern explicitly — *"The **only** approved role-assignment mechanism in
Test/Acc/Prd (C-TECH-040): Entra security group → Dataverse **group team** (type AAD Security Group) →
security role. Direct user-to-role assignments are permitted in Dev only."* It also supplies the idempotent
Web API creation pattern and the canonical persona-mapping table format used below. Two Entra group *sets* are
therefore required and are different things: **environment groups** (the outer gate the source describes) and
**role groups** (the role binding this TAD derives).

| Persona | Entra Security Group | Dataverse Group Team | Security Role(s) | App Access |
|---|---|---|---|---|
| **Process owner** (Emily) | `REV-PP-GrantApplications-Admins-PRD` | `REV Admins` | `REV Admin` | MDA `REV Grant Administration`; trustee portal (read) |
| **Finance staff** | `REV-PP-GrantApplications-Finance-PRD` (not created — no Phase 1 table is reachable by this persona) | `REV Finance` | `REV Finance` — **not created; `wbs:8.2`** | **MDA `REV Grant Administration` — payment capture area only** (`ADR-048`, rev 6, `wbs:8.3`). *Rev 5 briefly superseded this cell with a separate app `rev_financecapture` (`ADR-044`); the reviewer rejected that on 2026-09-09 and this original approved cell is the one in effect.* ⚠ The area is a **navigation** boundary, not a security one — see `ADR-048` |
| **Trustee** | `REV-PP-GrantApplications-Trustees-PRD` (not created — no Phase 1 table is reachable by this persona) | `REV Trustees` | `REV Trustee` | Trustee portal **only** (Code App per ADR-003). No direct table access |
| **Service identity** (`svc-grantautomation`) | `REV-PP-GrantApplications-Service-PRD` | `REV Service Accounts` | `REV Service Automation` (DERIVED — see §6.2) | Owns and runs all flows and connections; publishes the trustee app |
| **Maker** (Xander, build only) | `REV-GrantApplications-DEV` | *(none — direct assignment permitted in DEV)* | System Customizer in DEV only | DEV maker portal |
| **Platform / audit admin** (tenant admin, Wanstor or Xander) | existing tenant admin group | *(none)* | Power Platform Administrator / Dataverse System Administrator — **held by nobody in the application personas** (§6.5) | Admin centres only |
| *Environment gate — not a role* | `REV-GrantApplications-DEV`, `REV-GrantApplications-PRD` | — | — | Controls who can reach the environment at all (NFR-005) |

Five Entra security groups plus the existing tenant admin group. Group teams are **not solution components** —
they are created per environment by an idempotent `post_deploy` script (§12, C-TECH-042), looking the role up
**by name in the target environment** because role GUIDs differ per environment.

> ✅ **Confirmed by the reviewer on 2026-08-10.** The group-team layer, the four role groups and the
> `REV Service Automation` role are architect derivations, accepted as-is. They do not change the *effective
> access* the Security Model's §6 access matrix defines — which is what the DPO signs off — they make it
> expressible and compliant with C-TECH-040. The DPO sign-off on ADR-002 is unaffected and still outstanding.

### 6.2 Security roles — why four, when the source says three

The Security Model §4 states "Three Dataverse security roles carry all access. There is no fourth role and no
personal exception." **Its own access matrix in §6 cannot be expressed with three roles.** The matrix gives
the Bank Account and Payment tables as `Admin: None` / `Service account: Runs`, and Admin is held by
**both** Emily and the service account. A single shared role cannot simultaneously deny bank access to Emily
and grant it to the service account.

| Role | Holder | Table privileges | Notes |
|---|---|---|---|
| `REV Admin` | Emily (process owner) | Full CRUD on Applicant, Application, Review, Grant, Provider, Anonymised Statistic, Setting, Error Log (read). **No Bank Account, no Payment.** Reads Tier 4 columns including the raw narrative | Owns views and configuration. **Not** a Dataverse System Administrator (§6.5) |
| `REV Finance` | Finance staff | Bank Account and Payment: create, read, update. **Provider: create, read, update** — ✅ *correction CONFIRMED by the reviewer 2026-09-09 (proposed rev 5, was "read")*. **Grant: read + AppendTo** — ✅ *addition CONFIRMED by the reviewer 2026-09-09 (proposed rev 5)*. Anonymised Statistic: read. Signed-PDF library: read | The only role that sees bank details (NFR-002). No Applicant or Application privilege. **Does not exist in source — `wbs:8.2`. See §6.2.1 for the two rev-5 corrections and the full build specification** |
| `REV Trustee` | Trustees (tenant users) | Read on Application, Review, Grant — **filtered by `REV_TrusteeRestricted`**. Write verdict + notes on Review. Read Anonymised Statistic | No direct table access; reaches data through the app only. No export-to-Excel privilege — the offline route is the anonymised pack (FR-032/FR-039) |
| `REV Service Automation` **(DERIVED)** | `svc-grantautomation` only | Everything `REV Admin` has, **plus** Bank Account and Payment (flow runtime), plus write on Anonymised Statistic and Error Log | Exists so the source's own access matrix is expressible. Assigned only to the service account, via group team |

Roles are **copies, never modified out-of-box roles** (C-TECH-046, development-agent scope) and ship as
solution components. **Documented deviation from `knowledge/technology/security-model.md`:** that file
prescribes a base-plus-additive pattern with a shared `[PREFIX] Base User` role. It is **not** applied here,
because the source's access matrix deliberately gives the Trustee role *no* access to Provider or Setting —
so a shared base role would either grant trustees more than the DPO signed off, or be empty. With four narrow
persona roles the guidance's actual purpose (no monolithic role) is already met. Recorded for reviewer
acknowledgement.

### 6.2.1 The Finance role does not exist — what `wbs:8.3` assumes, and what `wbs:8.2` must deliver

**Added rev 5 (`wbs:8.3`), resolving SDD OQ-152.** Measured 2026-09-09 from source:
`src/solutions/RevitaliseGrantAutomation/Roles/` holds `REV Admin`, `REV Service Automation` and
`REV Trustee`. **There is no Finance role.** The `REV_FinanceOnly` profile exists and releases the
16 secured columns, and its member list in `provisioning/deploymentSettings/` is exactly
`REV Service Accounts` — `REV Admins` deliberately excluded.

> **Correction to a widely-repeated statement:** the profile does **not** have "no member". It has
> one, and it is the unattended service account. The practical effect for the finance surface is
> the same — no human can read the 16 columns — but the difference matters twice: the service
> identity is a **second reader** of all bank and payment data by design (flow runtime, §6.2), so
> NFR-002's "finance role only" is in the built system "the finance role **and** the service
> account"; and WBS 8.2's membership change is one more entry in an existing array, not a first
> binding.

**Does the payment capture form's design assume the role exists?** No for authoring, yes for
acceptance. Stated per verification level, because "depends on 8.2" is too coarse to schedule
against (`C-TECH-053`):

| Level | Reachable without `wbs:8.2`? | Why |
|---|---|---|
| **V1 well-formed** | **Yes** | No artefact `wbs:8.3` authors names the role. `rev_grantadministration`'s `<AppModuleRoleMaps />` stays empty and is **not edited** by 8.3 — app sharing is per-environment config, not a solution component |
| **V2 packaged** | **Yes** | `pac solution pack` reads no role |
| **V3 accepted by the target** | **Yes** | Import updates the existing app module and sitemap and creates the forms and views; none references the role |
| **V4 openable and usable by a signed-in human** | **NO — two independent blocks** | (a) `share-apps.ps1` associates the app by role **name** and reports `FAILED — security role 'REV Finance' not found` when it is absent, so nobody is granted app access. (b) Even with access, a user outside `REV_FinanceOnly` sees **every field empty on both finance tables**, and cannot create a Bank Account **at all** — `rev_accountholdername` and `rev_payeetype` are `ApplicationRequired` *and* secured, so the platform demands a value the user may not write |
| **V5 end-to-end** | **NO** | Follows from V4 |

So `wbs:8.3` is **independently buildable and gate-verifiable to V3**, and **US-030 AC-1 through
AC-5 are not verifiable until `wbs:8.2` lands** (`ADR-047`). 8.3 must not be reported complete on
V3 evidence — and note that its evidence rule in `contract/evidence-map.json` is **now wrong as well
as weak**: it is a directory-existence check on `AppModules/rev_financecapture`, a separate app that
`ADR-044`'s rejection means will never exist, so the rule can no longer be satisfied by anything at
all. §9.4 specifies the replacement rules; `pm-agent` owns that file.

**What `wbs:8.2` must deliver for this surface to work.** Specified here because the form's
requirements determine it and because two items are **corrections to §6.2's approved row**, not
new asks. Not built here — 8.2 is a separate task with its own hours (`C-COM-002`):

| # | Deliverable | Why |
|---|---|---|
| 1 | Create/Read/Write on `rev_bankaccount` and `rev_payment` | FR-150 |
| 2 | **Read + AppendTo on `rev_grant`; Append on `rev_payment`** — ✅ **CONFIRMED by the reviewer 2026-09-09** | **FR-151. §6.2's approved Finance row named no Grant privilege at all** — a Payment cannot reference a Grant the role cannot read |
| 3 | **Create/Read/Write on `rev_provider`** — ✅ **CONFIRMED by the reviewer 2026-09-09** | **FR-150 requires the finance role to create and edit Providers; §6.2's approved row granted "Provider: read"** |
| 4 | **No `prvAssignrev_provider`, no `prvSharerev_provider`** | `rev_provider` is `OrganizationOwned`, so those privileges do not exist; requesting one fails the whole role binding, which is precisely what `verify-role-privilege-ownership.py` exists to catch |
| 5 | `REV Finance` added to `REV_FinanceOnly`'s `memberTeams` in all three settings files | Without it the form is blank for its own users |
| 6 | Entra group → group team → role binding | `C-TECH-040` |
| 7 | `REV Finance` added to the **existing `REV Grant Administration` app's** `dataverse.apps[].securityRoles` — **not a new app entry** (`ADR-048`, rev 6) | `share-apps.ps1` grants app access from that list |

**Items 2 and 3 are ✅ CONFIRMED by the reviewer on 2026-09-09** — they change what the approved
Finance role grants, and they were found by writing the form's requirements down rather than by any
gate. They are `wbs:8.2`'s to build, not `wbs:8.3`'s. *Previously read (rev 5): flagged for reviewer
confirmation.*

**One consequence of confirming item 2 that the approved row did not carry, measured 2026-09-09.**
`verify-field-security-coverage.py` warns, on this solution as it stands: *"`rev_grant.rev_amountawarded`
is `IsSecured=1`, but Dataverse maintains `rev_amountawarded_base` alongside it with
`CanBeSecuredForRead=False`. Anyone with Read on `rev_grant` can read the same value from the twin,
so column security is not the control here — the TABLE PRIVILEGE is. Before granting any new role
Read on `rev_grant`, confirm it is entitled to this amount."* Item 2 **is** that new Read. The
finance persona is judged entitled — it exists to pay the awarded amount, and FR-151 requires a
Payment to reference its Grant — so this is recorded as an accepted, stated consequence rather than
a blocker. It is written here because the gate asks for the confirmation to be made explicitly, and
because `wbs:8.2` is the dispatch that will make the grant.

**Item 7 changed shape in rev 6 and its security consequence is stated in `ADR-048`.** Adding
`REV Finance` to the **admin** app's role list means this persona can navigate an app that also
contains Applicant, Application, Review, Setting and Error Log. The barrier that keeps applicant
data off that persona's screen is therefore **only** the role's table privileges (§6.2: no Applicant
and no Application privilege), not the app boundary as well.

### 6.3 Secrets — the source's pattern does not satisfy C-TECH-002

The source specifies the intake endpoint's trust as **"Shared secret / service mailbox"** and names no store
for it. C-TECH-002 (HARD, architect scope) requires all secrets to come from the approved secrets manager.
**Flagged rather than silently fixed**, per the intake rule; the compliant pattern this TAD documents is:

- The intake bearer token / shared secret (and the Gravity Forms REST credential, if the REST-pull fallback is
  adopted) is held in a **Dataverse secret-type environment variable backed by Azure Key Vault** — the only
  platform-approved secret mechanism for Power Platform. It is never a plain environment variable (readable by
  any maker), never in flow definition JSON, and never in the committed solution (C-TECH-001, C-TECH-031).
- **Azure Key Vault is OUT-OF-PALETTE** (an Azure service beyond Entra ID) and no source document evidences
  that Revitalise has an Azure subscription. It is recorded as an out-of-palette dependency in the Adoption
  Report and as a §12 provisioning item needing a reviewer decision.
- **Preferred alternative that removes the secret entirely:** adopt the **scheduled REST pull** as the primary
  intake instead of the inbound webhook (ADR-011). This reverses the trust direction — the service account
  calls out, so there is no public endpoint to protect — but it reintroduces batch latency, which is one of
  the problems the programme exists to remove. A third option is Entra ID OAuth on the request trigger, which
  requires Alex to implement a client-credentials token call in WordPress.
- All other integrations use **OAuth connections owned by the service account** through connection
  references, so no credential material is handled by the solution at all.

### 6.4 DLP connector policy (C-TECH-045)

Applied at environment level to **all three** environments — DEV, TST/ACC and PRD (NFR-007, ADR-006). The source's business group **omits two
connectors the design actually uses** — flagged, because a DLP policy that omits a used connector silently
disables the flow on import.

| Group | Connectors |
|---|---|
| **Business** (may share data) | Microsoft Dataverse, SharePoint, Office 365 Outlook, Microsoft Teams, Approvals, AI Builder, DocuSign, QuickBooks Online, **Request/HTTP** ⚠️ *added — the intake trigger; the source flags it as premium with DLP implications but leaves it out of the group*, **Word Online (Business)** ⚠️ *added — trustee-pack generation, in the integration register but not the DLP group* |
| **Blocked** | Consumer social, personal storage, and every connector not listed above — blocked in all three environments |

### 6.5 Audit integrity and audit administration (C-DOM-012 — DERIVED)

No source document addresses audit-log integrity; SDD §7.9 marks it architecture-level and unresolved.

- The Dataverse audit store is **written by the platform and is not an application table**. No security role
  can update or delete an individual audit record through the app, the API or a flow — it is append-only by
  construction.
- **Audit administration is separated from application administration.** The `REV Admin` role is a custom
  role that **must not** carry the audit-deletion privilege (`prvDeleteAuditPartition` / bulk audit delete),
  and neither Emily nor the service account holds the Dataverse **System Administrator** or Power Platform
  Administrator role. Those sit with the tenant admin (Wanstor / the maker), who has no application role and
  no business reason to read grant data. Deleting audit history therefore requires a different person with a
  different role — the separation that makes the trail tamper-evident.
- **Audit retention: 6 years — ✅ CONFIRMED by the reviewer (Xander Lykopoulos) on 2026-08-10** (C-DOM-013).
  No source document stated a period; the value was derived to match the longest personal-data retention
  period so the trail covers the full life of every record class, and is now a confirmed architectural
  decision rather than a proposal. Dataverse audit retention is therefore set to **6 years** on all three
  environments (DEV, TST/ACC, PRD) as a `post_deploy` configuration item (§12).
  The tension this resolves, recorded for the record: audit rows contain before/after values of Tier 4
  columns, so a retention period **longer** than 6 years would keep personal data beyond the deletion of the
  record it describes and undercut Art. 5(1)(e); a **shorter** one would leave part of a granted record's life
  unevidenced. Six years is the only value that satisfies both. Risk A-R11 is closed by this decision.

### 6.6 Privileged actions require elevated authorisation (C-DOM-021 — DERIVED)

Also unresolved in every source; SDD §7.9 assigns it here.

| Privileged action | Elevated control |
|---|---|
| Create / modify the recurring **bulk-delete jobs** | Environment System Administrator (tenant admin) only. Not available to `REV Admin`. Applied as a reviewed `post_deploy` provisioning step, never ad hoc |
| **On-demand erasure** run | Triggered by `REV Admin`, but every run writes the evidence log with actor, record reference, rule applied and legal-hold outcome (FR-054), and the DPO is notified of the action. The legal-hold carve-out is evaluated by the flow, not by the operator (FR-052) |
| **Bulk export** | The `REV Trustee` role carries **no export-to-Excel privilege** — the sanctioned offline route is the anonymised pack. Export from the Admin/Finance roles is audited by app-access and field-change auditing |
| **Admin configuration** — thresholds, Likert map, redaction threshold | `REV Admin` only, through the `rev_setting` table, **with auditing enabled on that table** so every threshold change is evidenced against the decisions it affected (FR-017, FR-018) |
| **Role membership change** | An Entra group membership change, governed by the tenant joiner-and-leaver process run with Wanstor; the DPO is notified of any change to who can read special-category or finance data (Security Model §8). **Review cadence: every 6 months — ✅ CONFIRMED by the reviewer on 2026-08-10.** This **supersedes** the Security Model §8 and SDD §7.9 working assumption of "quarterly, or at the start of each panel round", and closes SDD OQ-008 (C-DOM-022) |
| **Solution import to PROD** | Managed solution only, behind the pipeline's approval gate (§9). No direct edit in PROD |
| **Audit deletion** | Separated to the tenant admin (§6.5) |

### 6.7 App registrations and API permissions (C-TECH-043)

**REQUIRED — ADR-007 is settled (Power Platform Pipelines), and these registrations are still needed.** The
earlier text made them conditional on the pac-CLI route; that was wrong even under Pipelines. GitHub Actions
still authenticates to DEV to run the build gates and to stage the unmanaged solution, and the CI jobs still
verify the promoted version and run the per-environment provisioning scripts. What Pipelines removes is the
*import into TST/ACC and PRD*, not the need for a CI identity.

**Updated 2026-08-12 — the single deploy registration is now three, one per target environment (ADR-007,
ADR-021).** Least privilege, with justification for anything broad:

| Registration | Permissions | Justification |
|---|---|---|
| `rev-grantautomation-deploy-dev`<br>`rev-grantautomation-deploy-tstacc`<br>`rev-grantautomation-deploy-prd` | Each: Dataverse `user_impersonation`; a Dataverse **application user in its own environment only**, holding a `REV Deployment` role (solution import + customisation privileges) — **not** System Administrator. Each holds **exactly one** federated credential, subject `repo:<org>/<repo>:environment:<dev\|tst_acc\|prd>`, and **no client secret** | Solution import/export and pipeline promotion, scoped per environment. **C-TECH-044 is satisfied, not merely preferred** (ADR-021): the credential is a GitHub OIDC federated credential consumed by `pac auth create --githubFederated`. **Three registrations rather than three credentials on one** because credential-only scoping gates token *issuance* but not *authority* — every subject would resolve to one service principal that is an application user in all three environments, so a token minted by the TST/ACC job could import into PRD. Splitting the registration makes the boundary "this identity does not exist in PRD", which is what C-TECH-043 asks for. Cost: three registrations, and the `entra.appRegistrations` block in `test-settings.json` and `prd-settings.json` is no longer identical. No extra consent surface: all three request only Dataverse `user_impersonation` |
| `REV-MS-Provisioning` | Microsoft Graph `Group.Create` + `GroupMember.ReadWrite.All` (application); SharePoint `Sites.Selected` scoped to `/sites/grants` | Creates the five Entra security groups and the signed-PDF library. **`Sites.Selected` is chosen specifically to avoid `Sites.FullControl.All`.** `GroupMember.ReadWrite.All` is tenant-wide and is the narrowest permission that can manage group membership — justified here and recorded in **ADR-018**; scoped by the `APPROVE TENANT` gate and the Deployment Summary record (C-TECH-041) |

No app registration is used by the running solution. The trustee portal is a **Code App** (ADR-003,
confirmed), so its data access goes **only** through managed connector data sources
(`pac code add-data-source`) — no hand-rolled token acquisition or credential handling
(C-TECH-048, development-agent scope).

---

## 7. Non-Functional Decisions

Every NFR in SDD §5 is answered with an architectural decision. Four (NFR-022 to NFR-025) are recorded gaps
in the SDD — no threshold exists to design against, so the decision states what the architecture *enables*
and what input is still needed.

| NFR ID | Decision | Rationale |
|---|---|---|
| NFR-001 | Raw narrative, "other condition" notes and ethnic group are Tier 4 columns in the `REV_TrusteeRestricted` column security profile, readable by `REV Admin` and `REV Service Automation` only. ⚠️ **Corrected 2026-08-27 (SDD Amendment A-05, Finding 3).** This row previously also named the **condition profiles**. That was inaccurate and had been since before A-05: `rev_conditionprofile` and `rev_supportrecipientconditionprofile` carry `IsSecured=0` and are absent from the profile — **verified live in DEV on 2026-08-27**, not inferred from source. They are **trustee-visible by design** under §3.1's stated rule, *categorical answers are trustee-visible; identity and free text are not*, and §3.1's own rows have always said so. The control is unchanged and nothing moved out of the profile; only this description was wrong | Column security is enforced by the platform below the app layer, so no app, view, export or flow can bypass it (ADR-002). A condition *category* is what a trustee is meant to weigh; a condition described in free text is not, which is why the raw columns are secured and the profiles are not |
| NFR-002 | Bank Account and Payment tables are excluded from `REV Admin` **at table level**, and every column additionally sits in `REV_FinanceOnly` | Table-level denial plus column security is defence in depth; separation of duties survives a role misconfiguration |
| NFR-003 | Identity never reaches a trustee-facing view because the columns are filtered by profile **before the app loads them** — not hidden in the UI. ⚠️ **Strengthened 2026-08-27 (A-05, delta TAD ADR-032):** the trustee portal additionally **never selects a secured column at all**, so identity is withheld by two independent mechanisms — the platform's, and the app's own query. FR-078's "restricted" state is rendered from a build-time field catalogue derived from `FieldSecurityProfiles.xml`, not from a null returned by a query. This matters because the same app is read by the **process owner**, who *is* a profile member (§6.1): a query-based approach would have shown her real values on a screen designed to be anonymous | A UI-level control can be bypassed by export, API or a shared link; a platform control cannot. And a platform control that returns different data to different readers of the *same* screen is not, by itself, an anonymity guarantee — which is why the app declines to ask as well |
| NFR-004 | MFA for all staff, trustee and service-identity sign-ins; the service account's Conditional Access exception is **scoped**, not a blanket MFA exemption | Unattended flows must not be blocked by interactive-sign-in policy, but the account stays governed (Security Model §7) |
| NFR-005 | Per-environment Entra security groups (`REV-GrantApplications-DEV/PROD`) gate environment access ahead of any role | Outer gate / inner gate model; membership managed in one place (§6.1) |
| NFR-006 | All external connections are OAuth connections owned by `svc-grantautomation`, bound via the four connection references | Survives staff changes; governed centrally; no personal login in the runtime path |
| NFR-007 | Environment-level DLP policy on all three environments (DEV, TST/ACC, PRD), business group as §6.4 — **with Request/HTTP and Word Online (Business) added** | The source's group omits two used connectors; a DLP gap silently disables flows on import |
| NFR-008 | Bearer token / shared secret validated as the first action of the intake flow, before any Dataverse write; secret held per §6.3 | Rejects unauthenticated callers at the boundary (C-TECH-006) |
| NFR-009 | UK region for all three environments; UK residency configured for AI Builder, DocuSign and QuickBooks; **verified at setup and recorded as evidence**, not assumed | No source evidences verification; DPIA action A5 is open (risk A-R19) |
| NFR-010 | Four native recurring Dataverse bulk-delete jobs — 6-year, 12-month, 6-month, **plus the derived orphaned-Applicant sweep** — running monthly against status-plus-date queries; cascade removes the case | Native, status-aware, no licence beyond Dataverse, logged as system jobs (ADR-004). No deletion depends on a person remembering |
| NFR-011 | Dataverse point-in-time restore window (7 days by default) sits far inside every retention period; backups remain in the UK region. Third-party backup tooling, if any, must be confirmed | A backup that outlives the retention period is an ungoverned copy. SDD OQ-019 open |
| NFR-012 | `rev_errorlog` schema physically cannot hold personal data — flow name, run ID, error message, record reference, timestamp, severity only. Notification payloads carry references, not narratives | Constraining the schema is stronger than instructing the developer (see the §5.14 pseudonymity caveat) |
| NFR-013 | The data model carries only the columns needed to assess, decide, pay and report; `rev_agerange` and `rev_locationarea` are derived at intake so trustees never need the precise values | Minimisation designed into the schema (Art. 5(1)(c)) |
| NFR-014 | Native Dataverse field-change auditing at environment and table level on all ten tables — timestamp (UTC), actor, action, record ID, before/after | Platform-native, not bolt-on; satisfies C-DOM-010/011 without custom code |
| NFR-015 | App-access logging enabled; trustee portal opens are recorded with user and timestamp | Security Model §8 |
| NFR-016 | Retention/erasure evidence log holds record reference, data type, date and rule only; bulk-delete runs additionally recorded as Dataverse system jobs | Durable evidence with no second copy of personal data (FR-054) |
| NFR-017 | Redaction confidence threshold is a `rev_setting` row (`RedactionConfidenceThreshold`, initial 85%), read at run time | Adjustable after launch with no redesign and no solution import (NFR-019) |
| NFR-018 | Trustee visibility requires `rev_eligibleforround = true` **and** `rev_redactionreleased = true`; both default false, so the flow **fails closed** | 100% of low-confidence redactions and Borderline outcomes reach a human because the default state is *withheld*, not *shown* |
| NFR-019 | All tunables in the `rev_setting` table (process-owner editable through the MDA); only per-environment values in environment variables (`rev_SignedDocLibrary`, `rev_ServiceMailbox`, `rev_DefaultThreshold`) | Environment variables need maker-portal access and a solution context; a Dataverse table row does not. ADR-010 |
| NFR-020 | Reading-age ~12 applies to the WordPress form (built by Alex to the supplied specification) and to every applicant-facing message a flow sends. The specification handed to Alex must carry it as an acceptance criterion | The applicant-facing surface is out-of-palette, so the requirement travels as a specification obligation, not a build task (§8) |
| NFR-021 | ~200 applications/year with headroom to 250 and 300+ cumulative grants is **far** inside Dataverse limits; the constraint is licence seats and AI Builder credits, not platform capacity | Scale risk here is commercial, not technical (SDD OQ-017) |
| NFR-022 | **No performance threshold exists in any source (SDD OQ-020).** Architecture position: intake is event-driven so an application exists within seconds of submission; scoring is a single-row flow; the only long-running operations are the narrative flow (AI Builder call per record) and the batch envelope run, both asynchronous with no user waiting. **No measurable target is committed — a threshold is needed before the test-agent can test it** | Recording the gap rather than inventing a number |
| NFR-023 | **No availability target exists (SDD OQ-021).** Architecture position: availability is the Power Platform SLA; the design's own resilience is the documented fallback per integration (§4) and the fail-closed narrative flow. The reviewer should confirm whether the board-cycle week and the application round are periods where downtime is unacceptable | Recording the gap |
| NFR-024 | **No accessibility standard is named in any source (SDD OQ-022).** Derived: **WCAG 2.1 AA** as the baseline (`skills/accessibility-checklist.md`), with **WCAG 2.2 AA recommended** for the applicant-facing form. See §8 and ADR-020 | The applicant population is disabled people and unpaid carers with ~age-12 average reading level; this is the least defensible gap in the source set |
| NFR-025 | **No SAR/erasure turnaround SLA exists (SDD OQ-023).** The capability is designed (§4.2, §5.12) but the statutory one-month Art. 15 period is the only benchmark available | Recording the gap; the DPO must set the internal target |

---

## 8. Accessibility

**No source document names an accessibility standard.** This is recorded in SDD NFR-024 / OQ-022 and is the
gap with the largest human consequence in the set, because the applicant population is disabled people and
unpaid carers applying while under strain, with an average reading level around age 12.

**Derived standard: WCAG 2.1 Level AA** as the project baseline — the standard `skills/accessibility-checklist.md`
mandates for every new or modified UI. **WCAG 2.2 AA is recommended** for the applicant-facing form
specifically: its additions (2.4.11 focus not obscured, 2.5.7 dragging movements, 2.5.8 target size minimum,
3.2.6 consistent help, 3.3.7 redundant entry, 3.3.8 accessible authentication) map directly onto the
difficulties this population has with long forms. **Reviewer decision — ADR-020.**

| Surface | Palette status | Accessibility obligation |
|---|---|---|
| **Application form** — WordPress / Gravity Forms | **OUT-OF-PALETTE** — built by Alex | The highest-stakes surface and the one this system does not build. WCAG 2.1 AA (2.2 AA recommended) must be an **acceptance criterion in the field-by-field specification handed to Alex**, along with NFR-020's reading age, visible labels not placeholder-only (3.3.2), errors identified in text and not by colour (1.4.1, 3.3.1), a progress indicator that is announced not just drawn (FR-004), save-and-resume without a time limit (FR-005, 2.2.1), and a pre-submission summary with per-section edit (FR-006, 3.3.4) |
| **Trustee portal** — Code App (ADR-003, confirmed) | In-palette | Fluent UI React components with semantic landmarks; full keyboard operability of the sortable/filterable list (FR-034) including sort controls as real buttons; visible focus; unique page titles; status messages via `aria-live` when a verdict saves; 44×44px targets; contrast ≥ 4.5:1; **no information conveyed by colour alone** — status and verdict carry text labels. Verified by axe-core in CI plus manual keyboard and screen-reader passes (automated tools catch only 30–40%) |
| **Print / offline export** (FR-039) | In-palette | The print stylesheet must preserve heading hierarchy and reading order, and must render the same anonymised content — an export that leaks a column the screen hides would be a disclosure, not an accessibility defect |
| **Anonymised document pack** (FR-032) | In-palette | Tagged PDF from the Word template with real heading styles and a document language, so a trustee using a screen reader can navigate it. This is the fallback that exists so no trustee is excluded (US-014) — an untagged PDF would defeat its purpose |
| **Grant Administration MDA** | In-palette | Inherits Model-Driven App platform accessibility; custom columns need meaningful display names, and the `rev_setting` editing surface must not rely on colour to convey which threshold is active |

Trustees are themselves an older cohort in many charities; the offline pack and the print route are
accessibility features, not just adoption features.

---

## 9. Deployment Topology

✅ **CONFIRMED by the reviewer (Xander Lykopoulos) on 2026-08-10 — three environments: DEV, TST/ACC, PRD.**
This is the three-environment middle option this TAD proposed (ADR-006, now `Adopted`). It supersedes both the
source's two-environment topology (DEV/PROD) and this system's four-environment default
(Dev → Test → Acc → Prd). **Test and Acceptance are combined into a single environment, `TST/ACC`.**

**Promotion path: DEV → TST/ACC → PRD.**

| Environment | Method | Notes |
|---|---|---|
| **DEV** | `Revitalise – Grant Automation (DEV)`. Managed Power Platform environment, Dataverse enabled, **UK region**. Holds the **unmanaged** (editable) solution. Access gated by `REV-GrantApplications-DEV`. Xander (maker) + service account | **Synthetic / anonymised test data only — no real applicant PII** (source §3; C-TECH-007). All building and iteration happens here. Code App published with `pac code push` during build |
| **TST/ACC** *(Test and Acceptance combined — the confirmed topology)* | `Revitalise – Grant Automation (TSTACC)`. Managed environment, Dataverse enabled, **UK region**. Receives the **managed** solution as the first managed import. Access gated by a third environment security group, `REV-GrantApplications-ACC` (§12). Service account + maker + Emily and at least one trustee for acceptance | **Serves both functions on one environment:** (a) the **test-agent gate** — managed-import behaviour, connection-reference re-binding, environment-variable substitution, EasyRepro for the MDA, Playwright for the Code App; (b) **UAT** — Emily's walkthrough per automation and the trustee portal demo round. **Synthetic / anonymised data only** — it is not a production-data environment (C-TECH-007) |
| **PRD** | `Revitalise – Grant Automation (PROD)`. Managed environment, Dataverse enabled, **UK region**. Receives the **managed** (locked) solution; **no direct edits**. Access gated by `REV-GrantApplications-PRD`. Service account owns and runs all flows and connections | Real applicant data under the Data Governance Framework. Promotion: increment version → export managed → import → map the four connection references to service-account connections → set the three environment variables → smoke-test one controlled application end to end, including a deliberate failure to confirm the Error Log and Failure Alert fire → enable live triggers (ALM Runbook §4) |

### 9.1 ⚠️ Pipeline gate structure changes — pipeline-agent must apply this

**This is a deliberate, recorded deviation from `agents/WORKFLOW.md`, not a silent one.** The three-environment
topology changes the gate chain, and `config/revitalise-grant-automation-pipeline.yml` must be built to the
right-hand column:

| | WORKFLOW.md default (four environments) | **Confirmed for this feature (three environments)** |
|---|---|---|
| Stage 0 | Tenant prerequisites `[APPROVE TENANT]` | Tenant prerequisites `[APPROVE TENANT]` — **unchanged** |
| Stage 1 | `Dev → Test` (auto) | **`Dev → TST/ACC`** (auto) — carries the test-agent gate |
| Stage 2 | `Test → Acc` `[APPROVE ACC]` | **removed — no separate Acc hop exists.** `APPROVE ACC` is **no longer applicable as its own gate step** |
| Stage 3 | `Acc → Prd` `[APPROVE PRD]` | **`TST/ACC → Prd`** `[APPROVE PRD]` — unchanged keyword, different source environment |

Consequences pipeline-agent and test-agent must account for:
- **Two hops, not three.** The promotion chain is `Dev → TST/ACC → Prd`.
- **`APPROVE ACC` is not a step.** Acceptance sign-off happens **inside** the TST/ACC stage, alongside the
  test-agent gate, rather than as a separate environment promotion. If the reviewer wants acceptance recorded
  as an explicit human keyword, the practical option is to require **both** the test-agent `APPROVED` gate and
  an acceptance confirmation before `APPROVE PRD` — that is a pipeline-config choice, and the default
  behaviour is that `APPROVE PRD` is the single remaining human deployment gate after Stage 0.
- **`ENV_URL_TEST` and `ENV_URL_ACC` collapse to one value.** `knowledge/technology/build-and-deploy.md`
  defines both; this feature uses a single TST/ACC environment URL. The pipeline config must not assume two
  distinct downstream non-production environments.
- **Deployment Summary** (C-TECH-032) records two promotions per release, not three.
- **A third environment security group is required** — `REV-GrantApplications-ACC` — added to §12.

### 9.1.1 What this decision buys, and what it gives up

- **Buys:** a real managed-import test gate. The first managed solution import in the project's life now lands
  in TST/ACC, not PROD, so connection-reference re-binding and environment-variable substitution — the things
  that break first and do not exist in an unmanaged Dev environment — are exercised before production. **Risk
  A-R15 is closed by this decision.**
- **Gives up:** a separate acceptance environment. UAT runs on the same environment as testing, so an
  acceptance session can be affected by test data or an in-flight test run. Mitigation: reset or segregate
  test data before each acceptance session, and treat the PROD smoke test with one controlled application
  (ALM Runbook §4) as the final acceptance evidence.
- **Costs:** one additional Dataverse-enabled environment beyond the source's two, consuming chargeable
  database capacity (risk A-R18). Capacity should be confirmed at WBS 0.2 before provisioning.

### 9.2 ALM tooling — ✅ **RESOLVED: Power Platform Pipelines (ADR-007, `Adopted` 2026-08-12)**

**Confirmed by the reviewer (Xander Lykopoulos) on 2026-08-12.** This supersedes this TAD's own earlier
recommendation of pac CLI + GitHub Actions. Both tools are retained; what was decided is the **boundary**
between them. ADR-007 carries the full decision, the citations, and an honest account of why the earlier
recommendation lost. The short version:

| Aspect | **GitHub Actions** (`.github/workflows/ci.yml`) | **Power Platform Pipelines** |
|---|---|---|
| Scope | `validate` → `build` → `stage-dev` | `DEV → TST/ACC → PRD` (two hops, §9.1) |
| Source of truth | Unpacked solution at `src/solutions/RevitaliseGrantAutomation/` in **this** repo | — consumes DEV's unmanaged solution |
| Validation | The 15 build gates in `config/…-build.yml` | Pre-flight against each target: dependencies, connection references, environment variables |
| Artefact | `build/artifacts/` — build/audit record, **no longer the deployed bits** | Exports from DEV itself; stores managed + unmanaged immutably in the host; promotes the *same* artefact to each stage |
| Environment values | Settings files retained as the reviewed record only | Collected in its own deployment pane; **no settings file accepted** |
| Rollback | — | Redeploy a previous version from run history (pipeline setting must be enabled) |

**The hand-off point is `stage-dev`: import the UNMANAGED solution into DEV, with `--publish-changes`.**
It could not have been anything else. Pipelines cannot be handed a pre-built artefact — it exports from the
development environment when a deployment is requested — so the only way this repository's source reaches a
Pipelines deployment is for DEV's unmanaged solution to match the repository. `--publish-changes` is
load-bearing because Pipelines does not publish unmanaged customisations before exporting.

**Promotion is manual for the first release, by design.** `pac pipeline deploy` is a real, documented,
locally-verified command, but two things about invoking it from CI could not be verified — whether a *service
principal* may **request** a promotion, and the semantics of `--currentVersion` / `--newVersion`. The `cli`
path is implemented and switchable per environment; `promote_mode: manual` is the default until one UI-driven
promotion settles both. Detail in `config/revitalise-grant-automation-pipeline.yml` → `alm.promotion_mechanism`.

**What this costs, recorded here so §12 is not read as unchanged:** a custom **pipelines host** environment
that does not exist yet, and **Managed Environment status on TST/ACC and PRD**, which requires premium use
rights. Both are new §12 tenant prerequisites. `major.minor.build` versioning and the ALM Runbook's
pre-deployment checklist are adopted unchanged, as they would have been either way.

### 9.3 Code App deployment

The trustee portal is a Code App (ADR-003, confirmed), so this section applies. The Code App is added to the
feature solution in Dev so TST/ACC and PRD receive it inside the managed import. `dist/` and `node_modules/`
are gitignored; `power.config.json`, `src/**` and the generated data-source services are committed.

**The open deviation recorded here is now CLOSED, and the answer is the preferred route.** This section
previously carried a conditional — *"if the tenant does not yet support solution-packaged code apps,
`pac code push` runs per environment as a `post_deploy` step"* — because nobody had pushed a code app in this
tenant and the behaviour was genuinely unknown. It was settled by observation on **2026-08-23** (`IMP-0223`),
not by reading documentation:

> After `pac code push --solutionName RevitaliseGrantAutomation` succeeded against DEV,
> `solutioncomponents?$filter=_solutionid_value eq <id>` returned **componenttype 300** with exactly one row
> whose `objectid` (`70869c95-92e5-442f-b5b9-44b3d3e549f6`) is the Code App's own `appId` — identical to
> `pac code list` and to `power.config.json`. Componenttype 300 is the same code documented for Canvas Apps.

A pushed Code App therefore **is** a solution component and travels with the managed export like any other.
The per-environment-push alternative is not needed on this project's ALM path (Power Platform Pipelines,
ADR-007), and `config/revitalise-grant-automation-pipeline.yml` no longer declares a second push for TST/ACC
or PRD.

**Scope of the evidence, per `C-TECH-053`:** verified in DEV only. That the component *survives the managed
export* into TST/ACC has not been observed by anyone yet. Read the same query in the target environment after
the first promotion and record the result there — do not infer it from this paragraph.

### 9.4 The finance capture app (`wbs:8.3`) — artefacts, and the gate it newly activates

**Added rev 5. Re-derived rev 6 for the area design (`ADR-048`), not patched.** The payment capture
surface ships **inside the existing `config/revitalise-grant-automation-build.yml` and
`-pipeline.yml`**; no new build or pipeline config is created, and no new provisioning script is
written.

| Artefact | Path | New / changed |
|---|---|---|
| App membership | `AppModules/rev_grantadministration/AppModule.xml` — three `<AppModuleComponent type="1" schemaName="rev_provider\|rev_bankaccount\|rev_payment" />` lines | Changed, 3 lines |
| Navigation | `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` — three `<SubArea Entity="…">` under the **existing** `rev_group_finance` group, which today holds only `rev_sub_roundfinance` | Changed |
| Root components | `Other/Solution.xml` | **Unchanged.** All three tables are already `<RootComponent type="1" … behavior="0" />`, and `behavior="0"` carries their forms and views with them. Rev 5 predicted two new lines (`type="80"`/`type="62"`) for a separate app; that app is not being built |
| Main forms + views | `Entities/{rev_provider,rev_bankaccount,rev_payment}/FormXml/` and `SavedQueries/` | New — unchanged from rev 5 |
| App share + profile member | `provisioning/deploymentSettings/*.json` | Changed — **data only**, and now **one fewer change than rev 5**: `REV Finance` is added to the *existing* app's `securityRoles` array rather than a new `dataverse.apps[]` entry being created. `share-apps.ps1` and `ensure-column-security-profile-members.ps1` are already data-driven |

**Every artefact above is on the import-creatable side of `C-TECH-050`**, so `wbs:8.3` adds no new
per-environment prerequisite. The only prerequisite in its path is a role it does not build (§6.2.1).

**Three gate consequences, read from the build config's own `steps:` block rather than from memory.**
The steps that can see this change are `root-components-resolve`
(`config/revitalise-grant-automation-build.yml` `steps:`), `forms-and-views-reachable` and
`shipped-content`. `root-components-resolve` is **not** exercised, because `Other/Solution.xml` does
not change.

1. **`forms-and-views-reachable` reachability half — already satisfied by luck and worth keeping.**
   `pac solution pack` silently drops a `FormXml/` or `SavedQueries/` folder unless the entity
   declares the empty marker elements. **All three finance tables already declare both**, with
   empty folders — which is why that step emits six harmless warnings about them today. Adding
   files converts each warning into a packable component with **no `Entity.xml` edit**.

2. **`C-TECH-077` newly applies to 16 columns, and this is the one to get right.** That HARD
   assertion — *a column secured for capture has a control on its table's main form* — applies
   only to a table that **has** a `FormXml/main/` form. `rev_bankaccount` and `rev_payment` have
   none today, so their 16 secured columns are outside its scope: the current run reports
   **53 secured columns with a main-form control across 13 entities** and exits 0 without
   considering them. **Creating a main form on those two tables brings all 16 into scope in the
   same change.** The design satisfies it the simple way — every column of both tables appears on
   the main form, which FR-150/151/152 want anyway — giving a predicted **69 across 15 entities**.
   That figure is a **prediction, not a measurement**: development-agent re-runs the step and
   reports the actual, so a disagreement is visible rather than absorbed. **Unchanged by rev 6** —
   column security sits below the app layer, so it does not matter which app the form lives in.
   Measured baseline today: *53 secured columns with a main-form control across 13 entities, 12
   warnings, exit 0*.

3. **`shipped-content` is newly exercised, and it is the step that makes the area design safe.**
   Its checks 1 and 1b implement the rule that adding a table to a model-driven app is **four
   changes** — the entity, a SubArea, an `<AppModuleComponent type="1">`, and the environment's
   audit switch — and it covers the first three. Today it reports *7 entities with UI, all
   reachable across 1 site map*; the three finance tables are outside its scope only because their
   `FormXml/` and `SavedQueries/` folders are empty. **Adding the forms and views brings all three
   into scope in the same change**, so a SubArea without its matching `AppModuleComponent` — the
   defect that shipped once here and was found by the reviewer in play mode, not by any gate —
   fails the build. Predicted after this work: **10 entities with UI, all reachable across 1 site
   map**. A prediction, not a measurement.

   **This step is also why `ADR-044` would have failed the build, which was not known when it was
   written.** Check 1b loops over **every** app module and requires every entity referenced by
   **any** site map to be an `AppModuleComponent` of **that** app. A second app containing only the
   three finance tables would therefore have been reported as missing `rev_applicant`,
   `rev_application`, `rev_grant`, `rev_review`, `rev_setting`, `rev_errorlog` and
   `rev_roundfinance` — seven `APP MEMBERSHIP` errors on a HARD step, for a solution that was
   correct. `ADR-044` named `forms-and-views-reachable` and `root-components-resolve` and did not
   enumerate this one. Recorded in `ADR-044`'s rejection consequences.

**One ordering fact, already true and not resequenced:** `share-apps.ps1` requires the app module
to exist, and says so itself (*"app module 'x' not found — import the managed solution first"*).
It already runs in `post_deploy`, after import. Under `ADR-048` the app module it names already
exists and is already shared, so the only change is one more role name in an existing array.

### 9.4.1 The `wbs:8.3` evidence rule in `contract/evidence-map.json` is now wrong — the correction, for `pm-agent`

`contract/evidence-map.json` is `pm-agent`'s file and is **not** edited here, exactly as §6.2.1's
two role-privilege corrections were specified for `wbs:8.2` without being built here. `wbs:8.3`'s
only rule today is a directory-existence check on
`src/solutions/RevitaliseGrantAutomation/AppModules/rev_financecapture`. That directory will never
exist: `ADR-044` is rejected. The rule is therefore not merely weak — it is **unsatisfiable**, and
`wbs:8.3` can never derive as complete while it stands.

The replacement must name **one file and one granted element per rule**, never a directory glob plus
a substring — that is the shape a rule regressed into on `wbs:8.2` and had to be rewritten twice.
Five rules, each satisfiable only by the deliverable actually existing:

| # | `kind` | `file` | `pattern` |
|---|---|---|---|
| 1 | `grep` | `src/solutions/RevitaliseGrantAutomation/AppModules/rev_grantadministration/AppModule.xml` | `<AppModuleComponent\s+type="1"\s+schemaName="rev_payment"` |
| 2 | `grep` | `src/solutions/RevitaliseGrantAutomation/AppModules/rev_grantadministration/AppModule.xml` | `<AppModuleComponent\s+type="1"\s+schemaName="rev_bankaccount"` |
| 3 | `grep` | `src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` | `<SubArea[^>]*\sEntity="rev_payment"` |
| 4 | `grep` | `src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` | `<SubArea[^>]*\sEntity="rev_bankaccount"` |
| 5 | `path` | `src/solutions/RevitaliseGrantAutomation/Entities/rev_payment/FormXml/main` | — |

**Why these five and not others.** Rules 1–4 are the two halves the platform requires and that a
site map alone does not give: a SubArea makes the table appear in the app **designer**, and only the
`AppModuleComponent` makes it render for a user. Naming both halves for both secured tables means no
single edit can satisfy the rule while leaving the surface unusable. Rule 5 is what makes the task's
own deliverable — a capture **form** — the thing being proved, rather than navigation to an empty
table; it is the one rule here that a comment cannot satisfy, because `FormXml/main` is a directory
the packer reads. `rev_provider` is deliberately **not** named: it is an unsecured supporting table
and `wbs:8.4` already has its own rule over `rev_payment`'s lookups.

**And assert the negative before accepting the change.** Re-run
`python3 scripts/derive-wbs-state.py` and confirm `wbs:8.3` reads **not complete** against the
repository as it stands today — none of the five artefacts exists yet. A tightening nobody watched
fail is a tightening nobody has tested.

---

## 10. Architecture Decision Records

`Adopted` = the source made this decision and it is carried over unchanged. `Derived` = the architect made it
because the source left a gap this system's constraints do not allow to stay open. `Decision required` = two
defensible positions exist and the reviewer chooses.

### ADR-001: Dataverse as the system of record, replacing the SharePoint baseline
**Status:** `Adopted` (source v0.4, superseding v0.3) · **Date:** 2026-08-10
**Context:** v0.3 based the solution on SharePoint lists. The retention schedule requires status-aware
scheduled deletion; the trustee control requires column-level security; the audit obligation requires
field-change auditing. SharePoint provides none of the three.
**Decision:** Dataverse is the system of record and the integration hub. Ten custom tables. One SharePoint
library retained for the signed PDF only.
**Consequences:** *Positive* — relational integrity, cascade delete, native bulk-delete retention, column
security, native auditing, no "single source of truth on a laptop". *Negative* — Dataverse is a premium data
source: every app user needs a per-user Power Apps Premium entitlement, moving the recurring licence bill from
~£150–180/yr to ~£750–1,000/yr at list (~£370–500 at nonprofit). *Neutral* — build cost is neutral to slightly
faster; the change raises the licence bill, not the build hours.

### ADR-002: Field-level (column) security as the trustee anonymisation control
**Status:** `Adopted (conditional — DPO sign-off, SDD OQ-004)` · **Date:** 2026-08-10
**Context:** The documented process mandates manual anonymisation by a single key holder — 3–4 hours per board
cycle, twelve cycles a year, where one missed indirect reference ("my husband John") is a personal-data breach.
**Decision:** A Dataverse column security profile (`REV_TrusteeRestricted`) hides identifying columns from the
Trustee role so they never reach the trustee app. AI Builder redacts only the free-text narratives. Structured
identifiers are hidden, not scrubbed.
**Consequences:** *Positive* — platform-enforced rather than person-enforced; cannot be bypassed by export, API
or view; removes 36–48 hours a year. *Negative* — it is a **stronger but different** control from the one the
DPO's documented process describes, so build must not start on this basis until OQ-004 is answered. If physical
separation is required instead, the fallback is a separate trustee-facing table kept in sync — a design change
the architect must size, not a configuration change. *Neutral* — condition profiles remain trustee-visible by
design; the case is what trustees weigh, the person is not.

### ADR-003: Trustee portal application type — Code App
**Status:** ✅ `Adopted` — **confirmed by the reviewer (Xander Lykopoulos) on 2026-08-10** · **Date:** 2026-08-10
**Context:** The source was deliberately open: the component map says "Dataverse canvas / model-driven app", and
the Solution Design says twice that "the recommended approach is a Dataverse app (a **Code App or Canvas
App**)". Against this system's palette, **Code App and Model-Driven App are in-palette; Canvas App is
explicitly OUT-OF-PALETTE.**
**Decision:** the trustee portal is built as a **Power Apps Code App** (React / Vite / TypeScript).
**Canvas App is descoped and rejected** as an alternative; the out-of-palette question it raised is closed.
A Model-Driven App was available as a second in-palette option and was not selected.
**Consequences:** *Positive* — in-palette, so this system builds, tests (Playwright) and ships it inside the
managed solution; `knowledge/technology/stack-overview.md` marks Code Apps "preferred over Canvas Apps"; the
sortable/filterable summary list (FR-034, Kevin's data-only view) and the print/offline export (FR-039) are
straightforward in React. *Negative* — a Code App is developer-maintained, which sits slightly against the
"maintainable by non-developers" principle, and the source's own 14–20 hour estimate assumed a low-code app,
so effort should be re-confirmed at development. Node/Vite/React toolchain and Playwright coverage are now
required (§9.3). *Neutral* — the choice does not affect the anonymisation control: the app reads the same
secured Dataverse columns whichever type is used. **C-TECH-048 now applies** — Code App data access only
through managed connector data sources (§6.7). **Risk A-R17 is closed by this decision.**

### ADR-004: Native Dataverse bulk delete + cascade, not a custom retention sweep flow
**Status:** `Adopted` · **Date:** 2026-08-10
**Context:** Retention must be status-aware, scheduled, automatic, and reconciled across four systems.
**Decision:** Recurring Dataverse bulk-delete jobs run monthly against status-plus-date queries; parental
cascade removes Review, Grant and Payment with the Application. A light Power Automate helper flow covers only
what the native job cannot reach: DocuSign envelope purge, the QuickBooks finance carve-out, on-demand erasure
and (derived) the SAR extract and orphaned-Applicant sweep.
**Consequences:** *Positive* — native, no custom sweep, no licence beyond Dataverse, each run logged as a
system job. *Negative* — bulk-delete jobs are **environment configuration, not solution components**, so they
must be provisioned per environment and cannot be version-controlled in the solution (§12). *Neutral* — this
inverts `knowledge/technology/dataverse.md`'s Restrict Delete guidance; see the §3.3 documented deviation.

### ADR-005: Purview basic retention labels as a backstop only
**Status:** `Adopted` · **Date:** 2026-08-10
**Context:** Business Premium includes basic (time-based) Purview labels; event-based retention needs E5 or the
Purview Suite add-on, priced per user across the whole tenant to serve one automation's need.
**Decision:** Basic time-based labels on the Application table and the signed-PDF library as a safety net, so
nothing survives well past its period if a job is paused. Status-aware enforcement stays with the bulk-delete
jobs. The Purview Suite add-on is not licensed.
**Consequences:** *Positive* — a second, independent line of defence at no extra cost. *Negative* — Purview is
**out-of-palette** (an M365 compliance service, not a buildable component), so label configuration is a manual
tenant task recorded in §12. *Neutral* — remains available later for tenant-wide records management.

### ADR-006: Environment topology — three environments: DEV, TST/ACC, PRD
**Status:** ✅ `Adopted` — **confirmed by the reviewer (Xander Lykopoulos) on 2026-08-10** · **Date:** 2026-08-10
**Context:** Source: DEV + PROD, "the minimum responsible separation". This system's default: Dev → Test →
Acc → Prd, with the test-agent gate at Test and an `APPROVE ACC` gate. Options presented were (a) the source's
two, (b) this system's four, (c) a three-environment middle position.
**Decision:** **option (c) — three environments: DEV, TST/ACC, PRD**, with Test and Acceptance combined into a
single `TST/ACC` environment. Promotion path `DEV → TST/ACC → PRD`.
**Consequences:** *Positive* — restores a real managed-import test gate at the lowest incremental capacity cost;
the first managed import lands in TST/ACC rather than PROD, closing risk A-R15. *Negative* — **the pipeline gate
chain deviates from `agents/WORKFLOW.md`: two hops instead of three, and `APPROVE ACC` no longer exists as its
own gate step** (see §9.1 — pipeline-agent must build `config/revitalise-grant-automation-pipeline.yml` to that
structure, and `ENV_URL_TEST` / `ENV_URL_ACC` collapse to one value). UAT shares an environment with testing, so
test data must be reset or segregated before each acceptance session. One additional Dataverse-enabled
environment beyond the source's two consumes chargeable capacity (risk A-R18), to be confirmed at WBS 0.2.
*Neutral* — a third environment security group, `REV-GrantApplications-ACC`, is added to §12.

### ADR-007: ALM tooling — **Power Platform Pipelines. `Adopted`.**
**Status:** ✅ `Adopted` — **decided by the reviewer (Xander Lykopoulos) on 2026-08-12.** Supersedes this
TAD's own earlier recommendation, which is retained below for the record. · **Date:** 2026-08-10, resolved
2026-08-12

**Context:** The source recommends Power Platform Pipelines with Azure DevOps Git as source of truth; this
system's build-agent and pipeline-agent assume pac CLI + GitHub Actions with the solution unpacked into this
repository. Both are defensible; they are not compatible without a choice. This ADR previously **recommended
the pac-CLI route** on the grounds that C-TECH-030/032/041 depend on it and that Power Platform Pipelines
"leaves the pipeline-agent with nothing to drive". **The reviewer chose Power Platform Pipelines anyway.**
That recommendation was wrong on one point of fact and overstated on another — recorded here because a
superseded recommendation is only useful if it says why it lost:

- **Wrong on fact:** Pipelines is not un-automatable from outside its own UI. `pac pipeline deploy` and
  `pac pipeline list` are a documented, supported CLI surface
  ([reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/pipeline)), and
  Pipelines exposes Dataverse business events (`OnDeploymentRequested`, `OnApprovalStarted`, …) for
  extensibility ([extend pipelines](https://learn.microsoft.com/en-us/power-platform/alm/extend-pipelines)).
  The pipeline-agent has plenty to drive.
- **Overstated on C-TECH-030:** the constraint's *purpose* — an immutable artefact, no ad-hoc deploys, and no
  bypassing of QA — is met **more strongly** by Pipelines than by the pac route, because the platform
  physically prevents it: "the system stores them in the pipelines host and prohibits any tampering or
  modification… the same managed artifact, per version, will be deployed to all subsequent stages in the
  pipeline in sequential order. This ensures no solution can bypass QA environments or approval processes."
  What changes is *who produces* the artefact — see Consequences.

**Decision:** **Power Platform Pipelines** is the promotion mechanism for DEV → TST/ACC → PRD. GitHub Actions
is retained for everything up to and including staging DEV. Neither tool is discarded; the boundary between
them is explicit and is the substance of this decision:

| | **GitHub Actions owns** | **Power Platform Pipelines owns** |
|---|---|---|
| Scope | `validate` → `build` → `stage-dev` | `DEV → TST/ACC → PRD` |
| Source of truth | Unpacked solution at `src/solutions/RevitaliseGrantAutomation/` | — (consumes DEV's unmanaged solution) |
| Validation | All 15 build gates: secret scan, XML/JSON parse, root-component resolution, field-security coverage, the FR-016 special-category grep, `pac solution check`, both `pac solution pack` runs | Pre-flight validation against each target: missing dependencies, connection references, environment variables |
| Artefact | Build/audit artefact in `build/artifacts/` — **no longer the deployed bits** | Exports managed + unmanaged from DEV itself, stores them immutably in the host, deploys the same artefact to every subsequent stage |
| Environment values | — (settings files retained as the reviewed record only) | Collected in its own deployment pane; **does not accept a settings file** |
| Gates | `APPROVE TENANT` (Stage 0); `APPROVE PRD` via GitHub Environment required reviewers | Stage order and version order enforced by the platform; optional delegated-deployment approvals |
| Rollback | — | Redeploy a previous version from run history (requires the pipeline setting) |
| Auth | GitHub OIDC federated credential, one identity per target environment | The requesting or delegated identity |

**The hand-off point is "import the unmanaged solution into DEV", and it could not have been anything else.**
Pipelines cannot be given a pre-built artefact: it exports the solution from the development environment the
moment a deployment is requested. So the only way this repository's source reaches a Pipelines deployment is
for DEV's unmanaged solution to match the repository, which is what the `stage-dev` job does. `--publish-changes`
on that import is load-bearing, because Pipelines does not publish unmanaged customisations before exporting.

**Promotion is triggered manually for the first release, deliberately.** The CLI surface is real and its
parameter shape was verified both in the Learn reference and against the locally installed `pac` 2.4.1. Two
things could **not** be verified and are recorded as open rather than guessed: (a) whether a **service
principal** may *request* a promotion — every Microsoft example has a maker requesting, with service
principals appearing only as the *delegated* identity that performs the import, or as the identity that calls
`UpdateApprovalStatus`; and (b) the semantics of `--currentVersion` / `--newVersion`. `promote_mode` is
therefore `manual` in the pipeline config, with the `cli` path fully implemented and switchable per
environment once one UI-driven promotion settles both. See
`config/revitalise-grant-automation-pipeline.yml` → `alm.promotion_mechanism`.

**Consequences:**

*Positive* — the platform, not a shell script, guarantees that the artefact promoted to PRD is byte-identical
to the one TST/ACC accepted, and that no version can skip a stage. Deployment history, artefact retention and
audit live in the host with out-of-box reporting. Connection references and environment variables are
validated *before* the import rather than discovered broken after it. The client's own ALM runbook is
satisfied without translation. One-click promotion for a charity with one maker is a real operational win.

*Negative, and none of it is cosmetic* —
1. **New tenant infrastructure that does not exist:** a **custom pipelines host** environment with the Power
   Platform Pipelines application installed, plus Environment records and a two-stage pipeline. Added to §12.
   A custom host is required rather than the auto-provisioned platform host, because platform-host pipelines
   are *personal* pipelines and "can't be extended", can't be shared, and cap at three environments.
2. **TST/ACC and PRD must be Managed Environments**, which requires licences granting premium use rights.
   This is a **licence cost the pac-CLI route did not carry**, and from February 2026 Microsoft enables it on
   pipeline targets automatically. Added to §12 and to the capacity check already required by risk A-R18.
3. **`pac-import-tstacc.json` and `pac-import-prd.json` are no longer consumed.** Pipelines does not accept a
   deployment settings file. Both files are retained as the reviewed, code-reviewed record of the values an
   operator types into the deployment pane — which keeps C-TECH-047 satisfied but moves its enforcement from
   a tool to a human reading a file.
4. **C-TECH-030's satisfaction mechanism changes.** The deployed artefact is produced by the platform, not by
   the build-agent. The constraint's intent is met (immutable, traceable, no ad-hoc deploys, no stage
   bypass), but its literal wording — "the managed/immutable artifact **produced by the build-agent**" — no
   longer describes what happens. Flagged for the Tech Lead who owns `constraints/technology/`: the
   constraint text should name the pipelines host as an acceptable artefact store. Not amended here, because
   agents do not edit constraints.
5. **Import behaviour is fixed:** "Upgrade without Overwrite customizations". `--force-overwrite` and
   `--activate-plugins` no longer apply beyond DEV.
6. **Cross-tenant deployment is ruled out** ("Can pipelines deploy to a different tenant? No."). Not a Phase 1
   need, but it closes a door.

*Neutral* — the `major.minor.build` versioning scheme and the ALM Runbook's pre-deployment checklist are
adopted unchanged, as they would have been either way. `APPROVE TENANT` and `APPROVE PRD` survive intact:
Stage 0 is unaffected, and `APPROVE PRD` is now enforced by required reviewers on the `prd` GitHub
Environment, which gates the job that performs (or hands over) the promotion.

**Related decision, recorded here because it is a direct consequence — one deploy identity per environment.**
The previous design used a single `APP_ID` + `CLIENT_SECRET` for every target. C-TECH-044's resolution to a
federated credential (below, and ADR-021) created the opportunity to scope per environment, and the reviewer
asked for that scoping to be visible rather than assumed. **Three app registrations** —
`rev-grantautomation-deploy-dev` / `-tstacc` / `-prd` — each hold **exactly one** federated credential bound
to their own GitHub Environment OIDC subject, and each is a Dataverse application user **in their own
environment only**. Separate registrations rather than several credentials on one registration, because
credential-only scoping gates token *issuance* but not *authority*: every subject would still resolve to one
service principal that is an application user everywhere, so a token minted by the TST/ACC job could import
into PRD. The boundary would have been convention. §6.7 and §12 updated.

### ADR-021: CI/CD authentication — GitHub OIDC federated credential, not a client secret
**Status:** `Adopted` — resolves C-TECH-044, which had been carried as an open SOFT warning through three Dev
Summary revisions · **Date:** 2026-08-12
**Context:** C-TECH-044 prefers federated credentials or certificates over client secrets. `.github/workflows/ci.yml`
authenticated with `APP_ID` + `CLIENT_SECRET`; both deployment settings files already declared a
`federatedCredentials` block anticipating the switch, but nothing consumed it, and the declared subject
(`ref:refs/heads/main`) would never have matched a workflow that triggers on `feature/**`.
**Decision:** Authenticate with `pac auth create --githubFederated --applicationId … --tenant …`, which
exchanges the GitHub OIDC token for an Entra token with no stored secret
([pac auth reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/auth);
[OIDC/FIC tutorial](https://learn.microsoft.com/en-us/power-platform/alm/tutorials/github-actions-oidc-fic)).
No `azure/login` step is required — pac performs the exchange itself. Each authenticating job declares
`permissions: id-token: write` and runs under a GitHub Environment, so the OIDC subject is
`repo:<org>/<repo>:environment:<name>`: a small fixed set of exact-matchable subjects instead of one per
branch name.
**Consequences:** *Positive* — no client secret exists to leak, expire or rotate; combined with the
certificate-based provisioning identity, the pipeline holds no shared secret at all. The subject is pinned to
a named environment, so a token cannot be minted from an arbitrary branch. *Negative* — `--githubFederated`
is flagged `(Preview)` in the CLI's own help output (though not in the Learn reference), so the pac version is
pinned in `.github/actions/setup-powerplatform`; and the credential must be re-registered if the repository
or organisation is renamed. *Neutral* — the provisioning identity's certificate auth is unchanged and was
already compliant.

### ADR-008: Entra security group → Dataverse group team → security role
**Status:** `Derived` · **Date:** 2026-08-10
**Context:** The Security Model describes Entra groups gating environments and three Dataverse roles, but never
the construct binding them; it implies trustees hold their role as individual users, which in PROD violates
C-TECH-040 (HARD).
**Decision:** Every persona role is assigned through an Entra-group-backed Dataverse **group team** (type AAD
Security Group) in PROD, per the populated `knowledge/technology/security-model.md` pattern. Direct assignment
is permitted in DEV only. Four role groups plus two environment groups (§6.1).
**Consequences:** *Positive* — access is auditable and centrally governed via Entra membership; joiner/leaver
handling is a group change, not a Dataverse change. *Negative* — group teams are not solution components, so
they need an idempotent `post_deploy` script per environment (C-TECH-042). *Neutral* — effective access is
identical to the Security Model's access matrix.

### ADR-009: A fourth security role for the service identity
**Status:** `Derived` · **Date:** 2026-08-10
**Context:** The Security Model states there is "no fourth role", yet its own access matrix requires the
service account to reach Bank Account and Payment while the Admin role — shared with Emily — must not.
**Decision:** Add `REV Service Automation`, assigned only to `svc-grantautomation` via its group team. Four
roles total (§6.2).
**Consequences:** *Positive* — the access matrix becomes expressible without granting Emily bank access or
giving the service account System Administrator. *Negative* — deviates from a statement the DPO may have read
as a commitment; must be surfaced at DPO sign-off. *Neutral* — no persona gains access the matrix does not
already grant.

### ADR-010: Configuration in a Dataverse `Setting` table, not environment variables
**Status:** `Derived` (source left it as "Env. variables / table") · **Date:** 2026-08-10
**Context:** NFR-019 requires the process owner to change thresholds, mappings and templates without developer
involvement. Environment variables require maker-portal access and a solution context; they are also the
correct home for values that differ per environment (C-TECH-031/047).
**Decision:** Business tunables live in `rev_setting` rows editable by `REV Admin` in the MDA. Environment
variables hold only per-environment values: `rev_SignedDocLibrary`, `rev_ServiceMailbox`,
`rev_DefaultThreshold`.
**Consequences:** *Positive* — NFR-019 is met by a table row, not a deployment; auditing on the table evidences
every threshold change against the decisions it affected. *Negative* — one more table; flows must read settings
at run time rather than binding at import. *Neutral* — the source permitted either.

### ADR-011: Intake channel and endpoint trust
**Status:** `Decision required` — **still open after the 2026-08-10 gate** · **Date:** 2026-08-10
**Context:** The source's primary intake is a WordPress webhook to an HTTP request trigger, trusted by a
"shared secret" with no named store — which does not satisfy C-TECH-002 (HARD).
**Decision:** Webhook remains the recommended primary for latency, with the secret held in a **Key
Vault-backed Dataverse secret environment variable**. Alternatives: scheduled REST pull (no public endpoint,
no inbound secret, but batch latency returns) or Entra OAuth on the trigger (needs a token call implemented in
WordPress by Alex).
**Consequences:** *Positive* — event-driven intake removes the export-import delay the programme exists to
remove. *Negative* — introduces **Azure Key Vault, which is out-of-palette**, and no source evidences that
Revitalise has an Azure subscription (§6.3, §12). *Neutral* — all three options are downstream-invisible; no
other component changes (SDD OQ-014).

**Update 2026-08-12 (development-agent, fix cycle for test-agent defect D-001) — THE ADR STAYS OPEN.**
Test-agent found (TC-401 / D-001) that the endpoint's *primary* authentication control existed nowhere in the
delivery chain, while the flow was already written for one of this ADR's three named alternatives and its
second gate already assumed an OAuth-issued caller identity. That is a narrower problem than the channel
decision, and it has been fixed on its own terms: **the Entra OAuth route is now the fully provisioned,
owned and testable default implementation** —
- the caller identity exists as a provisioned Entra app registration with the API permission it needs
  (`rev-wordpress-intake`, §12, `provisioning/entra/ensure-intake-client.ps1`);
- the control has a **named owner and an exact value** — trigger authentication parameter *"Specific users in
  my tenant"*, Allowed users = that registration's service principal object id — as a per-environment
  `post_deploy` item (§12);
- it is **verified after every deployment** by `provisioning/entra/verify-intake-endpoint-auth.ps1`, which
  asserts 401/403 for an unauthenticated caller *and* that the rejection happened before the workflow
  definition ran, which is the part a bare 401 does not prove.

**This does not close the ADR, deliberately.** The final channel choice is pending a conversation with Alex
(the website developer) and remains the reviewer's to make; what changed is that the *default* is now real
rather than asserted. If that conversation lands on the **shared-secret** route, C-TECH-002 pulls Azure Key
Vault back in (still out-of-palette, still unevidenced) and the flow's second gate compares a secret-type
environment variable instead of a client id. If it lands on the **scheduled REST pull**, the trigger becomes a
Recurrence, there is no public endpoint to authenticate, and the app registration, the `intake` settings block
and both intake scripts are deleted together. Each route's teardown is listed in-place in
`provisioning/deploymentSettings/*-settings.json` so the wrong one cannot be left behind.
**Status remains `Decision required`. SDD OQ-014 remains open.**

### ADR-012: AI Builder treated as in-palette, invoked from a Power Automate flow
**Status:** `Derived` · **Date:** 2026-08-10
**Context:** AI Builder is not one of the seven named palette items, but it is central to Automation #5.
**Decision:** Treat AI Builder's **prebuilt** PII-detection model as an in-palette capability, on the basis
that it is a first-party Power Platform service consumed through the AI Builder connector **from a Power
Automate flow (palette item 4)**, and its model reference ships inside the solution. It is not a Copilot Studio
agent, not an Azure service beyond Entra ID, and requires no custom code or separate runtime. Recorded in the
Adoption Report for reviewer acknowledgement rather than treated as out-of-palette.
**Consequences:** *Positive* — Automation #5, the largest single item (30–46 h), stays inside this system's
build scope. *Negative* — it needs capacity provisioning (credits) that no in-palette component otherwise
needs, and a DLP business-group entry; the 1 Nov 2026 seeded-credit change is an open commercial risk
(SDD OQ-017). *Neutral* — a **custom-trained** AI Builder model would be a different judgement; only the
prebuilt model is in scope.

### ADR-013: Primary name columns hold pseudonymous references, never names
**Status:** `Derived` · **Date:** 2026-08-10
**Context:** A Dataverse primary name column surfaces in lookups, related-record panes, search results and
audit summaries — paths a column security profile secures inconsistently in practice.
**Decision:** `rev_applicant.rev_name` = pseudonymised ID (`REV-A-00001`); `rev_application.rev_name` = the
application reference; `rev_bankaccount.rev_name` = account nickname or masked last four, never the account
number. Real names live in separate column-secured attributes.
**Consequences:** *Positive* — removes a whole class of accidental identity leak into trustee-visible surfaces.
*Negative* — administrative screens show references rather than names, so the MDA needs name columns placed
prominently on forms and views for Emily. *Neutral* — matches the source's own autonumber convention.

### ADR-014: Signed PDFs in a SharePoint library linked by URL, not Dataverse document management
**Status:** `Adopted` · **Date:** 2026-08-10
**Context:** One document type leaves Dataverse: the signed DocuSign acceptance.
**Decision:** One SharePoint library holds signed PDFs only; the URL is stored on the Grant row. Dataverse
server-based SharePoint integration and document locations are **not** configured.
**Consequences:** *Positive* — far less configuration; no per-record document location provisioning; retention
is a URL plus a helper-flow delete. *Negative* — no automatic parent-child document folder structure, and the
PDF is not protected by Dataverse column security, so **library permissions must independently deny the
Trustee role** (§6, access matrix: trustee = "link only"). *Neutral* — an alternative is a Dataverse
annotation, kept as the documented fallback.

### ADR-015: Teams notifications as 1:1 chat to the process owner, not a channel post
**Status:** `Derived` · **Date:** 2026-08-10
**Context:** FR-009 requires the new-application notification to carry the **applicant name** and reference.
The source says only "Teams".
**Decision:** Flows post to the process owner's **1:1 chat** as the Flow bot. No Team and no channel is
provisioned. The daily summary carries counts only (FR-021).
**Consequences:** *Positive* — personal data in a notification reaches one named recipient, not every member of
a channel; nothing to provision, so `knowledge/technology/teams.md`'s (placeholder) team provisioning is not
needed. *Negative* — no shared operational view if a second processor (Jan) is appointed; that would need a
private channel and a re-run of this decision. *Neutral* — Outlook to the service mailbox is the fallback.

### ADR-016: Power BI deferred to a future phase
**Status:** `Adopted` · **Date:** 2026-08-10
**Context:** Earlier versions considered a Power BI trustee dashboard (25–38 h plus Power BI Pro licences).
**Decision:** Out of scope. The trustee portal is a Dataverse app; Power BI Pro is not required. Revisit as a
Phase 5 enhancement if trustees later want an interactive dashboard.
**Consequences:** *Positive* — 14–20 h instead of 25–38 h, no Power BI Pro line, and the anonymisation control
stays enforced by column security rather than by report design. *Negative* — no ad-hoc analytics for trustees.
*Neutral* — Power BI is **out-of-palette** in this system, so a future phase would be built outside it;
recorded as a noted future item, not a current blocker.

### ADR-017: QuickBooks duplicate check — connector read query primary, Grant History table fallback
**Status:** `Adopted` (with the SDD scope conflict in §3.5 noted) · **Date:** 2026-08-10
**Context:** At 68 cumulative grants, full bidirectional QBO integration is premature. The SDD places "full
QuickBooks API integration" out of scope; the architecture makes a read-only connector query primary.
**Decision:** A single **read-only** QBO query by name/email is the primary check — which is not "full API
integration". If the QBO edition or the payment records cannot support it (SDD OQ-015), fall back to a
quarterly export into `rev_granthistory` with a cross-reference flow.
**Consequences:** *Positive* — evidence of the check on every application (FR-025) with no manual step; lower
effort than full integration. *Negative* — depends on grant payments carrying a searchable applicant
identifier, still unconfirmed; TRIP/Donorfy legacy records are not covered (SDD OQ-016). *Neutral* — the
fallback adds an eleventh table only if adopted.

### ADR-018: Least-privilege provisioning permissions
**Status:** `Derived` (required by C-TECH-043) · **Date:** 2026-08-10
**Context:** If this system's pipeline is adopted, provisioning Entra groups and the SharePoint library needs
app-only Graph and SPO permissions. Broad permissions are a tenant-wide attack surface.
**Decision:** `Sites.Selected` scoped to `/sites/grants` instead of `Sites.FullControl.All`; `Group.Create` +
`GroupMember.ReadWrite.All` (the narrowest permission that can manage group membership) instead of
`Directory.ReadWrite.All`. Federated credentials preferred over client secrets. All provisioning runs behind
`APPROVE TENANT` and is recorded in the Deployment Summary.
**Consequences:** *Positive* — no `Directory.*` or `*.FullControl.All` grant in the tenant. *Negative* —
`GroupMember.ReadWrite.All` is still tenant-wide, which is why it is justified here explicitly rather than
assumed. *Neutral* — ~~not needed at all if ADR-007 selects Power Platform Pipelines with manual
provisioning.~~ **Corrected 2026-08-12: ADR-007 selected Power Platform Pipelines and this registration is
still needed.** Pipelines promotes solutions; it does not create Entra security groups or SharePoint sites.
The provisioning identity is unaffected by the ALM choice and its certificate auth already satisfied
C-TECH-044.

### ADR-019: Audit administration separated from application administration
**Status:** `Derived` (required by C-DOM-012) · **Date:** 2026-08-10
**Context:** No source addresses audit-log integrity. If the application admin can delete audit history, the
trail is not tamper-evident.
**Decision:** `REV Admin` carries no audit-deletion privilege and neither Emily nor the service account holds
Dataverse System Administrator or Power Platform Administrator. Those sit with the tenant admin, who holds no
application role. Audit retention set to 6 years (§6.5).
**Consequences:** *Positive* — deleting audit history requires a different person with a different role.
*Negative* — Emily cannot self-serve audit configuration; she depends on Wanstor or the maker. *Neutral* — the
6-year audit retention period is **confirmed by the reviewer on 2026-08-10** (C-DOM-013 closed; §6.5).

### ADR-020: Accessibility standard — WCAG 2.1 AA baseline, 2.2 AA recommended for the applicant form
**Status:** `Derived` (no source names a standard) · **Date:** 2026-08-10
**Context:** No source document names an accessibility standard, despite an applicant population of disabled
people and unpaid carers with ~age-12 average reading level (SDD NFR-024, OQ-022).
**Decision:** WCAG 2.1 AA as the project baseline per `skills/accessibility-checklist.md`; WCAG 2.2 AA
recommended for the WordPress application form, carried into Alex's specification as an acceptance criterion.
**Consequences:** *Positive* — a testable standard exists, so the test-agent can write verifiable cases.
*Negative* — the highest-stakes surface is out-of-palette, so compliance depends on a third party honouring the
specification; this needs a named acceptance step. *Neutral* — reviewer may set 2.2 AA for everything.

### ADR-043: The Grant Referee's Title/Address/Town-City/Postcode DocuSign tabs are not modelled in Dataverse — left for the referee to complete at signing
**Status:** `Decided` · **Date:** 2026-09-06 · **Raised by:** `contract/change-orders/CO-002.md`

**Context:** The live DocuSign template's own anchor-tag table (reviewer-supplied 2026-09-06;
`docs/development/revitalise-grant-automation-dev-summary.md`, "Revision — reviewer-supplied
DocuSign anchor-tag ground truth") carries a Title/Address/Town-City/Postcode tab on **both**
signers. Signer 1 (Grant Acceptor)'s four values already exist on `rev_applicant`/`rev_application`
(§3.1). Signer 2 (Grant Referee)'s do not — no column on `rev_application`, no referee entity, and
automation #1's intake form (`wbs:1.1`–`1.6`) names no referee-facing capture step. `contract/change-
orders/CO-002.md` asked architect-agent to decide where to capture them before pricing.

Three placements were weighed: new columns directly on `rev_application` (`wbs:3.2`-adjacent,
cheapest but couples a second data subject's personal address onto the applicant's record); new
intake at automation #1 (new scope layered on new scope, since no referee-facing form step exists
today); or a new referee entity (only justified by a one-to-many or reporting need this flow does
not have — FR-041/FR-042 read only from `Get_the_applicant`/`Get_the_application`, and no FR
requires querying or reporting on a referee's address).

**What the requirement actually is.** FR-041 scopes Create Envelope's pre-population to "the
applicant's name, grant amount, holiday provider, dates and conditions" — the Grant Referee is
named nowhere in that list. FR-042 requires only that the document **route** to "the referee or
GP" for a second signature — a person identified for routing, not a record whose personal details
the system displays back to them. SDD OQ-046 independently confirms `rev_refereename`/
`rev_refereeemail`/`rev_refereephone` exist "for a later stage of the process (FR-042/FR-051)
rather than because intake should be asking and isn't" — i.e. for routing and erasure, not for
populating a signing document. No FR asks this system to hold, query or report on a referee's
title, address, town or postcode; DocuSign's own anchor tabs for these four fields exist
specifically so the signer supplies them at the point of signing, which is also the one moment
that value is certain to be current — a stored value can go stale between intake and signing (a
referee moves house), a DocuSign-time entry cannot.

**Decision:** No schema change. `rev_application` gains no `referee_*` columns; no referee entity
is created; automation #1 gains no referee-facing form step. Signer 2's Title, Address, Town/City
and Postcode tabs stay blank at envelope creation, for the referee to complete themselves during
signing — matching what `REVAcceptanceCreateEnvelope-8F1C2A44-1006-4B7A-9E21-0A1B2C3D4E06` already
commits as its default pending this exact confirmation.

**Consequences:** *Positive* — no new Tier 4 columns, no new lawful-basis/retention/erasure
surface for a second data subject's address data (C-DOM-002, C-DOM-003); no new capture surface to
design, build or test; the value the referee enters is necessarily current. *Negative* — Signer 2's
experience is asymmetric with Signer 1's (who does get a fully pre-filled document), and if the
reviewer later finds referee address data is needed for reporting or correspondence, this decision
reverses and the schema work CO-002 deferred still has to happen. *Neutral* — the broader "should
Signer 1's remaining personal-detail tabs (Phone/Email) also stay signer-entered" question is
unrelated and stays open exactly as the dev summary's own product-decision item records it; this
ADR closes only the four referee fields CO-002 raised.

**CO-002 disposition:** Closes as **not needed** — no schema change, no new capture surface, no
hours to price. `wbs:3.2` is unaffected and continues under its existing scope (envelope creation
"with pre-populated fields" from data that already exists, per its own description).

### ADR-044: The finance surface is a SEPARATE model-driven app, `rev_financecapture` — ❌ REJECTED
**Status:** ❌ **`Rejected` by the reviewer, 2026-09-09 (rev 6)** · **Proposed:** 2026-09-09 (rev 5,
as `Derived`) · **`wbs:8.3`** · **Superseded by:** `ADR-048`

**Retained, not deleted.** This project keeps decision history rather than erasing it, and a
rejected ADR is the cheapest way to stop the same proposal being re-derived from the same evidence
next time somebody reads the evidence map.

**Context (as proposed).** Two approved artefacts disagreed. §6.1's App Access cell gave the Finance
persona *"MDA `REV Grant Administration` — payment capture area only"*. `contract/evidence-map.json`
gives `wbs:8.3` the evidence rule `path: …/AppModules/rev_financecapture` — a separate app. The
source architecture names only *"Payment capture form — Power Apps"* and decides nothing between
them.

**Proposed decision (NOT in effect).** A separate model-driven app, unique name `rev_financecapture`,
display name `REV Finance Capture`, containing `rev_provider`, `rev_bankaccount` and `rev_payment`
and nothing else, superseding §6.1's App Access cell.

**Why it was proposed.** The argument was defence in depth: the Finance role would never be
associated with the admin app, so even a role misconfiguration granting Read on `rev_applicant`
could not put applicant data on a screen this persona can navigate to. The secondary argument was
that it satisfied the evidence rule `wbs:8.3` already had, avoiding an evidence-map change.

**Why the reviewer declined it, 2026-09-09.** The conflict was resolved the other way: **§6.1's
approved cell is right and the evidence rule is wrong.** A rule in `contract/evidence-map.json` is
not an architectural decision and does not get to overturn an approved design by being read second —
resolving the conflict in the evidence rule's favour let a check written to *verify* the design
*change* it. `ADR-048` records the design now in effect and §9.4.1 specifies the corrected rule.

**Two consequences of the rejection, both worth keeping on the page.**

*The defence in depth is genuinely given up, and this is the real cost.* The Finance role is now
associated with an app that also contains Applicant, Application, Review, Setting and Error Log, so
the **only** thing keeping applicant data off that persona's screen is the role's table privileges
(§6.2 grants it none on either table). A model-driven app area is a navigation boundary, not a
security boundary — a user with Read privilege reaches a table through search or a direct URL
whether or not it is in the site map. That was true of the *area* design all along; what changes is
that the app boundary is no longer a second, independent line. It is stated here rather than left
implicit, and it raises the stakes on `wbs:8.2` building the role exactly as §6.2 specifies.

*The proposal would have failed the build, which was not known when it was written.* The
`shipped-content` step's app-membership check requires every entity referenced by **any** site map
to be a component of **every** app module. A second app holding only the three finance tables would
have produced seven `APP MEMBERSHIP` failures on a HARD step for a solution that was correct
(§9.4 gate consequence 3). The rev-5 ADR enumerated `forms-and-views-reachable` and
`root-components-resolve` and stopped there — one more instance of an ADR that named the gates it
remembered rather than the gates the build config names for the artefact it was changing.

### ADR-045: Model-driven, not canvas and not a Code App
**Status:** `Derived` · **Date:** 2026-09-09 · **`wbs:8.3`**

**Context.** The source says only *"Power Apps"*. Three app types are in palette, and the trustee
portal precedent (ADR-003) chose a Code App, so the question is live rather than obvious.

**Decision.** A **model-driven app**.

**Consequences.** *Positive* — it ships entirely as diffable solution XML, which six existing build
gates already read (§9.4). A canvas `.msapp` is an opaque binary: no gate here could verify that a
secured column reached a screen, and `C-TECH-077` — the gate that exists precisely to catch a
column that cannot be typed into — would be blind to it. *Positive* — column security,
`ApplicationRequired` enforcement and auditing are applied by the platform **below** the app layer,
identically in every app type, so this choice gives up no control. *Positive* — accessibility is
inherited from the Unified Interface rather than authored, which matters because §8's WCAG 2.1 AA
obligation would otherwise move onto this project with no automated check able to see a regression.
*Positive* — it avoids the Code App host defects this project has already paid for (a Code App
reported live and reachable can still fail every Dataverse call for a real signed-in user).
*Negative* — less layout control than a canvas app; a finance capture form needs none.

### ADR-046: FR-153 and FR-154 are conventions carried by ONE control — the column `<Description>`
**Status:** `Derived` · **Date:** 2026-09-09 · **Amended rev 7 — 2026-09-10** · **`wbs:8.3`**
· **Relates to:** SDD OQ-151, ADR-013 · **Corrects:** its own rev-5 Decision, which named two
interventions while its own Consequences named one (test report **D-02**, TC-07)

**Context.** FR-153 (organisation-only provider contacts) and FR-154 (no natural person in the Bank
Account nickname) are rules about *what a human types into a free-text box*. The platform's options
are a format constraint on the column (a schema change — `wbs:8.1`, out of scope for 8.3), a
business rule (no regular-expression capability, and cannot recognise a personal name), or client
script (out of palette, and cannot recognise one either).

**Decision (amended rev 7 — ONE intervention, not two).** Carry both rules as **column
`<Description>` text on the column**, and **claim no mechanical enforcement**.

> *Previously read (rev 5): "Carry both as column `<Description>` text surfaced on the form, **plus a
> labelled instruction beside the Bank Account nickname control**."* That second intervention is
> **struck, not deferred**, and this ADR now agrees with the one that shipped. Three reasons, in the
> order that decides it. (1) **It did not ship** — the Bank Account form's own header records the
> column description as the only intervention, and the build that carried it is
> `build/artifacts/revitalise-grant-automation-20260910-3/`, SUCCESS. (2) **It has no ground-truthed
> shape in this solution.** Every `<cell>` in every shipped form here carries a bound data control:
> `grep -rho 'classid="{[0-9A-Fa-f-]*}"' src/solutions/RevitaliseGrantAutomation/Entities/*/FormXml/`
> returns 11 distinct classids, all of them data controls, and no label-only cell and no WebResource
> control exists anywhere in this solution to copy. A form-level instruction would have been a new
> out-of-palette control pattern authored blind against a live environment — the exact shape A-R59
> exists to keep out of `wbs:8.3`. (3) **It would add nothing the description does not**, at the same
> point in the same screen, *provided* the description is visible there — which is the contract the
> next paragraph names rather than assumes.

**Consequences, traced to what the user actually sees and what happens when the rule is broken.**
*What the finance user sees* — the Account Nickname control is bound to `rev_bankaccount.rev_name`,
whose `<Description>` in `Entity.xml` reads *"A nickname or masked last-four identifier for this
account … NEVER the full account number"*. **Whether Unified Interface renders that description as
always-visible help text beside the control, or only inside a hover/click information tooltip, is
NOT verified and is not assumed here** — it is the description-rendering row in §12.2 and a V4 observation. The
distinction is the whole control: as visible help text this is a weak control; as a hover-only
tooltip it is **effectively no control at all**, because a user who never hovers never reads it, and
FR-154's total shipped intervention would then be zero. *If the rule is broken* — the value **saves
successfully**. No error, no warning, no log entry. The applicant's name is then readable to every
holder of Read on Bank Account or Payment, projected through the lookup onto every Payment row, and
unremovable by column security. The only signal is a human reading the column. *What is genuinely
reduced* — §3.1's rev-5 measurement narrows the exposure from two columns to one:
`rev_payment.rev_name` is an autonumber and cannot carry an identity at all. *Residual, stated
plainly* — this is a declared policy that is not mechanically enforced. The mechanical form is a
schema change (a secured `rev_payeeref` with the nickname derived from it) belonging to `wbs:8.1`.

#### ADR-046a — the naming convention itself (resolves SDD OQ-151 in full: reviewer-confirmed rev 8)

**Added rev 7 — 2026-09-10. Reviewer-confirmed rev 8 — 2026-09-10, as proposed, no replacement.**
Because the convention *is* the control, a convention that covers only
half the cases is a control that covers only half the cases. The shipped description offers two
examples — `'Sunrise Lodge - main'` and `'…4321'` — and **both are provider-account shapes**. It says
nothing about an applicant reimbursement account, which is the only case FR-154 was written for
(test report **TC-08**). That gap is closed here, in both directions.

**The constraint any convention must satisfy is architecture's to state, and it is not a business
choice.** The value must be (a) non-identifying of a natural person, (b) recognisable to a finance
user at a glance, (c) ≤ 100 characters of plain text, and (d) safe under projection — it is copied
onto every Payment row through `rev_payment.rev_bankaccountid`'s lookup-name companion
(`C-TECH-070`(3)), so it is read by everyone who can read a Payment, not only by whoever can read
the Bank Account.

**The convention, per payee type** — `rev_payeetype` already distinguishes the two cases on the same
form, so the description can name both:

| `rev_payeetype` | Convention | Example | Why it satisfies (a) |
|---|---|---|---|
| Provider | The **provider's organisation name**, plus a free qualifier where one provider holds more than one account | `Sunrise Lodge - main` | An organisation is not a natural person. This is the shipped examples' own shape, now stated as a rule rather than shown as an example |
| Applicant (reimbursement) | The **grant reference**, plus a free qualifier | `REV-2026-001 - reimbursement` | **`ADR-013` established the grant reference as this project's pseudonymous applicant reference for exactly this purpose.** It is derived from an approved decision of this TAD, not invented here |

**Neither row may carry the applicant's name, initials, or any masked form of the account number
belonging to a natural person.** The masked last-four shape stays available for the provider row
only: a masked last four on an applicant's own account is still a value attributed to that applicant
by the row it sits on.

**Status of SDD OQ-151 — CLOSED rev 8 (2026-09-10), reviewer-confirmed.** The question as the SDD
asked it (*"what nickname convention satisfies FR-154 …?"*, owner: process owner / finance, due
*"Before build"*) is **past its date and the build has happened**, so it could not be met as written;
rev 7 re-scoped it rather than carrying forward a date nobody could act on, and rev 8 records the
answer that closes it. The history, kept rather than deleted:

- **What shipped without waiting (rev 7):** the table above, as the **default convention**. It is
  fail-safe in the sense that matters — every cell of it is non-identifying, so a finance user who
  follows it cannot breach FR-154 — and it replaces a description that is silent on the applicant
  case, which is strictly worse than any answer.
- **What still needed a human (rev 7):** whether the business *prefers* a different recognisable
  reference. The question narrowed from *"originate a convention"* to *"confirm the default above, or
  replace the applicant row"*, due **before `wbs:8.2` deploys** — the date with a mechanism behind it,
  since today no principal outside `REV_FinanceOnly` holds Read on either table (§6.2) and `wbs:8.2`
  is what makes that exposure live.
- **The answer (rev 8, 2026-09-10):** the reviewer confirmed the default convention above **as
  proposed, with no replacement** — `REV-2026-001 - reimbursement` (the grant reference, per
  `ADR-013`) for the applicant-reimbursement row. SDD OQ-151 is closed; nothing in the table above
  changes, and no further business decision is pending.

**Build specification for `development-agent` (`wbs:8.3`, FR-154 — a description-only change, no
schema change, no change order).** Amend `rev_bankaccount.rev_name`'s `<Description>` in
`src/solutions/RevitaliseGrantAutomation/Entities/rev_bankaccount/Entity.xml` to state both rows of
the table above, and amend the Bank Account form header's FR-154 note to cite `ADR-046a` rather than
recording the single-intervention reduction as an unexplained one. The column already exists and the
form control already binds it; nothing else changes.

**FR-153 needs no equivalent fix, and that was measured rather than assumed.** Both provider contact
columns' shipped descriptions already state the rule outright rather than only illustrating it —
`rev_contactemail`: *"A role-based mailbox only (e.g. bookings@provider.example) — NEVER a named
individual's address"*; `rev_contactphone`: *"A switchboard number only — same role-based-only
condition"*. The half-covered-convention defect is specific to `rev_bankaccount.rev_name`.

### ADR-047: `wbs:8.2` is an acceptance precondition for `wbs:8.3`, not an authoring blocker
**Status:** `Derived` · **Date:** 2026-09-09 · **`wbs:8.3`** · **Adopts:** SDD §8 D-1

**Context.** The `REV Finance` role does not exist; 16 of 18 columns on the two finance tables are
released only through a profile whose sole member is the service account (§6.2.1).

**Decision.** Author, pack, import and gate `wbs:8.3` now. Record V4 and V5 as **blocked on
`wbs:8.2`**, per the level-by-level analysis in §6.2.1. Build no part of the role here.

**Consequences.** *Positive* — 8.3's artefacts are independently verifiable to V3 and its build
gates are meaningful with no role in existence. *Negative* — **US-030 AC-1 through AC-5 cannot be
demonstrated**, and 8.3 must not be reported complete on V3 evidence; its evidence rule was a
directory-existence check that a V1 artefact satisfies, a weak rule of the same shape already
recorded against 8.2, and **rev 6 makes it unsatisfiable outright** — the directory it names is the
rejected `ADR-044`'s app. The replacement is specified in §9.4.1. *Neutral* — no hours move between
tasks.

**Unaffected by rev 6.** This ADR is about the *role*, not the *app*, and the V1–V5 analysis in
§6.2.1 holds identically for an area inside the admin app: no artefact `wbs:8.3` authors names the
role in either design, and both V4 blocks (app sharing by role name, and empty secured columns for a
non-member) are the same.

### ADR-048: The finance surface is an AREA inside the existing `REV Grant Administration` app
**Status:** `Adopted` — **reviewer decision, 2026-09-09** · **`wbs:8.3`** · **Supersedes:**
`ADR-044` · **Closes:** SDD OQ-150

**Context.** `ADR-044` proposed a separate app and the reviewer rejected it, resolving the §3.5
conflict in favour of §6.1's approved App Access cell rather than in favour of
`contract/evidence-map.json`'s rule. This ADR records what is in effect, so no reader has to
reconstruct it from a rejection.

**Decision.** The payment capture surface is an **area inside the existing `rev_grantadministration`
model-driven app**: `rev_provider`, `rev_bankaccount` and `rev_payment` are added as
`<AppModuleComponent type="1">` entries and as SubAreas under the site map's **existing**
`rev_group_finance` group, which today holds only `rev_sub_roundfinance`. **§6.1's App Access cell
for the Finance persona — *"MDA `REV Grant Administration` — payment capture area only"* — is the
one in effect and is restored unchanged.** `ADR-045` (model-driven, not canvas and not a Code App)
and `ADR-046` (FR-153/FR-154 are documented conventions) stand as written; neither depended on the
app-versus-area question. *(Rev 7 note: `ADR-046` was later amended for a self-contradiction in its
own Decision and gained `ADR-046a`. That amendment is also independent of this one — it is about how
many controls carry the convention, not about where the form lives.)*

**Consequences.** *Positive* — no new app module, no new site map, and **no change to
`Other/Solution.xml` at all**: the three tables are already root components with `behavior="0"`, so
their forms and views travel with them. *Positive* — one settings change instead of two: `REV
Finance` joins the existing app's `securityRoles` array rather than a new `dataverse.apps[]` entry
being created. *Positive* — `shipped-content`'s app-membership check is satisfiable, which the
two-app design would not have been (§9.4 consequence 3). *Negative, and stated plainly* — **the app
boundary is no longer a second barrier**; the sole control keeping applicant data off the finance
persona's screen is the role's table privileges, and an area is navigation, not security (see
`ADR-044`'s rejection consequences and §6.2.1's note under item 7). *Negative* — `wbs:8.3`'s
evidence rule must change, which `ADR-044` was partly chosen to avoid; §9.4.1 specifies the
replacement for `pm-agent`. *Neutral* — no hours move between tasks and no column changes.

---

## 11. Risks & Mitigations

R1–R9 are the risks *to individuals* adopted from SDD §7.7 (DPIA §6–§7). A-R10 onward are
**architecture-level risks identified during this intake** and are new to the document set.

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **R1** A trustee identifies an applicant from data that should be redacted | Low (after controls) | High | Column security profile applied below the app layer (§6); redaction fails closed (§5.5); trustee role has no export privilege; print/pack routes render only permitted columns |
| **R2** Special-category health data exposed to someone without a need to see it | Low | High | Tier 4 columns in `REV_TrusteeRestricted`; Finance role has no Application privilege; four narrow persona roles; role changes notified to the DPO |
| **R3** An applicant wrongly rejected by the automated score without meaningful human review | **Medium — pending DPO (OQ-005)** | High | FR-018 override, FR-019 Borderline routing, FR-022 withhold-on-missing-answer; thresholds in `rev_setting` so auto-reject can be routed through the process owner as a **configuration change** if the DPO requires it |
| **R4** Health free-text kept longer than necessary on granted records | **Medium — DPO decision open (OQ-006)** | Medium | `rev_narrativeraw` is a distinct column, so early redaction is a configuration change, not a rebuild |
| **R5** Bank or payment details accessed outside the Finance role | Low | High | Table-level denial to `REV Admin` **plus** `REV_FinanceOnly` column profile — defence in depth |
| **R6** Data processed or stored outside the UK | Low | High | UK region on all three environments; UK residency configured per connector; verified at setup as a §12 gate item |
| **R7** An erasure request not honoured across every system holding a copy | Low | High | Cascade from Applicant; helper flow reaches DocuSign, the PDF library and QuickBooks; carve-out reported to the requester (FR-052) |
| **R8** Service account compromised, exposing the whole dataset | Low | High | MFA; **scoped** CA exception, not a blanket exemption; dedicated `REV Service Automation` role rather than System Administrator; no interactive use |
| **R9** A leaver keeps access after their role ends | Low | Medium | Access is Entra group membership (ADR-008), removed by the tenant joiner-and-leaver process; environment group is a second gate. ✅ **Membership review cadence confirmed at 6 months** (reviewer, 2026-08-10) — supersedes the sources' quarterly assumption and closes OQ-008 |
| **A-R10** **Orphaned Applicant rows survive retention** — the bulk-delete job targets Application, so a `rev_applicant` row holding name, address, DOB and ethnic group persists indefinitely | **High if unmitigated** | High | Derived orphan sweep (§3.4 gap 1, §5.12, §12). **New finding — no source covers it** |
| **A-R11** ~~Audit rows contain before/after values of Tier 4 columns, so audit retention can outlive the record it describes~~ **CLOSED** | — | — | ✅ **Closed 2026-08-10.** Audit retention **confirmed at 6 years** by the reviewer, matching the longest record class — the only value that neither outlives the record nor leaves a granted record's life unevidenced (§6.5, C-DOM-013) |
| **A-R12** `rev_errorlog.rev_recordreference` is pseudonymous, so the "non-personal" classification the sources assert is not strictly true | Medium | Low | 90-day operational retention (derived); no name, contact detail or narrative fragment ever written; Tier 2 handling, no trustee access. Flagged for DPO confirmation |
| **A-R13** **WBS 0.3 — service account + scoped CA exception — outstanding with Wanstor.** Every unattended automation depends on it | **High — already late** | High | Carried as the one blocking §12 dependency. Escalate now; it gates Phase 1, not Phase 3 (SDD OQ-018) |
| **A-R14** Intake endpoint secret has no approved store in the source design | Medium | High | Key Vault-backed secret environment variable, or switch to the REST-pull intake and remove the secret entirely (§6.3, ADR-011). **Azure subscription is unevidenced** |
| **A-R15** ~~With a two-environment topology, the first managed import lands in PROD and the test-agent has no environment for the managed artefact~~ **CLOSED** | — | — | ✅ **Closed 2026-08-10.** ADR-006 confirmed **three environments (DEV, TST/ACC, PRD)**, so the first managed import lands in TST/ACC and the test-agent gates the managed artefact there (§9, §9.1) |
| **A-R16** AI Builder credit coverage unconfirmed ahead of the **1 Nov 2026** seeded-credit change | Medium | Medium | Confirm before Automation #5 goes live (SDD OQ-017); the degraded path is 100% manual redaction, which restores 3–4 h per cycle of manual work but does not breach anything |
| **A-R17** ~~If Canvas App is chosen for the portal, the component leaves this system's build palette~~ **CLOSED** | — | — | ✅ **Closed 2026-08-10.** ADR-003 confirmed **Code App**; Canvas App descoped and rejected. Residual, tracked at development: the Code App is developer-maintained and the source's 14–20 h estimate assumed a low-code app |
| **A-R18** The third environment (TST/ACC) consumes chargeable Dataverse capacity a charity may not have | Medium | Low | Confirm database capacity at WBS 0.2 **before provisioning TST/ACC**; three environments is the lowest-cost topology that still keeps a real managed-import test gate (ADR-006) |
| **A-R19** UK residency of DocuSign and QuickBooks Online is **asserted but not evidenced** in any source | Medium | High | Verification is a §12 `APPROVE TENANT` gate item with written evidence retained; DPIA action A5 |
| **A-R20** Trustee adoption — some trustees may resist moving off email attachments | Medium | Medium | Offline anonymised pack (FR-032) and print route (FR-039) exist so partial adoption excludes no one; one round of trustee feedback budgeted (SDD OQ-013, OQ-024) |
| **A-R21** DPIA and RoPA are **concept drafts, not signed off**, and the DPIA sign-off table is empty | **High** | High | Art. 35 requires completion before go-live (SDD OQ-030). Build may start on approved requirements, but **not** on the field-level-security and 6-year-retention basis until OQ-004/005/006 are recorded |
| **A-R22** **No SAR extract mechanism is built or agreed** — FR-053 has no assigned component; §4.2 records a proposal only | Medium | Medium | ✅ **Accepted as a known gap by the reviewer on 2026-08-10** (C-DOM-005, SOFT, accepted-risk path). **Carried forward to development-agent as an open item**, with the four questions in §4.2 to close it. Note there is also no SAR turnaround SLA in any source (SDD OQ-023), so the test-agent has no threshold to verify against even once a mechanism exists |
| **A-R56** **The six-year retention clock never starts.** `rev_grant.rev_finalpaymentdate` is written by nothing: the `REV \| Finance \| Capture Payment` flow was its only writer and stays unbuilt, while the `wbs:8.3` form captures `rev_isfinalpayment` on the **Payment** row and propagates it nowhere (§5.11) | Medium | **High** | **OPEN — the reviewer deferred the deciding decision on 2026-09-09 (rev 6), so this risk is accepted as standing, not mitigated.** Not `wbs:8.3`'s to fix and deliberately not absorbed into it; it is the concrete cost of §3.5 conflict 2's flow decision staying open. Interim: the date can be set by hand on the Grant, but nothing prompts anyone to and no gate detects that nobody did. *Previously read (rev 5): put to the reviewer as the fact that should decide it* |
| **A-R57** **`wbs:8.3`'s evidence rule is wrong, not merely weak (rev 6).** It is a directory-existence check on `AppModules/rev_financecapture` — the app `ADR-044`'s rejection means will never exist — so it can now be satisfied by nothing, and `wbs:8.3` can never derive as complete while it stands. The original risk stands too: US-030 AC-1–AC-5 need `wbs:8.2` (§6.2.1) | **High** | High | §9.4.1 specifies the five replacement rules for `pm-agent`, which owns `contract/evidence-map.json`. ADR-047 states the V-level split explicitly. *Previously read (rev 5): a directory-existence check satisfied by a V1 artefact — the weak-evidence shape already recorded against `wbs:8.2`* |
| **A-R58** **A later rollup silently defeats `REV_FinanceOnly`.** A rollup of `rev_payment.rev_amount` onto Grant or Application copies a secured value into an unsecured column — the one construct that can. NFR-150 forbids it and **no gate checks for it**: no build step reads rollup or formula metadata | Low | **High** | Held by review, not by a gate, and said so rather than implied. Proposed as an improvement finding so the absence is on the record |
| **A-R59** **The finance forms and app module are hand-authored ahead of a live environment**, and an app module authored blind has already failed import once on this project with a `NullReferenceException` naming no field | Medium | High | Copy the element shape from `AppModules/rev_grantadministration/AppModule.xml`, which **is** a real DEV export whose header records the eleven ways the first hand-authored guess was wrong — not from documentation. Closed in one first-environment sweep, not one import failure at a time (§12.2) |

---

## 12. Provisioning & External Dependencies

Every component that **cannot ship inside the solution**. Scope `tenant` → `tenant_prerequisites` block in
`config/revitalise-grant-automation-pipeline.yml`, gated `APPROVE TENANT`; scope `per-env` → `post_deploy`.
All scripts must be idempotent, check-before-create, and report `CREATED` / `EXISTS` / `FAILED` per resource
(C-TECH-042, development-agent / pipeline-agent scope).

| Item | Type | Tool / Script | Scope | Gate |
|---|---|---|---|---|
| `REV-GrantApplications-DEV` environment security group | Entra ID security group | `provisioning/entra/` — Microsoft Graph PowerShell | tenant | `APPROVE TENANT` |
| `REV-GrantApplications-ACC` environment security group — **new, required by the three-environment topology (ADR-006)** | Entra ID security group | `provisioning/entra/` — Graph PowerShell | tenant | `APPROVE TENANT` |
| `REV-GrantApplications-PRD` environment security group | Entra ID security group | `provisioning/entra/` — Graph PowerShell | tenant | `APPROVE TENANT` |
| `REV-PP-GrantApplications-Admins-ACC`, `REV-PP-GrantApplications-Service-ACC` (TST/ACC), `REV-PP-GrantApplications-Admins-PRD`, `REV-PP-GrantApplications-Service-PRD` (PRD) role groups — **Phase 1 scope only; `Finance`/`Trustees` role groups are not created in this phase, no Phase 1 table is reachable by either persona.** Already created manually by the reviewer on 2026-08-14 | Entra ID security groups (4) | `provisioning/entra/` — Graph PowerShell | tenant | `APPROVE TENANT` |
| **`svc-grantautomation@revitalise.org` service account: creation, licences, MFA, scoped Conditional Access exception** | Entra ID user + CA policy | **Manual — Wanstor (WBS 0.3)** | tenant | `APPROVE TENANT` — ⚠️ **OUTSTANDING AND BLOCKING (SDD OQ-018, risk A-R13)** |
| **`rev-grantautomation-deploy-dev` / `-tstacc` / `-prd` app registrations (3) + a Dataverse application user for each in ITS OWN environment only** — **CHANGED 2026-08-12 (ADR-007/ADR-021).** Replaces the single shared `rev-grantautomation-deploy`. Each holds **exactly one** federated credential bound to its own GitHub Environment OIDC subject (`repo:<org>/<repo>:environment:<dev\|tst_acc\|prd>`) and **no client secret**. Separate registrations, not several credentials on one: credential-only scoping gates token *issuance* but not *authority* (§6.7) | Entra app registrations ×3 + Dataverse app users | `provisioning/entra/ensure-app-registration.ps1` (per settings file) + `provisioning/dataverse/`; the `-dev` one by hand, as Phase 1 has no `dev-settings.json` | tenant + per-env | `APPROVE TENANT` |
| **Pipelines host environment — NEW, required by ADR-007.** A dedicated Dataverse **production** environment, UK region, with the **Power Platform Pipelines** application installed; holds all pipeline configuration, security and run history. Must be a **custom host**, not the auto-provisioned platform host (platform-host pipelines are *personal* pipelines: cannot be extended, cannot be shared, cap at three environments). Must not double as DEV. ⚠ Deleting it deletes all pipelines and run history | Power Platform environment + first-party application install | PPAC → Deployments → New custom host, **or** Environments → *host* → Resources → Dynamics 365 apps → Install app | tenant | `APPROVE TENANT` |
| **Pipeline + stage configuration — NEW, required by ADR-007.** In the Deployment Pipeline Configuration app: one Environment record per environment (DEV = *Development*, TST/ACC and PRD = *Target*), each validating to Success; then pipeline `REV Grant Automation Standard` with DEV linked and **two** stages in order — *Deploy to TST/ACC*, then *Deploy to PRD* with the former as its Previous Deployment Stage. Two stages, not three (ADR-006). Stage GUIDs read via `pac pipeline list` and stored as `PIPELINE_STAGE_ID` per GitHub Environment. **Enable the redeploy-previous-versions setting**, or rollback by redeployment is unavailable | Dataverse configuration in the host | Manual, Deployment Pipeline Configuration app | tenant | `APPROVE TENANT` |
| **Managed Environment status on TST/ACC and PRD — NEW, required by ADR-007, and a LICENCE COST.** "All other environments used in pipelines must be enabled as managed environments. Licenses granting premium use rights are required for all managed environments." The host and DEV are exempt. From **February 2026** Microsoft enables this on pipeline targets automatically, so it happens whether planned for or not — confirm entitlements **before** provisioning, with the A-R18 capacity check | Managed Environment enablement + licensing | PPAC → Environments → Enable Managed Environments (or the automatic setting per pipelines host) | tenant, applied per-env | `APPROVE TENANT` — ⚠ **cost impact, confirm with Revitalise** |
| **Pipelines access assignment — NEW, required by ADR-007.** `Deployment Pipeline Administrator` in the host for the maker/administrator; the pipeline record shared with whoever runs it (`Deployment Pipeline User` + Read). Requesters also need export rights in DEV and import rights in the target. ⚠ Whether a **service principal** may *request* a promotion is **not documented** — the item to settle before any `promote_mode` moves from `manual` to `cli` | Dataverse security roles + row sharing in the host | Manual, Deployment Pipeline Configuration app | tenant | `APPROVE TENANT` |
| `REV-MS-Provisioning` app registration + admin consent (`Group.Create`, `GroupMember.ReadWrite.All`, `Sites.Selected`) | Entra app registration + admin consent | `provisioning/entra/` — see ADR-018 | tenant | `APPROVE TENANT` |
| Power Platform environments **DEV + TST/ACC + PRD** — **UK region**, Dataverse enabled, bound to their security groups (three environments per ADR-006; confirm database capacity first — risk A-R18) | Power Platform environment | `pac admin create` / Power Platform Admin PowerShell | tenant | `APPROVE TENANT` |
| **UK residency verification** for the environments, AI Builder, DocuSign and QuickBooks — written evidence retained | Compliance verification | Manual, evidenced | tenant | `APPROVE TENANT` (NFR-009, DPIA A5) |
| Environment DLP connector policy (business / blocked groups per §6.4, **including Request/HTTP and Word Online**) | DLP policy | Power Platform Admin PowerShell | tenant, applied per-env | `APPROVE TENANT` |
| AI Builder credit / capacity assignment to the PROD environment | Capacity allocation | Power Platform admin centre | per-env | `APPROVE TENANT` (SDD OQ-017) |
| SharePoint site `/sites/grants` + "Signed Acceptances" document library; **Trustee role denied** | SPO site collection + library | `provisioning/sharepoint/` — PnP.PowerShell | tenant (site collection) | `APPROVE TENANT` |
| **`rev-wordpress-intake` app registration + service principal + `Microsoft Flow Service` `User` permission and admin consent — NEW 2026-08-12, closes test-agent defect D-001 (C-TECH-006 HARD).** The OAuth client-credentials identity Alex's WordPress site presents to the intake endpoint. Two identifiers come out of it and they are **not interchangeable**: the application (client) id → the `rev_IntakeAllowedClientId` environment variable (the flow's *second* gate); the **service principal object id** → the trigger's Allowed users list (the *primary* gate). The permission exists so Entra will issue a token for `https://service.flow.microsoft.com//.default`; without it the endpoint is unreachable, not merely unauthenticated. ⚠ The caller's own certificate/secret is **deliberately outside this pipeline** — issued interactively and handed to Alex out of band, because a pipeline that mints a credential prints one (C-TECH-001). ⚠ ADR-011 remains **open**: this is the default implementation, not the settled channel | Entra app registration + SP + admin consent | `provisioning/entra/ensure-intake-client.ps1` (per settings file) + `grant-admin-consent.ps1` | tenant | `APPROVE TENANT` |
| **Intake trigger authentication parameter on `REV \| Intake \| WordPress to Dataverse` — NEW 2026-08-12, the primary control D-001 found unassigned (NFR-008, C-TECH-006 HARD).** Set the trigger's *"Who can trigger the flow?"* parameter to **"Specific users in my tenant"** with **Allowed users = the `rev-wordpress-intake` service principal object id**. This is a **trigger setting, not a solution component** — Microsoft documents it at [`/power-automate/oauth-authentication`](https://learn.microsoft.com/en-us/power-automate/oauth-authentication) and publishes no workflow-definition property for it, so it cannot ship in the managed solution and cannot be asserted by reading the flow JSON. **Owner: Wanstor (tenant administration); value supplied by the maker from the `ensure-intake-client.ps1` output.** Apply it **before** the flow is turned on. ⚠ A blank Allowed users list silently means *any user in the tenant*; read the field back after saving. ⚠ Whether the setting survives a solution import is **unverified** (no environment exists), so it is configured **and** verified on every deployment rather than assumed | Power Automate trigger setting | Manual in the designer, then **verified** by `provisioning/entra/verify-intake-endpoint-auth.ps1` as a smoke test on TST/ACC and PRD | per-env | `post_deploy` + `smoke_tests` (C-TECH-006 `Verify By`) |
| **Intake endpoint URL as a CI secret (`INTAKE_ENDPOINT_URL_TEST` / `_PRD`) — NEW 2026-08-12.** A Power Automate HTTP trigger URL carries its own SAS signature in `sig=`, so the URL **is** a credential (Microsoft documents regenerating it). Held as a per-environment CI secret, never as a value in a settings file (C-TECH-001/047); consumed only by the auth smoke test | CI secret | Manual, read once from the trigger card | per-env | `post_deploy` |
| Azure Key Vault + secret-type environment variable for the intake secret — **OUT-OF-PALETTE; only if ADR-011 keeps the webhook** | Azure resource | Manual | tenant | `APPROVE TENANT` — reviewer decision first (§6.3) |
| Purview **basic** retention labels on the Application table and the signed-PDF library — **OUT-OF-PALETTE** | Purview configuration | Manual, Purview portal | tenant | `APPROVE TENANT` (ADR-005) |
| Dataverse group teams `REV Admins`, `REV Finance`, `REV Trustees`, `REV Service Accounts` + role bindings (role looked up **by name** per environment) | Dataverse group teams | `provisioning/dataverse/` — Web API, idempotent | per-env | `post_deploy` (C-TECH-040) |
| Column security profile membership — role/team assignment to `REV_TrusteeRestricted` and `REV_FinanceOnly` | Dataverse configuration | `provisioning/dataverse/` | per-env | `post_deploy` |
| Environment + table auditing enabled on all ten tables; **audit retention = 6 years** | Dataverse configuration | `provisioning/dataverse/` | per-env | `post_deploy` (NFR-014, §6.5) |
| Recurring bulk-delete jobs ×3 — 6 years / 12 months / 6 months — **plus the derived orphaned-Applicant sweep** | Dataverse system jobs | `provisioning/dataverse/` | per-env | `post_deploy` (ADR-004, §3.4) |
| App sharing — trustee portal shared to the `REV Trustees` group team; Grant Administration MDA to `REV Admins` / `REV Service Automation` | App sharing | `provisioning/dataverse/share-apps.ps1` — data-driven from `deploymentSettings[].dataverse.apps` | per-env | `post_deploy` |
| **App sharing — the EXISTING `REV Grant Administration` MDA additionally associated with `REV Finance` — rev 6, `wbs:8.3` (`ADR-048`).** Add one role name to that app's existing `dataverse.apps[].securityRoles` array in each settings file; **no new `dataverse.apps[]` entry and no script change** — `share-apps.ps1` already iterates both. ⚠ It resolves the role **by name** and reports `FAILED — security role 'REV Finance' not found` while `wbs:8.2` is outstanding, which is the intended and visible failure, not a defect (§6.2.1). *Rev 5 recorded a new `dataverse.apps[]` entry for a separate `rev_financecapture` app; `ADR-044` was rejected* | App sharing | `provisioning/dataverse/share-apps.ps1` (existing) | per-env | `post_deploy` |
| **`REV Finance` group team added to `REV_FinanceOnly` membership — `wbs:8.2`, required before `wbs:8.3` reaches V4.** Today the profile's only member is `REV Service Accounts`; `REV Admins` is deliberately excluded and must stay so (NFR-002). Add to `memberTeams` in all three settings files; **no script change** | Dataverse configuration | `provisioning/dataverse/ensure-column-security-profile-members.ps1` (existing) | per-env | `post_deploy` |
| Connection references bound to service-account connections: `rev-dataverse`, `rev-docusign`, `rev-qbo`, `rev-outlook` | Connections | Manual once per environment (interactive OAuth consent required) | per-env | `post_deploy` |
| Environment variable values + connection reference bindings | Deployment settings | **CHANGED 2026-08-12 (ADR-007): supplied in the Power Platform Pipelines deployment pane, which validates them before the import. Pipelines does not accept a `--settings-file`.** `provisioning/deploymentSettings/pac-import-tstacc.json` and `pac-import-prd.json` are retained as the reviewed record of the values to enter — C-TECH-047 stays satisfied, but its enforcement moves from a tool to a human reading a code-reviewed file | per-env | During promotion (was `post_deploy`) |
| `rev_setting` seed rows — thresholds, Likert map, income ceiling, redaction threshold, reminder/escalation days | Reference data | `provisioning/dataverse/` — idempotent upsert | per-env | `post_deploy` — ⚠️ values await SDD OQ-001, OQ-002, OQ-003, OQ-011 |
| **DocuSign**: account, acceptance template replicating the Canva form, UK residency, envelope purge aligned to the retention schedule | External SaaS | Manual — Revitalise procures | external | Reviewer / before Automation #3 go-live |
| **QuickBooks Online**: read-only OAuth connection; confirm edition and that payments carry a searchable applicant identifier | External SaaS | Manual | external | Reviewer (SDD OQ-015) |
| **WordPress / Gravity Forms**: form built to the field-by-field specification (incl. WCAG + reading-age acceptance criteria), webhook or REST credential issued | External, **OUT-OF-PALETTE** | Alex, website designer | external | Reviewer (SDD OQ-014, ADR-020) |
| Licences: Power Apps Premium ×2 (maker/service + Emily), Power Apps pay-as-you-go (trustees), Power Automate Premium (service account) | Licensing | Manual — Revitalise procures | tenant | Reviewer (SDD OQ-017, OQ-025) |

---

### 12.1 Environment Prerequisites — the finance capture surface (`wbs:8.3`)

**Added rev 5.** `C-TECH-050`: Entities, Attributes, Global OptionSets, Security Roles and Field
Security Profiles are created via the Dataverse Web API, never assumed creatable by solution
import. **This runs again per environment — DEV, TST/ACC and PRD — not once per feature.**

| Item | Why a deploy cannot create it | Script | Runs before | Re-run per env? |
|---|---|---|---|---|
| The 24 columns across `rev_provider` / `rev_bankaccount` / `rev_payment` | `C-TECH-050` — attributes are not creatable by import | `ensure-schema.ps1` | First import | **Yes** — already wired; `wbs:8.3` adds nothing |
| `REV_FinanceOnly` + its 16 `<FieldPermission>` rows | `C-TECH-050`, widened 2026-09-07 to cover **every** `fieldpermissions` row, not only first creation | `ensure-schema.ps1` | First import | **Yes** — already wired; `wbs:8.3` adds no permission |
| `REV Finance` security role | `C-TECH-050` — roles are not creatable by import | **`wbs:8.2`'s** | Before `share-apps.ps1` can succeed | **Yes** |
| **App module membership, site map, forms, views** | **Not a prerequisite — solution import creates the forms and views and updates the existing app module and site map** | *(solution import)* | — | No |

The last row is the useful one: **every artefact `wbs:8.3` authors is on the import-creatable side
of `C-TECH-050`**, so it adds no new per-environment prerequisite. The only prerequisite in its
path is a role it does not build.

### 12.2 Platform Contract Verification Plan — the finance capture surface (`wbs:8.3`)

**Added rev 5.** `C-TECH-051` / `C-TECH-052`. Each row below is hand-authored ahead of a live
environment and carries an `A-nnn` row in the Dev Summary §10 Unvalidated Assumptions Register.

| Component | Hand-authored? | Ground-truth method | Platform-assigned values | Verified at |
|---|---|---|---|---|
| Three `<AppModuleComponent type="1">` lines in `AppModules/rev_grantadministration/AppModule.xml` | Yes | **No guessing needed — the seven sibling lines in the same element are a real DEV export**, and the shape is `type="1" schemaName="…"` by `schemaName`, never by id (`C-TECH-051`) | None — no id is authored | V3 import; **V4 open-in-designer** |
| Three `<SubArea Entity="…">` under the existing `rev_group_finance` group in `AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml` | Yes | **Copy `rev_sub_settings`/`rev_sub_errorlog`, the entity-form SubAreas in this same file.** Use the `Entity=` form, **not** a view-pinned `Url=` — that file's own header records three wrong `Url` shapes settled against a live import and a Microsoft-authored managed site map | None | V3 import; **V4 play mode** — the designer's edit mode is not the test (`shipped-content` check 1b) |
| `Other/Solution.xml` root components | **No — unchanged** | All three tables are already `type="1" … behavior="0"`, which carries their forms and views. Rev 5 planned `type="80"` and `type="62"` lines for the rejected separate app | — | — |
| `FormXml/main/*.xml` on the three tables | Yes | Copy from a table in this solution that already has a working main form — `rev_grant` and `rev_application` both do | `formid` | V3 import; **V4 is the real test** — a form can import cleanly and still fail to open |
| `SavedQueries/*.xml` on the three tables | Yes | Same — copy a working sibling | `savedqueryid` | V3 import |
| **How a column `<Description>` renders on a Unified Interface main form** — always-visible help text beside the control, or only inside a hover/click information tooltip (**added rev 7**) | n/a — a platform rendering behaviour, not authored source | **No source in this repository can answer it, and it is not guessed here.** Open the Bank Account form in DEV as a signed-in user with `REV_FinanceOnly` membership and look at the Account Nickname control | — | **V4 — the first time a human opens the form** |

**The row above needs a Dev Summary §10 register row, and this document deliberately does not
allocate its id (added rev 7).** `development-agent` opens it, taking a **fresh** id and checking it
against the register before use — test-report **D-01** is an `A-FIN` id already carrying two
different meanings, and `verify-assumption-markers.py` cannot see that class of collision because it
only checks that the id appears at the target.

**These can be authored blind, and the mitigation is the first-environment sweep, not care**
(A-R59). Every row closes in one pass against DEV before the first deploy — not one import failure
at a time. This project has already paid fifteen import attempts for the alternative.

**One contract is genuinely unknown and is named rather than assumed:** whether a model-driven app
whose every bound column is column-secured renders its forms **empty** for a user with no profile
membership, or **errors**. §6.2.1 assumes empty fields, from how column security behaves elsewhere
in this solution. It is a V4 observation, and it is recorded as an assumption, not a fact.

---

## Appendix A — Requirement Traceability (SDD → TAD)

Every FR and NFR in the approved SDD maps to an architectural element. This is the architect's contract with
the SDD and the baseline the development-agent and test-agent trace from.

| SDD requirement | TAD element |
|---|---|
| FR-001 – FR-006 | WordPress / Gravity Forms application form — **out-of-palette**, §4, §8, §12 (specification obligation, incl. NFR-020 reading age) |
| FR-007, FR-008 | `REV \| Intake` flow §5.1; `rev_application.rev_name` §3.1 (**reference-format conflict §3.5 #1**) |
| FR-009 | `REV \| Intake` → Teams 1:1 chat, ADR-015 |
| FR-010 | `REV \| Ops \| Failure Alert` §5.14; `rev_errorlog` §3.1 |
| FR-011 – FR-016 | `REV \| Scoring \| Calculate & Flag` §5.2; `rev_circumstancescore`, `rev_scorebreakdown`, `rev_incomeflag` §3.1; `rev_setting` §3.1 |
| FR-017 | `rev_setting` table, ADR-010, NFR-019 |
| FR-018 | `rev_statusoverridden` / `rev_overriddenby` / `rev_overriddenon` §3.1; override short-circuit §5.2 |
| FR-019, FR-022 | §5.2 Borderline and missing-answer branches; §6.6 (Approvals option §4) |
| FR-020 | `rev_status` choice + filtered views §3.1 |
| FR-021 | `REV \| Scoring \| Daily Summary` §5.3 (counts only) |
| FR-023 – FR-025 | `REV \| Duplicate \| QBO Check` §5.4; ADR-017; `rev_duplicateflag` and prior-grant columns §3.1 |
| FR-026 – FR-031 | `REV \| Narrative \| Scrub Free-Text` §5.5; `REV_TrusteeRestricted` profile §6; `rev_narrativeraw` / `rev_narrativeredacted` / `rev_redactionconfidence` / `rev_redactionreleased` §3.1; ADR-002 |
| FR-032, FR-033 | `REV \| Narrative \| Trustee Pack` §5.6 — **DERIVED flow**; Word Online (Business) §4; tagged-PDF requirement §8 |
| FR-034 – FR-039 | Trustee portal — **Code App, confirmed (ADR-003)**; `REV_TrusteeRestricted` §6; `rev_eligibleforround` §3.1; §8 accessibility; no export privilege §6.2 |
| FR-037, FR-040, FR-047 | `REV \| Portal \| Finalise Decisions` §5.7; `rev_review` verdict columns §3.1 |
| FR-041 – FR-045 | `REV \| Acceptance \| Create Envelope / Reminders & Escalation / Completion` §5.8–5.10; DocuSign §4; `rev_grant` acceptance columns §3.1 |
| FR-046 | `rev_manualacceptancerecorded` on Grant, recorded via the MDA — no flow, by design §5.10 |
| FR-048 | Native recurring bulk-delete jobs ×3 + status/date columns, ADR-004, §12 |
| FR-049 | `REV \| Retention` helper mode 1 §5.12 — DocuSign envelope purge, signed-PDF delete |
| FR-050 | QuickBooks finance carve-out §5.12; Bank Account / Payment retention §3.4 gap 2 |
| FR-051, FR-052 | Helper mode 2 §5.12; cascade design §3.3; legal-hold carve-out evaluated by the flow §6.6 |
| FR-053 | ⚠️ **NO AGREED MECHANISM** — §4.2 records a proposal only (helper mode 3, §5.12). Accepted open item, carried to development-agent (C-DOM-005, risk A-R22) |
| FR-054 | Retention/erasure evidence log §5.12, §6; Dataverse system jobs |
| FR-055 | `rev_anonymisedstatistic` (no lookups) §3.1; write assignment §5.13 — **DERIVED**; pre-delete verification §5.12 |
| NFR-001 – NFR-025 | §7, row by row |
| SDD OQ-026 (Provider classification) | **Answered provisionally** in §3.2 — Tier 2, conditional on no named contacts; reviewer confirmation required |
| SDD OQ-020 – OQ-023 (performance, availability, accessibility, SAR SLA) | §7 NFR-022 – NFR-025 and §8 — recorded as gaps; ADR-020 proposes the accessibility standard |
| SDD OQ-004 – OQ-006 (DPO decisions) | ADR-002 conditional status; risks R3, R4, A-R21; §6 |
| SDD OQ-008 (role review cadence) | ✅ **Closed** — confirmed at 6 months, §6.6, R9 |

**Payment capture form — added rev 5, from `docs/plans/revitalise-payment-capture-plan.md`
(`wbs:8.3`).** Every row below is V3-verifiable now and **V4-verifiable only after `wbs:8.2`**
(§6.2.1, ADR-047):

| SDD requirement | TAD element | V4 without `wbs:8.2`? |
|---|---|---|
| FR-150 (one finance surface over the three tables) | `ADR-048` area inside the existing admin app, `ADR-045` model-driven; §6.1 App Access; §9.4 artefacts. *(Rev 5 named `ADR-044`, a separate app — rejected)* | No |
| FR-151 (Grant + payee account + amount required) | **Already enforced by schema** — all three columns are `ApplicationRequired` in `Entity.xml`, so no business rule, web resource or plugin is added; the design obligation is that the three controls are present and **not** `disabled` (§9.4) | No — also needs Read + AppendTo on `rev_grant` from `wbs:8.2` (§6.2.1) |
| FR-152 (QuickBooks reference) | `rev_payment.rev_qboreference` §3.1 — plain text, optional at create, editable after. **No QuickBooks integration**; Automation #7 / FR-023 is untouched | No |
| FR-153 (organisation-only provider contacts) | `ADR-046`; §3.2's Tier 2 derivation, whose binding condition this requirement now *is* | Partly — a Provider row is unsecured, so observable without `wbs:8.2` |
| FR-154 (no natural person in the Bank Account nickname) | `ADR-046` (**one** intervention — the column `<Description>`; rev 7 strikes the second one its rev-5 Decision named and that never shipped) and **`ADR-046a`**, which states the convention for both payee types and specifies the description change; §3.1's `rev_bankaccount` rev-5 note — narrowed to that one column, because `rev_payment.rev_name` is an autonumber | No. **And its V4 test is not only "can a finance user type into it" but §12.2's description-rendering row: whether the description is visible at all** |
| NFR-150 (no new unsecured column; no rollup off a secured column) | §7 NFR-002 row; risk **A-R58** — **no gate enforces the rollup half**, and that is stated rather than implied | Source-verifiable now |
| US-030 AC-1 – AC-5 | §6.2.1's level table | **No — all five** |
| SDD OQ-150 (separate app or an area?) | ✅ **Closed by the reviewer 2026-09-09 — an AREA inside the existing `REV Grant Administration` app** (`ADR-048`). *Rev 5 closed it the other way, to a separate app (`ADR-044`); that ADR is rejected and retained* | — |
| SDD OQ-151 (nickname convention for reimbursement accounts) | ✅ **CLOSED rev 8 — 2026-09-10, reviewer-confirmed.** `ADR-046a` states the convention for **both** payee types and specifies the `Entity.xml` description change; the reviewer confirmed the applicant-reimbursement row (`REV-2026-001 - reimbursement`, the grant reference per `ADR-013`) **as proposed, with no replacement**. No business decision remains pending. *History: rev 7 re-scoped the question to confirm-or-replace, due before `wbs:8.2` deploys, narrowing it from the SDD's original OPEN/load-bearing framing where `ADR-046` recommended the grant reference and the business decided* | — |
| SDD OQ-152 (finance role privileges on Grant) | ✅ **Answered as a build specification for `wbs:8.2`** — §6.2.1 items 1–7, two of which correct §6.2's approved row | — |

---

## Appendix B — Gate Decision Record (2026-08-10)

Decisions taken by the reviewer at the architecture gate, and what each one closed.

| # | Item | Decision | Status change | Where applied |
|---|---|---|---|---|
| 1 | **C-DOM-005** — SAR mechanism | No mechanism exists or is agreed. §4.2 is a **proposal only**. Accepted as a known gap to close during or before development | SOFT warning → **ACCEPTED (open item carried to development-agent)** | §4.2 rewritten; §5.12 mode 3 marked proposed; risk A-R22 added; Appendix A FR-053 |
| 2 | **C-DOM-013** — audit log retention | **6 years** | DERIVED (unconfirmed) → **CONFIRMED** | §6.5; ADR-019; risk A-R11 closed; §12 |
| 3 | **C-DOM-022** — role membership review cadence | **6 months** — supersedes the sources' "quarterly or per panel round" assumption | TBC → **CONFIRMED**; SDD OQ-008 closed | §6.6; risk R9; Appendix A |
| 4 | **ADR-003** — trustee portal type | **Code App.** Canvas App descoped and rejected | `Decision required` → **`Adopted`** | ADR-003; §1.2; §2.2; §6.1; §6.7; §8; §9.3; risk A-R17 closed; Appendix A |
| 5 | **ADR-006** — environment topology | **Three environments: DEV, TST/ACC, PRD** (Test and Acceptance combined). Promotion `DEV → TST/ACC → PRD` | `Decision required` → **`Adopted`** | §9 rewritten; **§9.1 pipeline gate-structure deviation recorded**; risk A-R15 closed, A-R18 revised; §12 (new `REV-GrantApplications-ACC` group, three environments) |
| 6 | **§6.1** — group-team binding pattern | Derived pattern accepted as-is; no change to the mapping table | DERIVED (flagged) → **DERIVED, confirmed** | §6.1 |

**Still open after this gate** (neither blocks development starting, both must be settled before the pipeline
config is generated): ~~**ADR-007** ALM tooling, and~~ **ADR-011** intake channel / endpoint-trust route
including the out-of-palette Azure Key Vault dependency.
→ **ADR-007 was closed on 2026-08-12 in favour of Power Platform Pipelines** by explicit reviewer decision,
against this TAD's recommendation. See §9.2, ADR-007 and the new ADR-021. **ADR-011 remains the only
architectural decision still open.** **Unchanged and still outstanding externally:** DPO decisions
SDD OQ-004/005/006 (ADR-002 conditional), the WBS 0.3 service account with Wanstor (risk A-R13), and the
performance / availability / SAR-SLA thresholds SDD OQ-020/OQ-021/OQ-023.

---

## Approval
**Reviewed by:** Xander Lykopoulos  **Date:** 2026-08-10  **Response:** `APPROVED`

Approved with one explicitly accepted SOFT constraint warning: **C-DOM-005** — no SAR extract mechanism is
built or agreed (§4.2, risk A-R22), carried forward to development-agent as an open item.
