#!/usr/bin/env python3
"""Enforce the domain constraints that are mechanically decidable from solution source.

WHY THIS EXISTS. `constraints/domain/domain-constraints.md` held fifteen rows on 2026-08-19.
Thirteen were generic GDPR and audit boilerplate whose `Verify By` was a document section
("TAD §6 documents the append-only mechanism"), and two — C-DOM-030 and C-DOM-031 — were
still the scaffolding's literal `[PLACEHOLDER] Replace with your first domain-specific
constraint`, HARD, in architect-agent's and development-agent's scope, with
`[Verification method]` as their verification.

A HARD constraint whose rule text is a placeholder always passes. That is `gate-cannot-fail`
(IMP-0035, `blocker`), and it had gone unnoticed through every gate of every feature this
project has shipped, because `skills/how-to-apply-constraints.md` offers no outcome between
PASS and VIOLATION for a rule that cannot be evaluated at all.

Meanwhile the technology side of the same repository had acquired nine executable gates. The
asymmetry is not an accident: 32 of the 47 findings in `logs/improvement-log.jsonl` come from
build-agent and pipeline-agent, so the learning loop only ever fed technology constraints.
Nothing about the charity's actual obligations — Article 9 health data, safeguarding, the
scoring-fairness position — had any mechanical enforcement whatsoever.

This script is the domain side's first executable gate.

WHAT IT CHECKS. Everything is read from `constraints/domain/special-category-register.yml` at
check time; nothing is transcribed into this file (C-TECH-060's rule, applied to a column list
instead of a length limit).

  C-DOM-030  Every register column exists in its declared entity, and the build config's
             FR-016 grep alternation contains EXACTLY the register's columns. The alternation
             was previously hand-maintained inside a shell one-liner and was edited four times
             in eight days; a name dropped from it narrows a HARD compliance gate silently.

  C-DOM-031  Every register column carries <IsSecured>1</IsSecured>, unless the register
             records an explicit `secured: exception` with a reason and an owner. Exceptions
             are printed on every run — a documented exception stays visible, it does not
             become invisible.

  C-DOM-032  Every register column carries <IsAuditEnabled>1</IsAuditEnabled>. Special-category
             data with no audit trail cannot answer "who saw this, and when" — the question
             C-DOM-010 and C-DOM-011 exist to answer, and which nothing enforced.

  C-DOM-004  No registered column name appears on an entity the register does not declare it
             on. A special-category column copied onto rev_errorlog — or given an undeclared
             second home — is a "personal data in application logs" breach that no diff of a
             single file makes visible. This was verified by "code review checklist item
             confirmed", i.e. by someone remembering.

  C-DOM-033  Every attribute carrying <IsSecured>1</IsSecured> appears in the register's
             `columns:` list OR in its `pending_adjudication:` list — never neither, never both.
             The four checks above all read the register and ask whether SOURCE agrees with IT;
             none asked the converse, so a secured Article 9 column that nobody registered passed
             every one of them. rev_applicant.rev_ethnicgroup did, for eight days, while its own
             Description read "UK GDPR ARTICLE 9 special-category data (Tier 4)" (IMP-0598).

             This asserts only that every secured column has been LOOKED AT. It does NOT assert
             the classification is right: Article 9 membership is a legal judgement about what
             data means, owned by the Domain Owner / Compliance Lead. `pending_adjudication:` is
             a visible, enumerated DEBT, printed on every run including green ones.

  It also REPORTS (does not fail on) any other attribute in the solution with auditing off, so
  a deliberate exclusion is a visible decision rather than a silent one. Two exist today:
  rev_applicant.rev_fullname and rev_application.rev_costs.

Run:
    python3 scripts/verify-domain-invariants.py src/solutions/RevitaliseGrantAutomation

Exits 0 on PASS, 1 on any violation, 2 on a usage error. Fails — never passes — when the
register, the solution root, or the build config cannot be read, so it cannot report PASS over
nothing (IMP-0007).

Wired into config/<slug>-build.yml as the `domain-invariants` step.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - the CI job installs it explicitly
    print("verify-domain-invariants: FAILED — pyyaml is not installed "
          "(`python3 -m pip install pyyaml`).", file=sys.stderr)
    raise SystemExit(1)

DEFAULT_REGISTER = Path("constraints/domain/special-category-register.yml")
FR016_STEP = "no-special-category-data-in-scoring"


def load_register(path: Path) -> tuple[dict, list[str]]:
    if not path.is_file():
        return {}, [f"register '{path}' does not exist. A domain gate with no register "
                    f"checks nothing (IMP-0007)."]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return {}, [f"register '{path}' is not valid YAML: {exc}"]
    if not isinstance(data, dict) or not (data.get("columns") or []):
        return {}, [f"register '{path}' declares no columns."]
    return data, []


def load_attributes(solution_root: Path) -> tuple[dict[tuple[str, str], dict], list[str]]:
    """Map (entity, logical_name) -> {'secured': str|None, 'audit': str|None}."""
    pattern = os.path.join(str(solution_root), "Entities", "*", "Entity.xml")
    paths = sorted(glob.glob(pattern))
    if not paths:
        return {}, [f"no Entities/*/Entity.xml found under '{solution_root}'. A gate with no "
                    f"scannable surface must fail, not pass (IMP-0007)."]

    attributes: dict[tuple[str, str], dict] = {}
    errors: list[str] = []
    for path in paths:
        entity = Path(path).parent.name
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{path}: not well-formed XML — {exc}")
            continue
        for attribute in root.iter("attribute"):
            logical = (attribute.findtext("LogicalName")
                       or attribute.get("PhysicalName") or "").strip().lower()
            if not logical:
                continue
            attributes[(entity, logical)] = {
                "secured": attribute.findtext("IsSecured"),
                "audit": attribute.findtext("IsAuditEnabled"),
                "path": os.path.relpath(path),
            }
    return attributes, errors


def build_config_alternation(build_config: Path) -> tuple[set[str] | None, list[str]]:
    """Extract the column names from the FR-016 gate's grep alternation."""
    if not build_config.is_file():
        return None, [f"build config '{build_config}' does not exist, so the FR-016 gate's "
                      f"column list cannot be cross-checked against the register."]
    try:
        config = yaml.safe_load(build_config.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"build config '{build_config}' is not valid YAML: {exc}"]

    steps = (config or {}).get("steps") or []
    command = next((str(s.get("command") or "") for s in steps
                    if isinstance(s, dict) and s.get("name") == FR016_STEP), "")
    if not command:
        return None, [f"build config '{build_config}' declares no '{FR016_STEP}' step. That "
                      f"step is the HARD FR-016 compliance gate; its absence is a violation, "
                      f"not a reason to skip this check."]

    match = re.search(r"body/\(([^)]*)\)", command)
    if not match:
        return None, [f"could not parse the column alternation out of the '{FR016_STEP}' "
                      f"step's command. Expected the shape `body/(name|name|...)`."]
    return {n.strip().lower() for n in match.group(1).split("|") if n.strip()}, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solution_root", type=Path,
                        help="path to the unpacked solution, e.g. src/solutions/<Name>")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--build-config", type=Path, default=None,
                        help="config/<slug>-build.yml; skips the FR-016 cross-check if unset")
    args = parser.parse_args(argv)

    errors: list[str] = []
    notes: list[str] = []

    if not args.solution_root.is_dir():
        print(f"verify-domain-invariants: FAILED — '{args.solution_root}' is not a directory. "
              f"A gate pointed at a missing target does not pass (IMP-0007).", file=sys.stderr)
        return 1

    register, register_errors = load_register(args.register)
    errors += register_errors
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("\nDOMAIN INVARIANTS: FAILED — the register could not be read.", file=sys.stderr)
        return 1

    attributes, attr_errors = load_attributes(args.solution_root)
    errors += attr_errors

    columns = register.get("columns") or []
    exceptions: list[tuple[str, str]] = []
    checked = 0

    for entry in columns:
        name = str(entry.get("name") or "").strip().lower()
        entity = str(entry.get("entity") or "").strip()
        if not name or not entity:
            errors.append(f"register row {entry!r}: 'name' and 'entity' are both required.")
            continue

        found = attributes.get((entity, name))
        if found is None:
            errors.append(
                f"C-DOM-030 — {entity}.{name} is in the special-category register but does "
                f"not exist in {args.solution_root}/Entities/{entity}/Entity.xml. Either the "
                f"column was removed and the register was not updated, or it was never "
                f"created. A register that names phantom columns protects nothing."
            )
            continue

        checked += 1
        secured_mode = str(entry.get("secured") or "required").strip().lower()

        # ── C-DOM-031 — secured, or an explicit exception with a reason and an owner ────
        if secured_mode == "exception":
            reason = str(entry.get("reason") or "").strip()
            owner = str(entry.get("owner") or "").strip()
            if not reason or not owner:
                errors.append(
                    f"C-DOM-031 — {entity}.{name} declares `secured: exception` with no "
                    f"{'reason' if not reason else 'owner'}. An undocumented exception to a "
                    f"HARD constraint is indistinguishable from an oversight."
                )
            else:
                exceptions.append((f"{entity}.{name}", reason.split("\n")[0].strip()))
        elif secured_mode == "required":
            if found["secured"] != "1":
                errors.append(
                    f"C-DOM-031 — {entity}.{name} is special-category data "
                    f"(<IsSecured>{found['secured']}</IsSecured>). Set <IsSecured>1</IsSecured> "
                    f"and add it to the field security profile, or record a `secured: "
                    f"exception` with a reason and an owner in {args.register}."
                )
        else:
            errors.append(f"register row {entity}.{name}: 'secured' must be 'required' or "
                          f"'exception', got '{secured_mode}'.")

        # ── C-DOM-032 — auditing, with no exception route ──────────────────────────────
        if found["audit"] != "1":
            errors.append(
                f"C-DOM-032 — {entity}.{name} is special-category data with "
                f"<IsAuditEnabled>{found['audit']}</IsAuditEnabled>. Special-category data "
                f"with no audit trail cannot answer 'who saw this, and when' (C-DOM-010, "
                f"C-DOM-011, NFR-014)."
            )

    # ── C-DOM-004 — a registered column must not be duplicated onto another entity ──────
    # "Personal data must not be written to application logs" was verified by "code review
    # checklist item confirmed" — that is, by someone remembering. The mechanical half of it
    # is decidable here: a special-category column name appearing on an entity the register
    # does not declare it on is either a copy onto the error-log table or an undeclared
    # second home for the same data. Both are C-DOM-004 breaches and neither is visible in a
    # diff that only adds one attribute to one file.
    registered_names = {str(e.get("name") or "").strip().lower(): str(e.get("entity") or "").strip()
                        for e in columns}
    for (entity, name), meta in sorted(attributes.items()):
        declared_entity = registered_names.get(name)
        if declared_entity and entity != declared_entity:
            errors.append(
                f"C-DOM-004 — {entity}.{name} duplicates the special-category column "
                f"registered on {declared_entity}. A registered column appearing on a second "
                f"entity is either a copy into a log or audit table, or an undeclared second "
                f"home for Article 9 data. Declare it in {args.register} with its own basis "
                f"and security position, or remove it."
            )

    # ── C-DOM-030 — the build gate's list and the register must be the same list ────────
    alternation_size = None
    if args.build_config is not None:
        alternation, alternation_errors = build_config_alternation(args.build_config)
        errors += alternation_errors
        if alternation is not None:
            alternation_size = len(alternation)
            registered = {str(e.get("name") or "").strip().lower() for e in columns}
            missing_from_gate = sorted(registered - alternation)
            extra_in_gate = sorted(alternation - registered)
            if missing_from_gate:
                errors.append(
                    f"C-DOM-030 — the FR-016 gate in {args.build_config} does not bar "
                    f"{', '.join(missing_from_gate)}. Every register column must appear in the "
                    f"'{FR016_STEP}' alternation, or the HARD compliance gate silently narrows."
                )
            if extra_in_gate:
                errors.append(
                    f"C-DOM-030 — the FR-016 gate bars {', '.join(extra_in_gate)}, which the "
                    f"register does not list. Add them to {args.register} (with a basis) or "
                    f"remove them from the gate. Two lists that disagree are one list nobody "
                    f"maintains."
                )

    # The (entity, name) keys the register declares. Used by C-DOM-033 below and by the
    # report-only auditing pass at the end.
    registered_keys = {(str(e.get("entity") or "").strip(),
                        str(e.get("name") or "").strip().lower()) for e in columns}

    # ── C-DOM-033 — every SECURED column is adjudicated, in one list or the other ───────
    #
    # IMP-0598 (blocker). rev_applicant.rev_ethnicgroup was live, IsSecured=1, IsAuditEnabled=1,
    # in REV_TrusteeRestricted, intake-flow mapped, and self-describing in its own Entity.xml
    # Description as "UK GDPR ARTICLE 9 special-category data (Tier 4)" — and absent from the
    # register for eight days. Every check above passed throughout, because all four of them read
    # the register and ask whether SOURCE agrees with IT. None asked the converse: whether the
    # register is COMPLETE against source. A register that claims to be a single source of truth
    # is only as complete as somebody's memory until something checks that direction.
    #
    # WHAT THIS ASSERTS, precisely: every attribute with <IsSecured>1</IsSecured> appears in
    # `columns:` or in `pending_adjudication:`. Nothing more. It does NOT assert that a column was
    # classified CORRECTLY — Article 9 membership is a legal judgement about what data means, and
    # the register's owner is the Domain Owner / Compliance Lead, not this script.
    #
    # WHY IT IS SHAPED LIKE THIS. The finding proposed scanning Entity.xml descriptions for
    # Article-9 language. Measured over all 226 attributes on 2026-09-04, every automatic signal is
    # noise, and one of them is inverted: description text (case-insensitive) → 9 findings, 1 true
    # positive (11%), and its false positives are the columns whose authors documented NON-
    # membership most carefully — rev_gender's "gender is not a UK GDPR Article 9 category",
    # rev_hearaboutus, rev_review.rev_notes1, and the five *redacted counterparts that cite their
    # Article 9 SOURCE. Better documentation, more findings: the polarity IMP-0422/IMP-0428 record,
    # now measured a sixth time. IsSecured alone → 52 findings, 1 true positive (2%).
    # REV_TrusteeRestricted membership → 36, 1 (3%), and that fails for a stated reason: the
    # profile's own description releases "the Tier 4 identifying AND special-category columns".
    #
    # So this asserts on VALUES against an ENUMERATED corpus, fail-closed. Per IMP-0560, the corpus
    # was enumerated BEFORE the set was chosen: 68 secured attributes, 17 registered, 51 pending.
    # Day-one findings: 0, and 0 is correct because the set IS the measured corpus. The first newly
    # secured column after that produces exactly one true finding, by name.
    pending_raw = register.get("pending_adjudication") or []
    pending_keys: set[tuple[str, str]] = set()
    for entry in pending_raw:
        if not isinstance(entry, dict):
            errors.append(f"register 'pending_adjudication' row {entry!r} is not a mapping; "
                          f"expected {{entity: ..., name: ...}}.")
            continue
        entity = str(entry.get("entity") or "").strip()
        name = str(entry.get("name") or "").strip().lower()
        if not entity or not name:
            errors.append(f"register 'pending_adjudication' row {entry!r}: 'entity' and 'name' "
                          f"are both required.")
            continue
        if (entity, name) in registered_keys:
            errors.append(
                f"C-DOM-033 — {entity}.{name} is in BOTH 'columns:' and "
                f"'pending_adjudication:'. A column is either adjudicated as special-category or "
                f"awaiting adjudication, never both — two lists that overlap are one list nobody "
                f"maintains. Remove it from 'pending_adjudication:'."
            )
            continue
        if (entity, name) not in attributes:
            errors.append(
                f"C-DOM-033 — {entity}.{name} is in 'pending_adjudication:' but does not exist "
                f"in {args.solution_root}/Entities/{entity}/Entity.xml. Delete the row: an "
                f"adjudication debt against a column that is gone is noise that makes the real "
                f"debt harder to see."
            )
            continue
        pending_keys.add((entity, name))

    unadjudicated = sorted(
        (entity, name) for (entity, name), meta in attributes.items()
        if meta["secured"] == "1"
        and (entity, name) not in registered_keys
        and (entity, name) not in pending_keys
    )
    for entity, name in unadjudicated:
        errors.append(
            f"C-DOM-033 — {entity}.{name} carries <IsSecured>1</IsSecured> and appears in "
            f"NEITHER 'columns:' nor 'pending_adjudication:' in {args.register}. Somebody decided "
            f"this column needs column-level security; nothing records whether it is UK GDPR "
            f"Article 9 special-category data. Decide, then declare it: add it to 'columns:' with "
            f"a basis (and to the '{FR016_STEP}' alternation), or to 'pending_adjudication:' if "
            f"the call belongs to the Domain Owner. Do not leave it in neither — that silence is "
            f"exactly how rev_ethnicgroup stayed unregistered for eight days (IMP-0598)."
        )

    secured_total = sum(1 for meta in attributes.values() if meta["secured"] == "1")

    # ── Report-only: attributes with auditing off, so a silence is a visible decision ───
    for (entity, name), meta in sorted(attributes.items()):
        if (entity, name) in registered_keys:
            continue
        if meta["audit"] is not None and meta["audit"] != "1":
            notes.append(f"{entity}.{name} has <IsAuditEnabled>{meta['audit']}</IsAuditEnabled>")

    for note in notes:
        print(f"NOTE: auditing is off — {note}", file=sys.stderr)
    if notes:
        print(f"NOTE: {len(notes)} attribute(s) above are outside the special-category "
              f"register, so this gate does not fail on them. They are printed so the "
              f"exclusion is a decision, not a silence.", file=sys.stderr)

    # C-DOM-033's pending count is printed on BOTH paths, and before the verdict. A figure that is
    # computed and then discarded on the PASS branch is the defect IMP-0511 records: the register's
    # adjudication debt must be visible on every green run, or it becomes invisible the moment it
    # stops failing.
    if pending_keys:
        print(f"NOTE: C-DOM-033 — {len(pending_keys)} secured column(s) are enumerated in "
              f"'pending_adjudication:' in {args.register}: column-secured, Article 9 status NOT "
              f"yet adjudicated by the Domain Owner / Compliance Lead. This is a DEBT, not a "
              f"clearance (IMP-0598). Discharge a row by deciding it, then moving or deleting it.",
              file=sys.stderr)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nDOMAIN INVARIANTS: FAILED — {len(errors)} violation(s) across "
              f"{len(columns)} registered column(s) and {secured_total} secured column(s).",
              file=sys.stderr)
        return 1

    print(f"DOMAIN INVARIANTS: PASS — {checked} special-category column(s) verified.")
    print(f"  C-DOM-033 secured-column coverage: {secured_total} secured "
          f"= {secured_total - len(pending_keys)} registered + {len(pending_keys)} pending "
          f"adjudication, 0 undeclared")
    print(f"  C-DOM-030 register ↔ FR-016 gate:  "
          f"{'in sync (' + str(alternation_size) + ' names)' if alternation_size is not None else 'not cross-checked (no --build-config)'}")
    print(f"  C-DOM-031 column security:         "
          f"{checked - len(exceptions)} secured, {len(exceptions)} documented exception(s)")
    print(f"  C-DOM-032 auditing:                {checked} / {checked} enabled")
    for name, reason in exceptions:
        print(f"    exception — {name}: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
