#!/usr/bin/env python3
"""C-TECH-076 — an authored CSS declaration whose correctness is ARITHMETIC against another
declared value is checked mechanically, not asserted in a comment.

WHY THIS EXISTS (IMP-0486, IMP-0509, IMP-0526)
----------------------------------------------
A CSS defect that reduces to arithmetic is invisible to every test in this repository and is
found only by a human looking at a rendered screen. jsdom computes no layout, so no vitest
assertion can see it. That sentence is true of EVERY arithmetic relation in a stylesheet, not
only of the one property that happened to fail first — which is why this gate is scoped to the
class rather than to a property.

It was `verify-css-line-height.py` until 2026-08-31, scoped to check A alone. The class
recurred one day later with a second property (`IMP-0526`, the `auto-fit` column count), so the
gate that existed and did not fire was mis-scoped, not broken. Renamed and broadened by
improvement review 4; check A's logic is unchanged.

WHAT IT ASSERTS — VALUES, NOT PHRASES
-------------------------------------
Both checks compare declared values against declared values. Neither reads a comment, and
neither offers a comment-phrase escape hatch: a retraction marker is a phrase, and a
phrase-based gate is the instrument this project has measured at 48-100% false five times
(`IMP-0422`, `IMP-0428`). Where an author needs an exemption, the exemption is a DECLARED VALUE.

CHECK A — line-height against the ambient body size
---------------------------------------------------
A rule setting a font-size larger than the ambient body size declares its own `line-height`.
A Code App renders inside FluentProvider, whose root sets `line-height: 22px` — a value tuned
for Fluent's own base font size. At `--text-xl: 24px` the line box is SMALLER THAN THE GLYPHS,
so wrapped lines overlap. The ambient body size is READ from the token file's own `--text-base`
declaration, never transcribed, so re-tuning the scale re-tunes the gate. `clamp()` is judged on
its MAXIMUM, which is the size that overlaps.

CHECK B — an auto-fit/auto-fill floor cannot cap a column count unless it is container-relative
------------------------------------------------------------------------------------------------
`repeat(auto-fit, minmax(<floor>, 1fr))` fits `floor(container / floor_width)` columns. A floor
stated in ABSOLUTE units therefore sets a MINIMUM TRACK WIDTH and can never set a MAXIMUM COLUMN
COUNT: raising it from 160px to 240px does not produce 4 columns, it produces 6 at 1500px. The
only floors that cap the count are container-relative — `max(240px, (100% - 3 * gap) / 4)` can
never be narrower than a quarter of the row, so a fifth column cannot fit at any width.

`IMP-0526`: ADR-041 raised the floor to 240px and its comment asserted this "lands at 2 rows of
4 on the desktop widths this portal is actually used at". Eight tiles landed 6 + 2 on a
reviewer's screen. The arithmetic was never solved.

SCOPE, and why it is this narrow (measured, see the review document)
--------------------------------------------------------------------
Authored stylesheets only — `src/code-apps/*/src/**/*.css`. Run over everything under
`src/code-apps/` check A's candidate reported 77 findings across 17 files, dominated by
`node_modules/` and a `dist/` bundle that re-reports every authored rule. Restricted to authored
sources but flagging every missing `line-height` it reported 23, most of them at 13-17px where
inheriting 22px is harmless or generous. Both numbers teach a reader to ignore the gate.

RESIDUALS, stated because they are not covered:
  • Check A reads ONE rule at a time and cannot see an INHERITED line-height. A rule that
    inherits a correct line-height from a parent selector is a false positive by construction.
    Measured at zero in this corpus; fix such a case by declaring the line-height, not by
    exempting the gate.
  • Check B cannot read intent. A grid DELIBERATELY uncapped — as many columns as fit, no
    maximum — is a false positive by construction. Measured at zero in this corpus (2
    declarations, both container-relative). The escape is a declared value: an explicit
    `repeat(N, ...)` track count, or a container-relative term in the floor. There is
    deliberately no comment escape hatch.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# A declaration block: everything between the selector's `{` and its matching `}`. CSS here is
# authored by hand and never nests rules inside rules, so a non-greedy brace match is exact.
RULE_RE = re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}", re.MULTILINE)
DECL_RE = re.compile(r"(?P<prop>[-a-zA-Z]+)\s*:\s*(?P<val>[^;]+)")
TOKEN_DEF_RE = re.compile(r"(--[-a-zA-Z0-9]+)\s*:\s*([^;]+);")
VAR_RE = re.compile(r"var\(\s*(--[-a-zA-Z0-9]+)")
LEN_RE = re.compile(r"^(-?\d+(?:\.\d+)?)(px|pt|rem)$")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

# A term that makes a length scale with the grid container (or the viewport it fills).
# `%` resolves against the grid container's content box; `cq*` against the query container;
# `vw`/`vh`/`vmin`/`vmax` against the viewport. Any one of them lets a floor cap a column count.
CONTAINER_RELATIVE_RE = re.compile(r"%|\bcq[a-z]+\b|\d(?:vw|vh|vmin|vmax)\b")

DEFAULT_ROOT_FONT_PX = 16.0  # for rem; the browser default this project does not override


def strip_comments(text: str) -> str:
    """Blank out comments, PRESERVING newlines so reported line numbers stay true.

    Without this a rule's `selector` capture swallows the whole comment block above it —
    this file's stylesheets carry 25-line explanatory comments before a rule — and the
    finding message becomes unreadable. The defect was caught by running the gate over the
    real corpus, not by the fixtures.
    """
    return COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def collect_tokens(files: list[Path]) -> dict[str, str]:
    """Every custom-property definition across the authored stylesheets."""
    tokens: dict[str, str] = {}
    for path in files:
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        for name, raw in TOKEN_DEF_RE.findall(text):
            tokens.setdefault(name, raw.strip())
    return tokens


def resolve_px(value: str, tokens: dict[str, str], depth: int = 0) -> float | None:
    """Resolve a font-size expression to pixels, or None when it cannot be resolved.

    `clamp(min, preferred, max)` resolves to its MAX: that is the size at which the inherited
    line box overlaps, so it is the size the gate must judge.
    """
    if depth > 8:
        return None
    value = value.strip()

    if value.startswith("clamp(") and value.endswith(")"):
        parts = split_args(value[len("clamp(") : -1])
        return resolve_px(parts[-1], tokens, depth + 1) if parts else None

    # A bare var() reference, possibly with a fallback: var(--x, 20px)
    match = VAR_RE.match(value)
    if match:
        name = match.group(1)
        if name in tokens:
            return resolve_px(tokens[name], tokens, depth + 1)
        return None

    unit = LEN_RE.match(value)
    if unit:
        number, suffix = float(unit.group(1)), unit.group(2)
        if suffix == "px":
            return number
        if suffix == "pt":
            return number * 4.0 / 3.0
        if suffix == "rem":
            return number * DEFAULT_ROOT_FONT_PX
    return None


def split_args(text: str) -> list[str]:
    """Split a comma-separated argument list, respecting nested parentheses."""
    args, depth, current = [], 0, ""
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            args.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        args.append(current.strip())
    return args


def balanced_call(text: str, start: int) -> str | None:
    """Return the argument text of a function call whose `(` follows `text[start:]`.

    `start` is the index of the opening parenthesis. Returns None on an unbalanced call.
    """
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    return None


def authored_stylesheets(root: Path) -> list[Path]:
    """Authored Code App stylesheets. Never node_modules, dist, coverage or build output."""
    found: list[Path] = []
    for path in sorted((root / "src" / "code-apps").rglob("*.css")):
        parts = set(path.parts)
        if parts & {"node_modules", "dist", "coverage", "build", ".vite"}:
            continue
        # Authored sources live under the app's own `src/`.
        rel = path.relative_to(root / "src" / "code-apps")
        if len(rel.parts) < 2 or rel.parts[1] != "src":
            continue
        found.append(path)
    return found


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_line_height(path: Path, text: str, root: Path, tokens: dict[str, str],
                      base: float) -> list[str]:
    """CHECK A — a rule above the ambient body size declares its own line-height."""
    findings: list[str] = []
    for rule in RULE_RE.finditer(text):
        body = rule.group("body")
        decls = {m.group("prop").lower(): m.group("val").strip()
                 for m in DECL_RE.finditer(body)}
        if "font-size" not in decls or "line-height" in decls:
            continue
        size = resolve_px(decls["font-size"], tokens)
        if size is None or size <= base:
            continue
        selector = " ".join(rule.group("sel").split())
        # Report the line of the font-size declaration, not the selector.
        offset = rule.start("body") + body.lower().index("font-size")
        findings.append(
            f"{path.relative_to(root)}:{line_of(text, offset)}: `{selector}` sets "
            f"font-size {decls['font-size']} ({size:g}px), above the ambient body size "
            f"{base:g}px, with no line-height in the same rule. It will inherit the host "
            f"framework's line-height (FluentProvider's root sets 22px), giving a line box "
            f"of ratio {22.0 / size:.2f} — wrapped lines crowd below ~1.2 and OVERLAP below "
            f"1.0. Declare an explicit line-height on this rule (C-TECH-076)."
        )
    return findings


def check_autofit_floor(path: Path, text: str, root: Path) -> list[str]:
    """CHECK B — an auto-fit/auto-fill minmax floor that is purely absolute caps nothing."""
    findings: list[str] = []
    for rule in RULE_RE.finditer(text):
        body = rule.group("body")
        for decl in DECL_RE.finditer(body):
            if decl.group("prop").lower() != "grid-template-columns":
                continue
            value = decl.group("val")
            for repeat in re.finditer(r"\brepeat\s*\(", value):
                args_text = balanced_call(value, repeat.end() - 1)
                if args_text is None:
                    continue
                args = split_args(args_text)
                if len(args) < 2 or args[0].strip().lower() not in ("auto-fit", "auto-fill"):
                    continue
                track = args[1].strip()
                minmax = re.match(r"minmax\s*\(", track)
                if not minmax:
                    continue
                inner = balanced_call(track, minmax.end() - 1)
                if inner is None:
                    continue
                floor_args = split_args(inner)
                if not floor_args:
                    continue
                floor = floor_args[0].strip()
                if CONTAINER_RELATIVE_RE.search(floor):
                    continue
                selector = " ".join(rule.group("sel").split())
                offset = rule.start("body") + decl.start()
                findings.append(
                    f"{path.relative_to(root)}:{line_of(text, offset)}: `{selector}` sets "
                    f"`grid-template-columns: repeat({args[0].strip()}, minmax({floor}, …))`. "
                    f"That floor is PURELY ABSOLUTE, so it sets a minimum TRACK WIDTH and can "
                    f"never cap the COLUMN COUNT: the grid fits floor(container ÷ {floor}) "
                    f"columns, which grows without limit as the container widens. If a maximum "
                    f"column count N is intended, make the floor container-relative — "
                    f"`minmax(max({floor}, (100% - (N-1) * <gap>) / N), 1fr)` — or declare an "
                    f"explicit `repeat(N, …)` track list. Raising an absolute floor changes "
                    f"where the grid reflows, never how many columns it tops out at "
                    f"(C-TECH-076, IMP-0526)."
                )
    return findings


def scan(root: Path) -> tuple[list[str], float | None, int]:
    files = authored_stylesheets(root)
    if not files:
        return [], None, 0

    tokens = collect_tokens(files)
    base = resolve_px(tokens.get("--text-base", ""), tokens)
    if base is None:
        return (
            [f"cannot resolve the ambient body size: no --text-base among "
             f"{len(tokens)} custom properties in {len(files)} authored stylesheet(s). "
             f"This gate asserts against that VALUE and refuses to guess it."],
            None,
            len(files),
        )

    findings: list[str] = []
    for path in files:
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        findings.extend(check_line_height(path, text, root, tokens, base))
        findings.extend(check_autofit_floor(path, text, root))
    return findings, base, len(files)


# ── selftest ──────────────────────────────────────────────────────────────────────────────

BAD_FIXTURE = """
:root { --text-base: 17px; --text-xl: 24px; }
.cardTitle { margin: 0; font-size: var(--text-xl); color: red; }
"""

GOOD_FIXTURE = """
:root { --text-base: 17px; --text-xl: 24px; }
.cardTitle { margin: 0; font-size: var(--text-xl); line-height: 1.25; color: red; }
.small { font-size: var(--text-base); }
.clamped { font-size: clamp(15px, 4cqi, 16px); }
"""

# Check B. The bad fixture is IMP-0526's own declaration, verbatim from `ba50830^`.
BAD_GRID_FIXTURE = """
:root { --text-base: 17px; }
.statTiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
"""

GOOD_GRID_FIXTURE = """
:root { --text-base: 17px; --space-4: 16px; }
.statTiles {
  display: grid;
  grid-template-columns: repeat(
    auto-fit,
    minmax(max(240px, (100% - 3 * var(--space-4)) / 4), 1fr)
  );
}
.fixedTracks { display: grid; grid-template-columns: repeat(4, 1fr); }
.explicitPair { display: grid; grid-template-columns: minmax(140px, max-content) 1fr; }
.viewportFloor { display: grid; grid-template-columns: repeat(auto-fill, minmax(20vw, 1fr)); }
"""


def write_fixture(root: Path, css: str) -> None:
    target = root / "src" / "code-apps" / "fixture-app" / "src" / "styles"
    target.mkdir(parents=True, exist_ok=True)
    (target / "fixture.css").write_text(css, encoding="utf-8")


def selftest() -> int:
    cases = [
        ("A: a rule above base with no line-height FAILS", BAD_FIXTURE, 1),
        ("A: the same rule with a line-height PASSES", GOOD_FIXTURE, 0),
        ("B: an absolute auto-fit floor FAILS", BAD_GRID_FIXTURE, 1),
        ("B: container-relative, viewport and explicit track lists PASS",
         GOOD_GRID_FIXTURE, 0),
    ]
    failures = 0
    for name, css, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, css)
            findings, base, _ = scan(root)
            ok = len(findings) == expected
            print(f"  {'ok  ' if ok else 'FAIL'} {name}: "
                  f"expected {expected}, got {len(findings)}")
            if not ok:
                failures += 1
                for finding in findings:
                    print(f"        {finding}")

    # An empty root must be an ERROR, never a silent PASS. This is IMP-0523: the explicit-root
    # branch found no stylesheets, returned base=None with no findings, and the PASS line
    # formatted None. A gate that reports PASS over nothing is `gate-cannot-fail` (IMP-0007).
    with tempfile.TemporaryDirectory() as tmp:
        code = run(Path(tmp))
        ok = code == 1
        print(f"  {'ok  ' if ok else 'FAIL'} C: a root with no authored stylesheets ERRORS: "
              f"expected exit 1, got {code}")
        if not ok:
            failures += 1

    print(f"verify-css-arithmetic: selftest {len(cases) + 1} fixture(s), {failures} failure(s)")
    return 1 if failures else 0


def run(root: Path) -> int:
    findings, base, file_count = scan(root)

    # IMP-0523. `base` is None whenever the corpus could not be resolved — either no authored
    # stylesheet was found under this root at all, or none declares `--text-base`. Both are
    # refusals, and both must exit non-zero: the old code fell through to the PASS line and
    # raised `TypeError: unsupported format string passed to NoneType.__format__`.
    if file_count == 0:
        print(f"verify-css-arithmetic: ERROR — no authored stylesheet found under {root}. "
              f"This gate scans `<root>/src/code-apps/*/src/**/*.css`; pass the REPOSITORY "
              f"root (the default), not a subdirectory of it. Refusing to report PASS over "
              f"an empty corpus.")
        return 1

    if base is None:
        for finding in findings:
            print(f"verify-css-arithmetic: ERROR — {finding}")
        return 1

    if not findings:
        print(f"verify-css-arithmetic: PASS — {file_count} authored stylesheet(s), ambient "
              f"body size {base:g}px. No rule above it missing a line-height (check A); no "
              f"auto-fit/auto-fill floor that cannot cap its column count (check B).")
        return 0

    for finding in findings:
        print(f"verify-css-arithmetic: {finding}")
    print(f"verify-css-arithmetic: FAILED — {len(findings)} declaration(s) across "
          f"{file_count} authored stylesheet(s).")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(REPO_ROOT),
                        help="repository root to scan (default: this repository)")
    parser.add_argument("--selftest", action="store_true",
                        help="run the fixtures that prove this gate can fail")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    return run(Path(args.root).resolve())


if __name__ == "__main__":
    sys.exit(main())
