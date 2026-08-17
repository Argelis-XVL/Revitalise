# Solution Design Document — Application Form Field Corrections

**Feature Slug:** `revitalise-form-field-corrections`
**Requested By:** Xander Lykopoulos (reviewer / process owner side), from a field-by-field
comparison of the Dataverse Application and Applicant forms against the live WordPress form
**Date:** 2026-08-16
**Revision:** 1.4 — D-4 corrected after a live re-check of the form (see *Decisions taken at the
plan gate* below); OQ-037 partially answered
**Status:** DRAFT
**Parent SDD:** `docs/plans/revitalise-grant-automation-plan.md` — this document does not replace it.
It adds requirements FR-056 to FR-064, NFR-026 to NFR-028, US-016 to US-019 and OQ-031 to OQ-039,
continuing that document's numbering so no identifier is reused.

**Model tier:** `strategic` — escalated from `standard` under `config/models.yml` →
`agents.plan-agent.escalate_to_strategic_when`, first condition ("feature touches regulated data").
Two of the seven work items change a column's UK GDPR classification from ordinary personal data to
special category. That is expensive to get wrong and expensive to reverse once records exist.

---

## Decisions taken at the plan gate — 2026-08-16

Recorded here because six of the seven change the shape of the work, and one of them closes a
question the parent SDD has carried since the architecture gate.

| # | Decision | Effect |
|---|---|---|
| **D-1** | **Secure the employment column.** Released to the process owner and the service identity only, via `REV_TrusteeRestricted`. *Superseded in part by D-6 — originally covered both reclassified columns.* | Adds one `IsSecured=1` attribute and one `FieldPermission` entry. |
| **D-2** | **No data exists in DEV.** | Settles **OQ-031**. Every delete-and-recreate and every option-set renumber in this pass is safe. This is the window; it closes at the first real application. |
| **D-3** | **The live form already asks the employment question as five options.** | Settles **OQ-033**, and removes the external dependency on Alex for W2. Also means `form-validation-spec.md` §4 is stale — see **OQ-037**. |
| **D-4** | **CORRECTED at revision 1.4.** Care-hours bands are `9 hours or less` / `10 – 19 hours` / `20 – 34 hours` / **`35 – 59 hours`** / `50+`. The band-four value agreed at revision 1.0 (`35 - 50 hours`) was itself the misreading — three independent re-fetches of the live form on 2026-08-16, one asking specifically for the raw radio-input markup, all returned "35 – 59 hours", and the reviewer confirmed this directly against the page. | Settles **OQ-034** a second time, in the opposite direction from the first pass. **Reopens V-10**: bands four and five overlap at 50–59 hours, exactly as the original validation spec flagged and as this pass had believed it was closing. See §8. |
| **D-5** | **The removal is the three carer columns only.** | Settles **OQ-035**. `rev_supportrecipientname`, `rev_providerpreference`, `rev_applicant.rev_title` and `rev_privacynoticeacceptedon` stay, and remain open as M-10 items. |
| **D-6** | **`rev_exceptionalcircumstance` stays trustee-visible — do not secure it.** The trustees have a reason to see it: they cannot judge a request for exceptional funding without knowing what the exceptional circumstance is. | Settles **OQ-038** by removing the gap rather than filling it. Reverses the exceptional-circumstance half of D-1. Raises **OQ-039** (DPIA/RoPA must record it). §7.4 shows this is the solution's *existing* rule, not an exception to it. |
| **D-7** | **Rename the employment column to `rev_employmentstatus`** ("Employment Status") as part of its recreate. | Settles **OQ-032**. The intake payload field becomes `employment_status`. Free now only because D-2's window is empty. |

---

## 1. Business Context

The grant application form is built and hosted on WordPress (Gravity Forms) by Alex. The Dataverse
schema that receives it was built here. Nobody built both. Every difference between them is a
question the charity asks an applicant and then loses, a question it stores an answer to but never
asks, or an answer stored in a shape that cannot hold what was asked.

`docs/development/revitalise-grant-automation-form-validation-spec.md` §9 already lists ten such
gaps (M-01 to M-10) from a documentary comparison. This pass is different: it comes from the
reviewer opening both forms side by side and reading them. That produced seven findings, five of
which are new or contradict what the repository currently believes.

Two of the seven are **regressions introduced earlier today** in commit `1faf2b4`, made in good
faith from a visual check of the live form that read the wrong export column:

- `rev_exceptionalcircumstance` was converted from a Choice to a Boolean on the stated grounds
  that the live form asks Yes/No. It does not. Raw export column **128** is the Yes/No question
  (*"I'd like to make an exceptional funding request"*, already held by
  `rev_exceptionalfundingrequested`); column **129** is a separate four-option radio. The two
  columns are adjacent in the export, which is how they came to be conflated.
- `rev_carehoursperweek` was added as an integer against a question the form asks as five bands.
  It can never be populated as built.

