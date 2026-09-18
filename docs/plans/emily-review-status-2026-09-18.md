# Emily Review — Status Brief and Decisions Needed

<!-- id-allocation: none -->

**Date:** 2026-09-18
**Covers:** `docs/plans/emily-review-feedback-2026-09-plan.md` (revision 4, 49 items) and the build
work done against it on 2026-09-17/18. Nothing here is committed yet — this is the state of the
working tree.

**Headline: roughly two-thirds of the buildable work is done and verified. One item is stopped on
a compliance decision only you can make. The rest is either correctly waiting on Emily/Alex, or
simply not started yet.**

---

## 1. Decisions needed from you

### 1a. Compliance sign-off: letting the scoring flow read benefit status (blocks EF-28b/M-04)

EF-28b's fix — the one already promised to Emily in the response email — makes the scoring flow
check `rev_receivesbenefits` before it derives the income flag, so a benefits-Yes application reads
"qualifies on means-tested benefits" instead of the wrong "not stated — cannot assess." **The logic
is built and correct**, but it trips two HARD build gates on purpose:

- `no-special-category-data-in-scoring` (FR-016, the Data (Use and Access) Act 2025 gate)
- `domain-invariants` (checks the compliance register against the gate)

Both exist specifically to stop an automated decision from silently using data SDD §7.1 classifies
at the highest restriction tier. `rev_receivesbenefits` is on that list. Unblocking these two red
gates means editing `constraints/domain/special-category-register.yml` — and that file's own header
says explicitly: **"Owner: Domain Owner / Compliance Lead — DPO notified for any change."** I did
not touch it.

**What I need from you:** confirm that reading `rev_receivesbenefits` for the income flag only
(never the circumstance score — I added a dedicated test that enforces that boundary) is an
acceptable, DPO-notifiable exception, the same tier of decision as EF-34's pending DPO sign-off.
If yes, I'll draft the register update for your review rather than apply it myself.

**Also needs the same sign-off, and is smaller:** six columns secured by this pass
(`rev_locationarea`, `rev_helperorganisation`, `rev_helperrelationship`,
`rev_safeguardingactioncompleted`, `-completedon`, `-completedby`) were never added to the
register's `pending_adjudication` list, which is a second, separate HARD-gate failure
(`domain-invariants`, "UNADJUDICATED-SECURED"). This is bookkeeping, not a new classification
question — but the same file, so the same rule applies.

### 1b. EF-40 (county) — the settled approach may not be buildable as written

The plan's own revision 4 records: *"county goes into the existing `rev_locationarea` column, for
the grant admin."* That column is a closed 13-value region Choice, not free text — it cannot hold a
county name without either becoming a different field or losing the region values it already holds.
The plan's own §4.4 flags this as a rider, not a settled mechanism: *"local authority is the better
attribute if funder reporting is the purpose."* **Nothing has been built for EF-40.** Before I build
anything, I need you to pick one:

- Reuse `rev_locationarea` for county anyway (requires redefining what the column means — a real
  option-set change, not the disclosure-only rework it was priced as), or
- Add a genuinely new `rev_county` (or `rev_localauthority`) column, which is a small schema change
  but no longer "no new column, no trustee-facing change" as recorded in §5b.

### 1c. EF-17 — section or tab, and whether to apply the form's own ordering

