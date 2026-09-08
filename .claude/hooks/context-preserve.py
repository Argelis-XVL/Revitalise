#!/usr/bin/env python3
"""PreCompact hook: snapshot cheap, filesystem-derived task context before compaction.

Part of Phase 2 of docs/improvements/IMPLEMENTATION-PLAN.md (audit rec 1). The
"fourth/fifth case" in agents/WORKFLOW.md exists because a dispatch that dies or a
session that compacts loses track of what it was doing mid-task, forcing a human to
manually reconcile live state. This hook does not (and cannot) see the conversation
transcript -- a hook gets no access to that -- so it snapshots what a *later* session
COULD reconstruct only slowly by re-running git/log commands: current branch and HEAD,
uncommitted changes, the tail of the routing/build/pipeline logs, and any WBS task ids
mentioned in those tails. context-recovery.py reads this back and injects it as
additionalContext on the next SessionStart.

This is an aid, not a substitute for `git commit` between hops -- a hook cannot commit
work for you, it can only tell the next session where to look.

Self-test:  python3 .claude/hooks/context-preserve.py --selftest
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_TAIL_LINES = 5
LOGS_TO_SAMPLE = (
    "logs/routing.log",
    "logs/build.log",
    "logs/pipeline.log",
    "logs/pm.log",
)


def project_dir() -> str:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.realpath(env)
    return os.path.realpath(os.path.join(HOOK_DIR, os.pardir, os.pardir))


def handover_dir(root: str) -> str:
    return os.path.join(root, "logs", "handover")


def run(cmd: list[str], cwd: str) -> str:
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=5, check=False
        )
        return out.stdout.strip()
    except Exception as exc:  # noqa: BLE001 -- a snapshot must never crash the compaction
        return f"<unavailable: {exc}>"


def tail_lines(path: str, n: int) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        return [line.rstrip("\n") for line in lines[-n:]]
    except OSError:
        return []


def build_snapshot(root: str, payload: dict) -> dict:
    return {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "trigger": payload.get("trigger") or payload.get("custom_instructions") or "unknown",
        "session_id": payload.get("session_id") or "unknown",
        "git": {
            "branch": run(["git", "branch", "--show-current"], root),
            "head": run(["git", "log", "-1", "--oneline"], root),
            "status_short": run(["git", "status", "--short"], root).splitlines()[:50],
        },
        "log_tails": {
            name: tail_lines(os.path.join(root, name), LOG_TAIL_LINES)
            for name in LOGS_TO_SAMPLE
            if os.path.exists(os.path.join(root, name))
        },
    }


def write_snapshot(root: str, snapshot: dict) -> str:
    out_dir = handover_dir(root)
    os.makedirs(out_dir, exist_ok=True)
    session_id = snapshot.get("session_id") or "unknown"
    safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
    path = os.path.join(out_dir, f"{safe_id}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
    # also keep a rolling "latest" pointer for the common case of one active session
    latest_path = os.path.join(out_dir, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
    return path


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0  # a hook that cannot parse its input must not block compaction

    root = project_dir()
    try:
        snapshot = build_snapshot(root, payload)
        write_snapshot(root, snapshot)
    except Exception:  # noqa: BLE001 -- never block compaction on a snapshot failure
        pass
    return 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    import tempfile

    ok = 0
    fail = 0

    def check(label, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1
        else:
            fail += 1
            print(f"FAIL {label}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "logs"), exist_ok=True)
        with open(os.path.join(tmp, "logs", "routing.log"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(f"line {i}" for i in range(30)))

        payload = {"session_id": "abc/123", "trigger": "auto"}
        snap = build_snapshot(tmp, payload)
        check("session_id carried through", snap["session_id"], "abc/123")
        check("trigger carried through", snap["trigger"], "auto")
        check("log tail length capped", len(snap["log_tails"]["logs/routing.log"]), LOG_TAIL_LINES)
        check(
            "log tail is the actual tail",
            snap["log_tails"]["logs/routing.log"][-1],
            "line 29",
        )
        check("missing logs omitted", "logs/build.log" in snap["log_tails"], False)

        path = write_snapshot(tmp, snap)
        check("snapshot file uses sanitized id", os.path.basename(path), "abc_123.json")
        check("snapshot written", os.path.exists(path), True)
        check("latest pointer written", os.path.exists(os.path.join(tmp, "logs", "handover", "latest.json")), True)

        with open(path, encoding="utf-8") as fh:
            reloaded = json.load(fh)
        check("round-trips through JSON", reloaded["session_id"], "abc/123")

    # a payload with no session_id must not crash path construction
    empty_snap = build_snapshot(os.getcwd(), {})
    check("empty payload session_id fallback", empty_snap["session_id"], "unknown")

    print(f"context-preserve selftest: {ok} passed, {fail} failed")
    return 1 if fail else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
