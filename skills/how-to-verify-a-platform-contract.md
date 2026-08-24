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

An E2–E4 shape may still be the right thing to commit — sometimes no environment exists yet. It
must be committed **as a declared guess** (§4), never as a settled fact.

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
