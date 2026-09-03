# Known Failure Modes

**GENERATED FILE — do not hand-edit.** Regenerate with
`python3 scripts/generate-known-failure-modes.py` after any change to
`logs/improvement-log.jsonl`. CI and the improvement-agent verify it is current with
`--check`.

Source: `logs/improvement-log.jsonl` (581 entries, 578 distinct lessons)
Generated: 2026-09-02

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
| **x52** | `platform-contract-guessed-not-groundtruthed` | `before-authoring` ×44, `Capabilities` ×8 | IMP-0388, IMP-0406, IMP-0435, IMP-0473, IMP-0507, IMP-0508 (+46 earlier — see appendix) |
| **x43** | `gate-cannot-fail` | `before-build` ×42, `Capabilities` | IMP-0475, IMP-0491, IMP-0511, IMP-0542, IMP-0568, IMP-0569 (+37 earlier — see appendix) |
| **x31** | `hand-maintained-count-drifts-from-source` (also logged as `test-coupled-to-absolute-counts`) | `Unrouted` ×23, `before-build` ×8 | IMP-0521, IMP-0522, IMP-0529, IMP-0533, IMP-0534, IMP-0549 (+25 earlier — see appendix) |
| **x31** | `platform-fact-groundtruthed` | `Capabilities` ×24, `before-authoring` ×7 | IMP-0409, IMP-0417, IMP-0466, IMP-0467, IMP-0469, IMP-0496 (+25 earlier — see appendix) |
| **x28** | `finding-diagnosis-unverified` | `Unrouted` ×28 | IMP-0553, IMP-0560, IMP-0562, IMP-0564, IMP-0570, IMP-0571 (+22 earlier — see appendix) |
| **x28** | `gate-reassures-wrongly` | `Unrouted` ×28 | IMP-0461, IMP-0478, IMP-0483, IMP-0497, IMP-0527, IMP-0565 (+22 earlier — see appendix) |
| **x28** | `learning-substrate-destroyed` | `before-success` ×22, `Capabilities` ×6 | IMP-0333, IMP-0364, IMP-0421, IMP-0443, IMP-0456, IMP-0488 (+22 earlier — see appendix) |
| **x27** | `no-assertion-on-shipped-content` | `before-success` ×26, `Capabilities` | IMP-0509, IMP-0563, IMP-0566, IMP-0577, IMP-0581, IMP-0584 (+21 earlier — see appendix) |
| **x26** | `declared-policy-not-mechanically-enforced` | `Unrouted` ×25, `Capabilities` | IMP-0480, IMP-0501, IMP-0548, IMP-0567, IMP-0572, IMP-0574 (+20 earlier — see appendix) |
| **x25** | `approved-document-internally-inconsistent` | `Unrouted` ×25 | IMP-0465, IMP-0468, IMP-0481, IMP-0482, IMP-0492, IMP-0493 (+19 earlier — see appendix) |
| **x15** | `gate-scope-mismatch` | `before-build` ×15 | IMP-0445, IMP-0455, IMP-0472, IMP-0503, IMP-0505, IMP-0516 (+9 earlier — see appendix) |
| **x14** | `platform-state-divergence` | `Unrouted` ×14 | IMP-0372, IMP-0407, IMP-0408, IMP-0449, IMP-0489, IMP-0514 (+8 earlier — see appendix) |
| **x13** | `exit-zero-does-not-mean-created` | `before-deploy` ×13 | IMP-0101, IMP-0104, IMP-0106, IMP-0114, IMP-0122, IMP-0148 (+7 earlier — see appendix) |
| **x12** | `harness-blocks-destructive-call` | `operating` ×9, `Capabilities` ×3 | IMP-0245, IMP-0252, IMP-0287, IMP-0313, IMP-0314, IMP-0363 (+6 earlier — see appendix) |
| **x12** | `two-invocation-paths-disagree` | `before-build` ×12 | IMP-0144, IMP-0168, IMP-0232, IMP-0259, IMP-0394, IMP-0476 (+6 earlier — see appendix) |
| **x12** | `v3-does-not-imply-v4` | `before-deploy` ×11, `Capabilities` | IMP-0191, IMP-0192, IMP-0224, IMP-0227, IMP-0485, IMP-0502 (+6 earlier — see appendix) |
| **x11** | `gate-fires-on-nothing` | `before-build` ×11 | IMP-0428, IMP-0471, IMP-0495, IMP-0535, IMP-0557, IMP-0558 (+5 earlier — see appendix) |
| **x11** | `output-shape-defeats-the-reader` | `before-extending` ×10, `Capabilities` | IMP-0130, IMP-0142, IMP-0334, IMP-0450, IMP-0506, IMP-0554 (+5 earlier — see appendix) |
| **x7** | `untriaged-tool-warning` | `Unrouted` ×7 | IMP-0214, IMP-0323, IMP-0393, IMP-0411, IMP-0499, IMP-0573 (+1 earlier — see appendix) |
| **x6** | `agent-instructions-describe-a-topology-that-changed` | `before-running-elsewhere` ×6 | IMP-0056, IMP-0092, IMP-0162, IMP-0183, IMP-0222, IMP-0498 |
| **x6** | `test-assumed-name-is-solution-unique` | `Unrouted` ×6 | IMP-0234, IMP-0236, IMP-0237, IMP-0240, IMP-0247, IMP-0269 |
| **x5** | `baseline-restated-not-cited` | `before-commercial` ×5 | IMP-0029, IMP-0063, IMP-0064, IMP-0096, IMP-0418 |
| **x5** | `config-placeholder-known-but-not-fixed` | `before-running-elsewhere` ×5 | IMP-0145, IMP-0166, IMP-0175, IMP-0243, IMP-0244 |
| **x5** | `dispatched-agent-stalls-silently` | `Unrouted` ×3, `Capabilities` ×2 | IMP-0291, IMP-0300, IMP-0357, IMP-0520, IMP-0537 |
| **x5** | `requirement-names-data-the-solution-cannot-supply` | `Unrouted` ×5 | IMP-0293, IMP-0296, IMP-0326, IMP-0371, IMP-0463 |
| **x4** | `credential-not-on-the-machine-that-needs-it` | `before-running-elsewhere` ×3, `Capabilities` | IMP-0048, IMP-0061, IMP-0105, IMP-0528 |
| **x4** | `evidence-rule-satisfied-by-a-forward-reference` | `before-commercial` ×4 | IMP-0067, IMP-0097, IMP-0099, IMP-0140 |
| **x4** | `identifier-namespace-collision-across-documents` | `Unrouted` ×4 | IMP-0327, IMP-0336, IMP-0339, IMP-0576 |
| **x4** | `wrong-artefact-cited-as-evidence` | `Unrouted` ×4 | IMP-0305, IMP-0341, IMP-0429, IMP-0552 |
| **x3** | `concurrent-session-same-file-write` | `Unrouted` ×3 | IMP-0539, IMP-0541, IMP-0547 |
| **x3** | `gate-invocation-omits-required-arg` | `Unrouted` ×3 | IMP-0470, IMP-0479, IMP-0494 |
| **x3** | `incorporated-document-version-mismatch` | `Unrouted` ×3 | IMP-0071, IMP-0297, IMP-0381 |
| **x3** | `input-type-with-no-owning-agent` | `before-extending` ×3 | IMP-0028, IMP-0384, IMP-0510 |
| **x3** | `live-verification-capability` | `Capabilities` ×3 | IMP-0083, IMP-0555, IMP-0556 |
| **x2** | `change-order-sizing-without-precedent` | `Capabilities` ×2 | IMP-0278, IMP-0288 |
| **x2** | `code-apps-new-connector-blocks-boot` | `Capabilities`, `Unrouted` | IMP-0365, IMP-0392 |
| **x2** | `declared-knowledge-source-is-empty` | `Capabilities`, `before-extending` | IMP-0034, IMP-0058 |
| **x2** | `digest-cap-hides-a-whole-subject-area` | `Unrouted` ×2 | IMP-0383, IMP-0543 |
| **x2** | `dispatch-brief-asserts-unverified-fact` | `Unrouted` ×2 | IMP-0530, IMP-0559 |
| **x2** | `hard-gate-red-on-pre-existing-debt` | `Unrouted` ×2 | IMP-0439, IMP-0477 |
| **x2** | `instrument-exists-never-used` | `before-commercial` ×2 | IMP-0032, IMP-0545 |
| **x2** | `repo-path-contains-spaces` | `operating` ×2 | IMP-0010, IMP-0079 |
| **x2** | `stale-claim-contradicting-rechecked-source` | `Unrouted` ×2 | IMP-0524, IMP-0575 |
| **x2** | `tad-narrative-omits-an-already-existing-column` | `Unrouted` ×2 | IMP-0337, IMP-0338 |
| **x2** | `test-asserts-the-defect` | `Unrouted` ×2 | IMP-0111, IMP-0138 |

> **Two class names describing one property are COUNTED as one row here.** `test-coupled-to-absolute-counts` → `hand-maintained-count-drifts-from-source`. The alias is in this table only: each lesson still renders in its own section below, and the two halves keep their own gates, because a test fixture and a figure in a document are checked by different tools. The count is merged because the altitude rule fires on the *second* instance of a class — and a property recorded under two names produces a weaker signal than its true instance count ever should (`IMP-0330`).

> **A class named in two sections renders only in the last one.** `repo-path-contains-spaces` → `before-build`, `operating` (renders in `operating`). This is a silent precedence in the routing table, not a decision anything records — fix it by naming the class once, in the section where the lesson actually applies.


## Before you execute a build config

*88 lessons from 88 findings.*

- When a freshness/staleness bound is deliberately allowed to be unset as a fail-safe default, trace its effect through EVERY code path that uses the same comparison, not just the primary one it was designed for. Here, a bound meant to prevent 'skip recomputation and show something stale' also silently defeated 'accept the recomputation I just triggered and watched finish' -- because both checks shared one expression. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0511</sub>
- When a flow's answer moves from an HTTP response into a Dataverse row, re-derive WHO CAN WRITE that row before anything else: the app needs Write on the table to place its request, and one table serving both directions of the exchange hands the caller Write over the answer too. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0401</sub>
- Before believing a fix to a provisioning script's payload-building function is complete, check whether the step that CALLS it is create-only. ensure-schema.ps1's relationship step reports EXISTS and skips, so a corrected relationship/lookup body never reaches an environment where the relationship already exists — the fix lands in a fresh PRD and never in DEV, which is the harder direction to notice because DEV is where testing happens. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0259</sub>
- A compound deliverable ('X + access test') needs its evidence rule split so the human-verification half is tracked separately from the buildable half, and left permanently unsatisfiable by repository evidence alone -- report it as derived_status=partial (or a new manual_verification_required state) until a dated V4 confirmation exists, never as complete. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0230</sub>
- Before dispatching build-agent, check whether an open improvement-log finding already names a preflight-build-config defect (grep for class gate-cannot-fail against the target build config) — an unresolved NEW finding of this shape will halt the very next build at step 1, and the fix belongs to whoever owns the build config (development-agent), not to build-agent, which may not edit config/<slug>-build.yml.  
  <sub>IMP-0569</sub>
