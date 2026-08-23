# Improvement Review 10 — 2026-08-22

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 unread `NEW` → 1 cluster, consolidated with 2 already-pending proposals against the same file
**Trigger:** reviewer request — update [code-apps.md](../../knowledge/technology/code-apps.md) for the new Power Apps CLI after a live check against Microsoft's own documentation
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The findings guard delivery tasks 6.1–6.5 (the Trustee Review Portal). No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`. **Nothing in section 3 has been applied — no rule, knowledge, constraint or script file has been touched.** Three things were done, because none of them edits a rule: `reviewed_in` was stamped on the three entries this document owns, one new finding was appended (IMP-0196, section 7), and the digest was regenerated.~~

> **CORRECTION, 2026-08-22 (improvement review 11, item 4).** The struck-through line above is stale. This review **was** approved and applied — see its own *Applied* section below, which is the half that is true. The header was written at drafting time and applying a review appends a section without rewriting it, so the two halves date from different moments.
>
> `scripts/verify-improvement-log.py` now fails on exactly this contradiction (`IMP-0204`). Read a review's disposition from its *Applied* section and from the working tree, never from its status header (`IMP-0181`).

---

## The headline

**This review makes the unapplied pile smaller, not bigger.** Three separate proposals already
target [code-apps.md](../../knowledge/technology/code-apps.md) and none has been applied: review 6's
item 9, review 9's item 1, and now this. Rather than stack a fourth, item 1 below is **one complete
rewrite of that file that discharges all four findings at once** — so approving this review reduces
the outstanding count against that file from three to zero.

**The migration is a full replacement for everything except sharing.** Every command in the current
toolchain table has a documented equivalent in the new CLI, and I verified each one against
Microsoft Learn today rather than taking it from the finding. The single gap is app sharing, and it
is the one thing this project cannot currently do on this machine anyway.

**The migration is also new information on a stuck blocker, which is the most valuable thing here.**
The Trustee Portal's Dataverse calls fail for real users with *"Invalid organization URL 'null'
provided"*, and the standing conclusion was: stop guessing locally, raise a Microsoft support
ticket, and do not re-run `pac code add-data-source` again because it is a confirmed no-op. The new
CLI binds data sources through a **different, actively-developed generator** and produces per-table
typed services instead of the one generic service that would not compile. That clears the "do not
retry without new information" bar. It is a cheap, non-destructive attempt that was not available
when that conclusion was reached.

**One correction to the finding, and it matters for timing.** Microsoft's page does not say
`pac code` *is* deprecated. The exact wording is that the new CLI *"will replace these commands,
which will be deprecated in a future release."* Nothing built on `pac code` stops working today, so
this is a migrate-because-it-is-better decision, not a migrate-or-break one. I have written the
knowledge file to say that precisely, because the difference decides whether the live app has to be
touched this week.

---

## 1. Regression check — did review 9's changes work?

**Review 9's five items were never applied, so there is nothing yet to audit.** I re-ran its four
needles against the working tree rather than trusting its table, and all four artefacts are still
absent. The outstanding count has gone from 14 to 19 in the day since.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Review 9 item 1 — code-apps.md environment toggle | **NO** | `platform-fact-groundtruthed` | YES — IMP-0194, IMP-0195 | Not a wrong-altitude call; the change was never made. **Folded into item 1 below** |
| Review 9 item 3 — `verify-pipeline-config.py` check 13 | **NO** | `declared-policy-not-mechanically-enforced` | — | Still proposed; unaffected by this review |
| Review 9 item 4 — `verify-constraint-verifiers.py` | **NO** | `gate-cannot-fail` | — | Still proposed. Would have caught [C-TECH-048](../../constraints/technology/technology-constraints.md#L90)'s unexecutable `Verify By`, which item 3 below reports |
| Review 9 item 5 — improvement-agent activation order | **NO** | `learning-substrate-destroyed` | NO | **Working in spirit** — I followed it manually and it saved a full pass over 23 settled entries. Its absence from the file is why that depended on me remembering |
| Review 6 item 9 — code-apps.md pac ground truth | **NO** (approved) | `platform-contract-guessed-not-groundtruthed` | YES — IMP-0195 refines it | **Superseded in part.** Its `getClient` workaround is a `pac code` workaround; the replacement CLI may not need it. **Folded into item 1** |

**Classes that recurred after a prose change:** none — no prose change was made.
**Classes that recurred after a gate:** none.
**The one finding worth recording from this check:** review 9's item 5 is the change that made this
review cheap, and it is still unapplied. Every future review pays that cost again until it lands.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-fact-groundtruthed  (x2 of x4 in scope: IMP-0194, IMP-0195)
Altitude:  CLASS for the read path, INSTANCE for the content — and the split is deliberate.
           The class now stands at x4 (IMP-0185, IMP-0193, IMP-0194, IMP-0195), which by
           skills/how-to-promote-a-finding.md §2 forbids another instance patch. But this class
           is not a defect class: every member carries capability:true and records "we went and
           got ground truth, here is what it says." There is no gate that prevents learning a
           platform fact a second time. So the generalisable property is not the fact — it is
           whether the fact REACHES anyone, and that is mechanical.
Ladder row: "One instance, but the cause is general and a human needs to know it" → knowledge/,
           for the content. Plus "The system's own memory failed" → a read-path change, for the
           routing: all four members of this class currently land in the digest's Unrouted
           section, which by that section's own words reaches nobody.
Becomes:   (1) a complete rewrite of knowledge/technology/code-apps.md — toolchain, ALM, and the
           generator-defect note — folding in review 6 item 9 and review 9 item 1;
           (2) one class name added to the digest routing table so this and every future
           ground-truthing finding reaches the agent about to hand-author a platform artefact;
           (3) an amendment to C-TECH-048, whose HARD rule text names a command that is going away.
Retires:   nothing. Review 6 item 9 and review 9 item 1 are SUPERSEDED rather than retired —
           they were never applied, so there is nothing on disk to withdraw. Their content is
           carried forward in item 1, not dropped.
Cites:     IMP-0194, IMP-0195, IMP-0161, IMP-0182, IMP-0186, IMP-0188, IMP-0192
Residual:  Three things this does not cover, all named in item 4 below. Group sharing through
           `pa app share` is undocumented and untested, so the file records it as unverified
           rather than claiming a replacement. The new CLI is not installed on this machine, so
           every `pa` command in the file is verified against Microsoft's documentation and NOT
           against execution — the file says so, per C-TECH-053. And the seven other repository
           files that name `pac code` are listed, not edited: correcting them is delivery work
           against a live app, not a rule change, and doing it here would put a build config
           edit behind an improvement gate.
```

