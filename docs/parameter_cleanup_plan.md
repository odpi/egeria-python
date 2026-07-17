# Parameter Cleanup Plan

## Overview
This document tracks the standardization of `get` and `find` methods across the `pyegeria` SDK to ensure consistency, discoverability, and compatibility with the reporting engine and MCP adapter.

## Key Requirements (==>)
- **Consistent Parameters**: All retrieval methods must consistently expose `graph_query_depth` and `metadata_element_type_name`.
- **Search Defaults**: `find_xxx` methods should use `search_string='*'` as the default.
- **Output Defaults**: `output_format` should default to `'JSON'`.
- **Flexibility**: Use `**kwargs` to allow passing additional parameters to the reporting engine or Egeria body.
- **Pydantic Alignment**: Method signatures should reflect valid parameters for the corresponding Egeria Pydantic models (e.g., `FindRequestBody`, `SearchStringRequestBody`).

## Standard Patterns

### find_xxx (Search)
```python
async def _async_find_xxx(
    self,
    search_string: str = "*",
    starts_with: bool = True,
    ends_with: bool = False,
    ignore_case: bool = True,
    metadata_element_type_name: str | None = None,
    metadata_element_subtypes: list[str] | None = None,
    include_only_relationships: list[str] | None = None,
    skip_relationships: list[str] | None = None,
    graph_query_depth: int = 3,
    as_of_time: datetime | str | None = None,
    start_from: int = 0,
    page_size: int = 0,
    sequencing_order: str | None = None,
    sequencing_property: str | None = None,
    output_format: str = "JSON",
    report_spec: str | dict | None = None,
    body: dict | SearchStringRequestBody | FindRequestBody | None = None,
    **kwargs
)
```

### get_xxx_by_name (Filtering)
```python
async def _async_get_xxx_by_name(
    self,
    name: str,
    metadata_element_type_name: str | None = None,
    metadata_element_subtypes: list[str] | None = None,
    include_only_relationships: list[str] | None = None,
    skip_relationships: list[str] | None = None,
    graph_query_depth: int = 3,
    start_from: int = 0,
    page_size: int = 0,
    output_format: str = "JSON",
    report_spec: str | dict | None = None,
    body: dict | FilterRequestBody | None = None,
    **kwargs
)
```

### get_xxx_by_guid (Retrieval)
```python
async def _async_get_xxx_by_guid(
    self,
    guid: str,
    include_only_relationships: list[str] | None = None,
    skip_relationships: list[str] | None = None,
    graph_query_depth: int = 3,
    output_format: str = "JSON",
    report_spec: str | dict | None = None,
    body: dict | GetRequestBody | None = None,
    **kwargs
)
```
## Phase Estimates

| Phase | Description | Estimated Effort |
| :--- | :--- | :--- |
| **Phase 1** | **ServerClient Refinement**: Update base helper methods to support explicit parameter prioritization and body mapping. | 0.5 Day |
| **Phase 2** | **Priority Modules**: Standardize `AssetMaker`, `ConnectionMaker`, `GlossaryManager`, `ProjectManager`. | 2.5 Days |
| **Phase 3** | **Mid-tier Modules**: Standardize 15 modules (e.g., `SubjectArea`, `DigitalBusiness`). | 3.5 Days |
| **Phase 4** | **Final Sweep**: Standardize all remaining 22+ modules. | 4.5 Days |
| **Phase 5** | **Verification**: Audit docstrings and run full scenario test suite. | 2.0 Days |
| **Total** | | **13.0 Days** |

## Method Checklist

