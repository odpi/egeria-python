# OMVS Audit Report

Ground truth: `pyegeria/http clients` (40 collections)
Subject: `pyegeria/omvs` (43 modules)

| Result | Count |
|---|---|
| OK | 557 |
| Mismatch (verb/path/body) | 102 |
| Missing | 288 |
| Found in another module | 13 |
| URL lint | 0 |

## Duplicate endpoints (same verb + path)

_Review only - cross-service overlap is often intentional._

- `POST /automated-curation/governance-action-types/initiate`
  - `automated-curation.py`: `_async_initiate_gov_action_type`
  - `automated-curation.py`: `_async_initiate_survey`
- `POST /classification-explorer/elements/by-ownership`
  - `classification-explorer.py`: `_async_get_owners_elements`
  - `classification-explorer.py`: `_async_get_subject_area_members`
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
- `POST /governance-officer/governance-definitions/{}/retrieve`
  - `action-author.py`: `_async_get_governance_action_process`
  - `governance-officer.py`: `_async_get_governance_action_process`
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
- `POST /runtime-manager/platforms/by-deployed-implementation-type`
  - `runtime-manager.py`: `_async_get_platforms_by_type`
  - `runtime-manager.py`: `_async_get_platform_templates_by_type`
- `POST /runtime-manager/software-servers/by-deployed-implementation-type`
  - `runtime-manager.py`: `_async_get_servers_by_dep_impl_type`
  - `runtime-manager.py`: `_async_get_server_templates_by_dep_impl_type`
- `POST /solution-architect/solution-blueprints/{}/update`
  - `solution-architect.py`: `_async_update_solution_blueprint_status`
  - `solution-architect.py`: `_async_update_solution_blueprint`
- `POST /{}/collections/by-search-string`
  - `security-officer.py`: `_async_find_security_roles`
  - `security-officer.py`: `_async_find_security_groups`
- `POST /{}/governance-definitions`
  - `governance-officer.py`: `_async_create_governance_definition`
  - `governance-officer.py`: `_async_create_data_lens`


### Service: action-author


### Service: actor-manager

- find All ContributionRecords: MISSING  (`POST /actor-manager/contribution-records/by-search-string`)
- updateActorRole: MISMATCH `update_actor_role`
    - PATH
      SDK: /actor-manager/actor-roles/{}/update
      API: /actor-manager/actor-roles/update
- Detach a team role from a team profile.: MISSING  (`POST /actor-manager/actor-roles/{}/team-role-appointments/{}/detach`)
- linkITProfileRoleToProfile: MISSING  (`POST /actor-manager/actor-roles/{}/it-profile-role-appointments/{}/attach`)
- detachITProfileRoleFromProfile: MISSING  (`POST /actor-manager/actor-roles/{}/it-profile-role-appointments/{}/detach`)
- deleteActorRole: MISMATCH `delete_actor_role`
    - PATH
      SDK: /actor-manager/actor-roles/{}/delete
      API: /actor-manager/actor-roles/delete
    - BODY DeleteElementRequestBody != DeleteRelationshipRequestBody
- getActorRoleByGUID: MISMATCH `get_actor_role_by_guid`
    - PATH
      SDK: /actor-manager/actor-roles/{}/retrieve
      API: /actor-manager/actor-roles/{}/retrieve"}
- detachProfileIdentity: MISSING  (`POST /actor-manager/user-identities/{}/profile-identity/{}/detach`)
- addSecurityGroupMembership: MISMATCH `add_security_group_membership`
    - PATH
      SDK: /actor-manager/user-identities/{}/security-group-membership/classify
      API: /actor-manager/user-identities/{}/security-group-memberships/classify
- updateSecurityGroupMembership: MISMATCH `update_security_group_membership`
    - PATH
      SDK: /actor-manager/user-identities/{}/security-group-membership/reclassify
      API: /actor-manager/user-identities/{}/security-group-memberships/reclassify
- removeAllSecurityGroupMembership: MISSING  (`POST /actor-manager/user-identities/{}/security-group-memberships/declassify`)

### Service: asset-catalog


### Service: asset-maker

- unDeployITAsset: MISSING  (`POST /asset-maker/assets/{}/deployed-on/{}/detach`)
- linkSoftwareCapability: MISSING  (`POST /asset-maker/assets/{}/supported-software-capabilities/{}/attach`)
- detachSoftwareCapability: MISSING  (`POST /asset-maker/assets/{}/supported-software-capabilities/{}/detach`)
- linkSupportedGovernanceService: MISSING  (`POST /asset-maker/governance-engines/{}/supported-governance-services/{}/attach`)
- updateSupportedGovernanceService: MISSING  (`POST /asset-maker/supported-governance-services/{}/update`)
- detachSupportedGovernanceService: MISSING  (`POST /asset-maker/supported-governance-services/{}/detach`)

### Service: automated-curation

- getTechnologyTypesForOpenMetadataType: MISSING  (`POST /automated-curation/open-metadata-types/{}/technology-types`)
- getTechnologyTypeDetail: MISSING  (`POST /automated-curation/technology-types/by-name`)
- getTechnologyTypeHierarchy: MISSING  (`POST /automated-curation/technology-types/hierarchy`)
- getTechnologyTypeTemplates: MISSING  (`POST /automated-curation/technology-types/elements`)
- createElementFromTemplate: MISSING  (`POST /automated-curation/catalog-templates/new-element`)
- getElementFromTemplate: MISSING  (`POST /automated-curation/catalog-templates/new-element`)
- createElementFromTemplate - Marquez endpoint: MISSING  (`POST /automated-curation/catalog-templates/new-element`)
- initiateGovernanceActionType: MISSING  (`POST /automated-curation/governance-action-types/initiate`)
- initiateGovernanceActionProcess: MISSING  (`POST /automated-curation/governance-action-processes/initiate`)
- updateEngineActionStatus: MISSING  (`POST /automated-curation/engine-actions/{}/status/update`)
- claimEngineAction: MISSING  (`POST /automated-curation/engine-actions/{}/claim`)
- getActiveClaimedEngineActions: MISSING  (`GET /automated-curation/governance-engines/{}/engine-actions/active-claimed`)
- updateActionTargetStatus: MISSING  (`POST /automated-curation/engine-actions/action-targets/update`)
- recordCompletionStatus: MISSING  (`POST /automated-curation/engine-actions/{}/completion-status`)

### Service: classification-explorer

