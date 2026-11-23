"""PY-64: where a live check on 6.4 (read-only, 2026-11-23) showed find("*") returns the same element type and
shape as the by-name call, a by-name helper asked for "*" (or None, or "") runs its find. Every other helper keeps
PY-63's refusal. Fixtures use SYNTHETIC values on the key sets the live check saw (the laz data holds realistic
personal values and the fork is public)."""
import asyncio
import importlib
import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyegeria import PyegeriaInvalidParameterException

# key: (module, class, by-name helper, find, the element's typeName and top-level keys from the live check or None)
ROUTED = {
    "note_logs": ("pyegeria.core._server_client", "ServerClient", "get_note_logs_by_name", "find_note_logs",
                  "NoteLog", ["noteLogEntries", "noteLogSubjects", "mermaidGraph"]),
    "search_keyword": ("pyegeria.core._server_client", "ServerClient", "get_search_keyword_by_keyword",
                       "find_search_keywords", "SearchKeyword", ["keywordElements", "mermaidGraph"]),
    "actor_profiles": ("pyegeria.omvs.actor_manager", "ActorManager", "get_actor_profiles_by_name",
                       "find_actor_profiles", "Person", []),
    "actor_roles": ("pyegeria.omvs.actor_manager", "ActorManager", "get_actor_roles_by_name", "find_actor_roles",
                    "PersonRole", ["mermaidGraph", "rolePerformers"]),
    "user_identities": ("pyegeria.omvs.actor_manager", "ActorManager", "get_user_identities_by_name",
                        "find_user_identities", "UserIdentity",
                        ["configuredInSecurityCollections", "mermaidGraph", "userProfile"]),
    "contribution_records": ("pyegeria.omvs.actor_manager", "ActorManager", "get_contribution_records_by_name",
                             "find_contribution_records", "ContributionRecord",
                             ["contributorProfile", "mermaidGraph"]),
    "perspectives": ("pyegeria.omvs.actor_manager", "ActorManager", "get_perspectives_by_name", "find_perspectives",
                     "Perspective", ["memberOfCollections", "mermaidGraph", "scopedElements"]),
    "contact_details": ("pyegeria.omvs.actor_manager", "ActorManager", "get_contact_details_by_name",
                        "find_contact_details", "ContactDetails", ["contacts", "mermaidGraph"]),
    "assets": ("pyegeria.omvs.asset_maker", "AssetMaker", "get_assets_by_name", "find_assets", "Asset", []),
    "software_capabilities": ("pyegeria.omvs.asset_maker", "AssetMaker", "get_software_capabilities_by_name",
                              "find_software_capabilities", "SoftwareCapability", []),
    "collections": ("pyegeria.omvs.collection_manager", "CollectionManager", "get_collections_by_name",
                    "find_collections", "Collection", []),
    "glossaries": ("pyegeria.omvs.glossary_manager", "GlossaryManager", "get_glossaries_by_name", "find_glossaries",
                   "Glossary", ["collectionMembers", "mermaidGraph", "searchKeywords"]),
    "communities": ("pyegeria.omvs.community_matters_omvs", "CommunityMatters", "get_communities_by_name",
                    "find_communities", "Community", []),
    "locations": ("pyegeria.omvs.location_arena", "LocationArena", "get_locations_by_name", "find_locations",
                  "Location", []),
    "subject_areas": ("pyegeria.omvs.subject_area", "SubjectArea", "get_subject_areas_by_name", "find_subject_areas",
                      "SubjectArea", []),
    "business_capabilities": ("pyegeria.omvs.digital_business", "DigitalBusiness",
                              "get_business_capabilities_by_name", "find_business_capabilities",
                              "BusinessCapability", []),
    "valid_value_definitions": ("pyegeria.omvs.reference_data", "ReferenceDataManager",
                                "get_valid_value_definitions_by_name", "find_valid_value_definitions",
                                "ValidValueDefinition", []),
    "statements_of_applicability": ("pyegeria.omvs.security_officer", "SecurityOfficer",
                                    "get_statements_of_applicability_by_name",
                                    "find_statements_of_applicability", "StatementOfApplicability", []),
    "connections": ("pyegeria.omvs.connection_maker", "ConnectionMaker", "get_connections_by_name",
                    "find_connections", "Connection",
                    ["connectedResources", "connectorType", "endpoint", "mermaidGraph"]),
    "connector_types": ("pyegeria.omvs.connection_maker", "ConnectionMaker", "get_connector_types_by_name",
                        "find_connector_types", "ConnectorType", []),
    "endpoints": ("pyegeria.omvs.connection_maker", "ConnectionMaker", "get_endpoints_by_name", "find_endpoints",
                  "Endpoint", []),
    "data_structures": ("pyegeria.omvs.data_designer", "DataDesigner", "get_data_structures_by_name",
                        "find_data_structures", "DataStructure", []),
    "data_fields": ("pyegeria.omvs.data_designer", "DataDesigner", "get_data_fields_by_name", "find_data_fields",
                    "DataField", ["implementedBy", "memberOfCollections", "mermaidGraph", "partOfDataStructures"]),
    "data_value_specifications": ("pyegeria.omvs.data_designer", "DataDesigner",
                                  "get_data_value_specifications_by_name", "find_data_value_specifications",
                                  "DataValueSpecification", []),
    "external_references": ("pyegeria.omvs.external_links", "ExternalReferences",
                            "get_external_references_by_name", "find_external_references", "ExternalReference", []),
    "external_identifiers": ("pyegeria.omvs.external_links", "ExternalReferences",
                             "get_external_identifiers_by_name", "find_external_identifiers",
                             "ExternalIdentifier", []),
    "governance_definitions": ("pyegeria.omvs.governance_officer", "GovernanceOfficer",
                               "get_governance_definitions_by_name", "find_governance_definitions",
                               "NotificationType", []),
    "schema_attributes": ("pyegeria.omvs.schema_maker", "SchemaMaker", "get_schema_attributes_by_name",
                          "find_schema_attributes", "SchemaAttribute", []),
    "design_patterns": ("pyegeria.omvs.solution_architect", "SolutionArchitect", "get_design_patterns_by_name",
                        "find_design_patterns", "DesignPattern", []),
}

