___

## Setup Valid Metadata Map Value
> Create or update the valid value for a name/value pair that can be stored in a particular open metadata map-valued property.

### Metadata Property Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The open metadata property name the valid value is set up for.


### Map Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The name of the map entry, for a map-valued property.


### Preferred Value
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The valid/preferred value being set up for the property (or map name/value).


### Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The open metadata type name the valid value applies to; leave unset to apply to all types.


### Metadata Display Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Display name for the valid metadata value.


### Metadata Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Description of the valid metadata value.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


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


___
