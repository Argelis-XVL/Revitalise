# The Live Application Form — What It Collects, and Where It Loses Data

**Feature slug:** `revitalise-grant-automation`
**Automation:** #1 — Form Validation & Completeness (SDD FR-001 to FR-006)
**Date:** 2026-08-13 · **revision 1.0 — reframed from a build specification into documentation of the live form**
**Status:** DOCUMENTATION of the live form as it stood on 2026-08-13, plus one scoped change request (§7).
**Supersedes:** revisions 0.1, 0.2 and 0.3 of this document, which were written as a forward specification for a form that already existed. See §0.
**The form:** https://revitalise.org.uk/apply-for-funding/ — a 20-page Gravity Forms form (form id 3) on Revitalise's WordPress site, built and owned by **Alex**, Revitalise's external website designer. It is live and taking applications now.
**Evidence:** the page's own HTML and its embedded Gravity Forms conditional-logic map, fetched 2026-08-13; and `docs/Import/Application Data Export(Sheet1).csv` (163 columns, `cp1252`) — the charity's annotated inventory of that form's export layout. See §2.
**SDD:** `docs/plans/revitalise-grant-automation-plan.md` (APPROVED) — §1, §4 A, §4 B, §5, §6, §7
**TAD:** `docs/architecture/revitalise-grant-automation-architecture.md` (APPROVED) — §4, §4.1, §5.1, §6, §8, §12, ADR-011, ADR-020
**Solution source:** `src/solutions/RevitaliseGrantAutomation/` — `Entities/rev_applicant`, `Entities/rev_application`, `OptionSets/*.xml`, `Workflows/REVIntakeWordPressToDataverse-*.json`

---

## 0. Revision 1.0 — the premise of this document was wrong, and this is the correction

Revisions 0.1 to 0.3 were written as **a specification to hand to Alex so that Alex could build a
form**. Every section was phrased that way: "the form you build", "before you start", "the acceptance
contract for the form build", "do not build until OPEN-20 is closed", "Revitalise closes §14, this
document is then reissued as CONFIRMED and handed to Alex".

**The form already exists. Alex already built it. It is live and it is taking applications.** The
reviewer has confirmed this directly. Nothing in revisions 0.1 to 0.3 was going to be built from,
because the thing it described building is already in production.

That single error made three other things wrong, and they are worth naming because they explain most
of the corrections in this revision:

| What the earlier revisions assumed | What is actually true |
|---|---|
| The 163-column CSV was a **target** the new form should produce | It is a **description of the live form's existing export**, annotated by the charity. Reality, not a goal. |
| Where the live form and the committed Dataverse schema disagreed, the form should be changed | The form is out-of-palette and already live. **Where they disagree, either the intake mapping changes, the schema changes, or a change request goes to Alex** — and which of those three it is has to be decided case by case. §9. |
| The field list, option values and validation rules could be *specified* | They can only be *observed*. Where this document states an option value or a rule, it is because the live form's own HTML says so. Where the live form disagrees with a committed option set, that is a defect in the integration, not in the form. §6. |

**What survives from revisions 0.1 to 0.3, and is carried into this document:** the closed open items
(the confirmed score out of 60, the confirmed frequency scale for the seven SWEMWBS items, the
withdrawal of the referee and emergency-contact questions, the two columns added for carer detail),
the FR-001 to FR-006 traceability, the data-minimisation positions, and the reasoning about why
particular things must not be collected. Those were right. The premise around them was not.

**What this document is now for**, in priority order:

1. **§8 — the payload contract as it really is**, so Automation #4 (the intake) maps against what the
   live form actually sends. This is what fixes test-agent defect **D-003**.
2. **§7 — one scoped change request to Alex**, covering *only* validation and completeness: the
   specific places where the live form lets a wrongly-filled-in or incomplete application through.
   That is the original Automation #1 problem statement (SDD §1: ~60% of processing time is spent
   chasing applicants for missing or wrong information) and it is the only thing being asked of Alex
   right now.
3. **§9 — the mapping gaps that need a decision from the reviewer or Emily** before they can be
   closed in code, stated plainly rather than resolved by guesswork.
4. **§10 — what has and has not actually been checked about accessibility**, which is test-agent
   defect **D-004**. This is deliberately **not** part of the change request in §7: accessibility and
   validation are different concerns and bundling them would dilute both.

---

## 1. Background, in one paragraph

Revitalise awards respite-holiday grants to disabled people and unpaid carers. Around 60% of the
charity's processing time goes on chasing applicants for missing or wrong information (SDD §1).
Applicants have an average reading level of around age 12 and are applying while under strain. The
live form is the surface where that 60% is created or prevented: an application that arrives complete
and correctly typed flows through automatic scoring, gets a reference, and reaches the trustee pack
without anyone touching it; an application that arrives short of one scored answer is withheld from
automatic scoring and handled by hand (FR-022). The form is therefore the highest-leverage surface in
the whole programme, and it is the one surface the Power Platform solution does not own (TAD §8, §12).

---

## 2. How the live form was established, and what could not be established

Three sources, in descending order of authority.

| Source | What it gives | How far it can be trusted |
|---|---|---|
| **The live page's HTML**, fetched directly on 2026-08-13 | Every field, its Gravity Forms field id, its control type, whether it is marked required, its maximum length, every option label and value, all 20 page breaks, the progress indicator | **Authoritative for structure.** These are the attributes the browser receives. Where this document states a field is required, it is because the field carries `gfield_contains_required`. |
| **The form's embedded conditional-logic map** (`window.gf_form_conditional_logic[3]`) | All 23 conditional-logic rules, verbatim, including which field each one is triggered by and on which value | **Authoritative for conditional logic**, with one caveat: it is the client-side map. Gravity Forms evaluates the same rules server-side from the same stored definition, but a plugin could in principle add a rule that is not in this map. Where §7 says "no rule exists", it means no rule exists **in the form's own logic map** — worth confirming with Alex rather than asserting as final. |
| **`docs/Import/Application Data Export(Sheet1).csv`** | The 163 columns of the form's export, in order, and the charity's own commentary on several of them | **Authoritative for the export layout.** It is **not** a set of real applications — the file has two rows: the header, and one row of the charity's annotations ("Not needed", "Psuedynomised ID Number", "To be automatically generated"). No claim in this document about historic data quality is drawn from applicant data, because there is none in this file. |

**One column of that CSV is unusually valuable and is used throughout §7.** Column 9, "Notes", is
annotated by the charity as:

> Admin notes - typically, this is why the application is incomplete. Normally standardised as the
> following missing items - **Location, Age Confirmation, Date, Amount, Disability Information**

That is the charity telling us, in its own words, which five things are missing or wrong often enough
to have become a standard list. Column 8, "Reason for Non-Qual", adds that non-qualification reasons
include "**age being under 18**" and "**location of applicant (not holiday) being not in the UK**".
Every item in §7 that maps onto one of those is marked **[charity-evidenced]**, and those are the ones
to fix first.

### What could NOT be established, and is therefore not claimed anywhere in this document

- **Colour contrast**, keyboard-only navigation, focus order, reflow at 200%/400% zoom, screen-reader
  announcement quality and touch-target sizes. None of these can be read out of static HTML. See §10.
- **Server-side validation.** The form's client-side rules are visible; what Gravity Forms and the
  site's PHP do with a hand-crafted POST is not. Gravity Forms does re-validate required fields and
  field types server-side by default, so the baseline is likely sound, but this has not been tested.
- **What happens after submission** — whether anything posts to Dataverse today. Nothing in this
  repository has run against a live environment (test report §0).
- **Whether the CSV's column inventory is in step with the live form.** In at least one place it is
  not: the inventory carries separate "Start Date" (col 117) and "End Date" (col 118) columns, and the
  live form asks a single free-text "Provisional date" (field 75). See V-04.

---

## 3. The real structure — 20 pages

One page per step, a progress indicator reading **"Step N of 20"** with a percentage, `*` on required
fields with an "indicates required" legend, forward/back navigation, and **no review screen**.

| Page | Heading on the page | Fields (Gravity Forms ids) | Notes |
|---|---|---|---|
| 1 | *(consent gate)* | 135 honeypot, **31** Grant Terms and Conditions | The Continue button is gated on 31 being ticked — the only page-level gate on the form |
| 2 | Personal Details | **15** Name, **14** Address | Name: First + Last only. Address: street, line 2, town/city, postcode |
| 3 | Contact Details | **21** Preferred contact method, **19** Email, **20** Phone | 19 and 20 are conditional on 21 — see V-01 |
| 4 | Age Confirmation | **32** Age Confirmation, **26** Age Range | 26 is **optional** — see V-02 |
| 5 | Who You Are | **30** Are you…, **34** Is someone helping you complete this application? | 34 is hidden when 30 = "A carer applying on behalf of a disabled person" |
| 6 | Helper's Details | **36** Helper's Name, **43** Helper's Email, **44** Helper's Phone, **39** Helper's Organisation, **38** Relationship to you, **40** Applicant Consent, **42** Explanation, **41** Helper Declaration | **Not gated on field 34** — see V-03, the largest single finding |
| 7 | Disability Information | **47** Do you have a disability…, **49** ten condition checkboxes, **50** Other conditions text, **51** Brief confirmation | 49 gated on 47 = Yes; 50 gated on 49 including "Other" |
| 8 | Care Support | **54** Do you require care support in your daily life?, **55** Brief description, 56 static note | 55 gated on 54 = Yes |
| 9 | Disability Information *(the person you support)* | **122** Does the person you support have a disability…, **123** ten condition checkboxes, **124** Other conditions text, **125** Brief confirmation | **Not gated on applicant type** — see V-05 |
| 10 | Types And Levels Of Care | **128** ten care-type checkboxes, **129** Other care types, **130** One brief example, **131** Hours of care a week | **Not gated on applicant type** — see V-05. Nothing on this page has anywhere to be stored — see §9 |
| 11 | Current Circumstances | **133** Life satisfaction 0–10, **132** the seven SWEMWBS statements, **134** the three "last year" questions | The only inputs to the automatic score. See V-08 and §9 |
| 12 | Financial Eligibility | **61** means-tested benefits, **62** Benefit provider, **63** currently working, **64** household income, **65** significant care costs, **66** explain, **67** savings over £6,000, **68** why you cannot fund it | 63, 64, 65 and 67 are all gated on 61 = **No** — see V-06 |
| 13 | Application Details / Estimated Cost Breakdown | **71** Type of Break, **72** Other type, **73** Location or Activity Name, **75** Provisional date, **76** Accommodation cost, **77** Travel, **78** Other, **79** Total, **81** Amount requested, **82** other funding, **84** source, **83** amount, **85** awaiting decision from, **94** exceptional funding request | See V-04 and V-07 |
| 14 | Exceptional Funding Request | **90** Exceptional circumstance, **91** Other, **92** Explain, **93** Additional amount | **Not gated on field 94** — see V-03 |
| 15 | How Would This Break Help You? | **88** the narrative | Capped at **325 characters** — see V-09 |
| 16 | Group Application | **98** part of a group trip?, **99** names of other group members | 99 gated on 98 = Yes ✔ |
| 17 | Previous Funding | **102** had funding before?, **103** more than 12 months ago? | 103 **not gated** on 102 — see V-03 |
| 18 | How Did You Hear About Us? | **107** nine checkboxes (optional), **108** which other location | 108 gated on 107 including "Other" ✔. Nothing here has anywhere to be stored — §9 |
| 19 | Revitalise Funding | 111 static note about the offer letter, **119** Would you like the form posted to you? | Optional |
| 20 | Equality Monitoring | **117** Gender, **118** Ethnic group | Both optional, both explicitly declinable ✔ |

