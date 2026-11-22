___

## Link Embedded Data Value
> Record that a data value is embedded in another (the EmbeddedDataValue relationship, parent to embedded), at a Position (0 means unset). Needs Egeria 6.4.

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Parent Data Value
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data value that the embedded value is part of: its qualified name, display name or GUID.


### Embedded Data Value
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data value embedded in the parent value: its qualified name, display name or GUID.


### Position
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: The ordinal position: of a data field within its containing data structure, or of a data value among an element's processing variables or a parent value's embedded values (0 means unset).

>	**Default Value**: 0


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


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


### Anchor Scope IDs
>	**Input Required**: False

>	**Attribute Type**: Reference Name List

>	**Description**: A list of IDs that are anchor scopes for this element.


### Make Anchor
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: Is the element at end2 an anchor to end1?

>	**Default Value**: false


___
