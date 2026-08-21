# Session handover — trustee portal build reaches its gates, three improvement reviews pending

**Date:** 2026-08-21, 20:05
**Repository:** Revitalise / Grant Application Process (branch `project-management`)
**Session type:** active delivery session, stopped by explicit reviewer instruction with one dispatch
**still in flight in the background of this session.** Nothing has been committed; nothing has been
deployed to any environment. One live write (a Dataverse role create) may or may not have landed —
check disk state below before assuming either way.
**Audience:** a fresh Claude Code session — possibly a different account — picking this up, to send
`APPROVE IMPROVEMENTS`.

This is the third handover in this chain. Read them in order if you want the full history:
[prerequisites](2026-08-21-trustee-portal-prerequisites-session-handover.md) (read-only query) →
[build session](2026-08-21-trustee-portal-build-session-handover.md) (two stalled background
dispatches, corrected the `REV_TrusteeRestricted` inversion) → this one.

---

## How to use this document

Read `CLAUDE.md` first as normal — `agents/lead-agent.md`, `agents/WORKFLOW.md`,
`logs/known-failure-modes.md`. This document does not replace that sequence.

**The reviewer's explicit instruction for the next session: send `APPROVE IMPROVEMENTS`.** Three
improvement reviews are sitting at that gate — see "What needs APPROVE IMPROVEMENTS" below. That is
the one thing this handover exists to hand off cleanly. Everything else here is state you need to
know before or alongside doing that, not a second instruction competing with it.

**One dispatch below is an in-process background agent of *this* session**, exactly the trap the
previous handover described and exactly what happened to its own two dispatches: a different session
or account cannot resume it by name, `ListAgents`/`SendMessage` are scoped to the session that spawned
it, and it may have completed, partially landed, or done nothing between this being written and being
read. Check disk state (commands in the last section) before trusting anything below about it.

---

## What was asked, and what was decided

This session picked up the previous handover's two stalled dispatches (development-agent for WBS
6.1–6.5, improvement-agent for the two blockers), found both had made **zero** progress since the
handover was written — disk state and `verify-improvement-log.py --check` were byte-identical to its
snapshot — and re-dispatched both fresh, carrying forward the `REV_TrusteeRestricted` correction.
Both this time reached their own gates. Along the way:

1. The re-dispatched **development-agent** completed WBS 6.1–6.5 (the Code App, both screens,
   decision capture, the print route, four schema columns, two new build gates) and reached
   `GATE_PENDING`, held for `CODE REVIEW APPROVED` — **still open, not yet answered.**
2. The re-dispatched **improvement-agent** cleared the two original blockers, but in doing so found
   that an *earlier* review from the same day (review 4, 15:25) had reached its own gate and been
   left unapproved for five hours, so none of its five proposals existed on disk — logged as
   [IMP-0154](../../logs/improvement-log.jsonl). It produced **review 5**, carrying review 4's
   proposals forward.
