# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (348 entries, 347 distinct lessons)
Generated: 2026-08-26

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

**`Renders in` is where this class's lessons actually appear below** — not where the routing table says they should. A lesson whose finding carries `capability: true` renders under `Capabilities` whatever its class, so a class can sit in this table and have none of its lessons in the section you expect. Reading the class name alone and inferring a section is how one review predicted a digest delta of 31→26 and measured 31→30 (`IMP-0198`).

| Count | Class | Renders in | Findings |
|---|---|---|---|
| **x42** | `platform-contract-guessed-not-groundtruthed` | `before-authoring` ×35, `Capabilities` ×7 | IMP-0001, IMP-0006, IMP-0011, IMP-0017, IMP-0037, IMP-0044, IMP-0045, IMP-0068, IMP-0074, IMP-0087, IMP-0091, IMP-0108, IMP-0112, IMP-0116, IMP-0124, IMP-0128, IMP-0135, IMP-0137, IMP-0153, IMP-0161, IMP-0188, IMP-0189, IMP-0190, IMP-0199, IMP-0202, IMP-0208, IMP-0216, IMP-0217, IMP-0226, IMP-0249, IMP-0254, IMP-0255, IMP-0267, IMP-0272, IMP-0273, IMP-0276, IMP-0277, IMP-0303, IMP-0304, IMP-0329, IMP-0345, IMP-0349 |
| **x33** | `gate-cannot-fail` | `before-build` ×32, `Capabilities` | IMP-0002, IMP-0004, IMP-0007, IMP-0020, IMP-0024, IMP-0025, IMP-0035, IMP-0036, IMP-0041, IMP-0042, IMP-0043, IMP-0046, IMP-0050, IMP-0089, IMP-0115, IMP-0117, IMP-0129, IMP-0132, IMP-0141, IMP-0152, IMP-0157, IMP-0159, IMP-0167, IMP-0180, IMP-0197, IMP-0205, IMP-0230, IMP-0233, IMP-0241, IMP-0242, IMP-0281, IMP-0282, IMP-0319 |
| **x23** | `learning-substrate-destroyed` | `before-success` ×17, `Capabilities` ×6 | IMP-0016, IMP-0022, IMP-0023, IMP-0033, IMP-0038, IMP-0049, IMP-0055, IMP-0080, IMP-0103, IMP-0118, IMP-0125, IMP-0126, IMP-0154, IMP-0169, IMP-0181, IMP-0204, IMP-0213, IMP-0250, IMP-0251, IMP-0285, IMP-0301, IMP-0309, IMP-0333 |
| **x17** | `hand-maintained-count-drifts-from-source` (also logged as `test-coupled-to-absolute-counts`) | `Unrouted` ×10, `before-build` ×7 | IMP-0005, IMP-0039, IMP-0120, IMP-0150, IMP-0155, IMP-0160, IMP-0176, IMP-0198, IMP-0211, IMP-0212, IMP-0235, IMP-0260, IMP-0262, IMP-0263, IMP-0315, IMP-0330, IMP-0351 |
| **x16** | `platform-fact-groundtruthed` | `Capabilities` ×15, `before-authoring` | IMP-0185, IMP-0193, IMP-0194, IMP-0195, IMP-0206, IMP-0209, IMP-0210, IMP-0221, IMP-0223, IMP-0256, IMP-0257, IMP-0261, IMP-0295, IMP-0306, IMP-0316, IMP-0317 |
| **x15** | `declared-policy-not-mechanically-enforced` | `Unrouted` ×14, `Capabilities` | IMP-0143, IMP-0165, IMP-0174, IMP-0184, IMP-0231, IMP-0265, IMP-0275, IMP-0286, IMP-0299, IMP-0307, IMP-0312, IMP-0318, IMP-0325, IMP-0335, IMP-0348 |
| **x14** | `gate-reassures-wrongly` | `Unrouted` ×14 | IMP-0069, IMP-0094, IMP-0110, IMP-0134, IMP-0147, IMP-0149, IMP-0151, IMP-0156, IMP-0207, IMP-0225, IMP-0229, IMP-0246, IMP-0283, IMP-0343 |
| **x14** | `no-assertion-on-shipped-content` | `before-success` ×13, `Capabilities` | IMP-0008, IMP-0015, IMP-0047, IMP-0052, IMP-0060, IMP-0085, IMP-0090, IMP-0127, IMP-0131, IMP-0139, IMP-0320, IMP-0324, IMP-0346, IMP-0350 |
| **x13** | `exit-zero-does-not-mean-created` | `before-deploy` ×13 | IMP-0013, IMP-0018, IMP-0019, IMP-0030, IMP-0065, IMP-0078, IMP-0082, IMP-0101, IMP-0104, IMP-0106, IMP-0114, IMP-0122, IMP-0148 |
| **x11** | `harness-blocks-destructive-call` | `operating` ×8, `Capabilities` ×3 | IMP-0021, IMP-0040, IMP-0084, IMP-0133, IMP-0170, IMP-0220, IMP-0245, IMP-0252, IMP-0287, IMP-0313, IMP-0314 |
| **x10** | `two-invocation-paths-disagree` | `before-build` ×10 | IMP-0026, IMP-0051, IMP-0053, IMP-0077, IMP-0093, IMP-0107, IMP-0144, IMP-0168, IMP-0232, IMP-0259 |
| **x10** | `v3-does-not-imply-v4` | `before-deploy` ×9, `Capabilities` | IMP-0012, IMP-0088, IMP-0100, IMP-0113, IMP-0121, IMP-0187, IMP-0191, IMP-0192, IMP-0224, IMP-0227 |
| **x8** | `output-shape-defeats-the-reader` | `before-extending` ×7, `Capabilities` | IMP-0059, IMP-0070, IMP-0095, IMP-0102, IMP-0109, IMP-0130, IMP-0142, IMP-0334 |
| **x8** | `platform-state-divergence` | `Unrouted` ×8 | IMP-0123, IMP-0136, IMP-0171, IMP-0178, IMP-0218, IMP-0228, IMP-0270, IMP-0271 |
| **x7** | `approved-document-internally-inconsistent` | `Unrouted` ×7 | IMP-0158, IMP-0302, IMP-0331, IMP-0332, IMP-0340, IMP-0344, IMP-0347 |
| **x6** | `test-assumed-name-is-solution-unique` | `Unrouted` ×6 | IMP-0234, IMP-0236, IMP-0237, IMP-0240, IMP-0247, IMP-0269 |
| **x5** | `agent-instructions-describe-a-topology-that-changed` | `before-running-elsewhere` ×5 | IMP-0056, IMP-0092, IMP-0162, IMP-0183, IMP-0222 |
| **x5** | `config-placeholder-known-but-not-fixed` | `before-running-elsewhere` ×5 | IMP-0145, IMP-0166, IMP-0175, IMP-0243, IMP-0244 |
| **x5** | `finding-diagnosis-unverified` | `Unrouted` ×5 | IMP-0258, IMP-0266, IMP-0298, IMP-0308, IMP-0322 |
| **x5** | `gate-fires-on-nothing` | `before-build` ×5 | IMP-0057, IMP-0164, IMP-0196, IMP-0248, IMP-0328 |
| **x4** | `baseline-restated-not-cited` | `before-commercial` ×4 | IMP-0029, IMP-0063, IMP-0064, IMP-0096 |
| **x4** | `evidence-rule-satisfied-by-a-forward-reference` | `before-commercial` ×4 | IMP-0067, IMP-0097, IMP-0099, IMP-0140 |
| **x3** | `credential-not-on-the-machine-that-needs-it` | `before-running-elsewhere` ×2, `Capabilities` | IMP-0048, IMP-0061, IMP-0105 |
| **x3** | `identifier-namespace-collision-across-documents` | `Unrouted` ×3 | IMP-0327, IMP-0336, IMP-0339 |
| **x3** | `requirement-names-data-the-solution-cannot-supply` | `Unrouted` ×3 | IMP-0293, IMP-0296, IMP-0326 |
| **x3** | `untriaged-tool-warning` | `Unrouted` ×3 | IMP-0177, IMP-0214, IMP-0323 |
| **x2** | `change-order-sizing-without-precedent` | `Capabilities` ×2 | IMP-0278, IMP-0288 |
| **x2** | `declared-knowledge-source-is-empty` | `Capabilities`, `before-extending` | IMP-0034, IMP-0058 |
| **x2** | `dispatched-agent-stalls-silently` | `Capabilities`, `Unrouted` | IMP-0291, IMP-0300 |
| **x2** | `incorporated-document-version-mismatch` | `Unrouted` ×2 | IMP-0071, IMP-0297 |
| **x2** | `repo-path-contains-spaces` | `operating` ×2 | IMP-0010, IMP-0079 |
| **x2** | `tad-narrative-omits-an-already-existing-column` | `Unrouted` ×2 | IMP-0337, IMP-0338 |
| **x2** | `test-asserts-the-defect` | `Unrouted` ×2 | IMP-0111, IMP-0138 |
| **x2** | `wrong-artefact-cited-as-evidence` | `Unrouted` ×2 | IMP-0305, IMP-0341 |

