"""user_pwd=NO_PASSWORD opts out of the configured default password (owner ruling 2026-11-14, "Opt-out in 6.x").

Every client fills a missing password (None) from settings.User_Profile.user_pwd, and CLIs rely on that, so None
keeps its meaning. A token-only client (the Portal, Studio or EA acting for a signed-in user) passes NO_PASSWORD:
no password on the client, on any sub-client EgeriaTech builds, or on pyegeria's helper clients, so an expired
token fails as a 401 instead of the one auto-retry signing in again with the demo password.
"""
import json

import httpx
import pytest

import pyegeria.core._base_platform_client as platform_module
import pyegeria.core._base_server_client as server_module
from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.core._no_password import NO_PASSWORD, carried_password, password_as_given, resolve_password
from pyegeria.core._exceptions import PyegeriaUnauthorizedException
from pyegeria.core.config import settings
from pyegeria.egeria_tech_client import EgeriaTech

pytestmark = pytest.mark.unit

PLATFORM = "https://localhost:9443"
VIEW_SERVER = "qs-view-server"
ENDPOINT = f"{PLATFORM}/servers/{VIEW_SERVER}/api/open-metadata/test"
DEMO_PWD = "demo-default-secret"


class FakeEgeria:
    """Mints a token for any user whose password is DEMO_PWD; only the latest token per user is accepted."""

    def __init__(self):
        self.mint_attempts = []   # (user, password) of every /api/token call
        self.valid = set()
        self.served_as = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/token"):
            body = json.loads(request.content)
            self.mint_attempts.append((body["userId"], body.get("password")))
            if body.get("password") != DEMO_PWD:
                return httpx.Response(401, text="Unauthorized")
            token = f"{body['userId']}-{len(self.mint_attempts)}"
            self.valid = {t for t in self.valid if not t.startswith(f"{body['userId']}-")} | {token}
            return httpx.Response(200, text=token)
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if token not in self.valid:
            return httpx.Response(401, text="Unauthorized")
        self.served_as.append(token.rsplit("-", 1)[0])
        return httpx.Response(200, json={"class": "VoidResponse", "relatedHTTPCode": 200})


@pytest.fixture
def demo_default(monkeypatch):
    """A demo password configured as the settings default, as on a quickstart host."""
    monkeypatch.setattr(settings.User_Profile, "user_pwd", DEMO_PWD)
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
    monkeypatch.setattr(BasePlatformClient, "check_connection", lambda self: "test")
    return DEMO_PWD


@pytest.fixture
def egeria(monkeypatch, demo_default):
    fake = FakeEgeria()
    real_client = httpx.AsyncClient

    def client(*args, **kwargs):
        kwargs.pop("verify", None)
        return real_client(transport=httpx.MockTransport(fake.handler))

    monkeypatch.setattr(platform_module, "AsyncClient", client)
    monkeypatch.setattr(server_module, "AsyncClient", client)
    return fake


def test_resolve_password(demo_default):
    assert resolve_password(NO_PASSWORD) == (None, False)
    assert resolve_password(None) == (DEMO_PWD, True)        # 6.x: None takes the configured password
    assert resolve_password("given") == ("given", True)
    assert password_as_given(NO_PASSWORD) is None and password_as_given("x") == "x"
    assert not NO_PASSWORD and repr(NO_PASSWORD) == "NO_PASSWORD"
    import copy, pickle
    assert copy.deepcopy(NO_PASSWORD) is NO_PASSWORD and pickle.loads(pickle.dumps(NO_PASSWORD)) is NO_PASSWORD


_MAP_NAMES = None


def _names():
    global _MAP_NAMES
    if _MAP_NAMES is None:
        import pyegeria.core._base_server_client as bsc
        real = bsc.BaseServerClient.check_connection
        bsc.BaseServerClient.check_connection = lambda self: "test"
        try:
            _MAP_NAMES = sorted(EgeriaTech(VIEW_SERVER, PLATFORM, "peterprofile", "x", "tok")._subclient_map)
        finally:
            bsc.BaseServerClient.check_connection = real
    return _MAP_NAMES


