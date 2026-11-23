# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49: the hand-written report specs after Dan's decisions on the audit (Q1 to Q5, groups B, C and D).

Each case names the column a spec shows and why. No Egeria: the specs are read from the registry.
"""
import pytest

from pyegeria.authoring.validate import type_attributes
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit


def _keys(label):
    fs = get_report_registry()[label]
    return [c.key for f in fs.formats for c in f.attributes]


def _keyset(label):
    return set(_keys(label))


PUBLICATION = ["number_of_pages", "page_range", "publication_series", "pub_series_volume", "publisher", "first_pub_date",
               "pub_date", "pub_city", "pub_year", "pub_numbers"]


# --- Q1 and Q2 (groups B and C)

@pytest.mark.parametrize("label", ["ExternalReference", "CitedDocument", "RelatedMedia"])
def test_reference_url_is_dropped_where_a_url_column_already_exists(label):
    keys = _keys(label)
    assert "reference_url" not in keys and keys.count("url") == 1


def test_external_references_renames_reference_url_reference_sources_and_current_version():
    keys = _keys("External-References")
    for gone in ("reference_url", "reference_sources", "current_version"):
        assert gone not in keys
    assert {"url", "sources", "version_identifier"} <= set(keys)


def test_the_publication_fields_leave_external_references():
    assert not set(PUBLICATION) & _keyset("External-References")


def test_the_cited_document_spec_keeps_every_publication_field_under_its_real_name():
    keys = _keyset("CitedDocument")
    assert {"number_of_pages", "page_range", "publication_series", "publication_series_volume", "publisher",
            "first_publication_date", "publication_date", "publication_city", "publication_year",
            "publication_numbers"} <= keys


# --- Q4

def test_projects_shows_the_real_start_dates_and_not_the_dead_columns():
    keys = _keyset("Projects")
    assert "start_date" not in keys and "project_roles" not in keys
    assert {"planned_start_date", "actual_start_date"} <= keys


@pytest.mark.parametrize("label", ["Digital-Products", "Digital-Products-MyE", "Digital-Products-Slim"])
def test_digital_products_next_version_is_next_version_date(label):
    keys = _keyset(label)
    assert "next_version" not in keys and "next_version_date" in keys


@pytest.mark.parametrize("label", ["My-User", "My-User-MD"])
def test_my_user_has_no_job_status(label):
    assert "job_status" not in _keyset(label)


def test_my_user_projects_detail_has_no_project_type():
    assert "projectType" not in _keyset("My-User-Projects-Detail")


# --- Q5: the target type is what the find returns

@pytest.mark.parametrize("label,target", [
    ("Actor-Roles", "ActorRole"), ("Glossary-Terms", "GlossaryTerm"), ("Help-Terms", "GlossaryTerm"),
    ("ExternalIdentifier", "ExternalId"), ("Folders", "CollectionFolder"), ("Data-Specifications", "DataSpec"),
    ("Governance-Process", "GovernanceActionProcess"),
    ("Secrets-Collection-User-Profile-Charts", "GovernanceZone"),
])
def test_the_target_type_is_the_type_the_find_returns(label, target):
    fs = get_report_registry()[label]
    assert fs.target_type == target
    assert type_attributes(target) is not None


# --- Group D

def test_governance_controls_no_longer_shows_the_metric_fields_and_has_the_real_status_name():
    keys = _keyset("Governance-Controls")
    assert not {"measurement", "target", "user_defined_status"} & keys
    assert "user_defined_content_status" in keys


def test_the_metric_spec_shows_measurement_and_target():
    assert {"measurement", "target"} <= _keyset("Governance-Metric-DrE-Basic")
    assert {"measurement", "target", "user_defined_content_status"} <= _keyset("Governance-Metric-DrE-Advanced")


def test_glossary_terms_shows_examples_not_example():
    keys = _keyset("Glossary-Terms")
    assert "example" not in keys and "examples" in keys
