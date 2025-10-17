"""
Pytest configuration for pyegeria tests.

This file introduces a switch to run tests live against a local Egeria instance
instead of using monkeypatching/unit fakes.

How to enable live tests:
- Use CLI option: pytest --live-egeria
- Or set env var: PYEG_LIVE_EGERIA=1

Live connection details (defaults when enabled):
- server_name = "qs-view-server"
- platform_url = "https://localhost:9443"
- user_id = "peterprofile"
- user_pwd = "secret"

You can override these via environment variables if needed:
- PYEG_SERVER_NAME, PYEG_PLATFORM_URL, PYEG_USER_ID, PYEG_USER_PWD

Notes:
- SSL verification is controlled by pyegeria._globals.enable_ssl_check, which is
  False by default in this repo to allow localhost self-signed certs.
"""
from __future__ import annotations

import os
import pytest

from pyegeria._client_new import Client2


LIVE_FLAG_ENV = "PYEG_LIVE_EGERIA"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("pyegeria")
    group.addoption(
        "--live-egeria",
        action="store_true",
        default=False,
        help="Run tests live against local Egeria at https://localhost:9443 instead of monkeypatching",
    )


def _env_truthy(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session")
def live_egeria_enabled(pytestconfig: pytest.Config) -> bool:
    via_cli = bool(pytestconfig.getoption("--live-egeria"))
    via_env = _env_truthy(LIVE_FLAG_ENV, False)
    return via_cli or via_env


@pytest.fixture(scope="session")
def live_client(live_egeria_enabled: bool) -> Client2:
    """Provide a real Client2 instance connected to local Egeria when enabled.

    Skips if live testing is not enabled.
    """
    if not live_egeria_enabled:
        pytest.skip("Live Egeria tests are disabled. Use --live-egeria or set PYEG_LIVE_EGERIA=1")

    server_name = os.getenv("PYEG_SERVER_NAME", "qs-view-server")
    platform_url = os.getenv("PYEG_PLATFORM_URL", "https://localhost:9443")
    user_id = os.getenv("PYEG_USER_ID", "peterprofile")
    user_pwd = os.getenv("PYEG_USER_PWD", "secret")

    # Construct the real client; BaseClient.check_connection() will verify connectivity
    client = Client2(
        server_name=server_name,
        platform_url=platform_url,
        user_id=user_id,
        user_pwd=user_pwd,
    )
    return client


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """When live mode is enabled, skip unit tests (marked as 'unit')."""
    live = bool(config.getoption("--live-egeria")) or _env_truthy(LIVE_FLAG_ENV, False)
    if not live:
        return

    skip_unit = pytest.mark.skip(reason="Skipped in live Egeria mode")
    for item in items:
        if any(mark.name == "unit" for mark in item.iter_markers()):
            item.add_marker(skip_unit)
