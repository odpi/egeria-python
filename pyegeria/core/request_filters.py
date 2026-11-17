"""Standard request filters for pyegeria's find_* and get_* methods.

Every public ``find_*`` / ``get_*`` method that sends a request body accepts the
standard filters as ``**kwargs`` and passes them to the shared request helper in
``pyegeria.core._server_client``. Signatures stay short; this module is the one
place that says what those filters are:

* ``GetFilters``, ``ListFilters`` and ``SearchFilters`` are the PEP 692 TypedDicts
  the methods annotate as ``**kwargs: Unpack[...]`` (editor completion, one-line
  signatures). Each field carries a docstring.
* ``valid_filter_names(kind)`` derives the names each helper accepts from the
  matching request-body model (``GetRequestBody``, ``ResultsRequestBody``,
  ``FilterRequestBody``, ``SearchStringRequestBody`` ...), so it cannot drift from
  what pyegeria actually sends.
* ``filter_body_kwargs(kind, kwargs)`` is what the helpers call: it maps the
  public spellings onto the body's wire names and warns (``UnknownFilterWarning``)
  on any name that is neither a filter nor a known rendering option.
* ``filter_reference_markdown()`` renders the tables in
  ``docs/search-and-get-filters.md`` from the TypedDicts + models (a micro-test
  checks the page is current).

A micro-test checks that each TypedDict, mapped through ``PUBLIC_ALIASES`` and
together with ``CALL_PARAMETERS``, covers exactly the fields of its model.

Plan: an unknown name WARNS in 6.2.28; a later release will raise instead.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import os
import re
import warnings
from datetime import datetime
from functools import lru_cache
from typing import Any, Literal, TypedDict

from loguru import logger

from pyegeria.models.models import (
    ActivityStatusFilterRequestBody,
    ActivityStatusRequestBody,
    ActivityStatusSearchString,
    ContentStatusFilterRequestBody,
    ContentStatusSearchString,
    DeploymentStatusFilterRequestBody,
    DeploymentStatusSearchString,
    FilterRequestBody,
    FindPropertyNamesRequestBody,
    FindRequestBody,
    GetRequestBody,
    ResultsRequestBody,
    SearchStringRequestBody,
)

__all__ = [
    "GetFilters",
    "ListFilters",
    "SearchFilters",
    "FindFilters",
    "UnknownFilterWarning",
    "SearchRefused",
    "FilterKind",
    "valid_filter_names",
    "filter_body_kwargs",
    "filter_reference_markdown",
    "PUBLIC_ALIASES",
    "CALL_PARAMETERS",
    "RENDER_OPTIONS",
    "DEPRECATED_NAMES",
    "deprecated_names",
    "canonicalize_names",
]


class SearchRefused(ValueError):
    """A find_* call refused a search it should not send, such as '*' with no type or a root type
    (it would list every element). A ``ValueError``, so ``except ValueError`` still catches it; the
    report executor logs it at WARNING, as an expected refusal."""


class UnknownFilterWarning(UserWarning):
    """A find_*/get_* call was given a keyword argument that is not a filter for its request.

    pyegeria 6.2.28 warns; a later release will raise ``TypeError`` instead.
    """


# --------------------------------------------------------------------------------------
# The TypedDicts (PEP 692). Keys are the public, snake_case spellings.
# --------------------------------------------------------------------------------------


class GetFilters(TypedDict, total=False):
    """Standard filters for a get_* call that retrieves one element (``GetRequestBody``)."""

    metadata_element_type: str
    """Restrict results to this open metadata type (and its subtypes), e.g. ``"DataClass"``."""
    metadata_element_subtypes: list[str]
    """Only return elements of these subtypes, e.g. ``["DataClass"]``. Honoured on searches and lists; Egeria ignores it on a get-by-GUID."""
    skip_relationships: list[str]
    """Relationship type names to leave out of each element's related-element graph."""
    include_only_relationships: list[str]
    """Only include these relationship type names in each element's related-element graph."""
    skip_classified_elements: list[str]
    """Leave out elements that carry any of these classifications."""
    include_only_classified_elements: list[str]
    """Only return elements that carry one of these classifications."""
    max_mermaid_node_count: int
    """Largest number of nodes Egeria draws in the returned Mermaid graph."""
    governance_zone_filter: list[str]
    """Only return elements in these governance zones."""
    as_of_time: datetime | str
    """Query the repository as it was at this time (ISO-8601 string or datetime)."""
    effective_time: datetime | str
    """Only return elements (and relationships) effective at this time."""
    relationship_page_size: int
    """Page size for the relationships returned with each element (0 = server default)."""
    for_lineage: bool
    """Include elements marked Memento (deleted but kept for lineage)."""
    for_duplicate_processing: bool
    """Return duplicates as stored, without deduplication processing."""
    external_source_guid: str
    """GUID of the external metadata source the request is made on behalf of."""
    external_source_name: str
    """Qualified name of the external metadata source the request is made on behalf of."""
    request_id: str
    """Caller-supplied id echoed in Egeria's audit log for tracing the request."""


