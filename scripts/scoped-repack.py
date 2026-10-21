#!/usr/bin/env python3
"""Build a component-scoped DEV import pack from a build artifact's unmanaged solution zip.

WHY THIS EXISTS (IMP-1137, improvement review 2026-10-17 row 1). Partial DEV pushes -- a pack
holding only some of a build's solution components -- were assembled by hand six times in nine
days (logs/pipeline.log, 2026-10-09 to 2026-10-17). On 2026-10-17 the hand-built pack for
workflow 1011 plus two AI prompts was rejected by pac before import ("Unexpected end of file while
parsing Comment"): the repack regex matched the text <connectionreferences> inside one of the
438 XML comments in that build's customizations.xml and cut the file in the middle of the comment.

WHAT IT DOES. Reads the artifact's UNMANAGED solution zip (a managed one is refused), keeps the
RootComponents named with --component, keeps their customizations.xml elements and their files,
and removes every other component element. Removal is done on BYTE SPANS found by a lexical scan
that skips comments, CDATA sections and processing instructions, so:

  * a comment or CDATA section that quotes an element name can never be matched as that element;
  * every kept element's bytes are identical to the source (checked after writing, not assumed).

FAIL-CLOSED. It writes nothing, and exits 1, when:

  * a --component value matches no root component (or connection reference) in the artifact;
  * the solution is managed;
  * the zip holds a file whose path it does not recognise, or a customizations.xml section with
    children it does not know how to identify (the allow-lists below were set from the real
    artifacts revitalise-grant-automation-20261017-1 (24 files) and -20261021-3 (28 files, the
    first with a classic-workflow .xaml) at apply time, 2026-10-21);
  * either rewritten XML file does not parse;
  * a kept element's bytes, or a kept file's bytes, differ from the source.

PROVENANCE. Next to the output it writes <out>.provenance.json: the source zip path and sha256,
the output sha256, the requested ids, the kept root components, and a sha256 per output file. The
pipeline-agent names that sidecar in its WRITE BEGUN line, so a scoped pack can be traced to the
build-agent artifact it came from (C-TECH-030). A pack built by this tool is SCOPED: it deploys to
the first environment only, and it never satisfies "the newest artifact deployed, and unscoped".

LEVEL. A green --selftest and a corpus run prove the pack parses and holds the artifact's exact
bytes (V1). Whether pac imports it is V3 and is seen only at a real partial push.

This is a TOOL, not a gate: its input exists only at deploy time, so no build step runs it.

Usage:
  python3 scripts/scoped-repack.py --artifact build/artifacts/<build-id> \\
      --component 8f1c2a44-1011-4b7a-9e21-0a1b2c3d4e11 --component e853d7c8-dd36-4917-951f-50108a812fc4 \\
      --out build/exports/scoped-<build-id>.zip
  python3 scripts/scoped-repack.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# ── Lexical scan ─────────────────────────────────────────────────────────────────────────────


class ScanError(ValueError):
    pass


class Node:
    __slots__ = ("name", "start", "end", "children", "tag_text")

    def __init__(self, name: str, start: int, tag_text: str):
        self.name = name
        self.start = start          # index of '<' of the start tag
        self.end = -1               # index just past '>' of the end tag (or of the empty tag)
        self.children: list[Node] = []
        self.tag_text = tag_text    # the start tag itself, for attribute reads


_NAME = re.compile(r"[^\s/>]+")
_ATTR = re.compile(r"""([^\s=/>]+)\s*=\s*("([^"]*)"|'([^']*)')""")


def _find(text: str, needle: str, at: int, what: str) -> int:
    j = text.find(needle, at)
    if j < 0:
        raise ScanError(f"unterminated {what} starting at offset {at}")
    return j + len(needle)