- verify-design-doc-claims.py's retraction blind spot (IMP-0428) is not a one-time cost paid once per document — it recurs every time a NEW sentence explains or cross-references an already-retracted claim, even in a document review 36 already made green. Author guidance embedded only in the gate's failure message does not reach the author before the sentence is written. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0535</sub>
- A gate that CRASHES has not failed safe - it has stopped being a gate, and every rule that says 'run the validator first' silently becomes unenforced. Two concrete fixes, both cheap: (1) validate `proposed_change` is a dict in the schema check, so a malformed entry is reported by ID at the point the log is read rather than surfacing later as a traceback; (2) make every consumer type-guard rather than None-guard - `isinstance(row.get('proposed_change'), dict)`, not `or {}`. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0423</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0431`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- A gate that selects its inputs by glob over a directory must EXCLUDE anything the repository ignores, or its verdict depends on local filesystem state no commit can change and differs between this Mac and CI. Concretely: scripts/verify-audited-tables.py's SETTINGS_GLOB matches provisioning/deploymentSettings/acc-settings.json, which is a Pester fixture gitignored at .gitignore:58 for exactly this reason, and an interrupted run leaving it behind turns the HARD `audited-tables` step red over a throwaway file AND stops DataverseScripts.Tests.ps1's whole 56-test container from running. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0410</sub>
- Every reader of logs/worklog.jsonl must call scripts/lib/worklog.py, never re-parse the file itself -- IMP-0093 named three scripts that needed this and fixed them, but a fourth script (collect-project-status.py, the one PM STATUS answers are required to render from without adding any figure of their own) reimplemented the pre-fix arithmetic and reproduces the identical 84-vs-64 over-count today. Grep for every 'WORKLOG.read_text' / raw json.loads(line) pattern against logs/worklog.jsonl, not just the three scripts IMP-0093 already named.  
  <sub>IMP-0232</sub>
- FIFTH instance of this class (after IMP-0005, IMP-0039, IMP-0120, IMP-0155) and the second specifically inside DeploymentSettings.Tests.ps1 (IMP-0155 already named this same file's option-set/role/relationship counts as stale). Adding a table to dataverse.auditing.auditedTables breaks this test every time; per skills/how-to-promote-a-finding.md the fix is to derive the expected count and table list from src/solutions/RevitaliseGrantAutomation/Entities/ (the way scripts/verify-audited-tables.py already does) rather than hand-typing a fourth/fifth/sixth number.  
  <sub>IMP-0212</sub>
- EnsureSchema.Tests.ps1's option-set count (line 196), role count (line 503), relationship-call count (line 592) and AddPrivilegesRole-call count (line 601) are FOURTH-instance absolute-count assertions (after IMP-0005/IMP-0039/IMP-0120) and are currently stale (expect 21/2/3/79, actual 24/3/6/99) against rev_review + REV Trustee role work already in this tree. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0155</sub>
- unit-tests is TWO gates in one step - the test count and the 80% coverage threshold - and a manifest that records only the counts hides a HARD C-TECH-014 failure. Record BOTH numbers, always. And when you add a .ps1 under provisioning/{common,entra,dataverse}, coverage scope includes it the moment it lands: contract tests that assert a script's output vocabulary lift the test count and cover almost none of its lines, so the suite goes greener while the constraint goes red. Check the coverage figure, not the pass count, after adding provisioning code.  
  <sub>IMP-0132</sub>
- A corrected worklog session must be excluded by every reader of logs/worklog.jsonl, not just by verify-worklog.py. Put the corrects/superseded rule in scripts/lib/ and have verify-wbs-chain.py and compute-invoice.py call it, or the repository states two different invoiced-to-date totals and both gates pass.  
  <sub>IMP-0093</sub>
- A preflight result that depends on files left behind by a previous run is not a result. `tee PATH` PRODUCES that path and `test -s PATH` asserts on it — both now have branches in extract_paths — and any new intra-step write-then-assert pattern needs one too. When changing the preflight, run it with ARTIFACT_DIR pointing at a directory that does NOT exist; on a reused directory it will agree with you for the wrong reason.  
  <sub>IMP-0089</sub>
- In ensure-schema.ps1, RELATIONSHIPS must run before ALTERNATE KEYS: a key on a lookup column cannot be created before the relationship that creates that column (Dataverse 0x80040203). Sections reordered 2026-08-18. Mocked API tests cannot catch step-order defects - a mocked POST succeeds regardless of what exists.  
  <sub>IMP-0043</sub>
- There is no preflight for pipeline.yml. A pipeline step can name a script that does not exist, a parameter that does not exist, or a path that does not exist, and nothing will say so until the stage runs against a live environment. Verify every script path and parameter against the script's own param block before executing a stage - and note that alternate keys are declared in Entity.xml <EntityKeys>, not created by a script switch.  
  <sub>IMP-0042</sub>
- A HARD constraint whose rule text is still a placeholder always PASSES and is therefore a gate that cannot fail. C-DOM-030 and C-DOM-031 are placeholders; report them as UNEVALUABLE rather than PASS, and note that skills/how-to-apply-constraints.md has no status for that outcome.  
  <sub>IMP-0035</sub>
- In a YAML `>` folded scalar, keep every line at the SAME indentation and put `&&`/`||` at line END — a more-indented line keeps its newline and yields a shell syntax error. Preflight now runs `bash -n` on every step command.  
  <sub>IMP-0025</sub>
- The `! grep ... && echo` gate pattern turns EVERY grep failure — including 'target does not exist' (exit 2) — into a PASS. Verify the target path exists before trusting any such gate.  
  <sub>IMP-0007</sub>
- `pac solution check --path` takes a PACKED .zip, never a source folder — and it must run AFTER the pack step that produces it.  
  <sub>IMP-0004</sub>

> **68 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`gate-cannot-fail`** (×30): IMP-0424, IMP-0458, IMP-0475, IMP-0491, IMP-0542, IMP-0568 (+24 earlier — see appendix)
>   · **`gate-scope-mismatch`** (×13): IMP-0445, IMP-0455, IMP-0472, IMP-0503, IMP-0505, IMP-0516 (+7 earlier — see appendix)
>   · **`gate-fires-on-nothing`** (×10): IMP-0328, IMP-0428, IMP-0471, IMP-0495, IMP-0557, IMP-0558 (+4 earlier — see appendix)
>   · **`two-invocation-paths-disagree`** (×9): IMP-0077, IMP-0107, IMP-0144, IMP-0168, IMP-0394, IMP-0476 (+3 earlier — see appendix)
>   · **`hand-maintained-count-drifts-from-source`** (×6): IMP-0005, IMP-0039, IMP-0120, IMP-0235, IMP-0315, IMP-0416


## Before you hand-author a platform artefact

*53 lessons from 53 findings.*

- subscriptionRequest/message on the Dataverse connector's SubscribeWebhookTrigger is NOT {1 Create, 2 Update, 3 Delete}. Read live from stringmap in REV-GrantApplications-DEV 2026-08-28: 1 Added, 2 DELETED, 3 MODIFIED, 4 Added or Modified, 5 Added or Deleted, 6 Modified or Deleted, 7 Added or Modified or Deleted. For 'fires when a row is updated' the value is 3. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0406</sub>
- Adding a NEW connector type to a Code App's power.config.json (not just a new table on an already-connected connector) is not safely additive by default -- ground-truth, before the next such addition, whether the Power Apps Code App host resolves ALL declared data sources before first render or only on first call. Until confirmed, treat a brand-new connector as a boot-risk change: verify with a real signed-in test user immediately after the push, before treating the deploy as done, rather than deferring V4 the way both the 22:34 and 23:11 entries did. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0358</sub>
- When a corrected write pattern (GET-full-object -> mutate -> PUT-uncast-URI) is established for one Dataverse Web API metadata endpoint, check every OTHER script in the repo that PATCHes a sibling metadata endpoint before trusting its PATCH as still-working precedent -- ensure-schema.ps1's own step-3b comment had already flagged ensure-auditing.ps1's entity-level PATCH as 'the one still-open exception to reconcile', by name, and it sat unreconciled until a live run actually needed the write to happen for real.  
  <sub>IMP-0277</sub>
- A Dataverse Web API metadata write (EntityDefinitions and its derived Attributes types alike) never accepts PATCH -- entity and attribute metadata updates are PUT-only, and PUT requires the complete current object, never a partial body. Before writing any future entity-metadata update, follow the corrected GET-full-object -> mutate -> PUT-whole-object pattern already fixed in ensure-schema.ps1 step 3b (IMP-0272/IMP-0273), never the organisation-record PATCH pattern elsewhere in the same script -- a data record and a metadata endpoint look similar in this codebase but take opposite verbs.  
  <sub>IMP-0276</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0277`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- When a metadata PATCH against a Dataverse Web API collection is rejected outright ('does not support http method X'), check Microsoft's own 'Update a column' / 'Update table definitions' pages before assuming a missing cast segment: entity and attribute metadata updates are documented as PUT-only, with the full current object as the body, and the cast segment (needed on the GET used to fetch that object) does NOT carry over to the write URI. A verb rejection and a wrong-cast 404 read alike as 'the naive call failed' but have different fixes.  
  <sub>IMP-0273</sub>
