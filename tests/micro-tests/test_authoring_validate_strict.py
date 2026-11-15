# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-15 (BRIEF-AUTHORING-PHASE2 step 2): authoring validate is strict.

1. The find method must fit the target type: refused when it returns another type (prototype C06: target
   Asset + find_projects passed). An unknown fit is a warning, never a pass.
2. A column key must be an attribute of the target type or its super types (or a key the formatter derives).
   The old loose check (any key some pyegeria spec uses) survives only with legacy=True, with a warning.
"""
import pytest

from pyegeria.authoring import SpecDraft, validate
from pyegeria.authoring.validate import DERIVED_KEYS, FIND_ELEMENT_TYPES, _registry_columns_and_types, type_attributes
from pyegeria.view._output_format_models import FormatSet

pytestmark = pytest.mark.unit


def _spec(**over) -> SpecDraft:
    fs = {"target_type": "Project", "heading": "Projects", "description": "d",
          "formats": [{"types": ["TABLE"], "attributes": [{"name": "Name", "key": "display_name"}]}],
          "action": {"function": "ProjectManager.find_projects", "required_params": ["search_string"]}}
    fs.update(over)
    return SpecDraft(label="Draft Projects", format_set=FormatSet.model_validate(fs))


class _Valid:
    """valid_metadata with type definitions {name: super type name}; a name left out can't be read."""

    def __init__(self, supers):
        self.supers = supers

    async def _async_get_typedef_by_name(self, name):
        if name not in self.supers:
            return {}
        parent = self.supers[name]
        return {"guid": f"guid-{name}", "name": name, "superType": {"name": parent} if parent else None}


class _Client:
    def __init__(self, supers):
        self.valid_metadata = _Valid(supers)


ASSET_TYPES = {"Asset": "Referenceable", "Referenceable": "OpenMetadataRoot", "OpenMetadataRoot": None,
               "DataSet": "Asset"}


# ── 1. the find method must fit the target type ──

def test_c06_asset_target_with_find_projects_is_refused():
    result = validate(_spec(target_type="Asset"), _Client(ASSET_TYPES))
    assert not result.ok
    assert any("ProjectManager.find_projects returns Project elements" in e and "target type is Asset" in e
               for e in result.errors), result.errors


def test_the_same_mismatch_with_no_client_is_a_warning_and_not_a_pass():
    result = validate(_spec(target_type="Asset"))
    assert not any("find_projects returns" in e for e in result.errors)
    assert any("Can't tell whether find method ProjectManager.find_projects" in w for w in result.warnings)
    assert any("element type" in n or "super types not read" in n for n in result.not_checked)
    assert "find method fits the target type" not in result.checked


def test_the_find_methods_own_type_and_registered_pairs_fit_with_no_client():
    assert "find method fits the target type" in validate(_spec(target_type="Project")).checked
    assert "find method fits the target type" in validate(_spec(target_type="Campaign")).checked   # a shipped pair


def test_a_subtype_fits_through_its_super_types():
    spec = _spec(target_type="DataSet", action={"function": "AssetMaker.find_assets",
                                                "required_params": ["search_string"]})
    result = validate(spec, _Client(ASSET_TYPES))
    assert not any("find_assets returns" in e for e in result.errors), result.errors
    assert "find method fits the target type" in result.checked


def test_an_unreadable_target_type_is_a_warning_not_a_refusal():
    result = validate(_spec(target_type="Asset"), _Client({}))
    assert not any("find_projects returns" in e for e in result.errors)
    assert any("super types couldn't be read" in w for w in result.warnings)


def test_a_find_method_with_no_recorded_type_is_a_warning():
    result = validate(_spec(action={"function": "ProjectManager.find_something_new", "required_params": []}))
    assert any("pyegeria has no record of its element type" in w for w in result.warnings)


def test_a_generic_find_fits_any_target():
    assert None in FIND_ELEMENT_TYPES.values()
    spec = _spec(target_type="Asset", action={"function": "ClassificationExplorer.get_elements",
                                              "required_params": []})
    assert "find method fits the target type" in validate(spec).checked


# ── 2. strict column keys ──

def test_a_valid_key_passes_and_an_unknown_key_is_refused_naming_it():
    assert validate(_spec()).ok
    result = validate(_spec(formats=[{"types": ["TABLE"], "attributes": [{"name": "Colour", "key": "favourite_colour"}]}]))
    assert any("'favourite_colour'" in e and "isn't an attribute of Project" in e for e in result.errors)


def test_a_super_type_attribute_is_accepted():
    assert "qualified_name" in type_attributes("Project")          # a Referenceable attribute, inherited
    result = validate(_spec(formats=[{"types": ["TABLE"], "attributes": [
        {"name": "QN", "key": "qualified_name"}, {"name": "Mission", "key": "mission"}]}]))
    assert result.ok, result.errors


