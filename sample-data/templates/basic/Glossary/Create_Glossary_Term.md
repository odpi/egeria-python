# Create Glossary Term
> Creates or updates a glossary term — a concept, phrase, or word defined within a glossary.
>
>	**Alternative Names**: Term

## Display Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The common name of an element.

>	**Alternative Labels**: "Term Name"


## Glossary Name
>	**Input Required**: True

>	**Attribute Type**: Reference Name List

>	**Description**: Zero or more existing glossaries that this term is a member of.

>	**Alternative Labels**: Glossary Name; Glossaries; In Glossaries; In Glossary; Glossary Names


## Abbreviation
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An abbreviation for the glossary term.


## Example
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: An example of how the glossary term is used.

>	**Alternative Labels**: Examples


## Folders
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: Existing folder collections that you'd like to make the term a member of.

>	**Alternative Labels**: Folders; Collection Folders


## Summary
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A short summary of the element's meaning or purpose.


## Usage
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The usage guidance for this element — how it is intended to be used in context.


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

