#!/usr/bin/env python3
"""A test asserting a count of SOLUTION SOURCE must derive it, or say it is count-coupled.

WHY THIS EXISTS, and why it is a script rather than another paragraph.

`test-coupled-to-absolute-counts` is at **x5**: `IMP-0005`, `IMP-0039`, `IMP-0120`, `IMP-0155`,
`IMP-0212`. The fifth halted a build — `DeploymentSettings.Tests.ps1` expected 4 audited tables
against a schema that legitimately has 6.

**The rule is not missing. It is excellent, and it did not work.**
`knowledge/technology/coding-standards.md` carries a full write-up produced after instances 1 and
2: a discrimination table separating *a total this project's own source declares* (fragile — derive
it) from *a fixture's own cardinality* (stable — leave it literal), a preference order (an
invariant that needs no count, then a derived count, then a literal with a stated caveat), and an
explicit escape hatch — a deliberate literal "carries a comment stating that plainly".

Then instances 3, 4 and 5 happened. And **one** assertion in the whole suite carries the
annotation the convention asks for.

That is the regression rule from `agents/improvement-agent.md` in its purest form: a recurrence
after a *prose* change is evidence the fix was at the wrong altitude. The write-up lives in a
knowledge file nobody opens at the moment they type a literal, and nothing checked it. So this
script is the same rule, at the moment it applies.

HOW IT AVOIDS BEING A NOISY GATE. This matters, because a gate that fires on correct code is how
the `gate-fires-on-nothing` class (x3) happens, and the suite has **234** absolute-count
assertions of which the large majority are legitimately literal.

It does not flag a literal count. It flags a literal count whose SUBJECT is built from solution
source, inside the same `It` block — the exact tell `coding-standards.md` names: *"does the number
describe something under src/solutions/RevitaliseGrantAutomation/, or something under
src/tests/fixtures/ or a mock's own setup?"* A mock-invocation count (`$posts.Count`), a fixture's
own cardinality, a flow's trigger-key count: all untouched, because none of them is populated from
a source reader.

Source is recognised two ways, both narrow and named:
  * one of this repo's own source-reading helpers — `Get-RevEntityLogicalNames`,
    `Get-RevEntityDefinition`, `Get-RevOptionSetDefinitions`, `Get-RevRoleDefinitions`,
    `Get-RevRelationshipDefinitions`, `Get-RevFieldSecurityProfileDefinition`,
    `Get-RevLookupAttributes`;
  * a deployment-settings JSON read (`dataverse.auditing.auditedTables` and friends), which is the
    shape that produced `IMP-0212`.

THE ESCAPE HATCH IS THE ONE ALREADY DOCUMENTED. Keep the literal and write the comment
`coding-standards.md` already prescribes — any line in the block containing `count-coupled`
satisfies this gate. That is deliberate: `EnsureSchema.Tests.ps1` keeps
`$securedColumns.Count | Should -Be 51` on purpose, beside a count-free `Compare-Object`, with the
fragility named in its own comment. That assertion must keep passing this gate, and it does.

WHAT IT CANNOT DO. It reasons about one `It` block at a time, textually. A collection assembled in
a `BeforeAll` several screens up and asserted in an `It` is invisible to it — the honest limit, and
the reason this gate is a floor rather than a proof. It also cannot tell a *correct* derived count
from an incorrect one; deriving is what it asks for, not arithmetic.

Run:
    python3 scripts/verify-source-derived-test-counts.py
    python3 scripts/verify-source-derived-test-counts.py --selftest

**SOFT.** Exits 0 even with findings — they are WARNings, never blockers — because IMP-0212's
actual harm was a halted build, and because the gate cannot read intent (see the note beside the
exit in `main`). Exits 1 only when it scans zero test files, which would mean the checker itself
is broken (`IMP-0007`). Promote to HARD when the live count reaches zero and holds.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEST_GLOB = "src/tests/**/*.Tests.ps1"

# A literal count assertion: `$x.Count | Should -Be 4`, `(...).Count | Should -BeExactly 12`.
LITERAL_COUNT = re.compile(
    r"(?P<subject>[^\s|]+)\.Count\s*\|\s*Should\s+-Be(?:Exactly)?\s+(?P<n>\d+)")

# This repository's own readers of solution source. Named explicitly rather than pattern-matched:
# the whole point is to flag ONLY counts of things the solution declares.
SOURCE_READERS = (
    "Get-RevEntityLogicalNames", "Get-RevEntityDefinition", "Get-RevOptionSetDefinitions",
    "Get-RevRoleDefinitions", "Get-RevRelationshipDefinitions",
    "Get-RevFieldSecurityProfileDefinition", "Get-RevLookupAttributes",
)

# The settings-file shape that produced IMP-0212 — a count of an array whose truth is the
# Entities/ folders on disk, asserted against a hand-typed number.
SETTINGS_ARRAYS = ("auditedTables", "settingRows", "columnSecurityProfiles", "groupTeams")

# The escape hatch coding-standards.md already prescribes.
ANNOTATION = "count-coupled"

IT_START = re.compile(r"^\s*It\s+['\"]")
BLOCK_START = re.compile(r"^\s*(It|Describe|Context|BeforeAll|BeforeEach)\s")


def it_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """(start, end) line indices for each `It` block, ending at the next block at any depth."""
    blocks: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        if not IT_START.match(line):
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if BLOCK_START.match(lines[j]):
                end = j
                break
        blocks.append((i, end))
    return blocks


# Readers of a MOCK's own recorded calls. Never solution source, however much source the
# surrounding block also reads — the first draft flagged
# `@(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0` because its It block happened to
# mention a settings array elsewhere. That is a fixture's own cardinality and correctly literal.
MOCK_READERS = ("Get-FakeDataverseCalls", "Should -Invoke", "Get-Fake")


def _source_mention(text: str) -> str | None:
    if any(mock in text for mock in MOCK_READERS):
        return None
    for reader in SOURCE_READERS:
        if reader in text:
            return reader
    for array in SETTINGS_ARRAYS:
        if array in text:
            return f"a deployment-settings '{array}' array"
    return None


def subject_reads_source(subject: str, block_lines: list[str]) -> str | None:
    """Does the ASSERTED SUBJECT trace back to solution source, within this block?

    Tightened after the first live run. Asking "does this It block mention a source reader"
    over-fires: a block legitimately reads source for setup and then asserts on a mock's call
    count. What matters is whether the thing being COUNTED came from source.

    Resolution is textual and bounded to a few hops, which is enough for the real shapes here:
    `$ageRange.Options` -> `$ageRange = $optionSets | Where-Object ...` -> `$optionSets =
    Get-RevOptionSetDefinitions ...`.
    """
    direct = _source_mention(subject)
    if direct:
        return direct

    root = re.match(r"[@(\s]*(?P<var>\$[A-Za-z_][\w:]*)", subject)
    if not root:
        return None

    seen: set[str] = set()
    frontier = [root.group("var")]
    for _hop in range(4):
        if not frontier:
            break
        nxt: list[str] = []
        for var in frontier:
            if var in seen:
                continue
            seen.add(var)
            assign = re.compile(r"^\s*" + re.escape(var) + r"\s*=\s*(?P<rhs>.+)$")
            for line in block_lines:
                m = assign.match(line)
                if not m:
                    continue
                rhs = m.group("rhs")
                # A mock assignment is TERMINAL. Without this the walk kept going and found a
                # source reader somewhere else in the block, which flagged
                # `$body.Attributes.Count | Should -Be 1` — where `$body` is a captured request
                # payload, i.e. a fixture's own cardinality and correctly literal.
                if any(mock in rhs for mock in MOCK_READERS):
                    return None
                found = _source_mention(rhs)
                if found:
                    return found
                nxt.extend(re.findall(r"\$[A-Za-z_][\w:]*", rhs))
        frontier = nxt
    return None


def scan(repo_root: Path) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    counts = {"files": 0, "literals": 0, "source_coupled": 0, "annotated": 0}

    for path in sorted(repo_root.glob(TEST_GLOB)):
        if not path.is_file():
            continue
        counts["files"] += 1
        rel = path.relative_to(repo_root).as_posix()
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

        for start, end in it_blocks(lines):
            block_lines = lines[start:end]
            block = "\n".join(block_lines)
            for offset, line in enumerate(block_lines):
                m = LITERAL_COUNT.search(line)
                if not m:
                    continue
                counts["literals"] += 1
                reader = subject_reads_source(m.group("subject"), block_lines)
                if reader is None:
                    continue          # a fixture's or a mock's own cardinality — correctly literal
                counts["source_coupled"] += 1
                if ANNOTATION in block.lower():
                    counts["annotated"] += 1
                    continue
                failures.append(
                    f"{rel}:{start + offset + 1}: asserts a literal count of "
                    f"{m.group('n')} on `{m.group('subject')}.Count`, in an It block that reads "
                    f"solution source ({reader}). This number changes on every legitimate schema "
                    f"addition, so a failure here reads as a regression when it is a maintenance "
                    f"cost — that is how a build was halted on 2026-08-23, the FIFTH instance "
                    f"(IMP-0005, IMP-0039, IMP-0120, IMP-0155, IMP-0212).\n"
                    f"    Fix it the way coding-standards.md prescribes, in order: (1) an "
                    f"invariant that needs no count — `Compare-Object` between the two sources, "
                    f"as EnsureSchema.Tests.ps1's secured-column cross-reference already does; "
                    f"(2) a count derived from the same source the script reads; (3) keep the "
                    f"literal and write the '{ANNOTATION} by design' comment, which satisfies "
                    f"this gate.")
    return failures, counts


def selftest() -> int:
    import tempfile

    def test_file(body: str) -> str:
        return "Describe 'x' {\n" + body + "\n}\n"

    cases = [
        ("a literal count of a source-derived set is caught",
         "    It 'all tables' {\n"
         "        $t = @(Get-RevEntityLogicalNames)\n"
         "        $t.Count | Should -Be 4\n"
         "    }\n", True),
        ("the settings-array shape that halted the build is caught",
         "    It 'audited' {\n"
         "        $tables = @($s.dataverse.auditing.auditedTables)\n"
         "        $tables.Count | Should -Be 4\n"
         "    }\n", True),
        ("a mock-invocation count is NOT flagged",
         "    It 'posts twice' {\n"
         "        $posts = @(Get-FakeDataverseCalls -Method POST)\n"
         "        $posts.Count | Should -Be 2\n"
         "    }\n", False),
        ("a fixture's own cardinality is NOT flagged",
         "    It 'fixture rows' {\n"
         "        $rows = @('a','b','c')\n"
         "        $rows.Count | Should -Be 3\n"
         "    }\n", False),
        ("the documented annotation satisfies the gate",
         "    It 'secured columns' {\n"
         "        # This assertion is count-coupled by design and breaks on every schema addition.\n"
         "        $c = @(Get-RevEntityLogicalNames)\n"
         "        $c.Count | Should -Be 51\n"
         "    }\n", False),
        ("a mock count in a block that ALSO reads source is NOT flagged",
         "    It 'nothing written' {\n"
         "        $rows = @($s.dataverse.auditing.auditedTables)\n"
         "        @(Get-FakeDataverseCalls -Method PATCH).Count | Should -Be 0\n"
         "    }\n", False),
        ("a chained subject IS traced to source",
         "    It 'option values' {\n"
         "        $optionSets = Get-RevOptionSetDefinitions -RepoRoot $r\n"
         "        $ageRange = $optionSets | Where-Object Name -eq 'rev_agerange'\n"
         "        $ageRange.Options.Count | Should -Be 9\n"
         "    }\n", True),
        ("a derived count with no literal is NOT flagged",
         "    It 'derived' {\n"
         "        $expected = @(Get-RevEntityLogicalNames).Count\n"
         "        $actual = @($s.dataverse.auditing.auditedTables).Count\n"
         "        $actual | Should -Be $expected\n"
         "    }\n", False),
    ]

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for why, body, expect_fail in cases:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "src" / "tests" / "provisioning").mkdir(parents=True)
            (root / "src" / "tests" / "provisioning" / "X.Tests.ps1").write_text(
                test_file(body), encoding="utf-8")
            failures, counts = scan(root)
            got = bool(failures)
            ok = got == expect_fail
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(failures)} failure(s) "
                  f"({counts['literals']} literal, {counts['source_coupled']} source-coupled, "
                  f"{counts['annotated']} annotated)")
            if not ok:
                for f in failures:
                    print(f"          {f.splitlines()[0]}")
                failed += 1

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src" / "tests").mkdir(parents=True)
        _f, counts = scan(root)
        ok = counts["files"] == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  no test files yields zero scanned "
              f"(caller must fail, not pass): files={counts['files']}")
        failed += 0 if ok else 1

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="A test asserting a count of solution source must derive it or annotate it.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]
    failures, counts = scan(repo_root)

    if counts["files"] == 0:
        print(f"ERROR: '{TEST_GLOB}' matched no files. A checker with nothing to read must fail "
              f"rather than report PASS (IMP-0007).", file=sys.stderr)
        return 1

    if failures:
        for f in failures:
            print(f"WARNING: {f}", file=sys.stderr)
        print(f"\nSOURCE-DERIVED TEST COUNTS: {len(failures)} fragile literal(s) of "
              f"{counts['source_coupled']} source-coupled assertion(s), out of "
              f"{counts['literals']} literal count(s) across {counts['files']} test file(s) "
              f"— SOFT: reported as WARN, never blocking.", file=sys.stderr)
        # ── SOFT on purpose, and this is the load-bearing design decision ──────────────────
        # Exit 0 even with findings, matching verify-derived-counts.py's convention for the same
        # class of drift. Three reasons, in order of weight:
        #
        # 1. IMP-0212's actual harm was A HALTED BUILD. A gate that blocks the build to complain
        #    about an assertion that might go stale would reproduce the harm it exists to prevent,
        #    on a wider surface.
        # 2. It cannot read intent, and one live finding proves it. EnsureSchema.Tests.ps1's
        #    `$body.Attributes.Count | Should -Be 1` asserts that ConvertTo-RevEntityBody inlines
        #    exactly ONE attribute — an invariant of the transformation, which happens to be
        #    reached through a source reader. Correct as a literal, and indistinguishable from a
        #    schema total by any textual rule. Annotating it `count-coupled` would be a lie, so
        #    the gate must tolerate being wrong about it rather than force a false comment.
        # 3. coding-standards.md already frames the retrofit as "scoped implementation work for
        #    whoever next touches src/tests/", not a wholesale rewrite behind a review. A WARN
        #    stream is what that framing needs; a blocker is not.
        #
        # Promote to HARD only when the live count reaches zero and stays there — at that point a
        # new finding is a genuine regression rather than a backlog item.
        return 0

    print(f"SOURCE-DERIVED TEST COUNTS: PASS — {counts['literals']} literal count assertion(s) "
          f"across {counts['files']} test file(s); {counts['source_coupled']} are coupled to "
          f"solution source and every one is derived or annotated "
          f"({counts['annotated']} annotated).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
