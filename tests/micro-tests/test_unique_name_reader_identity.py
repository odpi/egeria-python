"""READBACK U1 (Architect, 2026-11-15): the ClassificationExplorer that ``unique_name._reader`` builds for a
caller with no unique-name read of its own must be the caller exactly: their token and NO password (never the
settings default, which a 401 auto-retry could re-sign with), or a password the caller itself holds; with
neither, or on a fake/non-client, "unknown" with no client built and no call to Egeria; and the explorer is
closed. Hermetic: the settings default password is set to a canary, and EGERIA_* identity vars are cleared."""
import asyncio

import pytest

from pyegeria.core import unique_name as un
from pyegeria.core.config import settings

pytestmark = pytest.mark.unit

CANARY = "settings-default-password-canary"


@pytest.fixture(autouse=True)
def _hermetic(monkeypatch):
    for var in ("EGERIA_USER", "EGERIA_USER_PASSWORD", "EGERIA_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_pwd", CANARY)


@pytest.fixture
def no_network(monkeypatch):
    """Any real HTTP request fails the test."""
    import httpx

    def _refuse(*a, **kw):
        raise AssertionError("a network call was made")

    monkeypatch.setattr(httpx.AsyncClient, "send", _refuse)
    monkeypatch.setattr(httpx.Client, "send", _refuse)


@pytest.fixture
def explorers(monkeypatch):
    """Record each real ClassificationExplorer built, its read stubbed, its close counted."""
    from pyegeria.omvs.classification_explorer import ClassificationExplorer
    built = []

    def _read(self, qn, *_, **__):
        self.seen = (self.user_pwd, self.headers.get("Authorization"))
        return {"elementHeader": {"guid": "e", "type": {"typeName": "Collection"}}}

    async def _aread(self, qn, *_, **__):
        return _read(self, qn)

    async def _aclose(self):
        self.closed = getattr(self, "closed", 0) + 1

    def _close(self):
        self.closed = getattr(self, "closed", 0) + 1

    real_init = ClassificationExplorer.__init__

    def _init(self, *a, **kw):
        real_init(self, *a, **kw)
        built.append(self)

    monkeypatch.setattr(ClassificationExplorer, "__init__", _init)
    monkeypatch.setattr(ClassificationExplorer, "get_element_by_unique_name", _read)
    monkeypatch.setattr(ClassificationExplorer, "_async_get_element_by_unique_name", _aread)
    monkeypatch.setattr(ClassificationExplorer, "close_session", _close)
    monkeypatch.setattr(ClassificationExplorer, "_async_close_session", _aclose)
    return built


class _Caller:
    """A client with no unique-name read of its own (like CollectionManager)."""

    def __init__(self, token=None, user_pwd=None, user_id="peterprofile",
                 view_server="qs-view-server", platform_url="https://laz:9443"):
        self.view_server, self.platform_url, self.user_id, self.user_pwd = view_server, platform_url, user_id, user_pwd
        self._token = token

    def get_token(self):
        if self._token is None:
            raise KeyError("Authorization")
        return f"Bearer {self._token}"


def test_a_scrubbed_caller_with_a_token_shares_the_token_and_no_password(explorers, no_network):
    found = un.by_unique_name(_Caller(token="tok-peter", user_pwd=None), "Q")
    assert found.guid == "e"
    (ex,) = explorers
    assert ex.seen == (None, "Bearer tok-peter")        # no settings default; the bare token, not "Bearer Bearer"
    assert ex.user_pwd is None and CANARY not in repr(vars(ex))
    assert ex.closed == 1


def test_a_caller_with_a_token_and_a_password_still_sends_no_password(explorers, no_network):
    un.by_unique_name(_Caller(token="tok", user_pwd="peters-own"), "Q")
    assert explorers[0].user_pwd is None


def test_no_token_uses_only_the_callers_own_password(explorers, no_network):
    un.by_unique_name(_Caller(token=None, user_pwd="peters-own"), "Q")
    (ex,) = explorers
    assert ex.user_pwd == "peters-own" and ex.user_id == "peterprofile" and ex.closed == 1


@pytest.mark.parametrize("caller", [
    _Caller(token=None, user_pwd=None),                       # scrubbed, no token
    _Caller(token=None, user_pwd=""),
    _Caller(token=None, user_pwd="x", user_id=None),          # a password with no user of its own
])
def test_neither_token_nor_own_password_is_unknown_with_no_client_built(caller, explorers, no_network):
    found = un.by_unique_name(caller, "Q")
    assert found.answer == "unknown" and "neither a token nor its own password" in found.reason
    assert explorers == []
    assert asyncio.run(un.async_by_unique_name(caller, "Q")).answer == "unknown" and explorers == []


@pytest.mark.parametrize("caller", [
    object(),                                                  # a non-client
    _Caller(token="tok", view_server=None),
    _Caller(token="tok", platform_url=None),
    _Caller(token="tok", view_server=b"qs"),                   # not a string
    _Caller(token="tok", platform_url="  "),
])
def test_a_fake_or_non_client_is_unknown_with_no_client_and_no_network(caller, explorers, no_network):
    found = un.by_unique_name(caller, "Q")
    assert found.answer == "unknown" and "isn't a client on an Egeria platform" in found.reason
    assert explorers == []
    assert asyncio.run(un.async_by_unique_name(caller, "Q")).answer == "unknown"


def test_a_magicmock_without_real_strings_builds_nothing(explorers, no_network):
    from unittest.mock import MagicMock
    assert un.by_unique_name(MagicMock(spec=["view_server", "platform_url", "get_token"]), "Q").answer == "unknown"
    assert explorers == []


def test_the_explorer_is_closed_after_a_failed_read_too(explorers, monkeypatch, no_network):
    from pyegeria.omvs.classification_explorer import ClassificationExplorer

    def _boom(self, *a, **kw):
        raise TimeoutError("slow")

    monkeypatch.setattr(ClassificationExplorer, "get_element_by_unique_name", _boom)
    found = un.by_unique_name(_Caller(token="tok"), "Q")
    assert found.answer == "unknown" and explorers[0].closed == 1


def test_async_shares_the_token_without_a_password_and_closes(explorers, no_network):
    found = asyncio.run(un.async_by_unique_name(_Caller(token="tok-a"), "Q"))
    assert found.guid == "e"
    (ex,) = explorers
    assert ex.seen == (None, "Bearer tok-a") and ex.closed == 1


def test_a_caller_with_its_own_read_builds_nothing(explorers):
    class Own:
        def get_element_by_unique_name(self, qn):
            return "No elements found"

    assert un.by_unique_name(Own(), "Q").answer == "absent" and explorers == []