- A metadata PATCH against Dataverse's abstract AttributeMetadata entity set requires the concrete derived-type cast segment IN THE URI, not only in the request body's @odata.type -- the same polymorphism trap already known on the GET/read side (a 404 under the wrong cast) also applies to writes, as an outright method-not-supported rejection of the base, uncast collection. Before modeling a new metadata PATCH on an existing one, check whether the target entity set is polymorphic; EntityDefinitions and Attributes are not interchangeable examples of the same shape.  
  <sub>IMP-0272</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0273`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- A Dataverse table's primary name attribute can never carry IsSecured=1 - creating it fails with 0x8004f501 "The field '<name>' is not securable." Never secure a primary name column, even when a source document's literal wording states a blanket rule like "every column" with no exception carved out; ground-truth against a real create call before treating that wording as settled.  
  <sub>IMP-0249</sub>
- Before running the V4 access test's positive control ('read as the process owner/service identity, confirm populated'), confirm live that at least one identity is actually a member of REV_TrusteeRestricted (fieldsecurityprofiles({id})/systemuserprofiles for DEV's direct-assignment model, or teamprofiles for TST/ACC/PRD's group-team model) -- in DEV as of 2026-08-23 it is zero on both axes, so the comparison read will return null for everyone and prove nothing until one identity (e.g. svc_grantapplications, or the named process owner) is added as a direct member first.  
  <sub>IMP-0221</sub>
- The intake flow still has SIX Get-a-row-by-id actions using an alternate key in Row ID (AgeBandMap, PostcodeRegionMap, AgeRangeLabelMap, ExceptionalCircumstanceLabelMap, EmploymentStatusLabelMap, CareHoursBandLabelMap). The connector rejects that shape - proven by the scoring flow failing on all 11 of its first runs - so the intake flow will fail on its first live submission from the website. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0112</sub>
- Fluent v9's createLightTheme does not guarantee AA: colorBrandBackground and colorBrandBackgroundStatic are brand[80] behind a hard-coded white, so a brand whose shade 80 is under 4.5:1 against white ships a failing primary button. Compute white-on-brand[80] before adopting any ramp, and if it is under 4.5:1 move BOTH rest tokens to brand[70] and shift Hover/Pressed/Selected one step too (brand[60]/[30]/[50]), or rest and hover become the same colour and the button loses all hover feedback. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0352</sub>
- Before debugging a Power Platform app's Dataverse/connector/role errors on ANY machine, first confirm which Entra identity the browser is actually signed in as (open https://myaccount.microsoft.com in a plain tab, no app link first) - a device enrolled in Microsoft's Company Portal / Enterprise SSO extension (check `pluginkit -m | grep -i microsoft` and `profiles status -type enrollment`) can silently authenticate every Microsoft sign-in, INCLUDING INCOGNITO WINDOWS, as whatever account the extension last cached, with no prompt and no browser-level fix. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0189</sub>
- pac code push fails HTTP 403 CodeAppOperationNotAllowedInEnvironment unless the target environment has the 'Power Apps code apps' product feature enabled first (Power Platform admin center -> Environments -> <env> -> Settings -> Product -> Features -> 'Power Apps code apps' toggle -> Save). Admin-center UI only -- no pac CLI verb, and it is not a Dataverse organization-entity attribute. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0182</sub>
- A field security profile's membership list is who it grants access TO, not who it withholds from - never write a dispatch instruction that says 'bind role X to profile Y' without first reading the profile XML to confirm whether X should be ADDED as a member (grants access) or must NEVER be a member (the actual control). For REV_TrusteeRestricted specifically, the control IS non-membership - trustees must never be added to it.  
  <sub>IMP-0153</sub>
- Initialize variable is legal ONLY at the top level of a Power Automate flow - never inside a Scope, condition, Apply to each or Switch. A nested one packs, imports and reports Activated, then the designer refuses to save and the flow cannot be turned on. Increment/Set/AppendToString variable may nest freely; only the declaration may not. When a nested declaration has to be lifted, move the runAfter guard it sat behind onto the action that CONSUMES the variable, not onto the declaration.  
  <sub>IMP-0137</sub>
- The workflow definition language has NO select() and NO filter() expression - both are data-operation ACTIONS (Select, Filter array), and item() is only valid inside one. To project an array in an expression you cannot; add a Select action and join its body. Grep any flow for 'select(' and 'filter(' before believing it works: both pack, import and report Activated, and fail only when the branch containing them is first taken. Related: if() evaluates ONLY the branch it takes here, proven by TD-07 failing and TD-08 passing on the same action.  
  <sub>IMP-0124</sub>
  <br><sub>**⚠ CONTESTED by `IMP-0412`** — a later finding disputes a claim in this lesson and NEITHER has been re-tested. Read that entry before relying on this one; it carries the form that is safe under either answer.</sub>
- The Dataverse connector is ASYMMETRIC: CreateRecord accepts a nested "item": { columns } object (verified working), UpdateRecord does NOT - its columns must be flattened to "item/<column>" beside entityName and recordId, the same way Teams uses body/recipient and Office 365 uses emailMessage/To. A nested item on an UpdateRecord shows as an action with NO PROPERTIES CONFIGURED in the designer and writes nothing WHILE SUCCEEDING, so there is no error and no error-log row - a green run and an empty column is the only symptom. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0116</sub>
- subscriptionRequest/runas must be 3 for 'flow owner' on a Dataverse row trigger. 4 packs, imports and reports statecode=Activated while creating NO webhook subscription, so the flow never fires and nothing reports a problem. After turning any Dataverse-triggered flow on, assert a callbackregistration row exists for the table (callbackregistrations?$filter=entityname eq 'x') - that is the only signal that distinguishes a registered trigger from an activated-but-dead one. Source at REVScoringCalculateAndFlag line 59 still carries 4 and will reproduce this in TST/ACC and PRD.  
  <sub>IMP-0108</sub>
- `secrets` is not available in ANY `if:` expression - GitHub rejects the WHOLE workflow file and every run shows zero jobs, with no failing check to notice. To branch on whether a secret exists, project it into a job-level `env` boolean (job `env` MAY read secrets) and test `env.FLAG == 'true'` in the step `if:`. And validate .github/workflows/*.yml before pushing: an invalid workflow file is the only defect class CI cannot tell you about, because nothing runs.  
  <sub>IMP-0074</sub>
- An environmentvariabledefinition.xml must contain ONLY its root element - no XML declaration, no comment. A comment makes solution import fail with 0x80040216 at ImportXml.GetComponentsList, naming nothing, while the file remains valid XML and pac solution pack exits 0. The rule is in src/solutions/RevitaliseGrantAutomation/environmentvariabledefinitions/README.md. BEFORE authoring a new file beside existing ones, diff your element set against a sibling and read any README in that folder.  
  <sub>IMP-0045</sub>
- Dataverse rejects a Picklist->String/Boolean change via solution import, and the follow-up delete is blocked by any form that references the column. Procedure: strip the control from the form in a transitional import, delete, then recreate at the correct type via the Web API.  
  <sub>IMP-0017</sub>

> **33 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`platform-contract-guessed-not-groundtruthed`** (×26): IMP-0360, IMP-0361, IMP-0388, IMP-0473, IMP-0507, IMP-0508 (+20 earlier — see appendix)
>   · **`platform-fact-groundtruthed`** (×6): IMP-0356, IMP-0359, IMP-0362, IMP-0367, IMP-0378, IMP-0496
>   · **`platform-field-length-limit-unenforced`** (×1): IMP-0009


## Before you declare a deploy or an import successful

*25 lessons from 25 findings.*

- Before reporting a Code App feature "DEPLOYED TO DEV (V3)", grep the app's own runtime call sites against dataSourcesInfo.ts's top-level keys for every entity set referenced -- a table existing live and correctly named in solution source says nothing about whether `pac/pa app add-data-source` was ever run for it in the Code App, and V3 (solution accepted) gives no signal either way.  
  <sub>IMP-0485</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0487`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- A `pa app add data-source --table <t> -u <org-url>` success, a clean `tsc`/`eslint`, and a `git diff` showing new generated files are evidence about the PER-TABLE typed-service data source only. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0224</sub>
