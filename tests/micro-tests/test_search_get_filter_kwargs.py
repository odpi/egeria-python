# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Search and get filters are universal, checked and documented (pyegeria 6.2.28).

* every public find_*/get_* method that sends a filterable request body accepts
  **kwargs and forwards it toward the shared request helper;
* the TypedDicts in pyegeria.core.request_filters, the name check and the docs page
  all come from the request-body models, and cannot drift from them;
* an unknown filter name warns (UnknownFilterWarning) and a known one reaches the
  request body -- including through a report spec's spec_params.
"""
from __future__ import annotations

import json
import pathlib
import warnings

import pytest

from pyegeria.core import request_filters as rf
from pyegeria.core._filter_kwargs_survey import in_scope, survey
from pyegeria.core.request_filters import UnknownFilterWarning

REPO = pathlib.Path(__file__).resolve().parents[2]

# Methods that reach a shared helper only incidentally (a platform-GUID lookup, or an
# aggregate over another call) -- the request they are named for has no filterable body.
EXEMPT = {
    "SecurityOfficer._async_get_user_account": "GET user-account; helper reached only via the platform-GUID lookup",
    "SecurityOfficer.get_user_account": "as above",
    "SecurityOfficer._async_get_user_list": "GET user-accounts; helper reached only via the platform-GUID lookup",
    "SecurityOfficer.get_user_list": "as above",
    "SecurityOfficer._async_get_security_access_control": "GET access control; helper reached only via the platform-GUID lookup",
    "SecurityOfficer.get_security_access_control": "as above",
    "SecurityOfficer._async_get_control_implementation_summary": "a computed summary over one statement of applicability",
    "SecurityOfficer.get_control_implementation_summary": "as above",
}


@pytest.fixture(scope="module")
def methods():
    return in_scope(survey())


# ---------------------------------------------------------------------------- part 1

def test_survey_finds_the_find_and_get_families(methods):
    names = {m.qualname for m in methods}
    assert "DataDesigner.find_data_value_specifications" in names
    assert "DataDesigner.find_all_data_structures" in names
    assert "DataDesigner.find_all_data_fields" in names
    assert "CollectionManager.find_digital_products" in names
    assert "MetadataExpert.find_metadata_elements" in names
    assert len(methods) > 450


def test_every_find_and_get_method_accepts_and_forwards_kwargs(methods):
    missing = [m.qualname for m in methods
               if m.qualname not in EXEMPT and not (m.kwargs_name and m.passes_kwargs())]
    assert not missing, (
        "These find_*/get_* methods send a filterable request but do not accept **kwargs "
        "or do not pass it on toward the shared request helper:\n  " + "\n  ".join(sorted(missing)))


def test_exemptions_are_still_needed(methods):
    by_name = {m.qualname: m for m in methods}
    stale = [q for q in EXEMPT if q not in by_name or (by_name[q].kwargs_name and by_name[q].passes_kwargs())]
    assert not stale, f"remove from EXEMPT: {stale}"


def test_unpack_annotation_matches_the_request_kind(methods):
    """Annotated methods name the right TypedDict; un-annotated ones have a PEP 692 overlap reason."""
    wrong, unexplained = [], []
    for m in methods:
        if m.qualname in EXEMPT:
            continue
        td = getattr(rf, m.filters)
        ann = m.unpack_annotation()
        if ann is not None and ann != m.filters:
            wrong.append(f"{m.qualname}: Unpack[{ann}] but sends {m.filters}")
        overlap = m.explicit_params & set(td.__annotations__)
        if ann is not None and overlap:
            wrong.append(f"{m.qualname}: Unpack[{ann}] duplicates explicit params {sorted(overlap)}")
        if ann is None and not overlap:
            unexplained.append(m.qualname)
    assert not wrong, "\n".join(wrong)
    assert not unexplained, ("Annotate **kwargs: Unpack[...] on: " + ", ".join(sorted(unexplained)))


# ---------------------------------------------------------------------------- one source

@pytest.mark.parametrize("model, td", list(rf.TYPED_DICT_FOR_MODEL.items()),
                         ids=lambda x: getattr(x, "__name__", str(x)))
def test_typed_dict_covers_exactly_the_model(model, td):
    model_fields = {n for n in model.model_fields if n != "class_"}
    mapped = {rf.PUBLIC_ALIASES.get(k, k) for k in td.__annotations__}
    call = set(rf.CALL_PARAMETERS[model])
    if model is rf.SearchStringRequestBody:  # also covers FindPropertyNamesRequestBody
        model_fields |= {n for n in rf.FindPropertyNamesRequestBody.model_fields if n != "class_"}
        call |= rf._FIND_PROPERTY_NAMES_CALL_PARAMETERS
    assert not (mapped & call), "a call parameter is repeated in the TypedDict"
    assert mapped | call == model_fields, (
        f"{td.__name__} vs {model.__name__}: missing {sorted(model_fields - mapped - call)}, "
        f"extra {sorted((mapped | call) - model_fields)}")


def test_every_typed_dict_field_has_a_docstring():
    docs = rf._field_docs()
    for td in (rf.GetFilters, rf.ListFilters, rf.SearchFilters, rf.FindFilters):
        own = rf._own_fields(td)
        assert own and all(docs[td.__name__].get(k) for k in own), td.__name__


def test_docs_page_tables_are_generated_from_the_module():
    page = (REPO / "docs" / "search-and-get-filters.md").read_text(encoding="utf-8")
    start, end = "<!-- BEGIN GENERATED FILTER TABLES -->\n", "<!-- END GENERATED FILTER TABLES -->"
    generated = page.split(start, 1)[1].split(end, 1)[0]
    assert generated == rf.filter_reference_markdown(), (
        "docs/search-and-get-filters.md is stale: regenerate the block with "
        "pyegeria.core.request_filters.filter_reference_markdown()")


# ---------------------------------------------------------------------------- part 2

def test_known_filter_maps_to_wire_name_and_unknown_warns():
    with pytest.warns(UnknownFilterWarning, match=r"'metadata_element_subtipes'.*metadata_element_subtypes"):
        body = rf.filter_body_kwargs("search", {"metadata_element_subtypes": ["DataClass"],
                                                "metadata_element_subtipes": ["X"],
                                                "max_depth": 2, "anchorGUID": "a1", "sequencing_order": None})
    assert body == {"metadataElementSubtypeNames": ["DataClass"], "anchorGUID": "a1"}


def test_render_options_do_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        assert rf.filter_body_kwargs("get", {"refresh_spec": False, "include_peers": True}) == {}


def test_valid_sets_come_from_the_models():
    assert "metadata_element_subtypes" in rf.valid_filter_names("get")
    assert "anchor_guid" not in rf.valid_filter_names("get")       # not on GetRequestBody
    assert "anchor_guid" in rf.valid_filter_names("name")
    assert "filter_string" in rf.valid_filter_names("name")
    assert "property_names" in rf.valid_filter_names("search")
    assert "skip_subtypes" in rf.valid_filter_names("find")
    assert "skip_subtypes" not in rf.valid_filter_names("search")


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture
def designer(monkeypatch):
    from pyegeria.omvs.data_designer import DataDesigner

    monkeypatch.setattr(DataDesigner, "check_connection", lambda self: "test")
    client = DataDesigner("view-server", "https://egeria.example:9443", "user", "pwd")
    sent: list[dict] = []

    async def fake_request(method, url, payload=None, *args, **kwargs):
        sent.append(json.loads(payload) if isinstance(payload, str) else (payload or {}))
        return _Response({"elements": [{"elementHeader": {"guid": "g1"}}], "element": {"elementHeader": {"guid": "g1"}}})

    monkeypatch.setattr(client, "_async_make_request", fake_request)
    client.sent = sent
    return client


def test_find_data_value_specifications_restricted_to_data_class(designer):
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        designer.find_data_value_specifications("*", metadata_element_subtypes=["DataClass"])
    assert designer.sent[-1]["metadataElementSubtypeNames"] == ["DataClass"]


def test_find_unknown_filter_warns_and_is_not_sent(designer):
    with pytest.warns(UnknownFilterWarning, match="find_data_value_specifications"):
        designer.find_data_value_specifications("*", metadata_element_subtipes=["DataClass"])
    assert "metadataElementSubtypeNames" not in designer.sent[-1]
    assert "metadata_element_subtipes" not in designer.sent[-1]


def test_find_all_data_fields_now_filters(designer):
    designer.find_all_data_fields(limit_results_by_status=["ACTIVE"])
    assert designer.sent[-1]["limitResultsByStatus"] == ["ACTIVE"]


def test_get_by_guid_forwards_get_filters(designer):
    designer.get_data_class_by_guid("g1", as_of_time="2026-01-01T00:00:00", skip_relationships=["Foo"])
    body = designer.sent[-1]
    assert body["skipRelationships"] == ["Foo"] and body["asOfTime"].startswith("2026-01-01")


def test_get_by_name_forwards_public_spelling(designer):
    designer.get_data_value_specifications_by_name("x", metadata_element_subtypes=["DataClass"], anchor_domain="Glossary")
    body = designer.sent[-1]
    assert body["metadataElementSubtypeNames"] == ["DataClass"]
    assert body["anchorDomainName"] == "Glossary"


def test_get_by_guid_unknown_filter_warns(designer):
    with pytest.warns(UnknownFilterWarning, match="anchor_guid"):  # anchor filters are list/search only
        designer.get_data_class_by_guid("g1", anchor_guid="a1")


# ---------------------------------------------------------------------------- report specs

def test_spec_params_typo_warns_through_the_report_executor(designer, monkeypatch):
    """A report spec's spec_params go into the same kwargs, so a typo there warns too."""
    import pyegeria.view.format_set_executor as fse
    from pyegeria.omvs.data_designer import DataDesigner

    fmt = {"action": {"function": "DataDesigner.find_data_value_specifications",
                      "required_params": [], "optional_params": ["search_string"],
                      "spec_params": {"metadata_element_subtypes": ["DataClass"],
                                      "metadata_element_subtipes": ["DataClass"]}}}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, kind: fmt)
    monkeypatch.setattr(fse, "_resolve_client_and_method",
                        lambda decl: (DataDesigner, decl.split(".")[-1]))
    monkeypatch.setattr(fse, "_resolve_action_target_client", lambda client, cls: designer)

    class _Tech:
        user_id, user_pwd = "user", "pwd"

        def get_token(self):
            return "token"

    import asyncio
    with pytest.warns(UnknownFilterWarning, match="metadata_element_subtipes"):
        out = asyncio.run(fse._async_run_report_impl("Data-Classes-Test", _Tech(), output_format="JSON",
                                                     params={"search_string": "*"}))
    assert out["kind"] == "json"
    assert designer.sent[-1]["metadataElementSubtypeNames"] == ["DataClass"]


