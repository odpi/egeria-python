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


def _allowed_endpoint(query_url: Any, client) -> Tuple[str, Tuple[str, ...], Optional[str]]:
    """The pyegeria method, body classes and an optional note for a stored Query URL, or SavedQueryRefused.

    The URL is checked, never followed: the call always goes to this client's own platform. So the stored
    host is not the boundary (the Portal stores queryURL from inside its container, e.g.
    https://host.docker.internal:9443/..., while a notebook or EA uses https://localhost:9443): a different
    http(s) scheme or host:port is accepted and noted. User info, a query string, a fragment, a
    scheme-relative URL, an odd path, another view server and a path off the allow-list are refused."""
    if not isinstance(query_url, str) or not query_url.strip():
        raise SavedQueryRefused("The saved query has no Query URL, so there is no stored request to run.")
    raw = query_url.strip()
    if any(c in raw for c in ("\\", "%", "\n", "\r", "\t", " ")):
        raise SavedQueryRefused(f"The saved query's Query URL {raw!r} has characters a query endpoint path "
                                f"never has, so it is not run.")
    if raw.startswith("//"):
        raise SavedQueryRefused(f"The saved query's Query URL {raw!r} is scheme-relative, so it is not run.")
    parts = urlsplit(raw)
    if parts.query or parts.fragment:
        raise SavedQueryRefused(f"The saved query's Query URL {raw!r} carries a query string or fragment; "
                                f"only a bare endpoint path is run.")
    note = None
    if parts.scheme or parts.netloc:
        if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
            raise SavedQueryRefused(f"The saved query's Query URL {raw!r} is not an http(s) URL, so it is not run.")
        if "@" in parts.netloc:
            raise SavedQueryRefused(f"The saved query's Query URL {raw!r} carries user info, so it is not run.")
        if (parts.scheme.lower(), parts.netloc.lower()) != _client_origin(client):
            note = (f"the stored URL names {parts.scheme}://{parts.netloc}; the request went to this client's "
                    f"platform ({getattr(client, 'platform_url', '')}), never to the stored host")
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
    method, classes = ALLOWED_QUERY_ENDPOINTS[path]
    return method, classes, note


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

    Parameters (a saved query as a template, brief §9; one model with the Portal)
    -----------------------------------------------------------------------------
    A SavedQuery may declare `additionalProperties.parameters`, a JSON list of
    {"name", "type", "default"?, "searchPath"?, "requestPath"?}. The type is one of the Portal's:
    string/str, integer/int, number/float, boolean/bool, list/array. There are no placeholders: the
    stored bodies stay valid requests, which Egeria's Smart Collections connector runs literally.
    - `searchPath` (default: `name`) is a dotted path into the stored Portal search (`formula`, else
      `additionalProperties.searchSpec`), where the Portal's refresh applies the value.
    - `requestPath` is a dotted path into the stored `queryRequestBody`, where live mode applies the
      value: typed, as a value only, never in a key and never in the URL, which is not a template.
    - Effective value, the same rule as the Portal: the value given, else the stored search value at
      `searchPath`, else the default. A cached answer is returned only when `lastRefreshParams` (which
      the Portal records for every declared name) equals that map; otherwise it is refused, and the
      reason points to live mode. The result carries `params`, labelled "as of <time>, for k=v, ...".
    - Live mode: every parameter's effective value (from `formula`, never the value already in
      `queryRequestBody`) is set at its `requestPath`; a declared `pageSize` becomes the read's page
      size, and `startFrom` stays the read's own. A parameter with no `requestPath` applies to the
      Portal's search only, so live mode refuses it when it is given, or when its effective value is a
      default the stored search doesn't hold.
    - A SavedQuery registered as a Smart Collection (`additionalProperties.smartCollection == "true"`,
      the Portal's test) is re-run by Egeria's SmartCollectionsMembershipManager about every 30
      minutes from its stored request. Its cached answer stands only for the stored effective values
      (whatever a refresh recorded), is labelled "kept current by Egeria", and is refused for other
      values, pointing to live mode.
    An undeclared name, a value of the wrong type, a string with control characters or over 512
    characters, a bad path, or params on a query that declares none, is refused with a sentence.

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
        effective = _effective_parameters(declared, params, _stored_search(props, additional))
    except SavedQueryRefused as refused:
        return _result(name, mode, output, state="not_established", reason=refused.sentence,
                       absence="not_applicable", refused=True)

    registered = _is_registered_smart_collection(additional)
    if mode == "cached" and registered:
        # P-3: Egeria's SmartCollectionsMembershipManager re-runs the STORED request about every 30 minutes,
        # so the Results Set answers only for the stored effective values, whatever a refresh recorded.
        used = _effective_parameters(declared, None, _stored_search(props, additional)) if declared else {}
        if declared and effective != used:
            return _not_measured(name, "cached", output, f"this saved query is a Smart Collection, kept current by "
                                 f"Egeria with its stored values ({_label(used)}), so its cached answer cannot "
                                 f"stand for {_label(effective)}; use mode live for these values")
        out = _cached(client, name, output, additional, page_size, max_pages, kept_current=True)
    elif mode == "cached":
        used = effective
        if declared:
            recorded = _recorded_parameters(additional.get("lastRefreshParams"))
            if recorded is None:
                return _not_measured(name, "cached", output, f"the cached answer does not record the parameter "
                                     f"values it was refreshed with, so it cannot stand for {_label(effective)}; "
                                     f"use mode live")
            if recorded != effective:
                return _not_measured(name, "cached", output, f"the cached answer is for {_label(recorded)}, not "
                                     f"{_label(effective)}; use mode live for these values")
        out = _cached(client, name, output, additional, page_size, max_pages)
    else:
        try:
            method, classes, note = _allowed_endpoint(props.get("queryURL"), client)
            body = _request_body(props.get("queryRequestBody"), classes)
            body, used = _apply_request_parameters(declared, params, body, effective,
                                                   _stored_search(props, additional))
        except SavedQueryRefused as refused:
            logger.warning(f"saved_query: refused to run {name!r}: {refused.sentence}")
            return _result(name, mode, output, state="not_established", reason=refused.sentence,
                           absence="not_applicable", refused=True)
        if any(p.get("requestPath") == "pageSize" for p in declared) and isinstance(body.get("pageSize"), int):
            page_size = max(1, min(body["pageSize"], 1000))  # a declared page size is the read's page size
        out = _live(client, name, output, method, body, page_size, max_pages)
        out["how"] = f"{method} on this client's platform" + (f"; {note}" if note else "")
    if declared:
        out["params"] = used
        if out.get("subtitle") and out.get("asOf"):
            out["subtitle"] = out["subtitle"].replace(f"as of {out['asOf']}",
                                                      f"as of {out['asOf']}, for {_label(used)}", 1)
        elif out.get("subtitle"):
            out["subtitle"] = f"{out['subtitle']}, for {_label(used)}"
    return out


def _is_registered_smart_collection(additional: Dict[str, Any]) -> bool:
    """The Portal's own test (insights_handler._is_registered_smart_collection)."""
    return str((additional or {}).get("smartCollection") or "").strip().lower() == "true"


# ── parameters: one model with the Portal (insights_handler, b9dce798) ──────

# The Portal's types, read the same way: no coercion, and a bool is never an int.
_PARAM_TYPES = {
    "string": (str,), "str": (str,),
    "integer": (int,), "int": (int,),
    "number": (int, float), "float": (int, float),
    "boolean": (bool,), "bool": (bool,),
    "list": (list,), "array": (list,),
}
_PATH = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.([A-Za-z_][A-Za-z0-9_]*|[0-9]+))*$")
_MAX_STRING = 512


