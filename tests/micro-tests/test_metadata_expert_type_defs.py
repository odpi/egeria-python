"""
MetadataExpert type-definition maintenance: add/update/delete enum and type
definitions through the API (Egeria-api-metadata-expert.http). No live server:
the HTTP call is captured and the URL, verb, body and query params asserted.
"""
import json

import pytest

from pyegeria.omvs.metadata_expert import MetadataExpert

ROOT = "/api/open-metadata/metadata-expert"


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(calls: list, payload: dict, monkeypatch) -> MetadataExpert:
    monkeypatch.setattr(MetadataExpert, "check_connection", lambda self: "test")
    client = MetadataExpert("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload_=None, *args, params=None, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload_) if isinstance(payload_, str) else payload_,
                      "params": params})
        return _Response(payload)

    client._async_make_request = fake_make_request
    return client


ENUM = {
    "class": "OpenMetadataEnumDef", "name": "CuisineType", "description": "The style of cooking.",
    "elementDefs": [{"ordinal": 0, "value": "Unclassified", "description": "d"},
                    {"ordinal": 99, "value": "Other", "description": "o"}],
    "defaultValue": {"ordinal": 0, "value": "Unclassified", "description": "d"},
}
ENTITY = {
    "class": "OpenMetadataEntityDef", "name": "Recipe", "description": "How to prepare a dish.",
    "superType": {"name": "Referenceable"},
    "attributeDefinitions": [
        {"attributeName": "cuisine", "attributeType": {"class": "OpenMetadataEnumDef", "name": "CuisineType"},
         "attributeDescription": "The style of cooking."}],
}
PATCH = {
    "class": "OpenMetadataTypeDefPatch", "typeDefGUID": "type-guid", "typeDefName": "Recipe",
    "applyToVersion": 1,
    "attributeDefinitions": [{"attributeName": "preparationTimeMinutes",
                              "attributeType": {"class": "OpenMetadataPrimitiveDef", "name": "int"}}],
}


@pytest.mark.asyncio
async def test_add_enum_def(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "GUIDResponse", "guid": "enum-guid"}, monkeypatch)

    guid = await client._async_add_enum_def(ENUM)

    assert guid == "enum-guid"
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ROOT}/open-metadata-attribute-types/enum-defs")
    assert calls[0]["body"] == ENUM


@pytest.mark.asyncio
async def test_add_type_def_keeps_nested_and_undeclared_fields(monkeypatch):
    calls: list = []
    client = _client(calls, {"guid": "type-guid"}, monkeypatch)
    body = {**ENTITY, "relationshipAttributes": [{"relationshipType": {"name": "Foo"}}]}

    guid = await client._async_add_type_def(body)

    assert guid == "type-guid"
    assert calls[0]["url"].endswith(f"{ROOT}/open-metadata-types")
    # nothing the caller supplied is silently dropped (extra="allow")
    assert calls[0]["body"] == body


@pytest.mark.asyncio
async def test_add_type_def_without_guid_returns_payload(monkeypatch):
    client = _client([], {"class": "VoidResponse", "relatedHTTPCode": 200}, monkeypatch)

    assert await client._async_add_type_def(ENTITY) == {"class": "VoidResponse", "relatedHTTPCode": 200}


@pytest.mark.asyncio
async def test_update_type_def(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "VoidResponse"}, monkeypatch)

    result = await client._async_update_type_def(PATCH)

    assert result is None
    assert calls[0]["url"].endswith(f"{ROOT}/open-metadata-types/update")
    assert calls[0]["body"] == PATCH


@pytest.mark.asyncio
async def test_delete_type_def_sends_name_as_query_param_and_no_body(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "VoidResponse"}, monkeypatch)

    await client._async_delete_type_def("type-guid", "Recipe")

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ROOT}/open-metadata-types/guid/type-guid/delete")
    assert calls[0]["params"] == {"typeDefName": "Recipe"}
    assert calls[0]["body"] is None


@pytest.mark.asyncio
async def test_delete_enum_def_sends_name_as_query_param_and_no_body(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "VoidResponse"}, monkeypatch)

    await client._async_delete_enum_def("enum-guid", "CuisineType")

    assert calls[0]["url"].endswith(f"{ROOT}/open-metadata-attribute-types/enum-defs/guid/enum-guid/delete")
    assert calls[0]["params"] == {"enumDefName": "CuisineType"}
    assert calls[0]["body"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("method, bad_body", [
    ("_async_add_enum_def", {"class": "OpenMetadataEnumDef"}),            # name missing
    ("_async_add_type_def", {"class": "NotATypeDef", "name": "x"}),       # unknown class
    ("_async_update_type_def", {"class": "OpenMetadataTypeDefPatch", "typeDefName": "x"}),  # guid/version missing
])
async def test_invalid_bodies_are_rejected_before_any_request(method, bad_body, monkeypatch):
    calls: list = []
    client = _client(calls, {}, monkeypatch)

    with pytest.raises(Exception):
        await getattr(client, method)(bad_body)

    assert calls == []
