# OMVS Audit Report

Ground truth: `pyegeria/http clients` (40 collections)
Subject: `pyegeria/omvs` (44 modules)

| Result | Count |
|---|---|
| OK | 708 |
| Mismatch (verb/path/body) | 7 |
| Missing | 36 |
| Renamed (implemented, verb+path matches under a different name) | 191 |
| Found in another module | 18 |
| URL lint | 0 |

## Duplicate endpoints (same verb + path)

_Review only - cross-service overlap is often intentional._

- `GET /my-profile`
  - `my-profile.py`: `_async_get_my_profile`
  - `my-profile.py`: `_async_get_my_profile_by_get`
- `GET /runtime-manager/engine-hosts/{}/governance-engines/refresh-config`
  - `runtime-manager.py`: `_async_refresh_gov_eng_config`
  - `runtime-manager.py`: `_async_refresh_gov_engine`
- `GET /valid-metadata/get-valid-metadata-values/{}`
  - `valid-metadata.py`: `_async_get_valid_metadata_values`
  - `feedback-manager.py`: `_async_get_valid_metadata_values`
- `POST /automated-curation/governance-action-types/initiate`
  - `automated-curation.py`: `_async_initiate_gov_action_type`
  - `automated-curation.py`: `_async_initiate_survey`
- `POST /classification-explorer/elements/by-exact-property-value`
  - `classification-explorer.py`: `_async_get_elements_by_property_value`
  - `feedback-manager.py`: `_async_get_elements_by_property_value`
- `POST /classification-explorer/elements/by-ownership`
  - `classification-explorer.py`: `_async_get_owners_elements`
  - `classification-explorer.py`: `_async_get_subject_area_members`
- `POST /classification-explorer/elements/{}`
  - `classification-explorer.py`: `_async_get_element_by_guid`
  - `feedback-manager.py`: `_async_get_element_by_guid_`
- `POST /classification-explorer/elements/{}/by-relationship/{}/with-exact-property-value`
  - `classification-explorer.py`: `_async_get_related_elements_with_property_value`
  - `feedback-manager.py`: `_async_get_related_elements_with_property_value`
- `POST /classification-explorer/elements/{}/search-keywords`
  - `classification-explorer.py`: `_async_add_search_keyword_to_element`
  - `feedback-manager.py`: `_async_add_search_keyword_to_element`
- `POST /classification-explorer/relationships/with-exact-property-value`
  - `classification-explorer.py`: `_async_get_relationships_with_property_value`
  - `feedback-manager.py`: `_async_get_relationships_with_property_value`
- `POST /classification-explorer/search-keywords/{}/remove`
  - `classification-explorer.py`: `_async_remove_search_keyword_from_element`
  - `feedback-manager.py`: `_async_remove_search_keyword`
- `POST /classification-explorer/search-keywords/{}/update`
  - `classification-explorer.py`: `_async_update_search_keyword`
  - `feedback-manager.py`: `_async_update_search_keyword`
- `POST /collection-manager/collections`
  - `collection-manager.py`: `_async_create_collection`
  - `collection-manager.py`: `_async_create_data_spec_collection`
  - `collection-manager.py`: `_async_create_report_type_collection`
  - `collection-manager.py`: `_async_create_question_spec_folder`
  - `collection-manager.py`: `_async_create_security_list`
  - `collection-manager.py`: `_async_create_data_dictionary_collection`
  - `collection-manager.py`: `_async_create_skill_set_collection`
  - `collection-manager.py`: `_async_create_reference_list_collection`
  - `collection-manager.py`: `_async_create_digital_product`
  - `collection-manager.py`: `_async_create_digital_product_catalog`
  - `collection-manager.py`: `_async_create_agreement`
  - `collection-manager.py`: `_async_create_digital_subscription`
- `POST /collection-manager/collections/{}/update`
  - `collection-manager.py`: `_async_update_collection`
  - `collection-manager.py`: `_async_update_digital_product`
  - `collection-manager.py`: `_async_update_agreement`
  - `collection-manager.py`: `_async_update_digital_subscription`
- `POST /data-designer/data-value-specifications`
  - `data-designer.py`: `_async_create_data_value_specification`
  - `data-designer.py`: `_async_create_data_grain`
  - `data-designer.py`: `_async_create_data_class`
- `POST /data-designer/data-value-specifications/{}/delete`
  - `data-designer.py`: `_async_delete_data_value_specification`
  - `data-designer.py`: `_async_delete_data_class`
- `POST /data-designer/data-value-specifications/{}/retrieve`
  - `data-designer.py`: `_async_get_data_value_specification_by_guid`
  - `data-designer.py`: `_async_get_data_class_by_guid`
- `POST /glossary-manager/glossaries/terms`
  - `glossary-manager.py`: `_async_create_glossary_term`
  - `glossary-manager.py`: `_async_create_question`
