# Failure Analysis (2026-08-09 → 2026-08-17) and Self-Learning System Design

**Author:** lead-agent, live session with Xander Lykopoulos
**Scope:** every build-agent and pipeline-agent failure in the last week, their root-cause classes,
why these two agents are the hotspot, and the design that makes the system remember.
**Evidence base:** `logs/build.log`, `logs/pipeline.log`, `logs/routing.log`,
`build/artifacts/.../manifest.json`, `config/revitalise-grant-automation-build.yml` inline comments,
`docs/development/revitalise-grant-automation-dev-deployment-handover.md`, and the 14 Claude Code
session transcripts for this project (~33 MB).

---

## 0. Executive summary

The system does not have a *capture* problem. It has a **read-back** problem.

build-agent and pipeline-agent already write forensic-quality post-mortems — `build.log` entries run
to 300 words with confirmed root causes, and build #6's manifest carries a structured
`defect_found_and_fixed_this_build` array with a `why_it_was_never_caught` field per defect. That is
already almost exactly the schema a learning system needs.

Nothing ever reads any of it back. build-agent and pipeline-agent are the only two agents in the
roster whose activation sequence loads **no** prior-experience input — not the handover document, not
their own logs, not the assumption register. So every build re-enters the same minefield with no map,
and the map it draws on the way out is written to a directory the next build overwrites.

Three findings carry most of the weight:

1. **21 distinct incidents** in eight days cluster into 8 root-cause classes. One class — *"the gate
   built to catch a defect was itself broken and could not fail"* — accounts for 4 incidents including
   a **HARD compliance gate (FR-016) that was a silent no-op from the day it was written**.
2. **The learning substrate is being destroyed.** Six builds, one artifact directory. Manifests for
   builds #1–#3 no longer exist; #6 overwrote #5 on disk.
3. **The manual learning loop already ran, and was not enough.** On 2026-08-14 you asked for it twice
   in explicit terms. It produced C-TECH-049/050/051, a new skill, and three verify scripts. On
   2026-08-16 and 08-17 the *same meta-classes* recurred. The loop learns one instance at a time,
   always one incident behind.

---

## Part 1 — What actually failed

### 1.1 build-agent

| # | Date | Failure | Detected by |
|---|---|---|---|
| B1 | 08-12 | All 15 OptionSet files wrapped in a redundant outer `<optionsets>` element; Role/Workflow/FieldSecurityProfile/EntityRelationship files stored identifying values as child elements where the packer expects root attributes. Both pack types failed. Resolved by **decompiling `SolutionPackagerLib.dll` with `ilspycmd`** | build-agent |
| B2 | 08-16 | `lint` (`pac solution check`) ran **before** `pack-managed` and pointed `--path` at the unpacked source folder. The command requires a packed `.zip`. **Broken since the file was written; survived builds #1–#4** because `auth` and `lint` were deferred together every time | build-agent, on first real auth |
| B3 | 08-16 | `secret-scan` gate scans the whole working tree, so a gitignored, never-committed provisioning certificate at `provisioning/certs/` triggered a BLOCKED. No version-control leak existed | build-agent |
| B4 | 08-16 | Three hardcoded schema-count assertions went stale (16→17 option sets, 88→94 attributes, 34→38 secured columns) — **broken by the agent's own approved schema additions in the same session** | build-agent |
| B5 | 08-17 | FR-016 gate's target path was missing its `.json` extension. `grep -r` on a nonexistent path exits 2, and the leading `!` inverts any non-zero exit to a pass. **A HARD compliance gate that never once read the scoring flow** | Found incidentally while editing the pattern list |
| B6 | 08-17 | `rev_careprovidedexample`'s shipped `<Description>` still named `rev_carersupport`, a column removed in the same build | Found by unpacking the zip and grepping |
| B7 | 08-14 | `pac solution pack` **silently dropped** all FormXml and SavedQueries content — 0 warnings, 0 errors — because no marker element in `Entity.xml` made the folders reachable. Solution shipped to DEV with 8 view files and 4 form files on disk and **0 views, 0 forms** created | Reviewer, in the maker portal |
| B8 | ~08-13 | `gitleaks detect` without `--no-git` scanned commit *history*, not the working tree. For two revisions none of the 47 files under `src/solutions/` was tracked, so C-TECH-001 recorded PASS while covering **none** of the delivered source | test-agent (D-006) |
| B9 | 08-17 | `pac solution check` reported results downloaded to `solution-checker/`; directory was empty afterward. Attributed to the repo path containing spaces. **Not investigated** | build-agent |
| B10 | all | `artifact_output` is hardcoded to `revitalise-grant-automation-20260810-1/`. Six builds, one directory, against WORKFLOW.md's mandated `<slug>-<date>-<n>/`. Manifests #1–#3 lost | This analysis |
| B11 | 08-14 | `rev_setting.rev_description` has MaxLength=500. Nothing in the build read `deploymentSettings/*.json`, so 4 of 11 seed rows failed only when run live against DEV | Live execution (D-021) |

