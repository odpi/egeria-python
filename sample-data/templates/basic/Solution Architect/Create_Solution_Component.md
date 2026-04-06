# Create Solution Component
> Creates or updates a reusable solution component — a building block of a solution blueprint or information supply chain.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## Actors
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Actors or Solution Roles related to this element.


## In Information Supply Chain
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Supply chains that this supply chain is a segment of.


## In Solution Blueprints
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Solution blueprints that contain this component.


## In Solution Components
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Solution components that include this one.


## Planned Deployed Implementation Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The planned implementation type for deployment.


## Solution Component Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Type of solution component.


## Solution SubComponents
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Solution sub-components of this component. In current approach the parent does not specify sub-components; components specify their parents instead.


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

