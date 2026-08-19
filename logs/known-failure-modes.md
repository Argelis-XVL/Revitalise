# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (69 entries, 69 distinct lessons)
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
| **x13** | `gate-cannot-fail` | IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025, IMP-0035, IMP-0036, IMP-0041, IMP-0042, IMP-0043, IMP-0046, IMP-0050 |
| **x8** | `platform-contract-guessed-not-groundtruthed` | IMP-0001, IMP-0006, IMP-0011, IMP-0017, IMP-0037, IMP-0044, IMP-0045, IMP-0068 |
| **x7** | `learning-substrate-destroyed` | IMP-0016, IMP-0022, IMP-0023, IMP-0033, IMP-0038, IMP-0049, IMP-0055 |
| **x5** | `exit-zero-does-not-mean-created` | IMP-0013, IMP-0018, IMP-0019, IMP-0030, IMP-0065 |
| **x5** | `no-assertion-on-shipped-content` | IMP-0008, IMP-0015, IMP-0047, IMP-0052, IMP-0060 |
| **x3** | `baseline-restated-not-cited` | IMP-0029, IMP-0063, IMP-0064 |
| **x3** | `two-invocation-paths-disagree` | IMP-0026, IMP-0051, IMP-0053 |
| **x2** | `credential-not-on-the-machine-that-needs-it` | IMP-0048, IMP-0061 |
| **x2** | `declared-knowledge-source-is-empty` | IMP-0034, IMP-0058 |
| **x2** | `harness-blocks-destructive-call` | IMP-0021, IMP-0040 |
| **x2** | `test-coupled-to-absolute-counts` | IMP-0005, IMP-0039 |


## Before you execute a build config

*20 lessons from 20 findings.*

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
- A test asserting an absolute schema count breaks on every legitimate schema addition. Expect to fix counts when you add columns; do not assume the test found a defect.  
  <sub>IMP-0005</sub>
- A structural check that regexes raw XML text can be satisfied by a marker inside a COMMENT. Strip comments before asserting on element presence.  
  <sub>IMP-0020</sub>
- A negative-test fixture for a scanner must not be a literal in source. Assemble the pattern at runtime from fragments, or generate the fixture into a temp directory, so the fixture is real at execution time and invisible at rest.  
  <sub>IMP-0024</sub>
- Never put angle brackets in a Pester test name — `<foo>` is a template placeholder resolved against $foo. And verify the suite through `src/tests/Invoke-Tests.ps1`, the path CI actually uses, not only `Invoke-Pester -Path`.  
  <sub>IMP-0026</sub>
- `pac solution pack` accepts a malformed GUID and exits 0 - a non-hex character in a form, tab, section or cell id packs cleanly and fails later in the environment. `scripts/verify-guid-syntax.py` (gate `guid-syntax`) now checks every 36-character {...} token in every solution .xml AND in every file name, because SolutionPackager names form and view files after their ids.  
  <sub>IMP-0036</sub>
- Adding one Dataverse table breaks about a dozen absolute-count assertions across the Pester suite, none of them a real defect. Expect to update counts; do not assume a failure found a bug. SECOND instance of this class - it now needs generalising (derive counts from source, or assert invariants) rather than another round of hand-editing.  
  <sub>IMP-0039</sub>
- The `auth` step cannot run outside GitHub Actions - it needs the OIDC token env vars. Locally, an existing `pac auth` profile serves the same purpose and `lint` works from it. Declare the step conditional on the CI context rather than deferring it every local build, and do not let a manifest claim 'no deferred steps' when a step was skipped.  
  <sub>IMP-0041</sub>
- There is no PnP site template in provisioning/sharepoint/templates/ - only a README - so no script in this repo can create a SharePoint library today. ensure-site.ps1 takes -Env only and applies a template as the source of truth for libraries. A TAD that declares a SharePoint library as a prerequisite must also declare who authors that template.  
  <sub>IMP-0046</sub>
