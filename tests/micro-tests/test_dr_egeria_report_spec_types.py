# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dr.Egeria commands for Egeria 6.3's report specs, measurements and dashboards (odpi/egeria#9432):
Create Report Spec / Measurement Specification / Dashboard / Display Data Container / Display Data Field,
Link (and Detach) Basis Data Field / As Of Data Field / Report Type Instance / Report Run Of, and the
typed outputFormat / reportParameters on Create Report.

No live server: a fake client records the outgoing calls. The link/detach URL-level behaviour of the
four new relationships is also covered by test_data_designer_links.py, which iterates DATA_DESIGNER_LINKS.
"""
import json
from typing import Any, cast

import pytest

import md_processing.dr_egeria  # noqa: F401  (loads the compact command specs)
from md_processing.md_processing_utils.common_md_utils import set_collection_manager_body
from md_processing.md_processing_utils.md_processing_constants import COLLECTION_SUBTYPES
from md_processing.v2.data_designer import (
    DATA_DESIGNER_LINKS, DataDesignerLinkProcessor, DataValueSpecificationProcessor,
)
from md_processing.v2.extraction import DrECommand
from md_processing.v2.report import DashboardProcessor, ReportProcessor
from md_processing.v2.schema_maker import SchemaElementProcessor

GUID1 = "aaaaaaaa-0000-0000-0000-000000000001"
GUID2 = "bbbbbbbb-0000-0000-0000-000000000002"


class _Recorder:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def _record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return "cccccccc-0000-0000-0000-000000000003"
        return _record


class _FakeClient(_Recorder):
    def __init__(self):
        super().__init__()
        self.data_designer = _Recorder()
        self.schema_maker = _Recorder()
        self.classification_manager = _Recorder()


def _processor(cls, verb, object_type, om_type, attributes, as_is=None):
    client = _FakeClient()
    p = cls(client=cast(Any, client), command=DrECommand(verb=verb, object_type=object_type, attributes={},
                                                         raw_block=f"# {verb} {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": f"{om_type}::test", "attributes": attributes}
    p.as_is_element = as_is

    async def _render(guid):
        return guid
    p.render_result_markdown = _render
    return p, client


def _a(**values):
    return {k.replace("_", " "): {"value": v} for k, v in values.items()}


# ------------------------------------------------------------------ relationships

@pytest.mark.parametrize("om_type, end1, end2, method", [
    ("BasisDataField", "Measurement Specification", "Data Field", "_async_link_basis_data_field"),
    ("AsOfDataField", "Measurement Specification", "Data Field", "_async_link_as_of_data_field"),
    ("ReportTypeInstance", "Report Type", "Report", "_async_link_report_type_instance"),
    ("ReportRunOf", "Results Set", "Report", "_async_link_report_run_of"),
])
def test_link_table_entries(om_type, end1, end2, method):
    assert DATA_DESIGNER_LINKS[om_type][:3] == (end1, end2, method)


@pytest.mark.asyncio
async def test_report_run_of_sends_result_state():
    attributes = {"Results Set": {"guid": GUID1}, "Report": {"guid": GUID2},
                  **_a(Label="run 1", Result_State="complete", Result_State_Reason="ok",
                       Result_Location="file:///r.json")}
    p, client = _processor(DataDesignerLinkProcessor, "Link", "Report Run Of", "ReportRunOf", attributes)
    await p.apply_changes()

    (method, args, _), = client.data_designer.calls
    assert method == "_async_link_report_run_of"
    assert args[:2] == (GUID1, GUID2)
    assert args[2]["properties"] == {"class": "ReportRunOfProperties", "label": "run 1",
                                     "resultState": "complete", "resultStateReason": "ok",
                                     "resultLocation": "file:///r.json"}


# ------------------------------------------------------------------ Measurement Specification

@pytest.mark.asyncio
async def test_create_measurement_specification():
    attributes = _a(Display_Name="term count", Units="terms", Completeness_Declared="lower_bound",
                    Confidence_Form="measured", Uncertainty_Form="plus_minus")
    attributes["Absence Sentences"] = {"value": {"nothing_found": "No terms.", "not_measured": "Not counted."}}
    p, client = _processor(DataValueSpecificationProcessor, "Create", "Measurement Specification",
                           "MeasurementSpecification", attributes)
    await p.apply_changes()

    (method, args, _), = client.data_designer.calls
    assert method == "_async_create_data_value_specification"
    props = args[0]["properties"]
    assert props["class"] == "MeasurementSpecificationProperties"
    assert props["completenessDeclared"] == "lower_bound"
    assert props["confidenceForm"] == "measured"
    assert props["uncertaintyForm"] == "plus_minus"
    assert props["absenceSentences"]["not_measured"] == "Not counted."
    assert props["units"] == "terms"


@pytest.mark.asyncio
async def test_plain_data_value_specification_has_no_measurement_fields():
    p, client = _processor(DataValueSpecificationProcessor, "Create", "Data Value Specification",
                           "DataValueSpecification", _a(Display_Name="dvs"))
    await p.apply_changes()
    props = client.data_designer.calls[0][1][0]["properties"]
    assert "completenessDeclared" not in props


# ------------------------------------------------------------------ Report Spec

def test_report_spec_routes_as_collection_subtype():
    assert "Report Spec" in COLLECTION_SUBTYPES


def test_report_spec_body():
    attributes = _a(Display_Name="Glossaries", Microflow='[{"function": "find_glossaries"}]',
                    Target_Type_Name="Glossary", Include_Preamble=False)
    attributes["Output Types"] = {"value": ["MD", "JSON"]}
    attributes["Aliases"] = {"value": ["Glossary List"]}
    body = set_collection_manager_body("ReportSpec", "ReportSpec::Glossaries", attributes)
    assert body["class"] == "ReportSpecProperties"
    # RS-EGERIA-TIER: a bare list (format 0) is written as microflow/1
    assert json.loads(body["microflow"]) == {"format": "microflow/1", "params": {},
                                             "stages": [{"stage": "producer/find", "function": "find_glossaries",
                                                         "params": {}}],
                                             "formatters": {}}
    assert body["targetTypeName"] == "Glossary"
    assert body["outputTypes"] == ["MD", "JSON"]
    assert body["includePreamble"] is False
    assert body["aliases"] == ["Glossary List"]


# ------------------------------------------------------------------ Dashboard and Report

@pytest.mark.asyncio
async def test_create_dashboard():
    attributes = _a(Display_Name="Ops", Refresh_Time_Interval=15, Layout_Style="grid")
    attributes["Aliases"] = {"value": ["Operations"]}
    p, client = _processor(DashboardProcessor, "Create", "Dashboard", "Dashboard", attributes)
    await p.apply_changes()

    (method, args, _), = client.calls
    assert method == "_async_create_asset"
    assert args[0] == ["DashboardProperties"]
    props = args[1]["properties"]
    assert props["class"] == "DashboardProperties"
    assert props["refreshTimeInterval"] == 15
    assert props["layoutStyle"] == "grid"
    assert props["aliases"] == ["Operations"]


@pytest.mark.asyncio
async def test_update_dashboard():
    p, client = _processor(DashboardProcessor, "Update", "Dashboard", "Dashboard",
                           _a(Display_Name="Ops", Layout_Style="columns"),
                           as_is={"elementHeader": {"guid": GUID1}})
    await p.apply_changes()
    (method, args, _), = client.calls
    assert method == "_async_update_asset"
    assert args[0] == GUID1
    assert args[1]["properties"]["layoutStyle"] == "columns"


@pytest.mark.asyncio
async def test_create_report_writes_typed_output_format_and_parameters():
    attributes = _a(Display_Name="Clinical terms", Report_Spec="Glossary-Terms", Output_Format="REPORT-GRAPH")
    attributes["Report Parameters"] = {"value": {"collection_guid": "c-1"}}
    p, client = _processor(ReportProcessor, "Create", "Report", "Report", attributes)
    await p.apply_changes()

    (method, args, _), = client.calls
    assert method == "_async_create_asset"
    props = args[1]["properties"]
    assert props["outputFormat"] == "REPORT-GRAPH"
    assert json.loads(props["reportParameters"]) == {"collection_guid": "c-1"}
    # the additionalProperties keys the Portal reads are kept
    assert props["additionalProperties"]["outputFormat"] == "REPORT-GRAPH"
    assert props["additionalProperties"]["collectionGuid"] == "c-1"


# ------------------------------------------------------------------ Display Data Container / Field

@pytest.mark.asyncio
async def test_create_display_data_container():
    attributes = _a(Display_Name="TABLE", Renderer="table", Placement_Kind="inline", Span="2",
                    Presentation_Style="card", Markdown_Content="# Summary")
    p, client = _processor(SchemaElementProcessor, "Create", "Display Data Container", "DisplayDataContainer",
                           attributes)
    await p.apply_changes()

    (method, args, _), = client.schema_maker.calls
    assert method == "_async_create_schema_attribute"
    props = args[0]["properties"]
    assert props["class"] == "DisplayDataContainerProperties"
    assert props["typeName"] == "DisplayDataContainer"
    assert (props["renderer"], props["placementKind"], props["span"], props["presentationStyle"],
            props["markdownContent"]) == ("table", "inline", "2", "card", "# Summary")
    assert "inputField" not in props


@pytest.mark.asyncio
async def test_create_display_data_field():
    attributes = _a(Display_Name="tile", Input_Field=False, Presentation_Style="kpi")
    p, client = _processor(SchemaElementProcessor, "Create", "Display Data Field", "DisplayDataField",
                           attributes)
    await p.apply_changes()
    props = client.schema_maker.calls[0][1][0]["properties"]
    assert props["class"] == "DisplayDataFieldProperties"
    assert props["inputField"] is False
    assert props["presentationStyle"] == "kpi"
    assert "renderer" not in props


@pytest.mark.asyncio
async def test_plain_schema_attribute_unchanged():
    p, client = _processor(SchemaElementProcessor, "Create", "Schema Attribute", "SchemaAttribute",
                           _a(Display_Name="col"))
    await p.apply_changes()
    props = client.schema_maker.calls[0][1][0]["properties"]
    assert props["class"] == "SchemaAttributeProperties"
    assert "placementKind" not in props


# ------------------------------------------------------------------ specs and registration

NEW_COMMANDS = {
    "Create Report Spec": "ReportSpec",
    "Create Measurement Specification": "MeasurementSpecification",
    "Create Dashboard": "Dashboard",
    "Create Display Data Container": "DisplayDataContainer",
    "Create Display Data Field": "DisplayDataField",
    "Link Basis Data Field": "BasisDataField",
    "Link As Of Data Field": "AsOfDataField",
    "Link Report Type Instance": "ReportTypeInstance",
    "Link Report Run Of": "ReportRunOf",
}


@pytest.mark.parametrize("command, om_type", NEW_COMMANDS.items())
def test_compact_spec_command(command, om_type):
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec
    spec = get_command_spec(command)
    assert spec, command
    assert spec["OM_TYPE"] == om_type


@pytest.mark.parametrize("command", list(NEW_COMMANDS) + [
    "Update Report Spec", "Update Measurement Specification", "Update Dashboard",
    "Detach Basis Data Field", "Detach As Of Data Field", "Detach Report Type Instance", "Detach Report Run Of",
])
def test_dispatcher_registers(command):
    from md_processing.dr_egeria import setup_dispatcher
    dispatcher = setup_dispatcher(cast(Any, _FakeClient()))
    verb, _, object_type = command.partition(" ")
    cls = dispatcher.resolve_processor_class(
        DrECommand(verb=verb, object_type=object_type, attributes={}, raw_block=""))
    assert cls is not None, command


def test_output_format_list_covers_the_report_format_registry():
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec
    from pyegeria.view.base_report_formats import get_report_registry
    spec = get_command_spec("Create Report")
    attr = next(a for a in spec["Attributes"] if a.get("name") == "Output Format")
    # DOCUMENT (SD-1/SD-2) is not offered by Create Report yet: rendering a document report is SD-3
    # (Portal/EA), so a Report's Output Format cannot name it until then.
    registry_types = {t for fs in get_report_registry().values() for f in fs.formats for t in f.types} - {"ALL", "DOCUMENT"}
    assert registry_types <= set(attr["valid_values"])
    assert "KPI" in attr["valid_values"]
    assert attr["property_name"] == "outputFormat"


@pytest.mark.parametrize("command, expected", [
    ("Create Dashboard", "DashboardProcessor"),
    ("Update Dashboard", "DashboardProcessor"),
    ("Create Dashboard Sheet", "CreateDashboardSheetProcessor"),
    ("Create Report Spec", "CollectionManagerProcessor"),
    ("Create Measurement Specification", "DataValueSpecificationProcessor"),
    ("Create Display Data Container", "SchemaElementProcessor"),
    ("Create Display Data Field", "SchemaElementProcessor"),
    ("Link Basis Data Field", "DataDesignerLinkProcessor"),
    ("Link Report Run Of", "DataDesignerLinkProcessor"),
    ("Detach Report Type Instance", "DataDesignerLinkProcessor"),
])
def test_dispatcher_routes_to_the_right_processor(command, expected):
    # Found live 2026-11-07: "Create Dashboard Sheet" had the alternate name "Dashboard", whose alias
    # registration took over the "Create Dashboard" key, so an Egeria Dashboard was silently written as
    # a local Dashboard Sheet record instead.
    from md_processing.dr_egeria import setup_dispatcher
    dispatcher = setup_dispatcher(cast(Any, _FakeClient()))
    verb, _, object_type = command.partition(" ")
    cls = dispatcher.resolve_processor_class(
        DrECommand(verb=verb, object_type=object_type, attributes={}, raw_block=""))
    assert cls is not None and cls.__name__ == expected, (command, cls)


# ------------------------------------------------------------------ Report Spec microflow/1 (RS-EGERIA-TIER)

_E_COLLECTIONS_FORMAT0 = json.dumps([{
    "stage": "producer/find", "type": "Collection", "function": "CollectionManager.find_collections",
    "params": {"search_string": "$search_string"}, "required_params": ["search_string"],
    "optional_params": ["page_size", "start_from"], "out": "CollectionRow",
    "columns": ["display_name", "qualified_name"]}])


def test_report_spec_microflow_bare_list_is_converted_with_microflow_from_legacy():
    from pyegeria.view.microflow import microflow_from_legacy
    body = set_collection_manager_body("ReportSpec", "ReportSpec::E-Collections",
                                       _a(Display_Name="E-Collections", Microflow=_E_COLLECTIONS_FORMAT0))
    stored = json.loads(body["microflow"])
    assert stored == json.loads(microflow_from_legacy(json.loads(_E_COLLECTIONS_FORMAT0)).to_json())
    assert stored["format"] == "microflow/1"
    assert stored["params"]["search_string"]["required"] is True
    assert stored["formatters"]["ALL"]["columns"] == ["display_name", "qualified_name"]


def test_report_spec_microflow_object_is_validated_and_kept():
    obj = {"format": "microflow/1", "params": {"search_string": {"type": "string", "required": True}},
           "stages": [{"stage": "producer/find", "function": "CollectionManager.find_collections",
                       "params": {"search_string": "$search_string"}}],
           "formatters": {"DICT": {"columns": [{"field": "display_name", "label": "Display Name"}]}}}
    body = set_collection_manager_body("ReportSpec", "ReportSpec::X",
                                       _a(Display_Name="X", Microflow=json.dumps(obj)))
    assert json.loads(body["microflow"]) == obj


@pytest.mark.parametrize("text,words", [
    ("[{not json", "not valid JSON"),
    ('{"format": "microflow/7", "stages": []}', "unknown microflow format"),
    ('{"format": "microflow/1", "stages": [{"stage": "producer/find"}], "extra": 1}', "not valid"),
])
def test_report_spec_microflow_invalid_is_an_error_with_words(text, words):
    with pytest.raises(ValueError, match=f"Microflow: .*{words}"):
        set_collection_manager_body("ReportSpec", "ReportSpec::X", _a(Display_Name="X", Microflow=text))


def test_report_spec_microflow_error_fails_preflight_validation():
    from md_processing.v2.collection_manager_processor import CollectionManagerProcessor
    p, _ = _processor(CollectionManagerProcessor, "Create", "Report Spec", "ReportSpec",
                      _a(Display_Name="X", Microflow="[{not json"))
    p.canonical_object_type = "Report Spec"
    errors = p.check_parsed_attributes(p.parsed_output["attributes"])
    assert len(errors) == 1 and "Report Spec 'X': Microflow: the microflow is not valid JSON" in errors[0]
    ok, _ = _processor(CollectionManagerProcessor, "Create", "Report Spec", "ReportSpec",
                       _a(Display_Name="X", Microflow=_E_COLLECTIONS_FORMAT0))
    ok.canonical_object_type = "Report Spec"
    assert ok.check_parsed_attributes(ok.parsed_output["attributes"]) == []
    other, _ = _processor(CollectionManagerProcessor, "Create", "Collection Folder", "CollectionFolder",
                          _a(Display_Name="X", Microflow="[{not json"))
    other.canonical_object_type = "Collection Folder"
    assert other.check_parsed_attributes(other.parsed_output["attributes"]) == []
