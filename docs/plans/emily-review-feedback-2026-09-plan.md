# Client Review Feedback — Triage Plan

**Feature slug:** `emily-review-feedback-2026-09`
**Produced by:** plan-agent (intake mode), 2026-09-11
**WBS task ids referenced:** 1.1, 1.2, 1.4, 2.6, 2.7, 4.2, 6.7, 6.8 — and `wbs:6.9`, which is not in
the accepted baseline (see *Baseline notes*, below)

<!-- id-allocation: none -->

> **Source:** adopted from `docs/Import/2026-09-07-08-emily-sheardown-review-feedback.md` on
> 2026-09-11 by plan-agent (intake mode). Original author: Emily Sheardown, Revitalise Respite
> Holidays. See the Adoption Report in the gate log.

> **This document triages. It authorises nothing.** Under `C-COM-002` work enters by WBS task id or
> by an approved change order. Sixteen of the thirty-nine items below map to no accepted task and
> are marked `change-order-candidate`; they go to `commercial-agent` before any delivery work starts.

---

## 1. What this document is, and the one rule it applies

Emily sent two emails. The first reviews the **Trustee Review Portal**; the second reviews the
**grant administrator model-driven app**. Together they contain **39 discrete items**. Every one is
listed in §3. None has been dropped. Three merges are declared in §2.

The resolution test applied to every item is a single question, and it is the WBS's own wording, not
a judgement:

> **Does the item change something the quoted task's own deliverable already produced?**
> Yes → `in-baseline`. No → `change-order-candidate`.

That test matters more here than usual, because the two rework tasks are narrower than they look:

| Task | What the accepted WBS says it reworks |
|---|---|
| **2.7** Process feedback + rework | *"Adjust **flow, views, and Settings** based on Emily's feedback."* |
| **6.8** Process feedback + rework | *"Adjust **screens, detail content and the decision form** based on **trustee** feedback."* |

2.7 does **not** say *forms*. That single word decides sixteen items: a change to the grant admin
app's tab-and-section layout is not a flow, not a view and not a Setting, and no other accepted task
covers the grant administrator model-driven app's form design. The app itself was delivered under
Phase 0 task 0.4 (*Dataverse solution + table schema*), which has no feedback loop.

This is the working hypothesis in the dispatch brief tested and **partly rejected**. Source 2's
*scoring-flow* items do land on 2.7, as predicted. Source 2's *form-layout* items do not land
anywhere.

---

## 2. Merges, and the two traps in the source

Three merges, each declared:

| Merged into | From | Why |
|---|---|---|
| **EF-02** | Source 1 opening (*"remove from the Trustees"*) + Source 1 comment 8 (*"Region shouldn't be visible for Trustees"*) | The same ask, stated twice within one email |
| **EF-01** | Source 1 opening (*"include this in the overall grant portal accessed by the grant admin"*) + Source 2 unlabelled item 5, first clause | Transcriber's note 2: one requirement, two surfaces |
| **EF-03** | Source 1 opening (*"a 'city' identifier using the postcode"*) + Source 2 unlabelled item 5, second clause (*"extended to cities using postcodes"*) | The same ask on two surfaces |

**Trap 1 — the auto-reject / auto-pass near-duplicate is not a duplicate, and one half is already
built.** The transcriber flagged that Source 2's unlabelled item and General item 1 carry the same
sentence against different buckets. They resolve differently: an **Auto-rejected Applications**
sub-area already exists under the **Casework** group in
`src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml`,
backed by the `AutoRejectedApplications` saved query. So EF-15 is answerable by showing Emily where
it is. There is **no** equivalent for auto-pass; EF-16 is real, small, and is a view — so it is the
one item of the pair that 2.7 covers.

**Trap 2 — Region and city are three separate items, not one.** Hiding region from trustees (EF-02)
is a **column-security** change. Showing region to the grant admin (EF-01) is a form change against
data that is already readable. Deriving a city from a postcode (EF-03) is a capability that does not
exist anywhere in this solution and needs an external reference dataset. They have three different
resolutions and three different owners.

