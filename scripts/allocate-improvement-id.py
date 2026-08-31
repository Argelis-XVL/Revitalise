#!/usr/bin/env python3
"""Allocate the next `IMP-nnnn` id — and optionally append the entry — without a collision.

Why this script exists
----------------------
`skills/how-to-log-an-improvement.md` has said since 2026-08-19 (`IMP-0080`) to take a finding
id from the MAXIMUM across the whole log and to re-read it immediately before appending, because
two agent sessions can be live in this repository at once and it sits on a synced SharePoint path.

That rule is prose, and prose has now failed six times:

  IMP-0080  2026-08-19  the founding incident — IMP-0074 written twice, and CI never reported it
                        because ci.yml was invalid that day (IMP-0074's own defect)
  IMP-0301  2026-08-25  an id read minutes earlier was already taken
  IMP-0312  2026-08-25  appended as IMP-0311, removed, re-appended
  IMP-0339  2026-08-26  same race, plan-agent
  IMP-0375  2026-08-27  reassigned from IMP-0366 by hand, mid-session
  IMP-0369  2026-08-27  TWO live duplicate pairs at once (IMP-0368 and IMP-0369)

`skills/how-to-promote-a-finding.md`'s altitude rule forbids a seventh instance patch. This is
the generalisation: the read-the-maximum step becomes a command instead of a thing to remember.

How the race is actually closed
-------------------------------
Reading the maximum and appending are two operations, and the gap between them is the race. This
script closes it with an advisory lock (`fcntl.flock`) held across BOTH, so two cooperating
processes on the same machine serialise instead of interleaving. The append itself is a single
`os.write` to a descriptor opened `O_APPEND`, which POSIX makes atomic with respect to other
writers — so a partial line can never appear even if the lock is unavailable.

RESIDUAL, stated because it is real: `flock` coordinates processes on ONE machine. It cannot
coordinate two machines syncing the same SharePoint path. That case is caught rather than
prevented — `generate-known-failure-modes.py` now refuses over a duplicate id (`IMP-0369`), so
a collision surfaces at the next digest run instead of at the next commit.

Usage
-----
    python3 scripts/allocate-improvement-id.py                  # print the next free id
    python3 scripts/allocate-improvement-id.py --append e.json   # set its id, append, validate
    python3 scripts/allocate-improvement-id.py --selftest        # incl. a concurrency fixture

With `--append`, the entry file may omit `id` entirely or carry a placeholder; whatever is there
is overwritten with the id allocated inside the lock. That is the point: the id you were going to
guess is the one thing this script will not let you supply.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover — Windows; the O_APPEND write still applies
    fcntl = None  # type: ignore[assignment]

LOG = Path("logs/improvement-log.jsonl")
ID_PATTERN = re.compile(r"^IMP-(\d{4})$")


def max_id(log_path: Path) -> int:
    """The highest id in the WHOLE file, never `tail -1`.

    `tail -1` is what IMP-0080 was written against: entries are not appended in id order (this
    log has several stretches where they are not), so the last line is routinely not the maximum.
    """
    if not log_path.exists():
        return 0
    highest = 0
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # a malformed line is the validator's problem, not the allocator's
        m = ID_PATTERN.match(str(row.get("id", "")))
        if m:
            highest = max(highest, int(m.group(1)))
    return highest


def format_id(n: int) -> str:
    return f"IMP-{n:04d}"


def _open_locked(log_path: Path):
    """A descriptor on the log, O_APPEND, with an exclusive advisory lock if available."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(log_path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def allocate(log_path: Path) -> str:
    """The next free id, read under the lock so a concurrent allocate cannot see the same one."""
    fd = _open_locked(log_path)
    try:
        return format_id(max_id(log_path) + 1)
    finally:
        os.close(fd)  # releases the flock


def append(log_path: Path, entry: dict) -> str:
    """Allocate and append inside ONE critical section. Returns the id written."""
    fd = _open_locked(log_path)
    try:
        allocated = format_id(max_id(log_path) + 1)
        entry = {**entry, "id": allocated}
        # `id` first so the file stays readable; json.dumps with no spaces matches the log's style.
        ordered = {"id": allocated, **{k: v for k, v in entry.items() if k != "id"}}
        line = json.dumps(ordered, ensure_ascii=False) + "\n"
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
        return allocated
    finally:
        os.close(fd)


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_ENTRY = {
    "ts": "2026-08-28T00:00", "agent": "fixture", "feature": "fixture", "class": "fixture",
    "severity": "friction", "cost": "none", "what": "fixture", "expected": "fixture",
    "root_cause": "fixture", "detected_by": "agent-self", "observable_at": "n/a",
    "why_it_was_never_caught": "fixture", "class_instance_of": "fixture",
    "lesson": "fixture", "status": "NEW",
}


