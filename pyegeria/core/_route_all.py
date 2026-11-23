# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-64: a by-name helper asked for "everything" runs its own find.

No Egeria by-name endpoint accepts a null name, and "*" there is an exact match (PY-63), so `get_x_by_name("*")`
cannot work as a request. Where a live check on 6.4 showed that the module's `find_x("*")` returns the same
element type and shape as the by-name call (and the two have the same output_format and report_spec defaults),
`@routes_all_to("_async_find_x")` sends the call there. Everything else keeps PY-63's refusal.

Only what the caller passed goes to the find, so the find's own defaults apply (which, for the routed pairs, a test
holds equal to the by-name helper's). A call that carries a `body` is not routed: its name is in the body.
"""
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable


#: The other keywords a caller (or the helper's own body) may carry the name in: the deprecated `filter_string=` and
#: its relatives. A real name in any of them means the call is a by-name call, not a request for everything.
NAME_ALIASES = ("filter_string", "name", "filter", "search_string", "keyword")


def _is_missing(value: Any) -> bool:
    return value is None or str(value).strip() in ("", "*")


def routes_all_to(find_name: str) -> Callable:
    """Decorate an async by-name helper: a None, empty or "*" name (after the helper's own default) is answered
    by `self.<find_name>("*", ...)` with the arguments the caller gave that the find also takes."""
    def decorator(fn: Callable) -> Callable:
        sig = inspect.signature(fn)
        name_param = list(sig.parameters)[1]          # the first argument after self is the name / keyword

        @functools.wraps(fn)
        async def wrapper(self, *args, **kwargs):
            bound = sig.bind(self, *args, **kwargs)
            given = dict(bound.arguments)
            effective = given.get(name_param, sig.parameters[name_param].default)
            extra = next((v for k, v in given.items()
                          if sig.parameters[k].kind is inspect.Parameter.VAR_KEYWORD), {})
            body = given.get("body", extra.get("body"))
            if _is_missing(effective):
                effective = next((extra[a] for a in NAME_ALIASES if a in extra and not _is_missing(extra[a])),
                                 effective)
            if _is_missing(effective) and body is None:
                find = getattr(self, find_name, None)
                if find is not None:
                    find_params = inspect.signature(find).parameters
                    takes_any = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in find_params.values())
                    passed: dict = {}
                    for key, value in given.items():
                        if key in ("self", name_param, "body"):
                            continue
                        if sig.parameters[key].kind is inspect.Parameter.VAR_KEYWORD:
                            passed.update({k: v for k, v in value.items()
                                           if k not in NAME_ALIASES and (takes_any or k in find_params)})
                        elif key in find_params or takes_any:
                            passed[key] = value
                    return await find("*", **passed)
            return await fn(self, *args, **kwargs)

        wrapper.routes_all_to = find_name
        return wrapper
    return decorator
