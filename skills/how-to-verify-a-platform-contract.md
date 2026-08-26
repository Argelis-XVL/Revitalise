# Skill: How to Verify a Platform Contract

Used by: `architect-agent`, `development-agent` (and every sub-agent it spawns),
`build-agent`, `test-agent`, `pipeline-agent`

Load this skill at two moments:

1. **Before hand-authoring any artefact whose shape, limits, or behaviour the platform owns** —
   solution XML, flow JSON, manifest and settings files, provisioning API payloads, folder layouts.
2. **The moment a real environment first becomes available** — that is the trigger for the sweep
   in §6, not a later convenience.

---

## Why this skill exists

Getting one hand-authored solution into its first environment cost **fifteen import attempts**
(`docs/development/revitalise-grant-automation-dev-deployment-handover.md`). Every failure was a
real defect. Every defect had the same origin:

> **A plausible guess about a platform contract, committed to source, and validated only by
> something that could not detect it being wrong.**

`pac solution pack` validated layout and passed. A 640-test suite validated internal consistency
and passed. XML/JSON well-formedness gates passed. All three were working correctly; none of them
could see the defect. Three of the fifteen failures survived a *successful import* and were only
visible when a human opened the flow.

The pattern that broke the cycle every time: **stop guessing, create the thing for real, and look
at how the platform represents it.** It cost minutes and settled questions that repeated
import-error iteration and documentation research had not.

---

## 1. What counts as a platform contract

Anything the platform — not this project — decides. If getting it wrong produces an error from the
platform rather than from our own code, it is a platform contract:

| Category | Examples |
|---|---|
| **Serialisation shape** | Element vs attribute; PascalCase vs lowercase; wrapper elements; CDATA; which child elements are mandatory |
| **File and folder layout** | Where a component's file lives, what it is called — and whether that changed between tool versions |
| **Field limits** | Max lengths, allowed characters, required-when-present rules |
| **Identity** | Which ids the platform assigns vs accepts; whether a component matches by id, name, or schema name |
| **Capability** | What an import/deploy can *create* vs only *update*; which component types may be declared where |
| **Runtime coupling** | Configuration on one element that silently makes another element invalid |
| **Host environment** | Which APIs, drives, and paths exist on the OS the script will actually run on |

Every one of these categories produced at least one of the fifteen failures.

---

## 2. Evidence levels — only one of them is verification

Before writing the artefact, name the evidence you have:

| Level | Evidence | Status |
|---|---|---|
| **E1** | An artefact **the platform itself produced**: an export + unpack of a working instance, a `GET` of a live record, a metadata response | **VERIFIED** |
| **E2** | First-party documentation **for the exact platform and tool version in use** | ASSUMED |
| **E3** | Documentation for a different version, decompiled source, a blog, a similar component elsewhere in the solution | GUESS |
| **E4** | It looked obvious / it was symmetrical with something nearby | GUESS |

**Only E1 is verification.** E2 is where the environment-variable folder-layout failure came from —
the source was accurate, for an older `pac`. E4 is where most of the XML shape failures came from.

### Evidence must come from the artefact that GOVERNS the claim

A level is not the only thing that can be wrong with a citation. **Evidence can be E1 — produced by
the platform, read off disk — and still be evidence about a different question than the one being
answered.** That is not a lower level; it is the wrong artefact, and it produces confidently wrong
premises that no gate reads.

| A claim about… | Cites | Never |
|---|---|---|
| What a persona is **permitted** to read | `Roles/<Role>/<Role>.xml` — the privilege and its level | An application-code filter |
| Whether a **column** is confidential | `Entities/*/Entity.xml` (`IsSecured`) **plus** `Other/FieldSecurityProfiles.xml` (which profile releases it, and to which teams) | The absence of the column from a form or a generated model |
| What the **app does** | The application code | A role definition |
| What an **import** can create vs only update | An export of a working instance | Symmetry with a nearby component type |

`IMP-0305` is the worked example. A TAD argued that a trustee "cannot count rows they are correctly
prevented from seeing" and cited the app's own `ELIGIBLE_FILTER` as proof. The role definition says
otherwise: **REV Trustee holds `prvReadrev_application` at Global.** The platform permits the wider
read; the app declines to make it. The limit is a requirement plus an application-code filter, not a
privilege.

