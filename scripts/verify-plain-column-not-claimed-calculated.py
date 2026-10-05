#!/usr/bin/env python3
"""A plain column must not be described as calculated, and one admitted to be plain must be written.

Usage:
    verify-plain-column-not-claimed-calculated.py <solution-root> [<repo-root>]
    verify-plain-column-not-claimed-calculated.py --selftest

WHY THIS EXISTS. IMP-1033 (rev_applicant.rev_fullname) and its recurrence (rev_application.rev_costs),
both found 2026-10-03 and both the same shape: on 2026-08-14 solution import rejected the calculated
column form, so the column shipped as an ORDINARY writable column ("NOT CALCULATED YET"). Its comment,
its user-facing Description, the design doc and the intake flow all kept assuming it was calculated, so
nothing ever wrote it and it stayed empty on every row. Downstream readers treated the null as unknown.

THE INVARIANT (three rules, all derived from the source, no list of columns held here):
  A. A column with no SourceType/FormulaDefinition (plain) must not have a <Description> that claims it
     is CALCULATED (upper case) or that it "cannot be typed/written/edited". That text is shown to users
     and is false for a plain column.
  B. A column whose own comment says "NOT CALCULATED YET" admits it is plain pending a conversion that
     has not happened. Some flow must then actually write it -- a write payload key `item/<col>` or
     `body/<col>` in Workflows/*.json -- or it is empty forever.
     WHY PROVISIONING IS NOT A WRITER (IMP-1036): the first version also counted any whole-word mention
     of the column under provisioning/. The scripts that CREATE a column always name it (ensure-schema.ps1's
     header, the knownFutureCalculatedColumns map in ensure-schema-helpers.psm1), so Rule B could not fail
     on either real case it was written for. Run against the pre-fix tree it gave 0 Rule B findings; the
     payload-only form gives 5, all true. A test-data seeder would not populate production rows either.
  C. A column that declares SourceType/FormulaDefinition (calculated) must not be written by any flow
     payload: Dataverse rejects a write to a calculated column, so every create carrying it fails. This is
     the coupling the rev_applicant/rev_application Entity.xml comments say MUST be honoured if the planned
     conversion to calculated happens (IMP-1033, IMP-1037): the intake flow's writes come out in the same
     change.
RESIDUAL: it reads declarations and the presence of a write payload key, never that the written value is
right; a column with no marker and no Description claim is not examined by A or B; a flow writing the
column inside an expression that is not a payload key reads as "not written" (a false FAIL, the safe
direction).
"""
import io, os, re, sys, tempfile, contextlib

ATTR = re.compile(r'<attribute PhysicalName="([^"]+)">(.*?)</attribute>', re.S)
DESC = re.compile(r'<Description description="([^"]*)"')
CLAIM = re.compile(r'\bCALCULATED\b|cannot be (?:typed|written|edited)')


def _writers(col, sol):
    """True when some flow carries `item/<col>` or `body/<col>` as a write payload key (IMP-1036)."""
    rx = re.compile(r'"(?:item|body)/' + re.escape(col) + r'"')
    for base, _, files in os.walk(os.path.join(sol, "Workflows")):
        for f in files:
            if f.endswith(".json"):
                try:
                    if rx.search(open(os.path.join(base, f), encoding="utf-8").read()):
                        return True
                except OSError:
                    pass
    return False


def main(argv):
    sol = argv[1]
    # argv[2] (<repo-root>) is accepted for the wired command line and no longer read: provisioning/
    # is not a writer (IMP-1036).
    problems, checked, calculated = [], 0, 0
    for ent in sorted(os.listdir(os.path.join(sol, "Entities"))):
        p = os.path.join(sol, "Entities", ent, "Entity.xml")
        if not os.path.isfile(p):
            continue
        for col, body in ATTR.findall(open(p, encoding="utf-8").read()):
            if "<SourceType>" in body or "<FormulaDefinition>" in body or "<Formula" in body:
                calculated += 1
                if _writers(col, sol):
                    problems.append(f"{ent}.{col}: CALCULATED column written by a flow payload (item/ or body/); Dataverse rejects the write, so the create fails (IMP-1033/IMP-1037 coupling, Rule C)")
                continue
            checked += 1
            for d in DESC.findall(body):
                if CLAIM.search(d):
                    problems.append(f"{ent}.{col}: PLAIN column whose Description claims it is calculated / cannot be written (IMP-1033 class)")
            if "NOT CALCULATED YET" in body and not _writers(col, sol):
                problems.append(f"{ent}.{col}: admits it is plain (NOT CALCULATED YET) but no flow write payload (item/ or body/ in Workflows/*.json) writes it; a mention in provisioning/ is not a write (IMP-1033 class, IMP-1036)")
    for m in problems:
        print("FAIL " + m)
    if problems:
        return 1
    print(f"PASS plain-column-not-claimed-calculated: {checked} plain columns checked, {calculated} calculated columns checked for writes")
    return 0


_ATTR = '''<attribute PhysicalName="rev_x"><!-- {comment} --><Type>money</Type><Name>rev_x</Name>{calc}
<Descriptions><Description description="{desc}" languagecode="1033" /></Descriptions></attribute>'''


def _tree(root, comment, desc, writer, provisioning_mention=False, calculated=False):
    os.makedirs(os.path.join(root, "sol", "Entities", "rev_t"))
    os.makedirs(os.path.join(root, "sol", "Workflows"))
    os.makedirs(os.path.join(root, "provisioning"))
    calc = "<SourceType>1</SourceType>" if calculated else ""
    open(os.path.join(root, "sol", "Entities", "rev_t", "Entity.xml"), "w").write(_ATTR.format(comment=comment, desc=desc, calc=calc))
    open(os.path.join(root, "sol", "Workflows", "f.json"), "w").write('{"item/rev_x": "1"}' if writer else "{}")
    if provisioning_mention:
        open(os.path.join(root, "provisioning", "ensure-schema.ps1"), "w").write("# rev_x is created here as a plain column\n")
    return os.path.join(root, "sol"), root


def selftest():
    cases = [
        ("claims-calculated-must-fail", "NOT CALCULATED YET", "CALCULATED as a sum", True, 1, "Description claims"),
        ("cannot-be-written-must-fail", "x", "it cannot be written by a flow", True, 1, "Description claims"),
        ("plain-unwritten-must-fail", "NOT CALCULATED YET", "The total.", False, 1, "no flow write payload"),
        ("plain-written-must-pass", "NOT CALCULATED YET", "The total, written by the flow.", True, 0, "PASS"),
        ("lowercase-calculated-process-must-pass", "x", "when the scoring process last calculated it", False, 0, "PASS"),
        ("mentioned-only-in-provisioning-must-fail", "NOT CALCULATED YET", "The total.", False, 1, "a mention in provisioning/ is not a write", True, False),
        ("calculated-and-written-must-fail", "x", "The total.", True, 1, "CALCULATED column written by a flow payload", False, True),
    ]
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, comment, desc, writer, rc_want, text_want, *extra in cases:
            sol, repo = _tree(os.path.join(tmp, name), comment, desc, writer, *extra)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main(["x", sol, repo])
            ok = rc == rc_want and text_want in buf.getvalue()
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} -> exit {rc}")
            if not ok:
                bad.append(name)
    if bad:
        print("SELFTEST FAILED: " + ", ".join(bad), file=sys.stderr)
        return 1
    print(f"verify-plain-column-not-claimed-calculated: SELFTEST OK - {len(cases)} fixtures")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
