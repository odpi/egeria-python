# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Reference Data authoring (Create Reference Data Set/Value, the valid-value
relationship links) and the Valid Metadata family split out of Reference Data.
No live server: the Egeria client is a fake that records calls.
"""
import json
from pathlib import Path
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.reference_data import (
    ReferenceDataElementProcessor,
    ReferenceDataLinkProcessor,
    ValidMetadataValueProcessor,
    ValidValueLinkProcessor,
)
from md_processing.v2.utils import parse_line_list, parse_table

SPEC_DIR = Path(__file__).resolve().parents[2] / "md_processing" / "data" / "compact_commands"


# ── parsing ────────────────────────────────────────────────────────────────────

def test_parse_table_rows_keyed_by_header():
    rows = parse_table("| Value | Display Name | Default |\n|:---|---|---:|\n"
                       "| PENDING | Pending | true |\n| SHIP\\|PED | Shipped, D.C. |  |\n| | | |")
    assert rows == [{"Value": "PENDING", "Display Name": "Pending", "Default": "true"},
                    {"Value": "SHIP|PED", "Display Name": "Shipped, D.C.", "Default": None}]


def test_parse_table_not_a_table():
    assert parse_table("just text") == []
    assert parse_table("| only a header |") == []


def test_parse_line_list_keeps_commas():
    assert parse_line_list("- PENDING\n- Washington, D.C.\n\n* A; B\nPLAIN") == [
        "PENDING", "Washington, D.C.", "A; B", "PLAIN"]


# ── specs ──────────────────────────────────────────────────────────────────────

def _family(stem):
    return json.loads((SPEC_DIR / f"{stem}.json").read_text())


def test_valid_metadata_commands_moved_to_their_own_family():
    rd, vm = _family("commands_reference_data_compact"), _family("commands_valid_metadata_compact")
    moved = {"Setup Valid Metadata Value", "Clear Valid Metadata Value", "Setup Valid Metadata Map Name",
             "Clear Valid Metadata Map Name", "Setup Valid Metadata Map Value", "Clear Valid Metadata Map Value",
             "Set Consistent Metadata Values", "Link Specification Property Assignment",
             "Detach Specification Property Assignment"}
    assert vm["family"] == "Valid Metadata"
    assert moved <= set(vm["commands"])
    assert not moved & set(rd["commands"])
    assert all(vm["commands"][c]["family"] == "Valid Metadata" for c in moved)


def test_reference_data_commands_and_styles():
    rd = _family("commands_reference_data_compact")
    for name in ("Create Reference Data Set", "Create Reference Data Value", "Link Valid Value Member",
                 "Detach Valid Value Member", "Link Consistent Valid Values", "Link Associated Valid Values",
                 "Link Mapped Valid Values", "Link Valid Value Implementation"):
        assert name in rd["commands"], name
    attrs = rd["attribute_definitions"]
    assert attrs["Value Table"]["style"] == "Table"
    assert attrs["Values"]["style"] == "Line List"
    assert attrs["Members"]["style"] == "Reference Name List"
    assert attrs["Preferred Value"]["input_required"] is False
    assert rd["commands"]["Create Reference Data Set"]["OM_TYPE"] == "ReferenceDataSet"


def test_shared_attribute_copies_are_identical_across_families():
    # Attribute names are one global namespace (last file wins), so a copy that
    # drifts would silently change other families' commands.
    seen = {}
    for path in sorted(SPEC_DIR.glob("*.json")):
        for name, definition in json.loads(path.read_text()).get("attribute_definitions", {}).items():
            seen.setdefault(name, []).append((path.stem, definition))
    for stem in ("commands_reference_data_compact", "commands_valid_metadata_compact"):
        for name, definition in _family(stem)["attribute_definitions"].items():
            if name == "Element Id":  # Reference Data's own copy predates this change
                continue
            others = [d for s, d in seen[name] if s != stem]
            winner = seen[name][-1][1]
            assert not others or definition == winner or not definition.get("valid_values") and winner.get(
                "valid_values"), f"{name} in {stem} differs from the winning definition"


# ── fake client ────────────────────────────────────────────────────────────────

def _g(n: int) -> str:
    return f"00000000-0000-0000-0000-{n:012d}"


class _RefData:
    def __init__(self):
        self.calls = []
        self._n = 0

    async def _async_create_valid_value_definition(self, body):
        self._n += 1
        self.calls.append(("create", body))
        return _g(self._n)

    async def _async_update_valid_value_definition(self, guid, body):
        self.calls.append(("update", guid, body))

    def __getattr__(self, name):
        if name.startswith("_async_"):
            async def method(*args):
                self.calls.append((name[len("_async_"):],) + args)
            return method
        raise AttributeError(name)


class _ValidMetadata:
    def __init__(self):
        self.calls = []

    async def _async_setup_valid_metadata_value(self, property_name, type_name, body):
        self.calls.append((property_name, type_name, body))


class _Client:
    def __init__(self, current_members=None):
        self.reference_data = _RefData()
        self.valid_metadata = _ValidMetadata()
        self._current = current_members or []

    async def _async_get_related_metadata_elements(self, guid, rel, body, **kwargs):
        return {"elementList": [
            {"element": {"elementGUID": g},
             "relationshipProperties": {"propertiesAsStrings": {"isDefaultValue": str(d).lower(),
                                                                "ordinal": str(o)}}}
            for g, d, o in self._current]}


async def _rendered(guid):
    return guid


def _processor(cls, client, verb, object_type, attributes, om_type="", qualified_name=None, as_is=None):
    p = cls(client=cast(Any, client),
            command=DrECommand(verb=verb, object_type=object_type, attributes={},
                               raw_block=f"## {verb} {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": qualified_name, "attributes": attributes}
    p.as_is_element = as_is
    p.render_result_markdown = _rendered

    async def resolve(qn, tech_type=None):
        return None
    p.resolve_element_guid = resolve
    return p


def _a(**kv):
    return {k.replace("_", " "): (v if isinstance(v, dict) else {"value": v}) for k, v in kv.items()}


# ── Create Reference Data Set ──────────────────────────────────────────────────

async def test_create_set_creates_inline_values_and_links_members():
    client = _Client()
    attrs = _a(Display_Name="Order Status", Values=["PENDING", "Washington, D.C."],
               Value_Table=[{"Value": "SHIPPED", "Description": "Left", "Default": "true", "Ordinal": "9"}],
               Default_Member="PENDING")
    attrs["Members"] = {"value": ["Existing"], "guid_list": ["existing-guid"]}
    p = _processor(ReferenceDataElementProcessor, client, "Create", "Reference Data Set", attrs,
                   "ReferenceDataSet", "ReferenceDataSet::Order Status")
    assert await p.apply_changes() == _g(1)

    calls = client.reference_data.calls
    creates = [c[1]["properties"] for c in calls if c[0] == "create"]
    assert creates[0]["class"] == "ReferenceDataSetProperties"
    assert [(c["class"], c["qualifiedName"], c["preferredValue"]) for c in creates[1:]] == [
        ("ReferenceDataValueProperties", "ReferenceDataSet::Order Status::PENDING", "PENDING"),
        ("ReferenceDataValueProperties", "ReferenceDataSet::Order Status::Washington, D.C.", "Washington, D.C."),
        ("ReferenceDataValueProperties", "ReferenceDataSet::Order Status::SHIPPED", "SHIPPED"),
    ]
    links = {c[2]: c[3]["properties"] for c in calls if c[0] == "link_valid_value_member"}
    assert set(links) == {"existing-guid", _g(2), _g(3), _g(4)}
    assert links["existing-guid"].get("ordinal") == 1
    assert links[_g(2)].get("isDefaultValue") is True and links[_g(2)]["ordinal"] == 2
    assert links[_g(4)].get("isDefaultValue") is True and links[_g(4)]["ordinal"] == 9
    assert not any(c[0] == "detach_valid_value_member" for c in calls)


async def test_rerun_unlinks_dropped_members_and_skips_unchanged():
    client = _Client(current_members=[("keep", False, 1), ("dropped", False, 2)])
    attrs = _a(Display_Name="Order Status")
    attrs["Members"] = {"value": ["Keep"], "guid_list": ["keep"]}
    p = _processor(ReferenceDataElementProcessor, client, "Update", "Reference Data Set", attrs,
                   "ReferenceDataSet", "ReferenceDataSet::Order Status",
                   as_is={"elementHeader": {"guid": "set-guid"}})
    await p.apply_changes()
    calls = client.reference_data.calls
    assert calls[0][0] == "update" and calls[0][1] == "set-guid"
    assert not any(c[0] == "link_valid_value_member" for c in calls)  # unchanged -> no relink
    assert [c[1:3] for c in calls if c[0] == "detach_valid_value_member"] == [("set-guid", "dropped")]


async def test_update_without_member_attributes_leaves_membership_alone():
    client = _Client(current_members=[("keep", False, 1)])
    p = _processor(ReferenceDataElementProcessor, client, "Update", "Reference Data Set",
                   _a(Display_Name="Order Status", Description="new"), "ReferenceDataSet",
                   "ReferenceDataSet::Order Status", as_is={"elementHeader": {"guid": "set-guid"}})
    await p.apply_changes()
    assert [c[0] for c in client.reference_data.calls] == ["update"]


async def test_create_value_joins_its_set():
    client = _Client()
    attrs = _a(Display_Name="PENDING", Preferred_Value="PENDING", Is_Default_Member=True, Member_Ordinal=3)
    attrs["In Reference Data Set"] = {"value": "Order Status", "guid": "set-guid"}
    p = _processor(ReferenceDataElementProcessor, client, "Create", "Reference Data Value", attrs,
                   "ReferenceDataValue", "ReferenceDataValue::PENDING")
    await p.apply_changes()
    create, link = client.reference_data.calls
    assert create[1]["properties"]["class"] == "ReferenceDataValueProperties"
    assert create[1]["properties"]["preferredValue"] == "PENDING"
    assert link[0] == "link_valid_value_member" and link[1:3] == ("set-guid", _g(1))
    assert link[3]["properties"] == {"class": "ValidValueMemberProperties", "isDefaultValue": True, "ordinal": 3}


# ── relationship links ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("verb, expected", [("Link", "link_mapped_valid_values"),
                                            ("Detach", "detach_mapped_valid_values")])
async def test_link_processor_branches_on_verb(verb, expected):
    client = _Client()
    attrs = _a(Association_Description="same meaning", Confidence="80")
    attrs["Valid Value 1"] = {"value": "a", "guid": "g1"}
    attrs["Valid Value 2"] = {"value": "b", "guid": "g2"}
    p = _processor(ValidValueLinkProcessor, client, verb, "Mapped Valid Values", attrs, "ValidValuesMapping")
    await p.apply_changes()
    (call,) = client.reference_data.calls
    assert call[0] == expected and call[1:3] == ("g1", "g2")
    if verb == "Link":
        assert call[3]["properties"] == {"class": "ValidValuesMappingProperties",
                                         "associationDescription": "same meaning", "confidence": 80}


async def test_link_implementation_properties():
    client = _Client()
    attrs = _a(Symbolic_Name="PEND", Implementation_Value="P")
    attrs["Valid Value"] = {"value": "PENDING", "guid": "vv"}
    attrs["Implementation Element"] = {"value": "orders.status", "guid": "col"}
    p = _processor(ValidValueLinkProcessor, client, "Link", "Valid Value Implementation", attrs,
                   "ValidValuesImplementation")
    await p.apply_changes()
    (call,) = client.reference_data.calls
    assert call[0] == "link_valid_value_implementation" and call[1:3] == ("vv", "col")
    assert call[3]["properties"] == {"class": "ValidValuesImplementationProperties",
                                     "symbolicName": "PEND", "implementationValue": "P"}


async def test_assignment_links_send_their_relationship_properties():
    client = _Client()
    attrs = _a(Attribute_Name="status", Confidence="70", Steward="erin", Notes="checked")
    attrs["Element Id"] = {"value": "ann", "guid": "ann-guid"}
    attrs["Reference Value"] = {"value": "PENDING", "guid": "vv"}
    p = _processor(ReferenceDataLinkProcessor, client, "Link", "Reference Value Assignment", attrs,
                   "ReferenceValueAssignment")
    await p.apply_changes()
    props = client.reference_data.calls[0][3]["properties"]
    assert props == {"class": "ReferenceValueAssignmentProperties", "attributeName": "status",
                     "confidence": 70, "steward": "erin", "notes": "checked"}

    client = _Client()
    attrs = {"Element Id": {"value": "f", "guid": "f-guid"}, "Valid Value Set": {"value": "s", "guid": "s-guid"}}
    p = _processor(ReferenceDataLinkProcessor, client, "Link", "Element to Valid Values", attrs,
                   "ValidValuesAssignment")
    await p.apply_changes()
    assert client.reference_data.calls[0][3]["properties"]["strictRequirement"] is True


# ── Valid Metadata ─────────────────────────────────────────────────────────────

async def test_setup_valid_metadata_value_table():
    client = _Client()
    attrs = _a(Metadata_Property_Name="projectHealth", Type_Name="Project",
               Metadata_Value_Table=[{"Preferred Value": "On Track", "Description": "fine"},
                                     {"Preferred Value": "At Risk"}, {"Description": "no value"}])
    p = _processor(ValidMetadataValueProcessor, client, "Setup", "Valid Metadata Value", attrs)
    await p.apply_changes()
    assert client.valid_metadata.calls == [
        ("projectHealth", "Project", {"displayName": "On Track", "description": "fine", "preferredValue": "On Track"}),
        ("projectHealth", "Project", {"displayName": "At Risk", "description": None, "preferredValue": "At Risk"}),
    ]


async def test_setup_valid_metadata_value_needs_a_value():
    p = _processor(ValidMetadataValueProcessor, _Client(), "Setup", "Valid Metadata Value",
                   _a(Metadata_Property_Name="projectHealth"))
    with pytest.raises(Exception, match="Preferred Value or a Metadata Value Table"):
        await p.apply_changes()