- `pac code add-data-source -a <apiId>` takes the SHORT connector id (e.g. `shared_commondataserviceforapps`), never the full '/providers/Microsoft.PowerApps/apis/<id>' path shown by `pac connection list`'s API Id column or power.config.json's connectionReferences.<guid>.id - passing the full path 404s with a visibly malformed doubled-slash URL (.../connectors//providers/...). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0192</sub>
- When a Code App's Dataverse connector fails with 'Invalid organization URL null provided' and account identity, role grant (including team-inherited roles via teamroles, not just systemuserroles), and per-user connection existence all check out live, stop treating it as a local configuration problem - it is very likely a Power Apps Code Apps (Preview) host/SDK defect outside this project's control. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0191</sub>
- A Code App reported live by `pac code list` and reachable in the maker portal (V3) can still fail every Dataverse connector call for a real signed-in user with "Invalid organization URL 'null' provided" - identical across unrelated tables, which rules out a security-role cause outright (that would 403 per-entity on that entity's own privileges, not repeat verbatim). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0187</sub>
- A callbackregistration existing, with a createdon that is not stale against the flow's modifiedon, and a live subscriptionRequest matching source exactly, is still not proof a Dataverse-triggered flow will fire — the only proof is creating a real row and observing rev_scoredon (or an asyncoperation, or an error log row) change. REV | Scoring | Calculate & Flag passed every documented precondition in REV-GrantApplications-ACC (TST/ACC) and did not fire for any of 12 rows in 9 minutes, after firing correctly for all 12 in DEV. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0148</sub>
- Adding a column is TWO deployments, not one. The form cell travels in the solution import; the COLUMN does not - creating schema by import is unsupported, which is exactly why ensure-schema.ps1 exists. Run `pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev` after any import that adds a column, and verify with EntityDefinitions(LogicalName='x')/Attributes?$select=LogicalName. Skip it and you ship a form bound to a column that is not there, with a successful import and a published solution to reassure you.  
  <sub>IMP-0122</sub>
- Set an environment variable's CURRENT VALUE, never its DEFAULT VALUE. A default lives inside the environmentvariabledefinition, which is solution content, so the next import overwrites it with whatever source declares - nothing - and every flow that reads it silently loses its configuration. A current value is a separate environmentvariablevalue row that no import here touches. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0121</sub>
- A callbackregistration row surviving a solution import is not evidence that the trigger works. Compare its createdon against the flow's modifiedon: if the registration predates the import, it pins logicappsversion to a definition version that no longer exists, and Dataverse delivers events into nothing - no run, no error, empty run history. Existence is the wrong assertion. The registration must be RECREATED: turn the flow off, confirm the row disappears, then turn it on from the DESIGNER and confirm a row with a NEW createdon appears. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0114</sub>
- When a Dataverse-triggered flow does not fire, ownership and scope are NOT the first thing to suspect - prove it with two rows, one owned by the flow owner and one not, which takes two minutes and rules out scope=User entirely. If neither fires and callbackregistrations is 0, every remaining cause is OUTSIDE Dataverse (connection health, DLP policy, a subscription error shown only in the maker UI) and no amount of further querying will find it: hand it to someone with the Power Automate UI. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0106</sub>
- statecode=1 on a cloud flow does NOT mean its Dataverse trigger is registered. Query callbackregistrations?$filter=entityname eq '<table>' - if it returns 0, Dataverse will never call the flow, no run is attempted, and run history shows nothing because there is nothing to show. Fix it by opening the flow in the Power Automate DESIGNER and saving it, not by toggling it in the Solutions list. Check the count as an identity with System Administrator, or a 0 may mean you cannot see the rows. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0104</sub>
- An environment variable DEFINITION travels in the solution; its VALUE does not, and nothing in this repo writes one. Query environmentvariablevalue joined to environmentvariabledefinition before believing any flow can notify anyone: on 2026-08-20 DEV held 4 definitions and 0 values, so every Teams action and the failure-alert fallback email would have failed. isrequired=1 with no defaultvalue is the shape to look for - it is a required setting nobody is scripted to supply.  
  <sub>IMP-0101</sub>
- Attribute-level IsAuditEnabled proves nothing: Dataverse auditing needs organizations.isauditenabled AND the table's own IsAuditEnabled, and NEITHER is settable from solution source — entity-level IsAuditEnabled is absent from every Entity.xml here. Query organizations?$select=isauditenabled,auditretentionperiodv2 and EntityDefinitions(...)?$select=IsAuditEnabled live before reporting any audit constraint as PASS, and check logs/pipeline.log that ensure-auditing.ps1 actually ran — on 2026-08-19 it never had, and DEV had no audit trail at all.  
  <sub>IMP-0082</sub>
- A Status column is a claim, not a result - the same class as a successful import that created nothing. Derive task state from repository and environment evidence, keep the hand-typed value as claimed_status, and report every disagreement: WBS 0.4 was marked Done with five of the eight tables it names absent.  
  <sub>IMP-0030</sub>
- Solution import can report SUCCESS having silently skipped components. This is the second recorded instance; treat 'import succeeded' as a claim to verify, never a result.  
  <sub>IMP-0018</sub>
- An Unvalidated Assumptions Register row that is still OPEN is a prediction of a live defect, not paperwork. Close it before deploying, or expect the reviewer to find it.  
  <sub>IMP-0014</sub>
- After an import, query EVERY declared component type by name. A hand-written subset of types to check will omit the one that failed — savedquery and systemform were both absent from the list that 'verified' the first DEV deploy.  
  <sub>IMP-0013</sub>
- A successful import proves the component was ACCEPTED, not that it works. Three components imported cleanly, were queryable, and still could not be opened or saved by a maker.  
  <sub>IMP-0012</sub>
- A fully green local build (all static/preflight gates passing) says nothing about whether an environment-side V4 step blocking the feature has moved since the last test cycle - re-check the environment fact itself (here: callbackregistration.createdon) at the START of every test cycle rather than inferring from a clean build log that progress was made on it.  
  <sub>IMP-0502</sub>
- An unmanaged pac solution import with --force-overwrite DEACTIVATES every cloud flow in the solution - statecode 1 becomes 0 - while reporting 'completed successfully'. Capture the flow statecodes BEFORE the import and re-assert them after, and treat re-activation as a named post-deploy step with an owner. Re-activate IN THE DESIGNER, never by PATCHing workflow.statecode: a statecode flip can leave the flow reporting Activated with no callbackregistration row, which is the un-triggerable state that cost four rounds on 2026-08-20. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0113</sub>

> **5 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`exit-zero-does-not-mean-created`** (×3): IMP-0019, IMP-0065, IMP-0078
>   · **`v3-does-not-imply-v4`** (×2): IMP-0088, IMP-0100


## Before you report SUCCESS at all

*48 lessons from 48 findings.*

- A dev-summary sentence claiming a UI conversion is "implemented in full" or "shipped" must be checked against git (is it committed?) and pipeline.log/a deployment artifact (did it reach the target?), never against the working tree alone -- "the file exists and the build is clean" is V1/V2 evidence and cannot support "shipped" language, which a reviewer deciding what to expect on screen reasonably reads as V4.  
  <sub>IMP-0486</sub>
- When an ADR splits a table and the superseded columns are RETAINED rather than deleted, the old columns stay valid write targets and every stale writer keeps succeeding silently — a green run with an empty UI is the only symptom. After any such split, grep provisioning/ AND the flow definitions for the OLD entity set name and re-point every writer, then assert the new target in a test; do not trust a <Description> saying 'written by nothing' to be true, because nothing checks it. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0434</sub>
- DataverseScripts.Tests.ps1's 56-test container is a convention/shape check (IMP-0246's class), not a behavioural test — passing it is not evidence that a NEW provisioning script's own Dataverse-call logic executes even once. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0433</sub>
- REVIntakeWordPressToDataverse and REVScoringDailySummary each read personal-data rows (rev_application/rev_applicant) without Secure Outputs — a real, already-shipped exposure, not a hypothetical one. Fixing it is OUT OF THIS DISPATCH'S WBS SCOPE (6.1/6.3/6.5/6.9) — it touches Automation #1 and #2, not the Trustee Portal — and is flagged here rather than silently fixed, per C-COM-002 (work enters by WBS task id or a change-order decision, never built first and reconciled later). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0320</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0322`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- When a dispatch is fixing a stale-write finding, re-run the gate against its output rather than trusting the fix: the dispatch fixing IMP-0438 removed one superseded-column write and added two more plus a write to the flow's own trigger column, while rewriting the header, the inline comment and the status message to say the body was 'rev_name and nothing else'. Prose and code were edited in the same commit and only the prose was correct. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0446</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0447`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- Fixing the script a finding describes does not close the finding's own log entry -- IMP-0277 corrected ensure-auditing.ps1 but left IMP-0276 (the finding it corrects) sitting NEW/unread with no deferred_reason, which is independently a C-TECH-061 HARD violation that fails any build reaching the unit-tests step. Before dispatching a full build, run `python3 scripts/verify-improvement-log.py --check` standalone first -- it is the exact assertion buried 39-41 steps into the sequence, needs no npm/tsc/vitest/pester setup, and turns a several-minute wasted build attempt into a one-second pre-check. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0285</sub>
- Adding a Dataverse table to a model-driven app is FOUR changes, not two and not three: (1) the entity, (2) a SubArea in AppModuleSiteMaps/, (3) an <AppModuleComponent type="1" schemaName=".."/> in AppModules/<app>/AppModule.xml, and (4) the audit switch in the environment. Miss (3) and the table appears in the designer's EDIT mode and is absent in PLAY mode, surviving a hard refresh — which reads exactly like a platform caching bug and is not one. Diff AppModule.xml's component list against the Entities/ folders on disk before believing any reachability gate.  
  <sub>IMP-0090</sub>
- When a fix makes one config resolve a value per run, grep for every OTHER file that names that value. IMP-0016 fixed build.yml and left pipeline.yml pointing at a directory that stopped existing the next day. Also: `upload-artifact` roots the archive at the least common ancestor of the paths it matched — name the PARENT directory, not a `**` glob, or the directory you care about is stripped from the archive.  
  <sub>IMP-0049</sub>
- ensure-schema.ps1 derives nothing from disk: Get-RevEntityLogicalNames is a hand-kept list and the relationship detail path was hardcoded to one file. An entity absent from that list is an entity C-TECH-050's prerequisite step will NOT create, silently - so adding a table means editing that list, and a gate should compare it against Entities/ on disk.  
  <sub>IMP-0038</sub>
- Each build gets its own artifact directory via scripts/resolve-artifact-dir.py. Never hardcode an artifact path: six builds once shared one directory and three manifests were lost.  
  <sub>IMP-0016</sub>
- SVG/canvas baseline-offset (dy) arithmetic that is supposed to equal a stated design-token gap is the same class of unassertable-in-jsdom arithmetic C-TECH-076 was written for, and should be broadened to a check C (or a new constraint row) that reads the named gap/ascent/descender constants in a chart component and confirms the derived dy against them symbolically, the same way check A/B read CSS values rather than trusting a comment.  
  <sub>IMP-0584</sub>
- When reserving space below a wrapped SVG/CSS text block by setting a text node's dy/baseline offset, that offset is a BASELINE position, not a visible gap: the glyphs' ASCENT sits above the baseline, so a dy equal to the desired gap under-reserves by roughly one ascent (~0.8em). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0581</sub>
- When two or more per-chart width constants are each meant to hold the SAME wrapped-tick-label budget, derive them from ONE shared pixel-width constant computed from the wrap budget (chars-per-line x an estimated glyph width), never let each chart's own width be sized independently by a different heuristic (a size ratio, a bar count, a guess) -- two independently-guessed figures governed by the same real-world constraint will eventually diverge, and jsdom cannot catch the divergence.  
  <sub>IMP-0577</sub>
- Two controls that declare the same `min-height` are not the same height unless BOTH also fix their box: `min-height` is the rendered height only where an explicit `height` or `box-sizing: border-box` plus fitting padding already bounds it, and is otherwise a floor a content-sized box has already cleared. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0566</sub>
- When you add a SECOND mechanism that relocates content, extend the destination and the assertion in the same change - an existing 'nothing is lost' test covers only the population it was written for, and two relocation mechanisms produce disjoint populations. Concretely for generate-known-failure-modes.py: the per-section cap and the per-lesson budget both point readers at known-failure-modes-appendix.md, and the appendix needs a part for each. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0563</sub>
- A font-size change to a shape borrowed from a host framework (Fluent, or any design system whose root sets typography on `body`/its provider root) needs an explicit line-height alongside it -- inheriting the host's line-height tuned for its own base font-size silently produces overlapping wrapped lines at any size larger than that base, and this is invisible to jsdom-based tests, clean type-checks, and clean lint, because it is a paint-time collision, not a box-model defect. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0509</sub>
- A review parked at its gate is invisible to the queue gate, so `unread` cannot be trusted to mean 'nobody has looked at this' while any review sits unapproved. Before treating a batch trigger as real, check whether a review document already names the entries - verify-improvement-log.py prints exactly that as a WARNING per entry, and those warnings are the signal, not noise. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0421</sub>
- IMP-0172's 'verify live state directly, do not re-dispatch the same scale of work' protocol holds even when a dispatch dies AFTER finishing its real work, mid-report -- the tell is a terminal message describing report-writing or summarising rather than implementation, and the fix is the same: check the files, run every verification command yourself (including re-running any tool the dead agent's own comments claim passed, rather than trusting the claim), and only re-dispatch the narrow remainder if something is actually missing or broken.  
  <sub>IMP-0364</sub>
- When a defect in a hand-authored flow definition is fixed, add a source-level test over the definition in the same change - the packer, the Solution Checker and the flow-shape gate all pass over a semantically broken failure path, so the fix is guarded by nothing until such a test exists.  
  <sub>IMP-0346</sub>
- A build manifest's free-text provenance note is an unchecked claim about shipped content - resolve every artefact it names to a path on disk before trusting it, because no gate reads that prose. Record the dirty-path COUNT (IMP-0078) and stop there; enumerating what the dirty tree contains restates the dispatch's intended scope, not the tree's actual contents.  
  <sub>IMP-0324</sub>

> **28 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`learning-substrate-destroyed`** (×16): IMP-0301, IMP-0309, IMP-0333, IMP-0443, IMP-0456, IMP-0488 (+10 earlier — see appendix)
>   · **`no-assertion-on-shipped-content`** (×12): IMP-0131, IMP-0139, IMP-0350, IMP-0353, IMP-0438, IMP-0448 (+6 earlier — see appendix)


## Operating constraints of this environment

*12 lessons from 12 findings.*

- Under Auto Mode, a cert/keychain-touching pwsh command is refused by the classifier regardless of whether every Dataverse call inside it is a GET -- IMP-0084's 'reads run freely' finding holds only for a non-Auto-Mode session. An agent dispatched under Auto Mode has ZERO live-Dataverse reach, not just no-write reach, and must say so plainly rather than assuming the read-only method that worked in a previous test round will work again.  
  <sub>IMP-0287</sub>
- Under Auto Mode, the classifier can refuse an Agent-tool dispatch outright based on the prompt describing a live write -- not only the pwsh command a dispatched agent later tries to run. This is a NEW, earlier refusal point than the seven prior instances of this class. Before re-dispatching any agent whose job is to attempt a known-blocked live write, expect the dispatch call itself may be refused, and have the REVIEWER ACTION REQUIRED message (the exact command for the human to run themselves) ready as the immediate next step rather than assuming a subagent will get a chance to try.  
  <sub>IMP-0252</sub>
- Under Auto Mode, the classifier auto-denies a cert/keychain-touching pwsh command outright with no permission prompt -- this may hold even in a session that would otherwise count as the reviewer's own 'foreground' one per IMP-0173, because auto mode itself removes the human from the approval loop. Before assuming a foreground retry will succeed, check whether Auto Mode is active in that session too; if so, the retry needs a normal (non-auto) interactive session where a human can see and approve the prompt. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0245</sub>
- Fifth instance. Any agent that can be dispatched to run a live `provisioning/**/*.ps1` write - not only pipeline-agent - needs the same 'Reviewer-Executed Operations' behaviour: attempt the call, and on a classifier refusal emit the exact command plus its pre/post verification query rather than reporting the task as merely blocked. Currently this behaviour lives only in agents/pipeline-agent.md; development-agent.md's sub-agent table (identity-agent, automation-agent, config-agent, m365-agent - every one that can write to a live environment) has no equivalent pointer.  
  <sub>IMP-0170</sub>
- THIRD instance. A gate keyword authorises an operation inside this system; it does not grant the session permission to perform it. Live Dataverse WRITES (metadata PATCH, DeleteOptionValue, organisation settings) are refused by the harness even under APPROVE TENANT, while reads are not. Establish the permission BEFORE reporting that a gate keyword will produce a live change: either the reviewer adds a Bash permission rule, or the operation is handed to them with the exact call to make. Never leave the reviewer believing a keyword was sufficient.  
  <sub>IMP-0084</sub>
- Before assuming a provisioning script needs a code change for a new attribute/option-set/field-permission, check whether it reads its inputs generically from the XML source tree (Get-RevEntityLogicalNames-style helpers in this project's ensure-schema-helpers.psm1 do, for all three) -- most of this project's schema changes over its history needed zero script changes, only new/edited XML. And: a HARD count assertion in this codebase's own Pester suite (e.g. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0363</sub>
- When an Agent-tool dispatch itself is refused (not a call the dispatched agent later tries), do not retry the identical dispatch. If the dispatching agent already has its own working, unrefused live access this session (confirmed by a prior successful Bash-tool live call), do the operation directly in the dispatching agents own foreground Bash session instead of re-dispatching at the same scope — this resolved the whole flow-authoring task in this instance.  
  <sub>IMP-0313</sub>
- When handing a human (not a subagent) a command that depends on environment variables, state the export syntax for THEIR shell explicitly rather than reusing whatever syntax the surrounding documentation happens to use. This project's own knowledge file only ever shows these two values inside a PowerShell object literal, which reads as "this is a pwsh session" and is not -- the actual usage pattern everywhere else is export in bash/zsh, then invoke pwsh -File as a subprocess (env vars inherit into the child process normally). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0253</sub>
- Fourth instance, and the first since the protocol was written — the protocol worked, so do not escalate it further. Two additions from this one: (1) READS can be refused too, when the shell command carries a $(...) substitution that looks like injection; reach for the dedicated Read tool rather than rephrasing the shell. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0133</sub>
- Third confirmation: `pac solution check --outputDirectory` writes NOTHING on this repo's path and still says 'Finished downloading 1 files'. Tee the command's stdout into the artifact and assert the target directory is non-empty — otherwise the only evidence for a HARD gate lives in a console log that CI throws away.  
  <sub>IMP-0079</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0413`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- Destructive metadata calls (DeleteOptionValue) may be refused by the session's safety classifier regardless of authorisation. Route these to the reviewer via the maker portal.  
  <sub>IMP-0021</sub>
- This repo's path contains spaces. `pac solution check --outputDirectory` silently writes nothing; read the result from stdout instead.  
  <sub>IMP-0010</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0420`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>


## Before you run something on a machine it has never run on

*16 lessons from 16 findings.*

- A dispatch whose brief requires a live ensure-schema.ps1 (or any provisioning script needing PROVISION_APP_ID/PROVISION_CERT_THUMBPRINT) run should say so up front and route straight to REVIEWER ACTION REQUIRED rather than let identity-agent discover the missing credential mid-dispatch -- four instances now (IMP-0048, IMP-0061, IMP-0105, this one) without the dispatching agent pre-checking  
  <sub>IMP-0528</sub>
- Before reporting a build SUCCESS or dispatching to pipeline-agent, run python3 scripts/verify-pipeline-config.py config/<slug>-pipeline.yml directly - it is cheap, standalone, and not currently a step in any build.yml, so nothing else will run it for you.  
  <sub>IMP-0175</sub>
- A provisioning identity working in one Dataverse environment is not evidence it works in another — each environment needs its own application user created for it. Before relying on any provisioning/dataverse/*.ps1 -Env <env> step in a pipeline config, confirm with a plain WhoAmI call that the identity is recognised in that specific org; 'token acquired' only proves Entra ID accepted the audience, never that Dataverse has provisioned the caller.  
  <sub>IMP-0146</sub>
- The real tenant id (735a23b1-97d7-4c81-85f7-35c50321138a, confirmed working against DEV via dev-scoring-settings.json) is a one-line fix for test-settings.json and prd-settings.json, and it was identified a full day before this entry without being applied. When a finding records a concrete unresolved value, verify the target file was actually edited before marking it APPLIED — do not let a knowledge-doc update stand in for the repo fix.  
  <sub>IMP-0145</sub>
- When an ADR changes the environment chain, the executable configs are the EASY half. Grep agents/, CLAUDE.md and every README for the old environment names in the same change — an agent following a stale instruction blocks on a gate keyword nobody is going to send, and reports it as waiting rather than as broken. Read the environments out of config/<slug>-pipeline.yml, never out of a numbered stage heading.  
  <sub>IMP-0056</sub>
- A certificate THUMBPRINT is a lookup key, not a credential. Any job running provisioning/**/*.ps1 must also import the .pfx into the runner's CurrentUser/My store and prove the thumbprint resolves WITH a private key before the first step that uses it. Use X509Store, never Import-PfxCertificate or Cert:\ — both are Windows-only (C-TECH-054).  
  <sub>IMP-0048</sub>
- Before packaging config/revitalise-grant-automation-build.yml, run `pwsh provisioning/dataverse/ensure-schema.ps1 -Env dev` to create REV_FinanceOnly live, then `fieldsecurityprofiles?$filter=name eq 'REV_FinanceOnly'&$select=fieldsecurityprofileid` and substitute the real id into Other/FieldSecurityProfiles.xml:627 and the matching <RootComponent> in Other/Solution.xml:252 (same procedure IMP-0166 used for REV Trustee's roleid). This is a pipeline-agent/reviewer live-write action, not a development-agent source fix and not something build-agent can perform.  
  <sub>IMP-0243</sub>
- When a dispatch instruction names a specific sub-agent fan-out and the work turns out to be one continuous chain of ground-truth-then-construct reasoning, STOP and either (a) do the fan-out anyway, passing the ground-truthed platform fact and the exact construction to write as the sub-agent's brief, or (b) if genuinely inseparable, say so explicitly in the gate output rather than silently completing the work in the parent session. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0498</sub>
- Before a new provisioning/*.ps1 script is considered done, run it through src/tests/provisioning/DataverseScripts.Tests.ps1's generic convention checks (Exit-Provisioning at the end, Write-CheckResult's CREATED/EXISTS/FAILED vocabulary, and a README inventory entry) rather than relying on a later, unrelated build's Pester run to surface it. Flagged for whoever owns WBS 6.5 (provisioning/dataverse/verify-access-test-identity.ps1) to fix; not actioned by this build-agent dispatch, which is scoped to WBS 0.4.  
  <sub>IMP-0244</sub>
- Before treating a pipeline.yml step marked 'DEAD AS DECLARED' as unrunnable, check whether the settings file or capability its blocked_on cites has since been added — dev-auditing-settings.json existed for a full day before anyone re-ran ensure-auditing.ps1 -Env dev against it, and the harness refusal it also cited (IMP-0084) did not reproduce when finally re-tried. A blocked_on note is a claim about a point in time, not a standing fact.  
  <sub>IMP-0222</sub>
- When a blocker trigger fires, process the UNREAD subset only. Run python3 scripts/verify-improvement-log.py --check FIRST and read its state breakdown: an entry in awaiting-approval already has a review document and needs the keyword sent against that document, never a second review of the same finding (IMP-0154). improvement-agent.md activation step 2 still says 'read every NEW entry', which was written when NEW meant unread and now costs a full strategic-tier pass over settled work.  
  <sub>IMP-0183</sub>
- The REV Trustee role ships with id {PENDING-ROLE-ID-REV-TRUSTEE} and is absent from Other/Solution.xml's <RootComponents>, so root-components-resolve is RED and the role will not deploy until the role is created in DEV, its real roleid read back with `roles?$filter=name eq 'REV Trustee'&$select=roleid`, substituted into both the role file and a new <RootComponent type="20">. Second instance of a known, documented placeholder left in place (IMP-0145 was tenantId). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0166</sub>
- config/models.yml declares NO escalation conditions for frontend-agent, even though ADR-003 puts a hand-authored React Code App in the palette - so the sub-agent owning the most novel artefact in the project defaults to standard tier while narrower sub-agents carry explicit escalation rules. When dispatching frontend-agent for Code App work, pass an explicit model override; and when an ADR adds an artefact type, re-read models.yml in the same change.  
  <sub>IMP-0162</sub>
- The provisioning identity can read and write Dataverse but CANNOT read Entra app registrations from this Mac - Connect-ProvisioningGraph succeeds and Get-MgApplication then fails with Authorization_RequestDenied. So provisioning/entra/*.ps1 cannot run here as things stand, and rev_IntakeAllowedClientId's value must come from the Entra portal or from ensure-intake-client.ps1 run under an identity that holds Application.ReadWrite.All with admin consent. A successful Graph connection proves the credential, never the permission. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0105</sub>
- When a blocked capability becomes available, grep every agent file and skill for the sentence that said it was blocked - not just the script and the agent that requested the fix. warranty-clock.py now reads Build Terms v1.0 from docs/Import/ and answers; commercial-agent.md and how-to-account-for-billable-time.md still say it refuses.  
  <sub>IMP-0092</sub>
- Filename CASE is part of the contract on every filesystem except the one you are probably using. Check `git ls-files` rather than `ls` when a file must be found by an exact name — `ls` on macOS shows you what you meant, `git ls-files` shows you what the runner will see.  
  <sub>IMP-0054</sub>


## Before you bill an hour, accept a phase, or report status

*13 lessons from 13 findings.*

- Billing basis is a reviewer decision, not an inference: delivered scope priced at the WBS estimate and reconstructed session time give answers tens of hours apart on the same month. scripts/deliverable-hours.py computes the first, scripts/reconstruct-worklog.py the second, and both print which basis they assume. Until an APPROVE BASELINE amends contract/delivery-parameters.json's estimating_rule, the repository holds both rules and verify-worklog.py will warn on any actual that equals an estimate.  
  <sub>IMP-0096</sub>
- WBS v0.5 totals 177-277h over 61 tasks; it is internally consistent and is the CUSTOMER-ACCEPTED specification. The agreement's total is unverified — 292 is the reviewer's recollection, not a figure read from the PDF. Do not quote a contracted total until it is read from the signed document. `brew install poppler` makes that document machine-readable and is the cheapest way to close this permanently.  
  <sub>IMP-0063</sub>
- Never restate contracted hours, fees, phase membership or dates in a repo document - cite the generated baseline. SDD section 10 said 106-160h over 7 automations against a signed 292h over 9, and every downstream document inherited it.  
  <sub>IMP-0029</sub>
- An aggregation key that never aggregates is invisible: it emits valid output and the only symptom is that the collapsed form never appears. Where a generator groups on a free-text field, print the merge count so a key that has gone inert says so -- 'N findings -> N groups' is the tell, and here the two figures have been equal for the whole life of the file while a header line labelled one of them 'distinct lessons'. Note also the second-order cost: the inert term sat FIRST in a sort key, which promoted the tiebreak below it into the real ranking function (IMP-0543). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0545</sub>
- A privilege named in a handoff carries a ROLE, and the role is the half that gets swapped in compression - verify both halves against the role XML before acting. Specifically on this project: prvWriterev_roundstatisticsrequest is deliberately live on REV Trustee (the trustee writes the statistics ask, REV Trustee.xml:252) and stale only on REV Service Automation; prvReadWorkflow is absent from REV Trustee source since 2026-08-27 and stale only in the live environment. Revoking the first from the trustee role would break Refresh Figures for every trustee. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0418</sub>
- Before marking a finding APPLIED because 'the target file already carries the rule', grep the file for the substance of the lesson, not just confirm the file exists. An APPLIED status is itself a claim (C-COM-005's rule, applied to this log) and this repository's own gates do not yet verify it — do so by hand until they do.  
  <sub>IMP-0140</sub>
- Two tasks whose evidence resolves to the same file are one delivered task and one unproven one. Report evidence collisions in derive-wbs-state.py: task 1.6's only proof is a grep inside task 1.2's deliverable, so it earns hours whenever 1.2 ships. Third instance of this class alongside 2.8, 8.2 and 6.5 — the fix belongs on the SHAPE of an evidence rule.  
  <sub>IMP-0099</sub>
- A task whose deliverable names a CLIENT act — sign-off, acceptance, walkthrough, demo — can never be evidenced by a document we authored. Point those rules at contract/acceptance/ or mark them `manual`; a grep of our own test report proves we tested, not that they accepted. Second instance of this class: task 2.8 alongside 8.2 and 6.5, so the fix is a rule about the SHAPE of an evidence rule, not another per-task correction.  
  <sub>IMP-0097</sub>
- A date read from a contract is a fact about the contract, not about delivery. Record the actual start separately and measure elapsed time from it: the agreement's kick-off was 2026-07-04, work began 2026-08-10, and using the former made every long-standing blocker read as 46 days old on a nine-day-old project. The same trap applies to milestone dates used as evidence that a phase began.  
  <sub>IMP-0073</sub>
- An evidence rule must be satisfiable only by the deliverable existing, never by a declaration that it will. A grep for a table name passes on a role privilege that forward-declares it; pair every grep with an existence check on the thing itself.  
  <sub>IMP-0067</sub>
- A work breakdown that reconciles against ITSELF is not thereby complete. When a computed total misses a stated one, ask what work is MISSING from the breakdown before concluding the documents disagree - here it was 20 hours of DocuSign platform selection and trialling, which is distinct from building the DocuSign workflow. WBS v0.5 needs a v0.6 carrying it; do not edit v0.5, it is the customer-accepted specification.  
  <sub>IMP-0064</sub>
- Propose actual hours at the moment the evidence exists - on each DEV deploy and in each dev summary - not at month end. The WBS shipped with Actual Hours and Delta columns and all 61 rows were still empty six weeks into a T&M engagement.  
  <sub>IMP-0032</sub>
- Resolve every incoming request to WBS task ids before routing, and take the next unit of work from the ready set over the WBS dependency graph, phase-ordered against contractual dates. Asking 'what next' in conversation built Phase 2 in August while Phase 1, due three weeks earlier, sat untouched.  
  <sub>IMP-0031</sub>


## Before you extend this system or accept a new kind of input

*16 lessons from 16 findings.*

- When a supplied design artefact is intake'd, enumerate its FULL directory tree (not just the folder the first read happened to land in) before scoping what gets converted -- a sibling folder can hold an app-specific reference implementation for the exact feature being built, as ui_kits/trustee-review-portal/ did here, sitting beside the generic components/ folder that got all the attention. Concretely: grep the supplied root for the feature's own name/screen names (here, 'trustee', 'RoundOverview', 'ApplicationDetail') before declaring the intake complete.  
  <sub>IMP-0510</sub>
- Never replace a mandatory activation step with an elective discovery affordance. IMP-0070 is the recorded cost of a rule that exists but sits in no activation sequence - an agent that knew the reporting rule and did not load the file - and agents/improvement-agent.md states the principle already: 'A rule in CLAUDE.md that appears in no activation sequence is a rule that depends on remembering.' Native Claude Code Skills are additive and safe to add ALONGSIDE the prose; the harm in WS-G is entirely in its removal half. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0554</sub>
- Every decision item in the 'What you need to decide' section follows a fixed template: **Problem/Issue** (max 1 sentence) · **Suggested fix** (max 1 sentence) · **What happens if you don't** (max 2 sentences) · a direct line-link to the source document for anyone who wants to read further. Separate each item with a horizontal rule. This is stricter than 'one bold question per block' and should replace it for this section.  
  <sub>IMP-0506</sub>
- scripts/verify-provisioning-step-convergence.py's step marker is `# ── <n>. <title> ────` with BOX-DRAWING U+2500 and a trailing rule — not the `# -- <n>. ` its own UNCLASSIFIABLE message and docstring show. Copy the shape from a script that already passes (ensure-schema.ps1's `# ── 1. Global option sets ────`) rather than from the gate's advice. And the general form, for anyone writing a gate: a remediation sentence that ASCII-flattens the exact token it demands is an instruction that cannot be followed — print the literal bytes, or point at a file that already has it right.  
  <sub>IMP-0450</sub>
- A supplied design or brand artefact can arrive anywhere in the tree, not only docs/Import/. Before designing against one, establish whether its directory is tracked, whether any build step reads it, and which agent owns it - 'Designsystem/' is read by no build step and was kept outside src/ by an architecture decision (ADR-034), not by any existing rule.  
  <sub>IMP-0384</sub>
- generate-known-failure-modes.py's stdout 'distinct lessons' counts every row; the digest header's counts only NEW and APPLIED, because a REJECTED finding must stop teaching. A one-line gap between the two figures is the REJECTED population - not staleness, and not a concurrent session. Do not spend a review paragraph on it.  
  <sub>IMP-0334</sub>
- Never write `Write-Output ("a {0}" -f $x) + "b"` across a line break — `-f` binds tighter than `+`, so PowerShell concatenates `"b"` to the RESULT of `("a {0}" -f $x)`'s own trailing fragment only when parenthesised that way, and the outer `Write-Output (...) + ...` shape sends the first piece to the pipeline and evaluates `+` on the cmdlet's return separately, splitting the message across two output lines with a bare `+` between them. Build the whole template with string `+` FIRST inside one set of outer parens, then apply `-f` to the concatenated whole: `(("a {0} " + "b") -f $x)`.  
  <sub>IMP-0142</sub>
- A notification a human must ACT on needs a FactSet and a button to the record - not <br/>-separated lines and the name of a view to find by hand. Build the deep link as <rev_GrantAdminAppUrl>&pagetype=entityrecord&etn=<table>&id=<guid from the trigger>; the record button matters more than the list button, because the reader is being told about ONE application. When one notification in a solution gets a card, check every OTHER notification in the same solution in the same change - the three here were authored together and only the one with nothing to open got fixed.  
  <sub>IMP-0130</sub>
- result('<scope>')[0] gives the scope's FIRST CHILD, not the action that failed, and for a nested scope its message is the useless wrapper 'An action failed. No dependent actions succeeded.' Filter result() for the child whose status is Failed, and when that child is itself a scope, call result() on the inner scope to reach the leaf. Prove any error-handling path by making the flow fail on purpose and reading what it logged - reasoning about an error expression is not testing it.  
  <sub>IMP-0109</sub>
- provisioning/README.md's status vocabulary has no REMOVED state, so a teardown script reports a completed deletion as CREATED. Read the resource NAME on the line, not the status word, when the script is a remove-*. If you add a removal script, say in its header which state you mapped to what - do not leave the reader to infer that CREATED means gone.  
  <sub>IMP-0102</sub>
- In a gate block, the headline number must be the number the human is approving. State the ladder explicitly - evidence span, plus lead-in, equals total session time, minus non-billable, equals BILLABLE FOR APPROVAL - and never reuse the word 'proposed' for two different quantities in the same block.  
  <sub>IMP-0095</sub>
- Load skills/how-to-report-to-the-reviewer.md BEFORE writing any multi-paragraph report, not after. It was established on 2026-08-19 after three rejected drafts and was then ignored the same day, because it is named in CLAUDE.md but absent from every agent's activation steps and checked by nothing.  
  <sub>IMP-0070</sub>
- If a function must be mockable from a test that INVOKES a script (rather than dot-sourcing it), the function must live in a .psm1 and be imported — a dot-sourced definition is re-created in the script's own scope and shadows the mock. When mocking a function that a module calls internally, Pester needs -ModuleName <module> to patch that module's session state.  
  <sub>IMP-0062</sub>
- Check that a file named in your Knowledge to Load section actually contains knowledge. All four of plan-agent's domain files are still [PLACEHOLDER] templates; the real domain knowledge for this project is in docs/plans/ (approved SDD), docs/architecture/ (approved TAD) and docs/Import/ (DPIA, RoPA, Data Governance). A slice SDD should cite those, and an agent authoring a feature with no parent SDD has no domain knowledge at all and will not be told so.  
  <sub>IMP-0034</sub>
- Every input surface must name the agent that owns it. docs/Import/ accepts any document but only plan-agent and architect-agent intake from it, so a commercial or operational source dropped there is silently unread. Give pm-agent a BASELINE INTAKE mode and add a commercial checklist to the intake skill before relying on a quote that lives in that folder.  
  <sub>IMP-0028</sub>
- A request to ADD a capability to this system has no route: lead-agent's routing table is delivery-only and improvement-agent's triggers are finding-only. Route capability requests to improvement-agent in capability mode, authorised by a design document in docs/improvements/, and do not hand-create agents/ or constraints/ files to work around it.  
  <sub>IMP-0027</sub>


## Capabilities established in earlier sessions

These are things that WORK and were once lost. Do not ask the reviewer to re-supply them.

*63 lessons from 63 findings.*

- The Dataverse Web API OMITS a null-valued column from a response body — $select names what you asked for, not what comes back — and under Set-StrictMode -Version Latest (which every provisioning script sets) reading that absent property is a TERMINATING error, not $null. Guard every optional-column read with ($response.PSObject.Properties.Name -contains 'col'), never a bare $response.col. And when mocking it in a test, make the fake OMIT the property rather than set it to $null: a null-valued fake passes while the real API throws, so the mock must reproduce the absence.  
  <sub>IMP-0435</sub>
- When a hand-rolled Code App data layer's generic-connector reads fail on org-url-null and the app's own already-generated per-table typed services are confirmed to compile and to use a structurally different (immune) resolution path, migrate the READ call sites to those services while leaving any write that depends on connector-operation headers (If-Match, etc.) on the low-level executeAsync -- this is mechanically a change to ONE file (the hand-rolled client wrapper) when that wrapper's public function signatures are kept stable, not a repository-wide refactor. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0227</sub>
- To verify a Power Apps Code App generated service's write semantics, read the installed @microsoft/power-apps package's own shipped source under node_modules/@microsoft/power-apps/dist/ for the exact pinned version (Data.types.d.ts for the public signature, the two DataOperationExecutor.js files, and runtimeDataClient.js's _createHeaders) rather than assuming symmetry with a hand-rolled connector-operation call. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0210</sub>
- When a Power Apps Code App's Dataverse connector fails with 'Invalid organization URL null provided', pass -u/--org-url explicitly to `pa app add data-source` (the environment's real org URL, readable from `pac auth list`) before escalating to Microsoft support -- do not rely on it resolving automatically from --connection-id/--environment-id, and do not expect pa connection list-datasets/list-tables to be fixable the same way, since neither takes an org-url flag at all.  
  <sub>IMP-0208</sub>
- A parent agent's FAILED notification (API spend limit or any other terminal error) does NOT mean its own sub-dispatches stopped — they were already launched and keep running independently, and their completions arrive as separate, later notifications. Before concluding an improvement-agent (or any agent that itself uses the Agent tool) batch did 'nothing', run ListAgents to see every child's status, and verify each touched file directly (compile/parse/selftest/run against real data) rather than trusting only the parent's last words. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0172</sub>
- NEVER sum a nullable Dataverse column with xpath(...,'sum(...)') unguarded: XPath 1.0 returns 0 over an empty node-set and NaN over any non-numeric leaf, NaN is not valid JSON, and one blank money cell therefore destroys the whole aggregate document. Filter the nulls OUT before projecting to XML (that filter's length() is also the measure's honest denominator - coercing a null to 0 while still counting the row biases the mean), and guard the empty case with if(empty(...), null, ...). Do not coerce; exclude.  
  <sub>IMP-0467</sub>
- xpath(xml(<string>),'sum(<path>)') is a FIRST-PARTY DOCUMENTED way to total a variable-length array in a cloud flow (Logic Apps expression-functions reference, X section, Example 7) - it is not an undocumented trick, and Logic Apps evaluates it with the .NET XPath library, so XPath 1.0 semantics govern. Having proved a function absent from the WDL math table, read the same reference's other sections before recording the alternatives as unverified.  
  <sub>IMP-0466</sub>
- A self-caught correctness bug worth recording alongside the capability: the first draft of the poll loop checked `computedOn !== null` alone to decide 'a fresh result is ready', which is wrong the instant a poll times out while an OLDER (but still non-null) computedOn sits on the row from a previous cycle -- that reads as fresh and would show a stale result as current. The fix threads an explicit isFresh flag out of the poll loop, set true only when a row's computedOn is confirmed newer than the timestamp THIS specific write produced, and every downstream decision (parse vs. pending vs. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0392</sub>
- In this app, a component test can prove which class KEY a component asked for and never that the stylesheet declares it or what it declares. The two halves must be split deliberately: assert the key name as a substring in the component test, and assert the rule's existence and content by reading the stylesheet off disk (theme.test.ts:266-329's technique). Never read a green class assertion as evidence that a style ships.  
  <sub>IMP-0386</sub>
