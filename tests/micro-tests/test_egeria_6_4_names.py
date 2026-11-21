# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A0 for the Egeria 6.4 additions (odpi/egeria#9463): the names module agrees with the generated tables and
with the PR's `.http` sample collections, and every one names the same Egeria source sha."""
import re
from pathlib import Path

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from pyegeria.core import egeria_6_4_names as n
from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "egeria-6.4"
HTTP_FILES = ("Egeria-api-governance-officer.http", "Egeria-api-data-engineer.http",
              "Egeria-api-project-manager.http", "Egeria-api-devops-pipeline.http", "Egeria-api-schema-maker.http")
# A path segment that only the 6.4 requests use; it picks the 6.4 requests out of the full collections.
_6_4_SEGMENTS = {"decisions", "outcomes", "assessments", "data-values", "data-value-sources",
                 "processing-variables", "embedded-data-values", "project-targets", "branch",
                 "supported-variable-types"}
_POST = re.compile(r"^POST\s+\{\{baseURL\}\}/servers/\{\{viewServer\}\}/api/open-metadata/(\S+?)(?:\?\S*)?\s*$", re.M)


def _http_paths() -> set[str]:
    paths = set()
    for name in HTTP_FILES:
        for path in _POST.findall((FIXTURES / name).read_text(encoding="utf-8")):
            path = re.sub(r"\{\{(\w+)\}\}", r"{\1}", path)
            if _6_4_SEGMENTS & set(path.split("/")):
                paths.add(path)
    return paths


def test_counts_match_the_spec():
    assert len(n.TYPE_NAMES) == len(set(n.TYPE_NAMES)) == 11
    assert len(n.ROOT_ELEMENT_LISTS) == 14
    assert len(n.PROPERTIES_CLASSES) == 11
    assert len(n.URL_PATHS) == len(set(n.URL_PATHS)) == 31
    assert set(n.ROOT_ELEMENT_LISTS.values()) <= set(n.TYPE_NAMES)


@pytest.mark.parametrize("list_name", sorted(n.ROOT_ELEMENT_LISTS))
def test_root_element_list_is_generated_with_its_relationship_type(list_name):
    assert list_name in RELATIONSHIP_FIELDS, f"{list_name} is missing: regenerate egeria_relationship_fields.py"
    assert RELATIONSHIP_FIELDS[list_name] == (n.ROOT_ELEMENT_LISTS[list_name],)


@pytest.mark.parametrize("cls", sorted(n.PROPERTIES_CLASSES))
def test_properties_class_is_generated_with_the_spec_keys(cls):
    assert cls in PROPERTIES_CLASS_FIELDS, f"{cls} is missing: regenerate properties_class_fields.py"
    kind, keys = n.PROPERTIES_CLASSES[cls]
    gen_kind, gen_keys = PROPERTIES_CLASS_FIELDS[cls]
    assert gen_kind == kind
    assert set(keys) <= set(gen_keys), f"{cls} lacks {sorted(set(keys) - set(gen_keys))}"


def test_assessment_properties_example_from_the_plan():
    kind, keys = PROPERTIES_CLASS_FIELDS["AssessmentProperties"]
    assert kind == "relationship" and {"assessmentTime", "assessorTypeName"} <= set(keys)


def test_branch_properties_has_no_label_or_description():
    _, keys = PROPERTIES_CLASS_FIELDS["BranchProperties"]
    assert not {"label", "description"} & set(keys)


def test_names_module_and_http_paths_agree():
    http = _http_paths()
    names = set(n.URL_PATHS)
    assert not names - http, f"in egeria_6_4_names but not in the .http collections: {sorted(names - http)}"
    assert not http - names, f"in the .http collections but not in egeria_6_4_names: {sorted(http - names)}"


def test_fixtures_and_generated_tables_name_the_same_source_sha():
    sha = n.EGERIA_6_4_SOURCE_SHA
    assert f"head: {sha}" in (FIXTURES / "SOURCE").read_text(encoding="utf-8")
    import md_processing.md_processing_utils.properties_class_fields as pcf
    import pyegeria.view.egeria_relationship_fields as erf
    assert sha in pcf.__doc__, "properties_class_fields.py was not generated from the fixtures' sha"
    assert sha[:10] in erf.__doc__, "egeria_relationship_fields.py was not generated from the fixtures' sha"
