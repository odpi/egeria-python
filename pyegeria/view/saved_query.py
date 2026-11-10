"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

`saved_query`: a saved query as the source of a Report (Route B, 6.2.34).

A Report names a SavedQuery by qualifiedName, and a tile shows its answer as a count (KPI) or a list.
The SavedQuery is found as the viewer, so zones apply.
- mode="cached": the members of its Results Set (the last answer, materialised by the Portal's
  refresh or by Egeria's Smart Collections connector), with the refresh time ("as of ...").
- mode="live": runs the stored request now, with the viewer's token. It reads every page (an empty
  page is the end) up to a bound, and marks a stopped read `capped` with a lower bound, never a total.

Security. A SavedQuery's Query URL is authored data, and a Report can name anyone's SavedQuery, so the
stored URL never chooses where the viewer's token goes (the Portal's ?url= leak was this class). The
URL is only checked, never followed:
- its path must name one allow-listed view-server query endpoint, as a relative path or under this
  client's own `/servers/<view server>`;
- an absolute URL is accepted only when it names this client's own platform (same scheme, host and
  port, no user info) and view server: the shape the Portal itself stores. Any other host, port,
  scheme or view server, a query string, a fragment, or an encoded or dotted path is refused with a
  sentence;
- the request is then made by pyegeria's own method for that endpoint, on the viewer's own client.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

from loguru import logger

__all__ = ["saved_query", "SavedQueryRefused", "ALLOWED_QUERY_ENDPOINTS", "SAVED_QUERY_PAGE_SIZE",
           "SAVED_QUERY_MAX_PAGES"]

# Allow-listed view-server query endpoints (path below /servers/<view server>), each with the pyegeria
# method that calls it and the request-body classes it takes. Nothing else is ever run.
ALLOWED_QUERY_ENDPOINTS: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "/api/open-metadata/metadata-expert/metadata-elements/by-search-conditions":
        ("find_metadata_elements", ("FindRequestBody",)),
}

SAVED_QUERY_PAGE_SIZE = 500
SAVED_QUERY_MAX_PAGES = 20  # 10,000 elements; a read that has not ended by then is a lower bound

_QUERY_TYPE = "SavedQuery"


class SavedQueryRefused(ValueError):
    """The saved query's stored request is not one this function will run. `sentence` says why."""

    def __init__(self, sentence: str):
        self.sentence = sentence
        super().__init__(sentence)


# ── reading an OpenMetadataElement ─────────────────────────────────────────

def _value(v: Any) -> Any:
    """A property value from an OpenMetadataElement's propertyValueMap, as plain Python."""
    if not isinstance(v, dict):
        return v
    if "primitiveValue" in v:
        return v["primitiveValue"]
    if "mapValues" in v:
        return {k: _value(x) for k, x in ((v["mapValues"] or {}).get("propertyValueMap") or {}).items()}
    if "arrayValues" in v:
        items = ((v["arrayValues"] or {}).get("propertyValueMap") or {})
        return [_value(items[k]) for k in sorted(items, key=lambda k: int(k) if str(k).isdigit() else k)]
    return v


def _properties(el: Dict[str, Any]) -> Dict[str, Any]:
    """Properties of an element in either shape: OpenMetadataElement or a view-service bean."""
    pvm = ((el.get("elementProperties") or {}).get("propertyValueMap"))
    if isinstance(pvm, dict):
        return {k: _value(v) for k, v in pvm.items()}
    return dict(el.get("properties") or {})


def _guid(el: Dict[str, Any]) -> str:
    return el.get("elementGUID") or (el.get("elementHeader") or {}).get("guid") or ""


def _type_name(el: Dict[str, Any]) -> str:
    t = el.get("type") or (el.get("elementHeader") or {}).get("type") or {}
    return t.get("typeName") or ""


