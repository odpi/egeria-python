___

## Link Semantic Assignment
> Create a SemanticAssignment relationship (0370) between an existing element and a glossary term, indicating the data matches the term meaning.

### Target Element
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: Qualified name of the existing element being classified or linked.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Confidence Level
>	**Input Required**: False

>	**Attribute Type**: Simple Int

>	**Description**: Percentage confidence (0-100) that a Semantic Assignment correctly links the element to the glossary term (0370).


### Semantic Expression
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Expression describing how the element meaning relates to the assigned glossary term (0370 SemanticAssignment).


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


### Governance Status
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Status of a governance classification assignment, looked up from the statusIdentifier valid value set. Accepts the current display name or a preferred-value integer.

>	**Valid Values**: Discovered,Proposed,Imported,Validated,Deprecated,Obsolete,Other

>	**Default Value**: Validated


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


### Glossary Term
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: Term that provides meaning to this field.

>	**Alternative Labels**: Term


### Steward
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The identifier of the steward responsible for the element.


### Source
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The source of the information.


___
