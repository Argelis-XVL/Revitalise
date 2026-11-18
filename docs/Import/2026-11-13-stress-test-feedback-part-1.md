# Stress-test feedback, part 1 (test period)

**Received:** 2026-11-13, from the reviewer (Argelis), relayed verbatim below.
**Source:** a Claude Cowork reconciliation of the reviewer's call notes against the call transcript
and the Granola summary *"Stress-Test Application Portal"*. The call was with Emily (Revitalise,
finance + process owner). This is the **first part** of the test-period feedback; more will follow.
**Status:** raw intake. Not yet triaged, not yet work items, not yet mapped to WBS tasks.

---

Your notes match what was agreed at the end of the call. Earlier in the call, though, several requests and open questions came up that aren't in your list.

**Your notes against the transcript**

| Your note | What was said | Verdict |
|---|---|---|
| Care Support N/A | Support Needs tab, "Type of care support". Emily confirmed the two applicant types: a carer applying for a disabled person, and a disabled person. | Covered |
| Finance N/A when receives benefits = yes | Income band and employment status. You also raised savings, because someone on benefits may still have savings. **Emily is checking whether the form asks about savings in that case.** | Covered, but the savings question is still open |
| Total costs not editable | Emily edits the cost lines on Break Details but Total Cost doesn't recalculate, and she can't override it. You said it's imported from the form, "so I either need to open that thing". | Your note records the problem, not the fix. Decide whether the field becomes editable or recalculates from the lines. |
| Security role on review table | Emily has no "New" button on Reviews. | Covered |
| DocuSign trigger → manual | Remove the trigger on grant creation. Replace it with a select-and-run action, like Finalize Decisions. You also floated sending the referee request email from Finalize Decisions, and said you'd scope it. Until the fix is in, Emily fills in referee details before running Finalize Decisions. | Covered, but the referee email idea and the scoping aren't in your notes |
| Casework handbook | Emily asked for two things: how to create a group (Group Linkage), and where the scoring and narrative scrubbing settings are. She also called the review-creation steps "great to add to the booklet". | Covered, but the specific content to add isn't listed |
| Views on review table | Emily's action: one view per workflow stage. | Covered (Emily owns it) |

**Missing from your notes**

1. **Portal visibility.** Applications show in the trustee portal once Eligible for Round = Yes, even with no review. You said "I think I need to reconfigure that", then asked Emily which she prefers. It was never settled, so confirm with her.
2. **Admin verdict button.** Emily, as admin, sees the pink verdict button on reviews where she isn't a trustee. You said it shouldn't show at all, and marked it as a later improvement.
3. **Safeguard against releasing the wrong application.** Emily asked for a second check, so an application can't reach the portal unless it's Eligible for Panel. You didn't have an answer during the call.
4. **Statistics scope.** Emily wants all-time statistics, including the total number of applications received. You agreed it needs reconfiguring and suggested a toggle between this round and all time.
5. **Historical count.** It's set to 730, but the real number is about 1,500. Emily is to give you the figure. Historical demographics would need a separate import.
6. **Start date format.** 15/12 may need to be entered as 12/15. Check this.
7. **Automating review creation.** You put this in the new year because it isn't in the current budget. It needs a table that stores the trustee rotation.
8. **Narrative scrubbing tuning.** "Friend" was changed to "person". Emily logs cases like this and you tune the settings. Possessive pronouns (they're/their) need watching.
9. **Test with realistic data.** Emily is to send a handful of real applications through the web form, then you delete them afterwards.
10. **Subject access request workflows** are built but not tested yet.
11. **Payments.** The payment process, providers and bank accounts are parked until later.
12. **Emily's step-by-step document.** She updates it and sends it to you.
13. **Follow-up.** Wednesday 18 Nov, 16:00 CET / 15:00 UK. You also said you'd update her over chat on the fixes.

One correction to my last answer: the Granola summary said "possibly savings". The transcript shows it's a specific open question for Emily, not a maybe.