def _elements(result: Any) -> List[Dict[str, Any]]:
    """An Egeria list result; its 'No elements found' string is an empty list."""
    if isinstance(result, dict):
        result = [result]
    return [e for e in result if isinstance(e, dict)] if isinstance(result, list) else []


def _summary(el: Dict[str, Any]) -> Dict[str, Any]:
    p = _properties(el)
    return {"guid": _guid(el), "typeName": _type_name(el), "qualifiedName": p.get("qualifiedName"),
            "displayName": p.get("displayName") or p.get("name")}


# ── the allow-list ─────────────────────────────────────────────────────────

def _client_origin(client) -> Tuple[str, str]:
    parts = urlsplit(str(getattr(client, "platform_url", "") or ""))
    return parts.scheme.lower(), parts.netloc.lower()


def _allowed_endpoint(query_url: Any, client) -> Tuple[str, Tuple[str, ...]]:
    """The pyegeria method and body classes for a stored Query URL, or SavedQueryRefused."""
    if not isinstance(query_url, str) or not query_url.strip():
        raise SavedQueryRefused("The saved query has no Query URL, so there is no stored request to run.")
    raw = query_url.strip()
    if any(c in raw for c in ("\\", "%", "\n", "\r", "\t", " ")):
        raise SavedQueryRefused(f"The saved query's Query URL {raw!r} has characters a query endpoint path "
                                f"never has, so it is not run.")
    parts = urlsplit(raw)
    if parts.query or parts.fragment:
        raise SavedQueryRefused(f"The saved query's Query URL {raw!r} carries a query string or fragment; "
                                f"only a bare endpoint path is run.")
    if parts.scheme or parts.netloc or raw.startswith("//"):
        scheme, origin = _client_origin(client)
        if "@" in parts.netloc or parts.scheme.lower() != scheme or parts.netloc.lower() != origin:
            raise SavedQueryRefused(
                f"The saved query's Query URL names {parts.scheme}://{parts.netloc}, not this platform: a stored "
                f"URL never chooses where your token is sent, so it is not run.")
    path = parts.path if parts.path.startswith("/") else "/" + parts.path
    if "//" in path or any(seg in (".", "..") for seg in path.split("/")):
        raise SavedQueryRefused(f"The saved query's Query URL path {path!r} is not a plain endpoint path, "
                                f"so it is not run.")
    if path.startswith("/servers/"):
        segs = path.split("/", 3)  # ['', 'servers', '<view server>', 'api/...']
        server = segs[2] if len(segs) > 2 else ""
        if server != str(getattr(client, "view_server", "")):
            raise SavedQueryRefused(f"The saved query's Query URL names view server {server!r}, not "
                                    f"{getattr(client, 'view_server', '')!r}, so it is not run.")
        path = "/" + (segs[3] if len(segs) > 3 else "")
    if path not in ALLOWED_QUERY_ENDPOINTS:
        raise SavedQueryRefused(f"The saved query's Query URL path {path!r} is not one of the query endpoints a "
                                f"Report may run ({', '.join(sorted(ALLOWED_QUERY_ENDPOINTS))}).")
    return ALLOWED_QUERY_ENDPOINTS[path]


def _request_body(stored: Any, classes: Tuple[str, ...]) -> Dict[str, Any]:
    if isinstance(stored, str):
        try:
            stored = json.loads(stored) if stored.strip() else None
        except ValueError:
            raise SavedQueryRefused("The saved query's Query Request Body is not JSON, so it is not run.")
    if not isinstance(stored, dict):
        raise SavedQueryRefused("The saved query has no Query Request Body to run.")
    if stored.get("class") not in classes:
        raise SavedQueryRefused(f"The saved query's Query Request Body is a {stored.get('class')!r}; this "
                                f"endpoint takes {', '.join(classes)}.")
    return stored


# ── the function ───────────────────────────────────────────────────────────

