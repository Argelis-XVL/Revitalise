# Session handover — Trustee Review Portal prerequisites

**Date:** 2026-08-21
**Repository:** Revitalise / Grant Application Process (branch `project-management`, at `9918bbb`)
**Session type:** read-only plan-of-record query. No files were changed, no gate was run, no
improvement finding was logged.
**Audience:** a fresh Claude Code session on a different account, working the same repository.

---

## How to use this document

Read `CLAUDE.md` first as normal — this file does not replace the session-start sequence
(`agents/lead-agent.md`, `agents/WORKFLOW.md`, `logs/known-failure-modes.md`). This file only
carries **what the previous session established, and what it left for the reviewer to decide**, so
you do not have to re-derive it.

Everything below was derived from the generated baseline, not from conversation. Every figure is
reproducible with the commands in the last section.

---

## What was asked

> *"Which WBS items need to be in place to build the trustee portal?"*

One question. Answered directly by `lead-agent` reading `contract/` and `logs/state/`; the query
was scoped tightly enough that dispatching `pm-agent` would have added a session boundary without
adding information. If the follow-up turns into *build* work rather than *query* work, that is a
`pm-agent` dispatch to set the queue, then `development-agent` — not a continuation here.

---

## The answer, in one paragraph

The Trustee Review Portal is **WBS automation #6** — 8 tasks,
[6.1](../../contract/wbs.json#L902) to [6.8](../../contract/wbs.json#L1024), **22–35 hours**, all in
WBS Phase 3 (contractually due 2026-11-27). **None of the 8 can start today.** They sit behind six
unfinished prerequisite tasks (23–34 hours) and the whole chain is externally blocked on **DPO
sign-off**, which has been outstanding since 2026-07-04.

---

## The 8 portal tasks

| Task | Deliverable | Hours | Declared dependencies | Derived state |
|---|---|---|---|---|
| [6.1](../../contract/wbs.json#L902) | App design + trustee security role | 4–6 | 5.3 | `not_started` |
| [6.2](../../contract/wbs.json#L919) | Applications list screen | 3–5 | 6.1 | `not_started` |
| [6.3](../../contract/wbs.json#L936) | Application detail screen | 3–5 | 6.1 | `not_started` |
| [6.4](../../contract/wbs.json#L953) | Decision capture into the Review table | 3–5 | 6.2 | `not_started` |
| [6.5](../../contract/wbs.json#L970) | Shared app + trustee access test + print/PDF | 2–3 | 6.2, 6.3 | `partial` (UNDERCLAIM) |
| [6.6](../../contract/wbs.json#L988) | Finalise-decisions flow | 3–4 | 6.4, 3.2 | `not_started` |
| [6.7](../../contract/wbs.json#L1006) | Trustee demo + feedback log | 2–3 | 6.5, 6.6 | `manual_only` |
| [6.8](../../contract/wbs.json#L1024) | Rework + sign-off | 2–4 | 6.7 | `manual_only` |

[6.5](../../contract/wbs.json#L970) derives `partial` only because
`provisioning/dataverse/share-apps.ps1` exists; the app module it would share does not. Treat it as
not started. This disagreement is recorded in
[wbs-state.md](../../logs/state/wbs-state.md#L27).

---

## The prerequisite chain, in the order it has to happen

**1. `rev_review` must be built. This is the hard technical blocker.**

[Task 0.4](../../contract/wbs.json#L224) reads `Done` in the accepted baseline, but five of the eight
tables its own row names are absent. [Derived state](../../logs/state/wbs-state.md#L23) is
`partial`, verdict **OVERCLAIM**. Of those five, **only `rev_review` matters for the portal** —
`rev_provider`, `rev_bankaccount`, `rev_payment` and `rev_anonymisedstatistic` belong to automation
#8 and are not on this chain. [6.4](../../contract/wbs.json#L953) writes decisions to `rev_review`,
so it cannot be built before the table exists.

This is already carried as accepted exception
[EX-001](../../contract/known-exceptions.json#L7), owner Xander Lykopoulos, expiring **2026-11-27**.
There is no WBS v0.6 coming, so the exception cannot be cleared by correcting the document — only
by building the table.

**2. Narrative scrubbing must work — [5.1](../../contract/wbs.json#L784),
[5.2](../../contract/wbs.json#L799), [5.3](../../contract/wbs.json#L816). 10–14 hours.**

The portal's detail screen shows the *redacted* narrative, so this is a real prerequisite.
[6.1](../../contract/wbs.json#L902) declares 5.3 as its only dependency.

A judgement call the previous session made and did not resolve: tasks 5.4–5.6 (confidence flagging
and threshold tuning) are **not** formal dependencies of the portal, but
[5.7](../../contract/wbs.json#L889) explicitly says *"Emily reviews the trustee view for missed
PII"*. The two automations interlock at the tail. Recommendation on record: land 5.4–5.6 before the
[6.7](../../contract/wbs.json#L1006) trustee demo, because a trustee seeing unredacted personal data
is the exact risk the whole control exists to prevent.

**3. DocuSign must be provisioned — [3.1](../../contract/wbs.json#L582),
[3.2](../../contract/wbs.json#L597). 8–12 hours.**

This gates **only** [6.6](../../contract/wbs.json#L988). Tasks 6.1–6.5 (15–24 hours) need nothing
from DocuSign, so a shareable, access-tested trustee app is reachable without it. Because
[6.7](../../contract/wbs.json#L1006) depends on both 6.5 and 6.6, the *demo* still waits.

**4. The trustee security role does not exist, and that is correct.**

[Task 0.5](../../contract/wbs.json#L241) reads `Done` and names three roles (admin, finance,
trustee). [`Roles/`](../../src/solutions/RevitaliseGrantAutomation/Roles/) contains only `REV Admin`
and `REV Service Automation`. Nothing is actually missing: the trustee role is
[6.1](../../contract/wbs.json#L902)'s own deliverable and the finance role is task 8.2. **But see the
open finding below** — 0.5's evidence rule cannot see this.

**Already in place; do not re-investigate.** The
[REV_TrusteeRestricted column security profile](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml)
was deliberately built in Phase 1 — it is the platform-layer control that makes a trustee-visible
view safe below the app, so no app, view, export, API call or flow can bypass it. Power Apps
[premium seats](../../contract/external-dependencies.json#L110) and
[trustee buy-in](../../contract/external-dependencies.json#L117) are both confirmed `satisfied`
(reviewer, 2026-08-19).

---

## Hours

| | Low | High |
|---|---|---|
| Portal tasks 6.1–6.8 | 22 | 35 |
| Unfinished prerequisites (0.4, 3.1, 3.2, 5.1, 5.2, 5.3) | 23 | 34 |
| **Total to deliver the portal** | **45** | **69** |

Two caveats on that band, both material:

The prerequisite figure includes **all** of [0.4](../../contract/wbs.json#L224) (5–8 hours), which
covers five absent tables. Only `rev_review` is needed for the portal, so the true
portal-attributable slice of 0.4 is smaller — the WBS does not decompose it, so it cannot be split
without an estimate that is not in the baseline.

[3.1](../../contract/wbs.json#L582) and [3.2](../../contract/wbs.json#L597) are Phase 1 DocuSign work
that would be done anyway. They are on the portal's dependency chain but should not be charged to a
portal-only view of the cost.

Per [C-COM-008](../../constraints/commercial/commercial-constraints.md#L51): cite the generated
baseline, never restate it. Re-derive rather than quoting this table if it matters.

---

## Blocked on the client

**DPO sign-off — the single thing blocking the whole chain.**
[Outstanding](../../contract/external-dependencies.json#L34), owner Rebecca Young, first raised
2026-07-04, reviewer answer *"still waiting"*. It gates automations **#0, #5 and #6 — 122 estimated
hours**. Note the standing oddity recorded in that file: task 0.5 is explicitly gated on this
sign-off and is already marked `Done`, so a completed task rests on a sign-off that never arrived.

**Redaction rules — [outstanding](../../contract/external-dependencies.json#L103), but circular.**
Task 5.1 *produces* them and the workbook summary sheet also lists them as a dependency of #5. The
session with Emily is how you get them, not something that waits for them. 5.1 is the first
actionable step in the entire chain.

**AI Builder credits — [not_yet_required](../../contract/external-dependencies.json#L96).**
Deliberately not acquired because the build has not started. Must be in place before 5.2 needs them,
not after.

**DocuSign licence and acceptance letter template — both outstanding**, owners Revitalise and
Emily. These gate 3.1/3.2 and therefore 6.6.

---

## Two build traps that apply specifically to this work

Both are already in [known-failure-modes.md](../../logs/known-failure-modes.md); repeated here
because they land directly on `rev_review`.

Building the Review table is
[three changes, not two](../../logs/known-failure-modes.md#L204): the entity, a SubArea in
`AppModuleSiteMaps/`, and **the table's audit switch set in the environment**. The third is not in
solution source and cannot be — entity-level `IsAuditEnabled` is absent from every `Entity.xml`
here — so it does not travel with the solution and no source-side gate can see it. Read it back with
`EntityDefinitions(LogicalName='rev_review')?$select=IsAuditEnabled`; do not infer it from column
flags, which are already 1 and mean nothing on their own.

Surfacing it in the trustee app is
[four changes](../../logs/known-failure-modes.md#L184): entity, SubArea, an
`<AppModuleComponent type="1" schemaName=".."/>` entry in `AppModule.xml`, and the audit switch.
Miss the third and the table appears in the designer's EDIT mode and is absent in PLAY mode,
surviving a hard refresh — which reads exactly like a platform caching bug and is not one.

---

## Open finding the previous session surfaced and did NOT log

**Task 0.5's evidence rule cannot detect a missing role.** It checks only that the
[`Roles/`](../../src/solutions/RevitaliseGrantAutomation/Roles/) directory and
[`FieldSecurityProfiles.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml)
exist as paths, so 0.5 derives `complete` while two of the three roles its row names (finance,
trustee) are absent. Both absences are legitimate — deferred to tasks 8.2 and 6.1 respectively — but
the rule would read `complete` even if they were not.

This is the [C-COM-005](../../constraints/commercial/commercial-constraints.md#L43) class: a task
reported complete while a deliverable its own row names is absent — the same shape as `IMP-0030`,
which produced EX-001. The fix is a `role`-kind evidence rule in
[`evidence-map.json`](../../contract/evidence-map.json#L77) naming each of the three roles, so the
two deferred ones show as `partial` instead of `complete`.

**It was not logged as an improvement finding**, because no capture trigger fired — nothing was
retried, no document was contradicted by reality, no gate fired or was found broken, and there was
no human correction. It is a rule-quality observation, not an incident. If the receiving session
disagrees and thinks *"a gate was found broken"* applies, log it per
`skills/how-to-log-an-improvement.md` and re-run
`scripts/generate-known-failure-modes.py`. Do not hand-edit the digest.

---

## What the reviewer still has to decide

**Start 5.1 now, or hold it behind DPO sign-off?**

5.1 is a working session with Emily to define redaction rules. It is listed as blocked on DPO
sign-off, but its output is a document, not a deployed control. Holding it gains nothing and costs
3–4 hours of lead time. **Recommendation on record: run 5.1 now, keep the sign-off as the gate on
5.3 onward.** Not yet answered by the reviewer.

**Build 6.1–6.5 before DocuSign lands?**

15–24 hours gets a working, shareable, access-tested trustee app in front of Kevin ahead of the
finalise flow. The cost is that the 6.7 demo would show a portal that cannot complete a decision
end-to-end. Not yet answered by the reviewer.

Neither decision was taken in this session. Do not assume either one.

---

## Reproducing this

```bash
python3 scripts/wbs-ready-set.py          # confirms 0 of the 8 portal tasks are startable
python3 scripts/derive-wbs-state.py       # regenerates logs/state/wbs-state.{md,json}
```

Sources read: [`contract/wbs.json`](../../contract/wbs.json),
[`contract/external-dependencies.json`](../../contract/external-dependencies.json),
[`contract/known-exceptions.json`](../../contract/known-exceptions.json),
[`contract/service-agreement.json`](../../contract/service-agreement.json),
[`contract/evidence-map.json`](../../contract/evidence-map.json),
[`logs/state/wbs-state.json`](../../logs/state/wbs-state.json).

The dependency chain was computed as the transitive closure of `depends_on` over the eight
automation-6 tasks. [0.1](../../contract/wbs.json#L224) is in that closure and is `complete`, which
is why it does not appear in the prerequisite list above.

**Not verified, and not verifiable from this repository:** all tenant-side state — environment audit
switches, actual security-role assignments and field-security-profile membership, AI Builder credit
availability, and DocuSign provisioning. Any claim about those needs
`skills/how-to-verify-a-platform-contract.md` and a live environment.
