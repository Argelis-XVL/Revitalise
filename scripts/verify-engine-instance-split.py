#!/usr/bin/env python3
"""Report the state of every scripts/ <-> .engine/scripts/ pair while the migration is live.

WHY THIS EXISTS (IMP-0696). After the Phase 3c/3d/3e "thin consumer of the engine" commit,
most scripts under ``scripts/`` are still BYTE-IDENTICAL DUPLICATES of ``.engine/scripts/``,
not wrappers and not symlinks. ``.engine`` is a git submodule, so the two copies are genuinely
separate files with nothing keeping them in step.

That matters because of which one RUNS. ``config/<slug>-build.yml`` invokes
``python3 scripts/<name>.py`` — never the ``.engine`` path. So a change applied only to the
engine copy does not execute, while both files still parse and both still pass their own
``--selftest``. There is no error to notice; the fix is simply absent at runtime.

Before this gate, each dispatch rediscovered the split state one script at a time:
``contract/delivery-parameters.json``'s ``_wiring_gap`` note is a hand-written record of
exactly that rediscovery for a single script.

WHAT IT REPORTS, per pair:

* ``DUPLICATE``    - both copies exist and are byte-identical. The migration has not split
                     this script yet, so a change must target BOTH copies or convert the
                     instance side to a wrapper. **This is the state that silently diverges.**
* ``WRAPPER``      - both exist and differ. Assumed to be a completed Phase 3f split: the
                     instance holds client-specific facts, the engine holds the mechanism.
* ``INSTANCE-ONLY`` - no engine counterpart. Client-specific by construction.
* ``ENGINE-ONLY``  - no instance counterpart. Not reachable from this repo's build config.

SEVERITY IS DELIBERATELY *WARNING*, NOT FAILURE. A duplicate pair is a correct, expected
intermediate state of a migration that is still in flight — failing on it would open the
build red on work no dispatch owns, which is the shape ``IMP-0439``/``IMP-0491`` warn about.
What the gate buys is that the remaining surface is ONE NUMBER in the build log instead of a
per-script discovery. When the migration completes, ``--max-duplicates 0`` turns it into a
real gate without touching this file.

Run:
    python3 scripts/verify-engine-instance-split.py
    python3 scripts/verify-engine-instance-split.py --max-duplicates 0   # once migration ends
    python3 scripts/verify-engine-instance-split.py --selftest

Exits 0 unless --max-duplicates is exceeded. Wired into config/<slug>-build.yml as the SOFT
``engine-instance-split`` step.
"""

from __future__ import annotations

import argparse
import filecmp
import sys
import tempfile
from pathlib import Path

INSTANCE_DIR = Path("scripts")
ENGINE_DIR = Path(".engine/scripts")


def classify(instance_dir: Path, engine_dir: Path) -> dict[str, list[str]]:
    """Bucket every *.py in either directory by its split state."""
    out: dict[str, list[str]] = {
        "DUPLICATE": [], "WRAPPER": [], "INSTANCE-ONLY": [], "ENGINE-ONLY": []}

    inst = {p.name for p in instance_dir.glob("*.py")} if instance_dir.is_dir() else set()
    eng = {p.name for p in engine_dir.glob("*.py")} if engine_dir.is_dir() else set()

    for name in sorted(inst | eng):
        i, e = instance_dir / name, engine_dir / name
        if name in inst and name in eng:
            # shallow=False: compare CONTENT, not (size, mtime). A submodule checkout gives
            # both copies fresh mtimes, so a shallow compare would call every pair different
            # and report a clean migration that has not happened.
            same = filecmp.cmp(i, e, shallow=False)
            out["DUPLICATE" if same else "WRAPPER"].append(name)
        elif name in inst:
            out["INSTANCE-ONLY"].append(name)
        else:
            out["ENGINE-ONLY"].append(name)
    return out


