# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""ISSUE-185 (6.2.36): get_collection_members ignored start_from and page_size.

They are the method's own parameters, so they never reached **kwargs, and they were never passed on: every call
read the first page. A reader paging until an empty page (saved_query) therefore re-read the same members until its
bound, and a 3-member Results Set read as "at least 60" on the Portal and in EA (the Architect's live Route B
read-back, 2026-11-11). Also: paging given as arguments was dropped whenever a caller passed its own body.

The fake server below answers members/ requests the way Egeria pages: by the body's startFrom and pageSize.
"""
import asyncio
import json

import pytest

from pyegeria.core._server_client import _with_paging
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.view import saved_query as sq

pytestmark = pytest.mark.unit

MEMBERS = [{"elementHeader": {"guid": f"m{i}", "type": {"typeName": "DataSet"}},
            "properties": {"qualifiedName": f"Asset::{i}", "displayName": f"Asset {i}"}} for i in range(7)]


class _Response:
    def __init__(self, body):
        self._body = body

    def json(self):
        return self._body


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(CollectionManager, "check_connection", lambda self: "test")
    c = CollectionManager("view-server", "https://localhost:1", "user", "pwd")
    c.sent = []

    async def server(method, url, body=None, *a, **kw):
        req = json.loads(body) if isinstance(body, str) else (body or {})
        c.sent.append(req)
        start, size = req.get("startFrom", 0), req.get("pageSize", 0) or len(MEMBERS)
        page = MEMBERS[start:start + size]
        return _Response({"elements": page} if page else {"element": "No elements found"})

    c._async_make_request = server
    return c


def _members(c, **kw):
    return asyncio.run(c._async_get_collection_members(collection_guid="rs-1", output_format="JSON", **kw))


def _guids(found):
    return [e["elementHeader"]["guid"] for e in found] if isinstance(found, list) else found


def test_two_pages_differ(client):
    assert _guids(_members(client, start_from=0, page_size=3)) == ["m0", "m1", "m2"]
    assert _guids(_members(client, start_from=3, page_size=3)) == ["m3", "m4", "m5"]
    assert _guids(_members(client, start_from=6, page_size=3)) == ["m6"]
    assert _members(client, start_from=9, page_size=3) == "No elements found"


def test_the_request_body_carries_the_paging(client):
    _members(client, start_from=50, page_size=50)
    assert client.sent[-1]["startFrom"] == 50 and client.sent[-1]["pageSize"] == 50
    assert client.sent[-1]["class"] == "ResultsRequestBody"


def test_a_callers_body_gets_the_calls_paging_unless_it_sets_its_own(client):
    _members(client, body={"class": "ResultsRequestBody", "limitResultsByStatus": ["ACTIVE"]}, start_from=3, page_size=3)
    assert (client.sent[-1]["startFrom"], client.sent[-1]["pageSize"]) == (3, 3)
    assert client.sent[-1]["limitResultsByStatus"] == ["ACTIVE"]
    _members(client, body={"class": "ResultsRequestBody", "pageSize": 2}, start_from=3, page_size=3)
    assert (client.sent[-1]["startFrom"], client.sent[-1]["pageSize"]) == (3, 2)   # the body's own wins


@pytest.mark.parametrize(("body", "start", "size", "expected"), [
    ({"a": 1}, 0, 0, {"a": 1}),
    ({"a": 1}, 5, 10, {"a": 1, "startFrom": 5, "pageSize": 10}),
    ({"start_from": 2}, 5, 10, {"start_from": 2, "pageSize": 10}),
    ({"startFrom": 2, "pageSize": 4}, 5, 10, {"startFrom": 2, "pageSize": 4}),
])
def test_with_paging(body, start, size, expected):
    assert _with_paging(body, start, size) == expected
    assert body == {k: v for k, v in body.items()}   # the caller's dict is not changed


def test_saved_query_reads_every_member_once_through_the_real_call(client):
    found, capped, note = sq._read_pages(
        lambda start, size: client.get_collection_members(collection_guid="rs-1", start_from=start, page_size=size,
                                                          output_format="JSON"),
        3, 20)
    assert _guids(found) == [f"m{i}" for i in range(7)] and capped is False and note is None


# ── a server that ignores paging (what laz showed): repetition is never a count, and never "capped" ──

def test_a_page_that_repeats_stops_the_read_and_says_so():
    first3 = MEMBERS[:3]
    found, capped, note = sq._read_pages(lambda start, size: list(first3), 50, 20)
    assert _guids(found) == ["m0", "m1", "m2"] and capped is False
    assert note.startswith("paging did not advance: the read from position 3 returned only elements already read")


def test_a_genuinely_long_read_is_still_capped():
    found, capped, note = sq._read_pages(
        lambda start, size: [{"elementHeader": {"guid": f"g{start + i}"}} for i in range(size)], 5, 4)
    assert len(found) == 20 and capped is True and note is None


def test_the_tile_the_architect_saw_reads_3_not_at_least_60():
    class Stuck:
        """laz on 2026-11-11: (0,50), (3,50), (50,50), (0,2), (2,2) all returned the same 3 members."""
        platform_url, view_server = "https://localhost:9443", "qs-view-server"

        def find_metadata_elements(self, body=None, **kw):
            return [{"elementHeader": {"guid": "sq-1", "type": {"typeName": "SavedQuery"}},
                     "properties": {"qualifiedName": "SavedQuery::stuck", "additionalProperties": {
                         "resultsSetGuid": "rs-1", "lastRefreshedTime": "2026-11-11T10:00:00+00:00"}}}]

        def get_related_elements(self, *a, **kw):
            return "No elements found"

        def get_collection_members(self, **kw):
            return list(MEMBERS[:3])

    out = sq.saved_query(Stuck(), "SavedQuery::stuck")
    assert out["value"] == 3 and out["display"] == "3" and not out.get("capped")
    assert "paging did not advance" in out["note"]