def _json_value(raw: Any, what: str) -> Any:
    if isinstance(raw, str):
        if not raw.strip():
            return None
        try:
            return json.loads(raw)
        except ValueError:
            raise SavedQueryRefused(f"The saved query's {what} is not JSON.")
    return raw


def _declared_parameters(raw: Any) -> List[Dict[str, Any]]:
    decl = _json_value(raw, "declared parameters")
    if decl is None:
        return []
    if not isinstance(decl, list):
        raise SavedQueryRefused("The saved query's declared parameters are not a list.")
    out: List[Dict[str, Any]] = []
    seen = set()
    for d in decl:
        name = d.get("name") if isinstance(d, dict) else None
        if not isinstance(name, str) or not _PATH.match(name):
            raise SavedQueryRefused(f"The saved query declares a parameter {d!r} with no plain (dotted) name.")
        if name in seen:
            raise SavedQueryRefused(f"The saved query declares the parameter {name!r} twice.")
        seen.add(name)
        ptype = str(d.get("type") or "string").lower()
        if ptype not in _PARAM_TYPES:
            raise SavedQueryRefused(f"The saved query's parameter {name!r} has type {ptype!r}; the types are "
                                    f"string, integer, number, boolean, list.")
        for key in ("searchPath", "requestPath"):
            if d.get(key) is not None and (not isinstance(d[key], str) or not _PATH.match(d[key])):
                raise SavedQueryRefused(f"The saved query's parameter {name!r} has a {key} {d[key]!r} that is not "
                                        f"a plain dotted path.")
        entry = {**d, "type": ptype}
        if "default" in d and d["default"] is not None:
            _check_value(name, entry, d["default"])  # a bad default is refused too
        out.append(entry)
    return out


