___

## Link Report Run Of
> Link a results set to the report it is a run of, with the run's result state (ReportRunOf relationship: ResultsSet -> Report).

### Results Set
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A results set (collection) name. Preferably a qualified name.


### Report
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A report name. Preferably a qualified name.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Result State
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Status of the results of this report run. Validated against Egeria's valid metadata values for resultState.


### Result State Reason
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Reason for the result state. Validated against Egeria's valid metadata values for resultStateReason.


### Result Location
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Where the results of this run are stored.


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
