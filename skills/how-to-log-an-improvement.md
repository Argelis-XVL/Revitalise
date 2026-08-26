# Skill: How to Log an Improvement

Load this at the moment you need to write an entry — not upfront. It is one page by design.

**Where:** append one JSON object per line to `logs/improvement-log.jsonl`.
**Never** rewrite or reorder existing lines. Append-only means no merge conflicts, no
read-before-write, and no token cost for the file you are adding to.

---

## 1. When to log

Exactly these triggers. The narrowness is deliberate — a log full of observations is a log
nobody processes.

| # | Trigger | Why it is on the list |
|---|---|---|
| 1 | **A second attempt** at the same operation with changed input | The first attempt is work. The second is evidence. The fifteen-attempt DEV import produced one document, written afterwards from memory. |
| 2 | **Reality contradicted a document or config in this repo** | The repo was wrong, and it will be wrong the same way next time. |
| 3 | **Any `BLOCKED` / `FAILED` / `HOLD` status** | Already a stop; the marginal cost of a line is zero. |
| 4 | **Any human correction of your output** | The highest-value signal in the system. 14 of the 21 incidents in the founding analysis were found by the reviewer, and every one was discarded. |
| 5 | **A gate fired, or a gate was found broken** | A gate that fires proves it works. A gate found broken is a `blocker`. |
| 6 | **A capability was established that a future session would not know** | The keychain-certificate procedure was lost in one day. |

If you are unsure whether something qualifies: does the *next* run need to know? If yes, log it.

Do **not** log: routine successes, style preferences, anything already recorded in
`logs/known-failure-modes.md` (add to the recurrence count instead, by reusing its
`class_instance_of`).

---

## 2. The schema

```json
{"id":"IMP-0024","ts":"2026-08-18T09:14","agent":"build-agent","feature":"revitalise-grant-automation",
 "class":"gate-defect","severity":"blocker","cost":"2 build cycles",
 "what":"one sentence: what happened, concretely",
 "expected":"what the doc, config, or your own plan said would happen",
 "root_cause":"why it happened — the mechanism, not the symptom",
 "detected_by":"human|tool|agent-self",
 "observable_at":"V1|V2|V3|V4|V5|n/a",
 "why_it_was_never_caught":"which gate should have caught this and did not, or 'nothing'",
 "class_instance_of":"kebab-case-class-name",
 "lesson":"the imperative sentence a future agent needs. This is what reaches the digest.",
 "proposed_change":{"type":"constraint|knowledge|skill|agent|template|build-gate|script|none",
                    "target":"path","summary":"..."},
 "status":"NEW"}
```

### Required fields, and the three that do the work

`id` is the next unused `IMP-nnnn`. Take it from the **maximum id in the whole file**, not from
the last line, and read it again immediately before you append:

```bash
python3 -c "import json; print('IMP-%04d' % (max(int(json.loads(l)['id'][4:]) for l in open('logs/improvement-log.jsonl')) + 1))"
```

**Two sessions can be live in this repository at once.** Append-only removes the conflict on
existing lines; it does not reserve an id. On 2026-08-19 two sessions seven minutes apart both
read `tail -1`, both saw `IMP-0073`, and both wrote `IMP-0074` (`IMP-0080`). `tail -1` cannot
even see a higher id further up the file.

Nothing can prevent the race, so **run the gate before you commit**:

```bash
python3 scripts/verify-improvement-log.py     # fails with: duplicate id — also on line <n>
```

That check already existed and caught nothing, because it only ran in CI — and CI was dead that
day on an invalid workflow file. A gate you never run locally is a gate that protects the next
person, not you. Regenerate the digest and stage it together with the log, or your commit holds
two different moments of the same file.

**`why_it_was_never_caught`** — the most important field. It converts an anecdote into a
specification for a gate:
- `"nothing"` → demands a new check
- `"the build gate, if it had run in the right order"` → demands a step-order fix
- `"no test asserts form label text"` → names the missing assertion exactly

