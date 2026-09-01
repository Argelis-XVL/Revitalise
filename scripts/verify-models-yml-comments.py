#!/usr/bin/env python3
"""SOFT lint: a comment beside a PROPAGATING key in config/models.yml never reaches the agent.

WHAT THIS GUARDS, AND WHY IT CURRENTLY FINDS NOTHING
----------------------------------------------------
`config/models.yml` is two things at once, and only one of them propagates. It is a config a human
reads and annotates, AND it is the input to `scripts/generate-subagents.py`, which parses it with a
YAML loader and emits `.claude/agents/<name>.md`. **The loader keeps VALUES and discards COMMENTS.**

So a rule a dispatched agent must obey has to live INSIDE the string value. Written in a comment
above the key, it reaches the human editing `config/models.yml` and never the agent reading
`.claude/agents/<name>.md`. `--check` stays GREEN either way: a comment-only edit leaves the
generated files genuinely current and merely silent, so no existing gate can tell a dropped comment
from one that was never meant to propagate. `IMP-0310` is one change applied twice for exactly this.

**Measured 2026-09-01: this lint reports 0 findings against the current `config/models.yml`.** That
is the honest result, not a clean-run claim — the historical instance was fixed before this script
existed. This is a REGRESSION GUARD, not a repair. State that when it first fires, or whoever sees
it will read a legitimate human note as an error.

WHY SOFT, AND WHY IT WILL STAY SOFT
-----------------------------------
A comment beside these keys is *sometimes* legitimately a note to a human — "de-escalation was
measured and rejected here", "see review 9" — and nothing in the text distinguishes that from a
rule the agent needed. A HARD block would therefore generate exactly the false positives that teach
people to route around a gate (`IMP-0181`). This reports; it does not decide.

Run:
    python3 scripts/verify-models-yml-comments.py                 # default: config/models.yml
    python3 scripts/verify-models-yml-comments.py --selftest      # proves it CAN fail
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MODELS = Path("config/models.yml")

# The three keys `scripts/generate-subagents.py` actually reads into the generated agent file.
# A comment above any OTHER key is harmless: nothing about that key propagates either, so the
# comment is not competing with a value that does.
PROPAGATING_KEYS = ("tier:", "escalate_to_strategic_when:", "de_escalate_to_mechanical_when:")


def scan(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no_of_key, key_line, comment_line) for each propagating key preceded by a comment.

    Walks UPWARD through a contiguous comment block so a multi-line comment is reported once, at its
    first line — reporting every line of a six-line comment as six findings is how a SOFT check
    becomes noise nobody reads.
    """
    lines = text.splitlines()
    out: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        if not any(line.strip().startswith(k) for k in PROPAGATING_KEYS):
            continue
        j = i - 1
        if j < 0 or not lines[j].strip().startswith("#"):
            continue
        while j - 1 >= 0 and lines[j - 1].strip().startswith("#"):
            j -= 1
        out.append((i + 1, line.strip(), lines[j].strip()))
    return out


def report(path: Path, findings: list[tuple[int, str, str]]) -> None:
    for lineno, key, comment in findings:
        print(f"  SOFT  {path}:{lineno}: {key[:60]}")
        print(f"          preceded by a comment beginning {comment[:70]!r}")
        print(f"          If that text is a rule the DISPATCHED AGENT must obey, it is being "
              f"discarded by the YAML loader — move it inside the string value. If it is a note "
              f"for a human reading this file, it is fine as it is; this check cannot tell the "
              f"difference and does not try (IMP-0310).", file=sys.stderr)


def selftest() -> int:
    """Prove the check can fail, and that it does not fire on the shapes it must not."""
    ok = True

    def check(label: str, cond: bool) -> None:
        nonlocal ok
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            ok = False

    # (1) fires on a comment above a propagating key
    bad = "agents:\n  plan-agent:\n    # plan-agent must always cite the SDD section\n    tier: standard\n"
    check("fires on a comment directly above `tier:`", len(scan(bad)) == 1)

    # (2) multi-line comment block reported ONCE, at its first line
    multi = ("agents:\n  x:\n    # line one\n    # line two\n    # line three\n"
             "    escalate_to_strategic_when: never\n")
    f = scan(multi)
    check("multi-line comment block reported once", len(f) == 1)
    check("multi-line block reported at its FIRST line", f and f[0][2] == "# line one")

    # (3) does NOT fire when there is no comment
    clean = "agents:\n  plan-agent:\n    tier: standard\n    escalate_to_strategic_when: never\n"
    check("silent on a key with no preceding comment", scan(clean) == [])

    # (4) does NOT fire on a comment above a NON-propagating key
    other = "agents:\n  plan-agent:\n    # a note about the description\n    description: things\n"
    check("silent on a comment above a non-propagating key", scan(other) == [])

    # (5) all three propagating keys are recognised
    for k in PROPAGATING_KEYS:
        src = f"agents:\n  x:\n    # note\n    {k} value\n"
        check(f"recognises `{k}`", len(scan(src)) == 1)

    # (6) end-to-end through main(), on a real temp file, so the exit path is exercised too
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "models.yml"
        p.write_text(bad, encoding="utf-8")
        check("main() returns 0 on a finding (SOFT never blocks)", main([str(p)]) == 0)

    print(f"\nverify-models-yml-comments: selftest {'PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, nargs="?", default=MODELS)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.path.exists():
        print(f"verify-models-yml-comments: {args.path} does not exist", file=sys.stderr)
        return 2

    findings = scan(args.path.read_text(encoding="utf-8"))
    print(f"verify-models-yml-comments: {args.path} · {len(findings)} finding(s) "
          f"[SOFT — reports, never blocks]")
    if findings:
        report(args.path, findings)
    else:
        print("  no comment sits directly above a propagating key "
              "(tier / escalate_to_strategic_when / de_escalate_to_mechanical_when)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
