# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""delete_saved_query (6.2.35): deleting a SavedQuery detaches its SmartQuery links first, so no Results Set is left
linked to a query that no longer exists, and a link Egeria would not let go of stops the delete with the reason.

The related elements below have the shape Egeria returns from get_related_elements (checked live on 2026-11-09,
tests/micro-tests/dashboard_fake_egeria.py): {elementHeader, relatedBy: {relationshipHeader,
relationshipProperties}, properties}, with the Results Set at end 1 of SmartQuery and the SavedQuery at end 2.
"""
import pytest

from pyegeria.view.saved_query import delete_saved_query

pytestmark = pytest.mark.unit

SQ = "5a7e0000-0000-0000-0000-0000000000a1"


def _results_set(guid):
    return {"class": "OpenMetadataRootElement",
            "elementHeader": {"class": "ElementHeader", "guid": guid,
                              "type": {"typeName": "ResultsSet", "superTypeNames": ["Collection", "Referenceable"]}},
            "relatedBy": {"relationshipHeader": {"guid": f"rel-{guid}", "type": {"typeName": "SmartQuery"}},
                          "relationshipProperties": {"class": "SmartQueryProperties", "typeName": "SmartQuery"}},
            "properties": {"typeName": "ResultsSet", "qualifiedName": f"ResultsSet::{guid}"}}


class _Client:
    """Records every call; a SmartQuery read pages through `linked`; the element read is a `kind`."""

    def __init__(self, linked=(), detach_error=None, kind="SavedQuery", read_error=None):
        self.linked, self.detach_error, self.calls = list(linked), detach_error, []
        self.kind, self.read_error = kind, read_error

    def get_asset_by_guid(self, guid, graph_query_depth=3, output_format="JSON", **kw):
        self.calls.append(("read", guid))
        if self.read_error:
            raise self.read_error
        if self.kind is None:
            return "No elements found"
        return {"elementHeader": {"guid": guid, "type": {"typeName": self.kind, "superTypeNames": ["Asset"]}},
                "properties": {"qualifiedName": f"{self.kind}::{guid}"}}

    def get_related_elements(self, guid, relationship_type=None, start_at_end=1, start_from=0, page_size=0, **kw):
        self.calls.append(("related", guid, relationship_type, start_at_end, start_from))
        page = self.linked[start_from:start_from + page_size]
        return [_results_set(g) for g in page] or "No elements found"

    def detach_smart_query(self, results_set_guid, saved_query_guid, body=None):
        self.calls.append(("detach", results_set_guid, saved_query_guid))
        if self.detach_error:
            raise self.detach_error

    def delete_asset(self, guid, body=None):
        self.calls.append(("delete", guid))


def test_every_smart_query_link_is_detached_before_the_saved_query_is_deleted():
    client = _Client(linked=["rs-1", "rs-2"])
    out = delete_saved_query(client, SQ)
    assert client.calls == [("read", SQ),
                            ("related", SQ, "SmartQuery", 2, 0), ("related", SQ, "SmartQuery", 2, 50),
                            ("detach", "rs-1", SQ), ("detach", "rs-2", SQ),
                            ("delete", SQ)]
    assert out == {"deleted": SQ, "detached": ["rs-1", "rs-2"], "results_sets_kept": ["rs-1", "rs-2"]}


def test_a_saved_query_with_no_results_set_is_just_deleted():
    client = _Client()
    out = delete_saved_query(client, SQ)
    assert [c[0] for c in client.calls] == ["read", "related", "delete"] and out["detached"] == []


def test_a_link_egeria_will_not_detach_stops_the_delete_and_says_why():
    client = _Client(linked=["rs-1"], detach_error=RuntimeError("OMAG-GENERIC-HANDLERS-403-005"))
    with pytest.raises(RuntimeError, match=r"Results Set rs-1 could not be detached .*403-005.*not deleted"):
        delete_saved_query(client, SQ)
    assert ("delete", SQ) not in client.calls


def test_a_guid_is_required():
    with pytest.raises(ValueError):
        delete_saved_query(_Client(), "")


# the Architect's 6.2.35 read-back: only a SavedQuery is deleted, and every link is read

@pytest.mark.parametrize("kind", ["UserIdentity", "Report", "Collection"])
def test_a_guid_that_is_not_a_saved_query_is_refused_and_nothing_is_deleted(kind):
    client = _Client(linked=["rs-1"], kind=kind)
    with pytest.raises(RuntimeError, match=rf"is a {kind}, not a SavedQuery; nothing was deleted"):
        delete_saved_query(client, SQ)
    assert [c[0] for c in client.calls] == ["read"]


def test_a_guid_that_finds_nothing_or_cannot_be_read_is_refused():
    with pytest.raises(RuntimeError, match="is not found, not a SavedQuery"):
        delete_saved_query(_Client(kind=None), SQ)
    client = _Client(read_error=RuntimeError("HTTP 500"))
    with pytest.raises(RuntimeError, match="could not be read .*HTTP 500.*not deleted"):
        delete_saved_query(client, SQ)
    assert [c[0] for c in client.calls] == ["read"]


def test_links_are_read_until_an_empty_page_not_a_short_one():
    rs = [f"rs-{i}" for i in range(120)]           # a full page, a full page, a short page, then the empty one
    client = _Client(linked=rs)
    out = delete_saved_query(client, SQ)
    assert [c[4] for c in client.calls if c[0] == "related"] == [0, 50, 100, 150]
    assert out["detached"] == rs and client.calls[-1] == ("delete", SQ)


def test_more_links_than_the_bound_is_refused_with_nothing_detached(monkeypatch):
    from pyegeria.view import saved_query as sq
    monkeypatch.setattr(sq, "DELETE_LINK_MAX_PAGES", 2)
    client = _Client(linked=[f"rs-{i}" for i in range(100)])
    with pytest.raises(RuntimeError, match="more than 100 SmartQuery links; refused"):
        delete_saved_query(client, SQ)
    assert not [c for c in client.calls if c[0] in ("detach", "delete")]
