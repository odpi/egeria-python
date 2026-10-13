___

## Detach Associated Valid Values
> Removes the ValidValueAssociation relationship.

### Valid Value 1
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The first valid value in the relationship.


### Valid Value 2
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The second valid value in the relationship.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Association Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of the association between the two valid values.


### Association Type
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Type of the association between the two valid values.


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


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional Properties  allow arbitrary properties not defined in the type definitions to be added to any referenceable element.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