Two things about how that error survived, both worth internalising:

1. **The conclusion was right on other grounds,** so nothing prompted a re-check. A correct
   decision is not evidence that its stated reason is correct.
2. **The corrected framing was strictly stronger** — the wider read being technically available is
   precisely *why* it must never reach a browser. The weaker argument still supported the decision,
   which is exactly what let it stand.

#### The same rule has a LIVENESS half: a proposed schema is not evidence about a live artefact

The table above is about citing the wrong *kind* of artefact. There is a second way to cite the
wrong artefact while quoting it perfectly: **citing a design document's proposed schema as though
it were the live file.** A `grep` hit inside `docs/improvements/` is a hit on somebody's proposal.

| A claim about… | Cites | Never |
|---|---|---|
| A field in `contract/*.json` | that file's own keys — `python3 -c "import json;print(json.load(open('contract/wbs.json')).keys())"` | a matching string inside a design document under `docs/improvements/` |
| What a ledger records | the ledger | the design that proposed the ledger |

`IMP-0341` is the worked example. A dispatch brief stated that `contract/wbs.json`'s
`deliverable_map` carried a note against a feature slug — `wbs: [], note: "corrections after V4
review — may be unquoted"`. **`contract/wbs.json` has no `deliverable_map` key and no occurrence of
the slug**; its top-level keys are `_generated_by`, `_units`, `source`, `totals`, `per_phase`,
`per_automation`, `known_gap`, `corrected_totals_with_known_gap`, `tasks`. The quoted note lives
inside a *proposed* YAML schema in `docs/improvements/2026-08-17-project-management-agent-design.md`.

The consequence was not cosmetic and it inverted the answer: feature-slug-to-WBS mapping is
recorded **nowhere** in `contract/` today, so that work is *genuinely unrecorded* commercially
rather than *recorded-as-unquoted*. One is a `C-COM-002` question for `commercial-agent`; the other
is a footnote. **Before citing a field in `contract/`, confirm the field exists in that file** —
open it, do not trust a grep across the repository.

So before writing that a persona *cannot* read something, open the role file and read the privilege
and its level. `C-TECH-066`'s access half compares TAD-declared visibility against `prvRead`
privileges in one direction only — it catches a TAD claiming a persona *can* read a table its role
has no privilege on. **The opposite direction, a TAD claiming a persona cannot read something its
role in fact permits, is unchecked, and it is the direction that quietly justifies architecture.**

An E2–E4 shape may still be the right thing to commit — sometimes no environment exists yet. It
must be committed **as a declared guess** (§4), never as a settled fact.

### A NEGATIVE claim needs the whole set. Enumerate it — one command

**"No column supplies X", "no such column exists anywhere in the solution", "this data cannot be
sourced" — these are the only claims a partial scan cannot support**, because the evidence for them
is the entire attribute set and nothing less. A positive claim needs one grep hit; a negative claim
needs all of them.

```bash
python3 scripts/dump-entity-attributes.py rev_application          # the whole set, one table
python3 scripts/dump-entity-attributes.py --all --grep prefer      # name AND description
```

Run it before you write the claim, and **`--grep` the description, not only the name** — the column
you are looking for is usually named nothing like the requirement's words.

This project wrote that claim wrongly three times about **one TAD sentence**, and the third time it
cost a mechanical coverage gate and a priced change-order candidate:

| Finding | The claim | The reality |
|---|---|---|
| `IMP-0326` | "no preferred, holiday or travel date column exists anywhere in the solution" | drove improvement review 29's largest escalation |
| `IMP-0337` | "break location is unresolvable, no backing column" | `rev_breaklocation`, `nvarchar(250)`, unsecured, its own `<Description>` reading **"TRUSTEE-VISIBLE ON PURPOSE"** for exactly that data |
| `IMP-0338` | same sentence, dates half | `rev_breakstart` / `rev_breakend`, committed **eleven days before** the finding that said they did not exist. It carries `corrects` against `IMP-0326` |

The coverage gate is green today with **no schema change and no change order**. The class was never
about data the solution could not supply; it was about nobody enumerating the columns — and a
category list, remembered or written, is what an enumeration is not. `IMP-0337`'s own lesson is
blunter: do not accept a briefing that groups several items together as equally unresolvable, even
when a prior finding's summary line says so. Grep each one yourself.

