"""Pager step 5, the exists-lookups ruling (2026-11-14): found / absent / unknown, and write guards that never
create on unknown."""
import asyncio
from typing import Any, Dict, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.core import paging
from pyegeria.core._exceptions import PyegeriaException, PyegeriaNotFoundException

pytestmark = pytest.mark.unit

NULL = NO_ELEMENTS_FOUND


# ── async_exists / exists ──

def test_found_stops_at_the_first_page_with_a_match():
    calls = []

    def fetch(start, size):
        calls.append(start)
        return [{"guid": f"g{start}"}]

    r = paging.exists(fetch, lambda row: row["guid"] == "g100", method="get_collection_members")
    assert r.answer == "found" and r.found and r.matches == [{"guid": "g100"}] and calls == [0, 100]


def test_absent_only_when_the_read_reached_the_end():
    r = paging.exists(lambda s, n: NULL, lambda row: True, method="get_collection_members")
    assert r.answer == "absent" and r.read.end_reason == "null_then_empty_probes"


@pytest.mark.parametrize("method", sorted(paging.NULL_NOT_END_METHODS))
def test_a_null_not_end_method_is_never_absent(method):
    r = paging.exists(lambda s, n: NULL, lambda row: True, method=method)
    assert r.answer == "unknown" and "Egeria didn't confirm there are no more" in r.words("X")


def test_a_limit_is_unknown_and_max_pages_is_bounded():
    r = paging.exists(lambda s, n: [], lambda row: True, method="get_collection_members", max_pages=3)
    assert r.answer == "unknown" and r.read.end_reason == "max_pages"
    with pytest.raises(ValueError):
        paging.exists(lambda s, n: NULL, lambda row: True, method=None, max_pages=paging.EXISTS_MAX_PAGES + 1)


def test_async_exists_matches_exactly_client_side():
    async def fetch(start, size):
        return [{"properties": {"qualifiedName": "Q::1x"}}, {"properties": {"qualifiedName": "Q::1"}}] if start == 0 \
            else NULL

    r = asyncio.run(paging.async_exists(fetch, lambda el: el["properties"]["qualifiedName"] == "Q::1",
                                        method="get_collection_members"))
    assert r.answer == "found" and len(r.matches) == 1


# ── the three-way guid lookup, and the journal-entry write guard ──

class _Client:
    """ServerClient's own methods, with a fake by-property-value read."""

    def __init__(self, pages: Dict[int, Any]):
        self.pages, self.created = pages, []

    async def _async_get_elements_by_property_value(self, name, props, type_name=None, start_from=0, page_size=0,
                                                    **kw):
        return self.pages.get(start_from, NULL)

    async def _async_create_note_log(self, element_guid=None, display_name=None, **kw):
        self.created.append(display_name)
        return "new-note-log"

    async def _async_create_note(self, *a, **kw):
        return "note-guid"


def _bind(client):
    from pyegeria.core._server_client import ServerClient
    for name in ("_async_lookup_guid_for_name", "_async_add_journal_entry"):
        setattr(client, name, getattr(ServerClient, name).__get__(client))
    return client


def _el(qn, guid="g1"):
    return {"elementHeader": {"guid": guid}, "properties": {"qualifiedName": qn}}


def test_lookup_guid_for_name_is_three_way():
    c = _bind(_Client({0: [_el("NoteLog::a")]}))
    found = asyncio.run(c._async_lookup_guid_for_name("NoteLog::a", ["qualifiedName"], "NoteLog"))
    assert found.answer == "found" and found.matches[0]["elementHeader"]["guid"] == "g1"
    nothing = asyncio.run(_bind(_Client({}))._async_lookup_guid_for_name("NoteLog::a", ["qualifiedName"]))
    assert nothing.answer == "unknown"   # by-property-value is NULL_NOT_END: never "absent" today


def test_lookup_guid_for_name_still_refuses_two_matches():
    c = _bind(_Client({0: [_el("Q", "g1"), _el("Q", "g2")]}))
    with pytest.raises(PyegeriaException):
        asyncio.run(c._async_lookup_guid_for_name("Q", ["qualifiedName"]))


def test_a_journal_entry_never_creates_a_note_log_on_an_unknown_lookup():
    c = _bind(_Client({}))
    with pytest.raises(PyegeriaException) as exc:
        asyncio.run(c._async_add_journal_entry(note_log_qn="NoteLog::a", note_entry="x"))
    assert c.created == [] and "can't tell whether it exists" in str(exc.value.context)


def test_a_journal_entry_uses_the_note_log_it_found():
    c = _bind(_Client({0: [_el("NoteLog::a", "nl-1")]}))
    asyncio.run(c._async_add_journal_entry(note_log_qn="NoteLog::a", note_entry="x"))
    assert c.created == []
