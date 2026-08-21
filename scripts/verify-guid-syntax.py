#!/usr/bin/env python3
"""Verify every element of hand-authored solution source that MUST hold an id holds a real one.

WHY THIS EXISTS. While authoring rev_grant on 2026-08-18 the form's cell, tab, section and
form ids were written with a non-hex character in them — `{a1000000-0000-4000-8000-00000000ga01}`
contains a `g`. `pac solution pack` accepted the folder and exited 0. Nothing in the build
noticed: the file is well-formed XML, so `source-validate` passes; the ids are not
RootComponents, so `verify-solution-root-components.py` never looks at them. That is IMP-0036 /
C-TECH-058, and it is the same shape as every defect in this project's digest that cost a
deployment: a plausible-looking hand-authored value the packer does not validate, which fails
only later, in an environment, with an error that names nothing useful.

WHY IT WAS REWRITTEN (2026-08-21, improvement review 6 item 3, cluster A — IMP-0157, IMP-0164,
IMP-0167). The first version scanned for a SHAPE: every `{...}` token exactly 36 characters
long. It therefore proved only that things which already look like GUIDs are well formed. It
reported "284 GUIDs across 70 files all parse" over a tree containing
`{PENDING-ROLE-ID-REV-TRUSTEE}` in `Roles/REV Trustee/REV Trustee.xml` where an id is required:
a 27-character placeholder is not a MALFORMED GUID to a shape scanner, it is not a GUID at all,
so it was skipped. Scanning for a shape means everything off-shape is invisible.

So the check is now driven from THE ELEMENTS THAT MUST HOLD AN ID (the `ELEMENTS` table below),
not from tokens that already look like one, and three properties fall out of one pass:

  1. SYNTAX       — every id is a well-formed UUID. Unchanged in strength, over both file
                    CONTENTS and file NAMES (SolutionPackager names form files after their
                    formid, so a malformed name is as broken as a malformed element).
  2. COMPLETENESS — an id-bearing element holding a value that is not a UUID FAILS. This is the
                    property the shape scanner could not have. `{PENDING-ROLE-ID-REV-TRUSTEE}`
                    is caught here.
  3. UNIQUENESS   — a component type's PRIMARY KEY may not collide with another instance of the
                    SAME component type. Never across all tokens, and never across types.

PROPERTY 3 IS DELIBERATELY NARROW, AND THE WIDER RULE WAS DISPROVED BY MEASUREMENT BEFORE
ANYONE BUILT IT. IMP-0157 found a real collision — a hand-fabricated `savedqueryid` that already
belonged to another table's view — and proposed "fail on any id appearing in more than one
file". IMP-0164 measured that proposal against real source and found it fires ~23 times, every
one of them correct source. Re-measured on 2026-08-21 against this tree it is 22 values in more
than one file, and 169 repeat occurrences in total, in exactly four legitimate shapes:

  * Microsoft's control class ids are shared across all six forms BY DESIGN — 10 distinct
    `<control classid=>` values used 160 times. This one shape alone is 150 of the 169 repeats.
  * a role, a field security profile and a cloud flow id MUST appear both in its own definition
    file and in `Other/Solution.xml`'s matching `<RootComponent id=>`.
  * a form id MUST equal its own file name.
  * a site-map `<SubArea Url=...viewid=>` MUST repeat the `savedqueryid` of the view it opens.

A gate that fails the build 22 times on correct source teaches everyone to route around it,
which is how a gate becomes worse than no gate. Hence: only `key=True` rows below are checked
for collisions, only within their own component type. Measured on this tree, primary-key
collisions: 0. Legitimate repeats that must NOT be reported: 169.

THE HAND-KEPT LIST IS THE THING THAT CAN GO STALE, so it is asserted non-empty PER ELEMENT
TYPE. If the gate resolves zero elements for a type it declares it checks, it FAILS rather than
passing over nothing — that is IMP-0007's shape, the `! grep ... && echo` pattern that turned
every grep failure, including "the target does not exist", into a PASS. The per-type assertion
is enforced when the target is a whole solution root (it contains `Other/Solution.xml`); a
fixture subtree is legitimately partial, so there the weaker global form applies — resolving
zero id-bearing elements of ANY type is still a FAILURE.

XML COMMENTS ARE STRIPPED before the element pass. Solution source here documents itself
heavily and two id-bearing occurrences exist ONLY inside comments — a `<RootComponent
type="20" id="..."/>` example in `Roles/REV Trustee/REV Trustee.xml` and an
`<AppModuleComponent type="62" id="{d4f6a8b0-4002-...}"/>` example in `AppModuleSiteMap.xml`.
Counting those would invent violations and invent duplicates. This is the same lesson
`verify-forms-and-views-reachable.py` learned, and the same one that made
`grep -c '<FieldPermission'` report 52 where source has 51.

Run:
    python3 scripts/verify-guid-syntax.py src/solutions/RevitaliseGrantAutomation
    python3 scripts/verify-guid-syntax.py src/tests/fixtures/known-bad/guid-syntax

Exits 0 when every id-bearing element holds a well-formed, non-colliding UUID and every
declared element type resolved at least one element; 1 otherwise; 2 on a usage error. Wired
into config/<slug>-build.yml as the `guid-syntax` step.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import uuid
from collections import defaultdict
from typing import NamedTuple

# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE ID-BEARING ELEMENT LIST.
#
# Every row was confirmed to exist in real source before it was written here — the element
# names are not guessed. Each `pattern` was run over
# src/solutions/RevitaliseGrantAutomation and the observed count on 2026-08-21 is recorded in
# `observed`. Adding a row means running it over real source first; a row that resolves
# nothing in a solution root fails this gate by design (see the module docstring).
#
#   key=True   this value is the component's PRIMARY KEY. Two instances of the SAME component
#              type may not share it. Checked for collisions.
#   key=False  this value is a REFERENCE to a component defined elsewhere. Repetition is the
#              whole point of a reference, so it is checked for SYNTAX and COMPLETENESS only.
#              Putting `control classid` or `RootComponent id` in the key set is precisely the
#              rule IMP-0164 disproved.
# ─────────────────────────────────────────────────────────────────────────────────────────────


class Element(NamedTuple):
    component: str  # component type — the scope within which a primary key must be unique
    field: str  # the element or attribute that carries the id
    pattern: str  # one capture group, the raw id text
    key: bool  # True = primary key of `component`; False = a reference to one
    observed: int  # count measured against real source on 2026-08-21
    why: str  # what breaks if this holds a non-id


ELEMENTS: tuple[Element, ...] = (
    Element(
        "form", "<formid>",
        r"<formid>\s*([^<>]*?)\s*</formid>",
        True, 6,
        "the form's own primary key; a malformed one is IMP-0036 itself",
    ),
    Element(
        "view", "<savedqueryid>",
        r"<savedqueryid>\s*([^<>]*?)\s*</savedqueryid>",
        True, 14,
        "the view's own primary key; IMP-0157 was a fabricated one already owned by another "
        "table's view",
    ),
    Element(
        "security role", "<Role id=>",
        r"<Role\b[^>]*?\bid=\"([^\"]*)\"",
        True, 3,
        "must equal the live roleid — an import declaring the same role name with a different "
        "id fails outright (IMP-0166)",
    ),
    Element(
        "field security profile", "<FieldSecurityProfile fieldsecurityprofileid=>",
        r"<FieldSecurityProfile\b[^>]*?\bfieldsecurityprofileid=\"([^\"]*)\"",
        True, 1,
        "FieldSecurityProfileProcessor keys type 70 RootComponents on this value, so a bad one "
        "means the profile does not ship",
    ),
    Element(
        "cloud flow", "<Workflow WorkflowId=>",
        r"<Workflow\b[^>]*?\bWorkflowId=\"([^\"]*)\"",
        True, 4,
        "the flow's primary key, repeated in the .json file name and in Solution.xml's type 29 "
        "RootComponent",
    ),
    Element(
        "form tab", "<tab id=>",
        r"<tab\b[^>]*?\bid=\"([^\"]*)\"",
        True, 12,
        "one of the four form sub-component ids hand-authored wrong in IMP-0036",
    ),
    Element(
        "form section", "<section id=>",
        r"<section\b[^>]*?\bid=\"([^\"]*)\"",
        True, 31,
        "one of the four form sub-component ids hand-authored wrong in IMP-0036",
    ),
    Element(
        "form cell", "<cell id=>",
        r"<cell\b[^>]*?\bid=\"([^\"]*)\"",
        True, 160,
        "one of the four form sub-component ids hand-authored wrong in IMP-0036. NOTE the "
        "sibling <control id=> is a column LOGICAL NAME, not an id, and is not listed here",
    ),
    Element(
        "packed file name", "{...}.xml basename",
        # Filled by scan_file_name(), not by a regex over file contents.
        r"(?!)",
        False, 6,
        "SolutionPackager names form files after their formid; a malformed name is as broken as "
        "a malformed element. NOT a key: matching its own formid is required, not a collision",
    ),
    Element(
        "solution root component", "<RootComponent id=>",
        r"<RootComponent\b[^>]*?\bid=\"([^\"]*)\"",
        False, 7,
        "a reference to a role, flow or profile defined elsewhere; RootComponentsValidation "
        "treats an unmatched component as FATAL. Types 62 and 80 are keyed by schemaName, not "
        "id, and correctly resolve nothing here",
    ),
    Element(
        "form control class", "<control classid=>",
        r"<control\b[^>]*?\bclassid=\"([^\"]*)\"",
        False, 160,
        "Microsoft's platform control class id. SHARED ACROSS EVERY FORM BY DESIGN — 150 of the "
        "169 legitimate repeats on this tree. Never a key",
    ),
    Element(
        "app web resource", "<WebResourceId>",
        r"<WebResourceId>\s*([^<>]*?)\s*</WebResourceId>",
        False, 1,
        "AppModule.xml's own header records that this is a SHARED PLATFORM RESOURCE, NOT UNIQUE "
        "TO THIS APP, so it is a reference and never a key",
    ),
    Element(
        "sitemap subarea view", "<SubArea Url=...viewid=>",
        r"<SubArea\b[^>]*?\bUrl=\"[^\"]*?viewid=([^&\"]*)",
        False, 6,
        "repeats the savedqueryid of the view the sub-area opens. Three brace encodings are "
        "live here on purpose (IMP-0087/IMP-0091), so all three are accepted",
    ),
)

# Canonical dashed 8-4-4-4-12. Stricter than uuid.UUID(), which also accepts undashed and
# urn:uuid: spellings that SolutionPackager does not write.
CANONICAL_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
XML_COMMENT = re.compile(r"<!--.*?-->", re.S)
BRACED_IN_NAME = re.compile(r"\{([^{}]*)\}")
# The pre-2026-08-21 shape scan, kept verbatim as a backstop so the rewrite cannot lose
# IMP-0036 coverage anywhere the element list does not reach. It runs over RAW text, comments
# included, exactly as before.
LEGACY_SHAPE_TOKEN = re.compile(r"\{([^{}\s]{36})\}")


def blank_comments(text: str) -> str:
    """Blank out XML comments, preserving byte offsets and line numbers."""
    return XML_COMMENT.sub(
        lambda m: "".join("\n" if c == "\n" else " " for c in m.group(0)), text
    )


def unwrap(raw: str) -> str:
    """Strip the optional brace form an id is written in. `{g}`, `%7bg%7d` and bare `g` are all
    live in this solution's site map on purpose, so all three unwrap to the same value."""
    value = raw.strip()
    lowered = value.lower()
    for lo, hi in (("{", "}"), ("%7b", "%7d")):
        if lowered.startswith(lo) and lowered.endswith(hi) and len(value) > len(lo) + len(hi) - 1:
            return value[len(lo):len(value) - len(hi)].strip()
    return value


