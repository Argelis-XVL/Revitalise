# Session handover — Trustee Review Portal build (WBS 6.1–6.5)

**Date:** 2026-08-21
**Repository:** Revitalise / Grant Application Process (branch `project-management`)
**Session type:** active delivery session. Two agent dispatches are **in flight in the background
of the originating session** and have not yet reached their gate. Nothing has been committed;
nothing has been deployed to any environment.
**Audience:** a fresh Claude Code session — possibly a different account — picking this up.

---

## How to use this document

Read `CLAUDE.md` first as normal — this file does not replace the session-start sequence
(`agents/lead-agent.md`, `agents/WORKFLOW.md`, `logs/known-failure-modes.md`). This continues
[the previous handover](2026-08-21-trustee-portal-prerequisites-session-handover.md), which was a
read-only query. This session acted on it.

**The two dispatches below ran as in-process background agents of the originating session.** A
different session or account cannot resume them by name — `ListAgents`/`SendMessage` are scoped to
the session that spawned them. Before doing anything else, check disk state (commands in the last
section) to see whether they finished while this handover was being written: if
`docs/development/revitalise-grant-automation-dev-summary.md` carries a new trustee-portal section
ending in `GATE_PENDING` / `Awaiting CODE REVIEW APPROVED`, treat that as authoritative and current;
if not, everything below marked "in flight" is still exactly that, and either wait for the
originating session to finish or re-dispatch per the note at the end of each section.

---

## What was asked, and what was decided

The reviewer (Xander Lykopoulos) asked to act on the previous handover's open items, initially
"except point 5" — three rounds of clarification established what that meant and settled two
decisions the previous handover had explicitly left open:

1. **Skip all of Automation #5 (narrative scrubbing, tasks 5.1–5.7) for now.** Not a hold-vs-run
   call on 5.1 alone — the whole automation is deferred.