- getValidMetadataValues - severityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/severityLevel`)
- getImpactClassifiedElements: MISSING  (`POST /classification-explorer/elements/by-impact`)
- getValidMetadataValues - confidenceLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/confidenceLevel`)
- getConfidenceClassifiedElements: MISSING  (`POST /classification-explorer/elements/by-confidence`)
- getValidMetadataValues - criticalityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/criticalityLevel`)
- getCriticalityClassifiedElements: MISSING  (`POST /classification-explorer/elements/by-criticality`)
- getValidMetadataValues - confidentialityLevel values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/confidentialityLevel`)
- getConfidentialityClassifiedElements: MISSING  (`POST /classification-explorer/elements/by-confidentiality`)
- getValidMetadataValues - retentionBasis values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/retentionBasis`)
- getRetentionClassifiedElements: MISSING  (`POST /classification-explorer/elements/by-retention`)
- addSecurityTags: MISSING  (`POST /classification-explorer/elements/{}/security-tags`)
- clearSecurityTags: MISSING  (`POST /classification-explorer/elements/{}/security-tags/remove`)
- addAccountingCodes: MISSING  (`POST /classification-explorer/elements/{}/accounting-codes`)
- clearAccountingCodes: MISSING  (`POST /classification-explorer/elements/{}/accounting-codes/remove`)
- addOwnership: MISSING  (`POST /classification-explorer/elements/{}/ownership`)
- clearOwnership: MISSING  (`POST /classification-explorer/elements/{}/ownership/remove`)
- clearDigitalResourceOrigin: MISSING  (`POST /classification-explorer/elements/{}/digital-resource-origin/remove`)
- setupPeerDuplicates: MISSING  (`POST /classification-explorer/related-elements/{}/peer-duplicate/{}/attach`)
- clearSemanticAssignment: MISSING  (`POST /classification-explorer/elements/{}/semantic-assignment/terms/{}/detach`)
- getSemanticAssignees: MISMATCH `get_semantic_assignees`
    - PATH
      SDK: /classification-explorer/glossaries/elements/by-semantic-assignment/{}
      API: /classification-explorer/elements/by-semantic-assignment/{}
- addGovernanceDefinitionToElement: MISSING  (`POST /classification-explorer/elements/{}/governed-by/definition/{}/attach`)
- removeGovernanceDefinitionFromElement: MISSING  (`POST /classification-explorer/elements/{}/governed-by/definition/{}/detach`)
- addGovernanceExpectations: MISSING  (`POST /classification-explorer/elements/{}/governance-expectations`)
- updateGovernanceExpectations: MISSING  (`POST /classification-explorer/elements/{}/governance-expectations/update`)
- clearGovernanceExpectations: MISSING  (`POST /classification-explorer/elements/{}/governance-expectations/remove`)
- addResourceListToElement: MISSING  (`POST /classification-explorer/elements/{}/resource-list/{}/attach`)
- removeResourceListFromElement: MISSING  (`POST /classification-explorer/elements/{}/resource-list/{}/detach`)
- addMoreInformationToElement: MISSING  (`POST /classification-explorer/elements/{}/more-information/{}/attach`)
- removeMoreInformationFromElement: MISSING  (`POST /classification-explorer/elements/{}/more-information/{}/detach`)
- getSourceElements: MISMATCH `get_source_elements`
    - PATH
      SDK: /classification-explorer/glossaries/elements/{}/source
      API: /classification-explorer/elements/{}/source
- getElementsSourcedFrom: MISMATCH `get_elements_sourced_from`
    - PATH
      SDK: /classification-explorer/glossaries/elements/{}/sourced-from
      API: /classification-explorer/elements/{}/sourced-from
- removeScopeFromElement: MISSING  (`POST /classification-explorer/elements/{}/scoped-by/{}/detach`)
- licenseElement: ELSEWHERE -> `governance-officer.py`
- getLicensedElements: MISMATCH `get_licensed_elements`
    - PATH
      SDK: /classification-explorer/glossaries/elements/licenses/{}
      API: /classification-explorer/elements/licenses/{}
- getLicenses: MISMATCH `get_licenses`
    - PATH
      SDK: /classification-explorer/glossaries/elements/{}/licenses
      API: /classification-explorer/elements/{}/licenses
- certifyElement: ELSEWHERE -> `governance-officer.py`
- getCertifiedElements: MISMATCH `get_certified_elements`
    - PATH
      SDK: /classification-explorer/glossaries/elements/certifications/{}
      API: /classification-explorer/elements/certifications/{}
- getSearchKeywordByGUID: MISSING  (`POST /classification-explorer/search-keywords/{}/retrieve`)
- getSearchKeywordsByKeyword: MISSING  (`POST /classification-explorer/search-keywords/by-keyword`)
- findSearchKeywords: MISSING  (`POST /classification-explorer/search-keywords/by-search-string`)
- getRootElementByGUID: MISSING  (`POST /classification-explorer/elements/{}`)
- getRootElementByUniqueName: MISSING  (`POST /classification-explorer/elements/by-unique-name`)
- getMetadataElementGUIDByUniqueName: ELSEWHERE -> `metadata-expert.py`
- getRootElementsByType: MISSING  (`POST /classification-explorer/elements/by-type`)
- getRootElementsByPropertyValue: MISSING  (`POST /classification-explorer/elements/by-exact-property-value`)
- findRootElementsByPropertyValue: MISSING  (`POST /classification-explorer/elements/by-property-value-search`)
- getRootElementsByCategory: MISSING  (`POST /classification-explorer/elements/by-category`)
- findRootAuthoredElements: MISSING  (`POST /classification-explorer/authored-elements/by-search-string`)
- getRootAuthoredElementsByCategory: MISSING  (`POST /classification-explorer/authored-elements/by-category`)
- getRootElementsByClassification: MISSING  (`POST /classification-explorer/elements/by-classification/{}`)
- getRootElementsByClassificationWithPropertyValue: MISSING  (`POST /classification-explorer/elements/by-classification/{}/with-exact-property-value`)
- findRootElementsByClassificationWithPropertyValue: MISSING  (`POST /classification-explorer/elements/by-classification/{}/with-property-value-search`)
- getRelatedRootElements: MISSING  (`POST /classification-explorer/elements/{}/by-relationship`)
- getRelatedRootElementsWithPropertyValue: MISSING  (`POST /classification-explorer/elements/{}/by-relationship/{}/with-exact-property-value`)
- findRelatedRootElementsWithPropertyValue: MISSING  (`POST /classification-explorer/elements/{}/by-relationship/{}/with-property-value-search`)
- getRelationshipByGUID: ELSEWHERE -> `metadata-expert.py`

### Service: collection-manager

- createGlossary: ELSEWHERE -> `glossary-manager.py`
- createDataSharingAgreementCollection: MISSING  (`POST /collection-manager/collections`)
- updateAgreementStatus: MISSING  (`POST /collection-manager/collections/{}/update`)
- updateDigitalSubscriptionStatus: MISSING  (`POST /collection-manager/collections/{}/update`)
- detachDataDescription: MISSING  (`POST /collection-manager/metadata-elements/{}/data-descriptions/{}/detach`)
- attachSmartQuery: MISSING  (`POST /collection-manager/collections/results-sets/{}/smart-query/{}/attach`)
- detachSmartQuery: MISSING  (`POST /collection-manager/collections/results-sets/{}/smart-query/{}/detach`)
- attachAssociatedSkillSet: MISSING  (`POST /collection-manager/actors/{}/associated-skill-sets/{}/attach`)
- detachAssociatedSkillSet: MISMATCH `detach_associated_skill_set`
    - PATH
      SDK: /{}/actors/{}/associated-skill-sets/{}/detach
      API: /collection-manager/actors/{}/associated-skill-sets/{}/detach
- updateCollectionMembership: MISSING  (`POST /collection-manager/collections/{}/members/{}/update`)

### Service: community-matters


### Service: connection-maker

- createConnection: MISMATCH `create_connection`
    - PATH
      SDK: /{}/connections
      API: /connection-maker/connections
- createConnectionFromTemplate: MISMATCH `create_connection_from_template`
    - PATH
      SDK: /{}/connections/from-template
      API: /connection-maker/connections/from-template
- updateConnection: MISMATCH `update_connection`
    - PATH
      SDK: /{}/connections/{}/update
      API: /connection-maker/connections/{}/update
- linkConnectionConnectorType: MISMATCH `link_connection_connector_type`
    - PATH
      SDK: /{}/connections/{}/connector-types/{}/attach
      API: /connection-maker/connections/{}/connector-types/{}/attach
- detachConnectionConnectorType: MISMATCH `detach_connection_connector_type`
    - PATH
      SDK: /{}/connections/{}/connector-types/{}/detach
      API: /connection-maker/connections/{}/connector-types/{}/detach
- linkConnectionEndpoint: MISMATCH `link_connection_endpoint`
    - PATH
      SDK: /{}/connections/{}/endpoints/{}/attach
      API: /connection-maker/connections/{}/endpoints/{}/attach
- detachConnectionEndpoint: MISMATCH `detach_connection_endpoint`
    - PATH
      SDK: /{}/connections/{}/endpoints/{}/detach
      API: /connection-maker/connections/{}/endpoints/{}/detach
- linkEmbeddedConnection: MISMATCH `link_embedded_connection`
    - PATH
      SDK: /{}/connections/{}/embedded-connections/{}/attach
      API: /connection-maker/connections/{}/embedded-connections/{}/attach
- detachEmbeddedConnection: MISMATCH `detach_embedded_connection`
    - PATH
      SDK: /{}/connections/{}/embedded-connections/{}/detach
      API: /connection-maker/connections/{}/embedded-connections/{}/detach
- linkAssetToConnection: MISMATCH `link_asset_to_connection`
    - PATH
      SDK: /{}/assets/{}/connections/{}/attach
      API: /connection-maker/assets/{}/connections/{}/attach
- detachAssetFromConnection: MISMATCH `detach_asset_from_connection`
    - PATH
      SDK: /{}/assets/{}/connections/{}/detach
      API: /connection-maker/assets/{}/connections/{}/detach
- linkEndpointToITAsset: MISMATCH `link_endpoint_to_it_asset`
    - PATH
      SDK: /{}/assets/{}/endpoints/{}/attach
      API: /connection-maker/assets/{}/endpoints/{}/attach
- detachEndpointFromITAsset: MISMATCH `detach_endpoint_from_it_asset`
    - PATH
      SDK: /{}/assets/{}/endpoints/{}/detach
      API: /connection-maker/assets/{}/endpoints/{}/detach
- deleteConnection: MISMATCH `delete_connection`
    - PATH
      SDK: /{}/connections/{}/delete
      API: /connection-maker/connections/{}/delete
- getConnectionsByName: MISMATCH `get_connections_by_name`
    - PATH
      SDK: /{}/connections/by-name
      API: /connection-maker/connections/by-name
- findConnections: MISMATCH `find_connections`
    - PATH
      SDK: /{}/connections/by-search-string
      API: /connection-maker/connections/by-search-string
- getConnectionByGUID: MISMATCH `get_connection_by_guid`
    - PATH
      SDK: /{}/connections/{}/retrieve
      API: /connection-maker/connections/{}/retrieve
- createConnectorType: MISMATCH `create_connector_type`
    - PATH
      SDK: /{}/connector-types
      API: /connection-maker/connector-types
- createConnectorTypeFromTemplate: MISMATCH `create_connector_type_from_template`
    - PATH
      SDK: /{}/connector-types/from-template
      API: /connection-maker/connector-types/from-template
- updateConnectorType: MISMATCH `update_connector_type`
    - PATH
      SDK: /{}/connector-types/{}/update
      API: /connection-maker/connector-types/{}/update
- deleteConnectorType: MISMATCH `delete_connector_type`
    - PATH
      SDK: /{}/connector-types/{}/delete
      API: /connection-maker/connector-types/{}/delete
- getConnectorTypesByName: MISMATCH `get_connector_types_by_name`
    - PATH
      SDK: /{}/connector-types/by-name
      API: /connection-maker/connector-types/by-name
- getConnectorTypesByConnectorProviderClassName: MISMATCH `get_connector_types_by_connector_provider_class_name`
    - PATH
      SDK: /{}/connector-types/by-connector-provider-class-name
      API: /connection-maker/connector-types/by-connector-provider-class-name
- findConnectorTypes: MISMATCH `find_connector_types`
    - PATH
      SDK: /{}/connector-types/by-search-string
      API: /connection-maker/connector-types/by-search-string
- getConnectorTypeByGUID: MISMATCH `get_connector_type_by_guid`
    - PATH
      SDK: /{}/connector-types/{}/retrieve
      API: /connection-maker/connector-types/{}/retrieve
- createEndpoint: MISMATCH `create_endpoint`
    - PATH
      SDK: /{}/endpoints
      API: /connection-maker/endpoints
- createEndpointFromTemplate: MISMATCH `create_endpoint_from_template`
    - PATH
      SDK: /{}/endpoints/from-template
      API: /connection-maker/endpoints/from-template
- updateEndpoint: MISMATCH `update_endpoint`
    - PATH
      SDK: /{}/endpoints/{}/update
      API: /connection-maker/endpoints/{}/update
- deleteEndpoint: MISMATCH `delete_endpoint`
    - PATH
      SDK: /{}/endpoints/{}/delete
      API: /connection-maker/endpoints/{}/delete
- getEndpointsByName: MISMATCH `get_endpoints_by_name`
    - PATH
      SDK: /{}/endpoints/by-name
      API: /connection-maker/endpoints/by-name
- getEndpointsByNetworkAddress: MISMATCH `get_endpoints_by_network_address`
    - PATH
      SDK: /{}/endpoints/by-network-address
      API: /connection-maker/endpoints/by-network-address
- getEndpointsForAsset: MISMATCH `get_endpoints_for_asset`
    - PATH
      SDK: /{}/assets/{}/endpoints/retrieve
      API: /connection-maker/assets/{}/endpoints/retrieve
- findEndpoints: MISMATCH `find_endpoints`
    - PATH
      SDK: /{}/endpoints/by-search-string
      API: /connection-maker/endpoints/by-search-string
- getEndpointByGUID: MISMATCH `get_endpoint_by_guid`
    - PATH
      SDK: /{}/endpoints/{}/retrieve
      API: /connection-maker/endpoints/{}/retrieve

### Service: data-designer

- findAllDataStructures - with full request body: MISSING  (`POST /data-designer/data-structures/by-search-string`)
- findDataStructures - with full request body: MISSING  (`POST /data-designer/data-structures/by-search-string`)
- getDataStructuresByName - with full request body: MISSING  (`POST /data-designer/data-structures/by-name`)
- getDataStructureByGUID - with request body: MISSING  (`POST /data-designer/data-structures/{}/retrieve`)
- linkNestedDataFields: MISSING  (`POST /data-designer/data-fields/{}/nested-data-fields/{}/attach`)
- detachNestedDataFields: MISSING  (`POST /data-designer/data-fields/{}/nested-data-fields/{}/detach`)
- findAllDataFields - with full request body: MISSING  (`POST /data-designer/data-fields/by-search-string`)
- findDataFields - with full request body: MISSING  (`POST /data-designer/data-fields/by-search-string`)
- getDataFieldsByName - with full request body: MISSING  (`POST /data-designer/data-fields/by-name`)
- getDataFieldByGUID - with request body: MISSING  (`POST /data-designer/data-fields/{}/retrieve`)
- createDataValueSpecificationFromTemplate: MISSING  (`POST /data-designer/data-value-specifications/from-template`)
- detachSpecializedDataValueSpecification: MISMATCH `detach_specialized_data_value_specification`
    - PATH
      SDK: /data-designer/data-value-specifications/{}/specialized-data-value-specification-definition/{}/detach
      API: /data-designer/data-value-specifications/{}/specialized-data-value-specifications/{}/detach
- assignDataValueSpecification: MISSING  (`POST /data-designer/elements/{}/data-value-specifications/{}/attach`)
- detachDataValueSpecificationAssignment: MISSING  (`POST /data-designer/elements/{}/data-value-specifications/{}/detach`)
- findAllDataClasses: MISSING  (`POST /data-designer/data-value-specifications/by-search-string`)
- findAllDataGrains: MISSING  (`POST /data-designer/data-value-specifications/by-search-string`)
- findDataValueSpecifications - with full request body: MISSING  (`POST /data-designer/data-value-specifications/by-search-string`)
- linkDataValueSpecificationDefinition: MISSING  (`POST /data-designer/data-definitions/{}/data-value-specification-definition/{}/attach`)
- detachDataValueSpecificationDefinition: MISSING  (`POST /data-designer/data-definitions/{}/data-value-specification-definition/{}/detach`)
- detachCertificationTypeToDataStructure: MISSING  (`POST /data-designer/certification-types/{}/data-structure-definition/{}/detach`)

### Service: data-discovery


### Service: data-engineer

- getTabularDataSetReport: MISSING  (`GET /data-engineer/tabular-data-sets/{}/report`)

### Service: digital-business


### Service: external-links

- linkCitedDocumentReference: MISSING  (`POST /external-links/elements/{}/cited-document-references/{}/attach`)
- detachCitedDocumentReference: MISSING  (`POST /external-links/elements/{}/cited-document-references/{}/detach`)
- deleteExternalReference: MISMATCH `delete_external_reference`
    - BODY DeleteRelationshipRequestBody != DeleteElementRequestBody

### Service: feedback-manager

- addCommentToElement: MISSING  (`POST /feedback-manager/elements/{}/comments`)
- updateComment: MISSING  (`POST /feedback-manager/comments/{}/update`)
- setupAcceptedAnswer: MISSING  (`POST /feedback-manager/comments/questions/{}/answers/{}`)
- clearAcceptedAnswer: MISSING  (`POST /feedback-manager/comments/questions/{}/answers/{}/remove`)
- removeCommentFromElement: MISSING  (`POST /feedback-manager/comments/{}/remove`)
- getCommentByGUID: MISSING  (`POST /feedback-manager/comments/{}/retrieve`)
- getAttachedComments: MISSING  (`POST /feedback-manager/elements/{}/comments/retrieve`)
- findComments: MISSING  (`POST /feedback-manager/comments/by-search-string`)
- addLikeToElement: MISSING  (`POST /feedback-manager/elements/{}/likes`)
- removeLikeFromElement: MISSING  (`POST /feedback-manager/elements/{}/likes/remove`)
- getAttachedLikes: MISSING  (`POST /feedback-manager/elements/{}/likes/retrieve`)
- addRatingToElement: MISSING  (`POST /feedback-manager/elements/{}/ratings`)
- removeRatingFromElement: MISSING  (`POST /feedback-manager/elements/{}/ratings/remove`)
- getAttachedRatings: MISSING  (`POST /feedback-manager/elements/{}/ratings/retrieve`)
- createInformalTag: MISSING  (`POST /feedback-manager/tags`)
- updateTagDescription: MISSING  (`POST /feedback-manager/tags/{}/update`)
- deleteTag: MISSING  (`POST /feedback-manager/tags/{}/remove`)
- getTag: MISSING  (`POST /feedback-manager/tags/{}/retrieve`)
- getTagsByName: MISSING  (`POST /feedback-manager/tags/by-name`)
- findTags: MISSING  (`POST /feedback-manager/tags/by-search-string`)
- findMyTags: MISSING  (`POST /feedback-manager/tags/private/by-search-string`)
- addTagToElement: MISSING  (`POST /feedback-manager/elements/{}/tags/{}`)
- getElementsByTag: MISSING  (`POST /feedback-manager/elements/by-tag/{}/retrieve`)
- getAttachedTags: MISSING  (`POST /feedback-manager/elements/{}/tags/retrieve`)
- removeTagFromElement: MISSING  (`POST /feedback-manager/elements/{}/tags/{}/remove`)
- createNoteLog: MISSING  (`POST /feedback-manager/elements/{}/note-logs`)
- updateNoteLog: MISSING  (`POST /feedback-manager/note-logs/{}`)
- removeNoteLog: MISSING  (`POST /feedback-manager/note-logs/{}/remove`)
- findNoteLogs: MISSING  (`POST /feedback-manager/note-logs/by-search-string`)
- getNoteLogsByName: MISSING  (`POST /feedback-manager/note-logs/by-name`)
- getNoteLogsForElement: MISSING  (`POST /feedback-manager/elements/{}/note-logs/retrieve`)
- getNoteLogByGUID: MISSING  (`POST /feedback-manager/note-logs/{}/retrieve`)
- createNote: MISSING  (`POST /feedback-manager/assets`)
- updateNote: MISSING  (`POST /feedback-manager/assets/{}/update`)
- removeNote: MISSING  (`POST /feedback-manager/assets/{}/delete`)
- findNotes: MISSING  (`POST /feedback-manager/assets/by-search-string`)
- getNotesForNoteLog: MISSING  (`POST /feedback-manager/note-logs/{}/notes/retrieve`)
- getNoteByGUID: MISSING  (`POST /feedback-manager/assets/{}/retrieve`)

### Service: glossary-manager

- getTermRelationshipTypeNames: MISSING  (`GET /glossary-manager/glossaries/terms/relationships/type-names`)
- clearTermAsAbstractConcept: MISMATCH `remove_is_abstract_concept`
    - BODY DeleteClassificationRequestBody != DeleteElementRequestBody
- clearTermAsActivity: MISMATCH `remove_activity_description`
    - BODY DeleteClassificationRequestBody != DeleteRelationshipRequestBody
- clearTermAsContext: MISMATCH `remove_is_context_definition`
    - BODY DeleteClassificationRequestBody != DeleteRelationshipRequestBody

### Service: governance-officer

- getValidMetadataValues - domainIdentifier values: MISSING  (`GET /valid-metadata/get-valid-metadata-values/domainIdentifier`)
- createGovernanceDefinition: MISMATCH `create_governance_definition`
    - PATH
      SDK: /{}/governance-definitions
      API: /governance-officer/governance-definitions
- createRegulation: MISSING  (`POST /governance-officer/governance-definitions`)
- addRegulatorToRegulation: MISMATCH `add_regulator_to_regulation`
    - PATH
      SDK: /{}/regulations/{}/regulators/organizations/{}/attach
      API: /governance-officer/regulations/{}/regulators/organizations/{}/attach
- removeRegulatorFromRegulation: MISSING  (`POST /governance-officer/regulations/{}/regulators/organizations/{}/detach`)
- createGovernanceControl: MISSING  (`POST /governance-officer/governance-definitions`)
- createDataLens: MISMATCH `create_data_lens`
    - PATH
      SDK: /{}/governance-definitions
      API: /governance-officer/governance-definitions
- createSecurityAccessControl: MISSING  (`POST /governance-officer/governance-definitions`)
- createNamingStandardRule: MISSING  (`POST /governance-officer/governance-definitions`)
- createCertificationType: MISSING  (`POST /governance-officer/governance-definitions`)
- createLicenseType: MISSING  (`POST /governance-officer/governance-definitions`)
- createGovernanceDefinitionFromTemplate: MISMATCH `create_governance_definition_from_template`
    - PATH
      SDK: /{}/governance-definitions/from-template
      API: /governance-officer/governance-definitions/from-template
- updateGovernanceDefinition: MISMATCH `update_governance_definition`
    - PATH
      SDK: /{}/governance-definitions/{}/update
      API: /governance-officer/governance-definitions/{}/update
- updateGovernanceDefinitionStatus: MISSING  (`POST /governance-officer/governance-definitions/{}/update`)
- detachPeerDefinitions: MISMATCH `detach_peer_definitions`
    - PATH
      SDK: /{}/governance-definitions/{}/peer-definitions/{}/{}/detach
      API: /governance-officer/governance-definitions/{}/peer-definitions/{}/{}/detach
- attachSupportingDefinition: MISSING  (`POST /governance-officer/governance-definitions/{}/supporting-definitions/{}/{}/attach`)
- detachSupportingDefinition: MISSING  (`POST /governance-officer/governance-definitions/{}/supporting-definitions/{}/{}/detach`)
- findAllGovernanceDefinitions: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- findAllGovernanceDefinitions - with full request body: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- findGovernanceDefinitions: MISMATCH `find_governance_definitions`
    - PATH
      SDK: /{}/governance-definitions/by-search-string
      API: /governance-officer/governance-definitions/by-search-string
- findGovernanceDefinitions - with full request body: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- getGovernanceDefinitionsByName: MISMATCH `get_governance_definitions_by_name`
    - PATH
      SDK: /{}/governance-definitions/by-name
      API: /governance-officer/governance-definitions/by-name
- getGovernanceDefinitionsByName - with full request body: MISSING  (`POST /governance-officer/governance-definitions/by-name`)
- getGovernanceDefinitionByGUID: MISMATCH `get_governance_definition_by_guid`
    - PATH
      SDK: /{}/governance-definitions/{}/retrieve
      API: /governance-officer/governance-definitions/{}/retrieve
- getGovernanceDefinitionByGUID - with request body: MISSING  (`POST /governance-officer/governance-definitions/{}/retrieve`)
- getAllGovernanceActionTypes: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- findGovernanceActionTypes: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- getGovernanceActionTypesByName: MISSING  (`POST /governance-officer/governance-definitions/by-name`)
- getGovernanceActionTypeByGUID: MISSING  (`POST /governance-officer/governance-definitions/{}/retrieve`)
- findGovernanceActionProcesses: MISSING  (`POST /governance-officer/governance-action-processes/by-search-string`)
- getAllGovernanceActionProcesses: MISSING  (`POST /governance-officer/governance-definitions/by-search-string`)
- getGovernanceActionProcessesByName: MISSING  (`POST /governance-officer/governance-definitions/by-name`)
- getGovernanceActionProcessGraph: MISMATCH `get_governance_action_process_graph`
    - PATH
      SDK: /{}/governance-action-processes/{}/graph
      API: /governance-officer/governance-action-processes/{}/graph
    - BODY FilterRequestBody != ResultsRequestBody
- addGovernanceDefinitionToElement: MISSING  (`POST /governance-officer/elements/{}/governed-by/definition/{}/attach`)
- removeGovernanceDefinitionFromElement: MISSING  (`POST /governance-officer/elements/{}/governed-by/definition/{}/detach`)
- linkDesignToImplementation: MISMATCH `link_design_to_implementation`
    - PATH
      SDK: /{}/designs/{}/implementations/{}/attach
      API: /governance-officer/designs/{}/implementations/{}/attach
- detachDesignFromImplementation: MISMATCH `detach_design_from_implementation`
    - PATH
      SDK: /{}/designs/{}/implementations/{}/detach
      API: /governance-officer/designs/{}/implementations/{}/detach
    - BODY DeleteElementRequestBody != DeleteRelationshipRequestBody
- linkImplementationResource: MISMATCH `link_implementation_resource`
    - PATH
      SDK: /{}/designs/{}/implementation-resources/{}/attach
      API: /governance-officer/designs/{}/implementation-resources/{}/attach
- detachImplementationResource: MISMATCH `detach_implementation_resource`
    - PATH
      SDK: /{}/designs/{}/implementation-resources/{}/detach
      API: /governance-officer/designs/{}/implementation-resources/{}/detach
- linkApprovedPurpose: MISSING  (`POST /governance-officer/elements/{}/approved-purposes/{}/attach`)
- detachApprovedPurpose: MISSING  (`POST /governance-officer/elements/{}/approved-purposes/{}/detach`)
- linkGovernanceResults: MISMATCH `link_governance_results`
    - PATH
      SDK: /{}/governance-metrics/{}/measurements/{}/attach
      API: /governance-officer/governance-metrics/{}/measurements/{}/attach
- detachGovernanceResults: MISMATCH `detach_governance_results`
    - PATH
      SDK: /{}/governance-metrics/{}/measurements/{}/detach
      API: /governance-officer/governance-metrics/{}/measurements/{}/detach
- licenseElement: MISMATCH `license_element`
    - PATH
      SDK: /{}/elements/{}/license-types/{}/license
      API: /governance-officer/elements/{}/license-types/{}/license
- updateLicense: ELSEWHERE -> `classification-explorer.py`
- unlicenseElement: ELSEWHERE -> `classification-explorer.py`
- certifyElement: MISMATCH `certify_element`
    - PATH
      SDK: /{}/elements/{}/certification-types/{}/certify
      API: /governance-officer/elements/{}/certification-types/{}/certify
- updateCertification: ELSEWHERE -> `classification-explorer.py`
- decertifyElement: ELSEWHERE -> `classification-explorer.py`

### Service: lineage-linker

- linkLineage: MISMATCH `link_lineage`
    - PATH
      SDK: /lineage-linker/elements/{}/{}/{}/attach
      API: /lineage-linker/from-elements/{}/via/{}/to-elements/{}/attach

### Service: location-arena

- linkPeerLocation: MISSING  (`POST /location-arena/locations/{}/adjacent-locations/{}/attach`)

### Service: metadata-expert

- createMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements`)
- updateMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/update-properties`)
- updateMetadataElementEffectivityInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/update-effectivity`)
- deleteMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/delete`)
- archiveMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/archive`)
- reclassifyMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/classifications/{}/update-properties`)
- updateClassificationEffectivityInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/classifications/{}/update-effectivity`)
- declassifyMetadataElementInStore: MISSING  (`POST /metadata-expert/metadata-elements/{}/classifications/{}/delete`)
- createRelatedElementsInStore: MISSING  (`POST /metadata-expert/related-elements`)
- updateRelatedElementsInStore: MISSING  (`POST /metadata-expert/related-elements/{}/update-properties`)
- updateRelatedElementsEffectivityInStore: MISSING  (`POST /metadata-expert/related-elements/{}/update-effectivity`)
- deleteRelatedElementsInStore: MISSING  (`POST /metadata-expert/related-elements/{}/delete`)
- getMetadataElementByGUID: MISMATCH `get_metadata_element_by_guid`
    - PATH
      SDK: /{}/metadata-elements/{}
      API: /metadata-expert/metadata-elements/{}
