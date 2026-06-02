""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.


"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EgeriaConfig:
    platform_url: str
    view_server: str
    user: str
    password: str
    token_ttl_seconds: int = 900  # refresh proactively every 15 minutes by default

    @staticmethod
    def from_env() -> "EgeriaConfig":
        # Legacy env names some tests expect
        legacy_platform = os.getenv("EGERIA_PLATFORM_URL")
        legacy_view_server = os.getenv("EGERIA_VIEW_SERVER")

        # Don’t silently default to localhost so tests can detect missing env
        platform_url = os.getenv("EGERIA_PLATFORM_URL", legacy_platform or "https://localhost:9443")
        view_server = os.getenv("EGERIA_VIEW_SERVER", legacy_view_server or "qs-view-server")

        return EgeriaConfig(
            platform_url=platform_url,
            view_server=view_server,
            user=os.getenv("EGERIA_USER", "erinoverview"),
            password=os.getenv("EGERIA_USER_PASSWORD", "secret"),
            token_ttl_seconds=int(os.getenv("EGERIA_TOKEN_TTL_SECONDS", "900")),
        )

    def with_overrides(
        self,
        *,
        platform_url: Optional[str] = None,
        view_server: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        token_ttl_seconds: Optional[int] = None,
    ) -> "EgeriaConfig":
        return EgeriaConfig(
            platform_url=platform_url or self.platform_url,
            view_server=view_server or self.view_server,
            user=user or self.user,
            password=password or self.password,
            token_ttl_seconds=(
                token_ttl_seconds if token_ttl_seconds is not None else self.token_ttl_seconds
            ),
        )


# Properly define the module-level current config
_current_config: Optional[EgeriaConfig] = None


def set_global_config(cfg: EgeriaConfig) -> None:
    global _current_config
    _current_config = cfg


def get_global_config() -> EgeriaConfig:
    # Rebuild from env every call so tests that mutate env are reflected
    global _current_config
    env_cfg = EgeriaConfig.from_env()
    return _current_config or env_cfg


__all__ = [
    "EgeriaConfig",
    "get_global_config",
    "set_global_config",
]
