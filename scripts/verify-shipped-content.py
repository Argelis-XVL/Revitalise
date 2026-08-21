#!/usr/bin/env python3
"""Assert that shipped solution content is REACHABLE and CONSISTENT, not merely well-formed.

WHY THIS EXISTS. This project has a class of defect called `no-assertion-on-shipped-content`,
recorded four times. Every instance is the same shape: a component that packs cleanly, imports
cleanly, passes every structural gate — and is still wrong or unusable when a human looks at it.

  IMP-0052  rev_grant shipped with a main form and three saved queries and NO SubArea in the
            app's site map. Nothing could navigate to any of it. `forms-and-views-reachable`
            passed, because it asks whether the PACKER will keep the form — a different
            question from whether a PERSON can reach it. Confirmed by the reviewer on
            2026-08-19 as a real defect: "the grant table and views/forms should have been
            available in the model driven app."

  IMP-0008  A shipped <Description> still named `rev_carersupport`, a column deleted in the
            same build. Prose inside metadata is shipped content too, and nothing reads it.

  IMP-0015  Eleven scored-answer fields carried generic form labels ("Wellbeing Answer 1")
            instead of the real survey questions. Structurally perfect, semantically wrong.

ONE GATE, NOT THREE. `skills/how-to-promote-a-finding.md` §2 forbids giving the fourth instance
of a class its own instance patch. Checks 1 and 2 below are implemented; check 3 is declared
and NOT silently omitted — see NOT_YET_IMPLEMENTED at the bottom of this docstring.

WHAT IT CHECKS.

  1. NAVIGABILITY (IMP-0052) — every entity that ships a FormXml/ or SavedQueries/ folder
     appears as a SubArea in at least one AppModuleSiteMap, unless the entity is listed in
     `headless_entities` in the shapes file. Adding a table is TWO changes; this is the second.

  2. NO DANGLING COLUMN REFERENCES (IMP-0008) — no <Description> or <displayname> text
     anywhere in the solution names a `<prefix>_` column that does not exist in any Entity.xml.
     Prose in metadata ships to the environment and is read by makers.

  3. FORM LABELS MATCH THE COLUMN (IMP-0015) — every form control's label matches the
     `displayname` its own attribute declares in Entity.xml. The precedence rule, from the
     reviewer on 2026-08-19: **the column name is leading, but it can be altered if necessary.**
     So a difference is permitted and must be DECLARED — an undeclared difference fails.

     That distinction is the whole check. IMP-0015's defect was eleven scored-answer fields
     carrying "Wellbeing Answer 1" instead of the real survey question: nobody chose those
     labels, they were left over. A deliberate shortening of a long column name is fine; a label
     nobody decided is the bug. Declare an override with `--allow-label-override
     entity.column="the label"`, or in `form_label_overrides` in the shapes file.

Run:
    python3 scripts/verify-shipped-content.py src/solutions/RevitaliseGrantAutomation

Exits 0 when clean, 1 on any violation, 2 on a usage error. Fails — never passes — when the
solution root has no entities or no site map, so it cannot report OK over nothing (IMP-0007).

Wired into config/<slug>-build.yml as the `shipped-content` step.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Entities that legitimately have no navigation. Kept here rather than in a separate file
# because it is two lines and belongs beside the check that reads it; promote it to the
# shapes file if it ever grows past a handful.
HEADLESS_ENTITIES: set[str] = set()

COLUMN_REF = re.compile(r"\b(rev_[a-z0-9]+)\b")


def entities_with_ui(solution_root: Path) -> dict[str, list[str]]:
    """entity -> the UI folders it ships (FormXml, SavedQueries)."""
    found: dict[str, list[str]] = {}
    for entity_dir in sorted(Path(solution_root, "Entities").glob("*")):
        if not entity_dir.is_dir():
            continue
        kinds = []
        for kind in ("FormXml", "SavedQueries"):
            sub = entity_dir / kind
            if sub.is_dir() and any(sub.rglob("*.xml")):
                kinds.append(kind)
        if kinds:
            found[entity_dir.name] = kinds
    return found


def sitemap_entities(solution_root: Path) -> tuple[set[str], int]:
    """Every entity referenced by a SubArea, across every app module site map."""
    referenced: set[str] = set()
    maps = sorted(Path(solution_root, "AppModuleSiteMaps").rglob("*.xml"))
    for path in maps:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for sub in root.iter("SubArea"):
            entity = sub.get("Entity")
            if entity:
                referenced.add(entity.strip())
            # A SubArea may reach an entity only through a Url= querystring.
            url = sub.get("Url") or ""
            for match in re.finditer(r"etn=([a-z0-9_]+)", url):
                referenced.add(match.group(1))
    return referenced, len(maps)


def saved_query_ids(solution_root: Path) -> dict[str, set[str]]:
    """entity logical name -> the savedqueryid GUIDs it ships, normalised."""
    found: dict[str, set[str]] = {}
    entities = Path(solution_root, "Entities")
    if not entities.is_dir():
        return found
    for entity_dir in sorted(p for p in entities.iterdir() if p.is_dir()):
        ids: set[str] = set()
        for path in sorted(Path(entity_dir, "SavedQueries").glob("*.xml")):
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"<savedqueryid>([^<]+)</savedqueryid>", text):
                ids.add(normalise_guid(match.group(1)))
        if ids:
            found[entity_dir.name] = ids
    return found


def normalise_guid(raw: str) -> str:
    """Three encodings of the same viewid ship in this repo's site map today: URL-encoded
    braces (%7b..%7d), literal braces ({..}) and bare. They are the same view, and a check
    that compares them literally would report two false failures (IMP-0091)."""
    g = raw.strip().lower()
    for junk in ("%7b", "%7d", "{", "}"):
        g = g.replace(junk, "")
    return g


def sitemap_subareas(solution_root: Path) -> list[tuple[str, str, str, str]]:
    """(site map path, SubArea Id, Entity attribute or '', Url attribute or '')."""
    out: list[tuple[str, str, str, str]] = []
    for path in sorted(Path(solution_root, "AppModuleSiteMaps").rglob("*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for sub in root.iter("SubArea"):
            out.append((os.path.relpath(path), sub.get("Id") or "(no Id)",
                        (sub.get("Entity") or "").strip(), (sub.get("Url") or "").strip()))
    return out


def app_module_tables(solution_root: Path) -> tuple[dict[str, set[str]], int]:
    """app unique name -> the entity schema names it lists as AppModuleComponent type="1".

    Added 2026-08-19 (IMP-0090, blocker). A model-driven app renders the tables in ITS OWN
    component list. The site map only lays out what the app already contains. rev_grant had a
    site-map group and three sub-areas and was still invisible to every user, because
    AppModule.xml listed four tables and rev_grant was not one of them — its comment still read
    "The four Phase 1 tables".

    The symptom is the reason this is worth a gate: the table appears in the app designer's EDIT
    mode, which reads the site map, and is absent in PLAY mode, which reads this list. It
    survives a hard cache refresh. It reads exactly like a platform caching bug.
    """
    apps: dict[str, set[str]] = {}
    paths = sorted(Path(solution_root, "AppModules").rglob("AppModule.xml"))
    for path in paths:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        name = path.parent.name
        tables: set[str] = set()
        for comp in root.iter("AppModuleComponent"):
            if (comp.get("type") or "").strip() == "1":
                schema = (comp.get("schemaName") or "").strip()
                if schema:
                    tables.add(schema)
        apps[name] = tables
    return apps, len(paths)

def attribute_labels(solution_root: Path) -> dict[str, str]:
    """entity.column -> the displayname the attribute itself declares. The authority (IMP-0015)."""
    out: dict[str, str] = {}
    for path in sorted(Path(solution_root, "Entities").glob("*/Entity.xml")):
        entity = path.parent.name.lower()
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for attribute in root.iter("attribute"):
            name = (attribute.findtext("LogicalName")
                    or attribute.get("PhysicalName") or "").strip().lower()
            if not name:
                continue
            label = ""
            for dn in attribute.iter("displaynames"):
                for d in dn.iter("displayname"):
                    if (d.get("languagecode") or "1033") == "1033":
                        label = (d.get("description") or "").strip()
                        break
            if not label:
                label = (attribute.findtext("displayname") or "").strip()
            if label:
                out[f"{entity}.{name}"] = label
    return out


def form_control_labels(solution_root: Path) -> list[tuple[str, str, str, str]]:
    """(entity, column, label, form file) for every labelled, data-bound control on a form."""
    found: list[tuple[str, str, str, str]] = []
    for form in sorted(Path(solution_root, "Entities").glob("*/FormXml/**/*.xml")):
        entity = form.parts[form.parts.index("Entities") + 1].lower()
        try:
            root = ET.parse(form).getroot()
        except ET.ParseError:
            continue
        for cell in root.iter("cell"):
            label = ""
            for lab in cell.iter("label"):
                if (lab.get("languagecode") or "1033") == "1033":
                    label = (lab.get("description") or "").strip()
                    break
            if not label:
                continue
            for ctrl in cell.iter("control"):
                col = (ctrl.get("datafieldname") or "").strip().lower()
                if col:
                    found.append((entity, col, label, str(form)))
    return found


def declared_columns(solution_root: Path) -> set[str]:
    columns: set[str] = set()
    for path in sorted(Path(solution_root, "Entities").glob("*/Entity.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for attribute in root.iter("attribute"):
            name = (attribute.findtext("LogicalName")
                    or attribute.get("PhysicalName") or "").strip().lower()
            if name:
                columns.add(name)
    return columns


# The multi-line text control. A cell bound to it renders as a fixed-height box unless the
# CELL (not the control) carries auto="true" - "Use all available vertical space" in the
# maker portal (IMP-0127). Ground-truthed 2026-08-21 by reading the reviewer's own
# maker-portal edit back out of DEV with `pac org fetch` on `systemform.formxml`.
MULTILINE_TEXT_CONTROL = "{E0DECE4B-6FC8-4a8f-A065-082708572369}"


def multiline_cells_missing_auto(solution_root: Path) -> list[tuple[str, str, str]]:
    """(form path, cell id, column) for every multi-line text control cell without auto="true"."""
    missing: list[tuple[str, str, str]] = []
    for form in sorted(Path(solution_root, "Entities").glob("*/FormXml/**/*.xml")):
        try:
            root = ET.parse(form).getroot()
        except ET.ParseError:
            continue
        for cell in root.iter("cell"):
            for ctrl in cell.iter("control"):
                classid = (ctrl.get("classid") or "").strip()
                if classid.lower() != MULTILINE_TEXT_CONTROL.lower():
                    continue
                auto = (cell.get("auto") or "").strip().lower()
                if auto != "true":
                    missing.append((str(form), cell.get("id") or "(no id)",
                                    (ctrl.get("datafieldname") or "").strip()))
    return missing


# Every nvarchar/ntext column in this solution above this length already declares
# Format=textarea; every one at or below it is a genuinely short single-line field (a name, an
# email, a postcode, an address line). Derived from source on 2026-08-21 (IMP-0128) — the
# boundary is where the data actually splits, not an imported number.
LONG_TEXT_THRESHOLD = 250


def long_text_columns_missing_textarea(solution_root: Path) -> list[tuple[str, str, int, str]]:
    """(entity, column, length, format) for a long text column whose Format is not textarea."""
    problems: list[tuple[str, str, int, str]] = []
    for path in sorted(Path(solution_root, "Entities").glob("*/Entity.xml")):
        entity = path.parent.name
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for attribute in root.iter("attribute"):
            typ = (attribute.findtext("Type") or "").strip()
            if typ not in ("nvarchar", "ntext"):
                continue
            length_text = attribute.findtext("Length") or attribute.findtext("MaxLength")
            if not length_text or not length_text.isdigit():
                continue
            length = int(length_text)
            fmt = (attribute.findtext("Format") or "").strip().lower()
            if length > LONG_TEXT_THRESHOLD and fmt != "textarea":
                name = (attribute.findtext("LogicalName")
                        or attribute.get("PhysicalName") or "").strip()
                problems.append((entity, name, length, fmt or "(none)"))
    return problems


# A verb this gate cannot resolve to a real mechanism is a promise the flow cannot keep
# (IMP-0139). "Complete the missing answers... and re-run scoring" shipped for a flow that is
# create-triggered only and reads every answer from triggerOutputs() — the only thing that
# looks like a re-run, Resubmit in the run history, replays the cached payload and reproduces
# the identical verdict. Scoped to create-only flows: a flow with a Request, Recurrence or
# update trigger may genuinely be re-run, so this only fires where the promise is provably empty.
UNBUILT_RECOVERY_VERBS = re.compile(r"\bre-?run\b|\bresubmit(ted|ting)?\b", re.IGNORECASE)


def _shipped_strings(node, skip_keys=("description", "$schema")):
    """Every string value in a flow definition, skipping developer-facing documentation keys.

    A flow's own `description` explains DESIGN INTENT to the next developer ("exists so the
    flow stays safe to re-run by hand") and is never shown to a user; only body/messageBody,
    item/<column> writes and similar action inputs ship. Walking everything except
    `description` is how check 2 above already draws this line for entity metadata prose.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key in skip_keys:
                continue
            yield from _shipped_strings(value, skip_keys)
    elif isinstance(node, list):
        for item in node:
            yield from _shipped_strings(item, skip_keys)
    elif isinstance(node, str):
        yield node