- `POST /governance-officer/governance-action-processes/{}/graph`
  - `action-author.py`: `_async_get_governance_action_process_graph`
  - `governance-officer.py`: `_async_get_governance_action_process_graph`
- `POST /governance-officer/governance-definitions`
  - `governance-officer.py`: `_async_create_governance_definition`
  - `governance-officer.py`: `_async_create_data_lens`
- `POST /governance-officer/governance-definitions/{}/retrieve`
  - `action-author.py`: `_async_get_governance_action_process`
  - `governance-officer.py`: `_async_get_governance_definition_by_guid`
  - `governance-officer.py`: `_async_get_governance_action_process`
- `POST /lineage-linker/from-elements/{}/via/{}/to-elements/{}/attach`
  - `lineage-linker.py`: `_async_link_lineage`
  - `lineage-linker.py`: `_async_link_data_flow`
- `POST /metadata-expert/metadata-elements/{}/history`
  - `metadata-expert.py`: `_async_get_element_history`
  - `metadata-expert.py`: `_async_get_metadata_element_history`
- `POST /metadata-expert/metadata-elements/{}/update-effectivity`
  - `metadata-expert.py`: `_async_update_metadata_element_effectivity`
  - `feedback-manager.py`: `_async_update_element_effectivity`
- `POST /metadata-expert/related-elements`
  - `collection-manager.py`: `_async_link_saved_query_to_results_set`
  - `metadata-expert.py`: `_async_create_related_elements`
- `POST /metadata-expert/related-elements/{}/delete`
  - `collection-manager.py`: `_async_detach_saved_query_from_results_set`
  - `metadata-expert.py`: `_async_delete_related_elements`
- `POST /platform-services/server-platform/servers/{}/instance`
  - `platform-services.py`: `_async_activate_server_stored_config`
  - `platform-services.py`: `_async_activate_server_supplied_config`
- `POST /product-manager/collections`
  - `product-manager.py`: `_async_create_digital_product`
  - `product-manager.py`: `_async_create_digital_product_catalog`
- `POST /product-manager/collections/by-name`
  - `product-manager.py`: `_async_get_digital_products_by_name`
  - `product-manager.py`: `_async_get_digital_product_catalogs_by_name`
- `POST /product-manager/collections/by-search-string`
  - `product-manager.py`: `_async_find_digital_products`
  - `product-manager.py`: `_async_find_digital_product_catalogs`
- `POST /product-manager/collections/{}/delete`
  - `product-manager.py`: `_async_delete_digital_product`
  - `product-manager.py`: `_async_delete_digital_product_catalog`
- `POST /product-manager/collections/{}/retrieve`
  - `product-manager.py`: `_async_get_digital_product_by_guid`
  - `product-manager.py`: `_async_get_digital_product_catalog_by_guid`
- `POST /product-manager/collections/{}/update`
  - `product-manager.py`: `_async_update_digital_product`
  - `product-manager.py`: `_async_update_digital_product_catalog`
- `POST /runtime-manager/omag-servers/{}/instance/load/open-metadata-archives/file`
  - `runtime-manager.py`: `_async_add_archive_file`
  - `feedback-manager.py`: `_async_add_archive_file`
- `POST /runtime-manager/platforms/by-deployed-implementation-type`
  - `runtime-manager.py`: `_async_get_platforms_by_type`
  - `runtime-manager.py`: `_async_get_platform_templates_by_type`
- `POST /runtime-manager/software-servers/by-deployed-implementation-type`
  - `runtime-manager.py`: `_async_get_servers_by_dep_impl_type`
  - `runtime-manager.py`: `_async_get_server_templates_by_dep_impl_type`
- `POST /security-officer/collections/by-search-string`
  - `security-officer.py`: `_async_find_security_roles`
  - `security-officer.py`: `_async_find_security_groups`
- `POST /solution-architect/solution-blueprints/{}/update`
  - `solution-architect.py`: `_async_update_solution_blueprint_status`
  - `solution-architect.py`: `_async_update_solution_blueprint`


### Service: action-author


### Service: actor-manager

- find All ContributionRecords: RENAMED -> `actor-manager.py`:`_async_find_contribution_records`
- updateActorRole: MISMATCH `update_actor_role`
    - PATH
      SDK: /actor-manager/actor-roles/{}/update
      API: /actor-manager/actor-roles/update
- Detach a team role from a team profile.: RENAMED -> `actor-manager.py`:`_async_detach_team_role_from_profile`
- linkITProfileRoleToProfile: RENAMED -> `actor-manager.py`:`_async_link_it_profile_role_to_it_profile`
- detachITProfileRoleFromProfile: RENAMED -> `actor-manager.py`:`_async_detach_it_profile_role_from_it_profile`
- deleteActorRole: MISMATCH `delete_actor_role`
    - PATH
      SDK: /actor-manager/actor-roles/{}/delete
      API: /actor-manager/actor-roles/delete
