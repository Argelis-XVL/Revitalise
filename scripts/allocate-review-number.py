#!/usr/bin/env python3
"""Claim the next free `<date>-improvement-review[-N].md` filename — without a collision.

Why this script exists
----------------------
`agents/improvement-agent.md`'s Outputs table names the review document
`docs/improvements/<YYYY-MM-DD>-improvement-review.md`, and every dispatch has derived the `-N`
suffix the same way: list the directory, find the highest number, add one. Two dispatches that
list the directory before either writes compute the SAME number.

This is not a hypothetical, and it is not a new class. It is `IMP-0080`'s race — two live sessions
reading the same "current max" and computing the same "next" — arriving at a second resource:

  IMP-0539  2026-08-31  Groups 1 and 2 both chose `2026-08-31-improvement-review-7.md`
  IMP-0540  2026-08-31  corrects IMP-0539: nothing was actually overwritten, because the losing
                        dispatch had not yet written its file. A NEAR-MISS, not a loss
  IMP-0541  2026-08-31  the race itself, stated without the false clobber claim: had both reached
                        step 8 before either wrote, they would have collided exactly as two
                        sessions once collided on the log's next id

The id space next door was mechanised for exactly this after prose failed SIX times — see
`scripts/allocate-improvement-id.py`'s own header (IMP-0080, IMP-0301, IMP-0312, IMP-0339,
IMP-0375, IMP-0369). `skills/how-to-promote-a-finding.md`'s altitude rule forbids answering a
second instance of a mechanised class with a third paragraph of prose. This is that mechanisation.

How the race is actually closed
-------------------------------
Cheaper than next door, because here the CLAIM and the CREATE are the same operation.
`allocate-improvement-id.py` needs an advisory lock, because reading the maximum id and appending
a line are two operations with a gap between them. A filename has no such gap:

    os.open(path, O_CREAT | O_EXCL)

either creates the file or raises `FileExistsError`, atomically, with no lock. The loser of the
race does not corrupt anything — it simply gets an exception and tries the next number. So this
script holds no lock at all, and cannot leave a stale one behind if it is killed.

The stub it writes is the point. A reserved-but-empty name is what makes the claim VISIBLE to the
next dispatch's directory listing, which is the only thing the losing dispatch ever consults.

RESIDUAL, stated because it is real: `O_EXCL` is atomic per FILESYSTEM. It cannot coordinate two
machines syncing the same SharePoint path, which is where this repository lives. That case stays
caught rather than prevented — two stubs with the same name would surface as a sync conflict copy,
not as a silent overwrite. This is the same residual `allocate-improvement-id.py` records for
`flock`, and it is a smaller residual than the one it replaces: today the losing dispatch writes
its whole document over the winner's.

Usage
-----
    python3 scripts/allocate-review-number.py              # claim the next free name for today
    python3 scripts/allocate-review-number.py --peek       # compute it, claim nothing
    python3 scripts/allocate-review-number.py --date 2026-08-31
    python3 scripts/allocate-review-number.py --selftest   # incl. a concurrency fixture

`--peek` exists for measurement and for dry runs. It is deliberately NOT the default: a number you
computed but did not claim is precisely the thing that caused IMP-0539.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path

REVIEWS_DIR = Path("docs/improvements")

# `<date>-improvement-review.md` is number 1; `-N.md` is number N. Anchored at both ends so a
# neighbouring document in the same directory — a capability design, a failure analysis — can
# never be read as a review. `2026-08-31-capability-design-agent-system-optimisation.md` is the
# live example this anchoring exists for.
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-improvement-review(?:-(\d+))?\.md$")

STUB = """\
# Improvement Review — {date} ({n})

**RESERVED** — a dispatch claimed this filename at draft start and has not yet written its review.

This stub is not an empty file by accident. It is the claim itself: a concurrent
`improvement-agent` dispatch computing "the next unused review number" reads this directory, and
an unclaimed number is one two dispatches will both take (`IMP-0539`, `IMP-0541`). Claimed with
`scripts/allocate-review-number.py`.

