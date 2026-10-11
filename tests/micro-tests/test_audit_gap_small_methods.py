"""
Audit-gap methods added from the refreshed Egeria .http collections:
  asset-maker:       update_data_set_content, detach_data_set_content_relationship
  connection-maker:  link_resource_to_connection, detach_resource_from_connection
No live server: the HTTP call is captured and the verb, URL and body asserted.
"""
import json

import pytest

from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.connection_maker import ConnectionMaker


class _Response:
    def json(self):
        return {"class": "VoidResponse", "relatedHTTPCode": 200}


def _capture(client, calls: list):
    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


def _asset_maker(calls, monkeypatch):
    monkeypatch.setattr(AssetMaker, "check_connection", lambda self: "test")
    return _capture(AssetMaker("view-server", "https://localhost:1", "user", "pwd"), calls)


def _connection_maker(calls, monkeypatch):
    monkeypatch.setattr(ConnectionMaker, "check_connection", lambda self: "test")
    return _capture(ConnectionMaker("view-server", "https://localhost:1", "user", "pwd"), calls)


ASSET_ROOT = "/servers/view-server/api/open-metadata/asset-maker"
CONN_ROOT = "/servers/view-server/api/open-metadata/connection-maker"


@pytest.mark.asyncio
async def test_update_data_set_content_addresses_the_relationship_by_its_own_guid(monkeypatch):
    calls: list = []
    client = _asset_maker(calls, monkeypatch)
    props = {"class": "DataSetContentProperties", "queryId": "q1", "query": "select 1",
             "queryType": "SQL", "iscQualifiedName": "isc::one"}

    await client._async_update_data_set_content(
        "rel-guid", {"class": "UpdateRelationshipRequestBody", "mergeUpdate": True, "properties": props})

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ASSET_ROOT}/data-set-content/rel-guid/update")
    assert calls[0]["body"]["class"] == "UpdateRelationshipRequestBody"
    assert calls[0]["body"]["mergeUpdate"] is True
    # none of the DataSetContent properties is dropped on the way out
    assert calls[0]["body"]["properties"] == props


@pytest.mark.asyncio
async def test_detach_data_set_content_relationship_with_body(monkeypatch):
    calls: list = []
    client = _asset_maker(calls, monkeypatch)

    await client._async_detach_data_set_content_relationship(
        "rel-guid", {"class": "DeleteRelationshipRequestBody", "externalSourceGUID": "src"})

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ASSET_ROOT}/data-set-content/rel-guid/detach")
    assert calls[0]["body"]["class"] == "DeleteRelationshipRequestBody"
    assert calls[0]["body"]["externalSourceGUID"] == "src"


@pytest.mark.asyncio
async def test_detach_data_set_content_relationship_without_body(monkeypatch):
    calls: list = []
    client = _asset_maker(calls, monkeypatch)

    await client._async_detach_data_set_content_relationship("rel-guid")

    assert calls[0]["url"].endswith(f"{ASSET_ROOT}/data-set-content/rel-guid/detach")
    assert calls[0]["body"] is None


@pytest.mark.asyncio
async def test_new_methods_do_not_reuse_the_two_element_paths(monkeypatch):
    # the older attach/detach address the two linked elements; the new ones must not
    calls: list = []
    client = _asset_maker(calls, monkeypatch)

    await client._async_detach_data_set_content_relationship("rel-guid")

    assert "/data-sets/" not in calls[0]["url"]


@pytest.mark.asyncio
async def test_link_resource_to_connection(monkeypatch):
    calls: list = []
    client = _connection_maker(calls, monkeypatch)
    props = {"class": "ResourceConnectionProperties", "label": "primary", "description": "d"}

    await client._async_link_resource_to_connection(
        "element-guid", "connection-guid", {"class": "NewRelationshipRequestBody", "properties": props})

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{CONN_ROOT}/elements/element-guid/connections/connection-guid/attach")
    assert calls[0]["body"]["class"] == "NewRelationshipRequestBody"
    assert calls[0]["body"]["properties"] == props


@pytest.mark.asyncio
async def test_detach_resource_from_connection_sends_delete_options(monkeypatch):
    calls: list = []
    client = _connection_maker(calls, monkeypatch)

    await client._async_detach_resource_from_connection(
        "element-guid", "connection-guid",
        {"class": "DeleteRelationshipRequestBody", "deleteMethod": "SOFT_DELETE"})

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{CONN_ROOT}/elements/element-guid/connections/connection-guid/detach")
    assert calls[0]["body"]["deleteMethod"] == "SOFT_DELETE"


@pytest.mark.asyncio
async def test_link_resource_is_distinct_from_the_asset_only_path(monkeypatch):
    calls: list = []
    client = _connection_maker(calls, monkeypatch)

    await client._async_link_resource_to_connection("e", "c", {"class": "NewRelationshipRequestBody"})
    await client._async_link_asset_to_connection("a", "c", {"class": "NewRelationshipRequestBody"})

    assert "/elements/e/connections/c/attach" in calls[0]["url"]
    assert "/assets/a/connections/c/attach" in calls[1]["url"]
