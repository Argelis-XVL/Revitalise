# Improvement Review 15 — 2026-08-23

**Agent:** improvement-agent (tier `strategic`)
**Findings processed:** 2 → 2 clusters (1 unread `blocker`, 1 appended by this review)
**Trigger:** blocker escalation — `IMP-0215`, processed immediately rather than batched
**Gate:** `APPROVE IMPROVEMENTS`
**WBS:** `system`. No contracted task is claimed here.

**Status:** ~~AWAITING `APPROVE IMPROVEMENTS`.~~ **APPLIED 2026-08-23** — see section 6.

---

## The headline

**The fix is applied, and the proposed form of it would have broken the build on the machine that
runs builds.** `timeout` is GNU coreutils. This Mac has neither `timeout` nor `gtimeout`. Builds
here run from the Mac while CI runs `ubuntu-latest`, so `timeout 180 pac ...` would have passed in
CI and failed with `command not found` locally — the worst possible split. It is now
`scripts/run-with-timeout.sh`, which uses `timeout`/`gtimeout` when present and a portable
poll-and-kill otherwise.

**On the judgement you flagged: I do not think this is a hosted-service outage, and the control
that settles it takes ten seconds.** Entra ID and Dataverse were both healthy from this machine at
the moment `pac` was hanging. So the note I have written is not the "wait and retry, no ticket
possible" playbook you floated — it is the discriminator that tells the two situations apart,
because writing the outage playbook would have enshrined a wrong diagnosis.

**There is a concrete prime suspect.** A `pac --non-interactive` process, alive **15 hours 34
minutes**, spawned by the VS Code Power Platform extension — which bundles its own `pac` binary,
separate from `~/.dotnet/tools/pac`. It predates all five hangs and holds the shared MSAL token
cache.

---

## 1. The evidence, because it reverses the conclusion

Three probes, run while processing the finding:

| Probe | What it isolates | Result |
|---|---|---|
| `pac auth list` | pac, **local only** — reads the profile store, no token needed | **instant** ✅ |
| `pac org who` | pac, **network + cached token** | **hung, zero output**, had to be killed ❌ |
| Cert-based `Get-DataverseAccessToken` + `organizations?$select=name` | Entra ID and Dataverse, **bypassing pac entirely** | token **4172ms**, org responded **5557ms** ✅ |

The third probe is the one that matters: the platform answered in under six seconds while `pac`
could not complete a `who`. And the split between probes 1 and 2 is diagnostic in itself — the
local command was fine and the token-needing command was not, which is the signature of a
contended token cache rather than a dead endpoint.

Then `pgrep -fl pac` found the 15h34m process.

**Why five identical hangs looked like stronger evidence than they were.** Every attempt exercised
the same pac code path, so five results were **one observation repeated**. Repetition is not
corroboration. That is the transferable half, and it is the second time this project has reached
for the vendor before running a local control — `IMP-0208` was the first, where six findings
concluded *"escalate to Microsoft"* over `Invalid organization URL 'null'` and a local flag fixed
it.

---

## 2. Clusters and promotion decisions

```
CLUSTER A: the hanging step  (IMP-0215, blocker)
Altitude:  INSTANCE -> a build-config change plus a reusable script. Not a constraint: the
           rule "put a timeout on a call to a hosted service" is real but this is its first
           instance in this repo, and §4 of the promotion skill says wait for the second
           unless the mechanism is a platform law. It is not — it is a missing guard.
Ladder row: "a tool could catch it mechanically".
Becomes:   scripts/run-with-timeout.sh (new, portable, 5 selftest cases) wrapping the `lint`
           step at 180s — ~5x the documented ~35s, so a slow-but-working check still finishes.
Retires:   nothing.
Cites:     IMP-0215, IMP-0040, IMP-0061
Residual:  The timeout makes the failure FAST and legible; it does not make the checker run.
           `lint` remains the one step between this build and a fully green run, and the
           C-TECH-062 quality gate it serves is unverified until it completes once. Also: the
           wrapper guards this one step. Every other call to a hosted service in build.yml and
           pipeline.yml is still unbounded, and a second instance is what would justify
           sweeping them.
```