def test_report_param_aliases_do_not_warn():
    import pyegeria.view.format_set_executor as fse
    params = fse._normalize_report_params({"metadata_element_name": "DataClass", "sort_order": "ANY",
                                           "order_property_name": "name", "anchor_scope_id": "s1",
                                           "limit_result_by_status": "ACTIVE"}, action_mode="find")
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        body = rf.filter_body_kwargs("search", params)
    assert body["metadataElementTypeName"] == "DataClass"
    assert body["sequencingOrder"] == "ANY" and body["anchorScopeGUID"] == "s1"


# Every built-in report spec's spec_params must be a filter (or explicit parameter) of the
# method it calls. Before 6.2.28 a misspelt one was silently dropped and the report ran
# unfiltered (e.g. Cited-Document listed every external reference); fix any failure at the
# source -- the Dr.Egeria compact specs' find_constraints -- then run refresh_specs.
def test_builtin_report_spec_params_are_valid_filters(methods):
    from pyegeria.view.base_report_formats import get_report_registry

    kind = {"SearchFilters": "search", "ListFilters": "name", "GetFilters": "get", "FindFilters": "find"}
    by_name = {(m.cls, m.name): m for m in methods}
    found = set()
    for spec_name, fs in get_report_registry().items():
        action = getattr(fs, "action", None)
        func = getattr(action, "function", "") or ""
        if "." not in func:
            continue
        cls, meth = func.split(".")[:2]
        m = by_name.get((cls, meth)) or by_name.get((cls, "_async_" + meth.removeprefix("_async_")))
        if m is None:
            continue
        wire = rf._wire_map(kind[m.filters])
        for key in (getattr(action, "spec_params", None) or {}):
            if key not in wire and key not in rf.RENDER_OPTIONS and key not in m.explicit_params:
                found.add((key, func))
    assert not found, f"spec_params that are not filters of the called method: {sorted(found)}"


