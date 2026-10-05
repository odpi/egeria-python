"""
ISSUE-126: ProductManager and DigitalBusiness called ServerClient.__init__ instead of
CollectionManager.__init__, so collection_command_root (used by 27 inherited methods) was never set.
ISSUE-127: delete_collection / delete_digital_product pre-filled a body dict, so the shared helper
silently ignored cascade=True.
"""
import ast
import glob
import json
import os

import pytest

from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.omvs.product_manager import ProductManager

OMVS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "pyegeria", "omvs")


def test_every_omvs_subclass_runs_its_base_constructor():
    """Structural guard for the whole bug class: a client that derives from another OMVS client but whose
    __init__ never calls that client's __init__ silently misses the attributes it sets."""
    classes = {}
    for path in sorted(glob.glob(os.path.join(OMVS_DIR, "*.py"))):
        for node in ast.parse(open(path).read()).body:
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            init = next((m for m in node.body if isinstance(m, ast.FunctionDef) and m.name == "__init__"), None)
            called = set()
            if init:
                for call in ast.walk(init):
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "__init__":
                        owner = call.func.value
                        called.add(owner.id if isinstance(owner, ast.Name) else "super()")
            classes[node.name] = (bases, init is not None, called)

    offenders = [f"{name} (skips {base}.__init__)"
                 for name, (bases, has_init, called) in classes.items() if has_init
                 for base in bases
                 if base in classes and base != "ServerClient" and base not in called and "super()" not in called]
    assert offenders == []


@pytest.mark.parametrize("cls", [CollectionManager, GlossaryManager, ProductManager, DigitalBusiness])
def test_collection_manager_subclasses_have_the_collection_roots(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    assert client.collection_command_root.endswith("/api/open-metadata/collection-manager/collections")
    assert client.metadata_expert_command_root.endswith("/api/open-metadata/metadata-expert")


def test_each_subclass_keeps_its_own_root(monkeypatch):
    monkeypatch.setattr(ProductManager, "check_connection", lambda self: "test")
    monkeypatch.setattr(DigitalBusiness, "check_connection", lambda self: "test")

    assert ProductManager("v", "https://localhost:1", "u", "p").product_manager_command_root.endswith("/product-manager")
    assert DigitalBusiness("v", "https://localhost:1", "u", "p").digital_business_command_root.endswith("/digital-business")


# --- ISSUE-127 ------------------------------------------------------------------------------

class _Response:
    def json(self):
        return {"relatedHTTPCode": 200}


def _capture(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method, tail", [
    (CollectionManager, "_async_delete_collection", "/collections/g1/delete"),
    (ProductManager, "_async_delete_collection", "/collections/g1/delete"),   # inherited; was broken by ISSUE-126
    (DigitalBusiness, "_async_delete_collection", "/collections/g1/delete"),  # likewise
    (ProductManager, "_async_delete_digital_product", "/collections/g1/delete"),
])
async def test_cascade_true_reaches_the_server(cls, method, tail, monkeypatch):
    client, calls = _capture(cls, monkeypatch)

    await getattr(client, method)("g1", cascade=True)

    assert calls[0]["url"].endswith(tail)
    assert calls[0]["body"]["cascadeDelete"] is True
    assert calls[0]["body"]["class"] == "DeleteElementRequestBody"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["_async_delete_collection", "_async_delete_digital_product"])
async def test_cascade_default_does_not_cascade(method, monkeypatch):
    client, calls = _capture(ProductManager, monkeypatch)

    await getattr(client, method)("g1")

    assert calls[0]["body"].get("cascadeDelete") in (None, False)


@pytest.mark.asyncio
async def test_an_explicit_body_is_still_honoured(monkeypatch):
    client, calls = _capture(CollectionManager, monkeypatch)
    body = {"class": "DeleteElementRequestBody", "cascadeDelete": True, "deleteMethod": "PURGE"}

    await client._async_delete_collection("g1", body=body)

    assert calls[0]["body"]["cascadeDelete"] is True and calls[0]["body"]["deleteMethod"] == "PURGE"