def _exact_qn_body(qn: str) -> Dict[str, Any]:
    return {"class": "FindRequestBody", "metadataElementTypeName": _QUERY_TYPE, "graphQueryDepth": 0,
            "startFrom": 0, "pageSize": 10,
            "searchProperties": {"class": "SearchProperties", "matchCriteria": "ALL", "conditions": [{
                "property": "qualifiedName", "operator": "EQ",
                "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": qn}}]}}


def _result(name: str, mode: str, output: str, *, state: str, reason: str = "", absence: Optional[str] = None,
            count: Optional[int] = None, elements: Optional[List[Dict[str, Any]]] = None,
            capped: bool = False, as_of: Optional[str] = None, refused: bool = False) -> Dict[str, Any]:
    out: Dict[str, Any] = {"savedQuery": name, "mode": mode, "output": output, "state": state,
                           "state_reason": reason, "value": count, "capped": capped,
                           "atLeast": count if capped else None, "asOf": as_of,
                           "display": None if count is None else (f"≥{count}" if capped else str(count))}
    if capped:
        out["value"] = None  # a lower bound is never a total
    if absence:
        out["absence"] = absence
    if refused:
        out["refused"] = True
    out["elements"] = (elements if elements is not None else []) if output == "list" else None
    if as_of and state in ("measured", "nothing_found"):
        out["subtitle"] = f"as of {as_of}" + (f" · at least {count}: the read stopped at its bound"
                                              if capped else "")
    return out


def _is_not_visible(exc: BaseException) -> bool:
    from pyegeria.view.dashboard_resolver import is_not_visible_error  # lazy: keeps imports light
    return is_not_visible_error(exc)


def _not_measured(name, mode, output, reason):
    return _result(name, mode, output, state="not_established", reason=reason, absence="not_measured")


def _read_pages(fetch, page_size: int, max_pages: int) -> Tuple[List[Dict[str, Any]], bool]:
    """Every element `fetch(start_from, page_size)` returns, paging until an empty page. Returns
    (elements, capped): capped when `max_pages` pages were read and the next was not shown to be empty."""
    found: List[Dict[str, Any]] = []
    start = 0
    for _ in range(max_pages):
        page = _elements(fetch(start, page_size))
        if not page:
            return found, False
        found.extend(page)
        start += len(page)
    return found, True