class ListFilters(GetFilters, total=False):
    """Standard filters for a get_* call that returns a list, e.g. get_*_by_name (``FilterRequestBody`` / ``ResultsRequestBody``)."""

    anchor_guid: str
    """Only return elements anchored to the element with this GUID."""
    anchor_domain: str
    """Only return elements whose anchor is in this domain (an open metadata type name)."""
    anchor_scope_guid: str
    """Only return elements whose anchor scope is the element with this GUID."""
    limit_results_by_status: list[str]
    """Only return elements whose status is one of these, e.g. ``["ACTIVE"]``; Egeria's ElementStatus: UNKNOWN, ACTIVE, INVALID, DELETED, OTHER (a content status such as DRAFT is refused)."""
    sequencing_order: Literal[
        "ANY", "CREATION_DATE_RECENT", "CREATION_DATE_OLDEST", "LAST_UPDATE_RECENT",
        "LAST_UPDATE_OLDEST", "PROPERTY_ASCENDING", "PROPERTY_DESCENDING",
    ] | str
    """Order of the results; ``PROPERTY_ASCENDING``/``PROPERTY_DESCENDING`` need ``sequencing_property``."""
    sequencing_property: str
    """Property name to sort on when ``sequencing_order`` is a PROPERTY_* order."""


class SearchFilters(ListFilters, total=False):
    """Standard filters for a find_* call (``SearchStringRequestBody`` / ``FindPropertyNamesRequestBody``)."""

    property_names: list[str]
    """Search only these properties (switches the request to ``FindPropertyNamesProperties``)."""


class FindFilters(ListFilters, total=False):
    """Filters for the complex-query finds that send a ``FindRequestBody`` (find_metadata_elements, find_root_elements)."""

    search_properties: dict
    """A ``SearchProperties`` structure: property conditions the elements must match."""
    match_classifications: dict
    """A ``MatchClassifications`` structure: classification conditions the elements must match."""
    skip_subtypes: bool
    """When true, ``metadata_element_subtypes`` lists subtypes to EXCLUDE rather than the only ones to include."""


FilterKind = Literal[
    "get", "list", "name", "search", "find",
    "activity_search", "activity_filter", "activity",
    "content_search", "content_filter",
    "deployment_search", "deployment_filter",
]

# Which request-body model(s) each helper kind sends, and which TypedDict documents it.
_KIND_MODELS: dict[str, tuple[type, ...]] = {
    "get": (GetRequestBody,),
    "list": (ResultsRequestBody,),
    "name": (FilterRequestBody,),
    "search": (SearchStringRequestBody, FindPropertyNamesRequestBody),
    "find": (FindRequestBody,),
    "activity_search": (ActivityStatusSearchString,),
    "activity_filter": (ActivityStatusFilterRequestBody,),
    "activity": (ActivityStatusRequestBody,),
    "content_search": (ContentStatusSearchString,),
    "content_filter": (ContentStatusFilterRequestBody,),
    "deployment_search": (DeploymentStatusSearchString,),
    "deployment_filter": (DeploymentStatusFilterRequestBody,),
}

TYPED_DICT_FOR_MODEL: dict[type, type] = {
    GetRequestBody: GetFilters,
    ResultsRequestBody: ListFilters,
    FilterRequestBody: ListFilters,
    SearchStringRequestBody: SearchFilters,
    FindRequestBody: FindFilters,
}

# Public spelling -> request-body model field. The public spelling is the one the
# search helper (_async_find_request) has always used; the model spelling is accepted too.
PUBLIC_ALIASES: dict[str, str] = {
    "metadata_element_type": "metadata_element_type_name",
    "metadata_element_subtypes": "metadata_element_subtype_names",
    "anchor_domain": "anchor_domain_name",
    "relationship_page_size": "relationships_page_size",
}

# Legacy spellings that are accepted (not advertised in the TypedDicts).
LEGACY_ALIASES: dict[str, str] = {
    # _async_get_name_request's parameter for include_only_classified_elements
    "classification_names": "include_only_classified_elements",
    # Dr.Egeria / report-param spellings (format_set_executor._normalize_report_params maps
    # them to the canonical name but leaves the original key in the params it forwards)
    "limit_result_by_status": "limit_results_by_status",
    "sort_order": "sequencing_order",
    "output_sort_order": "sequencing_order",
    "order_property_name": "sequencing_property",
    "anchor_scope_id": "anchor_scope_guid",
}

