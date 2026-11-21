#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Audit the request bodies our code BUILDS for a `properties.class` that silently loses data.

Egeria deserialises RelationshipProperties / ClassificationProperties / EntityProperties (and the
other framework Properties beans) with `ignoreUnknown=true`. A body whose `"class"` names a class
that doesn't declare a key we send loses that key with no error: TR-89 sent `libraryType` under
`SoftwareCapabilityProperties`, and only `SourceControlLibraryProperties` reads it. A wrong,
unrelated class is already rejected loudly by Egeria (`handleInvalidPropertiesObject`), so this
audit hunts the quiet cases only.

Findings
--------
UNREAD_KEYS
    A dict literal whose `"class"` is a Properties class in PROPERTIES_CLASS_FIELDS
    (md_processing/md_processing_utils/properties_class_fields.py) carries keys that class doesn't
    read. Keys come from the literal itself, from `**` spreads that resolve to another literal in
    the same function, and from later `x["k"] = ...`, `x.update({...})`, `x |= {...}` and
    `x.setdefault("k", ...)` on a name bound to the literal.
PARENT_CLASS
    The class is an ancestor of a more specific Properties class that the call is evidently about.
    Evidence, any of: the body's own `"typeName"`; the enclosing function's name (snake_case of
    the subtype, e.g. `create_source_control_library`); a URL path segment in a string in the
    same function (`/source-control-libraries`). The hierarchy comes from Egeria's Java at the
    ref the table was generated from (read with `git cat-file`, never a checkout), or, without an
    Egeria clone, is *inferred*: same kind and a strict superset of fields.
NO_CLASS
    A built dict in a polymorphic slot (`properties`, `parentRelationshipProperties`,
    `replacementProperties`, or a value of `initialClassifications` /
    `replacementClassifications`) under a `*RequestBody`, with no `"class"`; or a request body
    with no `"class"` whose `properties` does name a table class. Both are a 400 on Egeria 6.x.

