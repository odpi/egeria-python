___

## Initiate Engine Action
> Ad-hoc initiate an engine action against a governance engine -- a one-off runtime request, distinct from the design-time Governance Action Process/Type/Step definitions elsewhere in this family. The engine action element remains afterward as an audit record of what was requested and its outcome.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Governance Engine Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The exact name of the governance engine that should execute this request (e.g. Egeria Survey Engine, Asset Onboarding Engine) -- a plain name, not a resolved element reference: passed directly as the REST path parameter, and generic element-search does not currently index GovernanceEngine configuration elements.


### Domain Identifier
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The governance domain, looked up from the domainIdentifier valid value set (deployments may extend this set without rebuilding Egeria). All domains is "All Domains". Accepts either the current display name or a preferred-value integer; old-style ALL_CAPS enum names (e.g. IT_INFRASTRUCTURE) are still accepted for backward compatibility.

>	**Valid Values**: All Domains,Data,Privacy,Security,IT Infrastructure,Software Development,Corporate,Asset Management,Other

>	**Default Value**: All Domains


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Legal
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Copyright and/or license information for the element or associated resource.


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


### GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


### URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


### Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version


### Request Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The request type the executing governance engine uses to identify the governance service to run.


### Request Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Parameters to pass to the governance service when this step executes.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Action Target Elements
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Elements this engine action operates on, passed to the governance service as action targets (all sharing the actionTargetName "actionTarget").


### Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


### External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


### External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


### For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


### For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


### Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


### Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the anchoring element.


### Anchor Scope ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor scope to restrict search.

>	**Alternative Labels**: Anchor Scope


### Glossary Term
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Term that provides meaning to this field.

>	**Alternative Labels**: Term


### Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the element is its own anchor or is anchored to a different element.

>	**Default Value**: true


### Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the update should be a merge or replace.

>	**Alternative Labels**: isMergeUpdate

>	**Default Value**: true


### Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the parent is at end1 of the relationship

>	**Default Value**: true


### Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the parent


### Parent Relationship Attributes
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of relationship attributes to establish the parent relationship.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type of parent relationship.


### Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Repository or element header status for an element.

>	**Default Value**: ACTIVE


### Zone Membership
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Zones scope visibility of elements to different users.


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional Properties  allow arbitrary properties not defined in the type definitions to be added to any referenceable element.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Class Word Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a class word in a naming standard.

>	**Default Value**: False


### Confidence Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidenceLevel enum: UNCLASSIFIED=0, AD_HOC=1, TRANSACTIONAL=2, AUTHORITATIVE=3, DERIVED=4, OBSOLETE=5, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,AD_HOC,TRANSACTIONAL,AUTHORITATIVE,DERIVED,OBSOLETE,OTHER


### Confidentiality Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidentialityLevel enum: UNCLASSIFIED=0, INTERNAL=1, CONFIDENTIAL=2, SENSITIVE=3, RESTRICTED=4, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,INTERNAL,CONFIDENTIAL,SENSITIVE,RESTRICTED,OTHER


### Criticality Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses CriticalityLevel enum: UNCLASSIFIED=0, MARGINAL=1, IMPORTANT=2, CRITICAL=3, CATASTROPHIC=4, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,MARGINAL,IMPORTANT,CRITICAL,CATASTROPHIC,OTHER


### Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An identier


### Impact Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, severity_identifier: int}. severity_identifier uses ImpactSeverity enum: UNCLASSIFIED=0, LOW=1, MEDIUM=2, HIGH=3, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,LOW,MEDIUM,HIGH,OTHER


### Modifier Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a modifier in a naming standard.

>	**Default Value**: False


### Policy Management Point
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Combined classification from 0435. Applied to Referenceable. Structure: {point_type: str, name: str, description: str}. point_type is one of: PolicyAdministrationPoint, PolicyDecisionPoint, PolicyEnforcementPoint, PolicyInformationPoint, PolicyRetrievalPoint. A Referenceable may have multiple policy management point classifications simultaneously.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Prime Word Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a prime word in a naming standard.

>	**Default Value**: False


### Retention Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, basis_identifier: int, associated_guid: str, archive_after: date, delete_after: date}. basis_identifier uses RetentionBasis enum: UNCLASSIFIED=0, TEMPORARY=1, PROJECT_LIFETIME=2, TEAM_LIFETIME=3, CONTRACT_LIFETIME=4, REGULATED_LIFETIME=5, TIMEBOXED_LIFETIME=6, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,TEMPORARY,PROJECT_LIFETIME,TEAM_LIFETIME,CONTRACT_LIFETIME,REGULATED_LIFETIME,TIMEBOXED_LIFETIME,OTHER


### Security Tags
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Optional security tags for security processing.


### Request Source Elements
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Elements that triggered/requested this engine action.


### Received Guards
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Guard values passed in from the element/process step that triggered this engine action.


### Process Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The qualified/display name of the governance action process (if any) that requested this engine action.


___