**There is deliberately no gate over this.** A gate would have to read a negative claim out of
prose and refute it against schema, which is the design improvement review 29 measured at **48%
false positives** before rejecting it. The mechanical half here is a tool that makes the correct
method one command; the rule still depends on you running it.

### Documentation is E2. It has no V-level, and the two scales must not be mixed

The **E** scale grades *what your evidence is*. The **V** scale (§5) grades *what you executed*.
They are different questions and neither substitutes for the other.

So there is no such thing as *"verification level: documentation only (V2)"* — a phrase that
reached an applied knowledge file on 2026-08-22 (`IMP-0207`). `V2` means **"does it package"**,
which is not a statement anyone can make about a CLI reference page. Documentation-sourced is
**E2, status ASSUMED**, and that is all.

Say it the way the evidence actually divides, per section of the document if they differ:

> The command surface is **executed** ground truth (`pa <group> --help`, this machine,
> 2026-08-22). Runtime behaviour is **E2** — no command has been run against a live environment.

### For an npm-distributed CLI or SDK, E2 is never where you stop

**An installed package carries its own ground truth, offline, in two places nobody thinks to
open.** Both outrank the documentation, and both are E1:

| What you want to know | Read this, not the docs |
|---|---|
| What commands and flags exist | `<cli> --help`, then `<cli> <group> --help` |
| What a module actually exports | the installed `.d.ts` under `node_modules/<pkg>/dist/` |
| What version is really in use | the installed `node_modules/<pkg>/package.json` |
| Whether the tool is even here | `npm ls -g --depth=0` **and** `npm config get prefix` — not `which` |

The last row is its own trap (`IMP-0200`): a global npm install can put a binary in a directory
that is not on `PATH`, so `which <tool>` reports nothing and **a PATH gap is indistinguishable
from a missing install**. A knowledge file once said *"`pa` is not installed on this machine"*
while the CLI sat one unexported directory away, installed 34 minutes earlier.

**The rule: if the tool installs in one command, E2 is not an acceptable resting place for a
claim about it.** Install it and read its help. Fifteen minutes of `--help` calls corrected five
claims in one file and closed an assumption (`A-TR-12`) that had been open since the code was
written. `scripts/verify-toolchain-claims.py` now enforces the mechanical half of this —
install, version and command-name claims in `knowledge/technology/*.md` are checked against the
machine on every build.

---

## 3. The ground-truth procedure

When any environment of the target platform exists, this takes minutes and ends the argument:

1. **Create the smallest real instance** of the component — via the platform API, or by hand in the
   maker/admin UI for things that are awkward to build programmatically.
2. **Ask the platform to give it back**: export + unpack it, or `GET` the record and read the
   response.
3. **Copy the shape exactly** — element names, casing, attribute-vs-child, ordering, folder path.
   Do not "improve" it, do not normalise it to match neighbouring files, do not drop elements that
   look redundant.
4. **Record the evidence** in the register (§4) or the Dev Summary: the command run, the date, and
   the platform/tool version. A contract verified against tool version X is not verified for
   version Y.

Prefer this over a second round of error-message iteration. **Two failed guesses is the signal to
stop guessing** — at that point the ground-truth route is already cheaper than continuing.

### Before step 1: state your harness mode, because under Auto Mode there is no live route

**The cert-based Dataverse read established by `IMP-0083` is not an always-available fallback.**
Under Auto Mode the classifier auto-denies a cert/keychain-touching `pwsh` command with no
permission prompt, **reads included** — zero writes in the script changes nothing about the
outcome (`IMP-0287`). `IMP-0084`'s "read-only queries ran freely" holds only for a non-Auto-Mode
session, which is why this looked like a reliable route for three test-report revisions in a row:
none of them recorded the mode they ran in.

So, in order:

1. **Say which mode you are in, and treat `unknown` as unavailable.** "Unknown" is the honest
   answer when you cannot determine it, and it resolves to *no live route*, not to *try it and
   see*.
2. **Where there is no live route, do not record E2 as though the live route had been tried and
   failed.** It was never reached. The register row stays `OPEN` with *"no live route in this
   session"* as the blocker, which is a different fact from *"the platform disagreed"*.
