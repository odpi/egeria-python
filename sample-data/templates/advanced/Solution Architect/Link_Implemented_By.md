___

## Link Implemented By
> Attach a design object (e.g. Information Supply Chain, Solution Component, Governance Definition) to its implementation via the ImplementedBy relationship (0737).

### Design Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The design element (e.g. Information Supply Chain, Solution Component, or Governance Definition) that is implemented.


### Implementation Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: The element (e.g. a deployed capability, process, or connector) that implements the Design Element.


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


### Design Step
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The step in the design process that this implementation relationship reflects.


### Implementation Role
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The role that the implementation element plays in delivering the design element.


### Transformation
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Any transformation performed by the implementation on its way to fulfilling the design.


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