- getAnchoredElementsGraph: MISSING  (`POST /metadata-expert/metadata-elements/{}/with-anchored-elements`)
- getMetadataElementByUniqueName: MISMATCH `get_metadata_element_by_unique_name`
    - PATH
      SDK: /{}/metadata-elements/by-unique-name
      API: /metadata-expert/metadata-elements/by-unique-name
- getMetadataElementGUIDByUniqueName: MISMATCH `get_metadata_guid_by_unique_name`
    - PATH
      SDK: /{}/metadata-elements/guid-by-unique-name
      API: /metadata-expert/metadata-elements/guid-by-unique-name
    - BODY FilterRequestBody != UniqueNameRequestBody
- getClassificationHistory: MISMATCH `get_classification_history`
    - PATH
      SDK: /{}/metadata-elements/{}/classifications/{}/history
      API: /metadata-expert/metadata-elements/{}/classifications/{}/history
- findMetadataElementsWithString: MISMATCH `find_metadata_elements_with_string`
    - PATH
      SDK: /{}/metadata-elements/by-search-string
      API: /metadata-expert/metadata-elements/by-search-string
- findElementsForAnchor: MISMATCH `find_elements_for_anchor`
    - PATH
      SDK: /{}/metadata-elements/by-search-string/for-anchor/{}
      API: /metadata-expert/metadata-elements/by-search-string/for-anchor/{}
