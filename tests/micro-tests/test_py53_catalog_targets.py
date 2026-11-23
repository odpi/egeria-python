"""PY-53 Q2: a catalog-target row is the TARGET; the CatalogTarget properties come from the entry of
refreshedByConnectors for the connector that was asked about (never the first)."""
import copy

from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.view.base_report_formats import get_report_registry

CONNECTOR = "conn-2"

# trimmed from the 6.4 get_catalog_targets response (laz, 2026-11-23); no credentials
ROW = {
    "elementHeader": {"guid": "tgt-1", "type": {"typeName": "SoftwareServer"}, "origin": {}, "versions": {}},
    "properties": {"displayName": "UC Server", "qualifiedName": "UC::1", "description": "the target"},
    "refreshedByConnectors": [
        {"relationshipHeader": {"type": {"typeName": "CatalogTarget"}},
         "relationshipProperties": {"catalogTargetName": "OTHER", "metadataCollectionQualifiedName": "other-mc",
                                    "permittedSynchronization": "FROM_THIRD_PARTY"},
         "relatedElement": {"elementHeader": {"guid": "conn-1"}, "properties": {"displayName": "Other"}}},
        {"relationshipHeader": {"type": {"typeName": "CatalogTarget"}},
         "relationshipProperties": {"catalogTargetName": "MINE", "metadataCollectionQualifiedName": "mine-mc",
                                    "permittedSynchronization": "TO_THIRD_PARTY",
                                    "configurationProperties": {"a": "b"}},
         "relatedElement": {"elementHeader": {"guid": CONNECTOR}, "properties": {"displayName": "Mine"}}},
        {"relationshipHeader": {"type": {"typeName": "CatalogTarget"}},
         "relationshipProperties": {"catalogTargetName": "THIRD"},
         "relatedElement": {"elementHeader": {"guid": "conn-3"}, "properties": {"displayName": "Third"}}},
    ],
}


def _keys():
    return [c.key for f in get_report_registry()["Catalog-Target"].formats for c in f.attributes]


def _extract(element, connector=CONNECTOR):
    cols = {"formats": {"attributes": [{"name": k, "key": k} for k in _keys()]}}
    out = AutomatedCuration._extract_catalog_target_properties(
        AutomatedCuration.__new__(AutomatedCuration), copy.deepcopy(element), cols, integ_connector_guid=connector)
    return {c["key"]: c.get("value") for c in out["formats"]["attributes"]}


def test_the_spec_runs_get_catalog_targets_and_has_the_relationship_columns():
    fs = get_report_registry()["Catalog-Target"]
    assert fs.action.function == "AutomatedCuration.get_catalog_targets"
    assert fs.action.required_params == ["integ_connector_guid"]
    assert {"metadata_source_qualified_name", "connection_name", "delete_method", "catalog_target_name",
            "metadata_collection_qualified_name", "permitted_synchronization", "templates"} <= set(_keys())


def test_the_entry_for_the_asked_connector_is_used_not_the_first():
    got = _extract(ROW)  # the right connector is SECOND in the list
    assert got["catalog_target_name"] == "MINE"
    assert got["metadata_collection_qualified_name"] == "mine-mc"
    assert got["permitted_synchronization"] == "TO_THIRD_PARTY"
    assert got["configuration_properties"] == {"a": "b"}


def test_the_target_name_and_type_come_from_the_row_not_the_connector():
    got = _extract(ROW)
    assert got["target_display_name"] == "UC Server" and got["target_qualified_name"] == "UC::1"
    assert got["target_description"] == "the target" and got["target_type_name"] == "SoftwareServer"


def test_absent_relationship_properties_are_blank():
    got = _extract(ROW)
    assert got["metadata_source_qualified_name"] == "" and got["connection_name"] == "" and got["delete_method"] == ""


def test_no_matching_entry_gives_blank_columns_and_still_shows_the_row():
    got = _extract(ROW, connector="conn-unknown")
    assert got["catalog_target_name"] == "" and got["permitted_synchronization"] == ""
    assert got["target_display_name"] == "UC Server"


def test_no_connector_guid_never_falls_back_to_the_first_entry():
    assert _extract(ROW, connector=None)["catalog_target_name"] == ""


def test_the_getter_hands_the_connector_guid_to_the_output():
    import asyncio
    from unittest.mock import AsyncMock
    mgr = AutomatedCuration.__new__(AutomatedCuration)
    mgr.ref_curation_command_base = "http://x"
    mgr.CATALOG_TARGET_LABEL = "CatalogTarget"
    mgr._async_get_name_request = AsyncMock(return_value=[])
    asyncio.run(AutomatedCuration._async_get_catalog_targets(mgr, "6b0b3c8e-1c36-4f0e-8a4e-111111111111"))
    gen = mgr._async_get_name_request.call_args.kwargs["_gen_output"]
    assert gen.keywords["integ_connector_guid"] == "6b0b3c8e-1c36-4f0e-8a4e-111111111111"
