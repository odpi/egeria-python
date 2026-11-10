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
import os

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

DOCKER_URL = f"https://host.docker.internal:9443/servers/{VIEW}{ENDPOINT}"


@pytest.mark.parametrize("url", [
    PORTAL_URL,                                   # this platform, this view server
    ENDPOINT,                                     # relative to the view server
    ENDPOINT.lstrip("/"),
    f"/servers/{VIEW}{ENDPOINT}",
    PORTAL_URL.replace("https://localhost", "HTTPS://LOCALHOST"),
    DOCKER_URL,                                   # the Portal's in-container URL (P-1)
    f"http://localhost:9443/servers/{VIEW}{ENDPOINT}",
    f"https://egeria.example.com:443/servers/{VIEW}{ENDPOINT}",
])
def test_allow_listed_requests_run(url):
    viewer = _Viewer(stored=[_saved_query(query_url=url)], answer=2)
    out = saved_query(viewer, QN, mode="live")
    assert out["value"] == 2 and "refused" not in out


def test_a_portal_saved_query_runs_from_localhost_and_the_host_is_noted_never_followed():
    viewer = _Viewer(stored=[_saved_query(query_url=DOCKER_URL)], answer=3)
    assert viewer.platform_url == "https://localhost:9443"
    out = saved_query(viewer, QN, mode="live")
    assert out["value"] == 3
    assert out["how"] == ("find_metadata_elements on this client's platform; the stored URL names "
                          "https://host.docker.internal:9443; the request went to this client's platform "
                          "(https://localhost:9443), never to the stored host")
    assert [c[0] for c in viewer.calls] == ["find", "find", "find"]  # only the viewer's own client


def test_the_same_origin_needs_no_note():
    out = saved_query(_Viewer(answer=1), QN, mode="live")
    assert out["how"] == "find_metadata_elements on this client's platform"


REFUSED = [
    ("https://erin@localhost:9443/servers/qs-view-server" + ENDPOINT, "user info"),
    ("https://localhost:9443@evil.example.com/servers/qs-view-server" + ENDPOINT, "user info"),
    ("//evil.example.com/servers/qs-view-server" + ENDPOINT, "scheme-relative"),
    ("ftp://localhost:9443/servers/qs-view-server" + ENDPOINT, "not an http(s) URL"),
    ("javascript:alert(1)", "not an http(s) URL"),
    ("/servers/another-view-server" + ENDPOINT, "names view server 'another-view-server'"),
    ("https://host.docker.internal:9443/servers/another-view-server" + ENDPOINT, "names view server"),
    ("/api/open-metadata/metadata-expert/metadata-elements/by-search-string", "not one of the query endpoints"),
    ("/api/open-metadata/asset-maker/assets", "not one of the query endpoints"),
    ("https://evil.example.com/api/open-metadata/asset-maker/assets", "not one of the query endpoints"),
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


# ── parameters (brief §9): one model with the Portal (P-2) ──

FIXTURE = json.load(open(os.path.join(os.path.dirname(__file__), "data",
                                      "portal_saved_query_parameters_2026_11_10.json")))
FQN = FIXTURE["properties"]["qualifiedName"]
REL = "relationship_conditions.0.relationship_type"


def _portal(**changes):
    """The shared fixture as a find returns it (an OpenMetadataElement), with `changes` to its
    additionalProperties (None removes one) or, for formula / queryRequestBody / queryURL, its properties."""
    props = json.loads(json.dumps(FIXTURE["properties"]))
    additional = props.pop("additionalProperties")
    for k, v in changes.items():
        target = props if k in ("formula", "queryRequestBody", "queryURL") else additional
        if v is None:
            target.pop(k, None)
        else:
            target[k] = v if isinstance(v, str) else json.dumps(v)
    pvm = {k: _str(v) for k, v in props.items()}
    pvm["additionalProperties"] = {"class": "MapTypePropertyValue", "mapValues": {
        "class": "InstanceProperties", "propertyValueMap": {k: _str(v) for k, v in additional.items()}}}
    return {"elementGUID": FIXTURE["guid"], "type": {"typeName": "SavedQuery"},
            "elementProperties": {"class": "ElementProperties", "propertyValueMap": pvm}}


def _ran(viewer):
    return [c[1] for c in viewer.calls[1:] if c[0] == "find"]


def _declare(*entries):
    return {"parameters": list(entries)}


# cached: the Portal's own record matches pyegeria's effective values

def test_the_portal_fixture_cached_answer_matches_and_is_labelled():
    out = saved_query(_Viewer(stored=[_portal()], members=37), FQN)
    assert out["value"] == 37
    assert out["params"] == {"type_name": "Asset", REL: "DataFlow"}
    assert out["subtitle"] == ('as of 2026-11-10T22:41:07+00:00, for '
                               'relationship_conditions.0.relationship_type="DataFlow", type_name="Asset"')


def test_the_stored_search_value_wins_over_the_default_so_no_false_refusal():
    # type_name's default is DataSet, but the stored search holds Asset, and the Portal recorded Asset
    out = saved_query(_Viewer(stored=[_portal()], members=5), FQN)
    assert out["value"] == 5 and out["params"]["type_name"] == "Asset"


def test_the_default_applies_only_when_the_stored_search_has_no_value():
    search = json.loads(FIXTURE["properties"]["formula"])
    search["type_name"] = None
    q = _portal(formula=search, lastRefreshParams={"type_name": "DataSet", REL: "DataFlow"})
    out = saved_query(_Viewer(stored=[q], members=4), FQN)
    assert out["value"] == 4 and out["params"]["type_name"] == "DataSet"


def test_search_spec_is_read_when_formula_is_empty_as_the_portal_does():
    q = _portal(formula="", searchSpec=FIXTURE["properties"]["formula"])
    assert saved_query(_Viewer(stored=[q], members=2), FQN)["value"] == 2


def test_search_path_names_where_the_portal_applies_it():
    params = [{"name": "kind", "type": "string", "searchPath": "type_name"}]
    q = _portal(parameters=params, lastRefreshParams={"kind": "Asset"})
    out = saved_query(_Viewer(stored=[q], members=6), FQN)
    assert out["value"] == 6 and out["params"] == {"kind": "Asset"}


def test_a_cached_answer_for_other_values_is_never_returned():
    viewer = _Viewer(stored=[_portal()], members=37)
    out = saved_query(viewer, FQN, params={"type_name": "DataSet"})
    assert out["value"] is None and out["state"] == "not_established"
    assert ('is for relationship_conditions.0.relationship_type="DataFlow", type_name="Asset", not '
            'relationship_conditions.0.relationship_type="DataFlow", type_name="DataSet"') in out["state_reason"]
    assert "use mode live" in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]  # the members were never read