# kept refusing: not routed, with the reason (RULING / live check 2026-11-23)
REFUSED = {
    # (a) pairs the live check could not prove
    "tags": ("pyegeria.core._server_client", "ServerClient", "get_tags_by_name"),                  # find("*") empty
    "skills": ("pyegeria.omvs.actor_manager", "ActorManager", "get_skills_by_name"),               # find("*") empty
    "context_events": ("pyegeria.omvs.time_keeper", "TimeKeeper", "get_context_events_by_name"),   # find("*") empty
    "data_values": ("pyegeria.omvs.data_engineer", "DataEngineer", "get_data_values_by_name"),     # find("*") empty
    "decisions": ("pyegeria.omvs.governance_officer", "GovernanceOfficer", "get_decisions_by_name"),  # empty
    "digital_products": ("pyegeria.omvs.product_manager", "ProductManager", "get_digital_products_by_name"),
    "digital_product_catalogs": ("pyegeria.omvs.product_manager", "ProductManager",
                                 "get_digital_product_catalogs_by_name"),                           # PY-71
    "metadata_repository_cohorts": ("pyegeria.omvs.runtime_manager", "RuntimeManager",
                                    "get_metadata_repository_cohorts_by_name"),                    # find("*") empty
    "concept_model_elements": ("pyegeria.omvs.solution_architect", "SolutionArchitect",
                               "get_concept_model_elements_by_name"),                               # find("*") empty
    "engine_actions": ("pyegeria.omvs.automated_curation", "AutomatedCuration", "get_engine_actions_by_name"),  # 408
    "annotations": ("pyegeria.omvs.data_discovery", "DataDiscovery", "get_annotations_by_name"),    # other property
    # the report-spec / output_format default differs between the helper and its find
    "terms": ("pyegeria.omvs.glossary_manager", "GlossaryManager", "get_terms_by_name"),
    "specification_property": ("pyegeria.omvs.valid_metadata", "ValidMetadataManager",
                               "get_specification_property_by_name"),
    "projects": ("pyegeria.omvs.project_manager", "ProjectManager", "get_projects_by_name"),
    "schema_types": ("pyegeria.omvs.schema_maker", "SchemaMaker", "get_schema_types_by_name"),
    # (b) not routed by design
    "servers": ("pyegeria.omvs.runtime_manager", "RuntimeManager", "get_servers_by_name"),
    "solution_ports": ("pyegeria.omvs.solution_architect", "SolutionArchitect", "get_solution_ports_by_name"),
    "governance_action_processes": ("pyegeria.omvs.product_manager", "ProductManager",
                                    "get_governance_action_processes_by_name"),
}


def _lenient(self, name):
    if name.startswith("__"):
        raise AttributeError(name)
    return "http://x"


def _client(module, cls, elements=None):
    klass = getattr(importlib.import_module(module), cls)
    klass = type(klass.__name__, (klass,), {"__getattr__": _lenient})
    obj = klass.__new__(klass)
    resp = MagicMock()
    resp.json.return_value = {"elements": elements if elements is not None else []}
    obj._async_make_request = AsyncMock(return_value=resp)
    obj._async_refresh_report_spec = AsyncMock(return_value=None)
    return obj


