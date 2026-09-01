#!/usr/bin/env python3
"""PreToolUse hook: only improvement-agent may write the system's own rules.

`agents/improvement-agent.md` has claimed since 2026-08-17 that it is "the only agent
that edits agents/, constraints/, skills/ and knowledge/". Until this hook existed that
was an unenforced declaration: any dispatched subagent could Edit or Write those paths
and nothing would stop it. This is change A1 of improvement review 9 (WS-A).

DENY when ALL THREE hold:
  1. `agent_id` is present in the hook input   -> the call comes from a dispatched
     subagent, not the root session;
  2. `agent_type` is not `improvement-agent`;
  3. the resolved `tool_input.file_path` is under agents/, constraints/, skills/ or
     knowledge/ inside the project directory.

Everything else is allowed by staying silent (exit 0, no output).

THREE HONEST LIMITS, restated here so no reader has to find the review:
  - It binds DISPATCHED AGENTS ONLY. `agent_id` is absent for the root session, so the
    main conversation and the human retain write access to all four directories. That is
    deliberate; it is also narrower than "nobody but improvement-agent".
  - It is NOT A SANDBOX. A subagent running under a permission mode that bypasses the
    permission classifier would not be stopped. `scripts/generate-subagents.py` emits no
    `permissionMode`, so no project agent is in that state today.
  - It protects the FOUR RULE DIRECTORIES only. `scripts/`, `config/` and `contract/`
    are not covered; delivery agents legitimately write some of those.
  - It covers the WRITE TOOLS only. A subagent that writes a protected file through Bash
    (`sed -i`, a heredoc, a python one-liner) is not stopped by this hook, because
    matching a path out of an arbitrary shell command is not decidable. The control is
    "the obvious route is refused, and the refusal names what to do instead", not "the
    write is impossible". Matching Bash on a path regex was considered and rejected: it
    would be the phrase-matching instrument this project has measured at 48-100% false
    five times (agents/improvement-agent.md, corpus-measurement section).

Fixture support: if `.claude/hooks/.fixture-dump.jsonl` EXISTS, every invocation appends
its raw stdin plus the decision to that file. Deleting the file turns dumping off. This
is how the live proof in improvement review 6 (2026-09-01) was obtained, and it is what
lets the proof be re-run after any harness upgrade. It never changes the decision.

Self-test:  python3 .claude/hooks/protect-system-rules.py --selftest
"""

from __future__ import annotations

import json
import os
import sys

PROTECTED_DIRS = ("agents", "constraints", "skills", "knowledge")
PRIVILEGED_AGENT = "improvement-agent"
WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_PATH = os.path.join(HOOK_DIR, ".fixture-dump.jsonl")


