"""C3: every client pyegeria builds to act for another goes through `pyegeria.core._helper_client.helper_client`.

The Architect's probe: a parent built with NO_PASSWORD whose token arrives through set_bearer_token (which writes
only the Authorization headers, never `self.token`). Each helper used to copy `self.user_pwd` raw and
`token=self.token`, so it had NO token and the configured default password: it signed in again as the demo
user. Now each helper gets the parent's bare token once and no password. Hermetic: EGERIA_USER* cleared, the
settings default password set to a canary.
"""
import ast
import json
import pathlib

import httpx
import pytest

import pyegeria
import pyegeria.core._base_platform_client as platform_module
import pyegeria.core._base_server_client as server_module
from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.core._exceptions import PyegeriaUnauthorizedException
from pyegeria.core._helper_client import bare_token, helper_client
from pyegeria.core._no_password import NO_PASSWORD
from pyegeria.core.config import settings

pytestmark = pytest.mark.unit

PLATFORM = "https://localhost:9443"
VIEW_SERVER = "qs-view-server"
CANARY = "settings-default-password-canary"


@pytest.fixture(autouse=True)
def _hermetic(monkeypatch):
    for var in ("EGERIA_USER", "EGERIA_USER_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_pwd", CANARY)
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
    monkeypatch.setattr(BasePlatformClient, "check_connection", lambda self: "test")


def _parent(cls, *, password=NO_PASSWORD, token="peter-token"):
    parent = cls(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=password)
    if token:
        parent.set_bearer_token(token)   # the headers only: parent.token stays None
    return parent


def _cls_explorer_collection(parent):
    return parent._collection_client()


def _ac_governance_engine(parent):
    return parent._governance_engine_client()


def _dd_asset_maker(parent):
    return parent._asset_maker_client()


def _spec_cache(parent):
    from pyegeria.omvs.collection_manager import CollectionManager
    from pyegeria.view import egeria_spec_cache as esc
    return esc._collection_client(parent, CollectionManager)


def _executor_fallback(parent):
    from pyegeria.omvs.governance_engine import GovernanceEngine
    from pyegeria.view.format_set_executor import _resolve_action_target_client
    return _resolve_action_target_client(parent, GovernanceEngine)


def _unique_name_reader(parent):
    from pyegeria.core import unique_name as un
    return un._reader(parent, "get_element_by_unique_name").explorer


def _tech_sub_client(parent):
    return parent._get_subclient("collections")


def _parent_class(name):
    from pyegeria.egeria_tech_client import EgeriaTech
    from pyegeria.omvs.automated_curation import AutomatedCuration
    from pyegeria.omvs.classification_explorer import ClassificationExplorer
    from pyegeria.omvs.collection_manager import CollectionManager
    from pyegeria.omvs.data_discovery import DataDiscovery
    return {"ClassificationExplorer": ClassificationExplorer, "AutomatedCuration": AutomatedCuration,
            "DataDiscovery": DataDiscovery, "CollectionManager": CollectionManager,
            "EgeriaTech": EgeriaTech}[name]


HELPERS = [
    ("ClassificationExplorer", _cls_explorer_collection),
    ("AutomatedCuration", _ac_governance_engine),
    ("DataDiscovery", _dd_asset_maker),
    ("CollectionManager", _spec_cache),
    ("CollectionManager", _executor_fallback),
    ("CollectionManager", _unique_name_reader),
    ("EgeriaTech", _tech_sub_client),
    ("EgeriaTech", _spec_cache),
]
IDS = [f"{p}-{h.__name__.lstrip('_')}" for p, h in HELPERS]


@pytest.mark.parametrize("parent_name,helper", HELPERS, ids=IDS)
def test_the_probe_a_no_password_parent_given_its_token_later(parent_name, helper):
    """NO_PASSWORD, then set_bearer_token: the helper holds the token (once prefixed) and no password."""
    parent = _parent(_parent_class(parent_name))
    child = helper(parent)
    assert child is not None
    assert child.user_pwd is None and child.use_default_password is False
    assert child.headers["Authorization"] == "Bearer peter-token"
    assert child.user_id == "peterprofile"


@pytest.mark.parametrize("parent_name,helper", HELPERS, ids=IDS)
def test_a_scrubbed_parent_given_its_token_later(parent_name, helper):
    """The Portal / Studio / EA shape: built with None (the default filled it), password cleared, token set."""
    parent = _parent(_parent_class(parent_name), password=None)
    parent.user_pwd = None
    child = helper(parent)
    assert child.user_pwd is None
    assert child.headers["Authorization"] == "Bearer peter-token"


