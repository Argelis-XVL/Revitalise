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

RUNG 5, added 2026-08-24 (improvement review 24): NAMES A LIVE CHECK NOBODY CAN EXECUTE. A HARD
`Verify By` that demands LIVE verification, and whose only route through the pipeline config is a
step declared `script: manual`, is not a verified rule — it is an operator checklist item wearing
a HARD rule's clothes. `C-TECH-064` is the live fixture: it has said `script: manual` at
`environments.dev.verification[4]` since 2026-08-19, waiting on an executable form that was handed
to a delivery agent and never written. Two blockers landed on 2026-08-24 that this step is written
to catch — five lookup columns unsecured live, four tables with no audit trail — and neither was
seen, because a checklist item is only performed by someone who remembers it.

This rung reports the CONDITION; it does not remove it. Nor does it prove anyone RAN an executable
step — that needs a deploy-time record and is not built here.

THE OVER-FIRE CONTROL. On 2026-08-22 this repository's three constraint files named 22 distinct
repository paths across their `Verify By` cells and 21 of them resolved. One gate, one failing
row, 21 passing cases: that ratio is the evidence the gate discriminates rather than simply
objecting. If a future run reports every path missing, suspect the extractor, not the repo.

WIRED IN AS SOFT, 2026-08-24 (improvement review 25). Until then this gate ran NOWHERE. It was
review 24's headline change, it correctly exits 1 on `C-TECH-064` against the real tree, and a
grep across `config/`, `.github/` and `constraints/` found the only mention of its own filename
to be `C-TECH-064`'s prose. A gate nobody runs is a gate that does not exist — instance 31 of
`gate-cannot-fail`, and the most-recorded class in this project wearing its politest disguise.

`--warn-only` is what makes SOFT possible. `scripts/ci/run-config-steps.sh` halts on the first
non-zero exit and has no per-step "record but continue" mode, so the only way to wire a SOFT check
into a build config is a command that exits 0. It prints every finding either way; the flag
changes the exit code and nothing else. SOFT rather than HARD is a DELIVERY decision, not a rules
one: this gate exits 1 on the real tree today (`C-TECH-064`'s live audit rung is reachable only by
a step declared `script: manual`), so wiring it HARD would block every build until somebody writes
a live verifier that was handed to a delivery agent and never built. Making its absence visible on
every build is the honest half-measure; the verifier itself is still delivery work and still
unwritten.

Run:
    python3 scripts/verify-constraint-verifiers.py
    python3 scripts/verify-constraint-verifiers.py --warn-only
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


# ── Rung 5: a HARD live check whose only route is `script: manual` ─────────────────────────
# IMP-0270, IMP-0271. Both are C-TECH-064's own subject matter — live environment state that
# solution source cannot express — and both stood unseen while every source-side gate was green.
# The route that would have caught them exists and is declared `script: manual`.
#
# The two halves are deliberately separate: WHICH rows demand a live check is read from the
# constraint text, and WHETHER a live route is executable is read from the pipeline config. A row
# no pipeline step names at all is NOT this rung's finding — that is rung 2 ("present but never
# run") and reporting it here would drown the one real case in six.
PIPELINE_GLOB = "config/*-pipeline.yml"

# Phrases that mean "go and ask the running environment", as opposed to reading source. Anchored
# on demands rather than on the word "live" alone: several rows use "live" narratively while their
# verification is a source-side script, and a looser pattern reports those as defects.
LIVE_DEMAND = re.compile(
    r"\bverified LIVE\b|\bLIVE against\b|\bREADS live state\b|\breads live\b"
    r"|\blive (?:query|queries|comparison|verification|re-?run)\b"
    r"|\?\$select=|EntityDefinitions\(",
    re.I)

HARD_CELL = re.compile(r"^\s*HARD\s*$")


def _pipeline_helpers():
    """Borrow `is_manual` and `iter_steps` from verify-pipeline-config.py.

    Imported rather than re-implemented on purpose. `MANUAL_PREFIXES` there is kept in sync with
    the `case` block in scripts/ci/run-config-steps.sh, and a second copy here would drift from
    both — which is IMP-0093's lesson exactly ("a rule implemented twice is a rule that will be
    implemented once somewhere else"). Returns None when the helper cannot be loaded, and the
    caller then reports this rung as unverifiable rather than passing it.
    """
    import importlib.util

    sibling = Path(__file__).resolve().parent / "verify-pipeline-config.py"
    if not sibling.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_rev_pipeline_config", sibling)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)          # raises SystemExit if pyyaml is absent
    except (SystemExit, ImportError, OSError, SyntaxError):
        return None
    if not (hasattr(module, "is_manual") and hasattr(module, "iter_steps")):
        return None
    return module


def _step_text(step: dict) -> str:
    """Everything a step says about itself, including its `blocked_on` reason and comments."""
    return " ".join(str(v) for v in step.values())