- findElementsInAnchorDomain: MISMATCH `find_elements_in_anchor_domain`
    - PATH
      SDK: /{}/metadata-elements/by-search-string/in-anchor-domain/{}
      API: /metadata-expert/metadata-elements/by-search-string/in-anchor-domain/{}
- findElementsInAnchorScope: MISMATCH `find_elements_in_anchor_scope`
    - PATH
      SDK: /{}/metadata-elements/by-search-string/in-anchor-scope/{}
      API: /metadata-expert/metadata-elements/by-search-string/in-anchor-scope/{}
- getAllRelatedMetadataElements: MISSING  (`POST /metadata-expert/related-elements/{}/any-type`)
- getRelatedMetadataElements: MISMATCH `get_related_metadata_elements`
    - PATH
      SDK: /{}/related-elements/{}/type/{}
      API: /metadata-expert/related-elements/{}/type/{}
- getAllMetadataElementRelationships: MISMATCH `get_all_metadata_element_relationships`
    - PATH
      SDK: /{}/metadata-elements/{}/linked-by-any-type/to-elements/{}
      API: /metadata-expert/metadata-elements/{}/linked-by-any-type/to-elements/{}
- getMetadataElementRelationships: MISMATCH `get_metadata_element_relationships`
    - PATH
      SDK: /{}/metadata-elements/{}/linked-by-type/{}/to-elements/{}
      API: /metadata-expert/metadata-elements/{}/linked-by-type/{}/to-elements/{}