- When adding a build step that IS a gate, check `python3 scripts/verify-build-config.py` reports the gate COUNT rising, not just the step count. A gate whose name matches no pattern in GATE_NAME_PATTERNS is silently exempt from the negative-test requirement — the gate-over-the-gates has a gate-shaped hole in it.  
  <sub>IMP-0050</sub>
- A number that appears in both a document and a script default will drift, and the path that passes it explicitly will hide the drift. Either read it from the document at run time, or assert the two are equal in a test. Check the DEFAULT of any parameter the build always overrides — it is the branch nothing exercises.  
  <sub>IMP-0051</sub>
- config/models.yml is the ONLY place a model id may appear, and it goes stale silently. Check it against the current Anthropic models page whenever a new Claude generation ships. Do not restate pricing in this repo at all — cite the pricing page at the moment a budget is made, exactly as IMP-0029 requires for contracted hours.  
  <sub>IMP-0053</sub>
- Scope a secret scan to what the build READS, never to `.`. Scanning build output means scanning tool-generated text with generic detectors, and the false positives land on a HARD gate. A gate that fires on nothing teaches people to ignore it — the mirror of a gate that cannot fire. When narrowing any security gate, add a test proving the narrowing did not remove the case it exists for.  
  <sub>IMP-0057</sub>


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

*7 lessons from 7 findings.*

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
- Invoiced hours are not completed hours. Never compute a variance against an estimate for a phase still in progress: the phase looks efficient right up until the remaining work is booked. Before comparing actuals to an estimate, establish that the phase is CLOSED - client testing and feedback included, since those are the activities most likely to be outstanding when the build looks done.  
  <sub>IMP-0065</sub>


## Before you report SUCCESS at all

*11 lessons from 11 findings.*

- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- ensure-schema.ps1 derives nothing from disk: Get-RevEntityLogicalNames is a hand-kept list and the relationship detail path was hardcoded to one file. An entity absent from that list is an entity C-TECH-050's prerequisite step will NOT create, silently - so adding a table means editing that list, and a gate should compare it against Entities/ on disk.  
  <sub>IMP-0038</sub>
- When a fix makes one config resolve a value per run, grep for every OTHER file that names that value. IMP-0016 fixed build.yml and left pipeline.yml pointing at a directory that stopped existing the next day. Also: `upload-artifact` roots the archive at the least common ancestor of the paths it matched — name the PARENT directory, not a `**` glob, or the directory you care about is stripped from the archive.  
  <sub>IMP-0049</sub>
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
- Adding a table is TWO changes: the entity plus a SubArea in the app's site map. `forms-and-views-reachable` proves the pack keeps the form; it says nothing about whether anyone can navigate to it. Before declaring a table delivered, grep AppModuleSiteMaps/ for its logical name.  
  <sub>IMP-0052</sub>
- Scaffolding demo data in an audit log is worse than no log: it answers 'what did the system do' with work that never happened. When adopting a template repository, clear logs/ and build/artifacts/ in the same commit that makes it a real project — and check .gitignore's re-include rules, which are what let a foreign manifest reach git.  
  <sub>IMP-0055</sub>
- Adding a Dataverse table is TWO changes: the entity, and a SubArea in AppModuleSiteMaps/. `forms-and-views-reachable` proves the packer keeps the form; `shipped-content` proves a person can reach it. Before declaring a table delivered, grep AppModuleSiteMaps/ for its logical name.  
  <sub>IMP-0060</sub>


## Operating constraints of this environment

*2 lessons from 2 findings.*

- This repo's path contains spaces. `pac solution check --outputDirectory` silently writes nothing; read the result from stdout instead.  
  <sub>IMP-0010</sub>
- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>


## Before you run something on a machine it has never run on

*3 lessons from 3 findings.*

- A certificate THUMBPRINT is a lookup key, not a credential. Any job running provisioning/**/*.ps1 must also import the .pfx into the runner's CurrentUser/My store and prove the thumbprint resolves WITH a private key before the first step that uses it. Use X509Store, never Import-PfxCertificate or Cert:\ — both are Windows-only (C-TECH-054).  
  <sub>IMP-0048</sub>
