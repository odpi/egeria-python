# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49: the report-spec generator emits only columns a find report can fill.

The generated "-DrE-" specs used to take every Create-command attribute as a column. Most of those can never be filled:
request-only parameters (effective_time, is_own_anchor, anchor_*, template_*, instance_*, parent_guid ...), classification
payloads, a `user_defined_status` no element bean has, and Reference Name attributes that name no column the formatter
fills. The rule (commands/tech/gen_report_specs.py):

- stored attributes: kept;
- Reference Name / Reference Name List attributes: the relationship-list column, if RELATIONSHIP_FIELDS has the list
  (ATTRIBUTE_RELATIONSHIP_LISTS), the key a client derives (CLIENT_DERIVED_KEYS), else none;
- request-only parameters: never emitted;
- classification payloads: not emitted (PY-53 later);
- user_defined_status: user_defined_content_status where the target type has it, else none.
"""
import json

import pytest

from commands.tech import gen_report_specs as g
from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS

pytestmark = pytest.mark.unit


def _attr(variable_name, style="Simple", level="Basic", **extra):
    return {"variable_name": variable_name, "level": level, "style": style, **extra}


def _payload(attrs, display_name="Widget", om_type="Project"):
    defs = {label: d for label, d in attrs.items()}
    return {
        "attribute_definitions": defs,
        "bundles": {"B": {"inherits": None, "own_attributes": list(defs)}},
        "commands": {f"Create {display_name}": {
            "display_name": display_name, "family": "Testing", "verb": "Create", "OM_TYPE": om_type,
            "find_method": "ProjectManager.find_projects", "find_constraints": "", "bundle": "B",
            "custom_attributes": []}},
    }


def _keys(tmp_path, attrs, display_name="Widget", om_type="Project", level="Advanced"):
    path = tmp_path / "commands_t.json"
    path.write_text(json.dumps(_payload(attrs, display_name, om_type)), encoding="utf-8")
    fs = g.build_format_sets_from_commands(path)[f"{display_name}-DrE-{level}"]
    return {c.key for f in fs.formats for c in f.attributes}


BASE = {"Display Name": _attr("display_name"), "Qualified Name": _attr("qualified_name"), "Description": _attr("description")}


@pytest.mark.parametrize("key", ["effective_time", "is_own_anchor", "anchor_scope_guid", "anchor_guid", "template_guid",
                                 "template_properties", "placeholder_property_values", "instance_type_name",
                                 "instance_properties", "parent_guid", "initial_classifications"])
def test_request_only_parameters_are_never_emitted(tmp_path, key):
    keys = _keys(tmp_path, {**BASE, "X": _attr(key, level="Advanced")})
    assert key not in keys and "display_name" in keys


@pytest.mark.parametrize("key", ["confidence_classification", "confidentiality_classification", "criticality_classification",
                                 "impact_classification", "retention_classification", "security_tags",
                                 "policy_management_point", "supplementary_properties", "class_word_classification",
                                 "prime_word_classification", "modifier_classification", "is_abstract_concept",
                                 "is_activity_description", "is_data_value", "term_activity_type"])
def test_classification_payloads_are_not_emitted(tmp_path, key):
    assert key not in _keys(tmp_path, {**BASE, "X": _attr(key, "Valid Value", "Advanced")})


def test_user_defined_status_becomes_user_defined_content_status_where_the_target_has_it(tmp_path):
    keys = _keys(tmp_path, {**BASE, "UDS": _attr("user_defined_status", level="Advanced")}, "Project", "Project")
    assert "user_defined_status" not in keys and "user_defined_content_status" in keys


def test_user_defined_status_is_dropped_where_the_target_does_not_have_it(tmp_path):
    keys = _keys(tmp_path, {**BASE, "UDS": _attr("user_defined_status", level="Advanced")}, "Widget", "Nonexistent")
    assert "user_defined_status" not in keys and "user_defined_content_status" not in keys


def test_user_defined_status_does_not_duplicate_an_existing_content_status_column(tmp_path):
    attrs = {**BASE, "UDS": _attr("user_defined_status", level="Advanced"),
             "UDCS": _attr("user_defined_content_status", level="Advanced")}
    path = tmp_path / "commands_t.json"
    path.write_text(json.dumps(_payload(attrs, "Project", "Project")), encoding="utf-8")
    fs = g.build_format_sets_from_commands(path)["Project-DrE-Advanced"]
    all_keys = [c.key for f in fs.formats if f.types == ["ALL"] for c in f.attributes]
    assert all_keys.count("user_defined_content_status") == 1


def test_glossary_term_is_mapped_to_the_semantic_definitions_relationship_list(tmp_path):
    keys = _keys(tmp_path, {**BASE, "Glossary Term": _attr("glossary_term", "Reference Name", "Advanced",
                                                           existing_element="GlossaryTerm")})
    assert "glossary_term" not in keys and "semantic_definitions" in keys
    assert g.ATTRIBUTE_RELATIONSHIP_LISTS["glossary_term"] == "semanticDefinitions"


def test_a_reference_name_attribute_with_no_known_relationship_list_is_skipped(tmp_path):
    keys = _keys(tmp_path, {**BASE, "Mystery": _attr("mystery_ref", "Reference Name List", "Advanced")})
    assert "mystery_ref" not in keys


def test_every_mapped_relationship_list_exists_in_the_6_4_table():
    missing = {k: v for k, v in g.ATTRIBUTE_RELATIONSHIP_LISTS.items() if v not in RELATIONSHIP_FIELDS}
    assert not missing, missing


def test_the_two_data_value_hierarchy_aliases_become_one_column(tmp_path):
    attrs = {**BASE, "In DVS": _attr("in_data_value_specification", "Reference Name", "Advanced"),
             "Spec DVS": _attr("specializes_data_value_specification", "Reference Name", "Advanced")}
    path = tmp_path / "commands_t.json"
    path.write_text(json.dumps(_payload(attrs, "Data Class", "DataClass")), encoding="utf-8")
    fs = g.build_format_sets_from_commands(path)["Data-Class-DrE-Advanced"]
    keys = [c.key for f in fs.formats if f.types == ["ALL"] for c in f.attributes]
    assert keys.count("super_data_value_specification") == 1
    assert "in_data_value_specification" not in keys and "specializes_data_value_specification" not in keys


def test_stored_attributes_are_kept(tmp_path):
    keys = _keys(tmp_path, {**BASE, "Mission": _attr("mission", level="Advanced"), "Priority": _attr("priority", "Simple Int", "Advanced")})
    assert {"display_name", "qualified_name", "description", "mission", "priority"} <= keys


def test_a_command_whose_attributes_are_all_request_only_still_gets_the_universal_columns(tmp_path):
    attrs = {"Template GUID": _attr("template_guid", level="Advanced"), "Parent GUID": _attr("parent_guid", level="Advanced")}
    keys = _keys(tmp_path, attrs, "Widget", "Referenceable", level="Advanced")
    assert keys == {"display_name", "qualified_name", "description", "guid"}


def _technology_keys(tmp_path, command, display_name):
    payload = _payload({**BASE}, display_name, "")
    cmd = payload["commands"].pop(next(iter(payload["commands"])))
    cmd = {**cmd, "display_name": display_name, "find_method": "ClassificationExplorer.find_elements_by_property_value"}
    payload["commands"][command] = cmd
    path = tmp_path / "commands_t.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    fs = g.build_format_sets_from_commands(path)[display_name.replace(" ", "-") + "-DrE-Advanced"]
    return fs.target_type, {c.key for f in fs.formats for c in f.attributes}


def test_the_technology_column_is_added_where_the_target_type_has_the_attribute(tmp_path):
    target, keys = _technology_keys(tmp_path, "Create UC Server Element", "UC Server Element")
    assert target == "SoftwareServer" and "deployed_implementation_type" in keys


def test_the_technology_column_is_not_added_where_the_target_type_lacks_it(tmp_path):
    target, keys = _technology_keys(tmp_path, "Create UC Catalog Element", "UC Catalog Element")
    assert target == "Namespace" and "deployed_implementation_type" not in keys
