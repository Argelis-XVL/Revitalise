# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (26 entries, 26 distinct lessons)
Generated: 2026-08-17

## How to use this file

Read it **before** your own config or instruction set, and treat it as a checklist against
that config — not as background reading. Every line below is a defect that actually happened
on this project, with the finding ids that recorded it. A `x{n}` marker means that class has
now recurred {n} times, which is the system telling you a general gate is missing where an
instance patch was applied.

`build-agent` and `pipeline-agent` load this file on activation
(`agents/build-agent.md` step 0, `agents/pipeline-agent.md` step 0). Other agents load it
when their work touches a listed area.


## Recurring classes — where a general gate is missing

Each of these has happened more than once. Per `skills/how-to-promote-a-finding.md`, the second instance of a class may **not** get another instance-level patch: it must be generalised, and the instance gates retired.

| Count | Class | Findings |
|---|---|---|
| **x6** | `gate-cannot-fail` | IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025 |
| **x4** | `platform-contract-guessed-not-groundtruthed` | IMP-0001, IMP-0006, IMP-0011, IMP-0017 |
| **x3** | `exit-zero-does-not-mean-created` | IMP-0013, IMP-0018, IMP-0019 |
| **x3** | `learning-substrate-destroyed` | IMP-0016, IMP-0022, IMP-0023 |
| **x2** | `no-assertion-on-shipped-content` | IMP-0008, IMP-0015 |


## Before you execute a build config

*10 lessons from 10 findings.*

- `gitleaks detect` scans commit HISTORY by default. Without --no-git it can report PASS over none of the files the build actually packages.  
  <sub>IMP-0002</sub>
- `pac solution check --path` takes a PACKED .zip, never a source folder — and it must run AFTER the pack step that produces it.  
  <sub>IMP-0004</sub>
- The `! grep ... && echo` gate pattern turns EVERY grep failure — including 'target does not exist' (exit 2) — into a PASS. Verify the target path exists before trusting any such gate.  
  <sub>IMP-0007</sub>
- In a YAML `>` folded scalar, keep every line at the SAME indentation and put `&&`/`||` at line END — a more-indented line keeps its newline and yields a shell syntax error. Preflight now runs `bash -n` on every step command.  
  <sub>IMP-0025</sub>
- Credential material (.pfx/.cer/.pem) must live OUTSIDE the repo, not merely gitignored — secret-scan reads the working tree, correctly, and will block the build.  
  <sub>IMP-0003</sub>
- A test asserting an absolute schema count breaks on every legitimate schema addition. Expect to fix counts when you add columns; do not assume the test found a defect.  
  <sub>IMP-0005</sub>
- This repo's path contains spaces. `pac solution check --outputDirectory` silently writes nothing; read the result from stdout instead.  
  <sub>IMP-0010</sub>
- A structural check that regexes raw XML text can be satisfied by a marker inside a COMMENT. Strip comments before asserting on element presence.  
  <sub>IMP-0020</sub>

> **2 further lesson(s) in this section are not shown** (cap: 8). Findings: IMP-0024, IMP-0026. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you hand-author a platform artefact

*5 lessons from 5 findings.*

- Never infer a SolutionPackager file shape from documentation. Create the smallest real instance, export + unpack it, and copy the shape exactly.  
  <sub>IMP-0001</sub>
- An entity's FormXml/ and SavedQueries/ folders are dropped SILENTLY at pack time unless Entity.xml declares the empty <FormXml /> / <SavedQueries /> markers. 0 warnings, 0 errors, 0 components created.  
  <sub>IMP-0006</sub>
- rev_setting.rev_description is MaxLength=500. This project's verbose documentation style exceeds it. Same class as the flow 256-char cap.  
  <sub>IMP-0009</sub>
- Every one of fifteen import failures was a plausible guess about a platform contract, committed to source, validated only by gates that could not detect it being wrong. Two failed guesses is the signal to stop guessing and go get ground truth.  
  <sub>IMP-0011</sub>
- Dataverse rejects a Picklist->String/Boolean change via solution import, and the follow-up delete is blocked by any form that references the column. Procedure: strip the control from the form in a transitional import, delete, then recreate at the correct type via the Web API.  
  <sub>IMP-0017</sub>


## Before you declare a deploy or an import successful

*5 lessons from 5 findings.*

- A successful import proves the component was ACCEPTED, not that it works. Three components imported cleanly, were queryable, and still could not be opened or saved by a maker.  
  <sub>IMP-0012</sub>
- After an import, query EVERY declared component type by name. A hand-written subset of types to check will omit the one that failed — savedquery and systemform were both absent from the list that 'verified' the first DEV deploy.  
  <sub>IMP-0013</sub>
- An Unvalidated Assumptions Register row that is still OPEN is a prediction of a live defect, not paperwork. Close it before deploying, or expect the reviewer to find it.  
  <sub>IMP-0014</sub>
- Solution import can report SUCCESS having silently skipped components. This is the second recorded instance; treat 'import succeeded' as a claim to verify, never a result.  
  <sub>IMP-0018</sub>
- Solution import RELABELS matching option values but does NOT delete values the new source omits. Orphaned values survive every subsequent import. Compare live option-set members against source.  
  <sub>IMP-0019</sub>


## Before you report SUCCESS at all

*4 lessons from 4 findings.*

- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- Prose inside shipped metadata (a <Description>) can name a column you removed. Unpack the packed zip and grep for removed names before declaring the build clean.  
  <sub>IMP-0008</sub>
- No test asserts form label TEXT. Labels can be structurally perfect and semantically wrong; check them against the attribute's own authored wording.  
  <sub>IMP-0015</sub>
- Findings belong in logs/improvement-log.jsonl. logs/routing.log is one routing decision per line and is read by nothing.  
  <sub>IMP-0023</sub>


## Operating constraints of this environment

*1 lesson from 1 finding.*

- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*1 lesson from 1 finding.*

- The provisioning certificate is in this Mac's CurrentUser/My keychain (thumbprint A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE, app id 077f1f90-3218-4a06-bc90-887464353aa7). Cert-based app-only auth to DEV works from there — do not ask the reviewer to re-supply it.  
  <sub>IMP-0022</sub>


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