def scan_live_verification_routes(repo_root: Path) -> tuple[list[str], list[str], int]:
    """Return (failures, unverifiable, hard_live_rows_seen).

    A failure is a HARD row demanding live verification whose every naming pipeline step is
    declared manual. A row named by no step at all is counted but not reported (rung 2).
    """
    failures: list[str] = []
    unverifiable: list[str] = []

    hard_live: list[tuple[str, str]] = []
    for rel in CONSTRAINT_FILES:
        path = repo_root / rel
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not CONSTRAINT_ROW.match(line) or RETIRED_ROW.match(line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not any(HARD_CELL.match(c) for c in cells):
                continue
            if LIVE_DEMAND.search(verify_by_cell(line)):
                hard_live.append((CONSTRAINT_ROW.match(line).group(1), rel))

    if not hard_live:
        return failures, unverifiable, 0

    helpers = _pipeline_helpers()
    if helpers is None:
        unverifiable.append(
            "the live-route rung could not run: scripts/verify-pipeline-config.py did not load "
            "(pyyaml missing, most likely — `python3 -m pip install pyyaml`). "
            f"{len(hard_live)} HARD row(s) demanding live verification went unchecked. This is "
            "reported rather than passed, because a rung that silently checks nothing is the "
            "defect this whole gate exists for (IMP-0007).")
        return failures, unverifiable, len(hard_live)

    import yaml

    routes: dict[str, list[tuple[str, bool]]] = {cid: [] for cid, _ in hard_live}
    configs = sorted(repo_root.glob(PIPELINE_GLOB))
    if not configs:
        unverifiable.append(
            f"no pipeline config matched {PIPELINE_GLOB}, so no HARD row's live route could be "
            f"resolved. {len(hard_live)} row(s) went unchecked.")
        return failures, unverifiable, len(hard_live)

    for config_path in configs:
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError) as exc:
            unverifiable.append(f"{config_path.name} did not parse, so its steps were not "
                                f"considered: {exc}")
            continue
        if not isinstance(config, dict):
            continue
        for location, step in helpers.iter_steps(config):
            if not isinstance(step, dict):
                continue
            text = _step_text(step)
            value = str(step.get("script") or step.get("command") or "")
            executable = bool(value.strip()) and not helpers.is_manual(value)
            for cid in routes:
                if cid in text:
                    routes[cid].append((f"{config_path.name}:{location}", executable))

    for cid, rel in hard_live:
        named = routes[cid]
        if not named:
            # Rung 2's territory, not this one. Counted, deliberately not reported.
            continue
        if any(executable for _loc, executable in named):
            continue
        where = ", ".join(loc for loc, _ in named)
        failures.append(
            f"{cid} ({rel}): its `Verify By` demands LIVE verification, and every pipeline step "
            f"that names it is declared `script: manual` ({where}). A HARD rule verified only by "
            f"a step the runner records as an operator checklist item is not enforced — it is "
            f"performed by whoever remembers. Two blockers on 2026-08-24 (IMP-0270, IMP-0271) "
            f"were exactly what this step reads for, and both stood unseen with every "
            f"source-side gate green. Either supply the executable form, or narrow the rule to "
            f"evidence the pipeline can actually produce.")

    return failures, unverifiable, len(hard_live)


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

    # ── Rung 5 fixtures: a HARD live check reachable only by a manual step (IMP-0270/0271) ──
    # Four shapes, and the last two are the ones that keep a gate honest: a row that demands a
    # live check and HAS an executable route must not be reported, and a row no step names at
    # all belongs to rung 2 and must not be reported here either.
    def _pipeline(steps: str) -> str:
        return ("feature: fixture\nartifact: fixture\nenvironments:\n  dev:\n"
                "    verification:\n" + steps)

    rung5 = [
        ("a HARD live check reachable only by a manual step is caught",
         "HARD", "The step READS live state and compares it to source: `?$select=IsAuditEnabled`",
         _pipeline("      - level: V3\n"
                   "        description: live audit check for C-TEST-200\n"
                   "        script: manual\n"), True),
        ("the same row with one executable route passes",
         "HARD", "The step READS live state and compares it to source: `?$select=IsAuditEnabled`",
         _pipeline("      - level: V3\n"
                   "        description: live audit check for C-TEST-200\n"
                   "        script: manual\n"
                   "      - level: V3\n"
                   "        description: executable form of C-TEST-200\n"
                   "        script: pwsh provisioning/dataverse/ensure-auditing.ps1 -Env dev\n"),
         False),
        ("a SOFT row demanding a live check is out of scope",
         "SOFT", "The step READS live state and compares it to source: `?$select=IsAuditEnabled`",
         _pipeline("      - level: V3\n"
                   "        description: live audit check for C-TEST-200\n"
                   "        script: manual\n"), False),
        ("a HARD row no pipeline step names is rung 2, not this rung",
         "HARD", "The step READS live state and compares it to source: `?$select=IsAuditEnabled`",
         _pipeline("      - level: V3\n"
                   "        description: an unrelated manual step\n"
                   "        script: manual\n"), False),
        ("a HARD row whose verification is source-side is not a live demand at all",
         "HARD", "`python3 scripts/verify-improvement-log.py` exits 0",
         _pipeline("      - level: V3\n"
                   "        description: live audit check for C-TEST-200\n"
                   "        script: manual\n"), False),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for why, severity, cell, pipeline_yaml, should_fail in rung5:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "constraints" / "technology").mkdir(parents=True)
            (root / "constraints" / "technology" / "technology-constraints.md").write_text(
                "| ID | Rule | Sev | Owner | Why | Verify By |\n|---|---|---|---|---|---|\n"
                f"| C-TEST-200 | rule | {severity} | owner | why | {cell} |\n", encoding="utf-8")
            (root / "config").mkdir(parents=True, exist_ok=True)
            (root / "config" / "fixture-pipeline.yml").write_text(pipeline_yaml, encoding="utf-8")
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            (root / "scripts" / "verify-improvement-log.py").write_text("#\n")

            route_failures, route_unver, seen = scan_live_verification_routes(root)
            got = bool(route_failures)
            ok = got == should_fail and not route_unver
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(route_failures)} failure(s) over "
                  f"{seen} HARD live row(s), {len(route_unver)} unverifiable")
            if not ok:
                failed += 1
                for message in route_failures + route_unver:
                    print(f"                   {message[:160]}")

    total = len(cases) + 1 + len(rung4) + 1 + len(rung5)
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
    parser.add_argument("--warn-only", action="store_true",
                        help="print every finding but exit 0, so the check can be wired into a "
                             "build config as SOFT (run-config-steps.sh halts on any non-zero "
                             "exit and has no record-but-continue mode)")
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
        # NOT downgraded by --warn-only, deliberately. That flag lowers what this gate says about
        # the TREE; it does not lower what the gate says about ITSELF. An extractor that reads
        # nothing is broken tooling inside a build step, and broken tooling stops a build whatever
        # the step's severity — otherwise a SOFT wiring becomes a way to make IMP-0007 silent.
        print("ERROR: extracted ZERO repository paths from the constraint files. Either every "
              "Verify By is prose — in which case this project has no mechanically verifiable "
              "constraints and that is the finding — or PATH_TOKEN/REPO_DIRS stopped matching. "
              "A checker that checks nothing must fail rather than report PASS (IMP-0007).",
              file=sys.stderr)
        return 1

    claim_failures, unverifiable, claims = scan_fixture_claims(repo_root)
    route_failures, route_unverifiable, hard_live = scan_live_verification_routes(repo_root)
    unverifiable += route_unverifiable

    if failures or files_missing or claim_failures or route_failures:
        for cid, token, rel in failures:
            print(f"ERROR: {cid} ({rel}): its `Verify By` names `{token}`, which does not "
                  f"exist. A HARD rule whose only admissible evidence cannot be produced "
                  f"cannot be satisfied, cannot honestly be reported PASS, and blocks every "
                  f"deploy it governs. Either create the artefact, or narrow the rule to "
                  f"name evidence somebody can actually generate — do not leave it pointing "
                  f"at a script nobody has written (IMP-0184).", file=sys.stderr)
        for message in claim_failures + route_failures:
            print(f"ERROR: {message}", file=sys.stderr)
        for message in unverifiable:
            print(f"WARNING: {message}", file=sys.stderr)
        verdict = "REPORTED (--warn-only)" if args.warn_only else "FAILED"
        print(f"\nCONSTRAINT VERIFIERS: {verdict} — {len(failures)} unresolved path(s) of "
              f"{paths} checked, {len(claim_failures)} stale fixture-count claim(s) of "
              f"{claims} checked, and {len(route_failures)} HARD live check(s) of {hard_live} "
              f"reachable only by a manual step, across {rows} active constraint row(s).",
              file=sys.stderr)
        if args.warn_only:
            print("NOTE: --warn-only, so this exits 0 and does not block the build. The "
                  "finding above is real and unfixed; it is wired SOFT because the remedy is "
                  "delivery work (an executable live verifier for C-TECH-064) that nobody has "
                  "written, and a HARD wiring would block every build until they do.",
                  file=sys.stderr)
            return 0
        return 1

    for message in unverifiable:
        print(f"WARNING: {message}", file=sys.stderr)

    print(f"CONSTRAINT VERIFIERS: PASS — {paths} repository path(s) named by {rows} active "
          f"constraint row(s) all resolve, {claims} fixture-count claim(s) match the "
          f"total their own gate reports, and every one of {hard_live} HARD row(s) demanding "
          f"live verification has at least one executable pipeline route.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
