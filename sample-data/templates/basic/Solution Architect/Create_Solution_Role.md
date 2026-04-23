___

# Create Solution Role
> Creates or updates a solution role — a collection of responsibilities associated with a solution component.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## Role Domain Identifier
>	**Input Required**: False

>	**Attribute Type**: Enum

>	**Description**: String representing the governance domain. All domains is ALL

>	**Valid Values**: ALL,DATA,PRIVACY,SECURITY,IT_INFRASTRUCTURE,SOFTWARE_DEVELOPMENT,CORPORATE,ASSET_MANAGEMENT,OTHER

>	**Default Value**: ALL


## Role Identifier
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A user-assigned identifier for the solution role.


## Role Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Type of the solution role. Currently must be GovernanceRole.

>	**Default Value**: GovernanceRole


## Title
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Title of the solution role.


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


## Scope
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Scope of the definition or element.


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


___
