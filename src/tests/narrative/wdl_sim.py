#!/usr/bin/env python3
"""A small executor for the subset of Power Automate's workflow definition language (WDL) that
`REV | Narrative | Scrub Free-Text` uses (wbs:5.3). Test-only.

WHY IT EXISTS. The flow is a hand-authored platform artefact implementing a custom security control
over Article 9 free text, and this session cannot run it (DEV is read-only, no flow run is possible).
A structural assertion ("the write sits in the If's else branch") proves where things are, not what
they do (knowledge/technology/power-automate.md, "Guards and fallbacks are tested with the input that
triggers them"). So the SHIPPED JSON is executed here, action by action, over the 20-sample corpus,
and its writes and decision are compared with the Python flow model in redaction_reference.py.

WHAT IT IS NOT. It is not the platform. Where the platform's semantics are uncertain, the STRICTER
reading is implemented, so an expression that survives here survives the platform either way:
  * if() evaluates ALL its arguments (eager) - power-automate.md records both answers as open;
  * substring(), indexing, length(), trim() and arithmetic THROW on out-of-range or null input;
  * range() with a count below 1 throws (the flow always guards it);
  * string comparison in contains/startsWith/endsWith/equals/indexOf can be run case-SENSITIVE or
    case-INSENSITIVE (`Engine(case_insensitive=...)`); the tests run the corpus both ways;
  * a container (Scope, loop iteration) fails when a child failed and nothing ran after it on
    Failed - the platform's "last action decides" rule for handled errors.
Anything outside the subset raises Unsupported, so a new function cannot pass silently.

It also RECORDS every action's evaluated inputs and outputs and every variable assignment, so the
tests can assert the run-history closure (C-DOM-004): no text where secureData does not hide it.
"""
from __future__ import annotations

import copy
import json
import math
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


class Unsupported(Exception):
    pass


class WdlError(Exception):
    """An expression or action failure the platform would report as a failed action."""


class Terminated(Exception):
    def __init__(self, status):
        super().__init__(status)
        self.status = status


# ── Tokeniser and parser ───────────────────────────────────────────────────────────────────────
def tokenize(text: str):
    toks, i = [], 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == "'":
            j, buf = i + 1, []
            while True:
                if j >= len(text):
                    raise WdlError("unterminated string")
                if text[j] == "'":
                    if j + 1 < len(text) and text[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(text[j])
                j += 1
            toks.append(("str", "".join(buf)))
            i = j + 1
            continue
        if c.isdigit() or (c == "-" and i + 1 < len(text) and text[i + 1].isdigit()):
            j = i + 1
            while j < len(text) and (text[j].isdigit() or text[j] == "."):
                j += 1
            s = text[i:j]
            toks.append(("num", float(s) if "." in s else int(s)))
            i = j
            continue
        if c.isalpha() or c == "_" or c == "$":
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] in "_$"):
                j += 1
            toks.append(("id", text[i:j]))
            i = j
            continue
        if c in "(),[]?.":
            toks.append((c, c))
            i += 1
            continue
        raise WdlError(f"unexpected character {c!r} in expression")
    return toks


class Parser:
    def __init__(self, text):
        self.toks, self.p = tokenize(text), 0

    def peek(self, k=0):
        return self.toks[self.p + k] if self.p + k < len(self.toks) else (None, None)

    def take(self, kind):
        t = self.peek()
        if t[0] != kind:
            raise WdlError(f"expected {kind}, got {t}")
        self.p += 1
        return t

    def parse(self):
        node = self.expr()
        if self.p != len(self.toks):
            raise WdlError(f"trailing tokens {self.toks[self.p:]}")
        return node

    def expr(self):
        t = self.peek()
        if t[0] == "str":
            self.p += 1
            node = ("lit", t[1])
        elif t[0] == "num":
            self.p += 1
            node = ("lit", t[1])
        elif t[0] == "id":
            self.p += 1
            if t[1] in ("true", "false", "null") and self.peek()[0] != "(":
                node = ("lit", {"true": True, "false": False, "null": None}[t[1]])
            else:
                self.take("(")
                args = []
                if self.peek()[0] != ")":
                    args.append(self.expr())
                    while self.peek()[0] == ",":
                        self.p += 1
                        args.append(self.expr())
                self.take(")")
                node = ("call", t[1], args)
        else:
            raise WdlError(f"unexpected token {t}")
        while True:
            t = self.peek()
            if t[0] == "?" and self.peek(1)[0] == "[":
                self.p += 2
                key = self.expr()
                self.take("]")
                node = ("idx", node, key, True)
            elif t[0] == "[":
                self.p += 1
                key = self.expr()
                self.take("]")
                node = ("idx", node, key, False)
            elif t[0] == "?" and self.peek(1)[0] == ".":
                self.p += 2
                node = ("idx", node, ("lit", self.take("id")[1]), True)
            elif t[0] == ".":
                self.p += 1
                node = ("idx", node, ("lit", self.take("id")[1]), False)
            else:
                return node