- Never adopt a supplied palette or design system as AA-compliant without computing every pair yourself. The Revitalise design system's own tokens fail 4.5:1 on four text pairings, fail the 3:1 focus floor on three of its own six surfaces, and one of its form components removes the focus outline outright. The corrected values, every ratio and the five corrections are in the TAD SS8.4; the fix for the button ladder is to route it through the supplied 16-shade ramp rather than invent a darker pink, which is the same fix theme.ts:66-88 already made once.  
  <sub>IMP-0385</sub>
- Before treating a 'Cannot find module .../dist/data/multiSelectPicklistUtils' (or any @microsoft/power-apps/dist internal-import) failure in this app's test suite as a real defect, run `rm -rf node_modules/.vite` and re-run — vitest.config.ts's server.deps.inline already documents and fixes this exact class, and a stale dependency-optimization cache can reproduce the pre-fix symptom verbatim even when the fix is correctly in place. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0370</sub>
- After `pa app add flow --flow-id <id>`, before the next `pac code push`, check power.config.json's new connectionReferences entry for a `workflowDetails` member and delete it (keep id/displayName/dataSources only) -- pac 2.4.1's code-push PUT rejects it outright with HTTP 400 InvalidRequestContent naming `AppConnectionReference` as the type with no such member. Re-running `pa app add flow` or `pa app refresh data-source` later will rewrite the field back in, so this is a repeat-every-time step, not a one-off fix.  
  <sub>IMP-0355</sub>
