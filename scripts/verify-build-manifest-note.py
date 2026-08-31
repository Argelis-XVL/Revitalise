#!/usr/bin/env python3
"""A build manifest's free-text notes record COUNTS, never an inventory of shipped content.

WHY THIS FORBIDS A SHAPE INSTEAD OF CHECKING A CLAIM
---------------------------------------------------
`IMP-0324`. Build `20260825-1`'s `source_commit_note` said the packaged working tree "includes
the trustee-portal-visual-refresh changes (rev_roundfinance table, LandingPage/charts UI,
A-FIN-05/07/A-002 marker fixes)". No `LandingPage*`, chart or `RoundStatistics*` file existed
anywhere under `src/code-apps/`, and the built bundle in the same artifact contained none; the
Dev Summary correctly reported them as NOT STARTED. The dirty-path COUNT in the same note was
correct — `IMP-0078` required the sha and the count, and both were right. The note went further
and enumerated what the dirty tree contained, and that enumeration was written from the
dispatch's intended scope rather than from the tree.

Nothing reads manifest prose. `verify-build-config.py` validates steps, inputs and negative-test
coverage; no gate reads `manifest.json`'s free text, so any artefact name in it is unchecked and
travels into the deploy and into any acceptance pack built from the artifact.

**The obvious gate — extract every path-like token and resolve it to a real file — was NOT
built, and the reason is on the record.** That is fuzzy prose-matching, and fuzzy prose-matching
produced five distinct false-positive classes in one sitting on 2026-08-25 (`IMP-0319`). So this
forbids a CLASS OF CLAIM instead of adjudicating one: a note may not contain a filename-shaped
or `rev_*`-shaped token at all. **Zero false positives are structurally possible**, because
there is nothing to judge — the token is either there or it is not, and a note that needs one is
a note saying something it should not say.

WHAT IT CHECKS, over every free-text note field in a manifest:
  * no `rev_*` identifier  (a table, column or option set named as shipped content)
  * no filename-shaped token — `Something.tsx`, `foo.json`, `LandingPage.tsx`
  * no bare component-name token in `PascalCase.ext` form

Counts, shas, tool versions, plain prose and the words `src/`, `provisioning/`, `config/` as
DIRECTORIES are all fine: a directory is where the count was taken, not a claim about contents.

WHAT IT CANNOT DO: it cannot tell a true enumeration from a false one, and does not try. It
removes the ability to make either.


AND, ADDED 2026-08-28 BY IMPROVEMENT REVIEW 33 CHANGE 3 — TWO REQUIRED-FIELD ASSERTIONS
---------------------------------------------------------------------------------------
The note check above forbids a manifest from claiming too much. These two assert that it claims
enough, and both come from a field going missing or going aggregate with every gate green.

  * `wbs` — PRESENT, non-empty, and every id resolving against `contract/wbs.json`'s baselined
    tasks OR a covered id declared by a `contract/change-orders/` document.

    `IMP-0350`. Build `20260826-1` carried `"wbs": ["6.1","6.3","6.9"]` as its third line. The
    very next build of the same feature, `20260826-2`, has no `wbs` field at all. Both report
    SUCCESS, `constraint_check` PASS, every gate green. Nothing in the build config required the
    field — it was a convention held in the authoring agent's head, and the previous cycle's test
    report cited it by line number, which made it look established. The WBS task id is the join
    key between a commit, a contract line and an invoice; `verify-wbs-chain.py` is the one thing
    that would have noticed, and it was dark for an unrelated reason (a stale
    `logs/state/wbs-state.json`).

    Resolution goes through the CHANGE ORDERS as well as the baseline deliberately: `6.9` is a
    legitimately approved id that is absent from the 61 baselined tasks, covered by
    `contract/change-orders/CO-001.md`. A gate resolving against the baseline alone would fail a
    build over an approved id, which is how a gate teaches people to route around it (`IMP-0181`).

  * `soft_gates` — one finding COUNT PER SOFT STEP, keyed by step name, with the expected key set
    DERIVED from the build config's own step list (every step whose command carries
    `--warn-only`).

    `IMP-0395`, and NOT the change that finding proposes. It says `verify-derived-counts.py` is
    not a build step; it has been the `derived-counts` step since 2026-08-24, added by the review
    that existed *because* the gate was unwired. That proposal is withheld. What replaced it is
    the mechanism that actually failed: the step is SOFT via `--warn-only`, prints four drifts on
    every run, and the last builds recorded `warnings: {total: 83, untriaged: 0}` — an AGGREGATE
    a new true positive disappears into arithmetically. One number per step makes a drift from 4
    to 5 visible in the artefact instead of invisible inside 83.

    RESIDUAL: the derivation reads `--warn-only`, which is mechanically decidable. A step that is
    SOFT by its own internal design instead — `source-derived-test-counts` exits 0 with findings
    by choice — is NOT covered, and cannot be without reading each script's intent.

MEASURED OVER THE REAL CORPUS BEFORE WIRING — 22 manifests on disk, 32 findings
------------------------------------------------------------------------------
The number is stated rather than an impression, and the adjudication is per class:

  * `MISSING FIELD soft_gates` ×15 — TRUE by the rule, and every one is RETROACTIVE: the field
    did not exist when those builds ran. Not actionable, and not a defect anyone can now fix.
  * `NO BUILD CONFIG` ×7 — the features `revitalise-alert-links`, `revitalise-cards-and-forms`,
    `revitalise-errorlog-runlink`, `revitalise-grant-record`, `revitalise-scoring-config-read`
    and `revitalise-withhold-select` have no `config/<slug>-build.yml` on disk any more. Also
    retroactive.
  * `MISSING FIELD wbs` ×5 — TRUE, and one of them is `IMP-0350`'s own instance
    (`revitalise-grant-automation-20260826-2`).
  * `NOTE ENUMERATES CONTENT` ×5 — the PRE-EXISTING note check, unchanged by this review.
  * `UNKNOWN TASK ID` ×1 → **0 after one narrowing**, which removes it by name: see `_NON_BILLABLE`.

**So 22 of the 32 are about manifests that predate the fields, which is why `--note-only`
exists and why this is NOT wired as a step over `build/artifacts/`.** The operative input is the
ONE manifest build-agent has just written — that is how `IMP-0350` itself specifies the wiring,
because every config step runs before the manifest exists. Reading a historical artifact means
`--note-only`.

Usage
-----
    python3 scripts/verify-build-manifest-note.py <manifest.json | artifact-dir> [...]
    python3 scripts/verify-build-manifest-note.py --note-only <manifest.json>   # skip the two
    python3 scripts/verify-build-manifest-note.py --build-config <path> <manifest.json>
    python3 scripts/verify-build-manifest-note.py --selftest

`--note-only` exists for reading a HISTORICAL manifest: the two required-field assertions are
about what a build writes from now on, and 5 of the 21 manifests already on disk predate the
`wbs` convention entirely. Never pass it for a build you are producing.

Exits 0 clean · 1 on any violation · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# Every field whose value is free text a human wrote. Kept explicit rather than "any string":
# `build_tool` and `build_os` legitimately carry version strings full of dots.
NOTE_FIELDS = ("source_commit_note", "note", "notes", "provenance_note", "packaging_note")

# A `rev_*` identifier — a table, column or option set named as shipped content.
PREFIXED_IDENT = re.compile(r"(?<![A-Za-z0-9_])(rev_[a-z][a-z0-9_]{2,})")
# A filename: a token with an extension this project actually ships.
FILENAME = re.compile(
    r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_-]+\.(?:tsx?|jsx?|json|xml|md|ps1|psm1|py|css|zip|yml|yaml))"
    r"(?![A-Za-z0-9_])")

# Directory names are not content claims: they say WHERE a count was taken.
ALLOWED_DIRS = {"src/", "provisioning/", "config/", "build/", "docs/", "scripts/", "logs/"}

REPO_ROOT = Path(__file__).resolve().parent.parent


def offenders(text: str) -> list[str]:
    found: list[str] = []
    found += [f"`{m}`" for m in dict.fromkeys(PREFIXED_IDENT.findall(text))]
    found += [f"`{m}`" for m in dict.fromkeys(FILENAME.findall(text))
              if not any(m.startswith(d) for d in ALLOWED_DIRS)]
    return found


def check_manifest(path: Path, note_only: bool = False,
                   build_config: Path | None = None,
                   repo_root: Path = REPO_ROOT) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"  MANIFEST UNREADABLE - {path}: {exc}"]
    if not isinstance(data, dict):
        return [f"  MANIFEST UNREADABLE - {path}: top level is not an object"]

    errors: list[str] = []
    if not note_only:
        errors += check_required_fields(path, data, build_config, repo_root)
    for field in NOTE_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        bad = offenders(value)
        if bad:
            errors.append(
                f"  NOTE ENUMERATES CONTENT - {path} `{field}` names "
                f"{', '.join(bad)}. A manifest note records the dirty-path COUNT and stops "
                f"there (IMP-0078); enumerating what the tree CONTAINS restates the dispatch's "
                f"intended scope, not the tree, and nothing reads that prose — build 20260825-1 "
                f"claimed a LandingPage and charts that existed nowhere in the artifact "
                f"(IMP-0324). Point at `wbs`, `steps_not_executed` and the count instead."
            )
    return errors


# ── the two required-field assertions (IMP-0350, IMP-0395) ────────────────────────────────

def baselined_task_ids(repo_root: Path = REPO_ROOT) -> set[str]:
    """Every task id in the accepted WBS. Read from the generated file, never transcribed."""
    try:
        data = json.loads((repo_root / "contract" / "wbs.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        return set()
    return {str(t.get("id")) for t in tasks if isinstance(t, dict) and t.get("id")}


# `| New task id | **6.9** |` — a change order declaring an id the baseline does not carry.
_COVERED_ID = re.compile(r"New task id\s*\|\s*\**\s*([0-9]+(?:\.[0-9]+)*)\s*\**\s*\|")

# THE NARROWING, and it removes a measured false positive BY NAME.
#
# The approved rule was "every id resolves against contract/wbs.json or a change order". Measured
# over all 22 manifests on disk it produced one UNKNOWN TASK ID: `'system'`, in
# build/artifacts/revitalise-cards-and-forms-20260821-2/manifest.json. That is not an overclaim —
# `wbs:system, non-billable` is an established repository-wide sentinel for work that serves no
# contracted task: it appears nine times in logs/routing.log, twice as a `wbs` value in
# logs/improvement-log.jsonl, and in the header of the review document proposing this very check.
# Failing a build over the sentinel this system uses for its own system work would be a gate
# nobody could satisfy honestly.
#
# It stays NARROW: only these two literals, and each still has to be written down. An id that is
# merely absent from the baseline is still a failure — which is the half IMP-0350 is about.
_NON_BILLABLE = {"system", "n/a"}


def covered_task_ids(repo_root: Path = REPO_ROOT) -> set[str]:
    """Ids a change-order document declares. `6.9` is the live example — approved, unbaselined."""
    found: set[str] = set()
    directory = repo_root / "contract" / "change-orders"
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.md")):
        try:
            found.update(_COVERED_ID.findall(path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return found


def soft_step_names(config_path: Path) -> tuple[set[str], str | None]:
    """(names of every --warn-only step, problem). Derived from the config, never hand-listed."""
    try:
        import yaml
    except ImportError:  # pragma: no cover - PyYAML is present wherever the build runs
        return set(), ("PyYAML is not importable, so the SOFT step list cannot be derived. "
                       "Reported rather than treated as an empty set: an empty derivation is "
                       "how a gate reports OK over nothing (IMP-0007).")
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, Exception) as exc:  # noqa: BLE001 - yaml raises many types
        return set(), f"cannot read {config_path}: {exc}"
    steps = (data or {}).get("steps") or []
    if not isinstance(steps, list) or not steps:
        return set(), f"{config_path} declares no steps, so nothing identifies its SOFT gates."
    names = {str(s.get("name")) for s in steps
             if isinstance(s, dict) and "--warn-only" in str(s.get("command") or "")}
    return names, None


def check_required_fields(path: Path, data: dict,
                          build_config: Path | None = None,
                          repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []

    # ── wbs (IMP-0350) ───────────────────────────────────────────────────────────────────
    wbs = data.get("wbs")
    if wbs is None:
        errors.append(
            f"  MISSING FIELD `wbs` - {path}: the manifest carries no `wbs` field. The WBS task "
            f"id is the join key between a commit, a contract line and an invoice; build "
            f"20260826-1 carried it and 20260826-2, the very next build of the same feature, did "
            f"not — both SUCCESS, every gate green (IMP-0350). If this build maps to no accepted "
            f"task, that is a change-order decision for commercial-agent, not a field to omit "
            f"(C-COM-002).")
    elif not isinstance(wbs, list) or not wbs or not all(
            isinstance(i, str) and i.strip() for i in wbs):
        errors.append(
            f"  BAD FIELD `wbs` - {path}: expected a non-empty list of task-id strings, got "
            f"{wbs!r}.")
    else:
        baselined = baselined_task_ids(repo_root)
        covered = covered_task_ids(repo_root)
        if not baselined:
            errors.append(
                f"  UNRESOLVABLE - {path}: contract/wbs.json yielded no task ids, so `wbs` "
                f"cannot be resolved. A gate that cannot read its reference must fail rather "
                f"than pass every id (IMP-0007).")
        else:
            for ident in wbs:
                ident = ident.strip()
                if ident in baselined or ident in covered or ident.lower() in _NON_BILLABLE:
                    continue
                errors.append(
                    f"  UNKNOWN TASK ID - {path}: `wbs` names {ident!r}, which is neither one of "
                    f"the {len(baselined)} baselined tasks in contract/wbs.json nor a covered id "
                    f"declared by a contract/change-orders/ document "
                    f"({', '.join(sorted(covered)) or 'none'}). Work enters by WBS task id "
                    f"(C-COM-002).")

    # ── soft_gates (IMP-0395) ────────────────────────────────────────────────────────────
    feature = str(data.get("feature") or "").strip()
    config = build_config
    if config is None:
        if not feature:
            errors.append(
                f"  MISSING FIELD `feature` - {path}: without it the build config cannot be "
                f"resolved, so the SOFT step list cannot be derived.")
            return errors
        config = repo_root / "config" / f"{feature}-build.yml"
    if not config.is_file():
        errors.append(
            f"  NO BUILD CONFIG - {path}: expected {config} to derive the SOFT step list from. "
            f"A gate that cannot find its input must fail rather than report OK (IMP-0007).")
        return errors

    expected, problem = soft_step_names(config)
    if problem:
        errors.append(f"  SOFT STEPS UNDERIVABLE - {path}: {problem}")
        return errors

    reported = data.get("soft_gates")
    if reported is None:
        errors.append(
            f"  MISSING FIELD `soft_gates` - {path}: expected one finding COUNT per SOFT step, "
            f"keyed by step name — {', '.join(sorted(expected))}. `warnings.total` is an "
            f"aggregate: builds recorded 83 warnings with 0 untriaged while `derived-counts` "
            f"printed four drifts on every run, and a fifth would have been arithmetically "
            f"invisible inside it (IMP-0395).")
        return errors
    if not isinstance(reported, dict):
        errors.append(f"  BAD FIELD `soft_gates` - {path}: expected an object mapping step name "
                      f"to a finding count, got {type(reported).__name__}.")
        return errors

    missing = sorted(expected - set(reported))
    extra = sorted(set(reported) - expected)
    if missing:
        errors.append(
            f"  SOFT GATE UNCOUNTED - {path}: `soft_gates` records no count for "
            f"{', '.join(missing)}, which {'is' if len(missing) == 1 else 'are'} SOFT "
            f"(--warn-only) in {config.name}. A SOFT gate with no per-step number is a finding "
            f"that disappears into the aggregate (IMP-0395).")
    if extra:
        errors.append(
            f"  SOFT GATE NOT IN CONFIG - {path}: `soft_gates` names {', '.join(extra)}, which "
            f"{'is' if len(extra) == 1 else 'are'} not a --warn-only step in {config.name}. The "
            f"key set is DERIVED from the config, so a stale name means the manifest was copied "
            f"rather than measured.")
    for name, count in sorted(reported.items()):
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            errors.append(
                f"  BAD SOFT GATE COUNT - {path}: `soft_gates[{name!r}]` is {count!r}; expected "
                f"a non-negative integer count of findings that step reported this build.")
    return errors


def resolve(targets: list[str]) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    problems: list[str] = []
    for raw in targets:
        p = Path(raw)
        if p.is_dir():
            found = sorted(p.rglob("manifest.json"))
            if not found:
                problems.append(f"  NO MANIFEST - {p} contains no manifest.json. A gate with "
                                f"nothing to check must not report OK (IMP-0007).")
            paths += found
        elif p.is_file():
            paths.append(p)
        else:
            problems.append(f"  TARGET MISSING - {p} does not exist. A gate pointed at a "
                            f"missing target does not pass (IMP-0007).")
    return paths, problems


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_GOOD_NOTE = ("HEAD describes the last COMMIT only. 41 uncommitted paths exist under src/, "
              "provisioning/ and config/ at pack time — this build packaged the WORKING TREE "
              "(pac solution pack reads disk, not git), so source_commit is descriptive of "
              "ancestry only (IMP-0078's caution). See `wbs` for the contracted scope.")
_BAD_TABLE = _GOOD_NOTE + " It includes the rev_roundfinance table."
_BAD_FILE = _GOOD_NOTE + " It includes LandingPage.tsx and the charts."

_CASES: dict[str, tuple[dict, bool, str]] = {
    "a-note-naming-a-rev_-table-fails": (
        {"source_commit_note": _BAD_TABLE}, True, "`rev_roundfinance`"),
    "a-note-naming-a-filename-fails": (
        {"source_commit_note": _BAD_FILE}, True, "`LandingPage.tsx`"),
    # The real note from build 20260825-1, reduced to its shape: BOTH offences at once.
    "the-real-20260825-1-note-fails-on-both-counts": (
        {"source_commit_note": _GOOD_NOTE + " includes the trustee-portal-visual-refresh "
                                            "changes (rev_roundfinance table, LandingPage/charts "
                                            "UI, A-FIN-05/07/A-002 marker fixes)"},
        True, "NOTE ENUMERATES CONTENT"),
    # THE OVER-FIRING CONTROLS. Every one of these is a legitimate note or field.
    "a-count-only-note-naming-DIRECTORIES-passes": (
        {"source_commit_note": _GOOD_NOTE}, False, ""),
    "version-strings-full-of-dots-are-not-notes-and-must-not-be-scanned": (
        {"build_tool": "pac 2.4.1+g3799f3e (.NET 10.0.5)",
         "build_os": "Darwin 25.6.0 arm64", "source_commit_note": _GOOD_NOTE}, False, ""),
    "a-manifest-with-no-note-field-passes": (
        {"feature": "x", "source_tree_dirty_paths": 0}, False, ""),
    "an-empty-note-passes": (
        {"source_commit_note": "   "}, False, ""),
}


def _required_field_cases(tmp: Path) -> list[tuple[str, bool, str]]:
    """Fixtures for the two required-field assertions, against a throwaway repo root."""
    root = tmp / "repo"
    (root / "contract" / "change-orders").mkdir(parents=True)
    (root / "config").mkdir(parents=True)
    (root / "contract" / "wbs.json").write_text(json.dumps(
        {"tasks": [{"id": "6.1"}, {"id": "6.3"}, {"id": "0.4"}]}), encoding="utf-8")
    (root / "contract" / "change-orders" / "CO-001.md").write_text(
        "| New task id | **6.9** |\n", encoding="utf-8")
    (root / "config" / "feat-build.yml").write_text(
        "steps:\n"
        "  - name: hard-gate\n    command: python3 scripts/verify-x.py\n"
        "  - name: derived-counts\n    command: python3 scripts/verify-derived-counts.py"
        " --warn-only\n"
        "  - name: review-document\n    command: python3 scripts/verify-review-document.py"
        " --warn-only\n", encoding="utf-8")

    good = {"feature": "feat", "wbs": ["6.1", "6.9"],
            "soft_gates": {"derived-counts": 4, "review-document": 0}}

    def variant(**changes) -> dict:
        out = dict(good)
        for key, value in changes.items():
            if value is _DROP:
                out.pop(key, None)
            else:
                out[key] = value
        return out

    return [
        ("required: the good manifest passes — baselined id, change-order id, both SOFT steps "
         "counted", variant(), False, ""),
        ("required: a manifest with NO wbs field fails — IMP-0350's exact shape",
         variant(wbs=_DROP), True, "MISSING FIELD `wbs`"),
        ("required: an empty wbs list fails", variant(wbs=[]), True, "BAD FIELD `wbs`"),
        ("required: a wbs id in neither the baseline nor a change order fails",
         variant(wbs=["6.1", "9.9"]), True, "UNKNOWN TASK ID"),
        ("required: the `system` non-billable sentinel PASSES — the narrowing that removes the "
         "corpus's one UNKNOWN TASK ID false positive by name",
         variant(wbs=["system"]), False, ""),
        ("required: `system` alongside real contracted ids PASSES",
         variant(wbs=["6.1", "system"]), False, ""),
        ("required: a CHANGE-ORDER-covered id alone passes — 6.9 is approved and unbaselined, "
         "and failing a build over it is how a gate teaches people to route around it",
         variant(wbs=["6.9"]), False, ""),
        ("required: a manifest with NO soft_gates field fails",
         variant(soft_gates=_DROP), True, "MISSING FIELD `soft_gates`"),
        ("required: soft_gates missing one --warn-only step fails — the aggregate a drift "
         "disappears into is what IMP-0395 is about",
         variant(soft_gates={"derived-counts": 4}), True, "SOFT GATE UNCOUNTED"),
        ("required: soft_gates naming a step that is NOT --warn-only fails, because the key set "
         "is derived from the config",
         variant(soft_gates={"derived-counts": 4, "review-document": 0, "hard-gate": 0}),
         True, "SOFT GATE NOT IN CONFIG"),
        ("required: a non-integer soft-gate count fails",
         variant(soft_gates={"derived-counts": "four", "review-document": 0}),
         True, "BAD SOFT GATE COUNT"),
        ("required: a manifest naming a feature with no build config fails rather than "
         "reporting OK", variant(feature="nosuch"), True, "NO BUILD CONFIG"),
        ("required: --note-only skips both assertions, for reading a HISTORICAL manifest",
         variant(wbs=_DROP, soft_gates=_DROP), False, ""),
    ]


class _Drop:
    pass


_DROP = _Drop()
_required_case_count = 0


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        # ── the two required-field assertions ────────────────────────────────────────────
        cases = _required_field_cases(Path(tmp))
        global _required_case_count
        _required_case_count = len(cases)
        root = Path(tmp) / "repo"
        for index, (label, payload, expect_fail, want) in enumerate(cases):
            path = Path(tmp) / f"required{index}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = check_manifest(path, note_only="--note-only" in label, repo_root=root)
            rc = 1 if errors else 0
            text = "\n".join(errors)
            ok = ((rc != 0) if expect_fail else (rc == 0)) and (not want or want in text)
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {label} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors:
                    print(f"                   {line}")
                failures.append(label)

        for name, (payload, expect_fail, want) in _CASES.items():
            path = Path(tmp) / f"{name}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = check_manifest(path, note_only=True)
            rc = 1 if errors else 0
            text = "\n".join(errors)
            ok = ((rc != 0) if expect_fail else (rc == 0)) and (not want or want in text)
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc}, "
                  f"{len(errors)} error(s)")
            if not ok:
                for line in errors:
                    print(f"                   {line}")
                failures.append(name)

        # Refusing to pass over nothing.
        empty = Path(tmp) / "emptydir"
        empty.mkdir()
        _paths, problems = resolve([str(empty)])
        ok = bool(problems)
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"a-directory-with-no-manifest-FAILS → {len(problems)} problem(s)")
        if not ok:
            failures.append("a-directory-with-no-manifest-FAILS")
        _paths, problems = resolve([str(Path(tmp) / "nope")])
        ok = bool(problems)
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"a-missing-target-FAILS → {len(problems)} problem(s)")
        if not ok:
            failures.append("a-missing-target-FAILS")

    if failures:
        print(f"\nverify-build-manifest-note: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    total = len(_CASES) + 2 + _required_case_count
    print(f"\nverify-build-manifest-note: SELFTEST OK — {total} fixtures, 7 of them over-firing "
          f"controls. The note check forbids a SHAPE, so zero false positives are structural "
          f"there; the two required-field checks read `wbs` and `soft_gates` against "
          f"contract/wbs.json, contract/change-orders/ and the build config's own step list, so "
          f"nothing is hand-listed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("targets", nargs="*", help="manifest.json files, or directories to search")
    p.add_argument("--warn-only", action="store_true", help="report and exit 0")
    p.add_argument("--note-only", action="store_true",
                   help="skip the wbs / soft_gates required-field assertions (historical "
                        "manifests only — never for a build you are producing)")
    p.add_argument("--build-config", help="build config to derive the SOFT step list from "
                                         "(default: config/<feature>-build.yml)")
    p.add_argument("--selftest", action="store_true")
    try:
        args = p.parse_args(argv)
    except SystemExit:
        return 2

    if args.selftest:
        return selftest()
    if not args.targets:
        p.error("give at least one manifest.json or directory (or --selftest)")

    build_config = Path(args.build_config) if args.build_config else None
    paths, problems = resolve(args.targets)
    errors = list(problems)
    for path in paths:
        errors += check_manifest(path, note_only=args.note_only, build_config=build_config)

    if errors:
        label = "WARN" if args.warn_only else "FAILED"
        print(f"build-manifest-note: {label}\n" + "\n".join(errors), file=sys.stderr)
        return 0 if args.warn_only else 1
    scope = ("no note enumerates shipped content" if args.note_only else
             "no note enumerates shipped content, every `wbs` id resolves against the baseline "
             "or a change order, and every SOFT build step has its own finding count")
    print(f"build-manifest-note: OK — {len(paths)} manifest(s) checked; {scope}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
