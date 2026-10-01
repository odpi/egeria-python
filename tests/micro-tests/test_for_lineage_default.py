"""
forLineage defaults for Dr.Egeria (see lineage_visible in
pyegeria/core/_base_platform_client.py and AsyncBaseCommandProcessor.
effective_for_lineage):

- inside lineage_visible(), every JSON request body is sent with
  forLineage=true -- including bodies SDK helpers build with it false;
- editing commands default to forLineage=true so Promise-classified elements
  stay visible; report commands (View/List/Run) default to false; an explicit
  "For Lineage" value always wins;
- a Memento (logically deleted) element found that way is treated as absent.
"""
import json

import pytest

from pyegeria import lineage_visible
from pyegeria.core._base_platform_client import _apply_for_lineage_default
from pyegeria.omvs.asset_catalog import AssetCatalog

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


# ---------------------------------------------------------------- request layer

def test_bodies_untouched_outside_lineage_visible():
    body = {"class": "GetRequestBody", "forLineage": False}
    assert _apply_for_lineage_default(body) is body


@pytest.mark.parametrize("body", [
    {"class": "GetRequestBody", "forLineage": False},        # SDK helper default
    {"class": "UpdateElementRequestBody"},                   # request body without the field
    {"class": "FindPropertyNameProperties", "forLineage": False},  # name lookup body
])
def test_request_bodies_get_for_lineage_true(body):
    with lineage_visible():
        assert _apply_for_lineage_default(body)["forLineage"] is True
        assert json.loads(_apply_for_lineage_default(json.dumps(body)))["forLineage"] is True


@pytest.mark.parametrize("payload", [{"class": "SomeProperties", "name": "x"}, {"name": "x"}, "not json"])
def test_other_payloads_unchanged(payload):
    with lineage_visible():
        assert _apply_for_lineage_default(payload) == payload


def test_lineage_visible_false_leaves_bodies_alone():
    with lineage_visible(False):
        body = {"class": "GetRequestBody", "forLineage": False}
        assert _apply_for_lineage_default(body) is body


class _Response:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {"class": "VoidResponse", "relatedHTTPCode": 200}


class _Session:
    def __init__(self):
        self.sent = []

    async def post(self, endpoint, **kwargs):
        payload = kwargs.get("json", kwargs.get("content"))
        self.sent.append(json.loads(payload) if isinstance(payload, str) else payload)
        return _Response()


@pytest.mark.asyncio
async def test_post_path_applies_default(monkeypatch):
    # No live server: skip the constructor's connection check, and use a port
    # nothing listens on so any real network call would fail loudly.
    monkeypatch.setattr(AssetCatalog, "check_connection", lambda self: "test")
    session = _Session()
    client = AssetCatalog("view-server", "https://localhost:1", "user", "pwd")
    client.session = session

    await client._async_make_request("POST", "https://x/y", '{"class": "GetRequestBody", "forLineage": false}')
    with lineage_visible():
        await client._async_make_request("POST", "https://x/y", '{"class": "GetRequestBody", "forLineage": false}')

    assert [b["forLineage"] for b in session.sent] == [False, True]


# ---------------------------------------------------------------- Dr.Egeria defaults

class _Processor(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        return ""


def _processor(verb: str, object_type: str, attributes: dict) -> _Processor:
    return _Processor(object(), DrECommand(verb=verb, object_type=object_type, attributes=attributes,
                                           raw_block=f"## {verb} {object_type}\n"))


@pytest.mark.parametrize("verb, object_type, attributes, expected", [
    ("Update", "Solution Component", {}, True),              # editing: default true
    ("Create", "Solution Component", {}, True),
    ("Link", "Solution Components", {}, True),
    ("View", "Report", {}, False),                          # reports: default false
    ("Update", "Solution Component", {"For Lineage": "false"}, False),  # explicit wins
    ("View", "Report", {"For Lineage": "true"}, True),
    ("Update", "Solution Component", {"For Lineage": ""}, True),        # blank = not set
])
def test_effective_for_lineage(verb, object_type, attributes, expected):
    assert _processor(verb, object_type, attributes).effective_for_lineage() is expected


def test_memento_element_treated_as_absent():
    memento = {"elementHeader": {"guid": "g1", "memento": {"typeName": "Memento"}}}
    promise = {"elementHeader": {"guid": "g2", "promise": {"typeName": "Promise"}}}
    assert AsyncBaseCommandProcessor._ignore_memento(memento) is None
    assert AsyncBaseCommandProcessor._ignore_memento(promise) is promise
    assert AsyncBaseCommandProcessor._ignore_memento(None) is None