**Field totals, counted from the markup rather than estimated.** **94 field containers**: 20 section
headers, 2 static HTML blocks, 1 anti-spam honeypot, and **71 applicant-facing question fields**. Of
those 71, **61 are marked required** and 10 are optional (age range, helper's organisation, the helper
explanation, both "Brief confirmation" boxes, other funding, referral source, postal preference,
gender, ethnic group). Counting the two Likert grids' rows individually — they carry 7 and 3 statements
— gives **79 distinct questions**. The 20 page breaks are not field containers and are not in the 94.

**Two structural facts worth stating plainly:**

- **There is no "check your answers" screen.** The phrase does not appear anywhere on the page and
  page 20 leads straight to the submit control. FR-006 is not implemented. §11.
- **There is no "save and continue later".** Gravity Forms' save-and-continue markup
  (`gform_save_link`) is absent. On a 20-page form, for a population that often needs another
  person's help to finish, FR-005 is not implemented. §11, V-12.

---

## 4. The real field inventory, and where each field goes

One row per applicant-facing question. **CSV col** is the column in the export inventory. **Payload**
is the JSON field the intake accepts (§8); a dash means the intake has no field for it. **Dataverse**
is the target column; a dash means nothing stores it.

Legend: **R** = marked required on the live form · **O** = optional · **C** = conditional (required
only when revealed).

### Page 1 — the consent gate

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 31 | Grant Terms and Conditions | Consent checkbox | R | — | 12–14 | `grant_terms_consent` + `grant_terms_consent_date` | `rev_application.rev_granttermsconsent` / `…consentdate` |

### Page 2 — Personal Details

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 15.2 | Title | *(sub-field disabled — not rendered)* | — | — | 15 | `title` | `rev_applicant.rev_title` — **never populated**, §9 |
| 15.3 | First name | Text | R | — | 16 | `first_name` | `rev_applicant.rev_firstname` |
| 15.6 | Last name | Text | R | — | 18 | `last_name` | `rev_applicant.rev_lastname` |
| — | Middle name, suffix | *(not rendered)* | — | — | 17, 19 | — | — (CSV annotates both "Not needed") |
| 14.1 | Street address | Text | R | — | 20 | `address_line` | `rev_applicant.rev_addressline` |
| 14.2 | Address line 2 | Text | O | — | 21 | `address_line2` | `rev_applicant.rev_addressline2` |
| 14.3 | Town / City | Text | R | — | 22 | `town_city` | `rev_applicant.rev_towncity` |
| 14.5 | Postcode | Text, **no format check** | R | — | 24 | `postcode` | `rev_applicant.rev_postcode` |
| 14.4 | State / Province | *(hidden)* | — | — | 23 | — | — |
| 14.6 | Country | *(hidden, fixed to "United Kingdom")* | — | — | 25 | — | — · **see V-11** |

### Page 3 — Contact Details

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 21 | Preferred contact method — Email / Phone / Post | **Checkbox group** (multi-select) | R | — | 26, 27, 28 | — | — · **not stored anywhere**, §9 |
| 19 | Email + **Confirm Email** | `type=email`, two boxes | C (21 includes Email) | — | 29 | `email` | `rev_applicant.rev_email` |
| 20 | Phone | `type=tel`, no format check | C (21 includes Phone) | — | 30 | `phone` | `rev_applicant.rev_phone` |

The form's own help text on this page is *"Please provide at least one way for us to contact you."*
The implementation does not deliver that — see **V-01**.

### Page 4 — Age Confirmation

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 32 | Age Confirmation (aged 18 or over) | Consent checkbox | R | — | 31–33 | `age_confirmation_consent` + `…_date` | `rev_application.rev_ageconfirmationconsent` / `…consentdate` |
| 26 | Age Range — eight bands | Radio | **O** | — | 34 | `age_range` | `rev_applicant.rev_agerange` |

**There is no date-of-birth field anywhere on the live form.** The word "birth" does not appear on the
page. This is the single most consequential difference between the live form and what the intake was
built to expect, and it is fixed in code in this revision — see §8 and V-02.

### Page 5 — Who You Are

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 30 | Are you… — three options (§6) | Radio | R | — | 35 | `applicant_type` | `rev_applicant.rev_applicanttype` |
| 34 | Is someone helping you complete this application? | Radio Yes/No | R, hidden when 30 = "A carer applying on behalf of a disabled person" | — | 36 | — *(routing answer)* | — |

### Page 6 — Helper's Details — **entirely unconditional**

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 36.3 / 36.6 | Helper's first and last name | Text | **R** | — | 38, 40 | `helper_name` | `rev_application.rev_helpername` |
| 43 | Helper's Email + Confirm Email | `type=email` | **R** | — | 42 | `helper_email` | `rev_application.rev_helperemail` |
| 44 | Helper's Phone | `type=tel` | **R** | — | 43 | `helper_phone` | `rev_application.rev_helperphone` |
| 39 | Helper's Organisation ("If applicable.") | Text | O | — | 44 | `helper_organisation` | `rev_application.rev_helperorganisation` |
| 38 | Relationship to you ("e.g., family member, support worker, friend, carer.") | **Free text** | **R** | — | 45 | `helper_relationship` | `rev_application.rev_helperrelationship` — **type mismatch**, §9 |
| 40 | Applicant Consent | Consent checkbox | **R** | — | 46–48 | `applicant_consent` + `…_date` | `rev_application.rev_applicantconsent` / `…consentdate` |
| 42 | Explanation | Textarea | O | — | 49 | — | — · **not stored**, §9 |
| 41 | Helper Declaration | Consent checkbox | **R** | — | 50–52 | `helper_declaration_consent` + `…_date` | `rev_application.rev_helperdeclarationconsent` / `…consentdate` |

Six required fields about a third party, shown to every applicant whether or not anyone is helping.
**V-03.**

### Page 7 — Disability Information (the applicant)

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 47 | Do you have a disability as defined by the Equality Act 2010? | Radio Yes/No | R | — | 53 | — | — · **not stored**, §9 |
| 49 | Do any conditions or illnesses affect you in any of the following areas? — **ten** checkboxes (§6) | Checkbox group | C (47 = Yes) | — | 54–63 | `condition_profile` | `rev_application.rev_conditionprofile` — **option mismatch**, §9 |
| 50 | Other conditions or illnesses affect you | Text | C (49 includes Other) | — | 64 | `other_condition_raw` | `rev_application.rev_otherconditionraw` |
| 51 | Brief confirmation ("Optional but helpful…") | Textarea | O | 650 | 65 | — | — · **not stored**, §9 |

### Page 8 — Care Support (the applicant's own needs)

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 54 | Do you require care support in your daily life? | Radio Yes/No | R | — | 66 | `needs_care_support_personally` | `rev_application.rev_needscaresupportpersonally` |
| 55 | Brief description | Textarea | C (54 = Yes) | 900 | 67 | `care_support_description` | `rev_application.rev_caresupportdescription` |

### Page 9 — Disability Information (the person supported)

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 122 | Does the person you support have a disability…? | Radio Yes/No | R | — | 68 | — | — · **not stored**, §9 |
| 123 | Ten checkboxes, same list as 49 | Checkbox group | C (122 = Yes) | — | 69–78 | `support_recipient_condition_profile` | `rev_application.rev_supportrecipientconditionprofile` — **option mismatch**, §9 |
| 124 | Other conditions or illnesses | Text | C (123 includes Other) | — | 79 | `support_recipient_other_condition_raw` | `rev_application.rev_supportrecipientotherconditionraw` |
| 125 | Brief confirmation | Textarea | O | 650 | 80 | — | — · **not stored**, §9 |

**The person supported is never named.** `support_recipient_name` / `rev_supportrecipientname` exists
and has no source on the live form. §9.

### Page 10 — Types And Levels Of Care — nothing here is stored

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 128 | What type of care and support do you personally provide? — ten checkboxes + Other | Checkbox group | R | — | 81–91 | — | — |
| 129 | Other types of care and support | Text | C (128 includes Other) | — | 92 | — | — |
| 130 | One brief example of the level of care required | Textarea | R | **180** | 93 | — | — |
| 131 | Hours of care a week — five bands (§6) | Radio | R | — | 94 | — | — |

### Page 11 — Current Circumstances — the eleven scored answers

