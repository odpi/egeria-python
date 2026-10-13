___

## Link Valid Value Member
> Links a value as a member of a reference data set (or any valid value set) (ValidValueMember relationship).

### Valid Value Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The valid value set/definition that defines the allowed values for this element (ValidValuesAssignment relationship).

>	**Alternative Labels**: Valid Value Definition


### Member Value
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The value that is a member of the set (end 2 of ValidValueMember).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Is Default Member
>	**Input Required**: False

>	**Attribute Type**: Bool

>	**Description**: If true, this value is the set's default (isDefaultValue on the ValidValueMember relationship).

>	**Default Value**: false


### Member Ordinal
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Position of the value within the set (ordinal on the ValidValueMember relationship).

>	**Default Value**: 0


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
