# Regulations & Obligations

**Populated 2026-08-18** (`IMP-0034`). Sources as listed in `knowledge/domain/overview.md`.
Obligations are the **controller's**, recorded here; this file does not set them.

---

## Applicable Frameworks

### UK GDPR and the Data Protection Act 2018

Every part of this platform processes personal data, and the application itself collects
**Article 9 special-category data** — health and disability condition profiles, an "other
condition" free-text note, benefit status, and ethnic group where captured.

Lawful bases, per entity, are recorded in the approved SDD §7.2 from Revitalise's Privacy Notice
(20 Feb 2026). In summary: **Article 6** — necessary to assess and administer the grant;
**Article 9(2)(b)** social protection and **Article 9(2)(h)** health and social care for the
special-category elements.

Key obligations for this platform:

- **Art. 5(1)(c) minimisation** — only fields needed to assess, decide, pay and report are
  collected (SDD NFR-013).
- **Art. 5(1)(e) storage limitation** — retention enforced automatically by status plus trigger
  date, not by anyone remembering (SDD NFR-010). Schedule below.
- **Art. 5(2) accountability** — native field-change auditing of every create/update/delete on a
  record holding personal data, with before/after values (SDD NFR-014).
- **Art. 15 right of access** — a complete extract for a named individual must be producible
  (SDD FR-053). ⚠️ **No mechanism exists yet, and no response-time SLA is recorded anywhere**
  (SDD OQ-023, C-DOM-005, TAD risk A-R22). Accepted as a known gap at the architecture gate.
- **Art. 17 right to erasure** — on-demand erasure across the Dataverse tables and every linked
  copy: the signed-PDF library, DocuSign envelopes and QuickBooks. Includes referees, helpers,
  group members and emergency contacts captured with the application (SDD FR-051).
  Legal-hold carve-outs are honoured and **reported to the requester** (FR-052).
- **Art. 32 security** — least-privilege roles, column security, separation of duties, TLS 1.2+
  on every hop, MFA on the service identity under a scoped Conditional Access exception.
- **Data residency** — 100% of processing, storage and backup in the **UK region**, across
  Power Platform, Dataverse, AI Builder, DocuSign and QuickBooks. Zero transfers outside the UK.
  ⚠️ **To be verified at environment setup and recorded as evidence, not assumed** (SDD NFR-009,
  DPIA action A5, TAD risk A-R19 — still open).

### Data (Use and Access) Act 2025 (DUAA)

Governs the **automated-decision** position. The scoring flow calculates a score, applies the
knockout threshold and income ceiling, and sets auto-pass / borderline / auto-reject.

The controller's stated safeguards (DPIA §8): disability, health-condition data and the free-text
narrative **do not feed the score**; the process owner reviews every borderline case, sets the
threshold, and can override any outcome; trustees make the funding decision on eligible cases.

⚠️ **Open, and it is the DPO's to confirm:** whether automatic rejection at the threshold, with
that oversight, meets Revitalise's automated-decision position. If a stronger form of human
review is required before a rejection stands, auto-reject outcomes route to the process owner
instead of closing — a configuration change within the current design, not a rebuild.

### Charities Act 2011

The **six-year financial-record duty**. This is why a successful grant's full record — including
the health free-text — is retained six years from final payment, and why erasure of a paid grant
carries a legal-hold carve-out that must be reported to the requester rather than silently
applied.

### Equality Act 2010

The applicant population is disabled by definition. Accessibility of the applicant-facing form
and of any trustee-facing app is an obligation, not an enhancement. See
`skills/accessibility-checklist.md`.

---

## Retention Schedule (as the controller has set it)

From `Revitalise-Data-Governance-Framework-v0.2.docx` §4. Enforced primarily by **native
Dataverse recurring bulk-delete jobs** against a status-plus-date query; because Review, Grant
and Payment hang off Application by cascade, deleting the Application removes the whole case.

| Data / outcome | Trigger | Retention | Then |
|---|---|---|---|
| Successful grant — full record incl. health free-text | Status = Grant Paid; from **final payment date** | **6 years** | Delete full record |
| Unsuccessful application | Status = Rejected; from decision date | **12 months** | Delete full record |
| Withdrawn / incomplete | Status = Withdrawn / Incomplete; from last contact | **6 months** | Delete full record |
| Monitoring & evaluation (pseudonymised) | Follows its parent grant record | Same as record | Delete with record |
| Signed acceptance PDF | Attached to the grant record | 6 years (with record) | Delete with record |
| Financial record (name, amount, date) — QuickBooks | Status = Grant Paid | 6 years | Per finance policy |
| Irreversibly anonymised statistics | No identifiers, not linkable | **Indefinite** | Retain |
| Error Log (operational, non-personal) | — | ~12 months **[TBC]** | Separate from the personal-data schedule |

Supporting controls: a residual **Retention & Erasure helper flow** for what the native job
cannot reach (DocuSign envelope purge, the QuickBooks carve-out, on-demand erasure); **Purview
basic time-based retention labels** as a backstop on the Application table and the signed-PDF
library; deletion logging with **no personal data** in it.

⚠️ **Open:** whether the health free-text may be redacted earlier than six years is a DPO
minimisation decision. The design allows it as configuration (DPIA R4, SDD OQ-006).

---

## Key Dates and Timelines

| Obligation | Timeline |
|---|---|
| Retention enforcement run | At least **monthly** (SDD NFR-010) |
| Acceptance signature reminders | **3 days** and **7 days** after issue (FR-043) |
| Acceptance escalation to the process owner | **14 days** unsigned (FR-044) |
| Impact report due | **One month after the holiday end date** |
| Panel cycle | **Monthly**; up to three attempts per application |
| Record retention | Per the schedule above — 6 years / 12 months / 6 months by outcome |
| Personal-data breach notification to the ICO | 72 hours of becoming aware (statutory; no project-specific procedure is recorded) |
| SAR turnaround | ⚠️ **Not specified.** Statutory default is one month; **no internal SLA exists** (SDD OQ-023, NFR-025) |
| Role-membership review cadence | ⚠️ **[TBC]** — quarterly or per panel round is the working assumption (DPIA §7) |
