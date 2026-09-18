# Email to Emily Sheardown — Grant Portal Feedback Response

**Produced by:** plan processing, 2026-09-17  
**For:** Emily Sheardown  
**Subject:** Grant portal — answers to your feedback + one live fix we found  
**Reviewer:** send after checking; see the open question at the end

---

Hi Emily,

We've been through your two emails and the walkthrough in detail. Most of what you asked is already in the plan and most of those are things we build, not ask about — so this email covers the things we can answer straight away.

---

## Things that are already there

**EF-15 — Auto-rejected applications:** This one's already built. There's an *Auto-rejected Applications* view under Casework alongside Borderline and Under Review. I'll send a screenshot so you can confirm it's what you were picturing.

**EF-30 — Employment status dropdown:** The five options in the form are exactly what the system holds — same values, same order. Nothing to change.

**EF-23 — "No rounding was applied":** We're removing this message entirely. The rounding it refers to was switched off last August (when we changed *Not sure* from half a point to zero, with your agreement), so there's nothing to round and nothing to say about it.

**EF-28b — Income questions skipping on benefits:** The form already does this. When someone answers Yes to receiving means-tested benefits, it skips income, employment status and savings. We confirmed it against all 63 Round 4 submissions — every single benefits-Yes application had those questions blank. The only change here is on our side (see below under "What we're fixing").

---

## What certain things are

**EF-14 — Locked padlock symbols:** The padlock marks a column that's individually protected rather than open to everyone with app access. You as grant admin can read all of them. The one deliberate exception is bank and payment data — that's behind a separate level of access that the grant admin role is excluded from by design.

**EF-19 — Quality Monitoring section:** The form's last section is *Equality* Monitoring — it captures gender and ethnic group. Both are protected, both visible to you as grant admin, and neither is ever used in scoring or eligibility. Let me know if that's what you were asking about.

**EF-20 — Intake Review Note:** This one is written by the system, not by a person. It records when an answer coming in from the web form didn't match any option we hold for that field — it logs the field name, the value that was sent, and that nothing matched. It'll be empty for most applications. Your new review checklist (the eight Yes/No boxes) is a completely separate section that you fill in yourself.

**EF-26 — Override section:** This records a manual override of the automated outcome — whether it was overridden, by whom, when, the reason, and the decision date.

**EF-45 — Automatic auto-reject reason:** Yes, this is feasible, and cheaper than it sounds. The scoring flow already evaluates each rejection condition in order and knows exactly which one fired at the moment it sets the status — we just aren't writing it down yet. We're adding it as a column, placed right beside the status on the Casework tab so a caseworker sees both at a glance.

---

## Answers we owe you

**EF-06 — Anonymised narrative panel:** The panel is empty today and will stay that way until we've built the narrative-scrubbing automation. That's a piece of work we've recorded and deferred — it needs to run before any applicant's own words can be shown to trustees, to ensure nothing identifiable gets through. We'll flag it well before any trustee demo.

**EF-48 — Exceptional funding reason (and why the pack shows it blank):** The reason *is* captured — the applicant's own explanation of their exceptional circumstance lands in a secured column when they submit. The reason it's blank in the trustee pack is the same as EF-06: free text the applicant wrote needs to go through the scrubbing step before trustees see it. What *we can* surface now is the category — Medical, Disability-related, etc. — which is not secured and is trustee-visible by design. We just haven't put it on the list they read. That part we'll fix. For the full explanation, the answer is the same deferred automation as EF-06, so we'll send both answers together rather than a fortnight apart.

---

## Things you can do yourself (no wait needed)

**EF-18 — Personal details in application views:** You don't need us for this one. In any application view, click *Add Columns → Related → Applicant* and you can put name, address or email straight onto the view in a few clicks, with no changes from our side and no wait. Happy to walk through it if useful.

---

## Things we're changing (just flagging, no action needed from you)

**EF-21 — The eight review checkboxes:** We're building all eight — Location, Date, Amount, Exceptional Circumstance, Disability Information, Care Information, Group, Age. You asked, so the answer is yes. Two things worth knowing: each box will start blank rather than pre-set to No, so an application you haven't reviewed yet won't look like one you checked and failed. And the checklist will sit directly above the control that releases an application to the trustees, so it runs exactly where you'd naturally run it.

**EF-29 — Income bands:** Your four bands (Under £15,000 / £15,000–£25,000 / £25,000–£35,000 / Over £35,000) match the form exactly. Our own setting still has the older five bands on £10,000 boundaries — that's a placeholder we put in before we had your answer. We're correcting it, and removing the *Prefer not to say* option the form never offered. Nothing to ask — just letting you know the option list you'll see will match your own.