def scan(text: str) -> Node:
    """Return the document element as a span tree. Comments, CDATA, PIs and DOCTYPE are skipped."""
    root: Node | None = None
    stack: list[Node] = []
    i, n = 0, len(text)
    while True:
        i = text.find("<", i)
        if i < 0:
            break
        if text.startswith("<!--", i):
            i = _find(text, "-->", i + 4, "comment")
        elif text.startswith("<![CDATA[", i):
            i = _find(text, "]]>", i + 9, "CDATA section")
        elif text.startswith("<?", i):
            i = _find(text, "?>", i + 2, "processing instruction")
        elif text.startswith("<!", i):
            j = _find(text, ">", i + 2, "declaration")
            if "[" in text[i:j]:
                raise ScanError("a DOCTYPE with an internal subset is not supported")
            i = j
        elif text.startswith("</", i):
            j = _find(text, ">", i + 2, "end tag")
            name = text[i + 2:j - 1].strip()
            if not stack or stack[-1].name != name:
                raise ScanError(f"end tag </{name}> at offset {i} does not close "
                                f"<{stack[-1].name if stack else '?'}>")
            node = stack.pop()
            node.end = j
            i = j
        else:
            # Start or empty-element tag. '>' may legally appear inside a quoted attribute value.
            j, quote = i + 1, None
            while j < n:
                c = text[j]
                if quote:
                    if c == quote:
                        quote = None
                elif c in "\"'":
                    quote = c
                elif c == ">":
                    break
                j += 1
            if j >= n:
                raise ScanError(f"unterminated start tag at offset {i}")
            tag_text = text[i:j + 1]
            m = _NAME.match(text, i + 1)
            if not m:
                raise ScanError(f"tag with no name at offset {i}")
            node = Node(m.group(0), i, tag_text)
            if stack:
                stack[-1].children.append(node)
            elif root is None:
                root = node
            else:
                raise ScanError("more than one document element")
            if tag_text.endswith("/>"):
                node.end = j + 1
            else:
                stack.append(node)
            i = j + 1
    if stack:
        raise ScanError(f"<{stack[-1].name}> is never closed")
    if root is None:
        raise ScanError("no document element")
    return root


def attrs(node: Node) -> dict[str, str]:
    return {m.group(1): (m.group(3) if m.group(3) is not None else m.group(4))
            for m in _ATTR.finditer(node.tag_text)}


def child(node: Node, name: str) -> Node | None:
    for c in node.children:
        if c.name == name:
            return c
    return None


def inner_text(text: str, node: Node) -> str:
    """Text content of a leaf element (no child elements expected)."""
    if node.tag_text.endswith("/>"):
        return ""
    body = text[node.start + len(node.tag_text):node.end]
    body = body[:body.rfind("</")]
    return body.strip()


def remove_spans(text: str, spans: list[tuple[int, int]]) -> str:
    """Delete each span; where an element sits alone on its line, take the line with it."""
    out, last = [], 0
    for s, e in sorted(spans):
        ls = s
        while ls > 0 and text[ls - 1] in " \t":
            ls -= 1
        le = e
        while le < len(text) and text[le] in " \t":
            le += 1
        alone = (ls == 0 or text[ls - 1] == "\n") and (le < len(text) and text[le] in "\r\n")
        if alone:
            s = ls
            e = le + (2 if text.startswith("\r\n", le) else 1)
        if s < last:
            raise ScanError("overlapping removal spans")
        out.append(text[last:s])
        last = e
    out.append(text[last:])
    return "".join(out)


# ── What the tool knows. Set from the real artifact's contents; anything else is refused. ──────

def norm(value: str) -> str:
    return value.strip().strip("{}").lower()


# customizations.xml section -> (child element, how to read its identity)
#   ("attr", name)   identity is an attribute of the child
#   ("text", name)   identity is the text of one of the child's child elements
SECTIONS: dict[str, tuple[str, tuple[str, str]]] = {
    "Entities":              ("Entity",                ("text", "Name")),
    "Roles":                 ("Role",                  ("attr", "id")),
    "Workflows":             ("Workflow",              ("attr", "WorkflowId")),
    "FieldSecurityProfiles": ("FieldSecurityProfile",  ("attr", "fieldsecurityprofileid")),
    "EntityRelationships":   ("EntityRelationship",    ("attr", "Name")),
    "optionsets":            ("optionset",             ("attr", "Name")),
    "AppModuleSiteMaps":     ("AppModuleSiteMap",      ("text", "SiteMapUniqueName")),
    "AppModules":            ("AppModule",             ("text", "UniqueName")),
    "AIModels":              ("AIModel",               ("text", "msdyn_aimodelid")),
    # Not a root component in this solution: kept only when named explicitly with --component.
    "connectionreferences":  ("connectionreference",   ("attr", "connectionreferencelogicalname")),
}
# Structural sections, kept whole (not components).
KEEP_WHOLE = {"Languages"}
# Sections seen empty in the real artifact. Children appearing in one is refused (fail-closed).
KNOWN_EMPTY = {"Templates", "EntityMaps", "OrganizationSettings", "CustomControls",
               "SolutionPluginAssemblies", "EntityDataProviders", "EnvironmentVariables"}

