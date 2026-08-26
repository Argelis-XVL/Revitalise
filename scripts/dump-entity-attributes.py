#!/usr/bin/env python3
"""Print every attribute a solution entity declares — the ground truth behind a negative claim.

WHY THIS EXISTS. A negative claim about schema — *"no column supplies preferred dates"*, *"no
break-location column exists anywhere in the solution"* — is the one claim a partial scan cannot
support, because the evidence for it is the WHOLE attribute set and nothing less. This project has
now written that claim wrongly three times about the same TAD sentence:

  * `IMP-0326` recorded that "no preferred, holiday or travel date column exists anywhere in the
    solution", and drove improvement review 29's largest escalation — a mechanical coverage gate
    plus a priced change-order candidate.
  * `IMP-0337` found `rev_breaklocation` already present, unsecured, its own `<Description>`
    reading "TRUSTEE-VISIBLE ON PURPOSE" for exactly that data.
  * `IMP-0338` found `rev_breakstart` and `rev_breakend` on `rev_application`, committed eleven
    days BEFORE the finding that said no such column existed. It carries `corrects` against
    `IMP-0326`.

The coverage gate is green today with no schema change and no change order. **The class was never
about data the solution could not supply; it was about nobody enumerating the columns.**

So this is a TOOL, not a gate. `skills/how-to-verify-a-platform-contract.md` §2 states the rule —
a negative claim is backed by a full attribute enumeration, never a remembered category list — and
this makes obeying it one command. There is deliberately no gate over the prose: reading a negative
claim out of narrative and refuting it against schema is prose resolution, the design improvement
review 29 measured at 48% false positives before rejecting it.

USAGE

    python3 scripts/dump-entity-attributes.py rev_application
    python3 scripts/dump-entity-attributes.py --list
    python3 scripts/dump-entity-attributes.py rev_application --grep date
    python3 scripts/dump-entity-attributes.py --all --grep location

`--grep` filters on the attribute name AND its description, because the thing you are looking for
is often named nothing like the requirement's words: "preferred dates" is `rev_breakstart`, and
only the description says so.

EXIT CODES: 0 printed something; 1 the entity or solution does not exist, or a filter matched
nothing (an empty result must never read as "no such column" — that is the very defect); 2 usage.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SOLUTION = Path("src/solutions/RevitaliseGrantAutomation")


@dataclass(frozen=True)
class Attribute:
    entity: str
    physical_name: str
    type_: str
    max_length: str
    is_secured: str
    required: str
    description: str

    def line(self) -> str:
        secured = "SECURED" if self.is_secured == "1" else "-"
        length = self.max_length or "-"
        return (f"  {self.physical_name:<34} {self.type_:<14} len={length:<6} "
                f"{secured:<8} req={self.required or '-':<10} {self.description[:88]}")


def _text(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def read_entity(entity_dir: Path) -> list[Attribute]:
    """Every <attribute> the entity's own Entity.xml declares.

    Reads the SOURCE, not a generated model. A generated per-table model, a code-app type file and
    a form are all projections of one table — searching one answers a different question, which is
    how an approved amendment concluded that no column matched a category `rev_applicanttype` had
    reproduced verbatim for nine days.
    """
    xml = entity_dir / "Entity.xml"
    if not xml.is_file():
        return []
    try:
        root = ET.parse(xml).getroot()
    except ET.ParseError as exc:
        print(f"ERROR: {xml} does not parse: {exc}", file=sys.stderr)
        return []

    out: list[Attribute] = []
    for attr in root.iter("attribute"):
        name = attr.get("PhysicalName") or _text(attr.find("Name"))
        if not name:
            continue
        desc = ""
        descriptions = attr.find("Descriptions")
        if descriptions is not None:
            first = descriptions.find("Description")
            if first is not None:
                desc = (first.get("description") or "").strip()
        out.append(Attribute(
            entity=entity_dir.name,
            physical_name=name,
            type_=_text(attr.find("Type")),
            max_length=_text(attr.find("MaxLength")),
            is_secured=_text(attr.find("IsSecured")),
            required=_text(attr.find("RequiredLevel")),
            description=desc,
        ))
    return out


def entities(solution: Path) -> list[Path]:
    root = solution / "Entities"
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir())


def selftest() -> int:
    """Prove this tool reads a real Entity.xml, including the three columns that earned it."""
    failures: list[str] = []
    solution = DEFAULT_SOLUTION
    if not solution.is_dir():
        print("dump-entity-attributes --selftest: SKIPPED — no solution tree at "
              f"{solution} (run from the repository root).", file=sys.stderr)
        return 1

    found = read_entity(solution / "Entities" / "rev_application")
    by_name = {a.physical_name: a for a in found}
    if not found:
        failures.append("rev_application yielded no attributes at all")

    # The three columns three separate findings said did not exist. If this tool cannot see them,
    # it cannot support the rule it exists for.
    for column in ("rev_breaklocation", "rev_breakstart", "rev_breakend"):
        if column not in by_name:
            failures.append(f"{column} was not found, and IMP-0337/IMP-0338 established it is "
                            f"there — a dump that misses the columns this tool exists to surface "
                            f"is worse than no dump")

    # A text column must report its MaxLength, or the tool cannot serve C-TECH-060's question.
    lengths = [a for a in found if a.type_ == "nvarchar" and a.max_length]
    if not lengths:
        failures.append("no nvarchar attribute reported a MaxLength")

    # A description must come through: 'preferred dates' is rev_breakstart, and ONLY the
    # description says so. This is the whole reason --grep searches descriptions too.
    start = by_name.get("rev_breakstart")
    if start and "prefer" not in start.description.lower():
        failures.append("rev_breakstart's description did not come through, so a name-only "
                        "search would still miss it")

    if failures:
        for f in failures:
            print(f"SELFTEST FAILURE: {f}", file=sys.stderr)
        print(f"\ndump-entity-attributes --selftest: FAILED ({len(failures)} failure(s)).",
              file=sys.stderr)
        return 1

    print(f"dump-entity-attributes --selftest: OK — read {len(found)} attributes from "
          f"rev_application, including rev_breaklocation, rev_breakstart and rev_breakend (the "
          f"three columns IMP-0326 said did not exist), {len(lengths)} nvarchar MaxLength values, "
          f"and rev_breakstart's 'would prefer' description — the text that makes a name-only "
          f"search for 'preferred dates' miss it.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("entity", nargs="?", help="entity folder name, e.g. rev_application")
    parser.add_argument("--solution", type=Path, default=DEFAULT_SOLUTION)
    parser.add_argument("--all", action="store_true", help="every entity in the solution")
    parser.add_argument("--list", action="store_true", help="list entity names and exit")
    parser.add_argument("--grep", default=None,
                        help="case-insensitive filter over attribute name AND description")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    dirs = entities(args.solution)
    if not dirs:
        print(f"ERROR: no Entities/ under {args.solution}. Nothing was read, so nothing here "
              f"supports a claim in either direction.", file=sys.stderr)
        return 1

    if args.list:
        print(f"{len(dirs)} entity(ies) in {args.solution}:")
        for d in dirs:
            print(f"  {d.name}")
        return 0

    if args.all:
        targets = dirs
    elif args.entity:
        targets = [d for d in dirs if d.name == args.entity]
        if not targets:
            print(f"ERROR: no entity '{args.entity}' in {args.solution}. Present: "
                  f"{', '.join(d.name for d in dirs)}", file=sys.stderr)
            return 1
    else:
        parser.print_usage(sys.stderr)
        print("\nName an entity, or pass --all / --list.", file=sys.stderr)
        return 2

    needle = (args.grep or "").lower()
    total = 0
    shown = 0
    for d in targets:
        attrs = read_entity(d)
        total += len(attrs)
        if needle:
            attrs = [a for a in attrs
                     if needle in a.physical_name.lower() or needle in a.description.lower()]
        if not attrs:
            continue
        print(f"\n{d.name} — {len(attrs)} attribute(s)"
              + (f" matching {args.grep!r}" if needle else ""))
        for a in sorted(attrs, key=lambda x: x.physical_name):
            print(a.line())
        shown += len(attrs)

    print(f"\n{shown} attribute(s) shown of {total} declared across "
          f"{len(targets)} entity(ies).")
    if needle and shown == 0:
        # An empty filtered result is the exact moment a negative claim gets written. Say what it
        # does and does not prove, in the output, where the person reading it will see it.
        print(f"\nNOTHING matched {args.grep!r}. That is evidence about this NAME, not about the "
              f"data: 'preferred dates' is rev_breakstart and 'break location' is "
              f"rev_breaklocation, and neither contains the requirement's words. Re-run with a "
              f"different needle, or read the full dump, before writing that no column supplies "
              f"it (IMP-0326, IMP-0337, IMP-0338).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
