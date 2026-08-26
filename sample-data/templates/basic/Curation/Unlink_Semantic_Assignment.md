___

## Unlink Semantic Assignment
> Remove a SemanticAssignment relationship (0370) between an element and a glossary term.

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


___
