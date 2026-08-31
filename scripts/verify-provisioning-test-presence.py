#!/usr/bin/env python3
"""Every PowerShell script inside the DECLARED coverage
scope is named by at least one `*.Tests.ps1`, or carries a `config/coverage-exclusions.json`
entry.

IMP-0433's class, `no-assertion-on-shipped-content` (x18). Asserts on VALUES only: does any
test file contain this script's filename? No prose, no claim parsing, no intent.

WHY NOT THE OBVIOUS DESIGN. The obvious design reads the Dev Summary's own coverage CLAIM and
checks whether the suite it cites names the script it is about. That was built first and
measured: **8 candidate lines across docs/development, docs/tests and docs/deployments → 4
findings, 0 true, 4 false.** All four are co-occurrence, not a claim — a dependency sentence
naming a suite and two scripts, a test-count row naming the runner and two suites twice, and a
constraint row naming both. Extracting "this suite discharges that script's obligation" needs
intent, which IMP-0422 has now measured as unavailable to a prose gate five times. Discarded.

WHAT THIS GATE IS NOT. Being NAMED by a test file is not behavioural coverage — a script can be
named inside a generic convention loop that never executes a line of it, which is IMP-0433's
own defect and IMP-0246's before it. The real instrument stays `verify-coverage-threshold.py`
(C-TECH-014, HARD, 80% lines). This gate answers the cheaper, earlier question — "does anything
name this script at all?" — at preflight, so a missing behavioural test costs one second
instead of a full Pester run and a halted pack (IMP-0285's pattern).

SCOPE comes from knowledge/technology/coding-standards.md line 152, which declares the coverage
scope as `provisioning/{common,entra,dataverse}/**/*.ps1` — not from a list in this file.
Ignored paths are excluded per IMP-0410: a gate whose verdict depends on a gitignored fixture
differs between this Mac and CI.

ALSO ANSWERS `IMP-0436`, which asked for this same gate under the name
`verify-provisioning-script-tests.py`. That finding was appended by a `development-agent` dispatch
AFTER review 36's gate opened and while its keyword was in flight, and it arrived at an identical
mechanism independently — which is corroboration, not a conflict. This file is the one that
shipped; the alternative name is recorded here so a grep for either finds it, and so no second
dispatch builds a duplicate. `IMP-0436`'s own framing is the sharpest statement of why this exists:
an aggregate coverage percentage is a **lagging** indicator that cannot name the untested file, and
it blocks packaging rather than authoring.

KNOWN BLIND SPOT, from `IMP-0437`, which landed in the same batch. This gate reads test files off
the working tree, so an UNTRACKED `*.Tests.ps1` would satisfy it locally and not in CI — the quiet
direction of IMP-0410's class. The gitignore exclusion above covers the loud direction only. Run
`git status --porcelain src/tests/` before trusting a clean verdict.

RESOLVED 2026-08-28 by improvement review 37 (IMP-0437), and NOT in the direction that finding
proposed. Resolving every glob-driven gate's inputs through `git ls-files` was measured and
WITHHELD: applied here it would drop all three `seed-round-statistics-*.ps1` files, which are
untracked and are the exact scripts IMP-0433 and IMP-0436 are about. The rule is REPORT the split,
do not narrow the inputs — see `scripts/lib/tracked_paths.py`, "TWO INPUT UNIVERSES". The caveat
line below is that report.

BASELINES (IMP-0439). This gate is HARD and was wired while red over three pre-existing scripts,
which halted the build at step 4 of 72. `config/gate-baselines.json` carries the owned, dated
exceptions; an entry suppresses the FAIL and never the report, and an unowned or expired entry
fails. See `scripts/lib/gate_baseline.py`.
"""
from __future__ import annotations
import argparse, json, os, pathlib, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.gate_baseline import BaselineError, load_baselines  # noqa: E402

GATE = "provisioning-test-presence"

SCOPE_DECL = pathlib.Path("knowledge/technology/coding-standards.md")
SCOPE_RE = re.compile(r"provisioning/\{([a-z,]+)\}/\*\*/\*\.ps1")


def read_scope(repo: pathlib.Path) -> list[pathlib.Path]:
    """Derive the scope from the standard, never from a list in this file."""
    decl = repo / SCOPE_DECL
    if not decl.exists():
        raise SystemExit(f"provisioning-test-presence: FAIL — {SCOPE_DECL} does not exist, so the "
                         "coverage scope cannot be derived. Refusing to guess.")
    m = SCOPE_RE.search(decl.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"provisioning-test-presence: FAIL — no coverage-scope declaration found in "
                         f"{SCOPE_DECL}. Refusing to guess.")
    return [repo / "provisioning" / part for part in m.group(1).split(",")]


