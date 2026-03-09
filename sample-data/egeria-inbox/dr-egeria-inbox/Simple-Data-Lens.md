# Create Data Lens
>	A DataLens defines a geographic, temporal, and element scope for data collection and analysis.

## Anchor ID
>	**Input Required**: False

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.


## Glossary Term
>	**Input Required**: False

>	**Description**: Term that provides meaning to this field.

>	**Alternative Labels**: Term


## Is Own Anchor
>	**Input Required**: False

>	**Description**: Generally true.

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


## Journal Entry
>	**Input Required**: False

>	**Description**: 
This is my first attempt at create a data lens.

## Merge Update
>	**Input Required**: False

>	**Description**: If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Parent at End1
>	**Input Required**: False

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


## Parent ID
>	**Input Required**: False

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent


## Parent Relationship Attributes
>	**Input Required**: False

>	**Description**: Optional  details of the parent relationship attributes.


## Parent Relationship Type Name
>	**Input Required**: False

>	**Description**: The kind of the relationship to the parent element.


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element


## Status
>	**Input Required**: False

>	**Description**: The status of the business imperative. There is a list of valid values that this conforms to.

>	**Alternative Labels**: Definition Status

>	**Valid Values**: ['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']

>	**Default Value**: ACTIVE


## Zone Membership
>	**Input Required**: False

>	**Description**: Classification from 0424. Applied to OpenMetadataRoot. Structure: {zone_membership: list[str]}. Lists the governance zones an element belongs to.


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name

Test

## Class Word Classification
>	**Input Required**: False

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a class word in a naming standard.

>	**Default Value**: False


## Confidence Classification
>	**Input Required**: False

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidenceLevel enum: UNCLASSIFIED=0, AD_HOC=1, TRANSACTIONAL=2, AUTHORITATIVE=3, DERIVED=4, OBSOLETE=5, OTHER=99.


## Confidentiality Classification
>	**Input Required**: False

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses ConfidentialityLevel enum: UNCLASSIFIED=0, INTERNAL=1, CONFIDENTIAL=2, SENSITIVE=3, RESTRICTED=4, OTHER=99.


## Criticality Classification
>	**Input Required**: False

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, level_identifier: int}. level_identifier uses CriticalityLevel enum: UNCLASSIFIED=0, MARGINAL=1, IMPORTANT=2, CRITICAL=3, CATASTROPHIC=4, OTHER=99.


## Description
>	**Input Required**: False

>	**Description**: Description of the contents of the definition or relationship.

This is a first attempt at a data lens.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the definition.

>	**Alternative Labels**: Name

Lens1

## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Identifier
>	**Input Required**: False

>	**Description**: A user specified  identifier.


## Impact Classification
>	**Input Required**: False

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, severity_identifier: int}. severity_identifier uses ImpactSeverity enum: UNCLASSIFIED=0, LOW=1, MEDIUM=2, HIGH=3, OTHER=99.


## Modifier Classification
>	**Input Required**: False

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a modifier in a naming standard.

>	**Default Value**: False


## Policy Management Point
>	**Input Required**: False

>	**Description**: Combined classification from 0435. Applied to Referenceable. Structure: {point_type: str, name: str, description: str}. point_type is one of: PolicyAdministrationPoint, PolicyDecisionPoint, PolicyEnforcementPoint, PolicyInformationPoint, PolicyRetrievalPoint. A Referenceable may have multiple policy management point classifications simultaneously.


## Prime Word Classification
>	**Input Required**: False

>	**Description**: Classification from 0438. Applied to Referenceable. Marker classification (no attributes) indicating the element is a prime word in a naming standard.

>	**Default Value**: False


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## Retention Classification
>	**Input Required**: False

>	**Description**: Classification from 0422. Structure: {status_identifier: int, confidence: int, steward: str, steward_type_name: str, steward_property_name: str, source: str, notes: str, basis_identifier: int, associated_guid: str, archive_after: date, delete_after: date}. basis_identifier uses RetentionBasis enum: UNCLASSIFIED=0, TEMPORARY=1, PROJECT_LIFETIME=2, TEAM_LIFETIME=3, CONTRACT_LIFETIME=4, REGULATED_LIFETIME=5, TIMEBOXED_LIFETIME=6, OTHER=99.


## Security Tags
>	**Input Required**: False

>	**Description**: Classification from 0423. Applied to Referenceable. Structure: {security_labels: list[str], security_properties: dict[str, object], access_groups: dict[str, list[str]]}.


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Version Identifier
>	**Input Required**: False

