# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49 Q6: the generated specs target a real Egeria type.

A generated spec took its target_type from the Create command's display name, which is a name for people ("Postgres
Database Element", "Campaign") and often no Egeria type. Now:

- a classification (Campaign, Task, ...): the entity it classifies (Project, Collection, GlossaryTerm), the classification
  staying the find filter;
- a friendly name: the command's own OM_TYPE, when that is an Egeria entity;
- the Unity Catalog elements: the entity each is made as; Element and Instance: the generic root, Referenceable;
- the Schema ... From Template commands: the SchemaAttribute and SchemaType supertypes;
- Enum Def and Type Def: OpenMetadataTypeDef.

The Subscription Type command no longer exists.
"""
import pytest

from pyegeria.authoring.validate import type_attributes
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit

EXPECTED = {
    "Campaign": "Project", "Experiment": "Project", "Glossary-Project": "Project", "Governance-Project": "Project",
    "Personal-Project": "Project", "Study-Project": "Project", "Task": "Project",
    "Data-Sharing-Agreement": "Collection", "Question": "GlossaryTerm",
    "CSV-Data-File-Element": "CSVFile", "Folder-Element": "DataFolder", "Kafka-Server-Element": "SoftwareServer",
    "Postgres-Server-Element": "SoftwareServer", "Postgres-Database-Element": "RelationalDatabase",
    "Secrets-Store-Element": "SecretsCollection", "Question-Spec": "CollectionFolder",
    "Penetration-Test-Finding": "PenetrationTestFindingAnnotation", "Security-Finding": "SecurityFindingAnnotation",
    "Security-Posture-Summary": "SecurityPostureAnnotation", "Vulnerability-Finding": "VulnerabilityAnnotation",
    "Solution-Role": "SolutionActorRole",
    "UC-Server-Element": "SoftwareServer", "UC-Schema-Element": "DeployedDatabaseSchema",
    "UC-Table-Element": "VirtualRelationalTable", "UC-Function-Element": "DeployedAPI", "UC-Volume-Element": "DataFolder",
    "Element": "Referenceable", "Instance": "Referenceable",
    "Schema-Attribute-From-Template": "SchemaAttribute", "Schema-Type-From-Template": "SchemaType",
    "Enum-Def": "OpenMetadataTypeDef", "Type-Def": "OpenMetadataTypeDef",
}


@pytest.mark.parametrize("name,target", sorted(EXPECTED.items()))
@pytest.mark.parametrize("level", ["Basic", "Advanced"])
def test_the_generated_spec_targets_the_expected_type(name, target, level):
    assert get_report_registry()[f"{name}-DrE-{level}"].target_type == target


def test_every_target_that_is_an_entity_is_in_the_6_4_table():
    for name, target in EXPECTED.items():
        if target != "OpenMetadataTypeDef":
            assert type_attributes(target) is not None, (name, target)


def test_the_classification_specs_still_filter_on_their_classification():
    fs = get_report_registry()["Campaign-DrE-Basic"]
    assert fs.action.spec_params == {"include_only_classified_elements": ["Campaign"]}
    assert get_report_registry()["Data-Sharing-Agreement-DrE-Basic"].action.spec_params["classification_names"] == [
        "DataSharingAgreement"]


def test_the_subscription_type_spec_and_command_are_gone():
    registry = get_report_registry()
    assert not [k for k in registry if k.startswith("Subscription-Type-DrE")]
    from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir
    from pathlib import Path
    import md_processing
    specs = load_compact_specs_from_dir(str(Path(md_processing.__file__).parent / "data" / "compact_commands"))
    assert "Create Subscription Type" not in specs


def test_no_generated_spec_names_a_target_that_is_neither_an_entity_nor_a_known_exception():
    exceptions = {"Dashboard Sheet", "UC Catalog Element", "OpenMetadataTypeDef", "Journal Entry"}
    bad = []
    for label, fs in get_report_registry().items():
        if "-DrE-" in label and fs.target_type and type_attributes(fs.target_type) is None and fs.target_type not in exceptions:
            bad.append((label, fs.target_type))
    assert not bad, bad
