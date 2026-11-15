"""The Egeria credentials this process has made view-server clients with, and whether it serves many users.

The report-spec cache reads its EGERIA tier for a credential identity. Inside `exec_report_spec`, the async
runner and the dashboard resolver, that identity is set from the request's client. A read made outside them
(listing, describing, `report_spec_source`) has no client, so it uses the identity of this process's clients:
when the process has seen exactly one, that one. A process that has seen more than one is serving several
users, and no private cache loads outside a request's own identity there.

A process that serves many users declares it (`declare_multi_user()`, or PYEGERIA_MULTI_USER=1): the Portal, EA,
Studio and the MCP HTTP server. Counting identities is only a backstop there: a server builds clients as its
service user and then swaps `user_id` to the signed-in user's (the Portal's use_token), so the first identity
recorded is the service user's until a second one is seen. A declared process never takes a fallback identity.

This module only records; `pyegeria.view.egeria_spec_cache.current_spec_identity` decides.
"""
from __future__ import annotations

import os
import threading
from typing import Any, List, Optional, Tuple

_LOCK = threading.Lock()
_SEEN: List[Tuple[str, Optional[str], Optional[str]]] = []
_MULTI_USER = False
MULTI_USER_ENV = "PYEGERIA_MULTI_USER"
_MAX_SEEN = 16   # the reader only needs "one" or "more than one"; a long-running multi-user process stops growing


def note_credentials(user_id: Any, platform_url: Any, view_server: Any) -> None:
    """Record a (user, platform url, view server) this process makes Egeria calls with. Never raises."""
    if not isinstance(user_id, str) or not user_id.strip() or user_id.strip() == "?":
        return
    entry = (user_id.strip(), platform_url if isinstance(platform_url, str) and platform_url else None,
             view_server if isinstance(view_server, str) and view_server else None)
    with _LOCK:
        if entry not in _SEEN and len(_SEEN) < _MAX_SEEN:
            _SEEN.append(entry)


def note_client(client: Any) -> None:
    """`note_credentials` for a client object (its view_server, else its server_name)."""
    note_credentials(getattr(client, "user_id", None), getattr(client, "platform_url", None),
                     getattr(client, "view_server", None) or getattr(client, "server_name", None))


def seen_credentials() -> List[Tuple[str, Optional[str], Optional[str]]]:
    with _LOCK:
        return list(_SEEN)


def reset_credentials() -> None:
    """Forget every noted credential and any multi-user declaration (tests)."""
    global _MULTI_USER
    with _LOCK:
        _SEEN.clear()
        _MULTI_USER = False


def declare_multi_user(multi_user: bool = True) -> None:
    """Declare that this process serves more than one Egeria user (call at startup). Then no read outside a
    request's own identity (`spec_identity`) takes a fallback identity: no private cache loads for it and no
    fetched copy is served to it."""
    global _MULTI_USER
    _MULTI_USER = bool(multi_user)


def is_multi_user() -> bool:
    """Declared multi-user: `declare_multi_user()` or PYEGERIA_MULTI_USER=1/true/yes."""
    return _MULTI_USER or os.getenv(MULTI_USER_ENV, "").strip().lower() in ("1", "true", "yes")
