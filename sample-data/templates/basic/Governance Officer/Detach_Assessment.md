___

## Detach Assessment
> Remove one Assessment relationship: by its Assessment GUID, or else by Element + Decision + Label (+ Assessment Time when more than one matches). Zero or several matches are refused, listing the candidates. Needs Egeria 6.4.

### Assessment GUID
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: The GUID of the Assessment relationship, as Link Assessment writes it into the processed document. Identifies one assessment exactly: the same element can be assessed for a decision many times.


### Element
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The element at the other end of the relationship (any Referenceable): its qualified name, display name or GUID. For an assessment, the element that was assessed.

>	**Alternative Labels**: Assessed Element


### Decision
>	**Input Required**: False

>	**Attribute Type**: Reference Name

>	**Description**: The decision: its qualified name, display name or GUID.


### Label
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A label used to identify or categorise a relationship link.

>	**Alternative Labels**: Wire Label


### Assessment Time
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Date/time of the assessment, ISO 8601 with a zone (e.g. 2026-11-21T10:00:00Z); a time with no zone is refused. With Element, Decision and Label it can pick one assessment when no Assessment GUID is given.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


___
