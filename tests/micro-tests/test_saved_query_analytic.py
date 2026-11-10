# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Route B (6.2.34): `saved_query`, a saved query as the source of a Report.

The SavedQuery below has the shape the Portal's insights_handler writes (create_saved_query) and a find
returns (an OpenMetadataElement):
- a queryURL that is absolute, on this platform and view server;
- a queryRequestBody that is a JSON string;
- additionalProperties (a map value) carrying resultsSetGuid and lastRefreshedTime.

The security tests prove that the stored URL never chooses where the viewer's token goes. Every refused
URL leaves the fake with exactly one call: the lookup. The fake has no other way to reach anything.
Nothing reaches Egeria.
"""
import json

import pytest

from pyegeria.view import saved_query as sq
from pyegeria.view.saved_query import saved_query

pytestmark = pytest.mark.unit

PLATFORM, VIEW = "https://localhost:9443", "qs-view-server"
ENDPOINT = "/api/open-metadata/metadata-expert/metadata-elements/by-search-conditions"
PORTAL_URL = f"{PLATFORM}/servers/{VIEW}{ENDPOINT}"
QN = "SavedQuery::insights-query::Assets with no lineage::a1b2"
QUERY_BODY = {"class": "FindRequestBody", "metadataElementTypeName": "Asset", "limitResultsByStatus": ["ACTIVE"],
              "graphQueryDepth": 0, "startFrom": 0, "pageSize": 500}
GE = "≥"


def _str(v):
    return {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": v}


def _saved_query(query_url=PORTAL_URL, body=json.dumps(QUERY_BODY), refreshed="2026-11-10T18:02:11+00:00",
                 results_set="rs-guid", qn=QN):
    additional = {"pyegeriaInsightsQuery": "true", "queryUrl": "/api/insights/search", "queryHttpMethod": "POST",
                  "resultsSetGuid": results_set or "", "lastRefreshedTime": refreshed or "", "resultCount": ""}
    pvm = {"qualifiedName": _str(qn), "displayName": _str("Assets with no lineage"),
           "formula": _str(json.dumps({"type_name": "Asset"})), "formulaType": _str("egeria-insights-search-v1"),
           "additionalProperties": {"class": "MapTypePropertyValue", "mapValues": {
               "class": "InstanceProperties", "propertyValueMap": {k: _str(v) for k, v in additional.items()}}}}
    if query_url is not None:
        pvm["queryURL"] = _str(query_url)
    if body is not None:
        pvm["queryRequestBody"] = _str(body)
    return {"elementGUID": "sq-guid", "type": {"typeName": "SavedQuery"},
            "elementProperties": {"class": "ElementProperties", "propertyValueMap": pvm}}


def _element(i, type_name="DataSet"):
    return {"elementGUID": f"g{i}", "type": {"typeName": type_name},
            "elementProperties": {"propertyValueMap": {"qualifiedName": _str(f"Asset::{i}"),
                                                       "displayName": _str(f"Asset {i}")}}}


def _member(i):
    return {"elementHeader": {"guid": f"m{i}", "type": {"typeName": "DataSet"}},
            "properties": {"qualifiedName": f"Asset::{i}", "displayName": f"Asset {i}"}}


class _Viewer:
    """The viewer's own client. Records every call; it is the only way anything is reached."""
    platform_url, view_server = PLATFORM, VIEW

    def __init__(self, stored=None, answer=0, members=0, lookup_error=None, run_error=None):
        self.stored = [_saved_query()] if stored is None else stored
        self.answer, self.members = answer, members
        self.lookup_error, self.run_error = lookup_error, run_error
        self.calls = []

    def find_metadata_elements(self, body=None, **kw):
        self.calls.append(("find", json.loads(json.dumps(body))))
        if body.get("metadataElementTypeName") == "SavedQuery":
            if self.lookup_error:
                raise self.lookup_error
            return self.stored or "No elements found"
        if self.run_error:
            raise self.run_error
        start, size = body["startFrom"], body["pageSize"]
        page = [_element(i) for i in range(start, min(start + size, self.answer))]
        return page or "No elements found"

    def get_collection_members(self, collection_guid=None, start_from=0, page_size=0, output_format="JSON", **kw):
        self.calls.append(("members", collection_guid, start_from, page_size))
        page = [_member(i) for i in range(start_from, min(start_from + page_size, self.members))]
        return page or "No elements found"


