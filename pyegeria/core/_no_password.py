"""`NO_PASSWORD`: an explicit opt-out of the configured default password (owner ruling 2026-11-14, "Opt-out in
6.x").

In pyegeria 6.x a client given `user_pwd=None` (or no password) takes the configured password,
settings.User_Profile.user_pwd; CLIs pass `args.password`, None when the flag is omitted, and rely on that, so
None keeps that meaning. A caller that must never sign in with the configured password (a token-only client
acting for a signed-in user: the Portal, Studio, EA) passes `user_pwd=NO_PASSWORD` instead:

- the client holds no password (`user_pwd` is None) and records `use_default_password = False`;
- `EgeriaTech` (and `EgeriaClient`, `EgeriaConfig`) carry the opt-out to every sub-client they build, and
  pyegeria's internal helper clients carry it from the client they act for (`carried_password`);
- so the settings default password is never used: an expired token fails with a 401, and the one 401 auto-retry
  can't sign in again as the configured (demo) user.

pyegeria 7 drops the default password altogether.
"""
from __future__ import annotations

from typing import Any, Optional, Tuple


class _NoPassword:
    __slots__ = ()

    def __repr__(self) -> str:
        return "NO_PASSWORD"

    def __bool__(self) -> bool:
        return False

    def __reduce__(self):
        return "NO_PASSWORD"


NO_PASSWORD: Any = _NoPassword()


def resolve_password(user_pwd: Any) -> Tuple[Optional[str], bool]:
    """(the password a client holds, whether it may use the configured default). NO_PASSWORD gives
    (None, False); anything else keeps its 6.x meaning: a falsy value takes the configured password."""
    if user_pwd is NO_PASSWORD:
        return None, False
    if user_pwd:
        return user_pwd, True
    from pyegeria.core.config import settings
    return settings.User_Profile.user_pwd, True


def password_as_given(user_pwd: Any) -> Optional[str]:
    """`user_pwd` as the caller gave it, with NO_PASSWORD read as None (for classes that store it as given)."""
    return None if user_pwd is NO_PASSWORD else user_pwd


def carried_password(client: Any) -> Any:
    """The `user_pwd` to build a sub-client or helper client with, acting for `client`: NO_PASSWORD when `client`
    opted out of the default, else the password it holds."""
    if getattr(client, "use_default_password", True) is False:
        return NO_PASSWORD
    return getattr(client, "user_pwd", None)
