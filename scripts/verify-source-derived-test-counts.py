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

TWO TIERS, and the second one is why this gate is no longer purely SOFT.

**Tier 1 — SOFT (WARN, exit 0).** The default, and still the large majority. Exits 0 even with
findings because IMP-0212's actual harm was a halted build, and because the gate cannot read
intent (see the note beside the exit in `main`).

**Tier 2 — HARD (ERROR, exit 1): derive-and-compare.** Where a flagged literal's source mention is
one of the `SETTINGS_ARRAYS` shapes, the true value is *not* a matter of intent — it is sitting in
`provisioning/deploymentSettings/*.json`, which this gate can open and count. So for that subset
only, the gate compares the literal against the set of lengths actually observed in those files:
a literal matching none of them is a measured drift, not a judgement call, and it blocks.

ADDED 2026-08-31 (improvement review 48, `IMP-0521`). The class reached x7 and the seventh
instance halted a build at `unit-tests`, build step 69 — **44 steps after this gate had already
printed the correct diagnosis, naming the exact line, as a warning nobody had to act on.** That is
the regression-check row in `agents/improvement-agent.md`: a gate that exists and did not stop the
thing it detected is mis-scoped or mis-severitied. The scope was right; the severity was the
defect. Per that file's "assert on VALUES, not on PHRASES, wherever a value exists".

The SOFT reasoning above holds for every finding this gate cannot compute — the `Get-Rev*` readers
and the mock-call counts, which need PowerShell to evaluate — and those stay SOFT and stay WARN.
Exits 1 only on a tier-2 mismatch, or when it scans zero test files, which would mean the checker
itself is broken (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEST_GLOB = "src/tests/**/*.Tests.ps1"

# Tier 2's ground truth. These are the files whose arrays the SETTINGS_ARRAYS literals are
# asserting about, and they are machine-readable — which is the whole basis for blocking on them.
SETTINGS_GLOB = "provisioning/deploymentSettings/*.json"

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


# Invoking the script under test. When a mock's call count is asserted AFTER this, the count is
# whatever the script did while walking solution source — so it scales with source, and the mock
# carve-out below must not treat it as a fixture's own cardinality.
SCRIPT_UNDER_TEST = re.compile(r"^\s*&\s*\$script:")


def mock_count_tracks_source(literal: int, block_lines: list[str]) -> bool:
    """Is this mock-call count coupled to solution source after all?

    ADDED 2026-08-23 (improvement review 19, IMP-0235 + IMP-0238). The carve-out below is
    right about captured payloads and wrong about one shape, and the SIXTH instance of this
    class landed in exactly that shape: EnsureSchema.Tests.ps1 asserts `Should -Be 69` on the
    number of fieldpermission POSTs the provisioning script made. The fake answers once per
    call, so that 69 IS the count of field permissions declared in source — it moved 51 -> 69
    when a second profile was added, and this gate stayed silent because the subject traced to
    a mock.

    Two conditions, both required, because either alone over-fires:

      * the literal is NON-ZERO. `Should -Be 0` is an invariant ("nothing was written"), not a
        count of anything, and stays correctly literal however much source the block reads.
      * the block INVOKES the script under test. Without that the calls were made by the
        fixture itself and the count is the fixture's own cardinality.
    """
    if literal == 0:
        return False
    return any(SCRIPT_UNDER_TEST.match(line) for line in block_lines)


def subject_reads_source(subject: str, block_lines: list[str],
                         literal: int | None = None) -> str | None:
    """Does the ASSERTED SUBJECT trace back to solution source, within this block?

    Tightened after the first live run. Asking "does this It block mention a source reader"
    over-fires: a block legitimately reads source for setup and then asserts on a mock's call
    count. What matters is whether the thing being COUNTED came from source.

    Resolution is textual and bounded to a few hops, which is enough for the real shapes here:
    `$ageRange.Options` -> `$ageRange = $optionSets | Where-Object ...` -> `$optionSets =
    Get-RevOptionSetDefinitions ...`.
    """
    # A mock-call count that tracks source is reported before the carve-out can swallow it.
    if (any(mock in subject for mock in MOCK_READERS)
            and literal is not None and mock_count_tracks_source(literal, block_lines)):
        return "a mock invoked once per source item, counted after running the script under test"

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
                    if literal is not None and mock_count_tracks_source(literal, block_lines):
                        return ("a mock invoked once per source item, counted after running "
                                "the script under test")
                    return None
                found = _source_mention(rhs)
                if found:
                    return found
                nxt.extend(re.findall(r"\$[A-Za-z_][\w:]*", rhs))
        frontier = nxt
    return None


# The reader string _source_mention returns for a settings array, so tier 2 can recover which
# array was matched without changing that function's signature.
SETTINGS_READER = re.compile(r"^a deployment-settings '(?P<array>\w+)' array$")


def _lengths_of(node: object, key: str) -> list[int]:
    """Every list found under `key`, at any depth. Depth matters: the real files nest these
    under `dataverse`, and a top-level-only lookup silently finds nothing and reports zero
    observed values — which would make tier 2 pass over everything (IMP-0007's shape)."""
    found: list[int] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, list):
                found.append(len(v))
            found.extend(_lengths_of(v, key))
    elif isinstance(node, list):
        for v in node:
            found.extend(_lengths_of(v, key))
    return found