- getActorRoleByGUID: MISMATCH `get_actor_role_by_guid`
    - PATH
      SDK: /actor-manager/actor-roles/{}/retrieve
      API: /actor-manager/actor-roles/{}/retrieve"}
- detachProfileIdentity: RENAMED -> `actor-manager.py`:`_async_detach_identity_from_profile`
- removeAllSecurityGroupMembership: RENAMED -> `actor-manager.py`:`_async_remove_all_security_group_memberships`

### Service: asset-catalog


### Service: asset-maker

- unDeployITAsset: RENAMED -> `asset-maker.py`:`_async_undeploy_it_asset`
- linkSoftwareCapability: RENAMED -> `asset-maker.py`:`_async_link_software_capability_to_asset`
- detachSoftwareCapability: RENAMED -> `asset-maker.py`:`_async_detach_software_capability_from_asset`
- linkSupportedGovernanceService: MISSING  (`POST /asset-maker/governance-engines/{}/supported-governance-services/{}/attach`)
- updateSupportedGovernanceService: MISSING  (`POST /asset-maker/supported-governance-services/{}/update`)
- detachSupportedGovernanceService: MISSING  (`POST /asset-maker/supported-governance-services/{}/detach`)

### Service: automated-curation

- getTechnologyTypesForOpenMetadataType: RENAMED -> `automated-curation.py`:`_async_get_tech_types_for_open_metadata_type`
- getTechnologyTypeDetail: RENAMED -> `automated-curation.py`:`_async_get_tech_type_detail`
- getTechnologyTypeHierarchy: RENAMED -> `automated-curation.py`:`_async_get_tech_type_hierarchy`
- getTechnologyTypeTemplates: RENAMED -> `automated-curation.py`:`_async_get_technology_type_elements`
- createElementFromTemplate: ELSEWHERE -> `feedback-manager.py`
- getElementFromTemplate: RENAMED -> `automated-curation.py`:`_async_create_elem_from_template`
- createElementFromTemplate - Marquez endpoint: RENAMED -> `automated-curation.py`:`_async_create_elem_from_template`
- initiateGovernanceActionType: RENAMED -> `automated-curation.py`:`_async_initiate_gov_action_type`, `automated-curation.py`:`_async_initiate_survey`
- initiateGovernanceActionProcess: RENAMED -> `automated-curation.py`:`_async_initiate_gov_action_process`
- updateEngineActionStatus: MISSING  (`POST /automated-curation/engine-actions/{}/status/update`)
- claimEngineAction: MISSING  (`POST /automated-curation/engine-actions/{}/claim`)
- getActiveClaimedEngineActions: MISSING  (`GET /automated-curation/governance-engines/{}/engine-actions/active-claimed`)
- updateActionTargetStatus: MISSING  (`POST /automated-curation/engine-actions/action-targets/update`)
- recordCompletionStatus: MISSING  (`POST /automated-curation/engine-actions/{}/completion-status`)

### Service: classification-explorer