**Why the two findings are one cluster and not two.** The second is a root-cause refinement of the
compile defect the first one's migration may make moot. Recording them separately would put a
`pac code` bug report and its own replacement in two different documents.

---

## 3. Proposed changes

Three items. **One is a file rewrite that clears three pending proposals, one is a two-word
addition to a routing table, one is a correction to a HARD rule that is about to name a command
that no longer exists.**

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | knowledge | [code-apps.md](../../knowledge/technology/code-apps.md#L23) | Replace the [toolchain table](../../knowledge/technology/code-apps.md#L23), the [ALM section](../../knowledge/technology/code-apps.md#L103) and the [header warning](../../knowledge/technology/code-apps.md#L9) with the `pa` CLI, verified against Microsoft Learn 2026-08-22. Add the generator-defect note, the environment toggle prerequisite, and the unverified group-sharing flag. Full drafted content below | IMP-0194, IMP-0195, IMP-0161, IMP-0182, IMP-0186, IMP-0188 | PARTLY — `grep -c "pac code" knowledge/technology/code-apps.md` falls from **11 to 10**, and every survivor is either the comparison table naming `pac code` as the superseded tool (5) or the past-tense historical record (5). None instructs anyone to run it |
| 2 | script | [generate-known-failure-modes.py](../../scripts/generate-known-failure-modes.py#L84) | Add `platform-fact-groundtruthed` **and** `environment-feature-flag-undeclared` to the *Before you hand-author a platform artefact* tuple, beside `platform-contract-guessed-not-groundtruthed`. Same moment, same reader. The second class is review 9's routing half, folded in here so approving this review alone leaves neither class unrouted | IMP-0194, IMP-0195, IMP-0185, IMP-0193, IMP-0182 | YES — both classes must disappear from the digest's [Unrouted section](../../logs/known-failure-modes.md#L392) and five lessons must move into that section |
| 3 | constraint (amend) | [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | The HARD rule text names `pac code add-data-source` as the only sanctioned data-access route. Change it to name the mechanism rather than the tool: *"a CLI-generated connector data source (`pa app add data-source`, or `pac code add-data-source` while it remains supported)"* | IMP-0194 | NO, and that is a pre-existing defect — see section 4 |

**Constraint budget: 0 of 3 used.** Item 3 amends an existing row; no new constraint is proposed.
I considered and rejected a rule of the shape *"do not build on an announced-deprecated tool."* It
would be speculative, unenforceable, and would tax every future run for a defect nobody has met —
all three of the disqualifiers in the promotion skill's §4.

### Item 1, drafted in full

This is the content to be applied on approval, not a summary of it.

**Replaces [line 9](../../knowledge/technology/code-apps.md#L9)** — *"The toolchain is `pac code`"*:

> ⚠️ Code Apps are **not** PCF controls and **not** web resources — do not use `pac pcfpush` or
> copy build output into `WebResources/`. The toolchain is the **Power Apps CLI** (`pa`); see below
> for the `pac code` commands it replaces.

**Replaces the [Toolchain section](../../knowledge/technology/code-apps.md#L23) entirely:**

> ## Toolchain
>
> Code Apps have **two** CLIs. The npm-based one is the current tool. The `pac code` verbs still
> work and are on an announced deprecation clock.
>
> | | Current | Superseded |
> |---|---|---|
> | Tool | **Power Apps CLI** — `npm install --global @microsoft/power-apps-cli`, commands prefixed `pa` | PAC CLI, `pac code` verbs |
> | Status | Microsoft's documented prerequisite for Code Apps | Ships with Power Apps SDK v1.0.4+; the new CLI *"will replace these commands, which will be deprecated in a future release"* |
> | Prerequisites | IDE, Node.js LTS, npm, Git | Node LTS **plus** the .NET-based `pac` CLI |
>
> Read the status wording exactly: `pac code` is **announced for deprecation, not deprecated**.
> Nothing built on it stops working today. Migrate because the replacement is better, not because
> the old one is about to break.
>
> Verified against Microsoft Learn on 2026-08-22 — the `pac code` reference page and the Code Apps
> overview's prerequisite list, which now names *Power Apps CLI* and no longer requires `pac`.
> **Verification level: documentation only (V2).** No `pa` command below has been executed on this
> project; `pa` is not installed on this machine. Install it and re-verify before treating any of
> it as executed ground truth.
>
> | Command | Purpose |
> |---|---|
> | `pa auth login` · `pa auth status` · `pa auth switch` | Sign in through the system browser; show and change the active account. **No certificate, no `Cert:\` PSDrive** |
> | `pa app init --display-name "<App Name>" --environment-id <env-id>` | Initialise the app in the current directory; writes `power.config.json` |
> | `pa app add data-source --connector dataverse --table <table-logical-name>` | Add a Dataverse table — generates a **per-table** `<Table>Model.ts` and `<Table>Service.ts` |
> | `pa app add data-source --connector <id> --connection-id <id>` | Add a non-tabular connector (Office 365 Users, Teams, …) |
> | `pa app add data-source --connector <id> --connection-ref <logical-name> --solution-id <guid>` | Bind through a solution **connection reference** rather than a per-user connection — the environment-portable form, and the preferred one here |
> | `pa app add dataverse-api --api-name <operation>` | Add a Dataverse action or function (`pa app find-dataverse-api` to discover one) |
> | `pa app refresh data-source --name <name>` | Regenerate one data source's files after a schema change |
> | `pa app remove data-source --connector <id> --name <name>` | Remove a data source |
> | `pa app run` | Start the Power Apps local host; open the URL labelled **Local Play**, in the same browser profile as the tenant |
> | `npm run build` then `pa app push` | Build, then publish |
> | `pa app share --principal <emails-or-object-ids> [--access play\|edit]` | Share a published app. **See the ALM section — group support is unverified** |
> | `pa connector list` · `pa connection create` · `pa connection list` | Find connectors and create connections without opening the maker portal |
> | `pa app list-environment-variables` · `pa app list-flows` · `pa app add flow` | Environment variables and solution-aware flows available to the app |
>
> Generated files land in `src/generated/models/` and `src/generated/services/`. Tabular services
> expose `create` / `get` / `getall` / `update` / `delete`.
>
> The Power Apps SDK (`@microsoft/power-apps`) is a separate npm package from the CLI. At v1.0 and
> above it **no longer needs `initialize`** — remove any import of it and any `isInitialized`
> gate. This project is on 1.3.0 ([package.json](../../src/code-apps/trustee-review-portal/package.json#L19)).

**Replaces the [ALM section](../../knowledge/technology/code-apps.md#L103) entirely:**

> ## ALM — How a Code App Moves Through Environments
>
> **Prerequisite, once per environment, by a human.** *Power Apps code apps* is a per-environment
> product feature and it is **off by default**: Power Platform admin centre → Environments →
> `<env>` → Settings → Product → Features → **Enable code apps**. There is no CLI verb and no
> organization attribute for it, so no script in this repository can set it or read it back, and a
> push into an environment where it is off fails. A System Administrator or Environment
> Administrator does this once, before the first push. This stopped a DEV deploy on 2026-08-22.
>
> 1. **Dev.** `npm run build`, then `pa app push`. On the **first** push the CLI places the app in
>    a solution by itself: the environment's *preferred* solution, else the all-components Default
>    solution, else no solution at all if Dataverse is absent. Set a preferred solution for the
>    environment, or pass `--solution-id <guid>` and be explicit.
>    **Only a GUID is accepted — a solution name is not.** `pac solution list` does not show
>    solution ids; read one with `pac env fetch -xf <query>` or from the maker-portal URL.
> 2. **Later pushes** do not change solution membership unless `--solution-id` is passed again.
> 3. **Promotion.** The code app is a solution component and travels in the managed solution
>    through Test/Acc/Prd like every other component. Code apps do **not** support Power Platform
>    Git integration or source-code integration — the solution is the only transport.
> 4. **Environment-independent data sources.** Prefer a connection reference (`--connection-ref`
>    with `--solution-id`) over a per-user connection, and `@envvar:<schema-name>` for dataset and
>    table arguments, so one app resolves correctly per environment. Note what this changes: a
>    `connectionReferences` key written by `pac code` is a **local manifest key only**, with no
>    corresponding Dataverse row; `--connection-ref` binds to a real solution component.
> 5. **CI/CD push, when the solution route is not used.** Set `PA_CLI_USE_SP_AUTH=true`,
>    `SP_CLIENT_ID`, `SP_CLIENT_SECRET`, `SP_TENANT_ID`, then `pa app push --non-interactive`.
>    **A maker must first share the app with the service principal at `edit` access — a service
>    principal cannot grant itself access, and environment-level permissions are not enough.** Use
>    the **Enterprise application** object ID, never the App registration object ID. This is a
>    one-time human step, not a pipeline step.
> 6. **Sharing.** Share with the persona's **Entra security group**, never with individual users in
>    Test/Acc/Prd (see `security-model.md` → App Access).
>    ⚠️ **Which tool does this is UNVERIFIED, and it is the one gap in this migration.**
>    `pa app share --principal` is documented for user email addresses and service-principal object
>    IDs; Entra **groups are not named**. `share-apps.ps1`'s code-app branch does take a group
>    explicitly (`-PrincipalType Group`) but cannot run on this Mac — it fails both on an assembly
>    conflict and on the absence of the Windows-only `Cert:\` PSDrive. **Until `pa app share` is
>    tested with a group object ID, treat group sharing as a maker-portal step**, and do not record
>    `pa app share` as a replacement for that script.

**New subsection, after the ALM section:**

> ### Why the generated Dataverse service did not compile
>
> Executed ground truth, `pac` 2.4.1, 2026-08-21, re-inspected 2026-08-22. Kept as a historical
> record: it explains the hand-written client in this repository, and it is the evidence behind an
> upstream bug report.
>
> - `pac code init` created only `power.config.json` — it did not scaffold React, so the Vite
>   project here is hand-authored.
> - `pac code add-data-source` generated the **generic** Dataverse connector typing with no
>   per-table models, and `pac code list-tables` / `list-datasets` returned an empty `{}` on all
>   three dataset forms against this connection, so the typed route was unreachable.
> - The generated `MicrosoftDataverseService.ts` **does not compile**: a parameter named
>   `MSCRM.IncludeMipSensitivityLabel` becomes a TypeScript identifier, and `.` is not legal in
>   one. The workaround is `getClient(dataSourcesInfo)` from `@microsoft/power-apps/data` — never
>   editing generated output.
>
> **That last one is a `pac code` generator defect, not a connector-schema problem.** The same
> parameter object in the connector schema already carries
> `"x-ms-name-for-model": "mscrm_include_mip_sensitivity_label"` — a valid, dot-free identifier
> whose whole purpose is to name generated code. This repo's copy of the schema carries **185** of
> these hints. The generator uses the raw wire name and never falls back to one. The failure is
> absent from the Code Apps overview's five documented Limitations, so it is an unreported tool
> defect: raise it at <https://github.com/microsoft/PowerAppsCodeApps/issues>, which that overview
> names for feedback and guidance. For a fix commitment on a bug, the same page directs you to the
> standard Microsoft support channel instead.
>
> Two consequences. The `pa` CLI uses a **different** generator, so the defect may simply not exist
> there — untested. And per-table generation may never surface that parameter at all, in which case
> the defect is obsoleted rather than fixed, and its upstream priority is correspondingly low.

**Also corrects, in the same file:** [line 28](../../knowledge/technology/code-apps.md#L28)'s claim
that `pac code add-data-source` generates *typed* models (it generated one generic service here),
[line 46](../../knowledge/technology/code-apps.md#L46) and
[line 51](../../knowledge/technology/code-apps.md#L51)'s project-structure comments, and
[line 129](../../knowledge/technology/code-apps.md#L129)'s *"re-run `pac code add-data-source` on
schema change"* → `pa app refresh data-source --name <name>`.

---

## 4. Retirements

**No fresh sweep, and I am saying so rather than implying one.** Reviews 8 and 9 reviewed all 47
active technology constraints within the last 36 hours and found no clean candidate. Nothing has
been retired or superseded since. A third pass today at strategic-tier cost would return the same
answer.

**One retirement-shaped finding from this review, and it is a real one.**
[C-TECH-048](../../constraints/technology/technology-constraints.md#L90) is HARD, and its
`Verify By` is *"Code review: no MSAL/token code outside the module documented in TAD §6."* By this
project's own rule — a constraint whose verification is not mechanically executable is a comment —
that is not a constraint. "Code review" names no command. Item 3 above corrects the rule's *text*
so it stops naming a disappearing tool, but it does not fix this, and I am deliberately not fixing
it here: the honest repair is the grep that review 9's item 4 already proposes
(`verify-constraint-verifiers.py`), which would have flagged this row on its own. Fixing it inside
this review would duplicate that work at a worse altitude.

**The standing consolidation candidate is unchanged and I am again not taking it.**
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35) and
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86) govern one subject and
could collapse into one enforced row. The reason for holding is the reason this review proposes
three items and not eight: nineteen approved or proposed changes are unapplied.

---

## 5. Findings left unprocessed

No silent caps.

| Finding(s) | Class | Why deferred | Revisit when |
|---|---|---|---|
| IMP-0185, IMP-0193 | `platform-fact-groundtruthed` | Same class as this cluster, but outside the dispatch scope and about different subjects. Item 2's routing fix **does** carry their lessons into the digest's platform-artefact section, so they are not left unrouted | The next review that processes the unread queue |
| IMP-0186 | `windows-only-cmdlet-dependency` | Its subject — that `share-apps.ps1` cannot run on this Mac — is *cited* in item 1's sharing note, but its own disposition needs the group-sharing test in section 6 to resolve first | The `pa app share` group test returns an answer |
| IMP-0187, IMP-0189, IMP-0190, IMP-0191, IMP-0192 | mixed; three are `blocker` | Unread, outside the dispatch scope. **These are the four blockers the log gate is reporting** and they need their own review — but see section 6: item 1 changes what the next step for them should be | Immediately after this gate, as their own dispatch |
| IMP-0188 | `platform-contract-guessed-not-groundtruthed` | Its connection-reference lesson is *carried* into item 1's ALM step 4, but its own entry covers more than Code Apps and should be closed by the review that reads it properly | The next review that processes the unread queue |
| 14 entries in awaiting-approval | mixed | Already processed by reviews 5, 6, 8 and 9 and parked at those gates. They need a keyword sent against the document each one names, never a second review | The reviewer sends the keyword |

**Three of those five blocker-bearing entries are the org-url-null failure**, and section 6 explains
why this review changes their answer.

**Expect nine warnings from the log gate about this table, and do not let anyone silence them.**
Naming a deferral makes the gate treat it as processed and demand a `reviewed_in` stamp. Stamping
these would be false — four are unread blockers that need their own dispatch, which is the opposite
of processed. The warnings are the accurate state; the alternative is a review that looks cleaner by
saying less. Logged as IMP-0196.

---

## 6. What you need to decide

**Should we install the new CLI and re-bind the Trustee Portal's Dataverse data source through it?**

My recommendation is yes, and to do it before raising the Microsoft support ticket. The standing
conclusion on the portal's *"Invalid organization URL 'null' provided"* failure was to stop
guessing locally and escalate, explicitly because re-running `pac code add-data-source` is a
confirmed no-op against the live connection. The new CLI is a different generator reached through a
different code path, and it produces a per-table typed service instead of the generic one that
would not compile. That is genuinely new information, which is the exact bar that conclusion set
for another local attempt. It costs two commands and does not touch the live app until a push.

The counter-argument is that it is another local attempt on a defect three findings have already
concluded is a platform problem, and that the ticket has been deferred once already.

**Does `pa app share` accept an Entra security group, and who tests it?**

This is the one thing that decides whether the migration is a full replacement or a partial one,
and I could not close it from evidence. Microsoft's `pa app share --principal` reference documents
*"comma-separated email addresses or Microsoft Entra object IDs for the users or service principals
to share with"* — users and service principals, with groups mentioned nowhere. A group object ID is
an Entra object ID, so it may well work; the documentation simply does not say. This project's
convention shares Code Apps with the persona's Entra security group
([code-apps.md line 114](../../knowledge/technology/code-apps.md#L114)), and the script that does
that today ([share-apps.ps1](../../provisioning/dataverse/share-apps.ps1#L173)) passes
`-PrincipalType Group` explicitly — so this is not a detail, it is the whole convention.

Until it is tested live, item 1 records group sharing as a maker-portal step and does **not** claim
`pa app share` replaces that script's code-app branch. This also keeps the corresponding
unvalidated-assumption row open rather than closing it on documentation. The test is one command
against DEV against the already-published app, and it needs a signed-in maker — which, on this
machine, means the identity question raised on 2026-08-22 has to be settled first.

**Do the seven other files that name `pac code` get corrected now, or when the migration runs?**

Item 1 changes the knowledge file only. These still describe the old toolchain and are **not** in
this review:
[build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L8),
[stack-overview.md](../../knowledge/technology/stack-overview.md#L79),
[the pipeline config's push step](../../config/revitalise-grant-automation-pipeline.yml#L677),
[the build config](../../config/revitalise-grant-automation-build.yml#L528),
[verify-code-app-column-bindings.py](../../scripts/verify-code-app-column-bindings.py),
[the portal's own dataverse README](../../src/code-apps/trustee-review-portal/src/dataverse/README.md#L9),
and the two deployment-settings files.

My recommendation is to leave them until the migration is actually executed, and to correct them in
that same change — a config or script edit is delivery work, and routing it through an improvement
gate is the wrong altitude. One of them carries a concrete trap worth naming now:
[the pipeline's push step](../../config/revitalise-grant-automation-pipeline.yml#L677) passes a
solution **name** (`pac code push --solutionName`), and the replacement command accepts only a
solution **GUID**. That step will fail on migration until someone reads the real solution id.

---

## 7. Digest impact

| | Before | After |
|---|---|---|
| Log entries | 192 | **195** — two appended by this review, one by a concurrent session |
| Distinct lessons | 192 | **195** |
| Recurring classes (x≥2) | 24 | 24 — `gate-fires-on-nothing` moves from x2 to x3 |
| Lessons in the Unrouted section | 31 | **30** — see the correction below |

**Correction, and I got this wrong in the draft.** This table predicted Unrouted would fall from
31 to 26. The measured result after applying item 2 is **31 → 30**. The four
`platform-fact-groundtruthed` findings were never in Unrouted at all: they all carry
`capability: true`, and the capability flag routes a lesson to *Capabilities established in
earlier sessions* ahead of the class routing table. Only `environment-feature-flag-undeclared`
(IMP-0182) actually moved. Item 2 still earns its place — it routes IMP-0182 out of Unrouted
today, and it routes any future `platform-fact-groundtruthed` finding that does *not* carry the
capability flag — but the digest effect I claimed was four-fifths overstated.

The generalisable point, logged as IMP-0198: **the digest has two routing mechanisms and the
capability flag silently wins.** Nothing in the review process makes that visible, so a review
reading the recurring-classes table will predict a routing effect for findings that were already
routed. Check where a lesson actually lands before claiming a routing change moves it.

Item 2 is the only change with a digest effect, and it is the one that decides whether any of this
is read. Regenerate with `python3 scripts/generate-known-failure-modes.py` and confirm with
`--check`.

### Bookkeeping already done, and one stamp deliberately not moved

`reviewed_in` is stamped on **IMP-0194**, **IMP-0195** and **IMP-0161** — the three entries whose
disposition this document now owns in full. Statuses stay `NEW`; nothing is marked `APPLIED` before
the keyword. This is the step whose absence cost a duplicated strategic-tier dispatch on 2026-08-21.

**IMP-0182's stamp stays on review 9, deliberately.** This review carries two of its three halves —
the knowledge content and the digest routing — but its pipeline-config prerequisite and the
`verify-pipeline-config.py` check remain review 9's items 2 and 3. It is a `blocker`, so moving the
stamp would point the log gate at a document that handles only part of it. The log gate will
therefore keep warning that IMP-0182 is cited here while stamped there; that warning is correct and
this paragraph is the answer to it.

**One finding appended: IMP-0196, and this review is what discovered it.** Writing section 5's
deferral table triggered nine warnings from the log gate, one per finding named there. The gate
treats any finding id appearing anywhere in a review document as a processing claim needing a
`reviewed_in` stamp — but the promotion skill *requires* a review to name every finding it
deferred. So the two rules pull against each other, and the gate penalises the review that names
its deferrals while a review that quietly drops them scores clean. Four of those nine are unread
blockers this document explicitly says need their own dispatch; stamping them to silence the gate
would have been a false claim, so I left them unstamped and logged the gate defect instead. It is
the **third** instance of a gate firing on something that is not a defect, so the fix belongs on
citation *position* rather than on another per-review explanation.

Nothing else was logged. The other two triggers that could have fired — reality contradicting a
document, and a human correction of agent output — are already recorded as the two findings this
review processes.

---

## 8. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-22-improvement-review-2.md

Findings processed: 2 NEW (unread)  →  1 cluster, consolidating 2 pending proposals
Regression check:   5 prior changes audited, 0 classes recurred after a change (none applied)
Proposed:           0 constraints (cap 3), 1 gate/script edit, 1 knowledge rewrite,
                    1 constraint amendment, 0 agent-file edits, 0 retirements
Altitude calls:     1 generalised from instance to class (digest routing),
                    1 left as knowledge content, 2 pending proposals superseded not stacked
Digest:             regenerated — 193 lessons, 24 recurring classes, Unrouted 31 → 26 on approval

IMPROVEMENT LOG: 1 entry appended — IMP-0196  |  digest regenerated: YES

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

**Verification performed:** 8 Microsoft Learn pages read (the `pac code` reference, the CLI command
reference, the npm quickstart, the Code Apps overview, connect-to-data, connect-to-dataverse, ALM,
and use-service-principal); the connector-schema claim confirmed by hand at
`commondataserviceforapps.Schema.json` lines 2534 and 2540, with 185 `x-ms-name-for-model` hints in
that file; `pa` confirmed absent from this machine; `pac` confirmed at 2.4.1.

**Not verified:** every `pa` command in item 1, because the CLI is not installed here — the drafted
content states that limitation in the file itself rather than implying execution. Group sharing
through `pa app share` is undocumented and untested, and is section 6's second decision.

**Gate state, unchanged by this review:** `verify-improvement-log.py --check` reported
`FAILED — 3 problem(s)` before this review and reports the same 3 after it. The 12 WARNINGs it
prints include 9 caused by section 5's deferral table (IMP-0196) and 3 that pre-date this review.
`generate-known-failure-modes.py --check` confirms the digest is current at 193 entries.
Every line-link in this document was resolved against the file it names and confirmed to point at
the line it claims — none were guessed.

---

## 9. Applied

`APPROVE IMPROVEMENTS` received 2026-08-22. All of section 3 applied, plus the
`verify-improvement-log.py` fix the reviewer approved by name — see the scope note below.

| # | Change | Where | Entries moved to APPLIED |
|---|---|---|---|
| 1 | code-apps.md rewritten for the `pa` CLI — toolchain, ALM, generator-defect note, environment toggle, unverified group sharing | [code-apps.md](../../knowledge/technology/code-apps.md#L23) | IMP-0194, IMP-0195, IMP-0161 |
| 2 | `platform-fact-groundtruthed` + `environment-feature-flag-undeclared` routed to *Before you hand-author a platform artefact* | [generate-known-failure-modes.py](../../scripts/generate-known-failure-modes.py#L84) | — |
| 3 | C-TECH-048 names the mechanism, not the retiring tool | [C-TECH-048](../../constraints/technology/technology-constraints.md#L90) | IMP-0194 |
| 4 | Citation position decides meaning: an id named only under a *Findings left unprocessed* heading no longer demands a stamp. Two selftest fixtures, including the over-suppression control | [verify-improvement-log.py](../../scripts/verify-improvement-log.py#L603) | IMP-0196 |

**Scope note, stated plainly.** Item 4 was **not** in section 3 when this review went to the gate —
it was IMP-0196's logged `proposed_change`, described in section 7. The approval named it
explicitly, and moving IMP-0196 to `APPLIED` without it would have made that status a false claim,
so it was applied. Recording the drift rather than quietly renumbering section 3.

**Entries rejected:** none.

**Findings appended while applying:** IMP-0198 — the digest-impact miscount corrected in section 7.

### Deferred entries left unstamped, deliberately

Eight warnings remain from the log gate. Three
pre-date this review (IMP-0148, IMP-0181, IMP-0182). Five are findings whose lessons items 1 and 2
partially carry and which this review's Cites columns therefore name — IMP-0185, IMP-0186,
IMP-0188, IMP-0192, IMP-0193. Their state was not changed, for two reasons: their content was
never reviewed, only borrowed; and stamping `reviewed_in` on a `NEW` entry pointing at an
already-approved document would make the gate tell the next reader to send a keyword that has
already been sent. The accurate encoding is `deferred_reason` + `revisit_when`, which is a
reviewer decision with an owner — recommended, not taken unilaterally. **The four unread blockers
(IMP-0187, IMP-0189, IMP-0191, IMP-0192) were deliberately left triggering**, because that trigger
is what gets them their own dispatch.