---

## 3. The 39 items

**Size key.** `S` — a contained change to one surface. `M` — several surfaces, or one surface plus a
schema or reference-data change. `L` — new capability with an external dependency. Sizes are
relative shirt sizes for triage only; hours are `commercial-agent`'s to set against
`contract/wbs.json`, and this document states none (`C-COM-008`).

### 3.1 Source 1 — Trustee Review Portal (2026-09-07)

| Id | Source | What Emily asked for | Surface | Resolution | Proposed solution (business level) | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-01** | Opening + S2 unlabelled 5 | Region shown in the grant portal the grant admin uses | Grant admin app | `change-order-candidate` | Region is already captured and already readable by the grant admin — it is *Location Area* on the Applicant record. The ask is to surface it on the **Application** record, where casework actually happens. Add it, read-only, beside the applicant reference. Half of this item is answerable today (see §4a) | S | Bundle with EF-18, EF-38 — all three surface Applicant data on the Application record |
| **EF-02** | Opening + comment 8 | Region must not be visible to trustees | Column security (both surfaces) | `in-baseline` — **6.8** | **This is a permissions change, not a UI change.** `rev_locationarea` is currently unsecured, so trustees can read it from any surface — app, view, export or API. Hiding the column in the portal would leave the data reachable. Add `rev_locationarea` to the `REV_TrusteeRestricted` field-security profile, then remove the column from the portal list. Membership is the control and trustees are excluded by **not** being members | S | **Conflicts with the contracted deliverable.** WBS 6.2 specifies the list screen as *"applications with score, **region**, dates, status"*. This item removes something the customer accepted. Also: `rev_agerange` is unsecured on the same basis and Emily did not mention it — confirm whether the same reasoning applies |
| **EF-03** | Opening + S2 unlabelled 5 | A city identifier derived from the postcode, because the typed city field is unreliable | Intake flow + schema | `change-order-candidate` | **No city derivation exists.** The city a trustee or admin sees today is `rev_towncity`, the applicant's own typed answer — exactly the unreliable value Emily describes. Region (`rev_locationarea`) *is* derived from postcode at intake, so the pattern exists; a city needs a postcode→settlement lookup, which the region mapping does not contain. Proposal: derive a new *Derived City* value at intake alongside region, from a licensed postcode reference set, and report on the derived value only | **L** | **External dependency.** No postcode→city reference data exists in this repository, and the licensing of UK postcode data is not a decision plan-agent can make. See §4c. **Also needs a lawful basis recorded before design** — see §5, note 4 |
| **EF-04** | Comment 1 | Mirror the current Trustee Pack's setup and wording — simplified headings confuse trustees who see this once a quarter | Trustee portal | `in-baseline` — **6.8** | Re-label and re-order the detail screen's panels to follow the Trustee Pack the board already knows. The reasoning is sound and cheap to honour; the work cannot be scoped until the pack is in hand | M (unscoped) | **External dependency** — the current Trustee Pack is not in this repository. Emily must supply a copy. Blocks EF-07, EF-08, EF-09, which are individual instances of this same request |
| **EF-05** | Comment 2 | Notes compulsory for a rejection | Trustee portal | `in-baseline` — **6.8** | Notes are optional today on all three verdicts (`VerdictForm.tsx`, the *Notes (optional)* label). Make notes required when the verdict is **Reject**, with the same inline validation pattern the verdict radio already uses, and leave Approve optional | S | Ask Emily whether **Defer** should also require a note — a deferral that nobody can explain at the next round has the same problem she describes |
| **EF-06** | Comment 3 | *What is included in the anonymised narrative section?* | Trustee portal | `answer-only` | **Nothing, today, and that is by design.** The panel binds the redacted narrative column and nothing else. Narrative scrubbing (Automation #5) is deferred under the recorded exception `EX-003`, so the panel is permanently in its withheld state until that automation is built. Emily should know this before the trustee demo, because she may be expecting content | — | The answer is also a warning: `EX-003` states the exception clears only when Automation #5 lands **and** DPO sign-off arrives, *before any live trustee demo* |
| **EF-07** | Comment 4 | Move the full wellbeing answers lower down, show the actual questions and answers, keep only the score out of 60 at the top | Trustee portal + scoring flow | `in-baseline` — **6.8** and **2.7** | The wellbeing detail Emily can see is inside the *Score Breakdown* text, which the scoring flow writes and the portal renders in the second panel from the top. Two halves: the flow writes the breakdown with the **question text and the answer's label** instead of *"Wellbeing answer 3: response 2 = 4 points"* (that is 2.7); the portal shows the score alone at the top and the expanded breakdown further down (that is 6.8) | M | **Same underlying change as EF-24.** Do them once, for both surfaces |
| **EF-08** | Comment 5 | *Holiday Details* → *Application Details* | Trustee portal | `in-baseline` — **6.8** | Rename the panel heading | S | EF-04 — do it inside the Trustee Pack alignment so the wording is decided once |
| **EF-09** | Comment 6 | *Preferred Dates* → *Start* and *End Date* | Trustee portal | `in-baseline` — **6.8** | Rename and split the single row into two | S | **Conflicts with a known mapping gap.** Gap M-05/M-06 in the form validation spec records that the live form supplies one free-text *provisional date* and the two date columns therefore cannot be populated. Renaming now produces two permanently empty fields, which reads as a defect. Resolve the form's date capture first |
| **EF-10** | Comment 7 | Helper, referee and contact details should not be in the Trustee Portal | Trustee portal + column security | `in-baseline` — **6.8** | Two halves, and only one is cosmetic. The **names, emails and phone numbers** are already behind `REV_TrusteeRestricted` and render as withheld placeholders — removing the panel is presentation. But **Helper Organisation** and **Helper Relationship** are *not* in the profile and are genuinely readable by trustees today. Secure those two, then remove the panel | S | This is a live disclosure, not a preference. It should be secured whatever is decided about the panel |
| **EF-11** | Overview 1 | Remove *Days the round has been open* — not a representative figure | Portal landing screen | `change-order-candidate` | Remove the tile | S | **Two problems.** (a) *Applications per day* is computed from the same day count Emily calls unrepresentative — removing the days tile and keeping the rate is half a fix; ask whether both go. (b) The landing screen is `wbs:6.9` scope created by change order CO-001, not 6.1–6.8, and CO-001 has no rework task — see *Baseline notes* |
| **EF-12** | Overview 2 | Add wording for the wellbeing question 8, 9 and 10 statistics, and the circumstance score | Portal landing screen | `change-order-candidate` | Label the three "last year" charts with their full question text, and add a circumstance-score distribution to the round statistics | S/M | Same `wbs:6.9` / CO-001 problem as EF-11. The question text is the same text EF-07 and EF-24 need — decide it once |

### 3.2 Source 2 — Grant administrator application (2026-09-08)

| Id | Source | What Emily asked for | Surface | Resolution | Proposed solution (business level) | Size | Depends on / conflicts with |
|---|---|---|---|---|---|---|---|
| **EF-13** | Overall 1 | A simple end-to-end process flow of how the application process works in the new system | Documentation | `change-order-candidate` | **A process flow already exists** — `docs/Import/Revitalise-Process-Flow-v0.1.html`, a July 2026 draft. It can be sent today (see §4a), but it is stale: it says the application *"lands in SharePoint"*, which is not what was built. Refresh it to as-built and re-issue | S | No accepted task covers a client-facing process document. Task 0.1 delivered the internal solution architecture and is complete |
| **EF-14** | Overall 2 | Some sections show a locked symbol — will the grant admin receive all access? | Access model | `answer-only` | **Yes, with one deliberate exception.** The padlock marks a column-secured field. The grant admin role is a member of the profile that releases them, so the values are readable. The exception is **bank account and payment data**, which sits behind a second profile the grant admin is deliberately excluded from — separation of duties, so that whoever assesses a grant is not the person who can see where the money goes | — | Worth stating positively to Emily rather than as a limitation; it is a control she benefits from |
| **EF-15** | Unlabelled 1 | Auto-reject cases added as a category under *Casework* for sense-checking | Grant admin app | `answer-only` | **Already built.** *Auto-rejected Applications* is a sub-area under the Casework group, backed by its own saved view | — | Confirm with Emily that this is what she meant; if she means a different sense-check *workflow* rather than a queue, it reopens as new scope |
| **EF-16** | General 1 | Auto-pass cases added as a category under *Casework*, to check free-text answers are sufficient | Grant admin app | `in-baseline` — **2.7** | Add an *Auto-pass Applications* saved view and a Casework sub-area beside the existing three. A view is exactly what 2.7 covers | S | The sub-area is sitemap content rather than a view; that is the one stretch in this row and `commercial-agent` may take a different view of it |
| **EF-17** | Unlabelled 2 | A section at the end containing the full application | Grant admin app | `change-order-candidate` | A read-only *Full Application* tab rendering every captured answer in the order the applicant met them, so the admin can read the submission as submitted rather than as re-grouped for casework | M | Overlaps EF-37 (question wording) — the full-application view needs the form's own question text, which is the same work |
| **EF-18** | Unlabelled 3 | Include personal details in the application — name, address, email | Grant admin app | `change-order-candidate` | Surface the applicant's identity fields on the Application record, read-only, via the existing applicant link. The data exists and the grant admin can already read it; it is one click away rather than on the page | S | Bundle with EF-01 and EF-38. **Note the design intent being traded off:** the Application record deliberately shows a pseudonymised reference, and the separation is what makes the trustee portal safe. Putting names on the Application form is safe *only* because column security, not form design, is the control |
| **EF-19** | Unlabelled 4 | *Quality Monitoring — where are these recorded?* | Grant admin app | `answer-only` | Read as **equality** monitoring: gender and ethnic group, both captured on the Applicant record, both column-secured, both readable by the grant admin. Neither ever reaches scoring or eligibility | — | Confirm the reading. If Emily means **quality** monitoring — a service-quality or complaints record — nothing of that kind exists and it is new scope |
| **EF-20** | General 2, first clause | *Intake Review Note — assuming I will have access to all of these?* | Grant admin app | `answer-only` | Yes. The column is secured and the grant admin role is a member of the profile that releases it | — | Same answer as EF-14 |
| **EF-21** | General 2, remainder | Selectable categories in the Intake Review Note as well as free text — e.g. Location, Date, Amount | Grant admin app | `change-order-candidate` | Add a *Review Note Category* choice column beside the existing free-text note, so notes can be counted and the charity can see where applications most often need chasing. Her stated reason — spotting where improvements are needed — is a reporting requirement, so the categories should be a managed list, not free text | S | Needs the category list from Emily. A new column is not a flow, a view or a Setting, so 2.7 does not reach it |
| **EF-22** | General 3 | Split the scoring section into three: Life satisfaction / In the last 2 weeks… / In the last year… | Grant admin app | `change-order-candidate` | Split the single *Scoring* section into three, matching how the questions are actually asked. The form already carries the full question text on each field, so this is a regrouping only | S | The cheapest of the grant-admin form items. **Note a real data issue underneath it:** the three "last year" questions use a different answer scale from the seven "last 2 weeks" questions (gap M-02), which is precisely why grouping them separately is the right presentation |
| **EF-23** | General 4a | *What does "No Rounding was Applied" mean?* | Scoring flow | `answer-only` | It means the score was already a whole number. **It is now the only message that can ever appear:** the other branch existed for half-points from a *Not sure* answer, and *Not sure* was set to zero, so no fractional total is possible. The sentence therefore tells the reader nothing. Remove it — a one-line change to the flow, inside 2.7 | S | The removal is `in-baseline` 2.7 even though the question is answer-only |
| **EF-24** | General 4b | Break the score breakdown down by question — *"I've been feeling optimistic about the future: response 1 = 5 points"* | Scoring flow | `in-baseline` — **2.7** | Emily has written the target format herself. Today the flow writes *"Wellbeing answer 3: response 2 = 4 points"* — a question number and a response number. Change it to write the question text and the answer's label | S | **Same change as EF-07.** One flow edit serves the admin app and the trustee portal |
| **EF-25** | General 4c | *Knockout* → *Low band* | Scoring flow + Settings | `in-baseline` — **2.7** | Change the word wherever it is shown to a person: the score-breakdown text and the Setting's display label | S | Change the **label**, never the Setting row's name — the flow looks the threshold up by name, and renaming the row silently breaks scoring |
| **EF-26** | General 5 | *What does the "Override" section show?* | Grant admin app | `answer-only` | It records a manual override of the automated outcome by the process owner: whether the status was overridden, by whom, when, the reason given, and the decision date. The process owner may override any automated outcome and does not re-score by hand | — | Worth pairing with the answer to EF-34, which increases how often an override will be needed |
| **EF-27** | General 6 | An *action completed* record for safeguarding incidents | Grant admin app | `change-order-candidate` | Add an action-taken record beside the existing safeguarding flag and notes — what was done, by whom, when. Her reason is record-keeping, which means it needs a date and an owner, not a tick | S | New columns. Must be secured on the same basis as the existing safeguarding fields |
| **EF-28** | Eligibility 1 | Move means-tested benefits to the front — a *yes* means income, employment and savings are never asked | Grant admin app | `change-order-candidate` | Reorder the Income section so the benefits question leads, with the four dependent questions grouped beneath it. Emily's description of the conditional logic is **exactly right** and is already documented as rule V-06 in the form validation spec | S | **Raises an open decision the spec already carries (gap M-04):** because those four questions are skipped for benefit recipients, an absent income band must be treated as *qualifies on benefit status*, not as missing data — otherwise every benefit-receiving applicant is routed to manual review, which is the opposite of the programme's purpose |
| **EF-29** | Eligibility 2 | Income bands set as per the form | Schema + spec | `in-baseline` — **1.2, 1.4** | This is already a recorded open decision (gap M-03): the live form has **four** bands with £15k/£25k/£35k boundaries; the Dataverse column has **six** with £10k boundaries and a *Prefer not to say*. No band maps cleanly, and the boundaries overlap on the form. Emily's instruction resolves it — adopt the form's four bands | S/M | The **decision** is 1.2/1.4. The **schema change** that follows it is not covered by 2.7 (not a flow, view or Setting) and needs a home. Flag to `commercial-agent` with EF-30 |
| **EF-30** | Eligibility 3 | Employment status as a dropdown *as per form* | Schema + spec | `external-dependency` | **Cannot be closed from this repository, because two documents in it disagree about the live form.** The column was rebuilt on 2026-08-17 with five options, its own schema comment stating the form *"has always asked five options"*. The form validation spec, from an inspection of the live page, records field 63 as *"Are you currently working?" — Radio Yes/No*. One of the two is wrong and only the live form can say which | S once resolved | Transcriber's note 5 applies. Ground-truth against the live form or Alex's field export. See §4c |
| **EF-31** | Eligibility 4 | Automatic flag when the amount requested exceeds £500 for holidays/respite or £100 for day trips/activities **and** no exceptional funding request was made | Scoring flow + Settings | `in-baseline` — **2.7** | A new eligibility flag alongside the existing income flag: compare the requested amount against a threshold chosen by break type, and raise the flag only when no exceptional funding request accompanies it. Both thresholds belong in Settings, adjustable by the process owner, exactly as the knockout threshold and income ceiling already are | M | **The largest stretch of 2.7 in this plan, and I am flagging it rather than hiding it:** 2.4 delivered *"compare score to threshold, set status, check income ceiling"*, and this is a different check, not an adjustment of that one. It also needs a column to hold the flag. `commercial-agent` may reasonably call it new scope. **Blocked by EF-32** |
| **EF-32** | Eligibility 4, tail | *Unsure how "other" should be treated* — typically the explanation falls within the above categories and the admin can amend | Business rule | `answer-only` | The question is which threshold applies when the break type is *Other*. Emily has effectively answered it: the admin re-classifies. Proposal to confirm by return — *Other* takes **no automatic threshold**, and the flag is raised for manual review instead. That is the safe default and matches what she says already happens | — | **Blocks EF-31.** The rule cannot be built until this is confirmed |
| **EF-33** | Eligibility 5 | Costs and Funding moved into the *Break Details* section | Grant admin app | `change-order-candidate` | Move the Costs and Funding section from the Eligibility & Finance tab to the Break Details tab | S | Presentation only — no automation reads a field's tab. Bundle with EF-22, EF-28 |
| **EF-34** | Eligibility 6 | A *No* to *previous funding more than 12 months ago* should be auto-rejected — applicants may apply every 12 months | Scoring flow | `in-baseline` — **2.7** | The column exists and **no automation reads it**. Add the check to the flagging step: previous funding within twelve months sets the status to auto-reject | S/M | **Conflicts with an open compliance decision.** Whether automatic rejection may stand without human review is an open question for the DPO under the Data (Use and Access) Act 2025 (business rule BR-S10). Adding a second automatic rejection path widens the exposure of a question nobody has answered. Recommend routing this outcome to the process owner rather than closing the application, until the DPO decides |
| **EF-35** | Eligibility 7, first half | A new question on the application form: carers must confirm the person they support is over 18 | **Upstream WordPress form** | `external-dependency` | Alex adds the question to the live form; the spec and the field mapping are extended to match | S (ours) | Transcriber's note 6. This is Alex's work, and the intake contract cannot bind to a field the form does not send. The spec side is `in-baseline` — 1.1/1.2/1.4 for the specification, 4.2 for the mapping. See §4c |
| **EF-36** | Eligibility 7, second half | Show both age confirmations and the age range in the eligibility section, to sense-check answers that do not correspond | Grant admin app + schema | `change-order-candidate` | A new column for the second confirmation, plus both confirmations and the derived age range shown in the eligibility section rather than buried in Consent | S | **Blocked by EF-35** — there is nothing to store until the form asks. Note the existing *Age Confirmation Given* covers the applicant only |
| **EF-37** | Support Needs 1 | Show the questions as worded on the form — she cannot tell which is which | Grant admin app | `change-order-candidate` | Re-label the support-needs fields with the form's own question text, the way the scoring section's fields already are. *Narrative (Raw)*, *Care Support Description* and *Care Example (Raw)* are storage names, not questions | S | Overlaps EF-17. The scoring section is the worked precedent — it already carries full question text |
| **EF-38** | Support Needs 2 | Show whether the applicant is a disabled person, a carer, and so on | Grant admin app | `change-order-candidate` | The value exists — *Applicant Type*, with three options — but it lives on the Applicant record, not the Application. Surface it in the Support Needs section | S | Bundle with EF-01 and EF-18. **Note gap M-07:** the committed option list has three values against the live form's — confirm the list at the same time |
| **EF-39** | Consent 1 | Remove the date and time stamps — the consents are mandatory and completed at submission | Grant admin app | `change-order-candidate` | **Hide them from the form; do not delete the columns.** Emily is right that they add no value to a caseworker reading the record. But those timestamps are the charity's evidence of *when* each consent was given, which is what makes the consent demonstrable if anyone ever asks. Remove them from the form's layout and keep the data | S | **This is the one item where I recommend not doing exactly what was asked.** Deleting the columns would destroy a record the charity relies on, to save four rows on a form |

---

## 4. The three lists that need separate action

### 4a. Answerable by return email, at no build cost

Nine items. Six are questions Emily asked; three are things she asked for that already exist or exist
in part. Each answer below is grounded in this repository, not inferred.

| Id | The answer to send |
|---|---|
| **EF-06** | The anonymised narrative panel is empty today and will stay empty until narrative scrubbing (Automation #5) is built. That automation is currently deferred by a recorded, owned exception. **Say this before the trustee demo** — it is the item most likely to surprise the board |
| **EF-14** | The padlock means the field is individually protected rather than open to everyone with app access. The grant admin can read all of them. The single deliberate exception is bank and payment data, which only the finance role sees, so that the person assessing a grant is not the person who can see where money is paid |
| **EF-15** | Already built — *Auto-rejected Applications* sits under **Casework** alongside *Borderline* and *Under Review*. Worth a screenshot rather than a sentence |
| **EF-19** | Read as equality monitoring: gender and ethnic group, both on the applicant record, both protected, both visible to the grant admin, and neither ever used in scoring or eligibility. Ask her to confirm that is what she meant |
| **EF-20** | Yes — the intake review note is protected, and the grant admin is on the list of people it is released to |
| **EF-23** | It means the score was already a whole number. It is now the only message that can appear, because the answer that used to produce a half point is worth zero. We will remove the sentence |
| **EF-26** | It records a manual override of the automated outcome: whether it was overridden, by whom, when, why, and the decision date. It is how the process owner overrules the automation without re-scoring by hand |
| **EF-32** | Proposal to confirm: break type *Other* gets no automatic threshold and is flagged for manual review instead, since the admin re-classifies it anyway. **We need this answer before EF-31 can be built** |
| **EF-13** | A process flow already exists as a July draft and can be sent today, with the caveat that it predates the build and describes the intake landing in SharePoint rather than Dataverse. Offer it as an interim, and propose refreshing it |

### 4b. Change-order candidates — these go to `commercial-agent` before any delivery work (`C-COM-002`)

Sixteen items, in four natural bundles. Bundling matters: priced individually, sixteen small form
changes carry sixteen lots of overhead, and several of them touch the same form in the same place.

| Bundle | Items | What it is | Combined size |
|---|---|---|---|
| **A — Grant admin form reorganisation** | EF-01, EF-17, EF-18, EF-22, EF-28, EF-33, EF-37, EF-38 | One pass over the Application form: regroup the sections, re-label the fields with the form's own question text, surface applicant identity and type, add a full-application view. All presentation; no automation changes | **M** |
| **B — Grant admin new capture** | EF-21, EF-27, EF-36, EF-39 | Four schema-touching items: review-note categories, a safeguarding action record, the second age confirmation, and hiding (not deleting) consent timestamps | **S/M** |
| **C — Derived city** | EF-03 | New capability, external reference data, licensing decision. Should be priced alone — it is the only item here with an outside cost | **L** |
| **D — Landing screen and documentation** | EF-11, EF-12, EF-13 | Two changes to the round-statistics landing screen and one refreshed process-flow document | **S/M** |

**Bundle D needs a decision before it can be priced.** The landing screen was built under change order
CO-001 as `wbs:6.9`, and CO-001 has no rework task — so feedback on it is an amendment to CO-001, not
2.7 or 6.8 work. CO-001 already has two approved amendments, so the mechanism and the precedent exist.

### 4c. External dependencies, with their owner

| Dependency | Owner | Blocks | State |
|---|---|---|---|
| **The current Trustee Pack** — layout and wording | Emily Sheardown | EF-04, and through it EF-07, EF-08, EF-09 | Not in this repository. Request a copy |
| **The live form's employment-status question** — five options or a Yes/No | Alex (website) via Emily | EF-30 | **Two documents here disagree.** Only the live form or Alex's export settles it |
| **The live form's income bands** — confirmation of the four bands | Emily + trustee board | EF-29 | Already a recorded open decision (gap M-03). Emily's instruction resolves the direction; the board sets the boundaries because they move who qualifies |
| **A new age-confirmation question on the form** | Alex (website) | EF-35, EF-36 | Not yet built. Announced by Emily, not scheduled |
| **Postcode→city reference data** and its licence | Reviewer / Revitalise | EF-03 | Does not exist here. A licensing and cost decision, not a design one |
| **Structured break dates on the form** | Emily via Alex | EF-09 | Recorded as gap M-06. Until the form supplies two dates, renaming the field produces two empty boxes |
| **DPO decision on automatic rejection** under the Data (Use and Access) Act 2025 | DPO via Emily | EF-34 | Open (business rule BR-S10). A second auto-reject path should not ship before it closes |

---

## 5. Baseline notes — three things `commercial-agent` and `pm-agent` should see

**1. Source 1 arrived before the task quoted to collect it.** Task 6.7 is *"Demo to trustees +
feedback — walk Kevin and other trustees through the app"*, and 6.8 reworks the app *based on trustee
feedback*. The ready-set walk shows 6.7 waiting on 6.6, which is blocked on Automation #5 and DPO
sign-off; 6.8 waits on 6.7. Emily is the business contact, not a trustee. So booking Emily's twelve
Source 1 items to 6.8 spends the rework task **before the trustees have said anything**, and a second
round of feedback is still owed under the same task. Either 6.8 is split, or Emily's round is
absorbed and the trustees' round needs somewhere to go.

**2. Source 2 is 2.6's own deliverable, and 2.6 is ready to start.** Task 2.6 is *"Walkthrough with
Emily"* and its deliverable is a feedback log. Emily's second email **is** that feedback log, arriving
without the walkthrough. 2.7 unblocks the moment 2.6 closes. This part of the dispatch brief's
hypothesis holds exactly.

**3. `wbs:6.9` is not in `contract/wbs.json`.** The baseline holds 61 tasks and 6.9 is not among them;
it was created by change order CO-001 for the landing screen. This matters to EF-11 and EF-12, whose
surface is that screen. It also means one statement in `contract/known-exceptions.json` — that
*"wbs:6.9 sits alongside 6.1-6.8 in contract/wbs.json"* — is not true of the file it names. Reported
here, not fixed: correcting the commercial record is `pm-agent`'s and `commercial-agent`'s, not
plan-agent's.

**4. Four items would create new personal data, and one of them needs a lawful basis decided before
it is designed.** EF-21 (review-note category), EF-27 (safeguarding action record) and EF-36 (second
age confirmation) are new fields about processing the charity already performs, under the basis
already recorded for the Application record. **EF-03 is different:** deriving a settlement from a
postcode creates a new, more precise location attribute about a data subject, for a purpose Emily
states plainly — *"allow us to be even more specific with our funders."* That is a funder-reporting
purpose, not a grant-assessment one, and it is the first item in this engagement to propose a new
derived personal attribute for a purpose outside the application decision. The lawful basis, the
retention position and the anonymised-statistics treatment all have to be settled in the design that
follows the change order, not assumed from region's. Raised here so it is not discovered later:
this plan records no lawful basis because it designs no entity, and EF-03 must not proceed to design
without one.

---

## 6. Recommended sequence

1. **Send the nine answers in §4a this week.** Nine of thirty-nine items close at no build cost, and
   two of them (EF-06, EF-32) are things Emily needs to know before anything else can proceed.
2. **Ask for the four things in §4c that are just requests** — the Trustee Pack, the employment-status
   ground truth, the income bands, and the *Other* break-type rule. All four block sized work.
3. **Close 2.6 against Source 2**, which unblocks 2.7, then run the five `in-baseline` scoring items
   (EF-16, EF-23, EF-24, EF-25, EF-34) with EF-31 held pending EF-32.
4. **Take the four bundles in §4b to `commercial-agent`** as one decision, not sixteen.
5. **Secure `rev_locationarea`, `rev_helperorganisation` and `rev_helperrelationship`** (EF-02, EF-10).
   These are the only items in this plan where the current state is a live disclosure rather than a
   preference, and they should not wait on the change-order conversation.