> **Two class names describing one property are COUNTED as one row here.** `test-coupled-to-absolute-counts` → `hand-maintained-count-drifts-from-source`. The alias is in this table only: each lesson still renders in its own section below, and the two halves keep their own gates, because a test fixture and a figure in a document are checked by different tools. The count is merged because the altitude rule fires on the *second* instance of a class — and a property recorded under two names produces a weaker signal than its true instance count ever should (`IMP-0330`).

> **A class named in two sections renders only in the last one.** `repo-path-contains-spaces` → `before-build`, `operating` (renders in `operating`). This is a silent precedence in the routing table, not a decision anything records — fix it by naming the class once, in the section where the lesson actually applies.


## Before you execute a build config

*55 lessons from 55 findings.*

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
- FIFTH instance of this class (after IMP-0005, IMP-0039, IMP-0120, IMP-0155) and the second specifically inside DeploymentSettings.Tests.ps1 (IMP-0155 already named this same file's option-set/role/relationship counts as stale). Adding a table to dataverse.auditing.auditedTables breaks this test every time; per skills/how-to-promote-a-finding.md the fix is to derive the expected count and table list from src/solutions/RevitaliseGrantAutomation/Entities/ (the way scripts/verify-audited-tables.py already does) rather than hand-typing a fourth/fifth/sixth number.  
  <sub>IMP-0212</sub>
- A compound deliverable ('X + access test') needs its evidence rule split so the human-verification half is tracked separately from the buildable half, and left permanently unsatisfiable by repository evidence alone -- report it as derived_status=partial (or a new manual_verification_required state) until a dated V4 confirmation exists, never as complete. This is the third time 6.5 specifically has produced a false-complete reading (after the original 8.2/6.5 forward-reference pair, IMP-0067); per skills/how-to-promote-a-finding.md two instances of one class demand generalisation, and this is the second recorded instance for the SAME task id, which is stronger evidence still.  
  <sub>IMP-0230</sub>
- Every reader of logs/worklog.jsonl must call scripts/lib/worklog.py, never re-parse the file itself -- IMP-0093 named three scripts that needed this and fixed them, but a fourth script (collect-project-status.py, the one PM STATUS answers are required to render from without adding any figure of their own) reimplemented the pre-fix arithmetic and reproduces the identical 84-vs-64 over-count today. Grep for every 'WORKLOG.read_text' / raw json.loads(line) pattern against logs/worklog.jsonl, not just the three scripts IMP-0093 already named.  
  <sub>IMP-0232</sub>
- Before believing a fix to a provisioning script's payload-building function is complete, check whether the step that CALLS it is create-only. ensure-schema.ps1's relationship step reports EXISTS and skips, so a corrected relationship/lookup body never reaches an environment where the relationship already exists — the fix lands in a fresh PRD and never in DEV, which is the harder direction to notice because DEV is where testing happens. A create-only step needs a paired reconcile step for every property that can be corrected in source later (step 3b is that step for lookup IsSecured, one-directional by design: unsecured to secured only, never the reverse, because removing a column-level control is a human decision). And when testing an idempotent script, the state that matters is not 'everything absent' or 'everything present' but PRESENT-BUT-WRONG — the only one of the three that a partial live run actually leaves behind.  
  <sub>IMP-0259</sub>
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

> **35 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0036, IMP-0039, IMP-0041, IMP-0046, IMP-0050, IMP-0051, IMP-0053, IMP-0057, IMP-0077, IMP-0107, IMP-0115, IMP-0117, IMP-0120, IMP-0129, IMP-0141, IMP-0144, IMP-0152, IMP-0157, IMP-0159, IMP-0164, IMP-0167, IMP-0168, IMP-0180, IMP-0196, IMP-0205, IMP-0233, IMP-0235, IMP-0241, IMP-0242, IMP-0248, IMP-0281, IMP-0282, IMP-0315, IMP-0319, IMP-0328. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you hand-author a platform artefact

*38 lessons from 38 findings.*

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
- pac code push fails HTTP 403 CodeAppOperationNotAllowedInEnvironment unless the target environment has the 'Power Apps code apps' product feature enabled first (Power Platform admin center -> Environments -> <env> -> Settings -> Product -> Features -> 'Power Apps code apps' toggle -> Save). Admin-center UI only -- no pac CLI verb, and it is not a Dataverse organization-entity attribute. A human System/Environment Administrator must enable it once per environment before the first code app push into that environment; add it to environment_prerequisites for every environment a code app ships to (DEV now, TST/ACC and PRD when EX-003 permits promotion beyond DEV).  
  <sub>IMP-0182</sub>
- Before debugging a Power Platform app's Dataverse/connector/role errors on ANY machine, first confirm which Entra identity the browser is actually signed in as (open https://myaccount.microsoft.com in a plain tab, no app link first) - a device enrolled in Microsoft's Company Portal / Enterprise SSO extension (check `pluginkit -m | grep -i microsoft` and `profiles status -type enrollment`) can silently authenticate every Microsoft sign-in, INCLUDING INCOGNITO WINDOWS, as whatever account the extension last cached, with no prompt and no browser-level fix. On this Mac that cached identity is svc_grantapplications (this project's own provisioning service account), so any interactive Power Platform testing done here needs that fixed FIRST (Company Portal.app account, or a different, non-SSO-bound device) before any app/connection/role symptom on this machine can be trusted as real.  
  <sub>IMP-0189</sub>
- Before running the V4 access test's positive control ('read as the process owner/service identity, confirm populated'), confirm live that at least one identity is actually a member of REV_TrusteeRestricted (fieldsecurityprofiles({id})/systemuserprofiles for DEV's direct-assignment model, or teamprofiles for TST/ACC/PRD's group-team model) -- in DEV as of 2026-08-23 it is zero on both axes, so the comparison read will return null for everyone and prove nothing until one identity (e.g. svc_grantapplications, or the named process owner) is added as a direct member first.  
  <sub>IMP-0221</sub>
- A Dataverse table's primary name attribute can never carry IsSecured=1 - creating it fails with 0x8004f501 "The field '<name>' is not securable." Never secure a primary name column, even when a source document's literal wording states a blanket rule like "every column" with no exception carved out; ground-truth against a real create call before treating that wording as settled.  
  <sub>IMP-0249</sub>
- A metadata PATCH against Dataverse's abstract AttributeMetadata entity set requires the concrete derived-type cast segment IN THE URI, not only in the request body's @odata.type -- the same polymorphism trap already known on the GET/read side (a 404 under the wrong cast) also applies to writes, as an outright method-not-supported rejection of the base, uncast collection. Before modeling a new metadata PATCH on an existing one, check whether the target entity set is polymorphic; EntityDefinitions and Attributes are not interchangeable examples of the same shape.  
  <sub>IMP-0272</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0273`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- When a metadata PATCH against a Dataverse Web API collection is rejected outright ('does not support http method X'), check Microsoft's own 'Update a column' / 'Update table definitions' pages before assuming a missing cast segment: entity and attribute metadata updates are documented as PUT-only, with the full current object as the body, and the cast segment (needed on the GET used to fetch that object) does NOT carry over to the write URI. A verb rejection and a wrong-cast 404 read alike as 'the naive call failed' but have different fixes.  
  <sub>IMP-0273</sub>
- A Dataverse Web API metadata write (EntityDefinitions and its derived Attributes types alike) never accepts PATCH -- entity and attribute metadata updates are PUT-only, and PUT requires the complete current object, never a partial body. Before writing any future entity-metadata update, follow the corrected GET-full-object -> mutate -> PUT-whole-object pattern already fixed in ensure-schema.ps1 step 3b (IMP-0272/IMP-0273), never the organisation-record PATCH pattern elsewhere in the same script -- a data record and a metadata endpoint look similar in this codebase but take opposite verbs.  
  <sub>IMP-0276</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0277`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>

> **18 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0037, IMP-0087, IMP-0091, IMP-0161, IMP-0188, IMP-0190, IMP-0202, IMP-0217, IMP-0226, IMP-0254, IMP-0255, IMP-0267, IMP-0277, IMP-0303, IMP-0304, IMP-0329, IMP-0345, IMP-0349. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you declare a deploy or an import successful

*23 lessons from 23 findings.*

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
- A Code App reported live by `pac code list` and reachable in the maker portal (V3) can still fail every Dataverse connector call for a real signed-in user with "Invalid organization URL 'null' provided" - identical across unrelated tables, which rules out a security-role cause outright (that would 403 per-entity on that entity's own privileges, not repeat verbatim). Before re-suspecting Entra security groups, Environment Teams or the REV Trustee role on this specific error, check and if necessary recreate the app's own 'Microsoft Dataverse' CONNECTION in the maker portal (Connections) - it can predate power.config.json's appId resolving to a real value.  
  <sub>IMP-0187</sub>
- When a Code App's Dataverse connector fails with 'Invalid organization URL null provided' and account identity, role grant (including team-inherited roles via teamroles, not just systemuserroles), and per-user connection existence all check out live, stop treating it as a local configuration problem - it is very likely a Power Apps Code Apps (Preview) host/SDK defect outside this project's control. Escalate to Microsoft support (Power Platform admin center -> Help + support), quoting the original error's OperationId and ClientRequestId values for correlation, rather than continuing to guess at further local fixes. Two cheap things worth trying first, in case they force a fresh binding: (a) re-run `pac code add-data-source` for the Dataverse source to regenerate the connector binding, (b) test whether the SAME account can call the SAME shared_commondataserviceforapps connector successfully from a different app type (e.g. a throwaway Canvas App) in this environment, to isolate whether the defect is Code-Apps-specific or account/connector-wide.  
  <sub>IMP-0191</sub>
- `pac code add-data-source -a <apiId>` takes the SHORT connector id (e.g. `shared_commondataserviceforapps`), never the full '/providers/Microsoft.PowerApps/apis/<id>' path shown by `pac connection list`'s API Id column or power.config.json's connectionReferences.<guid>.id - passing the full path 404s with a visibly malformed doubled-slash URL (.../connectors//providers/...). Also: for the REV Trustee Review Portal specifically, re-running this command is CONFIRMED a no-op against the current live connection (4fc93a683f8945699cbb364403b02296) - do not re-try it as a remedy for the org-url-null error again without new information; the next step is a Microsoft support ticket, not another local regeneration attempt.  
  <sub>IMP-0192</sub>
- A `pa app add data-source --table <t> -u <org-url>` success, a clean `tsc`/`eslint`, and a `git diff` showing new generated files are evidence about the PER-TABLE typed-service data source only. Before marking a 'connector fails to resolve org URL' finding APPLIED for an app, confirm which data source key the app's actual call sites use (`getClient(dataSourcesInfo)`'s argument, and which top-level key in `dataSourcesInfo.ts` carries non-empty `apis` for the operations the app calls — `ListRecords`/`GetItem`/`UpdateOnlyRecord` live only under the generic connector key here, never under a per-table key) and re-run the original V4 reproduction step against THAT key specifically. A hand-rolled generic-connector client and its app's own typed per-table services can sit in the same `dataSourcesInfo.ts` with one fixed and the other still broken, and nothing short of re-opening the app as a real user will show which is which.  
  <sub>IMP-0224</sub>
- Solution import RELABELS matching option values but does NOT delete values the new source omits. Orphaned values survive every subsequent import. Compare live option-set members against source.  
  <sub>IMP-0019</sub>
- Invoiced hours are not completed hours. Never compute a variance against an estimate for a phase still in progress: the phase looks efficient right up until the remaining work is booked. Before comparing actuals to an estimate, establish that the phase is CLOSED - client testing and feedback included, since those are the activities most likely to be outstanding when the build looks done.  
  <sub>IMP-0065</sub>
- A manifest's source_commit only describes the artifact if the working tree was clean when the pack ran. Record `git status --porcelain` alongside the sha and state the count, because a sha copied from HEAD over a dirty tree names source the zip does not contain — build #7's manifest named a commit predating the whole rev_grant table it had just packaged.  
  <sub>IMP-0078</sub>

> **3 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0088, IMP-0100, IMP-0113. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Before you report SUCCESS at all

*30 lessons from 30 findings.*

- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- ensure-schema.ps1 derives nothing from disk: Get-RevEntityLogicalNames is a hand-kept list and the relationship detail path was hardcoded to one file. An entity absent from that list is an entity C-TECH-050's prerequisite step will NOT create, silently - so adding a table means editing that list, and a gate should compare it against Entities/ on disk.  
  <sub>IMP-0038</sub>
- When a fix makes one config resolve a value per run, grep for every OTHER file that names that value. IMP-0016 fixed build.yml and left pipeline.yml pointing at a directory that stopped existing the next day. Also: `upload-artifact` roots the archive at the least common ancestor of the paths it matched — name the PARENT directory, not a `**` glob, or the directory you care about is stripped from the archive.  
  <sub>IMP-0049</sub>
- Adding a Dataverse table to a model-driven app is FOUR changes, not two and not three: (1) the entity, (2) a SubArea in AppModuleSiteMaps/, (3) an <AppModuleComponent type="1" schemaName=".."/> in AppModules/<app>/AppModule.xml, and (4) the audit switch in the environment. Miss (3) and the table appears in the designer's EDIT mode and is absent in PLAY mode, surviving a hard refresh — which reads exactly like a platform caching bug and is not one. Diff AppModule.xml's component list against the Entities/ folders on disk before believing any reachability gate.  
  <sub>IMP-0090</sub>
- Fixing the script a finding describes does not close the finding's own log entry -- IMP-0277 corrected ensure-auditing.ps1 but left IMP-0276 (the finding it corrects) sitting NEW/unread with no deferred_reason, which is independently a C-TECH-061 HARD violation that fails any build reaching the unit-tests step. Before dispatching a full build, run `python3 scripts/verify-improvement-log.py --check` standalone first -- it is the exact assertion buried 39-41 steps into the sequence, needs no npm/tsc/vitest/pester setup, and turns a several-minute wasted build attempt into a one-second pre-check. Separately: when a build's config file, constraints file or improvement log changes mid-run (two sessions can be live on this synced path at once, IMP-0080/IMP-0213), re-hash the build config, re-run preflight against the CURRENT file, run any newly-inserted step standalone, and re-run the full sequence end to end rather than trusting a preflight or a partial log that described a different file -- do not patch just the one step that happened to fail.  
  <sub>IMP-0285</sub>
- REVIntakeWordPressToDataverse and REVScoringDailySummary each read personal-data rows (rev_application/rev_applicant) without Secure Outputs — a real, already-shipped exposure, not a hypothetical one. Fixing it is OUT OF THIS DISPATCH'S WBS SCOPE (6.1/6.3/6.5/6.9) — it touches Automation #1 and #2, not the Trustee Portal — and is flagged here rather than silently fixed, per C-COM-002 (work enters by WBS task id or a change-order decision, never built first and reconciled later). The new gate (scripts/verify-flow-definition-language.py check 5) is therefore NOT wired into config/revitalise-grant-automation-build.yml as a HARD step yet, because turning it on would fail the build over these two pre-existing flows this feature did not touch — verified narrowly against only the new flow instead (which passes).  
  <sub>IMP-0320</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0322`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
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

> **10 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0181, IMP-0204, IMP-0250, IMP-0251, IMP-0301, IMP-0309, IMP-0324, IMP-0333, IMP-0346, IMP-0350. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Operating constraints of this environment

*11 lessons from 11 findings.*

- THIRD instance. A gate keyword authorises an operation inside this system; it does not grant the session permission to perform it. Live Dataverse WRITES (metadata PATCH, DeleteOptionValue, organisation settings) are refused by the harness even under APPROVE TENANT, while reads are not. Establish the permission BEFORE reporting that a gate keyword will produce a live change: either the reviewer adds a Bash permission rule, or the operation is handed to them with the exact call to make. Never leave the reviewer believing a keyword was sufficient.  
  <sub>IMP-0084</sub>
- Fifth instance. Any agent that can be dispatched to run a live `provisioning/**/*.ps1` write - not only pipeline-agent - needs the same 'Reviewer-Executed Operations' behaviour: attempt the call, and on a classifier refusal emit the exact command plus its pre/post verification query rather than reporting the task as merely blocked. Currently this behaviour lives only in agents/pipeline-agent.md; development-agent.md's sub-agent table (identity-agent, automation-agent, config-agent, m365-agent - every one that can write to a live environment) has no equivalent pointer.  
  <sub>IMP-0170</sub>
- Under Auto Mode, the classifier auto-denies a cert/keychain-touching pwsh command outright with no permission prompt -- this may hold even in a session that would otherwise count as the reviewer's own 'foreground' one per IMP-0173, because auto mode itself removes the human from the approval loop. Before assuming a foreground retry will succeed, check whether Auto Mode is active in that session too; if so, the retry needs a normal (non-auto) interactive session where a human can see and approve the prompt. Also: ensure-schema.ps1-class operations (entity/attribute/role/field-security-profile metadata creation, C-TECH-050) have no native pac CLI verb at all in pac 2.4.1 -- unlike role assignment (pac admin assign-user, IMP-0220) -- so step 3a's fallback never has a target for this operation class and every occurrence goes straight to REVIEWER ACTION REQUIRED.  
  <sub>IMP-0245</sub>
- Under Auto Mode, the classifier can refuse an Agent-tool dispatch outright based on the prompt describing a live write -- not only the pwsh command a dispatched agent later tries to run. This is a NEW, earlier refusal point than the seven prior instances of this class. Before re-dispatching any agent whose job is to attempt a known-blocked live write, expect the dispatch call itself may be refused, and have the REVIEWER ACTION REQUIRED message (the exact command for the human to run themselves) ready as the immediate next step rather than assuming a subagent will get a chance to try.  
  <sub>IMP-0252</sub>
- Under Auto Mode, a cert/keychain-touching pwsh command is refused by the classifier regardless of whether every Dataverse call inside it is a GET -- IMP-0084's 'reads run freely' finding holds only for a non-Auto-Mode session. An agent dispatched under Auto Mode has ZERO live-Dataverse reach, not just no-write reach, and must say so plainly rather than assuming the read-only method that worked in a previous test round will work again.  
  <sub>IMP-0287</sub>
- This repo's path contains spaces. `pac solution check --outputDirectory` silently writes nothing; read the result from stdout instead.  
  <sub>IMP-0010</sub>
- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>
- Third confirmation: `pac solution check --outputDirectory` writes NOTHING on this repo's path and still says 'Finished downloading 1 files'. Tee the command's stdout into the artifact and assert the target directory is non-empty — otherwise the only evidence for a HARD gate lives in a console log that CI throws away.  
  <sub>IMP-0079</sub>
- Fourth instance, and the first since the protocol was written — the protocol worked, so do not escalate it further. Two additions from this one: (1) READS can be refused too, when the shell command carries a $(...) substitution that looks like injection; reach for the dedicated Read tool rather than rephrasing the shell. (2) Capture the pre-import state BEFORE attempting the write, not after the refusal: the environment-variable values, the flow statecodes and the callbackregistration createdon are what the reviewer needs to compare against afterwards, and they are cheap reads that are never refused.  
  <sub>IMP-0133</sub>
- When handing a human (not a subagent) a command that depends on environment variables, state the export syntax for THEIR shell explicitly rather than reusing whatever syntax the surrounding documentation happens to use. This project's own knowledge file only ever shows these two values inside a PowerShell object literal, which reads as "this is a pwsh session" and is not -- the actual usage pattern everywhere else is export in bash/zsh, then invoke pwsh -File as a subprocess (env vars inherit into the child process normally). Before generating a REVIEWER ACTION REQUIRED command block or any copy-paste instruction, confirm or state the target shell rather than assuming one from a script's own file extension.  
  <sub>IMP-0253</sub>
- When an Agent-tool dispatch itself is refused (not a call the dispatched agent later tries), do not retry the identical dispatch. If the dispatching agent already has its own working, unrefused live access this session (confirmed by a prior successful Bash-tool live call), do the operation directly in the dispatching agents own foreground Bash session instead of re-dispatching at the same scope — this resolved the whole flow-authoring task in this instance.  
  <sub>IMP-0313</sub>


## Before you run something on a machine it has never run on

*14 lessons from 14 findings.*

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
- When a blocker trigger fires, process the UNREAD subset only. Run python3 scripts/verify-improvement-log.py --check FIRST and read its state breakdown: an entry in awaiting-approval already has a review document and needs the keyword sent against that document, never a second review of the same finding (IMP-0154). improvement-agent.md activation step 2 still says 'read every NEW entry', which was written when NEW meant unread and now costs a full strategic-tier pass over settled work.  
  <sub>IMP-0183</sub>
- Before treating a pipeline.yml step marked 'DEAD AS DECLARED' as unrunnable, check whether the settings file or capability its blocked_on cites has since been added — dev-auditing-settings.json existed for a full day before anyone re-ran ensure-auditing.ps1 -Env dev against it, and the harness refusal it also cited (IMP-0084) did not reproduce when finally re-tried. A blocked_on note is a claim about a point in time, not a standing fact.  
  <sub>IMP-0222</sub>
- Before packaging config/revitalise-grant-automation-build.yml, run `pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev` to create REV_FinanceOnly live, then `fieldsecurityprofiles?$filter=name eq 'REV_FinanceOnly'&$select=fieldsecurityprofileid` and substitute the real id into Other/FieldSecurityProfiles.xml:627 and the matching <RootComponent> in Other/Solution.xml:252 (same procedure IMP-0166 used for REV Trustee's roleid). This is a pipeline-agent/reviewer live-write action, not a development-agent source fix and not something build-agent can perform.  
  <sub>IMP-0243</sub>
- Before a new provisioning/*.ps1 script is considered done, run it through src/tests/provisioning/DataverseScripts.Tests.ps1's generic convention checks (Exit-Provisioning at the end, Write-CheckResult's CREATED/EXISTS/FAILED vocabulary, and a README inventory entry) rather than relying on a later, unrelated build's Pester run to surface it. Flagged for whoever owns WBS 6.5 (provisioning/dataverse/verify-access-test-identity.ps1) to fix; not actioned by this build-agent dispatch, which is scoped to WBS 0.4.  
  <sub>IMP-0244</sub>


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

*11 lessons from 11 findings.*

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
- generate-known-failure-modes.py's stdout 'distinct lessons' counts every row; the digest header's counts only NEW and APPLIED, because a REJECTED finding must stop teaching. A one-line gap between the two figures is the REJECTED population - not staleness, and not a concurrent session. Do not spend a review paragraph on it.  
  <sub>IMP-0334</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*46 lessons from 46 findings.*

- A parent agent's FAILED notification (API spend limit or any other terminal error) does NOT mean its own sub-dispatches stopped — they were already launched and keep running independently, and their completions arrive as separate, later notifications. Before concluding an improvement-agent (or any agent that itself uses the Agent tool) batch did 'nothing', run ListAgents to see every child's status, and verify each touched file directly (compile/parse/selftest/run against real data) rather than trusting only the parent's last words. When the spend limit is hit, do not immediately re-dispatch the same scale of work — it will likely fail identically; surface it to the reviewer (the error names the remedy: /usage-credits, ask the admin for a higher limit) and, if anything must proceed before that, do the smallest remaining reconciliation as a single narrow dispatch, not another wide fan-out.  
  <sub>IMP-0172</sub>
- When a Power Apps Code App's Dataverse connector fails with 'Invalid organization URL null provided', pass -u/--org-url explicitly to `pa app add data-source` (the environment's real org URL, readable from `pac auth list`) before escalating to Microsoft support -- do not rely on it resolving automatically from --connection-id/--environment-id, and do not expect pa connection list-datasets/list-tables to be fixable the same way, since neither takes an org-url flag at all.  
  <sub>IMP-0208</sub>
- To verify a Power Apps Code App generated service's write semantics, read the installed @microsoft/power-apps package's own shipped source under node_modules/@microsoft/power-apps/dist/ for the exact pinned version (Data.types.d.ts for the public signature, the two DataOperationExecutor.js files, and runtimeDataClient.js's _createHeaders) rather than assuming symmetry with a hand-rolled connector-operation call. The generated update(tableName, id, changes) has no headers parameter and sends a plain PATCH - it cannot enforce update-only (If-Match) semantics, so it must not replace a hand-rolled UpdateOnlyRecord + If-Match:'*' write path without a different mechanism.  
  <sub>IMP-0210</sub>
- When a hand-rolled Code App data layer's generic-connector reads fail on org-url-null and the app's own already-generated per-table typed services are confirmed to compile and to use a structurally different (immune) resolution path, migrate the READ call sites to those services while leaving any write that depends on connector-operation headers (If-Match, etc.) on the low-level executeAsync -- this is mechanically a change to ONE file (the hand-rolled client wrapper) when that wrapper's public function signatures are kept stable, not a repository-wide refactor. Verification stops at V2/V3 (tsc/eslint/233 unit tests against a mocked SDK) without host/browser access -- a clean build here is explicitly NOT sufficient evidence per IMP-0224/C-TECH-053, and V4 (a real signed-in trustee reproducing the original three failing calls and finding them fixed) has NOT been performed by this session.  
  <sub>IMP-0227</sub>
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

> **26 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0143, IMP-0173, IMP-0185, IMP-0193, IMP-0194, IMP-0195, IMP-0197, IMP-0199, IMP-0206, IMP-0209, IMP-0213, IMP-0216, IMP-0220, IMP-0223, IMP-0256, IMP-0257, IMP-0261, IMP-0278, IMP-0288, IMP-0291, IMP-0295, IMP-0306, IMP-0311, IMP-0314, IMP-0316, IMP-0317. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


## Unrouted — no section assigned

> These findings' `class_instance_of` values are missing from the routing table in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches the agent at the moment it applies.

*108 lessons from 108 findings.*

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
- A table created live via ensure-schema.ps1 does not inherit table-level auditing - check EntityDefinitions(LogicalName='<table>')?$select=IsAuditEnabled live for every NEW table the moment it is created, not only at the next full deployment sweep, and add it to auditedTables in every settings file (including a DEV one, which currently does not carry the key) before any row is written to it.  
  <sub>IMP-0178</sub>
- `pac solution check` against the Microsoft-hosted Solution Checker can hang indefinitely past its documented ~35s duration with no error and no output beyond 'Checking these solution files'. Before re-running it a third time, check `ps` for a still-alive `pac` process from a prior attempt (a killed shell wrapper can leave the underlying `pac` process running), and treat two identical hangs as the signal to stop and report rather than keep re-attempting — wrap the step with an explicit client-side timeout (e.g. `timeout 120 pac solution check ...`) so a stall produces a clean, fast, diagnosable failure instead of consuming minutes per attempt with no new information.  
  <sub>IMP-0215</sub>
- Before telling the reviewer their V4 access-test identity is ready, re-query BOTH axes of the column-security profile's membership live (fieldsecurityprofiles(<id>)/systemuserprofiles AND /teamprofiles) and confirm the trustee test identity is NOT among either — a prior dispatch's request to add 'one identity' as the positive control does not name WHICH one, and a human satisfying it with the trustee's own account silently converts the negative control into a false positive. The positive-control identity and the trustee (negative-control) identity must be verified as two different systemuserids before every V4 attempt, not just the first.  
  <sub>IMP-0228</sub>
- A regex that renders a V4-outstanding claim must match every phrasing the source log actually uses, not the phrasing it happened to be written against. Before trusting collect-project-status.py's v4_outstanding field, grep logs/pipeline.log for 'V4' and confirm the regex matches every variant present, or default the field to true (unresolved) rather than false when V4 is not affirmatively confirmed performed.  
  <sub>IMP-0229</sub>
- A gate that matches by column NAME alone across a whole Dataverse solution breaks the moment two tables reuse the same physical name for different-sensitivity columns - and this solution's rev_name primary-name convention guarantees exactly that collision. FR-016's check needs to match on (entity, column) or scope itself to only the columns the scoring flow's trigger entity (rev_application) actually exposes, not every secured name anywhere in the solution. NOT FIXED by this entry's author - deliberately left red rather than guessed at, since narrowing a HARD security gate under FR-016/DUAA 2025 is a judgement call outside a schema-only WBS task.  
  <sub>IMP-0236</sub>
- A PowerShell helper that reads '$xml.Parent.Child' to get 'the one' instance of a repeatable XML element (here <FieldSecurityProfile>) returns a broken array-shaped value instead of erroring the moment a second instance exists - test it, or write it as a foreach over the child collection, before assuming cardinality one is safe for a component type the platform allows to repeat.  
  <sub>IMP-0238</sub>
- A PowerShell script must never assign $PID, $HOME, $PWD, $MATCHES or any other read-only automatic variable — StrictMode makes it fatal, and `$pid` is an easy shorthand for a profile/principal id. More generally, and this is the part worth remembering: an AST-parsing contract suite reporting 375/375 over a PowerShell script is V1 evidence about SHAPE and says nothing about whether the script runs. Never report a live check as 'in place' on a green convention suite. Two corollaries now in agents/improvement-agent.md: improvement-agent's own executables belong in scripts/ (repository-internal checks, no credentials), and an executable needing live-environment credentials is delivery work that belongs under provisioning/ and should be handed to a delivery agent rather than authored by the agent that identified the need. A related bookkeeping cost: this file sat untracked, so an unrelated build read it as a concurrent session's work and attributed its three conformance failures to the wrong owner (IMP-0244) — check `git log`/the review documents before attributing an untracked file in this synced repository.  
  <sub>IMP-0246</sub>
- A harness refusal, a permission prompt or a safety classifier is a CONTROL, not a defect in the pipeline -- never propose, document or implement a change whose mechanism is that the control sees less than before. Concretely forbidden: omitting or softening the description of a live write in a dispatch prompt, moving a refused operation into a broader-permissioned or less-scoped session to dodge a classifier, and any wording whose benefit is that the harness no longer recognises what is about to happen. The legitimate responses to a refusal are all additive: prove access first with a read-only probe, perform the write in a session properly scoped for it that reports its result and verification query back, or hand the exact command to the human with the query that proves the outcome. If a proposal's advantage disappears once the operation is described honestly, that is the tell.  
  <sub>IMP-0264</sub>
- A handoff or dev summary's claim that a live provisioning re-run 'succeeded after both fixes' is a claim, not a result, especially when two independent defects were fixed in the same source revision - re-query EACH defect's own revisit_when condition live and separately, never infer that one succeeding means the other did too.  
  <sub>IMP-0270</sub>
- Every newly-created Dataverse table needs its own ensure-auditing.ps1 -Env <env> pass before any row is written to it - creating the table (ensure-schema.ps1) and enabling its audit switch (ensure-auditing.ps1) are two separate live actions, and a table can sit live and unaudited indefinitely with every source-side gate green, exactly as rev_review did in the IMP-0085/IMP-0178 precedent, until someone queries IsAuditEnabled directly.  
  <sub>IMP-0271</sub>
- Adding an organization-owned, schema-only table (no UI) reproduces the same 2 forms-and-views-reachable warnings (empty FormXml/SavedQueries markers) every prior schema-only table produced — add the triage row to the CURRENT feature's own Dev Summary Section 11 in the same change that adds the table, citing the WBS-0.4 precedent, rather than relying on build-agent to notice the omission against a different feature's document.  
  <sub>IMP-0323</sub>
- Walk the contract chain in BOTH directions. A task claiming completion with no artefact is an unevidenced claim; an artefact no task accounts for is unquoted work, and only the reverse direction finds it. rev_grantadministration shipped with no WBS task naming it.  
  <sub>IMP-0066</sub>
- When a schedule computes headroom per phase, check whether the same capacity is being counted for more than one phase - it must be cumulative, because finishing phase N requires finishing 0..N-1 too. And distinguish 'late because nobody started it' from 'late because it is blocked on the client': the first needs a queue, the second needs a phone call.  
  <sub>IMP-0069</sub>

> **88 further lesson(s) in this section are not shown** (cap: 20). Findings: IMP-0094, IMP-0110, IMP-0119, IMP-0134, IMP-0136, IMP-0138, IMP-0147, IMP-0149, IMP-0150, IMP-0151, IMP-0156, IMP-0158, IMP-0160, IMP-0163, IMP-0171, IMP-0176, IMP-0177, IMP-0179, IMP-0184, IMP-0186, IMP-0198, IMP-0200, IMP-0201, IMP-0203, IMP-0207, IMP-0211, IMP-0214, IMP-0218, IMP-0219, IMP-0225, IMP-0231, IMP-0234, IMP-0237, IMP-0239, IMP-0240, IMP-0247, IMP-0258, IMP-0260, IMP-0262, IMP-0263, IMP-0265, IMP-0266, IMP-0268, IMP-0269, IMP-0274, IMP-0275, IMP-0279, IMP-0280, IMP-0283, IMP-0284, IMP-0286, IMP-0289, IMP-0292, IMP-0293, IMP-0294, IMP-0296, IMP-0297, IMP-0298, IMP-0299, IMP-0300, IMP-0302, IMP-0305, IMP-0307, IMP-0308, IMP-0310, IMP-0312, IMP-0318, IMP-0321, IMP-0322, IMP-0325, IMP-0326, IMP-0327, IMP-0330, IMP-0331, IMP-0332, IMP-0335, IMP-0336, IMP-0337, IMP-0338, IMP-0339, IMP-0340, IMP-0341, IMP-0342, IMP-0343, IMP-0344, IMP-0347, IMP-0348, IMP-0351. Read them in `logs/improvement-log.jsonl`, or raise the cap in `scripts/generate-known-failure-modes.py`.


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
