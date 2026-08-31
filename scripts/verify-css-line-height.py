#!/usr/bin/env python3
"""C-TECH-076 — a CSS rule setting a font-size larger than the ambient body size declares
its own line-height.

WHY THIS EXISTS (IMP-0486, IMP-0509)
------------------------------------
A Code App renders inside FluentProvider, whose root sets `line-height: 22px` — a value tuned
for Fluent's own base font size. Any authored rule that raises `font-size` above the ambient
body size and does NOT set a `line-height` inherits that 22px. At `--text-xl: 24px` the line
box is SMALLER THAN THE GLYPHS, so wrapped lines overlap. At `--text-lg: 20px` the ratio is
1.1, below the ~1.2 a descender needs.

This is arithmetic, not taste, and that is the whole reason it is gateable where the other 21
members of `no-assertion-on-shipped-content` were not. jsdom computes no layout, so no vitest
assertion can see it; `IMP-0509` was found by a human looking at a rendered screen.

WHAT IT ASSERTS — A VALUE, NOT A PHRASE
---------------------------------------
The ambient body size is READ from the token file's own `--text-base` declaration, never
transcribed, so re-tuning the scale re-tunes the gate. Every `font-size` is resolved through
the same token table. `clamp()` is judged on its MAXIMUM, which is the size that overlaps.

SCOPE, and why it is this narrow (measured, see the review document)
--------------------------------------------------------------------
Authored stylesheets only — `src/code-apps/*/src/**/*.css`. Run over everything under
`src/code-apps/` the candidate reported 77 findings across 17 files, dominated by
`node_modules/` and a `dist/` bundle that re-reports every authored rule. Restricted to
authored sources but flagging every missing `line-height` it reported 23, most of them at
13-17px where inheriting 22px is harmless or generous. Both numbers teach a reader to ignore
the gate. Flagging only sizes ABOVE the ambient base reports 2, both true.

RESIDUAL, stated because it is not covered: this reads ONE rule at a time and cannot see an
INHERITED line-height. A rule that inherits a correct line-height from a parent selector is a
false positive by construction. Measured at zero in this corpus, but the shape exists — fix
such a case by declaring the line-height on the rule, not by exempting the gate.
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


def strip_comments(text: str) -> str:
    """Blank out comments, PRESERVING newlines so reported line numbers stay true.

    Without this a rule's `selector` capture swallows the whole comment block above it —
    this file's stylesheets carry 25-line explanatory comments before a rule — and the
    finding message becomes unreadable. The defect was caught by running the gate over the
    real corpus, not by the fixtures.
    """
    return COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)

DEFAULT_ROOT_FONT_PX = 16.0  # for rem; the browser default this project does not override


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


def write_fixture(root: Path, css: str) -> None:
    target = root / "src" / "code-apps" / "fixture-app" / "src" / "styles"
    target.mkdir(parents=True, exist_ok=True)
    (target / "fixture.css").write_text(css, encoding="utf-8")


def selftest() -> int:
    cases = [
        ("a rule above base with no line-height FAILS", BAD_FIXTURE, 1),
        ("the same rule with a line-height PASSES", GOOD_FIXTURE, 0),
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
    print(f"verify-css-line-height: selftest {len(cases)} fixture(s), {failures} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(REPO_ROOT),
                        help="repository root to scan (default: this repository)")
    parser.add_argument("--selftest", action="store_true",
                        help="run the fixtures that prove this gate can fail")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    root = Path(args.root).resolve()
    findings, base, file_count = scan(root)

    if base is None and findings:
        for finding in findings:
            print(f"verify-css-line-height: ERROR — {finding}")
        return 1

    if not findings:
        print(f"verify-css-line-height: PASS — {file_count} authored stylesheet(s), ambient "
              f"body size {base:g}px, no rule above it missing a line-height.")
        return 0

    for finding in findings:
        print(f"verify-css-line-height: {finding}")
    print(f"verify-css-line-height: FAILED — {len(findings)} rule(s) across {file_count} "
          f"authored stylesheet(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