- getValidMetadataValues - severityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/severityLevel`)
- getValidMetadataValues - confidenceLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/confidenceLevel`)
- getValidMetadataValues - criticalityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/criticalityLevel`)
- getValidMetadataValues - confidentialityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/confidentialityLevel`)
- getValidMetadataValues - retentionBasis values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/retentionBasis`)
- addSecurityTags: RENAMED -> `classification-explorer.py`:`_async_set_security_tags_classification`
- clearSecurityTags: RENAMED -> `classification-explorer.py`:`_async_clear_security_tags_classification`
- addAccountingCodes: RENAMED -> `classification-explorer.py`:`_async_set_accounting_codes_classification`
- clearAccountingCodes: RENAMED -> `classification-explorer.py`:`_async_clear_accounting_codes_classification`
- addOwnership: RENAMED -> `classification-explorer.py`:`_async_add_ownership_to_element`
- clearOwnership: RENAMED -> `classification-explorer.py`:`_async_clear_ownership_from_element`
- clearDigitalResourceOrigin: RENAMED -> `classification-explorer.py`:`_async_clear_digital_resource_origin_from_element`
- setupPeerDuplicates: RENAMED -> `classification-explorer.py`:`_async_link_elements_as_peer_duplicates`
- clearSemanticAssignment: RENAMED -> `classification-explorer.py`:`_async_clear_semantic_assignment_classification`
- addGovernanceDefinitionToElement: RENAMED -> `classification-explorer.py`:`_async_add_gov_definition_to_element`
- removeGovernanceDefinitionFromElement: RENAMED -> `classification-explorer.py`:`_async_remove_gov_definition_from_element`
- addGovernanceExpectations: RENAMED -> `classification-explorer.py`:`_async_set_governance_expectation`
- updateGovernanceExpectations: RENAMED -> `classification-explorer.py`:`_async_update_governance_expectation`
- clearGovernanceExpectations: RENAMED -> `classification-explorer.py`:`_async_clear_governance_expectation`
- addResourceListToElement: RENAMED -> `classification-explorer.py`:`_async_add_resource_to_element`
- removeResourceListFromElement: RENAMED -> `classification-explorer.py`:`_async_remove_resource_from_element`
- addMoreInformationToElement: RENAMED -> `classification-explorer.py`:`_async_add_more_information`
- removeMoreInformationFromElement: RENAMED -> `classification-explorer.py`:`_async_remove_more_information`
- removeScopeFromElement: RENAMED -> `classification-explorer.py`:`_async_clear_scope_from_element`
- licenseElement: ELSEWHERE -> `governance-officer.py`
- certifyElement: ELSEWHERE -> `governance-officer.py`
- getSearchKeywordByGUID: ELSEWHERE -> `feedback-manager.py`
- getSearchKeywordsByKeyword: RENAMED -> `feedback-manager.py`:`_async_get_search_keyword_by_keyword`
- findSearchKeywords: ELSEWHERE -> `feedback-manager.py`
- getRootElementByGUID: RENAMED -> `classification-explorer.py`:`_async_get_element_by_guid`, `feedback-manager.py`:`_async_get_element_by_guid_`
- getRootElementByUniqueName: RENAMED -> `classification-explorer.py`:`_async_get_element_by_unique_name`
- getMetadataElementGUIDByUniqueName: ELSEWHERE -> `metadata-expert.py`
- getRootElementsByType: RENAMED -> `classification-explorer.py`:`_async_get_elements`
- getRootElementsByPropertyValue: RENAMED -> `classification-explorer.py`:`_async_get_elements_by_property_value`, `feedback-manager.py`:`_async_get_elements_by_property_value`
- findRootElementsByPropertyValue: RENAMED -> `classification-explorer.py`:`_async_find_elements_by_property_value`
- findRootAuthoredElements: RENAMED -> `classification-explorer.py`:`_async_find_authored_elements`
- getRootAuthoredElementsByCategory: RENAMED -> `classification-explorer.py`:`_async_find_authored_elements_by_category`
- getRootElementsByClassification: RENAMED -> `classification-explorer.py`:`_async_get_elements_by_classification`
- getRootElementsByClassificationWithPropertyValue: RENAMED -> `classification-explorer.py`:`_async_get_elements_by_classification_with_property_value`
- findRootElementsByClassificationWithPropertyValue: RENAMED -> `classification-explorer.py`:`_async_find_elements_by_classification_with_property_value`
- getRelatedRootElements: RENAMED -> `classification-explorer.py`:`_async_get_related_elements`
- getRelatedRootElementsWithPropertyValue: RENAMED -> `classification-explorer.py`:`_async_get_related_elements_with_property_value`, `feedback-manager.py`:`_async_get_related_elements_with_property_value`
- findRelatedRootElementsWithPropertyValue: RENAMED -> `classification-explorer.py`:`_async_find_related_elements_with_property_value`
- getRelationshipByGUID: ELSEWHERE -> `metadata-expert.py`

### Service: collection-manager

- createGlossary: ELSEWHERE -> `glossary-manager.py`
- createDataSharingAgreementCollection: RENAMED -> `collection-manager.py`:`_async_create_collection`, `collection-manager.py`:`_async_create_data_spec_collection`, `collection-manager.py`:`_async_create_report_type_collection`, `collection-manager.py`:`_async_create_question_spec_folder`, `collection-manager.py`:`_async_create_security_list`, `collection-manager.py`:`_async_create_data_dictionary_collection`, `collection-manager.py`:`_async_create_skill_set_collection`, `collection-manager.py`:`_async_create_reference_list_collection`, `collection-manager.py`:`_async_create_digital_product`, `collection-manager.py`:`_async_create_digital_product_catalog`, `collection-manager.py`:`_async_create_agreement`, `collection-manager.py`:`_async_create_digital_subscription`
- updateAgreementStatus: RENAMED -> `collection-manager.py`:`_async_update_collection`, `collection-manager.py`:`_async_update_digital_product`, `collection-manager.py`:`_async_update_agreement`, `collection-manager.py`:`_async_update_digital_subscription`
- updateDigitalSubscriptionStatus: RENAMED -> `collection-manager.py`:`_async_update_collection`, `collection-manager.py`:`_async_update_digital_product`, `collection-manager.py`:`_async_update_agreement`, `collection-manager.py`:`_async_update_digital_subscription`
- detachDataDescription: MISSING  (`POST /collection-manager/metadata-elements/{}/data-descriptions/{}/detach`)
- attachSmartQuery: MISSING  (`POST /collection-manager/collections/results-sets/{}/smart-query/{}/attach`)
- detachSmartQuery: MISSING  (`POST /collection-manager/collections/results-sets/{}/smart-query/{}/detach`)
- attachAssociatedSkillSet: RENAMED -> `collection-manager.py`:`_async_link_associated_skill_set`
- updateCollectionMembership: RENAMED -> `collection-manager.py`:`_async_update_collection_membership_prop`

### Service: community-matters


### Service: connection-maker


### Service: data-designer

- findAllDataStructures - with full request body: RENAMED -> `data-designer.py`:`_async_find_data_structures`
- findDataStructures - with full request body: RENAMED -> `data-designer.py`:`_async_find_data_structures`
- getDataStructuresByName - with full request body: RENAMED -> `data-designer.py`:`_async_get_data_structures_by_name`
- getDataStructureByGUID - with request body: RENAMED -> `data-designer.py`:`_async_get_data_structure_by_guid`
- linkNestedDataFields: RENAMED -> `data-designer.py`:`_async_link_nested_data_field`
- detachNestedDataFields: RENAMED -> `data-designer.py`:`_async_detach_nested_data_field`
- findAllDataFields - with full request body: RENAMED -> `data-designer.py`:`_async_find_data_fields`
- findDataFields - with full request body: RENAMED -> `data-designer.py`:`_async_find_data_fields`
- getDataFieldsByName - with full request body: RENAMED -> `data-designer.py`:`_async_get_data_fields_by_name`
- getDataFieldByGUID - with request body: RENAMED -> `data-designer.py`:`_async_get_data_field_by_guid`
- createDataValueSpecificationFromTemplate: MISSING  (`POST /data-designer/data-value-specifications/from-template`)
- assignDataValueSpecification: RENAMED -> `data-designer.py`:`_async_link_data_value_assignment`
- detachDataValueSpecificationAssignment: MISSING  (`POST /data-designer/elements/{}/data-value-specifications/{}/detach`)
- findAllDataClasses: RENAMED -> `data-designer.py`:`_async_find_data_value_specifications`
- findAllDataGrains: RENAMED -> `data-designer.py`:`_async_find_data_value_specifications`
- findDataValueSpecifications - with full request body: RENAMED -> `data-designer.py`:`_async_find_data_value_specifications`
- linkDataValueSpecificationDefinition: RENAMED -> `data-designer.py`:`_async_link_data_class_definition`
- detachDataValueSpecificationDefinition: RENAMED -> `data-designer.py`:`_async_detach_data_class_definition`
- detachCertificationTypeToDataStructure: MISSING  (`POST /data-designer/certification-types/{}/data-structure-definition/{}/detach`)

### Service: data-discovery


### Service: data-engineer

- getTabularDataSetReport: RENAMED -> `data-engineer.py`:`_async_get_tabular_data_set`

### Service: digital-business


### Service: external-links

- linkCitedDocumentReference: RENAMED -> `external-links.py`:`_async_link_cited_document`
- detachCitedDocumentReference: RENAMED -> `external-links.py`:`_async_detach_cited_document`

### Service: feedback-manager

- getTag: RENAMED -> `feedback-manager.py`:`_async_get_tag_by_guid`
- getNoteLogsForElement: RENAMED -> `feedback-manager.py`:`_async_get_attached_note_logs`

### Service: glossary-manager

- getTermRelationshipTypeNames: RENAMED -> `glossary-manager.py`:`_async_get_term_relationship_types`

### Service: governance-officer

- getValidMetadataValues - domainIdentifier values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/domainIdentifier`)
- createRegulation: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- removeRegulatorFromRegulation: RENAMED -> `governance-officer.py`:`_async_detach_regulator_from_regulation`
- createGovernanceControl: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- createSecurityAccessControl: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- createNamingStandardRule: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- createCertificationType: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- createLicenseType: RENAMED -> `governance-officer.py`:`_async_create_governance_definition`, `governance-officer.py`:`_async_create_data_lens`
- updateGovernanceDefinitionStatus: RENAMED -> `governance-officer.py`:`_async_update_governance_definition`
- attachSupportingDefinition: RENAMED -> `governance-officer.py`:`_async_attach_supporting_definitions`
- detachSupportingDefinition: RENAMED -> `governance-officer.py`:`_async_detach_supporting_definitions`
- findAllGovernanceDefinitions: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- findAllGovernanceDefinitions - with full request body: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- findGovernanceDefinitions - with full request body: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- getGovernanceDefinitionsByName - with full request body: RENAMED -> `governance-officer.py`:`_async_get_governance_definitions_by_name`
- getGovernanceDefinitionByGUID - with request body: RENAMED -> `action-author.py`:`_async_get_governance_action_process`, `governance-officer.py`:`_async_get_governance_definition_by_guid`, `governance-officer.py`:`_async_get_governance_action_process`
- getAllGovernanceActionTypes: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- findGovernanceActionTypes: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- getGovernanceActionTypesByName: RENAMED -> `governance-officer.py`:`_async_get_governance_definitions_by_name`
- getGovernanceActionTypeByGUID: RENAMED -> `action-author.py`:`_async_get_governance_action_process`, `governance-officer.py`:`_async_get_governance_definition_by_guid`, `governance-officer.py`:`_async_get_governance_action_process`
- findGovernanceActionProcesses: MISSING  (`POST /governance-officer/governance-action-processes/by-search-string`)
- getAllGovernanceActionProcesses: RENAMED -> `governance-officer.py`:`_async_find_governance_definitions`
- getGovernanceActionProcessesByName: RENAMED -> `governance-officer.py`:`_async_get_governance_definitions_by_name`
- addGovernanceDefinitionToElement: RENAMED -> `governance-officer.py`:`_async_attach_governed_by_definition`
- removeGovernanceDefinitionFromElement: RENAMED -> `governance-officer.py`:`_async_detach_governed_by_definition`
- linkApprovedPurpose: MISSING  (`POST /governance-officer/elements/{}/approved-purposes/{}/attach`)
- detachApprovedPurpose: MISSING  (`POST /governance-officer/elements/{}/approved-purposes/{}/detach`)
- updateLicense: ELSEWHERE -> `classification-explorer.py`
- unlicenseElement: ELSEWHERE -> `classification-explorer.py`
- updateCertification: ELSEWHERE -> `classification-explorer.py`
- decertifyElement: ELSEWHERE -> `classification-explorer.py`