- findMetadataElements: MISMATCH `find_metadata_elements`
    - PATH
      SDK: /{}/metadata-elements/by-search-conditions
      API: /metadata-expert/metadata-elements/by-search-conditions
- countMetadataElements: MISMATCH `count_metadata_elements`
    - PATH
      SDK: /{}/metadata-elements/by-search-conditions/count
      API: /metadata-expert/metadata-elements/by-search-conditions/count
- findRelationshipsBetweenMetadataElements: MISSING  (`POST /metadata-expert/relationships/by-search-conditions`)
- countRelationshipsBetweenMetadataElements: MISSING  (`POST /metadata-expert/relationships/by-search-conditions/count`)
- getRelationshipByGUID: MISMATCH `get_relationship_by_guid`
    - PATH
      SDK: /{}/relationships/by-guid/{}
      API: /metadata-expert/relationships/by-guid/{}
- getRelationshipHistory: MISMATCH `get_relationship_history`
    - PATH
      SDK: /{}/relationships/{}/history
      API: /metadata-expert/relationships/{}/history

### Service: my-profile

- getMyProfile: MISMATCH `get_my_profile`
    - VERB POST != GET
- Get My Profile: MISSING  (`POST /my-profile`)
- Add My Profile: MISSING  (`POST /my-profile/new`)