### actor_manager.py
- [x] `_async_find_actor_profiles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Actor-Profiles', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_actor_roles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Roles', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_contact_details(self, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_contribution_records(self, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_perspectives(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_skills(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_user_identities(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec='User-Identities', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_actor_profile_by_guid(self, actor_profile_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_actor_profiles_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Profiles')`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_actor_role_by_guid(self, actor_role_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_actor_roles_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Roles')`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_contact_details_by_guid(self, contact_details_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_contact_details_by_name(self, body=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_contribution_record_by_guid(self, contribution_record_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_contribution_records_by_name(self, body=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_perspective_by_guid(self, perspective_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_perspectives_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_skill_by_guid(self, skill_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_skills_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_user_identities_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='User-Identities')`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_user_identity_by_guid(self, user_identity_guid, element_type=None, body=None, output_format='JSON', report_spec='User-Identities')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `find_actor_profiles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Actor-Profiles', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_actor_roles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Roles', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_contact_details(self, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_contribution_records(self, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_perspectives(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_skills(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_user_identities(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec='User-Identities', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_actor_profile_by_guid(self, actor_profile_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_actor_profiles_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Profiles')`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_actor_role_by_guid(self, actor_role_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_actor_roles_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Actor-Roles')`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_contact_details_by_guid(self, contact_details_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_contact_details_by_name(self, body=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_contribution_record_by_guid(self, contribution_record_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_contribution_records_by_name(self, body=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_perspective_by_guid(self, perspective_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_perspectives_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_skill_by_guid(self, skill_guid, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_skills_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_user_identities_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='User-Identities')`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_user_identity_by_guid(self, user_identity_guid, element_type=None, body=None, output_format='JSON', report_spec='User-Identities')`
  - **Planned**: Standard Get By GUID Pattern

### asset_catalog.py
- [x] `_async_find_in_asset_domain(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_asset_graph(self, asset_guid, start_from=0, page_size=0, output_format='MERMAID', report_spec='Common-Mermaid', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_asset_lineage_graph(self, asset_guid, effective_time=None, as_of_time=None, relationship_types=None, limit_to_isc_q_name=None, hilight_isc_q_name=None, all_anchors=False, start_from=0, page_size=0, output_format='DICT', report_spec='Common-Mermaid')`
  - **Planned**: TODO
- [ ] `_async_get_asset_types(self)`
  - **Planned**: TODO
- [ ] `_async_get_assets_by_metadata_collection_id(self, metadata_collection_id, type_name=None, effective_time=None, start_from=0, page_size=0, output_format='JSON', report_spec='Referenceable')`
  - **Planned**: TODO
- [x] `find_in_asset_domain(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_asset_graph(self, asset_guid, start_from=0, page_size=0, output_format='MERMAID', report_spec='Common-Mermaid', body=None)`
  - **Planned**: TODO
- [ ] `get_asset_lineage_graph(self, asset_guid, effective_time=None, as_of_time=None, relationship_types=None, limit_to_isc_q_name=None, hilight_isc_q_name=None, all_anchors=False, start_from=0, page_size=0, output_format='DICT', report_spec='Common-Mermaid')`
  - **Planned**: TODO
- [ ] `get_asset_lineage_mermaid_graph(self, asset_guid, effective_time=None, as_of_time=None, relationship_types=None, limit_to_isc_q_name=None, hilight_isc_q_name=None, start_from=0, page_size=max_paging_size)`
  - **Planned**: TODO
- [ ] `get_asset_mermaid_graph(self, asset_guid, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_asset_types(self)`
  - **Planned**: TODO
- [ ] `get_assets_by_metadata_collection_id(self, metadata_collection_id, type_name=None, effective_time=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Referenceable')`
  - **Planned**: TODO

### asset_maker.py
- [x] `_async_find_assets(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0, property_names: Optional[list[str]] = None, body: dict | SearchStringRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_data_assets(self, search_string: str = "*", content_status_list: list[str] = ["ACTIVE"], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ContentStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_infrastructure(self, search_string: str = "*", deployment_status_list: list[str] = ["ACTIVE"], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | DeploymentStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_processes(self, search_string: str = "*", activity_status_list: list[str] = [], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ActivityStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_software_capabilities(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0, property_names: Optional[list[str]] = None, body: dict | SearchStringRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_action_target(self, action_target_guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: str | dict = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_action_targets(self, action_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_actions_for_action_target(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_actions_for_requestor(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_actions_for_sponsor(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [x] `_async_get_asset_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_assets_by_name(self, name: str, metadata_element_type_name: str | None = "Asset", metadata_element_subtypes: list[str] | None = None, include_only_classified_elements: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | FilterRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_assigned_actions(self, actor_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_capability_use(self, asset_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_catalog_target(self, guid: str, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_catalog_targets(self, integration_connector_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_data_assets_by_category(self, category: str, content_status_list: list[str] = ["ACTIVE"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ContentStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_governance_engines(self, governance_service_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_infrastructure_by_category(self, category: str, deployment_status_list: list[str] = ["ACTIVE"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | DeploymentStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_integration_groups(self, integration_connector_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_processes_by_category(self, category: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ActivityStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_software_capabilities_by_deployed_implementation_type(self, deployed_implementation_type: str, metadata_element_type_name: str | None = "SoftwareCapability", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | FilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [x] `_async_get_software_capabilities_by_name(self, name: str, metadata_element_type_name: str | None = "SoftwareCapability", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | FilterRequestBody] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_software_capabilities_for_infrastructure(self, infrastructure_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [x] `_async_get_software_capability_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `find_assets(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0, property_names: Optional[list[str]] = None, body: dict | SearchStringRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_data_assets(self, search_string: str = "*", content_status_list: list[str] = ["ACTIVE"], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ContentStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_infrastructure(self, search_string: str = "*", deployment_status_list: list[str] = ["ACTIVE"], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | DeploymentStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_processes(self, search_string: str = "*", activity_status_list: list[str] = ["IN_PROGRESS"], starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ActivityStatusSearchString] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_software_capabilities(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None, metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None, include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None, include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3, governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0, property_names: Optional[list[str]] = None, body: dict | SearchStringRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_action_target(self, action_target_guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: str | dict = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_action_targets(self, action_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_actions_for_action_target(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_actions_for_requestor(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_actions_for_sponsor(self, metadata_element_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [x] `get_asset_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_assets_by_name(self, name: str, metadata_element_type_name: str | None = "Asset", metadata_element_subtypes: list[str] | None = None, include_only_classified_elements: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | FilterRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_assigned_actions(self, actor_guid: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, body: dict | ActivityStatusRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_capability_use(self, asset_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_catalog_target(self, guid: str, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_catalog_targets(self, integration_connector_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_data_assets_by_category(self, category: str, content_status_list: list[str] = ["ACTIVE"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ContentStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_governance_engines(self, governance_service_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_infrastructure_by_category(self, category: str, deployment_status_list: list[str] = ["ACTIVE"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | DeploymentStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_integration_groups(self, integration_connector_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_processes_by_category(self, category: str, activity_status_list: list[str] = ["IN_PROGRESS"], graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | ActivityStatusFilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_software_capabilities_by_deployed_implementation_type(self, deployed_implementation_type: str, metadata_element_type_name: str | None = "SoftwareCapability", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | FilterRequestBody] = None, **kwargs)`
  - **Planned**: TODO
- [x] `get_software_capabilities_by_name(self, name: str, metadata_element_type_name: str | None = "SoftwareCapability", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = None, body: Optional[dict | FilterRequestBody] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_software_capabilities_for_infrastructure(self, infrastructure_guid: str, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | ResultsRequestBody | None = None, **kwargs)`
  - **Planned**: TODO
- [x] `get_software_capability_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: dict | str | None = None, body: dict | GetRequestBody | None = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern

### automated_curation.py
- [x] `_async_find_engine_actions(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='EngineAction', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_active_engine_actions(self, start_from=0, page_size=0, output_format='JSON', report_spec='Engine-Actions')`
  - **Planned**: TODO
- [ ] `_async_get_all_technology_types(self, start_from=0, page_size=0, output_format='JSON', report_spec='TechType')`
  - **Planned**: TODO
- [ ] `_async_get_catalog_target(self, relationship_guid, output_format='JSON', report_spec='CatalogTarget', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_catalog_targets(self, integ_connector_guid, start_from=0, page_size=0, output_format='JSON', report_spec='CatalogTarget', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_create_csv_data_file_element_from_template(self, file_name, file_type, file_path_name, version_identifier, file_encoding='UTF-8', file_extension='csv', file_system_name=None, description=None)`
  - **Planned**: TODO
- [ ] `_async_get_engine_actions(self, start_from=0, page_size=0, output_format='JSON', report_spec='EngineAction', body=None)`
  - **Planned**: TODO
- [x] `_async_get_engine_actions_by_name(self, name, start_from=0, page_size=0, output_format='JSON', report_spec='EngineAction', body=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_tech_type_detail(self, filter_string=None, body=None, output_format='JSON', report_spec='TechType', **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_tech_type_hierarchy(self, filter_string=None, body=None, output_format='JSON', report_spec='TechType', **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_tech_types_for_open_metadata_type(self, type_name, tech_name, start_from=0, page_size=0, output_format='JSON', report_spec='TechType', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_technology_type_elements(self, filter_string, effective_time=None, start_from=0, page_size=0, get_templates=False, output_format='JSON', report_spec='Tech-Type-Elements', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_template_guid_for_technology_type(self, type_name)`
  - **Planned**: TODO
- [x] `find_engine_actions(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='EngineAction', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_technology_types(self, search_string='*', body=None, starts_with=False, ends_with=False, ignore_case=True, start_from=0, page_size=0, output_format='JSON', report_spec='TechType', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_technology_types_body(self, search_string='*', starts_with=False, ends_with=False, ignore_case=True, anchor_domain=None, metadata_element_type=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=[], sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', output_format='JSON', report_spec='TechType', start_from=0, page_size=0, property_names=None, body=None)`
  - **Planned**: Standard Find Pattern
- [ ] `get_active_engine_actions(self, start_from=0, page_size=0, output_format='JSON', report_spec='EngineAction')`
  - **Planned**: TODO
- [ ] `get_all_technology_types(self, start_from=0, page_size=0, output_format='JSON', report_spec='TechType')`
  - **Planned**: TODO
- [ ] `get_catalog_target(self, relationship_guid, output_format='JSON', report_spec='CatalogTarget', body=None)`
  - **Planned**: TODO
- [ ] `get_catalog_targets(self, integ_connector_guid, start_from=0, page_size=0, output_format='JSON', report_spec='CatalogTarget', body=None)`
  - **Planned**: TODO
- [ ] `get_create_csv_data_file_element_from_template(self, file_name, file_type, file_path_name, version_identifier, file_encoding='UTF-8', file_extension='csv', file_system_name=None, description=None)`
  - **Planned**: TODO
- [ ] `get_engine_actions(self, start_from=0, page_size=0, output_format='JSON', report_spec='EngineAction', body=None)`
  - **Planned**: TODO
- [x] `get_engine_actions_by_name(self, name, start_from=0, page_size=0, output_format='JSON', report_spec='EngineAction', body=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_tech_type_detail(self, filter_string=None, body=None, output_format='JSON', report_spec='TechType', **kwargs)`
  - **Planned**: TODO
- [ ] `get_tech_type_hierarchy(self, filter_string=None, body=None, output_format='JSON', report_spec='TechType', **kwargs)`
  - **Planned**: TODO
- [ ] `get_tech_types_for_open_metadata_type(self, type_name, tech_name, start_from=0, page_size=0, output_format='JSON', report_spec='TechType', body=None)`
  - **Planned**: TODO
- [ ] `get_technology_type_elements(self, filter_string, effective_time=None, start_from=0, page_size=0, get_templates=False, output_format='JSON', report_spec='Tech-Type-Elements', body=None)`
  - **Planned**: TODO
- [ ] `get_template_guid_for_technology_type(self, type_name)`
  - **Planned**: TODO

### classification_explorer.py
- [x] `_async_find_authored_elements(self, search_string='*', content_status_list=[], starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_authored_elements_by_category(self, filter_string='*', content_status_list=[], start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_elements_by_classification_with_property_value(self, classification_name, property_value, property_names, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_elements_by_property_value(self, property_value, property_names, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_related_elements_with_property_value(self, element_guid, relationship_type, property_value, property_names, metadata_element_type_name=None, start_at_end=1, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_relationships_with_property_value(self, property_value, property_names, relationship_type=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_root_elements(self, metadata_element_type_name=None, search_properties=None, match_classifications=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_certifications(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_certified_elements(self, certification_type_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_classified_elements_by(self, classification_name, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_element_by_guid(self, element_guid, element_type_name=None, output_format='JSON', report_spec='Referenceable', body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_element_by_unique_name(self, name, property_name=None, output_format='JSON', report_spec='Referenceable', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_element_guid_by_unique_name(self, name, property_name=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements(self, metadata_element_type='Referenceable', start_from=0, page_size=10, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements_by_classification(self, classification_name, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements_by_classification_with_property_value(self, classification_name, property_value, property_names=None, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements_by_origin(self, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements_by_property_value(self, property_value=None, property_names=None, metadata_element_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, anchor_scope_guid=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_elements_sourced_from(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_governed_by_definitions(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_governed_elements(self, gov_def_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_guid_for_name(self, name, property_name=[], type_name=None)`
  - **Planned**: TODO
- [ ] `_async_get_licensed_elements(self, license_type_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_licenses(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_meanings(self, element_guid, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_owners_elements(self, owner_name, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_related_elements(self, element_guid, relationship_type=None, start_at_end=1, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_related_elements_with_property_value(self, element_guid, relationship_type, property_value, property_names=None, metadata_element_type_name=None, start_at_end=1, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_relationships(self, relationship_type=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_relationships_with_property_value(self, property_value, property_names, relationship_type=None, effective_time=None, for_lineage=False, for_duplicate_processing=False, start_from=0, page_size=0, timeout=default_timeout, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_scoped_elements(self, scope_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_scopes(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_security_tagged_elements(self, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_semantic_asignees(self, term_guid, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_source_elements(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_subject_area_members(self, subject_area, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `find_authored_elements(self, search_string='*', content_status_list=[], starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_authored_elements_by_category(self, filter_string='*', content_status_list=[], start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_elements_by_classification_with_property_value(self, classification_name, property_value, property_names, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_elements_by_property_value(self, property_value, property_names, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_related_elements_with_property_value(self, element_guid, relationship_type, property_value, property_names, metadata_element_type_name=None, start_at_end=1, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_relationships_with_property_value(self, property_value, property_names, relationship_type=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_root_elements(self, metadata_element_type_name=None, search_properties=None, match_classifications=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, timeout=default_timeout, body=None)`
  - **Planned**: Standard Find Pattern
- [ ] `get_actor_for_guid(self, guid)`
  - **Planned**: TODO
- [ ] `get_certifications(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_certified_elements(self, certification_type_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_classified_elements_by(self, classification_name, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_element_by_guid(self, element_guid, element_type_name=None, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_element_by_unique_name(self, name, property_name=None, output_format='JSON', report_spec='Referenceable', body=None)`
  - **Planned**: TODO
- [ ] `get_element_guid_by_unique_name(self, name, property_name=None, body=None)`
  - **Planned**: TODO
- [ ] `get_elements(self, metadata_element_type='Referenceable', start_from=0, page_size=10, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_elements_by_classification(self, classification_name, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_elements_by_classification_with_property_value(self, classification_name, property_value, property_names=None, metadata_element_type_name=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `get_elements_by_origin(self, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_elements_by_property_value(self, property_value=None, property_names=None, metadata_element_type=None, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, anchor_scope_guid=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `get_elements_sourced_from(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_governed_by_definitions(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_governed_elements(self, gov_def_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_guid_for_name(self, name, property_name=[], type_name=None)`
  - **Planned**: TODO
- [ ] `get_licensed_elements(self, license_type_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_licenses(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_meanings(self, element_guid, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_owners_elements(self, owner_name, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_related_elements(self, element_guid, relationship_type=None, start_at_end=1, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_related_elements_with_property_value(self, element_guid, relationship_type, property_value, property_names=None, metadata_element_type_name=None, start_at_end=1, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `get_relationships(self, relationship_type=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_relationships_with_property_value(self, property_value, property_names, relationship_type=None, effective_time=None, for_lineage=False, for_duplicate_processing=False, start_from=0, page_size=0, timeout=default_timeout, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_scoped_elements(self, scope_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_scopes(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_security_tagged_elements(self, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_semantic_asignees(self, term_guid, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_source_elements(self, element_guid, body=None, output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_subject_area_members(self, subject_area, body, output_format='JSON', report_spec=None)`
  - **Planned**: TODO

### collection_manager.py
- [x] `_async_find_collections(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, _type='Collection', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_digital_products(self, search_string='*', deployment_status_list=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_attached_collections(self, parent_guid, start_from=0, page_size=0, category=None, classification_names=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_collection_by_guid(self, collection_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_collection_hierarchy(self, collection_guid, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_collection_members(self, collection_guid=None, collection_name=None, collection_qname=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_collections_by_category(self, category, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_collections_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_digital_products_by_category(self, category, deployment_status_list=None, start_from=0, page_size=100, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_member_list(self, collection_guid=None, collection_name=None, collection_qname=None)`
  - **Planned**: TODO
- [x] `find_collections(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, _type='Collection', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_digital_products(self, search_string='*', deployment_status_list=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [ ] `get_attached_collections(self, parent_guid, start_from=0, page_size=0, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_collection_by_guid(self, collection_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_collection_hierarchy(self, collection_guid=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_collection_members(self, collection_guid=None, collection_name=None, collection_qname=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_collections_by_category(self, category, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_collections_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_digital_products_by_category(self, category, deployment_status_list=None, start_from=0, page_size=100, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_member_list(self, collection_guid=None, collection_name=None, collection_qname=None)`
  - **Planned**: TODO

### community_matters_omvs.py
- [x] `_async_find_communities(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_communities_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_community_by_guid(self, community_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `find_communities(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_communities_by_name(self, filter_string=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_community_by_guid(self, community_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern

### connection_maker.py
- [x] `_async_find_connections(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_connector_types(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_endpoints(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_connection_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_connections_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_connector_type_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_connector_types_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_endpoint_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_endpoints_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_endpoints_by_network_address(self, network_address: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_endpoints_for_asset(self, asset_guid: str, name: str = "*", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: TODO
- [x] `find_connections(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_connector_types(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_endpoints(self, search_string: str = "*", starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True, metadata_element_type: str | None = None, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, as_of_time: Optional[str] = None, start_from: int = 0, page_size: int = 0, sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[SearchStringRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_connection_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_connections_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_connector_type_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_connector_types_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_endpoint_by_guid(self, guid: str, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[GetRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_endpoints_by_name(self, name: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_endpoints_by_network_address(self, network_address: str, metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_endpoints_for_asset(self, asset_guid: str, name: str = "*", metadata_element_subtypes: list[str] | None = None, include_only_relationships: list[str] | None = None, skip_relationships: list[str] | None = None, graph_query_depth: int = 3, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: Optional[str | dict] = None, body: Union[FilterRequestBody, dict] = None, **kwargs)`
  - **Planned**: TODO

### core_omag_server_config.py
- [ ] `get_access_service_config(self, access_service_name, server_name=None)`
  - **Planned**: TODO
- [ ] `get_access_services_configuration(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_audit_log_destinations(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_basic_server_properties(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_cohort_config(self, cohort_name, server_name=None)`
  - **Planned**: TODO
- [ ] `get_configured_access_services(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_configured_view_svcs(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_engine_host_services_config(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_event_bus(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_integration_groups_config(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_local_metadata_collection_id(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_local_metadata_collection_name(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_local_repository_config(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_open_metadata_archives(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_placeholder_variables(self)`
  - **Planned**: TODO
- [ ] `get_server_classification(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_server_security_connection(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_server_type_classification(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_stored_configuration(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_view_svc_config(self, service_url_marker, server_name=None)`
  - **Planned**: TODO
- [ ] `get_view_svcs_config(self, server_name=None)`
  - **Planned**: TODO

### data_designer.py
- [x] `_async_find_all_data_fields(self, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_all_data_structures(self, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_data_fields(self, search_string, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_data_structures(self, search_string, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_data_value_specifications(self, search_string, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_data_class_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_data_field_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_data_field_rel_elements(self, guid)`
  - **Planned**: TODO
- [x] `_async_get_data_fields_by_name(self, filter_string, classification_names=None, body=..., start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_data_structure_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_data_structures_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_data_value_specification_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_data_value_specifications_by_name(self, filter_string, classification_names, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_all_data_fields(self, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_all_data_structures(self, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_data_fields(self, search_string, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=100, property_names=None, body=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_data_structures(self, search_string, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_data_value_specifications(self, search_string, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_data_class_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_data_class_rel_elements(self, guid)`
  - **Planned**: TODO
- [x] `get_data_field_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_data_field_rel_elements(self, guid)`
  - **Planned**: TODO
- [x] `get_data_fields_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_data_grain_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_data_grain_rel_elements(self, guid)`
  - **Planned**: TODO
- [ ] `get_data_memberships(self, data_get_fcn, data_struct_guid)`
  - **Planned**: TODO
- [ ] `get_data_memberships_with_dict(self, data_field_elements)`
  - **Planned**: TODO
- [ ] `get_data_rel_elements_dict(self, el_struct)`
  - **Planned**: TODO
- [x] `get_data_structure_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_data_structures_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_data_value_specification_by_guid(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_data_value_specification_rel_elements(self, guid)`
  - **Planned**: TODO
- [x] `get_data_value_specifications_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### data_discovery.py
- [x] `_async_find_annotations(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_annotation_by_guid(self, annotation_guid, element_type='Annotation', body=None, output_format='JSON', report_spec='Annotations')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_annotations_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Annotations')`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_annotations(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_annotation_by_guid(self, annotation_guid, element_type='Annotation', body=None, output_format='JSON', report_spec='Annotations')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_annotations_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Annotations')`
  - **Planned**: Standard Get By Name Pattern

### data_engineer.py
- [x] `_async_find_tabular_data_sets(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_tabular_data_set(self, tabular_data_set_guid, start_from_row=0, max_row_count=5000, output_format='JSON')`
  - **Planned**: TODO
- [x] `find_tabular_data_sets(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_tabular_data_set(self, tabular_data_set_guid, start_from_row=0, max_row_count=5000, output_format='JSON')`
  - **Planned**: TODO

### digital_business.py
- [x] `_async_find_business_capabilities(self, search_string='*', body=None, starts_with=False, ends_with=False, ignore_case=True, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_business_capabilities_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_business_capability_by_guid(self, business_capability_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `find_business_capabilities(self, search_string='*', body=None, starts_with=False, ends_with=False, ignore_case=True, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_business_capabilities_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_business_capability_by_guid(self, business_capability_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern

### external_links.py
- [x] `_async_find_external_references(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='ExternalReference', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_external_reference_by_guid(self, ext_ref_guid, element_type=None, body=None, output_format='JSON', report_spec='ExternalReference')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_external_references_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='ExternalReference')`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_external_references(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='ExternalReference', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_external_reference_by_guid(self, ext_ref_guid, element_type=None, body=None, output_format='JSON', report_spec='ExternalReference')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_external_references_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='ExternalReference')`
  - **Planned**: Standard Get By Name Pattern

### full_omag_server_config.py
- [ ] `get_access_services_topic_names(self, access_service_name, server_name=None)`
  - **Planned**: TODO
- [ ] `get_all_access_services_topic_names(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_cohort_topic_name(self, cohort_name, server_name=None)`
  - **Planned**: TODO
- [ ] `get_dedicated_cohort_topic_names(self, cohort_name, server_name=None)`
  - **Planned**: TODO
- [ ] `get_event_bus(self, server_name=None)`
  - **Planned**: TODO
- [ ] `get_integration_service_config(self, service_url_marker, server_name=None)`
  - **Planned**: TODO
- [ ] `get_integration_services_configs(self, server_name=None)`
  - **Planned**: TODO

### glossary_manager.py
- [x] `_async_find_glossaries(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_glossary_terms(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Glossary-Term-DrE', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_glossaries_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_glossary_by_guid(self, glossary_guid, element_type='Glossary', body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_glossary_term_activity_types(self)`
  - **Planned**: TODO
- [ ] `_async_get_glossary_term_rel_statuses(self)`
  - **Planned**: TODO
- [ ] `_async_get_glossary_term_statuses(self)`
  - **Planned**: TODO
- [x] `_async_get_term_by_guid(self, term_guid, element_type='GlossaryTerm', body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_term_relationship_types(self)`
  - **Planned**: TODO
- [x] `_async_get_terms_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_glossaries(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type='Glossary', metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=100, property_names=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_glossary_terms(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type='GlossaryTerm', metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec='Glossary-Term-DrE', start_from=0, page_size=100, property_names=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `get_glossaries_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_glossary_by_guid(self, glossary_guid, element_type='Glossary', body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_glossary_term_activity_types(self)`
  - **Planned**: TODO
- [ ] `get_glossary_term_rel_statuses(self)`
  - **Planned**: TODO
- [ ] `get_glossary_term_statuses(self)`
  - **Planned**: TODO
- [x] `get_term_by_guid(self, term_guid, element_type='GlossaryTerm', body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_term_relationship_types(self)`
  - **Planned**: TODO
- [x] `get_terms_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### governance_officer.py
- [x] `_async_find_governance_definitions(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_governance_definition_by_guid(self, definition_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_governance_definitions_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_governance_process_graph(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `find_governance_definitions(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_governance_definition_by_guid(self, definition_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_governance_definitions_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_governance_process_graph(self, guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO

### location_arena.py
- [x] `_async_find_locations(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_location_by_guid(self, location_guid, element_type=None, body=None, output_format='JSON', report_spec='Locations')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_locations_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Locations')`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_locations(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_location_by_guid(self, location_guid, element_type=None, body=None, output_format='JSON', report_spec='Locations')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_locations_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='Locations')`
  - **Planned**: Standard Get By Name Pattern

### metadata_expert.py
- [x] `_async_find_elements_for_anchor(self, anchor_guid, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_elements_in_anchor_domain(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_elements_in_anchor_scope(self, anchor_scope_guid, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_metadata_elements(self, body, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_metadata_elements_with_string(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_relationships_between_elements(self, body, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_all_metadata_element_relationships(self, end1_guid, end2_guid, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [ ] `_async_get_all_related_elements(self, element_guid, starting_at_end=0, start_from=0, page_size=0, graph_query_depth=5, relationships_page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_anchored_element_graph(self, guid, effective_time=None, as_of_time=None, mermaid_only=False, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_classification_history(self, guid, classification_name, effective_time=None, oldest_first=False, from_time=None, to_time=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_element_history(self, guid, effective_time=None, oldest_first=False, from_time=None, to_time=None, start_from=0, page_size=0, body=None)`
  - **Planned**: TODO
- [x] `_async_get_metadata_element_by_guid(self, guid, effective_time=None, as_of_time=None, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_metadata_element_by_unique_name(self, name, property_name='qualifiedName', effective_time=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_metadata_element_relationships(self, end1_guid, end2_guid, relationship_type, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [ ] `_async_get_metadata_guid_by_unique_name(self, name, property_name, as_of_time=None, effective_time=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_related_metadata_elements(self, element_guid, relationship_type, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [x] `_async_get_relationship_by_guid(self, guid, effective_time=None, as_of_time=None, for_lineage=None, for_duplicate_processing=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_relationship_history(self, guid, effective_time=None, oldest_first=False, from_time=None, to_time=None, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [x] `find_elements_for_anchor(self, anchor_guid, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_elements_in_anchor_domain(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_elements_in_anchor_scope(self, anchor_scope_guid, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_metadata_elements(self, body, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout)`
  - **Planned**: Standard Find Pattern
- [x] `find_metadata_elements_with_string(self, search_string='*', starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, zone_filter=None, metadata_element_type=None, metadata_element_sub_type=None, skip_relationships=None, include_only_relationships=None, relationship_page_size=10, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=5, as_of_time=None, effective_time=None, limit_results_by_status=None, sequencing_order='PROPERTY_ASCENDING', sequencing_property='qualifiedName', start_from=0, page_size=0, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_relationships_between_elements(self, body, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: Standard Find Pattern
- [ ] `get_all_metadata_element_relationships(self, end1_guid, end2_guid, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [ ] `get_all_related_elements(self, element_guid, starting_at_end=0, start_from=0, page_size=max_paging_size, graph_query_depth=5, relationships_page_size=0, body=None)`
  - **Planned**: TODO
- [ ] `get_anchored_element_graph(self, guid, effective_time=None, as_of_time=None, mermaid_only=False, body=None)`
  - **Planned**: TODO
- [ ] `get_classification_history(self, guid, classification_name, effective_time=None, oldest_first=False, from_time=None, to_time=None, start_from=0, page_size=max_paging_size, body=None)`
  - **Planned**: TODO
- [ ] `get_element_history(self, guid, effective_time=None, oldest_first=False, from_time=None, to_time=None, start_from=0, page_size=max_paging_size, body=None)`
  - **Planned**: TODO
- [x] `get_metadata_element_by_guid(self, guid, effective_time=None, as_of_time=None, body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_metadata_element_by_unique_name(self, name, property_name='qualifiedName', effective_time=None, body=None)`
  - **Planned**: TODO
- [ ] `get_metadata_element_relationships(self, end1_guid, end2_guid, relationship_type, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [ ] `get_metadata_guid_by_unique_name(self, name, property_name, as_of_time=None, effective_time=None, body=None)`
  - **Planned**: TODO
- [ ] `get_related_metadata_elements(self, guid, relationship_type, body, for_lineage=None, for_duplicate_processing=None, starting_at_end=0, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO
- [x] `get_relationship_by_guid(self, guid, effective_time=None, for_lineage=None, for_duplicate_processing=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_relationship_history(self, guid, effective_time=None, oldest_first=False, from_time=None, to_time=None, for_lineage=None, for_duplicate_processing=None, start_from=0, page_size=max_paging_size, timeout=default_timeout, mermaid_only=False)`
  - **Planned**: TODO

### my_profile.py
- [ ] `_async_get_my_actors(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_my_assigned_actions(self, metadata_element_type='Action', metadata_element_subtypes=[], activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_my_entries(self)`
  - **Planned**: TODO
- [ ] `_async_get_my_profile(self, body=None, output_format='JSON', report_spec='My-User-MD', **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_my_requested_actions(self, activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_my_resources(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_my_roles(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_my_sponsored_actions(self, activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `_async_get_my_to_dos(self, activity_status_list=[], metadata_element_type='Action', metadata_element_subtypes=[], output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `_async_get_my_user_identities(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_my_actors(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_my_assigned_actions(self, metadata_element_type='Action', metadata_element_subtypes=[], activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_my_entries(self)`
  - **Planned**: TODO
- [ ] `get_my_profile(self, body=None, output_format='JSON', report_spec='My-User-MD', **kwargs)`
  - **Planned**: TODO
- [ ] `get_my_requested_actions(self, activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_my_resources(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_my_roles(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_my_sponsored_actions(self, activity_status_list=[], start_from=0, page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, body=None, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: TODO
- [ ] `get_my_to_dos(self, activity_status_list=[], metadata_element_type='Action', metadata_element_subtypes=[], output_format='JSON', report_spec=None, start_from=0, page_size=0)`
  - **Planned**: TODO
- [ ] `get_my_user_identities(self, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO

### platform_services.py
- [ ] `_async_get_active_configuration(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_active_server_instance_status(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_active_server_list(self)`
  - **Planned**: TODO
- [ ] `_async_get_known_servers(self)`
  - **Planned**: TODO
- [ ] `get_active_configuration(self, server=None)`
  - **Planned**: TODO
- [ ] `get_active_server_instance_status(self, server=None)`
  - **Planned**: TODO
- [ ] `get_active_server_list(self)`
  - **Planned**: TODO
- [ ] `get_known_servers(self)`
  - **Planned**: TODO
- [ ] `get_platform_origin(self)`
  - **Planned**: TODO

### product_manager.py
- [x] `_async_find_digital_product_catalogs(self, search_string='*', body=None, starts_with=False, ends_with=False, ignore_case=True, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_digital_products(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, metadata_element_subtype=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_digital_product_by_guid(self, digital_product_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_digital_product_catalog_by_guid(self, digital_product_catalog_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_digital_product_catalogs_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_digital_products_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_digital_product_catalogs(self, search_string='*', body=None, starts_with=False, ends_with=False, ignore_case=True, start_from=0, page_size=0, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_digital_products(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, metadata_element_subtype=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_digital_product_by_guid(self, digital_product_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_digital_product_catalog_by_guid(self, digital_product_catalog_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_digital_product_catalogs_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_digital_products_by_name(self, filter_string, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### project_manager.py
- [x] `_async_find_projects(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_classified_projects(self, project_classification, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_linked_projects(self, parent_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_project_by_guid(self, project_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_project_graph(self, project_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_project_team(self, project_guid, team_role=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `_async_get_projects_by_classification_properties(self, approach=None, management_style=None, results_usage=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [x] `_async_get_projects_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_projects(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_classified_projects(self, project_classification, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_linked_projects(self, parent_guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_project_by_guid(self, project_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_project_graph(self, project_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_project_team(self, project_guid, team_role=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [ ] `get_projects_by_classification_properties(self, approach=None, management_style=None, results_usage=None, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: TODO
- [x] `get_projects_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### reference_data.py
- [x] `_async_find_valid_value_definitions(self, search_string, body=None, starts_with=False, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='json', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_valid_value_definition_by_guid(self, vv_def_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_valid_value_definitions_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_valid_value_definitions(self, search_string, body=None, starts_with=False, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='json', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_valid_value_definition_by_guid(self, vv_def_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_valid_value_definitions_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### runtime_manager.py
- [ ] `_async_get_integration_connector_config_properties(self, connector_name, server_guid=None, server_name=None, qualified_name=None, organization_name=None, output_format='JSON', report_spec='IntegrationConnector', body=None)`
  - **Planned**: TODO
- [x] `_async_get_platform_by_guid(self, platform_guid, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_platform_report(self, platform_guid=None, platform_name=None, output_format='JSON', report_spec='Platform-Report')`
  - **Planned**: TODO
- [ ] `_async_get_platform_templates_by_type(self, filter_string=None, effective_time=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: TODO
- [x] `_async_get_platforms_by_name(self, filter_string=None, start_from=0, page_size=0, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_platforms_by_type(self, filter_string=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: TODO
- [x] `_async_get_server_by_guid(self, server_guid=None, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_server_report(self, server_guid=None, server_name=None, output_format='JSON', report_spec='OMAGServers', organization_name=None)`
  - **Planned**: TODO
- [ ] `_async_get_server_templates_by_dep_impl_type(self, filter_string, start_from=0, page_size=0, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: TODO
- [ ] `_async_get_servers_by_dep_impl_type(self, filter_string, start_from=0, page_size=0, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: TODO
- [x] `_async_get_servers_by_name(self, filter_string=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_integration_connector_config_properties(self, connector_name, server_guid=None, server_name=None, qualified_name=None, organization_name=None, output_format='JSON', report_spec='IntegrationConnector', body=None)`
  - **Planned**: TODO
- [x] `get_platform_by_guid(self, platform_guid, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_platform_report(self, platform_guid=None, platform_name=None, output_format='JSON', report_spec='Platform-Report')`
  - **Planned**: TODO
- [ ] `get_platform_templates_by_type(self, filter_string=None, effective_time=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: TODO
- [x] `get_platforms_by_name(self, filter_string=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_platforms_by_type(self, filter_string=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Platforms', body=None)`
  - **Planned**: TODO
- [x] `get_server_by_guid(self, server_guid=None, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_server_report(self, server_guid=None, server_name=None, output_format='JSON', report_spec='OMAGServers', organization_name=None)`
  - **Planned**: TODO
- [ ] `get_server_templates_by_dep_impl_type(self, filter_string, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: TODO
- [ ] `get_servers_by_dep_impl_type(self, search_string='*', effective_time=None, start_from=0, page_size=0, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: TODO
- [x] `get_servers_by_name(self, filter_string, start_from=0, page_size=0, output_format='JSON', report_spec='OMAGServers', body=None)`
  - **Planned**: Standard Get By Name Pattern

### schema_maker.py
- [x] `_async_find_schema_types(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_schema_type_by_guid(self, schema_type_guid, element_type='SchemaType', body=None, output_format='JSON', report_spec='SchemaTypes')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `find_schema_types(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_schema_type_by_guid(self, schema_type_guid, element_type='SchemaType', body=None, output_format='JSON', report_spec='SchemaTypes')`
  - **Planned**: Standard Get By GUID Pattern

### security_officer.py
- [x] `_async_find_security_groups(self, search_string, graph_query_depth=0, start_from=0, page_size=0)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_security_roles(self, search_string, graph_query_depth=0, start_from=0, page_size=0)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_security_access_control(self, platform_name, control_name, platform_guid=None)`
  - **Planned**: TODO
- [ ] `_async_get_user_account(self, platform_name, user_id, platform_guid=None)`
  - **Planned**: TODO
- [ ] `_async_get_user_list(self, platform_name, status=None, user_type=None, platform_guid=None)`
  - **Planned**: TODO
- [x] `find_security_groups(self, search_string, graph_query_depth=0, start_from=0, page_size=0)`
  - **Planned**: Standard Find Pattern
- [x] `find_security_roles(self, search_string, graph_query_depth=0, start_from=0, page_size=0)`
  - **Planned**: Standard Find Pattern
- [ ] `get_security_access_control(self, platform_name, control_name, platform_guid=None)`
  - **Planned**: TODO
- [ ] `get_user_account(self, platform_name, user_id, platform_guid=None)`
  - **Planned**: TODO
- [ ] `get_user_list(self, platform_name, status=None, user_type=None, platform_guid=None)`
  - **Planned**: TODO

### server_operations.py
- [ ] `_async_get_active_configuration(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_active_server_status(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_active_service_list_for_server(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_connector_config(self, connector_name, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_governance_engine_summaries(self, server=None)`
  - **Planned**: TODO
- [ ] `_async_get_integration_daemon_status(self, server=None)`
  - **Planned**: TODO
- [ ] `get_active_configuration(self, server=None)`
  - **Planned**: TODO
- [ ] `get_active_server_status(self, server=None)`
  - **Planned**: TODO
- [ ] `get_active_service_list_for_server(self, server=None)`
  - **Planned**: TODO
- [ ] `get_connector_config(self, connector_name, server=None)`
  - **Planned**: TODO
- [ ] `get_governance_engine_summaries(self, server=None)`
  - **Planned**: TODO
- [ ] `get_integration_connector_status(self, server=None)`
  - **Planned**: TODO
- [ ] `get_integration_daemon_status(self, server=None)`
  - **Planned**: TODO

### solution_architect.py
- [x] `_async_find_design_patterns(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_information_supply_chains(self, search_string='*', add_implementation=True, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_solution_blueprints(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Solution-Blueprint', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_solution_components(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_find_solution_roles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_design_pattern_by_guid(self, guid, body=None, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_design_patterns_by_name(self, name, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_info_supply_chain_by_guid(self, guid, body=None, add_implementation=True, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_info_supply_chain_by_name(self, search_filter, body=None, add_implementation=True, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_solution_blueprint_by_guid(self, guid, body=None, output_format='JSON', report_spec='Solution-Blueprint')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_solution_blueprints_by_name(self, search_filter, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Solution-Blueprint')`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_solution_component_by_guid(self, guid, body=None, output_format='JSON', report_spec='Solution-Component-DrE')`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `_async_get_solution_component_implementations(self, solution_component_guid, body=None, start_from=0, page_size=0, output_format='JSON')`
  - **Planned**: TODO
- [x] `_async_get_solution_components_by_name(self, search_filter, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `_async_get_solution_role_by_guid(self, guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_solution_roles_by_name(self, search_filter, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_all_information_supply_chains(self, add_implementation=True, starts_with=True, ends_with=False, ignore_case=False, anchor_domain=None, metadata_element_type=None, metadata_element_subtypes=None, skip_relationships=None, include_only_relationships=None, skip_classified_elements=None, include_only_classified_elements=None, graph_query_depth=3, governance_zone_filter=None, as_of_time=None, effective_time=None, relationship_page_size=0, limit_results_by_status=None, sequencing_order=None, sequencing_property=None, output_format='JSON', report_spec=None, start_from=0, page_size=100, property_names=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_all_solution_blueprints(self, classification_names=None, metadata_element_subtypes=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_all_solution_components(self, classification_names=None, metadata_element_subtypes=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_all_solution_roles(self, classification_names=None, metadata_element_subtypes=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=0, output_format='JSON', report_spec=None, body=None)`
  - **Planned**: Standard Find Pattern
- [x] `find_design_patterns(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_information_supply_chains(self, search_string='*', add_implementation=True, body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_solution_blueprints(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Solution-Blueprint', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_solution_components(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `find_solution_roles(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec=None, **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_component_related_elements(self, guid)`
  - **Planned**: TODO
- [x] `get_design_pattern_by_guid(self, guid, body=None, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_design_patterns_by_name(self, name, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Design-Pattern-DrE', **kwargs)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_info_supply_chain_by_guid(self, guid, body=None, add_implementation=True, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_info_supply_chain_by_name(self, search_filter, body=None, add_implementation=True, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_solution_blueprint_by_guid(self, guid, body=None, output_format='JSON', report_spec='Solution-Blueprint')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_solution_blueprints_by_name(self, search_filter, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec='Solution-Blueprint')`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_solution_component_by_guid(self, guid, body=None, output_format='JSON', report_spec='Solution-Component-DrE')`
  - **Planned**: Standard Get By GUID Pattern
- [ ] `get_solution_component_implementations(self, solution_component_guid, body=None, start_from=0, page_size=max_paging_size, output_format='JSON')`
  - **Planned**: TODO
- [x] `get_solution_components_by_name(self, search_filter, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [x] `get_solution_role_by_guid(self, guid, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_solution_roles_by_name(self, search_filter, body=None, start_from=0, page_size=max_paging_size, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern

### subject_area.py
- [x] `_async_find_subject_areas(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_subject_area_by_guid(self, subject_area_guid, element_type='SubjectArea', body=None, output_format='JSON', report_spec='SubjectAreas')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_subject_areas_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='SubjectAreas')`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_subject_areas(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_subject_area_by_guid(self, subject_area_guid, element_type='SubjectArea', body=None, output_format='JSON', report_spec='SubjectAreas')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_subject_areas_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='SubjectAreas')`
  - **Planned**: Standard Get By Name Pattern

### time_keeper.py
- [x] `_async_find_context_events(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `_async_get_context_event_by_guid(self, context_event_guid, element_type='ContextEvent', body=None, output_format='JSON', report_spec='ContextEvents')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_context_events_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='ContextEvents')`
  - **Planned**: Standard Get By Name Pattern
- [x] `find_context_events(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [x] `get_context_event_by_guid(self, context_event_guid, element_type='ContextEvent', body=None, output_format='JSON', report_spec='ContextEvents')`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_context_events_by_name(self, filter_string=None, classification_names=None, body=None, start_from=0, page_size=0, output_format='JSON', report_spec='ContextEvents')`
  - **Planned**: Standard Get By Name Pattern

### valid_metadata.py
- [x] `_async_find_specification_property(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `_async_get_all_classification_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_all_entity_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_all_entity_types(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_all_relationship_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_consistent_metadata_values(self, property_name, type_name, map_name, preferred_value, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_specification_property_by_guid(self, spec_property_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `_async_get_specification_property_by_name(self, name, start_from=0, page_size=0, category=None, classification_names=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_specification_property_by_type(self, spec_property_type, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_specification_property_types(self, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_sub_types(self, type_name, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `_async_get_typedef_by_name(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `_async_get_valid_classification_types(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_valid_metadata_map_name(self, property_name, type_name, map_name, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_valid_metadata_map_value(self, property_name, type_name, preferred_value, map_name, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_valid_metadata_value(self, property_name, type_name, preferred_value, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_valid_metadata_values(self, property_name, type_name=None, start_from=0, page_size=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `_async_get_valid_relationship_types(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `find_specification_property(self, search_string='*', body=None, starts_with=True, ends_with=False, ignore_case=False, start_from=0, page_size=100, output_format='JSON', report_spec='Referenceable', **kwargs)`
  - **Planned**: Standard Find Pattern
- [ ] `get_all_classification_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_all_entity_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_all_entity_types(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_all_relationship_defs(self, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_consistent_metadata_values(self, property_name, type_name, map_name, preferred_value, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_specification_property_by_guid(self, spec_property_guid, element_type=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By GUID Pattern
- [x] `get_specification_property_by_name(self, name, start_from=0, page_size=0, category=None, classification_names=None, body=None, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_specification_property_by_type(self, spec_property_type, body=None, start_from=0, page_size=0, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_specification_property_types(self, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_sub_types(self, type_name, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [x] `get_typedef_by_name(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: Standard Get By Name Pattern
- [ ] `get_valid_classification_types(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_valid_metadata_map_name(self, property_name, type_name, map_name, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_valid_metadata_map_value(self, property_name, type_name, preferred_value, map_name, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_valid_metadata_value(self, property_name, type_name, preferred_value, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_valid_metadata_values(self, property_name, type_name=None, start_from=0, page_size=None, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
- [ ] `get_valid_relationship_types(self, entity_type, get_inherited_attributes=False, get_relationship_attributes=False, output_format='JSON', report_spec=None)`
  - **Planned**: TODO