```
CLUSTER B: the diagnosis  (IMP-0216, appended here)
Altitude:  KNOWLEDGE, in the file build-agent already loads at activation step 2 — which is who
           hits this. A gate is not available: nothing in a repository can probe whether a
           third party is healthy, and the value here is a PROCEDURE a human runs in ten
           seconds, not an assertion.
Ladder row: "one instance, but the cause is general and a human needs to know it". Second
           instance of the underlying class (platform-contract-guessed-not-groundtruthed, with
           IMP-0208), and the shared property is "the vendor was blamed before the cheap local
           control was run".
Becomes:   the three-probe discriminator table, the ordered procedure, and the
           no-correlation-id rule, in build-and-deploy.md.
Retires:   nothing — but it CORRECTS IMP-0215's own conclusion and its
           `hosted-service-unresponsive` class name, which is recorded rather than rewritten:
           the author's observation stands, the inference does not.
Residual:  The suspect is not proven. Confirming it means killing the stray process and
           re-running the check, and that process belongs to the reviewer's editor — see
           section 5. Until then "prime suspect, timeline fits" is the honest strength of the
           claim, and the note says so rather than asserting a cause.
```

---

## 3. Changes applied

| # | Type | Target | Change |
|---|---|---|---|
| 1 | script | `scripts/run-with-timeout.sh` (new) | Portable wall-clock limit: `timeout`/`gtimeout` when present, else poll → TERM → grace → KILL. Exit **124** on timeout, preserving GNU's convention so a stall is distinguishable from a real failure. 5 selftest cases |
| 2 | build-gate | [build.yml `lint`](../../config/revitalise-grant-automation-build.yml#L752) | `pac solution check` wrapped at 180s, with the portability trap documented in the step's comment so nobody "simplifies" it back to `timeout` |
| 3 | knowledge | [build-and-deploy.md](../../knowledge/technology/build-and-deploy.md#L246) | The discriminator: three probes and what each proves, `pgrep -fl pac` including the VS Code extension's separate binary, and why an unattributable hang is not a support ticket |

**Constraint budget: 0 of 3 used.**

### Why the timeout is worth having even though this was not an outage

Stated plainly, because it would be easy to read the reversal as making the fix pointless. It does
the opposite. The finding's real cost was **13.5 minutes across three attempts producing no new
information** — and that cost is identical whether the cause is Microsoft or a stray process on
this laptop. A hang that fails in three minutes with exit 124 is diagnosable; one that runs until
someone gets bored is not. The timeout is what makes the *next* occurrence cheap to investigate.

---

## 4. Retirements

**Checked, and none.** No rule became obsolete; one inference was corrected in place.

**The standing consolidation candidate is now the oldest un-acted item in this system** —
[C-TECH-001](../../constraints/technology/technology-constraints.md#L34),
[C-TECH-002](../../constraints/technology/technology-constraints.md#L35) and
[C-TECH-044](../../constraints/technology/technology-constraints.md#L86), carried for the fifth
review running. I said last review it should be the next review's first agenda point and it was
not, because a blocker arrived instead. Recording that pattern: it will keep losing to blockers
until someone schedules it deliberately.

---

## 5. What you need to decide

**Do you want the 15-hour `pac` process killed?**

It is PID 4389, `pac --non-interactive`, spawned by the VS Code Power Platform extension. It is the
prime suspect and the timeline fits all five hangs, but it belongs to your editor session and I did
not kill it — that is your environment, not the repository.

If you want it cleared, this is the sequence, and step 3 is what actually confirms the diagnosis:

```bash
pgrep -fl pac                                   # 1. confirm it is still there
kill 4389                                       # 2. or quit the Power Platform extension / VS Code
pac org who                                      # 3. should now answer in seconds, not hang
```

If `pac org who` answers after that, the hosted checker was never the problem and `lint` should
run normally. If it still hangs with the stray process gone **and** the cert-based control still
succeeds, then a pac-local auth defect is next — re-authenticate the profile
(`pac auth create --deviceCode`) before considering anything hosted.

**I am not recommending a Microsoft support ticket.** There is no correlation id to give them, and
the control says their service is up.

---

## 6. Applied

`APPROVE IMPROVEMENTS` — blocker trigger, processed immediately per `agents/WORKFLOW.md`, with the
timeout fix explicitly authorised in the dispatch.

**Entries moved to APPLIED:** `IMP-0215`, `IMP-0216`, both with `evidence_grep` needles.
**Entries rejected:** none.
**Findings appended:** `IMP-0216` — the discriminator, and the correction to `IMP-0215`'s
inference.

**Gate state:** build preflight PASS at 39 steps / 28 gates with `bash -n` clean on the modified
folded scalar; `run-with-timeout.sh --selftest` 5/5 on this host's fallback path; log gate OK;
digest current at 213 entries. `lint` itself is still unverified end-to-end — that is section 5.
