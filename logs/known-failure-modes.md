# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (47 entries, 47 distinct lessons)
Generated: 2026-08-19

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
| **x12** | `gate-cannot-fail` | IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025, IMP-0035, IMP-0036, IMP-0041, IMP-0042, IMP-0043, IMP-0046 |
| **x7** | `platform-contract-guessed-not-groundtruthed` | IMP-0001, IMP-0006, IMP-0011, IMP-0017, IMP-0037, IMP-0044, IMP-0045 |
| **x5** | `learning-substrate-destroyed` | IMP-0016, IMP-0022, IMP-0023, IMP-0033, IMP-0038 |
| **x4** | `exit-zero-does-not-mean-created` | IMP-0013, IMP-0018, IMP-0019, IMP-0030 |
| **x3** | `no-assertion-on-shipped-content` | IMP-0008, IMP-0015, IMP-0047 |
| **x2** | `harness-blocks-destructive-call` | IMP-0021, IMP-0040 |
| **x2** | `test-coupled-to-absolute-counts` | IMP-0005, IMP-0039 |


## Before you execute a build config

*17 lessons from 17 findings.*

- `gitleaks detect` scans commit HISTORY by default. Without --no-git it can report PASS over none of the files the build actually packages.  
  <sub>IMP-0002</sub>
- `pac solution check --path` takes a PACKED .zip, never a source folder — and it must run AFTER the pack step that produces it.  
  <sub>IMP-0004</sub>
- The `! grep ... && echo` gate pattern turns EVERY grep failure — including 'target does not exist' (exit 2) — into a PASS. Verify the target path exists before trusting any such gate.  
  <sub>IMP-0007</sub>
- In a YAML `>` folded scalar, keep every line at the SAME indentation and put `&&`/`||` at line END — a more-indented line keeps its newline and yields a shell syntax error. Preflight now runs `bash -n` on every step command.  
  <sub>IMP-0025</sub>
- A HARD constraint whose rule text is still a placeholder always PASSES and is therefore a gate that cannot fail. C-DOM-030 and C-DOM-031 are placeholders; report them as UNEVALUABLE rather than PASS, and note that skills/how-to-apply-constraints.md has no status for that outcome.  
  <sub>IMP-0035</sub>
- There is no preflight for pipeline.yml. A pipeline step can name a script that does not exist, a parameter that does not exist, or a path that does not exist, and nothing will say so until the stage runs against a live environment. Verify every script path and parameter against the script's own param block before executing a stage - and note that alternate keys are declared in Entity.xml <EntityKeys>, not created by a script switch.  
  <sub>IMP-0042</sub>
- In ensure-schema.ps1, RELATIONSHIPS must run before ALTERNATE KEYS: a key on a lookup column cannot be created before the relationship that creates that column (Dataverse 0x80040203). Sections reordered 2026-08-18. Mocked API tests cannot catch step-order defects - a mocked POST succeeds regardless of what exists.  
  <sub>IMP-0043</sub>
- Credential material (.pfx/.cer/.pem) must live OUTSIDE the repo, not merely gitignored — secret-scan reads the working tree, correctly, and will block the build.  
  <sub>IMP-0003</sub>

> **9 further lesson(s) in this section are not shown** (cap: 8). Findings: IMP-0005, IMP-0010, IMP-0020, IMP-0024, IMP-0026, IMP-0036, IMP-0039, IMP-0041, IMP-0046. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you hand-author a platform artefact

*7 lessons from 7 findings.*

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
- An environmentvariabledefinition.xml must contain ONLY its root element - no XML declaration, no comment. A comment makes solution import fail with 0x80040216 at ImportXml.GetComponentsList, naming nothing, while the file remains valid XML and pac solution pack exits 0. The rule is in src/solutions/RevitaliseGrantAutomation/environmentvariabledefinitions/README.md. BEFORE authoring a new file beside existing ones, diff your element set against a sibling and read any README in that folder.  
  <sub>IMP-0045</sub>
- Read the WHOLE artefact when copying a shape - `head -12` of an option set hides the optionset-level <Descriptions> and <displaynames> that sit after </options>, and `pac solution pack` accepts their absence with exit 0. A truncated read of a source of truth is not ground truth.  
  <sub>IMP-0037</sub>


## Before you declare a deploy or an import successful

*6 lessons from 6 findings.*

- A successful import proves the component was ACCEPTED, not that it works. Three components imported cleanly, were queryable, and still could not be opened or saved by a maker.  
  <sub>IMP-0012</sub>
- After an import, query EVERY declared component type by name. A hand-written subset of types to check will omit the one that failed — savedquery and systemform were both absent from the list that 'verified' the first DEV deploy.  
  <sub>IMP-0013</sub>
- An Unvalidated Assumptions Register row that is still OPEN is a prediction of a live defect, not paperwork. Close it before deploying, or expect the reviewer to find it.  
  <sub>IMP-0014</sub>
- Solution import can report SUCCESS having silently skipped components. This is the second recorded instance; treat 'import succeeded' as a claim to verify, never a result.  
  <sub>IMP-0018</sub>
- A Status column is a claim, not a result - the same class as a successful import that created nothing. Derive task state from repository and environment evidence, keep the hand-typed value as claimed_status, and report every disagreement: WBS 0.4 was marked Done with five of the eight tables it names absent.  
  <sub>IMP-0030</sub>