### 1.2 pipeline-agent

| # | Date | Failure | Detected by |
|---|---|---|---|
| P1 | 08-14 | **Fifteen `pac solution import` attempts.** Six root causes: FieldSecurityProfile element shape, fabricated Role GUIDs, three successive wrong guesses at `AppModuleSiteMap.xml`, `AppModule.xml` almost entirely wrong, connection-reference type 10371 unrecognised as a RootComponent, environment-variable folder layout from an older `pac` version | Live import, iteratively |
| P2 | 08-14 | Three **designer-save** failures that imported cleanly and were queryable via the Web API: 62 description fields over the 256-char cap, a stray `staticResult` block, and a concurrency/`operationOptions` conflict | Reviewer, opening flows |
| P3 | 08-14 | After a "successful" import: no views, no forms on any table, and `rev_setting` had zero rows | Reviewer |
| P4 | 08-16 | A-001's **guessed** multi-select control classid was wrong — dropdown rendered with no options on three fields. The Unvalidated Assumptions Register had recorded it as OPEN/E2 "pending V4" **and it shipped anyway** | Reviewer's V4 check |
| P5 | 08-16 | 11 scored-answer fields carried generic labels ("Wellbeing Answer 1") instead of the real questions. Pre-existing. "*Never caught because no test asserts form label text*" | Reviewer |
| P6 | 08-16 | Dataverse rejects Picklist→Text/Boolean via solution import; the subsequent delete returned 400 because a **form dependency** blocked it. Required a transitional import to strip the controls, then delete, then recreate at the correct type | Live, iteratively |
| P7 | 08-16 | `rev_hearaboutus` / `rev_otherhearaboutus` were **silently not created** by a "successful" import — caught only because `ensure-schema.ps1` afterwards reported CREATED rather than EXISTS | Independent Web API query |
| P8 | 08-16 | Solution import **relabels** matching option values but does **not delete** values the new source omits. `rev_breaktype` retains 4 stale values, `rev_applicanttype` 1. **Still open** | Independent query |
| P9 | 08-16 | The `DeleteOptionValue` cleanup call was declined by the session's own safety classifier — needs reviewer action or explicit re-authorisation | Harness |
| P10 | 08-17 | The certificate-from-Mac-keychain procedure, worked out and used successfully on 08-16, had to be **re-taught by you** the next day: *"yesterday you moved and got the certificate from the mac keychain. Make it so that you can use that again."* | You |

### 1.3 Root-cause classes

| Class | Incidents | Count | Already addressed? |
|---|---|---|---|
| **A — Platform contract guessed, not ground-truthed** | B1, B7, B11, P1, P2, P4, P6, P8 | **8** | Yes — C-TECH-052, the verification skill. Working, but see §2.7 |
| **B — Gate defect: the check could not fail** | B2, B3, B5, B8 | **4** | **No. Nothing in the system tests the gates** |
| **C — Silent partial success (exit 0, component absent)** | B7, P3, P7 | 3 | Partly — C-TECH-053 (a)/(b)/(c) |
| **D — No assertion on rendered content** | P5, B6 | 2 | No |
| **E — Self-inflicted staleness** | B4, B6 | 2 | No |
| **F — Memory loss between runs/sessions** | B10, P10 | 2 | No |
| **G — Environment/harness friction** | B9, P9 | 2 | No |
| **H — Deferred step reported as success** | B2's enabler | 1 (systemic) | No |

Class A is the largest and is the one the system *has* learned from. **Class B is the dangerous one**:
a gate that cannot fail doesn't just miss its defect, it manufactures the confidence that stops anyone
looking. B5 and B8 both recorded PASS for HARD constraints while reading nothing.

---

## Part 2 — Why build-agent and pipeline-agent specifically

Your instinct is correct, and the reasons are structural rather than incidental.

### 2.1 The tier assignment is inverted

