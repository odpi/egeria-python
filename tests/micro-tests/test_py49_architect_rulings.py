# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49: the Architect's rulings on the build questions (from the 6.4 Java and read-only SELECTs on laz).

- parent_glossary on Glossary-Terms is the glossary (or glossary subtype) the term is a member of: the term's own
  memberOfCollections entries whose related element is a Glossary, names joined. 6.4 has no TermAnchor; a term's
  anchorScopeGUIDs is a list and only a quarter of terms carry one, while CollectionMembership (Glossary at end 1) links
  most. Nothing found is blank, never "None", and there is no fallback to the scope GUID. The extractor stays synchronous.
- Secrets-Collection-User-Profile-Charts finds SecretsCollection assets (the find was the bug) and shows the two Mermaid
  keys Egeria sends, plus mermaidGraph; the four Bar/Pie keys nothing produces are gone.
"""
import pytest

from pyegeria.authoring.models import SpecDraft
from pyegeria.authoring.validate import validate
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit


def _member(type_name, name, qn=None):
    return {"relatedElement": {"elementHeader": {"guid": f"g-{name}", "type": {"typeName": type_name}},
                               "properties": {"displayName": name, "qualifiedName": qn or f"{type_name}::{name}"}}}


def _term_value(memberships):
    gm = GlossaryManager.__new__(GlossaryManager)
    element = {"elementHeader": {"guid": "t1", "type": {"typeName": "GlossaryTerm"}, "origin": {}, "versions": {}},
               "properties": {"displayName": "Term", "qualifiedName": "Term::x"}}
    if memberships is not None:
        element["memberOfCollections"] = memberships
    cols = {"formats": {"types": ["ALL"], "attributes": [
        {"name": "Glossary", "key": "parent_glossary", "value": None},
        {"name": "Display Name", "key": "display_name", "value": None}]}}
    out = gm._extract_term_properties(element, cols)
    return {c["key"]: c["value"] for c in out["formats"]["attributes"]}["parent_glossary"]


def test_parent_glossary_is_the_glossary_the_term_is_a_member_of():
    assert _term_value([_member("Glossary", "Coco Glossary")]) == "Coco Glossary"


def test_only_glossaries_and_their_subtypes_count_and_names_are_joined():
    memberships = [_member("Glossary", "Coco Glossary"), _member("SubjectArea", "Finance"),
                   _member("EditingGlossary", "Draft Glossary"), _member("Glossary", "Coco Glossary")]
    assert _term_value(memberships) == "Coco Glossary, Draft Glossary"


@pytest.mark.parametrize("memberships", [None, [], [_member("SubjectArea", "Finance")]])
def test_no_glossary_membership_is_blank_not_none(memberships):
    value = _term_value(memberships)
    assert value in ("", None) and str(value or "") == ""


def test_the_scope_guid_is_not_a_fallback():
    gm = GlossaryManager.__new__(GlossaryManager)
    element = {"elementHeader": {"guid": "t1", "type": {"typeName": "GlossaryTerm"}, "origin": {}, "versions": {},
                                 "otherClassifications": [{"classificationName": "Anchors",
                                                           "classificationProperties": {"anchorScopeGUID": "SCOPE-1"}}]},
               "properties": {"displayName": "Term", "qualifiedName": "Term::x"}}
    cols = {"formats": {"attributes": [{"name": "Glossary", "key": "parent_glossary", "value": None}]}}
    out = gm._extract_term_properties(element, cols)
    assert "SCOPE-1" not in str(out)


def test_the_validator_accepts_parent_glossary_as_client_derived():
    result = validate(SpecDraft(label="Glossary-Terms", format_set=get_report_registry()["Glossary-Terms"]))
    assert not [e for e in result.errors if "isn't an attribute of" in e]


def test_secrets_collection_spec_finds_secrets_collections_and_shows_the_mermaid_keys_egeria_sends():
    fs = get_report_registry()["Secrets-Collection-User-Profile-Charts"]
    assert fs.target_type == "SecretsCollection"
    assert fs.action.function == "AssetMaker.find_assets"
    assert fs.action.spec_params == {"metadata_element_type": "SecretsCollection"}
    keys = {c.key for f in fs.formats for c in f.attributes}
    assert keys == {"mermaidGraph", "userAccountTypeProfileMermaidPieChart", "userAccountStatusProfileMermaidPieChart"}


# --- the live check on a 6.4 platform (laz, read-only)

@pytest.mark.parametrize("level", ["Basic", "Advanced"])
def test_a_unity_catalog_catalog_is_found_by_its_qualified_name_prefix(level):
    """A UC catalog is a Namespace with no deployedImplementationType (live), so the technology filter matched nothing."""
    fs = get_report_registry()[f"UC-Catalog-Element-DrE-{level}"]
    assert fs.target_type == "Namespace"
    assert fs.action.spec_params == {"search_string": "Unity Catalog Catalog::", "metadata_element_type": "Namespace",
                                     "property_names": ["qualifiedName"]}
    assert "deployed_implementation_type" not in fs.action.optional_params
    assert "deployed_implementation_type" not in {c.key for f in fs.formats for c in f.attributes}


def test_the_other_technology_specs_keep_the_technology_filter():
    fs = get_report_registry()["UC-Server-Element-DrE-Basic"]
    assert fs.action.spec_params["default_deployed_implementation_type"]


def test_the_soa_controls_spec_drops_notes_and_shows_description():
    keys = {c.key for f in get_report_registry()["Statement-of-Applicability-Controls"].formats for c in f.attributes}
    assert "notes" not in keys and {"description", "is_applicable", "label", "implementation_status", "justification",
                                    "inclusion_reasons", "review_date", "implementation_description"} <= keys