### Service: notification-manager


### Service: people-organizer


### Service: platform-services

- Get OMAG Server Platform Origin: MISSING  (`GET /platform-services/server-platform/origin`)
- Get Active User List: MISSING  (`GET /platform-services/server-platform/security/user-list`)
- Get Contractor User List: MISSING  (`GET /platform-services/server-platform/security/user-list`)
- Get all known servers: MISSING  (`GET /platform-services/server-platform/servers`)
- Query the status of a specific server: ELSEWHERE -> `server-operations.py`
- Query a connector: MISSING  (`GET /platform-services/server-platform/connector-types/org.odpi.openmetadata.metadatasecurity.accessconnector.OpenMetadataAccessSecurityProvider`)
- Shutdown and unregister server from cohorts: MISSING  (`DELETE /platform-services/server-platform/servers/{}`)
- Shutdown all active servers: MISSING  (`DELETE /platform-services/server-platform/servers/instance`)
- Shutdown and unregister all active servers: MISSING  (`DELETE /platform-services/server-platform/servers`)
- Shutdown server platform: MISSING  (`DELETE /platform-services/server-platform/instance`)

### Service: privacy-officer

- linkPermittedProcessing: MISMATCH `link_permitted_processing`
    - PATH
      SDK: /{}/data-processing-purposes/{}/permitted-processing/{}/attach
      API: /privacy-officer/data-processing-purposes/{}/permitted-processing/{}/attach