def _helper(obj, name):
    return getattr(obj, "_async_" + name)


KEYS = [None, "", "*"]


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("pair", sorted(ROUTED))
def test_a_missing_or_star_name_runs_the_find(pair, key):
    module, cls, helper, find = ROUTED[pair][:4]
    obj = _client(module, cls)
    find_mock = AsyncMock(return_value=["found"])
    setattr(obj, "_async_" + find, find_mock)
    out = asyncio.run(_helper(obj, helper)(key))
    assert out == ["found"]
    assert find_mock.await_args.args == ("*",)
    obj._async_make_request.assert_not_called()


@pytest.mark.parametrize("pair", sorted(ROUTED))
def test_a_real_name_does_not_run_the_find(pair):
    module, cls, helper, find = ROUTED[pair][:4]
    obj = _client(module, cls)
    find_mock = AsyncMock(return_value=["found"])
    setattr(obj, "_async_" + find, find_mock)
    try:
        asyncio.run(_helper(obj, helper)("Some Name"))
    except PyegeriaInvalidParameterException:
        raise
    except Exception:
        pass
    find_mock.assert_not_called()
    assert obj._async_make_request.called


def test_the_callers_paging_and_format_go_to_the_find_and_the_body_is_not_routed():
    module, cls, helper, find = ROUTED["glossaries"][:4]
    obj = _client(module, cls)
    find_mock = AsyncMock(return_value=[])
    setattr(obj, "_async_" + find, find_mock)
    asyncio.run(_helper(obj, helper)("*", start_from=5, page_size=7, output_format="DICT", report_spec="X"))
    assert find_mock.await_args.kwargs == {"start_from": 5, "page_size": 7, "output_format": "DICT",
                                           "report_spec": "X"}
    find_mock.reset_mock()
    try:
        asyncio.run(_helper(obj, helper)(None, body={"filter": "G"}))
    except Exception:
        pass
    find_mock.assert_not_called()


@pytest.mark.parametrize("key", KEYS)
@pytest.mark.parametrize("pair", sorted(REFUSED))
def test_the_refused_helpers_still_refuse(pair, key):
    module, cls, helper = REFUSED[pair]
    obj = _client(module, cls)
    fn = _helper(obj, helper)
    first = list(inspect.signature(fn).parameters)[0]
    default = inspect.signature(fn).parameters[first].default
    if key is None and default not in (None, inspect.Parameter.empty, "", "*"):
        pytest.skip("the helper has its own non-empty default")
    with pytest.raises(PyegeriaInvalidParameterException):
        asyncio.run(fn(key))
    obj._async_make_request.assert_not_called()


@pytest.mark.parametrize("pair", sorted(ROUTED))
def test_the_report_spec_and_output_format_defaults_match_the_find(pair):
    module, cls, helper, find = ROUTED[pair][:4]
    klass = getattr(importlib.import_module(module), cls)
    h = inspect.signature(getattr(klass, "_async_" + helper)).parameters
    f = inspect.signature(getattr(klass, "_async_" + find)).parameters
    for name in ("report_spec", "output_format"):
        hd = h[name].default if name in h else inspect.Parameter.empty
        fd = f[name].default if name in f else inspect.Parameter.empty
        assert hd == fd, (pair, name, hd, fd)


def _element(type_name, extra_keys, n):
    el = {"class": "OpenMetadataRootElement",
          "elementHeader": {"guid": f"00000000-0000-0000-0000-00000000000{n}",
                            "type": {"typeName": type_name}},
          "properties": {"class": f"{type_name}Properties", "qualifiedName": f"{type_name}::Synthetic {n}",
                         "displayName": f"Synthetic {n}"}}
    for key in extra_keys:
        el[key] = [] if key != "mermaidGraph" else "graph LR"
    return el


@pytest.mark.parametrize("pair", sorted(ROUTED))
def test_the_routed_answer_is_the_find_answer_for_a_real_shaped_element(pair):
    module, cls, helper, find, type_name, extra = ROUTED[pair]
    elements = [_element(type_name, extra, 1), _element(type_name, extra, 2)]
    by_star = _client(module, cls, elements)
    direct = _client(module, cls, elements)
    got = asyncio.run(_helper(by_star, helper)("*"))
    want = asyncio.run(getattr(direct, "_async_" + find)("*"))
    assert got == want
    assert isinstance(got, list) and [e["elementHeader"]["type"]["typeName"] for e in got] == [type_name] * 2
    assert sorted(got[0]) == sorted(elements[0])
