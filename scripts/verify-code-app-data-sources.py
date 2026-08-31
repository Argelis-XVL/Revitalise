#!/usr/bin/env python3
"""Every entity set a code app registers to READ must be a declared Dataverse data source.

WHY THIS EXISTS, and why it earns a HARD build step on one finding
-----------------------------------------------------------------
`IMP-0329`. A TAD instructed that a new table "must be registered in the app's READ_SERVICES
map with its generated per-table service", calling it "a compile-and-run requirement, not a
convention". No generated service could exist: `pa app add data-source --connector dataverse
--table <t>` had never been run, and that verb was not among the TAD's own provisioning items —
the flow's equivalent (`pa app add flow`) was listed, because ADR-030 made it a build-time
dependency explicitly. A new Dataverse table read by an existing code app has the identical
dependency and nobody stated it. The screen shipped against a hand-written stand-in service.

**The defect is observable ONLY at V4 — a real signed-in user.** It compiles. It type-checks. It
passes every unit test, because the tests mock the SDK and a mock never resolves a data source.
The Power Apps SDK resolves a Dataverse-type source from the GENERATED `dataSourcesInfo`, so an
unregistered entity set throws at runtime and at no earlier level. This app has already spent
days on one V4-only data-source resolution defect from the other end (`IMP-0187`, `IMP-0191`,
`IMP-0192`, `IMP-0224`).

Comparing two lists that already exist in the tree moves that whole class from "a signed-in user
finds it" to "the build finds it". That is why one finding is enough here: the ladder's
"a tool could catch it mechanically" rung, not an instance count.

WHAT IT CHECKS
--------------
  1. Every key of `READ_SERVICES` in `src/dataverse/client.ts` has a matching entry in
     `.power/schemas/appschemas/dataSourcesInfo.ts` whose `dataSourceType` is `Dataverse`.
     A registration that resolves to nothing is a FAILURE.

  2. It refuses to pass over nothing (`IMP-0007`): a missing file, an unparseable map, or zero
     registrations found is a failure, never a silent OK.

Declared-but-unregistered sources are reported as a NOTE, not a failure — an unused data source
costs nothing and deleting one is a delivery decision, not a gate's.

RESIDUAL, stated because it is real and precisely the distinction `IMP-0224` was logged to draw:
this proves a data source is DECLARED, never that the connection behind it works. A declared
source with a broken connection still fails at V4, and no source-side gate can see that.

EXEMPTIONS LIVE IN THE SHARED REGISTER, NOT ON THIS COMMAND LINE (IMP-0485, IMP-0487)
-------------------------------------------------------------------------------------
This gate used to carry its own `--allow ENTITY=REASON` flag. It was retired on 2026-08-29,
because it was the only exemption channel in this repository that nobody could age.

What happened: this gate CAUGHT the `rev_roundstatisticsresults` defect on first contact and said
so in `logs/build.log` — `code-app-data-sources OK 6/7 (1 declared allowance, ADR-038)` — and an
inline `--allow` on the step's own command line turned that finding into an OK. The app was pushed
to DEV with the stand-in binding live, where the reviewer met a hard error on first load. The
allowance's own text said *"delete this line in the same change as step 9"*; step 9 landed and the
line survived, because a clearing action written as prose in a comment is not a clearing action.
Measured at the time: with the live `--allow` string the gate returned OK over an app whose
registration had been removed; without it, FAILED.

`config/gate-baselines.json` is the governed channel and four other gates already read it. It
requires `gate`, `matches`, `reason`, `owner`, `clears_when` and a dated `expires`; an entry
missing any of them fails, and an EXPIRED entry fails. An exemption suppresses the FAIL and never
the report — every run still prints the finding with its owner, expiry and clearing action cited
against it. `matches` here is the ENTITY SET name, matched exactly.

Usage
-----
    python3 scripts/verify-code-app-data-sources.py <app-root>
    python3 scripts/verify-code-app-data-sources.py --selftest

Exits 0 clean · 1 on any violation or an invalid/expired baseline · 2 on a usage error.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.gate_baseline import Baseline, BaselineError, load_baselines  # noqa: E402

GATE = "code-app-data-sources"

CLIENT_REL = Path("src/dataverse/client.ts")
DATASOURCES_REL = Path(".power/schemas/appschemas/dataSourcesInfo.ts")

# `const READ_SERVICES: Readonly<Record<string, ReadService>> = { ... };`
READ_SERVICES_BLOCK = re.compile(
    r"\bREAD_SERVICES\b[^=]*=\s*\{(?P<body>.*?)\}\s*;", re.DOTALL)
# `  rev_applications: Rev_applicationsService,` — the key is the ENTITY SET name.
REGISTRATION = re.compile(r"^\s*(?:\"|')?(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?:\"|')?\s*:", re.M)

# Top-level keys of the generated `dataSourcesInfo` object, at exactly two-space indent, with
# the `dataSourceType` that follows each one.
DATASOURCE_KEY = re.compile(r'^  "(?P<key>[^"]+)": \{', re.M)
DATASOURCE_TYPE = re.compile(r'"dataSourceType": "(?P<type>[^"]+)"')

DATAVERSE = "Dataverse"


def read_services(app_root: Path) -> tuple[list[str], str]:
    """The entity sets registered for reading. ([], reason) when it cannot be read."""
    path = app_root / CLIENT_REL
    if not path.is_file():
        return [], f"{CLIENT_REL} does not exist under {app_root}"
    text = path.read_text(encoding="utf-8", errors="replace")
    block = READ_SERVICES_BLOCK.search(text)
    if not block:
        return [], (f"no READ_SERVICES map found in {CLIENT_REL}. This gate reads that map by "
                    f"name; if it was renamed, rename it here too rather than leaving the "
                    f"check silently green.")
    keys = [m.group("key") for m in REGISTRATION.finditer(block.group("body"))]
    if not keys:
        return [], f"READ_SERVICES in {CLIENT_REL} parsed to zero registrations"
    return keys, ""


def declared_sources(app_root: Path) -> tuple[dict[str, str], str]:
    """entity set -> dataSourceType, from the GENERATED config the SDK resolves against."""
    path = app_root / DATASOURCES_REL
    if not path.is_file():
        return {}, (f"{DATASOURCES_REL} does not exist under {app_root}. It is generated by "
                    f"`pa app add data-source`; without it the SDK resolves nothing at all.")
    text = path.read_text(encoding="utf-8", errors="replace")
    found: dict[str, str] = {}
    matches = list(DATASOURCE_KEY.finditer(text))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        kind = DATASOURCE_TYPE.search(text[match.end():end])
        found[match.group("key")] = kind.group("type") if kind else "(none declared)"
    if not found:
        return {}, f"{DATASOURCES_REL} parsed to zero data sources"
    return found, ""


def check(app_root: Path, baseline: Baseline) -> tuple[int, list[str]]:
    lines: list[str] = []
    registered, why = read_services(app_root)
    if why:
        return 1, [f"  CANNOT READ REGISTRATIONS - {why}"]
    sources, why = declared_sources(app_root)
    if why:
        return 1, [f"  CANNOT READ DATA SOURCES  - {why}"]

    dataverse = {k for k, v in sources.items() if v == DATAVERSE}

    errors: list[str] = []
    exempt: list[str] = []
    for entity in registered:
        if entity in dataverse:
            continue
        cite = baseline.cite(entity)
        if cite:
            # Suppress the FAIL, never the report. The finding is printed in full, with its
            # owner, its expiry and the action that clears it beside it.
            exempt.append(
                f"  BASELINED: READ_SERVICES registers entity set '{entity}', which does not "
                f"resolve to a Dataverse source in {DATASOURCES_REL}.{cite}")
            continue
        wrong_type = sources.get(entity)
        detail = (f"declared with dataSourceType {wrong_type!r}, not {DATAVERSE!r}"
                  if wrong_type else "not declared at all")
        errors.append(
            f"  UNRESOLVABLE DATA SOURCE - READ_SERVICES registers entity set "
            f"'{entity}', which is {detail} in {DATASOURCES_REL}. The SDK resolves a "
            f"Dataverse source from that generated file, so this throws for a real "
            f"signed-in user and at no earlier level. Run: pa app add data-source "
            f"--connector dataverse --table <the table> -u <org-url> -c <connection-id>, "
            f"then commit the regenerated config (IMP-0329)."
        )

    unregistered = sorted(dataverse - set(registered))
    lines.append(f"  {len(registered)} registration(s), {len(dataverse)} Dataverse source(s) "
                 f"declared")
    if unregistered:
        lines.append(f"  note: declared but not registered for reading — "
                     f"{', '.join(unregistered)}. Not a failure; an unused data source is "
                     f"harmless and removing one is a delivery decision.")
    return (1 if errors else 0), errors + exempt + lines


# ── selftest ──────────────────────────────────────────────────────────────────────────────
# Fixtures prove the gate CAN fail. They do NOT prove it fails on the right things — that is
# the corpus run, and it is an obligation, not a nicety (IMP-0319, and this script's own
# measurement is in improvement review 29 cluster H).

_CLIENT = """
import { Rev_aService } from "../generated/services/Rev_aService";
const READ_SERVICES: Readonly<Record<string, ReadService>> = {
  rev_as: Rev_aService,
  rev_bs: Rev_bStandInService,
};
"""

_SOURCES_BOTH = """
export const dataSourcesInfo = {
  "connectorthing": { "dataSourceType": "Connector", "apis": {} },
  "rev_as": { "primaryKey": "rev_aid", "dataSourceType": "Dataverse", "apis": {} },
  "rev_bs": { "primaryKey": "rev_bid", "dataSourceType": "Dataverse", "apis": {} }
};
"""

_SOURCES_ONE = """
export const dataSourcesInfo = {
  "connectorthing": { "dataSourceType": "Connector", "apis": {} },
  "rev_as": { "primaryKey": "rev_aid", "dataSourceType": "Dataverse", "apis": {} }
};
"""

# The type-confusion case: the name IS declared, as the wrong kind of source. A gate keyed on
# the key alone would pass this, and the SDK would still fail to resolve it.
_SOURCES_WRONG_TYPE = """
export const dataSourcesInfo = {
  "rev_as": { "primaryKey": "rev_aid", "dataSourceType": "Dataverse", "apis": {} },
  "rev_bs": { "dataSourceType": "Connector", "apis": {} }
};
"""

# A well-formed register entry covering `rev_bs`, and the two ways a register entry is refused.
_OWNED = {"gate": GATE, "matches": "rev_bs", "reason": "A-LAND-1, hand-written stand-in service",
          "owner": "development-agent", "clears_when": "pa app add data-source is run for the "
          "table and the generated service replaces the stand-in",
          "expires": "2099-01-01", "finding": "IMP-0485"}
_UNOWNED = {k: v for k, v in _OWNED.items() if k != "owner"}
_EXPIRED = dict(_OWNED, expires="2020-01-01")

_CASES: dict[str, tuple[str | None, str | None, list[dict] | None, int, str]] = {
    # name: (client.ts, dataSourcesInfo.ts, gate-baselines entries, expected rc, substring)
    "every-registration-resolves-passes": (
        _CLIENT, _SOURCES_BOTH, None, 0, "2 registration(s), 2 Dataverse source(s)"),
    "a-registration-with-no-data-source-fails": (
        _CLIENT, _SOURCES_ONE, None, 1, "not declared at all"),
    "a-registration-declared-as-the-WRONG-TYPE-fails": (
        _CLIENT, _SOURCES_WRONG_TYPE, None, 1, "not 'Dataverse'"),
    # The exemption channel, now the shared register. The finding is still PRINTED — the
    # baseline suppresses the failure, never the report.
    "an-owned-register-exemption-passes-and-is-still-REPORTED": (
        _CLIENT, _SOURCES_ONE, [_OWNED], 0, "BASELINED until 2099-01-01, owner development-agent"),
    "an-UNOWNED-register-exemption-is-refused": (
        _CLIENT, _SOURCES_ONE, [_UNOWNED], 1, "missing: owner"),
    "an-EXPIRED-register-exemption-is-refused": (
        _CLIENT, _SOURCES_ONE, [_EXPIRED], 1, "EXPIRED"),
    "a-register-entry-for-ANOTHER-gate-does-not-exempt-anything-here": (
        _CLIENT, _SOURCES_ONE, [dict(_OWNED, gate="some-other-gate")], 1, "not declared at all"),
    # Refusing to pass over nothing (IMP-0007): four ways the inputs can be absent.
    "a-missing-client-file-fails": (
        None, _SOURCES_BOTH, None, 1, "does not exist"),
    "a-missing-datasources-file-fails": (
        _CLIENT, None, None, 1, "does not exist"),
    "a-renamed-READ_SERVICES-map-fails-rather-than-passing-silently": (
        "const OTHER_NAME = { rev_as: X };\n", _SOURCES_BOTH, None, 1,
        "no READ_SERVICES map found"),
    "an-empty-datasources-object-fails": (
        _CLIENT, "export const dataSourcesInfo = {\n};\n", None, 1, "zero data sources"),
}


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, (client, sources, entries, want_rc, want_text) in _CASES.items():
            # Each case gets its own repo root, so config/gate-baselines.json is per-case.
            repo = Path(tmp) / name
            root = repo / "app"
            if client is not None:
                (root / CLIENT_REL.parent).mkdir(parents=True, exist_ok=True)
                (root / CLIENT_REL).write_text(client, encoding="utf-8")
            if sources is not None:
                (root / DATASOURCES_REL.parent).mkdir(parents=True, exist_ok=True)
                (root / DATASOURCES_REL).write_text(sources, encoding="utf-8")
            root.mkdir(parents=True, exist_ok=True)
            if entries is not None:
                (repo / "config").mkdir(parents=True, exist_ok=True)
                (repo / "config/gate-baselines.json").write_text(
                    json.dumps({"baselines": entries}), encoding="utf-8")

            try:
                rc, out = check(root, load_baselines(repo, GATE))
            except BaselineError as exc:
                rc, out = 1, [f"  INVALID EXEMPTION - {exc}"]
            text = "\n".join(out)
            ok = rc == want_rc and want_text in text
            print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {name} → exit {rc} "
                  f"(expected {want_rc})")
            if not ok:
                failures.append(name)
                for line in out:
                    print(f"                   {line}")

        # The retired flag is a USAGE ERROR that names its replacement, not a silent no-op.
        rc = main([str(root), "--allow", "rev_bs=because"])
        ok = rc == 2
        print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"the-retired---allow-flag-is-a-usage-error-naming-the-register → exit {rc} "
              f"(expected 2)")
        if not ok:
            failures.append("retired --allow flag")

    if failures:
        print(f"\nverify-code-app-data-sources: SELFTEST FAILED — {', '.join(failures)}",
              file=sys.stderr)
        return 1
    print(f"\nverify-code-app-data-sources: SELFTEST OK — {len(_CASES) + 1} fixtures. Fixtures "
          f"prove it CAN fail; the corpus run is what proves it fails on the right things.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("app_root", nargs="?", help="code app root, e.g. src/code-apps/my-portal")
    p.add_argument("--allow", action="append", default=[], metavar="ENTITY=REASON",
                   help="RETIRED 2026-08-29 — exemptions live in config/gate-baselines.json")
    p.add_argument("--repo", default=None,
                   help="repository root holding config/gate-baselines.json (default: inferred)")
    p.add_argument("--selftest", action="store_true", help="run the fixture suite and exit")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.allow:
        print(f"verify-code-app-data-sources: --allow was RETIRED on 2026-08-29 and does "
              f"nothing. It was the only exemption channel here with no owner, no clearing "
              f"date and no ageing, and the one exemption taken through it went stale and "
              f"masked a live regression (IMP-0485, IMP-0487). Declare the exemption in "
              f"config/gate-baselines.json instead, with gate \"{GATE}\", matches "
              f"\"<entity-set>\", and a reason, owner, clears_when and dated expires. Refused: "
              f"{', '.join(args.allow)}", file=sys.stderr)
        return 2
    if not args.app_root:
        p.error("an app root is required (or --selftest)")

    root = Path(args.app_root)
    if not root.is_dir():
        print(f"verify-code-app-data-sources: {root} is not a directory", file=sys.stderr)
        return 2

    repo = Path(args.repo) if args.repo else Path(__file__).resolve().parent.parent
    try:
        baseline = load_baselines(repo, GATE)
    except BaselineError as exc:
        print(f"code-app-data-sources: FAILED — config/gate-baselines.json is unusable or an "
              f"entry is invalid: {exc}", file=sys.stderr)
        return 1

    rc, out = check(root, baseline)
    if rc:
        print("code-app-data-sources: FAILED\n" + "\n".join(out), file=sys.stderr)
    else:
        print("code-app-data-sources: OK\n" + "\n".join(out))
    return rc


if __name__ == "__main__":
    sys.exit(main())