The remaining five are gaps, not regressions: two questions the form asks and nothing stores, one
question whose answer shape loses the distinction that matters most, and three columns that exist,
appear on the form, are secured, and will always be empty.

None of this is visible to anyone until an application arrives. That is the argument for doing it
now, before go-live, rather than discovering it from a real applicant's record. **D-2 confirms the
window is open and empty.**

---

## 2. Objectives

- Make every column on the Application and Applicant tables correspond to a question the live form
  actually asks, in the shape it actually asks it.
- Undo the two corrections made today that went the wrong way, and record why, so the same
  column-off-by-one is not made a third time.
- Capture the three answers the form collects that currently have no destination and that bear
  directly on need: how the applicant wants to be contacted, why someone is acting on their behalf,
  and how much care they provide each week.
- Preserve the distinction between "cannot work because of disability or caring" and "not working"
  — the single answer in this pass with the most direct bearing on a needs-based funding decision.
- Stop the record asserting it holds information it can never receive.
- Do all of it before any real application exists, because every change here is destructive after
  that point.

---

## 3. Scope

### In Scope

| # | Work item | Nature |
|---|---|---|
| **W1** | `rev_application.rev_exceptionalcircumstance` — revert Boolean → Choice; restore the option set with the four real values; **trustee-visible, not secured** (D-6) | Regression fix + reclassification |
| **W2** | `rev_application.rev_currentlyworking` → **`rev_employmentstatus`** (D-7) — Boolean → Choice with the five values the live form already sends (D-3); **secure it** (D-1) | Regression fix + reclassification + rename |
| **W3** | `rev_applicant.rev_preferredcontactmethod` — new multi-select Choice (Email / Phone / Post) | New column, closes part of M-09 |
| **W4** | `rev_application.rev_consentexplanation` — new secured multi-line text | New column, closes part of M-09 |
| **W5** | `rev_application.rev_carehoursperweek` — integer → Choice with the five bands at D-4 | Regression fix |
| **W6** | Remove `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` — those three only (D-5) | Removal, closes part of M-10 |
| **W7** | Cross-cutting: option-list drift must fail loudly, not silently | New rule (FR-064) |

W2 is reclassified from "improvement" to "regression fix" by **D-3**: the live form has been asking
five options, and the Boolean was already wrong when it was written, not merely coarse.

Each work item carries its full change surface — entity XML, option sets, `Solution.xml` root
components, field security profile, `scripts/verify-field-security-coverage.py`, model-driven forms,
the intake flow's trigger schema and mapping, and the Pester suites. The per-item surface is in
**Appendix B**.

### Out of Scope

- **`rev_narrativeraw`** — checked as part of the same investigation and found correct. Gravity
  Forms field 88 → raw export column 133 → `rev_narrativeraw`, `ntext`, 4000 characters, secured.
  No change. The live form's **325-character cap** on that box is a real problem — it is the most
  important qualitative input to the decision and the most tightly limited field on the form — but
  it is already raised as **V-09** in the change request to Alex and stays there.
- **`rev_needscaresupportpersonally` / `rev_caresupportdescription`** (form page 8, export columns
  66–67) and **`rev_significantcarecosts` / `rev_carecostsexplanation`** (page 12, columns 110–111)
  — both pairs confirmed correct against the live form. No change.
- The other seven gaps in the validation spec's §9 — **M-01** (condition profile: ten functional
  areas against eight condition types) is a larger and more consequential disagreement than
  anything in this pass and needs its own decision, not a side effect of this one.
- The four remaining M-10 orphans, per **D-5**.
- Everything downstream of intake: scoring, anonymisation, trustee portal, acceptance. **D-6
  removes the one exception the previous revision carried here.**

---

## 4. Functional Requirements

### A. Exceptional circumstance (W1)

| ID | Requirement | Priority |
|---|---|---|
| FR-056 | The system SHALL record the applicant's exceptional circumstance as exactly one of **Palliative care**, **Carer breakdown or urgent need**, **Severe financial hardship**, or **Other (please specify)** WHEN an application carrying an exceptional funding request is submitted, SO THAT the reason for an above-normal request is on the record rather than only the fact of one. | High |
| FR-057 | The system SHALL retain the applicant's own wording of the circumstance WHEN the selected value is "Other (please specify)", SO THAT circumstances outside the four categories are not lost. | High |

### B. Employment status (W2)

| ID | Requirement | Priority |
|---|---|---|
| FR-058 | The system SHALL record the applicant's employment status as exactly one of **Yes, full-time**, **Yes, part-time**, **No, unable to work due to disability/health/caring responsibilities**, **No, retired**, or **No, other reason** WHEN the applicant answers the employment question, SO THAT an inability to work caused by disability or caring is distinguishable from retirement and from choice, which is the distinction a needs-based grant decision turns on. | High |
| ~~FR-059~~ | ~~Legacy Yes/No handling.~~ **Withdrawn at revision 1.1.** D-3 establishes that the live form already sends the five values, so there is no legacy value stream to handle. The general case is covered by FR-064, which is strictly stronger. | — |