# One name everywhere (6.2.28): the element-type and subtype filters are spelt
# metadata_element_type / metadata_element_subtypes in every signature and in **kwargs.
# These older spellings still work, with a DeprecationWarning naming the new one.
DEPRECATED_NAMES: dict[str, str] = {
    "metadata_element_type_name": "metadata_element_type",
    "metadata_element_name": "metadata_element_type",
    "metadata_element_subtype_names": "metadata_element_subtypes",
    "metadata_element_sub_type": "metadata_element_subtypes",
    "metadata_element_subtype": "metadata_element_subtypes",
}
_LIST_VALUED = frozenset({"metadata_element_subtypes"})
_MISSING = object()


def _canonical_value(new: str, value: Any) -> Any:
    """A lone string given for a list-valued filter (e.g. the old metadata_element_sub_type) becomes a list."""
    return [value] if new in _LIST_VALUED and isinstance(value, str) else value


def _deprecation(owner: str, old: str, new: str) -> None:
    warnings.warn(f"{owner}: '{old}' is deprecated; use '{new}'.", DeprecationWarning,
                  skip_file_prefixes=_SKIP_PREFIXES)


def canonicalize_names(kwargs: dict[str, Any], *, owner: str, bound: dict[str, Any] | None = None,
                       warn: bool = True) -> dict[str, Any]:
    """Map deprecated spellings in ``kwargs`` onto the canonical names, in place, and return it.

    Each deprecated name used raises one DeprecationWarning (unless ``warn`` is false). If the
    canonical name is also given (in ``kwargs`` or, via ``bound``, positionally) with a different
    value, raises ``TypeError`` -- the call is ambiguous.
    """
    for old in [k for k in kwargs if k in DEPRECATED_NAMES]:
        new = DEPRECATED_NAMES[old]
        value = _canonical_value(new, kwargs.pop(old))
        if warn:
            _deprecation(owner, old, new)
        given = kwargs.get(new, _MISSING)
        positional = False
        if given is _MISSING and bound is not None and new in bound:
            given, positional = bound[new], True
        if given is not _MISSING and given is not None and value is not None \
                and _canonical_value(new, given) != value:
            raise TypeError(f"{owner}: '{old}' (deprecated) is {value!r} but '{new}' is {given!r}; "
                            f"pass only '{new}'.")
        if (given is _MISSING or given is None) and not positional:
            kwargs[new] = value
    return kwargs


def deprecated_names(**renames: str):
    """Decorator: accept the deprecated spelling(s) of a renamed parameter.

    ``@deprecated_names(metadata_element_type_name="metadata_element_type")`` on a method whose
    parameter is now ``metadata_element_type`` keeps old callers working, with a
    DeprecationWarning, and refuses a call that gives both names with different values.
    """
    import functools

    unknown = {o: n for o, n in renames.items() if DEPRECATED_NAMES.get(o) != n}
    if unknown:
        raise ValueError(f"not in DEPRECATED_NAMES: {unknown}")

    def decorate(func):
        sig = inspect.signature(func)
        owner = func.__qualname__.replace("._async_", ".")

        def fix(args, kwargs):
            if not any(o in kwargs for o in renames):
                return kwargs
            rest = {k: v for k, v in kwargs.items() if k not in renames}
            try:
                bound = sig.bind_partial(*args, **rest).arguments
            except TypeError:
                bound = {}
            positional = {k: v for k, v in bound.items() if k not in rest}
            return canonicalize_names(dict(kwargs), owner=owner, bound=positional)

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **fix(args, kwargs))
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **fix(args, kwargs))
        wrapper.__deprecated_names__ = dict(renames)
        return wrapper

    return decorate

# Body fields every method declares as an explicit parameter (or that the helper
# fills itself). They are valid filter names but are not repeated in the TypedDicts,
# because PEP 692 forbids a TypedDict key that duplicates a named parameter.
CALL_PARAMETERS: dict[type, frozenset[str]] = {
    GetRequestBody: frozenset({"graph_query_depth"}),
    ResultsRequestBody: frozenset({"graph_query_depth", "start_from", "page_size"}),
    FilterRequestBody: frozenset({"graph_query_depth", "start_from", "page_size", "filter_string"}),
    SearchStringRequestBody: frozenset({
        "graph_query_depth", "start_from", "page_size",
        "search_string", "starts_with", "ends_with", "ignore_case",
    }),
    FindRequestBody: frozenset({"graph_query_depth", "start_from", "page_size"}),
}
# FindPropertyNamesRequestBody's property_value is the search string in property-names mode.
_FIND_PROPERTY_NAMES_CALL_PARAMETERS = frozenset({"property_value"})

