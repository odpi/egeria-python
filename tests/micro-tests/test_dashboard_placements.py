# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dashboard placements (Egeria 6.3; owner decision 2026-11-07): a REPORT placement is a DisplayDataField, and
the report it shows is linked by DataSetContent from the Dashboard to the Report with queryId = the
placement's qualifiedName and queryType = "placement". A placement with no such link is reported as
unbound, never as an empty value. No network: _async_make_request is replaced by a recorder.
"""
import json

import pytest

from pyegeria.omvs.asset_maker import AssetMaker, PLACEMENT_QUERY_TYPE, resolve_placement_reports

AM_BASE = "https://localhost:1/servers/view-server/api/open-metadata/asset-maker"


def _link(rel_guid, query_id, report_guid, report_name, query_type="placement"):
    return {
        "relationshipHeader": {"guid": rel_guid, "type": {"typeName": "DataSetContent"}},
        "relationshipProperties": {"class": "DataSetContentProperties", "queryId": query_id,
                                   "queryType": query_type},
        "relatedElement": {"elementHeader": {"guid": report_guid},
                           "properties": {"displayName": report_name, "qualifiedName": f"Report::{report_name}"}},
    }


DASHBOARD = {
    "elementHeader": {"guid": "dash-1"},
    "dataSetContent": [
        _link("rel-1", "DDF::kpi-tile", "rep-1", "Terms"),
        _link("rel-2", "DDF::panel", "rep-1", "Terms"),          # same report, second placement
        _link("rel-3", "DDF::twice", "rep-2", "Glossaries"),
        _link("rel-4", "DDF::twice", "rep-3", "Projects"),       # two links for one placement
        _link("rel-5", "DDF::lineage", "rep-4", "Lineage", query_type="lineage"),  # not a placement link
    ],
}


def test_states():
    out = resolve_placement_reports(DASHBOARD, ["DDF::kpi-tile", "DDF::panel", "DDF::twice", "DDF::missing",
                                                "DDF::lineage"])
    assert out["DDF::kpi-tile"]["state"] == "bound"
    assert out["DDF::kpi-tile"]["report_guid"] == "rep-1"
    assert out["DDF::kpi-tile"]["report_name"] == "Terms"
    assert out["DDF::kpi-tile"]["relationship_guid"] == "rel-1"
    assert out["DDF::panel"]["relationship_guid"] == "rel-2"
    assert out["DDF::twice"]["state"] == "ambiguous"
    assert {l["report_guid"] for l in out["DDF::twice"]["links"]} == {"rep-2", "rep-3"}
    assert "report_guid" not in out["DDF::twice"]   # none is chosen
    assert out["DDF::missing"] == {"state": "unbound", "links": []}
    assert out["DDF::lineage"]["state"] == "unbound"  # other queryTypes are not placement bindings


def test_dashboard_with_no_links_reports_every_placement_unbound():
    out = resolve_placement_reports({"elementHeader": {"guid": "dash-2"}}, ["a", "b"])
    assert out == {"a": {"state": "unbound", "links": []}, "b": {"state": "unbound", "links": []}}


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(monkeypatch, sent, element=None):
    monkeypatch.setattr(AssetMaker, "check_connection", lambda self: "test")
    client = AssetMaker("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        sent.append({"method": method, "url": url, "body": json.loads(body) if isinstance(body, str) else body})
        return _Response({"class": "GUIDResponse", "guid": "new-rel"})

    async def fake_get_asset(guid, include_only_relationships=None, **kwargs):
        sent.append({"get": guid, "include_only_relationships": include_only_relationships})
        return element

    client._async_make_request = fake_make_request
    client._async_get_asset_by_guid = fake_get_asset
    return client


@pytest.mark.asyncio
async def test_link_sets_query_id_and_type(monkeypatch):
    sent = []
    client = _client(monkeypatch, sent)

    guid = await client._async_link_placement_report(
        "dash-1", "rep-1", "DDF::kpi-tile",
        body={"properties": {"queryId": "ignored", "queryType": "ignored", "iscQualifiedName": "ISC::x"}})

    assert guid == "new-rel"
    assert sent[0]["url"] == f"{AM_BASE}/data-sets/dash-1/data-set-content/rep-1/attach"
    assert sent[0]["body"]["class"] == "NewRelationshipRequestBody"
    assert sent[0]["body"]["properties"] == {"class": "DataSetContentProperties", "queryId": "DDF::kpi-tile",
                                             "queryType": PLACEMENT_QUERY_TYPE, "iscQualifiedName": "ISC::x"}


@pytest.mark.asyncio
async def test_link_requires_placement_name(monkeypatch):
    client = _client(monkeypatch, [])
    with pytest.raises(ValueError):
        await client._async_link_placement_report("dash-1", "rep-1", "")


@pytest.mark.asyncio
async def test_get_placement_reports_reads_data_set_content(monkeypatch):
    sent = []
    client = _client(monkeypatch, sent, element=DASHBOARD)

    out = await client._async_get_placement_reports("dash-1", ["DDF::panel", "DDF::missing"])

    assert sent[0] == {"get": "dash-1", "include_only_relationships": ["DataSetContent"]}
    assert out["DDF::panel"]["state"] == "bound"
    assert out["DDF::missing"]["state"] == "unbound"


@pytest.mark.asyncio
async def test_unreadable_dashboard_is_an_error_not_unbound(monkeypatch):
    client = _client(monkeypatch, [], element="No elements found")
    with pytest.raises(ValueError, match="could not be retrieved"):
        await client._async_get_placement_reports("dash-x", ["DDF::panel"])


@pytest.mark.asyncio
async def test_detach_removes_only_this_placements_link(monkeypatch):
    sent = []
    client = _client(monkeypatch, sent, element=DASHBOARD)

    removed = await client._async_detach_placement_report("dash-1", "DDF::panel")

    assert removed == 1
    posts = [s for s in sent if "url" in s]
    assert [p["url"] for p in posts] == [f"{AM_BASE}/data-set-content/rel-2/detach"]  # not rel-1 (same report)


@pytest.mark.asyncio
async def test_detach_unbound_placement_removes_nothing(monkeypatch):
    sent = []
    client = _client(monkeypatch, sent, element=DASHBOARD)
    assert await client._async_detach_placement_report("dash-1", "DDF::missing") == 0
    assert [s for s in sent if "url" in s] == []


def test_sync_wrappers_exist():
    for name in ("link_placement_report", "get_placement_reports", "detach_placement_report"):
        assert callable(getattr(AssetMaker, name))