ALWAYS_FILES = {"solution.xml", "customizations.xml", "[Content_Types].xml"}
WORKFLOW_FILE = re.compile(r"^Workflows/[^/]+-([0-9A-Fa-f-]{36})\.(?:json|xaml)$")   # cloud flow / classic
ENVVAR_FILE = re.compile(r"^environmentvariabledefinitions/([^/]+)/environmentvariabledefinition\.xml$")
DOC_FILES = {"environmentvariabledefinitions/README.md"}   # documentation, kept unchanged


class RepackError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode(data: bytes) -> tuple[str, bool]:
    bom = data.startswith(b"\xef\xbb\xbf")
    return data[3:].decode("utf-8") if bom else data.decode("utf-8"), bom


def encode(text: str, bom: bool) -> bytes:
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def find_path(root: Node, *names: str) -> Node:
    node = root
    for name in names:
        nxt = child(node, name)
        if nxt is None:
            raise RepackError(f"solution.xml has no <{name}> under <{node.name}>")
        node = nxt
    return node


def identity(text: str, elem: Node, how: tuple[str, str]) -> str:
    kind, name = how
    if kind == "attr":
        return norm(attrs(elem).get(name, ""))
    sub = child(elem, name)
    return norm(inner_text(text, sub)) if sub is not None else ""


