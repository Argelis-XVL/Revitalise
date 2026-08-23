# Improvement Review 13 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 → 2 clusters (1 unread `blocker`, 1 appended by this review)
**Trigger:** blocker escalation — `IMP-0210`, appended by development-agent, processed immediately rather than batched
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. The finding guards delivery task 6.1. No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPLIED 2026-08-23** — see section 6.

---

## The headline

**The blocker is a good outcome, not a defect.** A dispatch was told to migrate the trustee portal
to the generated typed services, read the SDK's own shipped source *before* touching a write path,
found that the generated `update()` structurally cannot enforce update-only semantics, and stopped.
Nothing was applied; nothing broke. This is `C-TECH-052`'s discipline working exactly as designed.

**It needed no constraint and no new gate, because the control was already defended.**
[client.test.ts](../../src/code-apps/trustee-review-portal/src/dataverse/client.test.ts#L197)
asserts the operation name is `UpdateOnlyRecord` and that `parameters.If_Match === "*"`, under the
heading *"so it can never create a row"*. The migration this finding stopped would have failed that
test and one in `repository.test.ts`. So the promotion is a knowledge note — so nobody spends
another dispatch re-deriving it — and deliberately not a rule.

**The finding that earned a gate is the one I went looking for while checking this one.** Closing
`A-TR-10` meant reading the assumptions register, which showed its row still advertising itself as
an open E3 guess four screens above the live positive/negative control pair that closed it. That
is the **fourth** such row in two days.

---

## 1. Ground truth, established before drafting

The finding's claim was re-verified against the installed package rather than taken on trust, since
the whole conclusion rests on it. `@microsoft/power-apps` 1.3.0, this app's pinned version:

| Layer | Signature |
|---|---|
| `data/Data.types.d.ts` | `updateRecordAsync: <TInput, TResult>(tableName, recordId, changes)` |
| `internal/data/core/types/index.d.ts` | `updateRecordAsync<TRequest, TResponse>(tableName, id, data)` |
| `internal/data/core/api/updateRecord.js` | passes the same three arguments straight through |
| `defaultOperationOrchestrator.js` | `updateRecordAsync(tableName, id, data)` |
| `dataverseDataOperationExecutor.js` | `updateDataAsync(requestUrl, …, data, {operationName, datasetName, isDataVerseOperation})` |

**No headers parameter at any layer.** `runtimeDataClient._createHeaders` *does* read
`config.headers`, so the low-level client can carry caller headers — but `updateRecordAsync`'s
fixed arity never provides a path to populate it. The finding is precisely right.

**Why it is a correctness matter and not a nicety:** Dataverse's default `PATCH` is an **upsert**. A
`PATCH` against a nonexistent id returns 204 and silently creates the row — that is `A-TR-10`'s own
negative control, run live against this app. So "update" via the generated service is really
"update or create", and *"a `rev_review` row is only ever created by X"* is unenforceable through
it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: generated write semantics  (IMP-0210, blocker)
Altitude:  KNOWLEDGE, and I am declining to promote further on purpose.
           The promotion skill §4 permits skipping to a constraint on a first instance when the
           severity is blocker AND the mechanism is a platform law. The mechanism qualifies —
           a fixed arity is as hard a law as they come. The severity does not, in substance:
           nothing shipped, the agent stopped before implementing, and the cost was one
           dispatch's task rather than a defect.
Ladder row: "one instance, but the cause is general and a human needs to know it" -> knowledge/.
Becomes:   a subsection in code-apps.md under Data Access & Auth, with the read/write split
           stated as a rule: generated services for READS, executeAsync for any write that
           needs a connector-operation header.
Retires:   nothing.
Cites:     IMP-0210, IMP-0161
Residual:  The rule is prose and prose is weaker than a gate — BUT the specific control it
           protects is already mechanical: client.test.ts asserts UpdateOnlyRecord and
           If_Match '*', repository.test.ts asserts the shape in source. What is NOT covered
           is a FUTURE write path, on another table, choosing the generated service and
           needing a header nobody has thought about. No gate can see that in advance; the
           knowledge note is the only instrument that reaches it.
```

```
CLUSTER B: the register that cries wolf  (IMP-0211; instances A-TR-6, A-TR-7, A-TR-10, A-TR-12)
Altitude:  CLASS. Third instance of hand-maintained-count-drifts-from-source (x4) applied to a
           STATUS rather than a number, so §2 forbids a fourth per-row correction — and I had
           just made two of those by hand.
Ladder row: "a tool could catch it mechanically" + "second instance -> generalise".
Becomes:   scripts/verify-assumption-register.py + build gate `assumption-register`.
Retires:   nothing.
Cites:     IMP-0211, IMP-0014, IMP-0140, IMP-0150, IMP-0176
Residual:  Two real limits, both in the script's docstring rather than hidden. (1) It compares a
           row only against claims in the SAME document — a closure evidenced in a test report
           or deployment summary is invisible, and the answer is to record closures where the
           register is. (2) The inverse case, a row marked closed that the document never
           evidences, is REPORTED and never failed, because that evidence legitimately lives
           elsewhere. Four such rows are reported today.
```

**Why this cluster is not `IMP-0140` again.** That finding is about an APPLIED status in the
improvement log being a claim. This is the same property one document over, and the direction that
matters is the opposite of what `C-TECH-052` already checks: its `Verify By` has test-agent hunt
for *orphan guesses* — an artefact with no register row. Nothing looked for a **settled row still
advertising itself as unsettled**.

---

## 3. Changes applied

| # | Type | Target | Change |
|---|---|---|---|
| 1 | knowledge | [code-apps.md](../../knowledge/technology/code-apps.md#L153) | New subsection: the generated services cannot send custom headers on a write; Dataverse `PATCH` is an upsert; `executeAsync` is the only surface that can carry `If-Match`; reads-yes/writes-no rule; and a pointer to the two tests that already defend it |
| 2 | script | `scripts/verify-assumption-register.py` (new) + build gate `assumption-register` | Every register row must agree with its own document's closure claims. 10 selftest fixtures |
| 3 | doc | [dev summary](../../docs/development/revitalise-grant-automation-dev-summary.md#L4862) | `A-TR-7` and `A-TR-10` register rows closed at E1, naming the evidence that closed each |

**Constraint budget: 0 of 3 used.** No new constraint, and section 2 records why the one candidate
was declined rather than quietly skipped.

### What building the gate found

Worth recording, because it is the argument for fixtures over confidence:

- **One stale row hand inspection had missed** — `A-001`, closed in the narrative as *"A-001 closed
  above"*.
- **Two false positives of its own**, both fixed and both now fixtures. A naive *"id … CLOSED
  within N characters"* matched `A-TR-1` against `A-TR-12`'s closure in the line *"A-TR-1, A-TR-4,
  A-TR-5, A-TR-8, A-TR-9, A-TR-11 **remain OPEN** (A-TR-12 was closed …)"* — reporting two
  genuinely-open rows as settled, which is the direction that gets a gate switched off. And `A-001`
  itself was then reported stale when its row is a model closure record, worded **CORRECTED**
  rather than "closed", because a guess that turned out wrong is corrected, not closed.

The marker list is now deliberately wide (`closed`, `corrected`, `resolved`, `superseded`,
`withdrawn`, strike-through). The trade-off is one-directional and stated in the script: it risks
missing a stale row rather than shouting about a settled one.

---

## 4. Retirements

**Checked, and none.** The two documents this review touches gained content; nothing became
obsolete. The standing consolidation candidate —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35),
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86) — is unchanged and again
not taken, for the third review running. With the backlog now at one parked item, the next review
has no excuse.

---

## 5. Findings left unprocessed

No silent caps.

| Finding(s) | Why not processed | What closes it |
|---|---|---|
| `IMP-0197`, `IMP-0205` | Untouched by standing instruction: whether `power.config.json`'s `environmentId`/`appId` is a `C-TECH-047` breach or a sanctioned exception is still *"not sure yet"* | the reviewer's answer to that one question |
| `IMP-0198` | Parked at review 10's gate | the keyword against that document |
| `IMP-0112`, `IMP-0152` | Standing deferrals, reasons unchanged | as recorded on each |

**Delivery work named, not done:** the reads-only migration this dispatch scoped out
(`listApplicationsForReview` / `getApplication` / `getReviewForApplication` to the generated
`getAll()`/`get()`, leaving `saveVerdict` on `executeAsync`) stays a reviewer decision, and
`A-TRM-2` correctly records that it would lose compiler-level enforcement that every call site
supplies a `$select`. Not a rule change.

---

## 6. Applied

`APPROVE IMPROVEMENTS` — blocker trigger, processed immediately per `agents/WORKFLOW.md`.

**Entries moved to APPLIED:** `IMP-0210`, `IMP-0211` — both with `evidence_grep` needles.
**Entries rejected:** none.
**Findings appended:** `IMP-0211`, by this review, from reading the register while closing
`A-TR-10`.

**Gate state:** `assumption-register` PASS (28 rows, 8 registers, 3 documents, 17 genuinely open);
build preflight PASS at 38 steps / 27 gates; digest current at 208 entries.

**One verification limit, stated rather than implied.** The Microsoft Learn MCP server is
unauthorised in this session, so nothing here was cross-checked against Microsoft's published SDK
documentation. It did not matter for this finding — the installed package's own shipped source is
E1 and outranks documentation anyway — but a question that genuinely needed the docs could not have
been answered.
