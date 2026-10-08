# Improvement Review — 2026-10-07

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 34 `NEW` → 17 clusters (30 unread, 3 fixed-in-flight, and 1 logged by this review while drafting)
**Trigger:** post-deploy batch — DEV deploy of build `revitalise-grant-automation-20261007-3` (narrative scrubbing, wbs:5.3,5.4,5.6) finished PARTIAL at V3, [pipeline.log L328](logs/pipeline.log#L328)
**Gate:** `APPROVE IMPROVEMENTS`
**Status:** APPLIED 2026-10-08, on the reviewer's "Approve improvements" (Xander Lykopoulos, sent as its own message, relayed verbatim by lead-agent). Rows 1–10 applied; row 11 not applied, declined at D-2. See §8. Draft-time note, kept: `reviewed_in` was stamped on all 34 entries at draft time (step 6).
**WBS:** system work, `wbs:system`, not billable. The findings themselves belong to wbs:5.1–5.6, 3.1–3.2 and 6.5 as each entry records.

---

## Summary

The narrative-scrubbing build produced a lot of learning and very little damage. Of 34 findings, 23 can close on this review: three build stoppers were already fixed in flight, the AI Builder facts the team had to discover by hand get one written home, and two small mechanical fixes stop two recurring time-wasters (a warning that fires on a log line that exists, and an advisory scan that halts the build 70 steps in when it could fail in seconds).

Eleven stay open on purpose, with an owner and a return condition, because their fix is someone else's routed work, can only be seen when the flow runs in DEV, or — for data residency — waits on the customer. D-1 asks you to confirm how the residency finding is held while it waits. Two more decisions are small: the written rule for near-miss approval wording (D-2), and two expired exceptions only you can re-date or clear (D-3).

---

## 1. Regression check — did the last review's changes work?

The previous review is [2026-10-05-improvement-review-3.md](docs/improvements/2026-10-05-improvement-review-3.md#L251), applied 2026-10-05 and committed in `55d366a`.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Rows 1–2: re-pointed two closed findings' proof; the missing-file message names deliberate deletion | 2026-10-05 | `learning-substrate-destroyed` / `gate-found-broken` | NO | Working. `--check` has run on every build since with 0 errors |
| Row 3: flow-gate expiry assertion runs on an in-memory corpus | 2026-10-05 | `gate-found-broken` | NO | Working. The flow gate ran green on builds 20261007-1/-2/-3 |
| Rows 4, 6: a fixture or a config mutation that changes nothing now fails | 2026-10-05 | `gate-cannot-fail` | NO | Working. No new `gate-cannot-fail` finding in 33 |
| Row 5: the access-test rule names a manual check with a pasted record | 2026-10-05 | C-TECH-068 | not exercised | No access test has run. Its routed follow-up (the precondition's text should say "paste each query into the Deployment Summary") is still not done; carried as R10 |

**Changes whose class recurred after a prose fix:** one, from an older review. The "advisory database moves overnight" lesson was recorded as prose on 2026-09-30 and the same thing halted two builds on 2026-10-06. That is the signal to escalate to a mechanical change, and row 7 does so.
**Changes whose class recurred after a gate:** none.

The approval wording on review 3 ("Approve Improvement", singular) was accepted and recorded as a deviation; cluster 14 turns that into a written rule.

---

## 2. Clusters and promotion decisions

```
CLUSTER: platform-fact-groundtruthed / platform-contract-guessed — AI Builder  (x4: IMP-1064, IMP-1071, IMP-1085, IMP-1087)
Altitude:   KNOWLEDGE — four separate facts about one platform service, each found by hand and
            each needed again by the next flow that calls a prompt or the extractor
Ladder row: "one instance, but the cause is general and a human needs to know it"
Becomes:    row 1 — a new "AI Builder" section in knowledge/technology/power-automate.md
Retires:    nothing
Cites:      IMP-1064, IMP-1071, IMP-1085, IMP-1087
Residual:   regional availability and the catalogue are point-in-time readings (dated in the
            text). The TAD already carries all four corrections (rev 19/20), so no routed work
```

```
CLUSTER: live-definition-drifts-from-source  (x1 new: IMP-1088; class x3 with IMP-0813, IMP-1041)
Altitude:   CLASS — third instance. A general gate already exists for FLOWS
            (verify-live-flow-definitions.py, run after every DEV import: 11/11, 0 diffs today).
            This instance is a new component type (an AI model) drifting in the other direction:
            the maker edits DEV and the copy in source goes stale
Ladder row: "second instance → generalise" — extend the existing gate, do not write a second one
Becomes:    row 1 (the knowledge line) + R7 (the extension, routed: it reads a live environment,
            which is delivery work under agents/improvement-agent.md, not this agent's to author)
Retires:    nothing
Cites:      IMP-1088
Residual:   until R7 lands, the only defence is the knowledge line telling the next copier to
            check modifiedon before a build
```

```
CLUSTER: capability-established — read-only live routes  (x2: IMP-1065, IMP-1078)
Altitude:   KNOWLEDGE (capability)
Ladder row: "a capability was established and could be lost again"
Becomes:    row 4 — two recipes under "Verifying live Dataverse state" in testing-tools.md
Retires:    nothing
Cites:      IMP-1065, IMP-1078
Residual:   A-CSR-01 in the city-derivation dev summary is still OPEN though the read that
            closes it exists (R6)
```

```
CLUSTER: flow definitions executed and compared locally  (x2: IMP-1073, IMP-1080)
Altitude:   KNOWLEDGE — one capability plus the one rule it needs to be trusted
Ladder row: "a capability was established" + "cause is general, a human needs to know it"
Becomes:    row 5 — "Flow Test Approach" in testing-tools.md names the simulator and requires
            one mutation per new rule and a stage-by-failure-path cross product
Retires:    nothing
Cites:      IMP-1073, IMP-1080
Residual:   the simulator and its test file are UNTRACKED today (git ls-files: not found). Row 5
            is applied only once they are committed; otherwise it is withheld (see §3)
```

```
CLUSTER: what run history shows, and where result() can find a failure  (x2: IMP-1079, IMP-1074)
Altitude:   KNOWLEDGE for IMP-1079; NOTE for IMP-1074
Ladder row: "cause is general" (1079); IMP-1074's gate change is WITHHELD — it rests on an
            unverified reading of result() inside a loop
Becomes:    row 2 — one paragraph under "Run history is a log"
Retires:    nothing
Cites:      IMP-1079, IMP-1074
Residual:   both are V5 (runtime) and stay open until the flow runs in DEV. The same
            per-iteration-failure question is the clearing action of the spent exception in R8
```

```
CLUSTER: an external advisory database changes overnight  (x2: IMP-1072, IMP-1081; with IMP-0961 x3)
Altitude:   CLASS — third occurrence after a prose lesson. The gate fired correctly every time;
            what costs is WHERE it fires: step 71 of 108, after ~70 green steps, twice in a day
Ladder row: "a recurrence after a prose change → escalate"
Becomes:    row 7 — move both audit steps to directly after improvement-log-check. npm audit
            reads only the lockfile (measured: exit 0 in a directory holding package.json and
            package-lock.json and no node_modules), so it needs no install step before it
            + row 6 — one knowledge line on the remedy order
Retires:    nothing
Cites:      IMP-1072, IMP-1081
Residual:   an advisory published after the audit step but before packaging still ships. That
            window is minutes, and the audit's own design accepts it
```

```
CLUSTER: a test that counted occurrences instead of the property  (x2: IMP-1082, IMP-1083)
Altitude:   NOTE — fixed in flight, and fixed the right way: the test now asserts "exactly one
            editable control", and five form mutations each fail it
Ladder row: "one instance, specific" — the general class (hand-maintained counts, x48) has no
            general gate and this review does not propose one
Becomes:    nothing new
Retires:    nothing
Cites:      IMP-1082, IMP-1083
Residual:   IMP-1082's description has the two controls the wrong way round; IMP-1083 records
            the correction. The wider lesson — a build that halts early leaves later steps
            unobserved — is what row 7 reduces
```

```
CLUSTER: untriaged-tool-warning  (x3: IMP-1089, IMP-1090, IMP-1091)
Altitude:   KNOWLEDGE — the rule (C-TECH-055) FIRED CORRECTLY both times: two green builds
            were refused hand-off until the warnings were triaged. Nothing escaped
Ladder row: "cause is general, a human needs to know it"
Becomes:    row 3 — the checker's recursive-loop rule ignores trigger filters (one result per
            write) and a new flow's checker figures are first seen at the build's lint step
            + row 6 — after a test-runner major bump, read the coverage step's stderr
Retires:    nothing
Cites:      IMP-1089, IMP-1090, IMP-1091
Residual:   no gate diffs a step's stderr against the triage table; the class stays at x27
            with C-TECH-055 as its defence
```

```
CLUSTER: platform-contract-guessed-not-groundtruthed — a limit our own gate enforces  (x1: IMP-1092)
Altitude:   CLASS (skill) — the property is general: a gate that enforces a platform limit
            encodes a counting convention, and the convention is itself a guess
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    row 9 — one clause in the "Field limits" row of the platform-contract skill
Retires:    nothing
Cites:      IMP-1092
Residual:   the instance is fixed (register row A-NS-26 now exists) and the DEV import accepted
            the flow; activation, which may validate nesting again, has not happened
```

```
CLUSTER: environment region contradicts the residency requirement  (x2: IMP-1063, IMP-1094)
Altitude:   NOTE + decision — the reviewer ruled on 2026-10-06 that residency is parked at the
            customer and does not block building. The finding's lane already says exactly that:
            governance lane, never halts a build, holds only a production deploy
Ladder row: "one instance" — the proposed region gate is DEFERRED: its allowed list is the
            customer's undecided answer, so written today it could only be red or empty
Becomes:    nothing; DEFER on the reviewer's own ruling (D-1). Measured by simulation: leaving it
            open instead makes the log gate warn on every run that the entry was "left behind"
            by an applied review, because the schema has no "reviewed, deliberately held" state
Retires:    nothing
Cites:      IMP-1063, IMP-1094
Residual:   the TAD records the measurement; the requirement in it still says UK. IMP-1094,
            logged while drafting, records the schema gap: a reviewed finding cannot keep
            holding production without a standing warning. One instance; a field is proposed
            only if a second governance finding needs the same hold
```

```
CLUSTER: documents that disagree with what is on disk  (x7: IMP-1062, IMP-1066, IMP-1067, IMP-1068, IMP-1069, IMP-1075, IMP-1086)
Altitude:   NOTE for all seven — each names one sentence in one file; no shared mechanism a tool
            could check without reading prose, which this project has measured five times at
            48–100% false
Ladder row: "one instance, specific"
Becomes:    nothing new. Three are already fixed on disk (1066, 1068, 1075) and close. Four are
            routed (R1–R4) and stay open until their fix lands
Retires:    nothing
Cites:      IMP-1062, IMP-1066, IMP-1067, IMP-1068, IMP-1069, IMP-1075, IMP-1086
Residual:   IMP-1075 proposed a gate for "MaxLength matches <column>" in a description.
            Measured: 0 occurrences across every Entity.xml today, because the one instance was
            rewritten. A phrase gate over a corpus of zero is a gate that cannot fail; WITHHELD
```

```
CLUSTER: a design that did not look at the solution's own reference data  (x1: IMP-1076)
Altitude:   AGENT — a human correction, and the information was in the same document
Ladder row: "an agent had the information and still did the wrong thing"
Becomes:    row 10 — a short subsection in agents/architect-agent.md
Retires:    nothing
Cites:      IMP-1076
Residual:   it is an instruction; nothing checks an ADR for an inventory
```

```
CLUSTER: a deploy overwrites a value the process owner is meant to edit  (x1: IMP-1077)
Altitude:   NOTE + routed delivery work (R5)
Ladder row: "one instance" — the fix is in a provisioning script and the TAD, not in the rules
Becomes:    nothing here
Retires:    nothing
Cites:      IMP-1077
Residual:   latent today: every seeded setting edited in the app reverts on the next deploy
```

```
CLUSTER: unwritten-policy-produces-a-coin-flip — approval wording  (x1: IMP-1061)
Altitude:   AGENT (workflow) — every gate-guarding agent must answer this, and two agents given
            the same words can answer differently today
Ladder row: "the order/policy of steps was wrong" — the policy is missing, not wrong
Becomes:    row 11, wording per D-2
Retires:    nothing
Cites:      IMP-1061
Residual:   matching cannot authenticate a human; the existing record rule does that job
```

```
CLUSTER: two-invocation-paths-disagree — the provenance check vs the build log  (x1: IMP-1093; class x21)
Altitude:   CLASS fix in the reader — the writer is an agent's free text and has already
            produced four shapes; the reader should accept any line whose status word is SUCCESS
Ladder row: "a tool could catch it mechanically" — it does; it just reads one shape
Becomes:    row 8
Retires:    nothing
Cites:      IMP-1093
Residual:   a SUCCESS line that names no artifact path still warns; that is correct
```

```
CLUSTER: output-shape-defeats-the-reader — an unlabelled coverage figure  (x1: IMP-1084)
Altitude:   NOTE — fixed in source (the runner now says "of COMMANDS")
Ladder row: "one instance, specific"
Becomes:    nothing new
Retires:    nothing
Cites:      IMP-1084
Residual:   none worth naming
```

```
CLUSTER: exception-outlives-its-own-violation  (x1: IMP-1070)
Altitude:   NOTE + decision — two exceptions expired on 25 September; only their owner can
            re-date or clear them
Ladder row: "one instance"
Becomes:    nothing; D-3
Retires:    nothing
Cites:      IMP-1070
Residual:   the commercial chain gate fails on them whenever it is run; it is not a build step,
            so nothing halts
```

### Measurements behind the rows

**Row 8, the provenance reader.** Run against every artifact name in `logs/build.log` and `build/artifacts/` (163 names). Today's pattern recognises 49. The proposed pattern — the line's first word after its tags (and an optional `wbs:` token) is `SUCCESS`, and the line names that artifact — recognises 53. All 4 added are real build successes written in another shape: an ASCII hyphen instead of an em dash, a `wbs:` tag before the word, a `(V2 packaged)` qualifier, and two lines naming the artifact later in the sentence. **0 lost.** Lines that start `BLOCKED` or `FAILED` and mention SUCCESS later are still not matched, because the anchor is the status word.

**Row 7, the audit move.** Simulated on a scratch copy of the build config: `verify-build-config.py` exits 0 before and after the move with an identical report. No test refers to the step names. The two steps lose the `*paths_app` / `*paths_cards` anchors (defined later in the file) and carry the same literal paths instead.

---

## 3. Proposed changes

> `Type` values come from the closed vocabulary: `constraint` · `constraint-amendment` ·
> `script` · `skill` · `knowledge` · `agent` · `template` · `other`.

| # | Type | Target | Change | Cites | Mechanically verifiable? | Wiring |
|---|---|---|---|---|---|---|
| 1 | knowledge | [power-automate.md](knowledge/technology/power-automate.md#L389), new section "AI Builder" before "Performance" | Six facts, each dated: (a) read a model's input/output contract from `msdyn_aitemplate` with `pac env fetch --xmlFile`, never `<all-attributes/>`; (b) no prebuilt PII model exists in this tenant; the prebuilt entity extractor finds phone numbers and addresses in US format only and takes at most 5,000 characters; (c) the generative-prompt template returns `text` and `finishReason` and no score, so it cannot carry a confidence threshold; (d) prompt models in a Switzerland environment are cross-geo only; (e) a prompt exports as component type 401, inline in `Customizations.xml`, its run spec is base64 gzip JSON, and its run action's shape exists only in a flow that calls it — read it from a saved-not-run DEV test flow, with a Compose to capture the output path; (f) every publish in the prompt builder creates a new run configuration, so check its `modifiedon` against your export before a build ships the copy | IMP-1064, IMP-1071, IMP-1085, IMP-1087, IMP-1088 | YES — `grep -c '## AI Builder' knowledge/technology/power-automate.md` = 1 | N/A |
| 2 | knowledge | [power-automate.md "Run history is a log"](knowledge/technology/power-automate.md#L337) | One paragraph: the inputs pane of a Select or Filter array shows its whole from-array, so secure its inputs whenever those rows carry text, even when it outputs only numbers | IMP-1079 | YES — needle `inputs pane of a Select or Filter array` | N/A |
| 3 | knowledge | [build-and-deploy.md "Solution Checker Quality Gate"](knowledge/technology/build-and-deploy.md#L332) | Two sentences: `flow-avoid-recursive-loop` ignores trigger filtering attributes and fires once per write to the trigger's own table, so decide each result from the filter against the written columns (the narrative suite's trigger-loop test does this for every flow); a new or changed flow's checker figures first appear at the build's lint step — read the SARIF breakdown, not only the count | IMP-1090, IMP-1091 | YES — needle `ignores trigger filtering attributes` | N/A |
| 4 | knowledge | [testing-tools.md "Verifying live Dataverse state"](knowledge/technology/testing-tools.md#L148) | Two read-only recipes that work under Auto Mode: `msdyn_aitemplate` / `systemform.formxml` for AI model and live form shapes; `<entity name="entity">` with `logicalname, entitysetname` for an entity set name and row counts — passed as `--xmlFile`, because the inline `--xml` form crashes pac 2.4.1 | IMP-1065, IMP-1078 | YES — needle `entitysetname` in that file (0 today) | N/A |
| 5 | knowledge | [testing-tools.md "Flow Test Approach"](knowledge/technology/testing-tools.md#L123) | Name the local flow simulator (`src/tests/narrative/wdl_sim.py`) as the way to execute a hand-authored flow's logic before any environment exists, and state its rule: an oracle comparison proves agreement only on what it enumerates, so each new rule gets a mutation run and each switchable stage is crossed with each failure path. **Applied only if both files are tracked at apply time** (untracked today); otherwise WITHHELD and reported | IMP-1073, IMP-1080 | YES — needle `wdl_sim.py`; precondition `git ls-files src/tests/narrative/wdl_sim.py` non-empty | N/A |
| 6 | knowledge | [build-and-deploy.md "Code Apps Build"](knowledge/technology/build-and-deploy.md#L6) | Two lines: the audit can go red with no repository change — for a transitive dev-only package the remedy order is an `overrides` entry, then a version bump, then a dated exception, always in both apps; after a test-runner or coverage-provider major bump, read the coverage step's stderr once and keep coverage `include` to source files | IMP-1072, IMP-1081, IMP-1089 | YES — needle `remedy order is an overrides entry` | N/A |
| 7 | other | [build config](config/revitalise-grant-automation-build.yml#L789), steps `code-app-audit` and `code-app-audit-cards` | Move both steps, with their comment block, to directly after [`improvement-log-check`](config/revitalise-grant-automation-build.yml#L95), replacing the two YAML aliases with literal paths. A new advisory then fails a build in seconds instead of after ~70 steps. The file belongs to development-agent; this is a reorder only, no step added or removed | IMP-1072, IMP-1081 | YES — `verify-build-config.py` exit 0 (simulated: identical report before and after) | already wired (both steps HARD, unchanged) |
| 8 | script | [verify-artifact-provenance.py L184](scripts/verify-artifact-provenance.py#L184) and its `.engine/` twin (`cmp` identical) | Recognise a build.log line whose first word after its tags (and an optional `wbs:` token) is `SUCCESS` and which names the artifact, instead of one fixed `SUCCESS — path` shape. Update the docstring's corpus paragraph, which names one of the four lines as missing. New selftest fixtures: the 20261007-3 line and the hyphen line must not warn; a `BLOCKED` line naming the artifact must still warn | IMP-1093 | YES — `--selftest`; corpus 49 → 53 matches, 4 true, 0 lost | `SUITE_GATE_EXEMPT` + already listed at [verify-build-config.py L731](scripts/verify-build-config.py#L731): its input is an artifact, which exists only after a build; it runs at [pipeline-agent activation step 3](agents/pipeline-agent.md#L68). Unchanged |
| 9 | skill | [how-to-verify-a-platform-contract.md "Field limits"](skills/how-to-verify-a-platform-contract.md#L44) | Add to the row: *"— including a limit this project's own gate enforces: the gate's counting convention is a contract too. When an artefact is built to within one unit of a limit, register how the limit is counted and name the first import as its check."* | IMP-1092 | N/A — instruction change | N/A |
| 10 | agent | [architect-agent.md](agents/architect-agent.md#L89), new subsection before "Before an ADR SUPERSEDES" | *"Before an ADR fixes a list, a lookup or a matching rule as a constant: list the reference tables in the data model and the settings keys that hold values in the same domain, say for each why it is or is not used, and classify each list as a format specification (a constant) or tunable vocabulary (a setting)."* Engine-level text; grepped for client literals before writing | IMP-1076 | N/A — instruction change | N/A |
| 11 | agent | **NOT APPLIED — declined at D-2.** [WORKFLOW.md "Human Gate Keywords"](agents/WORKFLOW.md#L532), after the "never proceeds" sentence | The matching rule chosen in D-2. Recommended text: *"Matching is case-insensitive and word-exact. A variant that changes a word form only (singular/plural) is accepted when it arrives as a message on its own, and the agent quotes it verbatim at the top of its output and says the act can be reverted. A variant that drops or changes an id, and any variant of `APPROVE TENANT`, `APPROVE PRD`, `ISSUE INVOICE` or `CLIENT ACCEPTED`, is refused."* | IMP-1061 | N/A — instruction change | N/A |

**Constraint budget:** 0 of 3 used.

**Two repositories.** Rows 9, 10 and 11 land in the `.engine` submodule (commit and push there first, then the pointer bump). Row 8 is a script with a byte-identical engine twin; both copies change together. Everything else is the instance repository.

---

## 4. Retirements

Retirement check performed across 88 live and 10 retired constraint rows (derived with the two `grep` commands in `agents/improvement-agent.md`). The one candidate examined was C-TECH-055 (every tool warning triaged), because three findings in this batch are its class. It is not redundant: it is what refused hand-off of two green builds this week, correctly. None retired.

The three spent entries in `config/flow-check7-exceptions.json` are still there and all three have now expired; their removal stays routed (R8).

---

## 5. Findings left unprocessed

**Deferred:** none

All 30 unread and 3 fixed-in-flight entries are processed, plus IMP-1094, logged by this review while drafting. The 277 reviewer-deferred entries are out of scope (activation step 2); none carries `corrects` against anything here.

### Dispositions, decided by `observable_at`

| Finding | `observable_at` | Disposition | Evidence or return condition |
|---|---|---|---|
| IMP-1061 | n/a | **CLOSE** on row 11 | needle: the matching sentence in WORKFLOW.md |
| IMP-1062 | n/a | **DEFER** | routed R4. `revisit_when`: the tst_acc ensure-schema EVIDENCE sentence states what is known instead of "ran it with -Env test" |
| IMP-1063 | V3 | **DEFER** on your 2026-10-06 ruling (D-1) | `revisit_when`: the customer answers the residency question, or before any import to PRD, whichever comes first |
| IMP-1094 | V1 | **DEFER** — no change proposed on one instance | `revisit_when`: a second governance-lane finding needs to hold the production guard after its review |
| IMP-1064 | n/a | **CLOSE** on row 1 | needle `## AI Builder` |
| IMP-1065 | n/a | **CLOSE** on row 4 | needle in testing-tools.md |
| IMP-1066 | n/a | **CLOSE** — already fixed in the TAD | needle ``Rev 19, added to this table (`IMP-1066`)`` |
| IMP-1067 | n/a | **DEFER** | routed R1. `revisit_when`: evidence-map tasks 5.3/5.4 name `REVNarrativeScrubFreeText` |
| IMP-1068 | n/a | **CLOSE** — already fixed in the TAD | needle ``rows are removed (`IMP-1068`)`` |
| IMP-1069 | V3 | **DEFER** | routed R2. `revisit_when`: rev_agerange's description no longer says "date of birth" and that build is imported to DEV |
| IMP-1070 | V3 | **DEFER** | D-3. `revisit_when`: EX-006 and EX-007 are re-dated or cleared and `verify-wbs-chain.py` names neither |
| IMP-1071 | n/a | **CLOSE** on row 1 | needle `## AI Builder` |
| IMP-1072 | V1 | **CLOSE** — fixed in flight | existing needle `"vitest": "5.0.3"`; audit re-run today in both apps, exit 0 |
| IMP-1073 | n/a | **CLOSE** on row 5 (if withheld, DEFER until the files are tracked) | needle `wdl_sim.py` |
| IMP-1074 | V5 | **DEFER** — nobody here can run the flow | `revisit_when`: one forced failure inside a loop in DEV settles what result() returns there |
| IMP-1075 | n/a | **CLOSE** — fixed in the same change; gate WITHHELD (0 instances) | needle `written by REV \| Narrative \| Scrub Free-Text (TAD section 5.5, wbs:5.3)` in Entity.xml (9 lines today) |
| IMP-1076 | n/a | **CLOSE** on row 10 | needle in architect-agent.md |
| IMP-1077 | V3 | **DEFER** | routed R5. `revisit_when`: seed-settings distinguishes create-only rows, and a DEV re-run leaves an edited row unchanged |
| IMP-1078 | n/a | **CLOSE** on row 4 | needle `entitysetname` |
| IMP-1079 | V5 | **DEFER** — row 2 still applies | `revisit_when`: the scrub flow runs in DEV and the action's run-history inputs read as secured |
| IMP-1080 | V5 | **DEFER** — row 5 still applies | `revisit_when`: the scrub flow's first DEV runs agree with the oracle on every recorded case |
| IMP-1081 | V1 | **CLOSE** — fixed in flight | existing needle `"shell-quote": "^1.11.0"` |
| IMP-1082 | V1 | **CLOSE** — fixed in flight | existing needle in IntakeContract.Tests.ps1 |
| IMP-1083 | V1 | **CLOSE** | needle `exactly one EDITABLE main-form control (C-TECH-077)` |
| IMP-1084 | n/a | **CLOSE** — fixed in source | needle `of COMMANDS (Pester's metric` in Invoke-Tests.ps1 |
| IMP-1085 | n/a | **CLOSE** on row 1 | needle `## AI Builder` |
| IMP-1086 | n/a | **DEFER** | routed R3. `revisit_when`: the TAD records DEV's cross-region setting as measured ON (2026-10-06) and moves the A-NS-23 check to TST/ACC |
| IMP-1087 | n/a | **CLOSE** on row 1 | needle `## AI Builder` |
| IMP-1088 | n/a | **CLOSE** on row 1 | needle `## AI Builder`; R7 carries the general extension |
| IMP-1089 | V2 | **CLOSE** with `reobserved` | build 20261007-3 (and -2) ran the coverage step with no "Failed to parse file" line; build -1's result file has it |
| IMP-1090 | V2 | **CLOSE** with `reobserved` | build 20261007-3 lint: Medium 15, matching the triage row, [build.log L170](logs/build.log#L170) |
| IMP-1091 | V2 | **CLOSE** with `reobserved` | same build; plus row 3 |
| IMP-1092 | V3 | **CLOSE** with `reobserved` | the DEV import of 20261007-3 accepted the flow at nesting depth 8, [pipeline.log L328](logs/pipeline.log#L328); register row A-NS-26 now exists |
| IMP-1093 | V2 | **CLOSE** on row 8 with `reobserved` | re-run the provenance check on 20261007-3 at apply; it must print no build.log warning |

Totals: 23 close, 11 defer. Simulated on a scratch copy of the log (see "Verified" below).

### Routed work (no file changed by this review)

| # | To | What | Re-measured 2026-10-07 |
|---|---|---|---|
| R1 | pm-agent | [evidence-map.json L320](contract/evidence-map.json#L320) expects tasks 5.3/5.4's flow as `REVAnonymise`; the built flow is `REVNarrativeScrubFreeText`. Re-point both rules | still `REVAnonymise` |
| R2 | development-agent | [rev_agerange.xml L55](src/solutions/RevitaliseGrantAutomation/OptionSets/rev_agerange.xml#L55) says the band is "worked out from date of birth"; the approved requirement says no date of birth is collected | still present |
| R3 | architect-agent | [TAD ADR-072, rev 20 note](docs/architecture/revitalise-grant-automation-architecture.md#L4260) says *Move data across regions* "stays unticked" in every environment. DEV was measured ON on 2026-10-06, before the prompt was built. Record the measurement and move the "can a prompt be created with it off" check to TST/ACC | still says "stays unticked"; no "measured ON" anywhere in the TAD |
| R4 | development-agent | [pipeline config L2010](config/revitalise-grant-automation-pipeline.yml#L2010) says the reviewer ran ensure-schema "with -Env test". The committed script refused that value on that date. Rewrite the sentence to what is known: run reported before the ACC import on 2026-10-05, script version unrecorded, first pipeline run of `-Env test` is the evidence. No question to you is needed | still says "-Env test" |
| R5 | development-agent, with architect-agent for ADR-010 | [seed-settings.ps1 L223](provisioning/dataverse/seed-settings.ps1#L223) overwrites every setting row on every deploy, so a value the process owner edits in the app reverts. Add create-only rows; the TAD names which rows are deploy-owned. lead-agent resolves the WBS task before dispatch | confirmed: PATCH on every row |
| R6 | development-agent | [city-derivation dev summary L206](docs/development/city-derivation-dev-summary.md#L206): A-CSR-01 is still OPEN; the read-only route in row 4 verified it in DEV on 2026-10-06 | still OPEN |
| R7 | development-agent | Extend the post-import live comparison to the AI model component: compare DEV's active run configuration with the copy in source, so a prompt republished in DEV after export is caught before build, not by a person remembering | no such check exists |
| R8 | automation-agent | Carried from review 3: delete the 3 spent entries in `config/flow-check7-exceptions.json`. All three have now expired | still 3 entries |
| R9 | lead-agent | `src/tests/narrative/wdl_sim.py` and `test_scrub_flow_definition.py` are untracked, though the DEV build used them as evidence. Commit them with the narrative feature; row 5 depends on it | untracked |
| R10 | development-agent | Carried from review 3 (R6): the access-test precondition ([pipeline config L1592](config/revitalise-grant-automation-pipeline.yml#L1592)) still does not say that each live query and its result are pasted into the Deployment Summary, which C-TECH-068 now requires | still absent |

---

## 6. Digest impact

| | Before | After (projected) |
|---|---|---|
| Log entries | 1089 | 1089 |
| Unread | 30 | 0 |
| Fixed-in-flight awaiting a review | 3 | 0 |
| Recurring classes | `live-definition-drifts-from-source` x3, `capability-established` x5, `gate-fired` x5 | unchanged — no new class reaches a second member |

Regenerated on apply, not now.

---

## What is still open

**The narrative flow has never run.** It imported into DEV and is switched off. Four findings (what run history shows, where a loop failure surfaces, whether the simulator matches reality, whether DEV's cross-region setting matters) can only close after its first DEV runs.

**Residency is undecided.** It is with the customer. Nothing in this review changes that; D-1 only decides what the log does meanwhile. A PRD deploy still needs your own `APPROVE PRD`.

---

## What you need to decide

**D-1. Record the residency finding as deferred on your ruling, rather than as an open blocker?**

**Problem** — All three environments are in Switzerland while the requirement says UK; you ruled on 6 October that this is parked with the customer and does not block building, but the log still counts it as an open blocker.
**Suggested fix** — Defer it, quoting your ruling, to come back when the customer answers or before any import to PRD, whichever is first; a PRD deploy still cannot happen without your own `APPROVE PRD`.
**What happens if you don't** — Kept open, it holds the automatic production check (which you may want), but every log check then warns that this review "left it behind", and a warning that is always there teaches people to stop reading warnings.
[routing.log L1320](logs/routing.log#L1320)

**Reviewer's answer (2026-10-08, verbatim):** "Data residency will be decided later." Applied as the suggested fix: deferred on your ruling.

---

**D-2. How should an approval that is almost, but not exactly, the keyword be treated?**

**Problem** — "Approve Improvement" (singular) was accepted last time on judgement; no written rule says whether a changed word counts, so two agents can decide differently.
**Suggested fix** — Row 11's wording: case never matters; a singular/plural difference is accepted when sent as its own message and quoted back to you; a missing or changed id, and any variant for tenant, production, invoice or client-acceptance acts, is refused.
**What happens if you don't** — Each near-miss stays a coin flip, and the four acts that cannot be undone by a commit have no stricter rule than the rest.
[WORKFLOW.md L532](agents/WORKFLOW.md#L532)

**Reviewer's answer (2026-10-08, verbatim):** "no, just leave approval wording to what it was." Row 11 not applied; the finding is closed as rejected.

---

**D-3. Re-date or clear the two expired DocuSign exceptions?**

**Problem** — Exceptions EX-006 and EX-007 ([L41](contract/known-exceptions.json#L41), [L53](contract/known-exceptions.json#L53)) expired on 25 September; you are their owner.
**Suggested fix** — Clear EX-006 if Emily's accuracy review of the template is no longer needed; re-date EX-007 to the DocuSign licence milestone, which is still outstanding.
**What happens if you don't** — The commercial chain check fails whenever it is run, which hides any new failure behind these two; builds and deploys are not affected.
[IMP-1070 in the log](logs/improvement-log.jsonl)

**Reviewer's answer (2026-10-08, verbatim):** "EX006, review is not needed anymore. EX007 Docusign is licensed." Both exceptions cleared, not re-dated.

---

Verified: `verify-improvement-log.py --check` before drafting (30 unread, 3 fixed-in-flight, 0 deploy-lane blockers, 1 governance, 3 fixed-by-later-finding warnings). `npm audit --audit-level=high` re-run in both code apps: exit 0. `npm audit` in a lockfile-only directory: exit 0. Build-config move simulated: `verify-build-config.py` exit 0, identical report. Provenance pattern measured over 163 artifact names. Needles for every closure checked against the tree. The disposition table was simulated on a scratch copy of the log with every proposed needle written into a scratch tree: `--check` exit 0, 0 unread, 0 awaiting approval, 0 open blockers, 0 warnings; `--target-env prd` exit 0. Leaving the residency finding open instead gives 1 warning and holds PRD (that measurement is what changed D-1). The real log differs from its pre-draft copy in exactly the 33 stamped lines plus the appended IMP-1094, which carries `reviewed_in` from birth. **Not verified:** rows 1–11 are not written, so no selftest for row 8 has run; nothing live was read except through files already in the repository; the narrative flow's runtime behaviour is unobserved.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-10-07-improvement-review.md

Findings processed: 34 NEW  →  17 clusters
Regression check:   6 prior changes audited, 0 classes recurred (1 older prose lesson recurred → row 7)
Proposed:           0 constraints (cap 3), 1 gates/scripts, 7 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
                    + 1 other (build-config step reorder)
Altitude calls:     4 generalised from instance to class, 13 left as notes
Digest:             will regenerate — no new recurring class

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied record — 2026-10-08

### Summary

Rows 1–10 are applied and row 11 is not, because you declined it. Of the 34 findings, 22 are closed, 1 is closed as rejected (the approval-wording rule), and 11 stay open with an owner and a return condition. Both expired DocuSign exceptions are cleared; the matching update to the external-dependencies record is not mine to make and is routed to pm-agent.

### The approval, and the answers as applied

**Reviewer's words, verbatim:** "Approve improvements", sent as its own message, relayed by lead-agent. This differs from `APPROVE IMPROVEMENTS` in case only, which is how every earlier case variant in the routing log has been treated. Your D-2 answer keeps the wording rule as it was, so no new rule was used to judge it.

- **D-1 — "Data residency will be decided later."** The residency finding is deferred on your ruling of 6 October, restated today. It comes back when the customer answers or before any import to PRD, whichever is first. A PRD deploy still needs your own `APPROVE PRD`.
- **D-2 — "no, just leave approval wording to what it was."** Row 11 is not applied; [WORKFLOW.md "Human Gate Keywords"](agents/WORKFLOW.md#L532) is unchanged. The finding is closed as rejected, with your words as the reason.
- **D-3 — "EX006, review is not needed anymore. EX007 Docusign is licensed."** Both exceptions moved to the closed list in [known-exceptions.json](contract/known-exceptions.json#L117) (EX-006) and [L132](contract/known-exceptions.json#L132) (EX-007), each with your words and the date. Neither was re-dated.

### What has been applied

1. **AI Builder facts have one written home.** [power-automate.md "AI Builder"](knowledge/technology/power-automate.md#L394): the six dated facts as drafted.

2. **A Select's run-history inputs are its whole from-array.** [power-automate.md L360](knowledge/technology/power-automate.md#L360), under "Run history is a log".

3. **The Solution Checker loop rule and where a new flow's figures first appear.** [build-and-deploy.md L352](knowledge/technology/build-and-deploy.md#L352). It names the `NoTriggerLoop` tests as the proof route.

4. **Two read-only live recipes.** [testing-tools.md L191](knowledge/technology/testing-tools.md#L191) adds two rows to the FetchXML table, plus [L194](knowledge/technology/testing-tools.md#L194): pass FetchXML as a file.

5. **The local flow simulator, and the rule that makes it trustworthy.** [testing-tools.md L130](knowledge/technology/testing-tools.md#L130). **Its precondition held at apply:** both simulator files are now tracked (committed in `85b2abd`), so this row was applied rather than withheld.

6. **The audit remedy order and the coverage-stderr check.** [build-and-deploy.md L33](knowledge/technology/build-and-deploy.md#L33).

7. **Both audit steps now run directly after the improvement-log check.** [build config L108](config/revitalise-grant-automation-build.yml#L108), steps 6 and 7 of 102 (were 71 and 72). The two YAML aliases became literal paths, and one comment word changed from "above" to "below" because the install step is now later in the file. `verify-build-config.py` exits 0 with a report byte-identical to before the move. No test names either step.

8. **The provenance check reads the status word, not one line shape.** [verify-artifact-provenance.py L96](scripts/verify-artifact-provenance.py#L96), with the `.engine/` copy byte-identical. Selftest 18 fixtures, PASS (was 14). Three mutations each fail it: reverting to the old shape, dropping the status-word anchor, and dropping the name boundary. Corpus over 162 artifact names: 49 recognised before and 53 after, all 4 added are real successes, 0 lost. **One correction to the docstring, found while doing so:** it said the 20260823-2 warning was true. It was false, because that build's success line exists and names the artifact later in the sentence ([L61](scripts/verify-artifact-provenance.py#L61)). Re-running the check on build 20261007-3 now gives PASS with no warning.

9. **A limit our own gate enforces is a platform contract too.** [how-to-verify-a-platform-contract.md L44](skills/how-to-verify-a-platform-contract.md#L44), wording as approved.

10. **Before an ADR fixes a list, inventory what the solution already holds.** [architect-agent.md L89](agents/architect-agent.md#L89), wording as approved. No client-specific words in it.

**Two repositories.** Rows 8, 9 and 10 changed files in the `.engine` submodule: `scripts/verify-artifact-provenance.py`, the skill and the agent file. So did the digest's size sentence in `scripts/generate-known-failure-modes.py` (620 to 627 lines, both copies), which regenerating the digest made stale. Publishing them takes a commit and push in `.engine` first, then the pointer bump here. Nothing is committed.

### Withheld

- **Row 11:** declined at D-2.
- **R9 (commit the simulator files):** already done in `85b2abd`, so not routed.
- **The two gates the draft already withheld** stay withheld. The Entity.xml phrase gate still has 0 instances to find (re-measured today). The loop `result()` gate still rests on an unverified reading of the platform.

### Findings disposed

| Disposition | Count | Findings |
|---|---|---|
| Closed | 22 | IMP-1064, 1065, 1066, 1068, 1071, 1072, 1073, 1075, 1076, 1078, 1081, 1082, 1083, 1084, 1085, 1087, 1088, 1089, 1090, 1091, 1092, 1093 |
| Closed as rejected | 1 | IMP-1061 (D-2) |
| Deferred, return condition applied verbatim | 11 | IMP-1062, 1063, 1067, 1069, 1070, 1074, 1077, 1079, 1080, 1086, 1094 |

Four of the closures carry a re-observation, because their defects were visible only when something ran. Three are build 20261007-3's coverage and lint steps. One is that build's DEV import, which accepted the flow at nesting depth 8.

**The DocuSign exception finding stays deferred, though its return condition is met in substance.** With both exceptions cleared, the commercial chain check names neither and exits 0. That run used a copy of the task-state file, because the unmodified check first stops on that file being stale (exit 2). Regenerating it is pm-agent's job (R12). The next batch closes the finding on that clean run.

### Routed work, re-measured at apply

| # | To | Status at apply |
|---|---|---|
| R1 | pm-agent | **Still open.** The evidence map still names `REVAnonymise` for tasks 5.3/5.4 |
| R2 | development-agent | **Still open.** The age-band description still says "date of birth" |
| R3 | architect-agent | **Still open.** The TAD still says the cross-region setting "stays unticked" everywhere |
| R4 | development-agent | **Still open.** [pipeline config L2011](config/revitalise-grant-automation-pipeline.yml#L2011) still says "-Env test" |
| R5 | development-agent, with architect-agent | **Still open.** `seed-settings.ps1` still updates every setting row on every deploy |
| R6 | development-agent | **Still open.** A-CSR-01 still reads OPEN |
| R7 | development-agent | **Still open.** No live comparison reads an AI model's run configuration |
| R8 | automation-agent | **Still open.** All 3 spent entries are still in `config/flow-check7-exceptions.json` |
| R9 | lead-agent | **Done** in `85b2abd`. Withheld |
| R10 | development-agent | **Still open.** The access-test precondition still does not mention the Deployment Summary record |
| R11 (new) | pm-agent | [external-dependencies.json L82](contract/external-dependencies.json#L82) still marks "DocuSign licence" outstanding. Record your 2026-10-08 statement that DocuSign is licensed. Until then the ready-set tool lists 3.1 and 3.4 as blocked on the client |
| R12 (new) | pm-agent | Reconcile task 3.1 now that Emily's named template review is waived for good (EX-006 closed). Regenerate the stale task-state file, then re-run the commercial chain check unmodified |
| R13 (new) | development-agent, with pipeline-agent | [pipeline config L1366](config/revitalise-grant-automation-pipeline.yml#L1366) and L1447 still label automation #3 "DEV ONLY (EX-006/EX-007)". Both exceptions are closed, so that label no longer states a live reason. Promotion beyond DEV still needs its own gates; this review decides nothing about it |

### Not in this review

Two findings were logged after the draft and are left for the next batch: IMP-1095 (the scrub flow imported cleanly but would not save in the designer; fixed in flight) and IMP-1096 (the callback-URL check's app-only token is refused). Each now carries `excluded_by` naming this document. **IMP-1095 is now the only thing holding the production guard.** It also limits row 5: the local simulator does not model the designer's flow checker.

### What is still open

**The narrative flow has never run.** Four findings still close only after its first DEV runs.

**Residency is with the customer.** It is deferred on your ruling, and a PRD deploy still needs `APPROVE PRD`.

Verified: `verify-improvement-log.py --check` exit 0: 0 awaiting approval, 0 open blockers, 1 unread (IMP-1096, logged after the draft), 1 fixed in flight (IMP-1095). With `--target-env prd` it exits 1, held only by IMP-1095. `verify-artifact-provenance.py --selftest` 18/18 in both copies, plus three mutations. `verify-build-config.py` exit 0, report identical before and after the move. `verify-engine-instance-split.py` exit 0. `verify-wbs-chain.py` against a copy of the task-state file: exit 1 before (EX-006 and EX-007 expired), exit 0 after. `verify-pipeline-config.py` and `verify-tad-coverage.py` exit 0. `npm audit --audit-level=high` in both code apps: exit 0. Every closure needle was checked against the tree. Digest regenerated; `generate-known-failure-modes.py --check` exit 0. `verify-derived-counts.py` OK after the size sentence was corrected. `verify-class-defences.py` and `verify-review-document.py` exit 0. **Not verified:** nothing live was read. The unmodified commercial chain check was not run clean, because of the stale task-state file. Nothing is committed.