# kwargs that are not request filters but that the helpers legitimately pass on to
# output rendering (_gen_output / generate_output) or consume themselves.
RENDER_OPTIONS: frozenset[str] = frozenset({
    "refresh_spec",          # RS-EGERIA-TIER: fetch the report spec from Egeria for this call
    "report_format",         # legacy spelling of report_spec in the output formatters
    "max_depth", "include_peers", "include_children",  # graph/tree renderers
    "include_preamble",      # generate_output
    "search_string", "filter_string",  # echoed into report headings by _gen_output
})


@lru_cache(maxsize=None)
def _model_names(model: type) -> tuple[frozenset[str], dict[str, str]]:
    """(field names, {field name or alias -> wire alias}) for a request-body model, without ``class``."""
    names: set[str] = set()
    to_wire: dict[str, str] = {}
    for field_name, info in model.model_fields.items():
        if field_name == "class_":
            continue
        wire = info.alias or field_name
        names.add(field_name)
        to_wire[field_name] = wire
        to_wire[wire] = wire
    return frozenset(names), to_wire


@lru_cache(maxsize=None)
def _wire_map(kind: str) -> dict[str, str]:
    """Every accepted spelling for ``kind`` -> the body's wire (camelCase) name."""
    out: dict[str, str] = {}
    for model in _KIND_MODELS[kind]:
        _, to_wire = _model_names(model)
        out.update(to_wire)
    for public, field_name in {**PUBLIC_ALIASES, **LEGACY_ALIASES}.items():
        if field_name in out:
            out.setdefault(public, out[field_name])
    return out


def valid_filter_names(kind: str) -> frozenset[str]:
    """The snake_case filter names a ``kind`` of request accepts (model fields + public aliases)."""
    names: set[str] = set()
    for model in _KIND_MODELS[kind]:
        names |= _model_names(model)[0]
    names |= {p for p, f in PUBLIC_ALIASES.items() if f in names}
    return frozenset(names)


def _calling_method() -> str:
    """Best-effort name of the public pyegeria method a warning is about."""
    best = None
    frame = inspect.currentframe()
    while frame is not None:
        name = frame.f_code.co_name
        if re.match(r"^(_async_)?(find|get)_", name) and not name.endswith("_request") \
                and "pyegeria" in frame.f_code.co_filename:
            owner = frame.f_locals.get("self")
            best = f"{type(owner).__name__}.{name.removeprefix('_async_')}" if owner is not None else name
        frame = frame.f_back
    return best or "a find/get call"


_SKIP_PREFIXES = (
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep,  # the pyegeria package
    os.path.dirname(os.path.abspath(asyncio.__file__)) + os.sep,           # event-loop plumbing (run_sync)
)


def filter_body_kwargs(kind: str, kwargs: dict[str, Any], *, ignore: frozenset[str] | set[str] = frozenset()) -> dict[str, Any]:
    """Return the request-body entries for the filter kwargs of a ``kind`` request.

    Keys are the body's wire names (camelCase), so they override the helper's own
    defaults when splatted last into the body dict; ``None`` values are dropped. A name that is neither a filter
    for this request, a rendering option, nor in ``ignore`` raises an
    ``UnknownFilterWarning`` that names the bad key(s) and lists the valid ones;
    it is left out of the body (Pydantic would have dropped it silently anyway).
    """
    if any(k in DEPRECATED_NAMES for k in kwargs):
        kwargs = canonicalize_names(dict(kwargs), owner=_calling_method())
    wire = _wire_map(kind)
    body: dict[str, Any] = {}
    unknown: list[str] = []
    for key, value in kwargs.items():
        if key in wire:
            if value is not None:  # None means "not set": never override the helper's own default
                body[wire[key]] = value
        elif key in RENDER_OPTIONS or key in ignore:
            continue
        else:
            unknown.append(key)
    if unknown:
        valid = sorted(valid_filter_names(kind) - set(PUBLIC_ALIASES.values()))
        method = _calling_method()
        plural = "s" if len(unknown) > 1 else ""
        msg = (f"{method}: unknown filter{plural} {', '.join(repr(k) for k in unknown)} ignored. "
               f"Valid filters for this request: {', '.join(valid)}. "
               f"(pyegeria will raise an error for unknown filters in a future release.)")
        logger.warning(msg)
        warnings.warn(msg, UnknownFilterWarning, skip_file_prefixes=_SKIP_PREFIXES)
    return body