def ignored(p: pathlib.Path, repo: pathlib.Path) -> bool:
    return subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", str(p)]).returncode == 0


# IMP-0436 / IMP-0433. A CONVENTION suite is not coverage evidence, and this gate used to accept
# it as such. ScriptContract.Tests.ps1 discovers every script by `Get-ChildItem -Recurse` and
# asserts SHAPE — a parameter block, an output vocabulary — never behaviour, so a mention inside it
# is exactly the substitution IMP-0433 recorded as invalid ("passing it is not evidence that a NEW
# provisioning script's own Dataverse-call logic executes even once"). This gate's own summary line
# already said so in prose while counting such a mention anyway.
#
# Measured across the real corpus before adopting: the landed rule reported 3 findings, all true;
# excluding this suite reports 4, all true, adding create-self-signed-cert.ps1 — which no
# behavioural suite names at all. 0 false positives either way, so the exclusion is a strict
# improvement rather than a trade.
CONVENTION_SUITES = {"ScriptContract.Tests.ps1"}


def run(repo: pathlib.Path) -> tuple[list[str], list[str], int]:
    """(unbaselined findings, baselined findings, scripts counted)."""
    dirs = read_scope(repo)
    excl_path = repo / "config/coverage-exclusions.json"
    excl = set()
    if excl_path.exists():
        excl = {e["source"] for e in json.loads(excl_path.read_text(encoding="utf-8"))["exclusions"]}
    baseline = load_baselines(repo, GATE)
    tests = list((repo / "src/tests").rglob("*.Tests.ps1"))
    if not tests:
        raise SystemExit("provisioning-test-presence: FAIL — no *.Tests.ps1 found under src/tests. "
                         "A gate whose subject is missing must fail, not pass over nothing (IMP-0007).")
    behavioural = [t for t in tests if t.name not in CONVENTION_SUITES]
    if not behavioural:
        raise SystemExit("provisioning-test-presence: FAIL — every *.Tests.ps1 under src/tests is a "
                         "declared CONVENTION suite, so nothing can evidence behavioural coverage. "
                         "A gate with no usable inputs must fail (IMP-0007).")
    bodies = {t: t.read_text(encoding="utf-8") for t in behavioural}
    scripts = sorted(q for d in dirs if d.exists() for q in d.rglob("*.ps1"))
    findings: list[str] = []
    baselined: list[str] = []
    counted = 0
    for s in scripts:
        rel = s.relative_to(repo).as_posix() if s.is_absolute() else s.as_posix()
        if ignored(s, repo):
            continue
        counted += 1
        if rel in excl:
            continue
        if any(s.name in b for b in bodies.values()):
            continue
        msg = (f"{rel}: no BEHAVIOURAL *.Tests.ps1 under src/tests names this script "
               f"(a mention in a convention suite — {', '.join(sorted(CONVENTION_SUITES))} — "
               f"does not count, IMP-0433), and it has no config/coverage-exclusions.json entry. "
               f"Its lines count toward C-TECH-014's 80% threshold the moment a build runs.")
        cite = baseline.cite(rel)
        if cite:
            baselined.append(msg + cite)
        else:
            findings.append(msg)
    return findings, baselined, counted


