# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Client support for Egeria 6.3's report-spec, measurement and dashboard types (odpi/egeria#9432):
ReportSpec, MeasurementSpecification, Dashboard; the BasisDataField, AsOfDataField, ReportTypeInstance
and ReportRunOf relationships; the new Report / DisplayDataContainer / DisplayDataField attributes.

No network: _async_make_request is replaced by a recorder. URLs and body classes are checked against
the Data Designer .http file and the Java beans in that PR.
"""
import json

import pytest

from pyegeria.models import (
    AsOfDataFieldProperties,
    BasisDataFieldProperties,
    DashboardProperties,
    DataValueSpecificationProperties,
    MeasurementSpecificationProperties,
    ReportProperties,
    ReportRunOfProperties,
    ReportTypeInstanceProperties,
)
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.collection_manager import CollectionManager, ReportSpecProperties
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.schema_maker import (
    DisplayDataContainerProperties,
    DisplayDataFieldProperties,
    SchemaMaker,
)

DD_BASE = "https://localhost:1/servers/view-server/api/open-metadata/data-designer"


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "new-guid"}


def _client(cls, sent: list, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    monkeypatch.delenv("EGERIA_LOCAL_QUALIFIER", raising=False)
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    client.local_qualifier = None

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        sent.append({"method": method, "url": url,
                     "body": json.loads(body) if isinstance(body, str) else body})
        return _Response()

    client._async_make_request = fake_make_request
    return client


# ---------------------------------------------------------------------------------------------------
# Properties models: the "class" string must be the Java bean name (pyegeria #537)
# ---------------------------------------------------------------------------------------------------

MODELS = [
    DataValueSpecificationProperties, MeasurementSpecificationProperties, ReportProperties,
    DashboardProperties, BasisDataFieldProperties, AsOfDataFieldProperties,
    ReportTypeInstanceProperties, ReportRunOfProperties, ReportSpecProperties,
    DisplayDataContainerProperties, DisplayDataFieldProperties,
]


@pytest.mark.parametrize("model", MODELS, ids=[m.__name__ for m in MODELS])
def test_class_string_is_java_bean_name(model):
    annotation = model.model_fields["class_"].annotation
    assert annotation.__args__ == (model.__name__,)


def test_measurement_specification_serializes_new_fields():
    props = MeasurementSpecificationProperties(
        class_="MeasurementSpecificationProperties", qualified_name="MS::count", display_name="count",
        units="elements", completeness_declared="lower_bound", confidence_form="measured",
        uncertainty_form="plus_minus",
        absence_sentences={"nothing_found": "None found.", "not_measured": "Not measured."},
    ).model_dump(exclude_none=True)
    assert props["class"] == "MeasurementSpecificationProperties"
    assert props["completenessDeclared"] == "lower_bound"
    assert props["confidenceForm"] == "measured"
    assert props["uncertaintyForm"] == "plus_minus"
    assert props["absenceSentences"]["not_measured"] == "Not measured."
    assert props["units"] == "elements"
    # owner decision: the state set and basis/as-of fields are relationships, not properties
    for gone in ("stateSet", "basisField", "asOfField"):
        assert gone not in props


def test_dashboard_keeps_undeclared_asset_fields_and_no_injected_metadata():
    props = DashboardProperties(
        class_="DashboardProperties", qualified_name="Dashboard::ops", display_name="ops",
        aliases=["Ops"], refresh_time_interval=15, layout_style="grid", resourceName="ops-dash",
    ).model_dump(exclude_none=True)
    assert props["refreshTimeInterval"] == 15
    assert props["layoutStyle"] == "grid"
    assert props["aliases"] == ["Ops"]
    assert props["resourceName"] == "ops-dash"  # extra='allow': not silently dropped
    assert "metadata" not in props


def test_report_new_fields():
    props = ReportProperties(
        class_="ReportProperties", qualified_name="Report::g", display_name="g",
        output_format="REPORT-GRAPH", report_parameters='{"search_string": "Clinical"}',
    ).model_dump(exclude_none=True)
    assert props["outputFormat"] == "REPORT-GRAPH"
    assert json.loads(props["reportParameters"]) == {"search_string": "Clinical"}


def test_display_data_models_new_fields():
    container = DisplayDataContainerProperties(
        class_="DisplayDataContainerProperties", qualified_name="DDC::sheet", display_name="sheet",
        renderer="table", placement_kind="inline", span="2", presentation_style="card",
        markdown_content="# Summary",
    ).model_dump(exclude_none=True)
    assert {k: container[k] for k in ("renderer", "placementKind", "span", "presentationStyle",
                                      "markdownContent")} == {
        "renderer": "table", "placementKind": "inline", "span": "2", "presentationStyle": "card",
        "markdownContent": "# Summary"}

    field = DisplayDataFieldProperties(
        class_="DisplayDataFieldProperties", qualified_name="DDF::tile", display_name="tile",
        input_field=False, placement_kind="report", span="1", presentation_style="kpi",
    ).model_dump(exclude_none=True)
    assert field["inputField"] is False
    assert field["presentationStyle"] == "kpi"
    assert "renderer" not in DisplayDataFieldProperties.model_fields


# ---------------------------------------------------------------------------------------------------
# The four relationships: URL, verb and default properties class
# ---------------------------------------------------------------------------------------------------

LINKS = [
    ("basis_data_field", "data-value-specifications/ms-1/basis-data-fields/df-2", "BasisDataFieldProperties"),
    ("as_of_data_field", "data-value-specifications/ms-1/as-of-data-fields/df-2", "AsOfDataFieldProperties"),
    ("report_type_instance", "report-types/ms-1/report-type-instances/df-2", "ReportTypeInstanceProperties"),
    ("report_run_of", "results-sets/ms-1/report-runs/df-2", "ReportRunOfProperties"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("name, path, props_class", LINKS, ids=[l[0] for l in LINKS])
async def test_link_default_body(name, path, props_class, monkeypatch):
    sent: list = []
    client = _client(DataDesigner, sent, monkeypatch)

    guid = await getattr(client, f"_async_link_{name}")("ms-1", "df-2")

    assert guid == "new-guid"
    assert sent[0]["method"] == "POST"
    assert sent[0]["url"] == f"{DD_BASE}/{path}/attach"
    assert sent[0]["body"]["class"] == "NewRelationshipRequestBody"
    assert sent[0]["body"]["properties"]["class"] == props_class


@pytest.mark.asyncio
@pytest.mark.parametrize("name, path, props_class", LINKS, ids=[l[0] for l in LINKS])
async def test_detach(name, path, props_class, monkeypatch):
    sent: list = []
    client = _client(DataDesigner, sent, monkeypatch)

    await getattr(client, f"_async_detach_{name}")("ms-1", "df-2")

    assert sent[0]["method"] == "POST"
    assert sent[0]["url"] == f"{DD_BASE}/{path}/detach"


@pytest.mark.parametrize("name", [l[0] for l in LINKS])
def test_sync_wrappers_exist(name):
    assert callable(getattr(DataDesigner, f"link_{name}"))
    assert callable(getattr(DataDesigner, f"detach_{name}"))


@pytest.mark.asyncio
async def test_report_run_of_carries_result_state(monkeypatch):
    sent: list = []
    client = _client(DataDesigner, sent, monkeypatch)
    body = {
        "class": "NewRelationshipRequestBody",
        "properties": ReportRunOfProperties(
            class_="ReportRunOfProperties", label="run 1", result_state="nothing_found",
            result_state_reason="no glossaries", result_location="file:///tmp/r.json",
        ).model_dump(exclude_none=True),
    }

    await client._async_link_report_run_of("rs-1", "report-2", body)

    props = sent[0]["body"]["properties"]
    assert sent[0]["url"] == f"{DD_BASE}/results-sets/rs-1/report-runs/report-2/attach"
    assert props == {"class": "ReportRunOfProperties", "label": "run 1", "resultState": "nothing_found",
                     "resultStateReason": "no glossaries", "resultLocation": "file:///tmp/r.json"}


# ---------------------------------------------------------------------------------------------------
# Create / update paths
# ---------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_measurement_specification_created_through_data_value_specifications(monkeypatch):
    sent: list = []
    client = _client(DataDesigner, sent, monkeypatch)
    body = {
        "class": "NewElementRequestBody",
        "properties": {
            "class": "MeasurementSpecificationProperties",
            "qualifiedName": "MeasurementSpecification::term-count",
            "displayName": "term count",
            "completenessDeclared": "complete",
            "absenceSentences": {"nothing_found": "No terms."},
        },
    }

    guid = await client._async_create_data_value_specification(body)

    assert guid == "new-guid"
    assert sent[0]["url"] == f"{DD_BASE}/data-value-specifications"
    props = sent[0]["body"]["properties"]
    assert props["class"] == "MeasurementSpecificationProperties"
    assert props["completenessDeclared"] == "complete"
    assert props["absenceSentences"] == {"nothing_found": "No terms."}


@pytest.mark.asyncio
async def test_measurement_specification_update(monkeypatch):
    sent: list = []
    client = _client(DataDesigner, sent, monkeypatch)
    body = {"class": "UpdateElementRequestBody", "mergeUpdate": True,
            "properties": {"class": "MeasurementSpecificationProperties", "confidenceForm": "estimated"}}

    await client._async_update_data_value_specification("ms-1", body)

    assert sent[0]["url"] == f"{DD_BASE}/data-value-specifications/ms-1/update"
    assert sent[0]["body"]["properties"]["confidenceForm"] == "estimated"


@pytest.mark.asyncio
async def test_create_report_spec_from_arguments(monkeypatch):
    sent: list = []
    client = _client(CollectionManager, sent, monkeypatch)
    microflow = json.dumps([{"function": "find_glossaries", "params": {"search_string": "*"}}])

    guid = await client._async_create_report_spec(
        display_name="Glossaries", description="All glossaries", category="Glossary",
        microflow=microflow, target_type_name="Glossary", aliases=["Glossary List"],
        output_types=["MD", "JSON"], include_preamble=False)

    assert guid == "new-guid"
    assert sent[0]["method"] == "POST"
    assert sent[0]["url"].endswith("/api/open-metadata/collection-manager/collections")
    body = sent[0]["body"]
    assert body["isOwnAnchor"] is True
    props = body["properties"]
    assert props["class"] == "ReportSpecProperties"
    assert props["qualifiedName"] == "ReportSpec::Glossaries"
    assert props["microflow"] == microflow
    assert props["targetTypeName"] == "Glossary"
    assert props["outputTypes"] == ["MD", "JSON"]
    assert props["includePreamble"] is False  # an explicit False is sent, not dropped
    assert props["aliases"] == ["Glossary List"]


@pytest.mark.asyncio
async def test_create_report_spec_from_body(monkeypatch):
    sent: list = []
    client = _client(CollectionManager, sent, monkeypatch)
    body = {"class": "NewElementRequestBody", "isOwnAnchor": True,
            "properties": {"class": "ReportSpecProperties", "qualifiedName": "ReportSpec::x",
                           "displayName": "x", "microflow": "[]"}}

    await client._async_create_report_spec(body=body)

    assert sent[0]["body"]["properties"] == body["properties"]


@pytest.mark.asyncio
async def test_dashboard_created_through_asset_maker(monkeypatch):
    sent: list = []
    client = _client(AssetMaker, sent, monkeypatch)
    props = DashboardProperties(class_="DashboardProperties", qualified_name="Dashboard::ops",
                                display_name="ops", refresh_time_interval=60, layout_style="grid")
    body = {"class": "NewElementRequestBody", "isOwnAnchor": True,
            "properties": props.model_dump(exclude_none=True)}

    await client._async_create_asset(["DashboardProperties"], body)

    assert sent[0]["url"].endswith("/api/open-metadata/asset-maker/assets")
    assert sent[0]["body"]["properties"] == {"class": "DashboardProperties", "qualifiedName": "Dashboard::ops",
                                             "displayName": "ops", "refreshTimeInterval": 60,
                                             "layoutStyle": "grid"}


@pytest.mark.asyncio
async def test_display_data_container_through_schema_maker(monkeypatch):
    sent: list = []
    client = _client(SchemaMaker, sent, monkeypatch)
    props = DisplayDataContainerProperties(class_="DisplayDataContainerProperties", qualified_name="DDC::t",
                                           display_name="TABLE", renderer="table", placement_kind="inline")
    body = {"class": "NewElementRequestBody", "properties": props.model_dump(exclude_none=True)}

    await client._async_create_schema_attribute(body)

    assert sent[0]["url"].endswith("/api/open-metadata/schema-maker/schema-attributes")
    assert sent[0]["body"]["properties"]["renderer"] == "table"
    assert sent[0]["body"]["properties"]["placementKind"] == "inline"


# ---------------------------------------------------------------------------------------------------
# Report specs so run_report / Dr.Egeria Display can show the new types
# ---------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("label, function, spec_params", [
    ("Report-Specs", "CollectionManager.find_collections", {"metadata_element_subtypes": ["ReportSpec"]}),
    ("Measurement-Specifications", "DataDesigner.find_data_value_specifications",
     {"metadata_element_subtypes": ["MeasurementSpecification"]}),
    ("Dashboards", "MetadataExpert.find_metadata_elements_with_string", {"metadata_element_type": "Dashboard"}),
])
def test_report_specs_registered(label, function, spec_params):
    from pyegeria.view.base_report_formats import base_report_specs

    fs = base_report_specs[label]
    assert fs.action.function == function
    assert fs.action.spec_params == spec_params