If this stub is still here with no review under it, a dispatch was interrupted between claiming
its filename and writing its draft. That is recoverable and visible, which is the point — the
failure it replaces was invisible.
"""


def _existing_numbers(reviews_dir: Path, date: str) -> set[int]:
    """Every review number already present for `date`, from the directory listing."""
    found: set[int] = set()
    if not reviews_dir.exists():
        return found
    for p in reviews_dir.iterdir():
        m = NAME_RE.match(p.name)
        if m and m.group(1) == date:
            found.add(int(m.group(2)) if m.group(2) else 1)
    return found


def _path_for(reviews_dir: Path, date: str, n: int) -> Path:
    suffix = "" if n == 1 else f"-{n}"
    return reviews_dir / f"{date}-improvement-review{suffix}.md"


def peek(reviews_dir: Path, date: str) -> int:
    """The next free number, computed and NOT claimed. Never call this to pick a name to write."""
    taken = _existing_numbers(reviews_dir, date)
    n = 1
    while n in taken:
        n += 1
    return n


def claim(reviews_dir: Path, date: str, max_attempts: int = 200) -> tuple[Path, int]:
    """Claim the next free name atomically. Returns (path, number).

    The loop is the whole mechanism: `O_EXCL` tells us we lost a race, and losing costs one
    increment rather than a clobbered document.
    """
    reviews_dir.mkdir(parents=True, exist_ok=True)
    n = peek(reviews_dir, date)
    for _ in range(max_attempts):
        path = _path_for(reviews_dir, date, n)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            n += 1
            continue
        try:
            os.write(fd, STUB.format(date=date, n=n).encode("utf-8"))
        finally:
            os.close(fd)
        return path, n
    raise RuntimeError(
        f"allocate-review-number: {max_attempts} consecutive names taken for {date} — "
        f"that is not a race, it is a wrong date or a corrupted directory."
    )


# ── selftest ──────────────────────────────────────────────────────────────────────────────────

def selftest() -> int:
    import multiprocessing
    import tempfile

    failures: list[str] = []
    checks = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not cond:
            failures.append(msg)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        date = "2026-08-31"

        # 1. empty directory → 1, and the unsuffixed name
        p, n = claim(d, date)
        check(n == 1, f"first claim should be 1, got {n}")
        check(p.name == f"{date}-improvement-review.md", f"first name wrong: {p.name}")
        check(p.read_text().startswith("# Improvement Review"), "stub not written")

        # 2. second claim → 2, suffixed
        p2, n2 = claim(d, date)
        check(n2 == 2, f"second claim should be 2, got {n2}")
        check(p2.name == f"{date}-improvement-review-2.md", f"second name wrong: {p2.name}")

        # 3. a neighbouring non-review document must not be counted
        (d / f"{date}-capability-design-agent-system-optimisation.md").write_text("x")
        (d / f"{date}-failure-analysis.md").write_text("x")
        check(peek(d, date) == 3, f"neighbouring docs miscounted: peek={peek(d, date)}")

        # 4. a different date is a different sequence
        check(peek(d, "2026-09-01") == 1, "dates must not share a sequence")

        # 5. a GAP is not reused — 1 and 2 exist, 4 exists, next is 3 then 5
        (d / f"{date}-improvement-review-4.md").write_text("x")
        check(peek(d, date) == 3, f"expected the gap at 3, got {peek(d, date)}")
        _, n5 = claim(d, date)
        check(n5 == 3, f"gap should be claimed, got {n5}")
        check(peek(d, date) == 5, f"after filling 3, next is 5, got {peek(d, date)}")

        # 6. --peek claims NOTHING
        before = sorted(x.name for x in d.iterdir())
        peek(d, date)
        check(sorted(x.name for x in d.iterdir()) == before, "peek must not create a file")

    # 7. THE CONCURRENCY FIXTURE — the one assertion this script exists for.
    #    Without O_EXCL every worker computes the same number and they collide. This is the
    #    fixture that FAILS if the mechanism is removed, which is what makes it load-bearing
    #    rather than decorative (agents/improvement-agent.md: a green selftest must prove the
    #    thing CAN fail).
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        date = "2026-09-01"
        workers = 12
        with multiprocessing.Pool(workers) as pool:
            results = pool.starmap(_claim_worker, [(str(d), date)] * workers)
        nums = [r for r in results if isinstance(r, int)]
        errs = [r for r in results if not isinstance(r, int)]
        check(not errs, f"workers raised: {errs[:3]}")
        check(len(nums) == workers, f"expected {workers} claims, got {len(nums)}")
        check(len(set(nums)) == workers,
              f"COLLISION: {workers} concurrent claims produced {len(set(nums))} distinct "
              f"numbers — {sorted(nums)}")
        check(sorted(nums) == list(range(1, workers + 1)),
              f"claims should be exactly 1..{workers}, got {sorted(nums)}")
        files = [x for x in d.iterdir() if NAME_RE.match(x.name)]
        check(len(files) == workers, f"expected {workers} files on disk, got {len(files)}")

    if failures:
        for f in failures:
            print(f"allocate-review-number --selftest: FAIL — {f}", file=sys.stderr)
        print(f"\nallocate-review-number --selftest: FAILED "
              f"({len(failures)} of {checks} assertion(s)).", file=sys.stderr)
        return 1
    print(f"allocate-review-number --selftest: OK — {checks} assertion(s), including "
          f"12 concurrent claims yielding 12 distinct numbers.")
    return 0


def _claim_worker(dirname: str, date: str):
    """Module-level so multiprocessing can pickle it."""
    try:
        _, n = claim(Path(dirname), date)
        return n
    except Exception as exc:  # pragma: no cover — reported as a failure by the fixture
        return f"{type(exc).__name__}: {exc}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--dir", type=Path, default=REVIEWS_DIR)
    p.add_argument("--date", default=None,
                   help="YYYY-MM-DD; defaults to today's local date")
    p.add_argument("--peek", action="store_true",
                   help="print the next free name without claiming it")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()

    date = args.date or _dt.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        print(f"allocate-review-number: --date must be YYYY-MM-DD, got {date!r}", file=sys.stderr)
        return 2

    if args.peek:
        n = peek(args.dir, date)
        print(_path_for(args.dir, date, n))
        return 0

    path, n = claim(args.dir, date)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
