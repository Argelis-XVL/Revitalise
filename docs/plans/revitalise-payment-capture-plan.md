# Solution Design Document — Payment Capture Form (Automation #8, WBS 8.3)

**Feature Slug:** revitalise-payment-capture
**Requested By:** Xander Lykopoulos (reviewer / maker, Argelis Consultancy)
**Date:** 2026-09-09
**Status:** DRAFT
**WBS task id:** 8.3 — "Build payment capture form" (`contract/wbs.json`)

<!-- id-allocation: FR-150..FR-154, NFR-150, OQ-150..OQ-152, US-030 -->

> **Delta SDD.** This document is a delta against the approved parent SDD
> `docs/plans/revitalise-grant-automation-plan.md`, which allocates
> `FR-001..FR-063, FR-070..FR-079, NFR-001..NFR-032, OQ-001..OQ-048, US-001..US-023`.
> It takes a **disjoint block well clear of the parent's growth path** rather than continuing the
> parent's sequence, per `agents/plan-agent.md` step 4a. Requirements owned by the parent are
> cited by their parent id and are never restated or renumbered here.

**Mode: Author, not Intake.** Intake was considered and rejected. The candidate sources
(`docs/Import/grant-application-data-model-v0.2.md`, `Revitalise-Solution-Architecture-v0.4.docx`)
are design material already incorporated into the approved TAD and into `knowledge/domain/`; they
carry no functional requirements to adopt. What is missing is precisely the FR layer, which no
source contains. So this document authors it. Where a source and the built solution disagree,
**solution source under `src/solutions/RevitaliseGrantAutomation/Entities/` is the ground truth
used here** and the disagreement is named rather than silently resolved.

---

## 1. Business Context

Revitalise's finance role — a single 0.5 FTE post — is the sole holder of bank data in this
solution. It records the holiday providers the charity pays, the bank accounts it pays into, and
the individual disbursements made against an awarded Grant. Today this happens outside the
platform; the grant record and the money that discharges it live in different places, and the
QuickBooks reference that ties them together is held by one person.

Automation #8 closes that gap. The three tables it needs — Provider, Bank Account and Payment —
already exist in solution source, delivered under WBS 8.1. **What does not exist is any surface
from which the finance role can use them.** Every column on Bank Account and Payment except the
two primary name attributes is marked `IsSecured=1` and released only through the
`REV_FinanceOnly` column-security profile, so the data is, by design, invisible from the existing
grant administration app. WBS 8.3 delivers that surface.

### 1.1 The scope question this document closes

The approved parent SDD lists *"Payment process automation (company card, provider payments)"* as
out of scope, and the approved TAD records the resulting conflict at **TAD §3.5 conflict 2**.
`knowledge/domain/business-rules.md` **BR-F07** restates that conflict as *"Automation #8 …
has no functional requirement behind it … It must be authorised as a scope addition or descoped
before hours are booked to it."*

**BR-F07 overstates the gap on both halves, and the reasons are on the record.**

| BR-F07 says | The cited sources say | Consequence for WBS 8.3 |
|---|---|---|
| Automation #8 has no FR behind it | TAD §3.5 conflict 2 scopes the gap narrowly: *"The Bank Account and Payment tables, the Finance role and a minimal finance surface **are** required by US-015 AC-1 and NFR-002, so they are retained in this TAD. The `REV \| Finance \| Capture Payment` **flow** has no FR behind it."* | The **flow** is unrequirement'd. The **form** — WBS 8.3's deliverable — is already required by parent US-015 AC-1 and NFR-002. This document supplies its FRs. |
| It must be authorised or descoped before hours are booked | `docs/Import/baseline-lock.yml` → `d1_d2_phase_mapping.finance_workstream_note`, recorded from the reviewer 2026-08-19: *"D-2 asked whether Automation #8 (Finance) is a change order. Under D-5 it is IN the accepted specification, so it is in scope."* | Commercially **settled**. Automation #8 is inside the customer-accepted WBS v0.5, and 8.3 is one of its 61 tasks. No change order is required and none is proposed (`C-COM-002` is satisfied by the task id). |

