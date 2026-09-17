#!/usr/bin/env python3
"""Every source class in docs/Import/MANIFEST.yml maps to a checklist that actually exists.

WHY THIS EXISTS (IMP-0726, IMP-0739 — the FIFTH and SIXTH instances of one class). A document
supplied by the client can be dropped into `docs/Import/` at any time. `MANIFEST.yml` records
who adopts each one (`intaked_by`), and `skills/how-to-intake-external-documents.md` holds the
checklists they work from. Nothing connected the two, so a source could be registered, owned,
and still match no checklist — which is not an error anyone sees, it is SILENCE.

The four prior fixes each added an OWNER for a directory or an artefact and no CHECKLIST for a
kind of content:

  IMP-0028  a WBS quoting workbook, cited by a plan as the basis of its own estimate
  IMP-0384  a design system arriving in a directory named nowhere at all
  IMP-0510  a third artefact, same shape
  IMP-0726  client review feedback on a delivered surface — registered, owned, no checklist
  IMP-0739  the covering EMAIL BODY carrying two lists that were in none of its attachments

The altitude rule forbids a fifth instance patch, so this is the mechanical form of
IMP-0726's own `why_it_was_never_caught`, verbatim: *nothing asserts that every `class` value
used in docs/Import/MANIFEST.yml resolves to a checklist in the skill its `intaked_by` agent
loads.*

WHAT IT CHECKS:

  (a) every `class` in MANIFEST.yml appears in the skill's "Which checklist a source class maps
      to" table. A class with no row is a kind of input nobody has decided how to read.
  (b) every checklist NAMED in that table exists as a heading in the skill. A mapping pointing
      at a checklist that was renamed or never written is the same silence one step further in.
  (c) every file in docs/Import/ has a MANIFEST entry. An unregistered source is
      indistinguishable from an absent one — the manifest's own stated purpose.

FAIL-CLOSED, SO THE CORPUS WAS ENUMERATED BEFORE THE SET WAS CHOSEN (IMP-0560). The manifest
declares exactly four classes today — contractual, requirements, compliance, data-sample — and
the skill's table was written to cover those four, not guessed at.

`none` is a legal and meaningful value: it means the class is reference material nobody adopts.
A DECLARED none is distinguishable from a class nobody considered, which is the entire point.

Run:
    python3 scripts/verify-import-manifest-intake.py
    python3 scripts/verify-import-manifest-intake.py --selftest

Wired into config/<slug>-build.yml as the SOFT (--warn-only) step `import-manifest-intake`.
SOFT because check (c) opens with real findings against files this dispatch does not own
(IMP-0439, IMP-0491); (a) and (b) open green.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "docs/Import/MANIFEST.yml"
DEFAULT_SKILL = REPO_ROOT / "skills/how-to-intake-external-documents.md"
MAP_HEADING = "## Which checklist a source class maps to"

_CLASS = re.compile(r"^\s*class:\s*(\S+)\s*$", re.M)
_NAME = re.compile(r'^\s*-\s*name:\s*"([^"]+)"\s*$', re.M)
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.M)
_MAProw = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", re.M)
_TICKED = re.compile(r"`([^`]+)`")


def manifest_classes(text: str) -> set[str]:
    return {c.strip().strip('"\'') for c in _CLASS.findall(text)}


def manifest_names(text: str) -> set[str]:
    return set(_NAME.findall(text))


def skill_headings(text: str) -> set[str]:
    return {h.strip() for h in _HEADING.findall(text)}


def declared_map(text: str) -> dict[str, list[str]]:
    """class -> the checklists it maps to, read from the skill's own table."""
    start = text.find(MAP_HEADING)
    if start == -1:
        return {}
    end = text.find("\n## ", start + len(MAP_HEADING))
    block = text[start: end if end != -1 else len(text)]
    mapping: dict[str, list[str]] = {}
    for cls, targets in _MAProw.findall(block):
        if cls.strip() == "class":
            continue
        mapping[cls.strip()] = [t.strip() for t in _TICKED.findall(targets)]
    return mapping


