"""The Egeria credentials this process has made view-server clients with.

The report-spec cache reads its EGERIA tier for a credential identity. Inside `exec_report_spec`, the async
runner and the dashboard resolver, that identity is set from the request's client. A read made outside them
(listing, describing, `report_spec_source`) has no client, so it uses the identity of this process's clients:
when the process has seen exactly one, that one. A process that has seen more than one is serving several
users, and no private cache loads outside a request's own identity there.

This module only records; `pyegeria.view.egeria_spec_cache.current_spec_identity` decides.
"""
from __future__ import annotations

import threading
from typing import Any, List, Optional, Tuple

_LOCK = threading.Lock()
_SEEN: List[Tuple[str, Optional[str], Optional[str]]] = []
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
    """Forget every noted credential (tests)."""
    with _LOCK:
        _SEEN.clear()
