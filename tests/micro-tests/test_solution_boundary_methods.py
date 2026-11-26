# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
The 7 solution-boundary requests of odpi/egeria#9465 (SolutionArchitect): what each method sends, with `_async_make_request`
replaced by a recorder, so no platform is involved. The URLs and the one request body class are the ones read in odpi/egeria
main 2e22b1e85b (SolutionArchitectResource: POST /solution-boundaries, /from-template, /{guid}/update, /{guid}/delete,
/by-name, /{guid}/retrieve, /by-search-string).

Response bodies are SYNTHETIC (a guid, or an element with an elementHeader and properties): no platform in reach has the feature
yet, so nothing here claims a live answer. Only what the client SENDS is asserted.
"""
import inspect
import json

import pytest

from pyegeria import SolutionArchitect
from pyegeria.core._exceptions import PyegeriaInvalidParameterException

ROOT = "/servers/view-server/api/open-metadata/solution-architect/solution-boundaries"
GUID = "11111111-2222-3333-4444-555555555555"

METHODS = ["create_solution_boundary", "create_solution_boundary_from_template", "update_solution_boundary",
           "delete_solution_boundary", "find_solution_boundaries", "get_solution_boundary_by_guid",
           "get_solution_boundaries_by_name"]


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(monkeypatch, payload=None):
    monkeypatch.setattr(SolutionArchitect, "check_connection", lambda self: "test", raising=False)
    client = SolutionArchitect("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload_=None, *args, **kwargs):
        calls.append((method, url, json.loads(payload_) if isinstance(payload_, str) else payload_))
        return _Response(payload if payload is not None else {"relatedHTTPCode": 200, "guid": GUID})

    client._async_make_request = fake_make_request
    return client, calls


def _new_body(class_name="SolutionBoundaryProperties"):
    return {"class": "NewElementRequestBody", "properties": {"class": class_name, "qualifiedName": "Boundary::A", "displayName": "A"}}


def test_every_request_has_an_async_and_a_sync_method():
    for name in METHODS:
        assert inspect.iscoroutinefunction(getattr(SolutionArchitect, "_async_" + name)), name
        assert not inspect.iscoroutinefunction(getattr(SolutionArchitect, name)), name


def test_create_posts_to_solution_boundaries_with_the_boundary_class(monkeypatch):
    client, calls = _client(monkeypatch)
    assert client.create_solution_boundary(_new_body()) == GUID
    method, url, body = calls[-1]
    assert method == "POST" and url.endswith(ROOT)
    assert body["properties"]["class"] == "SolutionBoundaryProperties"


def test_create_and_update_name_the_boundary_properties_class_to_the_helper(monkeypatch):
    # the helpers do not reject another class in a dict body (blueprints behave the same), so what this pins is that the
    # METHOD names the boundary class as the one expected, not a blueprint's
    client, _ = _client(monkeypatch)
    seen = []

    async def spy_create(url, classes, body):
        seen.append(("create", classes))
        return GUID

    async def spy_update(url, classes, body):
        seen.append(("update", classes))

    client._async_create_element_body_request = spy_create
    client._async_update_element_body_request = spy_update
    client.create_solution_boundary(_new_body())
    client.update_solution_boundary(GUID, {"class": "UpdateElementRequestBody"})
    assert seen == [("create", ["SolutionBoundaryProperties"]), ("update", ["SolutionBoundaryProperties"])]


def test_create_from_template_posts_to_its_own_url(monkeypatch):
    client, calls = _client(monkeypatch)
    body = {"class": "TemplateRequestBody", "templateGUID": GUID, "isOwnAnchor": True,
            "replacementProperties": {"class": "ElementProperties", "propertyValueMap": {}}}
    client.create_solution_boundary_from_template(body)
    method, url, sent = calls[-1]
    assert method == "POST" and url.endswith(ROOT + "/from-template") and sent["templateGUID"] == GUID


def test_update_posts_to_the_guid_update_url(monkeypatch):
    client, calls = _client(monkeypatch)
    body = {"class": "UpdateElementRequestBody", "properties": {"class": "SolutionBoundaryProperties",
            "qualifiedName": "Boundary::A", "displayName": "A2"}}
    client.update_solution_boundary(GUID, body)
    method, url, sent = calls[-1]
    assert method == "POST" and url.endswith(f"{ROOT}/{GUID}/update")
    assert sent["properties"]["displayName"] == "A2"


def test_delete_posts_to_the_guid_delete_url_and_sends_what_a_blueprint_delete_sends(monkeypatch):
    client, calls = _client(monkeypatch)
    client.delete_solution_boundary(GUID, cascade_delete=True)
    client.delete_solution_blueprint(GUID, cascade_delete=True)
    (m1, url1, body1), (m2, url2, body2) = calls[-2], calls[-1]
    assert m1 == "POST" and url1.endswith(f"{ROOT}/{GUID}/delete")
    assert body1 == body2        # the same DeleteElementRequestBody; the cascade field is the one the shared helper sends
    assert url2.endswith(f"/solution-blueprints/{GUID}/delete")


def test_find_posts_the_search_string_to_by_search_string(monkeypatch):
    client, calls = _client(monkeypatch, {"elements": []})
    client.find_solution_boundaries("Core*", output_format="JSON")
    method, url, body = calls[-1]
    assert method == "POST" and f"{ROOT}/by-search-string" in url
    assert "Core*" in json.dumps(body)


def test_get_by_guid_asks_for_the_graph_with_an_any_time_body(monkeypatch):
    # SYNTHETIC element: an elementHeader and properties, no relationships
    element = {"elementHeader": {"guid": GUID, "type": {"typeName": "SolutionBoundary"}}, "properties": {"displayName": "A"}}
    client, calls = _client(monkeypatch, {"element": element})
    got = client.get_solution_boundary_by_guid(GUID, graph_query_depth=4, max_mermaid_node_count=20)
    method, url, body = calls[-1]
    assert method == "POST" and url.endswith(f"{ROOT}/{GUID}/retrieve")
    assert body["class"] == "AnyTimeRequestBody" and body["graphQueryDepth"] == 4 and body["maxMermaidNodeCount"] == 20
    assert got == element


def test_get_by_guid_accepts_the_named_keyword(monkeypatch):
    client, calls = _client(monkeypatch, {"element": {"elementHeader": {"guid": GUID}}})
    client.get_solution_boundary_by_guid(solution_boundary_guid=GUID)
    assert calls[-1][1].endswith(f"{ROOT}/{GUID}/retrieve")


def test_by_name_posts_the_name_filter(monkeypatch):
    client, calls = _client(monkeypatch, {"elements": []})
    client.get_solution_boundaries_by_name("Core Boundary")
    method, url, body = calls[-1]
    assert method == "POST" and url.endswith(ROOT + "/by-name") and body["filter"] == "Core Boundary"


@pytest.mark.parametrize("call", [
    lambda c: c.get_solution_boundary_by_guid(None),
    lambda c: c.delete_solution_boundary(""),
    lambda c: c.update_solution_boundary(None, {"class": "UpdateElementRequestBody"}),
])
def test_a_missing_guid_is_refused_before_anything_is_sent(monkeypatch, call):
    client, calls = _client(monkeypatch)
    with pytest.raises(PyegeriaInvalidParameterException):
        call(client)
    assert not calls


# ── output formats (the formatter and extractor added with the methods; SYNTHETIC element) ──────────────

_ELEMENT = {"elementHeader": {"guid": GUID, "status": "ACTIVE", "type": {"typeName": "SolutionBoundary", "typeId": "t-1"},
                              "origin": {"originCategory": "LOCAL_COHORT", "homeMetadataCollectionId": "mc-1",
                                         "homeMetadataCollectionName": "store"},
                              "versions": {"createdBy": "user", "createTime": "2026-11-25T00:00:00.000+00:00", "version": 1}},
            "properties": {"class": "SolutionBoundaryProperties", "qualifiedName": "Boundary::A", "displayName": "A",
                           "description": "d"},
            "mermaidGraph": "flowchart LR\n  a-->b"}


def test_json_output_is_the_element_untouched(monkeypatch):
    client, _ = _client(monkeypatch, {"element": _ELEMENT})
    assert client.get_solution_boundary_by_guid(GUID, output_format="JSON") == _ELEMENT


def test_mermaid_output_is_the_graph_only(monkeypatch):
    client, _ = _client(monkeypatch)
    out = client.generate_solution_boundary_output(_ELEMENT, GUID, "SolutionBoundary", "MERMAID")
    assert "flowchart LR" in str(out) and "Boundary::A" not in str(out)


def test_dict_output_reads_the_common_columns(monkeypatch):
    # The boundary's own report spec comes in the next change of the stack; the existing Solution-Blueprint spec has the same
    # common columns, so it is used here only to exercise the extractor on a SYNTHETIC boundary element.
    client, _ = _client(monkeypatch)
    rows = client.generate_solution_boundary_output(_ELEMENT, GUID, "SolutionBoundary", "DICT", report_spec="Solution-Blueprint")
    assert rows[0]["Display Name"] == "A" and rows[0]["Qualified Name"] == "Boundary::A"
    assert rows[0]["Type Name"] == "SolutionBoundary" and rows[0]["Created By"] == "user"
