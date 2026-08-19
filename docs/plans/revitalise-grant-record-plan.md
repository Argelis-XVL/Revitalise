# Solution Design Document — Grant Record and Signed-Acceptance Store

**Feature Slug:** `revitalise-grant-record`
**Requested By:** Xander Lykopoulos (reviewer)
**Date:** 2026-08-18
**Status:** APPROVED — 2026-08-18, with answers to OQ-G01, OQ-G02, OQ-G03, OQ-G06, OQ-G07 recorded below
**WBS tasks:** `0.4` (remainder) — Phase 0
**Unblocks:** `3.2`, `3.4`, `3.7` (Phase 1, #3 DocuSign Acceptance) · `6.6` (Phase 3) · `7.2` (Phase 4) · `8.4` (Phase 4)
**Parent SDD:** `docs/plans/revitalise-grant-automation-plan.md` (APPROVED)
**Parent TAD:** `docs/architecture/revitalise-grant-automation-architecture.md` (APPROVED)

> **This document introduces no new functional requirements.** Every requirement below is
> already approved in the parent SDD and is cited, never restated in full. That is deliberate:
> `IMP-0029` recorded a `blocker` in which an approved document restated a commercial baseline
> instead of citing it, and every downstream document inherited the error.

---

## 1. Business Context

Phase 1 of the signed Service Agreement (#3 Grant Acceptance, #1 Form Validation) is
contractually dated **25 September 2026** and has **0 of 13 WBS tasks started**, while Phase 2 —
dated three weeks later — is substantially built. `IMP-0031` recorded the cause: work order was
set by conversation rather than by the WBS dependency graph.

The repo-side blocker on Phase 1 is not the DocuSign account. It is that **`rev_grant` does not
exist**. WBS task `0.4` — Phase 0, marked `Status = Done` — names eight tables in its own
description; `src/solutions/RevitaliseGrantAutomation/Entities/` contains four
(`rev_applicant`, `rev_application`, `rev_errorlog`, `rev_setting`). `IMP-0030` recorded this as
a `blocker`: a hand-typed `Status` column is a claim, not a result.

Three of the acceptance automation's tasks write to the Grant record — `3.2` (create envelope
from an approved application), `3.4` (set status to *Acceptance Signed*, link the signed PDF),
`3.7` (bulk issue) — so none of them can be built against a table that is absent. `6.6`
(finalise decisions), `7.2` (duplicate-payment check, which reads the provider *via* the Grant)
and `8.4` (payment-to-grant wiring) have the same dependency.

This slice closes the `0.4` gap for the Grant record specifically, and stops there. It needs no
external party: no DocuSign account, no AI Builder credits, no QuickBooks access.

---

## 2. Objectives

1. Make the Grant record exist, in the shape the approved TAD §4 already specifies, so the three
   Phase 1 acceptance flows have somewhere to write.
2. Provide the signed-acceptance document store that ADR-014 adopted — one SharePoint library,
   URL held on the Grant row — with library permissions that independently deny the trustee role.
3. Bring WBS `0.4`'s claimed state and its actual state into agreement for this table, and record
   the remaining `0.4` gap (four further tables) rather than leaving it implied.
4. Exercise the self-learning system's gates on a first-of-its-kind artefact — a new entity is
   the shape that produced `IMP-0001`, `IMP-0006`, `IMP-0013`, `IMP-0015` and `IMP-0019`.

---

## 3. Scope

### In Scope

- **`rev_grant` entity**, Tier 4 — Restricted, with the columns TAD §4 enumerates:
  `rev_name` (autonumber `GR-2026-00001`), `rev_applicationid` (parental),
  `rev_amountawarded`, `rev_status`, `rev_holidaystart`, `rev_holidayend`, `rev_conditions`,
  `rev_docusignenvelopeid`, `rev_acceptanceissuedon`, `rev_acceptancesignedon`,
  `rev_signedpdfurl`, `rev_manualacceptancerecorded`, `rev_manualacceptancenote`,
  `rev_impactreport`, `rev_finalpaymentdate`.
- **One global option set** for grant status: *Awarded · Acceptance Issued · Acceptance Signed ·
  Paid* (TAD §4). Real values, not placeholders — `IMP-0014` shipped three dropdowns with no
  options because an `OPEN` assumption was recorded and not closed.
- **Relationship** `rev_application` 1:N `rev_grant`, parental, cascading per TAD §3.1 (6-year
  retention with the Application).
- **Form and views** on `rev_grant`, reachable at pack time. `IMP-0006`: an entity's `FormXml/`
  and `SavedQueries/` folders are dropped silently unless `Entity.xml` declares the empty marker
  elements — 0 warnings, 0 errors, 0 components created.
- **Security**: `REV Admin` table privileges; the Tier 4 columns that TAD §6's access matrix
  places behind column security added to the `REV_TrusteeRestricted` profile.
- **SharePoint signed-acceptance library** (ADR-014): one library, URL written to
  `rev_signedpdfurl`, permissions denying the trustee role independently of Dataverse.
- **Settings row(s)** only if the architect finds one is required; none is anticipated.

### Out of Scope

- The three acceptance flows `REV | Acceptance | Create Envelope / Reminders & Escalation /
  Completion` (WBS `3.2`, `3.3`, `3.4`) — blocked on the DocuSign account, template and UK
  residency evidence (Dev Summary §7.3). This slice makes them buildable; it does not build them.
- The DocuSign connection reference, and any DocuSign configuration.
- `rev_review`, `rev_provider`, `rev_bankaccount`, `rev_payment`, `rev_anonymisedstatistic` — the
  rest of WBS `0.4`'s eight tables. Named here so the remaining gap is explicit, not implied.
- `rev_providerid` on the Grant. TAD §4 declares it referential to `rev_provider`, which does not
  exist and belongs to WBS `8.1` — Phase 4, and **#8 has no FR behind it** (TAD §3.5 conflict 2).
  See OQ-G03.
- The retention and erasure helper flow, and the 6-year bulk-delete job keyed on
  `rev_finalpaymentdate`. The column ships; the job does not (Dev Summary §7.3).
- The post-approval referee / emergency-contact form (Dev Summary §7.4 — design scope of #3, and
  who completes it is still unspecified).

---

## 4. Functional Requirements

**Inherited from the parent SDD. No new ids.** Each row states what *this slice* must deliver for
the approved requirement to become satisfiable; the requirement text itself is in
`docs/plans/revitalise-grant-automation-plan.md`.

| Approved ID | What this slice delivers toward it | Priority |
|---|---|---|
| FR-040 | The Grant record the finalise step applies verdicts to | High |
| FR-041 | The fields the acceptance document is pre-populated from: amount, dates, conditions | High |
| FR-045 | `rev_status` = *Acceptance Signed* as a real option value, and `rev_signedpdfurl` + the library it points into | High |
| FR-046 | `rev_manualacceptancerecorded` + `rev_manualacceptancenote` — the print-sign-scan route, recorded against the Grant | High |
| FR-047 | A Grant record per approved application, so a batch issue has one row per grant to write | Med |
| FR-048 | `rev_finalpaymentdate` (the 6-year clock's trigger date) and the parental cascade from Application | High |
| FR-050 | The financial record that survives erasure of the personal record under the Charities Act 2011 duty | High |
| FR-055 | Nothing directly; noted because the anonymised snapshot draws on Grant outcome data and is out of scope here | Low |

**Requirements this slice explicitly does NOT advance:** FR-042, FR-043, FR-044 (signature
sequencing, reminders, escalation) — all three are flow behaviour against DocuSign.

---

## 5. Non-Functional Requirements

Inherited, cited, not restated:

| Approved ID | Relevance to this slice | Category |
|---|---|---|
| NFR-002 | Bank/payment separation — informs which Grant columns the finance role sees; the finance role itself is WBS `8.2` | Security |
| NFR-009 | UK region and residency, including the SharePoint library created here | Compliance |
| NFR-010 | Retention enforced by status and trigger date — `rev_finalpaymentdate` is that trigger for the 6-year class | Compliance |
| NFR-011 | The backup/restore window must sit inside the retention period of the Grant records | Compliance |
| NFR-013 | Data minimisation — the column list is TAD §4's, not an expansion of it | Compliance |
| NFR-014 | Create/update/delete auditing with before/after values on a record holding personal data | Audit |
| NFR-016 | Retention evidence log holds no personal data | Audit |

---

## 6. User Stories

Existing stories, with the acceptance criteria **this slice** can satisfy. No new stories.

### US-003: Accept a grant without a printer
- Given a grant exists, when the acceptance is completed, then its status can hold *Acceptance
  Signed* and the signed document's location is recorded on the grant. → FR-045
- Given an applicant cannot sign electronically, when the paper route is used, then the manual
  acceptance and its note can be recorded against the grant. → FR-046
- *Not satisfiable by this slice:* AC-2 and AC-3 (signature sequencing, reminders) — flow work.

### US-008: Enact the board's decisions in one step
- Given verdicts have been recorded, when decisions are finalised, then there is a grant record
  per approved application for the verdict to be applied to. → FR-040, FR-047

### US-004 / US-011: Know what is held about me · Retention happens without me
- Given a grant record exists, when its parent application is deleted, then the grant is deleted
  with it by the parental cascade. → FR-048
- Given the financial record duty applies, when erasure is requested, then the columns the duty
  covers are identifiable on the grant. → FR-050
- *Not satisfiable by this slice:* the retention run itself, and the purge of the signed PDF and
  signature envelope (FR-049) — both need the deferred helper flow.

### US-015: Finance sees payments, and nothing it does not need
- Given the finance role does not yet exist, when it is created in WBS `8.2`, then the Grant's
  financial columns are already classified and secured for it. → NFR-002

---

## 7. Compliance & Regulatory Considerations

### 7.1 Data classification (satisfies C-DOM-001)

`rev_grant` — **Tier 4, Restricted** (TAD §3.1): personal + financial. Retention: cascade with
the Application, **6 years from final payment**. This classification is the parent TAD's, not a
new judgement.

The classification drives two things the architect must settle precisely: which columns join
`REV_TrusteeRestricted`, and the library permission that denies the trustee role the signed PDF.
ADR-014's own *negative* consequence is that the PDF sits outside Dataverse and is therefore
**not** protected by column security, so the library ACL is the only control — the access matrix
gives the trustee "link only".

### 7.2 Lawful basis (satisfies C-DOM-002)

Cited verbatim in scope from the parent SDD §7.2, which records Revitalise's own bases from its
Privacy Notice (20 Feb 2026) and does not set them:

> **Grant (award, provider, dates, conditions, signed acceptance)** — Art. 6: necessary to
> administer and evidence the grant; retention under the Charities Act 2011 duty. Special
> category: n/a.

**No special-category data enters this entity.** Health and condition data stays on
`rev_application` behind NFR-001. The architect must confirm no Grant column becomes a route to
it — `rev_conditions` holds *grant conditions* (the terms of the award), not health conditions,
and the name is close enough to be worth stating explicitly.

### 7.3 Obligations touched

| Obligation | How this slice addresses it |
|---|---|
| Art. 5(1)(c) minimisation | Column list is TAD §4's exactly; nothing added |
| Art. 5(1)(e) storage limitation | `rev_finalpaymentdate` + parental cascade give the retention run its trigger and its scope |
| Art. 5(2) accountability | Native field-change auditing on the new entity (NFR-014) |
| Art. 17 erasure, with carve-out | FR-050's financial-record duty is why the Grant is the entity where erasure has a legal hold; the carve-out must be reportable (FR-052) |
| Art. 32 security | Column security on Tier 4 columns; SharePoint ACL denying trustees |

**DPIA / RoPA:** the Grant entity and the signed-PDF library are both already described in
`docs/Import/Revitalise-DPIA-v0.1.docx` and `Revitalise-RoPA-v0.1.docx`. This slice creates no
processing those documents do not already cover, so no DPIA revision is proposed. The architect
should confirm that the library's UK residency is evidenced rather than assumed (NFR-009, DPIA
action A5 — still open, TAD risk A-R19).

---

## 8. Assumptions & Dependencies

| # | Assumption / dependency | Status |
|---|---|---|
| A | `rev_application` exists in DEV and is deployable | ✅ Verified in source and deployed (Dev Summary §2.7) |
| B | `REV_TrusteeRestricted` column-security profile exists to extend | ✅ Verified in `Other/FieldSecurityProfiles.xml` |
| C | `REV Admin` role exists to grant table privileges to | ✅ Verified in `Roles/` |
| D | DocuSign is **not** required for this slice | ✅ By scope — no connector, no connection reference |
| E | A SharePoint site exists, or may be created, to hold the library | ⛔ **Unconfirmed.** Site creation is a **tenant-level** operation behind `APPROVE TENANT` (`provisioning/sharepoint/ensure-site.ps1`). Never yet executed |
| F | Cert-based app-only auth to DEV works from this Mac's keychain | ✅ `IMP-0022` — thumbprint `A6F94E…C7FE`, app id `077f1f90-…`. Do not ask the reviewer to re-supply |
| G | The service account's unattended sign-in Conditional Access exception | ⛔ **Still outstanding with Wanstor** (Dev Summary §7.4). Blocks TST/ACC/PRD, not DEV |
| H | `pac`-based DEV import path is proven | ✅ 15-attempt history, now succeeding (Dev Summary §2.7) |

### Digest lessons that apply to this slice, read before starting

From `logs/known-failure-modes.md` — this is a checklist against the build, not background:

- `IMP-0001` — never infer a SolutionPackager shape; copy it from a real exported instance.
- `IMP-0006` — declare `<FormXml />` / `<SavedQueries />` markers in `Entity.xml` or the folders
  pack to nothing, silently.
- `IMP-0013` / `IMP-0018` — after import, query **every** declared component type by name, from a
  list derived from source.
- `IMP-0019` — import relabels option values but never deletes omitted ones. Get the status option
  set right the first time.
- `IMP-0015` — form label **text** is asserted by nothing. Check labels against each attribute's
  own authored wording.
- `IMP-0014` — an `OPEN` assumption is a prediction of a live defect. `C-TECH-058` now blocks the
  deploy on one.
- `IMP-0017` — a wrong column *type* costs three imports to correct. Settle types before the first
  deploy.

---

## 9. Open Questions

**Answered at the plan gate, 2026-08-18, by the reviewer.** Recorded here so architect-agent
inherits closed questions rather than `OPEN` assumptions — `C-TECH-058` blocks a deploy on an
`OPEN` register row, and `IMP-0014` is why.

| # | Answer | Consequence for architecture |
|---|---|---|
| **OQ-G01** | **CLOSED.** The site collection exists: `https://revitalise212.sharepoint.com/sites/GrantApplications/`. **No document library is designated yet** | No tenant-level site creation, so **no `APPROVE TENANT` gate for this slice**. The library is created inside an existing site — `provisioning/sharepoint/ensure-site.ps1` is scoped down to ensure-library. The site URL is environment-specific and must be an **environment variable**, never a literal (`C-TECH-047`) |
| **OQ-G02** | **CLOSED.** Trustees see Dataverse data only. They do not look at signed PDFs — those are the grant administrator's | The library grants no access to the trustee group at all. Simpler and stronger than a deny: the trustee role is simply not a member. Removes ADR-014's residual worry, and the architect states the membership positively rather than as an exclusion |
| **OQ-G03** | **CLOSED — agreed, leave out.** `rev_providerid` is not built in this slice | Provider linkage arrives with WBS `8.1`. The TAD must record it as a **deliberate deferral with a named later task**, not an omission, and confirm that adding a lookup later needs no type change (`IMP-0017` cost three imports for a type change; an added lookup costs one ordinary import) |
| **OQ-G06** | **CLOSED — reverse the logic.** Grant no access now, so access can be granted later. The environment is empty | The finance-relevant Grant columns are **secured now and released to nobody**, rather than left open and secured later. This is the safe direction: retro-fitting column security to a populated table is disruptive, whereas releasing a secured column to a new profile is additive. The architect must confirm `verify-field-security-coverage.py` passes when a secured column is released by **no** profile — if that gate treats an unreleased secured column as a violation, the gate and this decision disagree and the gate wins until changed |
| **OQ-G07** | **CLOSED — agreed, this table only** | `rev_review`, `rev_provider`, `rev_bankaccount`, `rev_payment`, `rev_anonymisedstatistic` stay out. The remaining WBS `0.4` gap is recorded, not closed |

**Still open, carried to the architecture gate:**


| # | Question | Owner | Due |
|---|---|---|---|
| OQ-G04 | **Does `rev_docusignenvelopeid` ship in this slice?** It is a DocuSign artefact on an otherwise DocuSign-free slice. Shipping it now costs nothing and avoids a second schema pass; leaving it out keeps the slice honest about what is unverified. Recommend **ship it**, empty, and record it as unexercised until `3.2` | Architect | Architecture gate |
| OQ-G05 | **Is `GR-2026-00001` the agreed grant reference format?** TAD §4 states it. The parent SDD's FR-008 reference-format conflict (TAD §3.5 row 1) was resolved for Application and Applicant but the Grant format was never separately confirmed | Reviewer / Emily | Before build |

---

## 10. Effort Estimate

> **This section cites the contracted baseline; it does not restate or replace it.** `IMP-0029`
> is an open `blocker` against the parent SDD §10, which states 106–160 hours over 7 automations
> against a signed 292 hours over 9. Nothing below should be read as amending the agreement.

**Contracted baseline for this work:** WBS `0.4` — *"Dataverse solution & table schema build"* —
**5–8 hours**, Phase 0, per `docs/Import/Revitalise-WBS-Grant-Automation-v0.5.xlsx`. That range
covers all eight tables named in the task, plus the SharePoint library and permission groups.

**Consumed to date: unknown.** All 61 `Actual Hours` rows in the WBS are empty (`IMP-0032`), so
what the four existing tables cost is unrecorded. This slice cannot be netted against the
baseline until that is resolved.

**Proposal for this slice — a proposal, not a contractual figure:**

**Size:** **S**
**Range:** **3–5 hours**, on the assumption that OQ-G01 (the SharePoint site) is answered without
a site collection needing to be created. If a new site collection **is** required, add 1–2 hours
and a tenant-level gate.

| Component | Proposed | Basis |
|---|---|---|
| `rev_grant` Entity.xml, columns, option set, relationship | 1.5–2 h | Comparable to the `rev_errorlog` pass, plus a parental relationship |
| Form + views, with markers and label text checked | 0.5–1 h | `IMP-0006` and `IMP-0015` both land here |
| Role privileges + column security profile members | 0.5 h | Extending existing artefacts, not creating them |
| SharePoint library + trustee denial + provisioning script | 0.5–1.5 h | Wide because OQ-G02 is unanswered |

Per `IMP-0032`, actual hours are proposed **at the DEV deploy and in the dev summary**, not at
month end.

---

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
