"""PY-46: strict validation silently skipped the column check for a spec whose target_type is written the way
people write it ('License Type') instead of as Egeria's type name ('LicenseType'): the catalog lookup missed, the
check was recorded as 'no attribute catalog', and a spec with three columns License Type doesn't have passed.
The target type is now normalised to Egeria's name, so those columns are checked."""
import pytest

from pyegeria.authoring import SpecDraft, validate
from pyegeria.authoring.validate import egeria_type_name, type_attributes
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("written,egeria", [
    ("License Type", "LicenseType"), ("LicenseType", "LicenseType"), ("Actor Profile", "ActorProfile"),
    ("External-Reference", "ExternalReference"), ("Project", "Project"),
])
def test_a_target_type_written_for_people_resolves_to_egerias_type_name(written, egeria):
    assert egeria_type_name(written) == egeria
    assert type_attributes(written) == type_attributes(egeria) and type_attributes(written)


def test_an_unknown_type_stays_unknown_it_is_not_guessed_into_a_known_one():
    assert egeria_type_name("Not A Type") == "Not A Type"
    assert type_attributes("Not A Type") is None


def _spec(target_type, key):
    from pyegeria.view._output_format_models import FormatSet
    fs = {"target_type": target_type, "heading": "h", "description": "d",
          "formats": [{"types": ["TABLE"], "attributes": [{"name": "Name", "key": "display_name"},
                                                         {"name": "Bad", "key": key}]}],
          "action": {"function": "GovernanceOfficer.find_governance_definitions", "required_params": ["search_string"],
                     "spec_params": {"metadata_element_subtypes": ["LicenseType"]}}}
    return SpecDraft(label="Draft", format_set=FormatSet.model_validate(fs))


def test_a_spaced_target_type_has_its_columns_checked_not_skipped():
    result = validate(_spec("License Type", "measurement"))
    assert any("'measurement'" in e and "isn't an attribute of License Type" in e for e in result.errors), result.errors
    assert not any("no attribute catalog" in n for n in result.not_checked)


def test_the_same_column_is_refused_when_the_type_is_written_as_egeria_names_it():
    spaced = validate(_spec("License Type", "measurement"))
    exact = validate(_spec("LicenseType", "measurement"))
    assert bool(spaced.errors) == bool(exact.errors) is True


def test_a_real_license_type_attribute_passes_the_column_check():
    assert not any("isn't an attribute" in e for e in validate(_spec("License Type", "entitlements")).errors)


def test_the_license_type_spec_columns_are_all_real_attributes_now():
    registry = get_report_registry()
    for label in ("License-Type", "License-Type-DrE-Advanced", "License-Type-DrE-Basic"):
        result = validate(SpecDraft(label=label, format_set=registry[label]))
        assert "column attributes" in result.checked, label
        assert not [e for e in result.errors if "isn't an attribute" in e], (label, result.errors)
        assert not any("no attribute catalog" in n for n in result.not_checked), label