def prose_promising_an_unbuilt_rerun(solution_root: Path) -> list[tuple[str, str]]:
    """(flow file, matched fragment) for shipped prose telling a user to re-run/resubmit a
    flow that triggers on record CREATED only, with no other trigger giving it a real re-run
    path."""
    problems: list[tuple[str, str]] = []
    for flow in sorted(Path(solution_root).rglob("Workflows/*.json")):
        try:
            doc = json.loads(flow.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        triggers = doc.get("properties", {}).get("definition", {}).get("triggers", {}) or {}
        create_only = False
        for trigger in triggers.values():
            if trigger.get("type") != "OpenApiConnectionWebhook":
                continue
            message = (trigger.get("inputs", {}).get("parameters", {})
                       .get("subscriptionRequest/message"))
            if message in (1, "1"):
                create_only = True
        if not create_only:
            continue  # a Request/Recurrence/update trigger can genuinely be re-run
        actions = doc.get("properties", {}).get("definition", {}).get("actions", {}) or {}
        for value in _shipped_strings(actions):
            match = UNBUILT_RECOVERY_VERBS.search(value)
            if not match:
                continue
            start, end = max(0, match.start() - 50), min(len(value), match.end() + 50)
            problems.append((flow.name, value[start:end]))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solution_root", type=Path)
    parser.add_argument("--allow-headless", nargs="*", default=[],
                        help="entities that deliberately have no navigation")
    parser.add_argument("--cards", type=Path, default=None,
                        help="directory of readable Adaptive Card payloads that must match the "
                             "minified strings shipped in the flow definitions (IMP-0131)")
    parser.add_argument("--allow-label-override", nargs="*", default=[],
                        help="entity.column=\"the deliberate label\" — a declared difference "
                             "between a form label and its column's displayname")
    args = parser.parse_args(argv)

    if not args.solution_root.is_dir():
        print(f"shipped-content: FAILED — '{args.solution_root}' is not a directory. A gate "
              f"pointed at a missing target does not pass (IMP-0007).", file=sys.stderr)
        return 1

    errors: list[str] = []
    headless = HEADLESS_ENTITIES | {e.strip() for e in args.allow_headless if e.strip()}

    # ── 1. Navigability (IMP-0052) ──────────────────────────────────────────────────────
    ui = entities_with_ui(args.solution_root)
    if not ui:
        print(f"shipped-content: FAILED — no entity under '{args.solution_root}/Entities' "
              f"ships a FormXml/ or SavedQueries/ folder. A gate with no scannable surface "
              f"must fail rather than report OK (IMP-0007).", file=sys.stderr)
        return 1

    referenced, n_maps = sitemap_entities(args.solution_root)
    if n_maps == 0:
        errors.append(f"no AppModuleSiteMaps/**/*.xml found under '{args.solution_root}'. "
                      f"Every entity below would be trivially 'unreachable', so this gate "
                      f"refuses to guess.")
    else:
        for entity, kinds in sorted(ui.items()):
            if entity in headless or entity in referenced:
                continue
            errors.append(
                f"NAVIGABILITY — {entity} ships {' and '.join(kinds)} but appears in no "
                f"SubArea of any app site map, so nobody can reach it in the app. Adding a "
                f"table is FOUR changes: (1) the entity, (2) a SubArea in "
                f"AppModuleSiteMaps/, (3) an <AppModuleComponent type=\"1\"> in the app's "
                f"AppModule.xml, and (4) the table's audit switch IN THE ENVIRONMENT — which "
                f"is not in solution source and which no source-side gate can see "
                f"(IMP-0052, IMP-0060, IMP-0090, IMP-0085). This gate covers 1-3. If the "
                f"table is deliberately headless, pass it to --allow-headless with a reason "
                f"in the build config."
            )

    # ── 1b. The app must CONTAIN the table, not merely lay it out (IMP-0090) ─────────────
    apps, n_apps = app_module_tables(args.solution_root)
    if n_apps == 0:
        errors.append(f"no AppModules/**/AppModule.xml found under '{args.solution_root}'. If "
                      f"this solution ships a site map it must ship the app that uses it, and "
                      f"a gate that finds no app cannot report the tables reachable.")
    else:
        for app_name, tables in sorted(apps.items()):
            for entity in sorted(referenced):
                if entity in tables:
                    continue
                if entity in headless:
                    continue
                errors.append(
                    f"APP MEMBERSHIP — {entity} is referenced by a SubArea of the site map but "
                    f"is NOT an <AppModuleComponent type=\"1\"> in AppModules/{app_name}/"
                    f"AppModule.xml, so the app does not contain it and it will not render for "
                    f"a user. It WILL still appear in the app designer's edit mode, which reads "
                    f"the site map — that is what makes this look like a platform caching bug. "
                    f"Adding a table is FOUR changes: the entity, its SubArea, this component "
                    f"entry, and the audit switch in the environment. (IMP-0090 — this shipped, "
                    f"and the reviewer found it in play mode.)"
                )
            for entity in sorted(tables):
                if entity in referenced or entity in headless:
                    continue
                errors.append(
                    f"APP MEMBERSHIP — {entity} is an AppModuleComponent of "
                    f"AppModules/{app_name}/AppModule.xml but no SubArea of any site map "
                    f"references it, so it is in the app and unreachable from its navigation. "
                    f"Either give it a SubArea or pass it to --allow-headless with a reason."
                )

    # ── 1c. A SubArea Url is a URL, and a viewid it names must exist (IMP-0087, IMP-0091) ─
    # Three Url shapes shipped and satisfied the etn= check above while rendering nothing or
    # the wrong view: Entity= alongside Url="?pagetype=..." (opened the DEFAULT view),
    # Url="&pagetype=..." with no leading slash (written by the site-map DESIGNER itself, and
    # the sub-page did not render), and a viewid GUID in an encoding nothing resolved. The
    # existing gate reads etn= out of any string, so all three passed it.
    queries = saved_query_ids(args.solution_root)
    subareas = sitemap_subareas(args.solution_root)
    encodings: dict[str, int] = {}
    for map_path, sub_id, entity_attr, url in subareas:
        if not url:
            continue                      # an Entity= SubArea opens the default view; fine
        list_url = "pagetype=entitylist" in url
        if list_url and not (url.startswith("/") and "?" in url):
            errors.append(
                f"SUBAREA URL SHAPE — {map_path}: SubArea '{sub_id}' has "
                f"Url={url!r}. A SubArea Url is a URL, not a querystring to append: it must "
                f"begin with '/' and contain '?' (e.g. '/main.aspx?pagetype=entitylist&etn=..'). "
                f"Two other shapes have already shipped from here — one written by the site-map "
                f"designer itself — and neither rendered (IMP-0091)."
            )
        if list_url and entity_attr:
            errors.append(
                f"SUBAREA URL SHAPE — {map_path}: SubArea '{sub_id}' carries BOTH "
                f"Entity={entity_attr!r} and an entitylist Url. That combination opens the "
                f"table's DEFAULT view and silently ignores the view the Url names — it is how "
                f"five view-pinned sub-areas all opened the same list (IMP-0087). Use one or "
                f"the other: Entity= for the default view, Url= for a pinned view."
            )
        for raw in re.findall(r"viewid=([^&\"']+)", url):
            encodings[("braces" if "{" in raw or "%7b" in raw.lower() else "bare")] = \
                encodings.get("braces" if "{" in raw or "%7b" in raw.lower() else "bare", 0) + 1
            etn = re.search(r"etn=([a-z0-9_]+)", url)
            if not etn:
                errors.append(
                    f"SUBAREA URL SHAPE — {map_path}: SubArea '{sub_id}' pins a viewid but "
                    f"names no etn=, so nothing can say which entity's view it is.")
                continue
            entity = etn.group(1)
            have = queries.get(entity)
            if have is None:
                errors.append(
                    f"SUBAREA VIEW — {map_path}: SubArea '{sub_id}' pins a view on "
                    f"'{entity}', which ships no SavedQueries/ folder at all.")
            elif normalise_guid(raw) not in have:
                errors.append(
                    f"SUBAREA VIEW — {map_path}: SubArea '{sub_id}' pins viewid {raw!r} on "
                    f"'{entity}', and no SavedQuery in Entities/{entity}/SavedQueries/ has that "
                    f"savedqueryid. The sub-area will open something other than the list it is "
                    f"named after, and the packer accepts it (IMP-0087)."
                )

    # ── 2. No dangling column references in shipped prose (IMP-0008) ────────────────────
    columns = declared_columns(args.solution_root)
    if not columns:
        errors.append("no attributes found in any Entity.xml — cannot check shipped prose "
                      "for references to deleted columns.")
    else:
        for path in sorted(Path(args.solution_root).rglob("*.xml")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for element_name in ("Description", "description", "displayname", "DisplayName"):
                for match in re.finditer(
                        rf'<{element_name}[^>]*\b(?:description|default)="([^"]*)"', text):
                    prose = match.group(1)
                    for ref in set(COLUMN_REF.findall(prose)):
                        if ref.lower() in columns:
                            continue
                        # Entity and option-set names share the prefix; they are not columns.
                        if (Path(args.solution_root, "Entities", ref).is_dir()
                                or Path(args.solution_root, "OptionSets", ref + ".xml").is_file()):
                            continue
                        errors.append(
                            f"DANGLING REFERENCE — {os.path.relpath(path)}: shipped "
                            f"<{element_name}> prose names '{ref}', which is not a column in "
                            f"any Entity.xml, not an entity and not an option set. A "
                            f"description naming a deleted column ships to every environment "
                            f"and is read by makers (IMP-0008)."
                        )

    if errors:
        for error in sorted(set(errors)):
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nshipped-content: FAILED — {len(set(errors))} problem(s). These are defects "
              f"a packer and an import both accept.", file=sys.stderr)
        return 1

    # ── check 3: form labels against the column's own displayname (IMP-0015) ──────────────
    overrides: dict[str, str] = {}
    for spec in args.allow_label_override:
        key, _, val = spec.partition("=")
        if key.strip():
            overrides[key.strip().lower()] = val.strip().strip('"')

    authored = attribute_labels(args.solution_root)
    controls = form_control_labels(args.solution_root)
    label_problems: list[str] = []
    declared_diffs = 0
    for entity, col, label, form in controls:
        key = f"{entity}.{col}"
        expected = authored.get(key)
        if not expected or label == expected:
            continue
        if key in overrides and overrides[key] == label:
            declared_diffs += 1
            continue
        label_problems.append(
            f"form label {label!r} on {key} does not match the column's own displayname "
            f"{expected!r} ({form}). The column name is leading. If this difference is "
            f"deliberate, declare it: --allow-label-override '{key}=\"{label}\"'")

    if label_problems:
        print(f"shipped-content: FAILED — {len(label_problems)} form label(s) differ from their "
              f"column's authored name without being declared (IMP-0015).", file=sys.stderr)
        for problem in label_problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    # ── 4. A payload kept as a readable file is the payload that ships (IMP-0131) ───────
    # An Adaptive Card exists twice here: indented under docs/development/cards/ for review,
    # and minified inside a flow's body/messageBody. Editing either is a valid-JSON edit that
    # every other gate passes, so the two drift silently — and the same split has already put a
    # false statement in a shipped notes.md ("THIS IS NOT AN ADAPTIVE CARD", beside a flow that
    # had been posting one for a day). Ninth instance of `no-assertion-on-shipped-content`, so
    # it belongs in this gate rather than in a tenth script.
    cards_checked = 0
    if args.cards is not None:
        if not args.cards.is_dir():
            print(f"shipped-content: FAILED — --cards '{args.cards}' is not a directory. A "
                  f"declared surface that does not exist is not a surface (IMP-0007).",
                  file=sys.stderr)
            return 1
        card_files = sorted(args.cards.glob("*.json"))
        if not card_files:
            print(f"shipped-content: FAILED — --cards '{args.cards}' holds no *.json payloads.",
                  file=sys.stderr)
            return 1
        shipped: list[tuple[str, object]] = []
        for flow in sorted(args.solution_root.rglob("Workflows/*.json")):
            try:
                text = flow.read_text(encoding="utf-8")
            except OSError:
                continue
            for match in re.finditer(r'"body/messageBody"\s*:\s*("(?:[^"\\]|\\.)*")', text):
                try:
                    payload = json.loads(json.loads(match.group(1)))
                except (json.JSONDecodeError, ValueError):
                    continue  # an HTML message, not a card
                if isinstance(payload, dict) and payload.get("type") == "AdaptiveCard":
                    shipped.append((flow.name, payload))
        card_problems = []
        for card_file in card_files:
            try:
                readable = json.loads(card_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                card_problems.append(f"{card_file.name} is not readable JSON: {exc}")
                continue
            if not any(readable == payload for _, payload in shipped):
                card_problems.append(
                    f"{card_file.name} matches no AdaptiveCard shipped in any flow definition. "
                    f"The readable file and the minified string in body/messageBody have "
                    f"drifted, and the reviewer is reading the one that does not ship "
                    f"(IMP-0131).")
            else:
                cards_checked += 1
        if len(shipped) > len(card_files):
            card_problems.append(
                f"{len(shipped)} AdaptiveCard(s) ship in the flow definitions but only "
                f"{len(card_files)} readable payload(s) exist under {args.cards}. A card with "
                f"no readable file is a card nobody reviews.")
        if card_problems:
            print(f"shipped-content: FAILED — {len(card_problems)} card payload problem(s) "
                  f"(IMP-0131).", file=sys.stderr)
            for problem in card_problems:
                print(f"  {problem}", file=sys.stderr)
            return 1

    # ── 5. Every multi-line text cell asks for the space it needs (IMP-0127) ────────────
    multiline_problems = multiline_cells_missing_auto(args.solution_root)
    if multiline_problems:
        print(f"shipped-content: FAILED — {len(multiline_problems)} multi-line text cell(s) "
              f"without auto=\"true\" (IMP-0127).", file=sys.stderr)
        for form, cell_id, col in multiline_problems:
            print(f"  {form}: cell {cell_id} ({col}) — set auto=\"true\", the cell's own "
                  f"attribute, not the control's", file=sys.stderr)
        return 1

    # ── 6. A long text column declares the format that lets it grow (IMP-0128) ──────────
    long_text_problems = long_text_columns_missing_textarea(args.solution_root)
    if long_text_problems:
        print(f"shipped-content: FAILED — {len(long_text_problems)} text column(s) over "
              f"{LONG_TEXT_THRESHOLD} characters without Format=textarea (IMP-0128).",
              file=sys.stderr)
        for entity, col, length, fmt in long_text_problems:
            print(f"  {entity}.{col}: {length} chars, Format={fmt}. No type change and no "
                  f"form change needed — set Format to textarea on the column.",
                  file=sys.stderr)
        return 1

    # ── 7. Shipped prose promises no capability the solution does not have (IMP-0139) ───
    rerun_problems = prose_promising_an_unbuilt_rerun(args.solution_root)
    if rerun_problems:
        print(f"shipped-content: FAILED — {len(rerun_problems)} instance(s) of shipped prose "
              f"telling a user to re-run/resubmit a flow that triggers on record CREATED only "
              f"(IMP-0139).", file=sys.stderr)
        for flow_name, fragment in rerun_problems:
            print(f"  {flow_name}: …{fragment}… — Resubmit in the run history "
                  f"replays the cached trigger payload; it is not a re-run. Name the FR-018 "
                  f"override path instead, or give the flow a real re-run trigger first.",
                  file=sys.stderr)
        return 1

    print(f"shipped-content: OK — {len(ui)} entity(ies) with UI, all reachable across "
          f"{n_maps} site map(s); shipped prose references only columns that exist; "
          f"{len(controls)} form label(s) checked against their column's authored name.")
    pinned = sum(encodings.values())
    if pinned:
        print(f"  {pinned} view-pinned SubArea Url(s) checked; every viewid resolves to a "
              f"SavedQuery of the entity it names")
        if len(encodings) > 1:
            print(f"  NOTE — {len(encodings)} different viewid encodings in use "
                  f"({', '.join(f'{k}={v}' for k, v in sorted(encodings.items()))}). All "
                  f"resolve, so this does not fail; pick one before it looks like a rule.")
    if headless:
        print(f"  deliberately headless: {', '.join(sorted(headless))}")
    if declared_diffs:
        print(f"  declared label overrides honoured: {declared_diffs}")
    if cards_checked:
        print(f"  {cards_checked} Adaptive Card payload(s) match the string shipped in the flow "
              f"definition, byte for byte after parsing")
    print(f"  multi-line text cells: all carry auto=\"true\"; long text columns: none over "
          f"{LONG_TEXT_THRESHOLD} chars without Format=textarea; no create-only flow promises "
          f"a re-run it cannot perform")
    return 0


if __name__ == "__main__":
    sys.exit(main())
