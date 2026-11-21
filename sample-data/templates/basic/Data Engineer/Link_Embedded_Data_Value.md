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


___