def repack(source_zip: Path, components: list[str]) -> tuple[bytes, dict]:
    """Return (output zip bytes, provenance dict). Raises RepackError on any refusal."""
    wanted = {norm(c) for c in components if c.strip()}
    if not wanted:
        raise RepackError("no --component given")
    with zipfile.ZipFile(source_zip) as zin:
        infos = zin.infolist()
        raw = {i.filename: zin.read(i) for i in infos}

    for required in ("solution.xml", "customizations.xml"):
        if required not in raw:
            raise RepackError(f"{source_zip.name} has no {required}: not a solution zip")

    # ── solution.xml: refuse managed; choose root components ───────────────────────────────
    sol_text, sol_bom = decode(raw["solution.xml"])
    sol_root = scan(sol_text)
    manifest = find_path(sol_root, "SolutionManifest")
    managed = child(manifest, "Managed")
    if managed is None or inner_text(sol_text, managed) != "0":
        raise RepackError("the solution is not unmanaged (<Managed> is not 0); a scoped pack is "
                          "built from the artifact's UNMANAGED zip only")
    rcs = find_path(sol_root, "SolutionManifest", "RootComponents")

    kept_rc: list[dict] = []
    drop_spans: list[tuple[int, int]] = []
    matched: set[str] = set()
    for rc in rcs.children:
        if rc.name != "RootComponent":
            raise RepackError(f"unexpected <{rc.name}> inside <RootComponents>")
        a = attrs(rc)
        keys = {norm(a[k]) for k in ("id", "schemaName") if a.get(k)}
        hit = keys & wanted
        if hit:
            matched |= hit
            kept_rc.append({"type": a.get("type"), "id": a.get("id"), "schemaName": a.get("schemaName")})
        else:
            drop_spans.append((rc.start, rc.end))
    new_sol = remove_spans(sol_text, drop_spans)

    kept_types_keys: dict[str, set[str]] = {}
    for k in kept_rc:
        kept_types_keys.setdefault(k["type"], set()).update(
            norm(v) for v in (k["id"], k["schemaName"]) if v)

    # ── customizations.xml ────────────────────────────────────────────────────────────────
    cus_text, cus_bom = decode(raw["customizations.xml"])
    cus_root = scan(cus_text)
    cus_drop: list[tuple[int, int]] = []
    kept_elems: dict[tuple[str, str], str] = {}      # (section, identity) -> exact source text
    workflow_json: dict[str, str] = {}               # workflow id -> zip path from JsonFileName
    for section in cus_root.children:
        if section.name in KEEP_WHOLE:
            continue
        if section.name in KNOWN_EMPTY:
            if section.children:
                raise RepackError(f"customizations.xml <{section.name}> has children; this tool "
                                  f"does not know how to scope it (fail-closed)")
            continue
        if section.name not in SECTIONS:
            raise RepackError(f"customizations.xml has an unknown section <{section.name}> "
                              f"(fail-closed; extend SECTIONS after reading a real export)")
        elem_name, how = SECTIONS[section.name]
        for elem in section.children:
            if elem.name != elem_name:
                raise RepackError(f"<{section.name}> holds <{elem.name}>, expected <{elem_name}>")
            ident = identity(cus_text, elem, how)
            if not ident:
                raise RepackError(f"a <{elem_name}> in <{section.name}> has no identity")
            if section.name == "connectionreferences":
                keep = ident in wanted
                if keep:
                    matched.add(ident)
            else:
                keep = any(ident in keys for keys in kept_types_keys.values())
            if keep:
                kept_elems[(section.name, ident)] = cus_text[elem.start:elem.end]
                if section.name == "Workflows":
                    for tag in ("JsonFileName", "XamlFileName"):
                        jf = child(elem, tag)
                        if jf is not None:
                            workflow_json[ident] = inner_text(cus_text, jf).lstrip("/")
            else:
                cus_drop.append((elem.start, elem.end))
    new_cus = remove_spans(cus_text, cus_drop)

    missing = sorted(wanted - matched)
    if missing:
        raise RepackError(f"--component value(s) match no root component or connection reference "
                          f"in {source_zip.name}: {', '.join(missing)}")

    # Every kept root component of a type that lives in customizations.xml must have its element.
    in_cus = {"1": "Entities", "20": "Roles", "29": "Workflows", "70": "FieldSecurityProfiles",
              "10": "EntityRelationships", "9": "optionsets", "62": "AppModuleSiteMaps",
              "80": "AppModules", "401": "AIModels"}
    for k in kept_rc:
        sec = in_cus.get(k["type"])
        if sec is None and k["type"] != "380":
            raise RepackError(f"root component type {k['type']} is not one this tool knows "
                              f"(fail-closed)")
        if sec and not any(s == sec and i in {norm(v) for v in (k["id"], k["schemaName"]) if v}
                           for (s, i) in kept_elems):
            raise RepackError(f"root component type {k['type']} {k['id'] or k['schemaName']} has no "
                              f"<{SECTIONS[sec][0]}> in customizations.xml")

    # ── files ─────────────────────────────────────────────────────────────────────────────
    kept_wf_ids = kept_types_keys.get("29", set())
    kept_env = kept_types_keys.get("380", set())
    out_files: list[tuple[zipfile.ZipInfo, bytes]] = []
    dropped: list[str] = []
    for info in infos:
        name = info.filename
        if name.endswith("/"):
            continue
        if name == "solution.xml":
            data = encode(new_sol, sol_bom)
        elif name == "customizations.xml":
            data = encode(new_cus, cus_bom)
        elif name in ALWAYS_FILES or name in DOC_FILES:
            data = raw[name]
        elif (m := WORKFLOW_FILE.match(name)):
            if norm(m.group(1)) not in kept_wf_ids:
                dropped.append(name)
                continue
            data = raw[name]
        elif (m := ENVVAR_FILE.match(name)):
            if norm(m.group(1)) not in kept_env:
                dropped.append(name)
                continue
            data = raw[name]
        else:
            raise RepackError(f"{source_zip.name} holds a file this tool does not know: {name} "
                              f"(fail-closed)")
        out_files.append((info, data))
    for wf, path in workflow_json.items():
        if path and not any(i.filename == path for i, _ in out_files):
            raise RepackError(f"kept workflow {wf} names {path}, which is not in the pack")

    # ── verify before returning: parses, and kept bytes are the source's bytes ──────────────
    for label, data in (("solution.xml", encode(new_sol, sol_bom)),
                        ("customizations.xml", encode(new_cus, cus_bom))):
        try:
            ET.fromstring(data)
        except ET.ParseError as exc:
            raise RepackError(f"the rewritten {label} does not parse: {exc}") from exc
    re_root = scan(new_cus)
    for section in re_root.children:
        if section.name not in SECTIONS:
            continue
        elem_name, how = SECTIONS[section.name]
        for elem in section.children:
            key = (section.name, identity(new_cus, elem, how))
            if key not in kept_elems:
                raise RepackError(f"{key} survived in the output but was not kept")
            if new_cus[elem.start:elem.end] != kept_elems[key]:
                raise RepackError(f"kept element {key} is not byte-identical to the source")
    survivors = {(s.name, identity(new_cus, e, SECTIONS[s.name][1]))
                 for s in re_root.children if s.name in SECTIONS for e in s.children}
    if survivors != set(kept_elems):
        raise RepackError("kept elements missing from the output: "
                          f"{sorted(set(kept_elems) - survivors)}")
    for info, data in out_files:
        if info.filename not in ("solution.xml", "customizations.xml") and data != raw[info.filename]:
            raise RepackError(f"kept file {info.filename} differs from the source")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zout:
        for info, data in out_files:
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zout.writestr(zi, data)
    out_bytes = buf.getvalue()
    with zipfile.ZipFile(io.BytesIO(out_bytes)) as zcheck:
        if zcheck.testzip() is not None:
            raise RepackError("the written pack fails its own CRC check")

    provenance = {
        "tool": "scripts/scoped-repack.py",
        "scoped": True,
        "deploys_to": "first environment only",
        "source_zip": str(source_zip),
        "source_zip_sha256": sha256(source_zip.read_bytes()),
        "requested_components": components,
        "kept_root_components": kept_rc,
        "kept_customizations_elements": sorted(f"{s}:{i}" for s, i in kept_elems),
        "dropped_files": dropped,
        "files": {info.filename: sha256(data) for info, data in out_files},
        "files_identical_to_source": sorted(i.filename for i, _ in out_files
                                            if i.filename not in ("solution.xml", "customizations.xml")),
    }
    return out_bytes, provenance