- Solution import RELABELS matching option values but does NOT delete values the new source omits. Orphaned values survive every subsequent import. Compare live option-set members against source.  
  <sub>IMP-0019</sub>


## Before you report SUCCESS at all

*7 lessons from 7 findings.*

- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- ensure-schema.ps1 derives nothing from disk: Get-RevEntityLogicalNames is a hand-kept list and the relationship detail path was hardcoded to one file. An entity absent from that list is an entity C-TECH-050's prerequisite step will NOT create, silently - so adding a table means editing that list, and a gate should compare it against Entities/ on disk.  
  <sub>IMP-0038</sub>
- Prose inside shipped metadata (a <Description>) can name a column you removed. Unpack the packed zip and grep for removed names before declaring the build clean.  
  <sub>IMP-0008</sub>
- No test asserts form label TEXT. Labels can be structurally perfect and semantically wrong; check them against the attribute's own authored wording.  
  <sub>IMP-0015</sub>
- Findings belong in logs/improvement-log.jsonl. logs/routing.log is one routing decision per line and is read by nothing.  
  <sub>IMP-0023</sub>
- An unreconciled finding log cannot tell 'nothing was learned' from 'nobody did the bookkeeping'. Reconcile every entry against the artefact its proposed_change names - four one-line knowledge proposals sat unapplied for four days because 23 already-fixed entries were still marked NEW alongside them.  
  <sub>IMP-0033</sub>
- A Money column is TWO columns: <name> and an automatic <name>_base. The _base twin CANNOT be secured (CanBeSecuredForRead=False), so column security on a Money field does not protect its value from anyone with table Read. For an amount that must be restricted, use Decimal instead - single-currency orgs gain nothing from Money and lose the ability to secure the value. Verified live on rev_grant.rev_amountawarded 2026-08-19.  
  <sub>IMP-0047</sub>


## Operating constraints of this environment

*1 lesson from 1 finding.*

- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>


## Before you bill an hour, accept a phase, or report status

*3 lessons from 3 findings.*

- Never restate contracted hours, fees, phase membership or dates in a repo document - cite the generated baseline. SDD section 10 said 106-160h over 7 automations against a signed 292h over 9, and every downstream document inherited it.  
  <sub>IMP-0029</sub>
- Resolve every incoming request to WBS task ids before routing, and take the next unit of work from the ready set over the WBS dependency graph, phase-ordered against contractual dates. Asking 'what next' in conversation built Phase 2 in August while Phase 1, due three weeks earlier, sat untouched.  
  <sub>IMP-0031</sub>
- Propose actual hours at the moment the evidence exists - on each DEV deploy and in each dev summary - not at month end. The WBS shipped with Actual Hours and Delta columns and all 61 rows were still empty six weeks into a T&M engagement.  
  <sub>IMP-0032</sub>


## Before you extend this system or accept a new kind of input

*2 lessons from 2 findings.*

- A request to ADD a capability to this system has no route: lead-agent's routing table is delivery-only and improvement-agent's triggers are finding-only. Route capability requests to improvement-agent in capability mode, authorised by a design document in docs/improvements/, and do not hand-create agents/ or constraints/ files to work around it.  
  <sub>IMP-0027</sub>
- Every input surface must name the agent that owns it. docs/Import/ accepts any document but only plan-agent and architect-agent intake from it, so a commercial or operational source dropped there is silently unread. Give pm-agent a BASELINE INTAKE mode and add a commercial checklist to the intake skill before relying on a quote that lives in that folder.  
  <sub>IMP-0028</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*3 lessons from 3 findings.*

- The provisioning certificate is in this Mac's CurrentUser/My keychain (thumbprint A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE, app id 077f1f90-3218-4a06-bc90-887464353aa7). Cert-based app-only auth to DEV works from there — do not ask the reviewer to re-supply it.  
  <sub>IMP-0022</sub>
- `pac solution check` runs locally against an existing pac auth profile - the --githubFederated `auth` step is not required for it. ~35s, uploads the packed managed .zip to the hosted Europe checker, prints a severity table to stdout. READ THE RESULT FROM STDOUT: --outputDirectory created an EMPTY directory again on this run, re-confirming IMP-0010's space-in-path behaviour despite the log saying 'Finished downloading 1 files'. And check logs/build.log before claiming a step has never run.  
  <sub>IMP-0040</sub>
- An alternate key CAN target a lookup column (proven live: rev_grant.rev_applicationid), so ADR-G02's one-grant-per-application enforcement is sound. BUT the index is created ASYNCHRONOUSLY and reports EntityKeyIndexStatus=Pending straight after creation - while Pending it does NOT enforce uniqueness. Query EntityDefinitions(...)?$expand=Keys($select=EntityKeyIndexStatus) and wait for Active before treating the constraint as live or using the key for an upsert.  
  <sub>IMP-0044</sub>


## Unrouted — no section assigned

> These findings' `class_instance_of` values are missing from the routing table in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches the agent at the moment it applies.

*1 lesson from 1 finding.*

- Check that a file named in your Knowledge to Load section actually contains knowledge. All four of plan-agent's domain files are still [PLACEHOLDER] templates; the real domain knowledge for this project is in docs/plans/ (approved SDD), docs/architecture/ (approved TAD) and docs/Import/ (DPIA, RoPA, Data Governance). A slice SDD should cite those, and an agent authoring a feature with no parent SDD has no domain knowledge at all and will not be told so.  
  <sub>IMP-0034</sub>


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
