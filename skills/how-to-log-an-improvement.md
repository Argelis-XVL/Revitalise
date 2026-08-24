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
