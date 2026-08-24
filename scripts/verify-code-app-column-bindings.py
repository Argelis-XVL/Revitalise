#!/usr/bin/env python3
"""Verify a Code App references no column-secured (Tier 4) attribute, and does implement the
fail-closed trustee visibility gate.

WHY THIS EXISTS. The trustee portal's entire reason for existing is that trustees review cases
WITHOUT seeing who the applicant is (FR-036, NFR-003, ADR-002). That control is enforced at
runtime by Dataverse column security: the `REV Trustee` role is deliberately NOT a member of
the `REV_TrusteeRestricted` profile, so the ~39 secured columns come back empty for a trustee
no matter what the app asks for.

Runtime enforcement is the real control and this gate does not replace it. But an app that
ASKS for `rev_narrativeraw` is still a defect, for three reasons:

  1. It is one configuration change away from being a live Article 9 disclosure. The single
     change that would do it — adding the trustee team to the profile's membership — is
     guarded by `no-trustee-in-column-security-profile`, and defence in depth means not
     relying on one gate.
  2. The same app code runs for the PROCESS OWNER, who IS a member of the profile
     (TAD §6.1 gives Emily read access to the trustee portal). For her the column is
     populated. A "trustee-only" query that leaks under a different role is not trustee-only.
  3. A `$select` naming a secured column is how a developer signals intent, and the intent
     here must be unambiguous for the next reader.

WHAT IT CHECKS, AND WHY IT DERIVES RATHER THAN TRANSCRIBES. The obvious gate is
`grep -r rev_narrativeraw src/code-apps/`. That checks ONE column of thirty-nine, and it stops
being true the moment a fortieth is secured. So the forbidden set is read from the solution's
own `FieldSecurityProfiles.xml` at check time — every `<AttributeName>` under a
`<FieldPermission>` is a column the platform is hiding from someone, and none of them belongs
in this app. Add a column to the profile and this gate covers it the same day, with no edit
here (C-TECH-060's rule: read the limit from the schema, never transcribe it).

It then asserts the app actually implements the visibility rule, because "references no
secured column" is trivially satisfied by an app that queries nothing at all. TAD §5.5 makes
trustee visibility a CONJUNCTION that fails closed:

    rev_eligibleforround = true  AND  rev_redactionreleased = true

so all three of `rev_narrativeredacted`, `rev_redactionreleased` and `rev_eligibleforround`
must appear in the app source. That is a presence check, not a proof of correct logic — the
Vitest suite carries that — but it distinguishes "implemented" from "absent", which is the
distinction this project keeps getting wrong (IMP-0007, IMP-0035: a gate whose subject is
missing must FAIL, never pass).

Run:
    python3 scripts/verify-code-app-column-bindings.py \\
        src/code-apps/trustee-review-portal \\
        src/solutions/RevitaliseGrantAutomation/Other/FieldSecurityProfiles.xml

Exits 0 when the app references no secured column and implements the conjunction, 1 otherwise.
Wired into config/<slug>-build.yml as the `no-secured-columns-in-code-app` step.

HOW THE FORBIDDEN SET IS SCOPED, AND WHY IT IS NOT A NAME UNION (rewritten 2026-08-23,
improvement review 19 — IMP-0234, IMP-0236, IMP-0237, IMP-0240; rule C-TECH-069).

This solution reuses column names across tables BY CONVENTION, and the same name carries a
different sensitivity per table. `rev_name` is the pseudonymous case reference on
rev_application — precisely what a trustee is meant to see — and a Finance-only column on
rev_bankaccount and rev_payment. `rev_applicantid`, `rev_providerid` and `rev_grantid` repeat
the pattern. So a set of "secured column names", collected across the whole solution and then
matched by name, is wrong in both directions: it flags the trustee's own safe reference as a
breach, and it never tells you which table a hit belongs to.

This gate used to build exactly that union, and on 2026-08-23 a second profile (REV_FinanceOnly,
TAD §6.1) secured `rev_name` for the first time anywhere. Every legitimate
`rev_application.rev_name` reference in the app became a HARD failure of the privacy control
they are not part of. The first fix was a caller-supplied `--exclude-profile REV_FinanceOnly`
in build.yml. That worked and has been REMOVED, because it is a deny-list a human has to
maintain: the day a third profile lands, the default is the same false positive, and nothing
reminds anyone to decide. Review 18 had recorded the general form of that mistake — a rule
centralised while its subject list stays hand-written — hours before it was made again here.

What replaces it derives everything:

  1. THE APP'S OWN TABLES. Every entity under <solution>/Entities/ whose logical name appears
     in the app's AUTHORED source. For the trustee portal that is rev_applicant,
     rev_application, rev_provider, rev_review, rev_setting — and notably NOT rev_bankaccount
     or rev_payment, which the app has no data source for and no role access to.
  2. THE SAFE NAMES. Every column of those tables that is NOT secured on them. This is what
     rescues `rev_application.rev_name`: it is a real, unsecured column of a table the app
     genuinely queries.
  3. FORBIDDEN = every secured (entity, column) pair in the file, minus the safe names.

Coverage does not fall, and that mattered more than fixing the false positive. Point 3 keeps
every secured column of a table the app does NOT query — rev_grant's twelve, and the finance
columns whose names appear nowhere as a safe column — as a HARD failure, because an app naming
`rev_sortcode` has no innocent reading. Only names that are demonstrably safe columns of the
app's own tables are dropped, and if a future rev_application.rev_amount is ever added and
secured, point 2 stops rescuing it the same day, with no edit here.

The residual, stated because it is real: a column secured ONLY on a table the app does not
query, whose name is ALSO a safe column of a table it does, is not reported. `rev_name` is
exactly that case and is exactly what this gate must not report. If such a column ever needs
watching, the table is the thing to check, not the name — see knowledge/domain/data-entities.md.

Generated output is excluded from the forbidden-column scan and only from it: `src/generated/`
and `.power/` are produced verbatim by `pac code add-data-source` and describe the whole
connector surface, so a secured column name appearing there is Microsoft's text, not ours. The
REQUIRED-column checks deliberately still ignore those paths, so a required name found only in
generator output does not count as the app implementing anything.
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

# Extensions worth scanning. Anything a developer writes that could name a column.
SOURCE_EXT = {".ts", ".tsx", ".js", ".jsx", ".json", ".html", ".css", ".md"}

# Paths that are verbatim generator output, not authored source. Excluded from the FORBIDDEN
# scan only — see the module docstring.
GENERATED_DIRS = ("src/generated", ".power")

# Never scan dependency or build output.
SKIP_DIRS = {"node_modules", "dist", ".git", "coverage", ".vite"}

# The conjunction from TAD §5.5 plus FR-038's round scoping. All three must be present in
# AUTHORED source for the app to be implementing the control at all.
REQUIRED_COLUMNS = (
    ("rev_narrativeredacted", "the only narrative a trustee may ever read (FR-026, FR-035)"),
    ("rev_redactionreleased", "the human-in-the-loop release gate; visibility requires it "
                              "true, so its absence means the app cannot fail closed "
                              "(FR-029, FR-030, TAD §5.5)"),
    ("rev_eligibleforround", "scopes a trustee to the current round; without it every "
                             "readable application is shown (FR-038)"),
)


def secured_pairs(profile_path: str) -> tuple[set[tuple[str, str]], list[str]]:
    """Every (entity, column) pair any FieldPermission secures, across EVERY profile.

    Pairs, not names: a name alone cannot say which table it belongs to, and in this solution
    the same name is safe on one table and restricted on another (C-TECH-069). No profile is
    excluded — relevance is decided by the app's own tables in app_entities(), not by the
    caller naming profiles to skip.
    """
    tree = ET.parse(profile_path)
    pairs: set[tuple[str, str]] = set()
    profiles: list[str] = []
    for profile in tree.getroot().iter("FieldSecurityProfile"):
        profiles.append(profile.get("name", "<unnamed>"))
        for permission in profile.iter("FieldPermission"):
            entity = (permission.findtext("EntityName") or "").strip()
            column = (permission.findtext("AttributeName") or "").strip()
            if entity and column:
                pairs.add((entity, column))
    return pairs, profiles


def solution_entities(entities_root: str) -> set[str]:
    """Every entity logical name the solution declares, from the directory names on disk."""
    if not os.path.isdir(entities_root):
        return set()
    return {name for name in os.listdir(entities_root)
            if os.path.isdir(os.path.join(entities_root, name))}


def app_entities(authored_text: str, entities_root: str) -> set[str]:
    """The solution tables this app actually names in authored source.

    Derived, never declared. Referencing a table's column means naming the table somewhere —
    a data source, a query, a typed model — so the moment the app grows a table, that table's
    secured columns come into scope with no edit to this script or its build step.
    """
    return {entity for entity in solution_entities(entities_root) if entity in authored_text}


def entity_columns(entities_root: str, entity: str) -> set[str]:
    """Every column logical name declared on one entity, secured or not."""
    path = os.path.join(entities_root, entity, "Entity.xml")
    if not os.path.isfile(path):
        return set()
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return set()
    columns: set[str] = set()
    for attribute in tree.getroot().iter("attribute"):
        name = attribute.get("PhysicalName") or attribute.findtext("LogicalName") or ""
        if name.strip():
            columns.add(name.strip())
    return columns


def forbidden_columns(pairs: set[tuple[str, str]], mine: set[str],
                      entities_root: str) -> tuple[set[str], set[str]]:
    """Split every secured column name into (forbidden, safe-on-one-of-my-own-tables).

    A name is SAFE only when it is a real column of a table this app queries AND is not
    secured on that table. Everything else stays forbidden, including secured columns of
    tables the app does not query — an app naming `rev_sortcode` has no innocent reading.
    """
    secured_on_mine = {(entity, column) for entity, column in pairs if entity in mine}
    safe: set[str] = set()
    for entity in sorted(mine):
        for column in entity_columns(entities_root, entity):
            if (entity, column) not in secured_on_mine:
                safe.add(column)
    forbidden = {column for _, column in pairs} - safe
    return forbidden, safe


def is_generated(rel: str) -> bool:
    norm = rel.replace(os.sep, "/")
    return any(f"/{d}/" in f"/{norm}" or norm.startswith(d) for d in GENERATED_DIRS)


def scan(app_root: str) -> list[tuple[str, str]]:
    """Return (relative path, text) for every authored-or-generated source file."""
    out: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(app_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in sorted(filenames):
            if os.path.splitext(filename)[1] not in SOURCE_EXT:
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, app_root)
            try:
                with open(full, encoding="utf-8") as handle:
                    out.append((rel, handle.read()))
            except (OSError, UnicodeDecodeError) as exc:
                out.append((rel, ""))
                print(f"WARNING: {rel}: could not read ({exc}); treated as empty, which means "
                      "this gate cannot see its contents.", file=sys.stderr)
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    app_root, profile_path = argv[1].rstrip("/"), argv[2]

    if argv[3:]:
        print(f"no-secured-columns-in-code-app: FAILED — unexpected argument "
              f"{argv[3]!r}. --exclude-profile was removed on 2026-08-23 (improvement review "
              "19): relevance is now derived from the app's own tables, so there is no "
              "profile deny-list to pass. Drop the flag from the build step.", file=sys.stderr)
        return 2

    if not os.path.isdir(app_root):
        print(f"no-secured-columns-in-code-app: FAILED — {app_root} is not a directory. A gate "
              "pointed at a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1
    if not os.path.isfile(profile_path):
        print(f"no-secured-columns-in-code-app: FAILED — {profile_path} does not exist, so the "
              "forbidden-column set cannot be derived. Unevaluable is not satisfied.",
              file=sys.stderr)
        return 1

    # <solution>/Other/FieldSecurityProfiles.xml -> <solution>/Entities. Derived from the path
    # already supplied rather than added as a third argument, but asserted, because a gate whose
    # subject is missing must fail rather than pass over nothing (IMP-0007).
    entities_root = os.path.join(os.path.dirname(os.path.dirname(profile_path)), "Entities")
    if not os.path.isdir(entities_root):
        print(f"no-secured-columns-in-code-app: FAILED — expected the solution's Entities/ "
              f"directory at {entities_root}, derived from the profile path, and it is not "
              "there. Without it neither the app's own tables nor their safe columns can be "
              "derived, and this gate cannot be scoped.", file=sys.stderr)
        return 1

    try:
        pairs, profiles = secured_pairs(profile_path)
    except ET.ParseError as exc:
        print(f"no-secured-columns-in-code-app: FAILED — {profile_path} is not parseable XML: "
              f"{exc}", file=sys.stderr)
        return 1
    if not pairs:
        print(f"no-secured-columns-in-code-app: FAILED — {profile_path} declares no "
              "FieldPermission, so the forbidden set is empty and this gate would pass over "
              "anything. That is a broken gate, not a clean app.", file=sys.stderr)
        return 1

    files = scan(app_root)
    if not files:
        print(f"no-secured-columns-in-code-app: FAILED — no source files ({', '.join(sorted(SOURCE_EXT))}) "
              f"under {app_root}. Nothing was scanned, so this is not a pass.", file=sys.stderr)
        return 1

    authored = [(rel, text) for rel, text in files if not is_generated(rel)]
    if not authored:
        print(f"no-secured-columns-in-code-app: FAILED — every source file under {app_root} is "
              "generator output. An app with no authored source implements nothing.",
              file=sys.stderr)
        return 1

    authored_text = "\n".join(text for _, text in authored)

    # Scope the forbidden set to this app's own tables — see the docstring. mine is derived from
    # the authored source, so it grows the day the app grows a table.
    mine = app_entities(authored_text, entities_root)
    if not mine:
        print(f"no-secured-columns-in-code-app: FAILED — no solution table under "
              f"{entities_root} is named anywhere in {app_root}'s authored source, so the "
              "forbidden set cannot be scoped and every secured name would be treated as "
              "unsafe. An app that names no table implements nothing.", file=sys.stderr)
        return 1
    forbidden, safe = forbidden_columns(pairs, mine, entities_root)

    errors: list[str] = []

    # 1. No secured column may be named in AUTHORED source.
    for rel, text in authored:
        for column in sorted(forbidden):
            # WHOLE-IDENTIFIER match, not a substring. `rev_amount` is secured on rev_payment
            # and is a prefix of `rev_amountrequested`, an unsecured rev_application column the
            # trustee is SUPPOSED to see. A bare substring search reports the safe column as a
            # privacy breach — the same "a name fragment is not an identity" defect this gate's
            # own rescoping fixes one level up, found by this change's acceptance test
            # (improvement review 19). Dataverse logical names are [a-z0-9_], so a lookaround
            # on that class is the correct boundary; \b would not exclude a leading underscore.
            pattern = r"(?<![A-Za-z0-9_])" + re.escape(column) + r"(?![A-Za-z0-9_])"
            for match in re.finditer(pattern, text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel}:{line}: references '{column}', which column security hides. "
                    "A trustee-facing app must never name a secured column — and this same "
                    "code runs for the process owner, for whom the column IS populated.")
                break  # one report per column per file is enough to act on

    # 2. The fail-closed conjunction must actually be implemented.
    for column, why in REQUIRED_COLUMNS:
        if column not in authored_text:
            errors.append(
                f"{app_root}: no authored source references '{column}' — {why}. Its absence "
                "means the control is not implemented, which this gate must fail on rather "
                "than pass over.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nno-secured-columns-in-code-app: FAILED — {len(errors)} finding(s) across "
              f"{len(authored)} authored file(s); forbidden set = {len(forbidden)} secured "
              f"column(s) from {', '.join(profiles)}, scoped to the {len(mine)} table(s) this "
              f"app names ({', '.join(sorted(mine))}).", file=sys.stderr)
        return 1

    print(f"no-secured-columns-in-code-app: OK — {len(authored)} authored file(s) reference none "
          f"of the {len(forbidden)} forbidden column(s), derived from {len(pairs)} secured "
          f"(table, column) pair(s) across {', '.join(profiles)} and scoped to the "
          f"{len(mine)} table(s) this app names ({', '.join(sorted(mine))}); "
          f"{len(safe)} column(s) of those tables are unsecured and therefore safe. All "
          f"{len(REQUIRED_COLUMNS)} fail-closed visibility columns are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