def test_a_key_only_a_generated_spec_uses_is_refused_strictly_and_warned_when_legacy():
    key = "anchor_scope_guid"           # a Create command's attribute, in the generated -DrE- specs only
    used, _ = _registry_columns_and_types()
    assert key in used and key not in type_attributes("Project") | DERIVED_KEYS
    spec = _spec(formats=[{"types": ["TABLE"], "attributes": [{"name": "Odd", "key": key}]}])
    strict = validate(spec)
    assert any(f"'{key}'" in e for e in strict.errors)
    legacy = validate(spec, legacy=True)
    assert not any(f"'{key}'" in e for e in legacy.errors)
    assert any(f"'{key}'" in w and "legacy spec" in w for w in legacy.warnings)
    assert "column attributes (legacy: loose)" in legacy.checked


# ── R2: every recorded element type is a real Egeria type ──

def test_every_find_element_type_is_in_the_catalog():
    missing = sorted({t for t in FIND_ELEMENT_TYPES.values() if t is not None and type_attributes(t) is None})
    assert not missing, f"FIND_ELEMENT_TYPES names types the Properties catalog doesn't have: {missing}"


# ── R3: strict validation must not refuse a shipped find spec ──

def _shipped_find_specs():
    from pyegeria.view.base_report_formats import get_report_registry
    for label, fs in sorted(get_report_registry().items()):
        action = getattr(fs, "action", None)
        if action and getattr(action, "function", None) and not getattr(action, "analytic_function", None):
            yield label, fs


def test_strict_validation_refuses_no_shipped_find_spec_column():
    refused = {}
    checked = 0
    for label, fs in _shipped_find_specs():
        result = validate(SpecDraft(label=label, format_set=fs))
        bad = [e for e in result.errors if "isn't an attribute of" in e]
        checked += "column attributes" in result.checked
        if bad:
            refused[label] = bad
    assert checked > 50, "the shipped find specs weren't checked"
    assert not refused, f"strict column check refuses shipped specs: {refused}"


def test_no_shipped_find_spec_is_refused_for_its_find_method_fit():
    refused = {}
    for label, fs in _shipped_find_specs():
        errors = [e for e in validate(SpecDraft(label=label, format_set=fs)).errors if " returns " in e and "elements, but" in e]
        if errors:
            refused[label] = errors
    assert not refused, f"fit check refuses shipped specs: {refused}"


def test_the_allow_lists_name_only_keys_a_shipped_spec_uses():
    from pyegeria.authoring.validate import ANNOTATION_KEYS, RELATED_ELEMENT_KEYS
    used, _ = _registry_columns_and_types()
    unused = sorted((RELATED_ELEMENT_KEYS | ANNOTATION_KEYS) - used)
    assert not unused, f"allow-listed but no shipped spec uses them (remove): {unused}"


def _own_command_only_key(command="Create Project", target="Project"):
    """A key of the TARGET's own Dr.Egeria command that strict validation doesn't otherwise accept (not a
    type attribute, not formatter-derived, not on the documented lists), derived from the compact loader at test
    time so no rename of one attribute breaks the test."""
    from pathlib import Path
    import md_processing
    from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir
    from pyegeria.authoring.validate import (ANNOTATION_KEYS, RELATED_ELEMENT_KEYS, _derived_by_rule,
                                             _formatter_derived_keys)
    specs = load_compact_specs_from_dir(str(Path(md_processing.__file__).parent / "data" / "compact_commands"))
    keys = set()
    for entry in specs[command].get("Attributes") or []:
        for details in ([entry] if entry.get("variable_name") else entry.values()):
            if isinstance(details, dict) and details.get("variable_name"):
                keys.add(details["variable_name"])
    known = type_attributes(target) | _formatter_derived_keys() | RELATED_ELEMENT_KEYS | ANNOTATION_KEYS
    candidates = sorted(k for k in keys if k not in known and not _derived_by_rule(k))
    assert candidates, f"{command} has no command-only attribute key to test with"
    return candidates[0]


def test_a_generated_dre_spec_may_use_command_attribute_keys_but_a_hand_spec_may_not():
    key = _own_command_only_key()
    odd = {"types": ["TABLE"], "attributes": [{"name": "Odd", "key": key}]}
    hand = validate(_spec(formats=[odd]))
    assert any(f"'{key}'" in e for e in hand.errors)
    generated = validate(_spec(formats=[odd], description="Auto-generated format for Project (Create, Advanced)."))
    assert not any(f"'{key}'" in e for e in generated.errors)


def test_a_hand_written_project_spec_may_show_scope():
    """ProjectProperties.scope is real in Egeria since #9448 (c61bad65): strict must not refuse it, so the
    Properties catalog (properties_class_fields) is regenerated from an Egeria that has it."""
    assert "scope" in type_attributes("Project")
    result = validate(_spec(formats=[{"types": ["TABLE"], "attributes": [{"name": "Scope", "key": "scope"}]}]))
    assert not any("'scope'" in e for e in result.errors), result.errors
    assert result.ok, result.errors