3. **Emit a `REVIEWER ACTION REQUIRED` block** carrying the exact command and the query that
   proves the outcome, and name who can run it.

A refusal here is a control, not an obstacle (`agents/pipeline-agent.md` → *A refusal is a
control, not an obstacle*): every legitimate response adds something, and none of them relocates
the call to get a different answer.

---

## 4. The Unvalidated Assumptions Register

Every E2/E3/E4 contract gets a row in **Dev Summary §10** (`templates/dev-summary-template.md`) —
this is `C-TECH-052`, HARD:

| Col | Meaning |
|---|---|
| ID | `A-001`, `A-002` … stable within the feature |
| Claim | The specific thing assumed, in one sentence — *"`description` is a child element"*, not *"field security profile XML"* |
| Where | File and element/path in source |
| Evidence | E2 / E3 / E4 + the source of it |
| Why not verified | The blocker — usually "no environment exists yet" |
| Cheapest verification | The exact command or UI step that would settle it |
| Status | `OPEN` / `VERIFIED <date>` / `CORRECTED <ref>` |

Four rules:

- **Mark the guess where it lives, too.** A comment carrying the `A-nnn` id at the point in source
  where the guess was made — so the next person editing that file sees it without reading a document.
- **The register is a work list, not a disclaimer.** Writing a row down does not discharge it.
- **Precision matters.** On the feature that produced this skill, *every item its register flagged
  as unvalidated turned out to be wrong.* A register of vague rows would have caught none of them.
- **Every row is closed by execution, not by re-reading documentation.**

---

## 5. Verification is by execution, and it has levels

The single most expensive mistake available here is treating a green step as proof of the next
step. State the level actually reached; never report a higher one.

| Level | Question | Proven by | Proves **nothing** about |
|---|---|---|---|
| **V1** | Is it well-formed? | XML/JSON parse, schema validation | Whether any name in it is real |
| **V2** | Does it package? | `pac solution pack`, compile, bundle | **Layout only, not content** |
| **V3** | Was it accepted? | Import/deploy succeeded; the component is queryable in the target | Whether a human can use it |
| **V4** | Is it usable? | **A human opens it in the designer/editor and saves it** | Whether it does the right thing |
| **V5** | Does it run? | An end-to-end execution with real inputs and observed outputs | Any other environment |
| **V6** | Does it run *there*? | The same execution in the next environment / on the CI runner's OS | — |

These levels describe an artefact **executed against the platform**. They do not grade a
document, a CLI reference page or a claim read out of Microsoft Learn — that is the E scale in
§2, and mixing the two produces sentences like *"documentation only (V2)"* that read as far
stronger evidence than they are.

V1–V3 are automatable and belong in `build.yml` and `smoke_tests`. **V4 cannot be automated away**
and must be a named, owned step in the pipeline — three of the fifteen failures passed V3 cleanly
and failed V4. V6 is not pedantry: a provisioning helper that had only ever run on Windows used a
Windows-only API and would have failed every CI run on the Linux runner (`C-TECH-054`).

Idempotency belongs at V3: **re-run the deploy immediately.** A deploy that only succeeds against a
clean target is not a deploy that works.

---

## 6. The first-real-environment sweep

When the first real environment appears, **stop feature work and close the whole register at once.**

Verifying assumptions one at a time, as each import failure surfaces them, is what turns a
one-hour job into fifteen attempts: each attempt costs a full import cycle and reveals exactly one
defect, because the platform stops at the first thing it dislikes.

The sweep:

1. Create one real instance of **every** component type in the register (§3).
2. Export + unpack them **together**, and diff every guessed shape against ground truth in one pass.
3. Correct source, mark rows `VERIFIED` or `CORRECTED`, and record what changed.
4. Only then run the first import.

Re-run the sweep's environment-specific parts for **each new environment**: anything the platform
assigns per environment (ids, endpoints) and anything that must exist before a first deploy is
per-environment state, not per-feature state (`C-TECH-050`, `C-TECH-051`).

---

## 7. Warnings are findings

A warning from a platform tool is the platform telling you it did not do what you asked. Triage
every one: **resolve it, or record it with an explicit rationale** (`C-TECH-055`).

On this project a pack warning that root components were "not defined in customizations" was
present and ignored from the first build. It was a correct, specific report of the defect that
later caused failure #5 — carried through every green build for weeks.