def test_the_opt_out_reaches_egeria_tech_and_every_sub_client(demo_default):
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD, token="peter-token")
    assert tech.user_pwd is None and tech.use_default_password is False
    for name in _names():
        sub = tech._get_subclient(name)
        assert sub.user_pwd is None, name
        assert sub.use_default_password is False, name
        assert carried_password(sub) is NO_PASSWORD, name


def test_none_keeps_its_6x_meaning_on_egeria_tech_and_every_sub_client(demo_default):
    """CLIs pass args.password (None when the flag is omitted) and rely on the configured password."""
    for tech in (EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=None),
                 EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile")):
        assert tech.user_pwd == DEMO_PWD and tech.use_default_password is True
        for name in _names():
            assert tech._get_subclient(name).user_pwd == DEMO_PWD, name


def test_a_given_password_is_kept(demo_default):
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd="peters-own")
    assert tech.user_pwd == "peters-own"
    assert tech._get_subclient("collections").user_pwd == "peters-own"


@pytest.mark.parametrize("name", _names())
def test_every_client_class_constructed_directly_honours_the_opt_out(demo_default, name):
    cls = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd="x", token="tok")._subclient_map[name]
    for client in (cls(VIEW_SERVER, PLATFORM, "peterprofile", NO_PASSWORD, "tok"),
                   cls(VIEW_SERVER, PLATFORM, "peterprofile", user_pwd=NO_PASSWORD, token="tok")):
        assert client.user_pwd is None and client.use_default_password is False


def test_base_clients_honour_the_opt_out(demo_default):
    for cls in (BaseServerClient, BasePlatformClient):
        c = cls(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD)
        assert c.user_pwd is None and c.use_default_password is False
        assert cls(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=None).user_pwd == DEMO_PWD


def test_egeria_client_and_config_carry_the_opt_out(demo_default):
    from pyegeria.egeria_client import Egeria
    eg = Egeria(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD, token="tok")
    assert eg.user_pwd is None
    name = next(iter(eg._subclient_map))
    assert eg._get_subclient(name).user_pwd is None


def test_helper_clients_carry_the_opt_out(demo_default):
    """pyegeria's own helper clients (the spec cache's CollectionManager, the executor's fallback client) act
    for the caller: an opted-out caller's helper holds no password either."""
    from pyegeria.omvs.collection_manager import CollectionManager
    from pyegeria.view import egeria_spec_cache as esc
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD, token="tok")
    helper = esc._collection_client(tech, CollectionManager)
    assert helper.user_pwd is None and helper.use_default_password is False
    plain = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile")
    assert esc._collection_client(plain, CollectionManager).user_pwd == DEMO_PWD


async def test_an_expired_token_with_the_opt_out_fails_as_401_not_a_sign_in(egeria):
    """The token was minted here for peterprofile with a password given once; the client opted out of the default.
    When the token expires the request fails as a 401: no re-mint, and never with the configured demo password."""
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD)
    await tech._async_create_egeria_bearer_token("peterprofile", DEMO_PWD)
    sub = tech._get_subclient("glossary_manager")
    egeria.valid.clear()   # the token expires
    egeria.mint_attempts.clear()
    with pytest.raises(PyegeriaUnauthorizedException):
        await sub._async_make_request("POST", ENDPOINT, {})
    assert egeria.mint_attempts == []
    assert egeria.served_as == []


async def test_control_an_expired_token_with_none_still_renews_with_the_default(egeria):
    """Control (6.x, unchanged): None takes the configured password, and the one auto-retry renews with it."""
    tech = EgeriaTech(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=None)
    await tech._async_create_egeria_bearer_token()
    egeria.valid.clear()
    await tech._get_subclient("glossary_manager")._async_make_request("POST", ENDPOINT, {})
    assert egeria.served_as == ["peterprofile"]
    assert egeria.mint_attempts[-1] == ("peterprofile", DEMO_PWD)
