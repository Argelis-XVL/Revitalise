#!/usr/bin/env python3
"""A create-only provisioning step cannot converge, and C-TECH-042 could not tell the
difference. This gate makes each step say which it is.

Usage:
    verify-provisioning-step-convergence.py [<repo-root>]
    verify-provisioning-step-convergence.py --selftest

WHY THIS EXISTS. `IMP-0259`, a blocker, and the expensive part was not the defect but its
shape. `ensure-schema.ps1`'s relationship step is create-only: an existing relationship reports
`EXISTS` and is skipped, so `ConvertTo-RevRelationshipBody` is never called for it again. When
that function was fixed to carry `IsSecured`, the fix reached only environments where the
relationship did not yet exist. In DEV all five already existed, so five Tier 4 columns would
have stayed unsecured **forever**, while a fresh PRD came up correct on its first pass. Same
source, same script, two environments with different security, every gate green.

`C-TECH-042` requires provisioning scripts to be idempotent — "check-before-create, safe to
re-run". A create-only step satisfies that wording completely while being unable to converge.
Idempotency and convergence are not the same property, and nothing in the repository recorded
which steps had which.

WHAT THIS CHECKS. Every numbered step (`# -- <n>. ...`) in every `provisioning/**/*.ps1` is
classified from its own code:

  * writes nothing                    → READ-ONLY, nothing to declare.
  * issues a PATCH or a full-object   → RECONCILES. Either can correct an existing component.
    PUT                                 Dataverse's metadata endpoints (EntityDefinitions,
                                        Attributes) require PUT for updates PATCH does not
                                        support at all (IMP-0272/IMP-0273) — a PUT that
                                        replaces the fetched object wholesale converges a
                                        property exactly as much as a PATCH that sets it alone.
  * issues only a create              → CREATE-ONLY, and it must carry a CONVERGENCE
                                        declaration in its own comment region.

The declaration grammar, one line anywhere in the step's comments:

    # CONVERGENCE: immutable -- <why nothing about this component can be corrected later>
    # CONVERGENCE: reconciled by step <id> -- <which properties that step converges>
    # CONVERGENCE: no source-declared properties -- <why this step's writes carry nothing
    #                                                from source that could later change>
    # CONVERGENCE: UNRESOLVED -- owner:<agent>, <what has to be decided>

Outcomes, and the asymmetry is the point:

  * a create-only step with NO declaration        → FAIL. Silence is what cost five columns.
  * `reconciled by step X` where X does not exist → FAIL. A forward reference to nothing is
                                                    the `evidence-rule-satisfied-by-a-
                                                    forward-reference` class (IMP-0067).
  * `immutable` on a step that does PATCH/PUT     → FAIL. The claim contradicts the code.
  * `UNRESOLVED`                                  → WARN, every run, naming the owner.
  * a script that writes but has no numbered steps → WARN, listed by name. It cannot be
                                                    classified and must not read as a pass
                                                    (IMP-0007).

WHY UNRESOLVED IS A WARNING AND ABSENCE IS A FAILURE. Whether a given component's properties
can be corrected in a later run is a real Dataverse question, and several of these steps need a
judgement this gate has no business making. What the gate can insist on is that the question has
been *asked in writing* and has an owner. An honest UNRESOLVED beats a guess (`IMP-0224`), and
both beat silence.

RESIDUAL, stated because it is not covered. Classification is textual: it reads the step's own
region for create/reconcile call shapes listed in CREATE_CALLS and PATCH_CALLS (the latter now
matches PUT too — see PATCH_CALLS' own comment). A step that reaches the platform through a
helper this gate does not know about classifies as READ-ONLY and is skipped — so a new call
helper must be added here. It also cannot verify that a `reconciled by step X` claim is TRUE: it
checks the step exists and reconciles, not that it converges the same properties this step
creates. That last rung is `verify-declared-property-reaches-creation-path.py`'s neighbour and
does not exist.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

# Every shape in this repository that creates a component, and every shape that corrects one.
# Adding a call helper means adding it here — see the residual note in the module docstring.
CREATE_CALLS = r"-Method\s+POST|Invoke-RevSolutionPost|Invoke-RevPost"
# PUT added 2026-08-24 (IMP-0272/IMP-0273): a metadata PATCH against Dataverse's Attributes
# collection is rejected outright ("does not support http method 'PATCH'") — the documented
# shape for updating column/entity metadata is a full-object PUT. ensure-schema.ps1 step 3b
# reconciles lookup IsSecured this way. A PUT that replaces the whole fetched object corrects
# an existing component exactly as a PATCH does, so it must classify as RECONCILES too, or this
# gate would demand step 3b declare itself CREATE-ONLY — false, and the class this whole gate
# exists to catch (IMP-0259) restated one call shape later.
PATCH_CALLS = r"-Method\s+(?:PATCH|PUT)|Invoke-RevPatch"

STEP_MARKER = re.compile(r"(?m)^# ── (.+?) ─*$")
NUMBERED = re.compile(r"^(\d+[a-z]?)\.")
# Every whitespace class here is HORIZONTAL only ([^\S\n]). A plain \s* matches the newline,
# so the reason group swallowed the following line of code and a declaration with no reason at
# all read as fully explained — caught by this gate's own selftest before it shipped.
DECLARATION = re.compile(
    r"(?m)^[^\S\n]*#[^\S\n]*CONVERGENCE:[^\S\n]*"
    r"(immutable|reconciled by step[^\S\n]+(\S+?)|no source-declared properties|UNRESOLVED)\b"
    r"[^\S\n]*(?:--|—)?[^\S\n]*([^\n]*)$"
)


def _strip_comments(text: str) -> str:
    text = re.sub(r"<#.*?#>", "", text, flags=re.S)
    return re.sub(r"(?m)^\s*#.*$", "", text)


def steps(source: str) -> list[dict]:
    """Every step region in one script, numbered or not."""
    marks = [(m.start(), m.group(1).strip()) for m in STEP_MARKER.finditer(source)]
    out = []
    for index, (pos, title) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(source)
        region = source[pos:end]
        number = NUMBERED.match(title)
        code = _strip_comments(region)
        out.append({
            "id": number.group(1) if number else None,
            "title": title,
            "region": region,
            "creates": bool(re.search(CREATE_CALLS, code)),
            "patches": bool(re.search(PATCH_CALLS, code)),
        })
    return out


def classify(step: dict) -> str:
    if step["patches"]:
        return "RECONCILES"
    if step["creates"]:
        return "CREATE-ONLY"
    return "READ-ONLY"


def declaration(step: dict) -> tuple[str, str, str] | None:
    match = DECLARATION.search(step["region"])
    if match is None:
        return None
    kind = match.group(1)
    if kind.startswith("reconciled by step"):
        return ("reconciled", (match.group(2) or "").rstrip(".,"), match.group(3).strip())
    return (kind, "", match.group(3).strip())


def scripts_under(root: str) -> list[str]:
    found = []
    base = os.path.join(root, "provisioning")
    for dirpath, _dirs, files in os.walk(base):
        for name in sorted(files):
            if name.endswith(".ps1"):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def main(argv: list[str]) -> int:
    root = (argv[1] if len(argv) > 1 else ".").rstrip("/") or "."
    if not os.path.isdir(os.path.join(root, "provisioning")):
        print(f"FAIL - no provisioning/ directory under '{root}'. This check is not allowed to "
              f"pass on a missing target (IMP-0007).")
        return 1

    problems: list[str] = []
    warnings: list[str] = []
    counts = {"READ-ONLY": 0, "RECONCILES": 0, "CREATE-ONLY": 0}
    declared = 0

    for path in scripts_under(root):
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        all_steps = steps(source)
        numbered = [s for s in all_steps if s["id"]]
        ids = {s["id"] for s in numbered}

        if not numbered:
            code = _strip_comments(source)
            if re.search(CREATE_CALLS, code) or re.search(PATCH_CALLS, code):
                warnings.append(
                    f"  UNCLASSIFIABLE - {rel} writes to a live environment and has no numbered "
                    f"'# -- <n>. ' step markers, so its steps cannot be classified. Not a pass: "
                    f"add markers, or accept that convergence here is unrecorded.")
            continue

        for step in numbered:
            kind = classify(step)
            counts[kind] += 1
            decl = declaration(step)
            where = f"{rel} step {step['id']}"

            if kind != "CREATE-ONLY":
                if decl and decl[0] == "immutable" and step["patches"]:
                    problems.append(
                        f"  CLAIM CONTRADICTS CODE - {where} declares CONVERGENCE: immutable, "
                        f"but the step issues a PATCH or PUT. If it can correct a component, it "
                        f"is not immutable — say what it reconciles instead.")
                continue

            if decl is None:
                problems.append(
                    f"  CREATE-ONLY, UNDECLARED - {where} ({step['title'][:52]}) creates "
                    f"components and never issues a reconciling PATCH or PUT, so a property "
                    f"corrected in source later will never reach an environment where the "
                    f"component already exists. That is IMP-0259: the fix lands in a fresh PRD "
                    f"and never in DEV, which is where testing happens. Add a CONVERGENCE "
                    f"declaration — immutable, reconciled by step <id>, or UNRESOLVED with an "
                    f"owner.")
                continue

            declared += 1
            kind_of_decl, target, reason = decl
            if not reason:
                problems.append(
                    f"  DECLARATION WITHOUT A REASON - {where} declares "
                    f"CONVERGENCE: {kind_of_decl} with no explanation after it. The reason is "
                    f"the part a future reader needs.")
            if kind_of_decl == "reconciled":
                if not target:
                    problems.append(
                        f"  DECLARATION NAMES NO STEP - {where} says 'reconciled by step' "
                        f"without naming one.")
                elif target not in ids:
                    problems.append(
                        f"  FORWARD REFERENCE TO NOTHING - {where} says it is reconciled by "
                        f"step {target}, and {rel} has no step {target}. Steps present: "
                        f"{', '.join(sorted(ids))}. An evidence rule satisfied by a reference "
                        f"to something absent is the IMP-0067 class.")
                else:
                    other = next(s for s in numbered if s["id"] == target)
                    if not other["patches"]:
                        problems.append(
                            f"  NAMED STEP DOES NOT RECONCILE - {where} says step {target} "
                            f"reconciles it, but step {target} issues no reconciling PATCH or "
                            f"PUT either. Two create-only steps pointing at each other converge "
                            f"nothing.")
            if kind_of_decl == "UNRESOLVED":
                if "owner:" not in reason:
                    problems.append(
                        f"  UNRESOLVED WITHOUT AN OWNER - {where} declares UNRESOLVED but names "
                        f"no owner. An open question with nobody attached is not owned.")
                else:
                    warnings.append(f"  UNRESOLVED CONVERGENCE - {where}: {reason}")

    total = sum(counts.values())
    if problems:
        print(f"FAIL - provisioning step convergence is unrecorded or misdeclared "
              f"({len(problems)} problem(s)):")
        print("\n".join(problems))
        if warnings:
            print(f"\nWARNING ({len(warnings)}):")
            print("\n".join(warnings))
        return 1

    print(f"PASS - {total} numbered provisioning step(s): {counts['READ-ONLY']} read-only, "
          f"{counts['RECONCILES']} reconciling, {counts['CREATE-ONLY']} create-only and every "
          f"one of those carrying a CONVERGENCE declaration ({declared} declaration(s) read).")
    if warnings:
        print(f"\nWARNING - {len(warnings)} item(s) declared open or unclassifiable. Not a "
              f"build failure; an owned question:")
        print("\n".join(warnings))
    return 0


# ── selftest ──────────────────────────────────────────────────────────────────────────────

_HEAD = "#!/usr/bin/env pwsh\n"


def _script(*blocks: str) -> str:
    return _HEAD + "\n".join(blocks)


def _step(title: str, *, body: str = "", decl: str = "") -> str:
    bar = "─" * max(4, 60 - len(title))
    lines = [f"# ── {title} {bar}"]
    if decl:
        lines.append(f"# CONVERGENCE: {decl}")
    lines.append(body or "Write-Host 'nothing'")
    return "\n".join(lines) + "\n"


_CREATE = "Invoke-DataverseApi -Method POST -Path 'x' -Body $b"
_PATCH = "Invoke-DataverseApi -Method PATCH -Path 'x' -Body $b"
# PUT reconciles too (IMP-0272/IMP-0273) — Dataverse's Attributes/EntityDefinitions metadata
# endpoints reject PATCH outright and require a full-object PUT for an update. Modelled on
# ensure-schema.ps1 step 3b's actual call shape: a raw Invoke-RestMethod, not the
# Invoke-DataverseApi wrapper (which has no header passthrough for MSCRM.MergeLabels).
_PUT = "Invoke-RestMethod -Method PUT -Uri $uri -Headers $h -Body $b"


def _tree(base: str, name: str, content: str) -> str:
    root = os.path.join(base, "repo")
    target = os.path.join(root, "provisioning", "dataverse")
    os.makedirs(target, exist_ok=True)
    with open(os.path.join(target, name), "w", encoding="utf-8") as handle:
        handle.write(content)
    return root


def selftest() -> int:
    import contextlib
    import io

    cases: list[tuple[str, str, int, str]] = [
        ("create-only-undeclared-must-fail",
         _script(_step("1. Creates things", body=_CREATE)), 1, "CREATE-ONLY, UNDECLARED"),
        ("create-only-declared-immutable-must-pass",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="immutable -- an alternate key cannot be altered after creation")),
         0, "PASS"),
        ("reconciled-by-real-patching-step-must-pass",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="reconciled by step 2 -- step 2 PATCHes IsSecured"),
                 _step("2. Fixes things", body=_PATCH)), 0, "PASS"),
        ("reconciled-by-real-putting-step-must-pass",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="reconciled by step 2 -- step 2 PUTs the full attribute back with "
                            "IsSecured set (IMP-0272)"),
                 _step("2. Fixes things", body=_PUT)), 0, "PASS"),
        ("immutable-claim-on-a-putting-step-must-fail",
         _script(_step("1. Puts things", body=_PUT,
                       decl="immutable -- claimed wrongly")),
         1, "CLAIM CONTRADICTS CODE"),
        ("reconciled-by-absent-step-must-fail",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="reconciled by step 9 -- step 9 does it")),
         1, "FORWARD REFERENCE TO NOTHING"),
        ("reconciled-by-non-patching-step-must-fail",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="reconciled by step 2 -- step 2 does it"),
                 _step("2. Also only creates", body=_CREATE, decl="immutable -- it is")),
         1, "NAMED STEP DOES NOT RECONCILE"),
        ("immutable-claim-on-a-patching-step-must-fail",
         _script(_step("1. Patches things", body=_PATCH,
                       decl="immutable -- claimed wrongly")),
         1, "CLAIM CONTRADICTS CODE"),
        ("declaration-without-a-reason-must-fail",
         _script(_step("1. Creates things", body=_CREATE, decl="immutable")),
         1, "DECLARATION WITHOUT A REASON"),
        ("unresolved-with-owner-must-warn",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="UNRESOLVED -- owner:development-agent, can option-set members be "
                            "corrected later")), 0, "UNRESOLVED CONVERGENCE"),
        ("unresolved-without-owner-must-fail",
         _script(_step("1. Creates things", body=_CREATE,
                       decl="UNRESOLVED -- somebody should look at this")),
         1, "UNRESOLVED WITHOUT AN OWNER"),
        ("no-source-declared-properties-must-pass",
         _script(_step("1. Publishes", body=_CREATE,
                       decl="no source-declared properties -- PublishAllXml is an operation, "
                            "not a component carrying anything from source")), 0, "PASS"),
        ("writing-script-with-no-numbered-steps-must-warn",
         _script("# ── Helpers ───────────────\n" + _CREATE + "\n"), 0, "UNCLASSIFIABLE"),
        ("read-only-step-needs-no-declaration",
         _script(_step("1. Just reads", body="$x = Invoke-DataverseApi -Method GET -Path 'y'")),
         0, "PASS"),
        # A comment mentioning a create call must not classify the step as writing (IMP-0020).
        ("create-call-in-a-comment-only-must-not-classify",
         _script(_step("1. Discusses POST",
                       body="# we could Invoke-DataverseApi -Method POST here but do not\n"
                            "Write-Host 'read only'")), 0, "PASS"),
    ]

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, content, want_rc, want_text in cases:
            root = _tree(os.path.join(tmp, name), "ensure-thing.ps1", content)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                rc = main(["verify-provisioning-step-convergence.py", root])
            text = buffer.getvalue()
            ok = rc == want_rc and want_text in text
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in text.splitlines():
                    print(f"                   {line}")

    if failures:
        print(f"\nverify-provisioning-step-convergence: SELFTEST FAILED — "
              f"{', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nverify-provisioning-step-convergence: SELFTEST OK — {len(cases)} fixtures. "
          f"Silence fails, a forward reference to a step that does not exist or does not "
          f"reconcile fails, a claim contradicting the code fails, and an honestly-open "
          f"question warns with its owner named.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