def test_no_call_hard_codes_a_filter_beside_forwarded_kwargs(methods):
    """f(..., metadata_element_type="X", **kwargs) raises TypeError ("multiple values") as soon as a
    caller -- or a report spec's spec_params -- passes that filter. Put the default in the splat
    instead (f(..., **{"metadata_element_type": "X", **kwargs})) so the caller's value wins."""
    import ast

    kind = {"SearchFilters": "search", "ListFilters": "name", "GetFilters": "get", "FindFilters": "find"}
    bad = []
    for m in methods:
        if not m.kwargs_name:
            continue
        valid = rf.valid_filter_names(kind[m.filters]) | set(rf.LEGACY_ALIASES)
        for call in ast.walk(m.node):
            if not isinstance(call, ast.Call):
                continue
            if not any(k.arg is None and isinstance(k.value, ast.Name) and k.value.id == m.kwargs_name
                       for k in call.keywords):
                continue
            clash = [k.arg for k in call.keywords if k.arg in valid and k.arg not in m.explicit_params]
            if clash:
                bad.append(f"{m.qualname}: {clash}")
    assert not bad, "\n".join(bad)


# ---------------------------------------------------------------------------- one name everywhere

def test_no_signature_uses_a_deprecated_type_name():
    """6.2.28: the element-type filters are spelt metadata_element_type / metadata_element_subtypes
    in every method signature; the old spellings live only in DEPRECATED_NAMES."""
    import ast

    bad = []
    for path in sorted((REPO / "pyegeria").rglob("*.py")):
        if path.name == "request_filters.py" or "models" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = node.args
                for arg in a.posonlyargs + a.args + a.kwonlyargs:
                    if arg.arg in rf.DEPRECATED_NAMES:
                        bad.append(f"{path.relative_to(REPO)}:{node.lineno} {node.name}({arg.arg})")
    assert not bad, "rename to the canonical name:\n" + "\n".join(bad)


