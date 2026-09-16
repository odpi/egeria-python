"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Fake/live backend switch for the My Profile App test suite.

   By default every test in this folder runs against in-memory fakes, exactly as
   it always has. Setting ``PYEG_LIVE_EGERIA=1`` flips the suite over to a real
   Egeria view server (``https://localhost:9443`` by default) so the same tests
   exercise the real SDK calls, URLs and response shapes.

   The mechanism is deliberately small: ``EgeriaBackend.patch()`` replaces a
   symbol with a plain ``MagicMock`` in fake mode, and with
   ``MagicMock(wraps=<the real thing>)`` in live mode. Because a wrapping mock
   still records every call, assertions about *how* the app called Egeria
   (verbs, report-spec names, params) hold identically in both modes — only
   assertions about the returned *data* need to differ, and those go through
   :meth:`EgeriaBackend.expect`.

   WARNING: live mode is not read-only. ``create_profile``,
   ``create_digital_subscription`` and ``initiate_gov_action_process`` are
   executed for real against the configured server.
"""

from __future__ import annotations

import contextlib
import importlib
import os
import uuid
from typing import Any, Callable
from unittest.mock import MagicMock, patch

# Enable live mode with PYEG_LIVE_EGERIA=1 (same switch the rest of the repo uses).
LIVE_ENV = "PYEG_LIVE_EGERIA"

# Live connection details, each overridable by its own environment variable.
CONNECTION_ENV: dict[str, tuple[str, str]] = {
    "platform_url": ("PYEG_PLATFORM_URL", "https://localhost:9443"),
    "view_server": ("PYEG_SERVER_NAME", "qs-view-server"),
    "user_id": ("PYEG_USER_ID", "garygeeke"),
    "user_pwd": ("PYEG_USER_PWD", "secret"),
}

# pyegeria settings keys that must point at the live server before the app's
# load_app_config() caches them.
PYEGERIA_ENV_FOR = {
    "platform_url": "EGERIA_PLATFORM_URL",
    "view_server": "EGERIA_VIEW_SERVER",
    "user_id": "EGERIA_USER",
    "user_pwd": "EGERIA_USER_PASSWORD",
}


def env_truthy(name: str, default: bool = False) -> bool:
    """Interpret an environment variable as a boolean flag."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def live_requested() -> bool:
    """True when the caller asked for live Egeria tests."""
    return env_truthy(LIVE_ENV)


def connection_settings() -> dict[str, str]:
    """Resolve the Egeria connection details, honouring per-field overrides."""
    return {key: os.getenv(env_var, default) for key, (env_var, default) in CONNECTION_ENV.items()}


def export_pyegeria_env(settings: dict[str, str] | None = None) -> None:
    """Point pyegeria's own config at the live server.

    ``load_app_config()`` caches on first call, so this has to happen before any
    test constructs a screen or an app.
    """
    settings = settings or connection_settings()
    for key, env_var in PYEGERIA_ENV_FOR.items():
        os.environ[env_var] = settings[key]


_PROBE_UNSET = object()
_probe_result: Any = _PROBE_UNSET


def live_unavailable_reason() -> str | None:
    """Return None when the live server is usable, else why it is not.

    The result is probed once per session: a live run that cannot authenticate
    should skip cleanly rather than produce a screenful of connection errors.
    """
    global _probe_result
    if _probe_result is not _PROBE_UNSET:
        return _probe_result  # type: ignore[return-value]

    settings = connection_settings()
    try:
        from pyegeria.core._server_client import ServerClient

        client = ServerClient(
            server_name=settings["view_server"],
            platform_url=settings["platform_url"],
            user_id=settings["user_id"],
            user_pwd=settings["user_pwd"],
        )
        token = client.create_egeria_bearer_token(settings["user_id"], settings["user_pwd"])
        _probe_result = None if token else "the server returned no bearer token"
    except Exception as e:  # noqa: BLE001 - any failure means "not usable"
        _probe_result = f"{type(e).__name__}: {e}"
    return _probe_result  # type: ignore[return-value]


class UnexpectedNetworkCall(RuntimeError):
    """Raised when a fake-mode test reaches a real server."""


def block_network(monkeypatch, test_name: str) -> None:
    """Fail fake-mode tests that issue a real HTTP request.

    Without this, a test whose Egeria calls are only partly mocked passes
    quietly while depending on a reachable server — and then behaves
    differently on a machine that has none. pyegeria talks to Egeria through
    httpx, so intercepting its transport catches every route.
    """
    import httpx

    def _refuse(self, request, *args, **kwargs):
        raise UnexpectedNetworkCall(
            f"{test_name} tried to reach {request.url} while running against fakes. "
            "Patch the Egeria client/function through the `backend` fixture "
            "(backend.patch / backend.always_fake), or mark the test "
            "`@pytest.mark.allow_network` if the call is genuinely intended."
        )

    monkeypatch.setattr(httpx.Client, "send", _refuse)
    monkeypatch.setattr(httpx.AsyncClient, "send", _refuse)


def _resolve(target: str) -> Any:
    """Resolve a 'module.attribute' patch target to the live object."""
    module_name, _, attr = target.rpartition(".")
    if not module_name:
        raise ValueError(f"patch target must be 'module.attribute', got {target!r}")
    return getattr(importlib.import_module(module_name), attr)


# --- live-mode predicates for EgeriaBackend.expect ---------------------------

def nonempty_str(value: Any) -> bool:
    """Live check: a real, non-blank string came back."""
    return isinstance(value, str) and value.strip() != ""


def is_int(value: Any) -> bool:
    """Live check: an integer came back (karma points, counts, ...)."""
    return isinstance(value, int) and not isinstance(value, bool)


def at_least(minimum: int) -> Callable[[Any], bool]:
    """Live check: a size/count of at least `minimum`."""

    def _check(value: Any) -> bool:
        try:
            size = len(value)
        except TypeError:
            size = value
        return isinstance(size, int) and size >= minimum

    return _check


class EgeriaBackend:
    """Per-test handle on whichever backend the suite is running against."""

    def __init__(self, live: bool, stack: contextlib.ExitStack, **settings: str) -> None:
        self.live = live
        self.platform_url = settings["platform_url"]
        self.view_server = settings["view_server"]
        self.user_id = settings["user_id"]
        self.user_pwd = settings["user_pwd"]
        self._stack = stack

    # --- patching ------------------------------------------------------------

    def patch(self, target: str, *, returns: Any = None, side_effect: Any = None) -> MagicMock:
        """Switchable patch of `target`.

        Fake mode: a plain MagicMock returning `returns` (or raising
        `side_effect`). Live mode: a MagicMock wrapping the real object, so the
        call reaches Egeria and the returned mock still records call args.
        """
        if self.live:
            mock = MagicMock(wraps=_resolve(target))
        else:
            mock = MagicMock(return_value=returns, side_effect=side_effect)
        self._stack.enter_context(patch(target, mock))
        return mock

    def always_fake(self, target: str, *, returns: Any = None, side_effect: Any = None) -> MagicMock:
        """Patch `target` with a pure fake in both modes.

        For paths a live server cannot be asked to produce on demand — injected
        exceptions, deliberately empty result sets — where the test is really
        about the app's own error handling.
        """
        mock = MagicMock(return_value=returns, side_effect=side_effect)
        self._stack.enter_context(patch(target, mock))
        return mock

    def patch_object(self, target: Any, attribute: str, replacement: Any) -> Any:
        """Patch an attribute that is not Egeria-related in either mode (UI bits)."""
        return self._stack.enter_context(patch.object(target, attribute, replacement))

    # --- assertions ----------------------------------------------------------

    def expect(
        self,
        actual: Any,
        *,
        fake: Any,
        live: Callable[[Any], bool] | None = None,
        label: str = "value",
    ) -> None:
        """Assert on data whose exact value depends on the backend.

        In fake mode `actual` must equal `fake`. In live mode `live` (if given)
        must accept `actual`; with no `live` predicate the value is not checked,
        because the live server legitimately holds different content.
        """
        if self.live:
            if live is not None:
                assert live(actual), f"live-mode check failed for {label}: {actual!r}"
        else:
            assert actual == fake, f"{label}: expected {fake!r}, got {actual!r}"

    # --- helpers -------------------------------------------------------------

    def unique(self, value: str) -> str:
        """Make a name unique per live run; unchanged in fake mode.

        Egeria enforces uniqueness on qualifiedName, so a live write test that
        reuses a fixed display name passes once and then fails with a 409 on
        every subsequent run. Fake mode keeps the literal so its assertions
        stay exact.
        """
        return f"{value} {uuid.uuid4().hex[:8]}" if self.live else value

    def apply_connection(self, target: Any) -> None:
        """Point a test harness app at the active backend."""
        target.user_name = self.user_id
        target.user_password = self.user_pwd
        target.view_server = self.view_server
        target.platform_url = self.platform_url