**EF-40 — County:** County doesn't currently exist as a field. We're adding it as its own new column for you rather than repurposing the existing location field, so it won't clash with the region change on the trustee side. This one goes through our normal change-order process, so you'll see it priced separately rather than bundled in as a small change.

---

## What we found while checking your files

**EF-49 — A live error in region derivation (being fixed this week):** While we were checking your postcode file against our list, we found that five postcode areas were deriving the wrong region. The most obvious one: Blackburn (BB postcodes) was showing as West Midlands. That's because our lookup doesn't have an entry for BB, so it falls back to B for Birmingham. Canterbury and Hemel Hempstead were showing as *Not known*. We've corrected all five. Worth knowing because this affects what your trustees see in the location column today.

**EF-09 — Group 101's dates:** Checking the packs, Group 101 has a Start Date of 10 January 2027 and an End Date of 17 January 2026 — the end is fourteen months before the start. The form only asks for one free-text date field, so the start and end dates you see in the pack are entered manually with nothing checking them. Worth fixing at the form level, and in the meantime your new *Date* review box gives you a place to flag it before it goes to the board.

**EF-13 — Process flow:** There's a process flow document from July that we can send you now. It predates the build, so it still describes applications landing in SharePoint rather than in the system we built — worth treating as an interim. We'll refresh it to match what's actually been built.

---

## What we're changing on the landing screen (EF-11)

**Applications per day** is staying, but we're changing what it's calculated from. Right now it's driven by the current round's day count alone, which is the same figure you flagged as unrepresentative for the *Days the round has been open* tile. Instead we'll calculate it from every application the system has ever seen, broken down month by month, and call out any month that spikes or drops sharply against its preceding six. Because this system started granting later than the charity itself did, we'll also need two settings from you in due course: the date grants first started, and a total count of applications made before this system existed, so historic totals aren't understated.

---

## Scoring settings (EF-46) — we'd like to show you the numbers first

Before you confirm the threshold values, we'd like to put some real data in front of you, because the current provisional values behave quite differently in practice than they might look on paper.

Against all 63 Round 4 individual applications, the provisional settings produce:

| | Round 4 (63 individual) | Round 5 (12 group) |
|---|---|---|
| Auto-reject (score ≤ 20) | **1 application (2%)** | 0 |
| Borderline (21–30) | 11 (17%) | 1 (8%) |
| Auto-pass (> 30) | **51 (81%)** | 11 (92%) |

At a threshold of 20, one application in 63 is automatically rejected. That might be exactly right, or it might tell you the threshold needs adjusting. We wanted you to see the real round before you confirm the value rather than after.

One point on the income ceiling: 90% of Round 4 applications have no income band at all — because they answered Yes to means-tested benefits and the income questions were skipped. The system is currently recording those as "income not stated — cannot assess", which isn't accurate. We're fixing that separately: benefits-Yes applications will get their own flag ("Qualifies on means-tested benefits") so they don't get lumped in with genuine unknowns.

Could you review the scoring settings page in the system and let us know if you'd like to adjust any of the thresholds? We'll re-seed all the environments together once you confirm.

---

## On the *Other* break type threshold (EF-32)

You mentioned being unsure how *Other* should be treated for the >£500 / >£100 automatic flag. Our proposal: *Other* gets no automatic threshold and is flagged for manual review instead. To help you decide, the Round 4 numbers:

- 4 of 63 applications are *Other* break type
- Giving *Other* a £100 threshold: flags **2** of those 4
- Giving *Other* a £500 threshold: flags **0**
- No threshold for *Other*: flags **0** either way

The form change that creates the >£500 / >£100 flag on submission is going to your web developer — we'll send him a separate note with the exact wording.

---

Thanks Emily. Let us know on the threshold settings when you have a moment.

---

*Produced from `docs/plans/emily-review-feedback-2026-09-plan.md` §5a, updated against Revision 5
(reviewer decisions, 2026-09-18). Items addressed:*
*Answer-only: EF-06, EF-13, EF-14, EF-15, EF-18, EF-19, EF-20, EF-21, EF-23, EF-26, EF-29, EF-30, EF-32, EF-45, EF-48*
*Statements (findings/decisions from our side): EF-09, EF-11, EF-28b, EF-40, EF-49*
*Decision items: EF-46*
