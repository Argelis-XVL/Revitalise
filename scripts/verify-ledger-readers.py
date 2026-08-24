#!/usr/bin/env python3
"""Every reader of logs/worklog.jsonl goes through scripts/lib/worklog.py — enumerated from
source, never from a hand-written list.

WHY THIS EXISTS, and why it is not just another list.

`IMP-0093` (blocker, 2026-08-20) found the ledger's meaning implemented three times: two
scripts excluded a superseded session and one did not, so the repository stated 64 h and 84 h
invoiced at the same time and both gates exited 0. The fix was right — one module
(`scripts/lib/worklog.py`), the duplicates deleted, and a cross-check in
`scripts/ci/verify-pm-gates.sh` section 7 asserting the readers agree.

`IMP-0232` (blocker, 2026-08-23) is the same 84-vs-64 over-count, three days later, in a
fourth script. The cross-check ran on every CI run and passed, because **it named its three
readers by hand** and the repository had grown a fourth: `collect-project-status.py`, the one
script a project-status answer is required to render from verbatim. The policy itself was
stated only in the module's docstring — "no script may compute the superseded set itself" —
and a policy in a docstring is enforced by whoever reads the docstring.

So the altitude lesson is specific: **that fix generalised the RULE and hand-wrote the LIST.**
A gate naming three scripts is an instance gate wearing a class gate's clothes. The list is
what goes stale, not the rule (`skills/how-to-promote-a-finding.md` — derive the query list
from source, never hand-write it).

WHAT THIS CHECKS

  1. RAW PARSERS. Any file that reads and parses the ledger itself must be the module, or must
     appear in EXEMPT below with a stated reason. A new raw parser fails this gate.

  2. NO SILENT COVERAGE GAP. Any file that consumes the ledger through the module is either
     compared numerically by verify-pm-gates.sh section 7, or listed in NO_TOTAL as producing
     no invoiced figure. A fifth reader lands in neither bucket and fails — the point is that
     it forces a decision instead of being quietly uncovered, which is exactly what happened
     to the fourth.

The gate cannot compare a number it does not know how to extract from a script's output. It
can refuse to stay silent about a reader nobody has classified, and that is the difference
between this and the list it replaces.

Run:
    python3 scripts/verify-ledger-readers.py
    python3 scripts/verify-ledger-readers.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LEDGER = "worklog.jsonl"
MODULE = Path("scripts/lib/worklog.py")
SCAN_DIRS = (Path("scripts"),)

# Files that parse the ledger directly and are ALLOWED to, each with the reason. An exemption
# is visible here on purpose: an absence would be indistinguishable from an oversight, which
# is how the fourth reader got in. Only non-hours reads belong here — anything computing a
# total must use the module, because the total is the thing that diverged.
EXEMPT: dict[str, str] = {
    "scripts/lib/worklog.py":
        "IS the module — the single definition of what the ledger means.",
    "scripts/reconstruct-worklog.py":
        "reads which evidence refs have already been claimed, to avoid proposing the same "
        "work twice. Computes no hours total, so it cannot produce the invoiced-to-date "
        "divergence this gate exists to prevent. Deliberately counts SUPERSEDED sessions' "
        "evidence as claimed: a correction supersedes the hours, not the fact that the "
        "evidence was already accounted for.",
    "scripts/verify-ledger-readers.py":
        "IS this gate. It reads the ledger at no point; the match is its own --selftest "
        "fixture, a string containing a synthetic raw read that this check must reject. "
        "Listed rather than silently skipped so the exemption is visible to the next reader.",
}

# Ledger consumers that legitimately report no invoiced-to-date figure, so section 7 has
# nothing to compare them against.
NO_TOTAL: dict[str, str] = {
    "scripts/verify-worklog.py":
        "reports billable hours and internal consistency, not invoiced-to-date. Section 7 "
        "compares the three that do.",
    "scripts/deliverable-hours.py":
        "reports hours per WBS deliverable, not an invoiced total.",
}

# Consumers section 7 compares numerically. Kept here so this gate can assert the shell and
# this file have not drifted apart; the extraction itself stays in the shell.
COMPARED = {
    "scripts/verify-wbs-chain.py",
    "scripts/compute-invoice.py",
    "scripts/collect-project-status.py",
}

MENTIONS = re.compile(re.escape(LEDGER))
USES_MODULE = re.compile(r"import\s+worklog\b|from\s+worklog\s+import|lib\.worklog")

# A file PARSES the ledger only if a read is applied to the ledger ITSELF — not merely if the
# file happens to contain a filename, a `json.loads` and an `open()` somewhere.
#
# The first draft of this gate tested those three independently and reported two false
# positives: import-baseline.py (which names the ledger in one sentence of prose and parses
# entirely different files) and this gate itself (whose own selftest fixture is a string
# containing the filename). A gate whose first run flags two innocent files is a gate people
# learn to route around (IMP-0181), so the subject is bound explicitly:
#   1. find the names bound to the ledger path — WORKLOG = Path("logs/worklog.jsonl")
#   2. a read applied to one of those names, or applied inline to the literal path
LEDGER_BINDING = re.compile(
    r"(\w+)\s*=\s*(?:Path\s*\(\s*)?[\"'][^\"']*" + re.escape(LEDGER) + r"[\"']")
INLINE_READ = re.compile(
    r"(?:Path\s*\(\s*)?[\"'][^\"']*" + re.escape(LEDGER) + r"[\"']\s*\)?\s*"
    r"(?:\.read_text\(|\.open\(|\.read_bytes\()"
    r"|\bopen\s*\(\s*[\"'][^\"']*" + re.escape(LEDGER))


def parses_ledger(text: str) -> bool:
    """True where a read is applied to the ledger itself."""
    if INLINE_READ.search(text):
        return True
    for name in set(LEDGER_BINDING.findall(text)):
        if re.search(rf"\b{re.escape(name)}\s*\.\s*(read_text|open|read_bytes)\s*\(", text):
            return True
        if re.search(rf"\bopen\s*\(\s*{re.escape(name)}\b", text):
            return True
    return False


def classify(repo: Path) -> tuple[dict[str, str], list[str]]:
    """Return ({path: role}, problems). Roles: module/exempt-raw/raw/module-user/mention."""
    roles: dict[str, str] = {}
    problems: list[str] = []
    for d in SCAN_DIRS:
        for p in sorted((repo / d).rglob("*.py")):
            rel = p.relative_to(repo).as_posix()
            text = p.read_text(encoding="utf-8", errors="replace")
            if not MENTIONS.search(text):
                continue
            uses_module = bool(USES_MODULE.search(text))
            raw = parses_ledger(text)

            if rel == MODULE.as_posix():
                roles[rel] = "module"
                continue
            if raw and not uses_module:
                if rel in EXEMPT:
                    roles[rel] = "exempt-raw"
                else:
                    roles[rel] = "raw"
                    problems.append(
                        f"{rel} parses {LEDGER} itself and does not call "
                        f"scripts/lib/worklog.py. This is how the repository came to state "
                        f"two different invoiced-to-date totals at once (IMP-0093, and "
                        f"IMP-0232 when it recurred in a fourth script). Call load() / "
                        f"invoiced_to_date() / unbilled_billable(), or add an entry to "
                        f"EXEMPT in this file stating why a raw read is correct here.")
                continue
            if uses_module:
                roles[rel] = "module-user"
                if rel not in COMPARED and rel not in NO_TOTAL:
                    problems.append(
                        f"{rel} consumes the ledger through the module but is classified "
                        f"nowhere: it is neither compared by verify-pm-gates.sh section 7 "
                        f"(COMPARED) nor declared as producing no invoiced total (NO_TOTAL). "
                        f"An unclassified reader is an uncovered one — that silence is what "
                        f"let collect-project-status.py report 84 h against three gates' 64 h "
                        f"for three days (IMP-0232).")
                continue
            roles[rel] = "mention"
    return roles, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="prove the check can fail: a synthetic raw parser must be rejected")
    ap.add_argument("--repo", type=Path, default=Path("."))
    args = ap.parse_args(argv)
    repo = args.repo.resolve()

    if not (repo / MODULE).is_file():
        print(f"verify-ledger-readers: {MODULE} is missing — the single definition of the "
              f"ledger's meaning does not exist, so nothing here can be enforced.",
              file=sys.stderr)
        return 2

    roles, problems = classify(repo)

    if args.selftest:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "scripts"
            (fake / "lib").mkdir(parents=True)
            (fake / "lib" / "worklog.py").write_text("# stand-in for the module\n"
                                                     "'logs/worklog.jsonl'\n", encoding="utf-8")
            (fake / "rogue-reader.py").write_text(
                "import json\n"
                "from pathlib import Path\n"
                "for line in Path('logs/worklog.jsonl').read_text().splitlines():\n"
                "    json.loads(line)\n", encoding="utf-8")
            _, fake_problems = classify(Path(td))
        rogue = [p for p in fake_problems if "rogue-reader.py" in p]
        if not rogue:
            print("verify-ledger-readers: SELFTEST FAILED — a synthetic script that parses the "
                  "ledger raw was NOT rejected. This gate cannot fail, which makes it worse "
                  "than no gate (IMP-0007).", file=sys.stderr)
            return 1
        print("verify-ledger-readers: selftest PASS — a raw parser is rejected "
              "(1 synthetic fixture).")

    by_role: dict[str, list[str]] = {}
    for rel, role in roles.items():
        by_role.setdefault(role, []).append(rel)

    print(f"verify-ledger-readers: {len(roles)} file(s) reference {LEDGER}")
    for role, label in (("module", "the module itself"),
                        ("module-user", "read it through the module"),
                        ("exempt-raw", "raw read, exempt with a stated reason"),
                        ("mention", "name it in prose only — not readers"),
                        ("raw", "RAW PARSER, NOT EXEMPT")):
        names = sorted(by_role.get(role, []))
        if names:
            print(f"  {len(names)} {label}: {', '.join(names)}")

    for p in problems:
        print(f"  FAIL  {p}", file=sys.stderr)
    if problems:
        print(f"\nverify-ledger-readers: FAILED — {len(problems)} problem(s).", file=sys.stderr)
        return 1
    print("verify-ledger-readers: PASS — every reader goes through scripts/lib/worklog.py, "
          "and every reader is classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
