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


def secured_columns(profile_path: str) -> tuple[set[str], list[str]]:
    """Every attribute named by any FieldPermission — i.e. every column security hides."""
    tree = ET.parse(profile_path)
    cols: set[str] = set()
    profiles: list[str] = []
    for profile in tree.getroot().iter("FieldSecurityProfile"):
        profiles.append(profile.get("name", "<unnamed>"))
    for attr in tree.getroot().iter("AttributeName"):
        if attr.text and attr.text.strip():
            cols.add(attr.text.strip())
    return cols, profiles


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
    if len(argv) != 3:
        print(__doc__)
        return 2
    app_root, profile_path = argv[1].rstrip("/"), argv[2]

    if not os.path.isdir(app_root):
        print(f"no-secured-columns-in-code-app: FAILED — {app_root} is not a directory. A gate "
              "pointed at a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1
    if not os.path.isfile(profile_path):
        print(f"no-secured-columns-in-code-app: FAILED — {profile_path} does not exist, so the "
              "forbidden-column set cannot be derived. Unevaluable is not satisfied.",
              file=sys.stderr)
        return 1

    try:
        forbidden, profiles = secured_columns(profile_path)
    except ET.ParseError as exc:
        print(f"no-secured-columns-in-code-app: FAILED — {profile_path} is not parseable XML: "
              f"{exc}", file=sys.stderr)
        return 1
    if not forbidden:
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

    errors: list[str] = []

    # 1. No secured column may be named in AUTHORED source.
    for rel, text in authored:
        for column in sorted(forbidden):
            for match in re.finditer(re.escape(column), text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel}:{line}: references '{column}', which column security hides. "
                    "A trustee-facing app must never name a secured column — and this same "
                    "code runs for the process owner, for whom the column IS populated.")
                break  # one report per column per file is enough to act on

    # 2. The fail-closed conjunction must actually be implemented.
    authored_text = "\n".join(text for _, text in authored)
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
              f"column(s) from {', '.join(profiles)}.", file=sys.stderr)
        return 1

    print(f"no-secured-columns-in-code-app: OK — {len(authored)} authored file(s) reference none "
          f"of the {len(forbidden)} column(s) secured by {', '.join(profiles)}, and all "
          f"{len(REQUIRED_COLUMNS)} fail-closed visibility columns are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
