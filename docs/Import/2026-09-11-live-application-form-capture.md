# Live application form — ground-truth capture, 11 September 2026

**Source:** <https://revitalise.org.uk/apply-for-funding/> — the application form currently in
production and in use by applicants.
**Captured:** 2026-09-11, by fetching and reading the live page.
**Captured because:** Emily's review feedback of 2026-09-08 says "as per form" three times, and
two documents in this repository disagreed about what the form actually asks
(`docs/development/revitalise-grant-automation-form-validation-spec.md` records field 63 as a
Yes/No; the column's own schema comment says five options). The form is the authority. This file
records what it says so the next session does not re-guess it — the
`platform-contract-guessed-not-groundtruthed` class, at ×58, in its business-contract form.

> **This is a capture with a date on it, not a permanent fact.** The form is a live WordPress page
> that Revitalise edit, and Emily's own feedback announces a change to it ("We will be adding an
> additional question"). Re-fetch before relying on it after any Alex/WordPress change. Where a
> figure derived from it is asserted anywhere, register it rather than restating it.

---

## What this capture settles

### 1. Employment status — five options, not Yes/No

> **"Are you currently working?"**
> - Yes, full-time
> - Yes, part-time
> - No, unable to work due to disability/health/caring responsibilities
> - No, retired
> - No, other reason

This resolves the documented disagreement **in favour of the schema comment**. The Yes/No
recorded in the form-validation spec is stale.

### 2. Income band — four bands

> **"Approximate household income (before tax)"**
> - Under £15,000 per year
> - £15,000 – £25,000
> - £25,000 – £35,000
> - Over £35,000

This closes the open gap recorded as M-03 in the form-validation spec. The boundaries are the
form's; the scoring treatment of them remains a Revitalise business decision.

### 3. Means-tested benefits — already first, but NOT yet suppressing anything

> **"Do you currently receive any means-tested benefits?"** — Yes / No
> Followed by **"Benefit provider"** (free text), conditional on Yes.

It is already the first question of the financial section, so Emily's "can this be moved to
front?" is satisfied on the *form*. But her second sentence — *"If they select 'yes' they are not
asked about income, employment status or savings"* — is **not** how the live form behaves today:
the only thing conditional on a Yes is the benefit-provider field. Income, employment status and
the savings question are all still asked.

**So this is two requests, not one:** re-order the panel in the Dataverse app (ours), and add
conditional suppression to the WordPress form (Alex's). Do not read the second as already done.

### 4. Age — the applicant confirmation exists; the carer one does not

> **"I confirm I am 18 years of age or over"** (checkbox)
> **"...would you be willing to share your age range?"** — 18-24 / 25-34 / 35-44 / 45-54 / 55-64 /
> 65-74 / 75 or over / Prefer not to say

There is **no** "confirm the person you support is over 18" checkbox on the live form. Emily's
request for one is a genuine upstream addition, exactly as her email says.

### 5. Disabled person vs carer — already captured

> **"Are you"**
> - A disabled person
> - A carer applying on behalf of a disabled person
> - A carer applying for yourself

Emily's "can we include whether they are a disabled person/carer etc." needs no new question — the
data is already collected.

### 6. Support-needs free text — the exact wording Emily could not tell apart

> **"Please briefly describe how your disability affects you. You do not need to provide medical
> diagnoses or detailed symptoms."** (applicant's own disability)
> **"If yes, please briefly describe the type of support you need. You don't need to provide
> intimate personal care details."** (conditional on "Do you require care support in your daily
> life?" = Yes)
> **"Please briefly describe how their disability affects them."** (the person supported, carer
> route only)
> **"Please provide one brief example of the level of care required"** (carer route only)

Her note — *"I'm not clear on which questions are which"* — is a labelling defect against four
similar free-text questions, two of which are about a *different person* from the other two.

### 7. Wellbeing — three blocks, matching Emily's requested split exactly

> **"Overall, how satisfied are you with your life nowadays?"** — scale 0–10
>
> **"Please say what best describes your experience of each over the last 2 weeks."** — 5-point
> (None of the time / Rarely / Some of the time / Often / All of the time), seven statements:
> I've been feeling optimistic about the future · I've been feeling useful · I've been feeling
> relaxed · I've been dealing with problems well · I've been thinking clearly · I've been feeling
> close to other people · I've been able to make up my own mind about things
>
> **"Thinking about the last year, have you been able to"** — 6-point (Strongly disagree /
> Disagree / Neutral / Agree / Strongly agree / Not sure), three statements:
> Go out and do something you enjoy? · Enjoy other people's company? · Have a break when you've
> needed one?

Emily's "split the scoring into 3 sections — Life satisfaction / In the last 2 weeks… / In the
last year…" is the form's own structure. Her separate reference to **"wellbeing question 8, 9 and
10"** is most plausibly the three last-year statements, if the seven two-week statements are
numbered 1–7 — **but confirm that with her before building a statistic on it.**

### 8. Amount requested and exceptional funding — both present, so Emily's flag rule is buildable

> **"Amount Requesting from Revitalise"** (currency)
> **"I'd like to make an exceptional funding request"** — Yes / No
> **"Type of Break"** — Holiday accommodation (hotel, cottage, caravan, holiday park) / Day trips
> or outings / Activity or experience (e.g. theatre, concert, attraction) / Respite care facility
> stay / Other (please specify)

Emily's rule — flag when the amount exceeds £500 for holidays/respite or £100 for day
trips/activities **and** no exceptional funding request was made — maps onto these three fields
with no new question. Note her thresholds group *holiday accommodation* with *respite care
facility stay*, and *day trips* with *activity or experience*; "Other" is the case she flagged as
undecided.

### 9. Previous funding — present

> **"Have you received funding from us before?"** — Yes / No
> **"Was this more than 12 months ago?"** — Yes / No (conditional on Yes above)

Emily's rule (a "No" to the 12-month question is an auto-reject) is buildable as stated.

### 10. "Quality Monitoring" is almost certainly **Equality** Monitoring

The form's final section is **Equality Monitoring**:

> **"Gender"** — Female / Male / Non-binary / Prefer to self-describe / Prefer not to say
> **"Ethnic group"** — Asian or Asian British / Black, African, Caribbean or Black British /
> Mixed or Multiple ethnic groups / White / Other ethnic group / Prefer not to say

Emily asked "Quality Monitoring - where are these recorded?". There is no section by that name.
Answer the question about Equality Monitoring, and confirm the reading with her rather than
assuming it.

---

## Full section list, in form order

1. Grant Terms and Conditions · 2. Personal Details · 3. Contact Details · 4. Age Confirmation ·
5. Who You Are · 6. Helper's Details *(conditional)* · 7. Disability Information (Applicant) ·
8. Care Support (Applicant) · 9. Disability Information (Person Supported) *(conditional)* ·
10. Types and Levels of Care *(conditional)* · 11. Current Circumstances · 12. Financial
Eligibility · 13. Application Details · 14. Estimated Cost Breakdown · 15. Exceptional Funding
Request *(conditional)* · 16. How Would This Break Help You? · 17. Group Application ·
18. Previous Funding · 19. How Did You Hear About Us? · 20. Revitalise Funding ·
21. Equality Monitoring

Note section 13 is already called **"Application Details"** on the live form — which is the exact
rename Emily asks for in the Trustee Portal ("Holiday Details – change to 'Application Details'").
Her feedback is asking the portal to match the form's own vocabulary.

### Other option lists captured, for completeness

- **Preferred contact method:** Email / Phone / Post
- **Conditions or illnesses affecting you** *(multi-select, asked twice — once for the applicant,
  once for the person supported)*: Vision (for example blindness or partial sight) / Hearing (for
  example deafness or partial hearing) / Mobility (for example walking short distances or climbing
  stairs) / Dexterity (for example lifting and carrying objects, using a keyboard) / Learning or
  understanding or concentrating / Memory / Mental health / Stamina or breathing or fatigue /
  Socially or behaviourally (for example associated with autism spectrum disorder (ASD) which
  includes Asperger's, or attention deficit hyperactivity disorder (ADHD)) / Other (please specify)
- **Type of care and support provided** *(multi-select, carer route)*: Personal care (washing,
  dressing, toileting, feeding) / Mobility assistance / Medication management / Household tasks /
  Managing appointments and healthcare coordination / Financial and administrative support /
  Emotional support and companionship / Supervision for safety / Communication support /
  Night-time care / Other (please specify)
- **Hours of care per week:** 9 hours or less / 10 – 19 hours / 20 – 34 hours / 35 – 59 hours / 50+
  *(captured as written — the last two bands overlap, and "50+" sits below "35 – 59". Raise it
  with Emily; do not silently normalise it into a clean ladder.)*
- **Savings:** "Do you have savings over £6,000?" — Yes / No
- **Other funding:** Yes / No / Applied and awaiting decision from
- **Exceptional circumstance:** Palliative care / Carer breakdown/urgent need / Severe financial
  hardship / Other (please specify)
- **How did you hear about us:** Google search / Social media (Facebook, Twitter, etc.) / Referral
  from another charity / Healthcare professional (GP, nurse, social worker) / Friend or family
  member / Local authority/council / Previous guest of Revitalise / Other (please specify) /
  Prefer not to say

### Conditional logic observed on the live form

Helper's Details ← "Is someone helping you complete this application?" = Yes ·
Disability Information (Person Supported) ← applicant is a carer ·
Types and Levels of Care ← applicant is a carer ·
Care-support description ← "Do you require care support?" = Yes ·
Exceptional Funding Request ← exceptional request = Yes ·
Group member names ← group trip = Yes ·
"more than 12 months ago" ← previous funding = Yes ·
Benefit provider ← means-tested benefits = Yes ·
Care/medical expenses explanation ← significant costs = Yes ·
"Other type of break" ← Type of Break = Other ·
Additional funding source/amount ← other funding answered Yes or Awaiting

**Nothing suppresses income, employment status or savings.** See point 3 above.
