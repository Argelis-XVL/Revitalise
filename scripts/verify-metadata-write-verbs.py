#!/usr/bin/env python3
"""Assert that no provisioning script writes Dataverse METADATA with the wrong verb or URI shape.

WHY THIS EXISTS. `C-TECH-073`, and three live blockers inside 26 hours.

A Dataverse Web API **metadata** write is `PUT` with the complete current object. Microsoft's own
*Create and update table definitions using the Web API* page is categorical about it:

    "You can't use the PATCH method to update data model entities... you must use the PUT method
     when updating data model entities and be careful to include all the existing properties that
     you don't intend to change. You can't update individual properties."

That rule is invisible in this codebase, because a **data record** write and a **metadata** write
are made by the same helper, one line apart, and take opposite verbs:

    Invoke-DataverseApi -Method PATCH ... -Path 'organizations(<id>)'          # correct
    Invoke-DataverseApi -Method PATCH ... -Path "EntityDefinitions(...)"        # 0x80060888

Both look like "update a thing". One is right forever and one has never worked.

THE THREE INSTANCES.

  * `IMP-0272` (2026-08-24 20:10) — `ensure-schema.ps1` step 3b PATCHed
    `EntityDefinitions(...)/Attributes(...)` for five lookup columns. All five failed live with
    *"The requested resource does not support http method 'PATCH'."*
  * `IMP-0273` — the correction, from Microsoft's own worked example. `IMP-0272` had diagnosed a
    missing derived-type **cast** and proposed `PATCH` + cast, which would have failed a third
    time on the same five columns. The cast belongs on the preparatory `GET`; the write goes to
    the **uncast** URI.
  * `IMP-0276` (2026-08-24 22:03) — `ensure-auditing.ps1` PATCHed `EntityDefinitions(...)` itself
    to set `IsAuditEnabled` on four new finance tables. All four failed live with `0x80060888`.
    The same rule, one endpoint out, three hours later.

WHY A GATE AND NOT A KNOWLEDGE LINE. Improvement review 24 wrote the rule into
`knowledge/technology/testing-tools.md` scoped to *column* metadata, because a column write was
what had failed. Table metadata failed next, the same day. That is the altitude rule
(`skills/how-to-promote-a-finding.md` §2) biting a knowledge file: a second instance of a class
may not get another instance patch. This gate is the class-level form — it reads the ENDPOINT
FAMILY, so `GlobalOptionSetDefinitions` and `RelationshipDefinitions` are covered before anyone
writes against them for the first time.

WHY THE SIX PRE-EXISTING TABLES ARE THE POINT. `ensure-auditing.ps1` had reported `EXISTS` for
every one of its six original tables on every prior run — because `IsAuditEnabled` was already
true and the script's idempotency guard skipped the write. Not one of those six "successes" ever
executed the write path. A green run of an idempotent script is evidence about CONVERGENCE and
never about the write being correct (`C-TECH-042`).

WHAT IT CHECKS.

  FAIL  a `PATCH` (or `MERGE`) whose target resolves to a metadata entity set.
  FAIL  a metadata `PUT`/`PATCH` whose URI carries a derived-type cast segment
        (`/Microsoft.Dynamics.CRM.<Type>`). The cast disambiguates a polymorphic READ; on the
        write it is the shape `IMP-0272` proposed and `IMP-0273` disproved.
  WARN  a metadata `PUT` in a file that never sets the `MSCRM.MergeLabels` header. Without it
        Dataverse REPLACES the localised label collections of the object being written rather
        than merging them, so a full-object PUT assembled from a `GET` in one language is a
        destructive write against every other language installed.

WHAT IT CANNOT SEE — the residual, stated because a gate without one is a false sense of one.

  * **Whether a `PUT` body is the COMPLETE object.** That is the other half of the platform rule
    and it is not statically decidable here: the body is assembled by mutating a fetched object
    across several statements, so the gate reads the verb and the URI and stops there.
  * A URI built from a lookup table, spliced across more than one variable hop, or assembled by a
    helper is not resolved. Resolution follows ONE level of `$variable` assignment backwards
    within the same file.
  * The `MSCRM.MergeLabels` check is FILE-scoped, not call-scoped: a file with two PUTs and one
    header set is silent about the second.

Run:
    python3 scripts/verify-metadata-write-verbs.py
    python3 scripts/verify-metadata-write-verbs.py --selftest

Exits 0 when clean, 1 on any failure, 2 on a usage error. Fails — never passes — when it finds
ZERO scripts or ZERO API calls to inspect, because a checker that checks nothing must not report
PASS (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCAN_ROOTS = ("provisioning",)
SCRIPT_GLOBS = ("*.ps1", "*.psm1")

# The Dataverse Web API metadata entity sets. Anchored to this list rather than to a pattern:
# `organizations`, `fieldpermissions`, `rev_settings` and every other DATA collection take
# ordinary PATCH semantics, and a rule loose enough to catch metadata by shape would report a
# defect on all of them. Extend this tuple when the platform grows a new metadata collection.
METADATA_SETS = (
    "EntityDefinitions",
    "GlobalOptionSetDefinitions",
    "RelationshipDefinitions",
    "EntityKeyDefinitions",
    "ManyToManyRelationshipMetadata",
    "OneToManyRelationshipMetadata",
)

# `Attributes(...)` and `Attributes` only ever appear nested under EntityDefinitions, but a
# resolved URI fragment may carry only the tail. Matched separately so a bare Attributes segment
# is still recognised.
METADATA_SEGMENT = re.compile(
    r"(?:" + "|".join(METADATA_SETS) + r")\b|(?<![A-Za-z])Attributes\s*[(/]")

# A derived-type cast: `/Microsoft.Dynamics.CRM.LookupAttributeMetadata`.
CAST_SEGMENT = re.compile(r"/\s*Microsoft\.Dynamics\.CRM\.[A-Za-z]+")

MERGE_LABELS = re.compile(r"MSCRM\.MergeLabels", re.IGNORECASE)

# The two ways this repository reaches the Web API.
CALL_VERBS = re.compile(
    r"\b(?:Invoke-DataverseApi|Invoke-RestMethod|Invoke-WebRequest)\b", re.IGNORECASE)

METHOD_ARG = re.compile(r"-Method\s+['\"]?([A-Za-z]+)['\"]?", re.IGNORECASE)

# `-Path <value>` (the shared helper) or `-Uri <value>` (Invoke-RestMethod directly).
TARGET_ARG = re.compile(r"-(?:Path|Uri)\s+(.+?)(?=\s+-[A-Za-z]|\s*\|\s|$)", re.IGNORECASE)

# `$name = <rhs>` — one hop of backwards resolution.
ASSIGNMENT = re.compile(r"^\s*(\$[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$")
BARE_VARIABLE = re.compile(r"^\(?\s*(\$[A-Za-z_][A-Za-z0-9_]*)\s*\)?$")

WRITE_VERBS = {"PATCH", "MERGE", "PUT", "POST"}
UPDATE_VERBS = {"PATCH", "MERGE", "PUT"}


def logical_lines(text: str) -> list[tuple[int, str]]:
    """Join PowerShell backtick line-continuations into one logical line.

    THIS FUNCTION IS THE GATE. The first draft of this script matched `-Path` on the physical
    line that carried `-Method`, and every real call in this repository is written as

        Invoke-DataverseApi -Method PATCH -EnvironmentUrl $envUrl -AccessToken $token `
            -Path ('EntityDefinitions(...)' -f $logicalName) -Body $body

    so the target was on the NEXT line and invisible. The draft passed the pre-fix tree — green
    over the exact defect it exists to catch — and was caught only by running it against the
    committed tree at HEAD rather than trusting its own fixtures. Returns (1-based line number of
    the FIRST physical line, joined text).
    """
    out: list[tuple[int, str]] = []
    buffer = ""
    start = 0
    for number, raw in enumerate(text.splitlines(), 1):
        stripped = raw.rstrip()
        if not buffer:
            start = number
        # A trailing backtick continues the statement onto the next physical line. A backtick
        # inside a string ("`n") never sits at end-of-line, so end-anchoring is enough.
        if stripped.endswith("`"):
            buffer += stripped[:-1] + " "
            continue
        buffer += stripped
        out.append((start, buffer))
        buffer = ""
    if buffer:
        out.append((start, buffer))
    return out


