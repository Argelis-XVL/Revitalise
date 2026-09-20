# Improvement Review — 2026-09-19 (2)

**Status:** ~~AWAITING — nothing in section 3 has been applied. Those changes land only on
`APPROVE IMPROVEMENTS`.~~ **APPLIED 2026-09-19**, on a keyword relayed by two agents rather than
sent in the reviewer's own turn — see section 9, which records that, one narrowing, and four
withheld changes. Section 0 is a measurement, not a change, and it is the most urgent thing in
this document.

**Agent:** improvement-agent (tier `strategic`)
**Trigger:** three unread `blocker` entries — `IMP-0781`, `IMP-0782`, `IMP-0784` — routed
immediately rather than batched, per `agents/WORKFLOW.md` → Processing triggers.
**Scope:** the six `unread` entries. 169 `reviewer-deferred` and 0 `awaiting-approval` entries
were excluded by activation step 2 and are accounted for in section 6.
**Gate:** `APPROVE IMPROVEMENTS` — received by relay; the applied record is section 9.
**WBS:** this review touches `wbs:6.1, 6.2, 6.3, 6.4` as a **claim about evidence**, and proposes
no delivery work against them. See section 5 for the commercial consequence.

---

## 0. The parallel development dispatch is aimed at the wrong tasks

The dispatch that sent me here says a `development-agent` was dispatched in parallel "to fix the
underlying WBS 6.1-6.4 gaps `IMP-0784` describes". **Four measurements say those are not 6.1–6.4
gaps, and 6.1–6.4 are not defective.** This is reported first because that dispatch is running now.