# ── cached ──

def test_cached_count_is_the_results_set_as_of_its_refresh():
    viewer = _Viewer(members=37)
    out = saved_query(viewer, QN)
    assert out["value"] == 37 and out["display"] == "37" and out["state"] == "measured"
    assert out["asOf"] == "2026-11-10T18:02:11+00:00"
    assert out["subtitle"] == "as of 2026-11-10T18:02:11+00:00"
    assert [c[0] for c in viewer.calls] == ["find", "members", "members"]  # paged to the empty page
    assert viewer.calls[1][1] == "rs-guid"


def test_cached_list_names_each_member():
    out = saved_query(_Viewer(members=2), QN, output="list")
    assert out["elements"] == [
        {"guid": "m0", "typeName": "DataSet", "qualifiedName": "Asset::0", "displayName": "Asset 0"},
        {"guid": "m1", "typeName": "DataSet", "qualifiedName": "Asset::1", "displayName": "Asset 1"}]


def test_never_refreshed_is_not_an_empty_answer():
    viewer = _Viewer(stored=[_saved_query(refreshed="")], members=0)
    out = saved_query(viewer, QN)
    assert out["value"] is None and out["state"] == "not_established" and out["absence"] == "not_measured"
    assert "never been refreshed" in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


def test_an_empty_refreshed_answer_is_nothing_found():
    out = saved_query(_Viewer(members=0), QN)
    assert out["value"] == 0 and out["state"] == "nothing_found"


def test_a_cached_read_stopped_at_its_bound_is_a_lower_bound():
    out = saved_query(_Viewer(members=50), QN, page_size=10, max_pages=3)
    assert out["value"] is None and out["capped"] is True and out["atLeast"] == 30
    assert out["display"] == f"{GE}30"
    assert "at least 30" in out["subtitle"]


def test_no_results_set_is_said():
    out = saved_query(_Viewer(stored=[_saved_query(results_set="")]), QN)
    assert out["state"] == "not_established" and "no Results Set" in out["state_reason"]


# ── finding the saved query, as the viewer ──

def test_the_lookup_is_an_exact_qualified_name_find_of_a_saved_query():
    viewer = _Viewer(members=1)
    saved_query(viewer, QN)
    body = viewer.calls[0][1]
    assert body["metadataElementTypeName"] == "SavedQuery"
    cond = body["searchProperties"]["conditions"][0]
    assert (cond["property"], cond["operator"], cond["value"]["primitiveValue"]) == ("qualifiedName", "EQ", QN)


def test_a_missing_saved_query_is_not_a_zero():
    out = saved_query(_Viewer(stored=[]), QN)
    assert out["value"] is None and out["state"] == "not_established"
    assert "no saved query named" in out["state_reason"]


def test_a_near_miss_qualified_name_is_not_taken():
    out = saved_query(_Viewer(stored=[_saved_query(qn=QN + "-copy")]), QN)
    assert out["value"] is None and "no saved query named" in out["state_reason"]


def test_a_saved_query_in_a_hidden_zone_is_not_permitted():
    err = RuntimeError("OPEN-METADATA-SECURITY-403-020 The element sq-guid is not visible to user erinoverview")
    out = saved_query(_Viewer(lookup_error=err), QN)
    assert out["state"] == "not_established" and out["absence"] == "not_permitted" and out["value"] is None


# ── live ──

