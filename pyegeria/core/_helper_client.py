"""`helper_client`: the one way pyegeria builds a client that acts for another client (Architect C3).

pyegeria builds clients for a caller in several places: EgeriaTech's (and Egeria's, EgeriaConfig's) lazily built
sub-clients, and helpers such as ClassificationExplorer's CollectionManager, AutomatedCuration's
GovernanceEngine, DataDiscovery's AssetMaker, the spec cache's CollectionManager, the unique-name reader's
ClassificationExplorer, and the executor's fallback client. Each copied the caller's `user_pwd` and `token`
attributes. Two things went wrong:

- `set_bearer_token` writes only the Authorization headers, never `self.token`, so a caller given its token
  that way passed `token=None`: the helper had no token and signed in with the password it held;
- a raw `user_pwd` of None is filled by the helper's constructor with the configured default (6.x), so a
  token-only caller's helper held the demo password (the 10-28 shape).

`helper_client(cls, parent, **kw)` builds `cls` on the parent's platform and view server, as the parent's
user, with:

- the parent's BARE token, read from its Authorization header (or its `token`), set once through
  `set_bearer_token` (so exactly one "Bearer " prefix);
- the password: `carried_password(parent)` (the parent's own password, or NO_PASSWORD when it opted out or
  holds none; never the configured default). Under a token the parent didn't mint for itself, NO_PASSWORD: such
  a token is never renewed (see BaseServerClient._owns_token), so a password could only be used to sign in again;
- `_token_minted_for` copied only when the parent minted its token for its own user, so the helper renews the
  token exactly when the parent would.
"""
from __future__ import annotations

from typing import Any, Optional

from pyegeria.core._no_password import NO_PASSWORD, carried_password


def _text(value: Any) -> Optional[str]:
    return (value.strip() or None) if isinstance(value, str) else None


def bare_token(parent: Any) -> Optional[str]:
    """The parent's bearer token without any "Bearer " prefix, or None when it holds none. Read from its
    Authorization header (`get_token`) first, which `set_bearer_token` keeps current, then its `token`."""
    token = None
    # A facade (it holds a _subclient_map) is asked only through its class's own get_token: one that delegates
    # unknown names to its sub-clients (EgeriaConfig's __getattr__) would build a sub-client to answer, and
    # that sub-client is built by this function.
    if "_subclient_map" in getattr(parent, "__dict__", {}):
        method = getattr(type(parent), "get_token", None)
        getter = (lambda: method(parent)) if callable(method) else None
    else:
        getter = getattr(parent, "get_token", None)
    if callable(getter):
        try:
            token = _text(getter())
        except Exception:  # noqa: BLE001 -- no Authorization header
            token = None
    if not token:
        token = _text(getattr(parent, "token", None))
    while token and token.lower().startswith("bearer "):
        token = _text(token[7:])
    return token


def parent_owns_token(parent: Any) -> bool:
    """The parent minted its token for its own user (it would renew it on a 401)."""
    minted = getattr(parent, "_token_minted_for", None)
    return bool(minted) and minted == getattr(parent, "user_id", None)


def helper_password(parent: Any, token: Optional[str]) -> Any:
    """The `user_pwd` a helper acting for `parent` is built with (see the module docstring)."""
    if token and not parent_owns_token(parent):
        return NO_PASSWORD
    return carried_password(parent)


def helper_client(cls: Any, parent: Any, *, view_server: Optional[str] = None, **kwargs: Any) -> Any:
    """`cls` built to act for `parent`: its platform, view server and user; its bare token set once; its own
    password or none, never the configured default; `_token_minted_for` copied only for a self-minted token.
    `kwargs` go to `cls` (timeout=..., legacy_fallback=...)."""
    server = view_server or getattr(parent, "view_server", None) or getattr(parent, "server_name", None)
    token = bare_token(parent)
    client = cls(server, platform_url=getattr(parent, "platform_url", None), user_id=getattr(parent, "user_id", None),
                 user_pwd=helper_password(parent, token), **kwargs)
    if token:
        client.set_bearer_token(token)
        if parent_owns_token(parent):
            client._token_minted_for = parent._token_minted_for
    return client