Both agents are tier `mechanical` (Haiku), with this rationale in `config/models.yml`:

> "The build-agent reads a YAML file and executes commands in sequence. It reports success or failure.
> **No reasoning required.**"

What these two agents actually did this week: decompiled a .NET assembly to recover an undocumented
packer contract (B1); worked out that `pac solution check` takes a packed zip and that the step order
was therefore wrong (B2); ruled out data, binding, security and XML-structure causes by live query
before concluding a control classid was wrong (P4); diagnosed a form-dependency delete block and
devised a transitional-import sequence to clear it (P6); and noticed that a *successful* import had
silently not created two columns (P7).

That is the hardest diagnostic reasoning in the entire system, assigned the cheapest model, under an
instruction that says no reasoning is required. The agent files reinforce it: *"Read
`config/<slug>-build.yml` — this is your complete instruction set."* An agent told its config is
complete and authoritative is precisely an agent that will not question whether `lint` should run
before `pack`.

### 2.2 They are the only agents with no memory input

| Agent | Loads prior experience? |
|---|---|
| plan-agent | 4 domain knowledge files + constraints |
| architect-agent | 7+ knowledge files, constraints, the approved SDD |
| development-agent | TAD, SDD, 5+ knowledge files, constraints, §10 register |
| test-agent | SDD, TAD, Dev Summary §9, knowledge, constraints |
| **build-agent** | **`build.yml` + `build-and-deploy.md`. Nothing else.** |
| **pipeline-agent** | **`pipeline.yml` + `build-and-deploy.md`. Nothing else.** |

Neither loads the deployment handover document — the 277-line record of the fifteen-attempt
investigation written specifically so it wouldn't happen again. Neither reads its own log, where the
previous run's confirmed root causes are written in full prose. **The agents that most need
institutional memory are the two that have none.**

### 2.3 The substrate that would carry that memory is being destroyed

`artifact_output: build/artifacts/revitalise-grant-automation-20260810-1/` — hardcoded, date-stamped
2026-08-10, still in use for build #6 on 08-17. WORKFLOW.md mandates `<slug>-<date>-<n>/`.

Consequence: one directory, six builds. Git preserves manifests for builds #4 and #5 only; #6
overwrote #5 on disk; #1–#3 never existed in any committed form. The manifests are the richest
structured failure data the system produces, and they are being overwritten by design.

### 2.4 They are the collision point, not the culprit

Everything upstream validates *documents and internal consistency*. build-agent is the first agent to
touch a real tool; pipeline-agent is the first to touch a real environment. Every accumulated
upstream guess surfaces in one of those two places. 640 Pester tests passed while fifteen imports
failed — not because the tests were bad, but because they asserted internal consistency, which was
never the failing property.

This reframes part of the fix: **some of the remedy belongs upstream**, not in these two agents.

### 2.5 The gates are unverified, hand-written code

`build.yml` now has 19 steps, of which ~11 are custom gates: 5 `verify-*.py` scripts and 3 inverted
`grep` gates plus assorted inline validation. `src/tests/` — 653 tests — contains **no test of any
gate's ability to fail**. There is no known-bad fixture anywhere.

Three of these gates were found broken *in production use*: B2 (wrong order, wrong input type), B5
(nonexistent path, inverted exit code → unconditional pass), B8 (wrong scan scope). The inverted-grep
pattern `! grep -rnE ... path && echo "gate passed"` is structurally dangerous: **every** failure mode
of `grep` other than "found a match" produces a pass.

### 2.6 "Deferred" is being reported as success

Builds #1–#4 all reported `SUCCESS`, each explicitly annotating `auth` + `lint` as deferred and "not a
defect". Defensible individually; collectively it hid B2 for four consecutive green builds. A deferred
step is an **unexecuted** step, and the manifest should carry it as a coverage gap that the next build
inherits — not a footnote that resets each time.

### 2.7 The learning altitude is too low

This is the subtlest cause and the most important for the design.

The 08-14 loop produced C-TECH-049: *"no flow `description` may exceed 256 characters."* That is an
**instance**. The class is *"platform field-length limits that the packer does not enforce."* Two days
later B11 hit the same class from a different direction — `rev_setting.rev_description` at 500 chars —
and needed its own separate gate. The repo now has `verify-workflow-description-length.py` **and**
`verify-setting-description-length.py`, two scripts for one class, and no gate for the third instance
when it arrives.