### Service: lineage-linker


### Service: location-arena

- linkPeerLocation: RENAMED -> `location-arena.py`:`_async_link_peer_locations`

### Service: metadata-expert

- createMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_create_metadata_element`
- updateMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_update_metadata_element_properties`
- updateMetadataElementEffectivityInStore: RENAMED -> `metadata-expert.py`:`_async_update_metadata_element_effectivity`, `feedback-manager.py`:`_async_update_element_effectivity`
- deleteMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_delete_metadata_element`
- archiveMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_archive_metadata_element`
- reclassifyMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_reclassify_metadata_element`
- updateClassificationEffectivityInStore: RENAMED -> `metadata-expert.py`:`_async_update_classification_effectivity`
- declassifyMetadataElementInStore: RENAMED -> `metadata-expert.py`:`_async_declassify_metadata_element`
- createRelatedElementsInStore: RENAMED -> `collection-manager.py`:`_async_link_saved_query_to_results_set`, `metadata-expert.py`:`_async_create_related_elements`
- updateRelatedElementsInStore: RENAMED -> `metadata-expert.py`:`_async_update_related_elements_properties`
- updateRelatedElementsEffectivityInStore: RENAMED -> `metadata-expert.py`:`_async_update_related_elements_effectivity`
- deleteRelatedElementsInStore: RENAMED -> `collection-manager.py`:`_async_detach_saved_query_from_results_set`, `metadata-expert.py`:`_async_delete_related_elements`
- getAnchoredElementsGraph: RENAMED -> `metadata-expert.py`:`_async_get_anchored_element_graph`
- getAllRelatedMetadataElements: RENAMED -> `metadata-expert.py`:`_async_get_all_related_elements`
- findRelationshipsBetweenMetadataElements: RENAMED -> `metadata-expert.py`:`_async_find_relationships_between_elements`
- countRelationshipsBetweenMetadataElements: RENAMED -> `metadata-expert.py`:`_async_count_relationships_between_elements`

### Service: my-profile

- Get My Profile: MISSING  (`POST /my-profile`)
- Add My Profile: RENAMED -> `my-profile.py`:`_async_add_my_profile`

### Service: notification-manager


### Service: people-organizer


### Service: platform-services

- Get OMAG Server Platform Origin: MISSING  (`GET /platform-services/server-platform/origin`)
- Get Active User List: RENAMED -> `platform-services.py`:`_async_get_security_user_list`
- Get Contractor User List: RENAMED -> `platform-services.py`:`_async_get_security_user_list`
- Get all known servers: RENAMED -> `platform-services.py`:`_async_get_known_servers`
- Query the status of a specific server: ELSEWHERE -> `server-operations.py`
- Query a connector: MISSING  (`GET /platform-services/server-platform/connector-types/org.odpi.openmetadata.metadatasecurity.accessconnector.OpenMetadataAccessSecurityProvider`)
- Shutdown and unregister server from cohorts: MISSING  (`DELETE /platform-services/server-platform/servers/{}`)
- Shutdown all active servers: RENAMED -> `platform-services.py`:`_async_shutdown_all_servers`
- Shutdown and unregister all active servers: RENAMED -> `platform-services.py`:`_async_shutdown_unregister_servers`
- Shutdown server platform: RENAMED -> `platform-services.py`:`_async_shutdown_platform`

### Service: privacy-officer


### Service: product-catalog

- find DigitalProductCatalogs: MISSING  (`POST /product-catalog/collections/by-search-string`)
- find the open metadata product catalog: MISSING  (`POST /product-catalog/collections/by-search-string`)
- find the valid metadata value list digital product: MISSING  (`POST /product-catalog/collections/by-search-string`)
- getSolutionBlueprintsByName: ELSEWHERE -> `solution-architect.py`
- getTechnologyTypeDetail: RENAMED -> `automated-curation.py`:`_async_get_tech_type_detail`
- getTechnologyTypeTemplates: RENAMED -> `automated-curation.py`:`_async_get_technology_type_elements`
- createElementFromTemplate: ELSEWHERE -> `feedback-manager.py`
- getGovernanceActionProcessesByName: MISSING  (`POST /product-catalog/governance-definitions/by-name`)
- getGovernanceActionProcessGraph: ELSEWHERE -> `governance-officer.py`
- initiateGovernanceActionProcess: RENAMED -> `automated-curation.py`:`_async_initiate_gov_action_process`
- findSubscriptions: RENAMED -> `collection-manager.py`:`_async_find_collections`
- Get My Profile: MISSING  (`POST /my-profile`)
- getCommunitiesByName: ELSEWHERE -> `community-matters.py`
- getNoteLogsByName: ELSEWHERE -> `feedback-manager.py`

### Service: product-manager

- updateDigitalProductStatus: RENAMED -> `product-manager.py`:`_async_update_digital_product`, `product-manager.py`:`_async_update_digital_product_catalog`

### Service: project-manager

- createClassifiedProject: RENAMED -> `project-manager.py`:`_async_create_project`
- createCampaign: RENAMED -> `project-manager.py`:`_async_create_project`
- createTaskForProject: MISSING  (`POST /project-manager/projects/{}/task`)
- setupProjectDependency: RENAMED -> `project-manager.py`:`_async_set_project_dependency`
- setupProjectHierarchy: RENAMED -> `project-manager.py`:`_async_set_project_hierarchy`

### Service: reference-data


### Service: runtime-manager

- getPlatformsByDeployedImplementationType: RENAMED -> `runtime-manager.py`:`_async_get_platforms_by_type`, `runtime-manager.py`:`_async_get_platform_templates_by_type`
- getPlatformTemplatesByDeployedImplementationType: RENAMED -> `runtime-manager.py`:`_async_get_platforms_by_type`, `runtime-manager.py`:`_async_get_platform_templates_by_type`
- Get Connector Type: RENAMED -> `runtime-manager.py`:`_async_get_connector_type`
- getOMAGServerReport: RENAMED -> `runtime-manager.py`:`_async_get_server_report`
- activateWithStoredConfig: RENAMED -> `runtime-manager.py`:`_async_activate_server_with_stored_config`
- getConfigurationProperties: RENAMED -> `runtime-manager.py`:`_async_get_integration_connector_config_properties`
- updateConfigurationProperties: RENAMED -> `runtime-manager.py`:`_async_update_connector_configuration`
- updateEndpointNetworkAddress: RENAMED -> `runtime-manager.py`:`_async_update_endpoint_address`
- refreshConnectors: RENAMED -> `runtime-manager.py`:`_async_refresh_integration_connector`
- restartConnectors: RENAMED -> `runtime-manager.py`:`_async_restart_connector`
- refreshIntegrationGroupConfig: RENAMED -> `runtime-manager.py`:`_async_refresh_integ_group_config`
- refreshConfig: RENAMED -> `runtime-manager.py`:`_async_refresh_gov_eng_config`, `runtime-manager.py`:`_async_refresh_gov_engine`
- addOpenMetadataArchiveFile: RENAMED -> `runtime-manager.py`:`_async_add_archive_file`, `feedback-manager.py`:`_async_add_archive_file`
- addOpenMetadataArchiveContent: RENAMED -> `runtime-manager.py`:`_async_add_archive_content`

### Service: schema-maker

- updateSchemaAttribute: MISMATCH `update_schema_attribute`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/update
      API: /schema-maker/schema-attributes/update
- deleteSchemaAttribute: MISMATCH `delete_schema_attribute`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/delete
      API: /schema-maker/schema-attributes/delete
- getSchemaAttributeByGUID: MISMATCH `get_schema_attribute_by_guid`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/retrieve
      API: /schema-maker/schema-attributes/{}/retrieve"}

### Service: security-officer

- find Security Roles: RENAMED -> `security-officer.py`:`_async_find_security_roles`, `security-officer.py`:`_async_find_security_groups`
- find Security Groups: RENAMED -> `security-officer.py`:`_async_find_security_roles`, `security-officer.py`:`_async_find_security_groups`

### Service: solution-architect

- createInformationSupplyChain: RENAMED -> `solution-architect.py`:`_async_create_info_supply_chain`
- createInformationSupplyChainFromTemplate: RENAMED -> `solution-architect.py`:`_async_create_info_supply_chain_from_template`
- updateInformationSupplyChain: RENAMED -> `solution-architect.py`:`_async_update_info_supply_chain`
- linkPeersInInformationSupplyChain: RENAMED -> `solution-architect.py`:`_async_link_peer_info_supply_chains`
- unlinkPeerInformationSupplyChains: RENAMED -> `solution-architect.py`:`_async_unlink_peer_info_supply_chains`
- deleteInformationSupplyChain: RENAMED -> `solution-architect.py`:`_async_delete_info_supply_chain`
- findAllInformationSupplyChains - with full request body: RENAMED -> `solution-architect.py`:`_async_find_information_supply_chains`
- findInformationSupplyChains - with full request body: RENAMED -> `solution-architect.py`:`_async_find_information_supply_chains`
- getInformationSupplyChainsByName: RENAMED -> `solution-architect.py`:`_async_get_info_supply_chain_by_name`
- getInformationSupplyChainsByName - with full request body: RENAMED -> `solution-architect.py`:`_async_get_info_supply_chain_by_name`
- getInformationSupplyChainByGUID: RENAMED -> `solution-architect.py`:`_async_get_info_supply_chain_by_guid`
- getInformationSupplyChainByGUID - with request body: RENAMED -> `solution-architect.py`:`_async_get_info_supply_chain_by_guid`
- findAllSolutionBlueprints - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_blueprints`
- findSolutionBlueprints - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_blueprints`
- getSolutionBlueprintsByName - with full request body: RENAMED -> `solution-architect.py`:`_async_get_solution_blueprints_by_name`
- getSolutionBlueprintByGUID - with request body: RENAMED -> `solution-architect.py`:`_async_get_solution_blueprint_by_guid`
- linkSolutionComponentActor: RENAMED -> `solution-architect.py`:`_async_link_component_to_actor`
- detachSolutionComponentActor: MISSING  (`POST /solution-architect/solution-roles/{}/solution-component-actors/{}/detach`)
- findAllSolutionRoles - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_roles`
- findSolutionRoles - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_roles`
- getSolutionRolesByName - with full request body: RENAMED -> `solution-architect.py`:`_async_get_solution_roles_by_name`
- getSolutionRoleByGUID - with request body: RENAMED -> `solution-architect.py`:`_async_get_solution_role_by_guid`
- detachSubcomponent: RENAMED -> `solution-architect.py`:`_async_detach_sub_component`
- detachAllSolutionLinkingWire: RENAMED -> `solution-architect.py`:`_async_detach_solution_linking_wire`
- detachSolutionLinkingWire: MISMATCH `detach_solution_linking_wire`
    - PATH
      SDK: /solution-architect/solution-components/{}/wired-to/{}/detach
      API: /solution-architect/solution-components/wires/{}/detach
- findAllSolutionComponents - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_components`
- findSolutionComponents - with full request body: RENAMED -> `solution-architect.py`:`_async_find_solution_components`
- getSolutionComponentsByName - with full request body: RENAMED -> `solution-architect.py`:`_async_get_solution_components_by_name`
- getSolutionComponentByGUID - with request body: RENAMED -> `solution-architect.py`:`_async_get_solution_component_by_guid`