def is_uuid(value: str) -> bool:
    if not CANONICAL_UUID.match(value):
        return False
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = argv[1].rstrip("/")
    if not os.path.isdir(root):
        print(f"guid-syntax: FAILED — {root} is not a directory. A gate pointed at a missing "
              "target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    paths = sorted(glob.glob(os.path.join(root, "**", "*.xml"), recursive=True))
    if not paths:
        print(f"guid-syntax: FAILED — no .xml files found under {root}", file=sys.stderr)
        return 1

    # A whole solution root must contain every component type this gate declares. A fixture
    # subtree is legitimately partial.
    solution_root = os.path.isfile(os.path.join(root, "Other", "Solution.xml"))

    errors: list[str] = []
    resolved: dict[tuple[str, str], int] = {(e.component, e.field): 0 for e in ELEMENTS}
    # (component, normalised id) -> [ "rel:line", ... ]  — primary keys only
    keys: dict[tuple[str, str], list[str]] = defaultdict(list)
    # normalised id -> how many id-bearing elements of ANY type hold it. Only used to report
    # how many legitimate repeats the narrow uniqueness rule deliberately did not fire on.
    census: dict[str, int] = defaultdict(int)
    reported_values: set[tuple[str, str]] = set()
    checked = 0

    name_element = next(e for e in ELEMENTS if e.field == "{...}.xml basename")

    for path in paths:
        rel = os.path.relpath(path)
        raw = open(path, encoding="utf-8").read()
        body = blank_comments(raw)

        # ── file NAMES. SolutionPackager names form files after their formid. ──────────────
        for match in BRACED_IN_NAME.finditer(os.path.basename(path)):
            checked += 1
            resolved[(name_element.component, name_element.field)] += 1
            value = unwrap("{" + match.group(1) + "}")
            if not is_uuid(value):
                kind = "malformed" if len(match.group(1)) == 36 else "not an id at all"
                errors.append(
                    f"{rel}: FILE NAME carries '{{{match.group(1)}}}' — {kind}, not a "
                    f"well-formed UUID. {name_element.why}"
                )
                reported_values.add((rel, match.group(1)))
            else:
                census[value.lower()] += 1

        # ── file CONTENTS, driven from the element list. ───────────────────────────────────
        for element in ELEMENTS:
            if element is name_element:
                continue
            for match in re.finditer(element.pattern, body):
                checked += 1
                resolved[(element.component, element.field)] += 1
                raw_value = match.group(1)
                value = unwrap(raw_value)
                line = line_of(body, match.start(1))
                if not value:
                    errors.append(
                        f"{rel}:{line}: {element.component} {element.field} is EMPTY — an "
                        f"id-bearing element with no id. {element.why}"
                    )
                    reported_values.add((rel, raw_value))
                    continue
                if not is_uuid(value):
                    kind = ("malformed — 36 characters but not a parseable UUID"
                            if len(raw_value.strip("{}")) == 36
                            else "NOT A UUID AT ALL — a shape scan cannot see this")
                    errors.append(
                        f"{rel}:{line}: {element.component} {element.field} holds "
                        f"'{raw_value}' — {kind}. {element.why}"
                    )
                    reported_values.add((rel, raw_value))
                    continue
                census[value.lower()] += 1
                if element.key:
                    keys[(element.component, value.lower())].append(f"{rel}:{line}")

        # ── the pre-rewrite shape scan, kept so the rewrite cannot lose coverage. ──────────
        for token in sorted(set(LEGACY_SHAPE_TOKEN.findall(raw))):
            if (rel, token) in reported_values or (rel, "{" + token + "}") in reported_values:
                continue
            if not is_uuid(token):
                errors.append(
                    f"{rel}: malformed GUID '{{{token}}}' — not a parseable UUID (found by the "
                    "legacy shape scan, so no element in this gate's list claims it)"
                )

    # ── property 3: a primary key may not collide within its own component type. ───────────
    for (component, value), sites in sorted(keys.items()):
        if len(sites) > 1:
            errors.append(
                f"{component} primary key '{{{value}}}' is used {len(sites)} times within the "
                f"same component type: {', '.join(sites)}. Two {component}s cannot share one "
                "id (IMP-0157)."
            )

    # ── the hand-kept list must not go stale: no declared type may resolve nothing. ────────
    empty = [f"{c} {f}" for (c, f), n in resolved.items() if n == 0]
    if checked == 0:
        errors.append(
            f"no id-bearing element of ANY declared type was found under {root}. A gate that "
            "resolves nothing passes over nothing (IMP-0007)."
        )
    elif solution_root and empty:
        for name in sorted(empty):
            errors.append(
                f"the element list declares '{name}' and resolved ZERO of them under a full "
                f"solution root ({root}). Either the element name has changed and this gate is "
                "now blind to it, or the component was removed — either way this is not a PASS "
                "(IMP-0007)."
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nguid-syntax: FAILED — {len(errors)} problem(s) over {checked} id-bearing "
              f"element(s) in {len(paths)} file(s). `pac solution pack` accepts these and exits "
              "0; the target does not.", file=sys.stderr)
        return 1

    mode = "solution root" if solution_root else "partial tree"
    repeats = sum(n - 1 for n in census.values() if n > 1)
    print(f"guid-syntax: OK — {checked} id-bearing element(s) across {len(paths)} file(s) "
          f"({mode}): every value is a well-formed UUID, no primary key collides within its "
          f"component type, and {repeats} legitimate repeat(s) of an id across component types "
          "were correctly NOT reported (IMP-0164).")
    for element in ELEMENTS:
        count = resolved[(element.component, element.field)]
        role = "primary key" if element.key else "reference"
        print(f"    {count:>4} × {element.component} {element.field}  [{role}]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