def pick_zip(artifact: Path, explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else artifact / p
    unmanaged = []
    for z in sorted(artifact.glob("*.zip")):
        try:
            with zipfile.ZipFile(z) as zf:
                text = zf.read("solution.xml").decode("utf-8", "replace")
        except (KeyError, zipfile.BadZipFile):
            continue
        if re.search(r"<Managed>\s*0\s*</Managed>", text):
            unmanaged.append(z)
    if len(unmanaged) != 1:
        raise RepackError(f"{artifact} holds {len(unmanaged)} unmanaged solution zips; name one "
                          f"with --zip")
    return unmanaged[0]


def run(artifact: Path, zip_name: str | None, components: list[str], out: Path) -> dict:
    if not artifact.is_dir():
        raise RepackError(f"{artifact} is not an artifact directory")
    source = pick_zip(artifact, zip_name)
    out_bytes, prov = repack(source, components)
    manifest = artifact / "manifest.json"
    if manifest.exists():
        try:
            m = json.loads(manifest.read_text(encoding="utf-8"))
            prov["source_build"] = m.get("build_id") or m.get("buildId") or artifact.name
        except (OSError, ValueError):
            prov["source_build"] = artifact.name
    else:
        prov["source_build"] = artifact.name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(out_bytes)
    prov["out"] = str(out)
    prov["out_sha256"] = sha256(out_bytes)
    side = out.with_name(out.name + ".provenance.json")
    side.write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    prov["sidecar"] = str(side)
    return prov


# ── Self-test ────────────────────────────────────────────────────────────────────────────────

_WF_A = "aaaaaaaa-0000-4000-8000-00000000000a"
_WF_B = "bbbbbbbb-0000-4000-8000-00000000000b"
_AI = "cccccccc-0000-4000-8000-00000000000c"

_SOL = f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2">
  <SolutionManifest>
    <UniqueName>Fixture</UniqueName>
    <Managed>{{managed}}</Managed>
    <RootComponents>
      <!-- a comment quoting <RootComponent type="29" id="{{{_WF_B}}}" /> must not be read as one -->
      <RootComponent type="29" id="{{{_WF_A}}}" />
      <RootComponent type="29" id="{{{_WF_B}}}" />
      <RootComponent type="380" schemaName="rev_Thing" />
      <RootComponent type="401" id="{{{_AI}}}" behavior="0" />
    </RootComponents>
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>
"""

_CUS = f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!--
    Today's case (IMP-1137): this comment names <connectionreferences> and <AIModels>, and a
    regex that cut at the first "<connectionreferences>" landed here, mid-comment.
  -->
  <Entities></Entities>
  <Workflows>
    <Workflow WorkflowId="{{{_WF_A}}}" Name="A &gt; one">
      <JsonFileName>/Workflows/A-{_WF_A.upper()}.json</JsonFileName>
      <Note><![CDATA[ a CDATA section holding </Workflow> and <!-- is text ]]></Note>
    </Workflow>
    <Workflow WorkflowId="{{{_WF_B}}}" Name="B" Title="x > y">
      <JsonFileName>/Workflows/B-{_WF_B.upper()}.json</JsonFileName>
    </Workflow>
  </Workflows>
  <Templates />
  <AIModels>
    <!-- <AIModel> quoted in a comment -->
    <AIModel>
      <msdyn_aimodelid>{{{_AI}}}</msdyn_aimodelid>
      <msdyn_name>Prompt</msdyn_name>
    </AIModel>
  </AIModels>
  <connectionreferences>
    <connectionreference connectionreferencelogicalname="rev_SharedDataverse">
      <connectorid>/providers/x</connectorid>
    </connectionreference>
  </connectionreferences>
  <Languages>
    <Language>1033</Language>
  </Languages>
</ImportExportXml>
"""


def _fixture(dir_: Path, *, managed: str = "0", extra: dict[str, str] | None = None,
             cus: str | None = None) -> Path:
    art = dir_ / f"art-{len(list(dir_.iterdir()))}"
    art.mkdir()
    files = {
        "customizations.xml": cus if cus is not None else _CUS,
        "solution.xml": _SOL.replace("{managed}", managed),
        f"Workflows/A-{_WF_A.upper()}.json": '{"a": 1}',
        f"Workflows/B-{_WF_B.upper()}.json": '{"b": 2}',
        "environmentvariabledefinitions/rev_Thing/environmentvariabledefinition.xml": "<x/>",
        "[Content_Types].xml": "<Types/>",
    }
    files.update(extra or {})
    with zipfile.ZipFile(art / "Fixture.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            z.writestr(k, v)
    (art / "manifest.json").write_text('{"build_id": "fixture-1"}', encoding="utf-8")
    return art


def selftest() -> int:
    failures: list[str] = []

    def expect(cond: bool, label: str) -> None:
        print(f"  {'ok  ' if cond else 'FAIL'} {label}")
        if not cond:
            failures.append(label)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        # 1. Today's case: keep workflow A and the AI model; comment quotes both section names.
        art = _fixture(tmp)
        out = tmp / "out" / "scoped.zip"
        prov = run(art, None, [_WF_A, "{" + _AI.upper() + "}"], out)
        with zipfile.ZipFile(out) as z:
            names = set(z.namelist())
            cus = z.read("customizations.xml").decode()
            sol = z.read("solution.xml").decode()
        ET.fromstring(cus.encode())
        ET.fromstring(sol.encode())
        expect(True, "1a output customizations.xml and solution.xml parse")
        expect(_AI in cus and "<msdyn_name>Prompt</msdyn_name>" in cus,
               "1b AI model kept although a comment before it quotes <connectionreferences>")
        expect(f'WorkflowId="{{{_WF_B}}}"' not in cus, "1c workflow B removed from customizations")
        expect(f'<RootComponent type="29" id="{{{_WF_B}}}" />\n' not in sol.split("-->", 1)[1],
               "1d workflow B removed from RootComponents (the commented mention survives)")
        expect(f"Workflows/B-{_WF_B.upper()}.json" not in names, "1e workflow B json dropped")
        expect(f"Workflows/A-{_WF_A.upper()}.json" in names, "1f workflow A json kept")
        expect("rev_SharedDataverse" not in cus, "1g unnamed connection reference removed")
        expect("<Language>1033</Language>" in cus, "1h structural Languages kept")
        expect("CDATA section holding </Workflow>" in cus, "1i CDATA content inside kept element intact")
        expect(not any(n.startswith("environmentvariabledefinitions/rev_Thing") for n in names),
               "1j unrequested environment variable file dropped")
        side = json.loads(out.with_name("scoped.zip.provenance.json").read_text())
        expect(side["source_build"] == "fixture-1" and side["scoped"] is True
               and len(side["source_zip_sha256"]) == 64 and side["out_sha256"] == prov["out_sha256"],
               "1k sidecar names the build, the source hash and the output hash")
        expect(set(side["files"]) == names, "1l sidecar hashes every output file")
        # The naive cut IMP-1137 made: everything from the first literal "<connectionreferences>".
        naive = _CUS[:_CUS.find("<connectionreferences>")] + "</ImportExportXml>\n"
        try:
            ET.fromstring(naive.encode())
            naive_ok = True
        except ET.ParseError:
            naive_ok = False
        expect(not naive_ok, "1m regression: the naive regex cut of IMP-1137 does NOT parse")

        # 2. Refusals — each must raise and write nothing.
        def refused(label: str, fn) -> None:
            try:
                fn()
            except (RepackError, ScanError):
                expect(True, label)
                return
            expect(False, label)

        refused("2a unknown component id is refused",
                lambda: run(_fixture(tmp), None, ["deadbeef-0000-4000-8000-000000000000"],
                            tmp / "r1.zip"))
        expect(not (tmp / "r1.zip").exists(), "2b nothing written on refusal")
        refused("2c managed solution is refused",
                lambda: run(_fixture(tmp, managed="1"), None, [_WF_A], tmp / "r2.zip"))
        refused("2d unknown file in the zip is refused",
                lambda: run(_fixture(tmp, extra={"WebResources/x.js": "x"}), None, [_WF_A],
                            tmp / "r3.zip"))
        refused("2e children in a known-empty section are refused",
                lambda: run(_fixture(tmp, cus=_CUS.replace("<Templates />",
                                                           "<Templates><Template/></Templates>")),
                            None, [_WF_A], tmp / "r4.zip"))
        refused("2f unknown customizations section is refused",
                lambda: run(_fixture(tmp, cus=_CUS.replace("<Templates />", "<Reports><Report/></Reports>")),
                            None, [_WF_A], tmp / "r5.zip"))
        refused("2g unterminated comment is refused by the scanner",
                lambda: scan("<a><!-- never closed </a>"))

        # 3. Named connection reference is kept when asked for.
        out3 = tmp / "c.zip"
        run(_fixture(tmp), None, [_WF_A, "rev_SharedDataverse"], out3)
        with zipfile.ZipFile(out3) as z:
            expect("rev_SharedDataverse" in z.read("customizations.xml").decode(),
                   "3a a connection reference named with --component is kept")

    print(f"scoped-repack selftest: {'FAILED' if failures else 'OK'} "
          f"({len(failures)} failure(s))")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--artifact", type=Path, help="build/artifacts/<build-id> directory")
    p.add_argument("--zip", default=None, help="the unmanaged zip inside --artifact (auto when one)")
    p.add_argument("--component", action="append", default=[],
                   help="root component id (GUID, braces optional) or schemaName; repeat")
    p.add_argument("--out", type=Path, help="output zip path")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.artifact and args.component and args.out):
        p.error("--artifact, --component and --out are required")
    try:
        prov = run(args.artifact, args.zip, args.component, args.out)
    except (RepackError, ScanError) as exc:
        print(f"scoped-repack: REFUSED — {exc}", file=sys.stderr)
        return 1
    print(f"scoped-repack: OK — {prov['out']} ({len(prov['files'])} files, "
          f"{len(prov['kept_root_components'])} root components) from {prov['source_build']}; "
          f"sidecar {prov['sidecar']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