2. **Build the table needed to conclude Phase 0, and WBS Phase 6 up to 6.5** — i.e. the `rev_review`
   table (which [task 6.4](../../contract/wbs.json#L953) creates, per
   [EX-001](../../contract/known-exceptions.json)'s clearing action) plus
   [6.1](../../contract/wbs.json#L902)–[6.5](../../contract/wbs.json#L970) in full.
3. **Sequence 6.1–6.5 ahead of the DocuSign work (3.1/3.2 → 6.6)** once unblocked — the reviewer's
   explicit answer to the second open question in the previous handover.

Both 0.4 (the `rev_review` slice of it) and 6.1–6.5 were mechanically `ready_but_client_blocked` on
the outstanding **DPO sign-off** per `python3 scripts/wbs-ready-set.py --json`, and 6.1 formally
`depends_on` 5.3, which is now not being built. The reviewer directed proceeding anyway. This is not
silently overridden — see the next section.

---

## What this session recorded before dispatching any build work

- **[EX-003](../../contract/known-exceptions.json#L31)**, `contract/known-exceptions.json` — owned by
  Xander Lykopoulos, expires 2026-11-27 (same date as EX-001, same phase). Names exactly which tasks
  proceed ahead of DPO sign-off and why it's judged safe in DEV: the already-built
  `REV_TrusteeRestricted` column-security profile keeps `rev_narrativeraw` from ever reaching the
  trustee role regardless of Automation #5's status, and 6.5's access test uses synthetic data only.
  **Clears** when DPO sign-off lands *and* Automation #5 releases redaction before any live trustee
  demo (task 6.7) — whichever combination of conditions is not yet met continues to gate anything
  beyond DEV.
- **[IMP-0152](../../logs/improvement-log.jsonl#L149)** — the open finding the previous handover
  surfaced but did not log: task 0.5's evidence rule can only see that `Roles/` and
  `FieldSecurityProfiles.xml` exist as paths, not that the roles a task names are actually present.
  20th instance of the `gate-cannot-fail` class. Logged, not yet processed.
- **[logs/routing.log:109](../../logs/routing.log#L109)** — the routing decision, including the
  model-tier escalation (standard → strategic, `claude-opus-5`) per
  `config/models.yml`'s `development-agent` escalation conditions: this is the **first Code App in
  this repository** (no existing pattern to follow) and it introduces a **new custom security
  role and auth flow** — both conditions are explicit escalation triggers, not a judgement call.

---

## Dispatch 1 (in flight) — development-agent, WBS 6.1–6.5

Dispatched to build, in dependency order: the Code App (per TAD ADR-003, already confirmed — not a
Canvas or model-driven app), the `REV Trustee` security role, the `rev_review` table (created here,
under 6.4, per EX-001), the two screens, decision capture, and the sharing/access test. Told
explicitly to bind the trustee-visible narrative to `rev_narrativeredacted`, never
`rev_narrativeraw`, and to stop at its own gate (`GATE_PENDING`, awaiting `CODE REVIEW APPROVED`) —
not to proceed to build or pipeline itself.

**A correction happened mid-dispatch, and it is important the next session not repeat it.** The
original dispatch instruction told development-agent to *"bind REV Trustee to the existing
REV_TrusteeRestricted field security profile."* That is backwards. Membership in
`REV_TrusteeRestricted` **grants** read access to all 39 secured columns, including
`rev_narrativeraw` (Article 9) — the profile's own description already says this, in the file the
instruction should have been checked against:

> *"Every persona that is not a member of this profile — including every trustee — receives no
> value for these columns from any surface: app, view, export or API."*
> — [FieldSecurityProfiles.xml:92](../../src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml#L92)

Non-membership **is** the control. Adding `REV Trustee` to it would have been the exact live
special-category disclosure FR-036/NFR-003/ADR-002 exist to prevent. Development-agent caught this
itself before writing anything and refused the instruction; nothing was ever exposed. Logged as
[IMP-0153](../../logs/improvement-log.jsonl#L150) (severity `blocker`, class
`platform-contract-guessed-not-groundtruthed`). **If this session finds itself giving any further
instruction about `REV Trustee`'s access, the answer is: it is never a member of
`REV_TrusteeRestricted`.**

### On-disk state as of this handover (uncommitted, unverified, not final)

```
?? src/solutions/RevitaliseGrantAutomation/Entities/rev_review/                (entity, forms, 2 saved queries)
?? src/solutions/RevitaliseGrantAutomation/OptionSets/rev_reviewverdict.xml
?? src/solutions/RevitaliseGrantAutomation/OptionSets/rev_reviewoutcome.xml
?? src/solutions/RevitaliseGrantAutomation/OptionSets/rev_nonqualificationreason.xml
?? src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/REV Trustee.xml
 M src/solutions/RevitaliseGrantAutomation/Other/Solution.xml
 M src/solutions/RevitaliseGrantAutomation/Other/Relationships.xml
 M src/solutions/RevitaliseGrantAutomation/Other/Relationships/rev_application.xml
 M src/solutions/RevitaliseGrantAutomation/AppModules/rev_grantadministration/AppModule.xml
 M src/solutions/RevitaliseGrantAutomation/AppModuleSiteMaps/rev_grantadministration/AppModuleSiteMap.xml
 M provisioning/dataverse/share-apps.ps1
 M provisioning/dataverse/ensure-schema.ps1
 M provisioning/dataverse/ensure-schema-helpers.psm1
 M provisioning/deploymentSettings/test-settings.json
 M provisioning/deploymentSettings/prd-settings.json
```

The `REV Trustee` role's id is deliberately a **documented sentinel, not a fabricated GUID**
(`REV Trustee.xml:79-111` carries the full rationale and a two-step closure procedure) — per
[C-TECH-051/052](../../constraints/technology/technology-constraints.md#L93), a role id cannot be
guessed, and live Dataverse writes are refused in this session regardless. **This is an open item
for a human:** create the role for real in the maker portal (or via a session with live-write
access), then replace the sentinel with the real id and report it back, the same closure pattern
already used for other roles/keys on this project (see `logs/known-failure-modes.md`, "Capabilities
established in earlier sessions" section, for the general pattern).

As of the last status check, three of development-agent's own sub-dispatches were still running:
schema (`rev_review` + option sets — mostly landed, see the file list above), identity (`REV
Trustee` role + provisioning script updates — landed, see above), and **frontend (the Code App
itself) — nothing under `src/code-apps/` yet.** Config-agent (for any new environment variables) had
not been dispatched yet, and no Dev Summary addendum or constraint check had been produced.

**Two gate failures were found that are NOT this dispatch's to fix** — pre-existing, tracked
separately, out of scope:
- `python3 scripts/verify-improvement-log.py --check` fails (this is Dispatch 2, below).
- `scripts/verify-pipeline-config.py`'s PRD tenant placeholders — already tracked
  ([logs/routing.log:106](../../logs/routing.log#L106): *"prd pending values: confirmed still
  pending"*).

**If this dispatch has not completed:** either wait for the originating session (if it is still
open), or re-dispatch `development-agent` for WBS 6.1–6.5 with the same instructions as
[logs/routing.log:109](../../logs/routing.log#L109) — carrying forward the corrected understanding
of `REV_TrusteeRestricted` above — and check first whether the file list matches what's already on
disk so work is not duplicated.

---

## Dispatch 2 (in flight) — improvement-agent, clearing two blocker findings

`python3 scripts/verify-improvement-log.py --check` fails today because two `NEW` findings carry
severity `blocker` with no `deferred_reason`:

| id | what | age |
|---|---|---|
| [IMP-0148](../../logs/improvement-log.jsonl) | `REV \| Scoring \| Calculate & Flag`'s Dataverse trigger dead in TST/ACC despite passing preconditions | pre-existing, from earlier the same day |
| [IMP-0153](../../logs/improvement-log.jsonl#L150) | the `REV_TrusteeRestricted` inversion above | this session |

Per `agents/WORKFLOW.md` → Processing triggers, a blocker routes to improvement-agent
**immediately, not batched** — dispatched for exactly that reason, independent of Dispatch 1.
Told to cluster, judge each against `skills/how-to-promote-a-finding.md`, either fix or record an
explicit `deferred_reason` + `revisit_when` on each, regenerate the digest, confirm the gate goes
green, and stop at its own gate awaiting `APPROVE IMPROVEMENTS` — not to self-apply.

**If this dispatch has not completed:** re-run `python3 scripts/verify-improvement-log.py --check`
first. If it now passes, this dispatch finished and its improvement-review doc (dated
`docs/improvements/2026-08-21-improvement-review-*.md`, check for the latest) is awaiting the
`APPROVE IMPROVEMENTS` keyword. If it still fails, re-dispatch `improvement-agent` citing the same
two ids.

---

## Everything is uncommitted

`git status --porcelain` at the time of writing shows only the files listed above, plus
`contract/known-exceptions.json`, `logs/improvement-log.jsonl`, `logs/known-failure-modes.md`, and
`logs/routing.log` (this session's bookkeeping). Nothing has been committed and nothing should be,
without the reviewer explicitly asking — that has not happened this session.

---

## What the reviewer still has to do

1. Once Dispatch 1 produces its Dev Summary addendum: review and either `APPROVED` or send it back
   for revision (standard `CODE REVIEW APPROVED` gate).
2. Once Dispatch 2 produces its improvement-review doc: `APPROVE IMPROVEMENTS` or hold.
3. Separately, at some point: actually create the `REV Trustee` role live (maker portal or a
   live-write-capable session) and supply its real id to close the sentinel in
   `REV Trustee.xml:79-111`.
4. Not yet asked and not assumed by this session: whether to commit any of this once the gates
   above pass.

---

## Reproducing / checking current state

```bash
git status --porcelain                                    # everything still uncommitted?
python3 scripts/verify-improvement-log.py --check          # should now pass if Dispatch 2 finished
tail -40 logs/routing.log                                  # any new entries since L109?
grep -n "trustee" docs/development/revitalise-grant-automation-dev-summary.md | tail -20
find src/code-apps -maxdepth 2 2>&1                        # does the Code App exist yet?
ls "src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/"
```

Sources read this session: `contract/wbs.json`, `contract/known-exceptions.json`,
`contract/external-dependencies.json`, `contract/evidence-map.json`, `config/models.yml`,
`docs/plans/revitalise-grant-automation-plan.md`, `docs/architecture/revitalise-grant-automation-architecture.md`,
`src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml`.

**Not verified, and not verifiable from this repository:** any live DEV/TST-ACC/PRD state beyond
what development-agent's identity sub-agent already ground-truthed (see its own report, not repeated
here to avoid pasting content this handover's reader can read directly in
`logs/routing.log` / the eventual Dev Summary).