def test_live_runs_the_stored_body_through_pyegeria_paging_to_the_end():
    viewer = _Viewer(answer=1200)
    out = saved_query(viewer, QN, mode="live")
    assert out["value"] == 1200 and out["display"] == "1200" and out["capped"] is False
    runs = [c[1] for c in viewer.calls[1:]]
    assert [b["startFrom"] for b in runs] == [0, 500, 1000, 1200]
    assert all(b["metadataElementTypeName"] == "Asset" and b["limitResultsByStatus"] == ["ACTIVE"] for b in runs)
    assert out["asOf"]  # now


def test_live_stopped_at_its_bound_is_marked_never_a_total():
    out = saved_query(_Viewer(answer=10_000), QN, mode="live", page_size=100, max_pages=4)
    assert out["value"] is None and out["capped"] is True and out["atLeast"] == 400
    assert out["display"] == f"{GE}400"


def test_live_list_output():
    out = saved_query(_Viewer(answer=3), QN, mode="live", output="list")
    assert [e["guid"] for e in out["elements"]] == ["g0", "g1", "g2"]
    assert out["elements"][0]["qualifiedName"] == "Asset::0"


def test_a_live_request_egeria_refuses_is_not_permitted():
    err = RuntimeError("OPEN-METADATA-SECURITY-403-020 not visible to user erinoverview")
    out = saved_query(_Viewer(run_error=err), QN, mode="live")
    assert out["absence"] == "not_permitted" and out["value"] is None


def test_a_live_request_that_fails_is_not_measured():
    out = saved_query(_Viewer(run_error=TimeoutError("timed out")), QN, mode="live")
    assert out["absence"] == "not_measured" and out["value"] is None and "TimeoutError" in out["state_reason"]


# ── the allow-list: a stored URL never chooses where the token goes ──

@pytest.mark.parametrize("url", [
    PORTAL_URL,                                   # the Portal's own shape: this platform, this view server
    ENDPOINT,                                     # relative to the view server
    ENDPOINT.lstrip("/"),
    f"/servers/{VIEW}{ENDPOINT}",
    PORTAL_URL.replace("https://localhost", "HTTPS://LOCALHOST"),
])
def test_allow_listed_requests_run(url):
    viewer = _Viewer(stored=[_saved_query(query_url=url)], answer=2)
    out = saved_query(viewer, QN, mode="live")
    assert out["value"] == 2 and "refused" not in out


REFUSED = [
    ("https://evil.example.com/servers/qs-view-server" + ENDPOINT, "names https://evil.example.com"),
    ("https://evil.example.com" + ENDPOINT, "not this platform"),
    ("http://localhost:9443/servers/qs-view-server" + ENDPOINT, "not this platform"),     # scheme downgrade
    ("https://localhost:9444/servers/qs-view-server" + ENDPOINT, "not this platform"),    # another port
    ("https://erin@localhost:9443/servers/qs-view-server" + ENDPOINT, "not this platform"),  # user info
    ("https://localhost:9443@evil.example.com/servers/qs-view-server" + ENDPOINT, "not this platform"),
    ("//evil.example.com/servers/qs-view-server" + ENDPOINT, "not this platform"),        # scheme-relative
    ("ftp://localhost:9443/servers/qs-view-server" + ENDPOINT, "not this platform"),
    ("/servers/another-view-server" + ENDPOINT, "names view server 'another-view-server'"),
    ("/api/open-metadata/metadata-expert/metadata-elements/by-search-string", "not one of the query endpoints"),
    ("/api/open-metadata/asset-maker/assets", "not one of the query endpoints"),
    ("/api/insights/search", "not one of the query endpoints"),                            # the Portal's own API
    ("/api/open-metadata/metadata-expert/../asset-maker/assets", "not a plain endpoint path"),
    ("/api/open-metadata/metadata-expert/metadata-elements/./by-search-conditions", "not a plain endpoint path"),
    ("/api/open-metadata/metadata-expert//metadata-elements/by-search-conditions", "not a plain endpoint path"),
    ("/api/open-metadata/metadata-expert/metadata-elements/%2e%2e/by-search-conditions", "characters"),
    (ENDPOINT + "?pushDown=true", "query string"),
    (ENDPOINT + "#x", "query string or fragment"),
    ("", "no Query URL"),
    (None, "no Query URL"),
]


