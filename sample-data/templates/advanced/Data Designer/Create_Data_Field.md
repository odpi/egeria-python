# Create Data Field
> Creates or updates a data field — a named, typed element within a data structure. Supports nesting via In Data Field and data class assignment.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## Data Class
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data class that specifies the valid values or patterns for this data field (DataValueDefinition relationship).


## Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


## Default Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The default value assigned to this field or data class when no value is supplied.


## In Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data field that this element is nested within (NestedDataField relationship).


## In Data Structure
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data structure that contains this data field (MemberDataField relationship).


## Is Nullable
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


## Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of characters or digits allowed in the field.


## Maximum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of times this field may appear in the containing data structure (-1 means unbounded).

>	**Default Value**: 1


## Minimum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of times this field must appear in the containing data structure.

>	**Default Value**: 1


## Minimum Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of characters or digits required in the field.


## Name Patterns
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Name patterns for naming standard rules.


## Namespace Path
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The namespace path that qualifies the element's name within a larger naming hierarchy.


## Ordered Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the values in this field are ordered (i.e. sequence matters).


## Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


## Precision
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of significant digits after the decimal point for numeric fields.


## Sort Order
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The sort order for values in this field. Valid values from DataItemSortOrder enum: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER.


## Units
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


## Allow Duplicate Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the data class allows duplicate values in the data field.

>	**Default Value**: true


## Data Class
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data class that specifies the valid values or patterns for this data field (DataValueDefinition relationship).


## Data Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The data type of the field or value specification (e.g. string, int, date, boolean).

>	**Valid Values**: string,int,long,date,boolean,char,byte,float,double,biginteger,bigdecimal,array<string>,array<int>,map<string,string>,map<string,boolean>,map<string,int>,map<string,long>,map<string,double>,map<string,date>,map<string,object>,short,map<string,array<string>>,other

>	**Default Value**: string


## Default Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The default value assigned to this field or data class when no value is supplied.


## In Data Field
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data field that this element is nested within (NestedDataField relationship).


## In Data Structure
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data structure that contains this data field (MemberDataField relationship).


## Is Nullable
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the field may hold null values.

>	**Default Value**: true


## Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of characters or digits allowed in the field.


## Maximum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The maximum number of times this field may appear in the containing data structure (-1 means unbounded).

>	**Default Value**: 1


## Minimum Cardinality
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of times this field must appear in the containing data structure.

>	**Default Value**: 1


## Minimum Length
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The minimum number of characters or digits required in the field.


## Name Patterns
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Name patterns for naming standard rules.


## Ordered Values
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, the values in this field are ordered (i.e. sequence matters).


## Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position of the data field within its containing data structure.

>	**Default Value**: 0


## Precision
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The number of significant digits after the decimal point for numeric fields.


## Sort Order
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The sort order for values in this field. Valid values from DataItemSortOrder enum: UNKNOWN, UNSORTED, ASCENDING, DESCENDING, OTHER.


## Units
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The unit of measure for numeric values in this field or specification (e.g. metres, kg, USD).


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Category
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-defined category for the element, used to group related elements for display or search purposes.

>	**Alternative Labels**: Category Name


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


## Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


## Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


## Aliases
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Alternative names for this  field, used in different systems or contexts.

>	**Alternative Labels**: Alias


## Aliases
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Alternative names for this  field, used in different systems or contexts.

>	**Alternative Labels**: Alias


## Search Keywords
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of search keywords.


## GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: A unique identifier - typically of an element in this context.

>	**Alternative Labels**: guid; Guid


## URL
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: URL for further information.


## Version Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The version of the element

>	**Alternative Labels**: Version

>	**Default Value**: 1.0


## Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


## Effective From
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The beginning of when an element is viewable.


## Effective Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The time at which an element must be effective in order to be returned by the request.


## Effective To
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The ending time at which an element is visible.


## External Source GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: The unique identifier of an external source.


## External Source Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The name of an external source


## For Duplicate Processing
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support duplicate processing.


## For Lineage
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Flag indicating if the request is to support lineage.