def render(buckets: dict[str, list[str]], max_duplicates: int | None) -> tuple[str, int]:
    dupes = buckets["DUPLICATE"]
    lines: list[str] = []
    total = sum(len(v) for v in buckets.values())

    if dupes:
        lines.append(
            f"  {len(dupes)} UNSPLIT DUPLICATE pair(s) — a change to any of these must target "
            f"BOTH copies, or convert the instance side to a wrapper. The build runs the "
            f"scripts/ copy, so an engine-only edit does not execute (IMP-0696):")
        for name in dupes:
            lines.append(f"    {name}")

    summary = (f"engine-instance-split: {total} script(s) — "
               f"{len(dupes)} unsplit duplicate, {len(buckets['WRAPPER'])} split/wrapper, "
               f"{len(buckets['INSTANCE-ONLY'])} instance-only, "
               f"{len(buckets['ENGINE-ONLY'])} engine-only")

    if max_duplicates is not None and len(dupes) > max_duplicates:
        lines.append(f"\n{summary} — FAILED: {len(dupes)} duplicate(s) exceeds the "
                     f"--max-duplicates {max_duplicates} threshold.")
        return "\n".join(lines), 1
    return "\n".join(lines + ["", summary + "."]), 0


def selftest() -> int:
    """Prove each of the four states is distinguished, and that the check CAN fail."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        inst, eng = root / "scripts", root / ".engine" / "scripts"
        inst.mkdir(parents=True)
        eng.mkdir(parents=True)

        (inst / "dup.py").write_text("print('same')\n")
        (eng / "dup.py").write_text("print('same')\n")
        (inst / "split.py").write_text("print('instance wrapper')\n")
        (eng / "split.py").write_text("print('engine mechanism')\n")
        (inst / "only_here.py").write_text("print('instance')\n")
        (eng / "only_there.py").write_text("print('engine')\n")

        got = classify(inst, eng)
        expected = {
            "DUPLICATE": ["dup.py"], "WRAPPER": ["split.py"],
            "INSTANCE-ONLY": ["only_here.py"], "ENGINE-ONLY": ["only_there.py"]}
        for state, want in expected.items():
            ok = got[state] == want
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {state} → {got[state]} "
                  f"(expected {want})")
            if not ok:
                failures.append(state)

        # It must be able to FAIL, or it is not a gate.
        _, rc_fail = render(got, max_duplicates=0)
        _, rc_pass = render(got, max_duplicates=5)
        print(f"  {'OK' if rc_fail == 1 else 'DID NOT BEHAVE':16} "
              f"--max-duplicates 0 with 1 duplicate → exit {rc_fail} (expected 1)")
        print(f"  {'OK' if rc_pass == 0 else 'DID NOT BEHAVE':16} "
              f"--max-duplicates 5 with 1 duplicate → exit {rc_pass} (expected 0)")
        if rc_fail != 1:
            failures.append("must-fail")
        if rc_pass != 0:
            failures.append("must-pass")

        # A byte-identical pair with different mtimes must still read as DUPLICATE — the
        # submodule-checkout case this gate exists to survive.
        import os
        os.utime(eng / "dup.py", (0, 0))
        if classify(inst, eng)["DUPLICATE"] != ["dup.py"]:
            print("  DID NOT BEHAVE   mtime-differing identical pair misread as WRAPPER")
            failures.append("mtime")
        else:
            print("  OK               identical pair with differing mtime still DUPLICATE")

    if failures:
        print(f"\nverify-engine-instance-split: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print("\nverify-engine-instance-split: SELFTEST OK — 4 states distinguished, "
          "both exit paths proven, mtime-insensitivity proven.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instance-dir", type=Path, default=INSTANCE_DIR)
    ap.add_argument("--engine-dir", type=Path, default=ENGINE_DIR)
    ap.add_argument("--max-duplicates", type=int, default=None,
                    help="fail when more than N unsplit duplicate pairs remain "
                         "(omit to report only, which is correct while the migration is live)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.engine_dir.is_dir():
        print(f"engine-instance-split: no {args.engine_dir} — nothing to compare. This is "
              f"correct for a repository that does not consume the engine.")
        return 0

    text, rc = render(classify(args.instance_dir, args.engine_dir), args.max_duplicates)
    print(text, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main())
