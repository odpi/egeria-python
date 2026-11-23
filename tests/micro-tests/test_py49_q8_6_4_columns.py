# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49 Q8: the Egeria 6.4 attributes and relationships the specs did not show.

ProjectTarget on Projects; ProcessingVariable and SupportedVariableType (configuration values) on the process spec; the
fingerprint and hash attributes and the other end of EmbeddedDataValue on the data value specs; the user-defined content
status on Decision. Every key is a real 6.4 attribute or relationship list, which the strict validator confirms.
Branch's properties wait for PY-53.
"""
import pytest

from pyegeria.authoring.models import SpecDraft
from pyegeria.authoring.validate import validate
from pyegeria.view.base_report_formats import get_report_registry
from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS

pytestmark = pytest.mark.unit

ADDED = {
    "Projects": ["project_targets"],
    "Governance-Process": ["processing_variables", "process_variable_types"],
    "Decision": ["user_defined_content_status"],
    "Data-Value": ["fingerprint", "fingerprint_algorithm", "hash", "hash_algorithm", "parent_data_values"],
    "Literal-Data-Value": ["fingerprint", "fingerprint_algorithm", "hash", "hash_algorithm", "parent_data_values"],
}


def _keys(label):
    return {c.key for f in get_report_registry()[label].formats for c in f.attributes}


@pytest.mark.parametrize("label,key", [(l, k) for l, ks in ADDED.items() for k in ks])
def test_the_spec_shows_the_6_4_column(label, key):
    assert key in _keys(label)


@pytest.mark.parametrize("label", sorted(ADDED))
def test_the_strict_validator_accepts_every_column_of_the_spec(label):
    result = validate(SpecDraft(label=label, format_set=get_report_registry()[label]))
    assert not [e for e in result.errors if "isn't an attribute of" in e], result.errors


def test_the_relationship_columns_are_lists_egeria_attaches():
    from pyegeria.authoring.validate import _snake
    lists = {_snake(k) for k in RELATIONSHIP_FIELDS}
    for key in ("project_targets", "processing_variables", "process_variable_types", "parent_data_values"):
        assert key in lists
