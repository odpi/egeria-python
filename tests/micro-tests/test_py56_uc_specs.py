"""PY-56: the Unity Catalog report specs pass the caller's search through and show only columns an element has.

- The catalog spec found catalogs by a pinned search_string ("Unity Catalog Catalog::"), so the caller's search was
  ignored. The prefix is now a constraint (qualified_name_prefix) ANDed with the caller's search.
- uc_catalog (and the other inputs of the create-from-template commands: uc_schema, uc_table, host_url, port,
  network_address ...) are not properties of the element the spec finds, so those columns were always blank.
  (A Namespace has no relationship end to an Endpoint in RELATIONSHIP_FIELDS, so there is no `of:` column for
  the network address either.)
"""
import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.view.base_report_formats import get_report_registry

UC = ["UC-Catalog-Element", "UC-Server-Element", "UC-Schema-Element", "UC-Table-Element", "UC-Function-Element",
      "UC-Volume-Element"]
CREATE_ONLY = {"uc_catalog", "uc_schema", "uc_table", "uc_table_type", "uc_storage_loc", "uc_data_source_format",
               "uc_function", "uc_volume", "uc_vol_type", "uc_server_name", "host_url", "port", "network_address"}


def _keys(fs):
    return {c.key for f in fs.formats for c in f.attributes}


@pytest.mark.parametrize("level", ["Basic", "Advanced"])
@pytest.mark.parametrize("name", UC)
def test_no_unity_catalog_spec_shows_a_create_only_input(name, level):
    fs = get_report_registry()[f"{name}-DrE-{level}"]
    assert _keys(fs) & CREATE_ONLY == set()
    assert {"display_name", "qualified_name", "guid"} <= _keys(fs)


@pytest.mark.parametrize("level", ["Basic", "Advanced"])
def test_the_catalog_spec_takes_the_callers_search_and_constrains_by_prefix(level):
    fs = get_report_registry()[f"UC-Catalog-Element-DrE-{level}"]
    sp = fs.action.spec_params
    assert "search_string" not in sp
    assert sp["qualified_name_prefix"] == "Unity Catalog Catalog::" and sp["metadata_element_type"] == "Namespace"
    assert "property_names" not in sp or sp["property_names"] == ["displayName", "qualifiedName"]
    assert "search_string" in fs.action.required_params


def test_the_seed_stage_passes_search_string_through():
    seed = json.load(open("pyegeria/view/seed/Asset Maker.json"))["specs"]
    stages = {s["label"]: s["microflow"]["stages"][0]["params"] for s in seed if s.get("label", "").startswith("UC-Catalog")}
    assert stages
    for params in stages.values():
        assert params["search_string"] == "$search_string"
        assert params["qualified_name_prefix"] == "Unity Catalog Catalog::"


def _explorer():
    obj = ClassificationExplorer.__new__(ClassificationExplorer)
    obj._async_find_root_elements = AsyncMock(return_value=["found"])
    obj._async_get_elements = AsyncMock(return_value=["all"])
    return obj


def test_the_find_ands_the_prefix_with_the_callers_search():
    obj = _explorer()
    asyncio.run(obj._async_find_elements_by_property_value(
        "sales", ["displayName", "qualifiedName"], metadata_element_type="Namespace",
        qualified_name_prefix="Unity Catalog Catalog::"))
    sp = obj._async_find_root_elements.await_args.kwargs["search_properties"]
    assert sp["matchCriteria"] == "ALL"
    prefix = sp["conditions"][0]
    assert prefix["property"] == "qualifiedName" and prefix["operator"] == "STARTS_WITH"
    assert prefix["value"]["primitiveValue"] == "Unity Catalog Catalog::"
    nested = sp["conditions"][1]["nestedConditions"]
    assert nested["matchCriteria"] == "ANY"
    assert {(c["property"], c["value"]["primitiveValue"]) for c in nested["conditions"]} == \
        {("displayName", "sales"), ("qualifiedName", "sales")}


def test_a_star_search_lists_every_element_with_the_prefix():
    obj = _explorer()
    asyncio.run(obj._async_find_elements_by_property_value(
        "*", ["displayName", "qualifiedName"], metadata_element_type="Namespace",
        qualified_name_prefix="Unity Catalog Catalog::"))
    conds = obj._async_find_root_elements.await_args.kwargs["search_properties"]["conditions"]
    assert len(conds) == 1 and conds[0]["operator"] == "STARTS_WITH"


def test_the_technology_and_the_prefix_both_apply():
    obj = _explorer()
    asyncio.run(obj._async_find_elements_by_property_value(
        "x", ["displayName"], metadata_element_type="Namespace", deployed_implementation_type="T",
        qualified_name_prefix="P::"))
    conds = obj._async_find_root_elements.await_args.kwargs["search_properties"]["conditions"]
    assert [c.get("property") for c in conds[:2]] == ["deployedImplementationType", "qualifiedName"]
    assert "nestedConditions" in conds[2]


def test_without_a_prefix_nothing_changes():
    obj = _explorer()
    asyncio.run(obj._async_find_elements_by_property_value("*", ["displayName"], metadata_element_type="Namespace"))
    obj._async_get_elements.assert_awaited()
    obj._async_find_root_elements.assert_not_called()
