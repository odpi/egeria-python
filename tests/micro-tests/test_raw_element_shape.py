# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Raw metadata-expert elements are read in view-bean shape (pyegeria.core.element_shape).

Fixtures are real OpenMetadataElements read from laz (read only, 2026-11-13, Egeria 002a3ef1, as erinoverview):
- laz_topic_live_2026_11_13.json: get_metadata_element_by_guid of the live Topic `openlineage.events`;
- laz_topic_memento_2026_11_13.json: its archived (Memento) twin, from a forLineage find.
"""
import asyncio
import json
from pathlib import Path
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from pyegeria.core.element_shape import as_view_element, is_raw_element

pytestmark = pytest.mark.unit

DATA = Path(__file__).parent / "data" / "raw_elements"
LIVE = json.loads((DATA / "laz_topic_live_2026_11_13.json").read_text())
MEMENTO = json.loads((DATA / "laz_topic_memento_2026_11_13.json").read_text())


def test_a_raw_element_reads_as_a_view_bean():
    assert is_raw_element(LIVE)
    el = as_view_element(LIVE)
    assert el["elementHeader"]["guid"] == "00daa9fb-11b7-409d-9ee2-1602ea0aff42"
    assert el["elementHeader"]["type"]["typeName"] == "Topic"
    props = el["properties"]
    assert props["qualifiedName"] == "Topic::LocalKafka2.openlineage.events::inOut"
    assert props["displayName"] == "openlineage.events"
    assert props["contentStatus"] == "ACTIVE"                       # an enum, by symbolic name
    assert el["elementHeader"]["anchor"]["classificationProperties"]["anchorTypeName"] == "Topic"
    usage = el["elementHeader"]["usageActivity"]["classificationProperties"]
    assert isinstance(usage["findCount"], int)                      # a long, typed
    data_scope = el["elementHeader"]["dataScope"]["classificationProperties"]["additionalProperties"]
    assert isinstance(data_scope, dict) and data_scope["readCount"] == "5"   # a map<string,string>


def test_a_memento_is_found_in_its_header_slot():
    el = as_view_element(MEMENTO)
    assert el["elementHeader"]["memento"]["classificationProperties"]["archiveMethod"] == "deleteMetadataElementInStore"
    assert AsyncBaseCommandProcessor._ignore_memento(el) is None
    assert AsyncBaseCommandProcessor._ignore_memento(as_view_element(LIVE)) is not None


def test_a_view_bean_and_a_miss_are_unchanged():
    bean = {"elementHeader": {"guid": "g"}, "properties": {"qualifiedName": "q"}}
    assert as_view_element(bean) is bean
    assert as_view_element("No elements found") == "No elements found"
    assert as_view_element(None) is None


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


class _Client:
    """ClassificationExplorer fails (not a timeout); metadata-expert answers in the raw shape."""
    async def _async_get_element_by_guid_(self, guid):
        raise ValueError("unsupported type")

    async def _async_get_metadata_element_by_guid(self, guid):
        return LIVE


def test_fetch_element_fallback_returns_the_view_shape():
    p = _P(client=cast(Any, _Client()), command=DrECommand(verb="Update", object_type="Collection", attributes={},
                                                         raw_block="## Update Collection"), context={})
    el = asyncio.run(p.fetch_element("00daa9fb-11b7-409d-9ee2-1602ea0aff42"))
    assert el["elementHeader"]["guid"] == "00daa9fb-11b7-409d-9ee2-1602ea0aff42"
    assert el["properties"]["qualifiedName"] == "Topic::LocalKafka2.openlineage.events::inOut"


def test_find_in_asset_domain_sends_a_match_all_regex_not_null(monkeypatch):
    from pyegeria.omvs.asset_catalog import AssetCatalog
    seen = {}

    async def fake_find(self, url, _type, _gen_output, **params):
        seen.update(params)
        return []
    monkeypatch.setattr(AssetCatalog, "_async_find_request", fake_find)
    ac = AssetCatalog.__new__(AssetCatalog)
    ac.platform_url, ac.view_server = "https://x", "v"
    for given in ("*", None, ""):
        asyncio.run(AssetCatalog._async_find_in_asset_domain(ac, given))
        assert seen["search_string"] == ".*"
    asyncio.run(AssetCatalog._async_find_in_asset_domain(ac, "Report"))
    assert seen["search_string"] == "Report"