>	**Description**: Published  version identifier.


## Authors
>	**Input Required**: False

>	**Description**: Defines the authors if ab Authored Referenceable.


## Content Status
>	**Input Required**: False

>	**Description**: The status of an AuthotredReferenceable. There is a list of valid values that this conforms to.

>	**Valid Values**: ['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']

>	**Default Value**: ACTIVE


## User Defined Content Status
>	**Input Required**: False

>	**Description**: Only valid if Content Status is set to OTHER. User defined & managed status values.


## Domain Identifier
>	**Input Required**: False

>	**Description**: String representing the governance domain. All domains is ALL

>	**Valid Values**: ['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CPRPORATE', 'ASSET_MANAGEMENT', 'OTHER']

>	**Default Value**: 0
ALL

## Implications
>	**Input Required**: False

>	**Description**: List of implications.


## Importance
>	**Input Required**: False

>	**Description**: Importance of the definition.


## Outcomes
>	**Input Required**: False

>	**Description**: List of desired outcomes.


## Results
>	**Input Required**: False

>	**Description**: A list of expected results.


## Scope
>	**Input Required**: False

>	**Description**: Scope of the definition.


## Summary
>	**Input Required**: False

>	**Description**: Summary of the definition.


## Usage
>	**Input Required**: False

>	**Description**: How the governance definition will be used.


## Implementation Description
>	**Input Required**: False

>	**Description**: Describes how this governance control is implemented.

>	**Alternative Labels**: Implementation


## Max Height
>	**Input Required**: False

>	**Description**: Maximum height of the vertical scope.


## Data Collection End Time
>	**Input Required**: False

>	**Description**: End time for the data collection period.


## Data Collection Start Time
>	**Input Required**: False

>	**Description**: Start time for the data collection period.
01-01-2026

## Max Latitude
>	**Input Required**: False

>	**Description**: Maximum latitude of the geographic scope.


## Max Longitude
>	**Input Required**: False

>	**Description**: Maximum longitude of the geographic scope.


## Min Height
>	**Input Required**: False

>	**Description**: Minimum height of the vertical scope.


## Min Latitude
>	**Input Required**: False

>	**Description**: Minimum latitude of the geographic scope.


## Min Longitude
>	**Input Required**: False

>	**Description**: Minimum longitude of the geographic scope.


## Scope Elements
>	**Input Required**: False

>	**Description**: Map of element identifiers defining the scope of the data lens.


## User Defined Status
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name

Test

## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Identifier
>	**Input Required**: False

>	**Description**: role identifier


## Classifications
>	**Input Required**: false

>	**Description**: Optionally specify the initial classifications for a collection. Multiple classifications can be specified. 

>	**Alternative Labels**: classification


## Is Own Anchor
>	**Input Required**: False

>	**Description**: Generally True. 

>	**Alternative Labels**: Own Anchor

>	**Default Value**: True


## Anchor ID
>	**Input Required**: False

>	**Description**: Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)


## Parent ID
>	**Input Required**: False

>	**Description**: Unique name of the parent element.

>	**Alternative Labels**: Parent;


## Parent Relationship Type Name
>	**Input Required**: False

>	**Description**: The kind of the relationship to the parent element.


## Anchor Scope Name
>	**Input Required**: False

>	**Description**: Optional qualified name of an anchor scope.


## Parent at End1
>	**Input Required**: False

>	**Description**: Is the parent at end1 of the relationship?

>	**Default Value**: True


## Qualified Name
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## GUID
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


## Effective Time
>	**Input Required**: False

>	**Description**: An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.


## Effective From
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element becomes effective (visible).


## Effective To
>	**Input Required**: False

>	**Description**: A string in ISO-8601 format that defines the when an element is no longer effective (visible).


## Merge Update
>	**Input Required**: False

>	**Description**: If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.

>	**Alternative Labels**: Merge

>	**Default Value**: True


## Additional Properties
>	**Input Required**: False

>	**Description**: Additional user defined values organized as name value pairs in a dictionary.


## External Source GUID
>	**Input Required**: False

>	**Description**: Identifier of an external source that is associated with this element.


## External Source Name
>	**Input Required**: False

>	**Description**: Name of an external element that is associated with this element.


## Journal Entry
>	**Input Required**: False

>	**Description**: 


## URL
>	**Input Required**: False

>	**Description**: Link to supporting information


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element


## Supplementary Properties
>	**Input Required**: False

>	**Description**: Provide supplementary information to the element using the structure of a glossary term