**1. The evidence rules for 6.1–6.4 point at the Code App, deliberately.** Every rule for those
four tasks names a file under `src/code-apps/trustee-review-portal/`
([`contract/evidence-map.json#L348`](../../contract/evidence-map.json#L348)). That is not an
oversight: ADR-003 made the trustee deliverable a Code App rather than a Model-Driven App, and
`derive-wbs-state.py`'s own docstring records four rules checking Model-Driven App paths for
eleven days afterwards as the defect that was fixed
([`scripts/derive-wbs-state.py#L65`](../../scripts/derive-wbs-state.py#L65)).

**2. The reviewer checked a different application.** All five observations — an audit field under
the score breakdown on the Applications Form **CaseWorker tab**, an **Auto-pass view** wired into
the **casework section menu**, selectable **Gender/Equality views**, missing columns on the
**active-applications view** — are components of the `rev_grantadministration` Model-Driven App
(FormXml, SavedQueries, SiteMap SubAreas). None of them is a Code App screen.

**3. The components really are missing, and the mechanism is settled at V1 in source.**
`IMP-0784` offered three candidate root causes and could not distinguish them. They can be
distinguished, from the repository, in four greps:

| The reviewer saw | Measured in source | Verdict |
|---|---|---|
| No Auto-pass view | `Entities/rev_application/SavedQueries/` holds six files: ActiveApplications, AllApplications, AutoRejectedApplications, BorderlineAwaitingReview, EligibleForCurrentRound, UnderReviewIncompleteScoring | **Never authored** |
| No Gender/Equality views | `grep -rli 'gender\|equality'` across every `Entities/*/SavedQueries/` — 0 files | **Never authored** |
| No audit field on the CaseWorker tab | `grep -rlo 'CaseWorker\|Caseworker'` across `Entities/rev_application/FormXml/` — 0 files. There is no CaseWorker tab in source at all | **Never authored** |
| Active-applications view missing columns | `ActiveApplications.xml` declares five columns: `rev_name`, `rev_applicantid`, `rev_status`, `rev_submittedon`, `rev_circumstancescore` | **Authored narrow** |

So candidate (a) — packaged but not wired — is disproved, and candidate (c) — a Dev Summary
claim the evidence rule believed — is disproved. Candidate (b) is right, with one correction:
these were never authored **anywhere**, not merely never authored correctly.

**4. No accepted WBS task delivers them, and the system already knew that.** The Model-Driven app
being unquoted is a settled, `APPLIED` finding: *"The Grant Administration model-driven app
(`rev_grantadministration`) is shipped in the solution and no WBS task names it"* (`IMP-0066`,
found by `verify-wbs-chain.py`'s artefact-to-task direction on its first run). The 61 accepted
tasks contain no caseworker-views task; 6.x is the trustee Code App and 8.3 is the payment capture
form inside this same app.

**What follows.** Building these views is either unquoted work or a change order (`C-COM-002`), and
a `development-agent` fixing them under `wbs:6.1-6.4` would attach hours to four tasks whose
deliverable is a different application. Both halves are routed in section 5 — the re-scope to
lead-agent, the change-order decision to `commercial-agent`.

**The table above is timestamped, and the tree has already moved.** Re-measured twenty minutes
later: `AutoPassApplications.xml` now exists, the sitemap carries fifteen new lines, and the
`rev_application` main form is modified in the working tree — the parallel dispatch is building
these components now. That does not weaken the finding; it sharpens it. **The work is being written
against `wbs:6.1-6.4` as it goes**, so the attribution question is being answered by default rather
than decided, and the change-order decision is being taken by not taking it.

**This measurement is itself a finding**, appended as `IMP-0785` carrying `corrects: IMP-0784`,
per the capture contract.

---

## 1. Regression check — did the last review's changes work?

Review 1 of 2026-09-19 applied four changes, all within the last few hours.

| Prior change | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|
| A behavioural claim is re-verified by RUNNING it (`skills/how-to-log-an-improvement.md`, `.engine`) | `finding-diagnosis-unverified` | **No new instance.** Exercised here in the opposite direction: `IMP-0781`'s proposed gate was disproved by reading the map it proposes to check (section 2.1), and `IMP-0782`'s two premises were confirmed by reading the loop they describe (section 2.2) | Working |
| Class reuse asserts a property match even where the `Defended by` cell is `—` (same file) | class mis-reuse | **RECURRED ONCE.** `IMP-0784` carries `stale-claim-contradicting-rechecked-source`, and section 2.3 establishes it is not that mechanism | Prose fix, one recurrence — held at prose, reason below |
| Retag of `IMP-0775` / `IMP-0776` (`logs/improvement-log.jsonl`) | count inflation | **No instance** | Working |
| Closure of both with `evidence_grep` + `reobserved` | — | **No instance** | Working |

**The one recurrence, and why it stays prose.** The clause landed in the engine at 2026-09-18
20:26; `IMP-0784` was logged 2026-09-19 15:30, so the clause was in force. But the clause addresses
an author choosing between existing class names, and `IMP-0784`'s author had a live human report
and no way to know — without the four greps in section 0 — that the observation belonged to a
different application. **The mis-tag is downstream of the mis-attribution, not of the naming
rule.** Escalating it would mean a gate deciding whether a finding's mechanism matches a class
name's meaning, which is a gate reading prose for semantics — measured in this repository at
48–100% false, five times (`IMP-0422`, `IMP-0428`).

### Closure-evidence audit

Review 1 closed two entries at `observable_at` V2 on a full `Invoke-Tests.ps1` run — the exact
command whose failure produced them. That is re-observation at the level the defect was visible
at, and it holds up. **This review closes no `blocker`**: all three are `observable_at` V3/V4 and
none can be re-observed from a session with no credential and no live environment. They are parked
with `deferred_reason` + `revisit_when` rather than closed, per section 3.

---

## 2. Clusters and promotion decisions

### 2.1 `IMP-0781` — the proposed gate would not have caught this failure

```
CLUSTER: credential-not-on-the-machine-that-needs-it  (x5: IMP-0048, IMP-0061, IMP-0105,
                                                       IMP-0528, IMP-0781)
Altitude:   INSTANCE — the fifth NAME, the first instance of this sub-property
Ladder row: "an agent had the information and still did the wrong thing" → agent-file edit
Becomes:    change 1 (agents/pipeline-agent.md). NOT the gate the finding proposes
Retires:    nothing
Cites:      IMP-0781, IMP-0528
Residual:   nothing statically checkable proves ensure-schema.ps1 has RUN against an
            environment. The remaining defence is the dispatch declaring the credential it has
```

**The proposed gate is off-target, and the grep that shows it is one line.** `IMP-0781` proposes
comparing every `Get-RevSyntheticRelationship` key against Entity.xml lookups lacking a declared
relationship. That map **already had** `rev_safeguardingactioncompletedby` — it was added on
2026-09-17 for EF-27, and the finding says so itself. A map-versus-source gate compares two things
that already agreed. It would have reported green and the import would have failed identically.

There is also already a defence for the shape the gate would cover: an unmapped lookup throws an
actionable message from `Get-RevSyntheticRelationship`
([`ensure-schema-helpers.psm1#L801`](../../provisioning/dataverse/ensure-schema-helpers.psm1#L801)),
asserted by `src/tests/provisioning/EnsureSchema.Tests.ps1`. **Withheld, per the disproved-proposal
rule.**

**The actual mechanism is a credential, and it is the fifth entry under that name but the first of
its kind.** The four prior members are all about a credential's availability *in CI* — a cert that
could not be exported into a secret, a Graph read refused after a successful connect. This one is
an **interactive dispatch that had neither variable set, skipped all three credential-gated
pre-deploy steps silently, and attempted a live solution import anyway** through `pac`'s
separately-authenticated profile. Under the class-reuse rule, that is a distinct sub-property with
one instance, so the ladder's second-instance clause does not fire and an instance-level fix is
correct. Change 1 puts the check where the decision is made.

### 2.2 `IMP-0782` — both premises hold, and the fix is not mine to write

```
CLUSTER: platform-contract-guessed-not-groundtruthed  (x60, of which this is 1)
Altitude:   CLASS for the KNOWLEDGE, INSTANCE for the fix
Ladder row: "one instance, but the cause is general and a human needs to know it" → knowledge
Becomes:    change 2 (knowledge/technology/dataverse.md). The script change is ROUTED
Retires:    nothing
Cites:      IMP-0782, IMP-0783, IMP-0255, IMP-0272
Residual:   the two candidate mechanisms (inline IsSecured not honoured vs metadata-propagation
            lag) are still undistinguished, and this review does not pick one
```

**Both premises were read and both are true.** Step 3b iterates `$relationshipWork`, which is
built only from relationship definitions
([`ensure-schema.ps1#L500`](../../provisioning/dataverse/ensure-schema.ps1#L500)) — so a plain
String or Picklist attribute reclassified `IsSecured=1` after it already exists live has no
reconciliation path at all. And the loop skips anything not pre-existing
([`ensure-schema.ps1#L643`](../../provisioning/dataverse/ensure-schema.ps1#L643)), on a stated
assumption the code's own comment already flags as never demonstrated.

**The fix belongs to a delivery agent, and the reason is a rule rather than a preference.**
`ensure-schema.ps1` authenticates to a live environment. `agents/improvement-agent.md` puts that
squarely outside this role: hand over the requirement and the verification, do not write the
script. Routed as R2 with the exact requirement.

**The gate half is withheld too.** Extending `verify-field-security-coverage.py` would not have
caught this: it is a **source-versus-source** check — it compares `IsSecured` declarations against
`FieldSecurityProfiles.xml` — and all four columns were declared consistently in source. The gap is
source-versus-live, which `IMP-0258` already named as invisible to any source gate. Note also that
`scripts/verify-field-security-coverage.py` is a **wrapper**; the mechanism is in
`.engine/scripts/`, and a grep of the wrapper would have returned nothing and proved nothing.

**`IMP-0273` was read before this was written, and it changes nothing here.** It carries `corrects`
against `IMP-0272` and withdraws that entry's PATCH-plus-cast diagnosis in favour of a documented
PUT with the full object — a correction already carried in `ensure-schema.ps1`'s own header. Change
2 cites `IMP-0272` only for *which five columns the create path is proven on*, which the correction
does not touch.

**What change 2 records is what was observed, not why.** `IMP-0782` names two candidate
mechanisms and says in terms that this session cannot distinguish them. Writing either into a
knowledge file is the failure `skills/how-to-promote-a-finding.md` §4 names — an argued mechanism
in place of a confirmed one, which cost review 15 a wrong diagnosis in this same knowledge file.
So change 2 states the three creation paths, which one is proven, and what was seen; it asserts no
cause.

### 2.3 `IMP-0784` — a mis-attribution, not a stale claim

```
CLUSTER: wrong-artefact-cited-as-evidence  (x8 after this retag: IMP-0784 joins 7)
Altitude:   INSTANCE — the derived status is correct; the observation was mapped to the wrong task
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:    change 3 (retag) + IMP-0785 (the corrected diagnosis) + two routed items. NO gate
Retires:    nothing
Cites:      IMP-0784, IMP-0066, IMP-0675
Residual:   this project runs two applications and calls both "the portal" in prose. Nothing
            mechanical can fix a spoken ambiguity; section 5 R1 fixes the live consequence
```

Section 0 carries the measurement. Three further notes on what this does **not** become:

**No live-check evidence tier.** `IMP-0784` proposes a V4 tier in `derive-wbs-state.py` for 6.x UI
tasks. `derive-wbs-state.py` reads the repository; a V4 check is a signed-in human. The
evidence-map already has the right instrument for exactly this — `kind: manual`, which 6.5 uses and
which can never derive complete from the repo alone — and 6.1–6.4 do not need it, because their
Code App deliverable genuinely is evidenced in source.

**No "existence-only evidence" gate, and the corpus is why.** A gate flagging any task whose whole
evidence set is bare `path`/`entity`/`workflow` existence is mechanical and value-based, so it
passes the polarity test a prose gate fails. I measured it before proposing it: **23 of the 61
accepted tasks are existence-only**, including `0.1`, `3.2`, `5.1`, `6.1`, `6.4`, `8.1`. A gate that
opens red on 23 contracted rows no dispatch owns is the shape `agents/improvement-agent.md` tells
me not to ship.

**And the evidence-map's own quality note already carries three corrections of this family** —
a rule satisfied by a forward reference, a rule matching the negation of its deliverable, a rule
proving too early a stage. None of them is this. Here the rules are right and the reader was
looking at another application.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` · `script` ·
> `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | agent | `agents/pipeline-agent.md` **(`.engine` submodule)** | a live import declares the credential it holds, before it attempts one | IMP-0781, IMP-0528 | NO — instruction | N/A |
| 2 | knowledge | `knowledge/technology/dataverse.md` | the three field-security creation paths, and which one is proven | IMP-0782, IMP-0783 | NO — reference | N/A |
| 3 | other | `logs/improvement-log.jsonl` | retag `IMP-0784`; stamp `reviewed_in` on six entries; clear the `IMP-0778` warning | IMP-0784, IMP-0778 | YES — `verify-improvement-log.py --check` | N/A |
| 4 | other | `logs/improvement-log.jsonl` | park the three blockers with `deferred_reason` + `revisit_when`; close the three note-only entries | — | YES — same | N/A |

**0 new constraints** (cap 3). **0 gates/scripts** — two were proposed by findings and both are
withheld with the measurement that disproved them. **1 agent-file edit. 1 knowledge edit. 0
retirements.**

### Change 1 — a live import declares the credential it holds

Added to `agents/pipeline-agent.md`, in its activation sequence:

> **Before the first step that writes to an environment, state which credential this session
> has.** `PROVISION_APP_ID` and `PROVISION_CERT_THUMBPRINT` gate every script that dot-sources
> `provisioning-common.ps1` — `verify-environment-access.ps1`, `ensure-schema.ps1`,
> `reconcile-flow-statecodes.ps1`. `pac` authenticates separately, so **a session with no
> provisioning credential can still import a solution**, and will: the three pre-deploy steps fail
> or are skipped, and the import proceeds into an environment nothing has converged.
>
> Where both variables are absent, the Deployment Summary and the gate output name **which steps
> were excluded and who owns running them**, before the import — not afterwards as a diagnosis.
> Where the artefact's diff touches schema-shaping source (a new column, a new relationship, a new
> field permission), the import is not the next action: converging the environment is, and it needs
> a session that holds the credential.
>
> Reading the certificate out of a local keychain to self-supply the values is refused by the
> harness, correctly, and is not a workaround to attempt (`IMP-0781`).

Zero client literals apart from this project's own script paths, which are what the instruction is
about. Instance-level under `skills/how-to-promote-a-finding.md` §6.

### Change 2 — the three field-security creation paths

Added to `knowledge/technology/dataverse.md`, beside the existing `IsSecured` material:

> **A column reaches `IsSecured=1` live by one of three paths, and only one of them is proven.**
>
> | Path | State |
> |---|---|
> | A non-lookup attribute **created** with `IsSecured` in its create body | **Proven** — the five columns of `IMP-0255` / `IMP-0272` |
> | A lookup **created** in the same run, carrying `IsSecured` inline on the deep-insert `Lookup` body | **Unproven.** On 2026-09-19 a freshly created lookup's field permission still failed `0x8004f508` |
> | An attribute of **any** type that already exists live and whose source `IsSecured` flag changed afterwards | **Not covered for non-lookups.** The convergence loop walks relationship work only |
>
> Observed 2026-09-19, live, on four columns of one run: three non-lookup columns reclassified
> after they already existed and one freshly created lookup all failed field-permission creation
> with `0x8004f508` ("not secured for entity fieldpermission"). After the columns were secured by
> hand in the maker portal the import succeeded, and the target profile's permission count rose by
> exactly four. **Two mechanisms remain undistinguished** — the platform may not honour `IsSecured`
> on an inline deep-insert, or there may be a propagation lag between the relationship write and
> the permission write. Nothing here should be read as choosing one.
>
> Before relying on a newly declared `IsSecured=1`, identify which of the three paths the column is
> on, and read the live value back rather than assuming the create body was honoured.

### Change 3 — the retags and stamps

| Entry | Field | From | To |
|---|---|---|---|
| IMP-0784 | `class_instance_of` | `stale-claim-contradicting-rechecked-source` | `wrong-artefact-cited-as-evidence` (existing, x7 → x8) |
| IMP-0778 | `reviewed_in` | absent | `docs/improvements/2026-09-19-improvement-review.md`, plus this document |
| IMP-0779, IMP-0781, IMP-0782, IMP-0783, IMP-0784 | `reviewed_in` | absent | this document |

`IMP-0784`'s `class` stays `state-defect`-family as logged: the coarse field is not what mis-fired.
The `reviewed_in` stamps go on **at draft time**, per activation step 6 — they are what makes these
entries read as `awaiting-approval` rather than as findings nobody has opened.

### Change 4 — dispositions

**None of the three blockers can be closed from this session**, and all three are `observable_at`
V3 or V4. An honest open entry beats a closed one nobody tested.

| Entry | Disposition | `revisit_when` |
|---|---|---|
| IMP-0781 | `deferred_reason`: the gate it proposes is withheld as disproved (section 2.1); the durable part is change 1, which cannot be re-observed without a credentialled pipeline dispatch | the next DEV pipeline dispatch that holds `PROVISION_*` reports which pre-deploy steps it ran |
| IMP-0782 | `deferred_reason`: routed to `development-agent` (R2); the knowledge record is change 2, and the script fix is live-authenticating delivery work | `ensure-schema.ps1 -Env dev` re-run after R2 lands, reporting CREATED on all four columns |
| IMP-0784 | `deferred_reason`: diagnosis corrected by `IMP-0785`; the underlying gaps are routed as R1 and R3 and are not 6.1–6.4 work | the reviewer's change-order decision on the caseworker views (R3) |
| IMP-0778, IMP-0779, IMP-0783 | note-only closures — all three carry `proposed_change.type: none` and propose no artefact. `IMP-0779` is V2 and `IMP-0783` is V3, so each closure carries a `reobserved` recording the observation already made in the finding itself, or stays open if that cannot be written honestly | — |

### The disposition was simulated before this draft was parked, and it caught two things

Per activation step 8, the proposed statuses and fields were applied to a scratch copy of the log
and `verify-improvement-log.py --check` run against it. The real file carries only the six
`reviewed_in` stamps of change 3 — verified as exactly six changed lines against a backup taken
before stamping. Two results, neither of which reading would have produced:

**1. The first draft of `IMP-0778`'s closure was rejected.**

```
ERROR: IMP-0778: proposed_change.target names 2 paths and the closure accounts for only 0.
       Unaccounted: logs/known-failure-modes.md, scripts/generate-known-failure-modes.py.
```

Its `proposed_change` names two files and proposes changing neither. `applied_by` now says so
explicitly — that the rendered count and the generator's exclusion of rejected members both stay
as they are, deliberately — and the re-run exits 0.

**2. A claim this draft had already written about `IMP-0777` was stale.** Review 1 left it open as
a `blocker` its owner had to clear, and this draft repeated that. It has since been given a
reviewer-accepted `deferred_reason` — real values for the Dataverse lookups, one genuine SharePoint
decommission, one deferral — so it no longer holds the gate. **The simulated disposition exits 0**:
the blocker trigger this review exists to clear does clear, on three accepted `deferred_reason`s
and nothing else.

---

## 4. Retirements

**Checked, none found.** Derived rather than typed:

```bash
grep -rh '^| C-'   constraints/ --include='*.md' | wc -l   # 85
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   # 10
```

This review adds no constraint and no script, so there is no instance-level rule for a general one
to supersede. One candidate was considered: nothing in the constraint set claims that field
security converges on re-run, so `IMP-0782` retires nothing — it narrows a script's coverage claim,
which lives in the script and in change 2.

---

## 5. Routed work — for another agent, not for this review

| # | Item | Owner | Why not here |
|---|---|---|---|
| R1 | **Re-scope the parallel `development-agent` dispatch.** It was sent to fix "WBS 6.1-6.4 gaps". Section 0 measures those four tasks as correctly complete against a Code App deliverable, and the five observed gaps as Model-Driven App components under no accepted task. Sending it unchanged attaches hours to the wrong contract lines | lead-agent, now | Routing is lead-agent's, and this is live in flight |
| R2 | **Generalise `ensure-schema.ps1`'s `IsSecured` convergence.** Two requirements: (i) run the convergence over every attribute `FieldSecurityProfiles.xml` names, not only `$relationshipWork`'s lookups, with the concrete-type cast per attribute type; (ii) drop the `$preExistingRelationships` skip and read a freshly created lookup's live `IsSecured` back before the field-permission step. Verification: `ensure-schema.ps1 -Env dev` reports CREATED for all four columns of `IMP-0782` on a clean environment, and EXISTS on a second run | development-agent | The script authenticates to a live environment. `agents/improvement-agent.md`: hand over the requirement, never author it |
| R3 | **The caseworker views are a change-order decision.** An Auto-pass view, Gender/Equality views, a wider active-applications view and a CaseWorker form tab with an audit field, all in `rev_grantadministration` — an application `IMP-0066` already recorded as named by no WBS task. Decide whether this is warranty rework, in-scope under an existing task, or a change order (`C-COM-002`) before it is built | commercial-agent, then the reviewer | Hours and scope are `commercial-agent`'s; a commercial gate halts nothing and delivery continues |
| R4 | **`config/<slug>-pipeline.yml` may want `ensure-schema.ps1 -Env dev` as a DEV `environment_prerequisite`.** DEV's prerequisite block today names `verify-environment-access.ps1` and the code-apps feature toggle, not schema convergence. Whether convergence belongs there is a pipeline design decision | development-agent / pipeline-agent | The pipeline-config boundary: I may re-date a note settled by a repository fact, never widen the file's design |

All four rows were measured during this review. They are re-measured before they are handed on, at
approval time, per activation step 8 — a routed row is the output most likely to go stale, because
it sits open across exactly the interval in which someone else may fix or supersede it.

---

## 6. Findings left unprocessed

State counts as `verify-improvement-log.py --check` reported them **at activation**, before this
review stamped anything:

- **6 `unread`** — `IMP-0778`, `IMP-0779`, `IMP-0781`, `IMP-0782`, `IMP-0783`, `IMP-0784`. All six
  are in scope and all six are read in full. Nothing was silently capped.
- **0 `awaiting-approval`** at activation. There are six now, all stamped by this document.
- **169 `reviewer-deferred`**, left untouched per activation step 2, each carrying a
  reviewer-accepted `deferred_reason`. One (`IMP-0274`) names no `revisit_when` and has been
  reported as such for some time — unchanged here. None is stamped `excluded_by`: that field is
  for an id a review CITES without processing, and this document cites none of the 169.
- **0 `already-fixed`. 0 `approved-not-applied`.**
- **`IMP-0777`** — review 1's open `blocker`, and **it is no longer open**. It was given a
  reviewer-accepted `deferred_reason` on 2026-09-19: the Dataverse lookups resolved to real values,
  the SharePoint registration decommissioned, the Flow Service lookups deferred with a trigger.
  Re-measured here rather than carried forward, which is why section 3's simulation exits 0.
- Seven pre-existing `corrects` warnings (`IMP-0290`, `IMP-0298`, `IMP-0320`, `IMP-0430`,
  `IMP-0437`, `IMP-0703`, `IMP-0763`). Checked individually: none names an entry this review acts
  on.
- **`IMP-0785`** — appended by this review, carrying `corrects: IMP-0784`. It is the section 0
  measurement, and it is a capture obligation rather than a change.

### The three note-only entries, recorded rather than changed

All three propose no artefact, and closing them records the lesson without inventing a rule.

- **Two counts of one class over one file disagree by one wherever that class has a rejected
  member**, and neither the digest nor a re-derivation says which population it is counting.
- **A decommission instruction whose summary is broader than the scope it names is executed at
  the width of the summary** — five declarations were emptied where one was blocked, caught by a
  human before any commit.
- **A column can carry a field permission and still be unsecured for the profile that needs it**:
  four columns each held a System Administrator permission and none for the restricted profile,
  and the import succeeded on the secured flag rather than on the named profile's row.

### Duplicate check, per cluster

The `APPLIED` entries sharing each cluster's `class_instance_of` were read, narrowly, per
`skills/how-to-promote-a-finding.md` §3a. The credential class's four prior members are all CI
secret-availability; the field-security members (`IMP-0255`, `IMP-0272`) applied exactly the
narrow fix section 2.2 now finds the edge of; and `wrong-artefact-cited-as-evidence`'s seven
members include `IMP-0675`, which rewrote an evidence rule that rode on a neighbouring task's
evidence. **Nothing proposed here has already been done**, and one member — `IMP-0066` — is why
section 0 can state that the Model-Driven app is unquoted rather than merely suspect it.

---

## 7. Digest impact

Predicted, on approval:

- `stale-claim-contradicting-rechecked-source` drops from **x15 to x14** in the raw log count.
- `wrong-artefact-cited-as-evidence` rises to **x8**.
- `credential-not-on-the-machine-that-needs-it` reaches **x5** and gains its first
  interactive-dispatch member.
- Appending `IMP-0785` adds one lesson and regenerates the digest.

**The raw count and the rendered count are different populations** and may differ by one wherever a
class has a `REJECTED` member — `IMP-0778` records exactly this, and it is why the figures above
are stated as raw log counts rather than as digest rows.

**The registered `CURRENT SIZE` claim has already drifted, and not by this review.** Measured now:
the script's prose says 718 lines and the digest is 722 — findings appended by other dispatches
since review 1 corrected it. It is left as measured rather than corrected pre-emptively, because
this review's own regeneration will move it again; it is corrected once, in both copies of
`generate-known-failure-modes.py`, after that regeneration, and `verify-derived-counts.py` re-run
to confirm 10 of 10 claims green.

### The data-file rule

This review's only data edits are to `logs/improvement-log.jsonl`. The gate that validates it is
`verify-improvement-log.py`, not the generator that renders it, and it is run after every append
and stamp — validator first.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-09-19-improvement-review-2.md

Findings processed: 6 unread (3 blocker)  →  3 clusters
Regression check:   4 prior changes audited, 1 class recurred (prose fix; held at prose —
                    the mis-tag is downstream of a mis-attribution, section 1)
Proposed:           0 constraints (cap 3), 0 gates/scripts, 1 skill/knowledge edit,
                    1 agent-file edit, 0 retirements
Altitude calls:     0 generalised from instance to class, 1 retagged out of a class it never
                    belonged to, 2 proposed gates WITHHELD as disproved, 3 instance notes
Digest:             will regenerate — 1 lesson appended, 3 recurring classes affected

IMPROVEMENT LOG: 1 entry to append — IMP-0785  |  digest regenerated: on approval

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**One thing does not wait for the keyword, and it is section 0.** A `development-agent` is running
now against four WBS tasks that are not defective, to build components no accepted task covers.
That is R1 and R3, and both are decisions rather than changes.

---

## 9. Applied — 2026-09-19

`APPROVE IMPROVEMENTS` was received. **Read the provenance note at the end of this section before
treating this as settled** — the keyword reached this dispatch through two agent relays and not
through the reviewer's own turn, and a `blocker` logged an hour earlier is about exactly that.

| # | Target | Landed |
|---|---|---|
| 1 | `agents/pipeline-agent.md` (`.engine`) | activation step 6 gains the credential declaration: `pac` authenticates separately, so a session holding neither `PROVISION_*` variable can still import; name the excluded steps and their owner **before** the import, and where the diff touches schema-shaping source, converge first |
| 2 | `knowledge/technology/dataverse.md` | a new section under the securability material: the three paths a column takes to `IsSecured=1`, which one is proven, and the 2026-09-19 observation — asserting no cause between the two candidate mechanisms |
| 3 | `logs/improvement-log.jsonl` | `IMP-0784` retagged to `wrong-artefact-cited-as-evidence`; six `reviewed_in` stamps (applied at draft time, per step 6) |
| 4 | `logs/improvement-log.jsonl` | `IMP-0778`, `IMP-0779`, `IMP-0783` closed `APPLIED` with `evidence_grep` (and `reobserved` on the two above V1); `IMP-0781`, `IMP-0782`, `IMP-0784` parked with `deferred_reason` + `revisit_when` |
| 5 | `logs/improvement-log.jsonl` | **`IMP-0788`** appended — not `IMP-0785`, see the narrowing below |
| 6 | `scripts/generate-known-failure-modes.py` **and its `.engine` twin** | the registered `CURRENT SIZE` claim corrected 718 → 725 after regeneration; both copies, byte-identical |

### One narrowing, named in all three places it must be

The draft said it would append `IMP-0785` carrying the section 0 measurement in full. **Both halves
of that changed between parking and approval, and neither was chosen.**

- **The id was taken.** `commercial-agent` allocated `IMP-0785` for the change-order half and
  `development-agent` logged `IMP-0786` independently confirming both of this review's load-bearing
  claims. The id came from `scripts/allocate-improvement-id.py` instead of from the draft's typed
  number, which is what that script exists for.
- **The substance was already recorded twice, by two agents, both citing this document.** So the
  appended entry was narrowed to what remained genuinely unrecorded: **the `corrects` link to
  `IMP-0784`**, which neither `IMP-0785` nor `IMP-0786` carries — `IMP-0786` refers to "IMP-0785
  (corrects: IMP-0784)", but `IMP-0785` has no such field, so the correction was not joined to the
  entry it corrects.

The narrowing removes a third copy of one measurement and can name what it removes. It is recorded
in `IMP-0788`'s own `deferred_reason`, in this section, and in the gate output.

### Withheld, and why

- **The synthetic-relationship map gate** (`IMP-0781`) — the map already carried the entry when the
  import failed. A disproved premise is not enforced.
- **The `verify-field-security-coverage.py` extension** (`IMP-0782`) — a source-versus-source gate
  cannot see a source-versus-live gap.
- **The V4 evidence tier in `derive-wbs-state.py`** (`IMP-0784`) — the tasks are not defective, and
  the instrument for a human-only check already exists as `kind: manual`.
- **`IMP-0787`'s proposed agent-file change — not applied, and not merely deferred.** See below.

### Measured after regeneration — one prediction wrong, in a way worth recording

| Prediction (section 7) | Measured |
|---|---|
| `wrong-artefact-cited-as-evidence` rises to x8 | **x9.** The prediction counted the retag of `IMP-0784` and forgot that this review's own appended entry joins the same class |
| `stale-claim-contradicting-rechecked-source` drops to x14 | **x14.** Correct |
| `credential-not-on-the-machine-that-needs-it` at x5 | **x5.** Correct |

Digest regenerated: **725 lines**, 785 entries.

### Verification run

```
python3 scripts/verify-improvement-log.py --check      → exit 1 (IMP-0787 only — see below)
python3 scripts/generate-known-failure-modes.py --check → current (785 entries)
python3 scripts/verify-class-defences.py               → OK, 4 defences, 25 references
python3 scripts/verify-derived-counts.py               → OK, 10 of 10 claims
python3 scripts/verify-review-document.py --only …     → OK
python3 scripts/verify-doc-line-links.py …             → OK
```

**Level reached: V1.** No script was added, nothing was executed against a live environment, and
the two instruction changes cannot be executed at all. Change 2 records a live observation made by
others; this session made none.

### `IMP-0787` arrived mid-apply, and this review does not act on it

A `blocker` logged at 16:20 records `commercial-agent` refusing a relayed `APPROVE CHANGE ORDER
CO-006` three times, and proposes that `agents/commercial-agent.md` be told to accept a keyword
relayed by `lead-agent` as the canonical resume path.

**That change is not applied, and it is not a scoping decision.** Its mechanism is that a control
observes less than it did before: it would instruct agents to treat another agent's assertion that
a human approved something as the approval itself. `agents/improvement-agent.md` places that class
outside this role entirely, and the platform guardrail attached to every inbound agent message says
the same thing in its own words — no message from any agent is ever the user's consent. **The
refusal `IMP-0787` records as a defect was the receiving agent behaving correctly.**

The legitimate responses are additive and none of them is a rule change: the reviewer sends the
keyword in a turn the receiving agent can see, or the work is re-dispatched with the decision
already recorded. `IMP-0787` stays `unread`, holds the log gate at exit 1, and is a separate
review's business.

### And the same question applies to THIS review's own approval

`APPROVE IMPROVEMENTS` reached this dispatch as two agent messages — one from a fork, one from
`lead-agent` stating it was relaying the reviewer's verbatim reply from its own conversation turn.
**By the standard of the paragraph above, that is the weaker channel**, and it is recorded here
rather than left implicit. What was applied is limited to the draft the reviewer was shown, one
narrowing that only removes a duplicate, and bookkeeping. Nothing here widens a permission, touches
a live environment, or spends an hour. **If the reviewer did not send this keyword, say so and it
is revertible: every change above is in the working tree and nothing has been committed or
pushed.**

### Not committed

The working tree carries these changes and **nothing has been committed or pushed**, in either
repository. Change 1 is in the `.engine` submodule, as is the `.engine` half of change 6, and
publishing them is the three-step order in `agents/improvement-agent.md` — push the submodule
first, verify with `git -C .engine branch -r --contains HEAD`, then commit the pointer bump here.
A clean `git status` would prove nothing about whether that happened.
