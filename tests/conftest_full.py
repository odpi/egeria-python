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
from pyegeria.egeria_tech_client import EgeriaTech


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


@pytest.fixture(scope="session")
def live_egeria_tech_client(live_egeria_enabled: bool) -> EgeriaTech:
    """Provide a real EgeriaTech instance connected to local Egeria when enabled.

    Skips if live testing is not enabled.
    """
    if not live_egeria_enabled:
        pytest.skip("Live Egeria tests are disabled. Use --live-egeria or set PYEG_LIVE_EGERIA=1")

    server_name = os.getenv("PYEG_SERVER_NAME", "qs-view-server")
    platform_url = os.getenv("PYEG_PLATFORM_URL", "https://localhost:9443")
    user_id = os.getenv("PYEG_USER_ID", "peterprofile")
    user_pwd = os.getenv("PYEG_USER_PWD", "secret")

    # Construct the real EgeriaTech client
    client = EgeriaTech(
        view_server=server_name,
        platform_url=platform_url,
        user_id=user_id,
        user_pwd=user_pwd
    )
    
    # Create bearer token
    client.create_egeria_bearer_token(user_id, user_pwd)
    
    return client


@pytest.fixture
def mock_egeria_tech_client():
    """Provide a fully mocked EgeriaTech instance for unit testing."""
    from tests.fixtures.mock_responses import MockSubClientFactory
    
    class MockEgeriaTech:
        def __init__(self, view_server="test-server", platform_url="https://test.com", 
                     user_id="test_user", user_pwd="test_pass", token=None):
            self.view_server = view_server
            self.platform_url = platform_url
            self.user_id = user_id
            self.user_pwd = user_pwd
            self.token = token
            
            # Create mock sub-clients
            self._collection_manager = MockSubClientFactory.create_mock_collection_manager()(
                view_server=view_server, platform_url=platform_url, 
                user_id=user_id, user_pwd=user_pwd, token=token
            )
            self._external_references = MockSubClientFactory.create_mock_external_references()(
                view_server=view_server, platform_url=platform_url,
                user_id=user_id, user_pwd=user_pwd, token=token
            )
            self._glossary_manager = MockSubClientFactory.create_mock_glossary_manager()(
                view_server=view_server, platform_url=platform_url,
                user_id=user_id, user_pwd=user_pwd, token=token
            )
            self._governance_officer = MockSubClientFactory.create_mock_governance_officer()(
                view_server=view_server, platform_url=platform_url,
                user_id=user_id, user_pwd=user_pwd, token=token
            )
            self._metadata_explorer = MockSubClientFactory.create_mock_metadata_explorer()(
                view_server=view_server, platform_url=platform_url,
                user_id=user_id, user_pwd=user_pwd, token=token
            )
            
            self._subclients = [
                self._collection_manager,
                self._governance_officer, 
                self._metadata_explorer
            ]
        
        def create_egeria_bearer_token(self, user_id=None, user_pwd=None):
            token_val = None
            for sub in self._subclients:
                token_val = sub.create_egeria_bearer_token(user_id, user_pwd)
            self.token = token_val
            return token_val
        
        def set_bearer_token(self, token):
            for sub in self._subclients:
                sub.set_bearer_token(token)
            self.token = token
        
        def get_token(self):
            for sub in self._subclients:
                if hasattr(sub, "get_token"):
                    return sub.get_token()
            return self.token
        
        def close_session(self):
            for sub in self._subclients:
                if hasattr(sub, "close_session"):
                    try:
                        sub.close_session()
                    except Exception:
                        pass
        
        def __getattr__(self, name):
            for sub in self._subclients:
                if hasattr(sub, name):
                    return getattr(sub, name)
            raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")
    
    return MockEgeriaTech()


@pytest.fixture
def test_credentials():
    """Provide test credentials."""
    return {
        "user_id": "test_user",
        "user_pwd": "test_password", 
        "view_server": "test-view-server",
        "platform_url": "https://test-egeria.com:9443"
    }


@pytest.fixture
def test_params():
    """Provide standard test parameters."""
    return {
        "search_string": "*",
        "page_size": 10,
        "start_from": 0,
        "starts_with": True,
        "ends_with": False,
        "ignore_case": True
    }


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """When live mode is enabled, skip unit tests (marked as 'unit')."""
    live = bool(config.getoption("--live-egeria")) or _env_truthy(LIVE_FLAG_ENV, False)
    if not live:
        return

    skip_unit = pytest.mark.skip(reason="Skipped in live Egeria mode")
    for item in items:
        if any(mark.name == "unit" for mark in item.iter_markers()):
            item.add_marker(skip_unit)
