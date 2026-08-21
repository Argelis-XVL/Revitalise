# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (174 entries, 174 distinct lessons)
Generated: 2026-08-21

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
| **x23** | `gate-cannot-fail` | IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025, IMP-0035, IMP-0036, IMP-0041, IMP-0042, IMP-0043, IMP-0046, IMP-0050, IMP-0089, IMP-0115, IMP-0117, IMP-0129, IMP-0132, IMP-0141, IMP-0152, IMP-0157, IMP-0159, IMP-0167 |
| **x20** | `platform-contract-guessed-not-groundtruthed` | IMP-0001, IMP-0006, IMP-0011, IMP-0017, IMP-0037, IMP-0044, IMP-0045, IMP-0068, IMP-0074, IMP-0087, IMP-0091, IMP-0108, IMP-0112, IMP-0116, IMP-0124, IMP-0128, IMP-0135, IMP-0137, IMP-0153, IMP-0161 |
| **x14** | `learning-substrate-destroyed` | IMP-0016, IMP-0022, IMP-0023, IMP-0033, IMP-0038, IMP-0049, IMP-0055, IMP-0080, IMP-0103, IMP-0118, IMP-0125, IMP-0126, IMP-0154, IMP-0169 |
| **x13** | `exit-zero-does-not-mean-created` | IMP-0013, IMP-0018, IMP-0019, IMP-0030, IMP-0065, IMP-0078, IMP-0082, IMP-0101, IMP-0104, IMP-0106, IMP-0114, IMP-0122, IMP-0148 |
| **x10** | `no-assertion-on-shipped-content` | IMP-0008, IMP-0015, IMP-0047, IMP-0052, IMP-0060, IMP-0085, IMP-0090, IMP-0127, IMP-0131, IMP-0139 |
| **x8** | `gate-reassures-wrongly` | IMP-0069, IMP-0094, IMP-0110, IMP-0134, IMP-0147, IMP-0149, IMP-0151, IMP-0156 |
| **x8** | `two-invocation-paths-disagree` | IMP-0026, IMP-0051, IMP-0053, IMP-0077, IMP-0093, IMP-0107, IMP-0144, IMP-0168 |
| **x7** | `output-shape-defeats-the-reader` | IMP-0059, IMP-0070, IMP-0095, IMP-0102, IMP-0109, IMP-0130, IMP-0142 |
| **x5** | `harness-blocks-destructive-call` | IMP-0021, IMP-0040, IMP-0084, IMP-0133, IMP-0170 |
| **x5** | `v3-does-not-imply-v4` | IMP-0012, IMP-0088, IMP-0100, IMP-0113, IMP-0121 |
| **x4** | `baseline-restated-not-cited` | IMP-0029, IMP-0063, IMP-0064, IMP-0096 |
| **x4** | `evidence-rule-satisfied-by-a-forward-reference` | IMP-0067, IMP-0097, IMP-0099, IMP-0140 |
| **x4** | `test-coupled-to-absolute-counts` | IMP-0005, IMP-0039, IMP-0120, IMP-0155 |
| **x3** | `agent-instructions-describe-a-topology-that-changed` | IMP-0056, IMP-0092, IMP-0162 |
| **x3** | `config-placeholder-known-but-not-fixed` | IMP-0145, IMP-0166, IMP-0175 |
| **x3** | `credential-not-on-the-machine-that-needs-it` | IMP-0048, IMP-0061, IMP-0105 |
| **x3** | `declared-policy-not-mechanically-enforced` | IMP-0143, IMP-0165, IMP-0174 |
| **x3** | `hand-maintained-count-drifts-from-source` | IMP-0150, IMP-0160, IMP-0176 |
| **x3** | `platform-state-divergence` | IMP-0123, IMP-0136, IMP-0171 |
| **x2** | `declared-knowledge-source-is-empty` | IMP-0034, IMP-0058 |
| **x2** | `gate-fires-on-nothing` | IMP-0057, IMP-0164 |
| **x2** | `repo-path-contains-spaces` | IMP-0010, IMP-0079 |
| **x2** | `test-asserts-the-defect` | IMP-0111, IMP-0138 |


## Before you execute a build config

*38 lessons from 38 findings.*

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
- A preflight result that depends on files left behind by a previous run is not a result. `tee PATH` PRODUCES that path and `test -s PATH` asserts on it — both now have branches in extract_paths — and any new intra-step write-then-assert pattern needs one too. When changing the preflight, run it with ARTIFACT_DIR pointing at a directory that does NOT exist; on a reused directory it will agree with you for the wrong reason.  
  <sub>IMP-0089</sub>
- A corrected worklog session must be excluded by every reader of logs/worklog.jsonl, not just by verify-worklog.py. Put the corrects/superseded rule in scripts/lib/ and have verify-wbs-chain.py and compute-invoice.py call it, or the repository states two different invoiced-to-date totals and both gates pass.  
  <sub>IMP-0093</sub>
- unit-tests is TWO gates in one step - the test count and the 80% coverage threshold - and a manifest that records only the counts hides a HARD C-TECH-014 failure. Record BOTH numbers, always. And when you add a .ps1 under provisioning/{common,entra,dataverse}, coverage scope includes it the moment it lands: contract tests that assert a script's output vocabulary lift the test count and cover almost none of its lines, so the suite goes greener while the constraint goes red. Check the coverage figure, not the pass count, after adding provisioning code.  
  <sub>IMP-0132</sub>
- EnsureSchema.Tests.ps1's option-set count (line 196), role count (line 503), relationship-call count (line 592) and AddPrivilegesRole-call count (line 601) are FOURTH-instance absolute-count assertions (after IMP-0005/IMP-0039/IMP-0120) and are currently stale (expect 21/2/3/79, actual 24/3/6/99) against rev_review + REV Trustee role work already in this tree. Not fixed by this entry's author - out of that WBS scope - but the underlying counts, not the test file, are correct; whoever owns rev_review/REV Trustee (or the next agent to touch this file) should update the four numbers, and this is the fourth recorded case for generalising these tests to re-derive their expected counts from source (the way the FieldSecurityProfiles cross-reference test in the same file already does at line ~294) rather than hardcoding a number that must be remembered.  
  <sub>IMP-0155</sub>
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

> **18 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0050, IMP-0051, IMP-0053, IMP-0057, IMP-0077, IMP-0107, IMP-0115, IMP-0117, IMP-0120, IMP-0129, IMP-0141, IMP-0144, IMP-0152, IMP-0157, IMP-0159, IMP-0164, IMP-0167, IMP-0168. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you hand-author a platform artefact

