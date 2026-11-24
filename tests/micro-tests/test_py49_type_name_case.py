# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49: the validator resolves a spec's target type name without regard to case.

`egeria_type_name` removed spaces and punctuation but kept case, so names with a lower-case connector ('Terms and
Conditions', 'Statement of Applicability', 'Todo') never matched `TermsAndConditionsProperties` and so on, and the
specs naming them skipped the strict column check. An unknown name stays unknown.
"""
import pytest

from pyegeria.authoring.validate import egeria_type_name, type_attributes

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("written,egeria", [
    ("Terms and Conditions", "TermsAndConditions"),
    ("Statement of Applicability", "StatementOfApplicability"),
    ("Todo", "ToDo"),
    ("terms and conditions", "TermsAndConditions"),
    ("Data Class", "DataClass"),            # unchanged behaviour
    ("DataClass", "DataClass"),
    ("External-Reference", "ExternalReference"),
])
def test_the_name_resolves_to_the_egeria_type(written, egeria):
    assert egeria_type_name(written) == egeria
    assert type_attributes(written) is not None


@pytest.mark.parametrize("written", ["Terms and Condition", "Folder", "Not A Type", ""])
def test_an_unknown_name_stays_unknown(written):
    assert type_attributes(written) is None
    assert egeria_type_name(written) == written


def test_exact_name_wins_over_a_case_insensitive_match():
    # two catalog entries that differ only by case must not be conflated: the exact one is returned as written
    assert egeria_type_name("ToDo") == "ToDo"


def test_a_camel_case_column_key_is_checked_by_its_snake_form():
    """The formatter converts a snake_case key to camelCase and leaves a camelCase key as written, so both name the
    same attribute; the strict check must not refuse 'displayName' on a type that has display_name."""
    from pyegeria.authoring.models import SpecDraft
    from pyegeria.authoring.validate import validate
    spec = SpecDraft(label="Camel", format_set={
        "target_type": "ToDo", "heading": "Camel", "description": "d",
        "action": {"function": "ProjectManager.find_projects", "required_params": ["search_string"]},
        "formats": [{"types": ["TABLE"], "attributes": [
            {"name": "N", "key": "displayName"}, {"name": "S", "key": "activityStatus"}, {"name": "X", "key": "notAnAttribute"}]}]})
    errors = [e for e in validate(spec).errors if "isn't an attribute of" in e]
    assert any("'notAnAttribute'" in e for e in errors)
    assert not any("'displayName'" in e or "'activityStatus'" in e for e in errors)