- When an ADR changes the environment chain, the executable configs are the EASY half. Grep agents/, CLAUDE.md and every README for the old environment names in the same change — an agent following a stale instruction blocks on a gate keyword nobody is going to send, and reports it as waiting rather than as broken. Read the environments out of config/<slug>-pipeline.yml, never out of a numbered stage heading.  
  <sub>IMP-0056</sub>
- Filename CASE is part of the contract on every filesystem except the one you are probably using. Check `git ls-files` rather than `ls` when a file must be found by an exact name — `ls` on macOS shows you what you meant, `git ls-files` shows you what the runner will see.  
  <sub>IMP-0054</sub>


## Before you bill an hour, accept a phase, or report status

*6 lessons from 6 findings.*

- Never restate contracted hours, fees, phase membership or dates in a repo document - cite the generated baseline. SDD section 10 said 106-160h over 7 automations against a signed 292h over 9, and every downstream document inherited it.  
  <sub>IMP-0029</sub>
- WBS v0.5 totals 177-277h over 61 tasks; it is internally consistent and is the CUSTOMER-ACCEPTED specification. The agreement's total is unverified — 292 is the reviewer's recollection, not a figure read from the PDF. Do not quote a contracted total until it is read from the signed document. `brew install poppler` makes that document machine-readable and is the cheapest way to close this permanently.  
  <sub>IMP-0063</sub>
- Resolve every incoming request to WBS task ids before routing, and take the next unit of work from the ready set over the WBS dependency graph, phase-ordered against contractual dates. Asking 'what next' in conversation built Phase 2 in August while Phase 1, due three weeks earlier, sat untouched.  
  <sub>IMP-0031</sub>
- Propose actual hours at the moment the evidence exists - on each DEV deploy and in each dev summary - not at month end. The WBS shipped with Actual Hours and Delta columns and all 61 rows were still empty six weeks into a T&M engagement.  
  <sub>IMP-0032</sub>
- A work breakdown that reconciles against ITSELF is not thereby complete. When a computed total misses a stated one, ask what work is MISSING from the breakdown before concluding the documents disagree - here it was 20 hours of DocuSign platform selection and trialling, which is distinct from building the DocuSign workflow. WBS v0.5 needs a v0.6 carrying it; do not edit v0.5, it is the customer-accepted specification.  
  <sub>IMP-0064</sub>
- An evidence rule must be satisfiable only by the deliverable existing, never by a declaration that it will. A grep for a table name passes on a role privilege that forward-declares it; pair every grep with an existence check on the thing itself.  
  <sub>IMP-0067</sub>


## Before you extend this system or accept a new kind of input

*4 lessons from 4 findings.*

- A request to ADD a capability to this system has no route: lead-agent's routing table is delivery-only and improvement-agent's triggers are finding-only. Route capability requests to improvement-agent in capability mode, authorised by a design document in docs/improvements/, and do not hand-create agents/ or constraints/ files to work around it.  
  <sub>IMP-0027</sub>
- Every input surface must name the agent that owns it. docs/Import/ accepts any document but only plan-agent and architect-agent intake from it, so a commercial or operational source dropped there is silently unread. Give pm-agent a BASELINE INTAKE mode and add a commercial checklist to the intake skill before relying on a quote that lives in that folder.  
  <sub>IMP-0028</sub>
- Check that a file named in your Knowledge to Load section actually contains knowledge. All four of plan-agent's domain files are still [PLACEHOLDER] templates; the real domain knowledge for this project is in docs/plans/ (approved SDD), docs/architecture/ (approved TAD) and docs/Import/ (DPIA, RoPA, Data Governance). A slice SDD should cite those, and an agent authoring a feature with no parent SDD has no domain knowledge at all and will not be told so.  
  <sub>IMP-0034</sub>
- If a function must be mockable from a test that INVOKES a script (rather than dot-sourcing it), the function must live in a .psm1 and be imported — a dot-sourced definition is re-created in the script's own scope and shadows the mock. When mocking a function that a module calls internally, Pester needs -ModuleName <module> to patch that module's session state.  
  <sub>IMP-0062</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*7 lessons from 7 findings.*