### Service: subject-area

- linkSubjectAreas: RENAMED -> `subject-area.py`:`_async_link_subject_area_hierarchy`
- detachSubjectAreas: RENAMED -> `subject-area.py`:`_async_detach_subject_area_hierarchy`
- findAllSubjectAreas: MISSING  (`POST /subject-area/collectionss/by-search-string`)
- findAllSubjectAreas - with full request body: RENAMED -> `subject-area.py`:`_async_find_subject_areas`
- findSubjectAreas - with full request body: RENAMED -> `subject-area.py`:`_async_find_subject_areas`
- getSubjectAreasByName - with full request body: RENAMED -> `subject-area.py`:`_async_get_subject_areas_by_name`
- getSubjectAreaByGUID - with request body: RENAMED -> `subject-area.py`:`_async_get_subject_area_by_guid`

### Service: template-manager


### Service: time-keeper


### Service: valid-metadata

- setUpValidMetadataValue: RENAMED -> `valid-metadata.py`:`_async_setup_valid_metadata_value`
- setUpValidMetadataMapName: RENAMED -> `valid-metadata.py`:`_async_setup_valid_metadata_map_name`
- setUpValidMetadataMapValue: RENAMED -> `valid-metadata.py`:`_async_setup_valid_metadata_map_value`
- getAllTypes: RENAMED -> `valid-metadata.py`:`_async_get_all_entity_types`
- getEntityDefs: RENAMED -> `valid-metadata.py`:`_async_get_all_entity_defs`
- getRelationshipDefs: RENAMED -> `valid-metadata.py`:`_async_get_all_relationship_defs`
- getClassificationDefs: RENAMED -> `valid-metadata.py`:`_async_get_all_classification_defs`
- getAttributeTypes: MISSING  (`GET /valid-metadata/open-metadata-types/attribute-defs`)
- getTypeDefByName: RENAMED -> `valid-metadata.py`:`_async_get_typedef_by_name`
- setUpSpecificationProperty: RENAMED -> `valid-metadata.py`:`_async_setup_specification_property`