### C. Preferred contact method (W3)

| ID | Requirement | Priority |
|---|---|---|
| FR-060 | The system SHALL record every contact method the applicant selects — **Email**, **Phone**, **Post**, one or more — WHEN an application is submitted, SO THAT correspondence and grant offers reach applicants by a route they can actually use. | High |

### D. Consent explanation (W4)

| ID | Requirement | Priority |
|---|---|---|
| FR-061 | The system SHALL retain the explanation an applicant gives alongside the applicant-consent declaration WHEN one is given, SO THAT the basis on which a third party is acting for the applicant is on the record and not only in the mind of whoever read the submission. | Medium |

### E. Hours of care provided (W5)

| ID | Requirement | Priority |
|---|---|---|
| FR-062 | The system SHALL record the hours of care the applicant provides each week as exactly one of the five bands the form offers, WHEN the applicant answers that question, SO THAT the caring load is captured in the form it is actually asked in rather than discarded for being unstorable. | High |

### F. Removal of columns with no source (W6)

| ID | Requirement | Priority |
|---|---|---|
| FR-063 | The system SHALL NOT hold columns for whether a carer travels with the applicant, that carer's name, or the support that carer provides, UNTIL the application form asks those questions, SO THAT the schema does not assert it holds information it can never receive and staff do not read an empty field as a "no". | Medium |

### G. Option-list drift (W7)

| ID | Requirement | Priority |
|---|---|---|
| FR-064 | The system SHALL leave a column empty and record the mismatch against the application WHEN an incoming answer does not match any value in that column's option list, and SHALL NOT map it to a nearest value, SO THAT divergence between the website form and the system of record surfaces as a visible exception rather than as quietly wrong data. | High |

FR-064 is the requirement this whole pass argues for. Every finding here existed for weeks without
anything noticing, because nothing was watching for it. **D-3 makes the point sharper than the
original draft did**: the form changed to five options at some point and the repository never found
out. FR-064 is what would have told us.

**Matching is normalised, not literal.** The comparison SHALL trim surrounding whitespace, collapse
internal runs of whitespace, and treat hyphen, en-dash and em-dash as equivalent before matching.
The care-hours bands are the live example — this document has already seen them written as
`10 – 19 hours` and `10- 19 hours` in two different sources, and a literal comparison would reject
every submission while reporting a drift that does not exist. Case is also normalised. Nothing else
is: a value that differs by a word is a real mismatch and must be reported as one.

---

## 5. Non-Functional Requirements

| ID | Requirement | Category |
|---|---|---|
| NFR-026 | Every column added or reshaped by this pass SHALL be classified against UK GDPR Art. 6 / Art. 9 in §7.1 **before** it is built. Classification determines what must be *recorded*; it does not by itself determine what must be *secured* — securing is decided per column against necessity, under the rule at §7.4. | Compliance |
| NFR-027 | Where an Art. 9 special-category column is deliberately released to trustees, the necessity argument SHALL be recorded in this SDD, in the column's own schema description, and in the DPIA and RoPA, and the free-text elaboration behind that column SHALL remain secured. Per **D-6** this applies to `rev_exceptionalcircumstance`. | Compliance |
| NFR-028 | No option-set value SHALL be renumbered or removed once any application record references it. All option-set trimming and renumbering in this pass SHALL complete before the first real application is created. **D-2 confirms this is currently satisfiable.** | Compliance |

*(Accessibility NFR withdrawn at revision 1.2. D-3 and D-4 established that no public-form change
is required by this pass, so it had no subject. If OQ-037 surfaces a form change, it returns.)*

---

## 6. User Stories

### US-016: The reason for an exceptional request survives to the decision

**As a** trustee, **I want** to see which category of exceptional circumstance an applicant claims,
**so that** I can weigh a palliative-care request differently from a financial-hardship one instead
of being asked to approve an above-normal amount with no reason attached to it.

**Acceptance Criteria:**
- Given an application submitted with "Palliative care" selected, when the application record is
  created, then the exceptional circumstance column holds the value "Palliative care".
- Given an application submitted with "Other (please specify)" selected and free text supplied,
  when the record is created, then the selection is stored and the applicant's own wording is
  stored in the secured `rev_otherexceptionalcircumstance`.
- Given an application where the applicant made no exceptional funding request, when the record is
  created, then the exceptional circumstance column is empty and is distinguishable from any
  selected value.
- Given a trustee opens the application, when the record renders, then the exceptional circumstance
  **category is visible** and the free-text elaboration behind it is **not** (D-6, §7.4).

### US-017: An applicant who cannot work because of their disability is not recorded as simply "not working"

**As a** process owner assessing need, **I want** the employment answer to distinguish inability to
work from retirement and from choice, **so that** an applicant whose disability prevents them
working is not assessed identically to one who has retired comfortably.

