#!/usr/bin/env python3
"""Assert that a code app's composition root loads what the app ships, and that its test
harness composes what the composition root composes.

THE GENERAL GATE FOR CLASS `no-assertion-on-shipped-content`, code-app half (x15 in
logs/known-failure-modes.md). Two of those instances are the same blind spot from opposite
sides, and the second is the third file to carry it:

  * `IMP-0353` — `src/test/harness.tsx` rendered every component test inside
    `<FluentProvider theme={webLightTheme}>` while the app ships `brandTheme`. So 372 passing
    tests asserted markup under design tokens production does not use, `theme.ts` showed 0
    covered statements, and switching the harness to the shipped theme moved total coverage from
    96.42% to 98.53% with no new production code. Nothing connects "the composition root uses X"
    to "the harness uses X".
  * `IMP-0390` — TAD Revision 4's `A-R38` named the risk correctly (a global stylesheet imported
    only from `main.tsx` leaves the harness asserting markup the app never produces) and
    prescribed a mitigation that CANNOT DETECT IT. Every token assertion reads `ds-tokens.css`
    off disk, so deleting the `import "./styles/ds-tokens.css"` line from `main.tsx` leaves all
    29 passing while the running app renders every `var(--space-6)` in seven components as
    nothing. `brand.css` and `print.css` have carried the same exposure since they were written;
    `ds-tokens.css` is the third instance and the fix that shipped for it covers only the third.

Per `skills/how-to-promote-a-finding.md` §2 the third instance may not get another instance
patch. The property, independent of the instance: **a stylesheet the app ships is loaded by the
composition root, and the harness composes the same theme the composition root composes** — both
derived from disk, never from a hand-typed list. That is what this checks.

WHAT IT CHECKS, per code app under the given root — TWO checks:

  A. every non-module stylesheet under the app's `src/` is side-effect imported by its
     composition root (`src/main.tsx`). HARD. Separately, any stylesheet the composition root
     imports that the test harness does not is REPORTED and does not fail — see below;
  B. the test harness renders the same theme object the composition root renders. HARD.

WHY CHECK A DOES NOT FAIL ON HARNESS DIVERGENCE, WHICH IS HOW IT WAS PROPOSED.
Measured against the real tree before wiring, today's app imports three global stylesheets from
`main.tsx` and ONE of them from `src/test/harness.tsx` — and both files carry comments asserting
that all three are imported in the same change ("`src/test/harness.tsx` imports the same three
files in the same change, so the two module graphs cannot diverge (A-R38)"). `vitest.config.ts`
sets no `css` option, so vitest processes no CSS at all and nothing at runtime depends on the
harness import: **the claim is wrong, not the code.** Failing a build over it would demand a
change with no runtime effect; reporting it hands the two false comments to their owner. That
handover is recorded in improvement review 33 §5, owner `frontend-agent`.

WHY CHECK B COMPARES THEMES AND NOT PROVIDERS, WHICH IS ALSO HOW IT WAS PROPOSED.
As first specified — "the harness renders every provider the composition root renders" — it
measured **1 finding, 0 true, 1 false**: its only finding was `PowerProvider`, which the harness
omits CORRECTLY, because it injects a fake repository and has no SDK to configure. The shipped
form compares the theme prop only, which is `IMP-0353`'s actual defect, and removes that false
positive by name.

RESIDUAL, and it matters: check A proves a stylesheet is IMPORTED, never that a token in it
resolves at runtime — under this vitest config nothing can. Check B compares the theme
IDENTIFIER and the module it is imported from, not the object's contents; `theme.test.ts` pins
the values. And both read `main.tsx` as text: a composition root that assembled its provider
tree dynamically would be invisible to this gate, and no code app here does.

Run:
    python3 scripts/verify-code-app-composition-root.py src/code-apps
    python3 scripts/verify-code-app-composition-root.py --selftest   # prove it can fail

Exits 0 when every app is clean, 1 on any violation or unreadable input, 2 on a usage error.
Fails — never passes — when it finds no code apps at all, so it cannot report OK over an empty
tree (IMP-0007). C-TECH-057, C-TECH-067.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

# A side-effect import: `import "./styles/ds-tokens.css";` — no binding, just the specifier.
_SIDE_EFFECT_IMPORT = re.compile(r"""^\s*import\s+["']([^"']+)["']\s*;?\s*$""", re.MULTILINE)

# `theme={brandTheme}` on a FluentProvider. Deliberately not a JSX parser: this reads the one
# prop whose divergence IMP-0353 recorded, and reports honestly when it cannot find it.
_THEME_PROP = re.compile(r"theme\s*=\s*\{\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*\}")

# `import { brandTheme } from "../theme";` — the module a theme identifier comes from, so a
# harness importing a DIFFERENT module that happens to export the same name is still caught.
_NAMED_IMPORT = re.compile(
    r"""import\s*\{([^}]*)\}\s*from\s*["']([^"']+)["']""", re.MULTILINE)

# Directories that are build output or dependencies, never source.
_NOT_SOURCE = {"node_modules", "dist", "coverage", "build", ".power", ".vite"}

_COMPOSITION_ROOT = "main.tsx"
_HARNESS = Path("test") / "harness.tsx"


def _is_module_stylesheet(path: Path) -> bool:
    """A CSS Module is imported for its exported class names, not for its side effect."""
    return path.name.endswith(".module.css")


def _app_stylesheets(src: Path) -> list[Path]:
    return sorted(
        p for p in src.rglob("*.css")
        if not _is_module_stylesheet(p)
        and not any(part in _NOT_SOURCE for part in p.relative_to(src).parts))


def _side_effect_imports(text: str) -> list[str]:
    return _SIDE_EFFECT_IMPORT.findall(text)


def _resolve(importer: Path, specifier: str) -> Path | None:
    if not specifier.startswith("."):
        return None
    return (importer.parent / specifier).resolve()


def _imported_stylesheets(source_file: Path) -> set[Path]:
    try:
        text = source_file.read_text(encoding="utf-8")
    except OSError:
        return set()
    found = set()
    for specifier in _side_effect_imports(text):
        if not specifier.endswith(".css"):
            continue
        resolved = _resolve(source_file, specifier)
        if resolved is not None:
            found.add(resolved)
    return found


def _theme_source(source_file: Path) -> tuple[str | None, str | None]:
    """(theme identifier rendered, module it is imported from) for one file."""
    try:
        text = source_file.read_text(encoding="utf-8")
    except OSError:
        return None, None
    match = _THEME_PROP.search(text)
    if match is None:
        return None, None
    identifier = match.group(1)
    for names, module in _NAMED_IMPORT.findall(text):
        bound = [n.strip().split(" as ")[-1].strip() for n in names.split(",")]
        if identifier in bound:
            return identifier, module
    return identifier, None


def _module_identity(importer: Path, module: str | None) -> str | None:
    """Normalise a relative module specifier to a repo-relative path, so `./theme` in main.tsx
    and `../theme` in test/harness.tsx compare equal."""
    if module is None:
        return None
    if not module.startswith("."):
        return module
    return str((importer.parent / module).resolve())


def check_app(app: Path) -> tuple[list[str], list[str]]:
    """(errors, reports) for one code app."""
    errors: list[str] = []
    reports: list[str] = []
    src = app / "src"
    if not src.is_dir():
        return ([f"{app}: has no src/ directory, so nothing identifies its composition root. A "
                 "gate pointed at a missing target does not fail (IMP-0007)."], reports)

    root = src / _COMPOSITION_ROOT
    if not root.is_file():
        return ([f"{app}: no composition root at src/{_COMPOSITION_ROOT}. Check A and check B "
                 "both read it, and a gate that cannot find its input must fail rather than "
                 "report OK (IMP-0007)."], reports)

    # ── A. every shipped stylesheet is loaded by the composition root ────────────────────
    stylesheets = _app_stylesheets(src)
    if not stylesheets:
        errors.append(
            f"{app}: no non-module stylesheet found under src/. This gate exists because three "
            "of them were unguarded; finding none means the enumeration is wrong, not that the "
            "app is clean (IMP-0007).")
    root_imports = _imported_stylesheets(root)
    for stylesheet in stylesheets:
        if stylesheet.resolve() not in root_imports:
            errors.append(
                f"{app}: src/{stylesheet.relative_to(src)} is a global stylesheet the app ships "
                f"and src/{_COMPOSITION_ROOT} does not side-effect import it. A disk-read token "
                "test proves what the file SAYS, never that anything loads it — deleting the "
                "import leaves every such assertion passing while the running app renders every "
                "custom property in it as nothing (IMP-0390).")

    # ── A'. harness stylesheet divergence: REPORTED, never failed. See the docstring. ────
    harness = src / _HARNESS
    if harness.is_file():
        harness_imports = _imported_stylesheets(harness)
        missing = sorted(root_imports - harness_imports)
        for stylesheet in missing:
            try:
                shown = stylesheet.relative_to(src.resolve())
            except ValueError:
                shown = stylesheet
            reports.append(
                f"{app}: src/{_COMPOSITION_ROOT} imports {shown} and src/{_HARNESS} does not. "
                "Not a failure: vitest processes no CSS under this config, so nothing at "
                "runtime depends on it. Reported because both files carry comments asserting "
                "that all of them are imported in the same change — the CLAIM is wrong, not the "
                "code, and a false comment about a guard is how A-R38 produced a mitigation "
                "that could not fail (IMP-0390).")

    # ── B. the harness renders the theme the composition root renders ───────────────────
    if harness.is_file():
        root_theme, root_module = _theme_source(root)
        harness_theme, harness_module = _theme_source(harness)
        if root_theme is None:
            reports.append(
                f"{app}: no `theme={{…}}` prop found in src/{_COMPOSITION_ROOT}, so check B did "
                "not run for this app. Reported rather than passed silently.")
        elif harness_theme is None:
            errors.append(
                f"{app}: src/{_COMPOSITION_ROOT} renders theme `{root_theme}` and "
                f"src/{_HARNESS} renders no theme at all. Every rendering test then asserts "
                "markup under Fluent's defaults rather than the tokens the app ships "
                "(IMP-0353).")
        elif harness_theme != root_theme or (
                _module_identity(root, root_module) != _module_identity(harness, harness_module)):
            errors.append(
                f"{app}: src/{_COMPOSITION_ROOT} renders theme `{root_theme}` from "
                f"{root_module!r} and src/{_HARNESS} renders `{harness_theme}` from "
                f"{harness_module!r}. A harness that renders a different theme from production "
                "means every rendering test asserts markup the app never produces — 372 tests "
                "did exactly that, and the file naming the shipped theme was also the one file "
                "nothing measured (IMP-0353).")

    return errors, reports


def _code_apps(root: Path) -> list[Path]:
    if (root / "src" / _COMPOSITION_ROOT).is_file():
        return [root]
    # `p` is the main.tsx itself, so the APP root is two levels up — p.parent is src/. Getting
    # this wrong made every check report "has no src/ directory" against a tree that has one,
    # and the self-test is what caught it.
    return sorted(p.parent.parent for p in root.glob(f"*/src/{_COMPOSITION_ROOT}"))


def run(root: Path) -> int:
    if not root.is_dir():
        print(f"code-app-composition-root: FAILED — {root} is not a directory. A gate pointed "
              "at a missing target does not fail (IMP-0007).", file=sys.stderr)
        return 1

    apps = _code_apps(root)
    if not apps:
        print(f"code-app-composition-root: FAILED — no code app found under {root} (nothing "
              f"matching */src/{_COMPOSITION_ROOT}). A gate with nothing to check must not "
              "report OK (IMP-0007).", file=sys.stderr)
        return 1

    errors: list[str] = []
    reports: list[str] = []
    stylesheet_count = 0
    for app in apps:
        stylesheet_count += len(_app_stylesheets(app / "src"))
        app_errors, app_reports = check_app(app)
        errors += app_errors
        reports += app_reports

    for report in reports:
        print(f"REPORT: {report}", file=sys.stderr)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\ncode-app-composition-root: FAILED — {len(errors)} divergence(s) across "
              f"{len(apps)} code app(s) between what the app ships and what its composition "
              "root or test harness loads.", file=sys.stderr)
        return 1

    suffix = (f" {len(reports)} harness divergence(s) REPORTED above and NOT covered by this OK."
              if reports else "")
    print(f"code-app-composition-root: OK — {len(apps)} code app(s), {stylesheet_count} global "
          "stylesheet(s): every one side-effect imported by its composition root, and every "
          "harness renders the theme its composition root renders. NOTE: check A proves a "
          "stylesheet is IMPORTED, never that a token in it resolves at runtime — vitest "
          f"processes no CSS under this config (IMP-0390).{suffix}")
    return 0


# ── Self-test: the gate must be able to fail (C-TECH-057) ────────────────────

_MAIN_GOOD = '''
import { FluentProvider } from "@fluentui/react-components";
import { brandTheme } from "./theme";
import "./styles/ds-tokens.css";
import "./styles/brand.css";
createRoot(container).render(<FluentProvider theme={brandTheme}><App /></FluentProvider>);
'''

_HARNESS_GOOD = '''
import { FluentProvider } from "@fluentui/react-components";
import { brandTheme } from "../theme";
import "../styles/ds-tokens.css";
import "../styles/brand.css";
export function renderWithProviders(ui) {
  return render(<FluentProvider theme={brandTheme}>{ui}</FluentProvider>);
}
'''

# IMP-0353's exact shape: the harness renders Fluent's default, not the shipped theme.
_HARNESS_WRONG_THEME = _HARNESS_GOOD.replace(
    'import { brandTheme } from "../theme";',
    'import { webLightTheme } from "@fluentui/react-components";').replace(
    "theme={brandTheme}", "theme={webLightTheme}")

_HARNESS_NO_THEME = '''
import { render } from "@testing-library/react";
import "../styles/ds-tokens.css";
import "../styles/brand.css";
export function renderWithProviders(ui) { return render(ui); }
'''

# The same identifier from a DIFFERENT module — a divergence a name comparison alone misses.
_HARNESS_SHADOWED_THEME = _HARNESS_GOOD.replace(
    'from "../theme"', 'from "../test/localTheme"')


def _make_app(app: Path, main: str, harness: str | None,
              stylesheets: tuple[str, ...] = ("ds-tokens.css", "brand.css"),
              modules: tuple[str, ...] = ("app.module.css",)) -> None:
    (app / "src" / "styles").mkdir(parents=True)
    for name in stylesheets + modules:
        (app / "src" / "styles" / name).write_text(":root { --x: 1px; }", encoding="utf-8")
    (app / "src" / _COMPOSITION_ROOT).write_text(main, encoding="utf-8")
    if harness is not None:
        (app / "src" / "test").mkdir(parents=True)
        (app / "src" / _HARNESS).write_text(harness, encoding="utf-8")


def selftest() -> int:
    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        def case(label: str, expected: int, **kwargs) -> None:
            app = base / f"case{len(checks)}" / "app"
            _make_app(app, **kwargs)
            checks.append((label, run(app.parent) == expected))

        case("check A: a stylesheet the composition root does not import is rejected", 1,
             main=_MAIN_GOOD.replace('import "./styles/brand.css";\n', ""),
             harness=_HARNESS_GOOD)
        case("check A: every stylesheet imported by the composition root PASSES", 0,
             main=_MAIN_GOOD, harness=_HARNESS_GOOD)
        case("check A: a *.module.css is EXCLUDED — imported for its class names, not its "
             "side effect, so requiring a side-effect import would be wrong", 0,
             main=_MAIN_GOOD, harness=_HARNESS_GOOD)
        case("check A': a stylesheet the HARNESS omits is reported and does NOT fail", 0,
             main=_MAIN_GOOD,
             harness=_HARNESS_GOOD.replace('import "../styles/brand.css";\n', ""))
        case("check B: a harness rendering webLightTheme against a shipped brandTheme is "
             "rejected — IMP-0353's exact shape", 1,
             main=_MAIN_GOOD, harness=_HARNESS_WRONG_THEME)
        case("check B: a harness rendering NO theme is rejected", 1,
             main=_MAIN_GOOD, harness=_HARNESS_NO_THEME)
        case("check B: the same theme NAME from a different MODULE is rejected", 1,
             main=_MAIN_GOOD, harness=_HARNESS_SHADOWED_THEME)
        case("check B: an app with no harness is out of scope for check B and PASSES", 0,
             main=_MAIN_GOOD, harness=None)
        case("check B does NOT compare providers: a harness omitting PowerProvider PASSES — "
             "measured at 1 finding / 0 true / 1 false as first specified", 0,
             main=_MAIN_GOOD.replace(
                 "<FluentProvider", "<PowerProvider><FluentProvider").replace(
                 "</FluentProvider>", "</FluentProvider></PowerProvider>"),
             harness=_HARNESS_GOOD)
        case("an app whose src/ holds NO non-module stylesheet FAILS rather than reporting a "
             "clean enumeration", 1,
             main=_MAIN_GOOD, harness=_HARNESS_GOOD, stylesheets=())

        empty = base / "empty"
        empty.mkdir()
        checks.append(("a tree with no code app FAILS", run(empty) == 1))
        checks.append(("a missing directory FAILS", run(base / "nope") == 1))

        no_root = base / "no-root" / "app" / "src"
        no_root.mkdir(parents=True)
        checks.append(("an app directory with no main.tsx is not mistaken for a code app, so "
                       "the tree FAILS as empty", run(base / "no-root") == 1))

    print("\n── SELFTEST ────────────────────────────────────────────────────────────────")
    for label, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {label}")
    failed = [c for c in checks if not c[1]]
    if failed:
        print(f"\ncode-app-composition-root selftest: FAILED — {len(failed)} check(s)",
              file=sys.stderr)
        return 1
    print(f"\ncode-app-composition-root selftest: OK — {len(checks)} check(s); the gate can "
          "fail.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", help="src/code-apps, or one app directory")
    parser.add_argument("--selftest", action="store_true",
                        help="prove this gate can fail, then exit")
    args = parser.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if not args.root:
        parser.print_usage(sys.stderr)
        return 2
    return run(Path(args.root.rstrip("/")))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
