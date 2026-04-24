___

## Create License Type
> A type of license.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


### Domain Identifier
>	**Input Required**: False

>	**Attribute Type**: Enum

>	**Description**: String representing the governance domain. All domains is ALL

>	**Valid Values**: ALL,DATA,PRIVACY,SECURITY,IT_INFRASTRUCTURE,SOFTWARE_DEVELOPMENT,CORPORATE,ASSET_MANAGEMENT,OTHER

>	**Default Value**: ALL


### Implications
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of implications.


### Importance
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Importance of the definition.


### Outcomes
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of desired outcomes.


### Results
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of expected results.


### Summary
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A short summary of the element's meaning or purpose.


### Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


### Implementation Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Describes how this governance control is implemented.

>	**Alternative Labels**: Implementation


### Obligations
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing obligations.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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


### Qualified Name
>	**Input Required**: False

>	**Attribute Type**: QN

>	**Description**: The unique, text name of an element.


### Content Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: The lifecycle status of an element.

>	**Valid Values**: DRAFT,PREPARED,PROPOSED,APPROVED,REJECTED,ACTIVE,DEPRECATED,OTHER

>	**Default Value**: ACTIVE


### Scope
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Scope of the definition or element.


### Entitlements
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing entitlements.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


### Restrictions
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: A dictionary of property:value pairs describing restrictions.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


## Search Keywords
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


### Authors
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: The authors.


___