**Acceptance Criteria:**
- Given an applicant selects "No, unable to work due to disability/health/caring responsibilities",
  when the record is created, then that exact value is stored.
- Given a submission arrives carrying a value outside the five, when the record is created, then
  the employment status is empty and the mismatch is recorded against the application (FR-064).
- Given the employment status is empty for either reason, when a staff member views the record,
  then it reads as unanswered and not as "No".
- Given a trustee opens the application, when the record renders, then the employment status is not
  shown to them, in any surface (D-1).

### US-018: An applicant who asked to be contacted by post is contacted by post

**As an** applicant without reliable email, **I want** the charity to hold the fact that I asked to
be contacted by post, **so that** the grant offer arrives somewhere I can read it.

**Acceptance Criteria:**
- Given an applicant ticks Post only, when the record is created, then the preferred contact method
  holds Post and the applicant record has no email address, and neither is treated as an error.
- Given an applicant ticks both Email and Post, when the record is created, then both values are
  stored.

### US-019: The caring load is on the record

**As a** process owner, **I want** the hours of care an applicant provides each week to be stored,
**so that** the thing the charity exists to relieve is visible in the record rather than only in
the applicant's narrative.

**Acceptance Criteria:**
- Given an applicant selects "20 - 34 hours", when the record is created, then that band is stored.
- Given an applicant selects a band, when the record is viewed, then the band label is shown, not a
  number.

---

## 7. Compliance & Regulatory Considerations

### 7.0 What is actually new here

Five of the seven work items are shape corrections to data already classified in the parent SDD
§7.1 and already covered by its lawful bases in §7.2. Those need no new analysis and get none.

**Two things in this pass change a classification.** D-1 and D-6 settle how each is handled, and
they land differently. They are the reason this document escalated to strategic tier.

### 7.1 Data classification of every column touched (satisfies C-DOM-001 at plan level)

| Column | Before this pass | After this pass | Secured? |
|---|---|---|---|
| `rev_application.rev_exceptionalcircumstance` | Personal (Art. 6) — a Boolean "is there an exceptional circumstance" discloses nothing in itself | **Special category (Art. 9)** — "Palliative care" is health data about the applicant or someone they care for | **No — D-6.** Trustee-visible on necessity, §7.4. Its free-text elaborations stay secured |
| Employment status (`rev_currentlyworking` as reshaped) | Personal (Art. 6) — a Boolean "are you working" is ordinary financial circumstance, and its schema description says so | **Special category (Art. 9)** — "No, unable to work due to disability/health/caring responsibilities" is a disclosure of disability or health status | **Yes — D-1** |
| `rev_applicant.rev_preferredcontactmethod` (new) | — | Personal (Art. 6). A contact preference. Not special category, and it should not be secured — the people who need to know how to write to an applicant are exactly the people who correspond with them | No |
| `rev_application.rev_consentexplanation` (new) | — | **Special category (Art. 9)** — an explanation of why someone else is completing a form for an applicant will routinely name a health reason, on the same reasoning already applied to `rev_caresupportdescription` and `rev_otherconditionraw` | **Yes, from creation** — free text, §7.4 |
| `rev_application.rev_carehoursperweek` (reshaped) | Personal (Art. 6), not secured | Unchanged — a band of hours is a circumstance fact and exactly the fact trustees need | No |
| `rev_travellingwithcarer`, `rev_carername`, `rev_carersupport` (removed) | Personal / special category, two of the three secured | **Removed** | n/a |

The two classification changes are consequences of the reviewer's findings, not choices this
document makes. A Boolean that says "yes, something exceptional" is not health data. A value that
says "palliative care" is. The same column, reshaped, crosses the line. **What follows from the
classification is a separate decision, and §7.4 is where it is taken.**

### 7.2 Lawful basis (satisfies C-DOM-002)

No new lawful basis is required. Every column here sits inside a grouping already covered by the
parent SDD §7.2, taken from Revitalise's own Privacy Notice of 20 February 2026:

| Column | Art. 6 basis | Art. 9 condition | Grouping in parent §7.2 |
|---|---|---|---|
| `rev_exceptionalcircumstance` | Necessary to assess and administer the grant | Art. 9(2)(b) social protection; 9(2)(h) health and social care | Application |
| Employment status | Necessary to assess and administer the grant | Art. 9(2)(b); 9(2)(h) | Application |
| `rev_preferredcontactmethod` | Necessary to administer the grant | n/a | Applicant (identity, contact) |
| `rev_consentexplanation` | Necessary to administer the application | Art. 9(2)(b); 9(2)(h) | Application / Helper acting for an applicant |
| `rev_carehoursperweek` | Necessary to assess the grant | n/a | Application |

### 7.3 Data minimisation — this pass moves in both directions, and that is deliberate

