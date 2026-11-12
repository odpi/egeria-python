# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Dr.Egeria `Create Saved Query` / `Update Saved Query` carry Formula and Formula Type (6.2.34).

The Portal's insights refresh re-runs a SavedQuery's `formula` (formulaType egeria-insights-search-v1), so a
seeded SavedQuery needs to carry it (BRIEF-PORTAL-SAVED-QUERY-SEEDABLE-2026-11-10). Both attributes are in
the compact spec (Saved Query Base), and SavedQueryProcessor writes them as DataSetProperties' formula /
formulaType on create and on update. The fake client below stands in for Egeria; nothing reaches it.
"""
import asyncio
import json
import os

import pytest

from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir
from md_processing.v2.saved_query import SavedQueryProcessor

pytestmark = pytest.mark.unit

FORMULA = json.dumps({"type_name": "Asset", "relationship_conditions": [{"relationship_type": "DataFlow",
                                                                         "present": False}]})
FORMULA_TYPE = "egeria-insights-search-v1"


def _specs():
    import md_processing
    d = os.path.join(os.path.dirname(md_processing.__file__), "data", "compact_commands")
    return load_compact_specs_from_dir(d)


def test_the_command_spec_has_formula_and_formula_type():
    spec = _specs()["Create Saved Query"]
    names = [a.get("name") if isinstance(a, dict) else a for a in json.loads(json.dumps(spec.get("Attributes")
                                                                                          or spec.get("attributes")
                                                                                          or []))]
    flat = json.dumps(spec)
    assert "Formula" in flat and "Formula Type" in flat, names
    assert '"formula_type"' in flat


class _Client:
    def __init__(self):
        self.created, self.updated = [], []

    async def _async_create_asset(self, types, body):
        self.created.append((types, body))
        return "sq-guid"

    async def _async_update_asset(self, guid, body):
        self.updated.append((guid, body))


def _run(as_is=None, formula=FORMULA, formula_type=FORMULA_TYPE):
    proc = object.__new__(SavedQueryProcessor)
    proc.client = _Client()
    proc.as_is_element = as_is
    attributes = {"Display Name": {"value": "Assets with no lineage"},
                  "Query URL": {"value": "/api/open-metadata/metadata-expert/metadata-elements/by-search-conditions"},
                  "Query Request Body": {"value": json.dumps({"class": "FindRequestBody"})}}
    if formula is not None:
        attributes["Formula"] = {"value": formula}
    if formula_type is not None:
        attributes["Formula Type"] = {"value": formula_type}
    proc.parsed_output = {"attributes": attributes, "qualified_name": "SavedQuery::Assets-with-no-lineage"}

    async def _render(guid):
        return guid

    proc.render_result_markdown = _render
    asyncio.run(proc.apply_changes())
    return proc.client


def test_create_writes_formula_and_formula_type():
    client = _run()
    (types, body), = client.created
    assert types == ["SavedQueryProperties"]
    props = body["properties"]
    assert props["formula"] == FORMULA and props["formulaType"] == FORMULA_TYPE
    assert props["queryURL"].endswith("by-search-conditions")


def test_update_writes_formula_and_formula_type():
    client = _run(as_is={"elementHeader": {"guid": "sq-guid"}}, formula_type="egeria-insights-search-v1")
    (guid, body), = client.updated
    assert guid == "sq-guid" and body["class"] == "UpdateElementRequestBody"
    assert body["properties"]["formula"] == FORMULA
    assert body["properties"]["formulaType"] == FORMULA_TYPE


def test_without_them_nothing_is_invented():
    props = _run(formula=None, formula_type=None).created[0][1]["properties"]
    assert props.get("formula") is None and props.get("formulaType") is None
