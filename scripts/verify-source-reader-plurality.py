#!/usr/bin/env python3
"""Verify every reader of the solution's repeatable, name-keyed source survives a SECOND
instance of whatever it reads.

WHY THIS EXISTS. On 2026-08-23 one dispatch added four tables and a second field-security
profile, and SIX separate readers of solution source broke the same afternoon — two of them
guarding the trustee privacy control itself, which reported a false privacy breach against
entirely legitimate code. Every one had been correct while the source held exactly one of the
thing it read. The findings: IMP-0234, IMP-0236, IMP-0237, IMP-0238, IMP-0239, IMP-0240.

Each was fixed individually, in one afternoon, by the sessions that hit them. Six instance
patches for one property is exactly what skills/how-to-promote-a-finding.md's altitude rule
forbids, so this gate is the generalisation. The rule it enforces is C-TECH-069.

THE PROPERTY, STATED WITHOUT REFERENCE TO ANY OF THE SIX. A reader of solution source makes
two assumptions that hold silently while the source is small:

  CARDINALITY — "there is one of these." Adding a second <FieldSecurityProfile> made
      PowerShell's XML adapter return an array where a scalar was expected; every downstream
      property access returned nothing, with NO error, and the provisioning script would have
      issued zero of sixty-nine field-permission calls against a live environment.

  IDENTITY — "this name identifies one column." This solution reuses column names across
      tables by convention and the sensitivity differs per table: rev_name is the pseudonymous
      case reference on rev_application and a Finance-only column on rev_bankaccount. A
      reader that collects attribute names and then matches by name cannot tell the two apart.
      See knowledge/domain/data-entities.md for the domain statement of this.

THE THREE CHECKS, AND WHY EACH IS MECHANICAL RATHER THAN A JUDGEMENT.

  R1  PowerShell cardinality. A property-chain read of a repeatable element
      ($xml.FieldSecurityProfiles.FieldSecurityProfile) must be wrapped in @(...). This is the
      exact IMP-0238 defect, and @(...) is the exact fix IMP-0239 applied. The signal is
      unambiguous: with @(...) the code is correct for one instance and for ten; without it,
      it is correct only for one.

  R2  Python cardinality. A repeatable element must be read with .iter()/.findall(), never
      .find()/findtext() — find returns the FIRST match and silently ignores the rest. Same
      property, different language, and equally crisp.

  R3  Identity. A reader that collects attribute names from source must also read the owning
      entity's name somewhere in the same file. A file that reads <AttributeName> and never
      <EntityName> is building a name-keyed set with no way to resolve which table a hit
      belongs to — the IMP-0236/IMP-0240 defect, in both gates that had it.

The reader list is DERIVED, never declared: every file under the scanned roots that mentions
one of the source artefacts is a reader. That is deliberate and it is the lesson of the review
before this one — a general rule with a hand-written list of subjects is still an instance fix,
and a list that has gone stale once will go stale again. Add a reader and it is covered the
same day, with no edit here.

EXEMPTIONS are explicit, in-file and must give a reason: a line containing

    plurality-exempt: <reason>

within the flagged construct's file suppresses that file's findings for the rule named in the
same comment (or all rules when no rule is named). An exemption with no reason does not count —
that is how a gate becomes a formality.

Run:
    python3 scripts/verify-source-reader-plurality.py
    python3 scripts/verify-source-reader-plurality.py --selftest

Exits 0 when every reader is plurality-safe or exempt with a reason, 1 otherwise. Wired into
config/<slug>-build.yml as the `source-reader-plurality` step.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

# The source artefacts whose instance COUNT can legitimately grow. Mentioning one of these
# makes a file a reader; nothing else does.
SOURCE_ARTEFACTS = (
    "FieldSecurityProfiles.xml",
    "Entity.xml",
    "OptionSets",
    "Roles",
)

# Elements the solution schema allows to repeat. R1/R2 apply to these names only, so a scalar
# read of a genuinely singular element (Solution.xml's <SolutionManifest>) is not flagged.
REPEATABLE_ELEMENTS = (
    "FieldSecurityProfile",
    "FieldPermission",
    "Role",
    "RolePrivilege",
    "OptionSet",
    "Entity",
    "attribute",
    "RootComponent",
)

# Where readers live. Scanned recursively.
SCAN_ROOTS = ("scripts", "provisioning", "src/tests")

SKIP_DIRS = {"node_modules", ".git", "__pycache__", "dist", "coverage", ".vite"}

# The reason must be on the SAME LINE as the marker. `\s*` here would match the newline and
# then read the NEXT line of code as the reason, so `plurality-exempt:` with nothing after it
# would silently count as justified — caught by this gate's own selftest before it shipped.
EXEMPT = re.compile(r"plurality-exempt:[^\S\n]*(?P<rule>R[123])?[^\S\n]*(?P<reason>\S[^\n]*)")


def is_reader(text: str) -> bool:
    return any(artefact in text for artefact in SOURCE_ARTEFACTS)


def exemptions(text: str) -> tuple[set[str], bool]:
    """Return (exempted rule ids, exempt_all). An exemption with no reason does not count."""
    rules: set[str] = set()
    everything = False
    for match in EXEMPT.finditer(text):
        if not match.group("reason").strip():
            continue
        if match.group("rule"):
            rules.add(match.group("rule"))
        else:
            everything = True
    return rules, everything


def strip_powershell_comments(text: str) -> str:
    """Blank out <# block #> and # line comments, preserving line numbering.

    Needed because the clearest description of this defect class in the repository is the
    docstring of the function that was FIXED for it — ensure-schema-helpers.psm1 explains the
    old scalar read in prose, and matching that prose reports the fix as the defect.
    """
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))
    text = re.sub(r"<#.*?#>", blank, text, flags=re.DOTALL)
    return re.sub(r"#[^\n]*", blank, text)


def check_powershell(text: str) -> list[tuple[int, str]]:
    """R1 — a property-chain read of a repeatable element must be @(...)-wrapped.

    SCOPED TO XML NAVIGATION. The defect is specifically PowerShell's XML property adapter
    returning a scalar for one matching child and an array for more than one, so the root of
    the chain must be an XML variable. Without that scope this fired on
    `$result.Body.OptionSet.TrueOption` — a Boolean attribute's genuinely singular OptionSet
    inside an API response payload, which has nothing to do with the adapter.
    """
    code = strip_powershell_comments(text)
    findings: list[tuple[int, str]] = []
    for element in REPEATABLE_ELEMENTS:
        # $<something-xml>.<Plural>.<Element> — the shape that silently becomes an array.
        pattern = re.compile(r"\$[A-Za-z_]*[xX][mM][lL][\w]*(?:\.\w+)*?\.\w+\."
                             + re.escape(element) + r"\b")
        for match in pattern.finditer(code):
            line_no = code.count("\n", 0, match.start()) + 1
            line = code.splitlines()[line_no - 1]
            # @( anywhere on the line is the fix, and so is an explicit foreach over it —
            # both iterate correctly whether the value is a scalar or an array.
            if "@(" in line or re.search(r"\bforeach\b", line, re.IGNORECASE):
                continue
            findings.append((line_no, match.group(0)))
    return findings


def check_python(text: str) -> list[tuple[int, str]]:
    """R2 — a repeatable element must be read with iter/findall, never find/findtext."""
    findings: list[tuple[int, str]] = []
    pattern = re.compile(r"\.(?:find|findtext)\(\s*['\"](?P<el>\w+)['\"]")
    for match in pattern.finditer(text):
        if match.group("el") not in REPEATABLE_ELEMENTS:
            continue
        line_no = text.count("\n", 0, match.start()) + 1
        findings.append((line_no, match.group(0)))
    return findings


def check_identity(text: str) -> list[tuple[int, str]]:
    """R3 — collecting attribute names without ever resolving the owning entity.

    An entity is resolved either by reading its name out of the source alongside the attribute
    (<EntityName>, a LogicalName) or by being GIVEN it — a mandatory -Entity parameter plus an
    Entities/<entity>/Entity.xml path is exactly the fix IMP-0237 applied to
    Get-SecuredColumnNames, and counting it as unscoped would report that fix as the defect.
    """
    reads_attribute = re.search(r"AttributeName|PhysicalName", text)
    if not reads_attribute:
        return []
    entity_resolved = (
        r"EntityName"          # read out of the XML beside the attribute
        r"|entityname"
        r"|LogicalName\b"      # the entity's own logical name
        r"|\$Entity\b"         # given as a parameter …
        r"|-Entity\b"          # … or passed as one
        r"|['\"]Entities['\"]" # … or resolved through the Entities/<entity>/ path
    )
    if re.search(entity_resolved, text):
        return []
    line_no = text.count("\n", 0, reads_attribute.start()) + 1
    return [(line_no, reads_attribute.group(0))]


RULES = (
    ("R1", "a repeatable element read as a scalar — PowerShell returns an ARRAY the moment a "
           "second one exists, and every property access on it then silently yields nothing "
           "(IMP-0238, IMP-0239). Wrap the read in @(...) and iterate",
     (".ps1", ".psm1"), check_powershell),
    ("R2", "a repeatable element read with find/findtext, which returns only the FIRST match "
           "and ignores the rest. Use .iter() or .findall()",
     (".py",), check_python),
    ("R3", "attribute names collected with no owning-entity name read anywhere in the file — a "
           "name-keyed set cannot say which table a hit belongs to, and this solution reuses "
           "column names across tables with different sensitivities (IMP-0236, IMP-0240, "
           "C-TECH-069, knowledge/domain/data-entities.md)",
     (".py", ".ps1", ".psm1"), check_identity),
)


def scan_file(path: str, text: str) -> list[str]:
    ext = os.path.splitext(path)[1]
    exempt_rules, exempt_all = exemptions(text)
    if exempt_all:
        return []
    problems: list[str] = []
    for rule_id, why, extensions, check in RULES:
        if ext not in extensions or rule_id in exempt_rules:
            continue
        for line_no, snippet in check(text):
            problems.append(f"{path}:{line_no}: [{rule_id}] {snippet!r} — {why}.")
    return problems


def readers(roots: tuple[str, ...], base: str = ".") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for root in roots:
        full_root = os.path.join(base, root)
        if not os.path.isdir(full_root):
            continue
        for dirpath, dirnames, filenames in os.walk(full_root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in sorted(filenames):
                if os.path.splitext(filename)[1] not in (".py", ".ps1", ".psm1"):
                    continue
                path = os.path.join(dirpath, filename)
                try:
                    with open(path, encoding="utf-8") as handle:
                        text = handle.read()
                except (OSError, UnicodeDecodeError):
                    continue
                if is_reader(text):
                    found.append((os.path.relpath(path, base), text))
    return found


def selftest() -> int:
    """Six fixtures, one per finding this gate generalises, plus the shapes that must stay quiet."""
    cases: list[tuple[str, str, str, bool]] = [
        ("IMP-0238/0239: scalar read of a repeatable profile element IS flagged",
         "r.psm1",
         "# reads FieldSecurityProfiles.xml\n"
         "$profile = $xml.FieldSecurityProfiles.FieldSecurityProfile\n", True),
        ("the @(...) fix is NOT flagged",
         "r.psm1",
         "# reads FieldSecurityProfiles.xml\n"
         "$profiles = @($xml.FieldSecurityProfiles.FieldSecurityProfile)\n", False),
        ("a foreach over the collection is NOT flagged",
         "r.psm1",
         "# reads FieldSecurityProfiles.xml\n"
         "foreach ($p in $xml.FieldSecurityProfiles.FieldSecurityProfile) { $p.name }\n", False),
        ("IMP-0236/0240: attribute names with no entity qualifier IS flagged",
         "g.py",
         "# reads FieldSecurityProfiles.xml\n"
         "for a in tree.iter('AttributeName'):\n    cols.add(a.text)\n", True),
        ("the entity-qualified version is NOT flagged",
         "g.py",
         "# reads FieldSecurityProfiles.xml\n"
         "for p in tree.iter('FieldPermission'):\n"
         "    pairs.add((p.findtext('EntityName'), p.findtext('AttributeName')))\n", False),
        ("a repeatable element read with find() IS flagged",
         "g.py",
         "# reads Entity.xml\n"
         "el = tree.find('FieldPermission')\n", True),
        ("iter() over the same element is NOT flagged",
         "g.py",
         "# reads Entity.xml\n"
         "for el in tree.iter('FieldPermission'):\n    pass\n", False),
        ("a non-reader is not scanned at all",
         "x.py",
         "el = tree.find('FieldPermission')\n", False),
        ("an exemption WITH a reason suppresses",
         "g.py",
         "# reads FieldSecurityProfiles.xml\n"
         "# plurality-exempt: R3 reports a solution-wide inventory on purpose\n"
         "for a in tree.iter('AttributeName'):\n    cols.add(a.text)\n", False),
        ("an exemption with NO reason does not suppress",
         "g.py",
         "# reads FieldSecurityProfiles.xml\n"
         "# plurality-exempt:\n"
         "for a in tree.iter('AttributeName'):\n    cols.add(a.text)\n", True),
        # ── The three false positives this gate produced against the real tree on the day it
        # was written. Each narrowing is pinned here so it cannot silently come back.
        ("the OLD scalar read, described in a <# docstring #> of the function that FIXED it, "
         "is NOT flagged",
         "r.psm1",
         "<#\n  reads FieldSecurityProfiles.xml. Until 2026-08-23 this did\n"
         "  $xml.FieldSecurityProfiles.FieldSecurityProfile as a single element.\n#>\n"
         "$profiles = @($xml.FieldSecurityProfiles.FieldSecurityProfile)\n", False),
        ("a repeatable-sounding property on a NON-XML object graph is NOT flagged",
         "t.ps1",
         "# reads Entity.xml\n"
         "$result.Body.OptionSet.TrueOption.Label | Should -Be 'Yes'\n", False),
        ("a mandatory -Entity parameter resolves identity, so R3 stays quiet",
         "h.psm1",
         "# reads Entity.xml\n"
         "param([Parameter(Mandatory)][string]$Entity)\n"
         "$node = $x.SelectSingleNode(\"//attribute[@PhysicalName='$a']\")\n", False),
    ]

    failed = 0
    for label, filename, body, should_flag in cases:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, filename)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(body)
            flagged = bool(is_reader(body) and scan_file(filename, body))
        ok = flagged == should_flag
        if not ok:
            failed += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")

    # The trailing "SELFTEST OK — <n> fixtures" is a repository convention, not decoration:
    # verify-constraint-verifiers.py reads this total to check any constraint row that states a
    # fixture count for this gate, so extending the gate cannot leave a constraint describing it
    # stale (IMP-0260). Derived from the case list, never typed.
    if failed:
        print(f"\nSELFTEST: FAILED — {failed} case(s) of {len(cases)} fixtures")
        return 1
    print(f"\nSELFTEST: PASS\nverify-source-reader-plurality: SELFTEST OK — "
          f"{len(cases)} fixtures.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--base", default=".")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    found = readers(SCAN_ROOTS, args.base)
    if not found:
        print("source-reader-plurality: FAILED — no reader of the solution's repeatable source "
              f"was found under {', '.join(SCAN_ROOTS)}. This gate has no subject, which is a "
              "broken gate rather than a clean tree (IMP-0007).", file=sys.stderr)
        return 1

    problems: list[str] = []
    for path, text in found:
        problems.extend(scan_file(path, text))

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        print(f"\nsource-reader-plurality: FAILED — {len(problems)} finding(s) across "
              f"{len(found)} reader(s) of the solution's repeatable source. Each is a reader "
              "that is correct for exactly one instance of what it reads; the seventh instance "
              "of this class is what this gate exists to prevent (C-TECH-069).", file=sys.stderr)
        return 1

    print(f"source-reader-plurality: OK — {len(found)} reader(s) of the solution's repeatable, "
          "name-keyed source are plurality-safe: repeatable elements read as collections, and "
          "attribute names resolved against an owning entity.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