- The provisioning certificate is in this Mac's CurrentUser/My keychain (thumbprint A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE, app id 077f1f90-3218-4a06-bc90-887464353aa7). Cert-based app-only auth to DEV works from there — do not ask the reviewer to re-supply it.  
  <sub>IMP-0022</sub>
- `pac solution check` runs locally against an existing pac auth profile - the --githubFederated `auth` step is not required for it. ~35s, uploads the packed managed .zip to the hosted Europe checker, prints a severity table to stdout. READ THE RESULT FROM STDOUT: --outputDirectory created an EMPTY directory again on this run, re-confirming IMP-0010's space-in-path behaviour despite the log saying 'Finished downloading 1 files'. And check logs/build.log before claiming a step has never run.  
  <sub>IMP-0040</sub>
- An alternate key CAN target a lookup column (proven live: rev_grant.rev_applicationid), so ADR-G02's one-grant-per-application enforcement is sound. BUT the index is created ASYNCHRONOUSLY and reports EntityKeyIndexStatus=Pending straight after creation - while Pending it does NOT enforce uniqueness. Query EntityDefinitions(...)?$expand=Keys($select=EntityKeyIndexStatus) and wait for Active before treating the constraint as live or using the key for an upsert.  
  <sub>IMP-0044</sub>
- docs/Import/'Application Data Export'.{xlsx,csv} are the WordPress form's FIELD SCHEMA, not applicant data — 163 column definitions and one descriptive row, no emails, no postcodes, no NHS numbers. PM redesign decision D-8 is therefore answered NO and is not a DPIA matter. Do not re-raise it. A file named like a data export is worth opening before escalating it: the check is aggregate-only (count emails, postcodes, id-shaped numbers) and needs no personal data to be read or printed.  
  <sub>IMP-0058</sub>
- Write reports to be DECIDED FROM, not to be complete. Fixed order: Summary, What has been built, Elements added/changed, What is still open, What you need to decide, verification. Every identifier in prose is a clickable line-link to where it lives ([C-TECH-062](path#L132)) — grep the line number, never guess it, and never collect links into a references section because the reader cannot tell which belongs to which claim. NO <details>/<summary>: they do not render as expandable in this client. Conclusion first, then at most three sentences of rationale. Keep IMP-nnnn ids out of the body.  
  <sub>IMP-0059</sub>
- On macOS, X509Store('My','CurrentUser') IS the login keychain — no separate keychain API is needed, and Get-ProvisioningCertificate resolves the identity directly. Provisioning for this project therefore runs FROM THE MAC, not from a Linux runner; the CI cert-install action is the optional Linux path and the promote jobs now run it only when the .pfx secret exists, failing fast with the real reason when it does not.  
  <sub>IMP-0061</sub>
- A PDF with subset fonts IS machine-readable with the standard library: each font's /ToUnicode CMap reverses its encoding. scripts/lib/pmsources.py does it, and the same module reads .xlsx via zipfile + xml.etree. The signed agreement totals 292 hours, verified two ways. No poppler, pypdf or pandas install is needed for any contractual source.  
  <sub>IMP-0068</sub>


## Unrouted — no section assigned

> These findings' `class_instance_of` values are missing from the routing table in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches the agent at the moment it applies.

*2 lessons from 2 findings.*

- Walk the contract chain in BOTH directions. A task claiming completion with no artefact is an unevidenced claim; an artefact no task accounts for is unquoted work, and only the reverse direction finds it. rev_grantadministration shipped with no WBS task naming it.  
  <sub>IMP-0066</sub>
- When a schedule computes headroom per phase, check whether the same capacity is being counted for more than one phase - it must be cumulative, because finishing phase N requires finishing 0..N-1 too. And distinguish 'late because nobody started it' from 'late because it is blocked on the client': the first needs a queue, the second needs a phone call.  
  <sub>IMP-0069</sub>


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
