# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-45: properties_class_fields.py lists the keys Jackson binds, i.e. the public setters through each
class's whole superclass chain, wherever the superclass lives (A5 finding F15)."""
import importlib.util
from pathlib import Path

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS

_GEN = Path(__file__).resolve().parents[2] / "scripts" / "gen_properties_class_fields.py"


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location("_gen_properties_class_fields", _GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _keys(cls):
    return set(PROPERTIES_CLASS_FIELDS[cls][1])


# ---------------------------------------------------------------- the generated table (Egeria 2e22b1e85b)

def test_find_property_names_properties_inherits_the_search_options_chain():
    # FindPropertyNamesProperties -> SearchOptions -> QueryOptions -> GetOptions, all in .../search/
    keys = _keys("FindPropertyNamesProperties")
    assert {"metadataElementTypeName", "asOfTime", "anchorGUID", "pageSize", "startFrom"} <= keys


def test_resource_list_properties_has_its_package_private_fields():
    assert {"resourceUse", "label", "description", "additionalProperties"} <= _keys("ResourceListProperties")


# The 11 classes odpi/egeria#9463 adds: their key sets as A0 generated them. PY-45 must not change them.
A0_6_4_KEYS = {
    'AssessmentProperties': ['additionalProperties', 'assessmentTime', 'assessor', 'assessorPropertyName', 'assessorTypeName', 'description', 'effectiveFrom', 'effectiveTo', 'expiryTime', 'extendedProperties', 'label', 'notes', 'typeName'],
    'BranchProperties': ['displayName', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'purpose', 'scope', 'typeName', 'url'],
    'DataValueProperties': ['additionalProperties', 'category', 'dataFormat', 'dataType', 'description', 'displayName', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'fingerprint', 'fingerprintAlgorithm', 'hash', 'hashAlgorithm', 'identifier', 'legal', 'length', 'qualifiedName', 'typeName', 'url', 'usage', 'versionIdentifier'],
    'DataValueSourceProperties': ['description', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'label', 'typeName'],
    'DecisionProperties': ['additionalProperties', 'authors', 'category', 'contentStatus', 'description', 'displayName', 'disposition', 'effectiveFrom', 'effectiveTo', 'expiryTime', 'extendedProperties', 'identifier', 'implications', 'importance', 'lastReviewTime', 'legal', 'nextReviewTime', 'notes', 'qualifiedName', 'scope', 'startTime', 'summary', 'typeName', 'url', 'usage', 'userDefinedContentStatus', 'versionIdentifier'],
    'EmbeddedDataValueProperties': ['description', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'label', 'position', 'typeName'],
    'LiteralDataValueProperties': ['additionalProperties', 'category', 'dataFormat', 'dataType', 'dataValue', 'dataValueList', 'dataValueMap', 'description', 'displayName', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'fingerprint', 'fingerprintAlgorithm', 'hash', 'hashAlgorithm', 'identifier', 'legal', 'length', 'qualifiedName', 'typeName', 'url', 'usage', 'versionIdentifier'],
    'OutcomeProperties': ['description', 'disposition', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'importance', 'label', 'typeName'],
    'ProcessingVariableProperties': ['description', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'label', 'position', 'typeName'],
    'ProjectTargetProperties': ['description', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'label', 'typeName'],
    'SupportedVariableTypeProperties': ['description', 'effectiveFrom', 'effectiveTo', 'extendedProperties', 'label', 'maxCardinality', 'minCardinality', 'position', 'typeName'],
}


@pytest.mark.parametrize("cls", sorted(A0_6_4_KEYS))
def test_6_4_classes_keep_a0_keys(cls):
    assert sorted(_keys(cls)) == A0_6_4_KEYS[cls]


def test_table_has_no_duplicate_keys():
    for cls, (_, keys) in PROPERTIES_CLASS_FIELDS.items():
        assert len(keys) == len(set(keys)), cls


# ---------------------------------------------------------------- the generator on synthetic Java

_ROOT = "x/src/main/java/org/odpi/openmetadata/frameworks/"


def _src(package, body, imports=()):
    return "\n".join([f"package {package};", *[f"import {i};" for i in imports], body])


def test_package_private_setters_are_not_keys_but_package_private_fields_are(gen):
    sources = {
        _ROOT + "openmetadata/properties/RelationshipProperties.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.properties",
            "public class RelationshipProperties {\n  private String typeName;\n"
            "  public void setTypeName(String t) { typeName = t; }\n}"),
        # Only package-private (and static / private) setters: Jackson (setterVisibility=PUBLIC_ONLY)
        # binds none of them, so the class reads only what it inherits.
        _ROOT + "openmetadata/properties/HiddenProperties.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.properties",
            "public class HiddenProperties extends RelationshipProperties {\n"
            "  String secret;\n  void setSecret(String s) { secret = s; }\n"
            "  private void setOther(String s) {}\n  public static void setGlobal(String s) {}\n}"),
        # Package-private fields with public setters (the ResourceListProperties shape): all keys.
        _ROOT + "openmetadata/properties/VisibleProperties.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.properties",
            "public class VisibleProperties extends RelationshipProperties {\n"
            "  String resourceUse;\n  String label;\n"
            "  public void setResourceUse(String r) { resourceUse = r; }\n"
            "  public void setLabel(String l) { label = l; }\n"
            "  public void setURL(String u) {}\n  public void setISCName(String u) {}\n}"),
    }
    table = gen.build_table(sources)
    assert table["HiddenProperties"] == ("relationship", ("typeName",))
    assert table["VisibleProperties"] == ("relationship", ("typeName", "resourceUse", "label", "url", "iscname"))


def test_superclass_outside_properties_is_resolved_by_import_not_simple_name(gen):
    sources = {
        # Two classes called GetOptions; the import picks which one FindThingProperties extends.
        _ROOT + "openmetadata/search/GetOptions.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.search",
            "public class GetOptions {\n  public void setAsOfTime(Object t) {}\n}"),
        _ROOT + "other/GetOptions.java": _src(
            "org.odpi.openmetadata.frameworks.other",
            "public class GetOptions {\n  public void setWrong(Object t) {}\n}"),
        _ROOT + "openmetadata/search/QueryOptions.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.search",
            "public class QueryOptions extends GetOptions {\n  public void setPageSize(int p) {}\n}"),
        _ROOT + "openmetadata/properties/FindThingProperties.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.properties",
            "public class FindThingProperties extends QueryOptions\n{\n"
            "  public void setMetadataElementTypeName(String n) {}\n}",
            imports=("org.odpi.openmetadata.frameworks.openmetadata.search.QueryOptions",)),
    }
    table = gen.build_table(sources)
    assert table["FindThingProperties"] == ("other", ("asOfTime", "pageSize", "metadataElementTypeName"))
    # QueryOptions isn't a *Properties class, so it is read for the chain but not listed.
    assert "QueryOptions" not in table


def test_json_property_rename_and_nested_classes(gen):
    sources = {
        _ROOT + "openmetadata/properties/EntityProperties.java": _src(
            "org.odpi.openmetadata.frameworks.openmetadata.properties",
            "public abstract class EntityProperties {\n"
            "  @JsonProperty(\"enum\")\n  public void setEnumValues(Object e) {}\n"
            "  public static class Inner {\n    public void setInnerOnly(String s) {}\n  }\n"
            "  public void setAfterInner(String s) {}\n}"),
    }
    assert gen.build_table(sources)["EntityProperties"] == ("entity", ("enum", "afterInner"))
