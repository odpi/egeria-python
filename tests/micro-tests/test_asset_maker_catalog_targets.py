"""
ISSUE-122: AssetMaker.get_catalog_target(s) must not send
metadataElementTypeName="CatalogTarget" -- that is a relationship type, and the
server rejects it (OMAG-COMMON-400-019).
"""
import json

import pytest

from pyegeria.omvs.asset_maker import AssetMaker, CatalogTargetProperties


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client_capturing(bodies: list, payload: dict, monkeypatch) -> AssetMaker:
    monkeypatch.setattr(AssetMaker, "check_connection", lambda self: "test")
    client = AssetMaker("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        bodies.append(json.loads(body) if isinstance(body, str) else body)
        return _Response(payload)

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
async def test_get_catalog_targets_sends_no_element_type(monkeypatch):
    bodies: list = []
    client = _client_capturing(bodies, {"elements": []}, monkeypatch)

    await client._async_get_catalog_targets("conn-guid", output_format="JSON")

    assert "metadataElementTypeName" not in bodies[0]


@pytest.mark.asyncio
async def test_get_catalog_target_sends_no_element_type(monkeypatch):
    bodies: list = []
    client = _client_capturing(bodies, {"element": {}}, monkeypatch)

    await client._async_get_catalog_target("rel-guid", output_format="JSON")

    assert "metadataElementTypeName" not in bodies[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("flag, expected", [(True, "Widget"), (False, None)])
async def test_guid_request_filter_flag(flag, expected, monkeypatch):
    bodies: list = []
    client = _client_capturing(bodies, {"element": {}}, monkeypatch)

    await client._async_get_guid_request(
        "https://localhost:1/x", "Widget", lambda **kw: kw, output_format="JSON",
        filter_results_by_type=flag)

    assert bodies[0].get("metadataElementTypeName") == expected


def test_catalog_target_properties_keeps_relationship_fields():
    props = CatalogTargetProperties(
        qualifiedName="q", displayName="d", catalogTargetName="t", connectionName="c", metadataCollectionQualifiedName="m",
        permittedSynchronization="TO_THIRD_PARTY", deleteMethod="SOFT_DELETE")
    dumped = props.model_dump(exclude_none=True, by_alias=True)
    for key in ("connectionName", "metadataCollectionQualifiedName",
                "permittedSynchronization", "deleteMethod"):
        assert key in dumped


# Trimmed from a live get_catalog_target response (2026-10-04): a relationship, not an element;
# its ends are element stubs (guid / uniqueName / type), with no `properties` block.
_REL = {
    "relationshipGUID": "rel-1",
    "relationshipType": {"typeName": "CatalogTarget"},
    "relationshipProperties": {"propertiesAsStrings": {"catalogTargetName": "tgt"}},
    "elementGUIDAtEnd1": "conn-1",
    "elementAtEnd1": {"guid": "conn-1", "type": {"typeName": "IntegrationConnector"},
                      "uniqueName": "JDBC Cataloguer"},
    "elementGUIDAtEnd2": "asset-1",
    "elementAtEnd2": {"guid": "asset-1", "type": {"typeName": "Asset"}, "uniqueName": "q-asset"},
}


@pytest.mark.asyncio
async def test_get_catalog_target_dict_is_not_blank(monkeypatch):
    client = _client_capturing([], {"element": _REL}, monkeypatch)

    rows = await client._async_get_catalog_target("rel-1", output_format="DICT")

    assert rows[0]["GUID"] == "rel-1"
    assert rows[0]["Catalog Target Name"] == "tgt"
    assert rows[0]["Integration Connector"] == "JDBC Cataloguer"
    assert rows[0]["Target Element GUID"] == "asset-1"
    assert rows[0]["Target Element"] == "q-asset"


@pytest.mark.asyncio
async def test_get_catalog_target_md_is_not_blank(monkeypatch):
    client = _client_capturing([], {"element": _REL}, monkeypatch)

    md = await client._async_get_catalog_target("rel-1", output_format="MD")

    assert "rel-1" in md and "tgt" in md and "JDBC Cataloguer" in md
    assert "NO DISPLAY NAME" not in md
