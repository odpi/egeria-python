___

## Detach Valid Value Implementation
> Removes the ValidValuesImplementation relationship.

### Valid Value
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The valid value being implemented (end 1 of ValidValuesImplementation).


### Implementation Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The element (e.g. a deployed capability, process, or connector) that implements the Design Element.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Symbolic Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The symbolic name the implementing element uses for this valid value.


### Implementation Value
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The value the implementing element uses to represent this valid value.


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


### Additional Values
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Other values the implementing element uses for this valid value, as name/value pairs.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