**Added:** three answers the form already collects and the applicant already gives. Storing an
answer already being collected is not an increase in processing; discarding it while continuing to
ask for it is the worse position, because the applicant has already borne the intrusion and the
charity gets none of the benefit. Each of the three has a stated purpose above: FR-060 determines
how the offer is delivered, FR-061 evidences third-party authority, FR-062 measures the caring load
the grant exists to relieve.

**Removed:** three columns holding nothing, two of them secured. Deleting them is a small
minimisation gain and a larger honesty gain — `rev_carername` currently appears on the form,
carries a `REV_TrusteeRestricted` entry, and will always be empty.

**Tightened:** one column moves behind field-level security that was not behind it before (D-1).

### 7.4 The securing rule this solution actually implements — and why D-6 follows it

The previous revision of this document asserted that securing `rev_exceptionalcircumstance` was
"the consistent position". **That was wrong, and the correction matters because the architect will
carry this rationale forward.** Reading `REV_TrusteeRestricted`'s real `AttributeName` entries — as
opposed to the columns merely mentioned in its comments — the implemented rule is:

> **Categorical answers are trustee-visible. Identity and free text are not.**

The evidence is unambiguous and covers thirty-eight secured columns against every categorical
answer in the schema:

| Trustee-visible today (not secured) | Secured today |
|---|---|
| `rev_conditionprofile`, `rev_supportrecipientconditionprofile` — **both special category** | `rev_otherconditionraw`, `rev_supportrecipientotherconditionraw` — the free text behind them |
| `rev_needscaresupportpersonally`, `rev_careprovidedtype`, `rev_carehoursperweek` | `rev_caresupportdescription`, `rev_othercareprovidedtype`, `rev_careprovidedexample` |
| `rev_significantcarecosts`, `rev_savingsover6000`, `rev_incomeband` | `rev_carecostsexplanation`, `rev_unabletofundexplanation` |
| `rev_exceptionalfundingrequested`, `rev_breaklocation` | `rev_exceptionalfundingdetail`, `rev_otherexceptionalcircumstance` |

The pattern holds in every row: the charity's trustees are given the *category* of a person's
disability, care need, financial position and requested break, and are given none of the *words* in
which that person described it, and none of their identity. `rev_conditionprofile` is the closest
analogue to `rev_exceptionalcircumstance` — Art. 9 health data, held as a category, trustee-visible
by design, with its "other" free text secured. Its schema description says so in terms.

**D-6 puts `rev_exceptionalcircumstance` where that rule already puts it.** It is not an exception
carved out for convenience; securing it would have been the exception. The necessity argument is
the same one the solution already accepted for `rev_breaklocation` — a trustee cannot judge a
request for a break without knowing where the break is, and cannot judge a request for
**exceptional** funding without knowing what the exceptional circumstance is.

Two obligations attach, both in NFR-027:

1. `rev_otherexceptionalcircumstance` and `rev_exceptionalfundingdetail` — the free text behind the
   category — **stay secured**. The rule only works because both halves of it hold.
2. The DPIA and RoPA must record that trustees process this Art. 9 category. They already record it
   for the condition profiles, so this is an amendment to an existing entry rather than a new
   disclosure — but it is not automatic. **OQ-039.**

**The employment column is the genuine exception, and D-1 keeps it secured.** Under the rule above
a category would be visible, and its financial neighbours (`rev_incomeband`, `rev_savingsover6000`,
`rev_significantcarecosts`) all are. The reason it differs is that one of its five values —
"No, unable to work due to disability/health/caring responsibilities" — is a direct disability
disclosure rather than a financial fact, and nothing in the trustee's task requires it. The nearest
precedent is `rev_receivesbenefits`, which is secured for the same kind of reason. This asymmetry
is deliberate and should be written into the column's own schema description so the next reader
does not "fix" it.

### 7.5 Consequences for the DPO decisions already open

- **OQ-004** (is column security an acceptable trustee control?) now covers one more column, not
  two. D-6 reduces this pass's reliance on that answer.
- **OQ-006** (six-year retention of health free-text) now covers `rev_consentexplanation`.
- Neither is re-opened by this pass. Both have their surface changed by it, and the DPO should be
  told so rather than discovering it later.

### 7.6 Universal controls

`skills/compliance-checklist.md` §1 controls are unchanged by this pass and are inherited from the
parent SDD §7.9. Nothing here introduces a new integration, a new data subject category, a new
processor, or a new export route.

---

## 8. Assumptions & Dependencies

### Settled by D-2 — the window is open

**No real application data exists in any environment.** Every type change in this pass is a
delete-and-recreate of a live Dataverse attribute (Dataverse has no in-place Choice↔Boolean or
int↔Choice conversion — proven in this repository twice today), and every option-set trim
renumbers values. Both are safe now and destructive the moment a record references them. D-2
confirms nothing is at risk. **This assumption expires at the first real application**, and the
work in this pass should be sequenced before anything that creates one.

### Platform

- Delete-and-recreate is the only route for W1, W2 and W5. This is established, not assumed: the
  same operation was performed today for `rev_exceptionalcircumstance` and `rev_helperrelationship`
  and is recorded in `logs/routing.log` at 20:31 and in the Entity.xml comment at line 1508.
