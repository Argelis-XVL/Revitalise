# Improvement Review 22 — 2026-08-24

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 1 `NEW` (`unread`) → 1 cluster
**Trigger:** reviewer request, after a human correction of lead-agent output — [IMP-0253](../../logs/improvement-log.jsonl#L250), per [WORKFLOW.md → Processing triggers](../../agents/WORKFLOW.md#L207)
**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPROVED and APPLIED 2026-08-24** by the reviewer (Xander Lykopoulos). Changes 1–4 as drafted; change 5 applied in corrected form — its figure was wrong and its method was rejected. See section 8.
**Scope note:** the second review dated 2026-08-24. The first, [Review 21](./2026-08-24-improvement-review.md), is parked at its own gate on a different finding and is untouched here.
**WBS:** system work, not billable ([C-COM-002](../../constraints/commercial/commercial-constraints.md))

---

## Summary

The reviewer was handed PowerShell syntax to type into a zsh terminal, and it failed in a way that pointed at a missing file rather than at the wrong shell. The cause is one mislabelled code block in [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L134): the page lists both credentials the script needs and shows the command that needs them, but tags that command as PowerShell, so a reader primes on `$env:` and never sees `export`.

Five edits are proposed, no new constraints. One is a read-path fix — this lesson is *already* in the generated digest and invisible, sitting in a hidden overflow of 33 entries. The fifth is unrelated to the shell: performing this review's own retirement check turned up two rule files describing a repository that no longer exists.

---

## 1. Regression check — did the last review's changes work?

[Review 20](./2026-08-23-improvement-review-8.md) was approved and applied on 2026-08-23. Six changes, audited against every finding logged since.

| Prior change | Applied | Class it targeted | Recurred since? | Verdict |
|---|---|---|---|---|
| Coverage gate fails on a secured primary name, warns on a secured currency column — [verify-field-security-coverage.py L213](../../scripts/verify-field-security-coverage.py#L213), [L222](../../scripts/verify-field-security-coverage.py#L222) | 2026-08-23 | a column marked confidential that the platform cannot actually secure | NO | **Working.** No finding in that class since |
| [C-TECH-070](../../constraints/technology/technology-constraints.md#L141) — the rule the gate above enforces | 2026-08-23 | same | NO | **Working** |
| Refusal protocol: no command-line verb exists for this operation class — [pipeline-agent.md L118](../../agents/pipeline-agent.md#L118), [L129](../../agents/pipeline-agent.md#L129) | 2026-08-23 | a live write refused by the session's own safety classifier | **YES** — one new instance, the eighth | **Prose, and the recurrence was expected.** See below |
| A finding about a refused live operation must record the session conditions — [check_refusal_context](../../scripts/verify-improvement-log.py#L587) | 2026-08-23 | same class, the *diagnosis* half | **YES**, and **the gate did its job** | **Working — measurably.** See below |
| A closed finding must account for every path its proposed change named — [check_multi_target_closure](../../scripts/verify-improvement-log.py#L621) | 2026-08-23 | closing a finding on a subset of what it named | NO | **Working** |
| Digest routing made visible — [generate-known-failure-modes.py L264](../../scripts/generate-known-failure-modes.py#L264) | 2026-08-23 | a lesson that never reaches its reader | **YES, in a new form** | **Partly working.** Change 4 below is the consequence |

**The refusal-context gate is the one clear win, and it is worth stating precisely.** Review 20 wrote that gate so *"the eighth instance is diagnostic where the first seven were not"*. The eighth instance has since been logged, and it carries the field, populated on both axes: harness mode `auto`, dispatch `lead-foreground`. Seven prior instances argued about which variable mattered and recorded neither; the eighth records both because a gate refused the entry otherwise. That is a prose problem fixed by making the data mandatory, and it worked on first contact.

I checked that one field mechanically and read nothing else of that finding — its analysis belongs to the review already parked on it.

**The prose half of the same class recurred, as review 20 predicted it would.** Steps 3a and 4 are still prose and still guesses about a variable nobody has isolated. Review 20 said so itself and declined to escalate further. Nothing in this review changes that, and no new evidence has arrived to decide it.

---

## 2. Clusters and promotion decisions

```
CLUSTER: instruction-untested-in-target-shell  (x1: IMP-0253)
Altitude:   INSTANCE — first member of a new class, severity friction. The promotion skill's
            §4 rule for a one-member class applies: a knowledge line, not a constraint.
Ladder row: "One instance, but the cause is general and a human needs to know it"
              → knowledge/  (changes 1 and 2)
            "An agent had the information and still did the wrong thing"
              → agents/     (change 3)
            "The system's own memory failed"
              → read path   (change 4)
Becomes:    the four changes in §3
Retires:    nothing — see §4
Cites:      IMP-0253
Residual:   THE GATE THIS DOES NOT BUILD. The defect occurred in chat prose, which no script
            can inspect. I scanned every tracked .md for the on-disk shape of the same
            mistake — a PowerShell-labelled fence whose body is really a shell command — and
            found exactly ONE, the one that caused this. One instance is an instance patch,
            not a gate (promotion skill §2: the altitude rule binds on the SECOND instance).
            So this is deliberately left ungated. If a second mislabelled fence appears, the
            generalisation is a ~30-line checker over fence labels, and it should be built
            then rather than now.
            Also uncovered: nothing verifies that the shell named in a hand-off is the shell
            the reviewer is actually using. Change 3 states it as a fact; a future machine
            change would silently falsify it.
```

### Why the finding's own proposed fix was not followed

The finding proposed editing [testing-tools.md L170–174](../../knowledge/technology/testing-tools.md#L170), on the grounds that no file pairs the `export` syntax with the `pwsh -File` invocation. That diagnosis is close but points at the wrong page, and the difference decides where the fix belongs.

[build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L61) already carries **both halves on one page**: the two credentials are named in its variable table at [L70–71](../../knowledge/technology/build-and-deploy.md#L70), and the exact command that consumes them is at [L135](../../knowledge/technology/build-and-deploy.md#L135), under *First Import Into a New Environment*. Nothing joins them, and the block at [L134](../../knowledge/technology/build-and-deploy.md#L134) is fenced as ` ```powershell ` while containing a command you type into a **shell**. A reader who trusts that label concludes they are in a PowerShell session — which is precisely the wrong conclusion, and precisely the one that was drawn.

The correct `export` form does exist in the repository, in a dated handover at [line 118](../../docs/handovers/2026-08-21-trustee-portal-approval-session-handover.md#L118). It is in no activation sequence and no knowledge file, so nothing reads it.

### The mechanism, reproduced

Worth recording exactly, because the error message actively misleads:

```
$ zsh -c "\$env:PROVISION_APP_ID = 'abc123'"
zsh:1: no such file or directory: /…/Repository/RevitaliseROVISION_APP_ID
```

`:P` is zsh's realpath expansion modifier. `$env:P…` therefore expands the empty variable `env` to the working directory and glues the rest of the name on, so the error names a **path that nearly matches the repo root**. Both credentials begin with `P`, so both fail this way. Anyone reading that output looks for a missing directory; the actual problem is that the line is PowerShell.

---

## 3. Proposed changes

| # | Type | Target | Change | Cites | Mechanically verifiable? |
|---|---|---|---|---|---|
| 1 | knowledge | [build-and-deploy.md L132–136](../../knowledge/technology/build-and-deploy.md#L132) | Relabel the fence `bash`, fold the two `export` lines into the block that needs them, and record the zsh mis-parse so the misleading error is recognisable. One line at [L74](../../knowledge/technology/build-and-deploy.md#L74) noting these are set by hand locally, not only as CI secrets | IMP-0253 | Partly — `bash -n` parses the block; the prose does not |
| 2 | knowledge | [testing-tools.md after L180](../../knowledge/technology/testing-tools.md#L179) | One paragraph separating the two patterns: the `$auth` example is PowerShell *inside* a `pwsh` session; running a `provisioning/**` script means exporting in the outer shell and invoking `pwsh` as a subprocess. Points at change 1 as the canonical block | IMP-0253 | NO — instruction text |
| 3 | agent | [pipeline-agent.md step 5, L148–154](../../agents/pipeline-agent.md#L148) | The `REVIEWER ACTION REQUIRED` template gains a `Shell:` line, and a paragraph forbidding `$env:VAR = '…'` in any block handed to a human. Makes every future hand-off shell-correct by construction rather than assembled per occurrence | IMP-0253 | NO — instruction text |
| 4 | script | [generate-known-failure-modes.py L107–110](../../scripts/generate-known-failure-modes.py#L107) | Route this class into `Operating constraints of this environment`, alongside `repo-path-contains-spaces` — the same shape of lesson (a local fact that breaks a command assumed portable) | IMP-0253 | YES — regenerate and confirm the lesson renders in that section |
| 5 | agent + skill | [improvement-agent.md L160](../../agents/improvement-agent.md#L160), [how-to-promote-a-finding.md L97](../../skills/how-to-promote-a-finding.md#L97) | Correct a false statement that both files make about this repository. Found by obeying them — see below | new finding, logged on approval | YES — the corrected claim is a `grep -c` |

**Constraint budget: 0 of 3 used.**

No constraint is proposed, and that is a decision rather than an omission. This is one `friction` finding, the first in its class. The nearest existing rule, [C-TECH-054](../../constraints/technology/technology-constraints.md#L109), already governs the machine-facing version of this problem — a script assuming an OS it will not run on — and it is HARD and verified by executing scripts on the CI runner. What it does not cover is a command an agent *types at a human*, which no test suite can execute. Writing a constraint whose `Verify By` cannot name a command would produce a comment, which [anti-bloat limit 4](../../agents/improvement-agent.md#L164) forbids.

### Change 1, concretely

Replacing [L132–136](../../knowledge/technology/build-and-deploy.md#L132):

````
**1. Create the schema the import cannot create** (`C-TECH-050`)

```bash
export PROVISION_APP_ID="<app id>"
export PROVISION_CERT_THUMBPRINT="<thumbprint>"
pwsh -NoProfile -File provisioning/dataverse/ensure-schema.ps1 -Env <env>
```

Both values are read from the **outer shell**, which on this project's machines is **zsh**;
the `pwsh` subprocess inherits them normally. Neither is a secret — an app id is an
identifier and a thumbprint is a lookup key, not a credential (`IMP-0048`).

**Never write these as `$env:VAR = '…'` for someone to paste into a terminal.** That is
PowerShell, valid only *inside* a `pwsh` session. In zsh, `:P` is the realpath expansion
modifier, so `$env:PROVISION_APP_ID` expands to the working directory with
`ROVISION_APP_ID` appended and fails as `no such file or directory: /…/RevitaliseROVISION_APP_ID`.
The variable is never set and the error names a path, which sends the reader hunting for a
missing file instead of a wrong shell (`IMP-0253`).
````

### Change 3, concretely

The template at [L150–154](../../agents/pipeline-agent.md#L150) gains one line:

```
REVIEWER ACTION REQUIRED  |  feature:<slug>  |  env:<env>
Shell: zsh — the reviewer's own terminal, NOT a pwsh session
<what must change, in the reviewer's terms — portal path or the exact call>
Verify afterwards with: <the query that proves it, not the portal's confirmation>
```

followed by:

> **Everything in this block is pasted into the reviewer's own terminal.** That is zsh — not a `pwsh` session, and not an agent's Bash tool. Environment variables are therefore set with `export VAR=value`, and a PowerShell script is invoked as a subprocess: `pwsh -NoProfile -File <script> -Env <env>`. Never emit `$env:VAR = '…'` here; in zsh it mis-parses into an error naming a garbled path, which hides the real cause (`IMP-0253`). For the two provisioning credentials, the ready-made block is in `knowledge/technology/build-and-deploy.md` → *First Import Into a New Environment*.

---

## 4. Retirements

> Retirement check performed: 77 constraints reviewed across the three files (51 technology, 16 domain, 10 commercial); **none currently redundant**, and none superseded by anything in this review.

Nothing here replaces an existing gate — this review adds no gate. [C-TECH-054](../../constraints/technology/technology-constraints.md#L109) was the one row worth examining, since it is the closest in subject, and it stays: it governs scripts executing on a runner's OS, is enforced by executing them there, and is untouched by a documentation fix about human-facing commands.

### Change 5: the retirement rule describes a repository that no longer exists

Performing this check is what found it. Both files that order it state the same two things, and both are false:

> *"`constraints/README.md` has a Retired Constraints table; after 57 constraints it had zero rows."* — [improvement-agent.md L160](../../agents/improvement-agent.md#L160), and the same claim at [how-to-promote-a-finding.md L97](../../skills/how-to-promote-a-finding.md#L97)

There is **no** Retired Constraints table in [constraints/README.md](../../constraints/README.md) — `grep -c "Retired Constraints"` returns 0. Retirement is done in place in the constraint files themselves, per the procedure at [README.md L136–144](../../constraints/README.md#L136). And the count is not zero: **ten** constraints carry `status: retired`, against 77 live rows rather than 57 — [C-TECH-005](../../constraints/technology/technology-constraints.md#L38), [011](../../constraints/technology/technology-constraints.md#L49), [012](../../constraints/technology/technology-constraints.md#L50), [013](../../constraints/technology/technology-constraints.md#L51), [020](../../constraints/technology/technology-constraints.md#L60), [021](../../constraints/technology/technology-constraints.md#L61), [022](../../constraints/technology/technology-constraints.md#L62), [023](../../constraints/technology/technology-constraints.md#L63), [031](../../constraints/technology/technology-constraints.md#L72), [049](../../constraints/technology/technology-constraints.md#L91).

**This draft first said seven, and the reviewer caught it.** The cause is worth recording, because it is the same defect one level down: the first count came from `grep -rn retired constraints/*/*.md | head -10`, and the `head` cap silently truncated an 11-line result, of which 7 were retired rows. A truncated read of a source of truth is not ground truth — the lesson [IMP-0037](../../logs/improvement-log.jsonl) records — and a capped pipe reports a smaller number with no indication anything was cut. The reviewer's own arithmetic also reconciles it independently: 51 live technology rows out of 61 total means ten retired, not seven.

The correct derivation anchors on the struck-through row shape, not on the phrase:

```bash
grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l   # 10
grep -rc  'status: retired' constraints/*/*.md             # 11 — WRONG
```

The naive form returns one too many because [domain-constraints.md L13](../../constraints/domain/domain-constraints.md#L13) explains the convention in a sentence that mentions `status: retired` without being a retired row. I verified the anchored form has no false positives in the other direction either: all 10 of its matches also carry `status: retired`. The live count of 77 is independently corroborated by [verify-constraint-verifiers.py](../../scripts/verify-constraint-verifiers.py), which reports "77 active constraint row(s)" from its own parse.

This matters more than a stale number. An agent sent to find a table that does not exist learns that the instruction is unreliable, and the cheapest response to an unreliable instruction is to stop taking it literally. Both sentences are rewritten to point at the real mechanism and to cite the count as of a date, so the next drift is visible rather than silent.

A finding is appended for this on approval, in the same commit as the digest regeneration — one moment, not two, per the lesson that a log and a digest committed separately record two different states.

---

## 5. Findings left unprocessed

No silent caps. The queue held 15 `NEW` entries when this review opened and holds 17 now; I read one.

| Finding | State | Why not processed here | Revisit when |
|---|---|---|---|
| [IMP-0252](../../logs/improvement-log.jsonl#L249) | `awaiting-approval` | A review already processed it and is parked at its own gate — [Review 21](./2026-08-24-improvement-review.md). Re-deriving it is the defect `IMP-0183` records. The remedy is a keyword against that document, not a session | the reviewer answers that gate |
| IMP-0254, IMP-0255 | `unread` | **Arrived mid-review**, at 09:40, from a development-agent session that was still running. Both are `rework`, neither is a `blocker`, so no immediate-processing trigger fires. Reviewing findings while the session producing them is still open means reviewing a moving target | the next review, or immediately if either is re-logged as a blocker |
| 13 entries | `reviewer-deferred` | Each carries a `deferred_reason` a human accepted: IMP-0112, 0152, 0197, 0205, 0218, 0221, 0224, 0227, 0228, 0230, 0241, 0243, 0249 | their own recorded conditions |

**The two arrivals are worth one line of context.** The log grew from 250 to 252 entries while this document was being written, which is the concurrent-session hazard `IMP-0080` records for this SharePoint-synced repository. Both new entries are further instances of the largest class in the system — a platform contract guessed rather than ground-truthed, now at 32 — and both were logged by a delivery agent, not by me. They are named here so the next reader inherits them rather than discovering them.

The log gate will keep reporting `FAILED` after this review is applied, and that is correct: it fails on the parked blocker, and will keep failing until Review 21's gate is answered. This review cannot clear it and does not try.

---

## 6. Digest impact

The digest is **current** (`--check` green, 252 entries — it already absorbed the two mid-review arrivals). Changes 1–3 move nothing in it: the generator counts entries in both `NEW` and `APPLIED`, so moving this finding to `APPLIED` is invisible to it. The two deltas come from change 4 (where one lesson renders) and change 5 (one new entry).

| | Before | After (predicted) |
|---|---|---|
| Log entries | 252 | 253 |
| Distinct lessons | 252 | 253 |
| Recurring classes (x≥2) | 26 | 26 |
| This lesson renders in | `Unrouted — no section assigned`, inside a hidden overflow of 33 | `Operating constraints of this environment`, visible |

**The fourth row is the whole point of change 4.** This lesson reached the digest the moment it was logged and taught nobody, because it landed in a section that names 33 findings it does not show. `Operating constraints` currently shows 8 of 8, well under the cap of 20, so the lesson becomes visible there — and it is the section [pipeline-agent](../../agents/pipeline-agent.md) already reads at activation step 0, which is the agent whose template change 3 edits. The generator's own comment at [L111](../../scripts/generate-known-failure-modes.py#L111) records the same fix being made for three other classes in 2026-08-19.

**Predicted, not measured — and this exact operation is the one that has been mispredicted before.** [Review 10](./2026-08-22-improvement-review-2.md) added two classes to this same routing table, predicted the Unrouted section would fall from 31 lessons to 26, and measured 31 → 30: four findings of one class it moved had never been in Unrouted to begin with. I checked that specific failure mode here — this class has exactly one member and its single lesson is confirmed at [known-failure-modes.md L461](../../logs/known-failure-modes.md#L461), inside the Unrouted overflow — so the move is one lesson, not five. The figures are still confirmed after applying rather than before.

---

## 7. Gate

```
IMPROVEMENT REVIEW REQUIRED — docs/improvements/2026-08-24-improvement-review-2.md

Findings processed: 1 NEW  →  1 cluster
Regression check:   6 prior changes audited, 2 classes recurred
Proposed:           0 constraints (cap 3), 1 gate/script, 3 skill/knowledge edits,
                    2 agent-file edits, 0 retirements
Altitude calls:     0 generalised from instance to class, 1 left as an instance fix
Digest:             will regenerate — 253 lessons, 26 recurring classes
Improvement log:    1 new finding, appended on approval — two rule files assert a
                    Retired Constraints table that does not exist, and zero
                    retirements where there are seven (change 5)

Respond APPROVE IMPROVEMENTS to apply, or give feedback for revision.
```

---

## 8. Applied — 2026-08-24

**Approved by the reviewer (Xander Lykopoulos). Changes 1–4 applied as drafted; change 5 applied in corrected form after the reviewer rejected its figure and its method.**

The instruction on change 5 was explicit and is the more useful half of this review: do not replace a wrong hand-typed number with a right one, because the replacement is only right until the eleventh retirement. So the count is no longer asserted as a bare figure in either file — both sentences now carry the derivation command, and both are registered in the gate that already exists for this class.

### Elements changed

| # | Change | Where | Verified by |
|---|---|---|---|
| 1 | Schema block relabelled `bash`, the two `export` lines folded into the command that needs them, and the zsh `:P` mis-parse recorded so the misleading error is recognisable | [build-and-deploy.md L135](../../knowledge/technology/build-and-deploy.md#L135), pointer at [L74](../../knowledge/technology/build-and-deploy.md#L74) | the block is shell-correct by inspection; the mis-parse was reproduced before writing it |
| 2 | The `$auth` recipe is now explicitly PowerShell-inside-`pwsh`, distinguished from the outer-shell export pattern, pointing at change 1 | [testing-tools.md L182](../../knowledge/technology/testing-tools.md#L182) | prose |
| 3 | `REVIEWER ACTION REQUIRED` gained a `Shell:` line and a rule against `$env:VAR` in anything handed to a human | [pipeline-agent.md L151](../../agents/pipeline-agent.md#L151) | prose; every future hand-off now carries the shell |
| 4 | The class is routed into the digest's `Operating constraints` section | [generate-known-failure-modes.py L109](../../scripts/generate-known-failure-modes.py#L109) | **measured, not predicted** — the lesson now renders at [known-failure-modes.md L275](../../logs/known-failure-modes.md#L275); that section went 8 → 9 lessons |
| 5a | Both retirement sentences rewritten: the real in-place mechanism named, no phantom table, and the count carried as a command rather than a remembered figure | [improvement-agent.md L158](../../agents/improvement-agent.md#L158), [how-to-promote-a-finding.md L93](../../skills/how-to-promote-a-finding.md#L93) | `grep -c "Retired Constraints" constraints/README.md` → 0, which is why the phantom table is gone |
| 5b | Both claims registered so neither figure can go stale unnoticed | [derived-counts-registry.json](../../scripts/derived-counts-registry.json) — `improvement-agent-retired-constraint-count`, `promote-a-finding-retired-constraint-count` | `verify-derived-counts.py`: both rows match their derivation; 9 rows, 0 registry defects |

**No new script was written, deliberately.** [verify-derived-counts.py](../../scripts/verify-derived-counts.py#L20) already exists for exactly this class and its own docstring states that a new claim is *"a new row in `scripts/derived-counts-registry.json`, never a change to this file"*. This is the sixth instance of a hand-typed count drifting from source, and the gate built at the second instance absorbed it without modification — which is the altitude rule paying off rather than another script.

### Findings: what closed, what did not

| Finding | Disposition |
|---|---|
| The shell-syntax finding | **APPLIED.** `observable_at` is `n/a` (documentation), so no re-observation is owed. Needle: `Shell: zsh` in pipeline-agent.md |
| **New — the retirement-count defect** | **APPLIED** in the same breath as the fix. Needle points at the *registry row*, not at the sentence this review just wrote — a needle matching your own prose proves nothing (`IMP-0208`) |
| **New — the secured-column count is 51 in four places and 67 in source** | **Left open**, owner named. Not mine to close: one of the four is shipped solution source |

### The verification run surfaced a real defect, and it is not fixed

Registering the two new rows meant running the gate, and it reported four **pre-existing** drifts unrelated to this review: the field-security profile secures **67** columns and four documents say 51. Confirmed three independent ways, all agreeing on 67 — a real XML parse (67 `FieldPermission` elements), `IsSecured>1<` across every `Entity.xml` (67), and the registry's own pair count (67).

Stale in: [REV Trustee.xml:73](../../src/solutions/RevitaliseGrantAutomation/Roles/REV%20Trustee/REV%20Trustee.xml) — **shipped solution source** — plus the 2026-08-21 build handover and improvement review 5 (twice). The count has now moved 39 → 51 → 67, each move hand-edited in the same four places, which is the signal that the two shipped artefacts should stop stating a number at all. Logged and routed to whoever completes the `rev_bankaccount` / `rev_payment` field-security work; `REV Trustee.xml` is delivery source and not this agent's to author.

### Verification actually executed

| Check | Result |
|---|---|
| `generate-known-failure-modes.py --check` | current, 260 entries, 260 lessons, 476 lines |
| `verify-derived-counts.py --selftest` | 4 known-bad fixtures rejected, 3 known-good passed clean |
| `verify-derived-counts.py` (real registry) | 9 rows, **0 registry defects**; the 2 new rows match. 4 pre-existing drifts reported above |
| `verify-constraint-verifiers.py` | PASS — 69 paths named by 77 active constraint rows all resolve |
| `verify-improvement-log.py --check` | 3 problems, **none of them from this review** — an unread blocker, the parked Review 21 blocker, and the batch trigger |

**Not verified:** nothing in changes 2, 3 or 5a is mechanically checkable — they are instruction text, and only the count inside 5a is now gated. The `Shell: zsh` line in change 3 asserts the reviewer's shell as a fact; it was ground-truthed today (`$SHELL` and `dscl` both report `/bin/zsh`) but a future machine change would silently falsify it.
