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


# Built-in report specs whose spec_params name a filter the target method does not have.
# These were always silently dropped; 6.2.28 warns about them. Fix at the source (the
# Dr.Egeria compact specs / gen_report_specs) and remove them from this list.
KNOWN_BAD_SPEC_PARAMS = {
    ("metadata_element_types", "ExternalReferences.find_external_references"),
    ("classification", "GlossaryManager.find_glossary_terms"),
}


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
    assert found <= KNOWN_BAD_SPEC_PARAMS, f"new invalid spec_params: {sorted(found - KNOWN_BAD_SPEC_PARAMS)}"
    assert found == KNOWN_BAD_SPEC_PARAMS, f"fixed -- remove from KNOWN_BAD_SPEC_PARAMS: {sorted(KNOWN_BAD_SPEC_PARAMS - found)}"
