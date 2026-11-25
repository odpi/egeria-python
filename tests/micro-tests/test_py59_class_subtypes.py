"""PY-59: a `class:A` column matches a classification named A or any of its subtypes (Egeria 6.4)."""
import importlib.util
import os
import pathlib

import pytest

from pyegeria.view.column_source import check_source, resolve_source

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _el(*classifications):
    return {"elementHeader": {"classifications": [
        {"classificationName": name, "classificationProperties": props} for name, props in classifications]}}


def test_a_subtype_classification_fills_a_supertype_class_column():
    el = _el(("PolicyEnforcementPoint", {"pointType": "gate"}))
    assert resolve_source(el, "class:PolicyManagementPoint.pointType")[1] == "gate"
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyEnforcementPoint"


def test_the_exact_name_still_matches():
    el = _el(("PolicyManagementPoint", {"pointType": "base"}))
    assert resolve_source(el, "class:PolicyManagementPoint.pointType") == ("base", "base")
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyManagementPoint"


def test_an_unrelated_classification_does_not_fill_it():
    el = _el(("Confidence", {"confidenceLevel": 3}), ("PolicyManagementPoint", {"pointType": "x"}))
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyManagementPoint"
    assert resolve_source(_el(("Confidence", {})), "class:PolicyManagementPoint") == ("", "")


def test_a_supertype_does_not_fill_a_subtype_column():
    el = _el(("PolicyManagementPoint", {"pointType": "x"}))
    assert resolve_source(el, "class:PolicyEnforcementPoint") == ("", "")


def test_a_sibling_subtype_does_not_fill_another_subtypes_column():
    el = _el(("PolicyDecisionPoint", {}))
    assert resolve_source(el, "class:PolicyEnforcementPoint") == ("", "")


def test_a_project_kind_column_matches_its_subtypes():
    el = _el(("Campaign", {}), ("Task", {}))
    assert resolve_source(el, "class:ProjectKind")[1] == "Campaign, Task"


def test_two_names_still_list_every_match_once():
    el = _el(("PolicyEnforcementPoint", {}), ("Confidence", {}))
    assert resolve_source(el, "class:PolicyManagementPoint,Confidence")[1] == "PolicyEnforcementPoint, Confidence"


def test_the_supertype_table_names_real_classifications():
    from md_processing.md_processing_utils.properties_class_fields import (CLASSIFICATION_SUPERTYPES,
                                                                           PROPERTIES_CLASS_FIELDS)
    assert CLASSIFICATION_SUPERTYPES["PolicyEnforcementPoint"] == ("PolicyManagementPoint",)
    for sub, above in CLASSIFICATION_SUPERTYPES.items():
        assert PROPERTIES_CLASS_FIELDS[f"{sub}Properties"][0] == "classification"
        for sup in above:
            assert PROPERTIES_CLASS_FIELDS[f"{sup}Properties"][0] == "classification", (sub, sup)
    assert not any(a == "ClassificationBean" for above in CLASSIFICATION_SUPERTYPES.values() for a in above)


def test_the_validator_still_accepts_a_supertype_source():
    assert check_source("class:PolicyManagementPoint.pointType") == []


