# Skill: How to Promote a Finding

Loaded by **improvement-agent only**, at the point of deciding what a cluster of findings
should become.

The question this skill answers is not *"is this finding real?"* — the agent that logged it
already established that. It is **"what is the lowest-cost home that actually prevents a
recurrence?"**

---

## 1. The promotion ladder

Work down the table and stop at the first row that fits. Lower is cheaper and more durable.

| Evidence | Becomes | Where |
|---|---|---|
| One instance, specific to one feature, no general mechanism | **Nothing.** It stays a log note. | — |
| One instance, but the cause is general and a human needs to know it | A line in the relevant knowledge file | `knowledge/` |
| **A tool could catch it mechanically** | **A script plus a build/pipeline gate** | `scripts/` + `config/<slug>-build.yml` |
| A capability was established and could be lost again | A `capability: true` lesson | the digest |
| **Second instance of the same `class_instance_of`** | **Generalise — see §2. Instance patches are forbidden here.** | usually `scripts/` |
| A platform law, or a third instance | A constraint row, HARD or SOFT | `constraints/` |
| An agent had the information and still did the wrong thing | An agent-file or skill edit | `agents/`, `skills/` |
| The **order** of steps was wrong | A step-order or activation-order fix | `agents/WORKFLOW.md`, `config/*.yml` |
| The system's own memory failed | A read-path change | agent activation step 0 |

### Prefer the most mechanical home available

A script beats a constraint row beats a paragraph of prose. This is not a stylistic
preference — it is this project's own measured result. `C-TECH-049` (flow descriptions ≤256
chars, now generalised into `C-TECH-060`) became effective because a *script* existed and ran —
`scripts/verify-field-length-limits.py` today, `verify-workflow-description-length.py` when the
lesson was first learned.
The constraint text alone had no effect for the weeks it existed before the script.

Corollary: **a constraint whose `Verify By` is not mechanically executable is a comment.** If
you cannot name the command that checks it, you are proposing documentation, not enforcement.

---

## 2. The altitude rule

> **On the second instance of a class, you may not add another instance-level gate.**
> Generalise, and retire the instance gates you are replacing.

This rule exists because the manual loop broke precisely here. Its record:

- `C-TECH-049` fixed *"flow `description` fields exceed 256 characters"* — an **instance**.
- The class was *"platform field-length limits the packer does not enforce."*
- Two days later, `rev_setting.rev_description` at 500 characters hit the same class from a
  different direction and got **its own separate script**.
- The repo carried `verify-workflow-description-length.py` **and**
  `verify-setting-description-length.py`, and had no gate for the third instance.
- **Closed 2026-08-18** by the first improvement review, which is what this section asked for:
  both scripts are deleted, `C-TECH-049` is retired, and one schema-driven gate
  (`scripts/verify-field-length-limits.py`, `C-TECH-060`) reads `<MaxLength>` from
  `Entities/*/Entity.xml` instead of transcribing it. Both retired fixtures still fail under it —
  that assertion *is* the coverage proof this skill demands. Keep the history above: it is the
  clearest example in the repo of what the altitude rule prevents.

The same pattern in another class: *"import reported success but created nothing"* was found
on 08-14 (forms, views, settings rows) and rediscovered on 08-16 (two columns silently not
created). Nothing generalised the first fix, so the second was inevitable.

### How to generalise

Ask: **what is the property, independent of the instance?**

| Instances seen | The property | The general gate |
|---|---|---|
| flow `description` ≤256; `rev_setting.rev_description` ≤500 | *no shipped text field exceeds the MaxLength its own schema declares* | one gate that reads declared `MaxLength` from source and checks every text value against it |
| forms/views not created; two columns not created | *every component type the source declares is queried by name after import* | derive the query list **from source**, never hand-write it |
| lint path wrong; FR-016 path wrong; gitleaks scope wrong | *every gate's inputs exist, are produced earlier, and the gate can be made to fail* | `scripts/verify-build-config.py` + a negative test per gate |

Note the third row: three instances of `gate-cannot-fail` collapsed into one preflight plus
one test suite. That is what the ladder is for.

### When retiring an instance gate

Do not delete silently. In the same change:
1. Note the retirement in the review document, naming the general gate that replaces it.
2. Mark the constraint `status: retired` with a `retired_reason` per `constraints/README.md` —
   never renumber or reuse the ID.
3. Confirm the general gate covers every case the instance gates did. A generalisation that
   loses coverage is a regression, not a promotion. Prove it with the retired gates' own
   known-bad fixtures: they must still fail under the new gate.
4. **Grep the whole repository for the retired thing's literal token, and rewrite every
   INSTRUCTION to use it — not just the implementation and its call sites.**

   ```bash
   grep -rn -- '<the-retired-flag-or-mode-or-convention>' . \
     --include='*.py' --include='*.md' --include='*.yml' --include='*.json' \
     --exclude-dir=.git --exclude-dir=node_modules
   ```

   Read **every** hit and classify it: implementation · call site · **instruction** · history.
   The first two are what everyone remembers. An instruction is a comment, an agent file, a
   knowledge page or a config header **telling the next agent to use the thing you just
   retired** — and it is the one that costs, because a retired capability that still has a
   documented user is worse than one that was never retired: the next agent follows the
   instruction, gets a usage error, and has no reason to suspect the document.

   History is the one class you leave alone — an entry recording *"`--allow` was retired on
   `<date>`"* is the record working, not a stale reference.

   `IMP-0492`: retiring the `--allow` flag touched the code and its one call site and **not the
   config comment eleven lines above it**, which went on telling the next agent to reach for the
   flag. This is the same rule `skills/how-to-verify-a-platform-contract.md` already applies to
   closing an assumption, generalised to capability retirement — and the grep is a command,
   whereas whether every hit was correctly classified is a judgement, so this step is a
   checklist and not a gate.