---

## 8. A one-line error is not a diagnosis

Deploy tooling reports the *outcome*; the platform records the *reason* somewhere else. Before
forming any theory about a failure, go and get the detailed record — the import-job row, the async
operation, the server-side log, the stack trace. Platform-specific commands for this stack are in
`knowledge/technology/build-and-deploy.md` → **Diagnosing a Failed Import**.

Two useful signals when the message itself says nothing:

- **How long it took.** A failure much faster than a normal run failed at a structural stage,
  before it ever reached your content.
- **The handler name in the stack trace.** It names the component type, even when the message is a
  generic null-reference error.

---

## 9. One instance proves one instance

Proven in DEV is not proven in TST/PRD. Proven unmanaged is not proven managed. Proven on macOS is
not proven on the Linux CI runner. Proven on tool version 2.4.1 is not proven on 2.5.

When claiming something works, say **where** it was proven and at **which level** (§5). Anything
that has only ever executed in one place is unproven everywhere else, and belongs in the register
or in Dev Summary §7 (Known Limitations) — not in a completion claim.

### One live run does not close two defects

**When a handoff cites a prior live re-run as evidence that several defects are fixed, re-query
each defect's own `revisit_when` condition separately.** A confirmed fix is evidence for itself
and for nothing beside it, even when both fixes shipped in the same source revision and the same
run.

`IMP-0270` is why. A test cycle opened with the plain claim that the reviewer had run
`ensure-schema.ps1 -Env dev` once successfully after two fixes landed. One of them was live and
correct. The other had not taken effect at all: five Tier 4 lookup columns still reported
`IsSecured=False` and the finance profile held 11 of its intended 16 permissions. Two defects,
one run, one sentence covering both — and the only reason it was caught is that somebody ran the
queries instead of reading the sentence.

The cost of getting this wrong is asymmetric. Believing the claim signs off a privacy control
that is not there; re-querying costs one API call per defect.

---

## 10. Checklist

Before committing a hand-authored platform artefact:

- [ ] Every contract in it is named, with its evidence level (§2)
- [ ] Where an environment existed, ground truth was used instead of a guess (§3)
- [ ] Every E2/E3/E4 contract has a register row **and** an `A-nnn` comment in source (§4)
- [ ] Any platform limit that the packer/compiler does not enforce has a build gate (`build.yml`)
- [ ] Scripts run on the OS the pipeline will actually run them on (`C-TECH-054`)

Before reporting a component as done:

- [ ] The verification level reached is stated explicitly (§5)
- [ ] V3 was re-run to prove idempotency
- [ ] V4 was performed by a human, with the result recorded
- [ ] Every tool warning is resolved or recorded with a rationale (§7)
- [ ] Any diagnostic or temporary component created during investigation has been removed
      (`C-TECH-056`)
- [ ] **A removal recorded by someone else was re-queried by id, not believed.** `C-TECH-056`
      requires the removal to be *recorded*; nothing requires the record to be *true*. A dev
      summary stated that an investigation's test row and its control's upserted row "were both
      deleted afterward" and both were still live in DEV the next day (`IMP-0218`). A stated
      cleanup is a claim, exactly as a `Status` column is (`C-COM-005`) — and it is one live
      query to settle: ask for the specific ids and expect nothing back.

## 11. The absence of rows is not evidence of the absence of events

`flowrun` in the DEV environment was readable and held **zero rows for the whole environment**.
The conclusion drawn — that no cloud flow there had ever executed — was wrong, and eleven flow
runs proved it wrong: eleven `rev_errorlog` rows written by the scoring flow, each the record of
a run that the `flowrun` table did not contain (`IMP-0110`, `IMP-0107`).

A queryable table returning nothing tells you one of three things, and it does not tell you
which:

- the events did not happen;
- the events happened and this table is not where they are recorded;
- the events happened, are recorded here, and your identity cannot see the rows.

So an empty result is never a negative finding on its own. Pair it with a **positive** signal
before concluding anything: a row the process itself writes, a counter that moved, an artefact
that exists. Eleven error-log rows were sitting in the same environment the whole time.

This is the mirror image of §9, *one instance proves one instance*. Zero instances prove nothing
at all — and a confident negative is more expensive than an admitted unknown, because it closes
the investigation.