def selftest(repo: pathlib.Path) -> int:
    """Prove the gate CAN fail, and that each guard fires."""
    ok = True
    with tempfile.TemporaryDirectory() as td:
        fake = pathlib.Path(td)
        (fake / "knowledge/technology").mkdir(parents=True)
        (fake / "provisioning/dataverse").mkdir(parents=True)
        (fake / "src/tests").mkdir(parents=True)
        (fake / "config").mkdir()
        subprocess.run(["git", "init", "-q", str(fake)], check=True)
        (fake / SCOPE_DECL).write_text("| x | `provisioning/{common,entra,dataverse}/**/*.ps1` | 80% |\n")
        (fake / "provisioning/dataverse/untested.ps1").write_text("# nothing tests me\n")
        (fake / "src/tests/Some.Tests.ps1").write_text("Describe 'x' {}\n")
        (fake / "config/coverage-exclusions.json").write_text('{"exclusions": []}')

        f, _b, n = run(fake)
        print(f"  {'PASS' if len(f) == 1 else 'FAIL'}  an unnamed, unexcluded script FAILS "
              f"({len(f)} finding(s) over {n} script(s))")
        ok &= len(f) == 1

        (fake / "src/tests/Some.Tests.ps1").write_text("Describe 'untested.ps1' {}\n")
        f, _b, _n = run(fake)
        print(f"  {'PASS' if not f else 'FAIL'}  a script a test file NAMES passes ({len(f)} finding(s))")
        ok &= not f

        (fake / "src/tests/Some.Tests.ps1").write_text("Describe 'x' {}\n")
        (fake / "config/coverage-exclusions.json").write_text(
            '{"exclusions": [{"source": "provisioning/dataverse/untested.ps1"}]}')
        f, _b, _n = run(fake)
        print(f"  {'PASS' if not f else 'FAIL'}  an EXCLUDED script passes ({len(f)} finding(s))")
        ok &= not f

        # IMP-0436: a mention in a CONVENTION suite must not count as coverage evidence.
        (fake / "config/coverage-exclusions.json").write_text('{"exclusions": []}')
        (fake / "src/tests/Some.Tests.ps1").write_text("Describe 'x' {}\n")
        (fake / "src/tests/ScriptContract.Tests.ps1").write_text("Describe 'untested.ps1' {}\n")
        f, _b, _n = run(fake)
        print(f"  {'PASS' if len(f) == 1 else 'FAIL'}  a script named ONLY by the convention "
              f"suite still FAILS ({len(f)} finding(s), IMP-0433)")
        ok &= len(f) == 1
        (fake / "src/tests/ScriptContract.Tests.ps1").unlink()

        # IMP-0439: an owned, dated baseline suppresses the FAIL and never the report.
        (fake / "config/gate-baselines.json").write_text(json.dumps({"baselines": [{
            "gate": GATE, "matches": "provisioning/dataverse/untested.ps1", "reason": "r",
            "owner": "lead-agent", "clears_when": "c", "expires": "2099-01-01",
            "finding": "IMP-0439"}]}))
        f, b, _n = run(fake)
        print(f"  {'PASS' if not f and len(b) == 1 else 'FAIL'}  a BASELINED script does not fail "
              f"the gate but IS still reported ({len(f)} finding(s), {len(b)} baselined)")
        ok &= (not f and len(b) == 1)

        (fake / "config/gate-baselines.json").write_text(json.dumps({"baselines": [{
            "gate": GATE, "matches": "provisioning/dataverse/untested.ps1", "reason": "r",
            "owner": "lead-agent", "clears_when": "c", "expires": "2020-01-01",
            "finding": "IMP-0439"}]}))
        try:
            run(fake)
            print("  FAIL  an EXPIRED baseline should fail")
            ok = False
        except BaselineError:
            print("  PASS  an EXPIRED baseline FAILS — the suppression is dated, not permanent")
        (fake / "config/gate-baselines.json").unlink()

        (fake / SCOPE_DECL).write_text("no declaration here\n")
        try:
            run(fake)
            print("  FAIL  a missing scope declaration should abort")
            ok = False
        except SystemExit:
            print("  PASS  a missing scope declaration ABORTS rather than passing over nothing")
    print(f"\nprovisioning-test-presence selftest: {'OK' if ok else 'FAILED'} — 7 check(s); the gate can fail.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    repo = pathlib.Path(a.repo).resolve()
    if a.selftest:
        return selftest(repo)
    try:
        findings, baselined, counted = run(repo)
    except BaselineError as exc:
        print(f"provisioning-test-presence: FAILED — {exc}", file=sys.stderr)
        return 1
    for f in findings:
        print("UNTESTED: " + f, file=sys.stderr)
    for b in baselined:
        print("BASELINED: " + b)
    untracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard", "src/tests"],
        capture_output=True, text=True).stdout.split()
    caveat = ""
    if untracked:
        caveat = (f" CAVEAT (IMP-0437): {len(untracked)} UNTRACKED file(s) under src/tests/ were "
                  f"read as if delivered, so this verdict may be greener here than in CI — "
                  f"{', '.join(untracked[:3])}{' …' if len(untracked) > 3 else ''}.")
    verdict = "FAILED" if findings else "OK"
    print(f"provisioning-test-presence: {verdict} — {counted} script(s) in the declared coverage "
          f"scope, {len(findings)} named by no behavioural test file, {len(baselined)} baselined. "
          f"Being NAMED is not behavioural coverage: "
          f"a script can be named inside a convention loop that executes none of it (IMP-0433, "
          f"IMP-0246). verify-coverage-threshold.py (C-TECH-014) is the instrument that measures "
          f"lines; this is the leading indicator that NAMES the file.{caveat}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
