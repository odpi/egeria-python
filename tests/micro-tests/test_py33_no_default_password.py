"""
PY-33: pyegeria has no built-in default password.

`resolve_egeria_credentials` used to end `... or "secret"`, so a process with no password configured
signed in with a guessed one (the EA service-account 401 on 2026-11-17, TR-34, was exactly that). Now:
- with nothing configured, the resolved password is None;
- signing in with no password refuses in words, before any request is sent;
- a caller-given or configured password is used as before.
No live server: every HTTP send is refused and recorded. Building a sub-client may read the platform's
/api/about (best effort); the claim tested is that no sign-in request (/api/token) is sent without a password.
"""
import asyncio

import httpx
import pytest

from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core._no_password import NO_PASSWORD
from pyegeria.core.config import resolve_egeria_credentials, settings
from pyegeria.egeria_tech_client import EgeriaTech

URL = "https://127.0.0.1:9"   # never reached: every send is refused below


@pytest.fixture
def no_password_configured(monkeypatch):
    monkeypatch.delenv("EGERIA_USER_PASSWORD", raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_pwd", None, raising=False)


@pytest.fixture
def no_network(monkeypatch):
    sent = []

    async def refuse(self, request, *args, **kwargs):
        sent.append(str(request.url))
        raise AssertionError(f"no request may be sent: {request.url}")

    monkeypatch.setattr(httpx.AsyncClient, "send", refuse)
    return sent


def _token_requests(sent):
    return [u for u in sent if u.endswith("/api/token")]


def test_resolve_has_no_default_password(no_password_configured):
    user, pwd = resolve_egeria_credentials("someone")
    assert user == "someone"
    assert pwd is None   # not "secret"


def test_resolve_keeps_a_given_or_configured_password(no_password_configured, monkeypatch):
    assert resolve_egeria_credentials("someone", "given")[1] == "given"
    monkeypatch.setenv("EGERIA_USER_PASSWORD", "from-env")
    assert resolve_egeria_credentials("someone")[1] == "from-env"


@pytest.mark.parametrize("pwd", [None, "", NO_PASSWORD])
def test_sign_in_without_a_password_refuses_in_words(no_password_configured, no_network, pwd):
    client = EgeriaTech("qs-view-server", URL, user_id="someone", user_pwd=pwd)
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        client.create_egeria_bearer_token()
    text = str(info.value)
    assert "No password to sign in to Egeria as 'someone'" in text
    assert "no default" in text
    assert not _token_requests(no_network)   # refused before any sign-in request


def test_async_sign_in_without_a_password_refuses_in_words(no_password_configured, no_network):
    client = EgeriaTech("qs-view-server", URL, user_id="someone", user_pwd=NO_PASSWORD)
    with pytest.raises(PyegeriaInvalidParameterException):
        asyncio.run(client._async_create_egeria_bearer_token())
    assert not _token_requests(no_network)


def test_sign_in_with_a_password_still_sends_the_request(no_password_configured, no_network):
    client = EgeriaTech("qs-view-server", URL, user_id="someone", user_pwd="given")
    with pytest.raises(Exception) as info:   # reaches the (refused) network: the password was accepted
        client.create_egeria_bearer_token()
    assert not isinstance(info.value, PyegeriaInvalidParameterException) or "No password" not in str(info.value)
    assert _token_requests(no_network), "a password-holding client should have tried to sign in"