**`observable_at`** — the level at which the defect could be **seen**, on `C-TECH-053`'s ladder:
V1 well-formed · V2 packaged · V3 accepted by the target · V4 usable by a signed-in human · V5
executed end-to-end. **Required on every `blocker` and `rework` entry**, and the gate enforces it.

Answer *"at what level could someone have observed this?"*, not *"at what level did I happen to
notice it?"* — a defect a real user hits in the browser is V4 even if you found it by reading
source. `n/a` is a real answer and means the defect has no runtime symptom at all: a wrong
document, a missing citation, a process gap.

It exists because it decides **what may close the finding**. A defect at V2 or above cannot be
closed by a document saying it was fixed. `IMP-0208` was closed on a needle searching a knowledge
file for the words *"This is the fix, and it is confirmed working"* — a sentence written by the
review doing the closing. It matched by construction, and three days later the reviewer hit the
identical error as a real signed-in trustee (`IMP-0224`, `IMP-0225`).

**`reobserved`** — how a V2+ finding is actually closed. Not yours to write when you log the
finding; improvement-agent adds it at approval, and cannot close the entry without it:

```json
"reobserved":{"level":"V4","by":"XLykopoulos@revitalise.org.uk","ts":"2026-08-23T14:00",
              "rerun":"signed in to the portal, opened the applications list",
              "result":"symptom absent — list loaded, no org-url error"}
```

All five fields are required, `ts` must postdate the finding, and `level` may not be below
`observable_at`. A clean build, a clean lint, a zero CLI exit and a diff full of generated files
are V2/V3 evidence — they can never close a V4 defect.

**`refusal_context`** — **required** on class `harness-blocks-destructive-call` for any entry
dated after 2026-08-23, and `scripts/verify-improvement-log.py` fails the log without it. Until
2026-08-25 it appeared nowhere in this file, so the gate was rejecting a field nobody writing a
finding had been told to write (`IMP-0287`):

```json
"refusal_context":{"harness_mode":"auto|interactive|unknown",
                   "dispatch":"background|lead-foreground|reviewer-shell|unknown"}
```

Both members are required and `"unknown"` is a valid, honest answer — omitting the object is not.

It exists because **seven instances of this class never settled what actually decides a refusal**:
none recorded the session it happened in, so read-vs-write, Auto-Mode-vs-interactive and
background-vs-reviewer-shell stayed confounded across all seven (`IMP-0245`). One entry that
records the mode is worth more than another that records the refusal text verbatim — the text is
always the same sentence, and the mode is the variable.

**`corrects`** — the id of an earlier finding this one supersedes, when you have established
that the earlier entry's `root_cause`, `lesson` or `proposed_change` is **wrong**, not merely
incomplete. One id, as a string:

```json
"corrects":"IMP-0276"
```

Two gates and one activation step read this field, and until 2026-08-25 it appeared nowhere in
the file every agent loads to write a finding:

- `check_corrections()` in `scripts/verify-improvement-log.py` warns when a review document has
  already processed the entry you are correcting — because that review may be sitting at its
  gate proposing a HARD constraint built on the diagnosis you just disproved. That is `IMP-0275`:
  review 24 proposed a HARD gate from `IMP-0272`'s root cause, `IMP-0273` corrected it from
  Microsoft's own worked example before the keyword arrived, and applying the review as approved
  would have made a HARD gate red against correct code.
- The same function's second case warns when the entry you are correcting is still **unread** —
  see the next paragraph.
- `agents/improvement-agent.md` activation step 8 requires the applying agent to read every
  `corrects` warning before applying an approved review.