- ensure-schema-helpers.psm1's 'decimal' attribute branch (DecimalAttributeMetadata, Precision/MinValue/MaxValue flat properties, no PrecisionSource) is confirmed working live in DEV as of 2026-08-25 - A-FIN-02 can be closed. rev_roundfinance's EntitySetName is rev_roundfinances (naive pluralisation), PrimaryIdAttribute rev_roundfinanceid - do not re-guess either for this table again.  
  <sub>IMP-0316</sub>
- pac code add-data-source embeds the current environment's real API Management gateway host as a bare OpenAPI host/basePath/primaryRuntimeUrl field in .power/schemas/<connector>/*.Schema.json - grep for a literal "host": key and for azure-apihub.net, not only https:// prefixed strings, when checking a Code App tree for hardcoded environment values. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0197</sub>
- PreToolUse hooks DO fire inside dispatched subagents, and a hooks block added to .claude/settings.json is picked up mid-session without a restart - both are undocumented and were established by live fixture on 2026-09-01. The hook stdin carries agent_id (present only inside a dispatch) and agent_type (the subagent definition name, e.g. 'build-agent'), so 'which agent' x 'which path' is expressible and is enforced by .claude/hooks/protect-system-rules.py. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0556</sub>
- A harness question about how dispatch, discovery or permissions actually behave can be answered by EXECUTION, not inference: 'claude -p --model haiku <probe prompt>' spawns a genuinely fresh session from a Bash call, and its prompt can dispatch a Task subagent, so both the top-level and the subagent path are directly measurable. Put a canary string in the artefact under test so the answer cannot be confabulated, and clean the probe up afterwards. This is the same 'execute it, do not read it' rule as IMP-0426, extended from scripts to the harness itself.  
  <sub>IMP-0555</sub>