@pytest.fixture
def explorer(monkeypatch):
    from pyegeria.omvs.classification_explorer import ClassificationExplorer

    monkeypatch.setattr(ClassificationExplorer, "check_connection", lambda self: "test")
    client = ClassificationExplorer("view-server", "https://egeria.example:9443", "user", "pwd")
    sent: list[dict] = []

    async def fake_request(method, url, payload=None, *args, **kwargs):
        sent.append(json.loads(payload) if isinstance(payload, str) else (payload or {}))
        return _Response({"elements": [{"elementHeader": {"guid": "g1"}}]})

    monkeypatch.setattr(client, "_async_make_request", fake_request)
    client.sent = sent
    return client


def test_deprecated_type_name_still_works_with_a_warning(explorer):
    with pytest.warns(DeprecationWarning, match="'metadata_element_type_name' is deprecated; use 'metadata_element_type'"):
        explorer.find_elements_by_property_value("x", ["displayName"], metadata_element_type_name="EmbeddedProcess")
    assert explorer.sent[-1]["metadataElementTypeName"] == "EmbeddedProcess"


def test_canonical_type_name_does_not_warn(explorer):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        explorer.find_elements_by_property_value("x", ["displayName"], metadata_element_type="EmbeddedProcess")
    assert explorer.sent[-1]["metadataElementTypeName"] == "EmbeddedProcess"


def test_both_type_names_with_different_values_are_refused(explorer):
    with pytest.warns(DeprecationWarning), pytest.raises(TypeError, match="pass only 'metadata_element_type'"):
        explorer.find_elements_by_property_value("x", ["displayName"], metadata_element_type="A",
                                                 metadata_element_type_name="B")
    assert not explorer.sent


def test_deprecated_names_in_kwargs_warn_too(designer):
    with pytest.warns(DeprecationWarning, match="'metadata_element_subtype_names' is deprecated"):
        designer.find_data_value_specifications("*", metadata_element_subtype_names=["DataClass"])
    assert designer.sent[-1]["metadataElementSubtypeNames"] == ["DataClass"]


def test_lone_string_for_subtypes_becomes_a_list():
    with pytest.warns(DeprecationWarning):
        out = rf.canonicalize_names({"metadata_element_sub_type": "DataClass"}, owner="t")
    assert out == {"metadata_element_subtypes": ["DataClass"]}


def test_report_executor_canonicalizes_quietly():
    import pyegeria.view.format_set_executor as fse

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        out = fse._normalize_report_params({"metadata_element_type_name": "X",
                                            "metadata_element_subtype_names": "A,B"}, action_mode="find")
    assert out["metadata_element_type"] == "X" and out["metadata_element_subtypes"] == ["A", "B"]
    assert "metadata_element_type_name" not in out and "metadata_element_subtype_names" not in out