def test_the_cache_key_is_every_declared_value():
    q = _portal(lastRefreshParams={"type_name": "Asset", REL: "Lineage"})
    out = saved_query(_Viewer(stored=[q], members=9), FQN)
    assert out["value"] is None and 'relationship_type="Lineage"' in out["state_reason"]


def test_a_cached_answer_that_did_not_record_its_values_is_not_used():
    out = saved_query(_Viewer(stored=[_portal(lastRefreshParams=None)], members=9), FQN)
    assert out["value"] is None and "does not record the parameter values" in out["state_reason"]


# live: values go to requestPath, typed; no placeholders; the stored bodies stay runnable

def test_live_applies_a_value_at_its_request_path():
    viewer = _Viewer(stored=[_portal()], answer=3)
    out = saved_query(viewer, FQN, mode="live", params={"type_name": "DataSet"})
    assert out["value"] == 3
    assert {b["metadataElementTypeName"] for b in _ran(viewer)} == {"DataSet"}
    assert out["params"] == {"type_name": "DataSet", REL: "DataFlow"}


def test_live_with_no_values_runs_the_stored_request_as_stored():
    viewer = _Viewer(stored=[_portal()], answer=2)
    out = saved_query(viewer, FQN, mode="live")
    assert _ran(viewer)[0]["metadataElementTypeName"] == "Asset"
    assert out["params"] == {"type_name": "Asset", REL: "DataFlow"}


def test_the_stored_request_is_never_changed():
    q = _portal()
    before = json.dumps(q, sort_keys=True)
    saved_query(_Viewer(stored=[q], answer=1), FQN, mode="live", params={"type_name": "DataSet"})
    assert json.dumps(q, sort_keys=True) == before


def test_a_portal_only_parameter_cannot_be_set_live():
    viewer = _Viewer(stored=[_portal()], answer=3)
    out = saved_query(viewer, FQN, mode="live", params={REL: "Lineage"})
    assert out["refused"] is True and "applies to the Portal's search only" in out["state_reason"]
    assert "use mode cached, or refresh it in the Portal" in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


def test_a_portal_only_parameter_on_its_default_is_refused_live():
    params = [{"name": "page_size", "type": "integer", "default": 100}]  # the stored search has none
    viewer = _Viewer(stored=[_portal(parameters=params)], answer=3)
    out = saved_query(viewer, FQN, mode="live")
    assert out["refused"] is True and "'page_size' applies to the Portal's search only" in out["state_reason"]


