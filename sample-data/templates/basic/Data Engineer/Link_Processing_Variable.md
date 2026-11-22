___

## Link Processing Variable
> Record that an element (a process, a step) uses a data value as a variable (the ProcessingVariable relationship), at a Position (0 means unset). Needs Egeria 6.4.

### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Element
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The element at the other end of the relationship (any Referenceable): its qualified name, display name or GUID. For an assessment, the element that was assessed.

>	**Alternative Labels**: Assessed Element


### Data Value
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The data value: its qualified name, display name or GUID.


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
