#!/usr/bin/env python3
"""Verify a source-derived count stated in prose still matches the source it describes.

WHY THIS EXISTS. A count of source-derived items, written by hand into a sentence, drifts from
the source it describes and nothing has ever compared the two (IMP-0150, IMP-0160). Two measured
instances on this tree:

  * `config/revitalise-grant-automation-pipeline.yml` says "the eleven rev_setting rows" at two
    post-deploy steps. All three deployment-settings files that carry a `settingRows` array
    (`dev-scoring-settings.json`, `test-settings.json`, `prd-settings.json`) actually hold 14.
  * Five documents state the number of columns `REV_TrusteeRestricted` secures as 39 (one of
    them, the REV Trustee role file's own header, written the same day this gate was built).
    Source — `FieldSecurityProfiles.xml` — holds 51 `FieldPermission` entries, matching 51
    `IsSecured=1` columns across every `Entity.xml`. 39 was correct until twelve more secured
    columns landed on 2026-08-18 (`rev_grant`).

Both instances are the same class: `hand-maintained-count-drifts-from-source`, second occurrence,
so the altitude rule ("second instance -> generalise") forbids patching the two numbers and
requires this gate instead — a declared REGISTRY of (claim location, derivation), not one script
per claim. Registering a third claim is a new row in `scripts/derived-counts-registry.json`,
never a change to this file.

WHY THIS IS DELIBERATELY SOFT, NOT HARD. A stale number in prose misleads a human; it does not
break anything at runtime — the executable checks this project already has (Pester assertions,
`verify-field-security-coverage.py`) derive their own counts from source and are unaffected by a
sentence being wrong. A HARD gate over prose would block a deploy on a comment, which is a
disproportionate response to a defect class whose entire cost is someone reading a stale number
and believing it. The commercial side of this system already made the identical call —
`C-COM-008`, "never restate a baseline figure, cite the generated one" — and this is that rule
applied to technical counts rather than billed hours.

WHAT ITS EXIT CODE MEANS, AND HOW A CALLER SHOULD TREAT IT. This script follows the same
0/1/2 convention as every other gate in `scripts/`, but a caller wrapping it in a build or
pipeline step must NOT treat exit 1 as BLOCKED — only as WARN, appended to the gate output for a
human to accept or correct (constraints/README.md's SOFT severity: "the agent MAY proceed past
its gate but MUST document the violation"). Concretely:

  * exit 0 — every registered claim's number matches what its derivation recomputes right now.
  * exit 1 — one of two THINGS was found, both printed and both worth reporting, but NEITHER
    should stop a build or a deploy:
      - a DRIFT: a claim's number and the recomputed truth disagree (the defect this gate exists
        to catch), or
      - a REGISTRY DEFECT: the registry is empty, a row's target file does not exist, or a row's
        pattern no longer matches anything in its claim_file. This is the IMP-0007 shape —
        "a gate that reports OK over nothing is this project's most-recorded defect class" — so
        it is surfaced as a finding, not swallowed. Unlike a drift, a registry defect means the
        gate cannot currently see the thing it claims to check, which is worth fixing promptly
        even though this gate still does not block anything on it.
  * exit 2 — a command-line usage error (bad flags). Never a finding.

WHAT IT CHECKS. Each registry row supplies:

  * `claim_file` + `claim_pattern` — a regex with a named group `(?P<number>...)`, run against
    the file's current text. The line number reported is always RECOMPUTED from the match
    position, never stored in the registry — a stored line number drifts exactly the way the
    prose does. IMP-0150's own finding cited line 845 for a claim now sitting at lines 530 and
    962; this gate cannot repeat that mistake because it has nowhere to write a line number down.
    The captured `number` may be a digit string or a small English number word (see
    `_NUMBER_WORDS`); both parse to the same integer.
  * `derive` — how to recompute the truth. Three kinds:
      - `json_array_length`: the length of the array at `json_path` (dot-separated) in every
        file listed under `files`. All listed files must agree, or this is a registry defect —
        the "truth" itself would be ambiguous.
      - `xml_pair_count`: the number of `<outer_tag>...</outer_tag>` immediately followed by
        `<inner_tag>...</inner_tag>` pairs in `file`. Optionally SCOPED to one instance inside a
        shared multi-instance file with `scope_tag` + `scope_attr` + `scope_value` (all three or
        none) — added 2026-08-24 for `IMP-0269`, because a claim about ONE field-security profile
        was being checked against a count of EVERY profile in the file, and the two were the same
        number only while the solution held one profile. An unscoped row keeps the file-wide
        behaviour exactly. A scope resolving to zero or to more than one element is a REGISTRY
        DEFECT, never a count. This is deliberately NOT
        `grep -c '<FieldPermission'`: that pattern returns 52 on this solution's
        `FieldSecurityProfiles.xml` because a header COMMENT at line ~70 mentions the element
        name, and the container element `<FieldPermissions>` (plural) also starts with the
        literal substring `<FieldPermission`. Counting `EntityName`/`AttributeName` PAIRS instead
        — the same technique `verify-field-security-coverage.py` already uses — only matches
        real permission entries and gives the correct 51, verified two independent ways before
        this file encoded either number (FieldPermission elements via a real XML parse: 51;
        IsSecured=1 attributes across every Entity.xml: 51).
      - `shell`: runs `command` (a string) with the repo root as its working directory and reads
        its stdout, stripped, as a bare integer. This is the escape hatch for a future claim that
        does not fit either built-in kind — it still requires no change to this file, only a new
        registry row.

IMP-0007 SHAPE, ENFORCED. If the registry resolves to zero rows, or any row's `claim_file` or any
file its `derive` reads does not exist, that is a FAILURE (non-zero exit), never a silent pass.
A gate that reports OK because it looked at nothing is this project's most-recorded defect class
(23 instances as of the review that requested this gate).

Run:
    python3 scripts/verify-derived-counts.py                       # the real registry, repo root
    python3 scripts/verify-derived-counts.py --registry PATH.json  # a fixture registry
    python3 scripts/verify-derived-counts.py --warn-only           # print findings, exit 0
    python3 scripts/verify-derived-counts.py --selftest            # prove the gate can fail

Exits 0 clean, 1 on any drift or registry defect, 2 on a usage error.

`--warn-only` prints exactly the same findings and exits 0. It exists because this gate is SOFT
and the build runner has no per-step "record but do not halt" mode — `scripts/ci/run-config-steps.sh`
halts on the first non-zero exit, so the ONLY way to wire a SOFT check into `build.yml` is for the
command itself to exit 0. Added 2026-08-24 (`IMP-0269`), when the alternative was leaving this gate
reachable only by hand: it had correctly detected a real drift that then stood for a day, because
nothing ran it. Never pass `--warn-only` from a context that is meant to block.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

# ── English number words, small and deliberately not exhaustive ──────────────────────────────
# Only as many as a hand-typed prose count is plausible to use. A claim written as a bare digit
# never needs this table at all.
_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}


def word_to_int(token: str) -> int | None:
    """Parse a bare digit string or a small English number word (incl. 'twenty-one')."""
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    if token in _ONES:
        return _ONES[token]
    if "-" in token:
        tens, _, ones = token.partition("-")
        if tens in _TENS and ones in _ONES:
            return _TENS[tens] + _ONES[ones]
    if token in _TENS:
        return _TENS[token]
    return None


class RegistryError(Exception):
    """The registry itself is unusable: empty, a missing target, an unrecognised derivation."""


class Finding:
    def __init__(self, claim_id: str, kind: str, message: str, remedy: str = "") -> None:
        self.claim_id, self.kind, self.message, self.remedy = claim_id, kind, message, remedy

    def __str__(self) -> str:
        out = f"[{self.kind}] {self.claim_id}: {self.message}"
        if self.remedy:
            out += f"\n    → {self.remedy}"
        return out


def _get_path(doc: dict, dotted: str):
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _derive_json_array_length(params: dict, repo_root: Path) -> int:
    files = params.get("files") or []
    json_path = params.get("json_path")
    if not files or not json_path:
        raise RegistryError("json_array_length derive needs both 'files' and 'json_path'")
    lengths: dict[str, int] = {}
    for rel in files:
        path = repo_root / rel
        if not path.is_file():
            raise RegistryError(f"derivation source {rel} does not exist")
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RegistryError(f"{rel} is not valid JSON: {exc}") from exc
        array = _get_path(doc, json_path)
        if not isinstance(array, list):
            raise RegistryError(f"{rel}: '{json_path}' is not an array")
        lengths[rel] = len(array)
    distinct = set(lengths.values())
    if len(distinct) != 1:
        detail = ", ".join(f"{rel}={n}" for rel, n in sorted(lengths.items()))
        raise RegistryError(
            f"the sources this claim is derived from disagree with EACH OTHER ({detail}) — "
            "there is no single truth to compare the claim against until they agree")
    return distinct.pop()


def _pair_pattern(outer: str, inner: str) -> re.Pattern:
    """One definition of what a PAIR is, shared by the scoped and unscoped paths.

    Written once on purpose: the scoped path below counts pairs inside one element's subtree and
    the unscoped path counts them across the file, and two copies of this expression would drift
    into two different answers to the same question (IMP-0093).
    """
    return re.compile(
        rf"<{re.escape(outer)}>[^<]+</{re.escape(outer)}>\s*"
        rf"<{re.escape(inner)}>[^<]+</{re.escape(inner)}>")


def _derive_xml_pair_count(params: dict, repo_root: Path) -> int:
    rel = params.get("file")
    outer, inner = params.get("outer_tag"), params.get("inner_tag")
    if not rel or not outer or not inner:
        raise RegistryError("xml_pair_count derive needs 'file', 'outer_tag' and 'inner_tag'")
    path = repo_root / rel
    if not path.is_file():
        raise RegistryError(f"derivation source {rel} does not exist")
    text = path.read_text(encoding="utf-8")
    pattern = _pair_pattern(outer, inner)

    # ── SCOPE: which INSTANCE in a shared multi-instance file the claim is about (IMP-0269) ──
    # Optional, and its absence keeps the original file-wide behaviour so no existing row moves.
    #
    # WHY IT EXISTS. FieldSecurityProfiles.xml held one profile when this deriver was written, so
    # "every pair in the file" and "every pair in REV_TrusteeRestricted" were the same 51 and the
    # row was correct BY COINCIDENCE. REV_FinanceOnly landed on 2026-08-23 with 16 more, the
    # derive started returning 67, and the gate reported the trustee role file's correct "51
    # secured columns" as drifted. Obeying it would have written 67 into the header documenting a
    # privacy control that covers 51 columns — overstating the control by the 16 Finance-only
    # columns it does not reach. C-TECH-069 in one sentence: a check may not assume a whole
    # shared file is relevant to whatever it is checking.
    scope_tag = params.get("scope_tag")
    scope_attr = params.get("scope_attr")
    scope_value = params.get("scope_value")
    if not any((scope_tag, scope_attr, scope_value)):
        return len(pattern.findall(text))
    if not all((scope_tag, scope_attr, scope_value)):
        raise RegistryError(
            "a scoped xml_pair_count needs all three of 'scope_tag', 'scope_attr' and "
            "'scope_value' — a partial scope silently degrades to a file-wide count, which is "
            "the defect this option exists to fix (IMP-0269)")

    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise RegistryError(f"{rel} is not well-formed XML, so it cannot be scoped: {exc}") from exc

    matches = [el for el in root.iter(scope_tag) if el.get(scope_attr) == scope_value]
    if not matches:
        present = sorted({str(el.get(scope_attr)) for el in root.iter(scope_tag)
                          if el.get(scope_attr) is not None})
        raise RegistryError(
            f"{rel} has no <{scope_tag}> with {scope_attr}='{scope_value}'. Present: "
            f"{present or 'none'}. A scope that resolves to nothing is a registry defect, never "
            "a count of zero (IMP-0007)")
    if len(matches) > 1:
        raise RegistryError(
            f"{rel} has {len(matches)} <{scope_tag}> elements with {scope_attr}='{scope_value}'. "
            "Identity must resolve to exactly one instance, or the count belongs to no single "
            "claim (C-TECH-069)")

    # Count inside the resolved subtree using the SAME pair definition as the file-wide path.
    # ElementTree drops comments, so the `<!-- ... <FieldPermission ... -->` trap that made
    # `grep -c` wrong here cannot reappear through this route either.
    return len(pattern.findall(
        ElementTree.tostring(matches[0], encoding="unicode")))


def _derive_shell(params: dict, repo_root: Path) -> int:
    command = params.get("command")
    if not command:
        raise RegistryError("shell derive needs 'command'")
    try:
        result = subprocess.run(
            command, shell=True, cwd=repo_root, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RegistryError(f"derivation command failed to run: {exc}") from exc
    if result.returncode != 0:
        raise RegistryError(
            f"derivation command exited {result.returncode}: {result.stderr.strip()[:200]}")
    stdout = result.stdout.strip()
    if not stdout.isdigit():
        raise RegistryError(f"derivation command's stdout is not a bare integer: {stdout!r}")
    return int(stdout)


_DERIVERS = {
    "json_array_length": _derive_json_array_length,
    "xml_pair_count": _derive_xml_pair_count,
    "shell": _derive_shell,
}


def derive_truth(derive: dict, repo_root: Path) -> int:
    kind = derive.get("kind")
    fn = _DERIVERS.get(kind)
    if fn is None:
        raise RegistryError(f"unknown derive.kind '{kind}' — one of {sorted(_DERIVERS)}")
    return fn(derive, repo_root)


def check_claim(claim: dict, repo_root: Path) -> list[Finding]:
    claim_id = claim.get("id", "<unnamed claim>")
    findings: list[Finding] = []

    # ── A DATED RECORD IS NOT A DRIFTING CLAIM (IMP-0263) ─────────────────────────────────
    # The secured-column count has moved 39 -> 51 -> 67, and each move reported the same four
    # claims as drifted. Two of them are dated records — a build handover and an improvement
    # review — and "correcting" those asserts something their authors never observed. But
    # leaving them reported forever is worse: a SOFT gate that reports and is never acted on
    # trains readers to skip it, which is exactly how this class keeps recurring.
    #
    # So a row may declare itself historical. It is then NOT compared against current source.
    # Both keys are mandatory, because an unexplained exemption is how a live claim gets filed
    # as history: `historical` is the date the number was true, `historical_reason` says why the
    # document must not be edited. Anything missing is a REGISTRY DEFECT, not a skip.
    if "historical" in claim:
        missing = [k for k in ("historical", "historical_reason") if not claim.get(k)]
        if missing:
            return [Finding(
                claim_id, "REGISTRY DEFECT",
                f"declares itself historical but is missing {', '.join(missing)}",
                "a historical exemption needs the date the figure was true and the reason the "
                "document must not be corrected — otherwise it is an untracked live claim")]
        if "claim_file" not in claim:
            return [Finding(claim_id, "REGISTRY DEFECT", "row is missing 'claim_file'")]
        if not (repo_root / claim["claim_file"]).is_file():
            return [Finding(
                claim_id, "REGISTRY DEFECT",
                f"claim_file '{claim['claim_file']}' does not exist",
                "a registry row pointing at a missing file is not a pass, historical or not")]
        return []

    for key in ("claim_file", "claim_pattern", "derive"):
        if key not in claim:
            findings.append(Finding(claim_id, "REGISTRY DEFECT", f"row is missing '{key}'"))
    if findings:
        return findings

    rel = claim["claim_file"]
    path = repo_root / rel
    if not path.is_file():
        return [Finding(
            claim_id, "REGISTRY DEFECT",
            f"claim_file '{rel}' does not exist",
            "a registry row pointing at a missing file is not a pass — fix the path or "
            "remove the row (IMP-0007)")]

    try:
        pattern = re.compile(claim["claim_pattern"])
    except re.error as exc:
        return [Finding(claim_id, "REGISTRY DEFECT", f"claim_pattern does not compile: {exc}")]
    if "number" not in pattern.groupindex:
        return [Finding(
            claim_id, "REGISTRY DEFECT",
            "claim_pattern has no '(?P<number>...)' capture group")]

    text = path.read_text(encoding="utf-8")
    matches = list(pattern.finditer(text))
    if not matches:
        return [Finding(
            claim_id, "REGISTRY DEFECT",
            f"claim_pattern matched 0 times in {rel} — the wording has likely changed since "
            "this row was written",
            "recompute the pattern against the current text; do not assume the old wording "
            "still holds")]

    try:
        truth = derive_truth(claim["derive"], repo_root)
    except RegistryError as exc:
        return [Finding(claim_id, "REGISTRY DEFECT", str(exc))]

    for match in matches:
        line = text.count("\n", 0, match.start()) + 1
        raw = match.group("number")
        claimed = word_to_int(raw)
        if claimed is None:
            findings.append(Finding(
                claim_id, "REGISTRY DEFECT",
                f"{rel}:{line}: captured number '{raw}' does not parse as a digit string or "
                "a known English number word"))
            continue
        if claimed != truth:
            findings.append(Finding(
                claim_id, "DRIFT",
                f"{rel}:{line}: prose says {claimed} ('{match.group(0)}'), source says {truth}",
                "correct the prose to match source, or fix the source if the prose is right"))
    return findings


def load_registry(path: Path) -> list[dict]:
    if not path.is_file():
        raise RegistryError(f"registry file {path} does not exist")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegistryError(f"{path} is not valid JSON: {exc}") from exc
    claims = doc.get("claims")
    if claims is None:
        raise RegistryError(f"{path} has no 'claims' key")
    if not isinstance(claims, list):
        raise RegistryError(f"{path}: 'claims' is not a list")
    return claims


def run(registry_path: Path, repo_root: Path) -> tuple[int, list[Finding], int]:
    """Returns (exit_code, findings, claim_instances_checked)."""
    try:
        claims = load_registry(registry_path)
    except RegistryError as exc:
        return 1, [Finding("<registry>", "REGISTRY DEFECT", str(exc))], 0

    if not claims:
        return 1, [Finding(
            "<registry>", "REGISTRY DEFECT",
            f"{registry_path} resolves zero rows — a registry with nothing in it is not a "
            "pass, it is a gate with no inputs (IMP-0007)")], 0

    all_findings: list[Finding] = []
    checked = 0
    for claim in claims:
        all_findings += check_claim(claim, repo_root)
        checked += 1

    return (1 if all_findings else 0), all_findings, checked


# ── Self-test: prove the gate can fail, and prove it does not fire on everything ──────────────
# Fixtures are assembled at runtime, never committed (IMP-0024's lesson, applied here).

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_SELFTEST_RAN: list[int] = []


def selftest() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # A tiny fixture "source of truth": 3 items.
        _write(root / "source.json", json.dumps({"items": ["a", "b", "c"]}))

        # Case 1: empty registry -> must FAIL.
        empty_registry = root / "empty-registry.json"
        _write(empty_registry, json.dumps({"claims": []}))
        code, findings, _ = run(empty_registry, root)
        ok = code != 0
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} empty-registry → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("empty-registry")

        # Case 2: a row pointing at a nonexistent claim_file -> must FAIL.
        missing_file_registry = root / "missing-file-registry.json"
        _write(missing_file_registry, json.dumps({"claims": [{
            "id": "missing-file-claim",
            "claim_file": "does/not/exist.md",
            "claim_pattern": r"(?P<number>[0-9]+) items",
            "derive": {"kind": "json_array_length", "files": ["source.json"], "json_path": "items"},
        }]}))
        code, findings, _ = run(missing_file_registry, root)
        ok = code != 0
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} missing-claim-file → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("missing-claim-file")

        # Case 3: a row whose derivation source is missing -> must FAIL.
        missing_derive_registry = root / "missing-derive-registry.json"
        _write(root / "prose-3.md", "there are 3 items in the fixture")
        _write(missing_derive_registry, json.dumps({"claims": [{
            "id": "missing-derive-source",
            "claim_file": "prose-3.md",
            "claim_pattern": r"(?P<number>[0-9]+) items",
            "derive": {"kind": "json_array_length", "files": ["does-not-exist.json"],
                       "json_path": "items"},
        }]}))
        code, findings, _ = run(missing_derive_registry, root)
        ok = code != 0
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} missing-derive-source → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("missing-derive-source")

        # Case 4: a claim whose number is CORRECT -> must NOT be reported.
        correct_registry = root / "correct-registry.json"
        _write(correct_registry, json.dumps({"claims": [{
            "id": "correct-claim",
            "claim_file": "prose-3.md",
            "claim_pattern": r"(?P<number>[0-9]+) items",
            "derive": {"kind": "json_array_length", "files": ["source.json"], "json_path": "items"},
        }]}))
        code, findings, _ = run(correct_registry, root)
        ok = code == 0 and not findings
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} correct-claim-not-reported → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("correct-claim-not-reported")

        # Case 4b: the historical exemption (IMP-0263). A dated record with a reason is NOT
        # compared against source; the same row without a reason is a REGISTRY DEFECT, so the
        # exemption cannot be used to quietly retire a live claim.
        _write(root / "prose-hist.md", "there are 51 items in the dated record")
        for label, extra, want_findings in (
            ("historical-with-reason-not-compared",
             {"historical": "2026-08-21", "historical_reason": "a dated handover"}, 0),
            ("historical-without-reason-is-a-defect", {"historical": "2026-08-21"}, 1),
        ):
            reg = root / f"{label}.json"
            _write(reg, json.dumps({"claims": [dict({
                "id": label,
                "claim_file": "prose-hist.md",
                "claim_pattern": r"(?P<number>[0-9]+) items",
                "derive": {"kind": "json_array_length", "files": ["source.json"],
                           "json_path": "items"},
            }, **extra)]}))
            code, findings, _ = run(reg, root)
            ok = len(findings) == want_findings and (code == 0) == (want_findings == 0)
            _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {label} → exit {code}, "
                  f"{len(findings)} finding(s)")
            if not ok:
                failures.append(label)

        # Case 5: a claim whose number is WRONG -> must be reported as DRIFT, with both numbers.
        _write(root / "prose-5.md", "there are 5 items in the fixture")
        drift_registry = root / "drift-registry.json"
        _write(drift_registry, json.dumps({"claims": [{
            "id": "drifted-claim",
            "claim_file": "prose-5.md",
            "claim_pattern": r"(?P<number>[0-9]+) items",
            "derive": {"kind": "json_array_length", "files": ["source.json"], "json_path": "items"},
        }]}))
        code, findings, _ = run(drift_registry, root)
        ok = (code != 0 and len(findings) == 1 and findings[0].kind == "DRIFT"
              and "5" in findings[0].message and "3" in findings[0].message)
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} drifted-claim-reported → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("drifted-claim-reported")
            for f in findings:
                print(f"                   {f}")

        # Case 6: xml_pair_count must not be fooled by a comment or a plural container tag —
        # the exact shape of the real FieldSecurityProfiles.xml trap.
        _write(root / "profile.xml", """<Root>
  <!-- mentions <Pair> in a comment, and <Pairs> the container, neither is a real pair -->
  <Pairs>
    <Pair><EntityName>a</EntityName><AttributeName>x</AttributeName></Pair>
    <Pair><EntityName>b</EntityName><AttributeName>y</AttributeName></Pair>
  </Pairs>
