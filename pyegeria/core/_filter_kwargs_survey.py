"""Static survey of pyegeria's public find_*/get_* methods and the request filters they reach.

Used by the micro-test ``test_search_get_filter_kwargs.py`` (and by the one-off
script that added the ``Unpack[...]`` annotations), so both use one definition of
"a method that sends a filterable request body". Not part of the public API.

A method is in scope when, following ``self.<method>(...)`` calls within
``pyegeria/omvs``, it reaches one of the shared request helpers in
``_server_client`` or builds a body with ``filter_body_kwargs(<kind>, kwargs)``.
"""

from __future__ import annotations

import ast
import collections
import pathlib
from dataclasses import dataclass, field

PACKAGE = pathlib.Path(__file__).resolve().parents[1]

# Shared helper -> the TypedDict that documents its filters.
HELPER_FILTERS: dict[str, str] = {
    "_async_find_request": "SearchFilters",
    "_async_activity_status_search_request": "SearchFilters",
    "_async_content_status_search_request": "SearchFilters",
    "_async_deployment_status_search_request": "SearchFilters",
    "_async_get_name_request": "ListFilters",
    "_async_activity_status_filter_request": "ListFilters",
    "_async_content_status_filter_request": "ListFilters",
    "_async_deployment_status_filter_request": "ListFilters",
    "_async_activity_status_request": "ListFilters",
    "_async_get_results_body_request": "ListFilters",
    "_async_get_guid_request": "GetFilters",
    "_async_get_request_body_request": "GetFilters",
}
# filter_body_kwargs("<kind>", ...) called directly by a method -> TypedDict
KIND_FILTERS: dict[str, str] = {
    "search": "SearchFilters", "deployment_search": "SearchFilters", "activity_search": "SearchFilters",
    "content_search": "SearchFilters", "find": "FindFilters",
    "name": "ListFilters", "list": "ListFilters", "get": "GetFilters",
}
_RANK = {"GetFilters": 0, "ListFilters": 1, "SearchFilters": 2, "FindFilters": 3}


@dataclass
class Method:
    file: str
    cls: str
    name: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    reaches: set[str] = field(default_factory=set)

    @property
    def qualname(self) -> str:
        return f"{self.cls}.{self.name}"

    @property
    def base(self) -> str:
        return self.name.removeprefix("_async_")

    @property
    def is_public_find_get(self) -> bool:
        if self.name.startswith("_") and not self.name.startswith("_async_"):
            return False
        return self.base.startswith(("find_", "get_"))

    @property
    def filters(self) -> str | None:
        names = {HELPER_FILTERS.get(r) or KIND_FILTERS.get(r.removeprefix("kind:")) for r in self.reaches}
        names.discard(None)
        return max(names, key=_RANK.__getitem__) if names else None

    @property
    def explicit_params(self) -> set[str]:
        a = self.node.args
        return {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}

    @property
    def kwargs_name(self) -> str | None:
        return self.node.args.kwarg.arg if self.node.args.kwarg else None

    def passes_kwargs(self) -> bool:
        """True when **kwargs is forwarded: as **kwargs in a call or dict, or handed to filter_body_kwargs."""
        kwn = self.kwargs_name
        if kwn is None:
            return False
        for n in ast.walk(self.node):
            if isinstance(n, ast.keyword) and n.arg is None and isinstance(n.value, ast.Name) and n.value.id == kwn:
                return True
            if isinstance(n, ast.Dict) and any(k is None and isinstance(v, ast.Name) and v.id == kwn
                                               for k, v in zip(n.keys, n.values)):
                return True
            if isinstance(n, ast.Call) and any(isinstance(x, ast.Name) and x.id == kwn for x in n.args):
                return True
        return False

    def unpack_annotation(self) -> str | None:
        """'SearchFilters' when declared as **kwargs: Unpack[SearchFilters], else None."""
        kw = self.node.args.kwarg
        ann = kw.annotation if kw is not None else None
        if isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name) and ann.value.id == "Unpack" \
                and isinstance(ann.slice, ast.Name):
            return ann.slice.id
        return None


def _self_calls(fn) -> tuple[set[str], set[str]]:
    calls, kinds = set(), set()
    for c in ast.walk(fn):
        if not isinstance(c, ast.Call):
            continue
        f = c.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "self":
            calls.add(f.attr)
        if isinstance(f, ast.Name) and f.id == "filter_body_kwargs" and c.args \
                and isinstance(c.args[0], ast.Constant):
            kinds.add(f"kind:{c.args[0].value}")
    return calls, kinds


def survey(package: pathlib.Path = PACKAGE) -> list[Method]:
    """Every method in pyegeria/omvs, with the request helpers it reaches."""
    methods: dict[tuple[str, str, str], Method] = {}
    calls: dict[tuple[str, str, str], set[str]] = {}
    for path in sorted((package / "omvs").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            for fn in cls.body:
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    key = (path.name, cls.name, fn.name)
                    m = Method(path.name, cls.name, fn.name, fn)
                    c, kinds = _self_calls(fn)
                    m.reaches |= kinds
                    methods[key], calls[key] = m, c
    by_name = collections.defaultdict(list)
    for key in methods:
        by_name[key[2]].append(key)
    memo: dict = {}

    def reach(key, stack=()):
        if key in memo:
            return memo[key]
        if key in stack:
            return set()
        out = set(methods[key].reaches)
        for name in calls[key]:
            if name in HELPER_FILTERS:
                out.add(name)
                continue
            same_file = [k for k in by_name.get(name, []) if k[0] == key[0]]
            for k in same_file or by_name.get(name, []):
                out |= reach(k, stack + (key,))
        memo[key] = out
        return out

    for key, m in methods.items():
        m.reaches = reach(key)
    return list(methods.values())


def in_scope(methods: list[Method]) -> list[Method]:
    return [m for m in methods if m.is_public_find_get and m.filters]