@pytest.mark.parametrize("stored", ["peter-token", "Bearer peter-token", "Bearer Bearer peter-token"])
def test_bearer_bearer_never(stored):
    from pyegeria.omvs.collection_manager import CollectionManager
    parent = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD)
    parent.headers["Authorization"] = parent.text_headers["Authorization"] = f"Bearer {stored}"
    assert bare_token(parent) == "peter-token"
    child = helper_client(CollectionManager, parent)
    assert child.headers["Authorization"] == "Bearer peter-token"
    assert child.text_headers["Authorization"] == "Bearer peter-token"


def test_a_token_attribute_alone_is_used_once_prefixed():
    class Bare:
        view_server, platform_url, user_id, user_pwd, token = VIEW_SERVER, PLATFORM, "peterprofile", None, "Bearer t"
    from pyegeria.omvs.collection_manager import CollectionManager
    assert helper_client(CollectionManager, Bare()).headers["Authorization"] == "Bearer t"


def test_a_self_minted_token_is_renewed_by_the_helper_as_by_the_parent():
    """A CLI parent that minted its own token keeps its own password and its renewal on the helper."""
    from pyegeria.omvs.collection_manager import CollectionManager
    parent = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd="peters-own")
    parent.headers["Authorization"] = parent.text_headers["Authorization"] = "Bearer minted"
    parent._token_minted_for = "peterprofile"
    child = helper_client(CollectionManager, parent)
    assert child.user_pwd == "peters-own" and child._token_minted_for == "peterprofile"
    other = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd="peters-own")
    other.set_bearer_token("supplied")                     # not minted here: never renewed, so no password
    child = helper_client(CollectionManager, other)
    assert child.user_pwd is None and child._token_minted_for is None


def test_no_token_carries_only_the_parents_own_password():
    from pyegeria.omvs.collection_manager import CollectionManager
    own = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd="peters-own")
    assert helper_client(CollectionManager, own).user_pwd == "peters-own"
    cli = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile")   # 6.x: the configured password
    assert helper_client(CollectionManager, cli).user_pwd == CANARY
    opted = CollectionManager(VIEW_SERVER, PLATFORM, user_id="peterprofile", user_pwd=NO_PASSWORD)
    assert helper_client(CollectionManager, opted).user_pwd is None


def test_egeria_config_builds_a_sub_client_without_recursing():
    from pyegeria.egeria_config_client import EgeriaConfig
    cfg = EgeriaConfig(VIEW_SERVER, PLATFORM, user_id="garygeeke", user_pwd=NO_PASSWORD)
    sub = cfg._get_subclient(next(iter(cfg._subclient_map)))
    assert sub.user_pwd is None


class _FakeEgeria:
    def __init__(self):
        self.mints, self.valid = [], set()

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/token"):
            body = json.loads(request.content)
            self.mints.append((body["userId"], body.get("password")))
            return httpx.Response(200, text=f"{body['userId']}-minted")
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if token not in self.valid:
            return httpx.Response(401, text="Unauthorized")
        return httpx.Response(200, json={"class": "VoidResponse", "relatedHTTPCode": 200})


@pytest.mark.parametrize("parent_name,helper", HELPERS[:3] + HELPERS[6:7], ids=IDS[:3] + IDS[6:7])
async def test_the_probe_s_expired_token_fails_as_401_not_a_sign_in(monkeypatch, parent_name, helper):
    fake = _FakeEgeria()
    real_client = httpx.AsyncClient

    def client(*args, **kwargs):
        kwargs.pop("verify", None)
        return real_client(transport=httpx.MockTransport(fake.handler))

    monkeypatch.setattr(platform_module, "AsyncClient", client)
    monkeypatch.setattr(server_module, "AsyncClient", client)
    child = helper(_parent(_parent_class(parent_name)))     # "peter-token" is not valid: expired
    with pytest.raises(PyegeriaUnauthorizedException):
        await child._async_make_request("POST", f"{PLATFORM}/servers/{VIEW_SERVER}/api/open-metadata/x", {})
    assert fake.mints == []                                  # never signed in again, least of all as the canary


# ── The sweep: no client is built from another client's user_pwd / token outside helper_client ──

def _credential_arg(node):
    if isinstance(node, ast.Attribute) and node.attr in ("user_pwd", "token"):
        return True
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr"
            and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in ("user_pwd", "token"))


def _constructor(func):
    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
    return name[:1].isupper() or name in ("cls", "client_cls", "client_class", "sub_cls")


def test_no_client_is_built_from_another_clients_password_or_token_outside_helper_client():
    root = pathlib.Path(pyegeria.__file__).parent
    offenders = []
    for path in sorted(root.rglob("*.py")):
        if path.name == "_helper_client.py":
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _constructor(node.func):
                if any(_credential_arg(v) for v in [*node.args, *(k.value for k in node.keywords)]):
                    offenders.append(f"{path.relative_to(root)}:{node.lineno}")
    assert offenders == [], "build these with pyegeria.core._helper_client.helper_client: " + ", ".join(offenders)