---

## 3. Anti-bloat limits (hard)

1. **Every new constraint cites its `IMP-` ids.**
2. **Maximum 3 new constraints per review.** More than that means the clustering is too fine —
   propose consolidation instead.
3. **Every review considers retirement.** Name at least one candidate, or state that you
   checked and found none — a rule set that only grows is one nobody can hold in mind.
   Retirement happens in place in the constraint files (`status: retired` plus a
   `retired_reason`), per `constraints/README.md`; there is no separate retired-constraints
   table. Never hand-type the count — derive it with
   `grep -rh '^| ~~C-' constraints/ --include='*.md' | wc -l` (**10 retired as of 2026-08-24**).
   Anchor on the struck-through id: a naive `grep -c "status: retired"` returns one too many,
   catching the sentence that explains the convention. Registered in
   `scripts/derived-counts-registry.json` so the figure above cannot go stale unnoticed.
4. **No silent caps.** If you process only some findings, say which you deferred and why.

---

## 4. What is *not* evidence for promotion

### First, the one change this ladder never produces

**A harness refusal, a permission prompt or a safety classifier is a control, not a defect in the
pipeline.** No promotion may have as its mechanism that the control observes less than it did
before. Concretely forbidden, however phrased:

- omitting or softening the description of a live write in a dispatch prompt,
- moving a refused operation into a broader-permissioned or less-scoped session to get a
  different answer from the classifier,
- any wording whose benefit is that the harness no longer recognises what is about to happen.

The legitimate responses to a refusal are all **additive**: prove access first with a read-only
probe, perform the operation in a session properly scoped for it that reports its result and
verification query back, or hand the exact command to the human with the query that proves the
outcome. **If a proposal's advantage disappears once the operation is described honestly, that is
the tell.**

This is here because improvement review 21 proposed exactly that and had to be rejected
(`IMP-0264`). It recommended moving a refused live write into lead-agent's own shell and editing
`agents/lead-agent.md` so dispatch prompts would stop describing the write — reasoning, in its own
words, that the dispatch would then not be *"classified on intent it does not need to carry."*
Eight instances of `harness-blocks-destructive-call` logged as cost and friction had made *"how do
we stop being refused"* feel like the question; the question was *"how do we make this operation
visible and verifiable enough to be performed properly."* Nothing in this skill said so, so the
ladder promoted a bypass without tripping anything, and the only control that caught it was a
human reading the draft.

No gate can read a proposal's intent, so this rule is prose and will stay prose. It is stated
plainly instead: the agent applying this ladder is the one agent whose output edits the rules every
other agent obeys.

### And the ordinary exclusions

- **"It would be cleaner."** Not a finding.
- **"It might happen."** The log records what did happen. Speculative constraints tax every
  future run for a defect nobody has met.
- **One noisy incident with a large `cost`.** Cost ranks findings; it does not decide altitude.
  A single expensive one-off is still a one-off.
- **A finding whose `why_it_was_never_caught` is `"nothing"` and whose class has one member.**
  That is a candidate for a knowledge line, not a constraint. Wait for the second instance —
  unless the severity is `blocker` and the mechanism is a platform law, in which case skip to
  the constraint row and say why you skipped ahead.
- **An argued mechanism, in place of a confirmed one.** A plausible cause, however well
  reasoned, is not grounds to write a fix into a knowledge file. The causal test is running the
  exact failing call again and observing it succeed — not the elegance of the explanation.

  This one has its own history, and it is recent. Review 15 concluded that a stray
  `pac --non-interactive` process holding the MSAL token cache was why `pac` hung, and edited
  `knowledge/technology/build-and-deploy.md` on that basis. The process was a genuine anomaly
  and the reasoning was good. Killing it changed nothing — `pac org who` hung identically
  afterwards, and the real blocker was a macOS Keychain dialog waiting on screen, invisible to
  every shell probe anyone could have run (`IMP-0217`). Two simultaneous causes produced one
  symptom, and the review never ran the kill-and-retry test that would have shown it.

  So: **before an entry with `observable_at` of V2 or higher is marked `APPLIED`, the original
  reproduction step is re-run and the symptom observed gone**, and that goes in the entry's
  `reobserved` field. `scripts/verify-improvement-log.py` refuses the closure otherwise. Where
  the re-observation cannot be made in this session — it needs a signed-in human, or an
  environment nobody here can reach — the entry stays `NEW` with a `revisit_when` naming who
  can make it. An honest open entry beats a closed one nobody tested (`IMP-0224`, `IMP-0225`).

---

## 5. Output shape, per cluster

Record each decision in the review document like this, so the reasoning survives:

```
CLUSTER: gate-cannot-fail  (x4: IMP-0002, IMP-0004, IMP-0007, IMP-0020)
Altitude:  CLASS — 4 instances, all "a gate reported PASS while checking nothing"
Ladder row: "a tool could catch it mechanically" + "second instance → generalise"
Becomes:   scripts/verify-build-config.py (preflight) + src/tests/build/BuildGates.Tests.ps1
           (one negative test per gate)
Retires:   nothing — no instance gates existed for this class; it was undefended
Cites:     IMP-0002, IMP-0004, IMP-0007, IMP-0020
Residual:  `lint` cannot have a known-bad fixture (hosted third-party analyser). Documented
           as an exemption with a reason in verify-build-config.py, not silently skipped.
```

The `Residual` line is required. Every promotion leaves something uncovered; naming it is the
difference between a gate and a false sense of one.
