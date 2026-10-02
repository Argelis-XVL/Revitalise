#!/usr/bin/env python3
"""Hold two Code Apps identical on every CONTRACT file, and classify every file (ADR-056, ADR-060).

Run:
    python3 scripts/verify-code-app-variant-parity.py <app-a> <app-b> --config config/code-app-variant-parity.json
    python3 scripts/verify-code-app-variant-parity.py --selftest

WHY THIS EXISTS
---------------
TAD `docs/architecture/trustee-portal-design-2-architecture.md` ships the Design 2.0 card layout as a
SECOND Code App, `src/code-apps/trustee-review-portal-cards`, a full copy of
`src/code-apps/trustee-review-portal` rather than an importer of its source (ADR-055, ADR-056). The copy
is what makes retiring either app one folder deletion (§9.4). Its cost is drift: every contract the
trustee portal holds — the redaction states, the restricted-field catalogue, the visibility conjunction,
the no-secured-column data access, the nav order, the verdict write path — is held by FILES, and a fix
that reaches one folder and not the other silently leaves one app on the old contract.

REVISION 2 OF THE TAD (ADR-060) CHANGED THE SHAPE. Once every screen is redesigned, a per-path
allow-list of the files that may differ is a directory listing, not a statement. So every file is now
classified by glob, once, as one of two kinds:

  contract      must be byte-identical in both apps: data access, domain logic, the shell's markup,
                the design-system components, the verdict path, the tokens, the test setup, and EVERY
                TEST that is not explicitly presentation — so the first app's tests pin the card app's
                content and behaviour;
  presentation  may differ: pages, components, stylesheets, visual specs and their harnesses, the
                card-only modules, per-app identity, and the tests an ADR in the TAD authorises.

WHAT IT CHECKS (TAD §5.3)
------------------------
  P1  every file matching `contract` has the same sha256 in both apps (and exists in both);
  P2  a file present in ONE app only must be `presentation`;
  P3  `power.config.json`: the `databaseReferences` blocks are equal, the connector ids named in
      `connectionReferences` are equal, and the two `appId` values DIFFER. A copied
      `power.config.json` carries the first app's appId, and `pac code push` from the new folder
      would then overwrite the LIVE first app (TAD R-D2-1). A `null` appId in app B passes and is
      reported: the placeholder until the platform assigns one on the first push (A-TR-14);
  P4  every entry (in either list) names a glob, a reason and an ADR, and matches at least one file
      in one of the two apps — a classification that outlives its files stops meaning anything;
  P5  every file in either app matches EXACTLY ONE list. A file in neither fails (an unclassified
      file is a silent divergence waiting to happen); a file in both fails (the classification is
      ambiguous, so the gate cannot say whether it must be identical).

An entry may carry `except`: globs that are removed from what that entry matches. That is how
"every test is contract, except these" is written without a file ever matching both lists.

GLOB GRAMMAR. `**` matches any run of characters including `/`; `*` any run excluding `/`; `?` one
character excluding `/`; `{a,b}` alternation. Paths are relative to the app folder, POSIX separators.

It is a VALUE COMPARISON — hashes and directory listings — never a phrase match. There is no escape
flag: the escape is a committed, reviewed classification entry naming an ADR.

Excluded from the walk (build and install output, never source): node_modules, dist, coverage,
test-results, playwright-report, blob-report, .vite, *.tsbuildinfo, .DS_Store.

WHAT IT DOES NOT PROVE
----------------------
That a presentation file is CORRECT — its own tests and the contract tests that run over it do that.
And it does not look inside the built `dist/` bundles; that is why `package.json` and
`package-lock.json` are contract.

Exit codes: 0 pass · 1 one or more violations · 2 usage or unreadable input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

EXCLUDED_DIRS = {"node_modules", "dist", "coverage", "test-results", "playwright-report",
                 "blob-report", ".vite"}
EXCLUDED_SUFFIXES = (".tsbuildinfo",)
EXCLUDED_NAMES = {".DS_Store"}
POWER_CONFIG = "power.config.json"
KINDS = ("contract", "presentation")


class UsageError(Exception):
    pass


def walk(app: Path) -> dict[str, str]:
    """Relative POSIX path → sha256, for every source file under `app`."""
    found: dict[str, str] = {}
    for path in sorted(app.rglob("*")):
        rel = path.relative_to(app)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if not path.is_file() or path.name in EXCLUDED_NAMES or path.name.endswith(EXCLUDED_SUFFIXES):
            continue
        found[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


_GLOB_CACHE: dict[str, re.Pattern[str]] = {}


def glob_regex(pattern: str) -> re.Pattern[str]:
    cached = _GLOB_CACHE.get(pattern)
    if cached is not None:
        return cached
    out, i = [], 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "{":
            end = pattern.index("}", i)
            out.append("(?:" + "|".join(re.escape(p) for p in pattern[i + 1:end].split(",")) + ")")
            i = end + 1
        else:
            out.append(re.escape(c))
            i += 1
    compiled = re.compile("^" + "".join(out) + "$")
    _GLOB_CACHE[pattern] = compiled
    return compiled


def entry_matches(entry: dict, rel: str) -> bool:
    if not glob_regex(entry["glob"]).match(rel):
        return False
    return not any(glob_regex(ex).match(rel) for ex in entry.get("except", []))


def load_config(path: Path) -> dict[str, list]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UsageError(f"cannot read classification {path}: {exc}") from exc
    if "allow" in data:
        raise UsageError(f"{path}: the Revision 1 `allow` list is retired (ADR-060); use `contract` "
                         f"and `presentation`")
    out = {}
    for kind in KINDS:
        entries = data.get(kind)
        if not isinstance(entries, list):
            raise UsageError(f"{path}: `{kind}` must be a list")
        out[kind] = entries
    return out


def check_power_config(a: Path, b: Path) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    notes: list[str] = []
    configs = []
    for app in (a, b):
        cfg_path = app / POWER_CONFIG
        if not cfg_path.is_file():
            violations.append(f"P3 {app}/{POWER_CONFIG} is missing")
            return violations, notes
        try:
            configs.append(json.loads(cfg_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            violations.append(f"P3 {app}/{POWER_CONFIG} is not valid JSON: {exc}")
            return violations, notes
    ca, cb = configs
    if ca.get("databaseReferences") != cb.get("databaseReferences"):
        violations.append("P3 databaseReferences differ between the two power.config.json files: "
                          "the apps would read different data sources")

    def connector_ids(cfg: dict) -> set[str]:
        refs = cfg.get("connectionReferences") or {}
        return {str(ref.get("id")) for ref in refs.values() if isinstance(ref, dict)}

    if connector_ids(ca) != connector_ids(cb):
        violations.append(f"P3 connector ids differ: {sorted(connector_ids(ca))} vs {sorted(connector_ids(cb))}")
    id_a, id_b = ca.get("appId"), cb.get("appId")
    if id_a is not None and id_a == id_b:
        violations.append(f"P3 both apps carry appId {id_a}: a `pac code push` from {b} would "
                          f"OVERWRITE the live app pushed from {a} (TAD R-D2-1). Never copy "
                          f"power.config.json; leave appId null until the first push assigns one")
    if id_a is None:
        violations.append(f"P3 {a}/{POWER_CONFIG} has no appId: the reference app must be a pushed app")
    if id_b is None:
        notes.append(f"P3 {b} appId is null — the placeholder until the platform assigns one on "
                     f"the first push (A-TR-14); read it back and commit it then")
    return violations, notes


def run(a: Path, b: Path, config_path: Path) -> tuple[int, list[str], list[str]]:
    for app in (a, b):
        if not app.is_dir():
            raise UsageError(f"not a directory: {app}")
    config = load_config(config_path)
    files_a, files_b = walk(a), walk(b)
    every = sorted(set(files_a) | set(files_b))
    violations: list[str] = []

    # P4 first: a malformed entry must not silently classify anything.
    valid: dict[str, list[dict]] = {kind: [] for kind in KINDS}
    for kind in KINDS:
        for index, entry in enumerate(config[kind]):
            where = f"{kind}[{index}]"
            if not isinstance(entry, dict):
                violations.append(f"P4 {where} is not an object")
                continue
            missing = [key for key in ("glob", "reason", "adr")
                       if not isinstance(entry.get(key), str) or not entry[key].strip()]
            if missing:
                violations.append(f"P4 {where} ({entry.get('glob')}) lacks {', '.join(missing)}")
                continue
            if not entry["adr"].startswith("ADR-"):
                violations.append(f"P4 {where} ({entry['glob']}) names no ADR: {entry['adr']!r}")
            if not isinstance(entry.get("except", []), list):
                violations.append(f"P4 {where} ({entry['glob']}) `except` must be a list")
                continue
            if not any(entry_matches(entry, rel) for rel in every):
                violations.append(f"P4 {where} {entry['glob']!r} matches no file in either app — "
                                  f"delete it, or the classification outlives its files")
            valid[kind].append(entry)

    kind_of: dict[str, str] = {}
    for rel in every:
        hits = [kind for kind in KINDS if any(entry_matches(e, rel) for e in valid[kind])]
        if len(hits) == 0:
            violations.append(f"P5 {rel} is in neither list — classify it as contract or presentation, "
                              f"naming the ADR that decides it")
        elif len(hits) == 2:
            violations.append(f"P5 {rel} matches BOTH lists — the classification is ambiguous; add it "
                              f"to an `except` on one side")
        else:
            kind_of[rel] = hits[0]

    identical = 0
    for rel in every:
        kind = kind_of.get(rel)
        in_a, in_b = rel in files_a, rel in files_b
        if not (in_a and in_b):
            if kind == "contract":
                where = a if in_a else b
                violations.append(f"P2 {rel} is contract but exists only in {where} — a contract "
                                  f"file must be in both apps, byte-identical")
            continue
        if files_a[rel] == files_b[rel]:
            identical += 1
        elif kind == "contract":
            violations.append(f"P1 {rel} is contract and differs between the apps — commit the same "
                              f"change to both folders")

    p3, notes = check_power_config(a, b)
    violations += p3
    counts = {kind: sum(1 for k in kind_of.values() if k == kind) for kind in KINDS}
    notes.insert(0, f"{len(files_a)} file(s) in {a}, {len(files_b)} in {b}; {identical} byte-identical; "
                    f"{counts['contract']} contract, {counts['presentation']} presentation; "
                    f"{len(valid['contract'])}+{len(valid['presentation'])} entries")
    return (1 if violations else 0), violations, notes


# ── Self-test: fixtures are ASSEMBLED AT RUNTIME, never committed ─────────────────────────────
def _fixture(root: Path, app_id_b: object = None, files: dict[str, str] | None = None,
             config: dict | None = None) -> tuple[Path, Path, Path]:
    a, b = root / "a", root / "b"
    for app, app_id in ((a, "11111111-1111-1111-1111-111111111111"), (b, app_id_b)):
        (app / "src" / "domain").mkdir(parents=True)
        (app / "src" / "domain" / "visibility.ts").write_text("export const X = 1;\n")
        (app / "src" / "domain" / "visibility.test.ts").write_text("test\n")
        (app / "src" / "pages").mkdir()
        (app / "src" / "pages" / "Page.tsx").write_text(f"page {app.name}\n")
        (app / "node_modules").mkdir()
        (app / "node_modules" / "junk.js").write_text(str(app))  # excluded: must not count
        cfg = {"appId": app_id, "databaseReferences": {"default.cds": {"dataSources": {"t": {}}}},
               "connectionReferences": {"k": {"id": "/providers/x/apis/shared_cds"}}}
        (app / POWER_CONFIG).write_text(json.dumps(cfg))
    (b / "src" / "pages" / "New.tsx").write_text("new\n")
    for rel, content in (files or {}).items():
        path = b / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    cfg_path = root / "classes.json"
    cfg_path.write_text(json.dumps(config or {
        "contract": [
            {"glob": "src/domain/**", "reason": "r", "adr": "ADR-060"},
            {"glob": "**/*.test.ts", "except": ["src/pages/**"], "reason": "r", "adr": "ADR-060"},
        ],
        "presentation": [
            {"glob": "src/pages/**", "reason": "r", "adr": "ADR-060"},
            {"glob": POWER_CONFIG, "reason": "r", "adr": "ADR-056"},
        ],
    }))
    return a, b, cfg_path


def selftest() -> int:
    cases: list[tuple[str, int, object]] = []

    def case(name: str, expected: int):
        def register(fn):
            cases.append((name, expected, fn))
            return fn
        return register

    @case("identical contract files, differing and extra presentation files, null new appId PASS", 0)
    def _(root: Path):
        return _fixture(root)

    @case("a differing contract file FAILS (P1)", 1)
    def _(root: Path):
        return _fixture(root, files={"src/domain/visibility.ts": "export const X = 2;\n"})

    @case("a contract file in one app only FAILS (P2)", 1)
    def _(root: Path):
        return _fixture(root, files={"src/domain/extra.ts": "x\n"})

    @case("a copied appId FAILS (P3)", 1)
    def _(root: Path):
        return _fixture(root, app_id_b="11111111-1111-1111-1111-111111111111")

    @case("differing data sources FAIL (P3)", 1)
    def _(root: Path):
        a, b, cfg = _fixture(root, app_id_b="22222222-2222-2222-2222-222222222222")
        data = json.loads((b / POWER_CONFIG).read_text())
        data["databaseReferences"]["default.cds"]["dataSources"]["extra"] = {}
        (b / POWER_CONFIG).write_text(json.dumps(data))
        return a, b, cfg

    @case("an entry matching no file FAILS (P4)", 1)
    def _(root: Path):
        a, b, cfg = _fixture(root)
        data = json.loads(cfg.read_text())
        data["presentation"].append({"glob": "src/gone/**", "reason": "r", "adr": "ADR-060"})
        cfg.write_text(json.dumps(data))
        return a, b, cfg

    @case("an entry without a reason FAILS (P4)", 1)
    def _(root: Path):
        a, b, cfg = _fixture(root)
        data = json.loads(cfg.read_text())
        data["contract"][0]["reason"] = ""
        cfg.write_text(json.dumps(data))
        return a, b, cfg

    @case("an unclassified file FAILS (P5)", 1)
    def _(root: Path):
        return _fixture(root, files={"README.md": "x\n"})

    @case("a file in both lists FAILS (P5)", 1)
    def _(root: Path):
        a, b, cfg = _fixture(root)
        data = json.loads(cfg.read_text())
        data["contract"][1].pop("except")
        (a / "src" / "pages" / "Page.test.ts").write_text("t\n")
        (b / "src" / "pages" / "Page.test.ts").write_text("t\n")
        cfg.write_text(json.dumps(data))
        return a, b, cfg

    failures = 0
    for name, expected, build in cases:
        root = Path(tempfile.mkdtemp(prefix="parity-selftest-"))
        try:
            a, b, cfg = build(root)
            code, violations, _ = run(a, b, cfg)
        finally:
            shutil.rmtree(root, ignore_errors=True)
        tag = name.split("(")[-1].rstrip(")") if name.endswith(")") else ""
        ok = code == expected and (not tag or any(v.startswith(tag) for v in violations))
        failures += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name} (exit {code}, expected {expected})"
              + ("" if ok else f" — {violations}"))
    print(f"selftest: {len(cases) - failures}/{len(cases)} cases behaved")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("app_a", nargs="?", type=Path, help="the reference app (the pushed one)")
    parser.add_argument("app_b", nargs="?", type=Path, help="the variant held to it")
    parser.add_argument("--config", type=Path, help="the contract/presentation classification JSON")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble fixtures at runtime and prove the gate can fail AND pass")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if args.selftest:
        return selftest()
    if args.app_a is None or args.app_b is None or args.config is None:
        print("usage: verify-code-app-variant-parity.py <app-a> <app-b> --config <classes.json>",
              file=sys.stderr)
        return 2
    try:
        code, violations, notes = run(args.app_a, args.app_b, args.config)
    except UsageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for note in notes:
        print(f"note: {note}")
    for violation in violations:
        print(f"FAIL: {violation}")
    print("code-app-variant-parity: " + ("PASS" if code == 0 else f"FAIL — {len(violations)} violation(s)"))
    return code


if __name__ == "__main__":
    sys.exit(main())