- rev_setting key RoundStatisticsMoneyMeasureMinimumPopulation is k=5 by explicit reviewer risk decision (OQ-043, TAD S0.9.1) and is NOT a process-owner tunable like the FR-062 thresholds or RoundStatisticsStaleAfterSeconds beside it - lowering it releases money averages over smaller applicant groups and needs a reviewer decision, not a settings edit. Seed 5 in every environment: an absent row withholds the four measures, which is fail-safe but is not the approved behaviour, and a DEV/TST divergence would render the same round differently per environment.  
  <sub>IMP-0469</sub>
- When a Code App registers an entity set whose table does not exist live yet, the sanctioned response is `--allow ENTITY=REASON` on the `code-app-data-sources` step, with an owner and a clearing action in the reason string - NOT hand-authoring an entry in the generated dataSourcesInfo.ts (that fabricates platform-assigned metadata, C-TECH-051) and NOT deleting the step (its defect is invisible below V4 because every local check passes with a mocked SDK). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0417</sub>
- To read a LIVE flow definition (or any solution component) from this Mac, use `pac solution export` + `pac solution unpack` against the active pac profile - read-only, unrefused under Auto Mode, no cert or keychain call, and it produces the same file shape as src/solutions/ so a live-versus-source diff is a plain file comparison. Do NOT reach for `pac env fetch` for workflow.clientdata: it renders a fixed-width table and truncates the column, and pac 2.4.1 has no --dataFile flag. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0409</sub>
- Dataverse column-level WRITE control exists and is already used in this solution: FieldPermission carries CanRead, CanUpdate and CanCreate (Other/FieldSecurityProfiles.xml:112-114) and ensure-schema.ps1 writes all three. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0403</sub>

> **43 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`platform-fact-groundtruthed`** (×15): IMP-0261, IMP-0295, IMP-0306, IMP-0317, IMP-0354, IMP-0373 (+9 earlier — see appendix)
>   · **`learning-substrate-destroyed`** (×6): IMP-0022, IMP-0103, IMP-0118, IMP-0125, IMP-0126, IMP-0213
>   · **`platform-contract-guessed-not-groundtruthed`** (×6): IMP-0044, IMP-0068, IMP-0128, IMP-0135, IMP-0199, IMP-0216
>   · **`harness-blocks-destructive-call`** (×3): IMP-0040, IMP-0220, IMP-0314
>   · **`change-order-sizing-without-precedent`** (×2): IMP-0278, IMP-0288
>   · **`dispatched-agent-stalls-silently`** (×2): IMP-0291, IMP-0357
>   · **`credential-not-on-the-machine-that-needs-it`** (×1): IMP-0061
>   · **`declared-knowledge-source-is-empty`** (×1): IMP-0058
>   · **`declared-policy-not-mechanically-enforced`** (×1): IMP-0143
>   · **`existing-shared-class-satisfies-new-requirement`** (×1): IMP-0311
>   · **`foreground-write-not-refused`** (×1): IMP-0173
>   · **`import-does-not-touch-what-source-omits`** (×1): IMP-0086
>   · **`live-verification-capability`** (×1): IMP-0083
>   · **`no-assertion-on-shipped-content`** (×1): IMP-0127
>   · **`output-shape-defeats-the-reader`** (×1): IMP-0059


## Unrouted — no section assigned

> These findings' `class_instance_of` values are missing from the routing table in `scripts/generate-known-failure-modes.py`. Add them, so the lesson reaches the agent at the moment it applies.

*244 lessons from 244 findings.*

- A CSS comment claiming a specific resulting layout (e.g. 'lands at N columns') is not evidence the layout achieves it - grid track counts from auto-fit/auto-fill must be solved algebraically against the container widths the app is actually used at, or capped explicitly (e.g. via a container-relative max() expression), and a regression test should assert the resulting column count at representative widths.  
  <sub>IMP-0526</sub>
- A dispatch death (spend-limit, credit exhaustion, or any other external kill) can occur AFTER real live writes and BEFORE that dispatch appends its own end-of-stage pipeline.log entry, because pipeline-agent logs once per stage rather than once per operation. This means log absence proves only 'no entry was written', never 'no write was attempted' -- the two are the same signal today. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0484</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0490`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- Unlike IMP-0290 (rejected: that finding never actually checked routing.log and the escalation had in fact been applied), this is a genuine, verified instance of the same class -- confirmed by reading the exact ROUTED_TO line for this dispatch (routing.log's last line) and finding it silent on escalation where 4 sibling dispatches on the identical TAD are explicit. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0398</sub>
- Before extending a flow's computation logic against an approved TAD, grep the Code App's own dataverse client for how it actually expects to reach that flow today, not only what the TAD says -- `git status` on the feature's whole surface (app + entities + provisioning), not just the one file named in the handoff, would have shown this redesign was already three files deep and uncommitted. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0377</sub>
- (1) Do not re-attempt binding shared_logicflows to this app again without either a genuinely new variable to test (e.g. the flow rebuilt with a PowerAppsV2 trigger, never yet tried) or a Microsoft support ticket confirming the mechanism -- a third identical attempt would be the discouraged 'same scale of work, expect the same failure' pattern. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0365</sub>
- Every newly-created Dataverse table needs its own ensure-auditing.ps1 -Env <env> pass before any row is written to it - creating the table (ensure-schema.ps1) and enabling its audit switch (ensure-auditing.ps1) are two separate live actions, and a table can sit live and unaudited indefinitely with every source-side gate green, exactly as rev_review did in the IMP-0085/IMP-0178 precedent, until someone queries IsAuditEnabled directly.  
  <sub>IMP-0271</sub>
- A handoff or dev summary's claim that a live provisioning re-run 'succeeded after both fixes' is a claim, not a result, especially when two independent defects were fixed in the same source revision - re-query EACH defect's own revisit_when condition live and separately, never infer that one succeeding means the other did too.  
  <sub>IMP-0270</sub>
- Before telling the reviewer their V4 access-test identity is ready, re-query BOTH axes of the column-security profile's membership live (fieldsecurityprofiles(<id>)/systemuserprofiles AND /teamprofiles) and confirm the trustee test identity is NOT among either — a prior dispatch's request to add 'one identity' as the positive control does not name WHICH one, and a human satisfying it with the trustee's own account silently converts the negative control into a false positive. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0228</sub>
- Before deploying any build/artifacts/<slug>-<date>-<n>/ directory, grep logs/build.log for that exact directory name and confirm the directory itself contains manifest.json with status SUCCESS. An artifact directory existing on disk, even with zips and test-results present, is not evidence it went through build-agent's managed process or was approved by test-agent — check both before Stage 1, not after a failed or ad-hoc deploy is already underway.  
  <sub>IMP-0582</sub>
- A build-step warning whose TEXT is stable across revisions (e.g. Vite's 'Some chunks are larger than 500 kB') can still be a NEW, untriaged warning if the underlying MAGNITUDE has changed - re-check the actual printed figures against the Dev Summary's cited numbers every build, not just the warning's wording. Adding a charting library (recharts) to a Code App is exactly the kind of change that inflates a bundle silently past a previously-accepted rationale.  
  <sub>IMP-0573</sub>
- Before reporting an improvement-log entry's status as APPLIED with a verified exit 0, run scripts/verify-improvement-log.py --check (the exact flag build-agent's improvement-log-check step uses) — not a bare invocation — and confirm the entry carries an evidence_grep object naming the file and needle that prove the applied_by change, per skills/how-to-log-an-improvement.md's evidence_grep section.  
  <sub>IMP-0536</sub>
- Before appending prose to an existing Power Automate action/trigger/parameter description, check its CURRENT length against the 256-char designer save limit first (scripts/verify-field-length-limits.py) -- an already-long description has less headroom than a fresh one, and this is the mechanism by which a correctly-enforced gate still blocks a later, unrelated build.  
  <sub>IMP-0531</sub>
  <br><sub>**⚠ CORRECTED by `IMP-0532`** — a later finding contradicts this lesson. Read both before acting on it; the marker does not decide which is right.</sub>
- Before dispatching build-agent while any improvement-log finding is in state 'awaiting-approval' at blocker severity, re-run 'python3 scripts/verify-improvement-log.py --check' and read its own exit code -- a finding being 'already routed to a review document' does not exempt it from improvement-log-check (build.yml step 3, HARD), which fails by design until the reviewer answers APPROVE IMPROVEMENTS on that review. Do not infer a build gate's behaviour from a routing note; run the gate.  
  <sub>IMP-0527</sub>
- Before shipping a new rev_setting row or a MaxLength change, grep src/tests/ for a hardcoded key-count or padded-string-length assertion coupled to the changed file, and update or (better) re-derive it in the same change — do not let build-agent discover it at the unit-tests step, 40+ steps into a build.  
  <sub>IMP-0521</sub>
- A cross-document `#Lnnn` line-link is a hand-maintained pointer into a file neither the writer nor a later editor of that file is prompted to keep in sync — the second citation in the same plan document to drift this way (after IMP-0389/IMP-0430's #L363/#L924). Per the gate's own remediation and IMP-0389's lesson, drop the line number and cite the section identifier alone (`[TAD §3.5]` with no `#Lnnn`), or re-grep the heading's current line before every commit that touches either file.  
  <sub>IMP-0518</sub>
