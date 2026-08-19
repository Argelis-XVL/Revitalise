#!/usr/bin/env python3
"""Readers for the two contractual source documents. Standard library only.

WHY THIS MODULE EXISTS
----------------------
`IMP-0063` recorded the agreement's total as UNVERIFIED with this reason: "its PDF uses subset
fonts with custom glyph encoding and this machine has no PDF text extractor (no poppler, no
pypdf, no Quartz)". That was true of the tools tried, and false of the format: a PDF carries a
`/ToUnicode` CMap per font precisely so a subset encoding can be reversed, and `.xlsx` is a zip
of XML. Both are readable with `zipfile`, `zlib` and `xml.etree`.

No third-party package is imported here on purpose. `.github/workflows/ci.yml` installs `pyyaml`
for two steps, so a gate that needed it would run in CI and not on this machine — and a gate that
cannot run locally is a gate nobody exercises before pushing (`gate-cannot-fail`, x6 in
`logs/known-failure-modes.md`). Machine-read baselines are therefore JSON, not YAML.

WHAT IT PROVIDES
----------------
    sha256(path)                   -> content hash, for baseline-lock pinning
    read_wbs(path)                  -> {"tasks": [...], "summary": [...], "phases": [...]}
    read_pdf_text(path)             -> decoded text of a PDF drawn with subset fonts
    find_hours_in_agreement(text)   -> {"phases": {...}, "total": int|None}

D-3 (`docs/Import/baseline-lock.yml`): HOURS ONLY. `find_hours_in_agreement` deliberately returns
hours and never the fee figures it had to read past to find them.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

XLNS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ── xlsx ──────────────────────────────────────────────────────────────────────

def _col(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref).group(1)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _sheet_rows(z: zipfile.ZipFile, path: str, shared: list[str]) -> list[dict[int, str]]:
    rows = []
    for row in ET.fromstring(z.read(path)).iter("{%s}row" % XLNS["m"]):
        cells: dict[int, str] = {}
        for c in row.findall("m:c", XLNS):
            v = c.find("m:v", XLNS)
            t = c.get("t")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif v is not None:
                val = v.text
            else:
                val = ""
            if val not in (None, ""):
                cells[_col(c.get("r"))] = str(val)
        if cells:
            rows.append(cells)
    return rows


def read_wbs(path: str | Path) -> dict:
    """Parse the WBS workbook into plain dicts. Raises on a shape it does not recognise."""
    z = zipfile.ZipFile(path)
    shared: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", XLNS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % XLNS["m"])))

    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target")
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets: dict[str, str] = {}
    for sh in wb.find("m:sheets", XLNS):
        tgt = rels[sh.get("{%s}id" % XLNS["r"])].lstrip("/")
        p = tgt if tgt.startswith("xl/") else "xl/" + tgt
        sheets[sh.get("name")] = p

    detail_name = next((n for n in sheets if n.strip().lower() == "wbs detail"), None)
    if detail_name is None:
        raise ValueError(f"{path}: no 'WBS Detail' sheet — sheets present: {sorted(sheets)}")

    rows = _sheet_rows(z, sheets[detail_name], shared)
    header = {i: (rows[0].get(i) or "").strip() for i in rows[0]}
    want = ["Task ID", "Automation #", "Automation Name", "Task", "Description",
            "Hours (Low)", "Hours (High)", "Depends On", "Phase", "Deliverable",
            "Status", "Actual Hours", "Delta"]
    idx = {}
    for w in want:
        hit = [i for i, name in header.items() if name == w]
        if not hit:
            raise ValueError(f"{path}: 'WBS Detail' is missing the '{w}' column. "
                            f"Columns found: {[header[i] for i in sorted(header)]}")
        idx[w] = hit[0]

    def num(s):
        try:
            return float(s)
        except (TypeError, ValueError):
            return None

    tasks = []
    for r in rows[1:]:
        tid = (r.get(idx["Task ID"]) or "").strip()
        if not tid:
            continue
        deps = [d.strip() for d in re.split(r"[,;]", r.get(idx["Depends On"], "") or "")
                if d.strip() and d.strip() not in {"—", "-", "–"}]
        tasks.append({
            "id": tid,
            "automation": (r.get(idx["Automation #"]) or "").strip(),
            "automation_name": (r.get(idx["Automation Name"]) or "").strip(),
            "task": (r.get(idx["Task"]) or "").strip(),
            "description": (r.get(idx["Description"]) or "").strip(),
            "hours_low": num(r.get(idx["Hours (Low)"])),
            "hours_high": num(r.get(idx["Hours (High)"])),
            "depends_on": deps,
            "phase": (r.get(idx["Phase"]) or "").strip(),
            "deliverable": (r.get(idx["Deliverable"]) or "").strip(),
            "claimed_status": (r.get(idx["Status"]) or "").strip() or None,
            "actual_hours": num(r.get(idx["Actual Hours"])),
            "delta": num(r.get(idx["Delta"])),
        })

    summary = []
    sname = next((n for n in sheets if n.strip().lower() == "summary"), None)
    if sname:
        srows = _sheet_rows(z, sheets[sname], shared)
        shdr = {i: (srows[0].get(i) or "").strip() for i in srows[0]}
        col = {name: i for i, name in shdr.items()}
        for r in srows[1:]:
            label = (r.get(col.get("#", 0)) or "").strip()
            auto = (r.get(col.get("Automation", 1)) or "").strip()
            summary.append({
                "automation": label,
                "name": auto,
                "phase": (r.get(col.get("Phase", 2)) or "").strip(),
                "hours_low": num(r.get(col.get("Hours (Low)"))),
                "hours_high": num(r.get(col.get("Hours (High)"))),
                "tasks": num(r.get(col.get("Tasks"))),
                "annual_hours_saved": num(r.get(col.get("Annual Hours Saved"))),
                "dependencies": [d.strip() for d in
                                 re.split(r"[,;]", r.get(col.get("Dependencies"), "") or "")
                                 if d.strip() and d.strip() not in {"—", "-", "–"}],
            })

    return {"tasks": tasks, "summary": summary, "sheets": sorted(sheets)}


# ── pdf ───────────────────────────────────────────────────────────────────────

def _pdf_objects(data: bytes) -> dict[int, bytes]:
    objs: dict[int, bytes] = {}
    for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj\b", data):
        start = m.end()
        end = data.find(b"endobj", start)
        objs[int(m.group(1))] = data[start:end if end > 0 else start + 4096]
    for num, body in list(objs.items()):
        if b"/ObjStm" not in body:
            continue
        sm = re.search(rb"stream\r?\n", body)
        if not sm:
            continue
        try:
            dec = zlib.decompress(body[sm.end():body.find(b"endstream", sm.end())])
            n = int(re.search(rb"/N\s+(\d+)", body).group(1))
            first = int(re.search(rb"/First\s+(\d+)", body).group(1))
        except Exception:
            continue
        hdr = dec[:first].split()
        for i in range(n):
            onum, off = int(hdr[2 * i]), int(hdr[2 * i + 1])
            nxt = int(hdr[2 * i + 3]) + first if i + 1 < n else len(dec)
            objs[onum] = dec[first + off:nxt]
    return objs


def _stream(body: bytes) -> bytes | None:
    sm = re.search(rb"stream\r?\n", body)
    if not sm:
        return None
    raw = body[sm.end():body.find(b"endstream", sm.end())]
    try:
        return zlib.decompress(raw)
    except Exception:
        return raw


def read_pdf_text(path: str | Path) -> str:
    """Decode a PDF's text via each font's /ToUnicode CMap.

    Handles the subset-font encoding that made this document look unreadable (IMP-0063).
    Layout is not preserved: this is for asserting that a figure is present, not for reflowing
    prose.
    """
    data = Path(path).read_bytes()
    objs = _pdf_objects(data)

    cmaps: dict[int, dict[int, str]] = {}
    for num, body in objs.items():
        s = _stream(body) if b"stream" in body[:400] else None
        if not s or (b"beginbfchar" not in s and b"beginbfrange" not in s):
            continue
        m: dict[int, str] = {}
        for blk in re.findall(rb"beginbfchar(.*?)endbfchar", s, re.S):
            for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                try:
                    m[int(a, 16)] = "".join(chr(int(b[i:i + 4], 16)) for i in range(0, len(b), 4))
                except ValueError:
                    pass
        for blk in re.findall(rb"beginbfrange(.*?)endbfrange", s, re.S):
            for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                lo, hi, dst = int(a, 16), int(b, 16), int(c, 16)
                for i in range(hi - lo + 1):
                    m[lo + i] = chr(dst + i)
        if m:
            cmaps[num] = m

    name2cmap: dict[str, dict[int, str]] = {}
    for body in objs.values():
        for fname, fref in re.findall(rb"/([A-Za-z0-9]+)\s+(\d+)\s+0\s+R", body):
            fb = objs.get(int(fref), b"")
            tu = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", fb)
            if tu and int(tu.group(1)) in cmaps:
                name2cmap.setdefault(fname.decode(), cmaps[int(tu.group(1))])

    def decode(raw: bytes, cm: dict[int, str], two: bool) -> str:
        raw = re.sub(rb"\\(\d{1,3})", lambda m: bytes([int(m.group(1), 8) & 0xFF]), raw)
        raw = re.sub(rb"\\([()\\])", rb"\1", raw)
        if two:
            return "".join(cm.get((raw[i] << 8) | raw[i + 1], "") for i in range(0, len(raw) - 1, 2))
        return "".join(cm.get(b, chr(b) if 32 <= b < 127 else "") for b in raw)

    out: list[str] = []
    tok_re = (rb"/([A-Za-z0-9]+)\s+[\d.]+\s+Tf"
              rb"|\((?:\\.|[^\\()])*\)"
              rb"|<([0-9A-Fa-f\s]+)>\s*Tj"
              rb"|\[((?:[^\]\\]|\\.)*)\]\s*TJ"
              rb"|\bT[dD*]\b|\bET\b")
    for body in objs.values():
        if b"/Contents" not in body or b"/Page" not in body:
            continue
        for cref in re.findall(rb"/Contents\s+(\d+)\s+0\s+R", body):
            s = _stream(objs.get(int(cref), b""))
            if not s:
                continue
            cm: dict[int, str] = {}
            two = False
            for tok in re.finditer(tok_re, s):
                t = tok.group(0)
                if t.endswith(b"Tf"):
                    cm = name2cmap.get(tok.group(1).decode(), {})
                    two = any(k > 255 for k in cm) if cm else False
                    continue
                if t in (b"Td", b"TD", b"T*", b"ET"):
                    out.append("\n")
                    continue
                if tok.group(3) is not None:
                    for lit in re.finditer(rb"\((?:\\.|[^\\()])*\)|<([0-9A-Fa-f\s]+)>", tok.group(3)):
                        g = lit.group(0)
                        if g.startswith(b"<"):
                            out.append(decode(bytes.fromhex(re.sub(rb"\s", b"", g[1:-1]).decode()), cm, True))
                        else:
                            out.append(decode(g[1:-1], cm, two))
                    continue
                if tok.group(2) is not None:
                    out.append(decode(bytes.fromhex(re.sub(rb"\s", b"", tok.group(2)).decode()), cm, True))
                    continue
                if t.startswith(b"("):
                    out.append(decode(t[1:-1], cm, two))
    text = "".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{2,}", "\n", text)


def find_hours_in_agreement(text: str) -> dict:
    """Extract the per-phase HOUR figures and the total from the agreement's fee schedule.

    D-3: hours only. The schedule reads "Phase 0 ... 58 hrs @ <rate> <amount>"; this returns the
    58 and drops the rest. The total is cross-checked two ways — the sum of the phase rows, and
    the stated total divided by the stated rate — but neither the rate nor the amount is returned
    or written anywhere.
    """
    flat = re.sub(r"\s+", " ", text)
    phases: dict[str, int] = {}
    for m in re.finditer(r"Phase\s*(\d)\b[^0-9]{0,120}?(\d{1,3})\s*hrs", flat):
        phases.setdefault("phase_" + m.group(1), int(m.group(2)))
    summed = sum(phases.values()) if phases else None

    derived = None
    mt = re.search(r"Total\s*\(excl\.?\s*VAT\)\s*[^0-9]{0,12}([\d,]{4,})", flat)
    mr = re.search(r"([\d,]{2,6})\s*(?:per hour|/\s*hr|/hour)", flat)
    if mt and mr:
        try:
            total_amount = int(mt.group(1).replace(",", ""))
            rate = int(mr.group(1).replace(",", ""))
            if rate:
                derived = total_amount // rate
        except ValueError:
            pass

    return {"phases": phases, "total_from_phase_rows": summed,
            "total_from_amount_over_rate": derived,
            "agree": (summed is not None and derived is not None and summed == derived)}


MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], 1)}


def find_milestones_in_agreement(text: str) -> dict:
    """Extract the milestone dates from the agreement's timeline table.

    Returns {"phase_0": "2026-08-28", ..., "completion": "2026-12-11", "kick_off": "2026-07-04"}.
    Dates are contractual: a wrong one moves a warranty window, so they are read, never typed.
    """
    flat = re.sub(r"\s+", " ", text)
    out: dict[str, str] = {}

    def iso(day: str, month: str, year: str) -> str | None:
        mm = MONTHS.get(month.capitalize())
        return f"{year}-{mm:02d}-{int(day):02d}" if mm else None

    m = re.search(r"Kick\s*-?\s*off.{0,80}?(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", flat)
    if m:
        out["kick_off"] = iso(*m.groups())
    for m in re.finditer(r"Phase\s*(\d)\s*delivered(.{0,260}?)(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", flat):
        d = iso(m.group(3), m.group(4), m.group(5))
        if d:
            out.setdefault("phase_" + m.group(1), d)
    m = re.search(r"Completion(.{0,200}?)(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", flat)
    if m:
        out["completion"] = iso(m.group(2), m.group(3), m.group(4))
    return out