- **Destructive deployment steps require an explicit human go-ahead.** Attribute deletion has been
  declined twice this session by the auto-mode safety classifier, correctly. This pass contains six
  attribute deletions (three recreates, three removals) and will stop at the same point.
- `scripts/verify-field-security-coverage.py` checks in both directions — every `IsSecured=1`
  column must appear in `REV_TrusteeRestricted` and nothing else should. D-1's addition, D-6's
  deliberate *non*-addition, `rev_consentexplanation`, and W6's two removals all have to clear it.
- There is a **pre-existing open maker-portal item** from today's deployment: `rev_breaktype` has
  four orphaned values and `rev_applicanttype` one, awaiting manual removal via Settings → option
  set → remove option. That work should be bundled into the same maker-portal session as this
  pass's option-set changes rather than scheduled separately.

### External — the WordPress form

**D-3 removes this dependency for W2.** The live form already asks the employment question as five
options, so no form change is required there and no new item joins the V-01 … V-11 change request
to Alex on that account.

**D-4, corrected, does not remove the dependency for W5 — it restores it.** The live form's actual
fourth band is `35 – 59 hours`, which overlaps the fifth band, `50+`, across ten whole hours (50
through 59). This is not new: it is **V-10** from the original validation spec, unchanged and
unresolved. Revision 1.0 of this SDD believed it was closing V-10 by correcting the band to
`35 - 50 hours`; that correction was itself the misreading, and the overlap the live form actually
sends is real.

**This pass still builds the option set as the five values the form sends, overlap included.**
Re-inventing a cleaner band to avoid the overlap would repeat, in miniature, the exact mistake this
whole SDD exists to fix: choosing what a value "should" be instead of recording what the form
actually asks. FR-064's own principle — store what arrives, flag what doesn't fit, never guess a
nearest value — applies to the charity's own form copy as much as to an applicant's answer. **V-10
stays open** and belongs in the same change request to Alex as V-01 … V-11; it is not resolved by
this pass and this pass does not claim otherwise.

### Conflict with an approved requirement

**Parent SDD FR-003** requires the form to "present carer questions only when the applicant has
indicated they are travelling with a carer". W6 removes the columns those questions would write to.
This is not a reason to keep the columns — they have been empty since they were created and the
form has never asked — but FR-003 is now a requirement with no implementation and no data
destination. D-5 confirms the removal goes ahead, so the parent SDD must record that FR-003 is
unimplemented and say why. That is a documentation action on the parent, carried in this pass's
change surface.

---

## 9. Open Questions

### Resolved at the plan gate

| # | Question | Resolution |
|---|---|---|
| OQ-031 | Does any environment hold application records with values in the columns being deleted and recreated? | ✅ **No — D-2.** No data in DEV. All destructive operations are safe. |
| OQ-033 | Will the live form ask the employment question as five options, and when? | ✅ **It already does — D-3.** No form change needed; W2 becomes a regression fix. |
| OQ-034 | Confirm the care-hours band labels. | ✅ **D-4, corrected at revision 1.4** — `9 hours or less` / `10 – 19 hours` / `20 – 34 hours` / `35 – 59 hours` / `50+`. Revision 1.0's "35 - 50" reading was the error, not the fix; **V-10's band overlap is real and stays open**, see §8. |
| OQ-035 | Does the removal extend beyond the three carer columns? | ✅ **No — D-5.** The other four M-10 orphans stay and remain open as M-10. |
| OQ-032 | Should the employment column come back as `rev_employmentstatus`? | ✅ **Yes — D-7.** Renamed on recreate; intake payload field becomes `employment_status`. |
| OQ-036 | Do the two reclassified columns become invisible to trustees? | ✅ **Split — D-1 and D-6.** Employment: yes, secured. Exceptional circumstance: no, trustee-visible. |
| OQ-038 | What does a trustee see in place of the exceptional circumstance? | ✅ **The circumstance itself — D-6.** The gap is removed rather than filled. §7.4 shows this follows the solution's existing rule rather than excepting it. |

### Partially answered — a targeted re-check, not the full pass OQ-037 asks for

A live re-fetch of the form (2026-08-16, this session) checked every field this SDD's seven work
items touch, plus the disability, helper-routing, break-date, date-of-birth, referee,
emergency-contact and provider-preference questions, against both the export headers and the
current `Entity.xml` files. Results:

- **Confirmed correct, unchanged:** the disability Yes/No question and its Equality Act 2010
  definition, the helper-routing Yes/No question, both "Brief confirmation" help texts, the single
  free-text "Provisional date" field (reconfirms **V-04**), the absence of a date-of-birth question
  (reconfirms **M-10**), and the absence of any referee, emergency-contact or provider-preference
  question on the live form (these three exist on `rev_application` for a later stage of the
  process — Automation #3's acceptance/signature routing per parent FR-042/FR-051 — not because the
  intake form should be asking and isn't).
- **Confirmed stale, not yet fixed:** `form-validation-spec.md` §4's Page 10 table (GF fields
  128–131) still reads "nothing here is stored", but `rev_careprovidedtype`,
  `rev_othercareprovidedtype`, `rev_careprovidedexample` and `rev_carehoursperweek` were added
  earlier today and are mapped in the intake flow. The same table's Pages 15–20 section still marks
  GF field 107 ("How did you hear about us") as "not stored, §9", but `rev_hearaboutus` /
  `rev_otherhearaboutus` were also added today and mapped. Both are documentation debt from the same
  day's earlier commit, not schema defects — but they are exactly the kind of thing OQ-037 exists to
  catch, and mechanical (spec text vs. code), so worth fixing on sight rather than waiting.
- **What this re-check did not do:** work through §4's other ~65 rows line by line, or re-verify §6's
  remaining option lists (condition profile, income bands, the two wellbeing scales, break type,
  applicant type) against the live page. Those are the highest-consequence rows in the document —
  **M-01** and **M-02** in particular — and this pass had no reason to touch them. OQ-037's original
  recommendation, a full pass before the architect relies on §4/§6, still stands for those.

### Still open

| # | Question | Owner | Due |
|---|---|---|---|
| OQ-037 | **Full re-verification of `form-validation-spec.md` §4 and §6 against the live form — the two Page 10 / Page 107 rows above are now fixed as a side effect of this session, but the highest-value rows (condition profile, income bands, both wellbeing scales, break type, applicant type) are untouched.** *Recommendation: a targeted pass over just those five option lists, since everything else in §4/§6 that this session could reach checked out clean.* | Reviewer / Alex | **Before architecture — for the untouched rows only; the two fixed rows no longer block it** |
| OQ-039 | **Who amends the DPIA and RoPA to record that trustees process the exceptional-circumstance category, and when?** D-6 makes an Art. 9 column trustee-visible. Both documents already record the same arrangement for `rev_conditionprofile`, so this is an amendment to an existing entry and not a new disclosure — but NFR-027 requires it to be written down, not inferred. | DPO / Emily | Before go-live; with the DPIA conclusion at OQ-030 |

---

## 10. Effort Estimate

**Size:** M
**Range:** 4–7 days, most likely **6**
**Elapsed tracks effort.** The original draft flagged that W2 and W5 could not be verified end to
end until Alex changed the form. D-3 and D-4 removed that dependency entirely.

### How the estimate is built

| Work | Base |
|---|---|
| Schema: 3 delete-and-recreate conversions, 3 removals, 2 new columns | 1.0 day |
| Option sets: 1 restored, 3 new, plus the pre-existing `rev_breaktype`/`rev_applicanttype` orphan cleanup | 0.5 day |
| Field security: 2 additions (D-1, `rev_consentexplanation`), 2 removals, `verify-field-security-coverage.py` clean in both directions including D-6's deliberate absence | 0.4 day |
| Model-driven forms on two entities | 0.25 day |
| Intake flow: trigger schema, mappings, FR-064 drift detection with normalised matching | 1.0 day |
| Pester suites: schema assertions, intake contract, drift cases, hardcoded-count updates, trustee-visibility assertions in both directions (D-1 hidden, D-6 visible) | 0.75 day |
| Deployment, including the human-gated destructive steps and live verification | 0.75 day |
| Documentation: TAD delta, Dev Summary, validation-spec §9, parent SDD FR-003 note, the §7.4 rule written into two schema descriptions | 0.5 day |
| **Base subtotal** | **5.15 days** |

Multipliers from `skills/how-to-estimate-effort.md`: strict regulatory compliance **1.25×** — two
columns cross into Art. 9, one is secured and one is deliberately not, and both decisions have to
be evidenced. The high-security-classification multiplier is *not* applied on top: it is the same
fact counted twice, and this team performed exactly this operation on exactly this schema earlier
today, which is the strongest available argument against padding it further.

5.15 × 1.25 ≈ **6.4 days → M**, at the upper half of the band.

The estimate has now survived two rounds of gate decisions without moving outside the noise. That
is worth stating: the decisions clarified the work substantially and changed its size hardly at all.

### What would still change it

- **OQ-037 finding further drift** — unknown, and the reason it is due before architecture rather
  than during. If §4 has more wrong rows, they arrive as new work items, not as re-estimates. This
  is now the only open item that can move the number.

---

## Appendix A — Traceability Matrix (FR → US)