- A warning already triaged with full rationale in one feature's Dev Summary is NOT thereby triaged for a later feature that re-runs the same build step and reproduces it — C-TECH-055 is checked against the CURRENT feature's own document, so every feature's Dev Summary needs its own row (citing the earlier document's rationale is fine, omitting the row is not). **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0499</sub>
- A register row's OPEN/CLOSED state must be updated everywhere in the same document that later states closure, not only in the section a later pass happened to touch. verify-assumption-register.py (build step 'assumption-register', HARD) will halt the build on the first stale row found — strike through docs/development/trustee-portal-visual-refresh-dev-summary.md line 1884's A-RES-1 row to CLOSED (E1) before the next build attempt.  
  <sub>IMP-0493</sub>
- In verify-tad-coverage.py, a status-free Compose is a FRAGMENT, not a non-ok document: attribute it to the action(s) that interpolate outputs('<name>') from it, transitively, with a cycle guard. Fixed in flow_null_response_keys. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0461</sub>
- Before wiring a new gate as a blocking build step, RUN IT against the current tree and read the exit code — not only its --selftest. A gate that is correct and red is still a halted build, and pre-existing debt is not the introducing dispatch's to fix (C-COM-002). IMP-0320 is the precedent to follow: build the gate, measure it, and where it is red over work the dispatch does not own, either leave it unwired with the reason recorded, or give it a declared, owned, dated baseline whose semantics are known-exceptions.json's — an exception suppresses the FAIL, never the report. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0439</sub>
- Before designing to an approved requirement that says an app should READ a column, check whether that column is in a field security profile AND whether a build gate forbids referencing it - no-secured-columns-in-code-app fails on any secured column the Code App names, whatever the intent. And never accept 'column security will withhold it' as a safety argument without naming EVERY persona that opens the surface: this app is read by the process owner as well as by trustees, and she IS a profile member, so the same query returns real values for her. **[…]** <sub>*truncated — full text in `known-failure-modes-appendix.md`*</sub>  
  <sub>IMP-0371</sub>

> **224 further lesson(s) in this section are not shown** (cap: 20), indexed below by class so you can see WHAT KIND of lesson you are not being shown — not only how many. Read one with `python3 scripts/generate-known-failure-modes.py --subject <term>`, which prints every matching lesson rendered or capped; read the full text of every capped lesson in `known-failure-modes-appendix.md`; or read them all in `logs/improvement-log.jsonl`.
>   · **`finding-diagnosis-unverified`** (×28): IMP-0553, IMP-0560, IMP-0562, IMP-0564, IMP-0570, IMP-0571 (+22 earlier — see appendix)
>   · **`gate-reassures-wrongly`** (×26): IMP-0452, IMP-0457, IMP-0478, IMP-0483, IMP-0497, IMP-0565 (+20 earlier — see appendix)
>   · **`declared-policy-not-mechanically-enforced`** (×25): IMP-0480, IMP-0501, IMP-0548, IMP-0567, IMP-0572, IMP-0574 (+19 earlier — see appendix)
>   · **`approved-document-internally-inconsistent`** (×23): IMP-0459, IMP-0465, IMP-0468, IMP-0481, IMP-0482, IMP-0492 (+17 earlier — see appendix)
>   · **`hand-maintained-count-drifts-from-source`** (×21): IMP-0474, IMP-0522, IMP-0529, IMP-0533, IMP-0534, IMP-0549 (+15 earlier — see appendix)
>   · **`platform-state-divergence`** (×11): IMP-0372, IMP-0407, IMP-0408, IMP-0449, IMP-0489, IMP-0514 (+5 earlier — see appendix)
>   · **`test-assumed-name-is-solution-unique`** (×6): IMP-0234, IMP-0236, IMP-0237, IMP-0240, IMP-0247, IMP-0269
>   · **`untriaged-tool-warning`** (×5): IMP-0177, IMP-0214, IMP-0323, IMP-0393, IMP-0411
>   · **`identifier-namespace-collision-across-documents`** (×4): IMP-0327, IMP-0336, IMP-0339, IMP-0576
>   · **`requirement-names-data-the-solution-cannot-supply`** (×4): IMP-0293, IMP-0296, IMP-0326, IMP-0463
>   · **`wrong-artefact-cited-as-evidence`** (×4): IMP-0305, IMP-0341, IMP-0429, IMP-0552
>   · **`concurrent-session-same-file-write`** (×3): IMP-0539, IMP-0541, IMP-0547
>   · **`dispatched-agent-stalls-silently`** (×3): IMP-0300, IMP-0520, IMP-0537
>   · **`gate-invocation-omits-required-arg`** (×3): IMP-0470, IMP-0479, IMP-0494
>   · **`incorporated-document-version-mismatch`** (×3): IMP-0071, IMP-0297, IMP-0381
>   · **`digest-cap-hides-a-whole-subject-area`** (×2): IMP-0383, IMP-0543
>   · **`dispatch-brief-asserts-unverified-fact`** (×2): IMP-0530, IMP-0559
>   · **`stale-claim-contradicting-rechecked-source`** (×2): IMP-0524, IMP-0575
>   · **`tad-narrative-omits-an-already-existing-column`** (×2): IMP-0337, IMP-0338
>   · **`test-asserts-the-defect`** (×2): IMP-0111, IMP-0138
>   · **`a design document specifying an implementation detail precisely enough to be wrong, where the reviewer's approval covers the intent and not the annotation`** (×1): IMP-0387
>   · **`acceptance-happens-without-anyone-recording-it`** (×1): IMP-0072
>   · **`ambiguous-dispatch-instruction`** (×1): IMP-0578
>   · **`assumption-register-precondition-crossed-mid-register`** (×1): IMP-0219
>   · **`bulk-identifier-remap-misses-compound-forms`** (×1): IMP-0342
>   · **`column-name-substring-false-positive`** (×1): IMP-0321
>   · **`concurrent-pipeline-dispatch-mislabels-shared-operation-id`** (×1): IMP-0538
>   · **`declared-contract-unenforced`** (×1): IMP-0500
>   · **`dispatch-instruction-contradicts-an-approved-document`** (×1): IMP-0464
>   · **`escalation-trigger-conflates-request-and-document-state`** (×1): IMP-0280
>   · **`evidence-rule-targets-a-superseded-implementation-path`** (×1): IMP-0179
>   · **`exception-not-carried-into-the-arithmetic`** (×1): IMP-0098
>   · **`file-header-claim-not-true-of-every-member`** (×1): IMP-0579
>   · **`fix-keyed-on-the-symptom-not-the-condition`** (×1): IMP-0580
>   · **`flag-semantics-not-what-its-name-implies`** (×1): IMP-0583
>   · **`gate-blocks-on-unrelated-precondition`** (×1): IMP-0519
>   · **`gate-cannot-be-talked-around`** (×1): IMP-0119
>   · **`gate-classifier-assumes-fixed-verb-set`** (×1): IMP-0274
>   · **`hand-authored-tool-crashes-on-documented-argument`** (×1): IMP-0523
>   · **`hard-gate-red-on-pre-existing-debt`** (×1): IMP-0477
>   · **`helper-assumes-singleton-component`** (×1): IMP-0238
>   · **`hosted-service-unresponsive`** (×1): IMP-0215
>   · **`measurement-artefact-read-as-a-finding`** (×1): IMP-0163
>   · **`open-question-answerable-from-repo`** (×1): IMP-0284
>   · **`parallel-safety-table-computed-from-an-unresolved-mechanism`** (×1): IMP-0546
>   · **`proposed-control-overridden-by-risk-acceptance`** (×1): IMP-0289
>   · **`retired-constraint-premise-expired`** (×1): IMP-0294
>   · **`reusable-font-self-hosting-technique`** (×1): IMP-0513
>   · **`revision-header-committed-ahead-of-implementation`** (×1): IMP-0525
>   · **`routed-work-not-reverified-at-apply-time`** (×1): IMP-0517
>   · **`rule-written-where-the-generator-drops-it`** (×1): IMP-0310
>   · **`safety-bypass-proposed`** (×1): IMP-0264
>   · **`schema-fact-read-from-the-wrong-artefact`** (×1): IMP-0292
>   · **`session-lacks-live-credentials`** (×1): IMP-0512
>   · **`single-instance-assumed-in-array-property`** (×1): IMP-0239
>   · **`source-reader-plurality-false-positive`** (×1): IMP-0268
>   · **`spec-field-list-not-verified-against-implementation`** (×1): IMP-0279
>   · **`stale-deferral-uncaught-across-sessions`** (×1): IMP-0366
>   · **`tool-installed-but-not-on-path`** (×1): IMP-0200
>   · **`two-recorded-lessons-contradict-each-other`** (×1): IMP-0460
>   · **`unquoted-artefact`** (×1): IMP-0066
>   · **`vendor-plugin-reference-broken`** (×1): IMP-0203
>   · **`vendor-reference-implementation-not-surveyed`** (×1): IMP-0201
>   · **`windows-only-cmdlet-dependency`** (×1): IMP-0186
>   · **`worktree-isolation-base-predates-working-tree`** (×1): IMP-0400


---

## What this file cannot tell you

It records defects that have been **found**. The classes with the highest counts are the ones
this project has learned to look for — they are not necessarily the ones most likely to bite
next. A lesson's absence here is not evidence of safety; it is evidence that nobody has been
caught by it yet and written it down.

Full analysis of every entry, including why each was invisible to the gates that existed at
the time: `docs/improvements/2026-08-17-failure-analysis-and-self-learning-design.md`.