def check(manifest: Path, skill: Path, import_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not manifest.is_file():
        return ([f"{manifest} does not exist. A gate pointed at a missing target must fail, "
                 f"not pass (IMP-0007)."], [])
    if not skill.is_file():
        return ([f"{skill} does not exist, so no class can resolve to a checklist."], [])

    m_text = manifest.read_text(encoding="utf-8")
    s_text = skill.read_text(encoding="utf-8")

    mapping = declared_map(s_text)
    if not mapping:
        return ([f"{skill} carries no '{MAP_HEADING}' table, so nothing states which checklist "
                 f"a source class maps to. That table is this gate's source of truth and a "
                 f"missing one must fail rather than pass every class (IMP-0007)."], [])

    headings = skill_headings(s_text)

    # (a) every manifest class is mapped
    for cls in sorted(manifest_classes(m_text)):
        if cls not in mapping:
            errors.append(
                f"{manifest}: source class '{cls}' appears in no row of '{MAP_HEADING}' in "
                f"{skill.name}. A class nobody has mapped is a kind of supplied input with an "
                f"owner and no procedure — which fails SILENTLY, because the source is "
                f"registered and simply never read (IMP-0028, IMP-0384, IMP-0510, IMP-0726).\n"
                f"    → add a checklist for it, or add a row mapping it to `none` if it is "
                f"reference material nobody adopts. A declared `none` is the point."
            )

    # (b) every mapped checklist exists
    for cls, targets in sorted(mapping.items()):
        for target in targets:
            if target == "none":
                continue
            if target not in headings:
                errors.append(
                    f"{skill.name}: class '{cls}' maps to checklist '{target}', which is not a "
                    f"heading in this file. The mapping points at nothing, so the class reads "
                    f"as covered while no procedure exists.\n"
                    f"    → fix the heading name in the table, or write the checklist."
                )

    # (c) every file in docs/Import has an entry
    if import_dir.is_dir():
        registered = manifest_names(m_text)
        for path in sorted(import_dir.iterdir()):
            if not path.is_file() or path.name == manifest.name:
                continue
            if path.name not in registered:
                warnings.append(
                    f"{import_dir}/{path.name} has no entry in {manifest.name}, so it names no "
                    f"owning agent and no class. An unregistered source is indistinguishable "
                    f"from an absent one, which is the failure the manifest exists to prevent."
                )

    return errors, warnings


def render(errors: list[str], warnings: list[str], warn_only: bool) -> tuple[str, int]:
    lines = [f"ERROR: {e}" for e in errors] + [f"WARNING: {w}" for w in warnings]
    if not lines:
        return ("import-manifest-intake: OK — every source class in docs/Import/MANIFEST.yml "
                "maps to a checklist that exists, and every file in docs/Import/ is registered. "
                "NOT covered: whether a checklist is any good, only that one exists.", 0)
    lines.append(
        f"\nverify-import-manifest-intake: "
        f"{'FAILED (SOFT — report as WARN, do not block)' if warn_only else 'FAILED'} — "
        f"{len(errors)} unmapped/dangling class(es), {len(warnings)} unregistered file(s).")
    return "\n".join(lines), 0 if warn_only else (1 if errors or warnings else 0)


def selftest() -> int:
    skill = """
## Alpha Checklist (pm-agent)
text
## Which checklist a source class maps to

| class | checklist |
|---|---|
| `contractual` | `Alpha Checklist (pm-agent)` |
| `compliance` | `none` |

## Next
"""
    mapping = declared_map(skill)
    assert mapping == {"contractual": ["Alpha Checklist (pm-agent)"], "compliance": ["none"]}, mapping
    assert "Alpha Checklist (pm-agent)" in skill_headings(skill)

    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "docs").mkdir()
        imp = d / "docs" / "Import"; imp.mkdir()
        man = imp / "MANIFEST.yml"
        sk = d / "skill.md"
        sk.write_text(skill, encoding="utf-8")

        # clean: both classes mapped, both files registered
        man.write_text('files:\n  - name: "a.md"\n    class: contractual\n', encoding="utf-8")
        (imp / "a.md").write_text("x", encoding="utf-8")
        e, w = check(man, sk, imp)
        assert not e and not w, (e, w)
        assert render(e, w, False)[1] == 0

        # (a) an unmapped class must FAIL
        man.write_text('files:\n  - name: "a.md"\n    class: mystery\n', encoding="utf-8")
        e, w = check(man, sk, imp)
        assert any("appears in no row" in x for x in e), e
        assert render(e, w, False)[1] == 1, "a gate that cannot fail is not a gate"
        assert render(e, w, True)[1] == 0, "--warn-only must not block"

        # (b) a dangling checklist name must FAIL
        sk.write_text(skill.replace("`Alpha Checklist (pm-agent)`", "`Ghost Checklist (pm-agent)`"),
                      encoding="utf-8")
        man.write_text('files:\n  - name: "a.md"\n    class: contractual\n', encoding="utf-8")
        e, w = check(man, sk, imp)
        assert any("is not a heading" in x for x in e), e
        sk.write_text(skill, encoding="utf-8")

        # (c) an unregistered file must WARN
        (imp / "orphan.docx").write_text("x", encoding="utf-8")
        e, w = check(man, sk, imp)
        assert any("orphan.docx" in x for x in w), w

        # a missing map table must FAIL, never pass every class
        sk.write_text("## Alpha Checklist (pm-agent)\n", encoding="utf-8")
        e, w = check(man, sk, imp)
        assert any("carries no" in x for x in e), e

    print("verify-import-manifest-intake --selftest: OK — unmapped class, dangling checklist, "
          "unregistered file and missing map table all fire; a clean corpus exits 0; "
          "--warn-only exits 0 while still reporting.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    ap.add_argument("--import-dir", type=Path, default=None)
    ap.add_argument("--warn-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    import_dir = args.import_dir or args.manifest.parent
    errors, warnings = check(args.manifest, args.skill, import_dir)
    text, rc = render(errors, warnings, args.warn_only)
    print(text, file=sys.stderr if rc or errors or warnings else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
