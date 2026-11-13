# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 2: Search Keywords are attached after create, on every command.

The Referenceable bundle carries Search Keywords on nearly every Create; no processor applied them (116
rows DROPPED on the round-trip probe's PostgreSQL baseline). The base processor now attaches one
SearchKeyword per entry -- SearchKeywordProperties.displayName, the Java bean has no `keyword` field -- and
skips keywords the element already has.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from pyegeria import PyegeriaException

GUID = "44b02a92-779b-44d5-8bc4-8b138e90c91f"


class _Explorer:
    def __init__(self, fail_on=None):
        self.bodies = []
        self.fail_on = fail_on

    async def _async_add_search_keyword_to_element(self, guid, body):
        if body["properties"]["displayName"] == self.fail_on:
            raise PyegeriaException(response="Egeria refused the keyword")
        self.bodies.append((guid, body))
        return "kw-guid"


class _Client:
    def __init__(self, fail_on=None):
        self.classification_manager = _Explorer(fail_on)


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def _processor(client, as_is=None):
    p = _P(client=cast(Any, client), command=DrECommand(verb="Create", object_type="Glossary", attributes={},
                                                        raw_block="## Create Glossary"), context={})
    p.as_is_element = as_is
    p.parsed_output = {"attributes": {}}
    return p


@pytest.mark.asyncio
async def test_each_keyword_is_attached_by_display_name():
    client = _Client()
    p = _processor(client)
    await p._sync_search_keywords(GUID, {"Search Keywords": {"value": ["RTP-kw-1", "RTP-kw-2", "RTP-kw-1"]}})
    assert [b["properties"] for _, b in client.classification_manager.bodies] == [
        {"class": "SearchKeywordProperties", "displayName": "RTP-kw-1"},
        {"class": "SearchKeywordProperties", "displayName": "RTP-kw-2"}]
    assert all(g == GUID for g, _ in client.classification_manager.bodies)
    assert all(b["class"] == "NewAttachmentRequestBody" for _, b in client.classification_manager.bodies)


@pytest.mark.asyncio
async def test_existing_keywords_are_not_duplicated():
    client = _Client()
    as_is = {"searchKeywords": [{"relatedElement": {"properties": {"displayName": "RTP-kw-1"}}}]}
    p = _processor(client, as_is)
    await p._sync_search_keywords(GUID, {"Search Keywords": {"value": ["RTP-kw-1", "RTP-kw-2"]}})
    assert [b["properties"]["displayName"] for _, b in client.classification_manager.bodies] == ["RTP-kw-2"]


@pytest.mark.asyncio
async def test_no_keywords_no_calls_and_a_refusal_is_reported():
    client = _Client(fail_on="bad")
    p = _processor(client)
    await p._sync_search_keywords(GUID, {})
    assert client.classification_manager.bodies == []
    await p._sync_search_keywords(GUID, {"Search Keywords": {"value": ["bad", "good"]}})
    results = {r["label"]: r for r in p.related_results}
    assert [b["properties"]["displayName"] for _, b in client.classification_manager.bodies] == ["good"]
    assert any(r["status"] == "failure" and "Egeria refused the keyword" in r["message"] for r in p.related_results)
