#!/usr/bin/env python3
"""Assert that every repository path a constraint's `Verify By` names actually exists.

WHY THIS EXISTS. `IMP-0184`, and it is the expensive shape rather than an untidy one.

`C-TECH-064` is HARD. Improvement review 5 amended it to name
`provisioning/dataverse/verify-flow-trigger.ps1` as the *only* admissible evidence that a
Dataverse-triggered flow actually fires — explicitly ruling out `statecode`, the existence of a
`callbackregistration` row, its `createdon`, `subscriptionRequest/scope`, `runas`, and any run
reached by Resubmit. The amendment shipped and was committed. **The script has never existed.**

So a HARD constraint that gates every Dataverse-triggered flow deploy admitted exactly one form
of proof, and that proof could not be produced by anyone. It could not be honestly reported as
PASS, and it had been in that state in the committed tree since review 5.

This is the fourth instance of `declared-policy-not-mechanically-enforced` (`IMP-0143`,
`IMP-0165`, `IMP-0174`, `IMP-0184`), so per `skills/how-to-promote-a-finding.md` §2 it may not
get another instance patch. The generalisable property is not "this one script is missing". It
is:

    A `Verify By` that names a repository path is a promise that the path exists.

WHAT THIS DOES AND DOES NOT COVER. Three rungs, and only the first is here:

  * named but ABSENT      → this gate.
  * present but NEVER RUN → `IMP-0174`'s rung. A `Verify By` saying "wired as a build gate" is
                            not satisfied by a script that exists and passes `--selftest`;
                            somebody has to grep the build config's `steps:` block. Separate
                            check, not this one.
  * runs and asserts the WRONG PROPERTY → covered by nothing, and worth saying out loud.

THE OVER-FIRE CONTROL. On 2026-08-22 this repository's three constraint files named 22 distinct
repository paths across their `Verify By` cells and 21 of them resolved. One gate, one failing
row, 21 passing cases: that ratio is the evidence the gate discriminates rather than simply
objecting. If a future run reports every path missing, suspect the extractor, not the repo.

Run:
    python3 scripts/verify-constraint-verifiers.py
    python3 scripts/verify-constraint-verifiers.py --selftest

Exits 0 when every named path resolves, 1 on any unresolved path, 2 on a usage error. Fails —
never passes — when it extracts ZERO paths from a non-empty constraint set, because a checker
that checks nothing must not report PASS (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CONSTRAINT_FILES = (
    "constraints/technology/technology-constraints.md",
    "constraints/domain/domain-constraints.md",
    "constraints/commercial/commercial-constraints.md",
)

# Top-level directories that make a token a REPOSITORY path rather than prose. Anchored to
# this list on purpose: "Dev Summary §10" and "TAD §6" are legitimate Verify By content and
# are not paths, and a regex loose enough to catch them would report a defect on every row.
REPO_DIRS = ("scripts", "provisioning", "src", "config", "contract", "skills",
             "knowledge", "agents", "templates", "constraints", "docs", "logs",
             ".github")

PATH_TOKEN = re.compile(
    r"\b(?:" + "|".join(re.escape(d) for d in REPO_DIRS) + r")/[A-Za-z0-9_./*<>{}-]+")

# A row whose id is struck through is retired. Its Verify By is history, and its paths are
# allowed to have been deleted — that is what retirement MEANS. Checking them would make every
# correct retirement into a permanent failure.
RETIRED_ROW = re.compile(r"^\|\s*~~")
CONSTRAINT_ROW = re.compile(r"^\|\s*(C-[A-Z]+-\d+)\s*\|")

# Trailing characters that belong to the sentence, not to the path.
TRIM = "`.,;:)('\"*"


def normalise(token: str) -> str:
    """Strip sentence punctuation and collapse a documented template into a glob.

    `config/<slug>-build.yml` is a real, correct Verify By: the file is per-feature and the
    constraint cannot name one feature. It resolves through a glob. Same for `provisioning/*/`
    and `{PREFIX}` style placeholders.
    """
    token = token.strip().strip(TRIM)
    while token.endswith("/"):
        token = token[:-1]
    # <slug>, <name>, {PREFIX} → a single glob segment.
    token = re.sub(r"<[^>/]*>", "*", token)
    token = re.sub(r"\{[^}/]*\}", "*", token)
    return token


def resolves(repo_root: Path, token: str) -> bool:
    if "*" in token:
        try:
            return any(repo_root.glob(token))
        except (ValueError, NotImplementedError):
            return False
    return (repo_root / token).exists()


def verify_by_cell(line: str) -> str:
    """The last non-empty cell of a constraint table row.

    The table is `| ID | Rule | Severity | Owner | Why | Verify By |`, but several rows carry
    pipes inside inline code, so counting columns from the left is unreliable. The Verify By
    cell is the last one with content, which is stable.
    """
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    for cell in reversed(cells):
        if cell and cell not in {"—", "-"}:
            return cell
    return ""


# ── Rung 4: a Verify By's CLAIM about its gate, not just the gate's existence ──────────────
# IMP-0260. C-TECH-070's Verify By said its selftest "exits 0 over 3 fixtures" while the gate
# had grown to 7, and the row had been stale within a day of being written. Checking all three
# rows that state a count found a second one nobody had recorded: C-TECH-067 claimed 9 against
# an actual 11. Two of three wrong is why this is a check and not two number edits.
#
# The claim is checked by RUNNING the selftest the same row names and reading the total out of
# its own output — so extending a gate cannot falsify the constraint describing it, provided the
# selftest reports a total. Two of the four gates sampled on 2026-08-24 printed none, so the
# convention is now: every selftest ends with "SELFTEST OK — <n> fixtures".
FIXTURE_CLAIM = re.compile(r"(?<!\w)(\d+)\s+(?:selftest\s+)?fixtures?(?!\w)", re.I)
# A row that explains why its own count was once wrong quotes the old number, and the checker
# fired on the quotation — turning "here is the history of this mistake" into a fresh failure.
# A gate that punishes a row for documenting itself is one people learn to route around
# (IMP-0181), so a claim inside double quotes is history, not an assertion.
QUOTED = re.compile(r"\"[^\"]*\"")
SELFTEST_TOTAL = re.compile(r"SELFTEST OK\s*[—-]+\s*(\d+)\s+fixtures?", re.I)


def selftest_total(repo_root: Path, script_rel: str) -> int | None:
    """Run one gate's --selftest and read the fixture total it reports about itself.

    None means the script ran but reported no total in the agreed shape — which is a finding
    about that script, not a pass for the constraint row.
    """
    import subprocess

    script = repo_root / script_rel
    if not script.exists():
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--selftest"],
            capture_output=True, text=True, timeout=300, cwd=repo_root)
    except (OSError, subprocess.SubprocessError):
        return None
    match = SELFTEST_TOTAL.search(result.stdout + result.stderr)
    return int(match.group(1)) if match else None


def scan_fixture_claims(repo_root: Path) -> tuple[list[str], list[str], int]:
    """Return (failures, unverifiable, claims_checked) for every fixture count in a Verify By."""
    failures: list[str] = []
    unverifiable: list[str] = []
    checked = 0
    cache: dict[str, int | None] = {}

    for rel in CONSTRAINT_FILES:
        path = repo_root / rel
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not CONSTRAINT_ROW.match(line) or RETIRED_ROW.match(line):
                continue
            cid = CONSTRAINT_ROW.match(line).group(1)
            cell = verify_by_cell(line)
            # Blank out quoted spans first, so a row narrating its own past wrong number is not
            # read as claiming it. Same length, so any offsets stay meaningful.
            searchable = QUOTED.sub(lambda m: " " * len(m.group(0)), cell)
            claim = FIXTURE_CLAIM.search(searchable)
            if claim is None:
                continue
            scripts = [normalise(t) for t in PATH_TOKEN.findall(cell)]
            scripts = [s for s in scripts if s.startswith("scripts/") and s.endswith(".py")]
            if len(scripts) != 1:
                unverifiable.append(
                    f"{cid} ({rel}): its Verify By claims '{claim.group(0)}' but names "
                    f"{len(scripts)} python gate(s), so which script the count describes is "
                    f"ambiguous. Name exactly one, or cite the selftest's own reported total "
                    f"instead of a literal.")
                continue
            script_rel = scripts[0]
            if script_rel not in cache:
                cache[script_rel] = selftest_total(repo_root, script_rel)
            actual = cache[script_rel]
            checked += 1
            stated = int(claim.group(1))
            if actual is None:
                unverifiable.append(
                    f"{cid} ({rel}): claims '{claim.group(0)}' for {script_rel}, but that "
                    f"script's --selftest reports no total in the agreed shape "
                    f"('SELFTEST OK — <n> fixtures'). The claim cannot be checked, so it is "
                    f"free to drift. Add the footer to that script.")
            elif stated != actual:
                failures.append(
                    f"{cid} ({rel}): its Verify By says '{claim.group(0)}', and "
                    f"{script_rel} --selftest reports {actual}. A HARD row's Verify By is what "
                    f"an agent reads to decide whether the row passes, so a stale description "
                    f"of the gate is a stale rule (IMP-0260). Either correct the number, or "
                    f"better, reword to cite the selftest's own reported total so extending "
                    f"the gate cannot falsify the row again.")
    return failures, unverifiable, checked


def scan(repo_root: Path) -> tuple[list[tuple[str, str, str]], int, int, list[str]]:
    """Return (failures, rows_scanned, paths_checked, files_missing)."""
    failures: list[tuple[str, str, str]] = []
    rows_scanned = 0
    paths_checked = 0
    files_missing: list[str] = []
    seen: set[tuple[str, str]] = set()

    for rel in CONSTRAINT_FILES:
        path = repo_root / rel
        if not path.exists():
            files_missing.append(rel)
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not CONSTRAINT_ROW.match(line) or RETIRED_ROW.match(line):
                continue
            rows_scanned += 1
            cid = CONSTRAINT_ROW.match(line).group(1)
            cell = verify_by_cell(line)
            for raw in PATH_TOKEN.findall(cell):
                token = normalise(raw)
                if not token or token.count("/") == 0:
                    continue
                if (cid, token) in seen:
                    continue
                seen.add((cid, token))
                paths_checked += 1
                if not resolves(repo_root, token):
                    failures.append((cid, token, rel))
    return failures, rows_scanned, paths_checked, files_missing


def selftest() -> int:
    """Prove the extractor finds a missing path, accepts a real one, and ignores prose."""
    import tempfile

    cases = [
        # (row, should_fail, why)
        ("| C-TEST-001 | rule | HARD | owner | why | `python3 scripts/verify-improvement-log.py` "
         "exits 0 |", False, "a real path resolves"),
        ("| C-TEST-002 | rule | HARD | owner | why | `pwsh scripts/does-not-exist-ever.ps1` |",
         True, "an absent path is caught"),
        ("| C-TEST-003 | rule | HARD | owner | why | Code review against TAD §6; Dev Summary "
         "§10 has a row |", False, "prose naming no path is not a failure"),
        ("| ~~C-TEST-004~~ | *(retired)* | — | — | — | `scripts/deleted-by-design.py` |",
         False, "a retired row's paths are history"),
        ("| C-TEST-005 | rule | HARD | owner | why | `config/<slug>-build.yml` declares it |",
         False, "a documented per-feature template resolves by glob"),
    ]

    repo_root = Path(__file__).resolve().parents[1]
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for row, should_fail, why in cases:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "constraints" / "technology").mkdir(parents=True)
            (root / "constraints" / "technology" / "technology-constraints.md").write_text(
                "| ID | Rule | Sev | Owner | Why | Verify By |\n|---|---|---|---|---|---|\n"
                + row + "\n", encoding="utf-8")
            # Mirror the two real artefacts the fixtures reference.
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "verify-improvement-log.py").write_text("#\n")
            (root / "config").mkdir(parents=True, exist_ok=True)
            (root / "config" / "revitalise-grant-automation-build.yml").write_text("#\n")

            failures, rows, paths, _missing = scan(root)
            got = bool(failures)
            ok = got == should_fail
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: "
                  f"{len(failures)} failure(s) over {paths} path(s) in {rows} row(s)")
            if not ok:
                failed += 1

    # The IMP-0007 control: an empty constraint set must FAIL, never pass.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "constraints" / "technology").mkdir(parents=True)
        (root / "constraints" / "technology" / "technology-constraints.md").write_text(
            "| ID | Rule |\n|---|---|\n", encoding="utf-8")
        _f, rows, paths, _m = scan(root)
        ok = paths == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  a constraint set naming no paths yields 0 "
              f"(caller must fail, not pass): rows={rows} paths={paths}")
        if not ok:
            failed += 1

    # ── Rung 4 fixtures: the fixture-count claim (IMP-0260) ────────────────────────────────
    # Each writes a throwaway gate whose --selftest reports a known total, so the claim checker
    # is exercised end to end rather than against a mock.
    stub = ("import sys\n"
            "print('  OK  x')\n"
            "print('stub: SELFTEST OK — 7 fixtures.')\n")
    rung4 = [
        ("a matching fixture count passes",
         "`python3 scripts/stub-gate.py` and `--selftest` exits 0 over 7 fixtures", False),
        ("a stale fixture count is caught",
         "`python3 scripts/stub-gate.py` and `--selftest` exits 0 over 3 fixtures", True),
        ("a count quoted as history is not read as a claim",
         "`python3 scripts/stub-gate.py` `--selftest` reports its own total, having once "
         "said \"3 fixtures\" wrongly", False),
        ("a row naming no count is not checked at all",
         "`python3 scripts/stub-gate.py` `--selftest` exits 0", False),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for why, cell, should_fail in rung4:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "constraints" / "technology").mkdir(parents=True)
            (root / "constraints" / "technology" / "technology-constraints.md").write_text(
                "| ID | Rule | Sev | Owner | Why | Verify By |\n|---|---|---|---|---|---|\n"
                f"| C-TEST-100 | rule | HARD | owner | why | {cell} |\n", encoding="utf-8")
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "stub-gate.py").write_text(stub, encoding="utf-8")
            claim_failures, _unver, claims = scan_fixture_claims(root)
            got = bool(claim_failures)
            ok = got == should_fail
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(claim_failures)} failure(s) "
                  f"over {claims} claim(s)")
            if not ok:
                failed += 1

    # A claim whose gate reports no total must WARN, never pass silently.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "constraints" / "technology").mkdir(parents=True)
        (root / "constraints" / "technology" / "technology-constraints.md").write_text(
            "| ID | Rule | Sev | Owner | Why | Verify By |\n|---|---|---|---|---|---|\n"
            "| C-TEST-101 | rule | HARD | o | w | `python3 scripts/silent.py` `--selftest` "
            "exits 0 over 4 fixtures |\n", encoding="utf-8")
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "silent.py").write_text("print('done')\n", encoding="utf-8")
        claim_failures, unver, _claims = scan_fixture_claims(root)
        ok = not claim_failures and len(unver) == 1
        print(f"  {'ok  ' if ok else 'FAIL'}  a gate reporting no total warns rather than "
              f"passing: {len(claim_failures)} failure(s), {len(unver)} warning(s)")
        if not ok:
            failed += 1

    total = len(cases) + 1 + len(rung4) + 1
    if failed:
        print(f"\nSELFTEST: FAILED — {failed} case(s) of {total} fixtures  "
              f"(repo root {repo_root.name})")
        return 1
    print(f"\nSELFTEST: PASS  (repo root {repo_root.name})\n"
          f"verify-constraint-verifiers: SELFTEST OK — {total} fixtures.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assert every repository path named in a constraint's Verify By exists.")
    parser.add_argument("--selftest", action="store_true",
                        help="run the extractor against known-good and known-bad fixtures")
    parser.add_argument("--repo-root", default=None,
                        help="repository root (default: this script's parent directory)")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]

    failures, rows, paths, files_missing = scan(repo_root)

    for rel in files_missing:
        print(f"ERROR: constraint file not found: {rel}", file=sys.stderr)

    if paths == 0:
        print("ERROR: extracted ZERO repository paths from the constraint files. Either every "
              "Verify By is prose — in which case this project has no mechanically verifiable "
              "constraints and that is the finding — or PATH_TOKEN/REPO_DIRS stopped matching. "
              "A checker that checks nothing must fail rather than report PASS (IMP-0007).",
              file=sys.stderr)
        return 1

    claim_failures, unverifiable, claims = scan_fixture_claims(repo_root)

    if failures or files_missing or claim_failures:
        for cid, token, rel in failures:
            print(f"ERROR: {cid} ({rel}): its `Verify By` names `{token}`, which does not "
                  f"exist. A HARD rule whose only admissible evidence cannot be produced "
                  f"cannot be satisfied, cannot honestly be reported PASS, and blocks every "
                  f"deploy it governs. Either create the artefact, or narrow the rule to "
                  f"name evidence somebody can actually generate — do not leave it pointing "
                  f"at a script nobody has written (IMP-0184).", file=sys.stderr)
        for message in claim_failures:
            print(f"ERROR: {message}", file=sys.stderr)
        for message in unverifiable:
            print(f"WARNING: {message}", file=sys.stderr)
        print(f"\nCONSTRAINT VERIFIERS: FAILED — {len(failures)} unresolved path(s) of "
              f"{paths} checked and {len(claim_failures)} stale fixture-count claim(s) of "
              f"{claims} checked, across {rows} active constraint row(s).", file=sys.stderr)
        return 1

    for message in unverifiable:
        print(f"WARNING: {message}", file=sys.stderr)

    print(f"CONSTRAINT VERIFIERS: PASS — {paths} repository path(s) named by {rows} active "
          f"constraint row(s) all resolve, and {claims} fixture-count claim(s) match the "
          f"total their own gate reports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