**Setting `corrects` is not the whole job — the corrected entry's own queue entry must also
move.** Appending your entry and closing the one it corrects are two separate write actions, and
only the second clears `C-TECH-061`. `IMP-0277` corrected `ensure-auditing.ps1` and named
`IMP-0276` in `corrects`; `IMP-0276` stayed `NEW`/unread, which is independently a HARD
violation, and the next build spent a full ~9-minute attempt reaching the `unit-tests` step to
discover a check that runs in one second (`IMP-0285`, `blocker`). So: if you correct a finding,
either process it or route it to `improvement-agent` — and **do not stamp a `deferred_reason` on
it to clear your own build.** A deferral is a reviewer's decision, not a build-unblocking tool.

**Its limit, stated so you do not rely on it.** `corrects` is optional and no gate can infer it.
`IMP-0288` contradicted improvement review 26's disposition of `IMP-0278` while that review sat
at its gate, set no `corrects`, and every rung above stayed silent. If your finding contradicts a
conclusion some review reached, set `corrects` **and** say so in `what` — the prose is what a
human reads, and it is the only thing that catches the case the field misses.

**`appended_by`** — the review document that **wrote** this finding, when the agent appending it
is `improvement-agent` writing a finding of its own inside a review. One path, or a list:

```json
"appended_by":"docs/improvements/2026-08-25-improvement-review-3.md"
```

It is **not** `reviewed_in`, and the two are independent. `reviewed_in` says *a review processed
this*; `appended_by` says *a review authored this*. Both may be present, and often should be: a
finding review 28 logged and review 29 then processed carries review 28 in `appended_by` and
review 29 in `reviewed_in`.

Only one thing reads it, and that is the whole reason it exists. `check_missing_stamps()` in
`scripts/verify-improvement-log.py` warns when an `unread` entry is cited by a review document
and carries no `reviewed_in` — because such an entry is indistinguishable from one nobody has
opened (`IMP-0154`). **A review that appends its own findings always types their ids in a
non-deferral position**, so that check warned against every such review by construction and
instructed it to stamp a disposition existing nowhere. Review 28 was told to stamp `IMP-0319`,
which it had written itself; review 29 spent a re-derivation establishing that no review had
processed it (`IMP-0328`).

**Why a field and not a smarter regex.** That predicate had already grown two prose exemptions
for two earlier false-positive shapes (`IMP-0196`, and review 19 change 7), and the third
instance is where the altitude rule forbids a third. Nothing in prose separates *"I wrote this"*
from *"I processed this"* — the positions are identical — so the entry declares it. The general
form of the lesson: **a check that identifies its target by subtracting known-innocent positions
from all positions grows one exemption per shape forever and is wrong by construction on the
shapes nobody has met yet.**

**Its limit is the same as `corrects`'s, and for the same reason.** The field is optional and no
gate can infer it. It also buys silence, so it is checked like any other claim about a file: an
`appended_by` naming a document that does not exist is a HARD error, not a suppression.

**`root_cause` and `proposed_change` are a HYPOTHESIS, not a specification.** You write them
from a symptom, usually under time pressure, and the next agent along treats them as the work
order. **If you are the agent acting on a finding, re-verify both against source before building
either.** Two checks, both one command:

```bash
grep -rn "<the thing the finding says source never declares>" src/    # is the claim true?
grep -rln "<the check the finding proposes>" scripts/                 # does the gate exist?
```

`IMP-0255` failed both. It stated five lookup attributes "were never actually marked
IsSecured=1 anywhere in source" and that the XML shape had nowhere to carry the flag. Both
false: each was a full `<attribute>` element declaring `<IsSecured>1</IsSecured>`, and the
parser had read it since it was written. The real cause was **one omitted line** in the function
that builds the create call. Acting on the finding as written would have built a new XML
mechanism nothing needed. It also proposed a gate that already existed and had already **passed
over the very defect** — and that, not the missing gate, was the real finding, because it meant
the gate was looking in the wrong place (`IMP-0258`).

So: a wrong `root_cause` propagates whole into the `proposed_change`, and the corollary is worth
holding on its own — **a source-vs-source gate can never catch a source-vs-creation-path gap.**

