___

## Classify Security Tags
> Classify an existing element with the Security Tags classification (0423), attaching security labels/properties for downstream security processing.

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### Security Labels
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: List of security label tags applied to the element (0423 SecurityTags classification).


### Security Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Map of security property name/value pairs (0423 SecurityTags classification).

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


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