@pytest.mark.parametrize("url,words", REFUSED)
def test_every_other_url_is_refused_with_a_sentence_and_reaches_nothing(url, words):
    viewer = _Viewer(stored=[_saved_query(query_url=url)], answer=5)
    out = saved_query(viewer, QN, mode="live")
    assert out["refused"] is True and out["value"] is None
    assert out["state"] == "not_established" and out["absence"] == "not_applicable"
    assert words in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]  # the lookup only: the stored request never ran


@pytest.mark.parametrize("body,words", [
    (json.dumps({**QUERY_BODY, "class": "NewElementRequestBody"}), "takes FindRequestBody"),
    ("not json", "not JSON"),
    (None, "no Query Request Body"),
    ("[1, 2]", "no Query Request Body"),
])
def test_a_request_body_that_is_not_a_find_is_refused(body, words):
    viewer = _Viewer(stored=[_saved_query(body=body)], answer=5)
    out = saved_query(viewer, QN, mode="live")
    assert out["refused"] is True and words in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


def test_the_allow_list_is_the_one_find_endpoint():
    assert set(sq.ALLOWED_QUERY_ENDPOINTS) == {ENDPOINT}


def test_bad_arguments_are_errors_not_answers():
    for kw in ({"mode": "both"}, {"output": "chart"}):
        with pytest.raises(ValueError):
            saved_query(_Viewer(), QN, **kw)
    with pytest.raises(ValueError):
        saved_query(_Viewer(), "")


def test_it_is_a_registered_analytic_function():
    from pyegeria.view.analytic_registry import get_analytic_registry
    from pyegeria.view.format_set_executor import resolve_report_spec_function
    spec = get_analytic_registry()["saved_query"]
    assert spec.inputs == ["egeria_client:EgeriaTech"]
    assert resolve_report_spec_function("saved_query") is saved_query


def test_through_the_report_executor_it_runs_on_the_viewers_own_client():
    from pyegeria.view import format_set_executor as fse
    from pyegeria.view.role_supply import Subject, Viewer

    viewer = _Viewer(answer=4)

    class _Supply:
        asked = []

        def client(self, cls):
            self.asked.append(cls.__name__)
            return viewer

        def viewer(self):
            return Viewer(user_id="erinoverview", is_admin=False, display_name="Erin")

        def reader(self, source):
            return None

        def subject(self):
            return Subject(guid="g", type_name="Asset")

        def refusal_words(self, kind):
            return f"cannot supply {kind}"

    supply = _Supply()
    out = fse._run_analytic_function({"analytic_function": "saved_query"},
                                     params={"name": QN, "mode": "live"}, view_server="vs", view_url="https://x",
                                     user="u", user_pass="p", supply=supply)
    assert out["value"] == 4
    assert supply.asked == ["EgeriaTech"]
    assert all(c[0] == "find" for c in viewer.calls)


# ── parameters (brief §9): a saved query as a template ──

PARAMS = json.dumps([{"name": "type_name", "type": "enum", "values": ["Asset", "DataSet", "Process"], "default": "Asset"},
                     {"name": "label", "type": "string"},
                     {"name": "days", "type": "int", "default": 180},
                     {"name": "active", "type": "bool", "default": True}])
TEMPLATE = {"class": "FindRequestBody", "metadataElementTypeName": "{{type_name}}", "limitResultsByStatus": ["ACTIVE"],
            "searchProperties": {"class": "SearchProperties", "matchCriteria": "ALL", "conditions": [
                {"property": "displayName", "operator": "EQ", "value": {"class": "PrimitiveTypePropertyValue",
                                                                       "typeName": "string",
                                                                       "primitiveValue": "{{label}}"}}]},
            "graphQueryDepth": 0}