def saved_query(client, name: str, mode: str = "cached", output: str = "count",
                params: Optional[Dict[str, Any]] = None,
                page_size: int = SAVED_QUERY_PAGE_SIZE, max_pages: int = SAVED_QUERY_MAX_PAGES) -> Dict[str, Any]:
    """
    The answer of a SavedQuery named by `name` (its qualifiedName), as the viewer sees it.

    Parameters
    ----------
    client : EgeriaTech, already authenticated as the viewer
    name : the SavedQuery's qualifiedName
    mode : "cached" (its Results Set's members, as of the last refresh) or "live" (run the stored
        request now, with the viewer's token, through the allow-list)
    output : "count" (a KPI: `value`) or "list" (`elements`: guid, typeName, qualifiedName, displayName)
    params : values for the SavedQuery's declared parameters (see "Parameters" below)
    page_size, max_pages : the read's page size and bound; a read stopped by the bound is a lower bound

    Parameters (a saved query as a template, brief §9)
    --------------------------------------------------
    A SavedQuery may declare `additionalProperties.parameters`, a JSON list of
    {"name", "type": "string"|"int"|"bool"|"enum", "default", "required", "values" (for an enum)}.
    Its request body names a parameter as a whole value, "{{name}}", which is replaced by the typed
    value: never concatenated into a string, never put in a key, and never in the URL, which is not a
    template at all. An undeclared name, a missing required value, a value of the wrong type, or a
    placeholder anywhere else is refused with a sentence. With no declaration, any `params` is refused.
    The result carries `params`, the values it ran with (defaults included). A cached answer is the
    one its last refresh made, so it is returned only when the refresh recorded the same values
    (`additionalProperties.lastRefreshParams`); otherwise it is refused, and the reason points to live
    mode. A cached answer is never returned as if it matched other values.

    Returns a dict:
    - `value`: the count; None when it is not established or is only a lower bound;
    - `capped` and `atLeast`: whether the read stopped at its bound, and the lower bound;
    - `display`: "N", or "≥N" for a bound;
    - `asOf`: the refresh time for a cached answer, now for a live one;
    - `state`, `state_reason` and `absence`: the state envelope.

    It never returns 0 for an answer it could not read. A query that was never refreshed, a missing
    or hidden SavedQuery, or a refused URL is `not_established`, with the reason; a refused URL also
    sets `refused`. A refused Query URL never raises.
    """
    mode = (mode or "cached").lower()
    output = (output or "count").lower()
    if mode not in ("cached", "live"):
        raise ValueError(f"saved_query: mode must be 'cached' or 'live', not {mode!r}")
    if output not in ("count", "list"):
        raise ValueError(f"saved_query: output must be 'count' or 'list', not {output!r}")
    if not name:
        raise ValueError("saved_query: name (the SavedQuery's qualifiedName) is required")
    page_size = max(1, min(int(page_size or SAVED_QUERY_PAGE_SIZE), 1000))
    max_pages = max(1, int(max_pages or SAVED_QUERY_MAX_PAGES))

    try:
        found = _elements(client.find_metadata_elements(body=_exact_qn_body(name)))
    except Exception as exc:  # noqa: BLE001
        if _is_not_visible(exc):
            return _result(name, mode, output, state="not_established", absence="not_permitted",
                           reason=f"the saved query {name!r} is not visible to you")
        logger.debug(f"saved_query: lookup of {name!r} failed: {exc}")
        return _not_measured(name, mode, output, f"the saved query {name!r} could not be read "
                                                 f"({type(exc).__name__})")
    exact = [e for e in found if _properties(e).get("qualifiedName") == name]
    if not exact:
        return _not_measured(name, mode, output, f"no saved query named {name!r} is visible to you (it may "
                                                 f"not exist, or may be in a zone you cannot see)")
    if len(exact) > 1:
        return _not_measured(name, mode, output, f"{len(exact)} saved queries are named {name!r}; name one by "
                                                 f"a unique qualifiedName")
    props = _properties(exact[0])
    additional = props.get("additionalProperties") or {}
    if not isinstance(additional, dict):
        additional = {}

    try:
        declared = _declared_parameters(additional.get("parameters"))
        values = _bind_parameters(declared, params)
    except SavedQueryRefused as refused:
        return _result(name, mode, output, state="not_established", reason=refused.sentence,
                       absence="not_applicable", refused=True)

    if mode == "cached":
        if declared:
            recorded = _recorded_parameters(additional.get("lastRefreshParams"))
            if recorded is None:
                return _not_measured(name, "cached", output, f"the cached answer does not record the parameter "
                                     f"values it was refreshed with, so it cannot stand for {_label(values)}; "
                                     f"use mode live")
            if recorded != values:
                return _not_measured(name, "cached", output, f"the cached answer is for {_label(recorded)}, not "
                                     f"{_label(values)}; use mode live for these values")
        out = _cached(client, name, output, additional, page_size, max_pages)
    else:
        try:
            props = dict(props, queryRequestBody=_substitute(props.get("queryRequestBody"), values))
        except SavedQueryRefused as refused:
            return _result(name, mode, output, state="not_established", reason=refused.sentence,
                           absence="not_applicable", refused=True)
        out = _live(client, name, output, props, page_size, max_pages)
    if declared:
        out["params"] = values
        if out.get("subtitle"):
            out["subtitle"] = out["subtitle"].replace(f"as of {out['asOf']}",
                                                      f"as of {out['asOf']}, for {_label(values)}", 1)
    return out


# ── parameters ─────────────────────────────────────────────────────────────

_PARAM_TYPES = ("string", "int", "bool", "enum")
_PLACEHOLDER = re.compile(r"^\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}$")
_MAX_STRING = 512