def _gen():
    spec = importlib.util.spec_from_file_location("gen_pcf", ROOT / "scripts/gen_properties_class_fields.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


ENUM = """
    PROJECT_KIND_CLASSIFICATION("11111111-1111-1111-1111-111111111111",
                                "ProjectKind",
                                OpenMetadataWikiPages.MODEL_0130_PROJECTS),
    EXPERIMENT_CLASSIFICATION("22222222-2222-2222-2222-222222222222",
                              "Experiment",
                              OpenMetadataWikiPages.MODEL_0130_PROJECTS),
    GOVERNANCE_PROJECT_CLASSIFICATION("33333333-3333-3333-3333-333333333333", "GovernanceProject", X),
    BIG_EXPERIMENT_CLASSIFICATION("44444444-4444-4444-4444-444444444444", "BigExperiment", X),
    CONFIDENCE_CLASSIFICATION("55555555-5555-5555-5555-555555555555", "Confidence", X),
"""
ARCHIVE = """
    ClassificationDef a = archiveHelper.getClassificationDef(OpenMetadataType.PROJECT_KIND_CLASSIFICATION,
                                                             null,
                                                             this.archiveBuilder.getEntityDef(OpenMetadataType.PROJECT.typeName),
                                                             false);
    ClassificationDef b = archiveHelper.getClassificationDef(OpenMetadataType.EXPERIMENT_CLASSIFICATION,
                                                             this.archiveBuilder.getClassificationDef(OpenMetadataType.PROJECT_KIND_CLASSIFICATION.typeName),
                                                             this.archiveBuilder.getEntityDef(OpenMetadataType.PROJECT.typeName),
                                                             false);
    // ClassificationDef c = archiveHelper.getClassificationDef(OpenMetadataType.CONFIDENCE_CLASSIFICATION, this.archiveBuilder.getClassificationDef(OpenMetadataType.PROJECT_KIND_CLASSIFICATION.typeName), x, false);
    ClassificationDef d = archiveHelper.getClassificationDef(OpenMetadataType.GOVERNANCE_PROJECT_CLASSIFICATION,
                                                             this.archiveBuilder.getClassificationDef(OpenMetadataType.PROJECT_KIND_CLASSIFICATION.typeName),
                                                             this.archiveBuilder.getEntityDef(OpenMetadataType.PROJECT.typeName), false);
    ClassificationDef e = archiveHelper.getClassificationDef(OpenMetadataType.BIG_EXPERIMENT_CLASSIFICATION,
                                                             this.archiveBuilder.getClassificationDef(OpenMetadataType.EXPERIMENT_CLASSIFICATION.typeName),
                                                             null, false);
    ClassificationDef f = archiveHelper.getClassificationDef(OpenMetadataType.CONFIDENCE_CLASSIFICATION, null, null, false);
"""


def test_the_generator_reads_supertypes_from_the_typedefs():
    gen = _gen()
    names = gen.type_name_constants({"x/OpenMetadataType.java": ENUM})
    assert names["EXPERIMENT_CLASSIFICATION"] == "Experiment" and names["PROJECT_KIND_CLASSIFICATION"] == "ProjectKind"
    direct = gen.classification_typedef_supers({"x/OpenMetadataTypesArchive5_0.java": ARCHIVE}, names)
    assert direct == {"Experiment": "ProjectKind", "GovernanceProject": "ProjectKind", "BigExperiment": "Experiment"}
    chains = gen.supertype_chains(direct)
    assert chains["BigExperiment"] == ("Experiment", "ProjectKind")
    assert chains["GovernanceProject"] == ("ProjectKind",)
    assert "ProjectKind" not in chains and "Confidence" not in chains


def test_the_table_has_every_project_kind_subtype_the_typedefs_give():
    from md_processing.md_processing_utils.properties_class_fields import CLASSIFICATION_SUPERTYPES as table
    subs = {c for c, above in table.items() if "ProjectKind" in above}
    assert {"Campaign", "Task", "StudyProject", "PersonalProject", "Investigation",
            "Experiment", "GlossaryProject", "GovernanceProject"} <= subs


def test_a_governance_project_fills_a_project_kind_column():
    el = _el(("GovernanceProject", {}))
    assert resolve_source(el, "class:ProjectKind")[1] == "GovernanceProject"


def test_the_table_equals_a_typedef_parse_of_the_6_4_source():
    """Needs the odpi/egeria source the table was made from: EGERIA_6_4_SRC=<checkout> EGERIA_6_4_REF=<sha>."""
    src, ref = os.environ.get("EGERIA_6_4_SRC"), os.environ.get("EGERIA_6_4_REF", "2e22b1e85b")
    if not src:
        pytest.skip("set EGERIA_6_4_SRC to a checkout of odpi/egeria at the table's sha")
    from md_processing.md_processing_utils.properties_class_fields import CLASSIFICATION_SUPERTYPES as table
    gen = _gen()
    frameworks = gen.read_sources(src, ref)
    expected = gen.supertype_chains(gen.classification_typedef_supers(
        gen.read_typedef_sources(src, ref), gen.type_name_constants(frameworks)))
    assert dict(table) == expected


def test_the_header_names_the_source_sha_in_the_same_form():
    import md_processing.md_processing_utils.properties_class_fields as pcf
    assert "from Egeria 2e22b1e85b at 2e22b1e85b " in pcf.__doc__