3. Once development-agent's dispatch finished, its own findings pushed the improvement log past both
   its triggers again (19 `NEW`, several `blocker`), so a **second fresh improvement-agent dispatch**
   ran and produced **review 6** — which found, independently of anything it was asked to look at,
   that this project's CI has never once run on any commit (wired to a branch pattern,
   [`feature/**`](../../.github/workflows/ci.yml#L253), that has never existed here).
4. The reviewer then explicitly directed closing the one open item on the trustee role — creating
   `REV Trustee` for real in DEV, via the same service-account identity (`svc_grantapplications@
   revitalise.org.uk`, the active `pac auth` profile) that created the other two roles on
   2026-08-14 — and an **identity-agent dispatch for that is the one still in flight**, per the
   caveat above.
5. The reviewer then asked to stop this session and send `APPROVE IMPROVEMENTS` from a fresh one.

---

## What needs `APPROVE IMPROVEMENTS`

**Three review documents, all still open, none applied:**

| Review | Findings processed | What it's mainly about |
|---|---|---|
| [Review 4](../improvements/2026-08-21-improvement-review-4.md) (15:25) | — | The dead scoring-flow trigger (`IMP-0148`) — a canary probe, wired into smoke tests, a `C-TECH-064` amendment refusing metadata-only evidence |
| [Review 5](../improvements/2026-08-21-improvement-review-5.md) (18:14) | 9 NEW → 3 clusters | Carries review 4's five proposals forward unchanged (none ever applied); adds an allow-list check for `REV_TrusteeRestricted` membership; the stalled-review-gap fix itself (`IMP-0154`) |
| [Review 6](../improvements/2026-08-21-improvement-review-6.md) (19:57) | 19 NEW → 8 clusters | The CI branch-trigger defect; confirms `IMP-0155`'s fix is already on disk; rescopes a proposed GUID-uniqueness gate that would have false-failed 23 times; carries 4 and 5 forward again |

**Review 6's own recommendation, given to the reviewer before this session stopped:** apply all
three together, in the order 4 → 5 → 6, rather than as separate decisions — 6 already accounts for
everything still outstanding in 4 and 5. `python3 scripts/verify-improvement-log.py --check` exited
**0** while these three reviews were being written, but a fourth finding landed after review 6 was
authored ([`IMP-0170`](../../logs/improvement-log.jsonl#L167), see below) and put it back to **1**.
None of the three reviews account for it — process it alongside them, not as a reason to hold them.

Two questions review 6 put to the reviewer that a keyword alone doesn't answer, carried forward if
still unanswered when you read this:
- **Turn CI on knowing the first real run goes red?** (recommendation: yes)
- **Who opens `REV | Scoring | Calculate & Flag` in the Power Automate designer in
  REV-GrantApplications-ACC?** Asked in reviews 4, 5 and 6 now. No engineering proposal in any of
  the three closes this — it needs a named person with maker access.

Applying these reviews will edit `constraints/`, `scripts/`, `config/`, `skills/` and
`logs/known-failure-modes.md` per each review's own proposal list — read the reviews themselves for
exactly what changes, not this summary.

---

## The `REV Trustee` role: identity-agent finished, and the write needs the reviewer's own shell

**This actually completed after the rest of this document was drafted — do not re-dispatch
identity-agent for this, it will hit the identical wall.** The role is **not created.** The sentinel
`{PENDING-ROLE-ID-REV-TRUSTEE}` is still at
[`REV Trustee.xml:190`](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml#L190),
and [`Other/Solution.xml`](../../src/solutions/RevitaliseGrantAutomation/Other/Solution.xml#L170) still
has exactly two `type="20"` `RootComponent` entries (lines 170–171), not three.

identity-agent confirmed the pre-state live (zero rows for `name eq 'REV Trustee'` against DEV), then
ran the closure procedure's step 1. It was **refused twice**: first by a missing credential
precondition inside the script itself, then — after exporting the known-good auth triplet already on
record in this repo — by **this session's own Claude Code permission classifier**, before the call
ever reached PowerShell or Dataverse. This is not a Dataverse rejection and not a documentation gap;
it is the same class of harness refusal this project has hit four times before on other agents
(`logs/known-failure-modes.md` → "Operating constraints of this environment"), now logged as its
fifth instance and its first on an agent other than pipeline-agent
([`IMP-0170`](../../logs/improvement-log.jsonl#L167)).

**The reviewer needs to run this from their own shell, not from a dispatched agent:**

```bash
export PROVISION_APP_ID="077f1f90-3218-4a06-bc90-887464353aa7"
export PROVISION_CERT_THUMBPRINT="A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE"
pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev
```

Then read the real `roleid` back (a `pac env fetch` FetchXML query for `name eq 'REV Trustee'`,
`$select=roleid,name`, against `https://orge2b20d13.crm17.dynamics.com/`), substitute it for the
sentinel at `REV Trustee.xml:190`, add the matching `<RootComponent type="20" id="{real-id}"/>` to
`Solution.xml` right after lines 170–171, and confirm with
`python3 scripts/verify-solution-root-components.py src/solutions/RevitaliseGrantAutomation`.

**This reopened the improvement-log gate.** `IMP-0170` is `NEW`/`blocker` with no `deferred_reason`,
so `python3 scripts/verify-improvement-log.py --check` now exits **1**, not the 0 stated earlier when
review 6 was written — none of reviews 4/5/6 account for this finding, since it landed after all
three were authored. Route it to `improvement-agent` per the usual blocker trigger before or alongside
processing 4/5/6; it is a small, self-contained finding (a missing pointer in
`agents/development-agent.md`'s sub-agent table to the `Reviewer-Executed Operations` pattern
`pipeline-agent.md` already has).

---

## Development-agent's own gate: still open, separate from the improvement reviews

The Dev Summary at [`revitalise-grant-automation-dev-summary.md#L4802`](../development/revitalise-grant-automation-dev-summary.md#L4802)
is complete and was reported to the reviewer, awaiting `CODE REVIEW APPROVED`. Its own constraint
check reported `BLOCKED`, but on items that are inherited/environmental, not defects in what was
built: a pre-existing pipeline-config placeholder violation unchanged since before this session, and
two audit-logging constraints correctly left `unevaluable` for want of a live environment to query.
**Nothing in this session's exchange with the reviewer since that report addressed it** — it is not
answered by `APPROVE IMPROVEMENTS` and needs its own reply.

Four decisions were also put to the reviewer alongside it, unanswered as of this handover:
whether the four TAD-named schema columns built this session were in scope or unquoted work; whether
a write-lock on finalised review rounds (added unprompted) should stay; and ratifying two Code-App
conventions (CSS Modules; in-app view state instead of URL routes) as this project's precedent for
every future Code App.

---

## Everything is uncommitted

`git status --porcelain` at the time of writing shows the full session's work — the trustee portal
build, both improvement-log updates, all three review docs, and this handover — plus one unrelated
stray file, `docs/Import/~$Revitalise-WBS-Grant-Automation-v0.5.xlsx` (an Excel lock file, not
produced by this session; leave it alone). Nothing has been committed and nothing should be without
the reviewer explicitly asking — that has not happened this session.

---

## What the reviewer still has to do

1. Run the three-line shell command above, from their own machine, to actually create the `REV
   Trustee` role — no dispatched agent can do this, confirmed twice this session.
2. Send `APPROVE IMPROVEMENTS` (the instruction that prompted this handover) — decide whether that
   covers reviews 4, 5 and 6 together or individually, route `IMP-0170` alongside them, and answer
   the two questions in reviews 4–6 if still open.
3. Separately: `CODE REVIEW APPROVED` or revision feedback on the trustee-portal Dev Summary, and
   the four smaller decisions listed above.
4. Not yet asked and not assumed by this session: whether to commit any of this once the gates above
   pass.

---

## Reproducing / checking current state

```bash
git status --porcelain                                                      # everything still uncommitted?
python3 scripts/verify-improvement-log.py --check                           # exits 1 until IMP-0170 is
                                                                              # processed or deferred
grep -n "PENDING-ROLE-ID-REV-TRUSTEE" "src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/REV Trustee.xml"
                                                                              # still present as of this
                                                                              # handover — the role does
                                                                              # not exist yet
grep -n 'type="20"' "src/solutions/RevitaliseGrantAutomation/Other/Solution.xml"
                                                                              # still 2 lines, not 3
ls docs/improvements/2026-08-21-improvement-review-*.md                     # 4, 5, 6 all present, all unapplied
tail -25 logs/routing.log                                                   # any new entries since this session?
```

Sources read this session (in addition to everything the prior two handovers list): `config/models.yml`,
`agents/lead-agent.md`, `agents/WORKFLOW.md`, `skills/how-to-report-to-the-reviewer.md`,
`src/solutions/RevitaliseGrantAutomation/Roles/REV Trustee/REV Trustee.xml` (in full),
`src/solutions/RevitaliseGrantAutomation/Other/Solution.xml` (RootComponents section), the three
review documents' gate sections.

**Not verified, and not verifiable from this repository:** whether the reviewer has since run the
role-creation command themselves in a session with the right permissions — that is exactly what the
reproduction commands above are for.