def strip_comment(line: str) -> str:
    """Drop a trailing `#` comment, ignoring `#` inside a quoted string."""
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#":
            return line[:i]
    return line


def resolve_target(raw: str, index: int, lines: list[tuple[int, str]]) -> str:
    """The text of a call's `-Path`/`-Uri` argument, following one `$variable` hop backwards."""
    raw = raw.strip().rstrip("|").strip()
    bare = BARE_VARIABLE.match(raw)
    if not bare:
        return raw
    name = bare.group(1)
    for _number, earlier in reversed(lines[:index]):
        assign = ASSIGNMENT.match(strip_comment(earlier))
        if assign and assign.group(1).lower() == name.lower():
            return assign.group(2).strip()
    return raw


class Finding(str):
    """A failure message. Subclassed only so the selftest can assert on kind via a prefix."""


def scan_file(path: Path, rel: str) -> tuple[list[str], list[str], int]:
    """Return (failures, warnings, calls_inspected) for one script."""
    failures: list[str] = []
    warnings: list[str] = []
    calls = 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{rel}: could not be read ({exc})"], [], 0

    file_sets_merge_labels = bool(MERGE_LABELS.search(text))
    lines = logical_lines(text)

    for index, (number, joined) in enumerate(lines):
        line = strip_comment(joined)
        if not CALL_VERBS.search(line):
            continue
        method = METHOD_ARG.search(line)
        if not method:
            continue
        verb = method.group(1).upper()
        if verb not in WRITE_VERBS:
            calls += 1
            continue
        target_match = TARGET_ARG.search(line)
        if not target_match:
            calls += 1
            continue
        calls += 1
        target = resolve_target(target_match.group(1), index, lines)
        if not METADATA_SEGMENT.search(target):
            continue

        if verb in {"PATCH", "MERGE"}:
            failures.append(
                f"{rel}:{number}: {verb} against a Dataverse METADATA endpoint "
                f"({target.strip()[:90]}). Metadata writes are PUT-only with the COMPLETE "
                f"current object — Microsoft's own words are \"You can't update individual "
                f"properties.\" This exact call shape failed live three times on 2026-08-24 "
                f"(IMP-0272 on Attributes, IMP-0276 on EntityDefinitions). Fix: GET the full "
                f"object with no $select, strip every '@odata.*' response annotation, mutate the "
                f"one property, then PUT the whole object back to the same UNCAST URI with "
                f"MSCRM.MergeLabels: true. C-TECH-073.")
            continue

        if verb in UPDATE_VERBS and CAST_SEGMENT.search(target):
            failures.append(
                f"{rel}:{number}: {verb} to a metadata URI carrying a derived-type cast "
                f"({CAST_SEGMENT.search(target).group(0).strip()}). The cast disambiguates the "
                f"preparatory GET on a polymorphic collection; it does NOT carry over to the "
                f"write, which goes to the uncast URI. This is the shape IMP-0272 proposed and "
                f"IMP-0273 disproved against Microsoft's worked example. C-TECH-073.")
            continue

        if verb == "PUT" and not file_sets_merge_labels:
            warnings.append(
                f"{rel}:{number}: metadata PUT in a file that never sets the "
                f"'MSCRM.MergeLabels' header. Without it Dataverse REPLACES the object's "
                f"localised label collections rather than merging them, so a full-object PUT "
                f"assembled from a single-language GET is a destructive write against every "
                f"other language installed. Add it to the request headers.")

    return failures, warnings, calls