So this SDD proceeds. It closes the *documentation* gap — the missing FR layer behind a
contracted deliverable — and it does not reopen a *commercial* question that
`docs/Import/baseline-lock.yml` already answers. BR-F07's own staleness is logged as a finding
rather than edited here; only `improvement-agent` edits `knowledge/`.

**The `REV | Finance | Capture Payment` flow remains unauthorised and is explicitly out of scope
below.** TAD §3.5 conflict 2's reviewer decision on the flow is still open and is not this task's
to take.

---

## 2. Objectives

1. Give the finance role one place to record a Provider, a Bank Account and a Payment against an
   awarded Grant, and to record the QuickBooks reference that reconciles it.
2. Preserve separation of duties absolutely: nothing this surface adds may make bank or payment
   data reachable by the administrator role, the trustee role or the service identity
   (parent NFR-002, BR-F02).
3. Add no new personal-data processing. The surface exposes columns that already exist; it must
   not become the place where a natural person's identity leaks into an unsecurable column.
4. Leave the QuickBooks duplicate-payment check (Automation #7) and the unauthorised Finance
   capture flow untouched, so that neither is pre-empted by this task.

---

## 3. Scope

### In Scope — WBS 8.3 only

- A **finance-role application surface** presenting the three existing tables `rev_provider`,
  `rev_bankaccount` and `rev_payment`, with the forms and views needed to create and edit rows.
- **Payment capture**: Grant, Payee bank account, Amount, payment date, method, payment status,
  final-payment flag, and the **QuickBooks reference** (`rev_payment.rev_qboreference`) that WBS
  8.3's description names.
- **Provider capture** and **Bank Account capture** as the supporting records a payment needs.
- Data-entry rules that keep identifying values out of the two columns Dataverse cannot secure
  (FR-153, FR-154).

### Out of Scope

Each item below belongs to a different WBS task id or to no accepted task at all. Per
`C-COM-002`, none is built here and none is reconciled later.

| Excluded | Why, and where it belongs |
|---|---|
| The `REV \| Finance \| Capture Payment` flow | No FR behind it; TAD §3.5 conflict 2's reviewer decision is still open. Not an accepted WBS task in its own right. |
| Building or reworking the **REV Finance security role** | **WBS 8.2**, a separate task. See §8 D-1 — 8.3 depends on it functionally, but does not deliver it. |
| Payee logic (Payment names one Payee; provider retained via the Grant for reporting) | **WBS 8.4** |
| Recording test payments and verifying the duplicate-payment hook | **WBS 8.5** |
| The QuickBooks duplicate-payment check itself | **Automation #7**, parent FR-023 |
| Any change to the Provider / Bank Account / Payment **schema** | **WBS 8.1**, already delivered. This surface binds the columns that exist; it adds none. |
| Full QuickBooks API integration | Parent SDD out-of-scope; ADR-017 fallback position stands |

---

## 4. Functional Requirements

Every named data item below was resolved to a `(table, column)` pair against
`src/solutions/RevitaliseGrantAutomation/Entities/*/Entity.xml` and to its release state against
`src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml`, per
`skills/how-to-write-requirements.md` → *Data Provenance*. The measurements are in §4.1.

| ID | Requirement | Priority |
|---|---|---|
| FR-150 | The system SHALL present a single application surface from which `rev_provider`, `rev_bankaccount` and `rev_payment` records can be created, read and edited, WHEN the signed-in user holds the finance role, SO THAT the finance role can record a disbursement without being granted access to any other part of grant administration. | High |
| FR-151 | The payment capture surface SHALL require a Grant (`rev_payment.rev_grantid`), a payee bank account (`rev_payment.rev_bankaccountid`) and an amount (`rev_payment.rev_amount`) to be populated before a Payment record can be saved, SO THAT no disbursement is recorded that cannot be reconciled to an awarded grant. | High |
| FR-152 | The payment capture surface SHALL present the QuickBooks reference (`rev_payment.rev_qboreference`) as an optional field at creation and an editable field thereafter, SO THAT the reference can be recorded against the payment once QuickBooks has issued it, without blocking capture of a payment that has not yet been issued. | High |
| FR-153 | The Provider contact fields (`rev_provider.rev_contactemail`, `rev_provider.rev_contactphone`) SHALL hold organisational contact points only — a role-based address and a switchboard or department number — and SHALL NOT hold a named individual's personal contact details, SO THAT the Provider record remains outside the scope of personal-data processing and requires no lawful basis of its own. | High |
| FR-154 | The Bank Account nickname (`rev_bankaccount.rev_name`) SHALL NOT contain an applicant's name, nor any other identifier of a natural person, SO THAT a bank account cannot be attributed to an individual by a user who holds Read on Payment but is not a member of the `REV_FinanceOnly` profile. | High |

### 4.1 Data provenance — the measurements behind the clauses above

Measured 2026-09-09 from solution source. `secured` means `<IsSecured>1</IsSecured>`, released
only to members of `REV_FinanceOnly`.

| Table | Columns | Secured | Unsecured |
|---|---|---|---|
| `rev_provider` | 6 — `rev_name`, `rev_contactemail`, `rev_contactphone`, `rev_addressline`, `rev_region`, `rev_active` | 0 | all 6 |
| `rev_bankaccount` | 8 | 7 | `rev_name` only |
| `rev_payment` | 10 | 9 | `rev_name` only |

**16 secured columns across the two finance tables**, which matches `FieldSecurityProfiles.xml`'s
own statement that `REV_FinanceOnly` *"releases exactly the 16 IsSecured=1 columns across those two
tables"*. The profile is present in source; the role that would be its member is not (§8 D-1).

Two consequences drive FR-153 and FR-154, and both are platform facts rather than design choices:

1. **A primary name attribute cannot be secured at all.** `C-TECH-070`, ground-truthed 2026-08-23:
   a `IsSecured=1` primary name fails outright with `0x8004f501`. `rev_bankaccount.rev_name` and
   `rev_payment.rev_name` are therefore permanently readable by anyone holding table Read.
2. **A lookup's automatic `<lookup>name` companion reports `CanBeSecuredForRead=False`.** Also
   `C-TECH-070`. Securing `rev_payment.rev_bankaccountid` hides the GUID and **not** the related
   Bank Account's nickname text. So the nickname is projected onto every Payment row.

`rev_bankaccount.rev_name`'s own column description already anticipates this and asks for *"a
nickname or masked last-four identifier"*. **Nothing enforces it, and the payment capture form is
the exact surface where that value gets typed.** For a provider account a nickname is naturally
non-identifying ("Sunrise Lodge - main"); for an **applicant reimbursement** account the natural
thing for a finance user to type is the applicant's name, and that would leak an identity through
the lookup projection to every holder of Read on Payment. FR-154 exists for that case
specifically. OQ-151 asks the business what convention to use instead.

### 4.2 Requirements NOT written, and why

Per `skills/how-to-write-requirements.md`, an open question does not qualify a requirement — it
either blocks the clause or the clause omits the thing in question.

- **No FR requires the surface to display a duplicate-payment warning.** That check is Automation
  #7 / parent FR-023 and its second call site is WBS 8.5's to verify. A clause here would commit
  scope this task was not quoted for.
- **No FR names the finance role's privileges on Grant.** Selecting a Grant under FR-151 implies
  Read on `rev_grant`, but the role does not exist yet and its privilege set is WBS 8.2's
  deliverable. Recorded as OQ-152, not written into an FR this task cannot satisfy.

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-150 | Every column on `rev_bankaccount` and `rev_payment` other than the two primary name attributes SHALL remain released only through the `REV_FinanceOnly` column-security profile. The payment capture surface SHALL introduce no new unsecured column on either table, and no calculated or rollup column on any table that derives its value from a secured column — including any rollup of `rev_payment.rev_amount` onto Grant or Application. | Security |

Parent NFR-002 (bank and payment data readable by the finance role only; administrator role has no
access) governs this feature and is **not** restated as a new id. NFR-150 is the additive clause:
it constrains what this *surface* may do, which NFR-002 does not cover. A rollup is the specific
hazard — it is the one construct that lawfully copies a secured value into an unsecured one.

---

## 6. User Stories

### US-030: Finance records a disbursement in one place

**As a** finance officer, **I want** one surface where I can record a provider, its bank account
and a payment against an awarded grant with its QuickBooks reference, **so that** a disbursement
is captured against the grant it discharges without my needing access to applicant case data.

**Acceptance Criteria:**

- **AC-1** — Given I hold the finance role, when I open the finance surface, then I can create,
  read and edit Provider, Bank Account and Payment records. → FR-150
- **AC-2** — Given I am creating a Payment, when I attempt to save without a Grant, a payee bank
  account or an amount, then the record is not saved and the missing field is identified. → FR-151
- **AC-3** — Given a Payment record exists, when QuickBooks issues its reference, then I can record
  that reference against the payment without recreating it. → FR-152
- **AC-4** — Given I do **not** hold the finance role but do hold Read on Payment, when I open a
  Payment record, then every column except its name is empty, and the name identifies no natural
  person. → FR-154, NFR-150
- **AC-5** — Given I am creating a Provider, when I enter contact details, then the values recorded
  are organisational contact points and not a named individual's. → FR-153

**AC-4 is not verifiable until WBS 8.2 delivers the finance role** — see §8 D-1. It is stated here
because it is this feature's acceptance criterion, and deferred rather than dropped.

---

## 7. Compliance & Regulatory Considerations

Assessed against `skills/compliance-checklist.md` §1 (universal) and
`knowledge/domain/compliance-requirements.md`.

### 7.1 Lawful basis per entity in this feature's scope (satisfies C-DOM-002)

The lawful bases are **Revitalise's own**, from its Privacy Notice (20 Feb 2026). This document
records them; it does not set them. Bank Account and Payment are cited from the parent SDD §7.2,
unchanged.

| Entity | Holds personal data? | Art. 6 basis | Art. 9 condition | Source |
|---|---|---|---|---|
| Bank Account (`rev_bankaccount`) | Yes — account holder name, sort code, account number; may be an applicant's | Necessary to pay the grant and meet financial-record duties | n/a | Parent SDD §7.2, unchanged |
| Payment (`rev_payment`) | Yes, by linkage to Grant and Bank Account | Necessary to pay the grant and meet financial-record duties | n/a | Parent SDD §7.2, unchanged |
| Provider (`rev_provider`) | **No, by design — see below** | Not applicable | n/a | This document, FR-153 |

**Provider.** The parent SDD §7.2 records Provider as *"Not classified in any source document"*
and defers it to **OQ-026** (DPO / architect, at TAD stage). That question is inherited backlog and
is **not reopened here**. This feature does not need it answered, because ground truth shows
`rev_provider` carries **no contact-name column at all** — only an organisation name, a
contact email, a contact phone, an address line, a region and an active flag. The only items that
could be personal are the two contact points, and **FR-153 requires them to be organisational**.
On that basis Provider holds no personal data within this feature's scope and needs no lawful
basis of its own.

> ⚠️ **This is a conditional pass and the condition is FR-153.** If the reviewer rejects FR-153 —
> if finance must be able to record a named individual at a provider — then Provider holds personal
> data, OQ-026 becomes blocking for this feature, and the DPO must supply a basis before the form
> is built. Flagged in the gate output as a decision, not buried here.

### 7.2 Other universal controls

| Control | Position |
|---|---|
| **Minimisation** (Art. 5(1)(c)) | The surface binds only columns WBS 8.1 already delivered; it adds none. FR-153 and FR-154 actively reduce the personal data held. |
| **Storage limitation** (Art. 5(1)(e)) | Unchanged by this feature. Payment cascades from Application (BR-D02); an applicant reimbursement account is purged with the payment it served (BR-F05). |
| **Audit** (Art. 5(2)) | Unchanged. `rev_bankaccount` and `rev_payment` are already in the audited-tables list, and `rev_bankaccount.rev_name` carries `IsAuditEnabled=1` in source. This feature adds no column and therefore no audit gap. |
| **Access control** | Parent NFR-002 and NFR-150. The whole control rests on the `REV_FinanceOnly` profile having a member — see §8 D-1. |
| **No personal data in logs** (parent NFR-012) | Unchanged. This feature writes no operational log. |
| **Erasure** (Art. 17, parent FR-051) | Unchanged. Bank Account's reachability by the erasure sweep is an open remediation in the parent TAD and is not this task's to close. |
| **Accessibility** (Equality Act 2010) | The finance surface is a staff-facing internal surface, not applicant-facing. `skills/accessibility-checklist.md` still applies to it as a UI. |

---

## 8. Assumptions & Dependencies

### D-1 — A real dependency on WBS 8.2 that the contracted dependency graph does not record

**This is the finding this dispatch was asked to verify. It is real.**

| What | Measured 2026-09-09 |
|---|---|
| `contract/wbs.json` → task 8.3 | `depends_on: ["8.1"]` — 8.2 is not named |
| `src/solutions/RevitaliseGrantAutomation/Roles/` | Holds three roles: `REV Admin`, `REV Service Automation`, `REV Trustee`. **No finance role.** |
| `Other/FieldSecurityProfiles.xml` | `REV_FinanceOnly` exists and releases the 16 secured columns. Its intended membership is *"the REV Finance role's group team only"*. That role does not exist, so the profile has no member. |
| `logs/state/wbs-state.json` → 8.2 | `derived_status: complete` |

**Why the form is unusable until 8.2 lands.** 16 of the 18 columns across Bank Account and Payment
are secured, and the two that are not are the primary names. With no finance role, nobody
is a member of `REV_FinanceOnly`, so the payment capture form renders with **every field empty for
every user**, including its author. FR-150 and AC-1 through AC-5 are therefore not verifiable at
V4 until WBS 8.2 delivers the role and binds it to the profile.

**The scoping decision this document takes.** WBS 8.3 **proceeds now**, and the dependency is
recorded as an **acceptance precondition rather than an authoring blocker**:

- The form, views and app-module definition are solution source. They can be authored, packed,
  imported and gated with no finance role in existence.
- What cannot happen without 8.2 is **V4 sign-off** — a signed-in finance user opening the form and
  seeing data. That is stated here so nobody later reports 8.3 complete on V3 evidence.
- **8.2 is not reworked here.** It is a separate WBS task id with its own hours, and rebuilding it
  inside 8.3 would be exactly the unquoted work `C-COM-002` forbids.

**Recommendation to the reviewer:** add `8.2` to task 8.3's `depends_on` in `contract/wbs.json`.
That is a change to the contracted dependency graph and therefore `pm-agent`'s or
`commercial-agent`'s to make, not this agent's.

### D-2 — WBS 8.2's completion evidence does not test what it claims

Also verified, and logged as a finding. `contract/evidence-map.json` gives task 8.2 — *"Build
finance security role"* — this evidence rule:

```
{"kind": "grep", "file": "src/solutions/*/Roles/*/*.xml", "pattern": "rev_bankaccount"}
```

It matches, and `logs/state/wbs-state.json` therefore derives 8.2 as `complete`. **The line it
matches is a comment in `REV Trustee.xml` stating that the trustee role holds *no* privilege on
`rev_bankaccount`** — *"No rev_bankaccount or rev_payment privilege of any kind."* The rule is
satisfied by prose asserting the exact opposite of what it is meant to prove, in a file belonging
to a different role. A grep for a table name across all role files cannot distinguish a grant from
a documented refusal, and no finance role exists for it to find.

This is `C-COM-005`'s own principle — a status is a claim, not a result — reaching the derivation
itself. Not fixed here: `contract/evidence-map.json` is not this agent's to edit.

### Other assumptions

| # | Assumption | If wrong |
|---|---|---|
| A-1 | Automation #8 is inside the customer-accepted specification and needs no change order. | Recorded from the reviewer at `docs/Import/baseline-lock.yml` → `d1_d2_phase_mapping`. If withdrawn, 8.3 becomes a `commercial-agent` decision before anything is built. |
| A-2 | The finance surface is a **separate model-driven app**, not an area added to `rev_grantadministration`. | `contract/evidence-map.json` already expects `AppModules/rev_financecapture` as 8.3's evidence, and separation of duties argues the same way. Confirmed at TAD stage — OQ-150. |
| A-3 | The three tables need no schema change to support this form. | Verified: all 24 columns across the three tables exist in source today. If the TAD finds a gap, it is WBS 8.1 work, not 8.3. |
| A-4 | Provider's classification (parent OQ-026) stays open and stays out of this feature's path. | Holds only while FR-153 stands — see §7.1. |
| A-5 | The `REV \| Finance \| Capture Payment` flow stays unbuilt. | If the reviewer authorises it at TAD §3.5 conflict 2, it needs its own FR and its own task id; it is not absorbed into 8.3. |

---

## 9. Open Questions

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-150 | Is the finance surface a separate model-driven app (`rev_financecapture`) or an area inside the existing `rev_grantadministration` app? **Recommendation: separate app** — `contract/evidence-map.json` already names `AppModules/rev_financecapture` as this task's evidence, and a separate app keeps the administrator role off the surface entirely rather than relying on privileges alone. | architect-agent | TAD stage |
| OQ-151 | For an **applicant reimbursement** bank account, what nickname convention satisfies FR-154 while still letting a finance user recognise the account at a glance? A masked last-four is the column description's own suggestion; the business may prefer the grant reference. | Process owner (Emily) / finance | **CLOSED rev 8 (2026-09-10) — architectural half answered by TAD `ADR-046a`, reviewer-confirmed as proposed.** Re-dated 2026-09-11 (`IMP-0711`): the previous value was *Before build*, which names no observable event, is read by no gate, and was the wrong moment regardless — the exposure this question guards becomes live when **wbs:8.2 grants a persona Read on Payment**, not when the form is packed. Any residual business preference is a confirm-or-replace against `ADR-046a`, due at that privilege grant. |
| OQ-152 | Which privileges does the finance role need on `rev_grant` so a Grant can be selected under FR-151, and which Grant columns should the lookup surface? | WBS 8.2 / architect-agent | With WBS 8.2 |

**Inherited, not reopened, and not counted as this document's own:** parent **OQ-026** (Provider
classification and lawful basis) and the TAD §3.5 conflict 2 reviewer decision on the Finance
capture *flow*. Neither blocks this feature — see §7.1 and §3.