def observed_array_lengths(repo_root: Path, array: str) -> dict[int, list[str]]:
    """Observed length -> the settings files exhibiting it.

    A SET, not a single number, and deliberately so: `groupTeams` is legitimately 2 in
    `dev-settings.example.json` and 3 in test/prd. The rule tier 2 enforces is therefore
    *matches no observed value*, never *matches one nominated file* — otherwise correct
    per-environment divergence would read as drift.
    """
    observed: dict[int, list[str]] = {}
    for path in sorted(repo_root.glob(SETTINGS_GLOB)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for length in _lengths_of(data, array):
            observed.setdefault(length, []).append(path.relative_to(repo_root).as_posix())
    return observed


def scan(repo_root: Path) -> tuple[list[str], list[str], dict[str, int]]:
    failures: list[str] = []
    errors: list[str] = []
    counts = {"files": 0, "literals": 0, "source_coupled": 0, "annotated": 0,
              "compared": 0, "mismatched": 0}

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
                reader = subject_reads_source(m.group("subject"), block_lines,
                                              literal=int(m.group("n")))
                if reader is None:
                    continue          # a fixture's or a mock's own cardinality — correctly literal
                counts["source_coupled"] += 1
                if ANNOTATION in block.lower():
                    counts["annotated"] += 1
                    continue

                # ── Tier 2: derive and compare, where the true value is machine-readable ──
                settings = SETTINGS_READER.match(reader)
                if settings:
                    array = settings.group("array")
                    observed = observed_array_lengths(repo_root, array)
                    if observed:
                        counts["compared"] += 1
                        literal = int(m.group("n"))
                        if literal not in observed:
                            counts["mismatched"] += 1
                            seen = ", ".join(
                                f"{n} in {', '.join(files)}"
                                for n, files in sorted(observed.items()))
                            errors.append(
                                f"{rel}:{start + offset + 1}: asserts a literal count of "
                                f"{literal} on `{m.group('subject')}.Count` for the "
                                f"'{array}' array, and NO settings file declares that many. "
                                f"Observed: {seen}.\n"
                                f"    This is not a judgement about intent — it is a value "
                                f"comparison against files this gate reads, which is why it "
                                f"blocks where the rest of this gate warns. Either the literal "
                                f"is stale (update it, or better, derive it from the same "
                                f"source) or the settings files are wrong. Left as a WARN, this "
                                f"exact drift halted a build 44 steps later at `unit-tests` "
                                f"(IMP-0521).")
                            continue
                    # A literal matching an observed length is a correct transcription — still
                    # not DERIVED, so the tier-1 WARN below is retained at its usual wording.

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
    return failures, errors, counts


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
        # ── The sixth instance of this class landed in the shape the mock carve-out excluded.
        # Both fixtures below are mock-call counts; only the first tracks source.
        ("a NON-ZERO mock count asserted after running the script under test IS flagged",
         "    It 'every permission is posted' {\n"
         "        & $script:EnsureSchema -Env dev | Out-Null\n"
         "        $calls = @(Get-FakeDataverseCalls -Method POST -UriPattern 'fieldpermissions$')\n"
         "        $calls.Count | Should -Be 69\n"
         "    }\n", True),
        ("a ZERO mock count after the same invocation is an INVARIANT and stays quiet",
         "    It 'nothing was written' {\n"
         "        & $script:EnsureSchema -Env dev | Out-Null\n"
         "        $calls = @(Get-FakeDataverseCalls -Method DELETE)\n"
         "        $calls.Count | Should -Be 0\n"
         "    }\n", False),
    ]

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for why, body, expect_fail in cases:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "src" / "tests" / "provisioning").mkdir(parents=True)
            (root / "src" / "tests" / "provisioning" / "X.Tests.ps1").write_text(
                test_file(body), encoding="utf-8")
            failures, errors, counts = scan(root)
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
        _f, _e, counts = scan(root)
        ok = counts["files"] == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  no test files yields zero scanned "
              f"(caller must fail, not pass): files={counts['files']}")
        failed += 0 if ok else 1

    # ── Tier 2: derive-and-compare (review 48, IMP-0521). These need settings files on disk,
    # which is exactly why they are a separate block: the tier-1 cases above deliberately have
    # none, so tier 2 stays inert for them and their expectations are unchanged.
    def rows(n: int) -> list[dict]:
        return [{"key": f"k{i}"} for i in range(n)]

    tier2 = [
        ("a settings literal matching NO observed length is an ERROR",
         "    It 'keys' {\n"
         "        $testKeys = @($s.dataverse.settingRows | ForEach-Object { $_.key })\n"
         "        $testKeys.Count | Should -Be 15\n"
         "    }\n",
         {"test-settings.json": {"dataverse": {"settingRows": rows(16)}}}, True),
        ("a settings literal matching an observed length is NOT an error",
         "    It 'keys' {\n"
         "        $testKeys = @($s.dataverse.settingRows | ForEach-Object { $_.key })\n"
         "        $testKeys.Count | Should -Be 16\n"
         "    }\n",
         {"test-settings.json": {"dataverse": {"settingRows": rows(16)}}}, False),
        # The groupTeams case. Files legitimately DISAGREE per environment, so the rule is
        # "matches no observed value" — a literal of either 2 or 3 must be accepted.
        ("a literal matching ONE of several legitimately differing files is NOT an error",
         "    It 'teams' {\n"
         "        $t = @($s.dataverse.groupTeams)\n"
         "        $t.Count | Should -Be 2\n"
         "    }\n",
         {"dev-settings.example.json": {"dataverse": {"groupTeams": rows(2)}},
          "prd-settings.json": {"dataverse": {"groupTeams": rows(3)}}}, False),
        ("a literal matching NEITHER of two differing files IS an error",
         "    It 'teams' {\n"
         "        $t = @($s.dataverse.groupTeams)\n"
         "        $t.Count | Should -Be 7\n"
         "    }\n",
         {"dev-settings.example.json": {"dataverse": {"groupTeams": rows(2)}},
          "prd-settings.json": {"dataverse": {"groupTeams": rows(3)}}}, True),
        # No settings file declares the array -> nothing to compare against. Must stay a tier-1
        # WARN and must NOT block: a gate that blocks on an absent ground truth is IMP-0007's
        # shape pointing the other way.
        ("a settings array no file declares is NOT compared and does NOT block",
         "    It 'audited' {\n"
         "        $tables = @($s.dataverse.auditing.auditedTables)\n"
         "        $tables.Count | Should -Be 4\n"
         "    }\n",
         {"test-settings.json": {"dataverse": {"settingRows": rows(16)}}}, False),
        # The annotation escape hatch suppresses tier 1, and therefore tier 2 as well. Recorded
        # as a deliberate fixture so the behaviour cannot change silently.
        ("the count-coupled annotation suppresses tier 2 as well as tier 1",
         "    It 'keys' {\n"
         "        # count-coupled by design.\n"
         "        $testKeys = @($s.dataverse.settingRows)\n"
         "        $testKeys.Count | Should -Be 15\n"
         "    }\n",
         {"test-settings.json": {"dataverse": {"settingRows": rows(16)}}}, False),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        for why, body, settings, expect_error in tier2:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "src" / "tests" / "provisioning").mkdir(parents=True)
            (root / "src" / "tests" / "provisioning" / "X.Tests.ps1").write_text(
                test_file(body), encoding="utf-8")
            sdir = root / "provisioning" / "deploymentSettings"
            sdir.mkdir(parents=True)
            for name, payload in settings.items():
                (sdir / name).write_text(json.dumps(payload), encoding="utf-8")
            _failures, errors, counts = scan(root)
            ok = bool(errors) == expect_error
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(errors)} error(s), "
                  f"{counts['compared']} compared, {counts['mismatched']} mismatched")
            if not ok:
                for e in errors:
                    print(f"          {e.splitlines()[0]}")
                failed += 1

    # The trailing "SELFTEST OK — <n> fixtures" is a repository convention, not decoration:
    # verify-constraint-verifiers.py reads this total to check any constraint row that states a
    # fixture count for this gate, so extending the gate cannot leave a constraint describing it
    # stale (IMP-0260). Derived from the case list, never typed.
    total = len(cases) + len(tier2) + 1
    if failed:
        print(f"\nSELFTEST: FAILED — {failed} case(s) of {total} fixtures")
        return 1
    print(f"\nSELFTEST: PASS\nverify-source-derived-test-counts: SELFTEST OK — {total} fixtures.")
    return 0


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
    failures, errors, counts = scan(repo_root)

    if counts["files"] == 0:
        print(f"ERROR: '{TEST_GLOB}' matched no files. A checker with nothing to read must fail "
              f"rather than report PASS (IMP-0007).", file=sys.stderr)
        return 1

    # ── Tier 2 first: these BLOCK, so they must not be buried under the WARN stream ──────────
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if failures:
        for f in failures:
            print(f"WARNING: {f}", file=sys.stderr)
        print(f"\nSOURCE-DERIVED TEST COUNTS: {len(failures)} fragile literal(s) of "
              f"{counts['source_coupled']} source-coupled assertion(s), out of "
              f"{counts['literals']} literal count(s) across {counts['files']} test file(s) "
              f"— tier 1 SOFT: reported as WARN, never blocking.", file=sys.stderr)
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
        #
        # TIER 2 IS THE NAMED EXCEPTION to all of the above (review 48, IMP-0521). Reasons 1 and 2
        # are both arguments from UNCERTAINTY — the gate cannot tell a stale literal from a
        # correct one, so it must not block. That uncertainty does not exist when the true value
        # is a number in a JSON file this gate just read. Where it can measure, it blocks.
        if errors:
            print(f"\nSOURCE-DERIVED TEST COUNTS: {len(errors)} settings-array literal(s) match "
                  f"no observed value, of {counts['compared']} compared — tier 2 HARD.",
                  file=sys.stderr)
            return 1
        return 0

    if errors:
        print(f"\nSOURCE-DERIVED TEST COUNTS: {len(errors)} settings-array literal(s) match no "
              f"observed value, of {counts['compared']} compared — tier 2 HARD.",
              file=sys.stderr)
        return 1

    print(f"SOURCE-DERIVED TEST COUNTS: PASS — {counts['literals']} literal count assertion(s) "
          f"across {counts['files']} test file(s); {counts['source_coupled']} are coupled to "
          f"solution source and every one is derived or annotated "
          f"({counts['annotated']} annotated); {counts['compared']} settings-array literal(s) "
          f"compared against source, 0 mismatched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