- detachPermittedProcessing: MISMATCH `detach_permitted_processing`
    - PATH
      SDK: /{}/data-processing-purposes/{}/permitted-processing/{}/detach
      API: /privacy-officer/data-processing-purposes/{}/permitted-processing/{}/detach
- linkDataProcessingTarget: MISMATCH `link_data_processing_target`
    - PATH
      SDK: /{}/data-processing-actions/{}/targets/{}/attach
      API: /privacy-officer/data-processing-actions/{}/targets/{}/attach
- detachDataProcessingTarget: MISMATCH `detach_data_processing_target`
    - PATH
      SDK: /{}/data-processing-actions/{}/targets/{}/detach
      API: /privacy-officer/data-processing-actions/{}/targets/{}/detach

### Service: product-catalog

- find DigitalProductCatalogs: MISSING  (`POST /product-catalog/collections/by-search-string`)
- find the open metadata product catalog: MISSING  (`POST /product-catalog/collections/by-search-string`)
- find the valid metadata value list digital product: MISSING  (`POST /product-catalog/collections/by-search-string`)
- getSolutionBlueprintsByName: ELSEWHERE -> `solution-architect.py`
- getTechnologyTypeDetail: MISSING  (`POST /automated-curation/technology-types/by-name`)
- getTechnologyTypeTemplates: MISSING  (`POST /automated-curation/technology-types/elements`)
- createElementFromTemplate: MISSING  (`POST /automated-curation/catalog-templates/new-element`)
- getGovernanceActionProcessesByName: MISSING  (`POST /product-catalog/governance-definitions/by-name`)
- getGovernanceActionProcessGraph: ELSEWHERE -> `governance-officer.py`
- initiateGovernanceActionProcess: MISSING  (`POST /automated-curation/governance-action-processes/initiate`)
- findSubscriptions: MISSING  (`POST /collection-manager/collections/by-search-string`)
- Get My Profile: MISSING  (`POST /my-profile`)
- getCommunitiesByName: ELSEWHERE -> `community-matters.py`
- getNoteLogsByName: MISSING  (`POST /feedback-manager/note-logs/by-name`)

### Service: product-manager

- updateDigitalProductStatus: MISSING  (`POST /product-manager/collections/{}/update`)

### Service: project-manager

- createClassifiedProject: MISSING  (`POST /project-manager/projects`)
- createCampaign: MISSING  (`POST /project-manager/projects`)
- createTaskForProject: MISSING  (`POST /project-manager/projects/{}/task`)
- setupProjectDependency: MISSING  (`POST /project-manager/projects/{}/project-dependencies/{}/attach`)
- setupProjectHierarchy: MISSING  (`POST /project-manager/projects/{}/project-hierarchies/{}/attach`)

### Service: reference-data


### Service: runtime-manager