</Root>""")
        _write(root / "prose-2.md", "the profile secures 2 columns")
        xml_registry = root / "xml-registry.json"
        _write(xml_registry, json.dumps({"claims": [{
            "id": "xml-pair-claim",
            "claim_file": "prose-2.md",
            "claim_pattern": r"(?P<number>[0-9]+) columns",
            "derive": {"kind": "xml_pair_count", "file": "profile.xml",
                       "outer_tag": "EntityName", "inner_tag": "AttributeName"},
        }]}))
        code, findings, _ = run(xml_registry, root)
        ok = code == 0 and not findings
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} xml-pair-count-not-fooled → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("xml-pair-count-not-fooled")
            for f in findings:
                print(f"                   {f}")

        # Case 6b: THE SCOPE SELECTOR (IMP-0269) — the exact two-profile shape that produced the
        # false drift. The file holds 2 pairs under profile A and 3 under profile B. A claim
        # about A says 2; unscoped it would be compared against 5 and reported as drifted, which
        # is what happened live and would have overstated a privacy control if actioned.
        _write(root / "profiles.xml", """<Profiles>
  <!-- a comment naming <Pair> and the container <Pairs>, neither is a real pair -->
  <Profile name="A">
    <Pairs>
      <Pair><EntityName>t1</EntityName><AttributeName>c1</AttributeName></Pair>
      <Pair><EntityName>t1</EntityName><AttributeName>c2</AttributeName></Pair>
    </Pairs>
  </Profile>
  <Profile name="B">
    <Pairs>
      <Pair><EntityName>t2</EntityName><AttributeName>c3</AttributeName></Pair>
      <Pair><EntityName>t2</EntityName><AttributeName>c4</AttributeName></Pair>
      <Pair><EntityName>t2</EntityName><AttributeName>c5</AttributeName></Pair>
    </Pairs>
  </Profile>
