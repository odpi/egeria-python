"""
The 401 auto-retry in BaseServerClient._async_make_request re-mints a token as the client's own
user_id. It must only do that for a token the client minted for that user (or when it has no
token). A token supplied by the caller via set_bearer_token may belong to another user: re-minting
over it silently ran the request as the client's user (a portal session logged in as one user ran
Lineage Explorer queries as erinoverview).
"""
import json

import httpx
import pytest

import pyegeria.core._base_platform_client as platform_module
import pyegeria.core._base_server_client as server_module
from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.core._exceptions import PyegeriaUnauthorizedException
from pyegeria.egeria_tech_client import EgeriaTech

PLATFORM = "https://localhost:9443"
VIEW_SERVER = "qs-view-server"
ENDPOINT = f"{PLATFORM}/servers/{VIEW_SERVER}/api/open-metadata/test"


class FakeEgeria:
    """Mints numbered tokens per user; only the latest token per user is accepted."""

    def __init__(self):
        self.minted = []          # user ids, in mint order
        self.valid = set()
        self.served_as = []       # user id behind each accepted data request

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/token"):
            user = json.loads(request.content)["userId"]
            self.minted.append(user)
            token = f"{user}-{len(self.minted)}"
            self.valid = {t for t in self.valid if not t.startswith(f"{user}-")} | {token}
            return httpx.Response(200, text=token)
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if token not in self.valid:
            return httpx.Response(401, text="Unauthorized")
        self.served_as.append(token.rsplit("-", 1)[0])
        return httpx.Response(200, json={"class": "VoidResponse", "relatedHTTPCode": 200})


@pytest.fixture
def egeria(monkeypatch):
    fake = FakeEgeria()
    # The constructors check the connection; that is not under test here.
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
    monkeypatch.setattr(BasePlatformClient, "check_connection", lambda self: "test")
    real_client = httpx.AsyncClient

    def client(*args, **kwargs):
        kwargs.pop("verify", None)
        return real_client(transport=httpx.MockTransport(fake.handler))

    monkeypatch.setattr(platform_module, "AsyncClient", client)
    monkeypatch.setattr(server_module, "AsyncClient", client)
    return fake


def _client():
    return BaseServerClient(VIEW_SERVER, PLATFORM, user_id="erinoverview", user_pwd="secret")


async def test_external_token_is_not_replaced(egeria):
    client = _client()
    client.set_bearer_token("peterprofile-expired")
    with pytest.raises(PyegeriaUnauthorizedException):
        await client._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == []
    assert egeria.served_as == []


async def test_own_expired_token_is_renewed(egeria):
    client = _client()
    await client._async_create_egeria_bearer_token()
    egeria.valid.clear()  # the token expires
    await client._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == ["erinoverview", "erinoverview"]
    assert egeria.served_as == ["erinoverview"]


async def test_no_token_mints_one(egeria):
    client = _client()
    await client._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == ["erinoverview"]
    assert egeria.served_as == ["erinoverview"]


async def test_token_minted_for_another_user_is_not_replaced(egeria):
    client = _client()
    await client._async_create_egeria_bearer_token("peterprofile", "peters-password")
    egeria.valid.clear()
    with pytest.raises(PyegeriaUnauthorizedException):
        await client._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == ["peterprofile"]


async def test_set_bearer_token_after_minting_disables_retry(egeria):
    client = _client()
    await client._async_create_egeria_bearer_token()
    client.set_bearer_token("peterprofile-expired")
    with pytest.raises(PyegeriaUnauthorizedException):
        await client._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == ["erinoverview"]


async def test_egeria_tech_minted_token_renews_in_sub_clients(egeria):
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, "erinoverview", "secret")
    await tech._async_create_egeria_bearer_token()
    egeria.valid.clear()
    # A sub-client created after minting inherits the token and its owner.
    await tech._get_subclient("glossary_manager")._async_make_request("POST", ENDPOINT, {})
    assert egeria.served_as == ["erinoverview"]


async def test_egeria_tech_external_token_is_not_replaced(egeria):
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, "erinoverview", "secret")
    tech._get_subclient("collections")
    tech.set_bearer_token("peterprofile-expired")
    for name in ("collections", "glossary_manager"):  # existing and newly created sub-clients
        with pytest.raises(PyegeriaUnauthorizedException):
            await tech._get_subclient(name)._async_make_request("POST", ENDPOINT, {})
    assert egeria.minted == []