- getPlatformsByDeployedImplementationType: MISSING  (`POST /runtime-manager/platforms/by-deployed-implementation-type`)
- getPlatformTemplatesByDeployedImplementationType: MISSING  (`POST /runtime-manager/platforms/by-deployed-implementation-type`)
- Get Connector Type: MISSING  (`GET /runtime-manager/platforms/{}/connector-types/{}`)
- getElementsByCategory: MISSING  (`POST /runtime-manager/elements/by-category`)
- getOMAGServerReport: MISSING  (`GET /runtime-manager/omag-servers/{}/instance/report`)
- activateWithStoredConfig: MISSING  (`POST /runtime-manager/omag-servers/{}/instance`)
- getConfigurationProperties: MISSING  (`GET /runtime-manager/integration-daemons/{}/integration-connectors/{}/configuration-properties`)
- updateConfigurationProperties: MISSING  (`POST /runtime-manager/integration-daemons/{}/integration-connectors/configuration-properties`)
- updateEndpointNetworkAddress: MISSING  (`POST /runtime-manager/integration-daemons/{}/integration-connectors/{}/endpoint-network-address`)
- updateConnectorConnection: MISSING  (`POST /runtime-manager/integration-daemons/{}/integration-connectors/{}/connection`)
- refreshConnectors: MISSING  (`POST /runtime-manager/integration-daemons/{}/integration-connectors/refresh`)
- restartConnectors: MISSING  (`POST /runtime-manager/integration-daemons/{}/integration-connectors/restart`)
- refreshIntegrationGroupConfig: MISSING  (`GET /runtime-manager/integration-daemons/{}/integration-groups/{}/refresh-config`)
- refreshConfig: MISSING  (`GET /runtime-manager/engine-hosts/{}/governance-engines/{}/refresh-config`)
- addOpenMetadataArchiveFile: MISSING  (`POST /runtime-manager/omag-servers/{}/instance/load/open-metadata-archives/file`)
- addOpenMetadataArchiveContent: MISSING  (`POST /runtime-manager/omag-servers/{}/instance/load/open-metadata-archives/archive-content`)
- createMetadataRepositoryCohort: MISSING  (`POST /runtime-manager/metadata-repository-cohorts`)
- createMetadataRepositoryCohortFromTemplate: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/from-template`)
- updateMetadataRepositoryCohort: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/{}/update`)
- deleteMetadataRepositoryCohort: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/{}/delete`)
- getMetadataRepositoryCohortsByName: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/by-name`)
- findMetadataRepositoryCohorts: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/by-search-string`)
- getMetadataRepositoryCohortByGUID: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/{}/retrieve`)
- linkCohortMember: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/{}/cohort-members/{}/attach`)
- detachCohortMember: MISSING  (`POST /runtime-manager/metadata-repository-cohorts/{}/cohort-members/{}/detach`)
- connectToCohortGet: MISSING  (`GET /runtime-manager/cohort-members/{}/cohorts/{}/connect`)
- disconnectFromCohortGet: MISSING  (`GET /runtime-manager/cohort-members/{}/cohorts/{}/disconnect`)
- unregisterFromCohortGet: MISSING  (`GET /runtime-manager/cohort-members/{}/cohorts/{}/unregister`)

### Service: schema-maker

- deleteSchemaType: MISMATCH `delete_schema_type`
    - BODY DeleteElementRequestBody != MetadataSourceRequestBody
- updateSchemaAttribute: MISMATCH `update_schema_attribute`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/update
      API: /schema-maker/schema-attributes/update
- deleteSchemaAttribute: MISMATCH `delete_schema_attribute`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/delete
      API: /schema-maker/schema-attributes/delete
    - BODY DeleteElementRequestBody != MetadataSourceRequestBody
- getSchemaAttributeByGUID: MISMATCH `get_schema_attribute_by_guid`
    - PATH
      SDK: /schema-maker/schema-attributes/{}/retrieve
      API: /schema-maker/schema-attributes/{}/retrieve"}

### Service: security-officer

- setSecurityAccessControl: MISMATCH `set_security_access_control`
    - PATH
      SDK: /{}/platforms/{}/security-access-control
      API: /security-officer/platforms/{}/security-access-control
- getSecurityAccessControl: MISMATCH `get_security_access_control`
    - PATH
      SDK: /{}/platforms/{}/security-access-control/{}
      API: /security-officer/platforms/{}/security-access-control/{}
- deleteSecurityAccessControl: MISMATCH `delete_security_access_control`
    - PATH
      SDK: /{}/platforms/{}/security-access-control/{}
      API: /security-officer/platforms/{}/security-access-control/{}
- find Security Roles: MISSING  (`POST /security-officer/collections/by-search-string`)
- find Security Groups: MISSING  (`POST /security-officer/collections/by-search-string`)

### Service: solution-architect

- getDesignPatternsByName: MISMATCH `get_design_patterns_by_name`
    - PATH
      SDK: /solution-architect/design-patterns/by-name/{}
      API: /solution-architect/design-patterns/by-name
    - BODY SearchStringRequestBody != FilterRequestBody
- createInformationSupplyChain: MISSING  (`POST /solution-architect/information-supply-chains`)
- createInformationSupplyChainFromTemplate: MISSING  (`POST /solution-architect/information-supply-chains/from-template`)
- updateInformationSupplyChain: MISSING  (`POST /solution-architect/information-supply-chains/{}/update`)
- linkPeersInInformationSupplyChain: MISSING  (`POST /solution-architect/information-supply-chains/{}/peer-links/{}/attach`)
- unlinkPeerInformationSupplyChains: MISSING  (`POST /solution-architect/information-supply-chains/{}/peer-links/{}/detach`)
- deleteInformationSupplyChain: MISSING  (`POST /solution-architect/information-supply-chains/{}/delete`)
- findAllInformationSupplyChains - with full request body: MISSING  (`POST /solution-architect/information-supply-chains/by-search-string`)
- findInformationSupplyChains - with full request body: MISSING  (`POST /solution-architect/information-supply-chains/by-search-string`)
- getInformationSupplyChainsByName: MISSING  (`POST /solution-architect/information-supply-chains/by-name`)
- getInformationSupplyChainsByName - with full request body: MISSING  (`POST /solution-architect/information-supply-chains/by-name`)
- getInformationSupplyChainByGUID: MISSING  (`POST /solution-architect/information-supply-chains/{}/retrieve`)
- getInformationSupplyChainByGUID - with request body: MISSING  (`POST /solution-architect/information-supply-chains/{}/retrieve`)
- findAllSolutionBlueprints - with full request body: MISSING  (`POST /solution-architect/solution-blueprints/by-search-string`)
- findSolutionBlueprints - with full request body: MISSING  (`POST /solution-architect/solution-blueprints/by-search-string`)
- getSolutionBlueprintsByName - with full request body: MISSING  (`POST /solution-architect/solution-blueprints/by-name`)
- getSolutionBlueprintByGUID - with request body: MISSING  (`POST /solution-architect/solution-blueprints/{}/retrieve`)
- linkSolutionComponentActor: MISSING  (`POST /solution-architect/solution-roles/{}/solution-component-actors/{}/attach`)
- detachSolutionComponentActor: MISSING  (`POST /solution-architect/solution-roles/{}/solution-component-actors/{}/detach`)
- findAllSolutionRoles - with full request body: MISSING  (`POST /solution-architect/solution-roles/by-search-string`)
- findSolutionRoles - with full request body: MISSING  (`POST /solution-architect/solution-roles/by-search-string`)
- getSolutionRolesByName: MISMATCH `get_solution_roles_by_name`
    - PATH
      SDK: /solution-architect/solution-roles/by-name{}
      API: /solution-architect/solution-roles/by-name
- getSolutionRolesByName - with full request body: MISSING  (`POST /solution-architect/solution-roles/by-name`)
- getSolutionRoleByGUID - with request body: MISSING  (`POST /solution-architect/solution-roles/{}/retrieve`)
- detachSubcomponent: MISSING  (`POST /solution-architect/solution-components/{}/subcomponents/{}/detach`)
- detachAllSolutionLinkingWire: MISSING  (`POST /solution-architect/solution-components/{}/wired-to/{}/detach`)
- detachSolutionLinkingWire: MISMATCH `detach_solution_linking_wire`
    - PATH
      SDK: /solution-architect/solution-components/{}/wired-to/{}/detach
      API: /solution-architect/solution-components/wires/{}/detach
- findAllSolutionComponents - with full request body: MISSING  (`POST /solution-architect/solution-components/by-search-string`)
- findSolutionComponents - with full request body: MISSING  (`POST /solution-architect/solution-components/by-search-string`)
- getSolutionComponentsByName: MISMATCH `get_solution_components_by_name`
    - PATH
      SDK: /solution-architect/solution-components/by-name{}
      API: /solution-architect/solution-components/by-name
- getSolutionComponentsByName - with full request body: MISSING  (`POST /solution-architect/solution-components/by-name`)
- getSolutionComponentByGUID - with request body: MISSING  (`POST /solution-architect/solution-components/{}/retrieve`)
- getSolutionComponentImplementations: MISMATCH `get_solution_component_implementations`
    - PATH
      SDK: /solution-architect/solution-components/{}/implementations{}
      API: /solution-architect/solution-components/{}/implementations

### Service: subject-area

- linkSubjectAreas: MISSING  (`POST /subject-area/collections/{}/collection-hierarchies/{}/attach`)
- detachSubjectAreas: MISSING  (`POST /subject-area/collections/{}/collection-hierarchies/{}/detach`)
- findAllSubjectAreas: MISSING  (`POST /subject-area/collectionss/by-search-string`)
- findAllSubjectAreas - with full request body: MISSING  (`POST /subject-area/collections/by-search-string`)
- findSubjectAreas - with full request body: MISSING  (`POST /subject-area/collections/by-search-string`)
- getSubjectAreasByName - with full request body: MISSING  (`POST /subject-area/collections/by-name`)
- getSubjectAreaByGUID - with request body: MISSING  (`POST /subject-area/collections/{}/retrieve`)

### Service: template-manager


### Service: time-keeper


### Service: valid-metadata

- setUpValidMetadataValue: MISSING  (`POST /valid-metadata/setup-value/{}`)
- setUpValidMetadataMapName: MISSING  (`POST /valid-metadata/setup-map-name/{}`)
- setUpValidMetadataMapValue: MISSING  (`POST /valid-metadata/setup-map-value/{}/{}`)
- getAllTypes: MISSING  (`GET /valid-metadata/open-metadata-types`)
- getEntityDefs: MISSING  (`GET /valid-metadata/open-metadata-types/entity-defs`)
- getRelationshipDefs: MISSING  (`GET /valid-metadata/open-metadata-types/relationship-defs`)
- getClassificationDefs: MISSING  (`GET /valid-metadata/open-metadata-types/classification-defs`)
- getAttributeTypes: MISSING  (`GET /valid-metadata/open-metadata-types/attribute-defs`)
- getTypeDefByName: MISSING  (`GET /valid-metadata/open-metadata-types/name/{}`)
- setUpSpecificationProperty: MISSING  (`POST /valid-metadata/elements/{}/specification-properties`)