</Profiles>""")
        _write(root / "prose-scoped.md", "profile A secures 2 columns")
        _scope = {"kind": "xml_pair_count", "file": "profiles.xml",
                  "outer_tag": "EntityName", "inner_tag": "AttributeName"}
        for label, extra, want_findings, want_kind in (
            ("scoped-count-matches-the-profile-it-names",
             {"scope_tag": "Profile", "scope_attr": "name", "scope_value": "A"}, 0, None),
            ("unscoped-count-sums-the-file-and-drifts", {}, 1, "DRIFT"),
            ("a-scope-matching-nothing-is-a-registry-defect",
             {"scope_tag": "Profile", "scope_attr": "name", "scope_value": "Z"},
             1, "REGISTRY DEFECT"),
            ("a-partial-scope-is-a-registry-defect",
             {"scope_tag": "Profile", "scope_attr": "name"}, 1, "REGISTRY DEFECT"),
        ):
            reg = root / f"{label}.json"
            _write(reg, json.dumps({"claims": [{
                "id": label,
                "claim_file": "prose-scoped.md",
                "claim_pattern": r"(?P<number>[0-9]+) columns",
                "derive": dict(_scope, **extra),
            }]}))
            code, findings, _ = run(reg, root)
            ok = (len(findings) == want_findings
                  and (want_kind is None or findings[0].kind == want_kind))
            _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} {label} → "
                  f"exit {code}, {len(findings)} finding(s)")
            if not ok:
                failures.append(label)
                for f in findings:
                    print(f"                   {f}")

        # Case 6c: two elements answering to the same identity is ambiguous, not a sum.
        _write(root / "dupes.xml", """<Profiles>
  <Profile name="A"><Pairs>
    <Pair><EntityName>t1</EntityName><AttributeName>c1</AttributeName></Pair>
  </Pairs></Profile>
  <Profile name="A"><Pairs>
    <Pair><EntityName>t2</EntityName><AttributeName>c2</AttributeName></Pair>
  </Pairs></Profile>
