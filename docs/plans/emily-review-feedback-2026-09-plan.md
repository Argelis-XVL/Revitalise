# Client Review Feedback — Triage Plan

**Feature slug:** `emily-review-feedback-2026-09`
**Produced by:** plan-agent (intake mode), 2026-09-11
**Revision 2**, 2026-09-11 — the central premise of revision 1 was corrected by the reviewer. See §1.

<!-- id-allocation: none -->

> **Sources:** adopted from `docs/Import/2026-09-07-08-emily-sheardown-review-feedback.md` (Emily
> Sheardown's two review emails) and ground-truthed against
> `docs/Import/2026-09-11-live-application-form-capture.md` (the live application form, fetched
> 2026-09-11). Adopted by plan-agent in intake mode.

> **This document triages. It authorises nothing.** Under `C-COM-002` work enters by WBS task id or
> by an approved change order. After revision 2, **one** item maps to no accepted scope and **one**
> more is half new; both go to `commercial-agent` before any delivery work starts.

---

## 1. The rule this document applies — corrected

**Rework of anything already built is quoted work, and draws on the relevant automation's
feedback/rework reserve.** A change-order decision is for genuinely **new capability** only.

Revision 1 applied a different and wrong rule. It read task 2.7's text — *"Adjust flow, views, and
Settings"* — noticed that it does not say *forms*, and concluded that re-laying-out the grant admin
app's form was unquoted work. Sixteen items were marked `change-order-candidate` on that basis.
**The reading was right and the conclusion was wrong.** The WBS is a costed estimate with headroom,
not an exhaustive enumeration of permitted work: a component does not need its own row to be in
scope, and feedback on something already delivered is expected work, not new work.

I tested that against `contract/wbs.json` this session rather than taking it on trust, and it holds:

- **Every one of the 61 accepted tasks carries an hours range, not a point figure.** There is not a
  single row where the low and high figures are equal. The range is the reserve.
- **Seven of the nine automations carry an explicit feedback, rework or iteration row** — A1, A2,
  A3, A4, A5, A6 and A7. Ten such rows in total, each with its own range.

**One gap, reported rather than smoothed over: A0 and A8 have no feedback or rework row at all.**
Automation 0 (Platform Foundation & Governance) is where the grant administrator application's
container was delivered — the solution, the schema and the forms, under task 0.4 — and Automation 8
delivers a payment capture form. Both are user-facing and neither has a reserve of its own. Three
items below land on A0 for want of anywhere better, and they are marked so `commercial-agent` can
see them as a set rather than one at a time.

### How an item is routed to a reserve

The grant administrator app's form renders columns owned by different automations, so the reserve
follows **the automation that owns the data on that part of the form**, not the form itself:

| What the item touches | Reserve it draws on |
|---|---|
| Scoring, the score breakdown, status, eligibility flags and thresholds | **A2** — 2.6 / 2.7 |
| Fields captured by the intake: their labels, grouping and presence on the form | **A4** — 4.5 |
| The upstream WordPress form's own questions and conditional logic | **A1** — 1.2 / 1.4 / 1.5 |
| The trustee review portal's screens and decision form | **A6** — 6.7 / 6.8 |
| The round-statistics landing screen | **`wbs:6.9`** — change order CO-001 |
| Solution-level schema and client-facing documentation | **A0** — 0.4 / 0.6 / 0.8, *which carries no reserve* |

### And one principle the form capture handed us

**Where Emily asks for a rename, prefer the live form's own wording.** She asks for *Holiday
Details* → *Application Details*; the form's section 13 is already called **Application Details**.
She asks for the support-needs questions "as is on the form"; the form's wording is now captured
verbatim. She asks to split the scoring into three sections; the form already presents them as
three. Her feedback is repeatedly asking our surfaces to match the vocabulary the applicant already
met. That resolves EF-08, EF-22 and EF-37 without a further round of questions.

---

## 2. Merges, and the traps in the sources

Three merges, each declared:

| Merged into | From | Why |
|---|---|---|
| **EF-02** | Source 1 opening (*"remove from the Trustees"*) + Source 1 comment 8 (*"Region shouldn't be visible for Trustees"*) | The same ask, stated twice within one email |
| **EF-01** | Source 1 opening (*"include this in the overall grant portal accessed by the grant admin"*) + Source 2 unlabelled item 5, first clause | Transcriber's note 2: one requirement, two surfaces |
| **EF-03** | Source 1 opening (*"a 'city' identifier using the postcode"*) + Source 2 unlabelled item 5, second clause | The same ask on two surfaces |

**Trap 1 — the auto-reject / auto-pass near-duplicate is not a duplicate, and one half is already
built.** An **Auto-rejected Applications** sub-area already exists under the **Casework** group in
`AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml`, backed by the
`AutoRejectedApplications` saved query. EF-15 is answerable by showing Emily where it is. There is
no equivalent for auto-pass, so EF-16 is real.

**Trap 2 — Region and city are three separate items.** Hiding region from trustees (EF-02) is a
column-security change. Showing region to the grant admin (EF-01) is a form change against data
already readable. Deriving a city from a postcode (EF-03) is capability that does not exist. Three
resolutions, three owners.

**Trap 3 — one of Emily's items is two requests.** *"Means tested benefits — can this be moved to
front? If they select yes they are not asked about income, employment status or savings."* The live
form capture shows it **is already first**, and that **nothing on the live form suppresses** income,
employment status or savings on a Yes. So the re-order is ours, and the suppression is Alex's and
not yet built. Split as EF-28 and EF-28b.

---

## 3. The 39 items

**Size key.** `S` — a contained change to one surface. `M` — several surfaces, or one surface plus a
schema change. `L` — new capability with an external dependency. Sizes are relative shirt sizes for
triage only; hours belong to `commercial-agent` against `contract/wbs.json`, and this document
states none (`C-COM-008`).

### 3.1 Source 1 — Trustee Review Portal (2026-09-07)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-01** | Region shown in the grant portal the grant admin uses | Grant admin app | `in-baseline` | **A4** — 4.5 | Region is already captured and readable by the grant admin as *Location Area* on the Applicant record. Surface it on the **Application** record, read-only, where casework happens. Half of this item is answerable today (§4a) | S | Bundle with EF-18, EF-38 — all three surface Applicant data on the Application record |
| **EF-02** | Region must not be visible to trustees | Column security | `in-baseline` | **A6** — 6.8 | **A permissions change, not a UI change.** `rev_locationarea` is unsecured, so trustees can read it from any surface — app, view, export or API. Hiding the column in the portal would leave the data reachable. Add it to the `REV_TrusteeRestricted` profile, then drop the column from the portal list | S | **Reduces a contracted deliverable.** WBS 6.2 specifies the list screen as *"applications with score, **region**, dates, status"*. Also check `rev_agerange`, unsecured on the same footing and not mentioned by Emily |
| **EF-03** | A city identifier derived from the postcode, because the typed city field is unreliable | Intake flow + schema | **`change-order-candidate`** | — | **No city derivation exists.** The city shown today is `rev_towncity`, the applicant's own typed answer — exactly the unreliable value Emily describes. Region *is* derived from postcode at intake, so the pattern exists, but the region mapping holds no settlement data. Derive a *Derived City* at intake from a licensed postcode reference set and report on the derived value only | **L** | **The one item that survives revision 2 as genuinely new.** It needs external reference data nothing in the baseline provides, and a licence. Also needs a lawful basis before design — §5 note 4 |
| **EF-04** | Mirror the current Trustee Pack's setup and wording — simplified headings confuse quarterly readers | Trustee portal | `in-baseline` | **A6** — 6.8 | Re-label and re-order the detail screen to follow the pack the board already knows | M (unscoped) | **External dependency** — the Trustee Pack is not in this repository. Emily must supply a copy. Partly overtaken by the form-vocabulary principle in §1, which already settles EF-08 |
| **EF-05** | Notes compulsory for a rejection | Trustee portal | `in-baseline` | **A6** — 6.8 | Notes are optional today on all three verdicts (`VerdictForm.tsx`, the *Notes (optional)* label). Require notes when the verdict is **Reject**, using the same inline validation the verdict radio already uses; leave Approve optional | S | Ask whether **Defer** should also require a note — a deferral nobody can explain at the next round has the problem she describes |
| **EF-06** | *What is included in the anonymised narrative section?* | Trustee portal | `answer-only` | — | **Nothing today, by design.** The panel binds the redacted narrative column and nothing else. Narrative scrubbing (Automation #5) is deferred under exception `EX-003`, so the panel stays in its withheld state until that automation is built | — | The answer doubles as a warning: `EX-003` clears only when Automation #5 lands *and* DPO sign-off arrives, before any live trustee demo |
| **EF-07** | Move the full wellbeing answers lower down, show the actual questions and answers, keep only the score out of 60 at the top | Trustee portal + scoring flow | `in-baseline` | **A6** — 6.8 and **A2** — 2.7 | The wellbeing detail she can see is inside the *Score Breakdown* text the scoring flow writes, rendered in the second panel from the top. Two halves: the flow writes the breakdown with the **question text and the answer's label** instead of *"Wellbeing answer 3: response 2 = 4 points"* (A2); the portal shows the score alone at the top and the expanded breakdown lower down (A6). The question text is now available verbatim from the form capture | M | **Same underlying change as EF-24.** Do it once, for both surfaces |
| **EF-08** | *Holiday Details* → *Application Details* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename the panel. **The live form's section 13 is already called "Application Details"** — she is asking the portal to match the form | S | Settled without further input, per the §1 principle |
| **EF-09** | *Preferred Dates* → *Start* and *End Date* | Trustee portal | `in-baseline` | **A6** — 6.8 | Rename and split the single row into two | S | **Blocked, and the form capture does not unblock it.** Gap M-06 records that the form supplies one free-text provisional date, so the two date columns cannot be populated; the capture does not quote a date field either way. Renaming now yields two permanently empty fields. Confirm the form's date capture before doing this one |
| **EF-10** | Helper, referee and contact details should not be in the Trustee Portal | Trustee portal + column security | `in-baseline` | **A6** — 6.8 | Two halves, one of them not cosmetic. The helper/referee **names, emails and phone numbers** are already behind `REV_TrusteeRestricted` and render as withheld placeholders — removing the panel is presentation. **Helper Organisation and Helper Relationship are not in the profile and are readable by trustees today.** Secure those two, then remove the panel | S | A live disclosure, not a preference. Secure it whatever is decided about the panel |
| **EF-11** | Remove *Days the round has been open* — not a representative figure | Landing screen | `in-baseline` | **`wbs:6.9`** — CO-001 | Remove the tile | S | **Ask whether both tiles go.** *Applications per day* is computed from the same day count Emily calls unrepresentative, so removing one and keeping the other is half a fix |
| **EF-12** | Add wording for the wellbeing question 8, 9 and 10 statistics, **and** the circumstance score | Landing screen | **split** — `in-baseline` + `change-order-candidate` | **`wbs:6.9`** / CO-001-A3 | **Wording half — in-baseline:** label the three last-year charts with their full question text, now available verbatim. **Circumstance-score half — new:** the round statistics carry exceptional-circumstance figures, a wellbeing comparison and four applicant-distribution charts; **there is no circumstance-score distribution**, and CO-001's priced chart list does not include one | S / S | **"Question 8, 9 and 10" needs her confirmation.** If the seven two-week statements are numbered 1–7, they are the three last-year statements — plausible, not certain, and a statistic should not be built on an assumption about which questions she means |

### 3.2 Source 2 — Grant administrator application (2026-09-08)

| Id | What Emily asked for | Surface | Resolution | Reserve | Proposed solution | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-13** | A simple end-to-end process flow of how the process works in the new system | Documentation | `in-baseline` | **A0** — 0.6 / 0.8 *(no reserve)* | **A process flow already exists** — `docs/Import/Revitalise-Process-Flow-v0.1.html`, a July 2026 draft. Sendable today (§4a) but stale: it says the application *"lands in SharePoint"*, which is not what was built. Refresh to as-built and re-issue | S | One of the three items landing on A0, which has no feedback row |
| **EF-14** | Some sections show a locked symbol — will the grant admin receive all access? | Access model | `answer-only` | — | **Yes, with one deliberate exception.** The padlock marks a column-secured field; the grant admin role is a member of the profile that releases them. The exception is **bank and payment data**, behind a second profile the grant admin is deliberately excluded from — so whoever assesses a grant is not the person who can see where the money goes | — | Worth stating as a control she benefits from, not as a limitation |
| **EF-15** | Auto-reject cases added as a category under *Casework* for sense-checking | Grant admin app | `answer-only` | — | **Already built** — *Auto-rejected Applications* sits under Casework, with its own saved view | — | Confirm this is what she meant. If she means a sense-check *workflow* rather than a queue, it reopens |
| **EF-16** | Auto-pass cases added as a category under *Casework*, to check the free-text answers are sufficient | Grant admin app | `in-baseline` | **A2** — 2.7 | Add an *Auto-pass Applications* saved view and a Casework sub-area beside the existing three | S | — |
| **EF-17** | A section at the end containing the full application | Grant admin app | `in-baseline` | **A4** — 4.5 | A read-only *Full Application* tab rendering every captured answer in the order the applicant met them, so the admin reads the submission as submitted rather than as re-grouped for casework. The form's own section order is now captured and can be followed exactly | M | Overlaps EF-37 — both need the form's question text, which is the same work |
| **EF-18** | Include personal details in the application — name, address, email | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the applicant's identity fields on the Application record, read-only, via the existing link | S | Bundle with EF-01, EF-38. **Note the design intent traded off:** the Application record deliberately shows a pseudonymised reference. Putting names on it is safe *only* because column security, not form design, is the control |
| **EF-19** | *Quality Monitoring — where are these recorded?* | Grant admin app | `answer-only` | — | **The form's final section is called Equality Monitoring** — gender and ethnic group. Both are on the Applicant record, both column-secured, both readable by the grant admin, and neither ever reaches scoring or eligibility. There is no section called *Quality* Monitoring on the form | — | Confirm the reading with her. If she means service-quality or complaints, nothing of that kind exists and it is new |
| **EF-20** | *Intake Review Note — assuming I will have access to all of these?* | Grant admin app | `answer-only` | — | Yes. The column is secured and the grant admin is a member of the profile that releases it | — | Same answer as EF-14 |
| **EF-21** | Selectable categories in the Intake Review Note as well as free text — e.g. Location, Date, Amount | Grant admin app | `in-baseline` | **A4** — 4.5 | Add a *Review Note Category* choice beside the existing free-text note, so notes can be counted and the charity can see where applications most often need chasing. Her stated reason is reporting, so the list should be managed, not free text | S | Needs the category list from Emily. Routed to A4 on the field's name (*Intake* Review Note); A2's 2.7 is the defensible alternative if `commercial-agent` reads it as post-scoring triage |
| **EF-22** | Split the scoring into three sections: Life satisfaction / In the last 2 weeks… / In the last year… | Grant admin app | `in-baseline` | **A2** — 2.7 | **This is the form's own structure** — one 0–10 scale, seven two-week statements on a 5-point scale, three last-year statements on a 6-point scale. Split the single *Scoring* section to match | S | **Underlines a real data issue:** the three last-year questions use a different answer scale from the seven two-week questions (gap M-02), which is exactly why grouping them separately is right |
| **EF-23** | *What does "No Rounding was Applied" mean?* | Scoring flow | `answer-only` | **A2** — 2.7 *(for the removal)* | It means the score was already a whole number. **It is now the only message that can appear:** the other branch existed for half-points from a *Not sure* answer, and *Not sure* is worth zero, so no fractional total is possible. The sentence tells the reader nothing — remove it | S | — |
| **EF-24** | Break the score breakdown down by question — *"I've been feeling optimistic about the future: response 1 = 5 points"* | Scoring flow | `in-baseline` | **A2** — 2.7 | Emily wrote the target format herself. Today the flow writes *"Wellbeing answer 3: response 2 = 4 points"* — a question number and a response number. Write the question text and the answer's label instead; both are now available verbatim | S | **Same change as EF-07.** One flow edit serves both surfaces |
| **EF-25** | *Knockout* → *Low band* | Scoring flow + Settings | `in-baseline` | **A2** — 2.7 | Change the word wherever a person sees it: the score-breakdown text and the Setting's display label | S | Change the **label**, never the Setting row's name — the flow looks the threshold up by name, and renaming the row breaks scoring silently |
| **EF-26** | *What does the "Override" section show?* | Grant admin app | `answer-only` | — | It records a manual override of the automated outcome by the process owner: whether it was overridden, by whom, when, the reason, and the decision date. It is how the process owner overrules the automation without re-scoring by hand | — | Pair with the answer to EF-34, which increases how often an override will be needed |
| **EF-27** | An *action completed* record for safeguarding incidents | Grant admin app | `in-baseline` | **A0** — 0.4 *(no reserve)* | Add an action-taken record beside the existing safeguarding flag and notes — what was done, by whom, when. Her reason is record-keeping, so it needs a date and an owner, not a tick | S | **The weakest in-baseline call in this plan, flagged so it can be overturned.** No accepted task mentions safeguarding at all — the existing flag and notes arrived with the 0.4 schema build. Completing a record the system already keeps reads as extension, not new capability, but `commercial-agent` may disagree. Secure the new fields on the same basis as the existing ones |
| **EF-28** | Means-tested benefits moved to the front | Grant admin app | `in-baseline` | **A4** — 4.5 | Re-order the Income section so the benefits question leads, with the dependent questions grouped beneath it. Our app currently puts Income Band first | S | **Raises gap M-04:** if the four dependent questions are ever suppressed, an absent income band must be read as *qualifies on benefit status*, not as missing data — otherwise every benefit-receiving applicant routes to manual review, the opposite of the programme's purpose |
| **EF-28b** | *"If they select yes they are not asked about income, employment status or savings"* | **Upstream WordPress form** | `external-dependency` | **A1** — 1.2 / 1.4 *(spec side)* | **This is not how the live form behaves.** The only field conditional on a Yes is the benefit provider; income, employment status and the savings question are all still asked. Emily is describing intended behaviour, not current behaviour. Alex adds the conditional suppression; we specify it | S (ours) | Blocks nothing today, but it changes what an empty income band means — see EF-28 |
| **EF-29** | Income bands set as per the form | Schema + spec | `in-baseline` | **A1** — 1.4 *(decision)* · **A2** — 2.7 *(implementation)* | **Now specifiable.** The live form has four bands: Under £15,000 · £15,000–£25,000 · £25,000–£35,000 · Over £35,000. Our column has six with £10,000 boundaries plus a *Prefer not to say* the form does not offer. Adopt the form's four. The boundaries overlap at £25,000 and £35,000 on the form, and how the income flag treats a boundary value stays a Revitalise decision | S/M | Closes recorded gap M-03's option list. The **scoring treatment** of the boundaries is what remains open |
| **EF-30** | Employment status as a dropdown *as per form* | Schema | `answer-only` | — | **Settled, and nothing needs to change.** The live form asks *"Are you currently working?"* with **five** options — Yes full-time · Yes part-time · No, unable to work due to disability/health/caring responsibilities · No, retired · No, other reason — which is exactly what `rev_employmentstatus` holds. The Yes/No recorded in the form-validation spec at its field-63 row is **stale** | — | This was *"not verified"* in revision 1. It is now verified against the form capture, and the schema was right |
| **EF-31** | Automatic flag when the amount requested exceeds £500 for holidays/respite or £100 for day trips/activities **and** no exceptional funding request was made | Scoring flow + Settings | `in-baseline` | **A2** — 2.7 | **Buildable from fields that already exist** — amount requesting, the exceptional-funding Yes/No, and Type of Break. Her thresholds group *Holiday accommodation* with *Respite care facility stay*, and *Day trips or outings* with *Activity or experience*. Both thresholds belong in Settings, adjustable by the process owner, exactly as the knockout threshold and income ceiling are | M | **Blocked by EF-32** — the *Other* break type has no threshold until she says what it should be |
| **EF-32** | *Unsure how "other" should be treated* — the explanation typically falls within the above and the admin can amend | Business rule | `answer-only` | — | She has effectively answered it: the admin re-classifies. Proposal to confirm by return — *Other* takes **no automatic threshold** and is flagged for manual review instead. That is the safe default and matches what she says already happens | — | **Blocks EF-31.** The rule cannot be built until confirmed |
| **EF-33** | Costs and Funding moved into the *Break Details* section | Grant admin app | `in-baseline` | **A4** — 4.5 | Move the Costs and Funding section from the Eligibility & Finance tab to Break Details | S | Presentation only — no automation reads a field's tab |
| **EF-34** | A *No* to *previous funding more than 12 months ago* should be auto-rejected — applicants may apply every 12 months | Scoring flow | `in-baseline` | **A2** — 2.7 | The column exists, the form asks the question, and **no automation reads it**. Add the check to the flagging step | S/M | **Conflicts with an open compliance decision.** Whether automatic rejection may stand without human review is open for the DPO under the Data (Use and Access) Act 2025 (rule BR-S10). A second automatic rejection path widens an unanswered question. Recommend routing this outcome to the process owner rather than closing the application, until the DPO decides |
| **EF-35** | A new form question: carers confirm the person they support is over 18 | **Upstream WordPress form** | `external-dependency` | **A1** — 1.2 / 1.4 · **A4** — 4.2 *(spec and mapping)* | **Confirmed genuinely absent.** The live form has *"I confirm I am 18 years of age or over"* for the applicant and no equivalent for the person supported. Alex adds it; we extend the spec and the field mapping | S (ours) | Blocks the second half of EF-36. The intake cannot bind to a field the form does not send |
| **EF-36** | Show both age confirmations and the age range in the eligibility section, to sense-check answers that do not correspond | Grant admin app | `in-baseline` | **A4** — 4.5 | Surface the existing applicant confirmation and the derived age range in the eligibility section rather than leaving them under Consent. The second confirmation follows when EF-35 lands | S | **Partly blocked by EF-35** — there is nothing to store for the carer confirmation until the form asks |
| **EF-37** | Show the questions as worded on the form — she cannot tell which is which | Grant admin app | `in-baseline` | **A4** — 4.5 | **Now specifiable to the word, and the cause is clearer than she realised.** The four confusable free-text questions are *"Please briefly describe how your disability affects you"* and *"please briefly describe the type of support you need"* (the **applicant**), against *"Please briefly describe how their disability affects them"* and *"Please provide one brief example of the level of care required"* (the **person supported**). Two are about a different person. Re-label with the form's wording and group them under headings that name whose disability is being described | S | Overlaps EF-17. The scoring section is the worked precedent — it already carries full question text |
| **EF-38** | Show whether the applicant is a disabled person, a carer, and so on | Grant admin app | `in-baseline` | **A4** — 4.5 | **No new question needed.** The form asks *"Are you"* — A disabled person / A carer applying on behalf of a disabled person / A carer applying for yourself — and the value is stored as *Applicant Type* on the Applicant record. Surface it in Support Needs | S | Bundle with EF-01, EF-18 |
| **EF-39** | Remove the date and time stamps — the consents are mandatory and completed at submission | Grant admin app | `in-baseline` | **A4** — 4.5 | **Hide them from the form's layout; keep the columns.** Emily is right that they add nothing to a caseworker reading the record, and they are also the charity's evidence of *when* each consent was given, which is what makes the consent demonstrable | S | **The one item where the recommendation is not to do exactly what was asked** — and the reviewer has agreed with that reading |

---

## 4. The three lists that need separate action

### 4a. Answerable by return email, at no build cost

Ten items. Two moved here in revision 2: **EF-30**, settled by the form capture, and **EF-19**,
which the capture grounds in the form's own section name.

| Id | The answer to send |
|---|---|
| **EF-06** | The anonymised narrative panel is empty today and stays empty until narrative scrubbing is built. That automation is deferred under a recorded, owned exception. **Say this before the trustee demo** — it is the item most likely to surprise the board |
| **EF-14** | The padlock means the field is individually protected rather than open to everyone with app access. The grant admin can read all of them. The single deliberate exception is bank and payment data, visible only to the finance role, so the person assessing a grant is not the person who can see where money is paid |
| **EF-15** | Already built — *Auto-rejected Applications* sits under **Casework** alongside *Borderline* and *Under Review*. Send a screenshot rather than a sentence |
| **EF-19** | The form's final section is **Equality** Monitoring — gender and ethnic group. Both are on the applicant record, both protected, both visible to the grant admin, and neither is ever used in scoring or eligibility. There is no section called *Quality* Monitoring. Ask her to confirm that is what she meant |
| **EF-20** | Yes — the intake review note is protected, and the grant admin is on the list of people it is released to |
| **EF-23** | It means the score was already a whole number. It is now the only message that can appear, because the answer that used to produce a half point is worth zero. We will remove the sentence |
| **EF-26** | It records a manual override of the automated outcome: whether it was overridden, by whom, when, why, and the decision date |
| **EF-30** | Employment status already matches the form exactly — the same five options, in the same order. Nothing to change |
| **EF-32** | Proposal to confirm: break type *Other* gets no automatic threshold and is flagged for manual review instead, since the admin re-classifies it anyway. **We need this before EF-31 can be built** |
| **EF-13** | A process flow exists as a July draft and can be sent today, with the caveat that it predates the build and describes the intake landing in SharePoint rather than Dataverse. Offer it as an interim and propose a refresh |

**Two more questions to put to her in the same email**, because building on a guess would be worse
than asking:

- **EF-12** — does *"wellbeing question 8, 9 and 10"* mean the three *last year* statements? It is
  the plausible reading if the seven two-week statements are numbered 1–7, but a statistic should
  not be built on an inference about which questions she means.
- **EF-11** — should *Applications per day* go as well? It is computed from the same day count she
  calls unrepresentative.

### 4b. Change-order candidates — to `commercial-agent` before any delivery work (`C-COM-002`)

**Revision 2 reduced this list from sixteen items to one and a half.** Fourteen moved to
`in-baseline` under the corrected rule in §1; the two below are what survives on the *new capability*
test, and the second is half an item.

| Item | Why it is genuinely new | Size |
|---|---|---|
| **EF-03 — derived city from postcode** | The only item in this plan that cannot be built from anything the baseline provides. It needs an external postcode→settlement reference set and a licence, neither of which exists here or is implied by any accepted task. Region's own derivation is no precedent: that mapping holds regions, not settlements. It also needs a lawful basis decided before design — §5 note 4 | **L** |
| **EF-12, second half — a circumstance-score distribution on the landing screen** | The round statistics carry exceptional-circumstance figures, a wellbeing comparison and four applicant-distribution charts. There is no circumstance-score distribution, and CO-001's priced chart list does not name one. An amendment to CO-001, for which **CO-001-A1 and CO-001-A2 are the established precedent** | S |

The wording half of EF-12 and all of EF-11 are rework of landing-screen content that is built, and
draw on `wbs:6.9`'s own range.

### 4c. External dependencies, with their owner

Two dependencies were **closed** in revision 2 by the live form capture and are struck from this
list: the employment-status question (five options — settled, see EF-30) and the income bands
(four bands — settled as an option list, see EF-29).

| Dependency | Owner | Blocks | State |
|---|---|---|---|
| **Conditional suppression of income, employment and savings on a benefits Yes** | Alex (website) | EF-28b | **Not built.** The live form asks all three regardless. Emily described it as current behaviour; it is not |
| **A carer age-confirmation question on the form** | Alex (website) | EF-35, and the second half of EF-36 | **Confirmed absent** from the live form. A genuine upstream addition, exactly as her email says |
| **The current Trustee Pack** — layout and wording | Emily Sheardown | EF-04 | Not in this repository. Request a copy |
| **The scoring treatment of the income-band boundaries** | Emily + trustee board | EF-29 | The option list is now known; how the income flag treats £25,000 and £35,000 exactly is a Revitalise decision |
| **Postcode→city reference data and its licence** | Reviewer / Revitalise | EF-03 | Does not exist here. A licensing and cost decision, not a design one |
| **Structured break dates on the form** | Emily via Alex | EF-09 | Recorded as gap M-06 and **not settled by the capture**, which quotes no date field. Confirm before renaming |
| **DPO decision on automatic rejection** under the Data (Use and Access) Act 2025 | DPO via Emily | EF-34 | Open (rule BR-S10). A second auto-reject path should not ship before it closes |

---

## 5. Notes for `commercial-agent` and `pm-agent`

**1. The reserve model holds, with one hole.** Every accepted task is a range and ten feedback,
rework or iteration rows exist across seven automations. **A0 and A8 carry none.** A0 delivered the
grant administrator app's container under task 0.4 and A8 delivers a payment capture form; both are
user-facing. Three items here land on A0 — EF-13 (documentation refresh) and EF-27 (a safeguarding
field group), plus EF-27's classification. Nothing in Emily's feedback touches A8, so the gap is not
urgent, but it is structural rather than accidental and will recur.

**2. Source 2 is 2.6's own deliverable, and 2.6 is ready to start.** Task 2.6 is *"Walkthrough with
Emily"* and its deliverable is a feedback log. Emily's second email **is** that feedback log,
arriving without the walkthrough. Closing 2.6 unblocks 2.7.

**3. Source 1 arrived in the intended order, not ahead of it.** Revision 1 recorded that booking
Emily's Source 1 items to 6.8 would spend the trustees' rework capacity early. **That finding is
withdrawn.** Process-owner-first, then trustees, is the intended sequence, and the trustee round is
expected to be light. What remains true and worth carrying: 6.7's deliverable is still trustee
feedback that has not been collected, and `EX-003` gates the trustee demo on Automation #5 and DPO
sign-off.

**4. Four items would create new personal data, and one needs a lawful basis decided before design.**
EF-21 (review-note category), EF-27 (safeguarding action) and EF-36 (carer age confirmation) are new
fields about processing the charity already performs, under the basis already recorded for the
Application record. **EF-03 is different:** deriving a settlement from a postcode creates a new, more
precise location attribute, for a purpose Emily states plainly — *"allow us to be even more specific
with our funders."* That is funder reporting, not grant assessment. The lawful basis, the retention
position and the anonymised-statistics treatment all have to be settled in the design that follows
the change order, not inherited from region's. This plan records no lawful basis because it designs
no entity; EF-03 must not proceed to design without one.

**5. `wbs:6.9` is not in `contract/wbs.json`.** The baseline holds 61 tasks and 6.9 is not among
them; it was created by change order CO-001 for the landing screen. This is why EF-11 and EF-12 route
to CO-001 rather than to 6.8. It also means one statement in `contract/known-exceptions.json` — that
*"wbs:6.9 sits alongside 6.1-6.8 in contract/wbs.json"* — is not true of the file it names. Reported,
not fixed: correcting the commercial record belongs to `pm-agent` and `commercial-agent`.

**6. Two defects the form capture turned up that Emily did not raise.** The live form's *hours of
care per week* list reads *9 hours or less · 10 – 19 · 20 – 34 · 35 – 59 · 50+* — the last two bands
overlap, and *50+* sits below *35 – 59*. **Our `rev_carehoursband` option set reproduces it exactly**,
defect included, so an applicant caring 55 hours a week can be recorded in either band and the data
cannot be aggregated. Raise it with Emily; do not silently normalise it.

---

## 6. Recommended sequence

1. **Send the ten answers in §4a and the two questions beneath them this week.** Ten of thirty-nine
   items close at no build cost, and two of them (EF-06, EF-32) are things Emily needs to know before
   anything else proceeds.
2. **Close 2.6 against Source 2**, which unblocks 2.7, then run the A2 items — EF-16, EF-22, EF-23,
   EF-24, EF-25, EF-29, EF-34 — with EF-31 held pending EF-32.
3. **Run the A4 form pass as one piece of work**, not nine: EF-01, EF-17, EF-18, EF-21, EF-28, EF-33,
   EF-36, EF-37, EF-38, EF-39 all touch the same form and several touch the same section.
4. **Secure `rev_locationarea`, `rev_helperorganisation` and `rev_helperrelationship`** (EF-02,
   EF-10). These are the only items where the current state is a live disclosure rather than a
   preference, and they should not wait on anything else.
5. **Take EF-03 and EF-12's second half to `commercial-agent`.** Two decisions, not sixteen.
6. **Ask Alex for the two upstream changes** (EF-28b, EF-35) so they can be specified into A1's spec
   review while the A2 and A4 passes run.