## Request ID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user provided or system generated request id for a conversation.


## Anchor ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the anchoring element.


## Anchor Scope ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Anchor scope to restrict search.

>	**Alternative Labels**: Anchor Scope


## Glossary Term
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Term that provides meaning to this field.

>	**Alternative Labels**: Term


## Is Own Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the element is its own anchor or is anchored to a different element.

>	**Alternative Labels**: Own Anchor

>	**Default Value**: true


## Merge Update
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the update should be a merge or replace.

>	**Alternative Labels**: isMergeUpdate

>	**Default Value**: true


## Parent at End1
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: A flag indicating if the parent is at end1 of the relationship

>	**Default Value**: true


## Parent ID
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Name of the parent

>	**Alternative Labels**: Parent;


## Parent Relationship Attributes
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of relationship attributes to establish the parent relationship.


## Parent Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type of parent relationship.


## Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Repository or element header status for an element.

>	**Default Value**: ACTIVE


## Zone Membership
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Zones scope visibility of elements to different users.


## Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional Properties  allow arbitrary properties not defined in the type definitions to be added to any referenceable element.


## Class Word Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a class word in a naming standard.

>	**Default Value**: False


## Confidence Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidenceLevel enum: UNCLASSIFIED=0, AD_HOC=1, TRANSACTIONAL=2, AUTHORITATIVE=3, DERIVED=4, OBSOLETE=5, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,AD_HOC,TRANSACTIONAL,AUTHORITATIVE,DERIVED,OBSOLETE,OTHER


## Confidentiality Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidentialityLevel enum: UNCLASSIFIED=0, INTERNAL=1, CONFIDENTIAL=2, SENSITIVE=3, RESTRICTED=4, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,INTERNAL,CONFIDENTIAL,SENSITIVE,RESTRICTED,OTHER


## Criticality Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses CriticalityLevel enum: UNCLASSIFIED=0, MARGINAL=1, IMPORTANT=2, CRITICAL=3, CATASTROPHIC=4, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,MARGINAL,IMPORTANT,CRITICAL,CATASTROPHIC,OTHER


## Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An identier

>	**Alternative Labels**: ID


## Impact Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, severity_identifier: int}. severity_identifier uses ImpactSeverity enum: UNCLASSIFIED=0, LOW=1, MEDIUM=2, HIGH=3, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,LOW,MEDIUM,HIGH,OTHER


## Modifier Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a modifier in a naming standard.

>	**Default Value**: False


## Policy Management Point
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Combined classification from 0435. Applied to Referenceable. Structure: {point_type: str, name: str, description: str}. point_type is one of: PolicyAdministrationPoint, PolicyDecisionPoint, PolicyEnforcementPoint, PolicyInformationPoint, PolicyRetrievalPoint. A Referenceable may have multiple policy management point classifications simultaneously.


## Prime Word Classification
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a prime word in a naming standard.

>	**Default Value**: False


## Retention Classification
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, basis_identifier: int, associated_guid: str, archive_after: date, delete_after: date}. basis_identifier uses RetentionBasis enum: UNCLASSIFIED=0, TEMPORARY=1, PROJECT_LIFETIME=2, TEAM_LIFETIME=3, CONTRACT_LIFETIME=4, REGULATED_LIFETIME=5, TIMEBOXED_LIFETIME=6, OTHER=99.

>	**Valid Values**: UNCLASSIFIED,TEMPORARY,PROJECT_LIFETIME,TEAM_LIFETIME,CONTRACT_LIFETIME,REGULATED_LIFETIME,TIMEBOXED_LIFETIME,OTHER


## Security Tags
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Optional security tags for security processing.


## User Defined Content Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user defined content status = only valid if content status is OTHER.


## User Defined Status
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Only valid if  Status is set to OTHER. User defined & managed status values.


## Classifications
>	**Input Required**: false

>	**Attribute Type**: Named DICT

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Anchor Scope Name
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Optional qualified name of an anchor scope.


## Supplementary Properties
>	**Input Required**: False

>	**Attribute Type**: Named DICT

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