What counts as "built" (and what doesn't)
-----------------------------------------
* Built: a dict literal written in the code, plus the keys added to it in the same function, as
  above. A string class bound to a name in the same function (`cls = "XProperties"`) is resolved.
* Built by a table-filtering helper (counted, not checked): bodies made by Dr.Egeria's
  `typed_properties` family (md_processing/md_processing_utils/typed_properties.py), which keep
  only the keys the class reads and note the rest. They are already correct by construction.
* Pass-through (counted, skipped): a polymorphic slot whose value is a parameter of the enclosing
  function, i.e. the caller supplied the properties.
* Unclassified (listed, never guessed): a class given by an expression we can't resolve to a
  string (`f"{t}Properties"`, a parameter, a lookup table); a `*Properties` class that isn't in
  the table; a polymorphic slot filled by a call or other non-literal; a `**` spread or a computed
  key we can't resolve (the static keys are still checked).

Known limits: flow-insensitive within a function (every assignment to a name counts); no
inter-procedural tracking (a helper that takes the class as a parameter shows up as unclassified
at the helper, not at its callers); Python only. Tests and fakes are skipped unless --include-tests.

Usage
-----
    python scripts/audit_properties_class_bodies.py REPO [REPO ...] [--label NAME ...]
        [--egeria ~/localGit/egeria-v6/egeria] [--ref SHA] [--report PATH] [--include-tests]

Exit status 1 if any finding survives (a discovery tool first: it won't be clean on first run).
"""
from __future__ import annotations

import argparse
import ast
import difflib
import importlib.util
import os
import re
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS  # noqa: E402

UNREAD_KEYS = "UNREAD_KEYS"
PARENT_CLASS = "PARENT_CLASS"
NO_CLASS = "NO_CLASS"
KINDS = (UNREAD_KEYS, PARENT_CLASS, NO_CLASS)

POLY_SLOTS = {"properties", "parentRelationshipProperties", "replacementProperties"}
POLY_MAPS = {"initialClassifications", "replacementClassifications"}
SAFE_HELPERS = {"typed_properties", "parent_relationship_properties", "classification_map",
                "entity_properties", "new_element_properties"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__", ".tox",
             "site-packages", ".mypy_cache", ".pytest_cache"}
TEST_DIRS = {"tests", "test", "testing"}


@dataclass
class Finding:
    repo: str
    path: str
    line: int
    func: str
    kind: str
    cls: str | None
    keys: tuple[str, ...]
    detail: str
    fix: str


@dataclass
class Unclassified:
    repo: str
    path: str
    line: int
    func: str
    reason: str


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    unclassified: list[Unclassified] = field(default_factory=list)
    bodies_checked: int = 0
    pass_through: int = 0
    safe_helper: int = 0
    files: int = 0
    parse_errors: list[str] = field(default_factory=list)

    def extend(self, other: "Result") -> None:
        self.findings += other.findings
        self.unclassified += other.unclassified
        self.bodies_checked += other.bodies_checked
        self.pass_through += other.pass_through
        self.safe_helper += other.safe_helper
        self.files += other.files
        self.parse_errors += other.parse_errors


# ---------------------------------------------------------------- hierarchy

class Hierarchy:
    """Ancestor/descendant questions over the Properties classes in the table."""

    def __init__(self, parents: dict[str, str | None] | None, setters: dict[str, set[str]] | None = None):
        self.parents = parents
        self.inferred = parents is None
        self.setters = setters
        self._reads: dict[str, set[str]] = {}
        self.gaps: dict[str, set[str]] = {}  # table class -> keys Egeria reads that the table lacks (seen in use)
        if setters:  # the whole frameworks tree was read: no unscanned superclasses left to worry about
            self.incomplete = {c: p for c, p in incomplete_classes(parents).items() if p not in parents}
        else:
            self.incomplete = dict(KNOWN_INCOMPLETE) if parents is None else incomplete_classes(parents)

    def reads(self, cls: str) -> set[str]:
        """Keys `cls` reads: the table's, plus (with Egeria loaded) every public setter in its chain."""
        if cls not in self._reads:
            fields = set(PROPERTIES_CLASS_FIELDS[cls][1])
            if self.setters:
                fields |= chain_setters(cls, self.parents, self.setters)
            self._reads[cls] = fields
        return self._reads[cls]

    def is_ancestor(self, anc: str, cls: str) -> bool:
        if anc == cls or anc not in PROPERTIES_CLASS_FIELDS or cls not in PROPERTIES_CLASS_FIELDS:
            return False
        if self.inferred:
            ka, fa = PROPERTIES_CLASS_FIELDS[anc]
            kc, fc = PROPERTIES_CLASS_FIELDS[cls]
            return ka == kc and set(fa) < set(fc)
        seen, node = set(), self.parents.get(cls)
        while node and node not in seen:
            if node == anc:
                return True
            seen.add(node)
            node = self.parents.get(node)
        return False

    def descendants(self, anc: str) -> list[str]:
        return [c for c in PROPERTIES_CLASS_FIELDS if self.is_ancestor(anc, c)]


# Table classes whose superclass gen_properties_class_fields doesn't scan (it reads only *Properties.java
# and properties/ packages), so their inherited fields are missing from the table. Computed from the
# hierarchy when Egeria is loaded; this fallback is what Egeria c61bad6514 gives.
KNOWN_INCOMPLETE = {
    "FindPropertyNameProperties": "GetOptions", "FindPropertyNamesProperties": "SearchOptions",
    "FindDigitalResourceOriginProperties": "QueryOptions", "FindProjectClassificationProperties": "QueryOptions",
    "LevelIdentifierQueryProperties": "QueryOptions", "SecurityTagQueryProperties": "QueryOptions",
    "SemanticAssignmentQueryProperties": "QueryOptions",
}


def incomplete_classes(parents: dict[str, str | None]) -> dict[str, str]:
    """Table class -> the unscanned superclass its inherited fields would come from."""
    out = {}
    for cls in PROPERTIES_CLASS_FIELDS:
        node, seen = cls, set()
        while node and node not in seen:
            seen.add(node)
            p = parents.get(node)
            if p and p not in parents:
                out[cls] = p
                break
            node = p
    return out


def table_source_ref() -> str | None:
    """The Egeria sha PROPERTIES_CLASS_FIELDS was generated from (its module docstring says)."""
    spec = importlib.util.find_spec("md_processing.md_processing_utils.properties_class_fields")
    with open(spec.origin, encoding="utf-8") as f:
        m = re.search(r"from Egeria \S+ at ([0-9a-f]{7,40})", f.read(2000))
    return m.group(1) if m else None


_SETTER = re.compile(r"public\s+void\s+set(\w+)\s*\(")
_CLASS = re.compile(r"public\s+(?:abstract\s+)?class\s+(\w+)(?:\s*<[^>{]*>)?(?:\s+extends\s+(\w+))?")


def _decapitalize(name: str) -> str:
    """java.beans.Introspector.decapitalize, which Jackson uses for setter names."""
    if len(name) > 1 and name[0].isupper() and name[1].isupper():
        return name
    return name[:1].lower() + name[1:]


def load_egeria(egeria: str, ref: str) -> tuple[dict[str, str | None], dict[str, set[str]]]:
    """From Egeria's Java at `ref` (git cat-file, read-only): every frameworks class's superclass, and the
    JSON keys it declares a public setter for. Jackson binds through setters (the beans say
    `setterVisibility=PUBLIC_ONLY, fieldVisibility=NONE`), so setters are the ground truth; they also
    cover package-private fields and superclasses outside the properties packages, which
    gen_properties_class_fields' field regex misses."""
    spec = importlib.util.spec_from_file_location("_gen_pcf", os.path.join(_HERE, "gen_properties_class_fields.py"))
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    paths = [p for p in gen.git(egeria, "ls-tree", "-r", "--name-only", ref, "--", gen.FRAMEWORKS).decode().split("\n")
             if p.endswith(".java") and "/src/main/java/" in p]
    batch = gen.git(egeria, "cat-file", "--batch", stdin="".join(f"{ref}:{p}\n" for p in paths).encode())
    parents, setters, pos = {}, {}, 0
    for _ in paths:
        header_end = batch.index(b"\n", pos)
        size = int(batch[pos:header_end].split()[2])
        start = header_end + 1
        src = batch[start:start + size].decode("utf-8", errors="ignore")
        pos = start + size + 1
        m = _CLASS.search(src)
        if not m or m.group(1) in parents:
            continue
        parents[m.group(1)] = m.group(2)
        setters[m.group(1)] = {_decapitalize(x) for x in _SETTER.findall(src[m.end():])}
    return parents, setters


def chain_setters(cls: str, parents: dict, setters: dict) -> set[str]:
    out, node, seen = set(), cls, set()
    while node and node not in seen:
        seen.add(node)
        out |= setters.get(node, set())
        node = parents.get(node)
    return out


# ---------------------------------------------------------------- helpers

def _snake(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


def _plurals(word: str) -> set[str]:
    out = {word, word + "s"}
    if word.endswith("y"):
        out.add(word[:-1] + "ies")
    if word.endswith(("s", "x", "ch", "sh")):
        out.add(word + "es")
    return out


def _const_str(node) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _iter_scope(node):
    """Nodes in this scope, not descending into nested functions, lambdas or classes."""
    stack = list(ast.iter_child_nodes(node))
    while stack:
        n = stack.pop()
        yield n
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            stack.extend(ast.iter_child_nodes(n))


def _scopes(tree):
    """(qualified name, node, parameter names) for the module and every function."""
    yield "<module>", tree, set()
    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                a = child.args
                params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
                params |= {x.arg for x in (a.vararg, a.kwarg) if x}
                yield name, child, params
                yield from walk(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                yield from walk(child, f"{prefix}{child.name}.")
            else:
                yield from walk(child, prefix)
    yield from walk(tree, "")


def _call_name(call: ast.Call) -> str:
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


# ---------------------------------------------------------------- per-scope analysis

class _Scope:
    def __init__(self, repo, path, func, node, params, hierarchy, result):
        self.repo, self.path, self.func, self.node, self.params = repo, path, func, node, params
        self.h, self.r = hierarchy, result
        self.short = func.rsplit(".", 1)[-1]
        self.names: dict[str, list[tuple[int, ast.AST]]] = {}  # name -> (line, value) per assignment
        self.extra: dict[int, dict[str, int]] = {}      # id(dict) -> key -> line added later
        self.extra_unknown: dict[int, list[str]] = {}   # id(dict) -> unresolved additions
        self.slot: dict[int, tuple[str, ast.Dict | None]] = {}  # id(dict) -> (slot key, parent dict)
        self.strings: list[str] = []
        self.nodes = list(_iter_scope(node))

    # -- resolution
    def bound(self, name: ast.Name) -> list[ast.AST]:
        """What `name` holds where it's read: the nearest assignment at or before that line (so a name
        reused across if/elif branches resolves to its own branch's literal). All of them if none precedes."""
        binds = self.names.get(name.id, [])
        line = getattr(name, "lineno", None)
        before = [b for b in binds if line is None or b[0] < line
                  or (b[0] == line and not any(x is name for x in ast.walk(b[1])))]  # `x = {**x}` reads the old x
        if not before:
            return [v for _, v in binds]
        last = max(b[0] for b in before)
        return [v for ln, v in before if ln == last]

    def dicts_of(self, expr, depth=0) -> list[ast.Dict]:
        if depth > 6 or expr is None:
            return []
        if isinstance(expr, ast.Dict):
            return [expr]
        if isinstance(expr, ast.Name):
            return [d for v in self.bound(expr) for d in self.dicts_of(v, depth + 1)]
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
            return self.dicts_of(expr.left, depth + 1) + self.dicts_of(expr.right, depth + 1)
        if isinstance(expr, ast.Subscript):
            key = _const_str(expr.slice)
            if key is None:
                return []
            out = []
            for d in self.dicts_of(expr.value, depth + 1):
                for k, v in zip(d.keys, d.values):
                    if _const_str(k) == key:
                        out += self.dicts_of(v, depth + 1)
            return out
        return []

    def str_of(self, expr, depth=0) -> str | None:
        s = _const_str(expr)
        if s is not None or depth > 4:
            return s
        if isinstance(expr, ast.Name):
            vals = {self.str_of(v, depth + 1) for v in self.bound(expr)}
            return vals.pop() if len(vals) == 1 and None not in vals else None
        return None

    # -- passes
    def collect(self):
        for n in self.nodes:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.names.setdefault(t.id, []).append((n.lineno, n.value))
            elif isinstance(n, (ast.AnnAssign, ast.NamedExpr)) and isinstance(n.target, ast.Name) and n.value:
                self.names.setdefault(n.target.id, []).append((n.lineno, n.value))
            elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and isinstance(n.op, ast.BitOr):
                # x |= {...}  ==  x = x | {...}, where the left x is the binding before this line
                prev = ast.Name(id=n.target.id, ctx=ast.Load(), lineno=n.lineno - 1, col_offset=0)
                self.names.setdefault(n.target.id, []).append(
                    (n.lineno, ast.BinOp(left=prev, op=ast.BitOr(), right=n.value, lineno=n.lineno, col_offset=0)))
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                self.strings.append(n.value)
        # literal-to-literal slots
        for n in self.nodes:
            if isinstance(n, ast.Dict):
                for k, v in zip(n.keys, n.values):
                    self._link(_const_str(k), v, n)
        # later additions: x["k"] = v ; x.update(...) ; x.setdefault("k", ...) ; x |= {...}
        for n in self.nodes:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Subscript):
                        key = _const_str(t.slice)
                        if isinstance(t.value, ast.Name) and t.value.id in self.params:
                            # the caller's dict on some path; literals bound to the name elsewhere may not be it
                            if key in POLY_SLOTS and not isinstance(n.value, ast.Name):
                                self._unclassified(n.lineno, f"`{t.value.id}[{key!r}]` set on a parameter: "
                                                             "the caller's body, class not known here")
                            continue
                        for d in self.dicts_of(t.value):
                            if key is None:
                                self.extra_unknown.setdefault(id(d), []).append(
                                    f"key {ast.unparse(t.slice)} added at line {n.lineno}")
                            else:
                                self.extra.setdefault(id(d), {}).setdefault(key, n.lineno)
                                self._link(key, n.value, d)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("update", "setdefault"):
                for d in self.dicts_of(n.func.value):
                    if n.func.attr == "setdefault" and n.args:
                        key = _const_str(n.args[0])
                        if key:
                            self.extra.setdefault(id(d), {}).setdefault(key, n.lineno)
                        continue
                    for kw in n.keywords:
                        if kw.arg:
                            self.extra.setdefault(id(d), {}).setdefault(kw.arg, n.lineno)
                    for a in n.args:
                        srcs = self.dicts_of(a)
                        if not srcs:
                            self.extra_unknown.setdefault(id(d), []).append(
                                f"update({ast.unparse(a)}) at line {n.lineno}")
                        for s in srcs:
                            for k in s.keys:
                                if _const_str(k):
                                    self.extra.setdefault(id(d), {}).setdefault(_const_str(k), n.lineno)

    def _link(self, key, value, parent):
        if key in POLY_SLOTS:
            targets = self.dicts_of(value)
            for d in targets:
                self.slot.setdefault(id(d), (key, parent))
            if not targets:
                self._slot_value_unresolved(key, value, parent)
        elif key in POLY_MAPS:
            for m in self.dicts_of(value):
                for v in m.values:
                    for d in self.dicts_of(v):
                        self.slot.setdefault(id(d), (key, parent))

    def _slot_value_unresolved(self, key, value, parent):
        if not self._is_request_body(parent):
            return
        if isinstance(value, ast.Constant) and value.value is None:
            return
        if isinstance(value, ast.Name) and value.id in self.params and not self.bound(value):
            self.r.pass_through += 1
            return
        if isinstance(value, ast.Call) and _call_name(value) in SAFE_HELPERS:
            self.r.safe_helper += 1
            return
        if isinstance(value, ast.Name):
            srcs = self.bound(value)
            if srcs and all(isinstance(s, ast.Call) and _call_name(s) in SAFE_HELPERS for s in srcs):
                self.r.safe_helper += 1
                return
            if not srcs and value.id in self.params:
                self.r.pass_through += 1
                return
            what = ", ".join(ast.unparse(s)[:80] for s in srcs) or "unbound here"
            self._unclassified(value.lineno, f"`{key}` is `{value.id}` = {what}: not a literal")
            return
        self._unclassified(getattr(value, "lineno", parent.lineno),
                           f"`{key}` is `{ast.unparse(value)[:100]}`: not a literal")

    def _is_request_body(self, d: ast.Dict | None) -> bool:
        if d is None:
            return False
        cls = self.dict_class(d)[0]
        return bool(cls and cls.endswith("RequestBody"))

    def dict_class(self, d: ast.Dict, depth=0) -> tuple[str | None, ast.AST | None]:
        """The `"class"` value, looking through `**` spreads of literals (the last one wins, as in Python)."""
        found = (None, None)
        for k, v in zip(d.keys, d.values):
            if _const_str(k) == "class":
                found = (self.str_of(v), v)
            elif k is None and depth < 4:
                for s in self.dicts_of(v):
                    sub = self.dict_class(s, depth + 1)
                    if sub[1] is not None:
                        found = sub
        return found

    def dict_keys(self, d: ast.Dict, depth=0) -> tuple[dict[str, int], list[str]]:
        """Keys (with line) of the dict as finally sent, and what couldn't be resolved."""
        keys, unknown = {}, []
        for k, v in zip(d.keys, d.values):
            if k is None:  # ** spread
                srcs = [x for x in self.dicts_of(v) if x is not d] if depth < 4 else []
                if not srcs or self._spread_is_opaque(d, v):
                    unknown.append(f"spread **{ast.unparse(v)[:80]}")
                for s in srcs:
                    sk, su = self.dict_keys(s, depth + 1)
                    keys.update({x: d.lineno for x in sk if x not in keys})
                    unknown += su
            elif _const_str(k) is not None:
                keys.setdefault(_const_str(k), k.lineno)
            else:
                unknown.append(f"computed key {ast.unparse(k)[:60]}")
        for k, line in self.extra.get(id(d), {}).items():
            keys.setdefault(k, line)
        unknown += self.extra_unknown.get(id(d), [])
        return keys, unknown

    def analyse(self):
        if self.short in SAFE_HELPERS:
            for n in self.nodes:
                if isinstance(n, ast.Dict) and any(_const_str(k) == "class" for k in n.keys):
                    self.r.safe_helper += 1
            return
        for d in (n for n in self.nodes if isinstance(n, ast.Dict)):
            cls, cls_expr = self.dict_class(d)
            slot = self.slot.get(id(d))
            if cls_expr is None:
                self._check_no_class(d, slot)
                continue
            if cls is None:
                self._unclassified(d.lineno, f"class is `{ast.unparse(cls_expr)[:100]}`: not resolvable to a string")
                continue
            if cls not in PROPERTIES_CLASS_FIELDS:
                if cls.endswith("Properties"):
                    self._unclassified(d.lineno, f"class {cls} is not in PROPERTIES_CLASS_FIELDS")
                continue
            self.r.bodies_checked += 1
            keys, unknown = self.dict_keys(d)
            for u in unknown:
                self._unclassified(d.lineno, f"{cls}: {u}: keys not known (the static keys were checked)")
            self._check_unread(d, cls, keys)
            self._check_parent(d, cls, keys)

    def _check_unread(self, d, cls, keys):
        fields = self.h.reads(cls) | {"class"}
        table = set(PROPERTIES_CLASS_FIELDS[cls][1])
        missed = {k for k in keys if k in fields and k not in table and k != "class"}
        if missed:
            self.h.gaps.setdefault(cls, set()).update(missed)
        bad = tuple(sorted(k for k in keys if k not in fields))
        if not bad:
            return
        if cls in self.h.incomplete:
            self._unclassified(d.lineno, f"{cls} sends {', '.join(bad)}, but the table lacks the fields it inherits "
                                         f"from {self.h.incomplete[cls]} (not scanned by gen_properties_class_fields)")
            return
        readers = [c for c in PROPERTIES_CLASS_FIELDS if set(bad) <= self.h.reads(c)]
        subs = [c for c in readers if self.h.is_ancestor(cls, c)]
        if subs:
            fix = f"name the subclass that reads them: {', '.join(sorted(subs)[:4])}"
        elif readers:
            fix = (f"no subclass of {cls} reads them; classes that do: {', '.join(sorted(readers)[:4])}"
                   f"{' …' if len(readers) > 4 else ''} — use the right one, or drop/move the keys")
        else:
            per = {k: sorted(c for c in PROPERTIES_CLASS_FIELDS if k in self.h.reads(c)) for k in bad}
            parts = [f"{k}: {', '.join(v[:3]) + (' …' if len(v) > 3 else '') if v else 'no class'}" for k, v in per.items()]
            fix = ("no single class reads them all (" + "; ".join(parts) +
                   ") — drop them, split them into the right body, or move them to additionalProperties")
        near = {k: difflib.get_close_matches(k, sorted(fields - {"class"}), n=2, cutoff=0.6) for k in bad}
        near = {k: v for k, v in near.items() if v}
        if near:
            fix += "; closest names this class reads: " + "; ".join(f"{k} → {' / '.join(v)}" for k, v in near.items())
        lines = sorted({keys[k] for k in bad})
        self._finding(d.lineno, UNREAD_KEYS, cls, bad,
                      f"{cls} doesn't read {', '.join(bad)} (added at line {', '.join(map(str, lines))})", fix)

    def _check_parent(self, d, cls, keys):
        evidence = {}
        for k, v in zip(d.keys, d.values):
            if _const_str(k) == "typeName":
                t = self.str_of(v)
                if t and self.h.is_ancestor(cls, t + "Properties"):
                    evidence.setdefault(t + "Properties", []).append(f'typeName "{t}"')
        has_type_name = any(_const_str(k) == "typeName" and self.str_of(v) for k, v in zip(d.keys, d.values))
        # a literal typeName says what the element is; function names and URLs only hint at it
        descendants = [] if has_type_name else self.h.descendants(cls)
        fn = f"_{self.short.lower()}_"
        segs = set()
        for s in self.strings:
            if "/" in s:
                segs.update(p for p in s.split("/") if p)
        for sub in descendants:
            base = sub[: -len("Properties")]
            sn = _snake(base)
            if f"_{sn}_" in fn:
                evidence.setdefault(sub, []).append(f"function {self.short}")
            kebab = sn.replace("_", "-")
            if "-" in kebab or len(kebab) > 3:
                hit = _plurals(kebab) & segs
                if hit:
                    evidence.setdefault(sub, []).append(f"URL segment /{sorted(hit)[0]}")
        if not evidence:
            return
        # keep the most specific: drop a candidate that is an ancestor of another candidate
        best = [c for c in evidence if not any(self.h.is_ancestor(c, o) for o in evidence if o != c)]
        why = "; ".join(f"{c} ({', '.join(evidence[c])})" for c in sorted(best))
        only_sub = sorted(set().union(*(self.h.reads(c) for c in best)) - self.h.reads(cls))
        how = "inferred: strict field superset, no Egeria hierarchy loaded" if self.h.inferred else "Egeria hierarchy"
        self._finding(d.lineno, PARENT_CLASS, cls, tuple(sorted(k for k in keys if k in only_sub)),
                      f"{cls} is a parent of {why} [{how}]; subclass-only fields: "
                      f"{', '.join(only_sub[:8]) + (' …' if len(only_sub) > 8 else '') or 'none'}",
                      f"send {' or '.join(sorted(best))} (check the endpoint's element type first)")

    def _opaque_spread(self, d: ast.Dict) -> str | None:
        """A `**` spread we can't resolve to a literal: it may well carry the class."""
        for k, v in zip(d.keys, d.values):
            if k is None and self._spread_is_opaque(d, v):
                return ast.unparse(v)[:80]
        return None

    def _spread_is_opaque(self, d, v) -> bool:
        """Unresolvable, a parameter (the caller's dict, whatever else the name is bound to later),
        bound to something other than a literal too, or the dict itself (`x = {**x, ...}`)."""
        srcs = self.dicts_of(v)
        if not srcs or any(s is d for s in srcs):
            return True
        if isinstance(v, ast.Name):
            if v.id in self.params:
                return True
            return any(not isinstance(b, ast.Dict) for b in self.bound(v))
        return False

    def _check_no_class(self, d, slot):
        spread = self._opaque_spread(d)
        if spread and (slot or any(_const_str(k) == "properties" for k in d.keys)):
            if slot and (self._is_request_body(slot[1]) or slot[0] in POLY_MAPS):
                self._unclassified(d.lineno, f"`{slot[0]}` has no literal class; it may come from **{spread}")
            return
        if slot:
            key, parent = slot
            if self._is_request_body(parent) or key in POLY_MAPS:
                keys, _ = self.dict_keys(d)
                self._finding(d.lineno, NO_CLASS, None, tuple(sorted(keys)),
                              f"`{key}` under {self.dict_class(parent)[0] or 'a request body'} has no class",
                              "add the Properties class of the element/relationship/classification type")
            return
        # a request body with no class whose `properties` names a table class
        for k, v in zip(d.keys, d.values):
            if _const_str(k) == "properties":
                for p in self.dicts_of(v):
                    pc = self.dict_class(p)[0]
                    if pc in PROPERTIES_CLASS_FIELDS:
                        self._finding(d.lineno, NO_CLASS, pc, (),
                                      f"request body (properties {pc}) has no class",
                                      "add the request body class, e.g. NewElementRequestBody / "
                                      "UpdateElementRequestBody / NewRelationshipRequestBody")
                        return

    def _finding(self, line, kind, cls, keys, detail, fix):
        self.r.findings.append(Finding(self.repo, self.path, line, self.func, kind, cls, keys, detail, fix))

    def _unclassified(self, line, reason):
        self.r.unclassified.append(Unclassified(self.repo, self.path, line, self.func, reason))


# ---------------------------------------------------------------- driver

def audit_source(source: str, path: str, repo: str, hierarchy: Hierarchy) -> Result:
    r = Result(files=1)
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        r.parse_errors.append(f"{path}: {e}")
        return r
    if "class" not in source:
        return r
    for func, node, params in _scopes(tree):
        s = _Scope(repo, path, func, node, params, hierarchy, r)
        s.collect()
        s.analyse()
    return r


def iter_py(repo: str, include_tests: bool):
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                             and (include_tests or d not in TEST_DIRS))
        for f in sorted(filenames):
            if not f.endswith(".py"):
                continue
            if not include_tests and (f.startswith("test_") or f.startswith("fake_") or f == "conftest.py"):
                continue
            yield os.path.join(dirpath, f)


def audit_repo(repo: str, parents: dict | None = None, label: str | None = None,
               include_tests: bool = False, base: str | None = None,
               hierarchy: Hierarchy | None = None) -> Result:
    hierarchy = hierarchy or Hierarchy(parents)
    label = label or os.path.basename(os.path.abspath(repo))
    out = Result()
    for p in iter_py(repo, include_tests):
        with open(p, encoding="utf-8", errors="ignore") as f:
            src = f.read()
        out.extend(audit_source(src, os.path.relpath(p, base or repo), label, hierarchy))
    return out


def render(results: dict[str, Result], meta: dict, gaps: dict[str, set[str]] | None = None) -> str:
    L = ["# Properties-class audit of built request bodies", ""]
    L += [f"- {k}: {v}" for k, v in meta.items()]
    L += ["", "## Totals", "", "| repo | files | bodies checked | " + " | ".join(KINDS) +
          " | unclassified | pass-through | table-filtering helper |",
          "|---|---|---|" + "---|" * len(KINDS) + "---|---|---|"]
    for repo, r in results.items():
        cnt = {k: sum(f.kind == k for f in r.findings) for k in KINDS}
        L.append(f"| {repo} | {r.files} | {r.bodies_checked} | " + " | ".join(str(cnt[k]) for k in KINDS) +
                 f" | {len(r.unclassified)} | {r.pass_through} | {r.safe_helper} |")
    for kind in KINDS:
        L += ["", f"## {kind}", ""]
        rows = [f for r in results.values() for f in r.findings if f.kind == kind]
        if not rows:
            L.append("None.")
            continue
        L += ["| repo | file:line | function | class | keys | detail | suggested fix |", "|---|---|---|---|---|---|---|"]
        for f in rows:
            L.append(f"| {f.repo} | `{f.path}:{f.line}` | `{f.func}` | {f.cls or '—'} | "
                     f"{', '.join(f.keys) or '—'} | {f.detail} | {f.fix} |".replace("\n", " "))
    L += ["", "## Unclassified", ""]
    rows = [u for r in results.values() for u in r.unclassified]
    if not rows:
        L.append("None.")
    else:
        L += ["| repo | file:line | function | why not classified |", "|---|---|---|---|"]
        L += [f"| {u.repo} | `{u.path}:{u.line}` | `{u.func}` | {u.reason.replace('|', '/')} |" for u in rows]
    L += ["", "## Table gaps seen in use", "",
          "Keys our code sends that Egeria does read (a public setter in the class chain) but",
          "PROPERTIES_CLASS_FIELDS lacks. Not findings; they are gen_properties_class_fields misses",
          "(package-private fields, or superclasses outside the scanned packages), and Dr.Egeria's",
          "typed_properties would wrongly refuse to send them.", ""]
    if gaps:
        L += ["| class | keys the table lacks |", "|---|---|"]
        L += [f"| {c} | {', '.join(sorted(k))} |" for c, k in sorted(gaps.items())]
    else:
        L.append("None (or no Egeria clone was available to check).")
    errs = [e for r in results.values() for e in r.parse_errors]
    if errs:
        L += ["", "## Files that didn't parse", ""] + [f"- {e}" for e in errs]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--label", action="append", help="display name per repo, in order")
    ap.add_argument("--egeria", default=os.path.expanduser("~/localGit/egeria-v6/egeria"))
    ap.add_argument("--ref", help="Egeria ref for the hierarchy (default: the table's source sha)")
    ap.add_argument("--report", help="write the markdown report here")
    ap.add_argument("--include-tests", action="store_true")
    ap.add_argument("--base", action="append", help="show paths relative to this dir, per repo in order")
    args = ap.parse_args(argv)
    ref = args.ref or table_source_ref()
    parents, setters, how = None, None, "inferred (no Egeria clone); keys checked against the table only"
    if ref and os.path.isdir(args.egeria):
        try:
            parents, setters = load_egeria(args.egeria, ref)
            how = (f"Egeria {ref} (git cat-file, read-only): superclasses, and keys read = table ∪ public "
                   f"setters in the class chain")
        except Exception as e:  # noqa: BLE001 - fall back, and say so in the report
            how = f"inferred (couldn't read Egeria {ref}: {e}); keys checked against the table only"
    hierarchy = Hierarchy(parents, setters)
    labels = args.label or []
    results = {}
    for i, repo in enumerate(args.repos):
        label = labels[i] if i < len(labels) else os.path.basename(os.path.abspath(repo))
        base = args.base[i] if args.base and i < len(args.base) else None
        r = audit_repo(repo, label=label, include_tests=args.include_tests, base=base, hierarchy=hierarchy)
        if label in results:
            results[label].extend(r)
        else:
            results[label] = r
    meta = {"properties table source": table_source_ref() or "unknown", "class hierarchy": how,
            "tests and fakes": "included" if args.include_tests else "skipped"}
    text = render(results, meta, hierarchy.gaps)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    for label, r in results.items():
        print(f"{label}: files={r.files} checked={r.bodies_checked} "
              + " ".join(f"{k}={sum(f.kind == k for f in r.findings)}" for k in KINDS)
              + f" unclassified={len(r.unclassified)} pass_through={r.pass_through} helper={r.safe_helper}",
              file=sys.stderr)
    return 1 if any(r.findings for r in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
