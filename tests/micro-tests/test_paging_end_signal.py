"""Pager step 2: the list helpers record what Egeria actually sent ("null" / "empty" / "rows") before a method
collapses ``[]`` into "No elements found", and the pager reads that record. The public return values of the
collapse sites are pinned: unchanged with or without a recording."""
import asyncio
import json

import pytest

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core._server_client import LIST_REQUEST_RECORD, recording_list_requests
from pyegeria.core.paging import async_page_all, page_all
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.metadata_expert import MetadataExpert

pytestmark = pytest.mark.unit

TOPIC = {"class": "OpenMetadataElement", "elementGUID": "00daa9fb",
         "elementProperties": {"displayName": "openlineage.events"}}
ELEMENT = {"elementHeader": {"guid": "g1", "type": {"typeName": "GlossaryTerm"}},
           "properties": {"qualifiedName": "Term::One", "displayName": "One"}}
RELATIONSHIP = {"relationshipHeader": {"guid": "r1", "type": {"typeName": "Synonym"}}}


class _Response:
    def __init__(self, body, sent=None):
        self._text = json.dumps(body)
        self.request = type("R", (), {"content": json.dumps(sent or {}).encode()})()

    def json(self):
        return json.loads(self._text)


def _client(cls, monkeypatch, answer):
    """A client whose server answers every request with answer(body_sent) (a dict: the raw JSON)."""
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    c = cls("view-server", "https://localhost:1", "user", "pwd")

    async def server(method, url, body=None, *a, **kw):
        sent = json.loads(body) if isinstance(body, str) else (body or {})
        return _Response(answer(sent), sent)

    c._async_make_request = server
    return c


# Three representative collapse sites, each turning [] into "No elements found".

def _name_request(c):
    return c._async_get_name_request(f"{c.platform_url}/x/by-name", "GlossaryTerm", lambda **kw: kw,
                                     filter_string="One", output_format="JSON")


def _find_metadata_elements(c):
    return c._async_find_metadata_elements(body={"class": "FindRequestBody", "metadataElementTypeName": "Topic"})


def _outcome(coro):
    """The call's return value, or the exception type it raised: both are part of what's pinned (an explicit
    JSON null, which Egeria doesn't send for these responses, makes some sites raise today)."""
    try:
        return asyncio.run(coro)
    except Exception as exc:  # noqa: BLE001
        return type(exc)


def _get_relationships(c):
    return c._async_get_relationships("Synonym", output_format="JSON")


SITES = [  # (client class, call, the JSON key read, a row, what the key ABSENT returns today)
    (MetadataExpert, _name_request, "elements", ELEMENT, NO_ELEMENTS_FOUND),     # core _async_get_name_request
    (MetadataExpert, _find_metadata_elements, "elements", TOPIC, NO_ELEMENTS_FOUND),   # omvs: the B5 path
    (ClassificationExplorer, _get_relationships, "relationships", RELATIONSHIP,
     "No relationships found"),                                                  # omvs, relationships key
]
IDS = ["get_name_request", "find_metadata_elements", "get_relationships"]

ANSWERS = [  # (raw JSON Egeria sends, what the record says)
    (lambda k, row: {}, "null"),                     # the key absent: Egeria's null
    (lambda k, row: {k: None}, "null"),              # explicit null
    (lambda k, row: {k: []}, "empty"),               # a filtered page
    (lambda k, row: {k: [row]}, "rows"),
]


@pytest.mark.parametrize("cls,call,key,row,absent", SITES, ids=IDS)
@pytest.mark.parametrize("answer,expected", ANSWERS, ids=["absent", "null", "empty", "rows"])
def test_each_site_records_what_egeria_sent(monkeypatch, cls, call, key, row, absent, answer, expected):
    c = _client(cls, monkeypatch, lambda sent: answer(key, row))
    with recording_list_requests() as record:
        _outcome(call(c))
    assert record["page"] == expected