# ---------------------------------------------------------------------------- generic-search specs

# (ClassificationExplorer.get_elements is not here: it always sends a type, Referenceable by default.)
GENERIC_SEARCH_FUNCTIONS = {
    "MetadataExpert.find_metadata_elements_with_string",
    "ClassificationExplorer.find_elements_by_property_value",
}
TYPE_FILTERS = {"metadata_element_type", "metadata_element_subtypes", "include_only_classified_elements"}


def test_every_generic_search_spec_names_a_type():
    """A generic search with no type lists whatever matches across the whole repository, and with
    '*' Egeria refuses it outright ("searchString is null"). Each such report spec must say which
    type (or classification) it is about -- set it in the Dr.Egeria command's find_constraints."""
    from pyegeria.view.base_report_formats import get_report_registry

    untyped = []
    for name, fs in get_report_registry().items():
        action = getattr(fs, "action", None)
        if getattr(action, "function", None) in GENERIC_SEARCH_FUNCTIONS:
            if not TYPE_FILTERS & set(getattr(action, "spec_params", None) or {}):
                untyped.append(f"{name} -> {action.function}")
    assert not untyped, "generic-search report specs with no type filter:\n" + "\n".join(sorted(untyped))


def test_untyped_star_is_refused_with_words(explorer, monkeypatch):
    from pyegeria.core.request_filters import SearchRefused
    from pyegeria.omvs.metadata_expert import MetadataExpert

    with pytest.raises(SearchRefused, match="give a search string or a"):
        explorer.find_elements_by_property_value("*", ["displayName"])
    assert not explorer.sent

    monkeypatch.setattr(MetadataExpert, "check_connection", lambda self: "test")
    expert = MetadataExpert("view-server", "https://egeria.example:9443", "user", "pwd")
    with pytest.raises(SearchRefused, match="give a search string or a type"):
        expert.find_metadata_elements_with_string("*")


def test_typed_star_lists_every_element_of_the_type(explorer):
    explorer.find_elements_by_property_value("*", ["displayName", "qualifiedName"],
                                             metadata_element_type="EmbeddedProcess", page_size=5)
    body = explorer.sent[-1]
    assert body["metadataElementTypeName"] == "EmbeddedProcess"
    assert "propertyValue" not in body and "searchString" not in body  # sent as a by-type list


def test_report_search_string_reaches_property_value():
    import pyegeria.view.format_set_executor as fse
    from pyegeria.omvs.classification_explorer import ClassificationExplorer

    out = fse._bind_search_parameter(ClassificationExplorer.find_elements_by_property_value,
                                     {"search_string": "pump", "property_names": ["displayName"]})
    assert out == {"property_value": "pump", "property_names": ["displayName"]}


def _conditions(body):
    return body["searchProperties"]["conditions"]


def test_star_with_a_technology_lists_exactly_that_technology(explorer):
    explorer.find_elements_by_property_value("*", ["displayName", "qualifiedName"],
                                             metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="Unity Catalog Server")
    body = explorer.sent[-1]
    assert body["class"] == "FindRequestBody" and body["metadataElementTypeName"] == "SoftwareServer"
    # exact, so "Databricks Unity Catalog Server" is not a "Unity Catalog Server"
    assert _conditions(body) == [{"property": "deployedImplementationType", "operator": "CASE_INSENSITIVE_EQ",
                                  "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string",
                                            "primitiveValue": "Unity Catalog Server"}}]
    assert body["searchProperties"]["matchCriteria"] == "ALL"


def test_search_string_with_a_technology_ands_both_conditions_server_side(explorer):
    explorer.find_elements_by_property_value("Coco", ["displayName", "qualifiedName"],
                                             metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="PostgreSQL Server", page_size=25)
    body = explorer.sent[-1]
    tech, names = _conditions(body)
    assert tech["property"] == "deployedImplementationType" and tech["operator"] == "CASE_INSENSITIVE_EQ"
    nested = names["nestedConditions"]
    assert nested["matchCriteria"] == "ANY"
    assert [(c["property"], c["operator"], c["value"]["primitiveValue"]) for c in nested["conditions"]] == [
        ("displayName", "STARTS_WITH", "Coco"), ("qualifiedName", "STARTS_WITH", "Coco")]
    assert body["searchProperties"]["matchCriteria"] == "ALL" and body["pageSize"] == 25