| GF id | Question | Control | R/O/C | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|
| 133 | Overall, how satisfied are you with your life nowadays? | **`type=number`, min 0, max 10, `step=any`** | R | 95 | `feeling_scale_answer` | `rev_application.rev_feelingscaleanswer` |
| 132 row 1 | I've been feeling optimistic about the future | Likert, **5 columns** | R | 96 | `wellbeing_answer_1` | `rev_wellbeinganswer1` |
| 132 row 2 | I've been feeling useful | Likert, 5 | R | 97 | `wellbeing_answer_2` | `rev_wellbeinganswer2` |
| 132 row 3 | I've been feeling relaxed | Likert, 5 | R | 98 | `wellbeing_answer_3` | `rev_wellbeinganswer3` |
| 132 row 4 | I've been dealing with problems well | Likert, 5 | R | 99 | `wellbeing_answer_4` | `rev_wellbeinganswer4` |
| 132 row 5 | I've been thinking clearly | Likert, 5 | R | 100 | `wellbeing_answer_5` | `rev_wellbeinganswer5` |
| 132 row 6 | I've been feeling close to other people | Likert, 5 | R | 101 | `wellbeing_answer_6` | `rev_wellbeinganswer6` |
| 132 row 7 | I've been able to make up my own mind about things | Likert, 5 | R | 102 | `wellbeing_answer_7` | `rev_wellbeinganswer7` |
| 134 row 1 | Go out and do something you enjoy? | Likert, **6 columns** | R | 103 | `wellbeing_answer_8` | `rev_wellbeinganswer8` |
| 134 row 2 | Enjoy other people's company? | Likert, **6** | R | 104 | `wellbeing_answer_9` | `rev_wellbeinganswer9` |
| 134 row 3 | Have a break when you've needed one? | Likert, **6** | R | 105 | `wellbeing_answer_10` | `rev_wellbeinganswer10` |

Field 132's stem is *"Please say what best describes your experience of each over the last 2 weeks."*
Field 134's stem is *"Thinking about the last year, have you been able to"*. **The two blocks do not
share a response scale**, which revision 0.3 recorded as confirmed and which the live form
contradicts. §6, V-08, §9.

### Page 12 — Financial Eligibility

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 61 | Do you currently receive any means-tested benefits? | Radio Yes/No | R | — | 106 | `receives_benefits` | `rev_application.rev_receivesbenefits` |
| 62 | Benefit provider | Text | C (61 = Yes) | — | 107 | `benefit_provider` | `rev_application.rev_benefitprovider` |
| 63 | Are you currently working? | Radio Yes/No | **C (61 = No)** | — | 108 | `currently_working` | `rev_application.rev_currentlyworking` |
| 64 | Approximate household income (before tax) — four bands (§6) | Radio | **C (61 = No)** | — | 109 | `income_band` | `rev_application.rev_incomeband` — **option mismatch**, §9 |
| 65 | Do you have significant care costs or medical expenses? | Radio Yes/No | **C (61 = No)** | — | 110 | `significant_care_costs` | `rev_application.rev_significantcarecosts` |
| 66 | Please briefly explain those costs | Text | C (65 = Yes) | — | 111 | `care_costs_explanation` | `rev_application.rev_carecostsexplanation` |
| 67 | Do you have savings over £6,000? | Radio Yes/No | **C (61 = No)** | — | 112 | `savings_over_6000` | `rev_application.rev_savingsover6000` |
| 68 | Please briefly explain why you're unable to fund this break yourself | Textarea | R | 1200 | 113 | `unable_to_fund_explanation` | `rev_application.rev_unabletofundexplanation` |

Four of the eight financial questions — including the £6,000 savings test, which is an eligibility
rule — are asked **only of applicants who say they receive no means-tested benefits**. **V-06.**

### Page 13 — Application Details and cost breakdown

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 71 | Type of Break — five options (§6) | Radio | R | — | 114 | `break_type` | `rev_application.rev_breaktype` — **option mismatch**, §9 |
| 72 | Other type of break | Text | C (71 = Other) | — | 115 | `other_break_type` | `rev_application.rev_otherbreaktype` |
| 73 | Location or Activity Name ("Name of accommodation, location, or activity.") | Text | R | — | 116 | `break_location` | `rev_application.rev_breaklocation` |
| 75 | Provisional date (*"e.g., 'July 2025' or 'Summer 2025'."*) | **Free text** | R | — | 117 *(and 118 has no source)* | — | `rev_breakstart` / `rev_breakend` — **cannot be populated**, V-04 |
| 76 | Accommodation or Activity Cost | Number rendered as text | R | — | 119 | `accommodation_cost` | `rev_application.rev_accommodationcost` |
| 77 | Travel costs | Number rendered as text | R | — | 120 | `travel_cost` | `rev_application.rev_travelcost` |
| 78 | Other costs | Number rendered as text | R | — | 121 | `other_cost` | `rev_application.rev_othercost` |
| 79 | **Total estimated cost** | Number the applicant types | R | — | 122 | — | `rev_costs` is **calculated** — do not send, V-07 |
| 81 | Amount Requesting from Revitalise | Number rendered as text | R | — | 123 | `amount_requested` | `rev_application.rev_amountrequested` |
| 82 | Are you receiving funding from any other sources? — Yes / No / **Applied and awaiting decision from** | Radio | **O** | — | 124 | `receiving_other_funding` | `rev_application.rev_receivingotherfunding` — **three options into a boolean**, §9 |
| 84 | Please specify source of additional funding | Text | C (82 = Yes) | — | 125 | `other_funding_source` | `rev_application.rev_otherfundingsource` |
| 83 | Please specify amount of additional funding | Number | C (82 = Yes) | — | 126 | `other_funding_amount` | `rev_application.rev_otherfundingamount` |
| 85 | Awaiting decision from | Text | C (82 = "Applied and awaiting decision from") | — | 127 | `awaiting_decision_from` | `rev_application.rev_awaitingdecisionfrom` |
| 94 | I'd like to make an exceptional funding request | Radio Yes/No | R | — | 128 | `exceptional_funding_requested` | `rev_application.rev_exceptionalfundingrequested` |

**The standard grant amounts are stated on the live form**, in field 94's own help text: *"our usual
funding amounts are £500 towards the cost of a respite break or holiday and up to £100 towards a day
trip or activity"*. Earlier revisions of this document recorded "no maximum grant amount is stated in
any source document" — the live form states it. §12, OPEN-11.

### Page 14 — Exceptional Funding Request — **unconditional**

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 90 | Exceptional circumstance — four options (§6) | Radio | **R** | — | 129 | `exceptional_circumstance` | `rev_application.rev_exceptionalcircumstance` — **option mismatch**, §9 |
| 91 | Other exceptional circumstance | Text | C (90 = Other) | — | 130 | `other_exceptional_circumstance` | `rev_application.rev_otherexceptionalcircumstance` |
| 92 | Briefly explain exceptional circumstance | Textarea | **R** | 500 | 131 | `exceptional_funding_detail` | `rev_application.rev_exceptionalfundingdetail` |
| 93 | Additional amount requested | Number | **R** | — | 132 | `additional_amount_requested` | `rev_application.rev_additionalamountrequested` |

### Pages 15 to 20

| GF id | Question | Control | R/O/C | Max | CSV col | Payload | Dataverse |
|---|---|---|---|---|---|---|---|
| 88 | Please briefly explain how this break would benefit you | Textarea | R | **325** | 133 | `narrative_raw` | `rev_application.rev_narrativeraw` — V-09 |
| 98 | Is this part of a group trip? | Radio Yes/No | R | — | 134 | `is_group_trip` | `rev_application.rev_isgrouptrip` |
| 99 | Names of other group members | **GF List field** | C (98 = Yes) | — | 135 | `group_member_names` | `rev_application.rev_groupmembernames` |
| 102 | Have you received funding from us before? | Radio Yes/No | R | — | 136 | `received_funding_before` | `rev_application.rev_receivedfundingbefore` |
| 103 | Was this more than 12 months ago? | Radio Yes/No | **R, not gated on 102** | — | 137 | `more_than_12_months_ago` | `rev_application.rev_morethan12monthsago` |
| 107 | How did you hear about us? — nine checkboxes | Checkbox group | O | — | 138–146 | — | — · **not stored**, §9 |
| 108 | Which other location did you hear about us from? | Text | C (107 includes Other) | — | 147 | — | — |
| 119 | Would you like the form posted to you? | Radio | O | — | 148 | `would_like_form_posted` | `rev_application.rev_wouldlikeformposted` |
| 117 | Gender — five options (§6) | Radio | O | — | 149 | `gender` | `rev_applicant.rev_gender` |
| 118 | Ethnic group — six options (§6) | Radio | O | — | 150 | — | — · **deliberately not stored**, SDD OQ-027 |

### Fields the export carries that are not applicant answers

| CSV cols | What they are | Position |
|---|---|---|
| 1–11 | The charity's own admin columns: Status, Grant Round 1–3, ID Number, Amount Granted, Group, Reason for Non-Qual, Notes, Overall Circumstance Score (out of 60), Impact Report Due | **Not form fields.** Column 7 "Group" is annotated "Group Number - generated to link applications" — it is the process owner's own grouping, which is why `group_linkage` has been removed from the intake contract in this revision. Column 10 confirms the score is **out of 60**. |
| 151–163 | Gravity Forms metadata: Created By, Entry ID, Entry Date, Date Updated, Source Url, Transaction/Payment fields, Post Id, User Agent, User IP, Submission Speed | Only **Entry ID** is wanted — it is the `submission_id` (§8). **User IP and User Agent must never be sent**: personal data with no purpose here (NFR-013). |

---

## 5. The real conditional logic — all 23 rules

Read verbatim from the form's own logic map. "f*n*" is a Gravity Forms field id.

| # | Field shown | Shown when |
|---|---|---|
| 1 | Page 1's Continue button | f31 (Grant T&Cs) is ticked |
| 2 | f19 Email | f21 Preferred contact method **is** "Email" |
| 3 | f20 Phone | f21 Preferred contact method **is** "Phone" |
| 4 | f34 Is someone helping you? | f30 Are you… **is not** "A carer applying on behalf of a disabled person" |
| 5 | f49 Condition checkboxes (applicant) | f47 Do you have a disability **is** "Yes" |
| 6 | f50 Other conditions text (applicant) | f49 includes "Other (please specify)" |
| 7 | f55 Brief description of care needed | f54 Do you require care support **is** "Yes" |
| 8 | f62 Benefit provider | f61 means-tested benefits **is** "Yes" |
| 9 | f63 Are you currently working? | f61 means-tested benefits **is** "No" |
| 10 | f64 Household income band | f61 means-tested benefits **is** "No" |
| 11 | f65 Significant care costs? | f61 means-tested benefits **is** "No" |
| 12 | f66 Explain those costs | f65 **is** "Yes" |
| 13 | f67 Savings over £6,000? | f61 means-tested benefits **is** "No" |
| 14 | f72 Other type of break | f71 Type of Break **is** "Other (please specify)" |
| 15 | f83 Amount of additional funding | f82 **is** "Yes" |
| 16 | f84 Source of additional funding | f82 **is** "Yes" |
| 17 | f85 Awaiting decision from | f82 **is** "Applied and awaiting decision from" |
| 18 | f91 Other exceptional circumstance | f90 Exceptional circumstance **is** "Other (please specify)" |
| 19 | f99 Names of other group members | f98 Is this part of a group trip **is** "Yes" |
| 20 | f108 Which other location did you hear about us from | f107 includes "Other (please specify)" |
| 21 | f123 Condition checkboxes (person supported) | f122 Does the person you support have a disability **is** "Yes" |
| 22 | f124 Other conditions text (person supported) | f123 includes "Other (please specify)" |
| 23 | f129 Other types of care | f128 includes "Other (please specify)" |

