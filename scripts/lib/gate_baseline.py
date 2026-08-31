#!/usr/bin/env python3
"""A dated, owned baseline for a HARD gate: suppress the FAIL, never the report. Stdlib only.

WHY THIS MODULE EXISTS
----------------------
`IMP-0439`, a blocker. Improvement review 36 built `verify-provisioning-test-presence.py`, measured
it correctly (3 findings, all true), and wired it at `config/<slug>-build.yml` line 183 as step 4
of 72 — where **no step declares a severity**, so a non-zero exit halts the build. The gate was
right and the next build was dead, over three provisioning scripts that predated the dispatch and
which `C-COM-002` says are not the introducing dispatch's to fix.

`IMP-0320` is the recorded CORRECT handling of the same shape: that dispatch built its gate,
measured it red over two pre-existing flows it did not touch, and deliberately did **not** wire it.
Nothing carried that precedent forward, so review 36 reached the opposite decision with nothing
asking the question.

THE TWO WRONG ANSWERS, AND WHY THIS IS NOT EITHER OF THEM
--------------------------------------------------------
* **Un-wire the gate.** `contract/known-exceptions.json` names this exactly: *"a gate that is
  switched off because reality violates it is the gate-cannot-fail class arriving by the front
  door."*
* **Silence the findings.** Then the debt is invisible and the gate has stopped being a gate.

So this module implements the semantics `contract/known-exceptions.json` already established for
the commercial gates, for technology gates: **an exception suppresses the FAIL, never the report.**
Every run still prints every finding, with the exception cited against it, its owner named and its
expiry shown. An entry missing an owner, a clearing action or an expiry **fails**. An **expired**
entry fails. That is what stops a baseline becoming a permanent waiver.

WHY A SHARED MODULE AND NOT A BLOCK IN EACH GATE
------------------------------------------------
Two gates needed it in one review (`verify-provisioning-test-presence.py` and
`verify-superseded-column-writers.py`). Two copies of an expiry-checking rule is how one of them
grows a bug the other does not have, and the anti-bloat limits forbid the duplication. One file,
one set of semantics, one place to read them.

WHAT IT DOES NOT DO
-------------------
It is **opt-in**, like every helper in this directory, and nothing forces a new gate to consult it.
It also cannot tell a legitimate baseline from a lazy one — the control is the `expires` date and a
human reading the report, not this code. Stated rather than hidden.

THE FILE IT READS
-----------------
`config/gate-baselines.json`:

    {"baselines": [
      {"gate": "provisioning-test-presence", "matches": "provisioning/dataverse/foo.ps1",
       "reason": "...", "owner": "lead-agent", "clears_when": "...",
       "expires": "2026-09-30", "finding": "IMP-0439"}
    ]}

`matches` is compared against a finding's KEY — an exact string the gate chooses (a path, an
identifier). Substring matching was deliberately rejected: it is how one baseline silently covers a
finding nobody baselined.
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

__all__ = ["Baseline", "load_baselines", "BaselineError"]

REQUIRED = ("gate", "matches", "reason", "owner", "clears_when", "expires")


class BaselineError(RuntimeError):
    """The baseline file itself is unusable or an entry is invalid. Callers FAIL — never skip."""


class Baseline:
    """The baselines applying to ONE gate. Immutable after construction."""

    def __init__(self, gate: str, entries: list[dict]) -> None:
        self.gate = gate
        self._by_key = {e["matches"]: e for e in entries}
        self.entries = entries

    def excuses(self, key: str) -> dict | None:
        """The entry covering `key`, or None. Exact match only, by design."""
        return self._by_key.get(key)

    def cite(self, key: str) -> str:
        """The text a gate prints beside a suppressed finding, or '' if it is not covered."""
        e = self.excuses(key)
        if not e:
            return ""
        finding = f", {e['finding']}" if e.get("finding") else ""
        return (f" [BASELINED until {e['expires']}, owner {e['owner']}{finding} — "
                f"clears when: {e['clears_when']}]")

    @property
    def unused(self) -> list[str]:
        """Keys nobody claimed this run. A baseline for a finding that no longer exists is debt
        that has been paid and not recorded, so a gate should report it rather than carry it."""
        return sorted(self._claimed_gap)

    def note_claimed(self, keys: set[str]) -> None:
        self._claimed_gap = set(self._by_key) - keys


def load_baselines(repo_root: Path, gate: str, today: _dt.date | None = None) -> Baseline:
    """Every valid baseline for `gate`. Raises `BaselineError` on an invalid or expired entry.

    An absent file is NOT an error — it means no baselines, which is the desired steady state.
    """
    path = repo_root / "config" / "gate-baselines.json"
    if not path.is_file():
        b = Baseline(gate, [])
        b.note_claimed(set())
        return b
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"config/gate-baselines.json is unreadable: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("baselines"), list):
        raise BaselineError("config/gate-baselines.json must be an object with a 'baselines' list")

    today = today or _dt.date.today()
    mine, problems = [], []
    for i, e in enumerate(data["baselines"]):
        if not isinstance(e, dict):
            problems.append(f"baselines[{i}] is not an object")
            continue
        missing = [k for k in REQUIRED if not str(e.get(k, "")).strip()]
        if missing:
            problems.append(f"baselines[{i}] ({e.get('matches', '?')}) is missing: "
                            f"{', '.join(missing)}. An unowned or undated baseline is a permanent "
                            f"waiver, which is what this file exists to prevent")
            continue
        if e["gate"] != gate:
            continue
        try:
            expires = _dt.date.fromisoformat(str(e["expires"]))
        except ValueError:
            problems.append(f"baselines[{i}] ({e['matches']}) has an unparseable expires "
                            f"'{e['expires']}' — use YYYY-MM-DD")
            continue
        if expires < today:
            problems.append(f"baselines[{i}] ({e['matches']}) EXPIRED on {expires} — owner "
                            f"{e['owner']}. Clear it or re-decide it; an expired baseline fails")
            continue
        mine.append(e)
    if problems:
        raise BaselineError("; ".join(problems))
    b = Baseline(gate, mine)
    b.note_claimed(set())
    return b


def _selftest() -> int:
    """Proves a baseline CAN suppress, CANNOT be unowned, CANNOT be expired, and is EXACT."""
    import tempfile

    failed = 0

    def check(why: str, ok: bool, detail: str) -> None:
        nonlocal failed
        print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {detail}")
        failed += 0 if ok else 1

    good = {"gate": "g", "matches": "a/b.ps1", "reason": "r", "owner": "lead-agent",
            "clears_when": "c", "expires": "2099-01-01", "finding": "IMP-0439"}

    def write(root: Path, entries: list[dict]) -> None:
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "config/gate-baselines.json").write_text(
            json.dumps({"baselines": entries}), encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        b = load_baselines(root, "g")
        check("an ABSENT file means no baselines, not an error (the steady state)",
              b.entries == [] and b.excuses("a/b.ps1") is None, "no file -> 0 entries")

        write(root, [good])
        b = load_baselines(root, "g")
        check("a valid entry covers its key and the citation names owner, expiry and remedy",
              b.excuses("a/b.ps1") is not None and "lead-agent" in b.cite("a/b.ps1")
              and "2099-01-01" in b.cite("a/b.ps1") and "clears when" in b.cite("a/b.ps1"),
              b.cite("a/b.ps1").strip()[:90])

        check("matching is EXACT — a baseline must not silently cover a neighbour",
              b.excuses("a/b.ps1.bak") is None and b.excuses("b.ps1") is None,
              "substring keys not covered")

        check("a baseline for ANOTHER gate does not apply here",
              load_baselines(root, "other").entries == [], "gate-scoped")

        for field in ("owner", "clears_when", "expires", "reason"):
            bad = dict(good)
            bad.pop(field)
            write(root, [bad])
            raised = False
            try:
                load_baselines(root, "g")
            except BaselineError as exc:
                raised = field in str(exc)
            check(f"an entry with no '{field}' FAILS rather than suppressing anything",
                  raised, f"raised={raised}")

        write(root, [dict(good, expires="2020-01-01")])
        raised = False
        try:
            load_baselines(root, "g")
        except BaselineError as exc:
            raised = "EXPIRED" in str(exc)
        check("an EXPIRED entry FAILS — this is what stops a permanent waiver", raised,
              f"raised={raised}")

        write(root, [dict(good, expires="not-a-date")])
        raised = False
        try:
            load_baselines(root, "g")
        except BaselineError:
            raised = True
        check("an unparseable expiry FAILS rather than being treated as absent", raised,
              f"raised={raised}")

        (root / "config/gate-baselines.json").write_text("{not json", encoding="utf-8")
        raised = False
        try:
            load_baselines(root, "g")
        except BaselineError:
            raised = True
        check("a malformed file FAILS — a gate must never skip its baseline check silently",
              raised, f"raised={raised}")

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
