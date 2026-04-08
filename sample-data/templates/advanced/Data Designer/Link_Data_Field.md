# Link Data Field
> Links or unlinks two data fields via the LinkedDataField relationship, with an optional relationship type name to describe the nature of the association (e.g. ForeignKey, DerivedFrom).

## Linked Data Field 1
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The first data field in a LinkedDataField peer relationship.


## Linked Data Field 2
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The second data field in a LinkedDataField peer relationship.


## Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


## Link Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name of the relationship used in a LinkedDataField connection.


## Link Relationship Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name of the relationship used in a LinkedDataField connection.


## Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


## Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


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


## Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


## Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false