</Profiles>""")
        dupe_registry = root / "ambiguous-scope.json"
        _write(dupe_registry, json.dumps({"claims": [{
            "id": "ambiguous-scope-is-a-registry-defect",
            "claim_file": "prose-scoped.md",
            "claim_pattern": r"(?P<number>[0-9]+) columns",
            "derive": {"kind": "xml_pair_count", "file": "dupes.xml",
                       "outer_tag": "EntityName", "inner_tag": "AttributeName",
                       "scope_tag": "Profile", "scope_attr": "name", "scope_value": "A"},
        }]}))
        code, findings, _ = run(dupe_registry, root)
        ok = len(findings) == 1 and findings[0].kind == "REGISTRY DEFECT"
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} "
              f"ambiguous-scope-is-a-registry-defect → exit {code}, {len(findings)} finding(s)")
        if not ok:
            failures.append("ambiguous-scope-is-a-registry-defect")

        # Case 7: number word parsing — "three" must equal 3.
        _write(root / "prose-word.md", "there are three items in the fixture")
        word_registry = root / "word-registry.json"
        _write(word_registry, json.dumps({"claims": [{
            "id": "word-claim",
            "claim_file": "prose-word.md",
            "claim_pattern": r"(?P<number>three|[0-9]+) items",
            "derive": {"kind": "json_array_length", "files": ["source.json"], "json_path": "items"},
        }]}))
        code, findings, _ = run(word_registry, root)
        ok = code == 0 and not findings
        _SELFTEST_RAN.append(1); print(f"  {'OK' if ok else 'DID NOT BEHAVE':16} number-word-parses → exit {code}, "
              f"{len(findings)} finding(s)")
        if not ok:
            failures.append("number-word-parses")

    # The total is COUNTED, not typed — this gate's whole subject is prose that states a number
    # source has since moved past, and its own footer had drifted to understate its fixtures by
    # two the moment IMP-0263's historical cases were added. A gate exempt from its own rule is
    # the shape verify-constraint-verifiers.py now reads this line to check.
    total = len(_SELFTEST_RAN)
    if failures:
        print(f"\nverify-derived-counts: SELFTEST FAILED — {', '.join(failures)} "
              f"({len(failures)} of {total} fixtures)", file=sys.stderr)
        return 1
    print(f"\nverify-derived-counts: SELFTEST OK — {total} fixtures, covering a registry that is "
          f"empty, points at a missing file, names a missing derive source, is correct, is a "
          f"dated historical record with and without its reason, has drifted, the exact "
          f"FieldSecurityProfiles.xml trap shape, and the scope selector: scoped to the right "
          f"instance, unscoped and summing the file, scoped to nothing, partially scoped, and "
          f"scoped to an ambiguous identity.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=Path("scripts/derived-counts-registry.json"),
                        help="registry JSON file (default: scripts/derived-counts-registry.json)")
    parser.add_argument("--repo-root", type=Path, default=Path("."),
                        help="repo root the registry's paths are relative to (default: .)")
    parser.add_argument("--warn-only", action="store_true",
                        help="print findings and exit 0 — for wiring this SOFT gate into a "
                             "build config whose runner halts on any non-zero exit")
    parser.add_argument("--selftest", action="store_true",
                        help="assemble known-bad and known-good fixtures at runtime and prove "
                             "this gate behaves on each")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    repo_root = args.repo_root.resolve()
    code, findings, checked = run(args.registry, repo_root)

    if findings:
        drift = [f for f in findings if f.kind == "DRIFT"]
        defects = [f for f in findings if f.kind == "REGISTRY DEFECT"]
        label = "WARNING" if args.warn_only else "ERROR"
        for f in findings:
            print(f"{label}: {f}", file=sys.stderr)
        print(
            f"\nverify-derived-counts: FAILED (SOFT — report as WARN, do not block) — "
            f"{len(drift)} drifted claim(s), {len(defects)} registry defect(s), across "
            f"{checked} row(s) in {args.registry}."
            + (" Exiting 0: --warn-only." if args.warn_only else ""),
            file=sys.stderr,
        )
        return 0 if args.warn_only else code

    print(f"verify-derived-counts: OK — {checked} registered claim(s) in {args.registry} all "
          f"match what their derivation recomputes right now.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
