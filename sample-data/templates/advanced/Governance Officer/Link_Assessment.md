___

## Link Assessment
> Record an assessment of an element that contributes to a decision (the Assessment relationship, multi-link: the same element can be assessed many times). The processed document carries the new Assessment GUID; re-running it with that GUID updates that assessment instead of adding another. Needs Egeria 6.4.

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


### Decision
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The decision: its qualified name, display name or GUID.


### Assessment GUID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The GUID of the Assessment relationship, as Link Assessment writes it into the processed document. Identifies one assessment exactly: the same element can be assessed for a decision many times.


### Assessor
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Who or what made the assessment (a name or GUID).


### Assessor Type Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The type name of the assessor element.


### Assessor Property Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The property of the assessor element that identifies it (e.g. qualifiedName).


### Assessment Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time of the assessment, ISO 8601 with a zone (e.g. 2026-11-21T10:00:00Z); a time with no zone is refused. With Element, Decision and Label it can pick one assessment when no Assessment GUID is given.


### Expiry Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time (ISO 8601) after which the decision or assessment no longer applies.


### Notes
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Notes and observations about the element.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Description
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A description.


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


### Additional Properties
>	**Input Required**: False

>	**Attribute Type**: Dictionary

>	**Description**: Additional Properties  allow arbitrary properties not defined in the type definitions to be added to any referenceable element.

>	| Parameter Name | Parameter Value |
>	|---|---|
>	| example_key | example_value |


___