def scan(repo_root: Path) -> tuple[list[str], list[str], int, int]:
    """Return (failures, warnings, files_scanned, calls_inspected)."""
    failures: list[str] = []
    warnings: list[str] = []
    files = 0
    calls = 0

    paths: list[Path] = []
    for root in SCAN_ROOTS:
        base = repo_root / root
        if not base.is_dir():
            continue
        for pattern in SCRIPT_GLOBS:
            paths.extend(sorted(base.rglob(pattern)))

    for path in sorted(set(paths)):
        files += 1
        rel = str(path.relative_to(repo_root))
        file_failures, file_warnings, file_calls = scan_file(path, rel)
        failures.extend(file_failures)
        warnings.extend(file_warnings)
        calls += file_calls

    return failures, warnings, files, calls


# ── Fixtures ───────────────────────────────────────────────────────────────────────────────
# Every shape below is drawn from a real call in this repository or from a real defect. The
# continuation fixtures are the important ones: they are what the first draft got wrong.
_CASES: list[tuple[str, str, int, int]] = [
    # (name, script body, expected failures, expected warnings)
    ("data-record-PATCH-is-correct",
     "Invoke-DataverseApi -Method PATCH -EnvironmentUrl $u -AccessToken $t "
     "-Path ('organizations({0})' -f $id) -Body $b\n", 0, 0),

    ("metadata-PATCH-on-one-line-is-caught",
     "Invoke-DataverseApi -Method PATCH -EnvironmentUrl $u -AccessToken $t "
     "-Path \"EntityDefinitions(LogicalName='rev_grant')\" -Body $b\n", 1, 0),

    # THE DRAFT'S OWN DEFECT. Identical to the line above, split with a backtick exactly as
    # every real call in provisioning/ is written. The first draft reported 0 here.
    ("metadata-PATCH-across-a-backtick-continuation-is-caught",
     "Invoke-DataverseApi -Method PATCH -EnvironmentUrl $u -AccessToken $t `\n"
     "    -Path ('EntityDefinitions(LogicalName=''{0}'')' -f $n) -Body $b | Out-Null\n", 1, 0),

    ("metadata-PATCH-on-the-Attributes-collection-is-caught",
     "Invoke-RestMethod -Method PATCH -Headers $h -Body $b "
     "-Uri \"$base/EntityDefinitions(LogicalName='x')/Attributes(LogicalName='y')\"\n", 1, 0),

    # THE RESIDUAL, PINNED. A target the gate cannot resolve to a literal — assigned in another
    # file, passed as a parameter, or built across more than one hop — is NOT reported. That is a
    # deliberate silence, not a catch, and it is fixtured so nobody later reads the gate's PASS
    # as coverage it does not have.
    ("an-unresolvable-variable-target-is-a-known-residual",
     "Invoke-RestMethod -Method PATCH -Uri $uriFromSomewhereElse -Headers $h -Body $b\n", 0, 0),

    ("metadata-PATCH-through-a-resolved-variable-is-caught",
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''x'')/Attributes"
     "(LogicalName=''y'')' -f $envUrl\n"
     "Invoke-RestMethod -Method PATCH -Uri $uri -Headers $h -Body $b\n", 1, 0),

    ("the-corrected-full-object-PUT-passes",
     "$metadataHeaders = @{ 'MSCRM.MergeLabels' = 'true' }\n"
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''{1}'')' -f $envUrl, $n\n"
     "Invoke-RestMethod -Method PUT -Uri $uri -Headers $metadataHeaders `\n"
     "    -ContentType 'application/json' -Body $body | Out-Null\n", 0, 0),

    ("a-cast-on-the-write-URI-is-caught",
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''x'')/Attributes"
     "(LogicalName=''y'')/Microsoft.Dynamics.CRM.LookupAttributeMetadata' -f $envUrl\n"
     "$h = @{ 'MSCRM.MergeLabels' = 'true' }\n"
     "Invoke-RestMethod -Method PUT -Uri $uri -Headers $h -Body $b\n", 1, 0),

    # The cast is CORRECT here: this is the preparatory read.
    ("a-cast-on-the-preparatory-GET-is-correct",
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''x'')/Attributes"
     "(LogicalName=''y'')/Microsoft.Dynamics.CRM.LookupAttributeMetadata' -f $envUrl\n"
     "Invoke-RestMethod -Method GET -Uri $uri -Headers $h\n", 0, 0),

    ("a-metadata-PUT-with-no-MergeLabels-header-warns",
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''x'')' -f $envUrl\n"
     "Invoke-RestMethod -Method PUT -Uri $uri -Headers $h -Body $b\n", 0, 1),

    ("a-commented-out-metadata-PATCH-is-not-a-defect",
     "# Invoke-DataverseApi -Method PATCH -Path \"EntityDefinitions(LogicalName='x')\" "
     "-Body $b\n", 0, 0),

    ("creating-an-attribute-by-POST-to-the-uncast-collection-passes",
     "$uri = '{0}/api/data/v9.2/EntityDefinitions(LogicalName=''x'')/Attributes' -f $envUrl\n"
     "$h = @{ 'MSCRM.MergeLabels' = 'true' }\n"
     "Invoke-RestMethod -Method POST -Uri $uri -Headers $h -Body $b\n", 0, 0),
]