# --------------------------------------------------------------------------------------
# Documentation tables, rendered from the TypedDicts and models above.
# --------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _field_docs() -> dict[str, dict[str, str]]:
    """{TypedDict name: {field: docstring}} parsed from this module's source."""
    with open(__file__, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    docs: dict[str, dict[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in {"GetFilters", "ListFilters", "SearchFilters", "FindFilters"}:
            fields: dict[str, str] = {}
            body = node.body
            for i, stmt in enumerate(body):
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    nxt = body[i + 1] if i + 1 < len(body) else None
                    if isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant) and isinstance(nxt.value.value, str):
                        fields[stmt.target.id] = nxt.value.value
            docs[node.name] = fields
    return docs


def _own_fields(td: type) -> list[str]:
    parents = [b for b in td.__orig_bases__ if b is not TypedDict and isinstance(b, type)]
    inherited = set().union(*(set(p.__annotations__) for p in parents)) if parents else set()
    return [k for k in td.__annotations__ if k not in inherited]


def _type_text(td: type, key: str) -> str:
    with open(__file__, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == td.__name__:
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and getattr(stmt.target, "id", None) == key:
                    text = ast.unparse(stmt.annotation)
                    return "str" if text.startswith("Literal[") else text.replace("Literal[...] | ", "")
    return ""


def filter_reference_markdown() -> str:
    """Markdown tables of the standard filters, generated from the TypedDicts and request-body models."""
    docs = _field_docs()
    lines: list[str] = []
    rows = [
        ("GetFilters", GetFilters, "`GetRequestBody`", "get_*_by_guid and other single-element gets"),
        ("ListFilters", ListFilters, "`FilterRequestBody` (by name) / `ResultsRequestBody`", "get_*_by_name and other list gets"),
        ("SearchFilters", SearchFilters, "`SearchStringRequestBody` / `FindPropertyNamesRequestBody`", "find_*"),
        ("FindFilters", FindFilters, "`FindRequestBody`", "the complex-query finds (find_metadata_elements, find_root_elements)"),
    ]
    for name, td, body, used in rows:
        lines.append(f"### `{name}`")
        lines.append("")
        parent = [b.__name__ for b in td.__orig_bases__ if isinstance(b, type) and b.__name__ in {"GetFilters", "ListFilters"}]
        extra = f" Everything in `{parent[0]}`, plus:" if parent else ""
        lines.append(f"Used by {used}. Maps to {body}.{extra}")
        lines.append("")
        lines.append("| Filter | Type | Wire name | Meaning |")
        lines.append("|---|---|---|---|")
        wire = _wire_map({"GetFilters": "get", "ListFilters": "name", "SearchFilters": "search", "FindFilters": "find"}[name])
        for key in _own_fields(td):
            doc = docs[name].get(key, "").replace("``", "`")
            lines.append(f"| `{key}` | `{_type_text(td, key)}` | `{wire[key]}` | {doc} |".replace(" | str`", " \\| str`"))
        lines.append("")
    lines.append("### Call parameters (explicit on the method, also accepted as filters)")
    lines.append("")
    lines.append("| Request body | Parameters |")
    lines.append("|---|---|")
    for model, params in CALL_PARAMETERS.items():
        extra = _FIND_PROPERTY_NAMES_CALL_PARAMETERS if model is SearchStringRequestBody else frozenset()
        lines.append(f"| `{model.__name__}` | {', '.join(f'`{p}`' for p in sorted(params | extra))} |")
    lines.append("")
    lines.append("### Other accepted spellings")
    lines.append("")
    lines.append("| You may write | Same as |")
    lines.append("|---|---|")
    for alias, field_name in {**PUBLIC_ALIASES, **LEGACY_ALIASES}.items():
        lines.append(f"| `{alias}` | `{field_name}` |")
    lines.append("")
    lines.append("### Deprecated spellings")
    lines.append("")
    lines.append("These still work, with a `DeprecationWarning` naming the new name. Giving both the old and the "
                 "new name with different values raises `TypeError`.")
    lines.append("")
    lines.append("| Deprecated | Use |")
    lines.append("|---|---|")
    for old, new in DEPRECATED_NAMES.items():
        lines.append(f"| `{old}` | `{new}` |")
    lines.append("")
    lines.append("Each model field's camelCase wire name (e.g. `metadataElementSubtypeNames`) is accepted as well. "
                 "These rendering options are passed through to output formatting and are not warned about: "
                 + ", ".join(f"`{o}`" for o in sorted(RENDER_OPTIONS)) + ".")
    return "\n".join(lines) + "\n"