Same pattern in Class C: P3 (08-14, forms/views/settings missing after successful import) and P7
(08-16, columns silently not created) are the same class, discovered twice, two days apart.

**The manual loop patches instances. It never generalises to the class, so it is permanently one
incident behind.**

### 2.8 The assumption register predicts failures and doesn't stop them

A-001 was recorded correctly: multi-select classid, guessed, severity E2, OPEN, "pending V4". Then it
shipped, and you found it as a dropdown with no options. C-TECH-052 mandates *recording* a guess;
nothing mandates *closing* it before deploy. test-agent's fail conditions do cover it — an OPEN
assumption fails the run "if an environment exists in which it could be closed" — but the deploy went
ahead regardless.

The register is doing its job perfectly and is wired to nothing.

---

## Part 3 — Proof that the manual loop is insufficient

This matters because the obvious response to a bad week is "write a better handover document," and
that has already been tried, twice, by you, in explicit terms:

- **2026-08-14 18:56** — *"Make a handover document to update all the docs and scripts so the next
  time we don't run into so much problems deploying to development."*
- **2026-08-14 19:12** — *"Based on the created handover document ... Adjust the multi agent
  development system files so i don't run into these problems again."*

The loop ran and produced real work: C-TECH-049/050/051 (later 052–056),
`skills/how-to-verify-a-platform-contract.md`, three new verify scripts, and edits across all seven
agent files. Commit `ea66ddb`.

Then 08-16 and 08-17 produced P4, P5, P6, P7, P8, B4, B5, B6, B9 and P10 — new instances of classes A,
B, C, D, E and F. And P10 is the clean proof: a *working procedure*, established 08-16, gone by 08-17,
restored only because you remembered it.

The conclusion is not that the loop was done badly. It is that a loop which runs when a human
remembers to run it, learns at instance altitude, and writes only to files nobody reads back, cannot
converge.

---

## Part 4 — Design

Five components. The ordering matters: **the read path is worth more than the write path**, because
capture is already the system's strength.

### 4.1 `logs/improvement-log.jsonl` — append-only capture