def selftest() -> int:
    import tempfile

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, body, want_failures, want_warnings in _CASES:
            root = Path(tmp) / name
            (root / "provisioning" / "dataverse").mkdir(parents=True)
            (root / "provisioning" / "dataverse" / "fixture.ps1").write_text(
                body, encoding="utf-8")
            failures, warnings, files, calls = scan(root)
            ok = len(failures) == want_failures and len(warnings) == want_warnings
            print(f"  {'ok  ' if ok else 'FAIL'}  {name}: {len(failures)} failure(s) "
                  f"(want {want_failures}), {len(warnings)} warning(s) "
                  f"(want {want_warnings}), {calls} call(s) in {files} file(s)")
            if not ok:
                failed += 1
                for message in failures + warnings:
                    print(f"          {message[:150]}")

    # The IMP-0007 control: a tree with no scripts must yield zero calls, and main() must then
    # FAIL rather than report PASS over nothing.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "provisioning").mkdir(parents=True)
        _f, _w, files, calls = scan(root)
        ok = calls == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  an empty provisioning tree yields 0 calls "
              f"(caller must fail, not pass): files={files} calls={calls}")
        if not ok:
            failed += 1

    total = len(_CASES) + 1
    if failed:
        print(f"\nSELFTEST: FAILED — {failed} case(s) of {total} fixtures", file=sys.stderr)
        return 1
    print(f"\nSELFTEST: PASS\n"
          f"verify-metadata-write-verbs: SELFTEST OK — {total} fixtures.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assert no provisioning script writes Dataverse metadata with PATCH, or "
                    "with a derived-type cast on the write URI (C-TECH-073).")
    parser.add_argument("--selftest", action="store_true",
                        help="run the scanner against known-good and known-bad fixtures")
    parser.add_argument("--repo-root", default=None,
                        help="repository root (default: this script's parent directory)")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]

    failures, warnings, files, calls = scan(repo_root)

    if calls == 0:
        print("ERROR: inspected ZERO Dataverse API calls across "
              f"{files} provisioning script(s). Either this repository no longer reaches the "
              "Web API from provisioning/ — in which case this gate is obsolete and should be "
              "retired rather than left reporting PASS — or CALL_VERBS/METHOD_ARG stopped "
              "matching. A checker that checks nothing must fail (IMP-0007).", file=sys.stderr)
        return 1

    for message in warnings:
        print(f"WARNING: {message}", file=sys.stderr)

    if failures:
        for message in failures:
            print(f"ERROR: {message}", file=sys.stderr)
        print(f"\nMETADATA WRITE VERBS: FAILED — {len(failures)} invalid metadata write(s) of "
              f"{calls} Dataverse API call(s) inspected across {files} provisioning script(s).",
              file=sys.stderr)
        return 1

    print(f"METADATA WRITE VERBS: PASS — {calls} Dataverse API call(s) across {files} "
          f"provisioning script(s); every metadata write is a PUT to an uncast URI"
          + (f", {len(warnings)} warning(s)" if warnings else "") + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main())
