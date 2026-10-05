#!/usr/bin/env python3
"""Append ONE line to a plain `logs/*.log` file, stamped from the clock.

Why this script exists
----------------------
Every plain log in this system (`routing.log`, `build.log`, `pipeline.log`, `pm.log`, ...) is
one line per action in the form `[YYYY-MM-DD HH:MM] [AGENT] [feature] ...`, and until this script
the agent typed the stamp. On 2026-09-30 five agents typed times up to five and a half hours in
the future across three logs, the day after a written reminder to take the time from `date`
(IMP-0970). A reminder nobody reads at the moment of writing is the wrong altitude; this script
stamps the line from the clock (IMP-0970), so there is no stamp left for the agent to type.

Usage
-----
    python3 scripts/log-line.py logs/routing.log <<'EOF'
    [LEAD] [my-feature] ROUTED_TO:build-agent — reason
    EOF

    python3 scripts/log-line.py --selftest

The line is read from stdin. Use a QUOTED heredoc (`<<'EOF'`) so a backtick or `$` in a summary
is never run as a command by the shell. Line breaks inside the text are joined with a space: one
action is one line.

Refusals (exit 2, nothing written):
  * the target is not under `logs/` or does not end in `.log`;
  * the text already starts with a `[YYYY-MM-DD` stamp — the time is the tool's, never typed;
  * the text is empty.

The append is a single `os.write` on an `O_APPEND` descriptor under an exclusive advisory lock,
so two cooperating processes on one machine cannot interleave. RESIDUAL: the lock does not
coordinate two machines syncing the same path; minute resolution, local time.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover — Windows; the O_APPEND write still applies
    fcntl = None  # type: ignore[assignment]

STAMP_FORMAT = "%Y-%m-%d %H:%M"
PRESTAMPED = re.compile(r"^\s*\[\d{4}-\d{2}-\d{2}")


class Refused(Exception):
    pass


def check_target(target: Path) -> None:
    parts = target.as_posix().split("/")
    if "logs" not in parts[:-1] or target.suffix != ".log":
        raise Refused(f"{target}: only a logs/*.log file is written by this tool")


def build_line(text: str, now: datetime | None = None) -> str:
    joined = " ".join(part.strip() for part in text.splitlines() if part.strip())
    if not joined:
        raise Refused("empty line: nothing to write")
    if PRESTAMPED.match(joined):
        raise Refused("the text already starts with a [YYYY-MM-DD stamp; leave it out — "
                      "the time is the tool's, never typed (IMP-0970)")
    return f"[{(now or datetime.now()).strftime(STAMP_FORMAT)}] {joined}"


def append_line(target: Path, line: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(target), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, (line + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def _selftest() -> int:
    failures: list[str] = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}")
        if not ok:
            failures.append(name)

    fixed = datetime(2026, 10, 5, 9, 30)
    check("stamps from the clock",
          build_line("[LEAD] [x] ROUTED_TO:build-agent", fixed),
          "[2026-10-05 09:30] [LEAD] [x] ROUTED_TO:build-agent")
    check("joins line breaks", build_line("[A] one\n  two\n", fixed), "[2026-10-05 09:30] [A] one two")
    check("keeps backticks and $ literal", build_line("[A] ran `pac` with $HOME", fixed),
          "[2026-10-05 09:30] [A] ran `pac` with $HOME")
    for name, text in (("refuses a pre-stamped line", "[2026-10-05 09:00] [A] x"),
                       ("refuses an empty line", "  \n ")):
        try:
            build_line(text, fixed)
            check(name, "written", "refused")
        except Refused:
            check(name, "refused", "refused")
    for name, target in (("refuses a non-log path", Path("logs/improvement-log.jsonl")),
                         ("refuses a path outside logs/", Path("docs/x.log"))):
        try:
            check_target(target)
            check(name, "accepted", "refused")
        except Refused:
            check(name, "refused", "refused")
    with tempfile.TemporaryDirectory() as td:
        t = Path(td) / "logs" / "x.log"
        check_target(t)
        append_line(t, build_line("[A] first", fixed))
        append_line(t, build_line("[A] second", fixed))
        check("appends one line per call", t.read_text(encoding="utf-8").count("\n"), 2)

    print()
    if failures:
        print(f"log-line: SELFTEST FAILED — {len(failures)} failure(s): {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print("log-line: SELFTEST OK — 8 fixtures")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", type=Path, help="a logs/*.log file")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.target is None:
        ap.error("a logs/*.log target is required")
    try:
        check_target(args.target)
        line = build_line(sys.stdin.read())
    except Refused as exc:
        print(f"log-line: REFUSED — {exc}", file=sys.stderr)
        return 2
    append_line(args.target, line)
    print(f"log-line: wrote to {args.target}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