def _json_list(raw: Any, what: str) -> Any:
    if isinstance(raw, str):
        if not raw.strip():
            return None
        try:
            return json.loads(raw)
        except ValueError:
            raise SavedQueryRefused(f"The saved query's {what} is not JSON.")
    return raw


def _declared_parameters(raw: Any) -> Dict[str, Dict[str, Any]]:
    decl = _json_list(raw, "declared parameters")
    if decl is None:
        return {}
    if not isinstance(decl, list):
        raise SavedQueryRefused("The saved query's declared parameters are not a list.")
    out: Dict[str, Dict[str, Any]] = {}
    for d in decl:
        if not isinstance(d, dict) or not isinstance(d.get("name"), str) or not re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*", d["name"]):
            raise SavedQueryRefused(f"The saved query declares a parameter {d!r} with no plain name.")
        kind = d.get("type") or "string"
        if kind not in _PARAM_TYPES:
            raise SavedQueryRefused(f"The saved query's parameter {d['name']!r} has type {kind!r}; the types are "
                                    f"{', '.join(_PARAM_TYPES)}.")
        if kind == "enum" and not (isinstance(d.get("values"), list) and d["values"]):
            raise SavedQueryRefused(f"The saved query's enum parameter {d['name']!r} lists no values.")
        if d["name"] in out:
            raise SavedQueryRefused(f"The saved query declares the parameter {d['name']!r} twice.")
        out[d["name"]] = {"type": kind, "values": d.get("values"), "required": bool(d.get("required")),
                          "default": d.get("default")}
        if d.get("default") is not None:
            _typed(d["name"], out[d["name"]], d["default"])  # a bad default is refused too
    return out


def _typed(name: str, decl: Dict[str, Any], value: Any) -> Any:
    kind = decl["type"]
    if kind == "int":
        if isinstance(value, bool) or not (isinstance(value, int) or isinstance(value, str)
                                           and re.fullmatch(r"-?[0-9]{1,18}", value)):
            raise SavedQueryRefused(f"Parameter {name!r} takes an int, not {value!r}.")
        return int(value)
    if kind == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.lower() in ("true", "false"):
            return value.lower() == "true"
        raise SavedQueryRefused(f"Parameter {name!r} takes true or false, not {value!r}.")
    if not isinstance(value, str):
        raise SavedQueryRefused(f"Parameter {name!r} takes a string, not {value!r}.")
    if len(value) > _MAX_STRING or any(ord(c) < 32 for c in value) or "{{" in value or "}}" in value:
        raise SavedQueryRefused(f"Parameter {name!r}: the value is too long, has control characters, or "
                                f"looks like a placeholder.")
    if kind == "enum" and value not in decl["values"]:
        raise SavedQueryRefused(f"Parameter {name!r} takes one of {decl['values']}, not {value!r}.")
    return value