Emily's ask was one sentence: *"a section at the end that contains the full application."* Revision
4 flags two things as **ours, not hers**, that change the size and shape of the work: turning
"section" into a new tab (which now sits beside EF-47's Casework tab), and rendering every answer in
the form's own order (consistent with EF-22/EF-37, but not something she asked for). The plan says
explicitly this needs settling **before it is built or sized**. Nothing has been built.

### 1d. Change-order candidates — ready to route, waiting on your go-ahead to send them on

Three items are priced and ready for `commercial-agent`/your commercial process, per `C-COM-002`:
**EF-41** (postcode → location lookup, now split into a rework half and a genuinely-new half),
**EF-43** (group applications in the Trustee Portal, content settled by the delivered example),
**EF-12's second half** (a circumstance-score distribution chart, an amendment to CO-001). None of
these has had delivery work started against it, which is correct — but the routing step itself
(handing the three to commercial review) has not happened either. Say the word and I'll write it up.

---

## 2. What's fully built and verified

Everything below is in the working tree, not yet committed, and passes its own test suite:
**1,008 PowerShell tests, 751 TypeScript tests, and every build gate that doesn't depend on a live
tenant or the compliance sign-off in §1a.**

| Item | What was built |
|---|---|
| **EF-49** | Postcode region-derivation defect fixed (BB, CT, HP, PE, WD corrected) in all three environments |
| **EF-02 / EF-10** | Region, helper-organisation and helper-relationship secured; region column and filter removed from the Trustee Portal; `rev_exceptionalcircumstance` category surfaced there instead (EF-48's buildable half) |
| **EF-44** | Score breakdown split: `rev_scorebreakdown` (trustee-facing) and new `rev_scoringaudit` (admin-only audit trail of thresholds/status/income-flag at scoring time) |
| **EF-23** | The stale "no rounding was applied" passage removed from the score breakdown entirely |
| **EF-25** | "Threshold score" rename done via a new `rev_displayname` column on `rev_setting` — the machine key (`KnockoutThreshold`) is untouched, so scoring and all three environments keep working |
| **EF-22** | Wellbeing scoring section split into four sections matching the form's own structure |
| **EF-21** | All eight review checkboxes + free-text note, correct null-default semantics, placed on the new Casework tab directly above the release control |
| **EF-27** | Safeguarding action-completed fields (flag, date, who), secured, on the Casework tab |
| **EF-45** | `rev_autorejectreason` column built and placed beside status; the flow logic that writes it is correctly deferred pending EF-34/DPO |
| **EF-47** | New Casework tab, fields moved off General/Finance, sections in the order the plan specifies (Decision → Review checklist → Release → Override → Safeguarding) |
| **EF-37 (labels)** | The grant-admin-app side of the condition/care relabelling is in: disability, condition and care-support fields now carry the form's own wording, including "Brief Description of Disability" |
| **EF-29** *(this session)* | Income band option set trimmed to Emily's four confirmed bands; "Prefer not to say" dropped; re-seeded in all three environments |
| **EF-28b / M-04** *(this session)* | New `rev_incomeflag` option 4 ("Qualifies on means-tested benefits"); scoring flow checks benefit status before falling through to "not stated" — **built, but see §1a before it can ship clean** |
| **Regressions found and fixed** *(this session)* | A missing synthetic-relationship entry and a stale lookup count were breaking ~20 `ensure-schema.ps1` tests; six flow-action descriptions exceeded Power Automate's real 256-char save limit (a live deploy-breaking defect, not cosmetic); three stale comments and one dead label map were still naming a now-secured column; 23 deliberate form-label relabels were undeclared to the `shipped-content` gate |

**The response email to Emily** (`docs/plans/emily-response-2026-09-17.md`) is drafted and complete
— all 15 answer-only items, the 3 findings-to-tell-her, and the 2 decision items (EF-46's numbers,
EF-11's question) are in it.

---

## 3. Answered, no build required — closed

Fifteen items closed at zero build cost via the response email: EF-06, EF-13, EF-14, EF-15, EF-18,
EF-19, EF-20, EF-23 (the "what it means" half), EF-26, EF-29 (the "it matches" half), EF-30, EF-32,
EF-40 (the "why it doesn't exist" half — the *build* is still open, see §1b), EF-45 (the "yes it's
feasible" half), EF-48 (the "here's why it's blank" half). **One question is still open on her
side:** EF-11, whether *Applications per day* should be removed alongside the day-count tile.

---

## 4. Still to build — no blocker, just not reached yet

These are `in-baseline`, unblocked, and simply haven't been picked up:

| Item | What it is |
|---|---|
| **EF-07 / EF-24** | Rewrite the score breakdown to question text + answer label (e.g. *"I've been feeling optimistic... response 1 = 5 points"*) instead of raw column numbers — flagged in the flow's own comment as pending |
| **EF-31 (A2 half)** | The >£500/>£100 exceptional-funding flag against the existing corpus, break-type dependent — nothing built yet |
| **EF-08** | Rename the Trustee Portal panel *Holiday Details* → *Application Details* |
| **EF-16** | *Auto-pass Applications* saved view + Casework sub-area (deliberately sequenced after EF-46, since it's 81% of the round) |
| **EF-28** | Reorder the benefits/provider/income-band/income-flag fields on the form to match the form's own order |
| **EF-33** | Move Costs and Funding into the Break Details section |
| **EF-35 / EF-36** | New carer age-confirmation column (mirroring the existing applicant one) and surfacing both age confirmations + age range in the eligibility section |
| **EF-38** | Surface Applicant Type in Support Needs |
| **EF-39** | Hide consent date/time stamps from the form layout (keep the columns) |
| **EF-42** | *Group Applications* saved view + Casework sub-area, grouped on `rev_grouplinkage` as-is (no validation — that's accepted, deferred scope) |

The plan's own sequencing (§7, step 6) groups EF-01/17/21/27/28/33/36/37/38/39/42 as one pass
starting with EF-47. EF-47/EF-21/EF-27/EF-37 are done; the rest of that pass is what's listed above.

---

## 5. Waiting on someone else — not blocked by us

| Item | Waiting on | Note |
|---|---|---|
| **EF-11** | Emily | Still the only open question in the response email |
| **EF-32 / Other break type** | Emily | Three numbers sent with the email; needs her pick |
| **OQ-001/002/003 (thresholds)** | Emily + board | Round 4/5 distributions sent with the email |
| **EF-34** | DPO | Compound auto-rejection — same tier of decision as §1a |
| **EF-31 (form-block half), EF-09, EF-35 (form half)** | Alex | Our halves are built ahead of him where possible |
| **NI postcode licence (BT districts)** | Revitalise | Only 99 districts affected; not blocking the rest of EF-41 |

---

## 6. Out of scope for a repo-only session

A handful of PowerShell tests fail for reasons unrelated to this work and cannot be fixed from
here: `verify-pipeline-config`, `ensure-bulk-delete-jobs.ps1`, `provisioning-common.ps1` and
`verify-role-bindings.ps1` all need either a real Entra/Dataverse tenant connection or a local
`acc-settings.json` this machine doesn't have. Confirmed pre-existing, not caused by this work.

---

## 7. Suggested order

1. Answer §1a and §1b — they're the only things actually stopped.
2. Say go/no-go on routing the three change-order candidates (§1d).
3. I continue the §7 step-6 form pass (§4 above) — none of it needs a decision first.
4. EF-07/EF-24 and EF-31's A2 flag whenever you want them — same, no blocker.