def _param_query(body=TEMPLATE, params=PARAMS, last=None, url=PORTAL_URL, refreshed="2026-11-10T18:02:11+00:00"):
    el = _saved_query(query_url=url, body=json.dumps(body), refreshed=refreshed)
    amap = el["elementProperties"]["propertyValueMap"]["additionalProperties"]["mapValues"]["propertyValueMap"]
    amap["parameters"] = _str(params)
    if last is not None:
        amap["lastRefreshParams"] = _str(json.dumps(last))
    return el


def _ran(viewer):
    return [c[1] for c in viewer.calls[1:] if c[0] == "find"]


def test_declared_parameters_are_substituted_as_typed_values():
    viewer = _Viewer(stored=[_param_query()], answer=3)
    out = saved_query(viewer, QN, mode="live", params={"type_name": "DataSet", "label": "Sales \"Q4\" {x}"})
    body = _ran(viewer)[0]
    assert body["metadataElementTypeName"] == "DataSet"
    assert body["searchProperties"]["conditions"][0]["value"]["primitiveValue"] == "Sales \"Q4\" {x}"  # data
    assert out["params"] == {"type_name": "DataSet", "label": "Sales \"Q4\" {x}", "days": 180, "active": True}
    assert out["value"] == 3 and "for active=true, days=180, label=" in out["subtitle"]


def test_defaults_apply_and_are_reported():
    viewer = _Viewer(stored=[_param_query(body={**TEMPLATE, "searchProperties": None})], answer=1)
    out = saved_query(viewer, QN, mode="live")
    assert _ran(viewer)[0]["metadataElementTypeName"] == "Asset"
    assert out["params"] == {"type_name": "Asset", "days": 180, "active": True}


def test_an_int_parameter_stays_an_int():
    body = {**TEMPLATE, "searchProperties": None, "pageLimitDays": "{{days}}", "active": "{{active}}"}
    viewer = _Viewer(stored=[_param_query(body=body)], answer=1)
    saved_query(viewer, QN, mode="live", params={"days": "30", "active": "false"})
    sent = _ran(viewer)[0]
    assert sent["pageLimitDays"] == 30 and sent["active"] is False


@pytest.mark.parametrize("given,words", [
    ({"queryURL": "https://evil.example.com/x"}, "does not declare ['queryURL']"),     # a URL, as a name
    ({"../servers/x": "y"}, "does not declare"),                                      # path chars, as a name
    ({"type_name": "Asset/../../asset-maker"}, "takes one of"),                       # path chars, as a value
    ({"type_name": "https://evil.example.com"}, "takes one of"),                      # a URL, as a value
    ({"days": "30; drop"}, "takes an int"),                                           # a type mismatch
    ({"days": True}, "takes an int"),
    ({"days": 1.5}, "takes an int"),
    ({"active": "yes"}, "takes true or false"),
    ({"label": 7}, "takes a string"),
    ({"label": "{{type_name}}"}, "looks like a placeholder"),                         # no second-order templates
    ({"label": "a\nb"}, "control characters"),
    ({"label": "x" * 600}, "too long"),
])
def test_injection_and_type_mismatch_are_refused_and_nothing_runs(given, words):
    viewer = _Viewer(stored=[_param_query()], answer=3)
    out = saved_query(viewer, QN, mode="live", params=given)
    assert out["refused"] is True and out["value"] is None and words in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


def test_a_url_or_path_in_a_string_value_is_data_and_never_moves_the_request():
    viewer = _Viewer(stored=[_param_query()], answer=2)
    out = saved_query(viewer, QN, mode="live", params={"label": "https://evil.example.com/../../x"})
    assert out["value"] == 2
    sent = _ran(viewer)[0]
    assert sent["searchProperties"]["conditions"][0]["value"]["primitiveValue"] == "https://evil.example.com/../../x"
    assert sent["metadataElementTypeName"] == "Asset"  # the request is still pyegeria's own find


def test_params_on_a_query_that_declares_none_are_refused():
    out = saved_query(_Viewer(answer=1), QN, mode="live", params={"type_name": "DataSet"})
    assert out["refused"] is True and "declares no parameters" in out["state_reason"]


