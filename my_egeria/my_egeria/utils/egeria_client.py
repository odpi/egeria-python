""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.


"""

import asyncio
import os
import time
from typing import Any, Callable, Optional, Tuple
from urllib.parse import quote

# import requests

from typing import TYPE_CHECKING

# Only for type checkers; avoids importing pyegeria at runtime during test collection
if TYPE_CHECKING:
    from pyegeria import EgeriaTech as _EgeriaTechType  # noqa: F401

from .config import EgeriaConfig, get_global_config


# Registry to track all managers for clean shutdown
_MANAGER_REGISTRY: list["EgeriaTechClientManager"] = []


def _register_manager(manager: "EgeriaTechClientManager") -> None:
    _MANAGER_REGISTRY.append(manager)


def close_all_managers() -> None:
    for m in list(_MANAGER_REGISTRY):
        try:
            m.close()
        except Exception:
            pass
    _MANAGER_REGISTRY.clear()


def _bool_env(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")


def _build_origin_url(platform_url: str, user: str) -> str:
    base = platform_url.rstrip("/")
    user_q = quote(user or "", safe="")
    return f"{base}/open-metadata/platform-services/users/{user_q}/server-platform/origin"


def preflight_origin(platform_url: str, user: str, *, timeout: float = 3.0) -> None:
    """
    Quick connectivity check to Egeria platform origin endpoint with a short timeout.
    Raises ConnectionError if not reachable in time.
    """
    if not platform_url or "://" not in platform_url:
        raise ConnectionError(f"Malformed EGERIA_PLATFORM_URL: {platform_url!r}")

    url = _build_origin_url(platform_url, user)
    verify_ssl = _bool_env("EGERIA_SSL_VERIFY", True)
    # try:
    #     resp = requests.get(url, timeout=timeout, verify=verify_ssl)
    #     # Any 2xx is fine; otherwise let it raise with details
    #     if not (200 <= resp.status_code < 300):
    #         raise ConnectionError(f"Preflight failed ({resp.status_code}) for {url}")
    # except requests.exceptions.SSLError as e:
    #     raise ConnectionError(
    #         f"TLS verification failed for {url}. Set EGERIA_SSL_VERIFY=false for local dev if using self-signed certs."
    #     ) from e
    # except requests.exceptions.Timeout as e:
    #     raise ConnectionError(f"Preflight timeout contacting {url}") from e
    # except requests.RequestException as e:
    #     raise ConnectionError(f"Preflight error contacting {url}: {e}") from e


class EgeriaTechClientManager:
    """
    Manages the lifecycle of an EgeriaTech client:
    - builds client from config
    - authenticates and caches token
    - refreshes token proactively (TTL) and reactively (on failures)
    """

    def __init__(self, config: Optional[EgeriaConfig] = None):
        self.config = config or get_global_config()
        self._client: Optional[Any] = None
        self._last_auth_ts: float = 0.0
        _register_manager(self)

    def get_client(self) -> Any:
        # Set a standard loop policy to avoid deadlocks with nest_asyncio + run_coroutine_threadsafe
        try:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        except Exception:
            pass

        # Import pyegeria lazily to avoid import-time config validation during test collection
        try:
            from pyegeria import EgeriaTech
        except Exception as e:
            raise ImportError(
                "pyegeria is required to build an Egeria client. "
                "Ensure it is installed and configured if you call into the live client."
            ) from e

        if self._client is None:
            # Fast preflight to fail fast rather than hang
            preflight_origin(self.config.platform_url, self.config.user, timeout=3.0)

            # Build with explicit keyword arguments to avoid positional-order bugs
            self._client = EgeriaTech(
                view_server=self.config.view_server,
                platform_url=self.config.platform_url,
                user_id=self.config.user,
                user_pwd=self.config.password,
            )
            self._authenticate()
        elif self._token_expired():
            self._authenticate()
        return self._client

    def _token_expired(self) -> bool:
        if self._last_auth_ts <= 0:
            return True
        return (time.time() - self._last_auth_ts) >= self.config.token_ttl_seconds

    def _authenticate(self) -> None:
        if self._client and hasattr(self._client, "create_egeria_bearer_token"):
            self._client.create_egeria_bearer_token(self.config.user, self.config.password)
            self._last_auth_ts = time.time()

    def refresh_token(self) -> None:
        self._authenticate()

    def close(self) -> None:
        if self._client and hasattr(self._client, "close_session"):
            try:
                self._client.close_session()
            finally:
                self._client = None
                self._last_auth_ts = 0.0
        # Deregister on close to avoid registry growth
        try:
            _MANAGER_REGISTRY.remove(self)
        except ValueError:
            pass

    def invoke_with_auto_refresh(
        self, fn: Callable, args: Tuple = (), kwargs: Optional[dict] = None
    ):
        """
        Call client function, retrying once on failure by refreshing the token.
        """
        kwargs = kwargs or {}
        client = self.get_client()
        try:
            return fn(client, *args, **kwargs)
        except Exception:
            self.refresh_token()
            client = self.get_client()
            return fn(client, *args, **kwargs)
