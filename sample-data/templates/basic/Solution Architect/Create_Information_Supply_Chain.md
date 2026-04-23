___

# Create Information Supply Chain
> Creates or updates an information supply chain — a description of the flow of a particular type of data across a digital landscape.

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## In Information Supply Chain
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Supply chains that this supply chain is a segment of.


## Integration Style
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The integration style of the information supply chain (e.g. how data flows between segments).


## Nested Information Supply Chains
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of supply chains that compose this supply chain.


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


## Purpose
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The purpose of this collection — a short description of why it exists or what it is used for.


## Purposes
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: A list of purposes for this project (array&lt;string&gt;). Note: distinct from Collection.purpose (string, singular) which is a separate attribute on Collection Base.


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
