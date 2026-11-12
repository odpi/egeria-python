# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A merge update keeps the stored additionalProperties keys the document doesn't write.

Egeria replaces a map property whole, even with mergeUpdate true. A Create that found its element (and became
an Update) used to send only the document's keys, so on laz a SavedQuery's refresh keys were wiped, and a CDO
Report's search keys nearly were. The base processor now overlays the document's keys on the stored map
(md_processing/v2/additional_properties.py); a replace update replaces and says so; a merge update whose stored
map can't be read is refused. The fake clients stand in for Egeria; nothing reaches a server.
"""
from typing import Any, cast

import pytest

from md_processing.v2.additional_properties import (
    AdditionalPropertiesUnreadable, merge_additional_properties, stored_additional_properties,
)
from md_processing.v2.extraction import DrECommand
from md_processing.v2.report import ReportProcessor, upsert_dashboard_asset
from md_processing.v2.saved_query import SavedQueryProcessor

pytestmark = pytest.mark.unit

GUID = "aaaaaaaa-0000-0000-0000-00000000000a"

# The keys the Portal's insights refresh writes on a laz SavedQuery (wiped at 11:08Z by a Create->Update).
SAVED_QUERY_REFRESH_KEYS = {
    "lastRefreshedTime": "2026-11-12T10:55:02Z",
    "resultCount": "17",
    "resultsSetGuid": "bbbbbbbb-0000-0000-0000-00000000000b",
    "smartQueryRelGuid": "cccccccc-0000-0000-0000-00000000000c",
    "lastRefreshParams": '{"page_size": 100, "type_name": "Asset"}',
}

# A CDO Report: the three keys its document writes, and seven search keys only the stored element has.
CDO_DOCUMENT_KEYS = {"Report Spec": "Risk-DrE-Basic", "Output Format": "TABLE", "Search String": "CocoPharma::Risk::"}
CDO_STORED = {
    "reportSpec": "Risk-DrE-Basic",
    "outputFormat": "TABLE",
    "searchString": "CocoPharma::Risk::",
    "startsWith": "true",
    "endsWith": "false",
    "ignoreCase": "true",
    "metadataElementTypeName": "GovernanceRisk",
    "limitResultByStatus": "ACTIVE",
    "graphQueryDepth": "1",
    "pageSize": "200",
}


class _Recorder:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def _record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return "dddddddd-0000-0000-0000-00000000000d"
        return _record


class _Client(_Recorder):
    def __init__(self, fetched=None):
        super().__init__()
        self.classification_manager = _Recorder()
        self.data_designer = _Recorder()
        self._fetched = fetched

    async def _async_get_element_by_guid_(self, guid):
        return self._fetched

    def updates(self):
        return [args for name, args, _ in self.calls if name == "_async_update_asset"]


def _element(additional):
    props = {"qualifiedName": "X::test", "displayName": "test"}
    if additional is not None:
        props["additionalProperties"] = additional
    return {"elementHeader": {"guid": GUID}, "properties": props}


def _processor(cls, object_type, attributes, as_is, fetched=None, verb="Update"):
    client = _Client(fetched)
    p = cls(client=cast(Any, client), command=DrECommand(verb=verb, object_type=object_type, attributes={},
                                                         raw_block=f"## {verb} {object_type}"), context={})
    p.parsed_output = {"qualified_name": f"{object_type}::test", "attributes": attributes, "exists": True,
                       "guid": GUID}
    p.as_is_element = as_is

    async def _render(guid):
        return guid
    p.render_result_markdown = _render
    return p, client


async def _run(p):
    """What execute() does around apply_changes()."""
    await p._prepare_additional_properties()
    return await p.apply_changes()


def _a(merge=True, **values):
    attrs = {k: {"value": v} for k, v in values.items()}
    attrs["Display Name"] = {"value": "test"}
    attrs["Merge Update"] = {"value": merge, "is_default": True}
    return attrs


# ------------------------------------------------------------------ the merge itself

def test_merge_keeps_stored_keys_and_the_document_wins():
    merged = merge_additional_properties({"a": "1", "b": "2"}, {"b": "new", "c": "3"})
    assert merged == {"a": "1", "b": "new", "c": "3"}


def test_stored_map_is_unknown_without_properties():
    assert stored_additional_properties({"elementHeader": {"guid": GUID}}) is None
    assert stored_additional_properties(_element(None)) == {}
    assert stored_additional_properties(_element({"k": "v"})) == {"k": "v"}


# ------------------------------------------------------------------ SavedQuery (laz refresh keys)

@pytest.mark.asyncio
async def test_saved_query_create_to_update_keeps_the_refresh_keys():
    attributes = _a(**{"Additional Properties": {"owner": "erinoverview"}})
    p, client = _processor(SavedQueryProcessor, "Saved Query", attributes, _element(dict(SAVED_QUERY_REFRESH_KEYS)),
                           verb="Create")
    await _run(p)
    (guid, body), = client.updates()
    assert guid == GUID and body["mergeUpdate"] is True
    assert body["properties"]["additionalProperties"] == {**SAVED_QUERY_REFRESH_KEYS, "owner": "erinoverview"}


@pytest.mark.asyncio
async def test_saved_query_document_key_overrides_a_stored_key():
    attributes = _a(**{"Additional Properties": {"resultCount": "0"}})
    p, client = _processor(SavedQueryProcessor, "Saved Query", attributes, _element(dict(SAVED_QUERY_REFRESH_KEYS)))
    await _run(p)
    sent = client.updates()[0][1]["properties"]["additionalProperties"]
    assert sent == {**SAVED_QUERY_REFRESH_KEYS, "resultCount": "0"}


@pytest.mark.asyncio
async def test_saved_query_without_additional_properties_sends_no_map():
    p, client = _processor(SavedQueryProcessor, "Saved Query", _a(), _element(dict(SAVED_QUERY_REFRESH_KEYS)))
    await _run(p)
    assert client.updates()[0][1]["properties"].get("additionalProperties") is None  # Egeria keeps the stored map


# ------------------------------------------------------------------ Report (CDO search keys)

@pytest.mark.asyncio
async def test_report_create_to_update_keeps_the_cdo_search_keys():
    p, client = _processor(ReportProcessor, "Report", _a(**CDO_DOCUMENT_KEYS), _element(dict(CDO_STORED)),
                           verb="Create")
    await _run(p)
    (guid, body), = client.updates()
    sent = body["properties"]["additionalProperties"]
    assert sent == CDO_STORED  # all 10 keys, not just the 3 the document writes


@pytest.mark.asyncio
async def test_report_document_values_win_over_stored():
    p, client = _processor(ReportProcessor, "Report", _a(**{**CDO_DOCUMENT_KEYS, "Output Format": "LIST"}),
                           _element(dict(CDO_STORED)))
    await _run(p)
    sent = client.updates()[0][1]["properties"]["additionalProperties"]
    assert sent == {**CDO_STORED, "outputFormat": "LIST"}


# ------------------------------------------------------------------ replace update

@pytest.mark.asyncio
async def test_replace_update_replaces_and_says_so():
    attributes = _a(merge=False, **{"Additional Properties": {"owner": "erinoverview"}})
    p, client = _processor(SavedQueryProcessor, "Saved Query", attributes, _element(dict(SAVED_QUERY_REFRESH_KEYS)))
    await _run(p)
    body = client.updates()[0][1]
    assert body["mergeUpdate"] is False
    assert body["properties"]["additionalProperties"] == {"owner": "erinoverview"}
    (warning,) = [w for w in p.parsed_output["warnings"] if "Merge Update is false" in w]
    for key in SAVED_QUERY_REFRESH_KEYS:
        assert key in warning


@pytest.mark.asyncio
async def test_report_replace_update_sends_only_the_document_keys():
    p, client = _processor(ReportProcessor, "Report", _a(merge=False, **CDO_DOCUMENT_KEYS), _element(dict(CDO_STORED)))
    await _run(p)
    sent = client.updates()[0][1]["properties"]["additionalProperties"]
    assert sent == {"reportSpec": "Risk-DrE-Basic", "outputFormat": "TABLE", "searchString": "CocoPharma::Risk::"}


# ------------------------------------------------------------------ unreadable as-is element

@pytest.mark.asyncio
async def test_unreadable_element_is_refused_not_replaced():
    attributes = _a(**{"Additional Properties": {"owner": "erinoverview"}})
    headless = {"elementHeader": {"guid": GUID}}  # read without its properties, and the re-read finds nothing
    p, client = _processor(SavedQueryProcessor, "Saved Query", attributes, headless, fetched=None)
    with pytest.raises(AdditionalPropertiesUnreadable, match="Refusing to update"):
        await _run(p)
    assert client.updates() == []


@pytest.mark.asyncio
async def test_report_with_unreadable_element_is_refused():
    p, client = _processor(ReportProcessor, "Report", _a(**CDO_DOCUMENT_KEYS), {"elementHeader": {"guid": GUID}})
    with pytest.raises(AdditionalPropertiesUnreadable):
        await _run(p)
    assert client.updates() == []


@pytest.mark.asyncio
async def test_headless_element_is_re_read_by_guid():
    attributes = _a(**{"Additional Properties": {"owner": "erinoverview"}})
    p, client = _processor(SavedQueryProcessor, "Saved Query", attributes, {"elementHeader": {"guid": GUID}},
                           fetched=_element(dict(SAVED_QUERY_REFRESH_KEYS)))
    await _run(p)
    sent = client.updates()[0][1]["properties"]["additionalProperties"]
    assert sent == {**SAVED_QUERY_REFRESH_KEYS, "owner": "erinoverview"}


@pytest.mark.asyncio
async def test_update_with_no_as_is_element_is_refused():
    attributes = _a(**{"Additional Properties": {"owner": "erinoverview"}})
    p, _ = _processor(SavedQueryProcessor, "Saved Query", attributes, None)
    with pytest.raises(AdditionalPropertiesUnreadable):
        await p._prepare_additional_properties()


# ------------------------------------------------------------------ Dashboard asset upsert

@pytest.mark.asyncio
async def test_dashboard_upsert_merges_with_the_existing_map():
    client = _Client()
    existing = _element({"family": "CDO", "layoutHint": "grid"})
    props = {"class": "DashboardProperties", "qualifiedName": "Dashboard::CDO", "additionalProperties": {"family": "CDO2"}}
    guid, verb, body = await upsert_dashboard_asset(client, "Dashboard::CDO", props, existing)
    assert verb == "Updated"
    assert body["properties"]["additionalProperties"] == {"family": "CDO2", "layoutHint": "grid"}


@pytest.mark.asyncio
async def test_dashboard_upsert_unchanged_when_given_keys_match():
    client = _Client()
    existing = _element({"family": "CDO", "layoutHint": "grid"})
    props = {"class": "DashboardProperties", "qualifiedName": "X::test", "displayName": "test",
             "additionalProperties": {"family": "CDO"}}
    _, verb, body = await upsert_dashboard_asset(client, "X::test", props, existing)
    assert verb == "Unchanged" and body is None