def test_a_nested_request_path_sets_a_value_only():
    body = json.loads(FIXTURE["properties"]["queryRequestBody"])
    body["searchProperties"] = {"class": "SearchProperties", "matchCriteria": "ALL", "conditions": [
        {"property": "displayName", "operator": "EQ",
         "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": "Sales"}}]}
    params = [{"name": "label", "type": "string", "requestPath": "searchProperties.conditions.0.value.primitiveValue"}]
    viewer = _Viewer(stored=[_portal(queryRequestBody=body, parameters=params)], answer=1)
    out = saved_query(viewer, FQN, mode="live", params={"label": 'Q4 "x" {{y}} https://evil.example.com/../'})
    sent = _ran(viewer)[0]
    assert sent["searchProperties"]["conditions"][0]["value"]["primitiveValue"] == 'Q4 "x" {{y}} https://evil.example.com/../'
    assert sent["searchProperties"]["conditions"][0]["property"] == "displayName"  # data, never a key
    assert out["value"] == 1


def test_a_request_path_that_points_nowhere_is_refused():
    params = [{"name": "type_name", "type": "string", "requestPath": "searchProperties.conditions.0.property"}]
    out = saved_query(_Viewer(stored=[_portal(parameters=params)], answer=1), FQN, mode="live",
                      params={"type_name": "DataSet"})
    assert out["refused"] is True and "points at nothing" in out["state_reason"]


@pytest.mark.parametrize("given,words", [
    ({"queryURL": "https://evil.example.com/x"}, "does not declare ['queryURL']"),   # a URL, as a name
    ({"../servers/x": "y"}, "does not declare"),                                    # path chars, as a name
    ({"type_name": 5}, "must be a string, not int"),                                # type mismatch
    ({"type_name": True}, "must be a string, not bool"),
    ({"type_name": ["Asset"]}, "must be a string, not list"),
    ({"type_name": "a\nb"}, "control characters"),
    ({"type_name": "x" * 600}, "over 512 characters"),
])
def test_injection_and_type_mismatch_are_refused_and_nothing_runs(given, words):
    viewer = _Viewer(stored=[_portal()], answer=3)
    out = saved_query(viewer, FQN, mode="live", params=given)
    assert out["refused"] is True and out["value"] is None and words in out["state_reason"]
    assert [c[0] for c in viewer.calls] == ["find"]


@pytest.mark.parametrize("ptype,good,bad", [
    ("integer", 30, "30"), ("integer", 30, True), ("number", 1.5, "1.5"), ("boolean", False, "false"),
    ("list", ["a", "b"], "a,b"),
])
def test_types_are_the_portals_with_no_coercion(ptype, good, bad):
    body = {**json.loads(FIXTURE["properties"]["queryRequestBody"]), "x": None}
    params = [{"name": "x", "type": ptype, "requestPath": "x"}]
    viewer = _Viewer(stored=[_portal(queryRequestBody=body, parameters=params)], answer=1)
    assert saved_query(viewer, FQN, mode="live", params={"x": good})["value"] == 1
    assert _ran(viewer)[0]["x"] == good
    assert saved_query(_Viewer(stored=[_portal(queryRequestBody=body, parameters=params)]), FQN, mode="live",
                       params={"x": bad})["refused"] is True


def test_params_on_a_query_that_declares_none_are_refused():
    out = saved_query(_Viewer(answer=1), QN, mode="live", params={"type_name": "DataSet"})
    assert out["refused"] is True and "declares no parameters" in out["state_reason"]


@pytest.mark.parametrize("params,words", [
    ("not json", "not JSON"),
    ({"name": "x"}, "not a list"),
    ([{"name": "bad name"}], "no plain (dotted) name"),
    ([{"name": "a..b"}], "no plain (dotted) name"),
    ([{"name": "x", "type": "enum"}], "the types are"),
    ([{"name": "x"}, {"name": "x"}], "twice"),
    ([{"name": "x", "type": "integer", "default": "abc"}], "must be a integer"),
    ([{"name": "x", "requestPath": "metadataElementTypeName; drop"}], "not a plain dotted path"),
    ([{"name": "x", "requestPath": "../queryURL"}], "not a plain dotted path"),
    ([{"name": "x", "searchPath": "https://evil.example.com"}], "not a plain dotted path"),
])
def test_a_bad_declaration_is_refused(params, words):
    out = saved_query(_Viewer(stored=[_portal(parameters=params)], answer=1), FQN, mode="live")
    assert out["refused"] is True and words in out["state_reason"]


def test_the_url_is_never_parameterised():
    params = [{"name": "type_name", "type": "string", "requestPath": "metadataElementTypeName"}]
    viewer = _Viewer(stored=[_portal(parameters=params)], answer=1)
    saved_query(viewer, FQN, mode="live", params={"type_name": "https://evil.example.com"})
    assert all(c[0] == "find" for c in viewer.calls)  # still pyegeria's own find on the viewer's client
    assert _ran(viewer)[0]["metadataElementTypeName"] == "https://evil.example.com"  # data only