def _bind_parameters(declared: Dict[str, Dict[str, Any]], given: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    given = dict(given or {})
    if given and not declared:
        raise SavedQueryRefused(f"The saved query declares no parameters, so {sorted(given)} cannot be set.")
    unknown = sorted(k for k in given if k not in declared)
    if unknown:
        raise SavedQueryRefused(f"The saved query does not declare {unknown}; it declares {sorted(declared)}.")
    values: Dict[str, Any] = {}
    for pname, decl in declared.items():
        if pname in given and given[pname] is not None:
            values[pname] = _typed(pname, decl, given[pname])
        elif decl["default"] is not None:
            values[pname] = _typed(pname, decl, decl["default"])
        elif decl["required"]:
            raise SavedQueryRefused(f"Parameter {pname!r} is required and has no default.")
    return values


def _recorded_parameters(raw: Any) -> Optional[Dict[str, Any]]:
    try:
        rec = _json_list(raw, "recorded refresh parameters")
    except SavedQueryRefused:
        return None
    return rec if isinstance(rec, dict) else None


def _label(values: Dict[str, Any]) -> str:
    return ", ".join(f"{k}={json.dumps(v)}" for k, v in sorted(values.items())) or "no parameter values"


def _substitute(stored: Any, values: Dict[str, Any]) -> Any:
    """The stored request body with each whole-value "{{name}}" replaced by its typed value. A placeholder
    in a key, inside a longer string, or for a value not bound is refused. The URL is never touched."""
    if isinstance(stored, str):
        if "{{" not in stored:
            return stored
        try:
            stored = json.loads(stored)
        except ValueError:
            return stored  # _request_body refuses it with its own sentence

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            for k in node:
                if "{{" in str(k) or "}}" in str(k):
                    raise SavedQueryRefused("A placeholder appears in a key of the saved query's request body; "
                                            "placeholders are values only.")
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str) and ("{{" in node or "}}" in node):
            m = _PLACEHOLDER.match(node)
            if not m:
                raise SavedQueryRefused(f"The saved query's request body has a placeholder inside a longer string "
                                        f"({node!r}); a placeholder must be a whole value.")
            if m.group(1) not in values:
                raise SavedQueryRefused(f"The saved query's request body names {m.group(1)!r}, which has no value "
                                        f"(it is not declared, or has no default and was not given).")
            return values[m.group(1)]
        return node

    return walk(stored)


def _cached(client, name, output, additional, page_size, max_pages):
    as_of = additional.get("lastRefreshedTime") or None
    results_set = additional.get("resultsSetGuid") or None
    if not results_set:
        return _not_measured(name, "cached", output, "the saved query records no Results Set, so it has no "
                                                     "cached answer; use mode live, or refresh it")
    if not as_of:
        return _not_measured(name, "cached", output, "the saved query has never been refreshed, so its "
                                                     "Results Set holds no answer yet (not an empty answer)")
    try:
        members, capped = _read_pages(
            lambda start, size: client.get_collection_members(collection_guid=results_set, start_from=start,
                                                              page_size=size, output_format="JSON"),
            page_size, max_pages)
    except Exception as exc:  # noqa: BLE001
        if _is_not_visible(exc):
            return _result(name, "cached", output, state="not_established", absence="not_permitted",
                           reason="the saved query's Results Set is not visible to you")
        return _not_measured(name, "cached", output, f"its Results Set could not be read ({type(exc).__name__})")
    return _answer(name, "cached", output, members, capped, as_of)


def _live(client, name, output, props, page_size, max_pages):
    try:
        method, classes = _allowed_endpoint(props.get("queryURL"), client)
        body = _request_body(props.get("queryRequestBody"), classes)
    except SavedQueryRefused as refused:
        logger.warning(f"saved_query: refused to run {name!r}: {refused.sentence}")
        return _result(name, "live", output, state="not_established", reason=refused.sentence,
                       absence="not_applicable", refused=True)
    fn = getattr(client, method)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        found, capped = _read_pages(
            lambda start, size: fn(body={**body, "startFrom": start, "pageSize": size, "graphQueryDepth": 0}),
            page_size, max_pages)
    except Exception as exc:  # noqa: BLE001
        if _is_not_visible(exc):
            return _result(name, "live", output, state="not_established", absence="not_permitted",
                           reason="Egeria refused the saved query's request for you")
        return _not_measured(name, "live", output, f"the saved query's request failed ({type(exc).__name__})")
    return _answer(name, "live", output, found, capped, now)


def _answer(name, mode, output, elements, capped, as_of):
    n = len(elements)
    listed = [_summary(e) for e in elements] if output == "list" else None
    if n == 0:
        return _result(name, mode, output, state="nothing_found", absence="nothing_found", count=0,
                       elements=listed, as_of=as_of, reason="the saved query's answer is empty")
    return _result(name, mode, output, state="measured", count=n, elements=listed, capped=capped, as_of=as_of)