*17 lessons from 17 findings.*

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
- `secrets` is not available in ANY `if:` expression - GitHub rejects the WHOLE workflow file and every run shows zero jobs, with no failing check to notice. To branch on whether a secret exists, project it into a job-level `env` boolean (job `env` MAY read secrets) and test `env.FLAG == 'true'` in the step `if:`. And validate .github/workflows/*.yml before pushing: an invalid workflow file is the only defect class CI cannot tell you about, because nothing runs.  
  <sub>IMP-0074</sub>
- subscriptionRequest/runas must be 3 for 'flow owner' on a Dataverse row trigger. 4 packs, imports and reports statecode=Activated while creating NO webhook subscription, so the flow never fires and nothing reports a problem. After turning any Dataverse-triggered flow on, assert a callbackregistration row exists for the table (callbackregistrations?$filter=entityname eq 'x') - that is the only signal that distinguishes a registered trigger from an activated-but-dead one. Source at REVScoringCalculateAndFlag line 59 still carries 4 and will reproduce this in TST/ACC and PRD.  
  <sub>IMP-0108</sub>
- The intake flow still has SIX Get-a-row-by-id actions using an alternate key in Row ID (AgeBandMap, PostcodeRegionMap, AgeRangeLabelMap, ExceptionalCircumstanceLabelMap, EmploymentStatusLabelMap, CareHoursBandLabelMap). The connector rejects that shape - proven by the scoring flow failing on all 11 of its first runs - so the intake flow will fail on its first live submission from the website. Fix it the same way before Alex's integration is connected: one List rows call filtered for all six names, then first(body('Setting_<Key>'))?['rev_value'] per value, plus a row-count guard because List rows returns a short array where Get-a-row-by-id returned 404.  
  <sub>IMP-0112</sub>
- The Dataverse connector is ASYMMETRIC: CreateRecord accepts a nested "item": { columns } object (verified working), UpdateRecord does NOT - its columns must be flattened to "item/<column>" beside entityName and recordId, the same way Teams uses body/recipient and Office 365 uses emailMessage/To. A nested item on an UpdateRecord shows as an action with NO PROPERTIES CONFIGURED in the designer and writes nothing WHILE SUCCEEDING, so there is no error and no error-log row - a green run and an empty column is the only symptom. When a flow 'works' but a column is empty, open the write action in the designer and look at whether it has any properties at all.  
  <sub>IMP-0116</sub>
- The workflow definition language has NO select() and NO filter() expression - both are data-operation ACTIONS (Select, Filter array), and item() is only valid inside one. To project an array in an expression you cannot; add a Select action and join its body. Grep any flow for 'select(' and 'filter(' before believing it works: both pack, import and report Activated, and fail only when the branch containing them is first taken. Related: if() evaluates ONLY the branch it takes here, proven by TD-07 failing and TD-08 passing on the same action.  
  <sub>IMP-0124</sub>
- Initialize variable is legal ONLY at the top level of a Power Automate flow - never inside a Scope, condition, Apply to each or Switch. A nested one packs, imports and reports Activated, then the designer refuses to save and the flow cannot be turned on. Increment/Set/AppendToString variable may nest freely; only the declaration may not. When a nested declaration has to be lifted, move the runAfter guard it sat behind onto the action that CONSUMES the variable, not onto the declaration.  
  <sub>IMP-0137</sub>
- A field security profile's membership list is who it grants access TO, not who it withholds from - never write a dispatch instruction that says 'bind role X to profile Y' without first reading the profile XML to confirm whether X should be ADDED as a member (grants access) or must NEVER be a member (the actual control). For REV_TrusteeRestricted specifically, the control IS non-membership - trustees must never be added to it.  
  <sub>IMP-0153</sub>
- Read the WHOLE artefact when copying a shape - `head -12` of an option set hides the optionset-level <Descriptions> and <displaynames> that sit after </options>, and `pac solution pack` accepts their absence with exit 0. A truncated read of a source of truth is not ground truth.  
  <sub>IMP-0037</sub>
- A site-map SubArea that must open a SPECIFIC view is a platform contract this project has not ground-truthed, and the current source is a guess that does not work: all five view-pinned sub-areas carry BOTH Entity= and Url=, and every one opens the table's default view. Do NOT fix it with a second guess — that is what produced the first one. Use the A-001 method that worked: have the reviewer point ONE sub-area at the intended view in the app designer, save and publish, then read the platform's own regenerated sitemapxml back via the Web API and copy that exact shape for the rest. It is very unlikely to be a platform limitation; it is unverified.  
  <sub>IMP-0087</sub>
- A site-map SubArea Url must be a ROOT-RELATIVE URL — a leading slash, then ?, then the query string: Url="/main.aspx?pagetype=entitylist&etn=<table>&viewid=<guid>". A bare `&pagetype=...` fragment is not a URL; the app designer rejects it with 'expects a web resource' and the sub-area disappears from play mode. Read the shape off a Microsoft-authored managed sitemap in the same org — 'Power Platform Environment Settings' has 25 examples — rather than inferring it. AND NOTE: a leading-slash URL carries no host, so it is environment-independent and does NOT breach C-TECH-047; the solution-awareness objection to hardcoding a URL is answered by the relative form, not by avoiding URLs.  
  <sub>IMP-0091</sub>
- pac code ground truth (pac 2.4.1, verified 2026-08-21): `pac code init` creates ONLY power.config.json - it does not scaffold React, so the Vite project is hand-authored; `pac code add-data-source` generates the GENERIC Dataverse connector typing with no per-table models (grep -c rev_ returns 0); `pac code list-tables`/`list-datasets` fail with an empty `{}` against this connection on all three dataset forms, so the typed route is unreachable here; and the generated MicrosoftDataverseService.ts DOES NOT COMPILE - a parameter named `MSCRM.IncludeMipSensitivityLabel` contains an illegal `.`. Work around it via getClient(dataSourcesInfo) from @microsoft/power-apps/data, never by editing generated output.  
  <sub>IMP-0161</sub>


## Before you declare a deploy or an import successful

*19 lessons from 19 findings.*

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
- Attribute-level IsAuditEnabled proves nothing: Dataverse auditing needs organizations.isauditenabled AND the table's own IsAuditEnabled, and NEITHER is settable from solution source — entity-level IsAuditEnabled is absent from every Entity.xml here. Query organizations?$select=isauditenabled,auditretentionperiodv2 and EntityDefinitions(...)?$select=IsAuditEnabled live before reporting any audit constraint as PASS, and check logs/pipeline.log that ensure-auditing.ps1 actually ran — on 2026-08-19 it never had, and DEV had no audit trail at all.  
  <sub>IMP-0082</sub>
- An environment variable DEFINITION travels in the solution; its VALUE does not, and nothing in this repo writes one. Query environmentvariablevalue joined to environmentvariabledefinition before believing any flow can notify anyone: on 2026-08-20 DEV held 4 definitions and 0 values, so every Teams action and the failure-alert fallback email would have failed. isrequired=1 with no defaultvalue is the shape to look for - it is a required setting nobody is scripted to supply.  
  <sub>IMP-0101</sub>
- statecode=1 on a cloud flow does NOT mean its Dataverse trigger is registered. Query callbackregistrations?$filter=entityname eq '<table>' - if it returns 0, Dataverse will never call the flow, no run is attempted, and run history shows nothing because there is nothing to show. Fix it by opening the flow in the Power Automate DESIGNER and saving it, not by toggling it in the Solutions list. Check the count as an identity with System Administrator, or a 0 may mean you cannot see the rows. And note the trap this creates: a row-CREATED trigger never replays, so rows inserted before the registration existed must be deleted and re-created.  
  <sub>IMP-0104</sub>
- When a Dataverse-triggered flow does not fire, ownership and scope are NOT the first thing to suspect - prove it with two rows, one owned by the flow owner and one not, which takes two minutes and rules out scope=User entirely. If neither fires and callbackregistrations is 0, every remaining cause is OUTSIDE Dataverse (connection health, DLP policy, a subscription error shown only in the maker UI) and no amount of further querying will find it: hand it to someone with the Power Automate UI. Also: a designer save can silently change the trigger's scope (4 Organization -> 1 User here), so re-read subscriptionRequest/scope out of workflow.clientdata after any save and compare it against solution source. Two Web API details found on the way: ownerid expands to the 'principal' type which has NO fullname (select _ownerid_value and resolve it separately), and Write-Output inside a PowerShell function merges into that function's return value - use Write-Host for progress lines.  
  <sub>IMP-0106</sub>
- A callbackregistration row surviving a solution import is not evidence that the trigger works. Compare its createdon against the flow's modifiedon: if the registration predates the import, it pins logicappsversion to a definition version that no longer exists, and Dataverse delivers events into nothing - no run, no error, empty run history. Existence is the wrong assertion. The registration must be RECREATED: turn the flow off, confirm the row disappears, then turn it on from the DESIGNER and confirm a row with a NEW createdon appears. Deploying a Dataverse-triggered flow therefore has a mandatory post-deploy step that no import performs and no query can substitute for.  
  <sub>IMP-0114</sub>
- Set an environment variable's CURRENT VALUE, never its DEFAULT VALUE. A default lives inside the environmentvariabledefinition, which is solution content, so the next import overwrites it with whatever source declares - nothing - and every flow that reads it silently loses its configuration. A current value is a separate environmentvariablevalue row that no import here touches. Check with: environmentvariabledefinitions?$select=schemaname,defaultvalue&$expand=environmentvariabledefinition_environmentvariablevalue($select=value) - if the value comes from defaultvalue, it will not survive the next deploy. seed-test-data.ps1 now reports the source of each value and blocks when rev_ProcessOwnerUpn is empty.  
  <sub>IMP-0121</sub>
- Adding a column is TWO deployments, not one. The form cell travels in the solution import; the COLUMN does not - creating schema by import is unsupported, which is exactly why ensure-schema.ps1 exists. Run `pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev` after any import that adds a column, and verify with EntityDefinitions(LogicalName='x')/Attributes?$select=LogicalName. Skip it and you ship a form bound to a column that is not there, with a successful import and a published solution to reassure you.  
  <sub>IMP-0122</sub>
- A callbackregistration existing, with a createdon that is not stale against the flow's modifiedon, and a live subscriptionRequest matching source exactly, is still not proof a Dataverse-triggered flow will fire — the only proof is creating a real row and observing rev_scoredon (or an asyncoperation, or an error log row) change. REV | Scoring | Calculate & Flag passed every documented precondition in REV-GrantApplications-ACC (TST/ACC) and did not fire for any of 12 rows in 9 minutes, after firing correctly for all 12 in DEV. The fix per IMP-0104/IMP-0114 is to open the flow in the Power Automate DESIGNER and save it (or turn off, confirm the registration row disappears, then turn on from the designer) — never by toggling state or PATCHing statecode via the Web API (IMP-0113) — and this needs a human with maker access to TST/ACC, which no identity used by this project's scripts has.  
  <sub>IMP-0148</sub>
- Solution import RELABELS matching option values but does NOT delete values the new source omits. Orphaned values survive every subsequent import. Compare live option-set members against source.  
  <sub>IMP-0019</sub>
- Invoiced hours are not completed hours. Never compute a variance against an estimate for a phase still in progress: the phase looks efficient right up until the remaining work is booked. Before comparing actuals to an estimate, establish that the phase is CLOSED - client testing and feedback included, since those are the activities most likely to be outstanding when the build looks done.  
  <sub>IMP-0065</sub>
- A manifest's source_commit only describes the artifact if the working tree was clean when the pack ran. Record `git status --porcelain` alongside the sha and state the count, because a sha copied from HEAD over a dirty tree names source the zip does not contain — build #7's manifest named a commit predating the whole rev_grant table it had just packaged.  
  <sub>IMP-0078</sub>
- Renders-in-edit-mode is not renders-in-play-mode. A site map confirmed by Web API query, in a published app, can still fail to render for a user — so V4 stays a named human step and is never inferred from a successful query, however thorough. When it happens, re-check after propagation time before diagnosing, and check the sub-area shape (IMP-0087) before blaming the platform.  
  <sub>IMP-0088</sub>
- statecode=0 on a cloud flow means DRAFT, not activated, and a solution import never turns a flow on. Query workflows(<id>)?$select=statecode and read 1 as Activated; do not accept a Deployment Summary's word for it - this project's own summary labelled statecode=0 'activated' while its Dev Summary correctly called the same value Draft. A flow in Draft receives no trigger, so a row created against it is never processed and never will be.  
  <sub>IMP-0100</sub>
- An unmanaged pac solution import with --force-overwrite DEACTIVATES every cloud flow in the solution - statecode 1 becomes 0 - while reporting 'completed successfully'. Capture the flow statecodes BEFORE the import and re-assert them after, and treat re-activation as a named post-deploy step with an owner. Re-activate IN THE DESIGNER, never by PATCHing workflow.statecode: a statecode flip can leave the flow reporting Activated with no callbackregistration row, which is the un-triggerable state that cost four rounds on 2026-08-20. Also re-check the callbackregistration count after re-activation - a row from the pre-import flow version survives the import and must not be read as evidence that the new version's trigger is live.  
  <sub>IMP-0113</sub>


## Before you report SUCCESS at all

*18 lessons from 18 findings.*

- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- ensure-schema.ps1 derives nothing from disk: Get-RevEntityLogicalNames is a hand-kept list and the relationship detail path was hardcoded to one file. An entity absent from that list is an entity C-TECH-050's prerequisite step will NOT create, silently - so adding a table means editing that list, and a gate should compare it against Entities/ on disk.  
  <sub>IMP-0038</sub>
- When a fix makes one config resolve a value per run, grep for every OTHER file that names that value. IMP-0016 fixed build.yml and left pipeline.yml pointing at a directory that stopped existing the next day. Also: `upload-artifact` roots the archive at the least common ancestor of the paths it matched — name the PARENT directory, not a `**` glob, or the directory you care about is stripped from the archive.  
  <sub>IMP-0049</sub>
- Adding a Dataverse table to a model-driven app is FOUR changes, not two and not three: (1) the entity, (2) a SubArea in AppModuleSiteMaps/, (3) an <AppModuleComponent type="1" schemaName=".."/> in AppModules/<app>/AppModule.xml, and (4) the audit switch in the environment. Miss (3) and the table appears in the designer's EDIT mode and is absent in PLAY mode, surviving a hard refresh — which reads exactly like a platform caching bug and is not one. Diff AppModule.xml's component list against the Entities/ folders on disk before believing any reachability gate.  
  <sub>IMP-0090</sub>
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
- Allocate a finding id from the MAXIMUM id in the whole log, never from `tail -1`, and re-read immediately before appending — two sessions can be live in this repository at once, and this one is on a synced SharePoint path. Then run scripts/verify-improvement-log.py BEFORE committing: it detects duplicate ids exactly, and it is worthless if it only ever runs in CI. Regenerate the digest and stage it in the same breath as the log, or the commit contains two different moments.  
  <sub>IMP-0080</sub>
- Adding a Dataverse table is THREE changes, not two: the entity, a SubArea in AppModuleSiteMaps/, and the table's audit switch IN THE ENVIRONMENT. The third is not in solution source and cannot be — entity-level IsAuditEnabled is absent from every Entity.xml here — so it does not travel with the table and no source-side gate can see it. Five tables (rev_review, rev_provider, rev_bankaccount, rev_payment, rev_anonymisedstatistic) are still to be built and will each need it. Read it back with EntityDefinitions(LogicalName='x')?$select=IsAuditEnabled; do not infer it from the column flags, which are already 1 and mean nothing on their own.  
  <sub>IMP-0085</sub>
- An Adaptive Card in this solution lives in two places - docs/development/cards/<name>.json and the minified string in the flow's body/messageBody - and nothing checks they agree. After editing either, assert it: json.loads(the messageBody) == json.loads(the card file). The same drift has already put a false statement in a shipped notes.md, so when you change an action's operationId, grep that flow's notes.md for the old one.  
  <sub>IMP-0131</sub>
- Before shipping an instruction to a user, resolve the verb to a mechanism in the solution. 'Re-run scoring' had no mechanism: the scoring flow is create-triggered and reads every answer from triggerOutputs(), so a run-history Resubmit replays the stale payload and returns the same verdict - it is not a re-run, it is a replay. Any genuine rescore needs its own trigger and must read the row fresh, and that is unquoted scope.  
  <sub>IMP-0139</sub>
- Before re-deriving a blocker's analysis, grep docs/improvements/ for its IMP id — a review may already have processed it and stalled at its gate, and the log gate cannot tell that from an unread entry. When a review processes an entry, stamp reviewed_in on EVERY entry it processed, not only the ones it defers: review 4 stamped IMP-0149 and not IMP-0148, and the missing stamp cost a duplicated strategic-tier dispatch five hours later. And an unapproved review's proposals do not exist on disk — check the artefacts before repeating any claim a review document makes about them, because a review is a proposal until the keyword arrives.  
  <sub>IMP-0154</sub>
- Before treating a NEW finding as live work, check whether its fix already shipped — IMP-0155 summoned a strategic-tier review as an unread blocker while the generalisation it demanded was already committed in the same tree, visible in EnsureSchema.Tests.ps1's own comment naming IMP-0155 by id. Companion to IMP-0154 from the other side: that one is a REVIEW leaving no trace, this one is a DELIVERY fix leaving no trace. Allow evidence_grep on a NEW entry and report when it MATCHES, so 'the fix is on disk and the status is stale' becomes a thing the gate says rather than a thing someone notices.  
  <sub>IMP-0169</sub>


## Operating constraints of this environment

*6 lessons from 6 findings.*

- THIRD instance. A gate keyword authorises an operation inside this system; it does not grant the session permission to perform it. Live Dataverse WRITES (metadata PATCH, DeleteOptionValue, organisation settings) are refused by the harness even under APPROVE TENANT, while reads are not. Establish the permission BEFORE reporting that a gate keyword will produce a live change: either the reviewer adds a Bash permission rule, or the operation is handed to them with the exact call to make. Never leave the reviewer believing a keyword was sufficient.  
  <sub>IMP-0084</sub>
- Fifth instance. Any agent that can be dispatched to run a live `provisioning/**/*.ps1` write - not only pipeline-agent - needs the same 'Reviewer-Executed Operations' behaviour: attempt the call, and on a classifier refusal emit the exact command plus its pre/post verification query rather than reporting the task as merely blocked. Currently this behaviour lives only in agents/pipeline-agent.md; development-agent.md's sub-agent table (identity-agent, automation-agent, config-agent, m365-agent - every one that can write to a live environment) has no equivalent pointer.  
  <sub>IMP-0170</sub>
- This repo's path contains spaces. `pac solution check --outputDirectory` silently writes nothing; read the result from stdout instead.  
  <sub>IMP-0010</sub>
- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>
- Third confirmation: `pac solution check --outputDirectory` writes NOTHING on this repo's path and still says 'Finished downloading 1 files'. Tee the command's stdout into the artifact and assert the target directory is non-empty — otherwise the only evidence for a HARD gate lives in a console log that CI throws away.  
  <sub>IMP-0079</sub>
- Fourth instance, and the first since the protocol was written — the protocol worked, so do not escalate it further. Two additions from this one: (1) READS can be refused too, when the shell command carries a $(...) substitution that looks like injection; reach for the dedicated Read tool rather than rephrasing the shell. (2) Capture the pre-import state BEFORE attempting the write, not after the refusal: the environment-variable values, the flow statecodes and the callbackregistration createdon are what the reviewer needs to compare against afterwards, and they are cheap reads that are never refused.  
  <sub>IMP-0133</sub>


## Before you run something on a machine it has never run on

*10 lessons from 10 findings.*

- A certificate THUMBPRINT is a lookup key, not a credential. Any job running provisioning/**/*.ps1 must also import the .pfx into the runner's CurrentUser/My store and prove the thumbprint resolves WITH a private key before the first step that uses it. Use X509Store, never Import-PfxCertificate or Cert:\ — both are Windows-only (C-TECH-054).  
  <sub>IMP-0048</sub>
- When an ADR changes the environment chain, the executable configs are the EASY half. Grep agents/, CLAUDE.md and every README for the old environment names in the same change — an agent following a stale instruction blocks on a gate keyword nobody is going to send, and reports it as waiting rather than as broken. Read the environments out of config/<slug>-pipeline.yml, never out of a numbered stage heading.  
  <sub>IMP-0056</sub>
- The real tenant id (735a23b1-97d7-4c81-85f7-35c50321138a, confirmed working against DEV via dev-scoring-settings.json) is a one-line fix for test-settings.json and prd-settings.json, and it was identified a full day before this entry without being applied. When a finding records a concrete unresolved value, verify the target file was actually edited before marking it APPLIED — do not let a knowledge-doc update stand in for the repo fix.  
  <sub>IMP-0145</sub>
- A provisioning identity working in one Dataverse environment is not evidence it works in another — each environment needs its own application user created for it. Before relying on any provisioning/dataverse/*.ps1 -Env <env> step in a pipeline config, confirm with a plain WhoAmI call that the identity is recognised in that specific org; 'token acquired' only proves Entra ID accepted the audience, never that Dataverse has provisioned the caller.  
  <sub>IMP-0146</sub>
- Before reporting a build SUCCESS or dispatching to pipeline-agent, run python3 scripts/verify-pipeline-config.py config/<slug>-pipeline.yml directly - it is cheap, standalone, and not currently a step in any build.yml, so nothing else will run it for you.  
  <sub>IMP-0175</sub>
- Filename CASE is part of the contract on every filesystem except the one you are probably using. Check `git ls-files` rather than `ls` when a file must be found by an exact name — `ls` on macOS shows you what you meant, `git ls-files` shows you what the runner will see.  
  <sub>IMP-0054</sub>
- When a blocked capability becomes available, grep every agent file and skill for the sentence that said it was blocked - not just the script and the agent that requested the fix. warranty-clock.py now reads Build Terms v1.0 from docs/Import/ and answers; commercial-agent.md and how-to-account-for-billable-time.md still say it refuses.  
  <sub>IMP-0092</sub>
- The provisioning identity can read and write Dataverse but CANNOT read Entra app registrations from this Mac - Connect-ProvisioningGraph succeeds and Get-MgApplication then fails with Authorization_RequestDenied. So provisioning/entra/*.ps1 cannot run here as things stand, and rev_IntakeAllowedClientId's value must come from the Entra portal or from ensure-intake-client.ps1 run under an identity that holds Application.ReadWrite.All with admin consent. A successful Graph connection proves the credential, never the permission. Also: provisioning/deploymentSettings/test-settings.json still carries {{TENANT_ID}}, so anything reading tenantId from it fails fast - the real tenant id is in dev-scoring-settings.json.  
  <sub>IMP-0105</sub>
- config/models.yml declares NO escalation conditions for frontend-agent, even though ADR-003 puts a hand-authored React Code App in the palette - so the sub-agent owning the most novel artefact in the project defaults to standard tier while narrower sub-agents carry explicit escalation rules. When dispatching frontend-agent for Code App work, pass an explicit model override; and when an ADR adds an artefact type, re-read models.yml in the same change.  
  <sub>IMP-0162</sub>
- The REV Trustee role ships with id {PENDING-ROLE-ID-REV-TRUSTEE} and is absent from Other/Solution.xml's <RootComponents>, so root-components-resolve is RED and the role will not deploy until the role is created in DEV, its real roleid read back with `roles?$filter=name eq 'REV Trustee'&$select=roleid`, substituted into both the role file and a new <RootComponent type="20">. Second instance of a known, documented placeholder left in place (IMP-0145 was tenantId). Widen contract/known-exceptions.json beyond commercial gates so a deliberately-red build gate must carry an owner, a clearing action and an expiry instead of only a code comment.  
  <sub>IMP-0166</sub>


## Before you bill an hour, accept a phase, or report status

*11 lessons from 11 findings.*

- Never restate contracted hours, fees, phase membership or dates in a repo document - cite the generated baseline. SDD section 10 said 106-160h over 7 automations against a signed 292h over 9, and every downstream document inherited it.  
  <sub>IMP-0029</sub>
- WBS v0.5 totals 177-277h over 61 tasks; it is internally consistent and is the CUSTOMER-ACCEPTED specification. The agreement's total is unverified — 292 is the reviewer's recollection, not a figure read from the PDF. Do not quote a contracted total until it is read from the signed document. `brew install poppler` makes that document machine-readable and is the cheapest way to close this permanently.  
  <sub>IMP-0063</sub>
- Billing basis is a reviewer decision, not an inference: delivered scope priced at the WBS estimate and reconstructed session time give answers tens of hours apart on the same month. scripts/deliverable-hours.py computes the first, scripts/reconstruct-worklog.py the second, and both print which basis they assume. Until an APPROVE BASELINE amends contract/delivery-parameters.json's estimating_rule, the repository holds both rules and verify-worklog.py will warn on any actual that equals an estimate.  
  <sub>IMP-0096</sub>
- Resolve every incoming request to WBS task ids before routing, and take the next unit of work from the ready set over the WBS dependency graph, phase-ordered against contractual dates. Asking 'what next' in conversation built Phase 2 in August while Phase 1, due three weeks earlier, sat untouched.  
  <sub>IMP-0031</sub>
- Propose actual hours at the moment the evidence exists - on each DEV deploy and in each dev summary - not at month end. The WBS shipped with Actual Hours and Delta columns and all 61 rows were still empty six weeks into a T&M engagement.  
  <sub>IMP-0032</sub>
- A work breakdown that reconciles against ITSELF is not thereby complete. When a computed total misses a stated one, ask what work is MISSING from the breakdown before concluding the documents disagree - here it was 20 hours of DocuSign platform selection and trialling, which is distinct from building the DocuSign workflow. WBS v0.5 needs a v0.6 carrying it; do not edit v0.5, it is the customer-accepted specification.  
  <sub>IMP-0064</sub>
- An evidence rule must be satisfiable only by the deliverable existing, never by a declaration that it will. A grep for a table name passes on a role privilege that forward-declares it; pair every grep with an existence check on the thing itself.  
  <sub>IMP-0067</sub>
- A date read from a contract is a fact about the contract, not about delivery. Record the actual start separately and measure elapsed time from it: the agreement's kick-off was 2026-07-04, work began 2026-08-10, and using the former made every long-standing blocker read as 46 days old on a nine-day-old project. The same trap applies to milestone dates used as evidence that a phase began.  
  <sub>IMP-0073</sub>
- A task whose deliverable names a CLIENT act — sign-off, acceptance, walkthrough, demo — can never be evidenced by a document we authored. Point those rules at contract/acceptance/ or mark them `manual`; a grep of our own test report proves we tested, not that they accepted. Second instance of this class: task 2.8 alongside 8.2 and 6.5, so the fix is a rule about the SHAPE of an evidence rule, not another per-task correction.  
  <sub>IMP-0097</sub>
- Two tasks whose evidence resolves to the same file are one delivered task and one unproven one. Report evidence collisions in derive-wbs-state.py: task 1.6's only proof is a grep inside task 1.2's deliverable, so it earns hours whenever 1.2 ships. Third instance of this class alongside 2.8, 8.2 and 6.5 — the fix belongs on the SHAPE of an evidence rule.  
  <sub>IMP-0099</sub>
- Before marking a finding APPLIED because 'the target file already carries the rule', grep the file for the substance of the lesson, not just confirm the file exists. An APPLIED status is itself a claim (C-COM-005's rule, applied to this log) and this repository's own gates do not yet verify it — do so by hand until they do.  
  <sub>IMP-0140</sub>


## Before you extend this system or accept a new kind of input

*10 lessons from 10 findings.*

- A request to ADD a capability to this system has no route: lead-agent's routing table is delivery-only and improvement-agent's triggers are finding-only. Route capability requests to improvement-agent in capability mode, authorised by a design document in docs/improvements/, and do not hand-create agents/ or constraints/ files to work around it.  
  <sub>IMP-0027</sub>
- Every input surface must name the agent that owns it. docs/Import/ accepts any document but only plan-agent and architect-agent intake from it, so a commercial or operational source dropped there is silently unread. Give pm-agent a BASELINE INTAKE mode and add a commercial checklist to the intake skill before relying on a quote that lives in that folder.  
  <sub>IMP-0028</sub>
- Check that a file named in your Knowledge to Load section actually contains knowledge. All four of plan-agent's domain files are still [PLACEHOLDER] templates; the real domain knowledge for this project is in docs/plans/ (approved SDD), docs/architecture/ (approved TAD) and docs/Import/ (DPIA, RoPA, Data Governance). A slice SDD should cite those, and an agent authoring a feature with no parent SDD has no domain knowledge at all and will not be told so.  
  <sub>IMP-0034</sub>
- If a function must be mockable from a test that INVOKES a script (rather than dot-sourcing it), the function must live in a .psm1 and be imported — a dot-sourced definition is re-created in the script's own scope and shadows the mock. When mocking a function that a module calls internally, Pester needs -ModuleName <module> to patch that module's session state.  
  <sub>IMP-0062</sub>
- Load skills/how-to-report-to-the-reviewer.md BEFORE writing any multi-paragraph report, not after. It was established on 2026-08-19 after three rejected drafts and was then ignored the same day, because it is named in CLAUDE.md but absent from every agent's activation steps and checked by nothing.  
  <sub>IMP-0070</sub>
- In a gate block, the headline number must be the number the human is approving. State the ladder explicitly - evidence span, plus lead-in, equals total session time, minus non-billable, equals BILLABLE FOR APPROVAL - and never reuse the word 'proposed' for two different quantities in the same block.  
  <sub>IMP-0095</sub>
- provisioning/README.md's status vocabulary has no REMOVED state, so a teardown script reports a completed deletion as CREATED. Read the resource NAME on the line, not the status word, when the script is a remove-*. If you add a removal script, say in its header which state you mapped to what - do not leave the reader to infer that CREATED means gone.  
  <sub>IMP-0102</sub>
- result('<scope>')[0] gives the scope's FIRST CHILD, not the action that failed, and for a nested scope its message is the useless wrapper 'An action failed. No dependent actions succeeded.' Filter result() for the child whose status is Failed, and when that child is itself a scope, call result() on the inner scope to reach the leaf. Prove any error-handling path by making the flow fail on purpose and reading what it logged - reasoning about an error expression is not testing it.  
  <sub>IMP-0109</sub>
- A notification a human must ACT on needs a FactSet and a button to the record - not <br/>-separated lines and the name of a view to find by hand. Build the deep link as <rev_GrantAdminAppUrl>&pagetype=entityrecord&etn=<table>&id=<guid from the trigger>; the record button matters more than the list button, because the reader is being told about ONE application. When one notification in a solution gets a card, check every OTHER notification in the same solution in the same change - the three here were authored together and only the one with nothing to open got fixed.  
  <sub>IMP-0130</sub>
- Never write `Write-Output ("a {0}" -f $x) + "b"` across a line break — `-f` binds tighter than `+`, so PowerShell concatenates `"b"` to the RESULT of `("a {0}" -f $x)`'s own trailing fragment only when parenthesised that way, and the outer `Write-Output (...) + ...` shape sends the first piece to the pipeline and evaluates `+` on the cmdlet's return separately, splitting the message across two output lines with a bare `+` between them. Build the whole template with string `+` FIRST inside one set of outer parens, then apply `-f` to the concatenated whole: `(("a {0} " + "b") -f $x)`.  
  <sub>IMP-0142</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*19 lessons from 19 findings.*

- A parent agent's FAILED notification (API spend limit or any other terminal error) does NOT mean its own sub-dispatches stopped — they were already launched and keep running independently, and their completions arrive as separate, later notifications. Before concluding an improvement-agent (or any agent that itself uses the Agent tool) batch did 'nothing', run ListAgents to see every child's status, and verify each touched file directly (compile/parse/selftest/run against real data) rather than trusting only the parent's last words. When the spend limit is hit, do not immediately re-dispatch the same scale of work — it will likely fail identically; surface it to the reviewer (the error names the remedy: /usage-credits, ask the admin for a higher limit) and, if anything must proceed before that, do the smallest remaining reconciliation as a single narrow dispatch, not another wide fan-out.  
  <sub>IMP-0172</sub>
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
- Two working paths for live Dataverse verification from this Mac. (1) `pac env fetch --xmlFile <file>` runs FetchXML against the active pac profile — good for stringmap, sitemap, entitykey; it rejects a `top` attribute, so use no paging attributes. (2) For METADATA (EntityDefinitions, GlobalOptionSetDefinitions, Keys/EntityKeyIndexStatus, organizations) dot-source provisioning/common/provisioning-common.ps1, Import-Module provisioning/common/provisioning-cert.psm1, build the auth triplet by hand (tenant 735a23b1-97d7-4c81-85f7-35c50321138a, app 077f1f90-3218-4a06-bc90-887464353aa7, thumbprint A6F94E1801D1C62B7A82AE75E1AA5AD243ECC7FE) and call Get-DataverseAccessToken + Invoke-DataverseApi. QUIRK: on systemform/savedquery, `startswith(objecttypecode,'rev_')` fails with an Int32 conversion error even though the column is a string — use `objecttypecode eq 'rev_grant'` instead. Verified 2026-08-19: all three rev_ alternate keys report EntityKeyIndexStatus=Active, all 21 option sets and all 51 field permissions match source exactly.  
  <sub>IMP-0083</sub>
- Table auditing SURVIVES a solution import, both first run and re-run: because entity-level IsAuditEnabled is absent from every Entity.xml, the import neither sets nor clears it. So the switch is set ONCE per table per environment and stays set — do not re-do it after each release, and do not expect a release to do it for you. The same reasoning applies to any environment setting solution source omits: absent means untouched, not reset to default. Verified live on all five tables after two consecutive imports on 2026-08-19.  
  <sub>IMP-0086</sub>
- Test data for the flows exists: src/tests/data/scoring-test-data.json (12 cases with expected score, status and income flag derived from the LIVE DEV configuration) plus intake payloads and failure-alert inputs, loaded by provisioning/dataverse/seed-test-data.ps1 and asserted by verify-test-data.ps1. Four things worth knowing before touching it: (1) rev_name is an autonumber on all four tables - never send it; (2) the loader deliberately does NOT upsert on the rev_sourcesubmissionid alternate key, because a keyed PATCH does not fire the row-CREATED trigger the scoring flow listens on, so re-testing means remove-then-seed; (3) teardown finds rows by rev_sourcesubmissionid prefix 'TESTDATA-' and by rev_applicant.rev_lastcontactdate = 1900-01-01, because rev_applicant has no alternate key and its name, email and postcode are all secured columns; (4) `pwsh -File script.ps1 -Case A,B` passes the whole list as ONE string - array binding only happens under `pwsh -Command`, so a [string[]] parameter must split on commas itself.  
  <sub>IMP-0103</sub>
- A flow knows its own run URL: workflow()?['tags']?['environmentName'] is the environment id and workflow()?['name'] is the flow id, so a run deep link needs no environment variable and no hardcoded host. A CHILD flow cannot build the CALLER's link - workflow() there returns the child - so the caller must pass it. Added as text_5 on REV | Ops | Failure Alert and deliberately left OUT of the trigger's required array: a required input would break any caller not yet updated, and the alert is the last thing that should fail.  
  <sub>IMP-0118</sub>
- Teams adaptive cards WORK from this solution and the shape is now verified, not guessed: operationId PostCardToConversation on shared_teams, with poster/location/body-recipient exactly as PostMessageToConversation uses them, and the CARD PASSED AS A JSON STRING in body/messageBody. Action.OpenUrl buttons resolve, including URLs assembled from an environment variable plus a solution-held view id. Card payloads are kept as readable files under docs/development/cards/ and serialised into the definition. The HTML PostMessageToConversation action is retained behind each card with runAfter Failed/TimedOut/Skipped - keep that pattern for the next card until a second one has been seen working.  
  <sub>IMP-0125</sub>
- REV | Scoring | Calculate & Flag is verified V5 in DEV as of 2026-08-20: 12 of 12 cases pass, covering both borderline band edges (30 inclusive, 21 inclusive), the knockout threshold at 20, the override guard leaving a hand-decided row untouched, BOTH withheld-outcome variants (missing wellbeing answer and missing life-satisfaction answer), the three income-flag branches including 'not stated', and the FR-016 pair proving special-category data does not change a score. Reproduce with: remove-test-data.ps1 -Env dev -Force, then seed-test-data.ps1 -Env dev, wait ~30s, then verify-test-data.ps1 -Env dev and require exit 0. Six preconditions have to hold and the loader checks all of them: four flows Activated, a callbackregistration on rev_application whose createdon is NOT older than the last import, and rev_ProcessOwnerUpn holding a value. Keep the environment variables as VALUE ROWS, never definition defaults.  
  <sub>IMP-0126</sub>
- 'Use all available vertical space' on a multi-line text field is auto="true" on the CELL, not on the control and not a rowspan: <cell id="{..}" showlabel="true" locklevel="0" auto="true">. Ground-truthed by reading the reviewer's maker-portal edit back out of DEV with pac org fetch on systemform.formxml, 2026-08-21. Every cell whose control classid is {E0DECE4B-6FC8-4a8f-A065-082708572369} (multi-line text) needs it; there are 20 in this solution and pac solution pack carries all 20 into customizations.xml. When authoring a form cell for an ntext/textarea column, set it at authoring time - the column's Format does not imply it.  
  <sub>IMP-0127</sub>
- An nvarchar column renders as a growing multi-line box when its Format is textarea - <Type>nvarchar</Type> with <Format>textarea</Format>, no type change and NO FORM CHANGE AT ALL. Verified live 2026-08-21: after the reviewer set Text area on rev_setting.rev_description in the maker portal, the form read back out of DEV still carried the single-line control classid {4273EDBD-AC1D-40d3-9FB2-095C621B552D} and no auto attribute, so the renderer follows the COLUMN's format, not the form's control. Note the constraint that forces this route: Dataverse will NOT convert Single line of text to Multiple lines of text, so retyping nvarchar to ntext means deleting and recreating the column (IMP-0017). Also: ensure-schema.ps1 is create-only - it reports EXISTS and skips - so a format change on an existing column happens in the maker portal or by a metadata PATCH, never by running the script.  
  <sub>IMP-0128</sub>
- To read a form out of Dataverse with FetchXML, filter on `formid` (the primary key) — never on `objecttypecode`, which raises System.FormatException/Int32 for any string value in a CONDITION even though it selects fine, and never on `systemformid`, which is not an attribute name. Verified 2026-08-21 on rev_application's main form: `pac env fetch` with a formid condition returns 77KB of formxml. This CORRECTS the workaround recorded in IMP-0083 — get the form id from the source file name under Entities/<table>/FormXml/main/.  
  <sub>IMP-0135</sub>
- Delegating to another agent means dispatching it as a Claude Code subagent via the Task tool (`subagent_type: <agent-name>`), which loads `.claude/agents/<agent-name>.md` — generated from config/models.yml by `scripts/generate-subagents.py` — whose frontmatter pins the model. Continuing to talk to an agent inside the current conversation instead of dispatching it runs that work on whatever model the conversation already is, regardless of its declared tier. A pinned subagent cannot escalate itself mid-invocation either: the dispatcher must check escalate_to_strategic_when/de_escalate_to_mechanical_when in config/models.yml before dispatching and pass an explicit model: override when a condition is met. See agents/WORKFLOW.md -> 'Session Boundaries'.  
  <sub>IMP-0143</sub>
- When a dispatched (background) agent's live provisioning write is refused by the harness classifier, try the identical command directly in the lead-agent's own foreground Bash tool call before falling back to a REVIEWER ACTION REQUIRED block - it may succeed where the same call from a background dispatch did not. This resolved A-TR-2 (REV Trustee role creation) in one attempt after identity-agent's background dispatch (IMP-0170) was refused for the exact same command against the exact same environment. Reserve the reviewer's-own-shell fallback for when the foreground attempt is ALSO refused.  
  <sub>IMP-0173</sub>


## Unrouted — no section assigned

> These findings' `class_instance_of` values are missing from the routing table in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches the agent at the moment it applies.

*26 lessons from 26 findings.*

- When a contract incorporates a document by reference, check the VERSION of the file supplied against the version the contract names - presence is not sufficiency. The General Terms in this repo are v1.2 (June 2026) where the signed agreement incorporates v1.3 (August 2026).  
  <sub>IMP-0071</sub>
- Acceptance is not only an explicit act. Build Terms B5: a phase is also accepted by SILENCE (ten business days after submission with no specific written objection) and by USE (putting a deliverable into live operational use). Both start a 60-day warranty window with nobody recording anything, so track submission dates and live-use dates, not just written acceptances.  
  <sub>IMP-0072</sub>
- An invoiced total is not a scope credit. Before subtracting invoiced hours from delivered WBS scope, establish how many of them bought work the WBS itemises: 20 of this engagement's first 64 did not, and crediting all 64 under-bills the delivered build by that much. scripts/deliverable-hours.py --outside-wbs carries the distinction; the ledger itself still records only the total.  
  <sub>IMP-0098</sub>
- A test written from the same assumption as the code does not verify it, it locks it in - and it will block the fix. When a test names a platform contract ('resolves by alternate key', 'accepts this shape'), it may only assert what has been observed working against the platform, and its comment should say when and how that was observed. If a passing test has to be rewritten to let a WORKING implementation go green, the test was the defect. Also, when adding tests here: declare shared lists in BeforeAll, never in a Describe body - a Describe body runs at DISCOVERY and its variables are gone by the time an It body runs, so loops over them iterate nothing and pass vacuously (this bit me on the replacement tests, and .Count silently became 0).  
  <sub>IMP-0111</sub>
- rev_setting is designed to be edited in the environment without a deployment, so the settings files WILL drift from it and seed-settings.ps1 will silently revert a real decision. Before trusting any expected score, read the live rows and diff them against provisioning/deploymentSettings/<env>-*.json. When they differ, the AUDIT TRAIL on rev_setting settles who changed what and when: audits?$filter=_objectid_value eq <id> gives oldValue and newValue. And note what this particular decision cost: with "Not sure" worth 0 the map holds no fractional value, so the half-point rounding rule is now unreachable, the reachable score floor drops from 5 to 0, and the flow no longer reproduces the 25 published hand-scores it was once validated against.  
  <sub>IMP-0123</sub>
- CI has never run on this project. .github/workflows/ci.yml fires only on `push` to `feature/**`, and no feature/** branch has ever existed — work has lived on main, project-management and self-learning. Every gate described as 'wired into CI' has only ever executed when an agent chose to run it by hand, which is why four gates are red on this tree today with nothing reporting them. Before trusting any constraint whose Verify By names CI, confirm the workflow's trigger matches a branch that exists: `git branch -a` against the `on:` filter. This is the third arrival of 'the workflow ran zero jobs' (IMP-0074 invalid file, IMP-0080 single point of silence, this one an unmatchable filter) and the first two were both fixed at instance altitude.  
  <sub>IMP-0165</sub>
- A HARD constraint's Verify By naming 'wired as a build gate' is not satisfied by the script existing and passing --selftest - grep the actual steps: block of the build config the review claims to have changed, every time an improvement review is marked APPLIED for a build-gate item.  
  <sub>IMP-0174</sub>
- Walk the contract chain in BOTH directions. A task claiming completion with no artefact is an unevidenced claim; an artefact no task accounts for is unquoted work, and only the reverse direction finds it. rev_grantadministration shipped with no WBS task naming it.  
  <sub>IMP-0066</sub>
- When a schedule computes headroom per phase, check whether the same capacity is being counted for more than one phase - it must be cumulative, because finishing phase N requires finishing 0..N-1 too. And distinguish 'late because nobody started it' from 'late because it is blocked on the client': the first needs a queue, the second needs a phone call.  
  <sub>IMP-0069</sub>
- reconstruct-worklog.py's billable column is a keyword verdict on the whole cluster, not a classification: one improvement finding in a six-hour delivery session marks the entire session non-billable. Read work_type against the evidence kinds before accepting the column, and check every proposed session's phase against WL-0001's coverage by hand - evidence-ref matching cannot detect a re-bill against the historic seed.  
  <sub>IMP-0094</sub>
- flowrun / flowsession / processsession are all EMPTY in this environment even while cloud flows are running - do not read 0 rows there as 'no flow has run'. More generally: never use an empty table as evidence of absence until you have seen that table produce a row for a case you know happened. Establish the positive control first, or say plainly that you cannot tell the two apart.  
  <sub>IMP-0110</sub>
- Do not put an example URL in ANY file under src/solutions/ - not in a component description, not in a README, not in a comment explaining why you cannot. The C-TECH-047 gate greps the whole tree case-insensitively for the organisation host and SharePoint host patterns, and an illustration is indistinguishable from a real value. Say where to copy the value FROM instead of showing its shape. This is a gate working, not a gate to route around.  
  <sub>IMP-0119</sub>
- When you move a threshold out of a runner and into its own gate, change what the runner PRINTS in the same edit. src/tests/Invoke-Tests.ps1 should say 'coverage measured, not enforced here — see the coverage-threshold build step' when -CoverageThreshold is 0, and should not name C-TECH-014 at all. A tool that cites a constraint it does not enforce is worse than one that says nothing.  
  <sub>IMP-0134</sub>
- Do not assume an import deactivates every flow, and do not assume it deactivates only some. CAPTURE the statecodes before and diff them after - it is one FetchXML query on workflow with category=5. On 2026-08-21 two of four went to Draft and the two that did were the two whose definition JSON the import replaced; the other two kept statecode 1 with a fresh modifiedon. Whatever the rule turns out to be, the post-deploy re-activation list is derived from the diff, never from the count.  
  <sub>IMP-0136</sub>
- When an ordering test needs a named action, assert the edge on the action that CONSUMES the ordering (the loop, the write), never on a declaration or a Compose that merely sits first. A declaration's position is a platform constraint, not a design decision, so pinning a test to it makes the test wrong the moment the platform is obeyed.  
  <sub>IMP-0138</sub>
- 'Settings file resolved' is not 'settings resolved'. verify-pipeline-config.py check 10 proves the <env>-settings.json a step needs EXISTS; it never opens it, so a file full of {{PLACEHOLDER}} tokens counts as resolved and the preflight prints PASS over a pipeline whose first post-deploy step throws on line 60. Get-Setting's Assert-NoPlaceholder only fires at run time and only on the ONE key being read, so fixing a placeholder reveals the next one rather than the set - never read a successful fix as evidence the file is ready. Count them statically: walk the JSON, skip keys starting with _ (documentation), and report every {{...}} left in a value position.  
  <sub>IMP-0147</sub>
- In scripts/verify-pipeline-config.py, powershell_params() cannot see the last parameter of a SINGLE-LINE param() block, because the closing parenthesis it needs as a terminator is outside the slice it searches. The failure direction is a false FAIL in a HARD gate - it blocks a deploy step that is actually correct - which is the expensive direction the function's own comment says it avoids. Fix is one character (end + 1) plus a fixture with a single-line param block. Until then, declare provisioning script parameters multi-line, as every existing one does.  
  <sub>IMP-0149</sub>
- Before trusting a pipeline.yml step's prose description of how many rows/components it seeds, count the actual settings array (python3 -c "import json; print(len(json.load(open(path))['dataverse']['settingRows']))") - the description is hand-typed and does not update itself when rows are added elsewhere. Here the file held 14, the comment said 11, and both the comment and a handoff built on it repeated the stale number.  
  <sub>IMP-0150</sub>
- A reviewer's 'I re-ran it and it succeeded' after a Resubmit only proves the flow's action logic completes (here: that it can now read the just-seeded rev_setting rows without erroring) - it proves nothing about whether IMP-0148's live Dataverse trigger fires on a genuinely new row. Before closing a dead-trigger finding, insist on a fresh row created after the fix and an unprompted score appearing, not a resubmitted run.  
  <sub>IMP-0151</sub>
- src/tests/provisioning/ScriptContract.Tests.ps1's Dataverse-write check (line 236) matches an AST argument's raw Extent.Text against '^GET$', so -Method 'GET' (quoted) fails where -Method GET (bareword) passes even though both send an identical, safe read-only request - a false FAIL, not a caught defect. provisioning/dataverse/verify-environment-access.ps1 is the one script in this repo written with the quoted form, and it is also missing from provisioning/README.md's script inventory (a second, independent contract gap in the same file). Neither is fixed here - out of this dispatch's WBS scope - but both are one-line fixes: requote line 105 to the bareword convention (or loosen the test's regex to accept an optionally-quoted literal), and add the script's line to the README inventory table.  
  <sub>IMP-0156</sub>

> **6 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0158, IMP-0160, IMP-0163, IMP-0171, IMP-0176, IMP-0177. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