def project_dir() -> str:
    """The repository root. CLAUDE_PROJECT_DIR when the harness sets it, else the
    grandparent of this file (.claude/hooks/x.py -> repo root)."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.realpath(env)
    return os.path.realpath(os.path.join(HOOK_DIR, os.pardir, os.pardir))


def protected_path(file_path: str, root: str, cwd: str | None = None) -> str | None:
    """Return the protected top-level directory `file_path` falls under, or None.

    Resolves relative paths against the hook's cwd (the harness runs hooks in the
    project directory) and follows symlinks, so `../Revitalise/agents/x.md` and a
    symlink into agents/ are both caught.
    """
    if not file_path:
        return None
    base = cwd or os.getcwd()
    resolved = os.path.realpath(os.path.join(base, os.path.expanduser(file_path)))
    for name in PROTECTED_DIRS:
        guarded = os.path.realpath(os.path.join(root, name))
        if resolved == guarded or resolved.startswith(guarded + os.sep):
            return name
    return None


def decide(payload: dict, root: str, cwd: str | None = None) -> tuple[bool, str]:
    """(deny, reason). Pure: no I/O, so the self-test exercises the real decision."""
    tool = payload.get("tool_name") or ""
    if tool not in WRITE_TOOLS:
        return False, "not a write tool"

    agent_id = payload.get("agent_id")
    if not agent_id:
        return False, "root session (no agent_id) — not in scope"

    agent_type = payload.get("agent_type") or ""
    if agent_type == PRIVILEGED_AGENT:
        return False, "improvement-agent — permitted"

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    guarded = protected_path(file_path, root, cwd)
    if not guarded:
        return False, "path is not under a protected directory"

    return True, (
        f"BLOCKED by .claude/hooks/protect-system-rules.py: this is a dispatched "
        f"{agent_type or '<unnamed>'} subagent attempting {tool} against {guarded}/, "
        f"which only improvement-agent may write (agents/improvement-agent.md#L12). "
        f"Do not retry, do not route around this, and do not edit the rule file "
        f"yourself. Record the change you wanted as a finding in "
        f"logs/improvement-log.jsonl per skills/how-to-log-an-improvement.md and let "
        f"an improvement review apply it behind APPROVE IMPROVEMENTS."
    )


def dump(payload, deny, reason):
    """Append the raw hook input and the decision, but only when the fixture-dump file
    already exists. Never raises: an unwritable dump must not change a decision."""
    try:
        if not os.path.exists(DUMP_PATH):
            return
        with open(DUMP_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"input": payload, "deny": deny, "reason": reason}) + "\n")
    except Exception:
        pass


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # A hook that cannot parse its input must not block delivery work.
        dump({"unparseable": raw[:2000]}, False, "unparseable input")
        return 0

    deny, reason = decide(payload, project_dir())
    dump(payload, deny, reason)

    if deny:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }))
    return 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    root = os.path.realpath("/tmp/fake-repo")
    ok = 0
    fail = 0

    def check(label, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1
        else:
            fail += 1
            print(f"FAIL {label}: got {got!r}, want {want!r}")

    def d(payload, cwd=root):
        return decide(payload, root, cwd)[0]

    edit = lambda **kw: dict({"tool_name": "Edit"}, **kw)

    # 1. the case this hook exists for
    check("build-agent edits agents/", d(edit(
        agent_id="a1", agent_type="build-agent",
        tool_input={"file_path": "agents/build-agent.md"})), True)
    # 2-4. each remaining protected directory
    for i, name in enumerate(("constraints", "skills", "knowledge"), start=2):
        check(f"build-agent edits {name}/", d(edit(
            agent_id="a1", agent_type="build-agent",
            tool_input={"file_path": f"{name}/x.md"})), True)
    # 5. absolute path form
    check("absolute path", d(edit(
        agent_id="a1", agent_type="test-agent",
        tool_input={"file_path": f"{root}/constraints/technology/technology-constraints.md"})), True)
    # 6. traversal back into a protected directory
    check("traversal", d(edit(
        agent_id="a1", agent_type="test-agent",
        tool_input={"file_path": "src/../agents/plan-agent.md"})), True)
    # 7. the privileged agent is NOT blocked — the hook must not block its own user
    check("improvement-agent allowed", d(edit(
        agent_id="a1", agent_type="improvement-agent",
        tool_input={"file_path": "agents/build-agent.md"})), False)
    # 8. root session (no agent_id) is out of scope by design
    check("root session allowed", d(edit(
        agent_type="build-agent", tool_input={"file_path": "agents/build-agent.md"})), False)
    check("root session, empty agent_id", d(edit(
        agent_id="", agent_type="build-agent",
        tool_input={"file_path": "agents/build-agent.md"})), False)
    # 10. unprotected paths stay writable — delivery work must not be affected
    for p in ("src/app.tsx", "config/x-build.yml", "docs/plans/p.md",
              "scripts/verify-x.py", "logs/improvement-log.jsonl"):
        check(f"unprotected {p}", d(edit(
            agent_id="a1", agent_type="build-agent", tool_input={"file_path": p})), False)
    # 15. a directory whose name merely starts with a protected name
    check("agents-archive not protected", d(edit(
        agent_id="a1", agent_type="build-agent",
        tool_input={"file_path": "agents-archive/old.md"})), False)
    # 16. read tools are never in scope
    check("Read allowed", d(dict(
        tool_name="Read", agent_id="a1", agent_type="build-agent",
        tool_input={"file_path": "agents/build-agent.md"})), False)
    check("Bash not matched", d(dict(
        tool_name="Bash", agent_id="a1", agent_type="build-agent",
        tool_input={"command": "rm agents/build-agent.md"})), False)
    # 18. Write and NotebookEdit are in scope too
    check("Write blocked", d(dict(
        tool_name="Write", agent_id="a1", agent_type="build-agent",
        tool_input={"file_path": "skills/x.md"})), True)
    check("NotebookEdit blocked", d(dict(
        tool_name="NotebookEdit", agent_id="a1", agent_type="build-agent",
        tool_input={"notebook_path": "knowledge/x.ipynb"})), True)
    # 20. degenerate inputs must not crash and must not block
    check("empty payload", d({}), False)
    check("missing file_path", d(edit(
        agent_id="a1", agent_type="build-agent", tool_input={})), False)
    # 22. the deny reason names the mechanism, so a blocked agent knows what to do
    reason = decide(edit(agent_id="a1", agent_type="build-agent",
                         tool_input={"file_path": "agents/x.md"}), root, root)[1]
    check("reason names the hook", "protect-system-rules.py" in reason, True)
    check("reason names the log", "improvement-log.jsonl" in reason, True)

    print(f"protect-system-rules selftest: {ok} passed, {fail} failed")
    return 1 if fail else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
