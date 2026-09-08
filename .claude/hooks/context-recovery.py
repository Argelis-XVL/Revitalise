#!/usr/bin/env python3
"""SessionStart hook: surface the latest context-preserve.py snapshot, if recent.

Reads logs/handover/latest.json (written by context-preserve.py's PreCompact hook) and,
when it exists and is fresh enough to plausibly belong to the session being resumed,
injects a short summary as additionalContext -- branch, HEAD, uncommitted files, and the
tail of routing/build/pipeline logs at the moment of the last compaction. This does not
replace reading agents/WORKFLOW.md's own state (routing.log, wbs-state.json); it exists
so a resumed session doesn't have to run those checks blind before knowing there even
was a prior compaction to reconcile against.

A snapshot older than STALE_AFTER_SECONDS is treated as belonging to a different, long-
finished session and is not injected -- surfacing it would be more misleading than
saying nothing (the branch/HEAD it names may no longer exist).

Self-test:  python3 .claude/hooks/context-recovery.py --selftest
"""

from __future__ import annotations

import json
import os
import sys
import time

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
STALE_AFTER_SECONDS = 24 * 60 * 60  # a day; compaction handover is a same-session concern
MAX_TAIL_LINE_CHARS = 220  # this repo's log lines are dense prose entries, not short lines;
                           # injecting one raw would cost hundreds of tokens per session start


def project_dir() -> str:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.realpath(env)
    return os.path.realpath(os.path.join(HOOK_DIR, os.pardir, os.pardir))


def latest_snapshot_path(root: str) -> str:
    return os.path.join(root, "logs", "handover", "latest.json")


def load_snapshot(root: str) -> dict | None:
    path = latest_snapshot_path(root)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def is_stale(snapshot: dict, now: float | None = None) -> bool:
    captured_at = snapshot.get("captured_at")
    if not captured_at:
        return True
    try:
        captured_ts = time.mktime(time.strptime(captured_at[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return True
    return (now if now is not None else time.time()) - captured_ts > STALE_AFTER_SECONDS


def render(snapshot: dict) -> str:
    git = snapshot.get("git", {})
    status = git.get("status_short") or []
    lines = [
        "Context handover from a prior compaction (context-preserve.py):",
        f"- captured: {snapshot.get('captured_at', 'unknown')} (trigger: {snapshot.get('trigger', 'unknown')})",
        f"- branch/HEAD at capture: {git.get('branch', 'unknown')} @ {git.get('head', 'unknown')}",
    ]
    if status:
        lines.append(f"- uncommitted files at capture ({len(status)}): " + "; ".join(status[:10]))
    for name, tail in (snapshot.get("log_tails") or {}).items():
        if tail:
            last = tail[-1]
            if len(last) > MAX_TAIL_LINE_CHARS:
                last = last[:MAX_TAIL_LINE_CHARS] + f"... ({len(tail[-1])} chars, see {name})"
            lines.append(f"- tail of {name}: {last}")
    lines.append(
        "This is filesystem-derived, not a memory of the conversation -- verify against "
        "current git status and agents/WORKFLOW.md's own state before acting on it."
    )
    return "\n".join(lines)


def main() -> int:
    raw = sys.stdin.read()
    try:
        json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        pass  # payload isn't needed beyond confirming the hook received valid JSON

    root = project_dir()
    snapshot = load_snapshot(root)
    if not snapshot or is_stale(snapshot):
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": render(snapshot),
        }
    }))
    return 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    ok = 0
    fail = 0

    def check(label, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1
        else:
            fail += 1
            print(f"FAIL {label}: got {got!r}, want {want!r}")

    fresh = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time())),
        "trigger": "auto",
        "git": {"branch": "generalise-engine", "head": "abc1234 msg", "status_short": ["M foo.py"]},
        "log_tails": {"logs/routing.log": ["last line"]},
    }
    check("fresh snapshot not stale", is_stale(fresh), False)

    old = dict(fresh, captured_at=time.strftime(
        "%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - STALE_AFTER_SECONDS - 3600)
    ))
    check("day-old snapshot is stale", is_stale(old), True)

    check("missing captured_at is stale", is_stale({}), True)
    check("malformed captured_at is stale", is_stale({"captured_at": "not-a-date"}), True)

    rendered = render(fresh)
    check("render mentions branch", "generalise-engine" in rendered, True)
    check("render mentions trigger", "auto" in rendered, True)
    check("render includes disclaimer", "not a memory of the conversation" in rendered, True)

    empty_render = render({})
    check("render on empty snapshot does not crash", isinstance(empty_render, str), True)

    print(f"context-recovery selftest: {ok} passed, {fail} failed")
    return 1 if fail else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