def _check_value(name: str, p: Dict[str, Any], value: Any) -> Any:
    ptype = p["type"]
    if (isinstance(value, bool) and ptype not in ("boolean", "bool")) or not isinstance(value, _PARAM_TYPES[ptype]):
        raise SavedQueryRefused(f"Parameter {name!r} must be a {ptype}, not {type(value).__name__} ({value!r}).")
    for v in (value if isinstance(value, list) else [value]):
        if isinstance(v, str) and (len(v) > _MAX_STRING or any(ord(c) < 32 for c in v)):
            raise SavedQueryRefused(f"Parameter {name!r}: a value is over {_MAX_STRING} characters or has "
                                    f"control characters.")
        if isinstance(value, list) and not (v is None or isinstance(v, (str, int, float, bool))):
            raise SavedQueryRefused(f"Parameter {name!r}: a list holds plain values only.")
    return value


def _path_parts(path: str) -> List[Any]:
    return [int(x) if x.isdigit() else x for x in path.split(".")]


def _get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in _path_parts(path):
        try:
            cur = cur[part]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


def _set_path(obj: Any, path: str, value: Any, name: str) -> None:
    parts = _path_parts(path)
    cur = obj
    for part in parts[:-1]:
        try:
            cur = cur[part]
        except (KeyError, IndexError, TypeError):
            raise SavedQueryRefused(f"Parameter {name!r}: its requestPath {path!r} points at nothing in the "
                                    f"stored request (no {part!r}).")
    if isinstance(cur, (dict, list)) is False or (isinstance(cur, list) and not isinstance(parts[-1], int)):
        raise SavedQueryRefused(f"Parameter {name!r}: its requestPath {path!r} points at nothing in the stored "
                                f"request.")
    try:
        cur[parts[-1]] = value
    except (IndexError, TypeError):
        raise SavedQueryRefused(f"Parameter {name!r}: its requestPath {path!r} points at nothing in the stored "
                                f"request.")


def _stored_search(props: Dict[str, Any], additional: Dict[str, Any]) -> Dict[str, Any]:
    """The Portal's stored search: `formula`, else `additionalProperties.searchSpec` (as the Portal reads it)."""
    for raw in (props.get("formula"), additional.get("searchSpec")):
        try:
            spec = _json_value(raw, "stored search")
        except SavedQueryRefused:
            spec = None
        if isinstance(spec, dict) and spec:
            return spec
    return {}