@pytest.mark.parametrize("cls,call,key,row,absent", SITES, ids=IDS)
@pytest.mark.parametrize("answer,_", ANSWERS, ids=["absent", "null", "empty", "rows"])
def test_public_return_is_unchanged_by_recording(monkeypatch, cls, call, key, row, absent, answer, _):
    c = _client(cls, monkeypatch, lambda sent: answer(key, row))
    plain = _outcome(call(c))
    assert LIST_REQUEST_RECORD.get() is None
    with recording_list_requests():
        recorded = _outcome(call(c))
    assert recorded == plain


@pytest.mark.parametrize("cls,call,key,row,absent", SITES, ids=IDS)
def test_public_returns_are_pinned(monkeypatch, cls, call, key, row, absent):
    # The ruling: no public un-collapse in this work. [] still reads "No elements found", and an absent key
    # reads as each site always answered it.
    c = _client(cls, monkeypatch, lambda sent: {key: []})
    assert asyncio.run(call(c)) == NO_ELEMENTS_FOUND
    c = _client(cls, monkeypatch, lambda sent: {})
    assert asyncio.run(call(c)) == absent
    c = _client(cls, monkeypatch, lambda sent: {key: [row]})
    assert asyncio.run(call(c)) == [row]


# The pager reads the record, so a collapsing method's filtered page is not the end.

def _paged_server(pages):
    """Egeria paging by startFrom: `pages` maps startFrom to the raw `elements` value; unlisted is null."""
    def answer(sent):
        start = sent.get("startFrom", 0)
        return {"elements": pages[start]} if start in pages else {}
    return answer


def test_pager_carries_on_through_a_collapsed_empty_page(monkeypatch):
    # find_metadata_elements collapses [] to "No elements found"; without the record the pager would stop at 0.
    c = _client(MetadataExpert, monkeypatch, _paged_server({0: [], 1: [TOPIC]}))

    async def fetch(start, size):
        return await c._async_find_metadata_elements(
            body={"class": "FindRequestBody", "metadataElementTypeName": "Topic", "startFrom": start,
                  "pageSize": size})

    r = asyncio.run(async_page_all(fetch, fetch_page_size=1, end_policy="trusted"))
    assert [e["elementGUID"] for e in r.items] == ["00daa9fb"] and r.end == "confirmed"


def test_without_a_record_the_string_still_reads_as_null():
    # A fetch that isn't a pyegeria list call records nothing: its value is read as it is.
    r = page_all(lambda start, size: NO_ELEMENTS_FOUND, end_policy="trusted")
    assert r.items == [] and r.end == "confirmed"


def test_sync_wrapper_run_on_the_background_loop_still_records(monkeypatch):
    # Sync methods run their coroutine on pyegeria's background loop; the record must still reach the pager.
    c = _client(MetadataExpert, monkeypatch, _paged_server({0: [], 1: [TOPIC]}))

    def fetch(start, size):
        return c.find_metadata_elements(body={"class": "FindRequestBody", "metadataElementTypeName": "Topic",
                                              "startFrom": start, "pageSize": size})

    r = page_all(fetch, fetch_page_size=1, end_policy="trusted")
    assert [e["elementGUID"] for e in r.items] == ["00daa9fb"] and r.end == "confirmed"


def test_an_outer_recording_still_gets_the_last_request(monkeypatch):
    # exec_report_spec reads its own record (cap, depth) around the call; the pager's inner record merges up.
    c = _client(MetadataExpert, monkeypatch, _paged_server({0: [TOPIC]}))

    async def fetch(start, size):
        return await c._async_find_metadata_elements(
            body={"class": "FindRequestBody", "metadataElementTypeName": "Topic", "startFrom": start,
                  "pageSize": size, "graphQueryDepth": 0})

    with recording_list_requests() as outer:
        asyncio.run(async_page_all(fetch, fetch_page_size=1, end_policy="trusted"))
    assert outer["page"] == "null"                # the last request: startFrom 1, the end
    assert outer["graph_query_depth"] == 0