def test_a_missing_required_parameter_is_refused():
    params = json.dumps([{"name": "type_name", "type": "string", "required": True}])
    out = saved_query(_Viewer(stored=[_param_query(params=params)], answer=1), QN, mode="live")
    assert out["refused"] is True and "is required" in out["state_reason"]


@pytest.mark.parametrize("body,words", [
    ({**TEMPLATE, "{{type_name}}": "x"}, "in a key"),
    ({**TEMPLATE, "metadataElementTypeName": "Prefix{{type_name}}"}, "inside a longer string"),
    ({**TEMPLATE, "metadataElementTypeName": "{{undeclared}}"}, "names 'undeclared'"),
])
def test_a_placeholder_anywhere_but_a_whole_value_is_refused(body, words):
    viewer = _Viewer(stored=[_param_query(body=body)], answer=1)
    out = saved_query(viewer, QN, mode="live", params={"label": "x"})
    assert out["refused"] is True and words in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


@pytest.mark.parametrize("params,words", [
    ("not json", "not JSON"),
    (json.dumps({"name": "x"}), "not a list"),
    (json.dumps([{"name": "bad name"}]), "no plain name"),
    (json.dumps([{"name": "x", "type": "float"}]), "the types are"),
    (json.dumps([{"name": "x", "type": "enum"}]), "lists no values"),
    (json.dumps([{"name": "x"}, {"name": "x"}]), "twice"),
    (json.dumps([{"name": "x", "type": "int", "default": "abc"}]), "takes an int"),
])
def test_a_bad_declaration_is_refused(params, words):
    out = saved_query(_Viewer(stored=[_param_query(params=params)], answer=1), QN, mode="live")
    assert out["refused"] is True and words in out["state_reason"]


def test_the_url_is_never_a_template():
    url = PORTAL_URL.replace("by-search-conditions", "{{type_name}}")
    viewer = _Viewer(stored=[_param_query(url=url)], answer=1)
    out = saved_query(viewer, QN, mode="live", params={"type_name": "DataSet"})
    assert out["refused"] is True and [c[0] for c in viewer.calls] == ["find"]


# the cache: one Results Set holds one answer, for the values it was refreshed with

def test_a_cached_answer_is_labelled_with_the_values_it_was_refreshed_with():
    last = {"type_name": "Asset", "days": 180, "active": True}
    out = saved_query(_Viewer(stored=[_param_query(last=last)], members=9), QN)
    assert out["value"] == 9 and out["params"] == last
    assert out["subtitle"] == 'as of 2026-11-10T18:02:11+00:00, for active=true, days=180, type_name="Asset"'


def test_a_cached_answer_for_other_values_is_never_returned():
    last = {"type_name": "Asset", "days": 180, "active": True}
    viewer = _Viewer(stored=[_param_query(last=last)], members=9)
    out = saved_query(viewer, QN, params={"type_name": "DataSet"})
    assert out["value"] is None and out["state"] == "not_established"
    assert 'is for active=true, days=180, type_name="Asset", not active=true, days=180, type_name="DataSet"' \
        in out["state_reason"]
    assert "use mode live" in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]  # the members were never read


def test_the_cache_key_is_every_value_defaults_included():
    last = {"type_name": "Asset", "days": 30, "active": True}  # refreshed with days=30
    out = saved_query(_Viewer(stored=[_param_query(last=last)], members=9), QN)  # defaults: days=180
    assert out["value"] is None and "days=30" in out["state_reason"] and "days=180" in out["state_reason"]
    out = saved_query(_Viewer(stored=[_param_query(last=last)], members=9), QN, params={"days": "30"})
    assert out["value"] == 9


def test_a_cached_answer_that_did_not_record_its_values_is_not_used():
    out = saved_query(_Viewer(stored=[_param_query(last=None)], members=9), QN)
    assert out["value"] is None and "does not record the parameter values" in out["state_reason"]
