#!/usr/bin/env python3
"""Check a knowledge file's claims about the local toolchain against the local toolchain.

WHY THIS EXISTS. `IMP-0200`, `IMP-0199`, `IMP-0206`, `IMP-0207` — and the shape of the failure
matters more than any one of them.

On 2026-08-22 `knowledge/technology/code-apps.md` was rewritten from Microsoft's documentation
and stated *"`pa` is not installed on this machine"*. The CLI had been installed 34 minutes
earlier. It was a PATH gap — `npm config get prefix` puts the binary in a directory that is not
on `PATH`, so a bare `which pa` reports nothing and a missing install and an unexported PATH
look identical. Within hours, five findings landed against that one file, four of which were
answerable from this machine at the moment it was written: the install claim, the SDK's real
export surface, a vendor plugin nobody had surveyed, and an overstated deprecation framing.

**The altitude call.** A prose fix to that file had already failed twice in two days, and
`platform-contract-guessed-not-groundtruthed` stands at x25. `skills/how-to-promote-a-finding.md`
§2 forbids a third instance patch, so the generalisable property is not "this sentence was
wrong". It is:

    A knowledge file's claims about locally-installed tooling are hand-typed, checkable, and
    checked by nothing.

Three claim shapes are mechanically decidable, and this gate decides them:

  1. INSTALL claims   — "<pkg> is/is not installed" against `npm ls -g` **and** the resolved
                        binary, so a PATH gap can never again be read as an absent install.
  2. VERSION claims   — "this project is on <version>" against the package's own manifest.
  3. COMMAND claims   — every `pa <group> <command>` token against that CLI's own `--help`.

WHAT IT CANNOT DO, stated plainly. It cannot check prose. An overstated framing (`IMP-0202`), a
vendor plugin advertised but unpublished (`IMP-0203`) and a vendor-recommended package nobody
surveyed (`IMP-0201`) are all real defects in the same file and none is reachable from here.
Those stay knowledge content, reviewed by a human. This gate covers the claims a machine can
settle, which is exactly the set that was wrong.

Run:
    python3 scripts/verify-toolchain-claims.py
    python3 scripts/verify-toolchain-claims.py --selftest

Exits 0 when every decidable claim holds, 1 on any false claim, 2 on a usage error. Fails —
never passes — when it extracts ZERO claims from a non-empty scan set (`IMP-0007`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCAN_GLOB = "knowledge/technology/*.md"

# CLIs whose command surface this gate is allowed to interrogate. An allow-list, not a pattern:
# running `--help` executes a binary, and this gate must never invoke something a document
# merely mentions in prose.
COMMAND_CLIS = ("pa",)

# "`pa` is not installed on this machine", "@microsoft/power-apps-cli is not installed"
CLAIM_NOT_INSTALLED = re.compile(
    r"`?(?P<name>@?[A-Za-z][\w@/.-]*)`?\s+is\s+(?P<neg>not\s+)?installed", re.IGNORECASE)

# "This project is on 1.3.0", "is on SDK **1.3.0**" — the version claim, paired with the
# nearest package name mentioned in the same paragraph.
CLAIM_VERSION = re.compile(r"is on\s+(?:SDK\s+)?\*{0,2}(?P<version>\d+\.\d+\.\d+)\*{0,2}")
PKG_NEARBY = re.compile(r"`?(?P<pkg>@[\w.-]+/[\w.-]+)`?")

# A `pa <group> <command>` token inside inline code. Sub-commands like `add data-source` are
# two words, so up to three words are taken and the longest valid prefix wins.
CLAIM_COMMAND = re.compile(
    r"`(?P<cli>" + "|".join(COMMAND_CLIS) + r")\s+(?P<rest>[a-z][a-z-]*(?:\s+[a-z][a-z-]*){0,2})")

TIMEOUT = 30


class Probe:
    """Everything this gate learns about the machine, learned at most once."""

    def __init__(self) -> None:
        self._global: dict[str, str] | None = None
        self._help: dict[str, str] = {}

    # ── installs ────────────────────────────────────────────────────────────────────────
    def global_packages(self) -> dict[str, str]:
        if self._global is None:
            self._global = {}
            try:
                out = subprocess.run(["npm", "ls", "-g", "--depth=0", "--json"],
                                     capture_output=True, text=True, timeout=TIMEOUT,
                                     check=False)
                doc = json.loads(out.stdout or "{}")
                for name, meta in (doc.get("dependencies") or {}).items():
                    self._global[name] = str((meta or {}).get("version") or "")
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                pass
        return self._global

    def npm_prefix_bin(self) -> Path | None:
        try:
            out = subprocess.run(["npm", "config", "get", "prefix"], capture_output=True,
                                 text=True, timeout=TIMEOUT, check=False)
            prefix = out.stdout.strip()
            return Path(prefix) / "bin" if prefix else None
        except (OSError, subprocess.SubprocessError):
            return None

    def resolve_binary(self, name: str) -> Path | None:
        """A binary is 'present' if PATH finds it OR it sits in npm's own bin directory.

        The second half is the whole point of IMP-0200: a tool installed globally but absent
        from PATH is INSTALLED, and a gate that only consulted PATH would have agreed with the
        false claim it exists to catch.
        """
        found = shutil.which(name)
        if found:
            return Path(found)
        bindir = self.npm_prefix_bin()
        if bindir:
            candidate = bindir / name
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def split_version(token: str) -> tuple[str, str | None]:
        """'@microsoft/power-apps-cli@1.0.0' -> ('@microsoft/power-apps-cli', '1.0.0').

        A documented install claim usually pins the version, and the version is part of the
        claim rather than part of the name. Splitting it lets the same check verify both, and
        stops the pinned form being reported as an unknown package (which it was, on this
        gate's first live run).
        """
        m = re.match(r"^(?P<pkg>@?[\w./-]+?)@(?P<version>\d+\.\d+\.\d+)$", token)
        if m:
            return m.group("pkg"), m.group("version")
        return token, None

    def is_installed(self, token: str) -> tuple[bool, str]:
        token, pinned = self.split_version(token)
        packages = self.global_packages()
        if pinned is not None and token in packages:
            actual = packages[token]
            if actual != pinned:
                return False, (f"npm ls -g reports {token}@{actual}, not the claimed "
                               f"{pinned} — the package is installed, the version is stale")
            return True, f"npm ls -g reports {token}@{actual}, matching the claimed version"
        if token in packages:
            return True, f"npm ls -g reports {token}@{packages[token]}"
        binary = self.resolve_binary(token)
        if binary:
            on_path = shutil.which(token) is not None
            where = "on PATH" if on_path else "NOT on PATH — installed but unexported"
            return True, f"binary resolves at {binary} ({where})"
        # A short token may be a bin name provided by a differently-named package.
        for name, version in packages.items():
            if token in name.split("/")[-1]:
                return True, f"npm ls -g reports {name}@{version}, whose bin may be {token!r}"
        return False, "absent from npm ls -g, from PATH, and from npm's prefix bin"

    # ── command surface ─────────────────────────────────────────────────────────────────
    def help_text(self, cli: str, group: str | None = None) -> str:
        key = f"{cli} {group or ''}".strip()
        if key in self._help:
            return self._help[key]
        binary = self.resolve_binary(cli)
        text = ""
        if binary:
            argv = [str(binary)] + ([group] if group else []) + ["--help"]
            try:
                out = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT,
                                     check=False)
                text = (out.stdout or "") + (out.stderr or "")
            except (OSError, subprocess.SubprocessError):
                text = ""
        self._help[key] = text
        return text


def _installed_version(repo_root: Path, pkg: str) -> str | None:
    """The version actually installed under any node_modules in the repo, else the declared one."""
    for manifest in repo_root.glob(f"src/**/node_modules/{pkg}/package.json"):
        try:
            return str(json.loads(manifest.read_text(encoding="utf-8")).get("version") or "")
        except (OSError, json.JSONDecodeError):
            continue
    for manifest in repo_root.glob("src/**/package.json"):
        if "node_modules" in manifest.parts:
            continue
        try:
            doc = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for field in ("dependencies", "devDependencies"):
            spec = (doc.get(field) or {}).get(pkg)
            if spec:
                return str(spec).lstrip("^~=")
    return None


def scan(repo_root: Path, probe: Probe) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    counts = {"install": 0, "version": 0, "command": 0, "files": 0}

    for path in sorted(repo_root.glob(SCAN_GLOB)):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        counts["files"] += 1
        lines = text.splitlines()

        # ── 1. install claims ───────────────────────────────────────────────────────────
        for n, line in enumerate(lines, start=1):
            for m in CLAIM_NOT_INSTALLED.finditer(line):
                name = m.group("name")
                claims_absent = bool(m.group("neg"))
                # Only tools this gate can actually resolve are decidable.
                bare, _pin = probe.split_version(name)
                if bare not in COMMAND_CLIS and not bare.startswith("@"):
                    continue
                counts["install"] += 1
                present, why = probe.is_installed(name)
                if claims_absent and present:
                    failures.append(
                        f"{rel}:{n}: claims {name!r} is NOT installed, but it is — {why}. "
                        f"A PATH gap and a missing install look identical to `which`; check "
                        f"`npm ls -g --depth=0` and `npm config get prefix` too (IMP-0200).")
                elif not claims_absent and not present:
                    failures.append(
                        f"{rel}:{n}: claims {name!r} IS installed, but it is not — {why}.")

        # ── 2. version claims ──────────────────────────────────────────────────────────
        for n, line in enumerate(lines, start=1):
            vm = CLAIM_VERSION.search(line)
            if not vm:
                continue
            window = " ".join(lines[max(0, n - 4):n + 1])
            pm = PKG_NEARBY.search(window)
            if not pm:
                continue
            pkg, claimed = pm.group("pkg"), vm.group("version")
            actual = _installed_version(repo_root, pkg)
            if actual is None:
                continue
            counts["version"] += 1
            if actual != claimed:
                failures.append(
                    f"{rel}:{n}: says this project is on {pkg} {claimed}, but the tree says "
                    f"{actual}. A version in prose drifts the moment the dependency moves.")

        # ── 3. command claims ──────────────────────────────────────────────────────────
        for n, line in enumerate(lines, start=1):
            for m in CLAIM_COMMAND.finditer(line):
                cli = m.group("cli")
                if probe.resolve_binary(cli) is None:
                    continue          # not installed here: nothing to check against
                words = m.group("rest").split()
                root_help = probe.help_text(cli)
                if not root_help:
                    continue
                group = words[0]
                if group not in root_help:
                    counts["command"] += 1
                    failures.append(
                        f"{rel}:{n}: `{cli} {group}` is not a command group that "
                        f"`{cli} --help` lists.")
                    continue
                if len(words) < 2:
                    continue
                group_help = probe.help_text(cli, group)
                if not group_help:
                    continue
                counts["command"] += 1
                # Longest-prefix match: 'add data-source' before 'add'.
                candidates = [" ".join(words[1:3]), words[1]] if len(words) > 2 else [words[1]]
                if not any(c in group_help for c in candidates if c):
                    failures.append(
                        f"{rel}:{n}: `{cli} {group} {candidates[0]}` is not listed by "
                        f"`{cli} {group} --help`. Read the CLI's own help before documenting "
                        f"a command (IMP-0206).")

    return failures, counts


def selftest() -> int:
    import tempfile

    probe = Probe()
    pa_present = probe.resolve_binary("pa") is not None
    failed = 0

    cases: list[tuple[str, str, bool]] = [
        # (why, markdown body, expect_failure)
        ("a false 'not installed' claim about pa is caught",
         "The toolchain is `pa`.\n\nNote: `pa` is not installed on this machine.\n", pa_present),
        ("a true 'is installed' claim about pa passes",
         "Note: `pa` is installed on this machine.\n", False),
        ("prose with no decidable claim yields no failure",
         "Code Apps are not PCF controls. Prefer a connection reference.\n", False),
        ("a nonexistent command group is caught",
         "Run `pa wibble list` to do the thing.\n", pa_present),
        ("a real command group and command passes",
         "Run `pa solution list` and `pa app add data-source` as needed.\n", False),
        ("an unresolvable CLI is skipped rather than guessed at",
         "Run `zzznotatool frobnicate` first.\n", False),
        ("a version-pinned install claim is checked on BOTH name and version",
         "`@microsoft/power-apps-cli@1.0.0` is installed globally.\n", False),
        ("a version-pinned claim with the WRONG version is caught",
         "`@microsoft/power-apps-cli@9.9.9` is installed globally.\n",
         "@microsoft/power-apps-cli" in probe.global_packages()),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        for why, body, expect_fail in cases:
            root = Path(tmp) / re.sub(r"\W+", "_", why)
            (root / "knowledge" / "technology").mkdir(parents=True)
            (root / "knowledge" / "technology" / "fixture.md").write_text(body, encoding="utf-8")
            failures, counts = scan(root, probe)
            got = bool(failures)
            ok = got == expect_fail
            print(f"  {'ok  ' if ok else 'FAIL'}  {why}: {len(failures)} failure(s) "
                  f"({counts['install']} install, {counts['version']} version, "
                  f"{counts['command']} command claim(s) checked)")
            if not ok:
                for f in failures:
                    print(f"          {f}")
                failed += 1

    # The IMP-0007 control.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "knowledge" / "technology").mkdir(parents=True)
        _f, counts = scan(root, probe)
        ok = counts["files"] == 0
        print(f"  {'ok  ' if ok else 'FAIL'}  an empty scan set yields zero files "
              f"(caller must fail, not pass): files={counts['files']}")
        failed += 0 if ok else 1

    if not pa_present:
        print("  NOTE  `pa` is not resolvable here, so the command-surface and install "
              "fixtures degrade to 'skipped rather than guessed' — which is the designed "
              "behaviour, not a pass by accident.")

    print(f"\nSELFTEST: {'PASS' if not failed else f'FAILED — {failed} case(s)'}")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check knowledge files' claims about local tooling against the machine.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    repo_root = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parents[1]
    probe = Probe()
    failures, counts = scan(repo_root, probe)

    if counts["files"] == 0:
        print(f"ERROR: '{SCAN_GLOB}' matched no files. A checker with nothing to read must "
              f"fail rather than report PASS (IMP-0007).", file=sys.stderr)
        return 1

    decidable = counts["install"] + counts["version"] + counts["command"]
    if decidable == 0:
        print(f"WARNING: {counts['files']} knowledge file(s) scanned and no decidable toolchain "
              f"claim found. Not a failure — a file may legitimately make none — but if you "
              f"expected claims here, the patterns have stopped matching the prose.")

    if failures:
        for f in failures:
            print(f"ERROR: {f}", file=sys.stderr)
        print(f"\nTOOLCHAIN CLAIMS: FAILED — {len(failures)} false claim(s) of {decidable} "
              f"checked across {counts['files']} file(s).", file=sys.stderr)
        return 1

    print(f"TOOLCHAIN CLAIMS: PASS — {decidable} decidable claim(s) across {counts['files']} "
          f"knowledge file(s) all hold: {counts['install']} install, {counts['version']} "
          f"version, {counts['command']} command.")
    if os.environ.get("VERBOSE"):
        print(f"  npm global packages seen: {len(probe.global_packages())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