def _selftest() -> int:
    failures = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}")
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "log.jsonl"

        # 1. Empty / absent log.
        check("absent log allocates IMP-0001", allocate(p), "IMP-0001")

        # 2. The maximum is taken from the WHOLE file, not the last line — IMP-0080's actual defect.
        p.write_text(
            json.dumps({**_ENTRY, "id": "IMP-0007"}) + "\n"
            + json.dumps({**_ENTRY, "id": "IMP-0009"}) + "\n"
            + json.dumps({**_ENTRY, "id": "IMP-0003"}) + "\n",  # out of order, deliberately
            encoding="utf-8")
        check("max ignores tail -1 ordering", allocate(p), "IMP-0010")

        # 3. Append writes the allocated id, overriding whatever the caller guessed.
        got = append(p, {**_ENTRY, "id": "IMP-0002"})   # a guess that would have collided
        check("append overrides a colliding guess", got, "IMP-0010")
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        check("append added exactly one line", len(rows), 4)
        check("appended entry carries the allocated id", rows[-1]["id"], "IMP-0010")
        check("appended entry keeps its payload", rows[-1]["what"], "fixture")

        # 4. A malformed line must not stop allocation (it is the validator's problem).
        with p.open("a", encoding="utf-8") as fh:
            fh.write("{not json\n")
        check("malformed line does not break allocation", allocate(p), "IMP-0011")

        # 5. CONCURRENCY — the fixture the prose rule never had. N processes append at once;
        #    every id must be distinct, which is the property six findings say prose cannot hold.
        p2 = Path(td) / "concurrent.jsonl"
        p2.write_text(json.dumps({**_ENTRY, "id": "IMP-0100"}) + "\n", encoding="utf-8")
        script = Path(__file__).resolve()
        import subprocess
        entry_file = Path(td) / "e.json"
        entry_file.write_text(json.dumps(_ENTRY), encoding="utf-8")
        procs = [subprocess.Popen(
            [sys.executable, str(script), "--append", str(entry_file), "--log", str(p2),
             "--no-validate", "--quiet"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) for _ in range(8)]
        for pr in procs:
            pr.wait()
        rows2 = [json.loads(l) for l in p2.read_text().splitlines() if l.strip()]
        ids = [r["id"] for r in rows2]
        check("8 concurrent appends produced 9 lines", len(rows2), 9)
        check("8 concurrent appends produced 0 duplicate ids", len(ids) - len(set(ids)), 0)
        check("concurrent ids are contiguous", sorted(ids)[-1], "IMP-0108")

    print()
    if failures:
        print(f"allocate-improvement-id: SELFTEST FAILED — {len(failures)} failure(s): "
              f"{', '.join(failures)}", file=sys.stderr)
        return 1
    print("allocate-improvement-id: SELFTEST OK — 11 fixtures, including an 8-way concurrent "
          "append that the prose rule this script replaces has failed six times.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=Path, default=LOG)
    ap.add_argument("--append", type=Path, metavar="ENTRY.json",
                    help="a JSON object to append; its id is allocated inside the lock")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the post-append validator run (used by the concurrency fixture)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    if not args.append:
        print(allocate(args.log))
        return 0

    if not args.append.exists():
        print(f"allocate-improvement-id: {args.append} does not exist", file=sys.stderr)
        return 2
    try:
        entry = json.loads(args.append.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"allocate-improvement-id: {args.append} is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(entry, dict):
        print(f"allocate-improvement-id: {args.append} must hold a JSON OBJECT", file=sys.stderr)
        return 2

    allocated = append(args.log, entry)
    if not args.quiet:
        print(f"allocate-improvement-id: appended {allocated} to {args.log}")

    if args.no_validate:
        return 0

    # Validate immediately, in this process, so the appending agent cannot walk away from a
    # log it just broke. This is the other half of IMP-0369.
    import subprocess
    validator = Path(__file__).resolve().parent / "verify-improvement-log.py"
    if not validator.exists():
        return 0
    result = subprocess.run([sys.executable, str(validator)], capture_output=False)
    if result.returncode != 0 and not args.quiet:
        print(f"\nallocate-improvement-id: {allocated} was appended, and the log is now RED "
              f"(above). Fix it before reporting your IMPROVEMENT LOG line — regenerating the "
              f"digest is NOT validation (IMP-0369).", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