@pytest.mark.parametrize("starts, ends, ignore, op", [
    (True, False, False, "STARTS_WITH"), (False, True, False, "ENDS_WITH"), (True, True, False, "EQ"),
    (False, False, False, "LIKE"), (True, False, True, "CASE_INSENSITIVE_STARTS_WITH"),
    (False, False, True, "CASE_INSENSITIVE_LIKE")])
def test_search_options_map_to_egeria_operators(starts, ends, ignore, op):
    from pyegeria.omvs.classification_explorer import _match_operator
    assert _match_operator(starts, ends, ignore) == op


def test_generator_derives_type_and_technology_from_the_command():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gen_report_specs", REPO / "commands" / "tech" / "gen_report_specs.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    ce = "ClassificationExplorer.find_elements_by_property_value"
    assert gen._generic_search_constraints("Create Postgres Server Element", {"OM_TYPE": "SoftwareServer"}, ce, {}) == {
        "metadata_element_type": "SoftwareServer", "property_names": ["displayName", "qualifiedName"],
        "default_deployed_implementation_type": "PostgreSQL Server"}
    assert gen._generic_search_constraints("Create Element", {"OM_TYPE": ""}, ce, {})["metadata_element_type"] \
        == "OpenMetadataRoot"
    # an explicit type in find_constraints is kept; other find methods are untouched
    assert gen._generic_search_constraints("Create X", {"OM_TYPE": "A"}, ce, {"metadata_element_type": "B"})[
        "metadata_element_type"] == "B"
    assert gen._generic_search_constraints("Create X", {"OM_TYPE": "A"}, "GlossaryManager.find_glossaries", {}) == {}


def test_technology_specs_show_the_technology_column():
    from pyegeria.view.base_report_formats import get_report_registry

    fs = get_report_registry()["Postgres-Server-Element-DrE-Basic"]
    # the spec pins a DEFAULT; the run parameter is declared optional (no unknown-filter warning, and
    # the Portal's run form shows it)
    assert fs.action.spec_params["default_deployed_implementation_type"] == "PostgreSQL Server"
    assert "deployed_implementation_type" not in fs.action.spec_params
    assert "deployed_implementation_type" in fs.action.optional_params
    assert any(c.key == "deployed_implementation_type" for c in fs.formats[0].attributes)


def test_report_run_param_typo_warns(monkeypatch):
    """P3: exec_report_spec passes only the report's declared parameters; a caller's typo used to vanish."""
    import pyegeria.view.format_set_executor as fse

    with pytest.warns(UnknownFilterWarning, match=r"report 'R': parameter\(s\) 'metadata_element_subtipes' ignored"):
        fse._warn_dropped_params("R", {"search_string": "*", "metadata_element_subtipes": ["X"], "page_size": 5},
                                 {"search_string": "*", "page_size": 5}, ["search_string", "page_size"])
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        fse._warn_dropped_params("R", {"search_string": "*", "sort_order": "ANY"}, {"property_value": "*"},
                                 ["search_string"])


@pytest.mark.parametrize("root", ["OpenMetadataRoot", "Referenceable"])
def test_star_on_a_root_type_is_refused(explorer, root):
    # get_elements(OpenMetadataRoot, page_size=1000) ran the quickstart platform out of heap.
    with pytest.raises(ValueError, match="give a search string or a narrower type"):
        explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type=root)
    assert not explorer.sent
    explorer.find_elements_by_property_value("pump", ["displayName"], metadata_element_type=root)
    assert explorer.sent[-1]["propertyValue"] == "pump"


@pytest.mark.parametrize("asked, sent", [(0, 100), (None, 100), (1000, 100), (25, 25)])
def test_star_pages_never_more_than_100(explorer, asked, sent):
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="EmbeddedProcess",
                                             page_size=asked, start_from=200)
    body = explorer.sent[-1]
    assert body["pageSize"] == sent and body["startFrom"] == 200


def test_technology_star_pages_never_more_than_100(explorer):
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="PostgreSQL Server", page_size=1000)
    assert explorer.sent[-1]["pageSize"] == 100