```
FR-056 → US-016 AC-1, AC-2, AC-3
FR-057 → US-016 AC-2
FR-058 → US-017 AC-1
FR-060 → US-018 AC-1, AC-2
FR-061 → (no user story — a record-keeping requirement, verified by schema and intake tests)
FR-062 → US-019 AC-1, AC-2
FR-063 → (no user story — a removal, verified by absence)
FR-064 → US-017 AC-2
NFR-026 → §7.1                 (classification is evidenced by the table, not by a test)
NFR-027 → US-016 AC-4          (D-6 is testable in both directions: category readable by a
                                trustee role, free text not)
NFR-028 → US-017 AC-4          (D-1 is testable: a trustee-role read returns no value)
FR-059 → WITHDRAWN at revision 1.1, superseded by FR-064
```

## Appendix B — Change surface per work item

For the architect. Every row is a file or artefact that changes; none of these are optional.

| Work item | Entity XML | Option set | Solution.xml root components | Field security | Forms | Intake flow | Tests | Live Dataverse |
|---|---|---|---|---|---|---|---|---|
| **W1** exceptional circumstance | `bit` → `picklist`, restore `IsGlobal` + `OptionSetName`, **`IsSecured=0`**; rewrite the CORRECTED-2026-08-16 comment to record what actually happened; write the §7.4 necessity argument into the description | **Restore** `rev_exceptionalcircumstance.xml` with 4 values (was 7 placeholders — closes M-07 for this set) | Re-add the OptionSet root component | **None — D-6.** Must *not* appear in `REV_TrusteeRestricted`; `verify-field-security-coverage.py` must stay clean with it absent | Application main form: control class changes with the type | Trigger schema `string`; normalised label → value mapping | `EnsureSchema`, option-set counts, field-security coverage, a trustee-role read test asserting the category **is** readable and `rev_otherexceptionalcircumstance` is **not** | **Delete + recreate attribute** |
| **W2** employment status | `bit` → `picklist`, **`IsSecured=1`**, **renamed `rev_currentlyworking` → `rev_employmentstatus`, display name "Employment Status" (D-7)**; write the §7.4 asymmetry into the description | **New** `rev_employmentstatus.xml`, 5 values per FR-058 | Add — and **remove** the old attribute's root component | **Add** `FieldPermission` to `REV_TrusteeRestricted` (D-1) | Application main form: the old control is removed, not relabelled | Trigger schema + mapping: payload field `currently_working` → **`employment_status`**; normalised mapping | `EnsureSchema`, `IntakeContract` (payload field name changes in every assertion), field-security coverage, trustee-role read test asserting no value | **Delete + recreate attribute under the new name** |
| **W3** preferred contact method | **New** attribute on **`rev_applicant`**, `multiselectpicklist` | **New** `rev_contactmethod.xml`, 3 values | Add attribute + option set | Not secured (§7.1) | **Applicant** main form, beside email/phone | Trigger schema accepts an array; export columns 26/27/28 are three separate checkbox columns and must be combined | `EnsureSchema`, `IntakeContract` | Create attribute |
| **W4** consent explanation | **New** `ntext`, textarea, 2000, `IsSecured=1` | — | Add attribute | **Add** `FieldPermission` — free text, §7.4 | Application main form, beside `rev_applicantconsent` / `…consentdate` | Trigger schema + mapping (export column 49) | `EnsureSchema`, field-security coverage | Create attribute |
| **W5** care hours band | `int` → `picklist`; drop `MaxValue 168` | **New** `rev_carehoursband.xml`, 5 values per D-4 (corrected) — `35 – 59 hours` and `50+` overlap on the form itself; the option set stores both as sent and does not silently resolve the overlap | Add | Unchanged, not secured | Application main form | Trigger schema `string`; normalised label → value mapping (dash normalisation matters here specifically) | `EnsureSchema`, drift cases covering dash and spacing variants | **Delete + recreate attribute** |
| **W6** carer columns | **Remove** 3 attributes | — | Remove 3 attribute root components | **Remove** 2 `FieldPermission` entries (`rev_carername`, `rev_carersupport`) | Remove 3 controls from the Application main form | Remove 3 fields from the trigger schema and 3 mappings | Update hardcoded counts in `EnsureSchema` and `IntakeContract`; field-security coverage | **Delete 3 attributes** |
| **W7** drift detection | — | — | — | — | — | Per-field validation against the option list with normalised matching; mismatch → leave empty + record note | New drift cases per converted column | — |

**Documentation actions carried by this pass:** `form-validation-spec.md` §9 (close M-07 for the
exceptional-circumstance set, close the M-09 rows for preferred contact method, the consent
explanation and care hours, close the M-10 rows for the three carer columns) and §4 page 12 (the
employment row is wrong — see OQ-037); parent SDD (record FR-003 as unimplemented, per §8); DPIA
and RoPA amendment per OQ-039.

**Sequencing note.** W1, W2, W5 and W6 all delete live attributes. They should go in **one**
maker-portal / deployment session, together with the outstanding `rev_breaktype` and
`rev_applicanttype` orphan-value cleanup, behind a single explicit human go-ahead — not six
separate approvals, which is how the safety classifier ends up declining the seventh.

---

## Approval

**Reviewed by:** ___________  **Date:** ___________  **Response:** `APPROVED`