_PARSE_CACHE: dict = {}


def parse(text):
    if text not in _PARSE_CACHE:
        _PARSE_CACHE[text] = Parser(text).parse()
    return _PARSE_CACHE[text]


# ── Values ─────────────────────────────────────────────────────────────────────────────────────
def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def to_str(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float) and v.is_integer():
        return str(v)
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return str(v)


@dataclass
class ActionRecord:
    name: str
    type: str
    status: str
    inputs: object = None
    outputs: object = None
    error: dict | None = None
    secure: tuple = ()


@dataclass
class Engine:
    definition: dict
    trigger_body: dict
    parameters: dict = field(default_factory=dict)
    connector: object = None          # callable(name, operationId, params) -> body | raise
    child_flow: object = None         # callable(name, body) -> None
    case_insensitive: bool = True

    def __post_init__(self):
        self.results: dict[str, dict] = {}
        self.variables: dict = {}
        self.item_stack: list = []          # [(loop name, item)]
        self.select_item: list = []
        self.records: list[ActionRecord] = []
        self.assignments: list = []         # (variable, value)
        self.children: dict[str, list] = {}  # container name -> [{name, status, error}], for result()

    # ── expression evaluation ──────────────────────────────────────────────────────────────────
    def value(self, v):
        """Evaluate a definition value: expression strings, interpolations, objects, arrays."""
        if isinstance(v, str):
            if v.startswith("@@"):
                return v[1:]
            if v.startswith("@{") or "@{" in v:
                return self.interpolate(v)
            if v.startswith("@"):
                return self.eval(parse(v[1:]))
            return v
        if isinstance(v, dict):
            return {k: self.value(x) for k, x in v.items()}
        if isinstance(v, list):
            return [self.value(x) for x in v]
        return v

    def interpolate(self, s):
        out, i = [], 0
        while i < len(s):
            j = s.find("@{", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            depth, k, in_str = 0, j + 1, False
            while k < len(s):
                ch = s[k]
                if ch == "'":
                    in_str = not in_str
                elif not in_str and ch == "{":
                    depth += 1
                elif not in_str and ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            out.append(to_str(self.eval(parse(s[j + 2:k]))))
            i = k + 1
        return "".join(out)

    def eval(self, node):
        kind = node[0]
        if kind == "lit":
            return node[1]
        if kind == "idx":
            base = self.eval(node[1])
            key = self.eval(node[2])
            return self.index(base, key, node[3])
        if kind == "call":
            name, args = node[1], node[2]
            fn = getattr(self, "f_" + name, None)
            if fn is None:
                raise Unsupported(f"function {name}()")
            return fn(*[self.eval(a) for a in args])
        raise Unsupported(kind)

    def index(self, base, key, safe):
        if base is None:
            if safe:
                return None
            raise WdlError(f"cannot index null with {key!r}")
        if isinstance(base, dict):
            if isinstance(key, str) and "/" in key and key not in base:
                cur = base
                for part in key.split("/"):
                    cur = self.index(cur, part, safe)
                return cur
            if key in base:
                return base[key]
            if safe:
                return None
            raise WdlError(f"property {key!r} not found")
        if isinstance(base, list):
            if not is_num(key) or isinstance(key, float):
                raise WdlError(f"array index {key!r}")
            if key < 0 or key >= len(base):
                raise WdlError(f"array index {key} outside bounds")
            return base[key]
        raise WdlError(f"cannot index {type(base).__name__}")

    # string comparison helpers
    def _fold(self, s):
        return s.lower() if self.case_insensitive else s

    @staticmethod
    def _need_str(*xs):
        for x in xs:
            if not isinstance(x, str):
                raise WdlError(f"expected a string, got {x!r}")

    @staticmethod
    def _need_num(*xs):
        for x in xs:
            if not is_num(x):
                raise WdlError(f"expected a number, got {x!r}")

    @staticmethod
    def _need_bool(*xs):
        for x in xs:
            if not isinstance(x, bool):
                raise WdlError(f"expected a boolean, got {x!r}")

    def _eq(self, a, b):
        if is_num(a) and is_num(b):
            return a == b
        if isinstance(a, str) and isinstance(b, str):
            return self._fold(a) == self._fold(b)
        if type(a) is not type(b):
            return False
        if isinstance(a, list):
            return len(a) == len(b) and all(self._eq(x, y) for x, y in zip(a, b))
        if isinstance(a, dict):
            return a.keys() == b.keys() and all(self._eq(a[k], b[k]) for k in a)
        return a == b

    # ── functions ──────────────────────────────────────────────────────────────────────────────
    def f_concat(self, *xs):
        for x in xs:
            if isinstance(x, (list, dict)):
                raise Unsupported("concat() of a collection")
        return "".join(to_str(x) for x in xs)

    def f_substring(self, s, start, length=None):
        self._need_str(s)
        self._need_num(start)
        if start < 0 or start > len(s):
            raise WdlError(f"substring start {start} outside 0..{len(s)}")
        if length is None:
            return s[start:]
        self._need_num(length)
        if length < 0 or start + length > len(s):
            raise WdlError(f"substring({start}, {length}) outside length {len(s)}")
        return s[start:start + length]

    def f_length(self, x):
        if isinstance(x, (str, list)):
            return len(x)
        raise WdlError(f"length() of {x!r}")

    def f_range(self, start, count):
        self._need_num(start, count)
        if count < 1:
            raise WdlError(f"range() count {count} (the simulator is strict: below 1 throws)")
        return list(range(start, start + count))

    def f_contains(self, coll, val):
        if isinstance(coll, str):
            self._need_str(val)
            return self._fold(val) in self._fold(coll)
        if isinstance(coll, list):
            return any(self._eq(x, val) for x in coll)
        if isinstance(coll, dict):
            return val in coll
        raise WdlError(f"contains() on {coll!r}")

    def f_startsWith(self, s, p):
        self._need_str(s, p)
        return self._fold(s).startswith(self._fold(p))

    def f_endsWith(self, s, p):
        self._need_str(s, p)
        return self._fold(s).endswith(self._fold(p))

    def f_indexOf(self, s, p):
        self._need_str(s, p)
        return self._fold(s).find(self._fold(p))

    def f_lastIndexOf(self, s, p):
        self._need_str(s, p)
        if s == "":
            return -1
        return self._fold(s).rfind(self._fold(p))

    def f_equals(self, a, b):
        return self._eq(a, b)

    def f_if(self, c, a, b):  # eager: a and b are already evaluated
        self._need_bool(c)
        return a if c else b

    def f_and(self, *xs):
        self._need_bool(*xs)
        return all(xs)

    def f_or(self, *xs):
        self._need_bool(*xs)
        return any(xs)

    def f_not(self, x):
        self._need_bool(x)
        return not x

    def f_add(self, a, b):
        self._need_num(a, b)
        return a + b

    def f_sub(self, a, b):
        self._need_num(a, b)
        return a - b

    def f_mul(self, a, b):
        self._need_num(a, b)
        return a * b

    def f_div(self, a, b):
        self._need_num(a, b)
        if b == 0:
            raise WdlError("division by zero")
        if isinstance(a, int) and isinstance(b, int):
            return int(a / b)
        return a / b

    def f_mod(self, a, b):
        self._need_num(a, b)
        if b == 0:
            raise WdlError("mod by zero")
        return int(math.fmod(a, b)) if isinstance(a, int) and isinstance(b, int) else math.fmod(a, b)

    def _minmax(self, fn, xs):
        if len(xs) == 1 and isinstance(xs[0], list):
            xs = xs[0]
        if not xs:
            raise WdlError("min()/max() of nothing")
        self._need_num(*xs)
        return fn(xs)

    def f_min(self, *xs):
        return self._minmax(min, xs)

    def f_max(self, *xs):
        return self._minmax(max, xs)

    def _cmp(self, a, b):
        if is_num(a) and is_num(b):
            return (a > b) - (a < b)
        if isinstance(a, str) and isinstance(b, str):
            return (a > b) - (a < b)
        raise WdlError(f"cannot compare {a!r} and {b!r}")

    def f_less(self, a, b):
        return self._cmp(a, b) < 0

    def f_lessOrEquals(self, a, b):
        return self._cmp(a, b) <= 0

    def f_greater(self, a, b):
        return self._cmp(a, b) > 0

    def f_greaterOrEquals(self, a, b):
        return self._cmp(a, b) >= 0

    def f_coalesce(self, *xs):
        for x in xs:
            if x is not None:
                return x
        return None

    def f_empty(self, x):
        return x is None or (isinstance(x, (str, list, dict)) and len(x) == 0)

    def f_trim(self, s):
        self._need_str(s)
        return s.strip()

    def f_toLower(self, s):
        self._need_str(s)
        return s.lower()

    def f_toUpper(self, s):
        self._need_str(s)
        return s.upper()

    def f_ticks(self, s):
        """100-ns intervals since 0001-01-01 UTC. Throws on null or a non-ISO string, as the platform
        documents for its date functions (power-automate.md, 'A DATE FUNCTION OVER A POSSIBLY-NULL')."""
        self._need_str(s)
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            raise WdlError(f"ticks() of {s!r}") from None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (dt - datetime(1, 1, 1, tzinfo=timezone.utc)) // timedelta(microseconds=1) * 10

    def f_replace(self, s, old, new):
        self._need_str(s, old, new)
        if old == "":
            raise WdlError("replace() of an empty string")
        return s.replace(old, new)

    def f_split(self, s, sep):
        self._need_str(s, sep)
        return s.split(sep)

    def f_join(self, a, sep):
        if not isinstance(a, list):
            raise WdlError("join() of a non-array")
        return sep.join(to_str(x) for x in a)

    def f_first(self, c):
        if isinstance(c, (str, list)):
            return c[0] if c else None
        raise WdlError(f"first() of {c!r}")

    def f_last(self, c):
        if isinstance(c, (str, list)):
            return c[-1] if c else None
        raise WdlError(f"last() of {c!r}")

    def f_skip(self, c, n):
        if not isinstance(c, list):
            raise WdlError("skip() of a non-array")
        self._need_num(n)
        if n < 0:
            raise WdlError("skip() count below 0")
        return c[n:]

    def f_take(self, c, n):
        if not isinstance(c, (str, list)):
            raise WdlError("take() of a non-collection")
        self._need_num(n)
        if n < 0:
            raise WdlError("take() count below 0")
        return c[:n]

    def _dedup(self, items):
        out = []
        for x in items:
            if not any(self._eq(x, y) for y in out):
                out.append(x)
        return out

    def f_union(self, *arrays):
        for a in arrays:
            if not isinstance(a, list):
                raise WdlError("union() of a non-array")
        return self._dedup([x for a in arrays for x in a])

    def f_intersection(self, a, b):
        if not isinstance(a, list) or not isinstance(b, list):
            raise WdlError("intersection() of a non-array")
        return self._dedup([x for x in a if any(self._eq(x, y) for y in b)])

    def f_createArray(self, *xs):
        if not xs:
            raise WdlError("createArray() with no argument")
        return list(xs)

    def f_json(self, s):
        self._need_str(s)
        return json.loads(s)

    def f_int(self, x):
        if isinstance(x, bool):
            raise WdlError("int() of a boolean")
        if isinstance(x, int):
            return x
        if isinstance(x, str) and x.strip().lstrip("-").isdigit():
            return int(x)
        raise WdlError(f"int() of {x!r}")

    def f_float(self, x):
        if isinstance(x, bool):
            raise WdlError("float() of a boolean")
        if is_num(x):
            return float(x)
        if isinstance(x, str):
            try:
                return float(x)
            except ValueError:
                raise WdlError(f"float() of {x!r}") from None
        raise WdlError(f"float() of {x!r}")

    def f_string(self, x):
        return to_str(x)

    def f_sort(self, arr, key=None):
        if not isinstance(arr, list):
            raise WdlError("sort() of a non-array")
        if key is None:
            return sorted(arr)
        for x in arr:
            if not isinstance(x, dict) or key not in x:
                raise WdlError(f"sort() key {key!r} missing")
        return sorted(arr, key=lambda x: x[key])

    def f_decodeUriComponent(self, s):
        return urllib.parse.unquote(s)

    def f_item(self):
        if self.select_item:
            return self.select_item[-1]
        if not self.item_stack:
            raise WdlError("item() outside a loop")
        return self.item_stack[-1][1]

    def f_items(self, name):
        for loop, it in reversed(self.item_stack):
            if loop == name:
                return it
        raise WdlError(f"items({name!r}) outside that loop")

    def f_variables(self, name):
        if name not in self.variables:
            raise WdlError(f"variable {name} not initialised")
        return copy.deepcopy(self.variables[name])

    def _result(self, name):
        if name not in self.results:
            raise WdlError(f"action {name} has not run")
        return self.results[name]

    def f_outputs(self, name):
        return copy.deepcopy(self._result(name).get("outputs"))

    def f_body(self, name):
        return copy.deepcopy(self._result(name).get("body"))

    def f_triggerOutputs(self):
        return {"body": copy.deepcopy(self.trigger_body)}

    def f_parameters(self, name):
        if name not in self.parameters:
            raise WdlError(f"parameter {name}")
        return self.parameters[name]

    def f_workflow(self):
        return {"name": "flow", "tags": {"environmentName": "env"}, "run": {"name": "run-1"}}

    def f_result(self, name):
        """Immediate children only. For a loop, every iteration's children (the reading under which
        a failed iteration stays visible after later iterations succeed)."""
        if name not in self.children:
            raise WdlError(f"result({name!r}) of an action that has not run")
        return copy.deepcopy(self.children[name])

    # ── conditions in object form ──────────────────────────────────────────────────────────────
    def condition(self, expr):
        if isinstance(expr, str):
            v = self.value(expr)
            self._need_bool(v)
            return v
        if isinstance(expr, dict) and len(expr) == 1:
            op, args = next(iter(expr.items()))
            if op == "and":
                return all([self.condition(a) for a in args])
            if op == "or":
                return any([self.condition(a) for a in args])
            if op == "not":
                return not self.condition(args)
            vals = [self.value(a) for a in args]
            fn = getattr(self, "f_" + op, None)
            if fn is None:
                raise Unsupported(f"condition operator {op}")
            return fn(*vals)
        raise Unsupported(f"condition {expr!r}")

    # ── actions ────────────────────────────────────────────────────────────────────────────────
    def run(self):
        status = "Succeeded"
        try:
            status = self.run_container("$root", self.definition["actions"])
        except Terminated as t:
            status = t.status
        return status

    def run_container(self, cname, actions: dict, fresh=True) -> str:
        if fresh:
            self.children[cname] = []
        done: dict[str, str] = {}
        pending = list(actions)
        while pending:
            progressed = False
            for name in list(pending):
                ra = actions[name].get("runAfter") or {}
                if any(dep not in done for dep in ra):
                    continue
                pending.remove(name)
                progressed = True
                if all(done[dep] in sts for dep, sts in ra.items()):
                    done[name] = self.run_action(name, actions[name])
                else:
                    done[name] = "Skipped"
                    self.results[name] = {"status": "Skipped"}
            if not progressed:
                raise WdlError(f"runAfter cycle or missing dependency in {cname}: {pending}")
        for n, st in done.items():
            self.children[cname].append({"name": n, "status": st, "error": self.results.get(n, {}).get("error")})
        handled = {dep for a in actions.values() for dep, sts in (a.get("runAfter") or {}).items()
                   if "Failed" in sts or "TimedOut" in sts}
        failed = [n for n, s in done.items() if s in ("Failed", "TimedOut") and n not in handled]
        return "Failed" if failed else "Succeeded"

    def run_action(self, name, a) -> str:
        t = a["type"]
        secure = tuple((a.get("runtimeConfiguration") or {}).get("secureData", {}).get("properties", []))
        rec = ActionRecord(name, t, "Running", secure=secure)
        self.records.append(rec)
        try:
            status = getattr(self, "a_" + t)(name, a, rec)
        except Terminated:
            rec.status = "Succeeded"
            raise
        except (WdlError, KeyError, TypeError, ValueError, ConnectorFailure) as e:
            rec.status = "Failed"
            rec.error = {"code": type(e).__name__, "message": str(e)}
            self.results[name] = {"status": "Failed", "error": rec.error}
            return "Failed"
        rec.status = status
        self.results.setdefault(name, {})["status"] = status
        return status

    def _store(self, name, outputs, body=None, rec=None):
        self.results[name] = {"status": "Succeeded", "outputs": outputs, "body": body}
        if rec is not None:
            rec.outputs = outputs if body is None else body

    def a_InitializeVariable(self, name, a, rec):
        for v in a["inputs"]["variables"]:
            self.variables[v["name"]] = self.value(v.get("value"))
            self.assignments.append((v["name"], self.variables[v["name"]]))
        self._store(name, None)
        return "Succeeded"

    def a_SetVariable(self, name, a, rec):
        var = a["inputs"]["name"]
        if var not in self.variables:
            raise WdlError(f"variable {var} not initialised")
        val = self.value(a["inputs"]["value"])
        rec.inputs = val
        self.variables[var] = val
        self.assignments.append((var, val))
        self._store(name, None)
        return "Succeeded"

    def a_AppendToArrayVariable(self, name, a, rec):
        var = a["inputs"]["name"]
        val = self.value(a["inputs"]["value"])
        rec.inputs = val
        if not isinstance(self.variables.get(var), list):
            raise WdlError(f"{var} is not an array")
        self.variables[var].append(val)
        self.assignments.append((var, val))
        self._store(name, None)
        return "Succeeded"

    def a_Compose(self, name, a, rec):
        out = self.value(a["inputs"])
        rec.inputs = out
        self._store(name, out, out, rec)
        return "Succeeded"

    def a_Select(self, name, a, rec):
        src = self.value(a["inputs"]["from"])
        if not isinstance(src, list):
            raise WdlError("Select from a non-array")
        rec.inputs = src
        out = []
        for it in src:
            self.select_item.append(it)
            try:
                out.append(self.value(a["inputs"]["select"]))
            finally:
                self.select_item.pop()
        self._store(name, {"body": out}, out, rec)
        return "Succeeded"

    def a_Query(self, name, a, rec):
        src = self.value(a["inputs"]["from"])
        if not isinstance(src, list):
            raise WdlError("Filter array from a non-array")
        rec.inputs = src
        out = []
        for it in src:
            self.select_item.append(it)
            try:
                keep = self.value(a["inputs"]["where"])
            finally:
                self.select_item.pop()
            self._need_bool(keep)
            if keep:
                out.append(it)
        self._store(name, {"body": out}, out, rec)
        return "Succeeded"

    def a_If(self, name, a, rec):
        branch = a["actions"] if self.condition(a["expression"]) else (a.get("else") or {}).get("actions", {})
        status = self.run_container(name, branch)
        self.results[name] = {"status": status}
        return status

    def a_Scope(self, name, a, rec):
        status = self.run_container(name, a["actions"])
        self.results[name] = {"status": status}
        return status

    def a_Switch(self, name, a, rec):
        v = self.value(a["expression"])
        branch = (a.get("default") or {}).get("actions", {})
        for case in a.get("cases", {}).values():
            if self._eq(case["case"], v):
                branch = case["actions"]
                break
        status = self.run_container(name, branch)
        self.results[name] = {"status": status}
        return status

    def a_Foreach(self, name, a, rec):
        items = self.value(a["foreach"])
        if not isinstance(items, list):
            raise WdlError("Apply to each over a non-array")
        rec.inputs = items
        reps = ((a.get("runtimeConfiguration") or {}).get("concurrency") or {}).get("repetitions")
        if reps != 1:
            raise Unsupported(f"{name}: only sequential loops are simulated, and this flow needs them sequential")
        status = "Succeeded"
        self.children[name] = []
        for it in items:
            self.item_stack.append((name, it))
            try:
                if self.run_container(name, a["actions"], fresh=False) == "Failed":
                    status = "Failed"
            finally:
                self.item_stack.pop()
        self.results[name] = {"status": status}
        return status

    def a_Until(self, name, a, rec):
        limit = int(a.get("limit", {}).get("count", 60))
        status, n = "Succeeded", 0
        self.children[name] = []
        while True:
            n += 1
            if self.run_container(name, a["actions"], fresh=False) == "Failed":
                status = "Failed"
            if self.value(a["expression"]) is True or n >= limit:
                break
        self.results[name] = {"status": status, "iterations": n}
        return status

    def a_Terminate(self, name, a, rec):
        self.results[name] = {"status": "Succeeded"}
        raise Terminated(a["inputs"]["runStatus"])

    def a_OpenApiConnection(self, name, a, rec):
        params = self.value(a["inputs"]["parameters"])
        rec.inputs = params
        body = self.connector(name, a["inputs"]["host"]["operationId"], params)
        out = {"statusCode": 200, "body": body}
        self._store(name, out, body, rec)
        return "Succeeded"

    def a_Workflow(self, name, a, rec):
        body = self.value(a["inputs"]["body"])
        rec.inputs = body
        self.child_flow(name, body)
        self._store(name, None)
        return "Succeeded"


class ConnectorFailure(Exception):
    """Raised by a test's connector mock to make an action fail (no credits, throttled, refused)."""
