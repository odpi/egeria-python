___

## Create Report
> Defines a report with optional default parameters set, that can be placed on a Dashboard.

### Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Report Spec
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The name of the report spec (FormatSet) to run, e.g. 'Digital-Products', 'Collections', 'My-User-MD'. This is the primary identifier for the report — equivalent to --report in the CLI.

>	**Default Value**: Referenceable


### Deployed Implementation Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The implementation type for a deploymed resource.

>	**Alternative Labels**: Deployed Impl Type


### Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


### Resource Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of a resource.


### Analytic Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name-Value pairs of analytic parameters

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Ends With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the end of  a field.

>	**Default Value**: False


### Ignore Case
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, ignore the difference between upper and lower characters when matching the search string.

>	**Default Value**: False


### Metadata Element Subtype Names
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Filter results by the list of metadata elements. If none are provided, then no status filtering will be performed.


### Metadata Element Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Optionally filter results by the type of metadata element.


### Output Format
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Optional specification of output format for the query.

>	**Valid Values**: LIST,FORM,REPORT,MERMAID,DICT,MD,TABLE,JSON

>	**Default Value**: JSON


### Page Size
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of elements returned per page.

>	**Default Value**: 0


### Search String
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An optional search string to filter results by.

>	**Default Value**: *


### Start From
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: When paging through results, the starting point of the results to return.

>	**Default Value**: 0


### Starts With
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, look for matches with the search string starting from the beginning of  a field.

>	**Default Value**: True


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

>	**Default Value**: 1.0


### Report Parameters
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Name-Value pairs of extra parameters for the target Report Spec's action that aren't part of the standard find/search attribute set (e.g. collection_guid for the "Collection Members" report). Keys must match exactly what the target report spec's action expects.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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

>	**Alternative Labels**: Own Anchor

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

>	**Alternative Labels**: Parent;


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

>	**Alternative Labels**: ID


### Impact Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, severity_identifier: int}. severity_identifier uses ImpactSeverity enum: UNCLASSIFIED=0, LOW=1, MEDIUM=2, HIGH=3, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,LOW,MEDIUM,HIGH,OTHER


### Policy Management Point
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Combined classification from 0435. Applied to Referenceable. Structure: {point_type: str, name: str, description: str}. point_type is one of: PolicyAdministrationPoint, PolicyDecisionPoint, PolicyEnforcementPoint, PolicyInformationPoint, PolicyRetrievalPoint. A Referenceable may have multiple policy management point classifications simultaneously.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Retention Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, basis_identifier: int, associated_guid: str, archive_after: date, delete_after: date}. basis_identifier uses RetentionBasis enum: UNCLASSIFIED=0, TEMPORARY=1, PROJECT_LIFETIME=2, TEAM_LIFETIME=3, CONTRACT_LIFETIME=4, REGULATED_LIFETIME=5, TIMEBOXED_LIFETIME=6, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,TEMPORARY,PROJECT_LIFETIME,TEAM_LIFETIME,CONTRACT_LIFETIME,REGULATED_LIFETIME,TIMEBOXED_LIFETIME,OTHER


### Security Tags
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Optional security tags for security processing.


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


### Anchor Scope ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor scope to restrict search.

>	**Alternative Labels**: Anchor Scope


### AsOfTime
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An ISO-8601 string representing the time to view the state of the repository.


### Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


### Governance Zone Filter
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include only elements in one of the specified governance zones.


### Graph Query Depth
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The depth of the hierarchy to return. Default is 5. Specifying 0 returns only the top level attributes.

>	**Default Value**: 1


### Include Only Classified Elements
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include only elements with the specified classifications.


### Include Only Relationships
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Include information only about specified relationships.


### Limit Result by Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: One of the status values from a list of valid values.

>	**Valid Values**: UNKNOWN,DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,APPROVED_CONCEPT,UNDER_DEVELOPMENT,DEVELOPMENT_COMPLETE,APPROVED_FOR_DEPLOYMENT,STANDBY,ACTIVE,FAILED,DISABLED,COMPLETE,DEPRECATED,OTHER,DELETED

>	**Default Value**: ['ACTIVE']


### Order Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property to use for sorting if the sort_order_property is PROPERTY_ASCENDING or PROPERTY_DESCENDING


### Output Sort Order
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: How to order the results. The sort order can be selected from a list of valid value.

>	**Valid Values**: ANY,CREATION_DATE_RECENT,CREATION_DATA_OLDEST,LAST_UPDATE_RECENT,LAST_UPDATE_OLDEST,PROPERTY_ASCENDING,PROPERTY_DESCENDING


### Skip Classified Elements
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Skip elements with the any of the specified classifications.


### Skip Relationships
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Allow listed relationships to be skipped in the output returned.


### User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only valid if  Status is set to OTHER. User defined & managed status values.


### Classifications
>	**Input Required**: false

>	**Attribute Type**: Named DICT

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


### Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
