"""W1: a Report pins its collection by qualifiedName, not GUID.

The "Collection Members" report spec required collection_guid, so a Report had to hard-code a GUID, and it
broke (CLIENT_ERROR_400) once the collection was re-created. The spec now takes any one of collection_guid,
collection_qname or collection_name, and get_collection_members resolves a name at run time. A name that
matches nothing raises PyegeriaNotFoundException (relatedHTTPCode 404) naming the collection; it used to
surface as "Neither server_guid nor server_name were provided" (qualifiedName) or as a request for the
GUID "No elements found" (display name).
"""
import asyncio

import pytest

from pyegeria.core._exceptions import PyegeriaInvalidParameterException, PyegeriaNotFoundException
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.view.base_report_formats import get_report_registry

QN = "Coco Pharmaceuticals::WorkItemList::Local-Dashboards---Next-Steps::1.0"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(CollectionManager, "check_connection", lambda self: "test")
    c = CollectionManager("view-server", "https://localhost:1", "user", "pwd")
    c.lookups = []
    c.requests = []

    async def fake_lookup(guid=None, display_name=None, property_name="qualifiedName", qualified_name=None,
                          tech_type=None, organization_name=None, for_lineage=False):
        c.lookups.append((property_name, qualified_name or display_name))
        known = {("qualifiedName", QN): "coll-guid-1", ("displayName", "Local Dashboards - Next Steps"): "coll-guid-1"}
        if qualified_name:
            if ("qualifiedName", qualified_name) in known:
                return known[("qualifiedName", qualified_name)]
            if display_name is None:   # the real helper's fall-through when a qualifiedName isn't found
                raise PyegeriaInvalidParameterException(None, None, {"reason": "Neither server_guid nor server_name were provided"})
        return known.get(("displayName", display_name), NO_ELEMENTS_FOUND)

    async def fake_results(url, **kwargs):
        c.requests.append(url)
        return [{"guid": "member-1"}]

    monkeypatch.setattr(c, "_ServerClient__async_get_guid__", fake_lookup, raising=False)
    monkeypatch.setattr(c, "__async_get_guid__", fake_lookup, raising=False)
    monkeypatch.setattr(c, "_async_get_results_body_request", fake_results)
    return c


def _members(c, **kw):
    return asyncio.run(c._async_get_collection_members(output_format="JSON", **kw))


def test_members_by_qualified_name(client):
    assert _members(client, collection_qname=QN) == [{"guid": "member-1"}]
    assert client.requests[-1].endswith("/collections/coll-guid-1/members")
    assert client.lookups == [("qualifiedName", QN)]


def test_members_by_display_name(client):
    _members(client, collection_name="Local Dashboards - Next Steps")
    assert client.requests[-1].endswith("/collections/coll-guid-1/members")


def test_a_guid_is_used_as_given(client):
    _members(client, collection_guid="g-direct")
    assert client.requests[-1].endswith("/collections/g-direct/members")
    assert client.lookups == []


@pytest.mark.parametrize("kw, named", [
    ({"collection_qname": "Coco Pharmaceuticals::WorkItemList::Gone::1.0"}, "Coco Pharmaceuticals::WorkItemList::Gone::1.0"),
    ({"collection_name": "Gone"}, "Gone"),
])
def test_a_name_that_matches_nothing_is_not_found_and_never_requested(client, kw, named):
    with pytest.raises(PyegeriaNotFoundException) as info:
        _members(client, **kw)
    assert info.value.related_http_code == 404
    assert named in str(info.value)
    assert client.requests == [], "no members request with a made-up GUID"


def test_nothing_given_is_an_invalid_parameter(client):
    with pytest.raises(PyegeriaInvalidParameterException, match="collection_qname"):
        _members(client)


def test_the_report_spec_accepts_a_qualified_name():
    action = get_report_registry()["Collection Members"].action
    assert action.required_params == []
    for p in ("collection_guid", "collection_qname", "collection_name"):
        assert p in action.optional_params


def test_exec_report_spec_passes_the_qualified_name_through(monkeypatch):
    """The dashboard path: a Report's flat params reach get_collection_members unchanged."""
    import pyegeria.view.format_set_executor as fse
    calls = []

    class _Fake:
        def __init__(self, *a, **k): pass
        def create_egeria_bearer_token(self, *a, **k): return "token"
        def set_bearer_token(self, token): pass
        def close_session(self): pass
        def get_collection_members(self, collection_guid=None, collection_name=None, collection_qname=None,
                                   body=None, start_from=0, page_size=0, output_format="JSON", report_spec=None, **kw):
            calls.append({"collection_guid": collection_guid, "collection_qname": collection_qname,
                          "collection_name": collection_name})
            return [{"guid": "member-1"}]

    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_Fake, decl.split(".")[-1]))
    fse.exec_report_spec("Collection Members", output_format="DICT", params={"collection_qname": QN},
                         view_server="v", view_url="https://x", user="u", user_pass="p")
    assert calls == [{"collection_guid": None, "collection_qname": QN, "collection_name": None}]