---

## 10. Effort & Baseline

**Size (this feature only):** **S**

**Drivers of that size:** No schema change and no integration — every column the form binds already
exists. Size is driven by the surface itself (an app module, site map, three forms and their views)
and by the two data-entry rules that exist because Dataverse cannot secure a primary name or a
lookup's name projection. It is **not** driven by the security model, which WBS 8.2 owns.

**Assumptions behind it:** A-2 (separate app module) and A-3 (no schema change). If A-3 turns out
false the work is WBS 8.1's, not this task's, and the size here does not move.

**Baseline reference — cited, never restated:**

| | |
|---|---|
| WBS task id(s) | **8.3** — this document delivers exactly one task |
| Baseline document | `contract/wbs.json` and `docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx` (authoritative for hours, phase and dates); `contract/service-agreement.json` for phase hours and milestone dates |
| Contracted phase | As stated by the baseline for task 8.3 — read it there; it is not inferred or restated here |

> No hours figure, fee, phase membership or delivery date is written into this document
> (`C-COM-004`, `C-COM-008`, `IMP-0029`). For work covered by an accepted WBS task the estimate
> **is** that task's range in `contract/wbs.json` — it is not re-derived here, and it is not
> re-estimated downward for AI assistance (baseline decision D-6).

---

## 11. Traceability Matrix

| FR | User story AC | WBS task | Parent requirement it serves |
|---|---|---|---|
| FR-150 | US-030 AC-1 | 8.3 | US-015 AC-1, NFR-002 |
| FR-151 | US-030 AC-2 | 8.3 | — (new) |
| FR-152 | US-030 AC-3 | 8.3 | — (new; WBS 8.3's "with the QuickBooks reference") |
| FR-153 | US-030 AC-5 | 8.3 | Art. 5(1)(c) minimisation; relates to parent OQ-026 |
| FR-154 | US-030 AC-4 | 8.3 | NFR-002, BR-F02 |
| NFR-150 | US-030 AC-4 | 8.3 | NFR-002 |

Test cases are `test-agent`'s to allocate. **US-030 AC-4 is not verifiable at V4 until WBS 8.2
delivers the finance role** (§8 D-1) and must not be reported as passed on V3 evidence.

---

## Approval
**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
