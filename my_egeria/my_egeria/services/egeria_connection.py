# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the functions of my_egeria module.


"""

from __future__ import annotations

from typing import Optional

from ..utils.config import get_global_config
from ..utils.egeria_client import preflight_origin


# Shim for tests
PlatformServices = None


class EgeriaConnectionService:
    """Checks if Egeria is reachable and authenticates."""

    def __init__(self):
        cfg = get_global_config()
        self.view_server = cfg.view_server
        self.platform_url = cfg.platform_url
        self.user = cfg.user
        self.password = cfg.password
        self.platform_status: str = "Not connected"

    def is_connected(self) -> bool:
        try:
            preflight_origin(self.platform_url, self.user, timeout=2.0)
            return True
        except Exception:
            return False

    def connect_to_egeria(
        self,
        user: str,
        password: str,
        platform_url: str,
        view_server: str,
    ) -> bool:
        """Update connection parameters and perform authentication."""
        self.user = user
        self.password = password
        self.platform_url = platform_url
        self.view_server = view_server
        return self.authenticate(user, password)

    def authenticate(self, username: str, password: str) -> bool:
        try:
            from pyegeria import EgeriaTech

            client = EgeriaTech(
                view_server=self.view_server,
                platform_url=self.platform_url,
                user_id=self.user,
                user_pwd=self.password,
            )
            if hasattr(client, "create_egeria_bearer_token"):
                client.create_egeria_bearer_token(username, password)
            if hasattr(client, "close_session"):
                client.close_session()
            return True
        except Exception:
            return False

    def verify_connection(self) -> bool:
        if not self.platform_url:
            raise ConnectionError("Egeria platform URL not set.")
        if "://" not in self.platform_url:
            raise ConnectionError(f"Malformed Egeria platform URL: {self.platform_url}")

        # Fast preflight first
        preflight_origin(self.platform_url, self.user, timeout=2.0)
        self.platform_status = "running"
        return True


# ---------------- Module-level functional API (test-friendly) ----------------

_SERVICE_SINGLETON: Optional[EgeriaConnectionService] = None


def _service() -> EgeriaConnectionService:
    global _SERVICE_SINGLETON
    if _SERVICE_SINGLETON is None:
        _SERVICE_SINGLETON = EgeriaConnectionService()
    return _SERVICE_SINGLETON


def connect_to_egeria(
    user: str,
    password: str,
    platform_url: str,
    view_server: str,
) -> bool:
    """Functional facade for tests and callers that patch at module level."""
    return _service().connect_to_egeria(user, password, platform_url, view_server)


def is_connected() -> bool:
    """Quick connectivity check."""
    return _service().is_connected()


def verify_connection() -> bool:
    """Verify connectivity, raising on failure."""
    return _service().verify_connection()


__all__ = [
    "EgeriaConnectionService",
    "connect_to_egeria",
    "is_connected",
    "verify_connection",
]