**Rules 6, 14, 18, 20, 22 and 23 are exactly right** — every "Other (please specify)" free-text field
is gated on its own "Other" option being ticked, and the two condition-text fields are correctly
gated on their **own** checkbox group (f50 on f49 for the applicant, f124 on f123 for the person
supported). Getting those two crossed would put one person's health information in the other
person's column, and they are not crossed.

**What has no rule at all, and is therefore shown and required to everyone:**

- **The whole of page 6, Helper's Details** — f36, f43, f44, f39, f38, f40, f42, f41. Nothing on that
  page is gated on f34, the question that asks whether anyone is helping.
- **Three of the four fields on page 14, Exceptional Funding Request** — f90, f92 and f93. Nothing is
  gated on f94, the question that asks whether the applicant wants to make an exceptional request.
- **f103 "Was this more than 12 months ago?"**, which is not gated on f102 "Have you received funding
  from us before?".
- **The whole of page 9 and the whole of page 10**, which are about a person the applicant supports
  and the care they provide, and which are not gated on f30 "Are you…".

Those four are V-03 and V-05 in §7, and between them they are the largest source of wrongly
filled-in data on this form.

---

## 6. The real option lists

These close **OPEN-20**, which asked Revitalise to supply five option lists the earlier revisions
carried as placeholders. The live form has them. Each table below gives the **exact string the form
sends** and, where a committed option set exists, the value the intake would have to map it to.

#### Are you… (f30, CSV col 35) — three options, not four

| Form sends | Maps to `rev_applicanttype` |
|---|---|
| A disabled person | 1 (schema label "A disabled person applying for myself") |
| A carer applying on behalf of a disabled person | 4 (schema label "Someone applying on behalf of another person") |
| A carer applying for yourself | 2 (schema label "An unpaid carer applying for myself") |

Value 3 of `rev_applicanttype` ("An unpaid carer applying with the person I care for") has no
equivalent on the live form. §9.

#### Age Range (f26, CSV col 34) — eight bands

| Form sends | `rev_agerange` |
|---|---|
| 18-24 | 2 |
| 25-34 | 3 |
| 35-44 | 4 |
| 45-54 | 5 |
| 55-64 | 6 |
| 65-74 | 7 |
| 75 or over | 8 |
| Prefer not to say | 9 (Not known) |

This map is now configuration, not code: `rev_settings` row **`AgeRangeLabelMap`**. `rev_agerange`
value 1 ("Under 18") has no band on the form, because field 32 gates on being 18 or over.

#### Condition areas (f49 and f123, CSV cols 54–63 and 69–78) — **ten** checkboxes

Both groups offer the same ten, verbatim:

1. Vision (for example blindness or partial sight)
2. Hearing (for example deafness or partial hearing)
3. Mobility (for example walking short distances or climbing stairs)
4. Dexterity (for example lifting and carrying objects, using a keyboard)
5. Learning or understanding or concentrating
6. Memory
7. Mental health
8. Stamina or breathing or fatigue
9. Socially or behaviourally (for example associated with autism spectrum disorder (ASD) which includes Asperger's, or attention deficit hyperactivity disorder (ADHD))
10. Other (please specify)

The committed `rev_conditionprofile` option set carries a **different eight**: Physical disability,
Sensory impairment, Learning disability, Neurological condition, Long-term health condition, Mental
health condition, Autism, Other. **These two lists are not two spellings of the same thing** — they
classify along different axes (the form asks about *functional areas affected*, the option set names
*condition types*). This cannot be mapped without a decision. §9, the highest-priority item there.

#### Care types provided (f128, CSV cols 81–91) — ten checkboxes plus Other

Personal care (washing, dressing, toileting, feeding) · Mobility assistance · Medication management ·
Household tasks · Managing appointments and healthcare coordination · Financial and administrative
support · Emotional support and companionship · Supervision for safety · Communication support ·
Night-time care · Other (please specify). **Nothing stores any of it.** §9.

#### Hours of care a week (f131, CSV col 94) — five bands

| Form sends |
|---|
| 9 hours or less |
| 10 – 19 hours |
| 20 – 34 hours |
| **35 – 59 hours** |
| **50+** |

**Bands four and five overlap.** An applicant providing 55 hours of care a week can honestly tick
either. The standard census banding is 9 or less / 10–19 / 20–34 / **35–49** / 50+, so "35 – 59" is
almost certainly a typo for "35 – 49". **V-10.**

#### The response scales on page 11 — two different scales, not one

**Field 132, the seven SWEMWBS statements — five columns:**

| Column | Label |
|---|---|
| 1 | None of the time |
| 2 | Rarely |
| 3 | Some of the time |
| 4 | Often |
| 5 | All of the time |

This is exactly the frequency scale revision 0.3 recorded as confirmed, in exactly that order, and it
is SWEMWBS's own published scale. The committed `rev_likertresponse` option set matches it. ✔

**Field 134, the three "last year" questions — six columns:**

| Column | Label |
|---|---|
| 1 | Strongly disagree |
| 2 | Disagree |
| 3 | Neutral |
| 4 | Agree |
| 5 | Strongly agree |
| 6 | **Not sure** |

**Revision 0.3 recorded that all ten wellbeing questions used the same five-point frequency scale.
The live form contradicts that.** These three use a six-point agree/disagree scale with an
unscoreable "Not sure", on questions phrased as questions — "Have a break when you've needed one?"
answered "Strongly disagree". `rev_likertresponse` has five values and no "Not sure", so answers 6
have nowhere to go and the score out of 60 has no defined value for them. **V-08 and §9.**

#### Life satisfaction (f133, CSV col 95)

`type=number`, `min=0`, `max=10`, **`step=any`**, help text *"On a scale of 0 to 10, where 0 is 'not
at all' and 10 is 'completely'."* The 0-to-10 range confirms revision 0.3's OPEN-22 answer and the
CSV's own "out of 60" header. `step=any` accepts 7.5. **V-10.**

#### Household income (f64, CSV col 109) — four bands, not six

| Form sends | Nearest `rev_incomeband` |
|---|---|
| Under £15,000 per year | 1 or 2 — **ambiguous** |
| £15,000 - £25,000 | 2 or 3 — **ambiguous** |
| £25,000 - £35,000 | 3 or 4 — **ambiguous** |
| Over £35,000 | 4 or 5 — **ambiguous** |

The committed set has six values with £10,000 boundaries and a "Prefer not to say". The live form has
four with £15,000/£25,000/£35,000 boundaries and no decline option, and its bands are inclusive at
both ends so £25,000 exactly falls in two of them. **No band on the form maps cleanly to a band in
the option set.** §9 — and it matters more than the others because `rev_incomeband` feeds the income
eligibility flag (FR-011 to FR-015) against the `IncomeCeiling` setting.

#### Type of Break (f71, CSV col 114) — five options, not nine

Holiday accommodation (hotel, cottage, caravan, holiday park) · Day trips or outings · Activity or
experience (e.g., theatre, concert, attraction) · Respite care facility stay · Other (please specify)

#### Exceptional circumstance (f90, CSV col 129) — four options, not seven

Palliative care · Carer breakdown/urgent need · Severe financial hardship · Other (please specify)

#### Other funding (f82, CSV col 124) — three options into a boolean

Yes · No · **Applied and awaiting decision from**. `rev_receivingotherfunding` is a boolean, so the
third answer loses its distinctness. §9.

#### Gender (f117, CSV col 149) — five options

Female · Male · Non-binary · **Prefer to self-describe** · **Prefer not to say**. Maps 1:1 onto
`rev_gender` values 1–5, whose labels differ only in wording ("I describe myself another way", "I
would rather not say"). A declinable equality-monitoring question with a clear "this will not affect
your application" statement. ✔

#### Ethnic group (f118, CSV col 150) — six options, collected, deliberately not stored

Asian or Asian British · Black, African, Caribbean or Black British · Mixed or Multiple ethnic groups
· White · Other ethnic group · Prefer not to say.

**OPEN-17 is now fully settled on the facts.** The live form does collect ethnic group, optionally and
declinably, under an explicit "completely optional and will not affect your application in any way"
statement. It remains **deliberately absent** from the Dataverse schema and from the intake contract,
excluded at the architecture gate pending the DPO's input (SDD OQ-027). Nothing changes in the build;
what changes is that the question is now "should we keep collecting it, and on what basis", not "is it
collected".

---

## 7. The change request to Alex — validation and completeness only

**This is the one thing being asked of Alex right now.** It is deliberately narrow: the live form's
data validation, aimed at reducing wrongly filled-in and incomplete submissions. Nothing about
accessibility is in this list — that is §10, and it needs a real audit before anything is asked of
anybody.

Every item below is evidenced from the live form's own markup or logic map, or from the charity's own
"standard missing items" note (§2). **Nothing here is inferred from an assumption about how the form
ought to work.** Items marked **[charity-evidenced]** map onto one of the five items the charity
already records as routinely missing — those are the ones to do first.

### Priority 1 — fields that are required but should not be, and vice versa

**V-03. Three blocks of questions are required of applicants they do not apply to.**

| Block | The gate that exists | The gate that is missing |
|---|---|---|
| **Page 6, Helper's Details** — helper's name, email, phone, relationship, Applicant Consent, Helper Declaration (6 required fields) | f34 asks "Is someone helping you complete this application?" on page 5 | **Nothing on page 6 is conditional on f34.** An applicant completing the form alone must enter a name, a valid email address, a phone number and a relationship for a helper who does not exist, and tick a declaration on that person's behalf, or they cannot get past page 6 |
| **Page 14, Exceptional Funding Request** — circumstance, explanation, additional amount (3 required fields) | f94 asks "I'd like to make an exceptional funding request" on page 13 | **f90, f92 and f93 are not conditional on f94.** An applicant who answered "No" must still pick one of Palliative care / Carer breakdown / Severe financial hardship / Other, write an explanation, and enter an additional amount |
| **f103 "Was this more than 12 months ago?"** | f102 asks "Have you received funding from us before?" | **f103 is not conditional on f102.** An applicant who has never had funding must answer a question about when they had it |

**Why this is the top item.** These are not cosmetic. They *manufacture* wrong data: a required field
that does not apply is answered with whatever gets the applicant to the next page. The exceptional
funding block is the clearest case — every application will carry an exceptional circumstance and an
additional amount, so the field that is supposed to identify the urgent minority identifies everyone
and is worth nothing. The helper block is the most harmful, because it puts invented contact details
for a third party into a charity's records, and because a "Helper Declaration" ticked by somebody who
is not a helper is a declaration nobody made.

**The fix:** add conditional logic so that page 6's fields require f34 = "Yes", and page 14's fields
require f94 = "Yes", and f103 requires f102 = "Yes". Gravity Forms already does this correctly in 23
other places on this same form, including for every "Other (please specify)" box — so the mechanism is
in use and understood; these four are omissions, not limitations.

**One thing to check while doing it:** field 40, "Applicant Consent", currently sits on page 6. If it
is the *applicant's own* declaration it must stay unconditional and should move off the helper page;
if it is the applicant consenting to a helper acting for them, it belongs behind the f34 = Yes gate
with the rest. The form does not make clear which it is.

**V-05. Two whole pages about a person the applicant may not have. [charity-evidenced — "Disability Information"]**

Page 9 ("Does the person you support have a disability…?" plus ten condition checkboxes) and page 10
("What type of care and support do you personally provide?", a brief example, and hours of care a
week) are required of **every** applicant, including someone who picked "A disabled person" at f30 and
supports nobody.

**The fix:** gate pages 9 and 10 on f30 being one of the two carer answers. If the charity does want
to ask a disabled self-applicant whether they also care for someone, that needs its own question —
not a page that presumes the answer.

**V-01. An applicant can complete the form without giving an email address or a phone number.**

Field 21, "Preferred contact method", is a **required checkbox group** offering Email / Phone / Post.
Field 19 (Email) is shown only when Email is ticked; field 20 (Phone) only when Phone is ticked. An
applicant who ticks **Post** alone satisfies the required field and gives the charity **no email
address and no phone number at all**. The form's own help text on that page says *"Please provide at
least one way for us to contact you"* — the implementation does not enforce it.

**Why this matters more than it looks.** Chasing a missing detail is the 60% problem. An application
with no email address and no phone number can only be chased by post, which is the slowest and most
expensive channel the charity has, and the applicant cannot be sent an acknowledgement or a reference
number at all. It also breaks the downstream integration: the intake used to reject any payload with
no email address, which would have rejected these applications outright. That has been fixed on the
Revitalise side in this revision (§8), but the underlying problem is on the form.

**The fix, in preference order:** (a) make Email unconditional and required, and keep field 21 purely
as *"how would you like us to reply?"*; or (b) require **at least one of** Email or Phone — Gravity
Forms can do this with a rule on field 21 that requires Email or Phone to be among the ticked boxes;
or (c) if a genuinely postal-only route must exist, make the address fields carry the weight and say
explicitly on the page that a postal-only application will take longer.

**V-02. Age is only ever asserted by a tickbox. [charity-evidenced — "Age Confirmation"; non-qualification reason "age being under 18"]**

The form asks for **no date of birth** (the word "birth" does not appear on the page) and its "Age
Range" question (f26) is **optional**. The only age information guaranteed to arrive is field 32, a
required tickbox confirming the applicant is 18 or over. Yet "age being under 18" is one of the
charity's own recorded non-qualification reasons, and "Age Confirmation" is on its own list of
standard missing items.

**The fix, smallest first:** make the Age Range question **required**, keeping "Prefer not to say" as
an option so nobody is forced to disclose. That single change gives every application an age band
without collecting a date of birth, which is also the more data-minimising choice (NFR-013) and is
what the Revitalise side now expects. Only if the charity needs an exact age — for example to apply a
rule at a specific birthday — is a date of birth worth adding, and that is a bigger question for the
DPO.

### Priority 2 — format validation that is absent

**V-04. The break date is a free-text box. [charity-evidenced — "Date"]**

Field 75, "Provisional date", is a plain text input whose help text is *"e.g., 'July 2025' or
'Summer 2025'."* So free text is deliberate — but four things follow from it:

1. The charity cannot filter or sort applications by date, cannot check the break is far enough away
   to be funded through a monthly board cycle, and cannot spot a break that has already happened.
2. The export inventory carries **two** date columns, "Start Date" and "End Date" (117, 118). One
   free-text answer cannot fill two date columns. `rev_breakstart` and `rev_breakend` on the
   Revitalise side are date columns and **cannot be populated at all** from this field today.
3. The help text's examples are **2025** dates on a form taking applications in 2026. An applicant
   copying the example writes a date in the past.
4. There is no minimum notice check, so an applicant can ask for a break next week.

**The fix:** keep a free-text "roughly when?" if the charity wants it, but add a **start date** and an
**end date** as real date fields — Gravity Forms date fields with a minimum date of today, end not
before start. Make them optional if the charity truly cannot ask applicants to commit; even optional
structured dates are worth more than a required unstructured one. And update the example years.

**V-07. Nothing checks that the money adds up. [charity-evidenced — "Amount"]**

Fields 76, 77, 78 (accommodation, travel, other), 79 (**Total estimated cost**) and 81 (Amount
requesting from Revitalise) are all separate inputs the applicant types. Nothing computes the total
from its three parts, and nothing compares the amount requested against it. So an application can
arrive claiming £600 + £120 + £130 with a total of £400 and a request for £900, and no one finds out
until a person reads it.

**The fix:** make field 79 a **calculated, read-only** total of 76 + 77 + 78 — Gravity Forms supports
calculated number fields, so this needs no code. Validate field 81 as **not greater than** field 79.
Set `min=0` on all five and force two decimal places. And because the live form itself states the
usual amounts (£500 for a break, £100 for a day trip), a **warning** — not a block — when the request
exceeds those would set expectations honestly at the point the number is typed rather than after
assessment.

Note for the Revitalise side: the total is *calculated* in Dataverse from the three components, so
field 79 must not be posted even once it is computed in the browser. §8.

**V-11. The postcode is unvalidated, and the country is hidden. [charity-evidenced — non-qualification reason "location of applicant … not in the UK"]**

The postcode sub-field (14.5) is a plain text input with no pattern check, and the address block's
**Country sub-field is hidden and hard-set to "United Kingdom"** while the State/Province sub-field is
hidden and empty. Two consequences:

1. Revitalise derives the applicant's UK region from the postcode and shows the region — never the
   postcode — wherever a trustee can see it. An unreadable postcode means the region is honestly
   recorded as "Not known", and the trustee pack for that application is missing something the board
   uses.
2. A non-UK applicant is one of the charity's own recorded non-qualification reasons, and the form
   cannot detect one, because the country is fixed rather than asked.

**The fix:** add a UK postcode format check to 14.5 (accepting lower case and a missing space, which
Gravity Forms can normalise), with a plain-English message and an example. Whether to unhide the
country field is a policy question for Emily rather than a validation fix — but if UK residence is a
qualifying condition, something has to ask it.

**V-10. Two option lists let an applicant answer wrongly through no fault of their own.**

- Field 131, hours of care a week: the bands **"35 – 59 hours"** and **"50+"** overlap, so 50 to 59
  hours can be answered two ways. Almost certainly "35 – 49" was intended (the standard census
  banding). One-character fix.
- Field 133, life satisfaction: `type=number` with **`step=any`**, so 7.5 and 3.75 are accepted on a
  0-to-10 whole-number scale that feeds the automatic score. Set `step=1`. (Eleven radio buttons would
  be better still for this population, but that is an accessibility and usability argument, not a
  validation one, so it belongs in §10's audit rather than here.)
- Field 64, household income: the bands "£15,000 - £25,000" and "£25,000 - £35,000" are both
  inclusive, so exactly £25,000 falls in two of them. Making the upper bound exclusive ("£15,000 to
  £24,999") removes the ambiguity.

### Priority 3 — completeness, not correctness

**V-12. There is no way to save a part-finished application and come back to it.**

A 20-page form, for a population that often needs another person's help to finish, with Gravity Forms'
save-and-continue feature switched off. An applicant who stops to go and find their benefit details,
or who runs out of time, loses everything. That is a direct, mechanical cause of incomplete
applications — the applicant does not submit a partial form, they abandon it and start again later or
not at all.

**The fix:** enable save-and-continue, which emails a resume link. Two things must be got right if it
is switched on: the resume link and its email must contain **no personal data and nothing that
discloses what the form is about** (a subject line naming disability or grants is a disclosure to
anyone who can see a shared inbox), and a saved draft is personal data — often special-category
health data — held on the website, which needs a stated retention period. **Neither Revitalise's
retention schedule (SDD §7.6) nor its Record of Processing Activities covers a website-held draft**,
so the DPO has to set that period before the feature is enabled. See OPEN-4.

**V-09. The narrative the trustee board decides on is capped at 325 characters.**

Field 88, "Please briefly explain how this break would benefit you", has `maxlength=325` — about
three sentences. The trustee board's decision rests on this answer (FR-035), and the Revitalise column
holds far more. Two smaller caps are worth a look at the same time: field 130 ("one brief example of
the level of care required") is capped at **180** characters, which is shorter than the example the
form itself offers underneath it; and field 92 (explain the exceptional circumstance) at 500.

**The fix:** agree the cap with Emily rather than with the theme's defaults, raise it, and — whatever
the number — show a live character count so an applicant is not silently cut off mid-sentence. Never
truncate silently: a truncated account of somebody's circumstances is lost information nobody knows
is missing.

### What the form already does well, and should not be changed

Worth saying, so the list above is not read as a verdict on the form:

- **Every "Other (please specify)" free-text box is correctly gated on its own "Other" option** — six
  separate rules, all right, including the two condition-detail fields that must not be crossed
  between the applicant and the person they support.
- **The consent gate on page 1** blocks the Continue button until the terms are accepted, rather than
  failing at the end.
- **Anti-spam is a honeypot field, not a CAPTCHA.** There is no reCAPTCHA, hCaptcha or Turnstile
  anywhere on the form. That is the right choice for this population and it should stay that way.
- **The equality-monitoring questions are optional, declinable, and carry an explicit statement that
  they will not affect the application.**
- **The help text is genuinely kind in places** — "You do not need to provide medical diagnoses or
  detailed symptoms", "You don't need to provide amounts or proof at this stage", "This is completely
  optional and will not affect your application decision". That tone is an asset.
- **The progress indicator states position in words** ("Step 1 of 20") and not only as a bar.

---

## 8. The payload contract as it really is — this is the D-003 fix

Test-agent defect **D-003** recorded that this document carried two contradictory statements of what
the intake requires: a banner naming six fields, and a rule elsewhere demanding all eleven scored
answers as non-null integers. Both were written against an imagined form. **Neither survives contact
with the live form, and the fix was to change the code, not to reconcile two invented numbers.**

### What the intake required before this revision, and why every real submission would have failed

The intake flow required six fields and rejected the payload with a 400 if any were empty:
`submission_id`, `first_name`, `last_name`, `email`, `postcode`, `date_of_birth`.

- **`date_of_birth` is never collected by the live form.** Not conditionally, not optionally — the
  field does not exist. **Every real submission would have been rejected**, 100% of them, with a 400
  and a log line saying the payload was incomplete.
- **`email` is only collected when the applicant picks Email as their preferred contact method**
  (V-01). Postal-preference applicants would have been rejected too.

That is the genuine mapping gap the reviewer asked about, and it was in the code, not only in the
document.

### What the intake requires now

| Required | Why it is safe to require |
|---|---|
| `submission_id` | The Gravity Forms Entry ID (CSV col 152). Always present. It is the unique key that makes a retry idempotent. |
| `first_name` | Field 15.3, unconditional and required on the live form. |
| `last_name` | Field 15.6, unconditional and required. |
| `postcode` | Field 14.5, unconditional and required. |

Everything else is **accepted but not required**. That is deliberate, and the reason is FR-010 and
FR-022: rejecting an application at the boundary *loses* it, whereas accepting it and withholding it
from automatic scoring routes it to a person. For an applicant, "handled by a human, slower" is a
vastly better outcome than "submitted successfully into nothing".

**In particular, and correcting D-003's second half: the eleven scored answers are NOT required.** If
one is missing the application is still created, and the scoring automation withholds the score and
notifies the process owner (FR-022). The eleven answers are all `*` on the live form, so in practice
they arrive — but the intake does not make that a condition of accepting an application.

### The rest of the contract

1. **One POST per submission**, `Content-Type: application/json`, UTF-8, **HTTPS with TLS 1.2 or
   higher** (C-TECH-003).
2. **`submission_id` must be identical on every retry.** `rev_sourcesubmissionid` is a unique key: a
   second post with the same id **updates** the existing application. A new id on a retry creates a
   duplicate, which means the applicant is assessed twice and someone unpicks it by hand.
3. **Omit a conditional field that was never revealed.** Do not send it as `null` or `""` — an
   omitted field and an empty answer mean different things, and the intake reads them differently.
4. Dates as ISO 8601 date-only (`YYYY-MM-DD`); timestamps as ISO 8601 with an explicit UTC offset.
5. Money as a **number**, two decimal places, no symbol, no separator. Booleans as JSON `true` /
   `false`. Multi-select as a JSON **array of integers**, even for one choice.
6. Free text as plain text, HTML and script stripped, the applicant's own line breaks preserved as
   `\n`. Sanitise and validate **server-side**, not only in the browser (C-TECH-004, HARD).
7. **Never send** `user_ip`, `user_agent`, `submission_speed`, `source_url`, or any payment field —
   CSV cols 155–163. Personal data with no purpose here (NFR-013).
8. **Never log a field value.** The website's logs may carry the `submission_id`, the timestamp, the
   HTTP status and the error message, and nothing else, at any log level including debug (C-DOM-004,
   HARD, NFR-012).

### Fields the intake accepts — 82 in total

`submission_id` · `title` · `first_name` · `last_name` · `email` · `phone` · `address_line` ·
`address_line2` · `town_city` · `postcode` · `date_of_birth` · **`age_range`** · `applicant_type` ·
`gender` · `privacy_notice_accepted_on` · `travelling_with_carer` · `carer_name` · `carer_support` ·
`helper_name` · `helper_email` · `helper_phone` · `helper_organisation` · `helper_relationship` ·
`support_recipient_name` · `support_recipient_condition_profile` ·
`support_recipient_other_condition_raw` · `condition_profile` · `other_condition_raw` ·
`needs_care_support_personally` · `care_support_description` · `narrative_raw` · `is_group_trip` ·
`group_member_names` · `break_type` · `other_break_type` · `break_location` · `break_start` ·
`break_end` · `provider_preference` · `accommodation_cost` · `travel_cost` · `other_cost` ·
`amount_requested` · `receiving_other_funding` · `other_funding_source` · `other_funding_amount` ·
`awaiting_decision_from` · `exceptional_funding_requested` · `exceptional_circumstance` ·
`other_exceptional_circumstance` · `exceptional_funding_detail` · `additional_amount_requested` ·
`received_funding_before` · `more_than_12_months_ago` · `income_band` · `receives_benefits` ·
`benefit_provider` · `currently_working` · `significant_care_costs` · `care_costs_explanation` ·
`savings_over_6000` · `unable_to_fund_explanation` · `grant_terms_consent` ·
`grant_terms_consent_date` · `age_confirmation_consent` · `age_confirmation_consent_date` ·
`applicant_consent` · `applicant_consent_date` · `helper_declaration_consent` ·
`helper_declaration_consent_date` · `would_like_form_posted` · `wellbeing_answer_1` … `_10` ·
`feeling_scale_answer`

**`age_range` is new in this revision.** It carries the label the live form sends, verbatim — "18-24",
"75 or over", "Prefer not to say" — and the intake maps it to `rev_agerange` through the
`AgeRangeLabelMap` configuration row, case-insensitively. The date-of-birth derivation is kept as a
fallback for a future form version that supplies one; when neither is available `rev_agerange` is set
to 9, "Not known", which is honest rather than a guess.

### Fields removed from the contract, and what happens if they are sent

| Removed | When | Why |
|---|---|---|
| `full_name` | rev. 0.2 | The full name is *calculated* from first and last name. A payload carrying `full_name` stores no name at all. |
| `costs` / any total | rev. 0.2 | `rev_costs` is calculated from the three component costs. |
| `financial_answers` | rev. 0.2 | Replaced by eight typed fields. |
| `wellbeing_answer_11` | rev. 0.2 | There are ten wellbeing statements, not eleven. |
| `referee_name`, `referee_email`, `referee_phone`, `emergency_contact_name`, `emergency_contact_phone` | rev. 0.3 | Collected on a separate form sent to the relevant party **after** the board approves the grant. Not this form's job, not this integration's data. The five columns remain as that form's destination. |
| **`group_linkage`** | **rev. 1.0** | CSV column 7, annotated by the charity as "Group Number - **generated** to link applications". It is the process owner's own admin grouping, assigned by hand after the fact. The form does not ask it and the website must not be able to write it. The intake no longer accepts it and no longer writes `rev_grouplinkage`. |
| `ethnic_group` | never accepted | Collected by the form, deliberately excluded from the schema pending SDD OQ-027. |

### What the live form sends that has no home, and what the intake accepts that never arrives

Both lists are in §9. They are decisions, not defects to fix quietly.

### Endpoint and authentication — still not decided

**TAD ADR-011 is open** (SDD OQ-014): shared-secret webhook, Entra ID OAuth client credentials, or a
scheduled REST pull. The intake's primary control today is the Power Automate trigger's own
"Specific users in my tenant" setting checked against `rev_IntakeAllowedClientId` — see the trigger's
description in the flow definition and `provisioning/entra/verify-intake-endpoint-auth.ps1`. The
payload shape above is unchanged under all three options (TAD ADR-011); only the transport differs.

---

## 9. Mapping gaps that need a decision — not fixed in this revision, and why

Each of these is a real disagreement between the live form and the Revitalise side. **None of them can
be closed by picking an answer**, which is why they are listed rather than resolved. They are ordered
by consequence.

| # | The gap | Why it cannot just be fixed | Who decides |
|---|---|---|---|
| **M-01** | **Condition profile: ten functional areas on the form (Vision, Hearing, Mobility, Dexterity, Learning, Memory, Mental health, Stamina, Socially/behaviourally, Other) against eight condition types in `rev_conditionprofile` (Physical disability, Sensory impairment, Learning disability, …, Autism, Other).** | The two lists classify along **different axes**. "Mobility" is not "Physical disability"; "Sensory impairment" covers two of the form's boxes; "Autism" is inside the form's "Socially or behaviourally" box together with ADHD. Any mapping loses or invents information, and this data is shown to trustees (TAD §3.1) and reported to funders. Either the option set changes to the form's ten, or the form changes to the schema's eight, or an explicit many-to-many map is agreed and written down. | Emily + reviewer. **Highest priority.** |
| **M-02** | **The three "last year" questions use a six-point agree/disagree scale with "Not sure"; `rev_likertresponse` has five frequency values.** | Answers 1–5 could be stored as-is, but they would then mean "Strongly disagree" while the same stored value on questions 1–7 means "None of the time" — the same number meaning two different things in the same table. Answer 6, "Not sure", has no value at all, and no defined contribution to the score out of 60. Revision 0.3 recorded these three as using the same frequency scale as the SWEMWBS items; the live form disproves it. | Emily + reviewer. Blocks the score's integrity, not just its storage. |
| **M-03** | **Income band: four bands with £15k/£25k/£35k boundaries against six with £10k boundaries and a "Prefer not to say".** | `rev_incomeband` feeds the income eligibility flag against the `IncomeCeiling` setting (FR-011 to FR-015), so a wrong mapping changes who qualifies. No band maps cleanly. Also, because the income question is only asked of applicants **not** on means-tested benefits (V-06), the eligibility check has no band at all for a large group. | Emily + trustee board |
| **M-04** | **Four financial questions are only asked of applicants not on means-tested benefits** (V-06): employment status, income band, significant care costs, and the £6,000 savings test. | This may be entirely deliberate — receiving a means-tested benefit is itself evidence of low income. But if it is deliberate, the Revitalise side must treat an absent income band as "qualifies on benefit status" rather than as missing data, or every benefit-receiving applicant is routed to manual review, which is the opposite of the programme's purpose. If it is *not* deliberate, the savings test is being skipped for the group it most applies to. | Emily first, then the scoring configuration |
| **M-05** | **`helper_relationship` is an option-set column; the form's "Relationship to you" is free text** ("e.g., family member, support worker, friend, carer."). | A free-text value cannot be written to a picklist. Either the form becomes a choice list (and OPEN-20's `rev_helperrelationship` values become real), or the column becomes text. Converting a picklist column to text is destructive and needs a decision, not a commit. | Reviewer |
| **M-06** | **`rev_breakstart` and `rev_breakend` cannot be populated** — one free-text "Provisional date" against two date columns. | Depends on V-04. Until the form supplies structured dates the two columns stay empty, and FR-001's "preferred holiday dates" is not satisfied by anything. | Emily via V-04 |
| **M-07** | **Break type: five options against nine in `rev_breaktype`. Exceptional circumstance: four against seven. Applicant type: three against four.** | The committed sets were written as placeholders (OPEN-20) and the live form now supplies the real lists. Trimming an option set is safe *before* any application exists and unsafe after, because renumbering changes what historic records mean. This is a before-go-live change and should be done deliberately, in one pass, with §6's tables as the source. | Reviewer, before go-live |
| **M-08** | **Other funding: three answers (Yes / No / "Applied and awaiting decision from") into a boolean.** | The third answer is the one the charity most needs to distinguish — it means "this may be funded elsewhere, do not decide yet". A boolean cannot carry it. `rev_awaitingdecisionfrom` captures *who*, but nothing captures *the state*. Note also that field 82 is **optional** on the form, so all three of its dependent fields can be skipped. | Emily + reviewer |
| **M-09** | **Collected by the live form, stored nowhere.** Preferred contact method (cols 26–28) · both "do you/they have a disability" gates (53, 68) · both "Brief confirmation" descriptions (65, 80) · the helper "Explanation" (49) · all ten care types plus Other and its text (81–92) · the brief example of care level (93) · **hours of care a week (94)** · all nine referral-source options plus its other text (138–147) · the applicant-typed total cost (122). | Roughly **30 of the 139 form columns have no destination.** Some are deliberate (the total is calculated; ethnic group is excluded pending OQ-027). Most are not decisions anybody made — they are the difference between a form built in one place and a schema built in another. Hours of care a week and the care-type profile are the notable losses: both describe the caring load, which is what the charity exists to relieve. Adding columns is a schema change with a real blast radius (entity XML, column security profiles, forms, views, retention), so it belongs in a planned pass, not a side effect of this one. | Emily + reviewer |
| **M-10** | **Accepted by the intake, never sent by the live form.** `title` (the Name field's Title sub-field is disabled) · `date_of_birth` · `privacy_notice_accepted_on` (the form has four declarations, none of them a privacy-notice acknowledgement) · `travelling_with_carer`, `carer_name`, `carer_support` (the columns added in revision 0.2 to close OPEN-2 — the live form never asks any of the three) · `support_recipient_name` (the person supported is never named) · `provider_preference` · `break_start`, `break_end`. | Harmless at runtime — the intake writes nothing when they are absent. But they are a **false record of what the system holds**: `rev_carername` exists, is secured, appears on forms, and will always be empty. Either the form starts asking, or these are marked as populated by another route, or they are removed. Note `rev_travellingwithcarer`'s own schema description still says the value is "worked out automatically from the intake answers", which nothing does. | Reviewer |

---

## 10. Accessibility — what has actually been checked, and what has not

This is test-agent defect **D-004**. The earlier revisions asserted that
`skills/accessibility-checklist.md` "applies in its entirety" while only requiring evidence for the
criteria listed in their own tables — so criteria absent from those tables were never evidenced, most
consequentially **WCAG 2.1 AA 1.3.5 Identify Input Purpose**.

**This section is deliberately not part of the change request in §7.** The reviewer's current ask of
Alex is validation and completeness. Accessibility is a different concern with a different fix, and
bundling an unaudited nine-item wish list into a validation request would weaken both. What follows is
therefore a **record**, not a request: one confirmed finding, and an honest statement of what nobody
has checked yet.

### Confirmed by direct inspection of the live page's HTML on 2026-08-13

| Criterion | State | Evidence |
|---|---|---|
| **1.3.5 Identify Input Purpose** | **FAIL** | Across **251 `<input>` elements**, the `autocomplete` attribute appears **five times**: once as `new-password` on the anti-spam honeypot, and four times as `autocomplete='off'`. **Not one field carries a valid purpose token** — no `given-name`, `family-name`, `email`, `tel`, `address-line1`, `address-line2`, `address-level2` or `postal-code` anywhere. Browser and assistive-technology autofill therefore cannot help on any of the identity fields, and four inputs actively suppress it. |
| **3.1.1 Language of page** | PASS | `<html lang="en-GB">` |
| **2.4.1 Bypass blocks** | PASS (skip link present) | `href="#main">Skip to main content` |
| **1.3.1 / 3.3.2 label association** | Largely PASS | `<label for=` appears **132 times**; the Likert grids use `aria-labelledby` pointing at row and column headers, which is the correct pattern for a matrix. |
| **3.3.8 Accessible authentication (minimum)** | PASS | No reCAPTCHA, hCaptcha or Turnstile anywhere. Anti-spam is a honeypot text field. Correct for this population. |
| **3.3.7 Redundant entry** | **FAIL** | Both email fields are two-box "Enter Email / Confirm Email" pairs (fields 19 and 43). WCAG 2.2's 3.3.7 exists to stop exactly this. |
| Required-field convey­ance | Note, not a verdict | Required state is conveyed by `aria-required` (47 occurrences) and a visible `*` with an "indicates required" legend. The native HTML `required` attribute is **not used at all**. `aria-required` is valid and the legend is present, so this is not a failure — but it means the browser's own required-field enforcement is not a second line of defence. |

**The one thing worth writing down as a future request, when accessibility is the subject:** adding
`autocomplete` tokens is a small, bounded change with a disproportionate benefit for this population.
The fields that need one are the identity fields and nothing else — first name (`given-name`), last
name (`family-name`), email (`email`), phone (`tel`), street address (`address-line1`), address line 2
(`address-line2`), town or city (`address-level2`), postcode (`postal-code`), and, if a date of birth
is ever added, `bday`. **Do not add tokens to the health, financial or wellbeing questions** — an
autofill token on a disability or income field would invite a browser to remember and re-offer
special-category data, which is worse than no token at all.

### What has NOT been checked, and cannot be claimed either way

None of the following can be established from static HTML, and no automated or manual audit has been
run on this form:

- **Colour contrast** (1.4.3, 1.4.11) — needs measurement of every text/background pair, control
  border and focus indicator.
- **Keyboard-only completion**, focus order and keyboard traps (2.1.1, 2.1.2, 2.4.3) across 20 pages.
- **Focus visibility** and whether focus is obscured by sticky elements (2.4.7, 2.4.11).
- **Zoom and reflow** at 200% and 320 CSS pixels wide (1.4.4, 1.4.10) — the Likert matrices on page 11
  are the obvious risk.
- **Screen-reader behaviour** (4.1.3, 1.3.1 in practice) — whether conditional reveals are announced,
  whether the error summary is announced, whether the progress indicator conveys position.
- **Target sizes** (2.5.8) — whether every Likert cell and checkbox meets 24×24, let alone the
  project's stricter 44×44.
- **Error message quality and reading age** (3.3.1, 3.3.3, NFR-020) — the messages only appear on a
  failed submission, which a read-only fetch cannot produce.
- **Server-side validation and sanitisation** (C-TECH-004, HARD).

**Therefore: no conformance claim is made in either direction beyond the seven rows in the table
above.** `knowledge/technology/testing-tools.md` names axe-core plus a manual pass as the method for
this, and neither has been run. This is recorded as **OPEN-26**, unstarted, and the test report carries
D-004 as **PARTIAL**, not closed.

---

## 11. FR-001 to FR-006 against the live form

The FRs Automation #1 exists to satisfy, assessed against what the form actually does.

| FR | Requirement | State on the live form | Where |
|---|---|---|---|
| **FR-001** | Incomplete applications cannot be submitted | **Partially met, and over-met in the wrong places.** 61 of 71 question fields are required and per-page validation blocks progress. But the required set is wrong in both directions: it requires helper and exceptional-funding answers of applicants they do not apply to (V-03), and it does not require an email address (V-01), an age (V-02) or a usable break date (V-04). FR-001's own named mandatory list includes date of birth, which the form does not ask, and preferred holiday dates and provider preference, which it captures as one free-text answer. | §7 V-01 to V-05 |
| **FR-002** | Plain-English, field-specific error messages | **Not assessed.** Error messages are produced by Gravity Forms on a failed submission and cannot be read from a static fetch. The help text that *is* visible is genuinely plain and kind. | §10 |
| **FR-003** | Show only the questions relevant to the applicant | **Partially met.** 23 conditional rules exist and the fiddly ones — every "Other (please specify)", the two condition-detail fields — are correct. Four significant gates are missing entirely. | §5, V-03, V-05 |
| **FR-004** | Show progress through the form | **Met.** "Step N of 20" in words plus a percentage, on every page. | §3 |
| **FR-005** | Allow an applicant to save and come back later | **Not met.** Save-and-continue is not enabled. | V-12 |
| **FR-006** | Review screen with per-section edit before submission | **Not met.** There is no review screen; page 20 leads straight to submit. | §3 |

**FR-005 and FR-006 are the two the form does not implement at all**, and both bear directly on the
60% problem: no way to pause, and no chance to catch a mistake before it is submitted. V-12 covers
FR-005 because a save feature is a validation-adjacent change with a clear mechanism. FR-006 is a
larger piece of work and is left as a recorded gap rather than folded into a validation request.

---

## 12. Open items

Renumbered and restated against reality. Items the live-form evidence closes are struck through.

| Ref | Item | Who decides | Blocks |
|---|---|---|---|
| ~~OPEN-1~~ | ✅ **Closed, with one correction.** The seven SWEMWBS statements use exactly the confirmed five-point frequency scale, in the confirmed order, and `rev_likertresponse` matches. **But the three "last year" questions do not** — they use a six-point agree/disagree scale with "Not sure". That half reopens as **M-02**. The SWEMWBS licensing question (if Revitalise reports against national norms it needs a licence) is unchanged and blocks nothing. | — | See M-02 |
| ~~OPEN-2~~ | ⚠️ **Closed on the schema, void in practice.** `rev_carername` and `rev_carersupport` were added in revision 0.2, and the live form asks **neither**, nor whether a carer is travelling. See M-10. | Reviewer | — |
| ~~OPEN-3~~ | ✅ **Closed and confirmed against reality.** `rev_supportrecipientotherconditionraw` exists, and the live form's field 124 is correctly gated on the person-supported checkbox group, not the applicant's. | — | Closed |
| **OPEN-4** | **Retention for a website-held draft.** Not currently needed, because save-and-continue is off — but it becomes blocking the moment V-12 is done. Revitalise's retention schedule (SDD §7.6) covers submitted applications only; the RoPA does not record this processing at all. | DPO + Emily | **V-12** |
| **OPEN-5** | **The intake trust route — TAD ADR-011, SDD OQ-014.** Still open. Option A depends on Azure Key Vault, which is out-of-palette and unevidenced. | Reviewer / architect + Revitalise | §8 transport |
| **OPEN-6** | **The accessibility standard — SDD OQ-022, NFR-024, TAD ADR-020.** No source names one. ADR-020 recommends WCAG 2.1 AA plus six 2.2 AA criteria and is itself `Derived` and unconfirmed. | Revitalise + reviewer | §10's basis |
| **OPEN-7** | **Does Revitalise email the applicant a reference number?** FR-008 creates the reference and FR-009 notifies the process owner; nothing notifies the applicant. The live form's page 19 promises a "formal offer letter via post or email" if the application succeeds, which is a different thing. | Emily | Applicant communications |
| **OPEN-8** | **What the applicant is told about what happens next, and when.** No timescale exists in any source (SDD OQ-020, OQ-021, OQ-023). | Emily | Confirmation copy |
| ~~OPEN-9~~ | ✅ **Closed.** The eight financial questions match export columns 106–113 and each has a column. What the live form adds is **M-04**: four of them are only asked of applicants not on means-tested benefits. | — | See M-04 |
| **OPEN-10** | **The income band has no "Prefer not to say"** on the live form, and four bands rather than six. Confirm the intended bands and whether declining is allowed. Folded into **M-03**. | Emily | M-03 |
| ~~OPEN-11~~ | ✅ **Closed by the live form itself.** The standard amounts are stated on it: **£500** towards a respite break or holiday, **up to £100** towards a day trip or activity. Earlier revisions recorded that no source stated a maximum. What remains is the smaller question in **V-07**: should the form warn when a request exceeds those figures? | Emily | V-07 warning text |
| **OPEN-12** | **Is the narrative mandatory, and how long may it be?** It is required on the live form and capped at **325 characters**. The cap needs Emily's agreement, not the theme's default. | Emily | **V-09** |
| **OPEN-13** | **Minimum lead time for a break date.** No source states one, and the form cannot check anything at all today. | Emily | **V-04** |
| **OPEN-14** | **Under-18 applicants.** The live form gates on a required "18 or over" declaration and asks age band only optionally, while "age being under 18" is one of the charity's own non-qualification reasons. | Emily + DPO | **V-02** |
| **OPEN-15** | **The phone number and email address for the help route.** Needed for any error-message or help copy. | Emily | FR-002 copy |
| ~~OPEN-16~~ | ✅ **Closed.** The step order and grouping are no longer a proposal — §3 records the live form's 20 pages, and the progress indicator states "of 20" correctly. | — | Closed |
| **OPEN-17** | **Ethnic group — SDD OQ-027.** Settled on the facts: the live form collects it, optionally and declinably, with an explicit no-effect statement (§6). Still deliberately absent from the schema pending the DPO. The question is now "should we keep collecting it, and on what basis". | Emily + DPO | Confirmation only |
| **OPEN-18** | **Who signs off a change to the form, and against what.** ADR-020 notes that the highest-stakes surface is out-of-palette, so compliance depends on a third party, and that this "needs a named acceptance step". None exists. §7 is the first thing that will need one. | Revitalise | §7 acceptance |
| **OPEN-19** | **The form asks 71 question fields — 79 questions counting the Likert rows — across 20 pages, and nobody has decided that it should.** This is the same concern earlier revisions raised, now measured against the real form. Emily should say which questions can be dropped or deferred to after approval. V-03 and V-05 remove several *for the applicants they do not apply to*, which is the cheapest version of this and does not need the wider decision. | Emily + trustee board | Overall length |
| ~~OPEN-20~~ | ✅ **Closed.** All five option lists are in §6, read from the live form. They do not match the committed option sets — that is **M-07**, a different problem from the one OPEN-20 described. | — | See M-07 |
| **OPEN-21** | **Is the £6,000 savings threshold current?** It is the live form's own wording and is hard-coded in both the form and the column label. Note also M-04: the question is only asked of applicants not on means-tested benefits. | Emily | Wording |
| ~~OPEN-22~~ | ✅ **Closed and confirmed twice.** The live form's life-satisfaction field is `min=0 max=10`, and CSV column 10 is headed "Overall Circumstance Score (out of 60)". The Revitalise side is configured for 60. | — | Closed |
| ~~OPEN-23~~ | ✅ **Closed.** Referee and emergency contact are collected on a separate form after board approval; the live form asks for neither, which corroborates it. Who completes that separate form remains Automation #3's design question. | Automation #3 | Closed here |
| **OPEN-24** | **The exact wording of the four declarations** (grant terms, age confirmation, applicant consent, helper declaration). The live form carries all four and their text is static page copy that has not been reviewed here. Declaration wording has legal effect, and **none of these may be worded as consent to processing** — the lawful basis is legitimate interests with Art. 9(2)(b)/(h) for the health data (SDD §7.2). Note there is **no privacy-notice acknowledgement** on the live form at all, which is a separate gap. | Emily + DPO | Declaration copy |
| ~~OPEN-25~~ | ✅ **Largely closed by the live form's own copy.** Field 119 asks "Would you like the form posted to you?" with the help text *"If you will not be able to print this form yourself, please select 'yes'"*, and page 19 explains that a successful applicant receives a formal offer letter to sign and return. So the postal route is about the **offer letter**, not an alternative application channel. What remains is confirming that somebody acts on a "yes". | Emily | Confirmation only |
| **OPEN-26** | 🆕 **The accessibility audit has not been run.** axe-core across all 20 pages plus an error state, keyboard-only completion, NVDA + Chrome and VoiceOver + Safari, greyscale, contrast measurement, 200% zoom, 320px width, and a real Android and iOS device. Until it runs, no conformance claim is available beyond §10's seven confirmed rows. **This is test-agent D-004's remaining half and is why D-004 is PARTIAL, not closed.** | Reviewer to schedule; Revitalise + Alex to remediate | Any NFR-024 claim |
| **OPEN-27** | 🆕 **Is the country field's hidden "United Kingdom" value acceptable?** UK residence appears to be a qualifying condition (the charity's own non-qualification reasons name it) and the form cannot detect a non-UK applicant. | Emily | **V-11** |

### Related open questions already on the record

**SDD OQ-002** (the exact scoring methodology, including behaviour when a scored answer is missing) now
has a second dependency: M-02, because "Not sure" is an answer with no score. **SDD OQ-014** is
OPEN-5. **SDD OQ-022** is OPEN-6. **SDD OQ-027** is OPEN-17. **SDD OQ-004 to OQ-006** are DPO
decisions that gate the build as a whole (SDD §7.8) and must be closed before go-live.

---

## Document control

| | |
|---|---|
| Produced by | development-agent, 2026-08-10 (rev 0.1); 2026-08-11 (rev 0.2, schema revision pass); 2026-08-12 (rev 0.3, three reviewer answers); **2026-08-13 (rev 1.0, reframed as documentation of the live form)** |
| Status | **DOCUMENTATION**, not a specification. The form it describes is live. |
| Evidence | The live page's HTML and its embedded Gravity Forms conditional-logic map, fetched 2026-08-13; `docs/Import/Application Data Export(Sheet1).csv` (163-column inventory, `cp1252`, header plus one annotation row); the committed solution source |
| Derived from | SDD §1, §4 A, §4 B, §5, §6, §7; TAD §4, §4.1, §5.1, §6, §8, §12, ADR-011, ADR-020 |
| Constraints applied | C-TECH-003 (TLS), C-TECH-004 (input validation, HARD), C-DOM-004 (no personal data in logs, HARD), NFR-008, NFR-012, NFR-013, NFR-020, NFR-024 |
| What the live form contains | 20 pages · 94 field containers (20 section headers, 2 static HTML blocks, 1 honeypot) · **71 applicant-facing question fields**, 61 of them marked required, 10 optional · **79 distinct questions** counting the two Likert grids' 10 rows individually · 23 conditional-logic rules · no review screen · no save-and-continue · no CAPTCHA |
| Revision 1.0 summary | The premise was corrected: the form exists and this documents it (§0). §7 is a scoped validation and completeness change request for Alex, evidenced from the form's own markup and the charity's own "standard missing items" note — twelve items, priority-ordered. §8 states the real payload contract and records the code fix that goes with it: the intake no longer requires `email` or `date_of_birth` (neither is always collected), it now accepts `age_range`, and it no longer accepts `group_linkage` — **test-agent D-003 closed**. §9 lists ten mapping gaps that need a decision rather than a commit. §10 records one confirmed accessibility failure (`autocomplete` absent on all 251 inputs) and, honestly, everything that has not been audited — **test-agent D-004 PARTIAL, with OPEN-26 raised for the audit itself**. §6 closes OPEN-20 with the live form's real option lists, and OPEN-11, OPEN-16, OPEN-22 and OPEN-25 close on the form's own evidence. |
| Next step | Emily and the reviewer decide which of §7's twelve items to send to Alex, and in what order. §9's ten mapping decisions are separate and belong to the reviewer and Emily, not to Alex. §10's audit (OPEN-26) is separate again. |