def _effective_parameters(declared: List[Dict[str, Any]], given: Optional[Dict[str, Any]],
                          search: Dict[str, Any]) -> Dict[str, Any]:
    """Every declared name's effective value, by the Portal's rule: the value given, else the stored search
    value at searchPath, else the default. This is what the Portal records as lastRefreshParams."""
    given = dict(given or {})
    if given and not declared:
        raise SavedQueryRefused(f"The saved query declares no parameters, so {sorted(given)} cannot be set.")
    by_name = {p["name"]: p for p in declared}
    unknown = sorted(k for k in given if k not in by_name)
    if unknown:
        raise SavedQueryRefused(f"The saved query does not declare {unknown}; it declares {sorted(by_name)}.")
    values: Dict[str, Any] = {}
    for name, p in by_name.items():
        stored = _get_path(search, p.get("searchPath") or name)
        if name in given:
            values[name] = _check_value(name, p, given[name])
        elif stored is None and "default" in p:
            values[name] = _check_value(name, p, p["default"]) if p["default"] is not None else None
        else:
            values[name] = stored
    return values


# Paging keys the live read owns: a parameter may set the page size (it becomes the read's page size),
# never where the read starts.
_PAGING_OWNED = ("startFrom",)


def _apply_request_parameters(declared, given, body, effective, search) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """The stored request with every parameter's effective value set at its requestPath (typed, a value
    only), on a copy, and the values the run used.

    The effective value is the Portal's: the value given, else the value at searchPath in the stored
    search (`formula`, what the Portal ran), else the default. It is NOT the value already at requestPath
    in queryRequestBody: the two can differ (the Portal strips paging from formula, while queryRequestBody
    always says pageSize 500), and the Portal's record of a refresh is keyed on the former. A parameter with
    no requestPath can't change the request, so live mode is refused when it is given, or when its effective
    value is not what the stored search holds (a default)."""
    given = dict(given or {})
    body = json.loads(json.dumps(body))  # never change the stored copy
    used: Dict[str, Any] = {}
    for p in declared:
        name, rp = p["name"], p.get("requestPath")
        value = effective.get(name)
        if not rp:
            from_search = _get_path(search, p.get("searchPath") or name) is not None
            if name in given or (not from_search and value is not None):
                raise SavedQueryRefused(f"Parameter {name!r} applies to the Portal's search only (it has no "
                                        f"requestPath), so it cannot be set live; use mode cached, or refresh it "
                                        f"in the Portal with that value.")
            used[name] = value
            continue
        if _path_parts(rp)[0] in _PAGING_OWNED:
            raise SavedQueryRefused(f"Parameter {name!r}: its requestPath {rp!r} is paging the live read owns.")
        if value is not None:
            _set_path(body, rp, value, name)
        used[name] = value
    return body, used


def _recorded_parameters(raw: Any) -> Optional[Dict[str, Any]]:
    try:
        rec = _json_value(raw, "recorded refresh parameters")
    except SavedQueryRefused:
        return None
    return rec if isinstance(rec, dict) else None


def _label(values: Dict[str, Any]) -> str:
    return ", ".join(f"{k}={json.dumps(v)}" for k, v in sorted(values.items())) or "no parameter values"


def _cached(client, name, output, additional, page_size, max_pages, kept_current=False):
    as_of = additional.get("lastRefreshedTime") or None
    results_set = additional.get("resultsSetGuid") or None
    if not results_set:
        return _not_measured(name, "cached", output, "the saved query records no Results Set, so it has no "
                                                     "cached answer; use mode live, or refresh it")
    if not as_of and not kept_current:
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
    out = _answer(name, "cached", output, members, capped, as_of)
    if kept_current:
        out["keptCurrentBy"] = "Egeria (Smart Collection, re-run about every 30 minutes from the stored request)"
        when = f" \u00b7 as of {as_of}" if as_of else " \u00b7 no refresh time recorded"
        if out["state"] in ("measured", "nothing_found"):
            out["subtitle"] = "kept current by Egeria" + when + (
                f" \u00b7 at least {out['atLeast']}: the read stopped at its bound" if out.get("capped") else "")
    return out


def _live(client, name, output, method, body, page_size, max_pages):
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