JSONL so agents append without reading the file first (per CLAUDE.md's token rules), no merge
conflicts, machine-processable, greppable.

The schema is deliberately close to what build #6's manifest already emits:

```json
{"id":"IMP-0007","ts":"2026-08-17T16:10","agent":"build-agent","feature":"revitalise-form-field-corrections",
 "class":"gate-defect","severity":"blocker","cost":"unknown — undetected since authored",
 "what":"FR-016 gate target path missing .json; grep exit 2 inverted by ! to a pass",
 "expected":"gate greps the scoring flow for special-category column references",
 "root_cause":"inverted-exit-code gate pattern treats every grep failure mode as success",
 "detected_by":"agent-self",
 "why_it_was_never_caught":"no gate in this build verifies that a gate's own target path exists",
 "class_instance_of":"platform-limit-gate-cannot-fail",
 "proposed_change":{"type":"build-gate","target":"scripts/verify-build-config.py",
                    "summary":"preflight: assert every step's target paths exist and every gate can fail"},
 "status":"NEW"}
```

Three fields do the real work:

- **`why_it_was_never_caught`** — converts an anecdote into a specification for a gate. "Nothing"
  demands a new check; "the build gate, if it ran in the right order" demands a step-order fix.
- **`class_instance_of`** — the altitude field. This is what §2.7 was missing. Two entries sharing a
  class is the trigger to generalise instead of patching again.
- **`cost`** — lets the processor rank. Without it the log becomes an undifferentiated graveyard.

### 4.2 `logs/known-failure-modes.md` — the read path (highest-value single change)

A **generated**, capped digest — one page, ~40 lines, ordered by recurrence count. Not the raw log:
agents cannot afford to read a growing JSONL every run.

```markdown
# Known Failure Modes — generated 2026-08-17 from improvement-log.jsonl. Do not hand-edit.

## Before you execute any build config (4 recorded incidents)
- A gate's target path may not exist. `! grep` on a bad path exits 2 → inverted to PASS. [IMP-0007]
- A step may consume an artefact a later step produces. Check order before trusting it. [IMP-0004]
- `pac solution check` takes a packed .zip, never a source folder. [IMP-0004]
- `gitleaks detect` needs `--no-git`, or it scans history instead of the tree. [IMP-0002]

## Before you declare an import successful (3 recorded incidents)
- Exit 0 does not mean components were created. Query each by name. [IMP-0003, IMP-0009]
- Import relabels matching option values; it does NOT delete values the source omits. [IMP-0011]
- Picklist→String/Boolean is rejected; delete is blocked by form dependencies first. [IMP-0010]

## Capabilities established in earlier sessions (2 recorded)
- The provisioning cert lives in this Mac's CurrentUser/My keychain, thumbprint A6F94E…C7FE. [IMP-0012]
```

**Then add exactly one line to the activation sequence of build-agent and pipeline-agent:**

> `0. Read logs/known-failure-modes.md` — before reading your config, and treat it as a checklist
> against that config, not as background reading.

That single edit is the difference between an agent that re-enters the minefield and one that carries
the map. It also fixes P10 (capability amnesia) as a side effect.

### 4.3 `agents/improvement-agent.md` — the processor, tier `strategic`

The only place in the roster I would argue for Opus: it edits the rules governing every future
feature, and a wrong or over-broad constraint is sticky and expensive — exactly
`tiers.strategic.use_when`.

Sequence: read `NEW` entries → cluster by `class_instance_of` → apply the promotion ladder → propose a
diff behind `APPROVE IMPROVEMENTS` → on approval, apply, mark entries `APPLIED` with the change
reference, and **regenerate `known-failure-modes.md`** → write
`docs/improvements/<date>-improvement-review.md`.

**Promotion ladder** (`skills/how-to-promote-a-finding.md`):

| Evidence | Becomes |
|---|---|
| One instance, feature-specific | Stays a log note |
| One instance, blocker, cause is general | Line in the relevant knowledge file |
| A tool could catch it mechanically | **Script + build gate** — always preferred |
| **Second instance of the same `class_instance_of`** | **Generalise: one gate for the class, and retire the instance gates** |
| Platform law, or third instance | Constraint row (HARD/SOFT) |
| Agent had the information and still erred | Agent `.md` or skill edit |
| The order of steps was wrong | `WORKFLOW.md` / config step-order fix |
| A capability was established and lost | `known-failure-modes.md` capability section |

The rule that fixes §2.7: **on the second instance of a class, you may not add another instance gate.**
Applied to this week's data, that immediately collapses `verify-workflow-description-length.py` and
`verify-setting-description-length.py` into one field-length gate driven by the schema's own declared
MaxLength values — which would then also cover the third instance for free.

**Anti-bloat rules**, because the real risk of this whole idea is a system that strangles itself:

- Every new constraint cites the `IMP-` ids justifying it.
- More than 3 new constraints in one review → propose consolidation instead.
- Every review must consider **retirement**. `constraints/README.md`'s Retired table has zero rows
  after 56 constraints; that is a smell, not a clean record.
- A constraint whose `Verify By` is not mechanically executable is a comment, not a constraint.

### 4.4 `scripts/verify-build-config.py` — preflight, and the direct fix for your two examples

A gate over the gates. Run as step 1 of every build, before anything else:

1. Every step's input paths (`--path`, `--folder`, `--zipfile`, grep targets, script arguments) either
   **exist now** or are **declared outputs of an earlier step**. → catches **B2** (lint before pack)
   and **B5** (missing `.json`) mechanically, in one second, on day one.
2. No step consumes an artefact produced by a later step. → catches the ordering class generally,
   which is your *"order of packaging before build"* complaint.
3. Every gate has a **known-bad fixture** under `src/tests/fixtures/known-bad/` and is asserted to
   **exit non-zero** against it. → closes Class B. A gate that has never failed has never been tested.
4. No gate uses the bare `! grep … && echo` pattern without an explicit positive control.
5. Every `steps_not_applicable` / deferred step is emitted into the manifest as an inherited coverage
   gap. → closes §2.6.

Of everything in this document, item 3 is the highest-severity gap: **11 hand-written gates, 653
tests, zero tests that any gate can fail.**

### 4.5 Wiring the register to the gate

One-line change with outsized effect, closing §2.8: pipeline-agent's Stage 0.5 refuses to deploy while
any Dev Summary §10 assumption is `OPEN` **and** the target environment is one in which it could be
closed — unless the reviewer explicitly overrides with the assumption id named.

A-001 was recorded, correctly, as a guess about a control classid that only V4 could settle. Under
this rule it blocks at the gate with its own id, instead of arriving in the maker portal as a dropdown
with no options.

---

## Part 5 — File-by-file changes

**New (7):**

| Path | Purpose |
|---|---|
| `logs/improvement-log.jsonl` | Append-only capture |
| `logs/known-failure-modes.md` | Generated read-path digest — the memory |
| `agents/improvement-agent.md` | Processor, tier `strategic` |
| `skills/how-to-log-an-improvement.md` | Schema + 4 triggers + worked examples (~1 page, loaded inline) |
| `skills/how-to-promote-a-finding.md` | Promotion ladder, altitude rule, anti-bloat |
| `scripts/verify-build-config.py` | Preflight gate-over-the-gates |
| `templates/improvement-review-template.md` | Review output |
| `src/tests/fixtures/known-bad/` | One fixture per gate |

**Edited (~13):**

| Path | Change |
|---|---|
| **`agents/build-agent.md`** | Activation step 0: read `known-failure-modes.md`. New `## Improvement Capture`. Drop "this is your complete instruction set" — replace with "verify the config before trusting it". Preflight as step 1 |
| **`agents/pipeline-agent.md`** | Same step 0 + capture block. Stage 0.5 blocks on OPEN assumptions (§4.5) |
| `config/models.yml` | `improvement-agent: tier: strategic`. **Re-tier build/pipeline to `standard`** and rewrite the "no reasoning required" rationale — §2.1 |
| `config/<slug>-build.yml` | `artifact_output` → `<slug>-<date>-<n>/` per WORKFLOW.md — §2.3. Add preflight as step 1 |
| `agents/WORKFLOW.md` | Roster row; capture contract; processing triggers; `APPROVE IMPROVEMENTS` keyword |
| `CLAUDE.md` | "Learning Rules" block beside Token Rules; improvement-agent in the layout |
| Other 5 agent files | One `## Improvement Capture` block + one gate line each |
| `constraints/README.md` | New constraints must cite `IMP-` ids; retirement is mandatory at each review |
| 3 output templates | "Findings logged: IMP-nnnn, …" line |

**Capture triggers** — deliberately narrow, so the log doesn't fill with chatter:

1. Second attempt at the same operation with changed input.
2. Reality contradicted a document in this repo.
3. Any `BLOCKED` / `FAILED` status.
4. **Any human correction of agent output.** Currently the highest-value signal in the system and
   discarded entirely — 14 of the 21 incidents above were detected by you.

Plus a **human-initiated path**: *"log this: X"* to lead-agent. Both examples in your original request
were things *you* hit, not an agent, and you are the one running the deployments.

**Processing triggers:** feature/phase completion · on demand · ≥10 `NEW` entries · **any `blocker`
immediately** — you do not wait to learn from a fifteen-attempt failure.

---

## Part 6 — Seed data

Do not start this empty; capture is worthless without a corpus, and the corpus already exists in prose:

- **21 incidents** from Part 1 of this document, already classed and attributed.
- 9 tabulated root causes from handover §3.1/§3.2 — that table already has a "Prevented by" column,
  which is `proposed_change` under another name.
- 8 improvised `[FINDING]` entries currently sitting in `logs/routing.log`, where nothing can process
  them.
- `build.yml`'s inline comments — several hundred words of post-mortem per gate, including the full
  B5, B8 and B2 narratives.

That is enough to validate the schema against known data and to let the improvement-agent's very first
review produce the class-level generalisations of §4.3 rather than starting from one incident.

---

## Part 7 — Recommended order

| # | Change | Why first |
|---|---|---|
| 1 | Fix `artifact_output` to `<slug>-<date>-<n>/` | One line. Stops ongoing destruction of the best data the system produces |
| 2 | `scripts/verify-build-config.py` + known-bad fixtures | Closes Class B, the only class with nothing defending it. Directly fixes both examples you raised |
| 3 | Seed `improvement-log.jsonl` from Part 1 + handover + routing.log | Corpus before processor |
| 4 | Generate `known-failure-modes.md`; add the read line to build/pipeline activation | The read path. Highest leverage per line changed |
| 5 | Re-tier build/pipeline to `standard`; rewrite the rationale | Removes the instruction not to think |
| 6 | Wire the assumption register to the deploy gate | One rule, closes §2.8 |
| 7 | `improvement-agent.md` + the two skills + templates | Now there is something for it to process, and a ladder to process it with |

Steps 1–4 are roughly a session's work and address, between them, 11 of the 21 incidents. Step 7 is
what makes it self-sustaining, and it is deliberately last: an improvement-agent with no corpus and no
ladder would just be another thing to remember to run.