def test_exec_report_spec_surfaces_a_refusal(monkeypatch):
    """The sync executor used to swallow ValueError and return None."""
    import pyegeria.view.format_set_executor as fse

    class _Client:
        def __init__(self, *a, **k):
            pass

        def set_bearer_token(self, token):
            pass

        def close_session(self):
            pass

        def find_things(self, search_string="*", **kwargs):
            from pyegeria.core.request_filters import SearchRefused
            raise SearchRefused("give a search string or a narrower type")

    fmt = {"action": {"function": "X.find_things", "required_params": ["search_string"], "spec_params": {}}}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, kind: fmt)
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_Client, "find_things"))
    with pytest.raises(ValueError, match="narrower type"):
        fse.exec_report_spec("R", output_format="DICT", params={"search_string": "*"},
                             view_server="v", view_url="https://x", user="u", user_pass="p", token="t")



def _tech(body):
    conds = body.get("searchProperties", {}).get("conditions", []) if isinstance(body, dict) else []
    return [c["value"]["primitiveValue"] for c in conds if c.get("property") == "deployedImplementationType"]


def test_technology_default_applies_when_not_given(explorer):
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="SoftwareServer",
                                             default_deployed_implementation_type="PostgreSQL Server")
    assert _tech(explorer.sent[-1]) == ["PostgreSQL Server"]


def test_technology_star_means_any_technology(explorer):
    # '*' as the technology drops the condition: every SoftwareServer, '*' still lists via get_elements
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="*",
                                             default_deployed_implementation_type="PostgreSQL Server",
                                             page_size=500)
    body = explorer.sent[-1]
    assert _tech(body) == [] and body["metadataElementTypeName"] == "SoftwareServer"
    assert body["pageSize"] == 100  # still capped
    # a search string still matches by name, within the whole type
    explorer.find_elements_by_property_value("Coco", ["displayName"], metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="*",
                                             default_deployed_implementation_type="PostgreSQL Server")
    assert explorer.sent[-1]["propertyValue"] == "Coco" and _tech(explorer.sent[-1]) == []


def test_technology_star_keeps_the_root_type_refusal(explorer):
    with pytest.raises(ValueError, match="narrower type"):
        explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="OpenMetadataRoot",
                                                 deployed_implementation_type="*")


def test_any_other_technology_is_an_exact_match(explorer):
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="Apache Kafka Server",
                                             default_deployed_implementation_type="PostgreSQL Server")
    body = explorer.sent[-1]
    assert _tech(body) == ["Apache Kafka Server"]
    assert body["searchProperties"]["conditions"][0]["operator"] == "CASE_INSENSITIVE_EQ"


def test_report_run_param_overrides_the_technology_default(monkeypatch):
    """Through the executor: the spec pins the default, the caller's run parameter wins, no warning."""
    import pyegeria.view.format_set_executor as fse
    from pyegeria.view.base_report_formats import get_report_registry

    calls = []

    class _Client:
        def __init__(self, *a, **k):
            pass

        def set_bearer_token(self, token):
            pass

        def close_session(self):
            pass

        def find_elements_by_property_value(self, property_value, property_names, metadata_element_type=None,
                                            deployed_implementation_type=None,
                                            default_deployed_implementation_type=None, **kwargs):
            calls.append((deployed_implementation_type, default_deployed_implementation_type))
            return []

    action = get_report_registry()["Postgres-Server-Element-DrE-Basic"].action
    fmt = {"action": action.model_dump()}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, kind: fmt)
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_Client, "find_elements_by_property_value"))
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        for run_params in ({"search_string": "*"}, {"search_string": "*", "deployed_implementation_type": "*"}):
            fse.exec_report_spec("Postgres-Server-Element-DrE-Basic", output_format="DICT", params=run_params,
                                 view_server="v", view_url="https://x", user="u", user_pass="p", token="t")
    assert calls == [(None, "PostgreSQL Server"), ("*", "PostgreSQL Server")]



def test_technology_match_ignores_case(explorer):
    # exact, but "postgresql server" finds the PostgreSQL Server rather than an unexplained empty result
    explorer.find_elements_by_property_value("*", ["displayName"], metadata_element_type="SoftwareServer",
                                             deployed_implementation_type="postgresql server")
    cond = explorer.sent[-1]["searchProperties"]["conditions"][0]
    assert (cond["operator"], cond["value"]["primitiveValue"]) == ("CASE_INSENSITIVE_EQ", "postgresql server")