This is the same rule `skills/how-to-promote-a-finding.md` §4 states for improvement-agent
("an argued mechanism, in place of a confirmed one"), applied one step earlier: to whoever
writes the finding, and to whoever acts on it.

**`class_instance_of`** — the altitude field. Reuse an existing class name verbatim when one
fits; check `logs/known-failure-modes.md` first. Two entries sharing a class is the signal that
triggers generalisation instead of another instance patch. Inventing a near-duplicate class name
defeats the mechanism.

**`lesson`** — the imperative sentence that reaches `logs/known-failure-modes.md` and gets read
on every future activation. Write it for someone who has never seen the incident. Not *"the path
was wrong"* but *"`pac solution check --path` takes a packed .zip, never a source folder."*

`cost` should be concrete: attempt counts, cycles, hours, "undetected since authored". It is how
the improvement-agent ranks. `"unknown"` is acceptable; omitting it is not.

`severity`: `friction` (annoying, worked around) · `rework` (work had to be redone) ·
`blocker` (stopped progress, or shipped a defect). A `blocker` triggers the improvement-agent
immediately rather than waiting for a batch.

---

## 3. After appending

Regenerate the digest, or your finding teaches nobody:

```bash
python3 scripts/generate-known-failure-modes.py
```

Then report it in your gate output. Every agent's gate block carries this line, and it appears
even when the answer is none — its absence is what let a week of findings go uncaptured:

```
IMPROVEMENT LOG: <n> entries appended — IMP-0024, IMP-0025  |  digest regenerated: YES
```

---

## 4. Worked example — from the incident that created this skill

The reviewer's own words, 2026-08-17: *"yesterday you moved and got the certificate from the
mac keychain. Make it so that you can use that again."* A working procedure, established the
previous day, gone.

```json
{"id":"IMP-0022","ts":"2026-08-17T17:59","agent":"pipeline-agent","feature":"revitalise-grant-automation",
 "class":"memory-loss","severity":"rework","cost":"the reviewer had to re-teach a working procedure",
 "what":"The certificate-from-Mac-keychain procedure, worked out and used successfully on 08-16, was unavailable the next day.",
 "expected":"a capability established once stays available",
 "root_cause":"pipeline-agent loads only its pipeline.yml and one knowledge file. Nothing carries an established capability across sessions.",
 "detected_by":"human",
 "why_it_was_never_caught":"there was no read-back path of any kind - no agent reads prior logs, manifests, or the handover document",
 "class_instance_of":"learning-substrate-destroyed",
 "lesson":"The provisioning certificate is in this Mac's CurrentUser/My keychain (thumbprint A6F94E...C7FE, app id 077f1f90-...). Cert-based app-only auth to DEV works from there - do not ask the reviewer to re-supply it.",
 "capability":true,
 "proposed_change":{"type":"agent","target":"agents/pipeline-agent.md","summary":"read logs/known-failure-modes.md on activation; capabilities section carries established procedures"},
 "status":"NEW"}
```

Note `"capability": true` — an optional flag that routes the lesson to the digest's
*Capabilities established in earlier sessions* section. Use it for things that **work** and
would otherwise be rediscovered.

---

## 5. What you must not do

- Do not set `status` to anything but `NEW`. Only the improvement-agent moves an entry to
  `APPLIED` or `REJECTED`.
- Do not apply your own `proposed_change`. Propose it; the improvement-agent decides the
  altitude and the human approves it. An agent that fixes the rules mid-task is how a system
  accumulates one gate per incident.
- Do not hand-edit `logs/known-failure-modes.md`. It is generated.
- Do not write findings into `logs/routing.log`, `logs/build.log` or `logs/pipeline.log`.
  Eight findings were once improvised into `routing.log`, where nothing could process them
  (`IMP-0023`). Those logs remain one line per action, as `agents/WORKFLOW.md` specifies.
